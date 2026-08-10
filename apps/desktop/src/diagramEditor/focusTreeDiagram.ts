import type {
  FocusTreeModuleDiagramEdgeIntent,
  FocusTreeModuleDiagramPositionIntent,
  ModuleDiagramEdge,
  ModuleDiagramNode,
  ModuleDiagramPayload,
  ModuleDiagramTree
} from "../services/paradev";
import type { Locale } from "../i18n";
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

export const FOCUS_TREE_DIAGRAM_GRID_SIZE_PX = 96;

const FOCUS_TREE_PROVIDER_SCHEMA =
  "paradev.hoi4.focus-tree-diagram-projection.v1";
const FOCUS_TREE_SOURCE_FAMILY = "focus_tree";

type FocusTreeDiagramNodeRow = ModuleDiagramNode & {
  tree_id: string;
  source_path: string;
  source_revision: string;
};

type FocusTreeDiagramTreeRow = ModuleDiagramTree;

type FocusTreeDiagramNodePayload = {
  projectId: string;
  itemId: string;
  itemKind: "module";
  familyId: "focuses";
  family: typeof FOCUS_TREE_SOURCE_FAMILY;
  objectId: string;
  moduleId: string;
  relativeRoot: string;
  sourceRoot?: string;
  embeddedId: string;
  embeddedKind: "focus";
  sourcePath: string;
  sourceRevision: string;
  treeId: string;
  icon?: string;
  imagePath?: string;
};

export type FocusTreeDiagramEditIntents = {
  positionIntents: FocusTreeModuleDiagramPositionIntent[];
  edgeIntents: FocusTreeModuleDiagramEdgeIntent[];
};

export function buildFocusTreeDiagramDocument(
  payload: ModuleDiagramPayload,
  browser: ProjectBrowserPayload,
  locale: Locale = "en"
): DiagramDocument {
  assertFocusTreeDiagramPayload(payload);
  const trees = focusTreeRows(payload.trees);
  const itemByTreeId = focusTreeBrowserItems(browser, trees);
  const selectedTreeIds = new Set(itemByTreeId.keys());
  const rows = payload.nodes
    .filter(isFocusTreeDiagramNodeRow)
    .filter((row) => selectedTreeIds.has(row.tree_id))
    .sort(compareFocusNodes);
  const duplicateNodeId = firstDuplicate(rows.map((row) => row.id));
  if (duplicateNodeId) {
    throw new Error(
      `Focus tree diagram contains duplicate focus id ${duplicateNodeId}.`
    );
  }
  const nodeIds = new Set(rows.map((row) => row.id));
  const nodes = rows.map((row, order): DiagramNode => {
    const treeItem = itemByTreeId.get(row.tree_id);
    if (!treeItem) {
      throw new Error(
        `Focus tree ${row.tree_id} has no matching project module.`
      );
    }
    const item = focusTreeNodeBrowserItem(browser, row) ?? treeItem;
    const sourceRevision = cleanText(row.source_revision);
    if (!sourceRevision) {
      throw new Error(
        `Focus ${row.id} has no authoritative source revision.`
      );
    }
    const position = focusPosition(row);
    const relativeParentId = cleanText(row.relative_position_id);
    const relative =
      Boolean(relativeParentId) &&
      nodeIds.has(relativeParentId) &&
      position !== null;
    return {
      id: row.id,
      ...(relative ? { parentId: relativeParentId } : {}),
      order,
      mode: relative
        ? "relative"
        : position
          ? "absolute"
          : "auto",
      ...(position
        ? relative
          ? {
              dx: position.x,
              dy: position.y,
              relativePositionKind:
                "relative_position_id" as const
            }
          : {
              fixed: true,
              x: position.x,
              y: position.y
            }
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
        projectId: payload.project_id,
        itemId: item.id,
        itemKind: "module",
        familyId: "focuses",
        family: FOCUS_TREE_SOURCE_FAMILY,
        objectId: item.object_id || row.id,
        moduleId:
          cleanText(row.module_id) ||
          cleanText(item.module_id) ||
          `${FOCUS_TREE_SOURCE_FAMILY}/${row.tree_id}`,
        relativeRoot:
          cleanText(item.relative_root) ||
          sourceDirectory(row.source_path),
        ...(cleanText(item.source_root)
          ? { sourceRoot: cleanText(item.source_root) }
          : {}),
        embeddedId: row.id,
        embeddedKind: "focus",
        sourcePath: row.source_path,
        sourceRevision,
        treeId: row.tree_id,
        ...(cleanText(row.icon)
          ? { icon: cleanText(row.icon) }
          : {}),
        ...(cleanText(row.image_path)
          ? { imagePath: cleanText(row.image_path) }
          : {})
      } satisfies FocusTreeDiagramNodePayload
    };
  });
  return {
    schemaVersion: 1,
    gridSizePx: FOCUS_TREE_DIAGRAM_GRID_SIZE_PX,
    layoutOptions: { layerGap: 0 },
    nodes,
    edges: focusTreeDiagramEdges(payload.edges, rows)
  };
}

export function focusTreeDiagramEditIntents(
  payload: ModuleDiagramPayload,
  baseDocument: DiagramDocument,
  draftDocument: DiagramDocument
): FocusTreeDiagramEditIntents {
  assertFocusTreeDiagramPayload(payload);
  const baseNodes = nodeMap(baseDocument);
  const draftNodes = nodeMap(draftDocument);
  if (
    baseNodes.size !== draftNodes.size ||
    [...baseNodes].some(([id]) => !draftNodes.has(id))
  ) {
    throw new Error(
      "Focus tree diagram edits cannot add or remove focuses; edit the module source instead."
    );
  }

  const positionIntents: FocusTreeModuleDiagramPositionIntent[] = [];
  for (const [id, baseNode] of [...baseNodes].sort(
    ([left], [right]) => left.localeCompare(right)
  )) {
    const draftNode = draftNodes.get(id);
    if (!draftNode) {
      continue;
    }
    assertFocusStructureUnchanged(baseNode, draftNode);
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
    const sourceRevision =
      focusTreeNodePayload(baseNode)?.sourceRevision;
    if (!sourceRevision) {
      throw new Error(
        `Focus ${id} has no authoritative source revision.`
      );
    }
    positionIntents.push({
      focus_id: id,
      x: draftPosition.x,
      y: draftPosition.y,
      source_revision: sourceRevision
    });
  }

  assertLayoutEdgesUnchanged(baseDocument, draftDocument);
  const baseEdges = editableDiagramEdges(baseDocument);
  const draftEdges = editableDiagramEdges(draftDocument);
  const providerEdges = providerEdgeMap(payload.edges);
  const edgeKeys = new Set([
    ...baseEdges.keys(),
    ...draftEdges.keys()
  ]);
  const edgeIntents: FocusTreeModuleDiagramEdgeIntent[] = [];
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
      edge.kind === "dependency"
        ? "prerequisite"
        : "mutually_exclusive";
    const [sourceId, targetId] =
      kind === "mutually_exclusive"
        ? sortedEndpoints(edge.source, edge.target)
        : [edge.source, edge.target];
    const providerEdge = providerEdges.get(
      providerEdgeKey(kind, sourceId, targetId)
    );
    const sourceRevision = providerEdge
      ? cleanText(providerEdge.source_revision)
      : revisionForNewEdge(
          kind,
          sourceId,
          targetId,
          baseNodes
        );
    if (!sourceRevision) {
      throw new Error(
        `Focus relation ${sourceId} -> ${targetId} has no authoritative source revision.`
      );
    }
    edgeIntents.push({
      kind,
      source_id: sourceId,
      target_id: targetId,
      present: Boolean(draftEdge),
      source_revision: sourceRevision
    });
  }
  return { positionIntents, edgeIntents };
}

export function changedFocusTreeDiagramNodeIds(
  payload: ModuleDiagramPayload,
  baseDocument: DiagramDocument | null,
  draftDocument: DiagramDocument | null
): string[] {
  if (!baseDocument || !draftDocument) {
    return [];
  }
  const intents = focusTreeDiagramEditIntents(
    payload,
    baseDocument,
    draftDocument
  );
  const ids = new Set(
    intents.positionIntents.map((intent) => intent.focus_id)
  );
  for (const intent of intents.edgeIntents) {
    ids.add(intent.source_id);
    ids.add(intent.target_id);
  }
  return [...ids].sort();
}

export function focusTreeDiagramSourcePath(
  document: DiagramDocument,
  nodeId: string
): string {
  return (
    focusTreeNodePayload(
      document.nodes.find((node) => node.id === nodeId)
    )?.sourcePath ?? ""
  );
}

function assertFocusTreeDiagramPayload(
  payload: ModuleDiagramPayload
): void {
  if (
    payload.provider_schema !== FOCUS_TREE_PROVIDER_SCHEMA ||
    payload.family !== FOCUS_TREE_SOURCE_FAMILY ||
    !["module_def_pdx", "focus_collection_modules"].includes(
      payload.source_kind
    )
  ) {
    throw new Error(
      "Focus tree diagram payload does not match the authoritative module def.txt provider."
    );
  }
}

function focusTreeRows(
  rows: ModuleDiagramTree[] | undefined
): FocusTreeDiagramTreeRow[] {
  if (!Array.isArray(rows)) {
    throw new Error(
      "Focus tree diagram payload has no authoritative tree containers."
    );
  }
  const trees = rows.filter(
    (row): row is FocusTreeDiagramTreeRow =>
      Boolean(
        cleanText(row.id) &&
          cleanText(row.source_path) &&
          cleanText(row.source_revision)
      )
  );
  if (trees.length !== rows.length) {
    throw new Error(
      "Focus tree diagram payload contains an invalid tree container."
    );
  }
  const duplicateTreeId = firstDuplicate(
    trees.map((tree) => tree.id)
  );
  if (duplicateTreeId) {
    throw new Error(
      `Focus tree diagram contains duplicate tree id ${duplicateTreeId}.`
    );
  }
  return [...trees].sort(
    (left, right) =>
      left.id.localeCompare(right.id) ||
      left.source_path.localeCompare(right.source_path)
  );
}

function focusTreeBrowserItems(
  browser: ProjectBrowserPayload,
  trees: FocusTreeDiagramTreeRow[]
): Map<string, ProjectBrowserItem> {
  const items = browser.items
    .filter(
      (item) =>
        (item.kind === "module" || item.kind === "collection") &&
        canonicalFamilyId(item.family_id, item.family) ===
          "focuses"
    )
    .sort(
      (left, right) =>
        left.object_id.localeCompare(right.object_id) ||
        left.id.localeCompare(right.id)
    );
  if (items.length === 0 && trees.length > 0) {
    throw new Error(
      "Focus tree diagram has no matching project modules."
    );
  }
  const itemByTreeId = new Map<string, ProjectBrowserItem>();
  for (const tree of trees) {
    const matches = items.filter((item) =>
      browserItemMatchesTree(item, tree)
    );
    if (matches.length > 1) {
      throw new Error(
        `Focus tree ${tree.id} matches multiple project modules.`
      );
    }
    if (matches[0]) {
      itemByTreeId.set(tree.id, matches[0]);
    }
  }
  if (items.length > 0 && itemByTreeId.size === 0) {
    throw new Error(
      "The selected Focus tree module does not match the authoritative def.txt projection."
    );
  }
  return itemByTreeId;
}

function focusTreeNodeBrowserItem(
  browser: ProjectBrowserPayload,
  row: FocusTreeDiagramNodeRow
): ProjectBrowserItem | undefined {
  const moduleId = cleanText(row.module_id);
  const matches = browser.items.filter(
    (item) =>
      item.kind === "module" &&
      canonicalFamilyId(item.family_id, item.family) === "focuses" &&
      cleanText(item.collection_id) === row.tree_id &&
      [
        cleanText(item.object_id),
        cleanText(item.module_id),
        cleanText(item.id),
        cleanText(item.module_id).split("/").at(-1),
        cleanText(item.id).split(":").at(-1)
      ].includes(moduleId || row.id)
  );
  if (matches.length > 1) {
    throw new Error(
      `Focus ${row.id} matches multiple project modules.`
    );
  }
  return matches[0];
}

function browserItemMatchesTree(
  item: ProjectBrowserItem,
  tree: FocusTreeDiagramTreeRow
): boolean {
  const identifiers = new Set(
    [
      item.object_id,
      item.module_id,
      item.id,
      cleanText(item.module_id).split("/").at(-1),
      cleanText(item.id).split(":").at(-1)
    ].map(cleanText)
  );
  if (identifiers.has(tree.id)) {
    return true;
  }
  const relativeRoot = normalizePath(item.relative_root);
  const sourcePath = normalizePath(tree.source_path);
  return Boolean(
    relativeRoot &&
      (sourcePath === `${relativeRoot}/def.txt` ||
        sourcePath.startsWith(`${relativeRoot}/`))
  );
}

function isFocusTreeDiagramNodeRow(
  row: ModuleDiagramNode
): row is FocusTreeDiagramNodeRow {
  return Boolean(
    cleanText(row.id) &&
      cleanText(row.tree_id) &&
      cleanText(row.source_path) &&
      cleanText(row.source_revision)
  );
}

function compareFocusNodes(
  left: FocusTreeDiagramNodeRow,
  right: FocusTreeDiagramNodeRow
): number {
  return (
    left.tree_id.localeCompare(right.tree_id) ||
    left.id.localeCompare(right.id) ||
    left.source_path.localeCompare(right.source_path)
  );
}

function focusTreeDiagramEdges(
  providerEdges: ModuleDiagramEdge[],
  rows: FocusTreeDiagramNodeRow[]
): DiagramEdge[] {
  const nodeIds = new Set(rows.map((row) => row.id));
  const edges = new Map<string, DiagramEdge>();
  for (const row of rows) {
    const parentId = cleanText(row.relative_position_id);
    if (parentId && nodeIds.has(parentId) && parentId !== row.id) {
      addDiagramEdge(edges, "tree", parentId, row.id);
    }
  }
  for (const edge of providerEdges) {
    if (
      !nodeIds.has(edge.source) ||
      !nodeIds.has(edge.target) ||
      edge.source === edge.target
    ) {
      continue;
    }
    if (edge.kind === "prerequisite") {
      addDiagramEdge(
        edges,
        "dependency",
        edge.source,
        edge.target
      );
    } else if (edge.kind === "mutually_exclusive") {
      const [source, target] = sortedEndpoints(
        edge.source,
        edge.target
      );
      addDiagramEdge(edges, "reference", source, target);
    }
  }
  return [...edges.values()].sort(compareDiagramEdges);
}

function addDiagramEdge(
  edges: Map<string, DiagramEdge>,
  kind: DiagramEdge["kind"],
  source: string,
  target: string
): void {
  const id = `${kind}:${source}->${target}`;
  edges.set(id, { id, kind, source, target });
}

function compareDiagramEdges(
  left: DiagramEdge,
  right: DiagramEdge
): number {
  return (
    diagramEdgeOrder(left.kind) - diagramEdgeOrder(right.kind) ||
    left.source.localeCompare(right.source) ||
    left.target.localeCompare(right.target)
  );
}

function diagramEdgeOrder(kind: DiagramEdge["kind"]): number {
  return {
    dependency: 0,
    path: 1,
    tree: 2,
    reference: 3
  }[kind];
}

function nodeMap(
  document: DiagramDocument
): Map<string, DiagramNode> {
  const rows = new Map(
    document.nodes.map((node) => [node.id, node])
  );
  if (rows.size !== document.nodes.length) {
    throw new Error("Focus tree diagram node ids must be unique.");
  }
  return rows;
}

function assertFocusStructureUnchanged(
  baseNode: DiagramNode,
  draftNode: DiagramNode
): void {
  if (
    baseNode.mode !== draftNode.mode ||
    (baseNode.parentId ?? null) !==
      (draftNode.parentId ?? null) ||
    baseNode.relativePositionKind !==
      draftNode.relativePositionKind
  ) {
    throw new Error(
      `Focus ${baseNode.id} relative_position_id cannot be changed from the diagram editor.`
    );
  }
}

function authoredPosition(
  node: DiagramNode
): { x: number; y: number } | null {
  if (
    node.mode === "relative" &&
    finiteNumber(node.dx) &&
    finiteNumber(node.dy)
  ) {
    return { x: node.dx, y: node.dy };
  }
  if (
    node.mode === "absolute" &&
    finiteNumber(node.x) &&
    finiteNumber(node.y)
  ) {
    return { x: node.x, y: node.y };
  }
  return null;
}

function assertLayoutEdgesUnchanged(
  baseDocument: DiagramDocument,
  draftDocument: DiagramDocument
): void {
  const base = layoutEdgeKeys(baseDocument);
  const draft = layoutEdgeKeys(draftDocument);
  if (
    base.size !== draft.size ||
    [...base].some((key) => !draft.has(key))
  ) {
    throw new Error(
      "Focus relative_position_id links cannot be changed from the diagram editor."
    );
  }
}

function layoutEdgeKeys(
  document: DiagramDocument
): Set<string> {
  return new Set(
    document.edges
      .filter(
        (edge) =>
          edge.kind === "tree" || edge.kind === "path"
      )
      .map(
        (edge) =>
          `${edge.kind}\u0000${edge.source}\u0000${edge.target}`
      )
  );
}

function editableDiagramEdges(
  document: DiagramDocument
): Map<string, DiagramEdge> {
  const rows = document.edges
    .filter(
      (edge) =>
        edge.kind === "dependency" ||
        edge.kind === "reference"
    )
    .map((edge) => {
      const [source, target] =
        edge.kind === "reference"
          ? sortedEndpoints(edge.source, edge.target)
          : [edge.source, edge.target];
      return {
        ...edge,
        id: `${edge.kind}:${source}->${target}`,
        source,
        target
      };
    });
  return new Map(
    rows.map((edge) => [
      `${edge.kind}\u0000${edge.source}\u0000${edge.target}`,
      edge
    ])
  );
}

function providerEdgeMap(
  edges: ModuleDiagramEdge[]
): Map<string, ModuleDiagramEdge> {
  const rows = edges.filter(
    (
      edge
    ): edge is ModuleDiagramEdge & {
      kind: "prerequisite" | "mutually_exclusive";
    } =>
      edge.kind === "prerequisite" ||
      edge.kind === "mutually_exclusive"
  );
  return new Map(
    rows.map((edge) => {
      const [source, target] =
        edge.kind === "mutually_exclusive"
          ? sortedEndpoints(edge.source, edge.target)
          : [edge.source, edge.target];
      return [
        providerEdgeKey(edge.kind, source, target),
        edge
      ];
    })
  );
}

function providerEdgeKey(
  kind: "prerequisite" | "mutually_exclusive",
  source: string,
  target: string
): string {
  return `${kind}\u0000${source}\u0000${target}`;
}

function revisionForNewEdge(
  kind: "prerequisite" | "mutually_exclusive",
  sourceId: string,
  targetId: string,
  baseNodes: Map<string, DiagramNode>
): string {
  if (kind === "prerequisite") {
    return (
      focusTreeNodePayload(
        baseNodes.get(targetId)
      )?.sourceRevision ?? ""
    );
  }
  const source = focusTreeNodePayload(baseNodes.get(sourceId));
  const target = focusTreeNodePayload(baseNodes.get(targetId));
  if (
    !source ||
    !target ||
    source.sourcePath !== target.sourcePath ||
    source.sourceRevision !== target.sourceRevision
  ) {
    throw new Error(
      "A new mutually-exclusive relation must stay within one reviewed Focus tree source file."
    );
  }
  return source.sourceRevision;
}

function focusTreeNodePayload(
  node: DiagramNode | undefined
): FocusTreeDiagramNodePayload | null {
  if (
    !node?.payload ||
    typeof node.payload !== "object" ||
    Array.isArray(node.payload)
  ) {
    return null;
  }
  const payload =
    node.payload as Partial<FocusTreeDiagramNodePayload>;
  return payload.family === FOCUS_TREE_SOURCE_FAMILY &&
    payload.embeddedKind === "focus" &&
    typeof payload.sourcePath === "string" &&
    typeof payload.sourceRevision === "string"
    ? (payload as FocusTreeDiagramNodePayload)
    : null;
}

function focusPosition(
  row: FocusTreeDiagramNodeRow
): { x: number; y: number } | null {
  const x = row.x;
  const y = row.y;
  if (x == null && y == null) {
    return null;
  }
  if (!finiteNumber(x) || !finiteNumber(y)) {
    throw new Error(
      `Focus ${row.id} has invalid authored coordinates.`
    );
  }
  return { x, y };
}

function finiteNumber(
  value: unknown
): value is number {
  return typeof value === "number" && Number.isFinite(value);
}

function sortedEndpoints(
  left: string,
  right: string
): [string, string] {
  return left.localeCompare(right) <= 0
    ? [left, right]
    : [right, left];
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

function sourceDirectory(path: string): string {
  const clean = normalizePath(path);
  const separator = clean.lastIndexOf("/");
  return separator >= 0 ? clean.slice(0, separator) : "";
}

function normalizePath(value: string | undefined | null): string {
  return cleanText(value)
    .replace(/\\/g, "/")
    .replace(/\/+$/, "");
}

function cleanText(value: unknown): string {
  return typeof value === "string" ? value.trim() : "";
}

function localizedTitle(
  value: unknown,
  locale: Locale
): string {
  if (
    !value ||
    typeof value !== "object" ||
    Array.isArray(value)
  ) {
    return "";
  }
  const rows = Object.entries(value)
    .filter(
      (row): row is [string, string] =>
        typeof row[1] === "string" &&
        Boolean(row[1].trim())
    )
    .sort(([left], [right]) => left.localeCompare(right));
  const byLanguage = new Map(rows);
  const preferred =
    locale === "zh"
      ? ["l_simp_chinese", "l_chinese", "l_english"]
      : ["l_english", "l_simp_chinese", "l_chinese"];
  for (const language of preferred) {
    const title = cleanText(byLanguage.get(language));
    if (title) {
      return title;
    }
  }
  return cleanText(rows[0]?.[1]);
}

function titleFromIdentifier(value: string): string {
  return value
    .replace(/[_-]+/g, " ")
    .replace(/\b\w/g, (character) => character.toUpperCase());
}
