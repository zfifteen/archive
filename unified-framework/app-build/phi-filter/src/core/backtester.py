import numpy as np
from typing import List, Dict, Any, Optional
from .filter import GeometricTradingFilter
from .models import FilterConfig, SignalResult

class HistoricalBacktester:
    """
    Service for running geometric validity scanning over historical price data.
    """
    
    def __init__(self, filter_instance: Optional[GeometricTradingFilter] = None):
        self.filter = filter_instance or GeometricTradingFilter()

    def scan_fibonacci_signals(self, 
                               highs: np.ndarray, 
                               lows: np.ndarray, 
                               prices: np.ndarray, 
                               atrs: np.ndarray) -> Dict[str, Any]:
        """
        Scan historical data for valid Fibonacci retracement signals.
        
        A signal is 'valid' if the price at time T is within a 
        geometrically feasible Fibonacci level relative to the 
        high/low swing and ATR at time T.
        """
        n = len(prices)
        if not (n == len(highs) == len(lows) == len(atrs)):
            raise ValueError("All input arrays must have the same length")

        results = []
        total_signals_checked = 0
        total_signals_passed = 0

        # Fibonacci ratios we care about
        ratios = [0.236, 0.382, 0.500, 0.618, 0.786]
        
        for i in range(n):
            h, l, p, a = highs[i], lows[i], prices[i], atrs[i]
            if a <= 0: continue
            
            price_range = h - l
            if price_range <= 0: continue
            
            # Check each ratio level
            for ratio in ratios:
                level_price = l + price_range * ratio
                total_signals_checked += 1
                
                # Use core filter for feasibility check
                # Note: We use h/l as the support/resistance for the band center
                res = self.filter.filter_signal(level_price, l, h, a)
                
                if res.passed:
                    # If the level is feasible, check if the actual price 'hit' it
                    # Within a small tolerance (e.g., 0.1% of price)
                    if abs(p - level_price) / p < 0.001:
                        total_signals_passed += 1
                        results.append({
                            "index": i,
                            "ratio": ratio,
                            "level_price": float(level_price),
                            "actual_price": float(p),
                            "confidence": float(res.confidence)
                        })
                        
        return {
            "total_intervals": n,
            "total_signals_checked": total_signals_checked,
            "valid_signals_found": total_signals_passed,
            "rejection_rate": 1.0 - (total_signals_passed / total_signals_checked) if total_signals_checked > 0 else 0.0,
            "signals": results
        }

    def scan_custom_signals(self, 
                            prices: np.ndarray, 
                            supports: np.ndarray, 
                            resistances: np.ndarray, 
                            atrs: np.ndarray) -> Dict[str, Any]:
        """
        Generic scanner for custom signals (price, support, resistance, atr).
        Useful for users who have their own S/R detection and just want the 
        geometric feasibility filter applied historically.
        """
        n = len(prices)
        if not (n == len(supports) == len(resistances) == len(atrs)):
            raise ValueError("All input arrays must have the same length")

        # Use the vectorized filter_batch for extreme speed
        filter_results = self.filter.filter_batch(prices, supports, resistances, atrs)
        
        passed_indices = [i for i, r in enumerate(filter_results) if r.passed]
        
        results = []
        for i in passed_indices:
            res = filter_results[i]
            results.append({
                "index": i,
                "price": float(prices[i]),
                "confidence": float(res.confidence)
            })
            
        total_passed = len(passed_indices)
        
        return {
            "total_intervals": n,
            "valid_signals_found": total_passed,
            "rejection_rate": 1.0 - (total_passed / n) if n > 0 else 0.0,
            "signals": results
        }
