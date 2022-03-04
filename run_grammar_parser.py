#!/usr/bin/env python3

from parser.grammar import grammar_to_parsers
from pathlib import Path

if __name__ == "__main__":
    grammr_file = Path("./dummy_grammar.txt")

    grammar_to_parsers(grammr_file)

    ...
