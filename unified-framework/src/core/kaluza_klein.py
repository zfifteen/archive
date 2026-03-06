"""
Kaluza-Klein Theory Implementation for the Z Framework

This module implements the Kaluza-Klein mass tower formula m_n = n/R and integrates
it with the existing domain shift framework Z = n(Δₙ/Δmax). The Kaluza-Klein theory
extends the Z framework into 5D spacetime, unifying gravity and electromagnetism
through compactified extra dimensions.
"""

import numpy as np
import mpmath as mp
from typing import Union, List, Tuple
from .axioms import universal_invariance, curvature

# Set high precision for mathematical calculations
mp.mp.dps = 50

# Physical constants (in natural units where c = 1)
PLANCK_LENGTH = mp.mpf('1.616e-35')  # Planck length in meters
SPEED_OF_LIGHT = mp.mpf('299792458')  # Speed of light in m/s

class KaluzaKleinTower:
    """
    Implements the Kaluza-Klein mass tower m_n = n/R where:
    - n: mode number (integer)
    - R: compactification radius of the extra dimension
    - m_n: mass of the n-th Kaluza-Klein mode
    
    The class integrates with the Z framework by relating the mass tower
    to domain shifts through Z = n(Δₙ/Δmax).
    """
    
    def __init__(self, compactification_radius: float = 1e-16):
        """
        Initialize Kaluza-Klein tower with compactification radius R.
        
        Args:
            compactification_radius (float): The radius R of the compactified 
                                           fifth dimension in meters.
                                           Default is near Planck scale.
        """
        self.R = mp.mpf(compactification_radius)
        self.c = SPEED_OF_LIGHT
        
        # Validate physical parameters
        if self.R <= 0:
            raise ValueError("Compactification radius must be positive")
    
    def mass_tower(self, n: int) -> mp.mpf:
        """
        Compute the Kaluza-Klein mass tower: m_n = n / R
        
        Args:
            n (int): Mode number (must be positive integer)
            
        Returns:
            mp.mpf: Mass of the n-th Kaluza-Klein mode in natural units
        """
        if n <= 0:
            raise ValueError("Mode number n must be positive")
        
        return mp.mpf(int(n)) / self.R
    
    def momentum_tower(self, n: int) -> mp.mpf:
        """
        Compute momentum of n-th mode: p_n = n / R (in natural units c = 1)
        
        Args:
            n (int): Mode number
            
        Returns:
            mp.mpf: Momentum of the n-th mode
        """
        return self.mass_tower(n)  # In natural units, p = m for massive particles at rest
    
    def energy_tower(self, n: int, momentum_3d: float = 0.0) -> mp.mpf:
        """
        Compute energy of n-th mode: E_n = sqrt(p_3D^2 + (n/R)^2)
        
        Args:
            n (int): Mode number
            momentum_3d (float): 3D momentum magnitude
            
        Returns:
            mp.mpf: Energy of the n-th mode
        """
        m_n = self.mass_tower(int(n))
        p_3d = mp.mpf(momentum_3d)
        return mp.sqrt(p_3d**2 + m_n**2)
    
    def domain_shift_relation(self, n: int, d_n: int = None) -> Tuple[mp.mpf, mp.mpf]:
        """
        Relate Kaluza-Klein modes to domain shifts Z = n(Δₙ/Δmax).
        
        This function bridges the mass tower with the existing DiscreteZetaShift
        framework by computing the domain shift parameters.
        
        Args:
            n (int): Mode number (also used as integer in discrete domain)
            d_n (int, optional): Divisor count for curvature calculation.
                                If None, computed from n.
                                
        Returns:
            Tuple[mp.mpf, mp.mpf]: (delta_n, Z_value) where:
                - delta_n: Domain shift parameter Δₙ
                - Z_value: Z framework value Z = n(Δₙ/Δmax)
        """
        n = int(n)  # Ensure n is a regular int
        if d_n is None:
            from sympy import divisors
            d_n = len(divisors(n))
        
        # Calculate curvature-based domain shift
        kappa_n = curvature(n, d_n)
        
        # Mass-dependent domain shift: relate m_n to discrete curvature
        m_n = self.mass_tower(n)
        
        # Domain shift incorporates both curvature and mass tower effects
        # Delta_n = v * kappa_n * (1 + m_n * R) to couple discrete and continuous domains
        v = mp.mpf(1.0)  # Velocity parameter (can be adjusted)
        delta_n = v * kappa_n * (1 + m_n * self.R)
        
        # Maximum domain shift for normalization (using golden ratio principle)
        PHI = (1 + mp.sqrt(5)) / 2
        delta_max = mp.exp(2) * PHI  # e^2 * φ combining fundamental constants
        
        # Z framework value: Z = n(Δₙ/Δmax)
        Z_value = mp.mpf(n) * (delta_n / delta_max)
        
        return delta_n, Z_value
    
    def quantum_numbers(self, n: int) -> dict:
        """
        Compute quantum numbers associated with the n-th Kaluza-Klein mode.
        
        Args:
            n (int): Mode number
            
        Returns:
            dict: Dictionary containing various quantum numbers:
                - 'n': Mode number
                - 'mass': Mass m_n = n/R
                - 'momentum': Momentum p_n
                - 'energy': Energy E_n (at rest)
                - 'charge': Effective charge (related to mode number)
                - 'compactification_phase': Phase φ_n = 2πn related to compactification
        """
        m_n = self.mass_tower(n)
        p_n = self.momentum_tower(n)
        E_n = self.energy_tower(n)
        
        # Effective charge proportional to mode number (in Kaluza-Klein theory)
        charge = mp.mpf(n) / mp.sqrt(self.R)
        
        # Compactification phase
        phi_n = 2 * mp.pi * mp.mpf(n)
        
        return {
            'n': n,
            'mass': m_n,
            'momentum': p_n,
            'energy': E_n,
            'charge': charge,
            'compactification_phase': phi_n
        }
    
    def observable_spectrum(self, n_max: int = 10) -> List[dict]:
        """
        Generate spectrum of observable quantum numbers for modes n = 1 to n_max.
        
        Args:
            n_max (int): Maximum mode number to compute
            
        Returns:
            List[dict]: List of quantum number dictionaries for each mode
        """
        spectrum = []
        for n in range(1, n_max + 1):
            quantum_nums = self.quantum_numbers(n)
            delta_n, Z_value = self.domain_shift_relation(n)
            
            # Add domain shift information
            quantum_nums['delta_n'] = delta_n
            quantum_nums['Z_value'] = Z_value
            
            spectrum.append(quantum_nums)
        
        return spectrum
    
    def mass_gap(self, n1: int, n2: int) -> mp.mpf:
        """
        Compute mass gap between two Kaluza-Klein modes.
        
        Args:
            n1, n2 (int): Mode numbers
            
        Returns:
            mp.mpf: Mass difference |m_n2 - m_n1|
        """
        m1 = self.mass_tower(n1)
        m2 = self.mass_tower(n2)
        return mp.fabs(m2 - m1)
    
    def classical_limit_check(self, n: int) -> bool:
        """
        Check if mode n is in the classical limit (large n).
        The classical limit occurs when the mode wavelength is much smaller
        than the compactification radius.
        
        Args:
            n (int): Mode number
            
        Returns:
            bool: True if in classical limit, False otherwise
        """
        # Wavelength ~ R/n, classical when λ << R, i.e., n >> 1
        return n > 10  # Threshold can be adjusted based on physical requirements

def create_unified_mass_domain_system(compactification_radius: float = 1e-16, 
                                    mode_range: Tuple[int, int] = (1, 20)) -> dict:
    """
    Create a unified system combining Kaluza-Klein mass tower with domain shifts.
    
    This function demonstrates the integration of the mass tower formula m_n = n/R
    with the existing Z framework domain shifts Z = n(Δₙ/Δmax).
    
    Args:
        compactification_radius (float): Radius of compactified dimension
        mode_range (Tuple[int, int]): Range of mode numbers (min, max)
        
    Returns:
        dict: Unified system data containing:
            - 'kk_tower': KaluzaKleinTower instance
            - 'spectrum': Observable spectrum
            - 'correlations': Correlations between mass and domain shifts
            - 'summary_stats': Statistical summary
    """
    # Initialize Kaluza-Klein tower
    kk_tower = KaluzaKleinTower(compactification_radius)
    
    # Generate spectrum
    n_min, n_max = mode_range
    spectrum = []
    masses = []
    domain_shifts = []
    Z_values = []
    
    for n in range(n_min, n_max + 1):
        quantum_nums = kk_tower.quantum_numbers(n)
        delta_n, Z_value = kk_tower.domain_shift_relation(n)
        
        quantum_nums['delta_n'] = delta_n
        quantum_nums['Z_value'] = Z_value
        spectrum.append(quantum_nums)
        
        masses.append(float(quantum_nums['mass']))
        domain_shifts.append(float(delta_n))
        Z_values.append(float(Z_value))
    
    # Compute correlations
    masses_array = np.array(masses)
    domain_shifts_array = np.array(domain_shifts)
    Z_values_array = np.array(Z_values)
    
    correlations = {
        'mass_domain_correlation': np.corrcoef(masses_array, domain_shifts_array)[0, 1],
        'mass_Z_correlation': np.corrcoef(masses_array, Z_values_array)[0, 1],
        'domain_Z_correlation': np.corrcoef(domain_shifts_array, Z_values_array)[0, 1]
    }
    
    # Summary statistics
    summary_stats = {
        'mass_range': (np.min(masses_array), np.max(masses_array)),
        'domain_shift_range': (np.min(domain_shifts_array), np.max(domain_shifts_array)),
        'Z_value_range': (np.min(Z_values_array), np.max(Z_values_array)),
        'total_modes': len(spectrum)
    }
    
    return {
        'kk_tower': kk_tower,
        'spectrum': spectrum,
        'correlations': correlations,
        'summary_stats': summary_stats
    }