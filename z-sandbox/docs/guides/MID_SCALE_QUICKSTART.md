# Mid-Scale Validation - Quick Reference Guide

**User Story:** ZSB-VALID-512  
**Purpose:** Validate z-sandbox framework on 512-768 bit balanced semiprimes

## Quick Start (5 minutes)

### 1. Demo Run (128-bit, fast)
```bash
python3 python/mid_scale_demo.py
```
Expected: Complete in <1 second, shows full pipeline execution.

### 2. Generate Test Targets (3 targets, 512-bit)
```bash
python3 python/mid_scale_semiprime_generator.py \
  --num-targets 3 \
  --min-bits 512 \
  --max-bits 512 \
  --output test_targets.json
```
Expected: ~1-2 seconds per target.

### 3. Run Small Validation
```bash
python3 python/mid_scale_validation_runner.py \
  --targets test_targets.json \
  --num-samples 5000 \
  --output test_results.csv
```
Expected: Several minutes for 3 targets.

### 4. Visualize Results
```bash
python3 python/mid_scale_visualize.py \
  --input test_results.csv \
  --output plots/
```
Expected: Generates 4 plots + summary report.

## Full Validation Run (Production)

### Generate 10 Mid-Scale Targets
```bash
python3 python/mid_scale_validation_runner.py \
  --generate \
  --num-targets 10 \
  --min-bits 512 \
  --max-bits 768
```
Expected: ~30-60 seconds for generation.

### Run Validation Suite
```bash
python3 python/mid_scale_validation_runner.py \
  --targets mid_scale_targets.json \
  --dims 15 \
  --sampling-mode rqmc_adaptive \
  --num-samples 50000 \
  --output mid_scale_results.csv
```
Expected: Several hours to days depending on hardware.

### Analyze Results
```bash
python3 python/mid_scale_visualize.py \
  --input mid_scale_results.csv \
  --output validation_plots/
```

## Configuration Tuning

### For Speed (Quick Testing)
```bash
--dims 5 \
--sampling-mode rqmc_sobol \
--num-samples 1000
```

### For Accuracy (Full Validation)
```bash
--dims 15 \
--sampling-mode rqmc_adaptive \
--num-samples 100000
```

### For Balance (Recommended)
```bash
--dims 11 \
--sampling-mode rqmc_sobol \
--num-samples 10000
```

## Key Files

| File | Purpose | Size |
|------|---------|------|
| `mid_scale_semiprime_generator.py` | Generate targets | 360 lines |
| `mid_scale_validation_runner.py` | Run validation | 560 lines |
| `mid_scale_demo.py` | Quick demo | 160 lines |
| `mid_scale_visualize.py` | Visualizations | 370 lines |
| `test_mid_scale_generator.py` | Tests | 280 lines |
| `MID_SCALE_VALIDATION.md` | Documentation | 12 KB |

## Expected Performance

### Target Metrics (from User Story)

| Metric | Target | Status |
|--------|--------|--------|
| Success Rate | >50% | ⏳ To be measured |
| Speedup vs ECM | 10-20× | ⏳ Benchmark needed |
| Variance Reduction | >1,000× | ✅ Configured |
| Runtime (512-bit) | <50 hours | ⏳ To be measured |
| Runtime (768-bit) | <100 hours | ⏳ To be measured |

### Typical Timings (on consumer hardware)

| Bit Length | Generation | Per-Target Validation | Total (10 targets) |
|------------|------------|----------------------|-------------------|
| 512 | 2-5 sec | 30-120 min | 5-20 hours |
| 640 | 3-7 sec | 60-240 min | 10-40 hours |
| 768 | 5-10 sec | 120-480 min | 20-80 hours |

*Note: Times are estimates and vary greatly with hardware and configuration.*

## Troubleshooting

### Issue: "No factors found" for all targets
**Solution:** 
- Increase `--num-samples` (try 50000 or 100000)
- Try different `--sampling-mode` (rqmc_adaptive)
- Increase `--dims` (try 15 or 20)

### Issue: Out of memory
**Solution:**
- Decrease `--num-samples`
- Process fewer targets at once
- Use 64-bit Python build

### Issue: Too slow
**Solution:**
- Decrease `--dims` (try 5 or 7)
- Use `--sampling-mode rqmc_sobol` (fastest)
- Decrease `--num-samples`

### Issue: Import errors
**Solution:**
```bash
# Ensure all dependencies installed
pip install -r python/requirements.txt

# Set PYTHONPATH
export PYTHONPATH=/path/to/z-sandbox/python

# Or use absolute imports
python3 -c "import sys; sys.path.insert(0, 'python'); import mid_scale_validation_runner"
```

## Validation Checklist

Before reporting results, verify:

- [ ] All targets are balanced (±2 bits between p and q)
- [ ] No special forms used (check with --validate)
- [ ] Cryptographic randomness (Python secrets module)
- [ ] Reproducible (same seed gives same results)
- [ ] Metrics logged (CSV output generated)
- [ ] Visualizations created (plots directory populated)
- [ ] Tests pass (pytest tests/test_mid_scale_generator.py)
- [ ] No security alerts (CodeQL checker passed)

## Integration with Existing Framework

This implementation integrates:

1. **Z5D Axioms** (`z5d_axioms.py`)
   - κ(n) curvature for geometric weighting
   - θ'(n,k) resolution for prime bias

2. **Perturbation Theory** (`perturbation_theory.py`)
   - Laguerre polynomial basis
   - Anisotropic lattice distances
   - Vectorial perturbations

3. **Monte Carlo** (`monte_carlo.py`)
   - φ-biased sampling
   - Variance reduction modes
   - Low-discrepancy sequences

4. **RQMC Control** (`rqmc_control.py`)
   - Scrambled Sobol' sampling
   - Adaptive α scheduling
   - Ensemble replications

## References

- User Story: `ZSB-VALID-512`
- Documentation: `docs/MID_SCALE_VALIDATION.md`
- Tests: `tests/test_mid_scale_generator.py`
- Example: `python/mid_scale_demo.py`

## Support

For issues or questions:
1. Check `docs/MID_SCALE_VALIDATION.md` for detailed information
2. Run demo script to verify installation: `python3 python/mid_scale_demo.py`
3. Check test suite: `pytest tests/test_mid_scale_generator.py -v`
4. Review configuration in runner script comments

---

**Version:** 1.0  
**Last Updated:** 2025-10-28  
**Status:** Ready for Production Validation
