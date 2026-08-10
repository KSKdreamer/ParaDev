"""Python-backed project-local family for collection-owned news event files."""

from __future__ import annotations

from paradev.build import BuildRegistry, CollectionSourceFamily, Slot

FAMILY = "news_event"


def register(registry: BuildRegistry) -> BuildRegistry:
    registry.add(
        CollectionSourceFamily(
            family=FAMILY,
            pdx_path_template="events/{collection_id}.txt",
            loc_path_template="localisation/{language_folder}/{object_id}_{language}.yml",
            source_slots=(Slot("body", "body.pdx", required=True, kind="pdx"),),
            collection_source_slots=(
                Slot("header", "header.pdx", required=True, kind="pdx"),
                Slot("strings", "strings.loc", kind="loc"),
            ),
        )
    )
    return registry
