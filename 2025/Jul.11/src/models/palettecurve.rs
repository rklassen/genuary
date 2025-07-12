use glam::Vec3A;
use std::f32::consts::PI;

pub struct PaletteCurve {
    pub num_points: usize,
    pub amplitude: f32, // Combines amplitude and radius_scale into a single scaling factor
    pub oscilation: f32, // amplitude of an inner oscillation or secondary circle in the curve's shape.
    pub harmonic: usize,
    pub z_range: (f32, f32), // z range for the curve
    pub phi: f32, // phase shift
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

    /// calculate error for an array of vecs
    pub fn mean_square_error(
        &self,
        points: &[Vec3A],
    ) -> f32 {
        points.iter()
            .map(|p| {
                self.get_closest_point(p).distance_squared(*p)
            })
            .sum::<f32>() / points.len() as f32
    }

    /// Best fit an array of vec3a's to a curve
    /// colors are assumedly clamped in unit range [0.0, 1.0]
    pub fn best_fit(
        colors: &[Vec3A],
        num_points: usize,
    ) -> Self {
   
        assert!(
            colors.iter().all(|p| {
                (0.0..=1.0).contains(&p.x) &&
                (0.0..=1.0).contains(&p.y) &&
                (0.0..=1.0).contains(&p.z)
            }),
            "Each color component c must be 0.0 ≤ c ≤ 1.0."
        );

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
        let errors = Vec::new();

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
                                    let error = curve.mean_square_error(colors);
                                    curves.push(curve);
                                    errors.push(error);
                                }
                            }                            
                        }
                    }
                }
            }
        }

        let (best_index, _) = errors
            .iter()
            .enumerate()
            .min_by(|a, b| a.1.partial_cmp(b.1).unwrap_or(std::cmp::Ordering::Equal))
            .unwrap_or((0, &f32::MAX));

        curves[best_index].clone()

    }
}