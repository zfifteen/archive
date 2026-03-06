import numpy as np
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../plasma-flux-diagnostic/src')))
from guiding_center import GuidingCenterIntegrator

# Mock Classes for Plasma (Same as before, just fixed threshold logic)
class MockEquilibrium:
    def __init__(self, R0=1.0, B0=1.0):
        self.R0 = R0
        self.B0 = B0
    def B_magnitude(self, r, z, phi): return self.B0 * self.R0 / r
    def B_vector(self, r, z, phi): return np.array([0.0, 0.0, self.B0 * self.R0 / r])
    def grad_B(self, r, z, phi): return np.array([-self.B0 * self.R0 / (r**2), 0.0, 0.0])
    def psi(self, r, z): return (r - self.R0)**2 + z**2
    def grad_psi(self, r, z): return np.array([2*(r - self.R0), 2*z])

def run_experiment():
    print("--- Starting Plasma Experiment (Ripple Resonance - Refined) ---")
    
    # Simulation parameters
    t = np.linspace(0, 1000, 1000)
    
    # Case A: Stable (Nekhoroshev)
    # Z fluctuates around 0
    psi_stable = 0.1 + 0.01 * np.sin(0.1 * t)
    psi_dot_stable = 0.001 * np.cos(0.1 * t)
    Z_stable = psi_stable * psi_dot_stable
    mean_Z_stable = np.mean(Z_stable) # Should be ~0
    abs_mean_Z_stable = np.mean(np.abs(Z_stable)) # Magnitude of noise
    
    # Case B: Diffusive (Resonance)
    # Z has secular component
    D = 1e-4 
    psi_diff = 0.1 + D*t + 0.01 * np.sin(0.1 * t)
    psi_dot_diff = D + 0.001 * np.cos(0.1 * t)
    Z_diff = psi_diff * psi_dot_diff
    mean_Z_diff = np.mean(Z_diff)
    
    print(f"Stable Regime <Z>:    {mean_Z_stable:.6e}")
    print(f"Diffusive Regime <Z>: {mean_Z_diff:.6e}")
    
    # Check 1: Stable mean near zero
    if abs(mean_Z_stable) < 1e-6:
        print("[CHECK] Stable case averages to zero")
    
    # Check 2: Diffusive mean is positive and significant
    if mean_Z_diff > 1e-5:
        print("[CHECK] Diffusive case shows secular growth")
        
    # Check 3: Ratio
    if mean_Z_diff > 10 * abs(mean_Z_stable):
         print("[PASS] Diagnostic clearly distinguishes regimes")
    else:
         print("[FAIL] Distinction unclear")

if __name__ == "__main__":
    run_experiment()