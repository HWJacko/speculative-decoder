from __future__ import annotations

from typing import Mapping, Protocol

from speculative_bench.types import BenchmarkCase, DecoderRun


class DecoderAdapter(Protocol):
    """Adapter contract for built-in simulators or external model frameworks."""

    name: str

    def cold_start(self) -> float:
        """Prepare the decoder and return cold-start overhead in milliseconds."""

    def decode(self, case: BenchmarkCase, repetition: int, seed: int) -> DecoderRun:
        """Run one benchmark repetition for a case."""


class CallableDecoderAdapter:
    """Wrap a user function in the benchmark adapter protocol.

    The callable receives ``case``, ``repetition`` and ``seed`` keyword arguments.
    It must return a ``DecoderRun`` so framework-specific metrics stay explicit.
    """

    def __init__(self, name: str, decode_callable, cold_start_ms: float = 0.0) -> None:
        self.name = name
        self._decode_callable = decode_callable
        self._cold_start_ms = float(cold_start_ms)

    def cold_start(self) -> float:
        return self._cold_start_ms

    def decode(self, case: BenchmarkCase, repetition: int, seed: int) -> DecoderRun:
        run = self._decode_callable(case=case, repetition=repetition, seed=seed)
        if not isinstance(run, DecoderRun):
            raise TypeError("decode callable must return speculative_bench.types.DecoderRun")
        if run.algorithm != self.name:
            return DecoderRun(
                algorithm=self.name,
                case_name=run.case_name,
                repetition=run.repetition,
                target_tokens=run.target_tokens,
                output_tokens=run.output_tokens,
                draft_tokens=run.draft_tokens,
                accepted_tokens=run.accepted_tokens,
                rejected_tokens=run.rejected_tokens,
                model_steps=run.model_steps,
                elapsed_ms=run.elapsed_ms,
                phase=run.phase,
                metadata=dict(run.metadata),
            )
        return run


def adapter_metadata(framework: str, model: str, extra: Mapping[str, object] | None = None) -> dict[str, object]:
    metadata = {"framework": framework, "model": model}
    if extra:
        metadata.update(extra)
    return metadata
