from fastapi import FastAPI
from core.beam_models import create_spatial_grid, generate_gaussian_beam
from core.propagation import free_space_transfer_function, propagate_beam, apply_phase_screen
from core.geometry import get_trajectory_altitudes
from core.turbulence import generate_phase_screen
from core.metrics import calculate_beam_wander, calculate_scintillation
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

@app.get("/calculate_trajectory")
def calculate_trajectory(distance_km: float = 100.0, tx_altitude_m: float = 15.0):
    distance_m = distance_km * 1000.0
    z_points, altitudes = get_trajectory_altitudes(
        total_distance_m=distance_m, 
        tx_altitude_m=tx_altitude_m,
        num_points=10  # for testing dividing the path in 10parts
    )

    return {
        "message": "Earth curvature trajectory calculated successfully",
        "parameters": {
            "total_distance_km": distance_km,
            "transmitter_altitude_m": tx_altitude_m
        },
        "trajectory": {
            "distances_m": z_points,
            "altitudes_m": [round(alt, 2) for alt in altitudes]
        }
    }

@app.get("/propagate-turbulence")
def test_turbulence_propagation(distance_km: float=1.0, Cn2: float= 1e-1, seed: int=42):
    """ passing laser through phase screens"""
    grid_size = 256
    grid_length_m = 0.5
    wavelength_m = 1550e-9
    distance_m = distance_km * 1000.0

    #initial beam formation
    X, Y, dx = create_spatial_grid(N=grid_size, L=grid_length_m)
    initial_field, initial_peak = generate_gaussian_beam(X, Y, w0_mm=50.0)

    #phase screen generation
    phase_screen = generate_phase_screen(N=grid_size, dx=dx, Cn2=Cn2, wavelength=wavelength_m, dz=distance_m, seed=seed )

    #passing Beam through phase screen
    distorted_field = apply_phase_screen(initial_field, phase_screen)

    #propagating distroted beam in free space 
    H = free_space_transfer_function(N=grid_size, dx=dx, wavelength=wavelength_m, dz=distance_m)
    final_field = propagate_beam(distorted_field, H)

    #final metrics
    final_intensity = np.abs(final_field)**2
    final_peak = float(np.max(final_intensity))
    wander_m = calculate_beam_wander(final_intensity, X, Y)
    scint_index = calculate_scintillation(final_intensity)

    return {
        "message": "Beam propagated and metrics calculated",
        "metrics": {
            "initial_peak": round(initial_peak, 4),
            "final_peak": round(final_peak, 4),
            "intensity_drop_percentage": round((1 - (final_peak/initial_peak)) * 100, 2),
            "beam_wander_mm": round(wander_m * 1000, 4),  # mm mein convert kiya
            "scintillation_index": round(scint_index, 4)
        }
    }

