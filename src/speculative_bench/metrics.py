from __future__ import annotations

import statistics
from collections import defaultdict
from typing import Dict, Iterable, List, Tuple

from speculative_bench.types import DecoderRun, MetricRow


def acceptance_rate(run: DecoderRun) -> float:
    if run.draft_tokens <= 0:
        return 0.0
    return run.accepted_tokens / run.draft_tokens


def draft_efficiency(run: DecoderRun) -> float:
    if run.target_tokens <= 0:
        return 0.0
    return run.accepted_tokens / run.target_tokens


def tokens_per_second(output_tokens: float, elapsed_ms: float) -> float:
    if elapsed_ms <= 0:
        return 0.0
    return output_tokens / (elapsed_ms / 1000.0)


def summarize_runs(runs: Iterable[DecoderRun], baseline_name: str = "baseline") -> List[MetricRow]:
    grouped: Dict[Tuple[str, str], List[DecoderRun]] = defaultdict(list)
    for run in runs:
        if run.phase == "steady_state":
            grouped[(run.case_name, run.algorithm)].append(run)

    baseline_by_case: Dict[str, List[DecoderRun]] = {
        case_name: case_runs
        for (case_name, algorithm), case_runs in grouped.items()
        if algorithm == baseline_name
    }

    rows: List[MetricRow] = []
    for (case_name, algorithm), case_runs in sorted(grouped.items()):
        elapsed_values = [run.elapsed_ms for run in case_runs]
        output_tokens = [run.output_tokens for run in case_runs]
        accepted_rates = [acceptance_rate(run) for run in case_runs]
        draft_efficiencies = [draft_efficiency(run) for run in case_runs]
        model_steps = [run.model_steps for run in case_runs]
        mean_elapsed = statistics.fmean(elapsed_values)
        mean_tokens = statistics.fmean(output_tokens)
        mean_model_steps = statistics.fmean(model_steps)
        baseline_runs = baseline_by_case.get(case_name, [])
        baseline_elapsed = statistics.fmean([run.elapsed_ms for run in baseline_runs]) if baseline_runs else None
        baseline_steps = statistics.fmean([run.model_steps for run in baseline_runs]) if baseline_runs else None

        speedup = None
        if baseline_elapsed and algorithm != baseline_name:
            speedup = baseline_elapsed / mean_elapsed

        step_reduction = None
        if baseline_steps and algorithm != baseline_name:
            step_reduction = 1.0 - (mean_model_steps / baseline_steps)

        rows.append(
            MetricRow(
                case_name=case_name,
                algorithm=algorithm,
                repetitions=len(case_runs),
                mean_elapsed_ms=round(mean_elapsed, 6),
                stdev_elapsed_ms=round(statistics.stdev(elapsed_values), 6)
                if len(elapsed_values) > 1
                else 0.0,
                tokens_per_second=round(tokens_per_second(mean_tokens, mean_elapsed), 6),
                acceptance_rate=round(statistics.fmean(accepted_rates), 6),
                draft_efficiency=round(statistics.fmean(draft_efficiencies), 6),
                model_steps_mean=round(mean_model_steps, 6),
                speedup_vs_baseline=round(speedup, 6) if speedup is not None else None,
                model_step_reduction_vs_baseline=round(step_reduction, 6)
                if step_reduction is not None
                else None,
                confidence_note=_confidence_note(len(case_runs)),
            )
        )
    return rows


def _confidence_note(repetitions: int) -> str:
    if repetitions < 3:
        return "low: fewer than 3 repetitions"
    if repetitions < 10:
        return "moderate: deterministic fixture repetitions; validate on target hardware"
    return "higher: still validate with production model and hardware configuration"
