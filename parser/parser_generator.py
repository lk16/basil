from parser.grammar.parser import SymbolType, parse
from parser.tree import Tree
from pathlib import Path
from typing import List, Optional, Set, Tuple

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

    assert tree
    assert tree.symbol_type == SymbolType.ROOT
    file = tree

    tokens: List[Tuple[str, Tree]] = []

    hard_pruned_tokens: Set[str] = set()
    soft_pruned_tokens: Set[str] = set()
    last_decorator_value: Optional[str] = None

    for file_child in file.children:
        if file_child.symbol_type == SymbolType.DECORATOR_LINE:
            last_decorator_value = file_child[0].value(code)

        if file_child.symbol_type == SymbolType.TOKEN_DEFINITION_LINE:
            token_name = file_child[0].value(code)
            tokens.append((token_name, file_child[1]))

            if last_decorator_value:
                if last_decorator_value == "prune hard":
                    hard_pruned_tokens.add(token_name)
                elif last_decorator_value == "prune soft":
                    soft_pruned_tokens.add(token_name)
                else:
                    raise NotImplementedError

                last_decorator_value = None

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

    prefix_comments = "# ===================================== #\n"
    prefix_comments += "# THIS FILE WAS GENERATED, DO NOT EDIT! #\n"
    prefix_comments += "# ===================================== #\n\n"

    # This turns off formatting for flake8 and black
    prefix_comments += "# flake8: noqa\n"
    prefix_comments += "# fmt: off\n\n"

    parser_script = ""

    parser_script += "from enum import IntEnum, auto\n"
    parser_script += "from parser.parser import (\n"
    for parser in used_parsers:
        parser_script += f"    {parser},\n"

    parser_script += f"     parse_generic,\n"

    parser_script += ")\n"
    parser_script += "from parser.tree import Tree, prune_by_symbol_types\n"
    parser_script += "from typing import Dict, Final, Optional, Set\n"

    parser_script += "\n\n"
    parser_script += "class SymbolType(IntEnum):\n"
    for token_name, _ in sorted(tokens):
        parser_script += f"    {token_name} = auto()\n"
    parser_script += "\n\n"

    parser_script += "REWRITE_RULES: Final[Dict[IntEnum, Parser]] = {\n"
    parser_script += rewrite_rules_content
    parser_script += "}\n\n\n"

    if hard_pruned_tokens:
        parser_script += "HARD_PRUNED_SYMBOL_TYPES: Set[IntEnum] = {\n"
        for token_name in sorted(hard_pruned_tokens):
            parser_script += f"    SymbolType.{token_name},\n"
        parser_script += "}\n\n\n"

    if soft_pruned_tokens:
        parser_script += "SOFT_PRUNED_SYMBOL_TYPES: Set[IntEnum] = {\n"
        for token_name in sorted(soft_pruned_tokens):
            parser_script += f"    SymbolType.{token_name},\n"
        parser_script += "}\n\n\n"

    parser_script += "def parse(code: str) -> Tree:\n"
    parser_script += "    tree: Optional[Tree] = parse_generic(REWRITE_RULES, code)\n\n"

    if hard_pruned_tokens:
        parser_script += "    tree = prune_by_symbol_types(tree, HARD_PRUNED_SYMBOL_TYPES, prune_subtree=True)\n"
        parser_script += "    assert tree\n\n"

    if soft_pruned_tokens:
        parser_script += "    tree = prune_by_symbol_types(tree, SOFT_PRUNED_SYMBOL_TYPES, prune_subtree=False)\n"
        parser_script += "    assert tree\n\n"

    parser_script += "    return tree\n"

    # format with black
    formatted_script: str = format_str(parser_script, mode=FileMode())

    return prefix_comments + formatted_script


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
