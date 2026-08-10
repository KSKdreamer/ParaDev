import { isTranslationKey, type TranslationKey } from "./i18n";
import { moduleNavigationGroupKey } from "./moduleNavigationGroups";
import type {
  FeatureModule,
  ProjectBrowserFamily,
  ProjectBrowserPayload,
  ProjectDiagramNodeAuthoring,
  ProjectDiagramRelationship,
  ProjectDiagramSelectionDefault,
  ProjectTemplate,
  ProjectTemplatesPayload,
} from "./types";

const MODULE_ACCENT_COUNT = 10;
const DIAGRAM_TAB_PREFIX = "diagram:";

export type ProjectDiagramFamilyCapability = {
  readonly authoringKind?: "diagram-node" | "module";
  readonly editable: boolean;
  readonly familyId: string;
  readonly initialScope: "project" | "selected-entity";
  readonly readOnlyReasonKey?: TranslationKey;
  readonly renderer: string;
  readonly sdkFamily: string;
  readonly nodeAuthoring?: ProjectDiagramNodeAuthoring;
  readonly relationships: readonly ProjectDiagramRelationship[];
  readonly selectionDefaults: readonly ProjectDiagramSelectionDefault[];
  readonly showWhenSourceHidden?: boolean;
  readonly scopeAuthoringKind?: "collection";
  readonly sourceBacked: true;
  readonly title: string;
  readonly titleKey?: TranslationKey;
};

const DIAGRAM_RENDERER_UI: Readonly<
  Record<
    string,
    {
      readonly readOnlyReasonKey?: TranslationKey;
      readonly titleKey: TranslationKey;
    }
  >
> = {
  doctrine: {
    titleKey: "workspace.diagram.family.doctrineTree",
  },
  "focus-tree": {
    titleKey: "workspace.diagram.family.focusTree",
  },
  "mio-trait": {
    readOnlyReasonKey: "workspace.diagram.mio.readOnlyReason",
    titleKey: "workspace.diagram.family.mioTree",
  },
  technology: {
    titleKey: "workspace.diagram.family.technologyTree",
  },
};

export function familyIdFromTemplateFamily(family: string): string {
  return family.trim().toLowerCase().replace(/_/g, "-");
}

export function canonicalFamilyId(family: string, fallbackFamily = ""): string {
  const clean = family.trim().toLowerCase().replace(/_/g, "-");
  const fallback = fallbackFamily.trim().toLowerCase().replace(/_/g, "-");
  return clean || fallback;
}

export function moduleTitleKeyForFamilyId(
  familyId: string,
  browser: ProjectBrowserPayload | null = null,
): TranslationKey | undefined {
  return moduleTitleKeyForFamily(projectBrowserFamily(browser, familyId));
}

export function moduleTitleKeyForFamily(
  family: ProjectBrowserFamily | undefined,
): TranslationKey | undefined {
  return isTranslationKey(family?.title_key) ? family.title_key : undefined;
}

export function projectDiagramFamilyCapability(
  browser: ProjectBrowserPayload | null,
  familyId: string,
): ProjectDiagramFamilyCapability | undefined {
  const family = projectBrowserFamily(browser, familyId);
  const diagram = family?.diagram;
  if (!family || !diagram) {
    return undefined;
  }
  const rendererUi = DIAGRAM_RENDERER_UI[diagram.renderer];
  const authoringKind =
    diagram.authoring_kind === "module" || diagram.authoring_kind === "diagram-node"
      ? diagram.authoring_kind
      : undefined;
  const scopeAuthoringKind =
    diagram.scope_authoring_kind === "collection"
      ? diagram.scope_authoring_kind
      : undefined;
  return {
    ...(authoringKind ? { authoringKind } : {}),
    editable: diagram.editable,
    familyId: canonicalFamilyId(family.id, family.family),
    initialScope: diagram.initial_scope === "project" ? "project" : "selected-entity",
    ...(rendererUi?.readOnlyReasonKey
      ? { readOnlyReasonKey: rendererUi.readOnlyReasonKey }
      : {}),
    renderer: diagram.renderer,
    sdkFamily: diagram.id,
    ...(diagram.node_authoring
      ? { nodeAuthoring: diagram.node_authoring }
      : {}),
    relationships: diagram.relationships ?? [],
    selectionDefaults: diagram.selection_defaults ?? [],
    ...(diagram.show_when_source_hidden === true
      ? { showWhenSourceHidden: true }
      : {}),
    ...(scopeAuthoringKind ? { scopeAuthoringKind } : {}),
    sourceBacked: true,
    title: diagram.title,
    ...(rendererUi?.titleKey ? { titleKey: rendererUi.titleKey } : {}),
  };
}

export function projectDiagramSelectionValues(
  capability: ProjectDiagramFamilyCapability | undefined,
  selectedNode: Readonly<object> | null | undefined,
): Record<string, string> {
  if (!capability || !selectedNode) {
    return {};
  }
  const node = selectedNode as Readonly<Record<string, unknown>>;
  const values: Record<string, string> = {};
  for (const rule of capability.selectionDefaults) {
    const sourceValue = node[rule.source];
    let value: string;
    if (typeof sourceValue === "number" && Number.isFinite(sourceValue)) {
      const offset =
        typeof rule.offset === "number" && Number.isFinite(rule.offset)
          ? rule.offset
          : 0;
      value = String(sourceValue + offset);
    } else if (
      typeof sourceValue === "string" ||
      typeof sourceValue === "boolean"
    ) {
      if (rule.offset) {
        continue;
      }
      value = String(sourceValue);
    } else {
      continue;
    }
    if (!value.trim()) {
      continue;
    }
    values[rule.field] = (rule.template ?? "{value}").replace("{value}", value);
  }
  return values;
}

export function projectDiagramNodeIntent(
  capability: ProjectDiagramFamilyCapability | undefined,
  selectedNode: Readonly<object> | null | undefined,
): Record<string, unknown> | null {
  if (!capability?.nodeAuthoring) {
    return null;
  }
  if (
    !selectedNode ||
    (selectedNode as Readonly<Record<string, unknown>>).editable !== true
  ) {
    return capability.nodeAuthoring.requires_selection ? null : {};
  }
  const node = selectedNode as Readonly<Record<string, unknown>>;
  const values: Record<string, unknown> = {};
  for (const rule of capability.nodeAuthoring.selection_defaults) {
    const sourceValue = node[rule.source];
    let value: string | number | boolean;
    if (typeof sourceValue === "number" && Number.isFinite(sourceValue)) {
      const offset =
        typeof rule.offset === "number" && Number.isFinite(rule.offset)
          ? rule.offset
          : 0;
      value = sourceValue + offset;
    } else if (
      typeof sourceValue === "string" ||
      typeof sourceValue === "boolean"
    ) {
      if (rule.offset) {
        return null;
      }
      value = sourceValue;
    } else {
      return null;
    }
    if (typeof value === "string" && !value.trim()) {
      return null;
    }
    values[rule.field] = rule.template
      ? rule.template.replace("{value}", String(value))
      : value;
  }
  return values;
}

export function projectDiagramTitleKeyForFamilyId(
  browser: ProjectBrowserPayload | null,
  familyId: string,
): TranslationKey | undefined {
  return projectDiagramFamilyCapability(browser, familyId)?.titleKey;
}

export function supportsProjectDiagramFamily(
  browser: ProjectBrowserPayload | null,
  familyId: string,
): boolean {
  return projectDiagramFamilyCapability(browser, familyId) !== undefined;
}

export function diagramTabIdForModule(moduleId: string): string {
  return `${DIAGRAM_TAB_PREFIX}${canonicalFamilyId(moduleId)}`;
}

export function isDiagramTabId(tabId: string): boolean {
  return tabId.startsWith(DIAGRAM_TAB_PREFIX);
}

export function moduleIdForDiagramTabId(tabId: string): string {
  return isDiagramTabId(tabId) ? tabId.slice(DIAGRAM_TAB_PREFIX.length) : tabId;
}

export function moduleAccentIndex(moduleId: string): number {
  let hash = 0;
  for (let index = 0; index < moduleId.length; index += 1) {
    hash = (hash * 31 + moduleId.charCodeAt(index)) >>> 0;
  }
  return hash % MODULE_ACCENT_COUNT;
}

export function applyModuleOrder<T extends { id: string }>(
  modules: T[],
  order: string[],
): T[] {
  if (order.length === 0) {
    return modules;
  }
  const modulesById = new Map(modules.map((module) => [module.id, module]));
  const ordered = order
    .map((id) => modulesById.get(id))
    .filter((module): module is T => Boolean(module));
  const orderedIds = new Set(ordered.map((module) => module.id));
  return [
    ...ordered,
    ...modules.filter((module) => !orderedIds.has(module.id)),
  ];
}

export function moveModuleBefore<T extends { id: string }>(
  modules: T[],
  fromId: string,
  toId: string,
): T[] {
  if (fromId === toId) {
    return modules;
  }
  const moving = modules.find((module) => module.id === fromId);
  if (!moving || !modules.some((module) => module.id === toId)) {
    return modules;
  }
  const withoutMoving = modules.filter((module) => module.id !== fromId);
  const targetIndex = withoutMoving.findIndex((module) => module.id === toId);
  return [
    ...withoutMoving.slice(0, targetIndex),
    moving,
    ...withoutMoving.slice(targetIndex),
  ];
}

export function projectBrowserForFamily(
  browser: ProjectBrowserPayload | null,
  familyId: string,
): ProjectBrowserPayload | null {
  if (!browser) {
    return null;
  }
  const family = projectBrowserFamily(browser, familyId);
  const aliases = family
    ? projectBrowserFamilyAliases(family)
    : new Set([canonicalFamilyId(familyId)]);
  return {
    ...browser,
    families: browser.families.filter((candidate) =>
      projectBrowserFamilyMatches(candidate, aliases),
    ),
    items: browser.items.filter(
      (item) =>
        aliases.has(canonicalFamilyId(item.family_id)) ||
        aliases.has(canonicalFamilyId(item.family)),
    ),
  };
}

export function projectBrowserFamily(
  browser: ProjectBrowserPayload | null,
  familyId: string,
): ProjectBrowserFamily | undefined {
  const aliases = new Set([canonicalFamilyId(familyId)]);
  return browser?.families.find((family) =>
    projectBrowserFamilyMatches(family, aliases),
  );
}

export function workspaceFamilyIdForFamily(
  browser: ProjectBrowserPayload | null,
  family: string,
): string {
  const discovered = projectBrowserFamily(browser, family);
  return canonicalFamilyId(discovered?.id ?? family);
}

export function modulesForProjectState(
  browser: ProjectBrowserPayload | null,
  templates: ProjectTemplatesPayload | null,
  baseModules: FeatureModule[],
): FeatureModule[] {
  const discoveredFamilies = browser?.families ?? [];
  const hiddenFamilyIds = new Set(
    discoveredFamilies
      .filter((family) => !isVisibleWorkspaceFamily(family))
      .map((family) => canonicalFamilyId(family.id, family.family)),
  );
  const visibleDiscoveredFamilies = discoveredFamilies.filter(
    (family) =>
      isVisibleWorkspaceFamily(family) &&
      !hiddenFamilyIds.has(canonicalFamilyId(family.id, family.family)),
  );
  const discoveredById = aggregateDiscoveredFamilies(visibleDiscoveredFamilies);
  const templateFamilyIds = new Set(
    (templates?.templates ?? []).map((template) =>
      familyIdFromTemplate(template, discoveredFamilies),
    ),
  );
  const visibleTemplateFamilyIds = new Set(
    [...templateFamilyIds].filter((familyId) => !hiddenFamilyIds.has(familyId)),
  );
  const knownIds = new Set(baseModules.map((module) => module.id));
  const hasProjectState = browser !== null || templates !== null;

  const known = baseModules
    .filter(
      (module) =>
        !hasProjectState ||
        discoveredById.has(module.id) ||
        visibleTemplateFamilyIds.has(module.id),
    )
    .map((module) => {
      const family = discoveredById.get(module.id);
      const hasTemplate = visibleTemplateFamilyIds.has(module.id);
      const titleKey = moduleTitleKeyForFamily(family);
      return {
        ...module,
        ...(family?.diagram ? { diagram: family.diagram } : {}),
        ...(family ? { groupKey: moduleNavigationGroupKey(family.group) } : {}),
        ...(titleKey ? { titleKey } : {}),
        status:
          family && family.item_count > 0
            ? ("ready" as const)
            : hasTemplate
              ? ("scaffold" as const)
              : module.status,
        count: family?.item_count,
      };
    });

  const extraIds = new Set<string>();
  for (const family of visibleDiscoveredFamilies) {
    const familyId = canonicalFamilyId(family.id, family.family);
    if (!knownIds.has(familyId)) {
      extraIds.add(familyId);
    }
  }
  for (const familyId of visibleTemplateFamilyIds) {
    if (!knownIds.has(familyId)) {
      extraIds.add(familyId);
    }
  }

  const extra = [...extraIds]
    .map<FeatureModule>((familyId) => {
      const family = discoveredById.get(familyId);
      const titleKey = moduleTitleKeyForFamily(family);
      return {
        id: familyId,
        ...(family?.diagram ? { diagram: family.diagram } : {}),
        groupKey: moduleNavigationGroupKey(family?.group),
        ...(titleKey
          ? { titleKey }
          : { label: family?.title ?? titleFromFamilyId(familyId) }),
        status: family && family.item_count > 0 ? "ready" : "scaffold",
        count: family?.item_count,
      };
    })
    .sort((left, right) =>
      (left.label ?? left.id).localeCompare(
        right.label ?? right.id,
        undefined,
        { sensitivity: "base" },
      ),
    );

  return [...known, ...extra];
}

function isVisibleWorkspaceFamily(family: ProjectBrowserFamily): boolean {
  if (family.visible !== false) {
    return true;
  }
  return family.diagram?.show_when_source_hidden === true;
}

function familyIdFromTemplate(
  template: ProjectTemplate,
  families: ProjectBrowserFamily[],
): string {
  const declaredFamilyId = canonicalFamilyId(template.family_id ?? "");
  if (declaredFamilyId) {
    return declaredFamilyId;
  }
  const aliases = new Set([canonicalFamilyId(template.family)]);
  const discovered = families.find((family) =>
    projectBrowserFamilyMatches(family, aliases),
  );
  return canonicalFamilyId(discovered?.id ?? template.family);
}

function projectBrowserFamilyAliases(
  family: ProjectBrowserFamily,
): Set<string> {
  return new Set(
    [
      family.id,
      family.family,
      ...(family.aliases ?? []),
      family.diagram?.id,
      ...(family.diagram?.aliases ?? []),
    ]
      .filter((value): value is string => Boolean(value))
      .map((value) => canonicalFamilyId(value)),
  );
}

function projectBrowserFamilyMatches(
  family: ProjectBrowserFamily,
  aliases: ReadonlySet<string>,
): boolean {
  for (const alias of projectBrowserFamilyAliases(family)) {
    if (aliases.has(alias)) {
      return true;
    }
  }
  return false;
}

function aggregateDiscoveredFamilies(
  families: ProjectBrowserFamily[],
): Map<string, ProjectBrowserFamily> {
  const discoveredById = new Map<string, ProjectBrowserFamily>();
  for (const family of families) {
    const familyId = canonicalFamilyId(family.id, family.family);
    const existing = discoveredById.get(familyId);
    if (!existing) {
      discoveredById.set(familyId, {
        ...family,
        id: familyId,
      });
      continue;
    }
    discoveredById.set(familyId, {
      ...existing,
      ...(existing.diagram
        ? {}
        : family.diagram
          ? { diagram: family.diagram }
          : {}),
      item_count: existing.item_count + family.item_count,
      source_count: existing.source_count + family.source_count,
      layouts: Array.from(
        new Set([...existing.layouts, ...family.layouts]),
      ).sort(),
    });
  }
  return discoveredById;
}

function titleFromFamilyId(familyId: string): string {
  return familyId
    .replace(/[-_]+/g, " ")
    .split(" ")
    .filter(Boolean)
    .map((word) => `${word.charAt(0).toUpperCase()}${word.slice(1)}`)
    .join(" ");
}
