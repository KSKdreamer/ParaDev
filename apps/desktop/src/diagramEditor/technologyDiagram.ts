import type {
  ModuleDiagramEdge,
  ModuleDiagramPayload,
  TechnologyModuleDiagramEdgeIntent,
  TechnologyModuleDiagramPositionIntent
} from "../services/paradev";
import type { ProjectBrowserItem, ProjectBrowserPayload } from "../types";
import type {
  DiagramDocument,
  DiagramEdge,
  DiagramNode
} from "./layoutModel";

export const TECHNOLOGY_DIAGRAM_GRID_SIZE_PX = 48;

type TechnologyDiagramNodePayload = {
  projectId: string;
  itemId: string;
  itemKind: ProjectBrowserItem["kind"];
  familyId: "technologies";
  family: "technology";
  objectId: string;
  moduleId: string;
  relativeRoot: string;
  sourceRoot?: string;
  sourcePath: string;
  sourceRevision: string;
};

export type TechnologyDiagramEditIntents = {
  positionIntents: TechnologyModuleDiagramPositionIntent[];
  edgeIntents: TechnologyModuleDiagramEdgeIntent[];
};

export function buildTechnologyDiagramDocument(
  payload: ModuleDiagramPayload,
  browser: ProjectBrowserPayload
): DiagramDocument {
  if (payload.family !== "technology") {
    throw new Error(
      `Technology diagram payload has unexpected family ${payload.family}.`
    );
  }
  const itemsByObjectId = new Map(
    browser.items
      .filter(
        (item) =>
          item.kind === "module" &&
          item.family === "technology"
      )
      .map((item) => [item.object_id, item])
  );
  const nodes = payload.nodes
    .map((row, order): DiagramNode => {
      const item = itemsByObjectId.get(row.id);
      const imageUrl = technologyImageUrl(item);
      const sourceRevision = row.source_revision?.trim();
      if (!sourceRevision) {
        throw new Error(
          `Technology ${row.id} has no authoritative source revision.`
        );
      }
      const positioned =
        typeof row.x === "number" &&
        Number.isFinite(row.x) &&
        typeof row.y === "number" &&
        Number.isFinite(row.y);
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
        ...(imageUrl ? { imageUrl } : {}),
        title:
          item?.title ||
          titleFromIdentifier(row.id),
        payload: {
          projectId: payload.project_id,
          itemId: item?.id || `module:technology/${row.id}`,
          itemKind: "module",
          familyId: "technologies",
          family: "technology",
          objectId: row.id,
          moduleId: item?.module_id || `technology/${row.id}`,
          relativeRoot:
            item?.relative_root ||
            row.source_path.replace(/\/def\.txt$/, ""),
          ...(item?.source_root
            ? { sourceRoot: item.source_root }
            : {}),
          sourcePath: row.source_path,
          sourceRevision
        } satisfies TechnologyDiagramNodePayload
      };
    })
    .sort(
      (left, right) =>
        left.order - right.order || left.id.localeCompare(right.id)
    );
  const nodeIds = new Set(nodes.map((node) => node.id));
  const edges = payload.edges
    .filter(
      (edge): edge is ModuleDiagramEdge & {
        kind: "dependency" | "path";
      } =>
        (edge.kind === "dependency" || edge.kind === "path") &&
        nodeIds.has(edge.source) &&
        nodeIds.has(edge.target)
    )
    .map(
      (edge): DiagramEdge => ({
        id: `${edge.kind}:${edge.source}->${edge.target}`,
        kind: edge.kind,
        source: edge.source,
        target: edge.target
      })
    )
    .sort(
      (left, right) =>
        edgeOrder(left.kind) - edgeOrder(right.kind) ||
        left.source.localeCompare(right.source) ||
        left.target.localeCompare(right.target)
    );
  return {
    schemaVersion: 1,
    gridSizePx: TECHNOLOGY_DIAGRAM_GRID_SIZE_PX,
    nodes,
    edges
  };
}

export function technologyDiagramEditIntents(
  baseDocument: DiagramDocument,
  draftDocument: DiagramDocument
): TechnologyDiagramEditIntents {
  const baseNodes = new Map(
    baseDocument.nodes.map((node) => [node.id, node])
  );
  const draftNodes = new Map(
    draftDocument.nodes.map((node) => [node.id, node])
  );
  if (
    baseNodes.size !== draftNodes.size ||
    [...baseNodes].some(([id]) => !draftNodes.has(id))
  ) {
    throw new Error(
      "Technology diagram edits cannot add or remove nodes; create or remove the module instead."
    );
  }
  const positionIntents: TechnologyModuleDiagramPositionIntent[] = [];
  for (const [id, baseNode] of [...baseNodes].sort(([left], [right]) =>
    left.localeCompare(right)
  )) {
    const draftNode = draftNodes.get(id);
    if (!draftNode) {
      continue;
    }
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
    const sourceRevision = technologyNodePayload(
      baseNode
    )?.sourceRevision;
    if (!sourceRevision) {
      throw new Error(
        `Technology ${id} has no authoritative source revision.`
      );
    }
    positionIntents.push({
      technology_id: id,
      x: draftPosition.x,
      y: draftPosition.y,
      source_revision: sourceRevision
    });
  }

  const baseEdges = editableEdges(baseDocument);
  const draftEdges = editableEdges(draftDocument);
  const edgeKeys = new Set([
    ...baseEdges.keys(),
    ...draftEdges.keys()
  ]);
  const edgeIntents: TechnologyModuleDiagramEdgeIntent[] = [];
  for (const key of [...edgeKeys].sort()) {
    const baseEdge = baseEdges.get(key);
    const draftEdge = draftEdges.get(key);
    if (Boolean(baseEdge) === Boolean(draftEdge)) {
      continue;
    }
    const edge = draftEdge ?? baseEdge;
    if (!edge || (edge.kind !== "dependency" && edge.kind !== "path")) {
      continue;
    }
    const ownerId =
      edge.kind === "dependency" ? edge.target : edge.source;
    const sourceRevision = technologyNodePayload(
      baseNodes.get(ownerId)
    )?.sourceRevision;
    if (!sourceRevision) {
      throw new Error(
        `Technology ${ownerId} has no authoritative source revision.`
      );
    }
    edgeIntents.push({
      kind: edge.kind,
      source_id: edge.source,
      target_id: edge.target,
      present: Boolean(draftEdge),
      source_revision: sourceRevision
    });
  }
  return { positionIntents, edgeIntents };
}

export function changedTechnologyDiagramNodeIds(
  baseDocument: DiagramDocument | null,
  draftDocument: DiagramDocument | null
): string[] {
  if (!baseDocument || !draftDocument) {
    return [];
  }
  const intents = technologyDiagramEditIntents(
    baseDocument,
    draftDocument
  );
  const ids = new Set(
    intents.positionIntents.map((intent) => intent.technology_id)
  );
  for (const intent of intents.edgeIntents) {
    ids.add(
      intent.kind === "dependency"
        ? intent.target_id
        : intent.source_id
    );
  }
  return [...ids].sort();
}

export function technologyDiagramSourcePath(
  document: DiagramDocument,
  nodeId: string
): string {
  return (
    technologyNodePayload(
      document.nodes.find((node) => node.id === nodeId)
    )?.sourcePath ?? ""
  );
}

function editableEdges(
  document: DiagramDocument
): Map<string, DiagramEdge> {
  const rows = document.edges.filter(
    (edge) =>
      edge.kind === "dependency" || edge.kind === "path"
  );
  return new Map(
    rows.map((edge) => [
      `${edge.kind}\u0000${edge.source}\u0000${edge.target}`,
      edge
    ])
  );
}

function absolutePosition(
  node: DiagramNode
): { x: number; y: number } | null {
  if (
    node.mode !== "absolute" ||
    typeof node.x !== "number" ||
    !Number.isFinite(node.x) ||
    typeof node.y !== "number" ||
    !Number.isFinite(node.y)
  ) {
    return null;
  }
  return { x: node.x, y: node.y };
}

function technologyNodePayload(
  node: DiagramNode | undefined
): TechnologyDiagramNodePayload | null {
  if (
    !node?.payload ||
    typeof node.payload !== "object" ||
    Array.isArray(node.payload)
  ) {
    return null;
  }
  const payload = node.payload as Partial<TechnologyDiagramNodePayload>;
  return payload.family === "technology" &&
    typeof payload.sourcePath === "string" &&
    typeof payload.sourceRevision === "string"
    ? (payload as TechnologyDiagramNodePayload)
    : null;
}

function technologyImageUrl(
  item: ProjectBrowserItem | undefined
): string {
  const source = item?.sources.find((row) =>
    ["preview", "icon"].includes(row.slot)
  );
  return source?.relative_path || source?.path || "";
}

function edgeOrder(kind: DiagramEdge["kind"]): number {
  return kind === "dependency"
    ? 0
    : kind === "path"
      ? 1
      : kind === "tree"
        ? 2
        : 3;
}

function titleFromIdentifier(value: string): string {
  return value
    .replace(/^TECHNOLOGY_/, "")
    .split("_")
    .filter(Boolean)
    .map(
      (part) =>
        part.slice(0, 1).toUpperCase() +
        part.slice(1).toLowerCase()
    )
    .join(" ");
}
