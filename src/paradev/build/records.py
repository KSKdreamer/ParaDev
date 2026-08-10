"""Generic build graph records."""

from __future__ import annotations

import heapq
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from pathlib import Path, PurePosixPath
from typing import Any

from .._api_table import append_index_entry
from ..portable_paths import portable_path_identity, windows_portable_component_error

ARTIFACT_TARGET_ROOTS = {"output", "build"}


@dataclass(frozen=True, slots=True)
class Module:
    """A discovered source module.

    Args:
        module_id: Stable module identifier.
        family: Registered module family identifier.
        root: Module source root.
        source_slots: Matched source slot paths by slot name.
        collection_id: Optional collection identifier.
        metadata: Plain metadata loaded from module sources.
    """

    module_id: str
    family: str
    root: str | Path
    source_slots: Mapping[str, Sequence[str | Path]] = field(default_factory=dict)
    collection_id: str | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)
    payload: Any = None

    def to_dict(self) -> dict[str, Any]:
        """Return a deterministic JSON-safe module view."""

        data: dict[str, Any] = {
            "module_id": self.module_id,
            "family": self.family,
            "root": _path_str(self.root),
            "source_slots": {key: [_path_str(path) for path in self.source_slots[key]] for key in sorted(self.source_slots)},
            "metadata": dict(self.metadata),
        }
        if self.collection_id:
            data["collection_id"] = self.collection_id
        return data


@dataclass(frozen=True, slots=True)
class Collection:
    """A build-time group of modules."""

    collection_id: str
    family: str
    module_ids: tuple[str, ...] = ()
    source_slots: Mapping[str, Sequence[str | Path]] = field(default_factory=dict)
    metadata: Mapping[str, Any] = field(default_factory=dict)
    payload: Any = None

    def to_dict(self) -> dict[str, Any]:
        """Return a deterministic JSON-safe collection view."""

        data: dict[str, Any] = {
            "collection_id": self.collection_id,
            "family": self.family,
            "module_ids": list(self.module_ids),
            "metadata": dict(self.metadata),
        }
        if self.source_slots:
            data["source_slots"] = {key: [_path_str(path) for path in self.source_slots[key]] for key in sorted(self.source_slots)}
        return data


@dataclass(frozen=True, slots=True)
class Dependency:
    """One dependency edge in the build graph."""

    source: str
    target: str
    kind: str
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Return a deterministic JSON-safe dependency view."""

        data: dict[str, Any] = {
            "source": self.source,
            "target": self.target,
            "kind": self.kind,
        }
        if self.metadata:
            data["metadata"] = dict(self.metadata)
        return data


@dataclass(frozen=True, slots=True)
class Artifact:
    """One planned or emitted output artifact.

    Args:
        path: Relative path under the artifact target root.
        artifact_type: Registered artifact writer identifier.
        owner: Owning module, collection, or project.
        inputs: Source files used to produce this artifact.
        mode: Planning or emission mode marker.
        target_root: Project root selector. `output` writes under mod output;
            `build` writes under the ParaDev build root.
        metadata: JSON-safe artifact metadata.
        payload: Writer-only payload omitted from JSON views.
    """

    path: str | Path
    artifact_type: str
    owner: str
    inputs: tuple[str | Path, ...] = ()
    mode: str = "plan"
    target_root: str = "output"
    metadata: Mapping[str, Any] = field(default_factory=dict)
    payload: Any = None

    def to_dict(self) -> dict[str, Any]:
        """Return a deterministic JSON-safe artifact view."""

        return {
            "path": _path_str(self.path),
            "type": self.artifact_type,
            "owner": self.owner,
            "inputs": [_path_str(path) for path in self.inputs],
            "mode": self.mode,
            "target_root": self.target_root,
            "metadata": dict(self.metadata),
        }


@dataclass(frozen=True, slots=True)
class Diagnostic:
    """A build diagnostic for source, module, collection, or artifact checks."""

    code: str
    message: str
    severity: str = "error"
    family: str | None = None
    module_id: str | None = None
    collection_id: str | None = None
    slot: str | None = None
    source_path: str | Path | None = None
    artifact_path: str | Path | None = None
    target_root: str | None = None
    span: Mapping[str, int] | None = None
    slots: Sequence[str] = ()
    owners: Sequence[str] = ()

    def to_dict(self) -> dict[str, Any]:
        """Return a deterministic JSON-safe diagnostic view."""

        data: dict[str, Any] = {
            "code": self.code,
            "message": self.message,
            "severity": self.severity,
        }
        if self.family:
            data["family"] = self.family
        if self.module_id:
            data["module_id"] = self.module_id
        if self.collection_id:
            data["collection_id"] = self.collection_id
        if self.slot:
            data["slot"] = self.slot
        if self.slots:
            data["slots"] = [str(slot) for slot in self.slots]
        if self.owners:
            data["owners"] = [str(owner) for owner in self.owners]
        if self.source_path is not None:
            data["source_path"] = _path_str(self.source_path)
        if self.artifact_path is not None:
            data["artifact_path"] = _path_str(self.artifact_path)
        if self.target_root:
            data["target_root"] = self.target_root
        if self.span is not None:
            data["span"] = dict(self.span)
        return data


@dataclass(frozen=True, slots=True)
class BuildResult:
    """Dry-run or emitted build result."""

    project_id: str
    modules: tuple[Module, ...] = ()
    collections: tuple[Collection, ...] = ()
    dependencies: tuple[Dependency, ...] = ()
    artifacts: tuple[Artifact, ...] = ()
    diagnostics: tuple[Diagnostic, ...] = ()
    dry_run: bool = True
    profile: str | None = None

    @classmethod
    def plan(
        cls,
        project_id: str,
        *,
        profile: str | None = None,
        modules: Sequence[Module] = (),
        collections: Sequence[Collection] = (),
        dependencies: Sequence[Dependency] = (),
        artifacts: Sequence[Artifact] = (),
        diagnostics: Sequence[Diagnostic] = (),
    ) -> "BuildResult":
        """Create a dry-run build result and validate generic artifact collisions."""

        planned_modules, order_diagnostics = _module_order(modules)
        planned_collections = module_collections(planned_modules, collections)
        planned_artifacts = tuple(artifacts)
        planned_dependencies = (*_module_dependencies(planned_modules), *tuple(dependencies))
        all_diagnostics = [
            *diagnostics,
            *_module_dependency_diagnostics(planned_modules, order_diagnostics=order_diagnostics),
            *_localization_duplicate_diagnostics(planned_modules, planned_collections),
            *_artifact_path_diagnostics(planned_artifacts),
            *_artifact_target_root_diagnostics(planned_artifacts),
            *_artifact_collision_diagnostics(planned_artifacts),
            *_artifact_input_diagnostics(planned_modules, planned_collections, planned_artifacts),
        ]
        return cls(
            project_id=project_id,
            profile=_optional_text(profile),
            modules=planned_modules,
            collections=planned_collections,
            dependencies=planned_dependencies,
            artifacts=planned_artifacts,
            diagnostics=tuple(all_diagnostics),
            dry_run=True,
        )

    @property
    def blocked(self) -> bool:
        """Return whether the result has blocking diagnostics."""

        return any(diagnostic.severity == "error" for diagnostic in self.diagnostics)

    def summary(self) -> dict[str, int | bool]:
        """Return a JSON-safe build summary."""

        error_count = sum(1 for diagnostic in self.diagnostics if diagnostic.severity == "error")
        return {
            "module_count": len(self.modules),
            "collection_count": len(self.collections),
            "dependency_count": len(self.dependencies),
            "artifact_count": len(self.artifacts),
            "diagnostic_count": len(self.diagnostics),
            "error_count": error_count,
            "blocked": error_count > 0,
        }

    def to_dict(self) -> dict[str, Any]:
        """Return a deterministic JSON-safe build result view."""

        data: dict[str, Any] = {
            "project_id": self.project_id,
            "dry_run": self.dry_run,
            "modules": [module.to_dict() for module in self.modules],
            "collections": [collection.to_dict() for collection in self.collections],
            "dependencies": [dependency.to_dict() for dependency in self.dependencies],
            "artifacts": [artifact.to_dict() for artifact in self.artifacts],
            "diagnostics": [diagnostic.to_dict() for diagnostic in self.diagnostics],
            "summary": self.summary(),
        }
        if self.profile:
            data["profile"] = self.profile
        return data


def _optional_text(value: object) -> str | None:
    if not isinstance(value, str):
        return None
    text = value.strip()
    return text or None


def _module_dependencies(modules: Sequence[Module]) -> tuple[Dependency, ...]:
    dependencies: list[Dependency] = []
    for module in modules:
        for kind in ("requires", "after"):
            targets = _dependency_targets(module.metadata.get(kind))
            if not targets:
                continue
            dependencies.extend(Dependency(source=f"module:{module.module_id}", target=target, kind=kind) for target in targets)
    return tuple(dependencies)


def order_modules(modules: Sequence[Module]) -> tuple[Module, ...]:
    """Return modules in deterministic build order from resolvable `after` edges."""

    ordered, _diagnostics = _module_order(modules)
    return ordered


def module_collections(modules: Sequence[Module], collections: Sequence[Collection] = ()) -> tuple[Collection, ...]:
    """Return explicit collections or derive deterministic collections from modules."""

    grouped: dict[tuple[str, str], list[Module]] = {}
    for module in modules:
        if module.collection_id:
            append_index_entry(grouped, (module.family, module.collection_id), module)
    merged: list[Collection] = []
    seen: set[tuple[str, str]] = set()
    seen_ids: set[str] = set()
    for collection in sorted(collections, key=lambda item: (item.family, item.collection_id)):
        key = (collection.family, collection.collection_id)
        group = grouped.get(key, [])
        module_ids = list(collection.module_ids)
        module_ids.extend(module.module_id for module in group if module.module_id not in module_ids)
        merged.append(
            Collection(
                collection_id=collection.collection_id,
                family=collection.family,
                module_ids=tuple(module_ids),
                source_slots=collection.source_slots,
                metadata=collection.metadata,
                payload=collection.payload,
            )
        )
        seen.add(key)
        seen_ids.add(collection.collection_id)
    for key, group in sorted(grouped.items()):
        family, collection_id = key
        if key in seen or collection_id in seen_ids:
            continue
        merged.append(
            Collection(
                collection_id=collection_id,
                family=family,
                module_ids=tuple(module.module_id for module in group),
            )
        )
    return tuple(merged)


def _dependency_targets(value: Any) -> tuple[str, ...]:
    if not isinstance(value, Sequence) or isinstance(value, str | bytes):
        return ()
    return tuple(target.strip() for target in value if isinstance(target, str) and target.strip())


def _module_order(modules: Sequence[Module]) -> tuple[tuple[Module, ...], tuple[Diagnostic, ...]]:
    module_map = {module.module_id: module for module in modules}
    module_ids = sorted(module_map)
    if not any(_dependency_targets(module_map[module_id].metadata.get("after")) for module_id in module_ids):
        return tuple(module_map[module_id] for module_id in module_ids), ()
    aliases = _module_aliases(module_map.values())
    edges: dict[str, set[str]] = {module_id: set() for module_id in module_ids}
    indegrees = {module_id: 0 for module_id in module_ids}

    for module_id in module_ids:
        module = module_map[module_id]
        for target in _dependency_targets(module.metadata.get("after")):
            before_id = aliases.get(target)
            if before_id is None:
                continue
            if module_id not in edges[before_id]:
                edges[before_id].add(module_id)
                indegrees[module_id] += 1

    queue = [module_id for module_id in module_ids if indegrees[module_id] == 0]
    heapq.heapify(queue)
    ordered_ids: list[str] = []
    while queue:
        module_id = heapq.heappop(queue)
        ordered_ids.append(module_id)
        for after_id in sorted(edges[module_id]):
            indegrees[after_id] -= 1
            if indegrees[after_id] == 0:
                heapq.heappush(queue, after_id)

    diagnostics: list[Diagnostic] = []
    if len(ordered_ids) != len(module_ids):
        ordered_set = set(ordered_ids)
        cycle_ids = [module_id for module_id in module_ids if module_id not in ordered_set]
        diagnostics.append(
            Diagnostic(
                code="build.dependency_cycle",
                message=f"Module after dependencies contain a cycle: {', '.join(cycle_ids)}.",
                severity="error",
                module_id=cycle_ids[0],
                source_path="meta.yaml",
            )
        )
        ordered_ids.extend(cycle_ids)
    return tuple(module_map[module_id] for module_id in ordered_ids), tuple(diagnostics)


def _module_aliases(modules: Sequence[Module]) -> dict[str, str]:
    aliases: dict[str, str] = {}
    for module in modules:
        for alias in _module_symbol_aliases(module):
            aliases.setdefault(alias, module.module_id)
    return aliases


def _module_symbol_aliases(module: Module) -> tuple[str, ...]:
    object_id = _metadata_text(module.metadata, "object_id") or module.module_id.rsplit("/", 1)[-1]
    aliases = {
        module.module_id,
        f"module:{module.module_id}",
        f"{module.family}:{object_id}",
        f"{module.family}/{object_id}",
    }
    game_id = _metadata_text(module.metadata, "game_id")
    if game_id:
        aliases.add(game_id)
        aliases.add(f"{module.family}:{game_id}")
        aliases.add(f"{module.family}/{game_id}")
    return tuple(sorted(aliases))


def _metadata_text(metadata: Mapping[str, Any], key: str) -> str | None:
    value = metadata.get(key)
    if isinstance(value, str) and value.strip():
        return value.strip()
    return None


def _module_dependency_diagnostics(
    modules: Sequence[Module],
    *,
    order_diagnostics: Sequence[Diagnostic] | None = None,
) -> list[Diagnostic]:
    diagnostics = list(_module_order(modules)[1] if order_diagnostics is None else order_diagnostics)
    aliases = _module_aliases(modules)
    for module in modules:
        for field_name in ("requires", "after"):
            targets = module.metadata.get(field_name)
            if targets is None:
                continue
            if not isinstance(targets, Sequence) or isinstance(targets, str | bytes):
                diagnostics.append(
                    Diagnostic(
                        code="build.invalid_dependency_metadata",
                        message=f"Module {module.module_id} metadata field {field_name!r} must be a list of dependency targets.",
                        severity="error",
                        module_id=module.module_id,
                        source_path="meta.yaml",
                    )
                )
                continue
            invalid = [target for target in targets if not isinstance(target, str) or not target.strip()]
            if invalid:
                diagnostics.append(
                    Diagnostic(
                        code="build.invalid_dependency_metadata",
                        message=f"Module {module.module_id} metadata field {field_name!r} entries must be dependency target strings.",
                        severity="error",
                        module_id=module.module_id,
                        source_path="meta.yaml",
                    )
                )
            for target in _dependency_targets(targets):
                if _project_local_target(target) and target not in aliases:
                    diagnostics.append(
                        Diagnostic(
                            code="build.missing_dependency_target",
                            message=f"Module {module.module_id} dependency {target!r} from metadata field {field_name!r} does not resolve to a project module.",
                            severity="error",
                            module_id=module.module_id,
                            source_path="meta.yaml",
                        )
                    )
    return diagnostics


def _project_local_target(target: str) -> bool:
    return target.startswith("module:") or ("/" in target and ":" not in target)


def _localization_duplicate_diagnostics(modules: Sequence[Module], collections: Sequence[Collection]) -> list[Diagnostic]:
    seen: dict[tuple[str, str], tuple[str, Any, str, str | None]] = {}
    diagnostics: list[Diagnostic] = []
    for owner_id, entry, source_path, slot, module_id in _localization_entries(modules, collections):
        duplicate_key = (entry.language, entry.key)
        previous = seen.get(duplicate_key)
        if previous is None:
            seen[duplicate_key] = (owner_id, entry, source_path, slot)
            continue
        previous_owner_id, _previous_entry, previous_source_path, _previous_slot = previous
        if previous_owner_id == owner_id:
            continue
        diagnostics.append(
            Diagnostic(
                code="loc.project_duplicate_key",
                message=(
                    f"Localization key {entry.key!r} for {entry.language!r} is declared by "
                    f"{previous_owner_id} {previous_source_path} and {owner_id} {source_path}."
                ),
                severity="error",
                module_id=module_id,
                slot=slot,
                source_path=source_path,
            )
        )
    return diagnostics


def _localization_entries(modules: Sequence[Module], collections: Sequence[Collection]) -> tuple[tuple[str, Any, str, str | None, str | None], ...]:
    from .loaders import CollectionSourceBundle, ModuleSourceBundle

    rows = [
        (module.module_id, entry, _path_str(entry.source_path), _module_source_slot(module, entry.source_path), module.module_id)
        for module in modules
        if isinstance(module.payload, ModuleSourceBundle)
        for entry in module.payload.loc_entries
    ]
    rows.extend(
        (
            f"collection:{collection.collection_id}",
            entry,
            _path_str(entry.source_path),
            _collection_source_slot(collection, entry.source_path),
            None,
        )
        for collection in collections
        if isinstance(collection.payload, CollectionSourceBundle)
        for entry in collection.payload.loc_entries
    )
    return tuple(sorted(rows, key=lambda row: (row[0], row[1].language, row[1].key, row[2], row[1].text)))


def _artifact_collision_diagnostics(artifacts: Sequence[Artifact]) -> list[Diagnostic]:
    seen: dict[tuple[str, str], Artifact] = {}
    portable_seen: dict[tuple[str, str], Artifact] = {}
    diagnostics: list[Diagnostic] = []
    for artifact in artifacts:
        path = _path_str(artifact.path)
        target_root = artifact.target_root
        previous = seen.get((target_root, path))
        if previous is not None:
            diagnostics.append(
                Diagnostic(
                    code="build.artifact_path_collision",
                    message=f"Artifact path {path} under {target_root} root is produced by {previous.owner} and {artifact.owner}.",
                    severity="error",
                    artifact_path=path,
                    target_root=target_root,
                    owners=(previous.owner, artifact.owner),
                )
            )
            continue

        seen[(target_root, path)] = artifact
        portable_key = (target_root, _portable_artifact_path(path))
        previous = portable_seen.get(portable_key)
        if previous is None:
            portable_seen[portable_key] = artifact
            continue
        previous_path = _path_str(previous.path)
        diagnostics.append(
            Diagnostic(
                code="build.artifact_path_collision",
                message=(
                    f"Artifact paths {previous_path!r} from {previous.owner} and {path!r} from {artifact.owner} under {target_root} root "
                    "collide after Unicode NFC normalization and case folding."
                ),
                severity="error",
                artifact_path=path,
                target_root=target_root,
                owners=(previous.owner, artifact.owner),
            )
        )
    diagnostics.extend(_artifact_structural_collision_diagnostics(artifacts))
    return diagnostics


def _artifact_structural_collision_diagnostics(artifacts: Sequence[Artifact]) -> list[Diagnostic]:
    artifacts_by_path: dict[tuple[str, tuple[str, ...]], Artifact] = {}
    for artifact in artifacts:
        path = PurePosixPath(_path_str(artifact.path))
        if path.is_absolute() or ".." in path.parts:
            continue
        portable_parts = tuple(portable_path_identity(part) for part in path.parts)
        artifacts_by_path.setdefault((artifact.target_root, portable_parts), artifact)

    diagnostics: list[Diagnostic] = []
    for (target_root, parts), artifact in sorted(artifacts_by_path.items()):
        for length in range(len(parts) - 1, -1, -1):
            ancestor = artifacts_by_path.get((target_root, parts[:length]))
            if ancestor is None:
                continue
            ancestor_path = _path_str(ancestor.path)
            artifact_path = _path_str(artifact.path)
            diagnostics.append(
                Diagnostic(
                    code="build.artifact_path_collision",
                    message=(
                        f"Artifact path {ancestor_path!r} from {ancestor.owner} is a file ancestor of "
                        f"{artifact_path!r} from {artifact.owner} under {target_root} root."
                    ),
                    severity="error",
                    artifact_path=artifact_path,
                    target_root=target_root,
                    owners=(ancestor.owner, artifact.owner),
                )
            )
            break
    return diagnostics


def _portable_artifact_path(path: str) -> str:
    return portable_path_identity(path)


def _artifact_target_root_diagnostics(artifacts: Sequence[Artifact]) -> list[Diagnostic]:
    diagnostics: list[Diagnostic] = []
    for artifact in artifacts:
        if artifact.target_root in ARTIFACT_TARGET_ROOTS:
            continue
        diagnostics.append(
            Diagnostic(
                code="build.invalid_artifact_target_root",
                message=f"Artifact {artifact.path} target root {artifact.target_root!r} must be one of: build, output.",
                severity="error",
                artifact_path=artifact.path,
                target_root=artifact.target_root,
            )
        )
    return diagnostics


def _artifact_path_diagnostics(artifacts: Sequence[Artifact]) -> list[Diagnostic]:
    diagnostics: list[Diagnostic] = []
    for artifact in artifacts:
        path = _path_str(artifact.path)
        artifact_path = PurePosixPath(path)
        if artifact_path.is_absolute() or ".." in artifact_path.parts:
            diagnostics.append(
                Diagnostic(
                    code="build.invalid_artifact_path",
                    message=f"Artifact path {path} must be relative and stay under its target root.",
                    severity="error",
                    artifact_path=path,
                    target_root=artifact.target_root,
                )
            )
            continue
        for component in artifact_path.parts:
            portability_error = windows_portable_component_error(component)
            if portability_error is None:
                continue
            diagnostics.append(
                Diagnostic(
                    code="build.invalid_artifact_path",
                    message=(f"Artifact path {path} is not portable to Windows because component " f"{component!r} {portability_error}."),
                    severity="error",
                    artifact_path=path,
                    target_root=artifact.target_root,
                )
            )
            break
    return diagnostics


def _artifact_input_diagnostics(
    modules: Sequence[Module],
    collections: Sequence[Collection],
    artifacts: Sequence[Artifact],
) -> list[Diagnostic]:
    known_inputs = {*_module_source_paths(modules), *_collection_source_paths(collections)}
    if not known_inputs:
        return []

    diagnostics: list[Diagnostic] = []
    for artifact in artifacts:
        artifact_path = _path_str(artifact.path)
        for input_path in artifact.inputs:
            source_path = _path_str(input_path)
            if source_path in known_inputs:
                continue
            diagnostics.append(
                Diagnostic(
                    code="build.untracked_artifact_input",
                    message=f"Artifact {artifact_path} input {source_path} does not match any discovered module source slot.",
                    severity="warning",
                    source_path=source_path,
                    artifact_path=artifact_path,
                    target_root=artifact.target_root,
                )
            )
    return diagnostics


def _module_source_paths(modules: Sequence[Module]) -> set[str]:
    paths: set[str] = set()
    for module in modules:
        root = Path(module.root)
        for slot_paths in module.source_slots.values():
            for source_path in slot_paths:
                paths.add(_path_str(root / source_path))
    return paths


def _collection_source_paths(collections: Sequence[Collection]) -> set[str]:
    paths: set[str] = set()
    for collection in collections:
        payload = getattr(collection, "payload", None)
        root = Path(str(getattr(payload, "root", "")))
        for source in getattr(payload, "pdx_sources", ()):
            paths.add(_path_str(root / source.path))
        for entry in getattr(payload, "loc_entries", ()):
            paths.add(_path_str(root / entry.source_path))
        for source in getattr(payload, "copy_sources", ()):
            paths.add(_path_str(root / source.path))
    return paths


def _module_source_slot(module: Module, source_path: str | Path) -> str | None:
    normalized = _path_str(source_path)
    for slot in sorted(module.source_slots):
        for path in module.source_slots[slot]:
            if normalized == _path_str(path):
                return slot
    return None


def _collection_source_slot(collection: Collection, source_path: str | Path) -> str | None:
    from .loaders import CollectionSourceBundle

    payload = collection.payload
    if not isinstance(payload, CollectionSourceBundle):
        return None
    normalized = _path_str(source_path)
    for slot in sorted(payload.source_slots):
        for path in payload.source_slots[slot]:
            if normalized == _path_str(path):
                return slot
    return None


def _path_str(path: str | Path) -> str:
    return str(path).replace("\\", "/")
