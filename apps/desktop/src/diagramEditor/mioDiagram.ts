import type { Locale } from "../i18n";
import type {
  MioModuleDiagramEdgeIntent,
  MioModuleDiagramPositionIntent,
  ModuleDiagramEdge,
  ModuleDiagramNode,
  ModuleDiagramPayload,
} from "../services/paradev";
import type { ProjectBrowserItem, ProjectBrowserPayload } from "../types";
import type {
  DiagramDocument,
  DiagramEdge,
  DiagramEdgeKind,
  DiagramNode,
} from "./layoutModel";

export const MIO_DIAGRAM_GRID_SIZE_PX = 48;

const MIO_PROVIDER_SCHEMA = "paradev.hoi4.mio-trait-diagram-projection.v1";
const MIO_SOURCE_FAMILY = "military_industrial_organization";
const MIO_ORGANIZATION_GAP = 4;
const MIO_MINIMUM_ORGANIZATION_WIDTH = 4;

type MioDiagramNodeRow = ModuleDiagramNode & {
  kind: "initial_trait" | "trait";
  organization_id: string;
  source_path: string;
  source_revision: string;
  trait_id: string;
};

type MioDiagramNodePayload = {
  projectId: string;
  itemId: string;
  itemKind: "module";
  familyId: "military-industrial-organizations";
  family: typeof MIO_SOURCE_FAMILY;
  objectId: string;
  moduleId?: string;
  relativeRoot: string;
  sourceRoot?: string;
  sourcePath: string;
  sourceRevision: string;
  organizationId: string;
  organizationTitle: string;
  organizationOffsetX: number;
  traitId: string;
  traitKind: MioDiagramNodeRow["kind"];
  editable: boolean;
  relativePositionId?: string;
  nameKey: string;
  token?: string;
  icon?: string;
};

type GridPosition = {
  x: number;
  y: number;
};

type OrganizationLayout = {
  offsetX: number;
  positions: Map<string, GridPosition>;
};

export type MioDiagramEditIntents = {
  positionIntents: MioModuleDiagramPositionIntent[];
  edgeIntents: MioModuleDiagramEdgeIntent[];
};

export type MioDiagramOrganizationOption = {
  id: string;
  moduleId: string;
  title: string;
};

export function mioDiagramOrganizationOptions(
  payload: ModuleDiagramPayload,
  locale: Locale,
  moduleId = "",
): MioDiagramOrganizationOption[] {
  assertMioDiagramPayload(payload);
  const titles = organizationTitleById(payload.organizations, locale);
  const organizationIdsWithTraits = new Set(
    payload.nodes.filter(isMioDiagramNodeRow).map((row) => row.organization_id),
  );
  const options = (payload.organizations ?? [])
    .map((row): MioDiagramOrganizationOption | null => {
      const id = cleanText(row.organization_id) || cleanText(row.id);
      if (!id) {
        return null;
      }
      return {
        id,
        moduleId: cleanText(row.module_id),
        title: titles.get(id) ?? titleFromIdentifier(id),
      };
    })
    .filter(
      (row): row is MioDiagramOrganizationOption =>
        row !== null && organizationIdsWithTraits.has(row.id),
    )
    .sort((left, right) => left.id.localeCompare(right.id));
  const requestedModuleId = cleanText(moduleId);
  if (!requestedModuleId) {
    return options;
  }
  const owned = options.filter((row) => row.moduleId === requestedModuleId);
  return owned;
}

export function buildMioDiagramDocument(
  payload: ModuleDiagramPayload,
  browser: ProjectBrowserPayload,
  locale: Locale,
  organizationId?: string,
): DiagramDocument {
  assertMioDiagramPayload(payload);
  const allRows = payload.nodes
    .filter(isMioDiagramNodeRow)
    .sort(compareMioNodes);
  const organizationScopeRequested = organizationId !== undefined;
  const requestedOrganizationId = cleanText(organizationId);
  const knownOrganizationIds = new Set([
    ...(payload.organizations ?? []).map(
      (row) => cleanText(row.organization_id) || cleanText(row.id),
    ),
    ...allRows.map((row) => row.organization_id),
  ]);
  if (
    requestedOrganizationId &&
    !knownOrganizationIds.has(requestedOrganizationId)
  ) {
    throw new Error(
      `MIO organization ${requestedOrganizationId} is not present in the exact-source diagram payload.`,
    );
  }
  const rows = organizationScopeRequested
    ? allRows.filter((row) => row.organization_id === requestedOrganizationId)
    : allRows;
  const duplicateNodeId = firstDuplicate(rows.map((row) => row.id));
  if (duplicateNodeId) {
    throw new Error(
      `MIO diagram contains duplicate trait id ${duplicateNodeId}.`,
    );
  }
  const nodeIds = new Set(rows.map((row) => row.id));
  const relativeParentByNode = new Map(
    payload.edges
      .filter(
        (edge) =>
          edge.kind === "relative_position" &&
          nodeIds.has(edge.source) &&
          nodeIds.has(edge.target),
      )
      .map((edge) => [edge.target, edge.source]),
  );
  const organizationLayouts = layoutOrganizations(rows, relativeParentByNode);
  const organizationTitles = organizationTitleById(
    payload.organizations,
    locale,
  );
  const browserItems = moduleBrowserItems(browser);
  const nodes = rows.map((row, order): DiagramNode => {
    const layout = organizationLayouts.get(row.organization_id);
    const resolvedPosition = layout?.positions.get(row.id) ?? {
      x: order,
      y: 0,
    };
    const authoredPosition = finitePosition(row.position);
    const relativeParentId = relativeParentByNode.get(row.id);
    const relative =
      Boolean(relativeParentId) &&
      nodeIds.has(relativeParentId as string) &&
      authoredPosition !== null;
    const organizationOffsetX = layout?.offsetX ?? 0;
    const item = browserItemForMioNode(browserItems, row);
    const moduleId = cleanText(item?.module_id) || cleanText(row.module_id);
    const objectId =
      cleanText(item?.object_id) || moduleId || row.organization_id;
    const relativeRoot =
      cleanText(item?.relative_root) || sourceDirectory(row.source_path);
    const organizationTitle =
      organizationTitles.get(row.organization_id) ??
      titleFromIdentifier(row.organization_id);
    return {
      id: row.id,
      ...(relative ? { parentId: relativeParentId as string } : {}),
      order,
      mode: relative ? "relative" : "absolute",
      ...(relative && authoredPosition
        ? {
            dx: authoredPosition.x,
            dy: authoredPosition.y,
            relativePositionKind: "relative_position_id" as const,
          }
        : {
            fixed: true,
            x: resolvedPosition.x + organizationOffsetX,
            y: resolvedPosition.y,
          }),
      width: 1,
      height: 1,
      title:
        localizedTitle(row.localized_titles, locale) ||
        cleanText(row.name_key) ||
        cleanText(row.token) ||
        titleFromIdentifier(row.id),
      payload: {
        projectId: payload.project_id,
        itemId:
          cleanText(item?.id) || moduleId || `module:${row.organization_id}`,
        itemKind: "module",
        familyId: "military-industrial-organizations",
        family: MIO_SOURCE_FAMILY,
        objectId,
        ...(moduleId ? { moduleId } : {}),
        relativeRoot,
        ...(item?.source_root ? { sourceRoot: item.source_root } : {}),
        sourcePath: row.source_path,
        sourceRevision: row.source_revision,
        organizationId: row.organization_id,
        organizationTitle,
        organizationOffsetX,
        traitId: row.trait_id,
        traitKind: row.kind,
        editable: row.editable === true,
        ...(relativeParentId ? { relativePositionId: relativeParentId } : {}),
        nameKey: cleanText(row.name_key) || cleanText(row.token) || row.id,
        ...(cleanText(row.token) ? { token: cleanText(row.token) } : {}),
        ...(cleanText(row.icon) ? { icon: cleanText(row.icon) } : {}),
      } satisfies MioDiagramNodePayload,
    };
  });
  return {
    schemaVersion: 1,
    gridSizePx: MIO_DIAGRAM_GRID_SIZE_PX,
    nodes,
    edges: mioDiagramEdges(payload.edges, nodeIds, locale),
  };
}

export function mioDiagramEditIntents(
  payload: ModuleDiagramPayload,
  baseDocument: DiagramDocument,
  draftDocument: DiagramDocument,
): MioDiagramEditIntents {
  assertMioDiagramPayload(payload);
  const baseNodes = mioNodeMap(baseDocument);
  const draftNodes = mioNodeMap(draftDocument);
  if (
    baseNodes.size !== draftNodes.size ||
    [...baseNodes].some(([id]) => !draftNodes.has(id))
  ) {
    throw new Error(
      "MIO diagram edits cannot add or remove traits; edit the module source instead.",
    );
  }
  assertMioNonRelationshipEdgesUnchanged(baseDocument, draftDocument);
  const positionIntents: MioModuleDiagramPositionIntent[] = [];
  for (const [id, baseNode] of [...baseNodes].sort(([left], [right]) =>
    left.localeCompare(right),
  )) {
    const draftNode = draftNodes.get(id);
    if (!draftNode) {
      continue;
    }
    const source = mioNodePayload(baseNode);
    if (!source) {
      throw new Error(`MIO trait ${id} has no authoritative source identity.`);
    }
    assertMioNodeStructureUnchanged(baseNode, draftNode);
    const basePosition = mioAuthoredPosition(baseNode, source);
    const draftPosition = mioAuthoredPosition(draftNode, source);
    if (
      !draftPosition ||
      (basePosition &&
        basePosition.x === draftPosition.x &&
        basePosition.y === draftPosition.y)
    ) {
      continue;
    }
    if (!source.editable) {
      throw new Error(
        `MIO trait ${source.traitId} has no unambiguous editable source position.`,
      );
    }
    positionIntents.push({
      organization_id: source.organizationId,
      trait_id: source.traitId,
      x: draftPosition.x,
      y: draftPosition.y,
      source_revision: source.sourceRevision,
    });
  }
  const baseEdges = editableMioEdges(baseDocument);
  const draftEdges = editableMioEdges(draftDocument);
  const edgeIntents: MioModuleDiagramEdgeIntent[] = [];
  for (const key of [
    ...new Set([...baseEdges.keys(), ...draftEdges.keys()]),
  ].sort()) {
    const baseEdge = baseEdges.get(key);
    const draftEdge = draftEdges.get(key);
    if (Boolean(baseEdge) === Boolean(draftEdge)) {
      continue;
    }
    const edge = draftEdge ?? baseEdge;
    if (!edge || !isEditableMioRelationshipKind(edge.relationshipKind)) {
      continue;
    }
    const source = mioNodePayload(baseNodes.get(edge.source));
    const target = mioNodePayload(baseNodes.get(edge.target));
    if (!source || !target || source.organizationId !== target.organizationId) {
      throw new Error(
        `MIO relation ${edge.source} -> ${edge.target} must stay inside one reviewed organization.`,
      );
    }
    if (!target.editable) {
      throw new Error(
        `MIO trait ${target.traitId} has no unambiguous editable relationship source.`,
      );
    }
    edgeIntents.push({
      kind: edge.relationshipKind,
      organization_id: target.organizationId,
      present: Boolean(draftEdge),
      source_id: source.traitId,
      source_revision: target.sourceRevision,
      target_id: target.traitId,
    });
  }
  return { positionIntents, edgeIntents };
}

export function changedMioDiagramNodeIds(
  payload: ModuleDiagramPayload,
  baseDocument: DiagramDocument | null,
  draftDocument: DiagramDocument | null,
): string[] {
  if (!baseDocument || !draftDocument) {
    return [];
  }
  const intents = mioDiagramEditIntents(payload, baseDocument, draftDocument);
  return [
    ...new Set([
      ...intents.positionIntents
        .map((intent) =>
          mioNodeId(intent.organization_id, intent.trait_id, baseDocument),
        )
        .filter((id): id is string => Boolean(id)),
      ...intents.edgeIntents.flatMap((intent) =>
        [
          mioNodeId(intent.organization_id, intent.source_id, baseDocument),
          mioNodeId(intent.organization_id, intent.target_id, baseDocument),
        ].filter((id): id is string => Boolean(id)),
      ),
    ]),
  ].sort();
}

export function mioDiagramSourcePath(
  document: DiagramDocument,
  nodeId: string,
): string {
  return (
    mioNodePayload(document.nodes.find((node) => node.id === nodeId))
      ?.sourcePath ?? ""
  );
}

export function mioDiagramNodeEditable(
  document: DiagramDocument,
  nodeId: string,
): boolean {
  return (
    mioNodePayload(document.nodes.find((node) => node.id === nodeId))
      ?.editable === true
  );
}

function assertMioDiagramPayload(payload: ModuleDiagramPayload): void {
  if (
    payload.provider_schema !== MIO_PROVIDER_SCHEMA ||
    payload.family !== MIO_SOURCE_FAMILY ||
    payload.source_kind !== "module_pdx_source"
  ) {
    throw new Error(
      "MIO diagram payload does not match the authoritative exact-source provider.",
    );
  }
}

function mioNodeMap(document: DiagramDocument): Map<string, DiagramNode> {
  const rows = new Map(document.nodes.map((node) => [node.id, node]));
  if (rows.size !== document.nodes.length) {
    throw new Error("MIO diagram trait ids must be unique.");
  }
  return rows;
}

function assertMioNodeStructureUnchanged(
  baseNode: DiagramNode,
  draftNode: DiagramNode,
): void {
  const base = mioNodePayload(baseNode);
  const draft = mioNodePayload(draftNode);
  if (
    !base ||
    !draft ||
    baseNode.mode !== draftNode.mode ||
    (baseNode.parentId ?? null) !== (draftNode.parentId ?? null) ||
    baseNode.relativePositionKind !== draftNode.relativePositionKind ||
    base.organizationId !== draft.organizationId ||
    base.traitId !== draft.traitId ||
    base.sourcePath !== draft.sourcePath ||
    base.sourceRevision !== draft.sourceRevision
  ) {
    throw new Error(
      `MIO trait ${baseNode.id} source scope or relative_position_id cannot be changed from the diagram editor.`,
    );
  }
}

function mioAuthoredPosition(
  node: DiagramNode,
  payload: MioDiagramNodePayload,
): GridPosition | null {
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
    return {
      x: node.x - payload.organizationOffsetX,
      y: node.y,
    };
  }
  return null;
}

function mioDiagramEdgeKey(edge: DiagramEdge): string {
  return `${edge.kind}\u0000${edge.relationshipKind ?? ""}\u0000${edge.source}\u0000${edge.target}\u0000${relationshipGroupKey(edge.relationshipGroups)}`;
}

function editableMioEdges(document: DiagramDocument): Map<string, DiagramEdge> {
  return new Map(
    document.edges
      .filter((edge) => isEditableMioRelationshipKind(edge.relationshipKind))
      .map((edge) => [mioDiagramEdgeKey(edge), edge]),
  );
}

function assertMioNonRelationshipEdgesUnchanged(
  baseDocument: DiagramDocument,
  draftDocument: DiagramDocument,
): void {
  const base = new Set(
    baseDocument.edges
      .filter((edge) => !isEditableMioRelationshipKind(edge.relationshipKind))
      .map(mioDiagramEdgeKey),
  );
  const draft = new Set(
    draftDocument.edges
      .filter((edge) => !isEditableMioRelationshipKind(edge.relationshipKind))
      .map(mioDiagramEdgeKey),
  );
  if (base.size !== draft.size || [...base].some((key) => !draft.has(key))) {
    throw new Error(
      "MIO relationships must use a provider-declared reviewed relationship action.",
    );
  }
}

function isEditableMioRelationshipKind(
  kind: string | undefined,
): kind is MioModuleDiagramEdgeIntent["kind"] {
  return (
    kind === "relative_position" ||
    kind === "any_parent" ||
    kind === "all_parent" ||
    kind === "mutually_exclusive"
  );
}

function mioNodePayload(
  node: DiagramNode | undefined,
): MioDiagramNodePayload | null {
  if (
    !node?.payload ||
    typeof node.payload !== "object" ||
    Array.isArray(node.payload)
  ) {
    return null;
  }
  const payload = node.payload as Partial<MioDiagramNodePayload>;
  return payload.family === MIO_SOURCE_FAMILY &&
    typeof payload.organizationId === "string" &&
    typeof payload.traitId === "string" &&
    typeof payload.sourcePath === "string" &&
    typeof payload.sourceRevision === "string" &&
    typeof payload.organizationOffsetX === "number" &&
    Number.isFinite(payload.organizationOffsetX) &&
    typeof payload.editable === "boolean"
    ? (payload as MioDiagramNodePayload)
    : null;
}

function mioNodeId(
  organizationId: string,
  traitId: string,
  document: DiagramDocument,
): string | null {
  const node = document.nodes.find((candidate) => {
    const payload = mioNodePayload(candidate);
    return (
      payload?.organizationId === organizationId && payload.traitId === traitId
    );
  });
  return node?.id ?? null;
}

function isMioDiagramNodeRow(row: ModuleDiagramNode): row is MioDiagramNodeRow {
  return (
    Boolean(cleanText(row.id)) &&
    (row.kind === "initial_trait" || row.kind === "trait") &&
    Boolean(cleanText(row.organization_id)) &&
    Boolean(cleanText(row.source_path)) &&
    Boolean(cleanText(row.source_revision)) &&
    Boolean(cleanText(row.trait_id))
  );
}

function compareMioNodes(
  left: MioDiagramNodeRow,
  right: MioDiagramNodeRow,
): number {
  return (
    left.organization_id.localeCompare(right.organization_id) ||
    traitKindOrder(left.kind) - traitKindOrder(right.kind) ||
    left.id.localeCompare(right.id)
  );
}

function traitKindOrder(kind: MioDiagramNodeRow["kind"]): number {
  return kind === "initial_trait" ? 0 : 1;
}

function layoutOrganizations(
  rows: MioDiagramNodeRow[],
  relativeParentByNode: Map<string, string>,
): Map<string, OrganizationLayout> {
  const rowsByOrganization = new Map<string, MioDiagramNodeRow[]>();
  for (const row of rows) {
    const organizationRows = rowsByOrganization.get(row.organization_id) ?? [];
    organizationRows.push(row);
    rowsByOrganization.set(row.organization_id, organizationRows);
  }
  const layouts = new Map<string, OrganizationLayout>();
  let nextOffsetX = 0;
  for (const organizationId of [...rowsByOrganization.keys()].sort()) {
    const organizationRows = rowsByOrganization.get(organizationId) ?? [];
    const positions = organizationNodePositions(
      organizationRows,
      relativeParentByNode,
    );
    const xValues = [...positions.values()].map((position) => position.x);
    const minX = xValues.length > 0 ? Math.min(...xValues) : 0;
    const maxX = xValues.length > 0 ? Math.max(...xValues) : 0;
    const width = Math.max(MIO_MINIMUM_ORGANIZATION_WIDTH, maxX - minX + 1);
    layouts.set(organizationId, {
      offsetX: nextOffsetX - minX,
      positions,
    });
    nextOffsetX += width + MIO_ORGANIZATION_GAP;
  }
  return layouts;
}

function organizationNodePositions(
  rows: MioDiagramNodeRow[],
  relativeParentByNode: Map<string, string>,
): Map<string, GridPosition> {
  const rowsById = new Map(rows.map((row) => [row.id, row]));
  const resolved = new Map<string, GridPosition>();
  const resolving = new Set<string>();
  const fallbackById = new Map(
    rows.map((row, index) => [row.id, fallbackMioPosition(row, index)]),
  );

  const resolve = (nodeId: string): GridPosition => {
    const cached = resolved.get(nodeId);
    if (cached) {
      return cached;
    }
    const row = rowsById.get(nodeId);
    const fallback = fallbackById.get(nodeId) ?? {
      x: 0,
      y: 0,
    };
    if (!row || resolving.has(nodeId)) {
      return fallback;
    }
    resolving.add(nodeId);
    const local = finitePosition(row.position) ?? fallback;
    const parentId = relativeParentByNode.get(nodeId);
    const parent =
      parentId && rowsById.has(parentId) ? resolve(parentId) : null;
    const position = parent
      ? {
          x: parent.x + local.x,
          y: parent.y + local.y,
        }
      : local;
    resolving.delete(nodeId);
    resolved.set(nodeId, position);
    return position;
  };

  for (const row of rows) {
    resolve(row.id);
  }
  return resolved;
}

function fallbackMioPosition(
  row: MioDiagramNodeRow,
  index: number,
): GridPosition {
  if (row.kind === "initial_trait") {
    return { x: 0, y: -2 - index };
  }
  return { x: index * 2, y: 0 };
}

function finitePosition(
  value: ModuleDiagramNode["position"],
): GridPosition | null {
  if (
    !value ||
    typeof value.x !== "number" ||
    !Number.isFinite(value.x) ||
    typeof value.y !== "number" ||
    !Number.isFinite(value.y)
  ) {
    return null;
  }
  return { x: value.x, y: value.y };
}

function mioDiagramEdges(
  rows: ModuleDiagramEdge[],
  nodeIds: Set<string>,
  locale: Locale,
): DiagramEdge[] {
  const byRelationship = new Map<string, DiagramEdge>();
  for (const row of [...rows].sort(compareMioEdges)) {
    const kind = diagramEdgeKind(row.kind);
    if (
      !kind ||
      !nodeIds.has(row.source) ||
      !nodeIds.has(row.target) ||
      row.source === row.target
    ) {
      continue;
    }
    const key = `${row.kind}\u0000${row.source}\u0000${row.target}`;
    const relationshipGroups = mioRelationshipGroups(row);
    byRelationship.set(key, {
      id: `${row.kind}:${row.source}->${row.target}`,
      kind,
      label: mioRelationshipLabel(row.kind, locale, relationshipGroups),
      relationshipKind: row.kind,
      ...(relationshipGroups.length > 0 ? { relationshipGroups } : {}),
      source: row.source,
      target: row.target,
    });
  }
  return [...byRelationship.values()].sort(
    (left, right) =>
      diagramEdgeOrder(left.kind) - diagramEdgeOrder(right.kind) ||
      mioRelationshipOrder(left.relationshipKind) -
        mioRelationshipOrder(right.relationshipKind) ||
      left.source.localeCompare(right.source) ||
      left.target.localeCompare(right.target),
  );
}

function mioRelationshipLabel(
  kind: ModuleDiagramEdge["kind"],
  locale: Locale,
  groups: NonNullable<DiagramEdge["relationshipGroups"]>,
): string {
  const labels =
    locale === "zh"
      ? {
          all_parent: "全部前置",
          any_parent: "任一前置",
          mutually_exclusive: "互斥",
          relative_position: "相对位置",
        }
      : {
          all_parent: "All parents",
          any_parent: "Any parent",
          mutually_exclusive: "Mutually exclusive",
          relative_position: "Relative position",
        };
  const label = labels[kind as keyof typeof labels] ?? kind;
  if (groups.length === 0) {
    return label;
  }
  const groupNumbers = [
    ...new Set(groups.map((group) => group.groupIndex + 1)),
  ].sort((left, right) => left - right);
  const groupLabel =
    groupNumbers.length === 1
      ? locale === "zh"
        ? `第 ${groupNumbers[0]} 组`
        : `group ${groupNumbers[0]}`
      : locale === "zh"
        ? `第 ${groupNumbers.join("、")} 组`
        : `groups ${groupNumbers.join(", ")}`;
  return `${label} · ${groupLabel}`;
}

function mioRelationshipGroups(
  row: ModuleDiagramEdge,
): NonNullable<DiagramEdge["relationshipGroups"]> {
  const groups = (row.relation_groups ?? [])
    .map((group) => ({
      ownerId: cleanText(group.owner_id),
      groupIndex: group.group_index,
    }))
    .filter(
      (group) =>
        Boolean(group.ownerId) &&
        Number.isSafeInteger(group.groupIndex) &&
        group.groupIndex >= 0,
    );
  const unique = new Map(
    groups.map((group) => [`${group.ownerId}\u0000${group.groupIndex}`, group]),
  );
  return [...unique.values()].sort(
    (left, right) =>
      left.ownerId.localeCompare(right.ownerId) ||
      left.groupIndex - right.groupIndex,
  );
}

function relationshipGroupKey(
  groups: DiagramEdge["relationshipGroups"],
): string {
  return (groups ?? [])
    .map((group) => `${group.ownerId}\u0000${group.groupIndex}`)
    .sort()
    .join("\u0001");
}

function mioRelationshipOrder(kind: string | undefined): number {
  if (kind === "relative_position") {
    return 0;
  }
  if (kind === "all_parent") {
    return 1;
  }
  if (kind === "any_parent") {
    return 2;
  }
  if (kind === "mutually_exclusive") {
    return 3;
  }
  return 4;
}

function compareMioEdges(
  left: ModuleDiagramEdge,
  right: ModuleDiagramEdge,
): number {
  return (
    mioEdgeOrder(left.kind) - mioEdgeOrder(right.kind) ||
    left.source.localeCompare(right.source) ||
    left.target.localeCompare(right.target) ||
    left.id.localeCompare(right.id)
  );
}

function diagramEdgeKind(
  kind: ModuleDiagramEdge["kind"],
): DiagramEdgeKind | null {
  if (kind === "relative_position") {
    return "tree";
  }
  if (kind === "any_parent" || kind === "all_parent") {
    return "dependency";
  }
  if (kind === "mutually_exclusive") {
    return "reference";
  }
  return null;
}

function mioEdgeOrder(kind: ModuleDiagramEdge["kind"]): number {
  if (kind === "relative_position") {
    return 0;
  }
  if (kind === "all_parent") {
    return 1;
  }
  if (kind === "any_parent") {
    return 2;
  }
  if (kind === "mutually_exclusive") {
    return 3;
  }
  return 4;
}

function diagramEdgeOrder(kind: DiagramEdgeKind): number {
  if (kind === "tree") {
    return 0;
  }
  if (kind === "dependency") {
    return 1;
  }
  if (kind === "reference") {
    return 2;
  }
  return 3;
}

function organizationTitleById(
  rows: Array<Record<string, unknown>> | undefined,
  locale: Locale,
): Map<string, string> {
  const titles = new Map<string, string>();
  for (const row of rows ?? []) {
    const organizationId = cleanText(row.organization_id) || cleanText(row.id);
    if (!organizationId) {
      continue;
    }
    titles.set(
      organizationId,
      localizedTitle(row.localized_titles, locale) ||
        cleanText(row.name_key) ||
        titleFromIdentifier(organizationId),
    );
  }
  return titles;
}

function localizedTitle(value: unknown, locale: Locale): string {
  if (!value || typeof value !== "object" || Array.isArray(value)) {
    return "";
  }
  const rows = Object.entries(value)
    .filter(
      (row): row is [string, string] =>
        typeof row[1] === "string" && Boolean(row[1].trim()),
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

function moduleBrowserItems(
  browser: ProjectBrowserPayload,
): ProjectBrowserItem[] {
  return browser.items
    .filter((item) => item.kind === "module")
    .sort(
      (left, right) =>
        right.relative_root.length - left.relative_root.length ||
        left.id.localeCompare(right.id),
    );
}

function browserItemForMioNode(
  items: ProjectBrowserItem[],
  row: MioDiagramNodeRow,
): ProjectBrowserItem | undefined {
  const moduleId = cleanText(row.module_id);
  const exact = moduleId
    ? items.find((item) =>
        [
          item.id,
          item.module_id,
          item.object_id,
          `${item.family}/${item.object_id}`,
        ].includes(moduleId),
      )
    : undefined;
  if (exact) {
    return exact;
  }
  const sourcePath = cleanText(row.source_path);
  return items.find((item) => {
    const relativeRoot = cleanText(item.relative_root);
    return (
      Boolean(relativeRoot) &&
      (sourcePath === relativeRoot || sourcePath.startsWith(`${relativeRoot}/`))
    );
  });
}

function sourceDirectory(path: string): string {
  const clean = path.replace(/\\/g, "/").replace(/\/+$/, "");
  const separator = clean.lastIndexOf("/");
  return separator > 0 ? clean.slice(0, separator) : clean;
}

function titleFromIdentifier(identifier: string): string {
  const leaf = identifier.split("::").at(-1) ?? identifier;
  return leaf.replace(/[-_]+/g, " ").replace(/\s+/g, " ").trim() || identifier;
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

function finiteNumber(value: unknown): value is number {
  return typeof value === "number" && Number.isFinite(value);
}

function cleanText(value: unknown): string {
  return typeof value === "string" ? value.trim() : "";
}
