# grok-4-0709

**Official Documentation**: [Models and Pricing](https://docs.x.ai/docs/models#model-pricing)

## Quick Reference

- **Model ID**: `grok-4-0709`
- **Family**: Grok 4
- **Tier**: Frontier reasoning (standard, non-fast)
- **Context Window**: 256,000 tokens
- **Modalities**: Text input, image input → text output
- **Capabilities**: Function calling, structured outputs, reasoning
- **Rate Limits**: 2M tpm, 480 rpm
- **Pricing**: $3.00 input / $15.00 output (per 1M tokens)
- **Research Priority**: `core` (primary non-fast frontier target)

## Official Description

Per [xAI documentation](https://docs.x.ai/docs/models#grok-4-standard):

> Flagship reasoning model for long-context tasks, analysis, and multimodal understanding

## Key Characteristics

- **Reasoning-only**: No non-reasoning mode available (unlike 4.1 Fast variants)
- **Multimodal**: Processes both text and images
- **Long-context**: 256K token window for complex analysis
- **Premium tier**: 15x more expensive than fast variants ($3/$15 vs $0.20/$0.50)

## Migration Notes

Per [official migration guide](https://docs.x.ai/docs/models#additional-information-regarding-models):

- Grok 4 is a reasoning-only model with no non-reasoning mode
- Parameters `presencePenalty`, `frequencyPenalty`, `stop`, and `reasoning_effort` are not supported
- These parameters will cause errors if included in requests

## Documentation Structure

This directory contains:

- **capabilities.md**: Detailed capability analysis with official citations
- **strengths.md**: Documented strengths and optimal use cases
- **weaknesses.md**: Known limitations and constraints
- **prompt-patterns.md**: Effective prompt patterns for this model
- **experiments/**: Directory for empirical test logs
- **examples/**: Real-world prompt/response pairs

## When to Use grok-4-0709

Choose this model for:
- Complex reasoning tasks requiring extended thinking
- Long-context analysis (up to 256K tokens)
- Multimodal understanding (text + images)
- Structured output generation with function calling
- Tasks where quality justifies premium pricing

Choose fast variants instead for:
- High-throughput workloads
- Cost-sensitive applications
- Very long contexts (>256K tokens, use 4.1 Fast with 2M)
- Simple queries not requiring deep reasoning

## Last Updated

December 28, 2025

## Source

All specifications verified against: https://docs.x.ai/docs/models