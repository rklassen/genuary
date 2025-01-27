from math import pi, sin, cos

# very approximate sinusoidal representation of an EKG signal
def simulated_ekg(period: float):
    t = pi * 2.0 * period
    phase = 3.0 * cos ( t )
    r_wave = -sin ( t + phase )
    q_scalar = 0.50 - 0.75 * sin ( t - 1.0 )
    s_scalar = 0.25 - 0.125 * sin ( 1.25 * phase - 1.0 )
    return 3.14 * q_scalar * r_wave * s_scalar
