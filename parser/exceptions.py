from typing import Tuple


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
