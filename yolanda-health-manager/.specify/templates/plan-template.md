# Implementation Plan: [FEATURE]

**Branch**: `[###-feature-name]` | **Date**: [DATE] | **Spec**: [link]
**Input**: Feature specification from `/specs/[###-feature-name]/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

[Extract from feature spec: primary requirement + technical approach from research]

## Technical Context

<!--
  ACTION REQUIRED: Replace the content in this section with the technical details
  for the project. The structure here is presented in advisory capacity to guide
  the iteration process.
-->

**Language/Version**: [e.g., Python 3.11, Swift 5.9, Rust 1.75 or NEEDS CLARIFICATION]
**Primary Dependencies**: [e.g., FastAPI, UIKit, LLVM or NEEDS CLARIFICATION]
**Storage**: [if applicable, e.g., PostgreSQL, CoreData, files or N/A]
**Testing**: [e.g., pytest, XCTest, cargo test or NEEDS CLARIFICATION]
**Target Platform**: [e.g., Linux server, iOS 15+, WASM or NEEDS CLARIFICATION]
**Project Type**: [single/web/mobile - determines source structure]
**Performance Goals**: [domain-specific, e.g., 1000 req/s, 10k lines/sec, 60 fps or NEEDS CLARIFICATION]
**Constraints**: [domain-specific, e.g., <200ms p95, <100MB memory, offline-capable or NEEDS CLARIFICATION]
**Scale/Scope**: [domain-specific, e.g., 10k users, 1M LOC, 50 screens or NEEDS CLARIFICATION]

### Medical Application Context *(if handling PHI/medical data)*

**Medical Data Sources**: [e.g., FHIR R4 APIs, DICOM files, HL7 messages or N/A]
**FHIR Resources Needed**: [e.g., Patient, Observation, Condition, MedicationRequest or N/A]
**DICOM Modalities**: [e.g., MR (MRI), CT, XR (X-ray), US (ultrasound) or N/A]
**AI/ML Context**: [e.g., xAI/Grok for medical explanations, local ML models or N/A]
**Data Privacy Strategy**: [SQLCipher encryption, macOS Keychain for tokens, audit logging]
**Offline Capability**: [Which features work offline, sync strategy, cache duration]
**Accessibility Target**: [WCAG 2.1 AA compliance, keyboard nav coverage, medical term tooltips]
**Apple Silicon**: [ARM64 native build, Metal GPU usage, memory budget <2GB, startup <3s]

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

<!--
  CRITICAL: Review .specify/memory/constitution.md before proceeding.
  All features MUST comply with constitutional principles.
  Check applicable items - justify any "unchecked" in Complexity Tracking.
-->

### I. Security & Privacy First (NON-NEGOTIABLE)
- [ ] No cloud storage or sync dependencies identified
- [ ] OAuth tokens use macOS Keychain (keytar library)
- [ ] SQLite encrypted with SQLCipher (user-derived key)
- [ ] No PHI/PII in logs, errors, or console output
- [ ] Electron context isolation enabled, nodeIntegration disabled
- [ ] Content Security Policy configured (whitelisted domains only)
- [ ] Audit logging implemented (append-only, separate from medical DB)

### II. Medical Data Integrity
- [ ] FHIR resources preserve raw JSON alongside parsed fields
- [ ] DICOM files are read-only (display transformations only, never modify source)
- [ ] Lab values store reference ranges and units with every observation
- [ ] Timestamps use ISO 8601 format with timezone information
- [ ] Data sync operations are idempotent and resumable
- [ ] LOINC codes preserved for laboratory results
- [ ] FHIR R4 validation before database writes

### III. Offline-First Architecture
- [ ] Core features work without network connectivity
- [ ] FHIR sync failures don't block app startup or data viewing
- [ ] AI assistant degrades gracefully when API unavailable (cached responses or informative message)
- [ ] UI state persists to SQLite for session restoration
- [ ] Local cache strategy defined with appropriate TTL

### IV. Accessibility & Caregiver Focus
- [ ] WCAG 2.1 AA compliance plan defined
- [ ] Medical terminology tooltips/explanations implemented
- [ ] Font sizes adjustable without breaking layout
- [ ] High-contrast dark mode for late-night use
- [ ] Keyboard shortcuts for critical actions (timeline, DICOM, AI chat)
- [ ] Screen reader compatibility verified
- [ ] Color-blind friendly visual indicators

### V. Apple Silicon Optimization
- [ ] Native ARM64 build configuration (electron-builder)
- [ ] Metal GPU acceleration for DICOM rendering considered
- [ ] Python runtime is ARM64 native
- [ ] Memory budget defined and monitored (<2GB with all DICOM loaded)
- [ ] App startup performance target <3 seconds on M1 Max
- [ ] SQLite queries optimized (<1ms for common operations)

**GATE STATUS**: [PASS / CONDITIONAL PASS / FAIL]

**Violations Requiring Justification**: [List any unchecked items with detailed rationale in Complexity Tracking section below]

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)
<!--
  ACTION REQUIRED: Replace the placeholder tree below with the concrete layout
  for this feature. Delete unused options and expand the chosen structure with
  real paths (e.g., apps/admin, packages/something). The delivered plan must
  not include Option labels.
-->

```text
# [REMOVE IF UNUSED] Option 1: Single project (DEFAULT)
src/
├── models/
├── services/
├── cli/
└── lib/

tests/
├── contract/
├── integration/
└── unit/

# [REMOVE IF UNUSED] Option 2: Web application (when "frontend" + "backend" detected)
backend/
├── src/
│   ├── models/
│   ├── services/
│   └── api/
└── tests/

frontend/
├── src/
│   ├── components/
│   ├── pages/
│   └── services/
└── tests/

# [REMOVE IF UNUSED] Option 3: Mobile + API (when "iOS/Android" detected)
api/
└── [same as backend above]

ios/ or android/
└── [platform-specific structure: feature modules, UI flows, platform tests]
```

**Structure Decision**: [Document the selected structure and reference the real
directories captured above]

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., Cloud backup option] | [Disaster recovery for critical medical data] | [User explicitly requested cloud sync - VIOLATES Security & Privacy First - REJECTED] |
| [e.g., Third-party analytics] | [Usage tracking for feature prioritization] | [Violates zero-telemetry principle - use local audit logs instead] |
| [e.g., Plaintext database] | [Performance optimization] | [Security non-negotiable - SQLCipher overhead acceptable for medical data] |

**Note**: Violations of Principles I-III (Security, Data Integrity, Offline-First) are NON-NEGOTIABLE and MUST be rejected. Only Principles IV-V may have justified exceptions with user approval.
