import numpy as np 

def generate_phase_screen(N: int, dx: float, Cn2: float, wavelength: float, dz: float, seed: int = None):
    """ randome phase screen creation using kolmogorov turbulence spectrum model """

    if seed is not None:
        np.random.seed(seed)

    k = 2*np.pi / wavelength

    #spatial grid creation
    fx = np.fft.fftfreq(N, d=dx)
    FX, FY = np.meshgrid(fx, fx)
    K_transverse_sq = (2 * np.pi * FX)**2 + (2 * np.pi * FY)**2

    #to prevent error of divide by zero at centre
    K_transverse_sq[0, 0] = 1e-10
    K_mag = np.sqrt(K_transverse_sq)

    #kolmogorv spectrum formula
    Phi_n = 0.033 * Cn2 * (K_mag ** (-11/3))

    # Phase variance spectrum
    delta_k = 2 * np.pi / (N * dx)
    F_phi = 2 * np.pi * (k**2) * dz * Phi_n * (delta_k**2)
    F_phi[0, 0] = 0.0

    #random noise generation
    random_noise = (np.random.randn(N, N) + 1j * np.random.randn(N, N)) / np.sqrt(2)

    #scaling noise according to kolmogorov spectrum model
    complex_phase = random_noise * np.sqrt(F_phi)

    #phase screen finding usng inversse fft 
    phase_screen = np.fft.ifft2(complex_phase).real * (N**2)
    
    return phase_screen