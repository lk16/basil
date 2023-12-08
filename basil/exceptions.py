import re
from typing import Any, List, Optional, Set

from basil.models import EndOfFile, Position, Token


class ParseErrorCollector:
    def __init__(self) -> None:
        self.errors: List[ParseError] = []

    def register(self, error: "ParseError") -> None:
        self.errors.append(error)

    def reset(self) -> None:
        self.errors = []

    def get_furthest_error(self) -> "ParseError":
        if not self.errors:
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


class TokenizerException(Exception):
    def __init__(self, position: Position) -> None:
        self.position = position

    def __str__(self) -> str:  # pragma:nocover
        return f"{self.position}: Tokenization failed."


class SyntaxJSONLoadError(Exception):
    def __init__(self, msg: str) -> None:
        self.msg = msg

    def __str__(self) -> str:  # pragma:nocover
        return f"Could not load Syntax JSON: {self.msg}"


class SyntaxJSONParseError(SyntaxJSONLoadError):
    def __init__(self, error: ValueError) -> None:
        self.error = error

    def __str__(self) -> str:  # pragma:nocover
        return f"parse error: {self.error}"


class SyntaxJSONInvalidRoot(SyntaxJSONLoadError):
    def __init__(self) -> None:
        ...

    def __str__(self) -> str:  # pragma:nocover
        return "Expected root to be a JSON object"


class SyntaxJSONUnexpectedFields(SyntaxJSONLoadError):
    def __init__(self, fields: Set[str]) -> None:
        self.fields = fields

    def __str__(self) -> str:  # pragma:nocover
        return "Unexpected fields in JSON root: " + ", ".join(sorted(self.fields))


class SyntaxJSONMissingFields(SyntaxJSONLoadError):
    def __init__(self, fields: Set[str]) -> None:
        self.fields = fields

    def __str__(self) -> str:  # pragma:nocover
        return "Missing fields in JSON root: " + ", ".join(sorted(self.fields))


class SyntaxJSONUnexpectedFieldType(SyntaxJSONLoadError):
    def __init__(self, field: str, expected_type: str, found: Any) -> None:
        self.field = field
        self.expected_type = expected_type
        self.found_type = type(found)

    def __str__(self) -> str:  # pragma:nocover
        return f"Field {self.field} is a {self.found_type}, but should be a {self.expected_type}"


class SyntaxJSONDuplicateTokenType(SyntaxJSONLoadError):
    def __init__(self, token_type: str) -> None:
        self.token_type = token_type

    def __str__(self) -> str:  # pragma:nocover
        return f"Duplicate token type {self.token_type}"


class SyntaxJSONRegexError(SyntaxJSONLoadError):
    def __init__(self, token_type: str, error: re.error) -> None:
        self.token_type = token_type
        self.error = error

    def __str__(self) -> str:  # pragma:nocover
        return f"Failed to compile regex for {self.token_type}: {self.error}"


class SyntaxJSONUnknownFilteredTokenTypes(SyntaxJSONLoadError):
    def __init__(self, token_types: Set[str]) -> None:
        self.token_types = token_types

    def __str__(self) -> str:  # pragma:nocover
        return f"Unknown filtered token type(s): " + ", ".join(sorted(self.token_types))


class SyntaxJSONUnknownRootNode(SyntaxJSONLoadError):
    def __init__(self, root_node_type: str) -> None:
        self.root_node_type = root_node_type

    def __str__(self) -> str:  # pragma:nocover
        return f"Root node type {self.root_node_type} was not found in nodes"


class SyntaxJSONBadTokenTypeName(SyntaxJSONLoadError):
    def __init__(self, name: str) -> None:
        self.name = name

    def __str__(self) -> str:  # pragma:nocover
        return f"Token name {self.name} is not in snake_case"


class SyntaxJSONBadNodeTypeName(SyntaxJSONLoadError):
    def __init__(self, name: str) -> None:
        self.name = name

    def __str__(self) -> str:  # pragma:nocover
        return f"Node name {self.name} is not in TITLE_CASE"


class SyntaxJSONNodeDefinitionParseError(SyntaxJSONLoadError):
    def __init__(self, node_type: str, offset: Optional[int] = None) -> None:
        self.node_type = node_type
        self.offset = offset

    def __str__(self) -> str:  # pragma:nocover
        message = f"Could not create parser from definition of node {self.node_type}"
        if self.offset is not None:
            message += f", error at offset {self.offset}"

        return message


class SyntaxJSONNodeDefinitionUnknownTokenError(SyntaxJSONLoadError):
    def __init__(self, node_type: str, unknown_token_type: str) -> None:
        self.node_type = node_type
        self.unknown_token_type = unknown_token_type

    def __str__(self) -> str:  # pragma:nocover
        return f"In parser definition for node {self.node_type}: Unknown token type {self.unknown_token_type}"


class SyntaxJSONNodeDefinitionUnknownNodeError(SyntaxJSONLoadError):
    def __init__(self, node_type: str, unknown_node_type: str) -> None:
        self.node_type = node_type
        self.unknown_node_type = unknown_node_type

    def __str__(self) -> str:  # pragma:nocover
        return f"In parser definition for node {self.node_type}: Unknown token type {self.unknown_node_type}"


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

    def __str__(self) -> str:
        if isinstance(self.found, EndOfFile):
            return (
                f"{self.found.file}: Unexpected end of file\n"
                + "Expected one of: "
                + ", ".join(sorted(self.expected_token_types))
                + "\n"
            )

        return (
            f"{self.found.position}: Unexpected token type\n"
            + "Expected one of: "
            + ", ".join(sorted(self.expected_token_types))
            + "\n"
            + f"          Found: {self.found.type}\n"
        )
