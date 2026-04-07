# Z5D nth-Prime Predictor - Current Technical Specification

This specification describes the algorithm currently implemented in `src/z5d_predictor.c`. It does not treat the legacy Riemann-`R(x)` helpers in `z5d_math.c` as the active predictor path.

## Contract

Input:
- Positive integer `n`, accepted as `uint64_t`, decimal string, or arbitrary-size `mpz_t`

Output:
- Exact prime for the shipped benchmark indices `10^0 ... 10^18`
- Otherwise, a probable prime produced by calibrated seed generation plus forward refinement

Non-goals:
- Global proof that the returned off-grid value equals the exact nth prime
- Cross-platform portability guarantees for the C build

## Active algorithm

### 1. Exact benchmark lookup

For these indices, the implementation returns committed ground-truth values directly:

`1, 10, 10^2, ... , 10^18`

This lookup table is the repo's exact parity lock across C, Python, and Java.

### 2. Precision selection

For arbitrary-size `n`, MPFR precision starts from the default and grows with the bit length of `n`:

`required_precision = bitlen(n) + 2048`

This keeps enough headroom for logarithms and the fitted correction terms.

### 3. Closed-form seed

Let

`pnt = n(ln n + ln ln n - 1 + (ln ln n - 2)/ln n)`

The implementation then applies two fitted corrections:

- `d_term = ((ln pnt / e^4)^2) * pnt * c`
- `e_term = pnt^(-1/3) * pnt * kappa_star`

with:

- `c = -0.00016667`
- `kappa_star = 0.06500000`

The seed is:

`seed = round(pnt + d_term + e_term)`

If the corrected seed becomes non-positive, the code clamps back to `pnt`.

### 4. Forward refinement

The rounded seed is converted to an integer and refined forward to the next probable prime:

- Clamp minimum candidate to `2`
- Step back by one
- Call GMP `mpz_nextprime`

This refinement includes the candidate itself if it is already prime and otherwise returns the next probable prime above it.

## Guarantees and limits

Guaranteed by committed artifacts:
- Exact values on the 19-point benchmark grid
- Cross-language parity on that same grid
- Deterministic off-grid output for fixed inputs and fixed implementation

Not guaranteed:
- Exact nth-prime correctness off the shipped grid
- Error envelope beyond the checked-in benchmark points without rerunning experiments

## Public API notes

Primary callers should use:
- `z5d_predict_nth_prime_mpz_big`
- `z5d_predict_nth_prime_mpz`
- `z5d_predict_nth_prime_str`

The older `z5d_result_t` / `z5d_config_t` API surface remains available, but the active predictor no longer consumes `K` or Newton-iteration settings as part of its main algorithm.

## Legacy helper code

`z5d_math.c` still contains:
- logarithmic integral helpers
- Riemann-`R(x)` helpers
- Newton-style step helpers

These routines are retained for compatibility and research experimentation. They are not the current production path described in this specification.
