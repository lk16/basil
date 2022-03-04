from parser.tree import Tree, prune_by_symbol_types, prune_no_symbol, prune_zero_length
from typing import List, Optional

from tests.test_parser import SymbolsForTesting


# shortcut for tests
def make_tree(
    *, o: int = 0, l: int = 1, c: Optional[List[Tree]] = None, s: Optional[str] = None
) -> Tree:
    children = c or []

    if s:
        symbol_type = SymbolsForTesting[s]
    else:
        symbol_type = None

    offset = o
    length = l

    return Tree(offset, length, symbol_type, children)


def test_prune_no_symbol_simple() -> None:
    tree = make_tree(s="A")
    pruned_tree = prune_no_symbol(tree)

    expected_pruned_tree = make_tree(s="A")
    assert pruned_tree == expected_pruned_tree


def test_prune_no_symbol_tree_symbols() -> None:
    tree = make_tree(s="A", c=[make_tree(s="B"), make_tree(s="C")])
    pruned_tree = prune_no_symbol(tree)

    expected_pruned_tree = tree
    assert pruned_tree == expected_pruned_tree


def test_prune_no_symbol_two_children_without_symbols() -> None:
    tree = make_tree(s="A", c=[make_tree(), make_tree()])
    pruned_tree = prune_no_symbol(tree)

    expected_pruned_tree = make_tree(s="A")
    assert pruned_tree == expected_pruned_tree


def test_prune_no_symbol_grandchild_symbol() -> None:
    tree = make_tree(s="A", c=[make_tree(c=[make_tree(s="B")])])
    pruned_tree = prune_no_symbol(tree)

    expected_pruned_tree = make_tree(s="A", c=[make_tree(s="B")])
    assert pruned_tree == expected_pruned_tree


def test_prune_no_symbol_compilcated() -> None:
    tree = make_tree(
        s="A", c=[make_tree(c=[make_tree(s="B", c=[make_tree(c=[make_tree(s="C")])])])]
    )
    pruned_tree = prune_no_symbol(tree)

    expected_pruned_tree = make_tree(s="A", c=[make_tree(s="B", c=[make_tree(s="C")])])
    assert pruned_tree == expected_pruned_tree


def test_prune_no_symbol_ccompilcated_2() -> None:
    tree = make_tree(
        s="A",
        c=[
            make_tree(
                c=[
                    make_tree(
                        s="B",
                        c=[
                            make_tree(c=[make_tree(s="C")]),
                            make_tree(c=[make_tree(s="D")]),
                        ],
                    )
                ]
            )
        ],
    )
    pruned_tree = prune_no_symbol(tree)

    expected_pruned_tree = make_tree(
        s="A", c=[make_tree(s="B", c=[make_tree(s="C"), make_tree(s="D")])]
    )
    assert pruned_tree == expected_pruned_tree


def test_tree_value() -> None:
    code = "ABCDE"
    tree = make_tree(o=1, l=3)
    assert tree.value(code) == "BCD"


def test_prune_zero_length() -> None:
    tree = make_tree(s="A", c=[make_tree(l=0), make_tree(l=0, c=[make_tree(l=0)])])
    pruned_tree = prune_zero_length(tree)

    assert pruned_tree
    assert len(pruned_tree.children) == 0
    assert pruned_tree.symbol_type == SymbolsForTesting.A


def test_prune_by_symbol_type() -> None:
    tree = make_tree(s="A", c=[make_tree(c=[make_tree(s="B", c=[make_tree(s="C")])])])
    pruned_tree = prune_by_symbol_types(tree, {SymbolsForTesting.B}, prune_subtree=True)

    assert pruned_tree
    assert len(pruned_tree.children) == 1
    assert pruned_tree.symbol_type == SymbolsForTesting.A

    assert len(pruned_tree.children[0].children) == 0
