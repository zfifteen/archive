# Forensic Analysis of z5d-prime-predictor

This note records the repository's current, supportable shape rather than the broadest historical framing that appears in older drafts.

- The active nth-prime predictor path is a calibrated closed-form seed plus short forward refinement to a probable prime. The C, Python, and Java implementations all follow that same high-level contract.
- Exactness is locked on the shipped 19-point benchmark grid `10^0 ... 10^18` through committed lookup values and the cross-language parity harness.
- Off-grid behavior is empirical. The repo supports arbitrary-size integer inputs, but current checked-in docs should not claim a proof that off-grid outputs equal exact nth primes.
- The C build is intentionally macOS / Apple Silicon scoped and relies on Homebrew GMP / MPFR. Python uses `gmpy2`; Java uses `BigInteger`.
- Legacy Riemann-`R(x)` / Newton helper routines still exist in the tree, but they are historical or compatibility artifacts rather than the primary predictor described by the active docs.
- The exploratory `experiments/` and `whitepaper/` materials are useful research context, but they are not the canonical source of truth for what the active predictor currently guarantees.
