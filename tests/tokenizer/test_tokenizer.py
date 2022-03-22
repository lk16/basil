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
        Tokenizer(
            filename="foo.txt",
            code="",
            terminal_rules=terminal_rules,
            pruned_terminals=set(),
        ).tokenize()

    assert str(e.value) == "Terminal rewrite rules contain 1 unexpected types: Extra"


def test_check_terminal_rules_missing() -> None:
    terminal_rules: List[TokenDescriptor] = [
        Literal(DummyTerminal.A, "a"),
        Literal(DummyTerminal.B, "b"),
    ]

    with pytest.raises(MissingTerminalTypes) as e:
        Tokenizer(
            filename="foo.txt",
            code="",
            terminal_rules=terminal_rules,
            pruned_terminals=set(),
        ).tokenize()

    assert str(e.value) == "Terminal rewrite rules has 1 missing types: C"


def test_tokenize_simple() -> None:
    code = "ab"
    terminal_rules: List[TokenDescriptor] = [
        Literal(DummyTerminal.A, "a"),
        Literal(DummyTerminal.B, "b"),
        Literal(DummyTerminal.C, "c"),
    ]

    tokens = Tokenizer(
        filename="foo.txt",
        code=code,
        terminal_rules=terminal_rules,
        pruned_terminals=set(),
    ).tokenize()

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

    tokens = Tokenizer(
        filename="foo.txt",
        code=code,
        terminal_rules=terminal_rules,
        pruned_terminals=set(),
    ).tokenize()

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
        Tokenizer(
            filename="foo.txt",
            code=code,
            terminal_rules=terminal_rules,
            pruned_terminals=set(),
        ).tokenize()

    assert e.value == TokenizerError("foo.txt", code, 5)


def test_tokenize_regex_fail() -> None:
    code = "b"
    terminal_rules: List[TokenDescriptor] = [
        Regex(DummyTerminal.A, "a+"),
        Literal(DummyTerminal.B, "b"),
        Literal(DummyTerminal.C, "c"),
    ]

    tokens = Tokenizer(
        filename="foo.txt",
        code=code,
        terminal_rules=terminal_rules,
        pruned_terminals=set(),
    ).tokenize()

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

    tokens = Tokenizer(
        filename="foo.txt",
        code=code,
        terminal_rules=terminal_rules,
        pruned_terminals={DummyTerminal.C},
    ).tokenize()

    assert tokens == [
        Token(DummyTerminal.A, 3, 1),
        Token(DummyTerminal.B, 6, 1),
    ]


def test_tokenize_error_message() -> None:
    code = "aaabbbccc"
    terminal_rules: List[TokenDescriptor] = [
        Literal(DummyTerminal.A, "aaa"),
        Literal(DummyTerminal.B, "bbb"),
        Regex(DummyTerminal.C, "[ \n]*"),
    ]

    with pytest.raises(TokenizerError) as e:
        Tokenizer(
            filename="foo.txt",
            code=code,
            terminal_rules=terminal_rules,
            pruned_terminals=set(),
        ).tokenize()

    assert "Tokenize error at foo.txt:1:7" in str(e.value)
