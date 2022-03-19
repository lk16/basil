from enum import IntEnum
from parser.exceptions import BaseParseError, BaseParserException
from typing import Set


class MissingNonTerminalTypes(BaseParserException):
    def __init__(self, missing_types: Set[IntEnum]) -> None:
        super().__init__(
            f"NonTerminal rewrite rules has {len(missing_types)} missing types: "
            + ", ".join(type_.name for type_ in missing_types)
        )


class UnexpectedNonTerminalTypes(BaseParserException):
    def __init__(self, unexpected_types: Set[IntEnum]) -> None:
        super().__init__(
            f"NonTerminal rewrite rules contain {len(unexpected_types)} unexpected types: "
            + ", ".join(type_.name for type_ in unexpected_types)
        )


class MissingRootNonTerminalType(BaseParserException):
    def __init__(self) -> None:
        super().__init__(f"NonTerminal rewrite rules does not have a ROOT item")


class ParseError(BaseParseError):
    def __init__(self, filename: str, code: str, offset: int) -> None:
        super().__init__(filename, code, offset)
        # TODO send expected_token_type as argument here?

    def what(self) -> str:
        line_num, col_num = self.get_line_column_numbers()
        line = self.get_line()

        return (
            f"Parse error at {self.filename}:{line_num}:{col_num}\n"
            + f"{line}\n"
            + " " * (col_num - 1)
            + "^"
        )
