## 8. Prior Art and Novelty Assessment

### 8.1 Closest Known Work

| Prior Work | Overlap | Structural Difference |
|---|---|---|
| Fermat's factorization method (1640s)[^89] | Same algebra \(N = n^2 - m^2\) | No geometric interpretation of search anisotropy; treats \(n\) increments uniformly |
| Joukowski transform in aerodynamics[^43] | Same conformal map from circles to ellipses | Applied to fluid dynamics, never connected to integer factoring or lattice density |
| Polarization ellipse decomposition[^185] | Same RHCP + LHCP circular decomposition | Applied to EM waves; the Stokes identity \(S_3 = N\) for semiprimes appears to be new |
| Crown Sterling (2019)[^116] | Claims geometric semiprime factoring | No conformal framework, no Joukowski connection, methods not validated at scale |
| Geometric square-based RSA (2025)[^149] | Uses difference of squares geometrically | No phasor decomposition, no directional analysis |

### 8.2 Novelty Assessment

The genuinely new elements, as assessed against the facets of purpose, mechanism, evaluation, and application:

- **New mechanism:** The Joukowski derivative ratio as the source of directional sampling bias in factoring (Theorem 1)
- **New evaluation metric:** The enrichment asymmetry ratio as a quantitative signature of conformal anisotropy
- **New application:** The Stokes parameter dictionary mapping polarimetry concepts bijectively onto factoring concepts
- **New empirical result:** The Z5D detection asymmetry as computational evidence of conformal anisotropy[^167]

### 8.3 Rephrase Trap

Can the core insight be reduced to a cliche? "Balanced primes are hard to factor" is well known, but the *reason* given here (conformal isotropy of the Joukowski image) and the *quantitative prediction* (enrichment scales as \(q/p\)) are not reducible to this folk wisdom. The mechanism (conformal compression creating lattice density anisotropy) is not present in any standard account of factoring difficulty.