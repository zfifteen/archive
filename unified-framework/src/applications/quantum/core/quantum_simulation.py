"""
Quantum Simulation Module for Kaluza-Klein Theory

This module implements quantum simulations to model predicted observables
for different Kaluza-Klein masses m_n = n/R. It uses qutip to simulate
quantum systems and compute physical observables.
"""

import numpy as np
import qutip as qt
import matplotlib.pyplot as plt
from typing import List, Dict, Tuple, Optional
import mpmath as mp
import sys
import os

# Add core module to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from core.kaluza_klein import KaluzaKleinTower

# Set matplotlib backend for headless environments
plt.switch_backend('Agg')

class KaluzaKleinQuantumSimulator:
    """
    Quantum simulator for Kaluza-Klein theory observables.
    
    This class simulates quantum systems with Kaluza-Klein mass towers
    and computes various observables including energy spectra, transition
    probabilities, and correlation functions.
    """
    
    def __init__(self, kk_tower: KaluzaKleinTower, n_levels: int = 10):
        """
        Initialize quantum simulator with Kaluza-Klein tower.
        
        Args:
            kk_tower (KaluzaKleinTower): Kaluza-Klein tower instance
            n_levels (int): Number of energy levels to include in simulation
        """
        self.kk_tower = kk_tower
        self.n_levels = n_levels
        self.basis_states = None
        self.hamiltonian = None
        self._setup_quantum_system()
    
    def _setup_quantum_system(self):
        """Setup the quantum system with Kaluza-Klein energy levels."""
        # Create basis states for the n_levels lowest Kaluza-Klein modes
        self.basis_states = [qt.basis(self.n_levels, i) for i in range(self.n_levels)]
        
        # Create Hamiltonian with Kaluza-Klein energy spectrum
        H_data = np.zeros((self.n_levels, self.n_levels))
        
        for n in range(1, self.n_levels + 1):
            # Energy eigenvalue for n-th mode
            energy = float(self.kk_tower.energy_tower(n))
            H_data[n-1, n-1] = energy
        
        self.hamiltonian = qt.Qobj(H_data)
    
    def energy_spectrum(self) -> Tuple[np.ndarray, List[qt.Qobj]]:
        """
        Compute energy spectrum of the Kaluza-Klein system.
        
        Returns:
            Tuple[np.ndarray, List[qt.Qobj]]: (eigenvalues, eigenvectors)
        """
        eigenvalues, eigenvectors = self.hamiltonian.eigenstates()
        return eigenvalues, eigenvectors
    
    def transition_probabilities(self, initial_state: int, final_states: List[int]) -> np.ndarray:
        """
        Compute transition probabilities between Kaluza-Klein modes.
        
        Args:
            initial_state (int): Initial mode number (1-indexed)
            final_states (List[int]): List of final mode numbers
            
        Returns:
            np.ndarray: Transition probabilities
        """
        if initial_state < 1 or initial_state > self.n_levels:
            raise ValueError(f"Initial state must be between 1 and {self.n_levels}")
        
        initial_qstate = self.basis_states[initial_state - 1]
        probabilities = []
        
        for final_state in final_states:
            if final_state < 1 or final_state > self.n_levels:
                continue
            
            final_qstate = self.basis_states[final_state - 1]
            # Transition probability |<final|initial>|^2
            prob = abs(final_qstate.overlap(initial_qstate))**2
            probabilities.append(prob)
        
        return np.array(probabilities)
    
    def time_evolution(self, initial_state: qt.Qobj, times: np.ndarray) -> List[qt.Qobj]:
        """
        Simulate time evolution of a quantum state under Kaluza-Klein Hamiltonian.
        
        Args:
            initial_state (qt.Qobj): Initial quantum state
            times (np.ndarray): Time points for evolution
            
        Returns:
            List[qt.Qobj]: Evolved states at each time point
        """
        # Time evolution operator: U(t) = exp(-iHt)
        evolved_states = []
        
        for t in times:
            U_t = (-1j * self.hamiltonian * t).expm()
            evolved_state = U_t * initial_state
            evolved_states.append(evolved_state)
        
        return evolved_states
    
    def observable_expectation(self, state: qt.Qobj, observable: qt.Qobj) -> complex:
        """
        Compute expectation value of an observable in a given state.
        
        Args:
            state (qt.Qobj): Quantum state
            observable (qt.Qobj): Observable operator
            
        Returns:
            complex: Expectation value <state|observable|state>
        """
        return qt.expect(observable, state)
    
    def mass_dependent_observables(self, observable_type: str = 'position') -> Dict[int, float]:
        """
        Compute observables for different Kaluza-Klein masses.
        
        Args:
            observable_type (str): Type of observable ('position', 'momentum', 'energy')
            
        Returns:
            Dict[int, float]: Observable values for each mode number
        """
        observables = {}
        
        for n in range(1, self.n_levels + 1):
            state = self.basis_states[n - 1]
            
            if observable_type == 'position':
                # Position operator (simplified)
                x_op = qt.position(self.n_levels)
                obs_value = qt.expect(x_op, state)
            
            elif observable_type == 'momentum':
                # Momentum operator
                p_op = qt.momentum(self.n_levels)
                obs_value = qt.expect(p_op, state)
            
            elif observable_type == 'energy':
                # Energy expectation value
                obs_value = qt.expect(self.hamiltonian, state)
            
            else:
                raise ValueError(f"Unknown observable type: {observable_type}")
            
            observables[n] = float(np.real(obs_value))
        
        return observables
    
    def correlation_function(self, operator_A: qt.Qobj, operator_B: qt.Qobj, 
                           times: np.ndarray, initial_state: qt.Qobj) -> np.ndarray:
        """
        Compute two-time correlation function <A(0)B(t)>.
        
        Args:
            operator_A, operator_B (qt.Qobj): Operators for correlation
            times (np.ndarray): Time points
            initial_state (qt.Qobj): Initial state
            
        Returns:
            np.ndarray: Correlation function values
        """
        correlations = []
        
        # Evolve B(t) = exp(iHt) B exp(-iHt)
        for t in times:
            U_t = (-1j * self.hamiltonian * t).expm()
            U_t_dag = U_t.dag()
            
            B_t = U_t_dag * operator_B * U_t
            
            # Correlation: <initial|A†B(t)|initial>
            correlation = qt.expect(operator_A.dag() * B_t, initial_state)
            correlations.append(correlation)
        
        return np.array(correlations)

class ObservablePredictor:
    """
    Predicts physical observables for Kaluza-Klein modes using the Z framework.
    """
    
    def __init__(self, kk_tower: KaluzaKleinTower):
        """
        Initialize observable predictor.
        
        Args:
            kk_tower (KaluzaKleinTower): Kaluza-Klein tower instance
        """
        self.kk_tower = kk_tower
    
    def predict_mass_spectrum(self, n_modes: int = 20) -> Dict[str, np.ndarray]:
        """
        Predict mass spectrum and related observables.
        
        Args:
            n_modes (int): Number of modes to predict
            
        Returns:
            Dict[str, np.ndarray]: Predicted observables
        """
        modes = np.arange(1, n_modes + 1)
        masses = np.array([float(self.kk_tower.mass_tower(n)) for n in modes])
        energies = np.array([float(self.kk_tower.energy_tower(n)) for n in modes])
        
        # Domain shift correlations
        domain_shifts = []
        Z_values = []
        
        for n in modes:
            delta_n, Z_val = self.kk_tower.domain_shift_relation(n)
            domain_shifts.append(float(delta_n))
            Z_values.append(float(Z_val))
        
        domain_shifts = np.array(domain_shifts)
        Z_values = np.array(Z_values)
        
        return {
            'modes': modes,
            'masses': masses,
            'energies': energies,
            'domain_shifts': domain_shifts,
            'Z_values': Z_values
        }
    
    def predict_transitions(self, n_modes: int = 10) -> Dict[str, np.ndarray]:
        """
        Predict transition rates between Kaluza-Klein modes.
        
        Args:
            n_modes (int): Number of modes to consider
            
        Returns:
            Dict[str, np.ndarray]: Transition predictions
        """
        transition_matrix = np.zeros((n_modes, n_modes))
        energy_gaps = np.zeros((n_modes, n_modes))
        
        for i in range(n_modes):
            for j in range(n_modes):
                n_i, n_j = i + 1, j + 1
                
                # Energy gap
                E_i = float(self.kk_tower.energy_tower(n_i))
                E_j = float(self.kk_tower.energy_tower(n_j))
                energy_gaps[i, j] = abs(E_j - E_i)
                
                # Transition rate (simplified model based on energy gap)
                if i != j:
                    # Rate proportional to 1/ΔE for allowed transitions
                    delta_E = abs(E_j - E_i)
                    if delta_E > 0:
                        transition_matrix[i, j] = 1.0 / delta_E
        
        return {
            'transition_matrix': transition_matrix,
            'energy_gaps': energy_gaps
        }

def simulate_kaluza_klein_observables(compactification_radius: float = 1e-16,
                                    n_modes: int = 10,
                                    evolution_time: float = 1.0,
                                    n_time_steps: int = 100) -> Dict:
    """
    Comprehensive simulation of Kaluza-Klein observables.
    
    Args:
        compactification_radius (float): Compactification radius R
        n_modes (int): Number of KK modes to simulate
        evolution_time (float): Total evolution time
        n_time_steps (int): Number of time steps
        
    Returns:
        Dict: Complete simulation results
    """
    # Initialize Kaluza-Klein tower
    kk_tower = KaluzaKleinTower(compactification_radius)
    
    # Initialize quantum simulator
    simulator = KaluzaKleinQuantumSimulator(kk_tower, n_modes)
    
    # Initialize observable predictor
    predictor = ObservablePredictor(kk_tower)
    
    # Predict mass spectrum
    mass_predictions = predictor.predict_mass_spectrum(n_modes)
    
    # Predict transitions
    transition_predictions = predictor.predict_transitions(n_modes)
    
    # Compute energy spectrum
    eigenvalues, eigenvectors = simulator.energy_spectrum()
    
    # Simulate time evolution
    times = np.linspace(0, evolution_time, n_time_steps)
    initial_state = simulator.basis_states[0]  # Ground state
    evolved_states = simulator.time_evolution(initial_state, times)
    
    # Compute observables for different masses
    position_obs = simulator.mass_dependent_observables('position')
    momentum_obs = simulator.mass_dependent_observables('momentum')
    energy_obs = simulator.mass_dependent_observables('energy')
    
    # Compile results
    results = {
        'kk_tower': kk_tower,
        'mass_predictions': mass_predictions,
        'transition_predictions': transition_predictions,
        'energy_spectrum': {
            'eigenvalues': eigenvalues,
            'eigenvectors': eigenvectors
        },
        'time_evolution': {
            'times': times,
            'evolved_states': evolved_states
        },
        'observables': {
            'position': position_obs,
            'momentum': momentum_obs,
            'energy': energy_obs
        },
        'parameters': {
            'compactification_radius': compactification_radius,
            'n_modes': n_modes,
            'evolution_time': evolution_time
        }
    }
    
    return results

def visualize_kaluza_klein_spectrum(results: Dict, save_path: str = None) -> None:
    """
    Visualize Kaluza-Klein spectrum and observables.
    
    Args:
        results (Dict): Simulation results from simulate_kaluza_klein_observables
        save_path (str, optional): Path to save the plot
    """
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    
    # Mass spectrum
    mass_data = results['mass_predictions']
    axes[0, 0].plot(mass_data['modes'], mass_data['masses'], 'bo-', label='Masses m_n = n/R')
    axes[0, 0].set_xlabel('Mode number n')
    axes[0, 0].set_ylabel('Mass')
    axes[0, 0].set_title('Kaluza-Klein Mass Spectrum')
    axes[0, 0].legend()
    axes[0, 0].grid(True)
    
    # Energy spectrum
    axes[0, 1].plot(mass_data['modes'], mass_data['energies'], 'ro-', label='Energies E_n')
    axes[0, 1].set_xlabel('Mode number n')
    axes[0, 1].set_ylabel('Energy')
    axes[0, 1].set_title('Energy Spectrum')
    axes[0, 1].legend()
    axes[0, 1].grid(True)
    
    # Domain shifts correlation
    axes[1, 0].plot(mass_data['masses'], mass_data['domain_shifts'], 'go-', label='Domain shifts Δ_n')
    axes[1, 0].set_xlabel('Mass m_n')
    axes[1, 0].set_ylabel('Domain shift Δ_n')
    axes[1, 0].set_title('Mass vs Domain Shift')
    axes[1, 0].legend()
    axes[1, 0].grid(True)
    
    # Z framework values
    axes[1, 1].plot(mass_data['modes'], mass_data['Z_values'], 'mo-', label='Z = n(Δ_n/Δ_max)')
    axes[1, 1].set_xlabel('Mode number n')
    axes[1, 1].set_ylabel('Z value')
    axes[1, 1].set_title('Z Framework Values')
    axes[1, 1].legend()
    axes[1, 1].grid(True)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Plot saved to {save_path}")
    else:
        plt.savefig('kaluza_klein_spectrum.png', dpi=300, bbox_inches='tight')
        print("Plot saved to kaluza_klein_spectrum.png")
    
    plt.close()