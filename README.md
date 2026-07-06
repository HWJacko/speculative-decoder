# Speculative Decoding Benchmark Suite

A standalone benchmark suite for evaluating speculative decoding algorithms with deterministic fixtures, adapter-friendly integration points, and JSON/CSV/Markdown reports suitable for CI artifacts.

This project is a companion tool for teams exploring ideas similar to [deepseek-ai/DeepSpec](https://github.com/deepseek-ai/DeepSpec). It is not a clone, fork, or training stack. Its boundary is deliberately narrower: repeatable automated benchmarking for decoding strategies, with clear separation between cold-start overhead, steady-state throughput, and runtime configuration.

## Why this exists

Speculative decoding projects create a measurement problem as soon as they become practical. A training and evaluation codebase such as DeepSpec can advance draft-model and verifier techniques, but developers still need a small, reproducible harness that answers operational questions: how much startup overhead does an algorithm introduce, how much verifier work is saved, what acceptance rate is observed on representative prompts, and whether throughput changes survive repeated runs on the same hardware.

This companion project was synthesized from trend-discovery and duplicate-gating signals in the autonomous pipeline behind [Infrasieve](https://infrasieve.dev). The upstream signal was that speculative decoding was moving from paper-level technique into implementation-level infrastructure, while duplicate checks did not show a focused repository dedicated to standardized, machine-readable benchmark comparison for these algorithms. That combination creates demand for a standalone tool that can sit beside DeepSpec or any other model framework without inheriting its training pipeline, dependency graph, or release cadence.

Architecturally, the suite keeps the measurement contract independent from the model implementation. Built-in simulator adapters provide deterministic fixtures for validating the benchmark machinery, and external adapters can wrap DeepSpec, PyTorch, Transformers, vLLM, or custom serving code when developers are ready to make hardware-specific claims.

## Features

- Deterministic default benchmark cases for short, medium, and long generation tasks.
- Built-in baseline and speculative decoding simulator adapters.
- Metrics for acceptance rate, draft efficiency, model-step reduction, tokens/sec, cold-start overhead, and speedup versus baseline.
- JSON, CSV, and Markdown reports for automated processing and README/CI inclusion.
- Adapter protocol for real model frameworks without adding framework dependencies to this package.
- Docker and GitHub Actions examples for reproducible execution.

## Install

```sh
python -m pip install .
```

For local development:

```sh
python -m pip install ".[dev]"
pytest
```

You can also use the setup script:

```sh
sh scripts/bootstrap.sh
```

## Run

```sh
speculative-bench run --out reports
```

The command writes:

- `reports/benchmark-results.json`
- `reports/benchmark-results.csv`
- `reports/benchmark-summary.md`

List built-in algorithms:

```sh
speculative-bench list-algorithms
```

Run a subset:

```sh
speculative-bench run \
  --algorithm baseline \
  --algorithm speculative-balanced \
  --tag medium \
  --repeats 5 \
  --out reports
```

## Add Benchmark Cases

Create a JSON file with a `cases` array:

```json
{
  "cases": [
    {
      "name": "domain_specific_prompt",
      "prompt": "Draft a latency analysis for a production speculative decoding service.",
      "target_tokens": 96,
      "draft_tokens": 120,
      "acceptance_pattern": [1, 1, 0, 1, 0, 1, 1, 1],
      "tags": ["custom", "latency"]
    }
  ]
}
```

Then run:

```sh
speculative-bench run --cases examples/custom_cases.json --out reports
```

`acceptance_pattern` is a deterministic fixture used by simulator adapters. Real framework adapters should report observed acceptance counts from the actual decoder.

## Integrate A Real Decoder

Use `speculative_bench.integrations.CallableDecoderAdapter` or implement the `DecoderAdapter` protocol directly. Your adapter returns a `DecoderRun` for each case and repetition, making draft tokens, accepted tokens, rejected tokens, model steps, and elapsed time explicit.

See `examples/framework_adapter.py` for the expected shape.

The package intentionally does not depend on DeepSpec, PyTorch, Transformers, vLLM, CUDA libraries, or model weights. That isolation keeps the benchmark runner installable in CI and lets teams bind it to their own framework versions.

## Metrics

Cold-start and steady-state numbers are reported separately.

- `cold_start_ms`: one-time adapter setup overhead.
- `mean_elapsed_ms`: mean steady-state decode time across repetitions.
- `tokens_per_second`: output tokens divided by steady-state elapsed time.
- `acceptance_rate`: accepted draft tokens divided by total draft tokens.
- `draft_efficiency`: accepted draft tokens divided by target output tokens.
- `speedup_vs_baseline`: baseline elapsed time divided by algorithm elapsed time for the same case.
- `model_step_reduction_vs_baseline`: relative reduction in model steps versus baseline.

Confidence notes are conservative by design. Built-in algorithms are deterministic fixtures for validating the benchmark suite. Do not use them to claim model or algorithm superiority.

## CI And Artifacts

The included GitHub Actions workflow installs the package, runs tests, executes the deterministic benchmark, and uploads the report directory as an artifact.

For Docker:

```sh
docker build -t speculative-decoding-bench .
docker run --rm -v "$PWD/reports:/app/reports" speculative-decoding-bench
```

## Nearby Alternatives To Review Before Release

The original project gate accepted this concept with duplication score `0`, but release review should still check adjacent tools:

- General LLM benchmark harnesses that may add speculative decoding plugins.
- Framework-specific evaluation scripts inside DeepSpec-style repositories.
- Serving-system benchmarks that measure throughput but do not expose draft acceptance or verifier work.
- Paper reproduction repositories that benchmark one algorithm without a reusable adapter contract.

This suite should remain focused on automated, reproducible comparison rather than becoming a training framework, serving engine, or model zoo.
