from ui_coverage_tool.config import Settings
from ui_coverage_tool.src.history.models import CoverageHistoryState, AppHistoryState
from ui_coverage_tool.src.history.selector import build_selector_key
from ui_coverage_tool.src.reports.models import CoverageReportState
from ui_coverage_tool.src.tools.logger import get_logger

logger = get_logger("UI_COVERAGE_HISTORY_STORAGE")


class UICoverageHistoryStorage:
    def __init__(self, settings: Settings):
        self.settings = settings

    def load(self):
        history_file = self.settings.history_file

        if not history_file:
            logger.debug("No history file path provided, returning empty history state")
            return CoverageHistoryState()

        if not history_file.exists():
            logger.debug("History file not found, returning empty history state")
            return CoverageHistoryState()

        try:
            logger.info(f"Loading history from file: {history_file}")
            return CoverageHistoryState.model_validate_json(history_file.read_text())
        except Exception as error:
            logger.error(f"Error loading history from file {history_file}: {error}")
            return CoverageHistoryState()

    def save(self, state: CoverageHistoryState):
        history_file = self.settings.history_file

        if not history_file:
            logger.debug("History file path is not defined, skipping history save")
            return

        try:
            history_file.touch(exist_ok=True)
            history_file.write_text(state.model_dump_json(by_alias=True))
            logger.info(f"History state saved to file: {history_file}")
        except Exception as error:
            logger.error(f"Error saving history to file {history_file}: {error}")

    def save_from_report(self, report: CoverageReportState):
        state = CoverageHistoryState(
            apps={
                app.key: AppHistoryState(
                    total=report.apps_coverage[app.key].history,
                    elements={
                        build_selector_key(element.selector, element.selector_type): element.history
                        for element in report.apps_coverage[app.key].elements
                    }
                )
                for app in self.settings.apps
            }
        )
        self.save(state)
