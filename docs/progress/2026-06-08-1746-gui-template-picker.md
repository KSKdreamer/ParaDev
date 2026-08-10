# 2026-06-08 17:46 GUI Template Picker

## Scope

- Added a generic compact template picker for desktop create forms when a family has multiple SDK templates.
- Preserved the one-click path for families with a single template.
- Project-local templates are listed before built-in templates, and the first project-local candidate remains the default.
- Fixed template matching for GUI family ids such as `decisions` and `state-lore` against SDK template families such as `decision` and `state_lore`.

## Behavior

- `selectCreateTemplates(...)` returns ordered template candidates for a family.
- `selectCreateTemplate(...)` accepts an optional template id and falls back to the first candidate.
- The create form renders a `SelectField` only when there are at least two candidate templates.
- Switching templates refreshes the primary and advanced create fields from the selected template.

## Verification

- Red first: `rtk npm --prefix apps/desktop run test:model` failed with `selectCreateTemplates is not a function`.
- Green focused: `rtk npm --prefix apps/desktop run test:model` passed with 14 tests.
- Desktop build: `rtk npm --prefix apps/desktop run build` passed TypeScript and Vite build.
- Dev-server smoke: `curl -sSf http://127.0.0.1:5174/` and `curl -sSf http://127.0.0.1:5174/src/main.tsx` both returned expected Vite/React content.
- Rendered browser smoke was attempted, but the Playwright browser MCP profile was already locked by another browser instance and the local desktop package does not include Playwright for a fallback rendered probe.

## Unfinished Jobs

- Rendered Tauri verification should still exercise the full SDK-backed create/apply path.
- Template descriptions or previews may be useful later, but they are intentionally not shown yet to keep the create form compact.
