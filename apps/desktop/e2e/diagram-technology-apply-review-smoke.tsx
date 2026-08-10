import { useEffect, useMemo, useState } from "react";
import { createRoot } from "react-dom/client";
import { ProjectDiagramView } from "../src/diagramEditor/ProjectDiagramView";
import {
  moveDiagramNode,
  resolveDiagramLayout,
  setDiagramDependencyEdge,
  setDiagramPathEdge,
  type DiagramDocument,
  type DiagramMoveDelta
} from "../src/diagramEditor/layoutModel";
import {
  buildTechnologyDiagramDocument,
  changedTechnologyDiagramNodeIds,
  technologyDiagramEditIntents,
  technologyDiagramSourcePath,
  type TechnologyDiagramEditIntents
} from "../src/diagramEditor/technologyDiagram";
import { createTranslator } from "../src/i18n";
import {
  technologyDiagramApplySmokePayload,
  technologyDiagramSmokeBrowserPayload,
  technologyDiagramSmokeProjectRoot
} from "../src/testFixtures/technologyDiagram";
import { smokePngBytesForSourcePath } from "../src/testFixtures/smokeImages";
import { installNativeBinaryBridge } from "./native-binary-bridge";
import "../src/styles/theme.css";
import "../src/styles/app.css";

const projectRoot = technologyDiagramSmokeProjectRoot;
const t = createTranslator("en");

const baseDocument = buildTechnologyDiagramDocument(
  technologyDiagramApplySmokePayload,
  technologyDiagramSmokeBrowserPayload
);

installNativeBinaryBridge({
  loadBytes: previewBytesForSourcePath,
  onCacheWrite: () => {
    const root = documentElement();
    root.dataset.paradevTechnologyApplyImageLastCommand = "thumbnail-cache-write";
    root.dataset.paradevTechnologyApplyImageCacheWriteCount = String(
      Number(root.dataset.paradevTechnologyApplyImageCacheWriteCount ?? "0") + 1
    );
  },
  onRead: (sourcePath) => {
    const root = documentElement();
    root.dataset.paradevTechnologyApplyImageLastCommand = "binary-source";
    root.dataset.paradevTechnologyApplyImageReadCount = String(
      Number(root.dataset.paradevTechnologyApplyImageReadCount ?? "0") + 1
    );
    root.dataset.paradevTechnologyApplyImageLastPath = sourcePath;
  }
});

function DiagramTechnologyApplyReviewSmoke() {
  const [applyCount, setApplyCount] = useState(0);
  const [savedDocument, setSavedDocument] =
    useState<DiagramDocument>(baseDocument);
  const [currentDocument, setCurrentDocument] = useState<DiagramDocument>(baseDocument);
  const [dirty, setDirty] = useState(false);
  const [lastAppliedText, setLastAppliedText] = useState("");
  const [selectedNodeId, setSelectedNodeId] = useState("TECHNOLOGY_LANDMINE");

  const editIntents = useMemo(
    () =>
      technologyDiagramEditIntents(
        savedDocument,
        currentDocument
      ),
    [currentDocument, savedDocument]
  );
  const changedNodeIds = useMemo(
    () =>
      changedTechnologyDiagramNodeIds(
        savedDocument,
        currentDocument
      ),
    [currentDocument, savedDocument]
  );
  const changedEntities = useMemo(
    () =>
      changedNodeIds.map((id) => ({
        id,
        path: technologyDiagramSourcePath(baseDocument, id),
        title:
          baseDocument.nodes.find((node) => node.id === id)
            ?.title ?? id,
        draftText: technologyIntentPreviewForNode(
          id,
          editIntents
        )
      })),
    [changedNodeIds, editIntents]
  );
  const intentText = useMemo(
    () =>
      technologyIntentPreview(
        changedNodeIds,
        editIntents
      ),
    [changedNodeIds, editIntents]
  );
  const visibleIntentText = intentText || lastAppliedText;
  const intentCount =
    editIntents.positionIntents.length +
    editIntents.edgeIntents.length;
  const diagramDirty = dirty && intentCount > 0;

  useEffect(() => {
    const root = documentElement();
    const layout = resolveDiagramLayout(currentDocument);
    const selectedNode = layout.nodesById[selectedNodeId];
    root.dataset.paradevTechnologyApplyCount = String(applyCount);
    root.dataset.paradevTechnologyApplyDirty = diagramDirty ? "1" : "0";
    root.dataset.paradevTechnologyApplyDraftPlanOk = intentCount > 0 ? "1" : "0";
    root.dataset.paradevTechnologyApplyDraftPlanReason = intentCount > 0 ? "" : "no-changes";
    root.dataset.paradevTechnologyApplySourceEditCount = String(changedEntities.length);
    root.dataset.paradevTechnologyApplySourceEditPaths = changedEntities.map((entity) => entity.path).join("|");
    root.dataset.paradevTechnologyApplyPositionIntentCount = String(editIntents.positionIntents.length);
    root.dataset.paradevTechnologyApplyEdgeIntentCount = String(editIntents.edgeIntents.length);
    root.dataset.paradevTechnologyApplyChangedRows = String(changedEntities.length);
    root.dataset.paradevTechnologyApplyGridSizePx = String(currentDocument.gridSizePx);
    root.dataset.paradevTechnologyApplyIconNodeCount = String(currentDocument.nodes.filter((node) => node.width === 1 && node.height === 1).length);
    root.dataset.paradevTechnologyApplyImageNodeCount = String(currentDocument.nodes.filter((node) => node.imageUrl?.endsWith("/icon.png")).length);
    root.dataset.paradevTechnologyApplyLegacyImageCount = String(currentDocument.nodes.filter((node) => node.imageUrl?.includes("/legacy/")).length);
    root.dataset.paradevTechnologyApplyDependencyEdgeCount = String(currentDocument.edges.filter((edge) => edge.kind === "dependency").length);
    root.dataset.paradevTechnologyApplyPathEdgeCount = String(currentDocument.edges.filter((edge) => edge.kind === "path").length);
    root.dataset.paradevTechnologyApplyHasFirearmPositionIntent = hasPositionIntent(editIntents, "TECHNOLOGY_FIREARM_I", 5, 2) ? "1" : "0";
    root.dataset.paradevTechnologyApplyHasLandmineDependencyIntent = hasEdgeIntent(editIntents, "dependency", "TECHNOLOGY_POWDER_EXPLOSIVE", "TECHNOLOGY_LANDMINE", true) ? "1" : "0";
    root.dataset.paradevTechnologyApplyHasLandminePathIntent = hasEdgeIntent(editIntents, "path", "TECHNOLOGY_LANDMINE", "TECHNOLOGY_FIREARM_I", true) ? "1" : "0";
    root.dataset.paradevTechnologyApplyExactRevisionCount = String([
      ...editIntents.positionIntents,
      ...editIntents.edgeIntents
    ].filter((intent) => /^sha256:[0-9a-f]{64}$/.test(intent.source_revision)).length);
    root.dataset.paradevTechnologyApplyDefSourceCount = String(changedEntities.filter((entity) => entity.path.endsWith("/def.txt")).length);
    root.dataset.paradevTechnologyApplySelectedNodePosition = selectedNode ? `${selectedNode.worldX},${selectedNode.worldY},${selectedNode.width},${selectedNode.height}` : "";
  }, [applyCount, changedEntities, currentDocument, diagramDirty, editIntents, intentCount, selectedNodeId]);

  const moveFirearm = () => {
    setCurrentDocument((current) => moveDiagramNode(current, "TECHNOLOGY_FIREARM_I", { dx: 1, dy: -1 }));
    setDirty(true);
    setLastAppliedText("");
    setSelectedNodeId("TECHNOLOGY_FIREARM_I");
  };
  const moveNode = (nodeId: string, delta: DiagramMoveDelta) => {
    setCurrentDocument((current) => moveDiagramNode(current, nodeId, delta));
    setDirty(true);
    setLastAppliedText("");
  };
  const setDependency = (targetId: string, sourceId: string, enabled: boolean, selectedId = targetId) => {
    setCurrentDocument((current) => setDiagramDependencyEdge(current, sourceId, targetId, enabled));
    setDirty(true);
    setLastAppliedText("");
    setSelectedNodeId(selectedId);
  };
  const setPath = (sourceId: string, targetId: string, enabled: boolean, selectedId = sourceId) => {
    setCurrentDocument((current) => setDiagramPathEdge(current, sourceId, targetId, enabled));
    setDirty(true);
    setLastAppliedText("");
    setSelectedNodeId(selectedId);
  };
  const addLandmineLinks = () => {
    setCurrentDocument((current) =>
      setDiagramPathEdge(
        setDiagramDependencyEdge(
          current,
          "TECHNOLOGY_POWDER_EXPLOSIVE",
          "TECHNOLOGY_LANDMINE",
          true
        ),
        "TECHNOLOGY_LANDMINE",
        "TECHNOLOGY_FIREARM_I",
        true
      )
    );
    setDirty(true);
    setLastAppliedText("");
    setSelectedNodeId("TECHNOLOGY_LANDMINE");
  };

  return (
    <main className="diagram-technology-apply-smoke">
      <header className="diagram-technology-apply-smoke-status" aria-label="Technology apply review smoke status">
        <strong>Technology apply review smoke</strong>
        <button data-paradev-move-firearm="" onClick={moveFirearm} type="button">Move firearm</button>
        <button data-paradev-add-landmine-links="" onClick={addLandmineLinks} type="button">Add landmine links</button>
        <span data-paradev-smoke-apply-count="">Apply calls: {applyCount}</span>
        <span data-paradev-smoke-dirty-state="">{diagramDirty ? "Dirty" : "Clean"}</span>
        <span>Source intents: {intentCount}</span>
      </header>
      <ProjectDiagramView
        diagramChangedEntities={changedEntities}
        diagramDirty={diagramDirty}
        document={currentDocument}
        onDiagramApply={() => {
          setApplyCount((count) => count + 1);
          setLastAppliedText(intentText);
          setSavedDocument(currentDocument);
          setDirty(false);
        }}
        onDiagramDiscard={() => {
          setCurrentDocument(savedDocument);
          setDirty(false);
          setLastAppliedText("");
          setSelectedNodeId("TECHNOLOGY_LANDMINE");
        }}
        onNodeAddDependency={(targetId, sourceId) => setDependency(targetId, sourceId, true)}
        onNodeAddUnlock={(sourceId, targetId) => setPath(sourceId, targetId, true)}
        onNodeMove={moveNode}
        onNodeRemoveDependency={(targetId, sourceId) => setDependency(targetId, sourceId, false)}
        onNodeRemoveUnlock={(sourceId, targetId) => setPath(sourceId, targetId, false)}
        onNodeSelect={setSelectedNodeId}
        projectRoot={projectRoot}
        selectedNodeId={selectedNodeId}
        t={t}
        title="Technologies"
      />
      <pre className="diagram-technology-apply-smoke-draft" data-paradev-technology-intents="">{visibleIntentText}</pre>
    </main>
  );
}

function technologyIntentPreview(
  changedNodeIds: string[],
  intents: TechnologyDiagramEditIntents
): string {
  if (changedNodeIds.length === 0) {
    return "";
  }
  return JSON.stringify(
    {
      schema: "paradev.e2e.technology-source-intents.v1",
      source_edits: changedNodeIds.map((id) =>
        technologyIntentPreviewValue(id, intents)
      )
    },
    null,
    2
  );
}

function technologyIntentPreviewForNode(
  technologyId: string,
  intents: TechnologyDiagramEditIntents
): string {
  return JSON.stringify(
    technologyIntentPreviewValue(technologyId, intents),
    null,
    2
  );
}

function technologyIntentPreviewValue(
  technologyId: string,
  intents: TechnologyDiagramEditIntents
) {
  return {
    path: technologyDiagramSourcePath(
      baseDocument,
      technologyId
    ),
    position_intents: intents.positionIntents.filter(
      (intent) => intent.technology_id === technologyId
    ),
    edge_intents: intents.edgeIntents.filter(
      (intent) =>
        (intent.kind === "dependency"
          ? intent.target_id
          : intent.source_id) === technologyId
    )
  };
}

function hasPositionIntent(
  intents: TechnologyDiagramEditIntents,
  technologyId: string,
  x: number,
  y: number
): boolean {
  return intents.positionIntents.some(
    (intent) =>
      intent.technology_id === technologyId &&
      intent.x === x &&
      intent.y === y
  );
}

function hasEdgeIntent(
  intents: TechnologyDiagramEditIntents,
  kind: "dependency" | "path",
  sourceId: string,
  targetId: string,
  present: boolean
): boolean {
  return intents.edgeIntents.some(
    (intent) =>
      intent.kind === kind &&
      intent.source_id === sourceId &&
      intent.target_id === targetId &&
      intent.present === present
  );
}

async function previewBytesForSourcePath(sourcePath: string): Promise<number[]> {
  if (!technologyIdForSourcePath(sourcePath)) {
    throw new Error(`Unknown technology apply smoke image: ${sourcePath}`);
  }
  return smokePngBytesForSourcePath(sourcePath);
}

function technologyIdForSourcePath(sourcePath: string): string | undefined {
  return sourcePath.match(/technology\/([^/]+)\/icon\.png$/)?.[1];
}

function documentElement(): HTMLElement {
  return globalThis.document.documentElement;
}

const root = document.getElementById("root");

if (!root) {
  throw new Error("ParaDev technology apply review smoke root element was not found.");
}

const rootState = globalThis as typeof globalThis & { __paradevTechnologyApplyReviewSmokeRoot?: ReturnType<typeof createRoot> };
const reactRoot = rootState.__paradevTechnologyApplyReviewSmokeRoot ?? createRoot(root);
rootState.__paradevTechnologyApplyReviewSmokeRoot = reactRoot;
reactRoot.render(<DiagramTechnologyApplyReviewSmoke />);
