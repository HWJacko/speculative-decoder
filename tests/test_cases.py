import json

import pytest

from speculative_bench.cases import filter_cases, load_cases


def test_load_default_cases():
    cases = load_cases()

    assert len(cases) == 3
    assert cases[0].name == "short_instruction"
    assert cases[0].target_tokens > 0


def test_load_custom_cases(tmp_path):
    path = tmp_path / "cases.json"
    path.write_text(
        json.dumps(
            {
                "cases": [
                    {
                        "name": "custom",
                        "prompt": "Measure this.",
                        "target_tokens": 12,
                        "draft_tokens": 16,
                        "acceptance_pattern": [1, 0, 1],
                        "tags": ["custom"],
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    cases = load_cases(path)

    assert cases[0].name == "custom"
    assert filter_cases(cases, ["custom"]) == cases
    assert filter_cases(cases, ["missing"]) == []


def test_duplicate_case_names_fail(tmp_path):
    path = tmp_path / "cases.json"
    payload = {
        "cases": [
            {
                "name": "same",
                "prompt": "A",
                "target_tokens": 1,
                "draft_tokens": 1,
                "acceptance_pattern": [1],
            },
            {
                "name": "same",
                "prompt": "B",
                "target_tokens": 1,
                "draft_tokens": 1,
                "acceptance_pattern": [1],
            },
        ]
    }
    path.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(ValueError, match="duplicate"):
        load_cases(path)
