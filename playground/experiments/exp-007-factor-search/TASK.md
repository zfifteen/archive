# Implementation Intent

This tool exists to provide **evidentiary transparency** for skeptical experts. The target user is a Prime Number Theorem researcher who has encountered claims about "geometric resonance" and "asymmetric enrichment" in factorization search spaces and demands to see the raw distributional data before taking such claims seriously. The tool must therefore prioritize **exposing the phenomenon over abstracting it**—every design decision should favor outputting more data, not less; showing intermediate computations, not hiding them; and enabling independent verification, not requiring trust. This is explicitly *not* a factorization utility; it does not need to find factors efficiently or compete with existing algorithms. Its sole purpose is to generate candidate score distributions, mark where true factors fall within those distributions, compute the KS statistic rejecting uniformity, and output everything in formats that researchers can feed into their own analysis pipelines. If an implementation choice arises between "more performant but opaque" versus "slower but auditable," choose auditable. The success metric is whether a skeptical number theorist, upon reviewing the CSV output and recomputing the KS statistic independently, reaches the same p < 10⁻¹⁰ conclusion and observes factors clustering in high-score regions—not whether the tool runs fast or looks polished.

# Z5D Distribution Asymmetry Visualizer

## Technical Specification v1.0

***

## 1. Overview

### 1.1 Purpose

A C99 command-line tool that generates candidate score distributions for user-supplied semiprimes, computes the Kolmogorov-Smirnov statistic against uniform distribution, and outputs data files suitable for visualization. The tool demonstrates the validated non-uniform factor density phenomenon by exposing raw distributional data for independent analysis.

### 1.2 Core Deliverables

- Candidate score distribution data (CSV)
- KS test results with p-value computation
- Optional SVG histogram output
- Factor location markers within distribution
- Comparative baseline (uniform random) distribution

### 1.3 Target Users

Number theory researchers, cryptographers, and PNT specialists seeking to independently verify asymmetric enrichment claims through distributional analysis.

***

## 2. Dependencies

| Library | Version | Purpose | Required |
|---------|---------|---------|----------|
| GMP | ≥6.2.0 | Arbitrary-precision arithmetic for 10²⁰–10⁴⁰ range | Yes |
| libc | C99 | Standard library (math, stdio, stdlib) | Yes |
| POSIX | — | `getopt_long` for argument parsing | Optional¹ |

¹ Provide fallback short-option parsing for strict C99 compliance.

***

## 3. Architecture

### 3.1 Module Structure

```
z5d_visualizer/
├── Makefile
├── README.md
├── include/
│   ├── z5d_score.h        # Z5D geometric scoring interface
│   ├── qmc_sequence.h     # Quasi-Monte Carlo generators
│   ├── ks_test.h          # Kolmogorov-Smirnov implementation
│   ├── csv_writer.h       # CSV output formatting
│   ├── svg_writer.h       # SVG histogram generation
│   └── semiprime.h        # Semiprime validation/factorization
├── src/
│   ├── main.c             # Entry point, argument parsing
│   ├── z5d_score.c        # Z5D scoring implementation
│   ├── qmc_sequence.c     # Sobol/Halton sequence generators
│   ├── ks_test.c          # KS statistic and p-value
│   ├── csv_writer.c       # CSV output
│   ├── svg_writer.c       # SVG output
│   └── semiprime.c        # Primality testing, validation
└── test/
    ├── test_z5d.c         # Unit tests for scoring
    ├── test_ks.c          # Unit tests for KS computation
    └── known_vectors.h    # Test vectors with known factors
```

### 3.2 Data Flow

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│   Input     │────▶│   Candidate  │────▶│   Z5D       │
│   Semiprime │     │   Generator  │     │   Scorer    │
│   N = p×q   │     │   (QMC)      │     │             │
└─────────────┘     └──────────────┘     └──────┬──────┘
                                                │
                    ┌──────────────┐            │
                    │   Baseline   │            │
                    │   Generator  │────────────┤
                    │   (Uniform)  │            │
                    └──────────────┘            │
                                                ▼
                                         ┌─────────────┐
                                         │   Score     │
                                         │   Collector │
                                         └──────┬──────┘
                                                │
              ┌─────────────────────────────────┼─────────────────────┐
              │                                 │                     │
              ▼                                 ▼                     ▼
       ┌─────────────┐                   ┌─────────────┐       ┌─────────────┐
       │   KS Test   │                   │   CSV       │       │   SVG       │
       │   Engine    │                   │   Writer    │       │   Writer    │
       └─────────────┘                   └─────────────┘       └─────────────┘
```

***

## 4. Data Structures

### 4.1 Core Types

```c
/* include/semiprime.h */

typedef struct {
    mpz_t N;              /* Semiprime value */
    mpz_t p;              /* Smaller factor (0 if unknown) */
    mpz_t q;              /* Larger factor (0 if unknown) */
    unsigned int bits;    /* Bit length of N */
    int factors_known;    /* Boolean: factors provided */
} semiprime_t;

void semiprime_init(semiprime_t *sp);
void semiprime_clear(semiprime_t *sp);
int semiprime_set_str(semiprime_t *sp, const char *n_str, 
                      const char *p_str, const char *q_str);
int semiprime_validate(const semiprime_t *sp);
```

```c
/* include/z5d_score.h */

typedef struct {
    double coords[5];     /* 5D geometric coordinates */
} z5d_point_t;

typedef struct {
    mpz_t candidate;      /* Candidate factor value */
    double score;         /* Z5D score (signed) */
    double normalized;    /* Score normalized to [0,1] */
    z5d_point_t geometry; /* 5D embedding coordinates */
} scored_candidate_t;

typedef struct {
    scored_candidate_t *candidates;
    size_t count;
    size_t capacity;
    double score_min;
    double score_max;
    double score_mean;
    double score_variance;
} score_distribution_t;

void score_dist_init(score_distribution_t *dist, size_t initial_capacity);
void score_dist_clear(score_distribution_t *dist);
void score_dist_append(score_distribution_t *dist, const scored_candidate_t *sc);
void score_dist_compute_stats(score_distribution_t *dist);
```

```c
/* include/ks_test.h */

typedef struct {
    double d_statistic;   /* KS D statistic (supremum distance) */
    double p_value;       /* Two-sided p-value */
    size_t n_samples;     /* Sample count */
    double critical_001;  /* Critical value at α=0.001 */
    double critical_01;   /* Critical value at α=0.01 */
    double critical_05;   /* Critical value at α=0.05 */
    int reject_uniform;   /* Boolean: reject H₀ at α=0.05 */
} ks_result_t;

ks_result_t ks_test_uniform(const double *samples, size_t n);
ks_result_t ks_test_two_sample(const double *sample_a, size_t n_a,
                               const double *sample_b, size_t n_b);
```

### 4.2 Configuration Structure

```c
/* include/config.h */

typedef enum {
    QMC_SOBOL,
    QMC_HALTON,
    QMC_HYBRID
} qmc_strategy_t;

typedef enum {
    OUTPUT_CSV,
    OUTPUT_SVG,
    OUTPUT_BOTH
} output_format_t;

typedef struct {
    /* Input */
    char *semiprime_str;
    char *factor_p_str;       /* Optional: known factor p */
    char *factor_q_str;       /* Optional: known factor q */
    
    /* Sampling */
    size_t num_candidates;    /* Candidates to generate (default: 10000) */
    qmc_strategy_t qmc_type;  /* QMC sequence type */
    unsigned long seed;       /* RNG seed for baseline */
    
    /* Output */
    output_format_t format;
    char *output_prefix;      /* Output filename prefix */
    int include_baseline;     /* Generate uniform baseline comparison */
    int verbose;              /* Verbose terminal output */
    
    /* Histogram */
    size_t histogram_bins;    /* Bin count for histogram (default: 50) */
    int svg_width;            /* SVG canvas width (default: 800) */
    int svg_height;           /* SVG canvas height (default: 400) */
} config_t;

config_t config_defaults(void);
int config_parse_args(config_t *cfg, int argc, char **argv);
void config_cleanup(config_t *cfg);
```

***

## 5. Algorithm Specifications

### 5.1 Z5D Geometric Scoring

The Z5D scoring function maps candidate factors into a 5-dimensional geometric space and computes alignment with factor-predictive resonance patterns.

```c
/* src/z5d_score.c */

/*
 * z5d_embed - Map candidate factor to 5D geometric coordinates
 *
 * The embedding extracts five geometric features from the relationship
 * between candidate c and semiprime N:
 *
 *   dim[0]: Normalized position (c / √N)
 *   dim[1]: Residue phase (2π × (N mod c) / c)
 *   dim[2]: Digit sum ratio (digit_sum(c) / digit_sum(N))
 *   dim[3]: Bit density differential (popcount(c)/bits(c) - popcount(N)/bits(N))
 *   dim[4]: Coprimality signal (log(gcd(c-1, N-1)) / log(N))
 *
 * Parameters:
 *   point   - Output 5D coordinate structure
 *   c       - Candidate factor (2 ≤ c ≤ √N)
 *   N       - Semiprime being factored
 */
void z5d_embed(z5d_point_t *point, const mpz_t c, const mpz_t N);

/*
 * z5d_score - Compute geometric resonance score for embedded point
 *
 * The score measures alignment between the embedded point and 
 * factor-predictive regions identified through the geometric resonance
 * framework. Higher scores indicate elevated factor probability.
 *
 * Score computation:
 *   1. Compute distance to nearest resonance manifold in 5D space
 *   2. Apply inverse-square weighting
 *   3. Adjust for magnitude-dependent baseline
 *   4. Return signed score (positive = above baseline)
 *
 * Parameters:
 *   point   - 5D embedded coordinates
 *   N       - Semiprime (for magnitude-dependent adjustment)
 *
 * Returns:
 *   Signed double score; positive indicates elevated factor density
 */
double z5d_score(const z5d_point_t *point, const mpz_t N);

/*
 * z5d_score_candidate - Combined embed + score convenience function
 */
void z5d_score_candidate(scored_candidate_t *result, 
                         const mpz_t candidate, 
                         const mpz_t N);
```

### 5.2 Quasi-Monte Carlo Sequence Generation

```c
/* src/qmc_sequence.c */

typedef struct {
    qmc_strategy_t type;
    unsigned int dimension;
    unsigned long index;
    /* Sobol direction numbers */
    unsigned long *sobol_v;
    unsigned long sobol_x;
    /* Halton state */
    unsigned int halton_base;
} qmc_state_t;

/*
 * qmc_init - Initialize QMC generator state
 *
 * Parameters:
 *   state     - Generator state to initialize
 *   type      - Sequence type (Sobol, Halton, Hybrid)
 *   dimension - Coordinate dimension (1 for scalar candidates)
 */
void qmc_init(qmc_state_t *state, qmc_strategy_t type, unsigned int dimension);
void qmc_clear(qmc_state_t *state);

/*
 * qmc_next - Generate next value in [0, 1) interval
 *
 * For candidate generation, this value is scaled to search range:
 *   candidate = 2 + floor(qmc_next() × (√N - 2))
 */
double qmc_next(qmc_state_t *state);

/*
 * qmc_generate_candidate - Generate next candidate factor
 *
 * Maps QMC sequence value to valid candidate range [2, √N]
 * using low-discrepancy distribution.
 *
 * Parameters:
 *   candidate - Output: candidate factor (mpz_t, pre-initialized)
 *   state     - QMC generator state
 *   sqrt_N    - Square root of semiprime (search bound)
 */
void qmc_generate_candidate(mpz_t candidate, qmc_state_t *state, const mpz_t sqrt_N);
```

#### 5.2.1 Sobol Sequence Implementation

```c
/*
 * Sobol sequence using direction numbers from Joe & Kuo (2008)
 * for dimension 1. Provides O(N^-1) discrepancy vs O(N^-0.5) 
 * for pseudorandom sequences.
 */

static const unsigned long SOBOL_DIRECTION_V[32] = {
    0x80000000UL, 0x40000000UL, 0x20000000UL, 0x10000000UL,
    0x08000000UL, 0x04000000UL, 0x02000000UL, 0x01000000UL,
    0x00800000UL, 0x00400000UL, 0x00200000UL, 0x00100000UL,
    0x00080000UL, 0x00040000UL, 0x00020000UL, 0x00010000UL,
    0x00008000UL, 0x00004000UL, 0x00002000UL, 0x00001000UL,
    0x00000800UL, 0x00000400UL, 0x00000200UL, 0x00000100UL,
    0x00000080UL, 0x00000040UL, 0x00000020UL, 0x00000010UL,
    0x00000008UL, 0x00000004UL, 0x00000002UL, 0x00000001UL
};

static unsigned int rightmost_zero_bit(unsigned long n) {
    unsigned int pos = 0;
    while ((n & 1UL) == 1UL) {
        n >>= 1;
        pos++;
    }
    return pos;
}

double sobol_next(qmc_state_t *state) {
    unsigned int c = rightmost_zero_bit(state->index);
    state->sobol_x ^= state->sobol_v[c];
    state->index++;
    return (double)state->sobol_x / (double)0x100000000UL;
}
```

### 5.3 Kolmogorov-Smirnov Test

```c
/* src/ks_test.c */

/*
 * ks_test_uniform - Test sample against uniform U(0,1) distribution
 *
 * Computes the KS D statistic as the supremum distance between
 * empirical CDF and theoretical uniform CDF.
 *
 * Algorithm:
 *   1. Sort samples in ascending order
 *   2. For each sample x_i at rank i:
 *      - F_empirical(x_i) = i / n
 *      - F_uniform(x_i) = x_i
 *      - d_i = |F_empirical - F_uniform|
 *   3. D = max(d_i) over all i
 *   4. Compute p-value using asymptotic distribution
 *
 * Parameters:
 *   samples - Array of values in [0, 1] (will be sorted in-place)
 *   n       - Sample count
 *
 * Returns:
 *   ks_result_t with D statistic, p-value, and rejection decisions
 */
ks_result_t ks_test_uniform(double *samples, size_t n);

/*
 * ks_p_value - Compute p-value from D statistic
 *
 * Uses the asymptotic Kolmogorov distribution:
 *   P(D_n > d) ≈ 2 Σ_{k=1}^∞ (-1)^{k-1} exp(-2k²n d²)
 *
 * For n > 40, this approximation is accurate to <0.001.
 */
static double ks_p_value(double d_stat, size_t n) {
    double sqrt_n = sqrt((double)n);
    double lambda = (sqrt_n + 0.12 + 0.11 / sqrt_n) * d_stat;
    
    double sum = 0.0;
    for (int k = 1; k <= 100; k++) {
        double term = exp(-2.0 * k * k * lambda * lambda);
        if (k % 2 == 0) {
            sum -= term;
        } else {
            sum += term;
        }
        if (term < 1e-15) break;
    }
    return 2.0 * sum;
}
```

### 5.4 Baseline Uniform Generator

```c
/* src/baseline.c */

/*
 * Generate uniformly distributed candidates for comparison.
 * Uses Mersenne Twister (or xorshift128+) seeded for reproducibility.
 */

typedef struct {
    uint64_t state[2];
} xorshift_state_t;

void xorshift_seed(xorshift_state_t *state, unsigned long seed);
uint64_t xorshift_next(xorshift_state_t *state);
double xorshift_uniform(xorshift_state_t *state);

void baseline_generate_candidate(mpz_t candidate, 
                                 xorshift_state_t *state, 
                                 const mpz_t sqrt_N);
```

***

## 6. Output Specifications

### 6.1 CSV Format

**Filename:** `{prefix}_distribution.csv`

```csv
# Z5D Distribution Asymmetry Analysis
# Semiprime: {N}
# Factors: p={p}, q={q}
# Candidates: {count}
# QMC Strategy: {sobol|halton|hybrid}
# Generated: {ISO8601 timestamp}
#
index,candidate,score,normalized_score,dim0,dim1,dim2,dim3,dim4,is_factor
0,314159265358979,0.847,-0.234,0.707,3.141,0.333,0.021,-0.156,0
1,271828182845904,1.203,0.122,0.612,2.718,0.287,0.015,-0.089,0
...
4721,{p},2.891,0.983,0.500,0.000,0.412,0.002,0.847,1
...
```

**Columns:**
| Column | Type | Description |
|--------|------|-------------|
| `index` | int | Candidate sequence number |
| `candidate` | string | Candidate value (decimal string for arbitrary precision) |
| `score` | float | Raw Z5D score (signed) |
| `normalized_score` | float | Score mapped to [1] via min-max normalization |
| `dim0`–`dim4` | float | 5D embedding coordinates |
| `is_factor` | int | 1 if candidate equals p or q, 0 otherwise |

### 6.2 KS Statistics Output

**Filename:** `{prefix}_ks_results.txt`

```
================================================================================
KOLMOGOROV-SMIRNOV UNIFORMITY TEST
================================================================================

Semiprime N:     123456789012345678901234567890123456789012
Bit length:      137
Candidates:      10000
QMC Strategy:    Sobol

--------------------------------------------------------------------------------
ADAPTIVE (Z5D-SCORED) DISTRIBUTION
--------------------------------------------------------------------------------
KS D-statistic:  0.1847
p-value:         8.12e-11
Sample size:     10000

Critical values:
  α = 0.05:      0.0136    REJECT H₀
  α = 0.01:      0.0163    REJECT H₀  
  α = 0.001:     0.0195    REJECT H₀

Interpretation:  Distribution is NON-UNIFORM (p < 1e-10)
                 Probability of observing this by chance: ~1 in 12 billion

--------------------------------------------------------------------------------
BASELINE (UNIFORM RANDOM) DISTRIBUTION  
--------------------------------------------------------------------------------
KS D-statistic:  0.0089
p-value:         0.4127
Sample size:     10000

Critical values:
  α = 0.05:      0.0136    FAIL TO REJECT
  α = 0.01:      0.0163    FAIL TO REJECT
  α = 0.001:     0.0195    FAIL TO REJECT

Interpretation:  Distribution is CONSISTENT WITH UNIFORM

--------------------------------------------------------------------------------
FACTOR LOCATION ANALYSIS
--------------------------------------------------------------------------------
Factor p score:  2.891 (percentile: 98.3)
Factor q score:  2.743 (percentile: 97.1)
Combined rank:   Top 2.4% of candidates

================================================================================
```

### 6.3 SVG Histogram Format

**Filename:** `{prefix}_histogram.svg`

```xml
<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" 
     width="{width}" height="{height}" 
     viewBox="0 0 {width} {height}">
  
  <style>
    .title { font: bold 16px sans-serif; }
    .axis-label { font: 12px sans-serif; }
    .tick-label { font: 10px monospace; }
    .bar-adaptive { fill: #2563eb; opacity: 0.7; }
    .bar-baseline { fill: #9ca3af; opacity: 0.5; }
    .factor-marker { stroke: #dc2626; stroke-width: 2; }
    .legend { font: 11px sans-serif; }
  </style>
  
  <!-- Title -->
  <text x="{width/2}" y="25" class="title" text-anchor="middle">
    Z5D Score Distribution: N = {N_truncated}...
  </text>
  
  <!-- Axes -->
  <line x1="60" y1="{height-40}" x2="{width-20}" y2="{height-40}" 
        stroke="black" stroke-width="1"/>
  <line x1="60" y1="40" x2="60" y2="{height-40}" 
        stroke="black" stroke-width="1"/>
  
  <!-- X-axis label -->
  <text x="{width/2}" y="{height-10}" class="axis-label" text-anchor="middle">
    Normalized Z5D Score
  </text>
  
  <!-- Y-axis label -->
  <text x="15" y="{height/2}" class="axis-label" text-anchor="middle"
        transform="rotate(-90,15,{height/2})">
    Frequency
  </text>
  
  <!-- Histogram bars (adaptive) -->
  <g class="bars-adaptive">
    <!-- Generated programmatically: one rect per bin -->
    <rect x="{bin_x}" y="{bin_y}" width="{bin_width}" height="{bin_height}" 
          class="bar-adaptive"/>
    <!-- ... -->
  </g>
  
  <!-- Histogram bars (baseline) - overlaid with transparency -->
  <g class="bars-baseline">
    <rect x="{bin_x}" y="{bin_y}" width="{bin_width}" height="{bin_height}" 
          class="bar-baseline"/>
    <!-- ... -->
  </g>
  
  <!-- Factor location markers -->
  <line x1="{p_score_x}" y1="40" x2="{p_score_x}" y2="{height-40}" 
        class="factor-marker" stroke-dasharray="5,3"/>
  <line x1="{q_score_x}" y1="40" x2="{q_score_x}" y2="{height-40}" 
        class="factor-marker" stroke-dasharray="5,3"/>
  
  <!-- Factor labels -->
  <text x="{p_score_x}" y="55" class="tick-label" text-anchor="middle" 
        fill="#dc2626">p</text>
  <text x="{q_score_x}" y="55" class="tick-label" text-anchor="middle" 
        fill="#dc2626">q</text>
  
  <!-- Legend -->
  <rect x="{width-150}" y="50" width="12" height="12" class="bar-adaptive"/>
  <text x="{width-133}" y="60" class="legend">Adaptive (Z5D)</text>
  <rect x="{width-150}" y="70" width="12" height="12" class="bar-baseline"/>
  <text x="{width-133}" y="80" class="legend">Baseline (Uniform)</text>
  <line x1="{width-150}" y1="96" x2="{width-138}" y2="96" class="factor-marker"/>
  <text x="{width-133}" y="100" class="legend">True factors</text>
  
  <!-- KS annotation -->
  <text x="80" y="70" class="tick-label">
    KS p-value: {p_value_scientific}
  </text>
  <text x="80" y="85" class="tick-label">
    Enrichment: {enrichment_factor}×
  </text>
  
</svg>
```

***

## 7. Command-Line Interface

### 7.1 Usage

```
z5d_visualizer [OPTIONS] <semiprime>

DESCRIPTION
    Generate Z5D score distribution analysis for semiprime factorization.
    Outputs candidate score distributions and KS uniformity test results.

ARGUMENTS
    <semiprime>         Semiprime N to analyze (decimal string)

OPTIONS
    -p, --factor-p STR  Known factor p (enables factor marking in output)
    -q, --factor-q STR  Known factor q (enables factor marking in output)
    
    -n, --candidates N  Number of candidates to generate [default: 10000]
    -s, --strategy STR  QMC strategy: sobol, halton, hybrid [default: sobol]
    -r, --seed N        Random seed for baseline generator [default: 42]
    
    -o, --output PREFIX Output filename prefix [default: z5d_output]
    -f, --format FMT    Output format: csv, svg, both [default: both]
    -b, --no-baseline   Skip baseline uniform comparison
    
    --bins N            Histogram bin count [default: 50]
    --svg-width N       SVG width in pixels [default: 800]
    --svg-height N      SVG height in pixels [default: 400]
    
    -v, --verbose       Enable verbose progress output
    -h, --help          Display this help message
    --version           Display version information

EXAMPLES
    # Basic analysis with known factors
    z5d_visualizer -p 123456789012347 -q 987654321098767 \
                   121932631137021678369

    # Large semiprime, Halton sequence, CSV only
    z5d_visualizer --strategy halton --format csv --candidates 50000 \
                   -o analysis_10e30 \
                   "123456789012345678901234567890123456789012345678901"

    # Quick verification with reduced sample
    z5d_visualizer -n 1000 --no-baseline -v 15241578750190521
```

### 7.2 Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | Invalid arguments |
| 2 | Invalid semiprime (not composite, or factor mismatch) |
| 3 | Memory allocation failure |
| 4 | File I/O error |
| 5 | Numerical overflow (should not occur with GMP) |

***

## 8. Function Specifications

### 8.1 Main Entry Point

```c
/* src/main.c */

int main(int argc, char **argv) {
    config_t cfg = config_defaults();
    
    /* Parse arguments */
    if (config_parse_args(&cfg, argc, argv) != 0) {
        return EXIT_INVALID_ARGS;
    }
    
    /* Initialize semiprime */
    semiprime_t sp;
    semiprime_init(&sp);
    if (semiprime_set_str(&sp, cfg.semiprime_str, 
                          cfg.factor_p_str, cfg.factor_q_str) != 0) {
        fprintf(stderr, "Error: Invalid semiprime or factors\n");
        return EXIT_INVALID_SEMIPRIME;
    }
    
    /* Validate if factors provided */
    if (sp.factors_known && !semiprime_validate(&sp)) {
        fprintf(stderr, "Error: N ≠ p × q\n");
        return EXIT_INVALID_SEMIPRIME;
    }
    
    /* Generate adaptive distribution */
    score_distribution_t adaptive_dist;
    score_dist_init(&adaptive_dist, cfg.num_candidates);
    generate_adaptive_distribution(&adaptive_dist, &sp, &cfg);
    
    /* Generate baseline distribution (if requested) */
    score_distribution_t baseline_dist;
    if (cfg.include_baseline) {
        score_dist_init(&baseline_dist, cfg.num_candidates);
        generate_baseline_distribution(&baseline_dist, &sp, &cfg);
    }
    
    /* Compute KS statistics */
    ks_result_t adaptive_ks = compute_ks_uniform(&adaptive_dist);
    ks_result_t baseline_ks = {0};
    if (cfg.include_baseline) {
        baseline_ks = compute_ks_uniform(&baseline_dist);
    }
    
    /* Write outputs */
    if (cfg.format == OUTPUT_CSV || cfg.format == OUTPUT_BOTH) {
        write_csv(&adaptive_dist, cfg.include_baseline ? &baseline_dist : NULL,
                  &sp, &cfg);
    }
    if (cfg.format == OUTPUT_SVG || cfg.format == OUTPUT_BOTH) {
        write_svg_histogram(&adaptive_dist, 
                            cfg.include_baseline ? &baseline_dist : NULL,
                            &sp, &adaptive_ks, &cfg);
    }
    write_ks_results(&adaptive_ks, &baseline_ks, &sp, &cfg);
    
    /* Cleanup */
    score_dist_clear(&adaptive_dist);
    if (cfg.include_baseline) {
        score_dist_clear(&baseline_dist);
    }
    semiprime_clear(&sp);
    config_cleanup(&cfg);
    
    return EXIT_SUCCESS;
}
```

### 8.2 Distribution Generation

```c
/* src/generator.c */

/*
 * generate_adaptive_distribution - Generate Z5D-scored candidate distribution
 *
 * Algorithm:
 *   1. Initialize QMC sequence generator
 *   2. Compute √N as search bound
 *   3. For i = 0 to num_candidates-1:
 *      a. Generate candidate c_i via QMC
 *      b. Compute Z5D embedding and score
 *      c. Append to distribution
 *   4. Compute distribution statistics
 *   5. Normalize scores to [0,1]
 *
 * Parameters:
 *   dist    - Output distribution (pre-initialized)
 *   sp      - Semiprime structure
 *   cfg     - Configuration with candidate count and QMC type
 */
void generate_adaptive_distribution(score_distribution_t *dist,
                                    const semiprime_t *sp,
                                    const config_t *cfg) {
    mpz_t sqrt_N, candidate;
    mpz_inits(sqrt_N, candidate, NULL);
    mpz_sqrt(sqrt_N, sp->N);
    
    qmc_state_t qmc;
    qmc_init(&qmc, cfg->qmc_type, 1);
    
    scored_candidate_t sc;
    mpz_init(sc.candidate);
    
    for (size_t i = 0; i < cfg->num_candidates; i++) {
        qmc_generate_candidate(candidate, &qmc, sqrt_N);
        z5d_score_candidate(&sc, candidate, sp->N);
        
        /* Mark if this is a known factor */
        if (sp->factors_known) {
            if (mpz_cmp(candidate, sp->p) == 0 || 
                mpz_cmp(candidate, sp->q) == 0) {
                sc.is_factor = 1;
            }
        }
        
        score_dist_append(dist, &sc);
        
        if (cfg->verbose && (i % 1000 == 0)) {
            fprintf(stderr, "\rGenerating candidates: %zu/%zu", 
                    i, cfg->num_candidates);
        }
    }
    
    if (cfg->verbose) {
        fprintf(stderr, "\rGenerating candidates: %zu/%zu [done]\n",
                cfg->num_candidates, cfg->num_candidates);
    }
    
    score_dist_compute_stats(dist);
    normalize_scores(dist);
    
    mpz_clear(sc.candidate);
    qmc_clear(&qmc);
    mpz_clears(sqrt_N, candidate, NULL);
}
```

### 8.3 SVG Generation

```c
/* src/svg_writer.c */

/*
 * write_svg_histogram - Generate SVG histogram visualization
 *
 * Creates dual-overlay histogram showing adaptive vs baseline distributions
 * with factor location markers and KS statistics annotation.
 */
int write_svg_histogram(const score_distribution_t *adaptive,
                        const score_distribution_t *baseline,
                        const semiprime_t *sp,
                        const ks_result_t *ks,
                        const config_t *cfg) {
    
    char filename[256];
    snprintf(filename, sizeof(filename), "%s_histogram.svg", cfg->output_prefix);
    
    FILE *fp = fopen(filename, "w");
    if (!fp) return -1;
    
    /* Compute histogram bins */
    size_t *adaptive_bins = calloc(cfg->histogram_bins, sizeof(size_t));
    size_t *baseline_bins = baseline ? 
                            calloc(cfg->histogram_bins, sizeof(size_t)) : NULL;
    
    compute_histogram_bins(adaptive_bins, cfg->histogram_bins, adaptive);
    if (baseline) {
        compute_histogram_bins(baseline_bins, cfg->histogram_bins, baseline);
    }
    
    /* Find max bin height for scaling */
    size_t max_bin = 0;
    for (size_t i = 0; i < cfg->histogram_bins; i++) {
        if (adaptive_bins[i] > max_bin) max_bin = adaptive_bins[i];
        if (baseline && baseline_bins[i] > max_bin) max_bin = baseline_bins[i];
    }
    
    /* SVG header */
    fprintf(fp, "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n");
    fprintf(fp, "<svg xmlns=\"http://www.w3.org/2000/svg\" "
                "width=\"%d\" height=\"%d\" viewBox=\"0 0 %d %d\">\n",
            cfg->svg_width, cfg->svg_height, cfg->svg_width, cfg->svg_height);
    
    /* Embedded styles */
    write_svg_styles(fp);
    
    /* Chart area dimensions */
    int margin_left = 60, margin_right = 20;
    int margin_top = 50, margin_bottom = 50;
    int chart_width = cfg->svg_width - margin_left - margin_right;
    int chart_height = cfg->svg_height - margin_top - margin_bottom;
    double bin_width = (double)chart_width / cfg->histogram_bins;
    
    /* Title */
    char title[128];
    format_semiprime_short(title, sizeof(title), sp->N);
    fprintf(fp, "<text x=\"%d\" y=\"25\" class=\"title\" text-anchor=\"middle\">"
                "Z5D Score Distribution: N = %s</text>\n",
            cfg->svg_width / 2, title);
    
    /* Draw axes */
    write_svg_axes(fp, margin_left, margin_top, chart_width, chart_height,
                   cfg->svg_width, cfg->svg_height);
    
    /* Draw baseline bars (if present) */
    if (baseline) {
        fprintf(fp, "<g class=\"bars-baseline\">\n");
        for (size_t i = 0; i < cfg->histogram_bins; i++) {
            double height = (double)baseline_bins[i] / max_bin * chart_height;
            double x = margin_left + i * bin_width;
            double y = margin_top + chart_height - height;
            fprintf(fp, "  <rect x=\"%.1f\" y=\"%.1f\" width=\"%.1f\" "
                        "height=\"%.1f\" class=\"bar-baseline\"/>\n",
                    x, y, bin_width - 1, height);
        }
        fprintf(fp, "</g>\n");
    }
    
    /* Draw adaptive bars */
    fprintf(fp, "<g class=\"bars-adaptive\">\n");
    for (size_t i = 0; i < cfg->histogram_bins; i++) {
        double height = (double)adaptive_bins[i] / max_bin * chart_height;
        double x = margin_left + i * bin_width;
        double y = margin_top + chart_height - height;
        fprintf(fp, "  <rect x=\"%.1f\" y=\"%.1f\" width=\"%.1f\" "
                    "height=\"%.1f\" class=\"bar-adaptive\"/>\n",
                x, y, bin_width - 1, height);
    }
    fprintf(fp, "</g>\n");
    
    /* Draw factor markers (if known) */
    if (sp->factors_known) {
        write_svg_factor_markers(fp, adaptive, sp, 
                                 margin_left, margin_top, 
                                 chart_width, chart_height);
    }
    
    /* Legend and annotations */
    write_svg_legend(fp, baseline != NULL, cfg->svg_width);
    write_svg_ks_annotation(fp, ks, margin_left, margin_top);
    
    /* Close SVG */
    fprintf(fp, "</svg>\n");
    
    fclose(fp);
    free(adaptive_bins);
    if (baseline_bins) free(baseline_bins);
    
    return 0;
}
```

***

## 9. Build System

### 9.1 Makefile

```makefile
# Z5D Distribution Asymmetry Visualizer
# Build configuration for C99 with GMP

CC = gcc
CFLAGS = -std=c99 -Wall -Wextra -Wpedantic -O2
CFLAGS += -Iinclude
LDFLAGS = -lgmp -lm

# Debug build
DEBUG_CFLAGS = -std=c99 -Wall -Wextra -Wpedantic -g -O0 -DDEBUG
DEBUG_CFLAGS += -fsanitize=address,undefined

SRC_DIR = src
INC_DIR = include
BUILD_DIR = build
TEST_DIR = test

SRCS = $(wildcard $(SRC_DIR)/*.c)
OBJS = $(SRCS:$(SRC_DIR)/%.c=$(BUILD_DIR)/%.o)

TARGET = z5d_visualizer

.PHONY: all clean debug test install

all: $(BUILD_DIR) $(TARGET)

$(BUILD_DIR):
	mkdir -p $(BUILD_DIR)

$(TARGET): $(OBJS)
	$(CC) $(CFLAGS) -o $@ $^ $(LDFLAGS)

$(BUILD_DIR)/%.o: $(SRC_DIR)/%.c
	$(CC) $(CFLAGS) -c -o $@ $<

debug: CFLAGS = $(DEBUG_CFLAGS)
debug: clean all

test: $(TARGET)
	$(CC) $(CFLAGS) -o test_runner $(TEST_DIR)/*.c $(SRC_DIR)/z5d_score.c \
		$(SRC_DIR)/ks_test.c $(SRC_DIR)/qmc_sequence.c $(LDFLAGS)
	./test_runner

clean:
	rm -rf $(BUILD_DIR) $(TARGET) test_runner *.csv *.svg *.txt

install: $(TARGET)
	install -m 755 $(TARGET) /usr/local/bin/

# Dependencies (auto-generated would go here)
$(BUILD_DIR)/main.o: $(INC_DIR)/config.h $(INC_DIR)/semiprime.h
$(BUILD_DIR)/z5d_score.o: $(INC_DIR)/z5d_score.h
$(BUILD_DIR)/ks_test.o: $(INC_DIR)/ks_test.h
$(BUILD_DIR)/qmc_sequence.o: $(INC_DIR)/qmc_sequence.h
$(BUILD_DIR)/csv_writer.o: $(INC_DIR)/csv_writer.h
$(BUILD_DIR)/svg_writer.o: $(INC_DIR)/svg_writer.h
```

### 9.2 Build Instructions

```bash
# Install dependencies (Debian/Ubuntu)
sudo apt-get install libgmp-dev

# Install dependencies (macOS)
brew install gmp

# Build release
make

# Build with debug symbols and sanitizers
make debug

# Run tests
make test

# Install to /usr/local/bin
sudo make install
```

***

## 10. Testing Requirements

### 10.1 Unit Test Coverage

| Module | Test Cases |
|--------|------------|
| `z5d_score` | Score polarity consistency, embedding bounds, known-factor scores |
| `qmc_sequence` | Sequence uniformity, deterministic reproducibility, range compliance |
| `ks_test` | Known D-statistics, p-value accuracy, edge cases (n=1, n=10⁶) |
| `csv_writer` | Format compliance, special character escaping, large number formatting |
| `svg_writer` | Valid XML output, viewBox calculation, bin height scaling |
| `semiprime` | Validation logic, GMP string parsing, primality edge cases |

### 10.2 Integration Tests

```c
/* test/test_integration.c */

/*
 * Test: Known semiprime produces expected distribution properties
 *
 * Using semiprime 15241578750190521 = 123456789 × 123456789 (perfect square)
 * and non-square semiprime 143 = 11 × 13
 */
void test_known_semiprime_small(void) {
    /* 143 = 11 × 13 */
    semiprime_t sp;
    semiprime_init(&sp);
    semiprime_set_str(&sp, "143", "11", "13");
    
    config_t cfg = config_defaults();
    cfg.num_candidates = 1000;
    
    score_distribution_t dist;
    score_dist_init(&dist, 1000);
    generate_adaptive_distribution(&dist, &sp, &cfg);
    
    /* Factor scores should be in top quartile */
    double p_score = find_factor_score(&dist, "11");
    double q_score = find_factor_score(&dist, "13");
    
    assert(p_score > dist.score_mean + dist.score_variance);
    assert(q_score > dist.score_mean + dist.score_variance);
    
    score_dist_clear(&dist);
    semiprime_clear(&sp);
}

/*
 * Test: Large semiprime (10^30 range) completes without overflow
 */
void test_large_semiprime_no_overflow(void) {
    semiprime_t sp;
    semiprime_init(&sp);
    semiprime_set_str(&sp, 
        "123456789012345678901234567890123456789012345678901", 
        NULL, NULL);
    
    config_t cfg = config_defaults();
    cfg.num_candidates = 100;  /* Reduced for test speed */
    
    score_distribution_t dist;
    score_dist_init(&dist, 100);
    
    /* Should complete without crash or assertion failure */
    generate_adaptive_distribution(&dist, &sp, &cfg);
    
    assert(dist.count == 100);
    assert(isfinite(dist.score_mean));
    assert(isfinite(dist.score_variance));
    
    score_dist_clear(&dist);
    semiprime_clear(&sp);
}
```

### 10.3 Validation Against Known Results

The test suite must validate that:

1. **KS statistic computation** matches reference implementations (SciPy, R) within ε = 10⁻⁶
2. **QMC sequences** match published reference values for first 1000 terms
3. **Factor scores** consistently rank in top 5% for test corpus of 100 known semiprimes
4. **Output files** pass format validation (CSV parseable, SVG renders correctly)

***

## 11. Performance Targets

| Metric | Target | Measurement |
|--------|--------|-------------|
| Candidate throughput | ≥50,000/sec | 10⁴⁰ magnitude semiprime, single core |
| Memory usage | ≤100 MB | 100,000 candidates stored |
| Startup time | <100 ms | Time to first candidate generation |
| CSV write speed | ≥1 MB/sec | 100,000 candidate output |
| SVG generation | <500 ms | 50-bin histogram with 10,000 samples |

***

## 12. Error Handling

### 12.1 GMP Allocation Failures

```c
/*
 * GMP uses abort() on allocation failure by default.
 * Override with custom handler for graceful degradation.
 */
void *safe_gmp_allocate(size_t size) {
    void *ptr = malloc(size);
    if (!ptr) {
        fprintf(stderr, "Fatal: Memory allocation failed (%zu bytes)\n", size);
        exit(EXIT_MEMORY_ERROR);
    }
    return ptr;
}

void safe_gmp_free(void *ptr, size_t size) {
    (void)size;
    free(ptr);
}

void *safe_gmp_reallocate(void *ptr, size_t old_size, size_t new_size) {
    (void)old_size;
    void *new_ptr = realloc(ptr, new_size);
    if (!new_ptr) {
        fprintf(stderr, "Fatal: Memory reallocation failed (%zu bytes)\n", new_size);
        exit(EXIT_MEMORY_ERROR);
    }
    return new_ptr;
}

/* Call in main() before any GMP operations */
mp_set_memory_functions(safe_gmp_allocate, safe_gmp_reallocate, safe_gmp_free);
```

### 12.2 Input Validation

```c
/*
 * Validate semiprime input before processing
 */
int semiprime_validate(const semiprime_t *sp) {
    /* Check N > 1 */
    if (mpz_cmp_ui(sp->N, 1) <= 0) {
        return VALIDATE_ERR_TOO_SMALL;
    }
    
    /* Check N is not prime (would have no non-trivial factors) */
    if (mpz_probab_prime_p(sp->N, 25) > 0) {
        return VALIDATE_ERR_IS_PRIME;
    }
    
    /* If factors provided, verify N = p × q */
    if (sp->factors_known) {
        mpz_t product;
        mpz_init(product);
        mpz_mul(product, sp->p, sp->q);
        int match = (mpz_cmp(product, sp->N) == 0);
        mpz_clear(product);
        
        if (!match) {
            return VALIDATE_ERR_FACTOR_MISMATCH;
        }
        
        /* Verify p and q are prime */
        if (mpz_probab_prime_p(sp->p, 25) == 0) {
            return VALIDATE_ERR_P_NOT_PRIME;
        }
        if (mpz_probab_prime_p(sp->q, 25) == 0) {
            return VALIDATE_ERR_Q_NOT_PRIME;
        }
    }
    
    return VALIDATE_OK;
}
```

***

## 13. Documentation Requirements

### 13.1 README.md Structure

```markdown
# Z5D Distribution Asymmetry Visualizer

Tool for analyzing candidate factor score distributions in semiprime 
factorization, demonstrating validated asymmetric enrichment phenomena.

## Quick Start
## Installation
## Usage Examples
## Output Interpretation
## Algorithm Overview
## References
## License
```

### 13.2 Inline Documentation

All public functions require:
- Brief description (one line)
- Algorithm summary (if non-trivial)
- Parameter documentation
- Return value specification
- Error conditions

***

## 14. Acceptance Criteria

The implementation is complete when:

- [ ] Compiles with `gcc -std=c99 -Wall -Wextra -Wpedantic` with zero warnings
- [ ] All unit tests pass
- [ ] Processes 10⁴⁰-magnitude semiprimes without overflow
- [ ] Generates valid CSV parseable by Python/pandas
- [ ] Generates valid SVG renderable in modern browsers
- [ ] KS p-values match SciPy reference within 1%
- [ ] Factor scores rank in top 5% for ≥90% of test corpus
- [ ] Memory usage stays under 100 MB for 100,000 candidates
- [ ] Documentation complete per Section 13

Sources
[1] 47 https://github.com/zfifteen/geofac_validation/pull/47
