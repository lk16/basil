import re
from dataclasses import dataclass
from enum import IntEnum, auto
from pathlib import Path
from typing import Dict, List, Tuple


class TokenizeError(Exception):
    def __init__(self, code: str, offset: int) -> None:
        self.code = code
        self.offset = offset
        super().__init__(f"Tokenizer failed at offset {offset}")


class TokenType(IntEnum):
    BRACKET_CLOSE_AT_LEAST_ONCE = auto()
    BRACKET_CLOSE_OPTIONAL = auto()
    BRACKET_CLOSE_REGULAR = auto()
    BRACKET_CLOSE_REPEAT = auto()
    BRACKET_CLOSE_REPEAT_RANGE = auto()
    BRACKET_OPEN = auto()
    DECORATOR_MARKER = auto()
    DECORATOR_PRUNED = auto()
    DECORATOR_TOKEN = auto()
    EQUALS = auto()
    REGEX_START = auto()
    REPEAT_RANGE_END = auto()
    TOKEN_DEFINITION_END = auto()
    VERTICAL_BAR = auto()
    COMMENT = auto()
    LITERAL_EXPRESSION = auto()
    WHITESPACE = auto()
    INTEGER = auto()
    TOKEN_NAME = auto()


STRINGS: List[Tuple[TokenType, str]] = sorted(
    [
        (TokenType.BRACKET_CLOSE_AT_LEAST_ONCE, ")+"),
        (TokenType.BRACKET_CLOSE_OPTIONAL, ")?"),
        (TokenType.BRACKET_CLOSE_REGULAR, ")"),
        (TokenType.BRACKET_CLOSE_REPEAT, ")*"),
        (TokenType.BRACKET_CLOSE_REPEAT_RANGE, "({"),
        (TokenType.BRACKET_OPEN, "("),
        (TokenType.DECORATOR_MARKER, "@"),
        (TokenType.DECORATOR_PRUNED, "pruned"),
        (TokenType.DECORATOR_TOKEN, "terminal"),
        (TokenType.EQUALS, "="),
        (TokenType.REGEX_START, "regex("),
        (TokenType.REPEAT_RANGE_END, ",...}"),
        (TokenType.TOKEN_DEFINITION_END, "."),
        (TokenType.VERTICAL_BAR, "|"),
    ],
    key=lambda x: -len(x[1]),
)

REGEXES: Dict[TokenType, re.Pattern[str]] = {
    TokenType.COMMENT: re.compile("^//[^\n]*"),
    TokenType.LITERAL_EXPRESSION: re.compile('^"([^\\\\]|\\\\("|n|\\\\))*?"'),
    TokenType.WHITESPACE: re.compile("^[ \n]*"),
    TokenType.INTEGER: re.compile("^[0-9]+"),
    TokenType.TOKEN_NAME: re.compile("^[A-Z_]+"),
}


@dataclass
class Token:
    type: TokenType
    offset: int
    length: int


def main() -> None:
    code = Path("parser/grammar/grammar.txt").read_text()
    tokens = get_tokens(code)

    for token in tokens:
        print(token)


def get_token(code: str, offset: int) -> Token:
    for token_type, string in STRINGS:
        if code[offset:].startswith(string):
            return Token(token_type, offset, len(string))

    for token_type, regex in REGEXES.items():
        match = regex.match(code[offset:])
        if match and len(match.group(0)) > 0:
            return Token(token_type, offset, len(match.group(0)))

    raise TokenizeError(code, offset)


def get_tokens(code: str) -> List[Token]:
    offset = 0
    tokens: List[Token] = []

    while offset < len(code):
        try:
            token = get_token(code, offset)
        except TokenizeError as e:
            # TODO handle
            raise e

        tokens.append(token)
        offset += token.length

    return tokens
