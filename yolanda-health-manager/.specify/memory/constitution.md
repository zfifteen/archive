<!--
Sync Impact Report:
Version change: [TEMPLATE] → 1.0.0
Modified principles: All initial definitions
Added sections: Core Principles (5), Security & Privacy, Medical Data Standards, Governance
Removed sections: Generic template placeholders
Templates requiring updates:
  ✅ constitution.md (this file)
  ⚠ spec-template.md - pending alignment with health data principles
  ⚠ plan-template.md - pending security/HIPAA checklist integration
  ⚠ tasks-template.md - pending medical data task categories
Follow-up TODOs: None - all placeholders filled
-->

# Yolanda Evans Health Management System Constitution

## Core Principles

### I. Security & Privacy First (NON-NEGOTIABLE)

All medical data MUST remain local with zero cloud dependencies. OAuth2 tokens MUST be stored in macOS Keychain only. Database encryption (SQLCipher) is MANDATORY for all patient data at rest. No PHI/PII may be logged, transmitted, or stored in plaintext. Context isolation MUST be enabled in Electron with nodeIntegration disabled.

**Rationale**: HIPAA compliance and patient trust require bulletproof data protection. A single security breach undermines the entire caregiver mission.

### II. Medical Data Integrity

All FHIR resources MUST preserve raw JSON from source APIs alongside parsed data. DICOM files MUST never be modified - display transformations only. Lab values MUST store reference ranges and units with every observation. Timestamps MUST be ISO 8601 with timezone. Data sync operations MUST be idempotent and resumable.

**Rationale**: Medical decisions depend on data accuracy. Original source data must be retrievable for verification. Incorrect lab values or imaging data could endanger patient health.

### III. Offline-First Architecture

Core functionality (timeline view, DICOM viewer, medical record access) MUST work without network connectivity. FHIR sync failures MUST NOT block app startup or data viewing. AI assistant MUST gracefully degrade when xAI API is unavailable. All UI state MUST persist to SQLite for session restoration.

**Rationale**: Caregivers need reliable access to medical data regardless of network conditions. Emergency situations cannot wait for API calls.

### IV. Accessibility & Caregiver Focus

UI MUST meet WCAG 2.1 AA standards. Medical terminology MUST have plain-English tooltips/explanations. Font sizes MUST be adjustable for aging eyes. High-contrast dark mode MANDATORY for late-night use. Keyboard shortcuts REQUIRED for all critical actions (navigate timeline, open DICOM, ask AI).

**Rationale**: The primary user is a family caregiver managing complex medical conditions. Cognitive load must be minimized. Accessibility is not optional.

### V. Apple Silicon Optimization

All builds MUST target native ARM64 architecture. DICOM rendering MUST leverage Metal GPU acceleration where available. Python runtime MUST be ARM64 native. Memory usage MUST stay under 2GB with all DICOM loaded (32GB RAM available). App startup MUST complete in under 3 seconds on M1 Max.

**Rationale**: The target hardware (M1 Max MacBook Pro) enables premium performance. Users should not experience lag when reviewing medical imaging or lab trends.

## Security & Privacy Standards

### Data Storage Requirements

- SQLite database MUST use SQLCipher encryption with user-derived key
- DICOM files MAY remain unencrypted on disk (already protected by FileVault)
- OAuth tokens MUST use macOS Keychain (keytar library)
- Environment variables for API keys MUST NOT be committed to git
- `.env` files MUST be in `.gitignore`
- Backup files MUST preserve encryption (export format: encrypted SQLite)

### Network Security

- All HTTPS connections MUST validate certificates (no --insecure)
- Content Security Policy MUST be enforced in Electron renderer
- Only whitelisted domains permitted: `apis.upmchp.com`, `api.x.ai`
- No third-party analytics, crash reporting, or telemetry
- FHIR API rate limiting MUST respect 429 responses with exponential backoff

### Audit & Compliance

- Every data access operation MUST log: timestamp, resource type, user action
- Audit logs MUST be append-only and stored separately from medical database
- User MUST be able to export full audit trail
- No automatic data deletion - user controls data lifecycle

## Medical Data Standards

### FHIR Resource Handling

- Support FHIR R4 specification only (no R5 until widely adopted)
- Parse `Patient`, `Condition`, `Observation`, `MedicationRequest`, `Procedure` resources
- Store both structured fields AND raw JSON for future extensibility
- Validate required fields per FHIR spec before database insert
- Handle pagination for large result sets (bundle.link.next)

### DICOM Processing

- Support modalities: MR (MRI), CT, XR (X-ray) - prioritize MR for current dataset
- Parse DICOM metadata without loading pixel data for performance
- Display using Cornerstone.js library (industry standard)
- Support window/level presets: Soft Tissue, Bone, Brain
- Enable measurements: Length, Angle, Region of Interest
- Annotation persistence via SQLite (not embedded in DICOM files)

### Laboratory Data Presentation

- Flag abnormal values using `interpretation` field (L/H/LL/HH)
- Display reference ranges alongside all numeric values
- Support trend visualization (Recharts line graphs)
- Color coding: Red (abnormal), Yellow (borderline), Green (normal)
- LOINC code preservation for cross-system compatibility

## Development Workflow

### Feature Development Process

1. **Specification**: Create feature spec using `/speckit.specify`
2. **Clarification**: Run `/speckit.clarify` to identify ambiguities
3. **Planning**: Generate technical plan via `/speckit.plan`
4. **Task Breakdown**: Decompose into tasks with `/speckit.tasks`
5. **Implementation**: Execute in phases, Phase 1 complete before Phase 2 starts
6. **Testing**: Unit tests + integration tests + manual acceptance testing
7. **Security Review**: Run security checklist before merging to main

### Testing Requirements

- **Unit Tests**: All FHIR parsers, DICOM metadata extraction, date utilities
- **Integration Tests**: OAuth flow, FHIR sync end-to-end, SQLite CRUD operations
- **Manual Testing**: DICOM viewer rendering, AI chat accuracy, Timeline UX
- **Security Tests**: Token storage verification, database encryption check, CSP enforcement
- **Acceptance Criteria**: Every task must define "done" conditions

### Code Quality Standards

- TypeScript strict mode enabled (no `any` types in production code)
- ESLint + Prettier for consistent formatting
- Git commit messages MUST follow Conventional Commits (feat:, fix:, docs:, etc.)
- No merge to main without passing tests
- Every component MUST have inline documentation (JSDoc for functions)

## Governance

### Constitutional Authority

This constitution supersedes all other development practices. Any PR that violates core principles MUST be rejected regardless of functionality. Principles I-III (Security, Data Integrity, Offline-First) are NON-NEGOTIABLE and cannot be compromised for convenience or speed.

### Amendment Process

1. Propose amendment via GitHub issue with rationale
2. Discussion period (minimum 3 days or until user approval)
3. User (project owner) final approval required
4. Update constitution with version bump:
   - **MAJOR**: Remove/redefine non-negotiable principle
   - **MINOR**: Add new principle or materially expand guidance
   - **PATCH**: Clarifications, typo fixes, wording improvements
5. Propagate changes to all templates (spec, plan, tasks, checklists)
6. Commit message: `docs: amend constitution to vX.Y.Z (summary of changes)`

### Compliance Review

- Every `/speckit.specify` output MUST cite relevant constitutional principles
- Every `/speckit.plan` MUST include security/privacy checklist items
- Every `/speckit.tasks` MUST categorize tasks by principle alignment
- Every PR description MUST reference constitution sections addressed
- Quarterly constitution review to ensure principles remain relevant

### Guidance for AI Agents

When implementing features for this project:
- **Prioritize** user safety over feature velocity
- **Verify** FHIR data types before database writes
- **Test** OAuth token refresh edge cases
- **Document** medical terminology for non-clinical users
- **Confirm** accessibility requirements met (keyboard nav, screen reader support)
- **Question** any requirement that conflicts with Security & Privacy First

**Version**: 1.0.0 | **Ratified**: 2025-11-15 | **Last Amended**: 2025-11-15
