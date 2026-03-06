"""Configuration for search policy."""

import random
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class SearchPolicyConfig:
    """Configuration for the pre-filter search policy.

    max_steps: Maximum number of candidate offsets to generate.
    radius_scale: Multiplier for sampled gap sizes (tune for search breadth).
    direction_mode: How to alternate ± offsets ("ALTERNATE" or "RANDOM").
    rng: Dedicated random number generator for reproducibility.
    """

    max_steps: int = 10000
    radius_scale: float = 1.0
    direction_mode: str = "ALTERNATE"  # "ALTERNATE" or "RANDOM"
    seed: Optional[int] = None
    rng: random.Random = field(init=False)

    def __post_init__(self):
        if self.direction_mode not in ["ALTERNATE", "RANDOM"]:
            raise ValueError("direction_mode must be 'ALTERNATE' or 'RANDOM'")
        self.rng = random.Random(self.seed)
