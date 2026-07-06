from __future__ import annotations

import json
from importlib import resources
from pathlib import Path
from typing import Iterable, List, Mapping, Sequence

from speculative_bench.types import BenchmarkCase


def _case_items(payload: object) -> Sequence[Mapping[str, object]]:
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict) and isinstance(payload.get("cases"), list):
        return payload["cases"]
    raise ValueError("case file must be a JSON list or an object with a 'cases' list")


def load_cases(path: str | Path | None = None) -> List[BenchmarkCase]:
    if path is None:
        with resources.files("speculative_bench.data").joinpath("default_cases.json").open(
            "r",
            encoding="utf-8",
        ) as handle:
            payload = json.load(handle)
    else:
        with Path(path).open("r", encoding="utf-8") as handle:
            payload = json.load(handle)

    cases = [BenchmarkCase.from_mapping(item) for item in _case_items(payload)]
    names = [case.name for case in cases]
    duplicates = sorted({name for name in names if names.count(name) > 1})
    if duplicates:
        raise ValueError(f"duplicate benchmark case names: {', '.join(duplicates)}")
    return cases


def filter_cases(cases: Iterable[BenchmarkCase], tags: Sequence[str] | None = None) -> List[BenchmarkCase]:
    if not tags:
        return list(cases)
    requested = set(tags)
    return [case for case in cases if requested.intersection(case.tags)]
