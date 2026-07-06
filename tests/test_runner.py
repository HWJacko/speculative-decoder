from speculative_bench.algorithms import get_builtin_adapters
from speculative_bench.cases import load_cases
from speculative_bench.config import BenchmarkConfig
from speculative_bench.runner import BenchmarkRunner


def test_runner_separates_cold_start_and_steady_state():
    cases = load_cases()[:1]
    adapters = get_builtin_adapters(["baseline", "speculative-balanced"])
    config = BenchmarkConfig(repeats=2, warmups=1)

    result = BenchmarkRunner(cases, adapters, config).run()

    assert result.cold_start_ms["baseline"] > 0
    assert len(result.runs) == 4
    assert {run.phase for run in result.runs} == {"steady_state"}
    assert {row.algorithm for row in result.rows} == {"baseline", "speculative-balanced"}


def test_runner_is_deterministic_for_default_simulators():
    cases = load_cases()[:1]
    adapters = get_builtin_adapters(["speculative-balanced"])
    config = BenchmarkConfig(repeats=2, warmups=0, seed=123)

    first = BenchmarkRunner(cases, adapters, config).run()
    second = BenchmarkRunner(cases, adapters, config).run()

    assert [run.to_dict() for run in first.runs] == [run.to_dict() for run in second.runs]
