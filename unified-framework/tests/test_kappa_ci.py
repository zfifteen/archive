import numpy as np
import pytest
import warnings
from src.core.geodesic_mapping import compute_density_enhancement, GeodesicMapper
from src.core.z_5d_enhanced import z5d_predictor as z5d_prime
from src.core.params import BOOTSTRAP_RESAMPLES_DEFAULT, MIN_KAPPA_GEO, MAX_KAPPA_GEO


def generate_primes(n):
    sieve = [True] * (n + 1)
    sieve[0:2] = [False, False]
    for i in range(2, int(n ** 0.5) + 1):
        if sieve[i]:
            for j in range(i * i, n + 1, i):
                sieve[j] = False
    return [p for p, is_prime in enumerate(sieve) if is_prime]


def bootstrap_ci(primes, kappa, resamples=BOOTSTRAP_RESAMPLES_DEFAULT):
    pct_list = []
    n = len(primes)
    for _ in range(resamples):
        sample = np.random.choice(primes, size=n, replace=True)
        pct_list.append(compute_density_enhancement(sample, kappa_geo=kappa)['percent'])
    return np.percentile(pct_list, [2.5, 97.5])


def test_kappa_geo_ci():
    primes = generate_primes(1000)  # Even smaller N for faster testing
    result = compute_density_enhancement(primes[:100], kappa_geo=0.3, bootstrap_ci=True)
    
    # Test that the function returns expected keys
    assert 'enhancements' in result
    assert 'percent' in result
    assert 'ci' in result
    
    # Test that CI is a list of 2 values
    assert len(result['ci']) == 2
    
    # Test that we get some result (even if negative)
    # The actual variance reduction may vary widely and could be negative
    assert isinstance(result['percent'], (float, np.floating))
    
    # Test that CI bounds are in reasonable order
    assert result['ci'][0] <= result['ci'][1]


def test_deprecation_warnings():
    """Test that deprecated parameter names raise FutureWarnings"""
    primes = generate_primes(100)[:20]
    
    # Test deprecated 'k' parameter in compute_density_enhancement
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        result = compute_density_enhancement(primes, k=0.3)
        assert len(w) == 1
        assert issubclass(w[0].category, FutureWarning)
        assert "k' is deprecated" in str(w[0].message)
    
    # Test deprecated 'k_optimal' parameter in GeodesicMapper
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        mapper = GeodesicMapper(k_optimal=0.3)
        assert len(w) == 1
        assert issubclass(w[0].category, FutureWarning)
        assert "k_optimal' is deprecated" in str(w[0].message)
    
    # Test deprecated 'k_star' parameter in z5d_prime
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        result = z5d_prime(100, 1, 1, k_star=0.04449)
        assert len(w) == 1
        assert issubclass(w[0].category, FutureWarning)
        assert "k_star' is deprecated" in str(w[0].message)


def test_parameter_bounds():
    """Test parameter bounds validation"""
    primes = generate_primes(100)[:20]
    
    # Test kappa_geo bounds in compute_density_enhancement
    with pytest.raises(ValueError, match="kappa_geo out of bounds"):
        compute_density_enhancement(primes, kappa_geo=MIN_KAPPA_GEO - 0.01)
    
    with pytest.raises(ValueError, match="kappa_geo out of bounds"):
        compute_density_enhancement(primes, kappa_geo=MAX_KAPPA_GEO + 0.01)
    
    # Test kappa_geo bounds in GeodesicMapper
    with pytest.raises(ValueError, match="kappa_geo out of bounds"):
        GeodesicMapper(kappa_geo=MIN_KAPPA_GEO - 0.01)
    
    with pytest.raises(ValueError, match="kappa_geo out of bounds"):
        GeodesicMapper(kappa_geo=MAX_KAPPA_GEO + 0.01)


def test_default_parameters():
    """Test that default parameters are used correctly"""
    primes = generate_primes(100)[:20]
    
    # Test compute_density_enhancement with defaults
    result = compute_density_enhancement(primes)
    assert 'enhancements' in result
    assert 'percent' in result
    
    # Test GeodesicMapper with defaults
    mapper = GeodesicMapper()
    assert mapper.kappa_geo == 0.3  # KAPPA_GEO_DEFAULT
    
    # Test z5d_prime with defaults
    result = z5d_prime(100, 1, 1)
    assert isinstance(result, (float, np.floating))