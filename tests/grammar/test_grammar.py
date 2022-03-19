from parser.parser_generator import ParserGenerator
from pathlib import Path


def test_grammar_up_to_date() -> None:
    grammar_file = Path("parser/grammar/grammar.txt")
    parser_file = Path("parser/grammar/parser.py")

    assert ParserGenerator(grammar_file).is_up_to_date(parser_file)
