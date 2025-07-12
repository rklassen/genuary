use glam::Vec3A;
use std::f32::consts::PI;
use rayon::prelude::*;
use crate::models::imagetovec::Color;
use std::collections::HashMap;
use std::fmt;
use indicatif::{ProgressBar, ProgressStyle};
use std::sync::{Arc, Mutex};

pub struct PaletteCurve {
    pub num_points: usize,
    pub amplitude: f32, // Combines amplitude and radius_scale into a single scaling factor
    pub oscilation: f32, // amplitude of an inner oscillation or secondary circle in the curve's shape.
    pub harmonic: usize,
    pub z_range: (f32, f32), // z range for the curve
    pub phi: f32, // phase shift
}

impl Clone for PaletteCurve {
    fn clone(&self) -> Self {
        PaletteCurve {
            num_points: self.num_points,
            amplitude: self.amplitude,
            oscilation: self.oscilation,
            harmonic: self.harmonic,
            z_range: self.z_range,
            phi: self.phi,
        }
    }
}

impl PaletteCurve {
    /// Create a new PaletteCurve with the given parameters
    pub fn sample(
        &self,
        t: f32,
    ) -> Vec3A {
        let theta = 2.0 * PI * self.harmonic as f32 * t;
        let r = self.amplitude * (3.0 * theta + self.phi).sin()
            + self.oscilation * (self.harmonic as f32 * theta).sin();
        
        let x = 0.5 + r * theta.cos() * self.amplitude;
        let y = 0.5 + r * theta.sin() * self.amplitude;
        let z = self.z_range.0 + t * (self.z_range.1 - self.z_range.0);

        Vec3A::new(
            x.clamp(0.0, 1.0),
            y.clamp(0.0, 1.0),
            z.clamp(0.0, 1.0),
        )
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

    /// Create a new PaletteCurve with default parameters
    pub fn new(
        num_points: usize,
        amplitude: f32,
        oscilation: f32,
        harmonic: usize,
        z_range: (f32, f32),
        phi: f32,
    ) -> Self {
        PaletteCurve {
            num_points,
            amplitude,
            oscilation,
            harmonic,
            z_range,
            phi,
        }
    }

    /// calculate error for a HashMap of colors with counts
    pub fn mean_square_error(
        &self,
        color_counts: &HashMap<Color, usize>,
    ) -> f32 {
        let mut total_error = 0.0;
        let mut total_count = 0;

        for (color, count) in color_counts {
            let vec3a = color.to_vec3a();
            let closest_point = self.get_closest_point(&vec3a);
            let error = closest_point.distance_squared(vec3a);
            total_error += error * (*count as f32);
            total_count += count;
        }

        total_error / total_count as f32
    }

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
                (0.0..=1.0).contains(&vec3a.x) &&
                (0.0..=1.0).contains(&vec3a.y) &&
                (0.0..=1.0).contains(&vec3a.z),
                "Each color component c must be 0.0 ≤ c ≤ 1.0."
            );
        }

        let search_range_z = (-1.0, 2.0);
        let search_range_amplitude = (0.0, 1.0);
        let search_range_oscilation = (-1.0, 2.0);
        let search_range_harmonic = (1, 8);
        let search_range_phi = (0f32, 2.0 * PI);

        let curves_per_parameter = 8;
        let n = curves_per_parameter as f32;
        let increment_z = (search_range_z.1 - search_range_z.0) / n;
        let increment_amplitude = (search_range_amplitude.1 - search_range_amplitude.0) / n;
        let increment_oscilation = (search_range_oscilation.1 - search_range_oscilation.0) / n;
        let increment_harmonic = (search_range_harmonic.1 - search_range_harmonic.0) as f32 / n;
        let increment_phi = (search_range_phi.1 - search_range_phi.0) / n;

        let mut curves = Vec::new();

        for z in (0..curves_per_parameter).map(|i| {
            search_range_z.0 + i as f32 * increment_z
        }) {
            for amplitude in (0..curves_per_parameter).map(|i| {
                search_range_amplitude.0 + i as f32 * increment_amplitude
            }) {
                for oscilation in (0..curves_per_parameter).map(|i| {
                    search_range_oscilation.0 + i as f32 * increment_oscilation
                }) {
                    for harmonic in (1..=search_range_harmonic.1).map(|i| {
                        i as f32 * increment_harmonic
                    }) {
                        for phi in (0..curves_per_parameter).map(|i| {
                            search_range_phi.0 + i as f32 * increment_phi
                        }) {
                            for z_range_index in 0..curves_per_parameter {
                                let z_range_min = z + increment_z * z_range_index as f32;
                                for z_range_max_index in z_range_index..curves_per_parameter {
                                    let z_range_max = z + increment_z * z_range_max_index as f32;
                                    if z_range_max < z_range_min {
                                        continue;
                                    }
                                    let curve = PaletteCurve::new(
                                        num_points,
                                        amplitude,
                                        oscilation,
                                        harmonic as usize,
                                        (z_range_min, z_range_max),
                                        phi,
                                    );
                                    
                                    curves.push(curve);
                                    
                                }
                            }                            
                        }
                    }
                }
            }
        }
        println!("Created {} curves for evaluation.", curves.len());

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
                let error = curve.mean_square_error(color_counts);
                
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
        format!(
            "PaletteCurve Analysis:\n\
            ┌─────────────────────────────────────┐\n\
            │ Parameters:                         │\n\
            │   • Sample Points: {:>15}    │\n\
            │   • Amplitude:     {:>15.4}    │\n\
            │   • Oscillation:   {:>15.4}    │\n\
            │   • Harmonic:      {:>15}    │\n\
            │   • Z Range:       ({:>6.3}, {:>6.3}) │\n\
            │   • Phase (φ):     {:>15.4}    │\n\
            │   • Phase (deg):   {:>12.1}°    │\n\
            ├─────────────────────────────────────┤\n\
            │ Curve Properties:                   │\n\
            │   • Z Span:        {:>15.4}    │\n\
            │   • Frequency:     {:>15.1}    │\n\
            │   • Complexity:    {:>15}    │\n\
            └─────────────────────────────────────┘",
            self.num_points,
            self.amplitude,
            self.oscilation,
            self.harmonic,
            self.z_range.0,
            self.z_range.1,
            self.phi,
            self.phi * 180.0 / PI,
            self.z_range.1 - self.z_range.0,
            self.harmonic as f32 * 2.0 * PI,
            if self.harmonic > 5 { "High" } else if self.harmonic > 2 { "Medium" } else { "Low" }
        )
    }

    /// Get a compact one-line summary
    pub fn summary(&self) -> String {
        format!(
            "PaletteCurve[pts={}, amp={:.3}, osc={:.3}, harm={}, z=({:.3},{:.3}), φ={:.3}]",
            self.num_points,
            self.amplitude, 
            self.oscilation,
            self.harmonic,
            self.z_range.0,
            self.z_range.1,
            self.phi
        )
    }
}

impl fmt::Display for PaletteCurve {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, 
            "PaletteCurve {{\n\
            \x20\x20num_points: {},\n\
            \x20\x20amplitude: {:.4},\n\
            \x20\x20oscillation: {:.4},\n\
            \x20\x20harmonic: {},\n\
            \x20\x20z_range: ({:.4}, {:.4}),\n\
            \x20\x20phi: {:.4} ({}°)\n\
            }}",
            self.num_points,
            self.amplitude,
            self.oscilation,
            self.harmonic,
            self.z_range.0,
            self.z_range.1,
            self.phi,
            self.phi * 180.0 / PI
        )
    }
}

impl fmt::Debug for PaletteCurve {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        f.debug_struct("PaletteCurve")
            .field("num_points", &self.num_points)
            .field("amplitude", &self.amplitude)
            .field("oscillation", &self.oscilation)
            .field("harmonic", &self.harmonic)
            .field("z_range", &self.z_range)
            .field("phi_radians", &self.phi)
            .field("phi_degrees", &(self.phi * 180.0 / PI))
            .finish()
    }
}