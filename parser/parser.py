#!/usr/bin/env python

from dataclasses import dataclass
from enum import IntEnum
from parser.exceptions import (
    InternalParseError,
    ParseError,
    UnexpectedSymbolType,
    UnhandledSymbolType,
)
from parser.tree import Token, Tree, prune_by_symbol_types, prune_no_symbol
from typing import Dict, List, Optional, Set


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


class Parser:
    def __init__(
        self,
        tokens: List[Token],
        code: str,
        non_terminal_rules: Dict[IntEnum, Expression],
        prune_hard_symbols: Set[IntEnum],
        prune_soft_symbols: Set[IntEnum],
        root_token: str = "ROOT",
    ) -> None:
        self.tokens = tokens
        self.code = code
        self.non_terminal_rules = non_terminal_rules
        self.prune_hard_symbols = prune_hard_symbols
        self.prune_soft_symbols = prune_soft_symbols
        self.root_token = root_token

    def parse(self) -> Tree:
        self._check_non_terminal_rules()

        non_terminal_enum_type = type(next(iter(self.non_terminal_rules.keys())))
        root_non_terminal = non_terminal_enum_type[self.root_token]
        root_expr = self.non_terminal_rules[root_non_terminal]

        try:
            tree = self._parse(root_expr, 0)
            tree.token_type = root_non_terminal

            if tree.token_count != len(self.tokens):
                raise InternalParseError(tree.token_count, None)

            pruned_tree = prune_no_symbol(tree)

            if not pruned_tree:
                raise InternalParseError(0, None)

            pruned_tree = prune_by_symbol_types(
                pruned_tree, self.prune_hard_symbols, prune_hard=True
            )

            if not pruned_tree:
                raise InternalParseError(0, None)

            pruned_tree = prune_by_symbol_types(
                pruned_tree, self.prune_soft_symbols, prune_hard=False
            )

            if not pruned_tree:
                raise InternalParseError(0, None)

        except InternalParseError as e:
            raise self._humanize_parse_error(e) from e

        return pruned_tree

    def _parse(self, expr: Expression, offset: int) -> Tree:

        if offset >= len(self.tokens):
            raise InternalParseError(offset, None)

        parse_funcs = {
            ConcatenationExpression: self._parse_concatenation,
            ConjunctionExpression: self._parse_conjunction,
            NonTerminalExpression: self._parse_non_terminal,
            OptionalExpression: self._parse_optional,
            RepeatExpression: self._parse_repeat,
            TerminalExpression: self._parse_terminal,
        }

        # Should not fail, so if this raises a KeyError, we want the parser to crash.
        parse_func = parse_funcs[type(expr)]

        return parse_func(expr, offset)

    def _parse_conjunction(self, expr: Expression, offset: int) -> Tree:
        assert isinstance(expr, ConjunctionExpression)

        parsed: Optional[Tree] = None

        for child in expr.children:
            try:
                parsed = self._parse(child, offset)
                break
            except InternalParseError:
                continue

        if not parsed:
            raise InternalParseError(offset, None)

        return Tree(
            parsed.token_offset,
            parsed.token_count,
            None,
            [parsed],
        )

    def _parse_repeat(self, expr: Expression, offset: int) -> Tree:
        assert isinstance(expr, RepeatExpression)

        sub_trees: List[Tree] = []
        child_offset = offset

        while True:
            try:
                parsed = self._parse(expr.child, child_offset)
            except InternalParseError:
                break
            else:
                sub_trees.append(parsed)
                child_offset += parsed.token_count

        if len(sub_trees) < expr.min_repeats:
            raise InternalParseError(offset, None)

        return Tree(
            offset,
            child_offset - offset,
            None,
            sub_trees,
        )

    def _parse_optional(self, expr: Expression, offset: int) -> Tree:
        assert isinstance(expr, OptionalExpression)

        children: List[Tree] = []
        length = 0

        try:
            parsed = self._parse(expr.child, offset)
            children = [parsed]
            length = parsed.token_count
        except InternalParseError:
            pass

        return Tree(
            offset,
            length,
            None,
            children,
        )

    def _parse_concatenation(self, expr: Expression, offset: int) -> Tree:
        assert isinstance(expr, ConcatenationExpression)

        sub_trees: List[Tree] = []

        child_offset = offset

        for child in expr.children:
            parsed = self._parse(child, child_offset)
            sub_trees.append(parsed)
            child_offset += parsed.token_count

        return Tree(
            offset,
            child_offset - offset,
            None,
            sub_trees,
        )

    def _parse_terminal(self, expr: Expression, offset: int) -> Tree:
        assert isinstance(expr, TerminalExpression)

        if self.tokens[offset].type != expr.token_type:
            raise InternalParseError(offset, expr.token_type)

        return Tree(offset, 1, expr.token_type, [])

    def _parse_non_terminal(self, expr: Expression, offset: int) -> Tree:
        assert isinstance(expr, NonTerminalExpression)

        non_terminal_expansion = self.non_terminal_rules[expr.token_type]
        child = self._parse(non_terminal_expansion, offset)
        return Tree(child.token_offset, child.token_count, expr.token_type, [child])

    def _check_non_terminal_rules(self) -> None:
        symbols_enum = type(list((self.non_terminal_rules.keys()))[0])

        for enum_value in symbols_enum:
            try:
                self.non_terminal_rules[enum_value]
            except KeyError:
                raise UnhandledSymbolType(enum_value)

        unexpected_keys = self.non_terminal_rules.keys() - set(symbols_enum)
        if unexpected_keys:
            raise UnexpectedSymbolType(unexpected_keys)

        try:
            symbols_enum["ROOT"]
        except KeyError:
            raise ValueError(f"Non-terminals do not have a ROOT item")

    def _humanize_parse_error(self, e: InternalParseError) -> ParseError:
        if not self.tokens:
            # strange case: no input tokens
            return ParseError(0, 0, "<no input tokens found>", [])

        if e.token_offset == len(self.tokens):
            offset = self.tokens[-1].offset + self.tokens[-1].length
        else:
            offset = self.tokens[e.token_offset].offset

        before_offset = self.code[:offset]
        line_number = 1 + before_offset.count("\n")
        prev_newline = before_offset.rfind("\n")

        next_newline = self.code.find("\n", offset)
        if next_newline == -1:
            next_newline = len(self.code)

        column_number = offset - prev_newline
        line = self.code[prev_newline + 1 : next_newline]

        # TODO suggest expected symbol types

        return ParseError(line_number, column_number, line, [])


def parse_generic(
    non_terminal_rules: Dict[IntEnum, Expression],
    tokens: List[Token],
    code: str,
    prune_hard_symbols: Set[IntEnum],
    prune_soft_symbols: Set[IntEnum],
    root_token: str = "ROOT",
) -> Tree:

    return Parser(
        tokens,
        code,
        non_terminal_rules,
        prune_hard_symbols,
        prune_soft_symbols,
        root_token,
    ).parse()
