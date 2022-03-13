# ===================================== #
# THIS FILE WAS GENERATED, DO NOT EDIT! #
# ===================================== #

# flake8: noqa
# fmt: off
# nopycln: file

from enum import IntEnum, auto
from parser.parser import (
    ConcatenationParser,
    NonTerminalParser,
    OptionalParser,
    OrParser,
    Parser,
    RepeatParser,
    TerminalParser,
    Token,
    parse_generic,
)
from parser.tokenizer import RegexTokenizer, tokenize
from parser.tree import Tree
from typing import Dict, List, Optional, Set, Tuple


class Terminal(IntEnum):
    BRACKET_AT_LEAST_ONCE = auto()
    BRACKET_CLOSE = auto()
    BRACKET_OPEN = auto()
    BRACKET_OPTIONAL = auto()
    BRACKET_REPEAT = auto()
    COMMENT = auto()
    DECORATOR_MARKER = auto()
    DECORATOR_PRUNE_HARD = auto()
    DECORATOR_PRUNE_SOFT = auto()
    DECORATOR_TOKEN = auto()
    EQUALS = auto()
    LITERAL_EXPRESSION = auto()
    PERIOD = auto()
    REGEX_START = auto()
    TOKEN_NAME = auto()
    VERTICAL_BAR = auto()
    WHITESPACE = auto()


TERMINAL_RULES: List[Tuple[IntEnum, RegexTokenizer]] = [
    (Terminal.COMMENT, RegexTokenizer("//[^\n]*")),
    (Terminal.WHITESPACE, RegexTokenizer("[ \n]*")),
    (Terminal.TOKEN_NAME, RegexTokenizer("[A-Z_]+")),
    (Terminal.PERIOD, RegexTokenizer("\\.")),
    (Terminal.LITERAL_EXPRESSION, RegexTokenizer("\"([^\\\\]|\\\\.)*?\"")),
    (Terminal.DECORATOR_MARKER, RegexTokenizer("@")),
    (Terminal.DECORATOR_PRUNE_HARD, RegexTokenizer("prune hard")),
    (Terminal.DECORATOR_PRUNE_SOFT, RegexTokenizer("prune soft")),
    (Terminal.DECORATOR_TOKEN, RegexTokenizer("token")),
    (Terminal.EQUALS, RegexTokenizer("=")),
    (Terminal.BRACKET_OPEN, RegexTokenizer("\\(")),
    (Terminal.BRACKET_AT_LEAST_ONCE, RegexTokenizer("\\)\\+")),
    (Terminal.BRACKET_REPEAT, RegexTokenizer("\\)\\*")),
    (Terminal.BRACKET_OPTIONAL, RegexTokenizer("\\)\\?")),
    (Terminal.BRACKET_CLOSE, RegexTokenizer("\\)")),
    (Terminal.REGEX_START, RegexTokenizer("regex\\(")),
    (Terminal.VERTICAL_BAR, RegexTokenizer("\\|")),
]


class NonTerminal(IntEnum):
    BRACKET_EXPRESSION = auto()
    BRACKET_EXPRESSION_END = auto()
    CONCATENATION_EXPRESSION = auto()
    CONJUNCTION_EXPRESSION = auto()
    DECORATOR = auto()
    DECORATOR_VALUE = auto()
    LINE = auto()
    REGEX_EXPRESSION = auto()
    ROOT = auto()
    TOKEN_COMPOUND_EXPRESSION = auto()
    TOKEN_DEFINITION = auto()
    TOKEN_EXPRESSION = auto()


NON_TERMINAL_RULES: Dict[IntEnum, Parser] = {
    NonTerminal.BRACKET_EXPRESSION: ConcatenationParser(
        TerminalParser(Terminal.BRACKET_OPEN),
        NonTerminalParser(NonTerminal.TOKEN_COMPOUND_EXPRESSION),
        NonTerminalParser(NonTerminal.BRACKET_EXPRESSION_END),
    ),
    NonTerminal.BRACKET_EXPRESSION_END: OrParser(
        TerminalParser(Terminal.BRACKET_CLOSE),
        TerminalParser(Terminal.BRACKET_AT_LEAST_ONCE),
        TerminalParser(Terminal.BRACKET_REPEAT),
        TerminalParser(Terminal.BRACKET_OPTIONAL),
    ),
    NonTerminal.CONCATENATION_EXPRESSION: ConcatenationParser(
        OrParser(
            NonTerminalParser(NonTerminal.TOKEN_EXPRESSION),
            NonTerminalParser(NonTerminal.CONJUNCTION_EXPRESSION),
            NonTerminalParser(NonTerminal.BRACKET_EXPRESSION),
        ),
        RepeatParser(
            NonTerminalParser(NonTerminal.TOKEN_COMPOUND_EXPRESSION), min_repeats=1
        ),
    ),
    NonTerminal.CONJUNCTION_EXPRESSION: ConcatenationParser(
        NonTerminalParser(NonTerminal.TOKEN_EXPRESSION),
        TerminalParser(Terminal.VERTICAL_BAR),
        NonTerminalParser(NonTerminal.TOKEN_COMPOUND_EXPRESSION),
    ),
    NonTerminal.DECORATOR: ConcatenationParser(
        TerminalParser(Terminal.DECORATOR_MARKER),
        NonTerminalParser(NonTerminal.DECORATOR_VALUE),
    ),
    NonTerminal.DECORATOR_VALUE: OrParser(
        TerminalParser(Terminal.DECORATOR_PRUNE_HARD),
        TerminalParser(Terminal.DECORATOR_PRUNE_SOFT),
        TerminalParser(Terminal.DECORATOR_TOKEN),
    ),
    NonTerminal.LINE: OrParser(
        NonTerminalParser(NonTerminal.TOKEN_DEFINITION),
        NonTerminalParser(NonTerminal.DECORATOR),
    ),
    NonTerminal.REGEX_EXPRESSION: ConcatenationParser(
        TerminalParser(Terminal.REGEX_START),
        TerminalParser(Terminal.LITERAL_EXPRESSION),
        TerminalParser(Terminal.BRACKET_CLOSE),
    ),
    NonTerminal.ROOT: RepeatParser(NonTerminalParser(NonTerminal.LINE)),
    NonTerminal.TOKEN_COMPOUND_EXPRESSION: OrParser(
        NonTerminalParser(NonTerminal.CONCATENATION_EXPRESSION),
        NonTerminalParser(NonTerminal.CONJUNCTION_EXPRESSION),
        NonTerminalParser(NonTerminal.BRACKET_EXPRESSION),
        NonTerminalParser(NonTerminal.TOKEN_EXPRESSION),
    ),
    NonTerminal.TOKEN_DEFINITION: ConcatenationParser(
        TerminalParser(Terminal.TOKEN_NAME),
        TerminalParser(Terminal.EQUALS),
        NonTerminalParser(NonTerminal.TOKEN_COMPOUND_EXPRESSION),
        TerminalParser(Terminal.PERIOD),
    ),
    NonTerminal.TOKEN_EXPRESSION: OrParser(
        TerminalParser(Terminal.TOKEN_NAME),
        NonTerminalParser(NonTerminal.REGEX_EXPRESSION),
    ),
}

PRUNED_TERMINALS: Set[IntEnum] = {
    Terminal.COMMENT,
    Terminal.WHITESPACE,
}

HARD_PRUNED_NON_TERMINALS: Set[IntEnum] = set()


SOFT_PRUNED_NON_TERMINALS: Set[IntEnum] = {
    NonTerminal.LINE,
    NonTerminal.TOKEN_COMPOUND_EXPRESSION,
    NonTerminal.TOKEN_EXPRESSION,
}


def parse(code: str) -> Tuple[List[Token], Tree]:
    tokens: List[Token] = tokenize(code, TERMINAL_RULES, PRUNED_TERMINALS)
    tree: Tree = parse_generic(
        NON_TERMINAL_RULES,
        tokens,
        code,
        HARD_PRUNED_NON_TERMINALS,
        SOFT_PRUNED_NON_TERMINALS,
    )
    return tokens, tree
