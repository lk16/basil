from parser.exceptions import BaseParseError

import pytest


@pytest.mark.parametrize(
    ["code", "offset", "expected_line_num", "expected_column_num", "expected_line"],
    [
        ("", 0, 1, 1, ""),
        ("\n", 0, 1, 1, ""),
        ("\n", 1, 2, 1, ""),
        ("aaa", 3, 1, 4, "aaa"),
        ("aaa\n", 3, 1, 4, "aaa"),
        ("aaa\nbbb", 3, 1, 4, "aaa"),
        ("aaa\nbbb", 4, 2, 1, "bbb"),
        ("aaa\nbbb\n", 4, 2, 1, "bbb"),
        ("aaa\nbbb\n", 7, 2, 4, "bbb"),
        ("aaa\nbbb\n", 8, 3, 1, ""),
    ],
)
def test_base_parse_error(
    code: str,
    offset: int,
    expected_line_num: int,
    expected_column_num: int,
    expected_line: str,
) -> None:
    error = BaseParseError("", code, offset)
    assert error.get_line_column_numbers() == (expected_line_num, expected_column_num)
    assert error.get_line() == expected_line
