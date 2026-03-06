# Data Model: Initial Analysis

## RequirementRecord
- **Description**: Canonical representation of each functional or non-functional requirement parsed
  from spec/plan artifacts.
- **Fields**:
  - `key` (string, required) – slug such as `fr-001`.
  - `section` (enum: spec, plan) – origin document.
  - `priority` (enum: P1/P2/P3) – inferred from spec story priority or explicit tags.
  - `text` (string) – normalized requirement statement.
  - `charter_elements` (list<string>) – Mission Charter sections satisfied by the requirement.
- **Validation Rules**:
  - Keys must be unique within the feature directory.
  - Text must include an observable verb + measurable outcome; otherwise analyzer emits ambiguity finding.

## TaskRecord
- **Description**: Structured view of tasks defined in `tasks.md`.
- **Fields**:
  - `id` (string) – e.g., `T012`.
  - `phase` (string) – Phase designation from tasks file.
  - `parallelizable` (bool) – derived from `[P]` marker.
  - `story_ref` (string) – user story association.
  - `description` (string) – normalized action statement.
  - `paths` (list<string>) – filesystem references extracted from description.
- **Validation Rules**:
  - Paths must exist or be planned directories within repo structure.
  - Each task must reference at least one story or requirement.

## Finding
- **Description**: Output row within analyzer report summarizing an issue.
- **Fields**:
  - `id` (string) – stable identifier (e.g., `A1`).
  - `category` (enum) – Duplication, Ambiguity, Underspecification, Constitution, Coverage, Inconsistency.
  - `severity` (enum) – Critical, High, Medium, Low.
  - `locations` (list<string>) – file:line references.
  - `summary` (string) – concise description.
  - `recommendation` (string) – remediation guidance.
- **Validation Rules**:
  - Severity derived from declarative rules stored in `docs/methods/initial-analysis/rules.yaml`.
  - At most 50 findings per run; overflow triggers summary entry.

## CoverageMap
- **Description**: Bidirectional mapping between RequirementRecords and TaskRecords.
- **Fields**:
  - `requirement_key` (string).
  - `has_task` (bool).
  - `task_ids` (list<string>).
  - `notes` (string) – explanation for missing coverage or special handling.
- **Validation Rules**:
  - Coverage rows generated for every requirement (functional + non-functional).
  - Missing tasks flagged with severity based on requirement priority.

## ManifestEntry
- **Description**: Portion of Mission Charter compliance manifest emitted per analyzer run.
- **Fields**:
  - `element` (string) – Charter element name.
  - `present` (bool).
  - `location` (string) – path + line reference.
  - `notes` (string) – context or remediation.
- **Validation Rules**:
  - All 10 Charter elements must appear; missing element automatically sets `present=false` and raises Critical finding.
