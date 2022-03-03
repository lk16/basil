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
    COMMENT_LINE = auto()
    WHITESPACE_LINE = auto()
    TOKEN_DEFINITION_LINE = auto()
    TOKEN_NAME = auto()
    TOKEN_EXPRESSION = auto()
    WHITESPACE = auto()
    NON_EMPTY_WHITESPACE = auto()
    LITERAL_EXPRESSION = auto()


REWRITE_RULES: Dict[IntEnum, Parser] = {
    GrammarSymbolType.FILE: RepeatParser(SymbolParser(GrammarSymbolType.LINE)),
    GrammarSymbolType.LINE: OrParser(
        SymbolParser(GrammarSymbolType.COMMENT_LINE),
        SymbolParser(GrammarSymbolType.WHITESPACE_LINE),
        SymbolParser(GrammarSymbolType.TOKEN_DEFINITION_LINE),
    ),
    GrammarSymbolType.COMMENT_LINE: RegexBasedParser("^//[^\n]*\n"),
    GrammarSymbolType.WHITESPACE_LINE: RegexBasedParser("^ *\n"),
    GrammarSymbolType.TOKEN_DEFINITION_LINE: ConcatenationParser(
        SymbolParser(GrammarSymbolType.TOKEN_NAME),
        SymbolParser(GrammarSymbolType.WHITESPACE),
        LiteralParser("="),
        SymbolParser(GrammarSymbolType.WHITESPACE),
        SymbolParser(GrammarSymbolType.TOKEN_EXPRESSION),
        SymbolParser(GrammarSymbolType.WHITESPACE),
    ),
    GrammarSymbolType.TOKEN_NAME: RegexBasedParser("^[A-Z_]+"),
    GrammarSymbolType.TOKEN_EXPRESSION: OrParser(
        SymbolParser(GrammarSymbolType.LITERAL_EXPRESSION),
        SymbolParser(GrammarSymbolType.TOKEN_NAME),
        ConcatenationParser(
            LiteralParser("("),
            SymbolParser(GrammarSymbolType.NON_EMPTY_WHITESPACE),
            SymbolParser(GrammarSymbolType.TOKEN_EXPRESSION),
            SymbolParser(GrammarSymbolType.WHITESPACE),
            RepeatParser(
                ConcatenationParser(
                    LiteralParser("|"),
                    SymbolParser(GrammarSymbolType.WHITESPACE),
                    SymbolParser(GrammarSymbolType.TOKEN_EXPRESSION),
                    SymbolParser(GrammarSymbolType.WHITESPACE),
                ),
            ),
            OrParser(
                LiteralParser(")"),
                LiteralParser(")?"),
                LiteralParser(")*"),
                LiteralParser(")+"),
                LiteralParser(")+"),
                RegexBasedParser("^'\\)\\{\\d*,\\.\\.\\.\\}'"),
            ),
        ),
        RegexBasedParser(
            "^[^\n]*?\n"
        ),  # TODO remove, this matches everything on the rest of the line
    ),
    GrammarSymbolType.WHITESPACE: RegexBasedParser("^ *"),
    GrammarSymbolType.NON_EMPTY_WHITESPACE: RegexBasedParser("^ +"),
    GrammarSymbolType.LITERAL_EXPRESSION: RegexBasedParser(
        '^"([^\\\\]|\\\\("|n|\\\\))*?"'
    ),
}

ROOT_SYMBOL = GrammarSymbolType.FILE
