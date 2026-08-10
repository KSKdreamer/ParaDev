# Build Flow Docs Progress

Date: 2026-06-06 19:51 CST

Linear: TAL-294

## Done

- Added [../workflows/build-flow.md](../workflows/build-flow.md) for the current SDK and CLI build path.
- Documented dry-run builds, artifact emission, manifest emission, and profile override for the minimal demo project.
- Linked the build-flow page from the workflow index and docs menu.
- Avoided editing the dirty top-level canonical README files.

## Verification

- `rtk uv run paradev build demos/assets/projects/minimal --json`
- `rtk uv run paradev build <temp demo copy> --emit-artifacts --json`
- `rtk uv run paradev build <temp demo copy> --emit-manifests --json`
- `rtk uv run paradev build demos/assets/projects/minimal --profile hoi4 --json`
- `git diff --check -- docs/README.md docs/workflows/README.md docs/workflows/build-flow.md`
- `rtk bash scripts/test.bash`
- `rtk bash scripts/flake.bash --ci`

## Risks Or Blockers

- Live Linear sync is still pending because no Linear MCP tool or `linear` CLI is available in this session.
- Existing local desktop and README edits remain outside this build-flow docs slice.

## Next

- Add a small public SDK example or doctest-style coverage for `Project.load(...).build(...)` once README ownership is clear.
