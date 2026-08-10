"""Materialize project Entity and compiler records as project-local code."""

from __future__ import annotations

import argparse
import json
from collections.abc import Mapping
from pathlib import Path

from heavenbase.utils import load_yaml, save_txt, save_yaml

from paradev.build import DEFAULT_MODULE_SLOTS

HIDDEN_DESCRIPTOR = Path(".paradev/meta.yaml")


def materialize_project_extension_entities(project_root: Path) -> tuple[Path, ...]:
    """Replace inline module Entity schemas with co-located ``hb.Entity`` classes.

    Args:
        project_root: ParaDev project containing an ``extensions`` directory.

    Returns:
        Extension module files whose inline Entity record was materialized.

    Raises:
        TypeError: If an extension descriptor has an invalid shape.
        ValueError: If a declarative Entity cannot be matched to a build family.
    """

    root = project_root.expanduser().resolve()
    extensions_root = root / "extensions"
    written: list[Path] = []
    for extension_root in sorted(path for path in extensions_root.iterdir() if path.is_dir()):
        if extension_root.name.startswith("."):
            continue
        descriptor_path = _descriptor_path(extension_root)
        descriptor = _mapping(
            load_yaml(str(descriptor_path), strict=True),
            str(descriptor_path),
        )
        items = descriptor.get("items")
        if not isinstance(items, list):
            raise TypeError(f"{descriptor_path} items must be a list")
        entity_items = [item for item in items if isinstance(item, dict) and item.get("kind") == "entity"]
        if not entity_items:
            continue
        if len(entity_items) != 1:
            raise ValueError(f"{descriptor_path} must declare exactly one Entity record")
        entity_item = entity_items[0]
        if entity_item.get("source") == "path":
            entity_meta = _mapping(
                entity_item.get("meta"),
                f"{descriptor_path} Entity meta",
            )
            if "definition" in entity_meta:
                entity_meta.pop("definition")
                entity_item["meta"] = entity_meta
                save_yaml(descriptor, str(descriptor_path))
            continue
        if entity_item.get("source") != "inline":
            raise ValueError(f"{descriptor_path} uses unsupported Entity source " f"{entity_item.get('source')!r}")

        family_id, source_slots = _build_family_contract(
            items,
            descriptor_path=descriptor_path,
        )
        entity_id = _required_text(
            entity_item.get("identifier"),
            f"{descriptor_path} Entity identifier",
        )
        class_name = _entity_class_name(family_id)
        module_path = extension_root / "__init__.py"
        save_txt(
            _entity_module_source(
                class_name=class_name,
                entity_id=entity_id,
                family_id=family_id,
                source_slots=source_slots,
            ),
            str(module_path),
            encoding="utf-8",
        )

        entity_item["source"] = "path"
        entity_item["target"] = {
            "module": None,
            "qualname": class_name,
        }
        meta = _mapping(
            entity_item.get("meta"),
            f"{descriptor_path} Entity meta",
        )
        meta.pop("definition", None)
        entity_item["meta"] = meta
        save_yaml(descriptor, str(descriptor_path))
        written.append(module_path)
    return tuple(written)


def materialize_project_extension_build_families(
    project_root: Path,
) -> tuple[Path, ...]:
    """Move inline simple-source compilers beside their project Entity classes.

    The generated compiler references the Entity's ``resource_slots`` instead
    of copying slot declarations. This keeps resource discovery, authoring, and
    compilation on one Registry-loaded contract.
    """

    root = project_root.expanduser().resolve()
    extensions_root = root / "extensions"
    written: list[Path] = []
    for extension_root in sorted(path for path in extensions_root.iterdir() if path.is_dir()):
        if extension_root.name.startswith("."):
            continue
        descriptor_path = _descriptor_path(extension_root)
        descriptor = _mapping(
            load_yaml(str(descriptor_path), strict=True),
            str(descriptor_path),
        )
        items = descriptor.get("items")
        if not isinstance(items, list):
            raise TypeError(f"{descriptor_path} items must be a list")
        family_items = [item for item in items if isinstance(item, dict) and item.get("kind") == "paradev_build_family"]
        if not family_items:
            continue
        if len(family_items) != 1:
            raise ValueError(f"{descriptor_path} must declare exactly one build-family record")
        family_item = family_items[0]
        if family_item.get("source") == "path":
            family_meta = _mapping(
                family_item.get("meta"),
                f"{descriptor_path} build-family meta",
            )
            if "definition" in family_meta:
                family_meta.pop("definition")
                family_item["meta"] = family_meta
                save_yaml(descriptor, str(descriptor_path))
            continue
        if family_item.get("source") != "inline":
            raise ValueError(f"{descriptor_path} uses unsupported build-family source " f"{family_item.get('source')!r}")

        family_meta = _mapping(
            family_item.get("meta"),
            f"{descriptor_path} build-family meta",
        )
        definition = _mapping(
            family_meta.get("definition"),
            f"{descriptor_path} build-family definition",
        )
        family_id = _required_text(
            definition.get("family"),
            f"{descriptor_path} build-family id",
        )
        declaration = _mapping(
            definition.get("declaration"),
            f"{descriptor_path} build-family declaration",
        )
        kind = declaration.get("kind", "simple_source")
        if kind != "simple_source":
            raise ValueError(f"{descriptor_path} build-family kind {kind!r} must be " "materialized by its specialized compiler")
        entity_class = _entity_target_class(items, descriptor_path=descriptor_path)
        module_path = extension_root / "__init__.py"
        module_source = module_path.read_text(encoding="utf-8")
        save_txt(
            _append_build_family_source(
                module_source,
                class_name=entity_class,
                family_id=family_id,
                declaration=declaration,
            ),
            str(module_path),
            encoding="utf-8",
        )

        family_item["source"] = "path"
        family_item["target"] = {
            "module": None,
            "qualname": "build_family",
        }
        family_meta.pop("definition", None)
        family_item["meta"] = family_meta
        save_yaml(descriptor, str(descriptor_path))
        written.append(module_path)
    return tuple(written)


def _descriptor_path(extension_root: Path) -> Path:
    visible = extension_root / "meta.yaml"
    hidden = extension_root / HIDDEN_DESCRIPTOR
    if visible.is_file() and hidden.is_file():
        raise ValueError(f"{extension_root} contains both meta.yaml and .paradev/meta.yaml.")
    if hidden.is_file():
        return hidden
    if visible.is_file():
        return visible
    raise FileNotFoundError(f"{extension_root} has no project extension descriptor.")


def _build_family_contract(
    items: list[object],
    *,
    descriptor_path: Path,
) -> tuple[str, tuple[dict[str, object], ...]]:
    family_items = [item for item in items if isinstance(item, Mapping) and item.get("kind") == "paradev_build_family"]
    if not family_items:
        extension_items = [item for item in items if isinstance(item, Mapping) and item.get("kind") == "extension"]
        if len(extension_items) != 1:
            raise ValueError(f"{descriptor_path} must declare one extension when it has no " "project build-family override")
        extension_meta = _mapping(
            extension_items[0].get("meta"),
            f"{descriptor_path} extension meta",
        )
        extension_definition = _mapping(
            extension_meta.get("definition"),
            f"{descriptor_path} extension definition",
        )
        extension_data = _mapping(
            extension_definition.get("meta"),
            f"{descriptor_path} extension data",
        )
        family_id = _required_text(
            extension_data.get("family"),
            f"{descriptor_path} extension family",
        )
        slots = tuple(
            {
                "name": slot.name,
                "match": slot.match,
                "required": slot.required,
                "many": slot.many,
                "regex": slot.regex,
                "kind": slot.kind,
                "shared": slot.shared,
            }
            for slot in DEFAULT_MODULE_SLOTS
        )
        return family_id, slots
    if len(family_items) != 1:
        raise ValueError(f"{descriptor_path} must declare exactly one build-family record")
    family_meta = _mapping(
        family_items[0].get("meta"),
        f"{descriptor_path} build-family meta",
    )
    definition = _mapping(
        family_meta.get("definition"),
        f"{descriptor_path} build-family definition",
    )
    family_id = _required_text(
        definition.get("family"),
        f"{descriptor_path} build-family id",
    )
    declaration = _mapping(
        definition.get("declaration"),
        f"{descriptor_path} build-family declaration",
    )
    raw_slots = declaration.get("source_slots", ())
    if not isinstance(raw_slots, (list, tuple)):
        raise TypeError(f"{descriptor_path} build-family source_slots must be a list")
    slots = tuple(_mapping(slot, f"{descriptor_path} source slot") for slot in raw_slots)
    return family_id, slots


def _entity_target_class(
    items: list[object],
    *,
    descriptor_path: Path,
) -> str:
    entity_items = [item for item in items if isinstance(item, Mapping) and item.get("kind") == "entity"]
    if len(entity_items) != 1:
        raise ValueError(f"{descriptor_path} must declare exactly one Entity record")
    entity = entity_items[0]
    if entity.get("source") != "path":
        raise ValueError(f"{descriptor_path} Entity must be materialized before its compiler")
    target = _mapping(
        entity.get("target"),
        f"{descriptor_path} Entity target",
    )
    return _required_text(
        target.get("qualname"),
        f"{descriptor_path} Entity target qualname",
    )


def _append_build_family_source(
    module_source: str,
    *,
    class_name: str,
    family_id: str,
    declaration: dict[str, object],
) -> str:
    import_line = "from paradev.build import Slot\n"
    if import_line not in module_source:
        raise ValueError(f"{family_id} Entity module must import Slot from paradev.build")
    all_line = f'__all__ = ["{class_name}"]'
    if all_line not in module_source:
        raise ValueError(f"{family_id} Entity module has an unexpected __all__")
    module_source = module_source.replace(
        import_line,
        "from paradev.build import SimpleSourceFamily, Slot\n",
        1,
    )
    family_source = _simple_source_family_function(
        class_name=class_name,
        declaration=declaration,
    )
    return module_source.replace(
        f"\n\n{all_line}\n",
        f'{family_source}\n\n__all__ = ["{class_name}", "build_family"]\n',
        1,
    )


def _simple_source_family_function(
    *,
    class_name: str,
    declaration: dict[str, object],
) -> str:
    supported_keys = {
        "kind",
        "required_loc_keys",
        "source_slots",
        "sprite_slots",
        "templates",
        "title_loc_keys",
        "visible",
    }
    unsupported_keys = sorted(set(declaration).difference(supported_keys))
    if unsupported_keys:
        raise ValueError(f"{class_name} compiler uses unsupported declarative keys: " f"{unsupported_keys!r}")
    templates = _mapping(
        declaration.get("templates"),
        f"{class_name} compiler templates",
    )
    argument_lines = [
        f"        family={class_name}.family,",
        f"        source_slots={class_name}.resource_slots,",
    ]
    template_args = {
        "pdx": "pdx_path_template",
        "loc": "loc_path_template",
        "copy": "copy_path_template",
        "sprite_gfx": "sprite_gfx_path_template",
        "sprite_name": "sprite_name_template",
    }
    for template_name, argument_name in template_args.items():
        if template_name in templates:
            argument_lines.append(f"        {argument_name}={_python_literal(templates[template_name])},")
    for declaration_name in (
        "required_loc_keys",
        "title_loc_keys",
        "sprite_slots",
    ):
        if declaration_name in declaration:
            argument_lines.append(f"        {declaration_name}=" f"{_python_tuple(declaration[declaration_name], declaration_name)},")
    if declaration.get("visible") is False:
        argument_lines.append("        visible=False,")
    arguments = "\n".join(argument_lines)
    return (
        "\n\n\ndef build_family() -> SimpleSourceFamily:\n"
        '    """Return the Registry compiler owned by this Entity extension."""\n'
        "\n"
        "    return SimpleSourceFamily(\n"
        f"{arguments}\n"
        "    )\n"
    )


def _python_tuple(value: object, label: str) -> str:
    if not isinstance(value, (list, tuple)):
        raise TypeError(f"{label} must be a list")
    return repr(tuple(value))


def _entity_module_source(
    *,
    class_name: str,
    entity_id: str,
    family_id: str,
    source_slots: tuple[dict[str, object], ...],
) -> str:
    title = family_id.replace("_", " ")
    slot_lines = _slot_source(source_slots)
    return (
        f'"""PIHC3 {title} Entity extension."""\n'
        "\n"
        "from __future__ import annotations\n"
        "\n"
        "import heavenbase as hb\n"
        "\n"
        "from paradev.build import Slot\n"
        "\n"
        "\n"
        f"class {class_name}(hb.Entity):\n"
        f'    """One independently editable PIHC3 {title} module."""\n'
        "\n"
        f"    identifier = {_python_literal(entity_id)}\n"
        '    module_id = hb.field(hb.ShortText).default("").desc(\n'
        '        "Stable ParaDev module identifier."\n'
        "    )\n"
        "    data = hb.field(hb.Json).default({}).desc(\n"
        '        "Structured metadata, localization, and resource references."\n'
        "    )\n"
        f"    family = {_python_literal(family_id)}\n"
        f"    resource_slots = {slot_lines}\n"
        '    compilation_hooks = ("normalize", "check", "emit")\n'
        "\n"
        "\n"
        f'__all__ = ["{class_name}"]\n'
    )


def _slot_source(slots: tuple[dict[str, object], ...]) -> str:
    if not slots:
        return "()"
    rows: list[str] = ["("]
    for slot in slots:
        name = _required_text(slot.get("name"), "source slot name")
        match = _required_text(slot.get("match"), f"source slot {name} match")
        rows.extend(
            [
                "        Slot(",
                f"            name={_python_literal(name)},",
                f"            match={_python_literal(match)},",
            ]
        )
        for key in (
            "required",
            "many",
            "regex",
            "kind",
            "shared",
            "authoring_path",
        ):
            value = slot.get(key)
            if value in (None, False):
                continue
            if key in {"required", "many", "regex", "shared"} and value is not True:
                raise TypeError(f"source slot {name} {key} must be a boolean")
            if key == "kind" and not isinstance(value, str):
                raise TypeError(f"source slot {name} kind must be a string")
            if key == "authoring_path" and not isinstance(value, str):
                raise TypeError(f"source slot {name} authoring_path must be a string")
            rows.append(f"            {key}={_python_literal(value)},")
        rows.extend(["        ),"])
    rows.append("    )")
    return "\n".join(rows)


def _entity_class_name(family_id: str) -> str:
    words = family_id.replace("-", "_").split("_")
    return "PIHC3" + "".join(word.capitalize() for word in words) + "Module"


def _python_literal(value: object) -> str:
    if isinstance(value, str):
        return json.dumps(value, ensure_ascii=False)
    return repr(value)


def _mapping(value: object, label: str) -> dict[str, object]:
    if not isinstance(value, Mapping):
        raise TypeError(f"{label} must be a mapping")
    return {str(key): item for key, item in value.items()}


def _required_text(value: object, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise TypeError(f"{label} must be a non-empty string")
    return value.strip()


def main() -> int:
    """Run the inline-to-project-code migration."""

    parser = argparse.ArgumentParser()
    parser.add_argument("project_root", type=Path)
    args = parser.parse_args()
    entity_modules = materialize_project_extension_entities(args.project_root)
    family_modules = materialize_project_extension_build_families(args.project_root)
    print(f"Materialized {len(entity_modules)} project extension Entities and " f"{len(family_modules)} build families.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
