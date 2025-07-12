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
        Vec3A::new(
            self.r as f32 / 255.0,
            self.g as f32 / 255.0,
            self.b as f32 / 255.0,
        )
    }
}

/// Convert an image file to a vector of u8 RGB pixels
pub fn image_to_vec_u8rgb(
    path: &str
) -> Result<Vec<[u8; 3]>, image::ImageError> {
    let img = image::open(path)?;
    let (width, height) = img.dimensions();
    let mut pixels = Vec::with_capacity((width * height) as usize);

    for (_, _, pixel) in img.pixels() {
        let rgb = pixel.to_rgb();
        pixels.push([rgb[0], rgb[1], rgb[2]]);
    }

    Ok(pixels)
}

pub fn u8rgba_to_color_counts(pixels: Vec<[u8; 3]>) -> HashMap<Color, usize> {
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
