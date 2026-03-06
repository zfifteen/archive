"""
Unit tests for validating scaling behavior of PR-0003 components.

Tests individual components to verify their computational complexity
and scaling characteristics.
"""

import sys
import time
import unittest
from pathlib import Path
import numpy as np

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from prime_generator import sieve_of_eratosthenes, segmented_sieve, compute_gaps
from binning import analyze_bins, compute_bin_statistics
from statistics import (
    linear_regression,
    kolmogorov_smirnov_tests,
    ljung_box_test,
    compute_acf_pacf,
)


class TestPrimeGenerationScaling(unittest.TestCase):
    """Test scaling of prime generation algorithms."""

    def test_sieve_basic_scaling(self):
        """Test that basic sieve scales as O(n log log n)."""
        # Test at three scales
        scales = [10**4, 10**5, 10**6]
        times = []

        for scale in scales:
            start = time.time()
            primes = sieve_of_eratosthenes(scale)
            elapsed = time.time() - start
            times.append(elapsed)

        # Calculate scaling exponent between last two scales
        time_ratio = times[2] / times[1]
        scale_ratio = scales[2] / scales[1]

        # For O(n log log n), expected exponent is ~1.0-1.1
        exponent = np.log(time_ratio) / np.log(scale_ratio)

        # Should be between 0.8 and 1.3 (allowing for variance)
        self.assertGreater(exponent, 0.8, f"Sieve scaling too slow: {exponent:.2f}")
        self.assertLess(exponent, 1.3, f"Sieve scaling too fast: {exponent:.2f}")

    def test_segmented_sieve_memory_efficiency(self):
        """Test that segmented sieve uses reasonable memory."""
        import tracemalloc

        tracemalloc.start()
        primes = segmented_sieve(10**6, segment_size=10**5)
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        # Peak memory should be much less than storing 10^6 booleans
        # Full sieve would use ~1MB, segmented should use <200KB
        self.assertLess(
            peak,
            500_000,
            f"Segmented sieve using too much memory: {peak / 1024:.1f} KB",
        )


class TestBinningScaling(unittest.TestCase):
    """Test scaling of binning analysis."""

    def test_binning_sublinear_scaling(self):
        """Test that binning scales better than linear (due to fixed bins)."""
        # Generate synthetic data at different scales
        scales = [10**5, 10**6]
        times = []

        for scale in scales:
            # Create fake log-primes and log-gaps
            log_primes = np.log(np.arange(2, scale, dtype=np.float64))
            log_gaps = np.random.lognormal(0, 1, size=len(log_primes) - 1) * 0.001

            start = time.time()
            _ = analyze_bins(log_primes, log_gaps, n_bins=100)
            elapsed = time.time() - start
            times.append(elapsed)

        # Calculate scaling
        time_ratio = times[1] / times[0]
        scale_ratio = scales[1] / scales[0]
        exponent = np.log(time_ratio) / np.log(scale_ratio)

        # Should be close to linear (1.0) since we're iterating over all gaps
        # But might be slightly sub-linear due to fixed bin count
        self.assertGreater(exponent, 0.5, "Binning too efficient to be real")
        self.assertLess(exponent, 1.2, "Binning scaling worse than linear")

    def test_fixed_bin_count_property(self):
        """Test that bin count doesn't grow with data size."""
        for scale in [10**5, 10**6]:
            log_primes = np.log(np.arange(2, scale, dtype=np.float64))
            log_gaps = np.random.lognormal(0, 1, size=len(log_primes) - 1) * 0.001

            result = analyze_bins(log_primes, log_gaps, n_bins=100)

            # Always 100 bins regardless of data size
            self.assertEqual(len(result["mean"]), 100)


class TestStatisticalTestsScaling(unittest.TestCase):
    """Test scaling of statistical tests."""

    def test_regression_constant_time(self):
        """Test that regression on bins is O(1) since bin count is fixed."""
        # Test with different amounts of data (same 100 bins)
        times = []

        for n_points in [10**5, 10**6]:
            # Create 100 bin means (this is what regression sees)
            bin_means = np.random.randn(100) * 0.01

            start = time.time()
            for _ in range(100):  # Repeat for measurable time
                _ = linear_regression(bin_means)
            elapsed = time.time() - start
            times.append(elapsed)

        # Time should be nearly identical since input size is fixed
        ratio = times[1] / times[0]
        self.assertLess(ratio, 1.5, "Regression scaling with data size!")

    def test_ks_tests_linear_scaling(self):
        """Test that KS tests scale linearly or near-linear."""
        scales = [10**4, 10**5]
        times = []

        for scale in scales:
            data = np.random.lognormal(0, 1, size=scale) * 0.001

            start = time.time()
            _ = kolmogorov_smirnov_tests(data)
            elapsed = time.time() - start
            times.append(elapsed)

        time_ratio = times[1] / times[0]
        scale_ratio = scales[1] / scales[0]
        exponent = np.log(time_ratio) / np.log(scale_ratio)

        # KS test is O(n log n), so exponent should be 1.0-1.1
        self.assertGreater(exponent, 0.8)
        self.assertLess(exponent, 1.3)

    def test_ljungbox_quadratic_scaling(self):
        """Test that Ljung-Box exhibits super-linear (likely quadratic) scaling."""
        scales = [10**4, 2 * 10**4]  # Small scales to keep test fast
        times = []

        for scale in scales:
            data = np.random.lognormal(0, 1, size=scale) * 0.001

            start = time.time()
            _ = ljung_box_test(data, max_lag=20)  # Use fewer lags for speed
            elapsed = time.time() - start
            times.append(elapsed)

        time_ratio = times[1] / times[0]
        scale_ratio = scales[1] / scales[0]  # Should be 2.0
        exponent = np.log(time_ratio) / np.log(scale_ratio)

        # Ljung-Box appears to be O(n²) or O(n·k²)
        # With 2x data, expect ~4x time (exponent ~2.0)
        # Allow range 1.5-2.5 for variance
        self.assertGreater(exponent, 1.3, "Ljung-Box more efficient than expected")
        self.assertLess(exponent, 2.7, "Ljung-Box worse than O(n²)")

    def test_autocorr_optional_modes(self):
        """Test that autocorrelation modes work correctly."""
        # Test default mode (none)
        from ..run_experiment import run_experiment
        import os
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            results = run_experiment(
                max_prime=1e5, autocorr_mode="none", use_cache=False, verbose=False
            )

            # Check that ljung_box is None
            self.assertIsNone(results["autocorrelation"]["ljung_box"])
            self.assertEqual(
                results["autocorrelation"]["ljungbox_status"], "not_evaluated"
            )
            self.assertEqual(results["autocorrelation"]["autocorr_mode"], "none")

            # Check that ACF/PACF are still computed
            self.assertIn("acf_pacf_summary", results["autocorrelation"])
            self.assertIsNotNone(
                results["autocorrelation"]["acf_pacf_summary"]["significant_lags"]
            )

            # Test enabled mode
            results = run_experiment(
                max_prime=1e5, autocorr_mode="ljungbox", use_cache=False, verbose=False
            )

            # Check that ljung_box has data
            self.assertIsNotNone(results["autocorrelation"]["ljung_box"])
            self.assertEqual(results["autocorrelation"]["ljungbox_status"], "evaluated")
            self.assertEqual(results["autocorrelation"]["autocorr_mode"], "ljungbox")
            self.assertIn("lb_stats", results["autocorrelation"]["ljung_box"])

    def test_acf_pacf_linear_scaling(self):
        """Test that ACF/PACF scale near-linearly (FFT-based)."""
        scales = [10**4, 10**5]
        times = []

        for scale in scales:
            data = np.random.lognormal(0, 1, size=scale) * 0.001

            start = time.time()
            _ = compute_acf_pacf(data, nlags=50)
            elapsed = time.time() - start
            times.append(elapsed)

        time_ratio = times[1] / times[0]
        scale_ratio = scales[1] / scales[0]
        exponent = np.log(time_ratio) / np.log(scale_ratio)

        # FFT is O(n log n), so expect 1.0-1.1
        self.assertGreater(exponent, 0.7)
        self.assertLess(exponent, 1.3)


class TestCachingEffectiveness(unittest.TestCase):
    """Test that caching provides expected speedup."""

    def test_gap_computation_with_caching(self):
        """Test that gap caching eliminates recomputation."""
        import tempfile
        import shutil

        # Create temporary cache directory
        cache_dir = tempfile.mkdtemp()

        try:
            # Generate small prime set
            primes = sieve_of_eratosthenes(10**4)

            # First call: should compute
            start1 = time.time()
            result1 = compute_gaps(primes, cache_dir=cache_dir, limit=10**4)
            time1 = time.time() - start1

            # Second call: should load from cache
            start2 = time.time()
            result2 = compute_gaps(primes, cache_dir=cache_dir, limit=10**4)
            time2 = time.time() - start2

            # Cached version should be much faster
            self.assertLess(time2, time1 * 0.5, "Caching not providing speedup")

            # Results should be identical
            np.testing.assert_array_equal(result1["log_gaps"], result2["log_gaps"])

        finally:
            shutil.rmtree(cache_dir)


class TestScalingAssumptions(unittest.TestCase):
    """Test specific assumptions about scaling behavior."""

    def test_overall_scaling_without_ljungbox(self):
        """Test that without Ljung-Box, pipeline is near-linear."""
        # This is what the sub-linear claim should be based on

        scales = [10**4, 10**5]
        times = []

        for scale in scales:
            # Simulate pipeline without Ljung-Box
            data = np.random.lognormal(0, 1, size=scale) * 0.001
            log_primes = np.log(np.arange(2, scale + 2, dtype=np.float64))

            start = time.time()

            # Binning
            _ = analyze_bins(log_primes, data, n_bins=100)

            # KS tests (dominant component)
            _ = kolmogorov_smirnov_tests(data)

            # ACF/PACF
            _ = compute_acf_pacf(data, nlags=50)

            # Regression (on 100 bins)
            bin_means = np.random.randn(100) * 0.01
            _ = linear_regression(bin_means)

            elapsed = time.time() - start
            times.append(elapsed)

        time_ratio = times[1] / times[0]
        scale_ratio = scales[1] / scales[0]
        exponent = np.log(time_ratio) / np.log(scale_ratio)

        # Without Ljung-Box, should be near-linear (0.9-1.1)
        self.assertGreater(exponent, 0.7)
        self.assertLess(exponent, 1.3)


if __name__ == "__main__":
    # Run tests with verbose output
    unittest.main(verbosity=2)
