from parser.grammar.parser import REWRITE_RULES
from parser.parser import new_parse_generic
from parser.parser_generator import check_parser_staleness, generate_parser
from pathlib import Path

import pytest


@pytest.mark.parametrize(
    ["code"],
    [
        ("// some comment\n",),
        ("//\n",),
        ("\n",),
        ("    \n",),
        ("A = B\n",),
        ("A = (B)\n",),
        ("A = ( B )\n",),
        ('A = "B"\n',),
        ('A = ("B")\n',),
        ('A = ( "B" )\n',),
        ('A = "B" "C"\n',),
        ('A = ("B" "C")\n',),
        ('A = ( "B" "C" )\n',),
        ("A = (B C)\n",),
        ("A = ( B C )\n",),
        ("A = B | C\n",),
        ("A = B | C | D\n",),
        ("A = (B | C)\n",),
        ("A = (B | C | D)\n",),
        ('A = ("B" | "C")\n',),
        ('A = ("B" | "C" | "D")\n',),
        ("A = B C\n",),
        ("A = (B C)?\n",),
        ("A = (B C)+\n",),
        ("A = (B C)*\n",),
        ("A = (B C){3,...}\n",),
        ("A = (B C)? D\n",),
        ("A = B (C D)? E (F (G H)? I)? J\n",),
        ("A = (B)? (C D)+ (E)+\n",),
        ('A = regex("[a-z_]+")\n',),
        ('A = regex("\\"")\n',),
        ('A = regex("\\n")\n',),
        ('A = regex("\\\\")\n',),
    ],
)
def test_grammar_parser_accepts(code: str) -> None:
    new_parse_generic(REWRITE_RULES, code)


def test_parser_not_stale() -> None:
    grammar_path = Path("parser/grammar/grammar.txt")
    parser_path = Path("parser/grammar/parser.py")

    parser_code = generate_parser(grammar_path)
    assert not check_parser_staleness(parser_code, parser_path)
