#!/usr/bin/env python

from dataclasses import replace
from enum import IntEnum
from parser.exceptions import InternalParseError, ParseError
from parser.parser.exceptions import (
    MissingNonTerminalTypes,
    MissingRootNonTerminalType,
    UnexpectedNonTerminalTypes,
)
from parser.parser.models import (
    ConcatenationExpression,
    ConjunctionExpression,
    Expression,
    NonTerminalExpression,
    OptionalExpression,
    RepeatExpression,
    TerminalExpression,
    Tree,
)
from parser.tokenizer.tokenizer import Token
from typing import Callable, Dict, List, Optional, Set


class Parser:
    def __init__(
        self,
        *,
        tokens: List[Token],
        code: str,
        non_terminal_rules: Dict[IntEnum, Expression],
        prune_hard_tokens: Set[IntEnum],
        prune_soft_tokens: Set[IntEnum],
        root_token: str = "ROOT",
    ) -> None:
        self.tokens = tokens
        self.code = code
        self.non_terminal_rules = non_terminal_rules
        self.prune_hard_tokens = prune_hard_tokens
        self.prune_soft_tokens = prune_soft_tokens
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

            pruned_tree = prune_no_token_type(tree)

            if not pruned_tree:
                raise InternalParseError(0, None)

            pruned_tree = prune_by_token_types(
                pruned_tree, self.prune_hard_tokens, prune_hard=True
            )

            if not pruned_tree:
                raise InternalParseError(0, None)

            pruned_tree = prune_by_token_types(
                pruned_tree, self.prune_soft_tokens, prune_hard=False
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

        children: List[Tree] = []
        child_offset = offset

        while True:
            try:
                parsed = self._parse(expr.child, child_offset)
            except InternalParseError:
                break
            else:
                children.append(parsed)
                child_offset += parsed.token_count

        if len(children) < expr.min_repeats:
            raise InternalParseError(offset, None)

        return Tree(
            offset,
            child_offset - offset,
            None,
            children,
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
        tokens_enum = type(list((self.non_terminal_rules.keys()))[0])

        unexpected_keys = self.non_terminal_rules.keys() - set(tokens_enum)
        missing_keys: Set[IntEnum] = set(tokens_enum) - self.non_terminal_rules.keys()

        if missing_keys:
            raise MissingNonTerminalTypes(missing_keys)

        if unexpected_keys:
            raise UnexpectedNonTerminalTypes(unexpected_keys)

        if "ROOT" not in tokens_enum.__members__:
            raise MissingRootNonTerminalType

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

        # TODO suggest expected token types

        return ParseError(line_number, column_number, line, [])


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
        with_token_type: List[Tree] = []

        for child in tree.children:
            if child.token_type in token_types:
                with_token_type += get_descendants_without_token_types(
                    child, token_types
                )
            else:
                with_token_type.append(
                    replace(
                        child,
                        children=get_descendants_without_token_types(
                            child, token_types
                        ),
                    )
                )

        return with_token_type

    descendants_with_token_type = get_descendants_without_token_types(tree, token_types)

    children = [
        Tree(
            child.token_offset,
            child.token_count,
            child.token_type,
            get_descendants_without_token_types(child, token_types),
        )
        for child in descendants_with_token_type
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


def prune_no_token_type(tree: Optional[Tree]) -> Optional[Tree]:
    if not tree:
        return None

    assert tree.token_type is not None

    def get_descendants_with_token_type(tree: Tree) -> List[Tree]:
        with_token_type: List[Tree] = []

        for child in tree.children:
            if child.token_type is None:
                with_token_type += get_descendants_with_token_type(child)
            else:
                with_token_type.append(
                    replace(child, children=get_descendants_with_token_type(child))
                )

        return with_token_type

    return Tree(
        tree.token_offset,
        tree.token_count,
        tree.token_type,
        get_descendants_with_token_type(tree),
    )
