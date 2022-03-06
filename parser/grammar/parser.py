# ===================================== #
# THIS FILE WAS GENERATED, DO NOT EDIT! #
# ===================================== #

# flake8: noqa
# fmt: off

from enum import IntEnum, auto
from parser.parser import (
    ConcatenationParser,
    LiteralParser,
    OptionalParser,
    OrParser,
    Parser,
    RegexBasedParser,
    RepeatParser,
    SymbolParser,
    parse_generic,
)
from parser.tree import Tree, prune_by_symbol_types
from typing import Dict, Final, Optional, Set


class SymbolType(IntEnum):
    BRACKET_EXPRESSION = auto()
    BRACKET_EXPRESSION_END = auto()
    BRACKET_EXPRESSION_REPEAT_RANGE = auto()
    COMMENT_LINE = auto()
    CONCATENATION_EXPRESSION = auto()
    CONJUNCTION_EXPRESSION = auto()
    DECORATOR_LINE = auto()
    DECORATOR_VALUE = auto()
    INTEGER = auto()
    LINE = auto()
    LITERAL_EXPRESSION = auto()
    REGEX_EXPRESSION = auto()
    ROOT = auto()
    TOKEN_COMPOUND_EXPRESSION = auto()
    TOKEN_DEFINITION_LINE = auto()
    TOKEN_EXPRESSION = auto()
    TOKEN_NAME = auto()
    WHITESPACE = auto()
    WHITESPACE_LINE = auto()


REWRITE_RULES: Final[Dict[IntEnum, Parser]] = {
    SymbolType.BRACKET_EXPRESSION: ConcatenationParser(
        LiteralParser("("),
        SymbolParser(SymbolType.WHITESPACE),
        SymbolParser(SymbolType.TOKEN_COMPOUND_EXPRESSION),
        SymbolParser(SymbolType.WHITESPACE),
        SymbolParser(SymbolType.BRACKET_EXPRESSION_END),
    ),
    SymbolType.BRACKET_EXPRESSION_END: OrParser(
        LiteralParser(")"),
        LiteralParser(")+"),
        LiteralParser(")*"),
        LiteralParser(")?"),
        SymbolParser(SymbolType.BRACKET_EXPRESSION_REPEAT_RANGE),
    ),
    SymbolType.BRACKET_EXPRESSION_REPEAT_RANGE: ConcatenationParser(
        LiteralParser("){"), SymbolParser(SymbolType.INTEGER), LiteralParser(",...}")
    ),
    SymbolType.COMMENT_LINE: RegexBasedParser("//[^\n]*\n"),
    SymbolType.CONCATENATION_EXPRESSION: ConcatenationParser(
        SymbolParser(SymbolType.TOKEN_EXPRESSION),
        SymbolParser(SymbolType.WHITESPACE),
        SymbolParser(SymbolType.TOKEN_COMPOUND_EXPRESSION),
    ),
    SymbolType.CONJUNCTION_EXPRESSION: ConcatenationParser(
        SymbolParser(SymbolType.TOKEN_EXPRESSION),
        SymbolParser(SymbolType.WHITESPACE),
        LiteralParser("|"),
        SymbolParser(SymbolType.WHITESPACE),
        SymbolParser(SymbolType.TOKEN_COMPOUND_EXPRESSION),
    ),
    SymbolType.DECORATOR_LINE: ConcatenationParser(
        LiteralParser("@"),
        SymbolParser(SymbolType.WHITESPACE),
        SymbolParser(SymbolType.DECORATOR_VALUE),
        SymbolParser(SymbolType.WHITESPACE),
        LiteralParser("\n"),
    ),
    SymbolType.DECORATOR_VALUE: OrParser(
        LiteralParser("prune hard"),
        LiteralParser("prune soft"),
        ConcatenationParser(
            LiteralParser("forbidden"),
            SymbolParser(SymbolType.WHITESPACE),
            SymbolParser(SymbolType.TOKEN_COMPOUND_EXPRESSION),
        ),
    ),
    SymbolType.INTEGER: RegexBasedParser("[0-9]+"),
    SymbolType.LINE: OrParser(
        SymbolParser(SymbolType.COMMENT_LINE),
        SymbolParser(SymbolType.WHITESPACE_LINE),
        SymbolParser(SymbolType.TOKEN_DEFINITION_LINE),
        SymbolParser(SymbolType.DECORATOR_LINE),
    ),
    SymbolType.LITERAL_EXPRESSION: RegexBasedParser('"([^\\\\]|\\\\("|n|\\\\))*?"'),
    SymbolType.REGEX_EXPRESSION: ConcatenationParser(
        LiteralParser("regex("),
        SymbolParser(SymbolType.LITERAL_EXPRESSION),
        LiteralParser(")"),
    ),
    SymbolType.ROOT: RepeatParser(SymbolParser(SymbolType.LINE)),
    SymbolType.TOKEN_COMPOUND_EXPRESSION: OrParser(
        SymbolParser(SymbolType.TOKEN_EXPRESSION),
        SymbolParser(SymbolType.CONCATENATION_EXPRESSION),
        SymbolParser(SymbolType.CONJUNCTION_EXPRESSION),
        ConcatenationParser(
            SymbolParser(SymbolType.BRACKET_EXPRESSION),
            OptionalParser(
                ConcatenationParser(
                    SymbolParser(SymbolType.WHITESPACE),
                    SymbolParser(SymbolType.TOKEN_COMPOUND_EXPRESSION),
                )
            ),
        ),
    ),
    SymbolType.TOKEN_DEFINITION_LINE: ConcatenationParser(
        SymbolParser(SymbolType.TOKEN_NAME),
        SymbolParser(SymbolType.WHITESPACE),
        LiteralParser("="),
        SymbolParser(SymbolType.WHITESPACE),
        SymbolParser(SymbolType.TOKEN_COMPOUND_EXPRESSION),
        SymbolParser(SymbolType.WHITESPACE),
    ),
    SymbolType.TOKEN_EXPRESSION: OrParser(
        SymbolParser(SymbolType.LITERAL_EXPRESSION),
        SymbolParser(SymbolType.TOKEN_NAME),
        SymbolParser(SymbolType.REGEX_EXPRESSION),
    ),
    SymbolType.TOKEN_NAME: RegexBasedParser("[A-Z_]+"),
    SymbolType.WHITESPACE: RegexBasedParser(" *"),
    SymbolType.WHITESPACE_LINE: RegexBasedParser(" *\n"),
}


HARD_PRUNED_SYMBOL_TYPES: Set[IntEnum] = {
    SymbolType.COMMENT_LINE,
    SymbolType.WHITESPACE,
    SymbolType.WHITESPACE_LINE,
}


SOFT_PRUNED_SYMBOL_TYPES: Set[IntEnum] = {
    SymbolType.LINE,
    SymbolType.TOKEN_COMPOUND_EXPRESSION,
    SymbolType.TOKEN_EXPRESSION,
}


def parse(code: str) -> Tree:
    tree: Optional[Tree] = parse_generic(REWRITE_RULES, code)

    tree = prune_by_symbol_types(tree, HARD_PRUNED_SYMBOL_TYPES, prune_hard=True)
    assert tree

    tree = prune_by_symbol_types(tree, SOFT_PRUNED_SYMBOL_TYPES, prune_hard=False)
    assert tree

    return tree
