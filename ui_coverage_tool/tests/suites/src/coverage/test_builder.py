from pathlib import Path

from ui_coverage_tool.config import Settings
from ui_coverage_tool.src.coverage.builder import UICoverageBuilder
from ui_coverage_tool.src.coverage.models import AppCoverage, ElementCoverage
from ui_coverage_tool.src.history.builder import UICoverageHistoryBuilder
from ui_coverage_tool.src.history.models import (
    AppHistoryState,
    AppHistory,
    ElementHistory,
)
from ui_coverage_tool.src.tools.actions import ActionType
from ui_coverage_tool.src.tools.selector import SelectorType
from ui_coverage_tool.src.tools.types import Selector, AppKey
from ui_coverage_tool.src.tracker.models import CoverageResult, CoverageResultList


# -------------------------------
# TEST: build_element_coverage
# -------------------------------

def test_build_element_coverage_creates_valid_element(tmp_path: Path):
    results = CoverageResultList(
        root=[
            CoverageResult(
                app=AppKey("ui-app"),
                selector=Selector("#submit"),
                action_type=ActionType.CLICK,
                selector_type=SelectorType.CSS,
            ),
            CoverageResult(
                app=AppKey("ui-app"),
                selector=Selector("#submit"),
                action_type=ActionType.HOVER,
                selector_type=SelectorType.CSS,
            ),
        ]
    )

    settings = Settings(apps=[])
    settings.history_file = tmp_path / "history.json"
    history_builder = UICoverageHistoryBuilder(AppHistoryState(), settings)
    builder = UICoverageBuilder(results, history_builder)

    result = builder.build_element_coverage(results, Selector("#submit"), SelectorType.CSS)

    assert isinstance(result, ElementCoverage)
    assert result.selector == Selector("#submit")
    assert result.selector_type == SelectorType.CSS
    assert any(a.type == ActionType.CLICK for a in result.actions)
    assert any(a.type == ActionType.HOVER for a in result.actions)
    assert all(a.count >= 1 for a in result.actions)
    assert isinstance(result.history, list)
    assert isinstance(result.history[-1], ElementHistory)


def test_build_element_coverage_skips_unused_actions(tmp_path: Path):
    results = CoverageResultList(
        root=[
            CoverageResult(
                app=AppKey("ui-app"),
                selector=Selector("#btn"),
                action_type=ActionType.CLICK,
                selector_type=SelectorType.CSS,
            )
        ]
    )

    settings = Settings(apps=[])
    settings.history_file = tmp_path / "history.json"
    builder = UICoverageBuilder(results, UICoverageHistoryBuilder(AppHistoryState(), settings))

    result = builder.build_element_coverage(results, Selector("#btn"), SelectorType.CSS)

    assert len(result.actions) == 1
    assert result.actions[0].type == ActionType.CLICK


# -------------------------------
# TEST: build
# -------------------------------

def test_build_creates_app_coverage(tmp_path: Path):
    results = CoverageResultList(
        root=[
            CoverageResult(
                app=AppKey("ui-app"),
                selector=Selector("#login"),
                action_type=ActionType.CLICK,
                selector_type=SelectorType.CSS,
            ),
            CoverageResult(
                app=AppKey("ui-app"),
                selector=Selector("#search"),
                action_type=ActionType.HOVER,
                selector_type=SelectorType.CSS,
            ),
        ]
    )

    settings = Settings(apps=[])
    settings.history_file = tmp_path / "history.json"
    history_builder = UICoverageHistoryBuilder(AppHistoryState(), settings)

    builder = UICoverageBuilder(results, history_builder)

    result = builder.build()

    assert isinstance(result, AppCoverage)
    assert len(result.elements) == 2
    assert all(isinstance(el, ElementCoverage) for el in result.elements)
    assert isinstance(result.history, list)
    assert all(isinstance(h, AppHistory) for h in result.history)
    assert result.history[-1].total_actions == results.total_actions
    assert result.history[-1].total_elements == results.total_selectors


def test_build_with_empty_results(tmp_path: Path):
    results = CoverageResultList(root=[])
    settings = Settings(apps=[])
    settings.history_file = tmp_path / "history.json"
    builder = UICoverageBuilder(results, UICoverageHistoryBuilder(AppHistoryState(), settings))

    result = builder.build()

    assert isinstance(result, AppCoverage)
    assert result.elements == []
    assert isinstance(result.history, list)
    assert result.history == []


def test_build_element_coverage_integration(tmp_path: Path):
    results = CoverageResultList(
        root=[
            CoverageResult(
                app=AppKey("ui-app"),
                selector=Selector("#search"),
                action_type=ActionType.TYPE,
                selector_type=SelectorType.CSS,
            ),
            CoverageResult(
                app=AppKey("ui-app"),
                selector=Selector("#search"),
                action_type=ActionType.TYPE,
                selector_type=SelectorType.CSS,
            ),
        ]
    )

    settings = Settings(apps=[])
    settings.history_file = tmp_path / "history.json"
    builder = UICoverageBuilder(results, UICoverageHistoryBuilder(AppHistoryState(), settings))

    app_coverage = builder.build()
    assert isinstance(app_coverage, AppCoverage)

    search_element = next(el for el in app_coverage.elements if el.selector == Selector("#search"))
    assert search_element.actions[0].type == ActionType.TYPE
    assert search_element.actions[0].count == 2
    assert isinstance(search_element.history[-1], ElementHistory)
