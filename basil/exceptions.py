from typing import Set

from basil.models import EndOfFile, Position, Token


class TokenizerException(Exception):
    def __init__(self, position: Position) -> None:
        self.position = position

    def __str__(self) -> str:  # pragma:nocover
        return f"{self.position}: Tokenization failed."


class ParseError(Exception):
    def __init__(
        self,
        offset: int,
        found: Token | EndOfFile,
        expected_token_types: Set[str],
    ) -> None:
        self.found = found
        self.expected_token_types = expected_token_types
        self.offset = offset

    def __str__(self) -> str:  # pragma:nocover
        if isinstance(self.found, EndOfFile):
            return (
                f"{self.found.file}: Unexpected end of file\n"
                + "Expected one of: "
                + ", ".join(sorted(self.expected_token_types))
            )

        return (
            f"{self.found.position}: Unexpected token type\n"
            + "Expected one of: "
            + ", ".join(sorted(self.expected_token_types))
            + "\n"
            + f"          Found: {self.found.type}"
        )
