from parser.parser.exceptions import ParseError


class UnhandledTokenException(ParseError):
    def __init__(self, filename: str, code: str, offset: int, token_name: str) -> None:
        super().__init__(filename, code, offset)
        self.token_name = token_name

    def what(self) -> str:
        line_num, col_num = self.get_line_column_numbers()
        line = self.get_line()

        return (
            f"Unknown terminal or non-terminal at {self.filename}:{line_num}:{col_num}\n"
            + f"{line}\n"
            + " " * (col_num - 1)
            + "^"
        )
