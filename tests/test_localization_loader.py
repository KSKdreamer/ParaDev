from __future__ import annotations

import hashlib
from pathlib import Path

from heavenbase.utils import sha256hash

from paradev.build import CopySource, Diagnostic, LocalizationEntry, load_copy_sources, load_loc_sources


def test_loc_loader_reads_language_key_text_entries_in_deterministic_order(tmp_path: Path) -> None:
    (tmp_path / "main.loc").write_text(
        "\n".join(
            [
                "[l_english]",
                "GER_sample=Sample focus",
                "GER_sample_desc=Sample focus description",
            ]
        ),
        encoding="utf-8",
    )
    (tmp_path / "extra.loc").write_text(
        "\n".join(
            [
                "[l_french]",
                "GER_sample=Exemple",
            ]
        ),
        encoding="utf-8",
    )

    result = load_loc_sources(tmp_path, {"loc": ("main.loc", "extra.loc")}, module_id="focus/GER_sample")

    assert result.diagnostics == ()
    assert result.entries == (
        LocalizationEntry(key="GER_sample", language="l_french", text="Exemple", source_path="extra.loc", module_id="focus/GER_sample"),
        LocalizationEntry(key="GER_sample", language="l_english", text="Sample focus", source_path="main.loc", module_id="focus/GER_sample"),
        LocalizationEntry(
            key="GER_sample_desc",
            language="l_english",
            text="Sample focus description",
            source_path="main.loc",
            module_id="focus/GER_sample",
        ),
    )


def test_loc_loader_normalizes_language_aliases(tmp_path: Path) -> None:
    (tmp_path / "main.loc").write_text(
        "\n".join(
            [
                "[en]",
                "GER_sample=Sample focus",
                "[fr]",
                "GER_sample=Exemple",
            ]
        ),
        encoding="utf-8",
    )

    result = load_loc_sources(tmp_path, {"loc": ("main.loc",)}, module_id="focus/GER_sample")

    assert result.diagnostics == ()
    assert result.entries == (
        LocalizationEntry(key="GER_sample", language="l_english", text="Sample focus", source_path="main.loc", module_id="focus/GER_sample"),
        LocalizationEntry(key="GER_sample", language="l_french", text="Exemple", source_path="main.loc", module_id="focus/GER_sample"),
    )


def test_loc_loader_preserves_empty_bracket_sections(tmp_path: Path) -> None:
    (tmp_path / "main.loc").write_text(
        "\n".join(
            [
                "[en.GER_sample]",
                "Sample focus",
                "",
                "[en.GER_sample_desc]",
                "",
                "[zh.GER_sample_desc]",
            ]
        ),
        encoding="utf-8",
    )

    result = load_loc_sources(tmp_path, {"loc": ("main.loc",)}, module_id="focus/GER_sample")

    assert result.diagnostics == ()
    assert result.entries == (
        LocalizationEntry(key="GER_sample", language="l_english", text="Sample focus", source_path="main.loc", module_id="focus/GER_sample"),
        LocalizationEntry(key="GER_sample_desc", language="l_english", text="", source_path="main.loc", module_id="focus/GER_sample"),
        LocalizationEntry(key="GER_sample_desc", language="l_simp_chinese", text="", source_path="main.loc", module_id="focus/GER_sample"),
    )


def test_loc_loader_preserves_scripted_localization_brackets_inside_sections(tmp_path: Path) -> None:
    (tmp_path / "main.loc").write_text(
        "\n".join(
            [
                "[en.EVENT_NUKES_1]",
                "Overcharged Artifact Attack at [FROM.FROM.GetName]",
                "",
                "[en.DECISION_TOOLTIP]",
                "[GetC08PinGame2ContactCount]",
                "Today: [?ROOT.VAR|Y]",
            ]
        ),
        encoding="utf-8",
    )

    result = load_loc_sources(tmp_path, {"loc": ("main.loc",)}, module_id="event/EVENT_NUKES_1")

    assert result.diagnostics == ()
    assert result.entries == (
        LocalizationEntry(
            key="EVENT_NUKES_1",
            language="l_english",
            text="Overcharged Artifact Attack at [FROM.FROM.GetName]",
            source_path="main.loc",
            module_id="event/EVENT_NUKES_1",
        ),
        LocalizationEntry(
            key="DECISION_TOOLTIP",
            language="l_english",
            text="[GetC08PinGame2ContactCount]\nToday: [?ROOT.VAR|Y]",
            source_path="main.loc",
            module_id="event/EVENT_NUKES_1",
        ),
    )


def test_loc_loader_preserves_legacy_ini_text_without_yaml_escaping(tmp_path: Path) -> None:
    (tmp_path / "main.loc").write_text(
        "\n".join(
            [
                "[en]",
                'GER_sample=He said "ready" and used C:\\path',
                "GER_sample_desc:0=Cost: £5 # not a comment",
            ]
        ),
        encoding="utf-8",
    )

    result = load_loc_sources(tmp_path, {"loc": ("main.loc",)}, module_id="focus/GER_sample")

    assert result.diagnostics == ()
    assert result.entries == (
        LocalizationEntry(
            key="GER_sample",
            language="l_english",
            text='He said "ready" and used C:\\path',
            source_path="main.loc",
            module_id="focus/GER_sample",
        ),
        LocalizationEntry(
            key="GER_sample_desc",
            language="l_english",
            text="Cost: £5 # not a comment",
            source_path="main.loc",
            module_id="focus/GER_sample",
        ),
    )


def test_loc_loader_reads_hoi4_yaml_like_text_losslessly(tmp_path: Path) -> None:
    (tmp_path / "main.yml").write_text(
        'l_english:\n IDEA_TEST:0 "He said \\"ready\\" at C:\\\\path"\n' "l_simp_chinese:\n IDEA_TEST:0 '标题'\n",
        encoding="utf-8",
    )

    result = load_loc_sources(
        tmp_path,
        {"loc": ("main.yml",)},
        module_id="idea/IDEA_TEST",
    )

    assert result.diagnostics == ()
    assert result.entries == (
        LocalizationEntry(
            key="IDEA_TEST",
            language="l_english",
            text='He said "ready" at C:\\path',
            source_path="main.yml",
            module_id="idea/IDEA_TEST",
        ),
        LocalizationEntry(
            key="IDEA_TEST",
            language="l_simp_chinese",
            text="标题",
            source_path="main.yml",
            module_id="idea/IDEA_TEST",
        ),
    )


def test_loc_loader_accepts_clausewitz_keys_with_apostrophes(
    tmp_path: Path,
) -> None:
    (tmp_path / "main.yml").write_text(
        "l_english:\n" " FOCUS_HOLDER'S_BOULDER:0 \"Holder's Boulder\"\n" ' FOCUS_PINK_ISN\'T_A_COLOR_desc:0 "A valid description."\n',
        encoding="utf-8",
    )

    result = load_loc_sources(
        tmp_path,
        {"loc": ("main.yml",)},
        module_id="focus/FOCUS_HOLDER'S_BOULDER",
    )

    assert result.diagnostics == ()
    assert [entry.key for entry in result.entries] == [
        "FOCUS_HOLDER'S_BOULDER",
        "FOCUS_PINK_ISN'T_A_COLOR_desc",
    ]


def test_loc_loader_reports_duplicate_canonical_keys(tmp_path: Path) -> None:
    (tmp_path / "main.loc").write_text(
        "\n".join(
            [
                "[en]",
                "GER_sample=Sample focus",
            ]
        ),
        encoding="utf-8",
    )
    (tmp_path / "extra.loc").write_text(
        "\n".join(
            [
                "[l_english]",
                "GER_sample=Duplicate sample",
            ]
        ),
        encoding="utf-8",
    )

    result = load_loc_sources(tmp_path, {"loc": ("main.loc", "extra.loc")}, module_id="focus/GER_sample")

    assert result.entries == (
        LocalizationEntry(
            key="GER_sample",
            language="l_english",
            text="Duplicate sample",
            source_path="extra.loc",
            module_id="focus/GER_sample",
        ),
        LocalizationEntry(
            key="GER_sample",
            language="l_english",
            text="Sample focus",
            source_path="main.loc",
            module_id="focus/GER_sample",
        ),
    )
    assert result.diagnostics == (
        Diagnostic(
            code="loc.duplicate_key",
            message="Localization key 'GER_sample' for 'l_english' is declared by extra.loc and main.loc.",
            module_id="focus/GER_sample",
            slot="loc",
            source_path="main.loc",
        ),
    )


def test_loc_loader_reports_invalid_loc_shapes(tmp_path: Path) -> None:
    (tmp_path / "main.loc").write_text("GER_sample=Missing language\n", encoding="utf-8")

    result = load_loc_sources(tmp_path, {"loc": ("main.loc",)}, module_id="focus/GER_sample")

    assert result.entries == ()
    assert result.diagnostics[0].code == "loc.missing_language"
    assert result.diagnostics[0].source_path == "main.loc"


def test_loc_loader_reports_malformed_ini_as_diagnostic(tmp_path: Path) -> None:
    (tmp_path / "main.loc").write_text("[en\nGER_sample=Sample focus\n", encoding="utf-8")

    result = load_loc_sources(tmp_path, {"loc": ("main.loc",)}, module_id="focus/GER_sample")

    assert result.entries == ()
    assert result.diagnostics == (
        Diagnostic(
            code="loc.invalid_line",
            message="Localization line 1 must be '[language]' or 'key=value'.",
            module_id="focus/GER_sample",
            slot="loc",
            source_path="main.loc",
        ),
    )


def test_loc_loader_reports_missing_source_as_diagnostic(tmp_path: Path) -> None:
    result = load_loc_sources(tmp_path, {"loc": ("missing.loc",)}, module_id="focus/GER_sample")

    assert result.entries == ()
    assert result.diagnostics == (
        Diagnostic(
            code="loc.missing_source",
            message="Localization source missing.loc does not exist.",
            module_id="focus/GER_sample",
            slot="loc",
            source_path="missing.loc",
        ),
    )


def test_loc_loader_reports_unreadable_source_as_diagnostic(tmp_path: Path, monkeypatch) -> None:
    (tmp_path / "main.loc").write_text("[en]\nGER_sample=Sample focus\n", encoding="utf-8")

    def fail_read_text(self: Path, *args: object, **kwargs: object) -> str:
        if self.name == "main.loc":
            raise OSError("permission denied")
        return original_read_text(self, *args, **kwargs)

    original_read_text = Path.read_text
    monkeypatch.setattr(Path, "read_text", fail_read_text)

    result = load_loc_sources(tmp_path, {"loc": ("main.loc",)}, module_id="focus/GER_sample")

    assert result.entries == ()
    assert result.diagnostics == (
        Diagnostic(
            code="loc.unreadable_source",
            message="Localization source main.loc cannot be read. permission denied.",
            module_id="focus/GER_sample",
            slot="loc",
            source_path="main.loc",
        ),
    )


def test_copy_loader_preserves_relative_path_and_hash_metadata(tmp_path: Path) -> None:
    payload = b"sample image bytes"
    path = tmp_path / "copy/gfx/interface/goals/GER_sample.png"
    path.parent.mkdir(parents=True)
    path.write_bytes(payload)

    result = load_copy_sources(tmp_path, {"copy": ("copy/gfx/interface/goals/GER_sample.png",)}, module_id="focus/GER_sample")

    assert result.diagnostics == ()
    assert result.sources == (
        CopySource(
            slot="copy",
            path="copy/gfx/interface/goals/GER_sample.png",
            output_path="copy/gfx/interface/goals/GER_sample.png",
            sha256=sha256hash(payload),
            size=18,
            content_sha256=hashlib.sha256(payload).hexdigest(),
        ),
    )
