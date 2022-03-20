# ================================================================= #
#        THIS FILE WAS AUTOMATICALLY GENERATED, DO NOT EDIT!        #
# ================================================================= #

# This turns off formatting for flake8, pycln and black
# flake8: noqa
# fmt: off
# nopycln: file

from enum import IntEnum
from itertools import count
from parser.parser.models import (
    ConcatenationExpression,
    ConjunctionExpression,
    Expression,
    NonTerminalExpression,
    OptionalExpression,
    RepeatExpression,
    TerminalExpression,
    Tree,
)
from parser.parser.parser import Parser
from parser.tokenizer.models import Literal, Regex, Token, TokenDescriptor
from parser.tokenizer.tokenizer import Tokenizer
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
    DECORATOR_PRUNE = next(next_offset)
    DECORATOR_TOKEN = next(next_offset)
    EQUALS = next(next_offset)
    LITERAL_EXPRESSION = next(next_offset)
    PERIOD = next(next_offset)
    REGEX_START = next(next_offset)
    TOKEN_NAME = next(next_offset)
    VERTICAL_BAR = next(next_offset)
    WHITESPACE = next(next_offset)


TERMINAL_RULES: List[TokenDescriptor] = [
    Regex(Terminal.COMMENT, "//[^\n]*"),
    Regex(Terminal.WHITESPACE, "[ \n]*"),
    Regex(Terminal.TOKEN_NAME, "[A-Z_]+"),
    Literal(Terminal.PERIOD, "."),
    Regex(Terminal.LITERAL_EXPRESSION, '"([^\\\\]|\\\\.)*?"'),
    Literal(Terminal.DECORATOR_MARKER, "@"),
    Literal(Terminal.DECORATOR_PRUNE, "prune"),
    Literal(Terminal.DECORATOR_TOKEN, "token"),
    Literal(Terminal.EQUALS, "="),
    Literal(Terminal.BRACKET_OPEN, "("),
    Literal(Terminal.BRACKET_AT_LEAST_ONCE, ")+"),
    Literal(Terminal.BRACKET_REPEAT, ")*"),
    Literal(Terminal.BRACKET_OPTIONAL, ")?"),
    Literal(Terminal.BRACKET_CLOSE, ")"),
    Literal(Terminal.REGEX_START, "regex("),
    Literal(Terminal.VERTICAL_BAR, "|"),
]


class NonTerminal(IntEnum):
    BRACKET_EXPRESSION = next(next_offset)
    BRACKET_EXPRESSION_END = next(next_offset)
    CONCATENATION_EXPRESSION = next(next_offset)
    CONJUNCTION_EXPRESSION = next(next_offset)
    DECORATOR = next(next_offset)
    DECORATOR_VALUE = next(next_offset)
    GRAMMAR_ENTRY = next(next_offset)
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
            NonTerminalExpression(NonTerminal.CONJUNCTION_EXPRESSION),
            NonTerminalExpression(NonTerminal.BRACKET_EXPRESSION),
            NonTerminalExpression(NonTerminal.TOKEN_EXPRESSION),
        ),
        NonTerminalExpression(NonTerminal.TOKEN_COMPOUND_EXPRESSION),
    ),
    NonTerminal.CONJUNCTION_EXPRESSION: ConcatenationExpression(
        ConjunctionExpression(
            NonTerminalExpression(NonTerminal.BRACKET_EXPRESSION),
            NonTerminalExpression(NonTerminal.TOKEN_EXPRESSION),
        ),
        TerminalExpression(Terminal.VERTICAL_BAR),
        NonTerminalExpression(NonTerminal.TOKEN_COMPOUND_EXPRESSION),
    ),
    NonTerminal.DECORATOR: ConcatenationExpression(
        TerminalExpression(Terminal.DECORATOR_MARKER),
        NonTerminalExpression(NonTerminal.DECORATOR_VALUE),
    ),
    NonTerminal.DECORATOR_VALUE: ConjunctionExpression(
        TerminalExpression(Terminal.DECORATOR_PRUNE),
        TerminalExpression(Terminal.DECORATOR_TOKEN),
    ),
    NonTerminal.GRAMMAR_ENTRY: ConcatenationExpression(
        RepeatExpression(NonTerminalExpression(NonTerminal.DECORATOR)),
        NonTerminalExpression(NonTerminal.TOKEN_DEFINITION),
    ),
    NonTerminal.REGEX_EXPRESSION: ConcatenationExpression(
        TerminalExpression(Terminal.REGEX_START),
        TerminalExpression(Terminal.LITERAL_EXPRESSION),
        TerminalExpression(Terminal.BRACKET_CLOSE),
    ),
    NonTerminal.ROOT: RepeatExpression(
        NonTerminalExpression(NonTerminal.GRAMMAR_ENTRY)
    ),
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
        TerminalExpression(Terminal.LITERAL_EXPRESSION),
    ),
}


PRUNED_TERMINALS: Set[IntEnum] = {
    Terminal.COMMENT,
    Terminal.WHITESPACE,
}


PRUNED_NON_TERMINALS: Set[IntEnum] = {
    NonTerminal.TOKEN_COMPOUND_EXPRESSION,
    NonTerminal.TOKEN_EXPRESSION,
}


def parse(filename: str, code: str) -> Tuple[List[Token], Tree]:

    tokens: List[Token] = Tokenizer(
        filename=filename,
        code=code,
        terminal_rules=TERMINAL_RULES,
        pruned_terminals=PRUNED_TERMINALS,
    ).tokenize()

    tree: Tree = Parser(
        filename=filename,
        tokens=tokens,
        code=code,
        non_terminal_rules=NON_TERMINAL_RULES,
        pruned_non_terminals=PRUNED_NON_TERMINALS,
        root_token="ROOT",
    ).parse()

    return tokens, tree
