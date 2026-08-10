from __future__ import annotations

import os
from pathlib import Path

import heavenbase as hb
import pytest
from heavenbase.utils import dumps_json, loads_json

import paradev.build.extensions as project_extensions
from paradev.config import _CONTEXT_PARADEV
from paradev.sdk import Project, ProjectManifestError


def _write_project(root: Path, project_id: str = "registry_demo") -> None:
    (root / "src").mkdir(parents=True)
    (root / "paradev.yaml").write_text(
        "\n".join(
            (
                f"project_id: {project_id}",
                "title: Registry Demo",
                "game: hoi4",
                "source_roots: [src]",
                "build_root: .paradev/build",
                "",
            )
        ),
        encoding="utf-8",
    )


def _write_extension(
    root: Path,
    *,
    coordinate: str = "paradev-projects/registry_demo/sample",
    output_path: str = "common/demo/{object_id}.txt",
    hidden_metadata: bool = False,
    publication_block: str = "",
    presentation_block: str = "",
) -> None:
    module_root = root / "extensions" / "sample"
    module_root.mkdir(parents=True)
    (module_root / "__init__.py").write_text(
        "\n".join(
            (
                "from __future__ import annotations",
                "import os",
                "import heavenbase as hb",
                "from paradev.build import SimpleSourceFamily, Slot",
                "os.environ['PARADEV_TEST_EXTENSION_IMPORTED'] = 'yes'",
                "",
                "class SampleEntity(hb.Entity):",
                "    identifier = 'registry-demo-sample'",
                "    title = hb.field(hb.ShortText).default('')",
                "    family = 'registry_demo_sample'",
                "    resource_slots = (Slot('def', 'def.txt', required=True),)",
                "    compilation_hooks = ('normalize', 'check', 'emit')",
                "",
                "    @classmethod",
                "    def build_family(cls):",
                "        return SimpleSourceFamily(",
                "            family=cls.family,",
                "            source_slots=cls.resource_slots,",
                f"            pdx_path_template={output_path!r},",
                "        )",
                "",
                "def build_family():",
                "    return SampleEntity.build_family()",
                "",
            )
        ),
        encoding="utf-8",
    )
    descriptor_path = module_root / ".paradev/meta.yaml" if hidden_metadata else module_root / "meta.yaml"
    descriptor_path.parent.mkdir(parents=True, exist_ok=True)
    descriptor_path.write_text(
        f"""\
manifest_version: 2
coordinate: {coordinate}
version: 1.0.0
compatibility: {{heavenbase: {{min: 0.1.2.1, before: 0.1.3.0}}}}
items:
  - kind: entity
    identifier: registry-demo-sample
    source: path
    target: {{module: null, qualname: SampleEntity}}
    active: true
    meta: {{schema_version: 1}}
  - kind: extension
    identifier: registry-demo
    source: inline
    target: definition
    active: true
    meta:
      schema_version: 1
      dependencies: [entity:registry-demo-sample]
      definition:
        identifier: registry-demo
        name: Registry Demo
        version: 1.0.0
        desc: Test project extension.
        required: false
        requires: []
        entities: [registry-demo-sample]
        meta: {{}}
        setup: null
        api: null
        api_name: null
  - kind: paradev_build_family
    identifier: registry-demo-sample
    source: path
    target: {{module: null, qualname: build_family}}
    active: true
    meta:
      schema_version: 1
      dependencies: [extension:registry-demo]
{presentation_block}\
{publication_block}\
  - kind: paradev_authoring_template
    identifier: registry-demo-sample-basic
    source: inline
    target: definition
    active: true
    meta:
      schema_version: 1
      dependencies: [paradev_build_family:registry-demo-sample]
      definition:
        template_id: registry-demo:sample/basic
        declaration:
          title: Sample
          family: registry_demo_sample
          args:
            title: {{required: true}}
          files:
            meta.yaml: "title: {{title}}\\n"
            def.txt: "{{object_id}} = {{}}\\n"
""",
        encoding="utf-8",
    )


def test_project_extension_is_registry_first_and_owns_entity_family_and_template(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("PARADEV_TEST_EXTENSION_IMPORTED", raising=False)
    _write_project(tmp_path)
    _write_extension(tmp_path)

    project = Project.load(tmp_path)

    assert os.environ.get("PARADEV_TEST_EXTENSION_IMPORTED") is None
    assert [path.name for path in project.extension_modules] == ["sample"]

    registry = project._build_registry(profile="hoi4")
    family = registry.family("registry_demo_sample")

    assert os.environ["PARADEV_TEST_EXTENSION_IMPORTED"] == "yes"
    assert [slot.name for slot in family.source_slots] == ["def"]
    assert registry.identity_rewriter_for("registry_demo_sample").identifier == ("paradev.token-identity.v1")
    family_view = registry.to_view(family="registry_demo_sample")["families"][0]
    assert family_view["authoring"]["identity_copy"] == {
        "supported": True,
        "rewriter": "paradev.token-identity.v1",
    }
    template_rows = project.templates(template_id="registry-demo:sample/basic")["templates"]
    assert [(row["id"], row["family"], row["authoring_ready"]) for row in template_rows] == [("registry-demo:sample/basic", "registry_demo_sample", True)]

    extension = hb.ext.Extension.load("registry-demo", resolver=_CONTEXT_PARADEV.modules())
    entity = _CONTEXT_PARADEV.modules().resolve("entity", "registry-demo-sample")

    assert extension.entity_ids() == ["registry-demo-sample"]
    assert entity.family == "registry_demo_sample"
    assert entity.__module__.startswith("_heavenbase_artifact_")


def test_project_extension_stages_hidden_metadata_as_standard_heavenbase_module(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("PARADEV_TEST_EXTENSION_IMPORTED", raising=False)
    _write_project(tmp_path)
    _write_extension(tmp_path, hidden_metadata=True)
    module_root = tmp_path / "extensions/sample"

    project = Project.load(tmp_path)
    assert os.environ.get("PARADEV_TEST_EXTENSION_IMPORTED") is None
    family = project._build_registry(profile="hoi4").family("registry_demo_sample")

    assert not (module_root / "meta.yaml").exists()
    assert (module_root / ".paradev/meta.yaml").is_file()
    assert family.pdx_path_template == "common/demo/{object_id}.txt"
    assert os.environ["PARADEV_TEST_EXTENSION_IMPORTED"] == "yes"
    entity = _CONTEXT_PARADEV.modules().resolve(
        "entity",
        "registry-demo-sample",
    )
    assert entity.__module__.startswith("_heavenbase_artifact_")


def test_project_extension_loads_descriptor_owned_publication_replacements(
    tmp_path: Path,
) -> None:
    _write_project(tmp_path)
    _write_extension(
        tmp_path,
        hidden_metadata=True,
        publication_block="""\
      publication:
        replaces_families:
          - registry_demo_component
          - registry_demo_asset_component
""",
    )

    registry = Project.load(tmp_path)._build_registry(profile="hoi4")
    family = registry.family("registry_demo_sample")
    family_view = next(row for row in registry.to_view()["families"] if row["family"] == "registry_demo_sample")

    assert registry.publication_replacements_for("registry_demo_sample") == (
        "registry_demo_asset_component",
        "registry_demo_component",
    )
    assert not hasattr(family, "retired_families")
    assert "publication" not in family_view
    assert "replaces_families" not in family_view


def test_project_extension_loads_descriptor_owned_family_presentation(
    tmp_path: Path,
) -> None:
    _write_project(tmp_path)
    _write_extension(
        tmp_path,
        hidden_metadata=True,
        presentation_block="""\
      presentation:
        id: registry-demos
        title: Registry Demos
        group: events
        aliases: [registry-demo]
        title_key: modules.registryDemos.title
""",
    )

    registry = Project.load(tmp_path)._build_registry(profile="hoi4")
    family_view = next(row for row in registry.to_view()["families"] if row["family"] == "registry_demo_sample")

    assert registry.resolve_family("registry-demos") == "registry_demo_sample"
    assert registry.resolve_family("registry-demo") == "registry_demo_sample"
    assert family_view["presentation"] == {
        "id": "registry-demos",
        "title": "Registry Demos",
        "group": "events",
        "aliases": ["registry-demo"],
        "title_key": "modules.registryDemos.title",
    }


def test_project_extension_rejects_malformed_presentation_before_import(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("PARADEV_TEST_EXTENSION_IMPORTED", raising=False)
    _write_project(tmp_path)
    _write_extension(
        tmp_path,
        hidden_metadata=True,
        presentation_block="      presentation: invalid\n",
    )

    with pytest.raises(
        ProjectManifestError,
        match="meta.presentation must be a mapping",
    ):
        Project.load(tmp_path)._build_registry(profile="hoi4")

    assert os.environ.get("PARADEV_TEST_EXTENSION_IMPORTED") is None


def test_project_extension_rejects_malformed_publication_before_import(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("PARADEV_TEST_EXTENSION_IMPORTED", raising=False)
    _write_project(tmp_path)
    _write_extension(
        tmp_path,
        hidden_metadata=True,
        publication_block="      publication: invalid\n",
    )
    project = Project.load(tmp_path)

    with pytest.raises(
        ProjectManifestError,
        match="meta.publication must be a mapping",
    ):
        project._build_registry(profile="hoi4")

    assert os.environ.get("PARADEV_TEST_EXTENSION_IMPORTED") is None


def test_project_extension_rejects_ambiguous_visible_and_hidden_metadata(
    tmp_path: Path,
) -> None:
    _write_project(tmp_path)
    _write_extension(tmp_path)
    module_root = tmp_path / "extensions/sample"
    hidden = module_root / ".paradev/meta.yaml"
    hidden.parent.mkdir(parents=True)
    hidden.write_bytes((module_root / "meta.yaml").read_bytes())

    with pytest.raises(
        ProjectManifestError,
        match="contains both meta.yaml and .paradev/meta.yaml",
    ):
        Project.load(tmp_path)


def test_project_extension_coordinate_mismatch_fails_before_import(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("PARADEV_TEST_EXTENSION_IMPORTED", raising=False)
    _write_project(tmp_path, project_id="registry_mismatch")
    _write_extension(tmp_path, coordinate="paradev-projects/wrong/sample")
    project = Project.load(tmp_path)

    with pytest.raises(ProjectManifestError, match="does not match expected coordinate"):
        project._build_registry(profile="hoi4")

    assert os.environ.get("PARADEV_TEST_EXTENSION_IMPORTED") is None


def test_project_extension_cache_reinstalls_the_requested_checkout(
    tmp_path: Path,
) -> None:
    first_root = tmp_path / "first"
    second_root = tmp_path / "second"
    _write_project(first_root)
    _write_project(second_root)
    _write_extension(first_root, output_path="common/first/{object_id}.txt")
    _write_extension(second_root, output_path="common/second/{object_id}.txt")
    first = Project.load(first_root)
    second = Project.load(second_root)

    first_family = first._build_registry(profile="hoi4").family("registry_demo_sample")
    second_family = second._build_registry(profile="hoi4").family("registry_demo_sample")
    restored_first_family = first._build_registry(profile="hoi4").family("registry_demo_sample")

    assert first_family.pdx_path_template == "common/first/{object_id}.txt"
    assert second_family.pdx_path_template == "common/second/{object_id}.txt"
    assert restored_first_family.pdx_path_template == "common/first/{object_id}.txt"


def test_project_extension_refreshes_and_retries_heavenbase_registry_conflict(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _write_project(tmp_path)
    _write_extension(tmp_path)
    project = Project.load(tmp_path)
    resolver = _CONTEXT_PARADEV.modules()
    original_install = resolver.install
    install_attempts = 0
    refresh_attempts = 0

    def install_with_one_conflict(*args: object, **kwargs: object) -> object:
        nonlocal install_attempts
        install_attempts += 1
        if install_attempts == 1:
            raise hb.RegistryConflictError("Registry 'system-modules' compare-and-set conflict at revision 1; " "refresh before retrying")
        return original_install(*args, **kwargs)

    def refresh_after_conflict() -> bool:
        nonlocal refresh_attempts
        refresh_attempts += 1
        return True

    monkeypatch.setattr(resolver, "install", install_with_one_conflict)
    monkeypatch.setattr(resolver, "refresh", refresh_after_conflict)

    family = project._build_registry(profile="hoi4").family("registry_demo_sample")

    assert family.family == "registry_demo_sample"
    assert install_attempts == 2
    assert refresh_attempts == 3


def test_project_extension_reports_unrefreshable_registry_conflict(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _write_project(tmp_path)
    _write_extension(tmp_path)
    project = Project.load(tmp_path)
    resolver = _CONTEXT_PARADEV.modules()

    def conflicting_install(*args: object, **kwargs: object) -> object:
        del args, kwargs
        raise hb.RegistryConflictError("Registry 'system-modules' compare-and-set conflict at revision 1; " "refresh before retrying")

    monkeypatch.setattr(resolver, "install", conflicting_install)
    monkeypatch.setattr(resolver, "refresh", lambda: False)

    with pytest.raises(
        ProjectManifestError,
        match="Extension registry changed concurrently",
    ):
        project._build_registry(profile="hoi4")


def test_project_extension_reuses_verified_persistent_install_receipt(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _write_project(tmp_path)
    _write_extension(tmp_path)
    project = Project.load(tmp_path)
    resolver = _CONTEXT_PARADEV.modules()

    first = project._build_registry(profile="hoi4").family("registry_demo_sample")
    cache_path = tmp_path / ".paradev" / "cache" / "extension-install.json"
    assert cache_path.is_file()

    project_extensions._PROJECT_EXTENSION_INSTALL_CACHE.clear()
    install_attempts = 0
    original_install = resolver.install

    def counted_install(*args: object, **kwargs: object) -> object:
        nonlocal install_attempts
        install_attempts += 1
        return original_install(*args, **kwargs)

    def unexpected_publication_lock() -> object:
        raise AssertionError("a verified read must not wait for the writer lock")

    monkeypatch.setattr(resolver, "install", counted_install)
    monkeypatch.setattr(
        project_extensions,
        "_project_extension_registry_lock",
        unexpected_publication_lock,
    )

    restored = project._build_registry(profile="hoi4").family("registry_demo_sample")

    assert first.pdx_path_template == restored.pdx_path_template
    assert install_attempts == 0


def test_project_extension_rejects_incomplete_persistent_install_receipt(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _write_project(tmp_path)
    _write_extension(tmp_path)
    project = Project.load(tmp_path)
    resolver = _CONTEXT_PARADEV.modules()

    project._build_registry(profile="hoi4")
    cache_path = tmp_path / ".paradev" / "cache" / "extension-install.json"
    payload = loads_json(cache_path.read_text(encoding="utf-8"))
    assert isinstance(payload, dict)
    payload["publications"] = []
    cache_path.write_text(
        f"{dumps_json(payload, sort_keys=True, indent=2).rstrip()}\n",
        encoding="utf-8",
    )
    project_extensions._PROJECT_EXTENSION_INSTALL_CACHE.clear()
    install_attempts = 0
    original_install = resolver.install

    def counted_install(*args: object, **kwargs: object) -> object:
        nonlocal install_attempts
        install_attempts += 1
        return original_install(*args, **kwargs)

    monkeypatch.setattr(resolver, "install", counted_install)

    restored = project._build_registry(profile="hoi4").family("registry_demo_sample")

    assert restored.family == "registry_demo_sample"
    assert install_attempts == 1
