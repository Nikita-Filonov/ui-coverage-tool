from ui_coverage_tool.config import Settings, get_settings
from ui_coverage_tool.src.tools.types import Selector, AppKey
from ui_coverage_tool.src.tracker.models import SelectorType, ActionType, CoverageResult
from ui_coverage_tool.src.tracker.storage import UICoverageTrackerStorage


class UICoverageTracker:
    def __init__(self, app: str, settings: Settings | None = None):
        self.app = app
        self.settings = settings or get_settings()

        self.storage = UICoverageTrackerStorage(self.settings)

    def track_coverage(
            self,
            selector: str,
            action_type: ActionType,
            selector_type: SelectorType,
    ):
        self.storage.save(
            CoverageResult(
                app=AppKey(self.app),
                selector=Selector(selector),
                action_type=action_type,
                selector_type=selector_type
            )
        )
