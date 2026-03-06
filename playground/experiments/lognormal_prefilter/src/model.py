"""
Data and model layer for lognormal prime-gap distribution.

This module defines the Band structure and ModelStore for accessing
lognormal parameters derived from empirical prime gap data.
"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class Band:
    """
    Represents a prime-size band with fitted lognormal parameters.
    
    Attributes:
        p_min: Minimum prime value for this band (inclusive)
        p_max: Maximum prime value for this band (exclusive)
        shape: Lognormal shape parameter (sigma)
        scale: Lognormal scale parameter (exp(mu))
        min_gap: Optional minimum gap for clamping
        max_gap: Optional maximum gap for clamping
    """
    p_min: int
    p_max: int
    shape: float
    scale: float
    min_gap: Optional[float] = None
    max_gap: Optional[float] = None


class ModelStore:
    """
    Storage for lognormal prime-gap model bands.
    
    Provides lookup methods to find the appropriate band for a given prime value.
    """
    
    def __init__(self, bands: list[Band]):
        """
        Initialize the ModelStore with a list of bands.
        
        Args:
            bands: List of Band objects, should be sorted by p_min
        """
        self.bands = sorted(bands, key=lambda b: b.p_min)
    
    def get_band_for_p(self, p: int) -> Optional[Band]:
        """
        Get the band that contains prime p.
        
        Args:
            p: Prime value to look up
            
        Returns:
            Band object if p falls within a known band, None otherwise
        """
        for band in self.bands:
            if band.p_min <= p < band.p_max:
                return band
        return None
    
    def get_closest_band(self, p: int) -> Band:
        """
        Get the closest band to prime p.
        
        If p is outside all known ranges, returns the band with the
        nearest boundary.
        
        Args:
            p: Prime value to look up
            
        Returns:
            Closest Band object
        """
        # First try exact match
        band = self.get_band_for_p(p)
        if band is not None:
            return band
        
        # Find closest band by comparing distances to band boundaries
        closest_band = self.bands[0]
        min_distance = float('inf')
        
        for band in self.bands:
            # Distance to lower boundary
            dist_lower = abs(p - band.p_min)
            # Distance to upper boundary
            dist_upper = abs(p - band.p_max)
            # Take minimum distance
            dist = min(dist_lower, dist_upper)
            
            if dist < min_distance:
                min_distance = dist
                closest_band = band
        
        return closest_band


def create_default_model_store() -> ModelStore:
    """
    Create a ModelStore with default bands using parameters from empirical data.
    
    Parameters are extracted from lognormal fits in the results files from
    the PR-0003_prime_log_gap_optimized experiment. Each file contains
    fitted parameters for primes within specific ranges:
    - results-10-5.json: primes up to 10^5 (Band 1 uses 10^5-10^6 range)
    - results-10-6.json: primes up to 10^6 (Band 2 uses 10^6-10^7 range)
    - results-10-7.json: primes up to 10^7 (Band 3 uses 10^7-10^8 range)
    - results-10-9.json: primes up to 10^9 (Band 4 uses 10^8-10^9 range)
    
    Returns:
        ModelStore initialized with 4 default bands
    """
    bands = [
        # Band 1: 10^5 to 10^6
        # From results-10-6.json: shape=1.2867, scale=0.0002415, ks=0.0573
        Band(
            p_min=10**5,
            p_max=10**6,
            shape=1.2866741112925417,
            scale=0.0002415323263647987,
            min_gap=2.0,
            max_gap=1000.0
        ),
        # Band 2: 10^6 to 10^7
        # From results-10-6.json: shape=1.3091, scale=2.796e-05, ks=0.0516
        Band(
            p_min=10**6,
            p_max=10**7,
            shape=1.3091375410067352,
            scale=2.7958952440903736e-05,
            min_gap=2.0,
            max_gap=10000.0
        ),
        # Band 3: 10^7 to 10^8
        # From results-10-7.json: shape=1.3291, scale=3.166e-06, ks=0.0466
        Band(
            p_min=10**7,
            p_max=10**8,
            shape=1.3291388882859054,
            scale=3.1656537689046316e-06,
            min_gap=2.0,
            max_gap=100000.0
        ),
        # Band 4: 10^8 to 10^9
        # From results-10-9.json: shape=1.3579, scale=3.920e-08, ks=0.0421
        Band(
            p_min=10**8,
            p_max=10**9,
            shape=1.3579252379210984,
            scale=3.919707609575568e-08,
            min_gap=2.0,
            max_gap=1000000.0
        ),
    ]
    
    return ModelStore(bands)
