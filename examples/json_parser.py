# ===================================== #
# THIS FILE WAS GENERATED, DO NOT EDIT! #
# ===================================== #

# flake8: noqa
# fmt: off

from enum import IntEnum, auto
from parser.parser import (
    ConcatenationParser,
    LiteralParser,
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
    BOOLEAN = auto()
    INTEGER = auto()
    LIST = auto()
    NULL = auto()
    OBJECT = auto()
    OBJECT_ELEMENT = auto()
    ROOT = auto()
    STRING = auto()
    VALUE = auto()
    WHITESPACE = auto()


REWRITE_RULES: Final[Dict[IntEnum, Parser]] = {
    SymbolType.BOOLEAN: OrParser(LiteralParser("true"), LiteralParser("false")),
    SymbolType.INTEGER: RegexBasedParser("[0-9]+"),
    SymbolType.LIST: ConcatenationParser(
        LiteralParser("["),
        OrParser(
            SymbolParser(SymbolType.WHITESPACE),
            ConcatenationParser(
                SymbolParser(SymbolType.WHITESPACE),
                SymbolParser(SymbolType.VALUE),
                SymbolParser(SymbolType.WHITESPACE),
                RepeatParser(
                    ConcatenationParser(
                        LiteralParser(","),
                        SymbolParser(SymbolType.WHITESPACE),
                        SymbolParser(SymbolType.VALUE),
                        SymbolParser(SymbolType.WHITESPACE),
                    )
                ),
            ),
        ),
    ),
    SymbolType.NULL: LiteralParser("null"),
    SymbolType.OBJECT: ConcatenationParser(
        LiteralParser("{"),
        OrParser(
            SymbolParser(SymbolType.WHITESPACE),
            ConcatenationParser(
                SymbolParser(SymbolType.OBJECT_ELEMENT),
                RepeatParser(
                    ConcatenationParser(
                        LiteralParser(","), SymbolParser(SymbolType.OBJECT_ELEMENT)
                    )
                ),
            ),
        ),
    ),
    SymbolType.OBJECT_ELEMENT: ConcatenationParser(
        SymbolParser(SymbolType.WHITESPACE),
        SymbolParser(SymbolType.STRING),
        SymbolParser(SymbolType.WHITESPACE),
        LiteralParser(":"),
        SymbolParser(SymbolType.WHITESPACE),
        SymbolParser(SymbolType.VALUE),
        SymbolParser(SymbolType.WHITESPACE),
    ),
    SymbolType.ROOT: SymbolParser(SymbolType.VALUE),
    SymbolType.STRING: LiteralParser('"[^"]*"'),
    SymbolType.VALUE: OrParser(
        SymbolParser(SymbolType.OBJECT),
        SymbolParser(SymbolType.LIST),
        SymbolParser(SymbolType.STRING),
        SymbolParser(SymbolType.BOOLEAN),
        SymbolParser(SymbolType.INTEGER),
        SymbolParser(SymbolType.NULL),
    ),
    SymbolType.WHITESPACE: RegexBasedParser("[ \n]*"),
}


SOFT_PRUNED_SYMBOL_TYPES: Set[IntEnum] = {
    SymbolType.OBJECT_ELEMENT,
    SymbolType.VALUE,
}


def parse(code: str) -> Tree:
    tree: Optional[Tree] = parse_generic(REWRITE_RULES, code)

    tree = prune_by_symbol_types(tree, SOFT_PRUNED_SYMBOL_TYPES, prune_subtree=False)
    assert tree

    return tree
