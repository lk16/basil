from enum import IntEnum, auto
from parser.parser.models import (
    ConcatenationExpression,
    ConjunctionExpression,
    Expression,
    NonTerminalExpression,
    RepeatExpression,
    TerminalExpression,
    Tree,
)
from parser.parser.parser import Parser
from parser.tokenizer.models import Token
from typing import Dict


class DummyTerminal(IntEnum):
    A = auto()
    B = auto()
    C = auto()


class DummyNonTerminal(IntEnum):
    ROOT = auto()
    FOO = auto()


def test_parser_repeat() -> None:
    tokens = [
        Token(DummyTerminal.A, 0, 1),
        Token(DummyTerminal.A, 1, 1),
        Token(DummyTerminal.A, 2, 1),
    ]

    code = "abc"

    non_terminal_rules: Dict[IntEnum, Expression] = {
        DummyNonTerminal.ROOT: RepeatExpression(
            TerminalExpression(DummyTerminal.A),
        ),
        DummyNonTerminal.FOO: TerminalExpression(DummyTerminal.A),
    }

    parser = Parser(
        tokens=tokens,
        code=code,
        non_terminal_rules=non_terminal_rules,
        prune_soft_tokens=set(),
        prune_hard_tokens=set(),
        root_token="ROOT",
    )

    tree = parser.parse()

    assert tree == Tree(
        token_type=DummyNonTerminal.ROOT,
        token_offset=0,
        token_count=3,
        children=[
            Tree(
                token_offset=0, token_count=1, token_type=DummyTerminal.A, children=[]
            ),
            Tree(
                token_offset=1, token_count=1, token_type=DummyTerminal.A, children=[]
            ),
            Tree(
                token_offset=2, token_count=1, token_type=DummyTerminal.A, children=[]
            ),
        ],
    )


def test_parser_conjunction() -> None:
    tokens = [
        Token(DummyTerminal.A, 0, 1),
    ]

    code = "abc"

    non_terminal_rules: Dict[IntEnum, Expression] = {
        DummyNonTerminal.ROOT: ConjunctionExpression(
            TerminalExpression(DummyTerminal.A),
            TerminalExpression(DummyTerminal.B),
        ),
        DummyNonTerminal.FOO: TerminalExpression(DummyTerminal.A),
    }

    parser = Parser(
        tokens=tokens,
        code=code,
        non_terminal_rules=non_terminal_rules,
        prune_soft_tokens=set(),
        prune_hard_tokens=set(),
        root_token="ROOT",
    )

    tree = parser.parse()

    assert tree == Tree(
        token_type=DummyNonTerminal.ROOT,
        token_offset=0,
        token_count=1,
        children=[
            Tree(
                token_offset=0, token_count=1, token_type=DummyTerminal.A, children=[]
            ),
        ],
    )


def test_parser_concatenation() -> None:
    tokens = [
        Token(DummyTerminal.A, 0, 1),
        Token(DummyTerminal.B, 1, 1),
    ]

    code = "abc"

    non_terminal_rules: Dict[IntEnum, Expression] = {
        DummyNonTerminal.ROOT: ConcatenationExpression(
            TerminalExpression(DummyTerminal.A),
            TerminalExpression(DummyTerminal.B),
        ),
        DummyNonTerminal.FOO: TerminalExpression(DummyTerminal.A),
    }

    parser = Parser(
        tokens=tokens,
        code=code,
        non_terminal_rules=non_terminal_rules,
        prune_soft_tokens=set(),
        prune_hard_tokens=set(),
        root_token="ROOT",
    )

    tree = parser.parse()

    assert tree == Tree(
        token_type=DummyNonTerminal.ROOT,
        token_offset=0,
        token_count=2,
        children=[
            Tree(
                token_offset=0, token_count=1, token_type=DummyTerminal.A, children=[]
            ),
            Tree(
                token_offset=1, token_count=1, token_type=DummyTerminal.B, children=[]
            ),
        ],
    )


def test_parser_terminal() -> None:
    tokens = [
        Token(DummyTerminal.A, 0, 1),
    ]

    code = "a"

    non_terminal_rules: Dict[IntEnum, Expression] = {
        DummyNonTerminal.ROOT: TerminalExpression(DummyTerminal.A),
        DummyNonTerminal.FOO: TerminalExpression(DummyTerminal.A),
    }

    parser = Parser(
        tokens=tokens,
        code=code,
        non_terminal_rules=non_terminal_rules,
        prune_soft_tokens=set(),
        prune_hard_tokens=set(),
        root_token="ROOT",
    )

    tree = parser.parse()

    assert tree == Tree(
        token_offset=0, token_count=1, token_type=DummyTerminal.A, children=[]
    )


def test_parser_non_terminal() -> None:
    tokens = [
        Token(DummyTerminal.A, 0, 1),
    ]

    code = "a"

    non_terminal_rules: Dict[IntEnum, Expression] = {
        DummyNonTerminal.ROOT: NonTerminalExpression(DummyNonTerminal.FOO),
        DummyNonTerminal.FOO: TerminalExpression(DummyTerminal.A),
    }

    parser = Parser(
        tokens=tokens,
        code=code,
        non_terminal_rules=non_terminal_rules,
        prune_soft_tokens=set(),
        prune_hard_tokens=set(),
        root_token="ROOT",
    )

    tree = parser.parse()

    assert tree == Tree(
        token_offset=0,
        token_count=1,
        token_type=DummyNonTerminal.ROOT,
        children=[
            Tree(token_offset=0, token_count=1, token_type=DummyTerminal.A, children=[])
        ],
    )
