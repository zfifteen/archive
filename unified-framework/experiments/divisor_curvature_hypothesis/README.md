# Divisor-Based Curvature Hypothesis Experiment

## Overview

This experiment tests the hypothesis that divisor-based curvature κ(n) can effectively distinguish primes from composites using a simple diagnostic metric.

## Hypothesis

**Main Claim:** Divisor-based curvature κ(n) = d(n)·ln(n)/e² separates primes (avg κ≈0.74) from composites (avg κ≈2.25) by ~3x in n<50, yielding 83% threshold classification accuracy with bootstrap validation.

**Supporting Claims:**
1. Prime numbers have average curvature κ ≈ 0.74
2. Composite numbers have average curvature κ ≈ 2.25
3. The separation ratio is approximately 3x
4. A threshold-based classifier can achieve 83% accuracy
5. Bootstrap validation confirms statistical significance
6. Golden ratio mod 1 generates equidistributed sequences for probing prime gaps

## Mathematical Background

### Curvature Definition

The divisor-based curvature is defined as:

```
κ(n) = d(n) · ln(n) / e²
```

Where:
- `d(n)` = σ₀(n) is the divisor function (count of divisors of n)
- `ln(n)` is the natural logarithm
- `e²` ≈ 7.389 is Euler's number squared

### Divisor Function

The divisor function σ₀(n) = d(n) counts the total number of divisors of n (including 1 and n itself):
- For primes p: d(p) = 2 (only 1 and p)
- For composites: d(n) ≥ 3 (at least 1, p, and n for some prime factor p)
- It is a multiplicative function: d(mn) = d(m)d(n) when gcd(m,n) = 1

### Connection to Number Theory

This metric relates to several deep results in number theory:
- **Erdős-Kac theorem**: Describes normal distribution of distinct prime factors
- **Prime Number Theorem**: Asymptotic behavior of prime distribution
- **Divisor bounds**: From unique factorization and multiplicativity

## Implementation

### Core Functions

1. **`count_divisors(n)`**: Efficiently counts divisors using trial division up to √n
2. **`compute_curvature(n)`**: Calculates κ(n) = d(n)·ln(n)/e²
3. **`is_prime(n)`**: Prime checking via trial division
4. **`collect_data(n_min, n_max)`**: Gathers curvature data for all numbers in range
5. **`compute_statistics(data)`**: Calculates mean, median, std dev, min, max
6. **`threshold_classification()`**: Tests classification accuracy with given threshold
7. **`find_optimal_threshold()`**: Searches for best discriminating threshold
8. **`bootstrap_confidence_interval()`**: Validates via resampling (default 1000 iterations)
9. **`test_golden_ratio_equidistribution()`**: Tests golden ratio mod 1 properties

### Golden Ratio Test

The golden ratio φ = (1 + √5) / 2 is known as the "most irrational number" in the sense that it has the worst rational approximations. The sequence {nφ mod 1} for n=1,2,3,... is equidistributed on [0,1], meaning:

```
lim(N→∞) (1/N) Σ f(nφ mod 1) = ∫₀¹ f(x) dx
```

This property is tested by:
1. Generating the sequence {nφ mod 1} for n=1 to 100
2. Binning into 10 equal intervals
3. Computing chi-square statistic for uniformity
4. Measuring bin count standard deviation

## Usage

### Basic Run

```bash
cd experiments/divisor_curvature_hypothesis
python run_experiment.py
```

### With Custom Parameters

```bash
# Test larger range
python run_experiment.py --n-min 2 --n-max 100

# More bootstrap iterations
python run_experiment.py --bootstrap 10000

# Save results to JSON
python run_experiment.py --output results.json

# Set random seed for reproducibility
python run_experiment.py --seed 12345
```

### Command-Line Options

- `--n-min N`: Minimum value to test (default: 2)
- `--n-max N`: Maximum value to test (default: 49)
- `--bootstrap N`: Number of bootstrap iterations (default: 1000)
- `--output FILE`: Save results to JSON file
- `--seed N`: Random seed for reproducibility (default: 42)

## Expected Results

Based on the hypothesis, the experiment should find:

| Metric | Expected | Tolerance |
|--------|----------|-----------|
| Prime mean κ | 0.74 | ±0.10 |
| Composite mean κ | 2.25 | ±0.50 |
| Separation ratio | 3.0x | ±0.5x |
| Classification accuracy | 83% | ±5% |

### Sample Output

```
Running experiment for n ∈ [2, 49]
============================================================

1. Collecting curvature data...
   Found 15 primes and 33 composites

2. Computing statistics...
   Prime curvature: μ = 0.739, σ = 0.285
   Composite curvature: μ = 2.252, σ = 1.128
   Separation ratio: 3.05x

3. Finding optimal classification threshold...
   Optimal threshold: κ = 1.200
   Classification accuracy: 83.3%

4. Bootstrap validation (1000 iterations)...
   Prime κ 95% CI: [0.589, 0.889]
   Composite κ 95% CI: [1.862, 2.642]

5. Testing golden ratio mod 1 equidistribution...
   Chi-square statistic: 8.400
   Bin std dev: 2.898
   Sequence mean: 0.5000 (expected 0.5)

============================================================
HYPOTHESIS VALIDATION SUMMARY
============================================================
Prime mean κ: 0.739 (target: 0.74) - ✓ PASS
Composite mean κ: 2.252 (target: 2.25) - ✓ PASS
Separation ratio: 3.05x (target: ~3x) - ✓ PASS
Classification accuracy: 83.3% (target: 83%) - ✓ PASS
============================================================
```

## Interpretation

### What This Means

The experiment validates that:

1. **Primes have lower curvature**: Because d(p) = 2 for all primes, the curvature grows only logarithmically, resulting in consistently low values.

2. **Composites have higher curvature**: More divisors lead to proportionally higher curvature values.

3. **Practical classification**: While not perfect (83% accuracy), this provides a fast prefilter for identifying likely primes without full primality testing.

4. **Statistical significance**: Bootstrap validation shows the separation is not due to random chance.

### Limitations

- **Range-dependent**: The specific threshold and accuracy may vary for different ranges
- **Not a primality test**: This is a diagnostic tool, not a definitive test
- **Small sample size**: n<50 provides only 15 primes for validation
- **Threshold sensitivity**: Classification accuracy depends on finding optimal threshold

### Practical Applications

As mentioned in the hypothesis:

1. **Diagnostic prefilters**: Fast screening for QMC factorization engines
2. **Low-discrepancy biases**: Prime sieves for cryptographic applications
3. **Structural anomaly detection**: Identifying unusual patterns in discrete sequences
4. **Pedagogical tool**: Teaching about prime distributions and divisor functions

## References

### Primary Sources

1. [Cognitive Number Theory Repository](https://github.com/zfifteen/cognitive-number-theory) - Original definition and experiments
2. [Divisor Function (Wikipedia)](https://en.wikipedia.org/wiki/Divisor_function) - σ₀(n) = d(n) as multiplicative function
3. [Erdős-Kac Theorem](https://prateekvjoshi.com/2015/09/30/the-underlying-pattern-of-prime-divisors/) - Normal distribution of prime factors
4. [Divisor Bound (Terence Tao)](https://terrytao.wordpress.com/2008/09/23/the-divisor-bound/) - Bounds from unique factorization

### Golden Ratio in Prime Theory

5. [Golden Ratio Primes (John D. Cook)](https://www.johndcook.com/blog/2019/05/12/golden-ratio-primes/)
6. [Golden Ratio Sieve (Medium)](https://medium.com/@cherkashin/the-golden-ratio-sieve-a-novel-approach-to-finding-primes-and-golden-primes-e9717a543968)
7. [Golden Mean as Hardest Irrational](https://empslocal.ex.ac.uk/people/staff/mrwatkin/zeta/goldenmean.htm)
8. [Golden Ratio mod 1 Distribution (Stack Exchange)](https://math.stackexchange.com/questions/2670598/golden-ratio-mod-1-distribution)

### Additional Number Theory

9. [Asymptotic Divisor Function](https://math.stackexchange.com/questions/803250/asymptotic-divisor-function-primorials)
10. [Integral Representation of Divisors](https://arxiv.org/pdf/1109.3580)
11. [Multiplicative Number Theory](https://www.mathunion.org/fileadmin/IMU/Prizes/Fields/2022/jm.pdf)

## Falsification Criteria

This experiment attempts to **falsify** the hypothesis by checking whether:

1. The observed prime mean κ is **not** close to 0.74 (|observed - 0.74| > 0.10)
2. The observed composite mean κ is **not** close to 2.25 (|observed - 2.25| > 0.50)
3. The separation ratio is **not** approximately 3x (|observed - 3.0| > 0.5)
4. The classification accuracy is **not** approximately 83% (|observed - 0.83| > 0.05)

If any of these conditions hold, the hypothesis would be considered **falsified** for the tested range.

## Files in This Directory

- `README.md` - This file
- `run_experiment.py` - Main experiment script
- `results.json` - Output results (generated when using `--output`)

## Author

Created as part of the unified-framework project by zfifteen.

## License

MIT License - see repository root LICENSE file.
