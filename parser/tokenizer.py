import re
from dataclasses import dataclass
from enum import IntEnum
from parser.exceptions import InternalParseError
from typing import List, Optional, Set


@dataclass
class Token:
    type: IntEnum
    offset: int
    length: int

    def value(self, code: str) -> str:
        return code[self.offset : self.offset + self.length]


@dataclass
class TokenDescriptor:
    token_type: IntEnum


@dataclass
class Regex(TokenDescriptor):
    def __init__(self, token_type: IntEnum, regex: str) -> None:
        self.token_type = token_type
        self.value = re.compile(regex)

    value: re.Pattern[str]


@dataclass
class Literal(TokenDescriptor):
    value: str


class Tokenizer:
    def __init__(
        self,
        code: str,
        terminal_rules: List[TokenDescriptor],
        pruned_terminals: Set[IntEnum],
    ) -> None:
        self.code = code
        self.terminal_rules = terminal_rules
        self.pruned_terminals = pruned_terminals

    def _check_terminal_rules(self) -> None:
        enum_type = type(self.terminal_rules[0].token_type)

        found_enum_values = {item.token_type for item in self.terminal_rules}

        if found_enum_values != set(enum_type) or len(self.terminal_rules) != len(
            enum_type
        ):
            raise ValueError("Terminal rules has duplicates or missing items.")

    def tokenize(self) -> List[Token]:
        self._check_terminal_rules()

        tokenizables = {
            Literal: self._tokenize_literal,
            Regex: self._tokenize_regex,
        }

        tokens: List[Token] = []
        offset = 0

        while offset < len(self.code):
            token_match = False

            for token_descriptor in self.terminal_rules:

                # tokenize as literal or regex
                token_length = tokenizables[type(token_descriptor)](
                    token_descriptor, offset
                )

                if token_length is not None:
                    if token_descriptor.token_type not in self.pruned_terminals:
                        tokens.append(
                            Token(token_descriptor.token_type, offset, token_length)
                        )

                    offset += token_length
                    token_match = True
                    break

            if not token_match:
                # TODO use internal tokenize error
                raise InternalParseError(offset, None)

        return tokens

    def _tokenize_regex(
        self, tokenizable: TokenDescriptor, offset: int
    ) -> Optional[int]:
        assert isinstance(tokenizable, Regex)
        regex = tokenizable.value

        match = regex.match(self.code[offset:])

        if not match:
            return None

        match_length = len(match.group(0))

        if match_length == 0:
            return None

        return match_length

    def _tokenize_literal(
        self, tokenizable: TokenDescriptor, offset: int
    ) -> Optional[int]:
        assert isinstance(tokenizable, Literal)
        literal = tokenizable.value

        if not self.code[offset:].startswith(literal):
            return None

        return len(literal)
