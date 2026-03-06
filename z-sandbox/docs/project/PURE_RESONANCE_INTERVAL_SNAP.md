# PURE RESONANCE Interval Snap Plan (2025-11-06)

Goal: Factor N via geometric-only method by clustering fuzzy log-space crests and snapping integers locally.

Plan:
- Precision: mpmath-only (mp.dps=256), no float casts.
- Intervals: for each (k,m), l=½ ln N − (π/k)m, Δl=(π/k)Δm; keep [l−Δl, l+Δl].
- Cluster: greedy overlap clustering; keep clusters with ≥3 distinct k.
- Centers: mean(l) per cluster.
- Snap: for each center p*=round(exp(l)), wheel-sieve ±R (1e6–1e7), check N%p==0.
- Logging: results/<date>.tsv|jsonl and centers TSV.

Execution (initial sweep):
- k∈[0.27,0.33], Δk=0.001; m∈[−10,10], Δm=5e−4; min_k_cluster=3; R=1e6.

Results (2025-11-06T06:37Z):
- Centers: recorded to results/interval_centers_2025-11-06.tsv
- Checked: see results/2025-11-06.jsonl (interval_snap entry)
- Status: No factor found in initial snap; runtime under 10m.

Next:
- Increase m-range to 20, Δm=2.5e−4; k-step=5e−4; R=1e7 on top clusters only.
- Add deterministic seed to any tie-breaks; maintain mp.dps=512 if needed.
