import sys
from dataclasses import dataclass
from parser.exceptions import BaseParseError
from parser.grammar.parser import NonTerminal, Terminal
from parser.grammar.parser import parse as parse_grammar
from parser.parser.models import Tree
from parser.tokenizer.models import Token
from pathlib import Path
from typing import List, Optional, Set, Tuple

from black import FileMode, format_str


@dataclass
class ParsedGrammar:
    terminals: List[Tuple[str, Tree]]
    non_terminals: List[Tuple[str, Tree]]
    soft_pruned_non_terminals: Set[str]
    non_terminal_literals: List[str]
    pruned_terminals: Set[str]


class ParserGenerator:
    def __init__(self, grammar_path: Path) -> None:
        self.grammar_path = grammar_path.absolute()
        self.code = self.grammar_path.read_text()
        self.tokens, self.tree = parse_grammar(str(grammar_path), self.code)
        self._generated_parser_code: Optional[str] = None

    def _load_parsed_grammar(self) -> ParsedGrammar:
        # TODO make more readable
        parsed_grammar = ParsedGrammar([], [], set(), [], set())

        for grammar_item in self.tree.children:
            prune = False
            is_terminal = False

            for decorator in grammar_item.children[:-1]:
                assert decorator.token_type == NonTerminal.DECORATOR
                decorator_value = decorator[1].value(self.tokens, self.code)

                if decorator_value == "prune":
                    prune = True
                elif decorator_value == "token":
                    is_terminal = True
                else:  # pragma: nocover
                    raise NotImplementedError

            token_definition = grammar_item[-1]

            assert token_definition.token_type == NonTerminal.TOKEN_DEFINITION
            token_name = grammar_item[-1][0].value(self.tokens, self.code)

            if is_terminal:
                terminal = (token_name, token_definition[2])
                parsed_grammar.terminals.append(terminal)

                if prune:
                    parsed_grammar.pruned_terminals.add(token_name)

            else:
                non_terminal = (token_name, token_definition[2])
                parsed_grammar.non_terminals.append(non_terminal)

                if prune:
                    parsed_grammar.soft_pruned_non_terminals.add(token_name)

        return parsed_grammar

    def _generate_parser_code(self) -> str:  # pragma: nocover
        """
        Reads the grammar file and generates a python parser file from it.
        """
        if self._generated_parser_code:
            return self._generated_parser_code

        parsed_grammar = self._load_parsed_grammar()

        terminal_names = {item[0] for item in parsed_grammar.terminals}
        non_terminal_names = {item[0] for item in parsed_grammar.non_terminals}

        prefix_comments = "# ===================================== #\n"
        prefix_comments += "# THIS FILE WAS GENERATED, DO NOT EDIT! #\n"
        prefix_comments += "# ===================================== #\n\n"

        # This turns off formatting for flake8, pycln and black
        prefix_comments += "# flake8: noqa\n"
        prefix_comments += "# fmt: off\n"
        prefix_comments += "# nopycln: file\n\n"

        parser_code = ""
        parser_code += "from enum import IntEnum\n"
        parser_code += "from itertools import count\n"
        parser_code += "from parser.parser.models import (\n"
        parser_code += "    ConcatenationExpression,\n"
        parser_code += "    ConjunctionExpression,\n"
        parser_code += "    Expression,\n"
        parser_code += "    NonTerminalExpression,\n"
        parser_code += "    OptionalExpression,\n"
        parser_code += "    RepeatExpression,\n"
        parser_code += "    TerminalExpression,\n"
        parser_code += "    Tree,\n"
        parser_code += ")\n"
        parser_code += "from parser.parser.parser import Parser\n"
        parser_code += "from parser.tokenizer.models import Literal, Regex, Token, TokenDescriptor\n"
        parser_code += "from parser.tokenizer.tokenizer import Tokenizer\n"

        parser_code += "from typing import Dict, List, Optional, Set, Tuple\n"
        parser_code += "\n"

        parser_code += "# We can't use enum.auto, since Terminal and NonTerminal will have colliding values\n"
        parser_code += "next_offset = count(start=1)\n"
        parser_code += "\n\n"

        parser_code += "class Terminal(IntEnum):\n"
        for terminal_name, _ in sorted(parsed_grammar.terminals):
            parser_code += f"    {terminal_name} = next(next_offset)\n"
        parser_code += "\n\n"

        parser_code += "TERMINAL_RULES: List[TokenDescriptor] = [\n"
        for terminal_name, tree in parsed_grammar.terminals:
            token_descriptor = tree_to_python_token_descriptor(
                tree, self.tokens, self.code, terminal_name
            )
            parser_code += f"    {token_descriptor},\n"
        parser_code += "]\n\n\n"

        parser_code += "class NonTerminal(IntEnum):\n"
        for non_terminal_name, _ in sorted(parsed_grammar.non_terminals):
            parser_code += f"    {non_terminal_name} = next(next_offset)\n"
        parser_code += "\n\n"

        parser_code += "NON_TERMINAL_RULES: Dict[IntEnum, Expression] = {\n"
        for non_terminal_name, tree in sorted(parsed_grammar.non_terminals):
            parser_expr = tree_to_python_parser_expression(
                tree, self.tokens, self.code, terminal_names, non_terminal_names
            )
            parser_code += f"    NonTerminal.{non_terminal_name}: {parser_expr},\n"
        parser_code += "}\n\n\n"

        if parsed_grammar.pruned_terminals:
            parser_code += "PRUNED_TERMINALS: Set[IntEnum] = {\n"
            for name in sorted(parsed_grammar.pruned_terminals):
                parser_code += f"    Terminal.{name},\n"
            parser_code += "}\n\n\n"
        else:
            parser_code += "PRUNED_TERMINALS: Set[IntEnum] = set()\n\n\n"

        if parsed_grammar.soft_pruned_non_terminals:
            parser_code += "PRUNED_NON_TERMINALS: Set[IntEnum] = {\n"
            for non_terminal_name in sorted(parsed_grammar.soft_pruned_non_terminals):
                parser_code += f"    NonTerminal.{non_terminal_name},\n"
            parser_code += "}\n\n\n"
        else:
            parser_code += "PRUNED_NON_TERMINALS: Set[IntEnum] = set()\n\n\n"

        parser_code += (
            "def parse(filename: str, code: str) -> Tuple[List[Token], Tree]:\n"
            "    tokens: List[Token] = Tokenizer(\n"
            "        filename=filename,\n"
            "        code=code,\n"
            "        terminal_rules=TERMINAL_RULES,\n"
            "        pruned_terminals=PRUNED_TERMINALS,\n"
            "    ).tokenize()\n"
            "\n"
            "    tree: Tree = Parser(\n"
            "        filename=filename,\n"
            "        tokens=tokens,\n"
            "        code=code,\n"
            "        non_terminal_rules=NON_TERMINAL_RULES,\n"
            "        pruned_non_terminals=PRUNED_NON_TERMINALS,\n"
            '        root_token="ROOT"\n'
            "    ).parse()\n"
            "\n"
            "    return tokens, tree\n"
        )

        # format with black
        parser_code = format_str(parser_code, mode=FileMode())

        parser_code = prefix_comments + parser_code

        self._generated_parser_code = parser_code
        return parser_code

    def is_up_to_date(self, parser_path: Path) -> bool:
        if not parser_path.exists():
            return False

        return parser_path.read_text() == self._generate_parser_code()

    def write_if_stale(self, parser_path: Path) -> None:
        try:
            generated_code = self._generate_parser_code()
        except BaseParseError as e:
            print(e.args[0], file=sys.stderr)
            exit(1)

        if not self.is_up_to_date(parser_path):
            parser_path.write_text(generated_code)


def tree_to_python_token_descriptor(
    tree: Tree,
    tokens: List[Token],
    code: str,
    token_name: str,
) -> str:
    if tree.token_type == Terminal.LITERAL_EXPRESSION:
        literal = tree.value(tokens, code)
        return f"Literal(Terminal.{token_name}, {literal})"

    elif tree.token_type == NonTerminal.REGEX_EXPRESSION:
        regex = tree.children[1].value(tokens, code)
        return f"Regex(Terminal.{token_name}, {regex})"

    else:  # pragma: nocover
        raise NotImplementedError


def tree_to_python_parser_expression(
    tree: Tree,
    tokens: List[Token],
    code: str,
    terminal_names: Set[str],
    non_terminal_names: Set[str],
) -> str:
    if tree.token_type == NonTerminal.BRACKET_EXPRESSION:
        bracket_end = tree[2].value(tokens, code)
        child_expr = tree_to_python_parser_expression(
            tree[1], tokens, code, terminal_names, non_terminal_names
        )

        if bracket_end == ")":
            return child_expr
        elif bracket_end == ")*":
            return f"RepeatExpression({child_expr})"
        elif bracket_end == ")+":
            return (
                f"ConcatenationExpression({child_expr}, RepeatExpression({child_expr}))"
            )
        elif bracket_end == ")?":
            return f"OptionalExpression({child_expr})"
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
            "ConcatenationExpression("
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

        tail = tree[2]

        while tail.token_type == NonTerminal.CONJUNCTION_EXPRESSION:
            conjunc_items.append(tail[0])
            tail = tail[2]

        conjunc_items.append(tail)

        return (
            "ConjunctionExpression("
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
            return "TerminalExpression(Terminal." + tree.value(tokens, code) + ")"
        elif token_name in non_terminal_names:
            return "NonTerminalExpression(NonTerminal." + tree.value(tokens, code) + ")"
        else:
            raise NotImplementedError  # pragma: nocover

    raise NotImplementedError  # pragma: nocover
