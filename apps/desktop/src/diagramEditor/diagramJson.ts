import { diagramDependencyCycleEdge, diagramNodeMissingTreeEdge, diagramTreeEdgeParentMismatch, resolveDiagramLayout } from "./layoutModel";
import type { TranslationKey, Translator } from "../i18n";
import type { DiagramDocument, DiagramEdge, DiagramEdgeKind, DiagramNode, DiagramPositionMode, DiagramRelativePositionKind } from "./layoutModel";

const DIAGRAM_POSITION_MODES = new Set<DiagramPositionMode>(["absolute", "relative", "auto"]);
const DIAGRAM_RELATIVE_POSITION_KINDS = new Set<DiagramRelativePositionKind>(["legacy_offset", "relative_position_id"]);
const DIAGRAM_EDGE_KINDS = new Set<DiagramEdgeKind>(["tree", "reference", "dependency", "path"]);

export function exportDiagramJson(document: DiagramDocument): string {
  return `${JSON.stringify(document, null, 2)}\n`;
}

export function importDiagramJson(text: string, t?: Translator): DiagramDocument {
  let value: unknown;
  try {
    value = JSON.parse(text);
  } catch {
    throw diagramJsonError(t, "workspace.diagram.importError.invalidJson", "Diagram JSON is not valid JSON.");
  }
  const document = asRecord(value, diagramJsonMessage(t, "workspace.diagram.importError.rootObject", "Diagram JSON root must be an object."));
  if (document.schemaVersion !== 1) {
    throw diagramJsonError(t, "workspace.diagram.importError.schemaVersion", "Diagram JSON schemaVersion must be 1.");
  }
  if (!Number.isFinite(document.gridSizePx) || Number(document.gridSizePx) <= 0) {
    throw diagramJsonError(t, "workspace.diagram.importError.gridSizePositive", "Diagram JSON gridSizePx must be a positive number.");
  }
  if (!Array.isArray(document.nodes)) {
    throw diagramJsonError(t, "workspace.diagram.importError.nodesArray", "Diagram JSON nodes must be an array.");
  }
  if (!Array.isArray(document.edges)) {
    throw diagramJsonError(t, "workspace.diagram.importError.edgesArray", "Diagram JSON edges must be an array.");
  }

  const nodes = document.nodes.map((node, index) => parseDiagramNode(node, index, t));
  const nodeIds = new Set(nodes.map((node) => node.id));
  if (nodeIds.size !== nodes.length) {
    throw diagramJsonError(t, "workspace.diagram.importError.nodeIdsUnique", "Diagram JSON nodes must have unique ids.");
  }
  const edges = document.edges.map((edge, index) => parseDiagramEdge(edge, index, nodeIds, t));
  const edgeIds = new Set(edges.map((edge) => edge.id));
  if (edgeIds.size !== edges.length) {
    throw diagramJsonError(t, "workspace.diagram.importError.edgeIdsUnique", "Diagram JSON edges must have unique ids.");
  }
  const edgeKeys = new Set(edges.map((edge) => `${edge.kind}\0${edge.source}\0${edge.target}`));
  if (edgeKeys.size !== edges.length) {
    throw diagramJsonError(t, "workspace.diagram.importError.edgeRelationshipsUnique", "Diagram JSON edges must have unique kind/source/target relationships.");
  }
  const nonCanonicalEdge = edges.find((edge) => edge.id !== canonicalDiagramEdgeId(edge));
  if (nonCanonicalEdge) {
    const canonicalId = canonicalDiagramEdgeId(nonCanonicalEdge);
    throw diagramJsonError(t, "workspace.diagram.importError.edgeCanonicalId", `Diagram edge ${nonCanonicalEdge.id} must use canonical id ${canonicalId}.`, { canonicalId, edgeId: nonCanonicalEdge.id });
  }
  const imported: DiagramDocument = {
    schemaVersion: 1,
    gridSizePx: Number(document.gridSizePx),
    ...(document.layoutOptions !== undefined ? { layoutOptions: parseOptionalLayoutOptions(document.layoutOptions, t) } : {}),
    nodes,
    edges,
    ...(document.viewport !== undefined ? { viewport: parseOptionalViewport(document.viewport, t) } : {})
  };
  resolveDiagramLayout(imported);
  const treeMismatch = diagramTreeEdgeParentMismatch(imported);
  if (treeMismatch) {
    const parentId = treeMismatch.parentId ?? "root";
    throw diagramJsonError(t, "workspace.diagram.importError.treeEdgeParentMismatch", `Diagram tree edge ${treeMismatch.edge.id} disagrees with parent ${parentId} for node ${treeMismatch.edge.target}.`, { edgeId: treeMismatch.edge.id, nodeId: treeMismatch.edge.target, parentId });
  }
  const missingTreeEdgeNode = diagramNodeMissingTreeEdge(imported);
  if (missingTreeEdgeNode?.parentId) {
    throw diagramJsonError(t, "workspace.diagram.importError.nodeMissingTreeEdge", `Diagram node ${missingTreeEdgeNode.id} has parent ${missingTreeEdgeNode.parentId} but no matching tree edge.`, { nodeId: missingTreeEdgeNode.id, parentId: missingTreeEdgeNode.parentId });
  }
  const cyclicEdge = diagramDependencyCycleEdge(imported);
  if (cyclicEdge) {
    throw diagramJsonError(t, "workspace.diagram.importError.dependencyCycle", `Diagram dependency edge ${cyclicEdge.id} creates a cycle.`, { edgeId: cyclicEdge.id });
  }
  return imported;
}

function parseDiagramNode(value: unknown, index: number, t?: Translator): DiagramNode {
  const node = asRecord(value, diagramJsonMessage(t, "workspace.diagram.importError.nodeObject", `Diagram node at index ${index} must be an object.`, { index }));
  const id = stringField(node, "id", diagramJsonMessage(t, "workspace.diagram.importError.nodeId", `Diagram node at index ${index} must have an id.`, { index }));
  const mode = stringField(node, "mode", diagramJsonMessage(t, "workspace.diagram.importError.nodeMode", `Diagram node ${id} must have a mode.`, { nodeId: id }));
  if (!DIAGRAM_POSITION_MODES.has(mode as DiagramPositionMode)) {
    throw diagramJsonError(t, "workspace.diagram.importError.nodeUnsupportedMode", `Diagram node ${id} has unsupported mode ${mode}.`, { mode, nodeId: id });
  }
  const parsed: DiagramNode = {
    id,
    ...(typeof node.parentId === "string" && node.parentId ? { parentId: node.parentId } : {}),
    order: numberField(node, "order", diagramJsonMessage(t, "workspace.diagram.importError.nodeOrderNumeric", `Diagram node ${id} must have a numeric order.`, { nodeId: id })),
    mode: mode as DiagramPositionMode,
    width: positiveNumberField(node, "width", diagramJsonMessage(t, "workspace.diagram.importError.nodeWidthNumeric", `Diagram node ${id} must have a numeric width.`, { nodeId: id }), diagramJsonMessage(t, "workspace.diagram.importError.nodeWidthPositive", `Diagram node ${id} width must be positive.`, { nodeId: id })),
    height: positiveNumberField(node, "height", diagramJsonMessage(t, "workspace.diagram.importError.nodeHeightNumeric", `Diagram node ${id} must have a numeric height.`, { nodeId: id }), diagramJsonMessage(t, "workspace.diagram.importError.nodeHeightPositive", `Diagram node ${id} height must be positive.`, { nodeId: id })),
    ...(typeof node.fixed === "boolean" ? { fixed: node.fixed } : {}),
    ...(typeof node.imageUrl === "string" ? { imageUrl: node.imageUrl } : {}),
    ...(typeof node.title === "string" ? { title: node.title } : {}),
    ...(node.payload !== undefined ? { payload: node.payload } : {})
  };
  if (node.x !== undefined) {
    parsed.x = numberField(node, "x", diagramJsonMessage(t, "workspace.diagram.importError.nodeXNumeric", `Diagram node ${id} x must be numeric.`, { nodeId: id }));
  }
  if (node.y !== undefined) {
    parsed.y = numberField(node, "y", diagramJsonMessage(t, "workspace.diagram.importError.nodeYNumeric", `Diagram node ${id} y must be numeric.`, { nodeId: id }));
  }
  if (node.dx !== undefined) {
    parsed.dx = numberField(node, "dx", diagramJsonMessage(t, "workspace.diagram.importError.nodeDxNumeric", `Diagram node ${id} dx must be numeric.`, { nodeId: id }));
  }
  if (node.dy !== undefined) {
    parsed.dy = numberField(node, "dy", diagramJsonMessage(t, "workspace.diagram.importError.nodeDyNumeric", `Diagram node ${id} dy must be numeric.`, { nodeId: id }));
  }
  if (node.relativePositionKind !== undefined) {
    const relativePositionKind = stringField(node, "relativePositionKind", diagramJsonMessage(t, "workspace.diagram.importError.nodeRelativePositionKindString", `Diagram node ${id} relativePositionKind must be a string.`, { nodeId: id }));
    if (!DIAGRAM_RELATIVE_POSITION_KINDS.has(relativePositionKind as DiagramRelativePositionKind)) {
      throw diagramJsonError(t, "workspace.diagram.importError.nodeUnsupportedRelativePositionKind", `Diagram node ${id} has unsupported relativePositionKind ${relativePositionKind}.`, { kind: relativePositionKind, nodeId: id });
    }
    parsed.relativePositionKind = relativePositionKind as DiagramRelativePositionKind;
  }
  if (node.priority !== undefined) {
    parsed.priority = numberField(node, "priority", diagramJsonMessage(t, "workspace.diagram.importError.nodePriorityNumeric", `Diagram node ${id} priority must be numeric.`, { nodeId: id }));
  }
  if (node.subtreeWidth !== undefined) {
    parsed.subtreeWidth = positiveNumberField(
      node,
      "subtreeWidth",
      diagramJsonMessage(t, "workspace.diagram.importError.nodeSubtreeWidthNumeric", `Diagram node ${id} subtreeWidth must be numeric.`, { nodeId: id }),
      diagramJsonMessage(t, "workspace.diagram.importError.nodeSubtreeWidthPositive", `Diagram node ${id} subtreeWidth must be positive.`, { nodeId: id })
    );
  }
  if (node.subtreeWidthDelta !== undefined) {
    parsed.subtreeWidthDelta = numberField(node, "subtreeWidthDelta", diagramJsonMessage(t, "workspace.diagram.importError.nodeSubtreeWidthDeltaNumeric", `Diagram node ${id} subtreeWidthDelta must be numeric.`, { nodeId: id }));
  }
  if (node.subtreeCenterOffset !== undefined) {
    parsed.subtreeCenterOffset = numberField(node, "subtreeCenterOffset", diagramJsonMessage(t, "workspace.diagram.importError.nodeSubtreeCenterOffsetNumeric", `Diagram node ${id} subtreeCenterOffset must be numeric.`, { nodeId: id }));
  }
  return parsed;
}

function parseDiagramEdge(value: unknown, index: number, nodeIds: Set<string>, t?: Translator): DiagramEdge {
  const edge = asRecord(value, diagramJsonMessage(t, "workspace.diagram.importError.edgeObject", `Diagram edge at index ${index} must be an object.`, { index }));
  const id = stringField(edge, "id", diagramJsonMessage(t, "workspace.diagram.importError.edgeId", `Diagram edge at index ${index} must have an id.`, { index }));
  const source = stringField(edge, "source", diagramJsonMessage(t, "workspace.diagram.importError.edgeSource", `Diagram edge ${id} must have a source.`, { edgeId: id }));
  const target = stringField(edge, "target", diagramJsonMessage(t, "workspace.diagram.importError.edgeTarget", `Diagram edge ${id} must have a target.`, { edgeId: id }));
  const kind = stringField(edge, "kind", diagramJsonMessage(t, "workspace.diagram.importError.edgeKind", `Diagram edge ${id} must have a kind.`, { edgeId: id }));
  if (!DIAGRAM_EDGE_KINDS.has(kind as DiagramEdgeKind)) {
    throw diagramJsonError(t, "workspace.diagram.importError.edgeUnsupportedKind", `Diagram edge ${id} has unsupported kind ${kind}.`, { edgeId: id, kind });
  }
  if (source === target) {
    throw diagramJsonError(t, "workspace.diagram.importError.edgeSelf", `Diagram edge ${id} cannot target itself.`, { edgeId: id });
  }
  if (!nodeIds.has(source)) {
    throw diagramJsonError(t, "workspace.diagram.importError.edgeMissingSource", `Diagram edge ${id} references missing source ${source}.`, { edgeId: id, nodeId: source });
  }
  if (!nodeIds.has(target)) {
    throw diagramJsonError(t, "workspace.diagram.importError.edgeMissingTarget", `Diagram edge ${id} references missing target ${target}.`, { edgeId: id, nodeId: target });
  }
  return {
    id,
    source,
    target,
    kind: kind as DiagramEdgeKind
  };
}

function parseOptionalLayoutOptions(value: unknown, t?: Translator): DiagramDocument["layoutOptions"] {
  const options = asRecord(value, diagramJsonMessage(t, "workspace.diagram.importError.layoutOptionsObject", "Diagram layoutOptions must be an object."));
  return {
    ...optionalNumberOption(options, "rootX", diagramJsonMessage(t, "workspace.diagram.importError.layoutOptionsRootXNumeric", "Diagram layoutOptions rootX must be numeric.")),
    ...optionalNumberOption(options, "rootY", diagramJsonMessage(t, "workspace.diagram.importError.layoutOptionsRootYNumeric", "Diagram layoutOptions rootY must be numeric.")),
    ...optionalNumberOption(options, "siblingGap", diagramJsonMessage(t, "workspace.diagram.importError.layoutOptionsSiblingGapNumeric", "Diagram layoutOptions siblingGap must be numeric.")),
    ...optionalNumberOption(options, "layerGap", diagramJsonMessage(t, "workspace.diagram.importError.layoutOptionsLayerGapNumeric", "Diagram layoutOptions layerGap must be numeric."))
  };
}

function optionalNumberOption(record: Record<string, unknown>, key: string, message: string): Record<string, number> {
  return record[key] === undefined ? {} : { [key]: numberField(record, key, message) };
}

function canonicalDiagramEdgeId(edge: Pick<DiagramEdge, "kind" | "source" | "target">): string {
  return `${edge.kind}:${edge.source}->${edge.target}`;
}

function parseOptionalViewport(value: unknown, t?: Translator): DiagramDocument["viewport"] {
  return parseViewport(asRecord(value, diagramJsonMessage(t, "workspace.diagram.importError.viewportObject", "Diagram viewport must be an object.")), t);
}

function parseViewport(viewport: Record<string, unknown>, t?: Translator): DiagramDocument["viewport"] {
  return {
    x: numberField(viewport, "x", diagramJsonMessage(t, "workspace.diagram.importError.viewportXNumeric", "Diagram viewport x must be numeric.")),
    y: numberField(viewport, "y", diagramJsonMessage(t, "workspace.diagram.importError.viewportYNumeric", "Diagram viewport y must be numeric.")),
    zoom: positiveNumberField(viewport, "zoom", diagramJsonMessage(t, "workspace.diagram.importError.viewportZoomNumeric", "Diagram viewport zoom must be numeric."), diagramJsonMessage(t, "workspace.diagram.importError.viewportZoomPositive", "Diagram viewport zoom must be positive."))
  };
}

function diagramJsonError(t: Translator | undefined, key: TranslationKey, fallback: string, params: Record<string, string | number> = {}): Error {
  return new Error(diagramJsonMessage(t, key, fallback, params));
}

function diagramJsonMessage(t: Translator | undefined, key: TranslationKey, fallback: string, params: Record<string, string | number> = {}): string {
  return t ? t(key, params) : fallback;
}

function asRecord(value: unknown, message: string): Record<string, unknown> {
  if (!isRecord(value)) {
    throw new Error(message);
  }
  return value;
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function stringField(record: Record<string, unknown>, key: string, message: string): string {
  const value = record[key];
  if (typeof value !== "string" || !value) {
    throw new Error(message);
  }
  return value;
}

function numberField(record: Record<string, unknown>, key: string, message: string): number {
  const value = record[key];
  if (!Number.isFinite(value)) {
    throw new Error(message);
  }
  return Number(value);
}

function positiveNumberField(record: Record<string, unknown>, key: string, numericMessage: string, positiveMessage: string): number {
  const value = numberField(record, key, numericMessage);
  if (value <= 0) {
    throw new Error(positiveMessage);
  }
  return value;
}
