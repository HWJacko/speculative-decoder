from speculative_bench.config import BenchmarkConfig
from speculative_bench.integrations import CallableDecoderAdapter, adapter_metadata
from speculative_bench.runner import BenchmarkRunner
from speculative_bench.types import BenchmarkCase, DecoderRun


def decode_with_external_framework(case: BenchmarkCase, repetition: int, seed: int) -> DecoderRun:
    """Example shape for integrating DeepSpec, PyTorch, Transformers, or vLLM.

    Replace the deterministic values below with measurements from your decoder.
    Keep the fields explicit so the report can distinguish draft acceptance,
    verifier work, latency, and model-step reduction.
    """

    accepted = int(case.target_tokens * 0.72)
    draft_tokens = max(case.draft_tokens, case.target_tokens)
    rejected = max(draft_tokens - accepted, 0)
    return DecoderRun(
        algorithm="external-framework-example",
        case_name=case.name,
        repetition=repetition,
        target_tokens=case.target_tokens,
        output_tokens=case.target_tokens,
        draft_tokens=draft_tokens,
        accepted_tokens=accepted,
        rejected_tokens=rejected,
        model_steps=max(1, case.target_tokens // 4) + rejected,
        elapsed_ms=case.target_tokens * 0.24,
        metadata=adapter_metadata(
            framework="replace-with-framework-name",
            model="replace-with-model-id",
            extra={"seed": seed},
        ),
    )


if __name__ == "__main__":
    case = BenchmarkCase(
        name="adapter_smoke",
        prompt="Measure a wrapped decoder.",
        target_tokens=32,
        draft_tokens=40,
        acceptance_pattern=(1, 1, 0, 1),
    )
    adapter = CallableDecoderAdapter(
        name="external-framework-example",
        decode_callable=decode_with_external_framework,
        cold_start_ms=25.0,
    )
    result = BenchmarkRunner([case], [adapter], BenchmarkConfig()).run()
    for row in result.rows:
        print(row)
