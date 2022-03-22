from enum import IntEnum, auto
from parser.parser.exceptions import (
    MissingNonTerminalTypes,
    MissingRootNonTerminalType,
    ParseError,
    UnexpectedNonTerminalTypes,
)
from parser.parser.models import (
    ConcatenationExpression,
    ConjunctionExpression,
    Expression,
    NonTerminalExpression,
    OptionalExpression,
    RepeatExpression,
    TerminalExpression,
    Tree,
)
from parser.parser.parser import Parser
from parser.tokenizer.models import Token
from typing import Dict, List

import pytest


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
        filename="foo.txt",
        tokens=tokens,
        code=code,
        non_terminal_rules=non_terminal_rules,
        pruned_non_terminals=set(),
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


def test_parser_conjunction_fail() -> None:
    tokens = [
        Token(DummyTerminal.C, 0, 1),
    ]

    code = "c"

    non_terminal_rules: Dict[IntEnum, Expression] = {
        DummyNonTerminal.ROOT: ConjunctionExpression(
            TerminalExpression(DummyTerminal.A),
            TerminalExpression(DummyTerminal.B),
        ),
        DummyNonTerminal.FOO: TerminalExpression(DummyTerminal.A),
    }

    parser = Parser(
        filename="foo.txt",
        tokens=tokens,
        code=code,
        non_terminal_rules=non_terminal_rules,
        pruned_non_terminals=set(),
        root_token="ROOT",
    )

    with pytest.raises(ParseError) as e:
        parser.parse()

    assert e.value == ParseError("foo.txt", code, 0)


def test_parser_conjunction() -> None:
    tokens = [
        Token(DummyTerminal.A, 0, 1),
    ]

    code = "a"

    non_terminal_rules: Dict[IntEnum, Expression] = {
        DummyNonTerminal.ROOT: ConjunctionExpression(
            TerminalExpression(DummyTerminal.A),
            TerminalExpression(DummyTerminal.B),
        ),
        DummyNonTerminal.FOO: TerminalExpression(DummyTerminal.A),
    }

    parser = Parser(
        filename="foo.txt",
        tokens=tokens,
        code=code,
        non_terminal_rules=non_terminal_rules,
        pruned_non_terminals=set(),
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

    code = "ab"

    non_terminal_rules: Dict[IntEnum, Expression] = {
        DummyNonTerminal.ROOT: ConcatenationExpression(
            TerminalExpression(DummyTerminal.A),
            TerminalExpression(DummyTerminal.B),
        ),
        DummyNonTerminal.FOO: TerminalExpression(DummyTerminal.A),
    }

    parser = Parser(
        filename="foo.txt",
        tokens=tokens,
        code=code,
        non_terminal_rules=non_terminal_rules,
        pruned_non_terminals=set(),
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
        filename="foo.txt",
        tokens=tokens,
        code=code,
        non_terminal_rules=non_terminal_rules,
        pruned_non_terminals=set(),
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
        filename="foo.txt",
        tokens=tokens,
        code=code,
        non_terminal_rules=non_terminal_rules,
        pruned_non_terminals=set(),
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


def test_parser_optinal() -> None:
    tokens = [
        Token(DummyTerminal.A, 0, 1),
    ]

    code = "a"

    non_terminal_rules: Dict[IntEnum, Expression] = {
        DummyNonTerminal.ROOT: OptionalExpression(TerminalExpression(DummyTerminal.A)),
        DummyNonTerminal.FOO: TerminalExpression(DummyTerminal.A),
    }

    parser = Parser(
        filename="foo.txt",
        tokens=tokens,
        code=code,
        non_terminal_rules=non_terminal_rules,
        pruned_non_terminals=set(),
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


def test_parser_optinal_fail() -> None:
    tokens = [
        Token(DummyTerminal.B, 0, 1),
    ]

    code = "b"

    non_terminal_rules: Dict[IntEnum, Expression] = {
        DummyNonTerminal.ROOT: ConcatenationExpression(
            OptionalExpression(TerminalExpression(DummyTerminal.A)),
            TerminalExpression(DummyTerminal.B),
        ),
        DummyNonTerminal.FOO: TerminalExpression(DummyTerminal.A),
    }

    parser = Parser(
        filename="foo.txt",
        tokens=tokens,
        code=code,
        non_terminal_rules=non_terminal_rules,
        pruned_non_terminals=set(),
        root_token="ROOT",
    )

    tree = parser.parse()

    assert tree == Tree(
        token_offset=0,
        token_count=1,
        token_type=DummyNonTerminal.ROOT,
        children=[
            Tree(token_offset=0, token_count=1, token_type=DummyTerminal.B, children=[])
        ],
    )


def test_parser_code_longer_than_root_expects() -> None:
    tokens = [
        Token(DummyTerminal.A, 0, 1),
        Token(DummyTerminal.A, 1, 1),
    ]

    code = "aa"

    non_terminal_rules: Dict[IntEnum, Expression] = {
        DummyNonTerminal.ROOT: ConcatenationExpression(
            TerminalExpression(DummyTerminal.A),
        ),
        DummyNonTerminal.FOO: TerminalExpression(DummyTerminal.A),
    }

    parser = Parser(
        filename="foo.txt",
        tokens=tokens,
        code=code,
        non_terminal_rules=non_terminal_rules,
        pruned_non_terminals=set(),
        root_token="ROOT",
    )

    with pytest.raises(ParseError) as e:
        parser.parse()

    assert e.value == ParseError("foo.txt", code, 1)


def test_parser_check_non_terminal_rules_missing() -> None:

    non_terminal_rules: Dict[IntEnum, Expression] = {
        DummyNonTerminal.ROOT: ConcatenationExpression(
            TerminalExpression(DummyTerminal.A),
        ),
    }

    parser = Parser(
        filename="foo.txt",
        tokens=[],
        code="",
        non_terminal_rules=non_terminal_rules,
        pruned_non_terminals=set(),
        root_token="ROOT",
    )

    with pytest.raises(MissingNonTerminalTypes) as e:
        parser.parse()

    assert e.value == MissingNonTerminalTypes({DummyNonTerminal.FOO})


def test_parser_check_non_terminal_rules_unexpected() -> None:
    class ExtraNonTerminals(IntEnum):
        BAR = 99

    non_terminal_rules: Dict[IntEnum, Expression] = {
        DummyNonTerminal.ROOT: TerminalExpression(DummyTerminal.A),
        DummyNonTerminal.FOO: TerminalExpression(DummyTerminal.A),
        ExtraNonTerminals.BAR: TerminalExpression(DummyTerminal.A),
    }

    parser = Parser(
        filename="foo.txt",
        tokens=[],
        code="",
        non_terminal_rules=non_terminal_rules,
        pruned_non_terminals=set(),
        root_token="ROOT",
    )

    with pytest.raises(UnexpectedNonTerminalTypes) as e:
        parser.parse()

    assert e.value == UnexpectedNonTerminalTypes({ExtraNonTerminals.BAR})


def test_parser_check_non_terminal_rules_without_root() -> None:
    class NonTerminalsWithoutRoot(IntEnum):
        BAZ = 100

    non_terminal_rules: Dict[IntEnum, Expression] = {
        NonTerminalsWithoutRoot.BAZ: TerminalExpression(DummyTerminal.A),
    }

    parser = Parser(
        filename="foo.txt",
        tokens=[],
        code="",
        non_terminal_rules=non_terminal_rules,
        pruned_non_terminals=set(),
        root_token="ROOT",
    )

    with pytest.raises(MissingRootNonTerminalType):
        parser.parse()


def test_parser_pruning_non_terminals() -> None:

    non_terminal_rules: Dict[IntEnum, Expression] = {
        DummyNonTerminal.ROOT: ConcatenationExpression(
            TerminalExpression(DummyTerminal.A),
            NonTerminalExpression(DummyNonTerminal.FOO),
            TerminalExpression(DummyTerminal.A),
        ),
        DummyNonTerminal.FOO: TerminalExpression(DummyTerminal.B),
    }

    tokens = [
        Token(DummyTerminal.A, 0, 1),
        Token(DummyTerminal.B, 1, 1),
        Token(DummyTerminal.A, 2, 1),
    ]

    code = "aba"

    parser = Parser(
        filename="foo.txt",
        tokens=tokens,
        code=code,
        non_terminal_rules=non_terminal_rules,
        pruned_non_terminals={DummyNonTerminal.FOO},
        root_token="ROOT",
    )

    tree = parser.parse()

    assert tree == Tree(
        token_offset=0,
        token_count=3,
        token_type=DummyNonTerminal.ROOT,
        children=[
            Tree(
                token_offset=0, token_count=1, token_type=DummyTerminal.A, children=[]
            ),
            Tree(
                token_offset=2, token_count=1, token_type=DummyTerminal.A, children=[]
            ),
        ],
    )


def test_parser_at_least_once_at_end_of_input() -> None:
    tokens = [
        Token(DummyTerminal.A, 0, 1),
    ]

    code = "a"

    non_terminal_rules: Dict[IntEnum, Expression] = {
        DummyNonTerminal.ROOT: ConcatenationExpression(
            TerminalExpression(DummyTerminal.A),
            RepeatExpression(TerminalExpression(DummyTerminal.A)),
        ),
        DummyNonTerminal.FOO: TerminalExpression(DummyTerminal.A),
    }

    parser = Parser(
        filename="foo.txt",
        tokens=tokens,
        code=code,
        non_terminal_rules=non_terminal_rules,
        pruned_non_terminals=set(),
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


def test_parser_optional_at_end_of_input() -> None:
    tokens = [
        Token(DummyTerminal.A, 0, 1),
    ]

    code = "a"

    non_terminal_rules: Dict[IntEnum, Expression] = {
        DummyNonTerminal.ROOT: ConcatenationExpression(
            TerminalExpression(DummyTerminal.A),
            OptionalExpression(TerminalExpression(DummyTerminal.A)),
        ),
        DummyNonTerminal.FOO: TerminalExpression(DummyTerminal.A),
    }

    parser = Parser(
        filename="foo.txt",
        tokens=tokens,
        code=code,
        non_terminal_rules=non_terminal_rules,
        pruned_non_terminals=set(),
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


def test_parser_parse_error() -> None:
    tokens = [
        Token(DummyTerminal.A, 0, 3),
        Token(DummyTerminal.B, 3, 3),
        Token(DummyTerminal.C, 6, 3),
    ]

    code = "aaabbbccc"

    non_terminal_rules: Dict[IntEnum, Expression] = {
        DummyNonTerminal.ROOT: ConcatenationExpression(
            TerminalExpression(DummyTerminal.A),
            TerminalExpression(DummyTerminal.B),
        ),
        DummyNonTerminal.FOO: TerminalExpression(DummyTerminal.A),
    }

    parser = Parser(
        filename="foo.txt",
        tokens=tokens,
        code=code,
        non_terminal_rules=non_terminal_rules,
        pruned_non_terminals=set(),
        root_token="ROOT",
    )

    with pytest.raises(ParseError) as e:
        parser.parse()

    assert "Parse error at foo.txt:1:7" in str(e.value)


def test_parser_longer_than_root_expects() -> None:
    tokens = [
        Token(DummyTerminal.A, 0, 1),
    ]

    code = "a"

    non_terminal_rules: Dict[IntEnum, Expression] = {
        DummyNonTerminal.ROOT: ConcatenationExpression(
            TerminalExpression(DummyTerminal.A),
            TerminalExpression(DummyTerminal.B),
        ),
        DummyNonTerminal.FOO: TerminalExpression(DummyTerminal.A),
    }

    parser = Parser(
        filename="foo.txt",
        tokens=tokens,
        code=code,
        non_terminal_rules=non_terminal_rules,
        pruned_non_terminals=set(),
        root_token="ROOT",
    )

    with pytest.raises(ParseError) as e:
        parser.parse()

    assert "Parse error at foo.txt:1:2" in str(e.value)


def test_parser_empty_file_fail() -> None:
    tokens: List[Token] = []

    code = ""

    non_terminal_rules: Dict[IntEnum, Expression] = {
        DummyNonTerminal.ROOT: TerminalExpression(DummyTerminal.A),
        DummyNonTerminal.FOO: TerminalExpression(DummyTerminal.A),
    }

    parser = Parser(
        filename="foo.txt",
        tokens=tokens,
        code=code,
        non_terminal_rules=non_terminal_rules,
        pruned_non_terminals=set(),
        root_token="ROOT",
    )

    with pytest.raises(ParseError) as e:
        parser.parse()

    assert "Parse error at foo.txt:1:1" in str(e.value)


def test_parser_empty_file_ok() -> None:
    tokens: List[Token] = []

    code = ""

    non_terminal_rules: Dict[IntEnum, Expression] = {
        DummyNonTerminal.ROOT: RepeatExpression(TerminalExpression(DummyTerminal.A)),
        DummyNonTerminal.FOO: TerminalExpression(DummyTerminal.A),
    }

    parser = Parser(
        filename="foo.txt",
        tokens=tokens,
        code=code,
        non_terminal_rules=non_terminal_rules,
        pruned_non_terminals=set(),
        root_token="ROOT",
    )

    tree = parser.parse()

    assert tree == Tree(
        token_offset=0, token_count=0, token_type=DummyNonTerminal.ROOT, children=[]
    )
