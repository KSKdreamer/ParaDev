# ParaDev UI Style

Status: draft

Date: 2026-06-13

Implementation spec: [GUI Spec](./gui-spec.md)

## Direction

ParaDev should feel like a quiet desktop workbench, not a marketing site and not a full IDE. The default shell uses restrained material surfaces, thin borders, compact typography, and 8px-or-smaller rounded rectangles. The app should be comfortable for long modding sessions and clear enough for agents to explain what they are doing.

Design references:

- Ollama desktop app: simple local-app feel, file-aware chat surface, macOS and Windows desktop priority.
- GitHub Desktop: repository/project selector, left-side workflow navigation, contextual action bars.
- Codex and Cursor Agents: project/task side panels, main work area, tabbed agent/workflow context.
- Anthropic homepage: official brand swatches and light/dark theme variables.
- Streamlit Anthropic theming example: warm, restrained paper surfaces with explicit theme tokens for text, widgets, code, borders, and charts.
- EmoCompass provided CSS: paper-manual semantic colors used only where official Anthropic and Streamlit do not define a practical editor/status role.

## Layout Model

```text
App window
  left rail: global navigation, project switch, command access
  foldable project panel: active project selector and scrollable module browser
  main area:
    top toolbar: search, global local-path opener target, icon-only panel toggles, theme switch
    dynamic tab workspace: closable tabs, optional two-pane split
    foldable right inspector
    status bar: local service, SDK, MCP, REST, LSP, bundle state
```

The first screen is the app itself. Do not add a landing page, hero section, marketing copy, or decorative imagery to the desktop shell.

## Geometry

| Token | Value |
| --- | --- |
| Window min width | `1120px` |
| Window min height | `720px` |
| Left rail width | `64px` |
| Project panel width | `176px` |
| Inspector width | `320px` |
| Radius small | `6px` |
| Radius medium | `8px` |
| Radius large | `12px` |
| Border width | `1px` |
| Focus ring | `0 0 0 3px color-mix(in srgb, var(--accent) 22%, transparent)` |
| Fast motion | `150ms cubic-bezier(0.2, 0.8, 0.2, 1)` |
| Panel motion | `210ms cubic-bezier(0.2, 0.8, 0.2, 1)` |

Cards are only for repeated items or modal-like surfaces. Page sections and app panes use rails, panels, tables, lists, and split views.

Project and inspector panels collapse by animating their grid tracks instead of unmounting content. Keep this as the default modular behavior for future side panels, drawers, and split panes. Always pair motion with a `prefers-reduced-motion` fallback.

The right inspector is closed by default so the first-run workspace has more horizontal room. Project and inspector toolbar controls are icon-only with `title` labels; avoid visible button text for panel chrome.

Workspace tabs are dynamic and title-only. A tab strip should support closing every tab and selecting the active tab. Single-clicking a module or config row opens it as a VS Code-style preview tab, replacing the existing preview tab. Double-clicking the row/tab or editing inside a module tab pins it. When all tabs are closed, render an intentional empty workspace background with a short one-line prompt rather than forcing a placeholder tab. The main workspace may split horizontally into two panes, limited to two columns for the prototype. Split view is only enabled when at least two tabs are open. Each pane owns an active tab selection, while the tab strip remains a shared open-tab list.

The project panel starts with a compact active-project selector row:

- dropdown for available projects;
- icon-only `New Project` and `Open Project` buttons;
- small folder path beneath the selector.

The top toolbar owns the local-path opener target and every GUI path-open action must use that shared setting. The closed opener control is icon-only, while its dropdown menu shows icon plus full name. macOS choices are `Finder`, `Cursor`, `VS Code`, `Sublime Text`, `Terminal`, and `iTerm2`; Windows choices are `Explorer`, `Cursor`, `VS Code`, `Sublime Text`, `Command Prompt`, and `PowerShell`. File and image uploads are separate import flows and must not use it.

Persist theme, locale, opener target, sidebar open state, project-scoped module order, HeavenBase LLM route defaults, and module default sizes together as the versioned `paradev.desktop.app-settings.v1` GUI settings object through `CM_PARADEV`; localStorage is only the browser fallback and migration surface. Real runtime config keys exposed in the GUI, including `paradev.build.parallelism`, `paradev.cli.output`, and `paradev.ai.chat.default_role`, must use the desktop config-value bridge so the visible control changes the same `CM_PARADEV` value used by Python SDK and CLI calls.

The old project card, local services block, and split module/service sections are removed. Use one scrollable `Modules` section for domain choices. Module rows are compact tab-opening buttons: no status icons, dotted indicators, or descriptions in the project panel. Names truncate with ellipsis in the narrow rail and expose the full name through hover title. Module rows are drag-reorderable, with project-scoped persistence in frontend shell state, and accent bars are hashed from stable module ids through theme-defined `--option-accent-*` tokens. Seed it with common Hearts of Iron IV families such as countries, characters, decisions, divisions, national focuses, ideas, modifiers, map, states, events, technologies, equipment, buildings, scripted effects, scripted triggers, localization, assets, and music.

## Localization

All GUI text that is owned by the React shell should resolve through `apps/desktop/src/i18n`. Use flat dot-path keys such as `project.active.label`, `modules.countries.title`, and `workspace.action.splitRight` so translators can work without reading component code. English is the source dictionary, and Chinese must maintain the same key set so normal desktop flows do not fall back to English copy.

The prototype currently defaults to Chinese. New confirmed React-shell copy must be added to both locale dictionaries in the same change so the Chinese desktop UI remains complete.

## Typography

Use system fonts first:

```css
font-family:
  Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont,
  "Segoe UI", sans-serif;
```

Use `SFMono-Regular`, `Menlo`, `Consolas`, or `Liberation Mono` for paths, IDs, and protocol labels. Letter spacing stays `0`.

| Role | Size | Weight | Line height |
| --- | ---: | ---: | ---: |
| App title | `14px` | `650` | `20px` |
| Panel heading | `12px` | `650` | `16px` |
| Body | `13px` | `450` | `19px` |
| Label | `11px` | `600` | `14px` |
| Mono/status | `11px` | `500` | `15px` |

## Theme Tokens

The desktop shell maintains exactly three major themes. Keep the `ThemeName` union in `apps/desktop/src/types.ts`, the `.theme-*` blocks in `apps/desktop/src/styles/theme.css`, the toolbar labels in `apps/desktop/src/i18n`, and this section in sync.

| Mode | CSS class | Reference | Intent |
| --- | --- | --- | --- |
| Light Mode (Ollama Theme) | `.theme-light` | Ollama desktop app | Local-first light workbench with neutral surfaces and a muted teal action color. |
| Dark Mode (GitHub Soft Dark Theme) | `.theme-dark` | GitHub dark Primer colors | Soft developer dark mode with GitHub-like syntax colors and low-glare panels. |
| Anthropic Mode (Anthropic Theme) | `.theme-anthropic` | Anthropic homepage, then provided CSS and Streamlit | Official Anthropic homepage has highest priority; provided CSS and Streamlit only fill semantic/editor gaps. |

Official Anthropic homepage has highest priority for Anthropic Mode. Shell colors must use Anthropic homepage swatches when they exist: Slate Dark `#141413`, Slate Medium `#3d3d3a`, Slate Light `#5e5d59`, Ivory Light `#faf9f5`, Ivory Medium `#f0eee6`, Ivory Dark `#e8e6dc`, Cloud Light `#d1cfc5`, Accent `#c6613f`, Clay `#d97757`, Slate Faded 10 `#1414131a`, and Slate Faded 20 `#14141333`. Use Ivory Medium `#f0eee6` for the app canvas so Anthropic Mode keeps a warm paper feel; reserve Ivory Light `#faf9f5` for elevated sheets and editor surfaces. The provided `styles.css` and Streamlit Anthropic demo may only supply missing semantic roles such as editor syntax colors, success/warning/danger, and inline-code background.

### Code and label color contract

Every theme must define these token groups together:

- Shell surface tokens: `--bg`, `--surface`, `--surface-2`, `--surface-3`, `--text`, `--muted`, `--subtle`, `--label`, `--border`, `--border-strong`, `--accent`, `--accent-contrast`, `--accent-2`, `--accent-soft`, `--danger`, `--danger-soft`, `--warning`, `--warning-soft`, `--success`, `--success-soft`, and `--shadow`.
- Inline code tokens: `--code-bg` and `--code-text`. The global `code` rule uses these so path, id, and protocol labels do not drift from the active theme.
- CodeMirror tokens: `--cm-bg`, `--cm-text`, `--cm-gutter-bg`, `--cm-gutter-text`, `--cm-active-line`, `--cm-selection`, `--cm-search-match`, `--cm-search-selected`, `--cm-token-class`, `--cm-token-property`, `--cm-token-enum`, `--cm-token-string`, `--cm-token-number`, and `--cm-token-variable`.

Do not add a new major theme by only changing shell colors. Labels, inline code, CodeMirror editor chrome, semantic-token colors, search highlights, and selection colors must be reviewed in the same change.

### Light Mode (Ollama Theme)

```css
--bg: #f6f6f5;
--surface: #ffffff;
--surface-2: #f1f1ef;
--surface-3: #e9e9e6;
--text: #171717;
--muted: #6f6f6a;
--subtle: #9a9a94;
--label: #6f6f6a;
--border: #deded9;
--border-strong: #c8c8c1;
--accent: #2f6f68;
--accent-contrast: #ffffff;
--accent-2: #7f5636;
--accent-soft: #e2efec;
--danger: #b54545;
--danger-soft: #f6e3e1;
--warning: #a06419;
--warning-soft: #f4eadc;
--success: #2f7652;
--success-soft: #e1efe7;
--shadow: 0 12px 34px rgba(22, 22, 19, 0.08);
--code-bg: #ffffff;
--code-text: #24292f;
--cm-bg: #ffffff;
--cm-text: #24292f;
--cm-gutter-bg: #f6f8fa;
--cm-gutter-text: #6e7781;
--cm-active-line: #f6f8fa;
--cm-selection: rgba(9, 105, 218, 0.18);
--cm-search-match: rgba(191, 135, 0, 0.24);
--cm-search-selected: rgba(191, 135, 0, 0.36);
--cm-token-class: #8250df;
--cm-token-property: #0969da;
--cm-token-enum: #953800;
--cm-token-string: #0a7f47;
--cm-token-number: #0550ae;
--cm-token-variable: #cf222e;
```

### Dark Mode (GitHub Soft Dark Theme)

```css
--bg: #0d1117;
--surface: #161b22;
--surface-2: #21262d;
--surface-3: #30363d;
--text: #e6edf3;
--muted: #8b949e;
--subtle: #6e7681;
--label: #8b949e;
--border: #30363d;
--border-strong: #484f58;
--accent: #58a6ff;
--accent-contrast: #0d1117;
--accent-2: #d29922;
--accent-soft: #0f2744;
--danger: #f85149;
--danger-soft: #3a1518;
--warning: #d29922;
--warning-soft: #332412;
--success: #3fb950;
--success-soft: #102c1a;
--shadow: 0 18px 42px rgba(1, 4, 9, 0.3);
--code-bg: #161b22;
--code-text: #c9d1d9;
--cm-bg: #161b22;
--cm-text: #c9d1d9;
--cm-gutter-bg: #0d1117;
--cm-gutter-text: #6e7681;
--cm-active-line: rgba(88, 166, 255, 0.08);
--cm-selection: rgba(56, 139, 253, 0.28);
--cm-search-match: rgba(187, 128, 9, 0.34);
--cm-search-selected: rgba(187, 128, 9, 0.48);
--cm-token-class: #d2a8ff;
--cm-token-property: #79c0ff;
--cm-token-enum: #ffa657;
--cm-token-string: #a5d6ff;
--cm-token-number: #79c0ff;
--cm-token-variable: #ff7b72;
```

### Anthropic Mode (Anthropic Theme)

```css
--bg: #f0eee6;
--surface: #faf9f5;
--surface-2: #e8e6dc;
--surface-3: #d1cfc5;
--text: #141413;
--muted: #3d3d3a;
--subtle: #87867f;
--label: #5e5d59;
--border: #1414131a;
--border-strong: #14141333;
--accent: #c6613f;
--accent-contrast: #ffffff;
--accent-2: #d97757;
--accent-soft: #f1ded6;
--danger: #c25b4e;
--danger-soft: #f3ded8;
--warning: #d9853b;
--warning-soft: #f4e5d3;
--success: #059669;
--success-soft: #deeee5;
--shadow: 0 16px 38px rgba(20, 20, 19, 0.10);
--code-bg: #ecebe4;
--code-text: #141413;
--cm-bg: #faf9f5;
--cm-text: #141413;
--cm-gutter-bg: #f0eee6;
--cm-gutter-text: #5e5d59;
--cm-active-line: rgba(198, 97, 63, 0.10);
--cm-selection: rgba(198, 97, 63, 0.22);
--cm-search-match: rgba(217, 133, 59, 0.28);
--cm-search-selected: rgba(217, 133, 59, 0.40);
--cm-token-class: #c6613f;
--cm-token-property: #5563c1;
--cm-token-enum: #d97757;
--cm-token-string: #059669;
--cm-token-number: #d9853b;
--cm-token-variable: #c25b4e;
```

The Anthropic theme is anchored to the live Anthropic homepage. Streamlit contributes the inline-code background `#ecebe4` and the success/editor green `#059669`; the provided `styles.css` contributes the editor blue `#5563c1`, amber `#d9853b`, and danger red `#c25b4e` because those semantic roles are not first-class homepage shell swatches.

## Component Rules

- Use icon-only buttons for compact shell controls and add tooltips with `title`.
- Use text buttons only for clear commands such as `Build`, `Sync`, `Open Project`, and `Start Local API`.
- Use segmented controls for modes and themes.
- Use tabs for workspace contexts.
- Use checkboxes or toggles for binary service state.
- Use progress/status chips only when they carry real state.
- Keep all controls keyboard-focusable and sized consistently.
- Icons inherit `currentColor`; never hard-code icon strokes to black or white inside React components.

## Prototype Copy

Prototype text should name future surfaces without pretending they are complete. Use statuses such as `scaffold`, `planned`, `offline`, `local`, and `ready` instead of fake production metrics.

## Reference Sources

- Ollama announced its macOS and Windows desktop app with chat, file drag-and-drop, and multimodal support on 2025-07-30: `https://ollama.com/blog/new-app`.
- GitHub Desktop uses a repository bar, left workflow sidebar, and contextual action model: `https://docs.github.com/en/desktop/overview/creating-your-first-repository-using-github-desktop`.
- Anthropic homepage and live stylesheet: `https://www.anthropic.com/` and `https://cdn.prod.website-files.com/67ce28cfec624e2b733f8a52/css/ant-brand.shared.99b3c3efd.min.css`.
- Streamlit Anthropic live app: `https://advanced-theming-anthropic.streamlit.app/`.
- Streamlit Anthropic source config: `https://github.com/streamlit/docs/tree/main/python/concept-source/theming-overview-anthropic-light-inspried` and `.streamlit/config.toml` in that directory.
