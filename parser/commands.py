import sys
from parser.parser_generator import (
    check_parser_staleness,
    generate_parser,
    regenerate_parser_if_stale,
)
from pathlib import Path


def generate_parser_command() -> None:
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} GRAMMAR_SOURCE_FILE TARGET_PARSER_FILE")
        exit(1)

    grammar_path = Path(sys.argv[1])
    parser_path = Path(sys.argv[2])

    regenerate_parser_if_stale(grammar_path, parser_path)


def check_parser_staleness_command() -> None:
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} GRAMMAR_SOURCE_FILE PARSER_FILE")
        exit(1)

    grammar_path = Path(sys.argv[1])
    parser_path = Path(sys.argv[2])

    generated_parser = generate_parser(grammar_path)

    if check_parser_staleness(generated_parser, parser_path):
        exit(1)
