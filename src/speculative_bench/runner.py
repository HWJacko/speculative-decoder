from __future__ import annotations

from typing import Iterable, List

from speculative_bench.config import BenchmarkConfig
from speculative_bench.environment import collect_environment, utc_now_iso
from speculative_bench.integrations import DecoderAdapter
from speculative_bench.metrics import summarize_runs
from speculative_bench.types import BenchmarkCase, BenchmarkResult, DecoderRun


class BenchmarkRunner:
    def __init__(
        self,
        cases: Iterable[BenchmarkCase],
        adapters: Iterable[DecoderAdapter],
        config: BenchmarkConfig,
    ) -> None:
        self.cases = list(cases)
        self.adapters = list(adapters)
        self.config = config
        if not self.cases:
            raise ValueError("at least one benchmark case is required")
        if not self.adapters:
            raise ValueError("at least one decoder adapter is required")

    def run(self) -> BenchmarkResult:
        cold_start_ms = {adapter.name: adapter.cold_start() for adapter in self.adapters}
        runs: List[DecoderRun] = []

        for adapter in self.adapters:
            for case in self.cases:
                for warmup in range(self.config.warmups):
                    adapter.decode(case=case, repetition=-(warmup + 1), seed=self.config.seed)
                for repetition in range(self.config.repeats):
                    runs.append(adapter.decode(case=case, repetition=repetition, seed=self.config.seed))

        return BenchmarkResult(
            generated_at=utc_now_iso(),
            environment=collect_environment(),
            config=self.config.to_dict(),
            cases=[case.to_dict() for case in self.cases],
            cold_start_ms=cold_start_ms,
            rows=summarize_runs(runs),
            runs=runs,
        )
