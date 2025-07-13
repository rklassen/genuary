# preview the best fit curve for PaletteCurve

import numpy as np
import matplotlib.pyplot as plt

def sample_curve(
    n_points,
    amplitude,
    amplitude_phase,
    oscilation,
    oscilation_phase,
    harmonic,
):
    t_vals = np.linspace(0, 1, n_points)
    points = []
    random_scale = np.random.uniform(0.5, 1.5)
    for t in t_vals:
        theta = 2.0 * np.pi * harmonic * t * random_scale
        r = amplitude * np.sin(theta + amplitude_phase) + oscilation * np.sin(harmonic * theta + oscilation_phase)
        x = r * np.cos(theta) * amplitude
        y = r * np.sin(theta) * amplitude
        z = t
        # Match Rust clamping: x, y, z in [0.0, 1.0]
        x = np.clip(x, -1.0, 1.0)
        y = np.clip(y, -1.0, 1.0)
        z = np.clip(z, 0.0, 1.0)
        points.append((x, y, z))
    return np.array(points)

def random_harmonic():
    return np.random.uniform(0, 1) ** 2 * 8

# Parameters from best fit curve
n_curves = 1
n_points = 255
amplitude = 0.1
amplitude_phase = 0.0
oscilation = 0.1
oscilation_phase = 0
harmonic = 1.0

fig = plt.figure(figsize=(12, 8))
ax = fig.add_subplot(111, projection='3d')

for _ in range(n_curves):
    points = sample_curve(
        n_points,
        amplitude,
        amplitude_phase,
        oscilation,
        oscilation_phase,
        harmonic
    )
    ax.plot(points[:,0], points[:,1], points[:,2])

ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')
plt.title('PaletteCurve Preview (Best Fit Parameters)')
plt.show()