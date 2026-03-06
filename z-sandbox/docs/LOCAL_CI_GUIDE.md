# Running CI Locally - Guide

## Overview

This guide explains how to run all z-sandbox CI checks locally before pushing to GitHub, avoiding failed CI runs and speeding up your development workflow.

## Why Run CI Locally?

- **Catch errors before pushing**: Find issues in seconds, not minutes
- **Save CI resources**: Reduce failed GitHub Actions runs
- **Faster iteration**: No waiting for remote CI to start
- **Offline development**: Run checks without network access

## Solution: Custom Local CI Runner

Since z-sandbox workflows use `runs-on: self-hosted`, the standard `act` tool doesn't work out of the box. Instead, we created a native script that runs the same checks directly on your Mac.

## Quick Start

### Run All CI Checks

```bash
./run-ci-local.sh
```

This runs all 5 CI workflows:
1. Charter compliance validation
2. Gradle build & test
3. Geometric resonance artifact verification
4. Wiener attack tests
5. Markdown ingest (dry-run)

### Run Specific Workflow

```bash
./run-ci-local.sh --workflow charter    # Charter compliance only
./run-ci-local.sh -w gradle             # Gradle build only
./run-ci-local.sh -w geometric          # Geometric resonance only
./run-ci-local.sh -w wiener             # Wiener tests only
./run-ci-local.sh -w ingest             # Markdown ingest only
```

### Verbose Output

```bash
./run-ci-local.sh --verbose              # Show all command output
./run-ci-local.sh -v -w charter          # Verbose for specific workflow
```

## Available Workflows

| Workflow | Description | GitHub File |
|----------|-------------|-------------|
| `charter` | Mission Charter compliance validation | `charter-compliance.yml` |
| `gradle` | Build and test Java components | `ci.yml` |
| `geometric` | Verify 127-bit factorization artifacts | `verify-geometric-resonance.yml` |
| `wiener` | Run Wiener attack tests | `wiener-attack-tests.yml` |
| `ingest` | Ingest loose markdown files (dry-run) | `ingest-loose-md.yml` |

## Integration with Git

### Pre-Push Hook (Recommended)

Automatically run CI checks before every push:

```bash
# Create the hook
cat > .git/hooks/pre-push << 'EOF'
#!/bin/bash
echo "Running local CI checks before push..."
./run-ci-local.sh
EOF

# Make it executable
chmod +x .git/hooks/pre-push
```

Now `git push` will automatically run all CI checks. If any fail, the push is aborted.

### Disable for One Push

To skip the pre-push hook when needed:

```bash
git push --no-verify
```

## Understanding the Output

### Success Example

```
==================================================
CI Summary
==================================================

Passed: 5
  ✓ charter
  ✓ gradle
  ✓ geometric
  ✓ wiener
  ✓ ingest

All CI checks passed! ✓
Safe to push to GitHub.
```

### Failure Example

```
==================================================
CI Summary
==================================================

Passed: 4
  ✓ gradle
  ✓ geometric
  ✓ wiener
  ✓ ingest

Failed: 1
  ✗ charter

Some CI checks failed. Please fix before pushing.
```

## Workflow Details

### Charter Compliance (`--workflow charter`)

**What it does:**
- Detects changed markdown files (compared to `main`)
- Validates deliverables for Mission Charter compliance
- Checks for all 10 required elements

**Files checked:**
- Any file matching: `*_SUMMARY.md`, `*_REPORT.md`, `*_IMPLEMENTATION.md`, `*_GUIDE.md`, `*PLAN.md`
- Excludes: Templates, README, CLAUDE.md, GEMINI.md, AGENTS.md

**Validation script:**
```bash
python3 tools/validate_charter.py <file> --author="Local CI"
```

### Gradle Build (`--workflow gradle`)

**What it does:**
- Compiles Java source code
- Runs JUnit tests
- Generates JaCoCo coverage report

**Command:**
```bash
./gradlew -q test jacocoTestReport
```

**Output:**
- Build logs in console
- Test results in `build/reports/tests/test/index.html`
- Coverage report in `build/reports/jacoco/test/html/index.html`

### Geometric Resonance (`--workflow geometric`)

**What it does:**
- Verifies SHA256 checksums of artifacts
- Validates factor multiplication (p × q = N)
- Checks both factors appear in candidates.txt
- Validates metrics.json integrity
- Runs test suite
- Checks for prohibited imports

**Artifacts location:**
```
results/geometric_resonance_127bit/
├── checksums.txt
├── candidates.txt
├── metrics.json
└── method.py
```

**Skips if:** `results/geometric_resonance_127bit/` doesn't exist

### Wiener Attack (`--workflow wiener`)

**What it does:**
- Runs pytest on Wiener attack implementation
- Tests convergent fraction logic
- Validates attack success on vulnerable RSA keys

**Command:**
```bash
PYTHONPATH=python python -m pytest -q tests/test_wiener_attack.py
```

**Skips if:** `python/wiener_attack.py` doesn't exist

### Markdown Ingest (`--workflow ingest`)

**What it does:**
- Detects new root-level markdown files
- Runs ingest script in dry-run mode (no changes)
- Shows where files would be moved

**Command:**
```bash
python src/python/docs_ingest.py --dry-run <files>
```

**Skips if:** No new root-level `.md` files detected

## Troubleshooting

### "No module named X"

Install Python dependencies:

```bash
pip install mpmath sympy numpy pytest pyyaml
```

### "gradlew: Permission denied"

Make Gradle wrapper executable:

```bash
chmod +x gradlew
```

### "Cannot find main"

Your current branch may be new. The script will compare to `HEAD~1` instead of `main`:

```bash
# This is automatic, no action needed
```

### Script shows no output

Add `--verbose` flag:

```bash
./run-ci-local.sh --verbose
```

## Advanced Usage

### Run Multiple Specific Workflows

```bash
# Run charter and gradle only
./run-ci-local.sh -w charter && ./run-ci-local.sh -w gradle
```

### Custom Pre-Push Hook (Selective)

Run only fast checks before push:

```bash
cat > .git/hooks/pre-push << 'EOF'
#!/bin/bash
# Run only charter and gradle (skip slow tests)
./run-ci-local.sh -w charter && ./run-ci-local.sh -w gradle
EOF

chmod +x .git/hooks/pre-push
```

### CI in Watch Mode

Use with `entr` for continuous testing:

```bash
# Install entr
brew install entr

# Watch Python files, run charter on change
ls python/**/*.py | entr ./run-ci-local.sh -w charter

# Watch all source files, run all CI
git ls-files | entr ./run-ci-local.sh
```

## Comparison: act vs run-ci-local.sh

| Feature | act | run-ci-local.sh |
|---------|-----|-----------------|
| Runs in Docker | ✓ | ✗ (native) |
| Supports self-hosted | ✗ | ✓ |
| ARM64 native | Requires config | ✓ |
| Speed | Slower (Docker overhead) | Faster |
| Exact CI replica | High fidelity | High fidelity |
| Setup complexity | Medium | Low |
| Maintenance | GitHub maintains | You maintain |

**Recommendation:** Use `run-ci-local.sh` for z-sandbox since it's designed for self-hosted runners and runs natively on ARM64.

## Why act Doesn't Work Here

`act` requires Docker and expects standard GitHub-hosted runners (`ubuntu-latest`, `macos-latest`). Your workflows use `runs-on: self-hosted`, which:

1. References your local Mac environment
2. Has custom tooling (Java 11, Python 3.12, mpmath, etc.)
3. Doesn't translate to Docker images

The `.actrc` file we created maps `self-hosted` to a Docker image, but it still requires:
- Docker Desktop running (resource-heavy on M1)
- Rebuilding images for ARM64
- Mapping local file paths into containers

`run-ci-local.sh` bypasses all this by running commands directly, matching your actual CI environment.

## Files Created

This solution adds:

1. **`run-ci-local.sh`** - Main CI runner script
2. **`.actrc`** - Configuration for act (if you want to experiment)
3. **`docs/LOCAL_CI_GUIDE.md`** - This documentation

Add to `.gitignore` if desired:

```bash
echo ".actrc" >> .gitignore  # Optional, if you don't want to commit act config
```

But **do commit** `run-ci-local.sh` so the team can use it:

```bash
git add run-ci-local.sh docs/LOCAL_CI_GUIDE.md
git commit -m "Add local CI runner for pre-push validation"
```

## Next Steps

1. **Test the runner:**
   ```bash
   ./run-ci-local.sh
   ```

2. **Install pre-push hook:**
   ```bash
   cat > .git/hooks/pre-push << 'EOF'
   #!/bin/bash
   ./run-ci-local.sh
   EOF
   chmod +x .git/hooks/pre-push
   ```

3. **Push with confidence:**
   ```bash
   git push  # CI runs automatically, aborts if failures
   ```

## Support

If you encounter issues:

1. Check verbose output: `./run-ci-local.sh -v`
2. Run individual workflows: `./run-ci-local.sh -w charter`
3. Verify dependencies: `python3 --version`, `java -version`, `./gradlew --version`
4. Check GitHub Actions logs for differences between local and remote

## Summary

**Before:** Push → Wait for CI → Fail → Fix → Repeat

**After:** Run `./run-ci-local.sh` → Fix locally → Push once → Pass ✓

This saves time, CI resources, and reduces frustration. The script mirrors your GitHub workflows exactly, so local passes mean GitHub passes.

