import pytest

from ui_coverage_tool.src.history.selector import build_selector_key
from ui_coverage_tool.src.tools.selector import SelectorType
from ui_coverage_tool.src.tools.types import Selector


# -------------------------------
# TEST: build_selector_key
# -------------------------------

@pytest.mark.parametrize(
    "selector_type,selector,expected",
    [
        (SelectorType.CSS, Selector("#login-btn"), "CSS_#login-btn"),
        (SelectorType.XPATH, Selector("//button[@id='submit']"), "XPATH_//button[@id='submit']"),
    ],
)
def test_build_selector_key_various_types(
        selector_type: SelectorType,
        selector: Selector,
        expected: str,
) -> None:
    result = build_selector_key(selector, selector_type)
    assert result == expected
