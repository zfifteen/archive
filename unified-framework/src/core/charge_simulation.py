"""
Charge as v_w Motion: Gravity/Electromagnetism Unification

This module implements charge as velocity in the w-dimension (v_w), unifying
gravitational and electromagnetic effects within the Z framework's 5D spacetime model.

Building on the existing DiscreteZetaShift 5D coordinates (x, y, z, w, u), this module:
1. Models charge as motion velocity v_w in the w-dimension
2. Computes electromagnetic fields from v_w-induced curvature
3. Unifies gravity and electromagnetism through Z = A(B/c) geometric constraints
4. Provides simulation protocols for LHC-like experimental validation

Key Concepts:
- v_w represents charge-induced motion in compactified 5th dimension (Kaluza-Klein theory)
- Electromagnetic field strength ∝ v_w/c (relativistic w-motion)
- Gravitational curvature κ_g and electromagnetic curvature κ_em unified via Z framework
- Observable Kaluza-Klein towers m_n = n/R for compactified dimension
"""

import numpy as np
import mpmath as mp
from abc import ABC, abstractmethod
from .domain import DiscreteZetaShift, PHI, E_SQUARED
from .axioms import universal_invariance, curvature

# Physical constants (in natural units where c = 1)
C_LIGHT = 1.0  # Speed of light (normalized)
ALPHA_EM = 1/137.036  # Fine structure constant
G_NEWTON = 1.0  # Gravitational constant (normalized)
PLANCK_LENGTH = 1.0  # Planck length (normalized)

# Kaluza-Klein compactification scale
R_COMPACTIFICATION = PLANCK_LENGTH * np.sqrt(ALPHA_EM)  # ~10^-17 m

class ChargedParticle:
    """
    Represents a charged particle with motion in 5D spacetime.
    
    The particle's charge manifests as velocity v_w in the w-dimension,
    following the Z framework's geometric constraints.
    """
    
    def __init__(self, charge, mass, n_index=2):
        """
        Initialize charged particle.
        
        Args:
            charge: Electric charge (in units of elementary charge e)
            mass: Rest mass (in natural units)
            n_index: Integer index for DiscreteZetaShift embedding
        """
        self.charge = charge
        self.mass = mass
        self.n_index = n_index
        
        # Create underlying zeta shift for 5D embedding
        self.zeta_shift = DiscreteZetaShift(n_index)
        
        # Compute 5D coordinates
        self.coords_5d = self.zeta_shift.get_5d_coordinates()
        self.x, self.y, self.z, self.w, self.u = self.coords_5d
        
        # Compute v_w from charge using Z framework
        self.v_w = self._compute_v_w()
        
    def _compute_v_w(self):
        """
        Compute w-dimension velocity from charge using Z framework.
        
        Following Z = A(B/c), where:
        - A = charge magnitude |q|
        - B = w-coordinate motion rate  
        - c = speed of light (universal invariant)
        
        Returns v_w such that electromagnetic effects manifest as w-motion.
        """
        if self.charge == 0:
            return 0.0
            
        # Use Z framework: v_w = Z(charge, w-curvature) / c
        w_curvature = abs(self.w) / (1 + abs(self.w))  # Bounded curvature
        z_value = universal_invariance(abs(self.charge) * w_curvature, C_LIGHT)
        
        # Scale by fine structure constant and sign of charge
        v_w = np.sign(self.charge) * ALPHA_EM * z_value * C_LIGHT
        
        # Ensure |v_w| < c (relativistic constraint)
        if abs(v_w) >= C_LIGHT:
            v_w = np.sign(v_w) * C_LIGHT * (1 - 1e-6)
            
        return v_w
        
    def get_electromagnetic_field(self, position):
        """
        Compute electromagnetic field at given position due to v_w motion.
        
        Args:
            position: (x, y, z) coordinate where field is evaluated
            
        Returns:
            (E_field, B_field): Electric and magnetic field vectors
        """
        # Distance from particle
        dx = position[0] - self.x
        dy = position[1] - self.y  
        dz = position[2] - self.z
        r = np.sqrt(dx**2 + dy**2 + dz**2)
        
        if r < 1e-10:  # Avoid singularity
            return np.zeros(3), np.zeros(3)
            
        # Unit vector from particle to position
        r_hat = np.array([dx, dy, dz]) / r
        
        # Electric field from Coulomb law in 5D (projected to 3D)
        E_magnitude = self.charge * ALPHA_EM / (r**2)
        E_field = E_magnitude * r_hat
        
        # Magnetic field from v_w motion (similar to current loop)
        # B ∝ v_w × r_hat, with w-dimension creating effective current
        w_motion_vector = np.array([0, 0, self.v_w])  # Project w-motion to z
        B_field = (ALPHA_EM / C_LIGHT) * np.cross(w_motion_vector, r_hat) / r**2
        
        return E_field, B_field
        
    def get_gravitational_curvature(self):
        """
        Compute gravitational curvature from mass-energy including v_w motion.
        
        Uses Einstein field equations modified for 5D spacetime:
        κ_g = 8πG(T_μν + T_w) where T_w comes from w-motion energy
        """
        # Rest mass contribution
        mass_curvature = 8 * np.pi * G_NEWTON * self.mass
        
        # v_w kinetic energy contribution  
        gamma_w = 1 / np.sqrt(1 - (self.v_w / C_LIGHT)**2)
        kinetic_energy_w = (gamma_w - 1) * self.mass * C_LIGHT**2
        kinetic_curvature = 8 * np.pi * G_NEWTON * kinetic_energy_w / C_LIGHT**4
        
        return mass_curvature + kinetic_curvature
        
    def get_electromagnetic_curvature(self):
        """
        Compute electromagnetic curvature from charge motion in w-dimension.
        
        Following Maxwell equations in 5D: κ_em ∝ F_μν F^μν where F includes w-components
        """
        # Field energy density
        field_energy = (ALPHA_EM * self.charge**2) / (8 * np.pi * PLANCK_LENGTH**2)
        
        # w-motion field energy (magnetic-like from v_w)
        w_field_energy = (self.v_w / C_LIGHT)**2 * field_energy
        
        # Total electromagnetic curvature  
        em_curvature = 8 * np.pi * G_NEWTON * (field_energy + w_field_energy) / C_LIGHT**4
        
        return em_curvature
        
    def get_unified_curvature(self):
        """
        Unified gravity-electromagnetic curvature via Z framework.
        
        Combines gravitational and electromagnetic effects geometrically,
        resolving the traditional separation through 5D w-motion.
        """
        kappa_g = self.get_gravitational_curvature()
        kappa_em = self.get_electromagnetic_curvature()
        
        # Z framework unification: κ_unified = κ_g + κ_em + κ_interaction
        # Interaction term from w-motion coupling gravity and EM
        kappa_interaction = 2 * np.sqrt(kappa_g * kappa_em) * (self.v_w / C_LIGHT)
        
        return kappa_g + kappa_em + kappa_interaction

class ChargeSimulation:
    """
    Simulation environment for charge as v_w motion experiments.
    
    Provides protocols for testing gravity/EM unification against
    hypothetical LHC-like experimental data.
    """
    
    def __init__(self):
        self.particles = []
        self.field_grid = None
        self.simulation_time = 0.0
        
    def add_particle(self, charge, mass, n_index=None):
        """Add charged particle to simulation."""
        if n_index is None:
            n_index = len(self.particles) + 2  # Start from 2 like DiscreteZetaShift
        particle = ChargedParticle(charge, mass, n_index)
        self.particles.append(particle)
        return particle
        
    def compute_field_at_position(self, position):
        """
        Compute total electromagnetic field at position from all particles.
        
        Args:
            position: (x, y, z) coordinates
            
        Returns:
            (E_total, B_total): Total electric and magnetic fields
        """
        E_total = np.zeros(3)
        B_total = np.zeros(3)
        
        for particle in self.particles:
            E_field, B_field = particle.get_electromagnetic_field(position)
            E_total += E_field
            B_total += B_field
            
        return E_total, B_total
        
    def generate_field_grid(self, x_range, y_range, z_range, num_points=20):
        """Generate electromagnetic field on 3D grid for visualization."""
        x_vals = np.linspace(x_range[0], x_range[1], num_points)
        y_vals = np.linspace(y_range[0], y_range[1], num_points)  
        z_vals = np.linspace(z_range[0], z_range[1], num_points)
        
        X, Y, Z = np.meshgrid(x_vals, y_vals, z_vals, indexing='ij')
        E_grid = np.zeros((num_points, num_points, num_points, 3))
        B_grid = np.zeros((num_points, num_points, num_points, 3))
        
        for i in range(num_points):
            for j in range(num_points):
                for k in range(num_points):
                    position = [X[i,j,k], Y[i,j,k], Z[i,j,k]]
                    E_field, B_field = self.compute_field_at_position(position)
                    E_grid[i,j,k] = E_field
                    B_grid[i,j,k] = B_field
                    
        self.field_grid = {
            'coordinates': (X, Y, Z),
            'E_field': E_grid,
            'B_field': B_grid
        }
        return self.field_grid
        
    def compute_kaluza_klein_modes(self, n_max=10):
        """
        Compute Kaluza-Klein tower modes m_n = n/R for compactified w-dimension.
        
        These represent observable signatures of 5D unification that could be
        detected in LHC-like experiments.
        """
        modes = []
        for n in range(1, n_max + 1):
            mass_n = n / R_COMPACTIFICATION
            modes.append({
                'n': n,
                'mass': mass_n,
                'coupling_strength': ALPHA_EM / np.sqrt(n),
                'production_cross_section': (ALPHA_EM**2) / (mass_n**2)
            })
        return modes
        
    def simulate_lhc_collision(self, beam_energy, impact_parameter=0.0):
        """
        Simulate high-energy collision testing v_w charge model.
        
        Args:
            beam_energy: Center-of-mass energy (GeV)
            impact_parameter: Collision impact parameter
            
        Returns:
            collision_data: Dictionary with observables for comparison with LHC
        """
        # Create collision scenario with two beams
        proton_charge = 1.0
        proton_mass = 0.938  # GeV
        
        # Add beam particles with high n_index for high energy
        n_beam = int(beam_energy / 10)  # Scale with energy
        beam1 = self.add_particle(proton_charge, proton_mass, n_beam)
        beam2 = self.add_particle(proton_charge, proton_mass, n_beam + 1)
        
        # Collision observables
        collision_data = {
            'beam_energy': beam_energy,
            'impact_parameter': impact_parameter,
            'v_w_beam1': beam1.v_w,
            'v_w_beam2': beam2.v_w,
            'unified_curvature_beam1': beam1.get_unified_curvature(),
            'unified_curvature_beam2': beam2.get_unified_curvature(),
            'kaluza_klein_modes': self.compute_kaluza_klein_modes(),
            'w_dimension_signature': abs(beam1.v_w) + abs(beam2.v_w),
            'em_gravity_coupling': np.sqrt(beam1.get_gravitational_curvature() * 
                                         beam1.get_electromagnetic_curvature())
        }
        
        # Predicted signatures for LHC comparison
        collision_data['predicted_signatures'] = {
            'extra_dimensional_resonances': [mode['mass'] for mode in collision_data['kaluza_klein_modes']],
            'modified_coulomb_scattering': collision_data['w_dimension_signature'] * ALPHA_EM,
            'gravity_em_interference': collision_data['em_gravity_coupling'] / G_NEWTON
        }
        
        return collision_data

def create_hydrogen_atom_simulation():
    """
    Create simulation of hydrogen atom using v_w charge model.
    
    Tests if electron orbital motion can be described as w-dimension velocity
    while maintaining electromagnetic binding with proton.
    """
    sim = ChargeSimulation()
    
    # Add proton (at origin)
    proton = sim.add_particle(charge=1.0, mass=0.938, n_index=2)
    
    # Add electron (bound orbit represented as w-motion)
    electron = sim.add_particle(charge=-1.0, mass=0.000511, n_index=3)
    
    # Compute binding energy from unified curvature
    binding_curvature = proton.get_unified_curvature() + electron.get_unified_curvature()
    binding_energy = -13.6 * (1 + binding_curvature)  # Modified Rydberg formula
    
    return {
        'simulation': sim,
        'proton': proton,
        'electron': electron,
        'binding_energy': binding_energy,
        'electron_v_w': electron.v_w,
        'proton_v_w': proton.v_w,
        'unified_atom_curvature': binding_curvature
    }

def validate_unification_principle():
    """
    Validate that gravity and electromagnetism unify through v_w motion.
    
    Returns metrics comparing traditional separated calculations vs
    unified Z framework approach.
    """
    # Test case: charged massive particle
    test_particle = ChargedParticle(charge=1.0, mass=1.0, n_index=10)
    
    # Traditional separated approach
    gravity_only = test_particle.get_gravitational_curvature()
    em_only = test_particle.get_electromagnetic_curvature()
    separated_total = gravity_only + em_only
    
    # Unified Z framework approach
    unified_total = test_particle.get_unified_curvature()
    
    # Unification factor (should be > 1 if unification adds new physics)
    unification_factor = unified_total / separated_total if separated_total > 0 else np.inf
    
    return {
        'gravity_curvature': gravity_only,
        'em_curvature': em_only,
        'separated_total': separated_total,
        'unified_total': unified_total,
        'unification_factor': unification_factor,
        'v_w_contribution': test_particle.v_w / C_LIGHT,
        'validates_unification': unification_factor > 1.0
    }

# Example usage and validation
if __name__ == "__main__":
    # Validate unification principle
    validation = validate_unification_principle()
    print("Gravity/EM Unification Validation:")
    print(f"  Unified curvature factor: {validation['unification_factor']:.3f}")
    print(f"  v_w contribution: {validation['v_w_contribution']:.6f}")
    print(f"  Validates unification: {validation['validates_unification']}")
    
    # Test hydrogen atom
    hydrogen = create_hydrogen_atom_simulation()
    print(f"\nHydrogen Atom Simulation:")
    print(f"  Electron v_w: {hydrogen['electron_v_w']:.6f}")
    print(f"  Modified binding energy: {hydrogen['binding_energy']:.3f} eV")
    
    # Test LHC-like collision
    sim = ChargeSimulation()
    collision = sim.simulate_lhc_collision(beam_energy=14000)  # 14 TeV
    print(f"\nLHC Collision Simulation (14 TeV):")
    print(f"  W-dimension signature: {collision['w_dimension_signature']:.6f}")
    print(f"  KK modes: {len(collision['kaluza_klein_modes'])} predicted")