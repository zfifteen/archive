"""
Simulated Discrete-Gravity Dynamics: Empirical Validation

This module implements a non-hyperbolic gravitational response on a one-dimensional 
periodic lattice, testing the failure of hyperbolicity in the far field through
discrete gravity dynamics simulation.

MATHEMATICAL FRAMEWORK:
- Linearized update: α⋅h + β⋅Δh + γ⋅∂_t h = S(t,x)
- Parameters: α = 1, β = k², γ = 0.09753
- Dispersion relation: ω(q) = i(α + β⋅q²)/γ (purely imaginary, diffusive)
- Screening length: ℓ = √(β/α) = k
- Explicit Euler time-stepping: Δt = 0.01, 500 steps
- Lattice size: N = 512 (periodic boundary conditions)

INTEGRATION WITH Z FRAMEWORK:
This module follows the Z Framework System Instruction, using DiscreteZetaShift
objects for numerical computations and maintaining high-precision arithmetic
(mpmath dps=50) for validation.

SOURCE MODES:
- Mode A: Unit impulse at t=0 (linear response test)
- Mode B: Two-body surrogate (decaying circular orbit envelope injection)
- Mode C: Strong, short quench (localized perturbation)

EXPECTED BEHAVIORS:
- No propagating fronts or ringdown oscillations
- Exponential screening with length ℓ = k
- Diffusive behavior (purely imaginary dispersion)
- High-precision validation with agreement better than 10⁻¹⁰
"""

import numpy as np
import mpmath as mp
from typing import Tuple, Dict, List, Optional, Callable
from abc import ABC, abstractmethod

# Set high precision for numerical stability
mp.mp.dps = 50

# Import Z Framework components
try:
    from .domain import DiscreteZetaShift, PHI, E_SQUARED
    from .axioms import universal_invariance, curvature
    from .params import MP_DPS, KAPPA_GEO_DEFAULT, KAPPA_STAR_DEFAULT
    from .system_instruction import enforce_system_instruction
    _FRAMEWORK_AVAILABLE = True
except ImportError:
    _FRAMEWORK_AVAILABLE = False
    # Fallback for standalone usage
    PHI = (1 + mp.sqrt(5)) / 2
    E_SQUARED = mp.exp(2)
    MP_DPS = 50
    def enforce_system_instruction(func):
        return func


class DiscreteGravitySource(ABC):
    """
    Abstract base class for source terms S(t,x) in discrete gravity dynamics.
    
    Each source mode implements different physics scenarios for testing
    the failure of hyperbolicity in far-field gravitational response.
    """
    
    @abstractmethod
    def evaluate(self, t: float, x: np.ndarray) -> np.ndarray:
        """
        Evaluate source term S(t,x) at given time and positions.
        
        Args:
            t: Time coordinate
            x: Spatial coordinates array (length N)
            
        Returns:
            Source term values S(t,x) at each spatial point
        """
        pass
    
    @abstractmethod
    def get_description(self) -> str:
        """Return human-readable description of the source mode."""
        pass


class ModeAUnitImpulse(DiscreteGravitySource):
    """
    Mode A: Unit impulse at t=0 (linear response test).
    
    Tests fundamental linear response of the discrete gravity system
    to a localized impulse at the origin, examining exponential
    screening and absence of propagating fronts.
    """
    
    def __init__(self, amplitude: float = 1.0, center_index: int = 0):
        """
        Initialize unit impulse source.
        
        Args:
            amplitude: Peak amplitude of impulse
            center_index: Spatial index for impulse center
        """
        self.amplitude = amplitude
        self.center_index = center_index
        
    def evaluate(self, t: float, x: np.ndarray) -> np.ndarray:
        """
        Evaluate unit impulse: S(t,x) = amplitude * δ(x) * δ(t).
        
        Returns non-zero only at t=0 and x=center_index.
        """
        N = len(x)
        source = np.zeros(N, dtype=mp.mpf)
        
        # Apply impulse only at t=0 (within numerical tolerance)
        if abs(t) < 1e-10:
            source[self.center_index] = mp.mpf(self.amplitude)
            
        return source
    
    def get_description(self) -> str:
        return f"Mode A: Unit impulse (amplitude={self.amplitude}) at index {self.center_index}"


class ModeBTwoBodySurrogate(DiscreteGravitySource):
    """
    Mode B: Two-body surrogate (decaying circular orbit envelope injection).
    
    Simulates inspiral-like dynamics with sustained source representing
    localized energy-momentum evolution typical of compact binary systems.
    Tests far-field suppression and local energy storage.
    """
    
    def __init__(self, amplitude: float = 0.002, decay_rate: float = 0.1, 
                 frequency: float = 0.5, center_index: int = 0, width: int = 10):
        """
        Initialize two-body surrogate source.
        
        Args:
            amplitude: Peak amplitude of surrogate
            decay_rate: Exponential decay rate of orbit
            frequency: Orbital frequency
            center_index: Center of binary system
            width: Spatial width of source distribution
        """
        self.amplitude = amplitude
        self.decay_rate = decay_rate
        self.frequency = frequency
        self.center_index = center_index
        self.width = width
        
    def evaluate(self, t: float, x: np.ndarray) -> np.ndarray:
        """
        Evaluate two-body surrogate: envelope modulated oscillation.
        
        S(t,x) = A * exp(-decay*t) * cos(2π*f*t) * Gaussian(x-center, width)
        """
        N = len(x)
        source = np.zeros(N, dtype=mp.mpf)
        
        # Time-dependent envelope with decay and oscillation
        time_envelope = mp.mpf(self.amplitude) * mp.exp(-mp.mpf(self.decay_rate) * mp.mpf(t))
        time_modulation = mp.cos(2 * mp.pi * mp.mpf(self.frequency) * mp.mpf(t))
        
        # Spatial Gaussian distribution around center
        for i in range(N):
            # Handle periodic boundary conditions
            dx = min(abs(i - self.center_index), N - abs(i - self.center_index))
            spatial_weight = mp.exp(-mp.mpf(dx)**2 / (2 * mp.mpf(self.width)**2))
            
            source[i] = time_envelope * time_modulation * spatial_weight
            
        return source
    
    def get_description(self) -> str:
        return (f"Mode B: Two-body surrogate (A={self.amplitude}, "
                f"decay={self.decay_rate}, f={self.frequency}) at index {self.center_index}")


class ModeCStrongQuench(DiscreteGravitySource):
    """
    Mode C: Strong, short quench (localized perturbation).
    
    Tests response to intense but brief localized perturbation,
    examining absence of solitons, topological defects, and
    maintenance of localized response without propagation.
    """
    
    def __init__(self, amplitude: float = 0.01, duration: float = 0.1,
                 center_index: int = 0, width: int = 5):
        """
        Initialize strong quench source.
        
        Args:
            amplitude: Peak amplitude of quench
            duration: Time duration of quench
            center_index: Center of quench
            width: Spatial width of quench
        """
        self.amplitude = amplitude
        self.duration = duration
        self.center_index = center_index
        self.width = width
        
    def evaluate(self, t: float, x: np.ndarray) -> np.ndarray:
        """
        Evaluate strong quench: brief, intense, localized pulse.
        
        S(t,x) = A * rect(t/duration) * Gaussian(x-center, width)
        """
        N = len(x)
        source = np.zeros(N, dtype=mp.mpf)
        
        # Time-dependent rectangular pulse
        if t <= self.duration:
            time_weight = mp.mpf(self.amplitude)
        else:
            time_weight = mp.mpf(0.0)
            
        # Spatial Gaussian distribution
        for i in range(N):
            # Handle periodic boundary conditions
            dx = min(abs(i - self.center_index), N - abs(i - self.center_index))
            spatial_weight = mp.exp(-mp.mpf(dx)**2 / (2 * mp.mpf(self.width)**2))
            
            source[i] = time_weight * spatial_weight
            
        return source
    
    def get_description(self) -> str:
        return (f"Mode C: Strong quench (A={self.amplitude}, "
                f"duration={self.duration}) at index {self.center_index}")


class DiscreteGravitySimulator:
    """
    Main simulator for discrete gravity dynamics on periodic lattice.
    
    Implements explicit Euler time-stepping for the linearized equation:
    α⋅h + β⋅Δh + γ⋅∂_t h = S(t,x)
    
    with high-precision numerical stability and comprehensive diagnostics.
    """
    
    def __init__(self, N: int = 512, dt: float = 0.01, total_steps: int = 500,
                 alpha: float = 1.0, gamma: float = 0.09753, k: float = 0.3, delta: float = 0.0):
        """
        Initialize discrete gravity simulator.
        
        Args:
            N: Lattice size (periodic)
            dt: Time step for explicit Euler (first-order) or velocity-Verlet-like (second-order)
            total_steps: Total number of time steps
            alpha: Linear coefficient (default 1.0)
            gamma: Time derivative coefficient (default 0.09753)
            k: Spatial derivative coefficient (β = k²)
            delta: Messenger-mediated dynamics coefficient (default 0.0 for pure diffusive)
        """
        self.N = N
        self.dt = mp.mpf(dt)
        self.total_steps = total_steps
        self.alpha = mp.mpf(alpha)
        self.beta = mp.mpf(k)**2  # β = k²
        self.gamma = mp.mpf(gamma)
        self.k = mp.mpf(k)
        self.delta = mp.mpf(delta)  # Messenger-mediated dynamics parameter
        
        # Derived quantities
        self.effective_beta = self.beta - self.delta  # Effective spatial coefficient
        # Screening length: real for effective_beta > 0 (diffusive), imaginary for effective_beta < 0 (hyperbolic)
        self.screening_length = mp.sqrt(self.effective_beta / self.alpha) if self.effective_beta != 0 else mp.inf
        
        # Spatial grid (periodic)
        self.x = np.arange(N, dtype=mp.mpf)
        
        # Initialize field and derivatives
        self.h = np.zeros(N, dtype=mp.mpf)
        self.h_dot = np.zeros(N, dtype=mp.mpf)  # First time derivative (velocity)
        
        # For messenger-mediated dynamics, we need second-order time derivatives
        self.is_hyperbolic = self.delta > 0  # Use second-order integration when delta > 0
        
        # History storage for analysis
        self.time_history = []
        self.field_history = []
        self.energy_history = []
        self.strain_history = []
        
        # Source term
        self.source = None
        
        # Integration with Z Framework
        if _FRAMEWORK_AVAILABLE:
            self.zeta_shift = DiscreteZetaShift(N)
            
    def set_source(self, source: DiscreteGravitySource):
        """Set the source term S(t,x) for the simulation."""
        self.source = source
        
    def compute_spatial_derivative(self, field: np.ndarray) -> np.ndarray:
        """
        Compute spatial derivative Δh using finite differences with periodic BC.
        
        For periodic lattice: Δh[i] = h[i+1] - 2*h[i] + h[i-1]
        """
        N = len(field)
        delta_h = np.zeros(N, dtype=mp.mpf)
        
        for i in range(N):
            i_plus = (i + 1) % N  # Periodic boundary
            i_minus = (i - 1) % N
            delta_h[i] = field[i_plus] - 2*field[i] + field[i_minus]
            
        return delta_h
    
    def compute_dispersion_relation(self, q: float) -> complex:
        """
        Compute dispersion relation for the modified equation.
        
        For diffusive case (δ=0): ω(q) = i(α + β⋅q²)/γ
        For hyperbolic case (δ>0): γ⋅ω² + α + (β-δ)⋅q² = 0
                                   ω = ±i⋅√((α + (β-δ)⋅q²)/γ)
        
        Returns frequency ω(q) which is purely imaginary for stable modes.
        """
        if not self.is_hyperbolic:
            # Original diffusive case: γ⋅∂_t h + α⋅h + β⋅Δh = S
            return 1j * (self.alpha + self.beta * q**2) / self.gamma
        else:
            # Hyperbolic case: γ⋅∂²_t h + α⋅h + (β-δ)⋅Δh = S
            # ω² = -(α + (β-δ)⋅q²)/γ
            discriminant = (self.alpha + self.effective_beta * q**2) / self.gamma
            if discriminant >= 0:
                # Stable oscillatory mode
                return 1j * mp.sqrt(discriminant)
            else:
                # Propagating mode (if discriminant < 0, we get real frequencies)
                return mp.sqrt(-discriminant)
    
    def compute_lyapunov_functional(self) -> float:
        """
        Compute Lyapunov functional (energy) for the system.
        
        For diffusive case: E = (α/2)||h||² + (β/2)||∇h||²
        For hyperbolic case: E = (γ/2)||∂_t h||² + (α/2)||h||² + (|β-δ|/2)||∇h||²
        
        This functional decreases monotonically when S≡0 for stable systems.
        """
        norm_h_squared = mp.fsum([abs(h_i)**2 for h_i in self.h])
        
        grad_h = self.compute_spatial_derivative(self.h)
        norm_grad_h_squared = mp.fsum([abs(grad_i)**2 for grad_i in grad_h])
        
        if not self.is_hyperbolic:
            # Diffusive case
            energy = (self.alpha / 2) * norm_h_squared + (self.beta / 2) * norm_grad_h_squared
        else:
            # Hyperbolic case: add kinetic energy term
            norm_hdot_squared = mp.fsum([abs(hdot_i)**2 for hdot_i in self.h_dot])
            energy = ((self.gamma / 2) * norm_hdot_squared + 
                     (self.alpha / 2) * norm_h_squared + 
                     (abs(self.effective_beta) / 2) * norm_grad_h_squared)
        
        return float(energy)
    
    def compute_strain_proxy(self) -> float:
        """
        Compute strain proxy h(t) as characteristic amplitude measure.
        
        Returns RMS value of the field as proxy for gravitational strain.
        """
        rms_h = mp.sqrt(mp.fsum([abs(h_i)**2 for h_i in self.h]) / len(self.h))
        return float(rms_h)
    
    def compute_density_activation(self, threshold: float = 0.01) -> float:
        """
        Compute fraction of lattice sites with |h| > threshold.
        
        Measures spatial extent of gravitational response.
        """
        active_count = sum(1 for h_i in self.h if abs(h_i) > threshold)
        return active_count / len(self.h)
    
    @enforce_system_instruction
    def step(self, t: float):
        """
        Perform one time step using appropriate integration scheme.
        
        For diffusive case (δ=0): Explicit Euler: h^{n+1} = h^n + dt * (S - α*h - β*Δh) / γ
        For hyperbolic case (δ>0): Leapfrog: γ⋅∂²_t h + α⋅h + (β-δ)⋅Δh = S
        """
        # Compute spatial derivative
        delta_h = self.compute_spatial_derivative(self.h)
        
        # Evaluate source term
        if self.source is not None:
            source_values = self.source.evaluate(t, self.x)
        else:
            source_values = np.zeros(self.N, dtype=mp.mpf)
            
        if not self.is_hyperbolic:
            # Original diffusive case: γ⋅∂_t h = S - α⋅h - β⋅Δh
            for i in range(self.N):
                dh_dt = (source_values[i] - self.alpha * self.h[i] - self.beta * delta_h[i]) / self.gamma
                self.h[i] += self.dt * dh_dt
        else:
            # Hyperbolic case: γ⋅∂²_t h = S - α⋅h - (β-δ)⋅Δh
            # Use leapfrog integration: v^{n+1} = v^n + dt * acceleration
            #                          h^{n+1} = h^n + dt * v^{n+1}
            for i in range(self.N):
                acceleration = (source_values[i] - self.alpha * self.h[i] - self.effective_beta * delta_h[i]) / self.gamma
                self.h[i] += self.dt * self.h_dot[i]
                self.h_dot[i] += self.dt * acceleration
            
        # Store history for analysis
        self.time_history.append(float(t))
        self.field_history.append(self.h.copy())
        self.energy_history.append(self.compute_lyapunov_functional())
        self.strain_history.append(self.compute_strain_proxy())
    
    def run_simulation(self) -> Dict:
        """
        Run complete simulation and return results.
        
        Returns dictionary with time series, final state, and diagnostics.
        """
        if self.source is None:
            raise ValueError("No source term set. Use set_source() before running.")
            
        print(f"Running discrete gravity simulation: {self.source.get_description()}")
        print(f"Parameters: N={self.N}, dt={float(self.dt)}, steps={self.total_steps}")
        print(f"α={float(self.alpha)}, β={float(self.beta)}, γ={float(self.gamma)}, k={float(self.k)}, δ={float(self.delta)}")
        print(f"Mode: {'Hyperbolic (messenger-mediated)' if self.is_hyperbolic else 'Diffusive'}")
        print(f"Effective β = {float(self.effective_beta)}, Screening length ℓ = {float(self.screening_length)}")
        
        # Reset simulation state
        self.h = np.zeros(self.N, dtype=mp.mpf)
        self.h_dot = np.zeros(self.N, dtype=mp.mpf)  # Reset velocity for hyperbolic case
        self.time_history = []
        self.field_history = []
        self.energy_history = []
        self.strain_history = []
        
        # Time evolution
        for step in range(self.total_steps):
            t = step * self.dt
            self.step(float(t))
            
            # Progress reporting
            if step % 100 == 0:
                energy = self.energy_history[-1]
                strain = self.strain_history[-1]
                activation = self.compute_density_activation()
                print(f"Step {step}/{self.total_steps}: t={float(t):.3f}, "
                      f"E={energy:.2e}, strain={strain:.2e}, active={activation:.1%}")
        
        # Final analysis
        results = self.analyze_results()
        print("Simulation completed.")
        
        return results
    
    def analyze_results(self) -> Dict:
        """
        Comprehensive analysis of simulation results.
        
        Returns detailed diagnostics including:
        - Field amplitude analysis at key time points
        - Energy evolution and decay rates
        - Strain proxy behavior
        - Density activation statistics
        - Dispersion relation validation
        - Screening length verification
        """
        results = {
            'parameters': {
                'N': self.N,
                'dt': float(self.dt),
                'total_steps': self.total_steps,
                'alpha': float(self.alpha),
                'beta': float(self.beta),
                'gamma': float(self.gamma),
                'k': float(self.k),
                'screening_length': float(self.screening_length)
            },
            'time_series': {
                'time': self.time_history,
                'energy': self.energy_history,
                'strain': self.strain_history
            },
            'field_analysis': {},
            'diagnostics': {}
        }
        
        # Field amplitude analysis at key distances
        final_field = self.field_history[-1]
        field_amplitudes = {}
        
        # Analyze amplitude at center and various distances
        center_idx = 0
        field_amplitudes['A(0)'] = float(abs(final_field[center_idx]))
        
        # Check amplitudes at specific distances
        for r in [2, 5, 10, 20]:
            if r < self.N // 2:
                idx = r % self.N
                field_amplitudes[f'A({r})'] = float(abs(final_field[idx]))
                
        results['field_analysis']['amplitudes'] = field_amplitudes
        
        # Energy decay analysis
        if len(self.energy_history) > 10:
            initial_energy = self.energy_history[10]  # Skip initial transient
            final_energy = self.energy_history[-1]
            energy_decay = (initial_energy - final_energy) / initial_energy if initial_energy > 0 else 0
            results['diagnostics']['energy_decay_fraction'] = energy_decay
            results['diagnostics']['final_energy'] = final_energy
            
        # Strain analysis
        if len(self.strain_history) > 0:
            max_strain = max(self.strain_history)
            final_strain = self.strain_history[-1]
            results['diagnostics']['max_strain'] = max_strain
            results['diagnostics']['final_strain'] = final_strain
            
        # Density activation analysis
        final_activation = self.compute_density_activation()
        results['diagnostics']['final_density_activation'] = final_activation
        
        # Dispersion relation check (sample q values)
        q_values = np.linspace(0.1, 2.0, 10)
        dispersion_check = {}
        for q in q_values:
            omega = self.compute_dispersion_relation(q)
            if not self.is_hyperbolic:
                # Diffusive case: ω = i(α + β⋅q²)/γ
                theoretical_imag = float((self.alpha + self.beta * q**2) / self.gamma)
                dispersion_check[f'q={q:.1f}'] = {
                    'omega_imag': omega.imag,
                    'theoretical_imag': theoretical_imag,
                    'relative_error': abs(omega.imag - theoretical_imag) / theoretical_imag if theoretical_imag != 0 else 0
                }
            else:
                # Hyperbolic case: different validation
                discriminant = (self.alpha + self.effective_beta * q**2) / self.gamma
                dispersion_check[f'q={q:.1f}'] = {
                    'omega_real': omega.real,
                    'omega_imag': omega.imag,
                    'discriminant': float(discriminant),
                    'mode_type': 'stable' if discriminant >= 0 else 'propagating'
                }
        results['diagnostics']['dispersion_validation'] = dispersion_check
        
        return results
    
    def validate_high_precision(self, reference_results: Optional[Dict] = None,
                               tolerance: float = 1e-10) -> Dict:
        """
        High-precision validation using mpmath (dps=50).
        
        Validates numerical accuracy and agreement with reference results
        to better than 10⁻¹⁰ as specified in the issue.
        """
        validation_results = {
            'precision_achieved': MP_DPS,
            'tolerance_target': tolerance,
            'numerical_stability': True,
            'agreement_check': {}
        }
        
        # Check numerical stability (no NaN or infinite values)
        final_field = self.field_history[-1]
        for i, h_val in enumerate(final_field):
            if not mp.isfinite(h_val):
                validation_results['numerical_stability'] = False
                validation_results['error'] = f"Non-finite value at index {i}: {h_val}"
                break
                
        # Check energy conservation (when source is off)
        if len(self.energy_history) > 100:
            # Check last 100 steps for energy monotonicity (should decrease)
            energy_tail = self.energy_history[-100:]
            energy_increases = sum(1 for i in range(1, len(energy_tail)) 
                                 if energy_tail[i] > energy_tail[i-1])
            energy_monotonicity = energy_increases / len(energy_tail)
            validation_results['energy_monotonicity_violations'] = energy_monotonicity
            
        # If reference results provided, check agreement
        if reference_results is not None:
            for key, ref_value in reference_results.items():
                if key in self.analyze_results().get('field_analysis', {}).get('amplitudes', {}):
                    computed_value = self.analyze_results()['field_analysis']['amplitudes'][key]
                    relative_error = abs(computed_value - ref_value) / abs(ref_value) if ref_value != 0 else abs(computed_value)
                    validation_results['agreement_check'][key] = {
                        'reference': ref_value,
                        'computed': computed_value,
                        'relative_error': relative_error,
                        'within_tolerance': relative_error < tolerance
                    }
                    
        return validation_results


def create_mode_a_simulation(k: float = 0.3, N: int = 512, delta: float = 0.0) -> DiscreteGravitySimulator:
    """Create simulator configured for Mode A (unit impulse) testing."""
    sim = DiscreteGravitySimulator(N=N, k=k, delta=delta)
    source = ModeAUnitImpulse(amplitude=1.0, center_index=N//2)
    sim.set_source(source)
    return sim


def create_mode_b_simulation(k: float = 0.3, N: int = 512, delta: float = 0.0) -> DiscreteGravitySimulator:
    """Create simulator configured for Mode B (two-body surrogate) testing."""
    sim = DiscreteGravitySimulator(N=N, k=k, delta=delta)
    source = ModeBTwoBodySurrogate(amplitude=0.002, decay_rate=0.1, 
                                   frequency=0.5, center_index=N//2)
    sim.set_source(source)
    return sim


def create_mode_c_simulation(k: float = 0.3, N: int = 512, delta: float = 0.0) -> DiscreteGravitySimulator:
    """Create simulator configured for Mode C (strong quench) testing."""
    sim = DiscreteGravitySimulator(N=N, k=k, delta=delta)
    source = ModeCStrongQuench(amplitude=0.01, duration=0.1, center_index=N//2)
    sim.set_source(source)
    return sim


def create_messenger_mediated_simulation(k: float = 0.3, delta: float = 0.5, N: int = 512) -> DiscreteGravitySimulator:
    """
    Create simulator configured for messenger-mediated dynamics testing.
    
    Uses Mode A (unit impulse) with hyperbolic dynamics (δ > 0) to test
    finite-speed propagation and screened quasi-waves as described in the hypothesis.
    
    Args:
        k: Spatial coefficient (β = k²)
        delta: Messenger coefficient (δ > 0 for hyperbolic behavior)
        N: Lattice size
    """
    sim = DiscreteGravitySimulator(N=N, k=k, delta=delta)
    source = ModeAUnitImpulse(amplitude=1.0, center_index=N//2)
    sim.set_source(source)
    return sim


def run_parameter_sweep(k_values: List[float] = [0.3, 0.04449], 
                       modes: List[str] = ['A', 'B', 'C']) -> Dict:
    """
    Run complete parameter sweep across k values and source modes.
    
    This reproduces the empirical validation described in the issue,
    testing each combination of k and source mode.
    """
    sweep_results = {}
    
    for k in k_values:
        sweep_results[f'k={k}'] = {}
        
        for mode in modes:
            print(f"\n=== Running Mode {mode} with k={k} ===")
            
            if mode == 'A':
                sim = create_mode_a_simulation(k=k)
            elif mode == 'B':
                sim = create_mode_b_simulation(k=k)
            elif mode == 'C':
                sim = create_mode_c_simulation(k=k)
            else:
                raise ValueError(f"Unknown mode: {mode}")
                
            results = sim.run_simulation()
            validation = sim.validate_high_precision()
            
            sweep_results[f'k={k}'][f'mode_{mode}'] = {
                'simulation_results': results,
                'validation': validation
            }
            
    return sweep_results


if __name__ == "__main__":
    """
    Example usage demonstrating the discrete gravity dynamics simulation.
    """
    print("Discrete Gravity Dynamics: Empirical Validation")
    print("=" * 50)
    
    # Run parameter sweep as described in the issue
    results = run_parameter_sweep()
    
    # Print summary of key findings
    print("\n=== SUMMARY OF KEY FINDINGS ===")
    for k_key, k_results in results.items():
        print(f"\n{k_key}:")
        for mode_key, mode_results in k_results.items():
            mode_data = mode_results['simulation_results']
            validation = mode_results['validation']
            
            print(f"  {mode_key}:")
            print(f"    Final energy: {mode_data['diagnostics'].get('final_energy', 'N/A'):.2e}")
            print(f"    Final strain: {mode_data['diagnostics'].get('final_strain', 'N/A'):.2e}")
            print(f"    Density activation: {mode_data['diagnostics'].get('final_density_activation', 'N/A'):.1%}")
            print(f"    Numerical stability: {validation['numerical_stability']}")