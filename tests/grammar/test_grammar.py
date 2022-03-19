from parser.parser_generator import check_parser_staleness, generate_parser
from pathlib import Path


def test_grammar_up_to_date() -> None:
    grammar_file = Path("parser/grammar/grammar.txt")
    parser_file = Path("parser/grammar/parser.py")

    generated_parser = generate_parser(grammar_file)

    assert not check_parser_staleness(generated_parser, parser_file)
