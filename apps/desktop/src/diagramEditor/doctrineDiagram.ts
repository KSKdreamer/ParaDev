import type {
  DoctrineModuleDiagramEdgeIntent,
  DoctrineModuleDiagramPositionIntent,
  ModuleDiagramEdge,
  ModuleDiagramNode,
  ModuleDiagramPayload
} from "../services/paradev";
import { canonicalFamilyId } from "../projectModules";
import type {
  ProjectBrowserItem,
  ProjectBrowserPayload
} from "../types";
import type {
  DiagramDocument,
  DiagramEdge,
  DiagramNode
} from "./layoutModel";

export const DOCTRINE_DIAGRAM_GRID_SIZE_PX = 48;

const DOCTRINE_PROVIDER_SCHEMA =
  "paradev.hoi4.doctrine-diagram-projection.v1";
const DOCTRINE_SOURCE_FAMILY = "doctrine";

type DoctrineDiagramNodeRow = ModuleDiagramNode & {
  compiled_id?: string | null;
  definition_source_revision?: string;
  diagram_source_path?: string;
  module_id?: string | null;
};

type DoctrineDiagramNodePayload = {
  projectId: string;
  itemId: string;
  itemKind: "module";
  familyId: "doctrines";
  family: typeof DOCTRINE_SOURCE_FAMILY;
  objectId: string;
  moduleId: string;
  relativeRoot: string;
  sourceRoot?: string;
  sourcePath: string;
  diagramSourcePath?: string;
  sourceRevision: string;
  compiledId?: string;
  editable: boolean;
};

export type DoctrineDiagramEditIntents = {
  positionIntents: DoctrineModuleDiagramPositionIntent[];
  edgeIntents: DoctrineModuleDiagramEdgeIntent[];
};

export function buildDoctrineDiagramDocument(
  payload: ModuleDiagramPayload,
  browser: ProjectBrowserPayload
): DiagramDocument {
  assertDoctrineDiagramPayload(payload);
  const itemsByObjectId = doctrineBrowserItems(browser);
  const rows = payload.nodes
    .map((row) => doctrineNodeRow(row))
    .sort(
      (left, right) =>
        left.id.localeCompare(right.id) ||
        left.source_path.localeCompare(right.source_path)
    );
  const duplicateId = firstDuplicate(rows.map((row) => row.id));
  if (duplicateId) {
    throw new Error(
      `Doctrine diagram contains duplicate module id ${duplicateId}.`
    );
  }
  const nodes = rows.map((row, order): DiagramNode => {
    const item = itemsByObjectId.get(row.id);
    if (!item) {
      throw new Error(
        `Doctrine ${row.id} has no matching project module.`
      );
    }
    const sourceRevision = cleanText(row.source_revision);
    if (!sourceRevision) {
      throw new Error(
        `Doctrine ${row.id} has no authoritative diagram-state revision.`
      );
    }
    const positioned =
      finiteNumber(row.x) && finiteNumber(row.y);
    const diagramSourcePath = cleanText(
      row.diagram_source_path
    );
    const compiledId = cleanText(row.compiled_id);
    return {
      id: row.id,
      order,
      mode: positioned ? "absolute" : "auto",
      ...(positioned
        ? {
            fixed: true,
            x: row.x as number,
            y: row.y as number
          }
        : {}),
      width: 1,
      height: 1,
      title: cleanText(item.title) || titleFromIdentifier(row.id),
      ...(doctrineImageUrl(item)
        ? { imageUrl: doctrineImageUrl(item) }
        : {}),
      payload: {
        projectId: payload.project_id,
        itemId: item.id,
        itemKind: "module",
        familyId: "doctrines",
        family: DOCTRINE_SOURCE_FAMILY,
        objectId: row.id,
        moduleId:
          cleanText(item.module_id) ||
          cleanText(row.module_id) ||
          `${DOCTRINE_SOURCE_FAMILY}/${row.id}`,
        relativeRoot:
          cleanText(item.relative_root) ||
          sourceDirectory(row.source_path),
        ...(cleanText(item.source_root)
          ? { sourceRoot: cleanText(item.source_root) }
          : {}),
        sourcePath: row.source_path,
        ...(diagramSourcePath ? { diagramSourcePath } : {}),
        sourceRevision,
        ...(compiledId ? { compiledId } : {}),
        editable: row.editable === true && Boolean(diagramSourcePath)
      } satisfies DoctrineDiagramNodePayload
    };
  });
  const nodeIds = new Set(nodes.map((node) => node.id));
  const edges = payload.edges
    .map((edge) => doctrineDiagramEdge(edge, nodeIds))
    .filter((edge): edge is DiagramEdge => edge !== null)
    .sort(
      (left, right) =>
        edgeOrder(left.kind) - edgeOrder(right.kind) ||
        left.source.localeCompare(right.source) ||
        left.target.localeCompare(right.target)
    );
  return {
    schemaVersion: 1,
    gridSizePx: DOCTRINE_DIAGRAM_GRID_SIZE_PX,
    nodes,
    edges
  };
}

export function doctrineDiagramEditIntents(
  baseDocument: DiagramDocument,
  draftDocument: DiagramDocument
): DoctrineDiagramEditIntents {
  const baseNodes = doctrineNodeMap(baseDocument);
  const draftNodes = doctrineNodeMap(draftDocument);
  if (
    baseNodes.size !== draftNodes.size ||
    [...baseNodes].some(([id]) => !draftNodes.has(id))
  ) {
    throw new Error(
      "Doctrine diagram edits cannot add or remove nodes; create or remove the module instead."
    );
  }

  const positionIntents: DoctrineModuleDiagramPositionIntent[] = [];
  for (const [id, baseNode] of [...baseNodes].sort(
    ([left], [right]) => left.localeCompare(right)
  )) {
    const draftNode = draftNodes.get(id);
    if (!draftNode) {
      continue;
    }
    assertDoctrineNodeStructureUnchanged(baseNode, draftNode);
    const basePosition = absolutePosition(baseNode);
    const draftPosition = absolutePosition(draftNode);
    if (
      !draftPosition ||
      (basePosition &&
        basePosition.x === draftPosition.x &&
        basePosition.y === draftPosition.y)
    ) {
      continue;
    }
    const source = editableDoctrineNodePayload(baseNode);
    if (!source) {
      throw new Error(
        `Doctrine ${id} has no editable hidden diagram state.`
      );
    }
    positionIntents.push({
      doctrine_id: id,
      x: draftPosition.x,
      y: draftPosition.y,
      source_revision: source.sourceRevision
    });
  }

  const baseEdges = editableEdges(baseDocument);
  const draftEdges = editableEdges(draftDocument);
  const edgeKeys = new Set([
    ...baseEdges.keys(),
    ...draftEdges.keys()
  ]);
  const edgeIntents: DoctrineModuleDiagramEdgeIntent[] = [];
  for (const key of [...edgeKeys].sort()) {
    const baseEdge = baseEdges.get(key);
    const draftEdge = draftEdges.get(key);
    if (Boolean(baseEdge) === Boolean(draftEdge)) {
      continue;
    }
    const edge = draftEdge ?? baseEdge;
    if (!edge) {
      continue;
    }
    const kind =
      edge.kind === "reference"
        ? "mutually_exclusive"
        : "path";
    const [sourceId, targetId] =
      kind === "mutually_exclusive"
        ? sortedEndpoints(edge.source, edge.target)
        : [edge.source, edge.target];
    const source = editableDoctrineNodePayload(
      baseNodes.get(sourceId)
    );
    const target = editableDoctrineNodePayload(
      baseNodes.get(targetId)
    );
    if (!source || !target) {
      throw new Error(
        `Doctrine relation ${sourceId} -> ${targetId} requires editable hidden state at both endpoints.`
      );
    }
    edgeIntents.push({
      kind,
      source_id: sourceId,
      target_id: targetId,
      present: Boolean(draftEdge),
      source_revision: source.sourceRevision
    });
  }
  return { positionIntents, edgeIntents };
}

export function changedDoctrineDiagramNodeIds(
  baseDocument: DiagramDocument | null,
  draftDocument: DiagramDocument | null
): string[] {
  if (!baseDocument || !draftDocument) {
    return [];
  }
  const intents = doctrineDiagramEditIntents(
    baseDocument,
    draftDocument
  );
  const ids = new Set(
    intents.positionIntents.map((intent) => intent.doctrine_id)
  );
  for (const intent of intents.edgeIntents) {
    ids.add(intent.source_id);
    ids.add(intent.target_id);
  }
  return [...ids].sort();
}

export function doctrineDiagramSourcePath(
  document: DiagramDocument,
  nodeId: string
): string {
  return (
    doctrineNodePayload(
      document.nodes.find((node) => node.id === nodeId)
    )?.sourcePath ?? ""
  );
}

export function doctrineDiagramNodeEditable(
  document: DiagramDocument,
  nodeId: string
): boolean {
  return (
    doctrineNodePayload(
      document.nodes.find((node) => node.id === nodeId)
    )?.editable === true
  );
}

function assertDoctrineDiagramPayload(
  payload: ModuleDiagramPayload
): void {
  if (
    payload.provider_schema !== DOCTRINE_PROVIDER_SCHEMA ||
    payload.family !== DOCTRINE_SOURCE_FAMILY ||
    payload.source_kind !==
      "module_doctrine_definition_and_hidden_diagram_state"
  ) {
    throw new Error(
      "Doctrine diagram payload does not match the authoritative def.txt and hidden diagram-state provider."
    );
  }
}

function doctrineBrowserItems(
  browser: ProjectBrowserPayload
): Map<string, ProjectBrowserItem> {
  const items = browser.items.filter(
    (item) =>
      item.kind === "module" &&
      canonicalFamilyId(item.family_id, item.family) === "doctrines"
  );
  const duplicateId = firstDuplicate(
    items.map((item) => item.object_id)
  );
  if (duplicateId) {
    throw new Error(
      `Doctrine ${duplicateId} has more than one matching project module.`
    );
  }
  return new Map(items.map((item) => [item.object_id, item]));
}

function doctrineNodeRow(
  row: ModuleDiagramNode
): DoctrineDiagramNodeRow {
  if (
    !cleanText(row.id) ||
    !cleanText(row.source_path) ||
    !cleanText(row.source_revision)
  ) {
    throw new Error(
      "Doctrine diagram payload contains an invalid node source."
    );
  }
  return row as DoctrineDiagramNodeRow;
}

function doctrineDiagramEdge(
  edge: ModuleDiagramEdge,
  nodeIds: Set<string>
): DiagramEdge | null {
  if (
    !nodeIds.has(edge.source) ||
    !nodeIds.has(edge.target)
  ) {
    return null;
  }
  if (edge.kind === "path") {
    return {
      id: `path:${edge.source}->${edge.target}`,
      kind: "path",
      source: edge.source,
      target: edge.target
    };
  }
  if (edge.kind === "mutually_exclusive") {
    const [source, target] = sortedEndpoints(
      edge.source,
      edge.target
    );
    return {
      id: `reference:${source}->${target}`,
      kind: "reference",
      source,
      target
    };
  }
  return null;
}

function doctrineNodeMap(
  document: DiagramDocument
): Map<string, DiagramNode> {
  const rows = new Map(
    document.nodes.map((node) => [node.id, node])
  );
  if (rows.size !== document.nodes.length) {
    throw new Error("Doctrine diagram node ids must be unique.");
  }
  return rows;
}

function assertDoctrineNodeStructureUnchanged(
  baseNode: DiagramNode,
  draftNode: DiagramNode
): void {
  const base = doctrineNodePayload(baseNode);
  const draft = doctrineNodePayload(draftNode);
  if (
    !base ||
    !draft ||
    baseNode.mode !== draftNode.mode ||
    (baseNode.parentId ?? null) !== (draftNode.parentId ?? null) ||
    base.sourcePath !== draft.sourcePath ||
    base.diagramSourcePath !== draft.diagramSourcePath ||
    base.sourceRevision !== draft.sourceRevision ||
    base.editable !== draft.editable
  ) {
    throw new Error(
      `Doctrine ${baseNode.id} source scope cannot be changed from the diagram editor.`
    );
  }
}

function editableEdges(
  document: DiagramDocument
): Map<string, DiagramEdge> {
  const rows = document.edges.filter(
    (edge) => edge.kind === "path" || edge.kind === "reference"
  );
  return new Map(
    rows.map((edge) => {
      const [source, target] =
        edge.kind === "reference"
          ? sortedEndpoints(edge.source, edge.target)
          : [edge.source, edge.target];
      return [
        `${edge.kind}\u0000${source}\u0000${target}`,
        { ...edge, source, target }
      ];
    })
  );
}

function editableDoctrineNodePayload(
  node: DiagramNode | undefined
): DoctrineDiagramNodePayload | null {
  const payload = doctrineNodePayload(node);
  return payload?.editable === true ? payload : null;
}

function doctrineNodePayload(
  node: DiagramNode | undefined
): DoctrineDiagramNodePayload | null {
  if (
    !node?.payload ||
    typeof node.payload !== "object" ||
    Array.isArray(node.payload)
  ) {
    return null;
  }
  const payload = node.payload as Partial<DoctrineDiagramNodePayload>;
  return payload.family === DOCTRINE_SOURCE_FAMILY &&
    typeof payload.sourcePath === "string" &&
    typeof payload.sourceRevision === "string" &&
    typeof payload.editable === "boolean"
    ? (payload as DoctrineDiagramNodePayload)
    : null;
}

function absolutePosition(
  node: DiagramNode
): { x: number; y: number } | null {
  if (
    node.mode !== "absolute" ||
    !finiteNumber(node.x) ||
    !finiteNumber(node.y)
  ) {
    return null;
  }
  return { x: node.x, y: node.y };
}

function doctrineImageUrl(
  item: ProjectBrowserItem
): string {
  const source = item.sources.find((row) =>
    ["icon", "preview"].includes(row.slot)
  );
  return source?.relative_path || source?.path || "";
}

function sourceDirectory(path: string): string {
  const index = path.lastIndexOf("/");
  return index >= 0 ? path.slice(0, index) : "";
}

function sortedEndpoints(
  left: string,
  right: string
): [string, string] {
  return left.localeCompare(right) <= 0
    ? [left, right]
    : [right, left];
}

function edgeOrder(kind: DiagramEdge["kind"]): number {
  return kind === "path"
    ? 0
    : kind === "reference"
      ? 1
      : kind === "dependency"
        ? 2
        : 3;
}

function finiteNumber(value: unknown): value is number {
  return typeof value === "number" && Number.isFinite(value);
}

function cleanText(value: unknown): string {
  return typeof value === "string" ? value.trim() : "";
}

function firstDuplicate(values: string[]): string {
  const seen = new Set<string>();
  for (const value of values) {
    if (seen.has(value)) {
      return value;
    }
    seen.add(value);
  }
  return "";
}

function titleFromIdentifier(value: string): string {
  return value
    .split("_")
    .filter(Boolean)
    .map(
      (part) =>
        part.slice(0, 1).toUpperCase() +
        part.slice(1).toLowerCase()
    )
    .join(" ");
}
