import numpy as np

def calculate_beam_wander(intensity, X, Y):
    """ finds centeroid of beam, and finds beam wander from center"""
    # Total power
    total_power = np.sum(intensity)
    
    if total_power == 0:
        return 0.0, 0.0
        
    # X and Y direction beam wander (Centroid formula)
    centroid_x = np.sum(intensity * X) / total_power
    centroid_y = np.sum(intensity * Y) / total_power
    
    # Total shift (Pythagoras theorem)
    wander_distance = np.sqrt(centroid_x**2 + centroid_y**2)
    
    return float(wander_distance)

def calculate_scintillation(intensity):
    """ finds Scintillation Index (Intensity fluctuation).
    Formula: (Mean of I^2) / (Mean of I)^2 - 1
    """
    mean_intensity = np.mean(intensity)
    
    if mean_intensity == 0:
        return 0.0
        
    mean_intensity_sq = np.mean(intensity**2)
    
    # Scintillation index formula
    scintillation_index = (mean_intensity_sq / (mean_intensity**2)) - 1.0
    
    return float(scintillation_index)