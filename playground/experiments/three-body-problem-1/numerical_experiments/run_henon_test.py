import numpy as np
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../beam-flux-diagnostic/src/xsuite_module')))
class MockParticles:
    def __init__(self, x, px):
        self.x = x
        self.px = px

from flux_diagnostic import FluxDiagnostic

def henon_map(x, p, nu, epsilon):
    theta = 2 * np.pi * nu
    c, s = np.cos(theta), np.sin(theta)
    x = np.clip(x, -1e4, 1e4) # Prevent overflow
    p = np.clip(p, -1e4, 1e4)
    term = p - epsilon * x**2
    x_new = x * c - term * s
    p_new = x * s + term * c
    return x_new, p_new

def run_experiment():
    print("--- Starting Accelerator Experiment (Hénon Map - Unstable) ---")
    
    n_particles = 5000
    n_turns = 1000
    nu = 0.21 # Near 5th order resonance
    
    epsilons = [0.0, 5.0] 
    
    results = {}
    
    for eps in epsilons:
        np.random.seed(42)
        x = np.random.normal(0, 0.1, n_particles)
        p = np.random.normal(0, 0.1, n_particles)
        
        particles = MockParticles(x, p)
        diag = FluxDiagnostic(particles)
        
        z_values = []
        
        for t in range(n_turns):
            diag.update(t, dt=1.0, energy=1.0)
            x, p = henon_map(x, p, nu, eps)
            particles.x = x
            particles.px = p
            
            if len(diag.z_history) > 0:
                z_values.append(abs(diag.z_history[-1][1]))
                
        avg_z = np.mean(z_values)
        results[eps] = avg_z
        print(f"Epsilon: {eps:.2f} | <|Z_sigma|>: {avg_z:.6e}")

    ratio = results[5.0] / (results[0.0] + 1e-15)
    print(f"Instability Contrast Ratio: {ratio:.1f}")
    
    if ratio > 10.0:
        print("[PASS] Diagnostic detects instability")
    else:
        print("[FAIL] Contrast too low")

if __name__ == "__main__":
    run_experiment()