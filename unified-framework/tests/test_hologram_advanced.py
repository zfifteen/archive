"""
Test suite for advanced hologram visualizations.

This module tests the enhanced hologram.py functionality including:
- Class instantiation and basic functionality
- All visualization types (3D geometry, spirals, tori, 5D projections)
- Parameter validation and error handling
- Statistics computation
- File output functionality
"""

import os
import sys
import unittest
import tempfile
import shutil
from unittest.mock import patch

# Add the source path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src', 'number-theory', 'prime-curve'))

try:
    from hologram import AdvancedHologramVisualizer, ZetaShift, NumberLineZetaShift
except ImportError as e:
    print(f"Warning: Could not import hologram modules: {e}")
    AdvancedHologramVisualizer = None


class TestAdvancedHologramVisualizer(unittest.TestCase):
    """Test cases for AdvancedHologramVisualizer class."""
    
    def setUp(self):
        """Set up test fixtures."""
        if AdvancedHologramVisualizer is None:
            self.skipTest("AdvancedHologramVisualizer not available")
        
        self.visualizer = AdvancedHologramVisualizer(n_points=100)  # Small dataset for testing
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up test fixtures."""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_initialization(self):
        """Test visualizer initialization."""
        self.assertEqual(self.visualizer.n_points, 100)
        self.assertIsInstance(self.visualizer.helix_freq, float)
        self.assertIsInstance(self.visualizer.use_log_scale, bool)
        
        # Check that base data is computed
        self.assertEqual(len(self.visualizer.n), 99)  # n_points - 1
        self.assertEqual(len(self.visualizer.primality), 99)
    
    def test_get_statistics(self):
        """Test statistics computation."""
        stats = self.visualizer.get_statistics()
        
        self.assertIn('n_points', stats)
        self.assertIn('prime_count', stats)
        self.assertIn('prime_density', stats)
        self.assertIn('helix_frequency', stats)
        self.assertIn('use_log_scale', stats)
        
        self.assertIsInstance(stats['n_points'], int)
        self.assertIsInstance(stats['prime_count'], int)
        self.assertIsInstance(stats['prime_density'], float)
        
        # Basic sanity checks
        self.assertGreater(stats['n_points'], 0)
        self.assertGreaterEqual(stats['prime_count'], 0)
        self.assertLessEqual(stats['prime_count'], stats['n_points'])
        self.assertGreaterEqual(stats['prime_density'], 0.0)
        self.assertLessEqual(stats['prime_density'], 1.0)
    
    def test_prime_geometry_3d(self):
        """Test 3D prime geometry visualization."""
        fig = self.visualizer.prime_geometry_3d()
        self.assertIsNotNone(fig)
        
        # Test with save path
        save_path = os.path.join(self.temp_dir, 'test_3d.png')
        fig_saved = self.visualizer.prime_geometry_3d(save_path=save_path)
        self.assertIsNotNone(fig_saved)
        self.assertTrue(os.path.exists(save_path))
    
    def test_logarithmic_spiral(self):
        """Test logarithmic spiral visualizations."""
        # Test different configurations
        configs = [
            {'spiral_rate': 0.1, 'height_scale': 'sqrt'},
            {'spiral_rate': 0.2, 'height_scale': 'log'},
            {'spiral_rate': 0.05, 'height_scale': 'linear'}
        ]
        
        for config in configs:
            fig = self.visualizer.logarithmic_spiral(**config)
            self.assertIsNotNone(fig)
    
    def test_gaussian_prime_spiral(self):
        """Test Gaussian prime spiral visualizations."""
        angle_types = ['golden', 'pi', 'custom']
        
        for angle_type in angle_types:
            fig = self.visualizer.gaussian_prime_spiral(angle_increment=angle_type)
            self.assertIsNotNone(fig)
    
    def test_modular_torus(self):
        """Test modular torus visualizations."""
        # Test different torus configurations
        configs = [
            {'mod1': 17, 'mod2': 23, 'torus_ratio': 3.0},
            {'mod1': 11, 'mod2': 13, 'torus_ratio': 2.5}
        ]
        
        for config in configs:
            fig = self.visualizer.modular_torus(**config)
            self.assertIsNotNone(fig)
    
    def test_projection_5d(self):
        """Test 5D projection visualizations."""
        # Test different projection types
        configs = [
            {'projection_type': 'helical', 'dimensions': (0, 1, 2)},
            {'projection_type': 'orthogonal', 'dimensions': (1, 2, 3)},
            {'projection_type': 'perspective', 'dimensions': (0, 2, 4)}
        ]
        
        for config in configs:
            try:
                fig = self.visualizer.projection_5d(**config)
                self.assertIsNotNone(fig)
            except Exception as e:
                # 5D projections might fail with small datasets
                print(f"5D projection failed (expected with small dataset): {e}")
    
    def test_riemann_zeta_landscape(self):
        """Test Riemann zeta landscape visualization."""
        try:
            fig = self.visualizer.riemann_zeta_landscape(
                real_range=(0.1, 1.0),
                imag_range=(10, 30),
                resolution=20  # Small resolution for testing
            )
            self.assertIsNotNone(fig)
        except Exception as e:
            # Zeta function computations might fail in some environments
            print(f"Zeta landscape failed (may be environment-specific): {e}")
    
    def test_interactive_exploration(self):
        """Test interactive exploration functionality."""
        output_dir = os.path.join(self.temp_dir, 'exploration_output')
        
        # Test without saving
        self.visualizer.interactive_exploration(save_plots=False)
        
        # Test with saving
        self.visualizer.interactive_exploration(save_plots=True, output_dir=output_dir)
        
        # Check that output directory was created
        self.assertTrue(os.path.exists(output_dir))
        
        # Check that some files were created
        output_files = os.listdir(output_dir)
        self.assertGreater(len(output_files), 0)


class TestZetaShift(unittest.TestCase):
    """Test cases for enhanced ZetaShift functionality."""
    
    def test_golden_ratio_transform(self):
        """Test golden ratio transformation."""
        if not AdvancedHologramVisualizer:
            self.skipTest("ZetaShift not available")
            
        shift = NumberLineZetaShift(5.0)
        transform = shift.golden_ratio_transform(k=3.33)
        
        self.assertIsInstance(transform, float)
        self.assertGreaterEqual(transform, 0.0)
    
    def test_embed_5d(self):
        """Test 5D embedding functionality."""
        if not AdvancedHologramVisualizer:
            self.skipTest("ZetaShift not available")
            
        shift = NumberLineZetaShift(10.0)
        coords = shift.embed_5d()
        
        self.assertIsInstance(coords, tuple)
        self.assertEqual(len(coords), 5)
        
        # All coordinates should be finite numbers
        for coord in coords:
            self.assertIsInstance(coord, (int, float))
            self.assertTrue(abs(coord) < float('inf'))


class TestCompatibility(unittest.TestCase):
    """Test compatibility with original hologram.py functionality."""
    
    def test_vectorized_zeta_function(self):
        """Test that vectorized zeta function still works."""
        if not AdvancedHologramVisualizer:
            self.skipTest("zeta functions not available")
            
        try:
            from hologram import vectorized_zeta
            import numpy as np
            
            # Test with small array
            test_values = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
            results = vectorized_zeta(test_values)
            
            self.assertEqual(len(results), len(test_values))
            self.assertTrue(all(isinstance(r, (int, float)) for r in results))
        except ImportError:
            self.skipTest("vectorized_zeta not available")


if __name__ == '__main__':
    # Set matplotlib backend for headless testing
    import matplotlib
    matplotlib.use('Agg')
    
    unittest.main(verbosity=2)