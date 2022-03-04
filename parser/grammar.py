from enum import IntEnum
from parser.grammar_parser import REWRITE_RULES, ROOT_SYMBOL, GrammarSymbolType
from parser.parser import (
    ConcatenationParser,
    LiteralParser,
    OptionalParser,
    OrParser,
    Parser,
    RegexBasedParser,
    RepeatParser,
    SymbolParser,
    new_parse_generic,
)
from parser.tree import Tree, prune_by_symbol_types, prune_no_symbol, prune_zero_length
from pathlib import Path
from typing import Dict, List, Optional, Tuple

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


def _grammar_expression(parser: Parser, depth: int = 0) -> str:
    """
    Generates a BNF-like expression from a parser.
    This expression shows what the parser accepts.
    """

    if parser.symbol_type is not None and depth != 0:
        return parser.symbol_type.name

    if isinstance(parser, SymbolParser):  # pragma: nocover
        raise NotImplementedError  # unreachable

    elif isinstance(parser, ConcatenationParser):
        return " ".join(
            _grammar_expression(child, depth + 1) for child in parser.children
        )

    elif isinstance(parser, OrParser):
        expr = " | ".join(
            _grammar_expression(child, depth + 1) for child in parser.children
        )

        if depth != 0:
            expr = f"({expr})"

        return expr

    elif isinstance(parser, OptionalParser):
        return "(" + _grammar_expression(parser.child, depth + 1) + ")?"

    elif isinstance(parser, RepeatParser):
        expr = "(" + _grammar_expression(parser.child, depth + 1) + ")"
        if parser.min_repeats == 0:
            return expr + "*"
        elif parser.min_repeats == 1:
            return expr + "+"
        else:
            return expr + "{" + str(parser.min_repeats) + ",...}"

    elif isinstance(parser, RegexBasedParser):
        return "regex(" + escape_string(parser.regex.pattern[1:]) + ")"

    elif isinstance(parser, LiteralParser):
        return escape_string(parser.literal)

    else:  # pragma: nocover
        raise NotImplementedError


def check_grammar_file_staleness(
    grammar_file: Path, rewrite_rules: Dict[IntEnum, Parser], root_symbol: IntEnum
) -> Tuple[bool, str]:  # pragma: nocover
    if grammar_file.exists():
        old_grammar = grammar_file.read_text()
    else:
        old_grammar = ""

    new_grammar = parsers_to_grammar(rewrite_rules, root_symbol)

    stale = old_grammar != new_grammar
    return stale, new_grammar


def parsers_to_grammar(
    rewrite_rules: Dict[IntEnum, Parser],
    root_symbol: IntEnum,
) -> str:  # pragma: nocover

    output = (
        "// Human readable grammar. Easier to understand than actual rewrite rules.\n"
        "// This file was generated using regenerate_bnf_like_grammar_file().\n"
        "// A unit test should make sure this file is up to date with its source.\n\n"
        f"// The root symbol is {root_symbol.name}.\n\n"
    )

    symbols = sorted(rewrite_rules.keys(), key=lambda x: x.name)

    for i, symbol in enumerate(symbols):
        parser = rewrite_rules[symbol]
        output += f"{symbol.name} = " + _grammar_expression(parser)

        if i == len(symbols) - 1:
            output += "\n"
        else:
            output += "\n\n"

    return output


def tree_to_python_parser_expression(tree: Tree, code: str) -> str:

    if tree.symbol_type == GrammarSymbolType.LITERAL_EXPRESSION:
        value = tree.value(code)
        return "LiteralParser(" + escape_string(value[1:-1]) + ")"

    elif tree.symbol_type == GrammarSymbolType.REGEX_EXPRESSION:
        regex_value = tree[0].value(code)
        return "RegexBasedParser(" + escape_string(regex_value[1:-1]) + ")"

    elif tree.symbol_type == GrammarSymbolType.BRACKETED_EXPRESSION:
        return tree_to_python_parser_expression(tree[0], code)

    elif tree.symbol_type == GrammarSymbolType.TOKEN_COMPOUND_EXPRESSION:
        # TODO This was filtered out earlier, check why that failed
        return tree_to_python_parser_expression(tree[0], code)

    elif tree.symbol_type == GrammarSymbolType.TOKEN_EXPRESSION:
        # TODO This was filtered out earlier, check why that failed
        return tree_to_python_parser_expression(tree[0], code)

    elif tree.symbol_type == GrammarSymbolType.CONCATENATION_EXPRESSION:
        return (
            "ConcatenationParser("
            + tree_to_python_parser_expression(tree[0], code)
            + ", "
            + tree_to_python_parser_expression(tree[1], code)
            + ")"
        )

    elif tree.symbol_type == GrammarSymbolType.CONJUNCTION_EXPRESSION:
        return (
            "OrParser("
            + tree_to_python_parser_expression(tree[0], code)
            + ", "
            + tree_to_python_parser_expression(tree[1], code)
            + ")"
        )

    elif tree.symbol_type == GrammarSymbolType.TOKEN_NAME:
        return "SymbolParser(SymbolType." + tree.value(code) + ")"

    print(tree.symbol_type, " ", end="")
    raise NotImplementedError


def grammar_to_parsers(grammar_file: Path) -> str:
    """
    Reads the grammar file and generates a python parser file from it.
    """

    code = grammar_file.read_text()

    tree: Optional[Tree] = new_parse_generic(
        REWRITE_RULES, ROOT_SYMBOL, code, GrammarSymbolType
    )

    tree = prune_no_symbol(tree)

    assert tree
    print("tree size =", tree.size())

    tree = prune_zero_length(tree)

    assert tree
    print("tree size =", tree.size())

    tree = prune_by_symbol_types(
        tree,
        {
            GrammarSymbolType.WHITESPACE_LINE,
            GrammarSymbolType.WHITESPACE,
            GrammarSymbolType.COMMENT_LINE,
        },
        prune_subtree=True,
    )

    assert tree
    print("tree size =", tree.size())

    tree = prune_by_symbol_types(
        tree,
        {
            GrammarSymbolType.LINE,
            GrammarSymbolType.TOKEN_COMPOUND_EXPRESSION,
            GrammarSymbolType.TOKEN_EXPRESSION,
        },
        prune_subtree=False,
    )

    assert tree
    print("tree size =", tree.size())

    assert tree.symbol_type == GrammarSymbolType.FILE
    file = tree

    tokens: List[Tuple[str, Tree]] = []

    for token_definition in file.children:
        assert token_definition.symbol_type == GrammarSymbolType.TOKEN_DEFINITION_LINE
        tokens.append((token_definition[0].value(code), token_definition[1]))

    rewrite_rules_content = ""

    for token_name, token_expr in sorted(tokens):
        parser_expr = tree_to_python_parser_expression(token_expr, code)
        rewrite_rules_content += f"    SymbolType.{token_name}: {parser_expr},\n"

    available_parsers = [
        "ConcatenationParser",
        "LiteralParser",
        "OptionalParser",
        "OrParser",
        "Parser",
        "RegexBasedParser",
        "RepeatParser",
        "SymbolParser",
    ]

    used_parsers = [
        parser for parser in available_parsers if parser in rewrite_rules_content
    ]

    parser_script = "from enum import IntEnum, auto\n"
    parser_script += "from parser.parser import (\n"
    for parser in used_parsers:
        parser_script += f"    {parser},\n"

    parser_script += ")\n\n"
    parser_script += "from typing import Dict\n"

    parser_script += "\n\n"
    parser_script += "class SymbolType(IntEnum):\n"
    for token_name, _ in sorted(tokens):
        parser_script += f"    {token_name} = auto()\n"

    parser_script += "\n\n"
    parser_script += "REWRITE_RULES: Dict[IntEnum, Parser] = {\n"
    parser_script += rewrite_rules_content
    parser_script += "}\n"

    return parser_script
