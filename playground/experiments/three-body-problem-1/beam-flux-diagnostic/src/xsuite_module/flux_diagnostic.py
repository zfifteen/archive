class FluxDiagnostic:
    def __init__(self, particles, normalization='energy'):
        self.particles = particles
        self.sigma_history = []
        self.z_history = []
        self.normalization = normalization
        
    def compute_sigma(self):
        """Compute RMS beam size (confinement functional Q)"""
        import numpy as np
        x = self.particles.x
        return np.sqrt(np.mean(x**2))
        
    def compute_z_sigma(self, sigma_current, sigma_prev, dt, energy):
        """Compute Z_sigma = sigma * sigma_dot / Energy"""
        sigma_dot = (sigma_current - sigma_prev) / dt
        return sigma_current * sigma_dot / energy
        
    def update(self, turn_number, dt, energy):
        """Update diagnostic state for a new turn"""
        sigma_current = self.compute_sigma()
        
        if len(self.sigma_history) > 0:
            sigma_prev = self.sigma_history[-1]
            z_val = self.compute_z_sigma(sigma_current, sigma_prev, dt, energy)
            self.z_history.append((turn_number, z_val))
        
        self.sigma_history.append(sigma_current)
