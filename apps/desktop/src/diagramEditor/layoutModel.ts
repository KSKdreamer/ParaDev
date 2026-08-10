import { diagramNodeRelationshipScopeKey } from "./diagramScope";

export type DiagramNodeId = string;

export type DiagramPositionMode = "absolute" | "relative" | "auto";

export type DiagramRelativePositionKind = "legacy_offset" | "relative_position_id";

export type DiagramEdgeKind = "tree" | "reference" | "dependency" | "path";

export type DiagramNode = {
  id: DiagramNodeId;
  parentId?: DiagramNodeId | null;
  order: number;
  mode: DiagramPositionMode;
  x?: number;
  y?: number;
  dx?: number;
  dy?: number;
  relativePositionKind?: DiagramRelativePositionKind;
  fixed?: boolean;
  width: number;
  height: number;
  priority?: number;
  subtreeWidth?: number;
  subtreeWidthDelta?: number;
  subtreeCenterOffset?: number;
  imageUrl?: string;
  title?: string;
  payload?: unknown;
};

export type DiagramChildNodeInput = Omit<DiagramNode, "order" | "parentId"> & {
  order?: number;
};

export type DiagramEdge = {
  id: string;
  source: DiagramNodeId;
  target: DiagramNodeId;
  kind: DiagramEdgeKind;
  label?: string;
  relationshipKind?: string;
  relationshipGroups?: Array<{
    ownerId: string;
    groupIndex: number;
  }>;
  payload?: unknown;
};

export type DiagramDocument = {
  schemaVersion: 1;
  gridSizePx: number;
  layoutOptions?: DiagramLayoutOptions;
  nodes: DiagramNode[];
  edges: DiagramEdge[];
  viewport?: {
    x: number;
    y: number;
    zoom: number;
  };
};

export type DiagramBounds = {
  minX: number;
  minY: number;
  maxX: number;
  maxY: number;
};

export type ResolvedDiagramNode = DiagramNode & {
  worldX: number;
  worldY: number;
  subtreeBounds: DiagramBounds;
};

export type ResolvedDiagramLayout = {
  nodes: ResolvedDiagramNode[];
  nodesById: Record<DiagramNodeId, ResolvedDiagramNode>;
};

export type DiagramLayoutOptions = {
  rootX?: number;
  rootY?: number;
  siblingGap?: number;
  layerGap?: number;
  sourceFocusSlots?: boolean;
};

export type CanvasPoint = {
  x: number;
  y: number;
};

export type DiagramMoveDelta = {
  dx: number;
  dy: number;
};

export type DiagramGridPosition = {
  x: number;
  y: number;
};

export type DiagramNodeLayoutHints = {
  priority?: number;
  subtreeCenterOffset?: number;
  subtreeWidth?: number;
  subtreeWidthDelta?: number;
};

export type DiagramViewport = {
  x: number;
  y: number;
  zoom: number;
};

const DEFAULT_ROOT_X = 0;
const DEFAULT_ROOT_Y = 0;
const DEFAULT_SIBLING_GAP = 1;
const DEFAULT_LAYER_GAP = 4;

type ParentContext = {
  autoSlot?: CanvasPoint;
  node: ResolvedDiagramNode;
};

type DiagramRect = CanvasPoint & {
  height: number;
  width: number;
};

export function resolveDiagramLayout(document: DiagramDocument, options: DiagramLayoutOptions = {}): ResolvedDiagramLayout {
  const layoutOptions = { ...(document.layoutOptions ?? {}), ...options };
  const byId = new Map(document.nodes.map((node) => [node.id, node]));
  if (byId.size !== document.nodes.length) {
    throw new Error("Diagram nodes must have unique ids.");
  }
  for (const node of document.nodes) {
    if (node.parentId && !byId.has(node.parentId)) {
      throw new Error(`Diagram node ${node.id} references missing parent ${node.parentId}.`);
    }
  }

  const childrenByParent = groupChildren(document.nodes);
  const slotWidthFor = makeSlotWidthResolver(childrenByParent, layoutOptions);
  const rootNodes = sortNodes(document.nodes.filter((node) => !node.parentId));
  if (document.nodes.length > 0 && rootNodes.length === 0) {
    throw new Error("Diagram document has no root nodes; check parent links for cycles.");
  }
  const resolved: ResolvedDiagramNode[] = [];
  const nodesById: Record<DiagramNodeId, ResolvedDiagramNode> = {};
  const visiting = new Set<DiagramNodeId>();

  const resolveNode = (node: DiagramNode, parent?: ParentContext): ResolvedDiagramNode => {
    if (visiting.has(node.id)) {
      throw new Error(`Diagram node ${node.id} creates a cycle.`);
    }
    visiting.add(node.id);

    const point = resolvePoint(node, parent, layoutOptions);
    const base: ResolvedDiagramNode = {
      ...node,
      worldX: point.x,
      worldY: point.y,
      subtreeBounds: {
        minX: point.x,
        minY: point.y,
        maxX: point.x + snapGrid(node.width),
        maxY: point.y + snapGrid(node.height)
      }
    };

    resolved.push(base);
    nodesById[node.id] = base;

    const children = childrenByParent.get(node.id) ?? [];
    const autoSlots = autoChildSlots(base, children, layoutOptions, slotWidthFor);
    for (const child of children) {
      if (!byId.has(child.id)) {
        throw new Error(`Diagram child ${child.id} is not registered.`);
      }
      const childNode = resolveNode(child, {
        node: base,
        autoSlot: autoSlots.get(child.id)
      });
      base.subtreeBounds = mergeBounds(base.subtreeBounds, childNode.subtreeBounds);
    }

    visiting.delete(node.id);
    return base;
  };

  const rootGap = gap(layoutOptions.siblingGap, DEFAULT_SIBLING_GAP);
  let rootCursor = layoutOptions.rootX ?? DEFAULT_ROOT_X;
  rootNodes.forEach((node) => {
    const rootWidth = slotWidthFor(node);
    const rootSlot =
      node.mode === "auto"
        ? {
            x: snapGrid(rootCursor),
            y: layoutOptions.rootY ?? DEFAULT_ROOT_Y
          }
        : undefined;
    resolveNode(node, rootSlot ? { node: placeholderRoot(), autoSlot: rootSlot } : undefined);
    rootCursor = snapGrid(rootCursor + rootWidth + rootGap);
  });
  if (resolved.length !== document.nodes.length) {
    throw new Error("Diagram document has unresolved nodes; check parent links for cycles.");
  }

  return { nodes: resolved, nodesById };
}

export function pinDiagramNode(node: DiagramNode, resolved: Pick<ResolvedDiagramNode, "worldX" | "worldY">): DiagramNode {
  const rest = { ...node };
  delete rest.dx;
  delete rest.dy;
  delete rest.relativePositionKind;
  return {
    ...rest,
    mode: "absolute",
    fixed: true,
    x: snapGrid(resolved.worldX),
    y: snapGrid(resolved.worldY)
  };
}

export function moveDiagramNode(document: DiagramDocument, nodeId: DiagramNodeId, delta: DiagramMoveDelta): DiagramDocument {
  const node = document.nodes.find((candidate) => candidate.id === nodeId);
  if (!node) {
    return document;
  }
  const resolved = resolveDiagramLayout(document).nodesById[nodeId];
  if (!resolved) {
    return document;
  }
  return {
    ...document,
    nodes: document.nodes.map((candidate) =>
      candidate.id === nodeId
        ? moveSingleDiagramNode(candidate, delta, {
            worldX: resolved.worldX + delta.dx,
            worldY: resolved.worldY + delta.dy
          })
        : candidate
    )
  };
}

export function setDiagramNodePosition(document: DiagramDocument, nodeId: DiagramNodeId, position: DiagramGridPosition): DiagramDocument {
  const node = document.nodes.find((candidate) => candidate.id === nodeId);
  if (!node) {
    return document;
  }
  const resolved = resolveDiagramLayout(document).nodesById[nodeId];
  if (!resolved) {
    return document;
  }
  const x = snapGrid(position.x);
  const y = snapGrid(position.y);
  if (resolved.worldX === x && resolved.worldY === y) {
    return document;
  }
  return moveDiagramNode(document, nodeId, {
    dx: x - resolved.worldX,
    dy: y - resolved.worldY
  });
}

export function setDiagramNodeLayoutHints(document: DiagramDocument, nodeId: DiagramNodeId, hints: DiagramNodeLayoutHints): DiagramDocument {
  const node = document.nodes.find((candidate) => candidate.id === nodeId);
  if (!node) {
    return document;
  }
  const updated = applyDiagramNodeLayoutHints(node, hints);
  if (sameDiagramNode(node, updated)) {
    return document;
  }
  return {
    ...document,
    nodes: document.nodes.map((candidate) => (candidate.id === nodeId ? updated : candidate))
  };
}

export function setDiagramViewport(document: DiagramDocument, viewport: DiagramViewport): DiagramDocument {
  if (!Number.isFinite(viewport.x) || !Number.isFinite(viewport.y) || !Number.isFinite(viewport.zoom) || viewport.zoom <= 0) {
    return document;
  }
  const nextViewport: DiagramViewport = {
    x: snapViewportNumber(viewport.x),
    y: snapViewportNumber(viewport.y),
    zoom: snapViewportNumber(viewport.zoom)
  };
  if (document.viewport && document.viewport.x === nextViewport.x && document.viewport.y === nextViewport.y && document.viewport.zoom === nextViewport.zoom) {
    return document;
  }
  return {
    ...document,
    viewport: nextViewport
  };
}

export function moveDiagramSubtree(document: DiagramDocument, nodeId: DiagramNodeId, delta: DiagramMoveDelta): DiagramDocument {
  const node = document.nodes.find((candidate) => candidate.id === nodeId);
  if (!node) {
    return document;
  }
  const targetIds = collectSubtreeNodeIds(document, nodeId);
  const resolved = resolveDiagramLayout(document).nodesById;
  return {
    ...document,
    nodes: document.nodes.map((candidate) => {
      if (candidate.id === nodeId) {
        return moveSingleDiagramNode(candidate, delta, {
          worldX: resolved[candidate.id].worldX + delta.dx,
          worldY: resolved[candidate.id].worldY + delta.dy
        });
      }
      if (targetIds.has(candidate.id) && candidate.mode === "absolute") {
        return pinDiagramNode(candidate, {
          worldX: resolved[candidate.id].worldX + delta.dx,
          worldY: resolved[candidate.id].worldY + delta.dy
        });
      }
      return candidate;
    })
  };
}

export function removeDiagramSubtree(document: DiagramDocument, nodeId: DiagramNodeId): DiagramDocument {
  const node = document.nodes.find((candidate) => candidate.id === nodeId);
  if (!node || isProtectedSourceBackedNode(node)) {
    return document;
  }
  const targetIds = collectSubtreeNodeIds(document, nodeId);
  return {
    ...document,
    nodes: document.nodes.filter((node) => !targetIds.has(node.id)),
    edges: document.edges.filter((edge) => !targetIds.has(edge.source) && !targetIds.has(edge.target))
  };
}

export function removeDiagramNodeOnly(document: DiagramDocument, nodeId: DiagramNodeId): DiagramDocument {
  const node = document.nodes.find((candidate) => candidate.id === nodeId);
  if (!node || isProtectedSourceBackedNode(node)) {
    return document;
  }
  const children = sortNodes(document.nodes.filter((candidate) => candidate.parentId === node.id));
  const childIds = new Set(children.map((child) => child.id));
  const promotedOrderById = new Map(children.map((child, index) => [child.id, node.order + index]));
  const siblingOrderOffset = Math.max(children.length - 1, 0);
  const targetParentKey = parentKey(node.parentId);
  const resolved = resolveDiagramLayout(document).nodesById;
  const parent = node.parentId ? resolved[node.parentId] : undefined;
  const promotedTreeEdges: DiagramEdge[] = node.parentId
    ? children.map((child) => ({
        id: `tree:${node.parentId}->${child.id}`,
        source: node.parentId as DiagramNodeId,
        target: child.id,
        kind: "tree" as const
      }))
    : [];

  return {
    ...document,
    nodes: document.nodes.flatMap((candidate): DiagramNode[] => {
      if (candidate.id === node.id) {
        return [];
      }
      if (!childIds.has(candidate.id)) {
        if (siblingOrderOffset > 0 && parentKey(candidate.parentId) === targetParentKey && candidate.order > node.order) {
          return [{ ...candidate, order: candidate.order + siblingOrderOffset }];
        }
        return [candidate];
      }
      const promoted = { ...candidate, order: promotedOrderById.get(candidate.id) ?? candidate.order };
      if (node.parentId) {
        promoted.parentId = node.parentId;
      } else {
        delete promoted.parentId;
      }
      if (promoted.mode === "absolute") {
        return [promoted];
      }
      const current = resolved[promoted.id];
      if (promoted.mode === "relative" && parent) {
        return [relativeDiagramNode(promoted, current, parent)];
      }
      return [pinDiagramNode(promoted, current)];
    }),
    edges: [
      ...document.edges.filter((edge) => edge.source !== node.id && edge.target !== node.id && (edge.kind !== "tree" || !childIds.has(edge.target))),
      ...promotedTreeEdges
    ]
  };
}

export function insertDiagramChildNode(document: DiagramDocument, parentId: DiagramNodeId, node: DiagramChildNodeInput): DiagramDocument {
  if (!document.nodes.some((candidate) => candidate.id === parentId) || document.nodes.some((candidate) => candidate.id === node.id)) {
    return document;
  }
  const { order, ...nodeFields } = node;
  const nextOrder = nextDiagramChildOrder(document, parentId);
  const child: DiagramNode = {
    ...nodeFields,
    parentId,
    order: appendSafeDiagramOrder(order, nextOrder)
  };
  const parent = document.nodes.find((candidate) => candidate.id === parentId);
  if (parent && !sameDiagramRelationshipScope(parent, child)) {
    return document;
  }
  const edge: DiagramEdge = {
    id: `tree:${parentId}->${node.id}`,
    source: parentId,
    target: node.id,
    kind: "tree"
  };
  return {
    ...document,
    nodes: [...document.nodes, child],
    edges: document.edges.some((candidate) => candidate.id === edge.id) ? document.edges : [...document.edges, edge]
  };
}

export function insertDiagramRootNode(document: DiagramDocument, node: DiagramChildNodeInput): DiagramDocument {
  if (document.nodes.some((candidate) => candidate.id === node.id)) {
    return document;
  }
  const { order, ...nodeFields } = node;
  const nextOrder = nextDiagramRootOrder(document);
  return {
    ...document,
    nodes: [
      ...document.nodes,
      {
        ...nodeFields,
        order: appendSafeDiagramOrder(order, nextOrder)
      }
    ]
  };
}

export function reorderDiagramSibling(document: DiagramDocument, nodeId: DiagramNodeId, direction: -1 | 1): DiagramDocument {
  const node = document.nodes.find((candidate) => candidate.id === nodeId);
  if (!node) {
    return document;
  }
  const siblings = sortNodes(document.nodes.filter((candidate) => parentKey(candidate.parentId) === parentKey(node.parentId)));
  const index = siblings.findIndex((candidate) => candidate.id === nodeId);
  const nextIndex = index + direction;
  if (index < 0 || nextIndex < 0 || nextIndex >= siblings.length) {
    return document;
  }
  const reordered = [...siblings];
  const [selected] = reordered.splice(index, 1);
  reordered.splice(nextIndex, 0, selected);
  const firstOrder = Math.min(...siblings.map((candidate) => candidate.order));
  const orderById = new Map(reordered.map((candidate, order) => [candidate.id, firstOrder + order]));
  return {
    ...document,
    nodes: document.nodes.map((candidate) => {
      const order = orderById.get(candidate.id);
      return order === undefined ? candidate : { ...candidate, order };
    })
  };
}

export function setDiagramTreeParent(document: DiagramDocument, nodeId: DiagramNodeId, parentId: DiagramNodeId): DiagramDocument {
  const node = document.nodes.find((candidate) => candidate.id === nodeId);
  const parent = document.nodes.find((candidate) => candidate.id === parentId);
  if (!node || !parent || node.id === parent.id || node.parentId === parent.id || !sameDiagramRelationshipScope(node, parent) || collectSubtreeNodeIds(document, node.id).has(parent.id)) {
    return document;
  }
  const resolved = resolveDiagramLayout(document).nodesById;
  const targetResolved = resolved[node.id];
  const parentResolved = resolved[parent.id];
  const order = Math.max(node.order, nextDiagramChildOrder(document, parent.id));
  const edge: DiagramEdge = {
    id: `tree:${parent.id}->${node.id}`,
    source: parent.id,
    target: node.id,
    kind: "tree"
  };
  return {
    ...document,
    nodes: document.nodes.map((candidate) =>
      candidate.id === node.id
        ? reparentDiagramNode(candidate, parent.id, order, targetResolved, parentResolved)
        : candidate
    ),
    edges: [...document.edges.filter((candidate) => candidate.kind !== "tree" || candidate.target !== node.id), edge]
  };
}

export function clearDiagramTreeParent(document: DiagramDocument, nodeId: DiagramNodeId): DiagramDocument {
  const node = document.nodes.find((candidate) => candidate.id === nodeId);
  if (!node?.parentId) {
    return document;
  }
  const resolved = resolveDiagramLayout(document).nodesById;
  const order = Math.max(node.order, nextDiagramRootOrder(document));
  return {
    ...document,
    nodes: document.nodes.map((candidate) => {
      if (candidate.id !== node.id) {
        return candidate;
      }
      const next = { ...candidate };
      delete next.parentId;
      next.order = order;
      return next.mode === "absolute" ? next : pinDiagramNode(next, resolved[node.id]);
    }),
    edges: document.edges.filter((candidate) => candidate.kind !== "tree" || candidate.target !== node.id)
  };
}

export function setDiagramDependencyEdge(document: DiagramDocument, sourceId: DiagramNodeId, targetId: DiagramNodeId, enabled: boolean): DiagramDocument {
  return setDiagramTypedEdge(document, "dependency", sourceId, targetId, enabled);
}

export function setDiagramPathEdge(document: DiagramDocument, sourceId: DiagramNodeId, targetId: DiagramNodeId, enabled: boolean): DiagramDocument {
  return setDiagramTypedEdge(document, "path", sourceId, targetId, enabled);
}

export function diagramDependencyCycleEdge(document: DiagramDocument): DiagramEdge | null {
  const partial: DiagramDocument = {
    ...document,
    edges: []
  };
  for (const edge of document.edges) {
    if (edge.kind !== "dependency") {
      partial.edges.push(edge);
      continue;
    }
    if (hasDiagramDependencyPath(partial, edge.target, edge.source)) {
      return edge;
    }
    partial.edges.push(edge);
  }
  return null;
}

export function diagramTreeEdgeParentMismatch(document: DiagramDocument): { edge: DiagramEdge; parentId: DiagramNode["parentId"] } | null {
  const parentById = new Map(document.nodes.map((node) => [node.id, node.parentId]));
  for (const edge of document.edges) {
    if (edge.kind !== "tree") {
      continue;
    }
    const parentId = parentById.get(edge.target) ?? null;
    if (parentKey(parentId) !== edge.source) {
      return { edge, parentId };
    }
  }
  return null;
}

export function diagramNodeMissingTreeEdge(document: DiagramDocument): DiagramNode | null {
  const treeEdgeKeys = new Set(document.edges.filter((edge) => edge.kind === "tree").map((edge) => `${edge.source}\0${edge.target}`));
  return document.nodes.find((node) => Boolean(node.parentId) && !treeEdgeKeys.has(`${node.parentId}\0${node.id}`)) ?? null;
}

export function setDiagramReferenceEdge(document: DiagramDocument, sourceId: DiagramNodeId, targetId: DiagramNodeId, enabled: boolean): DiagramDocument {
  return setDiagramTypedEdge(document, "reference", sourceId, targetId, enabled);
}

function setDiagramTypedEdge(document: DiagramDocument, kind: "dependency" | "path" | "reference", sourceId: DiagramNodeId, targetId: DiagramNodeId, enabled: boolean): DiagramDocument {
  const source = sourceId.trim();
  const target = targetId.trim();
  const sourceNode = document.nodes.find((node) => node.id === source);
  const targetNode = document.nodes.find((node) => node.id === target);
  if (!source || !target || source === target || !sourceNode || !targetNode) {
    return document;
  }
  const hasEdge = document.edges.some((edge) => edge.kind === kind && edge.source === source && edge.target === target);
  if (enabled) {
    if (hasEdge) {
      return document;
    }
    if (!sameDiagramRelationshipScope(sourceNode, targetNode)) {
      return document;
    }
    if (kind === "dependency" && hasDiagramDependencyPath(document, target, source)) {
      return document;
    }
    return {
      ...document,
      edges: [...document.edges, { id: `${kind}:${source}->${target}`, source, target, kind }]
    };
  }
  if (!hasEdge) {
    return document;
  }
  return {
    ...document,
    edges: document.edges.filter((edge) => edge.kind !== kind || edge.source !== source || edge.target !== target)
  };
}

function sameDiagramRelationshipScope(left: DiagramNode, right: DiagramNode): boolean {
  return diagramNodeRelationshipScopeKey(left) === diagramNodeRelationshipScopeKey(right);
}

function isProtectedSourceBackedNode(node: DiagramNode): boolean {
  if (!node.payload || typeof node.payload !== "object" || Array.isArray(node.payload)) {
    return false;
  }
  const payload = node.payload as { embeddedKind?: unknown; itemId?: unknown; objectId?: unknown };
  return payload.embeddedKind !== "focus" && typeof payload.itemId === "string" && typeof payload.objectId === "string";
}

function isEmbeddedFocusNode(node: DiagramNode): boolean {
  if (!node.payload || typeof node.payload !== "object" || Array.isArray(node.payload)) {
    return false;
  }
  return (node.payload as { embeddedKind?: unknown }).embeddedKind === "focus";
}

function hasDiagramDependencyPath(document: DiagramDocument, sourceId: DiagramNodeId, targetId: DiagramNodeId): boolean {
  const targetsBySource = new Map<DiagramNodeId, DiagramNodeId[]>();
  for (const edge of document.edges) {
    if (edge.kind !== "dependency") {
      continue;
    }
    targetsBySource.set(edge.source, [...(targetsBySource.get(edge.source) ?? []), edge.target]);
  }

  const visited = new Set<DiagramNodeId>();
  const pending = [sourceId];
  while (pending.length > 0) {
    const id = pending.pop();
    if (!id || visited.has(id)) {
      continue;
    }
    if (id === targetId) {
      return true;
    }
    visited.add(id);
    pending.push(...(targetsBySource.get(id) ?? []));
  }
  return false;
}

export function moveDiagramNodeKeepingDescendants(document: DiagramDocument, nodeId: DiagramNodeId, delta: DiagramMoveDelta): DiagramDocument {
  const node = document.nodes.find((candidate) => candidate.id === nodeId);
  if (!node) {
    return document;
  }
  const targetIds = collectSubtreeNodeIds(document, nodeId);
  const resolved = resolveDiagramLayout(document).nodesById;
  const nextWorldPositions = new Map<DiagramNodeId, CanvasPoint>();
  nextWorldPositions.set(nodeId, {
    x: resolved[nodeId].worldX + delta.dx,
    y: resolved[nodeId].worldY + delta.dy
  });
  for (const candidate of document.nodes) {
    if (candidate.id !== nodeId && targetIds.has(candidate.id)) {
      nextWorldPositions.set(candidate.id, {
        x: resolved[candidate.id].worldX,
        y: resolved[candidate.id].worldY
      });
    }
  }
  return {
    ...document,
    nodes: document.nodes.map((candidate) => {
      const nextWorld = nextWorldPositions.get(candidate.id);
      if (!nextWorld) {
        return candidate;
      }
      if (candidate.id === nodeId) {
        return moveSingleDiagramNode(candidate, delta, {
          worldX: nextWorld.x,
          worldY: nextWorld.y
        });
      }
      if (candidate.mode !== "relative") {
        return pinDiagramNode(candidate, {
          worldX: nextWorld.x,
          worldY: nextWorld.y
        });
      }
      const parentId = candidate.parentId;
      const resolvedParent = parentId ? resolved[parentId] : undefined;
      const parentWorld =
        parentId && resolvedParent
          ? nextWorldPositions.get(parentId) ?? {
              x: resolvedParent.worldX,
              y: resolvedParent.worldY
            }
          : undefined;
      if (!parentWorld) {
        return pinDiagramNode(candidate, {
          worldX: nextWorld.x,
          worldY: nextWorld.y
        });
      }
      const rest = { ...candidate };
      delete rest.fixed;
      delete rest.x;
      delete rest.y;
      return {
        ...rest,
        mode: "relative",
        dx: snapGrid(nextWorld.x - parentWorld.x),
        dy: snapGrid(nextWorld.y - parentWorld.y)
      };
    })
  };
}

export function moveDiagramNodeRelayoutDescendants(document: DiagramDocument, nodeId: DiagramNodeId, delta: DiagramMoveDelta): DiagramDocument {
  if (!document.nodes.some((node) => node.id === nodeId)) {
    return document;
  }
  const moved = delta.dx === 0 && delta.dy === 0 ? document : moveDiagramNode(document, nodeId, delta);
  return autoLayoutDiagramDescendants(moved, nodeId);
}

export function pinDiagramDocument(document: DiagramDocument): DiagramDocument {
  const resolved = resolveDiagramLayout(document).nodesById;
  const nodes = document.nodes.map((node) => pinDiagramNode(node, resolved[node.id]));
  if (sameDiagramNodes(document.nodes, nodes)) {
    return document;
  }
  return {
    ...document,
    nodes
  };
}

export function pinDiagramSelectedNode(document: DiagramDocument, nodeId: DiagramNodeId): DiagramDocument {
  const target = document.nodes.find((node) => node.id === nodeId);
  if (!target) {
    return document;
  }
  const resolved = resolveDiagramLayout(document).nodesById;
  const pinned = pinDiagramNode(target, resolved[target.id]);
  if (sameDiagramNode(target, pinned)) {
    return document;
  }
  return {
    ...document,
    nodes: document.nodes.map((node) => (node.id === nodeId ? pinned : node))
  };
}

export function makeDiagramSelectedNodeRelative(document: DiagramDocument, nodeId: DiagramNodeId): DiagramDocument {
  const target = document.nodes.find((node) => node.id === nodeId);
  if (!target?.parentId) {
    return document;
  }
  const resolved = resolveDiagramLayout(document).nodesById;
  const targetNode = resolved[target.id];
  const parentNode = resolved[target.parentId];
  if (!targetNode || !parentNode) {
    return document;
  }
  const relative = relativeDiagramNode(target, targetNode, parentNode);
  if (sameDiagramNode(target, relative)) {
    return document;
  }
  return {
    ...document,
    nodes: document.nodes.map((node) => (node.id === nodeId ? relative : node))
  };
}

export function makeDiagramSubtreeRelative(document: DiagramDocument, nodeId: DiagramNodeId): DiagramDocument {
  if (!document.nodes.some((node) => node.id === nodeId)) {
    return document;
  }
  const targetIds = collectSubtreeNodeIds(document, nodeId);
  const resolved = resolveDiagramLayout(document).nodesById;
  const nodes = document.nodes.map((node) => {
    if (!targetIds.has(node.id) || !node.parentId || node.mode === "relative") {
      return node;
    }
    const nodeResolved = resolved[node.id];
    const parentResolved = resolved[node.parentId];
    return nodeResolved && parentResolved ? relativeDiagramNode(node, nodeResolved, parentResolved) : node;
  });
  if (sameDiagramNodes(document.nodes, nodes)) {
    return document;
  }
  return {
    ...document,
    nodes
  };
}

export function pinDiagramSubtree(document: DiagramDocument, nodeId: DiagramNodeId): DiagramDocument {
  if (!document.nodes.some((node) => node.id === nodeId)) {
    return document;
  }
  const targetIds = collectSubtreeNodeIds(document, nodeId);
  const resolved = resolveDiagramLayout(document).nodesById;
  const nodes = document.nodes.map((node) => (targetIds.has(node.id) ? pinDiagramNode(node, resolved[node.id]) : node));
  if (sameDiagramNodes(document.nodes, nodes)) {
    return document;
  }
  return {
    ...document,
    nodes
  };
}

export function autoLayoutDiagramNode(document: DiagramDocument, nodeId: DiagramNodeId): DiagramDocument {
  const target = document.nodes.find((node) => node.id === nodeId);
  if (!target) {
    return document;
  }
  const nextNode = autoLayoutNode(target);
  if (sameDiagramNode(target, nextNode)) {
    return document;
  }
  return {
    ...document,
    nodes: document.nodes.map((node) => (node.id === nodeId ? nextNode : node))
  };
}

export function autoLayoutDiagramSubtree(document: DiagramDocument, nodeId: DiagramNodeId): DiagramDocument {
  if (!document.nodes.some((node) => node.id === nodeId)) {
    return document;
  }
  const targetIds = collectSubtreeNodeIds(document, nodeId);
  const nodes = document.nodes.map((node) => (targetIds.has(node.id) ? autoLayoutNode(node) : node));
  if (sameDiagramNodes(document.nodes, nodes)) {
    return document;
  }
  return {
    ...document,
    nodes
  };
}

export function autoLayoutDiagramDescendants(document: DiagramDocument, nodeId: DiagramNodeId): DiagramDocument {
  if (!document.nodes.some((node) => node.id === nodeId)) {
    return document;
  }
  const targetIds = collectSubtreeNodeIds(document, nodeId);
  targetIds.delete(nodeId);
  const nodes = document.nodes.map((node) => (targetIds.has(node.id) ? autoLayoutNode(node) : node));
  if (sameDiagramNodes(document.nodes, nodes)) {
    return document;
  }
  return {
    ...document,
    nodes
  };
}

export function autoLayoutDiagramDocument(document: DiagramDocument): DiagramDocument {
  const nodes = document.nodes.map(autoLayoutNode);
  if (sameDiagramNodes(document.nodes, nodes)) {
    return document;
  }
  return {
    ...document,
    nodes
  };
}

export function unpinDiagramDocument(document: DiagramDocument): DiagramDocument {
  return autoLayoutDiagramDocument(document);
}

export function unpinDiagramSelectedNode(document: DiagramDocument, nodeId: DiagramNodeId): DiagramDocument {
  return autoLayoutDiagramNode(document, nodeId);
}

export function unpinDiagramSubtree(document: DiagramDocument, nodeId: DiagramNodeId): DiagramDocument {
  return autoLayoutDiagramSubtree(document, nodeId);
}

export function dragDeltaToGrid(start: CanvasPoint, end: CanvasPoint, gridSizePx: number): DiagramMoveDelta {
  return {
    dx: snapGrid((end.x - start.x) / gridSizePx),
    dy: snapGrid((end.y - start.y) / gridSizePx)
  };
}

export function toCanvasPoint(node: Pick<ResolvedDiagramNode, "worldX" | "worldY">, gridSizePx: number): CanvasPoint {
  return {
    x: snapGrid(node.worldX) * gridSizePx,
    y: snapGrid(node.worldY) * gridSizePx
  };
}

export function snapGrid(value: number): number {
  const snapped = value < 0 ? -Math.round(Math.abs(value)) : Math.round(value);
  return Object.is(snapped, -0) ? 0 : snapped;
}

function snapViewportNumber(value: number): number {
  const snapped = Math.round(value * 1000) / 1000;
  return Object.is(snapped, -0) ? 0 : snapped;
}

function moveSingleDiagramNode(node: DiagramNode, delta: DiagramMoveDelta, resolved: Pick<ResolvedDiagramNode, "worldX" | "worldY">): DiagramNode {
  if (node.mode === "auto" && node.relativePositionKind === "legacy_offset") {
    const rest = { ...node };
    delete rest.fixed;
    delete rest.x;
    delete rest.y;
    return {
      ...rest,
      mode: "auto",
      dx: snapGrid((node.dx ?? 0) + delta.dx),
      dy: snapGrid((node.dy ?? 0) + delta.dy),
      relativePositionKind: "legacy_offset"
    };
  }
  if (node.mode !== "relative") {
    return pinDiagramNode(node, resolved);
  }
  requireNumber(node.dx, `Relative node ${node.id} is missing dx.`);
  requireNumber(node.dy, `Relative node ${node.id} is missing dy.`);
  const rest = { ...node };
  delete rest.fixed;
  delete rest.x;
  delete rest.y;
  return {
    ...rest,
    mode: "relative",
    dx: snapGrid(node.dx + delta.dx),
    dy: snapGrid(node.dy + delta.dy)
  };
}

function relativeDiagramNode(node: DiagramNode, resolved: Pick<ResolvedDiagramNode, "worldX" | "worldY">, parent: Pick<ResolvedDiagramNode, "worldX" | "worldY">): DiagramNode {
  const rest = { ...node };
  delete rest.fixed;
  delete rest.x;
  delete rest.y;
  return {
    ...rest,
    mode: "relative",
    ...(node.relativePositionKind === "legacy_offset" ? { relativePositionKind: "legacy_offset" as const } : {}),
    dx: snapGrid(resolved.worldX - parent.worldX),
    dy: snapGrid(resolved.worldY - parent.worldY)
  };
}

function reparentDiagramNode(node: DiagramNode, parentId: DiagramNodeId, order: number, resolved: Pick<ResolvedDiagramNode, "worldX" | "worldY">, parent: Pick<ResolvedDiagramNode, "worldX" | "worldY">): DiagramNode {
  const reparented = {
    ...node,
    order,
    parentId
  };
  return node.mode === "absolute" ? reparented : relativeDiagramNode(reparented, resolved, parent);
}

function autoLayoutNode(node: DiagramNode): DiagramNode {
  const rest = { ...node };
  delete rest.dx;
  delete rest.dy;
  delete rest.relativePositionKind;
  delete rest.fixed;
  delete rest.x;
  delete rest.y;
  return {
    ...rest,
    mode: "auto"
  };
}

function applyDiagramNodeLayoutHints(node: DiagramNode, hints: DiagramNodeLayoutHints): DiagramNode {
  const next = { ...node };
  setOptionalDiagramNumber(next, "priority", hints.priority);
  setOptionalDiagramNumber(next, "subtreeWidth", positiveDiagramNumber(hints.subtreeWidth));
  setOptionalDiagramNumber(next, "subtreeWidthDelta", hints.subtreeWidthDelta);
  setOptionalDiagramNumber(next, "subtreeCenterOffset", hints.subtreeCenterOffset);
  return next;
}

function setOptionalDiagramNumber(node: DiagramNode, key: keyof DiagramNodeLayoutHints, value: number | undefined): void {
  if (typeof value === "number" && Number.isFinite(value)) {
    node[key] = snapGrid(value);
    return;
  }
  delete node[key];
}

function positiveDiagramNumber(value: number | undefined): number | undefined {
  return typeof value === "number" && Number.isFinite(value) && value > 0 ? value : undefined;
}

function sameDiagramNode(left: DiagramNode, right: DiagramNode): boolean {
  const leftRecord = left as Record<string, unknown>;
  const rightRecord = right as Record<string, unknown>;
  const leftKeys = Object.keys(leftRecord);
  const rightKeys = Object.keys(rightRecord);
  return leftKeys.length === rightKeys.length && leftKeys.every((key) => Object.is(leftRecord[key], rightRecord[key]));
}

function sameDiagramNodes(left: DiagramNode[], right: DiagramNode[]): boolean {
  return left.length === right.length && left.every((node, index) => sameDiagramNode(node, right[index]));
}

function resolvePoint(node: DiagramNode, parent: ParentContext | undefined, options: DiagramLayoutOptions): CanvasPoint {
  if (node.mode === "absolute") {
    requireNumber(node.x, `Absolute node ${node.id} is missing x.`);
    requireNumber(node.y, `Absolute node ${node.id} is missing y.`);
    return { x: snapGrid(node.x), y: snapGrid(node.y) };
  }

  if (node.mode === "relative") {
    if (!parent || parent.node.id === "__diagram_root__") {
      throw new Error(`Relative node ${node.id} requires a parent.`);
    }
    requireNumber(node.dx, `Relative node ${node.id} is missing dx.`);
    requireNumber(node.dy, `Relative node ${node.id} is missing dy.`);
    return {
      x: snapGrid(parent.node.worldX + node.dx),
      y: snapGrid(parent.node.worldY + node.dy)
    };
  }

  if (parent?.autoSlot) {
    return {
      x: snapGrid(parent.autoSlot.x),
      y: snapGrid(parent.autoSlot.y)
    };
  }

  return {
    x: snapGrid(options.rootX ?? DEFAULT_ROOT_X),
    y: snapGrid(options.rootY ?? DEFAULT_ROOT_Y)
  };
}

function autoChildSlots(
  parent: ResolvedDiagramNode,
  children: DiagramNode[],
  options: DiagramLayoutOptions,
  slotWidthFor: (node: DiagramNode) => number
): Map<DiagramNodeId, CanvasPoint> {
  const autoChildren = children.filter((child) => child.mode === "auto");
  const slots = new Map<DiagramNodeId, CanvasPoint>();
  if (autoChildren.length === 0) {
    return slots;
  }

  const sourceFocusSlots = options.sourceFocusSlots === true;
  const siblingGap = sourceFocusSlots ? 0 : gap(options.siblingGap, DEFAULT_SIBLING_GAP);
  const layerGap = gap(options.layerGap, DEFAULT_LAYER_GAP);
  const widths = autoChildren.map(slotWidthFor);
  const totalWidth = widths.reduce((sum, width) => sum + width, 0) + siblingGap * (autoChildren.length - 1);
  let cursorX = sourceFocusSlots
    ? parent.worldX - Math.floor(slotWidthFor(parent) / 2) - Math.floor(snapGrid(parent.subtreeWidthDelta ?? 0) / 2) + snapGrid(parent.subtreeCenterOffset ?? 0)
    : snapGrid(parent.worldX + snapGrid(parent.width) / 2 - totalWidth / 2 + snapGrid(parent.subtreeCenterOffset ?? 0));
  const childY = snapGrid(parent.worldY + snapGrid(parent.height) + layerGap);
  const occupiedRects = manualChildRects(parent, children);

  autoChildren.forEach((child, index) => {
    const childWidth = snapGrid(child.width);
    const childHeight = snapGrid(child.height);
    const y = snapGrid(childY + snapGrid(child.dy ?? 0));
    const x = shiftRectPastOccupied(
      {
        x: sourceFocusSlots ? snapGrid(cursorX + Math.floor(widths[index] / 2) + snapGrid(child.dx ?? 0)) : snapGrid(cursorX + (widths[index] - childWidth) / 2 + snapGrid(child.dx ?? 0)),
        y,
        width: childWidth,
        height: childHeight
      },
      occupiedRects,
      siblingGap
    );
    slots.set(child.id, {
      x,
      y
    });
    cursorX = sourceFocusSlots ? cursorX + widths[index] + siblingGap : snapGrid(cursorX + widths[index] + siblingGap);
  });

  return slots;
}

function manualChildRects(parent: ResolvedDiagramNode, children: DiagramNode[]): DiagramRect[] {
  return children.flatMap((child): DiagramRect[] => {
    if (child.mode === "auto") {
      return [];
    }
    if (child.mode === "absolute") {
      requireNumber(child.x, `Absolute node ${child.id} is missing x.`);
      requireNumber(child.y, `Absolute node ${child.id} is missing y.`);
      return [
        {
          x: snapGrid(child.x),
          y: snapGrid(child.y),
          width: snapGrid(child.width),
          height: snapGrid(child.height)
        }
      ];
    }
    requireNumber(child.dx, `Relative node ${child.id} is missing dx.`);
    requireNumber(child.dy, `Relative node ${child.id} is missing dy.`);
    return [
      {
        x: snapGrid(parent.worldX + child.dx),
        y: snapGrid(parent.worldY + child.dy),
        width: snapGrid(child.width),
        height: snapGrid(child.height)
      }
    ];
  });
}

function shiftRectPastOccupied(rect: DiagramRect, occupiedRects: DiagramRect[], gapSize: number): number {
  let x = rect.x;
  let shifted = true;
  while (shifted) {
    shifted = false;
    for (const occupied of occupiedRects) {
      const candidate = { ...rect, x };
      if (!rectsOverlap(candidate, occupied, gapSize)) {
        continue;
      }
      x = snapGrid(occupied.x + occupied.width + gapSize);
      shifted = true;
      break;
    }
  }
  return x;
}

function rectsOverlap(left: DiagramRect, right: DiagramRect, gapSize: number): boolean {
  const verticalOverlap = left.y < right.y + right.height && left.y + left.height > right.y;
  const horizontalOverlap = left.x < right.x + right.width + gapSize && left.x + left.width + gapSize > right.x;
  return verticalOverlap && horizontalOverlap;
}

function makeSlotWidthResolver(childrenByParent: Map<DiagramNodeId, DiagramNode[]>, options: DiagramLayoutOptions): (node: DiagramNode) => number {
  const cache = new Map<DiagramNodeId, number>();
  const visiting = new Set<DiagramNodeId>();
  const siblingGap = options.sourceFocusSlots === true ? 0 : gap(options.siblingGap, DEFAULT_SIBLING_GAP);

  const slotWidthFor = (node: DiagramNode): number => {
    const cached = cache.get(node.id);
    if (cached !== undefined) {
      return cached;
    }
    if (visiting.has(node.id)) {
      return snapGrid(node.width);
    }
    visiting.add(node.id);

    const childWidths = (childrenByParent.get(node.id) ?? [])
      .filter((child) => child.mode === "auto")
      .map(slotWidthFor);
    const childBandWidth =
      childWidths.length === 0 ? 0 : childWidths.reduce((sum, width) => sum + width, 0) + siblingGap * (childWidths.length - 1);
    const hintedWidth = node.subtreeWidth !== undefined ? snapGrid(node.subtreeWidth) : childBandWidth + snapGrid(node.subtreeWidthDelta ?? 0);
    const width = Math.max(snapGrid(node.width), hintedWidth);

    visiting.delete(node.id);
    cache.set(node.id, width);
    return width;
  };

  return slotWidthFor;
}

function groupChildren(nodes: DiagramNode[]): Map<DiagramNodeId, DiagramNode[]> {
  const childrenByParent = new Map<DiagramNodeId, DiagramNode[]>();
  for (const node of nodes) {
    if (!node.parentId) {
      continue;
    }
    const siblings = childrenByParent.get(node.parentId) ?? [];
    siblings.push(node);
    childrenByParent.set(node.parentId, siblings);
  }
  for (const [parentId, children] of childrenByParent) {
    childrenByParent.set(parentId, sortNodes(children));
  }
  return childrenByParent;
}

function collectSubtreeNodeIds(document: DiagramDocument, rootId: DiagramNodeId): Set<DiagramNodeId> {
  const childrenByParent = groupChildren(document.nodes);
  const ids = new Set<DiagramNodeId>();
  const pending = [rootId];
  while (pending.length > 0) {
    const id = pending.pop();
    if (!id || ids.has(id)) {
      continue;
    }
    ids.add(id);
    for (const child of childrenByParent.get(id) ?? []) {
      pending.push(child.id);
    }
  }
  return ids;
}

function nextDiagramChildOrder(document: DiagramDocument, parentId: DiagramNodeId): number {
  const siblings = document.nodes.filter((node) => parentKey(node.parentId) === parentKey(parentId));
  return siblings.length === 0 ? 0 : Math.max(...siblings.map((node) => node.order)) + 1;
}

function nextDiagramRootOrder(document: DiagramDocument): number {
  const roots = document.nodes.filter((node) => !node.parentId);
  return roots.length === 0 ? 0 : Math.max(...roots.map((node) => node.order)) + 1;
}

function appendSafeDiagramOrder(order: number | undefined, nextOrder: number): number {
  return typeof order === "number" && Number.isFinite(order) ? Math.max(order, nextOrder) : nextOrder;
}

function sortNodes(nodes: DiagramNode[]): DiagramNode[] {
  return [...nodes].sort((left, right) => priorityValue(right) - priorityValue(left) || left.order - right.order || left.id.localeCompare(right.id));
}

function priorityValue(node: DiagramNode): number {
  return typeof node.priority === "number" && Number.isFinite(node.priority) ? node.priority : 0;
}

function parentKey(parentId: DiagramNode["parentId"]): string {
  return parentId ?? "";
}

function mergeBounds(left: DiagramBounds, right: DiagramBounds): DiagramBounds {
  return {
    minX: Math.min(left.minX, right.minX),
    minY: Math.min(left.minY, right.minY),
    maxX: Math.max(left.maxX, right.maxX),
    maxY: Math.max(left.maxY, right.maxY)
  };
}

function requireNumber(value: number | undefined, message: string): asserts value is number {
  if (typeof value !== "number" || Number.isNaN(value)) {
    throw new Error(message);
  }
}

function gap(value: number | undefined, fallback: number): number {
  return snapGrid(value ?? fallback);
}

function placeholderRoot(): ResolvedDiagramNode {
  return {
    id: "__diagram_root__",
    order: 0,
    mode: "absolute",
    x: 0,
    y: 0,
    width: 0,
    height: 0,
    worldX: 0,
    worldY: 0,
    subtreeBounds: { minX: 0, minY: 0, maxX: 0, maxY: 0 }
  };
}
