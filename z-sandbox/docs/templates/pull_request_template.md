# [PR Title: Brief Description]

**Type:** Pull Request  
**Author:** [Your Name]  
**Date:** [YYYY-MM-DD]  
**Status:** [Draft/Ready for Review]

**Related Issue:** #[issue-number]

---

## First Principles

**Z-Framework Axioms Applied:**
- Z = A(B/c) where c = e² (if applicable)
- κ(n) = d(n) * ln(n+1) / e² (if applicable)
- [Other axioms as relevant]

**Mathematical/Algorithmic Foundations:**
- [Core algorithms or methods modified]
- [Key formulas or equations]

**Units and Precision:**
- [Precision requirements]
- [Units of measurement]

---

## Ground Truth & Provenance

**Changes Made:**
- [Describe what was changed]
- [File paths and specific modifications]

**Author:**
- [GitHub username / Agent name]

**Timestamp:**
- PR Created: [YYYY-MM-DDTHH:MM:SSZ]
- Last Updated: [YYYY-MM-DDTHH:MM:SSZ]

**Method:**
- [How changes were developed/tested]

**External Sources Referenced:**
- [List any external sources, papers, documentation used]
- [Include URLs, DOIs, access timestamps]

**Testing Evidence:**
- [Link to test results]
- [CI/CD run URLs]

---

## Reproducibility

### Environment
- Python: [version]
- Java: [version] (if applicable)
- Libraries changed: [name==old_version → new_version]
- Platform: [OS, architecture]

### Build and Test Commands
```bash
# Build
./gradlew build

# Run tests
./gradlew test
python -m pytest

# Verify changes
[specific test commands]
```

### Configuration Changes
- [Config files modified]
- [New environment variables]
- [Updated dependencies]

### Expected Behavior After Merge
- [What should work differently]
- [Performance expectations]

### Verification Steps for Reviewers
```bash
# Steps to verify this PR
git checkout copilot/[branch-name]
[commands to verify changes]
```

---

## Failure Knowledge

### Potential Regressions
- **Risk:** [Potential regression 1]
- **Detection:** [How to detect it]
- **Mitigation:** [What was done to prevent it]

### Known Issues (Pre-existing)
- [Issue 1: not addressed in this PR]
- [Issue 2: to be handled in follow-up]

### New Edge Cases Introduced
- [Edge case 1 and handling]
- [Edge case 2 and handling]

### Limitations of This Change
- [What this PR doesn't fix]
- [Known limitations]
- [Future work needed]

### Rollback Plan
```bash
# How to revert if issues arise
git revert [commit-hash]
[additional rollback steps if needed]
```

---

## Constraints

### Legal
- License compatibility: [verified/not applicable]
- Copyright: [original work / modified from source]
- Attribution requirements: [any needed]

### Ethical
- Research integrity: [how maintained]
- Data handling: [privacy considerations]

### Safety
- Security impact: [none / addressed as follows]
- Breaking changes: [yes/no, details]
- Backward compatibility: [maintained/broken, justification]

### Compliance
- Code style: [linted with...]
- Test coverage: [% coverage]
- Documentation updated: [yes/no]
- Charter compliance: [this PR is charter-compliant]

---

## Context

**Who:**
- Author: [name/handle]
- Reviewers: [@reviewer1, @reviewer2]
- Stakeholders: [who needs to know about this]

**What:**
- Problem: [what bug/issue/gap this addresses]
- Solution: [how this PR solves it]
- Scope: [what's included / what's not]

**When:**
- Milestone: [target release]
- Urgency: [high/medium/low]
- Dependencies: [blocked by / blocks]

**Where:**
- Repository: zfifteen/z-sandbox
- Branch: copilot/[branch-name]
- Affected modules: [list]

**Why:**
- Motivation: [why this change is needed now]
- Value: [what value it provides]
- Impact: [who/what benefits]

**Related Work:**
- Issue #[number]: [description]
- PR #[number]: [description]
- Discussion: [link if applicable]

---

## Models & Limits

### Algorithmic Changes
- **Algorithm:** [name/description]
- **Complexity:** [time/space complexity, before → after]
- **Assumptions:** [what assumptions are made]

### Validity Range
- **Input Domain:** [valid input ranges]
- **Tested Range:** [what was tested]
- **Untested Range:** [what wasn't tested but should work]

### Performance Characteristics
- **Speed:** [benchmarks, before → after]
- **Memory:** [usage, before → after]
- **Scalability:** [how it scales]

### Break Points
- [Condition 1: where algorithm may fail]
- [Condition 2: numerical instability points]

### Model Selection Rationale
- [Why this approach was chosen over alternatives]

---

## Interfaces & Keys

### API Changes
- **Breaking Changes:** [yes/no, list if yes]
- **New Functions/Methods:** [list with signatures]
- **Deprecated Functions:** [list with replacement]
- **Modified Signatures:** [before → after]

### Command-Line Changes
```bash
# Old
[old command format]

# New
[new command format]
```

### Configuration Changes
- File: [path]
- Changes: [what changed]
- Migration: [how to migrate existing configs]

### Environment Variables
- `NEW_VAR`: [purpose]
- `MODIFIED_VAR`: [change description]
- `DEPRECATED_VAR`: [use instead]

### I/O Changes
- Input formats: [changed/unchanged]
- Output formats: [changed/unchanged]
- File paths: [any changes]

### Secrets/Credentials
- [No new secrets / New secret required: REDACTED]
- [How secrets are managed]

---

## Calibration

### Parameters Modified
- **Parameter:** [name]
  - Old value: [value]
  - New value: [value]
  - Rationale: [why changed]
  - Impact: [expected effect]

### Thresholds Adjusted
- **Threshold:** [name]
  - Old: [value]
  - New: [value]
  - Validation: [how tested]

### Tuning Performed
- Method: [grid search / manual / empirical]
- Results: [summary of tuning results]
- Validation: [how validated]

### Performance Tuning
```bash
# Benchmark commands
[commands used to benchmark]
```

**Results:**
- Before: [metrics]
- After: [metrics]
- Improvement: [% or absolute]

---

## Purpose

### Primary Goal
[What this PR aims to accomplish]

### Secondary Goals
- [Additional benefit 1]
- [Additional benefit 2]

### Success Criteria
1. **Builds Successfully:** All builds pass
2. **Tests Pass:** [% coverage requirement]
3. **No Regressions:** Existing functionality intact
4. **[Custom Criterion]:** [specific to this PR]

### Success Metrics
- **Build Status:** [passing/failing]
- **Test Coverage:** [%]
- **Performance:** [meets/exceeds target]
- **Code Review:** [approved by at least N reviewers]

### Verification Procedures
1. **Automated Tests:**
   ```bash
   ./gradlew test
   python -m pytest
   ```
   Expected: All pass

2. **Manual Verification:**
   ```bash
   [manual test steps]
   ```
   Expected: [expected result]

3. **Regression Check:**
   ```bash
   [commands to check for regressions]
   ```
   Expected: No regressions

### Value Proposition
- **Technical:** [technical improvement]
- **User Impact:** [how users benefit]
- **Maintenance:** [maintenance implications]

---

## Changes Summary

### Files Modified
```
[file path 1] - [brief description]
[file path 2] - [brief description]
```

### Files Added
```
[file path 1] - [purpose]
[file path 2] - [purpose]
```

### Files Deleted
```
[file path 1] - [reason]
[file path 2] - [reason]
```

### Lines Changed
- Added: [count]
- Removed: [count]
- Modified: [count]

---

## Review Checklist

- [ ] Code follows project style guidelines
- [ ] Comments added for complex logic
- [ ] Tests added/updated for new functionality
- [ ] Documentation updated
- [ ] No breaking changes (or documented/justified)
- [ ] Security implications considered
- [ ] Performance impact assessed
- [ ] Backward compatibility maintained (or migration path provided)
- [ ] Charter compliance verified (this document)

---

## Compliance Manifest

```json
{
  "manifest_version": "1.0.0",
  "deliverable_id": "[pr-branch-name]",
  "deliverable_type": "pr",
  "timestamp": "[YYYY-MM-DDTHH:MM:SSZ]",
  "author": "[github-username]",
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
