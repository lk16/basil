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
from typing import Dict, List, Optional, Set, Type


@dataclass
class Parser:
    token_type: Optional[IntEnum] = None

    def parse(
        self,
        tokens: List[Token],
        offset: int,
        non_terminal_rules: Dict[IntEnum, "Parser"],
    ) -> Tree:  # pragma: nocover
        raise NotImplementedError


class OrParser(Parser):
    def __init__(self, *args: Parser) -> None:
        self.children = list(args)

    def parse(
        self,
        tokens: List[Token],
        offset: int,
        non_terminal_rules: Dict[IntEnum, "Parser"],
    ) -> Tree:
        parsed: Optional[Tree] = None

        for child in self.children:
            try:
                parsed = child.parse(tokens, offset, non_terminal_rules)
                break
            except InternalParseError:
                continue

        if not parsed:
            raise InternalParseError(offset, self.token_type)

        return Tree(
            parsed.token_offset,
            parsed.token_count,
            self.token_type,
            [parsed],
        )


class RepeatParser(Parser):
    def __init__(self, child: Parser, min_repeats: int = 0) -> None:
        self.child = child
        self.min_repeats = min_repeats

    def parse(
        self,
        tokens: List[Token],
        offset: int,
        non_terminal_rules: Dict[IntEnum, "Parser"],
    ) -> Tree:
        sub_trees: List[Tree] = []
        child_offset = offset

        while True:
            try:
                parsed = self.child.parse(tokens, child_offset, non_terminal_rules)
            except InternalParseError:
                break
            else:
                sub_trees.append(parsed)
                child_offset += parsed.token_count

        if len(sub_trees) < self.min_repeats:
            raise InternalParseError(offset, self.child.token_type)

        return Tree(
            offset,
            child_offset - offset,
            self.token_type,
            sub_trees,
        )


class OptionalParser(Parser):
    def __init__(self, child: Parser) -> None:
        self.child = child

    def parse(
        self,
        tokens: List[Token],
        offset: int,
        non_terminal_rules: Dict[IntEnum, "Parser"],
    ) -> Tree:

        children: List[Tree] = []
        length = 0

        try:
            parsed = self.child.parse(tokens, offset, non_terminal_rules)
            children = [parsed]
            length = parsed.token_count
        except InternalParseError:
            pass

        return Tree(
            offset,
            length,
            self.token_type,
            children,
        )


class ConcatenationParser(Parser):
    def __init__(self, *args: Parser) -> None:
        self.children = list(args)

    def parse(
        self,
        tokens: List[Token],
        offset: int,
        non_terminal_rules: Dict[IntEnum, "Parser"],
    ) -> Tree:
        sub_trees: List[Tree] = []

        child_offset = offset

        for child in self.children:
            parsed = child.parse(tokens, child_offset, non_terminal_rules)
            sub_trees.append(parsed)
            child_offset += parsed.token_count

        return Tree(
            offset,
            child_offset - offset,
            self.token_type,
            sub_trees,
        )


class TerminalParser(Parser):
    def __init__(self, token_type: IntEnum):
        self.token_type = token_type

    def parse(
        self,
        tokens: List[Token],
        offset: int,
        non_terminal_rules: Dict[IntEnum, "Parser"],
    ) -> Tree:
        try:
            token = tokens[offset]
        except IndexError:
            raise InternalParseError(offset, self.token_type)

        if token.type != self.token_type:
            raise InternalParseError(offset, self.token_type)

        assert self.token_type

        return Tree(offset, 1, self.token_type, [])


class NonTerminalParser(Parser):
    def __init__(self, token_type: IntEnum):
        self.token_type = token_type

    def parse(
        self,
        tokens: List[Token],
        offset: int,
        non_terminal_rules: Dict[IntEnum, "Parser"],
    ) -> Tree:
        assert self.token_type

        child = non_terminal_rules[self.token_type].parse(
            tokens, offset, non_terminal_rules
        )

        return Tree(child.token_offset, child.token_count, self.token_type, [child])


# ---


@dataclass
class Expression:
    ...


@dataclass
class ConjunctionExpression(Expression):
    children: List[Expression]


@dataclass
class RepeatExpression(Expression):
    child: Expression
    min_repeats: int


@dataclass
class OptionalExpression(Expression):
    child: Expression


@dataclass
class ConcatenationExpression(Expression):
    children: List[Expression]


@dataclass
class TerminalExpression(Expression):
    token_type: IntEnum


@dataclass
class NonTerminalExpression(Expression):
    token_type: IntEnum


class NewParser:
    def __init__(
        self, tokens: List[Token], non_terminal_rules: Dict[IntEnum, Expression]
    ) -> None:
        self.tokens = tokens
        self.non_terminal_rules = non_terminal_rules

    def parse(self) -> Tree:
        non_terminal_enum_type = type(next(iter(self.non_terminal_rules.keys())))
        root_non_terminal = non_terminal_enum_type["ROOT"]
        root_expr = self.non_terminal_rules[root_non_terminal]
        return self._parse(root_expr, 0)

    def _parse(self, expr: Expression, offset: int) -> Tree:

        if offset > len(self.tokens):
            raise NotImplementedError

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


def humanize_parse_error(
    code: str, tokens: List[Token], e: InternalParseError
) -> ParseError:
    if not tokens:
        # strange case: no input tokens
        return ParseError(0, 0, "<no input tokens found>", [])

    if e.token_offset == len(tokens):
        offset = tokens[-1].offset + tokens[-1].length
    else:
        offset = tokens[e.token_offset].offset

    before_offset = code[:offset]
    line_number = 1 + before_offset.count("\n")
    prev_newline = before_offset.rfind("\n")

    next_newline = code.find("\n", offset)
    if next_newline == -1:
        next_newline = len(code)

    column_number = offset - prev_newline
    line = code[prev_newline + 1 : next_newline]

    # TODO suggest expected symbol types

    return ParseError(line_number, column_number, line, [])


def _check_non_terminal_rules(
    non_terminal_rules: Dict[IntEnum, Parser]
) -> Type[IntEnum]:
    """
    Checks completeness, inconsistencies.
    Returns the IntEnum subclass type used for all keys
    """
    symbols_enum = type(list((non_terminal_rules.keys()))[0])

    for enum_value in symbols_enum:
        try:
            non_terminal_rules[enum_value]
        except KeyError:
            raise UnhandledSymbolType(enum_value)

    if set(non_terminal_rules.keys()) != set(symbols_enum):
        unexpected_keys = set(non_terminal_rules.keys()) - set(symbols_enum)
        raise UnexpectedSymbolType(unexpected_keys)

    try:
        symbols_enum["ROOT"]
    except KeyError:
        raise ValueError(f"Non-terminals do not have a ROOT item")

    return symbols_enum


def parse_generic(
    non_terminal_rules: Dict[IntEnum, Parser],
    tokens: List[Token],
    code: str,
    prune_hard_symbols: Set[IntEnum],
    prune_soft_symbols: Set[IntEnum],
    root_token: str = "ROOT",
) -> Tree:

    non_terminals_enum = _check_non_terminal_rules(non_terminal_rules)

    root_symbol = non_terminals_enum[root_token]

    tree = non_terminal_rules[root_symbol]

    # Prevent infinite recursion
    if not isinstance(tree, (NonTerminalParser, TerminalParser)):
        tree.token_type = root_symbol

    try:
        parsed: Optional[Tree] = tree.parse(tokens, 0, non_terminal_rules)

        assert parsed
        parsed.token_type = root_symbol

        if parsed.token_count != len(tokens):
            raise InternalParseError(parsed.token_count, None)

    except InternalParseError as e:
        raise humanize_parse_error(code, tokens, e) from e

    parsed = prune_no_symbol(parsed)
    assert parsed

    if prune_hard_symbols:
        parsed = prune_by_symbol_types(parsed, prune_hard_symbols, prune_hard=True)
        assert parsed

    if prune_soft_symbols:
        parsed = prune_by_symbol_types(parsed, prune_soft_symbols, prune_hard=False)
        assert parsed

    return parsed
