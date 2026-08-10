import type { Dispatch, SetStateAction } from "react";
import { createRoot } from "react-dom/client";
import { AppShell } from "../src/components/AppShell";
import { defaultConfigLlmStatus, defaultConfigPageSettings } from "../src/configPage/model";
import { railItems } from "../src/data/shell";
import { createTranslator, type Locale } from "../src/i18n";
import { smokeProjectRoot } from "../src/testFixtures/smokeImages";
import type { FeatureModule, ProjectOption, ThemeName } from "../src/types";
import "../src/styles/theme.css";
import "../src/styles/app.css";

const t = createTranslator("en");

const activeFeature: FeatureModule = {
  id: "focuses",
  titleKey: "modules.focuses.title",
  status: "ready",
  count: 738
};

const activeProject: ProjectOption = {
  id: "PIHC3",
  projectId: "PIHC3",
  name: "The Pony In The High Castle",
  path: smokeProjectRoot,
  game: "hoi4"
};

const bootProgress = {
  label: t("app.boot.refresh.label"),
  detail: t("app.boot.refresh.loadedDetail", { diagnostics: "2", items: "1,148", project: activeProject.name, templates: "16" }),
  value: 86
};

function noopDispatch<T>(): Dispatch<SetStateAction<T>> {
  return () => undefined;
}

function BootProgressSmoke() {
  const root = document.documentElement;
  root.dataset.paradevBootProgressSmokeValue = String(bootProgress.value);
  root.dataset.paradevBootProgressSmokeProject = activeProject.id;
  root.dataset.paradevBootProgressSmokeRows = "1148";
  root.dataset.paradevBootProgressSmokeTemplates = "16";

  return (
    <AppShell
      activeFeature={activeFeature}
      activeBrowserLoading={false}
      activeOption="focuses"
      activeProject={activeProject}
      activeRail="projects"
      activeTab=""
      activeWorkspaceTab={null}
      bootProgress={bootProgress}
      browser={null}
      configPageSettings={defaultConfigPageSettings()}
      configOptions={[]}
      dependencyBusyId=""
      dependencyStatusById={{}}
      featureModules={[activeFeature]}
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
      onCloseTab={() => undefined}
      onConfigPageSettingsChange={() => undefined}
      onInstallDependency={() => undefined}
      onModuleReorder={() => undefined}
      onOpenProject={() => undefined}
      onPinConfig={() => undefined}
      onPinModule={() => undefined}
      onPinTab={() => undefined}
      onProjectRefresh={async () => undefined}
      onSearchQueryChange={() => undefined}
      onSelectConfig={() => undefined}
      onSelectModule={() => undefined}
      onSelectModuleDiagram={() => undefined}
      onSelectProject={() => undefined}
      onSelectRail={() => undefined}
      onSelectSettings={() => undefined}
      onSplitToggle={() => undefined}
      onTestLlm={() => undefined}
      onTabSelect={() => undefined}
      openTabs={[]}
      openTarget="cursor"
      projectError=""
      projectLoading
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
  throw new Error("ParaDev boot progress smoke root element was not found.");
}

const rootState = globalThis as typeof globalThis & { __paradevBootProgressSmokeRoot?: ReturnType<typeof createRoot> };
const reactRoot = rootState.__paradevBootProgressSmokeRoot ?? createRoot(root);
rootState.__paradevBootProgressSmokeRoot = reactRoot;
reactRoot.render(<BootProgressSmoke />);
