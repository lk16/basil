from enum import IntEnum
from typing import Set


class MissingNonTerminalTypes(Exception):
    def __init__(self, missing_types: Set[IntEnum]) -> None:
        super().__init__(
            f"NonTerminal rewrite rules has {len(missing_types)} missing types: "
            + ", ".join(type_.name for type_ in missing_types)
        )


class UnexpectedNonTerminalTypes(Exception):
    def __init__(self, unexpected_types: Set[IntEnum]) -> None:
        super().__init__(
            f"NonTerminal rewrite rules contain {len(unexpected_types)} unexpected types: "
            + ", ".join(type_.name for type_ in unexpected_types)
        )


class MissingRootNonTerminalType(Exception):
    def __init__(self) -> None:
        super().__init__(f"NonTerminal rewrite rules does not have a ROOT item")
