"""
Tests for Charge as v_w Motion Simulation

Validates the implementation of charge as velocity in the w-dimension,
testing unification of gravity and electromagnetism within the Z framework.
"""

import sys
import os
import unittest
import numpy as np

# Add core to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from core.charge_simulation import (
    ChargedParticle, ChargeSimulation, 
    create_hydrogen_atom_simulation, validate_unification_principle,
    C_LIGHT, ALPHA_EM, R_COMPACTIFICATION
)
from core.domain import DiscreteZetaShift

class TestChargedParticle(unittest.TestCase):
    """Test ChargedParticle class functionality."""
    
    def setUp(self):
        """Set up test particles."""
        self.electron = ChargedParticle(charge=-1.0, mass=0.000511, n_index=3)
        self.proton = ChargedParticle(charge=1.0, mass=0.938, n_index=2)
        self.neutral = ChargedParticle(charge=0.0, mass=1.0, n_index=5)
        
    def test_particle_initialization(self):
        """Test particle creation and basic properties."""
        # Check basic properties
        self.assertEqual(self.electron.charge, -1.0)
        self.assertEqual(self.electron.mass, 0.000511)
        self.assertEqual(self.electron.n_index, 3)
        
        # Check 5D coordinates exist
        self.assertEqual(len(self.electron.coords_5d), 5)
        self.assertIsInstance(self.electron.x, float)
        self.assertIsInstance(self.electron.y, float)
        self.assertIsInstance(self.electron.z, float)
        self.assertIsInstance(self.electron.w, float)
        self.assertIsInstance(self.electron.u, float)
        
    def test_v_w_computation(self):
        """Test w-dimension velocity computation from charge."""
        # Charged particles should have non-zero v_w
        self.assertNotEqual(self.electron.v_w, 0.0)
        self.assertNotEqual(self.proton.v_w, 0.0)
        
        # Neutral particles should have zero v_w
        self.assertEqual(self.neutral.v_w, 0.0)
        
        # v_w should be bounded by speed of light
        self.assertLess(abs(self.electron.v_w), C_LIGHT)
        self.assertLess(abs(self.proton.v_w), C_LIGHT)
        
        # Opposite charges should have opposite v_w signs
        self.assertLess(self.electron.v_w * self.proton.v_w, 0)
        
    def test_electromagnetic_field(self):
        """Test electromagnetic field computation."""
        position = [1.0, 0.0, 0.0]  # 1 unit away on x-axis
        
        E_field, B_field = self.electron.get_electromagnetic_field(position)
        
        # Fields should be 3D vectors
        self.assertEqual(len(E_field), 3)
        self.assertEqual(len(B_field), 3)
        
        # Electric field should point away from negative charge
        self.assertLess(E_field[0], 0)  # Points toward electron
        
        # Field magnitude should be reasonable
        E_magnitude = np.linalg.norm(E_field)
        self.assertGreater(E_magnitude, 0)
        self.assertLess(E_magnitude, 1e10)  # Not infinite
        
    def test_gravitational_curvature(self):
        """Test gravitational curvature calculation."""
        gravity_curve = self.proton.get_gravitational_curvature()
        
        # Should be positive (attractive)
        self.assertGreater(gravity_curve, 0)
        
        # Should scale with mass
        heavy_particle = ChargedParticle(charge=0.0, mass=10.0, n_index=5)
        heavy_gravity = heavy_particle.get_gravitational_curvature()
        self.assertGreater(heavy_gravity, gravity_curve)
        
    def test_electromagnetic_curvature(self):
        """Test electromagnetic curvature calculation."""
        em_curve = self.electron.get_electromagnetic_curvature()
        
        # Should be positive
        self.assertGreater(em_curve, 0)
        
        # Should be zero for neutral particles
        neutral_em = self.neutral.get_electromagnetic_curvature()
        self.assertEqual(neutral_em, 0)
        
    def test_unified_curvature(self):
        """Test unified gravity-EM curvature."""
        unified_curve = self.proton.get_unified_curvature()
        gravity_curve = self.proton.get_gravitational_curvature()
        em_curve = self.proton.get_electromagnetic_curvature()
        
        # Unified should include both components
        self.assertGreater(unified_curve, gravity_curve)
        self.assertGreater(unified_curve, em_curve)
        
        # Should include interaction term
        simple_sum = gravity_curve + em_curve
        self.assertNotEqual(unified_curve, simple_sum)

class TestChargeSimulation(unittest.TestCase):
    """Test ChargeSimulation class functionality."""
    
    def setUp(self):
        """Set up test simulation."""
        self.sim = ChargeSimulation()
        
    def test_add_particle(self):
        """Test adding particles to simulation."""
        # Add test particles
        electron = self.sim.add_particle(charge=-1.0, mass=0.000511)
        proton = self.sim.add_particle(charge=1.0, mass=0.938)
        
        # Check particles were added
        self.assertEqual(len(self.sim.particles), 2)
        self.assertIsInstance(electron, ChargedParticle)
        self.assertIsInstance(proton, ChargedParticle)
        
    def test_field_computation(self):
        """Test total field computation from multiple particles."""
        # Add electron and proton
        self.sim.add_particle(charge=-1.0, mass=0.000511)
        self.sim.add_particle(charge=1.0, mass=0.938)
        
        # Compute field at test position
        position = [0.0, 0.0, 1.0]
        E_total, B_total = self.sim.compute_field_at_position(position)
        
        # Fields should be vectors
        self.assertEqual(len(E_total), 3)
        self.assertEqual(len(B_total), 3)
        
        # Total field should be superposition of individual fields
        self.assertIsInstance(E_total[0], (int, float, np.floating))
        self.assertIsInstance(B_total[0], (int, float, np.floating))
        
    def test_kaluza_klein_modes(self):
        """Test Kaluza-Klein tower computation."""
        kk_modes = self.sim.compute_kaluza_klein_modes(n_max=5)
        
        # Should return list of modes
        self.assertEqual(len(kk_modes), 5)
        
        # Each mode should have required properties
        for i, mode in enumerate(kk_modes):
            self.assertEqual(mode['n'], i + 1)
            self.assertGreater(mode['mass'], 0)
            self.assertGreater(mode['coupling_strength'], 0)
            self.assertGreater(mode['production_cross_section'], 0)
            
        # Masses should increase with mode number
        masses = [mode['mass'] for mode in kk_modes]
        self.assertEqual(masses, sorted(masses))
        
    def test_lhc_collision_simulation(self):
        """Test LHC collision simulation."""
        beam_energy = 14000  # GeV
        collision_data = self.sim.simulate_lhc_collision(beam_energy)
        
        # Should return collision data dictionary
        self.assertIsInstance(collision_data, dict)
        
        # Check required fields
        required_fields = [
            'beam_energy', 'v_w_beam1', 'v_w_beam2',
            'unified_curvature_beam1', 'unified_curvature_beam2',
            'kaluza_klein_modes', 'w_dimension_signature',
            'em_gravity_coupling', 'predicted_signatures'
        ]
        
        for field in required_fields:
            self.assertIn(field, collision_data)
            
        # Energy should match input
        self.assertEqual(collision_data['beam_energy'], beam_energy)
        
        # Should have added beam particles
        self.assertEqual(len(self.sim.particles), 2)

class TestUnificationValidation(unittest.TestCase):
    """Test gravity-EM unification validation."""
    
    def test_hydrogen_atom_simulation(self):
        """Test hydrogen atom simulation using v_w model."""
        hydrogen = create_hydrogen_atom_simulation()
        
        # Should return simulation components
        required_keys = [
            'simulation', 'proton', 'electron', 'binding_energy',
            'electron_v_w', 'proton_v_w', 'unified_atom_curvature'
        ]
        
        for key in required_keys:
            self.assertIn(key, hydrogen)
            
        # Check particle properties
        self.assertEqual(hydrogen['proton'].charge, 1.0)
        self.assertEqual(hydrogen['electron'].charge, -1.0)
        
        # Electron should have higher |v_w| due to lower mass
        self.assertGreater(abs(hydrogen['electron_v_w']), 
                          abs(hydrogen['proton_v_w']))
        
        # Binding energy should be negative (bound state)
        self.assertLess(hydrogen['binding_energy'], 0)
        
    def test_unification_principle(self):
        """Test that unification provides additional physics beyond separation."""
        validation = validate_unification_principle()
        
        # Should return validation metrics
        required_keys = [
            'gravity_curvature', 'em_curvature', 'separated_total',
            'unified_total', 'unification_factor', 'v_w_contribution',
            'validates_unification'
        ]
        
        for key in required_keys:
            self.assertIn(key, validation)
            
        # All curvatures should be positive
        self.assertGreater(validation['gravity_curvature'], 0)
        self.assertGreater(validation['em_curvature'], 0)
        self.assertGreater(validation['unified_total'], 0)
        
        # Unification should add new physics (factor > 1)
        self.assertGreater(validation['unification_factor'], 1.0)
        self.assertTrue(validation['validates_unification'])
        
        # v_w contribution should be reasonable
        self.assertGreater(abs(validation['v_w_contribution']), 0)
        self.assertLess(abs(validation['v_w_contribution']), 1.0)

class TestPhysicalConsistency(unittest.TestCase):
    """Test physical consistency of the model."""
    
    def test_charge_conservation(self):
        """Test that charge is properly conserved."""
        # Create electron-positron pair
        electron = ChargedParticle(charge=-1.0, mass=0.000511, n_index=3)
        positron = ChargedParticle(charge=1.0, mass=0.000511, n_index=4)
        
        # Total charge should be zero
        total_charge = electron.charge + positron.charge
        self.assertEqual(total_charge, 0.0)
        
        # v_w should have opposite signs
        self.assertLess(electron.v_w * positron.v_w, 0)
        
    def test_relativistic_constraints(self):
        """Test that relativistic constraints are satisfied."""
        # Create highly charged particle
        heavy_charge = ChargedParticle(charge=10.0, mass=1.0, n_index=10)
        
        # v_w should be less than speed of light
        self.assertLess(abs(heavy_charge.v_w), C_LIGHT)
        
        # Gamma factor should be real and > 1
        gamma = 1 / np.sqrt(1 - (heavy_charge.v_w / C_LIGHT)**2)
        self.assertGreater(gamma, 1.0)
        self.assertTrue(np.isfinite(gamma))
        
    def test_dimensional_consistency(self):
        """Test dimensional consistency of calculations."""
        particle = ChargedParticle(charge=1.0, mass=1.0, n_index=5)
        
        # Check that curvatures have consistent dimensions
        gravity_curve = particle.get_gravitational_curvature()
        em_curve = particle.get_electromagnetic_curvature()
        unified_curve = particle.get_unified_curvature()
        
        # All should have same units (inverse length squared)
        self.assertIsInstance(gravity_curve, (int, float, np.floating))
        self.assertIsInstance(em_curve, (int, float, np.floating))
        self.assertIsInstance(unified_curve, (int, float, np.floating))
        
        # Check field units
        position = [1.0, 0.0, 0.0]
        E_field, B_field = particle.get_electromagnetic_field(position)
        
        # Fields should have reasonable magnitudes
        E_mag = np.linalg.norm(E_field)
        B_mag = np.linalg.norm(B_field)
        
        self.assertGreater(E_mag, 0)
        self.assertGreater(B_mag, 0)
        self.assertTrue(np.isfinite(E_mag))
        self.assertTrue(np.isfinite(B_mag))

class TestNumericalStability(unittest.TestCase):
    """Test numerical stability of calculations."""
    
    def test_extreme_charges(self):
        """Test behavior with extreme charge values."""
        # Very small charge
        tiny_charge = ChargedParticle(charge=1e-10, mass=1.0, n_index=5)
        self.assertTrue(np.isfinite(tiny_charge.v_w))
        self.assertLess(abs(tiny_charge.v_w), C_LIGHT)
        
        # Large charge (should be clamped)
        large_charge = ChargedParticle(charge=1000.0, mass=1.0, n_index=5)
        self.assertTrue(np.isfinite(large_charge.v_w))
        self.assertLess(abs(large_charge.v_w), C_LIGHT)
        
    def test_extreme_masses(self):
        """Test behavior with extreme mass values."""
        # Very light particle
        light_particle = ChargedParticle(charge=1.0, mass=1e-10, n_index=5)
        self.assertTrue(np.isfinite(light_particle.get_gravitational_curvature()))
        
        # Very heavy particle
        heavy_particle = ChargedParticle(charge=1.0, mass=1e10, n_index=5)
        self.assertTrue(np.isfinite(heavy_particle.get_gravitational_curvature()))
        
    def test_field_singularities(self):
        """Test field calculations near particle positions."""
        particle = ChargedParticle(charge=1.0, mass=1.0, n_index=5)
        
        # Position very close to particle
        close_position = [particle.x + 1e-10, particle.y, particle.z]
        E_field, B_field = particle.get_electromagnetic_field(close_position)
        
        # Fields should be finite (singularity handled)
        self.assertTrue(np.all(np.isfinite(E_field)))
        self.assertTrue(np.all(np.isfinite(B_field)))

def run_tests():
    """Run all tests and return results."""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    test_classes = [
        TestChargedParticle,
        TestChargeSimulation, 
        TestUnificationValidation,
        TestPhysicalConsistency,
        TestNumericalStability
    ]
    
    for test_class in test_classes:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Return summary
    return {
        'tests_run': result.testsRun,
        'failures': len(result.failures),
        'errors': len(result.errors),
        'success': result.wasSuccessful()
    }

if __name__ == "__main__":
    print("Running Charge as v_w Motion Tests")
    print("=" * 50)
    
    results = run_tests()
    
    print("\n" + "=" * 50)
    print("Test Summary:")
    print(f"  Tests run: {results['tests_run']}")
    print(f"  Failures: {results['failures']}")
    print(f"  Errors: {results['errors']}")
    print(f"  Success: {results['success']}")
    
    if results['success']:
        print("\nAll tests passed! ✓")
    else:
        print("\nSome tests failed! ✗")
        
    # Run validation examples
    print("\n" + "=" * 50)
    print("Running Validation Examples:")
    
    # Test unification principle
    validation = validate_unification_principle()
    print(f"\nUnification Validation:")
    print(f"  Unification factor: {validation['unification_factor']:.3f}")
    print(f"  Validates unification: {validation['validates_unification']}")
    
    # Test hydrogen atom
    hydrogen = create_hydrogen_atom_simulation()
    print(f"\nHydrogen Atom Simulation:")
    print(f"  Electron v_w: {hydrogen['electron_v_w']:.6f}")
    print(f"  Proton v_w: {hydrogen['proton_v_w']:.6f}")
    print(f"  Modified binding energy: {hydrogen['binding_energy']:.3f} eV")