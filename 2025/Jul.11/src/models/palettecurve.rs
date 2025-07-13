use glam::Vec3A;
use std::f32::consts::PI;
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
    pub oscilation: f32, // Amplitude of an inner oscillation or secondary circle in the curve's shape.
    pub oscilation_phase: f32, // phase shift for oscilation term
    pub harmonic: f32, // number of cycles per t from 0 to 1
    pub z_range: (f32, f32), // z range for the curve
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
            z_range: self.z_range,
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
            let vec3a = color.to_vec3a();
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

        let search_range_z = (0.0, 1.0);
        let search_range_amplitude = (0.0, 1.0);
        let search_range_amplitude_phase = (0.0, 2.0 * PI);
        let search_range_oscilation = (-1.0, 2.0);
        let search_range_oscilation_phase = (0.0, 2.0 * PI);
        // harmonic is a random f32 in [0,1]^2 * 8
        let mut rng = rand::thread_rng();
        let mut curves = Vec::with_capacity(SEARCH_DEPTH);

        for _ in 0..SEARCH_DEPTH {
            let amplitude = rng.gen_range(search_range_amplitude.0..=search_range_amplitude.1);
            let amplitude_phase = rng.gen_range(search_range_amplitude_phase.0..=search_range_amplitude_phase.1);
            let oscilation = rng.gen_range(search_range_oscilation.0..=search_range_oscilation.1);
            let oscilation_phase = rng.gen_range(search_range_oscilation_phase.0..=search_range_oscilation_phase.1);
            
            let harmonic = {
                let r = rng.gen_range(0.0..=1.0);
                let r_squared = r * r;
                1f32 + r_squared * 7f32 // Scale to [1, 8]
            };

            let z_min = rng.gen_range(search_range_z.0..=search_range_z.1);
            let z_max = rng.gen_range(z_min..=search_range_z.1);
            let curve = PaletteCurve::new(
                num_points,
                amplitude,
                amplitude_phase,
                oscilation,
                oscilation_phase,
                harmonic,
                (z_min, z_max),
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

    #[allow(dead_code)]
    /// Sample `n` points along the curve and convert each Vec3A to Color
    pub fn colors(&self) -> Vec<Color> {
        (0..self.num_points)
            .map(|i| {
                let t = i as f32 / (self.num_points - 1).max(1) as f32;
                let vec = self.sample(t);
                Color::from_vec3a(vec)
            })
            .collect()
    }

    /// Get a detailed multiline description of the curve
    pub fn describe(&self) -> String {
        let desc = format!(
            "PaletteCurve Analysis:\n\
──────────────────────────────────────────────\n\
 Parameters:                                 \n\
   • Sample Points:      {:>4}               \n\
   • Amplitude:          {:>8.4}             \n\
   • Amplitude Phase:    {:>8.4}             \n\
   • Oscillation:        {:>8.4}             \n\
   • Oscillation Phase:  {:>8.4}             \n\
   • Harmonic:           {:>8.4}             \n\
   • Complexity:         {:<8}               \n\
──────────────────────────────────────────────\n",
            self.num_points,
            self.amplitude,
            self.amplitude_phase,
            self.oscilation,
            self.oscilation_phase,
            self.harmonic,
            if self.harmonic > 5.0 { "High" } else if self.harmonic > 2.0 { "Medium" } else { "Low" }
        );

        desc
    }

    /// Get the closest t value on the curve to a given point
    pub fn get_closest_t(
        &self,
        point: &Vec3A,
    ) -> f32 {

        let closest_t = (0..self.num_points)
            .map(|i| {
                let t = i as f32 / self.harmonic as f32;
                let sample_point = self.sample(t);
                let distance = sample_point.distance(*point);
                (t, distance)
            })
            .min_by(|a, b| {
                a.1.partial_cmp(&b.1)
                    .unwrap_or(std::cmp::Ordering::Equal)
            })
            .map(|(t, _)| t)
            .unwrap_or(0.0);

        closest_t
    }

    pub fn get_closest_point(
        &self,
        point: &Vec3A,
    ) -> Vec3A {
        let closest_t = self.get_closest_t(point);
        self.sample(closest_t)
    }

    /// calculate error for a HashMap of colors with counts
    pub fn mean_error(
        &self,
        color_counts: &HashMap<Color, usize>,
    ) -> f32 {
        let mut total_error = 0.0;
        let mut total_count = 0;

        for (color, count) in color_counts {
            let vec3a = color.to_vec3a();
            let closest_point = self.get_closest_point(&vec3a);
            let distance = closest_point.distance(color.to_vec3a());
            let error = distance.powi(3);
            // println!(
            //     "Color: ({:.3}, {:.3}, {:.3}), Closest Point: ({:.3}, {:.3}, {:.3}), Error: {:.3}",
            //     vec3a.x, vec3a.y, vec3a.z,
            //     closest_point.x, closest_point.y, closest_point.z,
            //     error
            // );
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
        z_range: (f32, f32),
    ) -> Self {
        PaletteCurve {
            num_points,
            amplitude,
            amplitude_phase,
            oscilation,
            oscilation_phase,
            harmonic,
            z_range,
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
        let z = self.z_range.0 + t * (self.z_range.1 - self.z_range.0);

        Vec3A::new(
            x.clamp(0.0, 1.0),
            y.clamp(0.0, 1.0),
            z.clamp(0.0, 1.0),
        )
    }


    /// Get a compact one-line summary
    pub fn summary(&self) -> String {
        format!(
            "PaletteCurve[pts={}, amp={:.3}, amp_phase={:.3}, osc={:.3}, osc_phase={:.3}, harm={:.3}, z=({:.3},{:.3})]",
            self.num_points,
            self.amplitude,
            self.amplitude_phase,
            self.oscilation,
            self.oscilation_phase,
            self.harmonic,
            self.z_range.0,
            self.z_range.1
        )
    }
}

impl fmt::Display for PaletteCurve {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, 
            "PaletteCurve {{\n\
            \x20\x20num_points: {},\n\
            \x20\x20amplitude: {:.4},\n\
            \x20\x20amplitude_phase: {:.4},\n\
            \x20\x20oscillation: {:.4},\n\
            \x20\x20oscillation_phase: {:.4},\n\
            \x20\x20harmonic: {:.4},\n\
            \x20\x20z_range: ({:.4}, {:.4})\n\
            }}",
            self.num_points,
            self.amplitude,
            self.amplitude_phase,
            self.oscilation,
            self.oscilation_phase,
            self.harmonic,
            self.z_range.0,
            self.z_range.1
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
            .field("z_range", &self.z_range)
            .finish()
    }
}