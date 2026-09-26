import json
import re
from pathlib import Path

import pytest
from click.testing import CliRunner

from ui_coverage_tool.cli.main import cli
from ui_coverage_tool.config import AppConfig, Settings
from ui_coverage_tool.src.tools.actions import ActionType
from ui_coverage_tool.src.tools.selector import SelectorType
from ui_coverage_tool.src.tracker.core import UICoverageTracker

runner = CliRunner()


def test_print_config_outputs_resolved_settings(
        settings: Settings,
        monkeypatch: pytest.MonkeyPatch,
        caplog: pytest.LogCaptureFixture,
) -> None:
    monkeypatch.setattr("ui_coverage_tool.cli.commands.print_config.get_settings", lambda: settings)

    result = runner.invoke(cli, ["print-config"])

    assert result.exit_code == 0
    config = json.loads(next(record.message for record in caplog.records if record.name == "PRINT_CONFIG"))
    assert config["apps"][0]["key"] == "test-service"
    assert config["results_dir"] == str(settings.results_dir)


def test_copy_report_updates_template(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    source = tmp_path / "submodules/ui-coverage-report/build/index.html"
    destination = tmp_path / "ui_coverage_tool/src/reports/templates/index.html"
    source.parent.mkdir(parents=True)
    destination.parent.mkdir(parents=True)
    source.write_text("<html>new template</html>", encoding="utf-8")
    destination.write_text("old template", encoding="utf-8")

    result = runner.invoke(cli, ["copy-report"])

    assert result.exit_code == 0
    assert destination.read_text(encoding="utf-8") == "<html>new template</html>"


def test_copy_report_keeps_template_when_build_is_missing(
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.chdir(tmp_path)
    destination = tmp_path / "ui_coverage_tool/src/reports/templates/index.html"
    destination.parent.mkdir(parents=True)
    destination.write_text("current template", encoding="utf-8")

    result = runner.invoke(cli, ["copy-report"])

    assert result.exit_code == 0
    assert destination.read_text(encoding="utf-8") == "current template"


def test_copy_report_logs_copy_error(
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
        caplog: pytest.LogCaptureFixture,
) -> None:
    monkeypatch.chdir(tmp_path)
    source = tmp_path / "submodules/ui-coverage-report/build/index.html"
    source.parent.mkdir(parents=True)
    source.write_text("new template", encoding="utf-8")

    def fail_copy(*args, **kwargs) -> None:
        raise OSError("disk full")

    monkeypatch.setattr("ui_coverage_tool.cli.commands.copy_report.shutil.copy", fail_copy)

    result = runner.invoke(cli, ["copy-report"])

    assert result.exit_code == 0
    assert any("Error copying the report: disk full" in message for message in caplog.messages)


@pytest.fixture
def report_template(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    template = tmp_path / "template.html"
    template.write_text(
        '<html><body><script id="state" type="application/json">OLD_STATE</script></body></html>',
        encoding="utf-8",
    )
    monkeypatch.setattr(Settings, "html_report_template_file", template)
    return template


def test_save_report_builds_separate_app_reports_and_embeds_json(
        reports_settings: Settings,
        report_template: Path,
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    reports_settings.apps.extend([
        AppConfig(key="second-app", name="Second App", url="https://second.example.com"),
        AppConfig(key="empty-app", name="Empty App", url="https://empty.example.com"),
    ])
    monkeypatch.setattr("ui_coverage_tool.cli.commands.save_report.get_settings", lambda: reports_settings)

    first = UICoverageTracker(app="test-service", settings=reports_settings)
    first.track_coverage("button", ActionType.CLICK, SelectorType.CSS)
    first.track_coverage("button", ActionType.CLICK, SelectorType.CSS)
    first.track_coverage("button", ActionType.VISIBLE, SelectorType.XPATH)
    second = UICoverageTracker(app="second-app", settings=reports_settings)
    second.track_coverage("#name", ActionType.FILL, SelectorType.CSS)

    result = runner.invoke(cli, ["save-report"])

    assert result.exit_code == 0, result.output
    report = json.loads(reports_settings.json_report_file.read_text(encoding="utf-8"))
    assert set(report["appsCoverage"]) == {"test-service", "second-app", "empty-app"}

    first_coverage = report["appsCoverage"]["test-service"]
    assert first_coverage["history"][-1]["totalActions"] == 3
    assert first_coverage["history"][-1]["totalElements"] == 2
    elements = {element["selectorType"]: element for element in first_coverage["elements"]}
    assert elements["CSS"]["actions"] == [{"type": "CLICK", "count": 2}]
    assert elements["XPATH"]["actions"] == [{"type": "VISIBLE", "count": 1}]
    assert report["appsCoverage"]["second-app"]["history"][-1]["totalActions"] == 1
    assert report["appsCoverage"]["empty-app"] == {"history": [], "elements": []}

    html = reports_settings.html_report_file.read_text(encoding="utf-8")
    match = re.search(r'<script id="state" type="application/json">(.*?)</script>', html)
    assert match is not None
    assert json.loads(match.group(1)) == report
    history = json.loads(reports_settings.history_file.read_text(encoding="utf-8"))
    assert history["apps"]["test-service"]["total"] == first_coverage["history"]


def test_save_report_preserves_history_across_runs_with_retention_limit(
        reports_settings: Settings,
        report_template: Path,
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    reports_settings.history_retention_limit = 2
    monkeypatch.setattr("ui_coverage_tool.cli.commands.save_report.get_settings", lambda: reports_settings)
    tracker = UICoverageTracker(app="test-service", settings=reports_settings)

    for _ in range(3):
        tracker.track_coverage("#save", ActionType.CLICK, SelectorType.CSS)
        result = runner.invoke(cli, ["save-report"])
        assert result.exit_code == 0, result.output

    report = json.loads(reports_settings.json_report_file.read_text(encoding="utf-8"))
    app = report["appsCoverage"]["test-service"]
    assert [entry["totalActions"] for entry in app["history"]] == [2, 3]
    assert [entry["actions"][0]["count"] for entry in app["elements"][0]["history"]] == [2, 3]

    history = json.loads(reports_settings.history_file.read_text(encoding="utf-8"))
    assert [entry["totalActions"] for entry in history["apps"]["test-service"]["total"]] == [2, 3]
