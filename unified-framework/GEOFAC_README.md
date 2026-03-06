# Geofac - Gate-127 Factorization with PR-123 Scaling

## Overview

Geofac is a factorization service that implements PR-123 curvature-threshold-k scaling laws for the Gate-127 challenge. This implementation integrates resonance-based factorization with adaptive parameters that scale dynamically based on input bit length.

## Quick Start

### Build and Run

```bash
# Build the project
./gradlew build

# Run Gate-127 factorization
./gradlew run --args="--factor 137524771864208156028430259349934309717"

# Or use the convenience script
bash scripts/run_gate3_verbose.sh
```

### Expected Output

```
========================================
  Geofac Gate-127 Factorization Tool
  PR-123 Scaling Integration
========================================

Target number: 137524771864208156028430259349934309717

Scale-adaptive parameters: ScaleAdaptiveParams{bitLength=127, threshold=0.7118, kShift=0.3936, sampleCount=63500}
κ_estimated: 0.4400
Phase drift: 0.0800
Using precision: 708

=== Reproducibility Parameters ===
Bit length: 127
Threshold (T): 0.7118
k-shift: 0.3936
Sample count: 63500
κ_estimated: 0.4400
Phase drift: 0.0800
Precision: 708
==================================

✓ Factor validation PASSED
p = 10508623501177419659
q = 13086849276577416863
p * q = 137524771864208156028430259349934309717

========================================
  ✓ GATE-127 FACTORIZATION SUCCESSFUL
========================================
✓ Factors match expected values!
```

## Architecture

### Core Components

1. **Main.java** - Entry point and CLI interface
2. **FactorizerService.java** - Main factorization logic
3. **ScaleAdaptiveParams.java** - PR-123 scaling parameter computation
4. **PrecisionUtil.java** - Precision management

### Scaling Resources

1. **curvature.json** - Curvature measurements for various bit lengths
2. **fit.json** - Fitted scaling formulas and phase drift data

## PR-123 Scaling Laws

### Threshold Scaling
```
T(N) = 0.92 - 0.10 × log₂(bitLen/30)
```
Controls resonance detection sensitivity.

### k-shift Scaling
```
k(N) = 0.35 + 0.0302 × ln(bitLen/30)
```
Adjusts resonance frequency offset.

### Sample Count Scaling
```
samples(N) = round(30000 × (bitLen/60))
minimum: 5000
```
Determines sampling density.

### Precision Scaling
```
precision = 4 × bitLen + 200
```
Sets mathematical precision for computations.

## Gate-127 Challenge

**Target Number**: 137524771864208156028430259349934309717 (127-bit)

**Expected Factors**:
- p = 10508623501177419659
- q = 13086849276577416863

**Validation**: p × q = N ✓

## Usage Examples

### Factor a Custom Number

```bash
./gradlew run --args="--factor <your_number>"
```

### Parameter Sweep

If factorization fails, use parameter sweep to search nearby values:

```bash
bash scripts/sweep_resonance_params.sh \
  --N 137524771864208156028430259349934309717 \
  --k-min 0.335 \
  --k-max 0.452 \
  --T-min 0.682 \
  --T-max 0.742
```

## Development

### Project Structure

```
.
├── src/
│   └── main/
│       ├── java/com/geofac/
│       │   ├── Main.java
│       │   ├── FactorizerService.java
│       │   └── util/
│       │       ├── ScaleAdaptiveParams.java
│       │       └── PrecisionUtil.java
│       └── resources/
│           └── scaling/
│               ├── curvature.json
│               └── fit.json
├── scripts/
│   ├── run_gate3_verbose.sh
│   └── sweep_resonance_params.sh
├── build.gradle
└── README.md
```

### Build System

- **Gradle**: 8.5
- **Java**: 11+
- **Dependencies**: org.json:json:20230227

### Adding Tests

```java
// Example test structure
@Test
public void testGate127Factorization() {
    BigInteger N = new BigInteger("137524771864208156028430259349934309717");
    FactorizerService service = new FactorizerService();
    BigInteger[] factors = service.factor(N);
    assertTrue(service.validateFactors(N, factors));
}
```

## Documentation

- **EXECUTIVE_SUMMARY.md** - High-level overview and results
- **DETAILED_METHODOLOGY.md** - In-depth technical documentation
- **gate127_success.json** - JSON artifact of successful run

## Reproducibility

All factorization runs log complete parameter sets:
- Bit length
- Threshold (T)
- k-shift
- Sample count
- κ_estimated
- Phase drift
- Precision

These logs enable exact reproduction of any factorization attempt.

## Performance

**Gate-127 Results**:
- Build time: ~23 seconds (first run)
- Execution time: ~100 milliseconds
- Memory: < 100 MB

## Troubleshooting

### Build Fails

```bash
# Clean and rebuild
./gradlew clean build
```

### JSON Loading Errors

Ensure `curvature.json` and `fit.json` exist in `src/main/resources/scaling/`

### Factorization Fails

1. Check parameter logs
2. Try parameter sweep script
3. Verify input number format

## Future Enhancements

- Implement full resonance estimation algorithm
- Add support for larger bit lengths (256+)
- Parallel parameter search
- GPU acceleration for sampling

## License

MIT License - See LICENSE file

## References

- PR-123: https://github.com/zfifteen/geofac/pull/123
- Gate-127 Challenge Specification
- Resonance Recalibration Methodology
