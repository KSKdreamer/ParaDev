import { useEffect, useState } from "react";
import { createRoot } from "react-dom/client";
import { createTranslator } from "../src/i18n";
import { diagramNodeRenderedImageSideLength, ProjectDiagramView, type DiagramChangedEntity } from "../src/diagramEditor/ProjectDiagramView";
import { autoLayoutDiagramDescendants, moveDiagramNode, moveDiagramNodeKeepingDescendants, moveDiagramNodeRelayoutDescendants, moveDiagramSubtree, resolveDiagramLayout, setDiagramDependencyEdge, setDiagramNodeLayoutHints, setDiagramReferenceEdge } from "../src/diagramEditor/layoutModel";
import {
  sourceBackedSmokeProjectRoot
} from "../src/diagramEditor/fixtures/sourceBackedSmokeModel";
import { buildDiagramMetadataTextDrafts } from "../src/moduleEditor/diagramMetadata";
import { buildDiagramApplyDraftPlan, buildDiagramChangedEntities } from "../src/moduleEditor/ModuleEditor";
import {
  sourceBackedLayoutHintBaseDocument,
  sourceBackedLayoutHintEntities,
  sourceBackedLayoutHintFocusId,
  sourceBackedLayoutHintSourceEditPath,
  sourceBackedLayoutHintSourceEditText,
  sourceBackedLayoutHintSourceInfoText,
  sourceBackedRelationshipSourceEditPath,
  sourceBackedRelationshipSourceEditText,
  sourceBackedRelationshipSourceInfoText
} from "../src/moduleEditor/fixtures/sourceBackedDiagramApplySmokeModel";
import { installSourceBackedFocusImageBridge } from "./source-backed-focus-image-bridge";
import "../src/styles/theme.css";
import "../src/styles/app.css";

const t = createTranslator("en");

const diagramDocument = sourceBackedLayoutHintBaseDocument;

installSourceBackedFocusImageBridge({
  cacheWriteCount: "paradevDiagramImageCacheWriteCount",
  lastCommand: "paradevDiagramImageLastCommand",
  lastPath: "paradevDiagramImageLastPath",
  readCount: "paradevDiagramImageReadCount"
});

const changedEntities: DiagramChangedEntity[] = [
  {
    id: "focus_tree:C08_PARTIV",
    path: "src/modules/focus_tree/C08_PARTIV/meta.yaml",
    title: "Part IV"
  },
  {
    id: "focus_tree:C08_PARTIV",
    path: "src/modules/focus_tree/C08_PARTIV/legacy/C08_PLAN_TWILIGHT/info.json",
    title: "Part IV"
  },
  {
    id: "focus_tree:FOCUS_C08_PLAN_TWILIGHT",
    title: "Twilight"
  }
];

function DiagramApplyReviewSmoke() {
  const [applyCount, setApplyCount] = useState(0);
  const [currentDocument, setCurrentDocument] = useState(diagramDocument);
  const [dirty, setDirty] = useState(true);
  const [selectedNodeId, setSelectedNodeId] = useState(sourceBackedLayoutHintFocusId);
  const draftPlan = diagramApplyPlanFor(currentDocument);
  const changedEntitiesForView = draftPlan.ok || draftPlan.rows.length > 0 ? draftPlan.rows : changedEntities;

  useEffect(() => {
    const root = documentElement();
    const layout = resolveDiagramLayout(currentDocument);
    const selectedNode = layout.nodesById[selectedNodeId];
    const sourceEdit = draftPlan.ok ? draftPlan.sourceEdits[0] : undefined;
    root.dataset.paradevDiagramApplyCount = String(applyCount);
    root.dataset.paradevDiagramDirty = dirty ? "1" : "0";
    root.dataset.paradevDiagramApplyDraftPlanOk = draftPlan.ok ? "1" : "0";
    root.dataset.paradevDiagramApplyDraftPlanReason = draftPlan.ok ? "" : draftPlan.reason;
    root.dataset.paradevDiagramApplyDraftRowCount = String(draftPlan.rows.length);
    root.dataset.paradevDiagramApplyDraftRowPaths = draftPlan.rows.map((row) => row.path ?? "").join("|");
    root.dataset.paradevDiagramApplySourceEditCount = draftPlan.ok ? String(draftPlan.sourceEdits.length) : "0";
    root.dataset.paradevDiagramApplySourceEditPath = sourceEdit?.path ?? "";
    root.dataset.paradevDiagramApplyLayoutHintDraft = sourceEdit?.path === sourceBackedLayoutHintSourceEditPath && sourceEdit.text === sourceBackedLayoutHintSourceEditText ? "1" : "0";
    root.dataset.paradevDiagramApplyRelationshipDraft = sourceEdit?.path === sourceBackedRelationshipSourceEditPath && sourceEdit.text === sourceBackedRelationshipSourceEditText ? "1" : "0";
    root.dataset.paradevDiagramApplySourceEditText = sourceEdit?.text ?? "";
    root.dataset.paradevDiagramGridSizePx = String(currentDocument.gridSizePx);
    root.dataset.paradevDiagramNodeCount = String(currentDocument.nodes.length);
    root.dataset.paradevDiagramFocusSlotCount = String(currentDocument.nodes.filter((node) => node.width === 1 && node.height === 1).length);
    root.dataset.paradevDiagramPreviewNodeCount = String(currentDocument.nodes.filter((node) => node.imageUrl?.endsWith("/preview.png")).length);
    root.dataset.paradevDiagramLegacyImageNodeCount = String(currentDocument.nodes.filter((node) => node.imageUrl?.includes("/legacy/focuses/") || node.imageUrl?.endsWith("/default.png")).length);
    const expectedFocusNode = currentDocument.nodes.find((node) => node.id === "FOCUS_C08_CANTERLOT_MIND") ?? currentDocument.nodes[0];
    root.dataset.paradevDiagramExpectedFocusImagePx = String(
      diagramNodeRenderedImageSideLength(
        {
          height: expectedFocusNode?.height ?? 1,
          payload: expectedFocusNode?.payload,
          width: expectedFocusNode?.width ?? 1
        },
        currentDocument.gridSizePx
      )
    );
    root.dataset.paradevDiagramSelectedNodePosition = selectedNode ? `${selectedNode.worldX},${selectedNode.worldY},${selectedNode.width},${selectedNode.height}` : "";
  }, [applyCount, currentDocument, dirty, draftPlan, selectedNodeId]);

  return (
    <main className="diagram-apply-smoke">
      <header className="diagram-apply-smoke-status" aria-label="Diagram apply smoke status">
        <strong>Diagram apply review smoke</strong>
        <span data-paradev-smoke-apply-count="">Apply calls: {applyCount}</span>
        <span data-paradev-smoke-dirty-state="">{dirty ? "Dirty" : "Clean"}</span>
      </header>
      <ProjectDiagramView
        diagramChangedEntities={dirty ? changedEntitiesForView : []}
        diagramDirty={dirty}
        document={currentDocument}
        onDiagramAutoLayout={() => setCurrentDocument((current) => autoLayoutDiagramDescendants(current, "FOCUS_C08_CANTERLOT_MIND"))}
        onDiagramApply={() => {
          setApplyCount((count) => count + 1);
          setDirty(false);
        }}
        onNodeAddDependency={(targetId, sourceId) => {
          setDirty(true);
          setSelectedNodeId(targetId);
          setCurrentDocument((current) => setDiagramDependencyEdge(current, sourceId, targetId, true));
        }}
        onNodeAddReference={(sourceId, targetId) => {
          setDirty(true);
          setSelectedNodeId(sourceId);
          setCurrentDocument((current) => setDiagramReferenceEdge(current, sourceId, targetId, true));
        }}
        onNodeAddUnlock={(sourceId, targetId) => {
          setDirty(true);
          setSelectedNodeId(sourceId);
          setCurrentDocument((current) => setDiagramDependencyEdge(current, sourceId, targetId, true));
        }}
        onNodeMove={(nodeId, delta) => setCurrentDocument((current) => moveDiagramNode(current, nodeId, delta))}
        onNodeMoveKeepingDescendants={(nodeId, delta) => setCurrentDocument((current) => moveDiagramNodeKeepingDescendants(current, nodeId, delta))}
        onNodeMoveRelayoutDescendants={(nodeId, delta) => setCurrentDocument((current) => moveDiagramNodeRelayoutDescendants(current, nodeId, delta))}
        onNodeMoveSubtree={(nodeId, delta) => setCurrentDocument((current) => moveDiagramSubtree(current, nodeId, delta))}
        onNodeRemoveDependency={(targetId, sourceId) => {
          setDirty(true);
          setSelectedNodeId(targetId);
          setCurrentDocument((current) => setDiagramDependencyEdge(current, sourceId, targetId, false));
        }}
        onNodeRemoveReference={(sourceId, targetId) => {
          setDirty(true);
          setSelectedNodeId(sourceId);
          setCurrentDocument((current) => setDiagramReferenceEdge(current, sourceId, targetId, false));
        }}
        onNodeRemoveUnlock={(sourceId, targetId) => {
          setDirty(true);
          setSelectedNodeId(sourceId);
          setCurrentDocument((current) => setDiagramDependencyEdge(current, sourceId, targetId, false));
        }}
        onNodeSelect={setSelectedNodeId}
        onNodeSetLayoutHints={(nodeId, hints) => {
          setDirty(true);
          setSelectedNodeId(nodeId);
          setCurrentDocument((current) => setDiagramNodeLayoutHints(current, nodeId, hints));
        }}
        projectRoot={sourceBackedSmokeProjectRoot}
        selectedNodeId={selectedNodeId}
        t={t}
        title="Focuses"
      />
    </main>
  );
}

function diagramApplyPlanFor(document: typeof diagramDocument) {
  const rows = buildDiagramChangedEntities(diagramDocument, document, sourceBackedLayoutHintEntities);
  const drafts = buildDiagramMetadataTextDrafts({
    baseDocument: diagramDocument,
    draftDocument: document,
    entities: sourceBackedLayoutHintEntities,
    metadataTextByEntityId: {},
    sourceTextByPath: {
      [sourceBackedLayoutHintSourceEditPath]: sourceBackedLayoutHintSourceInfoText,
      [sourceBackedRelationshipSourceEditPath]: sourceBackedRelationshipSourceInfoText
    }
  });
  return buildDiagramApplyDraftPlan(rows, drafts, sourceBackedLayoutHintEntities);
}

function documentElement(): HTMLElement {
  return globalThis.document.documentElement;
}

const root = document.getElementById("root");

if (!root) {
  throw new Error("ParaDev diagram apply smoke root element was not found.");
}

const rootState = globalThis as typeof globalThis & { __paradevDiagramApplySmokeRoot?: ReturnType<typeof createRoot> };
const reactRoot = rootState.__paradevDiagramApplySmokeRoot ?? createRoot(root);
rootState.__paradevDiagramApplySmokeRoot = reactRoot;
reactRoot.render(<DiagramApplyReviewSmoke />);
