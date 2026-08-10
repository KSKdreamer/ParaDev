"""Dry-run build planning helpers."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field, replace
from typing import Any

from .progress import BuildProgressCallback, emit_progress, scaled_percent
from .records import Artifact, BuildResult, Collection, Diagnostic, Module, module_collections, order_modules
from .registry import BuildRegistry


@dataclass(frozen=True, slots=True)
class BuildContext:
    """Context passed to registered build families."""

    project_id: str
    dry_run: bool = True
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class FamilyNormalizeResult:
    """Family-owned normalized modules plus diagnostics."""

    modules: tuple[Module, ...]
    diagnostics: tuple[Diagnostic, ...] = ()


@dataclass(frozen=True, slots=True)
class FamilyCompileResult:
    """Family-owned diagnostics and artifacts from one compile hook.

    Args:
        artifacts: Planned artifacts emitted by the family.
        diagnostics: Validation or compilation diagnostics owned by the family.
    """

    artifacts: tuple[Artifact, ...] = ()
    diagnostics: tuple[Diagnostic, ...] = ()


@dataclass(frozen=True, slots=True)
class _BuildPlanDraft:
    """Family-planned artifacts before whole-plan transforms and validation."""

    context: BuildContext
    profile: str | None
    modules: tuple[Module, ...]
    collections: tuple[Collection, ...]
    artifacts: tuple[Artifact, ...]
    diagnostics: tuple[Diagnostic, ...]


def plan_build(
    project_id: str,
    registry: BuildRegistry,
    *,
    profile: str | None = None,
    metadata: Mapping[str, Any] | None = None,
    modules: Sequence[Module] = (),
    collections: Sequence[Collection] = (),
    diagnostics: Sequence[Diagnostic] = (),
    parallelism: int = 1,
    progress: BuildProgressCallback | None = None,
) -> BuildResult:
    """Run registered families and return a dry-run build result.

    Args:
        project_id: Stable project identifier.
        registry: Build registry with families and optional writers.
        profile: Optional build profile identifier for result and manifest provenance.
        metadata: Optional project-level context for profile-owned artifacts.
        modules: Discovered modules.
        collections: Discovered collections.
        diagnostics: Existing diagnostics to carry into the result.
        parallelism: Maximum family compile or check/emit workers. Normalization
            remains sequential.
        progress: Optional callback for JSON-safe build progress events.

    Returns:
        Dry-run build result with planned artifacts and generic diagnostics.
    """

    draft = _plan_build_draft(
        project_id,
        registry,
        profile=profile,
        metadata=metadata,
        modules=modules,
        collections=collections,
        diagnostics=diagnostics,
        parallelism=parallelism,
        progress=progress,
    )
    return _finalize_build_draft(draft, registry, progress=progress)


def _plan_build_draft(
    project_id: str,
    registry: BuildRegistry,
    *,
    profile: str | None = None,
    metadata: Mapping[str, Any] | None = None,
    modules: Sequence[Module] = (),
    collections: Sequence[Collection] = (),
    diagnostics: Sequence[Diagnostic] = (),
    parallelism: int = 1,
    progress: BuildProgressCallback | None = None,
) -> _BuildPlanDraft:
    """Run family planning hooks without whole-plan transforms or validation."""

    ctx = BuildContext(project_id=project_id, dry_run=True, metadata=dict(metadata or {}))
    inactive_module_ids = {module.module_id for module in modules if module.metadata.get("inactive") is True}
    active_modules = tuple(module for module in modules if module.module_id not in inactive_module_ids)
    planned_diagnostics: list[Diagnostic] = [diagnostic for diagnostic in diagnostics if diagnostic.module_id not in inactive_module_ids]
    normalized_by_id = {module.module_id: module for module in active_modules}
    failed_families: set[str] = set()
    initial_collections = module_collections(order_modules(active_modules), collections)
    for family in registry.families:
        family_name = str(getattr(family, "family", "<unknown>"))
        family_modules = tuple(module for module in normalized_by_id.values() if module.family == family_name)
        if not family_modules:
            continue
        normalize = getattr(family, "normalize", None)
        if not callable(normalize):
            continue
        try:
            normalized = normalize(ctx, family_modules, initial_collections)
            if normalized is None:
                normalized = family_modules
            result = _coerce_normalize_result(normalized, family_name)
            _replace_family_modules(normalized_by_id, family_modules, result, family_name)
        except Exception as error:
            planned_diagnostics.append(_family_hook_diagnostic(family_name, "normalize", error))
            failed_families.add(family_name)
            continue
        planned_diagnostics.extend(result.diagnostics)

    artifacts: list[Artifact] = []
    module_tuple = order_modules(tuple(normalized_by_id.values()))
    collection_tuple = module_collections(module_tuple, collections)
    emit_progress(
        progress,
        "collection_compile",
        counts={"collections": len(collection_tuple), "modules": len(module_tuple)},
        detail=f"{len(collection_tuple)} collections assembled from {len(module_tuple)} modules.",
        label="Compiling collections",
        percent=36,
        total=len(collection_tuple),
    )
    families_with_modules = tuple(
        family for family in registry.families if tuple(module for module in module_tuple if module.family == str(getattr(family, "family", "<unknown>")))
    )
    family_total = len(families_with_modules)
    family_index = 0
    family_jobs: list[tuple[Any, str, tuple[Module, ...]]] = []
    for family in registry.families:
        family_name = str(getattr(family, "family", "<unknown>"))
        if family_name in failed_families:
            continue
        family_modules = tuple(module for module in module_tuple if module.family == family_name)
        if family_modules:
            family_index += 1
            emit_progress(
                progress,
                "entity_compile",
                counts={"modules": len(family_modules)},
                current=family_name,
                detail=f"{family_name}: {len(family_modules)} modules.",
                index=family_index,
                label="Compiling entities",
                percent=scaled_percent(40, 72, family_index, family_total),
                total=family_total,
            )
        family_jobs.append((family, family_name, family_modules))
    for result in _run_family_jobs(ctx, family_jobs, collection_tuple, parallelism=parallelism):
        planned_diagnostics.extend(result.diagnostics)
        artifacts.extend(result.artifacts)
    return _BuildPlanDraft(
        context=ctx,
        profile=profile,
        modules=module_tuple,
        collections=collection_tuple,
        artifacts=tuple(artifacts),
        diagnostics=tuple(planned_diagnostics),
    )


def _finalize_build_draft(
    draft: _BuildPlanDraft,
    registry: BuildRegistry,
    *,
    artifacts: Sequence[Artifact] | None = None,
    trailing_diagnostics: Sequence[Diagnostic] = (),
    progress: BuildProgressCallback | None = None,
) -> BuildResult:
    """Transform and validate one complete artifact plan."""

    artifact_plan = draft.artifacts if artifacts is None else tuple(artifacts)
    artifact_tuple, postprocess_diagnostics = _run_artifact_postprocessors(
        draft.context,
        registry,
        artifact_plan,
    )
    planned_diagnostics = (
        *draft.diagnostics,
        *postprocess_diagnostics,
        *_artifact_writer_diagnostics(artifact_tuple, registry),
    )
    emit_progress(
        progress,
        "artifact_generation",
        counts={"artifacts": len(artifact_tuple)},
        detail=f"{len(artifact_tuple)} artifacts planned.",
        label="Planning artifacts",
        percent=74,
        total=len(artifact_tuple),
    )
    result = BuildResult.plan(
        project_id=draft.context.project_id,
        profile=draft.profile,
        modules=draft.modules,
        collections=draft.collections,
        artifacts=artifact_tuple,
        diagnostics=planned_diagnostics,
    )
    if not trailing_diagnostics:
        return result
    return replace(result, diagnostics=(*result.diagnostics, *trailing_diagnostics))


def _run_family_jobs(
    ctx: BuildContext,
    family_jobs: Sequence[tuple[Any, str, tuple[Module, ...]]],
    collections: tuple[Collection, ...],
    *,
    parallelism: int,
) -> tuple[FamilyCompileResult, ...]:
    workers = max(1, int(parallelism))
    if workers == 1 or len(family_jobs) <= 1:
        return tuple(_run_family_job(ctx, family, family_name, family_modules, collections) for family, family_name, family_modules in family_jobs)
    with ThreadPoolExecutor(max_workers=min(workers, len(family_jobs))) as executor:
        futures = [
            executor.submit(_run_family_job, ctx, family, family_name, family_modules, collections) for family, family_name, family_modules in family_jobs
        ]
        return tuple(future.result() for future in futures)


def _run_family_job(
    ctx: BuildContext,
    family: Any,
    family_name: str,
    family_modules: tuple[Module, ...],
    collections: tuple[Collection, ...],
) -> FamilyCompileResult:
    compile_family = getattr(family, "compile", None)
    if callable(compile_family):
        try:
            return _coerce_compile_result(
                compile_family(ctx, family_modules, collections),
                family_name,
            )
        except Exception as error:
            return FamilyCompileResult(diagnostics=(_family_hook_diagnostic(family_name, "compile", error),))
    diagnostics: list[Diagnostic] = []
    check = getattr(family, "check", None)
    if callable(check):
        try:
            checked = check(ctx, family_modules, collections) or ()
            diagnostics.extend(_coerce_diagnostics(checked, family_name))
        except Exception as error:
            return FamilyCompileResult(diagnostics=(_family_hook_diagnostic(family_name, "check", error),))
    emit = getattr(family, "emit", None)
    if not callable(emit):
        error = ValueError(f"Build family {family_name!r} must define emit(ctx, modules, collections).")
        return FamilyCompileResult(diagnostics=(_family_hook_diagnostic(family_name, "emit", error),))
    try:
        emitted = emit(ctx, family_modules, collections) or ()
        return FamilyCompileResult(
            artifacts=_coerce_artifacts(emitted, family_name),
            diagnostics=tuple(diagnostics),
        )
    except Exception as error:
        diagnostics.append(_family_hook_diagnostic(family_name, "emit", error))
        return FamilyCompileResult(diagnostics=tuple(diagnostics))


def _coerce_compile_result(
    value: object,
    family: str,
) -> FamilyCompileResult:
    """Validate one combined family compile result."""

    if not isinstance(value, FamilyCompileResult):
        raise ValueError(f"Build family {family!r} compile must return FamilyCompileResult.")
    return FamilyCompileResult(
        artifacts=_coerce_artifacts(value.artifacts, family),
        diagnostics=_coerce_diagnostics(value.diagnostics, family),
    )


def _coerce_normalize_result(value: object, family: str) -> FamilyNormalizeResult:
    if isinstance(value, FamilyNormalizeResult):
        modules = value.modules
        diagnostics = _coerce_diagnostics(value.diagnostics, family)
    else:
        try:
            modules = tuple(value)  # type: ignore[arg-type]
        except TypeError as error:
            raise ValueError(f"Build family {family!r} normalize returned a non-sequence value: {value!r}.") from error
        diagnostics = ()
    for module in modules:
        if not isinstance(module, Module):
            raise ValueError(f"Build family {family!r} normalized a non-Module value: {module!r}.")
    return FamilyNormalizeResult(modules=modules, diagnostics=diagnostics)


def _replace_family_modules(
    modules_by_id: dict[str, Module],
    original: Sequence[Module],
    result: FamilyNormalizeResult,
    family: str,
) -> None:
    expected = {module.module_id for module in original}
    actual = {module.module_id for module in result.modules}
    if actual != expected:
        raise ValueError(f"Build family {family!r} normalize must return the same module ids.")
    for module in result.modules:
        if module.family != family:
            raise ValueError(f"Build family {family!r} normalize changed module {module.module_id!r} to family {module.family!r}.")
        modules_by_id[module.module_id] = module


def _coerce_artifacts(value: Sequence[Artifact], family: str) -> tuple[Artifact, ...]:
    artifacts: list[Artifact] = []
    for artifact in value:
        if not isinstance(artifact, Artifact):
            raise ValueError(f"Build family {family!r} emitted a non-Artifact value: {artifact!r}.")
        if artifact.owner.startswith("collection:"):
            metadata = dict(artifact.metadata)
            metadata.setdefault("family", family)
            metadata.setdefault("collection_id", artifact.owner.removeprefix("collection:"))
            artifact = replace(artifact, metadata=metadata)
        artifacts.append(artifact)
    return tuple(artifacts)


def _run_artifact_postprocessors(
    ctx: BuildContext,
    registry: BuildRegistry,
    artifacts: tuple[Artifact, ...],
) -> tuple[tuple[Artifact, ...], tuple[Diagnostic, ...]]:
    """Apply registered whole-plan artifact transforms in registry order."""

    current = artifacts
    for postprocessor in registry.postprocessors:
        postprocessor_id = str(getattr(postprocessor, "postprocessor_id", "<unknown>"))
        process = getattr(postprocessor, "process")
        try:
            processed = process(ctx, current)
            current = _coerce_postprocessed_artifacts(processed, postprocessor_id)
        except Exception as error:
            message = str(error).rstrip(".")
            diagnostic = Diagnostic(
                code="build.postprocessor_failed",
                message=(f"Build postprocessor {postprocessor_id!r} failed: " f"{type(error).__name__}: {message}."),
                severity="error",
            )
            return current, (diagnostic,)
    return current, ()


def _coerce_postprocessed_artifacts(
    value: object,
    postprocessor_id: str,
) -> tuple[Artifact, ...]:
    try:
        artifacts = tuple(value)  # type: ignore[arg-type]
    except TypeError as error:
        raise ValueError(f"Build postprocessor {postprocessor_id!r} returned a non-sequence value: {value!r}.") from error
    for artifact in artifacts:
        if not isinstance(artifact, Artifact):
            raise ValueError(f"Build postprocessor {postprocessor_id!r} returned a non-Artifact value: {artifact!r}.")
    return artifacts


def _coerce_diagnostics(value: Sequence[Diagnostic], family: str) -> tuple[Diagnostic, ...]:
    diagnostics: list[Diagnostic] = []
    for diagnostic in value:
        if not isinstance(diagnostic, Diagnostic):
            raise ValueError(f"Build family {family!r} emitted a non-Diagnostic value: {diagnostic!r}.")
        diagnostics.append(diagnostic if diagnostic.family is not None else replace(diagnostic, family=family))
    return tuple(diagnostics)


def _family_hook_diagnostic(family: str, hook: str, error: Exception) -> Diagnostic:
    message = str(error).rstrip(".")
    return Diagnostic(
        code=f"family.{hook}_failed",
        message=f"Build family {family!r} {hook} failed: {type(error).__name__}: {message}.",
        severity="error",
        family=family,
    )


def _artifact_writer_diagnostics(artifacts: Sequence[Artifact], registry: BuildRegistry) -> tuple[Diagnostic, ...]:
    writer_types = {str(getattr(writer, "artifact_type")) for writer in registry.writers}
    if not writer_types:
        return ()
    diagnostics: list[Diagnostic] = []
    seen: set[tuple[str, str]] = set()
    for artifact in sorted(artifacts, key=lambda item: (item.artifact_type, item.target_root, str(item.path))):
        key = (artifact.artifact_type, artifact.target_root)
        if artifact.artifact_type in writer_types or key in seen:
            continue
        seen.add(key)
        diagnostics.append(
            Diagnostic(
                code="build.missing_artifact_writer",
                message=f"Artifact type {artifact.artifact_type!r} is planned but no artifact writer is registered.",
                severity="error",
                artifact_path=artifact.path,
                target_root=artifact.target_root,
            )
        )
    return tuple(diagnostics)
