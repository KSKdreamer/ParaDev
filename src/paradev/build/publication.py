"""Hidden publication state for safe cached artifact reconciliation."""

from __future__ import annotations

import json
import os
from collections.abc import Iterable, Mapping, Sequence, Set
from dataclasses import dataclass, field, replace
from pathlib import Path, PurePosixPath

from paradev.portable_paths import portable_path_identity, windows_portable_component_error

from ._fs import AnchoredDirectory, open_anchored_directory
from .manifest import MANIFEST_SCHEMAS, artifact_collection_ids, artifact_module_ids
from .records import Artifact, BuildResult

EMITTED_ARTIFACTS_SCHEMA = "paradev.build.emitted-artifacts.v3"
_PREVIOUS_EMITTED_ARTIFACTS_SCHEMA = "paradev.build.emitted-artifacts.v2"
_LEGACY_EMITTED_ARTIFACTS_SCHEMA = "paradev.build.emitted-artifacts.v1"
EMITTED_ARTIFACTS_NAME = ".emitted-artifacts.json"
PUBLICATION_ROOT_SCHEMA = "paradev.build.publication-root.v1"
PUBLICATION_ROOT_NAME = ".paradev-publication.json"
_TARGET_ROOTS = frozenset({"build", "output"})


@dataclass(frozen=True, slots=True)
class PublicationState:
    """Validated hidden publication state for one pair of generated roots."""

    rows: tuple[dict[str, object], ...] = ()
    full_clean_owned: Mapping[str, bool] = field(default_factory=lambda: {"build": False, "output": False})
    complete: bool = False
    whole_project_baseline: bool = False


@dataclass(frozen=True, slots=True)
class PublicationRootState:
    """Validated exclusive-project claim for one generated root."""

    claimed: bool
    full_clean_owned: bool


@dataclass(frozen=True, slots=True)
class PublicationWritePermissions:
    """Per-root replacement and exact-content recovery permissions."""

    replace_paths: Mapping[str, frozenset[str]]
    adopt_paths: Mapping[str, frozenset[str]]
    rename_paths: Mapping[str, Mapping[str, str]]


@dataclass(frozen=True, slots=True)
class _ProjectedPublication:
    """Artifact rows validated once before a publication mutates the filesystem."""

    result: BuildResult
    current_by_key: dict[tuple[str, str], dict[str, object]]
    planned_by_key: dict[tuple[str, str], dict[str, object]]
    current_artifacts_by_key: dict[tuple[str, str], Artifact]


@dataclass(slots=True)
class _PublicationTransaction:
    """In-memory mirror of the exact durable ledger checkpoint being written."""

    projected: _ProjectedPublication
    previous_by_key: Mapping[tuple[str, str], Mapping[str, object]]
    reconciled_previous_keys: set[tuple[str, str]]
    stale_keys: set[tuple[str, str]]
    structural_blocker_keys: set[tuple[str, str]]
    checkpoint_by_key: dict[tuple[str, str], dict[str, object]] = field(default_factory=dict)
    checkpoint_started: bool = False


@dataclass(frozen=True, slots=True)
class _LedgerPathConflictIndex:
    """Index strict artifact-path ancestors and descendants by portable identity."""

    rows_by_key: Mapping[tuple[str, str], Mapping[str, object]]
    descendants_by_key: Mapping[tuple[str, str], tuple[Mapping[str, object], ...]]

    @classmethod
    def from_keyed_rows(
        cls,
        rows_by_key: Mapping[tuple[str, str], Mapping[str, object]],
    ) -> "_LedgerPathConflictIndex":
        """Build an index whose size is bounded by the total path-part count."""

        rows = dict(rows_by_key)
        descendants: dict[tuple[str, str], list[Mapping[str, object]]] = {}
        for (target_root, identity), row in rows.items():
            for ancestor in _strict_parent_identities(identity):
                descendants.setdefault((target_root, ancestor), []).append(row)
        return cls(
            rows_by_key=rows,
            descendants_by_key={key: tuple(indexed_rows) for key, indexed_rows in descendants.items()},
        )

    def conflicting_rows(
        self,
        row: Mapping[str, object],
    ) -> tuple[Mapping[str, object], ...]:
        """Return rows that are strict ancestors or descendants of ``row``."""

        target_root, identity = _ledger_key(row)
        conflicts: list[Mapping[str, object]] = []
        for ancestor in _strict_parent_identities(identity):
            previous = self.rows_by_key.get((target_root, ancestor))
            if previous is not None:
                conflicts.append(previous)
        conflicts.extend(self.descendants_by_key.get((target_root, identity), ()))
        return tuple(conflicts)


def inspect_publication_root(
    root: AnchoredDirectory,
    *,
    root_name: str,
    project_id: str,
    project_root: Path,
) -> PublicationRootState:
    """Inspect one root claim and refresh remount-volatile device identity."""

    if root_name not in _TARGET_ROOTS:
        raise ValueError(f"Unsupported publication root name: {root_name!r}.")
    encoded = root.read_bytes(PUBLICATION_ROOT_NAME)
    if encoded is None:
        return PublicationRootState(claimed=False, full_clean_owned=root.is_empty())
    path = root.requested_path / PUBLICATION_ROOT_NAME
    try:
        payload = json.loads(encoded.decode("utf-8"))
    except (UnicodeError, json.JSONDecodeError) as error:
        raise ValueError(f"Invalid ParaDev publication-root marker: {path}.") from error
    if not isinstance(payload, dict) or payload.get("schema") != PUBLICATION_ROOT_SCHEMA:
        raise ValueError(f"Unsupported ParaDev publication-root marker: {path}.")
    identity = payload.get("identity")
    if not isinstance(identity, dict):
        raise ValueError(f"Invalid ParaDev publication-root identity: {path}.")
    stored_project_id = identity.get("project_id")
    stored_project_root = identity.get("project_root")
    if stored_project_id != project_id or stored_project_root != _publication_path_identity(project_root):
        raise ValueError(
            f"Generated publication root belongs to project root {stored_project_root!r}, "
            f"not {_publication_path_identity(project_root)!r}: {root.requested_path}."
        )
    if identity.get("root_name") != root_name:
        raise ValueError(f"ParaDev publication-root marker has the wrong root role: {path}.")
    stored_root = identity.get("root")
    expected_root = _publication_root_record(root, full_clean_owned=False)
    if not isinstance(stored_root, dict) or not _publication_root_stable_identity_matches(stored_root, expected_root):
        raise ValueError(f"ParaDev publication-root marker does not match its directory: {path}.")
    full_clean_owned = payload.get("full_clean_owned")
    if not isinstance(full_clean_owned, bool):
        raise ValueError(f"ParaDev publication-root marker has invalid ownership state: {path}.")
    if stored_root.get("device") != expected_root["device"]:
        current = root.read_bytes(PUBLICATION_ROOT_NAME)
        if current != encoded:
            raise ValueError(f"ParaDev publication-root marker changed while its device identity was being refreshed: {path}.")
        refreshed_identity = dict(identity)
        refreshed_identity["root"] = expected_root
        refreshed_payload = dict(payload)
        refreshed_payload["identity"] = refreshed_identity
        refreshed = (json.dumps(refreshed_payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")
        root.write_bytes(PUBLICATION_ROOT_NAME, refreshed, replace=True)
    return PublicationRootState(claimed=True, full_clean_owned=full_clean_owned)


def claim_publication_root(
    root: AnchoredDirectory,
    *,
    root_name: str,
    project_id: str,
    project_root: Path,
    full_clean_owned: bool,
    require_empty_for_full_clean: bool,
) -> bool:
    """Atomically claim an unmarked generated root for one project.

    Return the effective full-clean ownership after revalidating any claim
    derived from an earlier empty-root inspection.
    """

    if root_name not in _TARGET_ROOTS:
        raise ValueError(f"Unsupported publication root name: {root_name!r}.")
    effective_full_clean_owned = full_clean_owned and (not require_empty_for_full_clean or root.is_empty())
    payload = {
        "schema": PUBLICATION_ROOT_SCHEMA,
        "identity": {
            "project_id": project_id,
            "project_root": _publication_path_identity(project_root),
            "root_name": root_name,
            "root": _publication_root_record(root, full_clean_owned=False),
        },
        "full_clean_owned": effective_full_clean_owned,
    }
    encoded = (json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")
    root.write_bytes(PUBLICATION_ROOT_NAME, encoded, replace=False)
    return effective_full_clean_owned


def require_publishable_artifacts(
    result: BuildResult,
    *,
    output_root: AnchoredDirectory,
    build_root: AnchoredDirectory,
    previous_rows: Sequence[Mapping[str, object]],
    claimed_roots: Mapping[str, bool],
    artifact_rows: Iterable[Mapping[str, object]] | None = None,
) -> PublicationWritePermissions:
    """Reject existing artifact leaves not tracked with the exact same spelling.

    The returned paths are the only leaves writers may atomically replace.
    Every other destination must use a no-clobber commit, which closes the
    preflight-to-rename race with other processes.
    """

    previous_by_key = {_ledger_key(row): row for row in previous_rows}
    previous_path_index = _LedgerPathConflictIndex.from_keyed_rows(previous_by_key)
    replaceable: dict[str, set[str]] = {"build": set(), "output": set()}
    adoptable: dict[str, set[str]] = {"build": set(), "output": set()}
    renamed: dict[str, dict[str, str]] = {"build": {}, "output": {}}
    rows = emitted_artifact_rows(result) if artifact_rows is None else artifact_rows
    for row in rows:
        target_root = str(row["target_root"])
        path = str(row["path"])
        previous = previous_by_key.get(_ledger_key(row))
        root = output_root if target_root == "output" else build_root
        if previous is not None:
            previous_path = str(previous["path"])
            if previous_path == path and root.entry_exists(path):
                replaceable[target_root].add(path)
            elif previous_path != path:
                renamed[target_root][path] = previous_path
                if root.same_entry(previous_path, path):
                    replaceable[target_root].add(path)
                elif previous.get("pending_replacement_path") == path and claimed_roots.get(target_root, False) and root.entry_exists(path):
                    adoptable[target_root].add(path)
            elif previous.get("pending_replacement_path") == path and claimed_roots.get(target_root, False) and root.entry_exists(path):
                adoptable[target_root].add(path)
            continue
        conflicting_previous = previous_path_index.conflicting_rows(row)
        if conflicting_previous:
            if (
                claimed_roots.get(target_root, False)
                and all(previous_row.get("pending_removal") is True for previous_row in conflicting_previous)
                and root.entry_exists(path)
            ):
                adoptable[target_root].add(path)
            continue
        if root.entry_exists(path):
            if claimed_roots.get(target_root, False):
                adoptable[target_root].add(path)
                continue
            raise ValueError("Cached build refuses to replace an untracked existing artifact path: " f"{target_root}:{path}.")
    return PublicationWritePermissions(
        replace_paths={root_name: frozenset(paths) for root_name, paths in replaceable.items()},
        adopt_paths={root_name: frozenset(paths) for root_name, paths in adoptable.items()},
        rename_paths={root_name: dict(paths) for root_name, paths in renamed.items()},
    )


def require_publishable_manifests(
    build_root: AnchoredDirectory,
    *,
    root_claimed: bool,
    project_id: str,
) -> None:
    """Reject foreign manifest replacement before a project claims a root."""

    if root_claimed:
        return
    for name, schema in MANIFEST_SCHEMAS.items():
        try:
            encoded = build_root.read_bytes(name)
            if encoded is None:
                continue
            payload = json.loads(encoded.decode("utf-8"))
        except (UnicodeError, json.JSONDecodeError, ValueError) as error:
            raise ValueError(f"Build manifest path is not a valid ParaDev manifest owned by this project: {name}.") from error
        if not isinstance(payload, dict) or payload.get("schema") != schema or payload.get("project_id") != project_id:
            raise ValueError(f"Build manifest path is not a valid ParaDev manifest owned by this project: {name}.")


def emitted_artifact_rows(result: BuildResult) -> tuple[dict[str, object], ...]:
    """Return validated ledger rows for artifacts in one emitted result."""

    module_families = {module.module_id: module.family for module in result.modules}
    module_collections: dict[str, set[tuple[str, str]]] = {}
    for module in result.modules:
        if module.collection_id is not None:
            module_collections.setdefault(module.module_id, set()).add((module.family, module.collection_id))
    collection_families: dict[str, set[str]] = {}
    for collection in result.collections:
        collection_families.setdefault(collection.collection_id, set()).add(collection.family)
        for module_id in collection.module_ids:
            module_collections.setdefault(module_id, set()).add((collection.family, collection.collection_id))

    rows: dict[tuple[str, str], dict[str, object]] = {}
    for artifact in result.artifacts:
        path = _relative_artifact_path(artifact.path)
        target_root = artifact.target_root
        if target_root not in _TARGET_ROOTS:
            raise ValueError(f"Unsupported emitted artifact target root: {target_root!r}.")
        _validate_unreserved_build_path(target_root, path)
        view = artifact.to_dict()
        module_ids = artifact_module_ids(view)
        collection_ids = artifact_collection_ids(view)
        family = artifact.metadata.get("family")
        if not isinstance(family, str) or not family:
            families = {module_families[module_id] for module_id in module_ids if module_id in module_families}
            family = next(iter(families)) if len(families) == 1 else None
        collection_keys = sorted(
            {
                (candidate_family, collection_id)
                for collection_id in collection_ids
                for candidate_family in ((family,) if isinstance(family, str) else tuple(sorted(collection_families.get(collection_id, ()))))
            }
            | {collection_key for module_id in module_ids for collection_key in module_collections.get(module_id, ())}
        )
        row: dict[str, object] = {
            "target_root": target_root,
            "path": path,
            "owner": artifact.owner,
            "module_ids": list(module_ids),
            "collection_keys": [list(key) for key in collection_keys],
        }
        if isinstance(family, str):
            row["family"] = family
        publication_scope = artifact.metadata.get("publication_scope")
        if publication_scope is not None:
            if publication_scope != "project":
                raise ValueError(f"Unsupported emitted artifact publication scope: {publication_scope!r}.")
            row["publication_scope"] = publication_scope
        publication_replaces = artifact.metadata.get("publication_replaces")
        if publication_replaces is not None:
            if publication_scope != "project":
                raise ValueError("Emitted artifact publication_replaces requires project publication scope.")
            if not isinstance(publication_replaces, Sequence) or isinstance(publication_replaces, str | bytes):
                raise ValueError("Emitted artifact publication_replaces must be a list of relative paths.")
            replace_paths = tuple(sorted({_relative_artifact_path(replace_path) for replace_path in publication_replaces}))
            for replace_path in replace_paths:
                _validate_unreserved_build_path(target_root, replace_path)
            row["publication_replaces"] = list(replace_paths)
        key = (target_root, _portable_relative_path_identity(path))
        if key in rows:
            raise ValueError(f"Duplicate emitted artifact ledger path: {target_root}:{path}.")
        rows[key] = row
    _validate_no_structural_path_collisions(rows)
    return tuple(rows[key] for key in sorted(rows))


def load_emitted_artifact_rows(
    build_root: Path | AnchoredDirectory,
    *,
    project_id: str,
    project_root: Path,
    output_root: Path | AnchoredDirectory,
) -> tuple[dict[str, object], ...]:
    """Load and validate the previous hidden publication ledger."""

    return load_publication_state(
        build_root,
        project_id=project_id,
        project_root=project_root,
        output_root=output_root,
    ).rows


def load_publication_state(
    build_root: Path | AnchoredDirectory,
    *,
    project_id: str,
    project_root: Path,
    output_root: Path | AnchoredDirectory,
) -> PublicationState:
    """Load rows and full-clean ownership from one validated hidden ledger."""

    validated = _validated_publication_ledger(
        build_root,
        project_id=project_id,
        project_root=project_root,
    )
    if validated is None:
        return PublicationState()
    rows, stored_roots, path, state, whole_project_baseline = validated
    expected_roots = _publication_root_records(
        output_root=output_root,
        build_root=build_root,
        full_clean_owned={"build": False, "output": False},
    )
    ownership: dict[str, bool] = {}
    matching_roots: dict[str, bool] = {}
    for root_name in sorted(_TARGET_ROOTS):
        stored_root = stored_roots.get(root_name)
        expected_root = expected_roots[root_name]
        if not isinstance(stored_root, dict):
            raise ValueError(f"ParaDev emitted-artifact ledger has invalid {root_name} root identity: {path}.")
        full_clean_owned = stored_root.get("full_clean_owned")
        if not isinstance(full_clean_owned, bool):
            raise ValueError(f"ParaDev emitted-artifact ledger has invalid {root_name} ownership state: {path}.")
        root_matches = _publication_root_stable_identity_matches(stored_root, expected_root)
        matching_roots[root_name] = root_matches
        ownership[root_name] = full_clean_owned if root_matches else False
    matching_rows = tuple(row for row in rows if matching_roots[str(row["target_root"])])
    roots_match = all(matching_roots.values())
    return PublicationState(
        rows=matching_rows,
        full_clean_owned=ownership,
        complete=state == "complete" and roots_match,
        whole_project_baseline=whole_project_baseline and roots_match,
    )


def load_build_root_ownership(
    build_root: Path | AnchoredDirectory,
    *,
    project_id: str,
    project_root: Path,
) -> bool:
    """Return legacy-v2 full-clean ownership for only the build root."""

    validated = _validated_publication_ledger(
        build_root,
        project_id=project_id,
        project_root=project_root,
    )
    if validated is None:
        return False
    _rows, stored_roots, path, _state, _whole_project_baseline = validated
    stored_root = stored_roots.get("build")
    if not isinstance(stored_root, dict):
        raise ValueError(f"ParaDev emitted-artifact ledger has invalid build root identity: {path}.")
    full_clean_owned = stored_root.get("full_clean_owned")
    if not isinstance(full_clean_owned, bool):
        raise ValueError(f"ParaDev emitted-artifact ledger has invalid build ownership state: {path}.")
    expected_root = _publication_root_record(build_root, full_clean_owned=False)
    root_matches = _publication_root_stable_identity_matches(stored_root, expected_root)
    return full_clean_owned and root_matches


def _publication_root_stable_identity_matches(
    stored_root: Mapping[str, object],
    expected_root: Mapping[str, object],
) -> bool:
    """Match one root across remounts whose operating-system device id drifts."""

    return all(stored_root.get(key) == expected_root.get(key) for key in ("path", "inode"))


def _validated_publication_ledger(
    build_root: Path | AnchoredDirectory,
    *,
    project_id: str,
    project_root: Path,
) -> tuple[tuple[dict[str, object], ...], dict[str, object], Path, str, bool] | None:
    path = _root_path(build_root) / EMITTED_ARTIFACTS_NAME
    if isinstance(build_root, AnchoredDirectory):
        encoded = build_root.read_bytes(EMITTED_ARTIFACTS_NAME)
    else:
        try:
            with open_anchored_directory(build_root, create=False) as publication_root:
                encoded = publication_root.read_bytes(EMITTED_ARTIFACTS_NAME)
        except FileNotFoundError:
            return None
    if encoded is None:
        return None
    try:
        payload = json.loads(encoded.decode("utf-8"))
    except (UnicodeError, json.JSONDecodeError) as error:
        raise ValueError(f"Invalid ParaDev emitted-artifact ledger: {path}.") from error
    if not isinstance(payload, dict):
        raise ValueError(f"Unsupported ParaDev emitted-artifact ledger: {path}.")
    schema = payload.get("schema")
    if schema == _LEGACY_EMITTED_ARTIFACTS_SCHEMA:
        return None
    if schema not in {_PREVIOUS_EMITTED_ARTIFACTS_SCHEMA, EMITTED_ARTIFACTS_SCHEMA}:
        raise ValueError(f"Unsupported ParaDev emitted-artifact ledger: {path}.")
    state = payload.get("state")
    if state not in {"pending", "complete"}:
        raise ValueError(f"ParaDev emitted-artifact ledger has invalid publication state: {path}.")
    if schema == EMITTED_ARTIFACTS_SCHEMA:
        whole_project_baseline = payload.get("whole_project_baseline")
        if not isinstance(whole_project_baseline, bool):
            raise ValueError(f"ParaDev emitted-artifact ledger has invalid whole-project baseline state: {path}.")
    else:
        whole_project_baseline = False
    artifacts = payload.get("artifacts")
    if not isinstance(artifacts, list):
        raise ValueError(f"ParaDev emitted-artifact ledger has no artifacts list: {path}.")
    rows = tuple(_validated_ledger_row(row, ledger_path=path) for row in artifacts)
    if state == "complete" and any("pending_removal" in row or "pending_replacement_path" in row for row in rows):
        raise ValueError(f"Complete ParaDev emitted-artifact ledger contains pending recovery state: {path}.")
    keys = {_ledger_key(row) for row in rows}
    if len(keys) != len(rows):
        raise ValueError(f"ParaDev emitted-artifact ledger contains duplicate paths: {path}.")
    identity = payload.get("identity")
    if not isinstance(identity, dict):
        raise ValueError(f"ParaDev emitted-artifact ledger has invalid root identity: {path}.")
    stored_project_id = identity.get("project_id")
    if not isinstance(stored_project_id, str) or not stored_project_id:
        raise ValueError(f"ParaDev emitted-artifact ledger has invalid project identity: {path}.")
    if stored_project_id != project_id:
        raise ValueError(f"ParaDev emitted-artifact ledger belongs to project {stored_project_id!r}, " f"not {project_id!r}: {path}.")
    stored_project_root = identity.get("project_root")
    expected_project_root = _publication_path_identity(project_root)
    if stored_project_root != expected_project_root:
        raise ValueError(f"ParaDev emitted-artifact ledger belongs to project root {stored_project_root!r}, " f"not {expected_project_root!r}: {path}.")
    stored_roots = identity.get("roots")
    if not isinstance(stored_roots, dict):
        raise ValueError(f"ParaDev emitted-artifact ledger has invalid root identity: {path}.")
    return rows, stored_roots, path, state, whole_project_baseline


def _project_artifact_publication(
    result: BuildResult,
    *,
    planned_result: BuildResult | None = None,
) -> _ProjectedPublication:
    """Validate and project current and planned artifact rows exactly once."""

    current_by_key = {_ledger_key(row): row for row in emitted_artifact_rows(result)}
    planned_by_key = _planned_rows(
        planned_result if planned_result is not None else result,
        current_result=result,
        current_by_key=current_by_key,
    )
    current_artifacts_by_key = {_artifact_ledger_key(artifact): artifact for artifact in result.artifacts}
    return _ProjectedPublication(
        result=result,
        current_by_key=current_by_key,
        planned_by_key=planned_by_key,
        current_artifacts_by_key=current_artifacts_by_key,
    )


def _begin_publication_transaction(
    projected: _ProjectedPublication,
    *,
    previous_rows: Sequence[Mapping[str, object]],
    target_modules: Set[str] | None = None,
    target_collections: Set[tuple[str, str]] | None = None,
    target_families: Set[str] | None = None,
    family_wide: bool = False,
    family_wide_families: Set[str] | None = None,
) -> _PublicationTransaction:
    """Resolve reconciliation scope around one validated publication plan."""

    (
        _current_by_key,
        _planned_by_key,
        previous_by_key,
        reconciled_previous_keys,
        stale_keys,
        structural_blocker_keys,
        _explicit_predecessor_keys,
    ) = _reconciliation_rows(
        projected.result,
        planned_result=None,
        previous_rows=previous_rows,
        target_modules=target_modules,
        target_collections=target_collections,
        target_families=target_families,
        family_wide=family_wide,
        family_wide_families=family_wide_families,
        projected=projected,
    )
    return _PublicationTransaction(
        projected=projected,
        previous_by_key=previous_by_key,
        reconciled_previous_keys=reconciled_previous_keys,
        stale_keys=stale_keys,
        structural_blocker_keys=structural_blocker_keys,
    )


def reconcile_emitted_artifacts(
    result: BuildResult,
    *,
    planned_result: BuildResult | None = None,
    project_root: Path,
    output_root: Path | AnchoredDirectory,
    build_root: Path | AnchoredDirectory,
    previous_rows: Sequence[Mapping[str, object]],
    target_modules: Set[str] | None = None,
    target_collections: Set[tuple[str, str]] | None = None,
    target_families: Set[str] | None = None,
    family_wide: bool = False,
    family_wide_families: Set[str] | None = None,
    delete_stale: bool = True,
    full_clean_owned: Mapping[str, bool],
    whole_project_baseline: bool,
    transaction: _PublicationTransaction | None = None,
) -> int:
    """Prune stale tracked artifacts and atomically publish the new ledger.

    A ``None`` target denotes a whole-project cached/full build. Partial builds
    replace only rows owned by their resolved safe scope plus global
    project/copy-root outputs. Files absent from the ledger are never deleted.
    Each post-write deletion is checkpointed before the next path is touched.
    """

    if transaction is None:
        transaction = _begin_publication_transaction(
            _project_artifact_publication(result, planned_result=planned_result),
            previous_rows=previous_rows,
            target_modules=target_modules,
            target_collections=target_collections,
            target_families=target_families,
            family_wide=family_wide,
            family_wide_families=family_wide_families,
        )
    current_by_key = transaction.projected.current_by_key
    planned_by_key = transaction.projected.planned_by_key
    previous_by_key = transaction.previous_by_key
    reconciled_previous_keys = transaction.reconciled_previous_keys
    stale_keys = transaction.stale_keys
    structural_blocker_keys = transaction.structural_blocker_keys
    renamed_keys = {key for key in reconciled_previous_keys.intersection(planned_by_key) if previous_by_key[key]["path"] != planned_by_key[key]["path"]}
    cleanup_keys = (stale_keys - structural_blocker_keys) | renamed_keys if delete_stale else set()
    if cleanup_keys:
        _delete_rows_with_pending_checkpoints(
            cleanup_keys,
            result=result,
            project_root=project_root,
            current_by_key=current_by_key,
            previous_by_key=previous_by_key,
            renamed_keys=renamed_keys,
            output_root=output_root,
            build_root=build_root,
            full_clean_owned=full_clean_owned,
            whole_project_baseline=whole_project_baseline,
            pending_by_key=transaction.checkpoint_by_key if transaction.checkpoint_started else None,
        )
    retained = {key: row for key, row in previous_by_key.items() if key not in reconciled_previous_keys}
    retained.update({key: planned_by_key[key] for key in reconciled_previous_keys.intersection(planned_by_key)})
    retained.update(current_by_key)
    _write_emitted_artifact_rows(
        build_root,
        tuple(retained[key] for key in sorted(retained)),
        project_id=result.project_id,
        project_root=project_root,
        output_root=output_root,
        state="complete",
        full_clean_owned=full_clean_owned,
        whole_project_baseline=whole_project_baseline,
    )
    transaction.checkpoint_by_key = {key: dict(row) for key, row in retained.items()}
    transaction.checkpoint_started = True
    return len(stale_keys)


def stage_emitted_artifacts(
    result: BuildResult,
    *,
    planned_result: BuildResult | None = None,
    project_root: Path,
    output_root: Path | AnchoredDirectory,
    build_root: Path | AnchoredDirectory,
    previous_rows: Sequence[Mapping[str, object]],
    target_modules: Set[str] | None = None,
    target_collections: Set[tuple[str, str]] | None = None,
    target_families: Set[str] | None = None,
    family_wide: bool = False,
    family_wide_families: Set[str] | None = None,
    full_clean_owned: Mapping[str, bool],
    whole_project_baseline: bool,
    transaction: _PublicationTransaction | None = None,
) -> int:
    """Journal only structural removals required before artifact writers.

    Structural blockers remain as explicit ``pending_removal`` rows so a retry
    can distinguish an already removed file from its replacement directory.
    Ordinary stale rows, renamed paths, and explicit migration predecessors
    remain byte-for-byte untouched until all replacement writers succeed.
    """

    if transaction is None:
        transaction = _begin_publication_transaction(
            _project_artifact_publication(result, planned_result=planned_result),
            previous_rows=previous_rows,
            target_modules=target_modules,
            target_collections=target_collections,
            target_families=target_families,
            family_wide=family_wide,
            family_wide_families=family_wide_families,
        )
    planned_by_key = transaction.projected.planned_by_key
    previous_by_key = transaction.previous_by_key
    reconciled_previous_keys = transaction.reconciled_previous_keys
    stale_keys = transaction.stale_keys
    structural_blocker_keys = transaction.structural_blocker_keys
    renamed_keys = {key for key in reconciled_previous_keys.intersection(planned_by_key) if previous_by_key[key]["path"] != planned_by_key[key]["path"]}
    pending = {key: dict(row) for key, row in previous_by_key.items()}
    for key, row in pending.items():
        if key not in structural_blocker_keys:
            row.pop("pending_removal", None)
        if key not in renamed_keys:
            row.pop("pending_replacement_path", None)
    for key in renamed_keys:
        pending[key]["pending_replacement_path"] = str(planned_by_key[key]["path"])
    transaction.checkpoint_by_key = pending
    transaction.checkpoint_started = True
    _write_emitted_artifact_rows(
        build_root,
        tuple(pending[key] for key in sorted(pending)),
        project_id=result.project_id,
        project_root=project_root,
        output_root=output_root,
        state="pending",
        full_clean_owned=full_clean_owned,
        whole_project_baseline=whole_project_baseline,
    )
    for key in _ordered_removal_keys(structural_blocker_keys, previous_by_key=previous_by_key):
        row = pending[key]
        if row.get("pending_removal") is True:
            continue
        _delete_tracked_artifact(
            (str(row["target_root"]), str(row["path"])),
            output_root=output_root,
            build_root=build_root,
        )
        row["pending_removal"] = True
        _write_emitted_artifact_rows(
            build_root,
            tuple(pending[pending_key] for pending_key in sorted(pending)),
            project_id=result.project_id,
            project_root=project_root,
            output_root=output_root,
            state="pending",
            full_clean_owned=full_clean_owned,
            whole_project_baseline=whole_project_baseline,
        )
    return len(stale_keys) + len(renamed_keys)


def clean_tracked_artifacts(
    result: BuildResult,
    *,
    project_root: Path,
    output_root: Path | AnchoredDirectory,
    build_root: Path | AnchoredDirectory,
    previous_rows: Sequence[Mapping[str, object]],
    target_roots: Set[str],
    full_clean_owned: Mapping[str, bool],
    whole_project_baseline: bool,
) -> int:
    """Delete only ledger-owned leaves from roots that cannot be cleared whole.

    A complete whole-project ledger is sufficient to rebuild a previously
    populated output root without treating unrelated files as generated data.
    The complete old ledger remains durable until every idempotent deletion
    succeeds. A crash or interruption can therefore retry from that ledger;
    only the final compact state transition rewrites it. This avoids rewriting
    a multi-megabyte PIHC3 ledger once per artifact.
    """

    unsupported = set(target_roots) - _TARGET_ROOTS
    if unsupported:
        names = ", ".join(sorted(unsupported))
        raise ValueError(f"Unsupported tracked-clean publication roots: {names}.")
    previous_by_key = {_ledger_key(row): dict(row) for row in previous_rows}
    clean_keys = {key for key in previous_by_key if key[0] in target_roots}
    if not clean_keys:
        return 0
    for key in _ordered_removal_keys(clean_keys, previous_by_key=previous_by_key):
        row = previous_by_key[key]
        _delete_tracked_artifact(
            (str(row["target_root"]), str(row["path"])),
            output_root=output_root,
            build_root=build_root,
        )
    retained = tuple(previous_by_key[key] for key in sorted(previous_by_key) if key not in clean_keys)
    _write_emitted_artifact_rows(
        build_root,
        retained,
        project_id=result.project_id,
        project_root=project_root,
        output_root=output_root,
        state="pending",
        full_clean_owned=full_clean_owned,
        whole_project_baseline=whole_project_baseline,
    )
    return len(clean_keys)


def record_written_artifacts(
    result: BuildResult,
    *,
    artifacts: Sequence[Artifact],
    project_root: Path,
    output_root: Path | AnchoredDirectory,
    build_root: Path | AnchoredDirectory,
    full_clean_owned: Mapping[str, bool],
    whole_project_baseline: bool,
    transaction: _PublicationTransaction | None = None,
) -> None:
    """Merge confirmed outputs without discarding a renamed predecessor."""

    confirmed = tuple(artifacts)
    if not confirmed:
        return
    if transaction is None:
        previous_rows = load_emitted_artifact_rows(
            build_root,
            project_id=result.project_id,
            project_root=project_root,
            output_root=output_root,
        )
        previous_by_key = {_ledger_key(row): dict(row) for row in previous_rows}
        confirmed_by_key = _project_confirmed_artifact_rows(result, confirmed)
    else:
        if not transaction.checkpoint_started:
            raise AssertionError("Artifact publication must be staged before writers are checkpointed.")
        previous_by_key = transaction.checkpoint_by_key
        confirmed_by_key = _transaction_confirmed_artifact_rows(transaction, confirmed)
    for key, row in confirmed_by_key.items():
        previous = previous_by_key.get(key)
        if previous is not None and previous.get("path") != row.get("path") and previous.get("pending_replacement_path") == row.get("path"):
            continue
        previous_by_key[key] = row
    _write_emitted_artifact_rows(
        build_root,
        tuple(previous_by_key[key] for key in sorted(previous_by_key)),
        project_id=result.project_id,
        project_root=project_root,
        output_root=output_root,
        state="pending",
        full_clean_owned=full_clean_owned,
        whole_project_baseline=whole_project_baseline,
    )


def _transaction_confirmed_artifact_rows(
    transaction: _PublicationTransaction,
    artifacts: Sequence[Artifact],
) -> dict[tuple[str, str], dict[str, object]]:
    """Reuse planned rows and reproject only artifacts changed by postprocessing."""

    confirmed_by_key: dict[tuple[str, str], dict[str, object]] = {}
    changed: list[Artifact] = []
    for artifact in artifacts:
        key = _artifact_ledger_key(artifact)
        planned_artifact = transaction.projected.current_artifacts_by_key.get(key)
        planned_row = transaction.projected.current_by_key.get(key)
        if planned_artifact == artifact and planned_row is not None:
            confirmed_by_key[key] = dict(planned_row)
        else:
            changed.append(artifact)
    if changed:
        confirmed_by_key.update(
            _project_confirmed_artifact_rows(
                transaction.projected.result,
                tuple(changed),
            )
        )
    for artifact in artifacts:
        transaction.projected.current_artifacts_by_key[_artifact_ledger_key(artifact)] = artifact
    transaction.projected.current_by_key.update(confirmed_by_key)
    return confirmed_by_key


def _project_confirmed_artifact_rows(
    result: BuildResult,
    artifacts: Sequence[Artifact],
) -> dict[tuple[str, str], dict[str, object]]:
    """Project ledger rows for one confirmed writer batch."""

    confirmed_result = BuildResult(
        project_id=result.project_id,
        modules=result.modules,
        collections=result.collections,
        artifacts=tuple(artifacts),
        profile=result.profile,
    )
    return {_ledger_key(row): dict(row) for row in emitted_artifact_rows(confirmed_result)}


def _reconciliation_rows(
    result: BuildResult,
    *,
    planned_result: BuildResult | None,
    previous_rows: Sequence[Mapping[str, object]],
    target_modules: Set[str] | None,
    target_collections: Set[tuple[str, str]] | None,
    target_families: Set[str] | None,
    family_wide: bool,
    family_wide_families: Set[str] | None,
    projected: _ProjectedPublication | None = None,
) -> tuple[
    dict[tuple[str, str], dict[str, object]],
    dict[tuple[str, str], dict[str, object]],
    dict[tuple[str, str], dict[str, object]],
    set[tuple[str, str]],
    set[tuple[str, str]],
    set[tuple[str, str]],
    set[tuple[str, str]],
]:
    if projected is None:
        projected = _project_artifact_publication(result, planned_result=planned_result)
    current_by_key = projected.current_by_key
    planned_by_key = projected.planned_by_key
    previous_by_key = {_ledger_key(row): row for row in previous_rows}
    full_scope = target_modules is None and target_collections is None and target_families is None
    selected_modules = target_modules or frozenset()
    selected_collections = target_collections or frozenset()
    selected_families = target_families or frozenset()
    selected_family_wide_families = set(family_wide_families or ())
    if family_wide:
        selected_family_wide_families.update(selected_families)
    current_path_index = _LedgerPathConflictIndex.from_keyed_rows(current_by_key)
    scoped_previous_keys = {
        key
        for key, row in previous_by_key.items()
        if full_scope
        or _ledger_row_in_scope(
            row,
            selected_modules=selected_modules,
            selected_collections=selected_collections,
            selected_families=selected_families,
            family_wide_families=selected_family_wide_families,
        )
    }
    structural_blockers = {
        previous_key
        for previous_key, previous_row in previous_by_key.items()
        if previous_key not in planned_by_key and current_path_index.conflicting_rows(previous_row)
    }
    explicit_predecessors = {
        (str(row["target_root"]), _portable_relative_path_identity(path))
        for row in current_by_key.values()
        for path in row.get("publication_replaces", ())
        if isinstance(path, str)
    }
    out_of_scope_structural_blockers = structural_blockers - scoped_previous_keys - explicit_predecessors
    if not full_scope and out_of_scope_structural_blockers:
        paths = ", ".join(f"{previous_by_key[key]['target_root']}:{previous_by_key[key]['path']}" for key in sorted(out_of_scope_structural_blockers))
        raise ValueError(
            "Targeted build cannot replace out-of-scope tracked artifacts with " f"a structural path conflict: {paths}. Run a family or full build."
        )
    reconciled_previous_keys = scoped_previous_keys | structural_blockers | explicit_predecessors.intersection(previous_by_key)
    stale_keys = reconciled_previous_keys - set(planned_by_key)
    return (
        current_by_key,
        planned_by_key,
        previous_by_key,
        reconciled_previous_keys,
        stale_keys,
        structural_blockers,
        explicit_predecessors.intersection(previous_by_key),
    )


def _planned_rows(
    result: BuildResult,
    *,
    current_result: BuildResult,
    current_by_key: Mapping[tuple[str, str], Mapping[str, object]],
) -> dict[tuple[str, str], dict[str, object]]:
    if result.artifacts == current_result.artifacts:
        return {key: dict(row) for key, row in current_by_key.items()}
    try:
        validated_rows = emitted_artifact_rows(result)
    except ValueError:
        # A targeted build may remain safe when an unrelated planned artifact
        # is invalid. Preserve the tolerant per-artifact fallback below only
        # for that exceptional case.
        pass
    else:
        return {_ledger_key(row): dict(row) for row in validated_rows}
    rows: dict[tuple[str, str], dict[str, object]] = {}
    current_path_index = _LedgerPathConflictIndex.from_keyed_rows(current_by_key)
    for artifact in result.artifacts:
        try:
            row = emitted_artifact_rows(replace(result, artifacts=(artifact,)))[0]
        except ValueError:
            continue
        key = _ledger_key(row)
        existing = rows.get(key)
        if existing is not None:
            if key in current_by_key:
                raise ValueError(f"Targeted artifact path conflicts with another planned artifact: {row['target_root']}:{row['path']}.")
            continue
        if current_path_index.conflicting_rows(row):
            raise ValueError(f"Targeted artifact path structurally conflicts with another planned artifact: {row['target_root']}:{row['path']}.")
        rows[key] = dict(row)
    return rows


def _delete_rows_with_pending_checkpoints(
    keys: Set[tuple[str, str]],
    *,
    result: BuildResult,
    project_root: Path,
    current_by_key: Mapping[tuple[str, str], Mapping[str, object]],
    previous_by_key: Mapping[tuple[str, str], Mapping[str, object]],
    renamed_keys: Set[tuple[str, str]],
    output_root: Path | AnchoredDirectory,
    build_root: Path | AnchoredDirectory,
    full_clean_owned: Mapping[str, bool],
    whole_project_baseline: bool,
    pending_by_key: dict[tuple[str, str], dict[str, object]] | None = None,
) -> None:
    """Delete post-write predecessors and durably checkpoint each path."""

    if pending_by_key is None:
        pending_rows = load_emitted_artifact_rows(
            build_root,
            project_id=result.project_id,
            project_root=project_root,
            output_root=output_root,
        )
        pending_by_key = {_ledger_key(row): dict(row) for row in pending_rows}
    for key in _ordered_removal_keys(keys, previous_by_key=previous_by_key):
        previous_row = previous_by_key[key]
        replacement = current_by_key.get(key) if key in renamed_keys else None
        if replacement is None or not _tracked_artifacts_are_same_entry(
            previous_row,
            replacement,
            output_root=output_root,
            build_root=build_root,
        ):
            _delete_tracked_artifact(
                (str(previous_row["target_root"]), str(previous_row["path"])),
                output_root=output_root,
                build_root=build_root,
                exact_spelling=key in renamed_keys,
            )
        pending_row = pending_by_key.get(key)
        if pending_row is not None and pending_row.get("path") == previous_row.get("path"):
            pending_by_key.pop(key)
        if key in renamed_keys:
            replacement = current_by_key.get(key)
            if replacement is None:
                raise AssertionError("Renamed publication predecessor has no confirmed replacement row.")
            pending_by_key[key] = dict(replacement)
        _write_emitted_artifact_rows(
            build_root,
            tuple(pending_by_key[pending_key] for pending_key in sorted(pending_by_key)),
            project_id=result.project_id,
            project_root=project_root,
            output_root=output_root,
            state="pending",
            full_clean_owned=full_clean_owned,
            whole_project_baseline=whole_project_baseline,
        )


def _ordered_removal_keys(
    keys: Set[tuple[str, str]],
    *,
    previous_by_key: Mapping[tuple[str, str], Mapping[str, object]],
) -> tuple[tuple[str, str], ...]:
    return tuple(
        sorted(
            keys,
            key=lambda item: (
                item[0],
                -len(PurePosixPath(str(previous_by_key[item]["path"])).parts),
                str(previous_by_key[item]["path"]),
            ),
        )
    )


def _validated_ledger_row(value: object, *, ledger_path: Path) -> dict[str, object]:
    if not isinstance(value, dict):
        raise ValueError(f"ParaDev emitted-artifact ledger row must be an object: {ledger_path}.")
    target_root = value.get("target_root")
    path = value.get("path")
    owner = value.get("owner")
    if target_root not in _TARGET_ROOTS:
        raise ValueError(f"ParaDev emitted-artifact ledger row has invalid target_root: {ledger_path}.")
    if not isinstance(path, str):
        raise ValueError(f"ParaDev emitted-artifact ledger row has invalid path: {ledger_path}.")
    clean_path = _relative_artifact_path(path)
    _validate_unreserved_build_path(target_root, clean_path, ledger_path=ledger_path)
    if not isinstance(owner, str) or not owner:
        raise ValueError(f"ParaDev emitted-artifact ledger row has invalid owner: {ledger_path}.")
    module_ids = _string_list(value.get("module_ids"), field="module_ids", ledger_path=ledger_path)
    collection_keys = _collection_key_list(value.get("collection_keys"), ledger_path=ledger_path)
    family = value.get("family")
    if family is not None and (not isinstance(family, str) or not family):
        raise ValueError(f"ParaDev emitted-artifact ledger row has invalid family: {ledger_path}.")
    publication_scope = value.get("publication_scope")
    if publication_scope is not None and publication_scope != "project":
        raise ValueError(f"ParaDev emitted-artifact ledger row has invalid publication_scope: {ledger_path}.")
    publication_replaces = value.get("publication_replaces")
    if publication_replaces is not None and publication_scope != "project":
        raise ValueError("ParaDev emitted-artifact ledger row publication_replaces requires " f"project publication scope: {ledger_path}.")
    replace_paths = (
        _string_list(
            publication_replaces,
            field="publication_replaces",
            ledger_path=ledger_path,
        )
        if publication_replaces is not None
        else ()
    )
    clean_replace_paths = tuple(sorted({_relative_artifact_path(replace_path) for replace_path in replace_paths}))
    for clean_replace_path in clean_replace_paths:
        _validate_unreserved_build_path(
            target_root,
            clean_replace_path,
            ledger_path=ledger_path,
        )
    row: dict[str, object] = {
        "target_root": target_root,
        "path": clean_path,
        "owner": owner,
        "module_ids": list(module_ids),
        "collection_keys": [list(key) for key in collection_keys],
    }
    if isinstance(family, str):
        row["family"] = family
    if publication_scope == "project":
        row["publication_scope"] = publication_scope
    if clean_replace_paths:
        row["publication_replaces"] = list(clean_replace_paths)
    pending_removal = value.get("pending_removal")
    if pending_removal is not None:
        if pending_removal is not True:
            raise ValueError(f"ParaDev emitted-artifact ledger row has invalid pending_removal: {ledger_path}.")
        row["pending_removal"] = True
    pending_replacement_path = value.get("pending_replacement_path")
    if pending_replacement_path is not None:
        clean_pending_path = _relative_artifact_path(pending_replacement_path)
        _validate_unreserved_build_path(target_root, clean_pending_path, ledger_path=ledger_path)
        if _portable_relative_path_identity(clean_pending_path) != _portable_relative_path_identity(clean_path):
            raise ValueError(f"ParaDev emitted-artifact ledger row has invalid pending replacement identity: {ledger_path}.")
        row["pending_replacement_path"] = clean_pending_path
    return row


def _relative_artifact_path(value: object) -> str:
    text = str(value).replace("\\", "/")
    path = PurePosixPath(text)
    if not text or text != path.as_posix() or path.is_absolute() or text == "." or any(part in {"", ".", ".."} for part in path.parts):
        raise ValueError(f"Artifact ledger path must be a normalized relative path: {value!r}.")
    for component in path.parts:
        portability_error = windows_portable_component_error(component)
        if portability_error is not None:
            raise ValueError(f"Artifact ledger path contains Windows-incompatible component " f"{component!r} ({portability_error}): {value!r}.")
    return text


def _validate_unreserved_build_path(
    target_root: object,
    path: str,
    *,
    ledger_path: Path | None = None,
) -> None:
    path_identity = _portable_relative_path_identity(path)
    marker_identity = _portable_relative_path_identity(PUBLICATION_ROOT_NAME)
    if path_identity == marker_identity or path_identity.startswith(f"{marker_identity}/"):
        location = f": {ledger_path}" if ledger_path is not None else "."
        raise ValueError(f"ParaDev emitted-artifact ledger cannot track its publication-root marker{location}")
    if target_root != "build":
        return
    ledger_identity = _portable_relative_path_identity(EMITTED_ARTIFACTS_NAME)
    if path_identity == ledger_identity or path_identity.startswith(f"{ledger_identity}/"):
        location = f": {ledger_path}" if ledger_path is not None else "."
        raise ValueError(f"ParaDev emitted-artifact ledger cannot track its own path namespace{location}")
    reserved_manifests = {_portable_relative_path_identity(name) for name in MANIFEST_SCHEMAS}
    if any(path_identity == reserved or path_identity.startswith(f"{reserved}/") for reserved in reserved_manifests):
        location = f": {ledger_path}" if ledger_path is not None else "."
        raise ValueError(f"ParaDev emitted-artifact ledger cannot track reserved manifest {path!r}{location}")


def _string_list(value: object, *, field: str, ledger_path: Path) -> tuple[str, ...]:
    if not isinstance(value, list) or not all(isinstance(item, str) and item for item in value):
        raise ValueError(f"ParaDev emitted-artifact ledger row has invalid {field}: {ledger_path}.")
    return tuple(sorted(set(value)))


def _collection_key_list(value: object, *, ledger_path: Path) -> tuple[tuple[str, str], ...]:
    if not isinstance(value, list):
        raise ValueError(f"ParaDev emitted-artifact ledger row has invalid collection_keys: {ledger_path}.")
    keys: list[tuple[str, str]] = []
    for item in value:
        if not isinstance(item, list) or len(item) != 2 or not all(isinstance(part, str) and part for part in item):
            raise ValueError(f"ParaDev emitted-artifact ledger row has invalid collection_keys: {ledger_path}.")
        keys.append((item[0], item[1]))
    return tuple(sorted(set(keys)))


def _ledger_key(row: Mapping[str, object]) -> tuple[str, str]:
    return str(row["target_root"]), _portable_relative_path_identity(str(row["path"]))


def _artifact_ledger_key(artifact: Artifact) -> tuple[str, str]:
    return artifact.target_root, _portable_relative_path_identity(_relative_artifact_path(artifact.path))


def _portable_relative_path_identity(path: str) -> str:
    return portable_path_identity(path)


def _strict_parent_identities(identity: str) -> tuple[str, ...]:
    parts = PurePosixPath(identity).parts
    return tuple("/".join(parts[:length]) for length in range(1, len(parts)))


def _validate_no_structural_path_collisions(
    rows: Mapping[tuple[str, str], Mapping[str, object]],
) -> None:
    terminal = "\0"
    tries: dict[str, dict[str, object]] = {}
    for (target_root, identity), row in sorted(rows.items()):
        node = tries.setdefault(target_root, {})
        for part in PurePosixPath(identity).parts:
            ancestor = node.get(terminal)
            if isinstance(ancestor, str):
                raise ValueError(f"Emitted artifact path {row['path']!r} is nested below file artifact {ancestor!r} " f"in {target_root}.")
            child = node.setdefault(part, {})
            if not isinstance(child, dict):
                raise AssertionError("Invalid emitted-artifact path trie node.")
            node = child
        descendants = [value for key, value in node.items() if key != terminal]
        if descendants:
            raise ValueError(f"Emitted artifact file path {row['path']!r} is an ancestor of another artifact " f"in {target_root}.")
        node[terminal] = str(row["path"])


def _ledger_row_in_scope(
    row: Mapping[str, object],
    *,
    selected_modules: Set[str],
    selected_collections: Set[tuple[str, str]],
    selected_families: Set[str],
    family_wide_families: Set[str],
) -> bool:
    if row.get("publication_scope") == "project":
        return True
    owner = row.get("owner")
    family = row.get("family")
    if isinstance(owner, str) and owner.startswith(("project:", "copy_root:")):
        return not isinstance(family, str) or family in selected_families
    if isinstance(family, str) and family in family_wide_families:
        return True
    has_granular_owner = False
    module_ids = row.get("module_ids")
    if isinstance(module_ids, list):
        granular_modules = {item for item in module_ids if isinstance(item, str)}
        has_granular_owner = has_granular_owner or bool(granular_modules)
        if selected_modules.intersection(granular_modules):
            return True
    collection_keys = row.get("collection_keys")
    if isinstance(collection_keys, list):
        keys = {
            (item[0], item[1])
            for item in collection_keys
            if isinstance(item, list) and len(item) == 2 and isinstance(item[0], str) and isinstance(item[1], str)
        }
        has_granular_owner = has_granular_owner or bool(keys)
        if selected_collections.intersection(keys):
            return True
    if has_granular_owner:
        return False
    if isinstance(family, str):
        return family in selected_families
    return False


def _delete_tracked_artifact(
    key: tuple[str, str],
    *,
    output_root: Path | AnchoredDirectory,
    build_root: Path | AnchoredDirectory,
    exact_spelling: bool = False,
) -> None:
    target_root, relative_path = key
    root = output_root if target_root == "output" else build_root
    if isinstance(root, AnchoredDirectory):
        root.delete_file(relative_path, exact_spelling=exact_spelling)
        return
    try:
        with open_anchored_directory(root, create=False) as publication_root:
            publication_root.delete_file(
                relative_path,
                exact_spelling=exact_spelling,
            )
    except FileNotFoundError:
        return


def _tracked_artifacts_are_same_entry(
    previous: Mapping[str, object],
    replacement: Mapping[str, object],
    *,
    output_root: Path | AnchoredDirectory,
    build_root: Path | AnchoredDirectory,
) -> bool:
    """Return whether a renamed predecessor aliases its published replacement."""

    target_root = str(previous["target_root"])
    if target_root != replacement.get("target_root"):
        return False
    root = output_root if target_root == "output" else build_root
    previous_path = str(previous["path"])
    replacement_path = str(replacement["path"])
    if isinstance(root, AnchoredDirectory):
        return root.same_entry(previous_path, replacement_path)
    try:
        with open_anchored_directory(root, create=False) as publication_root:
            return publication_root.same_entry(
                previous_path,
                replacement_path,
            )
    except FileNotFoundError:
        return False


def _publication_root_records(
    *,
    output_root: Path | AnchoredDirectory,
    build_root: Path | AnchoredDirectory,
    full_clean_owned: Mapping[str, bool],
) -> dict[str, dict[str, object]]:
    return {
        root_name: _publication_root_record(
            root,
            full_clean_owned=bool(full_clean_owned.get(root_name, False)),
        )
        for root_name, root in (("build", build_root), ("output", output_root))
    }


def _publication_root_record(
    root: Path | AnchoredDirectory,
    *,
    full_clean_owned: bool,
) -> dict[str, object]:
    device, inode = _root_identity(root)
    return {
        "path": _publication_path_identity(_root_path(root)),
        "device": device,
        "inode": inode,
        "full_clean_owned": full_clean_owned,
    }


def _publication_path_identity(path: Path) -> str:
    resolved = path.resolve(strict=False)
    if os.name != "nt":
        return str(resolved)
    return os.path.normcase(str(resolved))


def _write_emitted_artifact_rows(
    build_root: Path | AnchoredDirectory,
    rows: Sequence[Mapping[str, object]],
    *,
    project_id: str,
    project_root: Path,
    output_root: Path | AnchoredDirectory,
    state: str,
    full_clean_owned: Mapping[str, bool],
    whole_project_baseline: bool,
) -> None:
    payload = {
        "schema": EMITTED_ARTIFACTS_SCHEMA,
        "state": state,
        "whole_project_baseline": whole_project_baseline,
        "identity": {
            "project_id": project_id,
            "project_root": _publication_path_identity(project_root),
            "roots": _publication_root_records(
                output_root=output_root,
                build_root=build_root,
                full_clean_owned=full_clean_owned,
            ),
        },
        "artifacts": [dict(row) for row in rows],
    }
    encoded = (json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")
    if isinstance(build_root, AnchoredDirectory):
        build_root.write_bytes(EMITTED_ARTIFACTS_NAME, encoded)
        return
    with open_anchored_directory(build_root) as publication_root:
        publication_root.write_bytes(EMITTED_ARTIFACTS_NAME, encoded)


def _root_path(root: Path | AnchoredDirectory) -> Path:
    return root.path if isinstance(root, AnchoredDirectory) else root


def _root_identity(root: Path | AnchoredDirectory) -> tuple[int, int]:
    if isinstance(root, AnchoredDirectory):
        return root.identity
    with open_anchored_directory(root) as publication_root:
        return publication_root.identity
