import { Bot, FolderCog, Hammer, Layers3, Terminal } from "lucide-react";
import type { FeatureModule, PanelOption, ProjectOption, RailItem, SurfaceRow, WorkspaceTab } from "../types";

export const defaultRailId = "projects";

export const railItems: RailItem[] = [
  { id: "management", labelKey: "rail.management", icon: FolderCog },
  { id: "projects", labelKey: "rail.projects", icon: Layers3 },
  { id: "agents", labelKey: "rail.agents", icon: Bot },
  { id: "build", labelKey: "rail.build", icon: Hammer },
  { id: "developer", labelKey: "rail.developer", icon: Terminal }
];

export const projectOptions: ProjectOption[] = [
  {
    id: "minimal_hoi4",
    projectId: "minimal_hoi4",
    name: "Minimal HOI4 Project",
    path: "demos/assets/projects/minimal",
    sourceRoots: ["demos/assets/projects/minimal/src"],
    outputRoot: "demos/assets/projects/minimal/build/mod",
    buildRoot: "demos/assets/projects/minimal/.paradev/.cache/build",
    manifest: "demos/assets/projects/minimal/paradev.yaml"
  }
];

export const workspaceTabs: WorkspaceTab[] = [
  { id: "countries", titleKey: "modules.countries.title", kind: "module" },
  { id: "characters", titleKey: "modules.characters.title", kind: "module" },
  { id: "decisions", titleKey: "modules.decisions.title", kind: "module" },
  { id: "divisions", titleKey: "modules.divisions.title", kind: "module" },
  { id: "focuses", titleKey: "modules.focuses.title", kind: "module" },
  { id: "ideas", titleKey: "modules.ideas.title", kind: "module" },
  { id: "modifiers", titleKey: "modules.modifiers.title", kind: "module" },
  { id: "map", titleKey: "modules.map.title", kind: "module" },
  { id: "states", titleKey: "modules.states.title", kind: "module" },
  { id: "events", titleKey: "modules.events.title", kind: "module" },
  { id: "technologies", titleKey: "modules.technologies.title", kind: "module" },
  { id: "equipment", titleKey: "modules.equipment.title", kind: "module" },
  { id: "military-industrial-organizations", titleKey: "modules.militaryIndustrialOrganizations.title", kind: "module" },
  { id: "buildings", titleKey: "modules.buildings.title", kind: "module" },
  { id: "scripted-effects", titleKey: "modules.scriptedEffects.title", kind: "module" },
  { id: "scripted-triggers", titleKey: "modules.scriptedTriggers.title", kind: "module" },
  { id: "localization", titleKey: "modules.localization.title", kind: "module" },
  { id: "assets", titleKey: "modules.assets.title", kind: "module" },
  { id: "music", titleKey: "modules.music.title", kind: "module" },
  { id: "config-general", titleKey: "config.general.title", kind: "config" },
  { id: "config-appearance", titleKey: "config.appearance.title", kind: "config" },
  { id: "config-models", titleKey: "config.models.title", kind: "config" },
  { id: "config-projects", titleKey: "config.projects.title", kind: "config" },
  { id: "config-module-defaults", titleKey: "config.moduleDefaults.title", kind: "config" },
  { id: "config-dependencies", titleKey: "config.dependencies.title", kind: "config" }
];

export const featureModules: FeatureModule[] = [
  { id: "countries", titleKey: "modules.countries.title", descriptionKey: "modules.countries.description", status: "scaffold" },
  { id: "characters", titleKey: "modules.characters.title", descriptionKey: "modules.characters.description", status: "scaffold" },
  { id: "decisions", titleKey: "modules.decisions.title", descriptionKey: "modules.decisions.description", status: "planned" },
  { id: "divisions", titleKey: "modules.divisions.title", descriptionKey: "modules.divisions.description", status: "planned" },
  { id: "focuses", titleKey: "modules.focuses.title", descriptionKey: "modules.focuses.description", status: "scaffold" },
  { id: "ideas", titleKey: "modules.ideas.title", descriptionKey: "modules.ideas.description", status: "planned" },
  { id: "modifiers", titleKey: "modules.modifiers.title", descriptionKey: "modules.modifiers.description", status: "planned" },
  { id: "map", titleKey: "modules.map.title", descriptionKey: "modules.map.description", status: "planned" },
  { id: "states", titleKey: "modules.states.title", descriptionKey: "modules.states.description", status: "planned" },
  { id: "events", titleKey: "modules.events.title", descriptionKey: "modules.events.description", status: "planned" },
  { id: "technologies", titleKey: "modules.technologies.title", descriptionKey: "modules.technologies.description", status: "planned" },
  { id: "equipment", titleKey: "modules.equipment.title", descriptionKey: "modules.equipment.description", status: "planned" },
  { id: "military-industrial-organizations", titleKey: "modules.militaryIndustrialOrganizations.title", descriptionKey: "modules.militaryIndustrialOrganizations.description", status: "planned" },
  { id: "buildings", titleKey: "modules.buildings.title", descriptionKey: "modules.buildings.description", status: "planned" },
  { id: "scripted-effects", titleKey: "modules.scriptedEffects.title", descriptionKey: "modules.scriptedEffects.description", status: "scaffold" },
  { id: "scripted-triggers", titleKey: "modules.scriptedTriggers.title", descriptionKey: "modules.scriptedTriggers.description", status: "scaffold" },
  { id: "localization", titleKey: "modules.localization.title", descriptionKey: "modules.localization.description", status: "planned" },
  { id: "assets", titleKey: "modules.assets.title", descriptionKey: "modules.assets.description", status: "planned" },
  { id: "music", titleKey: "modules.music.title", descriptionKey: "modules.music.description", status: "planned" }
];

export const configOptions: PanelOption[] = [
  { id: "config-general", groupKey: "config.group.basic", titleKey: "config.general.title" },
  { id: "config-appearance", groupKey: "config.group.basic", titleKey: "config.appearance.title" },
  { id: "config-models", groupKey: "config.group.basic", titleKey: "config.models.title" },
  { id: "config-projects", groupKey: "config.group.project", titleKey: "config.projects.title" },
  { id: "config-module-defaults", groupKey: "config.group.project", titleKey: "config.moduleDefaults.title" },
  { id: "config-dependencies", groupKey: "config.group.dependency", titleKey: "config.dependencies.title" }
];

export const surfaceRows: SurfaceRow[] = [
  { id: "sdk", titleKey: "surface.sdk.title", runtime: "python", status: "ready", path: "src/paradev/sdk" },
  { id: "mcp", titleKey: "surface.mcp.title", runtime: "heavenbase-mcp", status: "scaffold", path: "src/paradev/surfaces/mcp.py" },
  { id: "cli", titleKey: "surface.cli.title", runtime: "python-typer-rich", status: "ready", path: "src/paradev/cli.py" },
  { id: "rest", titleKey: "surface.rest.title", runtime: "fastapi optional", status: "scaffold", path: "src/paradev/surfaces/rest.py" },
  { id: "openapi", titleKey: "surface.openapi.title", runtime: "json", status: "scaffold", path: "src/paradev/api" },
  { id: "bundle", titleKey: "surface.bundle.title", runtime: "python-bundle", status: "planned", path: "src/paradev/surfaces/bundle.py" },
  { id: "frontend", titleKey: "surface.frontend.title", runtime: "react-vite", status: "ready", path: "apps/desktop/src" },
  { id: "desktop", titleKey: "surface.desktop.title", runtime: "python-system-webview", status: "ready", path: "src/paradev/gui.py" },
  { id: "lsp", titleKey: "surface.lsp.title", runtime: "python-lsp", status: "planned", path: "src/paradev/lsp" },
  { id: "vscode", titleKey: "surface.vscode.title", runtime: "typescript-vscode", status: "planned", path: "packages/vscode-paradev" }
];
