from parser.grammar.parser import SymbolType
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
    ["tree", "code", "expected_python_expr"],
    [
        (make_tree(s="LITERAL_EXPRESSION", l=5), '"foo"', 'LiteralParser("foo")'),
        (make_tree(s="LITERAL_EXPRESSION", l=5), '"\\n"', 'LiteralParser("\\n")'),
        (
            make_tree(s="REGEX_EXPRESSION", c=[make_tree(o=6, l=8)]),
            'regex("[0-9]+")',
            'RegexBasedParser("[0-9]+")',
        ),
        (
            make_tree(
                s="BRACKET_EXPRESSION",
                c=[make_tree(o=1, l=5, s="LITERAL_EXPRESSION"), make_tree(o=6, l=1)],
            ),
            '("foo")',
            'LiteralParser("foo")',
        ),
        (
            make_tree(
                s="BRACKET_EXPRESSION",
                c=[make_tree(o=1, l=5, s="LITERAL_EXPRESSION"), make_tree(o=6, l=2)],
            ),
            '("foo")?',
            'OptionalParser(LiteralParser("foo"))',
        ),
        (
            make_tree(
                s="BRACKET_EXPRESSION",
                c=[make_tree(o=1, l=5, s="LITERAL_EXPRESSION"), make_tree(o=6, l=2)],
            ),
            '("foo")*',
            'RepeatParser(LiteralParser("foo"))',
        ),
        (
            make_tree(
                s="BRACKET_EXPRESSION",
                c=[make_tree(o=1, l=5, s="LITERAL_EXPRESSION"), make_tree(o=6, l=2)],
            ),
            '("foo")+',
            'RepeatParser(LiteralParser("foo"), min_repeats=1)',
        ),
        (
            make_tree(
                s="BRACKET_EXPRESSION",
                c=[
                    make_tree(o=1, l=5, s="LITERAL_EXPRESSION"),
                    make_tree(
                        o=6,
                        l=8,
                        s="BRACKET_EXPRESSION_REPEAT_RANGE",
                        c=[make_tree(o=8, l=1, s="INTEGER")],
                    ),
                ],
            ),
            '("foo"){3,...}',
            'RepeatParser(LiteralParser("foo"), min_repeats=3)',
        ),
        (
            make_tree(s="TOKEN_NAME", l=1),
            "A",
            "SymbolParser(SymbolType.A)",
        ),
        (
            make_tree(
                l=3,
                s="CONCATENATION_EXPRESSION",
                c=[make_tree(s="TOKEN_NAME", l=1), make_tree(s="TOKEN_NAME", o=2, l=1)],
            ),
            "A B",
            "ConcatenationParser(SymbolParser(SymbolType.A), SymbolParser(SymbolType.B))",
        ),
        (
            make_tree(
                l=5,
                s="CONCATENATION_EXPRESSION",
                c=[
                    make_tree(s="TOKEN_NAME", l=1),
                    make_tree(
                        l=3,
                        o=2,
                        s="CONCATENATION_EXPRESSION",
                        c=[
                            make_tree(s="TOKEN_NAME", o=2, l=1),
                            make_tree(s="TOKEN_NAME", o=4, l=1),
                        ],
                    ),
                ],
            ),
            "A B C",
            "ConcatenationParser(SymbolParser(SymbolType.A), SymbolParser(SymbolType.B), SymbolParser(SymbolType.C))",
        ),
        (
            make_tree(
                l=3,
                s="CONJUNCTION_EXPRESSION",
                c=[make_tree(s="TOKEN_NAME", l=1), make_tree(s="TOKEN_NAME", o=4, l=1)],
            ),
            "A | B",
            "OrParser(SymbolParser(SymbolType.A), SymbolParser(SymbolType.B))",
        ),
        (
            make_tree(
                l=9,
                s="CONJUNCTION_EXPRESSION",
                c=[
                    make_tree(s="TOKEN_NAME", l=1),
                    make_tree(
                        l=3,
                        o=2,
                        s="CONJUNCTION_EXPRESSION",
                        c=[
                            make_tree(s="TOKEN_NAME", o=4, l=1),
                            make_tree(s="TOKEN_NAME", o=8, l=1),
                        ],
                    ),
                ],
            ),
            "A | B | C",
            "OrParser(SymbolParser(SymbolType.A), SymbolParser(SymbolType.B), SymbolParser(SymbolType.C))",
        ),
    ],
)
def test_tree_to_python_parser_expression(
    tree: Tree, code: str, expected_python_expr: str
) -> None:
    python_expr = tree_to_python_parser_expression(tree, code)
    assert python_expr == expected_python_expr
