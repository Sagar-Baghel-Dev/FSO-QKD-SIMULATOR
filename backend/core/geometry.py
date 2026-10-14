import numpy as np 

EARTH_RADIUS_M = 6371000.0 #Earth Radius in Meters

def calculate_beam_altitude(distance_z_m: float, tx_altitude_m: float):
    """ calculating laser height from ground acc to earth curvature """

    r_plus_tx = EARTH_RADIUS_M + tx_altitude_m
    distance_from_earth_center = np.sqrt(r_plus_tx**2 + distance_z_m**2)
    current_altitude_m = distance_from_earth_center - EARTH_RADIUS_M

    return current_altitude_m

def get_trajectory_altitudes(total_distance_m: float, tx_altitude_m: float, num_points: int=100):
    """ for whole trajectory creating array of heights for 3d arcuse in frontedn """
    z_points = np.linspace(0,total_distance_m, num_points)
    altitudes = [calculate_beam_altitude(z, tx_altitude_m) for z in z_points]

    return z_points.tolist(), altitudes
