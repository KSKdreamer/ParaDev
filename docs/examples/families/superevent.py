"""Python-backed project-local family for standalone superevents."""

from __future__ import annotations

from paradev.build import BuildRegistry, SimpleSourceFamily, Slot

FAMILY = "superevent"


def register(registry: BuildRegistry) -> BuildRegistry:
    registry.add(
        SimpleSourceFamily(
            family=FAMILY,
            metadata_keys=("scope",),
            pdx_path_template="events/superevents/{object_id}.txt",
            loc_path_template="localisation/{language_folder}/{object_id}_{language}.yml",
            source_slots=(
                Slot("script", "script.pdx", required=True, kind="pdx"),
                Slot("loc", "*.loc", many=True, kind="loc"),
            ),
        )
    )
    return registry
