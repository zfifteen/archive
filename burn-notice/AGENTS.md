# AGENTS.md

**Purpose**: This document guides LLM agents working on the burn-notice repository to align with project goals and maintain consistency with the repository owner's intent.

---

## Project Mission

**burn-notice** is a scientifically rigorous framework for computational prompt engineering. The goal is to:

1. **Catalog empirical ground truth** about LLM providers and their models
2. **Document technical strengths and weaknesses** through structured, reproducible research
3. **Generate optimized prompts** based on documented model capabilities, not guesswork

This is **engineering**, not art. Every claim must be verifiable. Every approximation must be corrected to precision. Every source must be cited.

---

## Core Principles

### 1. Precision Over Approximation

**NEVER**:
- Use approximate values ("~1M tokens") when exact values exist (131,072 tokens)
- Rely on third-party sources when official documentation is available
- Include models not officially documented by the provider
- Make claims without citation links to authoritative sources

**ALWAYS**:
- Verify every technical detail against official provider documentation
- Correct approximations to exact values
- Link every claim to its authoritative source
- Remove content that cannot be verified

**Example**: The initial `providers/xai/MODELS.md` included "grok-3-fast" based on third-party sources. This was **incorrect** because xAI's official documentation does not list this model. It was removed.

### 2. Official Sources Are Authoritative

The hierarchy of truth for this repository:

1. **Official provider documentation** (e.g., https://docs.x.ai/docs/models)
2. **Official model cards and technical reports**
3. **Official API specifications**
4. Nothing else

Third-party benchmarks, aggregator sites, and community wikis are **not authoritative** for this project. If a model or capability is not in official docs, it does not exist for our purposes.

### 3. Structure Reflects Intent

The repository structure is deliberate:

```
burn-notice/
├── providers/          # Provider-specific technical ground truth
│   └── [provider]/
│       ├── MODELS.md   # Official model catalog with exact specs
│       └── ...         # Future: strengths/weaknesses research
├── schemas/            # JSON schemas for structured data
├── meta/               # Cross-provider taxonomies (techniques, metrics)
├── LICENSE
├── README.md
└── AGENTS.md           # This file
```

**Each directory has a purpose**:

- **`providers/`**: Empirical facts about specific vendors. Every model entry must match official documentation exactly.
- **`schemas/`**: Machine-readable specifications for how data should be structured.
- **`meta/`**: Cross-cutting concepts like "chain-of-thought reasoning" or "latency metrics" that apply across providers.

### 4. Documentation as Infrastructure

Documentation in this repository is not "nice to have" — it is **load-bearing infrastructure** for systematic prompt engineering.

Every file must be:
- **Complete**: No placeholder text, no "TODO" without tracking
- **Accurate**: Verified against authoritative sources
- **Linked**: Citations to official documentation for every claim
- **Structured**: Follow established patterns (see `providers/xai/MODELS.md` as reference)

---

## Repository Owner Profile

### Work Style

The repository owner is:
- An **independent computational researcher** specializing in algorithms and number theory
- **Precision-first**: Approximations are unacceptable when exact values exist
- **Verification-driven**: Every claim must be tested against authoritative sources
- **Systematically iterative**: Work proceeds in clear stages (draft → verify → refine)

### Technical Context

The owner:
- Writes high-precision code in C99, Python, and Swift
- Publishes reproducible research with rigorous specifications
- Uses multiple LLM assistants (Grok, Copilot, ChatGPT, Gemini, Perplexity) as research tools
- Demands reproducibility in experiments and documentation

### Why This Project Exists

The owner needs LLM usage to be **as precise and reproducible as mathematical algorithms**. When working on prime factorization or algorithm optimization, unreliable tools are worse than no tools.

**burn-notice** exists to make prompt engineering:
- **Predictable**: Understand which model to use for which task
- **Reproducible**: Document exactly what works and why
- **Scientific**: Treat model capabilities as empirically testable hypotheses

---

## Agent Guidelines

### When Adding Provider/Model Documentation

1. **Start with official docs**: Navigate directly to the provider's official model documentation
2. **Extract exact values**: Context windows, pricing, rate limits must be precise
3. **Verify model existence**: If a model is not in official docs, do not include it
4. **Link everything**: Every model, capability, and claim gets a link to official docs
5. **Follow the template**: Use `providers/xai/MODELS.md` as the reference structure

### When Correcting Existing Documentation

1. **Compare against official sources**: Always check current provider documentation
2. **Document what changed**: In commit messages, explicitly list corrections ("REMOVED X", "CORRECTED Y from A to B")
3. **Never assume**: If you're unsure whether a value is correct, verify it
4. **Remove over approximate**: Better to have fewer entries that are correct than many entries with errors

### When Working on Schemas

Schemas in `schemas/` should:
- Define clear, machine-readable structures
- Include examples that validate against the schema
- Link to provider documentation showing where each field comes from
- Use semantic field names that reflect the underlying model architecture

### When Building Meta Taxonomies

Content in `meta/` should:
- Define cross-provider concepts (e.g., "reasoning", "structured outputs")
- Reference specific provider implementations
- Cite research or official documentation for each technique
- Enable systematic comparison across providers

---

## Quality Standards

### For Model Documentation

Every model entry must include:
- ✅ Exact context window in tokens (not "~256K" but "256,000")
- ✅ Precise pricing (input/output per million tokens)
- ✅ Rate limits (tpm and rpm)
- ✅ Official capabilities list (function calling, structured outputs, etc.)
- ✅ Link to official model documentation
- ✅ Modalities (text input, image input, text output, etc.)
- ✅ Research priority (`core`, `secondary`, `document-only`)

### For Technical Claims

Every technical claim must:
- ✅ Be verifiable against official documentation
- ✅ Include a citation link
- ✅ Use exact values, not ranges or approximations
- ✅ Be current (note when last verified)

### For Code and Schemas

All structured data must:
- ✅ Validate against declared schemas
- ✅ Include examples
- ✅ Follow consistent naming conventions
- ✅ Be machine-readable (valid JSON, YAML, etc.)

---

## Common Mistakes to Avoid

### ❌ Including Unofficial Models

**Wrong**: Adding "grok-3-fast" because it appears on third-party model aggregators.

**Right**: Only including models listed in official xAI documentation at https://docs.x.ai/docs/models

### ❌ Approximating When Exact Values Exist

**Wrong**: "Context: ~131K tokens"

**Right**: "Context: 131,072 tokens" (from official docs)

### ❌ Omitting Citation Links

**Wrong**: "Supports function calling and structured outputs."

**Right**: "Supports [function calling](https://docs.x.ai/docs/guides/function-calling) and [structured outputs](https://docs.x.ai/docs/guides/structured-outputs)."

### ❌ Treating Provider Marketing as Technical Fact

**Wrong**: Copying marketing language like "blazingly fast" or "best-in-class."

**Right**: Documenting measurable capabilities like "4M tpm, 480 rpm" and "2,000,000 token context window."

### ❌ Leaving Incomplete or TODO Content

**Wrong**: "TODO: Add pricing information later."

**Right**: Either complete the section with accurate data from official docs, or file an issue to track the work.

---

## Working with This Repository

### Step-by-Step: Adding a New Provider

1. Create `providers/[provider-name]/` directory
2. Navigate to the provider's official model documentation
3. Create `MODELS.md` following the template from `providers/xai/MODELS.md`
4. For each model:
   - Extract exact technical specifications
   - Link to official documentation
   - Verify pricing and rate limits
   - Document capabilities with citation links
5. Add provider-level metadata (API base, knowledge cutoff, etc.)
6. Commit with detailed message explaining sources

### Step-by-Step: Updating Existing Documentation

1. Check the provider's current official documentation
2. Compare against the repository's version
3. Note discrepancies (models added/removed, specs changed)
4. Update with exact values from official docs
5. Commit with message listing specific changes ("CORRECTED X", "ADDED Y", "REMOVED Z")

### Step-by-Step: Validating Documentation

1. Open the official provider documentation
2. For each model in the repo:
   - Verify model ID exists officially
   - Check context window matches exactly
   - Confirm pricing is current
   - Validate capabilities list
3. Flag any discrepancies for correction
4. Update "Last verified" date after validation

---

## Reference: Exemplar Documentation

**`providers/xai/MODELS.md`** is the current reference standard. It demonstrates:

✅ **100% alignment with official documentation**  
✅ **Comprehensive citation links**  
✅ **Exact technical values** (not approximations)  
✅ **Structured, consistent format**  
✅ **Clear research priorities**  
✅ **Provider-specific and model-specific sections**  
✅ **Migration notes and technical details**  
✅ **Knowledge cutoff date and verification timestamp**  

When in doubt about format, structure, or level of detail, consult this file.

---

## Commit Message Standards

### For New Content

```
Add [provider] model inventory documentation

Created MODELS.md for [provider] based on official documentation.
- Documented X models with full specifications
- Linked to official docs for all claims
- Verified against https://[official-url] on [date]
```

### For Corrections

```
Align MODELS.md 100% with official [provider] documentation

Major corrections based on official docs:
- REMOVED [model-x] (does not exist in official docs)
- CORRECTED [field]: [old-value] → [new-value]
- ADDED [model-y] (newly documented by provider)
- ADDED pricing, rate limits, capability flags
```

### For Schemas

```
Add [schema-name].schema.json for [purpose]

Defines structure for [use-case].
- Required fields: [list]
- Optional fields: [list]
- Example: [link or inline]
- Validation: [tool/method]
```

---

## Summary: What Success Looks Like

When working on burn-notice, **success** means:

1. ✅ Every technical claim is **verifiable** against official documentation
2. ✅ Every approximation is **corrected** to an exact value
3. ✅ Every model listed **exists** in official provider docs
4. ✅ Every capability **links** to authoritative documentation
5. ✅ Repository structure **reflects** systematic organization
6. ✅ Commit messages **document** what changed and why
7. ✅ Documentation serves as **reliable infrastructure** for prompt engineering research

This repository is not a collection of notes — it is **computational infrastructure** for reproducible, scientific prompt engineering.

---

**Last Updated**: December 28, 2025  
**Reference Implementation**: `providers/xai/MODELS.md`  
**Contact**: Repository owner via GitHub issues
