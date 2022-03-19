from enum import IntEnum
from parser.tokenizer.exceptions import (
    MissingTerminalTypes,
    TokenizerError,
    UnexpectedTerminalTypes,
)
from parser.tokenizer.models import Literal, Regex, Token, TokenDescriptor
from typing import List, Optional, Set


class Tokenizer:
    def __init__(
        self,
        *,
        filename: str,
        code: str,
        terminal_rules: List[TokenDescriptor],
        pruned_terminals: Set[IntEnum],
    ) -> None:
        self.code = code
        self.filename = filename
        self.terminal_rules = terminal_rules
        self.pruned_terminals = pruned_terminals

    def _check_terminal_rules(self) -> None:
        enum_type = type(self.terminal_rules[0].token_type)

        found_enum_values = {item.token_type for item in self.terminal_rules}
        expected_enum_values: Set[IntEnum] = set(enum_type)

        unexpected_enum_values = found_enum_values - expected_enum_values
        missing_enum_values = expected_enum_values - found_enum_values

        if unexpected_enum_values:
            raise UnexpectedTerminalTypes(unexpected_enum_values)

        if missing_enum_values:
            raise MissingTerminalTypes(missing_enum_values)

    def tokenize(self) -> List[Token]:
        self._check_terminal_rules()
        tokens: List[Token] = []
        offset = 0

        while offset < len(self.code):
            token_match = False

            for token_descriptor in self.terminal_rules:

                if isinstance(token_descriptor, Literal):
                    token_length = self._tokenize_literal(token_descriptor, offset)
                elif isinstance(token_descriptor, Regex):
                    token_length = self._tokenize_regex(token_descriptor, offset)

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
                raise TokenizerError(self.filename, self.code, offset)

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
