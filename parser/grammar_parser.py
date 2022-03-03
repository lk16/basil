from enum import IntEnum, auto
from parser.parser import (
    ConcatenationParser,
    LiteralParser,
    OrParser,
    Parser,
    RegexBasedParser,
    RepeatParser,
    SymbolParser,
)
from typing import Dict


class GrammarSymbolType(IntEnum):
    FILE = auto()
    LINE = auto()
    COMMENT = auto()
    WHITESPACE_LINE = auto()
    TOKEN_DEFINITION = auto()
    TOKEN_NAME = auto()
    TOKEN_EXPRESSION = auto()
    WHITESPACE = auto()


REWRITE_RULES: Dict[IntEnum, Parser] = {
    GrammarSymbolType.FILE: RepeatParser(SymbolParser(GrammarSymbolType.LINE)),
    GrammarSymbolType.LINE: OrParser(
        SymbolParser(GrammarSymbolType.COMMENT),
        SymbolParser(GrammarSymbolType.WHITESPACE_LINE),
        SymbolParser(GrammarSymbolType.TOKEN_DEFINITION),
    ),
    GrammarSymbolType.COMMENT: RegexBasedParser("^//[^\n]*\n"),
    GrammarSymbolType.WHITESPACE_LINE: RegexBasedParser("^ *\n"),
    GrammarSymbolType.TOKEN_DEFINITION: ConcatenationParser(
        SymbolParser(GrammarSymbolType.TOKEN_NAME),
        SymbolParser(GrammarSymbolType.WHITESPACE),
        LiteralParser("="),
        SymbolParser(GrammarSymbolType.WHITESPACE),
        SymbolParser(GrammarSymbolType.TOKEN_EXPRESSION),
    ),
    GrammarSymbolType.TOKEN_NAME: RegexBasedParser("^[A-Z_]+"),
    GrammarSymbolType.TOKEN_EXPRESSION: RegexBasedParser("^[^\n]*?\n"),
    GrammarSymbolType.WHITESPACE: RegexBasedParser("^ *"),
}

ROOT_SYMBOL = GrammarSymbolType.FILE
