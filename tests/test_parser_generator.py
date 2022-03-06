from parser.grammar.parser import (
    HARD_PRUNED_SYMBOL_TYPES,
    REWRITE_RULES,
    SOFT_PRUNED_SYMBOL_TYPES,
    SymbolType,
)
from parser.parser import parse_generic
from parser.parser_generator import tree_to_python_parser_expression
from parser.tree import Tree
from typing import List, Optional

import pytest


# shortcut for tests
def make_tree(
    *, o: int = 0, l: int = 1, c: Optional[List[Tree]] = None, s: Optional[str] = None
) -> Tree:
    children = c or []

    if s:
        symbol_type = SymbolType[s]
    else:
        symbol_type = None

    offset = o
    length = l

    return Tree(offset, length, symbol_type, children)


@pytest.mark.parametrize(
    ["code", "expected_python_expr"],
    [
        ('"foo"', 'LiteralParser("foo")'),
        ('"\\n"', 'LiteralParser("\\n")'),
        (
            'regex("[0-9]+")',
            'RegexBasedParser("[0-9]+")',
        ),
        (
            'regex("A") regex("B")',
            'ConcatenationParser(RegexBasedParser("A"), RegexBasedParser("B"))',
        ),
        (
            'regex("A") regex("B") regex("C")',
            'ConcatenationParser(RegexBasedParser("A"), RegexBasedParser("B"), RegexBasedParser("C"))',
        ),
        (
            '("foo")',
            'LiteralParser("foo")',
        ),
        (
            '("foo")?',
            'OptionalParser(LiteralParser("foo"))',
        ),
        (
            "(A)? B",
            "ConcatenationParser(OptionalParser(SymbolParser(SymbolType.A)), SymbolParser(SymbolType.B))",
        ),
        (
            "(A)? (B)?",
            "ConcatenationParser(OptionalParser(SymbolParser(SymbolType.A)), OptionalParser(SymbolParser(SymbolType.B)))",
        ),
        (
            "(A)? (B)? (C)?",
            "ConcatenationParser(OptionalParser(SymbolParser(SymbolType.A)), OptionalParser(SymbolParser(SymbolType.B)), OptionalParser(SymbolParser(SymbolType.C)))",
        ),
        (
            '("foo")*',
            'RepeatParser(LiteralParser("foo"))',
        ),
        (
            '("foo")+',
            'RepeatParser(LiteralParser("foo"), min_repeats=1)',
        ),
        (
            '("foo"){3,...}',
            'RepeatParser(LiteralParser("foo"), min_repeats=3)',
        ),
        (
            "A",
            "SymbolParser(SymbolType.A)",
        ),
        (
            "A B",
            "ConcatenationParser(SymbolParser(SymbolType.A), SymbolParser(SymbolType.B))",
        ),
        (
            "(A) B",
            "ConcatenationParser(SymbolParser(SymbolType.A), SymbolParser(SymbolType.B))",
        ),
        (
            "A (B)",
            "ConcatenationParser(SymbolParser(SymbolType.A), SymbolParser(SymbolType.B))",
        ),
        (
            "(A) (B)",
            "ConcatenationParser(SymbolParser(SymbolType.A), SymbolParser(SymbolType.B))",
        ),
        (
            "(A)+ (B)+",
            "ConcatenationParser(RepeatParser(SymbolParser(SymbolType.A), min_repeats=1), RepeatParser(SymbolParser(SymbolType.B), min_repeats=1))",
        ),
        (
            "(A)+ (B)+ (C)+",
            "ConcatenationParser(RepeatParser(SymbolParser(SymbolType.A), min_repeats=1), RepeatParser(SymbolParser(SymbolType.B), min_repeats=1), RepeatParser(SymbolParser(SymbolType.C), min_repeats=1))",
        ),
        (
            "A B C",
            "ConcatenationParser(SymbolParser(SymbolType.A), SymbolParser(SymbolType.B), SymbolParser(SymbolType.C))",
        ),
        (
            "A | B",
            "OrParser(SymbolParser(SymbolType.A), SymbolParser(SymbolType.B))",
        ),
        (
            "A | B | C",
            "OrParser(SymbolParser(SymbolType.A), SymbolParser(SymbolType.B), SymbolParser(SymbolType.C))",
        ),
    ],
)
def test_tree_to_python_parser_expression(code: str, expected_python_expr: str) -> None:
    code = f"DUMMY_TOKEN = {code}\n"

    root_tree = parse_generic(
        REWRITE_RULES,
        code,
        HARD_PRUNED_SYMBOL_TYPES,
        SOFT_PRUNED_SYMBOL_TYPES,
        "ROOT",
    )

    tree = root_tree[0][1]

    python_expr = tree_to_python_parser_expression(tree, code, None)
    assert python_expr == expected_python_expr
