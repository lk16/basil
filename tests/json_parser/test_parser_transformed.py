import json
from typing import Any, Dict, List

import pytest

from basil.file_parser import FileParser
from basil.models import Token
from tests.json_parser import SYNTAX_JSON

TRANSFORMED_TYPE = None | bool | int | str | List[Any] | Dict[str, Any]


def transform_array(children: List[TRANSFORMED_TYPE | Token]) -> TRANSFORMED_TYPE:
    array: List[Any] = []
    for child in children:
        if isinstance(child, Token):
            # discard brackets and commas
            continue

        array.append(child)

    return array


def transform_one_child(children: List[TRANSFORMED_TYPE | Token]) -> TRANSFORMED_TYPE:
    assert len(children) == 1
    child = children[0]
    assert not isinstance(child, Token)
    return child


def transform_object(children: List[TRANSFORMED_TYPE | Token]) -> TRANSFORMED_TYPE:
    object: Dict[str, Any] = {}
    for child in children:
        if isinstance(child, Token):
            # discard brackets and commas
            continue

        assert isinstance(child, list)
        key, value = child
        assert isinstance(key, str)

        object[key] = value

    return object


def transform_object_item(children: List[TRANSFORMED_TYPE | Token]) -> TRANSFORMED_TYPE:
    assert len(children) == 3
    key = children[0]
    value = children[2]
    assert isinstance(key, str)
    return [key, value]


def node_transformer(
    node_type: str, children: List[TRANSFORMED_TYPE | Token]
) -> TRANSFORMED_TYPE:
    transformers = {
        "BOOLEAN": transform_one_child,
        "JSON": transform_one_child,
        "ARRAY": transform_array,
        "OBJECT_ITEM": transform_object_item,
        "OBJECT": transform_object,
    }

    try:
        transformer = transformers[node_type]
    except KeyError:
        raise NotImplementedError(f"for {node_type}")

    return transformer(children)


def token_transformer(token: Token) -> TRANSFORMED_TYPE | Token:
    if token.type in [
        "array_end",
        "array_start",
        "colon",
        "comma",
        "object_end",
        "object_start",
    ]:
        return token

    if token.type == "string":
        return token.value[1:-1]

    if token.type == "false":
        return False

    if token.type == "true":
        return True

    if token.type == "null":
        return None

    if token.type == "integer":
        return int(token.value)

    raise NotImplementedError(f"for {token.type}")


def basil_json_loads(text: str) -> TRANSFORMED_TYPE:
    file_parser = FileParser(SYNTAX_JSON)

    return file_parser.parse_text_and_transform(
        text,
        node_type="JSON",
        node_transformer=node_transformer,
        token_transformer=token_transformer,
    )


@pytest.mark.parametrize(
    ["text"],
    [
        ("null",),
        ("true",),
        ("false",),
        ('""',),
        ('"hello"',),
        ("123",),
        ("-123",),
        ("[]",),
        ("[1]",),
        ("[1,2,3]",),
        ("[null,false,{}]",),
        ('{"foo": [false, null, 123, {"bar": [], "baz": {}}]}',),
    ],
)
def test_json_transformed(text: str) -> None:
    assert basil_json_loads(text) == json.loads(text)
