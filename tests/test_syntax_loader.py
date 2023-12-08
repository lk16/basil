import json
from typing import Type

import pytest

from basil.syntax_loader.exceptions import (
    BadNodeTypeName,
    BadTokenTypeName,
    DuplicateTokenType,
    InvalidRoot,
    LoadError,
    MissingFields,
    NodeDefinitionParseError,
    NodeDefinitionUnknownNodeError,
    NodeDefinitionUnknownTokenError,
    ParseError,
    RegexError,
    UnexpectedFields,
    UnexpectedFieldType,
    UnknownFilteredTokenTypes,
    UnknownRootNode,
)
from basil.syntax_loader.syntax_loader import SyntaxLoader


@pytest.mark.parametrize(
    ["syntax_file_content", "expected_error_type"],
    [
        pytest.param("", ParseError, id="empty"),
        pytest.param("[]", InvalidRoot, id="invalid-root"),
        pytest.param(
            """{
                "filtered_tokens": {},
                "keyword_tokens": {},
                "nodes": {},
                "regular_tokens": [],
                "root_node": "",
                "unexpected": ""
            }""",
            UnexpectedFields,
            id="unexpected-fields",
        ),
        pytest.param(
            """{
                "filtered_tokens": ""
            }""",
            MissingFields,
            id="missing-fields",
        ),
        pytest.param(
            """{
                "filtered_tokens": [],
                "keyword_tokens": "",
                "nodes": {},
                "regular_tokens": {},
                "root_node": ""
            }""",
            UnexpectedFieldType,
            id="wrong-field-type-keyword-tokens",
        ),
        pytest.param(
            """{
                "filtered_tokens": [],
                "keyword_tokens": {},
                "nodes": {},
                "regular_tokens": "",
                "root_node": ""
            }""",
            UnexpectedFieldType,
            id="wrong-field-type-regular-tokens",
        ),
        pytest.param(
            """{
                "filtered_tokens": [],
                "keyword_tokens": {"foo": 3},
                "nodes": {},
                "regular_tokens": {},
                "root_node": ""
            }""",
            UnexpectedFieldType,
            id="wrong-field-type-keyword-token-item",
        ),
        pytest.param(
            """{
                "filtered_tokens": [],
                "keyword_tokens": {},
                "nodes": {},
                "regular_tokens": {"foo": 3},
                "root_node": ""
            }""",
            UnexpectedFieldType,
            id="wrong-field-type-regular-token-item",
        ),
        pytest.param(
            """{
                "filtered_tokens": 3,
                "keyword_tokens": {},
                "nodes": {},
                "regular_tokens": {},
                "root_node": ""
            }""",
            UnexpectedFieldType,
            id="wrong-field-type-filtered-tokens",
        ),
        pytest.param(
            """{
                "filtered_tokens": [3],
                "keyword_tokens": {},
                "nodes": {},
                "regular_tokens": {},
                "root_node": ""
            }""",
            UnexpectedFieldType,
            id="wrong-field-type-filtered-token-item",
        ),
        pytest.param(
            """{
                "filtered_tokens": [],
                "keyword_tokens": {},
                "nodes": 3,
                "regular_tokens": {},
                "root_node": ""
            }""",
            UnexpectedFieldType,
            id="wrong-field-type-nodes",
        ),
        pytest.param(
            """{
                "filtered_tokens": [],
                "keyword_tokens": {},
                "nodes": {"foo": 3},
                "regular_tokens": {},
                "root_node": ""
            }""",
            UnexpectedFieldType,
            id="wrong-field-type-node-item",
        ),
        pytest.param(
            """{
                "filtered_tokens": [],
                "keyword_tokens": {},
                "nodes": {},
                "regular_tokens": {},
                "root_node": 3
            }""",
            UnexpectedFieldType,
            id="wrong-field-type-root-node",
        ),
        pytest.param(
            """{
                "filtered_tokens": [],
                "keyword_tokens": {"foo": ""},
                "nodes": {},
                "regular_tokens": {"foo": ""},
                "root_node": ""
            }""",
            DuplicateTokenType,
            id="duplicate-token-type",
        ),
        pytest.param(
            """{
                "filtered_tokens": [],
                "keyword_tokens": {"foo": "["},
                "nodes": {},
                "regular_tokens": {},
                "root_node": ""
            }""",
            RegexError,
            id="regex-error-in-keyword-token",
        ),
        pytest.param(
            """{
                "filtered_tokens": [],
                "keyword_tokens": {},
                "nodes": {},
                "regular_tokens": {"foo": "["},
                "root_node": ""
            }""",
            RegexError,
            id="regex-error-in-regular-token",
        ),
        pytest.param(
            """{
                "filtered_tokens": ["foo"],
                "keyword_tokens": {},
                "nodes": {},
                "regular_tokens": {},
                "root_node": ""
            }""",
            UnknownFilteredTokenTypes,
            id="unknown-filtered-token-type",
        ),
        pytest.param(
            """{
                "filtered_tokens": [],
                "keyword_tokens": {},
                "nodes": {},
                "regular_tokens": {},
                "root_node": "foo"
            }""",
            UnknownRootNode,
            id="unknown-root-node",
        ),
        pytest.param(
            """{
                "filtered_tokens": [],
                "keyword_tokens": {"FOO": ""},
                "nodes": {"root": ""},
                "regular_tokens": {},
                "root_node": "root"
            }""",
            BadTokenTypeName,
            id="bad-keyword-token-type-name",
        ),
        pytest.param(
            """{
                "filtered_tokens": [],
                "keyword_tokens": {},
                "nodes": {"root": ""},
                "regular_tokens": {"FOO": ""},
                "root_node": "root"
            }""",
            BadTokenTypeName,
            id="bad-regular-token-type-name",
        ),
        pytest.param(
            """{
                "filtered_tokens": [],
                "keyword_tokens": {},
                "nodes": {"root": "", "FOO": ""},
                "regular_tokens": {},
                "root_node": "root"
            }""",
            BadNodeTypeName,
            id="bad-node-type-name",
        ),
        pytest.param(
            """{
                "filtered_tokens": [],
                "keyword_tokens": {},
                "nodes": {"FOO": "~"},
                "regular_tokens": {},
                "root_node": "FOO"
            }""",
            NodeDefinitionParseError,
            id="parser-definition-tokenize-error",
        ),
        pytest.param(
            """{
                "filtered_tokens": [],
                "keyword_tokens": {},
                "nodes": {"FOO": "bar"},
                "regular_tokens": {},
                "root_node": "FOO"
            }""",
            NodeDefinitionUnknownTokenError,
            id="parser-definition-unknown-token",
        ),
        pytest.param(
            """{
                "filtered_tokens": [],
                "keyword_tokens": {},
                "nodes": {"FOO": "BAR"},
                "regular_tokens": {},
                "root_node": "FOO"
            }""",
            NodeDefinitionUnknownNodeError,
            id="parser-definition-unknown-node",
        ),
        pytest.param(
            """{
                "filtered_tokens": [],
                "keyword_tokens": {},
                "nodes": {"FOO": "*"},
                "regular_tokens": {},
                "root_node": "FOO"
            }""",
            NodeDefinitionParseError,
            id="parser-definition-error-repeat-without-prefix",
        ),
        pytest.param(
            """{
                "filtered_tokens": [],
                "keyword_tokens": {},
                "nodes": {"FOO": "?"},
                "regular_tokens": {},
                "root_node": "FOO"
            }""",
            NodeDefinitionParseError,
            id="parser-definition-error-optional-without-prefix",
        ),
        pytest.param(
            """{
                "filtered_tokens": [],
                "keyword_tokens": {},
                "nodes": {"FOO": "+"},
                "regular_tokens": {},
                "root_node": "FOO"
            }""",
            NodeDefinitionParseError,
            id="parser-definition-error-repeat-atleast-once-without-prefix",
        ),
        pytest.param(
            """{
                "filtered_tokens": [],
                "keyword_tokens": {},
                "nodes": {"FOO": "|*"},
                "regular_tokens": {},
                "root_node": "FOO"
            }""",
            NodeDefinitionParseError,
            id="parser-definition-error-repeat-after-choice",
        ),
        pytest.param(
            """{
                "filtered_tokens": [],
                "keyword_tokens": {},
                "nodes": {"FOO": "|?"},
                "regular_tokens": {},
                "root_node": "FOO"
            }""",
            NodeDefinitionParseError,
            id="parser-definition-error-optional-after-choice",
        ),
        pytest.param(
            """{
                "filtered_tokens": [],
                "keyword_tokens": {},
                "nodes": {"FOO": "|+"},
                "regular_tokens": {},
                "root_node": "FOO"
            }""",
            NodeDefinitionParseError,
            id="parser-definition-error-repeat-atleast-once-after-choice",
        ),
        pytest.param(
            """{
                "filtered_tokens": [],
                "keyword_tokens": {},
                "nodes": {"FOO": "| FOO"},
                "regular_tokens": {},
                "root_node": "FOO"
            }""",
            NodeDefinitionParseError,
            id="parser-definition-error-choice-without-prefix",
        ),
        pytest.param(
            """{
                "filtered_tokens": [],
                "keyword_tokens": {},
                "nodes": {"FOO": ")"},
                "regular_tokens": {},
                "root_node": "FOO"
            }""",
            NodeDefinitionParseError,
            id="parser-definition-error-unmatched-group-end",
        ),
        pytest.param(
            """{
                "filtered_tokens": [],
                "keyword_tokens": {},
                "nodes": {"FOO": "("},
                "regular_tokens": {},
                "root_node": "FOO"
            }""",
            NodeDefinitionParseError,
            id="parser-definition-error-unmatched-group-start",
        ),
        pytest.param(
            """{
                "filtered_tokens": [],
                "keyword_tokens": {},
                "nodes": {"FOO": "FOO |"},
                "regular_tokens": {},
                "root_node": "FOO"
            }""",
            NodeDefinitionParseError,
            id="parser-definition-error-choice-without-rhs",
        ),
        pytest.param(
            """{
                "filtered_tokens": [],
                "keyword_tokens": {},
                "nodes": {"FOO": "FOO | "},
                "regular_tokens": {},
                "root_node": "FOO"
            }""",
            NodeDefinitionParseError,
            id="parser-definition-error-choice-with-whitespace-rhs",
        ),
        pytest.param(
            """{
                "filtered_tokens": [],
                "keyword_tokens": {},
                "nodes": {"FOO": "FOO | |"},
                "regular_tokens": {},
                "root_node": "FOO"
            }""",
            NodeDefinitionParseError,
            id="parser-definition-error-choice-with-choice-rhs",
        ),
        pytest.param(
            """{
                "filtered_tokens": [],
                "keyword_tokens": {},
                "nodes": {"FOO": ""},
                "regular_tokens": {},
                "root_node": "FOO"
            }""",
            NodeDefinitionParseError,
            id="parser-definition-error-empty-concatenate-parser",
        ),
    ],
)
def test_syntax_loader_errors(
    syntax_file_content: str, expected_error_type: Type[LoadError]
) -> None:
    with pytest.raises(expected_error_type):
        SyntaxLoader(syntax_file_content)


def test_syntax_loader_ok() -> None:
    syntax_file_content = json.dumps(
        {
            "filtered_tokens": [],
            "keyword_tokens": {"bar": "[bB]ar"},
            "nodes": {"FOO": "FOO* | ((bar)+ | baz)?"},
            "regular_tokens": {"baz": "baz+"},
            "root_node": "FOO",
        }
    )

    # Should not raise
    SyntaxLoader(syntax_file_content)
