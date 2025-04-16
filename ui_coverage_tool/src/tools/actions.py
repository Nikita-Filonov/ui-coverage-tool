from enum import Enum
from typing import Self


class ActionType(str, Enum):
    FILL = "FILL"
    TYPE = "TYPE"
    TEXT = "TEXT"
    VALUE = "VALUE"
    CLICK = "CLICK"
    HOVER = "HOVER"
    SELECT = "SELECT"
    HIDDEN = "HIDDEN"
    VISIBLE = "VISIBLE"
    CHECKED = "CHECKED"
    ENABLED = "ENABLED"
    DISABLED = "DISABLED"
    UNCHECKED = "UNCHECKED"

    @classmethod
    def to_list(cls) -> list[Self]:
        return list(cls)
