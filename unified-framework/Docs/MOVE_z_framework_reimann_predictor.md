# Z-Framework Riemann Predictor Move Artifacts Documentation

This document provides a comprehensive inventory of all artifacts related to the Riemann Hypothesis (RH) symmetry analysis, Z5D predictors, and related symmetry diagnostics that need to be included in the framework move.

## 1. Core Implementation Files

### Primary Experimental Framework
- **`riemann_z5d_symmetry_experiment.py`** (491 lines)
  - Main experimental implementation with high-precision arithmetic (50 decimal places)
  - Complete Z5D vs Riemann predictor comparison
  - Statistical analysis including correlation, scaling, and oscillation detection
  - Automated plot generation and results export
  - **Dependencies:** numpy, scipy, matplotlib, mpmath
  - **Status:** Core artifact - CRITICAL for move

### Z5D Predictor Implementations
- **`src/core/z_5d_enhanced.py`**
  - Enhanced Z5D predictor implementation
  - Core mathematical functions for prime prediction
  - **Dependencies:** Core framework components
  - **Status:** Core artifact - CRITICAL for move

- **`src/z_framework/discrete/z5d_predictor.py`**
  - Discrete Z5D predictor implementation
  - Specialized for discrete mathematical operations
  - **Dependencies:** Z-framework discrete components
  - **Status:** Core artifact - CRITICAL for move

- **`z5d_pi_fast_integrated.py`**
  - Fast integrated Z5D implementation for π(x) calculations
  - Optimized performance version
  - **Status:** Supporting artifact - HIGH priority for move

- **`validate_z5d_implementation.py`**
  - Validation framework for Z5D implementations
  - Critical for maintaining accuracy post-move
  - **Status:** Supporting artifact - HIGH priority for move

### Symmetry Diagnostics Visualization
- **`src/visualization/symmetry_diagnostics.py`**
  - Generates Figure X: Symmetry diagnostics between Li and Z₅D predictors
  - Four-panel comprehensive analysis (Collapse Test, Pivot Symmetry, Order-Gap Check, Affine Alignment)
  - **Dependencies:** matplotlib, numpy, core Z5D predictor
  - **Status:** Core artifact - CRITICAL for move

- **`src/visualization/theoretical_symmetry_diagnostics.py`**
  - Theoretical symmetry diagnostics implementation
  - Demonstrates expected behavior patterns
  - **Dependencies:** matplotlib, numpy, scipy
  - **Status:** Core artifact - CRITICAL for move

## 2. Scientific Documentation

### White Papers and Research Papers
- **`WHITE_PAPER_RIEMANN_Z5D_SYMMETRY_FALSIFICATION.md`**
  - Rigorous scientific falsification of "Riemann Predictors to Highlight Potential Symmetries" hypothesis
  - Complete methodology, results, and statistical analysis
  - **Status:** Core documentation - CRITICAL for move

- **`RIEMANN_Z5D_IMPLEMENTATION_SUMMARY.md`**
  - Implementation summary with key scientific findings
  - Project overview and deliverables
  - **Status:** Core documentation - CRITICAL for move

### Technical Documentation
- **`docs/visualization/symmetry_diagnostics.md`**
  - Technical documentation for symmetry diagnostics plots
  - Panel descriptions, parameters, usage instructions
  - Theoretical foundation and integration notes
  - **Status:** Core documentation - CRITICAL for move

### Research Reports
- **`docs/reports/zeta-validation-summary.md`**
  - Summary of zeta function validation results
  - **Status:** Supporting documentation - MEDIUM priority

## 3. Experimental Data and Results

### Primary Experimental Results
- **`riemann_z5d_experiment_results.json`** (4,093 bytes)
  - Complete experimental results from main framework
  - Statistical correlation data, scaling analysis, oscillation patterns
  - **Status:** Core data - CRITICAL for move

- **`riemann_z5d_experiment_report.txt`** (1,079 bytes)
  - Human-readable summary of experimental findings
  - **Status:** Core data - CRITICAL for move

### Validation Results
- **`computational_validation_results.json`** (6,040 bytes)
  - Computational validation data
  - **Status:** Supporting data - HIGH priority

- **`validation_results.json`** (160,167 bytes)
  - Comprehensive validation results
  - **Status:** Supporting data - HIGH priority

- **`tests/zeta_validation_results/`** (directory)
  - Directory containing zeta function validation results
  - **Status:** Supporting data - MEDIUM priority

### High-Precision Zeta Zero Data
- **`tests/zeta_zeros.csv`**
  - High-precision zeta zero values
  - Critical for Riemann hypothesis calculations
  - **Status:** Core data - CRITICAL for move

- **`test-finding/spectral-form-factor/*/zeta_zeros_*.csv`**
  - Multiple scale zeta zero datasets (small, medium, full scale)
  - **Status:** Supporting data - HIGH priority

### Problem Statement Reproduction
- **`problem_statement_reproduction_results.json`** (3,622 bytes)
  - Results from reproducing original problem statement
  - **Status:** Core data - HIGH priority

- **`reproduce_problem_statement.py`**
  - Script to reproduce original problem statement
  - **Status:** Supporting code - HIGH priority

## 4. Visualizations and Generated Plots

### Core Symmetry Diagnostic Plots
- **`tests/plots/symmetry_diagnostics_analysis_report.txt`** (610 bytes)
  - Statistical analysis report for actual symmetry diagnostics
  - **Status:** Core visualization - HIGH priority

- **`tests/plots/theoretical_symmetry_analysis_report.txt`** (830 bytes)
  - Analysis report for theoretical expectations
  - **Status:** Core visualization - HIGH priority

### Generated Experiment Plots
**Note:** Main experiment generates plots in `plots/` directory (not found in current state):
- **`plots/pred_vs_logk.png`** - Z5D vs Riemann predictions comparison (generated)
- **`plots/diff_vs_logk.png`** - Difference analysis across k values (generated)
- **`plots/norm_diff_vs_logk.png`** - Normalized difference patterns (generated)
- **`plots/symmetry_analysis_comprehensive.png`** - 4-panel comprehensive analysis (generated)
- **Status:** Generated visualizations - HIGH priority (need to be generated/preserved)

### Z5D Performance Visualizations
- **`tests/plots/z5d_absolute_errors.png`** (195,355 bytes)
  - Z5D absolute error analysis plot
  - **Status:** Core visualization - HIGH priority

- **`tests/plots/z5d_relative_errors.png`** (209,714 bytes)
  - Z5D relative error analysis plot
  - **Status:** Core visualization - HIGH priority

- **`tests/plots/z5d_predictions_vs_ground_truth.png`** (231,772 bytes)
  - Z5D predictions compared to ground truth
  - **Status:** Core visualization - HIGH priority

- **`tests/plots/z5d_improvement_factors.png`** (180,244 bytes)
  - Analysis of Z5D improvement factors
  - **Status:** Core visualization - HIGH priority

- **`tests/plots/z5d_comprehensive_summary.png`** (476,792 bytes)
  - Comprehensive summary visualization
  - **Status:** Core visualization - HIGH priority

### Prime Number Geometry Plots
- **`src/number-theory/prime-number-geometry/plots/`** (directory, ~5.5MB total)
  - Multiple timestamped plot files showing prime number geometric relationships
  - Files include: plot_2025-07-28_*.png, plot_2025-07-29_*.png
  - **Status:** Supporting visualizations - MEDIUM priority

### Enhanced Prime Geometry Visualizations
- **`src/number-theory/prime-curve/warp/enhanced_prime_geometry_*.png`**
  - Enhanced prime geometry for different scales (100, 1000, 6000)
  - **Status:** Supporting visualizations - MEDIUM priority
- **`tests/plots/z5d_enhanced/`** (directory)
  - **`parameter_space_3d_interactive.html`** - Interactive 3D parameter space
  - **`parameter_sensitivity_3d.html`** - 3D parameter sensitivity analysis
  - **`prediction_surface_3d.html`** - 3D prediction surface visualization
  - **Status:** Enhanced visualizations - MEDIUM priority

### Riemann Zeta Visualizations
- **`tests/plots/comprehensive_3d/riemann_zeta/`** (directory)
  - **`riemann_zeta_zeros_3d.html`** - 3D visualization of Riemann zeta zeros
  - **Status:** Specialized visualization - MEDIUM priority

### Interactive HTML Visualizations
- **`cluster_analysis.html`** (4,782,342 bytes)
  - Large interactive cluster analysis visualization
  - **Status:** Supporting visualization - LOW priority (due to size)

- **`methodology_comparison.html`** (4,772,438 bytes)
  - Interactive methodology comparison
  - **Status:** Supporting visualization - LOW priority (due to size)

## 5. Scripts and Validation Tools

### Core Validation Scripts
- **`scripts/validate_z5d_formula.py`**
  - Z5D formula validation script
  - **Status:** Core validation - HIGH priority

- **`scripts/validate_z5d_performance.py`**
  - Z5D performance validation
  - **Status:** Core validation - HIGH priority

### Enhanced Demo Scripts
- **`scripts/z5d_enhanced_demo.py`**
  - Enhanced Z5D demonstration script
  - **Status:** Demo code - MEDIUM priority

- **`scripts/z5d_integration_demo.py`**
  - Z5D integration demonstration
  - **Status:** Demo code - MEDIUM priority

### Large-Scale Testbed Scripts
- **`scripts/z5d_prime_testbed_10e13.py`**
- **`scripts/z5d_prime_testbed_10e14.py`**
- **`scripts/z5d_prime_testbed_10e15.py`**
  - Large-scale testing scripts for different magnitudes
  - **Status:** Testing infrastructure - MEDIUM priority

### Zeta Function Analysis Scripts
- **`tests/test-finding/scripts/complete_zeta_analysis.py`**
- **`tests/test-finding/scripts/enhanced_zeta_analysis.py`**
- **`tests/test-finding/scripts/zeta_zero_correlation_analysis.py`**
- **`tests/test-finding/scripts/zeta_zeros_validation.py`**
  - Specialized zeta function analysis tools
  - **Status:** Analysis tools - MEDIUM priority

## 6. Test Infrastructure

### Core Z5D Tests
- **`tests/test_z5d_predictor.py`**
  - Core Z5D predictor tests
  - **Status:** Test infrastructure - HIGH priority

- **`tests/test_z5d_enhanced_visualizations.py`**
  - Tests for enhanced Z5D visualizations
  - **Status:** Test infrastructure - HIGH priority

- **`tests/test_z5d_empirical_validation.py`**
  - Empirical validation test suite
  - **Status:** Test infrastructure - HIGH priority

### Symmetry Analysis Components
- **`tests/test_efficiency_through_symmetry.py`**
  - Tests for efficiency through symmetry algorithms
  - **Status:** Test infrastructure - HIGH priority

- **`experiments/efficiency_through_symmetry.py`**
  - Experimental implementation of efficiency through symmetry
  - **Status:** Experimental code - MEDIUM priority

### Geodesic Analysis Components  
- **`examples/geodesic_clustering_examples.py`**
  - Geodesic clustering example implementations
  - **Status:** Example code - MEDIUM priority

- **`examples/demos/prime-geodesics/prime_geodesics.py`**
  - Prime geodesic demonstration code
  - **Status:** Demo code - MEDIUM priority

- **`docs/prime_geodesic_algorithms.md`**
  - Documentation for prime geodesic algorithms
  - **Status:** Technical documentation - MEDIUM priority

- **`docs/applications/geodesic_clustering_documentation.md`**
  - Geodesic clustering application documentation
  - **Status:** Application documentation - MEDIUM priority
- **`tests/test_z5d_k1000000_zeta_validation.py`**
- **`tests/test_z5d_large_scale_accuracy.py`**
- **`tests/test_z5d_scientific_testbed.py`**
- **`tests/test_z5d_testbed_10e14.py`**
- **`tests/test_z5d_testbed_10e15.py`**
- **`tests/test_z5d_testbed_integration.py`**
  - Comprehensive large-scale testing infrastructure
  - **Status:** Test infrastructure - HIGH priority

### Zeta Function Tests
- **`tests/test_z5d_zeta_validation.py`**
- **`tests/test_zero_line_zeta_integration.py`**
- **`test_zeta_cycling_hypothesis.py`**
- **`test_zeta_cycling_strategies.py`**
  - Zeta function specific test suites
  - **Status:** Test infrastructure - MEDIUM priority

### Quick Validation Tests
- **`tests/test_z5d_quick_validation.py`**
  - Fast validation tests for CI/CD
  - **Status:** Test infrastructure - HIGH priority

## 7. Examples and Demonstrations

### Core Examples
- **`examples/z_riemann_crypto.py`**
  - Riemann hypothesis cryptographic applications
  - **Status:** Example code - MEDIUM priority

- **`examples/zeta_zero_vortex.py`**
  - Zeta zero vortex demonstration
  - **Status:** Example code - MEDIUM priority

### Zeta Function Examples
- **`examples/zeta_shift_correlation.py`**
- **`examples/zeta_shift_correlation_demo.py`**
- **`examples/validate_zeta_shift_correlation.py`**
  - Zeta shift correlation demonstrations
  - **Status:** Example code - MEDIUM priority

### Specialized Lab Examples
- **`examples/lab/zeta-zero-embeddings.py`**
- **`examples/lab/zeta-zero-helical-embedding-analyzer/`**
  - Advanced zeta zero analysis tools
  - **Status:** Lab code - LOW priority

### Demo Directories
- **`examples/demos/zeta-orbits/`**
  - Zeta orbit demonstrations
  - **Status:** Demo code - LOW priority

## 8. Configuration and Documentation

### Test Documentation
- **`docs/z5d_test_specifications.md`**
- **`docs/z5d_testbed_10e14_documentation.md`**
- **`docs/z5d_testbed_10e15_documentation.md`**
- **`docs/z5d_testbed_10e16_documentation.md`**
  - Comprehensive testbed documentation
  - **Status:** Technical documentation - HIGH priority

### Validation Documentation
- **`docs/test-finding/zeta-validation/`** (directory)
  - Zeta validation methodology documentation
  - **Status:** Technical documentation - MEDIUM priority

### Generated Reports
- **`test_z5d_zeta_validation/z5d_zeta_validation_report.txt`**
  - Generated validation report
  - **Status:** Generated documentation - MEDIUM priority

## 9. Statistical and Analysis Components

### Statistical Analysis Modules
- **`src/statistical/zeta_correlations.py`**
- **`src/statistical/zeta_zeros_extended.py`**
  - Statistical analysis components for zeta functions
  - **Status:** Analysis components - HIGH priority

### Core Analysis Components
- **`src/core/discrete_zeta_shift_lattice.py`**
  - Discrete zeta shift lattice implementation
  - **Status:** Core component - HIGH priority

## 10. Notebooks and Interactive Analysis

### Jupyter Notebooks
- **`notebooks/z5d_prime_plus.ipynb`**
  - Interactive Z5D analysis notebook
  - **Status:** Interactive analysis - MEDIUM priority

- **`tests/Discrete_Zeta_Shift_Lattice.ipynb`**
  - Discrete zeta shift lattice analysis
  - **Status:** Interactive analysis - MEDIUM priority

## Move Strategy Recommendations

### Priority 1 (CRITICAL) - Must Move First
1. Core implementation files (riemann_z5d_symmetry_experiment.py, Z5D predictors)
2. White papers and implementation summary
3. Primary experimental results and reports
4. High-precision zeta zero data
5. Symmetry diagnostics visualization code

### Priority 2 (HIGH) - Move Early
1. Validation scripts and test infrastructure
2. Core visualization plots and reports
3. Supporting data files
4. Technical documentation

### Priority 3 (MEDIUM) - Move After Core
1. Enhanced visualizations and demo scripts
2. Analysis tools and specialized scripts
3. Example code and lab experiments
4. Jupyter notebooks

### Priority 4 (LOW) - Move Last or Evaluate
1. Large HTML visualization files (>1MB)
2. Specialized lab code
3. Demo directories with minimal dependencies

## Dependencies and Integration Points

### External Dependencies
- **Python packages:** numpy, scipy, matplotlib, mpmath
- **Data files:** Zeta zero CSV files, validation datasets
- **Framework components:** Core Z-framework modules

### Internal Dependencies
- Symmetry diagnostics depend on Z5D predictor implementations
- Validation scripts require both code and data artifacts
- Documentation references specific code files and results

### Post-Move Validation
1. Run `riemann_z5d_symmetry_experiment.py` to verify core functionality
2. Execute test suite: `test_z5d_predictor.py`, `test_z5d_quick_validation.py`
3. Generate symmetry diagnostics plots to verify visualization pipeline
4. Validate zeta zero data integrity

## File Size Summary
- **Large files (>1MB):** HTML visualizations (~15MB), PNG plot collections (~108MB)
- **Medium files (100KB-1MB):** Individual PNG plots, comprehensive JSON results
- **Small files (<100KB):** Documentation, Python scripts, small data files

**Total estimated size:** ~130-150 MB (including all plots and visualizations)
**Core artifacts only:** ~15-20 MB (excluding large plot directories)

### Size Breakdown by Category:
- **Plot directories:** ~108 MB (tests/plots/) + ~5.4 MB (prime geometry plots)
- **Large HTML files:** ~15 MB (cluster_analysis.html, methodology_comparison.html)
- **JSON results and data:** ~1-2 MB
- **Source code and documentation:** ~5-10 MB
- **Generated reports and logs:** <1 MB

---
*Document generated on: August 21, 2024*
*Repository state: unified-framework main branch*
*Scope: Complete RH symmetry and Z5D predictor ecosystem*