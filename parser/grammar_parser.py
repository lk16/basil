from enum import IntEnum, auto
from parser.parser import OrParser, Parser, RegexBasedParser, RepeatParser, SymbolParser
from typing import Dict


class GrammarSymbolType(IntEnum):
    FILE = auto()
    LINE = auto()
    COMMENT = auto()
    WHITESPACE = auto()
    DEFINITION = auto()


REWRITE_RULES: Dict[IntEnum, Parser] = {
    GrammarSymbolType.FILE: RepeatParser(SymbolParser(GrammarSymbolType.LINE)),
    GrammarSymbolType.LINE: OrParser(
        SymbolParser(GrammarSymbolType.COMMENT),
        SymbolParser(GrammarSymbolType.WHITESPACE),
        SymbolParser(GrammarSymbolType.DEFINITION),
    ),
    GrammarSymbolType.COMMENT: RegexBasedParser("^//[^\n]*\n"),
    GrammarSymbolType.WHITESPACE: RegexBasedParser("^ *\n"),
    GrammarSymbolType.DEFINITION: RegexBasedParser("^[^\n]*?\n"),
}

ROOT_SYMBOL = GrammarSymbolType.FILE
