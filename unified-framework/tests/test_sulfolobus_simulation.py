#!/usr/bin/env python3
"""
Test suite for Sulfolobus genomics simulation
===========================================

Validates that the simulation reproduces expected findings correctly.
"""

import sys
import os
import unittest
import json

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src'))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.sulfolobus_genomics_simulation import SulfolobusGenomicsSimulation


class TestSulfolobusSimulation(unittest.TestCase):
    """Test cases for Sulfolobus genomics simulation"""
    
    def setUp(self):
        """Set up test instance"""
        self.simulation = SulfolobusGenomicsSimulation()
        
    def test_initialization(self):
        """Test simulation initialization"""
        self.assertEqual(self.simulation.n_genes, 2222)  # Updated gene count
        self.assertEqual(self.simulation.b_curvature, 0.3)
        self.assertAlmostEqual(self.simulation.c_delta_max, 7.389056, places=6)
        self.assertEqual(self.simulation.target_variance, 0.118)
        # Test new metabolic parameters
        self.assertEqual(self.simulation.growth_rate_glycerol, 0.0287)
        self.assertEqual(self.simulation.growth_rate_xylose, 0.0195)
        
    def test_zeta_shift_findings(self):
        """Test zeta shift computation accuracy"""
        results = self.simulation.reproduce_zeta_shift_findings()
        
        # Test initial z value (updated for 2222 genes)
        self.assertAlmostEqual(results['z_initial'], 90.23, delta=0.1)
        self.assertLess(results['z_initial_error'], 0.1)
        
        # Test next z value  
        self.assertAlmostEqual(results['z_next'], 0.829, delta=0.001)
        self.assertLess(results['z_next_error'], 0.001)
        
    def test_secondary_zeta_shift(self):
        """Test secondary zeta shift for metabolic rates"""
        results = self.simulation.reproduce_secondary_zeta_shift()
        
        # Test secondary z value (growth rate analysis)
        self.assertAlmostEqual(results['z_secondary'], 0.00117, delta=0.0001)
        self.assertLess(results['z_secondary_error'], 0.0001)
        
        # Test metabolic next z value
        self.assertAlmostEqual(results['z_next_metabolic'], 0.15, delta=0.01)
        self.assertLess(results['z_next_metabolic_error'], 0.01)
        
        # Test growth enhancement factor (~47%)
        expected_enhancement = 0.0287 / 0.0195  # ~1.47
        self.assertAlmostEqual(results['growth_enhancement_factor'], expected_enhancement, delta=0.01)
        
    def test_helical_embeddings(self):
        """Test helical coordinate reproduction"""
        results = self.simulation.reproduce_helical_embeddings()
        
        expected = results['expected']
        actual = results['actual']
        
        # Test all coordinates match expected values
        self.assertAlmostEqual(actual['x'], expected['x'], delta=0.001)
        self.assertAlmostEqual(actual['y'], expected['y'], delta=0.001)
        self.assertAlmostEqual(actual['z'], expected['z'], delta=0.001)
        self.assertAlmostEqual(actual['w'], expected['w'], delta=0.001)
        self.assertAlmostEqual(actual['u'], expected['u'], delta=0.001)
        
    def test_variance_trim(self):
        """Test variance reduction analysis"""
        results = self.simulation.reproduce_variance_trim()
        
        # Test 23% reduction is achieved
        self.assertAlmostEqual(results['trim_percentage'], 23.0, delta=0.1)
        self.assertLess(results['trim_error'], 0.1)
        
        # Test variance values are reasonable
        self.assertEqual(results['sigma_original'], 0.118)
        self.assertLess(results['sigma_optimized'], results['sigma_original'])
        
    def test_crispr_boost(self):
        """Test CRISPR efficacy boost"""
        results = self.simulation.reproduce_crispr_boost()
        
        # Test 20% boost is achieved exactly
        self.assertAlmostEqual(results['boost_percentage'], 20.0, delta=0.001)
        self.assertLess(results['boost_error'], 0.001)
        
        # Test boost factor
        self.assertEqual(results['boost_factor'], 1.2)
        
    def test_symbolic_validation(self):
        """Test symbolic constant validation"""
        results = self.simulation.validate_symbolic_links()
        
        # Test mathematical constants are present
        self.assertIn('phi_value', results)
        self.assertIn('pi_connection', results)
        self.assertIn('e_squared', results)
        
        # Test phi value is correct
        self.assertAlmostEqual(results['phi_value'], 1.618034, delta=0.000001)
        
    def test_full_simulation_success(self):
        """Test complete simulation runs successfully"""
        results = self.simulation.run_full_simulation()
        
        # Test overall success
        self.assertTrue(results['overall_success'])
        
        # Test all individual validations pass
        validation_status = results['validation_status']
        self.assertTrue(validation_status['zeta_shift_valid'])
        self.assertTrue(validation_status['helical_valid'])
        self.assertTrue(validation_status['variance_valid'])
        self.assertTrue(validation_status['crispr_valid'])
        
        # Test simulation parameters are correct
        params = results['simulation_parameters']
        self.assertEqual(params['n_genes'], 2222)  # Updated gene count
        self.assertEqual(params['b_curvature'], 0.3)
        self.assertEqual(params['precision_dps'], 50)
        # Test new metabolic parameters
        self.assertEqual(params['growth_rate_glycerol'], 0.0287)
        self.assertEqual(params['growth_rate_xylose'], 0.0195)
        
    def test_json_serialization(self):
        """Test results can be serialized to JSON through main function"""
        # Test that main function handles JSON serialization correctly
        from scripts.sulfolobus_genomics_simulation import main
        
        # Should not raise exception when main runs
        try:
            results = main()
            self.assertIsNotNone(results)
            
            # Check that JSON file was created
            import os
            json_file = 'sulfolobus_simulation_results.json'
            self.assertTrue(os.path.exists(json_file))
            
            # Should be able to read the JSON file
            import json
            with open(json_file, 'r') as f:
                restored = json.load(f)
                self.assertIsInstance(restored, dict)
                
        except Exception as e:
            self.fail(f"JSON serialization through main() failed: {e}")


if __name__ == '__main__':
    unittest.main()