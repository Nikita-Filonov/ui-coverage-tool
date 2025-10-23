from ui_coverage_tool.src.tools.actions import ActionType
from ui_coverage_tool.src.tools.selector import SelectorType
from ui_coverage_tool.src.tools.types import Selector, AppKey
from ui_coverage_tool.src.tracker.models import CoverageResultList


# -------------------------------
# TEST: filter
# -------------------------------

def test_filter_by_app(coverage_result_list: CoverageResultList):
    filtered = coverage_result_list.filter(AppKey("ui-app"))
    assert isinstance(filtered, CoverageResultList)
    assert len(filtered.root) == 2
    assert all(r.app == "ui-app" for r in filtered.root)


def test_filter_none_returns_all(coverage_result_list: CoverageResultList):
    filtered = coverage_result_list.filter()
    assert len(filtered.root) == len(coverage_result_list.root)


def test_filter_case_insensitive(coverage_result_list: CoverageResultList):
    filtered = coverage_result_list.filter(AppKey("UI-APP"))
    assert len(filtered.root) == 2
    assert all(r.app == "ui-app" for r in filtered.root)


# -------------------------------
# TEST: grouped_by_action
# -------------------------------

def test_grouped_by_action_returns_dict(coverage_result_list: CoverageResultList):
    grouped = coverage_result_list.grouped_by_action
    assert isinstance(grouped, dict)
    assert ActionType.CLICK in grouped
    assert isinstance(grouped[ActionType.CLICK], CoverageResultList)
    assert all(r.action_type == ActionType.CLICK for r in grouped[ActionType.CLICK].root)


def test_grouped_by_action_multiple_groups(coverage_result_list: CoverageResultList):
    grouped = coverage_result_list.grouped_by_action
    assert set(grouped.keys()) == {ActionType.CLICK, ActionType.HOVER}


# -------------------------------
# TEST: grouped_by_selector
# -------------------------------

def test_grouped_by_selector_returns_dict(coverage_result_list: CoverageResultList):
    grouped = coverage_result_list.grouped_by_selector
    assert isinstance(grouped, dict)
    assert all(isinstance(k, tuple) for k in grouped.keys())
    assert any(r.selector == "#login" for lst in grouped.values() for r in lst.root)


def test_grouped_by_selector_combines_same_selector(coverage_result_list: CoverageResultList):
    grouped = coverage_result_list.grouped_by_selector
    key = (Selector("#login"), SelectorType.CSS)
    assert key in grouped
    assert isinstance(grouped[key], CoverageResultList)
    assert len(grouped[key].root) == 2


# -------------------------------
# TEST: total_actions & total_selectors
# -------------------------------

def test_total_actions_and_total_selectors(coverage_result_list: CoverageResultList):
    assert coverage_result_list.total_actions == 3
    assert coverage_result_list.total_selectors == len(coverage_result_list.grouped_by_selector)


# -------------------------------
# TEST: count_action
# -------------------------------

def test_count_action_returns_correct_values(coverage_result_list: CoverageResultList):
    assert coverage_result_list.count_action(ActionType.CLICK) == 2
    assert coverage_result_list.count_action(ActionType.HOVER) == 1


def test_count_action_returns_zero_for_missing_type(coverage_result_list: CoverageResultList):
    assert coverage_result_list.count_action(ActionType.VISIBLE) == 0
