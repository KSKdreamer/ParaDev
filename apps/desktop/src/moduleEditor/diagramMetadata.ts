import { diagramNodeRelationshipScopeKey } from "../diagramEditor/diagramScope";
import { resolveDiagramLayout } from "../diagramEditor/layoutModel";
import type { DiagramDocument, DiagramNode, DiagramNodeLayoutHints, DiagramRelativePositionKind } from "../diagramEditor/layoutModel";
import type { ProjectDiagramNodePayload } from "../diagramEditor/projectDiagram";
import type { ModuleEntity } from "./model";
import type { SourceTextEdit } from "../types";

export type DiagramMetadataTextDraft = {
  entityId: string;
  slot: "meta" | "source";
  path?: string;
  text: string;
};

export type DiagramMetadataTextDraftInput = {
  baseDocument: DiagramDocument;
  draftDocument: DiagramDocument;
  entities: Pick<ModuleEntity, "id" | "sourceSlots">[];
  metadataTextByEntityId: Record<string, string>;
  sourceTextByPath?: Record<string, string>;
};

export type DiagramMetadataSourceInfoRef = {
  entityId: string;
  path: string;
};

type ChangedNode = {
  addNode?: boolean;
  clearPosition?: boolean;
  dependencySourceIds?: string[];
  dependencyTargetIds?: string[];
  entityId: string;
  focusOrderIds?: string[];
  id: string;
  layoutHints?: DiagramNodeLayoutHints;
  parentId?: string;
  parentChanged?: boolean;
  referenceTargetIds?: string[];
  relativePositionKind?: DiagramRelativePositionKind;
  relativePositionId?: string;
  removeNode?: boolean;
  sourceInfoPath?: string;
  x?: number;
  y?: number;
  embeddedKind?: ProjectDiagramNodePayload["embeddedKind"];
};

type YamlListItemRange = {
  childIndent: string;
  end: number;
  insertAt: number;
  start: number;
};

const YAML_LIST_ITEM_PATTERN = /^\s*-\s+/;
const FOCUS_DEPENDENCY_SOURCE_ALIAS_KEYS = ["dependency_ids", "dependencyIds", "dependencies", "prerequisite", "required_technologies", "requiredTechnologies"];
const FOCUS_LAYOUT_WIDTH_KEYS = ["w", "pw", "subtree_width", "subtreeWidth"];
const FOCUS_LAYOUT_WIDTH_DELTA_KEYS = ["dw", "subtree_width_delta", "subtreeWidthDelta"];
const FOCUS_LAYOUT_CENTER_OFFSET_KEYS = ["dc", "subtree_center_offset", "subtreeCenterOffset"];
const FOCUS_REFERENCE_TARGET_ALIAS_KEYS = ["mutuallyExclusive", "exclusive_with", "exclusiveWith"];

export function buildDiagramMetadataTextDrafts(input: DiagramMetadataTextDraftInput): DiagramMetadataTextDraft[] {
  const changed = changedDiagramNodes(input.baseDocument, input.draftDocument);
  if (changed.length === 0) {
    return [];
  }
  const sourceDrafts = buildDiagramSourceInfoDrafts(changed, input.sourceTextByPath ?? {});
  const entityIdsWithMeta = new Set(input.entities.filter((entity) => entity.sourceSlots.some((source) => source.slot === "meta")).map((entity) => entity.id));
  const changesByEntity = groupByEntity(changed.filter((node) => entityIdsWithMeta.has(node.entityId)));
  const focusCounts = focusCountsByEntity(input.draftDocument);
  const metaDrafts = Object.entries(changesByEntity).flatMap(([entityId, nodes]) => {
    const metadataText = input.metadataTextByEntityId[entityId];
    if (metadataText === undefined) {
      return [];
    }
    const nextText = nodes.reduce((text, node) => applyNodePosition(text, node), metadataText);
    const countedText = nodes.some((node) => node.embeddedKind === "focus") ? updateFocusCount(nextText, focusCounts[entityId] ?? 0) : nextText;
    return countedText === metadataText ? [] : [{ entityId, slot: "meta" as const, text: countedText }];
  });
  return [...metaDrafts, ...sourceDrafts];
}

export function changedDiagramMetadataEntityIds(baseDocument: DiagramDocument, draftDocument: DiagramDocument): string[] {
  return Array.from(new Set(changedDiagramNodes(baseDocument, draftDocument).map((node) => node.entityId))).sort();
}

export function changedDiagramMetadataSourceInfoPaths(baseDocument: DiagramDocument, draftDocument: DiagramDocument): string[] {
  return changedDiagramMetadataSourceInfoRefs(baseDocument, draftDocument).map((ref) => ref.path);
}

export function changedDiagramMetadataSourceInfoRefs(baseDocument: DiagramDocument, draftDocument: DiagramDocument): DiagramMetadataSourceInfoRef[] {
  const refsByKey = new Map<string, DiagramMetadataSourceInfoRef>();
  for (const node of changedDiagramNodes(baseDocument, draftDocument)) {
    if (!node.sourceInfoPath) {
      continue;
    }
    const key = `${node.entityId}\0${node.sourceInfoPath}`;
    refsByKey.set(key, { entityId: node.entityId, path: node.sourceInfoPath });
  }
  return [...refsByKey.values()].sort((left, right) => left.entityId.localeCompare(right.entityId) || left.path.localeCompare(right.path));
}

export function sourceTextEditsForDiagramMetadataDrafts(entities: Pick<ModuleEntity, "id" | "sourceSlots">[], drafts: DiagramMetadataTextDraft[]): SourceTextEdit[] {
  const entitiesById = new Map(entities.map((entity) => [entity.id, entity]));
  return drafts.flatMap((draft) => {
    if (draft.path) {
      return [{ path: draft.path, text: draft.text }];
    }
    const source = entitiesById.get(draft.entityId)?.sourceSlots.find((slot) => slot.slot === draft.slot);
    return source?.path ? [{ path: source.path, text: draft.text }] : [];
  });
}

function changedDiagramNodes(baseDocument: DiagramDocument, draftDocument: DiagramDocument): ChangedNode[] {
  const base = resolveDiagramLayout(baseDocument).nodesById;
  const draft = resolveDiagramLayout(draftDocument).nodesById;
  const baseNodesById = new Map(baseDocument.nodes.map((node) => [node.id, node]));
  return [
    ...removedFocusNodes(baseDocument, draftDocument),
    ...addedFocusNodes(baseDocument, draftDocument),
    ...changedFocusOrderNodes(baseDocument, draftDocument),
    ...changedDependencySourceNodes(baseDocument, draftDocument),
    ...changedDependencyTargetNodes(baseDocument, draftDocument),
    ...changedReferenceTargetNodes(baseDocument, draftDocument),
    ...changedParentNodes(baseDocument, draftDocument),
    ...changedLayoutHintNodes(baseDocument, draftDocument),
    ...draftDocument.nodes.flatMap((node): ChangedNode[] => {
      const baseNode = base[node.id];
      const draftNode = draft[node.id];
      const baseRawNode = baseNodesById.get(node.id);
      const payload = asProjectDiagramNodePayload(node.payload);
      if (!baseNode || !draftNode || !payload?.itemId) {
        return [];
      }
      const sourceInfoPath = focusSourceInfoPath(payload, asProjectDiagramNodePayload(baseRawNode?.payload));
      const relativePositionId = focusRelativePositionId(node);
      const baseRelativePositionId = focusRelativePositionId(baseRawNode);
      const relativePositionChanged = payload.embeddedKind === "focus" && relativePositionId !== baseRelativePositionId;
      if (node.mode === "auto") {
        const baseLegacyOffset = legacyAutoOffset(baseRawNode);
        const draftLegacyOffset = legacyAutoOffset(node);
        if (baseLegacyOffset || draftLegacyOffset) {
          if (!draftLegacyOffset) {
            return [
              {
                clearPosition: true,
                entityId: payload.itemId,
                id: node.id,
                embeddedKind: payload.embeddedKind,
                sourceInfoPath
              }
            ];
          }
          if (!baseLegacyOffset || baseLegacyOffset.x !== draftLegacyOffset.x || baseLegacyOffset.y !== draftLegacyOffset.y) {
            return [
              {
                entityId: payload.itemId,
                id: node.id,
                relativePositionKind: "legacy_offset",
                x: draftLegacyOffset.x,
                y: draftLegacyOffset.y,
                sourceInfoPath,
                embeddedKind: payload.embeddedKind
              }
            ];
          }
        }
        if (baseRawNode?.mode === "auto" && !relativePositionChanged) {
          return [];
        }
        return [
          {
            clearPosition: true,
            entityId: payload.itemId,
            id: node.id,
            relativePositionKind: node.relativePositionKind,
            ...(relativePositionChanged ? { relativePositionId } : {}),
            sourceInfoPath,
            embeddedKind: payload.embeddedKind
          }
        ];
      }
      if (baseRawNode?.mode === node.mode && baseNode.worldX === draftNode.worldX && baseNode.worldY === draftNode.worldY && !relativePositionChanged) {
        return [];
      }
      const writePosition = diagramMetadataWritePosition(node, baseRawNode, draftNode, draft);
      return [
        {
          entityId: payload.itemId,
          id: node.id,
          relativePositionKind: node.relativePositionKind,
          ...(relativePositionChanged ? { relativePositionId } : {}),
          x: writePosition.x,
          y: writePosition.y,
          sourceInfoPath,
          embeddedKind: payload.embeddedKind
        }
      ];
    })
  ];
}

function addedFocusNodes(baseDocument: DiagramDocument, draftDocument: DiagramDocument): ChangedNode[] {
  const baseNodeIds = new Set(baseDocument.nodes.map((node) => node.id));
  const draftFocusNodeIds = focusNodeIds(draftDocument);
  return draftDocument.nodes.flatMap((node): ChangedNode[] => {
    if (baseNodeIds.has(node.id)) {
      return [];
    }
    const payload = asProjectDiagramNodePayload(node.payload);
    if (payload?.embeddedKind !== "focus" || !payload.itemId) {
      return [];
    }
    return [
      {
        addNode: true,
        entityId: payload.itemId,
        id: node.id,
        parentId: focusParentId(node.parentId, draftFocusNodeIds),
        sourceInfoPath: focusSourceInfoPath(payload),
        embeddedKind: payload.embeddedKind
      }
    ];
  });
}

function removedFocusNodes(baseDocument: DiagramDocument, draftDocument: DiagramDocument): ChangedNode[] {
  const draftNodeIds = new Set(draftDocument.nodes.map((node) => node.id));
  return baseDocument.nodes.flatMap((node): ChangedNode[] => {
    if (draftNodeIds.has(node.id)) {
      return [];
    }
    const payload = asProjectDiagramNodePayload(node.payload);
    if (payload?.embeddedKind !== "focus" || !payload.itemId) {
      return [];
    }
    return [
      {
        entityId: payload.itemId,
        id: node.id,
        removeNode: true,
        sourceInfoPath: focusSourceInfoPath(payload),
        embeddedKind: payload.embeddedKind
      }
    ];
  });
}

function diagramMetadataWritePosition(
  draftRawNode: DiagramNode,
  baseRawNode: DiagramNode | undefined,
  draftNode: { worldX: number; worldY: number },
  draftNodesById: Record<string, { worldX: number; worldY: number }>
): { x: number; y: number } {
  const parentId = draftRawNode.parentId || baseRawNode?.parentId || "";
  const parent = parentId ? draftNodesById[parentId] : undefined;
  if (draftRawNode.mode === "relative" && parent) {
    return {
      x: draftNode.worldX - parent.worldX,
      y: draftNode.worldY - parent.worldY
    };
  }
  return sourceFocusWritePosition(draftRawNode, baseRawNode, {
    x: draftNode.worldX,
    y: draftNode.worldY
  });
}

function sourceFocusWritePosition(draftRawNode: DiagramNode, baseRawNode: DiagramNode | undefined, position: { x: number; y: number }): { x: number; y: number } {
  const payload = asProjectDiagramNodePayload(draftRawNode.payload) ?? asProjectDiagramNodePayload(baseRawNode?.payload);
  if (payload?.embeddedKind !== "focus" || payload.sourceFocusSlots !== true) {
    return position;
  }
  return {
    x: position.x - Math.floor(sourceFocusSubtreeWidth(draftRawNode, baseRawNode) / 2),
    y: position.y
  };
}

function sourceFocusSubtreeWidth(draftRawNode: DiagramNode, baseRawNode: DiagramNode | undefined): number {
  const width = typeof draftRawNode.subtreeWidth === "number" && Number.isFinite(draftRawNode.subtreeWidth) ? draftRawNode.subtreeWidth : baseRawNode?.subtreeWidth;
  return typeof width === "number" && Number.isFinite(width) && width > 0 ? width : 2;
}

function legacyAutoOffset(node: DiagramNode | undefined): { x: number; y: number } | null {
  if (!node || node.mode !== "auto" || node.relativePositionKind !== "legacy_offset") {
    return null;
  }
  const x = typeof node.dx === "number" && Number.isFinite(node.dx) ? node.dx : 0;
  const y = typeof node.dy === "number" && Number.isFinite(node.dy) ? node.dy : 0;
  return { x, y };
}

function focusRelativePositionId(node: DiagramNode | undefined): string {
  if (!node || node.mode !== "relative" || node.relativePositionKind === "legacy_offset") {
    return "";
  }
  return node.parentId?.trim() ?? "";
}

function groupByEntity(nodes: ChangedNode[]): Record<string, ChangedNode[]> {
  const grouped: Record<string, ChangedNode[]> = {};
  for (const node of nodes) {
    grouped[node.entityId] = [...(grouped[node.entityId] ?? []), node];
  }
  return grouped;
}

function focusCountsByEntity(document: DiagramDocument): Record<string, number> {
  const counts: Record<string, number> = {};
  for (const node of document.nodes) {
    const payload = asProjectDiagramNodePayload(node.payload);
    if (payload?.embeddedKind !== "focus" || !payload.itemId) {
      continue;
    }
    counts[payload.itemId] = (counts[payload.itemId] ?? 0) + 1;
  }
  return counts;
}

function buildDiagramSourceInfoDrafts(changed: ChangedNode[], sourceTextByPath: Record<string, string>): DiagramMetadataTextDraft[] {
  const changesByPath = groupBySourceInfoPath(changed.filter((node) => node.embeddedKind === "focus" && Boolean(node.sourceInfoPath)));
  return Object.entries(changesByPath).flatMap(([path, nodes]) => {
    const sourceText = sourceTextByPath[path];
    if (sourceText === undefined || nodes.length === 0) {
      return [];
    }
    const nextText = nodes.reduce((text, node) => applyNodeSourceInfo(text, node), sourceText);
    return nextText === sourceText ? [] : [{ entityId: nodes[0].entityId, slot: "source" as const, path, text: nextText }];
  });
}

function groupBySourceInfoPath(nodes: ChangedNode[]): Record<string, ChangedNode[]> {
  const grouped: Record<string, ChangedNode[]> = {};
  for (const node of nodes) {
    if (!node.sourceInfoPath) {
      continue;
    }
    grouped[node.sourceInfoPath] = [...(grouped[node.sourceInfoPath] ?? []), node];
  }
  return grouped;
}

function applyNodePosition(text: string, node: ChangedNode): string {
  if (node.addNode) {
    return addNodeMetadata(text, node);
  }
  if (node.removeNode) {
    return removeNodeMetadata(text, node);
  }
  if (node.focusOrderIds) {
    return reorderFocusItems(text, node.focusOrderIds);
  }
  if (node.dependencySourceIds) {
    return updateNodeDependencySources(text, node);
  }
  if (node.dependencyTargetIds) {
    return updateNodeDependencyTargets(text, node);
  }
  if (node.referenceTargetIds) {
    return updateNodeReferenceTargets(text, node);
  }
  if (node.parentChanged) {
    return updateNodeParent(text, node);
  }
  if (node.layoutHints) {
    return updateNodeLayoutHints(text, node);
  }
  if (node.clearPosition) {
    return clearNodePosition(text, node);
  }
  if (node.x === undefined || node.y === undefined) {
    return node.embeddedKind === "focus" && node.relativePositionId !== undefined ? updateFocusRelativePosition(text, node.id, node.relativePositionId) : text;
  }
  if (node.embeddedKind === "focus") {
    if (node.relativePositionKind === "legacy_offset") {
      return updateFocusLegacyOffset(text, node.id, node.x, node.y);
    }
    return node.relativePositionId === undefined
      ? updateFocusPosition(text, node.id, node.x, node.y)
      : updateFocusRelativePosition(updateFocusPosition(text, node.id, node.x, node.y), node.id, node.relativePositionId);
  }
  return updateTechnologyPosition(text, node.x, node.y);
}

function applyNodeSourceInfo(text: string, node: ChangedNode): string {
  const data = parseJsonRecord(text);
  if (!data || node.addNode || node.removeNode || node.focusOrderIds) {
    return text;
  }
  let changed = false;
  if (node.dependencySourceIds) {
    changed = updateSourceInfoDependencySources(data, node.dependencySourceIds) || changed;
  }
  if (node.referenceTargetIds) {
    changed = updateSourceInfoReferenceTargets(data, node.referenceTargetIds) || changed;
  }
  if (node.parentChanged) {
    changed = setOptionalJsonParent(data, node.parentId) || changed;
  }
  if (node.layoutHints) {
    changed = updateSourceInfoLayoutHints(data, node.layoutHints) || changed;
  }
  if (node.clearPosition) {
    changed = removeJsonKeys(data, ["x", "y", "dx", "dy", "cx", "cy", "relative_position_id", "relativePositionId"]) || changed;
  } else if (node.x !== undefined && node.y !== undefined) {
    if (node.relativePositionKind === "legacy_offset") {
      changed = updateSourceInfoLegacyOffset(data, node.x, node.y) || changed;
    } else {
      changed = updateSourceInfoCoordinates(data, node.x, node.y, node.relativePositionId) || changed;
    }
  } else if (node.relativePositionId !== undefined) {
    changed = setOptionalJsonString(data, "relative_position_id", node.relativePositionId) || changed;
    if (node.relativePositionId.trim()) {
      changed = setOptionalJsonString(data, "parent", "") || changed;
    }
  }
  return changed ? formatJsonRecord(data, text.endsWith("\n")) : text;
}

function parseJsonRecord(text: string): Record<string, unknown> | null {
  try {
    const parsed = JSON.parse(text) as unknown;
    return parsed && typeof parsed === "object" && !Array.isArray(parsed) ? (parsed as Record<string, unknown>) : null;
  } catch {
    return null;
  }
}

function formatJsonRecord(record: Record<string, unknown>, trailingNewline: boolean): string {
  return `${JSON.stringify(record, null, 4)}${trailingNewline ? "\n" : ""}`;
}

function updateSourceInfoLegacyOffset(record: Record<string, unknown>, x: number, y: number): boolean {
  let changed = removeJsonKeys(record, ["x", "y", "relative_position_id", "relativePositionId"]);
  const usesCenterOffset = hasJsonKey(record, "cx") || hasJsonKey(record, "cy") ? !hasJsonKey(record, "dx") && !hasJsonKey(record, "dy") : false;
  changed = setJsonNumber(record, usesCenterOffset ? "cx" : "dx", x) || changed;
  changed = setJsonNumber(record, usesCenterOffset ? "cy" : "dy", y) || changed;
  return changed;
}

function updateSourceInfoCoordinates(record: Record<string, unknown>, x: number, y: number, relativePositionId: string | undefined): boolean {
  let changed = removeJsonKeys(record, ["dx", "dy", "cx", "cy"]);
  changed = setJsonNumber(record, "x", x) || changed;
  changed = setJsonNumber(record, "y", y) || changed;
  if (relativePositionId !== undefined) {
    changed = setOptionalJsonString(record, "relative_position_id", relativePositionId) || changed;
    if (relativePositionId.trim()) {
      changed = setOptionalJsonString(record, "parent", "") || changed;
    }
  }
  return changed;
}

function updateSourceInfoLayoutHints(record: Record<string, unknown>, hints: DiagramNodeLayoutHints): boolean {
  let changed = setOptionalJsonNumber(record, "priority", hints.priority);
  changed = setOptionalSourceInfoWidth(record, hints.subtreeWidth) || changed;
  changed = setOptionalSourceInfoLayoutNumber(record, "dw", hints.subtreeWidthDelta, FOCUS_LAYOUT_WIDTH_DELTA_KEYS) || changed;
  changed = setOptionalSourceInfoLayoutNumber(record, "dc", hints.subtreeCenterOffset, FOCUS_LAYOUT_CENTER_OFFSET_KEYS) || changed;
  return changed;
}

function updateSourceInfoDependencySources(record: Record<string, unknown>, dependencySourceIds: string[]): boolean {
  let changed = removeJsonKeys(record, FOCUS_DEPENDENCY_SOURCE_ALIAS_KEYS.filter((key) => key !== "prerequisites"));
  changed = removeJsonKeysMatching(record, (key) => /^prerequisite__/.test(key)) || changed;
  changed = setOptionalJsonStringList(record, "prerequisites", dependencySourceIds) || changed;
  return changed;
}

function updateSourceInfoReferenceTargets(record: Record<string, unknown>, referenceTargetIds: string[]): boolean {
  let changed = removeJsonKeys(record, FOCUS_REFERENCE_TARGET_ALIAS_KEYS.filter((key) => key !== "mutually_exclusive"));
  changed = setOptionalJsonStringList(record, "mutually_exclusive", referenceTargetIds) || changed;
  return changed;
}

function setOptionalSourceInfoWidth(record: Record<string, unknown>, value: number | undefined): boolean {
  if (value === undefined) {
    return removeJsonKeys(record, FOCUS_LAYOUT_WIDTH_KEYS);
  }
  const key = hasJsonKey(record, "pw") && !hasJsonKey(record, "w") ? "pw" : "w";
  return setOptionalSourceInfoLayoutNumber(record, key, value, FOCUS_LAYOUT_WIDTH_KEYS);
}

function setOptionalSourceInfoLayoutNumber(record: Record<string, unknown>, key: string, value: number | undefined, keys: string[]): boolean {
  if (value === undefined) {
    return removeJsonKeys(record, keys);
  }
  let changed = removeJsonKeys(record, keys.filter((candidate) => candidate !== key));
  changed = setJsonNumber(record, key, value) || changed;
  return changed;
}

function setOptionalJsonStringList(record: Record<string, unknown>, key: string, values: string[]): boolean {
  const clean = Array.from(new Set(values.map((value) => value.trim()).filter(Boolean)));
  if (clean.length === 0) {
    return removeJsonKeys(record, [key]);
  }
  if (sameJsonStringList(record[key], clean)) {
    return false;
  }
  record[key] = clean;
  return true;
}

function sameJsonStringList(value: unknown, expected: string[]): boolean {
  return Array.isArray(value) && value.length === expected.length && value.every((item, index) => item === expected[index]);
}

function setOptionalJsonString(record: Record<string, unknown>, key: string, value: string | undefined): boolean {
  if (value === undefined || !value.trim()) {
    return removeJsonKeys(record, [key]);
  }
  if (record[key] === value) {
    return false;
  }
  record[key] = value;
  return true;
}

function setOptionalJsonParent(record: Record<string, unknown>, parentId: string | undefined): boolean {
  const value = parentId?.trim() ?? "";
  if (!value) {
    if (record.parent === null) {
      return false;
    }
    record.parent = null;
    return true;
  }
  return setOptionalJsonString(record, "parent", value);
}

function setOptionalJsonNumber(record: Record<string, unknown>, key: string, value: number | undefined): boolean {
  return value === undefined ? removeJsonKeys(record, [key]) : setJsonNumber(record, key, value);
}

function setJsonNumber(record: Record<string, unknown>, key: string, value: number): boolean {
  if (record[key] === value) {
    return false;
  }
  record[key] = value;
  return true;
}

function removeJsonKeys(record: Record<string, unknown>, keys: string[]): boolean {
  let changed = false;
  for (const key of keys) {
    if (!hasJsonKey(record, key)) {
      continue;
    }
    delete record[key];
    changed = true;
  }
  return changed;
}

function removeJsonKeysMatching(record: Record<string, unknown>, predicate: (key: string) => boolean): boolean {
  return removeJsonKeys(record, Object.keys(record).filter(predicate));
}

function hasJsonKey(record: Record<string, unknown>, key: string): boolean {
  return Object.prototype.hasOwnProperty.call(record, key);
}

function clearNodePosition(text: string, node: ChangedNode): string {
  if (node.embeddedKind === "focus") {
    return clearFocusRelativePosition(clearFocusPosition(clearFocusLegacyOffset(text, node.id), node.id), node.id);
  }
  return clearTechnologyPosition(text);
}

function addNodeMetadata(text: string, node: ChangedNode): string {
  if (node.embeddedKind === "focus") {
    return insertFocusItem(text, node.id, node.parentId ?? "");
  }
  return text;
}

function removeNodeMetadata(text: string, node: ChangedNode): string {
  if (node.embeddedKind === "focus") {
    return removeFocusItem(text, node.id);
  }
  return text;
}

function updateNodeDependencySources(text: string, node: ChangedNode): string {
  const dependencySourceIds = node.dependencySourceIds ?? [];
  if (node.embeddedKind === "focus") {
    return updateFocusDependencySources(text, node.id, dependencySourceIds);
  }
  return updateTechnologyDependencySources(text, dependencySourceIds);
}

function updateNodeDependencyTargets(text: string, node: ChangedNode): string {
  if (node.embeddedKind === "focus") {
    return text;
  }
  return updateTechnologyDependencyTargets(text, node.dependencyTargetIds ?? []);
}

function updateNodeReferenceTargets(text: string, node: ChangedNode): string {
  const referenceTargetIds = node.referenceTargetIds ?? [];
  if (node.embeddedKind === "focus") {
    return updateFocusReferenceTargets(text, node.id, referenceTargetIds);
  }
  return text;
}

function updateNodeParent(text: string, node: ChangedNode): string {
  if (node.embeddedKind === "focus") {
    return updateFocusParent(text, node.id, node.parentId ?? "");
  }
  return text;
}

function updateNodeLayoutHints(text: string, node: ChangedNode): string {
  if (node.embeddedKind === "focus" && node.layoutHints) {
    return updateFocusLayoutHints(text, node.id, node.layoutHints);
  }
  return text;
}

function changedDependencySourceNodes(baseDocument: DiagramDocument, draftDocument: DiagramDocument): ChangedNode[] {
  const baseSources = dependencySourceIdsByTarget(baseDocument);
  const draftSources = dependencySourceIdsByTarget(draftDocument);
  const baseFocusNodeIds = focusNodeIds(baseDocument);
  const draftFocusNodeIds = focusNodeIds(draftDocument);
  const draftNodesById = new Map(draftDocument.nodes.map((node) => [node.id, node]));
  const targetIds = new Set([...Object.keys(baseSources), ...Object.keys(draftSources)]);
  return [...targetIds].flatMap((targetId): ChangedNode[] => {
    const node = draftNodesById.get(targetId);
    const payload = node ? asProjectDiagramNodePayload(node.payload) : null;
    if (!payload?.itemId) {
      return [];
    }
    const baseIds = payload.embeddedKind === "focus" ? matchingIds(baseSources[targetId] ?? [], baseFocusNodeIds) : baseSources[targetId] ?? [];
    const draftIds = payload.embeddedKind === "focus" ? matchingIds(draftSources[targetId] ?? [], draftFocusNodeIds) : draftSources[targetId] ?? [];
    if (sameMembers(baseIds, draftIds)) {
      return [];
    }
    return [
      {
        dependencySourceIds: draftIds,
        entityId: payload.itemId,
        id: targetId,
        sourceInfoPath: focusSourceInfoPath(payload),
        embeddedKind: payload.embeddedKind
      }
    ];
  });
}

function dependencySourceIdsByTarget(document: DiagramDocument): Record<string, string[]> {
  const nodesById = new Map(document.nodes.map((node) => [node.id, node]));
  const orderById = new Map(document.nodes.map((node, index) => [node.id, index]));
  const grouped: Record<string, string[]> = {};
  for (const edge of document.edges) {
    if (edge.kind !== "dependency") {
      continue;
    }
    if (!sameRelationshipScope(nodesById, edge.source, edge.target)) {
      continue;
    }
    grouped[edge.target] = [...(grouped[edge.target] ?? []), edge.source];
  }
  return Object.fromEntries(
    Object.entries(grouped).map(([targetId, sourceIds]) => [
      targetId,
      [...new Set(sourceIds)].sort((left, right) => (orderById.get(left) ?? Number.MAX_SAFE_INTEGER) - (orderById.get(right) ?? Number.MAX_SAFE_INTEGER) || left.localeCompare(right))
    ])
  );
}

function changedDependencyTargetNodes(baseDocument: DiagramDocument, draftDocument: DiagramDocument): ChangedNode[] {
  const baseTargets = dependencyTargetIdsBySource(baseDocument);
  const draftTargets = dependencyTargetIdsBySource(draftDocument);
  const baseFocusNodeIds = focusNodeIds(baseDocument);
  const draftFocusNodeIds = focusNodeIds(draftDocument);
  const draftNodesById = new Map(draftDocument.nodes.map((node) => [node.id, node]));
  const sourceIds = new Set([...Object.keys(baseTargets), ...Object.keys(draftTargets)]);
  return [...sourceIds].flatMap((sourceId): ChangedNode[] => {
    const node = draftNodesById.get(sourceId);
    const payload = node ? asProjectDiagramNodePayload(node.payload) : null;
    if (!payload?.itemId) {
      return [];
    }
    if (payload.embeddedKind === "focus") {
      return [];
    }
    const baseIds = excludingIds(baseTargets[sourceId] ?? [], baseFocusNodeIds);
    const draftIds = excludingIds(draftTargets[sourceId] ?? [], draftFocusNodeIds);
    if (sameMembers(baseIds, draftIds)) {
      return [];
    }
    return [
      {
        dependencyTargetIds: draftIds,
        entityId: payload.itemId,
        id: sourceId,
        sourceInfoPath: focusSourceInfoPath(payload),
        embeddedKind: payload.embeddedKind
      }
    ];
  });
}

function dependencyTargetIdsBySource(document: DiagramDocument): Record<string, string[]> {
  const nodesById = new Map(document.nodes.map((node) => [node.id, node]));
  const orderById = new Map(document.nodes.map((node, index) => [node.id, index]));
  const grouped: Record<string, string[]> = {};
  for (const edge of document.edges) {
    if (edge.kind !== "dependency") {
      continue;
    }
    if (!sameRelationshipScope(nodesById, edge.source, edge.target)) {
      continue;
    }
    grouped[edge.source] = [...(grouped[edge.source] ?? []), edge.target];
  }
  return Object.fromEntries(
    Object.entries(grouped).map(([sourceId, targetIds]) => [
      sourceId,
      [...new Set(targetIds)].sort((left, right) => (orderById.get(left) ?? Number.MAX_SAFE_INTEGER) - (orderById.get(right) ?? Number.MAX_SAFE_INTEGER) || left.localeCompare(right))
    ])
  );
}

function changedReferenceTargetNodes(baseDocument: DiagramDocument, draftDocument: DiagramDocument): ChangedNode[] {
  const baseTargets = referenceTargetIdsBySource(baseDocument);
  const draftTargets = referenceTargetIdsBySource(draftDocument);
  const baseFocusNodeIds = focusNodeIds(baseDocument);
  const draftFocusNodeIds = focusNodeIds(draftDocument);
  const draftNodesById = new Map(draftDocument.nodes.map((node) => [node.id, node]));
  const sourceIds = new Set([...Object.keys(baseTargets), ...Object.keys(draftTargets)]);
  return [...sourceIds].flatMap((sourceId): ChangedNode[] => {
    const node = draftNodesById.get(sourceId);
    const payload = node ? asProjectDiagramNodePayload(node.payload) : null;
    if (payload?.embeddedKind !== "focus" || !payload.itemId) {
      return [];
    }
    const baseIds = matchingIds(baseTargets[sourceId] ?? [], baseFocusNodeIds);
    const draftIds = matchingIds(draftTargets[sourceId] ?? [], draftFocusNodeIds);
    if (sameMembers(baseIds, draftIds)) {
      return [];
    }
    return [
      {
        entityId: payload.itemId,
        id: sourceId,
        referenceTargetIds: draftIds,
        sourceInfoPath: focusSourceInfoPath(payload),
        embeddedKind: payload.embeddedKind
      }
    ];
  });
}

function referenceTargetIdsBySource(document: DiagramDocument): Record<string, string[]> {
  const nodesById = new Map(document.nodes.map((node) => [node.id, node]));
  const orderById = new Map(document.nodes.map((node, index) => [node.id, index]));
  const grouped: Record<string, string[]> = {};
  for (const edge of document.edges) {
    if (edge.kind !== "reference") {
      continue;
    }
    if (!sameRelationshipScope(nodesById, edge.source, edge.target)) {
      continue;
    }
    grouped[edge.source] = [...(grouped[edge.source] ?? []), edge.target];
  }
  return Object.fromEntries(
    Object.entries(grouped).map(([sourceId, targetIds]) => [
      sourceId,
      [...new Set(targetIds)].sort((left, right) => (orderById.get(left) ?? Number.MAX_SAFE_INTEGER) - (orderById.get(right) ?? Number.MAX_SAFE_INTEGER) || left.localeCompare(right))
    ])
  );
}

function changedParentNodes(baseDocument: DiagramDocument, draftDocument: DiagramDocument): ChangedNode[] {
  const baseFocusNodeIds = focusNodeIds(baseDocument);
  const draftFocusNodeIds = focusNodeIds(draftDocument);
  const baseNodesById = new Map(baseDocument.nodes.map((node) => [node.id, node]));
  const draftResolved = resolveDiagramLayout(draftDocument).nodesById;
  return draftDocument.nodes.flatMap((node): ChangedNode[] => {
    const baseNode = baseNodesById.get(node.id);
    const baseParentId = focusParentId(baseNode?.parentId, baseFocusNodeIds);
    const draftParentId = focusParentId(node.parentId, draftFocusNodeIds);
    if (!baseNode || baseParentId === draftParentId) {
      return [];
    }
    const payload = asProjectDiagramNodePayload(node.payload);
    if (payload?.embeddedKind !== "focus" || !payload.itemId) {
      return [];
    }
    const writePosition = !draftParentId ? diagramMetadataWritePosition(node, baseNode, draftResolved[node.id], draftResolved) : undefined;
    return [
      {
        entityId: payload.itemId,
        id: node.id,
        parentChanged: true,
        parentId: draftParentId,
        ...(writePosition ? { x: writePosition.x, y: writePosition.y } : {}),
        sourceInfoPath: focusSourceInfoPath(payload, asProjectDiagramNodePayload(baseNode.payload)),
        embeddedKind: payload.embeddedKind
      }
    ];
  });
}

function changedLayoutHintNodes(baseDocument: DiagramDocument, draftDocument: DiagramDocument): ChangedNode[] {
  const baseNodesById = new Map(baseDocument.nodes.map((node) => [node.id, node]));
  return draftDocument.nodes.flatMap((node): ChangedNode[] => {
    const baseNode = baseNodesById.get(node.id);
    if (!baseNode) {
      return [];
    }
    const payload = asProjectDiagramNodePayload(node.payload);
    if (payload?.embeddedKind !== "focus" || !payload.itemId) {
      return [];
    }
    const baseHints = layoutHintsFor(baseNode);
    const draftHints = layoutHintsFor(node);
    if (sameLayoutHints(baseHints, draftHints)) {
      return [];
    }
    return [
      {
        entityId: payload.itemId,
        id: node.id,
        layoutHints: draftHints,
        sourceInfoPath: focusSourceInfoPath(payload, asProjectDiagramNodePayload(baseNode.payload)),
        embeddedKind: payload.embeddedKind
      }
    ];
  });
}

function layoutHintsFor(node: DiagramNode): DiagramNodeLayoutHints {
  return {
    priority: finiteLayoutHint(node.priority),
    subtreeCenterOffset: finiteLayoutHint(node.subtreeCenterOffset),
    subtreeWidth: positiveLayoutHint(node.subtreeWidth),
    subtreeWidthDelta: finiteLayoutHint(node.subtreeWidthDelta)
  };
}

function sameLayoutHints(left: DiagramNodeLayoutHints, right: DiagramNodeLayoutHints): boolean {
  return (
    Object.is(left.priority, right.priority) &&
    Object.is(left.subtreeCenterOffset, right.subtreeCenterOffset) &&
    Object.is(left.subtreeWidth, right.subtreeWidth) &&
    Object.is(left.subtreeWidthDelta, right.subtreeWidthDelta)
  );
}

function finiteLayoutHint(value: unknown): number | undefined {
  return typeof value === "number" && Number.isFinite(value) ? value : undefined;
}

function positiveLayoutHint(value: unknown): number | undefined {
  return typeof value === "number" && Number.isFinite(value) && value > 0 ? value : undefined;
}

function focusParentId(parentId: DiagramNode["parentId"], focusIds: Set<string>): string {
  const id = parentKey(parentId);
  return focusIds.has(id) ? id : "";
}

function parentKey(parentId: DiagramNode["parentId"]): string {
  return parentId ?? "";
}

function changedFocusOrderNodes(baseDocument: DiagramDocument, draftDocument: DiagramDocument): ChangedNode[] {
  const baseOrders = focusOrderIdsByEntity(baseDocument);
  const draftOrders = focusOrderIdsByEntity(draftDocument);
  return Object.entries(draftOrders).flatMap(([entityId, draftIds]) => {
    const baseIds = baseOrders[entityId] ?? [];
    if (draftIds.length < 2 || !sameMembers(baseIds, draftIds) || sameStrings(baseIds, draftIds)) {
      return [];
    }
    return [
      {
        entityId,
        focusOrderIds: draftIds,
        id: `${entityId}:focus-order`,
        embeddedKind: "focus" as const
      }
    ];
  });
}

function focusOrderIdsByEntity(document: DiagramDocument): Record<string, string[]> {
  const nodesByEntity: Record<string, DiagramNode[]> = {};
  for (const node of document.nodes) {
    const payload = asProjectDiagramNodePayload(node.payload);
    if (payload?.embeddedKind !== "focus") {
      continue;
    }
    nodesByEntity[payload.itemId] = [...(nodesByEntity[payload.itemId] ?? []), node];
  }
  return Object.fromEntries(
    Object.entries(nodesByEntity).map(([entityId, nodes]) => [
      entityId,
      [...nodes].sort((left, right) => left.order - right.order || left.id.localeCompare(right.id)).map((node) => node.id)
    ])
  );
}

function focusNodeIds(document: DiagramDocument): Set<string> {
  return new Set(document.nodes.filter((node) => asProjectDiagramNodePayload(node.payload)?.embeddedKind === "focus").map((node) => node.id));
}

function sameRelationshipScope(nodesById: Map<string, DiagramNode>, sourceId: string, targetId: string): boolean {
  const source = nodesById.get(sourceId);
  const target = nodesById.get(targetId);
  return Boolean(source && target && diagramNodeRelationshipScopeKey(source) === diagramNodeRelationshipScopeKey(target));
}

function matchingIds(ids: string[], validIds: Set<string>): string[] {
  return ids.filter((id) => validIds.has(id));
}

function excludingIds(ids: string[], excludedIds: Set<string>): string[] {
  return ids.filter((id) => !excludedIds.has(id));
}

function sameMembers(left: string[], right: string[]): boolean {
  if (left.length !== right.length) {
    return false;
  }
  const leftIds = new Set(left);
  return right.every((id) => leftIds.has(id));
}

function sameStrings(left: string[], right: string[]): boolean {
  return left.length === right.length && left.every((value, index) => value === right[index]);
}

function updateTechnologyPosition(text: string, x: number, y: number): string {
  const nested = updateYamlPairAfterPath(text, ["folder", "position"], x, y);
  const flat = updateYamlPairAfterPath(nested, ["folder_position"], x, y);
  return flat === text ? insertTechnologyFolderPosition(text, x, y) : flat;
}

function clearTechnologyPosition(text: string): string {
  return removeYamlBlockAfterPath(removeYamlBlockAfterPath(text, ["folder", "position"]), ["folder_position"]);
}

function updateFocusCount(text: string, count: number): string {
  const lines = splitLines(text);
  const changed = updateExistingScalarCountInRange(lines, "focus_count", count, 0, lines.length);
  return changed ? lines.join("\n") : text;
}

function updateFocusPosition(text: string, focusId: string, x: number, y: number): string {
  const lines = splitLines(text);
  const sourceRange = sourceFocusListItemRange(lines, focusId);
  const range = sourceRange ?? focusListItemRange(lines, focusId);
  if (!range) {
    return text;
  }
  const next = [...lines];
  const hadLegacyOffset = ["dx", "dy", "cx", "cy"].some((key) => findKeyLine(lines, key, range.start + 1, range.end) >= 0);
  removePairsInRange(next, range.start + 1, range.end, ["dx", "dy", "cx", "cy"]);
  const offsetClearedRange = (sourceRange ? sourceFocusListItemRange(next, focusId) : focusListItemRange(next, focusId)) ?? range;
  if (hadLegacyOffset) {
    upsertScalarInRange(next, "parent", "", offsetClearedRange.start + 1, offsetClearedRange.end, offsetClearedRange.insertAt, offsetClearedRange.childIndent);
  }
  const nextRange = (sourceRange ? sourceFocusListItemRange(next, focusId) : focusListItemRange(next, focusId)) ?? offsetClearedRange;
  upsertPairInRange(next, nextRange.start + 1, nextRange.end, x, y, nextRange.insertAt, nextRange.childIndent);
  return next.join("\n");
}

function clearFocusPosition(text: string, focusId: string): string {
  const lines = splitLines(text);
  const range = sourceFocusListItemRange(lines, focusId) ?? focusListItemRange(lines, focusId);
  if (!range) {
    return text;
  }
  const next = [...lines];
  const changed = removePairsInRange(next, range.start + 1, range.end, ["x", "y"]);
  return changed ? next.join("\n") : text;
}

function updateFocusLegacyOffset(text: string, focusId: string, dx: number, dy: number): string {
  const lines = splitLines(text);
  const sourceRange = sourceFocusListItemRange(lines, focusId);
  const range = sourceRange ?? focusListItemRange(lines, focusId);
  if (!range) {
    return text;
  }
  const offsetPair = legacyOffsetPairForRange(lines, range);
  const conflictingKeys = offsetPair.xKey === "cx" ? ["x", "y", "dx", "dy", "relative_position_id"] : ["x", "y", "cx", "cy", "relative_position_id"];
  const next = [...lines];
  removePairsInRange(next, range.start + 1, range.end, conflictingKeys);
  const nextRange = (sourceRange ? sourceFocusListItemRange(next, focusId) : focusListItemRange(next, focusId)) ?? range;
  upsertNamedPairInRange(next, offsetPair.xKey, offsetPair.yKey, nextRange.start + 1, nextRange.end, dx, dy, nextRange.insertAt, nextRange.childIndent);
  return next.join("\n");
}

function legacyOffsetPairForRange(lines: string[], range: YamlListItemRange): { xKey: "cx" | "dx"; yKey: "cy" | "dy" } {
  const hasDx = findKeyLine(lines, "dx", range.start + 1, range.end) >= 0;
  const hasDy = findKeyLine(lines, "dy", range.start + 1, range.end) >= 0;
  const hasCx = findKeyLine(lines, "cx", range.start + 1, range.end) >= 0;
  const hasCy = findKeyLine(lines, "cy", range.start + 1, range.end) >= 0;
  return (hasCx || hasCy) && !hasDx && !hasDy ? { xKey: "cx", yKey: "cy" } : { xKey: "dx", yKey: "dy" };
}

function clearFocusLegacyOffset(text: string, focusId: string): string {
  const lines = splitLines(text);
  const range = sourceFocusListItemRange(lines, focusId) ?? focusListItemRange(lines, focusId);
  if (!range) {
    return text;
  }
  const next = [...lines];
  const changed = removePairsInRange(next, range.start + 1, range.end, ["dx", "dy", "cx", "cy"]);
  return changed ? next.join("\n") : text;
}

function updateFocusRelativePosition(text: string, focusId: string, relativePositionId: string): string {
  const lines = splitLines(text);
  const sourceRange = sourceFocusListItemRange(lines, focusId);
  const range = sourceRange ?? focusListItemRange(lines, focusId);
  if (!range) {
    return text;
  }
  const next = [...lines];
  let changed = upsertScalarInRange(next, "relative_position_id", relativePositionId, range.start + 1, range.end, range.insertAt, range.childIndent);
  if (relativePositionId.trim()) {
    const nextRange = sourceRange ? sourceFocusListItemRange(next, focusId) : focusListItemRange(next, focusId);
    if (nextRange) {
      changed = upsertScalarInRange(next, "parent", "", nextRange.start + 1, nextRange.end, nextRange.insertAt, nextRange.childIndent) || changed;
    }
  }
  return changed ? next.join("\n") : text;
}

function clearFocusRelativePosition(text: string, focusId: string): string {
  return updateFocusRelativePosition(text, focusId, "");
}

function updateFocusDependencySources(text: string, focusId: string, dependencySourceIds: string[]): string {
  const lines = splitLines(text);
  const sourceRange = sourceFocusListItemRange(lines, focusId);
  const range = sourceRange ?? focusListItemRange(lines, focusId);
  if (!range) {
    return text;
  }
  const next = [...lines];
  const aliasChanged = sourceRange ? removeYamlKeyBlocksInRange(next, range.start + 1, range.end, FOCUS_DEPENDENCY_SOURCE_ALIAS_KEYS) : false;
  const activeRange = (sourceRange ? sourceFocusListItemRange(next, focusId) : focusListItemRange(next, focusId)) ?? range;
  const insertAt = sourceRange ? activeRange.insertAt : relationshipListInsertAt(lines, "prerequisite_count", range);
  const listChanged = upsertScalarListInRange(next, "prerequisites", dependencySourceIds, activeRange.start + 1, activeRange.end, insertAt, activeRange.childIndent, Boolean(sourceRange));
  const nextRange = (sourceRange ? sourceFocusListItemRange(next, focusId) : focusListItemRange(next, focusId)) ?? activeRange;
  const countChanged = updateExistingScalarCountInRange(next, "prerequisite_count", dependencySourceIds.length, nextRange.start + 1, nextRange.end);
  return aliasChanged || listChanged || countChanged ? next.join("\n") : text;
}

function updateFocusReferenceTargets(text: string, focusId: string, referenceTargetIds: string[]): string {
  const lines = splitLines(text);
  const sourceRange = sourceFocusListItemRange(lines, focusId);
  const range = sourceRange ?? focusListItemRange(lines, focusId);
  if (!range) {
    return text;
  }
  const next = [...lines];
  const aliasChanged = sourceRange ? removeYamlKeyBlocksInRange(next, range.start + 1, range.end, FOCUS_REFERENCE_TARGET_ALIAS_KEYS) : false;
  const activeRange = (sourceRange ? sourceFocusListItemRange(next, focusId) : focusListItemRange(next, focusId)) ?? range;
  const insertAt = sourceRange ? activeRange.insertAt : relationshipListInsertAt(lines, "mutually_exclusive_count", range);
  const listChanged = upsertScalarListInRange(next, "mutually_exclusive", referenceTargetIds, activeRange.start + 1, activeRange.end, insertAt, activeRange.childIndent, Boolean(sourceRange));
  const nextRange = (sourceRange ? sourceFocusListItemRange(next, focusId) : focusListItemRange(next, focusId)) ?? activeRange;
  const countChanged = updateExistingScalarCountInRange(next, "mutually_exclusive_count", referenceTargetIds.length, nextRange.start + 1, nextRange.end);
  return aliasChanged || listChanged || countChanged ? next.join("\n") : text;
}

function updateFocusParent(text: string, focusId: string, parentId: string): string {
  const lines = splitLines(text);
  const range = sourceFocusListItemRange(lines, focusId) ?? focusListItemRange(lines, focusId);
  if (!range) {
    return text;
  }
  const next = [...lines];
  const changed = upsertScalarInRange(next, "parent", parentId, range.start + 1, range.end, range.insertAt, range.childIndent);
  return changed ? next.join("\n") : text;
}

function updateFocusLayoutHints(text: string, focusId: string, hints: DiagramNodeLayoutHints): string {
  const lines = splitLines(text);
  const sourceRange = sourceFocusListItemRange(lines, focusId);
  const initialRange = sourceRange ?? focusListItemRange(lines, focusId);
  if (!initialRange) {
    return text;
  }
  const next = [...lines];
  const locateRange = () => (sourceRange ? sourceFocusListItemRange(next, focusId) : focusListItemRange(next, focusId)) ?? initialRange;
  let changed = false;
  changed = upsertOptionalNumberInFocusRange(next, locateRange(), "priority", hints.priority) || changed;
  changed = upsertOptionalWidthHintInFocusRange(next, locateRange(), hints.subtreeWidth) || changed;
  changed = upsertOptionalCanonicalNumberInFocusRange(next, locateRange(), "dw", FOCUS_LAYOUT_WIDTH_DELTA_KEYS, hints.subtreeWidthDelta) || changed;
  changed = upsertOptionalCanonicalNumberInFocusRange(next, locateRange(), "dc", FOCUS_LAYOUT_CENTER_OFFSET_KEYS, hints.subtreeCenterOffset) || changed;
  return changed ? next.join("\n") : text;
}

function upsertOptionalWidthHintInFocusRange(lines: string[], range: YamlListItemRange, value: number | undefined): boolean {
  const start = range.start + 1;
  const end = range.end;
  const key = findKeyLine(lines, "pw", start, end) >= 0 ? "pw" : findKeyLine(lines, "w", start, end) >= 0 ? "w" : "w";
  return upsertOptionalCanonicalNumberInFocusRange(lines, range, key, FOCUS_LAYOUT_WIDTH_KEYS, value);
}

function upsertOptionalCanonicalNumberInFocusRange(lines: string[], range: YamlListItemRange, key: string, keys: string[], value: number | undefined): boolean {
  const start = range.start + 1;
  const end = range.end;
  if (value === undefined) {
    return removePairsInRange(lines, start, end, keys);
  }
  const removed = removePairsInRangeCount(lines, start, end, keys.filter((candidate) => candidate !== key));
  const nextEnd = Math.max(start, Math.min(lines.length, end - removed));
  const changed = upsertScalarInRange(lines, key, String(value), start, nextEnd, beforeTrailingBlankLines(lines, nextEnd), range.childIndent);
  return removed > 0 || changed;
}

function upsertOptionalNumberInFocusRange(lines: string[], range: YamlListItemRange, key: string, value: number | undefined): boolean {
  return upsertScalarInRange(lines, key, value === undefined ? "" : String(value), range.start + 1, range.end, beforeTrailingBlankLines(lines, range.end), range.childIndent);
}

function updateTechnologyDependencySources(text: string, dependencySourceIds: string[]): string {
  const lines = splitLines(text);
  const settingsIndex = findKeyLine(lines, "settings", 0);
  if (settingsIndex < 0) {
    if (dependencySourceIds.length === 0) {
      return text;
    }
    const insertAt = beforeTrailingBlankLines(lines, lines.length);
    lines.splice(insertAt, 0, "settings:", "    dependency_ids:", ...dependencySourceIds.map((id) => `    - ${id}`));
    return lines.join("\n");
  }
  const parentIndent = leadingWhitespace(lines[settingsIndex]);
  const start = settingsIndex + 1;
  const end = findBlockEnd(lines, start, parentIndent);
  const childIndent = childIndentForBlock(lines, start, end, parentIndent);
  const changed = upsertScalarListInRange(lines, "dependency_ids", dependencySourceIds, start, end, beforeTrailingBlankLines(lines, end), childIndent, true);
  return changed ? lines.join("\n") : text;
}

function updateTechnologyDependencyTargets(text: string, dependencyTargetIds: string[]): string {
  const lines = splitLines(text);
  const settingsIndex = findKeyLine(lines, "settings", 0);
  if (settingsIndex < 0) {
    if (dependencyTargetIds.length === 0) {
      return text;
    }
    const insertAt = beforeTrailingBlankLines(lines, lines.length);
    lines.splice(insertAt, 0, "settings:", `    path_count: ${dependencyTargetIds.length}`, "    path_target_ids:", ...dependencyTargetIds.map((id) => `    - ${id}`));
    return lines.join("\n");
  }
  const parentIndent = leadingWhitespace(lines[settingsIndex]);
  const start = settingsIndex + 1;
  const end = findBlockEnd(lines, start, parentIndent);
  const childIndent = childIndentForBlock(lines, start, end, parentIndent);
  const listChanged = upsertScalarListInRange(lines, "path_target_ids", dependencyTargetIds, start, end, scalarListInsertAt(lines, "path_count", start, end), childIndent, true);
  const countChanged = updateExistingScalarCountInRange(lines, "path_count", dependencyTargetIds.length, start, findBlockEnd(lines, start, parentIndent));
  return listChanged || countChanged ? lines.join("\n") : text;
}

function removeFocusItem(text: string, focusId: string): string {
  const lines = splitLines(text);
  const range = focusListItemRange(lines, focusId);
  if (!range) {
    return text;
  }
  const end = range.end === lines.length ? beforeTrailingBlankLines(lines, range.end) : range.end;
  const next = [...lines];
  next.splice(range.start, Math.max(1, end - range.start));
  return next.join("\n");
}

function insertFocusItem(text: string, focusId: string, parentId: string): string {
  const lines = splitLines(text);
  if (focusListItemRange(lines, focusId)) {
    return text;
  }
  const range = focusListRange(lines);
  if (!range) {
    return text;
  }
  const focusesIndex = findKeyLine(lines, "focuses", 0);
  if (focusesIndex >= 0 && isInlineEmptyYamlList(lines[focusesIndex], "focuses")) {
    lines[focusesIndex] = `${leadingWhitespace(lines[focusesIndex])}focuses:`;
  }
  const countFields = focusListRelationshipCountFields(lines, focusesIndex, range.end);
  const parent = parentId.trim();
  const focusLines = [`${range.itemIndent}-   id: ${focusId}`];
  if (countFields.prerequisite) {
    focusLines.push(`${range.childIndent}prerequisite_count: ${parent ? 1 : 0}`);
  }
  if (parent) {
    focusLines.push(`${range.childIndent}prerequisites:`, `${range.childIndent}- ${parent}`);
  }
  if (countFields.mutuallyExclusive) {
    focusLines.push(`${range.childIndent}mutually_exclusive_count: 0`);
  }
  const insertAt = beforeTrailingBlankLines(lines, range.end);
  const next = [...lines];
  next.splice(insertAt, 0, ...focusLines);
  return next.join("\n");
}

function focusListRelationshipCountFields(lines: string[], focusesIndex: number, end: number): { prerequisite: boolean; mutuallyExclusive: boolean } {
  const hasFocusCount = focusesIndex > 0 && findKeyLine(lines, "focus_count", 0, focusesIndex) >= 0;
  return {
    prerequisite: hasFocusCount || findKeyLine(lines, "prerequisite_count", focusesIndex + 1, end) >= 0,
    mutuallyExclusive: hasFocusCount || findKeyLine(lines, "mutually_exclusive_count", focusesIndex + 1, end) >= 0
  };
}

function reorderFocusItems(text: string, orderedIds: string[]): string {
  const lines = splitLines(text);
  const rangesById = new Map(orderedIds.map((id) => [id, focusListItemRange(lines, id)] as const));
  if (orderedIds.some((id) => !rangesById.get(id))) {
    return text;
  }
  const orderedRanges = orderedIds.map((id) => rangesById.get(id)).filter((range): range is YamlListItemRange => Boolean(range));
  const sourceRanges = [...orderedRanges].sort((left, right) => left.start - right.start);
  if (sourceRanges.some((range, index) => index > 0 && sourceRanges[index - 1].end !== range.start)) {
    return text;
  }
  const start = sourceRanges[0].start;
  const end = sourceRanges[sourceRanges.length - 1].end;
  const trailingStart = beforeTrailingBlankLines(lines, end);
  const trailing = lines.slice(trailingStart, end);
  const reordered = [...orderedRanges.flatMap((range) => lines.slice(range.start, beforeTrailingBlankLines(lines, range.end))), ...trailing];
  if (sameStrings(lines.slice(start, end), reordered)) {
    return text;
  }
  const next = [...lines];
  next.splice(start, end - start, ...reordered);
  return next.join("\n");
}

function insertTechnologyFolderPosition(text: string, x: number, y: number): string {
  const lines = splitLines(text);
  const settingsIndex = findKeyLine(lines, "settings", 0);
  if (settingsIndex < 0) {
    const insertAt = beforeTrailingBlankLines(lines, lines.length);
    lines.splice(insertAt, 0, "settings:", "    folder_position:", `        x: ${x}`, `        y: ${y}`);
    return lines.join("\n");
  }
  const parentIndent = leadingWhitespace(lines[settingsIndex]);
  const start = settingsIndex + 1;
  const end = findBlockEnd(lines, start, parentIndent);
  const childIndent = childIndentForBlock(lines, start, end, parentIndent);
  const insertAt = beforeTrailingBlankLines(lines, end);
  lines.splice(insertAt, 0, `${childIndent}folder_position:`, `${childIndent}    x: ${x}`, `${childIndent}    y: ${y}`);
  return lines.join("\n");
}

function removeYamlBlockAfterPath(text: string, path: string[]): string {
  const lines = splitLines(text);
  let start = 0;
  let end = lines.length;
  for (let index = 0; index < path.length; index += 1) {
    const lineIndex = findKeyLine(lines, path[index], start, end);
    if (lineIndex < 0) {
      return text;
    }
    const indent = leadingWhitespace(lines[lineIndex]);
    if (index === path.length - 1) {
      const blockEnd = beforeTrailingBlankLines(lines, findBlockEnd(lines, lineIndex + 1, indent));
      lines.splice(lineIndex, Math.max(1, blockEnd - lineIndex));
      return lines.join("\n");
    }
    start = lineIndex + 1;
    end = findBlockEnd(lines, start, indent);
  }
  return text;
}

function updateYamlPairAfterPath(text: string, path: string[], x: number, y: number): string {
  const lines = splitLines(text);
  let start = 0;
  for (const key of path) {
    const index = findKeyLine(lines, key, start);
    if (index < 0) {
      return text;
    }
    start = index + 1;
  }
  const end = findBlockEnd(lines, start, leadingWhitespace(lines[start - 1]));
  const next = [...lines];
  const updated = updatePairInRange(next, start, end, x, y);
  return updated ? next.join("\n") : text;
}

function removePairsInRange(lines: string[], start: number, end: number, keys: string[]): boolean {
  return removePairsInRangeCount(lines, start, end, keys) > 0;
}

function removePairsInRangeCount(lines: string[], start: number, end: number, keys: string[]): number {
  const indexes = keys.map((key) => findKeyLine(lines, key, start, end)).filter((index) => index >= 0);
  for (const index of indexes.sort((left, right) => right - left)) {
    lines.splice(index, 1);
  }
  return indexes.length;
}

function removeYamlKeyBlocksInRange(lines: string[], start: number, end: number, keys: string[]): boolean {
  let changed = false;
  let blockEnd = end;
  for (const key of keys) {
    let keyIndex = findKeyLine(lines, key, start, blockEnd);
    while (keyIndex >= 0) {
      const range = scalarListBlockRange(lines, keyIndex, blockEnd);
      const deleteCount = Math.max(1, range.end - range.start);
      lines.splice(range.start, deleteCount);
      blockEnd -= deleteCount;
      changed = true;
      keyIndex = findKeyLine(lines, key, start, blockEnd);
    }
  }
  return changed;
}

function updatePairInRange(lines: string[], start: number, end: number, x: number, y: number): boolean {
  const xIndex = findKeyLine(lines, "x", start, end);
  const yIndex = findKeyLine(lines, "y", start, end);
  if (xIndex < 0 || yIndex < 0) {
    return false;
  }
  lines[xIndex] = replaceYamlScalar(lines[xIndex], x);
  lines[yIndex] = replaceYamlScalar(lines[yIndex], y);
  return true;
}

function upsertPairInRange(lines: string[], start: number, end: number, x: number, y: number, insertAt: number, indent: string): boolean {
  return upsertNamedPairInRange(lines, "x", "y", start, end, x, y, insertAt, indent);
}

function upsertNamedPairInRange(lines: string[], xKey: string, yKey: string, start: number, end: number, x: number, y: number, insertAt: number, indent: string): boolean {
  const xIndex = findKeyLine(lines, xKey, start, end);
  const yIndex = findKeyLine(lines, yKey, start, end);
  if (xIndex >= 0) {
    lines[xIndex] = replaceYamlScalar(lines[xIndex], x);
  }
  if (yIndex >= 0) {
    lines[yIndex] = replaceYamlScalar(lines[yIndex], y);
  }
  const inserts = [];
  if (xIndex < 0) {
    inserts.push(`${indent}${xKey}: ${x}`);
  }
  if (yIndex < 0) {
    inserts.push(`${indent}${yKey}: ${y}`);
  }
  if (inserts.length > 0) {
    lines.splice(insertAt, 0, ...inserts);
  }
  return xIndex >= 0 || yIndex >= 0 || inserts.length > 0;
}

function upsertScalarInRange(lines: string[], key: string, value: string, start: number, end: number, insertAt: number, indent: string): boolean {
  const cleanedValue = value.trim();
  const keyIndex = findKeyLine(lines, key, start, end);
  if (keyIndex < 0) {
    if (!cleanedValue) {
      return false;
    }
    lines.splice(insertAt, 0, `${indent}${key}: ${cleanedValue}`);
    return true;
  }
  if (!cleanedValue) {
    lines.splice(keyIndex, 1);
    return true;
  }
  const next = replaceYamlStringScalar(lines[keyIndex], cleanedValue);
  if (next === lines[keyIndex]) {
    return false;
  }
  lines[keyIndex] = next;
  return true;
}

function upsertScalarListInRange(lines: string[], key: string, values: string[], start: number, end: number, insertAt: number, indent: string, keepEmpty = false): boolean {
  const cleanedValues = values.map((value) => value.trim()).filter(Boolean);
  const keyIndex = findKeyLine(lines, key, start, end);
  if (keyIndex < 0) {
    if (cleanedValues.length === 0) {
      return false;
    }
    lines.splice(insertAt, 0, `${indent}${key}:`, ...cleanedValues.map((value) => `${indent}- ${value}`));
    return true;
  }
  const range = scalarListBlockRange(lines, keyIndex, end);
  const current = lines.slice(range.start, range.end);
  const next =
    cleanedValues.length === 0
      ? keepEmpty
        ? [`${leadingWhitespace(lines[keyIndex])}${key}: []`]
        : []
      : [`${leadingWhitespace(lines[keyIndex])}${key}:`, ...cleanedValues.map((value) => `${range.itemIndent}- ${value}`)];
  if (sameStrings(current, next)) {
    return false;
  }
  lines.splice(range.start, range.end - range.start, ...next);
  return true;
}

function updateExistingScalarCountInRange(lines: string[], key: string, value: number, start: number, end: number): boolean {
  const keyIndex = findKeyLine(lines, key, start, end);
  if (keyIndex < 0) {
    return false;
  }
  const next = replaceYamlScalar(lines[keyIndex], value);
  if (next === lines[keyIndex]) {
    return false;
  }
  lines[keyIndex] = next;
  return true;
}

function relationshipListInsertAt(lines: string[], countKey: string, range: YamlListItemRange): number {
  const countIndex = findKeyLine(lines, countKey, range.start + 1, range.end);
  return countIndex >= 0 ? countIndex + 1 : beforeTrailingBlankLines(lines, range.end);
}

function scalarListInsertAt(lines: string[], countKey: string, start: number, end: number): number {
  const countIndex = findKeyLine(lines, countKey, start, end);
  return countIndex >= 0 ? countIndex + 1 : beforeTrailingBlankLines(lines, end);
}

function scalarListBlockRange(lines: string[], keyIndex: number, end: number): { end: number; itemIndent: string; start: number } {
  const keyIndent = leadingWhitespace(lines[keyIndex]);
  let blockEnd = keyIndex + 1;
  let itemIndent = keyIndent;
  for (let index = keyIndex + 1; index < end; index += 1) {
    const line = lines[index];
    if (!line.trim()) {
      blockEnd = index + 1;
      continue;
    }
    const indent = leadingWhitespace(line);
    const isListItem = YAML_LIST_ITEM_PATTERN.test(line);
    if (indent.length < keyIndent.length || (indent.length === keyIndent.length && !isListItem)) {
      break;
    }
    if (isListItem && itemIndent === keyIndent) {
      itemIndent = indent;
    }
    blockEnd = index + 1;
  }
  return { start: keyIndex, end: beforeTrailingBlankLines(lines, blockEnd), itemIndent };
}

function findKeyLine(lines: string[], key: string, start: number, end = lines.length): number {
  const pattern = new RegExp(`^\\s*${escapeRegExp(key)}:\\s*`);
  for (let index = start; index < end; index += 1) {
    if (pattern.test(lines[index])) {
      return index;
    }
  }
  return -1;
}

function findBlockEnd(lines: string[], start: number, parentIndent: string): number {
  for (let index = start; index < lines.length; index += 1) {
    if (lines[index].trim() && leadingWhitespace(lines[index]).length <= parentIndent.length) {
      return index;
    }
  }
  return lines.length;
}

function findNextListItem(lines: string[], start: number, itemIndent: string): number {
  const pattern = new RegExp(`^${escapeRegExp(itemIndent)}-\\s+`);
  for (let index = start; index < lines.length; index += 1) {
    if (pattern.test(lines[index])) {
      return index;
    }
  }
  return lines.length;
}

function replaceYamlScalar(line: string, value: number): string {
  return line.replace(/^(\s*[^:]+:\s*)(.*)$/, (_match, prefix: string, current: string) => `${prefix}${formatYamlScalar(current, value)}`);
}

function replaceYamlStringScalar(line: string, value: string): string {
  return line.replace(/^(\s*[^:]+:\s*)(.*)$/, (_match, prefix: string, current: string) => `${prefix}${formatYamlStringScalar(current, value)}`);
}

function formatYamlScalar(current: string, value: number): string {
  const trimmed = current.trim();
  if (trimmed.startsWith("'") && trimmed.endsWith("'")) {
    return `'${value}'`;
  }
  if (trimmed.startsWith('"') && trimmed.endsWith('"')) {
    return `"${value}"`;
  }
  return String(value);
}

function formatYamlStringScalar(current: string, value: string): string {
  const trimmed = current.trim();
  if (trimmed.startsWith("'") && trimmed.endsWith("'")) {
    return `'${value}'`;
  }
  if (trimmed.startsWith('"') && trimmed.endsWith('"')) {
    return `"${value}"`;
  }
  return value;
}

function splitLines(text: string): string[] {
  return text.split("\n");
}

function leadingWhitespace(line: string): string {
  return line.match(/^\s*/)?.[0] ?? "";
}

function childIndentForBlock(lines: string[], start: number, end: number, parentIndent: string): string {
  const child = lines.slice(start, end).find((line) => line.trim() && leadingWhitespace(line).length > parentIndent.length);
  return child ? leadingWhitespace(child) : `${parentIndent}    `;
}

function beforeTrailingBlankLines(lines: string[], end: number): number {
  let index = Math.min(end, lines.length);
  while (index > 0 && lines[index - 1] === "") {
    index -= 1;
  }
  return index;
}

function focusListItemRange(lines: string[], focusId: string): YamlListItemRange | null {
  const idIndex = lines.findIndex((line) => focusIdLinePattern(focusId).test(line));
  if (idIndex < 0) {
    return null;
  }
  const start = containingListItemStart(lines, idIndex);
  if (start < 0) {
    return null;
  }
  const itemIndent = leadingWhitespace(lines[start]);
  const end = findNextListItem(lines, start + 1, itemIndent);
  return {
    childIndent: childIndentForBlock(lines, start + 1, end, itemIndent),
    end,
    insertAt: idIndex + 1,
    start
  };
}

function sourceFocusListItemRange(lines: string[], focusId: string): YamlListItemRange | null {
  const sourceFocusesIndex = findKeyLine(lines, "source_focuses", 0);
  if (sourceFocusesIndex < 0) {
    return null;
  }
  const sourceFocusesIndent = leadingWhitespace(lines[sourceFocusesIndex]);
  const start = sourceFocusesIndex + 1;
  const firstItem = findFirstListItemAfterKey(lines, start, sourceFocusesIndent);
  if (firstItem < 0) {
    return null;
  }
  const itemIndent = leadingWhitespace(lines[firstItem]);
  const listEnd = findListEnd(lines, firstItem + 1, itemIndent);
  const idIndex = lines.findIndex((line, index) => index >= firstItem && index < listEnd && sourceFocusIdLinePattern(focusId).test(line));
  if (idIndex < 0) {
    return null;
  }
  const itemStart = containingListItemStart(lines, idIndex);
  if (itemStart < firstItem) {
    return null;
  }
  const itemEnd = Math.min(findNextListItem(lines, itemStart + 1, itemIndent), listEnd);
  const sourcePathIndex = findKeyLine(lines, "source_path", idIndex + 1, itemEnd);
  return {
    childIndent: childIndentForBlock(lines, itemStart + 1, itemEnd, itemIndent),
    end: itemEnd,
    insertAt: sourcePathIndex >= 0 ? sourcePathIndex + 1 : idIndex + 1,
    start: itemStart
  };
}

function focusListRange(lines: string[]): { childIndent: string; end: number; itemIndent: string } | null {
  const focusesIndex = findKeyLine(lines, "focuses", 0);
  if (focusesIndex < 0) {
    return null;
  }
  const focusesIndent = leadingWhitespace(lines[focusesIndex]);
  const start = focusesIndex + 1;
  const end = findBlockEnd(lines, start, focusesIndent);
  const firstItem = findFirstListItemAfterKey(lines, start, focusesIndent);
  if (firstItem < 0) {
    const itemIndent = `${focusesIndent}    `;
    return {
      childIndent: `${itemIndent}    `,
      end,
      itemIndent
    };
  }
  const itemIndent = leadingWhitespace(lines[firstItem]);
  const listEnd = findListEnd(lines, firstItem + 1, itemIndent);
  const firstItemEnd = Math.min(findNextListItem(lines, firstItem + 1, itemIndent), listEnd);
  return {
    childIndent: childIndentForBlock(lines, firstItem + 1, firstItemEnd, itemIndent),
    end: listEnd,
    itemIndent
  };
}

function isInlineEmptyYamlList(line: string, key: string): boolean {
  return new RegExp(`^\\s*${escapeRegExp(key)}:\\s*\\[\\s*\\]\\s*$`).test(line);
}

function findListEnd(lines: string[], start: number, itemIndent: string): number {
  for (let index = start; index < lines.length; index += 1) {
    if (!lines[index].trim()) {
      continue;
    }
    const indent = leadingWhitespace(lines[index]);
    if (indent.length < itemIndent.length) {
      return index;
    }
    if (indent.length === itemIndent.length && !YAML_LIST_ITEM_PATTERN.test(lines[index])) {
      return index;
    }
  }
  return lines.length;
}

function findFirstListItemAfterKey(lines: string[], start: number, keyIndent: string): number {
  for (let index = start; index < lines.length; index += 1) {
    if (!lines[index].trim()) {
      continue;
    }
    const indent = leadingWhitespace(lines[index]);
    if (indent.length < keyIndent.length) {
      return -1;
    }
    if (YAML_LIST_ITEM_PATTERN.test(lines[index])) {
      return index;
    }
    if (indent.length <= keyIndent.length) {
      return -1;
    }
  }
  return -1;
}

function containingListItemStart(lines: string[], index: number): number {
  if (YAML_LIST_ITEM_PATTERN.test(lines[index])) {
    return index;
  }
  const indent = leadingWhitespace(lines[index]).length;
  for (let current = index - 1; current >= 0; current -= 1) {
    if (!lines[current].trim()) {
      continue;
    }
    const currentIndent = leadingWhitespace(lines[current]).length;
    if (YAML_LIST_ITEM_PATTERN.test(lines[current]) && currentIndent < indent) {
      return current;
    }
    if (currentIndent < indent) {
      return -1;
    }
  }
  return -1;
}

function focusIdLinePattern(focusId: string): RegExp {
  return new RegExp(`^\\s*(?:-\\s+)?id:\\s*['"]?${escapeRegExp(focusId)}['"]?\\s*$`);
}

function sourceFocusIdLinePattern(focusId: string): RegExp {
  return new RegExp(`^\\s*focus_id:\\s*['"]?${escapeRegExp(focusId)}['"]?\\s*$`);
}

function focusSourceInfoPath(payload: ProjectDiagramNodePayload | null | undefined, fallback?: ProjectDiagramNodePayload | null): string | undefined {
  const sourceFocusPath = cleanSourceFocusPath(payload?.sourceFocusPath) || cleanSourceFocusPath(fallback?.sourceFocusPath);
  const sourceRoot = cleanPathText(payload?.sourceRoot) || cleanPathText(fallback?.sourceRoot);
  if (!sourceFocusPath || !sourceRoot) {
    return undefined;
  }
  const relativeRoot = cleanPathText(payload?.relativeRoot) || cleanPathText(fallback?.relativeRoot);
  const sourceRootRelativePath = cleanPathText(payload?.sourceRootRelativePath) || cleanPathText(fallback?.sourceRootRelativePath);
  const modulePath = modulePathUnderSourceRoot(relativeRoot, sourceRootRelativePath);
  return joinSourcePath(sourceRoot, modulePath, "legacy", sourceFocusPath, "info.json");
}

function modulePathUnderSourceRoot(relativeRoot: string, sourceRootRelativePath: string): string {
  if (!relativeRoot || !sourceRootRelativePath) {
    return "";
  }
  if (relativeRoot === sourceRootRelativePath) {
    return "";
  }
  const prefix = `${sourceRootRelativePath}/`;
  return relativeRoot.startsWith(prefix) ? relativeRoot.slice(prefix.length) : "";
}

function cleanSourceFocusPath(value: string | undefined): string {
  const clean = cleanPathText(value).replace(/^\/+/, "").replace(/\/+$/, "");
  const withoutInfo = clean.endsWith("/info.json") ? clean.slice(0, -"/info.json".length) : clean;
  if (!withoutInfo || isSchemePath(withoutInfo) || withoutInfo.startsWith("/")) {
    return "";
  }
  const parts = withoutInfo.split("/");
  return parts.some((part) => !part || part === "." || part === "..") ? "" : parts.join("/");
}

function cleanPathText(value: string | undefined): string {
  return (value ?? "").trim().replace(/\\/g, "/").replace(/\/+$/, "");
}

function isSchemePath(value: string): boolean {
  return /^[a-z][a-z0-9+.-]*:/i.test(value);
}

function joinSourcePath(...parts: string[]): string {
  return parts
    .filter((part) => part.trim())
    .map((part, index) => (index === 0 ? part.replace(/\/+$/, "") : part.replace(/^\/+|\/+$/g, "")))
    .join("/");
}

function asProjectDiagramNodePayload(value: DiagramNode["payload"]): ProjectDiagramNodePayload | null {
  if (!value || typeof value !== "object" || Array.isArray(value)) {
    return null;
  }
  const payload = value as Partial<ProjectDiagramNodePayload>;
  return typeof payload.itemId === "string" && typeof payload.objectId === "string" ? (payload as ProjectDiagramNodePayload) : null;
}

function escapeRegExp(value: string): string {
  return value.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}
