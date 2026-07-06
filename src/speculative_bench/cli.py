from __future__ import annotations

import argparse
from pathlib import Path
from typing import Sequence

from speculative_bench.algorithms import builtin_algorithm_names, get_builtin_adapters
from speculative_bench.cases import filter_cases, load_cases
from speculative_bench.config import BenchmarkConfig
from speculative_bench.reporting import write_reports
from speculative_bench.runner import BenchmarkRunner


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="speculative-bench",
        description="Run repeatable speculative decoding benchmark scenarios.",
    )
    subparsers = parser.add_subparsers(dest="command")

    run = subparsers.add_parser("run", help="run benchmarks and write reports")
    run.add_argument("--cases", type=Path, default=None, help="path to a JSON case file")
    run.add_argument(
        "--algorithm",
        action="append",
        choices=builtin_algorithm_names(),
        help="built-in algorithm to include; repeat for multiple values",
    )
    run.add_argument("--tag", action="append", help="include only cases with this tag")
    run.add_argument("--repeats", type=int, default=3, help="steady-state repetitions per case")
    run.add_argument("--warmups", type=int, default=1, help="warmup repetitions per case")
    run.add_argument("--seed", type=int, default=20260706, help="deterministic fixture seed")
    run.add_argument("--out", type=Path, default=Path("reports"), help="output directory")
    run.add_argument(
        "--formats",
        default="json,csv,md",
        help="comma-separated report formats: json,csv,md",
    )

    subparsers.add_parser("list-algorithms", help="print built-in algorithm names")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command is None:
        args = parser.parse_args(["run"])

    if args.command == "list-algorithms":
        for name in builtin_algorithm_names():
            print(name)
        return 0

    if args.command == "run":
        config = BenchmarkConfig.from_values(
            repeats=args.repeats,
            warmups=args.warmups,
            seed=args.seed,
            output_dir=args.out,
            formats=args.formats,
        )
        cases = filter_cases(load_cases(args.cases), args.tag)
        if not cases:
            requested = ", ".join(args.tag or [])
            print(f"no benchmark cases matched the requested tags: {requested}")
            return 0
        adapters = get_builtin_adapters(args.algorithm)
        result = BenchmarkRunner(cases=cases, adapters=adapters, config=config).run()
        written = write_reports(result, config.output_dir, config.formats)
        for fmt, path in sorted(written.items()):
            print(f"{fmt}: {path}")
        return 0

    parser.error("unknown command")
    return 2
