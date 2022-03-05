#!/usr/bin/env python3

from parser.parser_generator import regenerate_parser_if_stale
from pathlib import Path

if __name__ == "__main__":
    grammar_path = Path("./dummy_grammar.txt")
    parser_path = Path("./dummy_parser.py")

    regenerate_parser_if_stale(grammar_path, parser_path)
