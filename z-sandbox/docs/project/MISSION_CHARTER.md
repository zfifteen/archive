# Mission Charter: 10-Point Deliverable Standard

## Overview

This document defines the **10-Point Mission Charter** that governs all deliverables (text, code, data, plans, specifications, reports) produced in the z-sandbox repository. Every deliverable must explicitly address each of the 10 charter elements to ensure rigor, reproducibility, and alignment with project goals.

**Research Philosophy:** z-sandbox focuses on understanding and refining existing techniques through empirical validation, not claiming breakthroughs or generalizations beyond validated scope. We prioritize reproducibility, honest limitation documentation, and incremental improvements over grand claims.

## Charter Authority

**Project Owner:** Big D / DAL III  
**Enforcement:** All assistants, agents, and contributors  
**Scope:** All outputs marked as deliverables (specs, PRs, code diffs, research notes, experimental logs, runbooks, designs, plans)  
**Exclusions:** Ephemeral chat not marked as deliverable

---

## The 10 Charter Elements

Every deliverable **MUST** include a clearly labeled section for each element below:

### 1. First Principles
**Requirement:** Document the foundational axioms, definitions, and units underlying the deliverable.

**Must Include:**
- Mathematical axioms (e.g., Z = A(B/c), κ(n) = d(n) * ln(n+1) / e²)
- Physical constants and their values
- Units of measurement and coordinate systems
- Core definitions and terminology
- Fundamental assumptions

**Example:**
```
## First Principles
- Z-Framework Axiom: Z = A(B/c) where c = e² (invariant)
- Curvature: κ(n) = d(n) * ln(n+1) / e²
- Geometric Resolution: θ'(n,k) = φ * ((n mod φ) / φ)^k, k ≈ 0.3
- Units: All error measurements in ppm (parts per million)
- Precision: mpmath with tolerance < 1e-16
```

---

### 2. Ground Truth & Provenance
**Requirement:** Document what was tested, by whom, when, how, and trace all external sources.

**Must Include:**
- Test subject/dataset description
- Executor identity (agent, user, CI system)
- Timestamp (ISO 8601 format with timezone)
- Method/procedure followed
- External sources with full citations:
  - Author(s)
  - Title
  - Publisher/Domain
  - Stable locator (URL, DOI, ISBN)
  - Access date/time (ISO 8601)

**Example:**
```
## Ground Truth & Provenance
**Tested:** Geometric resonance factorization on 127-bit semiprime
**Executor:** User (Big D)
**Timestamp:** 2025-11-06T00:00:00Z (initial success), 2025-11-07 (platform issue documented)
**Method:** Dirichlet kernel filtering with golden-ratio QMC k-sampling
**Platform:** macOS M1 Max (ARM64)
**Implementation:** Java with BigDecimal (platform-independent)
**Validation Status:** Works on 1 example on Java; Python version has platform dependencies

**Sources:**
- Dirichlet Kernel. Wikipedia.
  https://en.wikipedia.org/wiki/Dirichlet_kernel (Accessed: 2025-11-09)
- Van der Corput sequence. Wikipedia.
  https://en.wikipedia.org/wiki/Van_der_Corput_sequence (Accessed: 2025-11-09)
- BigDecimalMath library. https://github.com/eobermuhlner/big-math
- Internal implementations:
  - Java (working): src/main/java/org/zfifteen/sandbox/GeometricResonanceFactorizer.java
  - Python (reference, x86_64 only): results/geometric_resonance_127bit/method.py
  - Platform issue analysis: articles/python-to-java-switch.md
```

---

### 3. Reproducibility
**Requirement:** Provide exact steps, configurations, seeds, versions, and environment details to enable independent reproduction.

**Must Include:**
- Exact commands with parameters
- Software versions (Python, Java, libraries)
- Hardware specifications (if relevant)
- Random seeds and initialization states
- Environment variables
- Configuration files (or inline configs)
- Expected output characteristics
- Tolerance thresholds for validation

**Example:**
```
## Reproducibility

**CRITICAL: Platform Dependency**
- **Python Implementation:** Works on x86_64 Linux only; **FAILS on ARM64 macOS** due to IEEE 754 float differences in QMC sampling
- **Java Implementation:** Platform-independent; works on x86_64, ARM64, etc.
- **This Platform:** macOS Apple M1 Max (ARM64) → **Use Java**

**Environment (Java - Working on This Platform):**
- Java 17+
- BigDecimalMath (ch.obermuhlner.math.big)
- Gradle 8.x
- Platform: macOS (Apple M1 Max, ARM64) or any JVM-compatible platform

**Commands (Java):**
```bash
./gradlew build
java -cp build/libs/z-sandbox.jar \
  org.zfifteen.sandbox.GeometricResonanceFactorizer \
  137524771864208156028430259349934309717 \
  --mc-digits=240 --samples=3000 --m-span=180 --J=6 --threshold=0.92
```

**Expected Output:**
- Factors found: p = 10508623501177419659, q = 13086849276577416863
- Runtime: ~3 minutes (hardware dependent)
- Deterministic across platforms

**Validation:**
```bash
# Verify factors (Java)
./gradlew test --tests "*GeometricResonance*"

# Python reference (x86_64 Linux only - use Docker if needed):
docker run --platform linux/amd64 -v $(pwd):/work -w /work \
  python:3.12.3-slim bash -c \
  "pip install mpmath==1.3.0 && cd results/geometric_resonance_127bit && python3 method.py"
```

**Platform Issue Documentation:**
- See `articles/python-to-java-switch.md` for full analysis
- See `docs/validation/reports/2025-11-07_GEOMETRIC_RESONANCE_REPRODUCTION_ATTEMPT.md` for failed ARM64 attempts
```

---

### 4. Failure Knowledge
**Requirement:** Document edge cases, known bugs, limitations, diagnostics, and mitigations.

**Must Include:**
- At least one explicit failure mode
- At least one diagnostic method
- At least one mitigation strategy
- Known bugs and their workarounds
- Limitations and boundary conditions
- Postmortems from past failures (if applicable)

**Example:**
```
## Failure Knowledge

**Failure Mode 1: Numerical Overflow**
- **Condition:** n > 10^2048 with precision < 4096 bits
- **Symptom:** mpmath raises OverflowError or silent precision loss
- **Diagnostic:** Check `mpmath.mp.dps` before computation; verify result magnitude
- **Mitigation:** Increase `dps` to 2 * log10(n) + safety_margin (500 bits)

**Failure Mode 2: Non-convergence**
- **Condition:** k parameter outside [0.25, 0.35] range
- **Symptom:** Iterations exceed 10^7 without converging
- **Diagnostic:** Monitor residual norm at each iteration; check for oscillation
- **Mitigation:** Restart with k=0.30 (empirically optimal); enable adaptive stepping

**Known Limitations:**
- Method validated only for semiprimes; behavior on general composites undefined
- Performance degrades for n with small prime factors (< 1000)
- Requires high-precision arithmetic; not suitable for embedded systems
```

---

### 5. Constraints
**Requirement:** Enumerate legal, ethical, safety guardrails and compliance notes.

**Must Include:**
- Legal constraints (licenses, patents, export controls)
- Ethical considerations
- Safety requirements
- Compliance mechanisms
- Data privacy and security requirements
- Access controls

**Example:**
```
## Constraints

**Legal:**
- Code licensed under terms specified in LICENSE file (to be added)
- RSA challenge numbers are public domain; no copyright restrictions
- No patented algorithms used; all methods are original research or public domain

**Ethical:**
- Research is purely academic; no intent to break active cryptographic systems
- Only historical RSA challenges (already factored or retired) are targeted
- Results shared openly for research community benefit

**Safety:**
- No execution of untrusted code from external sources
- All random number generation uses cryptographically secure seeds when applicable
- Secrets (if any) stored in environment variables, never in code or logs

**Compliance:**
- TRANSEC protocol followed for sensitive communications (see docs/security/TRANSEC.md)
- No personal data collected or processed
- All external dependencies vetted for known vulnerabilities (see security/)
```

---

### 6. Context
**Requirement:** Specify who, what, when, where, why this deliverable matters.

**Must Include:**
- Stakeholders and audience
- Problem being addressed
- Timeline and schedule constraints
- Location/environment context
- Motivation and business value
- Dependencies on other work

**Example:**
```
## Context

**Who:** Project Owner (Big D / DAL III), Claude Code assistant
**What:** Analysis and refinement of geometric resonance factorization for 127-bit targets
**When:** November 2025; exploratory research phase
**Where:** z-sandbox repository, local development environment
**Why:**
- Understand mechanics of Dirichlet kernel filtering approach
- Document current limitations honestly (single test case, unknown generalization)
- Identify optimization opportunities (closed-form kernel, parallelization)
- Establish baseline before testing on additional targets
- Research project, not claiming cryptographic breakthrough

**Dependencies:**
- Java implementation (production): src/main/java/org/zfifteen/sandbox/GeometricResonanceFactorizer.java
- Python implementation (reference, x86_64 only): results/geometric_resonance_127bit/method.py
- Analysis documentation: docs/methods/geometric/GEOMETRIC_RESONANCE_ANALYSIS.md
- Platform issue documentation: articles/python-to-java-switch.md
```

---

### 7. Models & Limits
**Requirement:** Document assumptions, validity ranges, and break points.

**Must Include:**
- Mathematical models used
- Assumptions underlying models
- Validity ranges (input domains)
- Known break points and singularities
- Approximation errors and bounds
- Model selection rationale

**Example:**
```
## Models & Limits

**Model:** Geometric Resonance with Dirichlet Kernel Filtering
- **Form:** p_hat = √N · exp(-π·m/k), filtered by |D_J(θ)| ≥ threshold
- **Assumptions:**
  - N is a balanced semiprime (p ≈ q, ratio within 2-3×)
  - True factors lie within explored neighborhood of √N
  - Dirichlet kernel effectively filters non-factors (empirical, not proven)
  - Golden ratio QMC provides adequate k-coverage

**Validated Range:**
- **Input:** Exactly one 127-bit semiprime tested (N = 1.375...×10³⁸)
- **Generalization:** UNKNOWN—no testing on other 127-bit targets
- **Parameters:** J=6, m_span=180, k∈[0.25,0.45], threshold=0.92

**Known Limitations:**
- Validated on single test case only
- Parameters may be overfit to this specific N
- Success rate on random 127-bit semiprimes: UNKNOWN
- Behavior on unbalanced semiprimes (p≪q): UNKNOWN
- Scaling to larger bit sizes: NOT CLAIMED

**Break Points:**
- N with highly unbalanced factors (p/q > 10): Likely fails (untested)
- Smaller targets (64-bit, 80-bit): Unknown if method works
- Larger targets (200-bit+): Unknown, not claiming success

**Current Status:** Promising research technique; needs validation on multiple targets
```

---

### 8. Interfaces & Keys
**Requirement:** List commands, required permissions, environment variables, secrets handling, and I/O paths.

**Must Include:**
- Command-line interfaces and arguments
- API endpoints (if applicable)
- Required permissions and access controls
- Environment variables
- Secrets handling and redaction policy
- Input/output file paths
- Configuration file locations
- Network interfaces (if applicable)

**Example:**
```
## Interfaces & Keys

**Command-Line Interface (Java - Production):**
```bash
java -cp build/libs/z-sandbox.jar \
  org.zfifteen.sandbox.GeometricResonanceFactorizer <N> [OPTIONS]

Options:
  --mc-digits=INT       Precision in decimal digits (default: 240)
  --samples=INT         QMC k-samples (default: 3000)
  --m-span=INT         Scan radius around m0 (default: 180)
  --J=INT              Dirichlet half-width (default: 6)
  --threshold=FLOAT    Normalized amplitude gate (default: 0.92)
  --k-lo=FLOAT         Min k-value (default: 0.25)
  --k-hi=FLOAT         Max k-value (default: 0.45)
```

**Command-Line Interface (Python - Reference, x86_64 Linux only):**
```bash
# WARNING: Fails on ARM64 macOS due to platform-specific float differences
# Use Docker with linux/amd64 platform or run on x86_64 Linux natively
cd results/geometric_resonance_127bit
python3 method.py

# No command-line arguments (configuration hardcoded for reproducibility)
# Outputs to stdout: p and q on separate lines
```

**Environment Variables:**
- `JAVA_HOME`: Required for Gradle builds
- `PYTHONPATH`: Must include `python/` for test imports (Python reference only)
- No sensitive configuration (all public research)

**I/O Paths:**
- **Java Input:** Command-line argument (N)
- **Java Output:** Stdout (factors), results/legit_<timestamp>/config.json, factors.txt, provenance.txt
- **Python Input:** Hardcoded N in method.py (reference implementation)
- **Python Output:** Stdout (p, q), run_metrics.json

**Permissions:**
- Read: All repository files
- Write: `results/`, `logs/`, `build/` (auto-created)
- Execute: Gradle tasks, Java classes, Python scripts (reference)

**Secrets Handling:**
- No secrets involved (public research on public numbers)
- No API keys, no database credentials
- All results fully public and reproducible

**Platform Compatibility:**
- **Java:** All platforms (x86_64, ARM64, others) - fully reproducible
- **Python:** x86_64 Linux only - ARM64 has IEEE 754 differences (see articles/python-to-java-switch.md)
```

---

### 9. Calibration
**Requirement:** State threshold values, rationale, tuning method, and validation checks.

**Must Include:**
- Calibrated parameters and their values
- Rationale for chosen values
- Tuning methodology
- Validation checks performed
- Sensitivity analysis
- Tolerance specifications
- Prior distributions (for Bayesian methods)

**Example:**
```
## Calibration

**Parameter: J (Dirichlet Half-Width)**
- **Value:** 6
- **Rationale:** Chosen empirically for successful run; theoretical basis unknown
- **Tuning Method:** NOT YET PERFORMED—single successful configuration
- **Validation:** NEEDED—should test J ∈ {4, 5, 6, 7, 8} on multiple targets
- **Sensitivity:** UNKNOWN—ablation study required

**Parameter: m_span (Scan Radius)**
- **Value:** 180
- **Rationale:** Chosen empirically; provides 361 integer m-values to explore
- **Tuning Method:** NOT YET PERFORMED—may be oversized
- **Validation:** NEEDED—should test {60, 90, 120, 180} on multiple targets
- **Sensitivity:** UNKNOWN—may be reducible for performance gain

**Parameter: threshold (Dirichlet Gate)**
- **Value:** 0.92 (normalized)
- **Rationale:** Empirically chosen; keeps ~25% of candidates
- **Tuning Method:** NOT YET PERFORMED—may be overfit to single example
- **Validation:** NEEDED—should sweep [0.85, 0.95] to find optimal
- **Sensitivity:** UNKNOWN—higher threshold may improve precision/recall tradeoff

**Parameter: k_range**
- **Range:** [0.25, 0.45]
- **Rationale:** Empirically chosen; no theoretical justification
- **Tuning Method:** NOT YET PERFORMED
- **Validation:** NEEDED—why not [0.30, 0.40] or [0.20, 0.50]?
- **Sensitivity:** UNKNOWN

**Calibration Status:**
- ⚠️ **WARNING:** All parameters are from single successful run
- ⚠️ **RISK:** May be overfit to N = 137524771864208156028430259349934309717
- ⚠️ **NEEDED:** Multi-target validation and ablation study

**Proposed Calibration Protocol:**
```bash
# Test parameter sensitivity on 10 different 127-bit targets
python3 tests/test_geometric_resonance_ablation.py \
  --targets=10 \
  --vary=J,m_span,threshold \
  --output=calibration_report.json
```
```

---

### 10. Purpose
**Requirement:** Define goals, success criteria, values, and how success is measured.

**Must Include:**
- Primary goals and objectives
- Success criteria (quantitative)
- Success metrics
- Verification procedures
- Value proposition
- Acceptance thresholds
- Measurement methodology

**Example:**
```
## Purpose

**Primary Goal:**
Understand how geometric resonance factorization works for 127-bit semiprimes and identify opportunities for refinement.

**Secondary Goals:**
- Document actual mechanics (Dirichlet filtering, QMC sampling, snap formula)
- Identify current limitations honestly (single test case, parameter sensitivity)
- Propose concrete optimizations (closed-form kernel, parallelization)
- Establish validation protocol for testing on multiple targets

**Success Criteria:**
1. **Understanding:** Document formula derivations and explain each component
2. **Limitations:** Identify at least 3 concrete limitations with current implementation
3. **Refinements:** Propose at least 3 actionable optimization strategies
4. **Validation:** Create test plan for evaluating generalization (untested currently)

**Success Metrics:**
- **Documentation:** Complete analysis document with derivations
- **Code Review:** Identify Java implementation issues and fixes
- **Optimization Proposals:** Concrete performance improvements (5-10× speedup targets)
- **Test Coverage:** Design ablation study for J, m_span, k_range parameters

**Verification Procedures:**
1. **Reproducibility:**
   ```bash
   cd results/geometric_resonance_127bit
   python3 method.py
   # Must produce identical factors on each run
   ```

2. **Mathematical Verification:**
   ```python
   # Verify formula simplification: theta = π·m
   import mpmath as mp
   mp.dps = 200
   N = mp.mpf('137524771864208156028430259349934309717')
   p_hat = ...  # computed from snap formula
   theta_orig = (mp.log(N) - 2*mp.log(p_hat)) * k / 2
   theta_simplified = mp.pi * m
   assert abs(theta_orig - theta_simplified) < 1e-50
   ```

3. **Implementation Testing:**
   ```bash
   # Java version should produce same results
   ./gradlew build
   java -cp build/libs/z-sandbox.jar \
     org.zfifteen.sandbox.GeometricResonanceFactorizer \
     137524771864208156028430259349934309717 \
     --mc-digits=240 --samples=801 --m-span=180 --J=6
   ```

**Measurement Methodology:**
- **Understanding:** Ability to explain each formula and component
- **Limitations:** Number of concrete issues identified and documented
- **Optimizations:** Projected speedup factors (theoretical analysis)
- **Validation:** Test plan completeness (covers multiple scenarios)

**Value Proposition:**
- **Scientific:** Honest assessment of a promising research technique
- **Practical:** Optimization roadmap for performance improvements
- **Educational:** Demystifies complex-sounding approach with clear analysis
- **Research:** Establishes baseline for future multi-target validation

**Explicit Non-Goals:**
- NOT claiming this works beyond the single tested 127-bit example
- NOT claiming polynomial-time factorization or RSA-breaking capability
- NOT claiming this is a general solution—it's an interesting technique to study
- NOT publishing until validated on multiple targets (currently: 1/1 success)
```

---

## Compliance Manifest Schema

Every deliverable must emit a machine-readable compliance manifest at the end. This manifest verifies that all 10 charter elements are present and valid.

### JSON Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Mission Charter Compliance Manifest",
  "type": "object",
  "required": [
    "manifest_version",
    "deliverable_id",
    "timestamp",
    "charter_compliance"
  ],
  "properties": {
    "manifest_version": {
      "type": "string",
      "description": "Version of this manifest schema",
      "const": "1.0.0"
    },
    "deliverable_id": {
      "type": "string",
      "description": "Unique identifier for this deliverable"
    },
    "deliverable_type": {
      "type": "string",
      "enum": ["spec", "pr", "code", "research_note", "log", "runbook", "design", "plan", "report"]
    },
    "timestamp": {
      "type": "string",
      "format": "date-time",
      "description": "ISO 8601 timestamp of deliverable creation"
    },
    "author": {
      "type": "string",
      "description": "Creator of deliverable (user, agent, system)"
    },
    "charter_compliance": {
      "type": "object",
      "required": [
        "first_principles",
        "ground_truth",
        "reproducibility",
        "failure_knowledge",
        "constraints",
        "context",
        "models_limits",
        "interfaces",
        "calibration",
        "purpose"
      ],
      "properties": {
        "first_principles": {
          "$ref": "#/definitions/element_status"
        },
        "ground_truth": {
          "$ref": "#/definitions/element_status"
        },
        "reproducibility": {
          "$ref": "#/definitions/element_status"
        },
        "failure_knowledge": {
          "$ref": "#/definitions/element_status"
        },
        "constraints": {
          "$ref": "#/definitions/element_status"
        },
        "context": {
          "$ref": "#/definitions/element_status"
        },
        "models_limits": {
          "$ref": "#/definitions/element_status"
        },
        "interfaces": {
          "$ref": "#/definitions/element_status"
        },
        "calibration": {
          "$ref": "#/definitions/element_status"
        },
        "purpose": {
          "$ref": "#/definitions/element_status"
        }
      }
    },
    "validation_result": {
      "type": "object",
      "properties": {
        "is_compliant": {
          "type": "boolean"
        },
        "missing_elements": {
          "type": "array",
          "items": {
            "type": "string"
          }
        },
        "warnings": {
          "type": "array",
          "items": {
            "type": "string"
          }
        }
      }
    }
  },
  "definitions": {
    "element_status": {
      "type": "object",
      "required": ["present", "location"],
      "properties": {
        "present": {
          "type": "boolean",
          "description": "Whether this element is documented"
        },
        "location": {
          "type": "string",
          "description": "Section/heading where element is documented"
        },
        "completeness": {
          "type": "number",
          "minimum": 0,
          "maximum": 1,
          "description": "Completeness score (0.0-1.0)"
        },
        "notes": {
          "type": "string",
          "description": "Additional notes or warnings"
        }
      }
    }
  }
}
```

### Example Manifest

```json
{
  "manifest_version": "1.0.0",
  "deliverable_id": "z-sandbox-geometric-resonance-analysis",
  "deliverable_type": "research_note",
  "timestamp": "2025-11-09T00:00:00Z",
  "author": "Claude Code with Big D",
  "charter_compliance": {
    "first_principles": {
      "present": true,
      "location": "Section 1: Mechanism Analysis",
      "completeness": 1.0,
      "notes": "Core formulas derived and explained"
    },
    "ground_truth": {
      "present": true,
      "location": "Section 2.4: Validation Gaps",
      "completeness": 0.8,
      "notes": "Single test case documented; generalization explicitly marked unknown"
    },
    "reproducibility": {
      "present": true,
      "location": "Python: method.py, Java: GeometricResonanceFactorizer.java",
      "completeness": 1.0,
      "notes": "Full source code provided with exact parameters"
    },
    "failure_knowledge": {
      "present": true,
      "location": "Section 2: Current Limitations",
      "completeness": 0.9,
      "notes": "Limitations documented; failure modes to be catalogued after multi-target testing"
    },
    "constraints": {
      "present": true,
      "location": "Section 6.3: Explicit Non-Goals in Purpose",
      "completeness": 1.0,
      "notes": "Explicitly states no RSA-breaking claims, research only"
    },
    "context": {
      "present": true,
      "location": "Executive Summary",
      "completeness": 1.0,
      "notes": "Scope and non-scope clearly defined"
    },
    "models_limits": {
      "present": true,
      "location": "Section 2.3: Theoretical Gaps, Section 6.2: What We Don't Know",
      "completeness": 1.0,
      "notes": "Unknowns explicitly documented; no overclaiming"
    },
    "interfaces": {
      "present": true,
      "location": "Section 1.1-1.4: Formula descriptions",
      "completeness": 1.0,
      "notes": "Python and Java implementations documented"
    },
    "calibration": {
      "present": true,
      "location": "Section 3.2: Parameter Tuning",
      "completeness": 0.7,
      "notes": "Parameters documented as empirical; ablation study needed"
    },
    "purpose": {
      "present": true,
      "location": "Section 6.3: Recommended Next Steps",
      "completeness": 1.0,
      "notes": "Research goals clearly stated; scaling claims explicitly avoided"
    }
  },
  "validation_result": {
    "is_compliant": true,
    "missing_elements": [],
    "warnings": [
      "ground_truth: Only one test case; need multi-target validation",
      "calibration: Parameters may be overfit; ablation study pending"
    ]
  }
}
```

---

## Usage Guidelines

### For Assistants/Agents

1. **Template Selection:** Use the appropriate deliverable template (see `docs/templates/`)
2. **Charter Sections:** Include all 10 charter elements as top-level sections
3. **Manifest Generation:** Generate compliance manifest using `tools/validate_charter.py`
4. **Validation:** Verify deliverable passes charter validation before submission

### For Contributors

1. **Review Checklist:** Ensure all 10 elements are addressed before PR submission
2. **CI Integration:** Charter validation runs automatically in GitHub Actions
3. **Rejection Criteria:** PRs missing charter elements will be rejected with specific feedback
4. **Templates:** Use provided templates in `docs/templates/` for consistency

### Enforcement Flags

```bash
# Enable charter enforcement (default)
--charter.enforce=true

# Use specific template
--charter.template=docs/templates/research_note.md

# Strict mode (no warnings allowed)
--charter.strict=true

# Generate manifest only
--charter.manifest-only=true
```

---

## References

- **Z-Framework Axioms:** docs/core/
- **Reproducibility Standards:** docs/guides/REPRODUCIBILITY.md
- **Security Protocols:** docs/security/TRANSEC.md
- **Testing Standards:** tests/README.md
- **Agent Operating Manual:** .github/agents/z-sandbox-agent.md

---

## Revision History

| Version | Date       | Author          | Changes                          |
|---------|------------|-----------------|----------------------------------|
| 1.0.0   | 2025-11-07 | Copilot Agent   | Initial charter definition       |
| 1.1.0   | 2025-11-09 | Claude Code     | Updated examples to align with research philosophy: removed grand RSA-breaking claims, added realistic geometric resonance examples, emphasized limitations documentation and honest assessment over breakthrough claims |

---

**This is a living document. All changes must be approved by the Project Owner.**
