from parser.grammar.parser import SymbolType, parse
from parser.tree import Tree, prune_by_symbol_types
from pathlib import Path
from typing import List, Optional, Tuple

from black import FileMode, format_str


def tree_to_python_parser_expression(tree: Tree, code: str) -> str:

    if tree.symbol_type == SymbolType.LITERAL_EXPRESSION:
        value = tree.value(code)
        return f"LiteralParser({value})"

    elif tree.symbol_type == SymbolType.REGEX_EXPRESSION:
        regex_value = tree[0].value(code)
        return f"RegexBasedParser({regex_value})"

    elif tree.symbol_type == SymbolType.BRACKET_EXPRESSION:
        bracket_end = tree[1].value(code)
        child_expr = tree_to_python_parser_expression(tree[0], code)

        if bracket_end == ")":
            return child_expr
        elif bracket_end == ")*":
            return f"RepeatParser({child_expr})"
        elif bracket_end == ")+":
            return f"RepeatParser({child_expr}, min_repeats=1)"
        elif bracket_end == ")?":
            return f"OptionalParser({child_expr})"
        elif bracket_end.startswith("){"):
            min_repeats = int(tree[1][0].value(code))
            return f"RepeatParser({child_expr}, min_repeats={min_repeats})"
        else:  # pragma: nocover
            raise NotImplementedError

    elif tree.symbol_type == SymbolType.CONCATENATION_EXPRESSION:
        conjunc_items = [tree[0]]

        tail = tree[1]

        while tail.symbol_type == SymbolType.CONCATENATION_EXPRESSION:
            conjunc_items.append(tail[0])
            tail = tail[1]

        conjunc_items.append(tail)

        return (
            "ConcatenationParser("
            + ", ".join(
                tree_to_python_parser_expression(concat_item, code)
                for concat_item in conjunc_items
            )
            + ")"
        )

    elif tree.symbol_type == SymbolType.CONJUNCTION_EXPRESSION:
        conjunc_items = [tree[0]]

        tail = tree[1]

        while tail.symbol_type == SymbolType.CONJUNCTION_EXPRESSION:
            conjunc_items.append(tail[0])
            tail = tail[1]

        conjunc_items.append(tail)

        return (
            "OrParser("
            + ", ".join(
                tree_to_python_parser_expression(conjunc_item, code)
                for conjunc_item in conjunc_items
            )
            + ")"
        )

    elif tree.symbol_type == SymbolType.TOKEN_NAME:
        return "SymbolParser(SymbolType." + tree.value(code) + ")"

    raise NotImplementedError  # pragma: nocover


def generate_parser(grammar_path: Path) -> str:  # pragma: nocover
    """
    Reads the grammar file and generates a python parser file from it.
    """

    code = grammar_path.read_text()

    tree: Optional[Tree] = parse(code)

    tree = prune_by_symbol_types(
        tree,
        {
            SymbolType.WHITESPACE_LINE,
            SymbolType.WHITESPACE,
            SymbolType.COMMENT_LINE,
        },
        prune_subtree=True,
    )

    tree = prune_by_symbol_types(
        tree,
        {
            SymbolType.LINE,
            SymbolType.TOKEN_COMPOUND_EXPRESSION,
            SymbolType.TOKEN_EXPRESSION,
        },
        prune_subtree=False,
    )

    assert tree
    assert tree.symbol_type == SymbolType.ROOT
    file = tree

    tokens: List[Tuple[str, Tree]] = []

    for token_definition in file.children:
        assert token_definition.symbol_type == SymbolType.TOKEN_DEFINITION_LINE
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

    parser_script = ""

    parser_script += "# ===================================== #\n"
    parser_script += "# THIS FILE WAS GENERATED, DO NOT EDIT! #\n"
    parser_script += "# ===================================== #\n\n"

    parser_script += "# flake8: noqa\n"

    parser_script += "from enum import IntEnum, auto\n"
    parser_script += "from parser.parser import (\n"
    for parser in used_parsers:
        parser_script += f"    {parser},\n"

    parser_script += f"     parse_generic,\n"

    parser_script += ")\n"
    parser_script += "from parser.tree import Tree\n"
    parser_script += "from typing import Dict, Final\n"

    parser_script += "\n\n"
    parser_script += "class SymbolType(IntEnum):\n"
    for token_name, _ in sorted(tokens):
        parser_script += f"    {token_name} = auto()\n"

    parser_script += "\n\n"
    parser_script += "REWRITE_RULES: Final[Dict[IntEnum, Parser]] = {\n"
    parser_script += rewrite_rules_content
    parser_script += "}\n"

    parser_script += "\n\n"
    parser_script += "def parse(code: str) -> Tree:\n"
    parser_script += "    return parse_generic(REWRITE_RULES, code)\n"

    # format with black
    return format_str(parser_script, mode=FileMode())  # type: ignore


def check_parser_staleness(
    generated_parser: str, parser_path: Path
) -> bool:  # pragma: nocover
    if not parser_path.exists():
        return True

    return parser_path.read_text() != generated_parser


def regenerate_parser_if_stale(
    grammar_path: Path, parser_path: Path
) -> None:  # pragma: nocover
    generated_parser = generate_parser(grammar_path)

    if check_parser_staleness(generated_parser, parser_path):
        parser_path.write_text(generated_parser)
