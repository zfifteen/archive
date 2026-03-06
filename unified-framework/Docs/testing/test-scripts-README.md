# Test Finding Scripts

This directory contains all test execution scripts, analysis tools, validation runners, and experimental code for the unified framework.

## Contents

### Test Scripts
- Individual component test files (test_*.py)
- Integration test suites
- Validation scripts for mathematical proofs

### Analysis Scripts  
- Data analysis and processing tools
- Statistical validation scripts
- Cross-correlation analysis tools
- Spectral form factor analysis

### Run Scripts
- Full analysis execution scripts
- Large-scale computation runners
- Automated test harnesses

## Usage

Scripts in this directory can be executed directly with Python:
```bash
python3 test-finding/scripts/[script_name].py
```

For scripts requiring the core framework, ensure PYTHONPATH is set:
```bash
export PYTHONPATH=/home/runner/work/unified-framework/unified-framework
python3 test-finding/scripts/[script_name].py
```

## LLM Integration Notes

- All scripts are self-contained with clear purposes
- Dependencies are documented within each script
- Results are output to ../results/ directory
- Cross-references updated throughout repository