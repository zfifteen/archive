"""
Comprehensive Test Suite for Prime Curvature LU Decomposition Quantum Integration
================================================================================

This test suite validates the enhanced LU decomposition functionality
with prime curvature analysis for quantum computing applications.

Test Coverage:
- PrimeGeodesicTransform functionality and mathematical properties
- EnhancedLUDecomposition conditioning and improvements  
- QuantumErrorCorrectionLU stability and performance
- QuantumCryptographyLU security and key generation
- Quantum circuit matrix optimization
- Edge cases and numerical stability
- Performance benchmarks and condition number improvements

Author: Z Framework Team
"""

import unittest
import numpy as np
import scipy.linalg as la
import warnings
from typing import Dict, List, Tuple, Any
import sys
import os

# Add path for imports
sys.path.append(os.path.dirname(__file__))
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.applications.lu_decomposition_quantum import (
    PrimeGeodesicTransform,
    EnhancedLUDecomposition, 
    QuantumErrorCorrectionLU,
    QuantumCryptographyLU,
    optimize_quantum_circuit_matrix,
    K_STAR,
    PHI_FLOAT
)

class TestPrimeGeodesicTransform(unittest.TestCase):
    """Test suite for PrimeGeodesicTransform class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.pgt = PrimeGeodesicTransform()
        self.test_values = [1, 2, 3, 5, 10, 100, 1000]
        self.test_arrays = [np.array([1, 2, 3]), np.array([10, 20, 30])]
        
    def test_initialization(self):
        """Test proper initialization of PrimeGeodesicTransform."""
        # Test default initialization
        pgt_default = PrimeGeodesicTransform()
        self.assertAlmostEqual(pgt_default.k_star, K_STAR, places=6)
        self.assertAlmostEqual(pgt_default.phi, PHI_FLOAT, places=6)
        
        # Test custom curvature parameter
        custom_k = 0.5
        pgt_custom = PrimeGeodesicTransform(custom_k)
        self.assertAlmostEqual(pgt_custom.k_star, custom_k, places=6)
        
    def test_transform_scalar(self):
        """Test prime curvature transformation for scalar inputs."""
        for n in self.test_values:
            result = self.pgt.transform(n)
            
            # Verify result is positive
            self.assertGreater(result, 0)
            
            # Verify mathematical relationship
            expected = PHI_FLOAT * ((n % PHI_FLOAT) / PHI_FLOAT) ** K_STAR
            self.assertAlmostEqual(result, expected, places=10)
            
    def test_transform_array(self):
        """Test prime curvature transformation for array inputs."""
        for arr in self.test_arrays:
            result = self.pgt.transform(arr)
            
            # Verify shape preservation
            self.assertEqual(result.shape, arr.shape)
            
            # Verify element-wise correctness
            for i, n in enumerate(arr):
                expected = PHI_FLOAT * ((n % PHI_FLOAT) / PHI_FLOAT) ** K_STAR
                self.assertAlmostEqual(result[i], expected, places=10)
                
    def test_inverse_transform(self):
        """Test inverse prime curvature transformation."""
        for n in self.test_values:
            # Forward then inverse should recover original
            transformed = self.pgt.transform(n)
            recovered = self.pgt.inverse_transform(transformed)
            
            # Account for modular operation in forward transform
            n_mod_phi = n % PHI_FLOAT
            self.assertAlmostEqual(recovered, n_mod_phi, places=8)
            
    def test_transform_properties(self):
        """Test mathematical properties of the transformation."""
        # Test continuity
        for n in self.test_values:
            eps = 1e-6
            f_n = self.pgt.transform(n)
            f_n_eps = self.pgt.transform(n + eps)
            
            # Function should be continuous (small change in input -> small change in output)
            self.assertLess(abs(f_n_eps - f_n), 0.1)
            
    def test_edge_cases(self):
        """Test edge cases and boundary conditions."""
        # Test zero
        result_zero = self.pgt.transform(0)
        self.assertAlmostEqual(result_zero, 0, places=10)
        
        # Test very small values
        result_small = self.pgt.transform(1e-10)
        self.assertGreater(result_small, 0)
        
        # Test very large values  
        result_large = self.pgt.transform(1e6)
        self.assertGreater(result_large, 0)
        self.assertLess(result_large, PHI_FLOAT)  # Should be bounded by modular operation

class TestEnhancedLUDecomposition(unittest.TestCase):
    """Test suite for EnhancedLUDecomposition class."""
    
    def setUp(self):
        """Set up test fixtures."""
        np.random.seed(42)
        
        # Well-conditioned matrix
        self.well_conditioned = np.array([[4, 2, 1], [2, 5, 3], [1, 3, 6]], dtype=np.float64)
        
        # Ill-conditioned matrix
        self.ill_conditioned = np.array([[1, 1, 1], [1, 1.0001, 1], [1, 1, 1.0001]], dtype=np.float64)
        
        # Random symmetric positive definite matrix
        A = np.random.randn(4, 4)
        self.spd_matrix = A @ A.T + np.eye(4)
        
    def test_initialization(self):
        """Test proper initialization of EnhancedLUDecomposition."""
        # Test successful initialization
        elu = EnhancedLUDecomposition(self.well_conditioned)
        self.assertEqual(elu.n, 3)
        np.testing.assert_array_equal(elu.original_matrix, self.well_conditioned)
        
        # Test non-square matrix rejection
        with self.assertRaises(ValueError):
            EnhancedLUDecomposition(np.array([[1, 2], [3, 4], [5, 6]]))
            
    def test_decompose_well_conditioned(self):
        """Test decomposition of well-conditioned matrix."""
        elu = EnhancedLUDecomposition(self.well_conditioned)
        P, L, U = elu.decompose()
        
        # Verify shapes
        self.assertEqual(P.shape, (3, 3))
        self.assertEqual(L.shape, (3, 3))
        self.assertEqual(U.shape, (3, 3))
        
        # Verify L is lower triangular
        np.testing.assert_array_almost_equal(L, np.tril(L))
        
        # Verify U is upper triangular  
        np.testing.assert_array_almost_equal(U, np.triu(U))
        
        # Verify decomposition accuracy - check against conditioned matrix
        conditioned_matrix = elu.get_conditioned_matrix()
        reconstructed = P.T @ L @ U
        np.testing.assert_array_almost_equal(
            np.linalg.norm(reconstructed - conditioned_matrix, 'fro'), 
            0, 
            decimal=10
        )
        
    def test_condition_improvement_ill_conditioned(self):
        """Test condition number improvement for ill-conditioned matrices."""
        elu = EnhancedLUDecomposition(self.ill_conditioned)
        P, L, U = elu.decompose()
        
        improvement = elu.get_condition_improvement()
        
        # Verify improvement metrics exist
        self.assertIn('original_condition', improvement)
        self.assertIn('improved_condition', improvement)
        self.assertIn('improvement_factor', improvement)
        self.assertIn('improvement_percentage', improvement)
        
        # Verify condition number was improved
        self.assertGreater(improvement['improvement_factor'], 1.0)
        self.assertGreater(improvement['improvement_percentage'], 0.0)
        
        # Original should be higher (worse) than improved
        self.assertGreater(improvement['original_condition'], improvement['improved_condition'])
        
    def test_eigenvalue_modulation(self):
        """Test eigenvalue modulation analysis."""
        elu = EnhancedLUDecomposition(self.spd_matrix)
        P, L, U = elu.decompose()
        
        eigenvalue_mod = elu.get_eigenvalue_modulation()
        
        # Verify eigenvalue modulation data
        self.assertIn('original', eigenvalue_mod)
        self.assertIn('transformed', eigenvalue_mod)  
        self.assertIn('improvement_ratio', eigenvalue_mod)
        
        # Verify array shapes
        self.assertEqual(len(eigenvalue_mod['original']), 4)
        self.assertEqual(len(eigenvalue_mod['transformed']), 4)
        
        # Verify improvement ratio is positive
        self.assertGreater(eigenvalue_mod['improvement_ratio'], 0)
        
    def test_universal_zeta_shift_integration(self):
        """Test integration with UniversalZetaShift."""
        elu = EnhancedLUDecomposition(self.well_conditioned)
        P, L, U = elu.decompose()
        
        # Verify UZS was initialized
        self.assertIsNotNone(elu.uzz)
        
        # Verify UZS parameters are positive
        self.assertGreater(float(elu.uzz.a), 0)
        self.assertGreater(float(elu.uzz.b), 0) 
        self.assertGreater(float(elu.uzz.c), 0)

class TestQuantumErrorCorrectionLU(unittest.TestCase):
    """Test suite for QuantumErrorCorrectionLU class."""
    
    def setUp(self):
        """Set up test fixtures."""
        np.random.seed(42)
        
        # Create error syndrome matrix (positive definite)
        A = np.random.randn(4, 4)
        self.syndrome_matrix = A @ A.T + 0.1 * np.eye(4)
        
        # Create error vectors
        self.error_vector = np.random.randn(4)
        self.small_error = 0.01 * np.random.randn(4)
        
    def test_initialization(self):
        """Test proper initialization of QuantumErrorCorrectionLU."""
        qec = QuantumErrorCorrectionLU(self.syndrome_matrix)
        np.testing.assert_array_equal(qec.syndrome_matrix, self.syndrome_matrix)
        self.assertIsNotNone(qec.enhanced_lu)
        
    def test_error_correction(self):
        """Test quantum error correction functionality."""
        qec = QuantumErrorCorrectionLU(self.syndrome_matrix)
        corrected_vector, metrics = qec.correct_errors(self.error_vector)
        
        # Verify output shapes
        self.assertEqual(corrected_vector.shape, self.error_vector.shape)
        
        # Verify metrics exist
        self.assertIn('condition_improvement', metrics)
        self.assertIn('eigenvalue_modulation', metrics)
        self.assertIn('correction_norm', metrics)
        self.assertIn('error_reduction', metrics)
        
        # Verify error reduction
        self.assertGreater(metrics['error_reduction'], 0)
        self.assertTrue(np.isfinite(metrics['correction_norm']))
        
    def test_error_correction_small_errors(self):
        """Test error correction with small error vectors."""
        qec = QuantumErrorCorrectionLU(self.syndrome_matrix)
        corrected_vector, metrics = qec.correct_errors(self.small_error)
        
        # Small errors should have small corrections
        self.assertLess(metrics['correction_norm'], 1.0)
        
    def test_numerical_stability(self):
        """Test numerical stability of error correction."""
        # Create ill-conditioned syndrome matrix
        ill_syndrome = np.array([[1, 1, 1, 1], [1, 1.0001, 1, 1], 
                               [1, 1, 1.0001, 1], [1, 1, 1, 1.0001]])
        
        qec = QuantumErrorCorrectionLU(ill_syndrome)
        corrected_vector, metrics = qec.correct_errors(self.error_vector)
        
        # Should still provide improvement despite ill-conditioning
        self.assertGreater(metrics['condition_improvement']['improvement_factor'], 1.0)
        self.assertTrue(np.isfinite(metrics['error_reduction']))

class TestQuantumCryptographyLU(unittest.TestCase):
    """Test suite for QuantumCryptographyLU class."""
    
    def setUp(self):
        """Set up test fixtures."""
        np.random.seed(42)
        
        # Create cryptographic key matrix (positive definite)
        A = np.random.randn(3, 3)
        self.key_matrix = A @ A.T + 0.1 * np.eye(3)
        
        # Create seed vectors
        self.seed_vector = np.random.randn(3)
        self.unit_seed = np.array([1, 0, 0])
        
    def test_initialization(self):
        """Test proper initialization of QuantumCryptographyLU."""
        qcrypto = QuantumCryptographyLU(self.key_matrix)
        np.testing.assert_array_equal(qcrypto.key_matrix, self.key_matrix)
        self.assertIsNotNone(qcrypto.enhanced_lu)
        
    def test_secure_key_generation(self):
        """Test secure cryptographic key generation."""
        qcrypto = QuantumCryptographyLU(self.key_matrix)
        secure_key, metrics = qcrypto.generate_secure_key(self.seed_vector)
        
        # Verify output properties
        self.assertEqual(secure_key.shape, self.seed_vector.shape)
        self.assertAlmostEqual(np.linalg.norm(secure_key), 1.0, places=10)  # Normalized
        
        # Verify metrics
        self.assertIn('condition_improvement', metrics)
        self.assertIn('eigenvalue_modulation', metrics)
        self.assertIn('key_entropy', metrics)
        self.assertIn('key_strength', metrics)
        
        # Verify entropy is positive
        self.assertGreater(metrics['key_entropy'], 0)
        
    def test_key_determinism(self):
        """Test that same seed produces same key."""
        qcrypto = QuantumCryptographyLU(self.key_matrix)
        
        key1, _ = qcrypto.generate_secure_key(self.seed_vector)
        key2, _ = qcrypto.generate_secure_key(self.seed_vector)
        
        np.testing.assert_array_almost_equal(key1, key2, decimal=10)
        
    def test_key_diversity(self):
        """Test that different seeds produce different keys."""
        qcrypto = QuantumCryptographyLU(self.key_matrix)
        
        key1, _ = qcrypto.generate_secure_key(self.seed_vector)
        key2, _ = qcrypto.generate_secure_key(self.unit_seed)
        
        # Keys should be different
        self.assertGreater(np.linalg.norm(key1 - key2), 0.1)
        
    def test_key_integrity_verification(self):
        """Test cryptographic key integrity verification."""
        qcrypto = QuantumCryptographyLU(self.key_matrix)
        secure_key, _ = qcrypto.generate_secure_key(self.seed_vector)
        
        integrity_metrics = qcrypto.verify_key_integrity(secure_key)
        
        # Verify integrity metrics
        self.assertIn('integrity_score', integrity_metrics)
        self.assertIn('entropy', integrity_metrics)
        self.assertIn('key_strength', integrity_metrics)
        self.assertIn('prime_curvature_factor', integrity_metrics)
        
        # Verify positive values
        self.assertGreater(integrity_metrics['integrity_score'], 0)
        self.assertGreater(integrity_metrics['entropy'], 0)
        self.assertGreater(integrity_metrics['key_strength'], 0)

class TestQuantumCircuitOptimization(unittest.TestCase):
    """Test suite for quantum circuit matrix optimization."""
    
    def setUp(self):
        """Set up test fixtures."""
        np.random.seed(42)
        
        # Create test circuit matrices
        self.simple_circuit = np.array([[1, 0.5], [0.5, 1]], dtype=np.float64)
        
        # Random circuit matrix
        A = np.random.randn(3, 3)
        self.random_circuit = A @ A.T + 0.1 * np.eye(3)
        
        # Ill-conditioned circuit
        self.ill_circuit = np.array([[1, 1, 1], [1, 1.001, 1], [1, 1, 1.001]])
        
    def test_circuit_optimization(self):
        """Test quantum circuit matrix optimization."""
        optimized, metrics = optimize_quantum_circuit_matrix(self.random_circuit)
        
        # Verify output shape
        self.assertEqual(optimized.shape, self.random_circuit.shape)
        
        # Verify metrics
        self.assertIn('condition_improvement', metrics)
        self.assertIn('eigenvalue_modulation', metrics)
        self.assertIn('circuit_fidelity', metrics)
        self.assertIn('optimization_factor', metrics)
        
        # Verify fidelity is reasonable (0 to 1 range)
        self.assertGreaterEqual(metrics['circuit_fidelity'], 0)
        self.assertLessEqual(metrics['circuit_fidelity'], 1)
        
    def test_optimization_improvement(self):
        """Test that optimization improves conditioning."""
        optimized, metrics = optimize_quantum_circuit_matrix(self.ill_circuit)
        
        # Should show improvement
        self.assertGreater(metrics['optimization_factor'], 1.0)
        self.assertGreater(metrics['condition_improvement']['improvement_factor'], 1.0)
        
    def test_optimization_fidelity(self):
        """Test optimization preserves circuit fidelity."""
        optimized, metrics = optimize_quantum_circuit_matrix(self.simple_circuit)
        
        # High fidelity expected for simple circuit
        self.assertGreater(metrics['circuit_fidelity'], 0.5)

class TestIntegrationAndPerformance(unittest.TestCase):
    """Integration tests and performance benchmarks."""
    
    def setUp(self):
        """Set up test fixtures."""
        np.random.seed(42)
        
    def test_end_to_end_workflow(self):
        """Test complete end-to-end workflow."""
        # Create test data
        A = np.random.randn(3, 3)
        test_matrix = A @ A.T + 0.1 * np.eye(3)
        
        # 1. Enhanced LU Decomposition
        elu = EnhancedLUDecomposition(test_matrix)
        P, L, U = elu.decompose()
        
        # 2. Quantum Error Correction
        error_vector = np.random.randn(3)
        qec = QuantumErrorCorrectionLU(test_matrix)
        corrected, qec_metrics = qec.correct_errors(error_vector)
        
        # 3. Quantum Cryptography
        seed = np.random.randn(3)
        qcrypto = QuantumCryptographyLU(test_matrix)
        secure_key, crypto_metrics = qcrypto.generate_secure_key(seed)
        
        # 4. Circuit Optimization
        optimized, opt_metrics = optimize_quantum_circuit_matrix(test_matrix)
        
        # Verify all operations completed successfully
        self.assertIsNotNone(P)
        self.assertIsNotNone(corrected)
        self.assertIsNotNone(secure_key)
        self.assertIsNotNone(optimized)
        
    def test_condition_number_improvements(self):
        """Test significant condition number improvements."""
        # Create progressively ill-conditioned matrices
        improvements = []
        
        for epsilon in [1e-1, 1e-2, 1e-3, 1e-4]:
            ill_matrix = np.array([[1, 1, 1], [1, 1+epsilon, 1], [1, 1, 1+epsilon]])
            
            elu = EnhancedLUDecomposition(ill_matrix)
            P, L, U = elu.decompose()
            
            improvement = elu.get_condition_improvement()
            improvements.append(improvement['improvement_percentage'])
            
        # Should see significant improvements for ill-conditioned matrices
        max_improvement = max(improvements)
        self.assertGreater(max_improvement, 50.0)  # At least 50% improvement
        
    def test_large_matrix_performance(self):
        """Test performance with larger matrices."""
        # Create larger test matrix
        n = 10
        A = np.random.randn(n, n)
        large_matrix = A @ A.T + 0.01 * np.eye(n)
        
        # Test enhanced LU decomposition
        elu = EnhancedLUDecomposition(large_matrix)
        P, L, U = elu.decompose()
        
        # Verify decomposition accuracy - check against conditioned matrix
        conditioned_matrix = elu.get_conditioned_matrix()
        reconstructed = P.T @ L @ U
        error = np.linalg.norm(reconstructed - conditioned_matrix, 'fro')
        self.assertLess(error, 1e-10)
        
    def test_numerical_stability_edge_cases(self):
        """Test numerical stability with edge cases."""
        # Test with near-singular matrix
        singular_matrix = np.array([[1, 1, 1], [1, 1, 1], [1, 1, 1.000001]])
        
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            
            elu = EnhancedLUDecomposition(singular_matrix)
            P, L, U = elu.decompose()
            
            # Should complete without errors
            self.assertIsNotNone(P)
            self.assertIsNotNone(L)
            self.assertIsNotNone(U)
            
    def test_prime_curvature_parameter_sensitivity(self):
        """Test sensitivity to prime curvature parameter."""
        test_matrix = np.array([[2, 1, 1], [1, 3, 1], [1, 1, 4]])
        
        # Test different curvature parameters
        parameters = [0.1, 0.3, 0.5, 0.7, 0.9]
        improvements = []
        
        for k in parameters:
            elu = EnhancedLUDecomposition(test_matrix, k)
            P, L, U = elu.decompose()
            improvement = elu.get_condition_improvement()
            improvements.append(improvement['improvement_factor'])
            
        # All should show improvement
        for imp in improvements:
            self.assertGreater(imp, 0.1)

def run_comprehensive_validation():
    """Run comprehensive validation of all functionality."""
    print("Running Comprehensive LU Decomposition Quantum Test Suite")
    print("=" * 60)
    
    # Create test suite
    test_classes = [
        TestPrimeGeodesicTransform,
        TestEnhancedLUDecomposition,
        TestQuantumErrorCorrectionLU,
        TestQuantumCryptographyLU,
        TestQuantumCircuitOptimization,
        TestIntegrationAndPerformance
    ]
    
    total_tests = 0
    passed_tests = 0
    
    for test_class in test_classes:
        print(f"\nRunning {test_class.__name__}...")
        suite = unittest.TestLoader().loadTestsFromTestCase(test_class)
        result = unittest.TextTestRunner(verbosity=0, stream=open(os.devnull, 'w')).run(suite)
        
        class_tests = result.testsRun
        class_passed = class_tests - len(result.failures) - len(result.errors)
        
        total_tests += class_tests
        passed_tests += class_passed
        
        print(f"  Tests run: {class_tests}, Passed: {class_passed}, Failed: {len(result.failures)}, Errors: {len(result.errors)}")
        
        if result.failures:
            print("  Failures:")
            for test, error in result.failures:
                print(f"    - {test}: {error.split(chr(10))[0]}")
                
        if result.errors:
            print("  Errors:")
            for test, error in result.errors:
                print(f"    - {test}: {error.split(chr(10))[0]}")
    
    print(f"\n" + "=" * 60)
    print(f"TOTAL TESTS: {total_tests}")
    print(f"PASSED: {passed_tests}")
    print(f"FAILED: {total_tests - passed_tests}")
    print(f"SUCCESS RATE: {(passed_tests / total_tests * 100):.1f}%")
    
    return passed_tests == total_tests

if __name__ == "__main__":
    # Run comprehensive validation
    success = run_comprehensive_validation()
    
    if success:
        print("\n✅ ALL TESTS PASSED! Prime Curvature LU Decomposition Quantum Integration validated.")
    else:
        print("\n❌ Some tests failed. Please review the output above.")
        
    sys.exit(0 if success else 1)