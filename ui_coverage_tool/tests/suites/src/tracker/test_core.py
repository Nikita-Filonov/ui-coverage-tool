import pytest

from ui_coverage_tool.config import Settings
from ui_coverage_tool.src.tools.actions import ActionType
from ui_coverage_tool.src.tools.selector import SelectorType
from ui_coverage_tool.src.tools.types import AppKey, Selector
from ui_coverage_tool.src.tracker.core import UICoverageTracker
from ui_coverage_tool.src.tracker.models import CoverageResult


# -------------------------------
# TEST: init
# -------------------------------

def test_init_creates_storage(settings: Settings) -> None:
    tracker = UICoverageTracker(app="ui-app", settings=settings)

    assert tracker.app == "ui-app"
    assert isinstance(tracker.storage, object)
    assert tracker.settings is settings


def test_init_uses_default_settings(monkeypatch: pytest.MonkeyPatch) -> None:
    called: dict[str, bool] = {}

    def fake_get_settings() -> Settings:
        called["used"] = True
        return Settings()

    monkeypatch.setattr("ui_coverage_tool.src.tracker.core.get_settings", fake_get_settings)

    tracker = UICoverageTracker(app="ui-app")

    assert called["used"] is True
    assert isinstance(tracker.settings, Settings)


# -------------------------------
# TEST: track_coverage
# -------------------------------

def test_track_coverage_calls_storage_save(settings: Settings, monkeypatch: pytest.MonkeyPatch) -> None:
    tracker = UICoverageTracker(app="ui-app", settings=settings)

    called: dict[str, CoverageResult] = {}

    def mock_save(result: CoverageResult) -> None:
        called["result"] = result
        assert isinstance(result, CoverageResult)
        assert result.app == AppKey("ui-app")
        assert result.selector == Selector("#login-btn")
        assert result.action_type == ActionType.CLICK
        assert result.selector_type == SelectorType.CSS

    monkeypatch.setattr(tracker.storage, "save", mock_save)

    tracker.track_coverage(
        selector="#login-btn",
        action_type=ActionType.CLICK,
        selector_type=SelectorType.CSS,
    )

    assert "result" in called


def test_track_coverage_multiple_calls(settings: Settings, monkeypatch: pytest.MonkeyPatch) -> None:
    tracker = UICoverageTracker(app="ui-app", settings=settings)
    saved: list[CoverageResult] = []

    def mock_save(result: CoverageResult) -> None:
        saved.append(result)

    monkeypatch.setattr(tracker.storage, "save", mock_save)

    tracker.track_coverage("#submit", ActionType.CLICK, SelectorType.CSS)
    tracker.track_coverage(".input", ActionType.HOVER, SelectorType.CSS)

    assert len(saved) == 2
    assert saved[0].selector == "#submit"
    assert saved[1].selector == ".input"
    assert all(isinstance(r, CoverageResult) for r in saved)
