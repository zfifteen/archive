"""
Configuration for the lognormal pre-filter search policy.
"""
from dataclasses import dataclass
from typing import Literal, Optional


DirectionMode = Literal["ALTERNATE", "RANDOM"]


@dataclass
class SearchPolicyConfig:
    """
    Configuration for the lognormal-guided search policy.
    
    Attributes:
        max_steps: Maximum number of candidate offsets to generate
        radius_scale: Multiplier applied to sampled gap sizes when 
                     turning them into offsets
        direction_mode: How to alternate ± offsets around sqrt(N):
                       - "ALTERNATE": alternates +1, -1, +1, -1, ...
                       - "RANDOM": randomly chooses +1 or -1 each step
        random_seed: Optional seed for reproducible random behavior
    """
    max_steps: int = 10000
    radius_scale: float = 1.0
    direction_mode: DirectionMode = "ALTERNATE"
    random_seed: Optional[int] = None


def create_default_config() -> SearchPolicyConfig:
    """
    Create a SearchPolicyConfig with default values.
    
    Returns:
        SearchPolicyConfig with reasonable defaults
    """
    return SearchPolicyConfig()
