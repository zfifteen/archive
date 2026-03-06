"""Top-level factorization pipeline."""

from typing import Optional
from .fermat import lognormal_fermat_stage
from .prefilter import factor_with_candidate_prefilter
from .model import ModelStore
from .config import SearchPolicyConfig
from .utils import pollard_rho


def factor_with_lognormal_prefilter(
    N: int, model_store: ModelStore, cfg: SearchPolicyConfig, seed: Optional[int] = None
) -> Optional[int]:
    """
    Full pipeline: Fermat stage -> candidate prefilter -> classical fallback.
    """
    # Stage 1: Lognormal-guided Fermat
    factor = lognormal_fermat_stage(N, model_store, cfg)
    if factor:
        return factor

    # Stage 2: Candidate prefilter
    factor = factor_with_candidate_prefilter(N, model_store, cfg)
    if factor:
        return factor

    # Stage 3: Classical fallback
    return pollard_rho(N)


def factor_classical(N: int) -> Optional[int]:
    """Baseline classical factorization (Pollard Rho)."""
    return pollard_rho(N)
