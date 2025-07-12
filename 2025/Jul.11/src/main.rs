/// Print a histogram of color frequencies for a given color_counts HashMap
fn print_color_histogram(color_counts: &std::collections::HashMap<models::imagetovec::Color, usize>) {
    let max_count = color_counts.values().copied().max().unwrap_or(1);
    let mut color_vec: Vec<_> = color_counts.iter().collect();
    color_vec.sort_by(|a, b| b.1.cmp(a.1)); // Sort descending by count
    // Find the max width needed for the count field
    let count_width = color_vec.iter().map(|(_, c)| c.to_string().len()).max().unwrap_or(1);
    for (color, count) in color_vec {
        let bar_len = (40 * *count / max_count).max(1); // scale to max 40 chars
        let bar = "█".repeat(bar_len);
        println!(
            "{:>3},{:>3},{:>3} | {:>width$} | {}",
            color.r, color.g, color.b, count, bar, width = count_width
        );
    }
}
use std::path::PathBuf;

mod models;
use models::PaletteCurve;
use models::image_to_vec_u8rgb;
use models::u8rgba_to_color_counts;
use webp::Encoder;
use std::fs::File;
use std::io::Write;

/// 1. Load an image
/// 2. Extract the palette, all pixels
/// 3. Generate all curves at increment x or n number
/// 4. Find which curve has least error to all pixels
/// 5. Report that curve data
/// 6. For each input color, find nearest point on curve
/// 7. Map input image to output image accordingly
fn main() {
    let image_paths = vec![
        PathBuf::from("_input/flower-9294773_1920.png"),
        // PathBuf::from("_input/grasshopper-9363974_1280.jpg"),
        // PathBuf::from("_input/mountain-9533968_1920.jpg"),
    ];

    let pixels_vec: Vec<_> = image_paths
        .iter()
        .map(|path| image_to_vec_u8rgb(
            &path.to_string_lossy()
        ).expect("Failed to load image"))
        .collect();

    println!("Successfully loaded {} images to u8 pixels.", pixels_vec.len());

    let mut hashmaps = Vec::new();
    for (i, pixels_u8) in pixels_vec.iter().enumerate() {
        let hashmap = u8rgba_to_color_counts(pixels_u8.clone());
        println!("Created color counts HashMap for image {} with {} unique colors.", i + 1, hashmap.len());
        hashmaps.push(hashmap);
    }

    for (i, color_counts) in hashmaps.iter_mut().enumerate() {
        let mut sorted_colors: Vec<_> = color_counts.iter().collect();
        sorted_colors.sort_by(|a, b| b.1.cmp(a.1)); // Sort descending by count
        let sorted_hashmap: std::collections::HashMap<_, _> = sorted_colors
            .into_iter()
            .map(|(color, count)| (color.clone(), *count))
            .collect();
        *color_counts = sorted_hashmap;
    }

    let top_colors: Vec<_> = hashmaps
        .iter()
        .map(|color_counts| {
            let mut color_vec: Vec<_> = color_counts.iter().collect();
            color_vec.sort_by(|a, b| b.1.cmp(a.1)); // Sort descending by count
            color_vec
                .into_iter()
                .take(15)
                .map(|(color, count)| (color.clone(), *count))
                .collect::<std::collections::HashMap<_, _>>()
        })
        .collect();


    let mut best_curves = Vec::new();
    for (i, color_counts) in top_colors.iter().enumerate() {
        println!("\n🎨 Processing Image {}...", i + 1);
        println!("Color Frequency Histogram for Image {}:", i + 1);
        print_color_histogram(color_counts);
        let best_curve = PaletteCurve::best_fit(color_counts, 255);
        println!("Randomized 1 curves for evaluation.");
        println!("Evaluating [████████████████████] 1/1");
        // println!("{:<25} {:<35} {:<10}", "Color", "Closest Point", "Error");
        // println!("{:-<25} {:-<35} {:-<10}", "", "", "");
        // for (color, _) in color_counts.iter() {
            // let vec3a = color.to_vec3a();
            // let closest_point = best_curve.get_closest_point(&vec3a);
            // let error = best_curve.sample(0.0).distance_squared(vec3a); // Or use best_curve.mean_square_error for all
            // println!(
            //     "{:>3},{:>3},{:>3}   {:>10.6}, {:>10.6}, {:>10.6}   {:>10.6}",
            //     color.r, color.g, color.b,
            //     closest_point.x, closest_point.y, closest_point.z,
            //     error
            // );
        // } /
        println!("✅ Best fit curve found for Image {}", i + 1);
        println!("\n{}", best_curve.describe());
        println!("\nSummary: {}", best_curve.summary());
        best_curves.push(best_curve);
    }

    for (i, pixels_u8) in pixels_vec.iter().enumerate() {
        let best_curve = &best_curves[i];
        let flat_pixels: Vec<u8> = pixels_u8.iter().flat_map(|rgb| rgb.iter()).copied().collect();
        let mapped_pixels = map_pixels_to_curve(best_curve, &flat_pixels);
        // Get image dimensions from the loaded pixels
        let (width, height) = {
            let img = image::open(&image_paths[i]).expect("Failed to open image for dimensions");
            (img.width(), img.height())
        };
        let orig_path = &image_paths[i];
        let mut out_path = orig_path.clone();
        // Change folder from _input to _output
        let out_path_str = out_path.to_string_lossy().replace("_input/", "_output/");
        // Switch extension to .webp
        let out_path_str = {
            let mut p = PathBuf::from(&out_path_str);
            p.set_extension("webp");
            p.to_string_lossy().to_string()
        };
        match save_pixels_as_webp(&mapped_pixels, width, height, &out_path_str, 80.0) {
            Ok(_) => println!("Saved mapped image to {}", out_path_str),
            Err(e) => eprintln!("Failed to save WebP: {}", e),
        }
    }

    println!("\n{}", "=".repeat(60));
    println!("🎯 Final Results Summary:");
    println!("{}", "=".repeat(60));
    
    for (i, curve) in best_curves.iter().enumerate() {
        println!("Image {}: {}", i + 1, curve.summary());
    }

    

}

/// Map each input pixel to the closest point on the curve, returning a new Vec<u8> of RGBA format
fn map_pixels_to_curve(curve: &PaletteCurve, input_pixels: &[u8]) -> Vec<u8> {
    let mut output = Vec::with_capacity((input_pixels.len() / 3) * 4);
    let channels = if input_pixels.len() % 4 == 0 { 4 } else { 3 };
    for chunk in input_pixels.chunks(channels) {
        let r = chunk[0] as f32 / 255.0;
        let g = chunk[1] as f32 / 255.0;
        let b = chunk[2] as f32 / 255.0;
        let input_vec = glam::Vec3A::new(r, g, b);
        let t = curve.get_closest_t(&input_vec);
        let curve_point = curve.sample(t);
        output.push((curve_point.x * 255.0).round().clamp(0.0, 255.0) as u8);
        output.push((curve_point.y * 255.0).round().clamp(0.0, 255.0) as u8);
        output.push((curve_point.z * 255.0).round().clamp(0.0, 255.0) as u8);
        // Always output alpha as 255 (opaque)
        output.push(255);
    }
    output
}

fn save_pixels_as_webp(pixels: &[u8], width: u32, height: u32, out_path: &str, quality: f32) -> std::io::Result<()> {
    // Ensure RGBA format
    let channels = if pixels.len() % 4 == 0 { 4 } else { 3 };
    let rgba_pixels = if channels == 4 {
        pixels.to_vec()
    } else {
        let mut out = Vec::with_capacity(width as usize * height as usize * 4);
        for chunk in pixels.chunks(3) {
            out.push(chunk[0]);
            out.push(chunk[1]);
            out.push(chunk[2]);
            out.push(255);
        }
        out
    };
    let encoder = Encoder::from_rgba(&rgba_pixels, width, height);
    let webp = encoder.encode(quality);
    let mut file = File::create(out_path)?;
    file.write_all(&webp)?;
    Ok(())
}

