from typing import List, Set

from basil.exceptions import ParseError


class ParseErrorCollector:
    def __init__(self) -> None:
        self.errors: List[ParseError] = []

    def register(self, error: "ParseError") -> None:
        # We only keep the furthest errors

        if not self.errors:
            self.errors = [error]

        max_offset = self.errors[0].offset

        if error.offset > max_offset:
            self.errors = [error]

        if error.offset == max_offset:
            self.errors.append(error)

    def reset(self) -> None:
        self.errors = []

    def get_furthest_error(self) -> "ParseError":
        if not self.errors:  # pragma:nocover
            raise ValueError("No errors were collected.")

        offset = self.errors[0].offset
        found = self.errors[0].found

        expected_token_types: Set[str] = set()

        for error in self.errors:
            expected_token_types.update(error.expected_token_types)

        return ParseError(offset, found, expected_token_types)
