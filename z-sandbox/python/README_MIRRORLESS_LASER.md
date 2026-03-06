# Mirrorless Laser Simulation - Quick Start Guide

This is a quick reference for using the mirrorless laser simulation module. For comprehensive documentation, see [docs/MIRRORLESS_LASER_SIMULATION.md](../docs/MIRRORLESS_LASER_SIMULATION.md).

## Installation

```bash
# Install QuTiP and dependencies
pip install qutip numpy scipy matplotlib

# Or use requirements.txt
pip install -r python/requirements.txt
```

## Minimal Example

```python
from mirrorless_laser import MirrorlessLaserSimulator, MirrorlessLaserConfig
import numpy as np

# Configure 4-atom chain with partial pumping
config = MirrorlessLaserConfig(N=4, pump_rate=2.0, eta=0.15)
simulator = MirrorlessLaserSimulator(config)

# Simulate dynamics
tlist = np.linspace(0, 10, 200)
total_exc, intensity, result = simulator.simulate(tlist)

print(f"Peak intensity: {np.max(intensity):.3f}")
```

## RQMC Ensemble

```python
# Run RQMC ensemble for variance reduction
results = simulator.rqmc_ensemble_simulation(
    tlist,
    num_samples=16,
    alpha=0.5,              # Coherence parameter
    use_laguerre=True       # Laguerre-optimized weights
)

print(f"Variance: {np.mean(results['norm_var_intensity'][50:]):.1%}")
```

## Demonstrations

```bash
# Run comprehensive demo (4 demonstrations)
PYTHONPATH=python python3 python/examples/mirrorless_laser_demo.py

# Run basic module demo
PYTHONPATH=python python3 python/mirrorless_laser.py

# Run tests (20 tests)
PYTHONPATH=python python3 tests/test_mirrorless_laser.py
```

## Key Features

- ✅ **QuTiP Integration**: Full master equation solver
- ✅ **RQMC Sampling**: Variance reduction ~3.5% (target <10%)
- ✅ **Anisotropic Corrections**: 7-24% from z-sandbox
- ✅ **Laguerre Basis**: Optimized sampling weights
- ✅ **20 Tests**: All passing with comprehensive coverage

## Z-Sandbox Tools Used

| Tool | Application |
|------|-------------|
| `perturbation_theory.py` | Anisotropic lattice corrections |
| `rqmc_control.py` | Scrambled Sobol' sampling |
| `low_discrepancy.py` | Low-discrepancy sequences |
| Laguerre basis | Mode decomposition & weights |

## Configuration Options

```python
config = MirrorlessLaserConfig(
    N=4,                      # Number of atoms
    omega=0.0,                # Transition frequency
    gamma=1.0,                # Decay rate
    r0=0.1,                   # Spacing (λ/(2π) units)
    pump_rate=2.0,            # Pumping rate
    pumped_indices=[1, 2],    # Atoms to pump
    eta=0.15,                 # Anisotropic parameter
    use_anisotropic=True,     # Enable corrections
    use_laguerre_weights=True # Enable optimization
)
```

## Typical Results

**4-atom chain, partial pumping**:
- Peak intensity: ~2.3
- Steady-state excitation: ~2.0
- RQMC variance: ~3.5%
- Buildup time: ~1.16 / γ

## Documentation

- [Complete Guide](../docs/MIRRORLESS_LASER_SIMULATION.md) - Full API reference (15k words)
- [Module Source](mirrorless_laser.py) - Core implementation (450+ lines)
- [Demo](examples/mirrorless_laser_demo.py) - 4 comprehensive demonstrations
- [Tests](../tests/test_mirrorless_laser.py) - 20 tests, all passing

## Applications

- Quantum sensors
- On-chip nanophotonics
- Superradiance research
- Open quantum systems

## Support

For issues or questions:
1. Check [MIRRORLESS_LASER_SIMULATION.md](../docs/MIRRORLESS_LASER_SIMULATION.md)
2. Run tests: `PYTHONPATH=python python3 tests/test_mirrorless_laser.py`
3. Run demo: `PYTHONPATH=python python3 python/examples/mirrorless_laser_demo.py`

---

*Part of z-sandbox framework - MIT License*
