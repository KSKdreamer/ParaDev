import { useEffect, useState } from "react";
import { createRoot } from "react-dom/client";
import { ProjectDiagramView } from "../src/diagramEditor/ProjectDiagramView";
import { buildTechnologyDiagramDocument } from "../src/diagramEditor/technologyDiagram";
import { createTranslator } from "../src/i18n";
import { smokePngBytesForSourcePath } from "../src/testFixtures/smokeImages";
import {
  technologyDiagramCanvasSmokePayload,
  technologyDiagramSmokeBrowserPayload,
  technologyDiagramSmokeProjectRoot
} from "../src/testFixtures/technologyDiagram";
import { installNativeBinaryBridge } from "./native-binary-bridge";
import "../src/styles/theme.css";
import "../src/styles/app.css";

const projectRoot = technologyDiagramSmokeProjectRoot;
const t = createTranslator("en");

const diagramDocument = buildTechnologyDiagramDocument(
  technologyDiagramCanvasSmokePayload,
  technologyDiagramSmokeBrowserPayload
);

installNativeBinaryBridge({
  loadBytes: previewBytesForSourcePath,
  onCacheWrite: () => {
    const root = documentElement();
    root.dataset.paradevTechnologyDiagramImageLastCommand = "thumbnail-cache-write";
    root.dataset.paradevTechnologyDiagramImageCacheWriteCount = String(
      Number(root.dataset.paradevTechnologyDiagramImageCacheWriteCount ?? "0") + 1
    );
  },
  onRead: (sourcePath) => {
    const root = documentElement();
    root.dataset.paradevTechnologyDiagramImageLastCommand = "binary-source";
    root.dataset.paradevTechnologyDiagramImageReadCount = String(
      Number(root.dataset.paradevTechnologyDiagramImageReadCount ?? "0") + 1
    );
    root.dataset.paradevTechnologyDiagramImageLastPath = sourcePath;
  }
});

function DiagramTechnologySmoke() {
  const [selectedNodeId, setSelectedNodeId] = useState("TECHNOLOGY_FIREARM_I");

  useEffect(() => {
    const root = documentElement();
    root.dataset.paradevTechnologyDiagramNodeCount = String(diagramDocument.nodes.length);
    root.dataset.paradevTechnologyDiagramEdgeCount = String(diagramDocument.edges.length);
    root.dataset.paradevTechnologyDiagramGridSizePx = String(diagramDocument.gridSizePx);
    root.dataset.paradevTechnologyDiagramIconNodeCount = String(diagramDocument.nodes.filter((node) => node.width === 1 && node.height === 1).length);
    root.dataset.paradevTechnologyDiagramImageNodeCount = String(diagramDocument.nodes.filter((node) => node.imageUrl?.endsWith("/icon.png")).length);
    root.dataset.paradevTechnologyDiagramDependencyEdgeCount = String(diagramDocument.edges.filter((edge) => edge.kind === "dependency").length);
    root.dataset.paradevTechnologyDiagramPathEdgeCount = String(diagramDocument.edges.filter((edge) => edge.kind === "path").length);
    root.dataset.paradevTechnologyDiagramDefSourceCount = String(diagramDocument.nodes.filter((node) => technologySourcePath(node)?.endsWith("/def.txt")).length);
    root.dataset.paradevTechnologyDiagramLegacyImageCount = String(diagramDocument.nodes.filter((node) => node.imageUrl?.includes("/legacy/")).length);
  }, []);

  return (
    <main className="diagram-technology-smoke">
      <header className="diagram-technology-smoke-status" aria-label="Technology diagram smoke status">
        <strong>Technology diagram smoke</strong>
        <span>Nodes: {diagramDocument.nodes.length}</span>
        <span>Links: {diagramDocument.edges.length}</span>
        <span>Grid: {diagramDocument.gridSizePx}px</span>
        <span>Images: {diagramDocument.nodes.filter((node) => node.imageUrl).length}</span>
      </header>
      <ProjectDiagramView document={diagramDocument} onNodeSelect={setSelectedNodeId} projectRoot={projectRoot} selectedNodeId={selectedNodeId} t={t} title="Technologies" />
    </main>
  );
}

async function previewBytesForSourcePath(sourcePath: string): Promise<number[]> {
  if (!technologyIdForSourcePath(sourcePath)) {
    throw new Error(`Unknown technology smoke image: ${sourcePath}`);
  }
  return smokePngBytesForSourcePath(sourcePath);
}

function technologyIdForSourcePath(sourcePath: string): string | undefined {
  return sourcePath.match(/technology\/([^/]+)\/icon\.png$/)?.[1];
}

function technologySourcePath(node: { payload?: unknown }): string {
  if (!node.payload || typeof node.payload !== "object" || Array.isArray(node.payload)) {
    return "";
  }
  const sourcePath = Reflect.get(node.payload, "sourcePath");
  return typeof sourcePath === "string" ? sourcePath : "";
}

function documentElement(): HTMLElement {
  return globalThis.document.documentElement;
}

const root = document.getElementById("root");

if (!root) {
  throw new Error("ParaDev technology diagram smoke root element was not found.");
}

const rootState = globalThis as typeof globalThis & { __paradevTechnologyDiagramSmokeRoot?: ReturnType<typeof createRoot> };
const reactRoot = rootState.__paradevTechnologyDiagramSmokeRoot ?? createRoot(root);
rootState.__paradevTechnologyDiagramSmokeRoot = reactRoot;
reactRoot.render(<DiagramTechnologySmoke />);
