---

description: "Task list template for feature implementation"
---

# Tasks: [FEATURE NAME]

**Input**: Design documents from `/specs/[###-feature-name]/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: The examples below include test tasks. Tests are OPTIONAL - only include them if explicitly requested in the feature specification.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Category] [Story] Description`

- **[ID]**: Task identifier (e.g., T001, T042-MED-3)
- **[P]**: Can run in parallel (different files, no dependencies)
- **[Category]**: Constitutional principle (SEC, MED, OFF, ACC, OPT, GEN) - see below
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Task Categories by Constitutional Principle

Use these prefixes in task IDs to track constitutional compliance:

- **SEC**: Security & Privacy tasks (keychain, encryption, CSP, audit logging)
- **MED**: Medical Data Integrity tasks (FHIR parsing, DICOM handling, reference ranges)
- **OFF**: Offline-First tasks (cache strategy, sync resumption, fallback UI)
- **ACC**: Accessibility tasks (WCAG compliance, tooltips, keyboard nav, dark mode)
- **OPT**: Apple Silicon Optimization tasks (ARM64 builds, Metal GPU, performance)
- **GEN**: General implementation tasks (not tied to specific principle)

**Example**: `T042-MED-3 [US2] Validate FHIR Observation resources against R4 spec in src/fhir/validator.ts`

## Path Conventions

- **Single project**: `src/`, `tests/` at repository root
- **Web app**: `backend/src/`, `frontend/src/`
- **Mobile**: `api/src/`, `ios/src/` or `android/src/`
- Paths shown below assume single project - adjust based on plan.md structure

<!-- 
  ============================================================================
  IMPORTANT: The tasks below are SAMPLE TASKS for illustration purposes only.
  
  The /speckit.tasks command MUST replace these with actual tasks based on:
  - User stories from spec.md (with their priorities P1, P2, P3...)
  - Feature requirements from plan.md
  - Entities from data-model.md
  - Endpoints from contracts/
  
  Tasks MUST be organized by user story so each story can be:
  - Implemented independently
  - Tested independently
  - Delivered as an MVP increment
  
  DO NOT keep these sample tasks in the generated tasks.md file.
  ============================================================================
-->

## Phase 0: Security & Privacy Infrastructure *(MANDATORY for medical data features)*

**Purpose**: Establish constitutional security requirements BEFORE any medical data is touched

**⚠️ CRITICAL**: This phase is MANDATORY for any feature handling PHI/medical data. No FHIR, DICOM, or patient data work can begin until complete.

- [ ] T000-SEC-1 Configure Electron with context isolation enabled and nodeIntegration disabled
- [ ] T000-SEC-2 Implement macOS Keychain wrapper using keytar for OAuth token storage
- [ ] T000-SEC-3 Initialize SQLite with SQLCipher encryption (user-derived key)
- [ ] T000-SEC-4 Create PHI sanitization utility for logging (strips all medical data from logs/errors)
- [ ] T000-SEC-5 [P] Set up Content Security Policy headers in Electron main process
- [ ] T000-SEC-6 [P] Create audit logging framework (append-only, separate database from medical data)
- [ ] T000-SEC-7 [P] Implement FileVault status check on app startup (warn if encryption disabled)

**Checkpoint**: Security foundation complete - medical data work can now begin

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [ ] T001 Create project structure per implementation plan
- [ ] T002 Initialize [language] project with [framework] dependencies
- [ ] T003 [P] Configure linting and formatting tools (TypeScript strict mode, ESLint, Prettier)
- [ ] T004 [P] Configure git hooks for pre-commit checks (no API keys, no PHI in diffs)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

Examples of foundational tasks (adjust based on your project):

- [ ] T004 Setup database schema and migrations framework
- [ ] T005 [P] Implement authentication/authorization framework
- [ ] T006 [P] Setup API routing and middleware structure
- [ ] T007 Create base models/entities that all stories depend on
- [ ] T008 Configure error handling and logging infrastructure
- [ ] T009 Setup environment configuration management

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - [Title] (Priority: P1) 🎯 MVP

**Goal**: [Brief description of what this story delivers]

**Independent Test**: [How to verify this story works on its own]

### Tests for User Story 1 (OPTIONAL - only if tests requested) ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T010 [P] [US1] Contract test for [endpoint] in tests/contract/test_[name].py
- [ ] T011 [P] [US1] Integration test for [user journey] in tests/integration/test_[name].py

### Implementation for User Story 1

- [ ] T012 [P] [US1] Create [Entity1] model in src/models/[entity1].py
- [ ] T013 [P] [US1] Create [Entity2] model in src/models/[entity2].py
- [ ] T014 [US1] Implement [Service] in src/services/[service].py (depends on T012, T013)
- [ ] T015 [US1] Implement [endpoint/feature] in src/[location]/[file].py
- [ ] T016 [US1] Add validation and error handling
- [ ] T017 [US1] Add logging for user story 1 operations

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - [Title] (Priority: P2)

**Goal**: [Brief description of what this story delivers]

**Independent Test**: [How to verify this story works on its own]

### Tests for User Story 2 (OPTIONAL - only if tests requested) ⚠️

- [ ] T018 [P] [US2] Contract test for [endpoint] in tests/contract/test_[name].py
- [ ] T019 [P] [US2] Integration test for [user journey] in tests/integration/test_[name].py

### Implementation for User Story 2

- [ ] T020 [P] [US2] Create [Entity] model in src/models/[entity].py
- [ ] T021 [US2] Implement [Service] in src/services/[service].py
- [ ] T022 [US2] Implement [endpoint/feature] in src/[location]/[file].py
- [ ] T023 [US2] Integrate with User Story 1 components (if needed)

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - [Title] (Priority: P3)

**Goal**: [Brief description of what this story delivers]

**Independent Test**: [How to verify this story works on its own]

### Tests for User Story 3 (OPTIONAL - only if tests requested) ⚠️

- [ ] T024 [P] [US3] Contract test for [endpoint] in tests/contract/test_[name].py
- [ ] T025 [P] [US3] Integration test for [user journey] in tests/integration/test_[name].py

### Implementation for User Story 3

- [ ] T026 [P] [US3] Create [Entity] model in src/models/[entity].py
- [ ] T027 [US3] Implement [Service] in src/services/[service].py
- [ ] T028 [US3] Implement [endpoint/feature] in src/[location]/[file].py

**Checkpoint**: All user stories should now be independently functional

---

[Add more user story phases as needed, following the same pattern]

---

## Phase N: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] TXXX [P] Documentation updates in docs/
- [ ] TXXX Code cleanup and refactoring
- [ ] TXXX Performance optimization across all stories
- [ ] TXXX [P] Additional unit tests (if requested) in tests/unit/
- [ ] TXXX Security hardening
- [ ] TXXX Run quickstart.md validation

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3)
- **Polish (Final Phase)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - May integrate with US1 but should be independently testable
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - May integrate with US1/US2 but should be independently testable

### Within Each User Story

- Tests (if included) MUST be written and FAIL before implementation
- Models before services
- Services before endpoints
- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel (within Phase 2)
- Once Foundational phase completes, all user stories can start in parallel (if team capacity allows)
- All tests for a user story marked [P] can run in parallel
- Models within a story marked [P] can run in parallel
- Different user stories can be worked on in parallel by different team members

---

## Parallel Example: User Story 1

```bash
# Launch all tests for User Story 1 together (if tests requested):
Task: "Contract test for [endpoint] in tests/contract/test_[name].py"
Task: "Integration test for [user journey] in tests/integration/test_[name].py"

# Launch all models for User Story 1 together:
Task: "Create [Entity1] model in src/models/[entity1].py"
Task: "Create [Entity2] model in src/models/[entity2].py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Test User Story 1 independently
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 → Test independently → Deploy/Demo
4. Add User Story 3 → Test independently → Deploy/Demo
5. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1
   - Developer B: User Story 2
   - Developer C: User Story 3
3. Stories complete and integrate independently

---

## Medical Data Validation Checkpoints

After each user story implementation (if feature handles PHI/medical data):

### Data Integrity Verification
- [ ] FHIR resources have raw JSON stored alongside parsed fields
- [ ] Lab values include reference ranges and units
- [ ] Timestamps are ISO 8601 format with timezone
- [ ] No DICOM files were modified (only display transformations)
- [ ] LOINC codes preserved for laboratory observations

### Security Verification
- [ ] No PHI/PII appears in application logs or console output
- [ ] OAuth tokens only in macOS Keychain (verify with security audit)
- [ ] Database encrypted at rest (SQLCipher enabled and tested)
- [ ] Audit trail complete for all data access operations
- [ ] FileVault status check passed on startup

### Offline Verification
- [ ] Feature works with network disabled (test airplane mode)
- [ ] Graceful degradation tested (API unavailable scenarios)
- [ ] UI state persists across app restarts (SQLite state restoration)
- [ ] Sync resumption works after interruption

### Accessibility Verification
- [ ] WCAG 2.1 AA compliance verified (contrast ratios, keyboard nav)
- [ ] Medical terms have tooltips visible and understandable
- [ ] Dark mode high-contrast verified
- [ ] Keyboard shortcuts functional for all critical actions
- [ ] Screen reader announces medical data correctly

## Notes

- [P] tasks = different files, no dependencies
- [Category] prefix tracks constitutional principle alignment
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Verify tests fail before implementing (TDD for constitutional compliance)
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Run Medical Data Validation Checkpoints after each user story
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
