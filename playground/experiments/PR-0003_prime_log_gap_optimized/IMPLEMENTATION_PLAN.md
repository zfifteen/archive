# PR-0003 Implementation Plan

## Status: Phase 1 Complete - Structure Created

### Implementation Approach: Incremental Coding

Following the incremental coding protocol, this experiment is being built in phases:

**Phase 1 (COMPLETE):** ✓ Create complete structure with ONE implemented function
**Phase 2 (NEXT):** Implement functions incrementally, one at a time

---

## Current State

### ✓ Fully Implemented
- `prime_generator.sieve_of_eratosthenes()` - Basic sieve for small primes

### 📝 Documented (Ready for Implementation)

#### Module: prime_generator.py
- [ ] `segmented_sieve()` - Memory-efficient segmented sieve
- [ ] `generate_primes_to_limit()` - Generate/load with caching
- [ ] `compute_gaps()` - Compute and cache gaps

#### Module: binning.py  
- [ ] `compute_log_prime_bins()` - Create 100 equal-width bins on log-prime axis
- [ ] `compute_bin_statistics()` - Compute mean, var, skew, kurt per bin
- [ ] `analyze_bins()` - Complete binning analysis pipeline

#### Module: statistics.py
- [ ] `linear_regression()` - Regression on bin means
- [ ] `kolmogorov_smirnov_tests()` - KS tests for multiple distributions
- [ ] `ljung_box_test()` - Autocorrelation test
- [ ] `compute_acf_pacf()` - ACF and PACF computation
- [ ] `check_decay_monotonic()` - Monotonic decay check
- [ ] `compute_skewness_kurtosis()` - Distribution moments

#### Module: visualization_2d.py (12 functions)
- [ ] `plot_decay_trend()` - Decay with regression
- [ ] `plot_log_gap_histogram()` - Histogram
- [ ] `plot_qq_lognormal()` - Q-Q plot
- [ ] `plot_acf()` - ACF plot
- [ ] `plot_pacf()` - PACF plot
- [ ] `plot_log_prime_vs_log_gap()` - Scatter
- [ ] `plot_box_plot_per_bin()` - Box plots
- [ ] `plot_cdf()` - CDF comparison
- [ ] `plot_kde()` - KDE plot
- [ ] `plot_regression_residuals()` - Residual plot
- [ ] `plot_log_gap_vs_regular_gap()` - Gap comparison
- [ ] `plot_prime_density()` - Density plot

#### Module: visualization_3d.py (5 functions)
- [ ] `plot_scatter_3d()` - 3D scatter
- [ ] `plot_surface_3d()` - Surface plot
- [ ] `plot_contour_3d()` - Contour plot
- [ ] `plot_wireframe_3d()` - Wireframe
- [ ] `plot_bar_3d()` - 3D bar chart

#### Module: run_experiment.py
- [ ] `run_experiment()` - Main pipeline
- [ ] `parse_arguments()` - CLI parsing
- [ ] `main()` - Entry point

---

## Implementation Order (Proposed)

Following dependency order and foundational-first approach:

### Batch 1: Core Infrastructure (4 functions)
1. `segmented_sieve()` - Needed for prime generation
2. `generate_primes_to_limit()` - Needed for all analysis
3. `compute_gaps()` - Needed for all analysis
4. `compute_log_prime_bins()` - Foundation for binning

### Batch 2: Binning & Statistics (5 functions)
5. `compute_bin_statistics()` - Extends binning
6. `analyze_bins()` - Completes binning module
7. `linear_regression()` - Key statistical test
8. `compute_skewness_kurtosis()` - Simple statistics
9. `check_decay_monotonic()` - Simple check

### Batch 3: Advanced Statistics (3 functions)
10. `kolmogorov_smirnov_tests()` - Complex but critical
11. `compute_acf_pacf()` - Needed for ACF/PACF plots
12. `ljung_box_test()` - Autocorrelation test

### Batch 4: Core 2D Plots (6 functions)
13. `plot_decay_trend()` - Most important plot
14. `plot_log_gap_histogram()` - Essential visualization
15. `plot_qq_lognormal()` - Distribution check
16. `plot_acf()` - Uses compute_acf_pacf()
17. `plot_pacf()` - Uses compute_acf_pacf()
18. `plot_log_prime_vs_log_gap()` - Basic scatter

### Batch 5: Additional 2D Plots (6 functions)
19. `plot_box_plot_per_bin()` - Distribution viz
20. `plot_cdf()` - CDF comparison
21. `plot_kde()` - KDE visualization
22. `plot_regression_residuals()` - Regression diagnostic
23. `plot_log_gap_vs_regular_gap()` - Gap comparison
24. `plot_prime_density()` - Validation plot

### Batch 6: 3D Plots (5 functions)
25. `plot_scatter_3d()` - 3D scatter
26. `plot_surface_3d()` - Surface
27. `plot_contour_3d()` - Contour
28. `plot_wireframe_3d()` - Wireframe
29. `plot_bar_3d()` - Bar chart

### Batch 7: Integration (3 functions)
30. `run_experiment()` - Main pipeline
31. `parse_arguments()` - CLI
32. `main()` - Entry point

**Total Functions to Implement:** 32 (1 already done, 31 remaining)

---

## Next Steps

To continue implementation, simply say "continue" or "implement next".

Each iteration will:
1. Select ONE function from the list above
2. Implement it COMPLETELY with full logic, error handling, documentation
3. Update ALL related comment blocks in other files
4. Test the implementation (when possible)

---

## Testing Strategy

As functions are implemented:
- Test small-scale first (e.g., 10^6 primes)
- Validate against PR-0002 results where applicable
- Check for NaN/Inf values
- Verify file I/O and caching
- Test plots on sample data

---

## Success Criteria

Experiment is complete when:
- [ ] All 32 functions implemented
- [ ] Can generate primes up to 10^9
- [ ] All 17 plots generated successfully
- [ ] results.json contains complete analysis
- [ ] Runs in <20 minutes for 10^9 primes
- [ ] Results align with PR-0002 methodology

---

Last updated: Phase 1 complete
Next action: Implement `segmented_sieve()`
