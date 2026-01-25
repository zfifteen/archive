import math
from divisor_density import d

PHI = (1 + math.sqrt(5)) / 2  # Golden ratio ≈ 1.618

def kappa_basic(n):
    """
    Basic curvature signal κ(n) = d(n) · ln(n) / e²
    
    Args:
        n (int): The number.
    
    Returns:
        float: The curvature value.
    """
    if n <= 1:
        return 0.0
    return d(n) * math.log(n) / math.exp(2)

def kappa_enhanced(n):
    """
    Enhanced curvature κ(n) = d(n) · ln(n+1) / e² · [1 + arctan(φ · frac(n/φ))]
    
    Args:
        n (int): The number.
    
    Returns:
        float: The enhanced curvature value.
    """
    if n <= 1:
        return 0.0
    frac_part = n / PHI - math.floor(n / PHI)
    return d(n) * math.log(n + 1) / math.exp(2) * (1 + math.atan(PHI * frac_part))

def distortion_mapping(n, v=1.0):
    """
    Distortion mapping Δ_n = v · κ(n)
    
    Args:
        n (int): The number.
        v (float): Traversal rate.
    
    Returns:
        float: The distortion value.
    """
    return v * kappa_basic(n)

def perceived_value(n, delta_n):
    """
    Perceived value n_perceived = n × exp(Δ_n)
    
    Args:
        n (int): The number.
        delta_n (float): Distortion value.
    
    Returns:
        float: The perceived value.
    """
    return n * math.exp(delta_n)

def z_normalization(n, v=1.0):
    """
    Z-normalization Z(n) = n / exp(v · κ(n))
    
    Args:
        n (int): The number.
        v (float): Traversal rate.
    
    Returns:
        float: The Z-normalized value.
    """
    return n / math.exp(v * kappa_basic(n))

# Alias for backward compatibility
kappa = kappa_basic