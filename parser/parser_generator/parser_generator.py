import sys
from parser.exceptions import BaseParseError
from parser.grammar.parser import NonTerminal, Terminal
from parser.grammar.parser import parse as parse_grammar
from parser.parser.models import Tree
from parser.parser_generator.exceptions import UnknownTokenException
from parser.parser_generator.models import ParsedGrammar
from pathlib import Path
from typing import Optional

from black import FileMode, format_str


class ParserGenerator:
    def __init__(self, grammar_path: Path) -> None:
        self.grammar_path = grammar_path.absolute()
        self.code = self.grammar_path.read_text()
        self.tokens, self.tree = parse_grammar(str(grammar_path), self.code)
        self._generated_parser_code: Optional[str] = None
        self._parsed_grammar = self._load_parsed_grammar()

    def _load_parsed_grammar(self) -> ParsedGrammar:

        parsed_grammar = ParsedGrammar.empty()

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
                    parsed_grammar.pruned_non_terminals.add(token_name)

        return parsed_grammar

    def _generate_parser_code(self) -> str:  # pragma: nocover
        """
        Reads the grammar file and generates a python parser file from it.
        """
        if self._generated_parser_code:
            return self._generated_parser_code

        prefix_comments = (
            "# ================================================================= #\n"
            "#        THIS FILE WAS AUTOMATICALLY GENERATED, DO NOT EDIT!        #\n"
            "# ================================================================= #\n"
            "\n"
            "# This turns off formatting for flake8, pycln and black\n"
            "# flake8: noqa\n"
            "# fmt: off\n"
            "# nopycln: file\n"
            "\n"
        )

        parser_code = (
            "from enum import IntEnum\n"
            "from itertools import count\n"
            "from parser.parser.models import (\n"
            "    ConcatenationExpression,\n"
            "    ConjunctionExpression,\n"
            "    Expression,\n"
            "    NonTerminalExpression,\n"
            "    OptionalExpression,\n"
            "    RepeatExpression,\n"
            "    TerminalExpression,\n"
            "    Tree,\n"
            ")\n"
            "from parser.parser.parser import Parser\n"
            "from parser.tokenizer.models import Literal, Regex, Token, TokenDescriptor\n"
            "from parser.tokenizer.tokenizer import Tokenizer\n"
            "from typing import Dict, List, Optional, Set, Tuple\n"
            "\n"
            "# We can't use enum.auto, since Terminal and NonTerminal will have colliding values\n"
            "next_offset = count(start=1)\n"
            "\n"
            "\n"
        )

        parser_code += "class Terminal(IntEnum):\n"
        for terminal_name, _ in sorted(self._parsed_grammar.terminals):
            parser_code += f"    {terminal_name} = next(next_offset)\n"
        parser_code += "\n\n"

        parser_code += "TERMINAL_RULES: List[TokenDescriptor] = [\n"
        for terminal_name, tree in self._parsed_grammar.terminals:
            token_descriptor = self._tree_to_token_descriptor_code(tree, terminal_name)
            parser_code += f"    {token_descriptor},\n"
        parser_code += "]\n\n\n"

        parser_code += "class NonTerminal(IntEnum):\n"
        for non_terminal_name, _ in sorted(self._parsed_grammar.non_terminals):
            parser_code += f"    {non_terminal_name} = next(next_offset)\n"
        parser_code += "\n\n"

        parser_code += "NON_TERMINAL_RULES: Dict[IntEnum, Expression] = {\n"
        for non_terminal_name, tree in sorted(self._parsed_grammar.non_terminals):
            parser_expr = self._tree_to_expression_code(tree)
            parser_code += f"    NonTerminal.{non_terminal_name}: {parser_expr},\n"
        parser_code += "}\n\n\n"

        if self._parsed_grammar.pruned_terminals:
            parser_code += "PRUNED_TERMINALS: Set[IntEnum] = {\n"
            for name in sorted(self._parsed_grammar.pruned_terminals):
                parser_code += f"    Terminal.{name},\n"
            parser_code += "}\n\n\n"
        else:
            parser_code += "PRUNED_TERMINALS: Set[IntEnum] = set()\n\n\n"

        if self._parsed_grammar.pruned_non_terminals:
            parser_code += "PRUNED_NON_TERMINALS: Set[IntEnum] = {\n"
            for non_terminal_name in sorted(self._parsed_grammar.pruned_non_terminals):
                parser_code += f"    NonTerminal.{non_terminal_name},\n"
            parser_code += "}\n\n\n"
        else:
            parser_code += "PRUNED_NON_TERMINALS: Set[IntEnum] = set()\n\n\n"

        parser_code += (
            "def parse(filename: str, code: str) -> Tuple[List[Token], Tree]:\n"
            "\n"
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
            print(e.what(), file=sys.stderr)
            exit(1)

        if not self.is_up_to_date(parser_path):
            parser_path.write_text(generated_code)

    def _tree_to_token_descriptor_code(
        self,
        tree: Tree,
        token_name: str,
    ) -> str:
        if tree.token_type == Terminal.LITERAL_EXPRESSION:
            literal = tree.value(self.tokens, self.code)
            return f"Literal(Terminal.{token_name}, {literal})"

        elif tree.token_type == NonTerminal.REGEX_EXPRESSION:
            regex = tree.children[1].value(self.tokens, self.code)
            return f"Regex(Terminal.{token_name}, {regex})"

        else:  # pragma: nocover
            raise NotImplementedError

    def _is_valid_terminal(self, terminal_name: str) -> bool:
        return any(
            terminal_pair[0] == terminal_name
            for terminal_pair in self._parsed_grammar.terminals
        )

    def _is_valid_non_terminal(self, terminal_name: str) -> bool:
        return any(
            non_terminal_pair[0] == terminal_name
            for non_terminal_pair in self._parsed_grammar.non_terminals
        )

    def _tree_to_expression_code(
        self,
        tree: Tree,
    ) -> str:
        if tree.token_type == NonTerminal.BRACKET_EXPRESSION:
            bracket_end = tree[2].value(self.tokens, self.code)
            child_expr = self._tree_to_expression_code(tree[1])

            if bracket_end == ")":
                return child_expr
            elif bracket_end == ")*":
                return f"RepeatExpression({child_expr})"
            elif bracket_end == ")+":
                return f"ConcatenationExpression({child_expr}, RepeatExpression({child_expr}))"
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
                    self._tree_to_expression_code(concat_item)
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
                    self._tree_to_expression_code(conjunc_item)
                    for conjunc_item in conjunc_items
                )
                + ")"
            )

        elif tree.token_type == Terminal.TOKEN_NAME:
            token_name = tree.value(self.tokens, self.code)

            if self._is_valid_terminal(token_name):
                return (
                    "TerminalExpression(Terminal."
                    + tree.value(self.tokens, self.code)
                    + ")"
                )
            elif self._is_valid_non_terminal(token_name):
                return (
                    "NonTerminalExpression(NonTerminal."
                    + tree.value(self.tokens, self.code)
                    + ")"
                )
            else:
                code_offset = self.tokens[tree.token_offset].offset
                raise UnknownTokenException(
                    str(self.grammar_path), self.code, code_offset, token_name
                )

        raise NotImplementedError  # pragma: nocover
