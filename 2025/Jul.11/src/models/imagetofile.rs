use image::{ImageBuffer, Rgba, RgbImage};
use std::fs::File;
use std::io::Write;
use webp::Encoder;

pub fn save_pixels_as_webp(
    pixels: &[u8],
    width: u32,
    height: u32,
    out_path: &str,
    quality: f32,
) -> std::io::Result<()> {
    // Create directory if it doesn't exist
    if let Some(parent) = std::path::Path::new(out_path).parent() {
        std::fs::create_dir_all(parent)?;
    }
    let pixels_len = pixels.len();
    let channels = if pixels_len % 4 == 0 { 4 } else { 3 };
    if channels == 3 {
        let mut rgba = Vec::with_capacity(pixels_len / 3 * 4);
        for chunk in pixels.chunks(3) {
            if chunk.len() < 3 {
                continue;
            }
            rgba.push(chunk[0]);
            rgba.push(chunk[1]);
            rgba.push(chunk[2]);
            rgba.push(255);
        }
        let encoder = Encoder::from_rgba(&rgba, width, height);
        let webp = encoder.encode(quality);
        let mut file = File::create(out_path)?;
        file.write_all(&webp)?;
    } else if channels == 4 {
        let encoder = Encoder::from_rgba(pixels, width, height);
        let webp = encoder.encode(quality);
        let mut file = File::create(out_path)?;
        file.write_all(&webp)?;
    } else {
        return Err(std::io::Error::new(
            std::io::ErrorKind::InvalidInput,
            format!("Unsupported channel count: {}", channels)
        ));
    }
    Ok(())
}
