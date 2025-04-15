from enum import Enum


class SelectorType(str, Enum):
    CSS = "CSS"
    XPATH = "XPATH"

    def __str__(self) -> str:
        return str(self.value)
