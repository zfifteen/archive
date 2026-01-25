# Experiment specification

- **Theorem**: Dirichlet's theorem on primes in arithmetic progressions.
- **Input artifact**: Screenshot / transcription of slide stating the limit formula for primes in residue classes, from 3Blue1Brown video: https://youtu.be/EK32jo7i5LQ?si=j6vIH12Enb2dPXtt (timestamp ~18:30-22:00)
- **Task**: Turn this into a mini-project (Gist-style) with:
  - `README.md` explaining the theorem and experiments.
  - Python code to sample primes, partition by residue class, and estimate densities.
  - Plot code generating multiple figures for different moduli.

- **Models under test**: Grok (xAI), Claude (Anthropic), GPT-4-class (OpenAI).
- **Controls**:
  - Same prompt text.
  - Same slide description.
  - Fixed temperature and max tokens per run.
  - No manual edits in `runs/*/raw/`.

- **Evaluation dimensions**:
  - Mathematical correctness.
  - Experimental design and code quality.
  - Plot quality and interpretability.
  - Pedagogical clarity.

## Source material

The experiment is inspired by 3Blue1Brown's video "Why do prime numbers make these spirals?" which presents Dirichlet's theorem in the context of prime spirals and Ulam's spiral. The video provides an intuitive visual explanation of how primes distribute themselves into residue classes modulo N, with the proportion approaching 1/φ(N) as described by Dirichlet's theorem.

This repo conducts an independent computational experiment to illustrate the theorem, without reproducing the video content.
