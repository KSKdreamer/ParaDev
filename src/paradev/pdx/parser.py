"""Recursive-descent parser for PDX token streams."""

from __future__ import annotations

from .ast import PDXBlock, PDXEntry, PDXScalar, SCALAR_BOOL, SCALAR_COLOR, SCALAR_ID, SCALAR_NUM, SCALAR_STR, SCALAR_VAR
from .diagnostics import PDXDiagnostic, PDXParseError
from .token import PDXTokenizer, Token, TokenType

_OPS = frozenset({TokenType.EQUALS, TokenType.NOT_EQUALS, TokenType.LT, TokenType.GT, TokenType.LE, TokenType.GE})
_VALS = frozenset({TokenType.IDENTIFIER, TokenType.NUMBER, TokenType.STRING, TokenType.BOOLEAN, TokenType.VARIABLE})
_VALUE_STARTS = frozenset({*_VALS, TokenType.LBRACE})
_TYPE_MAP = {
    TokenType.IDENTIFIER: SCALAR_ID,
    TokenType.NUMBER: SCALAR_NUM,
    TokenType.STRING: SCALAR_STR,
    TokenType.BOOLEAN: SCALAR_BOOL,
    TokenType.VARIABLE: SCALAR_VAR,
}


def parse_pdx(text: str) -> PDXBlock:
    """Parse PDX source text.

    Args:
        text: PDX source text.

    Returns:
        Parsed PDX block.

    Raises:
        PDXParseError: If the token stream contains unbalanced braces.
    """

    return PDXParser(PDXTokenizer(text).tokenize()).run()


class PDXParser:
    """Parse PDX tokens into :class:`PDXBlock` records."""

    __slots__ = ("_last_line", "_length", "_pos", "_tokens")

    def __init__(self, tokens: list[Token]) -> None:
        self._tokens = tokens
        self._pos = 0
        self._length = len(tokens)
        self._last_line = 0

    def run(self) -> PDXBlock:
        """Parse all tokens into a top-level block."""

        return self._block(open_token=None)

    def _peek(self) -> Token:
        if self._pos < self._length:
            return self._tokens[self._pos]
        return Token(TokenType.EOF, None, 0, 0)

    def _advance(self) -> Token:
        token = self._peek()
        self._pos += 1
        self._last_line = token.line
        return token

    def _block(self, open_token: Token | None) -> PDXBlock:
        block = PDXBlock()
        pending_comments: list[str] = []

        while True:
            token = self._peek()
            if token.type is TokenType.EOF:
                if open_token is not None:
                    self._raise("pdx.unclosed_block", "Unclosed PDX block.", open_token)
                block.trailing_comments = pending_comments
                return block
            if token.type is TokenType.RBRACE:
                if open_token is None:
                    self._raise("pdx.unexpected_rbrace", "Unexpected closing brace.", token)
                block.trailing_comments = pending_comments
                return block
            if token.type is TokenType.COMMENT:
                pending_comments.append(self._advance().value)
                continue

            entry = self._entry()
            if entry is None:
                continue
            entry.comments = pending_comments
            pending_comments = []

            next_token = self._peek()
            if next_token.type is TokenType.COMMENT and next_token.line == self._last_line:
                entry.inline_comment = self._advance().value
            block.entries.append(entry)

    def _entry(self) -> PDXEntry | None:
        token = self._peek()
        if token.type is TokenType.LBRACE:
            open_token = self._advance()
            block = self._block(open_token=open_token)
            self._consume_rbrace(open_token)
            return PDXEntry(val=block)

        if token.type not in _VALS:
            self._advance()
            return None

        key = _scalar(self._advance())
        next_token = self._peek()
        if next_token.type not in _OPS:
            return PDXEntry(key=key)

        op_token = self._advance()
        op = op_token.value
        value_token = self._peek()
        if value_token.type not in _VALUE_STARTS:
            self._raise("pdx.missing_value", f"PDX operator {op!r} requires a value.", op_token)
        if value_token.type is TokenType.LBRACE:
            open_token = self._advance()
            value: PDXScalar | PDXBlock = self._block(open_token=open_token)
            self._consume_rbrace(open_token)
        else:
            value = self._value_scalar()
        return PDXEntry(key=key, op=op, val=value)

    def _value_scalar(self) -> PDXScalar:
        token = self._advance()
        if token.type is TokenType.IDENTIFIER and str(token.value).lower() in {"rgb", "hsv"} and self._peek().type is TokenType.LBRACE:
            return self._color(token)
        return _scalar(token)

    def _color(self, name_token: Token) -> PDXScalar:
        open_token = self._advance()
        parts = [str(name_token.value).lower(), "{"]
        while self._peek().type not in {TokenType.RBRACE, TokenType.EOF}:
            parts.append(str(self._advance().value))
        if self._peek().type is TokenType.EOF:
            self._raise("pdx.unclosed_block", "Unclosed PDX color block.", open_token)
        self._advance()
        parts.append("}")
        raw = " ".join(parts)
        return PDXScalar(val=raw, raw=raw, type=SCALAR_COLOR)

    def _consume_rbrace(self, open_token: Token) -> None:
        if self._peek().type is not TokenType.RBRACE:
            self._raise("pdx.unclosed_block", "Unclosed PDX block.", open_token)
        self._advance()

    @staticmethod
    def _raise(code: str, message: str, token: Token) -> None:
        raise PDXParseError([PDXDiagnostic(code=code, message=message, line=token.line, column=token.column)])


def _scalar(token: Token) -> PDXScalar:
    scalar_type = _TYPE_MAP.get(token.type, SCALAR_ID)
    raw = f'"{token.value}"' if token.type is TokenType.STRING else str(token.value)
    return PDXScalar(val=token.value, raw=raw, type=scalar_type, anno={"span": {"line": token.line, "column": token.column}})
