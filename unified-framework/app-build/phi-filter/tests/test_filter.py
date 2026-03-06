import sys
import os
import unittest

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from core.filter import GeometricTradingFilter
from core.models import FilterConfig

class TestGeometricTradingFilter(unittest.TestCase):
    def setUp(self):
        self.filter = GeometricTradingFilter()

    def test_filter_signal_pass(self):
        # Price 100, Support 95, Resistance 105, ATR 2.0
        # Midpoint = 100, Band = 2.0 * 2.0 = 4.0
        # Bounds = [96, 104]
        # 100 is within bounds
        result = self.filter.filter_signal(100.0, 95.0, 105.0, 2.0)
        self.assertTrue(result.passed)
        self.assertEqual(result.confidence, 1.0)

    def test_filter_signal_reject_low(self):
        # Bounds = [96, 104]
        # 95 is outside
        result = self.filter.filter_signal(95.0, 95.0, 105.0, 2.0)
        self.assertFalse(result.passed)
        self.assertEqual(result.rejection_reason, "price_too_low")

    def test_filter_signal_reject_high(self):
        # Bounds = [96, 104]
        # 105 is outside
        result = self.filter.filter_signal(105.0, 95.0, 105.0, 2.0)
        self.assertFalse(result.passed)
        self.assertEqual(result.rejection_reason, "price_too_high")

    def test_fibonacci_filtering(self):
        # Price range 90-110, ATR 2.5
        # Midpoint 100, Band 5.0 -> [95, 105]
        # Fib levels: 90, 94.72, 97.64, 100.0, 102.36, 105.72, 110.0 ...
        # Should only pass levels between 95 and 105
        valid_levels = self.filter.filter_fibonacci_levels(110.0, 90.0, 100.0, 2.5)
        
        # 38.2% = 97.64 (pass)
        # 50.0% = 100.0 (pass)
        # 61.8% = 102.36 (pass)
        self.assertIn('38.2%', valid_levels)
        self.assertIn('50.0%', valid_levels)
        self.assertIn('61.8%', valid_levels)
        
        # 0.0% = 90.0 (reject)
        # 23.6% = 94.72 (reject)
        self.assertNotIn('0.0%', valid_levels)
        self.assertNotIn('23.6%', valid_levels)

if __name__ == '__main__':
    unittest.main()
