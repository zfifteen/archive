# prime-gap-lognormal

Empirical exploration of how gaps between consecutive primes behave, with evidence that their distributions are **lognormal** and their sequences exhibit **strong autocorrelation**, challenging classical exponential and independence heuristics for prime gaps.

## Motivation

Classical analytic number theory suggests that the average size of a prime gap near a prime $$p$$ is about $$\log p$$, and many probabilistic heuristics treat gaps as if they were drawn from an exponential distribution with this mean, often assuming independence between successive gaps.

This repository collects a set of tightly scoped, reproducible gists whose goal is to probe those assumptions empirically:  
- Do finite-range prime gaps actually look exponential when scrutinized with modern statistical tools?  
- Is there a more accurate distributional model (e.g. lognormal) for gaps across scales?  
- Are consecutive gaps effectively independent, or is there measurable autocorrelation over multiple lags?  

The project is deliberately structured so that each claim can eventually be backed by a small, self-contained executable "proof-of-concept" script, rather than informal plots or anecdotes.

## High-level goals

This repository aims to:

- Provide empirical evidence that **prime gaps are better modeled by lognormal distributions** (after suitable banding by scale) than by exponentials.
- Show that **gap sequences exhibit statistically significant autocorrelation** at small lags, contradicting independence assumptions often used in heuristic models.  
- Offer clear, reproducible technical specifications (`TECH_SPEC_*.md` gists) that can be implemented as standalone scripts once code is added.  
- Serve as a structured staging area on the path from "playground experiments" to something approaching a computational paper.  

At this stage, the repository focuses on **specification and design**: the technical specs describe exactly what future code should compute, how it should test hypotheses, and what constitutes success.

## Conceptual background

### Prime gaps in brief

A prime gap is the difference between two consecutive primes, for example the gap between 11 and 13 is 2, and the gap between 89 and 97 is 8.

From the prime number theorem one knows that the **average** gap near a large prime $$p$$ is about $$\log p$$, but individual gaps can be much smaller or much larger than this average, and they fluctuate in a complicated way.

Classical heuristics often model gaps as if they were drawn independently from an exponential distribution with mean $$\log p$$, which is a natural choice if one treats "a number being prime" as roughly a memoryless Bernoulli process with probability about $$1/\log p$$.

### Why lognormal?

A lognormal distribution is one whose logarithm is normally distributed; it is ubiquitous in settings where **multiplicative random effects** accumulate, such as in certain models of financial returns or multiplicative growth processes.

The central claim behind `prime-gap-lognormal` is that **prime gaps, when grouped into appropriate scale bands and examined empirically, follow lognormal rather than exponential distributions**, with strong statistical support from normality tests on $$\log(\text{gap})$$ and Q–Q plots.

### Why autocorrelation?

Independence of successive gaps is a strong assumption that underlies many simple probabilistic models of primes.

If gap sequences exhibit **autocorrelation**—for example, if large gaps tend to be followed by somewhat larger-than-average gaps, or if there is visible structure at lags 1–50—then the effective "random model" for primes is more structured than a simple memoryless process. This repository aims to make that structure explicit through time-series style analysis of gap sequences.

## Repository layout

The repository is organized to separate **narrative**, **specification**, and eventually **code**:

- `REPO_STORY.md`  
  - Narrative explanation of the discovery process, empirical surprises, and how the lognormal + autocorrelation picture emerged from experiments.  

- `PLAYGROUND_REFERENCES.md`  
  - Pointers into external playground or experimental repositories where raw exploratory code and notebooks currently live (e.g. prime sieves, gap extraction utilities, distribution-fitting helpers).  

- `gists/`  
  - Home of **reproducible proof-of-concept gists**, each centered around a specific claim.  
  - Each gist has a **technical specification** describing the experiment, inputs, statistical tests, visualizations, and success criteria.  

- `applications/`  
  - Separate application-level scenarios that may eventually **consume** the statistical structure uncovered here (e.g. cryptographic diagnostics, toy RSA-key sanity checks).  
  - At present, this is exploratory and orthogonal to the core gap-distribution work.  

- `.github/agents/`  
  - Specifications for automation or AI agents that can assist in turning the technical specs into concrete, reproducible implementations.  

As of now, the core logic is *specified*, not implemented; the specs are designed so that code can be dropped in later without redesigning the scientific workflow.

## Gists: formalized experiments

Each gist under `gists/` is intended to be a **minimal, executable scientific unit**: one discovery, one script, one story.

### Lognormal structure (`gists/lognormal_structure`)

This gist is centered on the claim:

> **Prime gaps, grouped into logarithmic scale bands, follow lognormal distributions with strong statistical support across all bands.**

The associated technical specification (`TECH_SPEC_LOGNORMAL_STRUCTURE.md`) defines:

- The **input scale range** (e.g. from $$10^6$$ to $$10^8$$, configurable) and how to partition primes into six log-spaced bands by $$\log_{10} p$$.  
- The extraction of consecutive prime gaps in each band, with data-quality rules such as enforcing minimum sample sizes and forbidding zero gaps (to keep $$\log(\text{gap})$$ well-defined).  
- Fitting procedures for the lognormal model via maximum likelihood on $$\log(\text{gap})$$, including parameter estimates, confidence intervals, and (optionally) method-of-moments cross-checks.  
- **Normality tests** (e.g. Shapiro–Wilk, Anderson–Darling) applied to the log-transformed gaps, along with clear success thresholds (p-values) and reporting formats.  
- **Visualization requirements**, especially Q–Q plots that should reveal near-linear behavior if the lognormal model is appropriate.  

The goal is to eventually have a single script in this gist that, when run, produces both the statistical tables and the plots that collectively serve as a "computational proof-of-concept" for lognormal gap distributions.

### Autocorrelation (`gists/autocorrelation`)

This gist focuses on the temporal structure of gap sequences:

> **Prime gap sequences show statistically significant autocorrelation at multiple lags, particularly lag 1, across multiple scale bands.**

The `TECH_SPEC_AUTOCORRELATION.md` file specifies:

- The same **prime-scale banding** scheme as the lognormal gist, so band comparisons are meaningful across experiments.  
- Construction of the raw gap sequences within each band and computation of the **autocorrelation function (ACF)** for lags in a specified range (e.g. 1–50).  
- Use of **joint and marginal significance tests** for autocorrelation, such as Ljung–Box tests over multiple lags and theoretical confidence bands derived from large-sample approximations.  
- **Visualization requirements** including ACF stem plots with confidence bands, band-by-band comparison grids, and potentially a lag-1 heatmap across bands.  
- Concrete **validation criteria** (e.g. thresholds on lag-1 autocorrelation and Ljung–Box p-values) that define what it means for "strong autocorrelation" to be convincingly demonstrated.  

The intent is that this gist will ultimately contain a self-contained script whose outputs can be inspected both numerically and visually to assess the presence of autocorrelation.

## Relationship to classical theory

This project does **not** claim any theorems about primes; it operates strictly in the empirical domain, over finite ranges that are large but bounded.  

However, the way gaps behave over those ranges is directly relevant to classical questions:

- The prime number theorem implies the **average gap** near $$p$$ behaves like $$\log p$$, but it does not prescribe the full distribution of gaps or their dependence structure.
- Heuristic models inspired by Cramér treat primes as independent "coin flips" with success probability roughly $$1/\log n$$, which leads naturally to exponential gap models and independence assumptions.

If empirical data instead aligns more closely with **lognormal** gap distributions and reveals **persistent autocorrelation**, then the classical "coin-flip with exponential gaps" story may require refinement when used as a practical model over accessible ranges.

This repository is designed to make such empirical tensions explicit in a way that is easy to audit, rerun, and extend.

## Current status and future work

At the time of this README:

- The **conceptual design and technical specifications** for key experiments (lognormal structure, autocorrelation) are written and versioned under `gists/`.  
- **Implementation code is intentionally not yet included**; the repository serves as a specification and documentation hub, with a clear plan for future executables.  

Planned next steps include:

- Implementing minimal, dependency-light Python scripts for each gist that adhere strictly to their respective `TECH_SPEC_*.md` documents.  
- Introducing a small "results" section or directory where canonical plots and summary tables can live once computations are run.  
- Tightening the bridge between this repository and any external playground repos, potentially migrating stable components (prime sieves, gap extractors, plotting utilities) into a shared library.  

Contributions, once code exists, will likely focus on:

- Extending the numeric ranges and band definitions.  
- Stress-testing the statistical methodology (alternative tests, robustness checks).  
- Exploring additional structures in gap sequences (e.g. higher-order dependencies, conditional distributions given previous gaps).
