from dataclasses import dataclass, replace
from enum import IntEnum
from typing import Any, Callable, Dict, List, Optional, Set


@dataclass
class Tree:
    symbol_offset: int
    symbol_length: int
    symbol_type: Optional[IntEnum]
    children: List["Tree"]

    def size(self) -> int:  # pragma: nocover
        return 1 + sum(child.size() for child in self.children)

    def dump(self, code: str) -> Dict[str, Any]:  # pragma: nocover
        type_str = ""

        if self.symbol_type:
            type_str = self.symbol_type.name

        return {
            "value": self.value(code),
            "type": type_str,
            "children": [child.dump(code) for child in self.children],
        }

    def value(self, code: str) -> str:
        return code[self.symbol_offset : self.symbol_offset + self.symbol_length]

    def __getitem__(self, index: int) -> "Tree":  # pragma: nocover
        return self.children[index]


def prune_zero_length(tree: Optional[Tree]) -> Optional[Tree]:
    if not tree:
        return None

    def prune_condition(tree: Tree) -> bool:
        return tree.symbol_length == 0

    return prune_tree(tree, prune_condition)


def prune_by_symbol_types(
    tree: Optional[Tree], symbol_types: Set[IntEnum], *, prune_hard: bool
) -> Optional[Tree]:
    if not tree:
        return None

    if prune_hard:
        return _prune_by_symbol_types_hard(tree, symbol_types)

    return _prune_by_symbol_types_soft(tree, symbol_types)


def _prune_by_symbol_types_hard(
    tree: Tree, symbol_types: Set[IntEnum]
) -> Optional[Tree]:
    def prune_condition(tree: Tree) -> bool:
        return tree.symbol_type in symbol_types

    return prune_tree(tree, prune_condition)


def _prune_by_symbol_types_soft(
    tree: Tree, symbol_types: Set[IntEnum]
) -> Optional[Tree]:
    def get_descendants_without_symbol_types(
        tree: Tree, symbol_types: Set[IntEnum]
    ) -> List[Tree]:
        with_symbol: List[Tree] = []

        for child in tree.children:
            if child.symbol_type in symbol_types:
                with_symbol += get_descendants_without_symbol_types(child, symbol_types)
            else:
                with_symbol.append(
                    replace(
                        child,
                        children=get_descendants_without_symbol_types(
                            child, symbol_types
                        ),
                    )
                )

        return with_symbol

    descendants_with_symbol = get_descendants_without_symbol_types(tree, symbol_types)

    children = [
        Tree(
            child.symbol_offset,
            child.symbol_length,
            child.symbol_type,
            get_descendants_without_symbol_types(child, symbol_types),
        )
        for child in descendants_with_symbol
    ]

    return Tree(tree.symbol_offset, tree.symbol_length, tree.symbol_type, children)


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

    assert tree.symbol_type is not None

    def get_descendants_with_symbol(tree: Tree) -> List[Tree]:
        with_symbol: List[Tree] = []

        for child in tree.children:
            if child.symbol_type is None:
                with_symbol += get_descendants_with_symbol(child)
            else:
                with_symbol.append(
                    replace(child, children=get_descendants_with_symbol(child))
                )

        return with_symbol

    return Tree(
        tree.symbol_offset,
        tree.symbol_length,
        tree.symbol_type,
        get_descendants_with_symbol(tree),
    )
