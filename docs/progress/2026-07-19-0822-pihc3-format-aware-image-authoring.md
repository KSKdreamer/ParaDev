# PIHC3 format-aware image authoring

## Outcome

ParaDev can now edit an existing PIHC3 PNG, DDS, TGA, JPEG, WebP, or BMP source from the Modules workspace without changing its source identity. The image editor always produces PNG data; the apply boundary converts that data back to the selected source format, validates the converted bytes, and atomically replaces the exact selected file. Raw binary replacements remain backward compatible.

This closes the false-green/read-only gap recorded in the previous authoring report. A novice can select a DDS/TGA-backed entity, drop or load a normal browser-readable image, edit it, and apply it without creating an ignored sibling PNG.

## Contract and GUI changes

- `SourceReplacement` keeps the existing `path` and base64 fields and adds optional `contentFormat: "png"` plus `targetFormat` for DDS, TGA, JPG, JPEG, WebP, and BMP. Native-web REST maps them to `content_format` and `target_format`; the Tauri request remains camelCase and the Python bridge normalizes it before calling the SDK.
- Existing images must be replaced at their exact absolute or project-relative selected path. Format-aware requests must target an existing file and its suffix must match `target_format`. Source-less image drafts remain PNG-only.
- DDS and TGA bytes are not passed to Filerobot because Chromium cannot decode them. The English/Chinese UI explains that the user should drop or load a PNG/JPEG/WebP/BMP replacement. Existing JPEG/WebP/BMP previews and processed draft previews remain directly editable.
- The REST OpenAPI seed and generated frontend field description document the additive conversion fields. Raw PNG replacement payloads are unchanged and do not invoke ImageMagick.

## Conversion safety

- Every converted upload is base64-decoded and checked for the PNG signature before any source mutation.
- All requested conversions finish before the Catalog mutation scope writes text, binary, or removal drafts. A dependency or conversion failure therefore leaves every requested source unchanged.
- ImageMagick is invoked with argv and `shell=False`. `magick` is primary. On non-Windows systems, the legacy `convert` fallback must identify itself as ImageMagick through `convert -version`; Windows never invokes the built-in `convert.exe` filesystem utility.
- Conversion scratch files use a cleaned system temporary directory and are rejected if that directory resolves inside the project. Canonical source discovery can never observe partial `.source.png` or `.converted.dds` files. Only the final replacement uses HeavenBase's same-directory `temp_file`, `save_bin`, `replace_file`, and `delete_file` helpers for an atomic rename.
- Converted headers are validated before replacement: DDS must be DXT5, TGA must be uncompressed with non-zero dimensions, and JPEG/WebP/BMP signatures must match their declared format. Empty, partial, or mislabeled converter output is rejected.

## Real PIHC3 acceptance

The final smoke used a copy-on-write clone and did not modify the user's dirty PIHC3 checkout. ParaDev replaced:

`src/modules/bookmark/PIHC/gfx/interface/bookmarks/PIHC.dds`

with the PNG source from `IDEA_C08_FADED_FRIENDSHIP_1`, then rediscovered and dry-built `bookmark/PIHC`:

- input PNG: 1,134,751 bytes;
- prior DDS SHA-256: `9fbc66a49aa48adaa628dfc657856e8764c728d09065695c876e9a482e93ac44`;
- final DXT5 DDS: 5,760,128 bytes, SHA-256 `1b78b074e450b04cf5b905ada37f3cd998dfe0ab695c67e6750ba063beb9a336`;
- no `PIHC.png` sibling and no conversion scratch file under the module;
- six bounded build artifacts, zero diagnostics, and one artifact input reference to the selected DDS.

The original PIHC3 worktree remains on `7a4efe41bf07084ffe8fe56c2ba2f158ea14527f` with its pre-existing modified and untracked paths unchanged.

## Verification

| Gate | Result |
| --- | --- |
| Repository Python suite excluding the externally versioned PIHC3 snapshot file | 1,451 passed; 2 warnings |
| Complete `tests/test_project.py` SDK/project suite | 237 passed |
| Format-aware draft subset | 18 apply/source-draft cases covered, including all advertised formats, fallback identity, Windows safety, cleanup, and no-mutation failures |
| Complete desktop Vitest suite | 933 passed across 55 files |
| Desktop production build | passed; existing large-chunk advisory remains |
| Complete Tauri Rust gate | 43 passed across 3 suites |
| Desktop/native-web/Tauri Python bridge suites | 165 passed; 1 warning |
| Repository formatting and lint | passed |
| Rust formatting and whitespace/diff validation | passed |
| Real PIHC3 DDS edit, rediscovery, and bounded build | passed; 6 artifacts; 0 diagnostics |

The Heaven-style scanner still reports the touched legacy modules' existing `os`, `pathlib`, `shutil`, subprocess, and JSON utility migrations. The new source path uses HeavenBase command, serialization, deletion, and atomic-file helpers; `tempfile.TemporaryDirectory` is used only because HeavenBase's `temp_file` intentionally creates a same-directory file, which is unsafe for pre-lock conversion scratch data.

## PIHC3 parity audit and remaining work

The 314 tests in `tests/test_pihc3_migration_contracts.py` are coupled to an ignored external `projects/PIHC3` snapshot. The clean release branch omits unrelated dirty migrations those historical assertions expect, while the dirty/repaired acceptance snapshot carries development-version, GUI-layout, and generated Finder metadata drift. This checkpoint does not report that external snapshot suite as green. The real conversion smoke above and the source-independent 1,451-test gate are green; the next PIHC3 branch must establish one authoritative clean fixture and reconcile the historical contracts to it.

The read-only parity audit identified the next branch as three reviewable commits in one PR:

1. Retire machine-local build dependencies. The absolute `pihc_dev` copy root scans 26,979 files but contributes zero of 37,559 artifacts and becomes a blocking missing-source error elsewhere. Localization dedupe currently changes 4,143 path winners and 17 semantic winners depending on PIHC_dev availability; source-map ownership can reproduce the intended precedence for all 6,073 duplicate keys.
2. Sync five C08 idea modules. Ten localization artifacts contain 18 real EN/ZH value differences across `IDEA_C08_FADED_FRIENDSHIP_1..4` and `IDEA_C08_NEVER_FORGET`; the other 1,156 reviewed idea artifacts are equivalent or explicitly compatible.
3. Align the one current trait repair. Of 417 byte-different trait artifacts, 416 are formatting-equivalent and one intentionally adds `modifier_army_sub_unit_infantry_magical_attack_factor = 0.35`. Only that trait's editable metadata mirrors and importer mapping should change; 139 trait modules must not be reformatted.

Native Tauri visual acceptance and final packaging remain blocked by the locked macOS GUI session. The format-aware path is fully exercised through SDK, REST/native-web mapping, Tauri serialization, desktop rendering/model tests, and real PIHC3 source/build acceptance, but that is not a substitute for the final unlocked native/package pass.
