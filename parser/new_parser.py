#!/usr/bin/env python

import re
from dataclasses import dataclass
from enum import IntEnum
from parser.exceptions import (
    InternalParseError,
    ParseError,
    UnexpectedSymbolType,
    UnhandledSymbolType,
)
from parser.tree import Tree, prune_by_symbol_types, prune_no_symbol, prune_zero_length
from typing import Dict, List, Optional, Set, Tuple, Type


@dataclass
class Token:
    type: IntEnum
    offset: int
    length: int


@dataclass
class Parser:
    symbol_type: Optional[IntEnum] = None

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
        longest_parsed: Optional[Tree] = None

        for child in self.children:
            try:
                parsed = child.parse(tokens, offset, non_terminal_rules)
            except InternalParseError:
                continue

            if not longest_parsed:
                longest_parsed = parsed
            elif parsed.symbol_length > longest_parsed.symbol_length:
                longest_parsed = parsed

        if not longest_parsed:
            raise InternalParseError(offset, self.symbol_type)

        return Tree(
            longest_parsed.symbol_offset,
            longest_parsed.symbol_length,
            self.symbol_type,
            [longest_parsed],
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
                child_offset += parsed.symbol_length

        if len(sub_trees) < self.min_repeats:
            raise InternalParseError(offset, self.child.symbol_type)

        return Tree(
            offset,
            child_offset - offset,
            self.symbol_type,
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
            length = parsed.symbol_length
        except InternalParseError:
            pass

        return Tree(
            offset,
            length,
            self.symbol_type,
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
            child_offset += parsed.symbol_length

        return Tree(
            offset,
            child_offset - offset,
            self.symbol_type,
            sub_trees,
        )


class TerminalParser(Parser):
    def __init__(self, symbol_type: IntEnum):
        self.symbol_type = symbol_type

    def parse(
        self,
        tokens: List[Token],
        offset: int,
        non_terminal_rules: Dict[IntEnum, "Parser"],
    ) -> Tree:
        raise NotImplementedError


class NonTerminalParser(Parser):
    def __init__(self, symbol_type: IntEnum):
        self.symbol_type = symbol_type

    def parse(
        self,
        tokens: List[Token],
        offset: int,
        non_terminal_rules: Dict[IntEnum, "Parser"],
    ) -> Tree:
        raise NotImplementedError


class LiteralParser(Parser):
    def __init__(self, literal: str):
        self.literal = literal

    def parse(
        self,
        tokens: List[Token],
        offset: int,
        non_terminal_rules: Dict[IntEnum, "Parser"],
    ) -> Tree:
        raise NotImplementedError


class RegexTokenizer:
    def __init__(self, regex: str):
        if regex.startswith("^"):
            raise ValueError(
                "Regex should not start with a caret '^' character"
                + "it's added in __init__() now."
            )

        self.regex = re.compile(f"^{regex}")

    def tokenize(self, code: str, offset: int) -> Optional[int]:
        match = self.regex.match(code[offset:])

        if not match:
            return None

        match_length = len(match.group(0))

        if match_length == 0:
            return None

        return match_length


def humanize_parse_error(code: str, e: InternalParseError) -> ParseError:
    before_offset = code[: e.offset]
    line_number = 1 + before_offset.count("\n")
    prev_newline = before_offset.rfind("\n")

    next_newline = code.find("\n", e.offset)
    if next_newline == -1:
        next_newline = len(code)

    column_number = e.offset - prev_newline
    line = code[prev_newline + 1 : next_newline]

    expected_symbol_types: List[IntEnum] = []

    if e.symbol_type:
        # TODO this may be wrong or unhelpful to the programmer
        expected_symbol_types.append(e.symbol_type)

    return ParseError(line_number, column_number, line, expected_symbol_types)


def _check_rules(rewrite_rules: Dict[IntEnum, Parser]) -> Type[IntEnum]:
    """
    Checks completeness, inconsistencies.
    Returns the IntEnum subclass type used for all keys
    """
    symbols_enum = type(list((rewrite_rules.keys()))[0])

    for enum_value in symbols_enum:
        try:
            rewrite_rules[enum_value]
        except KeyError:
            raise UnhandledSymbolType(enum_value)

    if set(rewrite_rules.keys()) != set(symbols_enum):
        unexpected_keys = set(rewrite_rules.keys()) - set(symbols_enum)
        raise UnexpectedSymbolType(unexpected_keys)

    return symbols_enum


def tokenize(
    code: str, terminal_rules: List[Tuple[IntEnum, RegexTokenizer]]
) -> List[Token]:
    # TODO check terminal_rules

    tokens: List[Token] = []
    offset = 0

    while offset < len(code):
        for token_type, tokenizer in terminal_rules:
            token_length = tokenizer.tokenize(code, offset)

            if token_length is not None:
                tokens.append(Token(token_type, offset, token_length))
                offset += token_length
                break

    return tokens


def parse_generic(
    non_terminal_rules: Dict[IntEnum, Parser],
    tokens: List[Token],
    code: str,
    prune_hard_symbols: Optional[Set[IntEnum]] = None,
    prune_soft_symbols: Optional[Set[IntEnum]] = None,
    root_token: str = "ROOT",
) -> Tree:
    non_terminals_enum = _check_rules(non_terminal_rules)

    try:
        non_terminals_enum["ROOT"]
    except KeyError:
        raise ValueError(f"{non_terminals_enum.__name__} does not have a ROOT item")

    root_symbol = non_terminals_enum[root_token]

    tree = non_terminal_rules[root_symbol]

    # Prevent infinite recursion
    if not isinstance(tree, NonTerminalParser):
        tree.symbol_type = root_symbol

    try:
        parsed: Optional[Tree] = tree.parse(tokens, 0, non_terminal_rules)

        assert parsed
        parsed.symbol_type = root_symbol

        if parsed.symbol_length != len(code):
            raise InternalParseError(parsed.symbol_length, None)

    except InternalParseError as e:
        raise humanize_parse_error(code, e) from e

    parsed = prune_no_symbol(parsed)
    assert parsed

    parsed = prune_zero_length(parsed)
    assert parsed

    if prune_hard_symbols is not None:
        parsed = prune_by_symbol_types(parsed, prune_hard_symbols, prune_hard=True)
        assert parsed

    if prune_soft_symbols is not None:
        parsed = prune_by_symbol_types(parsed, prune_soft_symbols, prune_hard=False)
        assert parsed

    return parsed
