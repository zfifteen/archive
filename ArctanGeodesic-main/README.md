# ArctanGeodesic
This is a standalone Python library implementing stable arctan identities and geodesic mappings θ′(n, k) = φ · ((n mod φ)/φ)^k, with φ = (1 + √5)/2 from Euclid's extreme/mean ratio (Elements Book VI Prop. 30).

**Classical Lineage:** Draws from 2,000+ years of mathematics—Ptolemy's Almagest (c. 150 AD, half/double-angle chord tables for tan(θ/2) and tan(2α)); Euclid's Elements (c. 300 BCE, Book V Def. 3 for proportions, Book II Prop. 11 for geometric means); Diophantus' Arithmetica (c. 250 CE, Book III for algebraic divisor manipulations in κ(n)); Euler's Introductio in analysin infinitorum (1748, Vol. 8-9 for trig derivatives d/dx arctan(u) = u'/(1+u²)); Riemann's 1859 zeta insights for prime correlations (r ≈ 0.935). Full citations in docs/classical_sources.md (13+ references).

**Empirical validations:** Symbolic exactness (SymPy), numeric precision <10^{-50} (mpmath dps=50), bootstrap CIs for ~15% density enhancements. Contribute via PRs for trig integrations and extensions (e.g., bio sequence analogs).

## Supporting Documentation from unified-framework

Copies of relevant documentation from the [zfifteen/unified-framework](https://github.com/zfifteen/unified-framework) repository, which discusses Z5D framework and RSA factorization enhancements:

- [README](docs/README_unified_framework.md) - Main repository overview.
- [RSA Tuning Scaling Experiment](docs/rsa_tuning_scaling_experiment.md) - Details on RSA-100 success and scaling challenges to RSA-129.
- [Z5D RSA Implementation Summary](docs/Z5D_RSA_IMPLEMENTATION_SUMMARY.md) - Summary of Z5D implementations for RSA factorization.
