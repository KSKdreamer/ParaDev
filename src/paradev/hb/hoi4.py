"""HeavenBase extension for HOI4 project catalog rows."""

from __future__ import annotations

import heavenbase as hb
from heavenbase.utils import sha256hash

HOI4_EXTENSION_ID = "hoi4"
_CATALOG_NAME_MAX_CHARS = hb.Catalog.schema().get("name").dtype.max_chars
_CATALOG_DESC_MAX_CHARS = hb.Catalog.schema().get("desc").dtype.max_chars
HOI4_ENTITY_TYPES = (
    "asset",
    "build-artifact",
    "build-dependency",
    "build-graph-edge",
    "build-graph-node",
    "collection",
    "diagnostic",
    "hoi4-entity",
    "loc-entry",
    "module",
    "pdx-document",
    "pdx-symbol",
    "project",
    "source-file",
    "source-slot",
    "sprite",
)
PDX_SYMBOL_FIELD_STORAGE = (
    ("symbol_id", "symbol_id"),
    ("document_id", "document_id"),
    ("module_id", "module_id"),
    ("collection_id", "collection_id"),
    ("family", "family"),
    ("slot", "slot"),
    ("path", "path"),
    ("key", "symbol_key"),
    ("kind", "kind"),
    ("op", "op"),
    ("value", "value"),
    ("value_type", "value_type"),
    ("line", "source_line"),
    ("column", "source_column"),
)
# Public Catalog payload names stay stable while storage avoids provider-reserved
# names such as ``key`` and ``column``.
PDX_SYMBOL_DATA_FIELDS = tuple(field_name for field_name, _storage_name in PDX_SYMBOL_FIELD_STORAGE)
# The previous Json payload was bounded by SQLite's own string limit rather than
# LongText's 65,535-character default. Keep that effective compatibility bound.
_PDX_TEXT_MAX_CHARS = 1_000_000_000


def entity_identifier(entity_type: str) -> str:
    """Return the HeavenBase entity identifier for one HOI4 catalog row group.

    Args:
        entity_type: Preview row group such as `source-file` or `pdx-symbol`.

    Returns:
        Stable HeavenBase entity identifier owned by the HOI4 extension.
    """

    return entity_type if entity_type.startswith(f"{HOI4_EXTENSION_ID}-") else f"{HOI4_EXTENSION_ID}-{entity_type}"


def entity_table(entity_type: str) -> str:
    """Return the SQLite table name for one HOI4 catalog row group.

    Args:
        entity_type: Preview row group such as `source-file` or `pdx-symbol`.

    Returns:
        Backend-safe table name used by HeavenBase SQLite storage.
    """

    return entity_identifier(entity_type).replace("-", "_")


def entity_type_from_identifier(identifier: str) -> str | None:
    """Return the catalog row group for a HOI4 entity identifier.

    Args:
        identifier: Entity identifier such as `hoi4-source-file`.

    Returns:
        Catalog row group if the identifier is owned by this extension.
    """

    if identifier in HOI4_ENTITY_TYPES:
        return identifier
    prefix = f"{HOI4_EXTENSION_ID}-"
    if not identifier.startswith(prefix):
        return None
    entity_type = identifier.removeprefix(prefix)
    return entity_type if entity_type in HOI4_ENTITY_TYPES else None


def normalize_entity_identifier(value: str) -> str:
    """Normalize a user-facing entity selector to a HOI4 entity identifier.

    Args:
        value: Short row group such as `source-file` or full id such as
            `hoi4-source-file`.

    Returns:
        Stable HOI4 extension entity identifier.
    """

    return value if value.startswith(f"{HOI4_EXTENSION_ID}-") else entity_identifier(value)


def hoi4_entities() -> tuple[type[hb.Entity], ...]:
    """Return persistent entity classes owned by the HOI4 extension.

    Returns:
        Entity classes used for catalog-backed HOI4 project workspaces.
    """

    return tuple(_ENTITY_CLASSES[entity_type] for entity_type in HOI4_ENTITY_TYPES)


def hoi4_extension() -> hb.ext.Extension:
    """Return the HOI4 HeavenBase extension definition.

    Returns:
        Extension object that registers catalog-backed HOI4 entities.
    """

    return hb.ext.Extension(
        HOI4_EXTENSION_ID,
        name="HOI4",
        desc="ParaDev Hearts of Iron IV project catalog entities.",
        entities=hoi4_entities(),
        required=False,
        tags={"hoi4": True, "paradev": True, "catalog": True},
    )


def register_hoi4_extension(*, context: hb.Context | None = None) -> hb.ext.Extension:
    """Register the HOI4 extension in ParaDev's HeavenBase context.

    Args:
        context: Optional explicit HeavenBase context. Defaults to ParaDev's
            isolated process context rather than HeavenBase's user context.

    Returns:
        Registered extension object.
    """

    if context is None:
        from paradev.config import _CONTEXT_PARADEV

        context = _CONTEXT_PARADEV
    return hoi4_extension().register(resolver=context.modules())


def _catalog_name(value: object) -> str:
    return _catalog_text(value, _CATALOG_NAME_MAX_CHARS)


def _catalog_desc(value: object) -> str:
    return _catalog_text(value, _CATALOG_DESC_MAX_CHARS)


def _catalog_text(value: object, max_chars: int) -> str:
    text = "" if value is None else str(value)
    if len(text) <= max_chars:
        return text
    suffix = f"...#{sha256hash(text)[:12]}"
    return text[: max_chars - len(suffix)] + suffix


def _pdx_symbol_catalog_tags(
    family: object,
    module_id: object,
    collection_id: object,
    slot: object,
) -> list[str]:
    tags = ["pdx-symbol"]
    for value in (family, module_id, collection_id, slot):
        if isinstance(value, str) and value:
            tags.append(value)
    return tags


class Hoi4PdxSymbol(hb.Entity):
    """Typed, lossless source symbol registered by the HOI4 extension."""

    identifier = entity_identifier("pdx-symbol")
    __derive__ = [
        hb.Entity.derive("catalog.name").compute(_catalog_name, inputs=["path"]),
        hb.Entity.derive("catalog.desc").compute(_catalog_desc, inputs=["path"]),
        hb.Entity.derive("catalog.tags").compute(
            _pdx_symbol_catalog_tags,
            inputs=["family", "module_id", "collection_id", "slot"],
        ),
    ]

    symbol_id = hb.field(hb.LongText(max_chars=_PDX_TEXT_MAX_CHARS)).required().desc("Stable symbol occurrence identifier.")
    document_id = hb.field(hb.LongText(max_chars=_PDX_TEXT_MAX_CHARS)).required().desc("Owning PDX document identifier.")
    module_id = hb.field(hb.LongText(max_chars=_PDX_TEXT_MAX_CHARS)).optional().desc("Owning module identifier when module-owned.")
    collection_id = hb.field(hb.LongText(max_chars=_PDX_TEXT_MAX_CHARS)).optional().desc("Owning collection identifier when collection-owned.")
    family = hb.field(hb.MediumText).required().desc("Registered build family.")
    slot = hb.field(hb.MediumText).required().desc("Registered source slot.")
    path = hb.field(hb.LongText(max_chars=_PDX_TEXT_MAX_CHARS)).required().desc("Stable path within the PDX document.")
    symbol_key = hb.field(hb.LongText(max_chars=_PDX_TEXT_MAX_CHARS)).required().desc("PDX entry key.")
    kind = hb.field(hb.ShortText).required().desc("PDX entry kind.")
    op = hb.field(hb.ShortText).optional().desc("PDX operator when present.")
    value = hb.field(hb.LongText(max_chars=_PDX_TEXT_MAX_CHARS)).optional().desc("Scalar PDX value when present.")
    value_type = hb.field(hb.ShortText).optional().desc("Scalar PDX value type when present.")
    source_line = hb.field(hb.Integer).optional().desc("One-based source line when available.")
    source_column = hb.field(hb.Integer).optional().desc("One-based source column when available.")


def _entity_class(entity_type: str) -> type[hb.Entity]:
    if entity_type == "pdx-symbol":
        return Hoi4PdxSymbol
    return type(
        "Hoi4" + "".join(part.title() for part in entity_type.split("-")),
        (hb.Entity,),
        {
            "__module__": __name__,
            "__doc__": f"HeavenBase row for ParaDev HOI4 {entity_type} catalog data.",
            "__derive__": [
                hb.Entity.derive("catalog.name").compute(_catalog_name, inputs=["name"]),
                hb.Entity.derive("catalog.desc").compute(_catalog_desc, inputs=["description"]),
            ],
            "identifier": entity_identifier(entity_type),
            "name": hb.field(hb.MediumText).default("").desc("Catalog display name."),
            "description": hb.field(hb.LongText).default("").desc("Catalog search description."),
            "tags": hb.field(hb.Json).default([]).desc("Catalog tags."),
            "data": hb.field(hb.Json).default({}).desc("Original preview row payload."),
        },
    )


_ENTITY_CLASSES = {entity_type: _entity_class(entity_type) for entity_type in HOI4_ENTITY_TYPES}
for _generated_entity in _ENTITY_CLASSES.values():
    globals()[_generated_entity.__name__] = _generated_entity
del _generated_entity


__all__ = [
    "HOI4_ENTITY_TYPES",
    "HOI4_EXTENSION_ID",
    "Hoi4PdxSymbol",
    "PDX_SYMBOL_DATA_FIELDS",
    "PDX_SYMBOL_FIELD_STORAGE",
    "entity_identifier",
    "entity_table",
    "entity_type_from_identifier",
    "hoi4_entities",
    "hoi4_extension",
    "normalize_entity_identifier",
    "register_hoi4_extension",
]
