from pathlib import Path

import pytest

from basil.models import Position, Token

POSITION = Position(Path("foo.txt"), 6, 9)
TOKEN = Token("some value", "some_type", POSITION)


def test_position_dunder_functions() -> None:
    assert str(POSITION) == "foo.txt:6:9"
    assert str(POSITION) == repr(POSITION)

    assert POSITION == POSITION
    hash(POSITION)
    POSITION < POSITION

    with pytest.raises(TypeError):
        POSITION == 3


def test_token_repr() -> None:
    assert repr(TOKEN) == "Token(type='some_type', value='some value')"
