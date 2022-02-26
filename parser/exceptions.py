from enum import IntEnum
from typing import List, Optional, Set


class InternalParseError(Exception):
    def __init__(self, offset: int, symbol_type: Optional[IntEnum]) -> None:
        self.offset = offset
        self.symbol_type = symbol_type
        super().__init__()


class ParseError(Exception):
    """
    Indicates parsing failed.
    """

    def __init__(
        self,
        line_number: int,
        column_number: int,
        line: str,
        expected_symbol_types: List[IntEnum],
    ) -> None:
        self.line_number = line_number
        self.column_number = column_number
        self.line = line
        self.expected_symbol_types = expected_symbol_types

        # TODO make this show some human readable parse error message
        super().__init__()


class UnhandledSymbolType(Exception):
    """
    Indicates rewrite rules misses an entry.
    """

    def __init__(self, symbol_type: IntEnum) -> None:
        super().__init__(f"Unhandled symbol type {symbol_type.name}")


class UnexpectedSymbols(Exception):
    """
    Indicates rewrite rules has an unexpected entry.
    """

    def __init__(self, unexpected_keys: Set[IntEnum]) -> None:
        super().__init__(
            f"Rewrite rules contain {len(unexpected_keys)} items, with keys: "
            + ", ".join(key.__repr__() for key in unexpected_keys)
        )
