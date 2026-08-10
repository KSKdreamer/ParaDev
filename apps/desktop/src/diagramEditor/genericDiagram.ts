import type { Locale } from "../i18n";
import type {
  GenericModuleDiagramEdgeIntent,
  GenericModuleDiagramPositionIntent,
  ModuleDiagramEdge,
  ModuleDiagramPayload,
} from "../services/paradev";
import type { ProjectBrowserItem, ProjectBrowserPayload } from "../types";
import type {
  DiagramDocument,
  DiagramEdge,
  DiagramEdgeKind,
  DiagramNode,
} from "./layoutModel";

export const GENERIC_DIAGRAM_GRID_SIZE_PX = 48;

type GenericDiagramNodePayload = {
  editable: boolean;
  family: string;
  familyId: string;
  itemId: string;
  itemKind: ProjectBrowserItem["kind"];
  moduleId: string;
  objectId: string;
  projectId: string;
  relativeRoot: string;
  sourcePath: string;
  sourceRevision: string;
  sourceRoot?: string;
};

type GenericDiagramEdgePayload = {
  sourceRevision: string;
};

export type GenericDiagramEditIntents = {
  edgeIntents: GenericModuleDiagramEdgeIntent[];
  positionIntents: GenericModuleDiagramPositionIntent[];
};

/**
 * Projects the transport-neutral graph vocabulary used by external Registry
 * providers into ParaDev's shared diagram document. Providers retain source
 * parsing and edit semantics; the desktop only renders reviewed graph facts.
 */
export function buildGenericDiagramDocument(
  payload: ModuleDiagramPayload,
  browser: ProjectBrowserPayload,
  locale: Locale,
): DiagramDocument {
  const rows = payload.nodes
    .map((row) => ({ ...row, id: exactIdentifier(row.id, "node id") }))
    .sort((left, right) => left.id.localeCompare(right.id));
  rejectDuplicates(
    rows.map((row) => row.id),
    "node id",
  );
  const nodeIds = new Set(rows.map((row) => row.id));
  const browserItems = browser.items.filter((item) => item.kind === "module");
  const nodes = rows.map((row, order): DiagramNode => {
    const item = genericBrowserItem(
      browserItems,
      payload.family,
      row.id,
      row.module_id,
    );
    const position = genericPosition(row, row.id);
    const parentId = cleanText(row.relative_position_id);
    if (parentId && !nodeIds.has(parentId)) {
      throw new Error(
        `Generic diagram node ${row.id} references unknown relative parent ${parentId}.`,
      );
    }
    const relative = Boolean(position && parentId);
    const sourcePath = cleanText(row.source_path);
    const sourceRevision = cleanText(row.source_revision);
    const editable = row.editable !== false && Boolean(sourceRevision);
    return {
      id: row.id,
      ...(relative ? { parentId } : {}),
      order,
      mode: relative ? "relative" : position ? "absolute" : "auto",
      ...(position
        ? relative
          ? {
              dx: position.x,
              dy: position.y,
              relativePositionKind: "relative_position_id" as const,
            }
          : { fixed: true, x: position.x, y: position.y }
        : {}),
      width: 1,
      height: 1,
      title:
        localizedTitle(row.localized_titles, locale) ||
        cleanText(row.name_key) ||
        titleFromIdentifier(row.id),
      ...(cleanText(row.image_path)
        ? { imageUrl: cleanText(row.image_path) }
        : {}),
      payload: {
        editable,
        family: payload.family,
        familyId: item?.family_id || payload.family,
        itemId: item?.id || `module:${payload.family}/${row.id}`,
        itemKind: item?.kind || "module",
        moduleId:
          cleanText(item?.module_id) ||
          cleanText(row.module_id) ||
          `${payload.family}/${row.id}`,
        objectId: cleanText(item?.object_id) || row.id,
        projectId: payload.project_id,
        relativeRoot:
          cleanText(item?.relative_root) || sourceDirectory(sourcePath),
        sourcePath,
        sourceRevision,
        ...(cleanText(item?.source_root)
          ? { sourceRoot: cleanText(item?.source_root) }
          : {}),
      } satisfies GenericDiagramNodePayload,
    };
  });
  const edges = payload.edges.map((edge) => genericDiagramEdge(edge, nodeIds));
  rejectDuplicates(
    edges.map(
      (edge) =>
        `${edge.relationshipKind ?? edge.kind}:${edge.source}->${edge.target}`,
    ),
    "edge",
  );
  edges.sort(
    (left, right) =>
      left.source.localeCompare(right.source) ||
      left.target.localeCompare(right.target) ||
      (left.relationshipKind ?? left.kind).localeCompare(
        right.relationshipKind ?? right.kind,
      ),
  );
  return {
    schemaVersion: 1,
    gridSizePx: GENERIC_DIAGRAM_GRID_SIZE_PX,
    nodes,
    edges,
  };
}

/** Return standard provider-owned edit intents for one generic graph draft. */
export function genericDiagramEditIntents(
  baseDocument: DiagramDocument,
  draftDocument: DiagramDocument,
): GenericDiagramEditIntents {
  const baseNodes = nodeMap(baseDocument);
  const draftNodes = nodeMap(draftDocument);
  if (
    baseNodes.size !== draftNodes.size ||
    [...baseNodes].some(([id]) => !draftNodes.has(id))
  ) {
    throw new Error(
      "Generic diagram edits cannot add or remove nodes; use the provider's registered authoring operation.",
    );
  }
  const positionIntents: GenericModuleDiagramPositionIntent[] = [];
  for (const [id, baseNode] of [...baseNodes].sort(([left], [right]) =>
    left.localeCompare(right),
  )) {
    const draftNode = draftNodes.get(id);
    if (!draftNode) {
      continue;
    }
    const basePosition = authoredPosition(baseNode);
    const draftPosition = authoredPosition(draftNode);
    if (
      !draftPosition ||
      (basePosition &&
        basePosition.x === draftPosition.x &&
        basePosition.y === draftPosition.y)
    ) {
      continue;
    }
    positionIntents.push({
      node_id: id,
      source_revision: requiredSourceRevision(baseNode, id),
      x: draftPosition.x,
      y: draftPosition.y,
    });
  }

  const baseEdges = edgeMap(baseDocument);
  const draftEdges = edgeMap(draftDocument);
  const edgeIntents: GenericModuleDiagramEdgeIntent[] = [];
  for (const key of new Set([...baseEdges.keys(), ...draftEdges.keys()])) {
    const baseEdge = baseEdges.get(key);
    const draftEdge = draftEdges.get(key);
    if (Boolean(baseEdge) === Boolean(draftEdge)) {
      continue;
    }
    const edge = draftEdge ?? baseEdge;
    if (!edge) {
      continue;
    }
    const edgePayload = genericEdgePayload(edge);
    const ownerNode = baseNodes.get(edge.source);
    edgeIntents.push({
      kind: edge.relationshipKind ?? edge.kind,
      present: Boolean(draftEdge),
      source_id: edge.source,
      source_revision:
        edgePayload?.sourceRevision ||
        requiredSourceRevision(ownerNode, edge.source),
      target_id: edge.target,
    });
  }
  return { edgeIntents, positionIntents };
}

export function changedGenericDiagramNodeIds(
  baseDocument: DiagramDocument,
  draftDocument: DiagramDocument,
): string[] {
  const intents = genericDiagramEditIntents(baseDocument, draftDocument);
  return [
    ...new Set([
      ...intents.positionIntents.map((intent) => intent.node_id),
      ...intents.edgeIntents.flatMap((intent) => [
        intent.source_id,
        intent.target_id,
      ]),
    ]),
  ].sort();
}

export function genericDiagramSourcePath(
  document: DiagramDocument,
  id: string,
): string {
  const node = document.nodes.find((candidate) => candidate.id === id);
  return genericNodePayload(node)?.sourcePath ?? "";
}

export function genericDiagramNodeSourceRevision(
  document: DiagramDocument,
  id: string,
): string {
  return requiredSourceRevision(
    document.nodes.find((candidate) => candidate.id === id),
    id,
  );
}

function genericDiagramEdge(
  edge: ModuleDiagramEdge,
  nodeIds: ReadonlySet<string>,
): DiagramEdge {
  const source = exactIdentifier(edge.source, "edge source");
  const target = exactIdentifier(edge.target, "edge target");
  const relationshipKind = exactIdentifier(edge.kind, "edge kind");
  const edgeId =
    cleanText(edge.id) || `${relationshipKind}:${source}->${target}`;
  for (const [role, nodeId] of [
    ["source", source],
    ["target", target],
  ] as const) {
    if (!nodeIds.has(nodeId)) {
      throw new Error(
        `Generic diagram edge ${edgeId} references unknown ${role} node ${nodeId}.`,
      );
    }
  }
  return {
    id: edgeId,
    source,
    target,
    kind: diagramEdgeKind(relationshipKind),
    relationshipKind,
    ...(edge.relation_groups
      ? {
          relationshipGroups: edge.relation_groups.map((group) => ({
            groupIndex: group.group_index,
            ownerId: group.owner_id,
          })),
        }
      : {}),
    ...(cleanText(edge.source_revision)
      ? { payload: { sourceRevision: cleanText(edge.source_revision) } }
      : {}),
  };
}

function diagramEdgeKind(kind: string): DiagramEdgeKind {
  if (kind === "dependency") {
    return "dependency";
  }
  if (kind === "path") {
    return "path";
  }
  if (kind === "relative_position") {
    return "tree";
  }
  return "reference";
}

function genericBrowserItem(
  items: ProjectBrowserItem[],
  family: string,
  nodeId: string,
  moduleId: string | null | undefined,
): ProjectBrowserItem | undefined {
  const cleanModuleId = cleanText(moduleId);
  if (cleanModuleId) {
    const moduleMatches = items.filter(
      (item) => cleanText(item.module_id) === cleanModuleId,
    );
    if (moduleMatches.length === 1) {
      return moduleMatches[0];
    }
  }
  const matches = items.filter(
    (item) => item.family === family && item.object_id === nodeId,
  );
  return matches.length === 1 ? matches[0] : undefined;
}

function genericPosition(
  value: {
    position?: { x: number; y: number };
    x?: number | null;
    y?: number | null;
  },
  nodeId: string,
): { x: number; y: number } | null {
  if (value.position !== undefined) {
    if (!finiteNumber(value.position.x) || !finiteNumber(value.position.y)) {
      throw new Error(
        `Generic diagram node ${nodeId} requires finite position coordinates.`,
      );
    }
    return { x: value.position.x, y: value.position.y };
  }
  const hasX = value.x !== undefined && value.x !== null;
  const hasY = value.y !== undefined && value.y !== null;
  if (!hasX && !hasY) {
    return null;
  }
  if (!finiteNumber(value.x) || !finiteNumber(value.y)) {
    throw new Error(
      `Generic diagram node ${nodeId} requires both finite x and y coordinates.`,
    );
  }
  return { x: value.x, y: value.y };
}

function authoredPosition(node: DiagramNode): { x: number; y: number } | null {
  if (
    node.mode === "relative" &&
    finiteNumber(node.dx) &&
    finiteNumber(node.dy)
  ) {
    return { x: node.dx, y: node.dy };
  }
  return finiteNumber(node.x) && finiteNumber(node.y)
    ? { x: node.x, y: node.y }
    : null;
}

function requiredSourceRevision(
  node: DiagramNode | undefined,
  id: string,
): string {
  const revision = genericNodePayload(node)?.sourceRevision;
  if (!revision) {
    throw new Error(
      `Generic diagram node ${id} has no authoritative source revision.`,
    );
  }
  return revision;
}

function genericNodePayload(
  node: DiagramNode | undefined,
): GenericDiagramNodePayload | null {
  const value = node?.payload;
  if (!value || typeof value !== "object" || Array.isArray(value)) {
    return null;
  }
  const payload = value as Partial<GenericDiagramNodePayload>;
  return typeof payload.sourcePath === "string" &&
    typeof payload.sourceRevision === "string"
    ? (payload as GenericDiagramNodePayload)
    : null;
}

function genericEdgePayload(
  edge: DiagramEdge,
): GenericDiagramEdgePayload | null {
  const value = edge.payload;
  if (!value || typeof value !== "object" || Array.isArray(value)) {
    return null;
  }
  const sourceRevision = (value as Partial<GenericDiagramEdgePayload>)
    .sourceRevision;
  return typeof sourceRevision === "string" && sourceRevision
    ? { sourceRevision }
    : null;
}

function nodeMap(document: DiagramDocument): Map<string, DiagramNode> {
  return new Map(document.nodes.map((node) => [node.id, node]));
}

function edgeMap(document: DiagramDocument): Map<string, DiagramEdge> {
  return new Map(
    document.edges.map((edge) => [
      `${edge.relationshipKind ?? edge.kind}:${edge.source}->${edge.target}`,
      edge,
    ]),
  );
}

function localizedTitle(
  values: Record<string, string> | undefined,
  locale: Locale,
): string {
  if (!values) {
    return "";
  }
  const keys =
    locale === "zh" ? ["zh", "simp_chinese", "en"] : ["en", "english"];
  for (const key of keys) {
    const value = cleanText(values[key]);
    if (value) {
      return value;
    }
  }
  return Object.values(values).map(cleanText).find(Boolean) ?? "";
}

function titleFromIdentifier(value: string): string {
  return value
    .replace(/[_-]+/g, " ")
    .replace(/\b\w/g, (character) => character.toLocaleUpperCase());
}

function sourceDirectory(value: string): string {
  return value.includes("/") ? value.slice(0, value.lastIndexOf("/")) : "";
}

function finiteNumber(value: unknown): value is number {
  return typeof value === "number" && Number.isFinite(value);
}

function cleanText(value: unknown): string {
  return typeof value === "string" ? value.trim() : "";
}

function exactIdentifier(value: unknown, label: string): string {
  const cleaned = cleanText(value);
  if (!cleaned) {
    throw new Error(`Generic diagram ${label} must be a non-empty string.`);
  }
  if (value !== cleaned) {
    throw new Error(
      `Generic diagram ${label} ${JSON.stringify(value)} cannot contain surrounding whitespace.`,
    );
  }
  return cleaned;
}

function rejectDuplicates(values: string[], label: string): void {
  const seen = new Set<string>();
  for (const value of values) {
    if (seen.has(value)) {
      throw new Error(`Generic diagram contains duplicate ${label} ${value}.`);
    }
    seen.add(value);
  }
}
