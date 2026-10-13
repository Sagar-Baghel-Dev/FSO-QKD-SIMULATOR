from fastapi import FastAPI
from core.beam_models import create_spatial_grid, generate_gaussian_beam

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
