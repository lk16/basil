import re
from enum import IntEnum, auto
from parser.exceptions import UnexpectedSymbolType, UnhandledSymbolType
from parser.parser import (
    ConcatenationParser,
    InternalParseError,
    LiteralParser,
    OptionalParser,
    OrParser,
    ParseError,
    Parser,
    RegexBasedParser,
    RepeatParser,
    SymbolParser,
    humanize_parse_error,
    new_parse_generic,
)
from typing import Dict

import pytest


# NOTE: Should not have Test prefix
class SymbolsForTesting(IntEnum):
    ROOT = auto()
    A = auto()
    B = auto()
    C = auto()
    D = auto()


@pytest.mark.parametrize("code", ["", "A", "B", "C", "D", "AA", "DA", "AD"])
def test_parser_three_options(code: str) -> None:
    rewrite_rules: Dict[IntEnum, Parser] = {
        SymbolsForTesting.ROOT: OrParser(
            SymbolParser(SymbolsForTesting.A),
            SymbolParser(SymbolsForTesting.B),
            SymbolParser(SymbolsForTesting.C),
        ),
        SymbolsForTesting.A: LiteralParser("A"),
        SymbolsForTesting.B: LiteralParser("B"),
        SymbolsForTesting.C: LiteralParser("C"),
        SymbolsForTesting.D: LiteralParser("D"),
    }

    expected_ok = re.compile("A|B|C").fullmatch(code)

    try:
        new_parse_generic(rewrite_rules, code)
    except ParseError:
        assert not expected_ok
    else:
        assert expected_ok


@pytest.mark.parametrize("code", ["", "A", "foo", "f", "B", " foo", "foo ", " foo "])
def test_parser_option_of_literal_and_symbol(code: str) -> None:
    rewrite_rules: Dict[IntEnum, Parser] = {
        SymbolsForTesting.ROOT: OrParser(
            SymbolParser(SymbolsForTesting.A), LiteralParser("foo")
        ),
        SymbolsForTesting.A: LiteralParser("A"),
        SymbolsForTesting.B: LiteralParser("B"),
        SymbolsForTesting.C: LiteralParser("C"),
        SymbolsForTesting.D: LiteralParser("D"),
    }

    expected_ok = re.compile("A|foo").fullmatch(code)

    try:
        new_parse_generic(rewrite_rules, code)
    except ParseError:
        assert not expected_ok
    else:
        assert expected_ok


@pytest.mark.parametrize("code", ["", "A", "AB", "ABC", " ABC", "ABC "])
def test_parser_three_literals(code: str) -> None:
    rewrite_rules: Dict[IntEnum, Parser] = {
        SymbolsForTesting.ROOT: ConcatenationParser(
            LiteralParser("A"), LiteralParser("B"), LiteralParser("C")
        ),
        SymbolsForTesting.A: LiteralParser("A"),
        SymbolsForTesting.B: LiteralParser("B"),
        SymbolsForTesting.C: LiteralParser("C"),
        SymbolsForTesting.D: LiteralParser("D"),
    }

    expected_ok = re.compile("ABC").fullmatch(code)

    try:
        new_parse_generic(rewrite_rules, code)
    except ParseError:
        assert not expected_ok
    else:
        assert expected_ok


@pytest.mark.parametrize(
    "code", ["A", "B", "C", "D", "AB", "AB ", "AC", "BC", "BD", "AA"]
)
def test_parser_optionals_with_concatenation(code: str) -> None:
    rewrite_rules: Dict[IntEnum, Parser] = {
        SymbolsForTesting.ROOT: ConcatenationParser(
            OrParser(
                SymbolParser(SymbolsForTesting.A), SymbolParser(SymbolsForTesting.B)
            ),
            OrParser(
                SymbolParser(SymbolsForTesting.C), SymbolParser(SymbolsForTesting.D)
            ),
        ),
        SymbolsForTesting.A: LiteralParser("A"),
        SymbolsForTesting.B: LiteralParser("B"),
        SymbolsForTesting.C: LiteralParser("C"),
        SymbolsForTesting.D: LiteralParser("D"),
    }

    expected_ok = re.compile("(A|B)(C|D)").fullmatch(code)

    try:
        new_parse_generic(rewrite_rules, code)
    except ParseError:
        assert not expected_ok
    else:
        assert expected_ok


@pytest.mark.parametrize(
    "code", ["", "foo", "foobar", "foobarbaz", "-foobarbaz", "foobarbazquux"]
)
def test_parser_concatenate_three_symbols(code: str) -> None:
    rewrite_rules: Dict[IntEnum, Parser] = {
        SymbolsForTesting.ROOT: ConcatenationParser(
            SymbolParser(SymbolsForTesting.A),
            SymbolParser(SymbolsForTesting.B),
            SymbolParser(SymbolsForTesting.C),
        ),
        SymbolsForTesting.A: LiteralParser("foo"),
        SymbolsForTesting.B: LiteralParser("bar"),
        SymbolsForTesting.C: LiteralParser("baz"),
        SymbolsForTesting.D: LiteralParser("D"),
    }

    expected_ok = re.compile("foobarbaz").fullmatch(code)

    try:
        new_parse_generic(rewrite_rules, code)
    except ParseError:
        assert not expected_ok
    else:
        assert expected_ok


@pytest.mark.parametrize("code", ["", "A", "B", "AB", "AAB", "AAAB", "BB", "ABB"])
def test_parser_repeat_symbols(code: str) -> None:
    rewrite_rules: Dict[IntEnum, Parser] = {
        SymbolsForTesting.ROOT: ConcatenationParser(
            RepeatParser(SymbolParser(SymbolsForTesting.A)),
            SymbolParser(SymbolsForTesting.B),
        ),
        SymbolsForTesting.A: LiteralParser("A"),
        SymbolsForTesting.B: LiteralParser("B"),
        SymbolsForTesting.C: LiteralParser("C"),
        SymbolsForTesting.D: LiteralParser("D"),
    }

    expected_ok = re.compile("A*B").fullmatch(code)

    try:
        new_parse_generic(rewrite_rules, code)
    except ParseError:
        assert not expected_ok
    else:
        assert expected_ok


@pytest.mark.parametrize("code", ["", "A", "B", "AB", "AAB", "AAAB", "BB", "ABB"])
def test_parser_repeat_symbols_with_at_least_one(code: str) -> None:
    rewrite_rules: Dict[IntEnum, Parser] = {
        SymbolsForTesting.ROOT: ConcatenationParser(
            RepeatParser(SymbolParser(SymbolsForTesting.A), min_repeats=1),
            SymbolParser(SymbolsForTesting.B),
        ),
        SymbolsForTesting.A: LiteralParser("A"),
        SymbolsForTesting.B: LiteralParser("B"),
        SymbolsForTesting.C: LiteralParser("C"),
        SymbolsForTesting.D: LiteralParser("D"),
    }

    expected_ok = re.compile("A+B").fullmatch(code)

    try:
        new_parse_generic(rewrite_rules, code)
    except ParseError:
        assert not expected_ok
    else:
        assert expected_ok


@pytest.mark.parametrize("code", ["", "AC", "ABC", "ABB", "CCB", "AAA"])
def test_parser_optional_symbol(code: str) -> None:
    rewrite_rules: Dict[IntEnum, Parser] = {
        SymbolsForTesting.ROOT: ConcatenationParser(
            SymbolParser(SymbolsForTesting.A),
            OptionalParser(SymbolParser(SymbolsForTesting.B)),
            SymbolParser(SymbolsForTesting.C),
        ),
        SymbolsForTesting.A: LiteralParser("A"),
        SymbolsForTesting.B: LiteralParser("B"),
        SymbolsForTesting.C: LiteralParser("C"),
        SymbolsForTesting.D: LiteralParser("D"),
    }

    expected_ok = re.compile("AB?C").fullmatch(code)

    try:
        new_parse_generic(rewrite_rules, code)
    except ParseError:
        assert not expected_ok
    else:
        assert expected_ok


def test_or_parser_longest() -> None:

    rewrite_rules: Dict[IntEnum, Parser] = {
        SymbolsForTesting.ROOT: OrParser(
            SymbolParser(SymbolsForTesting.A),
            SymbolParser(SymbolsForTesting.B),
        ),
        SymbolsForTesting.A: LiteralParser("A"),
        SymbolsForTesting.B: LiteralParser("AA"),
        SymbolsForTesting.C: LiteralParser("C"),
        SymbolsForTesting.D: LiteralParser("D"),
    }

    tree = new_parse_generic(rewrite_rules, "AA")

    assert tree.symbol_type == SymbolsForTesting.ROOT
    assert len(tree.children) == 1
    assert tree.children[0].symbol_type == SymbolsForTesting.B


def test_regex_parser_forbidden() -> None:

    rewrite_rules: Dict[IntEnum, Parser] = {
        SymbolsForTesting.ROOT: RegexBasedParser("AAB*", forbidden=["AA"]),
        SymbolsForTesting.A: LiteralParser("A"),
        SymbolsForTesting.B: LiteralParser("B"),
        SymbolsForTesting.C: LiteralParser("C"),
        SymbolsForTesting.D: LiteralParser("D"),
    }

    with pytest.raises(ParseError):
        new_parse_generic(rewrite_rules, "AA")


def test_symbol_parser_forward_symbol_type() -> None:

    rewrite_rules: Dict[IntEnum, Parser] = {
        SymbolsForTesting.ROOT: SymbolParser(SymbolsForTesting.A),
        SymbolsForTesting.A: OrParser(LiteralParser("AA"), LiteralParser("BB")),
        SymbolsForTesting.B: LiteralParser("B"),
        SymbolsForTesting.C: LiteralParser("C"),
        SymbolsForTesting.D: LiteralParser("D"),
    }

    tree = new_parse_generic(rewrite_rules, "AA")

    assert tree.symbol_type == SymbolsForTesting.ROOT


@pytest.mark.parametrize(
    ["code", "expected_match"],
    [
        ("", False),
        ("acd", True),
        ("bcd", True),
        ("acccd", True),
        ("bd", True),
        ("xacd", False),
        ("acdx", True),
    ],
)
def test_regex_parser(code: str, expected_match: bool) -> None:
    parser = RegexBasedParser("(a|b)c*d")

    try:
        parser.parse(code, 0)
    except InternalParseError:
        assert not expected_match
    else:
        assert expected_match


@pytest.mark.parametrize(
    ["offset", "expected_line_number", "expected_column_number", "expected_line"],
    [
        (0, 1, 1, "abc"),
        (2, 1, 3, "abc"),
        (3, 1, 4, "abc"),
        (4, 2, 1, "def"),
        (6, 2, 3, "def"),
        (7, 2, 4, "def"),
        (8, 3, 1, "ghi"),
        (10, 3, 3, "ghi"),
    ],
)
def test_humanize_parse_error(
    offset: int,
    expected_line_number: int,
    expected_column_number: int,
    expected_line: str,
) -> None:
    code = "abc\ndef\nghi"
    e = InternalParseError(offset, None)

    pe = humanize_parse_error(code, e)
    assert pe.line_number == expected_line_number
    assert pe.column_number == expected_column_number
    assert pe.line == expected_line


def test_parse_unhandled_symbol_type() -> None:
    rewrite_rules: Dict[IntEnum, Parser] = {
        SymbolsForTesting.ROOT: ConcatenationParser(
            SymbolParser(SymbolsForTesting.A),
            SymbolParser(SymbolsForTesting.B),
        ),
        SymbolsForTesting.A: LiteralParser("A"),
        SymbolsForTesting.B: LiteralParser("B"),
        SymbolsForTesting.C: LiteralParser("C"),
    }

    with pytest.raises(UnhandledSymbolType):
        new_parse_generic(rewrite_rules, "")


def test_parse_unexpected_symbol_type() -> None:
    class Dummy(IntEnum):
        Something = 999  # don't collide with value of SymbolsForTesting

    rewrite_rules: Dict[IntEnum, Parser] = {
        SymbolsForTesting.ROOT: ConcatenationParser(
            SymbolParser(SymbolsForTesting.A),
            SymbolParser(SymbolsForTesting.B),
        ),
        SymbolsForTesting.A: LiteralParser("A"),
        SymbolsForTesting.B: LiteralParser("B"),
        SymbolsForTesting.C: LiteralParser("C"),
        SymbolsForTesting.D: LiteralParser("D"),
        Dummy.Something: LiteralParser("S"),
    }

    with pytest.raises(UnexpectedSymbolType):
        new_parse_generic(rewrite_rules, "")


def test_parse_error_concatenation_parser() -> None:
    rewrite_rules: Dict[IntEnum, Parser] = {
        SymbolsForTesting.ROOT: ConcatenationParser(
            SymbolParser(SymbolsForTesting.A),
            SymbolParser(SymbolsForTesting.B),
        ),
        SymbolsForTesting.A: LiteralParser("A"),
        SymbolsForTesting.B: LiteralParser("B"),
        SymbolsForTesting.C: LiteralParser("C"),
        SymbolsForTesting.D: LiteralParser("D"),
    }

    with pytest.raises(ParseError) as e:
        new_parse_generic(rewrite_rules, "AC")

    assert "<source_file>:1:2" in str(e.value)


def test_parse_error_or_parser() -> None:
    rewrite_rules: Dict[IntEnum, Parser] = {
        SymbolsForTesting.ROOT: ConcatenationParser(
            SymbolParser(SymbolsForTesting.A),
            OrParser(
                SymbolParser(SymbolsForTesting.B),
                SymbolParser(SymbolsForTesting.C),
            ),
        ),
        SymbolsForTesting.A: LiteralParser("A"),
        SymbolsForTesting.B: LiteralParser("B"),
        SymbolsForTesting.C: LiteralParser("C"),
        SymbolsForTesting.D: LiteralParser("D"),
    }

    with pytest.raises(ParseError) as e:
        new_parse_generic(rewrite_rules, "AA")

    assert "<source_file>:1:2" in str(e.value)


def test_parse_error_regex_parser() -> None:
    rewrite_rules: Dict[IntEnum, Parser] = {
        SymbolsForTesting.ROOT: ConcatenationParser(
            SymbolParser(SymbolsForTesting.A), RegexBasedParser("(B|C)D")
        ),
        SymbolsForTesting.A: LiteralParser("A"),
        SymbolsForTesting.B: LiteralParser("B"),
        SymbolsForTesting.C: LiteralParser("C"),
        SymbolsForTesting.D: LiteralParser("D"),
    }

    with pytest.raises(ParseError) as e:
        new_parse_generic(rewrite_rules, "ABB")

    assert "<source_file>:1:2" in str(e.value)


def test_parse_error_repeat_parser() -> None:
    rewrite_rules: Dict[IntEnum, Parser] = {
        SymbolsForTesting.ROOT: ConcatenationParser(
            SymbolParser(SymbolsForTesting.A),
            RepeatParser(SymbolParser(SymbolsForTesting.B)),
            SymbolParser(SymbolsForTesting.C),
        ),
        SymbolsForTesting.A: LiteralParser("A"),
        SymbolsForTesting.B: LiteralParser("B"),
        SymbolsForTesting.C: LiteralParser("C"),
        SymbolsForTesting.D: LiteralParser("D"),
    }

    with pytest.raises(ParseError) as e:
        new_parse_generic(rewrite_rules, "ABBBD")

    assert "<source_file>:1:5" in str(e.value)


def test_parse_error_optional_parser() -> None:
    rewrite_rules: Dict[IntEnum, Parser] = {
        SymbolsForTesting.ROOT: ConcatenationParser(
            SymbolParser(SymbolsForTesting.A),
            OptionalParser(SymbolParser(SymbolsForTesting.B)),
            SymbolParser(SymbolsForTesting.C),
        ),
        SymbolsForTesting.A: LiteralParser("A"),
        SymbolsForTesting.B: LiteralParser("B"),
        SymbolsForTesting.C: LiteralParser("C"),
        SymbolsForTesting.D: LiteralParser("D"),
    }

    with pytest.raises(ParseError) as e:
        new_parse_generic(rewrite_rules, "AD")

    assert "<source_file>:1:2" in str(e.value)


def test_parse_error_literal_parser() -> None:
    rewrite_rules: Dict[IntEnum, Parser] = {
        SymbolsForTesting.ROOT: ConcatenationParser(
            LiteralParser("X"),
            LiteralParser("Y"),
        ),
        SymbolsForTesting.A: LiteralParser("A"),
        SymbolsForTesting.B: LiteralParser("B"),
        SymbolsForTesting.C: LiteralParser("C"),
        SymbolsForTesting.D: LiteralParser("D"),
    }

    with pytest.raises(ParseError) as e:
        new_parse_generic(rewrite_rules, "XA")

    assert "<source_file>:1:2" in str(e.value)


def test_regex_parser_value_error() -> None:
    with pytest.raises(ValueError):
        RegexBasedParser("^foo")  # argument should not start with '^'
