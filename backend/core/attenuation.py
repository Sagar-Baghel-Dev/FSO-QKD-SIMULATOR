import numpy as np

def calculate_atmospheric_attenuation(distance_km: float, attenuation_coeff_db_per_km: float = 0.2):
    """ calculates beam loss using beer lambert law """
    # Total loss in decibels (dB)
    total_attenuation_db = attenuation_coeff_db_per_km * distance_km
    
    # Transmittance: Yani actual mein kitne percentage roshni bachi hai (0.0 se 1.0 ke beech)
    # Physics formula: T = 10^(-dB/10)
    transmittance = 10 ** (-total_attenuation_db / 10.0)
    
    return float(transmittance), float(total_attenuation_db)

def apply_attenuation(intensity, transmittance: float):
    """final loss on laser intensity """
    return intensity * transmittance