from enum import IntEnum
from typing import List, Optional, Tuple


class BaseParseError(Exception):
    def __init__(self, filename: str, code: str, offset: int) -> None:
        self.filename = filename
        self.code = code
        self.offset = offset

        if type(self) == BaseParseError:  # pragma: nocover
            what = "Don't use BaseParseError directly!"
        else:
            what = self.what()

        super().__init__(what)

    def get_line_column_numbers(self) -> Tuple[int, int]:
        before_offset = self.code[: self.offset]
        line_num = 1 + before_offset.count("\n")
        prev_newline_offset = before_offset.rfind("\n")
        col_num = self.offset - prev_newline_offset
        return line_num, col_num

    def get_line(self) -> str:
        prev_newline = self.code.rfind("\n", 0, self.offset)

        next_newline = self.code.find("\n", self.offset)
        if next_newline == -1:
            next_newline = len(self.code)

        return self.code[prev_newline + 1 : next_newline]

    def what(self) -> str:  # pragma: nocover
        return ""


class InternalParseError(Exception):
    def __init__(self, offset: int, token_type: Optional[IntEnum]) -> None:
        self.token_offset = offset
        self.token_type = token_type
        super().__init__()


class ParseError(Exception):
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
