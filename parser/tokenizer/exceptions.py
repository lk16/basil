from enum import IntEnum
from typing import Set


class MissingTerminalTypes(Exception):
    def __init__(self, missing_types: Set[IntEnum]) -> None:
        super().__init__(
            f"Terminal rewrite rules has {len(missing_types)} missing types: "
            + ", ".join(type_.name for type_ in missing_types)
        )


class UnexpectedTerminalTypes(Exception):
    def __init__(self, unexpected_types: Set[IntEnum]) -> None:
        super().__init__(
            f"Terminal rewrite rules contain {len(unexpected_types)} unexpected types: "
            + ", ".join(type_.name for type_ in unexpected_types)
        )
