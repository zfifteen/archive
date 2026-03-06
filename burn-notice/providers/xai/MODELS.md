# xAI / Grok Model Inventory

**Official Reference**: [xAI Models and Pricing](https://docs.x.ai/docs/models)

This document catalogs xAI's officially documented Grok models, with a focus on technical traits relevant for prompt design and provider-level research. All information is sourced from xAI's official documentation.

- **Provider**: xAI (Grok)
- **API base**: `https://api.x.ai` ([OpenAI-compatible surface](https://docs.x.ai/docs/api-reference))
- **Modalities**: text, code, vision/multimodal (varies by model family)
- **Knowledge cutoff**: November 2024 for Grok 3 and Grok 4 models
- **Documentation**: https://docs.x.ai/docs

---

## Legend

- **Model ID**: Official model identifier for API calls
- **Family**: High-level group (Grok 4.1 Fast, Grok 4, Grok 3, Grok 2 / legacy, Code / specialized)
- **Tier**: Frontier reasoning vs. fast/cost-optimized vs. legacy
- **Context**: Maximum context window in tokens ([official docs](https://docs.x.ai/docs/models#context-window))
- **Modalities**: Input/output capabilities (text, image, code)
- **Capabilities**: Official feature flags from xAI
- **Rate Limits**: Tokens per minute (tpm) and requests per minute (rpm)
- **Pricing**: Input/output cost per million tokens ([pricing details](https://docs.x.ai/docs/models#model-pricing))
- **Research**: Your intent for this repo (`core`, `secondary`, `document-only`)

---

## Frontier 4.1 Fast Family

**Official Page**: [Grok 4.1 Fast](https://docs.x.ai/docs/models/grok-4-1-fast-reasoning)

xAI describes these as "frontier multimodal models optimized specifically for high-performance agentic tool calling."

**Shared Features**:
- Function calling
- Structured outputs
- Reasoning
- Lightning fast
- Low cost

### `grok-4-1-fast-reasoning`

**Official Docs**: [grok-4-1-fast-reasoning](https://docs.x.ai/docs/models/grok-4-1-fast-reasoning)

- **Family**: Grok 4.1 Fast
- **Tier**: Frontier reasoning, fast variant
- **Context**: 2,000,000 tokens
- **Modalities**: Text input, image input → text output
- **Capabilities**: Function calling, structured outputs, reasoning
- **Rate Limits**: 4M tpm, 480 rpm
- **Pricing**: $0.20 input / $0.50 output (per 1M tokens)
- **Role**: High-end reasoning with fast, agentic tool calling for complex tasks and workflows
- **Research**: `core` (target for deep strengths/weaknesses mapping)

**Key traits for prompt design**:
- Optimized for [server-side tools](https://docs.x.ai/docs/guides/tools/overview) and agentic workflows
- Supports [function calling](https://docs.x.ai/docs/guides/function-calling) and [structured outputs](https://docs.x.ai/docs/guides/structured-outputs)
- Reasoning mode with extended thinking capability

### `grok-4-1-fast-non-reasoning`

**Official Docs**: [grok-4-1-fast-non-reasoning](https://docs.x.ai/docs/models/grok-4-1-fast-non-reasoning)

- **Family**: Grok 4.1 Fast
- **Tier**: Fast / cost-optimized, minimal reasoning tokens
- **Context**: 2,000,000 tokens
- **Modalities**: Text input, image input → text output
- **Capabilities**: Function calling, structured outputs (no extended reasoning)
- **Rate Limits**: 4M tpm, 480 rpm
- **Pricing**: $0.20 input / $0.50 output (per 1M tokens)
- **Role**: High-throughput drafting, simple Q&A, low-latency applications without heavy chain-of-thought
- **Research**: `secondary` (characterize mainly in contrast to reasoning variant)

**Key traits for prompt design**:
- Same capabilities as reasoning variant but skips extended thinking
- Faster response times for straightforward queries
- Cost-effective for high-volume, simple interactions

---

## Grok 4 Fast Family

**Official Page**: [Models and Pricing](https://docs.x.ai/docs/models#model-pricing)

These models balance speed with high reasoning performance for long-context workloads.

### `grok-4-fast-reasoning`

- **Family**: Grok 4 Fast
- **Tier**: Fast frontier reasoning / long-context
- **Context**: 2,000,000 tokens
- **Modalities**: Text input, image input → text output
- **Capabilities**: Function calling, structured outputs, reasoning
- **Rate Limits**: 4M tpm, 480 rpm
- **Pricing**: $0.20 input / $0.50 output (per 1M tokens)
- **Role**: Long-context workloads that need both speed and high reasoning performance (e.g., code bases, large documents)
- **Research**: `core` (compare against 4.1 Fast and legacy models)

### `grok-4-fast-non-reasoning`

- **Family**: Grok 4 Fast
- **Tier**: Fast / cost-optimized
- **Context**: 2,000,000 tokens
- **Modalities**: Text input, image input → text output
- **Capabilities**: Function calling, structured outputs (no extended reasoning)
- **Rate Limits**: 4M tpm, 480 rpm
- **Pricing**: $0.20 input / $0.50 output (per 1M tokens)
- **Role**: Fast long-context processing without reasoning overhead
- **Research**: `secondary`

---

## Grok 4 (Standard)

### `grok-4-0709`

**Official Docs**: [Models and Pricing](https://docs.x.ai/docs/models#model-pricing)

- **Family**: Grok 4
- **Tier**: Frontier reasoning (standard, non-fast)
- **Context**: 256,000 tokens
- **Modalities**: Text input, image input → text output
- **Capabilities**: Function calling, structured outputs, reasoning
- **Rate Limits**: 2M tpm, 480 rpm
- **Pricing**: $3.00 input / $15.00 output (per 1M tokens)
- **Role**: Flagship reasoning model for long-context tasks, analysis, and multimodal understanding
- **Research**: `core` (primary non-fast frontier target)

**Migration Notes**: Per [official migration guide](https://docs.x.ai/docs/models#additional-information-regarding-models), Grok 4 is a reasoning-only model with no non-reasoning mode. Parameters `presencePenalty`, `frequencyPenalty`, `stop`, and `reasoning_effort` are not supported.

---

## Grok 3 Family

**Official Page**: [Models and Pricing](https://docs.x.ai/docs/models#model-pricing)

Grok 3 models are previous-generation frontier models, now partly superseded by Grok 4.x.

### `grok-3`

- **Family**: Grok 3
- **Tier**: Frontier reasoning (previous generation)
- **Context**: 131,072 tokens
- **Modalities**: Text input, image input → text output
- **Capabilities**: Function calling, structured outputs, reasoning
- **Rate Limits**: 600 rpm
- **Pricing**: $3.00 input / $15.00 output (per 1M tokens)
- **Role**: High-end reasoning and long-context baseline for comparing Grok 4/4.1
- **Research**: `secondary` (mainly for historical and regression comparisons)

### `grok-3-mini`

- **Family**: Grok 3 Mini
- **Tier**: Small / cost-efficient reasoning
- **Context**: 131,072 tokens
- **Modalities**: Text input, image input → text output
- **Capabilities**: Function calling, structured outputs, reasoning
- **Rate Limits**: 480 rpm
- **Pricing**: $0.30 input / $0.50 output (per 1M tokens)
- **Role**: Lightweight general model for non-domain-heavy tasks with lower cost
- **Research**: `document-only` (useful as a point of reference, but not a core focus)

---

## Grok 2 and Legacy Models

**Official Page**: [Models and Pricing](https://docs.x.ai/docs/models#model-pricing)

Older Grok models maintained for compatibility. Generally not recommended for new work.

### `grok-2-vision-1212`

- **Family**: Grok 2 / legacy
- **Tier**: Legacy multimodal model
- **Context**: 32,768 tokens
- **Modalities**: Text input, image input → text output
- **Capabilities**: Function calling, structured outputs (legacy)
- **Rate Limits**: 600 rpm
- **Pricing**: $2.00 input / $10.00 output (per 1M tokens)
- **Role**: Historical / compatibility endpoint; useful mainly for regression and migration testing
- **Research**: `document-only`

---

## Code-Focused and Specialized Models

**Official Page**: [Models and Pricing](https://docs.x.ai/docs/models#model-pricing)

xAI provides code-optimized Grok variants for repository-level reasoning and tooling integrations.

### `grok-code-fast-1`

**Official Docs**: [Prompt Engineering for Grok Code](https://docs.x.ai/docs/guides/grok-code-prompt-engineering)

- **Family**: Grok Code Fast
- **Tier**: Fast code / reasoning hybrid
- **Context**: 256,000 tokens
- **Modalities**: Text input, image input → text output
- **Capabilities**: Function calling, structured outputs, reasoning
- **Rate Limits**: 2M tpm, 480 rpm
- **Pricing**: $0.20 input / $1.50 output (per 1M tokens)
- **Role**: Code completion, refactoring, repository-level reasoning, and agentic code tools
- **Research**: `core` (code-focused traits are highly relevant to prompt scaffolding)

**Key traits for prompt design**:
- Optimized for code understanding and generation
- Strong repository-level context handling
- See [official prompt engineering guide](https://docs.x.ai/docs/guides/grok-code-prompt-engineering) for code-specific best practices

---

## Image Generation Models

**Official Page**: [Models and Pricing](https://docs.x.ai/docs/models#model-pricing)

### `grok-2-image-1212`

**Official Docs**: [Image Generations Guide](https://docs.x.ai/docs/guides/image-generations)

- **Family**: Grok 2 / Image Generation
- **Tier**: Legacy image generation
- **Context**: N/A (image output model)
- **Modalities**: Text input → image output
- **Rate Limits**: 300 rpm
- **Pricing**: $0.07 per image
- **Role**: Text-to-image generation
- **Research**: `document-only`

---

## Additional Official Information

### Model Capabilities Reference

For detailed capability documentation, see:
- [Function Calling](https://docs.x.ai/docs/guides/function-calling)
- [Structured Outputs](https://docs.x.ai/docs/guides/structured-outputs)
- [Chat with Reasoning](https://docs.x.ai/docs/guides/reasoning)
- [Server-Side Tools](https://docs.x.ai/docs/guides/tools/overview)
- [Live Search](https://docs.x.ai/docs/guides/live-search)
- [Files and Document Search](https://docs.x.ai/docs/guides/files)

### Pricing and Consumption

- **Token Costs**: [Consumption and Rate Limits](https://docs.x.ai/docs/key-information/consumption-and-rate-limits)
- **Tool Invocation Costs**: [Tools Pricing](https://docs.x.ai/docs/models#tools-pricing)
- **Cached Prompt Tokens**: [Caching Details](https://docs.x.ai/docs/models#cached-prompt-tokens)

### Migration and Compatibility

- **Migrating to New Models**: [Migration Guide](https://docs.x.ai/docs/key-information/migrating-to-new-models)
- **Grok 4 for Grok 3 Users**: [Grok 4 Information](https://docs.x.ai/docs/models#additional-information-regarding-models)
- **Model Aliases**: [Alias Documentation](https://docs.x.ai/docs/models#model-aliases)

### Key Technical Details

- **Maximum image size**: 20 MiB
- **Supported image formats**: JPG/JPEG, PNG
- **No realtime data**: Models have no knowledge beyond training data unless [Live Search](https://docs.x.ai/docs/guides/live-search) is enabled
- **Chat role flexibility**: No role order limitation; can mix `system`, `user`, `assistant` in any sequence

---

## Notes

- **All data verified**: Every model, context window, pricing, and capability listed here is directly from [xAI's official documentation](https://docs.x.ai/docs/models) as of the last update to this file.
- **No third-party sources**: This inventory excludes models not officially documented by xAI.
- **Research priorities**: The "Research" field reflects this repository's focus on prompt engineering and technical characterization, not xAI's recommendations.
- **Check for updates**: Model availability and pricing may change. Always verify against the [official models page](https://docs.x.ai/docs/models) and your [xAI Console](https://console.x.ai/team/default/models).

---

**Last verified**: December 28, 2025  
**Official source**: https://docs.x.ai/docs/models
