"""Focused structural-path indexing contracts for cached publication."""

from __future__ import annotations

from collections.abc import Mapping
from typing import cast

import pytest

from paradev.build import Artifact, BuildResult
from paradev.build import publication as build_publication
from paradev.build._fs import AnchoredDirectory


class _PublicationRootStub:
    def __init__(self, *existing_paths: str) -> None:
        self.existing_paths = frozenset(existing_paths)

    def entry_exists(self, path: str) -> bool:
        return path in self.existing_paths

    def same_entry(self, left: str, right: str) -> bool:
        return left in self.existing_paths and right in self.existing_paths


def _publication_root(*existing_paths: str) -> AnchoredDirectory:
    return cast(AnchoredDirectory, _PublicationRootStub(*existing_paths))


def _ledger_row(
    path: str,
    *,
    target_root: str = "output",
) -> dict[str, object]:
    return {
        "target_root": target_root,
        "path": path,
        "owner": "module:test/INDEX",
        "module_ids": ["test/INDEX"],
        "collection_keys": [],
    }


def _path_index(
    *rows: Mapping[str, object],
) -> build_publication._LedgerPathConflictIndex:
    keyed_rows = {build_publication._ledger_key(row): row for row in rows}
    return build_publication._LedgerPathConflictIndex.from_keyed_rows(keyed_rows)


@pytest.mark.parametrize(
    ("previous_path", "current_path"),
    (
        ("common/ideas", "common/ideas/alpha.txt"),
        ("common/ideas/alpha.txt", "common/ideas"),
        ("GFX/CAFÉ", "gfx/cafe\u0301/ICON.DDS"),
        ("GFX/CAFÉ/ICON.DDS", "gfx/cafe\u0301"),
    ),
)
def test_ledger_path_conflict_index_finds_strict_ancestors_and_descendants(
    previous_path: str,
    current_path: str,
) -> None:
    previous = _ledger_row(previous_path)
    index = _path_index(previous)

    assert index.conflicting_rows(_ledger_row(current_path)) == (previous,)
    assert index.conflicting_rows(_ledger_row(current_path, target_root="build")) == ()


def test_ledger_path_conflict_index_keeps_portable_spelling_aliases_exact() -> None:
    previous = _ledger_row("GFX/CAFÉ/ICON.DDS")
    current = _ledger_row("gfx/cafe\u0301/icon.dds")
    index = _path_index(previous)

    assert build_publication._ledger_key(previous) == build_publication._ledger_key(current)
    assert index.conflicting_rows(current) == ()


def test_cached_preflight_preserves_unicode_case_spelling_rename() -> None:
    previous_path = "GFX/CAFÉ/ICON.DDS"
    current_path = "gfx/cafe\u0301/icon.dds"
    previous = _ledger_row(previous_path)
    result = BuildResult(
        project_id="portable_spelling",
        artifacts=(
            Artifact(
                path=current_path,
                artifact_type="copy",
                owner="module:test/INDEX",
            ),
        ),
    )

    permissions = build_publication.require_publishable_artifacts(
        result,
        output_root=_publication_root(previous_path),
        build_root=_publication_root(),
        previous_rows=(previous,),
        claimed_roots={"build": True, "output": True},
    )

    assert permissions.rename_paths["output"] == {current_path: previous_path}


def test_cached_preflight_changed_ledger_uses_linear_path_index_operations(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    row_count = 2_048
    previous_rows = tuple(_ledger_row(f"legacy/{index:05d}.txt") for index in range(row_count))
    result = BuildResult(
        project_id="changed_ledger",
        artifacts=tuple(
            Artifact(
                path=f"current/{index:05d}.txt",
                artifact_type="pdx",
                owner=f"module:test/{index:05d}",
            )
            for index in range(row_count)
        ),
    )
    parent_identity_operations = 0
    strict_parent_identities = build_publication._strict_parent_identities

    def count_parent_identity_operation(identity: str) -> tuple[str, ...]:
        nonlocal parent_identity_operations
        parent_identity_operations += 1
        if parent_identity_operations > row_count * 2:
            raise AssertionError("Cached publication preflight exceeded its linear path-index operation budget.")
        return strict_parent_identities(identity)

    monkeypatch.setattr(
        build_publication,
        "_strict_parent_identities",
        count_parent_identity_operation,
    )

    permissions = build_publication.require_publishable_artifacts(
        result,
        output_root=_publication_root(),
        build_root=_publication_root(),
        previous_rows=previous_rows,
        claimed_roots={"build": True, "output": True},
    )

    assert parent_identity_operations == row_count * 2
    assert permissions.replace_paths == {"build": frozenset(), "output": frozenset()}
    assert permissions.adopt_paths == {"build": frozenset(), "output": frozenset()}
    assert permissions.rename_paths == {"build": {}, "output": {}}
