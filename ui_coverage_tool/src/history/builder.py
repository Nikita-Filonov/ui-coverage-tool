from datetime import datetime
from typing import TypeVar, Callable

from ui_coverage_tool.config import Settings
from ui_coverage_tool.src.history.models import ElementHistory, AppHistoryState, ActionHistory, AppHistory
from ui_coverage_tool.src.history.selector import build_selector_key
from ui_coverage_tool.src.tools.selector import SelectorType
from ui_coverage_tool.src.tools.types import Selector

T = TypeVar('T')


class UICoverageHistoryBuilder:
    def __init__(self, history: AppHistoryState, settings: Settings):
        self.history = history
        self.settings = settings
        self.created_at = datetime.now()

    def build_app_history(
            self,
            actions: list[ActionHistory],
            total_actions: int,
            total_elements: int
    ) -> AppHistory:
        return AppHistory(
            actions=actions,
            created_at=self.created_at,
            total_actions=total_actions,
            total_elements=total_elements
        )

    def build_element_history(self, actions: list[ActionHistory]) -> ElementHistory:
        return ElementHistory(created_at=self.created_at, actions=actions)

    def append_history(self, history: list[T], build_func: Callable[[], T]) -> list[T]:
        if not self.settings.history_file:
            return []

        new_item = build_func()
        if not new_item.actions:
            return history

        combined = [*history, new_item]
        combined.sort(key=lambda r: r.created_at)
        return combined[-self.settings.history_retention_limit:]

    def get_app_history(
            self,
            actions: list[ActionHistory],
            total_actions: int,
            total_elements: int
    ) -> list[AppHistory]:
        return self.append_history(
            self.history.total,
            lambda: self.build_app_history(
                actions=actions,
                total_actions=total_actions,
                total_elements=total_elements
            )
        )

    def get_element_history(
            self,
            actions: list[ActionHistory],
            selector: Selector,
            selector_type: SelectorType
    ) -> list[ElementHistory]:
        key = build_selector_key(selector, selector_type)
        history = self.history.elements.get(key, [])
        return self.append_history(history, lambda: self.build_element_history(actions))
