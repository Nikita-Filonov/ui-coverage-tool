from datetime import datetime

import pytest

from ui_coverage_tool import ActionType, SelectorType
from ui_coverage_tool.config import Settings
from ui_coverage_tool.src.coverage.models import AppCoverage, ElementCoverage, ActionCoverage
from ui_coverage_tool.src.history.models import AppHistory, ElementHistory, ActionHistory
from ui_coverage_tool.src.reports.models import CoverageReportState
from ui_coverage_tool.src.reports.storage import UIReportsStorage
from ui_coverage_tool.src.tools.types import Selector, AppKey


@pytest.fixture
def coverage_report_state(coverage_history_settings: Settings) -> CoverageReportState:
    app_key = AppKey("ui-app")

    action_history = [ActionHistory(type=ActionType.CLICK, count=3)]
    element_history = [ElementHistory(actions=action_history, created_at=datetime.now())]

    element_coverage = ElementCoverage(
        history=element_history,
        actions=[ActionCoverage(type=ActionType.CLICK, count=3)],
        selector=Selector("#submit"),
        selector_type=SelectorType.CSS,
    )

    app_history = [
        AppHistory(
            actions=action_history,
            created_at=datetime.now(),
            total_actions=10,
            total_elements=5,
        )
    ]
    app_coverage = AppCoverage(history=app_history, elements=[element_coverage])

    report = CoverageReportState.init(coverage_history_settings)
    report.apps_coverage = {app_key: app_coverage}

    return report


@pytest.fixture
def reports_storage(reports_settings: Settings) -> UIReportsStorage:
    return UIReportsStorage(reports_settings)
