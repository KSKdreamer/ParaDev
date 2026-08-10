import type { ProjectDiagramRelationship } from "../types";
import { diagramNodeRelationshipScopeKey } from "./diagramScope";
import type { DiagramDocument, DiagramEdge } from "./layoutModel";

export type DiagramRelationshipEndpoints = {
  sourceId: string;
  targetId: string;
};

export function diagramRelationshipEndpoints(
  relationship: ProjectDiagramRelationship,
  selectedNodeId: string,
  relatedNodeId: string,
): DiagramRelationshipEndpoints {
  const endpoints =
    relationship.selected_endpoint === "target"
      ? { sourceId: relatedNodeId, targetId: selectedNodeId }
      : { sourceId: selectedNodeId, targetId: relatedNodeId };
  if (
    relationship.symmetric &&
    endpoints.targetId.localeCompare(endpoints.sourceId) < 0
  ) {
    return {
      sourceId: endpoints.targetId,
      targetId: endpoints.sourceId,
    };
  }
  return endpoints;
}

export function diagramRelationshipRelatedNodeIds(
  document: DiagramDocument,
  relationship: ProjectDiagramRelationship,
  selectedNodeId: string,
): string[] {
  return [
    ...new Set(
      document.edges
        .filter((edge) =>
          diagramEdgeMatchesSelectedRelationship(
            edge,
            relationship,
            selectedNodeId,
          ),
        )
        .map((edge) =>
          edge.source === selectedNodeId ? edge.target : edge.source,
        ),
    ),
  ].sort();
}

export function diagramRelationshipCycleCandidateIds(
  document: DiagramDocument,
  relationship: ProjectDiagramRelationship,
  selectedNodeId: string,
): string[] {
  if (relationship.symmetric || relationship.visual_kind === "reference") {
    return [];
  }
  const adjacency = new Map<string, string[]>();
  for (const edge of document.edges) {
    if (!diagramEdgeMatchesKind(edge, relationship)) {
      continue;
    }
    const from =
      relationship.selected_endpoint === "target" ? edge.source : edge.target;
    const to =
      relationship.selected_endpoint === "target" ? edge.target : edge.source;
    adjacency.set(from, [...(adjacency.get(from) ?? []), to]);
  }
  const blocked: string[] = [];
  const pending = [...(adjacency.get(selectedNodeId) ?? [])];
  const seen = new Set<string>();
  while (pending.length > 0) {
    const nodeId = pending.pop();
    if (!nodeId || seen.has(nodeId)) {
      continue;
    }
    seen.add(nodeId);
    blocked.push(nodeId);
    pending.push(...(adjacency.get(nodeId) ?? []));
  }
  return blocked;
}

export function setDiagramRelationship(
  document: DiagramDocument,
  relationship: ProjectDiagramRelationship,
  selectedNodeId: string,
  relatedNodeId: string,
  present: boolean,
  payload?: unknown,
): DiagramDocument {
  if (!selectedNodeId || !relatedNodeId || selectedNodeId === relatedNodeId) {
    return document;
  }
  const selectedNode = document.nodes.find(
    (node) => node.id === selectedNodeId,
  );
  const relatedNode = document.nodes.find((node) => node.id === relatedNodeId);
  if (
    !selectedNode ||
    !relatedNode ||
    diagramNodeRelationshipScopeKey(selectedNode) !==
      diagramNodeRelationshipScopeKey(relatedNode)
  ) {
    return document;
  }
  const endpoints = diagramRelationshipEndpoints(
    relationship,
    selectedNodeId,
    relatedNodeId,
  );
  const exactEdges = document.edges.filter((edge) =>
    diagramEdgeMatchesEndpoints(edge, relationship, endpoints),
  );
  let nextEdges = document.edges;
  if (!present) {
    if (exactEdges.length === 0) {
      return document;
    }
    const removedIds = new Set(exactEdges.map((edge) => edge.id));
    nextEdges = document.edges.filter((edge) => !removedIds.has(edge.id));
  } else {
    if (relationship.cardinality === "one") {
      nextEdges = nextEdges.filter(
        (edge) =>
          !diagramEdgeMatchesSelectedRelationship(
            edge,
            relationship,
            selectedNodeId,
          ) || diagramEdgeMatchesEndpoints(edge, relationship, endpoints),
      );
    }
    if (
      !nextEdges.some((edge) =>
        diagramEdgeMatchesEndpoints(edge, relationship, endpoints),
      )
    ) {
      nextEdges = [
        ...nextEdges,
        {
          id: `${relationship.kind}:${endpoints.sourceId}->${endpoints.targetId}`,
          kind: relationship.visual_kind,
          label: relationship.label,
          relationshipKind: relationship.kind,
          source: endpoints.sourceId,
          target: endpoints.targetId,
          ...(payload === undefined ? {} : { payload }),
        },
      ];
    }
  }
  return nextEdges === document.edges || sameEdgeIds(nextEdges, document.edges)
    ? document
    : { ...document, edges: nextEdges };
}

function diagramEdgeMatchesSelectedRelationship(
  edge: DiagramEdge,
  relationship: ProjectDiagramRelationship,
  selectedNodeId: string,
): boolean {
  if (!diagramEdgeMatchesKind(edge, relationship)) {
    return false;
  }
  if (relationship.symmetric) {
    return edge.source === selectedNodeId || edge.target === selectedNodeId;
  }
  return relationship.selected_endpoint === "target"
    ? edge.target === selectedNodeId
    : edge.source === selectedNodeId;
}

function diagramEdgeMatchesEndpoints(
  edge: DiagramEdge,
  relationship: ProjectDiagramRelationship,
  endpoints: DiagramRelationshipEndpoints,
): boolean {
  if (!diagramEdgeMatchesKind(edge, relationship)) {
    return false;
  }
  return relationship.symmetric
    ? (edge.source === endpoints.sourceId &&
        edge.target === endpoints.targetId) ||
        (edge.source === endpoints.targetId &&
          edge.target === endpoints.sourceId)
    : edge.source === endpoints.sourceId && edge.target === endpoints.targetId;
}

function diagramEdgeMatchesKind(
  edge: DiagramEdge,
  relationship: ProjectDiagramRelationship,
): boolean {
  return edge.relationshipKind
    ? edge.relationshipKind === relationship.kind
    : edge.kind === relationship.visual_kind;
}

function sameEdgeIds(left: DiagramEdge[], right: DiagramEdge[]): boolean {
  return (
    left.length === right.length &&
    left.every((edge, index) => edge.id === right[index]?.id)
  );
}
