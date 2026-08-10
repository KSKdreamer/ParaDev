import { readFileSync } from "node:fs";
import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it, vi } from "vitest";
import { DESKTOP_CONFIG_KEYS, DESKTOP_CONFIG_KEY_VALUES, type DesktopConfigKey } from "../desktopConfig";
import { PARADEV_DESKTOP_AI_CHAT_PROFILES, PARADEV_DESKTOP_CONFIG_DEFAULTS, PARADEV_DESKTOP_CONFIG_ROWS } from "../generated/desktopContract";
import { createTranslator, type Locale } from "../i18n";
import type { OpenPathTarget } from "../openPathTargets";
import type { DesktopPathStatusPayload, ParaDevAiChatProfile, ParaDevAiChatSourceKindRow } from "../services/paradev";
import type { ProjectOption, ThemeName } from "../types";
import { ConfigPage } from "./ConfigPage";
import { defaultConfigPageSettings, normalizeConfigPageSettings, type ConfigDependencyStatus, type ConfigLlmStatus, type ConfigPageSettings, type ConfigPersistenceStatus } from "./model";

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

const aiChatProfiles: ParaDevAiChatProfile[] = [
  {
    id: "chat",
    detailKey: "chat.profile.chat.detail",
    labelKey: "chat.profile.chat.label",
    promptKey: "chat.profile.chat.prompt",
    label: "Chat",
    detail: "General ParaDev and HoI4 modding help.",
    prompt: "Help a Hearts of Iron IV modder use ParaDev.",
    sourceKinds: ["project"]
  },
  {
    id: "explain",
    labelKey: "chat.profile.explain.label",
    label: "Explain HoI4 code",
    detail: "Custom PIHC3 source explanation.",
    prompt: "Prefer PIHC3 source files and name the SDK operation that should make changes.",
    sourceKinds: ["project", "selection", "diagnostics"]
  }
] as unknown as ParaDevAiChatProfile[];
const generatedAiChatProfiles: ParaDevAiChatProfile[] = PARADEV_DESKTOP_AI_CHAT_PROFILES.map((profile) => ({
  ...profile,
  sourceKinds: Array.from(profile.sourceKinds)
}));

function renderConfigPage(
  activeConfigId: string,
  locale: Locale = "en",
  dependencyStatus: ConfigDependencyStatus = {
    schema: "paradev.desktop.dependency.v1",
    id: "imagemagick",
    installed: true,
    installCommand: ["brew", "install", "imagemagick"],
    installSupported: true,
    label: "ImageMagick",
    path: "/opt/homebrew/bin/magick",
    status: "ready",
    version: "ImageMagick 7.1.2"
  },
  llmStatus: ConfigLlmStatus = {
    baseUrl: "https://api.deepseek.com/v1",
    gateway: "openai",
    keySource: "DEEPSEEK_API_KEY",
    model: "deepseek-v4-flash",
    preset: "chat",
    provider: "deepseek",
    resultCode: "empty_response",
    status: "warning",
    testDetail: "deepseek / deepseek-v4-flash route returned an empty response.",
    testedAt: "2026-06-28T00:00:00.000Z"
  },
  settings: ConfigPageSettings = defaultConfigPageSettings(),
  persistenceStatus: ConfigPersistenceStatus | undefined = undefined,
  profiles: ParaDevAiChatProfile[] = aiChatProfiles,
  project: ProjectOption = activeProject,
  pathStatusByPath: Record<string, DesktopPathStatusPayload> = {},
  aiChatSourceKinds: string[] = ["project", "selection", "diagnostics", "templates"],
  aiChatSourceKindRows?: ParaDevAiChatSourceKindRow[],
  aiChatProfileLoadError?: string | null,
  pathStatusErrorByPath: Record<string, string> = {},
  preferredLanguageBusy = false,
  preferredLanguageError = ""
) {
  const t = createTranslator(locale);
  return renderToStaticMarkup(
    <ConfigPage
      activeConfigId={activeConfigId}
      activeProject={project}
      aiChatDefaultRole="chat"
      aiChatProfileLoadError={aiChatProfileLoadError}
      aiChatProfiles={profiles}
      aiChatSourceKindRows={aiChatSourceKindRows}
      aiChatSourceKinds={aiChatSourceKinds}
      dependencyBusyId=""
      dependencyStatusById={{ imagemagick: dependencyStatus }}
      locale={locale}
      llmStatus={llmStatus}
      onCheckDependency={() => undefined}
      onInstallDependency={() => undefined}
      onLocaleChange={vi.fn<(locale: Locale) => void>()}
      onOpenPath={vi.fn<(path: string) => void>()}
      onResetAiChatProfile={() => undefined}
      onSaveAiChatProfile={() => undefined}
      onOpenTargetChange={vi.fn<(target: OpenPathTarget) => void>()}
      onPreferredLanguageChange={vi.fn<(preferredLanguage: string) => void>()}
      persistenceStatus={persistenceStatus}
      pathStatusByPath={pathStatusByPath}
      pathStatusErrorByPath={pathStatusErrorByPath}
      onTestLlm={() => undefined}
      onThemeChange={vi.fn<(theme: ThemeName) => void>()}
      openTarget="cursor"
      projectOptions={[project]}
      preferredLanguageBusy={preferredLanguageBusy}
      preferredLanguageError={preferredLanguageError}
      settings={settings}
      t={t}
      theme="dark"
    />
  );
}

function desktopPathStatus(path: string, overrides: Partial<DesktopPathStatusPayload> = {}): DesktopPathStatusPayload {
  return {
    schema: "paradev.desktop.path-status.v1",
    inputPath: path,
    path,
    exists: true,
    kind: "directory",
    readable: true,
    openable: true,
    ...overrides
  };
}

describe("ConfigPage", () => {
  it("keeps desktop config controls wired through shared key aliases", () => {
    const pageSource = readFileSync(new URL("./ConfigPage.tsx", import.meta.url), "utf-8");
    const modelSource = readFileSync(new URL("./model.ts", import.meta.url), "utf-8");

    expect(pageSource).not.toMatch(/configKey="paradev\./);
    expect(pageSource).not.toMatch(/data-paradev-config-key="paradev\./);
    expect(modelSource).not.toMatch(/configKey: "paradev\./);
  });

  it("renders HeavenBase LLM presets and DeepSeek key status", () => {
    const markup = renderConfigPage("config-models");

    expect(markup).toContain("HeavenBase LLM");
    expect(markup).toContain("deepseek-v4-flash");
    expect(markup).toContain("DeepSeek v4 Flash");
    expect(markup).toContain("DEEPSEEK_API_KEY");
    expect(markup).toContain("https://api.deepseek.com/v1");
    expect(markup).toContain("Route was reachable but returned an empty reply.");
    expect(markup).not.toContain("empty response");
  });

  it("renders preset target models with friendly route labels", () => {
    const markup = renderConfigPage("config-models");

    expect(markup).toContain("<code>DeepSeek Flash</code>");
    expect(markup).toContain("<code>DeepSeek Pro</code>");
    expect(markup).toContain("<code>Claude Sonnet</code>");
    expect(markup).not.toContain("<code>ds-flash</code>");
    expect(markup).not.toContain("<code>ds-pro</code>");
    expect(markup).not.toContain("<code>sonnet</code>");
  });

  it("renders the HeavenBase LLM route as real config-backed fields", () => {
    const markup = renderConfigPage("config-models");

    expect(markup).toContain("paradev.ai.preset");
    expect(markup).toContain("paradev.ai.provider");
    expect(markup).toContain("paradev.ai.gateway");
    expect(markup).toContain("paradev.ai.model");
    expect(markup).toContain("paradev.ai.key_env");
    expect(markup).toContain("paradev.ai.base_url");
    expect(markup).toContain('data-paradev-config-key="paradev.ai.model"');
    expect(markup).toContain('data-paradev-config-key="paradev.ai.base_url"');
    expect(markup).toContain('value="deepseek-v4-flash"');
  });

  it("renders the HeavenBase preset as the primary route control with advanced overrides grouped", () => {
    const markup = renderConfigPage("config-models");
    const zhMarkup = renderConfigPage("config-models", "zh");
    const reasonMarkup = renderConfigPage(
      "config-models",
      "en",
      undefined,
      undefined,
      normalizeConfigPageSettings({
        llm: {
          model: "deepseek-v4-flash",
          preset: "reason"
        }
      })
    );
    const presetIndex = markup.indexOf('data-paradev-config-key="paradev.ai.preset"');
    const advancedIndex = markup.indexOf('data-paradev-route-overrides="advanced"');
    const actionIndex = markup.indexOf('<div class="config-action-row">', advancedIndex);
    const advancedMarkup = markup.slice(advancedIndex, actionIndex);

    expect(markup).toContain("Active preset");
    expect(markup).toContain("<h3>Chat</h3>");
    expect(markup).toContain("Route: Preset: Chat · Gateway: OpenAI · Provider: DeepSeek · Model: DeepSeek v4 Flash");
    expect(markup).not.toContain("config.models.activeRouteValue");
    expect(reasonMarkup).toContain("<h3>Reason</h3>");
    expect(reasonMarkup).toContain("Route: Preset: Reason · Gateway: OpenAI · Provider: DeepSeek · Model: DeepSeek v4 Flash");
    expect(markup).toContain("Advanced route overrides");
    expect(markup).toContain("Manual model, provider, and gateway values for non-default HeavenBase routes.");
    expect(zhMarkup).toContain("当前预设");
    expect(zhMarkup).toContain("路由：预设：聊天 · 网关：OpenAI · 提供方：DeepSeek · 模型：DeepSeek v4 Flash");
    expect(zhMarkup).toContain("高级路由覆盖");
    expect(presetIndex).toBeGreaterThan(-1);
    expect(advancedIndex).toBeGreaterThan(-1);
    expect(presetIndex).toBeLessThan(advancedIndex);
    expect(advancedMarkup).toContain('data-paradev-config-key="paradev.ai.model"');
    expect(advancedMarkup).toContain('data-paradev-config-key="paradev.ai.provider"');
    expect(advancedMarkup).toContain('data-paradev-config-key="paradev.ai.gateway"');
    expect(markup.slice(0, advancedIndex)).not.toContain('data-paradev-config-key="paradev.ai.model"');
    expect(markup.slice(0, advancedIndex)).not.toContain('data-paradev-config-key="paradev.ai.provider"');
    expect(markup.slice(0, advancedIndex)).not.toContain('data-paradev-config-key="paradev.ai.gateway"');
  });

  it("keeps config keys machine-readable without exposing them as visible helper text", () => {
    const modelsMarkup = renderConfigPage("config-models", "zh");
    const generalMarkup = renderConfigPage("config-general", "zh");
    const projectsMarkup = renderConfigPage("config-projects", "zh");
    const moduleDefaultsMarkup = renderConfigPage("config-module-defaults", "zh");

    expect(modelsMarkup).toContain('data-paradev-config-key="paradev.ai.preset"');
    expect(modelsMarkup).toContain('data-paradev-config-key="paradev.ai.key_env"');
    expect(modelsMarkup).toContain('data-paradev-config-key="paradev.ai.base_url"');
    expect(generalMarkup).toContain('data-paradev-config-key="paradev.project.name"');
    expect(generalMarkup).toContain('data-paradev-config-key="paradev.cli.output"');
    expect(generalMarkup).toContain('<option value="yaml" selected="">YAML 输出</option>');
    expect(generalMarkup).toContain('<option value="json">JSON 输出</option>');
    expect(projectsMarkup).toContain('data-paradev-config-key="paradev.build.parallelism"');
    expect(projectsMarkup).toContain('data-paradev-config-key="paradev.build.strict_metadata"');
    expect(projectsMarkup).toContain('data-paradev-config-key="paradev.hoi4.game_root"');
    expect(moduleDefaultsMarkup).toContain('data-paradev-config-key="paradev.desktop.thumbnail_cache.max_kb"');
    expect(modelsMarkup).toContain("会影响 AI 聊天和 HeavenBase 路由。");
    expect(modelsMarkup).not.toContain("会影响构建和命令行 ParaDev。");
    expect(generalMarkup).toContain('title="CLI 输出"');
    expect(modelsMarkup).not.toContain("CM_PARADEV");
    expect(generalMarkup).not.toContain('title="paradev.cli.output"');
    expect(modelsMarkup).not.toContain("<small>paradev.ai.key_env</small>");
    expect(modelsMarkup).not.toContain("<small>paradev.ai.model</small>");
    expect(modelsMarkup).not.toContain("<small>paradev.ai.base_url</small>");
    expect(generalMarkup).not.toContain("<small>paradev.project.name</small>");
    expect(generalMarkup).not.toContain("<small>paradev.cli.output</small>");
    expect(projectsMarkup).not.toContain("<small>paradev.build.parallelism</small>");
    expect(projectsMarkup).not.toContain("<small>paradev.hoi4.game_root</small>");
    expect(moduleDefaultsMarkup).not.toContain("<small>paradev.desktop.thumbnail_cache.max_kb</small>");
  });

  it("renders every desktop config-value bridge key on its configured tab", () => {
    const configKeyTabs = [
      [DESKTOP_CONFIG_KEYS.projectName, "config-general"],
      [DESKTOP_CONFIG_KEYS.cliOutput, "config-general"],
      [DESKTOP_CONFIG_KEYS.aiPreset, "config-models"],
      [DESKTOP_CONFIG_KEYS.aiProvider, "config-models"],
      [DESKTOP_CONFIG_KEYS.aiGateway, "config-models"],
      [DESKTOP_CONFIG_KEYS.aiModel, "config-models"],
      [DESKTOP_CONFIG_KEYS.aiKeyEnv, "config-models"],
      [DESKTOP_CONFIG_KEYS.aiBaseUrl, "config-models"],
      [DESKTOP_CONFIG_KEYS.aiChatDefaultRole, "config-models"],
      [DESKTOP_CONFIG_KEYS.hoi4LaunchMode, "config-projects"],
      [DESKTOP_CONFIG_KEYS.hoi4GameRoot, "config-projects"],
      [DESKTOP_CONFIG_KEYS.buildParallelism, "config-projects"],
      [DESKTOP_CONFIG_KEYS.buildStrictMetadata, "config-projects"],
      [DESKTOP_CONFIG_KEYS.thumbnailCacheMaxKb, "config-module-defaults"]
    ] satisfies Array<[DesktopConfigKey, string]>;

    expect(configKeyTabs.map(([key]) => key).sort()).toEqual([...DESKTOP_CONFIG_KEY_VALUES].sort());

    for (const [configKey, tabId] of configKeyTabs) {
      expect(renderConfigPage(tabId)).toContain(`data-paradev-config-key="${configKey}"`);
    }
  });

  it("derives config-backed defaults from generated desktop metadata", () => {
    const settings = defaultConfigPageSettings();

    expect(settings.project.name).toBe(PARADEV_DESKTOP_CONFIG_DEFAULTS[DESKTOP_CONFIG_KEYS.projectName]);
    expect(settings.cli.output).toBe(PARADEV_DESKTOP_CONFIG_DEFAULTS[DESKTOP_CONFIG_KEYS.cliOutput]);
    expect(settings.build.parallelism).toBe(PARADEV_DESKTOP_CONFIG_DEFAULTS[DESKTOP_CONFIG_KEYS.buildParallelism]);
    expect(settings.build.strictMetadata).toBe(PARADEV_DESKTOP_CONFIG_DEFAULTS[DESKTOP_CONFIG_KEYS.buildStrictMetadata]);
    expect(settings.hoi4.launchMode).toBe(PARADEV_DESKTOP_CONFIG_DEFAULTS[DESKTOP_CONFIG_KEYS.hoi4LaunchMode]);
    expect(settings.hoi4.gameRoot).toBe(PARADEV_DESKTOP_CONFIG_DEFAULTS[DESKTOP_CONFIG_KEYS.hoi4GameRoot]);
    expect(settings.llm.preset).toBe(PARADEV_DESKTOP_CONFIG_DEFAULTS[DESKTOP_CONFIG_KEYS.aiPreset]);
    expect(settings.llm.provider).toBe(PARADEV_DESKTOP_CONFIG_DEFAULTS[DESKTOP_CONFIG_KEYS.aiProvider]);
    expect(settings.llm.gateway).toBe(PARADEV_DESKTOP_CONFIG_DEFAULTS[DESKTOP_CONFIG_KEYS.aiGateway]);
    expect(settings.llm.model).toBe(PARADEV_DESKTOP_CONFIG_DEFAULTS[DESKTOP_CONFIG_KEYS.aiModel]);
    expect(settings.llm.keyEnv).toBe(PARADEV_DESKTOP_CONFIG_DEFAULTS[DESKTOP_CONFIG_KEYS.aiKeyEnv]);
    expect(settings.llm.baseUrl).toBe(PARADEV_DESKTOP_CONFIG_DEFAULTS[DESKTOP_CONFIG_KEYS.aiBaseUrl]);
    expect(settings.chat.defaultRole).toBe(PARADEV_DESKTOP_CONFIG_DEFAULTS[DESKTOP_CONFIG_KEYS.aiChatDefaultRole]);
    expect(settings.moduleDefaults.find((row) => row.id === "thumbnail-cache")).toMatchObject({
      configKey: DESKTOP_CONFIG_KEYS.thumbnailCacheMaxKb,
      value: PARADEV_DESKTOP_CONFIG_DEFAULTS[DESKTOP_CONFIG_KEYS.thumbnailCacheMaxKb]
    });
    expect(settings.moduleDefaults.filter((row) => row.configKey).map((row) => row.configKey)).toEqual([DESKTOP_CONFIG_KEYS.thumbnailCacheMaxKb]);
  });

  it("renders generated desktop config choices with localized labels", () => {
    const choiceRows = PARADEV_DESKTOP_CONFIG_ROWS.filter((row) => "choices" in row);
    const byKey = Object.fromEntries(choiceRows.map((row) => [row.key, row.choices]));
    const generalMarkup = renderConfigPage("config-general", "zh");
    const modelsMarkup = renderConfigPage("config-models", "zh");
    const projectsMarkup = renderConfigPage("config-projects", "zh");

    expect(byKey[DESKTOP_CONFIG_KEYS.cliOutput]).toEqual(["yaml", "json"]);
    expect(byKey[DESKTOP_CONFIG_KEYS.aiPreset]).toEqual(["system", "chat", "reason", "coder"]);
    expect(byKey[DESKTOP_CONFIG_KEYS.hoi4LaunchMode]).toEqual(["steam", "local"]);
    for (const value of byKey[DESKTOP_CONFIG_KEYS.cliOutput] ?? []) {
      expect(generalMarkup).toContain(`value="${value}"`);
    }
    for (const value of byKey[DESKTOP_CONFIG_KEYS.aiPreset] ?? []) {
      expect(modelsMarkup).toContain(`value="${value}"`);
    }
    for (const value of byKey[DESKTOP_CONFIG_KEYS.hoi4LaunchMode] ?? []) {
      expect(projectsMarkup).toContain(`value="${value}"`);
    }
    expect(generalMarkup).toContain("YAML 输出");
    expect(generalMarkup).toContain("JSON 输出");
    expect(modelsMarkup).toContain("聊天");
    expect(projectsMarkup).toContain("Steam 启动器");
    expect(projectsMarkup).toContain("本地应用");
    expect(modelsMarkup).not.toContain("valueType");
    expect(projectsMarkup).not.toContain("choices");
  });

  it("renders SDK-owned AI chat profiles as editable prompts", () => {
    const markup = renderConfigPage("config-models");

    expect(markup).toContain("AI chat profiles");
    expect(markup).toContain("Explain HoI4 code");
    expect(markup).toContain("Custom PIHC3 source explanation.");
    expect(markup).toContain("Prefer PIHC3 source files and name the SDK operation");
    expect(markup).toContain('data-paradev-ai-profile-prompt="explain"');
    expect(markup).toContain('data-paradev-ai-profile-action="reset"');
    expect(markup).toContain('data-paradev-ai-profile-action="save"');
    expect(markup).toContain("Project / Selection / Diagnostics");
    expect(markup).toContain("Reset");
  });

  it("renders the generated create-module AI chat profile as an editable SDK role", () => {
    const settings = normalizeConfigPageSettings({
      chat: { defaultRole: "create-module" }
    });
    const markup = renderConfigPage("config-models", "en", undefined, undefined, settings, undefined, generatedAiChatProfiles);
    const defaultRoleSelect = configSelectMarkup(markup, "paradev.ai.chat.default_role");
    const createModuleRow = profileRowMarkup(markup, "create-module");

    expect(defaultRoleSelect).toContain('<option value="create-module" selected="">Create content plan</option>');
    expect(createModuleRow).toContain("Plan new modules or collections through ParaDev templates before writing source files.");
    expect(createModuleRow).toContain("Help create ParaDev modules and collections through the Python SDK.");
    expect(createModuleRow).toContain('data-paradev-ai-profile-source-kind="templates"');
    expect(profileSourceToggleMarkup(markup, "create-module", "templates")).toContain("checked");
    expect(createModuleRow).toContain('<small class="config-ai-profile-badge">Create content plan · default</small>');
  });

  it("localizes generated AI chat profile operation tooltips", () => {
    const markup = renderConfigPage("config-models", "zh", undefined, undefined, undefined, undefined, generatedAiChatProfiles);
    const operation = profileOperationMarkup(markup, "create-module", "module.draft");

    expect(operation).toContain('title="模块草稿 · 从前端浏览器的系列 ID 规划或写入源模块草稿。"');
    expect(operation).not.toContain("Module Draft");
    expect(operation).not.toContain("Plan or write a source-module draft from a frontend browser family id.");
  });

  it("surfaces AI chat profile load failures while preserving loaded profile editors", () => {
    const markup = renderConfigPage(
      "config-models",
      "en",
      undefined,
      undefined,
      undefined,
      undefined,
      aiChatProfiles,
      activeProject,
      {},
      ["project", "selection", "diagnostics", "templates"],
      undefined,
      "AI chat profiles could not be loaded: bridge denied"
    );

    expect(markup).toContain('role="alert"');
    expect(markup).toContain("AI chat profiles could not be loaded: bridge denied");
    expect(markup).toContain('data-paradev-ai-profile-prompt="explain"');
    expect(markup).toContain("Explain HoI4 code");
  });

  it("disables AI chat profile saves when the draft has no SDK changes", () => {
    const markup = renderConfigPage("config-models");
    const chatRow = profileRowMarkup(markup, "chat");
    const explainRow = profileRowMarkup(markup, "explain");

    expect(profileSaveButtonMarkup(chatRow)).toContain("disabled");
    expect(profileSaveButtonMarkup(explainRow)).toContain("disabled");
  });

  it("renders built-in AI chat profile prompts through the selected locale", () => {
    const markup = renderConfigPage("config-models", "zh");

    expect(markup).toContain("你是 ParaDev AI。帮助 Hearts of Iron IV 模组作者使用 ParaDev。需要行动时，回答应务实、简洁，并以 Python SDK 为依据。");
    expect(markup).not.toContain("Help a Hearts of Iron IV modder use ParaDev.");
  });

  it("renders the AI chat default role as a config-backed setting", () => {
    const settings = normalizeConfigPageSettings({
      chat: { defaultRole: "explain" }
    });
    const markup = renderConfigPage("config-models", "en", undefined, undefined, settings);

    expect(markup).toContain("Default chat role");
    expect(markup).toContain('data-paradev-config-key="paradev.ai.chat.default_role"');
    expect(markup).toContain('<option value="explain" selected="">Explain HoI4 code</option>');
  });

  it("keeps SDK-provided future AI chat roles selectable", () => {
    const futureProfiles = [
      ...aiChatProfiles,
      {
        id: "refactor-module",
        label: "Refactor module",
        detail: "Improve an existing module.",
        prompt: "Refactor the selected module through SDK-backed edits.",
        sourceKinds: ["project", "selection"]
      }
    ] as unknown as ParaDevAiChatProfile[];
    const settings = normalizeConfigPageSettings({
      chat: { defaultRole: "refactor-module" }
    });
    const markup = renderConfigPage("config-models", "en", undefined, undefined, settings, undefined, futureProfiles);
    const defaultRoleSelect = configSelectMarkup(markup, "paradev.ai.chat.default_role");

    expect(defaultRoleSelect).toContain('<option value="refactor-module" selected="">Refactor module</option>');
    expect(defaultRoleSelect).toContain('<option value="chat">Chat</option>');
    expect(defaultRoleSelect).not.toContain('<option value="chat" selected="">Chat</option>');
  });

  it("renders AI chat profile context sources as editable localized toggles", () => {
    const markup = renderConfigPage("config-models");
    const zhMarkup = renderConfigPage("config-models", "zh");

    expect(markup).toContain("Context sources");
    expect(markup).toContain('data-paradev-ai-profile-source-kind="project"');
    expect(markup).toContain('data-paradev-ai-profile-source-kind="selection"');
    expect(markup).toContain('data-paradev-ai-profile-source-kind="diagnostics"');
    expect(markup).toContain('data-paradev-ai-profile-source-kind="templates"');
    expect(markup).toContain('data-paradev-ai-profile-source-kinds="project,selection,diagnostics,templates"');
    expect(profileSourceToggleMarkup(markup, "explain", "project")).toContain("checked");
    expect(profileSourceToggleMarkup(markup, "explain", "project")).toContain('data-paradev-ai-profile-source-selected="true"');
    expect(profileSourceOptionMarkup(markup, "explain", "project")).toContain('class="config-ai-profile-source-option selected"');
    expect(profileSourceOptionMarkup(markup, "explain", "project")).toContain('data-paradev-ai-profile-source-selected="true"');
    expect(profileSourceToggleMarkup(markup, "explain", "selection")).toContain("checked");
    expect(profileSourceToggleMarkup(markup, "explain", "selection")).toContain('data-paradev-ai-profile-source-selected="true"');
    expect(profileSourceToggleMarkup(markup, "explain", "diagnostics")).toContain("checked");
    expect(profileSourceToggleMarkup(markup, "explain", "diagnostics")).toContain('data-paradev-ai-profile-source-selected="true"');
    expect(profileSourceToggleMarkup(markup, "explain", "templates")).not.toContain("checked");
    expect(profileSourceToggleMarkup(markup, "explain", "templates")).toContain('data-paradev-ai-profile-source-selected="false"');
    expect(profileSourceOptionMarkup(markup, "explain", "templates")).toContain('class="config-ai-profile-source-option"');
    expect(profileSourceOptionMarkup(markup, "explain", "templates")).toContain('data-paradev-ai-profile-source-selected="false"');
    expect(zhMarkup).toContain("上下文来源");
    expect(zhMarkup).toContain("项目");
    expect(zhMarkup).toContain("选区");
    expect(zhMarkup).toContain("诊断");
    expect(zhMarkup).toContain("模板");
  });

  it("renders managed SDK operation strips for generated AI chat profiles", () => {
    const markup = renderConfigPage("config-models", "en", undefined, undefined, undefined, undefined, generatedAiChatProfiles);
    const zhMarkup = renderConfigPage("config-models", "zh", undefined, undefined, undefined, undefined, generatedAiChatProfiles);

    expect(markup).toContain("Managed SDK actions");
    expect(profileOperationMarkup(markup, "create-module", "module.draft")).toContain('data-paradev-ai-profile-operation-passive="true"');
    expect(profileOperationMarkup(markup, "create-module", "module.draft")).toContain("<code");
    expect(profileOperationMarkup(markup, "create-module", "module.draft")).not.toContain("role=");
    expect(profileOperationMarkup(markup, "build", "build.plan")).toContain("build.plan");
    expect(profileOperationMarkup(markup, "build", "build.start")).toContain("build.start");
    expect(markup).not.toContain('data-paradev-operation-id="build.start"');
    expect(markup).not.toContain('data-paradev-operation-id="module.draft"');
    expect(markup).not.toContain("config-ai-profile-operation-strip\" role=\"button");
    expect(zhMarkup).toContain("托管 SDK 动作");
  });

  it("renders AI chat source toggles from SDK-owned source kind rows", () => {
    const sourceKindRows: ParaDevAiChatSourceKindRow[] = [
      { id: "project", label: "Project", labelKey: "config.models.sourceKind.project", frontendKinds: ["workspace"] },
      { id: "selection", label: "Selection", labelKey: "config.models.sourceKind.selection", frontendKinds: ["source"] },
      { id: "diagnostics", label: "Diagnostics", labelKey: "config.models.sourceKind.diagnostics", frontendKinds: ["diagnostics"] },
      { id: "templates", label: "Templates", labelKey: "config.models.sourceKind.templates", frontendKinds: ["templates"] },
      { id: "project-index", label: "Project index", frontendKinds: ["catalog"] },
      { id: "scripted-gui", label: "Scripted GUI", frontendKinds: ["scripted-gui"] }
    ];
    const markup = renderConfigPage("config-models", "en", undefined, undefined, undefined, undefined, aiChatProfiles, activeProject, {}, [
      "project",
      "selection",
      "diagnostics",
      "templates",
      "project-index",
      "scripted-gui"
    ], sourceKindRows);
    const zhMarkup = renderConfigPage("config-models", "zh", undefined, undefined, undefined, undefined, aiChatProfiles, activeProject, {}, [
      "project",
      "selection",
      "diagnostics",
      "templates",
      "project-index",
      "scripted-gui"
    ], sourceKindRows);

    expect(markup).toContain('data-paradev-ai-profile-source-kind="project-index"');
    expect(markup).toContain('data-paradev-ai-profile-source-kind="scripted-gui"');
    expect(markup).toContain('data-paradev-ai-profile-source-kinds="project,selection,diagnostics,templates,project-index,scripted-gui"');
    expect(markup).toContain(">Project index</span>");
    expect(markup).toContain(">Scripted GUI</span>");
    expect(markup).not.toContain(">Unknown source</span>");
    expect(markup).not.toContain(">project-index</span>");
    expect(markup).not.toContain(">scripted-gui</span>");
    expect(zhMarkup).toContain('data-paradev-ai-profile-source-kind="project-index"');
    expect(zhMarkup).toContain('data-paradev-ai-profile-source-kind="scripted-gui"');
    expect(zhMarkup).toContain(">项目索引</span>");
    expect(zhMarkup).toContain(">脚本 GUI</span>");
    expect(zhMarkup).not.toContain(">未知来源</span>");
    expect(zhMarkup).not.toContain(">Project index</span>");
    expect(zhMarkup).not.toContain(">Scripted GUI</span>");
    expect(zhMarkup).not.toContain(">project-index</span>");
    expect(zhMarkup).not.toContain(">scripted-gui</span>");
  });

  it("renders empty AI chat profile context sources as an explicit localized state", () => {
    const profiles = [
      {
        id: "empty",
        detail: "No automatic context.",
        label: "No context",
        prompt: "Answer without attached project context.",
        sourceKinds: []
      }
    ] as unknown as ParaDevAiChatProfile[];
    const markup = renderConfigPage("config-models", "en", undefined, undefined, undefined, undefined, profiles);
    const zhMarkup = renderConfigPage("config-models", "zh", undefined, undefined, undefined, undefined, profiles);

    expect(markup).toContain("No context sources");
    expect(markup).not.toContain("Selected by default: Pending");
    expect(zhMarkup).toContain("无上下文来源");
    expect(zhMarkup).not.toContain("默认附加：待检测");
  });

  it("renders module defaults in a project-scoped table", () => {
    const markup = renderConfigPage("config-module-defaults");

    expect(markup).toContain("Module default sizes");
    expect(markup).toContain("Focus trees");
    expect(markup).toContain("Technology folders");
    expect(markup).toContain("Minimal HOI4 Project");
  });

  it("separates local preview defaults from shared thumbnail cache settings", () => {
    const markup = renderConfigPage("config-module-defaults");
    const previewSection = panelMarkup(markup, "Module default sizes");
    const cacheSection = panelMarkup(markup, "Thumbnail cache");

    expect(previewSection).toContain("Focus trees");
    expect(previewSection).toContain("Technology folders");
    expect(previewSection).toContain("Country flags");
    expect(previewSection).toContain("Only changes this app&#x27;s previews.");
    expect(previewSection).not.toContain("Instance thumbnails");
    expect(previewSection).not.toContain('data-paradev-config-key="paradev.desktop.thumbnail_cache.max_kb"');

    expect(cacheSection).toContain("Instance thumbnails");
    expect(cacheSection).toContain('data-paradev-config-key="paradev.desktop.thumbnail_cache.max_kb"');
    expect(cacheSection).toContain("Shared with builds and command-line ParaDev.");
    expect(cacheSection).not.toContain("Only changes this app&#x27;s previews.");
  });

  it("marks only shared module defaults as SDK-backed config fields", () => {
    const markup = renderConfigPage("config-module-defaults");
    const focusRow = moduleDefaultRowMarkup(markup, "Focus trees");
    const flagRow = moduleDefaultRowMarkup(markup, "Country flags");
    const thumbnailRow = moduleDefaultRowMarkup(markup, "Instance thumbnails");
    const thumbnailRowMetadata = PARADEV_DESKTOP_CONFIG_ROWS.find((row) => row.key === DESKTOP_CONFIG_KEYS.thumbnailCacheMaxKb);

    expect(focusRow).not.toContain("data-paradev-config-key");
    expect(flagRow).not.toContain("data-paradev-config-key");
    expect(focusRow).not.toContain("Shared with builds and command-line ParaDev.");
    expect(flagRow).not.toContain("Shared with builds and command-line ParaDev.");
    expect(focusRow).toContain("Only changes this app&#x27;s previews.");
    expect(flagRow).toContain("Only changes this app&#x27;s previews.");
    expect(thumbnailRow).toContain('data-paradev-config-key="paradev.desktop.thumbnail_cache.max_kb"');
    expect(thumbnailRow).toContain(`min="${thumbnailRowMetadata && "minimum" in thumbnailRowMetadata ? thumbnailRowMetadata.minimum : 1}"`);
    expect(thumbnailRow).toContain("Shared with builds and command-line ParaDev.");
    expect(thumbnailRow).not.toContain("Only changes this app&#x27;s previews.");
  });

  it("renders config model and module default rows through the selected locale", () => {
    const modelsMarkup = renderConfigPage("config-models", "zh");
    const moduleDefaultsMarkup = renderConfigPage("config-module-defaults", "zh");

    expect(modelsMarkup).toContain("预设");
    expect(modelsMarkup).toContain("模型");
    expect(modelsMarkup).toContain("提供方");
    expect(modelsMarkup).toContain("密钥来源");
    expect(modelsMarkup).toContain("聊天配置");
    expect(modelsMarkup).toContain("提示词");
    expect(modelsMarkup).toContain("重置");
    expect(modelsMarkup).toContain("说明 HOI4 代码");
    expect(modelsMarkup).toContain('value="说明 HOI4 代码"');
    expect(modelsMarkup).toContain("项目 / 选区 / 诊断");
    expect(modelsMarkup).toContain("聊天");
    expect(modelsMarkup).toContain('<small class="config-ai-profile-badge">聊天 · 默认</small>');
    expect(modelsMarkup).toContain('<small class="config-ai-profile-badge">说明 HOI4 代码</small>');
    expect(modelsMarkup).toContain("快速非推理回答");
    expect(modelsMarkup).not.toContain("Provider");
    expect(modelsMarkup).not.toContain("Key source");
    expect(modelsMarkup).not.toContain('value="Explain HoI4 code"');
    expect(modelsMarkup).not.toContain("Fast non-thinking answers");
    expect(modelsMarkup).not.toContain("project / selection / diagnostics");
    expect(modelsMarkup).not.toContain("<code>chat · 默认</code>");
    expect(modelsMarkup).not.toContain("<code>explain</code>");
    expect(moduleDefaultsMarkup).toContain("国家旗帜");
    expect(moduleDefaultsMarkup).toContain("默认国家旗帜预览宽度。");
    expect(moduleDefaultsMarkup).toContain("缩略图缓存");
    expect(moduleDefaultsMarkup).toContain("ParaDev 浏览模块源图像时复用的预览缓存限制。");
    expect(moduleDefaultsMarkup).toContain("只影响此应用里的预览。");
    expect(moduleDefaultsMarkup).not.toContain("Country flags");
  });

  it("renders LLM route test results through locale-safe summaries", () => {
    const baseStatus = {
      baseUrl: "https://api.deepseek.com/v1",
      gateway: "openai",
      keySource: "DEEPSEEK_API_KEY",
      model: "deepseek-v4-flash",
      preset: "chat",
      provider: "deepseek",
      testedAt: "2026-06-28T00:00:00.000Z"
    } satisfies Omit<ConfigLlmStatus, "status" | "testDetail">;
    const readyMarkup = renderConfigPage("config-models", "zh", undefined, {
      ...baseStatus,
      resultCode: "ok",
      status: "ready",
      testDetail: "Received hb-ok."
    });
    const emptyMarkup = renderConfigPage("config-models", "zh", undefined, {
      ...baseStatus,
      resultCode: "empty_response",
      status: "warning",
      testDetail: "raw backend text without the old English marker"
    });
    const errorMarkup = renderConfigPage("config-models", "zh", undefined, {
      ...baseStatus,
      resultCode: "exception",
      status: "error",
      testDetail: "bridge denied"
    });

    expect(readyMarkup).toContain("路由测试成功。");
    expect(readyMarkup).not.toContain("Received hb-ok.");
    expect(emptyMarkup).toContain("路由可达，但返回了空回复。");
    expect(emptyMarkup).not.toContain("empty response");
    expect(errorMarkup).toContain("路由测试失败。请检查预设、提供方、模型、密钥和网络。");
    expect(errorMarkup).not.toContain("bridge denied");
  });

  it("renders the LLM route test running copy from the configured provider and model", () => {
    const settings = normalizeConfigPageSettings({
      llm: {
        provider: "openrouter",
        gateway: "openrouter",
        model: "deepseek-reasoner",
        preset: "reason",
        keyEnv: "OPENROUTER_API_KEY",
        baseUrl: "https://openrouter.ai/api/v1"
      }
    });
    const runningStatus: ConfigLlmStatus = {
      baseUrl: settings.llm.baseUrl,
      gateway: settings.llm.gateway,
      keySource: settings.llm.keyEnv,
      model: settings.llm.model,
      preset: settings.llm.preset,
      provider: settings.llm.provider,
      resultCode: "unknown",
      status: "unknown",
      testDetail: "Testing openrouter / deepseek-reasoner through HeavenBase.",
      testedAt: "2026-06-30T00:00:00.000Z"
    };
    const markup = renderConfigPage("config-models", "en", undefined, runningStatus, settings);
    const zhMarkup = renderConfigPage(
      "config-models",
      "zh",
      undefined,
      {
        ...runningStatus,
        testDetail: "正在通过 HeavenBase 测试 openrouter / deepseek-reasoner。"
      },
      settings
    );

    expect(markup).toContain("Testing Preset: Reason · Gateway: OpenRouter · Provider: OpenRouter · Model: DeepSeek Reasoner through HeavenBase.");
    expect(markup).not.toContain("Testing openrouter / deepseek-reasoner through HeavenBase.");
    expect(markup).not.toContain("Testing DeepSeek v4 Flash through HeavenBase.");
    expect(zhMarkup).toContain("正在通过 HeavenBase 测试 预设：推理 · 网关：OpenRouter · 提供方：OpenRouter · 模型：DeepSeek Reasoner。");
    expect(zhMarkup).not.toContain("正在通过 HeavenBase 测试 openrouter / deepseek-reasoner。");
    expect(zhMarkup).not.toContain("正在通过 HeavenBase 测试 DeepSeek v4 Flash。");
  });

  it("renders dependency detection and install actions", () => {
    const markup = renderConfigPage("config-dependencies");

    expect(markup).toContain("Dependencies");
    expect(markup).toContain("ImageMagick");
    expect(markup).toContain("Installed");
    expect(markup).toContain("/opt/homebrew/bin/magick");
    expect(markup).toContain("brew install imagemagick");
  });

  it("renders all three maintained themes as selectable appearance options", () => {
    const markup = renderConfigPage("config-appearance");

    expect(markup).toContain("Light Mode (Ollama Theme)");
    expect(markup).toContain("Dark Mode (GitHub Soft Dark Theme)");
    expect(markup).toContain("Anthropic Mode (Anthropic Theme)");
  });

  it("renders build parallelism as a real project config setting", () => {
    const markup = renderConfigPage("config-projects");
    const parallelismRow = PARADEV_DESKTOP_CONFIG_ROWS.find((row) => row.key === DESKTOP_CONFIG_KEYS.buildParallelism);

    expect(markup).toContain("Build defaults");
    expect(markup).toContain("Build parallelism");
    expect(markup).toContain("paradev.build.parallelism");
    expect(markup).toContain(`min="${parallelismRow && "minimum" in parallelismRow ? parallelismRow.minimum : 1}"`);
    expect(markup).toContain("Strict metadata");
    expect(markup).toContain('data-paradev-config-key="paradev.build.strict_metadata"');
    expect(markup).toContain('value="1"');
  });

  it("renders one inherited project-language control without module metadata", () => {
    const project = { ...activeProject, preferredLanguage: "zh" };
    const markup = renderConfigPage(
      "config-projects",
      "en",
      undefined,
      undefined,
      undefined,
      undefined,
      aiChatProfiles,
      project,
      undefined,
      undefined,
      undefined,
      undefined,
      undefined,
      true,
      "Manifest changed while saving."
    );

    expect(markup).toContain("Authoring defaults");
    expect(markup).toContain("Project language");
    expect(markup).toContain("Modules inherit it without per-module metadata.");
    expect(markup).toContain('aria-label="Preferred project language"');
    expect(markup).toContain('<option value="zh" selected="">Simplified Chinese</option>');
    expect(markup).toContain("Saving project language…");
    expect(markup).toContain("Manifest changed while saving.");
    expect(markup).toContain("disabled");
  });

  it("renders HOI4 game root as a real project config setting", () => {
    const markup = renderConfigPage(
      "config-projects",
      "en",
      undefined,
      undefined,
      normalizeConfigPageSettings({ hoi4: { gameRoot: "/Games/Hearts of Iron IV" } })
    );

    expect(markup).toContain("HOI4 game root");
    expect(markup).toContain("paradev.hoi4.game_root");
    expect(markup).toContain('data-paradev-config-key="paradev.hoi4.game_root"');
    expect(markup).toContain('value="/Games/Hearts of Iron IV"');
  });

  it("renders project path open actions through the configured opener target", () => {
    const markup = renderConfigPage("config-projects");

    expect(markup).toContain('data-config-open-path="/tmp/minimal"');
    expect(markup).toContain('data-config-open-path="/tmp/minimal/src"');
    expect(markup).toContain('data-config-open-path="/tmp/minimal/build/mod"');
    expect(markup).toContain('data-config-open-path="/tmp/minimal/.paradev/.cache/build"');
    expect(markup).toContain('title="Open project root (/tmp/minimal) with Cursor"');
    expect(markup).toContain('title="Open source root (/tmp/minimal/src) with Cursor"');
    expect(markup).toContain('title="Open output directory (/tmp/minimal/build/mod) with Cursor"');
    expect(markup).toContain('title="Open build cache (/tmp/minimal/.paradev/.cache/build) with Cursor"');
    expect(pathOpenButtonMarkup(markup, "/tmp/minimal")).not.toContain("disabled");
    expect(markup).not.toContain('data-config-open-path=""');
  });

  it("renders SDK-backed project path status without duplicating filesystem checks in React", () => {
    const markup = renderConfigPage("config-projects", "en", undefined, undefined, undefined, undefined, aiChatProfiles, activeProject, {
      "/tmp/minimal": desktopPathStatus("/tmp/minimal"),
      "/tmp/minimal/src": desktopPathStatus("/tmp/minimal/src"),
      "/tmp/minimal/build/mod": desktopPathStatus("/tmp/minimal/build/mod", {
        exists: false,
        kind: "missing",
        openable: false,
        readable: false
      }),
      "/tmp/minimal/.paradev/.cache/build": desktopPathStatus("/tmp/minimal/.paradev/.cache/build", {
        exists: false,
        kind: "missing",
        openable: false,
        readable: false
      })
    });

    expect(markup).toContain("Ready");
    expect(markup).toContain("Generated on build");
    expect(pathOpenButtonMarkup(markup, "/tmp/minimal")).not.toContain("disabled");
    expect(pathOpenButtonMarkup(markup, "/tmp/minimal/build/mod")).toContain("disabled");
    expect(pathOpenButtonMarkup(markup, "/tmp/minimal/.paradev/.cache/build")).toContain("disabled");
  });

  it("surfaces SDK path status load failures instead of leaving project paths checking", () => {
    const markup = renderConfigPage(
      "config-projects",
      "en",
      undefined,
      undefined,
      undefined,
      undefined,
      aiChatProfiles,
      activeProject,
      {},
      ["project", "selection", "diagnostics", "templates"],
      undefined,
      null,
      {
        "/tmp/minimal": "Path status could not be loaded: backend denied"
      }
    );

    const projectRootRow = settingRowMarkup(markup, "Project root");
    expect(projectRootRow).toContain("Failed");
    expect(projectRootRow).toContain('title="Path status could not be loaded: backend denied"');
    expect(projectRootRow).not.toContain('title="Waiting for SDK path status."');
    expect(pathOpenButtonMarkup(markup, "/tmp/minimal")).toContain("disabled");
  });

  it("summarizes multiple source-root statuses and keeps indexed open labels", () => {
    const project = {
      ...activeProject,
      sourceRoots: ["/tmp/minimal/src", "/tmp/minimal/extra-src"]
    };
    const markup = renderConfigPage("config-projects", "en", undefined, undefined, undefined, undefined, aiChatProfiles, project, {
      "/tmp/minimal/src": desktopPathStatus("/tmp/minimal/src"),
      "/tmp/minimal/extra-src": desktopPathStatus("/tmp/minimal/extra-src", {
        exists: false,
        kind: "missing",
        openable: false,
        readable: false
      })
    });

    expect(markup).toContain("1/2 ready");
    expect(markup).toContain('title="Open source root 1 (/tmp/minimal/src) with Cursor"');
    expect(markup).toContain('title="Open source root 2 (/tmp/minimal/extra-src) with Cursor"');
    expect(pathOpenButtonMarkup(markup, "/tmp/minimal/src")).not.toContain("disabled");
    expect(pathOpenButtonMarkup(markup, "/tmp/minimal/extra-src")).toContain("disabled");
  });

  it("uses the shared build output path fallback when the project output root is unset", () => {
    const project = {
      ...activeProject,
      outputRoot: undefined,
      path: "/Users/modder/Projects/PIHC3",
      id: "PIHC3",
      projectId: "PIHC3",
      sourceRoots: []
    };
    const markup = renderConfigPage("config-projects", "en", undefined, undefined, undefined, undefined, aiChatProfiles, project);

    expect(markup).toContain('data-config-open-path="/Users/modder/Documents/Paradox Interactive/Hearts of Iron IV/mod/PIHC3"');
    expect(markup).toContain("Open output directory (/Users/modder/Documents/Paradox Interactive/Hearts of Iron IV/mod/PIHC3) with Cursor");
  });

  it("renders a HOI4 game-root open action only after a path is configured", () => {
    const unsetMarkup = renderConfigPage("config-projects");
    const configuredMarkup = renderConfigPage(
      "config-projects",
      "en",
      undefined,
      undefined,
      normalizeConfigPageSettings({ hoi4: { gameRoot: "/Games/Hearts of Iron IV" } })
    );

    expect(unsetMarkup).not.toContain('title="Open HOI4 game root');
    expect(unsetMarkup).toContain("Steam/default");
    expect(configuredMarkup).toContain('data-config-open-path="/Games/Hearts of Iron IV"');
    expect(configuredMarkup).toContain('title="Open HOI4 game root (/Games/Hearts of Iron IV) with Cursor"');
  });

  it("renders path statuses through Chinese translations", () => {
    const markup = renderConfigPage("config-projects", "zh", undefined, undefined, undefined, undefined, aiChatProfiles, activeProject, {
      "/tmp/minimal": desktopPathStatus("/tmp/minimal"),
      "/tmp/minimal/src": desktopPathStatus("/tmp/minimal/src"),
      "/tmp/minimal/build/mod": desktopPathStatus("/tmp/minimal/build/mod", {
        exists: false,
        kind: "missing",
        openable: false,
        readable: false
      })
    });

    expect(markup).toContain("可用");
    expect(markup).toContain("构建时生成");
    expect(markup).toContain("Steam/默认");
    expect(markup).not.toContain("Generated on build");
    expect(markup).not.toContain("Steam/default");
  });

  it("renders HOI4 launch mode as a real project config setting", () => {
    const markup = renderConfigPage(
      "config-projects",
      "en",
      undefined,
      undefined,
      normalizeConfigPageSettings({ hoi4: { launchMode: "local" } })
    );

    expect(markup).toContain("HOI4 launch mode");
    expect(markup).toContain("paradev.hoi4.launch_mode");
    expect(markup).toContain('data-paradev-config-key="paradev.hoi4.launch_mode"');
    expect(markup).toContain('<option value="local" selected="">Local app</option>');
  });

  it("renders project status labels through Chinese translations", () => {
    const markup = renderConfigPage("config-projects", "zh");

    expect(markup).toContain("就绪");
    expect(markup).toContain("脚手架");
    expect(markup).not.toContain(">ready<");
    expect(markup).not.toContain(">scaffold<");
    expect(markup).toContain("HOI4 启动方式");
    expect(markup).toContain("HOI4 游戏目录");
  });

  it("renders CLI output as a real command config setting", () => {
    const markup = renderConfigPage("config-general");

    expect(markup).toContain("Command defaults");
    expect(markup).toContain("CLI output");
    expect(markup).toContain("paradev.cli.output");
    expect(markup).toContain('value="yaml"');
  });

  it("renders active project root instead of the raw project id", () => {
    const markup = renderConfigPage("config-general");
    const zhMarkup = renderConfigPage("config-general", "zh");

    expect(markup).toContain("Project root");
    expect(markup).toContain("/tmp/minimal");
    expect(markup).not.toContain("Project ID");
    expect(markup).not.toContain("<code>minimal_hoi4</code>");
    expect(zhMarkup).toContain("项目根目录");
    expect(zhMarkup).not.toContain("项目 ID");
  });

  it("renders the Projects tab root row value as the local project path", () => {
    const markup = renderConfigPage("config-projects");
    const rootRow = settingRowMarkup(markup, "Project root");

    expect(rootRow).toContain("<code>/tmp/minimal</code>");
    expect(rootRow).toContain('data-config-open-path="/tmp/minimal"');
    expect(rootRow).not.toContain("<code>minimal_hoi4</code>");
  });

  it("renders the ParaDev config profile name as a real command config setting", () => {
    const markup = renderConfigPage("config-general", "en", undefined, undefined, normalizeConfigPageSettings({ project: { name: "PIHC3 Workbench" } }));
    const zhMarkup = renderConfigPage("config-general", "zh", undefined, undefined, normalizeConfigPageSettings({ project: { name: "PIHC3 Workbench" } }));

    expect(markup).toContain("Config profile name");
    expect(markup).toContain("paradev.project.name");
    expect(markup).toContain('data-paradev-config-key="paradev.project.name"');
    expect(markup).toContain('value="PIHC3 Workbench"');
    expect(zhMarkup).toContain("配置档案名称");
    expect(zhMarkup).toContain('data-paradev-config-key="paradev.project.name"');
  });

  it("renders persistence failures as visible localized alerts", () => {
    const markup = renderConfigPage("config-models", "en", undefined, undefined, undefined, {
      detail: "paradev.ai.model: bridge denied",
      labelKey: "config.page.saveFailed",
      state: "error"
    });
    const zhMarkup = renderConfigPage("config-models", "zh", undefined, undefined, undefined, {
      detail: "paradev.ai.model: bridge denied",
      labelKey: "config.page.saveFailed",
      state: "error"
    });

    expect(markup).toContain('role="alert"');
    expect(markup).toContain("Save failed");
    expect(markup).toContain("paradev.ai.model: bridge denied");
    expect(zhMarkup).toContain("保存失败");
    expect(zhMarkup).toContain("paradev.ai.model: bridge denied");
    expect(markup).not.toContain("CM_PARADEV</span>");
  });

  it("renders default persistence status as localized user copy", () => {
    const enMarkup = renderConfigPage("config-general", "en");
    const zhMarkup = renderConfigPage("config-general", "zh");

    expect(enMarkup).toContain("Saved");
    expect(zhMarkup).toContain("已保存");
    expect(enMarkup).not.toContain("CM_PARADEV</span>");
    expect(zhMarkup).not.toContain("CM_PARADEV</span>");
  });

  it("renders pending persistence without alert semantics", () => {
    const markup = renderConfigPage("config-general", "zh", undefined, undefined, undefined, {
      labelKey: "config.page.saving",
      state: "saving"
    });

    expect(markup).toContain("保存中");
    expect(markup).not.toContain('role="alert"');
  });

  it("normalizes build parallelism to a positive integer", () => {
    expect(normalizeConfigPageSettings({ build: { parallelism: 6 } }).build.parallelism).toBe(6);
    expect(normalizeConfigPageSettings({ build: { parallelism: 0 } }).build.parallelism).toBe(1);
    expect(normalizeConfigPageSettings({ build: { parallelism: 2.6 } }).build.parallelism).toBe(3);
  });

  it("normalizes strict metadata to a boolean", () => {
    const fallback = normalizeConfigPageSettings({ build: { strictMetadata: true } });
    const looseFallback = normalizeConfigPageSettings({ build: { strictMetadata: false } });

    expect(normalizeConfigPageSettings({ build: { strictMetadata: true } }).build.strictMetadata).toBe(true);
    expect(normalizeConfigPageSettings({ build: { strictMetadata: false } }, fallback).build.strictMetadata).toBe(false);
    expect(normalizeConfigPageSettings({ build: { strictMetadata: "true" } }, looseFallback).build.strictMetadata).toBe(false);
  });

  it("normalizes HOI4 game root as an optional trimmed path", () => {
    const fallback = normalizeConfigPageSettings({ hoi4: { gameRoot: "/Fallback/HOI4" } });

    expect(normalizeConfigPageSettings({ hoi4: { gameRoot: "  /Games/Hearts of Iron IV  " } }).hoi4.gameRoot).toBe("/Games/Hearts of Iron IV");
    expect(normalizeConfigPageSettings({ hoi4: { gameRoot: "   " } }, fallback).hoi4.gameRoot).toBe("");
    expect(normalizeConfigPageSettings({ hoi4: { gameRoot: 394360 } }, fallback).hoi4.gameRoot).toBe("/Fallback/HOI4");
  });

  it("normalizes HOI4 launch mode to supported choices", () => {
    const fallback = normalizeConfigPageSettings({ hoi4: { launchMode: "local" } });

    expect(normalizeConfigPageSettings({ hoi4: { launchMode: "local" } }).hoi4.launchMode).toBe("local");
    expect(normalizeConfigPageSettings({ hoi4: { launchMode: "steam" } }).hoi4.launchMode).toBe("steam");
    expect(normalizeConfigPageSettings({ hoi4: { launchMode: "baseGame" } }, fallback).hoi4.launchMode).toBe("local");
  });

  it("normalizes CLI output to supported choices", () => {
    expect(normalizeConfigPageSettings({ cli: { output: "json" } }).cli.output).toBe("json");
    expect(normalizeConfigPageSettings({ cli: { output: "toml" } }).cli.output).toBe("yaml");
  });

  it("preserves fallback module default rows when persisted app settings include only desktop-owned rows", () => {
    const normalized = normalizeConfigPageSettings({
      moduleDefaults: [
        { id: "focus-node", value: 104 },
        { id: "technology-node", value: 56 },
        { id: "portrait", value: 164 },
        { id: "flag", value: 90 }
      ]
    });

    expect(normalized.moduleDefaults.map((row) => [row.id, row.value])).toEqual([
      ["focus-node", 104],
      ["technology-node", 56],
      ["portrait", 164],
      ["flag", 90],
      ["thumbnail-cache", 256]
    ]);
  });

  it("normalizes the config profile name as a required trimmed value", () => {
    const fallback = normalizeConfigPageSettings({ project: { name: "Fallback Workbench" } });

    expect(normalizeConfigPageSettings({ project: { name: "  PIHC3 Workbench  " } }).project.name).toBe("PIHC3 Workbench");
    expect(normalizeConfigPageSettings({ project: { name: "   " } }, fallback).project.name).toBe("Fallback Workbench");
    expect(normalizeConfigPageSettings({ project: { name: 394360 } }, fallback).project.name).toBe("Fallback Workbench");
  });
});

function profileSourceToggleMarkup(markup: string, profileId: string, kind: string): string {
  const match = new RegExp(`<input[^>]*data-paradev-ai-profile-id="${profileId}"[^>]*data-paradev-ai-profile-source-kind="${kind}"[^>]*>`).exec(markup);
  expect(match).not.toBeNull();
  return match?.[0] ?? "";
}

function profileSourceOptionMarkup(markup: string, profileId: string, kind: string): string {
  const match = new RegExp(
    `<label[^>]*data-paradev-ai-profile-source-selected="[^"]*"[^>]*>.*?<input[^>]*data-paradev-ai-profile-id="${profileId}"[^>]*data-paradev-ai-profile-source-kind="${kind}"[^>]*>.*?</label>`
  ).exec(markup);
  expect(match).not.toBeNull();
  return match?.[0] ?? "";
}

function profileOperationMarkup(markup: string, profileId: string, operationId: string): string {
  const match = new RegExp(
    `<code[^>]*data-paradev-ai-profile-id="${profileId}"[^>]*data-paradev-ai-profile-operation-id="${operationId}"[^>]*>.*?</code>`
  ).exec(markup);
  expect(match).not.toBeNull();
  return match?.[0] ?? "";
}

function profileRowMarkup(markup: string, profileId: string): string {
  const promptIndex = markup.indexOf(`data-paradev-ai-profile-prompt="${profileId}"`);
  expect(promptIndex).toBeGreaterThanOrEqual(0);
  const rowStart = markup.lastIndexOf('<div class="config-ai-profile-row">', promptIndex);
  const nextRowStart = markup.indexOf('<div class="config-ai-profile-row">', promptIndex);
  expect(rowStart).toBeGreaterThanOrEqual(0);
  return markup.slice(rowStart, nextRowStart === -1 ? markup.length : nextRowStart);
}

function profileSaveButtonMarkup(markup: string): string {
  const match = /<button class="toolbar-button primary"[^>]*>/.exec(markup);
  expect(match).not.toBeNull();
  return match?.[0] ?? "";
}

function configSelectMarkup(markup: string, configKey: string): string {
  const keyIndex = markup.indexOf(`data-paradev-config-key="${configKey}"`);
  expect(keyIndex).toBeGreaterThanOrEqual(0);
  const selectStart = markup.lastIndexOf("<select", keyIndex);
  const selectEnd = markup.indexOf("</select>", keyIndex);
  expect(selectStart).toBeGreaterThanOrEqual(0);
  expect(selectEnd).toBeGreaterThan(keyIndex);
  return markup.slice(selectStart, selectEnd + "</select>".length);
}

function moduleDefaultRowMarkup(markup: string, label: string): string {
  const labelIndex = markup.indexOf(`<strong>${label}</strong>`);
  expect(labelIndex).toBeGreaterThanOrEqual(0);
  const rowStart = markup.lastIndexOf('<div class="config-table-row module-default-row">', labelIndex);
  const rowEnd = markup.indexOf("</div>", labelIndex);
  expect(rowStart).toBeGreaterThanOrEqual(0);
  expect(rowEnd).toBeGreaterThan(labelIndex);
  return markup.slice(rowStart, rowEnd + "</div>".length);
}

function panelMarkup(markup: string, title: string): string {
  const titleIndex = markup.indexOf(`<h3>${title}</h3>`);
  expect(titleIndex).toBeGreaterThanOrEqual(0);
  const panelStart = markup.lastIndexOf('<section class="config-panel">', titleIndex);
  const nextPanelStart = markup.indexOf('<section class="config-panel">', titleIndex + title.length);
  expect(panelStart).toBeGreaterThanOrEqual(0);
  return markup.slice(panelStart, nextPanelStart === -1 ? markup.length : nextPanelStart);
}

function pathOpenButtonMarkup(markup: string, path: string): string {
  const match = new RegExp(`<button[^>]*data-config-open-path="${escapeRegExp(path)}"[^>]*>`).exec(markup);
  expect(match).not.toBeNull();
  return match?.[0] ?? "";
}

function settingRowMarkup(markup: string, label: string): string {
  const labelIndex = markup.indexOf(`<strong>${label}</strong>`);
  expect(labelIndex).toBeGreaterThanOrEqual(0);
  const rowStart = markup.lastIndexOf('<div class="config-setting-row"', labelIndex);
  const nextRow = markup.indexOf('<div class="config-setting-row"', labelIndex + label.length);
  expect(rowStart).toBeGreaterThanOrEqual(0);
  return markup.slice(rowStart, nextRow === -1 ? markup.length : nextRow);
}

function escapeRegExp(value: string): string {
  return value.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}
