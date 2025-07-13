mod models;
use models::PaletteCurve;
use models::imagetovec::Color;
use glam::Vec3A;
use std::path::PathBuf;

fn main() {
    // 1. Create PaletteCurve with specified parameters
    let curve = PaletteCurve::new(
        255,
        0.5716,
        2.2763,
        0.9581,
        5.1980,
        1.4928,
    );

    // 2. Create palette points
    let palette_points: Vec<Vec3A> = curve.points();
    println!("Generated {} palette points", palette_points.len());

    // 3. Load colorwheel.webp
    let input_path = "/Users/richardklassen/Developer/genuary/2025/Jul.11/_input/colorwheel.webp";
    let (pixels, width, height) = models::image_to_vec_u8rgb(input_path)
        .expect("Failed to load colorwheel.webp");
    println!("Loaded colorwheel.webp: {}x{}", width, height);

    // 4. Map each pixel to closest palette point
    let mut output_pixels = Vec::with_capacity(pixels.len());
    for rgb in pixels.iter() {
        let color = Color { r: rgb[0], g: rgb[1], b: rgb[2] };
        let (h, s, l) = color.to_hsl();
        let pixel_vec = Color::to_vec3a(h, s, l);
        let closest = palette_points
            .iter()
            .min_by(|a, b| {
                PaletteCurve::error(**a, pixel_vec)
                    .partial_cmp(&PaletteCurve::error(**b, pixel_vec))
                    .unwrap_or(std::cmp::Ordering::Equal)
            })
            .unwrap_or(&palette_points[0]);
        let (h, s, l) = Color::vec3a_to_hsl(*closest);
        let mapped_color = Color::from_hsl(h, s, l);
        output_pixels.push(mapped_color.r);
        output_pixels.push(mapped_color.g);
        output_pixels.push(mapped_color.b);
        output_pixels.push(255); // Alpha channel
    }

    // 5. Save as webp
    let output_path = "/Users/richardklassen/Developer/genuary/2025/Jul.11/_input/palettewheel.webp";
    models::save_pixels_as_webp(&output_pixels, width, height, output_path, 80.0)
        .expect("Failed to save palettewheel.webp");
    println!("Saved palettewheel.webp");
}
