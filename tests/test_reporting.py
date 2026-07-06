from speculative_bench.algorithms import get_builtin_adapters
from speculative_bench.cases import load_cases
from speculative_bench.config import BenchmarkConfig
from speculative_bench.reporting import markdown_summary, write_reports
from speculative_bench.runner import BenchmarkRunner


def test_write_reports(tmp_path):
    result = BenchmarkRunner(
        load_cases()[:1],
        get_builtin_adapters(["baseline"]),
        BenchmarkConfig(repeats=1, warmups=0, output_dir=tmp_path),
    ).run()

    written = write_reports(result, tmp_path, ("json", "csv", "md"))

    assert set(written) == {"json", "csv", "md"}
    assert (tmp_path / "benchmark-results.json").exists()
    assert (tmp_path / "benchmark-results.csv").exists()
    assert (tmp_path / "benchmark-summary.md").exists()
    assert "Speculative Decoding Benchmark Summary" in markdown_summary(result)
