from parser.grammar_parser import REWRITE_RULES, ROOT_SYMBOL, GrammarSymbolType
from parser.parser import new_parse_generic

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
        ("A = B C\n",),
    ],
)
def test_grammar_parser_accepts(code: str) -> None:
    new_parse_generic(REWRITE_RULES, ROOT_SYMBOL, code, GrammarSymbolType)
