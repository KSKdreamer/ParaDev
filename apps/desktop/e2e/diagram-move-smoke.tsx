import { useEffect, useState } from "react";
import { createRoot } from "react-dom/client";
import { ProjectDiagramView } from "../src/diagramEditor/ProjectDiagramView";
import { createTranslator } from "../src/i18n";
import { moveDiagramNode, moveDiagramNodeKeepingDescendants, moveDiagramNodeRelayoutDescendants, moveDiagramSubtree, resolveDiagramLayout, type DiagramDocument } from "../src/diagramEditor/layoutModel";
import { sourceBackedSmokeProjectRoot } from "../src/diagramEditor/fixtures/sourceBackedSmokeModel";
import { installSourceBackedFocusImageBridge } from "./source-backed-focus-image-bridge";
import "../src/styles/theme.css";
import "../src/styles/app.css";

const t = createTranslator("en");
const moveDelta = { dx: 2, dy: 0 };
const focusRootId = "FOCUS_C08_CANTERLOT_MIND";
const focusBranchId = "FOCUS_C08_SECOND_SUMMIT";
const relativeLeafId = "FOCUS_C08_TO_THE_WAR";
const autoLeafId = "FOCUS_C08_PLAN_TWILIGHT";
const absoluteLeafId = "FOCUS_C08_PLAN_STARLIGHT";
const siblingId = "FOCUS_C08_PLAN_SUNBURST";

type MovementCommand = "base" | "subtree" | "node-only" | "relayout-descendants";

installSourceBackedFocusImageBridge();

function focusPayload(id: string) {
  return {
    embeddedId: id,
    embeddedKind: "focus" as const,
    itemId: "focus_tree:C08_PARTIV",
    objectId: "C08_PARTIV",
    sourceRootRelativePath: "src/modules/focus_tree/C08_PARTIV"
  };
}

const diagramDocument: DiagramDocument = {
  schemaVersion: 1,
  gridSizePx: 96,
  nodes: [
    {
      fixed: true,
      height: 1,
      id: focusRootId,
      imageUrl: focusPreviewUrl(focusRootId),
      mode: "absolute",
      order: 0,
      payload: focusPayload(focusRootId),
      title: "Canterlot Mind",
      width: 1,
      x: 8,
      y: 0
    },
    {
      dx: 0,
      dy: 2,
      height: 1,
      id: focusBranchId,
      imageUrl: focusPreviewUrl(focusBranchId),
      mode: "relative",
      order: 1,
      parentId: focusRootId,
      payload: focusPayload(focusBranchId),
      title: "Second Summit",
      width: 1
    },
    {
      dx: 0,
      dy: 2,
      height: 1,
      id: relativeLeafId,
      imageUrl: focusPreviewUrl(relativeLeafId),
      mode: "relative",
      order: 2,
      parentId: focusBranchId,
      payload: focusPayload(relativeLeafId),
      title: "To the War",
      width: 1
    },
    {
      height: 1,
      id: autoLeafId,
      imageUrl: focusPreviewUrl(autoLeafId),
      mode: "auto",
      order: 3,
      parentId: focusBranchId,
      payload: focusPayload(autoLeafId),
      title: "Twilight",
      width: 1
    },
    {
      fixed: true,
      height: 1,
      id: absoluteLeafId,
      imageUrl: focusPreviewUrl(absoluteLeafId),
      mode: "absolute",
      order: 4,
      parentId: focusBranchId,
      payload: focusPayload(absoluteLeafId),
      title: "Starlight",
      width: 1,
      x: 12,
      y: 8
    },
    {
      fixed: true,
      height: 1,
      id: siblingId,
      imageUrl: focusPreviewUrl(siblingId),
      mode: "absolute",
      order: 5,
      parentId: focusRootId,
      payload: focusPayload(siblingId),
      title: "Sunburst",
      width: 1,
      x: 14,
      y: 2
    }
  ],
  edges: [
    { id: `tree:${focusRootId}->${focusBranchId}`, kind: "tree", source: focusRootId, target: focusBranchId },
    { id: `tree:${focusBranchId}->${relativeLeafId}`, kind: "tree", source: focusBranchId, target: relativeLeafId },
    { id: `tree:${focusBranchId}->${autoLeafId}`, kind: "tree", source: focusBranchId, target: autoLeafId },
    { id: `tree:${focusBranchId}->${absoluteLeafId}`, kind: "tree", source: focusBranchId, target: absoluteLeafId },
    { id: `tree:${focusRootId}->${siblingId}`, kind: "tree", source: focusRootId, target: siblingId },
    { id: `dependency:${focusRootId}->${focusBranchId}`, kind: "dependency", source: focusRootId, target: focusBranchId },
    { id: `dependency:${focusBranchId}->${relativeLeafId}`, kind: "dependency", source: focusBranchId, target: relativeLeafId },
    { id: `reference:${autoLeafId}->${absoluteLeafId}`, kind: "reference", source: autoLeafId, target: absoluteLeafId }
  ]
};

function DiagramMoveSmoke() {
  const [currentDocument, setCurrentDocument] = useState(diagramDocument);
  const [command, setCommand] = useState<MovementCommand>("base");
  const [selectedNodeId, setSelectedNodeId] = useState(focusBranchId);

  useEffect(() => {
    exposeMovementState(currentDocument, command);
  }, [command, currentDocument]);

  return (
    <main className="diagram-move-smoke">
      <header className="diagram-move-smoke-status" aria-label="Diagram move smoke status">
        <strong>Diagram movement smoke</strong>
        <span>Command: {command}</span>
        <button
          type="button"
          onClick={() => {
            setCommand("base");
            setCurrentDocument(diagramDocument);
          }}
        >
          Reset
        </button>
        <button
          type="button"
          onClick={() => {
            setCommand("subtree");
            setCurrentDocument(moveDiagramSubtree(diagramDocument, focusBranchId, moveDelta));
          }}
        >
          Move Subtree
        </button>
        <button
          type="button"
          onClick={() => {
            setCommand("node-only");
            setCurrentDocument(moveDiagramNodeKeepingDescendants(diagramDocument, focusBranchId, moveDelta));
          }}
        >
          Move Node Only
        </button>
        <button
          type="button"
          onClick={() => {
            setCommand("relayout-descendants");
            setCurrentDocument(moveDiagramNodeRelayoutDescendants(diagramDocument, focusBranchId, moveDelta));
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
        onNodeSelect={setSelectedNodeId}
        projectRoot={sourceBackedSmokeProjectRoot}
        selectedNodeId={selectedNodeId}
        t={t}
        title="C08 Movement"
      />
    </main>
  );
}

function exposeMovementState(document: DiagramDocument, command: MovementCommand) {
  const root = documentElement();
  const baseLayout = resolveDiagramLayout(diagramDocument);
  const layout = resolveDiagramLayout(document);
  root.dataset.paradevDiagramMoveCommand = command;
  root.dataset.paradevDiagramMoveGridSizePx = String(document.gridSizePx);
  root.dataset.paradevDiagramMoveExpectedFocusImagePx = String(compactFocusImageSizePx(document.gridSizePx));
  root.dataset.paradevDiagramMoveImageNodeCount = String(document.nodes.filter((node) => node.imageUrl?.endsWith("/preview.png")).length);
  root.dataset.paradevDiagramMoveLegacyImageNodeCount = String(document.nodes.filter((node) => node.imageUrl?.includes("/legacy/focuses/") || node.imageUrl?.endsWith("/default.png")).length);
  root.dataset.paradevDiagramMovePositions = movementPositions(layout, [focusRootId, focusBranchId, relativeLeafId, autoLeafId, absoluteLeafId, siblingId]);
  root.dataset.paradevDiagramMoveModes = document.nodes.map((node) => `${node.id}:${node.mode}`).join("|");
  root.dataset.paradevDiagramMoveBranchDelta = movementDelta(baseLayout, layout, focusBranchId);
  root.dataset.paradevDiagramMoveRelativeLeafDelta = movementDelta(baseLayout, layout, relativeLeafId);
  root.dataset.paradevDiagramMoveAutoLeafDelta = movementDelta(baseLayout, layout, autoLeafId);
  root.dataset.paradevDiagramMoveAbsoluteLeafDelta = movementDelta(baseLayout, layout, absoluteLeafId);
  root.dataset.paradevDiagramMoveSiblingDelta = movementDelta(baseLayout, layout, siblingId);
}

function movementPositions(layout: ReturnType<typeof resolveDiagramLayout>, ids: string[]): string {
  return ids.map((id) => `${id}:${layout.nodesById[id]?.worldX ?? "?"},${layout.nodesById[id]?.worldY ?? "?"}`).join("|");
}

function movementDelta(baseLayout: ReturnType<typeof resolveDiagramLayout>, layout: ReturnType<typeof resolveDiagramLayout>, id: string): string {
  const base = baseLayout.nodesById[id];
  const node = layout.nodesById[id];
  return base && node ? `${node.worldX - base.worldX},${node.worldY - base.worldY}` : "";
}

function compactFocusImageSizePx(gridSizePx: number): number {
  return Math.min(Math.max(24, gridSizePx - 24), 72);
}

function focusPreviewUrl(focusId: string): string {
  return `src/modules/focus_tree/C08_PARTIV/icons/${focusId}.png`;
}

function documentElement(): HTMLElement {
  return globalThis.document.documentElement;
}

const root = document.getElementById("root");

if (!root) {
  throw new Error("ParaDev diagram move smoke root element was not found.");
}

const rootState = globalThis as typeof globalThis & { __paradevDiagramMoveSmokeRoot?: ReturnType<typeof createRoot> };
const reactRoot = rootState.__paradevDiagramMoveSmokeRoot ?? createRoot(root);
rootState.__paradevDiagramMoveSmokeRoot = reactRoot;
reactRoot.render(<DiagramMoveSmoke />);
