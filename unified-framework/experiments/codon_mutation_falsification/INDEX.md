# Codon Mutation Rate Falsification Experiment - Index

## Quick Links

- **[Executive Summary](EXECUTIVE_SUMMARY.md)** - Crystal clear results (read this first!)
- **[Detailed Methodology](README.md)** - Complete experimental design and justification
- **[Experiment Code](falsification_experiment.py)** - Fully reproducible Python implementation
- **[Raw Results](results.json)** - All numerical data in JSON format

## Experiment Overview

**Goal:** Attempt to falsify the hypothesis that Stadlmann's θ ≈ 0.525 bounds mutation rates in codon distributions with correlation r ≥ 0.90.

**Result:** ✅ **HYPOTHESIS CONCLUSIVELY FALSIFIED**

**Status:** Complete (2025-11-23)

## One-Sentence Summary

Empirical analysis of real E. coli DNA sequences shows **no correlation** (r = -0.17, p = 0.19) between Stadlmann's prime distribution parameter θ and biological codon mutation rates, definitively falsifying the claimed r ≥ 0.90 relationship.

## Key Findings (TL;DR)

| Metric | Claimed | Observed | Verdict |
|--------|---------|----------|---------|
| Correlation (r) | ≥ 0.90 | -0.17 | ❌ FALSIFIED |
| P-value | < 10⁻⁵ | 0.19 | ❌ FALSIFIED |
| 95% CI | Contains 0.90 | [-0.40, 0.08] | ❌ FALSIFIED |
| Direction | Positive | Negative | ❌ FALSIFIED |
| Effect Size | Strong | Negligible | ❌ FALSIFIED |

## Document Guide

### For Executives / Decision Makers
→ Read **[EXECUTIVE_SUMMARY.md](EXECUTIVE_SUMMARY.md)**
- Clear verdict with no technical jargon
- Key numbers and what they mean
- Recommendations for action

### For Scientists / Researchers
→ Read **[README.md](README.md)**
- Complete methodology
- Statistical justification
- Limitations and controls
- Theoretical background

### For Engineers / Developers
→ Review **[falsification_experiment.py](falsification_experiment.py)**
- Well-commented, production-quality code
- Reproducible (seed = 42)
- Extensible for similar experiments

### For Data Analysts
→ Load **[results.json](results.json)**
- All raw data and computed metrics
- Bootstrap distributions
- Ready for further analysis

## Reproduction Instructions

```bash
# Install dependencies
pip install biopython numpy scipy matplotlib

# Navigate to experiment directory
cd experiments/codon_mutation_falsification

# Run experiment (takes ~10 seconds)
python falsification_experiment.py

# Expected output: "❌ FALSIFIED (below threshold) - High confidence"
```

## Experiment Statistics

- **Date:** 2025-11-23
- **Random Seed:** 42 (fully deterministic)
- **Biological Data:** Real E. coli lacZ gene (6,415 bp)
- **Sample Size:** 2,138 codons
- **Bootstrap Resamples:** 1,000
- **Runtime:** ~10 seconds
- **Result:** Hypothesis falsified with very high confidence

## Why This Matters

This experiment demonstrates:

1. **Cross-domain claims require validation** - Mathematical parameters from one field (prime number theory) don't automatically apply to unrelated fields (biology)

2. **Empirical testing is essential** - The claimed correlation wasn't tested before being published; this experiment fills that gap

3. **Negative results are valuable** - Falsifying invalid hypotheses prevents wasted effort by future researchers

4. **Reproducibility is achievable** - Full code, data, and methodology provided for independent verification

## Citation

If you reference this work:

```
Codon Mutation Rate Falsification Experiment (2025)
Repository: github.com/zfifteen/unified-framework
Path: experiments/codon_mutation_falsification/
Date: 2025-11-23
Result: Hypothesis falsified (r = -0.17, CI [-0.40, 0.08], p = 0.19)
```

## Contact & Feedback

- **Issues:** Open an issue in the main repository
- **Questions:** Review the detailed methodology in README.md
- **Reproductions:** All code and data are included
- **Extensions:** Feel free to adapt this framework for similar tests

## Metadata

```json
{
  "experiment_id": "codon_mutation_falsification_v1",
  "hypothesis": "θ ≈ 0.525 bounds mutation rates with r ≥ 0.90",
  "status": "complete",
  "verdict": "falsified",
  "confidence": "very high",
  "date": "2025-11-23",
  "seed": 42,
  "reproducible": true
}
```

---

**Bottom Line:** The hypothesis is false. The Z Framework's θ parameter does not correlate with biological mutation rates.
