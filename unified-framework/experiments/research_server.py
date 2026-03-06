from fastmcp import FastMCP
import mpmath as mp
from typing import List, Tuple
import json

# Set mpmath precision
mp.dps = 50  # Target precision < 1e-16 is achievable with higher dps

mcp = FastMCP("Research Companion Server")

@mcp.tool
def compute_zeta_zeros(n: int) -> str:
    """Compute the first n non-trivial zeros of the Riemann zeta function.

    Args:
        n: Number of zeros to compute (max ~100 for reasonable time).

    Returns:
        JSON string with list of (real, imag) tuples.
    """
    if n <= 0 or n > 100:
        raise ValueError("n must be between 1 and 100.")
    try:
        zeros = []
        for i in range(1, n + 1):
            # Use mpmath's zeta zero function
            zero = mp.zetazero(i)
            zeros.append((float(mp.re(zero)), float(mp.im(zero))))
        return json.dumps(zeros)
    except Exception as e:
        raise ValueError(f"Error computing zeta zeros: {str(e)}")

@mcp.tool
def compute_curvature(n: int) -> float:
    """Compute curvature κ(n) = d(n) * ln(n+1) / e² for prime-density mapping.

    Args:
        n: Positive integer.

    Returns:
        Curvature value as float.
    """
    if n <= 0:
        raise ValueError("n must be positive.")
    try:
        d = mp.digamma(n + 1) - mp.digamma(1)  # Approximation for divisor function d(n)
        kappa = float(d * mp.log(n + 1) / (mp.e ** 2))
        return kappa
    except Exception as e:
        raise ValueError(f"Error computing curvature: {str(e)}")

@mcp.tool
def geometric_resolution(n: int, k: float = 0.3) -> float:
    """Compute geometric resolution θ'(n, k) = φ * ((n mod φ) / φ)^k for prime-density mapping.

    Args:
        n: Positive integer.
        k: Exponent, recommended 0.3.

    Returns:
        Resolution value as float.
    """
    if n <= 0:
        raise ValueError("n must be positive.")
    try:
        phi = (1 + mp.sqrt(5)) / 2  # Golden ratio
        mod_phi = float(mp.fmod(n, phi))
        theta_prime = float(phi * (mod_phi / phi) ** k)
        return theta_prime
    except Exception as e:
        raise ValueError(f"Error computing geometric resolution: {str(e)}")

@mcp.resource("data://zeta_zeros_sample")
def get_zeta_zeros_sample() -> str:
    """Sample zeta zeros for testing (first 10)."""
    sample = [
        (0.0, 14.134725141734693790457251983562470270784257115699243175685567460149963429809256764949010393171561),
        (0.0, 21.022039638771554992628479593896902777495476709786702842245821716903696281063088956999230912807489),
        (0.0, 25.010857580145688763213790992562821818659478205803834211132066938252341264600493318723203154462547),
        (0.0, 30.424876125859513210311897530584091320181560023715200183493652457386810105927376412026349387242908),
        (0.0, 32.935061587739189690662368964074903488072129551032005568086204600048561643229336986669596928617210),
        (0.0, 37.586178158825671257217763480705332821405597350830793218333001113724739453918628113122799651822477),
        (0.0, 40.918719012147495187398126914633254156147068875913836954425742029888584365283929473637993164212059),
        (0.0, 43.327073280914999519496122031631111529292185822805724905246540675763726946032516662779928494116036),
        (0.0, 48.005150881167159727942472749733678674059854052774041783796581370728637785012490712192528430937811),
        (0.0, 49.773832477672302181916784678563724057723001506192935095860204665086896439112745085867600684728520)
    ]
    return json.dumps(sample)

if __name__ == "__main__":
    mcp.run()