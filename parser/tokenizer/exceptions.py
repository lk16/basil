from enum import IntEnum
from parser.exceptions import BaseParseError, EqualitySupportingException
from typing import Set


class MissingTerminalTypes(EqualitySupportingException):
    def __init__(self, missing_types: Set[IntEnum]) -> None:
        super().__init__(
            f"Terminal rewrite rules has {len(missing_types)} missing types: "
            + ", ".join(type_.name for type_ in missing_types)
        )


class UnexpectedTerminalTypes(EqualitySupportingException):
    def __init__(self, unexpected_types: Set[IntEnum]) -> None:
        super().__init__(
            f"Terminal rewrite rules contain {len(unexpected_types)} unexpected types: "
            + ", ".join(type_.name for type_ in unexpected_types)
        )


class TokenizerError(BaseParseError):
    def __init__(self, filename: str, code: str, offset: int) -> None:
        super().__init__(filename, code, offset)
        # TODO send expected_token_types as argument here?

    def what(self) -> str:
        line_num, col_num = self.get_line_column_numbers()
        line = self.get_line()

        return (
            f"Tokenize error at {self.filename}:{line_num}:{col_num}\n"
            + f"{line}\n"
            + " " * (col_num - 1)
            + "^"
        )
