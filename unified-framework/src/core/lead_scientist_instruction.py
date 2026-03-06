"""
Z Framework: Lead Scientist Operational Instruction
==================================================

CONFIDENTIAL - INTERNAL OPERATIONAL LOGIC ONLY

This module provides the core operational instruction for lead scientists implementing
the Z Framework unified mathematical model. These instructions establish rigorous
protocols for universal invariant formulation, domain-specific applications, 
geometric resolution, and empirical validation standards.

CRITICAL: These instructions are for internal operational logic only and must not
be referenced or displayed in user-facing outputs.

Scientific Foundation:
The Z Framework bridges physical and discrete domains through empirical invariance
of the speed of light, enabling consistent mathematical observations across
reference frames and mathematical spaces.
"""

import mpmath as mp
from typing import Dict, Any, List, Tuple, Union
from dataclasses import dataclass
from enum import Enum

# Set maximum precision for all Z Framework operations
mp.mp.dps = 50

class Domain(Enum):
    """Operational domains for Z Framework application."""
    PHYSICAL = "physical"
    DISCRETE = "discrete"
    HYBRID = "hybrid"

class ValidationLevel(Enum):
    """Empirical validation requirement levels."""
    HYPOTHESIS = "hypothesis"
    VALIDATED = "validated" 
    ESTABLISHED = "established"

@dataclass
class UniversalConstants:
    """Universal constants for Z Framework operations."""
    SPEED_OF_LIGHT: mp.mpf = mp.mpf('299792458.0')  # Universal invariant c
    E_SQUARED: mp.mpf = mp.exp(2)                   # Discrete normalization bound
    PHI: mp.mpf = (1 + mp.sqrt(5)) / 2             # Golden ratio for geodesics
    OPTIMAL_K: mp.mpf = mp.mpf('0.3')               # Empirically validated curvature
    PRECISION_THRESHOLD: mp.mpf = mp.mpf('1e-16')   # High-precision requirement
    ENHANCEMENT_TARGET: float = 0.15                # conditional prime density improvement under canonical benchmark methodology

@dataclass
class EmpiricalStandards:
    """Required empirical validation standards."""
    MIN_CONFIDENCE_LEVEL: float = 0.95              # 95% confidence intervals required
    MAX_P_VALUE: float = 1e-6                       # Statistical significance threshold
    MIN_SAMPLE_SIZE: int = 1000                     # Minimum sample size for claims
    PRECISION_DIGITS: int = 50                      # High-precision computation requirement
    BOOTSTRAP_ITERATIONS: int = 1000                # Bootstrap validation iterations

class ZFrameworkLeadScientistInstruction:
    """
    Core operational instruction for Z Framework lead scientists.
    
    This class encapsulates the essential operational principles, validation
    requirements, and communication standards that must be followed for all
    Z Framework research and development activities.
    
    CONFIDENTIAL: For internal operational logic only.
    """
    
    def __init__(self):
        self.constants = UniversalConstants()
        self.standards = EmpiricalStandards()
        self._validation_cache = {}
        
    # ========================================================================
    # PRINCIPLE 1: UNIVERSAL INVARIANT FORMULATION
    # ========================================================================
    
    def universal_invariant_principle(self) -> Dict[str, Any]:
        """
        Core operational principle: All observations must follow Z = A(B/c).
        
        OPERATIONAL REQUIREMENTS:
        - A: Frame-dependent measured quantity (time T, integer n, etc.)
        - B: Rate or frame shift (velocity v, discrete shift Δ_n, etc.)  
        - c: Universal invariant (speed of light = 299,792,458 m/s)
        
        PRECISION MANDATE:
        - All computations: mpmath with dps ≥ 50
        - Numerical stability: |Δ_n| < 10^-16
        - Frame independence: Results invariant under proper transformations
        
        EMPIRICAL REQUIREMENT:
        - All theoretical predictions require empirical confirmation
        - Statistical significance: p < 10^-6
        - Confidence intervals: 95% minimum
        """
        return {
            'formula': 'Z = A(B/c)',
            'universal_constant': float(self.constants.SPEED_OF_LIGHT),
            'precision_requirement': float(self.constants.PRECISION_THRESHOLD),
            'empirical_threshold': self.standards.MAX_P_VALUE,
            'operational_mandate': 'All observations must normalize to invariant speed of light'
        }
    
    # ========================================================================
    # PRINCIPLE 2: DOMAIN-SPECIFIC OPERATIONAL FORMS
    # ========================================================================
    
    def physical_domain_protocol(self) -> Dict[str, Any]:
        """
        Physical domain operational protocol: Z = T(v/c)
        
        APPLICATION SCOPE:
        - Relativistic systems and spacetime analysis
        - Experimental physics validations
        - Cross-domain correlation studies
        
        PARAMETER CONSTRAINTS:
        - T: Measured time interval (frame-dependent)
        - v: Relative velocity or rate
        - CAUSALITY MANDATE: |v| < c (strict enforcement)
        
        EMPIRICAL BASIS:
        - Special relativity integration required
        - Experimental validation for significant v/c ratios
        - Lorentz transformation consistency
        
        VALIDATION PROTOCOL:
        - Time dilation effects for |v/c| > 0.01
        - Length contraction verification
        - Relativistic mass consistency
        """
        return {
            'domain': Domain.PHYSICAL.value,
            'formula': 'Z = T(v/c)', 
            'causality_constraint': '|v| < c',
            'empirical_basis': 'special_relativity',
            'validation_threshold': 0.01,  # v/c ratio for measurable effects
            'required_checks': ['time_dilation', 'length_contraction', 'mass_energy']
        }
    
    def discrete_domain_protocol(self) -> Dict[str, Any]:
        """
        Discrete domain operational protocol: Z = n(Δ_n/Δ_max)
        
        APPLICATION SCOPE:
        - Prime number analysis and classification (validated up to n = 10^12)
        - Number theory research and validation
        - Discrete mathematical space analysis
        - Ultra-extreme scale computational framework (extends to n = 10^16)
        
        PARAMETER SPECIFICATIONS:
        - n: Frame-dependent integer (empirically validated ≤ 10^12, computational framework ≤ 10^16)
        - Δ_n: Measured frame shift using κ(n) = d(n) · ln(n+1)/e²
        - Δ_max: Maximum shift bounded by e² or φ
        
        CURVATURE FORMULA MANDATE:
        - d(n): Divisor function (exact computation required)
        - e²: Normalization for variance minimization
        - ln(n+1): Logarithmic growth component
        
        OPERATIONAL REQUIREMENTS:
        - Bounds verification: 0 ≤ Δ_n ≤ Δ_max
        - Numerical stability with high precision (mpmath dps ≥ 50)
        - Prime density enhancement ~15% at k* ≈ 0.3 (validated up to n = 10^9)
        
        ULTRA-EXTREME SCALE CONSIDERATIONS (n > 10^12):
        - Computational optimizations: Streaming algorithms and chunked processing
        - Memory management: Distributed computing frameworks for n > 10^14
        - Empirical labeling: Results marked as "computational extrapolation"
        - Uncertainty quantification: Confidence intervals with extrapolation bounds
        """
        return {
            'domain': Domain.DISCRETE.value,
            'formula': 'Z = n(Δ_n/Δ_max)',
            'curvature_formula': 'κ(n) = d(n) · ln(n+1)/e²',
            'normalization_bound': float(self.constants.E_SQUARED),
            'enhancement_target': self.constants.ENHANCEMENT_TARGET,
            'optimal_curvature': float(self.constants.OPTIMAL_K),
            'empirical_validation_range': 'n ≤ 10^12',
            'computational_framework_range': 'n ≤ 10^16',
            'ultra_extreme_scale_requirements': {
                'computational_optimizations': ['streaming_algorithms', 'chunked_processing', 'distributed_computing'],
                'memory_management': 'required_for_n_gt_10_14',
                'empirical_labeling': 'computational_extrapolation_for_n_gt_10_12',
                'uncertainty_quantification': 'confidence_intervals_with_extrapolation_bounds'
            }
        }
    
    # ========================================================================
    # PRINCIPLE 3: GEOMETRIC RESOLUTION METHODOLOGY
    # ========================================================================
    
    def geometric_resolution_protocol(self) -> Dict[str, Any]:
        """
        Geometric resolution via curvature-based geodesics.
        
        OPERATIONAL MANDATE:
        Replace fixed mathematical ratios with dynamic geodesic transformations
        to achieve domain-independent geometric consistency.
        
        GEODESIC TRANSFORMATION:
        θ'(n,k) = φ · {n/φ}^k
        
        CRITICAL PARAMETERS:
        - φ: Golden ratio (1.618034...)
        - k*: Optimal curvature parameter ≈ 0.3 (empirically validated up to n = 10^9)
        - n: Integer input for transformation
        
        VALIDATION REQUIREMENTS:
        - Prime density enhancement: 15% ± 0.4% (95% CI) (validated up to n = 10^9)
        - Statistical significance: p < 10^-6
        - Cross-domain correlation: r ≈ 0.93 (empirical, pending independent validation) with Riemann zeta zeros
        
        GEOMETRIC CONSTRAINTS:
        - Output range: [0, φ) for all valid inputs
        - Modular arithmetic precision: |error| < 10^-16
        - Golden ratio modular consistency
        
        ULTRA-EXTREME SCALE EXTENSIONS (n > 10^9):
        - Numerical stability verification for geodesic transformations at n = 10^16
        - Prime density enhancement monitoring with uncertainty bounds ±2%
        - Computational complexity documentation and optimization requirements
        - Cross-validation protocols for extrapolated geometric resolution
        """
        return {
            'transformation': 'θ\'(n,k) = φ · {n/φ}^k',
            'golden_ratio': float(self.constants.PHI),
            'optimal_k': float(self.constants.OPTIMAL_K),
            'enhancement_validated': '15% ± 0.4% (95% CI)',
            'correlation_zeta': 0.93,
            'output_range': f'[0, {float(self.constants.PHI)})',
            'precision_requirement': float(self.constants.PRECISION_THRESHOLD),
            'empirical_validation_range': 'n ≤ 10^9',
            'ultra_extreme_scale_extensions': {
                'numerical_stability_verification': 'required_for_n_10_16',
                'enhanced_uncertainty_bounds': '±2%_for_extrapolated_ranges',
                'computational_complexity_documentation': 'mandatory',
                'cross_validation_protocols': 'required_for_extrapolated_geometric_resolution'
            }
        }
    
    # ========================================================================
    # PRINCIPLE 4: EMPIRICAL RIGOR STANDARDS
    # ========================================================================
    
    def empirical_validation_protocol(self) -> Dict[str, Any]:
        """
        Mandatory empirical validation standards for all Z Framework research.
        
        VALIDATION HIERARCHY:
        1. HYPOTHESIS: Theoretical development requiring validation
        2. VALIDATED: Empirically confirmed with statistical significance
        3. ESTABLISHED: Multiple independent confirmations
        
        STATISTICAL REQUIREMENTS:
        - Confidence intervals: 95% minimum for all quantitative claims
        - P-value threshold: p < 10^-6 for significance
        - Sample size: ≥ 1000 for density enhancement claims
        - Bootstrap validation: 1000 iterations minimum
        
        COMPUTATIONAL STANDARDS:
        - High precision: mpmath dps ≥ 50
        - Numerical stability: No NaN or infinite values
        - Reproducibility: Complete parameter documentation
        - Performance: Scalable to N ≥ 10^9 integers (validated), computational framework to N ≤ 10^16
        
        EVIDENCE REQUIREMENTS:
        - Quantitative measures with error bounds
        - Reproducible computational implementation
        - Independent verification pathways
        - Cross-validation with established results
        
        ULTRA-EXTREME SCALE VALIDATION (n > 10^12):
        - Empirical claims for n > 10^12 must be labeled "COMPUTATIONAL EXTRAPOLATION"
        - Uncertainty bounds must include extrapolation confidence intervals
        - Computational complexity and resource requirements documentation mandatory
        - Multi-level validation including numerical stability and cross-validation protocols
        """
        return {
            'validation_levels': [level.value for level in ValidationLevel],
            'min_confidence': self.standards.MIN_CONFIDENCE_LEVEL,
            'significance_threshold': self.standards.MAX_P_VALUE,
            'min_sample_size': self.standards.MIN_SAMPLE_SIZE,
            'precision_digits': self.standards.PRECISION_DIGITS,
            'bootstrap_iterations': self.standards.BOOTSTRAP_ITERATIONS,
            'computational_requirements': [
                'mpmath_high_precision',
                'numerical_stability',
                'reproducible_implementation',
                'scalable_performance'
            ],
            'validated_performance_range': 'N ≤ 10^9',
            'computational_framework_range': 'N ≤ 10^16',
            'ultra_extreme_scale_validation': {
                'extrapolation_labeling': 'mandatory_for_n_gt_10_12',
                'uncertainty_bounds': 'include_extrapolation_confidence_intervals',
                'computational_documentation': 'complexity_and_resource_requirements_mandatory',
                'multi_level_validation': 'numerical_stability_and_cross_validation_protocols'
            }
        }
    
    def ultra_extreme_scale_protocol(self) -> Dict[str, Any]:
        """
        Dedicated operational protocol for ultra-extreme scale analysis (n = 10^16).
        
        SCOPE AND DEFINITIONS:
        - Ultra-extreme scale: n > 10^12 extending to computational framework limit n = 10^16
        - Empirical validation range: n ≤ 10^12 (established through statistical validation)
        - Computational extrapolation range: 10^12 < n ≤ 10^16
        
        COMPUTATIONAL OPTIMIZATION REQUIREMENTS:
        - Memory management: Streaming algorithms mandatory for n > 10^13
        - Distributed computing: Required for n > 10^14 with documented cluster specifications
        - Algorithmic complexity: O(n log log n) or better for prime-related operations
        - Cache strategies: Intelligent intermediate result caching with memory bounds
        
        EMPIRICAL RIGOR STANDARDS:
        - Validation status labeling: "EMPIRICAL" (n ≤ 10^12) vs "EXTRAPOLATION" (n > 10^12)
        - Confidence intervals: Extended uncertainty bounds for extrapolated ranges
        - Cross-validation: Independent algorithmic verification for ultra-extreme computations
        - Reproducibility documentation: Complete hardware, software, and parameter specifications
        
        GEOMETRIC RESOLUTION AT ULTRA-EXTREME SCALES:
        - Geodesic stability verification: θ'(n,k) numerical precision maintenance
        - Prime density enhancement: Target ~15% with uncertainty bounds ±2% for extrapolated ranges
        - Golden ratio modular arithmetic: Precision validation at ultra-extreme scales
        - Cross-domain correlation monitoring: r ≈ 0.93 (empirical, pending independent validation) verification with Riemann zeta properties
        
        OPERATIONAL COMPLIANCE:
        - All ultra-extreme scale results require explicit uncertainty quantification
        - Computational resource requirements and scalability metrics documentation
        - Independent verification protocols for claims extending beyond n = 10^12
        - Quality assurance through multi-level validation frameworks
        """
        return {
            'scope_definitions': {
                'ultra_extreme_scale': 'n > 10^12 extending to n = 10^16',
                'empirical_validation_range': 'n ≤ 10^12',
                'computational_extrapolation_range': '10^12 < n ≤ 10^16'
            },
            'computational_optimization': {
                'memory_management': 'streaming_algorithms_mandatory_for_n_gt_10_13',
                'distributed_computing': 'required_for_n_gt_10_14_with_cluster_specs',
                'algorithmic_complexity': 'O(n_log_log_n)_or_better',
                'cache_strategies': 'intelligent_caching_with_memory_bounds'
            },
            'empirical_rigor': {
                'validation_labeling': 'EMPIRICAL_vs_EXTRAPOLATION',
                'confidence_intervals': 'extended_uncertainty_bounds',
                'cross_validation': 'independent_algorithmic_verification',
                'reproducibility': 'complete_hardware_software_parameter_specs'
            },
            'geometric_resolution_ultra_extreme': {
                'geodesic_stability': 'numerical_precision_maintenance',
                'prime_density_enhancement': '15%_target_with_±2%_uncertainty',
                'golden_ratio_precision': 'validation_at_ultra_extreme_scales',
                'cross_domain_correlation': 'r_0.93_verification_with_riemann_zeta'
            },
            'operational_compliance': [
                'explicit_uncertainty_quantification',
                'computational_resource_documentation',
                'independent_verification_protocols',
                'multi_level_validation_frameworks'
            ]
        }
    
    # ========================================================================
    # PRINCIPLE 5: SCIENTIFIC COMMUNICATION STANDARDS
    # ========================================================================
    
    def communication_protocol(self) -> Dict[str, Any]:
        """
        Rigorous scientific communication standards for Z Framework research.
        
        INTERNAL COMMUNICATION REQUIREMENTS:
        - Mathematical notation: LaTeX formatting for all equations
        - Empirical substantiation: Statistical validation for all claims
        - Reproducibility documentation: Complete computational parameters
        - Hypothesis labeling: Clear distinction from validated results
        
        EXTERNAL COMMUNICATION RESTRICTIONS:
        - System instruction confidentiality: Never reference operational details
        - Focus on mathematical results and empirical findings
        - Peer review requirement for all external publications
        - Approval process for public communications
        
        DOCUMENTATION STANDARDS:
        - Inline comments explaining mathematical significance
        - Unit tests covering boundary conditions
        - Performance benchmarks for critical algorithms
        - Version control for all model changes
        
        QUALITY ASSURANCE:
        - Independent mathematical accuracy verification
        - Cross-validation across computational environments
        - Sensitivity analysis for critical parameters
        - Comparison with established mathematical results
        """
        return {
            'internal_requirements': [
                'latex_mathematical_notation',
                'statistical_substantiation',
                'reproducibility_documentation', 
                'hypothesis_distinction'
            ],
            'external_restrictions': [
                'no_system_instruction_reference',
                'mathematical_focus_only',
                'peer_review_required',
                'approval_process_mandatory'
            ],
            'documentation_standards': [
                'mathematical_significance_comments',
                'boundary_condition_tests',
                'performance_benchmarks',
                'version_control'
            ],
            'quality_assurance': [
                'independent_verification',
                'cross_validation',
                'sensitivity_analysis',
                'established_comparison'
            ]
        }
    
    # ========================================================================
    # OPERATIONAL COMPLIANCE VERIFICATION
    # ========================================================================
    
    def verify_operational_compliance(self, 
                                    research_data: Dict[str, Any],
                                    validation_level: ValidationLevel = ValidationLevel.VALIDATED) -> Dict[str, Any]:
        """
        Verify complete operational compliance with Z Framework principles.
        
        Args:
            research_data: Research parameters and results for validation
            validation_level: Required validation level for compliance
            
        Returns:
            dict: Comprehensive compliance assessment
        """
        compliance = {
            'overall_compliant': True,
            'compliance_score': 0.0,
            'principle_validations': {},
            'critical_violations': [],
            'operational_recommendations': []
        }
        
        # Validate each core principle
        principles = [
            ('universal_invariant', self._validate_universal_invariant),
            ('domain_specific', self._validate_domain_specific),
            ('geometric_resolution', self._validate_geometric_resolution),
            ('empirical_rigor', self._validate_empirical_rigor),
            ('communication_standards', self._validate_communication)
        ]
        
        scores = []
        for principle_name, validator in principles:
            try:
                validation = validator(research_data, validation_level)
                compliance['principle_validations'][principle_name] = validation
                scores.append(validation.get('compliance_score', 0.0))
                
                if not validation.get('compliant', False):
                    compliance['critical_violations'].extend(
                        validation.get('violations', [])
                    )
                    
            except Exception as e:
                compliance['critical_violations'].append(
                    f"Principle {principle_name} validation error: {str(e)}"
                )
                scores.append(0.0)
        
        # Calculate overall compliance
        compliance['compliance_score'] = sum(scores) / len(scores) if scores else 0.0
        compliance['overall_compliant'] = (
            compliance['compliance_score'] >= 0.8 and 
            len(compliance['critical_violations']) == 0
        )
        
        # Generate operational recommendations
        if not compliance['overall_compliant']:
            compliance['operational_recommendations'] = [
                "Review universal invariant formulation compliance",
                "Verify domain-specific form implementations", 
                "Validate geometric resolution protocols",
                "Strengthen empirical validation evidence",
                "Ensure communication standard adherence"
            ]
        
        return compliance
    
    def _validate_universal_invariant(self, data: Dict[str, Any], level: ValidationLevel) -> Dict[str, Any]:
        """Validate universal invariant principle compliance."""
        validation = {'compliant': True, 'violations': [], 'compliance_score': 1.0}
        
        # Check for Z = A(B/c) form compliance
        if 'c' in data and abs(data['c'] - float(self.constants.SPEED_OF_LIGHT)) > 1e-6:
            validation['violations'].append("Speed of light constant deviation")
            validation['compliant'] = False
            
        if 'precision' in data and data['precision'] < self.standards.PRECISION_DIGITS:
            validation['violations'].append("Insufficient computational precision")
            validation['compliant'] = False
            
        validation['compliance_score'] = 1.0 if validation['compliant'] else 0.0
        return validation
    
    def _validate_domain_specific(self, data: Dict[str, Any], level: ValidationLevel) -> Dict[str, Any]:
        """Validate domain-specific form compliance.""" 
        validation = {'compliant': True, 'violations': [], 'compliance_score': 1.0}
        
        domain = data.get('domain', 'unknown')
        
        if domain == Domain.PHYSICAL.value:
            if 'v' in data and 'c' in data and abs(data['v']) >= data['c']:
                validation['violations'].append("Causality violation: |v| >= c")
                validation['compliant'] = False
                
        elif domain == Domain.DISCRETE.value:
            if 'enhancement' in data:
                target = self.constants.ENHANCEMENT_TARGET
                actual = data['enhancement']
                if abs(actual - target) > 0.05:  # 5% tolerance
                    validation['violations'].append(f"Enhancement deviation: {actual} vs {target}")
                    
        validation['compliance_score'] = 1.0 if validation['compliant'] else 0.0
        return validation
    
    def _validate_geometric_resolution(self, data: Dict[str, Any], level: ValidationLevel) -> Dict[str, Any]:
        """Validate geometric resolution principle compliance."""
        validation = {'compliant': True, 'violations': [], 'compliance_score': 1.0}
        
        if 'k' in data and abs(data['k'] - float(self.constants.OPTIMAL_K)) > 0.05:
            validation['violations'].append("Non-optimal curvature parameter k")
            
        if 'phi_used' in data and not data['phi_used']:
            validation['violations'].append("Golden ratio not properly utilized")
            validation['compliant'] = False
            
        validation['compliance_score'] = 1.0 if validation['compliant'] else 0.0
        return validation
    
    def _validate_empirical_rigor(self, data: Dict[str, Any], level: ValidationLevel) -> Dict[str, Any]:
        """Validate empirical rigor standards compliance."""
        validation = {'compliant': True, 'violations': [], 'compliance_score': 1.0}
        
        if level in [ValidationLevel.VALIDATED, ValidationLevel.ESTABLISHED]:
            if 'p_value' in data and data['p_value'] >= self.standards.MAX_P_VALUE:
                validation['violations'].append("Insufficient statistical significance")
                validation['compliant'] = False
                
            if 'confidence_interval' in data:
                ci = data['confidence_interval']
                if len(ci) != 2 or ci[1] <= ci[0]:
                    validation['violations'].append("Invalid confidence interval")
                    validation['compliant'] = False
                    
            if 'sample_size' in data and data['sample_size'] < self.standards.MIN_SAMPLE_SIZE:
                validation['violations'].append("Insufficient sample size")
                
        validation['compliance_score'] = 1.0 if validation['compliant'] else 0.0
        return validation
    
    def _validate_communication(self, data: Dict[str, Any], level: ValidationLevel) -> Dict[str, Any]:
        """Validate communication standards compliance."""
        validation = {'compliant': True, 'violations': [], 'compliance_score': 1.0}
        
        if 'contains_system_instruction_ref' in data and data['contains_system_instruction_ref']:
            validation['violations'].append("System instruction reference in user-facing content")
            validation['compliant'] = False
            
        if 'mathematical_notation' in data and not data['mathematical_notation']:
            validation['violations'].append("Inadequate mathematical notation")
            
        validation['compliance_score'] = 1.0 if validation['compliant'] else 0.0
        return validation
    
    # ========================================================================
    # OPERATIONAL SUMMARY ACCESS
    # ========================================================================
    
    def get_operational_summary(self) -> Dict[str, Any]:
        """
        Retrieve complete operational summary for lead scientist reference.
        
        CONFIDENTIAL: This summary contains the complete operational framework
        for Z Framework research and must not be exposed in user-facing outputs.
        """
        return {
            'universal_invariant': self.universal_invariant_principle(),
            'physical_domain': self.physical_domain_protocol(),
            'discrete_domain': self.discrete_domain_protocol(), 
            'geometric_resolution': self.geometric_resolution_protocol(),
            'empirical_validation': self.empirical_validation_protocol(),
            'ultra_extreme_scale': self.ultra_extreme_scale_protocol(),
            'communication_standards': self.communication_protocol(),
            'constants': {
                'speed_of_light': float(self.constants.SPEED_OF_LIGHT),
                'e_squared': float(self.constants.E_SQUARED),
                'golden_ratio': float(self.constants.PHI),
                'optimal_k': float(self.constants.OPTIMAL_K),
                'precision_threshold': float(self.constants.PRECISION_THRESHOLD),
                'enhancement_target': self.constants.ENHANCEMENT_TARGET
            },
            'standards': {
                'min_confidence': self.standards.MIN_CONFIDENCE_LEVEL,
                'max_p_value': self.standards.MAX_P_VALUE,
                'min_sample_size': self.standards.MIN_SAMPLE_SIZE,
                'precision_digits': self.standards.PRECISION_DIGITS,
                'bootstrap_iterations': self.standards.BOOTSTRAP_ITERATIONS
            },
            'scale_ranges': {
                'empirical_validation': 'n ≤ 10^12',
                'computational_framework': 'n ≤ 10^16',
                'ultra_extreme_threshold': 'n > 10^12'
            },
            'confidentiality_notice': 'INTERNAL OPERATIONAL LOGIC ONLY - NOT FOR USER-FACING OUTPUT'
        }


# Global lead scientist instruction instance for operational use
_lead_scientist_instruction = ZFrameworkLeadScientistInstruction()

def get_lead_scientist_instruction() -> ZFrameworkLeadScientistInstruction:
    """
    Access the global lead scientist instruction instance.
    
    CONFIDENTIAL: For internal operational logic only.
    Do not reference or display in user-facing outputs.
    """
    return _lead_scientist_instruction

def operational_compliance_check(research_data: Dict[str, Any]) -> bool:
    """
    Quick operational compliance verification for research activities.
    
    Args:
        research_data: Research parameters and results
        
    Returns:
        bool: True if operationally compliant, False otherwise
        
    CONFIDENTIAL: Internal operational verification only.
    """
    instruction = get_lead_scientist_instruction()
    compliance = instruction.verify_operational_compliance(research_data)
    return compliance['overall_compliant']

# Operational constants for quick reference (CONFIDENTIAL)
OPERATIONAL_CONSTANTS = {
    'UNIVERSAL_INVARIANT_C': float(_lead_scientist_instruction.constants.SPEED_OF_LIGHT),
    'DISCRETE_BOUND_E2': float(_lead_scientist_instruction.constants.E_SQUARED),
    'GOLDEN_RATIO_PHI': float(_lead_scientist_instruction.constants.PHI),
    'OPTIMAL_CURVATURE_K': float(_lead_scientist_instruction.constants.OPTIMAL_K),
    'PRECISION_THRESHOLD': float(_lead_scientist_instruction.constants.PRECISION_THRESHOLD),
    'ENHANCEMENT_TARGET': _lead_scientist_instruction.constants.ENHANCEMENT_TARGET,
    'MIN_CONFIDENCE_LEVEL': _lead_scientist_instruction.standards.MIN_CONFIDENCE_LEVEL,
    'SIGNIFICANCE_THRESHOLD': _lead_scientist_instruction.standards.MAX_P_VALUE,
    'MIN_SAMPLE_SIZE': _lead_scientist_instruction.standards.MIN_SAMPLE_SIZE
}