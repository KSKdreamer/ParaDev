import { describe, expect, it, vi } from "vitest";
import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import * as appModule from "./App";
import { resolveBuildTargetForBrowser } from "./buildPage/buildPageModel";
import {
  appBootProgress,
  aiChatOperationNavigationTarget,
  assertAiChatCollectionReviewAvailable,
  assertAiChatModuleBatchReviewAvailable,
  assertAiChatSourceUpdateReviewAvailable,
  applyDesktopConfigValuesToConfigPageSettings,
  aiChatReplyText,
  aiChatSourcesForWorkspace,
  browserHasScopedPayload,
  browserScopeForWorkspaceTab,
  claimSourceBrowserFallbackCheck,
  configPageSettingsForProjectModuleDefaults,
  configPersistenceFailureStatus,
  configPersistenceSavingStatus,
  diagramTabIdForModule,
  applyDocumentLocale,
  desktopConfigWritesForSettingsChange,
  htmlLangForLocale,
  isWorkspaceProjectModelReady,
  isWorkspaceTabBrowserLoading,
  loadDesktopStateWithRememberedProjectRecovery,
  mergeProjectBrowserPayloads,
  mergeProjectBrowserPayloadsForProject,
  moduleEditorSessionKeyForWorkspaceTab,
  moduleEditorSessionKeyRequiringClosePrompt,
  nextOpenTabEntriesForOpen,
  normalizeChatSettings,
  persistableAppSettingsPayload,
  initialProjectBootOutcome,
  isProjectBootWorkspaceBlocked,
  projectBootOutcomeAfterFailure,
  projectBootOutcomeAfterLoad,
  projectBootRecoveryError,
  projectBrowserBaseForRefresh,
  projectRefreshFailureDisposition,
  projectRowsToOptions,
  reconcileOpenTabEntries,
  refreshCompletedBuildProject,
  refreshProjectForBuildPage,
  rememberedProjectRecoveryDetail,
  rememberedProjectRecoveryMessage,
  shouldCompleteAuthoringCloseIntent,
  shouldLoadWorkspaceBrowserScope,
  shouldShowProjectBootLoading,
  shouldShowProjectOnboarding,
  shouldRecoverRememberedProject,
  shouldUseBrowserProjectFallback,
  scopedBrowserErrorForWorkspaceTab,
  scopedBrowserKey,
  sourceBrowserScopeForUnavailableCatalog,
  shouldCommitScopedBrowserPayload,
  tabsForModules,
  shouldCommitProjectRefresh,
  shouldUseCachedProjectBrowserForRefresh,
  workspaceTabIdForModuleSelection
} from "./App";
import { defaultConfigPageSettings } from "./configPage/model";
import { DESKTOP_CONFIG_KEY_VALUES, PARADEV_DESKTOP_CONFIG_KEYS } from "./desktopConfig";
import { createTranslator } from "./i18n";
import { projectDiagramFamilyCapability } from "./projectModules";
import {
  ModuleEditorSessionStore,
  moduleEditorSessionKey,
  type ModuleEditorBatchCreateState,
  type ModuleEditorCollectionCreateState
} from "./moduleEditor/editorSessionStore";
import { buildModuleEntities } from "./moduleEditor/model";
import type { DesktopProjectRow, DesktopStatePayload, FeatureModule, ProjectBrowserPayload, ProjectDiagramCapability, ProjectTemplatesPayload, WorkspaceTab } from "./types";

function browserPayload(
  family: string,
  familyId: string,
  itemId: string,
  diagram?: ProjectDiagramCapability
): ProjectBrowserPayload {
  return {
    schema: "paradev.sdk.project-browser.v1",
    project_id: "PIHC3",
    title: "PIHC3",
    root: "/tmp/PIHC3",
    profile: "hoi4",
    filters: {},
    families: [{ id: familyId, family, title: family, visible: true, item_count: 1, source_count: 1, layouts: ["canonical"], ...(diagram ? { diagram } : {}) }],
    items: [
      {
        id: itemId,
        kind: "module",
        layout: "canonical",
        family_id: familyId,
        family,
        object_id: itemId.split("/").pop() ?? itemId,
        module_id: `${family}/${itemId.split("/").pop() ?? itemId}`,
        title: itemId,
        root: `/tmp/PIHC3/src/modules/${family}/${itemId}`,
        relative_root: `src/modules/${family}/${itemId}`,
        source_count: 1,
        sources: []
      }
    ],
    diagnostics: []
  };
}

function templatesPayload(templates: ProjectTemplatesPayload["templates"]): ProjectTemplatesPayload {
  return {
    schema: "paradev.sdk.templates.v1",
    project_id: "PIHC3",
    profile: "hoi4",
    templates
  };
}

function batchCreateState(
  objectId = ""
): ModuleEditorBatchCreateState {
  return {
    open: true,
    pristineSourceRoot: "/tmp/PIHC3/src",
    pristineTemplateId: "pihc3:idea/basic",
    rows: [
      {
        key: 1,
        objectId,
        templateId: "pihc3:idea/basic",
        values: { cic: "", title: "" }
      }
    ],
    showAdvanced: false,
    sourceRoot: "/tmp/PIHC3/src"
  };
}

function collectionCreateState(
  collectionId = ""
): ModuleEditorCollectionCreateState {
  return {
    open: true,
    pristineSourceRoot: "/tmp/PIHC3/src",
    pristineTemplateId: "pihc3:focus-tree/basic",
    templateId: "pihc3:focus-tree/basic",
    collectionId,
    values: collectionId
      ? { country_tag: "C99", title: "AI Review Tree" }
      : {},
    showAdvanced: false,
    sourceRoot: "/tmp/PIHC3/src"
  };
}

describe("app boot progress", () => {
  it("validates restored modules only against the matching project model", () => {
    const project = {
      path: "/tmp/PIHC3",
      projectId: "PIHC3"
    };
    const matchingBrowser = browserPayload(
      "technology",
      "technologies",
      "module:technology/TECH_ALPHA"
    );
    const matchingTemplates = templatesPayload([]);

    expect(
      isWorkspaceProjectModelReady(
        project,
        matchingBrowser,
        matchingTemplates
      )
    ).toBe(true);
    expect(
      isWorkspaceProjectModelReady(project, null, matchingTemplates)
    ).toBe(false);
    expect(
      isWorkspaceProjectModelReady(project, matchingBrowser, null)
    ).toBe(false);
    expect(
      isWorkspaceProjectModelReady(
        project,
        { ...matchingBrowser, root: "/tmp/OTHER" },
        matchingTemplates
      )
    ).toBe(false);
    expect(
      isWorkspaceProjectModelReady(project, matchingBrowser, {
        ...matchingTemplates,
        project_id: "OTHER"
      })
    ).toBe(false);
  });

  it("switches project workspace ownership before the project panel can accept input", () => {
    const source = readFileSync(resolve(__dirname, "App.tsx"), "utf8");

    expect(source).toMatch(
      /useLayoutEffect\(\(\) => \{\s*const nextRoot = activeProjectOption\.path;\s*const previousRoot = workspaceViewProjectRootRef\.current;/
    );
  });

  it("loads workspace browser scopes only while the workspace rail is visible", () => {
    expect(shouldLoadWorkspaceBrowserScope("projects")).toBe(true);
    expect(shouldLoadWorkspaceBrowserScope("build")).toBe(false);
    expect(shouldLoadWorkspaceBrowserScope("settings")).toBe(false);
  });

  it("refreshes only build diagnostics after an active-project build completes", async () => {
    const calls: unknown[][] = [];
    const refresh = async (..._args: unknown[]) => {
      calls.push(_args);
      throw new Error("diagnostics refresh failed");
    };

    await expect(
      refreshCompletedBuildProject("/tmp/PIHC3", refresh, "/tmp/PIHC3")
    ).rejects.toThrow("diagnostics refresh failed");
    expect(calls).toEqual([["/tmp/PIHC3", "published"]]);
    await expect(
      refreshCompletedBuildProject("/tmp/PIHC3", refresh, "/tmp/OTHER")
    ).resolves.toBeUndefined();
  });

  it("propagates manual Build-page refresh failures through the production wrapper", async () => {
    const calls: unknown[][] = [];
    const refresh = async (...args: unknown[]) => {
      calls.push(args);
      throw new Error("manual browser refresh failed");
    };

    await expect(refreshProjectForBuildPage(refresh, "/tmp/PIHC3", "PIHC3")).rejects.toThrow(
      "manual browser refresh failed"
    );
    expect(calls).toEqual([["/tmp/PIHC3", "PIHC3", { throwOnError: true }]]);
  });

  it("maps GUI locales to document language tags", () => {
    expect(htmlLangForLocale("zh")).toBe("zh-CN");
    expect(htmlLangForLocale("en")).toBe("en");
  });

  it("shows first-run project selection only after an honest empty native registry is ready", () => {
    const checking = initialProjectBootOutcome(true);
    const empty = projectBootOutcomeAfterLoad(
      true,
      { active_project: null }
    );

    expect(checking).toEqual({ kind: "checking" });
    expect(isProjectBootWorkspaceBlocked(checking)).toBe(true);
    expect(
      shouldShowProjectBootLoading(checking, {
        projectLoading: true,
        settingsReady: false
      })
    ).toBe(true);
    expect(empty).toEqual({
      kind: "project-required",
      error: "",
      requestedPath: ""
    });
    expect(
      shouldShowProjectOnboarding(empty, {
        projectLoading: false,
        settingsReady: true
      })
    ).toBe(true);
    expect(
      shouldShowProjectOnboarding(empty, {
        projectLoading: true,
        settingsReady: true
      })
    ).toBe(false);
    expect(
      shouldShowProjectOnboarding(empty, {
        projectLoading: false,
        settingsReady: false
      })
    ).toBe(false);
  });

  it("keeps checkout-relative demo fallback exclusive to plain browser development", () => {
    const browserFallback = initialProjectBootOutcome(false);
    const nativeChecking = initialProjectBootOutcome(true);

    expect(browserFallback).toEqual({ kind: "browser-fallback" });
    expect(shouldUseBrowserProjectFallback(browserFallback)).toBe(true);
    expect(isProjectBootWorkspaceBlocked(browserFallback)).toBe(false);
    expect(shouldUseBrowserProjectFallback(nativeChecking)).toBe(false);
    expect(isProjectBootWorkspaceBlocked(nativeChecking)).toBe(true);
  });

  it("turns a failed remembered path into actionable recovery and clears it after a valid selection", () => {
    const failed = projectBootOutcomeAfterFailure(
      true,
      "/missing/PIHC3",
      new Error("paradev.yaml was not found")
    );

    expect(failed).toEqual({
      kind: "project-required",
      error: "paradev.yaml was not found",
      requestedPath: "/missing/PIHC3"
    });
    expect(
      shouldShowProjectOnboarding(failed, {
        projectLoading: false,
        settingsReady: true
      })
    ).toBe(true);
    expect(projectBootRecoveryError(failed, createTranslator("en"))).toContain(
      "could not reopen /missing/PIHC3"
    );
    expect(projectBootRecoveryError(failed, createTranslator("en"))).toContain(
      "Choose the project folder again"
    );

    const recovered = projectBootOutcomeAfterLoad(
      true,
      {
        active_project: {
          project_id: "PIHC3",
          title: "PIHC3",
          game: "hoi4",
          root: "/workspace/PIHC3",
          manifest: "/workspace/PIHC3/paradev.yaml",
          source_roots: ["/workspace/PIHC3/src"]
        }
      },
      "/workspace/PIHC3"
    );
    expect(recovered).toEqual({ kind: "ready" });
    expect(
      shouldShowProjectOnboarding(recovered, {
        projectLoading: false,
        settingsReady: true
      })
    ).toBe(false);
    expect(projectBootRecoveryError(recovered, createTranslator("en"))).toBe(
      ""
    );
  });

  it("recovers a failed saved startup path from the compatible project registry", async () => {
    const calls: Array<string | undefined> = [];
    const recoveredState = {
      schema: "paradev.desktop.state.v1",
      projects: [],
      active_project: {
        project_id: "PIHC3",
        title: "The Pony In The High Castle",
        game: "hoi4",
        root: "/workspace/current/PIHC3",
        manifest: "/workspace/current/PIHC3/paradev.yaml",
        source_roots: ["/workspace/current/PIHC3/src"]
      },
      browser: null,
      templates: null,
      diagnostics: []
    } satisfies DesktopStatePayload;
    const load = vi.fn(async (projectRoot?: string) => {
      calls.push(projectRoot);
      if (projectRoot) {
        throw new Error("retired_families is not supported");
      }
      return recoveredState;
    });

    const outcome = await loadDesktopStateWithRememberedProjectRecovery(load, {
      currentState: null,
      desktopBackend: true,
      options: { recoverRememberedProject: true },
      projectRoot: "/workspace/obsolete/PIHC3"
    });

    expect(calls).toEqual(["/workspace/obsolete/PIHC3", undefined]);
    expect(outcome.state).toBe(recoveredState);
    expect(outcome.recovery).toEqual({
      error: "retired_families is not supported",
      recoveredPath: "/workspace/current/PIHC3",
      recoveredTitle: "The Pony In The High Castle",
      requestedPath: "/workspace/obsolete/PIHC3"
    });
    const notice = rememberedProjectRecoveryMessage(
      outcome.recovery,
      createTranslator("en")
    );
    expect(notice).toContain("updated the saved location");
    expect(notice).not.toContain("retired_families");
    const detail = rememberedProjectRecoveryDetail(
      outcome.recovery,
      createTranslator("en")
    );
    expect(detail).toContain("/workspace/obsolete/PIHC3");
    expect(detail).toContain("/workspace/current/PIHC3");
    expect(detail).toContain("retired_families");
  });

  it("does not use startup recovery for manual selection or over an open workspace", async () => {
    const load = vi.fn(async () => {
      throw new Error("candidate is incompatible");
    });
    const currentState = {
      active_project: {
        project_id: "PIHC3",
        title: "PIHC3",
        game: "hoi4",
        root: "/workspace/current/PIHC3",
        manifest: "/workspace/current/PIHC3/paradev.yaml",
        source_roots: ["/workspace/current/PIHC3/src"]
      }
    };

    expect(
      shouldRecoverRememberedProject(
        true,
        null,
        "/workspace/candidate",
        { throwOnError: true, recoverRememberedProject: true }
      )
    ).toBe(false);
    expect(
      shouldRecoverRememberedProject(
        true,
        currentState,
        "/workspace/candidate",
        { recoverRememberedProject: true }
      )
    ).toBe(false);
    await expect(
      loadDesktopStateWithRememberedProjectRecovery(load, {
        currentState,
        desktopBackend: true,
        options: { recoverRememberedProject: true },
        projectRoot: "/workspace/candidate"
      })
    ).rejects.toThrow("candidate is incompatible");
    expect(load).toHaveBeenCalledTimes(1);
  });

  it("keeps the original saved-path failure when registry recovery finds no project", async () => {
    const emptyState = {
      schema: "paradev.desktop.state.v1",
      projects: [],
      active_project: null,
      browser: null,
      templates: null,
      diagnostics: []
    } satisfies DesktopStatePayload;
    const load = vi.fn(async (projectRoot?: string) => {
      if (projectRoot) {
        throw new Error("saved project is incompatible");
      }
      return emptyState;
    });

    await expect(
      loadDesktopStateWithRememberedProjectRecovery(load, {
        currentState: null,
        desktopBackend: true,
        options: { recoverRememberedProject: true },
        projectRoot: "/workspace/obsolete/PIHC3"
      })
    ).rejects.toThrow("saved project is incompatible");
    expect(load).toHaveBeenCalledTimes(2);
  });

  it("preserves a ready workspace when a different project candidate is invalid", () => {
    const currentState = {
      active_project: {
        project_id: "PIHC3",
        title: "PIHC3",
        game: "hoi4",
        root: "/workspace/PIHC3",
        manifest: "/workspace/PIHC3/paradev.yaml",
        source_roots: ["/workspace/PIHC3/src"]
      }
    };
    const failure = projectRefreshFailureDisposition(
      true,
      currentState,
      "/workspace/invalid",
      new Error("paradev.yaml was not found")
    );

    expect(failure).toEqual({
      bootOutcome: { kind: "ready" },
      candidateProject: true,
      preserveWorkspace: true
    });
    expect(isProjectBootWorkspaceBlocked(failure.bootOutcome)).toBe(false);

    const firstRunFailure = projectRefreshFailureDisposition(
      true,
      null,
      "/workspace/invalid",
      new Error("paradev.yaml was not found")
    );
    expect(firstRunFailure).toEqual({
      bootOutcome: {
        kind: "project-required",
        error: "paradev.yaml was not found",
        requestedPath: "/workspace/invalid"
      },
      candidateProject: false,
      preserveWorkspace: false
    });
    expect(isProjectBootWorkspaceBlocked(firstRunFailure.bootOutcome)).toBe(
      true
    );
  });

  it("does not pre-commit project identity before candidate validation succeeds", () => {
    const source = readFileSync(resolve(__dirname, "App.tsx"), "utf8");
    const handler = source.match(
      /const handleSelectProject = \(id: string\) => \{[\s\S]*?\n  \};\n\n  const handleModuleReorder/
    )?.[0];

    expect(handler).toBeTruthy();
    expect(handler).not.toContain("setActiveProjectIdentity");
    expect(handler).toContain(
      "refreshDesktopState(project.path, id, { throwOnError: true })"
    );
  });

  it("applies the selected GUI locale to the document element", () => {
    const documentLike = { documentElement: { lang: "en" } };

    applyDocumentLocale(documentLike, "zh");

    expect(documentLike.documentElement.lang).toBe("zh-CN");
  });

  it("starts the desktop shell with the default GUI document language", () => {
    const html = readFileSync(resolve(__dirname, "../index.html"), "utf8");

    expect(html).toContain(`<html lang="${htmlLangForLocale("zh")}">`);
  });

  it("maps SDK project descriptor metadata into GUI project options", () => {
    const rows: DesktopProjectRow[] = [
      {
        project_id: "PIHC3",
        title: "The Pony In The High Castle",
        game: "hoi4",
        root: "/tmp/PIHC3",
        manifest: "/tmp/PIHC3/paradev.yaml",
        preferred_language: "zh",
        source_roots: ["/tmp/PIHC3/src"],
        descriptor: {
          mod_version: "v0.2.3",
          supported_version: "1.19.*"
        },
        version: "0.2.3"
      }
    ];

    expect(projectRowsToOptions(rows)[0]).toMatchObject({
      id: "/tmp/PIHC3",
      projectId: "PIHC3",
      preferredLanguage: "zh",
      descriptor: {
        mod_version: "v0.2.3",
        supported_version: "1.19.*"
      },
      version: "0.2.3"
    });
  });

  it("keeps same-ID project checkouts independently selectable by canonical root", () => {
    const rows: DesktopProjectRow[] = [
      {
        project_id: "PIHC3",
        title: "PIHC3 original",
        game: "hoi4",
        root: "/workspace/original/PIHC3",
        manifest: "/workspace/original/PIHC3/paradev.yaml",
        source_roots: ["/workspace/original/PIHC3/src"]
      },
      {
        project_id: "PIHC3",
        title: "PIHC3 isolated checkout",
        game: "hoi4",
        root: "/workspace/isolated/PIHC3",
        manifest: "/workspace/isolated/PIHC3/paradev.yaml",
        source_roots: ["/workspace/isolated/PIHC3/src"]
      }
    ];

    const options = projectRowsToOptions(rows);

    expect(options.map((option) => option.id)).toEqual(["/workspace/original/PIHC3", "/workspace/isolated/PIHC3"]);
    expect(options.map((option) => option.projectId)).toEqual(["PIHC3", "PIHC3"]);
  });

  it("reports an open-project handoff while the desktop shell is launching a target", () => {
    const progress = appBootProgress({
      activeProjectName: "PIHC3",
      desktopStateLoaded: true,
      openTarget: "cursor",
      projectError: "",
      projectLoading: false,
      projectOpening: true,
      settingsReady: true,
      t: createTranslator("en")
    });

    expect(progress).toEqual({
      label: "Opening project",
      detail: "Opening PIHC3 in Cursor",
      value: 92
    });
  });

  it("keeps the open-project handoff visible during a background SDK refresh", () => {
    const progress = appBootProgress({
      activeProjectName: "PIHC3",
      desktopStateLoaded: true,
      openTarget: "cursor",
      projectError: "",
      projectLoading: true,
      projectOpening: true,
      settingsReady: true,
      t: createTranslator("en")
    });

    expect(progress).toEqual({
      label: "Opening project",
      detail: "Opening PIHC3 in Cursor",
      value: 92
    });
  });

  it("reports a failed initial project load instead of hiding startup progress", () => {
    const progress = appBootProgress({
      activeProjectName: "PIHC3",
      desktopStateLoaded: false,
      openTarget: "cursor",
      projectError: "desktop-state failed",
      projectLoading: false,
      projectOpening: false,
      settingsReady: true,
      t: createTranslator("en")
    });

    expect(progress).toEqual({
      detail: "desktop-state failed",
      label: "Project load failed",
      status: "error",
      value: 100
    });
  });

  it("summarizes already loaded SDK payload during a background project refresh", () => {
    const progress = appBootProgress({
      activeProjectName: "PIHC3",
      browserItemCount: 1148,
      desktopStateLoaded: true,
      diagnosticCount: 2,
      openTarget: "cursor",
      projectError: "",
      projectLoading: true,
      projectOpening: false,
      settingsReady: true,
      templateCount: 16,
      t: createTranslator("en")
    });

    expect(progress).toEqual({
      label: "Refreshing project",
      detail: "Refreshing PIHC3: 1,148 project rows, 16 templates, 2 diagnostics",
      value: 86
    });
  });

  it("allows only the latest project refresh request to commit async state", () => {
    expect(shouldCommitProjectRefresh(1, 2)).toBe(false);
    expect(shouldCommitProjectRefresh(2, 2)).toBe(true);
  });

  it("uses project browser cache only for automatic startup refreshes", () => {
    expect(shouldUseCachedProjectBrowserForRefresh()).toBe(true);
    expect(shouldUseCachedProjectBrowserForRefresh("")).toBe(true);
    expect(shouldUseCachedProjectBrowserForRefresh("   ")).toBe(true);
    expect(shouldUseCachedProjectBrowserForRefresh("/tmp/PIHC3")).toBe(false);
  });

  it("localizes known bridge details in config persistence failures", () => {
    expect(configPersistenceFailureStatus("AI profile chat", new Error("Writing AI chat profiles requires the ParaDev desktop application."), createTranslator("zh")).detail).toBe(
      "AI profile chat: 此操作需要使用 ParaDev 桌面应用。"
    );
  });

  it("merges SDK-backed desktop config values into the config page settings", () => {
    const base = defaultConfigPageSettings();

    const merged = applyDesktopConfigValuesToConfigPageSettings(base, {
      "paradev.ai.gateway": "openrouter",
      "paradev.ai.key_env": "OPENROUTER_API_KEY",
      "paradev.ai.model": "deepseek-reasoner",
      "paradev.ai.preset": "reason",
      "paradev.ai.provider": "deepseek",
      "paradev.ai.chat.default_role": "build",
      "paradev.ai.base_url": "https://openrouter.ai/api/v1",
      "paradev.build.parallelism": 4,
      "paradev.build.strict_metadata": true,
      "paradev.cli.output": "json",
      "paradev.desktop.thumbnail_cache.max_kb": 384,
      "paradev.hoi4.game_root": "  /Games/Hearts of Iron IV  ",
      "paradev.hoi4.launch_mode": "local",
      "paradev.project.name": "PIHC3 Workbench"
    });

    expect(merged).toMatchObject({
      build: { parallelism: 4, strictMetadata: true },
      cli: { output: "json" },
      project: { name: "PIHC3 Workbench" },
      hoi4: {
        gameRoot: "/Games/Hearts of Iron IV",
        launchMode: "local"
      },
      llm: {
        gateway: "openrouter",
        keyEnv: "OPENROUTER_API_KEY",
        model: "deepseek-reasoner",
        preset: "reason",
        provider: "deepseek",
        baseUrl: "https://openrouter.ai/api/v1"
      },
      chat: {
        defaultRole: "build"
      }
    });
    expect(merged.moduleDefaults.find((row) => row.id === "thumbnail-cache")).toMatchObject({ value: 384 });

    expect(
      applyDesktopConfigValuesToConfigPageSettings(base, {
        "paradev.ai.chat.default_role": "refactor-module"
      }).chat.defaultRole
    ).toBe("refactor-module");

    expect(
      applyDesktopConfigValuesToConfigPageSettings(base, {
        "paradev.ai.base_url": 394360,
        "paradev.ai.chat.default_role": "",
        "paradev.ai.model": "",
        "paradev.ai.preset": "creative",
        "paradev.build.parallelism": 0,
        "paradev.build.strict_metadata": "true",
        "paradev.cli.output": "toml",
        "paradev.desktop.thumbnail_cache.max_kb": 0,
        "paradev.hoi4.game_root": 394360,
        "paradev.hoi4.launch_mode": "baseGame",
        "paradev.project.name": ""
      })
    ).toEqual(base);
  });

  it("plans desktop config writes for every changed config-backed setting", () => {
    const previous = defaultConfigPageSettings();
    const next = {
      ...previous,
      build: { parallelism: 6, strictMetadata: true },
      cli: { output: "json" as const },
      hoi4: { gameRoot: "/Games/Hearts of Iron IV", launchMode: "local" as const },
      project: { name: "PIHC3 Workbench" },
      moduleDefaults: previous.moduleDefaults.map((row) => (row.id === "thumbnail-cache" ? { ...row, value: 512 } : row)),
      chat: { defaultRole: "build" },
      llm: {
        gateway: "openrouter",
        keyEnv: "OPENROUTER_API_KEY",
        model: "deepseek-reasoner",
        preset: "reason",
        provider: "openrouter",
        baseUrl: "https://openrouter.ai/api/v1"
      }
    };

    expect(desktopConfigWritesForSettingsChange(previous, next)).toEqual([
      ["paradev.project.name", "PIHC3 Workbench"],
      ["paradev.build.parallelism", 6],
      ["paradev.build.strict_metadata", true],
      ["paradev.desktop.thumbnail_cache.max_kb", 512],
      ["paradev.cli.output", "json"],
      ["paradev.hoi4.game_root", "/Games/Hearts of Iron IV"],
      ["paradev.hoi4.launch_mode", "local"],
      ["paradev.ai.preset", "reason"],
      ["paradev.ai.provider", "openrouter"],
      ["paradev.ai.gateway", "openrouter"],
      ["paradev.ai.model", "deepseek-reasoner"],
      ["paradev.ai.key_env", "OPENROUTER_API_KEY"],
      ["paradev.ai.base_url", "https://openrouter.ai/api/v1"],
      ["paradev.ai.chat.default_role", "build"]
    ]);
  });

  it("keeps the named desktop config map aligned with the SDK key tuple", () => {
    expect([...DESKTOP_CONFIG_KEY_VALUES].sort()).toEqual([...PARADEV_DESKTOP_CONFIG_KEYS].sort());
    expect(DESKTOP_CONFIG_KEY_VALUES).toHaveLength(PARADEV_DESKTOP_CONFIG_KEYS.length);
  });

  it("keeps desktop-only module defaults out of desktop config writes", () => {
    const previous = defaultConfigPageSettings();
    const next = {
      ...previous,
      moduleDefaults: previous.moduleDefaults.map((row) => (row.id === "thumbnail-cache" ? row : { ...row, value: row.value + 8 }))
    };

    expect(desktopConfigWritesForSettingsChange(previous, next)).toEqual([]);
  });

  it("serializes only desktop-owned config page settings into app settings", () => {
    const settings = defaultConfigPageSettings();
    const changed = {
      ...settings,
      build: { parallelism: 6, strictMetadata: false },
      cli: { output: "json" as const },
      hoi4: { gameRoot: "/Games/Hearts of Iron IV", launchMode: "local" as const },
      project: { name: "PIHC3 Workbench" },
      moduleDefaults: settings.moduleDefaults.map((row) => ({ ...row, value: row.value + 8 })),
      chat: { defaultRole: "build" },
      llm: {
        gateway: "openrouter",
        keyEnv: "OPENROUTER_API_KEY",
        model: "deepseek-reasoner",
        preset: "reason",
        provider: "openrouter",
        baseUrl: "https://openrouter.ai/api/v1"
      }
    };

    const payload = persistableAppSettingsPayload({
      schema: "paradev.desktop.app-settings.v1",
      activeProjectId: "PIHC3",
      activeProjectPath: "/tmp/PIHC3",
      chat: { dock: "side", open: true },
      configPage: changed,
      theme: "dark",
      locale: "en",
      openTarget: "cursor",
      sidebars: { projectPanelOpen: false, inspectorOpen: true },
      moduleDefaultsByProject: {
        EOH: [{ id: "focus-node", value: 72 }]
      },
      moduleOrderByProject: { PIHC3: ["ideas"] }
    });

    expect(payload).toEqual({
      schema: "paradev.desktop.app-settings.v1",
      activeProjectPath: "/tmp/PIHC3",
      chat: { dock: "side", open: true },
      theme: "dark",
      locale: "en",
      openTarget: "cursor",
      sidebars: { projectPanelOpen: false, inspectorOpen: true },
      moduleDefaultsByProject: {
        EOH: [{ id: "focus-node", value: 72 }],
        PIHC3: [
          { id: "focus-node", value: 104 },
          { id: "technology-node", value: 56 },
          { id: "portrait", value: 164 },
          { id: "flag", value: 90 }
        ]
      },
      moduleOrderByProject: { PIHC3: ["ideas"] }
    });
  });

  it("applies project-scoped module defaults without changing SDK-backed defaults", () => {
    const settings = defaultConfigPageSettings();
    const pihc3 = configPageSettingsForProjectModuleDefaults(settings, {
      EOH: [{ id: "focus-node", value: 72 }],
      PIHC3: [
        { id: "focus-node", value: 132 },
        { id: "flag", value: 96 },
        { id: "thumbnail-cache", value: 512 }
      ]
    }, "PIHC3");
    const eoh = configPageSettingsForProjectModuleDefaults(settings, {
      EOH: [{ id: "focus-node", value: 72 }],
      PIHC3: [{ id: "focus-node", value: 132 }]
    }, "EOH");
    const unsavedProject = configPageSettingsForProjectModuleDefaults(pihc3, {
      PIHC3: [{ id: "focus-node", value: 132 }]
    }, "NEW_PROJECT");

    expect(pihc3.moduleDefaults.map((row) => [row.id, row.value])).toEqual([
      ["focus-node", 132],
      ["technology-node", 48],
      ["portrait", 156],
      ["flag", 96],
      ["thumbnail-cache", 256]
    ]);
    expect(eoh.moduleDefaults.map((row) => [row.id, row.value])).toEqual([
      ["focus-node", 72],
      ["technology-node", 48],
      ["portrait", 156],
      ["flag", 82],
      ["thumbnail-cache", 256]
    ]);
    expect(unsavedProject.moduleDefaults.map((row) => [row.id, row.value])).toEqual([
      ["focus-node", 96],
      ["technology-node", 48],
      ["portrait", 156],
      ["flag", 82],
      ["thumbnail-cache", 256]
    ]);
  });

  it("normalizes persisted AI chat window settings", () => {
    expect(normalizeChatSettings({ open: true, dock: "side" })).toEqual({
      dock: "side",
      open: true
    });
    expect(normalizeChatSettings({ open: "yes", dock: "corner" }, { dock: "side", open: true })).toEqual({
      dock: "side",
      open: false
    });
  });

  it("builds visible persistence failure status for backend write errors", () => {
    const failureStatus = (
      appModule as typeof appModule & {
        configPersistenceFailureStatus?: (subject: string, error: unknown) => unknown;
      }
    ).configPersistenceFailureStatus;

    expect(typeof failureStatus).toBe("function");
    expect(failureStatus?.("paradev.ai.model", new Error("bridge denied"))).toEqual({
      detail: "paradev.ai.model: bridge denied",
      labelKey: "config.page.saveFailed",
      state: "error"
    });
    expect(failureStatus?.("AI profile explain reset", "network down")).toEqual({
      detail: "AI profile explain reset: network down",
      labelKey: "config.page.saveFailed",
      state: "error"
    });
  });

  it("builds visible persistence failure status for backend load errors", () => {
    const loadFailureStatus = (
      appModule as typeof appModule & {
        configPersistenceLoadFailureStatus?: (subject: string, error: unknown) => unknown;
      }
    ).configPersistenceLoadFailureStatus;

    expect(typeof loadFailureStatus).toBe("function");
    expect(loadFailureStatus?.("paradev.ai.model", new Error("Unsupported desktop config key"))).toEqual({
      detail: "paradev.ai.model: Unsupported desktop config key",
      labelKey: "config.page.loadFailed",
      state: "error"
    });
  });

  it("blocks app settings autosave after a backend load failure", () => {
    const shouldPersist = (
      appModule as typeof appModule & {
        shouldPersistAppSettings?: (input: { settingsLoadFailed: boolean; settingsReady: boolean }) => boolean;
      }
    ).shouldPersistAppSettings;

    expect(typeof shouldPersist).toBe("function");
    expect(shouldPersist?.({ settingsReady: false, settingsLoadFailed: false })).toBe(false);
    expect(shouldPersist?.({ settingsReady: true, settingsLoadFailed: false })).toBe(true);
    expect(shouldPersist?.({ settingsReady: true, settingsLoadFailed: true })).toBe(false);
  });

  it("builds visible persistence saving status for pending backend writes", () => {
    expect(configPersistenceSavingStatus()).toEqual({
      labelKey: "config.page.saving",
      state: "saving"
    });
  });

  it("keeps fallback AI chat profiles available after profile load failures", () => {
    const source = readFileSync(resolve(__dirname, "App.tsx"), "utf8");

    expect(source).not.toContain("setAiChatProfiles([])");
    expect(source).not.toContain("setAiChatSourceKinds([])");
    expect(source).toContain("fallbackParaDevAiChatProfilesPayload");
    expect(source).toContain("current.length > 0 ? current : fallback.profiles");
  });

  it("keeps path status bridge failures visible in config rows", () => {
    const source = readFileSync(resolve(__dirname, "App.tsx"), "utf8");

    expect(source).toContain("pathStatusErrorByPath");
    expect(source).toContain("pathStatusLoadErrorDetail");
    expect(source).not.toContain(`console.warn("Failed to load ParaDev desktop path status.", error);
          return null;`);
  });

  it("creates dedicated diagram tabs for focus, technology, MIO, and doctrine modules", () => {
    const modules: FeatureModule[] = [
      { id: "focuses", titleKey: "modules.focuses.title", status: "ready", diagram: { id: "focus_tree", aliases: [], renderer: "focus-tree", title: "Focus tree", editable: true } },
      { id: "ideas", titleKey: "modules.ideas.title", status: "ready" },
      { id: "technologies", titleKey: "modules.technologies.title", status: "ready", diagram: { id: "technology", aliases: [], renderer: "technology", title: "Technology tree", editable: true } },
      { id: "military-industrial-organizations", titleKey: "modules.militaryIndustrialOrganizations.title", status: "ready", diagram: { id: "military_industrial_organization", aliases: [], renderer: "mio-trait", title: "MIO tree", editable: true } },
      { id: "doctrines", titleKey: "modules.doctrines.title", status: "ready", diagram: { id: "doctrine", aliases: [], renderer: "doctrine", title: "Doctrine tree", editable: true } }
    ];

    expect(tabsForModules(modules)).toEqual([
      { id: "focuses", titleKey: "modules.focuses.title", kind: "module" },
      { id: "ideas", titleKey: "modules.ideas.title", kind: "module" },
      { id: "technologies", titleKey: "modules.technologies.title", kind: "module" },
      { id: "military-industrial-organizations", titleKey: "modules.militaryIndustrialOrganizations.title", kind: "module" },
      { id: "doctrines", titleKey: "modules.doctrines.title", kind: "module" },
      { id: diagramTabIdForModule("focuses"), familyId: "focuses", kind: "diagram" },
      { id: diagramTabIdForModule("technologies"), familyId: "technologies", kind: "diagram" },
      { id: diagramTabIdForModule("military-industrial-organizations"), familyId: "military-industrial-organizations", kind: "diagram" },
      { id: diagramTabIdForModule("doctrines"), familyId: "doctrines", kind: "diagram" },
      { id: "config-general", titleKey: "config.general.title", kind: "config" },
      { id: "config-appearance", titleKey: "config.appearance.title", kind: "config" },
      { id: "config-models", titleKey: "config.models.title", kind: "config" },
      { id: "config-projects", titleKey: "config.projects.title", kind: "config" },
      { id: "config-module-defaults", titleKey: "config.moduleDefaults.title", kind: "config" },
      { id: "config-dependencies", titleKey: "config.dependencies.title", kind: "config" }
    ]);
  });

  it("maps the Focus diagram tab to the authoritative source-backed provider", () => {
    const browser = browserPayload(
      "focus",
      "focuses",
      "FOCUS_A",
      {
        id: "focus_tree",
        aliases: ["focus"],
        renderer: "focus-tree",
        title: "Focus tree",
        editable: true
      }
    );
    const scope = browserScopeForWorkspaceTab({ id: diagramTabIdForModule("focuses"), familyId: "focuses", kind: "diagram" }, browser);

    expect(scope).toEqual({ family: "focus" });
    expect(scopedBrowserKey("/tmp/PIHC3", scope)).toBe("/tmp/PIHC3::focus::::");
    expect(projectDiagramFamilyCapability(browser, "focuses")).toMatchObject({
      familyId: "focuses",
      sdkFamily: "focus_tree",
      sourceBacked: true
    });
  });

  it("maps the doctrine diagram tab to PIHC3's registered SDK provider", () => {
    const browser = browserPayload(
      "doctrine",
      "doctrines",
      "DOCTRINE_A",
      {
        id: "doctrine",
        aliases: ["doctrines"],
        renderer: "doctrine",
        title: "Doctrine tree",
        editable: true
      }
    );
    const scope = browserScopeForWorkspaceTab(
      { id: diagramTabIdForModule("doctrines"), familyId: "doctrines", kind: "diagram" },
      browser
    );

    expect(scope).toEqual({ family: "doctrine" });
    expect(scopedBrowserKey("/tmp/PIHC3", scope)).toBe("/tmp/PIHC3::doctrine::::");
  });

  it("maps the MIO diagram tab to the canonical source-backed family", () => {
    const browser = browserPayload(
      "military_industrial_organization",
      "military-industrial-organizations",
      "MIO_A",
      {
        id: "military_industrial_organization",
        aliases: ["mio"],
        renderer: "mio-trait",
        title: "MIO tree",
        editable: true
      }
    );
    const scope = browserScopeForWorkspaceTab(
      {
        id: diagramTabIdForModule("military-industrial-organizations"),
        familyId: "military-industrial-organizations",
        kind: "diagram"
      },
      browser
    );

    expect(scope).toEqual({ family: "military_industrial_organization" });
    expect(scopedBrowserKey("/tmp/PIHC3", scope)).toBe(
      "/tmp/PIHC3::military_industrial_organization::::"
    );
  });

  it("loads the Entity module's direct sources when its cached browser is summary-only", () => {
    const tab = { id: "entity", titleKey: "modules.entity.title", kind: "module" } as const;
    const scope = browserScopeForWorkspaceTab(tab, null);
    const loadingByKey = {
      [scopedBrowserKey("/tmp/PIHC3", scope)]: true
    };

    expect(scope).toEqual({ family: "entity" });
    expect(isWorkspaceTabBrowserLoading(tab, "/tmp/PIHC3", loadingByKey, null)).toBe(true);
  });

  it("builds AI chat workspace context from the active module tab", () => {
    const browser = browserPayload("focus", "focuses", "C01_MAIN");

    expect(aiChatSourcesForWorkspace({ id: "focuses", titleKey: "modules.focuses.title", kind: "module" }, null, browser, createTranslator("en"))).toEqual([
      {
        id: "workspace:focuses",
        kind: "workspace",
        label: "National Focuses",
        familyId: "focuses"
      }
    ]);
  });

  it("maps AI chat module draft operations to the create planner for the selected family", () => {
    const featureModules: FeatureModule[] = [
      { id: "focuses", titleKey: "modules.focuses.title", status: "ready" },
      { id: "ideas", titleKey: "modules.ideas.title", status: "ready" }
    ];

    expect(
      aiChatOperationNavigationTarget({
        activeModule: "ideas",
        featureModules,
        operationId: "module.draft",
        role: "create-module",
        sources: [{ kind: "workspace", label: "National Focuses", familyId: "focuses" }]
      })
    ).toEqual({
      createMode: "single",
      familyId: "focuses",
      operationId: "module.draft",
      rail: "projects",
      role: "create-module",
      sources: [{ kind: "workspace", label: "National Focuses", familyId: "focuses" }]
    });
  });

  it("maps AI chat batch operations to the retained batch planner without execution", () => {
    const featureModules: FeatureModule[] = [
      { id: "focuses", titleKey: "modules.focuses.title", status: "ready" },
      { id: "ideas", titleKey: "modules.ideas.title", status: "ready" }
    ];

    expect(
      aiChatOperationNavigationTarget({
        activeModule: "ideas",
        featureModules,
        operationId: "module.create_batch",
        role: "create-module",
        sources: []
      })
    ).toEqual({
      createMode: "batch",
      familyId: "ideas",
      operationId: "module.create_batch",
      rail: "projects",
      role: "create-module",
      sources: []
    });
  });

  it("maps collection scaffold operations to the retained collection planner", () => {
    expect(
      aiChatOperationNavigationTarget({
        activeModule: "focuses",
        featureModules: [{ id: "focuses" }],
        operationId: "collection.scaffold",
        role: "create-module",
        sources: []
      })
    ).toEqual({
      createMode: "collection",
      familyId: "focuses",
      operationId: "collection.scaffold",
      rail: "projects",
      role: "create-module",
      sources: []
    });
  });

  it("rejects AI batch review without replacing a pristine open planner", () => {
    const store = new ModuleEditorSessionStore();
    const sessionKey = moduleEditorSessionKey("/tmp/PIHC3", "ideas");
    const state = batchCreateState();
    const t = createTranslator("en");

    expect(() =>
      assertAiChatModuleBatchReviewAvailable({
        editorSessionStore: store,
        sessionKey,
        t
      })
    ).not.toThrow();

    store.setBatchCreate(sessionKey, state);
    expect(
      store.getSnapshot().sessions.find(
        (session) => session.key === sessionKey
      )?.batchCreateDirty
    ).toBeUndefined();

    expect(() =>
      assertAiChatModuleBatchReviewAvailable({
        editorSessionStore: store,
        sessionKey,
        t
      })
    ).toThrow(
      "A batch planner is already open for this module family. Close it before reviewing the AI plan."
    );
    expect(store.read(sessionKey)?.batchCreate).toEqual(state);
  });

  it("preserves the dirty-planner rejection when reviewing an AI batch", () => {
    const store = new ModuleEditorSessionStore();
    const sessionKey = moduleEditorSessionKey("/tmp/PIHC3", "ideas");
    const state = batchCreateState("IDEA_EXISTING");
    const t = createTranslator("en");

    store.setBatchCreate(sessionKey, state);
    expect(
      store.getSnapshot().sessions.find(
        (session) => session.key === sessionKey
      )?.batchCreateDirty
    ).toBe(true);

    expect(() =>
      assertAiChatModuleBatchReviewAvailable({
        editorSessionStore: store,
        sessionKey,
        t
      })
    ).toThrow(
      "A batch draft already has unsaved input in this module family. Review or discard that draft before opening the AI plan."
    );
    expect(store.read(sessionKey)?.batchCreate).toEqual(state);
  });

  it("rejects AI collection review without replacing retained collection input", () => {
    const store = new ModuleEditorSessionStore();
    const sessionKey = moduleEditorSessionKey("/tmp/PIHC3", "focuses");
    const t = createTranslator("en");

    expect(() =>
      assertAiChatCollectionReviewAvailable({
        editorSessionStore: store,
        sessionKey,
        t
      })
    ).not.toThrow();

    const pristineOpen = collectionCreateState();
    store.setCollectionCreate(sessionKey, pristineOpen);
    expect(() =>
      assertAiChatCollectionReviewAvailable({
        editorSessionStore: store,
        sessionKey,
        t
      })
    ).toThrow(
      "A collection planner is already open for this family. Close it before reviewing the AI plan."
    );

    const dirty = collectionCreateState("C99_AI_REVIEW");
    store.setCollectionCreate(sessionKey, dirty);
    expect(() =>
      assertAiChatCollectionReviewAvailable({
        editorSessionStore: store,
        sessionKey,
        t
      })
    ).toThrow(
      "A collection draft already has unsaved input in this family. Review or discard that draft before opening the AI plan."
    );
    expect(store.read(sessionKey)?.collectionCreate).toEqual(dirty);
  });

  it("rejects AI source review when the family has retained authoring", () => {
    const store = new ModuleEditorSessionStore();
    const sessionKey = moduleEditorSessionKey("/tmp/PIHC3", "ideas");
    const t = createTranslator("en");

    expect(() =>
      assertAiChatSourceUpdateReviewAvailable({
        editorSessionStore: store,
        sessionKey,
        t
      })
    ).not.toThrow();

    store.setInlineCreate(sessionKey, {
      templateId: "pihc3:idea/basic",
      objectId: "IDEA_ALPHA",
      values: {},
      showAdvanced: false
    });
    expect(() =>
      assertAiChatSourceUpdateReviewAvailable({
        editorSessionStore: store,
        sessionKey,
        t
      })
    ).toThrow("This module family already has unsaved authoring work");

    store.discard(sessionKey);
    store.setSourceUpdate(sessionKey, {
      open: true,
      requests: [],
      plan: {
        schema: "paradev.source-form-update-batch.v1",
        projectId: "PIHC3",
        changed: false,
        counts: { requested: 0, changed: 0, unchanged: 0 },
        updates: [],
        sourceEdits: []
      }
    });
    expect(() =>
      assertAiChatSourceUpdateReviewAvailable({
        editorSessionStore: store,
        sessionKey,
        t
      })
    ).toThrow("An AI source-edit review is already open");
  });

  it("maps AI chat build operations to the Build rail without execution", () => {
    expect(
      aiChatOperationNavigationTarget({
        activeModule: "focuses",
        featureModules: [{ id: "focuses" }],
        operationId: "build.start",
        role: "build",
        sources: [{ content: "large text is dropped", kind: "diagnostics", label: "3 diagnostics" }]
      })
    ).toEqual({
      operationId: "build.start",
      rail: "build",
      role: "build",
      sources: [{ kind: "diagnostics", label: "3 diagnostics" }]
    });
  });

  it("ignores unknown AI chat operation ids", () => {
    expect(
      aiChatOperationNavigationTarget({
        activeModule: "focuses",
        featureModules: [{ id: "focuses" }],
        operationId: "build.nuke",
        sources: []
      })
    ).toBeNull();
  });

  it("keeps project AI chat context available from empty or config workspaces", () => {
    const browser = browserPayload("focus", "focuses", "C01_MAIN");
    const projectContent = "Project: PIHC3; families: 1; rows: 1.";
    const templates = templatesPayload([
      {
        id: "idea/basic",
        title: "Basic idea",
        family: "idea",
        source: "builtin",
        args: {},
        files: ["info.json"]
      }
    ]);

    expect(aiChatSourcesForWorkspace(null, null, browser, createTranslator("en"), templates)).toEqual([
      {
        id: "workspace:project",
        kind: "workspace",
        label: "PIHC3",
        content: projectContent,
        contentChars: projectContent.length,
        truncated: false
      },
      {
        id: "templates:project",
        kind: "templates",
        label: "Templates (1)",
        content: "1. idea/basic - Basic idea (family: idea, source: builtin, 1 file, args: none)",
        contentChars: 78,
        truncated: false
      }
    ]);
  });

  it("uses SDK family totals for summary project AI chat context", () => {
    const parsedBrowser = browserPayload("focus", "focuses", "C01_MAIN");
    const browser: ProjectBrowserPayload = {
      ...parsedBrowser,
      families: [{ ...parsedBrowser.families[0], item_count: 7 }],
      items: []
    };
    const sources = aiChatSourcesForWorkspace(null, null, browser, createTranslator("en"));
    const projectContent = "Project: PIHC3; families: 1; rows: 7.";

    expect(sources[0]).toEqual({
      id: "workspace:project",
      kind: "workspace",
      label: "PIHC3",
      content: projectContent,
      contentChars: projectContent.length,
      truncated: false
    });
  });

  it("adds compact AI diagnostics context when the active project has diagnostics", () => {
    const browser = {
      ...browserPayload("focus", "focuses", "C01_MAIN"),
      diagnostics: [
        {
          message: "Missing focus icon.",
          path: "src/modules/focus_tree/C01_MAIN/info.json",
          severity: "error"
        },
        {
          code: "PDX001",
          detail: "Unexpected token near cost.",
          level: "warning",
          source_path: "src/modules/focus_tree/C01_MAIN/def.txt"
        }
      ]
    };

    expect(aiChatSourcesForWorkspace({ id: "focuses", titleKey: "modules.focuses.title", kind: "module" }, null, browser, createTranslator("en"))).toEqual([
      {
        id: "workspace:focuses",
        kind: "workspace",
        label: "National Focuses",
        familyId: "focuses"
      },
      {
        id: "diagnostics:project",
        kind: "diagnostics",
        label: "Diagnostics (2)",
        content:
          "1. [error] src/modules/focus_tree/C01_MAIN/info.json: Missing focus icon.\n" +
          "2. [warning PDX001] src/modules/focus_tree/C01_MAIN/def.txt: Unexpected token near cost.",
        contentChars: 162,
        truncated: false
      }
    ]);
  });

  it("adds SDK template context for AI module planning", () => {
    const browser = browserPayload("focus", "focuses", "C01_MAIN");
    const templates = templatesPayload([
      {
        id: "idea/basic",
        title: "Basic idea",
        family: "idea",
        source: "builtin",
        args: {
          idea_id: { required: true, default: "", advanced: false },
          name: { required: false, default: "New Idea", advanced: false }
        },
        files: ["info.json", "localisation.yml"]
      },
      {
        id: "focus/basic",
        title: "Basic focus",
        family: "focus_tree",
        source: "project",
        args: {
          focus_id: { required: true, default: "", advanced: false }
        },
        files: ["info.json"]
      }
    ]);

    const sources = aiChatSourcesForWorkspace({ id: "focuses", titleKey: "modules.focuses.title", kind: "module" }, null, browser, createTranslator("en"), templates);
    const templateSource = sources.find((source) => source.kind === "templates");

    expect(sources.map((source) => source.kind)).toEqual(["workspace", "templates"]);
    expect(templateSource).toMatchObject({
      id: "templates:project",
      label: "Templates (2)",
      truncated: false
    });
    expect(templateSource?.content).toContain("idea/basic - Basic idea");
    expect(templateSource?.content).toContain("focus/basic - Basic focus");
    expect(templateSource?.content).toContain("idea_id required");
    expect(templateSource?.contentChars).toBe(templateSource?.content?.length);
  });

  it("keeps scalar template defaults safe in AI planning context", () => {
    const browser = browserPayload("idea", "ideas", "IDEA_ALPHA");
    const templates = templatesPayload([
      {
        id: "pihc3:idea/basic",
        title: "PIHC3 idea",
        family: "idea",
        source: "project",
        args: {
          cic: {
            required: false,
            default: 0.02,
            advanced: false,
            choices: [0.02, 0.05, false]
          }
        },
        files: ["def.txt"]
      }
    ]);

    const sources = aiChatSourcesForWorkspace(
      null,
      null,
      browser,
      createTranslator("en"),
      templates
    );

    expect(sources.find((source) => source.kind === "templates")?.content).toContain(
      "cic default=0.02 choices=0.02/0.05/false"
    );
  });

  it("localizes AI chat template and diagnostic context bodies", () => {
    const browser = {
      ...browserPayload("focus", "focuses", "C01_MAIN"),
      diagnostics: [
        {
          path: "src/modules/focus_tree/C01_MAIN/def.txt",
          severity: "warning"
        }
      ]
    };
    const templates = templatesPayload([
      {
        id: "idea/basic",
        title: "Basic idea",
        family: "idea",
        source: "builtin",
        args: {
          idea_id: { required: true, default: "", advanced: false },
          name: { required: false, default: "New Idea", advanced: false }
        },
        files: ["info.json", "localisation.yml"]
      }
    ]);

    const sources = aiChatSourcesForWorkspace({ id: "focuses", titleKey: "modules.focuses.title", kind: "module" }, null, browser, createTranslator("zh"), templates);
    const templateSource = sources.find((source) => source.kind === "templates");
    const diagnosticSource = sources.find((source) => source.kind === "diagnostics");

    expect(templateSource?.content).toContain("系列: idea");
    expect(templateSource?.content).toContain("来源: builtin");
    expect(templateSource?.content).toContain("2 个文件");
    expect(templateSource?.content).toContain("参数: idea_id 必填; name 默认=New Idea");
    expect(templateSource?.content).not.toContain("family:");
    expect(templateSource?.content).not.toContain("required");
    expect(diagnosticSource?.content).toContain("无诊断消息。");
    expect(diagnosticSource?.content).not.toContain("No diagnostic message.");
  });

  it("localizes project-level AI chat context from non-module workspaces", () => {
    const browser = browserPayload("focus", "focuses", "C01_MAIN");
    const sources = aiChatSourcesForWorkspace(null, null, browser, createTranslator("zh"));

    expect(sources[0]).toMatchObject({
      id: "workspace:project",
      kind: "workspace",
      label: "PIHC3"
    });
    expect(sources[0]).not.toHaveProperty("path");
    expect(sources[0].content).toBe("项目：PIHC3；系列：1；条目：1。");
    expect(sources[0].content).not.toContain("Project:");
  });

  it("omits AI template context when the SDK has no templates", () => {
    const browser = browserPayload("focus", "focuses", "C01_MAIN");
    const templates = templatesPayload([]);

    expect(aiChatSourcesForWorkspace({ id: "focuses", titleKey: "modules.focuses.title", kind: "module" }, null, browser, createTranslator("en"), templates)).toEqual([
      {
        id: "workspace:focuses",
        kind: "workspace",
        label: "National Focuses",
        familyId: "focuses"
      }
    ]);
  });

  it("localizes the AI chat route error fallback", () => {
    expect(() => aiChatReplyText({ detail: "", reply: "", status: "error" }, createTranslator("zh"))).toThrow("AI 路由返回错误。");
  });

  it("builds AI chat source context when a diagram-open selection carries a source path", () => {
    const browser = browserPayload("focus", "focuses", "C01_MAIN");
    const target = {
      entityId: "C01_MAIN",
      familyId: "focuses",
      sourcePath: "src/modules/focus_tree/C01_MAIN/info.json"
    };

    expect(aiChatSourcesForWorkspace({ id: "focuses", titleKey: "modules.focuses.title", kind: "module" }, target, browser, createTranslator("en"))).toEqual([
      {
        id: "source:src/modules/focus_tree/C01_MAIN/info.json",
        kind: "source",
        label: "National Focuses: C01_MAIN",
        detail: "src/modules/focus_tree/C01_MAIN/info.json",
        path: "src/modules/focus_tree/C01_MAIN/info.json",
        familyId: "focuses",
        entityId: "C01_MAIN"
      }
    ]);
  });

  it("adds selected dirty source text to AI chat source context", () => {
    const browser = browserPayload("focus", "focuses", "C01_MAIN");
    const target = {
      entityId: "C01_MAIN",
      familyId: "focuses",
      sourcePath: "src/modules/focus_tree/C01_MAIN/info.json",
      sourceContent: '{"id":"C01_MAIN","focus":"edited"}\n'
    };

    expect(aiChatSourcesForWorkspace({ id: "focuses", titleKey: "modules.focuses.title", kind: "module" }, target, browser, createTranslator("en"))).toEqual([
      {
        id: "source:src/modules/focus_tree/C01_MAIN/info.json",
        kind: "source",
        label: "National Focuses: C01_MAIN",
        detail: "src/modules/focus_tree/C01_MAIN/info.json",
        path: "src/modules/focus_tree/C01_MAIN/info.json",
        content: '{"id":"C01_MAIN","focus":"edited"}\n',
        contentChars: 35,
        truncated: false,
        familyId: "focuses",
        entityId: "C01_MAIN"
      }
    ]);
  });

  it("preserves intentionally empty selected source text in AI chat source context", () => {
    const browser = browserPayload("focus", "focuses", "C01_MAIN");
    const target = {
      entityId: "C01_MAIN",
      familyId: "focuses",
      sourcePath: "src/modules/focus_tree/C01_MAIN/info.json",
      sourceContent: ""
    };

    expect(aiChatSourcesForWorkspace({ id: "focuses", titleKey: "modules.focuses.title", kind: "module" }, target, browser, createTranslator("en"))).toEqual([
      {
        id: "source:src/modules/focus_tree/C01_MAIN/info.json",
        kind: "source",
        label: "National Focuses: C01_MAIN",
        detail: "src/modules/focus_tree/C01_MAIN/info.json",
        path: "src/modules/focus_tree/C01_MAIN/info.json",
        content: "",
        contentChars: 0,
        truncated: false,
        familyId: "focuses",
        entityId: "C01_MAIN"
      }
    ]);
  });

  it("downgrades selected-entity AI chat context without a source path to workspace metadata", () => {
    const browser = browserPayload("focus", "focuses", "C01_MAIN");

    expect(
      aiChatSourcesForWorkspace(
        { id: "focuses", titleKey: "modules.focuses.title", kind: "module" },
        { entityId: "C01_MAIN", familyId: "focuses" },
        browser,
        createTranslator("en")
      )
    ).toEqual([
      {
        id: "workspace:focuses:C01_MAIN",
        kind: "workspace",
        label: "National Focuses: C01_MAIN",
        familyId: "focuses",
        entityId: "C01_MAIN"
      }
    ]);
  });

  it("reports pane loading for the workspace tab scoped browser key", () => {
    const tab = { id: diagramTabIdForModule("focuses"), familyId: "focuses", kind: "diagram" } as const;
    const scope = browserScopeForWorkspaceTab(tab, null);
    const loadingByKey = {
      [scopedBrowserKey("/tmp/PIHC3", scope)]: true
    };

    expect(isWorkspaceTabBrowserLoading(tab, "/tmp/PIHC3", loadingByKey, null)).toBe(true);
    expect(isWorkspaceTabBrowserLoading(tab, "/tmp/PIHC3", {}, null)).toBe(false);
    expect(isWorkspaceTabBrowserLoading(tab, "", loadingByKey, null)).toBe(false);
    expect(isWorkspaceTabBrowserLoading(null, "/tmp/PIHC3", loadingByKey, null)).toBe(false);
    expect(isWorkspaceTabBrowserLoading({ id: "focuses", kind: "module" }, "/tmp/PIHC3", loadingByKey, null)).toBe(false);
  });

  it("reports scoped browser load errors for the workspace tab key", () => {
    const tab = { id: diagramTabIdForModule("focuses"), familyId: "focuses", kind: "diagram" } as const;
    const scope = browserScopeForWorkspaceTab(tab, null);
    const errorByKey = {
      [scopedBrowserKey("/tmp/PIHC3", scope)]: "Scoped SDK data could not be loaded: bridge denied"
    };
    const browser = browserPayload("focus", "focuses", "C01_MAIN");

    expect(scopedBrowserErrorForWorkspaceTab(tab, "/tmp/PIHC3", errorByKey, null)).toBe("Scoped SDK data could not be loaded: bridge denied");
    expect(scopedBrowserErrorForWorkspaceTab(tab, "/tmp/PIHC3", {}, null)).toBeNull();
    expect(scopedBrowserErrorForWorkspaceTab(tab, "", errorByKey, null)).toBeNull();
    expect(scopedBrowserErrorForWorkspaceTab(null, "/tmp/PIHC3", errorByKey, null)).toBeNull();
    expect(scopedBrowserErrorForWorkspaceTab(tab, "/tmp/PIHC3", errorByKey, browser)).toBeNull();
    expect(scopedBrowserErrorForWorkspaceTab({ id: "focuses", kind: "module" }, "/tmp/PIHC3", errorByKey, null)).toBeNull();
  });

  it("does not request scoped browser data when the cached browser already contains the family", () => {
    const browser = browserPayload("focus", "focuses", "C01_MAIN");

    expect(browserHasScopedPayload(browser, { family: "focus" })).toBe(true);
    expect(browserHasScopedPayload(browser, { family: "idea" })).toBe(false);
  });

  it("does request scoped browser data when cached browser only contains summary counts", () => {
    const browser = browserPayload("focus", "focuses", "C01_MAIN");
    browser.items = [];
    browser.families = [{ ...browser.families[0], item_count: 42, source_count: 100 }];

    expect(browserHasScopedPayload(browser, { family: "focus_tree" })).toBe(false);
  });

  it("keeps ordinary module tabs out of eager scoped browser loading", () => {
    const browser = browserPayload("focus", "focuses", "C01_MAIN");
    const scope = browserScopeForWorkspaceTab({ id: "focuses", titleKey: "modules.focuses.title", kind: "module" }, browser);

    expect(scope).toBeNull();
  });

  it("resolves a Technology module build from source only when the Catalog is missing", () => {
    const summary = browserPayload(
      "technology",
      "technologies",
      "module:technology/TECHNOLOGY_FIREARM_I"
    );
    summary.items = [];
    summary.families = [
      {
        ...summary.families[0],
        item_count: 300,
        source_count: 600
      }
    ];
    const tab: WorkspaceTab = {
      id: "technologies",
      kind: "module",
      titleKey: "modules.technologies.title"
    };

    expect(
      sourceBrowserScopeForUnavailableCatalog(tab, summary, {
        code: "catalog.present"
      })
    ).toBeNull();
    expect(
      sourceBrowserScopeForUnavailableCatalog(tab, summary, {
        code: "catalog.incomplete"
      })
    ).toEqual({ family: "technology" });
    expect(
      sourceBrowserScopeForUnavailableCatalog(tab, summary, {
        code: "catalog.unreadable"
      })
    ).toEqual({ family: "technology" });
    const scope = sourceBrowserScopeForUnavailableCatalog(tab, summary, {
      code: "catalog.missing"
    });
    expect(scope).toEqual({ family: "technology" });
    expect(browserHasScopedPayload(summary, scope)).toBe(false);

    const sourceBrowser = browserPayload(
      "technology",
      "technologies",
      "module:technology/TECHNOLOGY_FIREARM_I"
    );
    sourceBrowser.filters = { family: "technology" };
    const merged = mergeProjectBrowserPayloads(summary, sourceBrowser);
    expect(browserHasScopedPayload(merged, scope)).toBe(true);
    const [entity] = buildModuleEntities(merged!, "technologies");
    expect(entity?.moduleId).toBe("technology/TECHNOLOGY_FIREARM_I");

    expect(
      resolveBuildTargetForBrowser(merged, {
        family: entity?.family,
        id: entity?.moduleId ?? "",
        kind: "module"
      })
    ).toEqual({
      family: "technology",
      id: "technology/TECHNOLOGY_FIREARM_I",
      kind: "module"
    });
  });

  it("claims each missing-Catalog source fallback only once per project refresh", () => {
    const claimed = new Set<string>();
    const key = scopedBrowserKey("/tmp/PIHC3", { family: "technology" });

    expect(claimSourceBrowserFallbackCheck(claimed, key)).toBe(true);
    expect(claimSourceBrowserFallbackCheck(claimed, key)).toBe(false);
    expect([...claimed]).toEqual(["/tmp/PIHC3::technology::::"]);

    claimed.clear();
    expect(claimSourceBrowserFallbackCheck(claimed, key)).toBe(true);
    expect(claimSourceBrowserFallbackCheck(claimed, "")).toBe(false);
  });

  it("replaces the Entity summary with its scoped editable aggregate in the browser cache", () => {
    const summary = browserPayload("entity", "entity", "module:entity/HOI4DEV_ENTITIES");
    summary.families = [{ ...summary.families[0], item_count: 1, source_count: 184 }];
    summary.items = [];
    const scoped = browserPayload("entity", "entity", "module:entity/HOI4DEV_ENTITIES");
    scoped.families = [{ ...scoped.families[0], item_count: 1, source_count: 184 }];
    scoped.items = [{ ...scoped.items[0], source_count: 183 }];
    const scope = browserScopeForWorkspaceTab({ id: "entity", kind: "module" }, summary);

    expect(browserHasScopedPayload(summary, scope)).toBe(false);

    const merged = mergeProjectBrowserPayloads(summary, scoped);

    expect(merged?.families).toEqual(scoped.families);
    expect(merged?.items).toEqual(scoped.items);
    expect(browserHasScopedPayload(merged, scope)).toBe(true);
  });

  it("merges scoped browser payloads by canonical family id", () => {
    const fullBrowser = browserPayload("technology", "technologies", "TECH_A");
    const scopedFocus = browserPayload("focus", "focuses", "C01_MAIN");
    const replacementFocus = browserPayload("focus", "focuses", "C08_PARTIV");

    const merged = mergeProjectBrowserPayloads(fullBrowser, scopedFocus, replacementFocus);

    expect(merged?.families.map((family) => family.family)).toEqual(["technology", "focus"]);
    expect(merged?.items.map((item) => item.id)).toEqual(["TECH_A", "C08_PARTIV"]);
  });

  it("replaces a scoped family without moving it in the project summary order", () => {
    const technology = browserPayload("technology", "technologies", "TECH_A");
    const focus = browserPayload("focus", "focuses", "C01_MAIN");
    const entity = browserPayload("entity", "entity", "ENTITY_A");
    const summary: ProjectBrowserPayload = {
      ...technology,
      families: [...technology.families, ...focus.families, ...entity.families],
      items: [...technology.items, ...focus.items, ...entity.items]
    };
    const replacementFocus = {
      ...browserPayload("focus", "focuses", "C08_PARTIV"),
      filters: { family: "focus_tree" }
    };

    const merged = mergeProjectBrowserPayloads(summary, replacementFocus);

    expect(merged?.families.map((family) => family.family)).toEqual(["technology", "focus", "entity"]);
    expect(merged?.items.map((item) => item.id)).toEqual(["TECH_A", "ENTITY_A", "C08_PARTIV"]);
  });

  it("does not replace unrelated summary counts from a scoped source response", () => {
    const technology = browserPayload("technology", "technologies", "TECH_A");
    const focus = browserPayload("focus", "focuses", "C01_MAIN");
    const entity = browserPayload("entity", "entity", "ENTITY_A");
    const summary: ProjectBrowserPayload = {
      ...technology,
      families: [
        { ...technology.families[0], item_count: 300, source_count: 600 },
        { ...focus.families[0], item_count: 766, source_count: 3727 },
        { ...entity.families[0], item_count: 135, source_count: 316 }
      ],
      items: []
    };
    const scopedFocus: ProjectBrowserPayload = {
      ...focus,
      filters: { family: "focus" },
      families: [
        { ...technology.families[0], item_count: 0, source_count: 0 },
        { ...focus.families[0], item_count: 766, source_count: 3727 },
        { ...entity.families[0], item_count: 0, source_count: 0 }
      ]
    };

    const merged = mergeProjectBrowserPayloads(summary, scopedFocus);

    expect(
      merged?.families.map(({ family, item_count, source_count }) => ({
        family,
        item_count,
        source_count
      }))
    ).toEqual([
      { family: "technology", item_count: 300, source_count: 600 },
      { family: "focus", item_count: 766, source_count: 3727 },
      { family: "entity", item_count: 135, source_count: 316 }
    ]);
    expect(merged?.items.map((item) => item.id)).toEqual(["C01_MAIN"]);
  });

  it("filters scoped browser payloads to the active project root before merging", () => {
    const pihc3Browser = browserPayload("technology", "technologies", "TECH_A");
    const staleBrowser = {
      ...browserPayload("focus", "focuses", "C01_MAIN"),
      project_id: "OtherProject",
      root: "/tmp/OtherProject"
    };

    const merged = mergeProjectBrowserPayloadsForProject("/tmp/PIHC3", pihc3Browser, staleBrowser);

    expect(merged?.project_id).toBe("PIHC3");
    expect(merged?.families.map((family) => family.family)).toEqual(["technology"]);
    expect(merged?.items.map((item) => item.id)).toEqual(["TECH_A"]);
  });

  it("rejects stale scoped browser responses after the active project changes", () => {
    const pihc3Browser = browserPayload("focus", "focuses", "C01_MAIN");

    expect(shouldCommitScopedBrowserPayload(pihc3Browser, "/tmp/PIHC3", "/tmp/PIHC3", 7, 7)).toBe(true);
    expect(shouldCommitScopedBrowserPayload(pihc3Browser, "/tmp/PIHC3", "/tmp/OtherProject", 7, 7)).toBe(false);
    expect(shouldCommitScopedBrowserPayload({ ...pihc3Browser, root: "/tmp/OtherProject" }, "/tmp/PIHC3", "/tmp/PIHC3", 7, 7)).toBe(false);
  });

  it("rejects scoped browser responses captured before a same-project refresh", () => {
    const pihc3Browser = browserPayload("focus", "focuses", "C01_MAIN");

    expect(shouldCommitScopedBrowserPayload(pihc3Browser, "/tmp/PIHC3", "/tmp/PIHC3", 7, 8)).toBe(false);
  });

  it("keeps an unfiltered same-project browser visible while an explicit summary refresh runs", () => {
    const browser = browserPayload("focus", "focuses", "C01_MAIN");
    const project = { project_id: "PIHC3", title: "PIHC3", game: "hoi4", root: "/tmp/PIHC3", manifest: "/tmp/PIHC3/paradev.yaml", source_roots: [] };
    const state: DesktopStatePayload = {
      schema: "paradev.desktop.state.v1",
      projects: [project],
      active_project: project,
      browser,
      templates: null,
      diagnostics: []
    };

    expect(projectBrowserBaseForRefresh("/tmp/PIHC3", null, state)).toBe(browser);
    expect(projectBrowserBaseForRefresh("/tmp/Other", null, state)).toBeNull();
    expect(projectBrowserBaseForRefresh("/tmp/PIHC3", { ...browser, filters: { family: "focus_tree" } }, state)).toBe(browser);
  });

  it("keeps module selection routed to the normal module tab", () => {
    expect(workspaceTabIdForModuleSelection("focuses")).toBe("focuses");
    expect(workspaceTabIdForModuleSelection("technologies")).toBe("technologies");
    expect(workspaceTabIdForModuleSelection("ideas")).toBe("ideas");
  });

  it("keeps unpinned diagram previews separate from normal module previews", () => {
    const focusesDiagram = { id: diagramTabIdForModule("focuses"), familyId: "focuses", kind: "diagram" } as const;
    const technologiesDiagram = { id: diagramTabIdForModule("technologies"), familyId: "technologies", kind: "diagram" } as const;
    const focusesModule = { id: "focuses", titleKey: "modules.focuses.title", kind: "module" } as const;
    const ideasModule = { id: "ideas", titleKey: "modules.ideas.title", kind: "module" } as const;

    const withDiagram = nextOpenTabEntriesForOpen([], focusesDiagram);
    expect(withDiagram.map(({ id, pinned }) => ({ id, pinned }))).toEqual([
      { id: "diagram:focuses", pinned: false }
    ]);
    expect(withDiagram[0]?.tab).toEqual(focusesDiagram);

    const withModule = nextOpenTabEntriesForOpen(withDiagram, focusesModule);
    expect(withModule.map(({ id, pinned }) => ({ id, pinned }))).toEqual([
      { id: "diagram:focuses", pinned: false },
      { id: "focuses", pinned: false }
    ]);

    expect(
      nextOpenTabEntriesForOpen(withModule, ideasModule).map(
        ({ id, pinned }) => ({ id, pinned })
      )
    ).toEqual([
      { id: "diagram:focuses", pinned: false },
      { id: "ideas", pinned: false }
    ]);

    expect(
      nextOpenTabEntriesForOpen(withModule, technologiesDiagram).map(
        ({ id, pinned }) => ({ id, pinned })
      )
    ).toEqual([
      { id: "diagram:technologies", pinned: false },
      { id: "focuses", pinned: false }
    ]);
  });

  it("keeps module and config previews in the regular preview slot", () => {
    const focusesModule = { id: "focuses", titleKey: "modules.focuses.title", kind: "module" } as const;
    const projectsConfig = { id: "config-projects", titleKey: "config.projects.title", kind: "config" } as const;
    const withModule = nextOpenTabEntriesForOpen([], focusesModule);

    expect(
      nextOpenTabEntriesForOpen(withModule, projectsConfig).map(
        ({ id, pinned }) => ({ id, pinned })
      )
    ).toEqual([{ id: "config-projects", pinned: false }]);
  });

  it("retains a cached preview through transient model omissions and rebinds it when the family returns", () => {
    const store = new ModuleEditorSessionStore();
    const tab: WorkspaceTab = {
      id: "technologies",
      title: "Technology",
      kind: "module"
    };
    const key = moduleEditorSessionKeyForWorkspaceTab("/tmp/PIHC3", tab);
    expect(key).not.toBeNull();
    if (!key) {
      throw new Error("Expected a technologies session key.");
    }
    const entries = nextOpenTabEntriesForOpen([], tab);
    const release = vi.fn();
    store.ownResource(key, "blob:technology-preview", release);

    const omitted = reconcileOpenTabEntries(
      "/tmp/PIHC3",
      entries,
      [],
      store
    );
    expect(omitted.entries).toBe(entries);
    expect(omitted.cleanupFailure).toBeNull();
    expect(release).not.toHaveBeenCalled();
    expect(store.read(key)).not.toBeNull();

    const reboundTab: WorkspaceTab = {
      id: "technologies",
      title: "Technologies",
      kind: "module"
    };
    expect(
      reconcileOpenTabEntries(
        "/tmp/PIHC3",
        omitted.entries,
        [reboundTab],
        store
      ).entries
    ).toEqual([
      {
        id: "technologies",
        pinned: false,
        tab: reboundTab
      }
    ]);
  });

  it("keeps a cacheless legacy tab reachable when clean session disposal fails", () => {
    const store = new ModuleEditorSessionStore();
    const tab: WorkspaceTab = { id: "ideas", kind: "module" };
    const key = moduleEditorSessionKeyForWorkspaceTab("/tmp/PIHC3", tab);
    expect(key).not.toBeNull();
    if (!key) {
      throw new Error("Expected an ideas session key.");
    }
    const entries = [{ id: tab.id, pinned: false }];
    store.ownResource(key, "blob:idea-preview", () => {
      throw new Error("preview cleanup failed");
    });

    const reconciled = reconcileOpenTabEntries(
      "/tmp/PIHC3",
      entries,
      [],
      store
    );

    expect(reconciled.entries).toEqual([
      {
        ...entries[0],
        tab: {
          ...tab,
          title: "ideas"
        }
      }
    ]);
    expect(reconciled.cleanupFailure).toMatchObject({
      key,
      tabId: "ideas"
    });
    expect(store.read(key)).not.toBeNull();
  });

  it("cleans a cacheless unavailable tab's retained session before pruning", () => {
    const store = new ModuleEditorSessionStore();
    const tab: WorkspaceTab = { id: "ideas", kind: "module" };
    const key = moduleEditorSessionKeyForWorkspaceTab("/tmp/PIHC3", tab);
    expect(key).not.toBeNull();
    if (!key) {
      throw new Error("Expected an ideas session key.");
    }
    const release = vi.fn();
    store.ownResource(key, "blob:idea-preview", release);

    const reconciled = reconcileOpenTabEntries(
      "/tmp/PIHC3",
      [{ id: tab.id, pinned: true }],
      [],
      store
    );

    expect(reconciled.entries).toEqual([]);
    expect(reconciled.cleanupFailure).toBeNull();
    expect(release).toHaveBeenCalledOnce();
    expect(store.read(key)).toBeNull();
  });

  it("attempts shared orphan-session cleanup only once per reconciliation", () => {
    const store = new ModuleEditorSessionStore();
    const moduleTab: WorkspaceTab = {
      id: "technologies",
      kind: "module"
    };
    const diagramTab: WorkspaceTab = {
      id: diagramTabIdForModule("technologies"),
      familyId: "technologies",
      kind: "diagram"
    };
    const key = moduleEditorSessionKeyForWorkspaceTab(
      "/tmp/PIHC3",
      moduleTab
    );
    expect(key).not.toBeNull();
    if (!key) {
      throw new Error("Expected a technologies session key.");
    }
    const release = vi.fn(() => {
      throw new Error("preview cleanup failed");
    });
    store.ownResource(key, "blob:technology-preview", release);
    const entries = [
      { id: moduleTab.id, pinned: true },
      { id: diagramTab.id, pinned: true }
    ];

    const reconciled = reconcileOpenTabEntries(
      "/tmp/PIHC3",
      entries,
      [],
      store
    );

    expect(reconciled.entries).toEqual([
      {
        ...entries[0],
        tab: {
          ...moduleTab,
          title: "technologies"
        }
      },
      {
        ...entries[1],
        tab: {
          ...diagramTab,
          title: "technologies"
        }
      }
    ]);
    expect(reconciled.cleanupFailure).toMatchObject({
      key,
      tabId: moduleTab.id
    });
    expect(release).toHaveBeenCalledOnce();
    expect(store.read(key)).not.toBeNull();
  });

  it("prompts only when closing the final view of a dirty or busy editor session", () => {
    const store = new ModuleEditorSessionStore();
    const moduleTab: WorkspaceTab = { id: "ideas", kind: "module" };
    const diagramTab: WorkspaceTab = {
      id: diagramTabIdForModule("ideas"),
      familyId: "ideas",
      kind: "diagram"
    };
    const key = moduleEditorSessionKeyForWorkspaceTab("/tmp/PIHC3", moduleTab);
    expect(key).not.toBeNull();
    if (!key) {
      throw new Error("Expected a module editor session key.");
    }
    store.setInlineCreate(key, {
      templateId: "hoi4.idea",
      objectId: "IDEA_NEW",
      values: {},
      showAdvanced: false
    });

    expect(
      moduleEditorSessionKeyRequiringClosePrompt(
        "/tmp/PIHC3",
        moduleTab.id,
        [moduleTab, diagramTab],
        store.getSnapshot()
      )
    ).toBeNull();
    expect(
      moduleEditorSessionKeyRequiringClosePrompt(
        "/tmp/PIHC3",
        moduleTab.id,
        [moduleTab],
        store.getSnapshot()
      )
    ).toBe(key);
    expect(
      moduleEditorSessionKeyRequiringClosePrompt(
        "/tmp/other",
        moduleTab.id,
        [moduleTab],
        store.getSnapshot()
      )
    ).toBeNull();

    store.setInlineCreate(key, null);
    const finishBusy = store.beginBusy(key);
    expect(
      moduleEditorSessionKeyRequiringClosePrompt(
        "/tmp/PIHC3",
        moduleTab.id,
        [moduleTab],
        store.getSnapshot()
      )
    ).toBe(key);
    finishBusy();
  });

  it("completes an error-free close intent only after its work is clean", () => {
    const store = new ModuleEditorSessionStore();
    const tab: WorkspaceTab = { id: "ideas", kind: "module" };
    const key = moduleEditorSessionKeyForWorkspaceTab("/tmp/PIHC3", tab);
    expect(key).not.toBeNull();
    if (!key) {
      throw new Error("Expected an ideas session key.");
    }
    const tabIntent = { key, kind: "tab" as const, tabId: tab.id };

    store.setInlineCreate(key, {
      templateId: "hoi4.idea",
      objectId: "IDEA_NEW",
      values: {},
      showAdvanced: false
    });
    expect(
      shouldCompleteAuthoringCloseIntent(tabIntent, store.getSnapshot())
    ).toBe(false);
    store.setInlineCreate(key, null);
    expect(
      shouldCompleteAuthoringCloseIntent(tabIntent, store.getSnapshot())
    ).toBe(true);
    const finishBusy = store.beginBusy(key);
    expect(
      shouldCompleteAuthoringCloseIntent(tabIntent, store.getSnapshot())
    ).toBe(false);
    finishBusy();
    expect(
      shouldCompleteAuthoringCloseIntent(tabIntent, store.getSnapshot())
    ).toBe(true);
    expect(
      shouldCompleteAuthoringCloseIntent(
        { ...tabIntent, error: "cleanup failed" },
        store.getSnapshot()
      )
    ).toBe(false);
  });

  it("renders a static startup indicator before React mounts", () => {
    const html = readFileSync(resolve(__dirname, "../index.html"), "utf8");

    expect(html).toContain('id="paradev-startup-style"');
    expect(html).toContain('id="paradev-startup"');
    expect(html).toContain('role="status"');
    expect(html).toContain('aria-label="Starting ParaDev"');
    expect(html).not.toContain("Preparing workspace");
    expect(html).not.toContain('class="paradev-startup-copy"');
  });
});
