from parser.grammar import _grammar_expression, escape_string, unescape_string
from parser.parser import (
    ConcatenationParser,
    LiteralParser,
    OptionalParser,
    OrParser,
    Parser,
    RegexBasedParser,
    RepeatParser,
    SymbolParser,
)

import pytest

from tests.test_parser import SymbolsForTesting


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


@pytest.mark.parametrize(
    ["string", "expected_unescaped_string"],
    [
        ('""', ""),
        ('"foo bar"', "foo bar"),
        ('"foo\\r\\nbar"', "foo\r\nbar"),
        ('"a\\"b\\\\c\\\'"', "a\"b\\c'"),
    ],
)
def test_unescape_string(string: str, expected_unescaped_string: str) -> None:
    assert unescape_string(string) == expected_unescaped_string


@pytest.mark.parametrize(
    ["string"],
    [
        ("a",),
        ('"',),
        ('"a',),
    ],
)
def test_unescape_string_fail(string: str) -> None:
    with pytest.raises(ValueError):
        assert unescape_string(string)


@pytest.mark.parametrize(
    ["parser", "expected_grammar"],
    [
        (LiteralParser("A"), '"A"'),
        (LiteralParser("\n"), '"\\n"'),
        (ConcatenationParser(LiteralParser("A"), LiteralParser("B")), '"A" "B"'),
        (
            ConcatenationParser(
                SymbolParser(SymbolsForTesting.A), SymbolParser(SymbolsForTesting.B)
            ),
            "A B",
        ),
        (
            ConcatenationParser(
                LiteralParser("A"), OrParser(LiteralParser("B"), LiteralParser("C"))
            ),
            '"A" ("B" | "C")',
        ),
        (OrParser(LiteralParser("B"), LiteralParser("C")), '"B" | "C"'),
        (OptionalParser(LiteralParser("A")), '("A")?'),
        (RepeatParser(LiteralParser("A"), min_repeats=0), '("A")*'),
        (RepeatParser(LiteralParser("A"), min_repeats=1), '("A")+'),
        (RepeatParser(LiteralParser("A"), min_repeats=2), '("A"){2,...}'),
        (RegexBasedParser("^[ \n]*"), 'regex("[ \\n]*")'),
    ],
)
def test_grammar_expression(parser: Parser, expected_grammar: str) -> None:
    assert _grammar_expression(parser) == expected_grammar
