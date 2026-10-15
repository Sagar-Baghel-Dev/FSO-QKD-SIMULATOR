import numpy as np

def binary_entropy(e: float):
    """ Shannon Binary Entropy Function H(e). it calculates information leaked due to qber errors """
    if e <= 0 or e >= 0.5:
        return 0.0
    # Formula: -e*log2(e) - (1-e)*log2(1-e)
    return -e * np.log2(e) - (1 - e) * np.log2(1 - e)

def calculate_qkd_metrics(transmittance: float, base_qber: float = 0.01, pulse_rate_hz: float = 1e9):
    """Calculates final SKR and QBER, transmittance base_qber """
    # 1. Total QBER (Low transmittance = High Error)
    noise_factor = 0.0005 
    
    if transmittance <= 0:
        final_qber = 0.5 # 50% QBER matlab total random (link fail)
    else:
        final_qber = base_qber + (noise_factor / transmittance)
        
    final_qber = min(final_qber, 0.5)
    
    # 2. Secret Key Rate (SKR)
    # BB84 mein agar QBER ~11% se upar jaye toh key rate zero ho jata hai
    entropy = binary_entropy(final_qber)
    privacy_factor = 1.0 - (2.0 * entropy)
    
    if privacy_factor <= 0:
        secret_key_rate_bps = 0.0
    else:
        # Simplified Decoy-State Formula: Pulse Rate * Transmittance * Privacy_Factor
        # 0.1 yahan quantum signal emit hone ki probability hai (mu)
        secret_key_rate_bps = pulse_rate_hz * transmittance * 0.1 * privacy_factor
        
    return float(final_qber), float(secret_key_rate_bps)