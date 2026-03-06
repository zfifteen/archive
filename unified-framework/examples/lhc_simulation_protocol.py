"""
LHC Simulation Protocol: Testing Charge as v_w Motion

This module provides a comprehensive simulation protocol for testing the
gravity/electromagnetism unification model against hypothetical LHC data analogs.

The protocol validates:
1. Kaluza-Klein tower predictions from w-dimension compactification  
2. Modified electromagnetic interactions due to v_w motion
3. Gravity-EM coupling signatures in high-energy collisions
4. Cross-sections for extra-dimensional resonance production

Experimental observables are compared against Standard Model predictions
to identify signatures of the unified Z framework.
"""

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import json
from datetime import datetime
import sys
import os

# Add core to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from core.charge_simulation import ChargeSimulation, ChargedParticle, R_COMPACTIFICATION, ALPHA_EM

class LHCSimulationProtocol:
    """
    Comprehensive protocol for testing v_w charge model against LHC-like data.
    """
    
    def __init__(self, output_dir="lhc_simulation_results"):
        self.output_dir = output_dir
        self.results = {}
        self.simulation_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Standard Model reference values for comparison
        self.sm_references = {
            'proton_radius': 0.8775e-15,  # meters
            'electron_mass': 0.511,       # MeV
            'proton_mass': 938.3,         # MeV
            'alpha_em': 1/137.036,        # Fine structure constant
            'planck_mass': 1.22e19        # GeV
        }
        
    def run_energy_scan(self, energy_range=(7000, 14000), num_points=20):
        """
        Scan collision energies from 7-14 TeV testing v_w signatures.
        
        Args:
            energy_range: (min_energy, max_energy) in GeV
            num_points: Number of energy points to test
            
        Returns:
            energy_scan_data: Results for each energy point
        """
        energies = np.linspace(energy_range[0], energy_range[1], num_points)
        scan_results = []
        
        print(f"Running energy scan: {energy_range[0]}-{energy_range[1]} GeV ({num_points} points)")
        
        for i, energy in enumerate(energies):
            print(f"  Energy point {i+1}/{num_points}: {energy:.0f} GeV")
            
            sim = ChargeSimulation()
            collision_data = sim.simulate_lhc_collision(energy)
            
            # Extract key observables
            result = {
                'energy_gev': energy,
                'w_signature': collision_data['w_dimension_signature'],
                'kk_modes_count': len(collision_data['kaluza_klein_modes']),
                'max_kk_mass': max([mode['mass'] for mode in collision_data['kaluza_klein_modes']]),
                'unified_curvature': collision_data['unified_curvature_beam1'],
                'em_gravity_coupling': collision_data['em_gravity_coupling'],
                'modified_coulomb': collision_data['predicted_signatures']['modified_coulomb_scattering']
            }
            scan_results.append(result)
            
        self.results['energy_scan'] = scan_results
        return scan_results
        
    def test_kaluza_klein_production(self, beam_energy=14000):
        """
        Test production cross-sections for Kaluza-Klein modes.
        
        Compares predicted KK tower against Standard Model background
        to identify resonance signatures.
        """
        print(f"Testing KK production at {beam_energy} GeV")
        
        sim = ChargeSimulation()
        kk_modes = sim.compute_kaluza_klein_modes(n_max=20)
        
        # Compute production rates and detectability
        kk_analysis = []
        for mode in kk_modes:
            # Predicted production cross-section (pb)
            sigma_production = mode['production_cross_section'] * 1e12  # Convert to pb
            
            # Background estimate (QCD continuum)
            sigma_background = (ALPHA_EM**2) / (mode['mass']**2) * 1e10
            
            # Signal-to-background ratio
            s_over_b = sigma_production / sigma_background if sigma_background > 0 else np.inf
            
            # Detectability criterion (S/√B > 5 for discovery)
            luminosity = 150  # fb^-1 (typical LHC integrated luminosity)
            n_signal = sigma_production * luminosity * 1000  # Number of signal events
            n_background = sigma_background * luminosity * 1000
            significance = n_signal / np.sqrt(n_background) if n_background > 0 else np.inf
            
            kk_analysis.append({
                'mode_n': mode['n'],
                'mass_gev': mode['mass'],
                'cross_section_pb': sigma_production,
                'background_pb': sigma_background,
                's_over_b': s_over_b,
                'significance': significance,
                'discoverable': significance > 5.0
            })
            
        self.results['kk_production'] = kk_analysis
        
        # Count discoverable modes
        discoverable_modes = sum(1 for mode in kk_analysis if mode['discoverable'])
        print(f"  Predicted discoverable KK modes: {discoverable_modes}/{len(kk_analysis)}")
        
        return kk_analysis
        
    def compare_electromagnetic_interactions(self):
        """
        Compare electromagnetic interactions: Standard Model vs v_w model.
        
        Tests modifications to Coulomb scattering, pair production, etc.
        due to w-dimension velocity effects.
        """
        print("Comparing electromagnetic interactions")
        
        # Test particles with varying charge and mass
        test_scenarios = [
            {'name': 'electron', 'charge': -1, 'mass': 0.000511},
            {'name': 'muon', 'charge': -1, 'mass': 0.106},
            {'name': 'proton', 'charge': 1, 'mass': 0.938},
            {'name': 'heavy_ion', 'charge': 26, 'mass': 52.0}  # Iron-56
        ]
        
        em_comparison = []
        
        for scenario in test_scenarios:
            # Standard Model prediction (Coulomb scattering)
            sm_cross_section = (4 * np.pi * ALPHA_EM**2) / (scenario['mass']**2)
            
            # v_w model prediction  
            particle = ChargedParticle(scenario['charge'], scenario['mass'], n_index=10)
            
            # Modified cross-section includes v_w effects
            v_w_factor = 1 + (particle.v_w / 1.0)**2  # Correction factor
            vw_cross_section = sm_cross_section * v_w_factor
            
            # Relative deviation from SM
            deviation = (vw_cross_section - sm_cross_section) / sm_cross_section * 100
            
            em_comparison.append({
                'particle': scenario['name'],
                'charge': scenario['charge'],
                'mass_gev': scenario['mass'],
                'v_w': particle.v_w,
                'sm_cross_section': sm_cross_section,
                'vw_cross_section': vw_cross_section,
                'deviation_percent': deviation,
                'measurable': abs(deviation) > 1.0  # >1% deviation potentially measurable
            })
            
        self.results['em_comparison'] = em_comparison
        
        # Summary statistics
        measurable_deviations = sum(1 for comp in em_comparison if comp['measurable'])
        max_deviation = max(abs(comp['deviation_percent']) for comp in em_comparison)
        
        print(f"  Particles with measurable EM deviations: {measurable_deviations}/{len(em_comparison)}")
        print(f"  Maximum deviation from SM: {max_deviation:.2f}%")
        
        return em_comparison
        
    def test_gravity_em_unification(self):
        """
        Test signatures of gravity-electromagnetic unification.
        
        Searches for correlated gravitational and electromagnetic effects
        that would indicate unified origin via v_w motion.
        """
        print("Testing gravity-EM unification signatures")
        
        # Range of particle masses and charges
        masses = np.logspace(-3, 2, 10)  # 1 MeV to 100 GeV
        charges = [-2, -1, 0, 1, 2]
        
        unification_data = []
        
        for mass in masses:
            for charge in charges:
                if charge == 0:
                    continue  # Skip neutral particles for EM analysis
                    
                particle = ChargedParticle(charge, mass, n_index=5)
                
                # Measure gravity and EM curvatures separately and unified
                gravity_curve = particle.get_gravitational_curvature()
                em_curve = particle.get_electromagnetic_curvature()
                unified_curve = particle.get_unified_curvature()
                
                # Interaction strength (beyond simple sum)
                interaction_strength = unified_curve - (gravity_curve + em_curve)
                relative_interaction = interaction_strength / (gravity_curve + em_curve) if (gravity_curve + em_curve) > 0 else 0
                
                unification_data.append({
                    'mass_gev': mass,
                    'charge': charge,
                    'v_w': particle.v_w,
                    'gravity_curvature': gravity_curve,
                    'em_curvature': em_curve,
                    'unified_curvature': unified_curve,
                    'interaction_strength': interaction_strength,
                    'relative_interaction': relative_interaction * 100  # Percent
                })
                
        self.results['unification_test'] = unification_data
        
        # Statistical analysis
        interactions = [data['relative_interaction'] for data in unification_data]
        mean_interaction = np.mean(interactions)
        std_interaction = np.std(interactions)
        
        print(f"  Mean gravity-EM interaction: {mean_interaction:.3f}%")
        print(f"  Interaction variability: ±{std_interaction:.3f}%")
        
        return unification_data
        
    def generate_lhc_comparison_dataset(self):
        """
        Generate synthetic dataset matching LHC data format for comparison.
        
        Creates realistic collision events with v_w model predictions
        that could be compared against actual LHC measurements.
        """
        print("Generating LHC comparison dataset")
        
        # Simulate 10,000 collision events at 13 TeV
        num_events = 10000
        beam_energy = 13000  # GeV
        
        events = []
        
        for event_id in range(num_events):
            # Random impact parameter (0-2 fm)
            impact_parameter = np.random.exponential(0.5)
            
            # Simulate collision
            sim = ChargeSimulation()
            collision = sim.simulate_lhc_collision(beam_energy, impact_parameter)
            
            # Extract observables in LHC format
            event = {
                'event_id': event_id,
                'beam_energy': beam_energy,
                'impact_parameter': impact_parameter,
                'invariant_mass': np.random.normal(125, 5),  # Higgs-like peak
                'missing_energy': np.random.exponential(20),
                'jet_multiplicity': np.random.poisson(4),
                'w_signature': collision['w_dimension_signature'],
                'kk_resonance_prob': min(collision['w_dimension_signature'] * 0.1, 1.0),
                'unified_coupling': collision['em_gravity_coupling'],
                'sm_prediction': 1.0,  # Normalized SM expectation
                'vw_prediction': 1.0 + collision['w_dimension_signature'] * 0.01
            }
            events.append(event)
            
        # Convert to DataFrame for analysis
        df_events = pd.DataFrame(events)
        
        # Save dataset
        output_file = os.path.join(self.output_dir, f"lhc_comparison_dataset_{self.simulation_id}.csv")
        df_events.to_csv(output_file, index=False)
        
        self.results['synthetic_dataset'] = {
            'num_events': num_events,
            'filename': output_file,
            'summary_stats': {
                'mean_w_signature': float(df_events['w_signature'].mean()),
                'std_w_signature': float(df_events['w_signature'].std()),
                'max_kk_probability': float(df_events['kk_resonance_prob'].max()),
                'mean_vw_enhancement': float(df_events['vw_prediction'].mean() - 1.0)
            }
        }
        
        print(f"  Generated {num_events} events")
        print(f"  Mean w-signature: {df_events['w_signature'].mean():.6f}")
        print(f"  Dataset saved: {output_file}")
        
        return df_events
        
    def create_visualization_plots(self):
        """Create visualization plots for simulation results."""
        print("Creating visualization plots")
        
        fig, axes = plt.subplots(2, 2, figsize=(12, 10))
        fig.suptitle(f'LHC v_w Simulation Results - {self.simulation_id}')
        
        # Plot 1: Energy scan - w-signature vs energy
        if 'energy_scan' in self.results:
            energy_data = self.results['energy_scan']
            energies = [d['energy_gev'] for d in energy_data]
            w_sigs = [d['w_signature'] for d in energy_data]
            
            axes[0,0].plot(energies, w_sigs, 'b-o', markersize=4)
            axes[0,0].set_xlabel('Beam Energy (GeV)')
            axes[0,0].set_ylabel('W-dimension Signature')
            axes[0,0].set_title('Energy Dependence of v_w Effects')
            axes[0,0].grid(True, alpha=0.3)
            
        # Plot 2: KK mode masses
        if 'kk_production' in self.results:
            kk_data = self.results['kk_production']
            modes = [d['mode_n'] for d in kk_data]
            masses = [d['mass_gev'] for d in kk_data]
            
            axes[0,1].semilogy(modes, masses, 'r-s', markersize=4)
            axes[0,1].set_xlabel('KK Mode n')
            axes[0,1].set_ylabel('Mass (GeV)')
            axes[0,1].set_title('Kaluza-Klein Tower')
            axes[0,1].grid(True, alpha=0.3)
            
        # Plot 3: EM interaction deviations
        if 'em_comparison' in self.results:
            em_data = self.results['em_comparison']
            particles = [d['particle'] for d in em_data]
            deviations = [d['deviation_percent'] for d in em_data]
            
            colors = ['red' if abs(d) > 1.0 else 'blue' for d in deviations]
            axes[1,0].bar(range(len(particles)), deviations, color=colors, alpha=0.7)
            axes[1,0].set_xticks(range(len(particles)))
            axes[1,0].set_xticklabels(particles, rotation=45)
            axes[1,0].set_ylabel('Deviation from SM (%)')
            axes[1,0].set_title('EM Interaction Modifications')
            axes[1,0].axhline(y=1, color='gray', linestyle='--', alpha=0.5)
            axes[1,0].axhline(y=-1, color='gray', linestyle='--', alpha=0.5)
            axes[1,0].grid(True, alpha=0.3)
            
        # Plot 4: Gravity-EM unification correlation
        if 'unification_test' in self.results:
            unif_data = self.results['unification_test']
            gravity_curves = [d['gravity_curvature'] for d in unif_data]
            em_curves = [d['em_curvature'] for d in unif_data]
            
            axes[1,1].loglog(gravity_curves, em_curves, 'g.', alpha=0.6)
            axes[1,1].set_xlabel('Gravitational Curvature')
            axes[1,1].set_ylabel('EM Curvature')
            axes[1,1].set_title('Gravity-EM Correlation')
            axes[1,1].grid(True, alpha=0.3)
            
        plt.tight_layout()
        
        # Save plot
        plot_file = os.path.join(self.output_dir, f"lhc_simulation_plots_{self.simulation_id}.png")
        plt.savefig(plot_file, dpi=150, bbox_inches='tight')
        plt.close()
        
        print(f"  Plots saved: {plot_file}")
        return plot_file
        
    def save_results(self):
        """Save all simulation results to JSON file."""
        output_file = os.path.join(self.output_dir, f"lhc_simulation_results_{self.simulation_id}.json")
        
        # Add metadata
        self.results['metadata'] = {
            'simulation_id': self.simulation_id,
            'timestamp': datetime.now().isoformat(),
            'compactification_scale': R_COMPACTIFICATION,
            'fine_structure_constant': ALPHA_EM,
            'framework': 'Z Framework Charge as v_w Motion'
        }
        
        # Convert numpy types to native Python for JSON serialization
        def convert_numpy(obj):
            if isinstance(obj, np.integer):
                return int(obj)
            elif isinstance(obj, np.floating):
                return float(obj)
            elif isinstance(obj, np.ndarray):
                return obj.tolist()
            return obj
            
        def deep_convert(obj):
            if isinstance(obj, dict):
                return {k: deep_convert(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [deep_convert(v) for v in obj]
            else:
                return convert_numpy(obj)
                
        converted_results = deep_convert(self.results)
        
        with open(output_file, 'w') as f:
            json.dump(converted_results, f, indent=2)
            
        print(f"Results saved: {output_file}")
        return output_file
        
    def run_full_protocol(self):
        """Execute complete LHC simulation protocol."""
        print(f"Starting LHC Simulation Protocol - ID: {self.simulation_id}")
        print("=" * 60)
        
        # Run all test phases
        self.run_energy_scan()
        self.test_kaluza_klein_production()
        self.compare_electromagnetic_interactions()
        self.test_gravity_em_unification()
        self.generate_lhc_comparison_dataset()
        
        # Generate outputs
        self.create_visualization_plots()
        results_file = self.save_results()
        
        print("=" * 60)
        print("LHC Simulation Protocol Complete")
        print(f"Results directory: {self.output_dir}")
        print(f"Results file: {results_file}")
        
        # Summary of key findings
        if 'energy_scan' in self.results:
            max_w_sig = max(d['w_signature'] for d in self.results['energy_scan'])
            print(f"Maximum w-signature: {max_w_sig:.6f}")
            
        if 'kk_production' in self.results:
            discoverable = sum(1 for d in self.results['kk_production'] if d['discoverable'])
            print(f"Discoverable KK modes: {discoverable}")
            
        if 'em_comparison' in self.results:
            measurable = sum(1 for d in self.results['em_comparison'] if d['measurable'])
            print(f"Measurable EM deviations: {measurable}")
            
        return self.results

def main():
    """Run the LHC simulation protocol."""
    protocol = LHCSimulationProtocol()
    results = protocol.run_full_protocol()
    return results

if __name__ == "__main__":
    main()