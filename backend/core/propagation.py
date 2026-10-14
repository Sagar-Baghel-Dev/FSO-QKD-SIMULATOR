import numpy as np
def free_space_transfer_function(N: int, dx: float, dz:float, wavelength: float):
    """ Laser ko 'dz' distance aage badhane ka mathematical formula (Transfer Function)."""
    # wave number K
    k = 2*np.pi/wavelength

    #spatial freq
    fx = np.fft.fftfreq(N,d=dx)
    FX, FY= np.meshgrid(fx,fx)

    #transverse spatial freq
    k_transverse_sq = (2*np.pi*FX)**2 + (2*np.pi*FY)**2

    #fresenal propagation (transfer Function H)
    H = np.exp(-1j*(k_transverse_sq / (2*k))*dz)
    return H

def propagate_beam (field,H):
    """ Laser beam par transfer function lagakar usko aage badhana using FFT. """

    #beam ko freq me todna
    field_fft = np.fft.fft2(field)

    #distance effect Multiply by H
    field_fft_propagated = field_fft * H

    #inverse FFt
    field_out = np.fft.ifft2(field_fft_propagated)

    return field_out
