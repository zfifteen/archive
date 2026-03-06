# Zero-Bias Validation Artifact Schemas

This document defines the schemas for artifacts generated during zero-bias resonance validation runs.

## JSON Schemas

### config.json
Configuration and parameters for the factorization run.

```json
{
  "type": "object",
  "required": [
    "run_id",
    "commit_sha",
    "jvm_version",
    "gradle_version",
    "precision_digits",
    "dirichlet_normalized",
    "snap_mode",
    "bias_present",
    "threshold",
    "J",
    "k_lo",
    "k_hi",
    "k_step",
    "m_span",
    "samples",
    "seed"
  ],
  "properties": {
    "run_id": {
      "type": "string",
      "description": "Timestamped identifier (e.g., legit_20251108_1200UTC)"
    },
    "commit_sha": {
      "type": "string",
      "description": "Git commit hash used for the run"
    },
    "jvm_version": {
      "type": "string",
      "description": "Java version"
    },
    "gradle_version": {
      "type": "string",
      "description": "Gradle version"
    },
    "precision_digits": {
      "type": "integer",
      "minimum": 300,
      "description": "BigDecimal precision in digits"
    },
    "dirichlet_normalized": {
      "type": "boolean",
      "const": true,
      "description": "Whether Dirichlet gate is normalized to (2J+1)"
    },
    "snap_mode": {
      "type": "string",
      "enum": ["phase_corrected_nint"],
      "description": "Phase-corrected nearest-integer snap mode"
    },
    "bias_present": {
      "type": "boolean",
      "const": false,
      "description": "Zero-bias invariant flag"
    },
    "threshold": {
      "type": "number",
      "description": "Normalized Dirichlet amplitude threshold"
    },
    "J": {
      "type": "integer",
      "description": "Dirichlet kernel half-width"
    },
    "k_lo": {
      "type": "number",
      "description": "Lower bound of k sweep range"
    },
    "k_hi": {
      "type": "number",
      "description": "Upper bound of k sweep range"
    },
    "k_step": {
      "type": "number",
      "description": "Step size for k sweep"
    },
    "m_span": {
      "type": "integer",
      "description": "Radius for m scan around m0"
    },
    "samples": {
      "type": "integer",
      "description": "Number of QMC samples"
    },
    "seed": {
      "type": "integer",
      "const": 42,
      "description": "RNG seed for deterministic results"
    }
  }
}
```

### auto_bias.json (Fallback Estimator Output)
Derived bias from N-only calculations.

```json
{
  "type": "object",
  "required": [
    "estimator_id",
    "derived_bias",
    "method",
    "input_domain",
    "seed",
    "timestamp",
    "commit_sha"
  ],
  "properties": {
    "estimator_id": {
      "type": "string",
      "description": "Unique estimator run identifier"
    },
    "derived_bias": {
      "type": ["number", "null"],
      "description": "Estimated bias value or null if unused"
    },
    "method": {
      "type": "string",
      "description": "Estimation method (e.g., curvature_residual_fit)"
    },
    "input_domain": {
      "type": "object",
      "description": "K-grid and residual statistics used for estimation"
    },
    "seed": {
      "type": "integer",
      "const": 42,
      "description": "RNG seed used in estimation"
    },
    "timestamp": {
      "type": "string",
      "format": "date-time",
      "description": "ISO 8601 timestamp"
    },
    "commit_sha": {
      "type": "string",
      "description": "Git commit hash"
    },
    "notes": {
      "type": "string",
      "description": "Optional notes on estimation process"
    }
  }
}
```

## Text File Formats

### factors.txt
Factorization results with verification.

```
p = <prime_factor_p>
q = <prime_factor_q>
verification = <boolean>
```

- `p` and `q`: Prime factors as strings
- `verification`: Boolean indicating p*q == N and both are prime

### provenance.txt
Run metadata and command information.

```
run_id: <timestamped_id>
command: <full_gradle_command>
environment: <key_value_pairs>
timestamp: <iso8601>
commit_sha: <git_hash>
bias_source: <"zero-bias"|"N-only">
```

## CSV Schemas

### validation_manifest.csv
Summary of all validation artifacts.

| Column | Type | Description |
|--------|------|-------------|
| run_id | string | Unique run identifier |
| artifact_type | string | Type of artifact (config, factors, log, etc.) |
| path | string | Relative path to artifact |
| checksum | string | SHA256 checksum |
| timestamp | datetime | ISO 8601 creation time |
| bias_present | boolean | Bias flag (always false for success runs) |

## Log Format Standards

### run.log
Structured log output from factorization run.

```
timestamp level message
```

Where:
- `timestamp`: ISO 8601 with milliseconds
- `level`: INFO, WARN, ERROR
- `message`: Structured message with key=value pairs

Example:
```
2025-11-08T12:00:00.123Z INFO dirichlet_normalized=true snap_mode=phase_corrected_nint bias_present=false
2025-11-08T12:05:00.456Z INFO FOUND p=... q=...
```

## Validation Rules

All artifacts must:
- Use UTF-8 encoding
- Have deterministic column ordering
- Include required fields as specified
- Be stored under `specs/001-zero-bias-validation/validation/`
- Reference commit SHA and run ID for traceability