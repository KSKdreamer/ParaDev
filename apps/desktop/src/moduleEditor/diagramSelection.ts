import type { DiagramDocument, DiagramNode } from "../diagramEditor/layoutModel";
import type { ProjectDiagramNodePayload } from "../diagramEditor/projectDiagram";
import type { ModuleEntity } from "./model";

type SelectableEntity = Pick<ModuleEntity, "id" | "moduleId" | "objectId">;

export function entityIdForDiagramNode(entities: SelectableEntity[], document: DiagramDocument, nodeId: string): string {
  const node = document.nodes.find((candidate) => candidate.id === nodeId);
  if (!node) {
    return "";
  }
  const candidates = entityCandidatesForDiagramNode(node);
  const entity = entities.find((candidate) => entityMatchesDiagramNodeCandidates(candidate, candidates));
  return entity?.id ?? "";
}

export function diagramNodeIdForEntity(entity: SelectableEntity | null | undefined, document: DiagramDocument | null | undefined, currentNodeId = ""): string {
  if (!entity || !document) {
    return "";
  }
  const currentNode = currentNodeId ? document.nodes.find((node) => node.id === currentNodeId) : undefined;
  if (currentNode && diagramNodeMatchesEntity(currentNode, entity)) {
    return currentNode.id;
  }
  const directNode = document.nodes.find((node) => node.id === entity.objectId || node.id === entity.moduleId);
  if (directNode && diagramNodeMatchesEntity(directNode, entity)) {
    return directNode.id;
  }
  return document.nodes.find((node) => diagramNodeMatchesEntity(node, entity))?.id ?? "";
}

function entityCandidatesForDiagramNode(node: DiagramNode): Set<string> {
  const payload = asProjectDiagramNodePayload(node.payload);
  return new Set(
    [payload?.itemId, payload?.moduleId, payload?.objectId, payload?.embeddedId, node.id]
      .map((candidate) => candidate?.trim() ?? "")
      .filter(Boolean)
  );
}

function diagramNodeMatchesEntity(node: DiagramNode, entity: SelectableEntity): boolean {
  return entityMatchesDiagramNodeCandidates(entity, entityCandidatesForDiagramNode(node));
}

function entityMatchesDiagramNodeCandidates(entity: SelectableEntity, candidates: Set<string>): boolean {
  return candidates.has(entity.id) || candidates.has(entity.objectId) || Boolean(entity.moduleId && candidates.has(entity.moduleId));
}

function asProjectDiagramNodePayload(value: unknown): ProjectDiagramNodePayload | null {
  if (!value || typeof value !== "object" || Array.isArray(value)) {
    return null;
  }
  const payload = value as Partial<ProjectDiagramNodePayload>;
  return typeof payload.itemId === "string" && typeof payload.objectId === "string" ? (payload as ProjectDiagramNodePayload) : null;
}
