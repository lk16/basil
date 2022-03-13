from enum import IntEnum, auto
from parser.exceptions import ParseError
from parser.parser import Parser, TerminalParser, parse_generic
from parser.tokenizer import Token
from typing import Dict, List

import pytest


class DummyTerminal(IntEnum):
    A = auto()
    B = auto()
    C = auto()


def test_parse_terminal() -> None:
    class DummyNonTerminal(IntEnum):
        ROOT = auto()

    non_terminal_rules: Dict[IntEnum, Parser] = {
        DummyNonTerminal.ROOT: TerminalParser(DummyTerminal.A)
    }

    tokens = [
        Token(DummyTerminal.A, 0, 1),
    ]

    code = "a"

    tree = parse_generic(non_terminal_rules, tokens, code, set(), set(), "ROOT")

    assert len(tree.children) == 0
    assert tree.token_count == 1
    assert tree.token_offset == 0
    assert tree.token_type == DummyNonTerminal.ROOT
    assert tree.value(tokens, code) == "a"


@pytest.mark.parametrize(
    ["code", "tokens"],
    [
        ("", []),
        ("aa", [Token(DummyTerminal.A, 0, 1), Token(DummyTerminal.A, 1, 1)]),
        (
            "aaa",
            [
                Token(DummyTerminal.A, 0, 1),
                Token(DummyTerminal.A, 1, 1),
                Token(DummyTerminal.A, 2, 1),
            ],
        ),
        ("ab", [Token(DummyTerminal.A, 0, 1), Token(DummyTerminal.B, 1, 1)]),
        ("b", [Token(DummyTerminal.B, 0, 1)]),
    ],
)
def test_parse_terminal_fail(code: str, tokens: List[Token]) -> None:
    class DummyNonTerminal(IntEnum):
        ROOT = auto()

    non_terminal_rules: Dict[IntEnum, Parser] = {
        DummyNonTerminal.ROOT: TerminalParser(DummyTerminal.A)
    }

    with pytest.raises(ParseError):
        parse_generic(non_terminal_rules, tokens, code, set(), set(), "ROOT")
