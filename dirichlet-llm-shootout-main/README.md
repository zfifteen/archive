# dirichlet-llm-shootout

LLM shootout: Grok, Claude, and GPT turn a Dirichlet's theorem slide into a reproducible code-and-plots experiment.

## Idea

Given a single slide stating Dirichlet's theorem on primes in arithmetic progressions, each model must:
- Explain the theorem to a non-specialist technical audience.
- Design numerical experiments (primes in residue classes).
- Produce Python code and plots suitable for a GitHub Gist.

## Repo layout

- `meta/` – experiment design, task spec, and canonical prompts.
- `runs/` – raw outputs from each model (`grok/`, `claude/`, `gpt/`).
- `scripts/` – shared prime/plot utilities used in analysis.
- `analysis/` – evaluation rubric, scoring notebooks, comparison scripts.
- `results/` – final plots and summary tables.

## Getting started

1. Clone the repo and create a Python env.
2. Run `pip install -r requirements.txt` (to be added).
3. Use `scripts/primes_modN.py` to regenerate baseline experiments.
4. Drop each model's code into `runs/<model>/candidate-gist/` and execute.
5. Use evaluation scripts in `analysis/` to score and compare outputs.

## Source material

This experiment is inspired by 3Blue1Brown's video "Why do prime numbers make these spirals?" ([YouTube link](https://youtu.be/EK32jo7i5LQ?si=j6vIH12Enb2dPXtt), timestamp ~18:30-22:00), which presents Dirichlet's theorem in the context of prime spirals. This repo conducts an independent computational experiment to illustrate the theorem.

## License

MIT
