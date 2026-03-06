import unittest
import numpy as np
from src.core.backtester import HistoricalBacktester
from src.core.filter import GeometricTradingFilter

class TestBacktester(unittest.TestCase):
    def setUp(self):
        self.trading_filter = GeometricTradingFilter()
        self.backtester = HistoricalBacktester(self.trading_filter)

    def test_scan_custom_signals(self):
        # Create dummy data: 10 steps
        # Steps 0, 5, 9 will pass (price=100)
        # Others (price=120) will fail since band is [90, 110]
        prices = np.array([100.0, 120.0, 120.0, 120.0, 120.0, 100.0, 120.0, 120.0, 120.0, 100.0])
        supports = np.ones(10) * 95.0
        resistances = np.ones(10) * 105.0
        atrs = np.ones(10) * 5.0
        
        results = self.backtester.scan_custom_signals(prices, supports, resistances, atrs)
        
        self.assertEqual(results["total_intervals"], 10)
        self.assertEqual(results["valid_signals_found"], 3)
        self.assertAlmostEqual(results["rejection_rate"], 0.7)
        
        found_indices = [s["index"] for s in results["signals"]]
        self.assertEqual(found_indices, [0, 5, 9])

    def test_scan_fibonacci_signals(self):
        # High=110, Low=90, ATR=2.5
        # Range=20
        # Levels:
        # 0.236 -> 90 + 20*0.236 = 94.72
        # 0.382 -> 90 + 20*0.382 = 97.64
        # 0.500 -> 90 + 20*0.500 = 100.0
        # 0.618 -> 90 + 20*0.618 = 102.36
        # 0.786 -> 90 + 20*0.786 = 105.72
        
        # All these levels are within the band (100 +/- 2*2.5 = [95, 105]) EXCEPT 0.236 and 0.786
        # 94.72 is just outside 95
        # 105.72 is just outside 105
        
        # So valid ratios are 0.382, 0.500, 0.618
        
        n = 5
        highs = np.ones(n) * 110.0
        lows = np.ones(n) * 90.0
        atrs = np.ones(n) * 2.5
        
        # Prices that match levels
        prices = np.array([
            97.64,  # Matches 0.382
            100.0,  # Matches 0.500
            102.36, # Matches 0.618
            94.72,  # Matches 0.236 (but should be filtered out as infeasible)
            105.72  # Matches 0.786 (but should be filtered out as infeasible)
        ])
        
        results = self.backtester.scan_fibonacci_signals(highs, lows, prices, atrs)
        
        # total_signals_checked = 5 * 5 = 25
        self.assertEqual(results["total_intervals"], 5)
        # Only 3 signals should be found (indices 0, 1, 2)
        self.assertEqual(results["valid_signals_found"], 3)
        
        found_indices = [s["index"] for s in results["signals"]]
        self.assertEqual(found_indices, [0, 1, 2])

if __name__ == "__main__":
    unittest.main()
