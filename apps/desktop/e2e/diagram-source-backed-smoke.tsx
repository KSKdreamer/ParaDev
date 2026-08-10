import { useEffect, useState } from "react";
import { createRoot } from "react-dom/client";
import { createTranslator } from "../src/i18n";
import {
  sourceBackedSmokeDiagramDocument,
  sourceBackedSmokeProjectRoot,
  sourceBackedSmokeSummary
} from "../src/diagramEditor/fixtures/sourceBackedSmokeModel";
import { ProjectDiagramView } from "../src/diagramEditor/ProjectDiagramView";
import {
  moveDiagramNode,
  moveDiagramNodeKeepingDescendants,
  moveDiagramNodeRelayoutDescendants,
  moveDiagramSubtree,
  resolveDiagramLayout,
  setDiagramNodeLayoutHints,
  type DiagramDocument,
  type DiagramNodeLayoutHints
} from "../src/diagramEditor/layoutModel";
import { installSourceBackedFocusImageBridge } from "./source-backed-focus-image-bridge";
import "../src/styles/theme.css";
import "../src/styles/app.css";

const t = createTranslator("en");

const diagramDocument = sourceBackedSmokeDiagramDocument;
const movementBranchId = "FOCUS_C08_TO_THE_WAR";
const movementPlanIds = ["FOCUS_C08_PLAN_TWILIGHT", "FOCUS_C08_PLAN_STARLIGHT", "FOCUS_C08_PLAN_SUNBURST"] as const;
const movementUnaffectedId = "FOCUS_C08_THE_RISING_FIRE";
const movementDelta = { dx: 2, dy: 0 };

type SourceBackedMovementCommand = "base" | "layout-hints" | "node-only" | "relayout-descendants" | "subtree";

installSourceBackedFocusImageBridge({
  cacheWriteCount: "paradevSourceBackedImageCacheWriteCount",
  lastCommand: "paradevSourceBackedImageLastCommand",
  lastPath: "paradevSourceBackedImageLastPath",
  readCount: "paradevSourceBackedImageReadCount"
});

function DiagramSourceBackedSmoke() {
  const [selectedNodeId, setSelectedNodeId] = useState(movementBranchId);
  const [currentDocument, setCurrentDocument] = useState<DiagramDocument>(diagramDocument);
  const [command, setCommand] = useState<SourceBackedMovementCommand>("base");

  useEffect(() => {
    const root = documentElement();
    root.dataset.paradevSourceBackedNodeCount = String(sourceBackedSmokeSummary.nodeCount);
    root.dataset.paradevSourceBackedEdgeCount = String(sourceBackedSmokeSummary.edgeCount);
    root.dataset.paradevSourceBackedPreviewNodeCount = String(sourceBackedSmokeSummary.previewNodeCount);
    root.dataset.paradevSourceBackedLegacyNodeCount = String(sourceBackedSmokeSummary.legacyNodeCount);
    root.dataset.paradevSourceBackedRootIds = sourceBackedSmokeSummary.explicitRootIds.join(",");
    root.dataset.paradevSourceBackedRootCount = String(sourceBackedSmokeSummary.explicitRootIds.length);
    root.dataset.paradevSourceBackedTreeEdgeIds = sourceBackedSmokeSummary.treeEdgeIds.join(",");
    root.dataset.paradevSourceBackedDependencyEdgeIds = sourceBackedSmokeSummary.dependencyEdgeIds.join(",");
    exposeSmokeState(currentDocument, command, selectedNodeId);
  }, [command, currentDocument, selectedNodeId]);

  const handleSetLayoutHints = (nodeId: string, hints: DiagramNodeLayoutHints) => {
    setCommand("layout-hints");
    setSelectedNodeId(nodeId);
    setCurrentDocument((current) => setDiagramNodeLayoutHints(current, nodeId, hints));
  };

  return (
    <main className="diagram-source-backed-smoke">
      <header className="diagram-source-backed-smoke-status" aria-label="Source-backed diagram smoke status">
        <strong>Source-backed C08_PARTIV diagram smoke</strong>
        <span>Nodes: {sourceBackedSmokeSummary.nodeCount}</span>
        <span>Links: {sourceBackedSmokeSummary.edgeCount}</span>
        <span>Images: {sourceBackedSmokeSummary.previewNodeCount}</span>
        <button
          type="button"
          onClick={() => {
            setCommand("base");
            setSelectedNodeId(movementBranchId);
            setCurrentDocument(diagramDocument);
          }}
        >
          Reset
        </button>
        <button
          type="button"
          onClick={() => {
            setCommand("subtree");
            setCurrentDocument(moveDiagramSubtree(diagramDocument, movementBranchId, movementDelta));
          }}
        >
          Move Subtree
        </button>
        <button
          type="button"
          onClick={() => {
            setCommand("node-only");
            setCurrentDocument(moveDiagramNodeKeepingDescendants(diagramDocument, movementBranchId, movementDelta));
          }}
        >
          Move Node Only
        </button>
        <button
          type="button"
          onClick={() => {
            setCommand("relayout-descendants");
            setCurrentDocument(moveDiagramNodeRelayoutDescendants(diagramDocument, movementBranchId, movementDelta));
          }}
        >
          Relayout Descendants
        </button>
      </header>
      <ProjectDiagramView
        document={currentDocument}
        onNodeMove={(nodeId, delta) => setCurrentDocument((current) => moveDiagramNode(current, nodeId, delta))}
        onNodeMoveKeepingDescendants={(nodeId, delta) => setCurrentDocument((current) => moveDiagramNodeKeepingDescendants(current, nodeId, delta))}
        onNodeMoveRelayoutDescendants={(nodeId, delta) => setCurrentDocument((current) => moveDiagramNodeRelayoutDescendants(current, nodeId, delta))}
        onNodeMoveSubtree={(nodeId, delta) => setCurrentDocument((current) => moveDiagramSubtree(current, nodeId, delta))}
        onNodeSetLayoutHints={handleSetLayoutHints}
        onNodeSelect={setSelectedNodeId}
        projectRoot={sourceBackedSmokeProjectRoot}
        selectedNodeId={selectedNodeId}
        t={t}
        title="C08 Part IV Focuses"
      />
    </main>
  );
}

function exposeSmokeState(document: DiagramDocument, command: SourceBackedMovementCommand, selectedNodeId: string) {
  const root = documentElement();
  const baseLayout = resolveDiagramLayout(diagramDocument);
  const layout = resolveDiagramLayout(document);
  const selectedNode = document.nodes.find((node) => node.id === selectedNodeId);
  root.dataset.paradevSourceBackedMoveCommand = command;
  root.dataset.paradevSourceBackedMoveModes = document.nodes.map((node) => `${node.id}:${node.mode}`).join("|");
  root.dataset.paradevSourceBackedMovePositions = movementPositions(layout, [movementBranchId, ...movementPlanIds, movementUnaffectedId]);
  root.dataset.paradevSourceBackedMoveBranchDelta = movementDeltaText(baseLayout, layout, movementBranchId);
  root.dataset.paradevSourceBackedMoveTwilightDelta = movementDeltaText(baseLayout, layout, "FOCUS_C08_PLAN_TWILIGHT");
  root.dataset.paradevSourceBackedMoveStarlightDelta = movementDeltaText(baseLayout, layout, "FOCUS_C08_PLAN_STARLIGHT");
  root.dataset.paradevSourceBackedMoveSunburstDelta = movementDeltaText(baseLayout, layout, "FOCUS_C08_PLAN_SUNBURST");
  root.dataset.paradevSourceBackedMoveUnaffectedDelta = movementDeltaText(baseLayout, layout, movementUnaffectedId);
  root.dataset.paradevSourceBackedSelectedNodeId = selectedNodeId;
  root.dataset.paradevSourceBackedSelectedLayoutHints = selectedNode ? layoutHintText(selectedNode) : "";
}

function movementPositions(layout: ReturnType<typeof resolveDiagramLayout>, ids: string[]): string {
  return ids.map((id) => `${id}:${layout.nodesById[id]?.worldX ?? "?"},${layout.nodesById[id]?.worldY ?? "?"}`).join("|");
}

function movementDeltaText(baseLayout: ReturnType<typeof resolveDiagramLayout>, layout: ReturnType<typeof resolveDiagramLayout>, id: string): string {
  const base = baseLayout.nodesById[id];
  const node = layout.nodesById[id];
  return base && node ? `${node.worldX - base.worldX},${node.worldY - base.worldY}` : "";
}

function layoutHintText(node: DiagramDocument["nodes"][number]): string {
  return [
    `priority=${node.priority ?? ""}`,
    `w=${node.subtreeWidth ?? ""}`,
    `dw=${node.subtreeWidthDelta ?? ""}`,
    `dc=${node.subtreeCenterOffset ?? ""}`
  ].join("|");
}

function documentElement(): HTMLElement {
  return globalThis.document.documentElement;
}

const root = document.getElementById("root");

if (!root) {
  throw new Error("ParaDev source-backed diagram smoke root element was not found.");
}

const rootState = globalThis as typeof globalThis & { __paradevSourceBackedDiagramSmokeRoot?: ReturnType<typeof createRoot> };
const reactRoot = rootState.__paradevSourceBackedDiagramSmokeRoot ?? createRoot(root);
rootState.__paradevSourceBackedDiagramSmokeRoot = reactRoot;
reactRoot.render(<DiagramSourceBackedSmoke />);
