import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";
import { aiChatProfileOperationCards } from "../aiChatOperations";
import { PARADEV_DESKTOP_AI_CHAT_PROFILES } from "../generated/desktopContract";
import { createTranslator } from "../i18n";
import type { ParaDevAiChatProfile, ParaDevAiChatSource, ParaDevAiChatSourceKindRow } from "../services/paradev";
import {
  FloatingChatShell,
  aiChatRouteLabel,
  aiChatSelectedContextSummary,
  nextSelectedSourceIdsForContextChange,
  shouldSubmitAiChatComposerKey
} from "./FloatingChatShell";

const t = createTranslator("en");
const zh = createTranslator("zh");
const profiles: ParaDevAiChatProfile[] = PARADEV_DESKTOP_AI_CHAT_PROFILES.map((profile) => ({
  ...profile,
  sourceKinds: Array.from(profile.sourceKinds)
}));

describe("FloatingChatShell", () => {
  it("renders a compact launcher when closed", () => {
    const markup = renderToStaticMarkup(
      <FloatingChatShell
        activeProjectName="PIHC3"
        blocked={false}
        gateway="openai"
        model="deepseek-v4-flash"
        profiles={profiles}
        onSend={async () => "ok"}
        open={false}
        preset="chat"
        provider="deepseek"
        t={t}
      />
    );

    expect(markup).toContain('data-paradev-chat-shell="true"');
    expect(markup).toContain('data-paradev-chat-launcher="true"');
    expect(markup).toContain('aria-expanded="false"');
    expect(markup).toContain('aria-label="Open AI chat"');
    expect(markup).not.toContain('data-paradev-chat-panel="true"');
  });

  it("renders the chat panel, route, transcript, input, and send controls when open", () => {
    const markup = renderToStaticMarkup(
      <FloatingChatShell
        activeProjectName="PIHC3"
        avoidInspector={true}
        blocked={false}
        gateway="openai"
        model="deepseek-v4-flash"
        profiles={profiles}
        contextSources={[
          { kind: "workspace", label: "Focus trees", familyId: "focus_tree" },
          { kind: "diagnostics", label: "Diagnostics (2)", contentChars: 162, truncated: false }
        ]}
        onSend={async () => "ok"}
        open={true}
        preset="chat"
        provider="deepseek"
        t={t}
      />
    );

    expect(markup).toContain('class="ai-chat-shell open avoid-inspector"');
    expect(markup).toContain('data-paradev-chat-panel="true"');
    expect(markup).toContain('aria-label="AI chat"');
    expect(markup).toContain("AI chat");
    expect(markup).toContain("PIHC3");
    expect(markup).toContain("Explain HoI4 code");
    expect(markup).toContain("General ParaDev and HoI4 modding help.");
    expect(markup).toContain('title="General ParaDev and HoI4 modding help."');
    expect(markup).toContain('aria-describedby="');
    expect(markup).toMatch(/<small id="[^"]+" title="General ParaDev and HoI4 modding help\.">General ParaDev and HoI4 modding help\.<\/small>/);
    expect(markup).toContain('class="select-field compact ai-chat-role-select"');
    expect(markup).toContain('aria-label="Task"');
    expect(markup).toContain('data-paradev-chat-role="true"');
    expect(markup).toContain('data-paradev-chat-source="true"');
    expect(markup).toContain('data-paradev-chat-source-kind="diagnostics"');
    expect(markup).toContain("Focus trees");
    expect(markup).toContain("Diagnostics (2)");
    expect(sourceOptionMarkup(markup, "workspace")).toContain('class="ai-chat-source-option selected"');
    expect(sourceOptionMarkup(markup, "workspace")).toContain('data-paradev-chat-source-selected="true"');
    expect(sourceOptionMarkup(markup, "diagnostics")).toContain('data-paradev-chat-source-selected="false"');
    expect(contextSummaryMarkup(markup)).toContain("Context: Focus trees");
    expect(markup).toContain("Preset: Chat");
    expect(markup).toContain('title="Preset: Chat · Gateway: OpenAI · Provider: DeepSeek · Model: DeepSeek v4 Flash"');
    expect(markup).toContain("Gateway: OpenAI");
    expect(markup).toContain("Provider: DeepSeek");
    expect(markup).toContain("Model: DeepSeek v4 Flash");
    expect(markup).not.toContain("openai / deepseek");
    expect(markup).not.toContain("deepseek-v4-flash");
    expect(markup).toContain("No messages yet");
    expect(markup).toContain('data-paradev-chat-input="true"');
    expect(markup).toContain('placeholder="Ask ParaDev"');
    expect(markup).toContain('data-paradev-chat-send="true"');
    expect(markup).toContain('aria-label="Send"');
  });

  it("exposes selected source file paths on context chips", () => {
    const sourcePath = "src/modules/focus_tree/C01_MAIN/info.json";
    const markup = renderToStaticMarkup(
      <FloatingChatShell
        activeProjectName="PIHC3"
        blocked={false}
        contextSources={[{ kind: "source", label: "National Focuses: C01_MAIN", detail: sourcePath, path: sourcePath }]}
        gateway="openai"
        model="deepseek-v4-flash"
        profiles={profiles}
        onSend={async () => "ok"}
        open={true}
        preset="chat"
        provider="deepseek"
        t={t}
      />
    );

    expect(markup).toContain(`title="National Focuses: C01_MAIN · ${sourcePath}"`);
    expect(markup).toContain('class="ai-chat-source-detail"');
    expect(sourceInputMarkup(markup, "source")).not.toContain("checked");
    expect(sourceOptionMarkup(markup, "source")).toContain('data-paradev-chat-source-selected="false"');
    expect(contextSummaryMarkup(markup)).toContain("No context attached");
    expect(markup).toContain(sourcePath);
  });

  it("renders side-docked chat with a dock toggle instead of a floating launcher", () => {
    const markup = renderToStaticMarkup(
      <FloatingChatShell
        activeProjectName="PIHC3"
        blocked={false}
        dock="side"
        gateway="openai"
        model="deepseek-v4-flash"
        profiles={profiles}
        onDockChange={() => undefined}
        onOpenChange={() => undefined}
        onSend={async () => "ok"}
        open={true}
        preset="chat"
        provider="deepseek"
        t={t}
      />
    );

    expect(markup).toContain('class="ai-chat-shell open dock-side"');
    expect(markup).toContain('data-paradev-chat-dock="side"');
    expect(markup).toContain('data-paradev-chat-dock-toggle="true"');
    expect(markup).toContain('aria-label="Float AI chat"');
    expect(markup).not.toContain('data-paradev-chat-launcher="true"');
  });

  it("defaults selected context sources from the selected profile", () => {
    const markup = renderToStaticMarkup(
      <FloatingChatShell
        activeProjectName="PIHC3"
        blocked={false}
        gateway="openai"
        model="deepseek-v4-flash"
        profiles={profiles}
        contextSources={[
          { kind: "workspace", label: "Workspace state", familyId: "focus_tree" },
          { kind: "diagnostics", label: "Diagnostics (2)", contentChars: 162, truncated: false }
        ]}
        onSend={async () => "ok"}
        open={true}
        preset="chat"
        provider="deepseek"
        t={t}
      />
    );

    expect(sourceInputMarkup(markup, "workspace")).toContain("checked");
    expect(sourceInputMarkup(markup, "diagnostics")).not.toContain("checked");
  });

  it("honors the SDK default role when choosing the initial task and context", () => {
    const markup = renderToStaticMarkup(
      <FloatingChatShell
        activeProjectName="PIHC3"
        blocked={false}
        defaultRole="build"
        gateway="openai"
        model="deepseek-v4-flash"
        profiles={profiles}
        onOperationNavigate={() => undefined}
        contextSources={[
          { kind: "workspace", label: "Workspace state", familyId: "focus_tree" },
          { kind: "diagnostics", label: "Diagnostics (2)", contentChars: 162, truncated: false },
          { kind: "source", label: "Selected source", path: "src/modules/focus_tree/C01_MAIN/info.json" }
        ]}
        onSend={async () => "ok"}
        open={true}
        preset="chat"
        provider="deepseek"
        t={t}
      />
    );

    expect(optionMarkup(markup, "build")).toContain("selected");
    expect(optionMarkup(markup, "chat")).not.toContain("selected");
    expect(markup).toContain("Explain build commands, diagnostics, artifacts, and safe next actions.");
    expect(markup).toContain("SDK actions");
    expect(markup).toContain("Shown for planning; chat will not run actions.");
    expect(operationCardMarkup(markup, "build.plan")).toContain("Build Plan");
    expect(operationCardMarkup(markup, "build.plan")).toContain("Project.build");
    expect(operationCardMarkup(markup, "build.start")).toContain("Build Start");
    expect(operationCardMarkup(markup, "build.start")).toContain("desktop_start_build");
    expect(operationCardMarkup(markup, "build.start")).toContain('type="button"');
    expect(operationCardMarkup(markup, "build.start")).toContain('data-paradev-chat-operation-action="navigate"');
    expect(operationCardMarkup(markup, "build.start")).toContain('data-paradev-chat-operation-passive="true"');
    expect(operationCardMarkup(markup, "build.start")).toContain("Open Build page");
    expect(operationCardMarkup(markup, "build.start")).toContain("Does not start a build.");
    expect(operationCardMarkup(markup, "build.start")).toContain('aria-label="Open Build page; Does not start a build."');
    expect(markup).not.toContain('data-paradev-operation-id="build.start"');
    expect(sourceInputMarkup(markup, "workspace")).toContain("checked");
    expect(sourceInputMarkup(markup, "diagnostics")).toContain("checked");
    expect(sourceInputMarkup(markup, "source")).not.toContain("checked");
    expect(contextSummaryMarkup(markup)).toContain("Context: Workspace state, Diagnostics (2)");
  });

  it("summarizes attached contexts with localized selected-file wording", () => {
    expect(
      aiChatSelectedContextSummary(
        [
          { kind: "source", label: "National Focuses: C01_MAIN", path: "src/modules/focus_tree/C01_MAIN/info.json" },
          { kind: "diagnostics", label: "Diagnostics (2)" },
          { kind: "source", label: "National Focuses: C02_MAIN", path: "src/modules/focus_tree/C02_MAIN/info.json" }
        ],
        t
      )
    ).toBe("Context: Selected file, Diagnostics (2)");
    expect(aiChatSelectedContextSummary([], zh)).toBe("未附加上下文");
  });

  it("uses SDK source kind rows when mapping profile defaults to frontend context kinds", () => {
    const sourceKindRows: ParaDevAiChatSourceKindRow[] = [
      { id: "project-index", label: "Project index", frontendKinds: ["catalog"] }
    ];
    const profile = {
      id: "project-index",
      label: "Explain project index",
      detail: "Use catalog-backed project index context.",
      prompt: "Explain the indexed project context.",
      sourceKinds: ["project-index"]
    } as ParaDevAiChatProfile;

    expect(
      nextSelectedSourceIdsForContextChange(
        [],
        [],
        [{ id: "catalog:project", kind: "catalog", label: "Project index" }],
        profile,
        sourceKindRows
      )
    ).toEqual(["catalog:project"]);
  });

  it("preserves manually deselected source kinds when workspace context refreshes", () => {
    const previousSources: ParaDevAiChatSource[] = [
      { id: "workspace:project", kind: "workspace", label: "Project" },
      { id: "diagnostics:old", kind: "diagnostics", label: "Diagnostics (1)" }
    ];
    const nextSources: ParaDevAiChatSource[] = [
      { id: "workspace:project", kind: "workspace", label: "Project" },
      { id: "diagnostics:new", kind: "diagnostics", label: "Diagnostics (2)" }
    ];

    expect(nextSelectedSourceIdsForContextChange(["workspace:project"], previousSources, nextSources, profileById("build"))).toEqual(["workspace:project"]);
  });

  it("carries selected source kinds to refreshed workspace source ids", () => {
    const previousSources: ParaDevAiChatSource[] = [
      { id: "workspace:focus_tree", kind: "workspace", label: "Focus trees" },
      { id: "source:old", kind: "source", label: "Old selected file", path: "src/old.txt" }
    ];
    const nextSources: ParaDevAiChatSource[] = [
      { id: "workspace:focus_tree", kind: "workspace", label: "Focus trees" },
      { id: "source:new", kind: "source", label: "New selected file", path: "src/new.txt" }
    ];

    expect(nextSelectedSourceIdsForContextChange(["workspace:focus_tree", "source:old"], previousSources, nextSources, profileById("explain"))).toEqual([
      "workspace:focus_tree",
      "source:new"
    ]);
  });

  it("selects newly available source kinds when the active profile enables them by default", () => {
    const previousSources: ParaDevAiChatSource[] = [{ id: "workspace:project", kind: "workspace", label: "Project" }];
    const nextSources: ParaDevAiChatSource[] = [
      { id: "workspace:project", kind: "workspace", label: "Project" },
      { id: "templates:project", kind: "templates", label: "Templates" }
    ];

    expect(nextSelectedSourceIdsForContextChange(["workspace:project"], previousSources, nextSources, profileById("create-module"))).toEqual([
      "workspace:project",
      "templates:project"
    ]);
  });

  it("shows the SDK create-module role detail and default template context", () => {
    const markup = renderToStaticMarkup(
      <FloatingChatShell
        activeProjectName="PIHC3"
        blocked={false}
        contextSources={[
          { kind: "workspace", label: "Workspace state", familyId: "focus_tree" },
          { kind: "templates", label: "Templates (8)", contentChars: 240, truncated: false },
          { kind: "diagnostics", label: "Diagnostics (2)", contentChars: 162, truncated: false }
        ]}
        defaultRole="create-module"
        gateway="openai"
        model="deepseek-v4-flash"
        profiles={profiles}
        onOperationNavigate={() => undefined}
        onSend={async () => "ok"}
        open={true}
        preset="chat"
        provider="deepseek"
        t={t}
      />
    );

    expect(optionMarkup(markup, "create-module")).toContain("selected");
    expect(markup).toContain("Create content plan");
    expect(markup).toContain("Plan new modules or collections through ParaDev templates before writing source files.");
    expect(markup).toContain('title="Plan new modules or collections through ParaDev templates before writing source files."');
    expect(sourceInputMarkup(markup, "workspace")).toContain("checked");
    expect(sourceInputMarkup(markup, "templates")).toContain("checked");
    expect(sourceInputMarkup(markup, "diagnostics")).not.toContain("checked");
    expect(operationCardMarkup(markup, "module.draft")).toContain("Module Draft");
    expect(operationCardMarkup(markup, "module.draft")).toContain("Project.create_module_draft");
    expect(operationCardMarkup(markup, "module.draft")).toContain('data-paradev-chat-operation-action="navigate"');
    expect(operationCardMarkup(markup, "module.draft")).toContain('data-paradev-chat-operation-passive="true"');
    expect(operationCardMarkup(markup, "module.draft")).toContain("Open module draft planner");
    expect(operationCardMarkup(markup, "module.draft")).toContain("Does not create files.");
    expect(operationCardMarkup(markup, "module.draft")).toContain("Write-capable");
    expect(contextSummaryMarkup(markup)).toContain("Context: Workspace state, Templates (8)");
  });

  it("renders compact profile operation cards from the SDK-owned profile payload", () => {
    const cards = aiChatProfileOperationCards({
      operationCards: [
        {
          id: "module.draft",
          mutates: true,
          rest: "POST /projects/{project_id}/modules/{family_id}/drafts",
          sdk: "Project.create_module_draft",
          summary: "Plan or write a source-module draft from a frontend browser family id.",
          title: "Module Draft"
        },
        {
          id: "missing" as never,
          mutates: false,
          rest: "",
          sdk: "",
          summary: "",
          title: ""
        }
      ]
    } as unknown as ParaDevAiChatProfile);

    expect(cards.map((card) => card.operation.id)).toEqual(["module.draft"]);
    expect(cards[0]?.sdkLabel).toBe("Project.create_module_draft");
    expect(cards[0]?.restLabel).toBe("POST /projects/{project_id}/modules/{family_id}/drafts");
  });

  it("renders built-in role labels and details through the selected locale", () => {
    const markup = renderToStaticMarkup(
      <FloatingChatShell
        activeProjectName="PIHC3"
        blocked={false}
        defaultRole="create-module"
        gateway="openai"
        model="deepseek-v4-flash"
        profiles={profiles}
        onSend={async () => "ok"}
        open={true}
        preset="chat"
        provider="deepseek"
        t={zh}
      />
    );

    expect(markup).toContain("创建内容计划");
    expect(markup).toContain("先通过 ParaDev 模板规划新模块或集合，再写入源文件。");
    expect(markup).toContain("说明 HOI4 代码");
    expect(markup).not.toContain("Plan new modules through ParaDev templates before writing source files.");
    expect(markup).not.toContain("Explain HoI4 code");
  });

  it("renders managed SDK operation cards through the selected locale", () => {
    const markup = renderToStaticMarkup(
      <FloatingChatShell
        activeProjectName="PIHC3"
        blocked={false}
        defaultRole="build"
        gateway="openai"
        model="deepseek-v4-flash"
        profiles={profiles}
        onOperationNavigate={() => undefined}
        onSend={async () => "ok"}
        open={true}
        preset="chat"
        provider="deepseek"
        t={zh}
      />
    );

    expect(operationCardMarkup(markup, "build.plan")).toContain("构建计划");
    expect(operationCardMarkup(markup, "build.plan")).toContain("运行一次只读构建计划。");
    expect(operationCardMarkup(markup, "build.plan")).not.toContain("Build Plan");
    expect(operationCardMarkup(markup, "build.plan")).not.toContain("Run a dry build plan.");
    expect(operationCardMarkup(markup, "build.start")).toContain("启动构建");
    expect(operationCardMarkup(markup, "build.start")).toContain("通过 Python 桌面门面启动一次桌面构建。");
    expect(operationCardMarkup(markup, "build.start")).not.toContain("Build Start");
    expect(operationCardMarkup(markup, "build.start")).not.toContain("Start one desktop build run through the Python desktop facade.");
  });

  it("falls back to raw SDK detail text for future custom profiles", () => {
    const markup = renderToStaticMarkup(
      <FloatingChatShell
        activeProjectName="PIHC3"
        blocked={false}
        defaultRole="custom-review"
        gateway="openai"
        model="deepseek-v4-flash"
        profiles={[
          {
            id: "custom-review",
            label: "Review migration",
            detail: "Custom SDK-supplied review detail.",
            prompt: "Review the migration.",
            sourceKinds: ["project"]
          }
        ]}
        onSend={async () => "ok"}
        open={true}
        preset="chat"
        provider="deepseek"
        t={zh}
      />
    );

    expect(markup).toContain("Review migration");
    expect(markup).toContain("Custom SDK-supplied review detail.");
    expect(markup).toContain('title="Custom SDK-supplied review detail."');
  });

  it("surfaces AI profile load failures without hiding loaded roles", () => {
    const markup = renderToStaticMarkup(
      <FloatingChatShell
        activeProjectName="PIHC3"
        blocked={false}
        gateway="openai"
        model="deepseek-v4-flash"
        profileLoadError="AI chat profiles could not be loaded: bridge denied"
        profiles={profiles}
        onSend={async () => "ok"}
        open={true}
        preset="chat"
        provider="deepseek"
        t={t}
      />
    );

    expect(markup).toContain('role="alert"');
    expect(markup).toContain("AI chat profiles could not be loaded: bridge denied");
    expect(markup).toContain("Explain HoI4 code");
    expect(markup).toContain('data-paradev-chat-role="true"');
  });

  it("localizes the AI chat route label and avoids raw backend IDs", () => {
    expect(
      aiChatRouteLabel({
        gateway: "openrouter",
        model: "deepseek-reasoner",
        preset: "reason",
        provider: "deepseek",
        t
      })
    ).toBe("Preset: Reason · Gateway: OpenRouter · Provider: DeepSeek · Model: DeepSeek Reasoner");
    expect(
      aiChatRouteLabel({
        gateway: "openrouter",
        model: "deepseek-reasoner",
        preset: "reason",
        provider: "deepseek",
        t: zh
      })
    ).toBe("预设：推理 · 网关：OpenRouter · 提供方：DeepSeek · 模型：DeepSeek Reasoner");
    expect(
      aiChatRouteLabel({
        gateway: "",
        model: "",
        preset: "",
        provider: "deepseek",
        t: zh
      })
    ).toBe("预设：默认 · 网关：默认 · 提供方：DeepSeek · 模型：默认");
  });

  it("translates unlabeled source-kind fallbacks in Chinese", () => {
    const markup = renderToStaticMarkup(
      <FloatingChatShell
        activeProjectName="PIHC3"
        blocked={false}
        contextSources={[{ kind: "workspace" }]}
        gateway="openai"
        model="deepseek-v4-flash"
        profiles={profiles}
        onSend={async () => "ok"}
        open={true}
        preset="chat"
        provider="deepseek"
        t={zh}
      />
    );

    expect(markup).toContain(">项目</span>");
    expect(markup).toContain('aria-label="附加 项目"');
    expect(markup).not.toContain(">workspace</span>");
    expect(markup).not.toContain('aria-label="附加 workspace"');
  });

  it("uses localized known source labels instead of raw internal source kinds", () => {
    const markup = renderToStaticMarkup(
      <FloatingChatShell
        activeProjectName="PIHC3"
        blocked={false}
        contextSources={[{ kind: "scripted-gui" }]}
        gateway="openai"
        model="deepseek-v4-flash"
        profiles={profiles}
        onSend={async () => "ok"}
        open={true}
        preset="chat"
        provider="deepseek"
        t={zh}
      />
    );

    expect(markup).toContain(">脚本 GUI</span>");
    expect(markup).toContain('aria-label="附加 脚本 GUI"');
    expect(markup).not.toContain(">scripted-gui</span>");
    expect(markup).not.toContain('aria-label="附加 scripted-gui"');
  });

  it("submits the composer on Cmd or Ctrl Enter only", () => {
    expect(shouldSubmitAiChatComposerKey({ key: "Enter", metaKey: true })).toBe(true);
    expect(shouldSubmitAiChatComposerKey({ key: "Enter", ctrlKey: true })).toBe(true);
    expect(shouldSubmitAiChatComposerKey({ key: "Enter" })).toBe(false);
    expect(shouldSubmitAiChatComposerKey({ key: "Enter", metaKey: true, shiftKey: true })).toBe(false);
    expect(shouldSubmitAiChatComposerKey({ key: "Enter", altKey: true, ctrlKey: true })).toBe(false);
    expect(shouldSubmitAiChatComposerKey({ key: "Enter", isComposing: true, metaKey: true })).toBe(false);
    expect(shouldSubmitAiChatComposerKey({ key: "NumpadEnter", metaKey: true })).toBe(false);
  });

  it("does not render while boot progress blocks the shell", () => {
    const markup = renderToStaticMarkup(
      <FloatingChatShell
        activeProjectName="PIHC3"
        blocked={true}
        gateway="openai"
        model="deepseek-v4-flash"
        profiles={profiles}
        onSend={async () => "ok"}
        open={true}
        preset="chat"
        provider="deepseek"
        t={t}
      />
    );

    expect(markup).toBe("");
  });
});

function sourceInputMarkup(markup: string, kind: string): string {
  const match = new RegExp(`<input[^>]*data-paradev-chat-source-kind="${kind}"[^>]*>`).exec(markup);
  expect(match).not.toBeNull();
  return match?.[0] ?? "";
}

function sourceOptionMarkup(markup: string, kind: string): string {
  const match = new RegExp(`<label[^>]*data-paradev-chat-source-selected="[^"]*"[^>]*>.*?<input[^>]*data-paradev-chat-source-kind="${kind}"[^>]*>.*?</label>`).exec(
    markup
  );
  expect(match).not.toBeNull();
  return match?.[0] ?? "";
}

function operationCardMarkup(markup: string, operationId: string): string {
  const match = new RegExp(`<button[^>]*data-paradev-chat-operation-id="${operationId}"[^>]*>.*?</button>`).exec(markup);
  expect(match).not.toBeNull();
  return match?.[0] ?? "";
}

function contextSummaryMarkup(markup: string): string {
  const match = /<small[^>]*data-paradev-chat-context-summary="true"[^>]*>.*?<\/small>/.exec(markup);
  expect(match).not.toBeNull();
  return match?.[0] ?? "";
}

function optionMarkup(markup: string, value: string): string {
  const match = new RegExp(`<option[^>]*value="${value}"[^>]*>`).exec(markup);
  expect(match).not.toBeNull();
  return match?.[0] ?? "";
}

function profileById(id: string): ParaDevAiChatProfile {
  const profile = profiles.find((item) => item.id === id);
  expect(profile).toBeDefined();
  return profile as ParaDevAiChatProfile;
}
