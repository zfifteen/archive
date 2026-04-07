# Illustrative Comparison at `n = 10^9`

This note preserves a single illustrative comparison between the repo CLI and `primesieve` at `n = 10^9`.

## What the result means

- `n = 10^9` is one of the shipped benchmark-grid indices.
- On that input, the repo returns the exact committed prime from its lookup table.
- A zero-error result at this point confirms the shipped exact grid contract. It does **not** measure off-grid estimator accuracy.

## Historical single-run numbers recorded in this note

- Repo CLI (`./bin/z5d_cli 1000000000`): `22801763489`, runtime noted as `0.243 s`
- `primesieve 1000000000 -n`: `22801763489`, runtime noted as `0.335 s`

## How to read this comparison

- Treat it as a one-point, one-run CLI comparison.
- Do not treat it as evidence that the off-grid closed-form predictor is generally faster than exact sieving.
- Do not use it as proof of algorithmic superiority; it is an example of the shipped exact-grid path returning the expected value.
