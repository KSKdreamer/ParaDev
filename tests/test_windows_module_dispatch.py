"""Platform-neutral contracts for Windows module-authoring dispatch."""

from __future__ import annotations

from pathlib import Path

import pytest

from paradev.sdk import Project
from paradev.sdk import project as project_sdk
from paradev.sdk import templates as templates_sdk


@pytest.mark.unit
def test_single_scaffold_dispatches_to_retained_win32_adapter(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[dict[str, object]] = []

    def fake_write(**kwargs: object) -> None:
        calls.append(dict(kwargs))

    rendered = [
        {
            "relative_module_path": "def.txt",
            "content": "SAFE = {}\n",
        }
    ]
    monkeypatch.setattr(templates_sdk, "_uses_win32_scaffold_authority", lambda: True)
    monkeypatch.setattr(templates_sdk, "_write_scaffold_files_win32", fake_write)

    templates_sdk._write_scaffold_files_anchored(
        project_root=tmp_path,
        source_root=tmp_path / "src",
        family="idea",
        object_id="SAFE",
        folder_name="SAFE - Safe",
        rendered_files=rendered,
        force=False,
    )

    assert calls == [
        {
            "project_root": tmp_path,
            "source_root": tmp_path / "src",
            "family": "idea",
            "object_id": "SAFE",
            "folder_name": "SAFE - Safe",
            "rendered_files": rendered,
            "force": False,
        }
    ]


@pytest.mark.unit
def test_batch_scaffold_dispatches_to_retained_win32_adapter(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[dict[str, object]] = []

    def fake_write(**kwargs: object) -> None:
        calls.append(dict(kwargs))

    scaffolds = [
        (
            "idea",
            "SAFE",
            "SAFE",
            [{"relative_module_path": "def.txt", "content": "SAFE = {}\n"}],
        )
    ]
    monkeypatch.setattr(templates_sdk, "_uses_win32_scaffold_authority", lambda: True)
    monkeypatch.setattr(templates_sdk, "_write_scaffold_batch_win32", fake_write)

    templates_sdk._write_scaffold_batch_anchored(
        project_root=tmp_path,
        source_root=tmp_path / "src",
        scaffolds=scaffolds,
    )

    assert calls == [
        {
            "project_root": tmp_path,
            "source_root": tmp_path / "src",
            "scaffolds": scaffolds,
            "validate": None,
        }
    ]


@pytest.mark.unit
def test_module_folder_mutations_dispatch_to_retained_win32_adapter(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[tuple[str, dict[str, object]]] = []
    quarantine = project_sdk._ModuleRemovalQuarantine(
        name="idea-SAFE-transaction",
        path=tmp_path / "src/.paradev/module-trash/idea-SAFE-transaction",
    )

    def fake_rename(source_root: Path, **kwargs: object) -> None:
        calls.append(("rename", {"source_root": source_root, **kwargs}))

    def fake_remove(source_root: Path, **kwargs: object) -> project_sdk._ModuleRemovalQuarantine:
        calls.append(("remove", {"source_root": source_root, **kwargs}))
        return quarantine

    def fake_cleanup(
        source_root: Path,
        selected: project_sdk._ModuleRemovalQuarantine,
    ) -> project_sdk._ModuleRemovalCleanup:
        calls.append(("cleanup", {"source_root": source_root, "quarantine": selected}))
        return project_sdk._ModuleRemovalCleanup()

    monkeypatch.setattr(project_sdk, "_uses_win32_module_mutation_authority", lambda: True)
    monkeypatch.setattr(project_sdk, "_rename_module_directory_win32", fake_rename)
    monkeypatch.setattr(project_sdk, "_remove_module_directory_win32", fake_remove)
    monkeypatch.setattr(project_sdk, "_cleanup_module_quarantine_win32", fake_cleanup)

    source_root = tmp_path / "src"
    project_sdk._rename_module_directory(
        source_root,
        family="idea",
        source_name="SAFE",
        target_name="SAFER",
        target_object_id="SAFER",
    )
    selected = project_sdk._remove_module_directory(
        source_root,
        family="idea",
        module_name="SAFER",
    )
    cleanup = project_sdk._cleanup_module_quarantine(source_root, selected)

    assert selected == quarantine
    assert cleanup == project_sdk._ModuleRemovalCleanup()
    assert calls == [
        (
            "rename",
            {
                "source_root": source_root,
                "family": "idea",
                "source_name": "SAFE",
                "target_name": "SAFER",
                "target_object_id": "SAFER",
            },
        ),
        (
            "remove",
            {
                "source_root": source_root,
                "family": "idea",
                "module_name": "SAFER",
            },
        ),
        (
            "cleanup",
            {
                "source_root": source_root,
                "quarantine": quarantine,
            },
        ),
    ]


@pytest.mark.unit
def test_module_rename_reports_unavailable_authority_as_data_safety_block(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    project = Project.create(tmp_path / "starter", title="Starter Mod")

    def unavailable(*_args: object, **_kwargs: object) -> None:
        raise project_sdk._AnchoredModuleMutationUnavailable("Safe retained Windows module rename requires a fixed local NTFS or ReFS drive")

    monkeypatch.setattr(project_sdk, "_rename_module_directory", unavailable)

    with pytest.raises(ValueError, match="blocked to protect your files.*NTFS or ReFS"):
        project.rename_module(
            "modifier/starter_starter_modifier",
            "starter_renamed_modifier",
        )


@pytest.mark.unit
@pytest.mark.parametrize(
    "value",
    [
        "CON",
        "trailing.",
        "bad:name",
    ],
)
def test_module_identity_rejects_windows_nonportable_components(value: str) -> None:
    with pytest.raises(ValueError, match="not portable to Windows"):
        project_sdk._module_path_token(value, "object_id")


@pytest.mark.unit
@pytest.mark.parametrize(
    "value",
    [
        "CON.txt",
        "nested/trailing.",
        "nested/bad:name.txt",
    ],
)
def test_rendered_scaffold_path_rejects_windows_nonportable_components(
    value: str,
) -> None:
    with pytest.raises(templates_sdk.ProjectTemplateSpecError, match="not portable to Windows"):
        templates_sdk._safe_rendered_path(value, "idea/test")
