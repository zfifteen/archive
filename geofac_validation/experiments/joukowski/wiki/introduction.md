## 1. Introduction

The difficulty of factoring large semiprimes underpins the security of RSA cryptography and remains one of the central open problems at the intersection of number theory and computational complexity[^89][^172]. While algebraic and number-theoretic methods (Fermat, quadratic sieve, GNFS, ECM) dominate the field, there is persistent interest in whether *geometric* insight could reveal structure invisible to purely algebraic approaches[^184][^149].

This paper originates from a simple observation: the complex exponential parametrization of an ellipse, widely used in electrical engineering and signal processing, decomposes any ellipse into two circular motions (phasors). When the ellipse's semi-axes are set to the prime factors of a semiprime, this decomposition recovers Fermat's factorization variables as the phasor radii, and the Joukowski conformal map provides a natural bridge between the factor circle and the factor ellipse.

The core theoretical contribution is the proof that the Joukowski derivative ratio at the axis endpoints equals exactly \(q/p\) (Theorem 1), implying a measurable anisotropy in how the integer lattice is sampled by any ellipse-parametrized search. The core empirical contribution is the demonstration, via the Z5D geometric resonance framework, that this anisotropy manifests as a strong detection asymmetry favoring the larger factor.

### 1.1 Notation and Conventions

Throughout this paper:
- \(N = pq\) is a semiprime with \(p \leq q\)
- \(n = (p+q)/2\) is the Fermat half-sum
- \(m = (q-p)/2\) is the Fermat half-difference
- \(R = \sqrt{n/m}\) is the Joukowski radius
- \(u = \ln(R) = \operatorname{arctanh}(p/q)\) is the hyperbolic parameter
- \(\theta\) is the ellipse parametric angle (not the geometric angle to a point on the ellipse)