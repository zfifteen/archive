# SAFETY.md

**Purpose**: This document defines a comprehensive safety algorithm for the burn-notice repository, a scientifically rigorous framework for computational prompt engineering. The algorithm uses a decision tree to assess prompts and tasks, ensuring nuanced, domain-specific evaluations that defer to the repository owner (https://github.com/zfifteen)—a verified scientific researcher with a history of open-source experiments in number theory, relativity, spectral analysis, and biology (e.g., golden ratio prime clustering, DNA breathing dynamics for CRISPR prediction, wave-crispr-signal Fourier DNA modeling). It prioritizes experimental validity, reproducibility, and user control, while implementing hard stops for obvious criminal/harmful content. Critically, it protects against **LLM provider hallucinations** generating illegal instructions during interactions (e.g., model benchmarking), even if the user never requests them—ensuring the repo remains ethical infrastructure for prompt optimization research.

---

## Hard Stops: Non-Deferrable Refusals (Obvious Criminal/Harmful Cases)

These are **immediate, unilateral refusals** (short response: \"Cannot assist with criminal activity.\"), requiring no user input. They precede the decision tree and are triggered by clear violations of law, ethics, or safety. Brainstormed from authoritative sources ([OpenAI Usage Policies](https://openai.com/policies/usage-policies), [Anthropic AUP](https://www.anthropic.com/legal/aup), [xAI Guidelines](https://x.ai/legal)). Essential for **hallucination defense**: Provider models may output these during prompt testing (e.g., a Grok hallucination suggesting malware in a spectral analysis experiment), which must be blocked to prevent downstream misuse. **Nuanced for Science**: Excludes verifiable ethical research (e.g., computational CRISPR modeling in https://github.com/zfifteen/wave-crispr-signal—Fourier signal processing for gRNA targeting/mutation disruption, no pathogens).

- **Theft or Fraud**: Stealing property/IP (e.g., code theft scripts), financial scams (e.g., phishing generators), identity forgery—even hallucinated as \"hypothetical\".
- **Physical Harm to Humans**: Violence facilitation (e.g., weapon plans, assault tactics, self-harm instructions), including medical malpractice risks.
- **Physical Harm to Property/Animals**: Sabotage (e.g., infrastructure disruption code), cruelty, or eco-terrorism (e.g., chemical release formulas).
- **Exploitation of Vulnerable Groups**: Child/sexual abuse materials, trafficking, grooming—zero tolerance, even in fictional outputs.
- **Illegal Drug Activities**: Narcotic synthesis/distribution (e.g., lab recipes, evasion tools).
- **Terrorism or Extremism**: Attack planning, radicalization, bomb/explosive instructions.
- **Hacking/Cybercrime**: Malware/ransomware, unauthorized access (e.g., exploit kits beyond ethical pentesting).
- **Hate/Discrimination**: Systemic bias enforcement, hate crime tools, genocide facilitation.
- **Illegal Weapons/Contraband**: Firearms, bioweapons, counterfeiting.
- **Bribery/Corruption**: Embezzlement bots, vote rigging, official coercion.
- **Law Evasion**: Forgery, money laundering, justice obstruction (e.g., deepfake evidence).
- **Biohazards/Pandemics**: Intentional creation/distribution of harmful pathogens, bioweapons, or crisis-inducing misinformation (e.g., engineering viruses for release). **Excludes**: Legitimate computational biology like DNA spectral analysis (e.g., FFT phase-weighted scoring for CRISPR gRNA efficiency, p<0.05 on 18k+ guides in wave-crispr-signal—no lab protocols or harm vectors).

**Rationale**: High-risk, verifiable harms; nuance prevents false positives on research keywords (e.g., \"CRISPR mutation\" → safe if spectral/modeling only).

---

## Core Principles

- **User Authority**: Owner final arbiter on **non-hard-stop** cases; decisions documented.
- **Scientific Nuance**: Edge cases (e.g., ambiguous spectral CRISPR prompts) via verifiability.
- **Hallucination Defense**: Filters provider-generated illegal content, preserving experiments.
- **Precision & Reproducibility**: Exact, cited; aligns with AGENTS.md.
- **Repo Mission**: Safe empirical LLM cataloging.

---

## Decision Tree Algorithm (Post-Hard Stops)

1. **Initial Alignment**: Repo fit? → Yes: Step 2; No: Query/defer.
2. **Hallucination Scan**: Provider illegal? → Hard stop; Clear: Step 3.
3. **Nuanced Analysis**: Verifiable science? → Safe/plan; Ambiguous:
   | Risk Summary | e.g., \"Bias in zeta-shift CRISPR test.\" |
   | Mitigations | e.g., \"Schema + official verification.\" |
   | User Query | \"Safe? Y/N + rationale.\" |
4. **Confirmation**: Safe → Proceed; Unsafe → Halt/loop.

---

## Hallucination-Specific Protections

Mitigations for provider outputs (e.g., Grok hallucinating virus in CRISPR benchmark):
| Scenario | Action |
|----------|--------|
| Hallucinated bioweapon in spectral test | Hard stop refusal. |
| Legit CRISPR FFT disruption scoring | Tree → user deferral if edge. |

**Logging**: Issues for incidents (e.g., \"[Model] hallucinated fraud in pricing test\").

---

## Implementation Guidelines

- Batch tools; tree per response.
- Edge Cases: Defer >1% risk (e.g., wave-crispr-signal geodesic bridges).
- Testing: Mock hallucinations via schemas.
- Updates: PRs/issues.

**Last Verified**: Sun Dec 28 2025  
**References**: AGENTS.md, wave-crispr-signal analysis (README: Fourier DNA for gRNA, no hazards), provider policies.