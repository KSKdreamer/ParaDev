import type { Dispatch, SetStateAction } from "react";
import { useEffect, useMemo, useState } from "react";
import { createRoot } from "react-dom/client";
import { AppShell } from "../src/components/AppShell";
import { defaultConfigLlmStatus, defaultConfigPageSettings } from "../src/configPage/model";
import { nextOpenTabEntriesForOpen, tabsForModules, type OpenTabEntry } from "../src/App";
import { railItems } from "../src/data/shell";
import { c01MainSmokeBrowserItem, c01MainSmokeSummary, sourceBackedSmokeBrowserPayload, sourceBackedSmokeProjectRoot, sourceBackedSmokeSummary } from "../src/diagramEditor/fixtures/sourceBackedSmokeModel";
import { createTranslator, type Locale } from "../src/i18n";
import { moduleIdForDiagramTabId } from "../src/projectModules";
import type { FeatureModule, ProjectOption, ThemeName, WorkspaceModuleSelectionTarget } from "../src/types";
import { writeDiagramTabSmokeApplyDataset, writeDiagramTabSmokeHitTargetDataset, writeDiagramTabSmokePopupDataset, writeDiagramTabSmokeSelectedNodeDataset, writeDiagramTabSmokeSourceDataset } from "./diagram-tab-smoke-state";
import { installSourceBackedFocusImageBridge } from "./source-backed-focus-image-bridge";
import "../src/styles/theme.css";
import "../src/styles/app.css";

const t = createTranslator("en");

const activeProject: ProjectOption = {
  id: "PIHC3",
  projectId: "PIHC3",
  name: "The Pony In The High Castle",
  path: sourceBackedSmokeProjectRoot,
  game: "hoi4"
};

const featureModules: FeatureModule[] = [
  { id: "focuses", titleKey: "modules.focuses.title", status: "ready", count: c01MainSmokeSummary.nodeCount + sourceBackedSmokeSummary.nodeCount + 1 },
  { id: "ideas", titleKey: "modules.ideas.title", status: "ready", count: 1 },
  { id: "technologies", titleKey: "modules.technologies.title", status: "ready", count: 0 }
];
const browser = {
  ...sourceBackedSmokeBrowserPayload,
  families: sourceBackedSmokeBrowserPayload.families.map((family) => (family.id === "focus_tree" ? { ...family, item_count: 3, source_count: 3 } : family)),
  items: [
    c01MainSmokeBrowserItem,
    ...sourceBackedSmokeBrowserPayload.items,
    {
      ...sourceBackedSmokeBrowserPayload.items[0],
      id: "focus_tree:C09_MAIN",
      object_id: "C09_MAIN",
      module_id: "C09_MAIN",
      title: "C09 Main",
      root: `${sourceBackedSmokeProjectRoot}/src/modules/focus_tree/C09_MAIN`,
      relative_root: "src/modules/focus_tree/C09_MAIN",
      sources: [],
      metadata: {
        settings: {
          focuses: [{ id: "FOCUS_C09_OTHER_TREE", x: "0", y: "0" }]
        }
      }
    }
  ]
};

installSourceBackedFocusImageBridge({
  applyCount: "paradevDiagramTabSmokeApplyCount",
  applyEditCount: "paradevDiagramTabSmokeApplyEditCount",
  cacheWriteCount: "paradevDiagramTabSmokeImageCacheWriteCount",
  lastApplyPath: "paradevDiagramTabSmokeLastApplyPath",
  lastApplyText: "paradevDiagramTabSmokeLastApplyText",
  lastCommand: "paradevDiagramTabSmokeImageLastCommand",
  lastPath: "paradevDiagramTabSmokeImageLastPath",
  readCount: "paradevDiagramTabSmokeImageReadCount"
});

function noopDispatch<T>(): Dispatch<SetStateAction<T>> {
  return () => undefined;
}

function DiagramTabSmoke() {
  const workspaceTabs = useMemo(() => tabsForModules(featureModules), []);
  const [activeModule, setActiveModule] = useState("focuses");
  const [activeTab, setActiveTab] = useState("");
  const [openTabEntries, setOpenTabEntries] = useState<OpenTabEntry[]>([]);
  const [moduleSelectionTarget, setModuleSelectionTarget] = useState<WorkspaceModuleSelectionTarget | null>(null);
  const openTabs = useMemo(
    () =>
      openTabEntries.flatMap((entry) => {
        const tab = workspaceTabs.find((candidate) => candidate.id === entry.id);
        return tab ? [{ ...tab, pinned: entry.pinned }] : [];
      }),
    [openTabEntries, workspaceTabs]
  );
  const activeWorkspaceTab = openTabs.find((tab) => tab.id === activeTab) ?? openTabs[0] ?? null;
  const activeFeature = featureModules.find((module) => module.id === activeModule) ?? featureModules[0];
  const activeOption = activeWorkspaceTab?.kind === "diagram" ? activeWorkspaceTab.id : activeModule;

  const openWorkspaceTab = (id: string, options: { pinned?: boolean } = {}) => {
    const nextTab = workspaceTabs.find((tab) => tab.id === id);
    if (!nextTab) {
      return;
    }
    setOpenTabEntries((entries) => nextOpenTabEntriesForOpen(entries, nextTab, options));
    setActiveTab(nextTab.id);
  };

  useEffect(() => {
    const root = document.documentElement;
    root.dataset.paradevDiagramTabSmokeActiveTab = activeTab;
    root.dataset.paradevDiagramTabSmokeOpenTabs = openTabs.map((tab) => tab.id).join(",");
    root.dataset.paradevDiagramTabSmokeModuleTabCount = String(openTabs.filter((tab) => tab.kind === "module").length);
    root.dataset.paradevDiagramTabSmokeDiagramTabCount = String(openTabs.filter((tab) => tab.kind === "diagram").length);
    root.dataset.paradevDiagramTabSmokeSelectedKind = activeWorkspaceTab?.kind ?? "";
  }, [activeTab, activeWorkspaceTab?.kind, openTabs]);

  useEffect(() => {
    const updateCanvasCounters = () => {
      const root = document.documentElement;
      const focusImages = Array.from(document.querySelectorAll("image.project-diagram-node-image.focus-icon"));
      root.dataset.paradevDiagramTabSmokeFocusImageCount = String(focusImages.length);
      root.dataset.paradevDiagramTabSmokeDataUrlImageCount = String(focusImages.filter((image) => (image.getAttribute("href") ?? "").startsWith("data:image")).length);
      root.dataset.paradevDiagramTabSmokePlaceholderCount = String(document.querySelectorAll(".project-diagram-node-image-placeholder.focus-icon").length);
      root.dataset.paradevDiagramTabSmokePreviewNodeCount = String(focusImages.length);
      root.dataset.paradevDiagramTabSmokeExpectedC01NodeCount = String(c01MainSmokeSummary.nodeCount);
      const c01NodeCount = document.querySelectorAll("svg.project-diagram-main [data-node-id^='FOCUS_C01_']").length;
      root.dataset.paradevDiagramTabSmokeC01NodeCount = String(c01NodeCount);
      root.dataset.paradevDiagramTabSmokeC01PreviewNodeCount = String(c01MainSmokeSummary.previewNodeCount);
      root.dataset.paradevDiagramTabSmokeImageStatus = document.querySelector(".project-diagram-image-status")?.textContent?.trim() ?? "";
      writeDiagramTabSmokeHitTargetDataset(root, {
        c01HitTargetCount: document.querySelectorAll("svg.project-diagram-main .project-diagram-node-hit-target[data-node-hit-id^='FOCUS_C01_']").length,
        c01NodeCount,
        targetCount: document.querySelectorAll('svg.project-diagram-main .project-diagram-node-hit-target[data-node-hit-id="FOCUS_C01_DEM_CHANGE"]').length,
        targetId: "FOCUS_C01_DEM_CHANGE"
      });
      const applyButton = document.querySelector<HTMLButtonElement>(".project-diagram-apply");
      writeDiagramTabSmokeApplyDataset(root, {
        applyButtonDisabled: Boolean(applyButton?.disabled),
        applyButtonText: applyButton?.textContent?.trim() ?? "",
        applyPreviewText: document.querySelector(".project-diagram-apply-preview")?.textContent?.trim() ?? "",
        dirtySummaryText: document.querySelector(".project-diagram-dirty-summary")?.textContent?.trim() ?? "",
        reviewPanelCount: document.querySelectorAll(".project-diagram-apply-review").length
      });
      const selectedNode = document.querySelector("svg.project-diagram-main .project-diagram-node.selected");
      const selectedNodeId = selectedNode?.getAttribute("data-node-id") ?? "";
      const modeSwitch = document.querySelector(".project-diagram-node-mode-switch");
      writeDiagramTabSmokeSelectedNodeDataset(root, {
        mode: selectedDiagramNodeMode(selectedNode),
        nodeId: selectedNodeId,
        switchCount: document.querySelectorAll(".project-diagram-node-mode-switch").length,
        switchMode: modeSwitch?.getAttribute("data-node-mode-switch") ?? ""
      });
      const scopeSelect = document.querySelector<HTMLSelectElement>('select[aria-label="Focus tree diagram scope"]');
      root.dataset.paradevDiagramTabSmokeScopeOptionCount = String(scopeSelect?.options.length ?? 0);
      root.dataset.paradevDiagramTabSmokeScopeValue = scopeSelect?.value ?? "";
      root.dataset.paradevDiagramTabSmokeScopeText = scopeSelect ? Array.from(scopeSelect.options).map((option) => option.text).join(",") : "";
      root.dataset.paradevDiagramTabSmokeC09NodeCount = String(document.querySelectorAll('[data-node-id="FOCUS_C09_OTHER_TREE"]').length);
      const popup = document.querySelector(".project-diagram-node-info-popover");
      writeDiagramTabSmokePopupDataset(root, {
        ariaLabel: popup?.getAttribute("aria-label") ?? "",
        count: document.querySelectorAll(".project-diagram-node-info-popover").length,
        nodeId: popup?.querySelector(":scope > code")?.textContent?.trim() ?? "",
        openModuleText: popup?.querySelector(".project-diagram-node-open-module")?.textContent?.trim() ?? "",
        selectedNodeId,
        sourceInfoPath: popup?.querySelector(".project-diagram-node-info-source code")?.textContent?.trim() ?? "",
        title: popup?.querySelector("strong")?.textContent?.trim() ?? ""
      });
      const sourcePicker = document.querySelector<HTMLSelectElement>(".source-tab-source-picker select");
      const selectedSourceOption = sourcePicker ? sourcePicker.selectedOptions[0] : undefined;
      writeDiagramTabSmokeSourceDataset(root, {
        pickerCount: document.querySelectorAll(".source-tab-source-picker select").length,
        pickerOptionCount: sourcePicker ? Array.from(sourcePicker.options).filter((option) => !option.disabled).length : 0,
        pickerPath: document.querySelector(".source-tab-source-path")?.textContent?.trim() ?? "",
        pickerText: selectedSourceOption?.textContent?.trim() ?? "",
        pickerValue: sourcePicker?.value ?? "",
        sourceTabCount: document.querySelectorAll(".source-tab-strip > .source-tab").length,
        textPanelVisible: Boolean(document.querySelector(".source-editor-panel"))
      });
    };

    updateCanvasCounters();
    const observer = new MutationObserver(updateCanvasCounters);
    observer.observe(document.body, { attributes: true, childList: true, subtree: true });
    const interval = window.setInterval(updateCanvasCounters, 200);
    return () => {
      observer.disconnect();
      window.clearInterval(interval);
    };
  }, [activeTab, openTabs]);

  return (
    <AppShell
      activeFeature={activeFeature}
      activeBrowserLoading={false}
      activeOption={activeOption}
      activeProject={activeProject}
      activeRail="projects"
      activeTab={activeTab}
      activeWorkspaceTab={activeWorkspaceTab}
      bootProgress={null}
      browser={browser}
      configPageSettings={defaultConfigPageSettings()}
      configOptions={[]}
      dependencyBusyId=""
      dependencyStatusById={{}}
      featureModules={featureModules}
      inspectorOpen={false}
      locale="en"
      llmStatus={defaultConfigLlmStatus()}
      aiChatGateway="openai"
      aiChatModel="deepseek-v4-flash"
      aiChatProfiles={[]}
      aiChatProvider="deepseek"
      aiChatSources={[]}
      onCheckDependency={() => undefined}
      onAiChatSend={async () => "ok"}
      onCloseTab={(id) => {
        setOpenTabEntries((entries) => entries.filter((entry) => entry.id !== id));
        setActiveTab((current) => (current === id ? "" : current));
      }}
      onConfigPageSettingsChange={() => undefined}
      onInstallDependency={() => undefined}
      onModuleReorder={() => undefined}
      onOpenModuleEntity={(target) => {
        setActiveModule(target.familyId);
        setModuleSelectionTarget(target);
        openWorkspaceTab(target.familyId);
      }}
      onOpenProject={() => undefined}
      onPinConfig={(id) => openWorkspaceTab(id, { pinned: true })}
      onPinModule={(id) => {
        setActiveModule(id);
        openWorkspaceTab(id, { pinned: true });
      }}
      onPinTab={(id) => setOpenTabEntries((entries) => entries.map((entry) => (entry.id === id ? { ...entry, pinned: true } : entry)))}
      onProjectRefresh={async () => undefined}
      onSearchQueryChange={() => undefined}
      onSelectConfig={openWorkspaceTab}
      onSelectModule={(id) => {
        setActiveModule(id);
        openWorkspaceTab(id);
      }}
      onSelectModuleDiagram={(id) => {
        setActiveModule(moduleIdForDiagramTabId(id));
        openWorkspaceTab(id);
      }}
      onSelectProject={() => undefined}
      onSelectRail={() => undefined}
      onSelectSettings={() => undefined}
      onSplitToggle={() => undefined}
      onTestLlm={() => undefined}
      onTabSelect={setActiveTab}
      moduleSelectionTarget={moduleSelectionTarget}
      openTabs={openTabs}
      openTarget="cursor"
      projectError=""
      projectLoading={false}
      projectOpenError=""
      projectOpening={false}
      projectOptions={[activeProject]}
      projectPanelOpen
      railItems={railItems}
      searchQuery=""
      secondaryTab=""
      secondaryBrowserLoading={false}
      secondaryWorkspaceTab={null}
      setInspectorOpen={noopDispatch<boolean>()}
      setLocale={noopDispatch<Locale>()}
      setOpenTarget={() => undefined}
      setProjectPanelOpen={noopDispatch<boolean>()}
      setSecondaryTab={noopDispatch<string>()}
      setTheme={noopDispatch<ThemeName>()}
      splitView={false}
      surfaceRows={[]}
      templates={null}
      t={t}
      theme="light"
    />
  );
}

function selectedDiagramNodeMode(node: Element | null): string {
  const classes = node?.getAttribute("class")?.split(/\s+/) ?? [];
  if (classes.includes("absolute")) {
    return "absolute";
  }
  if (classes.includes("relative")) {
    return "relative";
  }
  if (classes.includes("auto")) {
    return "auto";
  }
  return "";
}

const root = document.getElementById("root");

if (!root) {
  throw new Error("ParaDev diagram tab smoke root element was not found.");
}

const rootState = globalThis as typeof globalThis & { __paradevDiagramTabSmokeRoot?: ReturnType<typeof createRoot> };
const reactRoot = rootState.__paradevDiagramTabSmokeRoot ?? createRoot(root);
rootState.__paradevDiagramTabSmokeRoot = reactRoot;
reactRoot.render(<DiagramTabSmoke />);
