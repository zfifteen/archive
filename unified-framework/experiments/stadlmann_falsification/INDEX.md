# Stadlmann Distribution Level Falsification - Master Index

## 🎯 Start Here

**Quick Summary:** The claimed 1-2% density boost from Stadlmann's distribution level θ ≈ 0.525 is **FALSIFIED**. The measured effect is ~0.20% (5-10× smaller than claimed).

**Status:** ⚠️ **PARTIAL FALSIFICATION** - The parameter works as a "dial" but the practical benefit is overstated.

---

## 📚 Document Navigation

### 1. Executive Summary (Start Here) ⭐
**File:** [EXECUTIVE_SUMMARY.md](EXECUTIVE_SUMMARY.md)

**Content:**
- Overall verdict and key findings
- Test-by-test results (5 tests)
- Statistical rigor details
- Recommendations

**Key Takeaway:** While θ functions as a "tunable dial" technically, the claimed 1-2% density boost is false - actual measurement shows ~0.20%.

**Read Time:** 10 minutes

---

### 2. Technical Analysis (Deep Dive)
**File:** [TECHNICAL_ANALYSIS.md](TECHNICAL_ANALYSIS.md)

**Content:**
- Mathematical background (Stadlmann 2023, Bombieri-Vinogradov)
- Z Framework implementation details
- Experimental methodology explained
- Root cause analysis of discrepancy
- Mathematical verification

**Key Insights:**
- Stadlmann's θ ≈ 0.5253 is an error term exponent, not a density multiplier
- Conical flow model may incorrectly translate θ to density
- Linear scaling assumption (BOOST_SCALING_FACTOR = 0.04) was never validated

**Read Time:** 15 minutes

---

### 3. Comparison with Existing Benchmark
**File:** [COMPARISON.md](COMPARISON.md)

**Content:**
- Cross-validation with `benchmarks/stadlmann_extended_validation.py`
- Perfect agreement on scale dependence (0.179%, 0.223%, 0.268%)
- Existing benchmark confirms 0% pass rate when verification enabled
- Explanation of why existing test didn't catch this

**Key Finding:** Both our test and the existing benchmark show ~0.2% enhancement. The benchmark has a `--verify-claims` flag that reveals 0/8 tests pass, but it's off by default.

**Read Time:** 8 minutes

---

### 4. Experiment Documentation
**File:** [README.md](README.md)

**Content:**
- Quick start guide
- Test descriptions
- Falsification methodology
- Requirements and runtime
- Results summary table

**Use Case:** Running the experiment yourself or understanding the methodology at a glance.

**Read Time:** 5 minutes

---

## 🧪 Experiment Files

### Main Experiment Code
**File:** `falsification_experiment.py` (615 lines)

**Tests Implemented:**
1. **Independence Test** - Verifies θ affects predictions (✅ SUPPORTED)
2. **Monotonicity Test** - Checks monotonic behavior (✅ SUPPORTED)
3. **Claimed Boost Test** - Validates 1-2% claim (❌ FALSIFIED)
4. **Scale Invariance Test** - Checks consistency across scales (✅ SUPPORTED)
5. **Randomness Test** - Tests if θ=0.525 is special (✅ SUPPORTED)

**Run:**
```bash
python falsification_experiment.py --seed 42
```

**Output:** `results.json` with full numerical data

---

### Results Data
**File:** `results.json`

**Content:**
- Raw test results (seed=42)
- All measurements and statistics
- Per-test falsification status
- Summary statistics

**Format:** JSON (easily parsed for further analysis)

---

### Visualization Script
**File:** `visualize_results.py`

**Generates:**
1. `falsification_visualization.png` - 4-panel test summary
2. `enhancement_comparison.png` - Claimed vs measured bar chart

**Run:**
```bash
python visualize_results.py
```

---

## 📊 Key Results at a Glance

### Test Summary
| Test | Status | Critical Metric | Threshold | Pass? |
|------|--------|----------------|-----------|-------|
| Independence | ✅ SUPPORTED | 0.84% effect | >0.01% | ✅ |
| Monotonicity | ✅ SUPPORTED | 0 reversals | <2 | ✅ |
| **Claimed Boost** | ❌ **FALSIFIED** | **0.20% boost** | **[0.8%, 2.2%]** | ❌ |
| Scale Invariance | ✅ SUPPORTED | CV=0.163 | <0.5 | ✅ |
| Randomness | ✅ SUPPORTED | 0% similar | <50% | ✅ |

**Overall:** 4/5 tests supported, but the 1 falsified test represents the core practical claim.

### Enhancement Measurements
| Method | Measurement | Status |
|--------|-------------|--------|
| **Claimed Minimum** | 1.0% | ❌ Not met |
| **Claimed CI Lower** | 0.8% | ❌ Not met |
| Bootstrap Test | **0.2025%** | ✅ Measured |
| Scale 10⁴ | 0.179% | ✅ Measured |
| Scale 10⁵ | 0.223% | ✅ Measured |
| Scale 10⁶ | 0.268% | ✅ Measured |
| **Claimed CI Upper** | 2.2% | ❌ Not met |
| **Claimed Maximum** | 2.0% | ❌ Not met |

**Conclusion:** All measurements ~0.2%, all claims 1-2% → **5-10× discrepancy**

---

## 🔬 Methodology

### Statistical Rigor
- ✅ Deterministic (seed=42)
- ✅ Large samples (10,000 primes, 100+ predictions)
- ✅ Bootstrap CIs (1,000 resamples)
- ✅ Multiple scales (10⁴, 10⁵, 10⁶)
- ✅ Clear pre-defined criteria
- ✅ Cross-validated with existing benchmark

### Falsification Criteria
Each test has a **clear falsification criterion**:
- **Independence:** Mean relative difference < 0.01% → FALSIFIED
- **Monotonicity:** ≥2 direction changes → FALSIFIED
- **Claimed Boost:** Mean outside [1%, 2%] OR CI doesn't overlap [0.8%, 2.2%] → FALSIFIED ✓
- **Scale Invariance:** CV > 0.5 → FALSIFIED
- **Randomness:** >50% of random values similar → FALSIFIED

Only the **Claimed Boost** test was falsified.

---

## 🎓 Interpretation

### What This Means

**Technical Implementation: ✅ CORRECT**
- θ parameter is properly integrated into Z5D predictor
- Conical flow model functions as designed
- Monotonic, scale-invariant behavior
- Non-arbitrary optimal value (θ=0.525)

**Practical Utility: ❌ OVERSTATED**
- Claimed 1-2% boost is **false**
- Actual ~0.2% effect is **too weak** for most applications
- "First-class computational primitive" designation is **misleading**

**Documentation: ❌ INCORRECT**
- Multiple files claim 1-2% enhancement
- Benchmark has hardcoded assumption (BOOST_SCALING_FACTOR = 0.04 "~2%")
- Existing tests don't verify claims by default

### Why It Matters

This represents a **5-10× overstatement** of a core framework feature's practical benefit. While the implementation is correct, the marketing and documentation make claims not supported by empirical testing.

---

## 💡 Recommendations

### Immediate (Documentation)
1. Update `src/core/params.py:115` - Correct 1-2% claim to ~0.2%
2. Update `src/core/z_5d_enhanced.py:319` - Same correction
3. Update `benchmarks/README.md:26` - Update claimed ranges
4. Update whitepapers - Search for "1-2%" claims
5. Enable `--verify-claims` by default in benchmark

### Future Research
1. **Test ultra-scales:** Perhaps effect emerges at k > 10⁶ or 10⁹?
2. **Test AP-filtered primes:** Maybe effect is specific to arithmetic progressions?
3. **Mathematical audit:** Verify conical flow translation of Stadlmann's result
4. **Different baselines:** Test θ=0.525 vs θ=0.5 (BV) instead of θ=0.51

### Code Changes (If 0.2% Stands)
If further testing confirms ~0.2% effect:
- Replace hardcoded `BOOST_SCALING_FACTOR = 0.04`
- Use actual `conical_density_enhancement_factor()` in benchmarks
- Add warnings about weak practical effect
- Reconsider "first-class primitive" framing

---

## 📖 Citation

If you use this falsification experiment in your work:

```
Stadlmann Distribution Level Falsification Experiment
Z Framework - github.com/zfifteen/unified-framework
experiments/stadlmann_falsification/
Date: 2025-11-18
Seed: 42 (reproducible)
```

---

## 🏁 Final Verdict

**The Hypothesis:** "Stadlmann's θ ≈ 0.525 operates as a 'tunable density dial' providing 1-2% density enhancements"

**Verdict:** **PARTIALLY FALSE**

- ✅ **"Tunable dial"** - TRUE (monotonic, scale-invariant, measurable effects)
- ❌ **"1-2% enhancements"** - FALSE (measured: ~0.20%, 5-10× smaller)

**Confidence:** **HIGH** (tight CIs, large samples, cross-validated, reproducible)

**Impact:** Significant overstatement requiring documentation corrections throughout the codebase.

---

**For Questions:** See individual documents for detailed explanations, or re-run the experiment with `--seed 42` for reproducibility.

**Last Updated:** 2025-11-18
