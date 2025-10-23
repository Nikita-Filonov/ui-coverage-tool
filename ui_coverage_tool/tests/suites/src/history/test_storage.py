import json
from datetime import datetime
from pathlib import Path

import pytest

from ui_coverage_tool.config import Settings
from ui_coverage_tool.src.coverage.models import AppCoverage, ElementCoverage, ActionCoverage
from ui_coverage_tool.src.history.models import (
    CoverageHistoryState,
    AppHistoryState,
    AppHistory,
    ElementHistory,
    ActionHistory,
)
from ui_coverage_tool.src.history.selector import build_selector_key
from ui_coverage_tool.src.history.storage import UICoverageHistoryStorage
from ui_coverage_tool.src.reports.models import CoverageReportState, CoverageReportConfig
from ui_coverage_tool.src.tools.actions import ActionType
from ui_coverage_tool.src.tools.selector import SelectorType
from ui_coverage_tool.src.tools.types import AppKey, Selector


# -------------------------------
# TEST: load
# -------------------------------

def test_load_returns_empty_if_no_history_file(coverage_history_settings: Settings) -> None:
    coverage_history_settings.history_file = None
    storage = UICoverageHistoryStorage(coverage_history_settings)

    result = storage.load()

    assert isinstance(result, CoverageHistoryState)
    assert result.apps == {}


def test_load_returns_empty_if_file_not_exists(coverage_history_settings: Settings) -> None:
    assert not coverage_history_settings.history_file.exists()
    storage = UICoverageHistoryStorage(coverage_history_settings)

    result = storage.load()

    assert isinstance(result, CoverageHistoryState)
    assert result.apps == {}


def test_load_reads_valid_json(coverage_history_settings: Settings) -> None:
    state = CoverageHistoryState(apps={AppKey("ui-app"): AppHistoryState()})
    coverage_history_settings.history_file.write_text(state.model_dump_json(by_alias=True))

    storage = UICoverageHistoryStorage(coverage_history_settings)
    result = storage.load()

    assert isinstance(result, CoverageHistoryState)
    assert "ui-app" in result.apps


def test_load_handles_invalid_json(coverage_history_settings: Settings) -> None:
    coverage_history_settings.history_file.write_text("{ invalid json }")

    storage = UICoverageHistoryStorage(coverage_history_settings)
    result = storage.load()

    assert isinstance(result, CoverageHistoryState)
    assert result.apps == {}


# -------------------------------
# TEST: save
# -------------------------------

def test_save_creates_and_writes_file(coverage_history_settings: Settings) -> None:
    state = CoverageHistoryState(apps={AppKey("ui-app"): AppHistoryState()})
    storage = UICoverageHistoryStorage(coverage_history_settings)

    storage.save(state)

    file_path: Path = coverage_history_settings.history_file
    assert file_path.exists()
    content = json.loads(file_path.read_text())
    assert "apps" in content


def test_save_logs_error(
        caplog: pytest.LogCaptureFixture,
        monkeypatch: pytest.MonkeyPatch,
        coverage_history_settings: Settings,
) -> None:
    state = CoverageHistoryState()
    storage = UICoverageHistoryStorage(coverage_history_settings)

    def fake_write_text(_):
        raise OSError("disk full")

    monkeypatch.setattr(Path, "write_text", fake_write_text)

    storage.save(state)
    assert any("Error saving history" in msg for msg in caplog.messages)


def test_save_skips_if_no_file(coverage_history_settings: Settings, caplog: pytest.LogCaptureFixture) -> None:
    coverage_history_settings.history_file = None
    storage = UICoverageHistoryStorage(coverage_history_settings)
    storage.save(CoverageHistoryState())

    assert any("skipping" in msg.lower() or "not defined" in msg.lower() for msg in caplog.messages)


# -------------------------------
# TEST: save_from_report
# -------------------------------

def test_save_from_report_builds_correct_state(
        monkeypatch: pytest.MonkeyPatch,
        coverage_history_settings: Settings,
) -> None:
    called: dict[str, CoverageHistoryState] = {}

    def mock_save(state: CoverageHistoryState) -> None:
        called["state"] = state

    storage = UICoverageHistoryStorage(coverage_history_settings)
    monkeypatch.setattr(storage, "save", mock_save)

    app_key = coverage_history_settings.apps[0].key
    selector = Selector("#submit")

    action_history = [ActionHistory(type=ActionType.CLICK, count=1)]
    element_history = [ElementHistory(actions=action_history, created_at=datetime.now())]

    app_coverage = AppCoverage(
        history=[
            AppHistory(
                actions=action_history,
                created_at=datetime.now(),
                total_actions=5,
                total_elements=2,
            )
        ],
        elements=[
            ElementCoverage(
                history=element_history,
                actions=[ActionCoverage(type=ActionType.CLICK, count=1)],
                selector=selector,
                selector_type=SelectorType.CSS,
            )
        ],
    )

    report = CoverageReportState(
        config=CoverageReportConfig(apps=coverage_history_settings.apps),
        apps_coverage={app_key: app_coverage},
    )

    storage.save_from_report(report)

    assert "state" in called
    state = called["state"]
    assert isinstance(state, CoverageHistoryState)
    assert app_key in state.apps

    app_state = state.apps[app_key]
    assert isinstance(app_state, AppHistoryState)
    assert len(app_state.total) == 1
    assert len(app_state.elements) == 1

    key = build_selector_key(selector, SelectorType.CSS)
    assert key in app_state.elements
    assert isinstance(app_state.elements[key][0], ElementHistory)
