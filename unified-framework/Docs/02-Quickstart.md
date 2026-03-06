# Quickstart

## Installation

```bash
git clone https://github.com/zfifteen/unified-framework
cd unified-framework
pip install -r requirements.txt
```

## Run Canonical Benchmark

Execute the standard φ-rotation mapping benchmark:

```bash
python scripts/run_canonical_benchmark.py
```

**Benchmark Parameters:**
- N = 1,000,000 integers
- B = 20 bins  
- k* = 0.3 (optimal curvature)
- 10,000 bootstrap resamples
- Fixed seed = 42

## Run nth-Prime Benchmark

Test Z_5D enhanced predictor performance:

```bash
python scripts/validate_z5d_performance.py
```

## Output Locations

- **Results**: `data/output/results/`
- **Logs**: `data/output/logs/`
- **Visualizations**: `data/output/visualizations/`
- **CSV reports**: `data/output/results/*.csv`

## Quick Validation

Verify installation with basic tests:

```bash
python tests/simple_test.py
python -m pytest tests/test_tc_inst_01_geodesic_validation.py -v
```