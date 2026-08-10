# Desktop E2E Fixtures

These fixtures are Vite-rendered smoke pages for desktop UI flows that normally need the same-origin native web bridge. They are not production entry points.

## Module Create Smoke

`module-create-smoke.html` installs a small mock same-origin REST bridge through `window.__PARADEV_RUNTIME_CONFIG__` before loading `/src/main.tsx`. The mock returns a PIHC3 desktop state with a project-local idea template, lets the rendered UI create a new idea draft, and flips an in-memory applied state when the UI executes `module.draft` with `write: true`.

The fixture deliberately declares numeric template defaults while returning
the SDK's string-normalized scaffold values. It also mirrors current project
browser, source-root, Catalog-mutation, and nullable guided-form contracts so
contract drift fails in the rendered create/apply flow instead of being hidden
behind a simplified mock.

Run:

```bash
rtk npm --prefix apps/desktop run dev -- --port 5180
```

Then open:

```text
http://127.0.0.1:5180/e2e/module-create-smoke.html
```

Expected flow:

1. Open the Ideas module (`理念` in the current default Chinese locale).
2. Fill object id `IDEA_RENDERED_FRIENDSHIP`, title `Rendered Friendship Idea`, and description.
3. Click New.
4. Click Apply.
5. Confirm the refreshed row is clean/canonical with three source files and the HTML dataset has `data-paradev-e2e-write-count="1"`.

This fixture verifies the rendered React create/apply path and refresh behavior. Python launcher and API tests remain responsible for the real native bridge and SDK filesystem write paths.

## Boot Progress Smoke

`boot-progress-smoke.html` mounts the real `AppShell` with a PIHC3 project refresh progress state. It verifies that the normal desktop window shows an active loading overlay, phase chips, a percentage value, payload-aware SDK row/template counts, and the animated progress track while SDK project state is still refreshing.

Run:

```bash
rtk npm --prefix apps/desktop run dev -- --port 5180
```

Then open:

```text
http://127.0.0.1:5180/e2e/boot-progress-smoke.html
```

Expected state:

1. The overlay shows `Refreshing project`, the PIHC3 project detail with `1,148 project rows`, `16 templates`, `2 diagnostics`, and `86%`.
2. The root app has `aria-busy="true"` and the underlying rail, project panel, and main shell are inert.
3. The progress track uses `animation-name: boot-progress-track-flow` so long project loads visibly remain active.

## Config Page Smoke

`config-page-smoke.html` mounts the real `AppShell` with a PIHC3-shaped project and browser payload, then enters Settings through the normal rail action. It verifies that user-visible configuration surfaces expose SDK-owned `CM_PARADEV` defaults instead of hiding them in local component state.

Run:

```bash
rtk npm --prefix apps/desktop run dev -- --port 5180
```

Then open:

```text
http://127.0.0.1:5180/e2e/config-page-smoke.html
```

Expected flow:

1. Click the Config rail button; confirm the Settings rail is selected, the Config side panel is populated, the General page shows `paradev.cli.output`, and the HTML dataset reports `data-paradev-config-page-smoke-has-cli-output-key="1"` with `data-paradev-config-page-smoke-cli-output-value="json"`.
2. Change CLI output from JSON to YAML; confirm the dataset reports `data-paradev-config-page-smoke-cli-output-value="yaml"`, `data-paradev-config-page-smoke-last-config-write-count="1"`, `data-paradev-config-page-smoke-last-config-write-key="paradev.cli.output"`, and `data-paradev-config-page-smoke-last-config-write-value="yaml"`.
3. Click `Projects`; confirm the Project config page shows PIHC3 paths, `paradev.build.parallelism`, `paradev.build.strict_metadata`, and the HTML dataset reports `data-paradev-config-page-smoke-has-build-strict-metadata-key="1"` with `data-paradev-config-page-smoke-build-strict-metadata-checked="0"`.
4. Change build parallelism to `6`; confirm the dataset reports `data-paradev-config-page-smoke-build-parallelism-value="6"`, `data-paradev-config-page-smoke-last-config-write-key="paradev.build.parallelism"`, and `data-paradev-config-page-smoke-last-config-write-value="6"`.
5. Toggle strict metadata; confirm the dataset reports `data-paradev-config-page-smoke-build-strict-metadata-checked="1"`, `data-paradev-config-page-smoke-last-config-write-key="paradev.build.strict_metadata"`, and `data-paradev-config-page-smoke-last-config-write-value="true"`.
6. Click `Models`; confirm the AI chat profiles render from SDK-owned source-kind rows, the route summary includes `Preset: Chat`, and the HTML dataset reports `data-paradev-config-page-smoke-ai-profile-source-kinds="project,selection,diagnostics,templates,project-index"`, `data-paradev-config-page-smoke-ai-profile-source-labels="Project,Selection,Diagnostics,Templates,Project index"`, `data-paradev-config-page-smoke-ai-explain-selected-sources="project,selection"`, and `data-paradev-config-page-smoke-ai-explain-toggle-count="5"`.
7. Open the floating AI chat; confirm Chat, Explain HoI4 code, Create module plan, and Build/debug project are available, and each selected role shows its localized SDK-owned detail below the role selector.
8. Change the LLM preset to `reason`; confirm the route summary and floating AI chat route label include `Preset: Reason`, and confirm the dataset reports `data-paradev-config-page-smoke-last-config-write-key="paradev.ai.preset"` and `data-paradev-config-page-smoke-last-config-write-value="reason"`.
9. Toggle the `Templates` context source in the `Explain HoI4 code` profile, click `Save`, and confirm the dataset reports `data-paradev-config-page-smoke-ai-explain-templates-selected="1"`, `data-paradev-config-page-smoke-ai-explain-save-disabled="1"`, `data-paradev-config-page-smoke-ai-last-saved-profile-id="explain"`, and `data-paradev-config-page-smoke-ai-last-saved-source-kinds="project,selection,templates"`.
10. Return to `Projects`; confirm the HTML dataset reports `data-paradev-config-page-smoke-active-tab="config-projects"`, `data-paradev-config-page-smoke-has-build-parallelism-key="1"`, `data-paradev-config-page-smoke-has-build-strict-metadata-key="1"`, and keeps the previously seen CLI output key/value.

## Native-Web PIHC3 AI Profile Smoke

Use this smoke when checking the rendered GUI against the real PIHC3 project through the REST-backed native bridge. Keep `PARADEV_ROOT` temporary so profile writes do not touch the user's normal config:

```bash
tmproot=$(rtk mktemp -d /tmp/paradev-native-web-smoke.XXXXXX)
rtk env PARADEV_ROOT="$tmproot" PARADEV_PROJECTS=projects/PIHC3 bash scripts/run.bash --native-web --port 5208 --bridge-port 8768
```

Then open:

```text
http://127.0.0.1:5208/
```

Expected flow:

1. Confirm the rendered app opens the localized PIHC3 project (`The Pony In The High Castle`).
2. Open Config, then Models (`配置` -> `模型`), and confirm `DeepSeek` is visible.
3. In the `说明 HOI4 代码` profile row, confirm the selected sources start as `项目` and `选区`.
4. Toggle `模板` in that same profile row, click that row's `保存` button, and confirm the row returns to saved state.
5. Verify the SDK facade sees the persisted source list:

```bash
rtk env PARADEV_ROOT="$tmproot" uv run python - <<'PY'
import json
from paradev.desktop import desktop_chat_profiles

payload = desktop_chat_profiles(project_root="projects/PIHC3")
profile = next(row for row in payload["profiles"] if row["id"] == "explain")
print(json.dumps({"projectRoot": payload["projectRoot"], "sourceKinds": profile["sourceKinds"]}, sort_keys=True))
PY
```

6. Reload the GUI, reopen Config -> Models, and confirm `说明 HOI4 代码` still has `模板` selected.
7. Click the `说明 HOI4 代码` row's reset button (`将 说明 HOI4 代码 重置为默认值`) and confirm the SDK facade returns to `["project", "selection"]`.
8. Check the browser and dev-server consoles for warnings; native-web bridge mode should not log `Failed to sync native ParaDev progress`.

## Diagram Apply Review Smoke

`diagram-apply-review-smoke.html` mounts the real `ProjectDiagramView` with the source-backed PIHC3 `C08_PARTIV` focus tree: one-slot focus icon nodes, tree/prerequisite/reference lines, relative branches, auto-laid descendants, one writable metadata row, one skipped metadata row, and module-owned `src/modules/focus_tree/C08_PARTIV/icons/*.png` image paths hydrated through the mocked same-origin binary-source bridge. It verifies that mixed diagram metadata starts behind the review gate, that selected focus layout and relationship edits generate migrated `info.json` drafts, that the first Apply click only acknowledges the review, that the second click runs the real Apply callback, and that actual PIHC3 focus icon images render on the canvas.

Run:

```bash
rtk npm --prefix apps/desktop run dev -- --port 5180
```

Then open:

```text
http://127.0.0.1:5180/e2e/diagram-apply-review-smoke.html
```

Expected flow:

1. Confirm the Apply button starts as `Review scope first`, the review list shows two `Write` rows (`meta.yaml` plus migrated `info.json`) and one `Skip` row, focus icon nodes render on a connected grid, each focus node is a 96 x 96 px source-coordinate slot with a 72 x 72 px actual preview image, and the HTML dataset has `data-paradev-diagram-apply-count="0"`.
2. Edit the selected `FOCUS_C08_TO_THE_WAR` PIHC layout hints through the inspector form: priority `15`, lane `8`, lane delta `2`, center `1`. Confirm `data-paradev-diagram-apply-draft-plan-ok="1"`, `data-paradev-diagram-apply-layout-hint-draft="1"`, `data-paradev-diagram-apply-source-edit-path` points at `legacy/C08_TO_THE_WAR/info.json`, and `data-paradev-diagram-apply-source-edit-text` contains `"w": 8`, `"dw": 2`, and `"dc": 1`.
3. Select `FOCUS_C08_THE_RISING_FIRE`, add `FOCUS_C08_CANTERLOT_MIND` as a prerequisite, then add `FOCUS_C08_PLAN_TWILIGHT` as a reference. Confirm `data-paradev-diagram-apply-relationship-draft="1"` and `data-paradev-diagram-apply-source-edit-path` points at `legacy/C08_THE_RISING_FIRE/info.json`.
4. Click `Review scope first`.
5. Confirm the Apply button changes to `Apply writable rows` and the apply count stays `0`.
6. Click `Apply writable rows`.
7. Confirm the status row changes to `Apply calls: 1` and `Clean`, and the HTML dataset has `data-paradev-diagram-apply-count="1"`, `data-paradev-diagram-grid-size-px="96"`, `data-paradev-diagram-focus-slot-count="9"`, `data-paradev-diagram-preview-node-count="9"`, `data-paradev-diagram-legacy-image-node-count="0"`, and `data-paradev-diagram-image-read-count="9"`.

## Diagram Move Smoke

`diagram-move-smoke.html` mounts the real editable `ProjectDiagramView` with a focused PIHC3 branch fixture. It uses direct module-owned `focus_tree/C08_PARTIV/icons/*.png` imports and deterministic controls for the three HOI4 focus-tree movement behaviors: move the selected subtree, move only the selected node while keeping descendants visually fixed, and move the selected node while returning descendants to auto layout.

Run:

```bash
rtk npm --prefix apps/desktop run dev -- --port 5180
```

Then open:

```text
http://127.0.0.1:5180/e2e/diagram-move-smoke.html
```

Expected flow:

1. Confirm the HTML dataset starts with `data-paradev-diagram-move-command="base"`, `data-paradev-diagram-move-grid-size-px="96"`, `data-paradev-diagram-move-image-node-count="6"`, and `data-paradev-diagram-move-legacy-image-node-count="0"`.
2. Click `Move Subtree`; confirm `data-paradev-diagram-move-branch-delta="2,0"` and branch descendants such as `data-paradev-diagram-move-relative-leaf-delta` also move while `data-paradev-diagram-move-sibling-delta="0,0"`.
3. Click `Move Node Only`; confirm `data-paradev-diagram-move-branch-delta="2,0"` while descendant deltas stay `0,0`.
4. Click `Relayout Descendants`; confirm `data-paradev-diagram-move-branch-delta="2,0"` and `data-paradev-diagram-move-modes` reports the descendants as `auto`.
5. In every state, the SVG canvas contains `.project-diagram-node-image.focus-icon` image elements at 72 x 72 px inside 96 x 96 px focus source-coordinate slots.

## Diagram Source-Backed Smoke

`diagram-source-backed-smoke.html` builds the real `ProjectDiagramView` from a PIHC3 project-browser payload for `C08_PARTIV`. The fixture exercises the adapter path from migrated `source_focuses` layout metadata and compiled focus `icon` keys into module-owned `src/modules/focus_tree/C08_PARTIV/icons/*.png` images, then hydrates those relative image paths through a mocked same-origin binary-source bridge. It verifies the HOI4-style canvas target: connected focus nodes, source-backed roots, prerequisite/reference lines, actual image icons, 96 px focus source-coordinate slots, and no raw `default.png` canvas fallback.

Run:

```bash
rtk npm --prefix apps/desktop run dev -- --port 5180
```

Then open:

```text
http://127.0.0.1:5180/e2e/diagram-source-backed-smoke.html
```

Expected state:

1. The status row shows `Nodes: 9`, `Links: 20`, and `Images: 9`.
2. The SVG canvas contains nine `.project-diagram-node-image.focus-icon` image elements and zero `.project-diagram-node-image-placeholder.focus-icon` placeholders.
3. The root HTML dataset reports `data-paradev-source-backed-preview-node-count="9"`, `data-paradev-source-backed-legacy-node-count="0"`, `data-paradev-source-backed-root-count="2"`, `data-paradev-source-backed-root-ids="FOCUS_C08_CANTERLOT_MIND,FOCUS_C08_THE_RISING_FIRE"`, and non-zero read/cache-write counts.
4. Each focus icon image is 72 x 72 px inside a 96 x 96 px focus source-coordinate slot, so the migrated image stays visibly smaller than a 2 x 2 focus grid footprint.
5. `FOCUS_C08_THE_RISING_FIRE` remains an independent root from source `parent: null`, while prerequisite lines such as `FOCUS_C08_TO_THE_WAR -> FOCUS_C08_PLAN_TWILIGHT` remain visible dependency edges.
6. Click `Move Subtree`; confirm `data-paradev-source-backed-move-branch-delta="2,0"` and each plan child delta is also `2,0`, while `data-paradev-source-backed-move-unaffected-delta="0,0"`.
7. Click `Move Node Only`; confirm the branch delta is `2,0`, each plan child delta is `0,0`, and `data-paradev-source-backed-move-modes` includes `FOCUS_C08_PLAN_TWILIGHT:absolute`.
8. Click `Relayout Descendants`; confirm `data-paradev-source-backed-move-branch-delta="2,0"`, `data-paradev-source-backed-move-starlight-delta="2,0"`, the side plans are repacked to `data-paradev-source-backed-move-twilight-delta="3,0"` and `data-paradev-source-backed-move-sunburst-delta="1,0"`, and `data-paradev-source-backed-move-modes` includes `FOCUS_C08_PLAN_TWILIGHT:auto`.
9. Reset, then edit the selected `FOCUS_C08_TO_THE_WAR` PIHC layout hints through the inspector form: priority `15`, lane `8`, lane delta `2`, center `1`. Confirm `data-paradev-source-backed-move-command="layout-hints"`, `data-paradev-source-backed-selected-layout-hints="priority=15|w=8|dw=2|dc=1"`, and the plan children reflow to `FOCUS_C08_PLAN_TWILIGHT:8,3|FOCUS_C08_PLAN_STARLIGHT:11,3|FOCUS_C08_PLAN_SUNBURST:14,3` inside `data-paradev-source-backed-move-positions`.

## Diagram Technology Smoke

`diagram-technology-smoke.html` builds the real `ProjectDiagramView` through `buildTechnologyDiagramDocument` from an authoritative PIHC3-style Technology projection plus the project-browser labels and source inventory. Positions and relationships come from module-local `def.txt`; images come only from the canonical `icon.png` preview slot. The mocked same-origin native bridge serves those image bytes without reading or writing a real project.

Run:

```bash
rtk npm --prefix apps/desktop run dev -- --port 5180
```

Then open:

```text
http://127.0.0.1:5180/e2e/diagram-technology-smoke.html
```

Expected state:

1. The status row shows `Nodes: 2`, `Links: 2`, `Grid: 48px`, and `Images: 2`.
2. The SVG canvas contains two `.project-diagram-node.icon-node` nodes and two `.project-diagram-node-image.compact-icon` image elements.
3. The root HTML dataset reports `data-paradev-technology-diagram-dependency-edge-count="1"` and `data-paradev-technology-diagram-path-edge-count="1"`: prerequisites and Technology paths remain distinct even when they connect the same two nodes.
4. The dataset also reports `data-paradev-technology-diagram-def-source-count="2"`, `data-paradev-technology-diagram-image-node-count="2"`, and `data-paradev-technology-diagram-legacy-image-count="0"`.
5. Each technology icon image is 34 x 34 px inside a 48 x 48 px technology slot, with no module-card title or mode text inside the node.

## Diagram Technology Apply Review Smoke

`diagram-technology-apply-review-smoke.html` mounts the editable Technology diagram from the same authoritative source-backed contracts with three PIHC3-style modules. `technologyDiagramEditIntents` converts canvas moves, prerequisites, and paths into revision-guarded `def.txt` intents. The page previews those intent payloads and simulates the review/apply state transition in memory; it never calls the module-diagram edit bridge and never writes project files.

Run:

```bash
rtk npm --prefix apps/desktop run dev -- --port 5180
```

Then open:

```text
http://127.0.0.1:5180/e2e/diagram-technology-apply-review-smoke.html
```

Expected flow:

1. Confirm the initial dataset reports `data-paradev-technology-apply-dirty="0"`, `data-paradev-technology-apply-image-node-count="3"`, `data-paradev-technology-apply-legacy-image-count="0"`, `data-paradev-technology-apply-dependency-edge-count="1"`, and `data-paradev-technology-apply-path-edge-count="1"`. Image read/cache-write counts become non-zero after hydration.
2. Click `Move firearm`; confirm `data-paradev-technology-apply-draft-plan-ok="1"`, `data-paradev-technology-apply-source-edit-count="1"`, `data-paradev-technology-apply-position-intent-count="1"`, `data-paradev-technology-apply-edge-intent-count="0"`, and `data-paradev-technology-apply-has-firearm-position-intent="1"`. The sole source path ends in `TECHNOLOGY_FIREARM_I/def.txt`, the intent carries `x: 5`, `y: 2`, and `data-paradev-technology-apply-exact-revision-count="1"`.
3. Discard or reload, then click `Add landmine links`; confirm `data-paradev-technology-apply-source-edit-count="1"`, `data-paradev-technology-apply-def-source-count="1"`, `data-paradev-technology-apply-edge-intent-count="2"`, `data-paradev-technology-apply-has-landmine-dependency-intent="1"`, and `data-paradev-technology-apply-has-landmine-path-intent="1"`. Both changes target the same Landmine `def.txt`, while the rendered totals become two dependency edges and two path edges.
4. Click `Review scope first`, then `Apply writable rows`; confirm `data-paradev-technology-apply-count="1"` and the status row becomes `Clean`. This confirms review UX only; the fixture deliberately has no writable backend.

## Diagram Tab Smoke

`diagram-tab-smoke.html` mounts the real `AppShell` with the full migrated PIHC3 `C01_MAIN` focus-tree browser payload, the source-backed `C08_PARTIV` payload, a second lightweight focus-tree module, and a stateful workspace tab model. It verifies that the normal module opener, the module-tab `Open National Focuses diagram` action, and the separate Diagrams section can be used independently: a user can open the National Focuses module tab, then open the National Focuses diagram tab without replacing the normal module tab. The diagram tab uses the same mocked same-origin binary-source bridge as the source-backed canvas smoke, so it also proves module-owned `focus_tree/<TREE>/icons/*.png` hydration in the shell path and exposes the focus-tree scope selector for switching trees inside the diagram tab.

Run:

```bash
rtk npm --prefix apps/desktop run dev -- --port 5180
```

Then open:

```text
http://127.0.0.1:5180/e2e/diagram-tab-smoke.html
```

Expected flow:

1. Click `National Focuses` in the Modules section.
2. Confirm the HTML dataset reports `data-paradev-diagram-tab-smoke-open-tabs="focuses"` and `data-paradev-diagram-tab-smoke-selected-kind="module"`.
3. Click `Open National Focuses diagram` above the normal module editor.
4. Confirm both `focuses` and `diagram:focuses` tabs are open, the selected kind is `diagram`, and the canvas shows the focus-tree diagram.
5. Confirm the HTML dataset reports `data-paradev-diagram-tab-smoke-expected-c01-node-count="83"`, `data-paradev-diagram-tab-smoke-c01-node-count="83"`, `data-paradev-diagram-tab-smoke-preview-node-count="83"`, `data-paradev-diagram-tab-smoke-focus-image-count="83"`, `data-paradev-diagram-tab-smoke-placeholder-count="0"`, `data-paradev-diagram-tab-smoke-image-status="Images 83/83"`, `data-paradev-diagram-tab-smoke-scope-option-count="3"`, `data-paradev-diagram-tab-smoke-scope-value="focus_tree:C01_MAIN"`, and non-zero image read/cache-write counts.
6. Select `FOCUS_C01_COZY_GLOW_CORONATION`; confirm the HTML dataset reports `data-paradev-diagram-tab-smoke-selected-node-id="FOCUS_C01_COZY_GLOW_CORONATION"`, `data-paradev-diagram-tab-smoke-selected-node-mode="auto"`, `data-paradev-diagram-tab-smoke-mode-switch-count="1"`, `data-paradev-diagram-tab-smoke-mode-switch-mode="auto"`, and `data-paradev-diagram-tab-smoke-mode-switch-selected-match="1"`.
7. Click the selected-node mode switch once; confirm `data-paradev-diagram-tab-smoke-selected-node-mode="relative"`, `data-paradev-diagram-tab-smoke-mode-switch-mode="relative"`, `data-paradev-diagram-tab-smoke-mode-switch-selected-match="1"`, `data-paradev-diagram-tab-smoke-apply-button-text="Review scope first"`, and `data-paradev-diagram-tab-smoke-apply-review-count="1"`.
8. Click `Review scope first`, then `Apply writable rows`; confirm `data-paradev-diagram-tab-smoke-apply-count="1"`, `data-paradev-diagram-tab-smoke-last-apply-path` points at `src/modules/focus_tree/C01_MAIN/legacy/C01_COZY_GLOW_CORONATION/info.json`, and `data-paradev-diagram-tab-smoke-last-apply-text` contains `"relative_position_id": "FOCUS_C01_CANTERLOT_PACT"`.
9. Double-click `FOCUS_C01_DEM_CHANGE`; confirm the HTML dataset reports `data-paradev-diagram-tab-smoke-popup-count="1"`, `data-paradev-diagram-tab-smoke-popup-node-id="FOCUS_C01_DEM_CHANGE"`, `data-paradev-diagram-tab-smoke-popup-source-info-path="src/modules/focus_tree/C01_MAIN/legacy/C01_DEM_CHANGE/info.json"`, and `data-paradev-diagram-tab-smoke-popup-selected-match="1"`.
10. Reopen the normal module tab, then click `National Focuses diagram` in the separate Diagrams section and confirm it selects the same diagram tab.

## Packaged System-WebView Smoke

Use a temporary project when checking the real desktop shell so PIHC3 is not mutated:

```bash
tmpdir=$(mktemp -d /tmp/paradev-webview-smoke.XXXXXX)
rtk uv run paradev new "$tmpdir/project" --project-id webview_smoke --title "System WebView Smoke" --json
PARADEV_PROJECTS="$tmpdir/project" rtk uv run paradev desktop-state --json
PARADEV_PROJECTS="$tmpdir/project" rtk uv run paradev scaffold "$tmpdir/project" idea IDEA_WEBVIEW_SMOKE --value title='System WebView Smoke Idea' --value description='Native WebView smoke project.' --write --json
rtk npm --prefix apps/desktop run build
PARADEV_PROJECTS="$tmpdir/project" rtk uv run paradev-gui --install-app --yes
PARADEV_PROJECTS="$tmpdir/project" rtk uv run paradev-gui
```

Stop the launched app after confirming the process stays alive. The `PARADEV_PROJECTS` override is inherited by the Python loopback bridge, so this smoke covers the same project-selection path as the GUI without touching `projects/PIHC3`.
