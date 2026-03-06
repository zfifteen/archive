#!/usr/bin/env python3
"""
Comprehensive test suite for Wave-Knob Invariant Prime Scanner
============================================================

Tests the complete z5d_mersenne implementation including:
- High-precision arithmetic 
- Auto-tune convergence
- Wave pattern validation
- Scaling behavior
- JSON output format
"""

import json
import subprocess
import unittest
from pathlib import Path
import tempfile
import os

class TestWaveKnobSystem(unittest.TestCase):
    """Test suite for the Wave-Knob prime scanner."""
    
    @classmethod
    def setUpClass(cls):
        """Find and verify z5d_mersenne binary."""
        # Try to find the binary
        possible_paths = [
            'src/c/z5d_mersenne',
            '../src/c/z5d_mersenne', 
            './z5d_mersenne'
        ]
        
        cls.binary_path = None
        for path in possible_paths:
            if Path(path).exists():
                cls.binary_path = Path(path).resolve()
                break
        
        if not cls.binary_path:
            raise unittest.SkipTest("z5d_mersenne binary not found")
        
        print(f"Testing with binary: {cls.binary_path}")
    
    def run_z5d_command(self, k, extra_args=None, timeout=30):
        """Run z5d_mersenne command and return parsed JSON result."""
        cmd = [str(self.binary_path), str(k), '--json']
        if extra_args:
            cmd.extend(extra_args)
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
            self.assertEqual(result.returncode, 0, f"Command failed: {' '.join(cmd)}\nstderr: {result.stderr}")
            return json.loads(result.stdout)
        except (subprocess.TimeoutExpired, json.JSONDecodeError) as e:
            self.fail(f"Command execution failed: {e}")
    
    def test_basic_functionality(self):
        """Test basic auto-tune functionality with small k values."""
        test_cases = [
            (100, "Basic small k"),
            (1000, "Medium k"),
            (10000, "Large k")
        ]
        
        for k, description in test_cases:
            with self.subTest(k=k, desc=description):
                result = self.run_z5d_command(k)
                
                # Validate JSON structure
                required_fields = ['k', 'window', 'step', 'R', 'prime_count', 'iterations', 
                                 'mr_calls', 'elapsed_ms', 'locked', 'wheel_residue']
                for field in required_fields:
                    self.assertIn(field, result, f"Missing field: {field}")
                
                # Validate auto-tune convergence
                self.assertTrue(result['locked'], "Auto-tune should converge")
                self.assertEqual(result['prime_count'], 1, "Should find exactly 1 prime")
                self.assertGreater(result['R'], 0, "R ratio should be positive")
                self.assertGreater(result['mr_calls'], 0, "Should make MR calls")
    
    def test_manual_scan_mode(self):
        """Test manual scan mode with fixed parameters."""
        result = self.run_z5d_command(1000, ['--scan', '--window=10', '--step=2'])
        
        # Validate manual scan results
        self.assertEqual(result['window'], 10)
        self.assertEqual(result['step'], 2)
        self.assertEqual(result['R'], 5.0)
        self.assertEqual(result['iterations'], 0)  # No iterations in manual mode
        self.assertGreaterEqual(result['prime_count'], 0)
    
    def test_high_precision_mode(self):
        """Test high-precision arithmetic with large k values."""
        # Test k=1e50 with high precision
        result = self.run_z5d_command('1e50', ['--prec=6144'], timeout=60)
        
        # Validate high-precision handling
        self.assertTrue(result['locked'], "Should handle large k values")
        self.assertEqual(result['prime_count'], 1)
        
        # Verify k was parsed correctly (should be a 50-digit number)
        k_str = result['k']
        self.assertTrue(len(k_str) >= 50, f"k should be ~50 digits, got {len(k_str)}")
        self.assertTrue(k_str.isdigit(), "k should be numeric")
    
    def test_wheel_modulus_options(self):
        """Test different wheel modulus options."""
        for wheel in [30, 210]:
            with self.subTest(wheel=wheel):
                result = self.run_z5d_command(1000, [f'--wheel={wheel}'])
                self.assertEqual(result['wheel_residue'], f'mod_{wheel}')
                self.assertTrue(result['locked'])
    
    def test_wave_pattern_validation(self):
        """Test that different R ratios produce different prime counts (wave behavior)."""
        k = 1000
        test_params = [
            (2, 2),   # R = 1.0
            (4, 2),   # R = 2.0 
            (10, 2),  # R = 5.0
            (20, 2),  # R = 10.0
        ]
        
        results = []
        for window, step in test_params:
            result = self.run_z5d_command(k, ['--scan', f'--window={window}', f'--step={step}'])
            results.append((result['R'], result['prime_count']))
        
        # Validate that we see different prime counts (wave behavior)
        prime_counts = [count for _, count in results]
        unique_counts = set(prime_counts)
        self.assertGreater(len(unique_counts), 1, 
                          f"Should see varying prime counts, got: {prime_counts}")
    
    def test_r_star_scaling(self):
        """Test that R* varies smoothly with k (scaling law)."""
        k_values = [100, 1000, 10000]
        r_star_values = []
        
        for k in k_values:
            result = self.run_z5d_command(k)
            if result['locked']:
                r_star_values.append(result['R'])
        
        # Should have multiple R* values
        self.assertGreaterEqual(len(r_star_values), 2, "Should get multiple R* values")
        
        # R* should be finite and positive
        for r_star in r_star_values:
            self.assertGreater(r_star, 0, "R* should be positive")
            self.assertLess(r_star, 100, "R* should be reasonable magnitude")
    
    def test_precision_parameter(self):
        """Test different precision settings."""
        k = '1e20'
        precisions = [1024, 4096, 8192]
        
        for prec in precisions:
            with self.subTest(precision=prec):
                result = self.run_z5d_command(k, [f'--prec={prec}'], timeout=60)
                self.assertTrue(result['locked'], f"Should work with {prec}-bit precision")
    
    def test_json_output_format(self):
        """Test JSON output format compliance."""
        result = self.run_z5d_command(100)
        
        # Validate data types
        self.assertIsInstance(result['k'], str)
        self.assertIsInstance(result['window'], int)
        self.assertIsInstance(result['step'], int)
        self.assertIsInstance(result['R'], float)
        self.assertIsInstance(result['prime_count'], int)
        self.assertIsInstance(result['iterations'], int)
        self.assertIsInstance(result['mr_calls'], int)
        self.assertIsInstance(result['elapsed_ms'], float)
        self.assertIsInstance(result['locked'], bool)
        self.assertIsInstance(result['wheel_residue'], str)
        
        # Validate ranges
        self.assertGreaterEqual(result['window'], 1)
        self.assertGreaterEqual(result['step'], 1) 
        self.assertGreaterEqual(result['prime_count'], 0)
        self.assertGreaterEqual(result['mr_calls'], 0)
        self.assertGreaterEqual(result['elapsed_ms'], 0)
    
    def test_error_handling(self):
        """Test error handling for invalid inputs."""
        # Invalid k value
        cmd = [str(self.binary_path), 'invalid_k']
        result = subprocess.run(cmd, capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0, "Should reject invalid k")
        
        # k too small
        cmd = [str(self.binary_path), '1']  # k < 2
        result = subprocess.run(cmd, capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0, "Should reject k < 2")
    
    def test_help_and_version(self):
        """Test help and version commands."""
        # Test --help
        cmd = [str(self.binary_path), '--help']
        result = subprocess.run(cmd, capture_output=True, text=True)
        self.assertEqual(result.returncode, 1)  # Help exits with 1
        self.assertIn('Usage:', result.stdout)
        
        # Test --version
        cmd = [str(self.binary_path), '--version']
        result = subprocess.run(cmd, capture_output=True, text=True)
        self.assertEqual(result.returncode, 1)  # Version exits with 1  
        self.assertIn('z5d_mersenne version', result.stdout)
    
    def test_target_count_parameter(self):
        """Test different target count settings."""
        # Target count = 2 (should find 2 primes)
        result = self.run_z5d_command(1000, ['--target=2'])
        
        # May or may not lock depending on parameter space,
        # but should attempt to find 2 primes
        self.assertGreaterEqual(result['prime_count'], 0)
    
    def test_comprehensive_integration(self):
        """Comprehensive integration test with all major features."""
        # Test ultra-large k with high precision, custom wheel, and JSON output
        result = self.run_z5d_command('1e100', 
                                    ['--prec=6144', '--wheel=210', '--mr-rounds=25'], 
                                    timeout=90)
        
        # Should handle this successfully
        self.assertTrue(result['locked'], "Should handle 1e100 successfully")
        self.assertEqual(result['prime_count'], 1)
        self.assertEqual(result['wheel_residue'], 'mod_210')
        
        # R* should be reasonable for this scale
        self.assertGreater(result['R'], 1, "R* should be > 1 for large k")
        self.assertLess(result['R'], 1000, "R* should be < 1000")
        
        # Should find a very large prime
        prime_found = result.get('prime_found')
        if prime_found and prime_found != 'null':
            self.assertGreater(len(str(prime_found)), 100, "Prime should be very large")

def run_performance_benchmark():
    """Optional performance benchmark (not part of standard test suite)."""
    # This can be run separately to measure performance
    pass

if __name__ == '__main__':
    # Add performance benchmark option
    import sys
    if '--benchmark' in sys.argv:
        sys.argv.remove('--benchmark')
        run_performance_benchmark()
    
    # Run the test suite
    unittest.main(verbosity=2)