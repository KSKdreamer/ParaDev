"""Project-level copy roots for compatibility overlays."""

from __future__ import annotations

import inspect
from dataclasses import dataclass, is_dataclass
from fnmatch import fnmatchcase
from pathlib import Path, PurePosixPath
from typing import cast

from typing_extensions import TypedDict, is_typeddict

from paradev._api_table import api_annotation_text, api_standard_table, api_table_selection
from paradev._api_table_markdown import (
    api_standard_reference_markdown,
)
from paradev.build import Artifact, Diagnostic

ARTIFACT_TARGET_ROOTS = {"output", "build"}
COPY_ROOTS_API_TABLE_SCHEMA = "paradev.sdk.copy_roots.api-table.v1"
_COPY_ROOTS_API_REFERENCE_PAGE = "docs/user-manual/copy-roots-api-reference.md"
_COPY_ROOTS_API_TEST_ANCHOR = "tests/test_architecture.py::test_copy_roots_api_table_lists_copy_root_contract"
_COPY_ROOTS_API_INDEX_NAMES = ("module_index", "feature_index", "kind_index")

__all__ = [
    "ARTIFACT_TARGET_ROOTS",
    "ProjectCopyRootSpecError",
    "CopyRootSpec",
    "project_copy_roots",
    "copy_root_artifacts",
    "merge_copy_root_artifacts",
    "COPY_ROOTS_API_TABLE_SCHEMA",
    "CopyRootsApiRow",
    "CopyRootsApiTable",
    "get_copy_roots_api_selection",
    "get_copy_roots_api_table",
    "render_copy_roots_api_reference_markdown",
]


class ProjectCopyRootSpecError(ValueError):
    """Raised when project copy-root declarations are invalid."""


@dataclass(frozen=True, slots=True)
class CopyRootSpec:
    """One external or project-local file tree copied into build output."""

    copy_id: str
    source: Path
    target: str = "."
    target_root: str = "output"
    include: tuple[str, ...] = ("**/*",)
    exclude: tuple[str, ...] = ()

    def to_view(self) -> dict[str, object]:
        """Return a JSON-safe copy-root view."""

        return {
            "id": self.copy_id,
            "source": str(self.source),
            "target": self.target,
            "target_root": self.target_root,
            "include": list(self.include),
            "exclude": list(self.exclude),
        }


class CopyRootsApiRow(TypedDict):
    """One public `paradev.sdk.copy_roots` API row."""

    symbol: str
    kind: str
    layer: str
    module: str
    feature: str
    import_path: str
    returns: str
    value: str
    registry_seam: str
    surface: str
    doc_page: str
    test_anchor: str


class CopyRootsApiTable(TypedDict):
    """Generated API-standard table for SDK copy-root helpers."""

    schema: str
    row_count: int
    module_index: dict[str, list[str]]
    feature_index: dict[str, list[str]]
    kind_index: dict[str, list[str]]
    rows: list[CopyRootsApiRow]


def project_copy_roots(value: object, root: Path, path: Path) -> tuple[CopyRootSpec, ...]:
    """Parse top-level `copy_roots` manifest declarations.

    Args:
        value: Raw manifest value.
        root: Project root path.
        path: Manifest path for diagnostics.

    Returns:
        Parsed copy-root specs.

    Raises:
        ProjectCopyRootSpecError: If a declaration is invalid.
    """

    if value is None:
        return ()
    if not isinstance(value, list):
        raise ProjectCopyRootSpecError(f"{path} key 'copy_roots' must be a list of copy-root mappings.")
    specs: list[CopyRootSpec] = []
    seen: set[str] = set()
    for index, item in enumerate(value):
        key = f"copy_roots[{index}]"
        if not isinstance(item, dict):
            raise ProjectCopyRootSpecError(f"{path} key {key!r} must be a mapping.")
        copy_id = _required_token(item.get("id"), f"{key}.id", path)
        if copy_id in seen:
            raise ProjectCopyRootSpecError(f"{path} key {key}.id {copy_id!r} is declared more than once.")
        seen.add(copy_id)
        source = _resolve_source(root, item.get("source"), f"{key}.source", path)
        target = _safe_target(item.get("target", "."), f"{key}.target", path)
        target_root = _target_root(item.get("target_root", "output"), f"{key}.target_root", path)
        include = _patterns(item.get("include", ["**/*"]), f"{key}.include", path)
        exclude = _patterns(item.get("exclude", []), f"{key}.exclude", path, allow_empty=True)
        specs.append(CopyRootSpec(copy_id=copy_id, source=source, target=target, target_root=target_root, include=include, exclude=exclude))
    return tuple(specs)


def copy_root_artifacts(specs: tuple[CopyRootSpec, ...]) -> tuple[tuple[Artifact, ...], tuple[Diagnostic, ...]]:
    """Return copy artifacts and diagnostics for project-level copy roots."""

    artifacts: list[Artifact] = []
    diagnostics: list[Diagnostic] = []
    for spec in specs:
        if not spec.source.is_dir():
            diagnostics.append(
                Diagnostic(
                    code="copy_root.missing_source",
                    message=f"Copy root {spec.copy_id} source directory does not exist: {spec.source}.",
                    severity="error",
                    source_path=spec.source,
                    target_root=spec.target_root,
                )
            )
            continue
        for source in sorted(path for path in spec.source.rglob("*") if path.is_file()):
            rel_path = source.relative_to(spec.source).as_posix()
            if not _included(rel_path, spec.include, spec.exclude):
                continue
            artifact_path = _target_path(spec.target, rel_path)
            try:
                stat = source.stat()
            except OSError as error:
                diagnostics.append(
                    Diagnostic(
                        code="copy_root.unreadable_source",
                        message=f"Copy root {spec.copy_id} source {source} cannot be read. {type(error).__name__}: {error}.",
                        severity="error",
                        source_path=source,
                        artifact_path=artifact_path,
                        target_root=spec.target_root,
                    )
                )
                continue
            artifacts.append(
                Artifact(
                    path=artifact_path,
                    artifact_type="copy",
                    owner=f"copy_root:{spec.copy_id}",
                    inputs=(source,),
                    target_root=spec.target_root,
                    metadata={
                        "copy_root": spec.copy_id,
                        "source_root": str(spec.source),
                        "source_path": rel_path,
                        "byte_size": stat.st_size,
                    },
                )
            )
    return tuple(artifacts), tuple(diagnostics)


def merge_copy_root_artifacts(
    copy_artifacts: tuple[Artifact, ...],
    generated_artifacts: tuple[Artifact, ...],
) -> tuple[tuple[Artifact, ...], tuple[Diagnostic, ...]]:
    """Return copy artifacts not shadowed by generated artifacts plus warnings."""

    generated = {(_artifact_target_root(artifact), _artifact_path(artifact)): artifact for artifact in generated_artifacts}
    kept: list[Artifact] = []
    diagnostics: list[Diagnostic] = []
    for artifact in copy_artifacts:
        key = (_artifact_target_root(artifact), _artifact_path(artifact))
        shadow = generated.get(key)
        if shadow is None:
            kept.append(artifact)
            continue
        diagnostics.append(
            Diagnostic(
                code="copy_root.shadowed_artifact",
                message=f"Copy root {_copy_root_id(artifact)} file {artifact.path} is shadowed by generated artifact {shadow.owner}.",
                severity="warning",
                source_path=artifact.inputs[0] if artifact.inputs else None,
                artifact_path=artifact.path,
                target_root=artifact.target_root,
                owners=(artifact.owner, shadow.owner),
            )
        )
    return tuple(kept), tuple(diagnostics)


def get_copy_roots_api_table() -> CopyRootsApiTable:
    """Return the API-standard table for SDK copy-root helpers.

    Returns:
        JSON-safe table derived from `paradev.sdk.copy_roots.__all__`, with
        copied rows and indexes for target roots, validation, manifest parsing,
        copy-root artifacts, artifact merging, and this reference-table helper.
    """

    return cast(CopyRootsApiTable, api_standard_table(COPY_ROOTS_API_TABLE_SCHEMA, _copy_roots_api_rows()))


def get_copy_roots_api_selection(
    symbol: str | None = None,
    index_name: str | None = None,
    key: str | None = None,
) -> CopyRootsApiTable | CopyRootsApiRow | list[str]:
    """Return the full copy-roots API table, one row, or one index bucket.

    Args:
        symbol: Optional public symbol to select from the table rows.
        index_name: Optional index name, such as `module_index`,
            `feature_index`, or `kind_index`.
        key: Optional key inside the selected index.

    Returns:
        A detached table copy when no selector is passed, a detached row copy
        when `symbol` is passed, or a copied list of symbols for an index
        bucket when `index_name` and `key` are passed.

    Raises:
        ValueError: If selectors are ambiguous, incomplete, or name an
            unsupported index.
        KeyError: If the requested symbol or index key is not present.
    """

    return cast(
        CopyRootsApiTable | CopyRootsApiRow | list[str],
        api_table_selection(
            get_copy_roots_api_table(),
            row_key_field="symbol",
            row_key=symbol,
            index_name=index_name,
            key=key,
            index_names=_COPY_ROOTS_API_INDEX_NAMES,
        ),
    )


def render_copy_roots_api_reference_markdown() -> str:
    """Render the SDK copy-root helper table as Markdown.

    Returns:
        Deterministic Markdown suitable for
        `docs/user-manual/copy-roots-api-reference.md`. The content is
        generated from `get_copy_roots_api_table()` so copy-root target roots,
        parser, artifact generation, artifact merge diagnostics, CLI command,
        and manual-page audits stay aligned.
    """

    table = get_copy_roots_api_table()
    return api_standard_reference_markdown(
        title="Copy Roots API Reference",
        source="paradev.sdk.copy_roots.get_copy_roots_api_table()",
        regenerate_when="Regenerate this file whenever SDK copy-root helpers change:",
        command="rtk uv run paradev copy-roots-api --markdown > docs/user-manual/copy-roots-api-reference.md",
        table=table,
        module_label="Copy-root",
        markdown_value=True,
    )


def _copy_roots_api_rows() -> list[CopyRootsApiRow]:
    rows: list[CopyRootsApiRow] = []
    for symbol in __all__:
        value = globals()[symbol]
        feature = _copy_roots_api_feature(symbol)
        rows.append(
            {
                "symbol": symbol,
                "kind": _copy_roots_api_kind(symbol, value),
                "layer": "sdk",
                "module": "sdk.copy_roots",
                "feature": feature,
                "import_path": f"paradev.sdk.copy_roots.{symbol}",
                "returns": _copy_roots_api_returns(symbol, value),
                "value": _copy_roots_api_value(symbol, value),
                "registry_seam": _copy_roots_api_registry_seam(feature),
                "surface": "sdk",
                "doc_page": _COPY_ROOTS_API_REFERENCE_PAGE,
                "test_anchor": _COPY_ROOTS_API_TEST_ANCHOR,
            }
        )
    return rows


def _copy_roots_api_feature(symbol: str) -> str:
    if symbol == "ARTIFACT_TARGET_ROOTS":
        return "target-roots"
    if symbol == "ProjectCopyRootSpecError":
        return "errors"
    if symbol == "CopyRootSpec":
        return "models"
    if symbol == "project_copy_roots":
        return "manifest"
    if symbol in {"copy_root_artifacts", "merge_copy_root_artifacts"}:
        return "artifacts"
    if symbol in {
        "COPY_ROOTS_API_TABLE_SCHEMA",
        "CopyRootsApiRow",
        "CopyRootsApiTable",
        "get_copy_roots_api_selection",
        "get_copy_roots_api_table",
        "render_copy_roots_api_reference_markdown",
    }:
        return "copy-roots-api"
    return "copy-roots"


def _copy_roots_api_kind(symbol: str, value: object) -> str:
    if symbol.endswith("_SCHEMA"):
        return "schema constant"
    if symbol == "ARTIFACT_TARGET_ROOTS":
        return "set constant"
    if is_typeddict(value):
        return "TypedDict"
    if is_dataclass(value):
        return "dataclass"
    if inspect.isfunction(value):
        return "function"
    if inspect.isclass(value) and issubclass(value, Exception):
        return "exception"
    return type(value).__name__


def _copy_roots_api_returns(symbol: str, value: object) -> str:
    if symbol.endswith("_SCHEMA"):
        return str(value)
    if symbol == "ARTIFACT_TARGET_ROOTS" and isinstance(value, set):
        return f"set[{len(value)}]"
    if is_typeddict(value):
        return "TypedDict schema"
    if is_dataclass(value):
        return f"{symbol} dataclass"
    if inspect.isfunction(value):
        return api_annotation_text(inspect.signature(value).return_annotation, strip_string_quotes=True)
    if inspect.isclass(value) and issubclass(value, Exception):
        return f"{symbol} exception"
    return type(value).__name__


def _copy_roots_api_value(symbol: str, value: object) -> str:
    if symbol.endswith("_SCHEMA"):
        return str(value)
    if symbol == "ARTIFACT_TARGET_ROOTS" and isinstance(value, set):
        return ", ".join(sorted(str(item) for item in value))
    return ""


def _copy_roots_api_registry_seam(feature: str) -> str:
    if feature == "target-roots":
        return "copy-root target roots"
    if feature == "errors":
        return "copy-root validation"
    if feature == "models":
        return "copy-root manifest model"
    if feature == "manifest":
        return "project manifest copy_roots parser"
    if feature == "artifacts":
        return "copy-root artifact pipeline"
    if feature == "copy-roots-api":
        return "copy roots API table"
    return "SDK copy roots"


def _required_token(value: object, key: str, path: Path) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ProjectCopyRootSpecError(f"{path} key {key!r} must be a non-empty string.")
    text = value.strip()
    if text in {".", ".."} or "/" in text or "\\" in text or any(char.isspace() for char in text):
        raise ProjectCopyRootSpecError(f"{path} key {key!r} must be one path token.")
    return text


def _resolve_source(root: Path, value: object, key: str, path: Path) -> Path:
    if not isinstance(value, str) or not value.strip():
        raise ProjectCopyRootSpecError(f"{path} key {key!r} must be a non-empty directory path.")
    candidate = Path(value).expanduser()
    if not candidate.is_absolute():
        candidate = root / candidate
    try:
        return candidate.resolve()
    except OSError as error:
        raise ProjectCopyRootSpecError(f"{path} key {key!r} cannot be resolved: {value}") from error


def _safe_target(value: object, key: str, path: Path) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ProjectCopyRootSpecError(f"{path} key {key!r} must be a non-empty relative output path.")
    text = value.strip()
    if "\\" in text:
        raise ProjectCopyRootSpecError(f"{path} key {key!r} must be relative and stay under the target root.")
    target = PurePosixPath(text)
    if target.is_absolute() or ".." in target.parts:
        raise ProjectCopyRootSpecError(f"{path} key {key!r} must be relative and stay under the target root.")
    return "." if target == PurePosixPath(".") else str(target)


def _target_root(value: object, key: str, path: Path) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ProjectCopyRootSpecError(f"{path} key {key!r} must be one of: build, output.")
    text = value.strip()
    if text not in ARTIFACT_TARGET_ROOTS:
        raise ProjectCopyRootSpecError(f"{path} key {key!r} must be one of: build, output.")
    return text


def _patterns(value: object, key: str, path: Path, *, allow_empty: bool = False) -> tuple[str, ...]:
    if not isinstance(value, list) or (not value and not allow_empty):
        raise ProjectCopyRootSpecError(f"{path} key {key!r} must be a list of glob patterns.")
    patterns: list[str] = []
    for index, item in enumerate(value):
        pattern_key = f"{key}[{index}]"
        if not isinstance(item, str) or not item.strip():
            raise ProjectCopyRootSpecError(f"{path} key {pattern_key!r} must be a non-empty glob pattern.")
        pattern = item.strip().replace("\\", "/")
        if PurePosixPath(pattern).is_absolute() or ".." in PurePosixPath(pattern).parts:
            raise ProjectCopyRootSpecError(f"{path} key {pattern_key!r} must stay under the source root.")
        patterns.append(pattern)
    return tuple(patterns)


def _included(rel_path: str, include: tuple[str, ...], exclude: tuple[str, ...]) -> bool:
    if not any(_match(rel_path, pattern) for pattern in include):
        return False
    return not any(_match(rel_path, pattern) for pattern in exclude)


def _match(rel_path: str, pattern: str) -> bool:
    if fnmatchcase(rel_path, pattern) or fnmatchcase(rel_path, f"{pattern.rstrip('/')}/**"):
        return True
    if pattern.startswith("**/") and fnmatchcase(rel_path, pattern[3:]):
        return True
    return False


def _target_path(target: str, rel_path: str) -> str:
    if target == ".":
        return rel_path
    return f"{target.rstrip('/')}/{rel_path}"


def _artifact_path(artifact: Artifact) -> str:
    return str(artifact.path).replace("\\", "/")


def _artifact_target_root(artifact: Artifact) -> str:
    return str(artifact.target_root)


def _copy_root_id(artifact: Artifact) -> str:
    value = artifact.metadata.get("copy_root")
    return value if isinstance(value, str) and value else artifact.owner.removeprefix("copy_root:")
