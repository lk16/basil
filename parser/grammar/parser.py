# ===================================== #
# THIS FILE WAS GENERATED, DO NOT EDIT! #
# ===================================== #

# flake8: noqa
# fmt: off
# nopycln: file

from enum import IntEnum, auto
from parser.parser import (
    ConcatenationParser,
    LiteralParser,
    NonTerminalParser,
    OptionalParser,
    OrParser,
    Parser,
    RegexTokenizer,
    RepeatParser,
    TerminalParser,
    Token,
    parse_generic,
    tokenize,
)
from parser.tree import Tree
from typing import Dict, List, Optional, Set, Tuple


class Terminal(IntEnum):
    internal_NON_TERMINAL_LITERAL = auto()
    COMMENT_LINE = auto()
    INTEGER = auto()
    NEWLINE = auto()
    LITERAL_EXPRESSION = auto()
    TOKEN_NAME = auto()
    WHITESPACE = auto()
    WHITESPACE_LINE = auto()


TERMINAL_RULES: List[Tuple[IntEnum, RegexTokenizer]] = [
    (
        Terminal.internal_NON_TERMINAL_LITERAL,
        RegexTokenizer(
            "prune\ soft|prune\ hard|regex\(|,\.\.\.\}|token|\)\?|\)\{|\)\*|\)\+|\(|\||=|@|\)"
        ),
    ),
    (Terminal.COMMENT_LINE, RegexTokenizer("//[^\n]*\n")),
    (Terminal.WHITESPACE_LINE, RegexTokenizer(" *\n")),
    (Terminal.WHITESPACE, RegexTokenizer(" *")),
    (Terminal.NEWLINE, RegexTokenizer("\n")),
    (Terminal.TOKEN_NAME, RegexTokenizer("[A-Z_]+")),
    (Terminal.INTEGER, RegexTokenizer("[0-9]+")),
    (Terminal.LITERAL_EXPRESSION, RegexTokenizer('"([^\\\\]|\\\\("|n|\\\\))*?"')),
]


class NonTerminal(IntEnum):
    internal_NON_TERMINAL_LITERAL = auto()
    BRACKET_EXPRESSION = auto()
    BRACKET_EXPRESSION_END = auto()
    BRACKET_EXPRESSION_REPEAT_RANGE = auto()
    CONCATENATION_EXPRESSION = auto()
    CONJUNCTION_EXPRESSION = auto()
    DECORATOR_LINE = auto()
    DECORATOR_VALUE = auto()
    LINE = auto()
    REGEX_EXPRESSION = auto()
    ROOT = auto()
    TOKEN_COMPOUND_EXPRESSION = auto()
    TOKEN_DEFINITION_LINE = auto()
    TOKEN_EXPRESSION = auto()


NON_TERMINAL_RULES: Dict[IntEnum, Parser] = {
    NonTerminal.internal_NON_TERMINAL_LITERAL: TerminalParser(
        Terminal.internal_NON_TERMINAL_LITERAL
    ),
    NonTerminal.BRACKET_EXPRESSION: ConcatenationParser(
        LiteralParser("("),
        NonTerminalParser(NonTerminal.TOKEN_COMPOUND_EXPRESSION),
        NonTerminalParser(NonTerminal.BRACKET_EXPRESSION_END),
    ),
    NonTerminal.BRACKET_EXPRESSION_END: OrParser(
        LiteralParser(")"),
        LiteralParser(")+"),
        LiteralParser(")*"),
        LiteralParser(")?"),
        NonTerminalParser(NonTerminal.BRACKET_EXPRESSION_REPEAT_RANGE),
    ),
    NonTerminal.BRACKET_EXPRESSION_REPEAT_RANGE: ConcatenationParser(
        LiteralParser("){"), TerminalParser(Terminal.INTEGER), LiteralParser(",...}")
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
        LiteralParser("|"),
        NonTerminalParser(NonTerminal.TOKEN_COMPOUND_EXPRESSION),
    ),
    NonTerminal.DECORATOR_LINE: ConcatenationParser(
        LiteralParser("@"),
        NonTerminalParser(NonTerminal.DECORATOR_VALUE),
        LiteralParser("\n"),
    ),
    NonTerminal.DECORATOR_VALUE: OrParser(
        LiteralParser("prune hard"), LiteralParser("prune soft"), LiteralParser("token")
    ),
    NonTerminal.LINE: OrParser(
        NonTerminalParser(NonTerminal.TOKEN_DEFINITION_LINE),
        NonTerminalParser(NonTerminal.DECORATOR_LINE),
    ),
    NonTerminal.REGEX_EXPRESSION: ConcatenationParser(
        LiteralParser("regex("),
        TerminalParser(Terminal.LITERAL_EXPRESSION),
        LiteralParser(")"),
    ),
    NonTerminal.ROOT: RepeatParser(NonTerminalParser(NonTerminal.LINE)),
    NonTerminal.TOKEN_COMPOUND_EXPRESSION: OrParser(
        NonTerminalParser(NonTerminal.TOKEN_EXPRESSION),
        NonTerminalParser(NonTerminal.CONCATENATION_EXPRESSION),
        NonTerminalParser(NonTerminal.CONJUNCTION_EXPRESSION),
        NonTerminalParser(NonTerminal.BRACKET_EXPRESSION),
    ),
    NonTerminal.TOKEN_DEFINITION_LINE: ConcatenationParser(
        TerminalParser(Terminal.TOKEN_NAME),
        LiteralParser("="),
        NonTerminalParser(NonTerminal.TOKEN_COMPOUND_EXPRESSION),
        LiteralParser("\n"),
    ),
    NonTerminal.TOKEN_EXPRESSION: OrParser(
        TerminalParser(Terminal.LITERAL_EXPRESSION),
        TerminalParser(Terminal.TOKEN_NAME),
        NonTerminalParser(NonTerminal.REGEX_EXPRESSION),
    ),
}

PRUNED_TERMINALS: Set[IntEnum] = {
    Terminal.COMMENT_LINE,
    Terminal.NEWLINE,
    Terminal.WHITESPACE_LINE,
    Terminal.WHITESPACE,
}

HARD_PRUNED_NON_TERMINALS: Set[IntEnum] = set()


SOFT_PRUNED_NON_TERMINALS: Set[IntEnum] = {
    NonTerminal.LINE,
    NonTerminal.TOKEN_COMPOUND_EXPRESSION,
    NonTerminal.TOKEN_EXPRESSION,
}


def parse(code: str) -> Tree:
    tokens: List[Token] = tokenize(code, TERMINAL_RULES, PRUNED_TERMINALS)
    return parse_generic(
        NON_TERMINAL_RULES,
        tokens,
        code,
        HARD_PRUNED_NON_TERMINALS,
        SOFT_PRUNED_NON_TERMINALS,
    )
