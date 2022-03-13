import re
from dataclasses import dataclass
from enum import IntEnum
from parser.exceptions import InternalParseError
from typing import List, Optional, Set, Tuple


@dataclass
class Token:
    type: IntEnum
    offset: int
    length: int

    def value(self, code: str) -> str:
        return code[self.offset : self.offset + self.length]


class RegexTokenizer:
    def __init__(self, regex: str):
        if regex.startswith("^"):
            raise ValueError("Regex should not start with a caret '^' character")

        self.regex = re.compile(f"^{regex}")

    def tokenize(self, code: str, offset: int) -> Optional[int]:
        match = self.regex.match(code[offset:])

        if not match:
            return None

        match_length = len(match.group(0))

        if match_length == 0:
            return None

        return match_length


def _check_terminal_rules(terminal_rules: List[Tuple[IntEnum, RegexTokenizer]]) -> None:
    enum_type = type(terminal_rules[0][0])

    found_enum_values = {item[0] for item in terminal_rules}

    if found_enum_values != set(enum_type) or len(terminal_rules) != len(enum_type):
        raise ValueError("Terminal rules has duplicates or missing items.")


def tokenize(
    code: str,
    terminal_rules: List[Tuple[IntEnum, RegexTokenizer]],
    pruned_terminals: Set[IntEnum],
) -> List[Token]:
    _check_terminal_rules(terminal_rules)

    tokens: List[Token] = []
    offset = 0

    while offset < len(code):
        token_match = False

        for token_type, tokenizer in terminal_rules:
            token_length = tokenizer.tokenize(code, offset)

            if token_length is not None:
                if token_type not in pruned_terminals:
                    tokens.append(Token(token_type, offset, token_length))

                offset += token_length
                token_match = True
                break

        if not token_match:
            # TODO use internal tokenize error
            raise InternalParseError(offset, None)

    return tokens
