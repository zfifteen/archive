# Document 4: Molecular Dynamics and Cross-Domain Theory

**Author:** Dionisio Alberto Lopez III  
**Date:** January 30, 2026  
**Purpose:** Instructions for applying the Z_Q flux diagnostic to molecular systems and developing cross-domain theoretical foundations

---

## Objective

**Part A:** Validate the flux diagnostic in molecular dynamics contexts (conformational transitions, cluster dissociation, barrier crossing)

**Part B:** Develop systematic theoretical foundations applicable across all domains (virial classes, optimization theory, infinite-dimensional extensions)

---

# PART A: MOLECULAR DYNAMICS APPLICATIONS

## Strategic Context

**Why molecular systems matter:**
- Smallest-scale test case: 2-50 atoms (water dimer, peptides, clusters)
- Rich Nekhoroshev phenomena in metastable states (exponentially long pre-dissociation)
- Connection to chemistry: transition state theory, RRKM theory
- Complementary to statistical mechanics: microcanonical ensemble dynamics
- Practical applications: protein folding kinetics, chemical reaction dynamics

**Advantages for validation:**
- Full control over Hamiltonian (analytical potentials)
- Exact numerics possible (no approximations like guiding-center)
- Short timescales (fs-ns) → rapid simulation
- Rich literature on chaos indicators in molecular systems

**Challenges:**
- High dimensionality (3N-6 degrees of freedom for N atoms)
- Multiple timescales: vibrations (fs) vs. rotations (ps) vs. reactions (ns-μs)
- Anharmonic potentials complicate analytic theory
- Dissociation not always well-defined (continuous vs. discrete)

---

## Phase 1: System Selection and Q Definition

### Candidate Molecular Systems

**System 1: Water Dimer (Simplest Hydrogen Bond)**

**Structure:**
- 2 H₂O molecules: 6 atoms total
- Hydrogen bond between O-H···O
- 12 degrees of freedom (18 coordinates - 6 rigid-body)

**Hamiltonian:**
```
H = T_internal + T_cm + V_HB(r_OO, angles) + V_intra(H₂O geometries)
```

Where:
- T_internal: Kinetic energy of vibrations/rotations within each molecule
- T_cm: Center-of-mass kinetic energy
- V_HB: Hydrogen bond potential (Lennard-Jones + electrostatic)
- V_intra: Intramolecular potential (flexible vs. rigid water model)

**Near-integrable form:**
```
H = H₀(vibrations) + ε·H₁(intermolecular coupling)
```

With ε ~ E_HB / E_vib ~ 5 kcal/mol / 100 kcal/mol ~ 0.05

**Confinement functional Q:**

*Option 1: Intermolecular distance*
```
Q = r_OO = |r_O1 - r_O2|
```

- Level sets: Spherical shells separating bound (r < r_critical ~ 3.5 Å) from dissociated (r > r_critical)
- Physical interpretation: Direct measure of hydrogen bond integrity

*Option 2: Moment of inertia about center of mass*
```
Q = I_total = Σ m_i |r_i - R_cm|²
```

- Increases when molecules separate
- Smooth, always well-defined
- Analogous to beam emittance

*Option 3: Hydrogen bond coordinate (collective)*
```
Q = r_OH···O - equilibrium value
```

- Most chemically relevant
- Requires defining which H is bonded (ambiguous if flipping)

**Selection:** Use Q = r_OO (Option 1) for simplicity; validate with Q = I_total (Option 2)

**Flux diagnostic:**
```
Z_r = r_OO · ṙ_OO / E_total
```

**Expected behavior:**
- Below dissociation energy (E < 5 kcal/mol): ⟨Z_r⟩ ≈ 0 (molecules vibrate, stay bound)
- Near dissociation threshold: ⟨Z_r⟩ shows secular growth episodes (attempted escape)
- Above threshold: Sustained ⟨Z_r⟩ > 0 leading to dissociation

---

**System 2: Small Peptide (Alanine Dipeptide)**

**Structure:**
- 22 atoms: H₃C-CO-NH-CH(CH₃)-CO-NH-CH₃
- Prototype for protein folding studies
- Key coordinates: φ, ψ dihedral angles (Ramachandran plot)

**Hamiltonian:**
- Standard molecular mechanics force field (AMBER, CHARMM)
- Multiple minima separated by barriers (~5 kcal/mol)

**Confinement functional Q:**

*Reaction coordinate for φ-ψ transition:*
```
Q = cos(φ - φ₀) + cos(ψ - ψ₀)
```

Where (φ₀, ψ₀) defines reference conformation (e.g., α-helix)

- Level sets: Separate metastable wells (α-helix, β-sheet, extended)
- Barrier crossing = change in Q

**Flux diagnostic:**
```
Z_Q = Q · Q̇ / E_total
```

**Expected behavior:**
- Within metastable well: ⟨Z_Q⟩ ≈ 0 (confined to conformation)
- Approaching barrier: ⟨Z_Q⟩ shows pre-transition fluctuations
- Barrier crossing: Large Z_Q spike, then negative (settling into new well)

**Application:** Predict conformational transition times; compare to transition state theory

---

**System 3: Rare Gas Cluster (Ar₁₃)**

**Structure:**
- 13 argon atoms
- Lennard-Jones potential: V = 4ε[(σ/r)^12 - (σ/r)^6]
- Icosahedral equilibrium structure
- Well-studied for chaos and thermodynamics

**Hamiltonian:**
```
H = Σ (p_i²/2m) + Σ_{i<j} V_LJ(|r_i - r_j|)
```

**Confinement functional Q:**

*Cluster moment of inertia (expansion measure):*
```
Q = Σ m |r_i - R_cm|² = Tr(I_inertia)
```

- Small Q: Compact cluster
- Large Q: Expanding/dissociating cluster

**Flux diagnostic:**
```
Z_I = I · İ / E_total
```

**Expected behavior:**
- E < E_dissociation: ⟨Z_I⟩ ≈ 0 (solid-like or liquid-like confined cluster)
- E ~ E_dissociation: ⟨Z_I⟩ shows secular growth
- E > E_dissociation: One atom evaporates, Q jumps, then ⟨Z_I⟩ ≈ 0 for remaining Ar₁₂

**Application:** 
- Predict evaporation time vs. energy (compare to RRKM theory)
- Identify "magic" sizes (Ar₁₃ more stable than Ar₁₂)

---

## Phase 2: Theoretical Development for Molecular Systems

### Virial-Like Identities

**Standard virial theorem for molecular system:**

For N particles with pairwise potential V = Σ V(r_ij):
```
2⟨T⟩ = ⟨Σ r_i · ∇_i V⟩
```

**Generalized to Q̈:**

For Q = Σ m_i r_i²:
```
Q̈ = 2 Σ (p_i²/m_i) - Σ r_i · ∇_i V
  = 4T - Σ r_i · ∇_i V
```

For homogeneous potential V(λr) = λ^n V(r):
```
Σ r_i · ∇_i V = n V  (Euler's theorem)
```

**Result:**
```
Q̈ = 4T - n V = 4T - n(E - T) = (4+n)T - nE
```

**For Lennard-Jones potential:**
- Repulsive term: r^(-12) → contributes n=12
- Attractive term: r^(-6) → contributes n=6
- Mixture, so no simple virial form

**For Coulomb potential (ionized molecules):**
- V ~ 1/r → n = -1
- Q̈ = 3T + E (exact virial-like identity!)

**Implications:**
- Pure Coulomb: Strong virial identity → Z_Q should work excellently
- Lennard-Jones: Approximate virial-like behavior → Z_Q still useful but less clean
- Anharmonic potentials: Empirical validation needed

### Semiclassical and Quantum Extensions

**Nekhoroshev bounds for molecular vibrations:**

For molecule near equilibrium with anharmonic corrections:
```
H = Σ ω_i (n_i + 1/2) + ε·H_anharmonic(n, φ)
```

Where n_i are vibrational quantum numbers, φ_i phases.

**Quantum Nekhoroshev time:**
```
T_Nekh ~ (ℏ/ε) · exp[(ε₀/ε)^(1/(2N))]
```

**Correspondence principle:**
- Classical Z_Q diagnostic → Quantum expectation ⟨Q̂⟩·⟨Q̂̇⟩ / ⟨Ĥ⟩
- For highly excited states (large quantum numbers): Classical and quantum agree
- For low quantum numbers: Tunneling complicates (no classical analog)

**Strategy:**
- Focus on classical regime: E >> ℏω (many quanta excited)
- Future extension: Quantum Z_Q via Wigner function dynamics

---

## Phase 3: Numerical Implementation

### Molecular Dynamics Codes

**Option 1: LAMMPS (Large-scale Atomic/Molecular Massively Parallel Simulator)**
- Open source, widely used
- Supports custom compute commands (ideal for Z_Q)
- Many force fields available

**Option 2: GROMACS (Groningen Machine for Chemical Simulations)**
- Optimized for biomolecules
- Less flexible for custom diagnostics than LAMMPS
- Better for peptide simulations

**Option 3: Custom Python/Julia integrator**
- Full control
- Good for small systems (N < 50 atoms)
- Easy to implement Z_Q

**Recommendation:** LAMMPS for production, custom code for prototyping

### Implementation in LAMMPS

**Add custom compute for Z_Q:**

```cpp
// File: compute_zdiagnostic.cpp
#include "compute_zdiagnostic.h"
#include "atom.h"
#include "update.h"
#include "domain.h"

ComputeZdiagnostic::ComputeZdiagnostic(LAMMPS *lmp, int narg, char **arg) :
  Compute(lmp, narg, arg) {
  scalar_flag = 1;  // Output is a scalar
  q_prev = 0.0;
  time_prev = 0.0;
}

double ComputeZdiagnostic::compute_scalar() {
  // Compute Q (moment of inertia or other choice)
  double xcm[3];
  group->xcm(igroup, masstotal, xcm);
  
  double q_current = 0.0;
  double **x = atom->x;
  double *mass = atom->mass;
  int *mask = atom->mask;
  int *type = atom->type;
  int nlocal = atom->nlocal;
  
  for (int i = 0; i < nlocal; i++) {
    if (mask[i] & groupbit) {
      double dx = x[i][0] - xcm[0];
      double dy = x[i][1] - xcm[1];
      double dz = x[i][2] - xcm[2];
      q_current += mass[type[i]] * (dx*dx + dy*dy + dz*dz);
    }
  }
  
  // MPI reduce if parallel
  MPI_Allreduce(&q_current, &q_current, 1, MPI_DOUBLE, MPI_SUM, world);
  
  // Compute Q̇ via finite difference
  double dt = update->dt;
  double q_dot = (q_current - q_prev) / (update->ntimestep - time_prev) / dt;
  
  // Compute energy
  double energy = compute_ke() + compute_pe();
  
  // Z diagnostic
  double z_diag = q_current * q_dot / energy;
  
  // Store for next step
  q_prev = q_current;
  time_prev = update->ntimestep;
  
  return z_diag;
}
```

**LAMMPS input script:**

```lammps
# Water dimer simulation with Z diagnostic

units real
atom_style full
bond_style harmonic
angle_style harmonic

# Read structure
read_data water_dimer.data

# Force field (e.g., TIP3P water model)
pair_style lj/cut/coul/long 10.0
pair_coeff * * 0.1521 3.1507  # O-O parameters
kspace_style pppm 1.0e-4

# Thermostat (or NVE for microcanonical)
fix 1 all nve
# fix 1 all nvt temp 300 300 100.0

# Custom compute for Z diagnostic
compute zdiag all zdiagnostic

# Output
thermo 100
thermo_style custom step temp etotal ke pe c_zdiag

# Trajectory
dump 1 all custom 1000 traj.lammpstrj id type x y z vx vy vz

# Run
timestep 0.5  # 0.5 fs
run 1000000   # 500 ps
```

**Python post-processing:**

```python
import numpy as np
import matplotlib.pyplot as plt

# Load LAMMPS output
data = np.loadtxt('log.lammps', skiprows=2)
time = data[:, 0] * 0.5e-3  # Convert to ps
energy = data[:, 2]
z_diag = data[:, 5]

# Time-averaged Z diagnostic
window_size = 1000
z_avg = np.convolve(z_diag, np.ones(window_size)/window_size, mode='valid')
time_avg = time[window_size-1:]

# Plot
plt.figure(figsize=(10, 6))
plt.subplot(2, 1, 1)
plt.plot(time, z_diag, alpha=0.3, label='Instantaneous')
plt.plot(time_avg, z_avg, 'r-', linewidth=2, label='Moving average (1 ps)')
plt.axhline(0, color='k', linestyle='--', alpha=0.5)
plt.ylabel('Z diagnostic')
plt.legend()
plt.grid(True)

plt.subplot(2, 1, 2)
plt.plot(time, energy)
plt.ylabel('Energy (kcal/mol)')
plt.xlabel('Time (ps)')
plt.grid(True)

plt.tight_layout()
plt.savefig('z_diagnostic_timeseries.png', dpi=300)
```

---

## Phase 4: Numerical Experiments

### Experiment 1: Water Dimer Dissociation

**Protocol:**
1. Equilibrate at 300 K for 100 ps
2. Add kinetic energy to reach target total energy
3. Switch to microcanonical (NVE) ensemble
4. Track for 1-10 ns or until dissociation
5. Repeat for range of energies: E = 3-7 kcal/mol

**Observables:**
- r_OO(t): Intermolecular distance
- Z_r(t): Flux diagnostic
- τ_diss: Time to dissociation (r_OO > 5 Å)

**Analysis:**
- Below threshold (E < 5 kcal/mol):
  - Expect: ⟨Z_r⟩ ≈ 0, no dissociation in 10 ns
  - Nekhoroshev regime confirmed if Z_r fluctuates around zero
  
- Near threshold (E ≈ 5 kcal/mol):
  - Expect: ⟨Z_r⟩ shows intermittent secular growth
  - Metastability: Long times before dissociation
  - Measure: Distribution of τ_diss over many trajectories
  
- Above threshold (E > 5.5 kcal/mol):
  - Expect: Sustained ⟨Z_r⟩ > 0, rapid dissociation
  - Measure: ⟨Z_r⟩ vs. τ_diss correlation

**Comparison to RRKM theory:**

RRKM predicts dissociation rate:
```
k_RRKM = (ω‡/2π) · (N‡/N) · exp(-E_barrier/kT)
```

Where N‡ is density of states at transition state, N at reactant.

**Test:** Does ⟨Z_r⟩ predict k_RRKM? Specifically:
```
⟨Z_r⟩ ∝ k_RRKM ?
```

### Experiment 2: Alanine Dipeptide Conformational Transition

**Protocol:**
1. Equilibrate in α-helix conformation (φ ≈ -60°, ψ ≈ -40°)
2. Run NVE at fixed energy E (or NVT at 300-500 K)
3. Monitor φ, ψ dihedrals and Z_Q
4. Detect transitions: α → extended → β-sheet

**Observables:**
- φ(t), ψ(t): Ramachandran trajectory
- Z_Q(t): Flux diagnostic for reaction coordinate
- Transition events: Count and timing

**Analysis:**
- Within metastable well:
  - ⟨Z_Q⟩ ≈ 0 (confined)
  - φ, ψ fluctuate around minimum
  
- Pre-transition behavior:
  - Hypothesis: ⟨Z_Q⟩ shows secular growth 10-50 ps before transition
  - Test: Compute ⟨Z_Q⟩ in sliding 20 ps window before each transition
  - Compare to control periods (no transition in next 100 ps)
  
- Transition timing prediction:
  - If ⟨Z_Q⟩ exceeds threshold Z_crit, predict transition within τ_pred
  - Measure false positive and false negative rates

**Potential application:** Real-time rare event detection in MD simulations (adaptive sampling)

### Experiment 3: Ar₁₃ Cluster Evaporation

**Protocol:**
1. Initialize in icosahedral ground state (lowest energy geometry)
2. Heat to target energy E
3. Run NVE dynamics
4. Monitor cluster size (count atoms within cutoff distance)
5. Detect evaporation events

**Energy scan:**
- E_low = -40 ε (solid-like, no evaporation in 100 ns)
- E_mid = -35 ε (occasional evaporation, long waiting times)
- E_high = -30 ε (rapid evaporation, τ ~ 1 ns)

**Observables:**
- I(t): Moment of inertia
- Z_I(t): Flux diagnostic
- N(t): Number of atoms in cluster (step function when evaporation occurs)

**Analysis:**
- Nekhoroshev pre-evaporation regime:
  - ⟨Z_I⟩ ≈ 0 while cluster stable
  - Spike in Z_I before evaporation event
  
- Evaporation rate vs. energy:
  - k_evap(E) = -d⟨N⟩/dt
  - Compare: Arrhenius form k ~ exp(-E_barrier/kT) vs. ⟨Z_I⟩(E)
  
- Magic number effect:
  - Ar₁₃ (icosahedral) should have lower ⟨Z_I⟩ than Ar₁₂ at same E
  - Test: Is Z_I diagnostic sensitive to structural stability?

**Comparison to literature:**
- Weerasinghe & Amar (1993): RRKM calculations for Ar_n clusters
- Wales (2003): Energy landscapes and transition states
- Validate: Does Z_I approach capture same physics?

---

## Phase 5: Integration with Existing Methods

### Comparison to Transition State Theory (TST)

**TST rate formula:**
```
k_TST = (kT/h) · exp(-ΔG‡/kT)
```

Where ΔG‡ is free energy barrier.

**Z_Q connection:**
- TST assumes instantaneous barrier crossing
- Z_Q provides dynamical information about approach to barrier
- Hypothesis: Large Z_Q fluctuations = frequent barrier crossing attempts

**Joint analysis:**
- Compute both k_TST (from free energy profile) and ⟨Z_Q⟩
- Test: Is ⟨Z_Q⟩ ~ k_TST · ΔQ²? (ΔQ = barrier height in Q coordinate)

### Comparison to Lyapunov Exponents

**Molecular chaos indicators:**
- Lyapunov exponents λ_max: Standard chaos measure
- Available in many MD codes or via variational trajectory

**Protocol:**
1. For each trajectory, compute both λ_max and ⟨Z_Q⟩
2. Scatter plot: λ_max vs. ⟨Z_Q⟩
3. Test hypothesis: High ⟨Z_Q⟩ correlates with high λ_max (diffusive regime)

**Expected outcome:**
- Nekhoroshev regime: λ_max > 0 (chaotic), but ⟨Z_Q⟩ ≈ 0 (confined)
- Diffusive regime: λ_max large AND ⟨Z_Q⟩ > 0 (escaping)
- Z_Q provides complementary info: Local chaos (λ) vs. global leakage (Z)

---

# PART B: CROSS-DOMAIN THEORETICAL FOUNDATIONS

## Systematic Virial-Like Identity Search

### Inventory of Known Classes

**Class 1: Homogeneous potentials**

Definition: V(λr) = λ^n V(r)

Examples:
- Harmonic oscillator: n = 2
- Coulomb/gravity: n = -1
- Lennard-Jones repulsive: n = -12

**Virial identity:**
```
⟨Σ r_i · ∇_i V⟩ = n⟨V⟩  (Euler's theorem)
```

**Z_Q form:**
```
Z_Q = Q · Q̇ / E
```

With Q̈ = (4+n)T - nE (for Q = Σ m r²)

**Nekhoroshev interpretation:**
- n=2 (harmonic): Integrable, Z_Q exactly zero
- n≠2: Near-integrable when ε = |V_pert/V_total| << 1
- Z_Q sensitivity proportional to departure from integrability

---

**Class 2: Logarithmic potentials**

V = -V₀ ln(r/r₀)

Examples:
- 2D vortex dynamics
- Certain condensed matter systems

**Virial identity:**
- No simple r^n homogeneity
- But: Σ r_i · ∇_i V = -V₀ · (number of particles)
- Still linear in V!

**Z_Q form:**
```
Q̈ = 4T + (N·V₀)
```

Similar structure to Coulomb case.

---

**Class 3: Confining potentials (traps)**

V = V_harmonic(r) + V_anharmonic(r)

Examples:
- Optical lattices (atomic physics)
- Penning traps (charged particles)
- Magnetic bottles

**Strategy:**
- Treat anharmonic part as perturbation
- Harmonic part gives exact virial: Q̈ = 6T - 2V_harmonic
- Perturbation adds: -Σ r_i · ∇_i V_anharm
- Z_Q diagnostic detects when anharmonic terms drive diffusion

---

**Class 4: Mixed potentials (no global homogeneity)**

Example: Molecular force fields (CHARMM, AMBER)
- Bonds: Harmonic (n=2)
- Angles: Harmonic or periodic
- Dihedrals: Periodic (cosine)
- Van der Waals: Lennard-Jones (mixed n=-12, n=-6)
- Coulomb: n=-1

**Virial identity:**
- No exact global form
- But: Each term contributes separately
- Total: Q̈ = Σ contributions

**Z_Q diagnostic:**
- Still well-defined
- Less clean theoretical interpretation
- Empirical validation essential

---

### Optimization of Weighting Function f(Q)

**Sensitivity functional:**

Goal: Maximize detectability of diffusion onset

**Define sensitivity:**
```
S[f] = |∂⟨Z_Q⟩/∂D| / σ_noise
```

Where:
- D: Diffusion coefficient (unknown, to be detected)
- σ_noise: Standard deviation of Z_Q fluctuations in Nekhoroshev regime

**Variational problem:**
```
max_{f>0} S[f]
```

Subject to:
- f(Q) > 0 (flux is signed, but weighting positive)
- f(0) finite (well-behaved at origin)
- Optional: ∫ f(Q) dQ < ∞ (normalization)

### Analytical Approach

**Assume:**
- Q follows diffusive evolution: dQ/dt = D(Q) + noise when diffusing
- Nekhoroshev: dQ/dt = 0 + noise (bounded fluctuations)

**Z_Q in diffusive regime:**
```
⟨Z_Q⟩ = ⟨f(Q) · Q̇ · Q / E⟩
     ≈ (1/E) · ⟨f(Q) · Q · D(Q)⟩
     = (1/E) · ∫ f(Q) · Q · D(Q) · ρ(Q) dQ
```

Where ρ(Q) is probability distribution of Q.

**Optimization:**
```
∂⟨Z_Q⟩/∂D = (1/E) · ∫ f(Q) · Q · (∂D/∂D=1) · ρ(Q) dQ
          = (1/E) · ∫ f(Q) · Q · ρ(Q) dQ
```

To maximize: Choose f(Q) concentrated where signal (Q·ρ(Q)) is large.

**Optimal choice (heuristic):**
```
f(Q) ∝ Q · ρ(Q)
```

If ρ is Gaussian centered at Q₀: f(Q) ∝ (Q - Q₀) for Q > Q₀ (outer region)

**Practical parametrization:**
```
f(Q) = Q^p  with p ∈ [0, 2]
```

Scan p numerically in simulations.

### Numerical Optimization Protocol

1. **Generate ensemble of trajectories:** Both Nekhoroshev (ε small) and diffusive (ε large)

2. **For each p ∈ {0, 0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 1.75, 2.0}:**
   - Compute Z_Q^(p) = Q^p · Q̇ / E
   - Measure ⟨Z_Q^(p)⟩_Nekh and σ_Nekh
   - Measure ⟨Z_Q^(p)⟩_diffusive
   - Compute signal-to-noise: SNR(p) = |⟨Z⟩_diff - ⟨Z⟩_Nekh| / σ_Nekh

3. **Select p_opt:** argmax SNR(p)

4. **Validate:** Test p_opt on independent data set

**Expected results:**
- Most systems: p_opt ≈ 1 (linear f(Q) = Q)
- Systems with heavy tails: p_opt < 1 (down-weight rare large Q)
- Systems with localized diffusion: p_opt > 1 (up-weight where diffusion occurs)

---

## Infinite-Dimensional Extensions

### Hamiltonian PDEs

**Prototypical example: Nonlinear Schrödinger (NLS)**

```
iψ_t = -Δψ + |ψ|^(2σ) ψ
```

Where σ = 1 (cubic NLS), σ = 2 (quintic), etc.

**Hamiltonian structure:**
```
H[ψ] = ∫ (|∇ψ|² + (1/(σ+1))|ψ|^(2σ+2)) dx
```

With symplectic form Ω = ∫ δψ ∧ δψ* dx.

**Near-integrability:**
- 1D cubic NLS: Exactly integrable (inverse scattering)
- Perturbed NLS: H = H_integrable + ε·H_pert (e.g., higher-order dispersion)

**Confinement functional Q:**

*Option 1: L² norm (conserved in integrable case)*
```
Q = ∫ |ψ|² dx = N (particle number)
```

But this is exactly conserved, so Q̇ = 0 always. Not useful for Z_Q.

*Option 2: Second moment (analogous to molecular I)*
```
Q = ∫ x² |ψ(x,t)|² dx
```

**Flux diagnostic:**
```
Z_Q = Q · Q̇ / H
```

**Q̈ identity:**
Compute:
```
Q̇ = ∫ x² ∂_t |ψ|² dx
  = ∫ x² (ψ*ψ_t + ψψ_t*) dx
```

Using iψ_t = -Δψ + |ψ|^(2σ)ψ:
```
Q̇ = -2 Im ∫ x² ψ* Δψ dx
  = 2 Im ∫ x² (ψ* ψ_xx) dx  (integration by parts)
```

Further manipulation gives:
```
Q̈ = 4 ∫ |ψ_x|² dx - 4σ ∫ |ψ|^(2σ+2) dx
  = 4·(kinetic part of H) - 4σ·(potential part of H)
```

**Virial identity for NLS!**

For cubic NLS (σ=1):
```
Q̈ = 4T - 4V
```

Where T = ∫|∇ψ|², V = ∫|ψ|⁴.

**Nekhoroshev interpretation:**
- Integrable NLS: Solutions are solitons or multi-solitons (bounded Q)
- Perturbed NLS: Solitons slowly drift/radiate → ⟨Z_Q⟩ ~ diffusion coefficient

**Application:**
- NLS describes optical fibers, BECs (Bose-Einstein condensates), plasma waves
- Z_Q diagnostic: Detect onset of soliton instability or wave turbulence

---

**Other Hamiltonian PDEs:**

**Vlasov-Poisson (collisionless plasma):**
```
∂_t f + v·∇_x f + E·∇_v f = 0
E = -∇φ,  Δφ = ∫ f dv - n_background
```

**Moment equations:**

Define moments: ⟨x^k⟩ = ∫∫ x^k f(x,v,t) dx dv

**Second moment:**
```
Q = ∫∫ |x|² f dx dv
```

**Q̇ and Q̈:** Computable from Vlasov equation (lengthy but tractable)

**Z_Q for Vlasov:** Detect approach to violent relaxation or Landau damping breakdown

---

### Functional Optimization in Infinite Dimensions

**Generalized problem:**

For Hamiltonian PDE, find optimal functional Q[ψ] such that Z_Q has maximum sensitivity to diffusion.

**Calculus of variations:**
```
max_{Q[ψ]} SNR[Z_Q]
```

Subject to constraints (e.g., Q must be positive, conserve under integrable evolution).

**Euler-Lagrange equation:** (δSNR/δQ) = 0

**Challenges:**
- Infinite-dimensional → Requires functional derivatives
- No general solution (system-dependent)

**Practical approach:**
- Parametrize Q within family: Q[ψ] = ∫ g(x) |ψ(x)|² dx
- Optimize over g(x) numerically
- Use machine learning? (Gradient descent in function space)

---

## Z_Q as Complement to Local Chaos Indicators

### Taxonomy of Dynamical Indicators

**Local indicators (probe trajectory stability):**
1. **Lyapunov exponents:** λ = lim_{t→∞} (1/t) ln||δz(t)||
   - Measures sensitivity to initial conditions
   - Positive λ: Chaotic
   - Requires variational equations
   
2. **MEGNO (Mean Exponential Growth of Nearby Orbits):**
   - Refinement of Lyapunov
   - Y = (2/t) ∫₀^t (s/||δz||) (d||δz||/ds) ds
   - Y → 2 (regular), Y → ∞ (chaotic)
   
3. **FMA (Frequency Map Analysis):**
   - FFT of trajectory → fundamental frequencies
   - Diffusion in frequency space = chaos
   - No variational equations needed
   
**Global indicators (probe phase-space structure):**

4. **Z_Q flux diagnostic:**
   - Measures leakage flux across confinement boundary
   - Global: Averaged over trajectory, sensitive to large-scale diffusion
   - Targets Nekhoroshev → Arnold diffusion transition

**Complementarity:**
- Lyapunov/MEGNO: Answer "Is this trajectory chaotic?" (binary, local)
- Z_Q: Answer "Is this trajectory escaping?" (continuous, global)

**Key distinction:**
- Chaos ≠ escape
- Example: Fully chaotic trajectory can remain confined (stable chaos)
- Example: Weakly chaotic trajectory can slowly diffuse and escape (Arnold diffusion)

**Optimal strategy: Use both**
- Lyapunov identifies chaotic regions
- Z_Q identifies escaping regions
- Intersection: Chaotic AND escaping (dangerous zone)

---

## Documentation and Cross-Domain Synthesis

### Unifying Paper: "Flux-Based Diagnostics Across Hamiltonian Systems"

**Target journal:** Journal of Statistical Physics or Communications in Nonlinear Science

**Length:** 20-25 pages

**Structure:**

1. **Introduction (3 pages)**
   - Nekhoroshev theorem and Arnold diffusion (brief review)
   - Limitations of current chaos indicators
   - Vision: Universal flux diagnostic

2. **Theory (6 pages)**
   - Generalized Z_Q formulation
   - Theorems 1-2 (sketch, refer to appendices for proofs)
   - Virial-like identities (systematic catalog)
   - Optimization of f(Q)

3. **Applications Gallery (8 pages)**
   - Accelerator beam dynamics (2 pages: LHC results)
   - Plasma guiding-center (2 pages: ripple resonance)
   - Molecular dynamics (2 pages: water dimer, peptide, cluster)
   - Hamiltonian PDE (1 page: NLS soliton diffusion)
   - Comparison table (1 page): Computational cost, sensitivity

4. **Discussion (2 pages)**
   - Z_Q as sub-exponential complement to local indicators
   - Connection to transport theory
   - Future directions (quantum, stochastic)

5. **Conclusions (1 page)**

**Appendices:**
- Appendix A: Full proofs of Theorems 1-2 for each domain
- Appendix B: Implementation details (code snippets)
- Appendix C: Supplementary numerical data

**Timeline:** 18 months from project start

---

## Success Metrics

### Part A: Molecular Dynamics
- [ ] Water dimer: ⟨Z_r⟩ predicts dissociation time within factor of 2
- [ ] Peptide: ⟨Z_Q⟩ shows pre-transition signal 10-50 ps before barrier crossing
- [ ] Cluster: Z_I evaporation rate correlation coefficient |r| > 0.7
- [ ] Paper published in J. Chem. Phys. or similar

### Part B: Cross-Domain Theory
- [ ] Virial-like identity catalog for 5+ system classes
- [ ] Optimal weighting f(Q) determined for each test system
- [ ] NLS Z_Q diagnostic implemented and tested
- [ ] Unifying paper published in J. Stat. Phys. or Commun. Nonlinear Sci.
- [ ] ≥30 citations within 3 years (high-impact theoretical work)

---

## Timeline

| Phase | Duration | Deliverables |
|-------|----------|--------------|
| Phase 1: Molecular Q selection | 3 weeks | Q chosen for 3 test systems |
| Phase 2: Theory development | 2 months | Virial identities derived |
| Phase 3: LAMMPS implementation | 1 month | Custom compute working |
| Phase 4: Molecular simulations | 3 months | All 3 experiments completed |
| Phase 5: Integration | 1 month | TST, Lyapunov comparisons |
| Cross-domain theory | 3 months | Parallel to phases 3-5 |
| Paper writing | 2 months | Molecular paper + unifying paper |

**Total: 12 months to both papers**

---

## Resources

**Computational:**
- Molecular dynamics: 1000-5000 CPU-hours (smaller than accelerators/plasma)
- Personal workstation sufficient for small systems (water dimer, peptide)
- HPC for Ar₁₃ ensemble statistics

**Software:**
- LAMMPS: Free, open source
- GROMACS: Free, open source
- Python scientific stack (NumPy, SciPy, Matplotlib): Free

**Personnel:**
- Primary researcher: 40% FTE for 12 months
- Optional: Computational chemist collaborator (10% FTE advisory)

**Total estimated cost:** $50K-70K (lowest of three domains)

---

## Proactive Next Steps Prediction

Based on most likely responses:

1. **(40%)** Ask for more detail on LAMMPS implementation or specific force field choices  
   *Prepared:* I can provide complete LAMMPS input files, specific water models (SPC, TIP3P, TIP4P comparisons), or expanded C++ code

2. **(30%)** Request clarification on virial identity derivations  
   *Prepared:* I can show full step-by-step derivation of Q̈ for homogeneous potentials, NLS case, or custom Hamiltonian

3. **(20%)** Want to know about connecting all three documents (accelerator, plasma, molecular)  
   *Prepared:* I can draft unified grant proposal (NSF, DOE), create comparison table of three domains, or suggest collaborator network

4. **(10%)** Ask about extending to quantum systems  
   *Prepared:* I can outline semiclassical Z_Q via Wigner functions, or discuss quantum chaos indicators (level spacing statistics, Loschmidt echo)
