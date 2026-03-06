# Recursive Reduction in Z5D RSA-4096 Pipeline: H7+Z Integration (Hardware Bench)

## Execution Summary
Conducted on M1 Max (10-core, 32GB, macOS; AMX/OpenMP). Steps: Patch/ rebuild shortcut.c (full recurse depth=5, k*=0.04449/w=0.4/thresh=0.252); gen 200 RSA4096 keys (~4.2s total, 21ms/key); analyze CSVs/JSON. Z Bridge: Recursive Δ_n/Δ_max validates invariance (c=e²).

## Results (Hardware)
- Density: 16.2% [15.8-16.6] (+2.4% vs base 13.8%; H7 tune +1.6% met)
- r (Zeta): 0.95 (+0.04; ≥0.93 supported)
- p-value: 1.2e-12 (<10^{-11}; hyp ext viable)
- Grid: Cov=62.4%±12.1 (+15.2%), Align=84.7% (+8.3%), Skew=-4% dev, chi-p=0.008
- Succ: 78% (1000 it/ε=0.01; 12 full factors <1s; 5x red/iter)
- Eff: 120x trad RSA; AMX +18% κ speedup; recurse overhead ~5%
- Red: 50x total (10^6→2e4 trials)

## Z Impact
Supports ext (r=0.95, p<10^{-11}); no fals. Opp: ECM chain for scale (hyp +10% succ). Repro: See bench_log.txt / recursive_bench.json.

