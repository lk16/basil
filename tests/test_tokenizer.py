from enum import IntEnum, auto
from parser.exceptions import InternalParseError
from parser.tokenizer import RegexTokenizer, Token, _check_terminal_rules, tokenize
from typing import List, Set, Tuple

import pytest


def test_tokenize_simple() -> None:
    class DummyEnum(IntEnum):
        A = auto()
        B = auto()

    code = "ab"
    terminal_rules: List[Tuple[IntEnum, RegexTokenizer]] = [
        (DummyEnum.A, RegexTokenizer("a")),
        (DummyEnum.B, RegexTokenizer("b")),
    ]

    tokens = tokenize(code, terminal_rules, set())

    assert tokens == [
        Token(DummyEnum.A, 0, 1),
        Token(DummyEnum.B, 1, 1),
    ]

    assert tokens[0].value(code) == "a"
    assert tokens[1].value(code) == "b"


def test_check_terminal_rules_missing() -> None:
    class DummyEnum(IntEnum):
        A = auto()
        B = auto()

    terminal_rules: List[Tuple[IntEnum, RegexTokenizer]] = [
        (DummyEnum.A, RegexTokenizer("a")),
    ]

    with pytest.raises(ValueError):
        _check_terminal_rules(terminal_rules)


def test_check_terminal_rules_duplicate() -> None:
    class DummyEnum(IntEnum):
        A = auto()
        B = auto()

    terminal_rules: List[Tuple[IntEnum, RegexTokenizer]] = [
        (DummyEnum.A, RegexTokenizer("a")),
        (DummyEnum.A, RegexTokenizer("a")),
        (DummyEnum.B, RegexTokenizer("b")),
    ]

    with pytest.raises(ValueError):
        _check_terminal_rules(terminal_rules)


def test_regex_tokenizer_with_caret() -> None:
    with pytest.raises(ValueError):
        RegexTokenizer("^foo")


def test_tokenize_empty_match() -> None:
    class DummyEnum(IntEnum):
        A = auto()
        B = auto()

    code = "b"
    terminal_rules: List[Tuple[IntEnum, RegexTokenizer]] = [
        (DummyEnum.A, RegexTokenizer("a*")),
        (DummyEnum.B, RegexTokenizer("b")),
    ]

    tokens = tokenize(code, terminal_rules, set())

    assert tokens == [
        Token(DummyEnum.B, 0, 1),
    ]

    assert tokens[0].value(code) == "b"


def test_tokenize_pruned_terminal() -> None:
    class DummyEnum(IntEnum):
        A = auto()
        B = auto()
        C = auto()

    code = "abc"
    terminal_rules: List[Tuple[IntEnum, RegexTokenizer]] = [
        (DummyEnum.A, RegexTokenizer("a")),
        (DummyEnum.B, RegexTokenizer("b")),
        (DummyEnum.C, RegexTokenizer("c")),
    ]

    pruned_terminals: Set[IntEnum] = {DummyEnum.B}

    tokens = tokenize(code, terminal_rules, pruned_terminals)

    assert tokens == [
        Token(DummyEnum.A, 0, 1),
        Token(DummyEnum.C, 2, 1),
    ]

    assert tokens[0].value(code) == "a"
    assert tokens[1].value(code) == "c"


def test_tokenize_fail() -> None:
    class DummyEnum(IntEnum):
        A = auto()
        B = auto()
        C = auto()

    code = "d"
    terminal_rules: List[Tuple[IntEnum, RegexTokenizer]] = [
        (DummyEnum.A, RegexTokenizer("a")),
        (DummyEnum.B, RegexTokenizer("b")),
        (DummyEnum.C, RegexTokenizer("c")),
    ]

    pruned_terminals: Set[IntEnum] = {DummyEnum.B}

    with pytest.raises(InternalParseError):
        tokenize(code, terminal_rules, pruned_terminals)
