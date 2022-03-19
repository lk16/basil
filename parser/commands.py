import sys
from parser.parser_generator import ParserGenerator
from pathlib import Path


def generate_parser_command() -> None:
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} GRAMMAR_SOURCE_FILE TARGET_PARSER_FILE")
        exit(1)

    grammar_path = Path(sys.argv[1])
    parser_path = Path(sys.argv[2])

    ParserGenerator(grammar_path).write_if_stale(parser_path)


def check_parser_staleness_command() -> None:
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} GRAMMAR_SOURCE_FILE PARSER_FILE")
        exit(1)

    grammar_path = Path(sys.argv[1])
    parser_path = Path(sys.argv[2])

    if not ParserGenerator(grammar_path).is_up_to_date(parser_path):
        exit(1)
