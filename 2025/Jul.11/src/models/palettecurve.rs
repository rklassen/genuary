use glam::Vec3A;
use std::{f32::consts::PI, path::PathBuf};
use rayon::prelude::*;
use crate::models::imagetovec::Color;
use std::collections::HashMap;
use std::fmt;
use indicatif::{ProgressBar, ProgressStyle};
use std::sync::{Arc, Mutex};
use rand::Rng;

const SEARCH_DEPTH: usize = 1 * 8192; // Number of random curves to generate for curve fitting

pub struct PaletteCurve {
    pub num_points: usize,
    pub amplitude: f32, // Combines amplitude and radius_scale into a single scaling factor
    pub amplitude_phase: f32, // phase shift for amplitude term
    pub harmonic: f32, // number of cycles per t from 0 to 1
    pub oscilation: f32, // Amplitude of an inner oscillation or secondary circle in the curve's shape.
    pub oscilation_phase: f32, // phase shift for oscilation term
}

impl Clone for PaletteCurve {
    fn clone(&self) -> Self {
        PaletteCurve {
            num_points: self.num_points,
            amplitude: self.amplitude,
            amplitude_phase: self.amplitude_phase,
            oscilation: self.oscilation,
            oscilation_phase: self.oscilation_phase,
            harmonic: self.harmonic,
        }
    }
}

impl PaletteCurve {
    /// Best fit a HashMap of colors with counts to a curve
    /// color_counts is a HashMap mapping colors to their occurrence counts
    /// returns a new PaletteCurve that best fits the given colors weighted by frequency
    pub fn best_fit(
        color_counts: &HashMap<Color, usize>,
        num_points: usize,
    ) -> Self {
        // Validate that all colors are in 0-1 range
        for color in color_counts.keys() {

            let (hue, sat, lum) = color.to_hsl();
            let vec3a = Color::to_vec3a(hue, sat, lum);
            assert!(
                (-1.0..=1.0).contains(&vec3a.x) &&
                (-1.0..=1.0).contains(&vec3a.y),
                "Each xy value must be -1.0 ≤ c ≤ 1.0, got xy = ({:.3}, {:.3})", vec3a.x, vec3a.y
            );
            assert!(
                0.0 <= vec3a.z &&
                1.0001 >= vec3a.z,
                "Z value must be 0.0 ≤ z ≤ 1.0, got z = {:.3}", vec3a.z
            );
        }

        let search_range_amplitude          = (0.1, 1.0);
        let search_range_amplitude_phase    = (0.0, 2.0 * PI);
        let search_range_oscilation         = (0.10, 1.0);
        let search_range_oscilation_phase   = (0.0, 2.0 * PI);
        // harmonic is a random f32 in [0,1]^2 * 8
        let mut rng = rand::thread_rng();
        let mut curves = Vec::with_capacity(SEARCH_DEPTH);

        for _ in 0..SEARCH_DEPTH {
            let amplitude = rng.gen_range(
                search_range_amplitude.0..=search_range_amplitude.1
            );
            let amplitude_phase = rng.gen_range(
                search_range_amplitude_phase.0..=search_range_amplitude_phase.1
            );
            let oscilation = rng.gen_range(
                search_range_oscilation.0..=search_range_oscilation.1
            );
            let oscilation_phase = rng.gen_range(
                search_range_oscilation_phase.0..=search_range_oscilation_phase.1,
            );

            let harmonic = {
                let r = rng.gen_range(0.0..=1.0);
                let r_squared = r * r * r;
                0.5f32 + r_squared * 4f32 // Scale to [1, 32]
            };

            let curve = PaletteCurve::new(
                num_points,
                amplitude,
                amplitude_phase,
                oscilation,
                oscilation_phase,
                harmonic,
            );
            curves.push(curve);
        }
        println!("Randomized {} curves for evaluation.", curves.len());

        // Create progress bar with custom style (32 chars max)
        let pb = ProgressBar::new(curves.len() as u64);
        pb.set_style(
            ProgressStyle::default_bar()
                .template("{prefix} [{bar:20.cyan/blue}] {pos}/{len}")
                .unwrap()
                .progress_chars("█▉▊▋▌▍▎▏ ")
        );
        pb.set_prefix("Evaluating");

        let pb_arc = Arc::new(Mutex::new(pb));

        let errors: Vec<f32> = curves
            .par_iter()
            .map(|curve| {
                let error = curve.mean_error(color_counts);
                // Update progress bar
                if let Ok(pb) = pb_arc.lock() {
                    pb.inc(1);
                }
                error
            }).collect();

        // Finish progress bar
        if let Ok(pb) = pb_arc.lock() {
            pb.finish_with_message("✓ Complete");
        }

        let (best_index, _) = errors
            .iter()
            .enumerate()
            .min_by(|a, b| a.1.partial_cmp(b.1).unwrap_or(std::cmp::Ordering::Equal))
            .unwrap_or((0, &f32::MAX));

        curves[best_index].clone()
    }

    /// Get a detailed multiline description of the curve
    pub fn describe(&self) -> String {
        [
            "| PaletteCurve      | Values  |",
            "|-------------------|---------|",
            &format!("| Sample Points     | {} |", self.num_points),
            &format!("| Amplitude         | {:.4} |", self.amplitude),
            &format!("| Amplitude Phase   | {:.4} |", self.amplitude_phase),
            &format!("| Oscillation       | {:.4} |", self.oscilation),
            &format!("| Oscillation Phase | {:.4} |", self.oscilation_phase),
            &format!("| Harmonic          | {:.4} |", self.harmonic),
        ].join("\n")
    }

    pub fn error(point: Vec3A, target: Vec3A) -> f32 {
        
        let computed_xy = Vec3A::new(point.x, point.y, 0.0);
        let target_xy = Vec3A::new(target.x, target.y, 0.0);
        // Compute the angle between computed_xy and target_xy as the hue error
        let dot = computed_xy.normalize().dot(target_xy.normalize()).clamp(-1.0, 1.0);
        let hue_error = dot.asin().abs()/PI; // Absolute angle, normalized to [0, 1]

        let computed_lum = computed_xy.length();
        let target_lum = target_xy.length();
        let lum_error = (computed_lum - target_lum).abs();

        let sat_error = (point.z - target.z).abs();

        hue_error + 1.24 * lum_error + 0.64 * sat_error

    }

    #[allow(dead_code)]
    /// Get the closest point on the curve to a given point
    pub fn get_closest_point(
        &self,
        point: &Vec3A,
    ) -> Vec3A {
        
        let points = self.points();
        points
            .into_iter()
            .min_by(|a, b| {
                PaletteCurve::error(*a, *point)
                    .partial_cmp(&PaletteCurve::error(*b, *point))
                    .unwrap_or(std::cmp::Ordering::Equal)
            })
            .unwrap_or(Vec3A::ZERO)

    }


    /// calculate error for a HashMap of colors with counts
    pub fn mean_error(
        &self,
        color_counts: &HashMap<Color, usize>,
    ) -> f32 {
        let mut total_error = 0.0;
        let mut total_count = 0;

        let points = self.points();

        for (color, count) in color_counts {
            let (hue, sat, lum) = color.to_hsl();
            let vec3a = Color::to_vec3a(hue, sat, lum);

            let error = points
                .iter()
                .map(|p| PaletteCurve::error(*p, vec3a))
                .fold(f32::MAX, |acc, e| acc.min(e));

            total_error += error * (*count as f32);
            total_count += count;
        }

        total_error / total_count as f32
    }

    /// Create a new PaletteCurve with default parameters
    pub fn new(
        num_points: usize,
        amplitude: f32,
        amplitude_phase: f32,
        oscilation: f32,
        oscilation_phase: f32,
        harmonic: f32,
    ) -> Self {
        PaletteCurve {
            num_points,
            amplitude,
            amplitude_phase,
            oscilation,
            oscilation_phase,
            harmonic,
        }
    }

    /// Create points3d, each in radial value, angular color, and z = sat
    pub fn points(&self) -> Vec<Vec3A> {
        (0..self.num_points)
            .map(|i| {
                let t = i as f32 / (self.num_points - 1).max(1) as f32;
                self.sample(t)
            })
            .collect()
    }

    /// Create a new PaletteCurve with the given parameters
    ///
    /// - `harmonic`: Number of cycles in the XY plane (frequency)
    pub fn sample(
        &self,
        t: f32,
    ) -> Vec3A {
        // theta cycles harmonic times in the XY plane as t goes from 0 to 1
        let random_scale = rand::random::<f32>() * 1.0 + 0.5; // [0.5, 1.5)
        let theta = 2.0 * PI * self.harmonic * t * random_scale;
        let r = self.amplitude * (theta + self.amplitude_phase).sin()
            + self.oscilation * (self.harmonic * theta + self.oscilation_phase).sin();

        let x = r * theta.cos() * self.amplitude;
        let y = r * theta.sin() * self.amplitude;
        let z = t;

        Vec3A::new(
            x.clamp(-1.0, 1.0),
            y.clamp(-1.0, 1.0),
            z.clamp(0.0, 1.0),
        )
    }


    /// Get a compact one-line summary
    pub fn summary(&self) -> String {
        format!(
            "PaletteCurve[pts={}, amp={:.3}, amp_phase={:.3}, osc={:.3}, osc_phase={:.3}, harm={:.3}]",
            self.num_points,
            self.amplitude,
            self.amplitude_phase,
            self.oscilation,
            self.oscilation_phase,
            self.harmonic,
        )
    }

    pub fn to_png(
        &self,
        pathbuf: PathBuf
    ) -> Result<(), image::ImageError> {

        use image::{RgbImage, Rgb};
        let colors_hsl = self.points()
            .iter()
            .map(|p| {
                let (hue, sat, lum) = Color::vec3a_to_hsl(*p);
                let color= Color::from_hsl(hue, sat, lum);
                (color, (hue, sat, lum))
            })
            .collect::<Vec<_>>();
        let grid_size = 16;
        let square_size = 8;
        let img_size = grid_size * square_size; // 1024
        let mut img = RgbImage::new(img_size as u32, img_size as u32);

        for idx in 0..colors_hsl.len().min(grid_size * grid_size) {
            let (color, _hsl) = &colors_hsl[idx];
            let gx = idx % grid_size;
            let gy = idx / grid_size;
            let x0 = gx * square_size;
            let y0 = gy * square_size;
            let rgb = Rgb([color.r, color.g, color.b]);
            for dy in 0..square_size {
                for dx in 0..square_size {
                    img.put_pixel((x0 + dx) as u32, (y0 + dy) as u32, rgb);
                }
            }
        }
        img.save(pathbuf)?;
        Ok(())
    }

}

impl fmt::Display for PaletteCurve {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, 
            "| Parameter         | Value      |\n\
            |-------------------|-----------|\n\
            | num_points        | {}        |\n\
            | amplitude         | {:.4}     |\n\
            | amplitude_phase   | {:.4}     |\n\
            | oscillation       | {:.4}     |\n\
            | oscillation_phase | {:.4}     |\n\
            | harmonic          | {:.4}     |\n\
",
            self.num_points,
            self.amplitude,
            self.amplitude_phase,
            self.oscilation,
            self.oscilation_phase,
            self.harmonic,
        )
    }
}

impl fmt::Debug for PaletteCurve {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        f.debug_struct("PaletteCurve")
            .field("num_points", &self.num_points)
            .field("amplitude", &self.amplitude)
            .field("amplitude_phase", &self.amplitude_phase)
            .field("oscillation", &self.oscilation)
            .field("oscillation_phase", &self.oscilation_phase)
            .field("harmonic", &self.harmonic)
            .finish()
    }
}