use image::{GenericImageView, Pixel};
use glam::Vec3A;
use std::collections::HashMap;

#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash)]
pub struct Color {
    pub r: u8,
    pub g: u8,
    pub b: u8,
}

impl Color {
    pub fn to_vec3a(&self) -> Vec3A {
        // Convert RGB to floats in [0,1]
        let r = self.r as f32 / 255.0;
        let g = self.g as f32 / 255.0;
        let b = self.b as f32 / 255.0;
        // Convert to HSL
        let max = r.max(g).max(b);
        let min = r.min(g).min(b);
        let lum = (max + min) / 2.0;
        let delta = max - min;
        let sat = {
            if delta == 0.0 { 0.0 }
            else { delta / (1.0 - (2.0 * lum - 1.0).abs()) }
        };
        let hue = if delta == 0.0 {
            0.0
        } else {
            match max {
            _ if max == r => 60.0 * ((g - b) / delta).rem_euclid(6.0),
            _ if max == g => 60.0 * ((b - r) / delta + 2.0),
            _ => 60.0 * ((r - g) / delta + 4.0),
            }
        };
        // Normalize hue to [0,1]
        let hue_norm = ((hue / 360.0) + 1.0) % 1.0;
        let theta = hue_norm * 2.0 * std::f32::consts::PI;
        let radius = lum;
        let x = radius * theta.cos();
        let y = radius * theta.sin();
        let z = sat;
        Vec3A::new(x, y, z)
    }

    pub fn from_vec3a(vec: Vec3A) -> Self {
        // Convert HSL to RGB
        let theta = vec.x.atan2(vec.y);
        let radius = vec.length();
        let sat = vec.z;
        let hue = theta.rem_euclid(2.0 * std::f32::consts::PI) / (2.0 * std::f32::consts::PI);
        let lum = radius;

        // Convert to RGB
        let c = (1.0 - (2.0 * lum - 1.0).abs()) * sat;
        let x = c * (1.0 - (hue * 6.0 % 2.0 - 1.0).abs());
        let m = lum - c / 2.0;

        let (r, g, b) = match hue {
            h if h < 1.0 / 6.0 => (c, x, 0.0),
            h if h < 2.0 / 6.0 => (x, c, 0.0),
            h if h < 3.0 / 6.0 => (0.0, c, x),
            h if h < 4.0 / 6.0 => (0.0, x, c),
            h if h < 5.0 / 6.0 => (x, 0.0, c),
            _ => (c, 0.0, x),
        };

        Color {
            r: ((r + m) * 255.0).clamp(0.0, 255.0) as u8,
            g: ((g + m) * 255.0).clamp(0.0, 255.0) as u8,
            b: ((b + m) * 255.0).clamp(0.0, 255.0) as u8,
        }
    }
}

/// Convert an image file to a vector of u8 RGB pixels and return dimensions
pub fn image_to_vec_u8rgb(
    path: &str
) -> Result<(Vec<[u8; 4]>, u32, u32), image::ImageError> {
    let img = image::open(path)?;
    let (width, height) = img.dimensions();
    let mut pixels = Vec::with_capacity((width * height) as usize);

    for (_, _, pixel) in img.pixels() {
        let rgb = pixel.to_rgb();
        pixels.push([rgb[0], rgb[1], rgb[2], 255]);
    }

    Ok((pixels, width, height))
}

pub fn u8rgba_to_color_counts(pixels: Vec<[u8; 4]>) -> HashMap<Color, usize> {
    let mut counts: HashMap<Color, usize> = HashMap::new();

    for pixel in pixels.iter() {
        let color = Color {
            r: pixel[0],
            g: pixel[1],
            b: pixel[2],
        };
        *counts.entry(color).or_insert(0) += 1;
    }

    counts
}
