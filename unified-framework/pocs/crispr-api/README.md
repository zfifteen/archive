# CRISPR Scoring POC API

This POC merges logic from `wave-crispr-signal` and `dna-breathing-dynamics-encoding` into a unified scoring service.

## Core Features
- **Spectral Encoding**: Combines base-specific breathing rates with nearest-neighbor thermodynamic stability.
- **Helical Registration**: Explicitly models the 10.5 bp/turn helical period of B-DNA.
- **CZT Resolution**: Uses Chirp Z-Transform for sub-bin resolution at the helical frequency.

## Current Progress
- [x] Unified scoring function implemented in `src/scorer.py`.
- [ ] API wrapper (FastAPI).
- [ ] Validation against Brunello dataset.

## How to Run
```bash
python src/scorer.py
```
