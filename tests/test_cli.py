import json

from speculative_bench.cli import main


def test_cli_list_algorithms(capsys):
    assert main(["list-algorithms"]) == 0
    out = capsys.readouterr().out
    assert "baseline" in out


def test_cli_run_writes_reports(tmp_path):
    assert main(["run", "--out", str(tmp_path), "--repeats", "1", "--warmups", "0"]) == 0

    payload = json.loads((tmp_path / "benchmark-results.json").read_text(encoding="utf-8"))
    assert payload["rows"]
    assert payload["cold_start_ms"]["baseline"] > 0


def test_cli_defaults_to_run(capsys):
    assert main([]) == 0
    out = capsys.readouterr().out
    assert "benchmark-results.json" in out


def test_cli_empty_tag_filter_exits_cleanly(capsys):
    assert main(["run", "--tag", "does-not-exist"]) == 0
    out = capsys.readouterr().out
    assert "no benchmark cases matched the requested tags: does-not-exist" in out
