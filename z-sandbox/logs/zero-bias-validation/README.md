# Zero-Bias Validation Logging Guidelines

This directory contains structured logs for zero-bias resonance validation runs. All logging must follow these guidelines to ensure auditability and reproducibility.

## Log File Naming Convention

- `zero_bias_success.log`: Primary successful run logs
- `control_<control_id>.log`: Control experiment logs (e.g., `control_gate_tight.log`)
- `estimator_<timestamp>.log`: Auto-bias estimator logs

## Structured Log Format

All log entries must use the following format:

```
<timestamp> <level> <message>
```

Where:
- `<timestamp>`: ISO 8601 with timezone (e.g., `2025-11-08T12:00:00.123Z`)
- `<level>`: `INFO`, `WARN`, `ERROR`, `DEBUG`
- `<message>`: Structured key=value pairs, space-separated

## Required Fields

Every log entry must include these fields:

- `commit_sha`: Git commit hash (e.g., `commit_sha=abc123...`)
- `precision`: BigDecimal precision digits (e.g., `precision=320`)
- `seed`: RNG seed (e.g., `seed=42`)

## Zero-Bias Specific Fields

Success runs must include:

- `dirichlet_normalized`: Must be `true` (e.g., `dirichlet_normalized=true`)
- `snap_mode`: Must be `phase_corrected_nint` (e.g., `snap_mode=phase_corrected_nint`)
- `bias_present`: Must be `false` (e.g., `bias_present=false`)

## Control Experiment Fields

Control logs must include:

- `control_id`: Identifier (e.g., `gate_tight`, `snap_disabled`)
- `expected_outcome`: Expected result (e.g., `expected_outcome=no_factors_found`)
- `observed_outcome`: Actual result

## Estimator Fields

Auto-bias estimator logs must include:

- `estimator_method`: Method used (e.g., `curvature_residual_fit`)
- `derived_bias`: Computed bias value or `null`
- `residual_stats`: Summary statistics of residuals

## Example Log Entries

### Success Run
```
2025-11-08T12:00:00.123Z INFO commit_sha=abc123def456 precision=320 seed=42 dirichlet_normalized=true snap_mode=phase_corrected_nint bias_present=false threshold=0.972 J=6 k_lo=0.24 k_hi=0.32 k_step=0.0001 m_span=7 samples=1800
2025-11-08T12:05:00.456Z INFO FOUND p=123456789012345678901234567890123456789012345678901234567890 q=98765432109876543210987654321098765432109876543210987654321 verification=true
```

### Control Run
```
2025-11-08T13:00:00.123Z INFO commit_sha=abc123def456 precision=320 seed=42 control_id=gate_tight expected_outcome=no_factors_found observed_outcome=no_factors_found threshold=0.985
```

### Estimator Run
```
2025-11-08T14:00:00.123Z INFO commit_sha=abc123def456 estimator_method=curvature_residual_fit derived_bias=0.00234 residual_stats=mean=1.2e-15,std=3.4e-16
```

## Implementation Notes

- Use Java's `java.time.Instant` for timestamps
- Ensure logs are written to stderr for CLI runs
- Include JVM version and system info in header entries
- Logs must be machine-parseable for automated validation
- Missing required fields constitute a critical failure

## Validation

Logs are validated by `tools/analysis/log_validator.py` which checks:
- Format compliance
- Required field presence
- Zero-bias invariant enforcement
- Timestamp ordering