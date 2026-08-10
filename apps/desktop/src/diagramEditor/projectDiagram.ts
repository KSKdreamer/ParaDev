import { canonicalFamilyId } from "../projectModules";
import type { ProjectBrowserItem, ProjectBrowserPayload } from "../types";
import type { DiagramDocument, DiagramEdge, DiagramEdgeKind, DiagramNode, DiagramNodeId, DiagramRelativePositionKind } from "./layoutModel";

export type ProjectDiagramOptions = {
  gridSizePx?: number;
  nodeWidth?: number;
  nodeHeight?: number;
  focusNodeWidth?: number;
  focusNodeHeight?: number;
  locale?: string;
};

export type ProjectDiagramNodePayload = {
  projectId: string;
  itemId: string;
  itemKind: ProjectBrowserItem["kind"];
  familyId: string;
  family: string;
  objectId: string;
  moduleId?: string;
  relativeRoot: string;
  sourceRoot?: string;
  sourceRootRelativePath?: string;
  embeddedId?: string;
  embeddedKind?: "focus";
  sourceFocusPath?: string;
  sourceFocusSlots?: boolean;
};

type DiagramEntryKind = "browser-item" | "focus";

type DiagramEntry = {
  id: DiagramNodeId;
  item: ProjectBrowserItem;
  kind: DiagramEntryKind;
  imageUrl?: string;
  metadata: Record<string, unknown>;
  order: number;
  title: string;
  parentCandidates: string[];
  explicitRootParent?: boolean;
  dependencySources: string[];
  dependencyTargets: string[];
  referenceTargets: string[];
  position?: GridPosition;
  positionMode?: "absolute" | "auto" | "relative";
  relativePositionKind?: DiagramRelativePositionKind;
  relativeParentCandidates: string[];
  sourceFocusPath?: string;
  sourceFocusSlots?: boolean;
  priority?: number;
  subtreeWidth?: number;
  subtreeWidthDelta?: number;
  subtreeCenterOffset?: number;
};

type SourceFocusLayoutContext = {
  entryIds: Set<string>;
  finalPositionsById: Map<string, GridPosition>;
  parentById: Map<string, string>;
  recordsById: Map<string, Record<string, unknown>>;
  subtreeWidthsById: Map<string, number>;
  usesSourceFocusSlots: boolean;
};

type GridPosition = {
  x: number;
  y: number;
};

const DEFAULT_GRID_SIZE_PX = 24;
const DEFAULT_FOCUS_GRID_SIZE_PX = 96;
const DEFAULT_TECHNOLOGY_GRID_SIZE_PX = 48;
const DEFAULT_NODE_WIDTH = 6;
const DEFAULT_NODE_HEIGHT = 2;
const DEFAULT_FOCUS_NODE_WIDTH = 1;
const DEFAULT_FOCUS_NODE_HEIGHT = 1;
const DEFAULT_TECHNOLOGY_NODE_WIDTH = 1;
const DEFAULT_TECHNOLOGY_NODE_HEIGHT = 1;

const FOCUS_COLLECTION_KEYS = ["focuses", "focus_nodes", "focusNodes", "focus_records", "focusRecords"];
const SOURCE_FOCUS_COLLECTION_KEYS = ["source_focuses", "sourceFocuses"];
const FOCUS_ID_KEYS = ["id", "focus_id", "focusId", "object_id", "objectId"];
const RELATIVE_PARENT_KEYS = ["relative_position_id", "relativePositionId"];
const SOURCE_FOCUS_LAYOUT_KEYS = ["tree", "parent", ...RELATIVE_PARENT_KEYS, "x", "y", "dx", "dy", "cx", "cy", "w", "pw", "dw", "dc", "priority"];
const SOURCE_FOCUS_POSITION_KEYS = ["parent", ...RELATIVE_PARENT_KEYS, "x", "y", "dx", "dy", "cx", "cy"];
const DIRECT_PARENT_KEYS = ["parent", "parent_id", "parentId", "source_parent", "sourceParent", ...RELATIVE_PARENT_KEYS];
const DEPENDENCY_SOURCE_KEYS = [
  "dependency_ids",
  "dependencyIds",
  "dependencies",
  "prerequisites",
  "prerequisite",
  "required_technologies",
  "requiredTechnologies"
];
const DEPENDENCY_TARGET_KEYS = ["path_target_ids", "pathTargetIds", "leads_to_tech", "leadsToTech", "unlocks", "unlock_ids", "unlockIds"];
const REFERENCE_TARGET_KEYS = ["mutually_exclusive", "mutuallyExclusive", "exclusive_with", "exclusiveWith"];
const IMAGE_URL_KEYS = ["imageUrl", "image_url", "thumbnailUrl", "thumbnail_url", "iconUrl", "icon_url", "previewUrl", "preview_url"];
const MODULE_LOCAL_IMAGE_KEYS = ["legacy_source_image", "legacySourceImage", "source_image", "sourceImage"];
const IMAGE_EXTENSIONS = new Set(["bmp", "dds", "jpg", "jpeg", "png", "tga", "webp"]);
const EDGE_KIND_ORDER: Record<DiagramEdgeKind, number> = {
  dependency: 0,
  path: 1,
  tree: 2,
  reference: 3
};

export function buildProjectDiagramDocument(
  browser: ProjectBrowserPayload,
  familyId: string,
  options: ProjectDiagramOptions = {}
): DiagramDocument {
  const targetFamilyId = canonicalFamilyId(familyId);
  const diagramOptions = projectDiagramOptionsForFamily(targetFamilyId, options);
  const entries = dedupeEntries(
    browser.items
      .filter((item) => canonicalFamilyId(item.family_id, item.family) === targetFamilyId)
      .sort((left, right) => compareItems(left, right, diagramOptions.locale))
      .flatMap((item, itemIndex) => entriesForItem(browser, item, itemIndex, diagramOptions))
  );
  const entryIds = new Set(entries.map((entry) => entry.id));
  const parentById = chooseParents(entries, entryIds);
  const nodes = entries.map<DiagramNode>((entry, index) => {
    const parentId = parentById.get(entry.id);
    const size = sizeForEntry(entry, diagramOptions);
    const relativePosition = Boolean(entry.position && parentId && entry.positionMode === "relative" && entry.relativeParentCandidates.includes(parentId));
    const autoPosition = Boolean(entry.position && entry.positionMode === "auto");
    return {
      id: entry.id,
      ...(parentId ? { parentId } : {}),
      order: index,
      mode: entry.position ? (relativePosition ? "relative" : autoPosition ? "auto" : "absolute") : "auto",
      ...(entry.position
        ? relativePosition || autoPosition
          ? { dx: entry.position.x, dy: entry.position.y }
          : { fixed: true, x: entry.position.x, y: entry.position.y }
        : {}),
      ...((relativePosition || autoPosition) && entry.relativePositionKind ? { relativePositionKind: entry.relativePositionKind } : {}),
      width: size.width,
      height: size.height,
      ...optionalNumberField("priority", entry.priority),
      ...optionalNumberField("subtreeWidth", entry.subtreeWidth),
      ...optionalNumberField("subtreeWidthDelta", entry.subtreeWidthDelta),
      ...optionalNumberField("subtreeCenterOffset", entry.subtreeCenterOffset),
      ...(entry.imageUrl ? { imageUrl: entry.imageUrl } : {}),
      title: entry.title,
      payload: payloadForEntry(browser, entry)
    };
  });

  return {
    schemaVersion: 1,
    gridSizePx: diagramOptions.gridSizePx ?? DEFAULT_GRID_SIZE_PX,
    ...(targetFamilyId === "focuses" ? { layoutOptions: { layerGap: 0, ...(entries.some((entry) => entry.kind === "focus" && entry.sourceFocusSlots) ? { sourceFocusSlots: true } : {}) } } : {}),
    nodes,
    edges: buildEdges(entries, entryIds, parentById)
  };
}

function projectDiagramOptionsForFamily(familyId: string, options: ProjectDiagramOptions): ProjectDiagramOptions {
  if (familyId === "focuses") {
    return {
      ...options,
      gridSizePx: options.gridSizePx ?? DEFAULT_FOCUS_GRID_SIZE_PX,
      focusNodeWidth: options.focusNodeWidth ?? DEFAULT_FOCUS_NODE_WIDTH,
      focusNodeHeight: options.focusNodeHeight ?? DEFAULT_FOCUS_NODE_HEIGHT
    };
  }
  if (familyId === "technologies") {
    return {
      ...options,
      gridSizePx: options.gridSizePx ?? DEFAULT_TECHNOLOGY_GRID_SIZE_PX,
      nodeWidth: options.nodeWidth ?? DEFAULT_TECHNOLOGY_NODE_WIDTH,
      nodeHeight: options.nodeHeight ?? DEFAULT_TECHNOLOGY_NODE_HEIGHT
    };
  }
  return options;
}

function entriesForItem(
  browser: ProjectBrowserPayload,
  item: ProjectBrowserItem,
  itemIndex: number,
  options: ProjectDiagramOptions
): DiagramEntry[] {
  const metadata = metadataRecord(item);
  const settings = settingsRecord(item);
  const focusRecords = focusRecordList(metadata, settings);
  if (focusRecords.length > 0) {
    const focusIds = new Set(focusRecords.map((focus) => stringForKeys(focus, FOCUS_ID_KEYS)).filter((id): id is string => Boolean(id)));
    const sourceLayoutContext = sourceFocusLayoutContextForItem(item, focusIds);
    return focusRecords
      .map((focus, focusIndex) => entryForFocus(item, focus, itemIndex * 100000 + focusIndex, options, sourceLayoutContext))
      .filter((entry): entry is DiagramEntry => Boolean(entry));
  }

  return [entryForBrowserItem(browser, item, itemIndex, options)];
}

function entryForBrowserItem(
  browser: ProjectBrowserPayload,
  item: ProjectBrowserItem,
  order: number,
  options: ProjectDiagramOptions
): DiagramEntry {
  const metadata = metadataRecord(item);
  const settings = settingsRecord(item);
  const imageUrl = imageUrlForItemRecord(item, settings) || imageUrlForItemRecord(item, metadata) || imageUrlForItemSources(item);
  return {
    id: item.object_id || item.id,
    item,
    kind: "browser-item",
    ...(imageUrl ? { imageUrl } : {}),
    metadata: settings,
    order,
    title: itemTitle(item, options.locale) || titleFromIdentifier(item.object_id || item.id),
    parentCandidates: identifiersForKeys(settings, DIRECT_PARENT_KEYS),
    dependencySources: dependencySourcesFor(settings),
    dependencyTargets: dependencyTargetsFor(settings),
    referenceTargets: referenceTargetsFor(settings),
    position: positionFor(settings, options.gridSizePx ?? DEFAULT_GRID_SIZE_PX),
    relativeParentCandidates: [],
    ...legacyLayoutHintsFor(settings)
  };
}

function entryForFocus(
  item: ProjectBrowserItem,
  focus: Record<string, unknown>,
  order: number,
  options: ProjectDiagramOptions,
  sourceLayoutContext: SourceFocusLayoutContext
): DiagramEntry | null {
  const id = stringForKeys(focus, FOCUS_ID_KEYS);
  if (!id) {
    return null;
  }
  const sourceFocus = sourceFocusRecordForFocus(item, id);
  const sourceLayout = sourceFocus ? sourceFocusLayoutFields(sourceFocus) : {};
  const layoutFocus = Object.keys(sourceLayout).length > 0 ? focusWithSourceLayout(focus, sourceLayout) : focus;
  const sourceSubtreeWidth = sourceFocusNumberForId(sourceLayoutContext.subtreeWidthsById, id);
  const dependencySourceFocus = relationshipRecordForFocus(focus, sourceFocus, DEPENDENCY_SOURCE_KEYS);
  const dependencyTargetFocus = relationshipRecordForFocus(focus, sourceFocus, DEPENDENCY_TARGET_KEYS);
  const referenceTargetFocus = relationshipRecordForFocus(focus, sourceFocus, REFERENCE_TARGET_KEYS);
  const imageUrl = focusImageUrlFor(item, focus, id, sourceFocus);
  const sourceFocusPath = sourceFocus ? sourceFocusSourcePath(sourceFocus) : undefined;
  const explicitPosition = sourceFocusExplicitDisplayPosition(sourceFocus, sourceSubtreeWidth, sourceLayoutContext.usesSourceFocusSlots) ?? positionFor(layoutFocus, options.gridSizePx ?? DEFAULT_GRID_SIZE_PX);
  const legacyOffset = explicitPosition ? undefined : legacyOffsetFor(layoutFocus);
  const legacyHints = legacyLayoutHintsWithInferredWidth(layoutFocus, sourceSubtreeWidth);
  const relativePositionParents = identifiersForKeys(layoutFocus, RELATIVE_PARENT_KEYS);
  const relativeParentCandidates = uniqueIds(relativePositionParents);
  const relativePositionKind = relativePositionParents.length > 0 ? "relative_position_id" : legacyOffset ? "legacy_offset" : undefined;
  const explicitRootParent = explicitRootParentFor(layoutFocus);
  const position = explicitPosition ?? legacyOffset;
  return {
    id,
    item,
    kind: "focus",
    ...(imageUrl ? { imageUrl } : {}),
    metadata: focus,
    order,
    title: focusTitle(focus, id, options.locale),
    ...(sourceFocusPath ? { sourceFocusPath } : {}),
    ...(sourceLayoutContext.usesSourceFocusSlots ? { sourceFocusSlots: true } : {}),
    parentCandidates: identifiersForKeys(layoutFocus, DIRECT_PARENT_KEYS),
    ...(explicitRootParent ? { explicitRootParent } : {}),
    dependencySources: dependencySourcesFor(dependencySourceFocus),
    dependencyTargets: dependencyTargetsFor(dependencyTargetFocus),
    referenceTargets: referenceTargetsFor(referenceTargetFocus),
    position,
    positionMode: explicitPosition ? (relativeParentCandidates.length > 0 ? "relative" : "absolute") : legacyOffset ? "auto" : undefined,
    ...(relativePositionKind ? { relativePositionKind } : {}),
    relativeParentCandidates,
    ...legacyHints
  };
}

function dedupeEntries(entries: DiagramEntry[]): DiagramEntry[] {
  const byId = new Map<DiagramNodeId, DiagramEntry>();
  for (const entry of entries) {
    if (!byId.has(entry.id)) {
      byId.set(entry.id, entry);
    }
  }
  return [...byId.values()].sort((left, right) => left.order - right.order || left.id.localeCompare(right.id));
}

function chooseParents(entries: DiagramEntry[], entryIds: Set<DiagramNodeId>): Map<DiagramNodeId, DiagramNodeId> {
  const parentById = new Map<DiagramNodeId, DiagramNodeId>();
  for (const entry of entries) {
    const candidates = entry.kind === "focus" && !entry.explicitRootParent ? [...entry.parentCandidates, ...entry.dependencySources] : entry.parentCandidates;
    const parentId = candidates.find((candidate) => candidate !== entry.id && entryIds.has(candidate));
    if (!parentId || createsParentCycle(entry.id, parentId, parentById)) {
      continue;
    }
    parentById.set(entry.id, parentId);
  }
  return parentById;
}

function createsParentCycle(childId: DiagramNodeId, parentId: DiagramNodeId, parentById: Map<DiagramNodeId, DiagramNodeId>): boolean {
  let current: DiagramNodeId | undefined = parentId;
  while (current) {
    if (current === childId) {
      return true;
    }
    current = parentById.get(current);
  }
  return false;
}

function buildEdges(
  entries: DiagramEntry[],
  entryIds: Set<DiagramNodeId>,
  parentById: Map<DiagramNodeId, DiagramNodeId>
): DiagramEdge[] {
  const edgesById = new Map<string, DiagramEdge>();
  for (const entry of entries) {
    for (const source of entry.dependencySources) {
      addEdge(edgesById, entryIds, source, entry.id, "dependency");
    }
    for (const target of entry.dependencyTargets) {
      addEdge(edgesById, entryIds, entry.id, target, "dependency");
    }
    for (const target of entry.referenceTargets) {
      addEdge(edgesById, entryIds, entry.id, target, "reference");
    }
    const parentId = parentById.get(entry.id);
    if (parentId) {
      addEdge(edgesById, entryIds, parentId, entry.id, "tree");
    }
  }
  return [...edgesById.values()].sort(compareEdges);
}

function addEdge(
  edgesById: Map<string, DiagramEdge>,
  entryIds: Set<DiagramNodeId>,
  source: DiagramNodeId,
  target: DiagramNodeId,
  kind: DiagramEdgeKind
): void {
  if (source === target || !entryIds.has(source) || !entryIds.has(target)) {
    return;
  }
  const id = `${kind}:${source}->${target}`;
  edgesById.set(id, { id, source, target, kind });
}

function compareEdges(left: DiagramEdge, right: DiagramEdge): number {
  return (
    left.source.localeCompare(right.source) ||
    left.target.localeCompare(right.target) ||
    EDGE_KIND_ORDER[left.kind] - EDGE_KIND_ORDER[right.kind] ||
    left.id.localeCompare(right.id)
  );
}

function metadataRecord(item: ProjectBrowserItem): Record<string, unknown> {
  return asRecord(item.metadata) ?? {};
}

function settingsRecord(item: ProjectBrowserItem): Record<string, unknown> {
  return asRecord(metadataRecord(item).settings) ?? metadataRecord(item);
}

function focusRecordList(metadata: Record<string, unknown>, settings: Record<string, unknown>): Record<string, unknown>[] {
  for (const source of [settings, metadata]) {
    for (const key of FOCUS_COLLECTION_KEYS) {
      const records = recordList(source[key]);
      if (records.length > 0) {
        return records;
      }
    }
  }
  return [];
}

function sourceFocusLayoutContextForItem(item: ProjectBrowserItem, entryIds: Set<string>): SourceFocusLayoutContext {
  const records = sourceFocusRecordsForItem(item);
  const layoutRecords = records.filter(sourceFocusControlsPosition);
  const context: SourceFocusLayoutContext = {
    entryIds,
    finalPositionsById: new Map(),
    parentById: new Map(),
    recordsById: new Map(),
    subtreeWidthsById: new Map(),
    usesSourceFocusSlots: layoutRecords.some(sourceFocusIsExplicitRoot)
  };
  if (layoutRecords.length === 0) {
    return context;
  }

  for (const record of layoutRecords) {
    const id = sourceFocusId(record);
    if (!id) {
      continue;
    }
    setSourceFocusMapValue(context.recordsById, id, record);
  }

  const childrenByParent = new Map<string, Record<string, unknown>[]>();
  for (const record of layoutRecords) {
    const id = sourceFocusId(record);
    const parentId = sourceFocusParentId(record);
    if (!id || !parentId || !sourceFocusRecordForId(context.recordsById, parentId)) {
      continue;
    }
    setSourceFocusMapValue(context.parentById, id, parentId);
    const siblings = childrenByParent.get(parentId) ?? [];
    siblings.push(record);
    childrenByParent.set(parentId, siblings);
  }
  for (const [parentId, children] of childrenByParent) {
    childrenByParent.set(parentId, sortSourceFocusRecords(children));
  }

  const visitingWidth = new Set<string>();
  const subtreeWidthFor = (record: Record<string, unknown>): number => {
    const id = sourceFocusId(record);
    if (!id) {
      return 2;
    }
    const cached = context.subtreeWidthsById.get(id);
    if (cached !== undefined) {
      return cached;
    }
    if (visitingWidth.has(id)) {
      return 2;
    }
    visitingWidth.add(id);
    const explicitWidth = positiveNumberValue(record.w ?? record.pw ?? record.subtree_width ?? record.subtreeWidth);
    const childWidth = (childrenByParent.get(id) ?? []).reduce((sum, child) => sum + subtreeWidthFor(child), 0);
    const width = explicitWidth ?? Math.max(2, childWidth + (numberValue(record.dw ?? record.subtree_width_delta ?? record.subtreeWidthDelta) ?? 0));
    visitingWidth.delete(id);
    setSourceFocusMapValue(context.subtreeWidthsById, id, width);
    return width;
  };

  for (const record of layoutRecords) {
    subtreeWidthFor(record);
  }

  const visitingPosition = new Set<string>();
  const positionRecord = (record: Record<string, unknown>, autoX = 0, autoY = 0): void => {
    const id = sourceFocusId(record);
    if (!id || visitingPosition.has(id) || context.finalPositionsById.has(id)) {
      return;
    }
    visitingPosition.add(id);
    const sourcePoint = sourceFocusLeftPosition(record, autoX, autoY);
    const width = subtreeWidthFor(record);
    setSourceFocusMapValue(context.finalPositionsById, id, {
      x: sourcePoint.x + Math.floor(width / 2),
      y: sourcePoint.y
    });

    let childX = sourcePoint.x - Math.floor((numberValue(record.dw ?? record.subtree_width_delta ?? record.subtreeWidthDelta) ?? 0) / 2) + (numberValue(record.dc ?? record.subtree_center_offset ?? record.subtreeCenterOffset) ?? 0);
    const childY = sourcePoint.y + 1;
    for (const child of childrenByParent.get(id) ?? []) {
      positionRecord(child, childX, childY);
      childX += subtreeWidthFor(child);
    }
    visitingPosition.delete(id);
  };

  for (const record of sortSourceFocusRecords(layoutRecords.filter((record) => !sourceFocusParentId(record)))) {
    positionRecord(record);
  }

  return context;
}

function sourceFocusControlsPosition(record: Record<string, unknown>): boolean {
  return SOURCE_FOCUS_POSITION_KEYS.some((key) => hasOwn(record, key));
}

function sourceFocusIsExplicitRoot(record: Record<string, unknown>): boolean {
  return !sourceFocusParentId(record) && numberValue(record.x) !== undefined && numberValue(record.y) !== undefined;
}

function sourceFocusRecordsForItem(item: ProjectBrowserItem): Record<string, unknown>[] {
  const metadata = metadataRecord(item);
  const settings = settingsRecord(item);
  for (const source of [settings, metadata]) {
    for (const key of SOURCE_FOCUS_COLLECTION_KEYS) {
      const records = recordList(source[key]);
      if (records.length > 0) {
        return records;
      }
    }
  }
  return [];
}

function sourceFocusLeftPosition(record: Record<string, unknown>, autoX: number, autoY: number): GridPosition {
  const x = numberValue(record.x);
  const y = numberValue(record.y);
  if (x !== undefined && y !== undefined) {
    return { x, y };
  }
  return {
    x: autoX + (numberValue(record.dx ?? record.cx) ?? 0),
    y: autoY + (numberValue(record.dy ?? record.cy) ?? 0)
  };
}

function sourceFocusNumberForId(numbersById: Map<string, number>, id: string): number | undefined {
  return numbersById.get(id) ?? numbersById.get(normalizedFocusIdentifier(id));
}

function sourceFocusRecordForId(recordsById: Map<string, Record<string, unknown>>, id: string): Record<string, unknown> | undefined {
  return recordsById.get(id) ?? recordsById.get(normalizedFocusIdentifier(id));
}

function sourceFocusExplicitDisplayPosition(sourceFocus: Record<string, unknown> | undefined, subtreeWidth: number | undefined, sourceFocusSlots: boolean): GridPosition | undefined {
  if (!sourceFocus) {
    return undefined;
  }
  const x = numberValue(sourceFocus.x);
  const y = numberValue(sourceFocus.y);
  if (x === undefined || y === undefined) {
    return undefined;
  }
  const relativePositionParents = identifiersForKeys(sourceFocus, RELATIVE_PARENT_KEYS);
  return {
    x: sourceFocusSlots && relativePositionParents.length === 0 ? x + Math.floor((subtreeWidth ?? 2) / 2) : x,
    y
  };
}

function setSourceFocusMapValue<T>(map: Map<string, T>, id: string, value: T): void {
  map.set(id, value);
  map.set(normalizedFocusIdentifier(id), value);
}

function sourceFocusId(record: Record<string, unknown>): string | undefined {
  return stringForKeys(record, FOCUS_ID_KEYS);
}

function sourceFocusParentId(record: Record<string, unknown>): string | undefined {
  return stringForKeys(record, ["parent", ...RELATIVE_PARENT_KEYS]);
}

function sortSourceFocusRecords(records: Record<string, unknown>[]): Record<string, unknown>[] {
  return [...records].sort((left, right) => (numberValue(right.priority) ?? 0) - (numberValue(left.priority) ?? 0) || (sourceFocusId(left) ?? "").localeCompare(sourceFocusId(right) ?? ""));
}

function dependencySourcesFor(record: Record<string, unknown>): string[] {
  const ids = hasOwn(record, "prerequisites") ? identifiersForKeys(record, ["prerequisites"]) : identifiersForKeys(record, DEPENDENCY_SOURCE_KEYS);
  const nestedPath = asRecord(record.path);
  return uniqueIds([...ids, ...identifiersForKeys(nestedPath ?? {}, DEPENDENCY_SOURCE_KEYS)]);
}

function dependencyTargetsFor(record: Record<string, unknown>): string[] {
  const nestedPath = asRecord(record.path);
  return uniqueIds([
    ...identifiersForKeys(record, DEPENDENCY_TARGET_KEYS),
    ...identifiersForKeys(nestedPath ?? {}, DEPENDENCY_TARGET_KEYS)
  ]);
}

function referenceTargetsFor(record: Record<string, unknown>): string[] {
  const ids = identifiersForKeys(record, ["mutually_exclusive"]);
  const aliasIds = hasOwn(record, "mutually_exclusive") ? [] : identifiersForKeys(record, REFERENCE_TARGET_KEYS.filter((key) => key !== "mutually_exclusive"));
  return uniqueIds([...ids, ...aliasIds]);
}

function imageUrlForRecord(record: Record<string, unknown>): string | undefined {
  for (const key of IMAGE_URL_KEYS) {
    const imageUrl = imageReferenceFromValue(record[key]);
    if (imageUrl) {
      return imageUrl;
    }
  }
  return undefined;
}

function imageUrlForItemRecord(item: ProjectBrowserItem, record: Record<string, unknown>): string | undefined {
  const direct = imageUrlForRecord(record);
  if (direct) {
    return moduleLocalImageUrlForItem(item, direct);
  }
  for (const key of MODULE_LOCAL_IMAGE_KEYS) {
    const imageUrl = imageReferenceFromValue(record[key]);
    if (imageUrl) {
      return moduleLocalImageUrlForItem(item, imageUrl);
    }
  }
  return undefined;
}

function moduleLocalImageUrlForItem(item: ProjectBrowserItem, imageUrl: string): string {
  if (isSchemeUrl(imageUrl) || imageUrl.startsWith("/") || imageUrl.startsWith("src/")) {
    return imageUrl;
  }
  const relativeRoot = cleanDisplayText(item.relative_root);
  const relativeImageUrl = imageUrl.replace(/^[\\/]+/, "");
  return relativeRoot && relativeImageUrl ? `${relativeRoot.replace(/[\\/]+$/, "")}/${relativeImageUrl}` : imageUrl;
}

function imageReferenceFromValue(value: unknown): string | undefined {
  const direct = imageReferenceFromText(value);
  if (direct) {
    return direct;
  }
  const record = asRecord(value);
  if (!record) {
    return undefined;
  }
  return imageReferenceFromText(stringForKeys(record, ["url", "path", "relative_path", "relativePath", "src", "href"]));
}

function imageUrlForItemSources(item: ProjectBrowserItem): string | undefined {
  for (const source of item.sources) {
    const slot = source.slot.toLowerCase();
    const extension = normalizedExtension(source.extension || source.name);
    const isImageSlot = slot === "icon" || slot === "image" || slot.includes("gfx");
    if (!isImageSlot && !IMAGE_EXTENSIONS.has(extension)) {
      continue;
    }
    const sourcePath = cleanDisplayText(source.path) || cleanDisplayText(source.relative_path);
    if (sourcePath) {
      return processedImagePath(sourcePath);
    }
  }
  return undefined;
}

function focusImageUrlFor(
  item: ProjectBrowserItem,
  focus: Record<string, unknown>,
  id: string,
  sourceFocus = sourceFocusRecordForFocus(item, id)
): string | undefined {
  const direct = imageUrlForRecord(focus);
  if (direct) {
    return direct;
  }
  return focusTreeImageUrlFor(item, focus, sourceFocus, id);
}

function sourceFocusRecordForFocus(item: ProjectBrowserItem, id: string): Record<string, unknown> | undefined {
  const metadata = metadataRecord(item);
  const settings = settingsRecord(item);
  const normalizedId = normalizedFocusIdentifier(id);
  for (const source of [settings, metadata]) {
    for (const key of SOURCE_FOCUS_COLLECTION_KEYS) {
      const records = recordList(source[key]);
      const record =
        records.find((candidate) => stringForKeys(candidate, FOCUS_ID_KEYS) === id) ??
        records.find((candidate) => normalizedFocusIdentifier(stringForKeys(candidate, FOCUS_ID_KEYS)) === normalizedId);
      if (record) {
        return record;
      }
    }
  }
  return undefined;
}

function sourceFocusLayoutFields(sourceFocus: Record<string, unknown>): Record<string, unknown> {
  const out: Record<string, unknown> = {};
  for (const key of SOURCE_FOCUS_LAYOUT_KEYS) {
    if (hasOwn(sourceFocus, key)) {
      out[key] = sourceFocus[key];
    }
  }
  return out;
}

function sourceFocusSourcePath(sourceFocus: Record<string, unknown>): string | undefined {
  return stringForKeys(sourceFocus, ["source_path", "sourcePath", "folder"]);
}

function focusWithSourceLayout(focus: Record<string, unknown>, sourceLayout: Record<string, unknown>): Record<string, unknown> {
  const merged = { ...focus, ...sourceLayout };
  if (sourceLayoutControlsPosition(sourceLayout) && !(hasOwn(sourceLayout, "x") && hasOwn(sourceLayout, "y"))) {
    delete merged.x;
    delete merged.y;
  }
  return merged;
}

function sourceLayoutControlsPosition(sourceLayout: Record<string, unknown>): boolean {
  return SOURCE_FOCUS_POSITION_KEYS.some((key) => hasOwn(sourceLayout, key));
}

function explicitRootParentFor(record: Record<string, unknown>): boolean {
  return DIRECT_PARENT_KEYS.some((key) => hasOwn(record, key) && record[key] === null);
}

function relationshipRecordForFocus(focus: Record<string, unknown>, sourceFocus: Record<string, unknown> | undefined, keys: string[]): Record<string, unknown> {
  return sourceFocus && keys.some((key) => hasOwn(sourceFocus, key)) ? sourceFocus : focus;
}

function hasOwn(record: Record<string, unknown>, key: string): boolean {
  return Object.prototype.hasOwnProperty.call(record, key);
}

function focusTreeImageUrlFor(
  item: ProjectBrowserItem,
  focus: Record<string, unknown>,
  sourceFocus: Record<string, unknown> | undefined,
  fallbackId: string
): string | undefined {
  const icon = stringForKeys(focus, ["icon", "icon_id", "iconId"]);
  const sourceIcon = sourceFocus ? stringForKeys(sourceFocus, ["icon", "icon_id", "iconId", "icon_path", "iconPath"]) : undefined;
  if (!icon && !sourceIcon) {
    return undefined;
  }
  const sourceFocusId = sourceFocus ? stringForKeys(sourceFocus, ["id", "focus_id", "focusId", "object_id", "objectId"]) : undefined;
  const focusId =
    (sourceFocusId?.startsWith("FOCUS_") ? sourceFocusId : undefined) ??
    focusIdFromIconKey(icon) ??
    (fallbackId.startsWith("FOCUS_") ? normalizedFocusIdentifier(fallbackId) : undefined);
  if (!focusId) {
    return undefined;
  }
  const treeId = cleanDisplayText(item.object_id);
  if (!treeId) {
    return undefined;
  }
  return `src/modules/focus_tree/${treeId}/icons/${focusId}.png`;
}

function focusIdFromIconKey(value: string | undefined): string | undefined {
  if (!value) {
    return undefined;
  }
  const clean = value.replace(/^GFX_/i, "").replace(/_icon$/i, "");
  return clean.startsWith("FOCUS_") ? clean : undefined;
}

function normalizedFocusIdentifier(value: string | undefined): string {
  return (value ?? "").replace(/[^A-Za-z0-9_]/g, "_");
}

function imageReferenceFromText(value: unknown): string | undefined {
  if (typeof value !== "string") {
    return undefined;
  }
  const clean = value.trim();
  if (!clean) {
    return undefined;
  }
  if (isSchemeUrl(clean)) {
    return clean;
  }
  const extension = normalizedExtension(clean);
  return IMAGE_EXTENSIONS.has(extension) ? processedImagePath(clean) : undefined;
}

function isSchemeUrl(value: string): boolean {
  return /^[a-z][a-z0-9+.-]*:/i.test(value);
}

function processedImagePath(path: string): string {
  return path.replace(/\.[^/.\\]+$/, ".png");
}

function normalizedExtension(value: string): string {
  return value.trim().toLowerCase().replace(/[?#].*$/, "").replace(/^.*[./\\]/, "");
}

function positionFor(record: Record<string, unknown>, gridSizePx: number): GridPosition | undefined {
  const candidates = [
    record,
    asRecord(record.position),
    asRecord(record.folder_position),
    asRecord(asRecord(record.folder)?.position),
    asRecord(record.tree_info_continuous_focus_position),
    asRecord(record.continuous_focus_position)
  ];
  for (const candidate of candidates) {
    if (!candidate) {
      continue;
    }
    const x = numberValue(candidate.x);
    const y = numberValue(candidate.y);
    if (x !== undefined && y !== undefined) {
      return { x, y };
    }
  }
  return technologyRootGuiPositionFor(record, gridSizePx);
}

function legacyOffsetFor(record: Record<string, unknown>): GridPosition | undefined {
  const x = numberValue(record.dx ?? record.cx);
  const y = numberValue(record.dy ?? record.cy);
  return x !== undefined || y !== undefined ? { x: x ?? 0, y: y ?? 0 } : undefined;
}

function legacyLayoutHintsFor(record: Record<string, unknown>): Pick<DiagramEntry, "priority" | "subtreeWidth" | "subtreeWidthDelta" | "subtreeCenterOffset"> {
  return {
    ...optionalNumberField("priority", numberValue(record.priority)),
    ...optionalPositiveNumberField("subtreeWidth", numberValue(record.w ?? record.pw ?? record.subtree_width ?? record.subtreeWidth)),
    ...optionalNumberField("subtreeWidthDelta", numberValue(record.dw ?? record.subtree_width_delta ?? record.subtreeWidthDelta)),
    ...optionalNumberField("subtreeCenterOffset", numberValue(record.dc ?? record.subtree_center_offset ?? record.subtreeCenterOffset))
  };
}

function legacyLayoutHintsWithInferredWidth(
  record: Record<string, unknown>,
  inferredWidth: number | undefined
): Pick<DiagramEntry, "priority" | "subtreeWidth" | "subtreeWidthDelta" | "subtreeCenterOffset"> {
  const hints = legacyLayoutHintsFor(record);
  return hints.subtreeWidth === undefined && inferredWidth !== undefined ? { ...hints, subtreeWidth: inferredWidth } : hints;
}

function technologyRootGuiPositionFor(record: Record<string, unknown>, gridSizePx: number): GridPosition | undefined {
  const rootGui = asRecord(record.legacy_root_gui);
  if (!rootGui || !rootGui.is_root || !Number.isFinite(gridSizePx) || gridSizePx <= 0) {
    return undefined;
  }
  const rootX = numberValue(rootGui.root_x ?? rootGui.rootX);
  const rootY = numberValue(rootGui.root_y ?? rootGui.rootY);
  if (rootX === undefined || rootY === undefined) {
    return undefined;
  }
  return {
    x: Math.round(rootX / gridSizePx),
    y: Math.round(rootY / gridSizePx)
  };
}

function identifiersForKeys(record: Record<string, unknown>, keys: string[]): string[] {
  return uniqueIds(keys.flatMap((key) => identifiersFromValue(record[key])));
}

function identifiersFromValue(value: unknown): string[] {
  if (typeof value === "string") {
    const identifier = cleanIdentifier(value);
    return identifier ? [identifier] : [];
  }
  if (Array.isArray(value)) {
    return value.flatMap(identifiersFromValue);
  }
  const record = asRecord(value);
  if (!record) {
    return [];
  }
  const direct = stringForKeys(record, ["id", "target", "focus", "technology", "tech", "object_id", "objectId"]);
  if (direct) {
    return [direct];
  }
  return Object.keys(record).map(cleanIdentifier).filter((identifier): identifier is string => Boolean(identifier));
}

function stringForKeys(record: Record<string, unknown>, keys: string[]): string | undefined {
  for (const key of keys) {
    const value = cleanIdentifier(record[key]);
    if (value) {
      return value;
    }
  }
  return undefined;
}

function cleanIdentifier(value: unknown): string | undefined {
  if (typeof value !== "string") {
    return undefined;
  }
  const clean = value.trim();
  return clean || undefined;
}

function numberValue(value: unknown): number | undefined {
  if (typeof value === "number" && Number.isFinite(value)) {
    return value;
  }
  if (typeof value !== "string") {
    return undefined;
  }
  const parsed = Number(value.trim());
  return Number.isFinite(parsed) ? parsed : undefined;
}

function positiveNumberValue(value: unknown): number | undefined {
  const parsed = numberValue(value);
  return parsed !== undefined && parsed > 0 ? parsed : undefined;
}

function recordList(value: unknown): Record<string, unknown>[] {
  if (!Array.isArray(value)) {
    return [];
  }
  return value.map(asRecord).filter((record): record is Record<string, unknown> => Boolean(record));
}

function asRecord(value: unknown): Record<string, unknown> | null {
  if (!value || typeof value !== "object" || Array.isArray(value)) {
    return null;
  }
  return value as Record<string, unknown>;
}

function uniqueIds(ids: string[]): string[] {
  return Array.from(new Set(ids.map((id) => id.trim()).filter(Boolean)));
}

function optionalNumberField<T extends string>(key: T, value: number | undefined): { [K in T]?: number } {
  return value !== undefined && Number.isFinite(value) ? ({ [key]: value } as { [K in T]?: number }) : {};
}

function optionalPositiveNumberField<T extends string>(key: T, value: number | undefined): { [K in T]?: number } {
  return value !== undefined && Number.isFinite(value) && value > 0 ? ({ [key]: value } as { [K in T]?: number }) : {};
}

function sizeForEntry(entry: DiagramEntry, options: ProjectDiagramOptions): { width: number; height: number } {
  if (entry.kind === "focus") {
    return {
      width: options.focusNodeWidth ?? DEFAULT_FOCUS_NODE_WIDTH,
      height: options.focusNodeHeight ?? DEFAULT_FOCUS_NODE_HEIGHT
    };
  }
  return {
    width: options.nodeWidth ?? DEFAULT_NODE_WIDTH,
    height: options.nodeHeight ?? DEFAULT_NODE_HEIGHT
  };
}

function payloadForEntry(browser: ProjectBrowserPayload, entry: DiagramEntry): ProjectDiagramNodePayload {
  return {
    projectId: browser.project_id,
    itemId: entry.item.id,
    itemKind: entry.item.kind,
    familyId: canonicalFamilyId(entry.item.family_id, entry.item.family),
    family: entry.item.family,
    objectId: entry.item.object_id,
    moduleId: entry.item.module_id,
    relativeRoot: entry.item.relative_root,
    sourceRoot: entry.item.source_root,
    sourceRootRelativePath: entry.item.source_root_relative_path,
    ...(entry.kind === "focus" ? { embeddedId: entry.id, embeddedKind: "focus" as const } : {}),
    ...(entry.sourceFocusPath ? { sourceFocusPath: entry.sourceFocusPath } : {}),
    ...(entry.sourceFocusSlots ? { sourceFocusSlots: true } : {})
  };
}

function compareItems(left: ProjectBrowserItem, right: ProjectBrowserItem, locale = "en"): number {
  return (
    (itemTitle(left, locale) || left.object_id).localeCompare(itemTitle(right, locale) || right.object_id, undefined, { sensitivity: "base" }) ||
    left.object_id.localeCompare(right.object_id) ||
    left.id.localeCompare(right.id)
  );
}

function itemTitle(item: ProjectBrowserItem, locale = "en"): string {
  const localized = localizedTitle(item.localized_titles, locale);
  return localized || cleanDisplayText(item.title) || item.object_id;
}

function focusTitle(focus: Record<string, unknown>, id: string, locale = "en"): string {
  const localized = localizedTitle(asRecord(focus.localized_titles) ?? asRecord(focus.localization), locale);
  const title = stringForKeys(focus, ["title", "name", "display_name", "displayName"]);
  const locKey = identifiersFromValue(focus.loc_keys)[0];
  return cleanDisplayText(localized) || cleanDisplayText(title) || titleFromIdentifier(locKey || id);
}

function localizedTitle(titles: Record<string, unknown> | undefined | null, locale: string): string {
  if (!titles) {
    return "";
  }
  const language = locale.startsWith("zh") ? "l_simp_chinese" : locale.startsWith("en") ? "l_english" : locale;
  return cleanDisplayText(titles[language]) || cleanDisplayText(titles.l_english);
}

function cleanDisplayText(value: unknown): string {
  return typeof value === "string" ? value.trim() : "";
}

function titleFromIdentifier(identifier: string): string {
  return identifier.replace(/_desc$/i, "").replace(/[-_]+/g, " ").replace(/\s+/g, " ").trim() || identifier;
}
