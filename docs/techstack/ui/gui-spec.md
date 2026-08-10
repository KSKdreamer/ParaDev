# ParaDev GUI Spec

Status: draft

Date: 2026-06-28

## Scope

This spec governs the ParaDev desktop React shell under `apps/desktop/src`. React and Vite are build-time tools; the shipped Python wheel serves the resulting static app to a thin macOS system-WebView host. The shell is a desktop workbench, not a web landing page or an IDE, and should stay quiet, compact, low contrast, and extensible.

## Shell Regions

```text
app
  rail: project management, editing, agent authoring, build, developer, settings
  side panel:
    modules mode: active project selector and module option list
    config mode: active project selector and configuration option list
  main shell:
    topbar: command field, global local-path opener target, panel toggles, theme switch, locale switch
    workspace: title-only tabs, optional two-pane split, inspector
    statusbar: runtime surface status
```

The rail settings button sets the side panel to config mode and opens the active config tab. Editing uses the module side panel. Management, Agents, Build, and Developer are full-width pages and do not show a stale module/config side panel.

The Agents page is a project-aware entry point to existing authoring contracts,
not a second agent runtime. It reads visible family and diagram counts from the
SDK browser summary and authoring-ready template counts from
`Project.templates()`. Its primary action opens ParaDev AI, whose content-plan
proposal must enter the retained module-batch or collection-scaffold editor for review before any write. The
external-agent section exposes the canonical `paradev mcp serve` stdio command,
the `$paradev-authoring` workflow identity, and a project-root-aware starter
prompt. The same-origin Python API resolves this information from the active
runtime: development returns the exact Python/CLI invocation and checkout
working directory, while a wheel install returns its installed entry point and
packaged resource paths. The package resource directory supplies the bundled
single-source skill copied from `.agents/skills/paradev-authoring/`; React must
display the returned path and availability instead of guessing installation
layout. Plain Vite labels values from a mocked or absent API as an unverified
build-time preview. Do not invent agent-session or handoff state in React, and
do not claim that an MCP command or skill wrote project files. All writes
remain plan-first, revision-guarded SDK operations.

## Component Primitives

All new shell controls should use the shared primitives in `apps/desktop/src/components/ui`.

| Primitive | File | Usage |
| --- | --- | --- |
| `IconButton` | `IconButton.tsx` | Icon-only toolbar, tab, project, and shell actions. |
| `SelectField` | `SelectField.tsx` | Project selector, language selector, split-pane tab selector, and future compact dropdowns. |
| `OptionList` | `OptionList.tsx` | Module list and config option list. |

Avoid one-off native `select` or ad hoc icon-button markup in feature code. Add a primitive variant first when a new control shape is needed.

## Control Styling

Controls use the same material treatment:

- height `32px` for normal controls and `28px` for compact split controls;
- radius `8px`, or `6px` for dense nested controls;
- `1px` border using `--border`;
- background `--surface`;
- hover background `--surface-2`;
- focus ring `0 0 0 3px color-mix(in srgb, var(--accent) 16-22%, transparent)`;
- icons inherit `currentColor`;
- dropdowns hide native arrows and use a `ChevronDown` affordance.

Native dropdown menus remain platform-rendered, but the closed control must match the material shell.

## Theme Maintenance Contract

The shell has three maintained major themes: Light Mode (Ollama Theme), Dark Mode (GitHub Soft Dark Theme), and Anthropic Mode (Anthropic Theme). The runtime theme ids are `light`, `dark`, and `anthropic`; the corresponding root classes are `.theme-light`, `.theme-dark`, and `.theme-anthropic`.

When changing a theme, update `apps/desktop/src/styles/theme.css`, `apps/desktop/src/i18n`, and [style.md](./style.md) together. Do not introduce a partial palette that only changes backgrounds and accents. Each theme must include shell surface tokens, `--label`, semantic action tokens (`--accent-contrast`, `--danger-soft`, `--warning-soft`, `--success-soft`), inline-code tokens (`--code-bg`, `--code-text`), and the full CodeMirror token group (`--cm-*`) so labels, path/id snippets, editor chrome, search highlights, syntax colors, and action states remain coherent.

Official Anthropic homepage has highest priority for Anthropic Mode. Keep homepage shell swatches exact when present: Slate Dark `#141413`, Slate Medium `#3d3d3a`, Slate Light `#5e5d59`, Ivory Light `#faf9f5`, Ivory Medium `#f0eee6`, Ivory Dark `#e8e6dc`, Cloud Light `#d1cfc5`, Accent `#c6613f`, Clay `#d97757`, Slate Faded 10 `#1414131a`, and Slate Faded 20 `#14141333`. Use Ivory Medium `#f0eee6` for the app canvas so Anthropic Mode stays warmer than Light Mode, and reserve Ivory Light `#faf9f5` for raised sheets and editor surfaces. Use the provided `styles.css` and Streamlit Anthropic demo only for missing semantic/editor roles such as inline-code background, status colors, and syntax-highlight colors, and document those secondary-source choices in [style.md](./style.md).

## Side Panel

Module and config lists share `OptionList`.

Rows are compact buttons:

- no description text;
- no status icon or dotted indicator;
- left accent bar only;
- row height starts at `34px`;
- selected rows use the same border/background pattern as hover plus shadow.
- names truncate with ellipsis and expose the full name through hover title;
- module-mode rows support drag reorder, persist order per active project in frontend shell state, and derive accent bars from stable ids through theme-defined `--option-accent-*` tokens.

Module and config panels both include the active project selector so project-scoped settings always show and can switch the current project context.

The topbar opener target is the only selector for local path opens: project, module, folder, and file open actions must use it. It uses a packaged icon dropdown: the closed control shows only the selected icon, while the opened menu shows each target's icon and full name. macOS targets are Finder, Cursor, VS Code, Sublime Text, Terminal, and iTerm2; Windows targets are Explorer, Cursor, VS Code, Sublime Text, Command Prompt, and PowerShell. File and image upload controls are import inputs and remain independent from the opener target.

The desktop shell persists global GUI settings as one versioned `paradev.desktop.app-settings.v1` object through `CM_PARADEV` under `paradev.desktop.gui`, with localStorage only as browser fallback and migration. This object owns theme, locale, opener target, project/inspector sidebar open state, project-scoped module order, and config-page settings such as HeavenBase LLM route defaults and local module default sizes. Config-page controls for real `CM_PARADEV` keys, such as `paradev.build.parallelism`, `paradev.cli.output`, `paradev.desktop.thumbnail_cache.max_kb`, and `paradev.ai.chat.default_role`, must additionally round-trip through the SDK-owned desktop config-value bridge so CLI, Python, and GUI use the same setting.

The project-wide browser cache accepts only an SDK payload with an empty `filters` map. Family/module-scoped browser responses are transient overlays: merge a replacement family in place so dashboard order remains stable, persist the merge only when it has an unfiltered same-project base, and reject responses captured before the latest project-refresh generation. Startup may display a valid cached base immediately, but must revalidate it with a fresh unfiltered summary in the background; an explicit same-project refresh keeps the current base visible until that summary commits.

## Tabs

Workspace tabs are title-only.

- No subtitle or description is rendered inside a tab.
- Default tab width is `120px`, minimum `100px`.
- Tab strip height is `42px`.
- All tabs can be closed.
- Zero tabs renders the intentional empty workspace prompt.
- Split view is disabled unless at least two tabs are open.
- Single-click module/config opens create or replace a preview tab. Preview tabs are italic and are not persistent workspace tabs.
- Double-clicking a module/config row or an open preview tab pins it. Editing inside a module tab also pins it, matching VS Code preview-tab behavior.

Module tabs render a generic draft-oriented source editor when SDK browser data is available. The editor uses a searchable entity list on the left and an entity detail panel on the right, with source-slot tabs for code/localization and an image replacement draft panel. The entity list uses the module display policy: default title is the browser-resolved localized/display title with object-id fallback, subtitle is the object id, and ordering has deterministic title/object-id/id tie-breakers. The compact create form consumes the SDK template payload from desktop state, prefers project-local templates, shows object id plus primary template arguments first, and keeps defaulted `advanced` arguments behind one optional control. When a family has one template, creation remains one-click; when a family has multiple templates, a compact template dropdown appears in the create header. Template-backed families are shown in the module list even when the browser has zero source rows, so the GUI can create the first instance of a family such as `entity` without requiring a preexisting source folder. In the installed system-WebView app, New calls the same-origin desktop API to run the scaffold draft plan and then creates the local draft from the resolved backend values; Apply on a new scaffold draft reruns that operation with `write: true`, marks the entity clean with source paths from the SDK plan, and refreshes desktop state so the backend browser becomes the source of truth again. Apply on source text edits calls the SDK-backed draft apply operation for one batch-preflighted project-contained write: the SDK enforces the reopen byte limit, parses JSON/YAML, and invokes any project-family text validator before changing a file. A rejection remains visible as an accessible alert and preserves the dirty editor draft. A successful source write reloads the text and refreshes project/browser/build diagnostics. The image replacement panel embeds Filerobot Image Editor for crop, adjust, filters, watermark, annotation, and resize tools; saving the editor state exports a processed PNG draft, and Apply sends that PNG through the same draft apply operation as a source replacement. Apply on canonical removal drafts sends the entity source-slot paths through the same operation and refreshes desktop state. Plain Vite is a build-time preview and must use an explicit mock or loopback API rather than a local domain fallback. Shared family-root removal drafts and backend DDS/TGA image conversion remain pending.

The family footer reports currently shown objects, loaded Catalog objects, the
complete family total, and family-wide source files as distinct facts. Search,
activity filters, and lazy paging must not make a partial view read as the
complete family.

Guided source editing is a thin Registry client, not a second compiler. The
form comes from the active project family's `source_form(...)` capability.
Built-in exact projectors cover JSON scalars, safely editable PDX scalars,
Registry-declared homogeneous integer lists, and localization text matched by
Registry `loc` slots; project families may still provide their own form.
Integer-list and localization controls are buffered text fields so
multiline section values commit on blur or Command/Ctrl+Enter rather than on
every keystroke. Their local preview consumes only the SDK-provided exact
span, newline, and source-revision patch; React does not discover family or
slot ownership.
Each edited control stores its id, typed scalar value, and the first unsaved
Code-mode text used to open Guided mode in the app-owned editor session. On
Apply, the desktop sends all guided sources for that entity to
`Project.plan_source_form_updates(...)`; the SDK rebuilds each form through the
active Registry, returns exact full-text edits paired with current disk size
and modification-time revisions, and performs no write. The desktop proceeds
with the ordinary atomic draft transaction only when every planned path and
planned text exactly matches the visible drafts. A stale, incomplete, or
contradictory plan fails closed and leaves the session dirty. Switching back
to Code mode clears guided control intent for that source while preserving the
visible text, so mixed Code-to-Guided work has one explicit ownership path.

PIHC3's Achievement, Division, Doctrine, Modifier, Inventory Item, State Lore,
and Superevent extensions declare their existing-source labels, help, scalar
semantics, and editable PDX block bodies on their Entity/Family classes. The
generic projection must preserve those declarations across Python, CLI, REST,
MCP, and desktop surfaces without React family switches. Inventory Item owns a
compact JSON source form with one helper-quantity range control; its external
family expands that value into generated PDX and localization. The UI edits
the declared JSON control through the same generic source-form renderer and
never needs Inventory-specific logic.

A discovered canonical module may remain metadata-free. Its Info panel does
not create a visible metadata file merely to store a display name. The SDK
browser exposes the concrete ordered title-localization keys resolved from the
active Registry family. Editing **Name** updates the preferred-language entry
and requests the physical `{object_id} - {portable title}` folder through one
guarded `Project.apply_source_draft(..., module_rename=...)` operation; a
title-only change may keep the same logical object id. The renderer commits
the final entity only after that combined response succeeds. If a
compatibility project already stores a title in an existing metadata source
and has no localization title target, the editor may update that existing
source, but it does not invent `meta.yaml`.

Do not add HOI4-family-specific create-form logic in React. Use `Project.templates()` and the template `advanced` flag instead.

The module list also exposes batch creation as a secondary authoring command when
the desktop bridge and an authoring-ready template are available. Its structured
rows use the same SDK template fields, allow an explicit source root when the
project has more than one, and always run `Project.create_modules(...)` as
preview first. Any edit invalidates the preview. Apply reuses the frozen request,
selected source root, and exact `plan_hash`; stale or blocked results require a
new preview. An incomplete rollback keeps the retained recovery path visible and
opens it only through the global opener target. Recovery notices are retained in
project-scoped workspace state across dialog and family changes until the user
explicitly dismisses them.

Authoring sessions belong to the application shell, not to one rendered module
or diagram component. Key them by canonical project root and family so changing
rails, switching projects, changing between list and diagram surfaces, or
temporarily unmounting a tab cannot silently discard drafts, batch-create
recovery state, diagram history, or owned blob URLs. A family write is also a
family-session lock: while one view is applying, every sibling view for that
session is inert and visibly busy.

Tab reconciliation is cleanup-first. A dirty or busy session keeps its tab
reachable even when the newest browser payload no longer contains that family.
A clean orphan tab is removed only after its retained session and resources are
disposed successfully; cleanup failure keeps the tab open and offers an
explicit retry. Closing the app or navigating away uses the same dirty/busy
summary. Browser unload uses the native browser warning, while installed-app
quit and window-close events use the localized ParaDev confirmation dialog
when the host exposes a close request. The native
bridge reserves an inactive lease for a renderer session/generation; the
frontend activates it only after its exit listener exists. Delayed activation
or release from a stale renderer cannot affect the active lease. Each pending
exit request has a one-use nonce bound to that lease, and native confirmation is
accepted only after the frontend acknowledges the matching request.
Acknowledgement starts a heartbeat while the dialog owns the request. A missed
heartbeat expires the acknowledged request but preserves the lease. Dialog
retry atomically acquires and acknowledges a fresh nonce before confirming;
up to eight recent visible nonces remain bounded idempotent retry aliases if a
bridge response is lost. A later native close can also obtain a fresh request,
and only a fresh request timing out unacknowledged retires a dead frontend.
Reservation, frontend listener registration, activation retry after transient
failures, ordinary native invocations, and teardown are bounded, and
asynchronous disposers are observed.

Confirmation uses a non-destructive five-second acquire phase followed by a
pinned cleanup phase. The acquire phase must obtain the build and lifecycle
locks, validate the exact acknowledged request, and receive the renderer begin
signal before its deadline. Once cleanup starts, it cannot be canceled,
released, expired, retried, or superseded; confirmation deliberately has no
renderer-side timeout. Keep the close dialog modal and make the entire
application shell inert until cleanup returns an error or native exit begins.
The native worker consumes the request and owns process exit after successful
cleanup, even if the renderer await is lost. A cleanup error must clear the
pinned phase and preserve the acknowledged request for a fresh retry before it
is shown to the user.

Diagram drafts retain the fingerprint of the browser document they were based
on. A clean history rebases when the backend changes, preserving only its
viewport. A dirty history remains visible but cannot overwrite a changed base
until the user resolves the source conflict. Missing backend rows use the same
principle for entity drafts: modified or removal drafts remain recoverable and
blocked, while a row that reappears clears the conflict automatically. Only a
complete authoritative family refresh may classify an omitted entity as
missing; filtered Catalog pages and search results merge returned rows without
treating the page boundary as deletion. Existing source drafts retain the
browser row's size and nanosecond modification-time revision. Apply sends that
revision to the SDK so an external source change rejects the complete request
before any file is overwritten. New image or asset targets send an explicit
expected-absence guard, and guarded file removals use the same source revision,
so creation and deletion races are rejected too.

The Assets tab is available whenever the selected Registry Entity declares a
copy resource slot, including aggregate slots with no single
`authoring_path`. A unique declared or existing slot-owned destination is
selected automatically. Multiple valid existing directories use one generic
destination chooser; no valid existing directory leaves a visible blocked
draft with an advanced project-relative path field. Every selection and manual
path must match a copy slot and stay inside the module before Apply. Existing
files remain replace-only rows so a new upload cannot silently overwrite an
ambiguous same-named resource. React must not branch on family names or
reimplement slot matching.

Tree routing is an explicit family capability, not a label heuristic. The
`focuses` and `technologies` GUI families open editable Focus tree and
Technology tree diagrams backed by the SDK `focus_tree` and `technology`
families. Their project-owned providers expose the same generic diagram-node
form: Focus and Technology creation installs one standalone module through an
exact-hash, build-accepted transaction, and selecting an existing node only
prefills provider-declared context. The Technology provider keeps shared PDX
support modules compilable but excludes them from the node graph. The
`doctrines` GUI family opens the source-backed Doctrine tree. Its project-owned
provider creates standalone subdoctrine modules and plans guarded hidden
diagram-state edits, while canonical PDX remains authoritative for compiled
doctrine content and relationships. The canonical
`military_industrial_organization` family keeps exact organization, policy,
weight, and localization sources together. MIO tree routing must consume the
SDK's source-backed organization and trait projection; the desktop must not
classify sources from folder names or metadata, parse PDX independently, or
offer a write that lacks an exact-source revision and compile-acceptance
contract. MIO source-field labels and help also come from that project-owned
family's Registry declarations and flow through the generic source-form
contract; React must not maintain a parallel MIO field table.

Successful writes reconcile the shell-owned session before awaiting browser
refresh, so a response that settles after the editor unmounts still becomes the
authoritative local state. The SDK treats at most 256 targets and 256 MiB of
streamed backups as one filesystem transaction. After a later failure, an
earlier target is restored only while it still matches ParaDev's exact mutation
token; newer external edits are preserved, and incomplete recovery reports the
retained path. The SDK invalidates the complete derived Catalog before changing
any touched canonical module and reports refresh-required status after source
success. Catalog query and completion remain blocked until a coherent refresh
clears the marker. Failed or unverified Catalog state remains latched in the
app-owned session across remounts until repair and does not silently clear an
unwritten rename, title, text, image, or diagram draft.

Rendered create/apply smoke coverage lives in `apps/desktop/e2e/module-create-smoke.html`. It loads the real React app through Vite with a mocked same-origin runtime bridge so agents can verify the compact form, draft creation, Apply call, clean refreshed row, console health, and screenshot state without adding Playwright to the package.

Real desktop verification should use an isolated temp project and pass it through `PARADEV_PROJECTS` before running `paradev desktop-state`, `paradev scaffold`, `scripts/build-wheel.bash`, and `scripts/smoke-macos-installed-app.bash`. This proves the installed wheel serves the packaged shell, owns the macOS app lifecycle, and can target a non-PIHC3 project without mutating migration sources.

Config tabs are opened from the config option list. They use the same left-list/right-content workbench pattern as module editing: compact grouped options in the side panel, real settings content in the workspace tab, and preview/pin tab behavior identical to modules.

## Build Lifecycle

Desktop build state belongs to the application shell, not to the Build page component. Store runs by project root and run identity above rail-specific views. The Build page receives the active project's runs and must never display another project's progress merely because the user switched projects while a build was running.

Before enabling Build or per-family rebuild controls, the native shell automatically reconciles `build.runs` from the current native process. It restores every active full and partial run, including after the Build rail was unmounted or the renderer/webview reloaded, then polls each active run independently through `build.status`. Rail navigation must not stop a build or its polling. Users should never have to see, copy, or enter a `run_id` to recover control.

Build-control conflicts use the selected project's run slice, not every run owned by the app. One project's full build excludes that project's partial builds, and one partial target cannot be duplicated within that project; an unrelated project may build concurrently while the app shell continues polling both.

The novice-facing dashboard should always answer three questions in plain language: what is building, how far it has progressed, and what the user can do next. Show backend-reported phase, item count, and percentage when available. When an active full build can be stopped, keep the localized Interrupt action visible and use the generated `build.interrupt` confirmation policy. Keep Build actions disabled while initial recovery is loading; if recovery fails, show an accessible error and let Refresh retry reconciliation instead of presenting an idle dashboard that could invite a conflicting build.

Completed, failed, and interrupted runs move into project-attributed history once. The native registry retains the newest 256 terminal payloads while keeping every active run; exact lookup of an evicted id returns `idle`. Renderer-local history is best-effort display state rather than authoritative process recovery. Multiple partial runs remain distinct by target. Refresh project diagnostics only for the project whose run finished, and do not switch the user's active project merely because a background build completed.

Current failed or interrupted target slots outrank successful sibling partials in the overview and disable Run Game. A successful full build is different: it establishes a clean baseline for the whole project and suppresses older partial-slot failures without removing their history. Preserve that baseline independently of the single full-run display slot. Use the registry-local monotonic `terminalSequence`, not wall-clock timestamps, so a later failed full remains visible without reviving pre-baseline partial failures and a genuinely later partial failure remains visible even after clock rollback.

Recovery is bounded to one native ParaDev process. A graceful app close cancels and reaps every app-owned build process group. A full native-process exit, crash, or relaunch does not continue the old build; the next app process starts with a new registry and the user starts a new build. Do not describe renderer reload recovery as process-restart persistence.

Keep a bounded renderer-local presentation checkpoint for the newest concrete run in each project/target slot. The checkpoint is not a process registry and must not persist registry-local terminal sequence values. During startup reconciliation, native rows are authoritative; if a checkpointed running id is absent from the new native registry, present it once as interrupted because ParaDev closed or relaunched, retain that adverse slot across later renderer mounts, and keep Run Game disabled. A later successful native build replaces or supersedes the checkpoint through the ordinary full-build baseline rules.

## Code Editor

CodeMirror 6 is the long-term default and main code editor for the ParaDev desktop GUI. Do not replace it with Monaco for the main app shell unless a future architecture review proves that a VS Code-like editor surface is required and that the Python LSP can still remain the source of truth. Monaco and `monaco-languageclient` remain acceptable for a separate VS Code-like surface, but the normal module/source editor should continue to use CodeMirror.

The default CodeMirror setup is explicit in `apps/desktop/src/moduleEditor/codeMirrorSetup.ts`; do not rely on implicit wrapper defaults. The baseline editor includes CM6 history, default/history/fold/search/completion/lint keymaps, line numbers, folding, search, close brackets, bracket matching, syntax highlighting, indentation, active line/gutter styling, custom selection drawing, multiple selections, rectangular selection, drop cursor, special-character highlighting, selection-match highlighting, and lint gutter/keymap affordances. PDX buffers add ParaDev LSP completion and semantic-token extensions on top; localization buffers add YAML language support. When adding editor behavior, prefer another small CodeMirror extension in this module over component-local event handlers.

The editor dependency policy is CodeMirror 6 package modules plus `@uiw/react-codemirror` as a thin React wrapper. Keep direct dependencies for CM6 packages that ParaDev imports (`@codemirror/autocomplete`, `@codemirror/commands`, `@codemirror/lang-yaml`, `@codemirror/language`, `@codemirror/lint`, `@codemirror/search`, `@codemirror/state`, and `@codemirror/view`) so npm lock drift is visible during review. Check the official [CodeMirror extension list](https://codemirror.net/docs/extensions/) before adding custom editor behavior.

## Config Options

The config side panel is grouped:

- Basic: General, Appearance, Models
- Project: Projects, Module defaults
- Dependency: Dependencies

Each option maps to a workspace tab id prefixed with `config-`, for example `config-general`.

The General page owns shell-level workspace settings such as locale, opener target, and SDK-backed command defaults such as `paradev.project.name` and `paradev.cli.output`. Appearance must expose all three maintained themes. Models must show the HeavenBase LLM route used by ParaDev, including preset, provider, gateway, model, key environment variable, base URL, and a live route test action for the configured preset-aware route. Floating AI chat role labels, details, prompts, default source kinds, and editable profile rows must come from the SDK-owned AI profile catalog, with localized details shown beside the role selector. Project pages own project paths, SDK-backed build defaults such as `paradev.build.parallelism`, and project-scoped module default sizes. Project path rows for root, source roots, output, build cache, and configured HOI4 game root must include compact status chips from `desktop_path_status(...)` plus icon-only open actions using the global opener target and the SDK-backed desktop open-path bridge; do not duplicate path existence checks or path-opening behavior in React. The Module defaults page owns local editing dimensions plus SDK-backed thumbnail cache size through `paradev.desktop.thumbnail_cache.max_kb`. Dependencies owns desktop dependency detection and install actions, starting with ImageMagick because asset conversion and image inspection workflows depend on it.

Create-module chat may return a structured `module.create_batch` proposal only after the Python owner validates it through `Project.create_modules(..., write=False)`. The floating shell renders that result as a quiet review-only card and never writes source files. An explicit review action must revalidate the active project, source root, template catalog, and retained editor state before opening the normal batch editor. The batch editor owns the visible rows, exact dry-plan hash, diagnostics, edit invalidation, and final explicit Apply action; project switches and stale template or session context must fail closed.

## Localization

All user-facing shell text resolves through `apps/desktop/src/i18n` using flat dot-path keys.

English is the source dictionary, and Chinese must define the same key set so the desktop shell can run without English UI fallback in normal flows. The current prototype defaults to Chinese (`zh`) because the maintained module, config, build, diagram, and chat labels have Chinese translations.

Do not inline new GUI strings in components unless they are brand marks, paths, or protocol/runtime literals.

## SDK Contract Imports

Frontend API metadata is SDK-owned. React shell code should import typed operation ids, summaries, workspace section/action rows, input/default/option-source helpers, endpoint/request/payload helpers, and lookup helpers from `apps/desktop/src/data/frontendApi.ts`.

`apps/desktop/src/generated/frontendApi.ts` is the generated source artifact from `render_frontend_api_typescript()` / CLI `frontend-api --typescript`. Do not hand-edit it, and do not maintain a second action list in shell data.

Shell navigation such as sidebars and tabs should derive from `frontendApiWorkspaceSections`. Workbench panels that render actions, forms, or navigation should use `frontendApiWorkspaceActions`, `getFrontendApiAction(...)`, `getFrontendApiActionDetail(...)`, `getFrontendApiActionPanelState(...)`, `getFrontendApiFormValuesWithDefaults(...)`, `getFrontendApiFormControls(..., optionResults)`, `getFrontendApiFormOptionRequests(...)`, `resolveFrontendApiFormOptionRequest(...)`, `resolveFrontendApiNormalizeRequest(...)`, `resolveFrontendApiRestPlanRequest(...)`, `getFrontendApiActionRunState(...)`, `buildFrontendApiRestExecutionRequest(...)`, `resolveFrontendApiRestExecutionRequest(...)`, `getFrontendApiSectionActions(...)`, and `getFrontendApiDefaultSectionAction(...)` first, then use `getFrontendApiBindings(...)` or `getFrontendApiRestBinding(...)` for the SDK, REST, MCP, or LSP binding advertised by the selected operation row. Codegen, inspectors, or route/tool explorers that start from a surface call key should use `frontendApiBindingIndex`, `getFrontendApiBindingOperationIds(...)`, `buildFrontendApiRestIndexKey(...)`, and `getFrontendApiRestOperationIds(...)`; do not read `PARADEV_FRONTEND_API_CONTRACT.index.binding` directly in components. Selected-section action tables should use `getFrontendApiSectionActions(...)` and `getFrontendApiRequiredInputNames(...)`; selected-action panels should use `getFrontendApiActionPanelState(...)` for selected-action detail, defaults, controls, option request plans, normalize/rest-plan request values, confirmation state, Run state, and stable request keys; selected-action execution-plan panels should render normalize/rest-plan result state and ready REST-plan execution state through the helper resolvers, not direct `fetch`, and Run controls must render disabled/detail/status from `getFrontendApiActionRunState(...)` rather than duplicating confirmation or REST-result checks; sidebar and tab selection should stay synchronized on the same workspace section id. Panels that only need raw generated field metadata should use `frontendApiInputOperations`, `getFrontendApiInputs(...)`, `getFrontendApiRequiredInputNames(...)`, `getFrontendApiDefaultValues(...)`, and `getFrontendApiOptionSourceInputs(...)` instead of scanning `operation.inputs` or maintaining local defaults. Panels that call frontend API meta endpoints should use `frontendApiEndpointPaths`, `buildFrontendApiActionUrl(...)`, `buildFrontendApiOptionsUrl(...)`, `buildFrontendApiNormalizeUrl(...)`, and `buildFrontendApiRestRequestUrl(...)` so query names stay aligned with the SDK; JSON POST callers should use `buildFrontendApiOptionsRequest(...)`, `resolveFrontendApiFormOptionRequest(...)`, `buildFrontendApiNormalizeRequest(...)`, `resolveFrontendApiNormalizeRequest(...)`, `buildFrontendApiRestPlanRequest(...)`, and `resolveFrontendApiRestPlanRequest(...)` so request methods, headers, submitted-value bodies, and offline/non-OK/meta-result errors stay centralized. A Vite shell that should call a running REST bridge must set `VITE_PARADEV_FRONTEND_API_BASE_URL`; otherwise the helper reports bridge-unavailable result state without producing browser 404s.

Confirmation controls should use `FrontendApiActionConfirmationStates` and `isFrontendApiActionConfirmationSatisfied(...)` from the helper. The visible checkbox is only acceptance state; title, summary, scope, style, and confirm fields come from `execution.confirmation`, and accepted state resets when submitted action values change.

Run controls should use `getFrontendApiActionRunState(...)` from the helper for `disabled`, `detail`, `status`, and `confirmation_satisfied`. Components may own local React state, but they should not recompute confirmation gating, loading-state gating, or REST result text.

Selected-action workbench panels should prefer `getFrontendApiActionPanelState(...)` before calling individual form/default/request helpers. Components still own React state, but the helper owns the derived panel view model and the stable option/execution request keys used by effects.

When changing `apps/desktop/src/data/frontendApi.ts`, run `rtk npm --prefix apps/desktop run test:unit` in addition to the production build. The unit gate exercises generated summary/group registry alignment, binding-index helpers, panel-state, option-resolution, normalize/rest-plan, REST-execution, and bridge-unavailable helper behavior directly against the checked-in generated SDK contract, while `rtk npm --prefix apps/desktop run build` still verifies TypeScript and Vite output.
