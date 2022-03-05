from parser.parser_generator import escape_string

import pytest


@pytest.mark.parametrize(
    ["string", "expected_escaped_string"],
    [
        ("", '""'),
        ("foo bar", '"foo bar"'),
        ("foo\r\nbar", '"foo\\r\\nbar"'),
        ("a\"b\\c'", '"a\\"b\\\\c\\\'"'),
    ],
)
def test_escape_string(string: str, expected_escaped_string: str) -> None:
    assert escape_string(string) == expected_escaped_string
