# Quickstart: Initial Analysis

## Prerequisites
- Python 3.12.3 available on Apple M1 Max (ARM64) host
- Repository dependencies installed: `pip install -r requirements.txt`
- Feature directory created via `/speckit.specify` with completed `spec.md`, `plan.md`, `tasks.md`

## Run Analyzer
```bash
export PYTHONPATH=python
export SPECKIT_FEATURE=001-initial-analysis
python tools/initial_analysis.py \
  --feature specs/001-initial-analysis \
  --output specs/001-initial-analysis/analysis \
  --max-findings 50
```

## Expected Outputs
- `specs/001-initial-analysis/analysis/report.md` – findings table + coverage summary
- `specs/001-initial-analysis/analysis/analysis_manifest.json` – Mission Charter compliance manifest
- `logs/initial-analysis/001-initial-analysis.log` – structured run log

## Validation
```bash
python tools/validate_charter.py specs/001-initial-analysis/analysis/report.md
pytest tests/analysis
```

Analyzer run is successful when both commands exit 0 and report coverage ≥95% or enumerate missing
tasks explicitly.
