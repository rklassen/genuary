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

    // Save palette swatches as PNG
    let swatch_path = "/Users/richardklassen/Developer/genuary/2025/Jul.11/_output/paletteswatches.png";
    curve.to_png(PathBuf::from(swatch_path)).expect("Failed to save palette swatches PNG");

    // 2. Create palette points
    let palette_points: Vec<Vec3A> = curve.points();
    println!("Generated {} palette points", palette_points.len());

    // 3. Load colorwheel.webp
    let input_path = "/Users/richardklassen/Developer/genuary/2025/Jul.11/_input/colorwheel.webp";
    let (pixels, width, height) = models::image_to_vec_u8rgb(input_path)
        .expect("Failed to load colorwheel.webp");
    println!("Loaded colorwheel.webp: {}x{}", width, height);

    // 4. Map each pixel to closest palette point
    use rayon::prelude::*;
    use indicatif::{ProgressBar, ProgressStyle};
    let pb = ProgressBar::new(pixels.len() as u64);
    pb.set_style(
        ProgressStyle::default_bar()
            .template("{prefix} [{bar:20.yellow/blue}] {pos}/{len}")
            .unwrap()
            .progress_chars("█▉▊▋▌▍▎▏ ")
    );
    pb.set_prefix("Mapping pixels");

    let output_pixels: Vec<u8> = pixels.par_iter().flat_map(|rgb| {
        pb.inc(1);
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
        vec![mapped_color.r, mapped_color.g, mapped_color.b, 255]
    }).collect();
    pb.finish_with_message("✓ Complete");

    // 5. Save as webp
    let output_path = "/Users/richardklassen/Developer/genuary/2025/Jul.11/_output/palettewheel.webp";
    models::save_pixels_as_webp(&output_pixels, width, height, output_path, 80.0)
        .expect("Failed to save palettewheel.webp");
    println!("Saved palettewheel.webp");
}
