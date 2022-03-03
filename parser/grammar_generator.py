from enum import IntEnum
from parser.parser import (
    ConcatenationParser,
    LiteralParser,
    OptionalParser,
    OrParser,
    Parser,
    RegexBasedParser,
    RepeatParser,
    SymbolParser,
)
from pathlib import Path
from typing import Dict, Tuple

ESCAPE_SEQUENCES = [
    ("\\", "\\\\"),
    ("'", "\\'"),
    ('"', '\\"'),
    ("\a", "\\a"),
    ("\b", "\\b"),
    ("\f", "\\f"),
    ("\n", "\\n"),
    ("\r", "\\r"),
    ("\t", "\\t"),
    ("\v", "\\v"),
]


def escape_string(s: str) -> str:
    result = s
    for before, after in ESCAPE_SEQUENCES:
        result = result.replace(before, after)

    return '"' + result + '"'


def unescape_string(s: str) -> str:
    if len(s) < 2 or s[0] != '"' or s[-1] != '"':
        raise ValueError

    result = s[1:-1]
    for after, before in ESCAPE_SEQUENCES:
        result = result.replace(before, after)

    return result


def _bnf_like_expression(parser: Parser, depth: int = 0) -> str:
    if parser.symbol_type is not None and depth != 0:
        return parser.symbol_type.name

    if isinstance(parser, SymbolParser):  # pragma: nocover
        raise NotImplementedError  # unreachable

    elif isinstance(parser, ConcatenationParser):
        return " ".join(
            _bnf_like_expression(child, depth + 1) for child in parser.children
        )

    elif isinstance(parser, OrParser):
        expr = " | ".join(
            _bnf_like_expression(child, depth + 1) for child in parser.children
        )

        if depth != 0:
            expr = f"({expr})"

        return expr

    elif isinstance(parser, OptionalParser):
        return "(" + _bnf_like_expression(parser.child, depth + 1) + ")?"

    elif isinstance(parser, RepeatParser):
        expr = "(" + _bnf_like_expression(parser.child, depth + 1) + ")"
        if parser.min_repeats == 0:
            return expr + "*"
        elif parser.min_repeats == 1:
            return expr + "+"
        else:
            return expr + f"{parser.min_repeats,...}"

    elif isinstance(parser, RegexBasedParser):
        return "regex(" + escape_string(parser.regex.pattern[1:]) + ")"

    elif isinstance(parser, LiteralParser):
        return '"' + escape_string(parser.literal) + '"'

    else:  # pragma: nocover
        raise NotImplementedError


def check_grammar_file_staleness(  # pragma: nocover
    grammar_file: Path, rewrite_rules: Dict[IntEnum, Parser], root_symbol: IntEnum
) -> Tuple[bool, str]:
    if grammar_file.exists():
        old_grammar = grammar_file.read_text()
    else:
        old_grammar = ""

    new_grammar = parsers_to_grammar(rewrite_rules, root_symbol)

    stale = old_grammar != new_grammar
    return stale, new_grammar


def parsers_to_grammar(  # pragma: nocover
    rewrite_rules: Dict[IntEnum, Parser],
    root_symbol: IntEnum,
) -> str:

    output = (
        "// Human readable grammar. Easier to understand than actual rewrite rules.\n"
        "// This file was generated using regenerate_bnf_like_grammar_file().\n"
        "// A unit test should make sure this file is up to date with its source.\n\n"
        f"// The root symbol is {root_symbol.name}.\n\n"
    )

    symbols = sorted(rewrite_rules.keys(), key=lambda x: x.name)

    for i, symbol in enumerate(symbols):
        parser = rewrite_rules[symbol]
        output += f"{symbol.name} = " + _bnf_like_expression(parser)

        if i == len(symbols) - 1:
            output += "\n"
        else:
            output += "\n\n"

    return output


def grammar_to_parsers(grammar_file: Path) -> str:
    """
    Reads the grammar file and generates a python parser file from it.
    """

    raise NotImplementedError
