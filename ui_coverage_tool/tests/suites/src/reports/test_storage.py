import json
from pathlib import Path

import pytest

from ui_coverage_tool.config import Settings
from ui_coverage_tool.src.reports.models import CoverageReportState
from ui_coverage_tool.src.reports.storage import UIReportsStorage


# -------------------------------
# FIXTURES
# -------------------------------

@pytest.fixture
def fake_html_template(tmp_path: Path) -> Path:
    html_path = tmp_path / "template.html"
    html_path.write_text(
        '<html><head></head><body>'
        '<script id="state" type="application/json">OLD_STATE</script>'
        '</body></html>',
        encoding='utf-8',
    )
    return html_path


# -------------------------------
# TEST: inject_state_into_html
# -------------------------------

def test_inject_state_into_html_replaces_script_tag(
        monkeypatch: pytest.MonkeyPatch,
        reports_storage: UIReportsStorage,
        fake_html_template: Path,
        coverage_report_state: CoverageReportState,
):
    monkeypatch.setattr(Settings, "html_report_template_file", fake_html_template)

    result_html = reports_storage.inject_state_into_html(coverage_report_state)

    assert '<script id="state" type="application/json">' in result_html
    assert 'OLD_STATE' not in result_html
    assert 'createdAt' in result_html


def test_inject_state_into_html_returns_original_if_no_script(
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
        reports_storage: UIReportsStorage,
        coverage_report_state: CoverageReportState,
):
    html_file = tmp_path / "empty.html"
    html_file.write_text("<html><body>No script here</body></html>", encoding="utf-8")
    monkeypatch.setattr(Settings, "html_report_template_file", html_file)

    result = reports_storage.inject_state_into_html(coverage_report_state)
    assert result == "<html><body>No script here</body></html>"


# -------------------------------
# TEST: save_json_report
# -------------------------------

def test_save_json_report_creates_file(
        reports_storage: UIReportsStorage,
        coverage_report_state: CoverageReportState,
):
    reports_storage.save_json_report(coverage_report_state)

    file_path = reports_storage.settings.json_report_file
    assert file_path.exists()
    content = json.loads(file_path.read_text())
    assert "config" in content
    assert "appsCoverage" in content


def test_save_json_report_skips_if_not_configured(
        caplog: pytest.LogCaptureFixture,
        coverage_report_state: CoverageReportState,
        coverage_history_settings: Settings,
):
    coverage_history_settings.json_report_file = None
    storage = UIReportsStorage(coverage_history_settings)

    storage.save_json_report(coverage_report_state)
    assert any("skipping JSON report generation" in msg for msg in caplog.messages)


def test_save_json_report_logs_error(
        caplog: pytest.LogCaptureFixture,
        monkeypatch: pytest.MonkeyPatch,
        reports_storage: UIReportsStorage,
        coverage_report_state: CoverageReportState,
):
    def fake_write_text(_):
        raise OSError("disk full")

    monkeypatch.setattr(Path, "write_text", fake_write_text)

    reports_storage.save_json_report(coverage_report_state)
    assert any("Failed to write JSON report" in msg for msg in caplog.messages)


# -------------------------------
# TEST: save_html_report
# -------------------------------

def test_save_html_report_creates_file(
        monkeypatch: pytest.MonkeyPatch,
        reports_storage: UIReportsStorage,
        fake_html_template: Path,
        coverage_report_state: CoverageReportState,
):
    monkeypatch.setattr(Settings, "html_report_template_file", fake_html_template)

    reports_storage.save_html_report(coverage_report_state)

    html_path = reports_storage.settings.html_report_file
    assert html_path.exists()
    content = html_path.read_text(encoding='utf-8')
    assert '<script id="state" type="application/json">' in content
    assert 'createdAt' in content


def test_save_html_report_skips_if_not_configured(
        caplog: pytest.LogCaptureFixture,
        coverage_report_state: CoverageReportState,
        coverage_history_settings: Settings,
):
    coverage_history_settings.html_report_file = None
    storage = UIReportsStorage(coverage_history_settings)

    storage.save_html_report(coverage_report_state)
    assert any("skipping HTML report generation" in msg for msg in caplog.messages)


def test_save_html_report_logs_error(
        caplog: pytest.LogCaptureFixture,
        monkeypatch: pytest.MonkeyPatch,
        reports_storage: UIReportsStorage,
        fake_html_template: Path,
        coverage_report_state: CoverageReportState,
):
    monkeypatch.setattr(Settings, "html_report_template_file", fake_html_template)

    def fake_write_text(_, **__):
        raise OSError("disk full")

    monkeypatch.setattr(Path, "write_text", fake_write_text)

    reports_storage.save_html_report(coverage_report_state)
    assert any("Failed to write HTML report" in msg for msg in caplog.messages)
