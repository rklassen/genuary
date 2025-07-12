# preview the best fit curve for PaletteCurve

import numpy as np
import matplotlib.pyplot as plt

def sample_curve(n_points, amplitude, amplitude_phase, oscilation, oscilation_phase, harmonic, z_range):
    t_vals = np.linspace(0, 1, n_points)
    points = []
    random_scale = np.random.uniform(0.5, 1.5)
    for t in t_vals:
        theta = 2.0 * np.pi * harmonic * t * random_scale
        r = amplitude * np.sin(theta + amplitude_phase) + oscilation * np.sin(harmonic * theta + oscilation_phase)
        x = 0.5 + r * np.cos(theta) * amplitude
        y = 0.5 + r * np.sin(theta) * amplitude
        z = z_range[0] + t * (z_range[1] - z_range[0])
        x = np.clip(x, 0.0, 1.0)
        y = np.clip(y, 0.0, 1.0)
        z = np.clip(z, 0.0, 1.0)
        points.append((x, y, z))
    return np.array(points)

def random_harmonic():
    return np.random.uniform(0, 1) ** 2 * 8

# Parameters from best fit curve
n_curves = 1
n_points = 255
amplitude = 0.5673
amplitude_phase = 0.5791
oscilation = 0.3849
oscilation_phase = 2.3699
harmonic = 2.5934
z_min = 0.361
z_max = 0.456

fig = plt.figure(figsize=(12, 8))
ax = fig.add_subplot(111, projection='3d')

for _ in range(n_curves):
    points = sample_curve(n_points, amplitude, amplitude_phase, oscilation, oscilation_phase, harmonic, (z_min, z_max))
    ax.plot(points[:,0], points[:,1], points[:,2])

ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')
plt.title('PaletteCurve Preview (Best Fit Parameters)')
plt.show()