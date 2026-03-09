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

    pub fn from_hsl(hue: f32, sat: f32, lum: f32) -> Self {
        let tolerance = 2e-2;
        assert!(
            (lum >= -tolerance) && (lum <= 1.0 + tolerance),
            "lum must be between 0.0 and 1.0 (±{}), got {}",
            tolerance,
            lum
        );
        assert!(
            (sat >= -tolerance) && (sat <= 1.0 + tolerance),
            "sat must be between 0.0 and 1.0 (±{}), got {}",
            tolerance,
            sat
        );
        assert!(
            (hue >= -tolerance) && (hue <= 1.0 + tolerance),
            "hue must be between 0.0 and 1.0 (±{}), got {}",
            tolerance,
            hue
        );
        // Clamp lum after assertion

        let theta = hue * 2.0 * std::f32::consts::PI;
        let radius = lum;
        let x = radius * theta.cos();
        let y = radius * theta.sin();
        let z = sat;

        // Convert to RGB
        let r = ((x + y) * 255.0).round() as u8;
        let g = ((y - x) * 255.0).round() as u8;
        let b = (z * 255.0).round() as u8;

        Color { r, g, b }
    }

    pub fn random() -> Self {
        use rand::Rng;
        let mut rng = rand::thread_rng();
        Color {
            r: rng.gen_range(0..=255),
            g: rng.gen_range(0..=255),
            b: rng.gen_range(0..=255),
        }
    }

    pub fn to_hsl(&self) -> (f32, f32, f32) {
        // convert `float` to `u8`
        let [r, g, b] = [self.r, self.g, self.b].map(|v| v as f32 / 255.0);
        // Convert to HSL
        let (min, max) = (r.min(g).min(b), r.max(g).max(b));
        let lum = (max + min) / 2.0;
        let delta = max - min;
        let sat = if delta == 0.0 { 0.0 } else { delta / (1.0 - (2.0 * lum - 1.0).abs()) };
        let hue = if delta == 0.0 {
            0.0
        } else {
            let h = match max {
                _ if max == r => ((g - b) / delta).rem_euclid(6.0),
                _ if max == g => (b - r) / delta + 2.0,
                _ => (r - g) / delta + 4.0,
            };
            h / 6.0 // scale [0,6) to [0,1)
        };
        (hue, sat, lum)
    }

    pub fn to_vec3a(
        hue: f32,
        sat: f32,
        lum: f32,
    ) -> Vec3A {
        
        assert!((hue >= 0.0) && (hue <= 1.0), "hue must be between 0.0 and 1.0, got {}", hue);

        let theta = hue * 2.0 * std::f32::consts::PI;
        let radius = lum;
        let x = radius * theta.cos();
        let y = radius * theta.sin();
        let z = sat;
        Vec3A::new(x, y, z)
    }

    pub fn vec3a_to_hsl(vec: Vec3A) -> (f32, f32, f32) {
        // Convert Vec3A to HSL
        let theta = vec.x.atan2(vec.y);
        let v_2d = Vec3A::new(vec.x, vec.y, 0.0);
        let lum = v_2d.length().min(1f32);
        let sat = vec.z.clamp(0.0, 1.0);
        let hue = theta.rem_euclid(2.0 * std::f32::consts::PI) / (2.0 * std::f32::consts::PI);

        let mut hue = hue;
        if hue < 0.0 {
            hue += 1.0;
        } else if hue > 1.0 {
            hue -= 1.0;
        }

        assert!((hue >= 0.0) && (hue <= 1.0), "check internal math in imagetovec::Color::vec3a_to_hsl.\nhue must be between 0.0 and 1.0, got {}", hue);
        assert!((sat >= 0.0) && (sat <= 1.0), "check internal math in imagetovec::Color::vec3a_to_hsl.\nsat must be between 0.0 and 1.0, got {}", sat);
        assert!((lum >= 0.0) && (lum <= 1.0), "check internal math in imagetovec::Color::vec3a_to_hsl.\nlum must be between 0.0 and 1.0, got {}", lum);

        (hue, sat, lum)
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
