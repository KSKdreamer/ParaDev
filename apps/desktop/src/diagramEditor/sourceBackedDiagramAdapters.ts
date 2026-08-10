import type { Locale } from "../i18n";
import type {
  ModuleDiagramEdgeIntent,
  ModuleDiagramPayload,
  ModuleDiagramPositionIntent,
} from "../services/paradev";
import type {
  ProjectBrowserPayload,
  ProjectDiagramRelationship,
} from "../types";
import {
  diagramRelationshipEndpoints,
  setDiagramRelationship,
} from "./diagramRelationships";
import {
  buildDoctrineDiagramDocument,
  changedDoctrineDiagramNodeIds,
  doctrineDiagramEditIntents,
  doctrineDiagramSourcePath,
} from "./doctrineDiagram";
import {
  buildFocusTreeDiagramDocument,
  changedFocusTreeDiagramNodeIds,
  focusTreeDiagramEditIntents,
  focusTreeDiagramSourcePath,
} from "./focusTreeDiagram";
import {
  buildGenericDiagramDocument,
  changedGenericDiagramNodeIds,
  genericDiagramEditIntents,
  genericDiagramNodeSourceRevision,
  genericDiagramSourcePath,
} from "./genericDiagram";
import type { DiagramDocument } from "./layoutModel";
import {
  buildMioDiagramDocument,
  changedMioDiagramNodeIds,
  mioDiagramEditIntents,
  mioDiagramSourcePath,
} from "./mioDiagram";
import {
  buildTechnologyDiagramDocument,
  changedTechnologyDiagramNodeIds,
  technologyDiagramEditIntents,
  technologyDiagramSourcePath,
} from "./technologyDiagram";

export type SourceBackedDiagramAdapterContext = {
  browser: ProjectBrowserPayload;
  locale: Locale;
  payload: ModuleDiagramPayload;
  scopeId?: string;
};

export type SourceBackedDiagramEditIntents = {
  edgeIntents: ModuleDiagramEdgeIntent[];
  positionIntents: ModuleDiagramPositionIntent[];
};

export type SourceBackedDiagramAdapter = {
  buildDocument: (
    context: SourceBackedDiagramAdapterContext,
  ) => DiagramDocument;
  changedNodeIds: (
    context: SourceBackedDiagramAdapterContext,
    baseDocument: DiagramDocument,
    draftDocument: DiagramDocument,
  ) => string[];
  editIntents: (
    context: SourceBackedDiagramAdapterContext,
    baseDocument: DiagramDocument,
    draftDocument: DiagramDocument,
  ) => SourceBackedDiagramEditIntents;
  sourcePath: (document: DiagramDocument, id: string) => string;
  setRelationship: (
    document: DiagramDocument,
    relationship: ProjectDiagramRelationship,
    selectedNodeId: string,
    relatedNodeId: string,
    present: boolean,
  ) => DiagramDocument;
};

const setSharedDiagramRelationship: SourceBackedDiagramAdapter["setRelationship"] =
  (document, relationship, selectedNodeId, relatedNodeId, present) =>
    setDiagramRelationship(
      document,
      relationship,
      selectedNodeId,
      relatedNodeId,
      present,
    );

const SOURCE_BACKED_DIAGRAM_ADAPTERS: Readonly<
  Record<string, SourceBackedDiagramAdapter>
> = {
  doctrine: {
    buildDocument: ({ browser, payload }) =>
      buildDoctrineDiagramDocument(payload, browser),
    changedNodeIds: (_context, baseDocument, draftDocument) =>
      changedDoctrineDiagramNodeIds(baseDocument, draftDocument),
    editIntents: (_context, baseDocument, draftDocument) =>
      doctrineDiagramEditIntents(baseDocument, draftDocument),
    setRelationship: setSharedDiagramRelationship,
    sourcePath: doctrineDiagramSourcePath,
  },
  "focus-tree": {
    buildDocument: ({ browser, locale, payload }) =>
      buildFocusTreeDiagramDocument(payload, browser, locale),
    changedNodeIds: ({ payload }, baseDocument, draftDocument) =>
      changedFocusTreeDiagramNodeIds(payload, baseDocument, draftDocument),
    editIntents: ({ payload }, baseDocument, draftDocument) =>
      focusTreeDiagramEditIntents(payload, baseDocument, draftDocument),
    setRelationship: setSharedDiagramRelationship,
    sourcePath: focusTreeDiagramSourcePath,
  },
  graph: {
    buildDocument: ({ browser, locale, payload }) =>
      buildGenericDiagramDocument(payload, browser, locale),
    changedNodeIds: (_context, baseDocument, draftDocument) =>
      changedGenericDiagramNodeIds(baseDocument, draftDocument),
    editIntents: (_context, baseDocument, draftDocument) =>
      genericDiagramEditIntents(baseDocument, draftDocument),
    setRelationship: (
      document,
      relationship,
      selectedNodeId,
      relatedNodeId,
      present,
    ) => {
      const endpoints = diagramRelationshipEndpoints(
        relationship,
        selectedNodeId,
        relatedNodeId,
      );
      const ownerId =
        relationship.owner_endpoint === "target"
          ? endpoints.targetId
          : endpoints.sourceId;
      return setDiagramRelationship(
        document,
        relationship,
        selectedNodeId,
        relatedNodeId,
        present,
        present
          ? {
              sourceRevision: genericDiagramNodeSourceRevision(
                document,
                ownerId,
              ),
            }
          : undefined,
      );
    },
    sourcePath: genericDiagramSourcePath,
  },
  "mio-trait": {
    buildDocument: ({ browser, locale, payload, scopeId }) =>
      buildMioDiagramDocument(payload, browser, locale, scopeId),
    changedNodeIds: ({ payload }, baseDocument, draftDocument) =>
      changedMioDiagramNodeIds(payload, baseDocument, draftDocument),
    editIntents: ({ payload }, baseDocument, draftDocument) =>
      mioDiagramEditIntents(payload, baseDocument, draftDocument),
    setRelationship: setSharedDiagramRelationship,
    sourcePath: mioDiagramSourcePath,
  },
  technology: {
    buildDocument: ({ browser, payload }) =>
      buildTechnologyDiagramDocument(payload, browser),
    changedNodeIds: (_context, baseDocument, draftDocument) =>
      changedTechnologyDiagramNodeIds(baseDocument, draftDocument),
    editIntents: (_context, baseDocument, draftDocument) =>
      technologyDiagramEditIntents(baseDocument, draftDocument),
    setRelationship: setSharedDiagramRelationship,
    sourcePath: technologyDiagramSourcePath,
  },
};

/**
 * Resolves one desktop diagram adapter by the renderer capability advertised
 * by the active Registry provider. Project families never participate in this
 * dispatch; external providers can use the shared `graph` protocol directly.
 */
export function sourceBackedDiagramAdapter(
  renderer: string | null | undefined,
): SourceBackedDiagramAdapter | undefined {
  return renderer ? SOURCE_BACKED_DIAGRAM_ADAPTERS[renderer] : undefined;
}

export function sourceBackedDiagramRendererIds(): string[] {
  return Object.keys(SOURCE_BACKED_DIAGRAM_ADAPTERS).sort();
}
