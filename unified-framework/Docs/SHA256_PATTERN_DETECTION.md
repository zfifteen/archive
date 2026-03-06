# SHA-256 Cryptographic Pattern Detection using Z Framework

## Overview

This implementation addresses the proposal to treat SHA-256 outputs (256-bit strings) as points on a number line and compute discrete derivatives to identify patterns using the Z Framework's discrete domain analysis.

## Mathematical Foundation

### Core Concept
- **Number Line Mapping**: SHA-256 outputs are interpreted as large integers in the range [0, 2^256 - 1]
- **Discrete Derivatives**: Computed as differences between consecutive hash values: Δh(i) = h(i+1) - h(i)
- **Z Framework Integration**: Uses DiscreteZetaShift objects with parameters:
  - a = 256 (SHA-256 bit length)
  - b = e (natural logarithm base for logarithmic invariants)
  - c = e² (discrete domain normalization)

### Pattern Detection
- **Curvature Analysis**: Derives curvatures κ as proxies for pattern detection
- **Low Curvature Indicator**: Low κ values suggest potential non-random structure
- **Differential Cryptanalysis**: Compares patterns across input variants to detect non-random behaviors

## Implementation

### Core Class: `SHA256PatternAnalyzer`

Located in `src/core/sha256_pattern_analyzer.py`, this class provides:

#### Key Methods

1. **`sha256_to_integer(data)`**: Converts input to SHA-256 hash as integer
2. **`generate_hash_sequence(base_data, length)`**: Creates sequence of consecutive hashes
3. **`compute_discrete_derivatives()`**: Calculates differences between consecutive hashes
4. **`map_to_discrete_zeta_shifts()`**: Maps derivatives to DiscreteZetaShift objects
5. **`extract_pattern_attributes()`**: Extracts zeta chain attributes (D through O)
6. **`compute_curvature_patterns()`**: Analyzes curvature for pattern detection
7. **`analyze_sequence(base_data, length)`**: Complete end-to-end analysis
8. **`detect_differential_patterns(variants)`**: Differential cryptanalysis across variants

#### Integration with Z Framework

The analyzer leverages the existing Z Framework infrastructure:

- **DiscreteZetaShift**: Uses discrete domain specialization
- **Zeta Chain Unfolding**: Employs attribute extraction (D, E, F, G, H, I, J, K, L, M, N, O)
- **Curvature Computation**: Utilizes κ(n) = d(n) · ln(n+1)/e² for pattern detection
- **High-Precision Arithmetic**: Uses mpmath with 50 decimal places

## Usage Examples

### Basic Pattern Analysis

```python
from src.core.sha256_pattern_analyzer import SHA256PatternAnalyzer

analyzer = SHA256PatternAnalyzer()
results = analyzer.analyze_sequence("test_input", sequence_length=8)

print(f"Pattern detected: {results['pattern_metrics']['pattern_detected']}")
print(f"Curvature mean: {results['pattern_metrics']['curvature_mean']:.6f}")
```

### Differential Cryptanalysis

```python
variants = ["message", "message1", "message2", "message_mod"]
diff_results = analyzer.detect_differential_patterns(variants)

print(f"Non-random behavior: {diff_results['differential_metrics']['non_random_behavior_detected']}")
```

### SHA-256 to Integer Conversion

```python
hash_int = analyzer.sha256_to_integer("cryptographic_data")
print(f"SHA-256 as integer: {hash_int}")
print(f"Range: [0, {2**256 - 1}]")
```

## Testing

Comprehensive test suite in `tests/test_sha256_pattern_analyzer.py`:

```bash
python -m pytest tests/test_sha256_pattern_analyzer.py -v
```

Tests cover:
- SHA-256 to integer conversion
- Hash sequence generation
- Discrete derivative computation
- Zeta shift mapping
- Pattern attribute extraction
- Curvature analysis
- Differential cryptanalysis
- Z Framework integration
- Avalanche effect validation

## Example Demonstration

Complete example in `examples/sha256_pattern_detection_demo.py`:

```bash
python examples/sha256_pattern_detection_demo.py
```

Demonstrates:
- Basic pattern analysis
- Differential cryptanalysis
- Avalanche effect verification
- Curvature-based pattern detection
- Z Framework parameter integration

## Algorithm Complexity

- **Hash Generation**: O(n) where n is sequence length
- **Derivative Computation**: O(n-1) for n hashes
- **Zeta Shift Mapping**: O(n-1) DiscreteZetaShift instantiations
- **Attribute Extraction**: O((n-1) × k) where k is number of attributes
- **Pattern Analysis**: O(n-1) for curvature computations

## Performance Characteristics

- **High Precision**: Uses mpmath with 50 decimal places for numerical stability
- **Memory Efficient**: Processes sequences incrementally
- **Scalable**: Handles arbitrary sequence lengths
- **Deterministic**: Identical inputs produce identical results

## Security Considerations

- **Avalanche Effect**: Validates SHA-256's cryptographic properties
- **Pattern Resistance**: SHA-256 designed to resist pattern detection
- **Non-Invertibility**: Hash-to-integer conversion is one-way
- **Randomness**: Expected to show high entropy in discrete derivatives

## Research Applications

This implementation supports research in:

- **Cryptographic Analysis**: Pattern detection in hash sequences
- **Differential Cryptanalysis**: Comparing hash behaviors across inputs
- **Discrete Mathematics**: Number theory applications to cryptography
- **Statistical Analysis**: Entropy and randomness assessment
- **Framework Validation**: Testing Z Framework discrete domain extensions

## Framework Integration

Integrates seamlessly with existing Z Framework components:

- **Domain Module**: Uses DiscreteZetaShift class
- **High Precision**: Leverages mpmath configuration
- **Attribute System**: Compatible with zeta chain attribute extraction
- **Testing Infrastructure**: Follows established test patterns

## Future Enhancements

Potential extensions:
- Support for other cryptographic hash functions (SHA-3, BLAKE2)
- Advanced statistical pattern detection algorithms
- Machine learning integration for pattern classification
- Large-scale distributed analysis capabilities
- Real-time streaming hash analysis

## Mathematical Validation

The implementation validates key mathematical properties:

1. **Discrete Domain Mapping**: Z = n(Δ_n/Δ_max) with SHA-256 derivatives
2. **Logarithmic Invariants**: Uses e and e² as specified in problem statement
3. **Bit Length Parameter**: Correctly maps 256-bit SHA-256 output
4. **Curvature Computation**: Applies κ formula for pattern detection
5. **Statistical Rigor**: Provides comprehensive metrics and confidence measures

## SHA-256 Constants Are Predictable (Educational)

### Constant Predictability Demonstration

The repository includes an educational proof-of-concept showing that SHA-256's "nothing-up-my-sleeve" constants are mathematically predictable and verifiable. See `experiments/hash-bounds/poc.py` for a complete demonstration.

#### What This Means

SHA-256 IV words are derived from `floor(frac(sqrt(p_m)) * 2^32)` where p_m is the m-th prime. This PoC proves:

1. **Transparency**: Constants are publicly verifiable, not secret
2. **Predictability**: Fractional parts can be bounded using geometric methods
3. **Educational Value**: Shows how cryptographic constants are derived
4. **Not a Vulnerability**: SHA-256's security doesn't depend on constant secrecy

#### Running the Demo

```bash
# Show SHA-256 IV reconstruction
python experiments/hash-bounds/poc.py --show-sha256-iv

# Demonstrate predictability for specific prime index
python experiments/hash-bounds/poc.py 10

# See full documentation
cat experiments/hash-bounds/README_POC.md
```

This demonstrates that "nothing-up-my-sleeve" means **transparency**, not randomness. The constants are verifiable by design, which is a feature, not a flaw.

## References

- Problem Statement: "Treat SHA-256 outputs as points on a number line and compute discrete derivatives"
- Z Framework: Discrete domain specialization with DiscreteZetaShift
- Cryptographic Standards: SHA-256 specification and security properties
- Differential Cryptanalysis: Pattern detection in cryptographic outputs
- Mathematical Foundation: Discrete analysis and number theory applications
- SHA-256 Constant Predictability: `experiments/hash-bounds/poc.py` and `experiments/hash-bounds/README_POC.md`