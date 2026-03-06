# Local CI Quick Reference

## Run All CI Checks
```bash
./run-ci-local.sh
```

## Run Specific Workflow
```bash
./run-ci-local.sh -w charter     # Charter compliance
./run-ci-local.sh -w gradle      # Java build/test
./run-ci-local.sh -w geometric   # Artifact verification
./run-ci-local.sh -w wiener      # Wiener tests
./run-ci-local.sh -w ingest      # Markdown ingest
```

## Verbose Mode
```bash
./run-ci-local.sh -v             # Show all output
./run-ci-local.sh -v -w charter  # Verbose for one workflow
```

## Setup Pre-Push Hook (One-Time)
```bash
cat > .git/hooks/pre-push << 'EOF'
#!/bin/bash
./run-ci-local.sh
EOF
chmod +x .git/hooks/pre-push
```

## Skip Pre-Push Hook (When Needed)
```bash
git push --no-verify
```

## Help
```bash
./run-ci-local.sh --help
```

## What Each Workflow Does

| Workflow | Checks |
|----------|--------|
| charter | Mission Charter compliance on changed .md files |
| gradle | Java compile, test, coverage |
| geometric | 127-bit artifact verification (checksums, factors, metrics) |
| wiener | Wiener attack tests (pytest) |
| ingest | Markdown file organization (dry-run) |

## Common Issues

**Missing dependencies:**
```bash
pip install mpmath sympy numpy pytest pyyaml
```

**Gradle permission:**
```bash
chmod +x gradlew
```

**See details:**
```bash
./run-ci-local.sh -v
```

## Expected Output

✅ **Success:**
```
All CI checks passed! ✓
Safe to push to GitHub.
```

❌ **Failure:**
```
Failed: 1
  ✗ charter

Some CI checks failed. Please fix before pushing.
```

## Full Documentation
See `docs/LOCAL_CI_GUIDE.md` for complete guide.

