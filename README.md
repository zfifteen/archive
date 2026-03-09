# Archive Classification

This README classifies each top-level project in this archive by inferred archival reason, based on repo-local artifacts (`README.md`, docs, manifests, and status notes). A project may appear in multiple tables when evidence supports multiple reasons.

## Classification Rubric

- **Falsified/Invalidated hypothesis**: Core thesis, claimed uplift, or validation gate was explicitly falsified or closed out as non-viable.
- **Limited/No practical utility**: Project is highly exploratory, narrow-scope, incomplete, or difficult to operationalize as documented.
- **Task accomplished, no longer needed**: Project appears to have met its immediate objective (experiment, scaffold, one-off tracking, or prototype cycle).
- **Other**: Archival driver does not cleanly fit above (for example: superseded/consolidated, sensitive/private operational context).

## Falsified/Invalidated Hypothesis

| Project | Description |
|---|---|
| [qmc_rsa-main](./qmc_rsa-main/) | QMC-vs-MC RSA sampling experiment suite with bias-mode analysis and statistical benchmarks. README explicitly documents θ′-biased QMC as falsified (reduced unique candidates). |
| [wave-crispr-signal](./wave-crispr-signal/) | CRISPR scoring and disruption-analysis toolkit with CLI/API surfaces and external comparator gates. Validation docs record authoritative Gate v3 `NO-GO` and thesis closeout. |
| [spectral-disruption-profiler-main](./spectral-disruption-profiler-main/) | CRISPR signal-processing SaaS prototype with synthetic-data validation and bootstrap analysis. Current reported synthetic lift confidence interval includes zero and required external datasets remain pending. |

## Limited/No Practical Utility

| Project | Description |
|---|---|
| [ArctanGeodesic-main](./ArctanGeodesic-main/) | Standalone Python library for arctan/geodesic identities and related number-theory mappings. Scope is mathematically specialized and oriented to research-style validations rather than broad production utility. |
| [FactorGoL-main](./FactorGoL-main/) | GPU-accelerated Conway’s Game of Life factorization experiment claiming resonance-based semiprime signals. Problem framing is highly niche and depends on nonstandard factorization assumptions. |
| [adaptive_lattice_sampling_engine-main](./adaptive_lattice_sampling_engine-main/) | Prototype adaptive lattice/QMC engine positioned for variance-sensitive simulation workloads. Repo appears as a concept-level package with limited operational integration context. |
| [cognitive-number-theory-main](./cognitive-number-theory-main/) | Theoretical curvature/distortion framework for integer-sequence diagnostics and related Z-framework primitives. Primarily conceptual/research-oriented with limited direct deployment pathway. |
| [distortion_mapping_analytics-main](./distortion_mapping_analytics-main/) | Python analytics toolkit applying curvature/distortion metrics for sequence classification and anomaly detection. Utility appears constrained by framework-specific assumptions and research framing. |
| [geofac](./geofac/) | Spring Boot/Shell geometric ranking plus arithmetic certification factorization pipeline for challenge semiprimes. Purpose and validation model are narrow to a specific experimental factoring objective. |
| [geofac-137524771864208156028430259349934309717-main](./geofac-137524771864208156028430259349934309717-main/) | Target-specific “wide net” repository tuned to a single 127-bit challenge semiprime with zero-knowledge constraints. Extremely specialized to one campaign target. |
| [golden_ratio_geodesic_optimizer-main](./golden_ratio_geodesic_optimizer-main/) | Golden-ratio geodesic sampling library with symbolic/high-precision validation hooks. README characterizes behavior as empirical/no-proof and niche to the Z-framework research line. |
| [prime-gap-lognormal-main](./prime-gap-lognormal-main/) | Empirical prime-gap distribution investigation repository focused on technical specs and planned proof-of-concept scripts. Current state is documentation-first with implementation intentionally deferred. |
| [transect](./transect/) | Zero-handshake encrypted messaging concept inspired by military COMSEC patterns. Ambitious protocol claims and niche deployment assumptions limit immediate practical adoption in this archive context. |
| [unified-framework](./unified-framework/) | Z5D geodesic prime toolkit for cross-domain invariants and nth-prime prediction workflows. Utility is concentrated in a specialized mathematical research ecosystem. |
| [z-sandbox](./z-sandbox/) | Broad research sandbox for geometric factorization/QMC experiments across multiple methods. High exploratory breadth and low product focus reduce direct practical utility. |
| [z5d-prime-predictor](./z5d-prime-predictor/) | Cross-language nth-prime predictor with calibrated estimator and empirical big-n sweeps. README notes empirical/non-proof guarantees beyond benchmark grids, limiting operational confidence for critical use. |
| [z_key_gen](./z_key_gen/) | Apple-hardware-focused RSA key generation pipeline built on Z5D predictor assumptions and native acceleration. Platform-specific and method-specific constraints narrow general applicability. |

## Task Accomplished, No Longer Needed

| Project | Description |
|---|---|
| [amx-lab](./amx-lab/) | Apple Silicon AMX research lab with agent definitions and experiment structure for matrix-heavy optimization. Functions as a focused exploration/reference repository whose immediate setup objective is complete. |
| [burn-notice](./burn-notice/) | Provider/model-organized prompt-engineering scaffold with shared schemas and taxonomy metadata. Appears intended as a reusable baseline scaffold that has already been established. |
| [dirichlet-llm-shootout-main](./dirichlet-llm-shootout-main/) | Comparative LLM experiment repo converting Dirichlet-theorem source material into reproducible code/plot outputs. Structured as a bounded shootout exercise with defined run/evaluation layout. |
| [geofac_validation](./geofac_validation/) | Geofac-Z5D validation campaign repository documenting coverage paradox findings and gradient-zoom pivot. Captures a completed validation cycle and resulting decision artifacts. |
| [geometric-prime-resonance-main](./geometric-prime-resonance-main/) | Theta contour-map visualization experiment for periodic bias inspection across scales. Packaged as a bounded experiment kit with generated artifacts and summaries. |
| [math](./math/) | Collection of small math experiments (e.g., advection-diffusion demo, prime-gap moment analyses) with local outputs/scripts. Serves as one-off experimental workspace rather than an ongoing product codebase. |
| [playground](./playground/) | Scratch workspace with whiteboard notes, agent instructions, snapshots, and cache/project scaffolding. Primarily an ideation sandbox that fulfilled exploratory use. |
| [qmc_rsa-main](./qmc_rsa-main/) | RSA candidate-sampling experiment suite that includes completed falsification runs for θ′ bias. Key investigation objective (test and resolve bias claim) is documented and concluded. |
| [va-benefits-tracker](./va-benefits-tracker/) | Private personal VA-benefits tracking repository for status, applications, and entitlements. Acts as an operational tracking artifact rather than active software development work. |
| [wave-crispr-signal](./wave-crispr-signal/) | CRISPR toolkit with explicit gate-driven closeout documentation. The current thesis is explicitly closed (`NO-GO`) for incremental continuation. |

## Other

| Project | Description |
|---|---|
| [geofac-137524771864208156028430259349934309717-main](./geofac-137524771864208156028430259349934309717-main/) | Single-target geofac variant focused on one challenge semiprime and custom windowing/QMC settings. Best treated as a campaign-specific branch artifact distinct from durable project lines. |
| [yolanda-health-manager](./yolanda-health-manager/) | Local health-management app prototype/specification bundle with webpack frontend scaffolding and medical-data-oriented build spec/context files. Contains sensitive operational context and appears better archived than actively evolved here. |
| [z-sandbox](./z-sandbox/) | Umbrella exploratory repository spanning multiple geometric factorization research threads. Overlaps with narrower successor/specialized repos in this archive. |
