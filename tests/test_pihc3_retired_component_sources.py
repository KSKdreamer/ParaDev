from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from hashlib import sha256
from pathlib import Path

from paradev.localization._source import parse_source
from paradev.portable_paths import portable_authoring_title
from paradev.sdk import Project

REPO_ROOT = Path(__file__).resolve().parents[1]
PIHC3_ROOT = REPO_ROOT / "projects/PIHC3"
FORBIDDEN_DIRECTORY_NAMES = {"inactive_collections", "inactive_modules", "legacy"}
FORBIDDEN_DIRECTORY_SUFFIXES = ("_component", "_asset_component")
FORBIDDEN_OBJECT_ID_PATTERN = re.compile(
    r"(?:^|_)(?:asset_component|component)(?:_|$)",
    flags=re.IGNORECASE,
)
LEGACY_SHADOW_SUFFIX_PATTERN = re.compile(
    r"_legacy\d*(?=\.[^.]+$)",
    flags=re.IGNORECASE,
)
RETIRED_SUPPORT_FAMILIES = {
    "decision_support",
    "idea_support",
    "special_project_support",
    "technology_support",
}
PREFERRED_LOCALIZATION_LANGUAGES = (
    "zh",
    "l_simp_chinese",
    "en",
    "l_english",
)
LOCALIZATION_REPLACEMENT_ROOT = PIHC3_ROOT / "src/modules/localization" / "LOCALIZATION_REPLACEMENTS - 全局本地化覆盖" / "localisation"
SOURCE_LAYOUT_CHECK = PIHC3_ROOT / "scripts/check_source_layout.py"


def _run_source_layout_check(project_root: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            str(SOURCE_LAYOUT_CHECK),
            "--project-root",
            str(project_root),
            "--json",
        ],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )


def _project_directories() -> tuple[Path, ...]:
    """Return the live PIHC3 tree without interpreting Git's historical objects."""

    directories: list[Path] = []
    for root, names, _files in os.walk(PIHC3_ROOT):
        names[:] = [name for name in names if name != ".git"]
        root_path = Path(root)
        directories.extend(root_path / name for name in names)
    return tuple(directories)


def _section_localization_rows(path: Path) -> dict[str, dict[str, str]]:
    rows: dict[str, dict[str, str]] = {}
    language: str | None = None
    key: str | None = None
    value_lines: list[str] = []

    def flush() -> None:
        if language is not None and key is not None:
            rows.setdefault(language, {})[key] = "\n".join(value_lines).strip()

    for line in path.read_text(encoding="utf-8").splitlines():
        match = re.fullmatch(r"\[(?P<language>[^.]+)\.(?P<key>.+)]", line.strip())
        if match is None:
            value_lines.append(line)
            continue
        flush()
        language = match.group("language")
        key = match.group("key")
        value_lines = []
    flush()
    return rows


def _humanized_id(object_id: str) -> str:
    return " ".join(part if re.fullmatch(r"[A-Z]\d+", part) else part.capitalize() for part in object_id.split("_"))


def _collection_title(folder: Path, collection_id: str) -> str:
    localization: dict[str, dict[str, str]] = {}
    for path in sorted(folder.glob("*.loc")):
        for language, rows in _section_localization_rows(path).items():
            localization.setdefault(language, {}).update(rows)
    for language in PREFERRED_LOCALIZATION_LANGUAGES:
        title = localization.get(language, {}).get(collection_id, "").strip()
        if title:
            return portable_authoring_title(title, object_id=collection_id)
    return portable_authoring_title(
        _humanized_id(collection_id),
        object_id=collection_id,
    )


def _preferred_localized_title(item: dict[str, object]) -> str | None:
    raw = item.get("localized_titles")
    if not isinstance(raw, dict):
        return None
    for language in PREFERRED_LOCALIZATION_LANGUAGES:
        title = raw.get(language)
        if isinstance(title, str) and title.strip():
            return title.strip()
    return None


def test_pihc3_has_no_retired_source_layout_or_migration_toolchain() -> None:
    """Keep completed migration machinery out of the authoring project."""

    source_root = PIHC3_ROOT / "src"
    scripts_root = PIHC3_ROOT / "scripts"
    migration_docs = PIHC3_ROOT / "docs/migration"
    project_directories = _project_directories()
    hidden_files = {
        path.relative_to(hidden_root).as_posix() for hidden_root in source_root.rglob(".paradev") for path in hidden_root.rglob("*") if path.is_file()
    }
    forbidden_directories = [
        path.relative_to(PIHC3_ROOT).as_posix()
        for path in project_directories
        if path.name in FORBIDDEN_DIRECTORY_NAMES or path.name.endswith(FORBIDDEN_DIRECTORY_SUFFIXES)
    ]
    assert forbidden_directories == []
    assert not [
        path
        for root in (
            source_root / "modules",
            PIHC3_ROOT / "extensions",
        )
        for path in root.iterdir()
        if path.name in RETIRED_SUPPORT_FAMILIES
    ]
    assert not tuple(scripts_root.glob("migrate*.py"))
    assert not tuple((scripts_root / "data").glob("pihc2_*"))
    assert hidden_files <= {"diagram.yaml", "entities.json", "meta.yaml"}
    assert {path.name for path in migration_docs.iterdir() if path.is_file()} == {"README.md"}

    extension_sources = "\n".join(
        path.read_text(encoding="utf-8") for path in sorted((PIHC3_ROOT / "extensions").rglob("*")) if path.is_file() and path.suffix in {".py", ".yaml"}
    )
    assert "replaces_families" not in extension_sources
    assert "_asset_component" not in extension_sources
    assert not re.search(r"\b[a-z][a-z_]*_component\b", extension_sources)


def test_pihc3_source_layout_preflight_reports_the_exact_live_inventory() -> None:
    result = _run_source_layout_check(PIHC3_ROOT)

    assert result.returncode == 0, result.stdout + result.stderr
    payload = json.loads(result.stdout)
    assert payload == {
        "errors": [],
        "ok": True,
        "schema": "pihc3.source-layout-audit.v1",
        "summary": {
            "collection_families": 2,
            "collections": 90,
            "hidden_metadata_files": 898,
            "module_families": 70,
            "modules": 14_575,
            "source_files": 36_470,
            "visible_metadata_files": 1,
        },
    }


def test_pihc3_source_layout_preflight_rejects_retired_and_ambiguous_sources(
    tmp_path: Path,
) -> None:
    project_root = tmp_path / "project"
    valid_module = project_root / "src/modules/idea/IDEA_OK - Clear title"
    valid_collection = project_root / "src/collections/focus/TREE_OK - Clear tree"
    valid_module.mkdir(parents=True)
    valid_collection.mkdir(parents=True)
    (valid_module / "def.txt").write_text("IDEA_OK = {}\n", encoding="utf-8")
    (valid_collection / "def.txt").write_text("focus_tree = {}\n", encoding="utf-8")
    for housekeeping_path in (
        project_root / "src/.DS_Store",
        project_root / "src/modules/.DS_Store",
        valid_module / ".DS_Store",
    ):
        housekeeping_path.write_bytes(b"Finder metadata is not authoring source")

    retired = project_root / "src/modules/idea_asset_component/OLD - Old"
    retired.mkdir(parents=True)
    (retired / "def.txt").write_text("old\n", encoding="utf-8")
    inactive_collections = project_root / "src/collections/inactive_collections"
    inactive_collections.mkdir()
    (inactive_collections / "old.txt").write_text("old\n", encoding="utf-8")
    legacy = valid_module / "Legacy"
    legacy.mkdir()
    (legacy / "source.txt").write_text("old\n", encoding="utf-8")
    copied = project_root / "src/modules/idea/IDEA_COPY - Clear title - 副本"
    copied.mkdir()
    (copied / "def.txt").write_text("copy\n", encoding="utf-8")
    empty = valid_module / "empty"
    empty.mkdir()
    malformed = project_root / "src/modules/idea/IDEA_WITHOUT_TITLE"
    malformed.mkdir()
    (malformed / "def.txt").write_text("broken\n", encoding="utf-8")
    metadata = valid_module / "meta.yaml"
    metadata.write_text("settings:\n  compiler: hidden\n", encoding="utf-8")

    result = _run_source_layout_check(project_root)

    assert result.returncode == 1
    payload = json.loads(result.stdout)
    assert payload["ok"] is False
    errors = "\n".join(payload["errors"])
    assert "retired directory: src/modules/idea_asset_component" in errors
    assert "retired directory: src/collections/inactive_collections" in errors
    assert "retired directory: src/modules/idea/IDEA_OK - Clear title/Legacy" in errors
    assert "source directory is empty: src/modules/idea/IDEA_OK - Clear title/empty" in errors
    assert "source path contains a copy marker:" in errors
    assert "source unit must use id - title:" in errors
    assert "visible metadata has system-owned keys" in errors
    assert ".DS_Store" not in errors
    assert payload["summary"]["source_files"] == 6


def test_pihc3_has_no_legacy_shadow_copies_beside_canonical_assets() -> None:
    """Reject obsolete ``*_legacy`` backups when the canonical asset exists."""

    shadow_copies: list[str] = []
    modules_root = PIHC3_ROOT / "src/modules"
    for path in modules_root.rglob("*"):
        if not path.is_file() or LEGACY_SHADOW_SUFFIX_PATTERN.search(path.name) is None:
            continue
        canonical_name = LEGACY_SHADOW_SUFFIX_PATTERN.sub("", path.name)
        if path.with_name(canonical_name).is_file():
            shadow_copies.append(path.relative_to(PIHC3_ROOT).as_posix())

    assert shadow_copies == []


def test_pihc3_hidden_localization_module_contains_only_explicit_replacements() -> None:
    """Keep ordinary Entity text out of the advanced replacement boundary."""

    localization_root = PIHC3_ROOT / "src/modules/localization"
    assert [path.name for path in localization_root.iterdir() if path.is_dir()] == ["LOCALIZATION_REPLACEMENTS - 全局本地化覆盖"]
    sources = sorted(LOCALIZATION_REPLACEMENT_ROOT.rglob("*.yml"))
    assert len(sources) == 141
    assert all(path.relative_to(LOCALIZATION_REPLACEMENT_ROOT).parts[0] == "replace" for path in sources)


def test_pihc3_direct_source_folders_use_id_and_preferred_localization() -> None:
    """Keep the physical authoring tree readable without opening metadata."""

    source_root = PIHC3_ROOT / "src"
    source_folders = sorted(
        child
        for kind in ("modules", "collections")
        for family in (source_root / kind).iterdir()
        if family.is_dir()
        for child in family.iterdir()
        if child.is_dir()
    )
    assert source_folders
    browser = Project.load(PIHC3_ROOT).browser()
    browser_items = {str(item["relative_path"]): item for item in browser["items"] if isinstance(item, dict) and isinstance(item.get("relative_path"), str)}
    malformed: list[str] = []
    retired_component_ids: list[str] = []
    mislabeled: list[str] = []
    for folder in source_folders:
        object_id, separator, title = folder.name.partition(" - ")
        if separator != " - " or not object_id.strip() or not title.strip():
            malformed.append(folder.relative_to(source_root).as_posix())
            continue
        if FORBIDDEN_OBJECT_ID_PATTERN.search(object_id):
            retired_component_ids.append(folder.relative_to(source_root).as_posix())
        if folder.parent.parent.name == "collections":
            expected_title = _collection_title(folder, object_id)
            if title != expected_title:
                mislabeled.append(f"{folder.relative_to(source_root).as_posix()} " f"(expected {expected_title!r})")
            continue
        item = browser_items.get(f"src/{folder.relative_to(source_root).as_posix()}")
        localized_title = _preferred_localized_title(item) if isinstance(item, dict) else None
        if localized_title is None:
            continue
        expected_title = portable_authoring_title(
            localized_title,
            object_id=object_id,
        )
        if title != expected_title:
            mislabeled.append(f"{folder.relative_to(source_root).as_posix()} " f"(expected {expected_title!r})")
    assert malformed == []
    assert retired_component_ids == []
    assert mislabeled == []


def test_pihc3_country_localization_has_one_module_owned_source() -> None:
    """Keep country text beside the country instead of in the shared bundle."""

    modules_root = PIHC3_ROOT / "src/modules"
    country_root = modules_root / "country"
    shared_root = LOCALIZATION_REPLACEMENT_ROOT
    module_roots = sorted(
        (path for path in country_root.iterdir() if path.is_dir()),
        key=lambda path: path.name,
    )
    assert len(module_roots) == 67
    assert not tuple(shared_root.glob("*/COUNTRY_C*_l_*.yml"))

    digest = sha256()
    identities: set[tuple[str, str]] = set()
    total_bytes = 0
    for module_root in module_roots:
        object_id, folder_title = module_root.name.split(" - ", 1)
        source = module_root / "main.loc"
        payload = source.read_bytes()
        document = parse_source(payload.decode("utf-8-sig"))
        assert document.issues == ()
        localized = {(entry.language, entry.key): entry.text for entry in document.entries}
        assert len(localized) == len(document.entries)
        assert identities.isdisjoint(localized)
        identities.update(localized)
        preferred_title = localized.get(
            ("l_simp_chinese", f"{object_id}_DEF"),
            localized[("l_simp_chinese", object_id)],
        )
        if preferred_title:
            assert folder_title == portable_authoring_title(
                preferred_title,
                object_id=object_id,
            )
        else:
            assert folder_title

        relative_path = source.relative_to(PIHC3_ROOT).as_posix().encode()
        digest.update(len(relative_path).to_bytes(8, "big"))
        digest.update(relative_path)
        digest.update(len(payload).to_bytes(8, "big"))
        digest.update(payload)
        total_bytes += len(payload)

    assert len(identities) == 1_250
    assert total_bytes == 209_131
    assert digest.hexdigest() == ("4d5844ca97b0dd2ce24b77106c3652f97f5033e636d137cbc7338f340949f0c1")

    discovery = Project.load(PIHC3_ROOT).discover_modules(family="country")
    assert discovery.diagnostics == ()
    assert len(discovery.modules) == 67
    assert all(module.payload.source_slots["loc"] == ("main.loc",) for module in discovery.modules)


def test_pihc3_focus_localization_has_one_module_owned_source() -> None:
    """Keep focus text with its node and tree-wide text with its collection."""

    modules_root = PIHC3_ROOT / "src/modules"
    focus_root = modules_root / "focus"
    shared_root = LOCALIZATION_REPLACEMENT_ROOT
    module_roots = sorted(
        (path for path in focus_root.iterdir() if path.is_dir()),
        key=lambda path: path.name,
    )
    assert len(module_roots) == 738
    assert not tuple(shared_root.glob("*/FOCUS_*_l_*.yml"))

    digest = sha256()
    identities: set[tuple[str, str]] = set()
    total_bytes = 0
    for module_root in module_roots:
        object_id, folder_title = module_root.name.split(" - ", 1)
        source = module_root / "main.loc"
        payload = source.read_bytes()
        document = parse_source(payload.decode("utf-8-sig"))
        assert document.issues == ()
        localized = {(entry.language, entry.key): entry.text for entry in document.entries}
        assert len(localized) == len(document.entries)
        assert identities.isdisjoint(localized)
        identities.update(localized)
        preferred_title = localized[("l_simp_chinese", object_id)]
        assert folder_title == portable_authoring_title(
            preferred_title,
            object_id=object_id,
        )

        relative_path = source.relative_to(PIHC3_ROOT).as_posix().encode()
        digest.update(len(relative_path).to_bytes(8, "big"))
        digest.update(relative_path)
        digest.update(len(payload).to_bytes(8, "big"))
        digest.update(payload)
        total_bytes += len(payload)

    assert len(identities) == 3_338
    assert total_bytes == 637_004
    assert digest.hexdigest() == ("cc569b0d2d89d40a760c7ddb621190598f59802b8f82c9b88376ec89e9f029de")

    discovery = Project.load(PIHC3_ROOT).discover_modules(family="focus")
    assert discovery.diagnostics == ()
    assert len(discovery.modules) == 738
    assert all(module.payload.source_slots["loc"] == ("main.loc",) for module in discovery.modules)


def test_pihc3_state_localization_has_one_module_owned_source() -> None:
    """Keep each state name beside its definition while aggregating at build time."""

    from paradev.pdx import PDXBlock

    modules_root = PIHC3_ROOT / "src/modules"
    state_root = modules_root / "state"
    shared_root = LOCALIZATION_REPLACEMENT_ROOT
    module_roots = sorted(
        (path for path in state_root.iterdir() if path.is_dir()),
        key=lambda path: int(path.name.split(" - ", 1)[0]),
    )
    assert len(module_roots) == 902
    assert not tuple(shared_root.glob("*/state_names_l_*.yml"))
    assert not tuple(shared_root.glob("*/victory_points_l_*.yml"))

    digest = sha256()
    identities: set[tuple[str, str]] = set()
    total_bytes = 0
    for module_root in module_roots:
        object_id, folder_title = module_root.name.split(" - ", 1)
        source = module_root / "main.loc"
        payload = source.read_bytes()
        document = parse_source(payload.decode("utf-8-sig"))
        assert document.issues == ()
        localized = {(entry.language, entry.key): entry.text for entry in document.entries}
        expected_key = f"STATE_{object_id}"
        assert {
            ("l_english", expected_key),
            ("l_russian", expected_key),
            ("l_simp_chinese", expected_key),
        } <= set(localized)
        assert all(key == expected_key or key.startswith("VICTORY_POINTS_") for _language, key in localized)
        keys = {key for _language, key in localized}
        assert all({language for language, localized_key in localized if localized_key == key} == {"l_english", "l_russian", "l_simp_chinese"} for key in keys)
        assert identities.isdisjoint(localized)
        identities.update(localized)
        assert folder_title == portable_authoring_title(
            localized[("l_simp_chinese", expected_key)],
            object_id=object_id,
        )

        relative_path = source.relative_to(PIHC3_ROOT).as_posix().encode()
        digest.update(len(relative_path).to_bytes(8, "big"))
        digest.update(relative_path)
        digest.update(len(payload).to_bytes(8, "big"))
        digest.update(payload)
        total_bytes += len(payload)

    assert len(identities) == 5_436
    assert total_bytes == 183_413
    assert digest.hexdigest() == ("701f4714084e22397c54a2fecd0f994ca7e4191ba54cd3b42bdad8e1672f556e")

    discovery = Project.load(PIHC3_ROOT).discover_modules(family="state")
    assert discovery.diagnostics == ()
    assert len(discovery.modules) == 902
    assert all(module.payload.source_slots["loc"] == ("main.loc",) for module in discovery.modules)
    for module in discovery.modules:
        expected_victory_points: set[str] = set()
        for root_entry in module.payload.pdx_sources[0].block.entries:
            if root_entry.key_str != "state" or not isinstance(root_entry.val, PDXBlock):
                continue
            for state_entry in root_entry.val.entries:
                if state_entry.key_str != "history" or not isinstance(state_entry.val, PDXBlock):
                    continue
                for history_entry in state_entry.val.entries:
                    if history_entry.key_str != "victory_points" or not isinstance(history_entry.val, PDXBlock):
                        continue
                    values = [entry.key_str for entry in history_entry.val.entries]
                    assert len(values) % 2 == 0
                    expected_victory_points.update(f"VICTORY_POINTS_{province}" for province in values[::2])
        assert {entry.key for entry in module.payload.loc_entries if entry.key.startswith("VICTORY_POINTS_")} == expected_victory_points


def test_pihc3_state_lore_uses_state_titles_and_only_compact_sources() -> None:
    """Keep lore text human-named while generating aggregate boilerplate."""

    modules_root = PIHC3_ROOT / "src/modules"
    lore_roots = sorted(path for path in (modules_root / "state_lore").iterdir() if path.is_dir())
    state_titles = {path.name.split(" - ", 1)[0]: path.name.split(" - ", 1)[1] for path in (modules_root / "state").iterdir() if path.is_dir()}
    variant_ids: set[str] = set()
    source_count = 0
    for module_root in lore_roots:
        object_id, title = module_root.name.split(" - ", 1)
        state_id = object_id.removeprefix("STATE_LORE_")
        files = {path.name for path in module_root.iterdir() if path.is_file()}
        expected = {"main.loc"}
        if (module_root / "variants.pdx").is_file():
            expected.add("variants.pdx")
            variant_ids.add(object_id)
        assert title == state_titles[state_id]
        assert files == expected
        source_count += len(files)

    assert len(lore_roots) == 79
    assert source_count == 81
    assert variant_ids == {"STATE_LORE_217", "STATE_LORE_772"}

    project = Project.load(PIHC3_ROOT)
    discovery = project.discover_modules(family="state_lore")
    assert discovery.diagnostics == ()
    assert len(discovery.modules) == 79
    assert all(module.payload.source_slots["loc"] == ("main.loc",) for module in discovery.modules)
    assert {module.module_id for module in discovery.modules if module.payload.source_slots.get("variants", ())} == {
        "state_lore/STATE_LORE_217",
        "state_lore/STATE_LORE_772",
    }
    browser = project.browser(
        family="state_lore",
        module_id="STATE_LORE_146",
    )
    assert [(item["module_id"], item["title"]) for item in browser["items"]] == [("state_lore/STATE_LORE_146", "偶链群岛")]


def test_pihc3_strategic_region_localization_has_one_module_owned_source() -> None:
    """Keep region names beside definitions and remove orphan placeholders."""

    modules_root = PIHC3_ROOT / "src/modules"
    region_root = modules_root / "strategic_region"
    shared_root = LOCALIZATION_REPLACEMENT_ROOT
    module_roots = sorted(
        (path for path in region_root.iterdir() if path.is_dir()),
        key=lambda path: int(path.name.split(" - ", 1)[0]),
    )
    assert len(module_roots) == 330
    assert not tuple(shared_root.glob("*/strategic_region_names_l_*.yml"))

    digest = sha256()
    identities: set[tuple[str, str]] = set()
    total_bytes = 0
    for module_root in module_roots:
        object_id, folder_title = module_root.name.split(" - ", 1)
        source = module_root / "main.loc"
        payload = source.read_bytes()
        document = parse_source(payload.decode("utf-8-sig"))
        assert document.issues == ()
        localized = {(entry.language, entry.key): entry.text for entry in document.entries}
        expected_key = f"STRATEGICREGION_{object_id}"
        assert set(localized) == {
            ("l_english", expected_key),
            ("l_russian", expected_key),
            ("l_simp_chinese", expected_key),
        }
        assert identities.isdisjoint(localized)
        identities.update(localized)
        assert folder_title == portable_authoring_title(
            localized[("l_simp_chinese", expected_key)],
            object_id=object_id,
        )

        relative_path = source.relative_to(PIHC3_ROOT).as_posix().encode()
        digest.update(len(relative_path).to_bytes(8, "big"))
        digest.update(relative_path)
        digest.update(len(payload).to_bytes(8, "big"))
        digest.update(payload)
        total_bytes += len(payload)

    assert len(identities) == 990
    assert total_bytes == 41_907
    assert digest.hexdigest() == ("82d9f34710b50a691b77b37741611bf1ace33645fc72edb9ff406e060ed5213d")

    discovery = Project.load(PIHC3_ROOT).discover_modules(family="strategic_region")
    assert discovery.diagnostics == ()
    assert len(discovery.modules) == 330
    assert all(module.payload.source_slots["loc"] == ("main.loc",) for module in discovery.modules)
