# ParaDev Docs Menu

Status: active index

Date: 2026-06-06

Purpose: give agents and contributors one canonical reading path after the legacy-doc cleanup. Read this file before using any other document under `docs/`.

## Authority Order

When documents overlap, use this order:

1. [goals/final-architecture.md](goals/final-architecture.md) is the active compiler and source-model architecture.
2. [goals/README.md](goals/README.md) is the roadmap and milestone framing.
3. [plans/](plans/) files connect the durable roadmap to active Linear execution.
4. [architecture/interfaces.md](architecture/interfaces.md) is the current surface-boundary and desktop shell architecture.
5. [resources/](resources/) files are evidence and background. They are not implementation contracts when they conflict with the active architecture.
6. [techstack/ui/](techstack/ui/) files govern the build-time React/Vite UI and packaged system-WebView application only.

## Fast Reading Path

For a new implementation agent:

1. Read [goals/final-architecture.md](goals/final-architecture.md).
2. Read [architecture/interfaces.md](architecture/interfaces.md).
3. Read [resources/02-heavenbase-architecture.md](resources/02-heavenbase-architecture.md) for HeavenBase and CLI/config direction.
4. Read [resources/03-hoi4-domain-and-entity-model.md](resources/03-hoi4-domain-and-entity-model.md) for HOI4 families and artifact expectations.
5. Read [goals/short-term-plan.md](goals/short-term-plan.md) for the next implementation slices.
6. Read [workflows/README.md](workflows/README.md) for the active implementation loop.

For product or planning agents:

1. Read [goals/README.md](goals/README.md).
2. Read [goals/design-considerations.md](goals/design-considerations.md).
3. Read [goals/final-architecture.md](goals/final-architecture.md).
4. Read [resources/01-product-vision-and-background.md](resources/01-product-vision-and-background.md).
5. Read [plans/linear.md](plans/linear.md) for current Linear execution.

For HoI4 modders and package users:

1. Start with [user-manual/README.md](user-manual/README.md).
2. Use [workflows/build-flow.md](workflows/build-flow.md) only when you need the current detailed SDK/CLI build contract.
3. Use [resources/03-hoi4-domain-and-entity-model.md](resources/03-hoi4-domain-and-entity-model.md) for deeper HoI4 family context.
4. Use [resources/04-pihc3-source-cutover.md](resources/04-pihc3-source-cutover.md) for the completed PIHC3 source cutover and clean-layout boundary.

For GUI agents:

1. Read [architecture/interfaces.md](architecture/interfaces.md).
2. Read [techstack/ui/style.md](techstack/ui/style.md).
3. Read [techstack/ui/gui-spec.md](techstack/ui/gui-spec.md).
4. Do not add GUI-side HOI4 business logic; call SDK/REST contracts.

For migration agents:

1. Read [resources/00-resources-and-references.md](resources/00-resources-and-references.md).
2. Read [resources/04-pihc3-source-cutover.md](resources/04-pihc3-source-cutover.md).
3. Read [resources/03-hoi4-domain-and-entity-model.md](resources/03-hoi4-domain-and-entity-model.md).
4. Treat legacy repositories as evidence, not implementation bases.

## Document Map

| File | Role | Read when |
| --- | --- | --- |
| [goals/README.md](goals/README.md) | Roadmap and milestone framing. | Choosing what to build next. |
| [goals/design-considerations.md](goals/design-considerations.md) | Problem statement and architecture rationale. | Rechecking why modules, collections, and artifacts exist. |
| [goals/final-architecture.md](goals/final-architecture.md) | Active final architecture for source modules, slots, collections, artifacts, PDX core, and surfaces. | Designing or implementing public compiler APIs. |
| [goals/short-term-plan.md](goals/short-term-plan.md) | Linear-backed near-term implementation plan. | Starting foundation work. |
| [plans/README.md](plans/README.md) | Planning index and main feature-loop goal. | Connecting local plans to Linear. |
| [plans/linear.md](plans/linear.md) | Active Linear issue map and sync notes. | Updating issue status or creating follow-up issues. |
| [architecture/interfaces.md](architecture/interfaces.md) | Surface boundaries for SDK, CLI, MCP, REST, LSP, VS Code, and desktop. | Touching integration surfaces or desktop packaging. |
| [user-manual/README.md](user-manual/README.md) | User-facing manual interface for HoI4 modders using SDK/CLI workflows. | Starting or continuing a ParaDev project as a user. |
| [resources/00-resources-and-references.md](resources/00-resources-and-references.md) | Local paths, legacy repos, external references, and refresh checklist. | Looking up evidence sources. |
| [resources/01-product-vision-and-background.md](resources/01-product-vision-and-background.md) | Product scope, target users, and principles. | Explaining the product or validating scope. |
| [resources/02-heavenbase-architecture.md](resources/02-heavenbase-architecture.md) | HeavenBase layer model, data model, CLI/MCP strategy. | Integrating config, CLI, MCP, schemas, indexes, or storage. |
| [resources/03-hoi4-domain-and-entity-model.md](resources/03-hoi4-domain-and-entity-model.md) | HOI4 family inventory, localization, assets, map, references, editor payloads. | Implementing game-package families. |
| [resources/04-pihc3-source-cutover.md](resources/04-pihc3-source-cutover.md) | Current PIHC3 semantic source layout and completed cutover boundary. | Editing, auditing, or packaging PIHC3 sources. |
| [resources/05-project-manifest.md](resources/05-project-manifest.md) | First `paradev.yaml` schema and discovery behavior. | Loading projects or touching project CLI/SDK contracts. |
| [techstack/ui/style.md](techstack/ui/style.md) | Visual style and shell interaction rules. | Editing `apps/desktop/src` styles or layout. |
| [techstack/ui/gui-spec.md](techstack/ui/gui-spec.md) | Concrete GUI shell component/spec rules. | Editing React components or UI primitives. |
| [workflows/README.md](workflows/README.md) | Feature, test, package, five-hour checkpoint, and Git workflows. | Running a work loop or handing off to another agent. |
| [workflows/build-flow.md](workflows/build-flow.md) | Current SDK and CLI build flow for the minimal demo project. | Running dry builds, artifact emission, manifest emission, or profile overrides. |
| [progress/README.md](progress/README.md) | Progress note naming and template. | Writing five-hour summaries. |

## Known Review Notes

- `goals/final-architecture.md` supersedes older metadata examples that still mention required `id`; the active metadata uses `type`, inferred folder identity, optional `game_id`, and optional `collection`/`owner`/`priority`.
- The current desktop runtime is the Python wheel's loopback API plus the macOS system WebView. React/Vite is build-time only, Chromium `--app` is an explicit fallback, and Windows native packaging is deferred.
- Version-sensitive HOI4 claims must be refreshed from the local game install, current wiki pages, or official patch notes before implementation.
- Use `rtk` command prefixes in local agent sessions, per repository instructions.
