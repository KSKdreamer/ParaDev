# 2026-07-28 PIHC3 AI Batch Authoring and macOS v4 Preview

## Outcome

ParaDev now turns a create-module chat request into a validated, review-only
batch proposal instead of prose-only guidance. The Python owner exposes exact
authoring-ready templates, accepts a strict structured response, and calls
`Project.create_modules(..., write=False)` once. The GUI revalidates project,
source-root, template, family, and retained-session context before opening the
existing batch editor. Chat cannot write files; only the editor's explicit
Apply action can commit the exact dry plan.

The example request for ideas A–E with `cic` modifiers
`0.02/0.05/0.08/0.12/0.16` produces five normalized requests and one dry plan.
Duplicate ids, mixed families, unknown values, non-finite or unsafe numbers,
stale project/template/source context, and already-open batch planners fail
closed. Editing a reviewed row invalidates the retained plan and requires a
new preview.

## Regression Gates

- Python: 2,305 passed, 35 native/external-fixture skips, 2 warnings.
- Desktop: 1,294 passed across 75 files; TypeScript and production Vite build
  passed.
- Rust: 92 passed.
- Formatting: 191 Python files unchanged; `git diff --check` passed.
- Windows workflow: 9 focused tests and actionlint passed. The workflow now
  uses uv-managed CPython 3.12.13, pins all actions by full SHA, requires 8 GiB
  before native smoke, and uploads only smoke-passing kits.

## Current Unsigned macOS Handoff

The preferred Apple-silicon candidate is:

`dist/release/aarch64-apple-darwin/preview-2026-07-28-ai-batch-v4/ParaDev-0.1.0-0-PIHC3-0.2.3-macos-arm64-UNVERIFIED-PREVIEW.dmg`

- Size: 1,871,503,207 bytes.
- SHA-256:
  `68a8024a2a4d1769680cda19c7fa49f87ba3541453c431cd14c9d376cb2f0ef7`.
- Bundled backend: Python 3.12.13, ParaDev 0.1.0.000dev, HeavenBase
  0.1.2.1, arm64; content fingerprint `660f138b7a2be1ea`.
- Embedded PIHC3 package: 1,844,557,429 bytes, SHA-256
  `87c8f75834ca3b32bdf5124e924a3013d8948ebb189615eeba88ee42f65ef01d`.

Construction and a separate check pass verified the disk image, mounted
contents, deep/strict ad-hoc app signature, arm64 executables, package catalog,
release manifest, first-start guide, and checksum inventory. Candidate
publication now refuses to replace any existing artifact and uses
same-directory no-replacement publication.

## Packaged PIHC3 Evidence

The durable evidence is:

`dist/release/aarch64-apple-darwin/smoke-2026-07-28-ai-batch-v4/macos-smoke-evidence.json`

Its SHA-256 is
`5d2b3ff068a956f135bea1bc9b973a79e84dd9cc2b7c8cd4bf7f068e6c0ba957`.
The mounted bundled backend used a fresh HOME/state/mod root and a child PATH
of `/usr/bin:/bin`; it did not use checkout Python, Conda, or uv.

| Mode | Seconds | Modules | Collections | Artifacts |
| --- | ---: | ---: | ---: | ---: |
| clean/full | 107.69 | 17,802 | 78 | 37,501 |
| cached full | 101.32 | 17,802 | 78 | 37,501 |
| family partial: `technology` | 62.21 | 300 | 0 | 11,899 |
| module partial: `technology/TECHNOLOGY_FIREARM_I` | 61.36 | 1 | 0 | 10,997 |

Every build returned exit 0 with zero diagnostics/errors. Clean and cached
results are byte-identical. After both partial builds, the complete v3
publication ledger and physical output contain the same 37,501 paths,
`whole_project_baseline` remains true, and launch readiness is `ready`.

## Remaining Acceptance Gaps

This is intentionally unverified, development-host evidence—not a public or
clean-machine release. Clean-OS acceptance remains 0/2. The v4 native GUI,
AI proposal card, button-driven builds, and HOI4 launch were not exercised.
No Windows MSI/NSIS artifact exists until the workflow is integrated and run
on native Windows. Signing/notarization is deferred and is not a blocker for
the requested unverified preview.
