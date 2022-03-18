from enum import IntEnum, auto
from parser.exceptions import InternalParseError
from parser.tokenizer.models import Literal, Regex, Token, TokenDescriptor
from parser.tokenizer.tokenizer import Tokenizer
from typing import List

import pytest


class DummyTokenType(IntEnum):
    A = auto()
    B = auto()
    C = auto()


def test_check_terminal_rules_extra() -> None:
    class Foo(IntEnum):
        Extra = 99

    terminal_rules: List[TokenDescriptor] = [
        Literal(DummyTokenType.A, "a"),
        Literal(DummyTokenType.B, "b"),
        Literal(DummyTokenType.C, "c"),
        Literal(Foo.Extra, "d"),
    ]

    with pytest.raises(ValueError) as e:
        Tokenizer("", terminal_rules, set()).tokenize()

    assert str(e.value) == "Terminal rules has unexpected values: Foo.Extra"


def test_check_terminal_rules_missing() -> None:
    terminal_rules: List[TokenDescriptor] = [
        Literal(DummyTokenType.A, "a"),
        Literal(DummyTokenType.B, "b"),
    ]

    with pytest.raises(ValueError) as e:
        Tokenizer("", terminal_rules, set()).tokenize()

    assert str(e.value) == "Terminal rules has missing values: DummyTokenType.C"


def test_tokenize_simple() -> None:
    code = "ab"
    terminal_rules: List[TokenDescriptor] = [
        Literal(DummyTokenType.A, "a"),
        Literal(DummyTokenType.B, "b"),
        Literal(DummyTokenType.C, "c"),
    ]

    tokens = Tokenizer(code, terminal_rules, set()).tokenize()

    assert tokens == [
        Token(DummyTokenType.A, 0, 1),
        Token(DummyTokenType.B, 1, 1),
    ]


def test_tokenize_regex() -> None:
    code = "aaaab"
    terminal_rules: List[TokenDescriptor] = [
        Regex(DummyTokenType.A, "a*"),
        Literal(DummyTokenType.B, "b"),
        Literal(DummyTokenType.C, "c"),
    ]

    tokens = Tokenizer(code, terminal_rules, set()).tokenize()

    assert tokens == [
        Token(DummyTokenType.A, 0, 4),
        Token(DummyTokenType.B, 4, 1),
    ]


def test_tokenize_fail() -> None:
    code = "aaaabx"
    terminal_rules: List[TokenDescriptor] = [
        Regex(DummyTokenType.A, "a*"),
        Literal(DummyTokenType.B, "b"),
        Literal(DummyTokenType.C, "c"),
    ]

    with pytest.raises(InternalParseError) as e:
        Tokenizer(code, terminal_rules, set()).tokenize()

    assert e.value.token_offset == 5


def test_tokenize_regex_fail() -> None:
    code = "b"
    terminal_rules: List[TokenDescriptor] = [
        Regex(DummyTokenType.A, "a+"),
        Literal(DummyTokenType.B, "b"),
        Literal(DummyTokenType.C, "c"),
    ]

    tokens = Tokenizer(code, terminal_rules, set()).tokenize()

    assert tokens == [
        Token(DummyTokenType.B, 0, 1),
    ]


def test_tokenize_prune() -> None:
    code = " \n a\n b\n "
    terminal_rules: List[TokenDescriptor] = [
        Literal(DummyTokenType.A, "a"),
        Literal(DummyTokenType.B, "b"),
        Regex(DummyTokenType.C, "[ \n]*"),
    ]

    tokens = Tokenizer(code, terminal_rules, {DummyTokenType.C}).tokenize()

    assert tokens == [
        Token(DummyTokenType.A, 3, 1),
        Token(DummyTokenType.B, 6, 1),
    ]
