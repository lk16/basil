from parser.tree import Tree, prune_no_symbol
from typing import List, Optional

from tests.test_parser import SymbolsForTesting


# shortcut for tests
def make_tree(*, c: Optional[List[Tree]] = None, s: Optional[str] = None) -> Tree:
    children = c or []

    if s:
        symbol_type = SymbolsForTesting[s]
    else:
        symbol_type = None

    return Tree(0, 1, symbol_type, children)


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
