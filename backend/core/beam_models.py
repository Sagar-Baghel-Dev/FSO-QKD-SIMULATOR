import numpy as np

def create_spatial_grid(N: int, L: float):
    """ Ek 2D grid banata hai laser simulation ke liye.
    N: Grid resolution (jaise 256, 512)
    L: Physical size meters mein (jaise 2.0 m) """
    dx = L/N
    x = np.linspace(-L/2, L/2, N)
    X,Y = np.meshgrid(x,x)
    return X,Y, dx

def generate_gaussian_beam(X,Y, w0_mm: float):
    """ek basic Gaussian laser beam initialize karta hai.
    w0_mm: Beam ki initial waist millimeters mein. """

    w0_m = w0_mm* 1e-3

    field = np.exp(-(X**2 + Y**2) / (w0_m**2)).astype(complex)
    intensity = np.abs(field)**2
    peak_intensity= float(np.max(intensity))
    return field, peak_intensity
