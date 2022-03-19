from enum import IntEnum, auto
from parser.tokenizer.exceptions import (
    MissingTerminalTypes,
    TokenizerError,
    UnexpectedTerminalTypes,
)
from parser.tokenizer.models import Literal, Regex, Token, TokenDescriptor
from parser.tokenizer.tokenizer import Tokenizer
from typing import List

import pytest


class DummyTerminal(IntEnum):
    A = auto()
    B = auto()
    C = auto()


def test_check_terminal_rules_extra() -> None:
    class Foo(IntEnum):
        Extra = 99

    terminal_rules: List[TokenDescriptor] = [
        Literal(DummyTerminal.A, "a"),
        Literal(DummyTerminal.B, "b"),
        Literal(DummyTerminal.C, "c"),
        Literal(Foo.Extra, "d"),
    ]

    with pytest.raises(UnexpectedTerminalTypes) as e:
        Tokenizer("foo.txt", "", terminal_rules, set()).tokenize()

    assert str(e.value) == "Terminal rewrite rules contain 1 unexpected types: Extra"


def test_check_terminal_rules_missing() -> None:
    terminal_rules: List[TokenDescriptor] = [
        Literal(DummyTerminal.A, "a"),
        Literal(DummyTerminal.B, "b"),
    ]

    with pytest.raises(MissingTerminalTypes) as e:
        Tokenizer("foo.txt", "", terminal_rules, set()).tokenize()

    assert str(e.value) == "Terminal rewrite rules has 1 missing types: C"


def test_tokenize_simple() -> None:
    code = "ab"
    terminal_rules: List[TokenDescriptor] = [
        Literal(DummyTerminal.A, "a"),
        Literal(DummyTerminal.B, "b"),
        Literal(DummyTerminal.C, "c"),
    ]

    tokens = Tokenizer("foo.txt", code, terminal_rules, set()).tokenize()

    assert tokens == [
        Token(DummyTerminal.A, 0, 1),
        Token(DummyTerminal.B, 1, 1),
    ]


def test_tokenize_regex() -> None:
    code = "aaaab"
    terminal_rules: List[TokenDescriptor] = [
        Regex(DummyTerminal.A, "a*"),
        Literal(DummyTerminal.B, "b"),
        Literal(DummyTerminal.C, "c"),
    ]

    tokens = Tokenizer("foo.txt", code, terminal_rules, set()).tokenize()

    assert tokens == [
        Token(DummyTerminal.A, 0, 4),
        Token(DummyTerminal.B, 4, 1),
    ]


def test_tokenize_fail() -> None:
    code = "aaaabx"
    terminal_rules: List[TokenDescriptor] = [
        Regex(DummyTerminal.A, "a*"),
        Literal(DummyTerminal.B, "b"),
        Literal(DummyTerminal.C, "c"),
    ]

    with pytest.raises(TokenizerError) as e:
        Tokenizer("foo.txt", code, terminal_rules, set()).tokenize()

    assert e.value.filename == "foo.txt"
    assert e.value.code == code
    assert e.value.offset == 5


def test_tokenize_regex_fail() -> None:
    code = "b"
    terminal_rules: List[TokenDescriptor] = [
        Regex(DummyTerminal.A, "a+"),
        Literal(DummyTerminal.B, "b"),
        Literal(DummyTerminal.C, "c"),
    ]

    tokens = Tokenizer("foo.txt", code, terminal_rules, set()).tokenize()

    assert tokens == [
        Token(DummyTerminal.B, 0, 1),
    ]


def test_tokenize_prune() -> None:
    code = " \n a\n b\n "
    terminal_rules: List[TokenDescriptor] = [
        Literal(DummyTerminal.A, "a"),
        Literal(DummyTerminal.B, "b"),
        Regex(DummyTerminal.C, "[ \n]*"),
    ]

    tokens = Tokenizer("foo.txt", code, terminal_rules, {DummyTerminal.C}).tokenize()

    assert tokens == [
        Token(DummyTerminal.A, 3, 1),
        Token(DummyTerminal.B, 6, 1),
    ]
