import re
from enum import IntEnum
from parser.tree import Token
from typing import List, Optional, Set, Tuple


class RegexTokenizer:
    def __init__(self, regex: str):
        if regex.startswith("^"):
            raise ValueError(
                "Regex should not start with a caret '^' character"
                + "it's added in __init__() now."
            )

        self.regex = re.compile(f"^{regex}")

    def tokenize(self, code: str, offset: int) -> Optional[int]:
        match = self.regex.match(code[offset:])

        if not match:
            return None

        match_length = len(match.group(0))

        if match_length == 0:
            return None

        return match_length


def tokenize(
    code: str,
    terminal_rules: List[Tuple[IntEnum, RegexTokenizer]],
    pruned_terminals: Set[IntEnum],
) -> List[Token]:
    # TODO check terminal_rules

    tokens: List[Token] = []
    offset = 0

    while offset < len(code):
        for token_type, tokenizer in terminal_rules:
            token_length = tokenizer.tokenize(code, offset)

            if token_length is not None:
                if token_type not in pruned_terminals:
                    tokens.append(Token(token_type, offset, token_length))

                offset += token_length
                break

    return tokens
