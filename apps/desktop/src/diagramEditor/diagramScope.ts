import { canonicalFamilyId } from "../projectModules";
import type { DiagramNode } from "./layoutModel";

export function diagramNodeRelationshipScopeKey(node: Pick<DiagramNode, "payload">): string {
  return diagramPayloadRelationshipScopeKey(node.payload);
}

export function diagramPayloadRelationshipScopeKey(value: unknown): string {
  const payload = diagramPayloadRecord(value);
  if (!payload) {
    return "node:";
  }
  const projectId = stringPayloadValue(payload.projectId);
  if (payload.embeddedKind === "focus") {
    const itemId = stringPayloadValue(payload.itemId) || stringPayloadValue(payload.objectId);
    return `focus:${projectId}:${itemId}`;
  }
  const familyId = diagramPayloadFamilyId(payload);
  return familyId ? `node:${projectId}:${familyId}` : "node:";
}

function diagramPayloadFamilyId(payload: Record<string, unknown>): string {
  const familyId = canonicalFamilyId(stringPayloadValue(payload.familyId), stringPayloadValue(payload.family));
  if (familyId) {
    return familyId;
  }
  const itemId = stringPayloadValue(payload.itemId);
  const familySeparator = itemId.indexOf(":");
  return familySeparator > 0 ? canonicalFamilyId(itemId.slice(0, familySeparator)) : "";
}

function diagramPayloadRecord(value: unknown): Record<string, unknown> | null {
  if (!value || typeof value !== "object" || Array.isArray(value)) {
    return null;
  }
  return value as Record<string, unknown>;
}

function stringPayloadValue(value: unknown): string {
  return typeof value === "string" ? value.trim() : "";
}
