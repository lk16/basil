from dataclasses import dataclass
from parser.parser.models import Tree
from typing import List, Set, Tuple


@dataclass
class ParsedGrammar:
    terminals: List[Tuple[str, Tree]]
    non_terminals: List[Tuple[str, Tree]]  # TODO should this be a Dict?
    pruned_terminals: Set[str]
    pruned_non_terminals: Set[str]

    @classmethod
    def empty(cls) -> "ParsedGrammar":
        return ParsedGrammar(
            terminals=[],
            non_terminals=[],
            pruned_terminals=set(),
            pruned_non_terminals=set(),
        )
