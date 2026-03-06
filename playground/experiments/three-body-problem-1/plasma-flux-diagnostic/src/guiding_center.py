import numpy as np
from scipy.integrate import solve_ivp

class GuidingCenterIntegrator:
    def __init__(self, equilibrium, perturbation_field, mass=1.67e-27, charge=1.6e-19, mu=1e-16):
        self.eq = equilibrium  # Object with B(r,z), psi(r,z), etc.
        self.pert = perturbation_field  # Ripple or error field model
        self.z_history = []
        self.m = mass
        self.q = charge
        self.mu = mu
        
    def compute_drifts(self, r, z, phi, v_para, B_vec, grad_B):
        """Compute combined ExB, Curvature, and Grad-B drifts"""
        B_mag = np.linalg.norm(B_vec)
        b_unit = B_vec / B_mag
        
        # Cross product terms (simplified for demonstration)
        # v_gradB = (mu / q B^2) B x gradB
        # v_curv = (m v_para^2 / q B^2) B x (b.grad)b
        
        # Placeholder for full drift physics
        v_drift = np.zeros(3) 
        return v_drift
    
    def guiding_center_rhs(self, t, y):
        """
        y = [r, z, phi, p_para]
        Returns dy/dt
        """
        r, z, phi, p_para = y
        
        # Evaluate fields
        B_mag = self.eq.B_magnitude(r, z, phi)
        B_vec = self.eq.B_vector(r, z, phi)
        grad_B = self.eq.grad_B(r, z, phi)
        
        # Parallel velocity
        v_para = p_para / (self.m * B_mag)
        
        # Drifts
        v_drift = self.compute_drifts(r, z, phi, v_para, B_vec, grad_B)
        
        # Equations of motion (guiding-center)
        dr_dt = v_para * B_vec[0]/B_mag + v_drift[0]
        dz_dt = v_para * B_vec[1]/B_mag + v_drift[1]
        dphi_dt = v_para * B_vec[2]/(r*B_mag) + v_drift[2]/r
        dp_para_dt = -self.mu * grad_B[2] # - self.q * self.eq.E_para(...)
        
        return [dr_dt, dz_dt, dphi_dt, dp_para_dt]
    
    def compute_z_psi(self, r, z, dr_dt, dz_dt, energy):
        """Compute flux diagnostic Z = psi * psi_dot / E"""
        psi = self.eq.psi(r, z)
        grad_psi = self.eq.grad_psi(r, z)
        psi_dot = dr_dt * grad_psi[0] + dz_dt * grad_psi[1]
        return psi * psi_dot / energy
