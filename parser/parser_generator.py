from dataclasses import dataclass
from parser.grammar.parser import SymbolType, parse
from parser.tree import Tree
from pathlib import Path
from typing import List, Optional, Set, Tuple


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
            min_repeats = int(tree[1][0][0].value(code))
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
        return "SymbolParser(NonTerminal." + tree.value(code) + ")"

    raise NotImplementedError  # pragma: nocover


class InvalidTree(Exception):
    def __init__(self, invalid_thing: str):
        self.symbol_type = invalid_thing
        super().__init__(f"{invalid_thing} is not allowed.")


def check_terminal_tree(tree: Tree, code: str) -> None:
    if tree.symbol_type in [SymbolType.LITERAL_EXPRESSION, SymbolType.REGEX_EXPRESSION]:
        pass
    elif tree.symbol_type == SymbolType.TOKEN_NAME:
        raise InvalidTree(tree.symbol_type.name)
    elif tree.symbol_type == SymbolType.BRACKET_EXPRESSION:
        bracket_end = tree[1].value(code)

        if bracket_end == ")":
            check_terminal_tree(tree[0], code)
        elif bracket_end in [")*", ")+", ")?"] or bracket_end.startswith("){"):
            raise InvalidTree(bracket_end)
        else:  # pragma: nocover
            raise NotImplementedError

    elif tree.symbol_type in [
        SymbolType.CONCATENATION_EXPRESSION,
        SymbolType.CONJUNCTION_EXPRESSION,
    ]:
        for child in tree.children:
            check_terminal_tree(child, code)
    else:
        raise NotImplementedError  # pragma: nocover


def check_non_terminal_tree(tree: Tree, code: str) -> None:
    # TODO
    raise NotImplementedError


@dataclass
class ParsedGrammar:
    terminals: List[Tuple[str, Tree]]
    non_terminals: List[Tuple[str, Tree]]
    hard_pruned_non_terminals: Set[str]
    soft_pruned_non_terminals: Set[str]


def load_parsed_grammar(file: Tree, code: str) -> ParsedGrammar:

    parsed_grammar = ParsedGrammar([], [], set(), set())

    prune_decorator: Optional[str] = None
    is_token = False

    for file_child in file.children:

        if file_child.symbol_type == SymbolType.DECORATOR_LINE:
            decorator = file_child[0].value(code)

            if decorator.startswith("prune"):
                prune_decorator = decorator
            elif decorator == "token":
                is_token = True
            else:  # pragma: nocover
                raise NotImplementedError

        if file_child.symbol_type == SymbolType.TOKEN_DEFINITION_LINE:
            name = file_child[0].value(code)

            if is_token:
                terminal = (name, file_child[1])
                parsed_grammar.terminals.append(terminal)
            else:
                non_terminal = (name, file_child[1])
                parsed_grammar.non_terminals.append(non_terminal)

                if prune_decorator:
                    if prune_decorator == "prune hard":
                        parsed_grammar.hard_pruned_non_terminals.add(name)
                    elif prune_decorator == "prune soft":
                        parsed_grammar.soft_pruned_non_terminals.add(name)
                    else:  # pragma: nocover
                        raise NotImplementedError

            prune_decorator = None
            is_token = False

    for name, tree in parsed_grammar.terminals:
        try:
            check_terminal_tree(tree, code)
        except InvalidTree as e:
            raise ValueError(f"Invalid tree for terminal {name}: {e}") from e

    for name, tree in parsed_grammar.non_terminals:
        try:
            check_non_terminal_tree(tree, code)
        except InvalidTree as e:
            raise ValueError(f"Invalid tree for non_terminal {name}: {e}") from e

    return parsed_grammar


def generate_parser(grammar_path: Path) -> str:  # pragma: nocover
    """
    Reads the grammar file and generates a python parser file from it.
    """

    code = grammar_path.read_text()
    tree = parse(code)

    assert tree.symbol_type == SymbolType.ROOT
    parsed_grammar = load_parsed_grammar(tree, code)

    prefix_comments = "# ===================================== #\n"
    prefix_comments += "# THIS FILE WAS GENERATED, DO NOT EDIT! #\n"
    prefix_comments += "# ===================================== #\n\n"

    # This turns off formatting for flake8, pycln and black
    prefix_comments += "# flake8: noqa\n"
    prefix_comments += "# fmt: off\n"
    prefix_comments += "# nopycln: file\n\n"

    parser_script = ""
    parser_script += "from enum import IntEnum, auto\n"
    parser_script += "from parser.parser import (\n"
    parser_script += "    ConcatenationParser,\n"
    parser_script += "    LiteralParser,\n"
    parser_script += "    OptionalParser,\n"
    parser_script += "    OrParser,\n"
    parser_script += "    Parser,\n"
    parser_script += "    RegexBasedParser,\n"
    parser_script += "    RepeatParser,\n"
    parser_script += "    SymbolParser,\n"
    parser_script += "    parse_generic,\n"
    parser_script += ")\n"
    parser_script += "from parser.tree import Tree, prune_by_symbol_types\n"
    parser_script += "from typing import Dict, Final, Optional, Set, List, Tuple\n"
    parser_script += "\n\n"

    parser_script += "class NonTerminal(IntEnum):\n"
    for non_terminal_name, _ in sorted(parsed_grammar.non_terminals):
        parser_script += f"    {non_terminal_name} = auto()\n"
    parser_script += "\n\n"

    parser_script += "NON_TERMINAL_RULES: Final[Dict[IntEnum, Parser]] = {\n"
    for non_terminal_name, tree in sorted(parsed_grammar.non_terminals):
        parser_expr = tree_to_python_parser_expression(tree, code)
        parser_script += f"    NonTerminal.{non_terminal_name}: {parser_expr},\n"
    parser_script += "}\n\n\n"

    parser_script += "class Terminal(IntEnum):\n"
    for terminal_name, _ in sorted(parsed_grammar.terminals):
        parser_script += f"    {terminal_name} = auto()\n"
    parser_script += "\n\n"

    parser_script += "TERMINAL_RULES: Final[List[Tuple[IntEnum, Parser]]] = [\n"
    for non_terminal_name, tree in sorted(parsed_grammar.terminals):
        parser_expr = tree_to_python_parser_expression(tree, code)
        parser_script += f"    (Terminal.{non_terminal_name}, {parser_expr}),\n"
    parser_script += "]\n\n\n"

    parser_script += "HARD_PRUNED_SYMBOL_TYPES: Set[IntEnum] = {\n"
    for non_terminal_name in sorted(parsed_grammar.hard_pruned_non_terminals):
        parser_script += f"    NonTerminal.{non_terminal_name},\n"
    parser_script += "}\n\n\n"

    parser_script += "SOFT_PRUNED_SYMBOL_TYPES: Set[IntEnum] = {\n"
    for non_terminal_name in sorted(parsed_grammar.soft_pruned_non_terminals):
        parser_script += f"    NonTerminal.{non_terminal_name},\n"
    parser_script += "}\n\n\n"

    parser_script += "def parse(code: str) -> Tree:\n"
    parser_script += "    return parse_generic(NON_TERMINAL_RULES, code, HARD_PRUNED_SYMBOL_TYPES, SOFT_PRUNED_SYMBOL_TYPES)\n"

    # format with black
    # TODO parser_script = format_str(parser_script, mode=FileMode())

    return prefix_comments + parser_script


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
