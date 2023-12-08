import pytest

from basil.exceptions import ParseError
from basil.file_parser import FileParser
from tests.json_parser import SYNTAX_JSON


def test_json_error_collector() -> None:
    text = '{"broken json":'

    file_parser = FileParser(SYNTAX_JSON)

    with pytest.raises(ParseError) as raised:
        file_parser.parse_text(text, node_type="JSON")

    assert raised.value.offset == 1

    parse_error = file_parser.error_collector.get_furthest_error()
    assert parse_error.offset == 3
