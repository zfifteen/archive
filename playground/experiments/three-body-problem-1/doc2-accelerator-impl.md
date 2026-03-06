# Document 2: Accelerator Beam Dynamics Implementation (Highest Priority)

**Author:** Dionisio Alberto Lopez III  
**Date:** January 30, 2026  
**Purpose:** Instructions for implementing and validating the generalized Z_Q flux diagnostic in particle accelerator beam dynamics

---

## Objective

Deploy the flux-based diagnostic in accelerator beam dynamics as the highest-priority validation domain, exploiting the field's existing familiarity with Nekhoroshev scaling, extreme computational demands, and immediate practical relevance.

---

## Phase 1: Confinement Functional Selection

### Beam Emittance as Confinement Proxy

**Primary choice - RMS emittance:**
```
ε_x = √(⟨x²⟩⟨p_x²⟩ - ⟨xp_x⟩²)
ε_y = √(⟨y²⟩⟨p_y²⟩ - ⟨yp_y⟩²)
```

**Rationale:**
- Level sets naturally separate core from halo particles
- Standard accelerator observable with clear physical interpretation
- Directly related to beam quality and collider luminosity
- Monitoring infrastructure already exists in facilities

**Alternative choices (evaluate trade-offs):**
- Second moments: σ²_x = ⟨x²⟩, σ²_px = ⟨p_x²⟩
- Higher moments for tail sensitivity: ⟨x⁴⟩^(1/4)
- Trace of covariance matrix: Tr(Σ)
- Determinant: det(Σ)

**Selection protocol:**
1. Test all candidates in numerical tracking
2. Measure sensitivity to halo formation
3. Evaluate computational cost
4. Choose based on signal-to-noise ratio

### Flux Diagnostic Definition

**For transverse plane (x, px):**
```
Z_σ = σ · σ̇ / E_beam
```

or with emittance:
```
Z_ε = ε · ε̇ / E_beam
```

**For full 6D phase space:**
```
Z_6D = (Σ ε_i · ε̇_i) / E_beam
```
where i ∈ {x, y, z} (or longitudinal coordinate)

**Normalization conventions:**
- E_beam: total beam energy
- Alternative: normalize by H_⊥ (transverse Hamiltonian) for decoupled systems
- Document choice and physical interpretation

---

## Phase 2: Theoretical Validation

### Nekhoroshev Estimates for Accelerator Models

**Establish exponential stability:**
- Review existing literature on Nekhoroshev bounds for symplectic maps
- Specific references: dynamic aperture studies at LHC (Giovannozzi et al.)
- Connection to DA scaling: r_DA ~ (ε₀/ε)^(1/(2n)) for n degrees of freedom

**Prove Theorem 1 for accelerator context:**

*Statement:* For a symplectic map M representing one turn in an accelerator lattice, with nonlinear perturbation strength ε (multipole errors, nonlinear elements), if the working point (Q_x, Q_y) satisfies resonance-avoidance conditions and the system meets Nekhoroshev steepness requirements, then:

```
|⟨Z_σ⟩_N| < C · exp(-κ/ε^α)
```

for number of turns N < N_Nekh ~ exp[(ε₀/ε)^β], where α, β depend on dimensionality.

*Proof steps:*
1. Map existing Nekhoroshev results for symplectic maps (Guzzo, Morbidelli, etc.)
2. Express σ or ε in terms of action variables
3. Use bounds on action drift: |Δℐ| < ε^a exp(-b/ε^c)
4. Propagate to σ̇ via chain rule
5. Time-average and collect exponential factors
6. Document explicit C, κ, α, β

**Prove Theorem 2 for diffusive halo formation:**

*Statement:* When resonance overlap occurs (Chirikov parameter K > 1) or dynamic aperture is approached, the flux diagnostic exhibits secular growth:

```
⟨Z_σ⟩ ~ D_eff · (∂σ/∂ℐ) / E_beam
```

where D_eff is the effective diffusion coefficient governing emittance growth and halo formation.

*Proof steps:*
1. Model resonance-driven diffusion: dℐ/dt = D_eff + noise
2. Relate emittance growth to action diffusion: ε̇ ~ (∂ε/∂ℐ)·D_eff
3. Show that ⟨Z_ε⟩ averages to secular term proportional to D_eff
4. Connect to beam loss rate and halo population growth
5. Validate functional form against known scaling laws

**Deliverable:** 10-15 page technical note with rigorous proofs adapted to accelerator terminology

---

## Phase 3: Numerical Implementation

### Integration with Standard Tracking Codes

**Primary targets:**
1. **MAD-X** (CERN standard lattice design tool)
   - Version: 5.09+ (2024 releases per GitHub)
   - Language: Fortran 90/95 with Python bindings
   - Module: TRACK (symplectic tracking)
   
2. **SixTrack** (LHC tracking workhorse)
   - High-precision 6D tracking
   - Optimized for long-term stability studies
   - Already used for dynamic aperture calculations

3. **Xsuite** (modern Python toolkit, 2024-2025)
   - Multiplatform beam dynamics framework
   - Replacing legacy tools at CERN
   - GPU acceleration capability

**Implementation requirements:**

For MAD-X:
```fortran
! Add to track module (track.f90 or equivalent)
SUBROUTINE compute_flux_diagnostic(n_particles, coords, energy, z_sigma)
  ! Input: particle coordinates (x, px, y, py, z, pz)
  ! Compute: σ = sqrt(⟨x²⟩)  (or full emittance)
  ! Compute: σ̇ via finite differences or saved history
  ! Output: Z_σ = σ·σ̇/E
END SUBROUTINE

! Call at each turn or at specified intervals
! Store time series for averaging
```

For SixTrack (similar structure):
```fortran
! Integrate into existing tracking loop
! Minimal overhead: compute second moments each turn
! Store Z diagnostic alongside existing aperture checks
```

For Xsuite (Python):
```python
class FluxDiagnostic:
    def __init__(self, particles, normalization='energy'):
        self.particles = particles
        self.sigma_history = []
        self.z_history = []
        
    def compute_sigma(self):
        x = self.particles.x
        return np.sqrt(np.mean(x**2))
        
    def compute_z_sigma(self, sigma_current, sigma_prev, dt, energy):
        sigma_dot = (sigma_current - sigma_prev) / dt
        return sigma_current * sigma_dot / energy
        
    def update(self, turn_number):
        # Compute at each turn, store time series
        # Provide methods for time-averaging
        pass
```

**Optimization strategies:**
- Compute only every N turns (N=10-100) for cost reduction
- Use incremental statistics formulas (avoid full particle loop each turn)
- Parallelize across particle ensemble if needed
- Cache previous values to enable finite-difference σ̇

**Validation tests:**
1. Verify Z_σ ≈ 0 for linear lattice (no perturbations)
2. Confirm secular growth when nonlinear errors introduced
3. Compare against existing halo diagnostics
4. Benchmark computational overhead: target <1% of total tracking time

---

## Phase 4: Numerical Experiments

### Test Case 1: 4D Hénon Map (Simplified Benchmark)

**Purpose:** Controlled environment with known Nekhoroshev scaling

**Setup:**
```
x_{n+1} = x_n cos(2πν) - (y_n - x_n²) sin(2πν)
y_{n+1} = x_n sin(2πν) + (y_n - x_n²) cos(2πν)
```
(Plus identical copy for second degree of freedom)

**Protocol:**
1. Vary perturbation strength ε (coefficient of x² term)
2. Track ensemble of 10^4 initial conditions
3. Compute Z_σ at each iteration
4. Measure ⟨Z_σ⟩ vs. ε and compare to Nekhoroshev prediction
5. Identify transition from exponentially small to secular growth

**Expected outcome:** Validate exponential scaling, establish baseline sensitivity

### Test Case 2: LHC Lattice at 6.5 TeV (Realistic Model)

**Purpose:** Direct validation against world's most studied accelerator

**Data sources:**
- LHC operational lattice files (MAD-X format, publicly available)
- Measured magnetic field errors (CERN Edms database)
- Published dynamic aperture measurements (Giovannozzi et al. 2019, arXiv:1907.10913)

**Simulation protocol:**
1. Load LHC lattice with realistic error table
2. Initialize particle distribution: Gaussian core + tail particles
3. Track for 10^5 to 10^7 turns (representing seconds to hours of beam time)
4. Compute Z_ε for horizontal and vertical planes separately
5. Monitor time evolution: ⟨Z_ε⟩_T for increasing averaging window T

**Comparison metrics:**
- Onset of emittance growth vs. published DA measurements
- Halo formation rate vs. beam loss monitor data
- Computational time vs. existing methods (FMA, Lyapunov)

**Archival data analysis:**
- LHC Run 2 (2015-2018) beam instrumentation data
- Correlate measured beam losses with predicted Z_ε trends
- Test predictive capability: can Z_ε provide early warning of degraded confinement?

### Test Case 3: Parameter Scan (Systematic Sensitivity Study)

**Variables to scan:**
- Perturbation strength ε (multipole error magnitudes)
- Working point (Q_x, Q_y) proximity to resonances
- Chromaticity settings
- Beam intensity (space charge effects if applicable)

**Diagnostic comparisons:**
- **Lyapunov exponents:** via variational equations (MAD-X PTC module)
- **FMA (Frequency Map Analysis):** via NAFF algorithm
- **MEGNO indicator:** via existing implementations
- **Z_σ diagnostic:** via new implementation

**Metrics to compare:**
- **Computational time:** wall-clock hours per 10^6 particle-turns
- **Sensitivity:** minimum detectable diffusion coefficient
- **False positive/negative rates:** how reliably each method flags diffusive onset
- **Ease of interpretation:** clarity of transition signature

**Expected results:**
- Z_σ computational advantage: 10-100× speedup confirmed
- Comparable or superior sensitivity to diffusion onset
- Clearer transition signature (binary: exponentially small vs. secular)

---

## Phase 5: Experimental Validation

### Live Beam Tests (Partnerships Required)

**Target facilities:**
1. **CERN LHC or IOTA** (Fermilab Integrable Optics Test Accelerator)
2. **Alternative:** European XFEL, SLAC LCLS (linacs with collective effects)

**Proposal elements:**
- Beam time request: 8-24 hours for dedicated study
- Required instrumentation: beam position monitors (BPMs), beam loss monitors (BLMs)
- Experimental protocol: systematic collimator scans or resonance crossings
- Real-time diagnostic: implement Z_ε calculation from BPM data stream

**Key measurements:**
1. **Collimator scan protocol** (ref: recent LHC studies, WEPA022 2023):
   - Slowly move collimator jaw inward
   - Monitor beam loss rate at each position
   - Simultaneously compute Z_ε from BPM second moments
   - Compare: does Z_ε show secular growth before losses spike?

2. **Controlled resonance crossing:**
   - Slowly ramp working point toward known resonance
   - Monitor both traditional diagnostics and Z_ε
   - Test hypothesis: Z_ε provides earlier warning than loss monitors

3. **Long-term stability measurement:**
   - Store beam for maximum possible time (hours)
   - Continuous Z_ε monitoring
   - Correlate with gradual emittance growth and beam lifetime

**Success criteria:**
- Z_ε shows secular growth 10-30 minutes before measurable beam losses
- Correlation coefficient |r| > 0.8 between Z_ε and loss rate
- Demonstration of predictive capability for adaptive control

**Adaptive control concept (stretch goal):**
- Feedback loop: Z_ε → tune/chromaticity correction → restored confinement
- Real-time optimization of working point based on Z_ε minimization
- Potential application: automated collimation optimization

---

## Phase 6: Documentation and Dissemination

### Technical Papers

**Paper 1: Theory and Numerical Validation**
- *Target journal:* Physical Review Accelerators and Beams (PRAB)
- *Length:* 12-15 pages
- *Content:* Theorems 1-2 proofs, Hénon map validation, LHC simulation results, computational comparison
- *Timeline:* Submit within 6 months of completing numerical experiments

**Paper 2: Experimental Validation**
- *Target journal:* Physical Review Accelerators and Beams or Nuclear Instruments and Methods A
- *Length:* 8-10 pages
- *Content:* Live beam test results, collimator scan analysis, predictive capability demonstration
- *Timeline:* Submit within 3 months of beam time completion

**Paper 3: Software Tool and Community Adoption**
- *Target:* Journal of Computational Physics or Computer Physics Communications
- *Length:* 6-8 pages + extensive supplementary material
- *Content:* Implementation details, user guide, benchmarks, open-source release
- *Timeline:* Concurrent with Paper 1

### Conference Presentations

**High-priority venues:**
1. **IPAC (International Particle Accelerator Conference)** - annual, May
2. **NAPAC (North American Particle Accelerator Conference)** - biennial
3. **Chamonix Workshop** (CERN annual LHC performance review) - January
4. **ICFA Advanced Beam Dynamics Workshops** - topical

**Presentation strategy:**
- First talk: Theory introduction + preliminary simulations (IPAC 2026)
- Second talk: Full numerical validation (NAPAC 2027 or IPAC 2027)
- Third talk: Experimental results (Chamonix 2027 or 2028)

### Software Release

**Open-source package: "BeamFlux" or "ZDiagnostic"**

**Repository structure:**
```
beam-flux-diagnostic/
├── src/
│   ├── madx_plugin/          # MAD-X integration
│   ├── sixtrack_plugin/      # SixTrack integration  
│   ├── xsuite_module/        # Xsuite Python module
│   └── standalone/           # Generic Python/Fortran library
├── examples/
│   ├── henon_map.py
│   ├── lhc_lattice/
│   └── simple_ring/
├── tests/
│   ├── unit_tests/
│   └── validation_tests/
├── docs/
│   ├── theory.md
│   ├── user_guide.md
│   └── api_reference.md
├── benchmarks/
│   └── comparison_to_fma_megno/
└── README.md
```

**Release targets:**
- GitHub: https://github.com/zfifteen/beam-flux-diagnostic
- PyPI: `pip install beam-flux-diagnostic`
- CERN GitLab (for MAD-X integration): official plugin submission

**Documentation requirements:**
- Theory background (digestible for practitioners)
- Installation instructions for each code platform
- Worked examples with expected outputs
- Troubleshooting guide
- Performance optimization tips

---

## Phase 7: Community Engagement

### Collaboration Building

**Key stakeholders to engage:**
1. **MAD-X development team** (CERN BE-ABP group)
   - Contact: Tobias Persson, Riccardo De Maria
   - Pitch: Low-overhead diagnostic for routine tracking studies
   
2. **LHC beam dynamics group** (CERN)
   - Contact: Massimo Giovannozzi (Nekhoroshev expert)
   - Pitch: Direct connection to existing DA modeling work
   
3. **SixTrack maintainers**
   - Pitch: Enhance halo prediction capabilities
   
4. **Fermilab IOTA project** (integrable optics test)
   - Contact: Sergei Nagaitsev, Valeri Lebedev
   - Pitch: Novel diagnostic for nonlinear integrable lattices

**Partnership benefits:**
- Co-authorship on papers
- Beam time access for experiments
- Code integration and maintenance support
- Visibility in accelerator physics community

### Tutorial Development

**Target audience:** Graduate students and early-career researchers

**Content outline:**
1. **Module 1:** Hamiltonian mechanics refresher
2. **Module 2:** Nekhoroshev theorem intuition (no full proof)
3. **Module 3:** Z_σ diagnostic derivation
4. **Module 4:** Hands-on: Implementing in MAD-X
5. **Module 5:** Case study: LHC simulation
6. **Module 6:** Interpretation and troubleshooting

**Delivery formats:**
- Jupyter notebooks with interactive examples
- Video lectures (20-30 min each module)
- Live workshops at accelerator schools (USPAS, CERN Accelerator School)

---

## Success Metrics

### Technical Milestones
- [ ] Theorems 1-2 proven for accelerator symplectic maps
- [ ] Code integrated into ≥2 major tracking platforms
- [ ] Computational speedup ≥10× demonstrated vs. FMA/MEGNO
- [ ] LHC simulation validation: match published DA evolution
- [ ] Experimental beam test completed with positive results

### Impact Metrics
- [ ] ≥2 papers published in high-impact journals (PRAB)
- [ ] ≥50 citations within 2 years of first publication
- [ ] ≥5 independent research groups adopt the method
- [ ] Software package: ≥100 downloads/month after 1 year
- [ ] Invited talk at major conference (IPAC, PAC)

### Community Adoption
- [ ] MAD-X official documentation includes Z_σ diagnostic
- [ ] Used in ≥1 major facility's operational procedures (LHC, IOTA, etc.)
- [ ] Tutorial attended by ≥20 students at accelerator school
- [ ] Contribution to CERN or Fermilab internal notes/reports

---

## Timeline Summary

| Phase | Duration | Key Deliverables |
|-------|----------|------------------|
| Phase 1: Q selection | 2 weeks | Optimal confinement functional chosen |
| Phase 2: Theory | 1 month | Theorems proven, technical note drafted |
| Phase 3: Implementation | 2 months | Code integrated into MAD-X, SixTrack, Xsuite |
| Phase 4: Simulations | 3 months | Hénon, LHC, parameter scan completed |
| Phase 5: Experiments | 6 months | Beam time proposal, execution, analysis |
| Phase 6: Papers | 4 months | Papers 1-3 drafted and submitted |
| Phase 7: Dissemination | Ongoing | Talks, tutorials, community engagement |

**Total to first paper submission:** ~6-7 months  
**Total to experimental validation paper:** ~12-14 months

---

## Risk Mitigation

**Risk 1:** MAD-X integration more complex than expected  
*Mitigation:* Start with standalone Python tool, later port to Fortran

**Risk 2:** Computational overhead too high for routine use  
*Mitigation:* Implement adaptive sampling (compute every N turns), GPU acceleration

**Risk 3:** Experimental beam time unavailable  
*Mitigation:* Focus on archival data analysis (LHC Run 2/3 datasets publicly available)

**Risk 4:** Diagnostic doesn't show clear advantage over existing methods  
*Mitigation:* Pivot to niche application (e.g., real-time monitoring for adaptive control)

---

## Resources Required

**Computational:**
- HPC cluster access: 1000-10,000 CPU-hours for parameter scans
- Existing at most universities/national labs

**Personnel:**
- Primary researcher: 50% FTE for 12 months
- Collaborator access: accelerator physicist (10% FTE advisory)
- Optional: software engineer (20% FTE for 3 months for integration)

**Travel:**
- 2-3 conferences (~$5K total)
- 1-2 site visits to CERN/Fermilab (~$3K total)

**Total estimated cost:** $80K-120K (salary + travel + computing)

---

## Proactive Next Steps

Based on highest probability of your next actions:

1. **Most likely (60%):** Request clarification on specific implementation details  
   *Prepared response:* I can provide detailed code templates, specific lattice file formats, or expanded theory derivations

2. **Second likely (25%):** Ask for help drafting collaboration email or proposal abstract  
   *Prepared response:* I can draft a compelling 1-page pitch for CERN collaborators or IOTA beam time proposal

3. **Third likely (15%):** Request breakdown of one specific phase (e.g., just the numerical implementation)  
   *Prepared response:* I can expand any phase into a standalone detailed protocol with week-by-week subtasks
