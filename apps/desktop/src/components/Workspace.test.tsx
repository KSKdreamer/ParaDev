import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it, vi } from "vitest";
import { createTranslator } from "../i18n";
import { en } from "../i18n/locales/en";
import { zh } from "../i18n/locales/zh";
import { diagramTabIdForModule } from "../projectModules";
import type { FeatureModule, ProjectBrowserPayload, WorkspaceTab } from "../types";
import { Workspace } from "./Workspace";

const activeFeature: FeatureModule = {
  id: "countries",
  titleKey: "modules.countries.title",
  status: "ready"
};

const focusBrowser: ProjectBrowserPayload = {
  schema: "paradev.sdk.project-browser.v1",
  project_id: "PIHC3",
  title: "PIHC3",
  root: "/workspace/PIHC3",
  profile: "hoi4",
  filters: {},
  diagnostics: [],
  items: [],
  families: [
    {
      id: "focuses",
      family: "focus",
      title: "Focuses",
      title_key: "modules.focuses.title",
      item_count: 1,
      source_count: 1,
      layouts: ["canonical"],
      diagram: {
        id: "focus_tree",
        aliases: ["focus", "focuses"],
        renderer: "focus-tree",
        title: "Focus tree",
        editable: true,
        authoring_kind: "diagram-node"
      }
    }
  ]
};

const mioBrowser: ProjectBrowserPayload = {
  ...focusBrowser,
  families: [
    {
      id: "military-industrial-organizations",
      family: "military_industrial_organization",
      title: "Military Industrial Organizations",
      item_count: 1,
      source_count: 1,
      layouts: ["canonical"],
      diagram: {
        id: "military_industrial_organization",
        aliases: ["mio"],
        renderer: "mio-trait",
        title: "Military Industrial Organization tree",
        editable: true,
        authoring_kind: "module"
      }
    }
  ]
};

function renderEmptyWorkspace() {
  return renderWorkspace({ t: createTranslator("en") });
}

function renderWorkspace(overrides: Partial<Parameters<typeof Workspace>[0]> = {}) {
  const t = overrides.t ?? createTranslator("en");
  const props = {
    activeFeature,
    aiChatDefaultRole: "chat",
    aiChatProfiles: [],
    activeTab: overrides.activeTab ?? "",
    activeWorkspaceTab: overrides.activeWorkspaceTab ?? null,
    browser: null,
    inspectorOpen: false,
    locale: "en",
    onCloseTab: () => undefined,
    onProjectRefresh: async () => undefined,
    onResetAiChatProfile: () => undefined,
    onSaveAiChatProfile: () => undefined,
    onSplitToggle: () => undefined,
    onTabSelect: () => undefined,
    openTarget: "finder",
    openTabs: overrides.openTabs ?? [],
    secondaryTab: "",
    secondaryWorkspaceTab: null,
    setSecondaryTab: () => undefined,
    splitView: false,
    surfaceRows: overrides.surfaceRows ?? [],
    templates: null,
    t,
    theme: "light",
    ...overrides
  } as unknown as Parameters<typeof Workspace>[0];

  return renderToStaticMarkup(<Workspace {...props} />);
}

describe("Workspace", () => {
  it("renders the no-tab state without the removed add-tab action", () => {
    const markup = renderEmptyWorkspace();

    expect(markup).toContain("Choose a module or config item from the left panel.");
    expect(markup).not.toContain("Open next tab");
    expect(markup).not.toContain("plus button");
  });

  it("does not expose add-tab translation keys", () => {
    expect("workspace.action.openNextTab" in en).toBe(false);
    expect("workspace.action.openNextTab" in zh).toBe(false);
  });

  it("renders the empty workspace and inspector label in Chinese without English fallbacks", () => {
    const markup = renderWorkspace({
      inspectorOpen: true,
      locale: "zh",
      t: createTranslator("zh")
    } as Partial<Parameters<typeof Workspace>[0]>);

    expect(markup).toContain("没有打开的标签页");
    expect(markup).toContain("检查器");
    expect(markup).not.toContain("No tabs open");
    expect(markup).not.toContain("Inspector");
  });

  it("localizes preview tab titles in Chinese", () => {
    const moduleTab: WorkspaceTab = { id: "countries", kind: "module", titleKey: "modules.countries.title" };
    const markup = renderWorkspace({
      activeTab: moduleTab.id,
      activeWorkspaceTab: moduleTab,
      locale: "zh",
      openTabs: [moduleTab],
      t: createTranslator("zh")
    } as Partial<Parameters<typeof Workspace>[0]>);

    expect(markup).toContain('title="国家（预览）"');
    expect(markup).not.toContain("(preview)");
  });

  it("marks dirty tabs visually and in their accessible name", () => {
    const moduleTab: WorkspaceTab = {
      dirty: true,
      id: "countries",
      kind: "module",
      titleKey: "modules.countries.title"
    };
    const markup = renderWorkspace({
      activeTab: moduleTab.id,
      activeWorkspaceTab: moduleTab,
      openTabs: [moduleTab]
    });

    expect(markup).toContain("tab-dirty-indicator");
    expect(markup).toContain('aria-label="Countries, unsaved changes"');
  });

  it("renders surface table labels and statuses in Chinese", () => {
    const surfaceTab: WorkspaceTab = { id: "surface-contracts", kind: "surface", title: "Surface contracts" };
    const markup = renderWorkspace({
      activeTab: surfaceTab.id,
      activeWorkspaceTab: surfaceTab,
      locale: "zh",
      openTabs: [surfaceTab],
      surfaceRows: [
        { id: "sdk", path: "src/paradev/sdk", runtime: "python", status: "ready", titleKey: "surface.sdk.title" },
        { id: "mcp", path: "src/paradev/surfaces/mcp.py", runtime: "heavenbase-mcp", status: "scaffold", titleKey: "surface.mcp.title" },
        { id: "bundle", path: "src/paradev/surfaces/bundle.py", runtime: "python-bundle", status: "planned", titleKey: "surface.bundle.title" }
      ],
      t: createTranslator("zh")
    } as Partial<Parameters<typeof Workspace>[0]>);

    expect(markup).toContain("接口");
    expect(markup).toContain("运行时");
    expect(markup).toContain("就绪");
    expect(markup).toContain("脚手架");
    expect(markup).toContain("规划中");
    expect(markup).toContain("Python SDK");
    expect(markup).toContain("MCP 工具包");
    expect(markup).not.toContain(">Status<");
    expect(markup).not.toContain(">ready<");
    expect(markup).not.toContain(">scaffold<");
    expect(markup).not.toContain(">planned<");
  });

  it("marks diagram tabs separately from normal module tabs", () => {
    const t = createTranslator("en");
    const moduleTab = { id: "focuses", titleKey: "modules.focuses.title", kind: "module" } as const;
    const diagramTab = { id: diagramTabIdForModule("focuses"), familyId: "focuses", kind: "diagram" } as const;
    const props = {
      activeFeature,
      activeTab: diagramTab.id,
      activeWorkspaceTab: diagramTab,
      browser: focusBrowser,
      inspectorOpen: false,
      locale: "en",
      onCloseTab: () => undefined,
      onProjectRefresh: async () => undefined,
      onSplitToggle: () => undefined,
      onTabPin: () => undefined,
      onTabSelect: () => undefined,
      openTarget: "finder",
      openTabs: [moduleTab, diagramTab],
      secondaryTab: "",
      secondaryWorkspaceTab: null,
      setSecondaryTab: () => undefined,
      splitView: false,
      surfaceRows: [],
      templates: null,
      t,
      theme: "light"
    } as unknown as Parameters<typeof Workspace>[0];

    const markup = renderToStaticMarkup(<Workspace {...props} />);

    expect(markup).toContain('data-tab-kind="module"');
    expect(markup).toContain('data-tab-kind="diagram"');
    expect(markup).toContain("diagram-tab");
    expect(markup).toContain("tab-kind-icon");
    expect(markup).toContain("Focus tree");
  });

  it("passes active scoped loading state into the diagram workspace pane", async () => {
    const t = createTranslator("en");
    const diagramTab = { id: diagramTabIdForModule("focuses"), familyId: "focuses", kind: "diagram" } as const;
    const props = {
      activeBrowserLoading: true,
      activeFeature,
      activeTab: diagramTab.id,
      activeWorkspaceTab: diagramTab,
      browser: focusBrowser,
      inspectorOpen: false,
      locale: "en",
      onCloseTab: () => undefined,
      onOpenDiagramTab: () => undefined,
      onProjectRefresh: async () => undefined,
      onSplitToggle: () => undefined,
      onTabPin: () => undefined,
      onTabSelect: () => undefined,
      openTarget: "finder",
      openTabs: [diagramTab],
      secondaryTab: "",
      secondaryWorkspaceTab: null,
      setSecondaryTab: () => undefined,
      splitView: false,
      surfaceRows: [],
      templates: null,
      t,
      theme: "light"
    } as unknown as Parameters<typeof Workspace>[0];

    renderToStaticMarkup(<Workspace {...props} />);
    await vi.dynamicImportSettled();
    const markup = renderToStaticMarkup(<Workspace {...props} />);

    expect(markup).toContain('class="empty-tab-panel module-loading-panel"');
    expect(markup).toContain("Loading National Focuses diagram");
  });

  it("offers a supported module tab action that opens its separate diagram tab", () => {
    const t = createTranslator("en");
    const moduleTab = { id: "focuses", titleKey: "modules.focuses.title", kind: "module" } as const;
    const props = {
      activeFeature,
      activeTab: moduleTab.id,
      activeWorkspaceTab: moduleTab,
      browser: focusBrowser,
      inspectorOpen: false,
      locale: "en",
      onCloseTab: () => undefined,
      onOpenDiagramTab: () => undefined,
      onProjectRefresh: async () => undefined,
      onSplitToggle: () => undefined,
      onTabPin: () => undefined,
      onTabSelect: () => undefined,
      openTarget: "finder",
      openTabs: [moduleTab],
      secondaryTab: "",
      secondaryWorkspaceTab: null,
      setSecondaryTab: () => undefined,
      splitView: false,
      surfaceRows: [],
      templates: null,
      t,
      theme: "light"
    } as unknown as Parameters<typeof Workspace>[0];

    const markup = renderToStaticMarkup(<Workspace {...props} />);

    expect(markup).toContain("Open Focus tree");
    expect(markup).toContain('class="toolbar-button workspace-open-diagram"');
    expect(markup).toContain("module-diagram-action-visible");
  });

  it("offers the PIHC3 MIO family action with a user-facing tree name", () => {
    const t = createTranslator("en");
    const moduleTab = {
      id: "military-industrial-organizations",
      titleKey: "modules.militaryIndustrialOrganizations.title",
      kind: "module"
    } as const;
    const props = {
      activeFeature,
      activeTab: moduleTab.id,
      activeWorkspaceTab: moduleTab,
      browser: mioBrowser,
      inspectorOpen: false,
      locale: "en",
      onCloseTab: () => undefined,
      onOpenDiagramTab: () => undefined,
      onProjectRefresh: async () => undefined,
      onSplitToggle: () => undefined,
      onTabPin: () => undefined,
      onTabSelect: () => undefined,
      openTarget: "finder",
      openTabs: [moduleTab],
      secondaryTab: "",
      secondaryWorkspaceTab: null,
      setSecondaryTab: () => undefined,
      splitView: false,
      surfaceRows: [],
      templates: null,
      t,
      theme: "light"
    } as unknown as Parameters<typeof Workspace>[0];

    const markup = renderToStaticMarkup(<Workspace {...props} />);

    expect(markup).toContain(
      "Open Military Industrial Organization trait tree"
    );
    expect(markup).toContain(
      'class="toolbar-button workspace-open-diagram"'
    );
  });

  it("does not offer an open-diagram action inside an existing diagram tab", () => {
    const t = createTranslator("en");
    const diagramTab = { id: diagramTabIdForModule("focuses"), familyId: "focuses", kind: "diagram" } as const;
    const props = {
      activeFeature,
      activeTab: diagramTab.id,
      activeWorkspaceTab: diagramTab,
      browser: null,
      inspectorOpen: false,
      locale: "en",
      onCloseTab: () => undefined,
      onOpenDiagramTab: () => undefined,
      onProjectRefresh: async () => undefined,
      onSplitToggle: () => undefined,
      onTabPin: () => undefined,
      onTabSelect: () => undefined,
      openTarget: "finder",
      openTabs: [diagramTab],
      secondaryTab: "",
      secondaryWorkspaceTab: null,
      setSecondaryTab: () => undefined,
      splitView: false,
      surfaceRows: [],
      templates: null,
      t,
      theme: "light"
    } as unknown as Parameters<typeof Workspace>[0];

    const markup = renderToStaticMarkup(<Workspace {...props} />);

    expect(markup).not.toContain("workspace-open-diagram");
  });
});
