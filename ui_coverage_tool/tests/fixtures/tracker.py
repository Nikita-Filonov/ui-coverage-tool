import pytest

from ui_coverage_tool.config import Settings
from ui_coverage_tool.src.tools.actions import ActionType
from ui_coverage_tool.src.tools.selector import SelectorType
from ui_coverage_tool.src.tools.types import AppKey, Selector
from ui_coverage_tool.src.tracker.models import CoverageResult, CoverageResultList
from ui_coverage_tool.src.tracker.storage import UICoverageTrackerStorage


@pytest.fixture
def coverage_result() -> CoverageResult:
    return CoverageResult(
        app=AppKey("ui-app"),
        selector=Selector("#submit"),
        action_type=ActionType.CLICK,
        selector_type=SelectorType.CSS,
    )


@pytest.fixture
def coverage_results() -> list[CoverageResult]:
    return [
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
        CoverageResult(
            app=AppKey("other-app"),
            selector=Selector("#login"),
            action_type=ActionType.CLICK,
            selector_type=SelectorType.CSS,
        ),
    ]


@pytest.fixture
def coverage_result_list(coverage_results: list[CoverageResult]) -> CoverageResultList:
    return CoverageResultList(root=coverage_results)


@pytest.fixture
def coverage_tracker_storage(settings: Settings) -> UICoverageTrackerStorage:
    return UICoverageTrackerStorage(settings)
