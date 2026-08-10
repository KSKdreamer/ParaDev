"""Normalize project authoring templates to a low-metadata folder contract."""

from __future__ import annotations

import argparse
from collections.abc import Mapping
from os import PathLike

from heavenbase.utils import (
    exists_file,
    get_file_name,
    list_dirs,
    load_yaml,
    pj,
    save_yaml,
)

CANONICAL_DIRECTORY = "{object_id} - {title}"
HIDDEN_METADATA_PATH = ".paradev/meta.yaml"
TITLE_LINE = "title: {title}\n"


def normalize_project_authoring_templates(
    project_root: str | PathLike[str],
) -> tuple[str, ...]:
    """Normalize project templates to titled folders and minimal visible metadata.

    Args:
        project_root (str | PathLike[str]): ParaDev project containing an
            `extensions` directory.

    Returns:
        tuple[str, ...]: Extension descriptors changed by the normalization.

    Raises:
        TypeError: If a template descriptor has an invalid shape.
        ValueError: If metadata cannot be classified safely.
    """

    extensions_root = pj(project_root, "extensions", abs=True)
    written: list[str] = []
    extension_roots = tuple(path for path in list_dirs(extensions_root, abs=True) if not get_file_name(path).startswith("."))
    for extension_root in extension_roots:
        descriptor_path = _descriptor_path(extension_root)
        descriptor = _mapping(
            load_yaml(str(descriptor_path), strict=True),
            str(descriptor_path),
        )
        items = descriptor.get("items")
        if not isinstance(items, list):
            raise TypeError(f"{descriptor_path} items must be a list")
        changed = False
        for item in items:
            if not isinstance(item, dict):
                continue
            if item.get("kind") != "paradev_authoring_template":
                continue
            meta = _mapping(
                item.get("meta"),
                f"{descriptor_path} template meta",
            )
            definition = _mapping(
                meta.get("definition"),
                f"{descriptor_path} template definition",
            )
            declaration = _mapping(
                definition.get("declaration"),
                f"{descriptor_path} template declaration",
            )
            if declaration.get("directory") != CANONICAL_DIRECTORY:
                declaration["directory"] = CANONICAL_DIRECTORY
                changed = True
            if _minimize_template_metadata(
                declaration,
                descriptor_path=descriptor_path,
            ):
                changed = True
            definition["declaration"] = declaration
            meta["definition"] = definition
            item["meta"] = meta
        if changed:
            save_yaml(descriptor, str(descriptor_path))
            written.append(descriptor_path)
    return tuple(written)


def _descriptor_path(extension_root: str) -> str:
    visible = pj(extension_root, "meta.yaml")
    hidden = pj(extension_root, HIDDEN_METADATA_PATH)
    if exists_file(visible) and exists_file(hidden):
        raise ValueError(f"{extension_root} contains both meta.yaml and .paradev/meta.yaml.")
    if exists_file(hidden):
        return hidden
    if exists_file(visible):
        return visible
    raise FileNotFoundError(f"{extension_root} has no project extension descriptor.")


def _minimize_template_metadata(
    declaration: dict[str, object],
    *,
    descriptor_path: str,
) -> bool:
    files = _mapping(
        declaration.get("files"),
        f"{descriptor_path} template files",
    )
    raw_metadata = files.get("meta.yaml")
    if raw_metadata is None:
        return False
    if not isinstance(raw_metadata, str):
        raise TypeError(f"{descriptor_path} template meta.yaml content must be text")
    normalized = raw_metadata.replace("\r\n", "\n")
    if not normalized.startswith(TITLE_LINE):
        if normalized.startswith(("collection:", "comment:")):
            return False
        raise ValueError(f"{descriptor_path} template metadata does not begin with the " "folder-derived title")
    authored = normalized.removeprefix(TITLE_LINE)
    files.pop("meta.yaml")
    if authored.strip():
        if authored.startswith("collection:"):
            files["meta.yaml"] = authored
        elif authored.startswith("settings:"):
            system_files = _mapping(
                declaration.get("system_files", {}),
                f"{descriptor_path} template system_files",
            )
            existing = system_files.get(HIDDEN_METADATA_PATH)
            if existing not in (None, authored):
                raise ValueError(f"{descriptor_path} already defines conflicting hidden " "module metadata")
            system_files[HIDDEN_METADATA_PATH] = authored
            declaration["system_files"] = system_files
        else:
            raise ValueError(f"{descriptor_path} template metadata contains unsupported visible keys")
    if not files:
        raise ValueError(
            f"{descriptor_path} template must declare an authored source file; " "ParaDev does not create visible metadata as a source placeholder"
        )
    declaration["files"] = files
    return True


def _mapping(value: object, label: str) -> dict[str, object]:
    if not isinstance(value, Mapping):
        raise TypeError(f"{label} must be a mapping")
    return {str(key): item for key, item in value.items()}


def main() -> int:
    """Run the project-template normalization."""

    parser = argparse.ArgumentParser()
    parser.add_argument("project_root")
    args = parser.parse_args()
    written = normalize_project_authoring_templates(args.project_root)
    print(f"Normalized {len(written)} project extension descriptors.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
