use std::path::PathBuf;

mod models;
use models::PaletteCurve;
use models::image_to_vec_u8rgb;
use models::u8rgba_to_color_counts;

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
        PathBuf::from("_input/grasshopper-9363974_1280.jpg"),
        PathBuf::from("_input/mountain-9533968_1920.jpg"),
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

    let mut best_curves = Vec::new();
    for (i, color_counts) in hashmaps.iter().enumerate() {
        println!("\n🎨 Processing Image {}...", i + 1);
        let best_curve = PaletteCurve::best_fit(color_counts, 1000);
        println!("✅ Best fit curve found for Image {}", i + 1);
        
        // Print detailed curve analysis
        println!("\n{}", best_curve.describe());
        
        // Also print compact summary
        println!("\nSummary: {}", best_curve.summary());
        
        best_curves.push(best_curve);
    }

    println!("\n{}", "=".repeat(60));
    println!("🎯 Final Results Summary:");
    println!("{}", "=".repeat(60));
    
    for (i, curve) in best_curves.iter().enumerate() {
        println!("Image {}: {}", i + 1, curve.summary());
    }
}

