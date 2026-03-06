"""Model layer for lognormal prime-gap factorization."""

from dataclasses import dataclass
from typing import Optional, List


@dataclass
class Band:
    """Represents a prime-size band with lognormal parameters."""

    p_min: int
    p_max: int
    shape: float
    scale: float
    min_gap: Optional[float] = None
    max_gap: Optional[float] = None


class ModelStore:
    """Stores lognormal bands for different prime sizes."""

    def __init__(self):
        # Hardcoded bands from empirical fits (results-10-6.json to 10-9.json)
        self.bands: List[Band] = [
            Band(
                p_min=100000,
                p_max=1000000,
                shape=1.3091375410067352,
                scale=2.7958952440903736e-05,
            ),
            Band(
                p_min=1000000,
                p_max=10000000,
                shape=1.3291388882859054,
                scale=3.1656537689046316e-06,
            ),
            Band(
                p_min=10000000,
                p_max=100000000,
                shape=1.3441884012687917,
                scale=3.543816270395733e-07,
            ),
            Band(
                p_min=100000000,
                p_max=1000000000,
                shape=1.3579252379210984,
                scale=3.919707609575568e-08,
            ),
        ]

    def get_band_for_p(self, p: int) -> Optional[Band]:
        """Return the band containing p."""
        for band in self.bands:
            if band.p_min <= p < band.p_max:
                return band
        return None

    def get_closest_band(self, p: int) -> Band:
        """Return the closest band by p range (approximation for out-of-band)."""
        if p < self.bands[0].p_min:
            return self.bands[0]
        elif p > self.bands[-1].p_max:
            return self.bands[-1]
        else:
            # Should not reach here if bands cover, but fallback
            return self.bands[0]
