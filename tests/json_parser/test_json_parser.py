import pytest

from basil.exceptions import ParseError, TokenizerException
from basil.file_parser import FileParser
from tests.json_parser import SYNTAX_JSON


@pytest.mark.parametrize(
    ["node_type", "text", "should_parse"],
    [
        ("ARRAY", "", False),
        ("ARRAY", "[]", True),
        ("ARRAY", "[3, ]", False),
        ("ARRAY", "[3, 3, ]", False),
        ("ARRAY", "[3, 3, 3, ]", False),
        ("ARRAY", "[3, 3, 3]", True),
        ("ARRAY", "[3, 3]", True),
        ("ARRAY", "[3]", True),
        ("ARRAY", "~", False),
        ("ARRAY", "3", False),
        ("BOOLEAN", "", False),
        ("BOOLEAN", "~", False),
        ("BOOLEAN", "3", False),
        ("BOOLEAN", "false", True),
        ("BOOLEAN", "true", True),
        ("JSON", '" "', True),
        ("JSON", '""', True),
        ("JSON", '"hello"', True),
        ("JSON", '{"foo": [3, null, false, {"bar": 3, "baz": []}]}', True),
        ("JSON", "-3", True),
        ("JSON", "", False),
        ("JSON", "~", False),
        ("JSON", "3", True),
        ("JSON", "false", True),
        ("JSON", "null", True),
        ("JSON", "true", True),
        ("OBJECT_ITEM", '"foo": "bar"', True),
        ("OBJECT_ITEM", '"foo": []', True),
        ("OBJECT_ITEM", '"foo": {}', True),
        ("OBJECT_ITEM", '"foo": 3', True),
        ("OBJECT_ITEM", '"foo": false', True),
        ("OBJECT_ITEM", '"foo": null', True),
        ("OBJECT_ITEM", "", False),
        ("OBJECT_ITEM", "~", False),
        ("OBJECT_ITEM", "3", False),
        ("OBJECT", '{"foo": 3, "bar": 3, }', False),
        ("OBJECT", '{"foo": 3, "bar": 3}', True),
        ("OBJECT", '{"foo": 3, }', False),
        ("OBJECT", '{"foo": 3}', True),
        ("OBJECT", "", False),
        ("OBJECT", "{}", True),
        ("OBJECT", "~", False),
        ("OBJECT", "3", False),
    ],
)
def test_json_syntax(node_type: str, text: str, should_parse: bool) -> None:
    file_parser = FileParser(SYNTAX_JSON)

    try:
        file_parser.parse_text(text, node_type=node_type)
    except (TokenizerException, ParseError):
        assert not should_parse
    else:
        assert should_parse
