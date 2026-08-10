from __future__ import annotations

import os
from pathlib import Path

import pytest

from paradev.sdk import templates as templates_sdk
from paradev.sdk import Project, ProjectManifestError
from paradev.sdk import project as project_sdk


def _write_titled_template_project(root: Path) -> Project:
    (root / "src").mkdir(parents=True)
    (root / "paradev.yaml").write_text(
        "\n".join(
            [
                "project_id: titled_template_project",
                "title: Titled Template Project",
                "game: hoi4",
                "source_roots: [src]",
                "output_root: build/mod",
                "build_root: .paradev/.cache/build",
                "templates:",
                "  modifier/titled:",
                "    title: Titled Modifier",
                "    family: modifier",
                "    directory: '{object_id} - {title}'",
                "    args:",
                "      title:",
                "        required: true",
                "    files:",
                "      meta.yaml: |",
                "        title: {title}",
                "      def.txt: |",
                "        {object_id} = {{",
                "          stability_factor = 0.05",
                "        }}",
            ]
        ),
        encoding="utf-8",
    )
    return Project.load(root)


def test_project_template_exposes_transport_neutral_reference_hint(
    tmp_path: Path,
) -> None:
    (tmp_path / "src").mkdir()
    (tmp_path / "paradev.yaml").write_text(
        "\n".join(
            [
                "project_id: referenced_template_project",
                "title: Referenced Template Project",
                "game: hoi4",
                "source_roots: [src]",
                "output_root: build/mod",
                "build_root: .paradev/.cache/build",
                "templates:",
                "  focus/referenced:",
                "    family: focus",
                "    args:",
                "      tree:",
                "        required: true",
                "        reference:",
                "          kind: collection",
                "          family: focus",
                "    files:",
                "      def.txt: '{object_id} = {{}}'",
            ]
        ),
        encoding="utf-8",
    )

    template = Project.load(tmp_path).templates(
        template_id="focus/referenced",
    )[
        "templates"
    ][0]

    reference = {"kind": "collection", "family": "focus"}
    assert template["args"]["tree"]["reference"] == reference
    assert template["form"]["fields"][0]["reference"] == reference


def test_project_local_template_directory_writes_titled_root_with_logical_identity(
    tmp_path: Path,
) -> None:
    project = _write_titled_template_project(tmp_path)

    template = project.templates(template_id="modifier/titled")["templates"][0]
    plan = project.scaffold_module(
        "modifier/titled",
        "GER_RECOVERY",
        values={"title": "German Recovery"},
        write=True,
    )

    module_root = tmp_path / "src/modules/modifier/GER_RECOVERY - German Recovery"
    assert template["directory"] == "{object_id} - {title}"
    assert plan["blocked"] is False
    assert plan["written"] is True
    assert plan["folder_name"] == "GER_RECOVERY - German Recovery"
    assert plan["object_id"] == "GER_RECOVERY"
    assert plan["module_id"] == "modifier/GER_RECOVERY"
    assert plan["root"] == str(module_root)
    assert plan["authoring_plan"]["authoring_path"]["object_id"] == "GER_RECOVERY"
    assert plan["authoring_plan"]["authoring_path"]["module_id"] == "modifier/GER_RECOVERY"
    assert plan["authoring_plan"]["authoring_path"]["root"] == str(module_root)
    assert plan["authoring_plan"]["authoring_path"]["relative_path"] == ("src/modules/modifier/GER_RECOVERY - German Recovery")
    assert {row["root"] for row in plan["authoring_plan"]["source_slots"]} == {str(module_root)}
    assert (module_root / "meta.yaml").read_text(encoding="utf-8") == ("title: German Recovery\n")


@pytest.mark.parametrize(
    "folder_name",
    [
        "GER_RECOVERY",
        "GER_RECOVERY - Previous Display Title",
    ],
    ids=["unsuffixed", "different-title"],
)
def test_project_local_template_directory_reuses_unique_logical_root(
    tmp_path: Path,
    folder_name: str,
) -> None:
    project = _write_titled_template_project(tmp_path)
    module_root = tmp_path / "src/modules/modifier" / folder_name
    module_root.mkdir(parents=True)

    plan = project.scaffold_module(
        "modifier/titled",
        "GER_RECOVERY",
        values={"title": "Current Display Title"},
        write=True,
    )

    assert plan["blocked"] is False
    assert plan["written"] is True
    assert plan["folder_name"] == folder_name
    assert plan["object_id"] == "GER_RECOVERY"
    assert plan["module_id"] == "modifier/GER_RECOVERY"
    assert plan["root"] == str(module_root)
    assert plan["authoring_plan"]["authoring_path"]["root"] == str(module_root)
    assert (module_root / "meta.yaml").read_text(encoding="utf-8") == ("title: Current Display Title\n")
    assert not (tmp_path / "src/modules/modifier/GER_RECOVERY - Current Display Title").exists()


def test_project_authoring_path_keeps_existing_legacy_display_suffix_addressable(
    tmp_path: Path,
) -> None:
    project = _write_titled_template_project(tmp_path)
    module_root = tmp_path / "src/modules/modifier/GER_LEGACY - Legacy title..."
    module_root.mkdir(parents=True)

    payload = project.authoring_path("module", "modifier", "GER_LEGACY")
    plan = project.authoring_plan("module", "modifier", "GER_LEGACY")

    assert payload["exists"] is True
    assert payload["root"] == str(module_root)
    assert payload["module_id"] == "modifier/GER_LEGACY"
    assert plan["authoring_path"]["root"] == str(module_root)


def test_project_authoring_path_keeps_existing_spaced_logical_id_addressable(
    tmp_path: Path,
) -> None:
    project = _write_titled_template_project(tmp_path)
    object_id = "1-West Arctic Dragon Lair"
    module_root = tmp_path / "src/modules/modifier" / object_id
    module_root.mkdir(parents=True)

    payload = project.authoring_path("module", "modifier", object_id)
    plan = project.authoring_plan("module", "modifier", object_id)

    assert payload["exists"] is True
    assert payload["root"] == str(module_root)
    assert payload["module_id"] == f"modifier/{object_id}"
    assert plan["authoring_path"]["root"] == str(module_root)


@pytest.mark.parametrize(
    ("object_id", "existing_folders"),
    [
        (
            "GER_RECOVERY",
            ("GER_RECOVERY", "GER_RECOVERY - Previous Display Title"),
        ),
        ("GER_RECOVERY", ("ger_recovery - Case Alias",)),
        ("CAFÉ_RECOVERY", ("CAFE\u0301_RECOVERY - Unicode Alias",)),
    ],
    ids=["ambiguous", "case-alias", "nfc-alias"],
)
def test_project_local_template_directory_blocks_ambiguous_or_portable_aliases(
    tmp_path: Path,
    object_id: str,
    existing_folders: tuple[str, ...],
) -> None:
    project = _write_titled_template_project(tmp_path)
    family_root = tmp_path / "src/modules/modifier"
    for folder_name in existing_folders:
        (family_root / folder_name).mkdir(parents=True, exist_ok=True)

    plan = project.scaffold_module(
        "modifier/titled",
        object_id,
        values={"title": "Current Display Title"},
        write=True,
    )

    assert plan["blocked"] is True
    assert plan["written"] is False
    assert any(row["severity"] == "error" for row in plan["diagnostics"])
    assert not (family_root / f"{object_id} - Current Display Title").exists()


@pytest.mark.parametrize(
    ("title", "folder_title"),
    [
        ("Nested/Title", "Nested－Title"),
        ("Windows:Reserved", "Windows－Reserved"),
        ("Trailing Dot.", "Trailing Dot"),
        (
            "Progress ([?ROOT.progress|Y0]/4)",
            "Progress",
        ),
        (
            "§YIntel§! £operative_mission_icons_small|1£Network",
            "Intel Network",
        ),
    ],
    ids=[
        "path-separator",
        "nonportable-character",
        "nonportable-trailing-dot",
        "runtime-value",
        "formatting-and-icon",
    ],
)
def test_project_local_template_directory_normalizes_title_without_changing_source(
    tmp_path: Path,
    title: str,
    folder_title: str,
) -> None:
    project = _write_titled_template_project(tmp_path)

    plan = project.scaffold_module(
        "modifier/titled",
        "GER_UNSAFE",
        values={"title": title},
        write=True,
    )

    module_root = tmp_path / "src/modules/modifier" / f"GER_UNSAFE - {folder_title}"
    assert plan["blocked"] is False
    assert plan["written"] is True
    assert plan["folder_name"] == f"GER_UNSAFE - {folder_title}"
    assert (module_root / "meta.yaml").read_text(encoding="utf-8") == (f"title: {title}\n")


def test_project_local_template_directory_rolls_back_when_alias_appears_during_install(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    project = _write_titled_template_project(tmp_path)
    original_check = templates_sdk._require_no_scaffold_module_alias
    check_count = 0

    def inject_alias(
        family_fd: int,
        *,
        object_id: str,
        folder_name: str,
    ) -> None:
        nonlocal check_count
        check_count += 1
        if check_count == 3:
            os.mkdir(f"{object_id} - Concurrent Alias", dir_fd=family_fd)
        original_check(
            family_fd,
            object_id=object_id,
            folder_name=folder_name,
        )

    monkeypatch.setattr(
        templates_sdk,
        "_require_no_scaffold_module_alias",
        inject_alias,
    )

    plan = project.create_module(
        "modifier/titled",
        "GER_RACE",
        values={"title": "Planned Title"},
    )

    family_root = tmp_path / "src/modules/modifier"
    assert plan["blocked"] is True
    assert plan["written"] is False
    assert {row["code"] for row in plan["diagnostics"]} == {"scaffold.concurrent_change"}
    assert not (family_root / "GER_RACE - Planned Title").exists()
    assert (family_root / "GER_RACE - Concurrent Alias").is_dir()
    transaction_root = tmp_path / "src/.paradev/module-transactions"
    assert not transaction_root.exists() or list(transaction_root.iterdir()) == []


def test_project_create_modules_supports_titled_roots_and_hidden_metadata_retry(
    tmp_path: Path,
) -> None:
    project = _write_titled_template_project(tmp_path)
    requests = [
        {
            "template_id": "modifier/titled",
            "object_id": "GER_ALPHA",
            "values": {"title": "Alpha Recovery"},
        },
        {
            "template_id": "modifier/titled",
            "object_id": "GER_BETA",
            "values": {"title": "Beta Recovery"},
        },
    ]

    plan = project.create_modules(requests)
    repeated = project.create_modules(requests)

    expected_roots = [
        tmp_path / "src/modules/modifier/GER_ALPHA - Alpha Recovery",
        tmp_path / "src/modules/modifier/GER_BETA - Beta Recovery",
    ]
    assert plan["blocked"] is False
    assert plan["plan_hash"] == repeated["plan_hash"]
    assert [row["folder_name"] for row in plan["modules"]] == [
        "GER_ALPHA - Alpha Recovery",
        "GER_BETA - Beta Recovery",
    ]
    assert [row["module_id"] for row in plan["modules"]] == [
        "modifier/GER_ALPHA",
        "modifier/GER_BETA",
    ]
    assert [row["root"] for row in plan["modules"]] == [str(root) for root in expected_roots]
    assert [row["authoring_plan"]["authoring_path"]["root"] for row in plan["modules"]] == [str(root) for root in expected_roots]

    applied = project.create_modules(
        requests,
        write=True,
        plan_hash=plan["plan_hash"],
    )

    assert applied["blocked"] is False
    assert applied["applied"] is True
    assert applied["written"] is True
    assert [row["status"] for row in applied["modules"]] == ["created", "created"]
    assert all((root / "meta.yaml").is_file() for root in expected_roots)

    stale_retry = project.create_modules(
        requests,
        write=True,
        plan_hash=plan["plan_hash"],
    )

    assert stale_retry["blocked"] is True
    assert {row["code"] for row in stale_retry["diagnostics"]} == {"module_batch.plan_hash_mismatch"}

    unchanged_before_hidden_metadata = project.create_modules(requests)
    hidden_root = expected_roots[0] / ".paradev"
    hidden_root.mkdir()
    (hidden_root / "import.yaml").write_text(
        "source: authored\n",
        encoding="utf-8",
    )
    unchanged_after_hidden_metadata = project.create_modules(requests)

    assert unchanged_before_hidden_metadata["plan_hash"] == (unchanged_after_hidden_metadata["plan_hash"])
    assert [row["status"] for row in unchanged_after_hidden_metadata["modules"]] == [
        "unchanged",
        "unchanged",
    ]

    retried = project.create_modules(
        requests,
        write=True,
        plan_hash=unchanged_after_hidden_metadata["plan_hash"],
    )

    assert retried["blocked"] is False
    assert retried["applied"] is True
    assert retried["written"] is False
    assert [row["status"] for row in retried["modules"]] == [
        "unchanged",
        "unchanged",
    ]


def test_project_manifest_reserves_module_local_paradev_template_files(
    tmp_path: Path,
) -> None:
    (tmp_path / "src").mkdir()
    (tmp_path / "paradev.yaml").write_text(
        "\n".join(
            [
                "project_id: reserved_template_file",
                "title: Reserved Template File",
                "game: hoi4",
                "source_roots: [src]",
                "output_root: build/mod",
                "build_root: .paradev/.cache/build",
                "templates:",
                "  modifier/reserved:",
                "    family: modifier",
                "    files:",
                "      .paradev/state.yaml: 'source: template'",
                "      def.txt: '{object_id} = {{}}'",
            ]
        ),
        encoding="utf-8",
    )

    with pytest.raises(ProjectManifestError, match=r"\.paradev"):
        Project.load(tmp_path)


def test_project_template_can_declare_trusted_hidden_system_metadata(
    tmp_path: Path,
) -> None:
    (tmp_path / "src").mkdir()
    (tmp_path / "paradev.yaml").write_text(
        "\n".join(
            [
                "project_id: hidden_template_metadata",
                "title: Hidden Template Metadata",
                "game: hoi4",
                "source_roots: [src]",
                "output_root: build/mod",
                "build_root: .paradev/.cache/build",
                "templates:",
                "  modifier/hidden:",
                "    family: modifier",
                "    directory: '{object_id} - {title}'",
                "    args:",
                "      title:",
                "        required: true",
                "      subtype:",
                "        default: political",
                "    files:",
                "      def.txt: '{object_id} = {{}}'",
                "    system_files:",
                "      .paradev/meta.yaml: |",
                "        settings:",
                "          subtype: {subtype}",
            ]
        ),
        encoding="utf-8",
    )
    project = Project.load(tmp_path)

    template = project.templates(template_id="modifier/hidden")["templates"][0]
    plan = project.scaffold_module(
        "modifier/hidden",
        "MODIFIER_HIDDEN",
        values={"title": "Hidden metadata"},
        write=True,
    )

    module_root = tmp_path / "src/modules/modifier/MODIFIER_HIDDEN - Hidden metadata"
    assert template["files"] == ["def.txt"]
    assert plan["blocked"] is False
    assert plan["written"] is True
    assert not (module_root / "meta.yaml").exists()
    assert (module_root / ".paradev/meta.yaml").read_text(encoding="utf-8") == "settings:\n  subtype: political\n"


def test_project_module_rename_preserves_human_readable_suffix(
    tmp_path: Path,
) -> None:
    project = _write_titled_template_project(tmp_path)
    previous_root = tmp_path / "src/modules/modifier/GER_OLD - Human Readable Title"
    previous_root.mkdir(parents=True)
    (previous_root / "meta.yaml").write_text(
        "title: Human Readable Title\n",
        encoding="utf-8",
    )
    (previous_root / "def.txt").write_text(
        "GER_OLD = { stability_factor = 0.05 }\n",
        encoding="utf-8",
    )

    payload = project.rename_module("modifier/GER_OLD", "GER_NEW")

    renamed_root = tmp_path / "src/modules/modifier/GER_NEW - Human Readable Title"
    assert payload["previous_module_id"] == "modifier/GER_OLD"
    assert payload["module_id"] == "modifier/GER_NEW"
    assert payload["previous_root"] == str(previous_root)
    assert payload["root"] == str(renamed_root)
    assert payload["relative_path"] == ("src/modules/modifier/GER_NEW - Human Readable Title")
    assert payload["module"]["root"] == str(renamed_root)
    assert not previous_root.exists()
    assert (renamed_root / "def.txt").read_text(encoding="utf-8") == ("GER_OLD = { stability_factor = 0.05 }\n")


def test_project_module_rename_rejects_existing_logical_target_alias(
    tmp_path: Path,
) -> None:
    project = _write_titled_template_project(tmp_path)
    family_root = tmp_path / "src/modules/modifier"
    previous_root = family_root / "GER_OLD - Human Readable Title"
    alias_root = family_root / "GER_NEW - Other Title"
    previous_root.mkdir(parents=True)
    alias_root.mkdir()
    (previous_root / "def.txt").write_text(
        "GER_OLD = { stability_factor = 0.05 }\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="Module target already exists"):
        project.rename_module("modifier/GER_OLD", "GER_NEW")

    assert previous_root.is_dir()
    assert alias_root.is_dir()
    assert not (family_root / "GER_NEW - Human Readable Title").exists()


def test_project_module_rename_rolls_back_when_logical_alias_appears(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    project = _write_titled_template_project(tmp_path)
    family_root = tmp_path / "src/modules/modifier"
    previous_name = "GER_OLD - Human Readable Title"
    target_name = "GER_NEW - Human Readable Title"
    previous_root = family_root / previous_name
    target_root = family_root / target_name
    concurrent_alias = family_root / "GER_NEW - Concurrent Alias"
    previous_root.mkdir(parents=True)
    (previous_root / "def.txt").write_text(
        "GER_OLD = { stability_factor = 0.05 }\n",
        encoding="utf-8",
    )
    original_rename = os.rename
    injected = False

    def inject_alias(source: str, target: str, *args: object, **kwargs: object) -> None:
        nonlocal injected
        original_rename(source, target, *args, **kwargs)
        if source == previous_name and target == target_name and not injected:
            injected = True
            os.mkdir(concurrent_alias.name, dir_fd=kwargs["dst_dir_fd"])

    monkeypatch.setattr(project_sdk.os, "rename", inject_alias)

    with pytest.raises(ValueError, match="Module rename path changed"):
        project.rename_module("modifier/GER_OLD", "GER_NEW")

    assert previous_root.is_dir()
    assert not target_root.exists()
    assert concurrent_alias.is_dir()
