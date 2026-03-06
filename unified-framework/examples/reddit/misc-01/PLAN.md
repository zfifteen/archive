# Implementation Plan for Prime Sequence Algorithm (misc_01.md)

## Objective
Implement and validate the algorithm proposed in `examples/reddit/misc-01/misc_01.md` to deterministically reproduce the sequence S = [1, 2, 3, 5, 6, ..., 498], where f(s_n) yields the n-th prime sequentially, with f(s) = next_prime(s - 1).

## Current Issues Identified
1. **Algorithm Mismatch**: The proposed pseudocode generates [1, 3, 5, ...] instead of [1, 2, 3, 5, ...], failing to match s_2 = 2.
2. **Prime Repeat Handling**: The algorithm incorrectly skips s=2 because f(2) = 2 (same as f(1)), but the sequence includes both.
3. **Sequential Guarantee**: Need to ensure f(s_n) = p_n without repeats unless the sequence allows it.
4. **Validation Gap**: No empirical verification of full 133-term match.

## Corrected Algorithm Design

### Core Function f(s)
```python
def next_prime(n):
    """Return smallest prime >= n"""
    if n <= 2:
        return 2
    if n % 2 == 0:
        n += 1
    while True:
        if is_prime(n):
            return n
        n += 2

def f(s):
    """f(s) = next_prime(s - 1)"""
    return next_prime(s - 1)
```

### Sequence Generation Algorithm
1. Initialize: primes_needed = [p_1, p_2, ..., p_133] (first 133 primes)
2. S = [1]  # s_1 = 1, f(1) = 2 = p_1
3. For n in 2 to 133:
   - Find smallest s >= S[-1] such that f(s) == primes_needed[n-1]
   - If multiple s give same prime, include minimal ones to match sequence length
   - Handle cases where f(s) repeats previous primes
4. Special handling for s_2 = 2: Allow f(2) = 2 even if same as f(1)

### Improved Pseudocode
```python
def generate_S_corrected(N=133):
    # Precompute primes
    primes = []
    p = 2
    for i in range(N):
        primes.append(p)
        p = next_prime(p + 1)

    S = [1]  # s_1
    used_primes = set([2])  # Track used primes to avoid duplicates

    for n in range(1, N):
        target_prime = primes[n]
        s = S[-1]

        while True:
            s += 1
            candidate_prime = f(s)
            if candidate_prime == target_prime and candidate_prime not in used_primes:
                S.append(s)
                used_primes.add(candidate_prime)
                break
            elif candidate_prime == target_prime and n == 1:  # Special case for s_2
                S.append(s)
                # Don't add to used_primes to allow repeat
                break

    return S
```

## Implementation Steps

### Phase 1: Core Functions (Day 1)
1. Implement `is_prime(n)` function (trial division, optimized)
2. Implement `next_prime(n)` function
3. Implement `f(s)` = next_prime(s - 1)
4. Precompute first 133 primes list

### Phase 2: Algorithm Development (Day 2)
1. Create `generate_S_corrected()` function
2. Handle special cases (s_2 = 2, prime repeats)
3. Test with first 10 terms against expected S
4. Debug mismatches and refine logic

### Phase 3: Full Validation (Day 3)
1. Run for N=133 and compare with provided S
2. Verify f(s_n) == p_n for all n
3. Check gap analysis matches Z-formula results
4. Performance optimization (should run in <1s)

### Phase 4: Analysis & Extensions (Day 4)
1. Z-formula validation of generated gaps
2. Statistical analysis of sequence properties
3. Explore pattern recognition in S
4. Document findings and limitations

## Validation Plan

### Unit Tests
- Test f(s) for s=1,2,3,5,6,8,9,...
- Verify primes list correctness
- Check edge cases (s=1, prime repeats)

### Integration Tests
- Generate S for N=10, 50, 133
- Compare with expected sequences
- Validate f(s_n) mappings

### Z-Analysis Validation
- Compute gaps g_k = s_{k+1} - s_k
- Calculate Z_k = g_k × (Δg_k / max_gap)
- Compare with documented Z values

### Performance Benchmarks
- Time for N=133 generation
- Memory usage for prime computations
- Scalability to N=1000+

## Tools & Dependencies
- **Language**: Python 3.8+
- **Libraries**:
  - `sympy` or custom `is_prime` for primality testing
  - `numpy` for statistical analysis
  - `matplotlib` for Z-formula plotting
- **Testing**: `pytest` for unit/integration tests

## Risk Assessment
- **High Risk**: Algorithm may still not match S exactly; may need pattern recognition approach
- **Medium Risk**: Performance issues with large N; optimize prime generation
- **Low Risk**: Z-validation implementation; straightforward once S is generated

## Success Criteria
- ✅ 100% match with provided S sequence
- ✅ f(s_n) = p_n for all n=1 to 133
- ✅ Z-analysis matches documented patterns
- ✅ Runtime < 5 seconds for full generation
- ✅ Clear documentation of algorithm logic

## Timeline
- **Week 1**: Implementation and debugging
- **Week 2**: Validation and analysis
- **Week 3**: Extensions and documentation

## Expected Outcomes
1. Working algorithm reproducing S deterministically
2. Insights into prime sequence patterns
3. Validated Z-formula applications
4. Foundation for further prime pattern research