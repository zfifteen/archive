import numpy as np
import time
from typing import List, Dict, Tuple, Optional
from .models import FilterConfig, SignalResult

PHI = (1 + np.sqrt(5)) / 2  # Golden ratio
LOG_PHI = np.log(PHI)

class GeometricTradingFilter:
    """
    Main geometric filter class for trading signals
    """
    
    def __init__(self, config: FilterConfig = None):
        self.config = config or FilterConfig()
        
        # Telemetry
        self.stats = {
            'total_signals': 0,
            'accepted_signals': 0,
            'rejected_signals': 0,
            'rejection_reasons': {},
            'avg_filter_time_ns': 0,
            'filter_times': []
        }
        
    def filter_signal(self, price: float, support: float, resistance: float, 
                     atr: float) -> SignalResult:
        """
        Core geometric filter - sub-microsecond execution
        """
        start_ns = time.perf_counter_ns()
        self.stats['total_signals'] += 1
        
        # Geometric constraint: price must be within volatility bands
        mid_point = 0.5 * (support + resistance)
        band_width = self.config.band_multiplier * atr
        
        lower_bound = mid_point - band_width
        upper_bound = mid_point + band_width
        
        # Filter decision
        if price < lower_bound:
            reason = "price_too_low"
            passed = False
            confidence = 0.0
        elif price > upper_bound:
            reason = "price_too_high"
            passed = False
            confidence = 0.0
        else:
            reason = None
            passed = True
            # Confidence based on distance from center
            distance_from_center = abs(price - mid_point)
            confidence = 1.0 - (distance_from_center / band_width) if band_width > 0 else 1.0
        
        # Update stats
        elapsed_ns = time.perf_counter_ns() - start_ns
        self._update_stats(passed, reason, elapsed_ns)
        
        return SignalResult(
            passed=passed,
            rejection_reason=reason,
            confidence=confidence,
            filter_time_ns=elapsed_ns
        )

    def filter_batch(self, prices: np.ndarray, supports: np.ndarray, 
                     resistances: np.ndarray, atrs: np.ndarray) -> List[SignalResult]:
        """
        Vectorized batch filtering for high-performance scanning.
        """
        start_ns = time.perf_counter_ns()
        n = len(prices)
        if n == 0:
            return []
            
        self.stats['total_signals'] += n
        
        mid_points = 0.5 * (supports + resistances)
        band_widths = self.config.band_multiplier * atrs
        
        lower_bounds = mid_points - band_widths
        upper_bounds = mid_points + band_widths
        
        passed_mask = (prices >= lower_bounds) & (prices <= upper_bounds)
        
        # Reasons (using object array for mixed types/None)
        reasons = np.full(n, None, dtype=object)
        reasons[prices < lower_bounds] = "price_too_low"
        reasons[prices > upper_bounds] = "price_too_high"
        
        # Confidence calculation (vectorized)
        # Avoid division by zero
        safe_band_widths = np.where(band_widths > 0, band_widths, 1e-9)
        confidences = 1.0 - (np.abs(prices - mid_points) / safe_band_widths)
        confidences = np.where(band_widths > 0, confidences, 1.0)
        # Clamp confidence and set to 0.0 if not passed
        confidences = np.clip(confidences, 0.0, 1.0)
        confidences[~passed_mask] = 0.0
        
        total_elapsed_ns = time.perf_counter_ns() - start_ns
        avg_elapsed_ns = total_elapsed_ns // n
        
        results = []
        for i in range(n):
            passed = bool(passed_mask[i])
            reason = reasons[i]
            conf = float(confidences[i])
            
            results.append(SignalResult(
                passed=passed,
                rejection_reason=reason,
                confidence=conf,
                filter_time_ns=avg_elapsed_ns
            ))
            
            # Efficiently update internal stats counters
            if passed:
                self.stats['accepted_signals'] += 1
            else:
                self.stats['rejected_signals'] += 1
                if reason:
                    self.stats['rejection_reasons'][reason] = \
                        self.stats['rejection_reasons'].get(reason, 0) + 1

        # Batch update timing stats
        # We add the avg time n times to maintain history consistency
        new_times = [avg_elapsed_ns] * min(n, 1000)
        self.stats['filter_times'].extend(new_times)
        if len(self.stats['filter_times']) > 1000:
            self.stats['filter_times'] = self.stats['filter_times'][-1000:]
            
        if self.stats['filter_times']:
            self.stats['avg_filter_time_ns'] = np.mean(self.stats['filter_times'])
            
        return results

    def generate_harmonic_lattice(self, base_price: float) -> Dict[int, float]:
        """
        Generate a harmonic lattice around a base price (e.g., sqrt(high*low)).
        Lattice = base_price * ratio^k
        """
        ratio = self.config.harmonic_ratio
        k_min = self.config.lattice_k_min
        k_max = self.config.lattice_k_max
        
        lattice = {}
        for k in range(k_min, k_max + 1):
            lattice[k] = base_price * (ratio ** k)
            
        return lattice

    def filter_harmonic_levels(self, base_price: float, atr: float) -> Dict[int, Dict]:
        """
        Generate and filter harmonic levels for geometric feasibility.
        Centered on base_price using ATR-based volatility bands.
        """
        lattice = self.generate_harmonic_lattice(base_price)
        
        valid_levels = {}
        for k, price in lattice.items():
            # Passing base_price as both support and resistance ensures 
            # the filter is centered exactly on the base_price.
            result = self.filter_signal(price, base_price, base_price, atr)
            if result.passed:
                valid_levels[k] = {
                    'price': price,
                    'confidence': result.confidence
                }
        return valid_levels
    
    def filter_fibonacci_levels(self, high: float, low: float, current_price: float,
                                atr: float) -> Dict[str, Dict]:
        """
        Filter Fibonacci retracement levels using custom harmonic ratio if specified.
        """
        price_range = high - low
        
        # Standard Fibonacci ratios + optional custom ratio
        fib_ratios = {
            '0.0%': 0.000,
            '23.6%': 0.236,
            '38.2%': 0.382,
            '50.0%': 0.500,
            '61.8%': 0.618,
            '78.6%': 0.786,
            '100.0%': 1.000,
        }
        
        # Add custom harmonic ratio if it's not PHI (which is 61.8% related)
        if abs(self.config.harmonic_ratio - PHI) > 0.001:
            fib_ratios[f'Custom({self.config.harmonic_ratio:.3f})'] = self.config.harmonic_ratio - 1.0
        
        # Add explicitly defined custom ratios
        if self.config.custom_ratios:
            for i, r in enumerate(self.config.custom_ratios):
                fib_ratios[f'Custom_{i}'] = r

        valid_levels = {}
        
        for name, ratio in fib_ratios.items():
            level = low + price_range * ratio
            result = self.filter_signal(level, low, high, atr)
            
            if result.passed:
                valid_levels[name] = {
                    'price': level,
                    'confidence': result.confidence
                }
        
        return valid_levels
    
    def filter_support_resistance(self, levels: List[float], current_price: float,
                                  volatility: float, timeframe_hours: int) -> List[float]:
        """
        Filter support/resistance levels by geometric reachability
        """
        # Time-scaled expected move
        expected_move = volatility * np.sqrt(timeframe_hours / 24)
        
        # 3-sigma bounds (99.7% confidence)
        lower_reach = current_price * np.exp(-3 * expected_move)
        upper_reach = current_price * np.exp(3 * expected_move)
        
        valid_levels = []
        
        for level in levels:
            if lower_reach <= level <= upper_reach:
                valid_levels.append(level)
            else:
                self.stats['total_signals'] += 1
                self.stats['rejected_signals'] += 1
        
        return valid_levels
    
    def filter_breakout(self, breakout_price: float, consolidation_range: Tuple[float, float],
                       volume_ratio: float, atr: float) -> Tuple[bool, float]:
        """
        Validate breakout using geometric and volume constraints
        """
        low, high = consolidation_range
        range_size = high - low
        
        # Geometric constraint 1: Breakout must be significant
        breakout_size = abs(breakout_price - high) if breakout_price > high else abs(low - breakout_price)
        min_breakout = 0.5 * atr
        
        if breakout_size < min_breakout:
            return False, 0.0
        
        # Geometric constraint 2: Volume must confirm (φ-harmonic ratio)
        min_volume_ratio = PHI  # 1.618× average
        
        if volume_ratio < min_volume_ratio:
            return False, 0.0
        
        # Geometric constraint 3: Range must be reasonable
        expected_range = 2 * atr
        range_ratio = range_size / expected_range if expected_range > 0 else 1.0
        
        if range_ratio < 0.5 or range_ratio > 2.0:
            return False, 0.0
        
        # Calculate confidence
        volume_score = min(volume_ratio / (PHI * 2), 1.0)
        size_score = min(breakout_size / atr, 1.0) if atr > 0 else 1.0
        range_score = 1.0 - abs(range_ratio - 1.0)
        
        confidence = (volume_score + size_score + range_score) / 3
        
        return True, confidence
    
    def _update_stats(self, passed: bool, reason: Optional[str], elapsed_ns: int):
        """Update internal statistics"""
        if passed:
            self.stats['accepted_signals'] += 1
        else:
            self.stats['rejected_signals'] += 1
            if reason:
                self.stats['rejection_reasons'][reason] = \
                    self.stats['rejection_reasons'].get(reason, 0) + 1
        
        # Update timing stats
        self.stats['filter_times'].append(elapsed_ns)
        if len(self.stats['filter_times']) > 1000:
            self.stats['filter_times'] = self.stats['filter_times'][-1000:]
        
        if self.stats['filter_times']:
            self.stats['avg_filter_time_ns'] = np.mean(self.stats['filter_times'])
    
    def get_rejection_rate(self) -> float:
        """Calculate current rejection rate"""
        total = self.stats['total_signals']
        if total == 0:
            return 0.0
        return self.stats['rejected_signals'] / total
    
    def report(self) -> Dict:
        """Generate performance report"""
        total = self.stats['total_signals']
        if total == 0:
            return {'error': 'No signals processed'}
        
        rejection_rate = self.get_rejection_rate()
        
        return {
            'total_signals': total,
            'accepted_signals': self.stats['accepted_signals'],
            'rejected_signals': self.stats['rejected_signals'],
            'rejection_rate': rejection_rate,
            'acceptance_rate': 1 - rejection_rate,
            'avg_filter_time_ns': self.stats['avg_filter_time_ns'],
            'avg_filter_time_us': self.stats['avg_filter_time_ns'] / 1000,
            'rejection_reasons': self.stats['rejection_reasons']
        }
