from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Dict, Iterable, List

from speculative_bench.integrations import DecoderAdapter
from speculative_bench.types import BenchmarkCase, DecoderRun


@dataclass(frozen=True)
class AlgorithmProfile:
    name: str
    draft_multiplier: float
    verifier_cost_ms: float
    draft_cost_ms: float
    base_decode_cost_ms: float
    cold_start_ms: float
    max_window: int
    acceptance_bias: int = 0


BUILTIN_PROFILES: Dict[str, AlgorithmProfile] = {
    "baseline": AlgorithmProfile(
        name="baseline",
        draft_multiplier=0.0,
        verifier_cost_ms=0.0,
        draft_cost_ms=0.0,
        base_decode_cost_ms=0.46,
        cold_start_ms=6.0,
        max_window=1,
    ),
    "speculative-balanced": AlgorithmProfile(
        name="speculative-balanced",
        draft_multiplier=1.0,
        verifier_cost_ms=0.17,
        draft_cost_ms=0.045,
        base_decode_cost_ms=0.22,
        cold_start_ms=9.5,
        max_window=4,
    ),
    "speculative-aggressive": AlgorithmProfile(
        name="speculative-aggressive",
        draft_multiplier=1.35,
        verifier_cost_ms=0.14,
        draft_cost_ms=0.052,
        base_decode_cost_ms=0.18,
        cold_start_ms=11.0,
        max_window=8,
        acceptance_bias=-1,
    ),
}


class SimulatedDecoderAdapter:
    """Deterministic decoder simulator used for fixtures and CI.

    These profiles do not claim real model performance. They provide a stable
    contract for metrics, reporting, and adapter integration tests.
    """

    def __init__(self, profile: AlgorithmProfile) -> None:
        self.profile = profile
        self.name = profile.name

    def cold_start(self) -> float:
        return self.profile.cold_start_ms

    def decode(self, case: BenchmarkCase, repetition: int, seed: int) -> DecoderRun:
        if self.name == "baseline":
            elapsed_ms = self._jitter(
                base=1.25 + case.target_tokens * self.profile.base_decode_cost_ms,
                case=case,
                repetition=repetition,
                seed=seed,
            )
            return DecoderRun(
                algorithm=self.name,
                case_name=case.name,
                repetition=repetition,
                target_tokens=case.target_tokens,
                output_tokens=case.target_tokens,
                draft_tokens=0,
                accepted_tokens=0,
                rejected_tokens=0,
                model_steps=case.target_tokens,
                elapsed_ms=elapsed_ms,
                metadata={"profile": "deterministic-simulator"},
            )

        draft_tokens = max(case.target_tokens, math.ceil(case.draft_tokens * self.profile.draft_multiplier))
        accepted_tokens = self._accepted_tokens(case, draft_tokens)
        rejected_tokens = max(draft_tokens - accepted_tokens, 0)
        verification_rounds = max(1, math.ceil(case.target_tokens / self.profile.max_window))
        model_steps = verification_rounds + rejected_tokens
        elapsed_ms = (
            1.7
            + case.target_tokens * self.profile.base_decode_cost_ms
            + draft_tokens * self.profile.draft_cost_ms
            + verification_rounds * self.profile.verifier_cost_ms
            + rejected_tokens * 0.035
        )
        elapsed_ms = self._jitter(base=elapsed_ms, case=case, repetition=repetition, seed=seed)
        return DecoderRun(
            algorithm=self.name,
            case_name=case.name,
            repetition=repetition,
            target_tokens=case.target_tokens,
            output_tokens=case.target_tokens,
            draft_tokens=draft_tokens,
            accepted_tokens=min(accepted_tokens, case.target_tokens),
            rejected_tokens=rejected_tokens,
            model_steps=model_steps,
            elapsed_ms=elapsed_ms,
            metadata={
                "profile": "deterministic-simulator",
                "max_window": self.profile.max_window,
                "acceptance_bias": self.profile.acceptance_bias,
            },
        )

    def _accepted_tokens(self, case: BenchmarkCase, draft_tokens: int) -> int:
        accepted = 0
        pattern = list(case.acceptance_pattern)
        for index in range(draft_tokens):
            shifted_index = max(index + self.profile.acceptance_bias, 0)
            accepted += pattern[shifted_index % len(pattern)]
        return accepted

    def _jitter(self, base: float, case: BenchmarkCase, repetition: int, seed: int) -> float:
        case_factor = sum(ord(char) for char in case.name) % 17
        deterministic_offset = ((case_factor + repetition + seed) % 11) * 0.013
        return round(base + deterministic_offset, 6)


def builtin_algorithm_names() -> List[str]:
    return list(BUILTIN_PROFILES)


def get_builtin_adapters(names: Iterable[str] | None = None) -> List[DecoderAdapter]:
    selected = list(names) if names else builtin_algorithm_names()
    unknown = sorted(set(selected).difference(BUILTIN_PROFILES))
    if unknown:
        raise ValueError(f"unknown algorithm(s): {', '.join(unknown)}")
    return [SimulatedDecoderAdapter(BUILTIN_PROFILES[name]) for name in selected]
