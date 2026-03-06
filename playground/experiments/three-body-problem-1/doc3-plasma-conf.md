# Document 3: Plasma Confinement Applications

**Author:** Dionisio Alberto Lopez III  
**Date:** January 30, 2026  
**Purpose:** Instructions for applying the generalized Z_Q flux diagnostic to magnetically confined plasma physics at the guiding-center or single-particle level

---

## Objective

Adapt and validate the flux-based diagnostic for plasma confinement physics, focusing on pre-collisional, resonance-driven transport mechanisms that bridge single-particle dynamics to collective transport.

---

## Strategic Context

**Why plasma physics is high-priority:**
- Arnold diffusion explicitly discussed in recent plasma literature (2026 review in Physics of Plasmas)
- Guiding-center dynamics in perturbed fields naturally near-integrable
- Major gap: quantitative diagnostics for resonance-driven leakage before collisional transport dominates
- Bridge from single-particle to kinetic/fluid descriptions via aggregation
- High-value facilities: ITER (under construction), existing tokamaks (DIII-D, JET, ASDEX-U), stellarators (W7-X, LHD)

**Key difference from accelerators:**
- Multiple timescales: gyration (~ns) << bounce/transit (~μs) << collisional (~ms) << confinement (~s)
- Dominant physics: magnetic field geometry, not nonlinear focusing
- Perturbations: toroidal field ripple, MHD instabilities, error fields, not multipole magnets

---

## Phase 1: System Formulation and Q Selection

### Guiding-Center Hamiltonian

**Reduced dynamics (gyro-averaged):**

For particle with charge q, mass m, magnetic moment μ:
```
H_gc = (1/2m)(p_∥ - qA_∥)² + μB(r) + qΦ(r)
```

Where:
- p_∥: parallel momentum (along B)
- A_∥: parallel component of vector potential
- μ = mv_⊥²/(2B): adiabatic invariant (magnetic moment)
- B(r): magnetic field magnitude
- Φ(r): electrostatic potential

**Near-integrable structure:**

For axisymmetric tokamak:
```
H_gc = H_0(ℐ) + ε H_1(ℐ, θ, ϕ, t)
```

Where:
- ℐ: action variables (energy, toroidal momentum, μ)
- H_0: axisymmetric equilibrium (integrable)
- ε H_1: perturbations (ripple, error fields, MHD)
- (θ, ϕ): poloidal and toroidal angles

### Confinement Functional Candidates

**Option 1: Radial flux surface label (strongest choice)**

For tokamak with nested flux surfaces:
```
Q = ψ(r, z)
```

Where ψ is the poloidal magnetic flux function defining surfaces.

**Advantages:**
- Natural confinement coordinate (ψ surfaces = confinement boundaries)
- Level sets exactly separate confined vs. escaping orbits
- Standard tokamak coordinate
- Related to plasma pressure, density profiles

**Challenges:**
- Requires equilibrium reconstruction to compute ψ(r,z) from field data
- For stellarators, flux surface quality degrades

**Option 2: Bounce/banana orbit width**

For trapped particles in tokamak:
```
Q = Δr_banana = 2∫[r_max - r_min]
```

**Advantages:**
- Directly measures radial excursion of particle
- Relevant for ripple-trapped and barely-trapped populations
- Computable from single orbit without global equilibrium

**Challenges:**
- Only meaningful for trapped particles (not passing)
- Different Q needed for different orbit topology

**Option 3: Second moment of radial distribution**

For ensemble of particles:
```
Q = ⟨r²⟩ = (1/N)Σ r_i²
```

Or relative to flux surface:
```
Q = ⟨(r - r_flux)²⟩
```

**Advantages:**
- Analogous to beam emittance in accelerators
- Natural for ensemble/kinetic description
- Smooth, always computable

**Challenges:**
- Requires ensemble tracking (computationally intensive)
- Less direct connection to transport than ψ

**Selection protocol:**
1. For single-particle studies: Use ψ (Option 1)
2. For orbit-classification studies: Use Δr_banana (Option 2) for trapped, ψ for passing
3. For kinetic simulations: Use ⟨(r-r_flux)²⟩ (Option 3)

### Flux Diagnostic Definition

**For single particle with Q = ψ:**
```
Z_ψ = ψ · ψ̇ / H_gc
```

**For ensemble with Q = ⟨r²⟩:**
```
Z_r = ⟨r²⟩ · d⟨r²⟩/dt / E_total
```

**For Q = Δr_banana (trapped particles):**
```
Z_Δr = Δr · (dΔr/dt) / H_gc
```

**Interpretation:**
- ⟨Z_Q⟩ ≈ 0: Nekhoroshev confinement (exponentially long orbit before escape)
- ⟨Z_Q⟩ shows secular growth: resonance-driven radial drift, precursor to loss

---

## Phase 2: Theoretical Development

### Virial-Like Identities for Plasma Systems

**Derive Q̈ equation for tokamak:**

For Q = ψ(r, z):
```
ψ̈ = d/dt[{ψ, H_gc}]
   = {ψ̇, H_gc}
   = {{ψ, H_gc}, H_gc}
```

Using guiding-center Poisson bracket structure.

**Key steps:**
1. Express {ψ, H_gc} in terms of guiding-center drifts (∇B drift, curvature drift)
2. Compute second Poisson bracket
3. Identify terms proportional to kinetic energy T and magnetic/electric potential energy
4. Look for structure analogous to c₁T + c₂V (as in virial theorem)

**Expected form (conjecture to verify):**
```
ψ̈ ~ A(ψ)·[mv_∥²] + B(ψ)·[μB] + C(ψ)·[perturbation terms]
```

Where A, B, C are geometric factors depending on equilibrium.

**If virial-like identity exists:** Strong theoretical foundation for Z_ψ diagnostic

**If not:** Z_ψ still valid, but less direct connection to energy partition

### Nekhoroshev Estimates for Tokamak Perturbations

**Perturbation mechanisms to consider:**

1. **Toroidal field ripple:**
   - Finite number of toroidal field coils (e.g., 18 in ITER)
   - Creates N-fold symmetric ripple: δB/B ~ ε_ripple cos(Nϕ)
   - Strength: ε_ripple ~ 10^-3 to 10^-2 at plasma edge

2. **Error fields:**
   - Misalignment of coils
   - Resistive wall modes
   - Strength: ε_err ~ 10^-4 (after correction)

3. **MHD modes:**
   - Tearing modes, ELMs (Edge Localized Modes)
   - Time-dependent perturbations
   - Can be much larger: δB/B ~ 10^-2 to 10^-1 during events

**Nekhoroshev time estimate:**

For ripple perturbation with n degrees of freedom (typically n=3: energy, P_ϕ, μ):
```
T_Nekh ~ (1/ω_bounce) · exp[(ε_0/ε_ripple)^(1/(2n))]
```

Where:
- ω_bounce: bounce frequency (~MHz)
- ε_0: convergence radius of perturbative series
- ε_ripple: ripple strength

**Typical numbers for ITER-like parameters:**
- ε_ripple ~ 10^-3
- ε_0 ~ 0.1 (order unity)
- n = 3
- Predicted T_Nekh ~ 10^-6 s · exp[(0.1/10^-3)^(1/6)] ~ 10^-6 · exp(2) ~ 10 μs

**Comparison to collisional time:** τ_collision ~ 1 ms (at ITER densities)

**Conclusion:** Nekhoroshev regime (10 μs << τ_coll) exists where Z_ψ diagnostic is sensitive to resonance-driven pre-collisional losses.

### Theorems for Plasma Context

**Theorem 1 (Nekhoroshev confinement in perturbed tokamak):**

*Statement:* For a guiding-center Hamiltonian H = H_0 + εH_1 in an axisymmetric tokamak with ripple/error field perturbation ε, if working surfaces satisfy resonance-avoidance and H satisfies steepness conditions, then for times t < T_Nekh:

```
|⟨Z_ψ⟩_t| < C · exp(-κ/ε^α)
```

*Proof strategy:* (10 pages)
- Apply existing Nekhoroshev results for nearly-integrable twist maps
- Map tokamak Poincaré map to abstract symplectic map
- Use bounds on radial drift from ripple theory (Goldston et al.)
- Propagate to ψ̇ via chain rule
- Time-average using ergodic theorem on invariant tori

**Theorem 2 (Resonance-driven radial transport):**

*Statement:* When ripple resonance condition ω_bounce = N·ω_transit is satisfied (trapped particles resonant with ripple periodicity), the flux diagnostic exhibits:

```
⟨Z_ψ⟩ ~ D_ripple · (∂ψ/∂I_bounce) / E
```

Where D_ripple is the ripple-induced diffusion coefficient.

*Proof strategy:* (8 pages)
- Use quasi-linear theory for ripple-resonant transport
- Relate D_ripple to ripple amplitude and resonance width
- Connect radial drift ⟨ṙ⟩ to flux surface motion ⟨ψ̇⟩
- Show time-averaging of Z_ψ isolates secular diffusive term

**Deliverable:** 15-20 page technical note with proofs and numerical validation strategy

---

## Phase 3: Numerical Implementation

### Guiding-Center Orbit Codes

**Primary tools:**

1. **ORBIT** (Oak Ridge Beam Ion Transport code)
   - Standard for fast-ion studies in tokamaks
   - Full 6D orbit integration with collisions
   - Used at DIII-D, NSTX, ITER design

2. **ASCOT** (Accelerated Simulation of Charged Particle Orbits in Tori)
   - Used at JET, ASDEX-U, ITER
   - Monte Carlo approach with variance reduction
   - Includes realistic 3D fields

3. **Custom Python/Julia orbit integrator:**
   - Lightweight for parameter studies
   - Symplectic integrators (e.g., Störmer-Verlet)
   - Full control for Z_ψ implementation

**Implementation in ORBIT:**

```fortran
! Add to orbit tracking loop
SUBROUTINE compute_plasma_flux_diagnostic(r, z, phi, v_para, v_perp, &
                                           psi, energy, z_psi)
  ! Input: particle position (r, z, phi) and velocity (v_∥, v_⊥)
  ! Compute: ψ(r,z) via equilibrium splines
  ! Compute: ψ̇ = {ψ, H} = v_d · ∇ψ (drift velocity · flux surface gradient)
  ! Output: Z_ψ = ψ·ψ̇/E
  
  ! Get psi from equilibrium
  CALL equil_psi(r, z, psi, grad_psi_r, grad_psi_z)
  
  ! Compute drifts
  CALL compute_drifts(r, z, v_para, v_perp, B_field, v_drift_r, v_drift_z)
  
  ! ψ̇ = v_drift · ∇ψ
  psi_dot = v_drift_r * grad_psi_r + v_drift_z * grad_psi_z
  
  ! Z diagnostic
  z_psi = psi * psi_dot / energy
  
END SUBROUTINE
```

**Custom Python implementation:**

```python
import numpy as np
from scipy.integrate import solve_ivp

class GuidingCenterIntegrator:
    def __init__(self, equilibrium, perturbation_field):
        self.eq = equilibrium  # Object with B(r,z), psi(r,z), etc.
        self.pert = perturbation_field  # Ripple or error field model
        self.z_history = []
        
    def guiding_center_rhs(self, t, y):
        """
        y = [r, z, phi, p_para]
        Returns dy/dt
        """
        r, z, phi, p_para = y
        
        # Evaluate fields
        B = self.eq.B_magnitude(r, z, phi)
        B_vec = self.eq.B_vector(r, z, phi)
        grad_B = self.eq.grad_B(r, z, phi)
        
        # Parallel velocity
        v_para = p_para / (self.m * B)
        
        # Drifts (grad-B, curvature, ExB)
        v_drift = self.compute_drifts(r, z, phi, v_para, B_vec, grad_B)
        
        # Equations of motion (guiding-center)
        dr_dt = v_para * B_vec[0]/B + v_drift[0]
        dz_dt = v_para * B_vec[1]/B + v_drift[1]
        dphi_dt = v_para * B_vec[2]/(r*B) + v_drift[2]/r
        dp_para_dt = -self.mu * grad_B[2] - self.q * self.eq.E_para(r,z,phi)
        
        return [dr_dt, dz_dt, dphi_dt, dp_para_dt]
    
    def compute_z_psi(self, r, z, dr_dt, dz_dt, energy):
        """Compute flux diagnostic"""
        psi = self.eq.psi(r, z)
        grad_psi = self.eq.grad_psi(r, z)
        psi_dot = dr_dt * grad_psi[0] + dz_dt * grad_psi[1]
        return psi * psi_dot / energy
    
    def integrate_with_diagnostic(self, y0, t_span, n_steps=10000):
        """Integrate orbit and compute Z_psi at each step"""
        sol = solve_ivp(self.guiding_center_rhs, t_span, y0, 
                        method='RK45', dense_output=True, max_step=1e-8)
        
        t_eval = np.linspace(t_span[0], t_span[1], n_steps)
        traj = sol.sol(t_eval)
        
        # Compute Z_psi at each point
        for i in range(n_steps):
            r, z = traj[0,i], traj[1,i]
            # Need velocity from RHS evaluation
            y = traj[:,i]
            dydt = self.guiding_center_rhs(t_eval[i], y)
            energy = self.compute_energy(y)
            z_val = self.compute_z_psi(r, z, dydt[0], dydt[1], energy)
            self.z_history.append((t_eval[i], z_val))
        
        return traj, np.array(self.z_history)
```

**Validation tests:**
1. Axisymmetric case (ε=0): Verify Z_ψ ≈ 0 (up to numerical noise)
2. Known ripple-loss rate: Compare ⟨Z_ψ⟩ to analytical predictions (if available)
3. Energy conservation: Ensure H_gc drift < 10^-6 over integration

---

## Phase 4: Numerical Experiments

### Test Case 1: Single-Particle Ripple Resonance

**Setup:**
- Axisymmetric tokamak equilibrium (e.g., ITER-like with circular cross-section)
- Add N-fold ripple: δB/B = ε cos(Nϕ), with N=18, ε = 10^-3
- Initialize barely-trapped particle near ripple resonance: ω_bounce ≈ N·ω_transit

**Protocol:**
1. Integrate guiding-center orbit for 10^4 to 10^6 bounce periods
2. Compute Z_ψ at each time step
3. Time-average: ⟨Z_ψ⟩_T for increasing window T
4. Scan initial conditions: pitch angle λ = v_∥/v, radial position

**Expected results:**
- Away from resonance: ⟨Z_ψ⟩ ~ 10^-6 or smaller (Nekhoroshev)
- At resonance: ⟨Z_ψ⟩ shows secular growth, particle escapes after ~10^4 bounces
- Map resonance structure in (λ, r) space

**Comparison:**
- Traditional method: Track until escape, plot "confined vs. lost" boundary
- Z_ψ method: Identify boundary by onset of secular ⟨Z_ψ⟩ growth
- Advantage: Z_ψ provides early warning before actual loss

### Test Case 2: Ensemble Transport in Stellarator

**Setup:**
- W7-X stellarator magnetic configuration (3D non-axisymmetric)
- Realistic error field from coil misalignment (data from W7-X equilibrium files)
- Initialize 10^4 particles: thermal distribution at core

**Protocol:**
1. Track ensemble for τ_collisionless ~ 1 ms (before collisions matter)
2. Compute ensemble-averaged: ⟨Z_r⟩ where Z_r = ⟨r²⟩·d⟨r²⟩/dt / E
3. Monitor radial diffusion coefficient: D_r ~ ∂⟨r²⟩/∂t
4. Compare: Is ⟨Z_r⟩ proportional to D_r?

**Expected results:**
- Proportionality: ⟨Z_r⟩ ~ D_r (validates Theorem 2)
- Identify "bad" flux surfaces with high ⟨Z_r⟩ (poor confinement)
- Optimize stellarator configuration: minimize ⟨Z_r⟩ over coil-current parameter space

**Deliverable:** Proof-of-concept that Z_r can guide stellarator optimization (connection to quasi-symmetry design principles)

### Test Case 3: Time-Dependent Perturbations (MHD)

**Setup:**
- Tokamak with rotating tearing mode: δB ~ ε(t)·cos(mθ - nϕ - ωt)
- Mode amplitude grows: ε(t) = ε_0·exp(γt), saturates at ε_sat
- Track particle ensemble through mode growth

**Protocol:**
1. Compute Z_ψ for individual particles and ensemble average
2. Correlate ⟨Z_ψ⟩(t) with mode amplitude ε(t)
3. Test hypothesis: ⟨Z_ψ⟩ increases before visible transport/loss

**Application:** Early-warning diagnostic for disruption precursors

---

## Phase 5: Aggregation to Kinetic Transport

### From Single-Particle Z to Collective Diffusion

**Goal:** Bridge microscopic Z_ψ to macroscopic transport coefficient D_⊥

**Theoretical connection:**

For ensemble of particles with distribution f(ψ, v_∥, μ, t):
```
∂f/∂t + v_d·∇f = C[f]  (kinetic equation)
```

Where v_d is drift velocity and C is collision operator.

**Moments of Z_ψ:**

Define phase-space averaged flux:
```
⟨Z_ψ⟩_ensemble = ∫ Z_ψ(particle) · f dψ dv_∥ dμ
```

**Conjecture:** ⟨Z_ψ⟩_ensemble ~ D_⊥ / (τ_E · E_thermal)

Where:
- D_⊥: perpendicular diffusion coefficient (from transport analysis)
- τ_E: energy confinement time (global experimental observable)

**Validation approach:**
1. Simulate ensemble with ORBIT/ASCOT
2. Compute both ⟨Z_ψ⟩_ensemble and D_⊥ (from ∂⟨r²⟩/∂t)
3. Test proportionality
4. If confirmed: Z_ψ provides microscopic justification for phenomenological D_⊥

**Connection to fluid/MHD:**
- In fluid limit, ⟨Z_ψ⟩ → virial-like flux in magnetohydrodynamics
- Potential bridge to existing MHD energy theorems

---

## Phase 6: Experimental Validation (Longer-Term)

### Diagnostic Requirements

**Challenge:** Cannot measure single-particle Z_ψ directly

**Proxy observables:**
1. **Fast-ion loss detectors:**
   - Measure particles hitting first wall
   - Correlate loss rate with computed ⟨Z_ψ⟩ for loss-cone particles
   
2. **Density profile evolution:**
   - Radial transport inferred from ∂n/∂t measurements
   - Compare to predicted ⟨Z_ψ⟩ for thermal population

3. **Beam emission spectroscopy (BES):**
   - Local density fluctuations
   - If Z_ψ sensitive to mode-driven transport, should correlate

**Proposed experiment at DIII-D:**

**Phase A: Controlled ripple scan**
- Intentionally introduce known error field (coil current perturbation)
- Scan amplitude: ε_err from 0 to 10^-3
- Measure: fast-ion loss rate vs. ε_err
- Compute: ⟨Z_ψ⟩ for simulated fast-ion population vs. ε_err
- Compare: Does ⟨Z_ψ⟩ threshold for secular growth match observed loss onset?

**Phase B: MHD precursor detection**
- Monitor plasma approaching tearing mode instability
- Compute ⟨Z_ψ⟩ in real-time from magnetic diagnostic data (reconstruct equilibrium + perturbed field)
- Test: Does ⟨Z_ψ⟩ spike before mode locking or disruption?
- Application: Add ⟨Z_ψ⟩ to disruption prediction suite (APEX code at DIII-D)

**Timeline:** 2-3 years (requires collaboration with tokamak group, proposal process, beam time)

---

## Phase 7: Applications and Extensions

### Application 1: Stellarator Optimization

**Current paradigm:**
- Optimize magnetic configuration for quasi-symmetry (minimizes drift-driven transport)
- Computationally expensive: full orbit following for many particles over coil-parameter space

**Z_ψ-based optimization:**
- Objective function: Minimize ⟨Z_ψ⟩_ensemble over coil currents
- Advantage: Single scalar, computed once per configuration
- Gradient-based optimization feasible (∂⟨Z_ψ⟩/∂I_coil)

**Prototype study:**
- Use W7-X configuration space (7 coil types, few-parameter family)
- Compute ⟨Z_ψ⟩ for grid of parameters
- Find minimum
- Compare to quasi-symmetry metric
- Deliverable: New optimization criterion complementing existing methods

### Application 2: ITER Disruption Prediction

**Context:**
- Disruptions (sudden loss of confinement) are major risk for ITER
- Need real-time predictors with ~100 ms warning time

**Z_ψ as precursor:**
- Hypothesis: Magnetic islands and tearing modes cause resonance overlap → Z_ψ secular growth → disruption
- Implementation: Add ⟨Z_ψ⟩ computation to real-time MHD equilibrium reconstruction
- Decision threshold: If ⟨Z_ψ⟩ > Z_crit, trigger mitigation (massive gas injection)

**Feasibility:**
- Real-time equilibrium reconstruction: standard at major tokamaks (~1 ms update)
- Z_ψ computation: lightweight, add ~10% overhead
- Integration with ITER disruption mitigation system (DMS)

**Proposal:** Phase I study (simulations), Phase II (test at DIII-D or EAST), Phase III (deploy at ITER)

### Application 3: Energetic Particle Confinement

**Relevance:**
- Fusion-born alpha particles (3.5 MeV) must remain confined to heat plasma
- Ripple losses of alphas reduce fusion gain Q
- ITER design: ε_ripple < 0.08% at edge to limit alpha losses to <5%

**Z_ψ for alpha optimization:**
- Compute ⟨Z_ψ⟩ for alpha particle distribution
- Map loss boundaries in (energy, pitch, radius) space
- Iterate: Adjust coil positions, shaping, to minimize ⟨Z_ψ⟩
- Feed into ITER design refinements or future reactor studies

---

## Documentation and Dissemination

### Papers

**Paper 1: Theory and Single-Particle Validation**
- *Journal:* Physics of Plasmas or Journal of Plasma Physics
- *Length:* 12-15 pages
- *Content:* Guiding-center Theorems 1-2, ripple resonance numerical tests, comparison to traditional loss-boundary methods
- *Timeline:* 8-10 months from project start

**Paper 2: Ensemble Transport and Kinetic Connection**
- *Journal:* Nuclear Fusion or Plasma Physics and Controlled Fusion
- *Length:* 10-12 pages
- *Content:* Aggregation theory, ORBIT/ASCOT simulations, connection to D_⊥, stellarator optimization case study
- *Timeline:* 12-15 months

**Paper 3: Experimental Validation (if successful)**
- *Journal:* Physical Review Letters (if compelling) or Nuclear Fusion
- *Length:* 5-6 pages (PRL) or 10 pages (NF)
- *Content:* DIII-D or W7-X data, loss-rate correlation, disruption precursor demonstration
- *Timeline:* 24-36 months

### Conferences

**Key venues:**
1. **APS Division of Plasma Physics (DPP)** - annual, October
2. **IAEA Fusion Energy Conference** - biennial, major international forum
3. **Sherwood Fusion Theory Conference** - annual, theory focus
4. **European Physical Society Conference on Plasma Physics** - biennial

**Presentation plan:**
- Year 1: DPP talk on theory and single-particle results
- Year 2: Sherwood talk on kinetic aggregation, IAEA poster on stellarator optimization
- Year 3: IAEA talk on experimental validation (if data available)

### Collaborations

**Target groups:**
1. **DIII-D Theory/Fast-Ion Group** (General Atomics)
   - Contact: Max Austin, Bill Heidbrink (UCI collaborator on fast ions)
   
2. **W7-X Theory Group** (IPP Greifswald)
   - Contact: Per Helander, Yuriy Turkin
   
3. **ITER Organization, Plasma Theory**
   - Contact: Alberto Loarte (disruptions), Sergei Putvinski (alpha transport)

4. **University groups:**
   - MIT Plasma Science & Fusion Center (diagnostics expertise)
   - U. Wisconsin (stellarator theory)

---

## Success Metrics

### Technical Achievements
- [ ] Virial-like identity derived for tokamak ψ̈
- [ ] Theorems 1-2 proven for guiding-center dynamics
- [ ] Code implemented in ORBIT or ASCOT
- [ ] Ripple resonance boundary mapped, matches traditional methods
- [ ] Ensemble ⟨Z_ψ⟩ correlated with transport coefficient D_⊥
- [ ] Stellarator optimization prototype completed

### Publications and Impact
- [ ] ≥2 papers in plasma physics journals (Phys. Plasmas, Nucl. Fusion)
- [ ] ≥20 citations within 2 years
- [ ] Invited talk at DPP or Sherwood
- [ ] Collaboration established with ≥1 major facility

### Long-Term Vision
- [ ] Z_ψ included in ITER disruption prediction algorithm
- [ ] Method adopted for stellarator design optimization
- [ ] Extension to gyrokinetic simulations (GENE, GS2 codes)

---

## Timeline and Resources

| Phase | Duration | Key Deliverables |
|-------|----------|------------------|
| Phase 1: Q selection | 3 weeks | Optimal Q for tokamak/stellarator |
| Phase 2: Theory | 2 months | Theorems proven, technical note |
| Phase 3: Implementation | 2 months | ORBIT/custom code with Z_ψ |
| Phase 4: Simulations | 4 months | Single-particle, ensemble, MHD tests |
| Phase 5: Aggregation | 2 months | Kinetic connection established |
| Phase 6: Experiments | 12+ months | Proposal, beam time, analysis |
| Phase 7: Applications | Ongoing | Optimization, disruption prediction |

**Total to first paper:** ~9-12 months  
**Total to experimental paper:** ~24-36 months

**Resources:**
- HPC: 5000-10,000 CPU-hours for orbit simulations
- Software: ORBIT (free for research), ASCOT (open source)
- Collaborations: Access to equilibrium data (free for publications)
- Travel: ~$6K for conferences
- Personnel: 40% FTE for 12 months (theory + simulations), 20% FTE year 2-3 (experiments)

**Total estimated cost:** $60K-90K (lower than accelerator project due to lighter experimental requirements)

---

## Risk Mitigation

**Risk 1:** Virial-like identity doesn't exist for ψ  
*Mitigation:* Z_ψ still valid without it; proceed with empirical validation

**Risk 2:** Collisional effects dominate, Nekhoroshev regime too short  
*Mitigation:* Focus on energetic/fast-ion population (longer τ_collision)

**Risk 3:** 3D stellarator fields too complex for clear signal  
*Mitigation:* Start with simpler 2D tokamak + ripple, extend later

**Risk 4:** Experimental access difficult  
*Mitigation:* Focus on theory + simulation papers; experiments as stretch goal

---

## Proactive Next Steps

Most likely user responses:

1. **(50%)** Request more detail on guiding-center implementation or specific equilibrium models  
   *Prepared:* I can provide full derivation of guiding-center equations, specific Python class structure, or pointers to EFIT equilibrium files

2. **(30%)** Ask about connection to existing plasma transport theory  
   *Prepared:* I can elaborate on links to quasi-linear theory, neoclassical transport, gyrokinetics

3. **(20%)** Want to know about computational cost relative to full gyrokinetic codes  
   *Prepared:* Z_ψ in guiding-center is ~10^6× faster than gyrokinetic PIC; can provide detailed comparison table
