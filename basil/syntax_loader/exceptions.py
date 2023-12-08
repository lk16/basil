import re
from typing import Any, Optional, Set


class LoadError(ValueError):
    def __init__(self) -> None:
        ...


class ParseError(LoadError):
    def __init__(self, error: ValueError) -> None:
        self.error = error

    def __str__(self) -> str:  # pragma:nocover
        return f"parse error: {self.error}"


class InvalidRoot(LoadError):
    def __str__(self) -> str:  # pragma:nocover
        return "Expected root to be a JSON object"


class UnexpectedFields(LoadError):
    def __init__(self, fields: Set[str]) -> None:
        self.fields = fields

    def __str__(self) -> str:  # pragma:nocover
        return "Unexpected fields in JSON root: " + ", ".join(sorted(self.fields))


class MissingFields(LoadError):
    def __init__(self, fields: Set[str]) -> None:
        self.fields = fields

    def __str__(self) -> str:  # pragma:nocover
        return "Missing fields in JSON root: " + ", ".join(sorted(self.fields))


class UnexpectedFieldType(LoadError):
    def __init__(self, field: str, expected_type: str, found: Any) -> None:
        self.field = field
        self.expected_type = expected_type
        self.found_type = type(found)

    def __str__(self) -> str:  # pragma:nocover
        return f"Field {self.field} is a {self.found_type}, but should be a {self.expected_type}"


# TODO move this class and its subclasses out
class DuplicateTokenType(LoadError):
    def __init__(self, token_type: str) -> None:
        self.token_type = token_type

    def __str__(self) -> str:  # pragma:nocover
        return f"Duplicate token type {self.token_type}"


class RegexError(LoadError):
    def __init__(self, token_type: str, error: re.error) -> None:
        self.token_type = token_type
        self.error = error

    def __str__(self) -> str:  # pragma:nocover
        return f"Failed to compile regex for {self.token_type}: {self.error}"


class UnknownFilteredTokenTypes(LoadError):
    def __init__(self, token_types: Set[str]) -> None:
        self.token_types = token_types

    def __str__(self) -> str:  # pragma:nocover
        return f"Unknown filtered token type(s): " + ", ".join(sorted(self.token_types))


class UnknownRootNode(LoadError):
    def __init__(self, root_node_type: str) -> None:
        self.root_node_type = root_node_type

    def __str__(self) -> str:  # pragma:nocover
        return f"Root node type {self.root_node_type} was not found in nodes"


class BadTokenTypeName(LoadError):
    def __init__(self, name: str) -> None:
        self.name = name

    def __str__(self) -> str:  # pragma:nocover
        return f"Token name {self.name} is not in snake_case"


class BadNodeTypeName(LoadError):
    def __init__(self, name: str) -> None:
        self.name = name

    def __str__(self) -> str:  # pragma:nocover
        return f"Node name {self.name} is not in TITLE_CASE"


class NodeDefinitionParseError(LoadError):
    def __init__(self, node_type: str, offset: Optional[int] = None) -> None:
        self.node_type = node_type
        self.offset = offset

    def __str__(self) -> str:  # pragma:nocover
        message = f"Could not create parser from definition of node {self.node_type}"
        if self.offset is not None:
            message += f", error at offset {self.offset}"

        return message


class NodeDefinitionUnknownTokenError(LoadError):
    def __init__(self, node_type: str, unknown_token_type: str) -> None:
        self.node_type = node_type
        self.unknown_token_type = unknown_token_type

    def __str__(self) -> str:  # pragma:nocover
        return f"In parser definition for node {self.node_type}: Unknown token type {self.unknown_token_type}"


class NodeDefinitionUnknownNodeError(LoadError):
    def __init__(self, node_type: str, unknown_node_type: str) -> None:
        self.node_type = node_type
        self.unknown_node_type = unknown_node_type

    def __str__(self) -> str:  # pragma:nocover
        return f"In parser definition for node {self.node_type}: Unknown token type {self.unknown_node_type}"
