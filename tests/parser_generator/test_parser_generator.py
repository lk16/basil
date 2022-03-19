from parser.grammar.parser import NonTerminal, Terminal
from parser.parser_generator.exceptions import UnknownTokenException
from parser.parser_generator.parser_generator import ParserGenerator
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Generator

import pytest

DUMMY_GRAMMAR = """
@ token
A = regex("a*") .

@ token
B = "b" .

@ token
@ prune
WHITESPACE = regex("[ \\n]*") .

// ---

FOO = A | B .

@ prune
BAR = B | (A B A) .

ROOT = (FOO)+ .


"""

GRAMMAR_WITH_UNKNOWN_TOKEN = """
ROOT = (FOO)+ .
"""


@pytest.fixture()
def grammar_path() -> Generator[Path, None, None]:
    with NamedTemporaryFile() as grammar_file:
        grammar_file.write(DUMMY_GRAMMAR.encode())
        grammar_file.seek(0)
        yield Path(grammar_file.name)


@pytest.fixture()
def grammar_with_unknown_token() -> Generator[Path, None, None]:
    with NamedTemporaryFile() as grammar_file:
        grammar_file.write(GRAMMAR_WITH_UNKNOWN_TOKEN.encode())
        grammar_file.seek(0)
        yield Path(grammar_file.name)


@pytest.fixture()
def parser_path(grammar_path: Path) -> Generator[Path, None, None]:
    with NamedTemporaryFile() as parser_file:
        parser_file.write(DUMMY_GRAMMAR.encode())
        parser_file.seek(0)
        parser_path_ = Path(parser_file.name)
        ParserGenerator(grammar_path).write_if_stale(parser_path_)
        yield parser_path_


def test_parser_generator_init(grammar_path: Path) -> None:
    parser_gen = ParserGenerator(grammar_path)
    tokens = parser_gen.tokens
    code = parser_gen.code

    assert parser_gen.grammar_path == grammar_path
    assert parser_gen.code == DUMMY_GRAMMAR
    assert parser_gen._generated_parser_code is None

    parsed_grammar = parser_gen._parsed_grammar

    assert len(parsed_grammar.terminals) == 3
    a, b, whitespace = parsed_grammar.terminals

    assert a[0] == "A"
    assert a[1].token_type == NonTerminal.REGEX_EXPRESSION
    assert a[1].children[1].token_type == Terminal.LITERAL_EXPRESSION
    assert a[1].children[1].value(tokens, code) == '"a*"'

    assert b[0] == "B"
    assert b[1].token_type == Terminal.LITERAL_EXPRESSION
    assert b[1].value(tokens, code) == '"b"'

    assert whitespace[0] == "WHITESPACE"
    assert whitespace[1].token_type == NonTerminal.REGEX_EXPRESSION
    assert whitespace[1].children[1].token_type == Terminal.LITERAL_EXPRESSION
    assert whitespace[1].children[1].value(tokens, code) == '"[ \\n]*"'


def test_parser_generator_up_to_date(grammar_path: Path, parser_path: Path) -> None:
    parser_gen = ParserGenerator(grammar_path)
    assert parser_gen.is_up_to_date(parser_path)


def test_parser_generator_not_up_to_date(grammar_path: Path) -> None:
    with NamedTemporaryFile() as empty_file:
        parser_gen = ParserGenerator(grammar_path)
        assert not parser_gen.is_up_to_date(Path(empty_file.name))


def test_parser_generator_is_up_to_date_non_existent(grammar_path: Path) -> None:
    non_existent = Path("/tmp/does-not-exist")
    assert not non_existent.exists()

    parser_gen = ParserGenerator(grammar_path)
    assert not parser_gen.is_up_to_date(non_existent)


def test_parser_generator_write_if_stale(grammar_path: Path, parser_path: Path) -> None:
    parser_gen = ParserGenerator(grammar_path)

    with NamedTemporaryFile() as new_file:
        new_file_path = Path(new_file.name)
        parser_gen.write_if_stale(new_file_path)

        assert parser_path.read_text() == new_file_path.read_text()


def test_parser_generator_write_if_not_stale(
    grammar_path: Path, parser_path: Path
) -> None:
    parser_code = parser_path.read_text()

    parser_gen = ParserGenerator(grammar_path)
    parser_gen.write_if_stale(parser_path)

    assert parser_path.read_text() == parser_code


def test_parser_generator_write_if_stale_crash(
    grammar_with_unknown_token: Path,
) -> None:
    parser_gen = ParserGenerator(grammar_with_unknown_token)

    with NamedTemporaryFile() as new_file:
        new_file_path = Path(new_file.name)
        with pytest.raises(SystemExit):
            parser_gen.write_if_stale(new_file_path)


def test_parser_generator_unknown_token(grammar_with_unknown_token: Path) -> None:
    parser_gen = ParserGenerator(grammar_with_unknown_token)

    with pytest.raises(UnknownTokenException) as e:
        parser_gen._generate_parser_code()

    assert e.value == UnknownTokenException(
        str(grammar_with_unknown_token.absolute()), parser_gen.code, 9, "FOO"
    )
