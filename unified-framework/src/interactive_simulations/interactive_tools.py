"""
Interactive Tools for Z Framework Simulations

This module provides interactive interfaces and parameter variation tools for
engineering teams to explore and validate the Z Framework across physical
and discrete domains.

Key Features:
- Unified simulation interface for both domains
- Parameter variation and sensitivity analysis
- Interactive parameter exploration with real-time feedback
- Cross-domain correlation analysis
- Empirical verification workflows
"""

import numpy as np
import matplotlib.pyplot as plt
from typing import Dict, List, Optional, Tuple, Union, Any
import warnings
from dataclasses import dataclass

try:
    from .physical_domain_simulation import WormholeTraversalSimulation
    from .discrete_domain_simulation import Z5DPrimeSimulation
    SIMULATIONS_AVAILABLE = True
except ImportError:
    SIMULATIONS_AVAILABLE = False
    warnings.warn("Simulation modules not available for interactive tools.")

@dataclass
class ParameterRange:
    """Data class for parameter range specifications."""
    min_val: float
    max_val: float
    n_points: int = 20
    log_scale: bool = False

class ParameterVariationAnalyzer:
    """
    Advanced parameter variation and sensitivity analysis tool.
    
    This class provides systematic parameter exploration capabilities
    for both physical and discrete domain simulations.
    """
    
    def __init__(self):
        """Initialize parameter variation analyzer."""
        self.physical_sim = None
        self.discrete_sim = None
        self.results_cache = {}
        
        if SIMULATIONS_AVAILABLE:
            self.physical_sim = WormholeTraversalSimulation()
            self.discrete_sim = Z5DPrimeSimulation()
    
    def analyze_physical_parameters(self, 
                                  v_ratio_range: ParameterRange = None,
                                  throat_length_range: ParameterRange = None,
                                  distance_range: ParameterRange = None,
                                  plot: bool = True) -> Dict:
        """
        Analyze parameter sensitivity in physical domain simulation.
        
        Parameters
        ----------
        v_ratio_range : ParameterRange, optional
            Range for v/c ratio exploration
        throat_length_range : ParameterRange, optional
            Range for wormhole throat length
        distance_range : ParameterRange, optional
            Range for flat-space distance
        plot : bool
            Whether to generate visualization plots
            
        Returns
        -------
        dict
            Parameter sensitivity analysis results
        """
        if not SIMULATIONS_AVAILABLE or self.physical_sim is None:
            print("⚠️  Physical simulation not available")
            return {}
        
        print("🌌 Physical Domain Parameter Analysis")
        print("=" * 40)
        
        # Default parameter ranges
        if v_ratio_range is None:
            v_ratio_range = ParameterRange(0.1, 0.99, 50)
        if throat_length_range is None:
            throat_length_range = ParameterRange(1, 1000, 10, log_scale=True)  # AU units
        if distance_range is None:
            distance_range = ParameterRange(1, 100, 10, log_scale=True)  # Light-year units
        
        results = {
            'v_ratio_analysis': {},
            'throat_length_analysis': {},
            'distance_analysis': {},
            'parameter_ranges': {
                'v_ratio': v_ratio_range,
                'throat_length': throat_length_range,
                'distance': distance_range
            }
        }
        
        # 1. v/c ratio sensitivity analysis
        print("📈 Analyzing v/c ratio sensitivity...")
        v_ratios = np.linspace(v_ratio_range.min_val, v_ratio_range.max_val, v_ratio_range.n_points)
        
        # Fixed parameters for v/c analysis
        fixed_distance = 10 * self.physical_sim.light_year
        fixed_throat = 10 * self.physical_sim.au
        
        v_analysis = self.physical_sim.simulate_traversal(fixed_distance, fixed_throat, v_ratios)
        results['v_ratio_analysis'] = v_analysis
        
        # 2. Throat length sensitivity analysis
        print("📏 Analyzing throat length sensitivity...")
        if throat_length_range.log_scale:
            throat_lengths = np.logspace(np.log10(throat_length_range.min_val), 
                                       np.log10(throat_length_range.max_val), 
                                       throat_length_range.n_points)
        else:
            throat_lengths = np.linspace(throat_length_range.min_val, throat_length_range.max_val, 
                                       throat_length_range.n_points)
        
        throat_lengths_m = throat_lengths * self.physical_sim.au  # Convert to meters
        
        # Fixed parameters for throat analysis
        fixed_v_ratio = 0.9
        throat_effects = []
        
        for L in throat_lengths_m:
            effect = self.physical_sim.simulate_traversal(fixed_distance, L, [fixed_v_ratio])
            throat_effects.append({
                'throat_length_au': L / self.physical_sim.au,
                'apparent_over_c': effect['apparent_over_c'][0],
                'traversal_time': effect['traversal_times'][0],
                'lorentz_factor': effect['lorentz_factors'][0]
            })
        
        results['throat_length_analysis'] = throat_effects
        
        # 3. Distance sensitivity analysis
        print("🌍 Analyzing distance sensitivity...")
        if distance_range.log_scale:
            distances = np.logspace(np.log10(distance_range.min_val), 
                                  np.log10(distance_range.max_val), 
                                  distance_range.n_points)
        else:
            distances = np.linspace(distance_range.min_val, distance_range.max_val, 
                                  distance_range.n_points)
        
        distances_m = distances * self.physical_sim.light_year  # Convert to meters
        
        distance_effects = []
        for D in distances_m:
            effect = self.physical_sim.simulate_traversal(D, fixed_throat, [fixed_v_ratio])
            distance_effects.append({
                'distance_ly': D / self.physical_sim.light_year,
                'apparent_over_c': effect['apparent_over_c'][0],
                'traversal_time': effect['traversal_times'][0]
            })
        
        results['distance_analysis'] = distance_effects
        
        # Generate plots if requested
        if plot:
            self._plot_physical_analysis(results)
        
        return results
    
    def analyze_discrete_parameters(self, 
                                  c_range: ParameterRange = None,
                                  k_star_range: ParameterRange = None,
                                  k_geom_range: ParameterRange = None,
                                  test_k_values: List[int] = None,
                                  plot: bool = True) -> Dict:
        """
        Analyze parameter sensitivity in discrete domain simulation.
        
        Parameters
        ----------
        c_range : ParameterRange, optional
            Range for dilation parameter c
        k_star_range : ParameterRange, optional
            Range for curvature parameter k*
        k_geom_range : ParameterRange, optional
            Range for geometric curvature exponent
        test_k_values : list, optional
            List of k values to test
        plot : bool
            Whether to generate visualization plots
            
        Returns
        -------
        dict
            Parameter sensitivity analysis results
        """
        if not SIMULATIONS_AVAILABLE or self.discrete_sim is None:
            print("⚠️  Discrete simulation not available")
            return {}
        
        print("🔢 Discrete Domain Parameter Analysis")
        print("=" * 40)
        
        # Default parameter ranges
        if c_range is None:
            c_range = ParameterRange(-0.01, 0.01, 30)
        if k_star_range is None:
            k_star_range = ParameterRange(-0.3, 0.3, 30)
        if k_geom_range is None:
            k_geom_range = ParameterRange(0.1, 0.9, 20)
        if test_k_values is None:
            test_k_values = [1000, 5000, 10000]
        
        results = {
            'c_analysis': {},
            'k_star_analysis': {},
            'k_geom_analysis': {},
            'parameter_ranges': {
                'c': c_range,
                'k_star': k_star_range,
                'k_geom': k_geom_range
            },
            'test_k_values': test_k_values
        }
        
        # Parameter value arrays
        c_values = np.linspace(c_range.min_val, c_range.max_val, c_range.n_points)
        k_star_values = np.linspace(k_star_range.min_val, k_star_range.max_val, k_star_range.n_points)
        k_geom_values = np.linspace(k_geom_range.min_val, k_geom_range.max_val, k_geom_range.n_points)
        
        print(f"Testing with k values: {test_k_values}")
        
        # Analyze each test k value
        for k_test in test_k_values:
            print(f"\n📊 Analyzing k = {k_test}")
            
            # Get reference prediction
            ref_pred = self.discrete_sim.predict_primes([k_test])['z5d_corrected'][0]
            
            # c parameter analysis
            c_errors = []
            for c in c_values:
                pred = self.discrete_sim.predict_primes([k_test], c=c, apply_geometric_correction=False)
                error = abs(pred['z5d_raw'][0] - ref_pred) / ref_pred * 100
                c_errors.append(error)
            
            # k* parameter analysis
            k_star_errors = []
            for k_star in k_star_values:
                pred = self.discrete_sim.predict_primes([k_test], k_star=k_star, apply_geometric_correction=False)
                error = abs(pred['z5d_raw'][0] - ref_pred) / ref_pred * 100
                k_star_errors.append(error)
            
            # Geometric parameter analysis
            k_geom_errors = []
            for k_geom in k_geom_values:
                pred = self.discrete_sim.predict_primes([k_test], k_geom=k_geom, apply_geometric_correction=True)
                error = abs(pred['z5d_corrected'][0] - ref_pred) / ref_pred * 100
                k_geom_errors.append(error)
            
            # Store results for this k value
            results['c_analysis'][k_test] = {
                'c_values': c_values,
                'errors': c_errors,
                'optimal_c': c_values[np.argmin(c_errors)],
                'min_error': np.min(c_errors)
            }
            
            results['k_star_analysis'][k_test] = {
                'k_star_values': k_star_values,
                'errors': k_star_errors,
                'optimal_k_star': k_star_values[np.argmin(k_star_errors)],
                'min_error': np.min(k_star_errors)
            }
            
            results['k_geom_analysis'][k_test] = {
                'k_geom_values': k_geom_values,
                'errors': k_geom_errors,
                'optimal_k_geom': k_geom_values[np.argmin(k_geom_errors)],
                'min_error': np.min(k_geom_errors)
            }
        
        # Generate plots if requested
        if plot:
            self._plot_discrete_analysis(results)
        
        return results
    
    def cross_domain_correlation_analysis(self, 
                                        physical_results: Dict = None,
                                        discrete_results: Dict = None) -> Dict:
        """
        Analyze correlations between physical and discrete domain parameters.
        
        Parameters
        ----------
        physical_results : dict, optional
            Physical domain analysis results
        discrete_results : dict, optional
            Discrete domain analysis results
            
        Returns
        -------
        dict
            Cross-domain correlation analysis
        """
        print("🔗 Cross-Domain Correlation Analysis")
        print("=" * 35)
        
        if physical_results is None or discrete_results is None:
            print("⚠️  Both physical and discrete results required for correlation analysis")
            return {}
        
        # Extract relevant metrics for correlation
        correlations = {}
        
        # Example: Correlation between v/c sensitivity and c parameter sensitivity
        if 'v_ratio_analysis' in physical_results and discrete_results['c_analysis']:
            print("📈 Analyzing v/c ↔ c parameter correlation...")
            
            # Get physical domain apparent speed variations
            v_analysis = physical_results['v_ratio_analysis']
            apparent_variations = np.diff(v_analysis['apparent_over_c'])
            
            # Get discrete domain c parameter error variations
            k_test = list(discrete_results['c_analysis'].keys())[0]
            c_analysis = discrete_results['c_analysis'][k_test]
            c_error_variations = np.diff(c_analysis['errors'])
            
            # Compute correlation if dimensions match
            min_len = min(len(apparent_variations), len(c_error_variations))
            if min_len > 2:
                from scipy.stats import pearsonr
                try:
                    corr_coef, p_value = pearsonr(apparent_variations[:min_len], 
                                                c_error_variations[:min_len])
                    
                    correlations['v_ratio_c_param'] = {
                        'correlation': corr_coef,
                        'p_value': p_value,
                        'significance': 'significant' if p_value < 0.05 else 'not_significant',
                        'interpretation': 'Strong' if abs(corr_coef) > 0.7 else 'Moderate' if abs(corr_coef) > 0.3 else 'Weak'
                    }
                    
                    print(f"  Correlation coefficient: {corr_coef:.3f}")
                    print(f"  P-value: {p_value:.3e}")
                    print(f"  Interpretation: {correlations['v_ratio_c_param']['interpretation']}")
                except Exception as e:
                    print(f"  Correlation calculation failed: {e}")
        
        # Unified framework validation
        if correlations:
            print(f"\n🔬 Framework Unification Assessment:")
            
            significant_correlations = sum(1 for c in correlations.values() 
                                         if c.get('significance') == 'significant')
            total_correlations = len(correlations)
            
            unification_score = significant_correlations / total_correlations if total_correlations > 0 else 0
            
            correlations['unification_metrics'] = {
                'significant_correlations': significant_correlations,
                'total_correlations': total_correlations,
                'unification_score': unification_score,
                'framework_validation': 'STRONG' if unification_score > 0.7 else 'MODERATE' if unification_score > 0.3 else 'WEAK'
            }
            
            print(f"  Significant correlations: {significant_correlations}/{total_correlations}")
            print(f"  Unification score: {unification_score:.2f}")
            print(f"  Framework validation: {correlations['unification_metrics']['framework_validation']}")
        
        return correlations
    
    def _plot_physical_analysis(self, results: Dict):
        """Generate plots for physical domain parameter analysis."""
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        
        # Plot 1: v/c ratio analysis
        ax1 = axes[0, 0]
        v_analysis = results['v_ratio_analysis']
        ax1.plot(v_analysis['v_ratios'], v_analysis['apparent_over_c'], 'b-', linewidth=2)
        ax1.set_xlabel('v/c Ratio')
        ax1.set_ylabel('Apparent Speed / c')
        ax1.set_title('Apparent Speed vs v/c Ratio')
        ax1.grid(True, alpha=0.3)
        ax1.set_yscale('log')
        
        # Plot 2: Throat length analysis
        ax2 = axes[0, 1]
        throat_analysis = results['throat_length_analysis']
        throat_lengths = [t['throat_length_au'] for t in throat_analysis]
        apparent_speeds = [t['apparent_over_c'] for t in throat_analysis]
        ax2.plot(throat_lengths, apparent_speeds, 'r-', linewidth=2)
        ax2.set_xlabel('Throat Length (AU)')
        ax2.set_ylabel('Apparent Speed / c')
        ax2.set_title('Apparent Speed vs Throat Length')
        ax2.grid(True, alpha=0.3)
        ax2.set_xscale('log')
        ax2.set_yscale('log')
        
        # Plot 3: Distance analysis
        ax3 = axes[1, 0]
        distance_analysis = results['distance_analysis']
        distances = [d['distance_ly'] for d in distance_analysis]
        apparent_speeds_d = [d['apparent_over_c'] for d in distance_analysis]
        ax3.plot(distances, apparent_speeds_d, 'g-', linewidth=2)
        ax3.set_xlabel('Distance (Light Years)')
        ax3.set_ylabel('Apparent Speed / c')
        ax3.set_title('Apparent Speed vs Distance')
        ax3.grid(True, alpha=0.3)
        ax3.set_xscale('log')
        ax3.set_yscale('log')
        
        # Plot 4: Lorentz factor
        ax4 = axes[1, 1]
        ax4.plot(v_analysis['v_ratios'], v_analysis['lorentz_factors'], 'purple', linewidth=2)
        ax4.set_xlabel('v/c Ratio')
        ax4.set_ylabel('Lorentz Factor γ')
        ax4.set_title('Relativistic Lorentz Factor')
        ax4.grid(True, alpha=0.3)
        ax4.set_yscale('log')
        
        plt.tight_layout()
        plt.show()
    
    def _plot_discrete_analysis(self, results: Dict):
        """Generate plots for discrete domain parameter analysis."""
        test_k_values = results['test_k_values']
        n_k = len(test_k_values)
        
        fig, axes = plt.subplots(n_k, 3, figsize=(18, 6*n_k))
        if n_k == 1:
            axes = axes.reshape(1, -1)
        
        for i, k_test in enumerate(test_k_values):
            # c parameter plot
            c_analysis = results['c_analysis'][k_test]
            axes[i, 0].plot(c_analysis['c_values'], c_analysis['errors'], 'b-', linewidth=2)
            axes[i, 0].axvline(x=c_analysis['optimal_c'], color='red', linestyle='--', 
                              label=f'Optimal: {c_analysis["optimal_c"]:.6f}')
            axes[i, 0].set_xlabel('c Parameter')
            axes[i, 0].set_ylabel('Relative Error (%)')
            axes[i, 0].set_title(f'c Sensitivity (k={k_test})')
            axes[i, 0].legend()
            axes[i, 0].grid(True, alpha=0.3)
            
            # k* parameter plot
            k_star_analysis = results['k_star_analysis'][k_test]
            axes[i, 1].plot(k_star_analysis['k_star_values'], k_star_analysis['errors'], 'r-', linewidth=2)
            axes[i, 1].axvline(x=k_star_analysis['optimal_k_star'], color='red', linestyle='--',
                              label=f'Optimal: {k_star_analysis["optimal_k_star"]:.6f}')
            axes[i, 1].set_xlabel('k* Parameter')
            axes[i, 1].set_ylabel('Relative Error (%)')
            axes[i, 1].set_title(f'k* Sensitivity (k={k_test})')
            axes[i, 1].legend()
            axes[i, 1].grid(True, alpha=0.3)
            
            # Geometric parameter plot
            k_geom_analysis = results['k_geom_analysis'][k_test]
            axes[i, 2].plot(k_geom_analysis['k_geom_values'], k_geom_analysis['errors'], 'g-', linewidth=2)
            axes[i, 2].axvline(x=k_geom_analysis['optimal_k_geom'], color='red', linestyle='--',
                              label=f'Optimal: {k_geom_analysis["optimal_k_geom"]:.3f}')
            axes[i, 2].set_xlabel('Geometric k Parameter')
            axes[i, 2].set_ylabel('Relative Error (%)')
            axes[i, 2].set_title(f'Geometric Sensitivity (k={k_test})')
            axes[i, 2].legend()
            axes[i, 2].grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.show()

class SimulationInterface:
    """
    Unified interface for running both physical and discrete domain simulations.
    
    This class provides a single entry point for engineering teams to interact
    with both simulation domains and explore parameter variations.
    """
    
    def __init__(self):
        """Initialize simulation interface."""
        self.physical_sim = None
        self.discrete_sim = None
        self.analyzer = ParameterVariationAnalyzer()
        
        if SIMULATIONS_AVAILABLE:
            self.physical_sim = WormholeTraversalSimulation()
            self.discrete_sim = Z5DPrimeSimulation()
        
        self.session_results = {}
    
    def run_full_verification_suite(self, 
                                  include_parameter_analysis: bool = True,
                                  include_cross_domain: bool = True,
                                  save_results: bool = False) -> Dict:
        """
        Run complete empirical verification suite for both domains.
        
        Parameters
        ----------
        include_parameter_analysis : bool
            Whether to include parameter sensitivity analysis
        include_cross_domain : bool
            Whether to include cross-domain correlation analysis
        save_results : bool
            Whether to save results to files
            
        Returns
        -------
        dict
            Complete verification suite results
        """
        print("🎯 Z Framework Complete Empirical Verification Suite")
        print("=" * 55)
        
        results = {
            'physical_domain': {},
            'discrete_domain': {},
            'parameter_analysis': {},
            'cross_domain_analysis': {},
            'overall_validation': {}
        }
        
        # 1. Physical Domain Simulation
        if self.physical_sim is not None:
            print("\n🌌 Physical Domain Verification")
            print("-" * 30)
            
            # Basic simulation
            physical_results = self.physical_sim.run_interactive_simulation(plot=True)
            empirical_validation = self.physical_sim.verify_empirical_consistency()
            causality_check = self.physical_sim.demonstrate_causality_preservation()
            
            results['physical_domain'] = {
                'simulation_results': physical_results,
                'empirical_validation': empirical_validation,
                'causality_check': causality_check
            }
        
        # 2. Discrete Domain Simulation
        if self.discrete_sim is not None:
            print("\n🔢 Discrete Domain Verification")
            print("-" * 30)
            
            # Basic simulation
            discrete_results = self.discrete_sim.run_interactive_simulation(plot=True)
            
            results['discrete_domain'] = {
                'simulation_results': discrete_results
            }
        
        # 3. Parameter Analysis
        if include_parameter_analysis and self.analyzer is not None:
            print("\n📊 Parameter Sensitivity Analysis")
            print("-" * 32)
            
            physical_param_analysis = self.analyzer.analyze_physical_parameters(plot=True)
            discrete_param_analysis = self.analyzer.analyze_discrete_parameters(plot=True)
            
            results['parameter_analysis'] = {
                'physical': physical_param_analysis,
                'discrete': discrete_param_analysis
            }
        
        # 4. Cross-Domain Analysis
        if include_cross_domain and 'parameter_analysis' in results:
            print("\n🔗 Cross-Domain Correlation Analysis")
            print("-" * 35)
            
            cross_domain_results = self.analyzer.cross_domain_correlation_analysis(
                results['parameter_analysis']['physical'],
                results['parameter_analysis']['discrete']
            )
            
            results['cross_domain_analysis'] = cross_domain_results
        
        # 5. Overall Validation Assessment
        print("\n✅ Overall Framework Validation")
        print("-" * 30)
        
        validation_score = self._compute_overall_validation_score(results)
        results['overall_validation'] = validation_score
        
        print(f"Framework Validation Score: {validation_score['score']:.2f}/1.00")
        print(f"Validation Status: {validation_score['status']}")
        
        # Store session results
        self.session_results = results
        
        # Save results if requested
        if save_results:
            self._save_results(results)
        
        return results
    
    def _compute_overall_validation_score(self, results: Dict) -> Dict:
        """Compute overall validation score based on all tests."""
        score_components = {}
        total_weight = 0
        weighted_score = 0
        
        # Physical domain validation (weight: 0.3)
        if 'physical_domain' in results and results['physical_domain']:
            physical_score = 0
            
            # Empirical validation
            if 'empirical_validation' in results['physical_domain']:
                emp_val = results['physical_domain']['empirical_validation']
                if 'overall' in emp_val and emp_val['overall']['all_tests_pass']:
                    physical_score += 0.5
            
            # Causality preservation
            if 'causality_check' in results['physical_domain']:
                causality = results['physical_domain']['causality_check']
                if 'overall' in causality and causality['overall']['causality_globally_preserved']:
                    physical_score += 0.5
            
            score_components['physical'] = physical_score
            weighted_score += physical_score * 0.3
            total_weight += 0.3
        
        # Discrete domain validation (weight: 0.3)
        if 'discrete_domain' in results and results['discrete_domain']:
            discrete_score = 0.8  # Base score for successful execution
            
            # Error analysis
            sim_results = results['discrete_domain']['simulation_results']
            if 'errors' in sim_results and sim_results['errors']:
                errors = sim_results['errors']
                if 'mean_z5d_corrected_error' in errors:
                    mean_error = errors['mean_z5d_corrected_error']
                    if mean_error < 1.0:  # Less than 1% error
                        discrete_score = 1.0
                    elif mean_error < 5.0:  # Less than 5% error
                        discrete_score = 0.8
                    else:
                        discrete_score = 0.5
            
            score_components['discrete'] = discrete_score
            weighted_score += discrete_score * 0.3
            total_weight += 0.3
        
        # Cross-domain correlation (weight: 0.4)
        if 'cross_domain_analysis' in results and results['cross_domain_analysis']:
            cross_domain_score = 0
            
            if 'unification_metrics' in results['cross_domain_analysis']:
                unif_metrics = results['cross_domain_analysis']['unification_metrics']
                unif_score = unif_metrics.get('unification_score', 0)
                cross_domain_score = unif_score
            
            score_components['cross_domain'] = cross_domain_score
            weighted_score += cross_domain_score * 0.4
            total_weight += 0.4
        
        # Final score
        final_score = weighted_score / total_weight if total_weight > 0 else 0
        
        # Status determination
        if final_score >= 0.8:
            status = "EXCELLENT - Framework fully validated"
        elif final_score >= 0.6:
            status = "GOOD - Framework validated with minor issues"
        elif final_score >= 0.4:
            status = "MODERATE - Framework partially validated"
        else:
            status = "POOR - Framework validation failed"
        
        return {
            'score': final_score,
            'status': status,
            'components': score_components,
            'total_weight': total_weight
        }
    
    def _save_results(self, results: Dict):
        """Save results to files."""
        try:
            import json
            import datetime
            
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"z_framework_verification_{timestamp}.json"
            
            # Convert numpy arrays to lists for JSON serialization
            def convert_numpy(obj):
                if isinstance(obj, np.ndarray):
                    return obj.tolist()
                elif isinstance(obj, np.integer):
                    return int(obj)
                elif isinstance(obj, np.floating):
                    return float(obj)
                elif isinstance(obj, dict):
                    return {key: convert_numpy(value) for key, value in obj.items()}
                elif isinstance(obj, list):
                    return [convert_numpy(item) for item in obj]
                else:
                    return obj
            
            json_results = convert_numpy(results)
            
            with open(filename, 'w') as f:
                json.dump(json_results, f, indent=2)
            
            print(f"💾 Results saved to {filename}")
            
        except Exception as e:
            print(f"⚠️  Failed to save results: {e}")

def run_complete_verification_example():
    """
    Example of running complete verification suite.
    Demonstrates full usage of the interactive simulation tools.
    """
    print("🚀 Complete Z Framework Verification Example")
    print("=" * 50)
    
    # Initialize interface
    interface = SimulationInterface()
    
    # Run full verification suite
    results = interface.run_full_verification_suite(
        include_parameter_analysis=True,
        include_cross_domain=True,
        save_results=True
    )
    
    return results

if __name__ == "__main__":
    # Run complete verification when module is executed directly
    run_complete_verification_example()