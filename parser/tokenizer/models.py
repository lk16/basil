import re
from dataclasses import dataclass
from enum import IntEnum


@dataclass
class Token:
    type: IntEnum
    offset: int
    length: int

    def value(self, code: str) -> str:  # pragma: nocover
        # For debugging
        return code[self.offset : self.offset + self.length]


@dataclass
class TokenDescriptor:
    token_type: IntEnum


@dataclass
class Regex(TokenDescriptor):
    def __init__(self, token_type: IntEnum, regex: str) -> None:
        self.token_type = token_type
        self.value = re.compile(regex)

    value: re.Pattern[str]


@dataclass
class Literal(TokenDescriptor):
    value: str
