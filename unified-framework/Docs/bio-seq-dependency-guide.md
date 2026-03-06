# Bio.Seq Dependency Guide

## Understanding Bio.Seq Import Errors

If you encounter errors like:
```
ModuleNotFoundError: No module named 'Bio'
```
or
```
ImportError: No module named 'Bio.Seq'
```

**Do NOT** try to install a package called `seq`. The solution is to install `biopython`.

## Correct Installation

The `Bio.Seq` module comes from the **biopython** package, not a separate "seq" package.

### Install biopython:
```bash
pip install biopython
```

### Or if using the project requirements:
```bash
pip install -r requirements.txt
```

## Understanding the Import

When you see code like:
```python
from Bio.Seq import Seq
```

This imports the `Seq` class from the `Bio.Seq` module, which is part of the **biopython** library.

## Common Confusion

❌ **Incorrect**: `pip install seq` (this package doesn't exist)
✅ **Correct**: `pip install biopython`

## Testing Your Installation

After installing biopython, test that it works:

```python
from Bio.Seq import Seq

# Create a DNA sequence
dna_seq = Seq("ATGCGATCGATC")
print(f"DNA sequence: {dna_seq}")
print(f"Length: {len(dna_seq)}")
```

## Framework Usage with Bio.Seq

The Z Framework's biological sequence analysis modules use Bio.Seq for:
- DNA/RNA sequence handling
- Protein sequence analysis  
- Quantum-inspired sequence alignment
- Helical coordinate generation

### Example:
```python
from Bio.Seq import Seq
from src.Bio.QuantumTopology import generate_helical_coordinates, quantum_alignment

# Analyze DNA sequences
seq1 = Seq("ATGCGATCGATC")
seq2 = Seq("ATGCGATCGATC")

# Generate helical coordinates using Z Framework
coords = generate_helical_coordinates(seq1)

# Perform quantum-inspired alignment
alignment = quantum_alignment(seq1, seq2)
print(f"Alignment score: {alignment['alignment_score']}")
```

## Troubleshooting

### Version Requirements
- Minimum biopython version: 1.83
- Compatible with Python 3.8+

### Alternative Installation Methods
```bash
# Using conda
conda install -c conda-forge biopython

# Using pip with specific version
pip install biopython>=1.83
```

### Import Error Handling

The framework includes graceful error handling that will show clear messages if biopython is missing:

```python
try:
    from Bio.Seq import Seq
except ImportError:
    print("Bio.Seq requires biopython package. Install with: pip install biopython")
```

## Related Packages

The Z Framework uses these related dependencies for biological analysis:
- **biopython**: Biological sequence handling (`Bio.Seq`, `Bio.SeqIO`)
- **numpy**: Numerical computations
- **scipy**: Scientific computing
- **matplotlib**: Visualization
- **plotly**: Interactive visualizations (optional)

## Support

If you continue to have issues after installing biopython:
1. Check your Python environment
2. Verify biopython version: `pip show biopython`
3. Test import in a fresh Python session
4. Check for conflicting package installations