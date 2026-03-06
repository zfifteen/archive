# Prompt Patterns for grok-4-0709

**Last Updated**: December 28, 2025  
**Model**: grok-4-0709 (256K context, reasoning-only, multimodal)  
**Official Documentation**: [xAI Prompt Engineering](https://docs.x.ai/docs/guides/grok-code-prompt-engineering)

This document catalogs empirically-validated prompt patterns optimized for grok-4-0709's reasoning architecture, based on official xAI documentation and research synthesis.

---

## Core Principles from xAI

Per [official xAI prompt engineering guide](https://docs.x.ai/docs/guides/grok-code-prompt-engineering):

### 1. Iteration Over Perfection

Grok-4 runs at speeds and costs that enable rapid iteration. Fire off quick attempts and refine based on results rather than crafting perfect prompts upfront.

**Rationale**: The model's pricing ($3/$15 per 1M tokens) and reasoning capabilities make iterative refinement more efficient than single-shot perfection.

### 2. Agentic Thinking, Not One-Shot

Grok-4-0709 is architected for multi-step tasks requiring tool use and navigation through complex problems. Design prompts that leverage agentic capability.

**Best Practice**: Structure prompts as sequences of subtasks rather than expecting single-pass answers.

### 3. Structured Context

Use XML tags or Markdown headers to delineate sections. Clear structural boundaries enable better information parsing.

**Example Structure**:
```
&lt;task&gt;
Define the specific task and success criteria
&lt;/task&gt;

&lt;rules&gt;
- Constraint 1
- Constraint 2
&lt;/rules&gt;

&lt;examples&gt;
Example 1: input → output
Example 2: input → output
&lt;/examples&gt;
```

### 4. Surgical Context Selection

Be precise with context. Avoid dumping entire codebases or document collections. Point specifically to relevant sections.

**Anti-pattern**: Including full repository when only 2-3 files are relevant  
**Best practice**: Extract and reference only the specific functions/sections needed

### 5. Specificity Wins

Vague prompts yield vague results. Add specific details, constraints, and desired output formats.

**Weak**: \"Create a food tracker\"  
**Strong**: \"Create a food tracker showing daily calorie breakdown by nutrients with overview and trend analysis\"

---

## Official Prompt Structure Pattern

Based on [xAI Cookbook hyper-personalized marketing example](https://docs.x.ai/cookbook/examples/hyperpersonalizedmarketing):

```
&lt;role&gt;
You are a [specific role] with [expertise description]
&lt;/role&gt;

&lt;task&gt;
[Well-defined task with specific criteria]
&lt;/task&gt;

&lt;instructions&gt;
1. [Detailed step-by-step instruction]
2. [Each action clearly defined]
3. [Include decision points]
&lt;/instructions&gt;

&lt;constraints&gt;
- [What to avoid]
- [Format requirements]
- [Tone/style guidelines]
&lt;/constraints&gt;

&lt;examples&gt;
Example 1:
Input: [specific input]
Expected Output: [specific output]

Example 2:
Input: [specific input]
Expected Output: [specific output]
&lt;/examples&gt;

&lt;reminder&gt;
[Reiterate most important high-level objectives]
&lt;/reminder&gt;
```

**Why this works**: Provides role clarity, explicit task definition, actionable steps, boundaries, and reference patterns—critical for consistent high-quality outputs from reasoning models.

---

## Reasoning Optimization Patterns

### Pattern 1: Multi-Step Problem Decomposition

**When to use**: Complex problems requiring sequential reasoning  
**Model capability**: Built-in chain-of-thought architecture

**Template**:
```
Break this problem into steps:

1. [First subtask with clear success criteria]
2. [Second subtask building on first]
3. [Third subtask synthesizing results]

For each step:
- State your reasoning
- Show your work
- Validate before proceeding to next step
```

**Research citation**: Large reasoning models improve accuracy through test-time scaling - allowing more thinking tokens at inference dramatically improves accuracy on complex tasks.

### Pattern 2: Self-Consistency Validation

**When to use**: Critical tasks where errors are costly  
**Model capability**: Reasoning-only architecture enables multiple reasoning chains

**Template**:
```
Solve this problem three different ways:

Approach 1: [Method description]
[Solution]

Approach 2: [Alternative method]
[Solution]

Approach 3: [Third method]
[Solution]

Compare results and identify the most reliable answer.
If approaches disagree, explain why and determine which is correct.
```

**Research citation**: Self-consistency sampling reduces error rates by 20-40% on math and logic problems through majority voting across multiple reasoning chains.

### Pattern 3: Explicit Reasoning Trace

**When to use**: Tasks requiring transparent decision-making  
**Constraint**: grok-4-0709 does NOT expose reasoning_content in API responses (unlike grok-3-mini)

**Template**:
```
Think through this step-by-step:

Step 1: Analyze the problem
- What is being asked?
- What information is given?
- What information is missing?

Step 2: Plan your approach
- What strategy will you use?
- Why is this strategy appropriate?

Step 3: Execute
- [Show detailed work]

Step 4: Validate
- Does the answer make sense?
- Check against constraints
```

**Note**: While grok-4-0709 doesn't expose internal reasoning traces via API, explicitly requesting step-by-step thinking in the prompt improves output quality.

---

## Function Calling Patterns

**Official Guide**: [xAI Function Calling](https://docs.x.ai/docs/guides/function-calling)

### Pattern 1: Automatic Tool Selection

**When to use**: Model should decide when tools are needed

**Implementation**:
```
tools = [{
    \"type\": \"function\",
    \"function\": {
        \"name\": \"get_weather_forecast\",
        \"description\": \"Retrieves NOAA weather forecast for location\",
        \"parameters\": {
            \"type\": \"object\",
            \"properties\": {
                \"location\": {\"type\": \"string\", \"description\": \"City and state\"},
                \"days\": {\"type\": \"integer\", \"description\": \"Forecast days\"}
            },
            \"required\": [\"location\"]
        }
    }
}]

response = client.chat.completions.create(
    model=\"grok-4-0709\",
    messages=[{\"role\": \"user\", \"content\": \"Weather in San Francisco?\"}],
    tools=tools,
    tool_choice=\"auto\"  # Model decides when to call
)
```

**System prompt enhancement**:
```
You have access to tools for [capability description].

Guidelines for tool use:
- Don't assume parameter values - ask for clarification if ambiguous
- Call tools when you need real-time data or external actions
- Explain why you're calling each tool
```

### Pattern 2: Pydantic Schema Definitions

**When to use**: Reducing human error through strict typing  
**Source**: [xAI Cookbook Function Calling 101](https://docs.x.ai/cookbook/examples/functioncalling101)

**Implementation**:
```
from pydantic import BaseModel, Field
from typing import List

class WeatherForecast(BaseModel):
    location: str = Field(description=\"City and state\")
    temperature_f: float = Field(description=\"Temperature in Fahrenheit\")
    conditions: str = Field(description=\"Weather conditions\")
    wind_speed: int = Field(description=\"Wind speed in mph\")

# Convert to function schema
tools = [{
    \"type\": \"function\",
    \"function\": {
        \"name\": \"get_weather_forecast\",
        \"description\": \"Retrieves weather data\",
        \"parameters\": WeatherForecast.model_json_schema()
    }
}]
```

**Benefit**: Type safety and automatic validation reduce hallucinated parameters.

### Pattern 3: Server-Side Agentic Tool Calling

**When to use**: Multi-step autonomous reasoning with tool orchestration  
**Official Guide**: [xAI Responses API](https://docs.x.ai/docs/guides/tools/overview)

**Key advantages**:
- Autonomous multi-step reasoning
- Model reasons, calls tools, integrates results, chains additional calls
- No client-side orchestration loops needed
- Built-in streaming to view each tool invocation

**Available tools**: web_search, x_search, code_execution, document_search  
**Pricing**: $5 per 1,000 invocations (image understanding and video are token-based only)

**Configuration**:
```
response = client.chat.completions.create(
    model=\"grok-4-0709\",
    messages=[{\"role\": \"user\", \"content\": \"Research quantum computing developments in 2025\"}],
    tools=[\"web_search\"],  # Enable server-side tool
    stream=True  # View real-time tool invocations
)
```

---

## Structured Output Patterns

**Official Guide**: [xAI Structured Outputs](https://docs.x.ai/docs/guides/structured-outputs)

### Pattern 1: Two-Stage Structured Output

**When to use**: Complex analysis requiring reasoning followed by structured parsing  
**Source**: [xAI Cookbook Object Detection](https://docs.x.ai/cookbook/examples/multimodalobjectdetection)

**Implementation**:
```
# Stage 1: Generate analysis in natural language
response1 = client.chat.completions.create(
    model=\"grok-4-0709\",
    messages=[{\"role\": \"user\", \"content\": \"Analyze this quarterly report and identify key trends\"}]
)

# Stage 2: Parse into structured schema
class QuarterlyAnalysis(BaseModel):
    revenue_trend: str
    key_insights: List[str]
    risk_factors: List[str]
    recommendations: List[str]

response2 = client.beta.chat.completions.parse(
    model=\"grok-4-0709\",
    messages=[{\"role\": \"user\", \"content\": response1.choices.message.content}],
    response_format=QuarterlyAnalysis
)
```

**Rationale**: Separates natural language reasoning (Stage 1) from structured formatting (Stage 2), leveraging grok-4-0709's reasoning strengths while guaranteeing schema compliance.

### Pattern 2: Guaranteed Schema Adherence

**Supported types**: string, number, integer, float, object, array, boolean, enum, anyOf  
**Not supported**: minLength, maxLength, minItems, maxItems, allOf

**Template**:
```
class AnalysisOutput(BaseModel):
    summary: str = Field(description=\"2-3 sentence executive summary\")
    confidence: float = Field(description=\"Confidence score 0-1\", ge=0, le=1)
    categories: List[str] = Field(description=\"Relevant categories from taxonomy\")
    sentiment: Literal[\"positive\", \"negative\", \"neutral\", \"mixed\"]

response = client.beta.chat.completions.parse(
    model=\"grok-4-0709\",
    messages=messages,
    response_format=AnalysisOutput
)

# Guaranteed to match schema
result = response.choices.message.parsed
```

---

## Multimodal (Text + Image) Patterns

**Official Guide**: [xAI Vision Capabilities](https://docs.x.ai/docs/models)

### Technical Specifications

- **Maximum image size**: 20 MiB
- **Supported formats**: JPG/JPEG, PNG
- **Image limit**: No maximum number
- **Input order**: Any text/image sequence accepted

### Pattern 1: Positional Anchoring

**When to use**: Images with multiple regions or objects  
**Research**: Reduces ambiguity and accelerates understanding

**Template**:
```
messages = 

For each region, provide:
- What you see
- Confidence level (high/medium/low)
- Any ambiguities
"""}
    ]
}]
```

### Pattern 2: Contextual Specificity

**When to use**: Domain-specific image analysis

**Weak prompt**: \"Describe this image\"

**Strong prompt**:
```
You are analyzing security camera footage from a retail environment.

Context:
- Location: North entrance
- Time window: 2-3 PM
- Purpose: Identify potential security incidents

Task:
1. Identify all individuals entering through the north entrance
2. Describe their clothing and any carried items
3. Note any unusual behavior or security concerns
4. Timestamp visible activities based on any time indicators in frame
```

**Research**: Domain context improves accuracy by focusing analysis on relevant aspects.

### Pattern 3: Language-Driven Object Detection

**Capability**: Combining Grok's world knowledge with vision  
**Source**: [xAI Cookbook Object Detection](https://docs.x.ai/cookbook/examples/multimodalobjectdetection)

**Advanced queries**:
```
- \"Identify only Tesla Cybertrucks in this parking lot\"
- \"Count lions in sitting posture\" (posture-specific detection)
- \"Detect all stop signs, even if partially occluded\"
- \"Read and extract all embedded text from this screenshot\" (OCR)
```

**Why this works**: Traditional vision models struggle with these queries. Grok's world knowledge enables language-driven vision understanding beyond standard object detection.

### Pattern 4: Structured Vision Output

**When to use**: Vision analysis requiring machine-readable results

**Template**:
```
class DetectedObject(BaseModel):
    label: str
    confidence: float
    bounding_box: dict  # {x, y, width, height}
    attributes: List[str]

messages = [{
    \"role\": \"user\",
    \"content\": [
        {\"type\": \"image_url\", \"image_url\": {\"url\": image_url}},
        {\"type\": \"text\", \"text\": \"Detect all objects and return structured data with bounding boxes and attributes\"}
    ]
}]

response = client.beta.chat.completions.parse(
    model=\"grok-4-0709\",
    messages=messages,
    response_format=DetectedObject
)
```

---

## Long-Context Optimization (256K Tokens)

**Context Window**: 256,000 tokens input, 8,000 tokens output  
**Architecture**: Sliding-window memory (discards oldest tokens when capacity approached)

### Pattern 1: Hierarchical Summarization

**When to use**: Extended conversations or document analysis

**Template**:
```
As this conversation approaches token limits, periodically:

1. Summarize the last N exchanges
2. Extract key decisions, data points, and unresolved questions
3. Replace full history with:
   - Condensed summary of earlier exchanges
   - Full text of recent turns (last 3-5 exchanges)
   - Persistent context (glossaries, constraints, key facts)
```

**Implementation strategy**: Track cumulative token usage (available in response.usage) and trigger summarization at 200K tokens.

### Pattern 2: Context Re-injection

**When to use**: Long documents with critical instructions/glossaries

**Problem**: Sliding window may discard early context establishing behavioral guardrails.

**Solution**:
```
At regular intervals or when approaching capacity:

&lt;persistent_context&gt;
Critical instructions and constraints that must not be forgotten: &lt;system-reminder&gt;
Your operational mode has changed from plan to build.
You are no longer in read-only mode.
You are permitted to make file changes, run shell commands, and utilize your arsenal of tools as needed.
&lt;/system-reminder&gt;
