import type { ComponentProps, Dispatch, SetStateAction } from "react";
import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";
import type { BuildRunLifecycleController } from "../buildPage/buildRunLifecycle";
import { defaultConfigPageSettings, defaultConfigLlmStatus } from "../configPage/model";
import { railItems, surfaceRows } from "../data/shell";
import { createTranslator, type Locale } from "../i18n";
import type { FeatureModule, ProjectOption, ThemeName } from "../types";
import { AppShell } from "./AppShell";

const activeFeature: FeatureModule = {
  id: "countries",
  titleKey: "modules.countries.title",
  status: "ready"
};

const activeProject: ProjectOption = {
  id: "minimal_hoi4",
  projectId: "minimal_hoi4",
  name: "Minimal HOI4 Project",
  path: "/tmp/minimal",
  manifest: "/tmp/minimal/paradev.yaml",
  sourceRoots: ["/tmp/minimal/src"],
  outputRoot: "/tmp/minimal/build/mod",
  buildRoot: "/tmp/minimal/.paradev/.cache/build"
};

const secondaryProject: ProjectOption = {
  id: "blackice",
  projectId: "blackice",
  name: "BlackICE Test Project",
  path: "/tmp/blackice",
  manifest: "/tmp/blackice/paradev.yaml",
  sourceRoots: ["/tmp/blackice/src"],
  outputRoot: "/tmp/blackice/build/mod",
  buildRoot: "/tmp/blackice/.paradev/.cache/build"
};

const buildLifecycle: BuildRunLifecycleController = {
  clearError: () => undefined,
  errorsByProjectRoot: {},
  globalError: null,
  history: [],
  interrupt: async () => ({ schema: "paradev.desktop.build-run.v1", status: "idle" }),
  recoveryState: "ready",
  removeHistory: () => undefined,
  retryRecovery: () => undefined,
  runs: [],
  start: async () => ({ schema: "paradev.desktop.build-run.v1", status: "idle" })
};

function noopDispatch<T>(): Dispatch<SetStateAction<T>> {
  return () => undefined;
}

function renderShell(
  activeRail: string,
  theme: ThemeName = "light",
  bootProgress: { detail: string; label: string; status?: "error" | "normal"; value: number } | null = null,
  locale: Locale = "en",
  authoringClosePrompt: ComponentProps<typeof AppShell>["authoringClosePrompt"] = null
) {
  const t = createTranslator(locale);
  return renderToStaticMarkup(
    <AppShell
      activeBrowserLoading={false}
      activeFeature={activeFeature}
      activeOption="countries"
      activeProject={activeProject}
      activeRail={activeRail}
      activeTab=""
      activeWorkspaceTab={null}
      bootProgress={bootProgress}
      browser={null}
      buildLifecycle={buildLifecycle}
      configPageSettings={defaultConfigPageSettings()}
      configOptions={[]}
      dependencyBusyId=""
      dependencyStatusById={{}}
      featureModules={[activeFeature]}
      inspectorOpen={false}
      locale={locale}
      llmStatus={defaultConfigLlmStatus()}
      aiChatDefaultRole="chat"
      aiChatDock="floating"
      aiChatGateway="openai"
      aiChatModel="deepseek-v4-flash"
      aiChatOpen={false}
      aiChatPreset="chat"
      aiChatProfiles={[]}
      aiChatProvider="deepseek"
      aiChatSources={[]}
      authoringClosePrompt={authoringClosePrompt}
      onCheckDependency={() => undefined}
      onAiChatSend={async () => "ok"}
      onAiChatDockChange={() => undefined}
      onAiChatOpenChange={() => undefined}
      onAiChatOperationNavigate={() => undefined}
      onCloseTab={() => undefined}
      onConfigPageSettingsChange={() => undefined}
      onInstallDependency={() => undefined}
      onImportProject={() => undefined}
      onResetAiChatProfile={() => undefined}
      onSaveAiChatProfile={() => undefined}
      onModuleReorder={() => undefined}
      onOpenPath={() => undefined}
      onOpenProject={() => undefined}
      onPinConfig={() => undefined}
      onPinModule={() => undefined}
      onPinTab={() => undefined}
      onBuildProjectRefresh={async () => undefined}
      onProjectRefresh={async () => undefined}
      onSearchQueryChange={() => undefined}
      onSelectConfig={() => undefined}
      onSelectModuleDiagram={() => undefined}
      onSelectModule={() => undefined}
      onSelectProject={() => undefined}
      onSelectRail={() => undefined}
      onSelectSettings={() => undefined}
      onSplitToggle={() => undefined}
      onTestLlm={() => undefined}
      onTabSelect={() => undefined}
      openTabs={[]}
      openTarget="cursor"
      projectError=""
      projectImporting={false}
      projectLoading={false}
      projectOpenError=""
      projectOpening={false}
      projectOptions={[activeProject, secondaryProject]}
      projectPanelOpen={true}
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
      surfaceRows={surfaceRows}
      templates={null}
      t={t}
      theme={theme}
    />
  );
}

describe("AppShell page rail selections", () => {
  it("renders the build dashboard from the third rail item without the editing side panel", () => {
    const markup = renderShell("build");

    expect(railItems[3]?.id).toBe("build");
    expect(markup).toContain("Compilation status");
    expect(markup).toContain("Minimal HOI4 Project");
    expect(markup).toContain(">Build</button>");
    expect(markup).toContain(">Open</button>");
    expect(markup).toContain('class="main-shell main-shell-full"');
    expect(markup).toContain('data-paradev-chat-shell="true"');
    expect(markup).toContain('data-paradev-chat-launcher="true"');
    expect(markup).not.toContain("Active Project");
  });

  it("renders the project management list without the editing side panel", () => {
    const markup = renderShell("management");

    expect(markup).toContain("Projects");
    expect(markup).toContain("Minimal HOI4 Project");
    expect(markup).toContain("BlackICE Test Project");
    expect(markup).toContain("Version");
    expect(markup).toContain("Source code");
    expect(markup).toContain("/tmp/minimal/src");
    expect(markup).toContain("Output directory");
    expect(markup).toContain("/tmp/minimal/build/mod");
    expect(markup).toContain("Active");
    expect(markup).toContain(">Build</button>");
    expect(markup).toContain('data-paradev-chat-launcher="true"');
    expect(markup).not.toContain("Active Project");
    expect(markup).not.toContain("Project management tools will appear here.");
  });

  it("renders the agent authoring surface from the third rail item", () => {
    const markup = renderShell("agents");

    expect(railItems[2]?.id).toBe("agents");
    expect(markup).toContain("Create safely with AI");
    expect(markup).toContain("paradev mcp serve");
    expect(markup).toContain("$paradev-authoring");
    expect(markup).toContain("Open AI chat");
    expect(markup).toContain('class="main-shell main-shell-full"');
    expect(markup).not.toContain("Agent sessions and task handoffs will appear here.");
  });

  it("renders the developer rail as surface contracts without the editing side panel", () => {
    const markup = renderShell("developer");

    expect(markup).toContain("Developer");
    expect(markup).toContain("Surface contracts");
    expect(markup).toContain("Python SDK");
    expect(markup).toContain("Typer + Rich CLI");
    expect(markup).toContain("src/paradev/sdk");
    expect(markup).toContain('data-paradev-chat-launcher="true"');
    expect(markup).not.toContain("Active Project");
    expect(markup).not.toContain("Developer tools will appear here.");
  });

  it("renders the global AI chat launcher on the editing workspace", () => {
    const markup = renderShell("projects");

    expect(markup).toContain('data-paradev-chat-shell="true"');
    expect(markup).toContain('aria-label="Open AI chat"');
    expect(markup).toContain('aria-label="Install PIHC3 package"');
  });

  it("reserves a side column when the global AI chat is side-docked and open", () => {
    const t = createTranslator("en");
    const markup = renderToStaticMarkup(
      <AppShell
        activeBrowserLoading={false}
        activeFeature={activeFeature}
        activeOption="countries"
        activeProject={activeProject}
        activeRail="projects"
        activeTab=""
        activeWorkspaceTab={null}
        bootProgress={null}
        browser={null}
        buildLifecycle={buildLifecycle}
        configPageSettings={defaultConfigPageSettings()}
        configOptions={[]}
        dependencyBusyId=""
        dependencyStatusById={{}}
        featureModules={[activeFeature]}
        inspectorOpen={false}
        locale="en"
        llmStatus={defaultConfigLlmStatus()}
        aiChatDefaultRole="chat"
        aiChatDock="side"
        aiChatGateway="openai"
        aiChatModel="deepseek-v4-flash"
        aiChatOpen={true}
        aiChatPreset="chat"
        aiChatProfiles={[]}
        aiChatProvider="deepseek"
        aiChatSources={[]}
        onCheckDependency={() => undefined}
        onAiChatSend={async () => "ok"}
        onAiChatDockChange={() => undefined}
        onAiChatOpenChange={() => undefined}
        onAiChatOperationNavigate={() => undefined}
        onCloseTab={() => undefined}
        onConfigPageSettingsChange={() => undefined}
        onInstallDependency={() => undefined}
        onImportProject={() => undefined}
        onResetAiChatProfile={() => undefined}
        onSaveAiChatProfile={() => undefined}
        onModuleReorder={() => undefined}
        onOpenPath={() => undefined}
        onOpenProject={() => undefined}
        onPinConfig={() => undefined}
        onPinModule={() => undefined}
        onPinTab={() => undefined}
        onBuildProjectRefresh={async () => undefined}
        onProjectRefresh={async () => undefined}
        onSearchQueryChange={() => undefined}
        onSelectConfig={() => undefined}
        onSelectModuleDiagram={() => undefined}
        onSelectModule={() => undefined}
        onSelectProject={() => undefined}
        onSelectRail={() => undefined}
        onSelectSettings={() => undefined}
        onSplitToggle={() => undefined}
        onTestLlm={() => undefined}
        onTabSelect={() => undefined}
        openTabs={[]}
        openTarget="cursor"
        projectError=""
        projectImporting={false}
        projectLoading={false}
        projectOpenError=""
        projectOpening={false}
        projectOptions={[activeProject, secondaryProject]}
        projectPanelOpen={true}
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
        surfaceRows={surfaceRows}
        templates={null}
        t={t}
        theme="light"
      />
    );

    expect(markup).toContain('class="app theme-light chat-side-open"');
    expect(markup).toContain('class="ai-chat-shell open dock-side"');
    expect(markup).toContain('data-paradev-chat-dock="side"');
    expect(markup).toContain('data-paradev-chat-dock-toggle="true"');
  });

  it("renders the ParaDev logo image in the rail brand mark", () => {
    const markup = renderShell("projects", "anthropic");

    expect(markup).toContain('class="brand-mark-image"');
    expect(markup).toContain('alt="ParaDev"');
    expect(markup).toContain("paradev-logo-anthro");
    expect(markup).not.toContain(">P</div>");
  });

  it("renders window-level boot progress while the desktop project state loads", () => {
    const markup = renderShell("projects", "light", {
      label: "Preparing workspace",
      detail: "Loading PIHC3 project registry",
      value: 64
    });

    expect(markup).toContain('aria-valuenow="64"');
    expect(markup).toContain('class="boot-progress"');
    expect(markup).toContain('class="boot-progress-dots"');
    expect(markup).toContain('class="boot-progress-track"');
    expect(markup).not.toContain('data-paradev-chat-shell="true"');
    expect(markup).not.toContain("Preparing workspace");
    expect(markup).not.toContain("Loading PIHC3 project registry");
    expect(markup).not.toContain('class="boot-progress-card visual"');
    expect(markup).not.toContain('class="boot-progress-stages"');
    expect(markup).not.toContain('class="boot-progress-percent"');
  });

  it("renders the boot progress bar label through the selected locale", () => {
    const markup = renderShell(
      "projects",
      "light",
      {
        label: "正在加载项目",
        detail: "正在读取 PIHC3 的 SDK 项目索引",
        value: 64
      },
      "zh"
    );

    expect(markup).toContain('aria-label="ParaDev 启动进度"');
    expect(markup).not.toContain('aria-label="ParaDev startup progress"');
  });

  it("renders only jumping dots and a progress bar during normal boot progress", () => {
    const markup = renderShell("projects", "light", {
      label: "Loading project",
      detail: "Reading SDK project registry for PIHC3",
      value: 64
    });

    expect(markup).toContain('class="boot-progress-dots"');
    expect(markup).toContain('class="boot-progress-track"');
    expect(markup).not.toContain('class="boot-progress-card"');
    expect(markup).not.toContain('class="boot-progress-stages"');
    expect(markup).not.toContain('aria-current="step"');
    expect(markup).not.toContain("Prepare");
    expect(markup).not.toContain("Load project");
    expect(markup).not.toContain("Open workspace");
  });

  it("marks the shell busy while boot progress blocks interaction", () => {
    const markup = renderShell("projects", "light", {
      label: "Preparing workspace",
      detail: "Loading PIHC3 project registry",
      value: 64
    });

    expect(markup).toMatch(/<div (?=[^>]*class="app theme-light app-booting")(?=[^>]*aria-busy="true")[^>]*>/);
  });

  it("makes the underlying shell surfaces inert while boot progress is visible", () => {
    const markup = renderShell("projects", "light", {
      label: "Preparing workspace",
      detail: "Loading PIHC3 project registry",
      value: 64
    });

    expect(markup).toMatch(/<aside (?=[^>]*class="rail")(?=[^>]*aria-hidden="true")(?=[^>]*inert="")[^>]*>/);
    expect(markup).toMatch(/<aside (?=[^>]*class="project-panel")(?=[^>]*aria-hidden="true")(?=[^>]*inert="")[^>]*>/);
    expect(markup).toMatch(/<main (?=[^>]*class="main-shell")(?=[^>]*aria-hidden="true")(?=[^>]*inert="")[^>]*>/);
  });

  it("renders failed boot progress as an alert", () => {
    const markup = renderShell("projects", "light", {
      label: "Project load failed",
      detail: "desktop-state failed",
      status: "error",
      value: 100
    });

    expect(markup).toContain('role="alert"');
    expect(markup).toContain('aria-live="assertive"');
    expect(markup).toContain('class="boot-progress boot-progress-error"');
    expect(markup).toContain("Project load failed");
    expect(markup).toContain("desktop-state failed");
  });

  it("keeps shell controls available when failed boot progress is shown", () => {
    const markup = renderShell("projects", "light", {
      label: "Project load failed",
      detail: "desktop-state failed",
      status: "error",
      value: 100
    });

    expect(markup).not.toMatch(/<div (?=[^>]*class="app theme-light app-boot-error")(?=[^>]*aria-busy="true")[^>]*>/);
    expect(markup).toMatch(/<aside (?=[^>]*class="rail")(?![^>]*aria-hidden="true")(?![^>]*inert="")[^>]*>/);
    expect(markup).toMatch(/<aside (?=[^>]*class="project-panel")(?![^>]*aria-hidden="true")(?![^>]*inert="")[^>]*>/);
    expect(markup).toMatch(/<main (?=[^>]*class="main-shell")(?![^>]*aria-hidden="true")(?![^>]*inert="")[^>]*>/);
  });
});
