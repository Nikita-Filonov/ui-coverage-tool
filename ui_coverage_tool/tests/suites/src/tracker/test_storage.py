import json
from pathlib import Path

import pytest

from ui_coverage_tool.config import Settings
from ui_coverage_tool.src.tracker.models import CoverageResult, CoverageResultList
from ui_coverage_tool.src.tracker.storage import UICoverageTrackerStorage


# -------------------------------
# TEST: clear
# -------------------------------

def test_clear_removes_result_json_and_preserves_other_files(
        settings: Settings,
        coverage_result: CoverageResult,
        coverage_tracker_storage: UICoverageTrackerStorage,
        caplog: pytest.LogCaptureFixture,
) -> None:
    settings.history_file = settings.results_dir / "history.json"
    settings.json_report_file = settings.results_dir / "report.json"
    settings.history_file.write_text("history", encoding="utf-8")
    settings.json_report_file.write_text("report", encoding="utf-8")
    (settings.results_dir / "notes.txt").write_text("keep", encoding="utf-8")
    (settings.results_dir / "other.json").write_text("remove", encoding="utf-8")
    nested_dir = settings.results_dir / "nested"
    nested_dir.mkdir()
    (nested_dir / "other.json").write_text("keep", encoding="utf-8")
    coverage_tracker_storage.save(coverage_result)
    coverage_tracker_storage.save(coverage_result)

    coverage_tracker_storage.clear()

    assert sorted(file.name for file in settings.results_dir.glob("*.json")) == ["history.json", "report.json"]
    assert (settings.results_dir / "notes.txt").read_text(encoding="utf-8") == "keep"
    assert (nested_dir / "other.json").read_text(encoding="utf-8") == "keep"
    assert any("Removed 3 coverage files" in message for message in caplog.messages)


def test_clear_succeeds_when_directory_is_missing(
        settings: Settings,
        coverage_tracker_storage: UICoverageTrackerStorage,
) -> None:
    settings.results_dir = settings.results_dir / "missing"

    coverage_tracker_storage.clear()

    assert not settings.results_dir.exists()


def test_clear_raises_when_path_is_not_a_directory(
        settings: Settings,
        coverage_tracker_storage: UICoverageTrackerStorage,
        tmp_path: Path,
) -> None:
    settings.results_dir = tmp_path / "results.json"
    settings.results_dir.write_text("keep", encoding="utf-8")

    with pytest.raises(NotADirectoryError, match="not a directory"):
        coverage_tracker_storage.clear()

    assert settings.results_dir.read_text(encoding="utf-8") == "keep"


# -------------------------------
# TEST: save
# -------------------------------

def test_save_creates_json_file(
        settings: Settings,
        coverage_result: CoverageResult,
        coverage_tracker_storage: UICoverageTrackerStorage,
) -> None:
    coverage_tracker_storage.save(coverage_result)

    files: list[Path] = list(settings.results_dir.glob("*.json"))
    assert len(files) == 1

    content: dict = json.loads(files[0].read_text())
    assert content["app"] == "ui-app"
    assert content["selector"] == "#submit"
    assert content["action_type"] == coverage_result.action_type
    assert content["selector_type"] == coverage_result.selector_type


def test_save_creates_dir_if_missing(
        caplog: pytest.LogCaptureFixture,
        tmp_path: Path,
        settings: Settings,
        coverage_result: CoverageResult,
) -> None:
    results_dir: Path = tmp_path / "nested" / "results"
    settings.results_dir = results_dir
    storage = UICoverageTrackerStorage(settings)

    assert not results_dir.exists()

    storage.save(coverage_result)

    assert results_dir.exists()
    assert any("creating" in msg.lower() for msg in caplog.messages)
    assert list(results_dir.glob("*.json"))


def test_save_logs_error(
        caplog: pytest.LogCaptureFixture,
        monkeypatch: pytest.MonkeyPatch,
        coverage_result: CoverageResult,
        coverage_tracker_storage: UICoverageTrackerStorage,
) -> None:
    def fake_write_text(_: str) -> None:
        raise OSError("Disk full")

    monkeypatch.setattr(Path, "write_text", fake_write_text)
    coverage_tracker_storage.save(coverage_result)

    assert any("error saving coverage data" in msg.lower() for msg in caplog.messages)


# -------------------------------
# TEST: load
# -------------------------------

def test_load_returns_empty_if_dir_missing(
        caplog: pytest.LogCaptureFixture,
        tmp_path: Path,
        settings: Settings
) -> None:
    settings.results_dir = tmp_path / "missing"
    storage = UICoverageTrackerStorage(settings)

    result: CoverageResultList = storage.load()

    assert isinstance(result, CoverageResultList)
    assert result.root == []
    assert any("does not exist" in msg.lower() or "results directory" in msg.lower() for msg in caplog.messages)


def test_load_reads_json_files(
        settings: Settings,
        coverage_result: CoverageResult,
        coverage_tracker_storage: UICoverageTrackerStorage,
) -> None:
    file_path: Path = settings.results_dir / "one.json"
    settings.results_dir.mkdir(exist_ok=True)
    file_path.write_text(coverage_result.model_dump_json())

    result: CoverageResultList = coverage_tracker_storage.load()

    assert isinstance(result, CoverageResultList)
    assert len(result.root) == 1
    parsed: CoverageResult = result.root[0]
    assert parsed.selector == "#submit"
    assert parsed.action_type == coverage_result.action_type


def test_load_ignores_non_json_files(
        settings: Settings,
        coverage_result: CoverageResult,
        coverage_tracker_storage: UICoverageTrackerStorage,
) -> None:
    settings.results_dir.mkdir(exist_ok=True)
    (settings.results_dir / "valid.json").write_text(coverage_result.model_dump_json())
    (settings.results_dir / "note.txt").write_text("not json")

    result: CoverageResultList = coverage_tracker_storage.load()

    assert len(result.root) == 1
    assert all(isinstance(r, CoverageResult) for r in result.root)
    assert result.root[0].app == "ui-app"
