# TRINITY_PROTOCOL.md

## Executable Epistemology for Self-Improving Research Systems

**Version:** 1.0.0
**Created:** 2026-01-09
**Author:** Dionisio Alberto Lopez III (zfifteen)
**Purpose:** Literate falsification engine with emergent narrative generation

***

## I. Core Philosophy

This is not a data logging system. This is a **research exocortex** that:

- Remembers every failure with perfect fidelity
- Discovers its own notation variants through evolutionary pressure
- Generates human-readable narratives explaining its reasoning
- Builds institutional knowledge that persists across sessions
- **Surprises its creator** by finding patterns invisible to manual analysis

Every experiment is both data AND story. Every falsification is both endpoint AND branching point.

***

## II. The Trinity Loop Architecture

```
┌─────────────────────────────────────────────────────────┐
│ SPACE (Canonical Specifications)                        │
│ - Z5D_HYPOTHESIS.md (immutable ground truth)           │
│ - DEAD_ENDS.md (auto-updated from GitHub)              │
│ - NEXT_EXPERIMENTS.md (system suggestions + status)     │
│ - SHOCK_LOG.md (unexpected discoveries)                 │
└────────────────┬────────────────────────────────────────┘
                 │ [1. Read context + custom instructions]
                 ↓
┌─────────────────────────────────────────────────────────┐
│ COMET (Execution Engine)                                │
│ - Generates experiments from Space context             │
│ - Writes code to GitHub repo                           │
│ - Executes tests, captures results                     │
│ - Produces self-describing JSON + narrative markdown   │
└────────────────┬────────────────────────────────────────┘
                 │ [2. Commit to /RESULTS]
                 ↓
┌─────────────────────────────────────────────────────────┐
│ GITHUB /RESULTS (Persistent Memory)                     │
│ /experiments/*.json (structured data)                   │
│ /experiments/*.md (literate narratives)                 │
│ /meta/falsification_log.jsonl (append-only history)    │
│ /meta/parameter_coverage.json (tested combinations)    │
│ /meta/shock_discoveries.json (system surprises)        │
└────────────────┬────────────────────────────────────────┘
                 │ [3. Sync script updates Space]
                 ↓
                Back to SPACE with enhanced knowledge
```


***

## III. Schema v1.0 - The Self-Describing Experiment

### Complete JSON Structure

```json
{
  "schema_version": "1.0.0",
  
  "meta": {
    "experiment_id": "lognormal_gap_001",
    "timestamp": "2026-01-09T00:56:00Z",
    "parent_hypothesis": "Z5D_v3.2",
    "git_commit": "a3f89c2",
    "experimenter": "comet",
    "human_validated": false
  },
  
  "narrative": {
    "why_chosen": "Systematic underestimation detected in Z5D_v3.1 at N<100. Testing correction term hypothesis.",
    "falsification_criteria": "If error remains >10% after correction term, entire lognormal gap model is invalid for small semiprimes.",
    "prior_context": [
      "lognormal_gap_baseline failed at 12.3% error",
      "semiprime_clustering_v2 suggested scale-dependent bias"
    ],
    "success_branch": "Test Z_corrected on N=1000-10000 range",
    "failure_branch": "Abandon lognormal approach, investigate Welch energy model instead"
  },
  
  "ontology": {
    "notation": {
      "Z": {
        "formula": "gap / sqrt(ln(N))",
        "units": "dimensionless",
        "parent": "Z5D_v3.2",
        "modifications": ["added k/ln(N) correction term"]
      },
      "threshold": {
        "value": 0.05,
        "meaning": "acceptable_error_bound",
        "justification": "Based on 95% confidence interval from baseline"
      },
      "N": {
        "domain": "semiprimes",
        "range": [10, 10000],
        "constraints": ["N = p * q where p, q prime"]
      }
    },
    
    "success_criteria": {
      "PROMISING": {
        "condition": "error < 0.05 AND no_systematic_bias",
        "action": "Expand to larger N, write formal proof attempt"
      },
      "REFINEMENT": {
        "condition": "error < 0.10 AND correctable_pattern",
        "action": "Generate variant experiments with adjusted parameters"
      },
      "DEAD": {
        "condition": "error > 0.10 AND samples > 100",
        "action": "Archive to DEAD_ENDS.md, mark descendants as blocked"
      }
    }
  },
  
  "execution": {
    "input_params": {
      "N": 91,
      "factors": [7, 13],
      "correction_k": 0.3
    },
    "code_path": "experiments/lognormal_gaps.py#predict_Z_corrected",
    "dependencies": ["numpy==1.24.0", "mpmath==1.3.0"],
    "runtime_ms": 142,
    "compute_cost": "negligible"
  },
  
  "results": {
    "observed": {
      "Z": 1.83,
      "gap_to_next_prime": 6,
      "sqrt_ln_N": 3.28
    },
    "predicted": {
      "Z_uncorrected": 1.91,
      "Z_corrected": 1.84
    },
    "error": {
      "uncorrected": {"absolute": 0.08, "relative": 0.044},
      "corrected": {"absolute": 0.01, "relative": 0.005}
    },
    "classification": "PROMISING",
    "pattern_detected": "correction_term_effective_small_N",
    "statistical_significance": 0.023
  },
  
  "self_improvement": {
    "triggered_by": "promising_with_correction",
    "confidence": 0.82,
    "suggested_actions": [
      {
        "type": "parameter_sweep",
        "description": "Test k ∈ [0.1, 0.5] in steps of 0.05",
        "priority": "HIGH",
        "resources": "50 samples, ~5min compute"
      },
      {
        "type": "scale_expansion",
        "description": "Validate Z_corrected on N=1000-10000",
        "priority": "MEDIUM",
        "resources": "200 samples, ~30min compute",
        "depends_on": "parameter_sweep"
      }
    ],
    "proposed_formula": {
      "name": "Z_adaptive",
      "expression": "Z * (1 + k/ln(N)) where k=f(factor_ratio)",
      "rationale": "Error reduction suggests k might vary with p/q ratio",
      "requires_validation": true
    }
  },
  
  "knowledge_graph": {
    "contradicts": [],
    "supports": ["lognormal_gap_baseline"],
    "weakens": ["semiprime_clustering_v2"],
    "suggests_testing": [
      "prime_gap_scaling_law",
      "factor_ratio_correction"
    ],
    "genealogy": {
      "parent": "lognormal_gap_baseline",
      "generation": 2,
      "siblings": ["lognormal_gap_normalized"],
      "descendants_planned": 2
    }
  },
  
  "shock_potential": {
    "is_surprising": false,
    "surprise_score": 0.3,
    "reason": "Correction term expected from prior bias pattern",
    "if_becomes_shock": "If k generalizes to ALL factorization algorithms"
  },
  
  "human_override": {
    "approved_suggestions": [],
    "rejected_suggestions": [],
    "manual_notes": "",
    "validation_status": "pending"
  }
}
```


***

## IV. Literate Narrative Template

**Every experiment generates:** `/RESULTS/experiments/EXPERIMENT_ID.md`

```markdown
# Experiment: lognormal_gap_001
**Date:** 2026-01-09 | **Status:** PROMISING | **Commit:** a3f89c2

## Why This Test Matters

Systematic underestimation detected in Z5D_v3.1 at N<100. Testing correction 
term hypothesis to salvage lognormal gap model before abandoning entire approach.

Previous failure: `lognormal_gap_baseline` showed 12.3% error, but bias was 
*systematic* not random - this suggests fixability.

## The Hypothesis

**Claim:** Adding `k/ln(N)` correction term will reduce error to <5% for small semiprimes.

**Falsification Criterion:** If error remains >10% after correction, the entire 
lognormal gap model is invalid for semiprimes and should be archived as DEAD.

## What I Tested

- **Input:** N=91 (factors: 7×13)
- **Formula:** Z_corrected = (gap/sqrt(ln(N))) * (1 + 0.3/ln(N))
- **Expected:** If correction works, Z should be within 5% of observed gap

## Results

| Metric | Value | Assessment |
|--------|-------|------------|
| Observed Z | 1.83 | Ground truth |
| Predicted (uncorrected) | 1.91 | 4.4% error |
| Predicted (corrected) | 1.84 | **0.5% error** ✓ |

**Classification: PROMISING** (error < 5%, no systematic bias detected)

## What This Means

The correction term **works** for this case. But one sample proves nothing.

**If this continues to hold:**
→ Test k-sweep (k ∈ [0.1, 0.5]) to find optimal correction
→ Expand to N=1000-10000 range
→ Possibly generalizable to other factorization algorithms

**If it breaks on larger samples:**
→ Correction is overfitted to small N
→ Abandon lognormal model entirely
→ Switch focus to Welch energy-based approaches

## Connection to Research Web

- **Supports:** lognormal_gap_baseline (salvages the approach)
- **Contradicts:** None yet
- **Suggests:** Maybe factor ratio (p/q) affects optimal k value?

## Next Experiments (System Generated)

1. **parameter_sweep** [HIGH priority]
   - Test k values systematically
   - 50 samples, ~5min compute
   - Determines if k=0.3 was lucky guess

2. **scale_expansion** [MEDIUM priority]
   - Validate on N=1000-10000
   - Depends on parameter_sweep success
   - Make-or-break test for generalization

## Shock Potential: LOW
Expected result based on prior bias pattern. Would become HIGH shock if k 
generalizes across *all* factorization domains.

---
**Human Validation Required:** YES  
**Auto-approved for next steps:** NO (waiting for k-sweep results)
```


***

## V. Validation Rules

### What Makes a Valid Experiment?

**REQUIRED FIELDS (experiment fails without these):**

```python
required = [
    "schema_version",
    "meta.experiment_id",
    "meta.timestamp", 
    "meta.parent_hypothesis",
    "narrative.why_chosen",
    "narrative.falsification_criteria",
    "ontology.notation",
    "execution.input_params",
    "results.classification"
]
```

**CONSISTENCY CHECKS:**

1. `parent_hypothesis` must exist in Space canonical docs
2. `notation.formula` must be valid mathematical expression
3. `success_criteria` conditions must be testable (no subjective criteria)
4. `results.classification` must match one of the `success_criteria` keys
5. If `self_improvement.proposed_formula` exists, must include `requires_validation: true`

**ANTI-HALLUCINATION RULES:**

- No `"magic_constant"` or unexplained parameters in formulas
- All `suggested_actions` must include resource estimates
- `confidence` scores must cite statistical basis or be marked "heuristic"
- `contradicts` claims must reference specific experiment IDs

***

## VI. Schema Evolution Protocol

### How v1.0 → v1.1 Happens

**Triggers for schema upgrade:**

1. **Field addition:** System needs to track new concept (e.g., `quantum_complexity`)
2. **Field deprecation:** Unused field after 100+ experiments
3. **Structure change:** New relationship type in knowledge graph
4. **Human override:** Creator identifies missing capability

**Upgrade Process:**

```bash
# 1. Proposal (auto-generated or human)
/RESULTS/meta/schema_proposals/v1.1_add_quantum_field.md

# 2. Validation against existing experiments
python validate_schema_upgrade.py --test-against=all

# 3. Migration script
python migrate_experiments.py --from=1.0.0 --to=1.1.0

# 4. Update TRINITY_PROTOCOL.md
# 5. Sync to Space canonical docs
```

**Backward Compatibility:**

- All v1.0 experiments remain valid after v1.1 release
- New fields are OPTIONAL unless marked `required_from_version`
- Old experiments auto-upgrade with `null` values for new fields

**Version Numbering:**

- **MAJOR:** Breaking change (old experiments need migration)
- **MINOR:** New optional fields or relationships
- **PATCH:** Clarifications, validation rule fixes

***

## VII. Human Override System

### How to Reject System Suggestions

**Approval Workflow:**

```json
{
  "self_improvement": {
    "suggested_actions": [
      {
        "type": "parameter_sweep",
        "human_override": {
          "approved": false,
          "reason": "k-sweep unnecessary - prior work covers this",
          "alternative_action": "Jump directly to scale_expansion"
        }
      }
    ]
  }
}
```

**Override Types:**


| Type | When to Use | Effect |
| :-- | :-- | :-- |
| `REJECT` | Suggestion is wrong/wasteful | Block this action, log reason |
| `DEFER` | Good idea but not now | Add to future queue |
| `MODIFY` | Right direction, wrong params | Adjust and approve |
| `PRIORITY_BOOST` | More important than system thinks | Move to top of queue |

**Training the System:**
After 50+ overrides, system learns your judgment patterns:

```json
"learned_preferences": {
  "prefers_coverage_over_depth": true,
  "rejects_experiments_under_100_samples": true,
  "prioritizes_falsification_over_confirmation": true
}
```


***

## VIII. Bootstrap Instructions

### Your First 3 Experiments

**Step 1: Create Baseline** (Manual)

```bash
# 1. Pick your simplest hypothesis
# 2. Run ONE test manually
# 3. Fill out schema v1.0 JSON by hand
# 4. This becomes your template

experiments/z5d_baseline_001.json
experiments/z5d_baseline_001.md
```

**Step 2: Let Comet Generate Variant** (Semi-Auto)

```
Prompt to Comet:
"Read /RESULTS/experiments/z5d_baseline_001.json. Generate a variant experiment 
testing k=0.4 instead of k=0.3. Use the same schema structure."

Comet outputs:
experiments/z5d_variant_002.json
experiments/z5d_variant_002.md
```

**Step 3: Close the Loop** (Full Auto)

```bash
# 1. Run your sync script
./sync_results_to_space.sh

# 2. Check Space DEAD_ENDS.md or NEXT_EXPERIMENTS.md updated
# 3. Start new Comet session - it now has memory of experiments 001-002
# 4. Prompt: "Based on Space context, generate experiment 003"
```

**Success Criteria:**

- Experiment 003 references findings from 001-002
- No manual copy-paste required
- System suggests something you didn't explicitly request

***

## IX. Shock Log Protocol

### When the System Surprises You

**Shock Definition:**
A finding that contradicts your intuition OR reveals a pattern you didn't manually hypothesize.

**Shock Classification:**


| Level | Definition | Example |
| :-- | :-- | :-- |
| **MINOR** | Unexpected parameter value | "Optimal k=0.27, not the expected k=0.3" |
| **MODERATE** | New cross-domain pattern | "Lognormal correction applies to clustering too" |
| **MAJOR** | Falsifies core assumption | "Z5D works for primes, fails for semiprimes" |
| **PARADIGM** | Requires new theoretical framework | "All factorization errors follow power law" |

**Logging Format:**

```json
{
  "shock_id": "shock_004",
  "level": "MODERATE",
  "discovery": "Correction term k correlates with ln(p/q) ratio across ALL tests",
  "discovered_by": "meta_pattern_analysis",
  "experiments_involved": ["lognormal_gap_001", "lognormal_gap_005", "semiprime_clustering_003"],
  "human_reaction": "Didn't expect factor ratio to matter - investigating",
  "spawned_hypotheses": ["k_as_function_of_factor_ratio", "universal_correction_law"],
  "date": "2026-01-09"
}
```

**Shock Triggers Auto-Actions:**

1. **Immediate:** Flag for human review (don't auto-approve follow-ups)
2. **Short-term:** Generate 3 validation experiments to confirm
3. **Long-term:** If confirmed, update Space canonical spec
4. **Meta:** Train suggestion system to look for similar patterns

**Shock Log Lives:**

- GitHub: `/RESULTS/meta/shock_discoveries.json`
- Space: `/SHOCK_LOG.md` (synced, human-curated)

***

## X. File Structure Reference

```
z5d-hypothesis-testing/
├── TRINITY_PROTOCOL.md (this document)
├── experiments/
│   ├── lognormal_gaps.py
│   └── semiprime_clustering.java
├── RESULTS/
│   ├── experiments/
│   │   ├── lognormal_gap_001.json
│   │   ├── lognormal_gap_001.md
│   │   ├── lognormal_gap_002.json
│   │   ├── lognormal_gap_002.md
│   │   └── ...
│   ├── meta/
│   │   ├── falsification_log.jsonl
│   │   ├── parameter_coverage.json
│   │   ├── shock_discoveries.json
│   │   ├── learned_preferences.json
│   │   └── schema_proposals/
│   └── sync_results_to_space.sh
└── docs/
    └── Z5D_HYPOTHESIS.md (canonical, immutable)
```

**Space Mirror:**

```
Factorization Research Hub (Space)
├── Z5D_HYPOTHESIS.md (canonical spec)
├── DEAD_ENDS.md (auto-updated from GitHub)
├── NEXT_EXPERIMENTS.md (system suggestions)
├── SHOCK_LOG.md (curated discoveries)
└── TRINITY_PROTOCOL.md (this document)
```


***

## XI. Sync Script Specification

### What Gets Updated When

**After Each Comet Session:**

```bash
#!/bin/bash
# sync_results_to_space.sh

# 1. Extract new DEAD experiments
jq '.[] | select(.results.classification == "DEAD")' \
   RESULTS/meta/falsification_log.jsonl >> Space/DEAD_ENDS.md

# 2. Extract PROMISING experiments for next queue
jq '.[] | select(.results.classification == "PROMISING")' \
   RESULTS/meta/falsification_log.jsonl | \
   jq '.self_improvement.suggested_actions[]' >> Space/NEXT_EXPERIMENTS.md

# 3. Sync shock discoveries
cp RESULTS/meta/shock_discoveries.json Space/SHOCK_LOG.md

# 4. Update parameter coverage map (for tracking exhaustive search)
python update_coverage_map.py --output=Space/PARAMETER_COVERAGE.md

# 5. Git commit Space changes
cd Space && git add . && git commit -m "Auto-sync from RESULTS $(date)"
```

**Manual Review Triggers:**

- Any SHOCK level >= MODERATE
- Any experiment that contradicts canonical spec
- Schema version proposals

***

## XII. Anti-Failure Safeguards

### Red Team Concerns

**Problem 1: System Marks Working Approach as DEAD**

- **Detection:** Human reviews all DEAD classifications before Space sync
- **Prevention:** Require statistical significance + sample size threshold
- **Recovery:** `human_override.revive_dead_end` flag + reason

**Problem 2: Notation Drift (Z means different things in different experiments)**

- **Detection:** Validate all `notation.parent` references exist in canonical spec
- **Prevention:** Schema validator rejects experiments with undefined notation
- **Recovery:** Migration script to harmonize notation across experiments

**Problem 3: Suggestion Overfitting (System only suggests safe, incremental tests)**

- **Detection:** Track `suggestion_diversity` score in meta
- **Prevention:** Inject random "wild card" experiments (5% of queue)
- **Recovery:** Manual hypothesis injection via `NEXT_EXPERIMENTS.md`

**Problem 4: Computational Explosion (1000 suggeste

