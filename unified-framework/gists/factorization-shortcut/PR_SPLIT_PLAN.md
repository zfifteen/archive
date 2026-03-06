# PR Split Plan

Based on feedback in PR #865 comment #3382657611, split the massive PR into 3 focused PRs.

## Current PR Stats
- **Files changed:** 34
- **Lines:** +106,443 -576
- **Status:** Too large, GitHub rendering issues

## Proposed Split

### PR A: Core Implementation (PRIORITY 1)
**Branch:** `z5d-factorization-core`
**Target files:**
```
gists/factorization-shortcut/
├── factorization_shortcut_z5d.py  ✅ Main implementation
├── README.md                       ✅ User documentation
├── test_validation.sh              ✅ Validation suite
└── tests/                          ⚠️  NEW: pytest suite for CI
    ├── __init__.py
    ├── test_core.py                (smoke tests, reproducibility)
    └── conftest.py                 (fixtures)
```

**Size estimate:** ~1,500 lines
**Dependencies:** Z5D binary (already in repo)
**CI requirements:** pytest, reproducible seed validation

**Action items before merge:**
1. ✅ Add crypto-safety disclaimer (DONE)
2. ⚠️  Add pytest CI suite
3. ⚠️  Expose batch mode OR shared library (remove subprocess overhead)
4. ✅ Parameters already exposed (--k, --epsilon)

---

### PR B: Validation & Analysis (PRIORITY 2)
**Branch:** `z5d-factorization-validation`
**Target files:**
```
src/c/4096-pipeline/
├── GIST_VALIDATION.md              ✅ Original gist validation
├── GIST_AB_COMPARISON.md           ✅ Sieve vs Z5D benchmark
├── GIST_OPTIMIZATION_PROPOSAL.md   ✅ Future optimizations
├── PYTHON_VS_C_COMPARISON.md       ✅ Why Python works, C doesn't
├── VALIDATION_SUMMARY.md           ✅ Executive summary
└── README_GIST_COMPARISON.md       ✅ Quick start guide
```

**Size estimate:** ~3,000 lines (pure documentation)
**Dependencies:** Core PR A (for references)
**CI requirements:** None (documentation only)

**Action items:**
1. ✅ Already complete
2. Add cross-references to Core PR after merge

---

### PR C: Benchmarks & Auxiliary Scripts (PRIORITY 3)
**Branch:** `z5d-factorization-benchmarks`
**Target files:**
```
gists/factorization-shortcut/
├── benchmarks/
│   ├── z5d_64bit_benchmark.py
│   ├── z5d_64bit_benchmark_results.json  ⚠️  Move to Release assets
│   └── benchmark_runner.sh
├── experiments/
│   ├── rsa_100_demo.py
│   ├── rsa_129_demo.py
│   ├── rsa_260_demo.py
│   └── logs/                        ⚠️  Move to Release assets
└── utils/
    └── download_file_from_url.py    ⚠️  Needs hardening
```

**Size estimate:** ~2,000 lines + large JSON/logs
**Dependencies:** Core PR A
**CI requirements:** Long-running benchmarks (optional, can be manual)

**Action items:**
1. ⚠️  Move large JSON/logs to GitHub Release assets
2. ⚠️  Harden downloader (timeout, streaming, SHA-256 validation)
3. ⚠️  Add `make bench64` target
4. Add crypto-safety disclaimers to RSA demo scripts

---

## Implementation Order

### Phase 1: Core PR (This Week)
```bash
git checkout -b z5d-factorization-core
# Cherry-pick only core files
# Add pytest suite
# Commit and push
```

**Merge criteria:**
- [ ] All tests pass in CI
- [ ] Crypto disclaimer visible
- [ ] README complete
- [ ] One perf fix (batch mode OR shared library)

### Phase 2: Validation PR (After Core Merge)
```bash
git checkout -b z5d-factorization-validation
# Add validation docs
# Update references to point to merged Core
```

**Merge criteria:**
- [ ] Core PR merged
- [ ] All cross-references updated
- [ ] Docs render correctly on GitHub

### Phase 3: Benchmarks PR (Optional)
```bash
git checkout -b z5d-factorization-benchmarks
# Add benchmark scripts
# Move large files to Release
# Add downloader hardening
```

**Merge criteria:**
- [ ] Large files moved to Release assets
- [ ] Downloader security hardened
- [ ] RSA demos have disclaimers

---

## Migration from Current PR #865

### Step 1: Close PR #865
Comment:
```
Closing this PR to split into 3 focused PRs per review feedback:
- PR A (Core): Reference implementation + tests
- PR B (Validation): Analysis and documentation
- PR C (Benchmarks): Auxiliary scripts and large data

This will make reviews faster and keep diffs manageable.
See PR_SPLIT_PLAN.md for details.
```

### Step 2: Create PR A (Core)
```bash
git checkout -b z5d-factorization-core main
# Cherry-pick core files only
git cherry-pick <commit-hash> -- gists/factorization-shortcut/factorization_shortcut_z5d.py
git cherry-pick <commit-hash> -- gists/factorization-shortcut/README.md
git cherry-pick <commit-hash> -- gists/factorization-shortcut/test_validation.sh
# Add new pytest suite
# Commit and push
```

### Step 3: Wait for PR A Merge

### Step 4: Create PR B (Validation)
```bash
git checkout -b z5d-factorization-validation main
git cherry-pick <commit-hash> -- src/c/4096-pipeline/*.md
# Update references
# Commit and push
```

### Step 5: Create PR C (Benchmarks)
```bash
git checkout -b z5d-factorization-benchmarks main
# Add benchmark files
# Harden downloader
# Move large files to Release
# Commit and push
```

---

## File Size Analysis

### Current PR #865
```
Total: +106,443 lines
├── Code: ~3,000 lines
├── Docs: ~3,500 lines
└── Data: ~100,000 lines (JSON/logs)
```

### After Split
**PR A (Core):**
```
Code: ~750 lines (factorization_shortcut_z5d.py)
Docs: ~500 lines (README.md)
Tests: ~200 lines (pytest suite)
Total: ~1,500 lines ✅ Reviewable
```

**PR B (Validation):**
```
Docs: ~3,000 lines (6 markdown files)
Total: ~3,000 lines ✅ Reviewable
```

**PR C (Benchmarks):**
```
Code: ~2,000 lines (scripts)
Data: MOVED to Release assets
Total: ~2,000 lines ✅ Reviewable
```

---

## Benefits of Split

1. **Faster Reviews:** Each PR focused on one concern
2. **Easier Rollback:** Can revert one piece without affecting others
3. **Better CI:** Core tests fast, benchmarks can be manual
4. **GitHub Rendering:** No more "Uh oh! error while loading"
5. **Incremental Value:** Get Core merged quickly, iterate on extras

---

## Next Steps

1. **Implement pytest suite** for Core PR
2. **Choose perf fix:** Batch mode (easier) or shared library (faster)
3. **Create Core PR branch** with cherry-picked commits
4. **Update this plan** as we go

---

**Status:** 🚧 In Progress
**Priority:** HIGH (blocks PR #865 merge)
**Owner:** @zfifteen
