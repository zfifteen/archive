"""
Top-level lognormal pre-filter factorization pipeline.
"""
import random
from typing import Optional

try:
    from .model import ModelStore
    from .config import SearchPolicyConfig
    from .fermat import lognormal_fermat_stage
    from .prefilter import factor_with_candidate_prefilter, pollard_rho
except ImportError:
    from model import ModelStore
    from config import SearchPolicyConfig
    from fermat import lognormal_fermat_stage
    from prefilter import factor_with_candidate_prefilter, pollard_rho


def factor_with_lognormal_prefilter(
    N: int,
    model_store: ModelStore,
    cfg: SearchPolicyConfig
) -> Optional[int]:
    """
    Full factorization pipeline with lognormal pre-filter.
    
    The pipeline tries multiple strategies in order:
    1. Lognormal-guided Fermat stage
    2. Lognormal candidate prefilter + direct division
    3. Classical factorization fallback (Pollard's rho)
    
    The lognormal model biases the search order to spend more effort
    near sqrt(N) in regions where prime gaps are likely, but does not
    change the mathematical correctness of the algorithms.
    
    Args:
        N: Number to factor (typically a semiprime p*q)
        model_store: ModelStore containing lognormal band parameters
        cfg: Search policy configuration
        
    Returns:
        A non-trivial factor of N on success, or None on failure
    """
    # Strategy 1: Lognormal-guided Fermat stage
    factor = lognormal_fermat_stage(N, model_store, cfg)
    if factor is not None:
        return factor
    
    # Strategy 2: Lognormal candidate prefilter
    # (This already includes a pollard_rho fallback internally)
    factor = factor_with_candidate_prefilter(N, model_store, cfg)
    if factor is not None:
        return factor
    
    # Strategy 3: Final fallback to pure classical method
    # (In case the prefilter's internal fallback also failed)
    # Initialize RNG if seed is provided for reproducibility
    rng = random.Random(cfg.random_seed) if cfg.random_seed is not None else random
    factor = pollard_rho(N, max_iterations=200000, rng=rng)
    
    return factor
