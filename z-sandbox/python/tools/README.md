# Z-Sandbox Tools

This directory contains utility tools and scripts for the z-sandbox project.

## Charter Validation Tool

### validate_charter.py

Mission Charter compliance validator that checks deliverables for the presence and completeness of all 10 required charter elements.

**Usage:**
```bash
python tools/validate_charter.py <deliverable_file> [options]
```

**Options:**
- `--strict`: Fail on warnings (not just missing elements)
- `--manifest-only`: Generate manifest without validation messages
- `--output FILE`: Output manifest to FILE (default: stdout)
- `--template TYPE`: Deliverable type (spec, pr, code, research_note, log, runbook, design, plan, report)
- `--author NAME`: Author/creator of deliverable

**Examples:**

Validate a deliverable:
```bash
python tools/validate_charter.py MISSION_CHARTER.md --template=spec --author="Copilot"
```

Generate manifest only:
```bash
python tools/validate_charter.py docs/CHARTER_IMPLEMENTATION_EXAMPLE.md \
  --manifest-only \
  --output=manifest.json
```

Strict validation (fail on warnings):
```bash
python tools/validate_charter.py docs/research/my_note.md --strict
```

**Exit Codes:**
- 0: Success (compliant or manifest generated)
- 1: Validation failed (missing elements or warnings in strict mode)
- 2: Error (file not found, invalid arguments, etc.)

**Tests:**
```bash
python tests/test_charter_validator.py
```

## Charter Elements

All deliverables must include these 10 charter elements:

1. **First Principles** - Axioms, definitions, units
2. **Ground Truth & Provenance** - Sources, timestamps, methods
3. **Reproducibility** - Commands, versions, seeds, environment
4. **Failure Knowledge** - Failure modes, diagnostics, mitigations
5. **Constraints** - Legal, ethical, safety, compliance
6. **Context** - Who, what, when, where, why
7. **Models & Limits** - Assumptions, validity ranges, break points
8. **Interfaces & Keys** - Commands, env vars, I/O paths
9. **Calibration** - Parameters, tuning, validation
10. **Purpose** - Goals, metrics, success criteria

See `MISSION_CHARTER.md` for detailed requirements and `docs/templates/` for templates.

## CI/CD Integration

The charter validation tool is integrated into GitHub Actions via `.github/workflows/charter-compliance.yml`. It automatically validates deliverables in pull requests.

**Workflow triggers:**
- Pull requests modifying markdown files in `docs/`, `python/`, or root
- Pushes to main branch
- Manual workflow dispatch

**What it checks:**
- Files with names containing: `_SUMMARY`, `_REPORT`, `_IMPLEMENTATION`, `_GUIDE`, `PLAN`
- Skips: templates, README files, and agent configuration files

## Templates

Deliverable templates are available in `docs/templates/`:

- `research_note_template.md` - Template for research notes
- `pull_request_template.md` - Template for PR descriptions

Use these templates to ensure your deliverables are charter-compliant from the start.

## Contributing

When adding new tools to this directory:

1. Document the tool in this README
2. Add tests in `tests/`
3. Make scripts executable (`chmod +x`)
4. Use Python 3.12+ standard library where possible
5. Follow project coding conventions

## Reference

- **Mission Charter:** `../MISSION_CHARTER.md`
- **Example Deliverable:** `../docs/CHARTER_IMPLEMENTATION_EXAMPLE.md`
- **Tests:** `../tests/test_charter_validator.py`
- **CI Workflow:** `../.github/workflows/charter-compliance.yml`
