# ===================================== #
# THIS FILE WAS GENERATED, DO NOT EDIT! #
# ===================================== #

# flake8: noqa
# fmt: off
# nopycln: file

from enum import IntEnum
from itertools import count
from parser.parser import (
    ConcatenationExpression,
    ConjunctionExpression,
    Expression,
    NonTerminalExpression,
    OptionalExpression,
    RepeatExpression,
    TerminalExpression,
    parse_generic,
)
from parser.tokenizer import RegexTokenizer, tokenize
from parser.tree import Token, Tree
from typing import Dict, List, Optional, Set, Tuple

# We can't use enum.auto, since Terminal and NonTerminal will have colliding values
next_offset = count(start=1)


class Terminal(IntEnum):
    BRACKET_AT_LEAST_ONCE = next(next_offset)
    BRACKET_CLOSE = next(next_offset)
    BRACKET_OPEN = next(next_offset)
    BRACKET_OPTIONAL = next(next_offset)
    BRACKET_REPEAT = next(next_offset)
    COMMENT = next(next_offset)
    DECORATOR_MARKER = next(next_offset)
    DECORATOR_PRUNE_HARD = next(next_offset)
    DECORATOR_PRUNE_SOFT = next(next_offset)
    DECORATOR_TOKEN = next(next_offset)
    EQUALS = next(next_offset)
    LITERAL_EXPRESSION = next(next_offset)
    PERIOD = next(next_offset)
    REGEX_START = next(next_offset)
    TOKEN_NAME = next(next_offset)
    VERTICAL_BAR = next(next_offset)
    WHITESPACE = next(next_offset)


TERMINAL_RULES: List[Tuple[IntEnum, RegexTokenizer]] = [
    (Terminal.COMMENT, RegexTokenizer("//[^\n]*")),
    (Terminal.WHITESPACE, RegexTokenizer("[ \n]*")),
    (Terminal.TOKEN_NAME, RegexTokenizer("[A-Z_]+")),
    (Terminal.PERIOD, RegexTokenizer("\\.")),
    (Terminal.LITERAL_EXPRESSION, RegexTokenizer('"([^\\\\]|\\\\.)*?"')),
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
    BRACKET_EXPRESSION = next(next_offset)
    BRACKET_EXPRESSION_END = next(next_offset)
    CONCATENATION_EXPRESSION = next(next_offset)
    CONJUNCTION_EXPRESSION = next(next_offset)
    DECORATOR = next(next_offset)
    DECORATOR_VALUE = next(next_offset)
    LINE = next(next_offset)
    REGEX_EXPRESSION = next(next_offset)
    ROOT = next(next_offset)
    TOKEN_COMPOUND_EXPRESSION = next(next_offset)
    TOKEN_DEFINITION = next(next_offset)
    TOKEN_EXPRESSION = next(next_offset)


NON_TERMINAL_RULES: Dict[IntEnum, Expression] = {
    NonTerminal.BRACKET_EXPRESSION: ConcatenationExpression(
        TerminalExpression(Terminal.BRACKET_OPEN),
        NonTerminalExpression(NonTerminal.TOKEN_COMPOUND_EXPRESSION),
        NonTerminalExpression(NonTerminal.BRACKET_EXPRESSION_END),
    ),
    NonTerminal.BRACKET_EXPRESSION_END: ConjunctionExpression(
        TerminalExpression(Terminal.BRACKET_CLOSE),
        TerminalExpression(Terminal.BRACKET_AT_LEAST_ONCE),
        TerminalExpression(Terminal.BRACKET_REPEAT),
        TerminalExpression(Terminal.BRACKET_OPTIONAL),
    ),
    NonTerminal.CONCATENATION_EXPRESSION: ConcatenationExpression(
        ConjunctionExpression(
            NonTerminalExpression(NonTerminal.TOKEN_EXPRESSION),
            NonTerminalExpression(NonTerminal.CONJUNCTION_EXPRESSION),
            NonTerminalExpression(NonTerminal.BRACKET_EXPRESSION),
        ),
        RepeatExpression(
            NonTerminalExpression(NonTerminal.TOKEN_COMPOUND_EXPRESSION), min_repeats=1
        ),
    ),
    NonTerminal.CONJUNCTION_EXPRESSION: ConcatenationExpression(
        NonTerminalExpression(NonTerminal.TOKEN_EXPRESSION),
        TerminalExpression(Terminal.VERTICAL_BAR),
        NonTerminalExpression(NonTerminal.TOKEN_COMPOUND_EXPRESSION),
    ),
    NonTerminal.DECORATOR: ConcatenationExpression(
        TerminalExpression(Terminal.DECORATOR_MARKER),
        NonTerminalExpression(NonTerminal.DECORATOR_VALUE),
    ),
    NonTerminal.DECORATOR_VALUE: ConjunctionExpression(
        TerminalExpression(Terminal.DECORATOR_PRUNE_HARD),
        TerminalExpression(Terminal.DECORATOR_PRUNE_SOFT),
        TerminalExpression(Terminal.DECORATOR_TOKEN),
    ),
    NonTerminal.LINE: ConjunctionExpression(
        NonTerminalExpression(NonTerminal.TOKEN_DEFINITION),
        NonTerminalExpression(NonTerminal.DECORATOR),
    ),
    NonTerminal.REGEX_EXPRESSION: ConcatenationExpression(
        TerminalExpression(Terminal.REGEX_START),
        TerminalExpression(Terminal.LITERAL_EXPRESSION),
        TerminalExpression(Terminal.BRACKET_CLOSE),
    ),
    NonTerminal.ROOT: RepeatExpression(NonTerminalExpression(NonTerminal.LINE)),
    NonTerminal.TOKEN_COMPOUND_EXPRESSION: ConjunctionExpression(
        NonTerminalExpression(NonTerminal.CONCATENATION_EXPRESSION),
        NonTerminalExpression(NonTerminal.CONJUNCTION_EXPRESSION),
        NonTerminalExpression(NonTerminal.BRACKET_EXPRESSION),
        NonTerminalExpression(NonTerminal.TOKEN_EXPRESSION),
    ),
    NonTerminal.TOKEN_DEFINITION: ConcatenationExpression(
        TerminalExpression(Terminal.TOKEN_NAME),
        TerminalExpression(Terminal.EQUALS),
        NonTerminalExpression(NonTerminal.TOKEN_COMPOUND_EXPRESSION),
        TerminalExpression(Terminal.PERIOD),
    ),
    NonTerminal.TOKEN_EXPRESSION: ConjunctionExpression(
        TerminalExpression(Terminal.TOKEN_NAME),
        NonTerminalExpression(NonTerminal.REGEX_EXPRESSION),
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
