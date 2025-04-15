from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict

from ui_coverage_tool.src.tools.actions import ActionType
from ui_coverage_tool.src.tools.types import AppKey


class ActionHistory(BaseModel):
    type: ActionType
    count: int


class ElementHistory(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    actions: list[ActionHistory]
    created_at: datetime = Field(alias="createdAt")


class TotalAppHistory(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    actions: list[ActionHistory]
    created_at: datetime = Field(alias="createdAt")
    total_actions: int = Field(alias="totalActions")
    total_elements: int = Field(alias="totalElements")


class AppHistory(BaseModel):
    total: list[TotalAppHistory]
    elements: dict[str, list[ElementHistory]]


class CoverageHistoryState(BaseModel):
    apps: dict[AppKey, AppHistory] = Field(default_factory=dict)
