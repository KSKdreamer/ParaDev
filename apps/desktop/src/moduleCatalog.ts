import { canonicalFamilyId, projectBrowserFamily } from "./projectModules";
import type {
  ProjectCatalogQueryPayload,
  ProjectCatalogRow,
} from "./services/paradev";
import type {
  ProjectBrowserFamily,
  ProjectBrowserItem,
  ProjectBrowserPayload,
  ProjectBrowserSource,
} from "./types";

export const MODULE_CATALOG_PAGE_SIZE = 100;

export type ModuleCatalogFamilyState = {
  projectRoot: string;
  family: string;
  rows: ProjectCatalogRow[];
  totalCount: number;
  filteredCount: number;
  hasMore: boolean;
  nextOffset: number | null;
  loading: boolean;
  error: string;
};

export function moduleCatalogFamilyKey(
  projectRoot: string,
  familyId: string,
): string {
  return `${projectRoot.trim()}::${canonicalFamilyId(familyId)}`;
}

export function loadingModuleCatalogFamilyState(
  current: ModuleCatalogFamilyState | undefined,
  projectRoot: string,
  family: string,
): ModuleCatalogFamilyState {
  const matchesIdentity = moduleCatalogStateMatches(
    current,
    projectRoot,
    family,
  );
  return {
    projectRoot: projectRoot.trim(),
    family: family.trim(),
    rows: matchesIdentity ? current.rows : [],
    totalCount: matchesIdentity ? current.totalCount : 0,
    filteredCount: matchesIdentity ? current.filteredCount : 0,
    hasMore: matchesIdentity ? current.hasMore : false,
    nextOffset: matchesIdentity ? current.nextOffset : null,
    loading: true,
    error: "",
  };
}

export function moduleCatalogFamilyStateWithPage(
  current: ModuleCatalogFamilyState | undefined,
  payload: ProjectCatalogQueryPayload,
  projectRoot: string,
  family: string,
): ModuleCatalogFamilyState {
  const append = payload.page.offset > 0;
  const canAppend =
    append &&
    moduleCatalogStateMatches(current, projectRoot, family) &&
    current.nextOffset === payload.page.offset;
  if (append && !canAppend) {
    return {
      ...loadingModuleCatalogFamilyState(current, projectRoot, family),
      loading: false,
      error:
        "Catalog paging response was out of sequence. Reload the module list.",
    };
  }
  return {
    projectRoot: projectRoot.trim(),
    family: family.trim(),
    rows: mergeProjectCatalogRows(canAppend ? current.rows : [], payload.rows),
    totalCount: payload.total_count,
    filteredCount: payload.filtered_count,
    hasMore: payload.page.has_more,
    nextOffset: payload.page.next_offset,
    loading: false,
    error: "",
  };
}

export function moduleCatalogFamilyStateWithError(
  current: ModuleCatalogFamilyState | undefined,
  projectRoot: string,
  family: string,
  error: string,
): ModuleCatalogFamilyState {
  return {
    ...loadingModuleCatalogFamilyState(current, projectRoot, family),
    loading: false,
    error: error.trim(),
  };
}

export function moduleCatalogFamilyStateWithHydratedRow(
  current: ModuleCatalogFamilyState,
  row: ProjectCatalogRow,
): ModuleCatalogFamilyState {
  const existing = current.rows.find(
    (candidate) => candidate.target_id === row.target_id,
  );
  const hydratedData = hydratedModuleCatalogData(row, current.family);
  if (
    !existing ||
    !hydratedData ||
    catalogModuleId(existing) !== stringValue(hydratedData.module_id)
  ) {
    return current;
  }
  return {
    ...current,
    rows: mergeProjectCatalogRows(current.rows, [row]),
  };
}

export function moduleCatalogFamilyStateWithDiscoveredRow(
  current: ModuleCatalogFamilyState,
  row: ProjectCatalogRow,
): ModuleCatalogFamilyState {
  return {
    ...current,
    rows: mergeProjectCatalogRows(current.rows, [row]),
  };
}

export function moduleCatalogTargetIdForEntity(
  state: ModuleCatalogFamilyState | undefined,
  entityId: string,
): string | null {
  if (!state) {
    return null;
  }
  const row = state.rows.find((candidate) =>
    moduleCatalogRowMatchesEntity(candidate, entityId),
  );
  return row && !hydratedModuleCatalogData(row, state.family)
    ? row.target_id
    : null;
}

export function moduleCatalogRowMatchesEntity(
  row: ProjectCatalogRow,
  entityId: string,
): boolean {
  return catalogModuleId(row) === moduleCatalogModuleIdForEntity(entityId);
}

export function moduleCatalogRowHasHydratedData(
  row: ProjectCatalogRow,
  expectedFamily: string,
): boolean {
  return Boolean(hydratedModuleCatalogData(row, expectedFamily));
}

export function moduleCatalogModuleIdForEntity(entityId: string): string {
  const value = entityId.trim();
  return value.startsWith("module:") ? value.slice("module:".length) : value;
}

export function moduleCatalogBrowser(
  baseBrowser: ProjectBrowserPayload,
  familyId: string,
  state: ModuleCatalogFamilyState,
): ProjectBrowserPayload {
  const baseFamily = projectBrowserFamily(baseBrowser, familyId);
  const baseItems = new Map(baseBrowser.items.map((item) => [item.id, item]));
  const items = state.rows.map((row) => {
    const item = projectBrowserItemFromCatalogRow(
      row,
      state.family,
      state.projectRoot,
      baseFamily?.id ?? familyId,
    );
    const baseItem = baseItems.get(item.id);
    if (!baseItem) {
      return baseFamily?.resource_slots
        ? { ...item, resource_slots: baseFamily.resource_slots }
        : item;
    }
    return {
      ...item,
      title: baseItem.title,
      localized_titles: baseItem.localized_titles,
      title_keys: baseItem.title_keys,
      sources: item.sources.map((source) => {
        const declared = baseItem.sources.find(
          (candidate) =>
            candidate.slot === source.slot &&
            normalizePath(candidate.relative_path || candidate.path) ===
              normalizePath(source.relative_path || source.path),
        );
        return declared?.slot_kinds
          ? { ...source, slot_kinds: [...declared.slot_kinds] }
          : source;
      }),
      ...(baseItem.image_targets?.length
        ? { image_targets: baseItem.image_targets }
        : {}),
      ...((baseItem.resource_slots ?? baseFamily?.resource_slots)
        ? {
            resource_slots:
              baseItem.resource_slots ?? baseFamily?.resource_slots,
          }
        : {}),
    };
  });
  return {
    ...baseBrowser,
    families: [moduleCatalogBrowserFamily(baseFamily, familyId, state, items)],
    items,
  };
}

export function projectBrowserItemFromCatalogRow(
  row: ProjectCatalogRow,
  fallbackFamily: string,
  projectRoot: string,
  presentationFamilyId: string,
): ProjectBrowserItem {
  const data = hydratedModuleCatalogData(row, fallbackFamily) ?? {};
  const moduleId = stringValue(data.module_id) || row.name;
  const family = stringValue(data.family) || fallbackFamily;
  const objectId = moduleObjectId(moduleId);
  const metadata = objectValue(data.metadata);
  const root = absoluteProjectPath(stringValue(data.root), projectRoot);
  const sources = moduleCatalogSources(data.source_slots, root, projectRoot);
  const collectionId = stringValue(data.collection_id);
  const declaredSourceRoot = stringValue(data.source_root);
  const sourceRoot = declaredSourceRoot
    ? absoluteProjectPath(declaredSourceRoot, projectRoot)
    : inferredModuleSourceRoot(root, family, objectId);
  const active =
    typeof data.active === "boolean"
      ? data.active
      : metadata.inactive !== true;
  return {
    id: `module:${moduleId}`,
    kind: "module",
    layout: "canonical",
    family_id: canonicalFamilyId(presentationFamilyId, family),
    family,
    object_id: objectId,
    module_id: moduleId,
    title: moduleCatalogTitle(metadata, objectId),
    root,
    relative_root: relativeProjectPath(projectRoot, root),
    ...(sourceRoot
      ? {
          source_root: sourceRoot,
          source_root_relative_path: relativeProjectPath(
            projectRoot,
            sourceRoot,
          ),
        }
      : {}),
    source_count: sources.length,
    sources,
    metadata,
    active,
    ...(collectionId ? { collection_id: collectionId } : {}),
  };
}

export function mergeProjectCatalogRows(
  current: readonly ProjectCatalogRow[],
  incoming: readonly ProjectCatalogRow[],
): ProjectCatalogRow[] {
  const rows = current.map(normalizedProjectCatalogRow);
  const indexByTargetId = new Map(
    rows.map((row, index) => [row.target_id, index]),
  );
  for (const candidate of incoming) {
    const row = normalizedProjectCatalogRow(candidate);
    const index = indexByTargetId.get(row.target_id);
    if (index === undefined) {
      indexByTargetId.set(row.target_id, rows.length);
      rows.push(row);
      continue;
    }
    const existing = rows[index];
    rows[index] =
      hydratedModuleCatalogData(existing) && !hydratedModuleCatalogData(row)
        ? existing
        : row;
  }
  return rows;
}

function moduleCatalogBrowserFamily(
  baseFamily: ProjectBrowserFamily | undefined,
  familyId: string,
  state: ModuleCatalogFamilyState,
  items: ProjectBrowserItem[],
): ProjectBrowserFamily {
  return {
    ...baseFamily,
    id: baseFamily?.id ?? canonicalFamilyId(familyId),
    family: baseFamily?.family ?? state.family,
    title: baseFamily?.title ?? moduleCatalogTitle({}, state.family),
    item_count: state.filteredCount,
    source_count:
      baseFamily?.source_count ??
      items.reduce((count, item) => count + item.source_count, 0),
    layouts: baseFamily?.layouts ?? ["canonical"],
  };
}

function moduleCatalogSources(
  value: unknown,
  root: string,
  projectRoot: string,
): ProjectBrowserSource[] {
  const slots = objectValue(value);
  const sources: ProjectBrowserSource[] = [];
  for (const slot of Object.keys(slots).sort()) {
    const paths = Array.isArray(slots[slot]) ? slots[slot] : [];
    for (const value of paths) {
      if (typeof value !== "string" || !value.trim()) {
        continue;
      }
      const path = absoluteModuleSourcePath(value.trim(), root);
      const name = path.split(/[\\/]/).at(-1) ?? path;
      const extension = name.includes(".")
        ? (name.split(".").at(-1)?.toLowerCase() ?? "")
        : "";
      sources.push({
        slot,
        name,
        path,
        relative_path: relativeProjectPath(projectRoot, path),
        extension,
      });
    }
  }
  return sources;
}

function absoluteModuleSourcePath(path: string, root: string): string {
  if (!root || isAbsolutePath(path)) {
    return normalizePath(path);
  }
  return `${normalizePath(root).replace(/\/+$/, "")}/${normalizePath(path).replace(/^\/+/, "")}`;
}

function relativeProjectPath(projectRoot: string, path: string): string {
  const root = normalizePath(projectRoot).replace(/\/+$/, "");
  const normalizedPath = normalizePath(path);
  if (!root || !path) {
    return "";
  }
  const caseInsensitive = isWindowsPath(root) || isWindowsPath(normalizedPath);
  const comparableRoot = caseInsensitive ? root.toLowerCase() : root;
  const comparablePath = caseInsensitive
    ? normalizedPath.toLowerCase()
    : normalizedPath;
  if (comparablePath === comparableRoot) {
    return ".";
  }
  return comparablePath.startsWith(`${comparableRoot}/`)
    ? normalizedPath.slice(root.length + 1)
    : normalizedPath;
}

function absoluteProjectPath(path: string, projectRoot: string): string {
  if (!path || isAbsolutePath(path)) {
    return normalizePath(path);
  }
  return `${normalizePath(projectRoot).replace(/\/+$/, "")}/${normalizePath(path).replace(/^\/+/, "")}`;
}

function inferredModuleSourceRoot(
  root: string,
  family: string,
  objectId: string,
): string {
  return moduleRootSource(root, family, objectId)?.sourceRoot ?? "";
}

function normalizePath(path: string): string {
  return path
    .trim()
    .replace(/\\/g, "/")
    .replace(/\/{2,}/g, (value, offset) => (offset === 0 ? "//" : "/"));
}

function isAbsolutePath(path: string): boolean {
  return (
    path.startsWith("/") ||
    /^[A-Za-z]:[\\/]/.test(path) ||
    /^[\\/]{2}[^\\/]/.test(path)
  );
}

function isWindowsPath(path: string): boolean {
  return /^[A-Za-z]:\//.test(path) || path.startsWith("//");
}

function moduleCatalogStateMatches(
  state: ModuleCatalogFamilyState | undefined,
  projectRoot: string,
  family: string,
): state is ModuleCatalogFamilyState {
  if (!state || state.family.trim() !== family.trim()) {
    return false;
  }
  const currentRoot = normalizePath(state.projectRoot);
  const nextRoot = normalizePath(projectRoot);
  return isWindowsPath(currentRoot) || isWindowsPath(nextRoot)
    ? currentRoot.toLowerCase() === nextRoot.toLowerCase()
    : currentRoot === nextRoot;
}

function catalogModuleId(row: ProjectCatalogRow): string {
  return stringValue(hydratedModuleCatalogData(row)?.module_id) || row.name;
}

function moduleObjectId(moduleId: string): string {
  const separator = moduleId.indexOf("/");
  return separator >= 0 ? moduleId.slice(separator + 1) : moduleId;
}

function moduleCatalogTitle(
  metadata: Record<string, unknown>,
  fallback: string,
): string {
  for (const key of ["title", "label", "name", "object_id"]) {
    const value = stringValue(metadata[key]);
    if (value) {
      return value;
    }
  }
  return fallback;
}

function objectValue(value: unknown): Record<string, unknown> {
  return value && typeof value === "object" && !Array.isArray(value)
    ? (value as Record<string, unknown>)
    : {};
}

function hydratedModuleCatalogData(
  row: ProjectCatalogRow,
  expectedFamily?: string,
): Record<string, unknown> | null {
  if (!isObjectValue(row.data)) {
    return null;
  }
  const data = row.data;
  const moduleId = stringValue(data.module_id);
  const family = stringValue(data.family);
  const root = stringValue(data.root);
  const metadata = data.metadata;
  if (
    !moduleId ||
    moduleId !== row.name.trim() ||
    !family ||
    (expectedFamily && family !== expectedFamily.trim())
  ) {
    return null;
  }
  const separator = moduleId.indexOf("/");
  const objectId = separator >= 0 ? moduleId.slice(separator + 1) : "";
  if (
    separator <= 0 ||
    moduleId.slice(0, separator) !== family ||
    !objectId ||
    !moduleRootSource(root, family, objectId)
  ) {
    return null;
  }
  if (!isModuleSourceSlots(data.source_slots) || !isObjectValue(metadata)) {
    return null;
  }
  if ("source_root" in data && !stringValue(data.source_root)) {
    return null;
  }
  if ("collection_id" in data && typeof data.collection_id !== "string") {
    return null;
  }
  return data;
}

function normalizedProjectCatalogRow(
  row: ProjectCatalogRow,
): ProjectCatalogRow {
  if (row.data === undefined || hydratedModuleCatalogData(row)) {
    return row;
  }
  const { data: _invalidData, ...lightweightRow } = row;
  return lightweightRow;
}

function moduleRootSource(
  root: string,
  family: string,
  objectId: string,
): { sourceRoot: string } | null {
  const normalizedRoot = normalizePath(root).replace(/\/+$/, "");
  const boundary = "/modules/";
  const caseInsensitive = isWindowsPath(normalizedRoot);
  const comparableRoot = caseInsensitive
    ? normalizedRoot.toLowerCase()
    : normalizedRoot;
  const boundaryIndex = comparableRoot.lastIndexOf(boundary);
  if (boundaryIndex < 0) {
    return null;
  }
  const modulePath = normalizedRoot.slice(boundaryIndex + boundary.length);
  const separator = modulePath.indexOf("/");
  if (separator <= 0 || modulePath.indexOf("/", separator + 1) >= 0) {
    return null;
  }
  const rootFamily = modulePath.slice(0, separator);
  const leaf = modulePath.slice(separator + 1);
  if (
    !pathSegmentEquals(rootFamily, family, caseInsensitive) ||
    !moduleLeafMatches(leaf, objectId, caseInsensitive)
  ) {
    return null;
  }
  const sourceRoot = normalizedRoot.slice(0, boundaryIndex);
  return {
    sourceRoot: /^[A-Za-z]:$/.test(sourceRoot)
      ? `${sourceRoot}/`
      : sourceRoot || "/",
  };
}

function moduleLeafMatches(
  leaf: string,
  objectId: string,
  caseInsensitive: boolean,
): boolean {
  if (pathSegmentEquals(leaf, objectId, caseInsensitive)) {
    return true;
  }
  const labelPrefix = `${objectId} - `;
  return caseInsensitive
    ? leaf.toLowerCase().startsWith(labelPrefix.toLowerCase())
    : leaf.startsWith(labelPrefix);
}

function pathSegmentEquals(
  left: string,
  right: string,
  caseInsensitive: boolean,
): boolean {
  return caseInsensitive
    ? left.toLowerCase() === right.toLowerCase()
    : left === right;
}

function isModuleSourceSlots(
  value: unknown,
): value is Record<string, string[]> {
  if (!isObjectValue(value)) {
    return false;
  }
  return Object.entries(value).every(
    ([slot, paths]) =>
      slot.trim().length > 0 &&
      Array.isArray(paths) &&
      paths.every((path) => typeof path === "string" && path.trim().length > 0),
  );
}

function isObjectValue(value: unknown): value is Record<string, unknown> {
  return Boolean(value) && typeof value === "object" && !Array.isArray(value);
}

function stringValue(value: unknown): string {
  return typeof value === "string" ? value.trim() : "";
}
