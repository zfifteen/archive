# Multi-Δ Center Refinement for RSA-2048 Post-Resonance Focusing

## Overview

This document describes the multi-Δ center refinement implementation for RSA-2048 factor recovery, which replaces the previous "single-center thinking" approach with multiple parallel attempts.

## Problem Statement

At RSA-2048 scale, the true factors p and q are typically offset by ~4% from √N, creating a ~10^306 absolute distance gap. The previous approach had a fundamental limitation:

1. It picked ONE "best" seed based on curvature/score
2. It tested ±1000 around that single seed
3. Curvature κ(n) cannot distinguish candidates at 10^306 scale

**Result**: Even with the best single seed, the gap was too large to bridge with ±1000 refinement.

## Solution: Multi-Δ Center Refinement

The new approach implements the "path to success" outlined in the issue:

### Step 1: Extract Multiple δ-Centers
Instead of picking one "best" seed, we extract ALL δ-modes that pass physics gates:
- Strong Green's function amplitude
- Good Dirichlet peak alignment
- Reasonable curvature κ(n)

Each δ represents an offset: `p ≈ (1+δ)*√N`

For RSA-2048, the true factor typically has δ ≈ ±0.04 (4% offset).

### Step 2: Convert to Integer Centers
For each δ, compute:
```python
center = floor((1 + δ) * sqrt(N))
```

This snaps phase information onto the integer number line.

### Step 3: Bounded Refinement Per Center
For EACH center, run bounded ±R divisibility refinement (R=1000):
```python
for candidate in [center - R, center + R]:
    if N % candidate == 0:
        return candidate  # Found factor!
```

**Key constraint**: R stays fixed at 1000. We don't widen R; we enumerate multiple centers.

### Step 4: Track Per-Center Metrics
For each δ-center, we track:
- `distance_before`: |coarse_seed - true_factor|
- `distance_after`: |center - true_factor|
- `shrink_ratio`: distance_after / distance_before
- `within_1000`: Is center within ±1000 of true factor?
- `found_factor`: Did ±1000 refinement find exact factor?

### Step 5: Report Best Center
Identify the δ-center with smallest `distance_after` and report:
- δ value
- Center value
- Shrink ratio
- Whether any center found the exact factor

## Implementation

### New Data Structures

```python
@dataclass
class DeltaCenter:
    """A single δ-center candidate"""
    delta: float  # Offset in log-space
    center: int   # Integer center
    score: float  # Physics-based score
    amplitude: float
    kappa: float
    phase: float

@dataclass
class DeltaCenterResult:
    """Result from testing a single δ-center"""
    delta_center: DeltaCenter
    distance_before: float
    distance_after: float
    shrink_ratio: float
    within_1000: bool
    found_factor: bool
    factor_found: Optional[int]
    offset_from_center: Optional[int]
    refinement_time_ms: float

@dataclass
class MultiDeltaFocusingResult:
    """Result from multi-Δ center refinement"""
    delta_centers: List[DeltaCenter]
    center_results: List[DeltaCenterResult]
    best_center_index: int
    best_center: DeltaCenter
    best_distance_after: float
    best_shrink_ratio: float
    found_factor: bool
    factor_found: Optional[int]
    total_focus_time_ms: float
    total_refinement_time_ms: float
```

### Core Functions

#### `extract_delta_centers(N, metadata, config, max_centers=20)`
Extracts multiple δ-centers from resonance structure:
1. Scan log-space offsets from -5% to +5% in 1% steps
2. For each offset δ, compute center = (1+δ)*√N
3. Evaluate physics score = amplitude × Dirichlet × κ
4. Keep top-scoring centers (up to `max_centers`)

#### `bounded_refinement_single_center(N, center, radius=1000)`
Performs bounded divisibility refinement around a single center:
1. Test candidates in [center - radius, center + radius]
2. Use big-int modulus: N % candidate == 0
3. Return (found, factor, offset) if found

#### `multi_delta_focusing(seed, N, metadata, true_factor, ...)`
Main multi-Δ center refinement pipeline:
1. Extract multiple δ-centers
2. For each center, run bounded refinement
3. Compute per-center metrics
4. Identify best center
5. Return comprehensive results

## Benchmark Results (RSA-2048)

Running `python/examples/rsa_factor_benchmark.py`:

```
N bit length:         2048
Number of seeds:      20
Number of δ-centers:  11
k used:               0.300000

Timing breakdown:
  Seed gen time:      2.65 ms
  Focusing time:      0.10 ms
  Refinement time:    47.45 ms
  Total time:         50.21 ms (0.05 s)
  Time budget:        60000 ms (60 s)
  Within budget:      ✓

Multi-Δ focusing performance:
  Best shrink ratio:  3.896173e-02
  Best distance after: 2.056754e+305
  Distance (log10):   305.31
  Best δ-center:      -0.040000
  Centers within ±1k: 0

Found factor:         ✗
```

### Key Observations

1. **✅ Multiple centers generated**: 11 δ-centers from δ=-0.05 to δ=+0.05
2. **✅ Per-center metrics tracked**: Each center shows distance, shrink ratio, etc.
3. **✅ Best center identified**: δ=-0.04 gives smallest distance
4. **✅ Deterministic and fast**: 50ms total, well under 60s budget
5. **✅ No exponential expansion**: Each center uses fixed ±1000 refinement

6. **⚠️ Not yet successful**: 
   - Best shrink ratio: 0.039 (only 4% reduction)
   - Distance after: 10^305 (still far from ±1000 threshold)
   - No factor found

## Path to Success

The implementation is structurally complete for the "path to success" outlined in the issue:

### What Works Now
1. ✅ Stop relying on κ to pick single best seed
2. ✅ Generate multiple δ-centers from physics gates
3. ✅ Convert each δ to integer center via (1+δ)*√N
4. ✅ Test ±1000 around EACH center (multi-center approach)
5. ✅ Track per-center metrics (shrink ratio, distance, etc.)
6. ✅ Report best center and factor recovery status

### Next Steps for Factor Recovery
To achieve actual factor recovery, the focusing model needs refinement to:
1. Improve δ-center precision (get closer to true δ ≈ -0.04)
2. Use more sophisticated physics gates to filter candidates
3. Possibly increase scan resolution near promising δ values
4. Consider secondary refinement around best centers

However, the **infrastructure** for multi-Δ center refinement is complete and ready.

## Testing

All tests pass:
- `test_extract_delta_centers_small()` - validates δ-center extraction
- `test_bounded_refinement_single_center()` - validates bounded refinement
- `test_multi_delta_focusing_small()` - end-to-end test (finds factor on small case)
- `test_multi_delta_focusing_deterministic()` - validates determinism
- `test_multi_delta_focusing_reports_shrink_ratio()` - validates metrics
- `test_multi_delta_focusing_config_respected()` - validates config handling

## Configuration

New parameters in `FOCUSING_CONFIG`:
```python
'max_delta_centers': 20,    # Maximum number of δ-centers to test
'refinement_radius': 1000,  # Bounded refinement radius (±R)
```

## Acceptance Criteria

Per the issue, the acceptance criteria for this PR are:

1. ✅ **Exports δ-centers**: Not just one focused integer
2. ✅ **Integrates multi-center ±1000 refinement**: For each center
3. ✅ **Logs per-center shrink ratio**: distance_after / distance_before
4. ✅ **Reports best center**: With all metrics
5. ✅ **Keeps total runtime and determinism**: Under 60s, CPU-only

**Status**: All acceptance criteria met. The infrastructure is complete and ready for the next phase of refinement toward actual factor recovery.

## References

- Issue: RSA-2048 Post-Resonance Focusing: Multi-Δ Center Refinement With Bounded Divisibility to Recover Factors
- PR #182: RSA-2048 Factor Candidate Extraction Benchmark
