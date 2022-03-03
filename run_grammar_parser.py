#!/usr/bin/env python3

from parser.grammar_parser import REWRITE_RULES, ROOT_SYMBOL, GrammarSymbolType
from parser.parser import new_parse_generic
from parser.tree import Tree
from pathlib import Path
from typing import Optional

if __name__ == "__main__":
    code = Path("./dummy_grammar.txt").read_text()

    tree: Optional[Tree] = new_parse_generic(
        REWRITE_RULES, ROOT_SYMBOL, code, GrammarSymbolType
    )

    print(tree)
