from __future__ import annotations

import sys

from heavenbase.utils import cmd, load_yaml, pj, save_yaml, touch_dir

CANONICAL_DIRECTORY = "{object_id} - {title}"
NORMALIZER_SCRIPT = pj("scripts", "normalize_project_authoring_templates.py", abs=True)


def test_template_normalizer_removes_folder_derived_visible_metadata(
    tmp_path,
) -> None:
    descriptor_path = _template_descriptor(
        tmp_path,
        files={
            "meta.yaml": "title: {title}\n",
            "def.txt": "{object_id} = {{}}\n",
        },
    )

    result = cmd([sys.executable, NORMALIZER_SCRIPT, tmp_path])
    declaration = load_yaml(descriptor_path, strict=True)["items"][0]["meta"]["definition"]["declaration"]

    assert result.code == 0
    assert result.out == "Normalized 1 project extension descriptors."
    assert declaration["directory"] == CANONICAL_DIRECTORY
    assert declaration["files"] == {"def.txt": "{object_id} = {{}}\n"}


def test_template_normalizer_rejects_visible_metadata_as_the_only_source(
    tmp_path,
) -> None:
    descriptor_path = _template_descriptor(
        tmp_path,
        files={"meta.yaml": "title: {title}\n"},
    )
    before = load_yaml(descriptor_path, strict=True)

    result = cmd([sys.executable, NORMALIZER_SCRIPT, tmp_path])

    assert result.code != 0
    assert "must declare an authored source file" in result.err
    assert load_yaml(descriptor_path, strict=True) == before


def _template_descriptor(tmp_path, *, files: dict[str, str]) -> str:
    extension_root = pj(tmp_path, "extensions", "sample", ".paradev")
    touch_dir(extension_root)
    descriptor_path = pj(extension_root, "meta.yaml")
    save_yaml(
        {
            "manifest_version": 2,
            "items": [
                {
                    "kind": "paradev_authoring_template",
                    "meta": {
                        "definition": {
                            "declaration": {
                                "title": "Sample",
                                "family": "sample",
                                "files": files,
                            }
                        }
                    },
                }
            ],
        },
        descriptor_path,
    )
    return descriptor_path
