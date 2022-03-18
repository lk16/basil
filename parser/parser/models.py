from dataclasses import dataclass
from enum import IntEnum
from parser.tokenizer.tokenizer import Token
from typing import List, Optional


@dataclass
class Expression:
    ...


@dataclass
class ConjunctionExpression(Expression):
    def __init__(self, *args: Expression) -> None:
        self.children = list(args)

    children: List[Expression]


@dataclass
class RepeatExpression(Expression):
    child: Expression
    min_repeats: int = 0


@dataclass
class OptionalExpression(Expression):
    child: Expression


@dataclass
class ConcatenationExpression(Expression):
    def __init__(self, *args: Expression) -> None:
        self.children = list(args)

    children: List[Expression]


@dataclass
class TerminalExpression(Expression):
    token_type: IntEnum


@dataclass
class NonTerminalExpression(Expression):
    token_type: IntEnum


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
