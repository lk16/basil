from dataclasses import dataclass, replace
from enum import IntEnum
from typing import Any, Callable, Dict, List, Optional, Set


@dataclass
class Tree:
    symbol_offset: int
    symbol_length: int
    symbol_type: Optional[IntEnum]
    children: List["Tree"]

    def size(self) -> int:
        return 1 + sum(child.size() for child in self.children)

    def dump(self, code: str) -> Dict[str, Any]:
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


def prune_zero_length(tree: Tree) -> Optional[Tree]:
    def prune_condition(tree: Tree) -> bool:
        return tree.symbol_length == 0

    return prune_tree(tree, prune_condition)


def prune_by_symbol_types(tree: Tree, symbol_types: Set[IntEnum]) -> Optional[Tree]:
    def prune_condition(tree: Tree) -> bool:
        return tree.symbol_type in symbol_types

    return prune_tree(tree, prune_condition)


def prune_useless(tree: Tree) -> Optional[Tree]:
    def prune_condition(tree: Tree) -> bool:
        return tree.symbol_type is None and len(tree.children) == 0

    return prune_tree(tree, prune_condition)


def prune_tree(tree: Tree, prune_condition: Callable[[Tree], bool]) -> Optional[Tree]:
    if prune_condition(tree):
        return None

    pruned_children: List[Tree] = []

    for child in tree.children:
        child_tree = prune_tree(child, prune_condition)
        if child_tree:
            pruned_children.append(child_tree)

    new_tree = replace(tree, children=pruned_children)
    return new_tree