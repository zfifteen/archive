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
- **NEV