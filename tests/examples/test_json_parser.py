from parser.parser_generator import check_parser_staleness, generate_parser
from pathlib import Path

import pytest

from examples.json_parser import parse as parse_json


def test_parser_not_stale() -> None:
    grammar_path = Path("examples/json_grammar.txt")
    parser_path = Path("examples/json_parser.py")

    parser_code = generate_parser(grammar_path)
    assert not check_parser_staleness(parser_code, parser_path)


@pytest.mark.parametrize(
    "code",
    "true",
)
def test_parse_json_values(code: str) -> None:
    # This would raise an exception if it fails
    parse_json(code)
