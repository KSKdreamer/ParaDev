/** @vitest-environment jsdom */

import { act, cloneElement } from "react";
import { createRoot } from "react-dom/client";
import { renderToStaticMarkup } from "react-dom/server";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { defaultConfigLlmStatus, normalizeConfigPageSettings } from "../configPage/model";
import { createTranslator } from "../i18n";
import type {
  FeatureModule,
  ProjectBrowserPayload,
  ProjectOption,
  WorkspaceModuleSelectionTarget,
  WorkspaceTab
} from "../types";

const mocks = vi.hoisted(() => ({
  moduleEditorProps: [] as Array<Record<string, unknown>>
}));

vi.mock("../moduleEditor/ModuleEditor", () => ({
  ModuleEditor: (props: Record<string, unknown>) => {
    mocks.moduleEditorProps.push(props);
    return <div data-game-root={String(props.gameRoot ?? "")} data-testid="module-editor" />;
  }
}));

import { Workspace } from "./Workspace";

const activeProject: ProjectOption = {
  id: "PIHC3",
  projectId: "PIHC3",
  name: "The Pony In The High Castle",
  path: "/workspace/projects/PIHC3",
  manifest: "/workspace/projects/PIHC3/paradev.yaml",
  sourceRoots: ["/workspace/projects/PIHC3/src"],
  outputRoot: "/workspace/projects/PIHC3/build/mod",
  buildRoot: "/workspace/projects/PIHC3/.paradev/.cache/build"
};

const activeFeature: FeatureModule = {
  id: "ideas",
  titleKey: "modules.ideas.title",
  status: "ready"
};

const moduleTab: WorkspaceTab = {
  id: "ideas",
  titleKey: "modules.ideas.title",
  kind: "module"
};

const browser: ProjectBrowserPayload = {
  schema: "paradev.sdk.project-browser.v1",
  project_id: "PIHC3",
  title: "The Pony In The High Castle",
  profile: "hoi4",
  root: activeProject.path,
  filters: {},
  items: [
    {
      id: "module:idea/IDEA_ALPHA",
      kind: "module",
      layout: "canonical",
      family_id: "ideas",
      family: "idea",
      object_id: "IDEA_ALPHA",
      module_id: "idea/IDEA_ALPHA",
      title: "Idea Alpha",
      root: `${activeProject.path}/src/modules/idea/IDEA_ALPHA`,
      relative_root: "src/modules/idea/IDEA_ALPHA",
      source_count: 0,
      sources: []
    }
  ],
  families: [
    {
      id: "ideas",
      family: "idea",
      title: "Ideas",
      item_count: 1,
      source_count: 0,
      layouts: ["canonical"]
    }
  ],
  diagnostics: []
};

describe("Workspace module editor config wiring", () => {
  beforeEach(() => {
    (
      globalThis as typeof globalThis & {
        IS_REACT_ACT_ENVIRONMENT: boolean;
      }
    ).IS_REACT_ACT_ENVIRONMENT = true;
    mocks.moduleEditorProps.length = 0;
  });

  it("passes the configured HOI4 game root into module editors", async () => {
    const configPageSettings = normalizeConfigPageSettings({ hoi4: { gameRoot: "/Games/Hearts of Iron IV" } });
    const handleSelectionTargetChange = () => undefined;
    const workspace = (
      <Workspace
        activeFeature={activeFeature}
        activeProject={activeProject}
        activeTab={moduleTab.id}
        activeWorkspaceTab={moduleTab}
        aiChatDefaultRole="chat"
        aiChatProfiles={[]}
        browser={null}
        configPageSettings={configPageSettings}
        dependencyBusyId=""
        dependencyStatusById={{}}
        inspectorOpen={false}
        llmStatus={defaultConfigLlmStatus(configPageSettings.llm)}
        locale="en"
        onCheckDependency={() => undefined}
        onCloseTab={() => undefined}
        onConfigPageSettingsChange={() => undefined}
        onInstallDependency={() => undefined}
        onLocaleChange={() => undefined}
        onModuleSelectionTargetChange={handleSelectionTargetChange}
        onOpenPath={() => undefined}
        onOpenTargetChange={() => undefined}
        onProjectRefresh={async () => undefined}
        onResetAiChatProfile={() => undefined}
        onSaveAiChatProfile={() => undefined}
        onSplitToggle={() => undefined}
        onTabPin={() => undefined}
        onTabSelect={() => undefined}
        onTestLlm={() => undefined}
        onThemeChange={() => undefined}
        openTarget="finder"
        openTabs={[moduleTab]}
        projectOptions={[activeProject]}
        secondaryTab=""
        secondaryWorkspaceTab={null}
        setSecondaryTab={() => undefined}
        splitView={false}
        surfaceRows={[]}
        templates={null}
        t={createTranslator("en")}
        theme="light"
      />
    );
    renderToStaticMarkup(workspace);
    await vi.dynamicImportSettled();
    const markup = renderToStaticMarkup(workspace);

    expect(markup).toContain('data-game-root="/Games/Hearts of Iron IV"');
    expect(mocks.moduleEditorProps[0]).toMatchObject({
      gameRoot: "/Games/Hearts of Iron IV",
      onModuleSelectionTargetChange: handleSelectionTargetChange
    });
  });

  it("preserves the filtered module browser across selection-only parent rerenders", async () => {
    const container = document.createElement("div");
    document.body.append(container);
    const root = createRoot(container);
    const firstTarget: WorkspaceModuleSelectionTarget = {
      entityId: "module:idea/IDEA_ALPHA",
      familyId: "ideas",
      sourcePath: "src/modules/idea/IDEA_ALPHA/def.json"
    };
    const secondTarget: WorkspaceModuleSelectionTarget = {
      ...firstTarget,
      sourcePath: "src/modules/idea/IDEA_ALPHA/meta.yaml"
    };

    try {
      await act(async () => {
        root.render(moduleWorkspace(firstTarget));
        await vi.dynamicImportSettled();
      });
      const firstFilteredBrowser = mocks.moduleEditorProps.at(-1)?.browser;
      expect(firstFilteredBrowser).toBeTruthy();

      await act(async () => {
        root.render(moduleWorkspace(secondTarget));
      });

      expect(mocks.moduleEditorProps.at(-1)?.browser).toBe(firstFilteredBrowser);
    } finally {
      act(() => root.unmount());
      container.remove();
    }
  });

  it("passes the scoped Focus browser unchanged into the source-backed diagram surface", async () => {
    const diagramTab: WorkspaceTab = {
      id: "diagram:focuses",
      familyId: "focuses",
      kind: "diagram"
    };
    const focusBrowser: ProjectBrowserPayload = {
      ...browser,
      filters: { family: "focus_tree" },
      families: [
        {
          id: "focuses",
          family: "focus_tree",
          title: "Focus trees",
          item_count: 1,
          source_count: 1,
          layouts: ["canonical"]
        }
      ],
      items: [
        {
          ...browser.items[0],
          id: "module:focus_tree/C01_MAIN",
          family_id: "focuses",
          family: "focus_tree",
          object_id: "C01_MAIN",
          module_id: "focus_tree/C01_MAIN",
          title: "C01 Main",
          root:
            `${activeProject.path}/src/modules/focus_tree/C01_MAIN`,
          relative_root:
            "src/modules/focus_tree/C01_MAIN"
        }
      ]
    };
    const selection: WorkspaceModuleSelectionTarget = {
      entityId: "module:focus_tree/C01_MAIN",
      familyId: "focuses"
    };
    const workspace = cloneElement(moduleWorkspace(selection), {
      activeTab: diagramTab.id,
      activeWorkspaceTab: diagramTab,
      browser: focusBrowser,
      openTabs: [diagramTab]
    });

    renderToStaticMarkup(workspace);
    await vi.dynamicImportSettled();
    renderToStaticMarkup(workspace);

    expect(mocks.moduleEditorProps.at(-1)).toMatchObject({
      browser: focusBrowser,
      familyId: "focuses",
      projectRoot: activeProject.path,
      selectedEntityId:
        "module:focus_tree/C01_MAIN",
      surface: "diagram"
    });
  });

  it("passes project path open actions into the config Projects tab", () => {
    const configPageSettings = normalizeConfigPageSettings({ hoi4: { gameRoot: "/Games/Hearts of Iron IV" } });
    const configTab: WorkspaceTab = { id: "config-projects", titleKey: "config.projects.title", kind: "config" };
    const markup = renderToStaticMarkup(
      <Workspace
        activeFeature={activeFeature}
        activeProject={activeProject}
        activeTab={configTab.id}
        activeWorkspaceTab={configTab}
        aiChatDefaultRole="chat"
        aiChatProfiles={[]}
        browser={null}
        configPageSettings={configPageSettings}
        dependencyBusyId=""
        dependencyStatusById={{}}
        inspectorOpen={false}
        llmStatus={defaultConfigLlmStatus(configPageSettings.llm)}
        locale="en"
        onCheckDependency={() => undefined}
        onCloseTab={() => undefined}
        onConfigPageSettingsChange={() => undefined}
        onInstallDependency={() => undefined}
        onLocaleChange={() => undefined}
        onOpenPath={() => undefined}
        onOpenTargetChange={() => undefined}
        onProjectRefresh={async () => undefined}
        onResetAiChatProfile={() => undefined}
        onSaveAiChatProfile={() => undefined}
        onSplitToggle={() => undefined}
        onTabPin={() => undefined}
        onTabSelect={() => undefined}
        onTestLlm={() => undefined}
        onThemeChange={() => undefined}
        openTarget="finder"
        openTabs={[configTab]}
        projectOptions={[activeProject]}
        secondaryTab=""
        secondaryWorkspaceTab={null}
        setSecondaryTab={() => undefined}
        splitView={false}
        surfaceRows={[]}
        templates={null}
        t={createTranslator("en")}
        theme="light"
      />
    );

    expect(markup).toContain('data-config-open-path="/workspace/projects/PIHC3"');
    expect(markup).toContain('data-config-open-path="/workspace/projects/PIHC3/src"');
    expect(markup).toContain('data-config-open-path="/workspace/projects/PIHC3/build/mod"');
    expect(markup).toContain('data-config-open-path="/workspace/projects/PIHC3/.paradev/.cache/build"');
    expect(markup).toContain('data-config-open-path="/Games/Hearts of Iron IV"');
    expect(markup).toContain('title="Open project root (/workspace/projects/PIHC3) with Finder"');
  });
});

function moduleWorkspace(moduleSelectionTarget: WorkspaceModuleSelectionTarget) {
  const configPageSettings = normalizeConfigPageSettings({});
  return (
    <Workspace
      activeFeature={activeFeature}
      activeProject={activeProject}
      activeTab={moduleTab.id}
      activeWorkspaceTab={moduleTab}
      aiChatDefaultRole="chat"
      aiChatProfiles={[]}
      browser={browser}
      configPageSettings={configPageSettings}
      dependencyBusyId=""
      dependencyStatusById={{}}
      inspectorOpen={false}
      llmStatus={defaultConfigLlmStatus(configPageSettings.llm)}
      locale="en"
      moduleSelectionTarget={moduleSelectionTarget}
      onCheckDependency={() => undefined}
      onCloseTab={() => undefined}
      onConfigPageSettingsChange={() => undefined}
      onInstallDependency={() => undefined}
      onLocaleChange={() => undefined}
      onModuleSelectionTargetChange={() => undefined}
      onOpenPath={() => undefined}
      onOpenTargetChange={() => undefined}
      onProjectRefresh={async () => undefined}
      onResetAiChatProfile={() => undefined}
      onSaveAiChatProfile={() => undefined}
      onSplitToggle={() => undefined}
      onTabPin={() => undefined}
      onTabSelect={() => undefined}
      onTestLlm={() => undefined}
      onThemeChange={() => undefined}
      openTarget="finder"
      openTabs={[moduleTab]}
      projectOptions={[activeProject]}
      secondaryTab=""
      secondaryWorkspaceTab={null}
      setSecondaryTab={() => undefined}
      splitView={false}
      surfaceRows={[]}
      templates={null}
      t={createTranslator("en")}
      theme="light"
    />
  );
}
