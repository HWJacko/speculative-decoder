from speculative_bench.metrics import acceptance_rate, draft_efficiency, summarize_runs, tokens_per_second
from speculative_bench.types import DecoderRun


def test_basic_metric_helpers():
    run = DecoderRun(
        algorithm="spec",
        case_name="case",
        repetition=0,
        target_tokens=10,
        output_tokens=10,
        draft_tokens=8,
        accepted_tokens=6,
        rejected_tokens=2,
        model_steps=4,
        elapsed_ms=5.0,
    )

    assert acceptance_rate(run) == 0.75
    assert draft_efficiency(run) == 0.6
    assert tokens_per_second(10, 5.0) == 2000.0


def test_summarize_runs_includes_speedup():
    runs = [
        DecoderRun("baseline", "case", 0, 10, 10, 0, 0, 0, 10, 10.0),
        DecoderRun("baseline", "case", 1, 10, 10, 0, 0, 0, 10, 12.0),
        DecoderRun("spec", "case", 0, 10, 10, 12, 8, 4, 5, 5.0),
        DecoderRun("spec", "case", 1, 10, 10, 12, 8, 4, 5, 6.0),
    ]

    rows = summarize_runs(runs)
    spec_row = next(row for row in rows if row.algorithm == "spec")

    assert spec_row.speedup_vs_baseline == 2.0
    assert spec_row.model_step_reduction_vs_baseline == 0.5
    assert spec_row.confidence_note.startswith("low")
