# Z Framework: Mathematical Research Repository

The Z Framework is a unified mathematical model bridging physical and discrete domains through the empirical invariance of the speed of light. It leverages the universal form Z = A(B/c) to analyze prime number distributions using geometric constraints and curvature-based geodesics.

Always reference these instructions first and fallback to search or bash commands only when you encounter unexpected information that does not match the info here.

## Working Effectively

### Environment Setup and Dependencies
- Install Python dependencies:
  - `pip3 install numpy pandas matplotlib mpmath sympy scikit-learn statsmodels scipy seaborn plotly`
  - Takes: ~45-50 seconds. NEVER CANCEL. Set timeout to 300+ seconds.
- Set Python path for imports (required when working outside repository root):
  - `export PYTHONPATH=/home/runner/work/unified-framework/unified-framework`
  - OR prefix commands: `PYTHONPATH=/home/runner/work/unified-framework/unified-framework python3 script.py`
  - **Note**: PYTHONPATH is only required when working from directories other than the repository root

### Core Mathematical Computations
- Test basic framework:
  - `python3 -c "from core.axioms import universal_invariance; print('Test:', universal_invariance(1.0, 3e8))"`
  - Takes: ~0.1 seconds
- Test discrete zeta shift computations:
  - `python3 -c "from core.domain import DiscreteZetaShift; dz = DiscreteZetaShift(10); print('Works')"`
  - Takes: ~1.1 seconds (includes high-precision mpmath initialization)

### Key Computational Scripts
- Run prime curvature proof analysis:
  - `python3 number-theory/prime-curve/proof.py`
  - Takes: ~2 seconds. NEVER CANCEL. Set timeout to 30+ seconds.
  - Computes optimal curvature exponent k* ≈ 0.3 with conditional prime density improvement under canonical benchmark methodology (CI [14.6%, 15.4%])
- Run hologram visualizations:
  - `python3 number-theory/prime-curve/hologram.py`
  - Takes: ~1.3 seconds
- Run golden curve analysis:
  - `PYTHONPATH=/home/runner/work/unified-framework/unified-framework python3 experiments/lab/golden-curve/brute_force.py`
  - Takes: ~0.8 seconds. Tests Bell inequality violation in prime distributions.
- Run comprehensive data generation:
  - `PYTHONPATH=/home/runner/work/unified-framework/unified-framework python3 test-finding/scripts/test.py`
  - Takes: ~143 seconds (2 minutes 23 seconds). NEVER CANCEL. Set timeout to 1800+ seconds (30+ minutes) for larger datasets.

### Performance Scaling
- 100 DiscreteZetaShift instances: ~0.01 seconds
- 1000 DiscreteZetaShift instances with full computation: ~2 seconds
- Large-scale analysis (test-finding/scripts/test.py): ~143 seconds (2 minutes 23 seconds)
- Prime hologram bootstrap (1000 primes): ~0.3 seconds

## Repository Structure

### Core Framework (/core/)
- `axioms.py` - Universal invariance functions, curvature calculations, golden ratio transformations
- `domain.py` - DiscreteZetaShift class with 5D helical embeddings and zeta shift computations
- `orbital.py` - Orbital mechanics and geometric projections

### Applications (/applications/)
- `vortex_filter.py` - Vortex filtering system
- `wave-crispr-signal.py` and `wave-crispr-signal-2.py` - CRISPR signal analysis tools
- `z_embeddings_csv.py` - Z framework CSV embedding utilities
- `Prime Density Curve/` - Prime density curve analysis tools
- Various visualization and encryption tools

### Research Experiments (/experiments/)
- `test.py` - Main comprehensive test suite (143 seconds runtime)
- `/lab/golden-curve/` - Golden ratio curvature analysis
- `/lab/light_primes/` - Prime hologram and density analysis
- `/lab/universal_frame_shift_transformer/` - Frame shift computations
- `/lab/wave-crispr-signal/` - Spectral analysis tools

### Number Theory (/number-theory/)
- `/prime-curve/` - Prime curvature analysis and proof scripts
- `/prime-number-geometry/` - Geometric prime analysis tools

## Validation Scenarios

Always test these core mathematical scenarios after making changes:

### Basic Framework Validation
- Test universal invariance calculation: `from core.axioms import universal_invariance; assert abs(universal_invariance(1.0, 3e8) - 3.33e-09) < 1e-10`
- Test DiscreteZetaShift instantiation: Create instances for n=1 to 100 and verify no exceptions
- Verify high-precision computations work: Check mpmath precision is set to 50 decimal places

### Mathematical Correctness Validation
- Run prime curvature proof: Verify k* ≈ 0.3 and enhancement = 15% (CI [14.6%, 15.4%])
- Test golden ratio transformations: Verify φ ≈ 1.618 calculations
- Validate Mersenne prime generation in proof.py output
- Test Bell inequality violation: Run golden-curve/brute_force.py and verify quantum entanglement detection

### Computational Performance Validation
- Benchmark DiscreteZetaShift: 1000 instances should complete in <3 seconds
- Test visualization generation: hologram.py should complete in <2 seconds
- Verify memory usage remains reasonable for large computations
- Test comprehensive analysis: test-finding/scripts/test.py should complete in ~143 seconds

### Critical Timing Requirements
- **NEVER CANCEL** long-running scripts: test-finding/scripts/test.py can take up to 143 seconds
- **ALWAYS** set appropriate timeouts: 30+ seconds for proof.py, 1800+ seconds for test-finding/scripts/test.py
- Dependency installation takes ~45-50 seconds and should never be cancelled

## Common Tasks and Timing

### Repository Navigation
```bash
# View repository structure
ls -la  # Shows main directories and documentation
find . -name "*.py" | head -20  # Browse Python scripts
cat README.md  # Comprehensive framework documentation (13.9KB)
```

### Python Syntax and Environment Verification
- Check all Python files compile: `find . -name "*.py" -exec python3 -m py_compile {} \;`
- Verify high precision: `python3 -c "import mpmath as mp; mp.mp.dps = 50; print('Precision:', mp.mp.dps)"`
- Test golden ratio: `python3 -c "import mpmath as mp; mp.mp.dps = 50; phi = (1 + mp.sqrt(5)) / 2; print('φ ≈', float(phi))"`

### Essential Computational Workflows
- **Always** set PYTHONPATH before running scripts: `export PYTHONPATH=/home/runner/work/unified-framework/unified-framework`
- **Always** use high precision for mathematical computations: `mp.mp.dps = 50`
- **Always** allow sufficient timeout for zeta computations (test-finding/scripts/test.py: 1800+ seconds)
- **Never** cancel dependency installation or long mathematical computations

### Documentation Files
- `README.md` - Complete framework description with mathematical foundations
- `MATH.md` - Mathematical detail and theory  
- `PROOFS.md` - Formal mathematical proofs
- `NEXT.md` - Future research directions
- `LICENSE` - MIT license

### Mathematical Computation Patterns
- Core computations use mpmath with 50 decimal precision
- Golden ratio φ = (1 + √5)/2 ≈ 1.618 is central to many calculations
- Optimal curvature parameter k* ≈ 0.3 from empirical validation (August 2025)
- Prime density enhancement of ~495% is achieved at optimal k*

### Known Dependencies and Limitations
- No traditional build system (pure Python research repository)
- No formal test suite beyond test-finding/scripts/test.py
- No GitHub Actions workflows or CI/CD pipeline
- Requires PYTHONPATH setup for core module imports
- Some scripts require command-line arguments (use --help to check)
- Visualization scripts use matplotlib with 'Agg' backend for headless environments
- High precision arithmetic (mpmath) requires sufficient timeout for large computations
- Zeta zero computations can take several minutes depending on dataset size

## Validation Requirements

### Before Making Changes
- Run basic framework test: `python3 -c "from core.axioms import *; from core.domain import *; print('Core imports successful')"`
- Verify mathematical constants: Check φ, e², and high precision settings

### After Making Changes  
- Run proof validation: `python3 number-theory/prime-curve/proof.py` (should show k* ≈ 0.3)
- Test visualization: `python3 number-theory/prime-curve/hologram.py` (should complete without errors)
- Validate core computations: Test DiscreteZetaShift with known values
- Check computation scaling: Verify 1000 instances complete in reasonable time

### Performance Monitoring
- Monitor memory usage during large computations
- Verify timing remains consistent with baseline measurements
- Check that high-precision arithmetic doesn't cause performance degradation

## Quick Reference

### Common File Locations
- Main proof script: `number-theory/prime-curve/proof.py`
- Core mathematical functions: `core/axioms.py`
- Primary computation class: `core/domain.py`
- Comprehensive test: `test-finding/scripts/test.py`
- Visualization tools: `number-theory/prime-curve/hologram.py`

### Key Mathematical Constants
- Golden ratio φ ≈ 1.618034
- Optimal curvature k* ≈ 0.3 (from empirical validation)
- Max prime enhancement = 495.2% (at optimal k*)
- Speed of light c (used as universal invariant)
- Euler's constant e (e² normalization factor)

### Repository Statistics
- 126 Python files
- 65 documentation files  
- ~72MB repository size
- Mathematical research focus (not software application)

## Troubleshooting

### Import Errors
- **"ModuleNotFoundError: No module named 'core'"**: Set PYTHONPATH or run from repository root
- **"ModuleNotFoundError: No module named 'numpy'"**: Install dependencies with pip3

### Performance Issues
- **Scripts taking too long**: Ensure adequate timeout (test-finding/scripts/test.py needs 1800+ seconds)
- **Memory errors**: High precision arithmetic requires sufficient memory for large datasets
- **Precision errors**: Verify mpmath.mp.dps is set to 50 decimal places

### Common Mistakes
- **Never cancel** long-running mathematical computations
- **Always use** appropriate timeouts for zeta computations
- **Always run** from repository root or set PYTHONPATH properly
- **Always verify** dependencies are installed before running scripts