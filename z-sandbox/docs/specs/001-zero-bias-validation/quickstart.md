# Quickstart: Zero-Bias Resonance Validation

## Prerequisites

- Java 17+, Gradle 8.14 (wrapper installs automatically)
- Python 3.12.3 with `pip install -r requirements.txt`
- Apple M1 Max or equivalent; ensure `PYTHONPATH=python`
- Feature branch checked out: `001-zero-bias-validation`

## 1. Freeze Context

Run the freeze context script to capture environment details:

```bash
./scripts/freeze_context.sh
```

This records:
- Git commit SHA
- JVM version
- Gradle version
- Python version

Files are saved to `specs/001-zero-bias-validation/validation/` for reproducibility.

## 2. Zero-Bias Success Run (no bias flag)

```bash
./gradlew run --args="137524771864208156028430259349934309717 \
  --mc-digits=320 \
  --samples=1800 \
  --k-lo=0.24 \
  --k-hi=0.32 \
  --k-step=0.0001 \
  --m-span=7 \
  --J=6 \
  --threshold=0.972"
```

Artifacts (auto or manual):

- `results/legit_<ts>/config.json`
- `results/legit_<ts>/factors.txt`
- `results/legit_<ts>/provenance.txt`
- `results/legit_<ts>/run.log`

Ensure `config.json` includes: `dirichlet_normalized=true`, `snap=phase_corrected_nint`,
`threshold`, `J`, `k_lo`, `k_hi`, `k_step`, `m_span`, `precision`, `seed`, commit SHA.

## 3. Controls

**Control A – Tight Gate**

```bash
./gradlew run --args="... --threshold=0.985"
```

Expected: “No factor found”. Save log to `results/controls/gate_tight.log`.

**Control B – Snap Disabled**

```bash
./gradlew run --args="... --snap-mode=off"
```

Expected: Failure. Save log to `results/controls/snap_disabled.log`.

## 4. Novelty Audit

```bash
python python/zero_bias/novelty_audit.py \
  --output specs/001-zero-bias-validation/audit/no_classical_java.txt
```

## 5. Auto-Bias Fallback (only if zero-bias fails)

```bash
python python/zero_bias/auto_bias_estimator.py \
  --N 137524771864208156028430259349934309717 \
  --output specs/001-zero-bias-validation/validation/auto_bias.json
```

Use generated bias with same Gradle command; label artifacts as `auto_bias`.

## 6. Validation & Reporting

```bash
python tools/validate_charter.py specs/001-zero-bias-validation/report.md
./gradlew test --tests org.zfifteen.sandbox.GeometricResonanceFactorizerTest
pytest tests/zero_bias
```

Update PR description with:

- Zero-bias success evidence
- Control logs
- Novelty audit path
- Statement relegating ln(q/p) runs to calibration history
