/// Print a histogram of color frequencies for a given color_counts HashMap
fn print_color_histogram(color_counts: &std::collections::HashMap<models::imagetovec::Color, usize>) {
    let max_count = color_counts.values().copied().max().unwrap_or(1);
    let mut color_vec: Vec<_> = color_counts.iter().collect();
    color_vec.sort_by(|a, b| b.1.cmp(a.1)); // Sort descending by count
    // Find the max width needed for the count field
    let count_width = color_vec.iter().map(|(_, c)| c.to_string().len()).max().unwrap_or(1);
    for (i, (color, count)) in color_vec.iter().enumerate() {
        if i >= 12 { break; }
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
const TOP_COLORS_COUNT: usize = 2048; // Limit to top N colors for each image
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

    // Load images and store pixel data and dimensions
    let mut pixels_vec = Vec::new();
    let mut dimensions_vec = Vec::new();
    for path in image_paths.iter() {
        let (pixels, width, height) = image_to_vec_u8rgb(&path.to_string_lossy())
            .expect("Failed to load image");
        println!("Loaded image: {} (dimensions: {}x{})", path.display(), width, height);
        pixels_vec.push(pixels);
        dimensions_vec.push((width, height));
    }

    println!("Successfully loaded {} images to u8 pixels.", pixels_vec.len());
    
    // Create a HashMap for each image's color counts
    let mut hashmaps = Vec::new();
    for (i, pixels_u8) in pixels_vec.iter().enumerate() {
        let hashmap = u8rgba_to_color_counts(pixels_u8.clone());
        println!("Created color counts HashMap for image {} with {} unique colors.", i + 1, hashmap.len());
        hashmaps.push(hashmap);
    }

    let top_colors: Vec<_> = hashmaps
        .iter()
        .map(|color_counts| {
            let mut color_vec: Vec<_> = color_counts.iter().collect();
            color_vec.sort_by(|a, b| b.1.cmp(a.1)); // Sort descending by count
            color_vec
                .into_iter()
                .take(TOP_COLORS_COUNT) // Limit to top N colors
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
        println!("✅ Best fit curve found for Image {}", i + 1);
        println!("\n{}", best_curve.describe());
        println!("\nSummary: {}", best_curve.summary());
        best_curves.push(best_curve);

        // Save palette grid PNG for each curve
        let palette_dir = std::path::Path::new("_output/palette");
        let _ = std::fs::create_dir_all(palette_dir);
        let palette_path = palette_dir.join(format!("palette-{}.png", i + 1));
        match best_curves.last().unwrap().to_png(palette_path.clone()) {
            Ok(_) => println!("✅ Palette PNG saved to {}", palette_path.display()),
            Err(e) => eprintln!("❌ Failed to save palette PNG: {}", e),
        }
    }



    for (i, pixels_u8) in pixels_vec.iter().enumerate() {
        let best_curve = &best_curves[i];
        let (width, height) = dimensions_vec[i];
        println!("\n⚙️ Processing image {}x{} pixels", width, height);
        let flat_pixels: Vec<u8> = pixels_u8.iter().flat_map(|rgb| rgb.iter()).copied().collect();
        println!("Flat pixel buffer size: {} bytes", flat_pixels.len());
        let mapped_pixels = map_pixels_to_curve(best_curve, &flat_pixels);
        let orig_path = &image_paths[i];
        let base_out_path = orig_path.to_string_lossy().replace("_input/", "_output/");
        let webp_path = {
            let mut p = PathBuf::from(&base_out_path);
            p.set_extension("webp");
            p.to_string_lossy().to_string()
        };
        let png_path = {
            let mut p = PathBuf::from(&base_out_path);
            p.set_extension("png");
            p.to_string_lossy().to_string()
        };
        let md_path = {
            let mut p = PathBuf::from(&base_out_path);
            p.set_extension("md");
            p.to_string_lossy().to_string()
        };
        match save_pixels_as_webp(&mapped_pixels, width, height, &webp_path, 80.0) {
            Ok(_) => {},
            Err(e) => eprintln!("❌ Failed to save WebP: {}", e),
        }
        match save_pixels_as_png(&mapped_pixels, width, height, &png_path) {
            Ok(_) => {},
            Err(e) => eprintln!("❌ Failed to save PNG: {}", e),
        }
        // Write markdown file with dimensions and curve display string
        let md_content = format!(
            "# Image Info\n\n- **Dimensions:** {}x{}\n\n## Curve Details\n\n{}\n",
            width, height, best_curve.describe()
        );
        if let Some(parent) = std::path::Path::new(&md_path).parent() {
            let _ = std::fs::create_dir_all(parent);
        }
        match std::fs::write(&md_path, md_content) {
            Ok(_) => println!("✅ Markdown info saved to {}", md_path),
            Err(e) => eprintln!("❌ Failed to save markdown: {}", e),
        }
    }

    println!("\n{}", "=".repeat(60));
    println!("🎯 Final Results Summary:");
    println!("{}", "=".repeat(60));
    
    for (i, curve) in best_curves.iter().enumerate() {
        println!("Image {}: {}", i + 1, curve.summary());
    }

    

}

/// Save the pixel data as a WebP image file
fn save_pixels_as_webp(pixels: &[u8], width: u32, height: u32, out_path: &str, quality: f32) -> std::io::Result<()> {
    // Create directory if it doesn't exist
    if let Some(parent) = std::path::Path::new(out_path).parent() {
        std::fs::create_dir_all(parent)?;
    }

    // Calculate correct dimensions based on actual data size
    let pixels_len = pixels.len();
    let channels = if pixels_len % 4 == 0 { 4 } else { 3 };
    let total_pixels = pixels_len / channels;
    
    // Terse debug info
    println!(
        "Dims: {}x{}, {} bytes, {} ch, {} px",
        width, height, pixels_len, channels, total_pixels
    );
    
    // Verify or recalculate dimensions
    let (actual_width, actual_height) = {
        if (width * height) as usize == total_pixels {
            // Dimensions match pixel count
            (width, height)
        } else {
            // Dimensions don't match, try to calculate them
            println!("⚠️ Dimension mismatch! Attempting to calculate correct dimensions...");
            // Try common image aspect ratios
            if total_pixels == 1920 * 1279 {
                println!("✅ Detected 1920x1279 image");
                (1920, 1279)
            } else if total_pixels == 1920 * 1280 {
                println!("✅ Detected 1920x1280 image");
                (1920, 1280)
            } else {
                // Keep width, adjust height
                let calculated_height = total_pixels as u32 / width;
                println!("⚠️ Using calculated dimensions: {}x{}", width, calculated_height);
                (width, calculated_height)
            }
        }
    };

    // Handle the WebP encoding based on channel count
    if channels == 3 {
        // Create temporary RGBA buffer for RGB input
        let mut rgba = Vec::with_capacity(total_pixels * 4);
        for chunk in pixels.chunks(3) {
            if chunk.len() < 3 {
                continue; // Skip incomplete chunks
            }
            rgba.push(chunk[0]);
            rgba.push(chunk[1]);
            rgba.push(chunk[2]);
            rgba.push(255); // Alpha
        }
        let encoder = Encoder::from_rgba(&rgba, actual_width, actual_height);
        let webp = encoder.encode(quality);
        
        let mut file = File::create(out_path)?;
        file.write_all(&webp)?;
        
        println!(
            "✅ WebP encoded and saved to {} ({}x{}, {} bytes, from RGB)",
            out_path,
            actual_width,
            actual_height,
            webp.len()
        );
    } else if channels == 4 {
        let encoder = Encoder::from_rgba(pixels, actual_width, actual_height);
        let webp = encoder.encode(quality);
        
        let mut file = File::create(out_path)?;
        file.write_all(&webp)?;
        
        println!("✅ WebP encoded and saved to {} ({}x{}, {} bytes, from RGBA)", 
                out_path, actual_width, actual_height, webp.len());
    } else {
        return Err(std::io::Error::new(
            std::io::ErrorKind::InvalidInput,
            format!("Unsupported channel count: {}", channels)
        ));
    }
    
    Ok(())
}

/// Save pixel data as PNG image
fn save_pixels_as_png(pixels: &[u8], width: u32, height: u32, out_path: &str) -> std::io::Result<()> {
    use image::{ImageBuffer, Rgba, RgbImage};
    
    // Create directory if it doesn't exist
    if let Some(parent) = std::path::Path::new(out_path).parent() {
        std::fs::create_dir_all(parent)?;
    }
    
    // Calculate correct dimensions based on actual data size
    let pixels_len = pixels.len();
    let channels = if pixels_len % 4 == 0 { 4 } else { 3 };
        
    // Choose the right approach based on channels
    if channels == 3 {
        // RGB image
        let img_buffer = RgbImage::from_raw(
            width, 
            height, 
            pixels.to_vec()
        ).ok_or_else(|| std::io::Error::new(
            std::io::ErrorKind::InvalidData, 
            format!("Failed to create RGB buffer: dimensions {}x{} don't match data size {}", 
                 width, height, pixels_len)
        ))?;
        
        img_buffer.save(out_path).map_err(|e| std::io::Error::new(
            std::io::ErrorKind::Other,
            format!("Failed to save PNG: {}", e)
        ))?;
    } else {
        // RGBA image
        let img_buffer = ImageBuffer::<Rgba<u8>, _>::from_raw(
            width,
            height,
            pixels.to_vec()
        ).ok_or_else(|| std::io::Error::new(
            std::io::ErrorKind::InvalidData,
            format!("Failed to create RGBA buffer: dimensions {}x{} don't match data size {}",
                   width, height, pixels_len)
        ))?;
        
        img_buffer.save(out_path).map_err(|e| std::io::Error::new(
            std::io::ErrorKind::Other,
            format!("Failed to save PNG: {}", e)
        ))?;
    }

    println!("✅ PNG saved to {} ({}x{} pixels)", out_path, width, height);
    Ok(())
}

/// Map each input pixel to the closest point on the curve, returning a new Vec<u8> in RGBA format
fn map_pixels_to_curve(curve: &PaletteCurve, input_pixels: &[u8]) -> Vec<u8> {
    let channels = if input_pixels.len() % 4 == 0 { 4 } else { 3 };
    let input_pixel_count = input_pixels.len() / channels;
    use indicatif::{ProgressBar, ProgressStyle};
    let pb = ProgressBar::new(input_pixel_count as u64);
    pb.set_style(
        ProgressStyle::default_bar()
            .template("{prefix} [{bar:20.magenta/white}] {pos}/{len}")
            .unwrap()
            .progress_chars("█▉▊▋▌▍▎▏ ")
    );
    pb.set_prefix("Converting pixels");
    let channels = if input_pixels.len() % 4 == 0 { 4 } else { 3 };
    
    // Calculate output dimensions
    let input_pixel_count = input_pixels.len() / channels;
    let mut output = Vec::with_capacity(input_pixel_count * 4); // Always RGBA output
    
    println!("{} Input pixels: {} bytes, {} channels per pixel", input_pixel_count, input_pixels.len(), channels);
    
    let curve_points = curve.points();

    // ...existing code...
    for chunk in input_pixels.chunks(channels) {
        if chunk.len() < 3 {
            println!("⚠️ Warning: Incomplete pixel data, skipping");
            continue;
        }
        
        // Convert chunk to models::imagetovec::Color and then to Vec3A
        let color = models::imagetovec::Color {
            r: chunk[0],
            g: chunk[1],
            b: chunk[2],
        };
        let input_vec = color.to_vec3a();
        
        let closest_point = curve_points
            .iter()
            .min_by(|a, b| {
                let da = (input_vec - **a).length_squared();
                let db = (input_vec - **b).length_squared();
                da.partial_cmp(&db).unwrap_or(std::cmp::Ordering::Equal)
            })
            .unwrap_or(&curve_points[0]);
    
        let closest_color = models::imagetovec::Color::from_vec3a(*closest_point);

        // Convert curve point to u8 RGB
        output.push(closest_color.r);
        output.push(closest_color.g);
        output.push(closest_color.b);
        output.push(255); // Always fully opaque
        pb.inc(1);
    }
    pb.finish_with_message("✓ Complete");
    // Manual ANSI color reset
    print!("\x1b[0m");
    
    println!("Generated {} bytes of RGBA data", output.len());
    output
}

