from typing import Type

import pytest

from basil.exceptions import SyntaxJSONLoadError, SyntaxJSONParseError
from basil.syntax_loader import SyntaxLoader


@pytest.mark.parametrize(
    ["syntax_file_content", "expected_error_type"],
    [pytest.param("", SyntaxJSONParseError, id="empty-json")],
)
def test_syntax_loader_errors(
    syntax_file_content: str, expected_error_type: Type[SyntaxJSONLoadError]
) -> None:
    with pytest.raises(expected_error_type):
        SyntaxLoader(syntax_file_content)
