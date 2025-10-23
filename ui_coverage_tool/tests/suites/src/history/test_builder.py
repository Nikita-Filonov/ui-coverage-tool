from datetime import datetime, timedelta
from pathlib import Path

from ui_coverage_tool.config import Settings
from ui_coverage_tool.src.history.builder import UICoverageHistoryBuilder
from ui_coverage_tool.src.history.models import (
    ActionHistory,
    ElementHistory,
    AppHistory,
    AppHistoryState,
)
from ui_coverage_tool.src.history.selector import build_selector_key
from ui_coverage_tool.src.tools.actions import ActionType
from ui_coverage_tool.src.tools.selector import SelectorType
from ui_coverage_tool.src.tools.types import Selector


# -------------------------------
# TEST: build_app_history
# -------------------------------

def test_build_app_history_creates_valid_instance(coverage_history_settings: Settings) -> None:
    builder = UICoverageHistoryBuilder(AppHistoryState(), coverage_history_settings)
    actions = [ActionHistory(type=ActionType.CLICK, count=5)]

    result = builder.build_app_history(actions, total_actions=10, total_elements=3)

    assert isinstance(result, AppHistory)
    assert result.actions == actions
    assert result.total_actions == 10
    assert result.total_elements == 3
    assert abs((result.created_at - builder.created_at).total_seconds()) < 1


# -------------------------------
# TEST: build_element_history
# -------------------------------

def test_build_element_history_creates_valid_instance(coverage_history_settings: Settings) -> None:
    builder = UICoverageHistoryBuilder(AppHistoryState(), coverage_history_settings)
    actions = [ActionHistory(type=ActionType.HOVER, count=2)]

    result = builder.build_element_history(actions)

    assert isinstance(result, ElementHistory)
    assert result.actions == actions
    assert abs((result.created_at - builder.created_at).total_seconds()) < 1


# -------------------------------
# TEST: append_history
# -------------------------------

def test_append_history_appends_and_sorts(coverage_history_settings: Settings) -> None:
    builder = UICoverageHistoryBuilder(AppHistoryState(), coverage_history_settings)

    old_item = ElementHistory(
        created_at=datetime.now() - timedelta(days=1),
        actions=[ActionHistory(type=ActionType.CLICK, count=1)],
    )

    def build_new() -> ElementHistory:
        return ElementHistory(
            created_at=datetime.now(),
            actions=[ActionHistory(type=ActionType.HOVER, count=2)],
        )

    result = builder.append_history([old_item], build_new)

    assert len(result) == 2
    assert result[0].actions[0].type == ActionType.CLICK
    assert result[1].actions[0].type == ActionType.HOVER
    assert result[0].created_at < result[1].created_at


def test_append_history_returns_empty_if_no_history_file(tmp_path: Path) -> None:
    settings = Settings(results_dir=tmp_path / "results")
    settings.history_file = None
    builder = UICoverageHistoryBuilder(AppHistoryState(), settings)

    def build_new() -> ElementHistory:
        return ElementHistory(
            created_at=datetime.now(),
            actions=[ActionHistory(type=ActionType.CLICK, count=1)],
        )

    result = builder.append_history([], build_new)
    assert result == []


def test_append_history_does_not_add_if_no_actions(coverage_history_settings: Settings) -> None:
    builder = UICoverageHistoryBuilder(AppHistoryState(), coverage_history_settings)

    history = [
        ElementHistory(
            created_at=datetime.now(),
            actions=[ActionHistory(type=ActionType.CLICK, count=1)],
        )
    ]

    def build_empty() -> ElementHistory:
        return ElementHistory(created_at=datetime.now(), actions=[])

    result = builder.append_history(history, build_empty)
    assert result == history


def test_append_history_respects_retention_limit(coverage_history_settings: Settings) -> None:
    builder = UICoverageHistoryBuilder(AppHistoryState(), coverage_history_settings)

    old_items = [
        ElementHistory(
            created_at=datetime.now() - timedelta(days=i),
            actions=[ActionHistory(type=ActionType.CLICK, count=1)],
        )
        for i in range(5)
    ]

    def build_new() -> ElementHistory:
        return ElementHistory(
            created_at=datetime.now(),
            actions=[ActionHistory(type=ActionType.HOVER, count=2)],
        )

    result = builder.append_history(old_items, build_new)
    assert len(result) == 3
    assert all(isinstance(item, ElementHistory) for item in result)


# -------------------------------
# TEST: get_app_history
# -------------------------------

def test_get_app_history_adds_record(coverage_history_settings: Settings) -> None:
    builder = UICoverageHistoryBuilder(AppHistoryState(), coverage_history_settings)
    actions = [ActionHistory(type=ActionType.CLICK, count=1)]

    result = builder.get_app_history(actions, total_actions=5, total_elements=2)

    assert isinstance(result, list)
    assert isinstance(result[-1], AppHistory)
    assert result[-1].total_actions == 5
    assert result[-1].total_elements == 2


# -------------------------------
# TEST: get_element_history
# -------------------------------

def test_get_element_history_creates_new_entry(coverage_history_settings: Settings) -> None:
    builder = UICoverageHistoryBuilder(AppHistoryState(), coverage_history_settings)
    actions = [ActionHistory(type=ActionType.FILL, count=3)]

    result = builder.get_element_history(actions, Selector("#input"), SelectorType.CSS)

    assert isinstance(result, list)
    assert isinstance(result[-1], ElementHistory)
    assert result[-1].actions == actions


def test_get_element_history_uses_existing_data(coverage_history_settings: Settings) -> None:
    builder = UICoverageHistoryBuilder(AppHistoryState(), coverage_history_settings)
    key = build_selector_key(Selector("#search"), SelectorType.CSS)

    old_entry = ElementHistory(
        created_at=datetime.now() - timedelta(days=1),
        actions=[ActionHistory(type=ActionType.HOVER, count=1)],
    )
    builder.history.elements[key] = [old_entry]

    new_actions = [ActionHistory(type=ActionType.CLICK, count=2)]
    result = builder.get_element_history(new_actions, Selector("#search"), SelectorType.CSS)

    assert len(result) == 2
    assert result[0].actions[0].type == ActionType.HOVER
    assert result[1].actions[0].type == ActionType.CLICK
