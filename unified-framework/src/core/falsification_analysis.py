#!/usr/bin/env python3
"""
Falsification Analysis Module for Z-Transformation Hypothesis

This module implements the specific analysis methods required for the
Z-Transformation hypothesis falsification as outlined in Issue #368.

Key implementations:
1. Graph Laplacian metric for arithmetic geometry analogs
2. Swarm dynamics simulation for emergence testing  
3. 5D relativistic constraint validation
4. Möbius transform analysis with e² normalization
5. Enhanced empirical validation framework
"""

import numpy as np
import mpmath as mp
import networkx as nx
from sympy import divisors, isprime, mobius
from typing import List, Tuple, Dict, Optional, Union
import collections
from .domain import DiscreteZetaShift
from .axioms import velocity_5d_constraint

# Set high precision
mp.mp.dps = 50

class GraphLaplacianMetric:
    """
    Implements graph Laplacian metric for formalizing arithmetic curvature.
    
    This provides a graph-theoretic approach to understand divisor relationships
    as geometric structures, addressing the curvature analogy falsification.
    """
    
    def __init__(self, max_n: int = 100):
        """
        Initialize graph metric for integers up to max_n.
        
        Args:
            max_n: Maximum integer to include in the graph
        """
        self.max_n = max_n
        self.graph = self._build_divisor_graph()
        
    def _build_divisor_graph(self) -> nx.Graph:
        """Build graph with edges weighted by divisor relationships."""
        G = nx.Graph()
        
        # Add nodes for all integers 2 to max_n
        nodes = list(range(2, self.max_n + 1))
        G.add_nodes_from(nodes)
        
        # Add edges weighted by inverse gcd (shared factors as "closeness")
        for i in nodes:
            for j in nodes:
                if i < j:
                    gcd_val = np.gcd(i, j)
                    if gcd_val > 1:  # Only connect if they share factors
                        weight = 1.0 / gcd_val
                        G.add_edge(i, j, weight=weight)
        
        return G
    
    def compute_curvature_proxy(self) -> Dict[str, float]:
        """
        Compute graph Laplacian eigenvalues as curvature proxy.
        
        Returns:
            Dictionary with curvature metrics
        """
        try:
            L = nx.normalized_laplacian_matrix(self.graph).toarray()
            eigenvals = np.linalg.eigvals(L)
            eigenvals = eigenvals[eigenvals > 1e-10]  # Remove near-zero eigenvalues
            
            if len(eigenvals) > 0:
                return {
                    'mean_eigenvalue': float(np.mean(eigenvals)),
                    'max_eigenvalue': float(np.max(eigenvals)),
                    'eigenvalue_variance': float(np.var(eigenvals)),
                    'num_eigenvalues': len(eigenvals)
                }
            else:
                return {'mean_eigenvalue': 0.0, 'max_eigenvalue': 0.0, 
                       'eigenvalue_variance': 0.0, 'num_eigenvalues': 0}
                
        except Exception as e:
            return {'error': str(e)}
    
    def analyze_prime_geodesics(self) -> Dict[str, Union[float, List[int]]]:
        """
        Analyze geodesic properties for primes vs composites.
        
        Returns:
            Dictionary with geodesic analysis results
        """
        nodes = list(range(2, self.max_n + 1))
        primes = [n for n in nodes if isprime(n)]
        composites = [n for n in nodes if not isprime(n)]
        
        # Compute degrees (local connectivity)
        prime_degrees = [self.graph.degree(p) for p in primes]
        composite_degrees = [self.graph.degree(c) for c in composites]
        
        # Compute shortest path lengths for sample pairs
        try:
            prime_paths = []
            for i, p1 in enumerate(primes[:10]):  # Sample first 10 primes
                for p2 in primes[i+1:11]:  # Avoid all pairs for performance
                    if nx.has_path(self.graph, p1, p2):
                        path_len = nx.shortest_path_length(self.graph, p1, p2)
                        prime_paths.append(path_len)
            
            return {
                'prime_mean_degree': float(np.mean(prime_degrees)) if prime_degrees else 0.0,
                'composite_mean_degree': float(np.mean(composite_degrees)) if composite_degrees else 0.0,
                'prime_degree_variance': float(np.var(prime_degrees)) if prime_degrees else 0.0,
                'composite_degree_variance': float(np.var(composite_degrees)) if composite_degrees else 0.0,
                'prime_mean_path_length': float(np.mean(prime_paths)) if prime_paths else 0.0,
                'prime_degrees': prime_degrees[:10],  # Sample for inspection
                'composite_degrees': composite_degrees[:10]
            }
            
        except Exception as e:
            return {'error': str(e)}

class SwarmDynamicsSimulation:
    """
    Implements swarm dynamics simulation for testing emergence vs definition.
    
    This simulates divisor-based particle interactions to test whether
    inertia-like damping emerges from collective κ(n) coupling.
    """
    
    def __init__(self, n_particles: int = 100, max_steps: int = 50):
        """
        Initialize swarm simulation.
        
        Args:
            n_particles: Number of particles in the swarm
            max_steps: Maximum simulation steps
        """
        self.n_particles = n_particles
        self.max_steps = max_steps
        
    def simulate_divisor_swarm(self, 
                              base_values: List[int],
                              coupling_strength: float = 0.1) -> Dict[str, List[float]]:
        """
        Simulate swarm dynamics with divisor-based coupling.
        
        Args:
            base_values: Base integer values for particles
            coupling_strength: Strength of κ(n) coupling
            
        Returns:
            Dictionary with simulation results
        """
        # Initialize particles with base integer values
        n_base = len(base_values)
        positions = np.random.choice(base_values, self.n_particles)
        velocities = np.zeros(self.n_particles)
        
        # Storage for trajectory analysis
        position_history = []
        velocity_history = []
        variance_history = []
        
        for step in range(self.max_steps):
            # Compute κ(n) for each particle
            kappas = np.array([self._compute_kappa(int(pos)) for pos in positions])
            
            # Update velocities based on κ(n) coupling (damping)
            velocity_updates = -coupling_strength * kappas * velocities
            
            # Add small random perturbation
            velocity_updates += 0.01 * np.random.randn(self.n_particles)
            
            velocities += velocity_updates
            
            # Update positions (keep as integers, modulo to stay in reasonable range)
            position_updates = velocities.astype(int)
            positions = np.abs(positions + position_updates) % max(base_values) + 2
            
            # Record statistics
            position_history.append(positions.copy())
            velocity_history.append(velocities.copy())
            variance_history.append(float(np.var(positions)))
        
        return {
            'final_positions': positions.tolist(),
            'final_velocities': velocities.tolist(),
            'position_variance_trajectory': variance_history,
            'mean_final_velocity': float(np.mean(np.abs(velocities))),
            'position_stability': float(np.std(variance_history)),
            'convergence_rate': self._compute_convergence_rate(variance_history)
        }
    
    def _compute_kappa(self, n: int) -> float:
        """Compute κ(n) = d(n) · ln(n+1)/e² for a given integer."""
        d_n = len(divisors(n))
        return float(d_n * mp.log(n + 1) / mp.exp(2))
    
    def _compute_convergence_rate(self, variance_history: List[float]) -> float:
        """Compute convergence rate from variance trajectory."""
        if len(variance_history) < 10:
            return 0.0
        
        # Fit exponential decay to last half of trajectory
        mid_point = len(variance_history) // 2
        recent_variance = variance_history[mid_point:]
        
        if len(recent_variance) < 2:
            return 0.0
            
        # Simple linear fit to log(variance) for exponential decay rate
        try:
            log_variance = np.log(np.array(recent_variance) + 1e-10)  # Avoid log(0)
            time_points = np.arange(len(recent_variance))
            
            if len(time_points) > 1:
                slope = np.polyfit(time_points, log_variance, 1)[0]
                return float(-slope)  # Negative slope indicates decay
            else:
                return 0.0
        except:
            return 0.0

class FiveDimensionalConstraintValidator:
    """
    Implements 5D relativistic constraint validation for frame-invariance testing.
    
    This tests the hypothesis that constraining v relativistically as a component
    in 5D velocity can preserve Lorentz-like invariance.
    """
    
    def __init__(self, c: float = 299792458.0):
        """
        Initialize constraint validator.
        
        Args:
            c: Speed of light (universal invariant)
        """
        self.c = c
        
    def test_5d_constraint_satisfaction(self, 
                                       v_4d_components: List[Tuple[float, float, float, float]],
                                       tolerance: float = 1e-6) -> Dict[str, Union[bool, float, List]]:
        """
        Test 5D velocity constraint v_{5D}^2 = c^2.
        
        Args:
            v_4d_components: List of (v_x, v_y, v_z, v_t) tuples
            tolerance: Tolerance for constraint satisfaction
            
        Returns:
            Dictionary with constraint validation results
        """
        results = {
            'all_satisfied': True,
            'violations': [],
            'max_violation': 0.0,
            'computed_v_w_values': [],
            'constraint_violations': []
        }
        
        for i, (v_x, v_y, v_z, v_t) in enumerate(v_4d_components):
            # Compute required v_w to satisfy constraint
            v_4d_squared = v_x**2 + v_y**2 + v_z**2 + v_t**2
            
            if v_4d_squared <= self.c**2:
                v_w_required = np.sqrt(self.c**2 - v_4d_squared)
                
                # Test constraint satisfaction
                violation = velocity_5d_constraint(v_x, v_y, v_z, v_t, v_w_required, self.c)
                
                results['computed_v_w_values'].append(float(v_w_required))
                results['constraint_violations'].append(float(violation))
                
                if violation > tolerance:
                    results['all_satisfied'] = False
                    results['violations'].append(i)
                    
                results['max_violation'] = max(results['max_violation'], violation)
                
            else:
                # 4D components already exceed c^2
                results['all_satisfied'] = False
                results['violations'].append(i)
                results['computed_v_w_values'].append(float('inf'))
                results['constraint_violations'].append(float('inf'))
                results['max_violation'] = float('inf')
        
        return results
    
    def test_prime_invariance_under_constraint(self, 
                                              primes: List[int],
                                              v_base: float = 0.5) -> Dict[str, float]:
        """
        Test whether primes maintain low variance under 5D constraint.
        
        Args:
            primes: List of prime numbers to test
            v_base: Base velocity component value
            
        Returns:
            Dictionary with prime invariance results
        """
        # Test various 5D velocity configurations
        v_configs = [
            (v_base * self.c, 0.3 * self.c, 0.2 * self.c, 0.1 * self.c),
            (0.4 * self.c, v_base * self.c, 0.3 * self.c, 0.2 * self.c),
            (0.3 * self.c, 0.3 * self.c, v_base * self.c, 0.1 * self.c)
        ]
        
        z_values_by_config = []
        
        for v_x, v_y, v_z, v_t in v_configs:
            v_4d_squared = v_x**2 + v_y**2 + v_z**2 + v_t**2
            
            if v_4d_squared <= self.c**2:
                v_w = np.sqrt(self.c**2 - v_4d_squared)
                
                # Normalize v for DiscreteZetaShift (use magnitude as rate)
                v_magnitude = np.sqrt(v_4d_squared + v_w**2) / self.c
                
                config_z_values = []
                for prime in primes:
                    try:
                        dzs = DiscreteZetaShift(prime, v=v_magnitude)
                        z_val = float(dzs.compute_z())
                        config_z_values.append(z_val)
                    except:
                        continue
                
                if config_z_values:
                    z_values_by_config.append(config_z_values)
        
        # Analyze variance across configurations
        if len(z_values_by_config) > 1:
            # Compute variance for each prime across configurations
            prime_variances = []
            for i in range(len(primes)):
                prime_z_across_configs = [config[i] for config in z_values_by_config 
                                        if i < len(config)]
                if len(prime_z_across_configs) > 1:
                    variance = np.var(prime_z_across_configs)
                    prime_variances.append(variance)
            
            return {
                'mean_prime_variance': float(np.mean(prime_variances)) if prime_variances else 0.0,
                'max_prime_variance': float(np.max(prime_variances)) if prime_variances else 0.0,
                'num_configs_tested': len(z_values_by_config),
                'num_primes_analyzed': len(prime_variances)
            }
        else:
            return {'mean_prime_variance': 0.0, 'max_prime_variance': 0.0, 
                   'num_configs_tested': 0, 'num_primes_analyzed': 0}

class MobiusTransformAnalyzer:
    """
    Implements Möbius transform analysis with e² normalization.
    
    This tests transform invariance and predictive power enhancement
    through arithmetic function integration.
    """
    
    def __init__(self):
        """Initialize Möbius transform analyzer."""
        self.e_squared = float(mp.exp(2))
        
    def analyze_mobius_normalized_transforms(self, 
                                           test_values: List[int]) -> Dict[str, Union[float, List]]:
        """
        Analyze Möbius μ(n) transforms normalized by e².
        
        Args:
            test_values: List of integers to analyze
            
        Returns:
            Dictionary with Möbius transform analysis
        """
        results = {
            'square_free_ratios': [],
            'square_free_bounded': True,
            'transform_variances': [],
            'zero_mobius_count': 0,
            'bounded_ratio_violations': []
        }
        
        for n in test_values:
            mu_n = mobius(n)
            
            if mu_n == 0:
                results['zero_mobius_count'] += 1
                continue
                
            # Normalized Möbius rate
            b_normalized = mu_n / self.e_squared
            
            try:
                # Original computation
                dzs_original = DiscreteZetaShift(n, v=1.0)
                z_original = float(dzs_original.compute_z())
                
                # Möbius-transformed computation
                dzs_mobius = DiscreteZetaShift(n, v=abs(b_normalized))
                z_mobius = float(dzs_mobius.compute_z())
                
                if z_original != 0 and np.isfinite(z_original) and np.isfinite(z_mobius):
                    ratio = abs(z_mobius / z_original)
                    results['square_free_ratios'].append(ratio)
                    
                    # Check if ratio is bounded (should be < 10 for good behavior)
                    if ratio >= 10.0:
                        results['square_free_bounded'] = False
                        results['bounded_ratio_violations'].append((n, ratio))
                
                # Compute variance in chain for transform stability
                chain_original = self._unfold_chain(dzs_original, 5)
                chain_mobius = self._unfold_chain(dzs_mobius, 5)
                
                if len(chain_original) > 1 and len(chain_mobius) > 1:
                    var_original = np.var(chain_original)
                    var_mobius = np.var(chain_mobius)
                    results['transform_variances'].append((var_original, var_mobius))
                
            except Exception:
                continue
        
        # Compute summary statistics
        if results['square_free_ratios']:
            results['mean_ratio'] = float(np.mean(results['square_free_ratios']))
            results['max_ratio'] = float(np.max(results['square_free_ratios']))
            results['ratio_variance'] = float(np.var(results['square_free_ratios']))
        else:
            results['mean_ratio'] = 0.0
            results['max_ratio'] = 0.0
            results['ratio_variance'] = 0.0
            
        return results
    
    def _unfold_chain(self, dzs: DiscreteZetaShift, steps: int) -> List[float]:
        """Unfold DiscreteZetaShift chain for given number of steps."""
        chain_values = [float(dzs.compute_z())]
        current = dzs
        
        for _ in range(steps):
            try:
                current = current.unfold_next()
                z_val = float(current.compute_z())
                chain_values.append(z_val)
            except:
                break
                
        return chain_values

class ComprehensiveFalsificationValidator:
    """
    Comprehensive validator that combines all falsification analyses.
    
    This provides a unified interface for running all falsification tests
    and generating a comprehensive assessment report.
    """
    
    def __init__(self, max_n: int = 100):
        """Initialize comprehensive validator."""
        self.max_n = max_n
        self.graph_metric = GraphLaplacianMetric(max_n)
        self.swarm_dynamics = SwarmDynamicsSimulation()
        self.constraint_validator = FiveDimensionalConstraintValidator()
        self.mobius_analyzer = MobiusTransformAnalyzer()
        
    def run_comprehensive_falsification_analysis(self) -> Dict[str, Dict]:
        """
        Run comprehensive falsification analysis across all criteria.
        
        Returns:
            Dictionary with complete falsification assessment
        """
        # Test data
        primes = [p for p in range(2, min(30, self.max_n)) if isprime(p)]
        semiprimes = [15, 21, 35, 77, 91]
        test_integers = list(range(2, min(50, self.max_n)))
        
        results = {}
        
        # 1. Graph Laplacian curvature analysis
        try:
            results['curvature_analysis'] = {
                'curvature_metrics': self.graph_metric.compute_curvature_proxy(),
                'prime_geodesics': self.graph_metric.analyze_prime_geodesics()
            }
        except Exception as e:
            results['curvature_analysis'] = {'error': str(e)}
        
        # 2. Swarm dynamics emergence testing
        try:
            results['emergence_analysis'] = self.swarm_dynamics.simulate_divisor_swarm(
                base_values=primes[:10], coupling_strength=0.1
            )
        except Exception as e:
            results['emergence_analysis'] = {'error': str(e)}
        
        # 3. 5D constraint validation
        try:
            v_4d_configs = [
                (0.5, 0.3, 0.2, 0.1),
                (0.6, 0.4, 0.3, 0.2),
                (0.4, 0.4, 0.4, 0.1)
            ]
            # Scale by c for realistic testing
            c = self.constraint_validator.c
            v_4d_scaled = [(v[0]*c, v[1]*c, v[2]*c, v[3]*c) for v in v_4d_configs]
            
            results['constraint_analysis'] = {
                'constraint_satisfaction': self.constraint_validator.test_5d_constraint_satisfaction(v_4d_scaled),
                'prime_invariance': self.constraint_validator.test_prime_invariance_under_constraint(primes[:5])
            }
        except Exception as e:
            results['constraint_analysis'] = {'error': str(e)}
        
        # 4. Möbius transform analysis
        try:
            results['transform_analysis'] = self.mobius_analyzer.analyze_mobius_normalized_transforms(
                test_integers[:20]
            )
        except Exception as e:
            results['transform_analysis'] = {'error': str(e)}
        
        # 5. Frame dependence analysis
        try:
            results['frame_dependence'] = self._analyze_frame_dependence(primes[:5], semiprimes[:3])
        except Exception as e:
            results['frame_dependence'] = {'error': str(e)}
        
        return results
    
    def _analyze_frame_dependence(self, primes: List[int], semiprimes: List[int]) -> Dict[str, float]:
        """Analyze frame dependence across v values."""
        v_values = [0.1, 0.5, 1.0, 2.0]
        
        # Test prime frame dependence
        prime_variances = []
        for prime in primes:
            z_values = []
            for v in v_values:
                try:
                    dzs = DiscreteZetaShift(prime, v=v)
                    z_values.append(float(dzs.compute_z()))
                except:
                    continue
            
            if len(z_values) > 1:
                prime_variances.append(np.var(z_values))
        
        # Test semiprime frame dependence
        semiprime_variances = []
        for semiprime in semiprimes:
            z_values = []
            for v in v_values:
                try:
                    dzs = DiscreteZetaShift(semiprime, v=v)
                    z_values.append(float(dzs.compute_z()))
                except:
                    continue
                    
            if len(z_values) > 1:
                semiprime_variances.append(np.var(z_values))
        
        return {
            'prime_mean_variance': float(np.mean(prime_variances)) if prime_variances else 0.0,
            'semiprime_mean_variance': float(np.mean(semiprime_variances)) if semiprime_variances else 0.0,
            'prime_max_variance': float(np.max(prime_variances)) if prime_variances else 0.0,
            'falsification_threshold_exceeded': any(v > 1e-16 for v in prime_variances) if prime_variances else False
        }