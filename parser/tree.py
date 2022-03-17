from dataclasses import dataclass, replace
from enum import IntEnum
from parser.tokenizer import Token
from typing import Callable, List, Optional, Set


@dataclass
class Tree:
    token_offset: int
    token_count: int
    token_type: Optional[IntEnum]
    children: List["Tree"]

    def size(self) -> int:  # pragma: nocover
        return 1 + sum(child.size() for child in self.children)

    def value(self, tokens: List["Token"], code: str) -> str:
        value_start = tokens[self.token_offset].offset
        last_token = tokens[self.token_offset + self.token_count - 1]
        value_end = last_token.offset + last_token.length

        return code[value_start:value_end]

    def __getitem__(self, index: int) -> "Tree":  # pragma: nocover
        return self.children[index]


def prune_by_token_types(
    tree: Optional[Tree], token_types: Set[IntEnum], *, prune_hard: bool
) -> Optional[Tree]:
    if not tree:
        return None

    if prune_hard:
        return _prune_by_token_types_hard(tree, token_types)

    return _prune_by_token_types_soft(tree, token_types)


def _prune_by_token_types_hard(tree: Tree, token_types: Set[IntEnum]) -> Optional[Tree]:
    def prune_condition(tree: Tree) -> bool:
        return tree.token_type in token_types

    return prune_tree(tree, prune_condition)


def _prune_by_token_types_soft(tree: Tree, token_types: Set[IntEnum]) -> Optional[Tree]:
    def get_descendants_without_token_types(
        tree: Tree, token_types: Set[IntEnum]
    ) -> List[Tree]:
        with_symbol: List[Tree] = []

        for child in tree.children:
            if child.token_type in token_types:
                with_symbol += get_descendants_without_token_types(child, token_types)
            else:
                with_symbol.append(
                    replace(
                        child,
                        children=get_descendants_without_token_types(
                            child, token_types
                        ),
                    )
                )

        return with_symbol

    descendants_with_symbol = get_descendants_without_token_types(tree, token_types)

    children = [
        Tree(
            child.token_offset,
            child.token_count,
            child.token_type,
            get_descendants_without_token_types(child, token_types),
        )
        for child in descendants_with_symbol
    ]

    return Tree(tree.token_offset, tree.token_count, tree.token_type, children)


def prune_tree(
    tree: Optional[Tree], prune_condition: Callable[[Tree], bool]
) -> Optional[Tree]:
    if not tree:
        return None

    if prune_condition(tree):
        return None

    pruned_children: List[Tree] = []

    for child in tree.children:
        child_tree = prune_tree(child, prune_condition)
        if child_tree:
            pruned_children.append(child_tree)

    new_tree = replace(tree, children=pruned_children)
    return new_tree


def prune_no_symbol(tree: Optional[Tree]) -> Optional[Tree]:
    if not tree:
        return None

    assert tree.token_type is not None

    def get_descendants_with_symbol(tree: Tree) -> List[Tree]:
        with_symbol: List[Tree] = []

        for child in tree.children:
            if child.token_type is None:
                with_symbol += get_descendants_with_symbol(child)
            else:
                with_symbol.append(
                    replace(child, children=get_descendants_with_symbol(child))
                )

        return with_symbol

    return Tree(
        tree.token_offset,
        tree.token_count,
        tree.token_type,
        get_descendants_with_symbol(tree),
    )
