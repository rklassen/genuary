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
        //PathBuf::from("_input/grasshopper-9363974_1280.jpg"),
        //PathBuf::from("_input/mountain-9533968_1920.jpg"),
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

    println!("\n{}", "=".repeat(60));
    println!("🎯 Final Results Summary:");
    println!("{}", "=".repeat(60));
    
    for (i, curve) in best_curves.iter().enumerate() {
        println!("Image {}: {}", i + 1, curve.summary());
    }
}

