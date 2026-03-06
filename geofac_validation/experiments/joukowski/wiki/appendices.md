## Appendix A: Full Derivation of Equation (1)

Starting from \(z = x + iy = a\cos\theta + ib\sin\theta\):

\[
z = a\left(\frac{e^{i\theta} + e^{-i\theta}}{2}\right) + ib\left(\frac{e^{i\theta} - e^{-i\theta}}{2i}\right)
\]

\[
= \frac{a}{2}(e^{i\theta} + e^{-i\theta}) + \frac{b}{2}(e^{i\theta} - e^{-i\theta})
\]

\[
= \frac{a+b}{2}\,e^{i\theta} + \frac{a-b}{2}\,e^{-i\theta} \quad \blacksquare
\]

## Appendix B: Verification of Constant Areal Velocity

For \(z = ne^{i\theta} + me^{-i\theta}\):

\[
\bar{z} = ne^{-i\theta} + me^{i\theta}
\]

\[
\frac{dz}{d\theta} = ine^{i\theta} - ime^{-i\theta}
\]

\[
\bar{z}\frac{dz}{d\theta} = (ne^{-i\theta} + me^{i\theta})(ine^{i\theta} - ime^{-i\theta})
\]

\[
= in^2 - inme^{-2i\theta} + inme^{2i\theta} - im^2
\]

\[
= i(n^2 - m^2) + inm(e^{2i\theta} - e^{-2i\theta})
\]

\[
= i(n^2 - m^2) - 2nm\sin(2\theta)
\]

Taking the imaginary part:

\[
L = \operatorname{Im}\!\left(\bar{z}\frac{dz}{d\theta}\right) = n^2 - m^2 = N \quad \blacksquare
\]

## Appendix C: Stokes Parameters in Circular Basis

For a field decomposed as \(E = E_R\,\hat{e}_R + E_L\,\hat{e}_L\) where \(\hat{e}_R = (\hat{x} + i\hat{y})/\sqrt{2}\) and \(\hat{e}_L = (\hat{x} - i\hat{y})/\sqrt{2}\), the Stokes parameters in the circular basis are[^155]:

\[
S_0 = |E_R|^2 + |E_L|^2, \quad S_3 = |E_R|^2 - |E_L|^2
\]

With \(E_R = R_+ = n\) and \(E_L = R_- = m\):

\[
S_0 = n^2 + m^2 = \frac{(p+q)^2 + (q-p)^2}{4} = \frac{2(p^2 + q^2)}{4} = \frac{p^2 + q^2}{2}
\]

\[
S_3 = n^2 - m^2 = N \quad \blacksquare
\]

## Appendix D: Proposed Experimental Protocol

**Objective:** Validate the enrichment scaling law (Prediction 9.1).

**Setup:**
1. Generate 1000 semiprimes at each of 6 factor ratios: \(q/p \in \{1.2, 1.5, 2.0, 3.0, 5.0, 10.0\}\), all with \(N\) in the 64-bit range.
2. For each semiprime, run Z5D scoring with standard parameters (\(c = -0.00247\), \(k^* = 0.04449\)).
3. Extract top-10K candidates by Z5D score.
4. Measure enrichment\_q (fraction of top-10K within 1% of \(q\)) and enrichment\_p (fraction within 1% of \(p\)).
5. Compute asymmetry ratio \(A = \text{enrichment\_q} / \text{enrichment\_p}\).

**Expected Result:** \(A\) should increase monotonically with \(q/p\), following either \(A \propto q/p\) or \(A \propto (q/p)^2\).

**Disconfirmation Threshold:** If \(A\) is not positively correlated with \(q/p\) at 95% confidence (Spearman \(\rho > 0.8\)), the conformal anisotropy explanation is rejected.

## Appendix E: Glossary of Terms

This glossary provides definitions for key terms used throughout the documentation.

| Term | Definition |
|------|------------|
| **Conformal Anisotropy** | The directional bias in the Joukowski conformal map, quantified by the derivative ratio q/p at the ellipse axis endpoints. Causes denser lattice sampling near the larger factor. |
| **Coverage Paradox** | The discrepancy between claimed coverage (~0.0007%) and actual coverage (~10^-11%) in blind sampling experiments, caused by conflating percentage of √N with percentage of candidates tested. |
| **Discovery Gap** | The chasm between statistical signal detection (p < 10^-300) and actual factor discovery through blind sampling. A sampling density problem, not a signal quality problem. |
| **Dwell-Time Bias** | The (q/p)^2 ratio by which parametric sampling spends more time near the larger factor due to slower arc speed at the ellipse major axis. |
| **Enrichment** | The ratio of candidates near true factors in top-K Z5D slices versus baseline (random) expectation. Measured separately for p (smaller) and q (larger) factors. |
| **Factor Radar** | Informal term for the GeoFac framework's function as a statistical distinguisher that detects factor proximity without directly discovering factors. |
| **Factoring Ellipse** | An ellipse with semi-major axis = q and semi-minor axis = p for semiprime N = pq. Area = πN. |
| **Fermat Variables** | n = (p+q)/2 (half-sum) and m = (q-p)/2 (half-difference). Satisfy N = n² - m². |
| **Hyperbolic Parameter** | u = ln(ℛ) = arctanh(p/q). Encodes factor ratio in hyperbolic space. |
| **Joukowski Radius** | ℛ = √(n/m). The radius of the pre-image circle that maps to the factoring ellipse under the Joukowski transform. |
| **Joukowski Transform** | The conformal map w = z + 1/z. Maps circles of radius R > 1 to ellipses with semi-axes R ± 1/R. |
| **Phasor Decomposition** | Representation of the ellipse as sum of counter-rotating circular motions (CCW radius R₊ = n, CW radius R₋ = m). |
| **Poincaré Latitude** | χ = (1/2)arcsin(V). Measures factor balance on the Poincaré sphere. Poles = balanced primes, equator = unbalanced. |
| **QMC (Quasi-Monte Carlo)** | Sampling method using low-discrepancy sequences (Sobol, Halton) for more uniform coverage than pseudorandom sampling. |
| **Stokes Parameter S₃** | In the circular basis, S₃ = R₊² - R₋² = n² - m² = N. The semiprime is identically the third Stokes parameter. |
| **Z5D Framework** | Geometric resonance scoring system using log-phase alignment with φ (golden ratio) and e (Euler's number) to produce PNT-aligned signals. |
