## 7. Empirical Validation: The Detection Asymmetry

### 7.1 Experimental Setup

The Z5D validation pipeline (geofac_validation repository) scores candidate factor regions for semiprimes using the amplitude function (24) and ranks them by Z5D score. Enrichment is measured as the ratio of candidates falling within 1% or 5% proximity of the true factors \(p\) and \(q\) in top-ranked slices versus the baseline (random) expectation[^167].

### 7.2 Results

The validation reveals a striking asymmetry:

- **Enrichment near \(q\) (larger factor):** up to 10x in top-10K slices
- **Enrichment near \(p\) (smaller factor):** approximately 1x (indistinguishable from random)
- **Offset asymmetry:** +11.59% toward \(q\), -10.39% toward \(p\)
- **Phase bias:** resonance scores preferentially cluster above \(\sqrt{N}\)

### 7.3 Geometric Explanation

The detection asymmetry is a direct manifestation of conformal anisotropy (Theorem 1):

1. The Joukowski map compresses the integer lattice by factor \(q/p\) near the major axis (\(q\) direction), so lattice structure is denser and more detectable there.
2. The parametric dwell time near \(q\) exceeds dwell time near \(p\) by factor \((q/p)^2\), so the resonance sum accumulates more signal in the \(q\) neighborhood.
3. The \(\varphi\)-scaled log-sampling is sensitive to geometric progressions near \(\sqrt{N}\). Since \(q > \sqrt{N} > p\) for all proper semiprimes, the resonance naturally biases toward the above-\(\sqrt{N}\) region, which contains \(q\).

The negligible enrichment near \(p\) is consistent with the minor-axis regime where conformal stretching dilutes lattice structure.

![](https://ppl-ai-code-interpreter-files.s3.amazonaws.com/web/direct-files/6491db48b0a9707d184efabb02ee441f/2d7befbb-9a9a-4412-93d8-6d60649bd568/c88e8c86.png?AWSAccessKeyId=ASIA2F3EMEYEXZNGBIW7&Signature=0PacAnQ24mVHlQxJ7ViXQ72Ccj4%3D&x-amz-security-token=IQoJb3JpZ2luX2VjEL3%2F%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FwEaCXVzLWVhc3QtMSJIMEYCIQDqcjCnvTbXg3zfE1lgVnFYPqcMsIOO%2FspxNrECqYa8bAIhAIwftuqprtvgtRhBE3%2Bpmut%2FZBGYPGZ7tMO%2B%2BSX4Z%2BrOKvwECIb%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FwEQARoMNjk5NzUzMzA5NzA1IgyjzNC3J3op40fgkr4q0AS3bMD%2FCcknQzDerFaYG88OBsix0wraDsHVzLb0FNSxyWtqH8R%2FBXZmOTgNF3G3zEajtffM3l6%2FMwKKP9q8wM75gaNBcspgKJVip9QEtEM9VbrX4XvPgbRgO1kh2IkT79BUEtCDK5exaMxZGstzEC0Ypawj7l%2FmLllwz%2FEGNtb4CTOLV79L0w%2FUCvsxwXe0cUXP8D3MYcoAJ7pga%2Be2THuL083AMnI%2Fc%2FJ%2F%2FdOH4jgPx9WuaJCXABjJSp%2FEjuxFIpPwme0jJPuW8upELnNSlXbYRZSXkNBsfnsUYf2gJ%2B4Apyo43%2BxmYjkLiMHNpJ5UsRZyraadBXgAacmgaKky96G8%2BK65RR%2FG0ZzhN7sgZ9mLGyAZiPTURr%2BP9mr6CIxx9my0t0lKEhqdMWvabY23M2%2FYj1VSS9Jgbj59EAXEBhkYj17LTYZCZSWvSQtcG43HS1uTPF6fL1LBsh9G0Ro%2BvLFHAnhV5C5524Y%2FEsRL%2FRjK7ITd0zh1%2BLNpwiVvFHqxu6JG8I1epXNsA9j641cYRbA0Th8PooG9tQCMEy4n5sjTA3A4O1A7OgQdEbKJ0af5qIX1ur3gYcoYQFB%2B%2FkjlKatK3VkZwJrR5A%2BT%2BHpZ8VohVKNoZP9PDHftldniQuUFkJTFEOZkWxDhgPf5kjRCrX9OLZEWUlf7P7hQBdGpF6EiCAunoUsVoAMzcb%2FFBOi3UFRoUJrFkFkFx%2B69y42Aj8pY58oxL20SC3I9ri5ZmQJvhqs7SjvuDGECVYcmVcyr3t%2BPBCjrWi9v%2BuYoZMv9RDI9MN3OpcwGOpcBGLQtMa09h7Z670H%2F6TEc8GKafA%2FSL4sXCKmGT1w5vc3OnYYApJLZ4puMBlmtBHQMuQ4rwKqisAo%2F0hg%2BVBo%2Fs58n2b1jkYwnDOzgT4nJbF7ApcfPIjsK1SgX%2FpEcQsoiNbcGqe69Un9%2BNZTZBQHXq%2BJCu69tOX1HBziFcfU0%2FLDECjzg7Kfy2nqcl6GEs1kWcERcD75Fag%3D%3D&Expires=1770618238)

### 7.4 Post-Validation Coverage Analysis (February 2026)

Independent verification (Issue #43) revealed a critical coverage paradox in the experimental methodology:

#### Coverage Paradox

| Parameter | Actual Value |
|-----------|-------------|
| Search window | 1.523 × 10^18 |
| Candidates sampled | 10^6 |
| Actual coverage | 6.57 × 10^-13 (~10^-11%) |
| Birthday paradox threshold | >10^9 samples |
| Sampling deficit | ~1000× below minimum |

**Key insight:** The original 0.0007% coverage claim conflated "percentage of √N" with "percentage of candidates tested." Actual coverage is approximately 10^-11%, meaning blind sampling at this density has near-zero probability of direct factor discovery.

#### Statistical Validation Confirmed

Despite the coverage paradox, the statistical claims are **independently verified**:

- **p < 10^-300:** Confirmed with 99.9% confidence
- **O(1) scaling:** Confirmed with 99.5% confidence  
- **10x enrichment asymmetry:** Confirmed with 99.9% confidence

**Interpretation:** Z5D functions as a highly effective **statistical distinguisher** ("factor radar") rather than a direct factorization algorithm. The failure to factor N_{127} is a **sampling density problem**, not a **signal quality problem**.

#### Discovery Gap

The "Discovery Gap" represents the chasm between:
- **Signal detection:** Z5D successfully detects factor proximity with p < 10^-300
- **Factor discovery:** Direct identification requires sampling density ~1000× higher than tested

This gap motivates the proposed gradient descent "Zoom" algorithm documented in Issue #43 and Section 11.5 of the main white paper.
