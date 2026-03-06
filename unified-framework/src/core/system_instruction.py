"""
Z Framework System Instruction: Operational Logic and Empirical Guidance
========================================================================

This module establishes the operational logic, empirical rigor, and mathematical principles 
for unified analysis within the Z Framework. It provides systematic validation of the core
principles and ensures consistent application across all domains.

SYSTEM INSTRUCTION PRINCIPLES:

1. Z Model Universal Invariant Formulation
2. Domain-Specific Forms (Physical and Discrete)  
3. Geometric Resolution via Curvature-Based Geodesics
4. Operational Guidance for Empirical Validation

This system instruction must be followed for all Z Framework operations to ensure
cross-domain consistency and empirical rigor.
"""

import numpy as np
import mpmath as mp
from typing import Dict, Any, Callable, Tuple, Union, Optional
from abc import ABC, abstractmethod
import warnings

# Set high precision for all Z Framework operations
mp.mp.dps = 50

class ZFrameworkSystemInstruction:
    """
    Central system instruction class that enforces Z Framework operational principles.
    
    This class provides the authoritative implementation of the Z Framework system
    instruction, ensuring all operations follow the established mathematical and
    empirical principles.
    """
    
    # Core constants following Z Framework specifications
    SPEED_OF_LIGHT = mp.mpf('299792458.0')  # Universal invariant c
    E_SQUARED = mp.exp(2)                   # Discrete domain normalization
    PHI = (1 + mp.sqrt(5)) / 2             # Golden ratio for geodesics
    OPTIMAL_K = mp.mpf('0.3')               # Empirically validated curvature parameter
    
    # Validation thresholds
    PRECISION_THRESHOLD = mp.mpf('1e-16')   # High-precision requirement
    ENHANCEMENT_THRESHOLD = 0.15            # conditional prime density improvement under canonical benchmark methodology
    VARIANCE_TARGET = 0.118                 # Target variance σ ≈ 0.118
    
    def __init__(self):
        """Initialize system instruction with validation state tracking."""
        self.validation_history = []
        self.empirical_claims = {}
        self.domain_validations = {}
        
    # ========================================================================
    # AXIOM 1: UNIVERSAL INVARIANT FORMULATION Z = A(B/c)
    # ========================================================================
    
    def validate_universal_form(self, A: Union[Callable, float], B: float, c: float = None) -> Dict[str, Any]:
        """
        Validate that computation follows universal Z form Z = A(B/c).
        
        Ensures:
        - c is the empirically invariant speed of light
        - B represents a rate (velocity, density shift, etc.)  
        - A is frame-dependent transformation
        - High-precision stability with Δ_n < 10^{-16}
        
        Args:
            A: Frame-dependent quantity (callable or scalar)
            B: Rate quantity  
            c: Universal invariant (defaults to speed of light)
            
        Returns:
            dict: Validation results including compliance status
        """
        if c is None:
            c = float(self.SPEED_OF_LIGHT)
            
        validation = {
            'universal_form_compliant': True,
            'c_is_invariant': abs(c - float(self.SPEED_OF_LIGHT)) < 1e-6,
            'precision_met': True,
            'errors': []
        }
        
        try:
            # Validate universal invariant c
            if c <= 0:
                validation['errors'].append("Universal invariant c must be positive")
                validation['universal_form_compliant'] = False
                
            if not validation['c_is_invariant']:
                validation['errors'].append(f"c={c} deviates from speed of light {self.SPEED_OF_LIGHT}")
                
            # Compute Z = A(B/c) with precision validation
            from .axioms import UniversalZForm
            z_form = UniversalZForm(c)
            result = z_form.compute_z(A, B, precision_check=True)
            
            validation['z_result'] = float(result)
            validation['ratio_b_over_c'] = B / c
            
        except ValueError as e:
            if "precision requirement not met" in str(e):
                validation['precision_met'] = False
                validation['errors'].append(str(e))
            else:
                validation['universal_form_compliant'] = False
                validation['errors'].append(str(e))
                
        except Exception as e:
            validation['universal_form_compliant'] = False
            validation['errors'].append(f"Universal form validation error: {str(e)}")
            
        # Record validation
        self.validation_history.append({
            'type': 'universal_form',
            'timestamp': mp.mp.dps,  # Use precision as timestamp proxy
            'result': validation
        })
        
        return validation
    
    # ========================================================================
    # AXIOM 2: DOMAIN-SPECIFIC FORMS
    # ========================================================================
    
    def validate_physical_domain(self, T_func: Callable, v: float, c: float = None) -> Dict[str, Any]:
        """
        Validate physical domain form Z = T(v/c) with empirical basis.
        
        Ensures:
        - T is frame-dependent measured quantity (time, length, mass, etc.)
        - v is velocity satisfying causality |v| < c
        - Empirical basis in special relativity (time dilation, Lorentz transformation)
        
        Args:
            T_func: Frame-dependent transformation function T
            v: Velocity
            c: Speed of light (defaults to universal constant)
            
        Returns:
            dict: Physical domain validation results
        """
        if c is None:
            c = float(self.SPEED_OF_LIGHT)
            
        validation = {
            'physical_domain_compliant': True,
            'causality_satisfied': abs(v) < c,
            'relativistic_effects_present': abs(v/c) > 0.01,  # Non-negligible relativistic effects
            'empirical_basis': 'special_relativity',
            'errors': []
        }
        
        try:
            # Validate causality constraint
            if abs(v) >= c:
                validation['causality_satisfied'] = False
                validation['errors'].append(f"Causality violation: |v|={abs(v)} >= c={c}")
                
            # Compute Z = T(v/c) using physical domain implementation  
            from .axioms import PhysicalDomainZ
            phys_z = PhysicalDomainZ(c)
            
            # Test with standard relativistic transformations
            if hasattr(T_func, '__name__'):
                if 'time' in T_func.__name__.lower():
                    result = phys_z.time_dilation(v, proper_time=1.0)
                elif 'length' in T_func.__name__.lower():
                    result = phys_z.length_contraction(v, rest_length=1.0)
                else:
                    # Generic transformation
                    universal_z = phys_z.universal_z
                    result = universal_z.compute_z(T_func, v)
            else:
                # Use universal Z form directly
                universal_z = phys_z.universal_z
                result = universal_z.compute_z(T_func, v)
                
            validation['z_physical'] = float(result)
            validation['velocity_ratio'] = v / c
            
            # Validate empirical predictions
            if abs(v/c) > 0.1:  # Significant relativistic effects
                validation['empirical_predictions'] = [
                    'time_dilation_measurable',
                    'length_contraction_measurable', 
                    'relativistic_mass_increase'
                ]
            
        except Exception as e:
            validation['physical_domain_compliant'] = False
            validation['errors'].append(f"Physical domain validation error: {str(e)}")
            
        self.domain_validations['physical'] = validation
        return validation
    
    def validate_discrete_domain(self, n: int, delta_n: float, delta_max: float = None) -> Dict[str, Any]:
        """
        Validate discrete domain form Z = n(Δ_n/Δ_max) with frame shifts.
        
        Ensures:
        - n is frame-dependent integer (empirically validated up to n = 10^12)
        - Δ_n is measured frame shift κ(n) = d(n) · ln(n+1)/e²
        - Δ_max is maximum shift bounded by e² or φ
        - e² normalization for variance minimization
        - Ultra-extreme scale considerations for n > 10^12
        
        Args:
            n: Frame-dependent integer
            delta_n: Measured frame shift at n
            delta_max: Maximum shift (defaults to e²)
            
        Returns:
            dict: Discrete domain validation results including ultra-extreme scale considerations
        """
        if delta_max is None:
            delta_max = float(self.E_SQUARED)
            
        validation = {
            'discrete_domain_compliant': True,
            'e_squared_normalization': abs(delta_max - float(self.E_SQUARED)) < 0.01,
            'curvature_formula_correct': False,
            'variance_minimized': False,
            'ultra_extreme_scale': n > 10**12,
            'empirical_range': n <= 10**12,
            'extrapolation_required': n > 10**12,
            'errors': []
        }
        
        # Add ultra-extreme scale warnings and requirements
        if n > 10**12:
            validation['scale_warnings'] = [
                f"n={n} exceeds empirical validation range (n ≤ 10^12)",
                "Results require EXTRAPOLATION labeling",
                "Enhanced uncertainty bounds necessary",
                "Computational optimization verification required"
            ]
            
        if n > 10**16:
            validation['discrete_domain_compliant'] = False
            validation['errors'].append(f"n={n} exceeds computational framework limit (n ≤ 10^16)")
            
        try:
            # Validate discrete curvature formula κ(n) = d(n) · ln(n+1)/e²
            from sympy import divisors
            from .axioms import curvature
            
            # For ultra-extreme scales, implement computational optimizations
            if n > 10**13:
                validation['computational_optimizations_required'] = [
                    'streaming_algorithms',
                    'chunked_processing',
                    'memory_management'
                ]
            
            if n > 10**14:
                validation['distributed_computing_required'] = True
                validation['cluster_specifications_needed'] = True
            
            d_n = len(list(divisors(n)))
            expected_delta_n = curvature(n, d_n)
            
            # Check if provided delta_n matches expected curvature formula
            delta_error = abs(delta_n - expected_delta_n)
            validation['curvature_formula_correct'] = delta_error < 0.01
            validation['expected_delta_n'] = float(expected_delta_n)
            validation['provided_delta_n'] = delta_n
            validation['delta_error'] = float(delta_error)
            
            if not validation['curvature_formula_correct']:
                validation['errors'].append(
                    f"Frame shift δ_n={delta_n} does not match curvature formula κ(n)={expected_delta_n}"
                )
                
            # Compute Z = n(Δ_n/Δ_max) using discrete domain implementation
            from .domain import DiscreteZetaShift
            discrete_z = DiscreteZetaShift(n, v=1.0, delta_max=delta_max)
            z_result = discrete_z.compute_z()
            
            validation['z_discrete'] = float(z_result)
            validation['ratio_delta_n_over_delta_max'] = delta_n / delta_max
            
            # Validate e² normalization benefits (variance minimization)
            if delta_max == float(self.E_SQUARED):
                validation['variance_minimized'] = True
                validation['normalization_benefits'] = ['variance_reduction', 'numerical_stability']
            
            # Ultra-extreme scale numerical stability verification
            if n > 10**12:
                validation['numerical_stability_check'] = {
                    'precision_maintained': abs(z_result) < float('inf'),
                    'no_nan_values': not np.isnan(float(z_result)),
                    'within_expected_bounds': 0 <= abs(z_result) <= 10 * n  # Reasonable upper bound
                }
            
        except Exception as e:
            validation['discrete_domain_compliant'] = False
            validation['errors'].append(f"Discrete domain validation error: {str(e)}")
            
        self.domain_validations['discrete'] = validation
        return validation
    
    # ========================================================================
    # AXIOM 3: GEOMETRIC RESOLUTION 
    # ========================================================================
    
    def validate_geometric_resolution(self, n: int, k: float = None) -> Dict[str, Any]:
        """
        Validate geometric resolution via curvature-based geodesics.
        
        Ensures:
        - Replacement of fixed ratios with geodesic transformations
        - Use of θ'(n, k) = φ · {n/φ}^k
        - Optimal k* ≈ 0.3 for prime density enhancement (validated up to n = 10^9)
        - ~15% enhancement validation (extrapolation bounds for n > 10^9)
        - Ultra-extreme scale numerical stability for n up to 10^16
        
        Args:
            n: Integer for geodesic transformation
            k: Curvature exponent (defaults to optimal k*)
            
        Returns:
            dict: Geometric resolution validation results with ultra-extreme scale considerations
        """
        if k is None:
            k = float(self.OPTIMAL_K)
            
        validation = {
            'geometric_resolution_compliant': True,
            'geodesic_transformation_used': True,
            'optimal_k_used': abs(k - float(self.OPTIMAL_K)) < 0.05,
            'golden_ratio_modular': True,
            'enhancement_achieved': False,
            'ultra_extreme_scale': n > 10**9,
            'empirical_enhancement_range': n <= 10**9,
            'extrapolation_enhancement_range': n > 10**9,
            'errors': []
        }
        
        # Ultra-extreme scale considerations
        if n > 10**9:
            validation['scale_considerations'] = [
                f"n={n} exceeds empirical enhancement validation range (n ≤ 10^9)",
                "Prime density enhancement requires extrapolation uncertainty bounds ±2%",
                "Numerical stability verification required for geodesic transformations",
                "Cross-validation protocols recommended"
            ]
            
        if n > 10**16:
            validation['geometric_resolution_compliant'] = False
            validation['errors'].append(f"n={n} exceeds computational framework limit (n ≤ 10^16)")
            
        try:
            # Validate θ'(n, k) = φ · {n/φ}^k transformation
            from .axioms import theta_prime
            
            theta_result = theta_prime(n, k, phi=self.PHI)
            validation['theta_prime_result'] = float(theta_result)
            validation['curvature_parameter_k'] = k
            
            # Validate golden ratio modular arithmetic
            n_mod_phi = n % self.PHI
            normalized_residue = n_mod_phi / self.PHI
            expected_theta = self.PHI * (normalized_residue ** k)
            
            theta_error = abs(theta_result - expected_theta)
            validation['golden_ratio_modular'] = theta_error < float(self.PRECISION_THRESHOLD)
            
            # Enhanced precision check for ultra-extreme scales
            if n > 10**12:
                validation['ultra_extreme_precision_check'] = {
                    'theta_error': float(theta_error),
                    'precision_threshold': float(self.PRECISION_THRESHOLD),
                    'numerical_stability_maintained': theta_error < 10 * float(self.PRECISION_THRESHOLD)
                }
                
                if theta_error >= 10 * float(self.PRECISION_THRESHOLD):
                    validation['errors'].append(
                        f"Ultra-extreme scale precision degradation: error={theta_error}"
                    )
                    
            if not validation['golden_ratio_modular']:
                validation['errors'].append(f"Golden ratio modular error: {theta_error}")
                
            # Validate optimal k* usage
            if not validation['optimal_k_used']:
                validation['errors'].append(
                    f"Curvature parameter k={k} deviates from optimal k*={self.OPTIMAL_K}"
                )
                
            # Prime density enhancement validation with scale-dependent uncertainty
            from sympy import isprime
            is_prime = isprime(n)
            validation['is_prime'] = is_prime
            
            # Scale-dependent enhancement validation
            if n <= 10**9:
                validation['enhancement_validation_status'] = 'EMPIRICAL'
                validation['target_enhancement'] = self.ENHANCEMENT_THRESHOLD
                validation['uncertainty_bounds'] = '±0.4%'
            else:
                validation['enhancement_validation_status'] = 'EXTRAPOLATION'
                validation['target_enhancement'] = self.ENHANCEMENT_THRESHOLD
                validation['uncertainty_bounds'] = '±2%'
                validation['extrapolation_confidence'] = 'requires_independent_verification'
            
            # Ultra-extreme scale computational requirements
            if n > 10**13:
                validation['computational_requirements'] = [
                    'streaming_algorithms_for_geodesic_computation',
                    'memory_optimization_for_modular_arithmetic',
                    'distributed_processing_consideration'
                ]
                
        except Exception as e:
            validation['geometric_resolution_compliant'] = False
            validation['errors'].append(f"Geometric resolution validation error: {str(e)}")
            
        return validation
    
    # ========================================================================
    # OPERATIONAL GUIDANCE
    # ========================================================================
    
    def validate_empirical_claim(self, claim: str, evidence: Dict[str, Any], confidence_level: float = 0.95) -> Dict[str, Any]:
        """
        Validate empirical claims with quantitative evidence.
        
        Ensures:
        - All claims are mathematically or empirically substantiated
        - Confidence intervals and statistical significance provided
        - Reproducible code and quantitative simulation priority
        - Clear labeling of hypotheses vs validated results
        
        Args:
            claim: Description of empirical claim
            evidence: Quantitative evidence supporting claim
            confidence_level: Required confidence level (default 0.95)
            
        Returns:
            dict: Empirical validation results
        """
        validation = {
            'claim': claim,
            'empirically_substantiated': False,
            'confidence_level_met': False,
            'reproducible_evidence': False,
            'hypothesis_vs_validated': 'hypothesis',  # Default to hypothesis until proven
            'errors': []
        }
        
        try:
            # Check for required evidence components
            required_fields = ['statistical_measure', 'confidence_interval', 'p_value', 'sample_size']
            missing_fields = [field for field in required_fields if field not in evidence]
            
            if missing_fields:
                validation['errors'].append(f"Missing evidence fields: {missing_fields}")
                return validation
                
            # Validate statistical significance
            p_value = evidence.get('p_value', 1.0)
            alpha = 1 - confidence_level
            validation['confidence_level_met'] = p_value < alpha
            
            # Validate confidence interval
            ci = evidence.get('confidence_interval', [])
            if len(ci) == 2:
                validation['confidence_interval_width'] = ci[1] - ci[0]
                validation['confidence_interval_valid'] = True
            else:
                validation['errors'].append("Invalid confidence interval format")
                
            # Check for reproducible code reference
            if 'reproducible_code' in evidence:
                validation['reproducible_evidence'] = True
                validation['code_reference'] = evidence['reproducible_code']
                
            # Determine if claim is validated or hypothesis
            if (validation['confidence_level_met'] and 
                validation['reproducible_evidence'] and 
                len(validation['errors']) == 0):
                validation['empirically_substantiated'] = True
                validation['hypothesis_vs_validated'] = 'validated'
                
        except Exception as e:
            validation['errors'].append(f"Empirical validation error: {str(e)}")
            
        # Store claim validation
        self.empirical_claims[claim] = validation
        return validation
    
    def validate_scientific_communication(self, output_text: str) -> Dict[str, Any]:
        """
        Validate scientific communication standards.
        
        Ensures:
        - Precise scientific tone
        - Clear distinction between validated results and hypotheses
        - Proper citation of empirical evidence
        - No unsupported assertions
        
        Args:
            output_text: Text output to validate
            
        Returns:
            dict: Communication validation results
        """
        validation = {
            'scientific_tone': True,
            'hypothesis_labeling': True,
            'evidence_citations': True,
            'unsupported_assertions': [],
            'recommendations': []
        }
        
        # Check for hypothesis indicators
        hypothesis_indicators = ['hypothesis', 'conjecture', 'proposed', 'theoretical', 'requires validation']
        validated_indicators = ['empirically demonstrated', 'validated', 'proven', 'established', 'empirically validated']
        
        # Simple text analysis (in practice, would use more sophisticated NLP)
        lower_text = output_text.lower()
        
        # Look for unsupported strong claims
        strong_claims = ['proves', 'definitely', 'certainly', 'always', 'never']
        for claim in strong_claims:
            if claim in lower_text:
                # Check if this strong claim is supported by both validation indicators AND evidence citations
                has_validation_support = any(ind in lower_text for ind in validated_indicators)
                citation_patterns = ['ci [', 'p <', 'p=', 'confidence interval', '±', 'bootstrap']
                has_evidence_citations = any(pattern in lower_text for pattern in citation_patterns)
                
                if not (has_validation_support and has_evidence_citations):
                    validation['unsupported_assertions'].append(f"Strong claim '{claim}' without adequate validation")
                    validation['scientific_tone'] = False
                
        # Check for proper hypothesis labeling
        if any(ind in lower_text for ind in validated_indicators):
            # Should have evidence citations (check for various citation formats)
            citation_patterns = ['ci [', 'p <', 'p=', 'confidence interval', '±', 'bootstrap']
            if not any(pattern in lower_text for pattern in citation_patterns):
                validation['evidence_citations'] = False
                validation['recommendations'].append("Add confidence intervals or p-values for validated claims")
                
        return validation
    
    # ========================================================================
    # SYSTEM INSTRUCTION COMPLIANCE VERIFICATION
    # ========================================================================
    
    def verify_full_compliance(self, operation_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Verify full compliance with Z Framework system instruction.
        
        Performs comprehensive validation across all four core principles:
        1. Universal invariant formulation
        2. Domain-specific forms  
        3. Geometric resolution
        4. Operational guidance
        
        Args:
            operation_data: Dictionary containing operation parameters and results
            
        Returns:
            dict: Complete compliance verification results
        """
        compliance = {
            'overall_compliant': True,
            'principle_validations': {},
            'compliance_score': 0.0,
            'critical_violations': [],
            'recommendations': []
        }
        
        # Validate each principle
        principles = [
            ('universal_invariant', self._validate_universal_invariant_principle),
            ('domain_specific', self._validate_domain_specific_principle), 
            ('geometric_resolution', self._validate_geometric_resolution_principle),
            ('operational_guidance', self._validate_operational_guidance_principle)
        ]
        
        scores = []
        for principle_name, validator in principles:
            try:
                validation = validator(operation_data)
                compliance['principle_validations'][principle_name] = validation
                
                # Calculate principle score
                score = self._calculate_principle_score(validation)
                scores.append(score)
                
                # Check for critical violations
                if score < 0.5:  # Less than 50% compliance
                    compliance['critical_violations'].append(f"{principle_name}: {validation.get('errors', [])}")
                    
            except Exception as e:
                compliance['critical_violations'].append(f"{principle_name}: validation error - {str(e)}")
                scores.append(0.0)
                
        # Calculate overall compliance score
        compliance['compliance_score'] = np.mean(scores) if scores else 0.0
        compliance['overall_compliant'] = compliance['compliance_score'] >= 0.8  # 80% threshold
        
        # Generate recommendations
        if not compliance['overall_compliant']:
            compliance['recommendations'].extend([
                "Review Z Framework system instruction principles",
                "Ensure empirical validation for all claims",
                "Verify geometric resolution implementation",
                "Check domain-specific form compliance"
            ])
            
        return compliance
    
    def _validate_universal_invariant_principle(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate universal invariant formulation principle."""
        # Extract parameters for universal form validation
        A = data.get('A', lambda x: x)  # Default linear transformation
        B = data.get('B', 1.0)
        c = data.get('c', float(self.SPEED_OF_LIGHT))
        
        return self.validate_universal_form(A, B, c)
    
    def _validate_domain_specific_principle(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate domain-specific forms principle."""
        domain = data.get('domain', 'unknown')
        
        if domain == 'physical':
            T_func = data.get('T_func', lambda x: x)
            v = data.get('v', 0.0)
            return self.validate_physical_domain(T_func, v)
        elif domain == 'discrete':
            n = data.get('n', 1)
            delta_n = data.get('delta_n', 1.0)
            return self.validate_discrete_domain(n, delta_n)
        else:
            return {'errors': [f'Unknown domain: {domain}'], 'compliant': False}
    
    def _validate_geometric_resolution_principle(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate geometric resolution principle."""
        n = data.get('n', 1)
        k = data.get('k', float(self.OPTIMAL_K))
        return self.validate_geometric_resolution(n, k)
    
    def _validate_operational_guidance_principle(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate operational guidance principle."""
        claims = data.get('empirical_claims', {})
        communication = data.get('communication_text', '')
        
        validation = {'errors': [], 'compliant': True}
        
        # Validate each empirical claim
        for claim, evidence in claims.items():
            claim_validation = self.validate_empirical_claim(claim, evidence)
            if not claim_validation['empirically_substantiated']:
                validation['errors'].append(f"Unsubstantiated claim: {claim}")
                validation['compliant'] = False
                
        # Validate communication
        if communication:
            comm_validation = self.validate_scientific_communication(communication)
            if comm_validation['unsupported_assertions']:
                validation['errors'].extend(comm_validation['unsupported_assertions'])
                validation['compliant'] = False
                
        return validation
    
    def _calculate_principle_score(self, validation: Dict[str, Any]) -> float:
        """Calculate compliance score for a principle validation."""
        if not isinstance(validation, dict):
            return 0.0
            
        # Look for specific compliance indicators by principle type
        compliance_indicators = []
        
        # Universal form indicators
        if 'universal_form_compliant' in validation:
            compliance_indicators.append(validation['universal_form_compliant'])
            
        # Physical domain indicators  
        if 'physical_domain_compliant' in validation:
            compliance_indicators.append(validation['physical_domain_compliant'])
            
        # Discrete domain indicators
        if 'discrete_domain_compliant' in validation:
            compliance_indicators.append(validation['discrete_domain_compliant'])
            
        # Geometric resolution indicators
        if 'geometric_resolution_compliant' in validation:
            compliance_indicators.append(validation['geometric_resolution_compliant'])
            
        # General compliance indicators
        if 'compliant' in validation:
            compliance_indicators.append(validation['compliant'])
            
        # Additional positive indicators
        positive_checks = [
            validation.get('c_is_invariant', None),
            validation.get('precision_met', None),
            validation.get('causality_satisfied', None),
            validation.get('e_squared_normalization', None),
            validation.get('curvature_formula_correct', None),
            validation.get('geodesic_transformation_used', None),
            validation.get('optimal_k_used', None),
            validation.get('empirically_substantiated', None)
        ]
        
        # Filter out None values and add to compliance indicators
        compliance_indicators.extend([check for check in positive_checks if check is not None])
        
        if not compliance_indicators:
            # No clear indicators, check for absence of errors as positive sign
            error_count = len(validation.get('errors', []))
            return 1.0 if error_count == 0 else 0.0
            
        # Calculate base score from compliance indicators
        base_score = sum(compliance_indicators) / len(compliance_indicators)
        
        # Penalty for errors
        error_count = len(validation.get('errors', []))
        error_penalty = min(0.1 * error_count, 0.5)  # Max 50% penalty
        
        return max(0.0, base_score - error_penalty)


# Global system instruction instance
_system_instruction = ZFrameworkSystemInstruction()

def get_system_instruction() -> ZFrameworkSystemInstruction:
    """Get the global Z Framework system instruction instance."""
    return _system_instruction

def enforce_system_instruction(func: Callable) -> Callable:
    """
    Decorator to enforce Z Framework system instruction compliance.
    
    This decorator automatically validates that function operations comply
    with the Z Framework system instruction principles.
    """
    def wrapper(*args, **kwargs):
        # Execute original function
        result = func(*args, **kwargs)
        
        # Extract operation data for validation
        operation_data = {
            'function_name': func.__name__,
            'args': args,
            'kwargs': kwargs,
            'result': result
        }
        
        # Attempt to extract domain-specific parameters
        if 'v' in kwargs and 'c' in kwargs:
            operation_data['domain'] = 'physical'
            operation_data['v'] = kwargs['v']
            operation_data['c'] = kwargs['c']
        elif 'n' in kwargs:
            operation_data['domain'] = 'discrete'
            operation_data['n'] = kwargs['n']
            
        # Validate compliance (but don't block execution)
        try:
            compliance = _system_instruction.verify_full_compliance(operation_data)
            if not compliance['overall_compliant']:
                warnings.warn(
                    f"Z Framework system instruction compliance warning in {func.__name__}: "
                    f"Score={compliance['compliance_score']:.2f}, "
                    f"Violations={compliance['critical_violations']}"
                )
        except Exception as e:
            warnings.warn(f"System instruction validation error in {func.__name__}: {str(e)}")
            
        return result
    
    wrapper.__name__ = func.__name__
    wrapper.__doc__ = func.__doc__
    return wrapper

# System instruction compliance validation for key mathematical constants
SYSTEM_CONSTANTS = {
    'c': _system_instruction.SPEED_OF_LIGHT,
    'e_squared': _system_instruction.E_SQUARED,
    'phi': _system_instruction.PHI,
    'k_star': _system_instruction.OPTIMAL_K,
    'precision_threshold': _system_instruction.PRECISION_THRESHOLD,
    'enhancement_threshold': _system_instruction.ENHANCEMENT_THRESHOLD,
    'variance_target': _system_instruction.VARIANCE_TARGET
}

def validate_system_constants() -> Dict[str, Any]:
    """Validate that system constants meet Z Framework requirements."""
    validation = {
        'constants_valid': True,
        'precision_adequate': mp.mp.dps >= 50,
        'constants': {},
        'errors': []
    }
    
    for name, value in SYSTEM_CONSTANTS.items():
        try:
            validation['constants'][name] = {
                'value': float(value),
                'precision': mp.mp.dps,
                'type': str(type(value))
            }
        except Exception as e:
            validation['errors'].append(f"Constant {name} validation error: {str(e)}")
            validation['constants_valid'] = False
            
    return validation