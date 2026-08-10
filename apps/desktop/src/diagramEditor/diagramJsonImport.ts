import { applyDiagramHistoryUpdate, type DiagramHistory } from "./diagramHistory";
import { importDiagramJson } from "./diagramJson";
import { canonicalFamilyId } from "../projectModules";
import { diagramPayloadRelationshipScopeKey } from "./diagramScope";
import type { TranslationKey, Translator } from "../i18n";
import type { DiagramDocument, DiagramNode } from "./layoutModel";

export type DiagramJsonImportDraftResult =
  | {
      ok: true;
      changed: boolean;
      document: DiagramDocument;
      history: DiagramHistory;
    }
  | {
      ok: false;
      changed: false;
      error: string;
      history: DiagramHistory;
    };

export function importDiagramJsonDraft(history: DiagramHistory, base: DiagramDocument | null, text: string, t?: Translator): DiagramJsonImportDraftResult {
  let document: DiagramDocument;
  try {
    document = importDiagramJson(text, t);
  } catch (error: unknown) {
    return {
      ok: false,
      changed: false,
      error: error instanceof Error ? error.message : String(error),
      history
    };
  }
  const compatibilityError = base ? diagramImportCompatibilityError(base, document, t) : "";
  if (compatibilityError) {
    return {
      ok: false,
      changed: false,
      error: compatibilityError,
      history
    };
  }

  const result = applyDiagramHistoryUpdate(history, base, () => document);
  return {
    ok: true,
    changed: result.changed,
    document,
    history: result.history
  };
}

function diagramImportMessage(t: Translator | undefined, key: TranslationKey, fallback: string, params: Record<string, string | number> = {}): string {
  return t ? t(key, params) : fallback;
}

type ProjectDiagramPayloadFields = {
  embeddedId: string;
  embeddedKind: string;
  family: string;
  familyId: string;
  itemId: string;
  itemKind: string;
  moduleId: string;
  objectId: string;
  projectId: string;
  relativeRoot: string;
  sourceRoot: string;
  sourceRootRelativePath: string;
};

const PROJECT_DIAGRAM_PAYLOAD_FIELD_NAMES: (keyof ProjectDiagramPayloadFields)[] = [
  "embeddedId",
  "embeddedKind",
  "family",
  "familyId",
  "itemId",
  "itemKind",
  "moduleId",
  "objectId",
  "projectId",
  "relativeRoot",
  "sourceRoot",
  "sourceRootRelativePath"
];

const PROJECT_DIAGRAM_PAYLOAD_CONTEXT_FIELD_NAMES = PROJECT_DIAGRAM_PAYLOAD_FIELD_NAMES.filter((name) => name !== "embeddedId" && name !== "embeddedKind");

function diagramImportCompatibilityError(base: DiagramDocument, imported: DiagramDocument, t?: Translator): string {
  const basePayloadByNodeId = new Map<string, ProjectDiagramPayloadFields>();
  const basePayloadsByItemId = new Map<string, ProjectDiagramPayloadFields[]>();
  for (const node of base.nodes) {
    const payload = projectDiagramPayloadFields(node);
    if (!payload) {
      continue;
    }
    basePayloadByNodeId.set(node.id, payload);
    basePayloadsByItemId.set(payload.itemId, [...(basePayloadsByItemId.get(payload.itemId) ?? []), payload]);
  }
  if (basePayloadByNodeId.size === 0) {
    return "";
  }
  const importedPayloadByNodeId = new Map<string, ProjectDiagramPayloadFields>();
  for (const node of imported.nodes) {
    const payload = projectDiagramPayloadFields(node);
    if (payload) {
      importedPayloadByNodeId.set(node.id, payload);
    }
  }
  const importedNodeIds = new Set(imported.nodes.map((node) => node.id));
  for (const [nodeId, payload] of basePayloadByNodeId) {
    if (!importedNodeIds.has(nodeId) && payload.embeddedKind !== "focus") {
      return diagramImportMessage(t, "workspace.diagram.importError.removesNonFocus", `Imported diagram removes non-focus metadata node ${nodeId} that cannot be deleted through diagram import.`, { nodeId });
    }
  }
  for (const node of imported.nodes) {
    const payload = projectDiagramPayloadFields(node);
    if (!payload) {
      return diagramImportMessage(t, "workspace.diagram.importError.missingPayload", `Imported diagram node ${node.id} is missing ParaDev metadata payload.`, { nodeId: node.id });
    }
    if (payload.embeddedKind === "focus") {
      if (!payload.embeddedId) {
        return diagramImportMessage(t, "workspace.diagram.importError.missingEmbeddedFocusId", `Imported diagram node ${node.id} is missing ParaDev embedded focus id.`, { nodeId: node.id });
      }
      if (payload.embeddedId !== node.id) {
        return diagramImportMessage(t, "workspace.diagram.importError.mismatchedEmbeddedFocusId", `Imported diagram node ${node.id} has embedded focus id ${payload.embeddedId} that disagrees with the node id.`, { embeddedId: payload.embeddedId, nodeId: node.id });
      }
      const parentId = typeof node.parentId === "string" ? node.parentId : "";
      if (parentId && importedPayloadByNodeId.get(parentId)?.embeddedKind !== "focus") {
        return diagramImportMessage(t, "workspace.diagram.importError.nonFocusParent", `Imported diagram node ${node.id} cannot use non-focus parent ${parentId}.`, { nodeId: node.id, parentId });
      }
    }
    const basePayloads = basePayloadsByItemId.get(payload.itemId) ?? [];
    if (basePayloads.length === 0) {
      return diagramImportMessage(t, "workspace.diagram.importError.outsideEntity", `Imported diagram node ${node.id} targets metadata entity ${payload.itemId} outside the current diagram.`, { itemId: payload.itemId, nodeId: node.id });
    }
    if (!basePayloads.some((basePayload) => canTargetImportedPayload(basePayload, payload))) {
      return diagramImportMessage(t, "workspace.diagram.importError.outsideObject", `Imported diagram node ${node.id} targets metadata object ${payload.objectId} outside ${payload.itemId}.`, { itemId: payload.itemId, nodeId: node.id, objectId: payload.objectId });
    }
    const basePayload = basePayloadByNodeId.get(node.id);
    if (!basePayload && payload.embeddedKind !== "focus") {
      return diagramImportMessage(t, "workspace.diagram.importError.addsNonFocus", `Imported diagram node ${node.id} adds a non-focus metadata node that cannot be saved.`, { nodeId: node.id });
    }
    if (!basePayload && payload.embeddedKind === "focus" && !basePayloads.some((candidate) => canTargetImportedPayload(candidate, payload) && sameProjectDiagramPayloadContextFields(candidate, payload))) {
      return diagramImportMessage(t, "workspace.diagram.importError.changesNewFocusPayload", `Imported diagram node ${node.id} changes ParaDev metadata payload for a new focus node.`, { nodeId: node.id });
    }
    if (basePayload && !sameProjectDiagramPayloadFields(basePayload, payload)) {
      return diagramImportMessage(t, "workspace.diagram.importError.changesCurrentPayload", `Imported diagram node ${node.id} changes ParaDev metadata payload for the current diagram.`, { nodeId: node.id });
    }
  }
  const edgeScopeError = diagramEdgeScopeCompatibilityError(imported, importedPayloadByNodeId, t);
  if (edgeScopeError) {
    return edgeScopeError;
  }
  return "";
}

function diagramEdgeScopeCompatibilityError(document: DiagramDocument, payloadByNodeId: Map<string, ProjectDiagramPayloadFields>, t?: Translator): string {
  for (const edge of document.edges) {
    const sourcePayload = payloadByNodeId.get(edge.source);
    const targetPayload = payloadByNodeId.get(edge.target);
    if (!sourcePayload || !targetPayload) {
      continue;
    }
    if (diagramPayloadRelationshipScopeKey(sourcePayload) === diagramPayloadRelationshipScopeKey(targetPayload)) {
      continue;
    }
    const sourceIsFocus = sourcePayload.embeddedKind === "focus";
    const targetIsFocus = targetPayload.embeddedKind === "focus";
    if (edge.kind !== "tree" && sourceIsFocus !== targetIsFocus) {
      const focusId = sourceIsFocus ? edge.source : edge.target;
      const nonFocusId = sourceIsFocus ? edge.target : edge.source;
      return diagramImportMessage(t, "workspace.diagram.importError.edgeFocusNonFocus", `Imported diagram edge ${edge.id} cannot connect focus node ${focusId} to non-focus node ${nonFocusId}.`, { edgeId: edge.id, focusId, nonFocusId });
    }
    return diagramImportMessage(t, "workspace.diagram.importError.edgeDifferentScopes", `Imported diagram edge ${edge.id} cannot connect nodes from different diagram source scopes.`, { edgeId: edge.id });
  }
  return "";
}

function canTargetImportedPayload(basePayload: ProjectDiagramPayloadFields, payload: ProjectDiagramPayloadFields): boolean {
  if (basePayload.objectId !== payload.objectId) {
    return false;
  }
  if (basePayload.embeddedKind === payload.embeddedKind) {
    return true;
  }
  return payload.embeddedKind === "focus" && basePayload.embeddedKind === "" && canonicalFamilyId(basePayload.familyId, basePayload.family) === "focuses";
}

function projectDiagramPayloadFields(node: Pick<DiagramNode, "payload">): ProjectDiagramPayloadFields | null {
  if (!node.payload || typeof node.payload !== "object" || Array.isArray(node.payload)) {
    return null;
  }
  const payload = node.payload as Record<string, unknown>;
  if (typeof payload.itemId !== "string" || typeof payload.objectId !== "string") {
    return null;
  }
  return {
    embeddedId: typeof payload.embeddedId === "string" ? payload.embeddedId : "",
    embeddedKind: typeof payload.embeddedKind === "string" ? payload.embeddedKind : "",
    family: typeof payload.family === "string" ? payload.family : "",
    familyId: typeof payload.familyId === "string" ? payload.familyId : "",
    itemId: payload.itemId,
    itemKind: typeof payload.itemKind === "string" ? payload.itemKind : "",
    moduleId: typeof payload.moduleId === "string" ? payload.moduleId : "",
    objectId: payload.objectId,
    projectId: typeof payload.projectId === "string" ? payload.projectId : "",
    relativeRoot: typeof payload.relativeRoot === "string" ? payload.relativeRoot : "",
    sourceRoot: typeof payload.sourceRoot === "string" ? payload.sourceRoot : "",
    sourceRootRelativePath: typeof payload.sourceRootRelativePath === "string" ? payload.sourceRootRelativePath : ""
  };
}

function sameProjectDiagramPayloadFields(left: ProjectDiagramPayloadFields, right: ProjectDiagramPayloadFields): boolean {
  return PROJECT_DIAGRAM_PAYLOAD_FIELD_NAMES.every((name) => left[name] === right[name]);
}

function sameProjectDiagramPayloadContextFields(left: ProjectDiagramPayloadFields, right: ProjectDiagramPayloadFields): boolean {
  return PROJECT_DIAGRAM_PAYLOAD_CONTEXT_FIELD_NAMES.every((name) => left[name] === right[name]);
}
