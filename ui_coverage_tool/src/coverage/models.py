from pydantic import BaseModel, Field, ConfigDict

from ui_coverage_tool.src.history.models import ElementHistory, AppHistory
from ui_coverage_tool.src.tools.actions import ActionType
from ui_coverage_tool.src.tools.selector import SelectorType
from ui_coverage_tool.src.tools.types import Selector


class ActionCoverage(BaseModel):
    type: ActionType
    count: int


class ElementCoverage(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    history: list[ElementHistory]
    actions: list[ActionCoverage]
    selector: Selector
    selector_type: SelectorType = Field(alias="selectorType")


class AppCoverage(BaseModel):
    history: list[AppHistory]
    elements: list[ElementCoverage]
