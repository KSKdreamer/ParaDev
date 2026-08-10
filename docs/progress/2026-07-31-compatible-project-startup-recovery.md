# Compatible project startup recovery

Date: 2026-07-31

## Outcome

ParaDev no longer strands the user on onboarding when its saved project path
points to a missing or pre-refactor PIHC3 checkout while another compatible
project is discoverable.

Startup now:

1. tries the saved path;
2. makes one registry discovery request after that path fails;
3. opens the discovered compatible project;
4. persists the recovered project path; and
5. shows a concise, non-blocking recovery notice.

The notice keeps the previous path, recovered path, and localized bridge error
in hover detail without exposing the full extension traceback in the normal
sidebar text.

Manual project selection remains strict. A failed user-selected candidate does
not trigger fallback and cannot replace an already open workspace.

## Rendered PIHC3 verification

The native-web bridge was started with the saved path pointing at the obsolete
`heavenbase-0116` PIHC3 checkout. That checkout failed extension activation on
its retired `retired_families` declaration. ParaDev then discovered and opened
the current project at:

`/Users/magolor/Projects/ParaDev/ParaDev-3/projects/PIHC3`

The rendered workspace exposed 51 visible authoring families, including
focuses, technologies, doctrines, MIOs, inventory items, state lore, and
superevents. The persisted desktop app config was read back and contained the
recovered current PIHC3 path.

## Verification

- Focused desktop recovery, panel, shell, and localization suite: 119 passed.
- Complete desktop Vitest gate: 1,424 passed.
- Production TypeScript/Vite build: passed.
- Native bridge, desktop backend, PIHC3 extensibility, and live-tree hygiene:
  139 passed.
- PIHC3 was already restored to its complete 14,617-module, 35,139-artifact
  full-build state before this GUI slice; no project source or build output was
  changed by startup recovery.
