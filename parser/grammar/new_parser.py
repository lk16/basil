import re
from dataclasses import dataclass
from enum import IntEnum, auto
from pathlib import Path
from typing import Any, Dict, List, Set, Tuple


class TokenizeError(Exception):
    def __init__(self, code: str, offset: int) -> None:
        self.code = code
        self.offset = offset
        super().__init__(f"Tokenizer failed at offset {offset}")


class TokenType(IntEnum):
    BRACKET_CLOSE_AT_LEAST_ONCE = auto()
    BRACKET_CLOSE_OPTIONAL = auto()
    BRACKET_CLOSE = auto()
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
        (TokenType.BRACKET_CLOSE, ")"),
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

PRUNED_TOKEN_TYPES: Set[TokenType] = {
    TokenType.COMMENT,
    TokenType.WHITESPACE,
}


@dataclass
class Token:
    type: TokenType
    offset: int
    length: int

    def value(self, code: str) -> str:
        return code[self.offset : self.offset + self.length]


@dataclass
class Tree:
    ...


@dataclass
class Terminal(Tree):
    token_type: TokenType


@dataclass
class NonTerminal(Tree):
    name: str


@dataclass
class Concatenation(Tree):
    children: List[Tree]


@dataclass
class Conjunction(Tree):
    children: List[Tree]


@dataclass
class Repeat(Tree):
    child: Tree


@dataclass
class AtLeastOnce(Tree):
    child: Tree


@dataclass
class RuleOptional(Tree):
    child: Tree


NON_TERMINALS: Dict[str, Tree] = {
    "ROOT": Repeat(NonTerminal("TOKEN_DEFINITION")),
    "TOKEN_DEFINITION": Concatenation(
        [
            Repeat(NonTerminal("DECORATOR")),
            NonTerminal("TOKEN_NAME"),
            Terminal(TokenType.EQUALS),
            NonTerminal("TOKEN_COMPOUND_EXPRESSION"),
            NonTerminal("TOKEN_DEFINITION_END"),
        ]
    ),
    "DECORATOR": Concatenation(
        [Terminal(TokenType.DECORATOR_MARKER), NonTerminal("DECORATOR_VALUE")]
    ),
    "DECORATOR_VALUE": Conjunction(
        [Terminal(TokenType.DECORATOR_PRUNED), Terminal(TokenType.DECORATOR_TOKEN)]
    ),
    "CONCATENATION_EXPRESSION": Concatenation(
        [
            Conjunction(
                [
                    NonTerminal("TOKEN_EXPRESSION"),
                    NonTerminal("CONJUNCTION_EXRPESSION"),
                    NonTerminal("BRACKET_EXPRESSION"),
                ]
            ),
            AtLeastOnce(NonTerminal("TOKEN_COMPOUND_EXPRESSION")),
        ]
    ),
    "BRACKET_EXPRESSION": Concatenation(
        [
            Terminal(TokenType.BRACKET_OPEN),
            NonTerminal("TOKEN_COMPOUND_EXPRESSION"),
            NonTerminal("BRACKET_EXPRESSION_END"),
        ]
    ),
    "BRACKET_EXPRESSION_END": Conjunction(
        [
            Terminal(TokenType.BRACKET_CLOSE),
            Terminal(TokenType.BRACKET_CLOSE_REPEAT),
            Terminal(TokenType.BRACKET_CLOSE_AT_LEAST_ONCE),
            Terminal(TokenType.BRACKET_CLOSE_OPTIONAL),
        ]
    ),
    "TOKEN_COMPOUND_EXPRESSION": Conjunction(
        [
            NonTerminal("TOKEN_EXPRESSION"),
            NonTerminal("CONCATENATION_EXPRESSION"),
            NonTerminal("CONJUNCTION_EXPRESSION"),
            NonTerminal("BRACKET_EXPRESSION"),
        ]
    ),
    "CONJUNCTION_EXPRESSION": Concatenation(
        [
            NonTerminal("TOKEN_COMPOUND_EXPRESSION"),
            Terminal(TokenType.VERTICAL_BAR),
            NonTerminal("TOKEN_COMPOUND_EXPRESSION"),
        ]
    ),
    "TOKEN_EXPRESSION": Conjunction(
        [
            NonTerminal("LITERAL_EXPRESSION"),
            NonTerminal("TOKEN_NAME"),
            NonTerminal("REGEX_EXPRESSION"),
        ]
    ),
    "REGEX_EXPRESSION": Concatenation(
        [
            Terminal(TokenType.REGEX_START),
            NonTerminal("LITERAL_EXPRESSION"),
            Terminal(TokenType.BRACKET_CLOSE),
        ]
    ),
}


def main() -> None:
    code = Path("parser/grammar/grammar.txt").read_text()
    pruned_token_types = PRUNED_TOKEN_TYPES
    tokens = get_tokens(code, pruned_token_types)
    non_terminals = NON_TERMINALS
    grammar_rules = get_grammar_rules(non_terminals)

    _ = grammar_rules
    _ = tokens


def get_token(code: str, offset: int) -> Token:
    for token_type, string in STRINGS:
        if code[offset:].startswith(string):
            return Token(token_type, offset, len(string))

    for token_type, regex in REGEXES.items():
        match = regex.match(code[offset:])
        if match and len(match.group(0)) > 0:
            return Token(token_type, offset, len(match.group(0)))

    raise TokenizeError(code, offset)


def get_tokens(code: str, pruned_token_types: Set[TokenType]) -> List[Token]:
    offset = 0
    tokens: List[Token] = []

    while offset < len(code):
        try:
            token = get_token(code, offset)
        except TokenizeError as e:
            # TODO handle
            raise e

        if token.type not in pruned_token_types:
            tokens.append(token)

        offset += token.length

    return tokens


def get_grammar_rules(non_terminals: Dict[str, Tree]) -> List[Any]:
    # TODO implement and update return type
    raise NotImplementedError
