"""Move central ParaDev family/template declarations into HeavenBase modules."""

from __future__ import annotations

import argparse
from collections.abc import Mapping
from pathlib import Path

from heavenbase.utils import load_yaml, save_txt, save_yaml, sha256hash

HIDDEN_DESCRIPTOR = Path(".paradev/meta.yaml")


def migrate_manifest_extensions(project_root: Path) -> tuple[Path, ...]:
    """Extract manifest families and templates into co-located module folders.

    Args:
        project_root: ParaDev project containing ``paradev.yaml``.

    Returns:
        HeavenBase descriptors created or updated by the migration.

    Raises:
        TypeError: If central extension declarations have invalid shapes.
        ValueError: If a generated record would duplicate an existing one.
    """

    root = project_root.expanduser().resolve()
    manifest_path = root / "paradev.yaml"
    manifest = _mapping(load_yaml(str(manifest_path), strict=True), str(manifest_path))
    families = _mapping(manifest.pop("families", {}), "families")
    templates = _mapping(manifest.pop("templates", {}), "templates")
    if not families and not templates:
        return ()

    templates_by_family: dict[str, list[tuple[str, dict[str, object]]]] = {}
    for template_id, raw_declaration in templates.items():
        declaration = _mapping(raw_declaration, f"templates.{template_id}")
        family = declaration.get("family")
        if not isinstance(family, str) or not family.strip():
            raise TypeError(f"templates.{template_id}.family must be a non-empty string")
        templates_by_family.setdefault(family.strip(), []).append((str(template_id), declaration))

    version = str(manifest.get("mod_version") or "0.1.0")
    project_id = _coordinate_part(str(manifest.get("project_id") or root.name))
    family_names = sorted({str(family) for family in families} | set(templates_by_family))
    written: list[Path] = []
    for family in family_names:
        module_root = root / "extensions" / family
        visible_descriptor = module_root / "meta.yaml"
        hidden_descriptor = module_root / HIDDEN_DESCRIPTOR
        if visible_descriptor.is_file() and hidden_descriptor.is_file():
            raise ValueError(f"{module_root} contains both meta.yaml and .paradev/meta.yaml.")
        descriptor_path = visible_descriptor if visible_descriptor.is_file() else hidden_descriptor
        created = not descriptor_path.exists()
        if created:
            module_root.mkdir(parents=True, exist_ok=False)
            descriptor_path.parent.mkdir(parents=True, exist_ok=True)
            save_txt(
                f'"""Registry declarations for the PIHC3 {family} module type."""\n',
                str(module_root / "__init__.py"),
                encoding="utf-8",
            )
            descriptor = _new_descriptor(
                project_id=project_id,
                family=family,
                version=version,
            )
        else:
            descriptor = _mapping(
                load_yaml(str(descriptor_path), strict=True),
                str(descriptor_path),
            )
        items = descriptor.get("items")
        if not isinstance(items, list):
            raise TypeError(f"{descriptor_path} items must be a list")
        existing_keys = {(item.get("kind"), item.get("identifier")) for item in items if isinstance(item, Mapping)}
        family_declaration = families.get(family)
        if family_declaration is not None:
            key = ("paradev_build_family", f"pihc3-{_identifier_part(family)}")
            if key in existing_keys:
                raise ValueError(f"{descriptor_path} already declares {key!r}")
            items.append(
                _family_item(
                    family,
                    _mapping(family_declaration, f"families.{family}"),
                    version=version,
                )
            )
            existing_keys.add(key)
        for template_id, declaration in sorted(
            templates_by_family.get(family, ()),
            key=lambda item: item[0],
        ):
            item = _template_item(template_id, declaration, version=version)
            key = (item["kind"], item["identifier"])
            if key in existing_keys:
                raise ValueError(f"{descriptor_path} already declares {key!r}")
            items.append(item)
            existing_keys.add(key)
        save_yaml(descriptor, str(descriptor_path))
        written.append(descriptor_path)

    save_yaml(manifest, str(manifest_path))
    return tuple(written)


def _new_descriptor(
    *,
    project_id: str,
    family: str,
    version: str,
) -> dict[str, object]:
    slug = _identifier_part(family)
    entity_id = f"pihc3-{slug}-module"
    extension_id = f"pihc3-{slug}"
    title = family.replace("_", " ").title()
    return {
        "manifest_version": 2,
        "coordinate": f"paradev-projects/{project_id}/{family}",
        "version": version,
        "compatibility": {
            "heavenbase": {
                "min": "0.1.2.1",
                "before": "0.1.3.0",
            }
        },
        "bundle": extension_id,
        "items": [
            {
                "kind": "entity",
                "identifier": entity_id,
                "name": f"PIHC3 {title} Module",
                "desc": f"Project-owned {family} source module record.",
                "source": "inline",
                "target": "definition",
                "active": True,
                "meta": {
                    "schema_version": 1,
                    "version": version,
                    "definition": _module_entity_schema(
                        entity_id=entity_id,
                        name=f"PIHC3 {title} Module",
                        family=family,
                    ),
                },
            },
            {
                "kind": "extension",
                "identifier": extension_id,
                "name": f"PIHC3 {title}",
                "desc": f"PIHC3 {family} module persistence and authoring.",
                "source": "inline",
                "target": "definition",
                "active": True,
                "meta": {
                    "schema_version": 1,
                    "version": version,
                    "dependencies": [f"entity:{entity_id}"],
                    "definition": {
                        "identifier": extension_id,
                        "name": f"PIHC3 {title}",
                        "version": version,
                        "desc": f"PIHC3 {family} module persistence and authoring.",
                        "required": False,
                        "requires": [],
                        "entities": [entity_id],
                        "meta": {
                            "project": "PIHC3",
                            "family": family,
                        },
                        "setup": None,
                        "api": None,
                        "api_name": None,
                    },
                },
            },
        ],
    }


def _module_entity_schema(
    *,
    entity_id: str,
    name: str,
    family: str,
) -> dict[str, object]:
    return {
        "entity_id": entity_id,
        "name": name,
        "desc": f"Persistent authoring record for one PIHC3 {family} source module.",
        "tags": ["paradev", "pihc3", family],
        "fields": {
            "module_id": {
                "name": "module_id",
                "dtype": {
                    "type": "short-text",
                    "max_chars": 255,
                },
                "pk": False,
                "required": False,
                "default": "",
                "has_default": True,
                "desc": "Stable ParaDev module identifier.",
                "tags": [],
                "examples": [],
            },
            "data": {
                "name": "data",
                "dtype": {"type": "json"},
                "pk": False,
                "required": False,
                "default": {},
                "has_default": True,
                "desc": "Structured metadata, localization, and resource references.",
                "tags": [],
                "examples": [],
            },
        },
    }


def _family_item(
    family: str,
    declaration: Mapping[str, object],
    *,
    version: str,
) -> dict[str, object]:
    slug = _identifier_part(family)
    return {
        "kind": "paradev_build_family",
        "identifier": f"pihc3-{slug}",
        "name": f"PIHC3 {family.replace('_', ' ').title()} Compiler",
        "desc": f"Registry-backed source slots and compiler hooks for {family}.",
        "source": "inline",
        "target": "definition",
        "active": True,
        "meta": {
            "schema_version": 1,
            "version": version,
            "dependencies": [f"extension:pihc3-{slug}"],
            "definition": {
                "family": family,
                "declaration": dict(declaration),
            },
        },
    }


def _template_item(
    template_id: str,
    declaration: Mapping[str, object],
    *,
    version: str,
) -> dict[str, object]:
    digest = sha256hash(template_id)[:16]
    return {
        "kind": "paradev_authoring_template",
        "identifier": f"pihc3-template-{digest}",
        "name": str(declaration.get("title") or template_id),
        "desc": f"PIHC3 authoring template {template_id}.",
        "source": "inline",
        "target": "definition",
        "active": True,
        "meta": {
            "schema_version": 1,
            "version": version,
            "definition": {
                "template_id": template_id,
                "declaration": dict(declaration),
            },
        },
    }


def _mapping(value: object, label: str) -> dict[str, object]:
    if not isinstance(value, Mapping):
        raise TypeError(f"{label} must be a mapping")
    return {str(key): item for key, item in value.items()}


def _identifier_part(value: str) -> str:
    clean = value.strip().lower().replace("_", "-")
    if not clean or any(not (char.isalnum() or char == "-") for char in clean):
        raise ValueError(f"Cannot normalize module identifier part {value!r}")
    return clean


def _coordinate_part(value: str) -> str:
    return _identifier_part(value).strip("-")


def main() -> int:
    """Run the manifest-to-module migration."""

    parser = argparse.ArgumentParser()
    parser.add_argument("project_root", type=Path)
    args = parser.parse_args()
    written = migrate_manifest_extensions(args.project_root)
    print(f"Migrated {len(written)} extension descriptors.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
