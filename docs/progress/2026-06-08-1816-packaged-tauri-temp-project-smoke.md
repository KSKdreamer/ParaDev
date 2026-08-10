# 2026-06-08 18:16 Packaged Tauri Temp-Project Smoke

Linear: TAL-298

## Scope

- Verified the real Tauri desktop build path after the rendered create/apply smoke.
- Kept all filesystem writes inside an isolated temp project at `/tmp/paradev-tauri-smoke.ciOFr9/project`.
- Did not mutate `projects/PIHC3`.

## Temp Project

- Created a project with `rtk uv run paradev new /tmp/paradev-tauri-smoke.ciOFr9/project --project-id tauri_smoke --title "Tauri Smoke" --json`.
- Confirmed `PARADEV_PROJECTS=/tmp/paradev-tauri-smoke.ciOFr9/project rtk uv run paradev desktop-state --json` resolved the active root to the temp project and returned project id `tauri_smoke`.
- Confirmed the desktop browser payload also used project id `tauri_smoke`.

## Create Path

- Ran `PARADEV_PROJECTS=/tmp/paradev-tauri-smoke.ciOFr9/project rtk uv run paradev scaffold /tmp/paradev-tauri-smoke.ciOFr9/project idea IDEA_TAURI_SMOKE_2 --value title='Tauri Smoke Idea' --value description='Native shell smoke project.' --write --json`.
- The SDK plan was unblocked, wrote `IDEA_TAURI_SMOKE_2`, and produced three files:
  - `src/modules/idea/IDEA_TAURI_SMOKE_2/meta.yaml`
  - `src/modules/idea/IDEA_TAURI_SMOKE_2/def.pdx`
  - `src/modules/idea/IDEA_TAURI_SMOKE_2/main.loc`

## Native Shell

- `rtk cargo test --manifest-path apps/desktop/src-tauri/Cargo.toml`: 8 tests passed.
- `rtk npm --prefix apps/desktop run tauri:build`: TypeScript, Vite, Rust release build, `.app`, and `.dmg` bundling passed.
- Direct bundled launch command:
  - `PARADEV_PROJECTS=/tmp/paradev-tauri-smoke.ciOFr9/project apps/desktop/src-tauri/target/release/bundle/macos/ParaDev.app/Contents/MacOS/paradev-desktop`
- Launch smoke result: process stayed alive for 5 seconds and emitted no startup log lines before being stopped.

## Result

The packaged desktop shell can now be verified against a disposable project while exercising the same SDK-backed project-state and scaffold paths that the GUI bridge depends on. This closes the immediate gap left by the mocked rendered smoke fixture. The next useful slices are to keep expanding PIHC3 template coverage and to convert remaining GUI fallbacks only when the SDK exposes the necessary payloads.
