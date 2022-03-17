from enum import IntEnum
from typing import List, Optional, Set


class InternalParseError(Exception):
    def __init__(self, offset: int, token_type: Optional[IntEnum]) -> None:
        self.token_offset = offset
        self.token_type = token_type
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
        expected_token_types: List[IntEnum],
    ) -> None:
        self.line_number = line_number
        self.column_number = column_number
        self.line = line
        self.expected_token_types = expected_token_types

        # TODO pass source file path
        source_file = "<source_file>"

        msg = (
            f"Parse error at {source_file}:{line_number}:{column_number}\n"
            + f"{self.line}\n"
            + " " * (self.column_number - 1)
            + "^"
        )

        super().__init__(msg)


class InternalTokenizeError(Exception):
    def __init__(self, offset: int, token_type: Optional[IntEnum]) -> None:
        self.token_offset = offset
        self.token_type = token_type
        super().__init__()


class UnhandledTokenType(Exception):
    """
    Indicates rewrite rules misses an entry.
    """

    def __init__(self, token_type: IntEnum) -> None:
        super().__init__(f"Unhandled token type {token_type.name}")


class UnexpectedTokenType(Exception):
    """
    Indicates rewrite rules has an unexpected entry.
    """

    def __init__(self, unexpected_keys: Set[IntEnum]) -> None:
        super().__init__(
            f"Rewrite rules contain {len(unexpected_keys)} items, with keys: "
            + ", ".join(key.__repr__() for key in unexpected_keys)
        )
