import re
from dataclasses import dataclass
from enum import IntEnum, auto
from pathlib import Path
from typing import Dict, List, Set, Tuple


class TokenizeError(Exception):
    def __init__(self, code: str, offset: int) -> None:
        self.code = code
        self.offset = offset
        super().__init__(f"Tokenizer failed at offset {offset}")


class Terminal(IntEnum):
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


class NonTerminal(IntEnum):
    ROOT = auto()
    TOKEN_DEFINITION = auto()
    DECORATOR = auto()
    DECORATOR_VALUE = auto()
    CONCATENATION_EXPRESSION = auto()
    BRACKET_EXPRESSION = auto()
    BRACKET_EXPRESSION_END = auto()
    TOKEN_COMPOUND_EXPRESSION = auto()
    CONJUNCTION_EXPRESSION = auto()
    TOKEN_EXPRESSION = auto()
    REGEX_EXPRESSION = auto()


STRINGS: List[Tuple[Terminal, str]] = sorted(
    [
        (Terminal.BRACKET_CLOSE_AT_LEAST_ONCE, ")+"),
        (Terminal.BRACKET_CLOSE_OPTIONAL, ")?"),
        (Terminal.BRACKET_CLOSE, ")"),
        (Terminal.BRACKET_CLOSE_REPEAT, ")*"),
        (Terminal.BRACKET_CLOSE_REPEAT_RANGE, "({"),
        (Terminal.BRACKET_OPEN, "("),
        (Terminal.DECORATOR_MARKER, "@"),
        (Terminal.DECORATOR_PRUNED, "pruned"),
        (Terminal.DECORATOR_TOKEN, "terminal"),
        (Terminal.EQUALS, "="),
        (Terminal.REGEX_START, "regex("),
        (Terminal.REPEAT_RANGE_END, ",...}"),
        (Terminal.TOKEN_DEFINITION_END, "."),
        (Terminal.VERTICAL_BAR, "|"),
    ],
    key=lambda x: -len(x[1]),
)

REGEXES: Dict[Terminal, re.Pattern[str]] = {
    Terminal.COMMENT: re.compile("^//[^\n]*"),
    Terminal.LITERAL_EXPRESSION: re.compile('^"([^\\\\]|\\\\("|n|\\\\))*?"'),
    Terminal.WHITESPACE: re.compile("^[ \n]*"),
    Terminal.INTEGER: re.compile("^[0-9]+"),
    Terminal.TOKEN_NAME: re.compile("^[A-Z_]+"),
}

PRUNED_TOKEN_TYPES: Set[Terminal] = {
    Terminal.COMMENT,
    Terminal.WHITESPACE,
}


@dataclass
class Token:
    type: Terminal
    offset: int
    length: int

    def value(self, code: str) -> str:
        return code[self.offset : self.offset + self.length]


@dataclass
class Tree:
    ...


class Epsilon:
    # Used to indicate no token is expected or consumed
    def __repr__(self) -> str:
        return "Epsilon()"


TreeItem = Tree | NonTerminal | Terminal | Epsilon


@dataclass
class Concatenation(Tree):
    children: List[TreeItem]


@dataclass
class Conjunction(Tree):
    children: List[TreeItem]


@dataclass
class Repeat(Tree):
    child: TreeItem


@dataclass
class AtLeastOnce(Tree):
    child: TreeItem


@dataclass
class RuleOptional(Tree):
    child: TreeItem


NON_TERMINALS: Dict[NonTerminal, Tree] = {
    NonTerminal.ROOT: Repeat(NonTerminal.TOKEN_DEFINITION),
    NonTerminal.TOKEN_DEFINITION: Concatenation(
        [
            Repeat(NonTerminal.DECORATOR),
            Terminal.TOKEN_NAME,
            Terminal.EQUALS,
            NonTerminal.TOKEN_COMPOUND_EXPRESSION,
            Terminal.TOKEN_DEFINITION_END,
        ]
    ),
    NonTerminal.DECORATOR: Concatenation(
        [Terminal.DECORATOR_MARKER, NonTerminal.DECORATOR_VALUE]
    ),
    NonTerminal.DECORATOR_VALUE: Conjunction(
        [Terminal.DECORATOR_PRUNED, Terminal.DECORATOR_TOKEN]
    ),
    NonTerminal.CONCATENATION_EXPRESSION: Concatenation(
        [
            Conjunction(
                [
                    NonTerminal.TOKEN_EXPRESSION,
                    NonTerminal.CONJUNCTION_EXPRESSION,
                    NonTerminal.BRACKET_EXPRESSION,
                ]
            ),
            AtLeastOnce(NonTerminal.TOKEN_COMPOUND_EXPRESSION),
        ]
    ),
    NonTerminal.BRACKET_EXPRESSION: Concatenation(
        [
            Terminal.BRACKET_OPEN,
            NonTerminal.TOKEN_COMPOUND_EXPRESSION,
            NonTerminal.BRACKET_EXPRESSION_END,
        ]
    ),
    NonTerminal.BRACKET_EXPRESSION_END: Conjunction(
        [
            Terminal.BRACKET_CLOSE,
            Terminal.BRACKET_CLOSE_REPEAT,
            Terminal.BRACKET_CLOSE_AT_LEAST_ONCE,
            Terminal.BRACKET_CLOSE_OPTIONAL,
        ]
    ),
    NonTerminal.TOKEN_COMPOUND_EXPRESSION: Conjunction(
        [
            NonTerminal.TOKEN_EXPRESSION,
            NonTerminal.CONCATENATION_EXPRESSION,
            NonTerminal.CONJUNCTION_EXPRESSION,
            NonTerminal.BRACKET_EXPRESSION,
        ]
    ),
    NonTerminal.CONJUNCTION_EXPRESSION: Concatenation(
        [
            NonTerminal.TOKEN_COMPOUND_EXPRESSION,
            Terminal.VERTICAL_BAR,
            NonTerminal.TOKEN_COMPOUND_EXPRESSION,
        ]
    ),
    NonTerminal.TOKEN_EXPRESSION: Conjunction(
        [
            Terminal.LITERAL_EXPRESSION,
            Terminal.TOKEN_NAME,
            NonTerminal.REGEX_EXPRESSION,
        ]
    ),
    NonTerminal.REGEX_EXPRESSION: Concatenation(
        [
            Terminal.REGEX_START,
            Terminal.LITERAL_EXPRESSION,
            Terminal.BRACKET_CLOSE,
        ]
    ),
}


def main() -> None:
    code = Path("parser/grammar/grammar.txt").read_text()
    pruned_token_types = PRUNED_TOKEN_TYPES
    tokens = get_tokens(code, pruned_token_types)
    non_terminals = NON_TERMINALS
    parse_table = get_parse_table(non_terminals)

    _ = parse_table
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


def get_tokens(code: str, pruned_token_types: Set[Terminal]) -> List[Token]:
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


def get_firsts(
    tree: TreeItem, non_terminals: Dict[NonTerminal, Tree]
) -> Set[Terminal | Epsilon]:
    breakpoint()

    if isinstance(tree, Concatenation):
        return get_firsts(tree.children[0], non_terminals)
    if isinstance(tree, Conjunction):
        firsts: Set[Terminal | Epsilon] = set()
        for child in tree.children:
            firsts |= get_firsts(child, non_terminals)
        return firsts
    if isinstance(tree, Repeat):
        return {tree.child, Epsilon()}
    if isinstance(tree, Epsilon):
        return {Epsilon()}
    if isinstance(tree, Terminal):
        return {Terminal}
    if isinstance(tree, NonTerminal):
        return get_firsts(non_terminals[tree], non_terminals)
    raise NotImplementedError


def get_parse_table(
    non_terminals: Dict[NonTerminal, Tree]
) -> Dict[Tuple[NonTerminal, Terminal], List[Terminal]]:

    raise NotImplementedError
