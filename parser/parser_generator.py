import re
import sys
from dataclasses import dataclass
from parser.exceptions import ParseError
from parser.grammar.parser import NonTerminal, Terminal, parse
from parser.tree import Token, Tree
from pathlib import Path
from typing import List, Optional, Set, Tuple

from black import FileMode, format_str


class UnknownTokenError(Exception):
    def __init__(self, token_name: str) -> None:
        self.token_name = token_name
        super().__init__(f"Unknown token name {token_name}")


def tree_to_python_parser_expression(
    tree: Tree,
    tokens: List[Token],
    code: str,
    terminal_names: Set[str],
    non_terminal_names: Set[str],
) -> str:
    if tree.token_type == Terminal.LITERAL_EXPRESSION:
        value = tree.value(tokens, code)
        return f"LiteralParser({value})"

    elif tree.token_type == NonTerminal.REGEX_EXPRESSION:
        regex_value = tree[0].value(tokens, code)
        return f"RegexTokenizer({regex_value})"

    elif tree.token_type == NonTerminal.BRACKET_EXPRESSION:
        bracket_end = tree[1].value(tokens, code)
        child_expr = tree_to_python_parser_expression(
            tree[0], tokens, code, terminal_names, non_terminal_names
        )

        if bracket_end == ")":
            return child_expr
        elif bracket_end == ")*":
            return f"RepeatParser({child_expr})"
        elif bracket_end == ")+":
            return f"RepeatParser({child_expr}, min_repeats=1)"
        elif bracket_end == ")?":
            return f"OptionalParser({child_expr})"
        elif bracket_end.startswith("){"):
            min_repeats = int(tree[1][0][0].value(tokens, code))
            return f"RepeatParser({child_expr}, min_repeats={min_repeats})"
        else:  # pragma: nocover
            raise NotImplementedError

    elif tree.token_type == NonTerminal.CONCATENATION_EXPRESSION:
        conjunc_items = [tree[0]]

        tail = tree[1]

        while tail.token_type == NonTerminal.CONCATENATION_EXPRESSION:
            conjunc_items.append(tail[0])
            tail = tail[1]

        conjunc_items.append(tail)

        return (
            "ConcatenationParser("
            + ", ".join(
                tree_to_python_parser_expression(
                    concat_item, tokens, code, terminal_names, non_terminal_names
                )
                for concat_item in conjunc_items
            )
            + ")"
        )

    elif tree.token_type == NonTerminal.CONJUNCTION_EXPRESSION:
        conjunc_items = [tree[0]]

        tail = tree[1]

        while tail.token_type == NonTerminal.CONJUNCTION_EXPRESSION:
            conjunc_items.append(tail[0])
            tail = tail[1]

        conjunc_items.append(tail)

        return (
            "OrParser("
            + ", ".join(
                tree_to_python_parser_expression(
                    conjunc_item, tokens, code, terminal_names, non_terminal_names
                )
                for conjunc_item in conjunc_items
            )
            + ")"
        )

    elif tree.token_type == Terminal.TOKEN_NAME:
        token_name = tree.value(tokens, code)

        if token_name in terminal_names:
            return "TerminalParser(Terminal." + tree.value(tokens, code) + ")"
        elif token_name in non_terminal_names:
            return "NonTerminalParser(NonTerminal." + tree.value(tokens, code) + ")"
        else:
            raise UnknownTokenError(token_name)

    raise NotImplementedError  # pragma: nocover


class InvalidTree(Exception):
    def __init__(self, invalid_thing: str):
        self.symbol_type = invalid_thing
        super().__init__(f"{invalid_thing} is not allowed.")


def check_terminal_tree(tree: Tree) -> None:
    if tree.token_type != NonTerminal.REGEX_EXPRESSION:
        raise InvalidTree("only REGEX_EXPRESSION is allowed")


def check_non_terminal_tree(tree: Tree) -> None:
    if tree.token_type == NonTerminal.REGEX_EXPRESSION:
        raise InvalidTree(tree.token_type.name)
    elif tree.token_type in [Terminal.TOKEN_NAME, Terminal.LITERAL_EXPRESSION]:
        pass
    elif tree.token_type == NonTerminal.BRACKET_EXPRESSION:
        check_non_terminal_tree(tree[0])
    elif tree.token_type in [
        NonTerminal.CONCATENATION_EXPRESSION,
        NonTerminal.CONJUNCTION_EXPRESSION,
    ]:
        for child in tree.children:
            check_non_terminal_tree(child)
    else:  # pragma: nocover
        raise NotImplementedError


def get_non_terminal_literals(tree: Tree, tokens: List[Token], code: str) -> List[str]:
    if tree.token_type in [NonTerminal.REGEX_EXPRESSION, Terminal.TOKEN_NAME]:
        return []
    if tree.token_type == Terminal.LITERAL_EXPRESSION:
        literal_value = tree.value(tokens, code)[1:-1]
        return [literal_value]
    elif tree.token_type == NonTerminal.BRACKET_EXPRESSION:
        return get_non_terminal_literals(tree[0], tokens, code)
    elif tree.token_type in [
        NonTerminal.CONCATENATION_EXPRESSION,
        NonTerminal.CONJUNCTION_EXPRESSION,
    ]:
        literals = []
        for child in tree.children:
            literals += get_non_terminal_literals(child, tokens, code)
        return literals
    else:  # pragma: nocover
        raise NotImplementedError


@dataclass
class ParsedGrammar:
    terminals: List[Tuple[str, Tree]]
    non_terminals: List[Tuple[str, Tree]]
    hard_pruned_non_terminals: Set[str]
    soft_pruned_non_terminals: Set[str]
    non_terminal_literals: List[str]
    pruned_terminals: Set[str]


def load_parsed_grammar(  # noqa: C901
    tree: Tree, tokens: List[Token], code: str
) -> ParsedGrammar:

    parsed_grammar = ParsedGrammar([], [], set(), set(), [], set())

    prune_decorator: Optional[str] = None
    is_terminal = False

    for file_child in tree.children:

        if file_child.token_type == NonTerminal.DECORATOR:
            decorator = file_child[0].value(tokens, code)

            if decorator.startswith("prune"):
                prune_decorator = decorator
            elif decorator == "token":
                is_terminal = True
            else:  # pragma: nocover
                raise NotImplementedError

        if file_child.token_type == NonTerminal.TOKEN_DEFINITION:
            name = file_child[0].value(tokens, code)

            if is_terminal:
                terminal = (name, file_child[1])
                parsed_grammar.terminals.append(terminal)

                if prune_decorator:
                    if prune_decorator == "prune hard":
                        parsed_grammar.pruned_terminals.add(name)
                    elif prune_decorator == "prune soft":
                        raise ValueError("Soft pruning doesn't make sense for tokens")
                    else:  # pragma: nocover
                        raise NotImplementedError

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
            is_terminal = False

    non_terminal_literals: List[str] = []

    for _, tree in parsed_grammar.non_terminals:
        non_terminal_literals += get_non_terminal_literals(tree, tokens, code)

    # remove duplicates and sort such that longest items come first
    parsed_grammar.non_terminal_literals = sorted(
        set(non_terminal_literals), key=lambda x: len(x), reverse=True
    )

    for name, tree in parsed_grammar.terminals:
        try:
            check_terminal_tree(tree)
        except InvalidTree as e:
            raise ValueError(f"Invalid tree for terminal {name}: {e}") from e

    for name, tree in parsed_grammar.non_terminals:
        try:
            check_non_terminal_tree(tree)
        except InvalidTree as e:
            raise ValueError(f"Invalid tree for non_terminal {name}: {e}") from e

    return parsed_grammar


def generate_parser(grammar_path: Path) -> str:  # pragma: nocover
    """
    Reads the grammar file and generates a python parser file from it.
    """

    code = grammar_path.read_text()
    tokens, tree = parse(code)

    assert tree.token_type == NonTerminal.ROOT
    parsed_grammar = load_parsed_grammar(tree, tokens, code)

    terminal_names = {item[0] for item in parsed_grammar.terminals}
    non_terminal_names = {item[0] for item in parsed_grammar.non_terminals}

    non_terminal_literal_parser_expr = (
        'RegexTokenizer("'
        + "|".join(
            re.escape(literal) for literal in parsed_grammar.non_terminal_literals
        )
        + '")'
    )

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
    parser_script += "    NonTerminalParser,\n"
    parser_script += "    OptionalParser,\n"
    parser_script += "    OrParser,\n"
    parser_script += "    Parser,\n"
    parser_script += "    RepeatParser,\n"
    parser_script += "    TerminalParser,\n"
    parser_script += "    parse_generic,\n"
    parser_script += ")\n"
    parser_script += "from parser.tokenizer import RegexTokenizer, tokenize\n"
    parser_script += "from parser.tree import Tree, Token\n"
    parser_script += "from typing import Dict, Optional, Set, List, Tuple\n"
    parser_script += "\n\n"

    parser_script += "class Terminal(IntEnum):\n"
    for terminal_name, _ in sorted(parsed_grammar.terminals):
        parser_script += f"    {terminal_name} = auto()\n"
    parser_script += "\n\n"

    parser_script += "TERMINAL_RULES: List[Tuple[IntEnum, RegexTokenizer]] = [\n"
    for non_terminal_name, tree in parsed_grammar.terminals:
        parser_expr = tree_to_python_parser_expression(
            tree, tokens, code, terminal_names, non_terminal_names
        )
        parser_script += f"    (Terminal.{non_terminal_name}, {parser_expr}),\n"
    parser_script += "]\n\n\n"

    parser_script += "class NonTerminal(IntEnum):\n"
    for non_terminal_name, _ in sorted(parsed_grammar.non_terminals):
        parser_script += f"    {non_terminal_name} = auto()\n"
    parser_script += "\n\n"

    parser_script += "NON_TERMINAL_RULES: Dict[IntEnum, Parser] = {\n"
    for non_terminal_name, tree in sorted(parsed_grammar.non_terminals):
        parser_expr = tree_to_python_parser_expression(
            tree, tokens, code, terminal_names, non_terminal_names
        )
        parser_script += f"    NonTerminal.{non_terminal_name}: {parser_expr},\n"
    parser_script += "}\n\n\n"

    if parsed_grammar.pruned_terminals:
        parser_script += "PRUNED_TERMINALS: Set[IntEnum] = {\n"
        for name in sorted(parsed_grammar.pruned_terminals):
            parser_script += f"    Terminal.{name},\n"
        parser_script += "}\n\n\n"
    else:
        parser_script += "PRUNED_TERMINALS: Set[IntEnum] = set()\n\n\n"

    if parsed_grammar.hard_pruned_non_terminals:
        parser_script += "HARD_PRUNED_NON_TERMINALS: Set[IntEnum] = {\n"
        for non_terminal_name in sorted(parsed_grammar.hard_pruned_non_terminals):
            parser_script += f"    NonTerminal.{non_terminal_name},\n"
        parser_script += "}\n\n\n"
    else:
        parser_script += "HARD_PRUNED_NON_TERMINALS: Set[IntEnum] = set()\n\n\n"

    if parsed_grammar.soft_pruned_non_terminals:
        parser_script += "SOFT_PRUNED_NON_TERMINALS: Set[IntEnum] = {\n"
        for non_terminal_name in sorted(parsed_grammar.soft_pruned_non_terminals):
            parser_script += f"    NonTerminal.{non_terminal_name},\n"
        parser_script += "}\n\n\n"
    else:
        parser_script += "SOFT_PRUNED_NON_TERMINALS: Set[IntEnum] = set()\n\n\n"

    parser_script += "def parse(code: str) -> Tuple[List[Token], Tree]:\n"
    parser_script += "    tokens: List[Token] = tokenize(code, TERMINAL_RULES)\n"
    parser_script += "    tree: Tree = parse_generic(NON_TERMINAL_RULES, tokens, code, HARD_PRUNED_NON_TERMINALS, SOFT_PRUNED_NON_TERMINALS)\n"
    parser_script += "    return tokens, tree\n"

    # format with black
    parser_script = format_str(parser_script, mode=FileMode())

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
    try:
        generated_parser = generate_parser(grammar_path)
    except ParseError as e:
        print(e.args[0], file=sys.stderr)
        exit(1)

    if check_parser_staleness(generated_parser, parser_path):
        parser_path.write_text(generated_parser)
