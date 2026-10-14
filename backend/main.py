from fastapi import FastAPI
from core.beam_models import create_spatial_grid, generate_gaussian_beam
from core.propagation import free_space_transfer_function, propagate_beam
import numpy as np

# 1. API Application initialising
app = FastAPI(title="FSO-QKD Simulation Engine")

# 2. Creating basic route/endpoint
@app.get("/")
def read_root():
    return {"status": "success", "message": "FSO-QKD Core Engine is running!"}

@app.get("/init-beam")
def initialize_beam(w0_mm: float=100.0, grid_size: int = 256, grid_length_m: float = 2.0):
    """ API endpoint jo frontend se beam ke parameters lega aur initial laser banayega.  """
    # 1. Grid formation
    X,Y,dx = create_spatial_grid(N=grid_size, L=grid_length_m)
    #2 Gaussian Laser Formation 
    field, peak_int = generate_gaussian_beam(X,Y,w0_mm)

    #sending JSON to react
    return {
        "message": "Gaussian beam successfully created",
        "parameters": {
            "beam_waist_mm": w0_mm,
            "grid_resolution": f"{grid_size}x{grid_size}",
            "physical_grid_size_m": grid_length_m
        },
        "metrics": {
            "peak_intensity": round(peak_int, 4)
        }
    }

@app.get("/propagate-test")
def test_propagation(distance_km: float = 10.0, w0_mm: float = 100.0, wavelength_nm: float = 1550.0):
    """ Ek test API jo laser banayegi aur usko 10km (ya given distance) aage propagate karegi. """
    
    # setting up parameters
    grid_size = 256
    grid_length_m = 2.0
    distance_m = distance_km*1000.0
    wavelength_m = wavelength_nm*1e-9

    # Initial beam formation
    X,Y,dx = create_spatial_grid(N= grid_size, L=grid_length_m)
    initial_field, initial_peak = generate_gaussian_beam(X,Y,w0_mm) 

    #beam Propagation
    H = free_space_transfer_function(N= grid_size, dx=dx, wavelength= wavelength_m, dz= distance_m)
    final_field = propagate_beam(initial_field,H)

    #finding Final itesity
    final_intensity = np.abs(final_field)**2
    final_peak = float(np.max(final_intensity))

    return {
        "message": f"Beam successfully propagated to {distance_km} km",
        "metrics": {
            "initial_peak_intensity": round(initial_peak, 4),
            "final_peak_intensity": round(final_peak, 4),
            "intensity_drop_percentage": round((1 - (final_peak/initial_peak)) * 100, 2)
        }
    }
