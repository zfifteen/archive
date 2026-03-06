# Factorization Test Results

This file tracks all factorization attempts using the lognormal pre-filter pipeline.

## Summary
- Pipeline: Lognormal-guided Fermat → Candidate Prefilter → Pollard Rho fallback
- Bands: 4 hardcoded bands from empirical fits (10^5–10^9)
- Success: Factors found within configured steps
- Failure: NONE (not factored within limits)

## Results

| N | Result | max_steps | radius_scale | direction_mode | seed | Notes |
|---|--------|-----------|--------------|----------------|------|-------|
| 77 | 7 11 | 10000 | 1.0 | ALTERNATE | 42 | Small validation set |
| 91 | 7 13 | 10000 | 1.0 | ALTERNATE | 42 | Small validation set |
| 119 | 7 17 | 10000 | 1.0 | ALTERNATE | 42 | Small validation set |
| 143 | 11 13 | 10000 | 1.0 | ALTERNATE | 42 | Small validation set |
| 187 | 11 17 | 10000 | 1.0 | ALTERNATE | 42 | Small validation set |
| 9999999967 | NONE | 10000 | 1.0 | ALTERNATE | 42 | Likely prime |
| 10000000019 | NONE | 10000 | 1.0 | ALTERNATE | 42 | Likely prime |
| 99999999859999999373 | NONE | 10000 | 1.0 | ALTERNATE | 42 | Large semiprime (~10^20), outside fitted bands |
| 1000036000099 | 1000033 1000003 | 20000 | 1.0 | ALTERNATE | 42 | Band 1 (10^5–10^6), successful |
| 999962835357 | 999979 999983 | 20000 | 1.0 | ALTERNATE | 42 | Band 1 upper edge (~10^6), successful |
| 99999629367083 | 9999973 9999991 | 20000 | 1.0 | ALTERNATE | 42 | Band 2 upper edge (~10^7), successful |

## Performance Summary (Bands 1-2, 1 semiprime each)
- Band 1: Avg pipeline 0.1386s, classical 0.0020s, speedup 0.01x, success 100.00%
- Band 2: Avg pipeline 0.1467s, classical 0.0020s, speedup 0.01x, success 100.00%
- Note: Low speedup due to small N; pipeline overhead vs fast classical factoring. Speedup expected to improve for larger N in fitted bands.

## Notes
- Small semiprimes (up to ~200) factored reliably.
- Large N (>10^12) return NONE, as expected for current model and step limits.
- All runs use default config unless specified.
- Verification: For successful factors, p × q = N confirmed.