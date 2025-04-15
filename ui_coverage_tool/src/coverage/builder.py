from ui_coverage_tool.src.coverage.models import AppCoverage, ElementCoverage, ActionCoverage
from ui_coverage_tool.src.history.builder import UICoverageHistoryBuilder
from ui_coverage_tool.src.history.models import ActionHistory
from ui_coverage_tool.src.tools.actions import ActionType
from ui_coverage_tool.src.tools.selector import SelectorType
from ui_coverage_tool.src.tools.types import Selector
from ui_coverage_tool.src.tracker.models import CoverageResultList


class UICoverageBuilder:
    def __init__(self, results_list: CoverageResultList, history_builder: UICoverageHistoryBuilder):
        self.results_list = results_list
        self.history_builder = history_builder

    def build_element_coverage(
            self,
            results: CoverageResultList,
            selector: Selector,
            selector_type: SelectorType
    ) -> ElementCoverage:
        actions = [
            ActionCoverage(type=action, count=results.count_action(action))
            for action in ActionType.to_list()
            if results.count_action(action) > 0
        ]

        return ElementCoverage(
            history=self.history_builder.get_element_history(
                actions=[ActionHistory(type=action.type, count=action.count) for action in actions],
                selector=selector,
                selector_type=selector_type
            ),
            actions=actions,
            selector=selector,
            selector_type=selector_type,
        )

    def build(self) -> AppCoverage:
        return AppCoverage(
            history=self.history_builder.get_app_history(
                actions=[
                    ActionHistory(type=action, count=results.total_actions)
                    for action, results in self.results_list.grouped_by_action.items()
                    if results.total_actions > 0
                ],
                total_actions=self.results_list.total_actions,
                total_elements=self.results_list.total_selectors
            ),
            elements=[
                self.build_element_coverage(results, selector, selector_type)
                for (selector, selector_type), results in self.results_list.grouped_by_selector.items()
            ],
        )
