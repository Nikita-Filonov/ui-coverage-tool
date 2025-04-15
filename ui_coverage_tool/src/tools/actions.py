from enum import Enum
from typing import Self


class ActionType(str, Enum):
    FILL = "FILL"
    CLICK = "CLICK"
    ASSERT_VISIBLE = "ASSERT_VISIBLE"
    ASSERT_HAVE_TEXT = "ASSERT_HAVE_TEXT"

    @classmethod
    def to_list(cls) -> list[Self]:
        return list(cls)
