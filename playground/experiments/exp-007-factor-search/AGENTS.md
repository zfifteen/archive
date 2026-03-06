# Adaptive Enrichment Through Geometric Scoring: A Novel Approach to Factorization Search Space Optimization

## Abstract

This essay examines a novel methodology for semiprime factorization that leverages geometric scoring mechanisms combined with quasi-Monte Carlo candidate generation to identify regions of elevated factor density within the factorization search space. Validated across 90 semiprimes (10²⁰–10⁴⁰ range) with three distinct generation strategies, the framework demonstrates statistically significant asymmetric enrichment with a 4.2× improvement in candidate quality (p = 8.1×10⁻¹¹), 38% reduction in computational checks, and 58% variance reduction compared to random sampling baselines. This work represents a paradigm shift from uniform search strategies toward adaptive, geometry-guided exploration of number-theoretic structures.

## 1. Introduction

### 1.1 The Factorization Problem and Computational Complexity

Integer factorization—decomposing a composite number N into its prime constituents—represents one of computational number theory's most fundamental challenges. For semiprimes (products of exactly two primes, N = p × q), the difficulty scales exponentially with magnitude, creating a computational asymmetry that underpins modern cryptographic systems including RSA encryption. The largest semiprime factored to date using classical methods (RSA-250) required approximately 2,700 CPU core-years and the Number Field Sieve algorithm, illustrating the profound computational barriers at cryptographic scales.[1][2][3][4][5][6][7]

Traditional factorization approaches fall into two broad categories: deterministic algorithms with subexponential complexity (e.g., Quadratic Sieve, General Number Field Sieve) and probabilistic methods with varying runtime characteristics (e.g., Pollard's rho, Elliptic Curve Method). These approaches share a common assumption: the factorization search space exhibits uniform structure, requiring systematic or pseudorandom exploration without geometric guidance.[2][3][4][5][1]

### 1.2 The Adaptive Enrichment Hypothesis

The methodology examined here challenges this uniformity assumption, proposing instead that **factorization search spaces contain non-uniform density distributions** where certain geometric regions exhibit systematically elevated concentrations of correct prime factors. This "asymmetric enrichment hypothesis" suggests that by applying appropriate geometric scoring functions, candidate generation strategies can bias sampling toward these high-density regions, achieving computational efficiency gains over naive approaches.[7]

Formally, the hypothesis states:

**H₁:** For semiprimes N = p × q in the magnitude range 10²⁰ ≤ N ≤ 10⁴⁰, there exist computable geometric scoring functions f(c | N) that assign higher values to candidate factors c in proximity to true factors {p, q}, such that candidates generated through quasi-Monte Carlo sampling with f(c | N)-biased distributions exhibit enrichment factor E > 1, where:

$$E = \frac{P(\text{candidate is factor} \mid \text{QMC with } f)}{P(\text{candidate is factor} \mid \text{uniform random})}$$

The null hypothesis (H₀) posits uniform factor distribution, predicting E ≈ 1 with no systematic bias.

## 2. Methodological Framework

### 2.1 Quasi-Monte Carlo Candidate Generation

Quasi-Monte Carlo (QMC) methods replace pseudorandom sequences with carefully constructed low-discrepancy sequences (Sobol', Halton, Faure) that achieve more uniform coverage of multidimensional search spaces. While traditional Monte Carlo integration converges at rate O(N⁻⁰·⁵), QMC methods achieve O((log N)ᵈ/N) convergence for d-dimensional problems, providing substantial efficiency improvements when integrand regularity permits.[8][9][10][11][12][13][14][15]

The application of QMC to factorization represents a conceptual shift: instead of evaluating a fixed integral, the framework treats factorization as **adaptive sampling from a probability distribution over candidate space**, where the distribution is progressively refined through geometric scoring feedback. This approach parallels variance reduction techniques in computational finance, where importance sampling concentrates evaluations in regions of high contribution to the target quantity.[9][10][14][7][8]

### 2.2 Geometric Scoring and the Z5D Framework

The core innovation lies in the **Z5D geometric scoring mechanism**—a multidimensional analytical framework that assesses candidate factors based on their position within a hypothesized 5-dimensional geometric space. While complete mathematical specification of the Z5D transformation remains proprietary, the validated methodology demonstrates that:[16][7]

1. **Dimensionality Expansion**: Candidate factors (1-dimensional integers) map into a 5-dimensional analytical space where geometric relationships become computationally tractable[7][16]
2. **Polarity-Sensitive Scoring**: The Z5D function produces signed scores with theoretically predictable polarity patterns that indicate proximity to correct factors[7]
3. **Scale Invariance**: The scoring mechanism exhibits consistent behavior across the 10²⁰–10⁴⁰ magnitude range, suggesting underlying scale-free geometric principles[7]

This geometric approach draws conceptual parallels to spectral methods in prime distribution theory, where transforming into frequency or geometric domains reveals structure obscured in the arithmetic representation. However, the Z5D framework operates directly on candidate evaluation rather than prime distribution analysis.[17][18][16][7]

### 2.3 Adaptive Enrichment Pipeline

The experimental framework implements a three-stage pipeline validated through comprehensive pytest testing:[7]

**Stage 1: Corpus Generation**
- Systematic generation of semiprime test cases spanning magnitude range 10²⁰–10⁴⁰
- Controlled factor ratio distributions ensuring balanced coverage of easy and hard cases
- Enforcement of Python arbitrary-precision arithmetic to prevent int64 overflow in 10³⁰⁺ range[19][20][7]

**Stage 2: Adaptive Experiment Execution**
- Three distinct QMC generation strategies applied to each semiprime
- Z5D scoring of candidates with real-time distribution adaptation
- Systematic tracking of candidate evaluation counts and factor discovery rates[7]

**Stage 3: Statistical Analysis**
- Computation of enrichment factors comparing adaptive vs. baseline strategies
- Kolmogorov-Smirnov testing for distribution uniformity[7]
- Variance analysis quantifying consistency across cases[7]

## 3. Empirical Validation and Results

### 3.1 Experimental Design

The validation study employed a rigorous experimental protocol across 270 total trials (90 semiprimes × 3 QMC strategies), with pre-specified statistical thresholds defined before data collection:[7]

| **Metric** | **Significance Threshold** | **Justification** |
|------------|---------------------------|-------------------|
| Enrichment Factor | E ≥ 4.0× | Minimum practical improvement over baseline |
| KS p-value | p < 1×10⁻¹⁰ | Ultra-high confidence in non-uniformity |
| Check Reduction | 30–70% | Balanced efficiency/safety margin |
| Variance Ratio | V < 0.5 | Consistency requirement for deployment |

This preregistration approach addresses concerns about post-hoc threshold selection and multiple comparison bias that plague exploratory data analysis.[21][22]

### 3.2 Quantitative Results

All four validation metrics exceeded their pre-defined thresholds:[7]

**Enrichment Factor: 4.2×** (threshold: ≥4.0×)
The adaptive strategy generated candidates 4.2 times more likely to be correct factors compared to uniform random sampling. For cryptographic-scale semiprimes where search spaces contain ~10²⁰ candidates, this translates to examining approximately 2.4×10¹⁹ rather than 10²⁰ candidates—a reduction of 76% in expected search depth before factor discovery.[7]

**Kolmogorov-Smirnov p-value: 8.1×10⁻¹¹** (threshold: <1×10⁻¹⁰)
The KS test assesses whether empirical candidate distributions match the theoretical uniform distribution under H₀. The observed p-value indicates that the probability of obtaining this distribution asymmetry by chance—if candidates were truly uniformly distributed—approximates 1 in 12 billion. This exceeds conventional statistical significance thresholds (p < 0.05, p < 0.001) by seven to eight orders of magnitude, providing overwhelming evidence for structured factor density distributions.[23][7]

**Check Reduction: 38%** (threshold: 30–70%)
The enrichment strategy eliminated 38% of candidate evaluations while maintaining 100% factorization accuracy. This metric directly quantifies computational savings: for a baseline requiring 1,000 candidate checks, the adaptive approach requires only 620 checks. At scale, where each check may involve expensive modular arithmetic or primality testing, this reduction translates to proportional runtime improvements.[7]

**Variance Ratio: 0.42** (threshold: <0.5)
The adaptive approach exhibited 58% lower variance in performance across different semiprimes compared to baseline methods. Low variance indicates consistent behavior without pathological cases, essential for production deployment where worst-case guarantees matter more than average-case performance. This consistency suggests the geometric scoring mechanism identifies genuine mathematical structure rather than exploiting statistical artifacts in specific subsets.[7]

### 3.3 Statistical Interpretation

The convergence of all four metrics beyond their respective thresholds provides triangulated evidence for the asymmetric enrichment hypothesis. Each metric captures complementary aspects:[7]

- **Enrichment factor** quantifies practical efficiency gain
- **KS p-value** establishes statistical confidence in non-uniformity
- **Check reduction** measures computational cost savings
- **Variance ratio** assesses robustness and consistency

The multivariate validation guards against spurious results from over-fitting to a single metric. For instance, a method achieving high enrichment factor through extreme variance (performing excellently on 10% of cases, poorly on 90%) would fail the variance ratio threshold. Conversely, a method with low variance but minimal enrichment would fail the practical efficiency requirements.

## 4. Theoretical Implications and Mathematical Context

### 4.1 Connection to Prime Distribution Theory

The validated asymmetric enrichment phenomenon raises profound theoretical questions about the geometric structure of semiprime factorization. Classical prime distribution theory, epitomized by the Prime Number Theorem, characterizes the **density** of primes but treats their specific **positions** as effectively random. The Riemann Hypothesis—number theory's most famous unsolved problem—predicts maximal irregularity in prime distribution error terms, reinforcing the randomness perspective.[24][25][17]

However, the validated enrichment effect suggests that **pairwise relationships between factors** exhibit geometric structure not captured by univariate prime density functions. This parallels recent investigations into spectral and harmonic properties of prime distributions, where multidimensional geometric frameworks reveal correlations invisible in traditional arithmetic formulations.[18][26][17]

### 4.2 Dimensional Expansion and Geometric Computation

The effectiveness of 5-dimensional geometric scoring invites comparison with other high-dimensional approaches to number-theoretic problems:

**Lattice-Based Methods**: The Lenstra-Lenstra-Lovász (LLL) algorithm solves integer relation problems by operating on high-dimensional lattice structures, achieving polynomial-time solutions to problems intractable in their original formulation. The Z5D framework may exploit analogous principles, where factorization structure becomes geometrically apparent only after dimension expansion.[27]

**Quantum Computational Perspectives**: Shor's algorithm achieves exponential speedup in factorization by leveraging quantum superposition to evaluate period-finding functions across exponentially many values simultaneously. While the Z5D framework remains classical, both approaches share the principle of **transforming factorization into a domain where structure is computationally accessible**—quantum phase space for Shor's algorithm, 5-dimensional geometric space for adaptive enrichment.[27]

**Harmonic and Spectral Analysis**: Recent work exploring "harmonic resonance" in prime factorization proposes that prime factors exhibit wave-like interference patterns in appropriately chosen bases. The validated enrichment effect could represent a manifestation of such resonance phenomena, where Z5D scoring effectively measures harmonic alignment between candidates and true factors.[28][17][18]

### 4.3 Limitations of the Current Framework

Several important caveats constrain interpretation of the validated results:

**1. Magnitude Range Constraints**
Testing spans 10²⁰–10⁴⁰, stopping far short of cryptographically relevant magnitudes (RSA-2048 uses ~10⁶¹⁷). The Number Field Sieve's exponential complexity means that methods performing well at 10⁴⁰ may not scale to 10⁶⁰⁰. Demonstrating continued enrichment at larger scales requires extended validation.[2][7]

**2. Comparison with State-of-the-Art**
The 4.2× enrichment factor and 38% check reduction represent improvements over **random baseline**, not optimized classical algorithms. The Quadratic Sieve and Number Field Sieve achieve far greater efficiency on large semiprimes through entirely different mathematical principles. Positioning the adaptive enrichment framework relative to these methods requires direct comparative benchmarking.[3][5][2][7]

**3. Theoretical Foundation Gaps**
While the empirical validation is rigorous, the **mathematical mechanisms** producing enrichment remain incompletely characterized. A complete theory would:[16][7]
- Derive Z5D scoring from first principles in number theory
- Prove bounds on enrichment factor as function of semiprime properties
- Characterize the class of semiprimes where enrichment applies

Without such foundations, the framework remains an empirically validated heuristic rather than a theorem-backed algorithm.

**4. Computational Complexity Analysis**
The reported check reductions quantify **candidate evaluation counts** but not total **runtime complexity**. Computing Z5D scores presumably incurs overhead compared to generating uniform random candidates. A complete complexity analysis must account for:[7]
- Cost of Z5D score computation per candidate
- QMC sequence generation overhead
- Adaptive distribution updates during search
- Amortization across multiple factorization attempts

## 5. Relation to Adaptive Design Methodologies

### 5.1 Adaptive Enrichment in Clinical Trials

The term "adaptive enrichment" originates in clinical trial design, where investigators modify eligibility criteria mid-trial based on interim analyses to concentrate resources on patient subpopulations most likely to benefit from experimental treatments. The validated factorization framework employs analogous principles:[22][29][30][31][32][33][21][23][7]

| **Clinical Trials** | **Factorization Framework** |
|---------------------|----------------------------|
| Patient subpopulations with varying treatment response | Candidate regions with varying factor density |
| Biomarker-guided patient selection | Geometry-guided candidate generation |
| Interim analysis triggers enrollment restriction | Adaptive QMC distribution updates |
| Statistical guarantees on Type I error | Pre-specified significance thresholds |
| Ethical imperative to minimize patient exposure to ineffective treatments | Computational imperative to minimize wasteful candidate checks |

Both domains share the mathematical challenge of **balancing exploration and exploitation**: sufficient initial exploration to identify promising regions, followed by concentrated exploitation of discovered structure.[29][31][21][22][23]

### 5.2 Bayesian Model Averaging and Variable Selection

Advanced adaptive enrichment designs employ Bayesian Model Averaging (BMA) to manage uncertainty across multiple candidate biomarkers, marginalizing over model spaces rather than committing to single predictive variables. The factorization framework's use of **three distinct QMC strategies** parallels this model averaging approach:[21][22][7]

Rather than betting on a single generation strategy, the experimental design systematically tests multiple approaches, identifying strategy-specific strengths and limitations. Future work could formalize this through Bayesian aggregation, weighting strategies by their empirical performance on similar semiprimes.

### 5.3 Variance Reduction in Computational Finance

The QMC-based candidate generation strategy directly parallels variance reduction techniques in computational finance, particularly in high-dimensional option pricing. Both domains seek to estimate quantities (option prices, factor locations) where naive Monte Carlo sampling suffers from high variance and slow convergence.[10][12][34][8][9]

Key shared principles include:

**Importance Sampling**: Concentrating samples in regions of high contribution to the target quantity. For option pricing, this means sampling paths most relevant to payoff; for factorization, this means sampling candidates with elevated factor probability.[34][8][9]

**Control Variates**: Using auxiliary quantities with known expectations to reduce estimator variance. The Z5D scoring mechanism may function analogously, providing control information about factor proximity.[34]

**Stratified Sampling**: Ensuring coverage across critical regions before refining high-density areas. The experimental design's systematic magnitude range and ratio distribution coverage embodies this principle.[8][10][7]

## 6. Computational Implementation and Numerical Robustness

### 6.1 Arbitrary-Precision Integer Arithmetic

A critical implementation decision addresses Python's interaction with numpy's fixed-width integer types. Numpy's int64 type wraps silently upon exceeding 2⁶³-1 ≈ 9.2×10¹⁸, producing nonsensical negative values that invalidate all downstream computation. For semiprimes in the 10³⁰–10⁴⁰ range, this overflow occurs routinely during multiplication operations.[20][35][36][19][7]

The validated framework enforces **Python native integers** throughout the pipeline, leveraging Python's arbitrary-precision implementation that dynamically allocates memory for integers of unbounded magnitude. The pytest test suite explicitly validates type correctness:[19][7]

```python
def test_python_int_output(self):
    corpus = generate_corpus(magnitudes=[20], ratios=[1.0], samples_per_cell=1)
    case = corpus[0]
    assert type(case.N) is int  # Python int, not np.int64
    assert type(case.p) is int
    assert type(case.q) is int
```

This design pattern prevents an entire class of silent numerical corruption failures that would render results meaningless.[19][7]

### 6.2 Numerical Stability and Test Coverage

The 22-test pytest suite provides systematic validation across multiple dimensions:[7]

**Correctness Tests**:
- Semiprime identity: N = p × q for all generated cases
- Primality of factors: p and q are prime
- Magnitude range compliance: 10²⁰ ≤ N ≤ 10⁴⁰

**Numerical Robustness Tests**:
- Integer type enforcement throughout pipeline
- Overflow prevention in arithmetic operations
- Floating-point precision in geometric computations

**Statistical Validity Tests**:
- Z5D score polarity patterns match predictions
- Enrichment bias detection sensitivity
- Variance ratio stability across subsets

The sub-2-second test runtime enables rapid iteration during development while maintaining comprehensive validation. This testing philosophy reflects software engineering best practices: **fast feedback loops with high coverage** prevent regressions and enable confident refactoring.[37][38][39][40][41][7]

### 6.3 Continuous Integration Readiness

The documented CI integration strategy positions the codebase for automated testing on every commit. GitHub Actions workflows enable:[38][39][40][42][7]

- **Matrix testing** across Python versions (3.7-3.11) and operating systems
- **Automated regression detection** blocking merges when tests fail
- **Coverage tracking** with trend analysis over time
- **CodeQL security scanning** preventing vulnerability introduction[43][44][45][46]

This infrastructure transforms research code into maintainable software artifacts suitable for long-term development and community contribution.[39][40][38][7]

## 7. Future Directions and Open Questions

### 7.1 Theoretical Foundations

**Deriving Z5D from First Principles**: The geometric scoring mechanism currently rests on empirical validation. Rigorous theoretical work should derive the 5-dimensional embedding from established number-theoretic principles, potentially connecting to:
- Algebraic number theory and ideal class groups
- Analytic number theory and L-functions
- Geometric number theory and arithmetic geometry

**Bounds and Complexity Analysis**: Proving asymptotic bounds on enrichment factor E(N) as function of semiprime magnitude would clarify scalability limitations. Key questions include:
- Does enrichment maintain E > 4 as N → 10¹⁰⁰?
- Can worst-case complexity be bounded below existing algorithms?
- What semiprime properties (factor ratio, digit patterns) predict enrichment effectiveness?

### 7.2 Algorithmic Extensions

**Hybrid Approaches**: Combining adaptive enrichment with classical methods may yield synergistic improvements:
- Use Z5D scoring to **initialize** Number Field Sieve parameter selection
- Apply enrichment for **pre-screening** before expensive ECM attempts
- Integrate geometric scoring into **parallel factorization** work distribution

**Alternative Geometric Frameworks**: The 5-dimensional choice raises natural questions:
- Would 3D or 7D embeddings perform differently?
- Can optimal dimensionality be determined from semiprime properties?
- Do different geometric spaces (hyperbolic, projective) offer advantages?

**Multi-Strategy Meta-Learning**: The three-strategy experimental design suggests a meta-learning opportunity:
- Train selection policies to choose optimal strategies per semiprime
- Dynamically switch strategies mid-factorization based on progress
- Ensemble multiple strategies with weighted voting

### 7.3 Cryptographic Applications

**RSA Security Implications**: If adaptive enrichment scales to cryptographic magnitudes (10⁶⁰⁰–10¹⁰⁰⁰), the security implications are profound:
- Do existing RSA keys exhibit geometric structure exploitable by Z5D scoring?
- Can key generation be modified to resist enrichment-based attacks?
- What enrichment factors would render 2048-bit RSA insecure?

**Post-Quantum Readiness**: Even if the classical framework doesn't threaten RSA directly, understanding geometric factor density informs post-quantum cryptography design:
- Which lattice-based schemes exhibit analogous geometric vulnerabilities?
- Can enrichment principles strengthen quantum-resistant algorithms?
- Do code-based cryptosystems show similar structure?

### 7.4 Cross-Domain Applications

The geometric scoring and adaptive sampling principles transcend factorization:

**Constraint Satisfaction**: Treating SAT/SMT solving as adaptive sampling over solution spaces with geometric scoring for clause satisfaction
**Optimization**: Applying enrichment to black-box optimization where objective landscape structure is learnable
**Machine Learning**: Using geometric embeddings for feature space exploration in high-dimensional regression
**Protein Folding**: Treating conformational search as adaptive sampling with energy-landscape geometric scoring

## 8. Conclusion

The validated adaptive enrichment framework represents a significant methodological innovation in semiprime factorization, demonstrating that **factorization search spaces exhibit non-uniform geometric structure** amenable to computational exploitation. The empirical results—4.2× enrichment factor with p < 10⁻¹⁰ statistical significance, 38% computational savings, and 58% variance reduction—provide compelling evidence for the asymmetric enrichment hypothesis across the tested 10²⁰–10⁴⁰ magnitude range.[7]

Beyond specific quantitative achievements, the framework introduces three conceptual advances with broader implications:

**1. Geometry as Computational Resource**: The Z5D scoring mechanism demonstrates that **dimensional expansion into geometric spaces** can expose structure invisible in native arithmetic representations, paralleling successful strategies in lattice-based cryptanalysis and quantum algorithms.

**2. Adaptive Sampling for Discrete Problems**: By formulating factorization as **adaptive probability distribution learning** rather than deterministic search, the framework imports powerful techniques from continuous optimization and statistical inference into discrete number theory.

**3. Systematic Empirical Validation**: The rigorous experimental design with pre-specified thresholds, comprehensive testing infrastructure, and multivariate metric validation establishes a **methodological template** for claims about novel computational approaches to hard mathematical problems.

The framework's greatest contribution may ultimately be methodological: it demonstrates how **geometric intuition, quasi-Monte Carlo sampling, and rigorous statistical validation** can converge to produce demonstrable improvements in classically hard computational problems. Whether these improvements scale to cryptographic magnitudes remains an open—and profoundly important—question for future investigation.

As computational number theory continues its evolution from purely theoretical discipline to engineering practice underpinning global infrastructure, methodologies bridging mathematical insight and computational efficiency become increasingly vital. The adaptive enrichment framework, with its validated demonstration of elevated factor density regions, represents a compelling step toward geometry-guided exploration of number-theoretic landscapes.

***

## References

 Pull Request #47: Add pytest integration and CI documentation for adaptive enrichment framework. GitHub: zfifteen/geofac_validation.[7]

 Mergify Documentation. Pytest Integration with CI Insights.[42]

 Helmholtz UQ. Quasi-Monte Carlo Method - Uncertainty Quantification.[13]

 Thall, P. F. (2021). Adaptive Enrichment Designs in Clinical Trials. Annual Review of Statistics.[29]

 WPI Digital Commons. Quasi Monte Carlo (QMC) Methods or Low Discrepancy Algorithms.[9]

 Simon, N., & Simon, R. (2013). Adaptive enrichment designs for clinical trials. PMC - NIH.[23]

 Wikipedia. Quasi-Monte Carlo method.[14]

 GitHub: sea-bass/python-testing-ci. Examples of testing and continuous integration with Python.[37]

 GitHub Docs. Building and testing Python.[38]

 tryexceptpass. Integrating Pytest Results with GitHub.[39]

 pytest-with-eric. Automated Python Unit Testing Made Easy with Pytest and GitHub Actions.[40]

 GitHub Docs. Python queries for CodeQL analysis.[43]

 Stack Overflow. Integer overflow in numpy arrays.[19]

 Canarys Automations. Code Scanning with GitHub and CodeQL.[44]

 NumPy Documentation. Data type promotion in NumPy.[20]

 GitHub Blog. CodeQL zero to hero part 3: Security research with CodeQL.[45]

 YouTube. Resolving Numpy Matrix Multiplication Overflow Issues.[35]

 GitHub Docs. About code scanning with CodeQL.[46]

 Reddit/Python. What's up with uint64 in numpy?[36]

 GitHub: pytest-dev/pytest. The pytest framework.[41]

 Academia.edu. Spectral Geometry and the Hidden Resonance of Primes.[17]

 SSRN. A Novel Algorithm for Factorization of Cryptographic Semiprimes.[1]

 PMC - NIH. An adaptive enrichment design using Bayesian model averaging.[21]

 Reddit/askmath. What algorithm should I use for prime factorisation of like REALLY large numbers.[2]

 AJRCOS. Factorization Algorithm for Semi-primes and the Cryptanalysis of RSA.[3]

 Reddit/badmathematics. Crown Sterling: Factoring semiprimes by looking for geometric patterns.[4]

 PMC - NIH. Adaptive enrichment in biomarker-stratified clinical trial design.[22]

 dpublication. A New Method for Factorizing Semi-Primes Using Simple Polynomials.[5]

 kisonik.una.io. Z5D Prime Predictor: A Critical Red Team Analysis.[16]

 arXiv. A Geometric Square-Based Approach to RSA Integer Factorization.[6]

 University of Waterloo. Quasi-Monte Carlo Multiple Integration.[8]

 Academia.edu. Instant Prime Factorization Through Harmonic Resonance.[18]

 Nature. Prime factorization using quantum annealing and computational algebraic geometry.[27]

 Stanford Digital Repository. Advances in quasi-Monte Carlo.[10]

 Reddit/numbertheory. Resonance-Guided Factorization.[28]

 arXiv. Quasi-Monte Carlo Methods: What, Why, and How?[11]

 math.pku.edu.cn. Monte Carlo and quasi-Monte Carlo methods.[12]

 goudryan.com. A Theory of Resonance.[26]

 SAGE Journals. Adaptive enrichment trial designs using joint modelling.[31]

 Project Euclid. Control Variates for Quasi-Monte Carlo.[34]

 University of Cambridge. Adaptive enrichment trial designs using joint modelling.[32]

 University of Regensburg. Adaptive enrichment trial designs using joint modelling.[33]

Sources
[1] A Novel Algorithm for Factorization of Cryptographic Semiprimes https://papers.ssrn.com/sol3/papers.cfm?abstract_id=5031854
[2] What algorithm should I use for prime factorisation of like REALLY ... https://www.reddit.com/r/askmath/comments/1guajuc/what_algorithm_should_i_use_for_prime/
[3] Factorization Algorithm for Semi-primes and the Cryptanalysis of ... https://journalajrcos.com/index.php/AJRCOS/article/view/458
[4] Crown Sterling: Factoring semiprimes by looking for the ... - Reddit https://www.reddit.com/r/badmathematics/comments/d9je6z/crown_sterling_factoring_semiprimes_by_looking/
[5] [PDF] A New Method for Factorizing Semi-Primes Using Simple Polynomials https://www.dpublication.com/wp-content/uploads/2020/10/16-507.pdf
[6] A Geometric Square-Based Approach to RSA Integer Factorization https://arxiv.org/html/2506.17233
[7] 47 https://github.com/zfifteen/geofac_validation/pull/47
[8] [PDF] Quasi- Monte Carlo Multiple Integration https://sas.uwaterloo.ca/~dlmcleis/s906/chapt6.pdf
[9] [PDF] Quasi Monte Carlo (QMC) Methods or Low Discrepancy Algorithms https://digital.wpi.edu/downloads/v118rd58t
[10] Advances in quasi-Monte Carlo | Stanford Digital Repository https://purl.stanford.edu/md497nt4593
[11] Quasi-Monte Carlo Methods: What, Why, and How? - arXiv https://arxiv.org/html/2502.03644v1
[12] [PDF] Monte Carlo and quasi-Monte Carlo methods https://www.math.pku.edu.cn/teachers/litj/notes/numer_anal/MCQMC_Caflisch.pdf
[13] Quasi-Monte Carlo Method - Uncertainty Quantification - Helmholtz UQ https://dictionary.helmholtz-uq.de/content/quasi_montecarlo_methods.html
[14] Quasi-Monte Carlo method - Wikipedia https://en.wikipedia.org/wiki/Quasi-Monte_Carlo_method
[15] [PDF] Quasi-Monte Carlo Software - arXiv https://arxiv.org/pdf/2102.07833.pdf
[16] Z5D Prime Predictor: A Critical Red Team Analysis https://kisonik.una.io/blog/z5d-prime-predictor-a-critical
[17] Spectral Geometry and the Hidden Resonance of Primes" Author https://www.academia.edu/129125956/_TeslaRack_Spectral_Geometry_and_the_Hidden_Resonance_of_Primes_Author
[18] Instant Prime Factorization Through Harmonic Resonance A Unified ... https://www.academia.edu/129440423/Instant_Prime_Factorization_Through_Harmonic_Resonance_A_Unified_Synthesis_of_Recursive_Geometry
[19] Integer overflow in numpy arrays - python https://stackoverflow.com/questions/1970680/integer-overflow-in-numpy-arrays
[20] Data type promotion in NumPy https://numpy.org/doc/2.3/reference/arrays.promotion.html
[21] An adaptive enrichment design using Bayesian model averaging for ... https://pmc.ncbi.nlm.nih.gov/articles/PMC11639530/
[22] Adaptive enrichment in biomarker-stratified clinical trial design - PMC https://pmc.ncbi.nlm.nih.gov/articles/PMC3980333/
[23] Adaptive enrichment designs for clinical trials - PMC - NIH https://pmc.ncbi.nlm.nih.gov/articles/PMC3769998/
[24] [PDF] arXiv:1305.0941v1 [math.NT] 4 May 2013 https://arxiv.org/pdf/1305.0941.pdf
[25] [PDF] Proposed Proofs For The Riemann Hypothesis, The Collatz ... https://vixra.org/pdf/2503.0176v1.pdf
[26] A Theory of Resonance - The Creation of Time https://goudryan.com/2025/12/19/a-theory-of-resonance/
[27] Prime factorization using quantum annealing and computational ... https://www.nature.com/articles/srep43048
[28] Resonance-Guided Factorization : r/numbertheory - Reddit https://www.reddit.com/r/numbertheory/comments/1i8pzp6/resonanceguided_factorization/
[29] [PDF] Adaptive Enrichment Designs in Clinical Trials https://odin.mdacc.tmc.edu/~pfthall/main/AnnRev-statistics2021_thall_enrichment.pdf
[30] Optimizing subgroup selection in two‐stage adaptive enrichment ... https://onlinelibrary.wiley.com/doi/full/10.1002/sim.8949
[31] Adaptive enrichment trial designs using joint modelling of ... https://journals.sagepub.com/doi/10.1177/09622802241287711
[32] [PDF] Adaptive enrichment trial designs using joint modelling of ... https://www.repository.cam.ac.uk/bitstreams/8dd0b73f-a6fb-4b84-9e4f-95c21148f194/download
[33] [PDF] Adaptive enrichment trial designs using joint modelling of ... https://epub.uni-regensburg.de/77768/1/burdon-et-al-2024-adaptive-enrichment-trial-designs-using-joint-modelling-of-longitudinal-and-time-to-event-data.pdf
[34] Control Variates for Quasi-Monte Carlo - Project Euclid https://projecteuclid.org/journals/statistical-science/volume-20/issue-1/Control-Variates-for-Quasi-Monte-Carlo/10.1214/088342304000000468.pdf
[35] Resolving Numpy Matrix Multiplication Overflow Issues - YouTube https://www.youtube.com/watch?v=YjfVSmEEViY
[36] What's up with uint64 in numpy? - Python - Reddit https://www.reddit.com/r/Python/comments/urwoto/whats_up_with_uint64_in_numpy/
[37] Examples of testing and continuous integration with Python ... - GitHub https://github.com/sea-bass/python-testing-ci
[38] Building and testing Python - GitHub Docs https://docs.github.com/actions/guides/building-and-testing-python
[39] Unit testing Python code using Pytest + GitHub Actions - YouTube https://www.youtube.com/watch?v=0aEJBygCn5Q
[40] Automated Python Unit Testing Made Easy with Pytest and GitHub ... https://pytest-with-eric.com/integrations/pytest-github-actions/
[41] The pytest framework makes it easy to write small tests, yet ... - GitHub https://github.com/pytest-dev/pytest
[42] Pytest Integration with CI Insights - Mergify Documentation https://docs.mergify.com/ci-insights/test-frameworks/pytest/
[43] Python queries for CodeQL analysis - GitHub Docs https://docs.github.com/en/code-security/reference/code-scanning/codeql/codeql-queries/python-built-in-queries
[44] Code Scanning with GitHub and CodeQL - Canarys Automations https://ecanarys.com/secure-your-code-with-github-code-scanning-and-codeql/
[45] CodeQL zero to hero part 3: Security research with CodeQL https://github.blog/security/vulnerability-research/codeql-zero-to-hero-part-3-security-research-with-codeql/
[46] About code scanning with CodeQL - GitHub Docs https://docs.github.com/code-security/code-scanning/introduction-to-code-scanning/about-code-scanning-with-codeql
[47] [PDF] optimized adaptive enrichment designs for multi-arm trials: learning ... https://biostats.bepress.com/cgi/viewcontent.cgi?article=1295&context=jhubiostat
[48] zfifteen/emergent-factorization-engine - GitHub https://github.com/zfifteen/emergent-factorization-engine
[49] [PDF] Optimal Interpolation of Spatially Discretized Geodetic Data http://scec.ess.ucla.edu/~zshen/publ/bssa15shen.pdf
[50] [PDF] Comparison of conditioning factors classification criteria in large ... https://nhess.copernicus.org/preprints/nhess-2024-29/nhess-2024-29.pdf
[51] [PDF] Comparison of conditioning factor classification criteria in large ... https://nhess.copernicus.org/articles/25/183/2025/nhess-25-183-2025.pdf
[52] Validation of meter-scale surface faulting offset measurements from ... https://pubs.geoscienceworld.org/gsa/geosphere/article/11/6/1884/132327/Validation-of-meter-scale-surface-faulting-offset
[53] The Geometric Eye of Prime Factorization - Robert Edward Grant https://robertedwardgrant.com/the-geometric-eye-of-prime-factorization/
[54] [PDF] Science at the environmental research station Schneefernerhaus ... https://elib.dlr.de/189714/1/Science%20at%20the%20environmental%20research%20station%20Schneefernerhaus%20%20Zugspitze.pdf
[55] gdal/NEWS-1.x.md at master - GitHub https://github.com/OSGeo/gdal/blob/master/NEWS-1.x.md
[56] Lab 2: QMC Basics — QMCPACK Manual documentation https://qmcpack.readthedocs.io/en/develop/lab_qmc_basics.html
[57] https://raw.githubusercontent.com/microsoft/JARVIS... https://raw.githubusercontent.com/microsoft/JARVIS/2c19142b56663a54b2c85f8622b38f98c5b2580f/server/data/p0_models.jsonl
[58] Diff - 6aa7eec5002756f5398774a35fb9d985e15a4573 https://gerrit.openbmc.org/plugins/gitiles/openbmc/openbmc/+/6aa7eec5002756f5398774a35fb9d985e15a4573%5E!/
[59] Evaluating a quantum-classical quantum Monte Carlo algorithm with ... https://link.aps.org/doi/10.1103/PhysRevResearch.6.043063
[60] Pull requests · zfifteen/geofac_validation · GitHub https://github.com/zfifteen/geofac_validation/pulls
[61] [PDF] 9 Hirsch-Fye Quantum Monte Carlo Method for Dynamical Mean ... https://www.cond-mat.de/events/correl11/manuscript/Bluemer.pdf
[62] Improved Experiment Design · Issue #41 · zfifteen/geofac_validation https://github.com/zfifteen/geofac_validation/issues/41
[63] A two-stage patient enrichment adaptive design in phase II oncology ... https://www.sciencedirect.com/science/article/abs/pii/S1551714413001985
[64] [PDF] Evaluating a quantum-classical quantum Monte Carlo algorithm with ... https://knowledge.uchicago.edu/record/13807/files/PhysRevResearch.6.043063.pdf
