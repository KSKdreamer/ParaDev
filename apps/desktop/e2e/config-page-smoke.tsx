import type { Dispatch, SetStateAction } from "react";
import { useEffect, useMemo, useRef, useState } from "react";
import { createRoot } from "react-dom/client";
import { desktopConfigWritesForSettingsChange } from "../src/App";
import { AppShell } from "../src/components/AppShell";
import { defaultConfigLlmStatus, defaultConfigPageSettings, type ConfigPageSettings } from "../src/configPage/model";
import { configOptions, featureModules, railItems, workspaceTabs } from "../src/data/shell";
import { DESKTOP_CONFIG_KEYS } from "../src/desktopConfig";
import { PARADEV_DESKTOP_AI_CHAT_PROFILES, PARADEV_DESKTOP_AI_CHAT_SOURCE_KIND_ROWS } from "../src/generated/desktopContract";
import { createTranslator, type Locale } from "../src/i18n";
import type { ParaDevAiChatProfile, ParaDevAiChatProfileWrite, ParaDevAiChatSourceKindRow } from "../src/services/paradev";
import { smokeProjectRoot } from "../src/testFixtures/smokeImages";
import type { ProjectBrowserPayload, ProjectOption, ThemeName, WorkspaceTab } from "../src/types";
import { configPageSmokeConfigChecked, configPageSmokeConfigValue, configPageSmokeHasConfigKey, writeConfigPageSmokeDataset } from "./config-page-smoke-state";
import "../src/styles/theme.css";
import "../src/styles/app.css";

const t = createTranslator("en");
const configTabs = workspaceTabs.filter((tab): tab is WorkspaceTab & { kind: "config" } => tab.kind === "config");
const initialAiChatProfiles: ParaDevAiChatProfile[] = PARADEV_DESKTOP_AI_CHAT_PROFILES.map((profile) => ({
  ...profile,
  sourceKinds: Array.from(profile.sourceKinds)
}));
const aiChatSourceKindRows: ParaDevAiChatSourceKindRow[] = [
  ...PARADEV_DESKTOP_AI_CHAT_SOURCE_KIND_ROWS.map((row) => ({
    ...row,
    frontendKinds: Array.from(row.frontendKinds)
  })),
  {
    id: "project-index",
    label: "Project index",
    frontendKinds: ["catalog"]
  }
];
const aiChatSourceKinds = aiChatSourceKindRows.map((row) => row.id);

const activeProject: ProjectOption = {
  id: "PIHC3",
  projectId: "PIHC3",
  name: "The Pony In The High Castle",
  path: smokeProjectRoot,
  game: "hoi4",
  manifest: `${smokeProjectRoot}/paradev.yaml`,
  sourceRoots: [`${smokeProjectRoot}/src`],
  outputRoot: `${smokeProjectRoot}/build/mod`,
  buildRoot: `${smokeProjectRoot}/.paradev/cache/build`,
  status: "ready"
};

const browser: ProjectBrowserPayload = {
  schema: "paradev.sdk.project-browser.v1",
  project_id: "PIHC3",
  title: activeProject.name,
  root: smokeProjectRoot,
  profile: "hoi4",
  families: [
    { id: "countries", family: "country", item_count: 45, layouts: ["canonical"], source_count: 180, title: "Countries" },
    { id: "ideas", family: "idea", item_count: 128, layouts: ["canonical"], source_count: 384, title: "Ideas" }
  ],
  items: [],
  diagnostics: []
};

const initialSettings: ConfigPageSettings = {
  ...defaultConfigPageSettings(),
  build: {
    parallelism: 4,
    strictMetadata: false
  },
  cli: {
    output: "json"
  }
};

function noopDispatch<T>(): Dispatch<SetStateAction<T>> {
  return () => undefined;
}

function ConfigPageSmoke() {
  const [activeRail, setActiveRail] = useState("projects");
  const [activeConfig, setActiveConfig] = useState("config-general");
  const [aiChatProfiles, setAiChatProfiles] = useState<ParaDevAiChatProfile[]>(initialAiChatProfiles);
  const [lastAiProfileSave, setLastAiProfileSave] = useState<{ profileId: string; sourceKinds: string[] } | null>(null);
  const [lastConfigWrite, setLastConfigWrite] = useState<{ count: number; key: string; value: string } | null>(null);
  const [settings, setSettings] = useState<ConfigPageSettings>(initialSettings);
  const seenControls = useRef({
    buildParallelism: false,
    buildStrictMetadata: false,
    cliOutput: false
  });
  const selectedConfigTab = configTabs.find((tab) => tab.id === activeConfig) ?? configTabs[0];
  const activeWorkspaceTab = activeRail === "settings" ? selectedConfigTab : null;
  const openTabs = useMemo(() => (activeWorkspaceTab ? [{ ...activeWorkspaceTab, pinned: false }] : []), [activeWorkspaceTab]);

  useEffect(() => {
    const updateDataset = () => {
      seenControls.current.cliOutput ||= configPageSmokeHasConfigKey(document, DESKTOP_CONFIG_KEYS.cliOutput);
      seenControls.current.buildParallelism ||= configPageSmokeHasConfigKey(document, DESKTOP_CONFIG_KEYS.buildParallelism);
      seenControls.current.buildStrictMetadata ||= configPageSmokeHasConfigKey(document, DESKTOP_CONFIG_KEYS.buildStrictMetadata);
      const settingsRailButton = document.querySelector<HTMLButtonElement>(`button[aria-label="${t("rail.config")}"]`);
      const aiSourceList = document.querySelector<HTMLElement>(".config-ai-profile-source-list[data-paradev-ai-profile-source-kinds]");
      const aiSourceLabels = Array.from(aiSourceList?.querySelectorAll("span") ?? [])
        .map((element) => element.textContent?.trim() ?? "")
        .filter(Boolean);
      const explainSourceToggles = Array.from(document.querySelectorAll<HTMLInputElement>('input[data-paradev-ai-profile-id="explain"][data-paradev-ai-profile-source-kind]'));
      const explainSelectedSources = explainSourceToggles
        .filter((input) => input.dataset.paradevAiProfileSourceSelected === "true")
        .map((input) => input.dataset.paradevAiProfileSourceKind ?? "")
        .filter(Boolean);
      const explainTemplatesToggle = document.querySelector<HTMLInputElement>('input[data-paradev-ai-profile-id="explain"][data-paradev-ai-profile-source-kind="templates"]');
      const explainProjectIndexToggle = document.querySelector<HTMLInputElement>(
        'input[data-paradev-ai-profile-id="explain"][data-paradev-ai-profile-source-kind="project-index"]'
      );
      const explainSaveButton = document.querySelector<HTMLButtonElement>('.config-ai-profile-row:has(input[data-paradev-ai-profile-id="explain"]) button[data-paradev-ai-profile-action="save"]');
      writeConfigPageSmokeDataset(document.documentElement, {
        activeTab: activeWorkspaceTab?.id ?? "",
        aiExplainProjectIndexSelected: explainProjectIndexToggle?.dataset.paradevAiProfileSourceSelected === "true",
        aiExplainSaveDisabled: explainSaveButton?.disabled ?? false,
        aiExplainSelectedSources: explainSelectedSources.join(","),
        aiExplainTemplatesSelected: explainTemplatesToggle?.dataset.paradevAiProfileSourceSelected === "true",
        aiExplainToggleCount: explainSourceToggles.length,
        aiLastSavedProfileId: lastAiProfileSave?.profileId ?? "",
        aiLastSavedSourceKinds: lastAiProfileSave?.sourceKinds.join(",") ?? "",
        aiProfileSourceLabels: aiSourceLabels.join(","),
        aiProfileSourceKinds: aiSourceList?.dataset.paradevAiProfileSourceKinds ?? "",
        buildParallelismValue: configPageSmokeConfigValue(document, DESKTOP_CONFIG_KEYS.buildParallelism, String(settings.build.parallelism)),
        buildStrictMetadataChecked: configPageSmokeConfigChecked(document, DESKTOP_CONFIG_KEYS.buildStrictMetadata, settings.build.strictMetadata),
        cliOutputValue: configPageSmokeConfigValue(document, DESKTOP_CONFIG_KEYS.cliOutput, settings.cli.output),
        configPanelCount: document.querySelectorAll(".config-panel").length,
        hasBuildParallelismKey: seenControls.current.buildParallelism,
        hasBuildStrictMetadataKey: seenControls.current.buildStrictMetadata,
        hasCliOutputKey: seenControls.current.cliOutput,
        lastConfigWriteCount: lastConfigWrite?.count ?? 0,
        lastConfigWriteKey: lastConfigWrite?.key ?? "",
        lastConfigWriteValue: lastConfigWrite?.value ?? "",
        projectName: activeProject.name,
        settingsRailSelected: settingsRailButton?.classList.contains("selected") ?? activeRail === "settings"
      });
    };

    updateDataset();
    const observer = new MutationObserver(updateDataset);
    observer.observe(document.body, { attributes: true, childList: true, subtree: true });
    const interval = window.setInterval(updateDataset, 200);
    return () => {
      observer.disconnect();
      window.clearInterval(interval);
    };
  }, [activeConfig, activeRail, activeWorkspaceTab?.id, aiChatProfiles, lastAiProfileSave, lastConfigWrite, settings]);

  const saveAiChatProfile = (profileId: string, profile: ParaDevAiChatProfileWrite) => {
    setLastAiProfileSave({
      profileId,
      sourceKinds: profile.sourceKinds ?? []
    });
    setAiChatProfiles((current) =>
      current.map((row) =>
        row.id === profileId
          ? {
              ...row,
              ...profile,
              sourceKinds: profile.sourceKinds ?? row.sourceKinds
            }
          : row
      )
    );
  };

  const selectConfig = (id: string) => {
    setActiveRail("settings");
    setActiveConfig(id);
  };

  const updateConfigPageSettings = (nextSettings: ConfigPageSettings) => {
    const writes = desktopConfigWritesForSettingsChange(settings, nextSettings);
    const [key, value] = writes[writes.length - 1] ?? ["", ""];
    setLastConfigWrite({
      count: writes.length,
      key,
      value: value == null ? "" : String(value)
    });
    setSettings(nextSettings);
  };

  return (
    <AppShell
      activeFeature={featureModules[0]}
      activeBrowserLoading={false}
      activeOption={activeRail === "settings" ? activeConfig : featureModules[0].id}
      activeProject={activeProject}
      activeRail={activeRail}
      activeTab={activeWorkspaceTab?.id ?? ""}
      activeWorkspaceTab={activeWorkspaceTab}
      bootProgress={null}
      browser={browser}
      configPageSettings={settings}
      configOptions={configOptions}
      dependencyBusyId=""
      dependencyStatusById={{}}
      featureModules={featureModules}
      inspectorOpen={false}
      locale="en"
      llmStatus={defaultConfigLlmStatus(settings.llm)}
      aiChatDefaultRole="chat"
      aiChatDock="floating"
      aiChatGateway="openai"
      aiChatModel="deepseek-v4-flash"
      aiChatOpen={false}
      aiChatProfiles={aiChatProfiles}
      aiChatProvider="deepseek"
      aiChatSourceKindRows={aiChatSourceKindRows}
      aiChatSourceKinds={aiChatSourceKinds}
      aiChatSources={[]}
      onCheckDependency={() => undefined}
      onAiChatDockChange={() => undefined}
      onAiChatOpenChange={() => undefined}
      onAiChatSend={async () => "ok"}
      onCloseTab={() => undefined}
      onConfigPageSettingsChange={updateConfigPageSettings}
      onInstallDependency={() => undefined}
      onModuleReorder={() => undefined}
      onOpenProject={() => undefined}
      onOpenPath={() => undefined}
      onPinConfig={selectConfig}
      onPinModule={() => undefined}
      onPinTab={() => undefined}
      onProjectRefresh={async () => undefined}
      onResetAiChatProfile={() => setLastAiProfileSave(null)}
      onSearchQueryChange={() => undefined}
      onSelectConfig={selectConfig}
      onSelectModule={() => undefined}
      onSelectModuleDiagram={() => undefined}
      onSelectProject={() => undefined}
      onSelectRail={setActiveRail}
      onSelectSettings={() => setActiveRail("settings")}
      onSplitToggle={() => undefined}
      onTestLlm={() => undefined}
      onTabSelect={selectConfig}
      onSaveAiChatProfile={saveAiChatProfile}
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

const root = document.getElementById("root");

if (!root) {
  throw new Error("ParaDev config page smoke root element was not found.");
}

const rootState = globalThis as typeof globalThis & { __paradevConfigPageSmokeRoot?: ReturnType<typeof createRoot> };
const reactRoot = rootState.__paradevConfigPageSmokeRoot ?? createRoot(root);
rootState.__paradevConfigPageSmokeRoot = reactRoot;
reactRoot.render(<ConfigPageSmoke />);
