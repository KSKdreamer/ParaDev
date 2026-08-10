"""Structured diagnostics for PDX parsing."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class PDXDiagnostic:
    """One parser diagnostic with a source span when available."""

    code: str
    message: str
    line: int
    column: int
    severity: str = "error"

    def to_dict(self) -> dict[str, object]:
        """Return a JSON-safe diagnostic view."""

        return {
            "code": self.code,
            "message": self.message,
            "line": self.line,
            "column": self.column,
            "severity": self.severity,
        }


class PDXParseError(ValueError):
    """Raised when PDX text cannot be parsed into a balanced AST.

    Args:
        diagnostics: Structured diagnostics explaining the parse failure.
    """

    def __init__(self, diagnostics: list[PDXDiagnostic]) -> None:
        self.diagnostics = diagnostics
        super().__init__("; ".join(diagnostic.message for diagnostic in diagnostics))
