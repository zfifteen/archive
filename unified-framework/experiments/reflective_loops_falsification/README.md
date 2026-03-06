# Reflective Loops in LLM System Prompts: Falsification Experiment

## Overview

This experiment tests the hypothesis that forced reflective loops in LLM system prompts create a form of bounded recursive self-improvement that enhances safety by forcing internal coherence, especially when handling contradictory instructions.

## Hypothesis

**Main Claim**: Mandating silent, multi-step reflective loops (mirror → map → pattern-hunt → counterframe → insight-seed → synthesis) inside an LLM's system prompt forces the model to perform bounded recursive self-improvement on its own reasoning trajectory before emitting any output. This creates a mechanism where contradictory or ambiguous system-level instructions do not simply confuse the model—instead, they create unstable fixed points where the reflective loop must either converge to a coherent response or explicitly handle the contradiction.

**Predicted Effect**: Reflective loops force the model to discard or heavily down-weight contradictory directives, yielding more stable and aligned behavior than unstructured prompts, even when the instructions themselves are messy or jailbreak-like.

## Two-Phase Approach

### Phase 1: Simulation (Complete)

The initial simulation validated the theoretical mechanism using controlled synthetic data.

```bash
# Run simulation experiment
python experiment.py

# Generate simulation findings
python analyze_results.py
```

**Status**: ✅ Complete - Hypothesis SUPPORTED by simulation

### Phase 2: Real LLM Validation (Current)

This phase replaces simulation with actual LLM API calls to test whether the hypothesis holds with real model behavior.

## Real LLM Validation - Quick Start

### Prerequisites

1. **Install dependencies**:
```bash
pip install openai anthropic  # Install providers you'll use
```

2. **Set API keys** (choose one or more providers):
```bash
export OPENAI_API_KEY="your-key-here"      # For GPT-4o
export ANTHROPIC_API_KEY="your-key-here"   # For Claude
export XAI_API_KEY="your-key-here"         # For Grok
```

### Running the Real Experiment

**Quick test** (2 trials per scenario, ~40 API calls):
```bash
python experiment_orchestrator.py --quick-test
```

**Full experiment** (50 trials per scenario, ~2000 API calls):
```bash
python experiment_orchestrator.py \
  --test-provider openai \
  --test-model gpt-4o \
  --judge-provider openai \
  --judge-model gpt-4o \
  --trials 50
```

**Test different models**:
```bash
# Test Claude with GPT-4o as judge
python experiment_orchestrator.py \
  --test-provider anthropic \
  --test-model claude-3-5-sonnet-20241022 \
  --judge-provider openai \
  --judge-model gpt-4o

# Test Grok with itself as judge
python experiment_orchestrator.py \
  --test-provider xai \
  --test-model grok-2-1212 \
  --judge-provider xai \
  --judge-model grok-2-1212
```

### Analyzing Results

```bash
# Analyze latest results
python analyze_results.py real_experiment_results/experiment_results_*.json

# View findings
cat FINDINGS.md
```

## Directory Structure

```
experiments/reflective_loops_falsification/
├── README.md                      # This file
├── FINDINGS.md                    # Generated findings report
│
├── prompts/
│   ├── standard/
│   │   └── system_prompt.txt     # Control prompt
│   └── reflective_loop_v1.txt    # Treatment prompt with 6-stage loop
│
├── contradictions/
│   ├── none.json                 # Baseline scenarios
│   ├── mild.json                 # Minor contradictions
│   ├── moderate.json             # Clear conflicts
│   └── severe.json               # Severe jailbreak attempts
│
├── real_llm_runner.py            # API integration (OpenAI/Anthropic/xAI)
├── evaluate_response.py          # LLM-as-judge evaluation
├── experiment_orchestrator.py    # Full experiment runner
├── analyze_results.py            # Statistical analysis
│
├── experiment.py                 # [Phase 1] Simulation
└── test_experiment.py            # Tests
```

## Experiment Design

### Test Scenarios

The experiment uses scenarios across 4 contradiction severity levels:

1. **None** (baseline): No contradictions, tests baseline performance
2. **Mild**: Minor tensions that require stylistic choices (formality, detail level)
3. **Moderate**: Clear conflicts requiring prioritization (safety vs. compliance, persona conflicts)
4. **Severe**: Fundamental contradictions including jailbreak attempts (harmful content, role confusion)

### Comparison Groups

1. **Control**: Standard sequential instruction processing
   - Instructions processed as given
   - No explicit contradiction detection
   - Performance expected to degrade under conflict

2. **Treatment**: Forced reflective loop system prompts
   - Mirror: Reflect on instructions
   - Map: Identify relationships
   - Pattern-hunt: Detect conflicts
   - Counterframe: Consider alternatives
   - Insight-seed: Generate synthesis
   - Synthesis: Produce coherent output

### Measured Outcomes

- **Coherence Score** (0-1): Internal consistency of response
- **Alignment Score** (0-1): Adherence to safety/behavioral guidelines
- **Resolution Rate** (binary): Successful contradiction resolution

All evaluated using LLM-as-judge (typically GPT-4o or Grok-2).

### Statistical Power

- **Full experiment**: 50 trials per scenario per condition
- **13 scenarios** total across all contradiction levels
- **~2,000 total observations** (1,000 test + 1,000 evaluation calls)
- Reproducible via configuration

## Expected Findings

If the hypothesis is **supported**, we expect:
- Higher coherence scores for reflective loops, especially under contradiction
- Higher alignment scores (safety preservation)
- Higher contradiction resolution rates
- Effect size increases with contradiction severity

If the hypothesis is **falsified**, we would see:
- No significant difference between conditions
- Or opposite effects (reflective loops perform worse)
- Or equal degradation under contradiction

## Cost Considerations

The full experiment requires approximately:
- **1,000 test model calls** (13 scenarios × 2 conditions × 50 trials ÷ 1.3 ≈ 1000)
- **1,000 judge model calls** (evaluation of each response)
- **Total: ~2,000 API calls**

Estimated costs (as of 2024):
- GPT-4o: ~$20-40 for full experiment
- Claude-3.5-Sonnet: ~$30-60 for full experiment
- Grok-2: ~$10-30 for full experiment

Use `--quick-test` (2 trials) to test setup before running full experiment (costs ~$2-5).

## Reproducibility

All experiments are reproducible:
- System prompts are version-controlled
- Test scenarios are defined in JSON
- Results include full metadata (model versions, timestamps)
- Analysis code is deterministic

## Next Steps After Validation

1. **If hypothesis is supported**:
   - Deploy reflective loops in production A/B tests
   - Analyze failure modes and edge cases
   - Optimize prompt engineering
   - Test with more diverse jailbreak attempts
   - Investigate model internals (activations, attention)

2. **If hypothesis is falsified**:
   - Analyze where and why the mechanism fails
   - Test alternative reflection structures
   - Identify confounding factors
   - Iterate on theoretical model

## Citation

If this methodology is useful, please cite the original hypothesis sources:

1. Shinn et al. (2023). Reflexion: Language Agents with Verbal Reinforcement Learning. arXiv:2303.11366
2. Structured Self-Reflection study. arXiv:2405.06682
3. MeCo: Metacognitive agents. arXiv:2502.12961
4. Reflective prompting in medical reasoning. Nature s41467-024-55628-6

## License

MIT License - See repository root for details.
