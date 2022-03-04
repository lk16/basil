from parser.grammar_parser import REWRITE_RULES, ROOT_SYMBOL, GrammarSymbolType
from parser.parser import new_parse_generic
from parser.tree import Tree, prune_by_symbol_types, prune_no_symbol, prune_zero_length
from pathlib import Path
from typing import List, Optional, Tuple

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


def tree_to_python_parser_expression(tree: Tree, code: str) -> str:

    if tree.symbol_type == GrammarSymbolType.LITERAL_EXPRESSION:
        value = tree.value(code)
        return f"LiteralParser({value})"

    elif tree.symbol_type == GrammarSymbolType.REGEX_EXPRESSION:
        regex_value = tree[0].value(code)
        return f"RegexBasedParser({regex_value})"

    elif tree.symbol_type == GrammarSymbolType.BRACKETED_EXPRESSION:
        return tree_to_python_parser_expression(tree[0], code)

    elif tree.symbol_type == GrammarSymbolType.TOKEN_COMPOUND_EXPRESSION:
        # TODO This was filtered out earlier, check why that failed
        return tree_to_python_parser_expression(tree[0], code)

    elif tree.symbol_type == GrammarSymbolType.TOKEN_EXPRESSION:
        # TODO This was filtered out earlier, check why that failed
        return tree_to_python_parser_expression(tree[0], code)

    elif tree.symbol_type == GrammarSymbolType.CONCATENATION_EXPRESSION:
        # TODO flatten long tails

        return (
            "ConcatenationParser("
            + tree_to_python_parser_expression(tree[0], code)
            + ", "
            + tree_to_python_parser_expression(tree[1], code)
            + ")"
        )

    elif tree.symbol_type == GrammarSymbolType.CONJUNCTION_EXPRESSION:
        # TODO flatten long tails

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

    parser_script += ")\n"
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
