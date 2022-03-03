from enum import IntEnum, auto
from parser.parser import (
    ConcatenationParser,
    OrParser,
    Parser,
    RegexBasedParser,
    SymbolParser,
)
from typing import Dict


class GrammarSymbolType(IntEnum):
    FILE = auto()
    COMMENT = auto()
    TOKEN_DEFINITION = auto()
    WHITESPACE = auto()


REWRITE_RULES: Dict[IntEnum, Parser] = {
    GrammarSymbolType.FILE: ConcatenationParser(
        OrParser(
            SymbolParser(GrammarSymbolType.COMMENT),
            SymbolParser(GrammarSymbolType.WHITESPACE),
            SymbolParser(GrammarSymbolType.TOKEN_DEFINITION),
        )
    ),
    GrammarSymbolType.COMMENT: RegexBasedParser("^//[^\n]*"),
    GrammarSymbolType.WHITESPACE: RegexBasedParser("^[ \n]*"),
    GrammarSymbolType.TOKEN_DEFINITION: RegexBasedParser("^[^\n]*"),
}

ROOT_SYMBOL = GrammarSymbolType.FILE
