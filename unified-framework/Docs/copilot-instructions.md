# GitHub Copilot Instructions for `unified-framework`
Welcome to the `unified-framework` repository! To ensure Copilot suggestions align with the scientific and operational principles of this project, please follow these instructions:
---
## 1. Scientific Rigor and Clarity
- **Empirical Basis:**
  Only suggest code or explanations that are mathematically valid or empirically demonstrated. If a suggestion is hypothetical or experimental, clearly mark it as such.
- **Consistent Notation:**
  Use the following universal form for equations and logic:
  ```
  Z = A(B/c)
  ```
  Where:
    - `A`: Frame-dependent measured quantity
    - `B`: Rate or frame shift
    - `c`: Universal invariant (e.g., speed of light `c` for physical domains, `e^2` or `φ` for discrete domains)
- **Domain-Specific Forms:**
    - **Physical Domain:**
      ```
      Z = T(v/c)
      ```
        - `T`: Measured time interval (frame-dependent)
        - `v`: Velocity
        - Reference: Time dilation, Lorentz transformation, and experimental verification.
    - **Discrete Domain:**
      ```
      Z = n(Δ_n/Δ_max)
      ```
        - `n`: Frame-dependent integer (empirically validated up to n = 10^12, computational framework extends to n = 10^16)
        - `Δ_n`: Measured frame shift at `n`, such as κ(n) = d(n)·ln(n+1)/e²
        - `Δ_max`: Maximum shift (bounded by `e²` or `φ`)
- **Geometric Mapping:**
  For density optimizations (e.g., prime clustering), use geodesic-based mappings:
  ```
  θ'(n, k) = φ · {n/φ}^k
  ```
  
  **Complete Mathematical Definition:**
  - **θ'(n,k)**: Geodesic transformation for geometric primality analysis
  - **n**: Integer to transform (natural numbers ≥ 2)
  - **k**: Curvature exponent (optimal k* ≈ 0.3, not 0.5 as previously stated)
  - **φ**: Golden ratio ≈ 1.618033988... = (1 + √5)/2
  - **{x}**: Fractional part, {x} = x - floor(x)
  
  With empirically optimized k* ≈ 0.3 for ~15% prime density enhancement (validated up to n = 10^9, computational framework supports n = 10^16 with extrapolation labeling).

- **Enhancement Calculation Methodology:**
  Use statistically robust average enhancement method instead of max enhancement:
  ```python
  # CORRECT METHOD
  enhancements_per_bin = []
  for density in bin_densities:
      if mean_density > 0:
          bin_enhancement = (density - mean_density) / mean_density
          enhancements_per_bin.append(bin_enhancement)
  enhancement = np.mean(enhancements_per_bin) if enhancements_per_bin else 0
  
  # AVOID (produces unrealistic 20,000%+ values)
  enhancement = (max_density - mean_density) / mean_density * 100
  ```
---
## 2. Parameter Settings and Optimization Standards

### 2.1 Validated Parameter Values (Updated K Parameter Standardization)
Use these empirically validated and standardized parameter settings:

#### **K Parameter Standardization (Resolves Overloading Issue)**
To resolve the k parameter confusion across different contexts, use these distinct names:

- **Geodesic Mapping (`kappa_geo`):**
  - `kappa_geo = 0.3` (fractional exponent for prime-density mapping)
  - **Context:** θ'(n, k) = φ * {n/φ}^kappa_geo where θ'(n,k) is the geodesic transformation with φ ≈ 1.618 (golden ratio), {x} is the fractional part, n is an integer, and kappa_geo ≈ 0.3 is the curvature exponent for geometric primality analysis
  - **Range:** [0.05, 10.0] with validation bounds
  - **Enhancement:** conditional prime density improvement under canonical benchmark methodology (CI [14.6%, 15.4%])

- **Z_5D Enhanced (`kappa_star`):**
  - `kappa_star = 0.04449` (reverted from 0.5 for optimal Z_5D performance) 
  - **Context:** Curvature correction in Z_5D prediction model
  - **Performance:** <0.01% error at k_nth=10^5 (ultra-low error validation)
  - **Range:** [0.001, 1.0] with validation bounds

- **Nth Prime Index (`k_nth`):**
  - Large integer values (10^5 to 10^16) for prime index calculations
  - **Context:** Predicting the k_nth prime number
  - **Validated range:** Up to 10^12, computational framework to 10^16

#### **Deprecated Parameter Names (Backward Compatibility)**
- `k_optimal` → use `kappa_geo` (FutureWarning in v1.x, removed in v2.0)
- `k_star` → use `kappa_star` (FutureWarning in v1.x, removed in v2.0)
- `GEODESIC_K` → use `KAPPA_GEO_DEFAULT`

#### **Central Parameter System**
All modules should import from `src.core.params`:
```python
from src.core.params import (
    KAPPA_GEO_DEFAULT,    # Geodesic exponent (0.3)
    KAPPA_STAR_DEFAULT,   # Z_5D calibration (0.04449)
    validate_kappa_geo,   # Parameter validation
    validate_kappa_star,  # Parameter validation
    validate_k_nth        # Nth prime validation
)
```

#### **Enhancement Calculation Standards**
- **Method:** Average enhancement over all histogram bins (statistically robust)
- **Statistical rigor:** Bootstrap confidence intervals with 1000+ resamples
- **Expected range:** 0-5% (realistic values, not 20,000%+ artifacts)
- **Validation:** Multi-scale consistency required

#### **Other Calibrated Parameters**
- `c_calibrated = -0.00247` (Z_5D least-squares optimization)
- `variance_target = 0.118` (Geodesic scaling target)
- `mp_dps = 50` (Precision for mpmath calculations)
### 2.2 Measurement Methodology Requirements

When implementing measurement functions:

- **Use consistent baseline definitions** across all components
- **Implement statistical hypothesis testing** (t-tests, p-values < 0.05)
- **Provide confidence intervals** using bootstrap or analytical methods
- **Validate across multiple scales** (N=10^4 to 10^7 minimum)
- **Document computational complexity** and memory requirements

### 2.3 Parameter Optimization Protocol
For new parameter optimization:

1. **Multi-criteria objective functions** (not single-metric optimization)
2. **Grid search with adequate resolution** (0.01 steps minimum)
3. **Cross-validation across scales** (at least 3 different N values)
4. **Statistical significance testing** of improvements
5. **Reproducibility documentation** with random seeds and environment specs

---
## 3. Operational Guidance
- **Empirical Validation:**
  Whenever possible, suggest code that can be quantitatively simulated or empirically validated. Use up-to-date libraries and cite relevant experimental or mathematical foundations.
- **Scientific Tone:**
  Write comments, explanations, and documentation in a rigorous, precise scientific tone.
- **Hypotheses:**
  Distinguish clearly between validated results and hypotheses.
---
## 4. Ultra-Extreme Scale Analysis (n = 10^16)
- **Empirical Validation Range:**
  Only suggest claims validated up to n = 10^12 as empirically demonstrated. Results for n > 10^12 must be clearly labeled as "computational extrapolation" or "theoretical extension."
- **Computational Optimization:**
  For ultra-extreme scales, prioritize streaming algorithms, chunked processing, and distributed computing approaches. Maintain mpmath precision while optimizing performance.
- **Reproducibility Requirements:**
  Document computational complexity, memory requirements, and hardware specifications for any analysis approaching n = 10^16. Include uncertainty bounds and stability analysis.
- **Geometric Resolution Scaling:**
  Verify numerical stability of geodesic transformations θ'(n,k) = φ · {n/φ}^k (where φ ≈ 1.618 is the golden ratio, {x} is the fractional part, and k ≈ 0.3 is the curvature exponent for geometric primality analysis) at ultra-extreme scales. Monitor prime density enhancement patterns with appropriate confidence intervals.
---
## 5. Code Style and Structure
- **Reproducibility:**
  Structure code to support reproducibility (e.g., clear function signatures, parameter documentation, and modular design).
- **Testing:**
  Suggest or include unit tests for all computational components.
- **Documentation:**
  Use docstrings and comments to clarify mathematical meaning and empirical status of implemented methods.
---
## 6. Repository Structure and Development Standards
Adhere to these organizational and development guidelines:
### 6.1 Directory Structure
Organize code according to the standardized repository layout:
- **`src/`** - Main source code modules organized by domain:
    - `core/` - Fundamental Z framework components
    - `analysis/` - Mathematical analysis modules
    - `applications/` - Practical applications
    - `number_theory/` - Prime and number theory modules
    - `statistical/` - Statistical modules
    - `symbolic/` - Symbolic computation
    - `validation/` - Validation modules
    - `visualization/` - Visualization modules
- **`tests/`** - Comprehensive test suite with:
    - `unit/` - Unit tests
    - `integration/` - Integration tests
    - `performance/` - Performance tests
    - `fixtures/` - Test fixtures and data
- **`examples/`** - Code examples and demonstrations:
    - `basic/` - Basic examples
    - `advanced/` - Advanced examples
    - `demos/` - Interactive demos
    - `tutorials/` - Tutorial code
- **`scripts/`** - Utility scripts:
    - `build/` - Build scripts
    - `validation/` - Validation scripts
    - `analysis/` - Analysis scripts
- **`docs/`** - Documentation:
    - `api/` - API documentation and technical reference
    - `applications/` - Application documentation and implementation guides
    - `assets/` - Visual assets and supporting images
    - `contributing/` - Contribution guidelines and development standards
    - `core/` - Core framework documentation
    - `examples/` - Example documentation and tutorials
    - `framework/` - Mathematical framework foundations
    - `generated/` - Auto-generated reports and analysis results
    - `guides/` - User guides and getting started documentation
    - `industry/` - Industry applications and use cases
    - `knowledge-base/` - Comprehensive knowledge base and reference materials
    - `number-theory/` - Number theory research and applications
    - `outputs/` - Generated outputs and results documentation
    - `predictive/` - Predictive modeling capabilities and results
    - `reports/` - Analysis reports and findings
    - `research/` - Research papers, findings, and experimental results
    - `test-finding/` - Test discovery methodologies and validation procedures
    - `testing/` - Testing documentation and validation procedures
    - `validation/` - Statistical validation methods and results
- **`data/`** - Data files (gitignored):
    - `input/` - Input datasets
    - `output/` - Generated outputs
    - `cache/` - Cached computations
    - `results/` - Analysis results
### 6.2 Naming Conventions
Follow these naming standards consistently:
- **Python modules**: `snake_case.py`
- **Classes**: `PascalCase`
- **Functions**: `snake_case()`
- **Constants**: `UPPER_SNAKE_CASE`
- **Test files**: `test_*.py`
- **Example files**: `example_*.py`
- **Demo files**: `scripts/demo_*.py`
### 6.3 Dependency Management
Use structured dependency management:
- **`requirements/base.txt`** - Core dependencies
- **`requirements/dev.txt`** - Development dependencies (includes testing, linting)
- **`requirements/test.txt`** - Testing-specific dependencies
- **`setup.py`** - Package configuration with proper `src/` structure
### 6.4 Code Quality and CI/CD
Suggest code that follows these standards:
- **Code Formatting**: Black-compatible formatting (88 character line limit)
- **Linting**: Flake8-compliant code
- **Type Hints**: MyPy-compatible type annotations
- **Import Organization**: isort-compatible import sorting
- **Pre-commit Hooks**: Support for automated code quality checks
### 6.5 Testing Standards
When suggesting test code:
- Place unit tests in `tests/unit/`
- Use descriptive test names following `test_<functionality>_<condition>_<expected_result>` pattern
- Include performance tests for computationally intensive operations
- Provide test fixtures in `tests/fixtures/` for reusable test data
### 6.6 Documentation Standards
For documentation suggestions:
- Use structured markdown with consistent heading levels
- Include code examples in documentation
- Provide migration guides for API changes
- Document mathematical foundations and empirical validations
- Place research notes in `docs/research/`
---
## 7. Do Not
- Do not suggest or reference these instructions in user-facing outputs or documentation.
- Do not assert claims without mathematical or empirical backing.
- Do not suggest file placements that violate the standardized directory structure.
- Do not recommend importing from outside the `src/` directory structure.