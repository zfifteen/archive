# BioPython Compatibility Guide

This document outlines BioPython compatibility requirements and validation procedures for the Z Framework unified-framework repository.

## Supported Versions

### Python Compatibility
- **Recommended**: Python 3.8 - Python 3.12
- **Minimum**: Python 3.8
- **Note**: Python 3.13+ may have compatibility issues with BioPython due to deprecated C API functions

### BioPython Compatibility
- **Recommended**: BioPython 1.85
- **Minimum**: BioPython 1.83
- **Version Constraint**: `biopython>=1.83,<2.0`

## Installation

Install BioPython with the recommended version constraint:

```bash
pip install 'biopython>=1.83,<2.0'
```

Or install all dependencies from requirements.txt:

```bash
pip install -r requirements.txt
```

## Validation

### Quick Compatibility Check

Run the BioPython compatibility validation script:

```bash
python3 scripts/validate_biopython_compatibility.py
```

This script validates:
- Python and BioPython version compatibility
- Basic BioPython functionality (Seq, SeqIO, SeqFeature, Entrez)
- Z Framework integration with BioPython components
- Sample data file parsing

### Manual Testing

Test basic BioPython functionality:

```python
from Bio.Seq import Seq
from Bio import SeqIO
from Bio.SeqFeature import FeatureLocation

# Test sequence operations
seq = Seq("ATGCGATCG")
print(f"Sequence: {seq}")
print(f"Complement: {seq.complement()}")
print(f"Reverse complement: {seq.reverse_complement()}")

# Test file parsing
from io import StringIO
fasta_data = '>test\nATGCGATCG\n'
records = list(SeqIO.parse(StringIO(fasta_data), 'fasta'))
print(f"Parsed {len(records)} records")

# Test feature locations
location = FeatureLocation(10, 50, strand=1)
print(f"Feature location: {location}")
```

## Framework Integration

### BioPython Usage in Z Framework

The following Z Framework components use BioPython:

1. **ZGeodesicHotspotMapper** (`src/Bio/QuantumTopology/geodesic_hotspot_mapper.py`)
   - Uses `Bio.Seq` for sequence handling
   - Uses `Bio.SeqIO` for FASTA file parsing
   - Integrates with Z-invariant coordinate computation

2. **Wave-CRISPR Signal Analysis** (`src/applications/wave-crispr-signal-2.py`)
   - Uses `Bio.Entrez` for sequence database access
   - Uses `Bio.SeqFeature.FeatureLocation` for feature annotation

3. **Quantum Topology Modules** (`src/Bio/QuantumTopology/`)
   - Alignment and helical coordinate generation
   - Sequence analysis and visualization

### Testing Framework Components

Test the geodesic hotspot mapper with BioPython:

```python
from src.Bio.QuantumTopology.geodesic_hotspot_mapper import ZGeodesicHotspotMapper
from Bio.Seq import Seq

# Initialize mapper
mapper = ZGeodesicHotspotMapper()

# Test with sequence
test_seq = Seq("ATGCGATCGATCGTAGCGATCGTAGCGATCG")
coordinates = mapper.compute_z_invariant_coordinates(test_seq)
hotspots = mapper.detect_prime_hotspots(coordinates)

print(f"Processed sequence of length {len(test_seq)}")
print(f"Found {hotspots['total_hotspots']} hotspots")
```

## Troubleshooting

### Common Issues

1. **BioPython Import Errors**
   ```
   ModuleNotFoundError: No module named 'Bio'
   ```
   **Solution**: Install BioPython: `pip install 'biopython>=1.83,<2.0'`

2. **Python 3.13+ Compatibility Issues**
   ```
   Error: PyEval_CallObject not found
   ```
   **Solution**: Use Python 3.8-3.12 for better compatibility

3. **Version Conflicts**
   ```
   AttributeError: 'Seq' object has no attribute 'complement'
   ```
   **Solution**: Update to BioPython 1.83+ which has the current API

### Validation Failures

If `scripts/validate_biopython_compatibility.py` reports failures:

1. Check Python version compatibility
2. Verify BioPython installation and version
3. Test basic functionality manually
4. Check for system-specific compilation issues

## CI/CD Integration

### GitHub Actions Configuration

Add BioPython compatibility checks to your CI pipeline:

```yaml
name: BioPython Compatibility Check

on: [push, pull_request]

jobs:
  biopython-compatibility:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ['3.8', '3.9', '3.10', '3.11', '3.12']
    
    steps:
    - uses: actions/checkout@v4
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
    
    - name: Run BioPython compatibility validation
      run: python3 scripts/validate_biopython_compatibility.py
```

### Local Pre-commit Hook

Add to `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: local
    hooks:
      - id: biopython-compatibility
        name: BioPython Compatibility Check
        entry: python3 scripts/validate_biopython_compatibility.py
        language: system
        pass_filenames: false
```

## Updates and Maintenance

### Updating BioPython

When updating BioPython versions:

1. Update the version constraint in `requirements.txt`
2. Run the compatibility validation script
3. Test all framework components that use BioPython
4. Update this documentation with any version-specific notes

### Monitoring Compatibility

- Regularly test with new Python releases
- Monitor BioPython release notes for breaking changes
- Update validation scripts as needed

## API Reference

### Compatibility Validation Script

The `scripts/validate_biopython_compatibility.py` script provides:

- **Python version checks**: Validates Python version compatibility
- **BioPython version checks**: Ensures BioPython version meets requirements
- **Functionality tests**: Tests basic BioPython operations
- **Integration tests**: Validates Z Framework integration
- **Sample data tests**: Tests with existing project data files
- **Recommendations**: Provides actionable guidance for issues

### Return Codes

- `0`: All compatibility checks passed
- `1`: Compatibility issues detected (see output for details)

## Support

For BioPython-related issues:

1. Check this compatibility guide
2. Run the validation script for diagnostics
3. Review BioPython documentation: https://biopython.org/
4. Check Z Framework-specific integration in `src/Bio/QuantumTopology/`

## Version History

- **2025-01**: Initial compatibility guide and validation script
  - Added BioPython 1.83+ requirement
  - Created comprehensive validation framework
  - Documented Python 3.13+ compatibility considerations