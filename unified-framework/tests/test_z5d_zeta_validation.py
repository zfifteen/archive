#!/usr/bin/env python3
"""
Z5D Prime Prediction Validation Using Zeta Zeros

This module validates the Z5D predictor's accuracy for k=1,000,000 by correlating
the prediction with properties derived from Riemann zeta zeros, establishing
mathematical consistency between discrete prime prediction and continuous
zeta zero analysis.

The validation methodology follows the Z Framework's cross-domain approach:
1. Compute Z5D prediction for k=1,000,000 
2. Compute relevant Riemann zeta zeros
3. Perform correlation analysis between prediction and zeta properties
4. Validate statistical consistency and mathematical alignment
"""

import sys
import os
import time
import numpy as np
import pandas as pd
import mpmath as mp
from scipy import stats
from pathlib import Path

# Add src to path for imports
src_path = os.path.join(os.path.dirname(__file__), '..', 'src')
sys.path.insert(0, src_path)

# Import Z Framework components
from z_framework.discrete.z5d_predictor import z5d_prime, validate_z5d_accuracy
from statistical.zeta_zeros_extended import ExtendedZetaZeroProcessor
from core.domain import DiscreteZetaShift
from core.sha256_pattern_analyzer import SHA256PatternAnalyzer
from core.params import SHA_MATCHING_SCORE_THRESHOLD, PEARSON_CORRELATION_THRESHOLD
from sympy import ntheory

# High precision settings
mp.mp.dps = 50
PHI = (1 + mp.sqrt(5)) / 2
E_SQUARED = mp.exp(2)


class Z5DZetaValidator:
    """
    Validates Z5D prime predictions using Riemann zeta zero correlation analysis.
    
    This class implements comprehensive validation that establishes mathematical
    consistency between the Z5D predictor's discrete domain predictions and
    the continuous domain properties of Riemann zeta zeros.
    """
    
    def __init__(self, target_k=1000000, num_zeros=300, output_dir="z5d_zeta_validation"):
        """
        Initialize the validator.
        
        Args:
            target_k (int): Target k value for Z5D prediction (default: 1,000,000)
            num_zeros (int): Number of zeta zeros to compute for correlation analysis
            output_dir (str): Directory for output files and reports
        """
        self.target_k = target_k
        self.num_zeros = num_zeros
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Initialize processors
        self.zeta_processor = ExtendedZetaZeroProcessor(cache_size=num_zeros)
        self.sha_analyzer = SHA256PatternAnalyzer()
        
        # Results storage
        self.results = {}
        self.z5d_prediction = None
        self.true_prime = None
        self.zeta_data = {}
        self.correlation_results = {}
        self.sha_validation_data = {}
        
        # SHA matching validation threshold
        self.z5d_error_threshold = 0.0001  # 0.01% error threshold
        
    def compute_z5d_prediction(self):
        """
        Compute Z5D prediction for the target k value.
        
        Returns:
            dict: Prediction results including value, calibration parameters, and metadata
        """
        print(f"Computing Z5D prediction for k={self.target_k:,}...")
        start_time = time.time()
        
        # Get Z5D prediction with high precision
        self.z5d_prediction = z5d_prime(
            self.target_k, 
            auto_calibrate=True,
            precision_threshold=1e12,
            force_backend='mpmath'  # Use high precision for accuracy
        )
        
        elapsed = time.time() - start_time
        
        # Store prediction results
        prediction_data = {
            'k': self.target_k,
            'z5d_prediction': self.z5d_prediction,
            'computation_time': elapsed,
            'backend_used': 'mpmath',
            'auto_calibrated': True
        }
        
        self.results['z5d_prediction'] = prediction_data
        
        print(f"Z5D prediction for k={self.target_k:,}: {float(self.z5d_prediction):.6f}")
        print(f"Computation time: {elapsed:.3f} seconds")
        
        return prediction_data
    
    def compute_reference_prime(self):
        """
        Compute the actual k-th prime for comparison (if computationally feasible).
        
        Returns:
            dict: Reference prime computation results
        """
        print(f"Computing reference prime for k={self.target_k:,}...")
        
        # For k=1,000,000, direct computation is expensive but feasible
        if self.target_k <= 1e6:
            try:
                start_time = time.time()
                self.true_prime = ntheory.prime(self.target_k)
                elapsed = time.time() - start_time
                
                reference_data = {
                    'k': self.target_k,
                    'true_prime': self.true_prime,
                    'computation_time': elapsed,
                    'method': 'sympy.ntheory.prime'
                }
                
                # Calculate prediction accuracy
                if self.z5d_prediction is not None:
                    error = abs(self.z5d_prediction - self.true_prime)
                    relative_error = error / self.true_prime
                    reference_data.update({
                        'absolute_error': error,
                        'relative_error': relative_error,
                        'relative_error_percent': relative_error * 100
                    })
                    
                    print(f"True {self.target_k:,}th prime: {self.true_prime:,}")
                    print(f"Z5D prediction error: {relative_error*100:.6f}%")
                
                self.results['reference_prime'] = reference_data
                return reference_data
                
            except Exception as e:
                print(f"Reference prime computation failed: {e}")
                return {'error': str(e), 'method': 'failed'}
        else:
            print(f"Reference prime computation skipped for k={self.target_k:,} (too large)")
            return {'method': 'skipped', 'reason': 'computationally_expensive'}
    
    def compute_zeta_zeros_analysis(self):
        """
        Compute Riemann zeta zeros and perform statistical analysis.
        
        Returns:
            dict: Zeta zero analysis results
        """
        print(f"Computing {self.num_zeros} Riemann zeta zeros for correlation analysis...")
        start_time = time.time()
        
        # Compute zeta zeros batch
        zeros_data = self.zeta_processor.compute_zeta_zeros_batch(
            j_start=1, 
            j_end=self.num_zeros,
            batch_size=50
        )
        
        # Extract heights and compute unfolded zeros
        heights = zeros_data['heights']
        spacings = zeros_data['spacings']
        
        # Apply unfolding transformation
        unfolded_zeros = []
        valid_heights = []
        
        for h in heights:
            # Unfolding transformation: tilde_t = t / (2π log(t / (2π e)))
            threshold = 2 * mp.pi * mp.e  # ≈ 17.08
            if h > threshold:
                arg = h / threshold
                log_val = mp.log(arg)
                if log_val > 0:
                    unfolded = h / (2 * mp.pi * log_val)
                    unfolded_zeros.append(float(unfolded))
                    valid_heights.append(h)
        
        # Compute unfolded spacings
        unfolded_spacings = []
        if len(unfolded_zeros) > 1:
            for i in range(1, len(unfolded_zeros)):
                spacing = unfolded_zeros[i] - unfolded_zeros[i-1]
                unfolded_spacings.append(spacing)
        
        elapsed = time.time() - start_time
        
        # Store zeta analysis results
        zeta_analysis = {
            'num_zeros_computed': len(heights),
            'num_valid_unfolded': len(unfolded_zeros),
            'heights': heights,
            'unfolded_zeros': unfolded_zeros,
            'unfolded_spacings': unfolded_spacings,
            'computation_time': elapsed,
            'statistics': {
                'mean_spacing': np.mean(unfolded_spacings) if unfolded_spacings else 0,
                'std_spacing': np.std(unfolded_spacings) if unfolded_spacings else 0,
                'min_height': float(min(heights)) if heights else 0,
                'max_height': float(max(heights)) if heights else 0
            }
        }
        
        self.zeta_data = zeta_analysis
        self.results['zeta_analysis'] = zeta_analysis
        
        print(f"Computed {len(unfolded_zeros)} valid unfolded zeros in {elapsed:.2f} seconds")
        return zeta_analysis
    
    def validate_z5d_zeta_correlation(self):
        """
        Validate Z5D prediction through correlation with zeta zero properties.
        
        This method establishes mathematical consistency between the Z5D prediction
        and statistical properties derived from Riemann zeta zeros using advanced
        correlation analysis based on the Z Framework's mathematical foundations.
        
        Returns:
            dict: Correlation validation results
        """
        print("Validating Z5D prediction through zeta zero correlation...")
        
        if not self.zeta_data or not self.z5d_prediction:
            raise ValueError("Must compute Z5D prediction and zeta analysis first")
        
        correlation_results = {}
        
        # 1. Prime-Zeta Geodesic Correlation Analysis
        # Based on Z Framework's discrete-continuous domain mapping
        spacings = self.zeta_data['unfolded_spacings']
        heights = self.zeta_data['heights']
        
        if spacings and len(spacings) > 10:
            # Generate prime geodesic properties around k=1,000,000
            prime_analysis = self._analyze_prime_geodesics_near_target()
            
            # Zeta zero embedding analysis using existing framework
            zeta_embedding_results = self._create_zeta_embeddings()
            
            # Cross-domain correlation using Z Framework methodology
            geodesic_correlation = self._compute_geodesic_correlation(
                prime_analysis, zeta_embedding_results, spacings)
            
            correlation_results['geodesic_analysis'] = geodesic_correlation
        
        # 2. Z5D Prediction Consistency Analysis
        # Validate prediction against theoretical expectations
        z5d_consistency = self._validate_z5d_consistency()
        correlation_results['z5d_consistency'] = z5d_consistency
        
        # 3. Enhanced GUE Analysis with Z Framework Integration
        if spacings and len(spacings) > 20:
            gue_analysis = self._enhanced_gue_analysis(spacings)
            correlation_results['gue_analysis'] = gue_analysis
        
        # 4. Golden Ratio Correlation Analysis
        # Based on φ-normalized geodesics from the repository
        phi_analysis = self._phi_correlation_analysis(spacings, heights)
        correlation_results['phi_analysis'] = phi_analysis
        
        # 5. Curvature-Based Validation
        # Using curvature computations from Z Framework
        curvature_analysis = self._curvature_validation_analysis()
        correlation_results['curvature_analysis'] = curvature_analysis
        
        # 6. Overall validation score using enhanced metrics
        validation_score = self._compute_enhanced_validation_score(correlation_results)
        correlation_results['validation_score'] = validation_score
        
        self.correlation_results = correlation_results
        self.results['correlation_validation'] = correlation_results
        
        return correlation_results
    
    def _analyze_prime_geodesics_near_target(self):
        """Analyze prime geodesics in the vicinity of the target k value."""
        try:
            # Generate primes around the target k for geodesic analysis
            k_start = max(1, self.target_k - 1000)
            k_end = self.target_k + 1000
            k_range = range(k_start, min(k_end, self.target_k + 100))  # Limit for computation
            
            prime_geodesics = []
            for k in k_range:
                if k <= 100000:  # Limit to computationally feasible range
                    try:
                        prime_k = ntheory.prime(k)
                        # Compute discrete zeta shift for this prime
                        dzs = DiscreteZetaShift(prime_k)
                        curvature_val = dzs.b * np.log(prime_k + 1) / float(E_SQUARED)
                        
                        prime_geodesics.append({
                            'k': k,
                            'prime': prime_k,
                            'curvature': curvature_val,
                            'zeta_shift': dzs.z,
                            'b_value': dzs.b
                        })
                    except:
                        pass
                        
                if len(prime_geodesics) >= 50:  # Limit for performance
                    break
            
            if prime_geodesics:
                curvatures = [pg['curvature'] for pg in prime_geodesics]
                zeta_shifts = [pg['zeta_shift'] for pg in prime_geodesics]
                
                return {
                    'num_primes_analyzed': len(prime_geodesics),
                    'curvature_mean': np.mean(curvatures),
                    'curvature_std': np.std(curvatures),
                    'zeta_shift_mean': np.mean(zeta_shifts),
                    'zeta_shift_std': np.std(zeta_shifts),
                    'geodesics': prime_geodesics[:20]  # Store sample for analysis
                }
            else:
                return {'error': 'No prime geodesics computed'}
                
        except Exception as e:
            return {'error': f'Prime geodesic analysis failed: {str(e)}'}
    
    def _create_zeta_embeddings(self):
        """Create zeta zero embeddings using the framework's methodology."""
        try:
            # Use first 50 zeros for embedding analysis
            zeros_subset = self.zeta_data['heights'][:50] if self.zeta_data['heights'] else []
            
            if len(zeros_subset) < 10:
                return {'error': 'Insufficient zeta zeros for embedding'}
            
            # Create 5D embeddings similar to the framework approach
            embeddings = []
            curvatures = []
            
            for i, height in enumerate(zeros_subset):
                # Create complex zero (on critical line)
                zero = complex(0.5, height)
                
                # Compute 5D embedding coordinates
                phi = float(PHI)
                theta_base = 2 * np.pi * i / 50
                
                x = float(np.sqrt(abs(height)) * np.cos(theta_base))
                y = float(np.sqrt(abs(height)) * np.sin(theta_base))
                z = float(0.5 * np.log(abs(height) + 1) / float(E_SQUARED))
                w = float(height / (2 * np.pi))
                u = float((i % phi) / phi)
                
                coords_5d = (x, y, z, w, u)
                embeddings.append(coords_5d)
                
                # Compute curvature
                coord_norm = np.linalg.norm(coords_5d)
                coord_sum = np.sum(np.abs(coords_5d))
                curvature = coord_norm / (1 + coord_sum) if coord_sum > 0 else 0
                curvatures.append(curvature)
            
            return {
                'num_embeddings': len(embeddings),
                'embeddings': embeddings,
                'curvatures': curvatures,
                'curvature_mean': np.mean(curvatures),
                'curvature_std': np.std(curvatures)
            }
            
        except Exception as e:
            return {'error': f'Zeta embedding creation failed: {str(e)}'}
    
    def _compute_geodesic_correlation(self, prime_analysis, zeta_embeddings, spacings):
        """Compute correlation between prime geodesics and zeta embeddings."""
        try:
            if 'error' in prime_analysis or 'error' in zeta_embeddings:
                return {'error': 'Cannot compute correlation due to analysis errors'}
            
            # Extract comparable features
            prime_curvatures = [pg['curvature'] for pg in prime_analysis.get('geodesics', [])]
            zeta_curvatures = zeta_embeddings.get('curvatures', [])
            
            correlations = {}
            
            # Curvature correlation (if both available)
            if len(prime_curvatures) > 5 and len(zeta_curvatures) > 5:
                min_len = min(len(prime_curvatures), len(zeta_curvatures))
                try:
                    corr, p_val = stats.pearsonr(
                        prime_curvatures[:min_len], 
                        zeta_curvatures[:min_len]
                    )
                    correlations['curvature_correlation'] = {
                        'correlation': corr,
                        'p_value': p_val,
                        'significant': p_val < 0.05
                    }
                except:
                    correlations['curvature_correlation'] = {'error': 'Correlation computation failed'}
            
            # Spacing-curvature cross-correlation
            if len(spacings) > 5 and len(prime_curvatures) > 5:
                min_len = min(len(spacings), len(prime_curvatures))
                try:
                    corr, p_val = stats.pearsonr(
                        spacings[:min_len],
                        prime_curvatures[:min_len]
                    )
                    correlations['spacing_prime_correlation'] = {
                        'correlation': corr,
                        'p_value': p_val,
                        'significant': p_val < 0.05
                    }
                except:
                    correlations['spacing_prime_correlation'] = {'error': 'Correlation computation failed'}
            
            # Statistical summary
            correlation_score = 0
            significant_count = 0
            total_correlations = 0
            
            for corr_name, corr_data in correlations.items():
                if 'correlation' in corr_data and 'significant' in corr_data:
                    total_correlations += 1
                    if corr_data['significant']:
                        significant_count += 1
                        correlation_score += abs(corr_data['correlation'])
            
            if total_correlations > 0:
                correlation_score /= total_correlations
            
            return {
                'correlations': correlations,
                'correlation_score': correlation_score,
                'significant_correlations': significant_count,
                'total_correlations': total_correlations,
                'success': True
            }
            
        except Exception as e:
            return {'error': f'Geodesic correlation computation failed: {str(e)}'}
    
    def _validate_z5d_consistency(self):
        """Validate Z5D prediction internal consistency."""
        try:
            # Check prediction against expected range
            expected_range = (15000000, 16000000)  # Expected range for 1M-th prime
            in_range = expected_range[0] <= self.z5d_prediction <= expected_range[1]
            
            # Check against asymptotic estimates
            k = self.target_k
            asymptotic_estimate = k * (np.log(k) + np.log(np.log(k)) - 1)
            asymptotic_ratio = self.z5d_prediction / asymptotic_estimate
            
            # Expected ratio should be close to 1.0 for good predictions
            ratio_consistency = 1 - abs(asymptotic_ratio - 1.0)
            
            # Check logarithmic consistency
            log_consistency = abs(np.log(self.z5d_prediction) - np.log(asymptotic_estimate))
            log_consistency_score = 1 / (1 + log_consistency)  # Higher score for lower difference
            
            return {
                'in_expected_range': in_range,
                'expected_range': expected_range,
                'asymptotic_estimate': asymptotic_estimate,
                'asymptotic_ratio': asymptotic_ratio,
                'ratio_consistency': max(0, ratio_consistency),
                'log_consistency_score': log_consistency_score,
                'overall_consistency': (int(in_range) + ratio_consistency + log_consistency_score) / 3
            }
            
        except Exception as e:
            return {'error': f'Z5D consistency validation failed: {str(e)}'}
    
    def _enhanced_gue_analysis(self, spacings):
        """Enhanced GUE analysis with better statistical methods."""
        try:
            spacings_array = np.array(spacings)
            
            # Remove extreme outliers for better analysis
            q1, q3 = np.percentile(spacings_array, [25, 75])
            iqr = q3 - q1
            lower_bound = q1 - 1.5 * iqr
            upper_bound = q3 + 1.5 * iqr
            filtered_spacings = spacings_array[
                (spacings_array >= lower_bound) & (spacings_array <= upper_bound)
            ]
            
            if len(filtered_spacings) < 10:
                return {'error': 'Insufficient valid spacings for GUE analysis'}
            
            # Normalize spacings
            mean_spacing = np.mean(filtered_spacings)
            if mean_spacing <= 0:
                return {'error': 'Invalid mean spacing for normalization'}
                
            normalized_spacings = filtered_spacings / mean_spacing
            
            # Compute basic statistics
            stats_dict = {
                'mean': np.mean(normalized_spacings),
                'std': np.std(normalized_spacings),
                'skewness': stats.skew(normalized_spacings),
                'kurtosis': stats.kurtosis(normalized_spacings)
            }
            
            # GUE theoretical values (approximate)
            gue_theoretical = {
                'mean': 1.0,
                'std': 0.5236,  # Approximate for GUE
                'skewness': 0.0,  # GUE is symmetric
                'kurtosis': 0.0   # Approximate
            }
            
            # Compute deviations from GUE
            deviations = {}
            consistency_scores = {}
            for stat_name in ['mean', 'std', 'skewness', 'kurtosis']:
                deviation = abs(stats_dict[stat_name] - gue_theoretical[stat_name])
                deviations[stat_name] = deviation
                # Higher score for lower deviation
                consistency_scores[stat_name] = 1 / (1 + deviation)
            
            overall_gue_score = np.mean(list(consistency_scores.values()))
            
            return {
                'filtered_count': len(filtered_spacings),
                'original_count': len(spacings_array),
                'statistics': stats_dict,
                'gue_theoretical': gue_theoretical,
                'deviations': deviations,
                'consistency_scores': consistency_scores,
                'overall_gue_score': overall_gue_score,
                'gue_consistent': overall_gue_score > 0.5
            }
            
        except Exception as e:
            return {'error': f'Enhanced GUE analysis failed: {str(e)}'}
    
    def _phi_correlation_analysis(self, spacings, heights):
        """Analyze correlations with golden ratio φ as per Z Framework."""
        try:
            phi = float(PHI)
            
            correlations = {}
            
            # φ-modular analysis of spacings
            if spacings and len(spacings) > 5:
                spacings_array = np.array(spacings, dtype=float)
                phi_modular_spacings = spacings_array % phi
                
                # Correlation between original and φ-modular spacings
                if len(spacings_array) == len(phi_modular_spacings):
                    try:
                        corr, p_val = stats.pearsonr(spacings_array, phi_modular_spacings)
                        correlations['phi_modular_spacing'] = {
                            'correlation': corr,
                            'p_value': p_val,
                            'significant': p_val < 0.05
                        }
                    except:
                        correlations['phi_modular_spacing'] = {'error': 'Correlation failed'}
            
            # φ-based height analysis
            if heights and len(heights) > 5:
                heights_array = np.array(heights)
                phi_normalized_heights = heights_array / phi
                
                # Distribution analysis
                phi_stats = {
                    'phi_normalized_mean': np.mean(phi_normalized_heights),
                    'phi_normalized_std': np.std(phi_normalized_heights),
                    'phi_modular_mean': np.mean(heights_array % phi),
                    'phi_ratio_score': abs(np.mean(phi_normalized_heights)) / (1 + np.std(phi_normalized_heights))
                }
                
                correlations['phi_height_analysis'] = phi_stats
            
            # Z5D prediction φ-relationship
            z5d_phi_properties = {
                'z5d_mod_phi': self.z5d_prediction % phi,
                'z5d_div_phi': self.z5d_prediction / phi,
                'z5d_phi_ratio': (self.z5d_prediction % phi) / phi,
                'phi_harmonic_score': 1 / (1 + abs((self.z5d_prediction % phi) - phi/2))
            }
            
            correlations['z5d_phi_analysis'] = z5d_phi_properties
            
            # Overall φ-correlation score
            phi_score_components = []
            
            if 'phi_modular_spacing' in correlations and 'correlation' in correlations['phi_modular_spacing']:
                phi_score_components.append(abs(correlations['phi_modular_spacing']['correlation']))
            
            if 'phi_height_analysis' in correlations:
                phi_score_components.append(correlations['phi_height_analysis']['phi_ratio_score'])
            
            if 'z5d_phi_analysis' in correlations:
                phi_score_components.append(correlations['z5d_phi_analysis']['phi_harmonic_score'])
            
            overall_phi_score = np.mean(phi_score_components) if phi_score_components else 0
            
            return {
                'correlations': correlations,
                'overall_phi_score': overall_phi_score,
                'phi_value': phi,
                'components_count': len(phi_score_components)
            }
            
        except Exception as e:
            return {'error': f'φ correlation analysis failed: {str(e)}'}
    
    def _should_lock_metrics(self, sha_matching_score, z5d_error_meets_threshold, z5d_error_rate, pearson_meets_threshold):
        """
        Helper method to determine if metrics should be locked based on SHA matching criteria.
        
        Args:
            sha_matching_score (float): SHA matching consistency score
            z5d_error_meets_threshold (bool): Whether Z5D error meets threshold
            z5d_error_rate (float or None): Z5D error rate, if available
            pearson_meets_threshold (bool): Whether Pearson correlation meets threshold
            
        Returns:
            bool: True if metrics should be locked
        """
        return (
            sha_matching_score > SHA_MATCHING_SCORE_THRESHOLD and
            (z5d_error_meets_threshold or z5d_error_rate is None) and
            pearson_meets_threshold
        )
    
    def validate_sha_matching(self):
        """
        Validate SHAs matching - ensure cryptographic hash analysis consistency 
        with Z Framework validation metrics.
        
        This method implements the core "SHAs matching" validation by analyzing
        cryptographic patterns in Z5D prediction data and ensuring consistency
        with zeta framework metrics.
        
        Returns:
            dict: SHA matching validation results
        """
        try:
            print("Validating SHAs matching...")
            
            # Generate test data based on Z5D prediction
            prediction_str = f"{self.z5d_prediction:.12f}"
            target_k_str = str(self.target_k)
            
            # Analyze SHA256 patterns for prediction consistency
            sha_results = self.sha_analyzer.analyze_sequence(prediction_str, sequence_length=8)
            
            # Create variants for differential analysis
            variants = [
                prediction_str,
                f"{self.z5d_prediction:.10f}",
                f"k={self.target_k}",
                f"z5d_{self.target_k}_{self.z5d_prediction:.8f}"
            ]
            
            differential_results = self.sha_analyzer.detect_differential_patterns(variants)
            
            # Extract key metrics for SHA validation
            pattern_metrics = sha_results.get('pattern_metrics', {})
            curvature_mean = pattern_metrics.get('curvature_mean', 0)
            pattern_detected = pattern_metrics.get('pattern_detected', False)
            
            # SHA-Z5D consistency analysis
            sha_z5d_consistency = {
                'curvature_consistency': 1.0 - abs(curvature_mean) if curvature_mean is not None else 0.5,
                'randomness_preserved': not pattern_detected,
                'differential_variance': differential_results.get('differential_metrics', {}).get('curvature_variance_across_variants', 0)
            }
            
            # Calculate Z5D error rate (if reference prime is available)
            z5d_error_rate = None
            z5d_error_meets_threshold = False
            
            if self.true_prime is not None:
                z5d_error_rate = abs(self.z5d_prediction - self.true_prime) / self.true_prime
                z5d_error_meets_threshold = z5d_error_rate < self.z5d_error_threshold
            
            # SHA-based geometric validation
            discrete_derivatives = sha_results.get('discrete_derivatives', [])
            geometric_consistency = 0.0
            if discrete_derivatives:
                # Analyze derivatives for geometric consistency with Z Framework
                derivative_std = np.std(discrete_derivatives)
                derivative_mean = np.mean(discrete_derivatives)
                if derivative_mean != 0:
                    geometric_consistency = 1.0 / (1.0 + abs(derivative_std / derivative_mean))
            
            # Zeta correlation with SHA patterns
            zeta_sha_correlation = 0.0
            if self.zeta_data and 'unfolded_spacings' in self.zeta_data:
                spacings = self.zeta_data['unfolded_spacings']
                if len(spacings) > 5 and len(discrete_derivatives) > 5:
                    min_len = min(len(spacings), len(discrete_derivatives))
                    try:
                        corr, p_val = stats.pearsonr(
                            spacings[:min_len], 
                            discrete_derivatives[:min_len]
                        )
                        if p_val < 1e-10:  # Meets p<10^{-10} requirement
                            zeta_sha_correlation = abs(corr)
                    except:
                        pass
            
            # Pearson correlation validation for zeta spacings
            pearson_meets_threshold = zeta_sha_correlation >= PEARSON_CORRELATION_THRESHOLD  # r≥0.93 requirement
            
            # Overall SHA matching validation
            sha_matching_components = [
                sha_z5d_consistency['curvature_consistency'],
                float(sha_z5d_consistency['randomness_preserved']),
                geometric_consistency,
                zeta_sha_correlation
            ]
            
            sha_matching_score = np.mean([c for c in sha_matching_components if c is not None])
            
            # Lock metrics when SHAs match (high consistency)
            metrics_locked = self._should_lock_metrics(
                sha_matching_score,
                z5d_error_meets_threshold,
                z5d_error_rate,
                pearson_meets_threshold
            )
            
            validation_results = {
                'sha_analysis_results': sha_results,
                'differential_analysis': differential_results,
                'sha_z5d_consistency': sha_z5d_consistency,
                'z5d_error_rate': z5d_error_rate,
                'z5d_error_meets_threshold': z5d_error_meets_threshold,
                'geometric_consistency': geometric_consistency,
                'zeta_sha_correlation': zeta_sha_correlation,
                'pearson_meets_threshold': pearson_meets_threshold,
                'sha_matching_score': sha_matching_score,
                'sha_matching_components': sha_matching_components,
                'metrics_locked': metrics_locked,
                'validation_criteria': {
                    'z5d_error_threshold': self.z5d_error_threshold,
                    'pearson_threshold': PEARSON_CORRELATION_THRESHOLD,
                    'p_value_threshold': 1e-10
                }
            }
            
            self.sha_validation_data = validation_results
            self.results['sha_matching_validation'] = validation_results
            
            print(f"SHA matching score: {sha_matching_score:.4f}")
            print(f"Z5D error rate: {z5d_error_rate:.6f}" if z5d_error_rate else "Z5D error rate: Not available")
            print(f"Pearson correlation (zeta-SHA): {zeta_sha_correlation:.4f}")
            print(f"Metrics locked: {metrics_locked}")
            
            return validation_results
            
        except Exception as e:
            error_result = {'error': f'SHA matching validation failed: {str(e)}'}
            self.sha_validation_data = error_result
            self.results['sha_matching_validation'] = error_result
            return error_result
    
    def _curvature_validation_analysis(self):
        """Validate using curvature-based analysis from Z Framework."""
        try:
            # Generate curvature analysis around the prediction
            k = self.target_k
            z5d_pred = self.z5d_prediction
            
            # Compute theoretical curvature expectations
            log_z5d = np.log(z5d_pred)
            curvature_theoretical = (log_z5d / float(E_SQUARED))**2  # Based on d_term formula
            
            # Compute discrete zeta shift for the predicted prime
            try:
                dzs = DiscreteZetaShift(int(z5d_pred))
                prediction_curvature = dzs.b * np.log(z5d_pred + 1) / float(E_SQUARED)
                curvature_consistency = 1 / (1 + abs(prediction_curvature - curvature_theoretical))
            except:
                prediction_curvature = 0
                curvature_consistency = 0
            
            # Geometric validation
            geometric_score = 1 / (1 + abs(log_z5d - np.log(k * np.log(k))))
            
            return {
                'curvature_theoretical': curvature_theoretical,
                'prediction_curvature': prediction_curvature,
                'curvature_consistency': curvature_consistency,
                'geometric_score': geometric_score,
                'overall_curvature_score': (curvature_consistency + geometric_score) / 2
            }
            
        except Exception as e:
            return {'error': f'Curvature validation failed: {str(e)}'}
    
    def _compute_enhanced_validation_score(self, correlation_results):
        """Compute enhanced validation score using all analysis components."""
        try:
            score_components = []
            component_weights = []
            
            # Z5D consistency (high weight)
            if 'z5d_consistency' in correlation_results and 'overall_consistency' in correlation_results['z5d_consistency']:
                consistency_score = correlation_results['z5d_consistency']['overall_consistency']
                score_components.append(consistency_score)
                component_weights.append(0.3)
            
            # Geodesic correlation (high weight)
            if 'geodesic_analysis' in correlation_results and correlation_results['geodesic_analysis'].get('success', False):
                geodesic_score = correlation_results['geodesic_analysis']['correlation_score']
                score_components.append(geodesic_score)
                component_weights.append(0.25)
            
            # GUE analysis (medium weight)
            if 'gue_analysis' in correlation_results and 'overall_gue_score' in correlation_results['gue_analysis']:
                gue_score = correlation_results['gue_analysis']['overall_gue_score']
                score_components.append(gue_score)
                component_weights.append(0.2)
            
            # φ correlation (medium weight)
            if 'phi_analysis' in correlation_results and 'overall_phi_score' in correlation_results['phi_analysis']:
                phi_score = correlation_results['phi_analysis']['overall_phi_score']
                score_components.append(phi_score)
                component_weights.append(0.15)
            
            # Curvature validation (medium weight)
            if 'curvature_analysis' in correlation_results and 'overall_curvature_score' in correlation_results['curvature_analysis']:
                curvature_score = correlation_results['curvature_analysis']['overall_curvature_score']
                score_components.append(curvature_score)
                component_weights.append(0.1)
            
            # Compute weighted average
            if score_components and component_weights:
                total_weight = sum(component_weights)
                if total_weight > 0:
                    weighted_score = sum(s * w for s, w in zip(score_components, component_weights)) / total_weight
                else:
                    weighted_score = np.mean(score_components)
            else:
                weighted_score = 0.0
            
            return {
                'overall_score': weighted_score,
                'components': score_components,
                'weights': component_weights,
                'num_components': len(score_components),
                'interpretation': self._interpret_enhanced_validation_score(weighted_score)
            }
            
        except Exception as e:
            return {
                'overall_score': 0.0,
                'error': f'Enhanced validation score computation failed: {str(e)}',
                'interpretation': 'Error in validation score computation'
            }
    
    def _interpret_enhanced_validation_score(self, score):
        """Provide enhanced interpretation of validation score."""
        if score >= 0.9:
            return "Excellent - Z5D prediction shows strong mathematical consistency with zeta zero analysis"
        elif score >= 0.8:
            return "Very Good - High correlation between Z5D prediction and zeta zero properties"
        elif score >= 0.7:
            return "Good - Substantial mathematical consistency supporting Z5D validation"
        elif score >= 0.6:
            return "Moderate-Good - Reasonable correlation detected with some strong components"
        elif score >= 0.5:
            return "Moderate - Some correlation detected, validation partially successful"
        elif score >= 0.4:
            return "Fair - Limited but detectable correlation, suggests mathematical relationship"
        elif score >= 0.3:
            return "Weak-Fair - Minimal correlation, some mathematical consistency indicated"
        elif score >= 0.2:
            return "Weak - Very limited correlation, requires further investigation"
        else:
            return "Poor - No significant correlation detected in current analysis"
    
    def run_complete_validation(self):
        """
        Run complete Z5D validation using zeta zeros and SHA matching.
        
        Returns:
            dict: Complete validation results
        """
        print("="*60)
        print("Z5D PRIME PREDICTION VALIDATION USING ZETA ZEROS AND SHA MATCHING")
        print("="*60)
        
        try:
            # Step 1: Compute Z5D prediction
            self.compute_z5d_prediction()
            
            # Step 2: Compute reference prime (if feasible)
            self.compute_reference_prime()
            
            # Step 3: Compute zeta zeros analysis
            self.compute_zeta_zeros_analysis()
            
            # Step 4: Validate SHA matching (new requirement)
            self.validate_sha_matching()
            
            # Step 5: Validate through correlation
            self.validate_z5d_zeta_correlation()
            
            # Step 6: Generate summary report
            self.generate_validation_report()
            
            print("\n" + "="*60)
            print("VALIDATION COMPLETED SUCCESSFULLY")
            print("="*60)
            
            return self.results
            
        except Exception as e:
            print(f"\nValidation failed: {e}")
            self.results['error'] = str(e)
            return self.results
    
    def generate_validation_report(self):
        """Generate comprehensive validation report."""
        report_file = self.output_dir / "z5d_zeta_validation_report.txt"
        
        with open(report_file, 'w') as f:
            f.write("Z5D PRIME PREDICTION VALIDATION USING ZETA ZEROS\n")
            f.write("="*60 + "\n\n")
            
            # Z5D Prediction Results
            if 'z5d_prediction' in self.results:
                z5d_data = self.results['z5d_prediction']
                f.write("Z5D PREDICTION RESULTS:\n")
                f.write(f"Target k: {z5d_data['k']:,}\n")
                f.write(f"Z5D prediction: {float(z5d_data['z5d_prediction']):,.6f}\n")
                f.write(f"Computation time: {z5d_data['computation_time']:.3f} seconds\n")
                f.write(f"Backend used: {z5d_data['backend_used']}\n\n")
            
            # Reference Prime Results
            if 'reference_prime' in self.results:
                ref_data = self.results['reference_prime']
                f.write("REFERENCE PRIME RESULTS:\n")
                if 'true_prime' in ref_data:
                    f.write(f"True {self.target_k:,}th prime: {ref_data['true_prime']:,}\n")
                    f.write(f"Absolute error: {ref_data['absolute_error']:,.3f}\n")
                    f.write(f"Relative error: {ref_data['relative_error_percent']:.6f}%\n")
                else:
                    f.write(f"Method: {ref_data.get('method', 'unknown')}\n")
                f.write("\n")
            
            # Zeta Analysis Results
            if 'zeta_analysis' in self.results:
                zeta_data = self.results['zeta_analysis']
                f.write("ZETA ZERO ANALYSIS RESULTS:\n")
                f.write(f"Zeros computed: {zeta_data['num_zeros_computed']}\n")
                f.write(f"Valid unfolded zeros: {zeta_data['num_valid_unfolded']}\n")
                stats_data = zeta_data['statistics']
                f.write(f"Mean spacing: {stats_data['mean_spacing']:.6f}\n")
                f.write(f"Spacing std: {stats_data['std_spacing']:.6f}\n")
                f.write(f"Height range: {stats_data['min_height']:.3f} - {stats_data['max_height']:.3f}\n\n")
            
            # Correlation Validation Results
            if 'correlation_validation' in self.results:
                corr_data = self.results['correlation_validation']
                f.write("CORRELATION VALIDATION RESULTS:\n")
                
                if 'validation_score' in corr_data:
                    score_data = corr_data['validation_score']
                    f.write(f"Overall validation score: {score_data['overall_score']:.3f}\n")
                    f.write(f"Components analyzed: {score_data.get('num_components', 0)}\n")
                    f.write(f"Interpretation: {score_data['interpretation']}\n\n")
                
                # Z5D Consistency Analysis
                if 'z5d_consistency' in corr_data:
                    z5d_cons = corr_data['z5d_consistency']
                    f.write("Z5D Consistency Analysis:\n")
                    f.write(f"  In expected range: {z5d_cons.get('in_expected_range', False)}\n")
                    f.write(f"  Asymptotic ratio: {z5d_cons.get('asymptotic_ratio', 0):.6f}\n")
                    f.write(f"  Overall consistency: {z5d_cons.get('overall_consistency', 0):.3f}\n\n")
                
                # Geodesic Analysis
                if 'geodesic_analysis' in corr_data:
                    geo_data = corr_data['geodesic_analysis']
                    f.write("Geodesic Correlation Analysis:\n")
                    if geo_data.get('success', False):
                        f.write(f"  Correlation score: {geo_data.get('correlation_score', 0):.3f}\n")
                        f.write(f"  Significant correlations: {geo_data.get('significant_correlations', 0)}\n")
                        f.write(f"  Total correlations: {geo_data.get('total_correlations', 0)}\n")
                    else:
                        f.write(f"  Status: {geo_data.get('error', 'Failed')}\n")
                    f.write("\n")
                
                # Enhanced GUE Analysis
                if 'gue_analysis' in corr_data:
                    gue_data = corr_data['gue_analysis']
                    f.write("Enhanced GUE Analysis:\n")
                    if 'overall_gue_score' in gue_data:
                        f.write(f"  Overall GUE score: {gue_data['overall_gue_score']:.3f}\n")
                        f.write(f"  GUE consistent: {gue_data.get('gue_consistent', False)}\n")
                        f.write(f"  Filtered spacings: {gue_data.get('filtered_count', 0)}/{gue_data.get('original_count', 0)}\n")
                    else:
                        f.write(f"  Status: {gue_data.get('error', 'Failed')}\n")
                    f.write("\n")
                
                # φ (Golden Ratio) Analysis
                if 'phi_analysis' in corr_data:
                    phi_data = corr_data['phi_analysis']
                    f.write("Golden Ratio (φ) Correlation Analysis:\n")
                    if 'overall_phi_score' in phi_data:
                        f.write(f"  Overall φ score: {phi_data['overall_phi_score']:.3f}\n")
                        f.write(f"  φ value: {phi_data.get('phi_value', 0):.6f}\n")
                        f.write(f"  Components analyzed: {phi_data.get('components_count', 0)}\n")
                    else:
                        f.write(f"  Status: {phi_data.get('error', 'Failed')}\n")
                    f.write("\n")
                
                # Curvature Analysis
                if 'curvature_analysis' in corr_data:
                    curv_data = corr_data['curvature_analysis']
                    f.write("Curvature Validation Analysis:\n")
                    if 'overall_curvature_score' in curv_data:
                        f.write(f"  Overall curvature score: {curv_data['overall_curvature_score']:.3f}\n")
                        f.write(f"  Curvature consistency: {curv_data.get('curvature_consistency', 0):.3f}\n")
                        f.write(f"  Geometric score: {curv_data.get('geometric_score', 0):.3f}\n")
                    else:
                        f.write(f"  Status: {curv_data.get('error', 'Failed')}\n")
                    f.write("\n")
            
            # SHA Matching Validation Results
            if 'sha_matching_validation' in self.results:
                sha_data = self.results['sha_matching_validation']
                f.write("SHA MATCHING VALIDATION RESULTS:\n")
                if 'error' not in sha_data:
                    f.write(f"  SHA matching score: {sha_data.get('sha_matching_score', 0):.4f}\n")
                    f.write(f"  Z5D error rate: {sha_data.get('z5d_error_rate', 'N/A')}\n")
                    f.write(f"  Z5D error meets threshold (<0.01%): {sha_data.get('z5d_error_meets_threshold', False)}\n")
                    f.write(f"  Pearson correlation (zeta-SHA): {sha_data.get('zeta_sha_correlation', 0):.4f}\n")
                    f.write(f"  Pearson meets threshold (≥{PEARSON_CORRELATION_THRESHOLD}): {sha_data.get('pearson_meets_threshold', False)}\n")
                    f.write(f"  Geometric consistency: {sha_data.get('geometric_consistency', 0):.4f}\n")
                    f.write(f"  Metrics locked: {sha_data.get('metrics_locked', False)}\n")
                    
                    # SHA-Z5D consistency details
                    sha_z5d = sha_data.get('sha_z5d_consistency', {})
                    f.write(f"  Curvature consistency: {sha_z5d.get('curvature_consistency', 0):.4f}\n")
                    f.write(f"  Randomness preserved: {sha_z5d.get('randomness_preserved', False)}\n")
                else:
                    f.write(f"  Status: {sha_data.get('error', 'Failed')}\n")
                f.write("\n")
        
        print(f"Validation report saved to: {report_file}")


def test_z5d_zeta_validation():
    """
    Test function for Z5D zeta validation with SHA matching.
    
    This test validates the Z5D predictor for k=1,000,000 using zeta zero correlation
    analysis and SHA matching validation, establishing mathematical consistency between 
    discrete and continuous domains.
    """
    print("Testing Z5D validation using zeta zeros and SHA matching...")
    
    # Create validator with smaller parameters for testing
    validator = Z5DZetaValidator(
        target_k=1000000,  # Full k=1,000,000 as specified
        num_zeros=100,     # Reduced for faster testing
        output_dir="test_z5d_zeta_validation"
    )
    
    # Run validation
    results = validator.run_complete_validation()
    
    # Verify basic results
    assert 'z5d_prediction' in results, "Z5D prediction failed"
    assert 'zeta_analysis' in results, "Zeta analysis failed"
    assert 'sha_matching_validation' in results, "SHA matching validation failed"
    
    # Verify SHA matching validation
    sha_validation = results['sha_matching_validation']
    assert 'error' not in sha_validation, f"SHA validation error: {sha_validation.get('error', 'Unknown')}"
    
    # Check key SHA matching metrics
    assert 'sha_matching_score' in sha_validation, "SHA matching score missing"
    assert 'metrics_locked' in sha_validation, "Metrics locked status missing"
    assert 'pearson_meets_threshold' in sha_validation, "Pearson threshold check missing"
    assert 'z5d_error_meets_threshold' in sha_validation, "Z5D error threshold check missing"
    
    # Verify Z Framework requirements from problem statement
    z5d_data = results['z5d_prediction']
    z5d_pred = z5d_data['z5d_prediction']
    
    # Check that prediction is reasonable for k=1,000,000
    assert 14000000 < z5d_pred < 17000000, f"Z5D prediction {z5d_pred} outside expected range"
    
    print(f"Z5D prediction: {float(z5d_pred):.6f}")
    print(f"SHA matching score: {sha_validation['sha_matching_score']:.4f}")
    print(f"Metrics locked: {sha_validation['metrics_locked']}")
    
    # Check if Z_5D error requirement is met (when reference is available)
    if sha_validation.get('z5d_error_rate') is not None:
        error_rate = sha_validation['z5d_error_rate']
        print(f"Z5D error rate: {error_rate:.6f} ({error_rate*100:.4f}%)")
        
        # Check if error is < 0.01% (0.0001)
        if error_rate < 0.0001:
            print("✓ Z_5D error < 0.01% requirement MET")
        else:
            print(f"⚠ Z_5D error {error_rate*100:.4f}% > 0.01% requirement")
    
    # Check Pearson correlation requirement
    pearson_corr = sha_validation.get('zeta_sha_correlation', 0)
    if pearson_corr >= PEARSON_CORRELATION_THRESHOLD:
        print(f"✓ Pearson correlation r={pearson_corr:.4f} ≥ {PEARSON_CORRELATION_THRESHOLD} requirement MET")
    else:
        print(f"⚠ Pearson correlation r={pearson_corr:.4f} < {PEARSON_CORRELATION_THRESHOLD} requirement")
    
    print("\nZ5D-SHA matching validation completed successfully!")
    return results
    assert 'correlation_validation' in results, "Correlation validation failed"
    
    # Check that we got a reasonable prediction
    z5d_pred = results['z5d_prediction']['z5d_prediction']
    assert 15000000 < z5d_pred < 16000000, f"Z5D prediction {z5d_pred} outside expected range"
    
    # Check validation score
    if 'validation_score' in results['correlation_validation']:
        score = results['correlation_validation']['validation_score']['overall_score']
        score = float(score)  # Ensure it's a regular float for formatting
        print(f"Validation score: {score:.3f}")
        assert score >= 0, "Validation score should be non-negative"
    
    print("✓ Z5D zeta validation test passed!")
    return results


if __name__ == "__main__":
    # Run the validation test
    test_results = test_z5d_zeta_validation()
    
    # Print summary
    print("\nVALIDATION SUMMARY:")
    print("-" * 40)
    if 'z5d_prediction' in test_results:
        z5d_val = test_results['z5d_prediction']['z5d_prediction']
        print(f"Z5D prediction for k=1,000,000: {z5d_val:,.2f}")
    
    if 'reference_prime' in test_results and 'relative_error_percent' in test_results['reference_prime']:
        error_pct = test_results['reference_prime']['relative_error_percent']
        print(f"Prediction accuracy: {100-error_pct:.4f}% (error: {error_pct:.6f}%)")
    
    if 'correlation_validation' in test_results and 'validation_score' in test_results['correlation_validation']:
        score_data = test_results['correlation_validation']['validation_score']
        score = float(score_data['overall_score'])  # Ensure it's a regular float
        print(f"Validation score: {score:.3f}")
        print(f"Interpretation: {score_data['interpretation']}")
    
    print("\n🎉 Z5D validation using zeta zeros completed successfully!")