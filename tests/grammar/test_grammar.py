from parser.grammar.parser import (
    NON_TERMINAL_RULES,
    PRUNED_NON_TERMINALS,
    PRUNED_TERMINALS,
    TERMINAL_RULES,
)
from parser.parser.models import Tree
from parser.parser.parser import Parser
from parser.parser_generator.parser_generator import ParserGenerator
from parser.tokenizer.tokenizer import Tokenizer
from pathlib import Path

import pytest


def test_grammar_up_to_date() -> None:
    grammar_file = Path("parser/grammar/grammar.txt")
    parser_file = Path("parser/grammar/parser.py")

    assert ParserGenerator(grammar_file).is_up_to_date(parser_file)


def parse_as(code: str, non_terminal_name: str) -> Tree:
    filename = "foo.txt"

    tokens = Tokenizer(
        filename=filename,
        code=code,
        terminal_rules=TERMINAL_RULES,
        pruned_terminals=PRUNED_TERMINALS,
    ).tokenize()

    return Parser(
        filename=filename,
        tokens=tokens,
        code=code,
        non_terminal_rules=NON_TERMINAL_RULES,
        pruned_non_terminals=PRUNED_NON_TERMINALS,
        root_token=non_terminal_name,
    ).parse()


@pytest.mark.parametrize(
    ["code"],
    [
        # basic
        ("A",),
        # bracket
        ("(A)",),
        ("( A )",),
        # concatenate
        ("A B",),
        # conjunction
        ("A|B",),
        ("A | B",),
        # bracket bracket
        ("((A))",),
        # bracket concatenate
        ("(A) (B)",),
        # bracket conjunction
        ("(A) | (B)",),
        # concatenate bracket
        ("(A B)",),
        # concatenate concatenate
        ("A B C",),
        # concatenate conjunction
        ("A | B C",),
        # conjunction bracket
        ("(A | B)",),
        # conjunction concatenate
        ("A B | C",),
        # conjunction conjunction
        ("A | B | C",),
    ],
)
def test_token_compound_expression(code: str) -> None:
    parse_as(code, "TOKEN_COMPOUND_EXPRESSION")
