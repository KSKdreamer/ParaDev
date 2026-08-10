from __future__ import annotations

import pytest
from heavenbase.utils import sha256hash

from paradev.sdk._metadata_cleanup import (
    MODULE_METADATA_CLEANUP_POLICY,
    plan_inferred_type_cleanup,
)


def test_inferred_type_cleanup_preserves_every_other_source_byte() -> None:
    content = ("# Human note\r\n" "type: idea\r\n" 'title: "友谊与工业"\r\n' "settings:\r\n" "  nested: [1, 2]\r\n").encode()
    expected = content.replace(b"type: idea\r\n", b"", 1)

    draft = plan_inferred_type_cleanup(
        content,
        "idea",
        source_path="src/modules/idea/FRIENDSHIP/meta.yaml",
    )

    assert draft.action == "update"
    assert draft.blocked is False
    assert draft.changed is True
    assert draft.replacement == expected
    assert draft.removed_keys == ("type",)
    assert draft.current_sha256 == sha256hash(content.decode())
    assert draft.target_sha256 == sha256hash(expected.decode())
    assert draft.diagnostics == ()
    assert draft.to_view() == {
        "policy": MODULE_METADATA_CLEANUP_POLICY,
        "source_path": "src/modules/idea/FRIENDSHIP/meta.yaml",
        "inferred_type": "idea",
        "action": "update",
        "blocked": False,
        "changed": True,
        "removed_keys": ["type"],
        "current": {
            "size_bytes": len(content),
            "sha256": sha256hash(content.decode()),
        },
        "planned": {
            "exists": True,
            "size_bytes": len(expected),
            "sha256": sha256hash(expected.decode()),
        },
        "diagnostics": [],
    }


def test_inferred_type_cleanup_removes_whitespace_only_metadata_file() -> None:
    content = b"type: technology\n\n  "

    draft = plan_inferred_type_cleanup(content, "technology")

    assert draft.action == "remove"
    assert draft.changed is True
    assert draft.target_exists is False
    assert draft.target_size is None
    assert draft.target_sha256 is None
    assert draft.replacement is None
    assert draft.removed_keys == ("type",)


@pytest.mark.parametrize(
    ("content", "expected"),
    [
        (b"type: idea\ntitle: Keep", b"title: Keep"),
        (b"type: idea\r\ntitle: Keep\r\n", b"title: Keep\r\n"),
        (b"type: idea\rtitle: Keep\r", b"title: Keep\r"),
        (b"type: idea   \ntitle: Keep\n", b"title: Keep\n"),
    ],
)
def test_inferred_type_cleanup_preserves_newline_and_eof_style(
    content: bytes,
    expected: bytes,
) -> None:
    draft = plan_inferred_type_cleanup(content, "idea")

    assert draft.action == "update"
    assert draft.replacement == expected


def test_inferred_type_cleanup_uses_standard_utf8_sha256() -> None:
    draft = plan_inferred_type_cleanup(b"type: idea\n", "idea")

    assert draft.current_sha256 == "2bdd61d4b6c24dbf8db3cfb694a6ebaff1e0c36f6b3e51c382c874001796818f"


def test_inferred_type_cleanup_keeps_comments_when_type_was_the_only_value() -> None:
    content = b"# Keep this author note.\ntype: focus\n# It remains useful.\n"
    expected = b"# Keep this author note.\n# It remains useful.\n{}\n"

    draft = plan_inferred_type_cleanup(content, "focus")

    assert draft.action == "update"
    assert draft.replacement == expected


def test_inferred_type_cleanup_is_unchanged_without_a_declared_type() -> None:
    content = b"title: Existing title\nsettings:\n  subtype: country\n"

    draft = plan_inferred_type_cleanup(content, "idea")

    assert draft.action == "unchanged"
    assert draft.changed is False
    assert draft.target_exists is True
    assert draft.target_size == len(content)
    assert draft.target_sha256 == draft.current_sha256
    assert draft.replacement is None
    assert draft.removed_keys == ()
    assert draft.diagnostics == ()


def test_inferred_type_cleanup_blocks_a_type_mismatch() -> None:
    content = b"type: event\ntitle: Wrong family\n"

    draft = plan_inferred_type_cleanup(content, "idea")

    assert draft.action == "blocked"
    assert draft.blocked is True
    assert draft.changed is False
    assert draft.target_exists is None
    assert draft.replacement is None
    assert [row.code for row in draft.diagnostics] == ["module_metadata_cleanup.type_mismatch"]


@pytest.mark.parametrize(
    "content",
    [
        b"'type': idea\n",
        b"type : idea\n",
        b"type: 'idea'\n",
        b"type: idea # preserve this comment\n",
        b"type: &family idea\n",
        b"{type: idea, title: Flow mapping}\n",
        b"base: &base {type: idea}\n<<: *base\n",
    ],
)
def test_inferred_type_cleanup_blocks_non_simple_type_sources(content: bytes) -> None:
    draft = plan_inferred_type_cleanup(content, "idea")

    assert draft.action == "blocked"
    assert draft.replacement is None
    assert [row.code for row in draft.diagnostics] == ["module_metadata_cleanup.type_not_simple"]


def test_inferred_type_cleanup_blocks_duplicate_type_entries() -> None:
    draft = plan_inferred_type_cleanup(b"type: idea\ntype: idea\n", "idea")

    assert draft.action == "blocked"
    assert [row.code for row in draft.diagnostics] == ["module_metadata_cleanup.duplicate_type"]


def test_inferred_type_cleanup_blocks_a_non_text_type() -> None:
    draft = plan_inferred_type_cleanup(b"type: 1\n", "1")

    assert draft.action == "blocked"
    assert [row.code for row in draft.diagnostics] == ["module_metadata_cleanup.type_not_simple"]


def test_inferred_type_cleanup_blocks_indirect_semantic_rebinding() -> None:
    content = b"type: idea\n<<: {type: wrong}\ntitle: Still visible\n"

    draft = plan_inferred_type_cleanup(content, "idea")

    assert draft.action == "blocked"
    assert [row.code for row in draft.diagnostics] == ["module_metadata_cleanup.semantic_change"]


@pytest.mark.parametrize(
    ("content", "code"),
    [
        (b"\xfftype: idea\n", "module_metadata_cleanup.invalid_utf8"),
        (b"type: [unterminated\n", "module_metadata_cleanup.invalid_yaml"),
        (b"- type\n- idea\n", "module_metadata_cleanup.invalid_mapping"),
        (
            b"type: idea\n---\ntitle: second document\n",
            "module_metadata_cleanup.invalid_yaml",
        ),
    ],
)
def test_inferred_type_cleanup_blocks_unreadable_or_ambiguous_yaml(
    content: bytes,
    code: str,
) -> None:
    draft = plan_inferred_type_cleanup(content, "idea")

    assert draft.action == "blocked"
    if code == "module_metadata_cleanup.invalid_utf8":
        assert draft.current_sha256 is None
    assert draft.target_exists is None
    assert draft.replacement is None
    assert [row.code for row in draft.diagnostics] == [code]


def test_inferred_type_cleanup_validates_internal_call_contract() -> None:
    with pytest.raises(TypeError, match="must be bytes"):
        plan_inferred_type_cleanup("type: idea\n", "idea")  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="inferred_type"):
        plan_inferred_type_cleanup(b"type: idea\n", " ")
    with pytest.raises(ValueError, match="source_path"):
        plan_inferred_type_cleanup(b"type: idea\n", "idea", source_path="")
