from typing import List, Set

from basil.exceptions import ParseError


class ParseErrorCollector:
    def __init__(self) -> None:
        self.errors: List[ParseError] = []

    def register(self, error: "ParseError") -> None:
        self.errors.append(error)

    def reset(self) -> None:
        self.errors = []

    def get_furthest_error(self) -> "ParseError":
        if not self.errors:  # pragma:nocover
            raise ValueError("No errors were collected.")

        max_offset = -1
        furthest_errors: List[ParseError] = []

        for error in self.errors:
            if error.offset > max_offset:
                max_offset = error.offset
                furthest_errors = [error]
            if error.offset == max_offset:
                furthest_errors.append(error)

        furthest_token = furthest_errors[0].found

        expected_token_types: Set[str] = set()

        for error in furthest_errors:
            expected_token_types.update(error.expected_token_types)

        return ParseError(max_offset, furthest_token, expected_token_types)
