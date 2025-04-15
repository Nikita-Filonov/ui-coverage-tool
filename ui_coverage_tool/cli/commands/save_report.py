from ui_coverage_tool.config import get_settings
from ui_coverage_tool.src.coverage.builder import UICoverageBuilder
from ui_coverage_tool.src.history.builder import UICoverageHistoryBuilder
from ui_coverage_tool.src.history.models import AppHistoryState
from ui_coverage_tool.src.history.storage import UICoverageHistoryStorage
from ui_coverage_tool.src.reports.models import CoverageReportState
from ui_coverage_tool.src.reports.storage import UIReportsStorage
from ui_coverage_tool.src.tools.logger import get_logger
from ui_coverage_tool.src.tracker.storage import UICoverageTrackerStorage

logger = get_logger("SAVE_REPORT")


def save_report_command():
    logger.info("Starting to save the report")

    settings = get_settings()

    reports_storage = UIReportsStorage(settings=settings)
    tracker_storage = UICoverageTrackerStorage(settings=settings)
    history_storage = UICoverageHistoryStorage(settings=settings)

    report_state = CoverageReportState.init(settings)
    history_state = history_storage.load()
    tracker_state = tracker_storage.load()
    for app in settings.apps:
        results_list = tracker_state.filter(app=app.key)

        coverage_builder = UICoverageBuilder(
            results_list=results_list,
            history_builder=UICoverageHistoryBuilder(
                history=history_state.apps.get(app.key, AppHistoryState()),
                settings=settings
            )
        )
        report_state.apps_coverage[app.key] = coverage_builder.build()

    history_storage.save_from_report(report_state)
    reports_storage.save_json_report(report_state)
    reports_storage.save_html_report(report_state)

    logger.info("Report saving process completed")
