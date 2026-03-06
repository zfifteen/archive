# [Deliverable Title]

**Type:** Research Note  
**Author:** [Your Name/Agent]  
**Date:** [YYYY-MM-DD]  
**Status:** [Draft/Review/Final]

---

## First Principles

**Axioms:**
- Z = A(B/c) where c = e² (Z-Framework universal invariant)
- κ(n) = d(n) * ln(n+1) / e² (discrete curvature)
- θ'(n,k) = φ * ((n mod φ) / φ)^k, k ≈ 0.3 (geometric resolution)

**Definitions:**
- [Define key terms used in this deliverable]

**Units:**
- [Specify units of measurement]

**Constants:**
- [List physical/mathematical constants with values]

---

## Ground Truth & Provenance

**Tested/Analyzed:**
- [What was tested or analyzed]

**Executor:**
- [Who performed the work: user, agent, system]

**Timestamp:**
- [ISO 8601: YYYY-MM-DDTHH:MM:SSZ]

**Method:**
- [How was it done]

**External Sources:**
1. [Author]. ([Year]). [Title]. [Publisher]. [URL/DOI]. Accessed: [ISO 8601 timestamp]
2. [Additional sources as needed]

---

## Reproducibility

### Environment
- Python: [version]
- Java: [version] (if applicable)
- Libraries: [name==version, ...]
- Platform: [OS, architecture]
- Hardware: [CPU, RAM if relevant]

### Commands
```bash
# Setup
cd /home/runner/work/z-sandbox/z-sandbox
export PYTHONPATH=python

# Run
[exact commands with all parameters]
```

### Configuration
- Random seed: [value]
- Key parameters: [param=value, ...]
- Environment variables: [VAR=value, ...]

### Expected Output
- [Describe expected results]
- Tolerance: [specify tolerances]
- Output location: [file paths]

### Validation
```bash
# Commands to validate results
[validation commands]
```

---

## Failure Knowledge

### Failure Mode 1: [Name]
- **Condition:** [When this failure occurs]
- **Symptom:** [Observable behavior]
- **Diagnostic:** [How to detect it]
- **Mitigation:** [How to prevent/fix it]

### Failure Mode 2: [Name]
- **Condition:** [When this failure occurs]
- **Symptom:** [Observable behavior]
- **Diagnostic:** [How to detect it]
- **Mitigation:** [How to prevent/fix it]

### Known Limitations
- [Limitation 1]
- [Limitation 2]
- [Limitation 3]

### Edge Cases
- [Edge case 1 and handling]
- [Edge case 2 and handling]

---

## Constraints

### Legal
- License: [license type]
- Copyright: [copyright holder]
- Patents: [relevant patents or "none known"]
- Export controls: [if applicable]

### Ethical
- [Ethical considerations]
- [Research ethics compliance]
- [Data usage restrictions]

### Safety
- [Safety requirements]
- [Security considerations]
- [Data protection measures]

### Compliance
- [Regulatory compliance]
- [Standards adherence]
- [Audit requirements]

---

## Context

**Who:**
- Stakeholders: [list]
- Audience: [intended audience]

**What:**
- Problem: [problem being addressed]
- Solution: [proposed solution]

**When:**
- Timeline: [schedule]
- Milestones: [key dates]

**Where:**
- Repository: z-sandbox
- Environment: [deployment context]

**Why:**
- Motivation: [why this work matters]
- Business value: [value proposition]
- Scientific contribution: [research value]

**Dependencies:**
- [Dependent work item 1]
- [Dependent work item 2]

---

## Models & Limits

### Mathematical Models
- **Model Name:** [description]
- **Form:** [mathematical formulation]
- **Assumptions:**
  - [Assumption 1]
  - [Assumption 2]

### Validity Range
- **Input Domain:** [min ≤ x ≤ max]
- **Parameter Ranges:** [param: min to max]
- **Precision Requirements:** [specifications]

### Break Points
- [Condition 1: singularity/discontinuity]
- [Condition 2: numerical instability]

### Approximation Bounds
- [Error bound 1: < value]
- [Error bound 2: < value]

### Model Selection Rationale
- [Why this model was chosen]

---

## Interfaces & Keys

### Command-Line Interface
```bash
[command] [OPTIONS]

Options:
  --option1 TYPE    Description (default: value)
  --option2 TYPE    Description (default: value)
  --help            Show help message
```

### Environment Variables
- `VAR_NAME`: [description]
- `VAR_NAME2`: [description]

### I/O Paths
- Input: [path patterns]
- Output: [path patterns]
- Logs: [path patterns]
- Temporary: [path patterns]

### Permissions Required
- Read: [paths]
- Write: [paths]
- Execute: [paths]

### Secrets Handling
- [How secrets are managed]
- [Redaction policy]
- [See: docs/security/TRANSEC.md]

### API (if applicable)
- Endpoint: [URL pattern]
- Authentication: [method]
- Rate limits: [specifications]

---

## Calibration

### Parameter: [Name]
- **Value:** [calibrated value]
- **Rationale:** [why this value]
- **Tuning Method:** [how it was tuned]
- **Validation:** [how it was validated]
- **Sensitivity:** [±delta impact]
- **Confidence Interval:** [95% CI: lower, upper]

### Threshold: [Name]
- **Value:** [threshold value]
- **Rationale:** [justification]
- **Validation:** [validation method]

### Prior Distribution (if Bayesian)
- **Distribution:** [type(params)]
- **Rationale:** [justification]
- **Validation:** [cross-validation results]

### Calibration Validation
```bash
# Commands to validate calibration
[validation commands]
```

**Expected Checks:**
- [Check 1: criteria]
- [Check 2: criteria]

---

## Purpose

### Primary Goal
[Clear statement of primary objective]

### Secondary Goals
- [Goal 1]
- [Goal 2]

### Success Criteria
1. **[Criterion 1]:** [quantitative threshold]
2. **[Criterion 2]:** [quantitative threshold]
3. **[Criterion 3]:** [quantitative threshold]

### Success Metrics
- **[Metric 1]:** [target value with units]
- **[Metric 2]:** [target value with units]
- **[Metric 3]:** [target value with units]

### Verification Procedures
1. **[Verification 1]:**
   ```bash
   # Commands to verify
   [verification commands]
   ```

2. **[Verification 2]:**
   ```bash
   # Commands to verify
   [verification commands]
   ```

### Measurement Methodology
- **[Metric 1]:** [how measured]
- **[Metric 2]:** [how measured]

### Value Proposition
- **Scientific:** [research value]
- **Practical:** [practical impact]
- **Educational:** [learning value]

---

## Compliance Manifest

```json
{
  "manifest_version": "1.0.0",
  "deliverable_id": "[unique-id]",
  "deliverable_type": "research_note",
  "timestamp": "[YYYY-MM-DDTHH:MM:SSZ]",
  "author": "[author]",
  "charter_compliance": {
    "first_principles": {"present": true, "location": "## First Principles (line X)", "completeness": 1.0},
    "ground_truth": {"present": true, "location": "## Ground Truth & Provenance (line X)", "completeness": 1.0},
    "reproducibility": {"present": true, "location": "## Reproducibility (line X)", "completeness": 1.0},
    "failure_knowledge": {"present": true, "location": "## Failure Knowledge (line X)", "completeness": 1.0},
    "constraints": {"present": true, "location": "## Constraints (line X)", "completeness": 1.0},
    "context": {"present": true, "location": "## Context (line X)", "completeness": 1.0},
    "models_limits": {"present": true, "location": "## Models & Limits (line X)", "completeness": 1.0},
    "interfaces": {"present": true, "location": "## Interfaces & Keys (line X)", "completeness": 1.0},
    "calibration": {"present": true, "location": "## Calibration (line X)", "completeness": 1.0},
    "purpose": {"present": true, "location": "## Purpose (line X)", "completeness": 1.0}
  },
  "validation_result": {
    "is_compliant": true,
    "missing_elements": [],
    "warnings": []
  }
}
```

---

**Template Version:** 1.0.0  
**Last Updated:** 2025-11-07  
**Reference:** MISSION_CHARTER.md
