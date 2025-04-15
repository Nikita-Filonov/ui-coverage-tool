from ui_coverage_tool.src.tools.selector import SelectorType
from ui_coverage_tool.src.tools.types import Selector, SelectorKey


def build_selector_key(selector: Selector, selector_type: SelectorType) -> SelectorKey:
    return SelectorKey(f'{selector_type}_{selector}')
