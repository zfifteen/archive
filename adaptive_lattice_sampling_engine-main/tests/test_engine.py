import unittest
import numpy as np
from adaptive_lattice_sampling import Engine

class TestEngine(unittest.TestCase):
    def test_sample_shape(self):
        """Test that sample returns correct shape."""
        engine = Engine(dimensions=2, num_points=10)
        samples = engine.sample()
        self.assertEqual(samples.shape, (10, 2))

    def test_sample_range(self):
        """Test that samples are in [0,1)."""
        engine = Engine(dimensions=3, num_points=5, seed=42)
        samples = engine.sample()
        self.assertTrue(np.all(samples >= 0))
        self.assertTrue(np.all(samples < 1))

    def test_adaptive_sample(self):
        """Test adaptive sample method."""
        engine = Engine(dimensions=2, num_points=10)
        samples = engine.adaptive_sample(lambda x: np.sum(x**2))
        self.assertEqual(samples.shape, (10, 2))  # Currently just returns basic sample

if __name__ == '__main__':
    unittest.main()