"""Tokenizer for Paradox PDX script files."""

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass
from enum import Enum, auto
from typing import Any

from .diagnostics import PDXDiagnostic, PDXParseError


class TokenType(Enum):
    """PDX lexical token categories."""

    IDENTIFIER = auto()
    NUMBER = auto()
    STRING = auto()
    BOOLEAN = auto()
    EQUALS = auto()
    NOT_EQUALS = auto()
    LT = auto()
    GT = auto()
    LE = auto()
    GE = auto()
    LBRACE = auto()
    RBRACE = auto()
    VARIABLE = auto()
    COMMENT = auto()
    EOF = auto()


@dataclass(frozen=True, slots=True)
class Token:
    """A PDX token with one-based source position."""

    type: TokenType
    value: Any = None
    line: int = 0
    column: int = 0

    @property
    def val(self) -> Any:
        """Legacy-compatible alias for ``value``."""

        return self.value

    @property
    def col(self) -> int:
        """Legacy-compatible alias for ``column``."""

        return self.column

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-safe token row."""

        return {
            "type": self.type.name.lower(),
            "value": self.value,
            "line": self.line,
            "column": self.column,
        }


def reconstruct(tokens: list[Token]) -> str:
    """Reconstruct canonical PDX text from tokens."""

    parts: list[str] = []
    for token in tokens:
        if token.type is TokenType.EOF:
            break
        if token.type is TokenType.STRING:
            parts.append('"' + str(token.value) + '"')
        elif token.type is TokenType.COMMENT:
            parts.append(str(token.value) + "\n")
        else:
            parts.append(str(token.value))
    return " ".join(parts).strip()


class PDXTokenizer:
    """Tokenize PDX text while preserving comments and source spans.

    Args:
        source: Raw PDX script text. A leading UTF-8 BOM is ignored.
    """

    __slots__ = ("_column", "_length", "_line", "_pos", "_source")

    def __init__(self, source: str) -> None:
        self._source = source[1:] if source.startswith("\ufeff") else source
        self._pos = 0
        self._length = len(self._source)
        self._line = 1
        self._column = 1

    def tokenize(self) -> list[Token]:
        """Return all tokens, including the final EOF token."""

        return list(self)

    def __iter__(self) -> Iterator[Token]:
        """Yield tokens until EOF."""

        while True:
            token = self._next_token()
            yield token
            if token.type is TokenType.EOF:
                return

    def _peek(self, offset: int = 0) -> str:
        index = self._pos + offset
        if index >= self._length:
            return ""
        return self._source[index]

    def _advance(self) -> str:
        char = self._source[self._pos]
        self._pos += 1
        if char == "\n":
            self._line += 1
            self._column = 1
        else:
            self._column += 1
        return char

    def _skip_whitespace(self) -> None:
        while self._pos < self._length and self._source[self._pos] in " \t\r\n":
            self._advance()

    def _next_token(self) -> Token:
        self._skip_whitespace()
        if self._pos >= self._length:
            return Token(TokenType.EOF, None, self._line, self._column)

        line = self._line
        column = self._column
        char = self._peek()

        if char == "#":
            return self._read_comment(line, column)
        if char == '"':
            return self._read_string(line, column)
        if char == "[":
            return self._read_bracketed_identifier(line, column)
        if char == "{":
            self._advance()
            return Token(TokenType.LBRACE, "{", line, column)
        if char == "}":
            self._advance()
            return Token(TokenType.RBRACE, "}", line, column)
        if char == "!" and self._peek(1) == "=":
            self._advance()
            self._advance()
            return Token(TokenType.NOT_EQUALS, "!=", line, column)
        if char == "<":
            self._advance()
            if self._peek() == "=":
                self._advance()
                return Token(TokenType.LE, "<=", line, column)
            return Token(TokenType.LT, "<", line, column)
        if char == ">":
            self._advance()
            if self._peek() == "=":
                self._advance()
                return Token(TokenType.GE, ">=", line, column)
            return Token(TokenType.GT, ">", line, column)
        if char == "=":
            self._advance()
            return Token(TokenType.EQUALS, "=", line, column)
        if char == "@":
            return self._read_variable(line, column)
        if char.isdigit() or (char == "-" and self._peek(1).isdigit()):
            return self._read_number(line, column)
        if self._is_identifier_start(char) or char == "-":
            return self._read_word(line, column)

        self._advance()
        return Token(TokenType.IDENTIFIER, char, line, column)

    def _read_comment(self, line: int, column: int) -> Token:
        start = self._pos
        while self._pos < self._length and self._source[self._pos] != "\n":
            self._pos += 1
            self._column += 1
        return Token(TokenType.COMMENT, self._source[start : self._pos], line, column)

    def _read_string(self, line: int, column: int) -> Token:
        self._advance()
        parts: list[str] = []
        while self._pos < self._length:
            char = self._peek()
            if char == "\\":
                self._advance()
                next_char = self._peek()
                if next_char:
                    self._advance()
                    parts.append("\\" + next_char)
                else:
                    parts.append("\\")
                continue
            if char == '"':
                self._advance()
                return Token(TokenType.STRING, "".join(parts), line, column)
            parts.append(self._advance())
        raise PDXParseError([PDXDiagnostic(code="pdx.unterminated_string", message="Unterminated PDX string.", line=line, column=column)])

    def _read_bracketed_identifier(self, line: int, column: int) -> Token:
        start = self._pos
        self._advance()
        while self._pos < self._length:
            char = self._advance()
            if char == "]":
                return Token(TokenType.IDENTIFIER, self._source[start : self._pos], line, column)
        raise PDXParseError([PDXDiagnostic(code="pdx.unterminated_bracket_value", message="Unterminated PDX bracketed value.", line=line, column=column)])

    def _read_variable(self, line: int, column: int) -> Token:
        self._advance()
        start = self._pos
        while self._pos < self._length and self._is_identifier_char(self._source[self._pos]):
            self._advance()
        if self._pos == start:
            raise PDXParseError([PDXDiagnostic(code="pdx.empty_variable", message="PDX variable '@' requires a name.", line=line, column=column)])
        self._consume_symbol_tail()
        return Token(TokenType.VARIABLE, "@" + self._source[start : self._pos], line, column)

    def _read_number(self, line: int, column: int) -> Token:
        start = self._pos
        if self._peek() == "-":
            self._advance()

        if self._peek() == "0" and self._peek(1) in {"x", "X"}:
            self._advance()
            self._advance()
            hex_start = self._pos
            while self._pos < self._length and self._source[self._pos] in "0123456789abcdefABCDEF":
                self._advance()
            if self._pos == hex_start:
                raise PDXParseError(
                    [
                        PDXDiagnostic(
                            code="pdx.invalid_hex_number",
                            message="PDX hexadecimal number requires at least one digit.",
                            line=line,
                            column=column,
                        )
                    ]
                )
            return Token(TokenType.NUMBER, self._source[start : self._pos], line, column)

        while self._pos < self._length and self._source[self._pos].isdigit():
            self._advance()
        while self._peek() == "." and self._peek(1).isdigit():
            self._advance()
            while self._pos < self._length and self._source[self._pos].isdigit():
                self._advance()

        if self._pos < self._length and self._is_identifier_char(self._source[self._pos]):
            while self._pos < self._length and (self._is_identifier_char(self._source[self._pos]) or self._source[self._pos] == "."):
                self._advance()
            return Token(TokenType.IDENTIFIER, self._consume_percent_suffix(start), line, column)

        raw = self._consume_percent_suffix(start)
        if raw.endswith("%"):
            return Token(TokenType.IDENTIFIER, raw, line, column)
        return Token(TokenType.NUMBER, raw, line, column)

    def _read_word(self, line: int, column: int) -> Token:
        start = self._pos
        self._advance()
        self._consume_symbol_tail()

        word = self._consume_percent_suffix(start)
        if word in {"yes", "no"}:
            return Token(TokenType.BOOLEAN, word, line, column)
        return Token(TokenType.IDENTIFIER, word, line, column)

    def _consume_symbol_tail(self) -> None:
        while self._pos < self._length:
            char = self._source[self._pos]
            if self._is_identifier_char(char):
                self._advance()
            elif char in {":", "@"} and self._pos + 1 < self._length and self._is_identifier_char(self._source[self._pos + 1]):
                self._advance()
            elif (
                char == "?"
                and self._pos + 1 < self._length
                and (self._is_identifier_char(self._source[self._pos + 1]) or self._source[self._pos + 1].isdigit())
            ):
                self._advance()
            elif char == "/" and self._pos + 1 < self._length and (self._is_identifier_char(self._source[self._pos + 1]) or self._source[self._pos + 1] == "/"):
                self._advance()
            elif (
                char == "^"
                and self._pos + 1 < self._length
                and (self._is_identifier_char(self._source[self._pos + 1]) or self._source[self._pos + 1].isdigit())
            ):
                self._advance()
            elif (
                char == "."
                and self._pos + 1 < self._length
                and (self._is_identifier_char(self._source[self._pos + 1]) or self._source[self._pos + 1].isdigit())
            ):
                self._advance()
            else:
                break

    def _consume_percent_suffix(self, start: int) -> str:
        if self._pos < self._length and self._source[self._pos] == "%":
            self._advance()
            if self._pos < self._length and self._source[self._pos] == "%":
                self._advance()
        return self._source[start : self._pos]

    @staticmethod
    def _is_identifier_start(char: str) -> bool:
        return char.isalpha() or char == "_"

    @staticmethod
    def _is_identifier_char(char: str) -> bool:
        return char.isalnum() or char in {"_", "-"}
