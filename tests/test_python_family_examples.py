from __future__ import annotations

from pathlib import Path
from shutil import copyfile

from paradev.build import BuildResult
from paradev.sdk import Project

ROOT = Path(__file__).resolve().parents[1]
EXAMPLE_ROOT = ROOT / "docs/examples/families"


def test_superevent_python_family_example_builds_module(tmp_path: Path) -> None:
    family_file = tmp_path / "tools/families/superevent.py"
    family_file.parent.mkdir(parents=True)
    copyfile(EXAMPLE_ROOT / "superevent.py", family_file)
    module_root = tmp_path / "src/modules/superevent/FALL_OF_PARIS"
    module_root.mkdir(parents=True)
    (module_root / "script.pdx").write_text("country_event = { id = superevent.1 }", encoding="utf-8")
    (module_root / "main.loc").write_text("en:\n  FALL_OF_PARIS: Fall of Paris\n", encoding="utf-8")
    (module_root / "meta.yaml").write_text("type: superevent\nscope: country\n", encoding="utf-8")
    _write_manifest(tmp_path, "python_family_superevent", "tools/families/superevent.py")

    project = Project.load(tmp_path)
    result = project.build()
    families = {row["family"]: row for row in project.families()["families"]}

    assert "superevent" in families
    assert [diagnostic.code for diagnostic in result.diagnostics] == []
    assert result.modules[0].source_slots == {"script": ("script.pdx",), "loc": ("main.loc",)}
    assert _content_artifact_paths(result) == [
        "events/superevents/FALL_OF_PARIS.txt",
        "localisation/english/FALL_OF_PARIS_l_english.yml",
    ]


def test_news_event_collection_python_family_example_builds_collection(tmp_path: Path) -> None:
    family_file = tmp_path / "tools/families/news_event.py"
    family_file.parent.mkdir(parents=True)
    copyfile(EXAMPLE_ROOT / "news_event.py", family_file)
    module_root = tmp_path / "src/modules/news_event/GER_news"
    collection_root = tmp_path / "src/collections/news_event/germany"
    module_root.mkdir(parents=True)
    collection_root.mkdir(parents=True)
    (module_root / "body.pdx").write_text("country_event = { id = germany.1 }", encoding="utf-8")
    (module_root / "meta.yaml").write_text("type: news_event\ncollection: germany\n", encoding="utf-8")
    (collection_root / "header.pdx").write_text("add_namespace = germany", encoding="utf-8")
    (collection_root / "strings.loc").write_text("en:\n  germany: Germany News\n", encoding="utf-8")
    _write_manifest(tmp_path, "python_family_news_event", "tools/families/news_event.py")

    project = Project.load(tmp_path)
    result = project.build()
    families = {row["family"]: row for row in project.families()["families"]}

    assert "news_event" in families
    assert [diagnostic.code for diagnostic in result.diagnostics] == []
    assert result.collections[0].module_ids == ("news_event/GER_news",)
    assert _content_artifact_paths(result) == [
        "events/germany.txt",
        "localisation/english/germany_l_english.yml",
    ]


def _write_manifest(root: Path, project_id: str, python_module: str) -> None:
    (root / "paradev.yaml").write_text(
        "\n".join(
            [
                f"project_id: {project_id}",
                "title: Python Family Example",
                "game: hoi4",
                "source_roots: [src]",
                "output_root: build/mod",
                "build_root: .paradev/.cache/build",
                "python_modules:",
                f"  - {python_module}",
            ]
        ),
        encoding="utf-8",
    )


def _content_artifact_paths(result: BuildResult) -> list[str]:
    return [artifact.path for artifact in result.artifacts if artifact.artifact_type != "mod_descriptor"]
