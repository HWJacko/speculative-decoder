from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Dict, Iterable

from speculative_bench.types import BenchmarkResult, MetricRow


def write_reports(result: BenchmarkResult, output_dir: str | Path, formats: Iterable[str]) -> Dict[str, Path]:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    written: Dict[str, Path] = {}
    selected = set(formats)

    if "json" in selected:
        path = out / "benchmark-results.json"
        path.write_text(json.dumps(result.to_dict(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
        written["json"] = path

    if "csv" in selected:
        path = out / "benchmark-results.csv"
        _write_csv(path, result.rows)
        written["csv"] = path

    if "md" in selected:
        path = out / "benchmark-summary.md"
        path.write_text(markdown_summary(result), encoding="utf-8")
        written["md"] = path

    return written


def _write_csv(path: Path, rows: Iterable[MetricRow]) -> None:
    fieldnames = [
        "case_name",
        "algorithm",
        "repetitions",
        "mean_elapsed_ms",
        "stdev_elapsed_ms",
        "tokens_per_second",
        "acceptance_rate",
        "draft_efficiency",
        "model_steps_mean",
        "speedup_vs_baseline",
        "model_step_reduction_vs_baseline",
        "confidence_note",
    ]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row.to_dict())


def markdown_summary(result: BenchmarkResult) -> str:
    lines = [
        "# Speculative Decoding Benchmark Summary",
        "",
        f"Generated: {result.generated_at}",
        "",
        "## Runtime",
        "",
        f"- Python: {result.environment.get('python_version')}",
        f"- Platform: {result.environment.get('platform')}",
        f"- CPU count: {result.environment.get('cpu_count')}",
        "",
        "## Cold Start",
        "",
        "| Algorithm | Cold start ms |",
        "| --- | ---: |",
    ]
    for algorithm, elapsed in sorted(result.cold_start_ms.items()):
        lines.append(f"| {algorithm} | {elapsed:.6f} |")

    lines.extend(
        [
            "",
            "## Steady-State Metrics",
            "",
            "| Case | Algorithm | ms | tok/s | acceptance | speedup | confidence |",
            "| --- | --- | ---: | ---: | ---: | ---: | --- |",
        ]
    )
    for row in result.rows:
        speedup = "" if row.speedup_vs_baseline is None else f"{row.speedup_vs_baseline:.3f}x"
        lines.append(
            "| "
            f"{row.case_name} | {row.algorithm} | {row.mean_elapsed_ms:.3f} | "
            f"{row.tokens_per_second:.2f} | {row.acceptance_rate:.3f} | {speedup} | "
            f"{row.confidence_note} |"
        )

    lines.extend(
        [
            "",
            "Confidence notes are intentionally conservative. Built-in algorithms are deterministic",
            "fixtures for validating benchmark plumbing; use external adapters for model claims.",
            "",
        ]
    )
    return "\n".join(lines)
