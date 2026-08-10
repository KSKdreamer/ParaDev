import { useCallback, useEffect, useLayoutEffect, useMemo, useRef, useState, useSyncExternalStore, type SetStateAction } from "react";
import { APP_SETTINGS_STORAGE_KEY } from "./appSettingsStorage";
import { aiRouteLabelWithPreset } from "./aiRouteText";
import {
  buildOutputOpenPath,
  type BuildTarget,
  type BuildTargetIntent
} from "./buildPage/buildPageModel";
import type { BuildDiagnosticsRefreshSource } from "./buildPage/buildDiagnosticsCache";
import { useBuildRunLifecycle } from "./buildPage/buildRunLifecycle";
import { AppShell } from "./components/AppShell";
import type {
  AiChatOperationNavigation,
  AiChatProposalReview
} from "./components/FloatingChatShell";
import { ProjectOnboarding } from "./components/ProjectOnboarding";
import { CONFIG_AI_PRESET_VALUES, CONFIG_CLI_OUTPUT_VALUES, CONFIG_HOI4_LAUNCH_MODE_VALUES, defaultConfigLlmStatus, defaultConfigPageSettings, defaultConfigPersistenceStatus, dependencyErrorStatus, llmErrorStatus, normalizeConfigPageSettings, type ConfigDependencyStatus, type ConfigLlmStatus, type ConfigPageSettings, type ConfigPersistenceStatus } from "./configPage/model";
import { configOptions, defaultRailId, featureModules as baseFeatureModules, projectOptions as fallbackProjectOptions, railItems, surfaceRows, workspaceTabs as baseWorkspaceTabs } from "./data/shell";
import { DESKTOP_CONFIG_KEYS, PARADEV_DESKTOP_CONFIG_KEYS, type DesktopConfigKey } from "./desktopConfig";
import { localizedParaDevServiceError, localizeDesktopBridgeError } from "./desktopBridgeErrors";
import { PARADEV_FRONTEND_API_OPERATION_IDS, type ParaDevFrontendApiOperationId } from "./generated/frontendApi";
import { createTranslator, htmlLangForLocale, type Locale, type Translator } from "./i18n";
import {
  ModuleEditorSessionStore,
  moduleEditorSessionKey,
  type ModuleEditorSessionKey,
  type ModuleEditorSessionStoreSnapshot
} from "./moduleEditor/editorSessionStore";
import {
  prepareAiChatCollectionReview,
  prepareAiChatModuleBatchReview,
  prepareAiChatSourceUpdateReview
} from "./moduleEditor/aiChatBatchProposal";
import { currentOpenPathPlatform, normalizeOpenPathTarget, OPEN_PATH_TARGETS, type OpenPathPlatform, type OpenPathTarget } from "./openPathTargets";
import { applyModuleOrder, canonicalFamilyId, diagramTabIdForModule, isDiagramTabId, moduleIdForDiagramTabId, moduleTitleKeyForFamilyId, modulesForProjectState, moveModuleBefore, projectBrowserFamily, workspaceFamilyIdForFamily } from "./projectModules";
import { isUnfilteredProjectBrowserPayload, readCachedProjectBrowser, writeCachedProjectBrowser } from "./projectBrowserCache";
import { templateScalarText } from "./templateValues";
import {
  installAuthoringCloseGuards
} from "./services/authoringCloseGuard";
import {
  chatWithParaDevAi,
  checkDesktopDependency,
  fallbackParaDevAiChatProfilesPayload,
  hasDesktopBackend,
  importProjectPackage,
  installDesktopDependency,
  loadDesktopPathStatus,
  loadDesktopState,
  loadParaDevAiChatProfiles,
  loadProjectBrowser,
  loadProjectCatalogStatus,
  openProjectPath,
  readAppConfig,
  readConfigValue,
  resetParaDevAiChatProfile,
  selectProjectPath,
  setProjectPreferredLanguage,
  testHeavenBaseLlmRoute,
  writeAppConfig,
  writeParaDevAiChatProfile,
  writeConfigValue,
  type ParaDevAiChatPayload,
  type ParaDevAiChatProfile,
  type ParaDevAiChatProfileWrite,
  type ParaDevAiChatSource,
  type ParaDevAiChatSourceKindRow,
  type DesktopPathStatusPayload,
  type ProjectCatalogStatusPayload
} from "./services/paradev";
import type { AiOperationIntent, AiOperationIntentSource, BootProgressState, DesktopProjectRow, DesktopStatePayload, FeatureModule, ModuleCreateIntent, PanelOption, ProjectBrowserPayload, ProjectOption, ProjectTemplate, ProjectTemplatesPayload, ThemeName, WorkspaceModuleSelectionTarget, WorkspaceTab } from "./types";

const APP_SETTINGS_SCHEMA = "paradev.desktop.app-settings.v1";
const MODULE_ORDER_STORAGE_PREFIX = "paradev.moduleOrder";
const OPEN_TARGET_STORAGE_KEY = "paradev.openTarget";
const THUMBNAIL_CACHE_MODULE_DEFAULT_ID = "thumbnail-cache";
const EMPTY_PROJECT_OPTION: ProjectOption = {
  id: "",
  projectId: "",
  name: "",
  path: ""
};

export { htmlLangForLocale } from "./i18n";

export type AiChatDock = "floating" | "side";

type AiChatSettings = {
  dock: AiChatDock;
  open: boolean;
};

type DesktopConfigWrite = [DesktopConfigKey, unknown];
type PersistedModuleDefault = Pick<ConfigPageSettings["moduleDefaults"][number], "id" | "value">;
type ModuleDefaultsByProject = Record<string, PersistedModuleDefault[]>;

export type DesktopStateRefreshOptions = {
  recoverRememberedProject?: boolean;
  throwOnError?: boolean;
};

type DesktopStateRefresh = (
  projectRoot?: string,
  fallbackProjectIdentity?: string,
  options?: DesktopStateRefreshOptions
) => Promise<void>;
type BuildDiagnosticsRefresh = (
  projectRoot: string,
  source: BuildDiagnosticsRefreshSource
) => Promise<void>;
type BuildDiagnosticsRefreshState = {
  generation: number;
  source: BuildDiagnosticsRefreshSource;
};

export type OpenTabEntry = {
  id: string;
  pinned: boolean;
  /** Last known SDK-backed tab identity, retained across catalog refreshes. */
  tab?: Omit<WorkspaceTab, "dirty" | "pinned">;
};

type AppSettingsPayload = {
  schema: typeof APP_SETTINGS_SCHEMA;
  activeProjectId: string;
  activeProjectPath: string;
  chat: AiChatSettings;
  configPage: ConfigPageSettings;
  theme: ThemeName;
  locale: Locale;
  openTarget: OpenPathTarget;
  sidebars: {
    projectPanelOpen: boolean;
    inspectorOpen: boolean;
  };
  moduleOrderByProject: Record<string, string[]>;
  moduleDefaultsByProject: ModuleDefaultsByProject;
};

type PersistedAppSettingsRead = {
  configLoadFailure: ConfigPersistenceStatus | null;
  settings: AppSettingsPayload;
};

type PersistableAppSettingsPayload = Omit<AppSettingsPayload, "activeProjectId" | "configPage">;

type AppBootProgressInput = {
  activeProjectName: string;
  browserItemCount?: number;
  desktopStateLoaded: boolean;
  diagnosticCount?: number;
  openTarget: OpenPathTarget;
  projectError: string;
  projectLoading: boolean;
  projectOpening: boolean;
  settingsReady: boolean;
  templateCount?: number;
  t: Translator;
};

export type ProjectBootOutcome =
  | {
      kind: "browser-fallback";
    }
  | {
      kind: "checking";
    }
  | {
      kind: "project-required";
      error: string;
      requestedPath: string;
    }
  | {
      kind: "ready";
    };

export type ProjectRefreshFailureDisposition = {
  bootOutcome: ProjectBootOutcome;
  candidateProject: boolean;
  preserveWorkspace: boolean;
};

export type RememberedProjectRecovery = {
  error: string;
  recoveredPath: string;
  recoveredTitle: string;
  requestedPath: string;
};

type DesktopStateLoad = (
  projectRoot?: string
) => Promise<DesktopStatePayload>;

export { diagramTabIdForModule } from "./projectModules";
type WorkspacePreviewGroup = "diagram" | "regular";
type WorkspaceViewState = {
  activeModule: string;
  activeTab: string;
  moduleSelectionTarget: WorkspaceModuleSelectionTarget | null;
  openTabEntries: OpenTabEntry[];
  secondaryTab: string;
  splitView: boolean;
};
export type AuthoringCloseIntent =
  | {
      error?: string;
      key: ModuleEditorSessionKey;
      kind: "tab";
      tabId: string;
    }
  | {
      kind: "busy";
    };
type ProjectBrowserScope = {
  family?: string;
  moduleId?: string;
  collectionId?: string;
};

export type AiChatOperationNavigationTarget =
  | {
      operationId: "build.plan" | "build.start";
      rail: "build";
      role: string;
      sources: AiOperationIntentSource[];
    }
  | {
      createMode: "batch" | "collection" | "single";
      familyId: string;
      operationId: "collection.scaffold" | "module.create_batch" | "module.draft";
      rail: "projects";
      role: string;
      sources: AiOperationIntentSource[];
    };

export function projectRowsToOptions(rows: DesktopProjectRow[]): ProjectOption[] {
  return rows.map((project) => ({
    id: project.root,
    projectId: project.project_id,
    name: project.title,
    path: project.root,
    descriptor: project.descriptor,
    game: project.game,
    preferredLanguage: project.preferred_language,
    manifest: project.manifest,
    sourceRoots: project.source_roots,
    version: project.version,
    outputRoot: project.output_root,
    buildRoot: project.build_root,
    status: project.status
  }));
}

export function appBootProgress({ activeProjectName, browserItemCount, desktopStateLoaded, diagnosticCount, openTarget, projectError, projectLoading, projectOpening, settingsReady, templateCount, t }: AppBootProgressInput): BootProgressState | null {
  if (projectError && !desktopStateLoaded) {
    return {
      label: t("app.boot.project.error.label"),
      detail: projectError,
      status: "error",
      value: 100
    };
  }
  if (!settingsReady) {
    return {
      label: t("app.boot.settings.label"),
      detail: t("app.boot.settings.detail"),
      value: 24
    };
  }
  if (projectLoading && !desktopStateLoaded) {
    return {
      label: t("app.boot.project.label"),
      detail: t("app.boot.project.detail", { project: activeProjectName }),
      value: 64
    };
  }
  if (projectOpening) {
    return {
      label: t("app.boot.open.label"),
      detail: t("app.boot.open.detail", { project: activeProjectName, target: t(openTargetLabelKey(openTarget)) }),
      value: 92
    };
  }
  if (projectLoading) {
    const hasPayloadSummary = browserItemCount !== undefined || templateCount !== undefined || diagnosticCount !== undefined;
    return {
      label: t("app.boot.refresh.label"),
      detail: hasPayloadSummary
        ? t("app.boot.refresh.loadedDetail", {
            diagnostics: formatBootCount(diagnosticCount ?? 0),
            items: formatBootCount(browserItemCount ?? 0),
            project: activeProjectName,
            templates: formatBootCount(templateCount ?? 0)
          })
        : t("app.boot.refresh.detail", { project: activeProjectName }),
      value: hasPayloadSummary ? 86 : 82
    };
  }
  return null;
}

export function shouldCommitProjectRefresh(requestId: number, latestRequestId: number): boolean {
  return requestId === latestRequestId;
}

export function shouldUseCachedProjectBrowserForRefresh(projectRoot?: string): boolean {
  return projectRoot === undefined || projectRoot.trim() === "";
}

export function initialProjectBootOutcome(desktopBackend: boolean): ProjectBootOutcome {
  return desktopBackend ? { kind: "checking" } : { kind: "browser-fallback" };
}

export function projectBootOutcomeAfterLoad(
  desktopBackend: boolean,
  state: Pick<DesktopStatePayload, "active_project">,
  requestedPath = ""
): ProjectBootOutcome {
  if (!desktopBackend) {
    return { kind: "browser-fallback" };
  }
  if (state.active_project) {
    return { kind: "ready" };
  }
  return {
    kind: "project-required",
    error: "",
    requestedPath: requestedPath.trim()
  };
}

export function projectBootOutcomeAfterFailure(
  desktopBackend: boolean,
  requestedPath: string | undefined,
  error: unknown
): ProjectBootOutcome {
  if (!desktopBackend) {
    return { kind: "browser-fallback" };
  }
  return {
    kind: "project-required",
    error: error instanceof Error ? error.message : String(error),
    requestedPath: requestedPath?.trim() ?? ""
  };
}

export function projectRefreshFailureDisposition(
  desktopBackend: boolean,
  currentState: Pick<DesktopStatePayload, "active_project"> | null,
  requestedPath: string | undefined,
  error: unknown
): ProjectRefreshFailureDisposition {
  const currentProject = currentState?.active_project;
  if (currentProject) {
    const cleanRequestedPath = requestedPath?.trim() ?? "";
    return {
      bootOutcome: projectBootOutcomeAfterLoad(desktopBackend, currentState),
      candidateProject:
        Boolean(cleanRequestedPath) && cleanRequestedPath !== currentProject.root,
      preserveWorkspace: true
    };
  }
  return {
    bootOutcome: projectBootOutcomeAfterFailure(
      desktopBackend,
      requestedPath,
      error
    ),
    candidateProject: false,
    preserveWorkspace: false
  };
}

export function shouldRecoverRememberedProject(
  desktopBackend: boolean,
  currentState: Pick<DesktopStatePayload, "active_project"> | null,
  requestedPath: string | undefined,
  options: DesktopStateRefreshOptions
): boolean {
  return (
    desktopBackend &&
    !currentState?.active_project &&
    Boolean(requestedPath?.trim()) &&
    options.recoverRememberedProject === true &&
    options.throwOnError !== true
  );
}

export async function loadDesktopStateWithRememberedProjectRecovery(
  load: DesktopStateLoad,
  {
    currentState,
    desktopBackend,
    options,
    projectRoot
  }: {
    currentState: Pick<DesktopStatePayload, "active_project"> | null;
    desktopBackend: boolean;
    options: DesktopStateRefreshOptions;
    projectRoot?: string;
  }
): Promise<{
  recovery: RememberedProjectRecovery | null;
  state: DesktopStatePayload;
}> {
  try {
    return {
      recovery: null,
      state: await load(projectRoot)
    };
  } catch (error: unknown) {
    if (
      !shouldRecoverRememberedProject(
        desktopBackend,
        currentState,
        projectRoot,
        options
      )
    ) {
      throw error;
    }
    let state: DesktopStatePayload;
    try {
      state = await load(undefined);
    } catch {
      throw error;
    }
    const recoveredProject = state.active_project;
    if (!recoveredProject) {
      throw error;
    }
    return {
      recovery: {
        error: errorDetail(error),
        recoveredPath: recoveredProject.root,
        recoveredTitle: recoveredProject.title,
        requestedPath: projectRoot?.trim() ?? ""
      },
      state
    };
  }
}

export function rememberedProjectRecoveryMessage(
  recovery: RememberedProjectRecovery | null,
  t: Translator
): string {
  if (!recovery) {
    return "";
  }
  return t("project.rememberedRecovery", {
    project: recovery.recoveredTitle
  });
}

export function rememberedProjectRecoveryDetail(
  recovery: RememberedProjectRecovery | null,
  t: Translator
): string {
  if (!recovery) {
    return "";
  }
  return t("project.rememberedRecoveryDetail", {
    message: localizeDesktopBridgeError(t, recovery.error),
    path: recovery.requestedPath,
    recoveredPath: recovery.recoveredPath
  });
}

export function shouldUseBrowserProjectFallback(outcome: ProjectBootOutcome): boolean {
  return outcome.kind === "browser-fallback";
}

export function isProjectBootWorkspaceBlocked(outcome: ProjectBootOutcome): boolean {
  return outcome.kind === "checking" || outcome.kind === "project-required";
}

export function shouldShowProjectOnboarding(
  outcome: ProjectBootOutcome,
  {
    projectLoading,
    settingsReady
  }: {
    projectLoading: boolean;
    settingsReady: boolean;
  }
): boolean {
  return settingsReady && !projectLoading && outcome.kind === "project-required";
}

export function shouldShowProjectBootLoading(
  outcome: ProjectBootOutcome,
  {
    projectLoading,
    settingsReady
  }: {
    projectLoading: boolean;
    settingsReady: boolean;
  }
): boolean {
  return (
    outcome.kind === "checking" ||
    (outcome.kind === "project-required" && (!settingsReady || projectLoading))
  );
}

export function projectBootRecoveryError(
  outcome: ProjectBootOutcome,
  t: Translator
): string {
  if (outcome.kind !== "project-required") {
    return "";
  }
  const detail = outcome.error
    ? localizeDesktopBridgeError(t, outcome.error)
    : t("project.onboarding.unavailable");
  if (outcome.requestedPath) {
    return t("project.onboarding.recoveryFailed", {
      message: detail,
      path: outcome.requestedPath
    });
  }
  return outcome.error
    ? t("project.onboarding.discoveryFailed", { message: detail })
    : "";
}

export function shouldLoadWorkspaceBrowserScope(activeRail: string): boolean {
  return activeRail === "projects";
}

export async function refreshCompletedBuildProject(
  activeProjectPath: string,
  refreshBuildDiagnostics: BuildDiagnosticsRefresh,
  projectRoot?: string
): Promise<void> {
  if (!projectRoot || projectRoot !== activeProjectPath) {
    return;
  }
  await refreshBuildDiagnostics(projectRoot, "published");
}

export async function refreshProjectForBuildPage(
  refreshDesktopState: DesktopStateRefresh,
  projectRoot?: string,
  fallbackProjectIdentity?: string
): Promise<void> {
  await refreshDesktopState(projectRoot, fallbackProjectIdentity, { throwOnError: true });
}

export function shouldPersistAppSettings(input: { settingsLoadFailed: boolean; settingsReady: boolean }): boolean {
  return input.settingsReady && !input.settingsLoadFailed;
}

export function applyDesktopConfigValuesToConfigPageSettings(settings: ConfigPageSettings, values: Partial<Record<DesktopConfigKey, unknown>>): ConfigPageSettings {
  return normalizeConfigPageSettings(
    {
      ...settings,
      build: {
        ...settings.build,
        parallelism: positiveConfigInteger(values[DESKTOP_CONFIG_KEYS.buildParallelism], settings.build.parallelism),
        strictMetadata: booleanConfig(values[DESKTOP_CONFIG_KEYS.buildStrictMetadata], settings.build.strictMetadata)
      },
      moduleDefaults: configModuleDefaultsWithValue(
        settings.moduleDefaults,
        THUMBNAIL_CACHE_MODULE_DEFAULT_ID,
        positiveConfigInteger(values[DESKTOP_CONFIG_KEYS.thumbnailCacheMaxKb], configModuleDefaultValue(settings, THUMBNAIL_CACHE_MODULE_DEFAULT_ID))
      ),
      cli: {
        ...settings.cli,
        output: cliOutputConfig(values[DESKTOP_CONFIG_KEYS.cliOutput], settings.cli.output)
      },
      project: {
        ...settings.project,
        name: aiTextConfig(values[DESKTOP_CONFIG_KEYS.projectName], settings.project.name)
      },
      hoi4: {
        ...settings.hoi4,
        gameRoot: optionalConfigText(values[DESKTOP_CONFIG_KEYS.hoi4GameRoot], settings.hoi4.gameRoot),
        launchMode: hoi4LaunchModeConfig(values[DESKTOP_CONFIG_KEYS.hoi4LaunchMode], settings.hoi4.launchMode)
      },
      chat: {
        ...settings.chat,
        defaultRole: aiChatRoleConfig(values[DESKTOP_CONFIG_KEYS.aiChatDefaultRole], settings.chat.defaultRole)
      },
      llm: {
        ...settings.llm,
        baseUrl: optionalConfigText(values[DESKTOP_CONFIG_KEYS.aiBaseUrl], settings.llm.baseUrl),
        gateway: aiTextConfig(values[DESKTOP_CONFIG_KEYS.aiGateway], settings.llm.gateway),
        keyEnv: aiTextConfig(values[DESKTOP_CONFIG_KEYS.aiKeyEnv], settings.llm.keyEnv),
        model: aiTextConfig(values[DESKTOP_CONFIG_KEYS.aiModel], settings.llm.model),
        preset: aiPresetConfig(values[DESKTOP_CONFIG_KEYS.aiPreset], settings.llm.preset),
        provider: aiTextConfig(values[DESKTOP_CONFIG_KEYS.aiProvider], settings.llm.provider)
      }
    },
    settings
  );
}

export function desktopConfigWritesForSettingsChange(previous: ConfigPageSettings, next: ConfigPageSettings): DesktopConfigWrite[] {
  const writes: DesktopConfigWrite[] = [];
  if (next.project.name !== previous.project.name) {
    writes.push([DESKTOP_CONFIG_KEYS.projectName, next.project.name]);
  }
  if (next.build.parallelism !== previous.build.parallelism) {
    writes.push([DESKTOP_CONFIG_KEYS.buildParallelism, next.build.parallelism]);
  }
  if (next.build.strictMetadata !== previous.build.strictMetadata) {
    writes.push([DESKTOP_CONFIG_KEYS.buildStrictMetadata, next.build.strictMetadata]);
  }
  if (configModuleDefaultValue(next, THUMBNAIL_CACHE_MODULE_DEFAULT_ID) !== configModuleDefaultValue(previous, THUMBNAIL_CACHE_MODULE_DEFAULT_ID)) {
    writes.push([DESKTOP_CONFIG_KEYS.thumbnailCacheMaxKb, configModuleDefaultValue(next, THUMBNAIL_CACHE_MODULE_DEFAULT_ID)]);
  }
  if (next.cli.output !== previous.cli.output) {
    writes.push([DESKTOP_CONFIG_KEYS.cliOutput, next.cli.output]);
  }
  if (next.hoi4.gameRoot !== previous.hoi4.gameRoot) {
    writes.push([DESKTOP_CONFIG_KEYS.hoi4GameRoot, next.hoi4.gameRoot]);
  }
  if (next.hoi4.launchMode !== previous.hoi4.launchMode) {
    writes.push([DESKTOP_CONFIG_KEYS.hoi4LaunchMode, next.hoi4.launchMode]);
  }
  if (next.llm.preset !== previous.llm.preset) {
    writes.push([DESKTOP_CONFIG_KEYS.aiPreset, next.llm.preset]);
  }
  if (next.llm.provider !== previous.llm.provider) {
    writes.push([DESKTOP_CONFIG_KEYS.aiProvider, next.llm.provider]);
  }
  if (next.llm.gateway !== previous.llm.gateway) {
    writes.push([DESKTOP_CONFIG_KEYS.aiGateway, next.llm.gateway]);
  }
  if (next.llm.model !== previous.llm.model) {
    writes.push([DESKTOP_CONFIG_KEYS.aiModel, next.llm.model]);
  }
  if (next.llm.keyEnv !== previous.llm.keyEnv) {
    writes.push([DESKTOP_CONFIG_KEYS.aiKeyEnv, next.llm.keyEnv]);
  }
  if (next.llm.baseUrl !== previous.llm.baseUrl) {
    writes.push([DESKTOP_CONFIG_KEYS.aiBaseUrl, next.llm.baseUrl]);
  }
  if (next.chat.defaultRole !== previous.chat.defaultRole) {
    writes.push([DESKTOP_CONFIG_KEYS.aiChatDefaultRole, next.chat.defaultRole]);
  }
  return writes;
}

export function configPersistenceSavingStatus(): ConfigPersistenceStatus {
  return {
    labelKey: "config.page.saving",
    state: "saving"
  };
}

export function configPersistenceFailureStatus(subject: string, error: unknown, t?: Translator): ConfigPersistenceStatus {
  return {
    detail: `${subject}: ${errorDetail(error, t)}`,
    labelKey: "config.page.saveFailed",
    state: "error"
  };
}

export function configPersistenceLoadFailureStatus(subject: string, error: unknown, t?: Translator): ConfigPersistenceStatus {
  return {
    detail: `${subject}: ${errorDetail(error, t)}`,
    labelKey: "config.page.loadFailed",
    state: "error"
  };
}

export function aiChatReplyText(response: Pick<ParaDevAiChatPayload, "detail" | "reply" | "status">, t: Translator): string {
  if (response.status === "error") {
    throw new Error(response.detail || response.reply || t("chat.routeError"));
  }
  return response.reply || response.detail || "";
}

/**
 * Rejects an AI batch review when opening it would replace active authoring.
 *
 * Dirty drafts retain their existing, more specific error. A pristine but
 * still-open dialog is also protected because silently replacing the visible
 * planner would discard the user's current context.
 */
export function assertAiChatModuleBatchReviewAvailable({
  editorSessionStore,
  sessionKey,
  t
}: {
  editorSessionStore: ModuleEditorSessionStore;
  sessionKey: ModuleEditorSessionKey;
  t: Translator;
}): void {
  const session = editorSessionStore
    .getSnapshot()
    .sessions.find((candidate) => candidate.key === sessionKey);
  if (session?.batchCreateDirty) {
    throw new Error(t("chat.proposal.moduleBatch.draftExists"));
  }
  if (editorSessionStore.read(sessionKey)?.batchCreate?.open) {
    throw new Error(t("chat.proposal.moduleBatch.dialogOpen"));
  }
}

/** Rejects a collection review when it would replace retained authoring. */
export function assertAiChatCollectionReviewAvailable({
  editorSessionStore,
  sessionKey,
  t
}: {
  editorSessionStore: ModuleEditorSessionStore;
  sessionKey: ModuleEditorSessionKey;
  t: Translator;
}): void {
  const session = editorSessionStore
    .getSnapshot()
    .sessions.find((candidate) => candidate.key === sessionKey);
  if (session?.collectionCreateDirty) {
    throw new Error(t("chat.proposal.collection.draftExists"));
  }
  if (editorSessionStore.read(sessionKey)?.collectionCreate?.open) {
    throw new Error(t("chat.proposal.collection.dialogOpen"));
  }
}

/** Rejects a Guided source review when it would replace retained authoring. */
export function assertAiChatSourceUpdateReviewAvailable({
  editorSessionStore,
  sessionKey,
  t
}: {
  editorSessionStore: ModuleEditorSessionStore;
  sessionKey: ModuleEditorSessionKey;
  t: Translator;
}): void {
  if (editorSessionStore.read(sessionKey)?.sourceUpdate) {
    throw new Error(t("chat.proposal.sourceUpdate.dialogOpen"));
  }
  const session = editorSessionStore
    .getSnapshot()
    .sessions.find((candidate) => candidate.key === sessionKey);
  if (session?.dirty || session?.busy) {
    throw new Error(t("chat.proposal.sourceUpdate.draftExists"));
  }
}

function formatBootCount(value: number): string {
  const clean = Math.max(0, Math.floor(Number.isFinite(value) ? value : 0));
  return String(clean).replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}

export function workspaceTabIdForModuleSelection(moduleId: string): string {
  return moduleId;
}

export function moduleEditorSessionKeyForWorkspaceTab(
  projectRoot: string,
  tab: Pick<WorkspaceTab, "familyId" | "id" | "kind">
): ModuleEditorSessionKey | null {
  const root = projectRoot.trim();
  if (!root || (tab.kind !== "module" && tab.kind !== "diagram")) {
    return null;
  }
  const familyId =
    tab.kind === "diagram"
      ? tab.familyId ?? moduleIdForDiagramTabId(tab.id)
      : tab.familyId ?? tab.id;
  return moduleEditorSessionKey(root, familyId);
}

export function moduleEditorSessionKeyRequiringClosePrompt(
  projectRoot: string,
  tabId: string,
  openTabs: readonly WorkspaceTab[],
  snapshot: ModuleEditorSessionStoreSnapshot
): ModuleEditorSessionKey | null {
  const tab = openTabs.find((row) => row.id === tabId);
  const key = tab
    ? moduleEditorSessionKeyForWorkspaceTab(projectRoot, tab)
    : null;
  if (!key) {
    return null;
  }
  const siblingOpen = openTabs.some(
    (row) =>
      row.id !== tabId &&
      moduleEditorSessionKeyForWorkspaceTab(projectRoot, row) === key
  );
  if (siblingOpen) {
    return null;
  }
  const session = snapshot.sessions.find((row) => row.key === key);
  return session && (session.dirty || session.busy) ? key : null;
}

export function isWorkspaceProjectModelReady(
  project: Pick<ProjectOption, "path" | "projectId">,
  browser: ProjectBrowserPayload | null,
  templates: ProjectTemplatesPayload | null
): boolean {
  return (
    browser?.root === project.path &&
    browser.project_id === project.projectId &&
    templates?.project_id === project.projectId
  );
}

export function nextOpenTabEntriesForOpen(entries: OpenTabEntry[], nextTab: WorkspaceTab, options: { pinned?: boolean } = {}): OpenTabEntry[] {
  const pinned = Boolean(options.pinned);
  const cachedTab = cachedWorkspaceTab(nextTab);
  const existing = entries.find((entry) => entry.id === nextTab.id);
  if (existing) {
    return entries.map((entry) =>
      entry.id === nextTab.id
        ? { ...entry, pinned: entry.pinned || pinned, tab: cachedTab }
        : entry
    );
  }
  if (pinned) {
    return [...entries, { id: nextTab.id, pinned: true, tab: cachedTab }];
  }
  const previewGroup = workspacePreviewGroupForTab(nextTab);
  const previewIndex = entries.findIndex((entry) => !entry.pinned && workspacePreviewGroupForTabId(entry.id) === previewGroup);
  if (previewIndex === -1) {
    return [...entries, { id: nextTab.id, pinned: false, tab: cachedTab }];
  }
  return entries.map((entry, index) =>
    index === previewIndex
      ? { id: nextTab.id, pinned: false, tab: cachedTab }
      : entry
  );
}

export type OpenTabCleanupFailure = Readonly<{
  error: unknown;
  key: ModuleEditorSessionKey;
  tabId: string;
}>;

/**
 * Reconciles open tabs with a refreshed SDK model without orphaning work.
 *
 * Current entries keep their cached tab identity through transient model
 * omissions and rebind when the SDK row returns. Cacheless legacy entries
 * still clean up orphaned sessions before they are removed.
 */
export function reconcileOpenTabEntries(
  projectRoot: string,
  entries: OpenTabEntry[],
  workspaceTabs: readonly WorkspaceTab[],
  store: ModuleEditorSessionStore
): Readonly<{
  cleanupFailure: OpenTabCleanupFailure | null;
  entries: OpenTabEntry[];
}> {
  const currentTabs = new Map(workspaceTabs.map((tab) => [tab.id, tab]));
  const snapshot = store.getSnapshot();
  const nextEntries: OpenTabEntry[] = [];
  const cleanupOutcomes = new Map<
    ModuleEditorSessionKey,
    "discarded" | "failed"
  >();
  let cleanupFailure: OpenTabCleanupFailure | null = null;
  let changed = false;

  for (const entry of entries) {
    const currentTab = currentTabs.get(entry.id);
    if (currentTab) {
      const cachedTab = cachedWorkspaceTab(currentTab);
      if (sameCachedWorkspaceTab(entry.tab, cachedTab)) {
        nextEntries.push(entry);
      } else {
        nextEntries.push({ ...entry, tab: cachedTab });
        changed = true;
      }
      continue;
    }

    if (entry.tab) {
      nextEntries.push(entry);
      continue;
    }

    const tab = moduleEditorWorkspaceTabForEntryId(entry.id);
    if (!tab) {
      changed = true;
      continue;
    }
    const key = moduleEditorSessionKeyForWorkspaceTab(projectRoot, tab);
    const summary = key
      ? snapshot.sessions.find((session) => session.key === key)
      : undefined;
    if (summary?.dirty || summary?.busy) {
      nextEntries.push({ ...entry, tab: cachedWorkspaceTab(tab) });
      changed = true;
      continue;
    }

    const cleanupOutcome = key ? cleanupOutcomes.get(key) : undefined;
    if (cleanupOutcome === "failed") {
      nextEntries.push({ ...entry, tab: cachedWorkspaceTab(tab) });
      changed = true;
      continue;
    }
    if (cleanupOutcome === "discarded") {
      changed = true;
      continue;
    }

    if (key && store.read(key)) {
      try {
        store.discard(key);
      } catch (error: unknown) {
        cleanupOutcomes.set(key, "failed");
        nextEntries.push({ ...entry, tab: cachedWorkspaceTab(tab) });
        changed = true;
        cleanupFailure ??= { error, key, tabId: entry.id };
        continue;
      }
    }
    if (key) {
      cleanupOutcomes.set(key, "discarded");
    }
    changed = true;
  }

  return {
    cleanupFailure,
    entries: changed ? nextEntries : entries
  };
}

function cachedWorkspaceTab(
  tab: WorkspaceTab
): Omit<WorkspaceTab, "dirty" | "pinned"> {
  const {
    dirty: _dirty,
    pinned: _pinned,
    ...cached
  } = tab;
  return cached;
}

function sameCachedWorkspaceTab(
  left: Omit<WorkspaceTab, "dirty" | "pinned"> | undefined,
  right: Omit<WorkspaceTab, "dirty" | "pinned">
): boolean {
  return Boolean(
    left &&
      left.id === right.id &&
      left.kind === right.kind &&
      left.familyId === right.familyId &&
      left.titleKey === right.titleKey &&
      left.title === right.title &&
      left.subtitleKey === right.subtitleKey
  );
}

function retainedWorkspaceTabForEntry(
  projectRoot: string,
  tabId: string,
  snapshot: ModuleEditorSessionStoreSnapshot
): Omit<WorkspaceTab, "dirty" | "pinned"> | null {
  const tab = moduleEditorWorkspaceTabForEntryId(tabId);
  if (!tab) {
    return null;
  }
  const key = moduleEditorSessionKeyForWorkspaceTab(projectRoot, tab);
  return key && snapshot.sessions.some((session) => session.key === key)
    ? tab
    : null;
}

function moduleEditorWorkspaceTabForEntryId(
  tabId: string
): Omit<WorkspaceTab, "dirty" | "pinned"> | null {
  const diagram = isDiagramTabId(tabId);
  const familyId = canonicalFamilyId(moduleIdForDiagramTabId(tabId));
  if (!familyId) {
    return null;
  }
  const tab: Omit<WorkspaceTab, "dirty" | "pinned"> = {
    id: tabId,
    ...(diagram ? { familyId } : {}),
    title: familyId,
    kind: diagram ? "diagram" : "module"
  };
  return tab;
}

export function shouldCompleteAuthoringCloseIntent(
  intent: AuthoringCloseIntent | null,
  snapshot: ModuleEditorSessionStoreSnapshot
): boolean {
  if (!intent || intent.kind === "busy" || intent.error) {
    return false;
  }
  const session = snapshot.sessions.find((row) => row.key === intent.key);
  return !session || (!session.busy && !session.dirty);
}

export function tabsForModules(modules: FeatureModule[]): WorkspaceTab[] {
  const moduleTabs = modules.map<WorkspaceTab>((module) => ({
    id: module.id,
    ...(module.titleKey ? { titleKey: module.titleKey } : {}),
    ...(module.label ? { title: module.label } : {}),
    kind: "module"
  }));
  const diagramTabs = modules.filter((module) => Boolean(module.diagram)).map<WorkspaceTab>((module) => ({
    id: diagramTabIdForModule(module.id),
    familyId: module.id,
    kind: "diagram"
  }));
  const configTabs = baseWorkspaceTabs.filter((tab) => tab.kind === "config");
  return [...moduleTabs, ...diagramTabs, ...configTabs];
}

export default function App() {
  const [editorSessionStore] = useState(() => new ModuleEditorSessionStore());
  const [desktopBackend] = useState(() => hasDesktopBackend());
  const subscribeToEditorSessions = useCallback(
    (listener: () => void) => editorSessionStore.subscribe(listener),
    [editorSessionStore]
  );
  const editorSessionSnapshot = useSyncExternalStore(
    subscribeToEditorSessions,
    () => editorSessionStore.getSnapshot(),
    () => editorSessionStore.getSnapshot()
  );
  const [openPathPlatform] = useState<OpenPathPlatform>(() => currentOpenPathPlatform());
  const initialSettings = useMemo(() => readInitialAppSettings(fallbackProjectOptions[0].id, openPathPlatform), [openPathPlatform]);
  const [settingsReady, setSettingsReady] = useState(false);
  const [settingsLoadFailed, setSettingsLoadFailed] = useState(false);
  const [theme, setTheme] = useState<ThemeName>(initialSettings.theme);
  const [locale, setLocale] = useState<Locale>(initialSettings.locale);
  const [configPageSettings, setConfigPageSettings] = useState<ConfigPageSettings>(initialSettings.configPage);
  const [activeRail, setActiveRail] = useState(defaultRailId);
  const [activeModule, setActiveModule] = useState(baseFeatureModules[0].id);
  const [activeConfig, setActiveConfig] = useState(configOptions[0].id);
  const [activeProjectIdentity, setActiveProjectIdentity] = useState(fallbackProjectOptions[0].id);
  const [activeProjectPath, setActiveProjectPath] = useState(initialSettings.activeProjectPath);
  const [desktopState, setDesktopState] = useState<DesktopStatePayload | null>(null);
  const [projectBootOutcome, setProjectBootOutcome] = useState<ProjectBootOutcome>(
    () => initialProjectBootOutcome(desktopBackend)
  );
  const [buildDiagnosticsRefreshByProjectRoot, setBuildDiagnosticsRefreshByProjectRoot] = useState<
    Record<string, BuildDiagnosticsRefreshState>
  >({});
  const [scopedBrowserByKey, setScopedBrowserByKey] = useState<Record<string, ProjectBrowserPayload>>({});
  const [scopedBrowserLoadingByKey, setScopedBrowserLoadingByKey] = useState<Record<string, boolean>>({});
  const [scopedBrowserErrorByKey, setScopedBrowserErrorByKey] = useState<Record<string, string>>({});
  const [pathStatusByPath, setPathStatusByPath] = useState<Record<string, DesktopPathStatusPayload>>({});
  const [pathStatusErrorByPath, setPathStatusErrorByPath] = useState<Record<string, string>>({});
  const [moduleOrderByProject, setModuleOrderByProject] = useState<Record<string, string[]>>(initialSettings.moduleOrderByProject);
  const [moduleDefaultsByProject, setModuleDefaultsByProject] = useState<ModuleDefaultsByProject>(initialSettings.moduleDefaultsByProject);
  const [moduleOrder, setModuleOrder] = useState<string[]>(initialSettings.moduleOrderByProject[fallbackProjectOptions[0].id] ?? []);
  const [openTarget, setOpenTarget] = useState<OpenPathTarget>(initialSettings.openTarget);
  const [projectLoading, setProjectLoading] = useState(true);
  const [projectError, setProjectError] = useState("");
  const [projectOpenError, setProjectOpenError] = useState("");
  const [projectLanguageBusy, setProjectLanguageBusy] = useState(false);
  const [projectLanguageError, setProjectLanguageError] = useState("");
  const [rememberedProjectRecovery, setRememberedProjectRecovery] =
    useState<RememberedProjectRecovery | null>(null);
  const [projectImporting, setProjectImporting] = useState(false);
  const [projectOpening, setProjectOpening] = useState(false);
  const [openTabEntries, setOpenTabEntries] = useState<OpenTabEntry[]>([]);
  const [authoringCloseIntent, setAuthoringCloseIntent] = useState<AuthoringCloseIntent | null>(null);
  const [moduleSelectionTarget, setModuleSelectionTarget] = useState<WorkspaceModuleSelectionTarget | null>(null);
  const [moduleCreateIntent, setModuleCreateIntent] = useState<ModuleCreateIntent | null>(null);
  const [buildAiOperationIntent, setBuildAiOperationIntent] = useState<AiOperationIntent | null>(null);
  const [buildTargetIntent, setBuildTargetIntent] = useState<BuildTargetIntent | null>(null);
  const [activeTab, setActiveTab] = useState("");
  const [secondaryTab, setSecondaryTab] = useState("");
  const [splitView, setSplitView] = useState(false);
  const [inspectorOpen, setInspectorOpen] = useState(initialSettings.sidebars.inspectorOpen);
  const [projectPanelOpen, setProjectPanelOpen] = useState(initialSettings.sidebars.projectPanelOpen);
  const [dependencyStatusById, setDependencyStatusById] = useState<Record<string, ConfigDependencyStatus>>({});
  const [dependencyBusyId, setDependencyBusyId] = useState("");
  const [llmStatus, setLlmStatus] = useState<ConfigLlmStatus | null>(defaultConfigLlmStatus(initialSettings.configPage.llm));
  const [configPersistenceStatus, setConfigPersistenceStatus] = useState<ConfigPersistenceStatus>(() => defaultConfigPersistenceStatus());
  const [aiChatDock, setAiChatDock] = useState<AiChatDock>(initialSettings.chat.dock);
  const [aiChatOpen, setAiChatOpen] = useState(initialSettings.chat.open);
  const [aiChatDefaultRole, setAiChatDefaultRole] = useState("chat");
  const [aiChatProfileLoadError, setAiChatProfileLoadError] = useState<string | null>(null);
  const [aiChatProfiles, setAiChatProfiles] = useState<ParaDevAiChatProfile[]>([]);
  const [aiChatSourceKindRows, setAiChatSourceKindRows] = useState<ParaDevAiChatSourceKindRow[]>([]);
  const [aiChatSourceKinds, setAiChatSourceKinds] = useState<string[]>([]);
  const [searchQuery, setSearchQuery] = useState("");
  const activeProjectIdRef = useRef(
    desktopBackend ? "" : fallbackProjectOptions[0].projectId
  );
  const activeProjectRootRef = useRef(
    initialSettings.activeProjectPath ||
      (desktopBackend ? "" : fallbackProjectOptions[0].path)
  );
  const latestProjectRefreshRef = useRef(0);
  const desktopStateRef = useRef<DesktopStatePayload | null>(null);
  const lastSavedSettingsRef = useRef("");
  const moduleCreateIntentNonceRef = useRef(0);
  const aiOperationIntentNonceRef = useRef(0);
  const buildTargetIntentNonceRef = useRef(0);
  const scopedBrowserRequestsRef = useRef(new Map<string, number>());
  const scopedBrowserResolvedKeysRef = useRef(new Set<string>());
  const sourceBrowserFallbackChecksRef = useRef(new Set<string>());
  const workspaceViewByProjectRef = useRef(new Map<string, WorkspaceViewState>());
  const workspaceViewProjectRootRef = useRef(
    desktopBackend ? "" : fallbackProjectOptions[0].path
  );
  const latestWorkspaceViewRef = useRef<WorkspaceViewState>({
    activeModule,
    activeTab,
    moduleSelectionTarget,
    openTabEntries,
    secondaryTab,
    splitView
  });
  latestWorkspaceViewRef.current = {
    activeModule,
    activeTab,
    moduleSelectionTarget,
    openTabEntries,
    secondaryTab,
    splitView
  };

  const t = useMemo(() => createTranslator(locale), [locale]);
  const loadedTemplates = desktopState?.templates ?? null;
  const projectOptions = useMemo(() => {
    if (isProjectBootWorkspaceBlocked(projectBootOutcome)) {
      return [];
    }
    const rows = desktopState?.projects ?? [];
    if (rows.length > 0) {
      return projectRowsToOptions(rows);
    }
    return shouldUseBrowserProjectFallback(projectBootOutcome)
      ? fallbackProjectOptions
      : [];
  }, [desktopState, projectBootOutcome]);
  const showProjectOnboarding = shouldShowProjectOnboarding(projectBootOutcome, {
    projectLoading,
    settingsReady
  });
  const showProjectBootLoading = shouldShowProjectBootLoading(
    projectBootOutcome,
    {
      projectLoading,
      settingsReady
    }
  );
  const projectWorkspaceBlocked = isProjectBootWorkspaceBlocked(
    projectBootOutcome
  );
  const activeProjectOption = useMemo(
    () =>
      projectOptions.find((project) => project.id === activeProjectIdentity) ??
      projectOptions[0] ??
      EMPTY_PROJECT_OPTION,
    [activeProjectIdentity, projectOptions]
  );
  useEffect(() => {
    setProjectLanguageError("");
  }, [activeProjectOption.path]);
  const templates =
    (desktopState?.active_project?.root ?? desktopState?.browser?.root) ===
    activeProjectOption.path
      ? loadedTemplates
      : null;
  const browser = useMemo(
    () => mergeProjectBrowserPayloadsForProject(activeProjectOption.path, desktopState?.browser ?? null, ...Object.values(scopedBrowserByKey)),
    [activeProjectOption.path, desktopState?.browser, scopedBrowserByKey]
  );
  const projectModules = useMemo(() => modulesForProjectState(browser, templates, baseFeatureModules), [browser, templates]);
  const featureModules = useMemo(() => applyModuleOrder(projectModules, moduleOrder), [moduleOrder, projectModules]);
  const workspaceTabs = useMemo(() => tabsForModules(featureModules), [featureModules]);
  const visibleFeatureModules = useMemo(() => filterPanelOptions(featureModules, searchQuery, t), [featureModules, searchQuery, t]);
  const visibleConfigOptions = useMemo(() => filterPanelOptions(configOptions, searchQuery, t), [searchQuery, t]);
  const activeFeature = useMemo(() => featureModules.find((module) => module.id === activeModule) ?? featureModules[0], [activeModule, featureModules]);
  const configPathStatusPaths = useMemo(
    () =>
      projectWorkspaceBlocked
        ? []
        : configProjectStatusPaths(
            activeProjectOption,
            configPageSettings.hoi4.gameRoot
          ),
    [
      activeProjectOption,
      configPageSettings.hoi4.gameRoot,
      projectWorkspaceBlocked
    ]
  );
  const openTabIds = useMemo(() => openTabEntries.map((entry) => entry.id), [openTabEntries]);
  const editorSessionSummaryByKey = useMemo(
    () => new Map(editorSessionSnapshot.sessions.map((session) => [session.key, session])),
    [editorSessionSnapshot]
  );
  const openTabs = useMemo(
    () =>
      openTabEntries.flatMap((entry) => {
        const tab =
          workspaceTabs.find((workspaceTab) => workspaceTab.id === entry.id) ??
          entry.tab ??
          retainedWorkspaceTabForEntry(
            activeProjectOption.path,
            entry.id,
            editorSessionSnapshot
          );
        if (!tab) {
          return [];
        }
        const sessionKey = moduleEditorSessionKeyForWorkspaceTab(activeProjectOption.path, tab);
        return [
          {
            ...tab,
            dirty: sessionKey
              ? editorSessionSummaryByKey.get(sessionKey)?.dirty ?? false
              : false,
            pinned: entry.pinned
          }
        ];
      }),
    [
      activeProjectOption.path,
      editorSessionSnapshot,
      editorSessionSummaryByKey,
      openTabEntries,
      workspaceTabs
    ]
  );
  const activeWorkspaceTab = useMemo(() => openTabs.find((tab) => tab.id === activeTab) ?? openTabs[0] ?? null, [activeTab, openTabs]);
  const secondaryWorkspaceTab = useMemo(() => {
    if (!activeWorkspaceTab) {
      return null;
    }

    return openTabs.find((tab) => tab.id === secondaryTab && tab.id !== activeWorkspaceTab.id) ?? openTabs.find((tab) => tab.id !== activeWorkspaceTab.id) ?? null;
  }, [activeWorkspaceTab, openTabs, secondaryTab]);
  const activeBrowserLoading = useMemo(() => isWorkspaceTabBrowserLoading(activeWorkspaceTab, activeProjectOption.path, scopedBrowserLoadingByKey, browser), [activeProjectOption.path, activeWorkspaceTab, browser, scopedBrowserLoadingByKey]);
  const activeBrowserError = useMemo(() => scopedBrowserErrorForWorkspaceTab(activeWorkspaceTab, activeProjectOption.path, scopedBrowserErrorByKey, browser), [activeProjectOption.path, activeWorkspaceTab, browser, scopedBrowserErrorByKey]);
  const secondaryBrowserLoading = useMemo(
    () => (splitView ? isWorkspaceTabBrowserLoading(secondaryWorkspaceTab, activeProjectOption.path, scopedBrowserLoadingByKey, browser) : false),
    [activeProjectOption.path, browser, scopedBrowserLoadingByKey, secondaryWorkspaceTab, splitView]
  );
  const secondaryBrowserError = useMemo(
    () => (splitView ? scopedBrowserErrorForWorkspaceTab(secondaryWorkspaceTab, activeProjectOption.path, scopedBrowserErrorByKey, browser) : null),
    [activeProjectOption.path, browser, scopedBrowserErrorByKey, secondaryWorkspaceTab, splitView]
  );
  const aiChatSources = useMemo(
    () => aiChatSourcesForWorkspace(activeWorkspaceTab, moduleSelectionTarget, browser, t, templates),
    [activeWorkspaceTab, browser, moduleSelectionTarget, t, templates]
  );
  const localizedProjectError = useMemo(() => localizeDesktopBridgeError(t, projectError), [projectError, t]);
  const localizedRememberedProjectRecovery = useMemo(
    () => rememberedProjectRecoveryMessage(rememberedProjectRecovery, t),
    [rememberedProjectRecovery, t]
  );
  const localizedRememberedProjectRecoveryDetail = useMemo(
    () => rememberedProjectRecoveryDetail(rememberedProjectRecovery, t),
    [rememberedProjectRecovery, t]
  );
  const projectRecoveryError = useMemo(
    () => projectBootRecoveryError(projectBootOutcome, t),
    [projectBootOutcome, t]
  );
  const appSettings = useMemo<AppSettingsPayload>(
    () => ({
      schema: APP_SETTINGS_SCHEMA,
      activeProjectId: activeProjectOption.projectId,
      activeProjectPath,
      chat: {
        dock: aiChatDock,
        open: aiChatOpen
      },
      configPage: configPageSettings,
      theme,
      locale,
      openTarget,
      sidebars: {
        projectPanelOpen,
        inspectorOpen
      },
      moduleOrderByProject,
      moduleDefaultsByProject
    }),
    [activeProjectOption.projectId, activeProjectPath, aiChatDock, aiChatOpen, configPageSettings, inspectorOpen, locale, moduleDefaultsByProject, moduleOrderByProject, openTarget, projectPanelOpen, theme]
  );
  const persistableAppSettings = useMemo(() => persistableAppSettingsPayload(appSettings), [appSettings]);
  const bootProgress = useMemo<BootProgressState | null>(
    () =>
      appBootProgress({
        activeProjectName: activeProjectOption.name,
        browserItemCount: browser?.items.length,
        desktopStateLoaded: desktopState !== null,
        diagnosticCount: desktopState?.diagnostics.length,
        openTarget,
        projectError: localizedProjectError,
        projectLoading,
        projectOpening,
        settingsReady,
        templateCount: templates?.templates.length,
        t
      }),
    [activeProjectOption.name, browser?.items.length, desktopState, localizedProjectError, openTarget, projectLoading, projectOpening, settingsReady, t, templates?.templates.length]
  );

  useEffect(() => {
    applyDocumentLocale(document, locale);
  }, [locale]);

  const refreshDesktopState = useCallback(async (
    projectRoot?: string,
    fallbackProjectIdentity = fallbackProjectOptions[0].id,
    options: DesktopStateRefreshOptions = {}
  ) => {
    const requestId = latestProjectRefreshRef.current + 1;
    latestProjectRefreshRef.current = requestId;
    let refreshedProjectRoot = "";
    setProjectLoading(true);
    try {
      const loaded = await loadDesktopStateWithRememberedProjectRecovery(
        (requestedProjectRoot) =>
          loadDesktopState(requestedProjectRoot, { includeBrowser: false }),
        {
          currentState: desktopStateRef.current,
          desktopBackend,
          options,
          projectRoot
        }
      );
      const { recovery, state } = loaded;
      if (!shouldCommitProjectRefresh(requestId, latestProjectRefreshRef.current)) {
        return;
      }
      const activeProjectRoot = state.active_project?.root ?? projectRoot ?? "";
      refreshedProjectRoot = activeProjectRoot;
      setActiveProjectPath(activeProjectRoot);
      const cachedBrowser = activeProjectRoot && shouldUseCachedProjectBrowserForRefresh(projectRoot) ? await readCachedProjectBrowser(activeProjectRoot) : null;
      if (!shouldCommitProjectRefresh(requestId, latestProjectRefreshRef.current)) {
        return;
      }
      const baseBrowser = projectBrowserBaseForRefresh(activeProjectRoot, cachedBrowser, desktopStateRef.current);
      scopedBrowserRequestsRef.current.clear();
      scopedBrowserResolvedKeysRef.current.clear();
      sourceBrowserFallbackChecksRef.current.clear();
      setScopedBrowserByKey({});
      setScopedBrowserLoadingByKey({});
      setScopedBrowserErrorByKey({});
      const stateWithBrowser = { ...state, browser: baseBrowser };
      desktopStateRef.current = stateWithBrowser;
      setDesktopState(stateWithBrowser);
      setProjectBootOutcome(
        projectBootOutcomeAfterLoad(desktopBackend, state, projectRoot)
      );
      setRememberedProjectRecovery(recovery);
      setActiveProjectIdentity(state.active_project?.root ?? fallbackProjectIdentity);
      setProjectError("");
      if (!activeProjectRoot || !hasDesktopBackend()) {
        return;
      }
      try {
        const browserPayload = await loadProjectBrowser({ projectRoot: activeProjectRoot, summary: true });
        if (!shouldCommitProjectRefresh(requestId, latestProjectRefreshRef.current)) {
          return;
        }
        if (!isUnfilteredProjectBrowserPayload(browserPayload)) {
          throw new Error("Project browser summary response must be unfiltered.");
        }
        await writeCachedProjectBrowser(browserPayload);
        if (!shouldCommitProjectRefresh(requestId, latestProjectRefreshRef.current)) {
          return;
        }
        const current = desktopStateRef.current;
        if (current?.active_project?.root === activeProjectRoot) {
          const next = { ...current, browser: browserPayload };
          desktopStateRef.current = next;
          setDesktopState(next);
        }
      } catch (error: unknown) {
        if (!shouldCommitProjectRefresh(requestId, latestProjectRefreshRef.current)) {
          return;
        }
        setProjectError(error instanceof Error ? error.message : String(error));
        if (options.throwOnError) {
          throw error;
        }
      }
    } catch (error: unknown) {
      if (!shouldCommitProjectRefresh(requestId, latestProjectRefreshRef.current)) {
        return;
      }
      const message = error instanceof Error ? error.message : String(error);
      const failure = projectRefreshFailureDisposition(
        desktopBackend,
        desktopStateRef.current,
        projectRoot,
        error
      );
      setProjectBootOutcome(failure.bootOutcome);
      if (!failure.preserveWorkspace) {
        setProjectError(message);
      } else if (!options.throwOnError) {
        if (failure.candidateProject) {
          setProjectOpenError(message);
        } else {
          setProjectError(message);
        }
      }
      if (options.throwOnError) {
        throw error;
      }
    } finally {
      if (shouldCommitProjectRefresh(requestId, latestProjectRefreshRef.current)) {
        setProjectLoading(false);
        if (refreshedProjectRoot) {
          setBuildDiagnosticsRefreshByProjectRoot((current) => ({
            ...current,
            [refreshedProjectRoot]: {
              generation: (current[refreshedProjectRoot]?.generation ?? 0) + 1,
              source: "live"
            }
          }));
        }
      }
    }
  }, [desktopBackend]);

  const refreshBuildDiagnostics = useCallback(async (
    projectRoot: string,
    source: BuildDiagnosticsRefreshSource
  ) => {
    setBuildDiagnosticsRefreshByProjectRoot((current) => ({
      ...current,
      [projectRoot]: {
        generation: (current[projectRoot]?.generation ?? 0) + 1,
        source
      }
    }));
  }, []);

  const refreshVisibleCompletedBuildProject = useCallback(
    async (projectRoot?: string) =>
      refreshCompletedBuildProject(activeProjectOption.path, refreshBuildDiagnostics, projectRoot),
    [activeProjectOption.path, refreshBuildDiagnostics]
  );

  const refreshBuildPageProject = useCallback(
    async (projectRoot?: string, fallbackProjectIdentity?: string) =>
      refreshProjectForBuildPage(refreshDesktopState, projectRoot, fallbackProjectIdentity),
    [refreshDesktopState]
  );

  const buildLifecycle = useBuildRunLifecycle({
    onProjectRefresh: refreshVisibleCompletedBuildProject,
    projects: projectOptions
  });

  useEffect(() => {
    void refreshDesktopState(
      initialSettings.activeProjectPath || undefined,
      undefined,
      { recoverRememberedProject: true }
    );
  }, [initialSettings.activeProjectPath, refreshDesktopState]);

  useEffect(() => {
    activeProjectIdRef.current = activeProjectOption.projectId;
    activeProjectRootRef.current = activeProjectPath || activeProjectOption.path;
    setConfigPageSettings((current) => configPageSettingsForProjectModuleDefaults(current, moduleDefaultsByProject, activeProjectOption.projectId));
    setModuleOrder(moduleOrderByProject[activeProjectOption.projectId] ?? []);
    setProjectOpenError("");
  }, [activeProjectOption.path, activeProjectOption.projectId, activeProjectPath, moduleDefaultsByProject, moduleOrderByProject]);

  useEffect(() => {
    let cancelled = false;
    if (configPathStatusPaths.length === 0) {
      setPathStatusByPath({});
      setPathStatusErrorByPath({});
      return () => {
        cancelled = true;
      };
    }
    setPathStatusByPath({});
    setPathStatusErrorByPath({});
    type PathStatusLoadResult = { kind: "failed"; error: string; path: string } | { kind: "ready"; status: DesktopPathStatusPayload };
    void Promise.all(
      configPathStatusPaths.map(async (path): Promise<PathStatusLoadResult> => {
        try {
          return { kind: "ready", status: await loadDesktopPathStatus(path) };
        } catch (error: unknown) {
          console.warn("Failed to load ParaDev desktop path status.", error);
          return { error: pathStatusLoadErrorDetail(t, error), kind: "failed", path };
        }
      })
    ).then((results) => {
      if (cancelled) {
        return;
      }
      setPathStatusByPath(
        Object.fromEntries(results.flatMap((result) => (result.kind === "ready" ? [[result.status.inputPath, result.status] as const] : [])))
      );
      setPathStatusErrorByPath(Object.fromEntries(results.flatMap((result) => (result.kind === "failed" ? [[result.path, result.error] as const] : []))));
    });
    return () => {
      cancelled = true;
    };
  }, [configPathStatusPaths, t]);

  useEffect(() => {
    let cancelled = false;
    if (projectWorkspaceBlocked) {
      const fallback = fallbackParaDevAiChatProfilesPayload("");
      setAiChatProfileLoadError(null);
      setAiChatDefaultRole(fallback.defaultRole);
      setAiChatProfiles(fallback.profiles);
      setAiChatSourceKindRows(fallback.sourceKindRows ?? []);
      setAiChatSourceKinds(fallback.sourceKinds);
      return () => {
        cancelled = true;
      };
    }
    loadParaDevAiChatProfiles(activeProjectOption.path)
      .then((payload) => {
        if (!cancelled) {
          setAiChatDefaultRole(payload.defaultRole);
          setAiChatProfileLoadError(null);
          setAiChatProfiles(payload.profiles);
          setAiChatSourceKindRows(payload.sourceKindRows ?? []);
          setAiChatSourceKinds(payload.sourceKinds);
        }
      })
      .catch((error: unknown) => {
        console.warn("Failed to load ParaDev AI chat profiles.", error);
        if (!cancelled) {
          const fallback = fallbackParaDevAiChatProfilesPayload(activeProjectOption.path);
          setAiChatProfileLoadError(aiChatProfileLoadErrorDetail(t, error));
          setAiChatDefaultRole((current) => current || fallback.defaultRole);
          setAiChatProfiles((current) => (current.length > 0 ? current : fallback.profiles));
          setAiChatSourceKindRows((current) => (current.length > 0 ? current : fallback.sourceKindRows ?? []));
          setAiChatSourceKinds((current) => (current.length > 0 ? current : fallback.sourceKinds));
        }
      });
    return () => {
      cancelled = true;
    };
  }, [activeProjectOption.path, projectWorkspaceBlocked, t]);

  useEffect(() => {
    let cancelled = false;
    readPersistedAppSettings(fallbackProjectOptions[0].id, openPathPlatform)
      .then((result) => {
        if (cancelled || !result) {
          return;
        }
        const { configLoadFailure, settings } = result;
        setSettingsLoadFailed(false);
        setTheme(settings.theme);
        setLocale(settings.locale);
        setConfigPageSettings(settings.configPage);
        setLlmStatus(defaultConfigLlmStatus(settings.configPage.llm));
        if (configLoadFailure) {
          setConfigPersistenceStatus(configLoadFailure);
        }
        setAiChatDock(settings.chat.dock);
        setAiChatOpen(settings.chat.open);
        setOpenTarget(normalizeOpenPathTarget(settings.openTarget, openPathPlatform));
        setProjectPanelOpen(settings.sidebars.projectPanelOpen);
        setInspectorOpen(settings.sidebars.inspectorOpen);
        setModuleOrderByProject(settings.moduleOrderByProject);
        setModuleDefaultsByProject(settings.moduleDefaultsByProject);
        setModuleOrder(settings.moduleOrderByProject[activeProjectIdRef.current] ?? []);
        setActiveProjectPath(settings.activeProjectPath);
        if (settings.activeProjectPath && settings.activeProjectPath !== activeProjectRootRef.current) {
          void refreshDesktopState(settings.activeProjectPath, undefined, {
            recoverRememberedProject: true
          });
        }
      })
      .catch((error: unknown) => {
        console.warn("Failed to load ParaDev app settings.", error);
        if (!cancelled) {
          setSettingsLoadFailed(true);
          setConfigPersistenceStatus(configPersistenceLoadFailureStatus("desktop app settings", error));
        }
      })
      .finally(() => {
        if (!cancelled) {
          setSettingsReady(true);
        }
      });
    return () => {
      cancelled = true;
    };
  }, [openPathPlatform, refreshDesktopState]);

  useEffect(() => {
    if (!shouldPersistAppSettings({ settingsLoadFailed, settingsReady })) {
      return;
    }
    const encoded = JSON.stringify(persistableAppSettings);
    const timeout = window.setTimeout(() => {
      if (encoded === lastSavedSettingsRef.current) {
        return;
      }
      lastSavedSettingsRef.current = encoded;
      writeStorageValue(APP_SETTINGS_STORAGE_KEY, encoded);
      writeAppConfig(persistableAppSettings as unknown as Record<string, unknown>).catch((error: unknown) => {
        console.warn("Failed to persist ParaDev app settings.", error);
        setConfigPersistenceStatus(configPersistenceFailureStatus("desktop app settings", error, t));
      });
    }, 250);
    return () => window.clearTimeout(timeout);
  }, [persistableAppSettings, settingsLoadFailed, settingsReady, t]);

  useEffect(() => {
    return installAuthoringCloseGuards({
      browserTarget: window,
      getState: () => editorSessionStore.getSnapshot()
    });
  }, [editorSessionStore]);

  useLayoutEffect(() => {
    const nextRoot = activeProjectOption.path;
    const previousRoot = workspaceViewProjectRootRef.current;
    if (!nextRoot || nextRoot === previousRoot) {
      return;
    }
    const previous = latestWorkspaceViewRef.current;
    if (previousRoot) {
      workspaceViewByProjectRef.current.set(previousRoot, {
        ...previous,
        moduleSelectionTarget: previous.moduleSelectionTarget
          ? { ...previous.moduleSelectionTarget }
          : null,
        openTabEntries: previous.openTabEntries.map((entry) => ({ ...entry }))
      });
    }
    workspaceViewProjectRootRef.current = nextRoot;
    const restored = workspaceViewByProjectRef.current.get(nextRoot);
    setActiveModule(restored?.activeModule ?? baseFeatureModules[0].id);
    setActiveTab(restored?.activeTab ?? "");
    setModuleSelectionTarget(
      restored?.moduleSelectionTarget
        ? { ...restored.moduleSelectionTarget }
        : null
    );
    setOpenTabEntries(
      restored?.openTabEntries.map((entry) => ({ ...entry })) ?? []
    );
    setSecondaryTab(restored?.secondaryTab ?? "");
    setSplitView(restored?.splitView ?? false);
    setModuleCreateIntent(null);
  }, [activeProjectOption.path]);

  useEffect(() => {
    if (
      !isWorkspaceProjectModelReady(
        activeProjectOption,
        browser,
        templates
      )
    ) {
      return;
    }
    if (featureModules.some((module) => module.id === activeModule)) {
      return;
    }
    setActiveModule(featureModules[0]?.id ?? "");
  }, [activeModule, activeProjectOption, browser, featureModules, templates]);

  useEffect(() => {
    if (!browser || browser.root !== activeProjectOption.path) {
      return;
    }
    const reconciled = reconcileOpenTabEntries(
      activeProjectOption.path,
      openTabEntries,
      workspaceTabs,
      editorSessionStore
    );
    if (reconciled.entries !== openTabEntries) {
      setOpenTabEntries(reconciled.entries);
    }
    if (reconciled.cleanupFailure) {
      const failure = reconciled.cleanupFailure;
      setAuthoringCloseIntent((current) =>
        current ?? {
          error: localizedParaDevServiceError(t, failure.error),
          key: failure.key,
          kind: "tab",
          tabId: failure.tabId
        }
      );
    }
  }, [
    activeProjectOption.path,
    browser,
    editorSessionSnapshot,
    editorSessionStore,
    openTabEntries,
    t,
    workspaceTabs
  ]);

  useEffect(() => {
    if (openTabIds.length === 0) {
      if (activeTab) {
        setActiveTab("");
      }
      if (secondaryTab) {
        setSecondaryTab("");
      }
      if (splitView) {
        setSplitView(false);
      }
      return;
    }

    const nextActiveTab = openTabIds.includes(activeTab) ? activeTab : openTabIds[0];
    if (nextActiveTab !== activeTab) {
      setActiveTab(nextActiveTab);
    }
    if (secondaryTab && (!openTabIds.includes(secondaryTab) || secondaryTab === nextActiveTab)) {
      setSecondaryTab(openTabIds.find((tabId) => tabId !== nextActiveTab) ?? "");
    }
    if (openTabIds.length < 2 && splitView) {
      setSplitView(false);
    }
  }, [activeTab, openTabIds, secondaryTab, splitView]);

  const loadScopedBrowserForTab = useCallback(
    async (
      tab: WorkspaceTab | null,
      scopeOverride: ProjectBrowserScope | null = null
    ) => {
      const scope = scopeOverride ?? browserScopeForWorkspaceTab(tab, browser);
      if (!scope || !activeProjectOption.path || !hasDesktopBackend()) {
        return;
      }
      if (browserHasScopedPayload(browser, scope)) {
        return;
      }
      const key = scopedBrowserKey(activeProjectOption.path, scope);
      if (
        scopedBrowserResolvedKeysRef.current.has(key) ||
        scopedBrowserByKey[key] ||
        scopedBrowserRequestsRef.current.has(key)
      ) {
        return;
      }
      const projectRoot = activeProjectOption.path;
      const refreshGeneration = latestProjectRefreshRef.current;
      scopedBrowserRequestsRef.current.set(key, refreshGeneration);
      setScopedBrowserLoadingByKey((current) => (current[key] ? current : { ...current, [key]: true }));
      setScopedBrowserErrorByKey((current) => removeScopedBrowserErrorKey(current, key));
      try {
        const payload = await loadProjectBrowser({
          projectRoot,
          family: scope.family,
          moduleId: scope.moduleId,
          collectionId: scope.collectionId
        });
        if (!shouldCommitScopedBrowserPayload(payload, projectRoot, activeProjectRootRef.current, refreshGeneration, latestProjectRefreshRef.current)) {
          return;
        }
        scopedBrowserResolvedKeysRef.current.add(key);
        setScopedBrowserByKey((current) => ({ ...current, [key]: payload }));
        setScopedBrowserErrorByKey((current) => removeScopedBrowserErrorKey(current, key));
        const baseBrowser = desktopState?.browser;
        const mergedPayload = isUnfilteredProjectBrowserPayload(baseBrowser)
          ? mergeProjectBrowserPayloadsForProject(projectRoot, baseBrowser, ...Object.values(scopedBrowserByKey), payload)
          : null;
        if (mergedPayload && isUnfilteredProjectBrowserPayload(mergedPayload)) {
          void writeCachedProjectBrowser(mergedPayload).catch((error: unknown) => {
            console.warn("Failed to persist scoped ParaDev browser cache.", error);
          });
        }
      } catch (error: unknown) {
        if (!shouldCommitProjectRefresh(refreshGeneration, latestProjectRefreshRef.current) || activeProjectRootRef.current !== projectRoot) {
          return;
        }
        console.warn("Failed to load scoped ParaDev browser payload.", error);
        setScopedBrowserErrorByKey((current) => ({
          ...current,
          [key]: scopedBrowserLoadErrorDetail(t, error)
        }));
      } finally {
        if (scopedBrowserRequestsRef.current.get(key) === refreshGeneration) {
          scopedBrowserRequestsRef.current.delete(key);
          setScopedBrowserLoadingByKey((current) => removeScopedBrowserLoadingKey(current, key));
        }
      }
    },
    [activeProjectOption.path, browser, desktopState?.browser, scopedBrowserByKey, t]
  );

  useEffect(() => {
    if (!shouldLoadWorkspaceBrowserScope(activeRail)) {
      return;
    }
    void loadScopedBrowserForTab(activeWorkspaceTab);
    if (splitView) {
      void loadScopedBrowserForTab(secondaryWorkspaceTab);
    }
  }, [activeRail, activeWorkspaceTab, loadScopedBrowserForTab, secondaryWorkspaceTab, splitView]);

  useEffect(() => {
    if (
      !shouldLoadWorkspaceBrowserScope(activeRail) ||
      !activeProjectOption.path ||
      !browser ||
      Object.keys(browser.filters).length > 0 ||
      !hasDesktopBackend()
    ) {
      return;
    }
    const tabs = splitView
      ? [activeWorkspaceTab, secondaryWorkspaceTab]
      : [activeWorkspaceTab];
    const unresolvedTabs = tabs.filter((tab) => {
      const scope = sourceBrowserScopeForOrdinaryModuleTab(tab, browser);
      if (!scope || browserHasScopedPayload(browser, scope)) {
        return false;
      }
      return claimSourceBrowserFallbackCheck(
        sourceBrowserFallbackChecksRef.current,
        scopedBrowserKey(activeProjectOption.path, scope)
      );
    });
    if (unresolvedTabs.length === 0) {
      return;
    }

    const projectRoot = activeProjectOption.path;
    const refreshGeneration = latestProjectRefreshRef.current;
    void loadProjectCatalogStatus({ projectRoot })
      .then((status) => {
        if (
          !shouldCommitProjectRefresh(
            refreshGeneration,
            latestProjectRefreshRef.current
          ) ||
          activeProjectRootRef.current !== projectRoot
        ) {
          return;
        }
        for (const tab of unresolvedTabs) {
          if (!tab) {
            continue;
          }
          const scope = sourceBrowserScopeForUnavailableCatalog(
            tab,
            browser,
            status
          );
          if (scope) {
            void loadScopedBrowserForTab(tab, scope);
          }
        }
      })
      .catch(() => {
        // The module editor retains the authoritative Catalog query/status error.
      });
  }, [
    activeProjectOption.path,
    activeRail,
    activeWorkspaceTab,
    browser,
    loadScopedBrowserForTab,
    secondaryWorkspaceTab,
    splitView
  ]);

  const blockBusyAuthoringNavigation = (): boolean => {
    if (!editorSessionStore.getSnapshot().busy) {
      return false;
    }
    setAuthoringCloseIntent({ kind: "busy" });
    return true;
  };

  const openWorkspaceTab = (id: string, options: { pinned?: boolean } = {}) => {
    const nextTab = workspaceTabs.find((tab) => tab.id === id);
    if (!nextTab) {
      return;
    }

    const pinned = Boolean(options.pinned);
    setOpenTabEntries((entries) => nextOpenTabEntriesForOpen(entries, nextTab, { pinned }));
    setActiveTab(nextTab.id);
    if (splitView) {
      setSecondaryTab((current) => (current === nextTab.id ? activeTab : current));
    }
  };

  const closeWorkspaceTabImmediately = useCallback((id: string) => {
    setOpenTabEntries((entries) => {
      const nextEntries = entries.filter((entry) => entry.id !== id);
      const nextIds = nextEntries.map((entry) => entry.id);
      if (nextIds.length === 0) {
        setActiveTab("");
        setSecondaryTab("");
        setSplitView(false);
        return nextEntries;
      }

      const nextActiveTab = activeTab === id || !nextIds.includes(activeTab) ? nextIds[0] : activeTab;
      if (nextActiveTab !== activeTab) {
        setActiveTab(nextActiveTab);
      }
      if (secondaryTab === id || !nextIds.includes(secondaryTab) || secondaryTab === nextActiveTab) {
        setSecondaryTab(nextIds.find((tabId) => tabId !== nextActiveTab) ?? "");
      }
      if (nextIds.length < 2) {
        setSplitView(false);
      }
      return nextEntries;
    });
  }, [activeTab, secondaryTab]);

  const handleCloseTab = (id: string) => {
    const tab = openTabs.find((row) => row.id === id);
    const sessionKey = tab
      ? moduleEditorSessionKeyForWorkspaceTab(activeProjectOption.path, tab)
      : null;
    const siblingOpen = Boolean(
      sessionKey &&
        openTabs.some(
          (row) =>
            row.id !== id &&
            moduleEditorSessionKeyForWorkspaceTab(activeProjectOption.path, row) ===
              sessionKey
        )
    );
    const session = sessionKey
      ? editorSessionSummaryByKey.get(sessionKey)
      : undefined;
    const promptKey = moduleEditorSessionKeyRequiringClosePrompt(
      activeProjectOption.path,
      id,
      openTabs,
      editorSessionSnapshot
    );
    if (promptKey) {
      setAuthoringCloseIntent({
        key: promptKey,
        kind: "tab",
        tabId: id
      });
      return;
    }

    if (sessionKey && !siblingOpen && !session) {
      try {
        editorSessionStore.discard(sessionKey);
      } catch (error: unknown) {
        setAuthoringCloseIntent({
          error: localizedParaDevServiceError(t, error),
          key: sessionKey,
          kind: "tab",
          tabId: id
        });
        return;
      }
    }
    closeWorkspaceTabImmediately(id);
  };

  const handlePinTab = (id: string) => {
    const nextTab = workspaceTabs.find((tab) => tab.id === id);
    if (!nextTab) {
      return;
    }
    setOpenTabEntries((entries) => {
      if (!entries.some((entry) => entry.id === id)) {
        return [
          ...entries,
          { id, pinned: true, tab: cachedWorkspaceTab(nextTab) }
        ];
      }
      return entries.map((entry) =>
        entry.id === id
          ? { ...entry, pinned: true, tab: cachedWorkspaceTab(nextTab) }
          : entry
      );
    });
  };

  const handleSelectModule = (id: string) => {
    if (blockBusyAuthoringNavigation()) {
      return;
    }
    setActiveModule(id);
    setActiveRail("projects");
    openWorkspaceTab(workspaceTabIdForModuleSelection(id));
  };

  const handlePinModule = (id: string) => {
    if (blockBusyAuthoringNavigation()) {
      return;
    }
    setActiveModule(id);
    setActiveRail("projects");
    openWorkspaceTab(workspaceTabIdForModuleSelection(id), { pinned: true });
  };

  const handleSelectModuleDiagram = (id: string) => {
    if (blockBusyAuthoringNavigation()) {
      return;
    }
    setActiveModule(moduleIdForDiagramTabId(id));
    setActiveRail("projects");
    openWorkspaceTab(id);
  };

  const handleOpenModuleEntity = (target: WorkspaceModuleSelectionTarget) => {
    if (blockBusyAuthoringNavigation()) {
      return;
    }
    setActiveModule(target.familyId);
    setActiveRail("projects");
    setModuleSelectionTarget(target);
    openWorkspaceTab(workspaceTabIdForModuleSelection(target.familyId));
  };

  const handleBuildTarget = (requestedTarget: BuildTarget) => {
    if (blockBusyAuthoringNavigation()) {
      return;
    }
    buildTargetIntentNonceRef.current += 1;
    setBuildTargetIntent({
      nonce: buildTargetIntentNonceRef.current,
      projectRoot: activeProjectOption.path,
      target: requestedTarget
    });
    setActiveRail("build");
  };

  const handleBuildTargetIntentConsumed = useCallback((nonce: number) => {
    setBuildTargetIntent((current) => (current?.nonce === nonce ? null : current));
  }, []);

  const handleModuleSelectionTargetChange = useCallback((target: WorkspaceModuleSelectionTarget | null) => {
    setModuleSelectionTarget((current) => (moduleSelectionTargetsEqual(current, target) ? current : target));
  }, []);

  const handleSelectConfig = (id: string) => {
    if (blockBusyAuthoringNavigation()) {
      return;
    }
    setActiveConfig(id);
    setActiveRail("settings");
    openWorkspaceTab(id);
  };

  const handlePinConfig = (id: string) => {
    if (blockBusyAuthoringNavigation()) {
      return;
    }
    setActiveConfig(id);
    setActiveRail("settings");
    openWorkspaceTab(id, { pinned: true });
  };

  const handleSelectRail = (id: string) => {
    if (blockBusyAuthoringNavigation()) {
      return;
    }
    setActiveRail(id);
  };

  const handleSelectSettings = () => {
    if (blockBusyAuthoringNavigation()) {
      return;
    }
    setActiveRail("settings");
    setProjectPanelOpen(true);
    openWorkspaceTab(activeConfig);
  };

  const handleSelectTab = (id: string) => {
    if (blockBusyAuthoringNavigation()) {
      return;
    }
    setActiveTab(id);
    if (splitView && secondaryTab === id) {
      setSecondaryTab(openTabIds.find((tabId) => tabId !== id) ?? "");
    }
  };

  const handleSplitToggle = () => {
    if (blockBusyAuthoringNavigation()) {
      return;
    }
    if (openTabIds.length < 2) {
      setSplitView(false);
      return;
    }

    setSplitView((enabled) => {
      if (enabled) {
        return false;
      }

      const nextActiveTab = openTabIds.includes(activeTab) ? activeTab : openTabIds[0];
      if (nextActiveTab !== activeTab) {
        setActiveTab(nextActiveTab);
      }
      setSecondaryTab(openTabIds.find((id) => id !== nextActiveTab) ?? "");
      return true;
    });
  };

  const handleSelectProject = (id: string) => {
    if (blockBusyAuthoringNavigation()) {
      return;
    }
    if (projectLoading || projectOpening || projectImporting) {
      return;
    }
    const project = projectOptions.find((option) => option.id === id);
    setProjectOpenError("");
    setRememberedProjectRecovery(null);
    if (!project) {
      return;
    }
    void refreshDesktopState(project.path, id, { throwOnError: true }).catch(
      (error: unknown) => {
        setProjectOpenError(
          t("project.openFailed", {
            message: localizedParaDevServiceError(t, error)
          })
        );
      }
    );
  };

  const handleModuleReorder = (fromId: string, toId: string) => {
    const nextModules = moveModuleBefore(featureModules, fromId, toId);
    const nextOrder = nextModules.map((module) => module.id);
    setModuleOrder(nextOrder);
    setModuleOrderByProject((current) => ({
      ...current,
      [activeProjectOption.projectId]: nextOrder
    }));
  };

  const handleOpenProject = () => {
    if (blockBusyAuthoringNavigation()) {
      return;
    }
    if (projectLoading || projectOpening || projectImporting) {
      return;
    }
    setProjectOpenError("");
    setRememberedProjectRecovery(null);
    setProjectOpening(true);
    selectProjectPath()
      .then(async (projectRoot) => {
        if (projectRoot) {
          await refreshDesktopState(projectRoot, undefined, {
            throwOnError: true
          });
        }
      })
      .catch((error: unknown) => {
        setProjectOpenError(t("project.openFailed", { message: localizedParaDevServiceError(t, error) }));
      })
      .finally(() => {
        setProjectOpening(false);
      });
  };

  const handleImportProjectPackage = () => {
    if (blockBusyAuthoringNavigation()) {
      return;
    }
    if (projectLoading || projectOpening || projectImporting) {
      return;
    }
    setProjectOpenError("");
    setRememberedProjectRecovery(null);
    setProjectImporting(true);
    importProjectPackage()
      .then(async (payload) => {
        if (payload) {
          await refreshDesktopState(payload.project_root, undefined, {
            throwOnError: true
          });
        }
      })
      .catch((error: unknown) => {
        setProjectOpenError(
          t("project.onboarding.installFailed", {
            message: localizedParaDevServiceError(t, error)
          })
        );
      })
      .finally(() => {
        setProjectImporting(false);
      });
  };

  const handleOpenPath = useCallback(
    (path: string) => {
      const cleanPath = path.trim();
      if (!cleanPath) {
        return;
      }
      openProjectPath(cleanPath, openTarget).catch((error: unknown) => {
        setProjectOpenError(t("project.openFailed", { message: localizedParaDevServiceError(t, error) }));
      });
    },
    [openTarget, t]
  );

  const handleOpenTargetChange = (target: OpenPathTarget) => {
    setOpenTarget(normalizeOpenPathTarget(target, openPathPlatform));
  };

  const handleConfigPageSettingsChange = (settings: ConfigPageSettings) => {
    const normalized = normalizeConfigPageSettings(settings, configPageSettings);
    const configWrites = desktopConfigWritesForSettingsChange(configPageSettings, normalized);
    const llmRouteChanged = configWrites.some(([key]) => key.startsWith("paradev.ai.") && key !== DESKTOP_CONFIG_KEYS.aiChatDefaultRole);
    setConfigPageSettings(normalized);
    setModuleDefaultsByProject((current) => moduleDefaultsByProjectForSettings(current, activeProjectIdRef.current, normalized));
    setAiChatDefaultRole(normalized.chat.defaultRole);
    setLlmStatus((current) => (llmRouteChanged ? defaultConfigLlmStatus(normalized.llm) : current ?? defaultConfigLlmStatus(normalized.llm)));
    if (configWrites.length > 0) {
      setConfigPersistenceStatus(configPersistenceSavingStatus());
      Promise.all(
        configWrites.map(async ([key, value]) => {
          try {
            await writeConfigValue(key, value);
            return null;
          } catch (error: unknown) {
            console.warn(`Failed to persist ParaDev config value ${key}.`, error);
            return configPersistenceFailureStatus(key, error, t);
          }
        })
      ).then((results) => {
        setConfigPersistenceStatus(results.find((result): result is ConfigPersistenceStatus => result !== null) ?? defaultConfigPersistenceStatus());
      });
    }
  };

  const handleProjectPreferredLanguageChange = useCallback(
    async (preferredLanguage: string) => {
      if (
        projectLanguageBusy
        || !activeProjectOption.path
        || preferredLanguage === activeProjectOption.preferredLanguage
      ) {
        return;
      }
      const projectRoot = activeProjectOption.path;
      const projectIdentity = activeProjectOption.id;
      setProjectLanguageBusy(true);
      setProjectLanguageError("");
      try {
        await setProjectPreferredLanguage(projectRoot, preferredLanguage);
        await refreshDesktopState(projectRoot, projectIdentity, {
          throwOnError: true,
        });
      } catch (error: unknown) {
        if (activeProjectRootRef.current === projectRoot) {
          setProjectLanguageError(localizedParaDevServiceError(t, error));
        }
      } finally {
        setProjectLanguageBusy(false);
      }
    },
    [
      activeProjectOption.id,
      activeProjectOption.path,
      activeProjectOption.preferredLanguage,
      projectLanguageBusy,
      refreshDesktopState,
      t,
    ],
  );

  const handleCheckDependency = (id: string) => {
    if (dependencyBusyId) {
      return;
    }
    setDependencyBusyId(id);
    checkDesktopDependency(id)
      .then((status) => {
        setDependencyStatusById((current) => ({ ...current, [id]: status }));
      })
      .catch((error: unknown) => {
        setDependencyStatusById((current) => ({
          ...current,
          [id]: dependencyErrorStatus(id, localizedParaDevServiceError(t, error))
        }));
      })
      .finally(() => {
        setDependencyBusyId("");
      });
  };

  const handleInstallDependency = (id: string) => {
    if (dependencyBusyId) {
      return;
    }
    setDependencyBusyId(id);
    installDesktopDependency(id)
      .then((status) => {
        setDependencyStatusById((current) => ({ ...current, [id]: status }));
      })
      .catch((error: unknown) => {
        setDependencyStatusById((current) => ({
          ...current,
          [id]: dependencyErrorStatus(id, localizedParaDevServiceError(t, error))
        }));
      })
      .finally(() => {
        setDependencyBusyId("");
      });
  };

  const handleTestLlm = () => {
    const { baseUrl, gateway, keyEnv, model, preset, provider } = configPageSettings.llm;
    setLlmStatus({
      ...defaultConfigLlmStatus(configPageSettings.llm),
      status: "unknown",
      testDetail: t("config.models.testRunning", { route: aiRouteLabelWithPreset({ gateway, model, preset, provider, t }) }),
      testedAt: new Date().toISOString()
    });
    testHeavenBaseLlmRoute({ baseUrl, gateway, keyEnv, model, preset, provider })
      .then(setLlmStatus)
      .catch((error: unknown) => {
        setLlmStatus(llmErrorStatus(configPageSettings.llm, localizedParaDevServiceError(t, error)));
      });
  };

  const handleSaveAiChatProfile = (profileId: string, profile: ParaDevAiChatProfileWrite) => {
    setConfigPersistenceStatus(configPersistenceSavingStatus());
    writeParaDevAiChatProfile(profileId, profile, activeProjectOption.path)
      .then((payload) => {
        setAiChatDefaultRole(payload.defaultRole);
        setAiChatProfileLoadError(null);
        setAiChatProfiles(payload.profiles);
        setAiChatSourceKindRows(payload.sourceKindRows ?? []);
        setAiChatSourceKinds(payload.sourceKinds);
        setConfigPersistenceStatus(defaultConfigPersistenceStatus());
      })
      .catch((error: unknown) => {
        console.warn("Failed to persist ParaDev AI chat profile.", error);
        setConfigPersistenceStatus(configPersistenceFailureStatus(`AI profile ${profileId}`, error, t));
      });
  };

  const handleResetAiChatProfile = (profileId: string) => {
    setConfigPersistenceStatus(configPersistenceSavingStatus());
    resetParaDevAiChatProfile(profileId, activeProjectOption.path)
      .then((payload) => {
        setAiChatDefaultRole(payload.defaultRole);
        setAiChatProfileLoadError(null);
        setAiChatProfiles(payload.profiles);
        setAiChatSourceKindRows(payload.sourceKindRows ?? []);
        setAiChatSourceKinds(payload.sourceKinds);
        setConfigPersistenceStatus(defaultConfigPersistenceStatus());
      })
      .catch((error: unknown) => {
        console.warn("Failed to reset ParaDev AI chat profile.", error);
        setConfigPersistenceStatus(configPersistenceFailureStatus(`AI profile ${profileId} reset`, error, t));
      });
  };

  const handleAiChatSend = useCallback(
    async (prompt: string, role = "chat", sources: ParaDevAiChatSource[] = []) => {
      const { baseUrl, gateway, keyEnv, model, preset, provider } = configPageSettings.llm;
      const response = await chatWithParaDevAi({
        baseUrl,
        gateway,
        keyEnv,
        model,
        preset,
        projectRoot: activeProjectOption.path,
        prompt,
        provider,
        role,
        sources
      });
      return {
        ...(response.proposal
          ? {
              proposal: {
                projectRoot: response.projectRoot,
                proposal: response.proposal,
                role: response.role,
                sources: response.sources
              }
            }
          : {}),
        text: aiChatReplyText(response, t)
      };
    },
    [activeProjectOption.path, configPageSettings.llm, t]
  );

  const handleAiChatOperationNavigate = (navigation: AiChatOperationNavigation) => {
    if (blockBusyAuthoringNavigation()) {
      return;
    }
    const target = aiChatOperationNavigationTarget({
      activeModule,
      featureModules,
      operationId: navigation.operationId,
      role: navigation.role,
      sources: navigation.sources
    });
    if (!target) {
      return;
    }
    if (target.rail === "build") {
      aiOperationIntentNonceRef.current += 1;
      setBuildAiOperationIntent(aiOperationIntentForTarget(target, aiOperationIntentNonceRef.current));
      setActiveRail("build");
      return;
    }

    setActiveModule(target.familyId);
    setActiveRail("projects");
    setProjectPanelOpen(true);
    setModuleSelectionTarget(null);
    openWorkspaceTab(workspaceTabIdForModuleSelection(target.familyId));
    moduleCreateIntentNonceRef.current += 1;
    aiOperationIntentNonceRef.current += 1;
    setModuleCreateIntent({
      ai: aiOperationIntentForTarget(target, aiOperationIntentNonceRef.current),
      familyId: target.familyId,
      mode: target.createMode,
      nonce: moduleCreateIntentNonceRef.current
    });
  };

  const handleAiChatProposalReview = (
    review: AiChatProposalReview
  ) => {
    if (blockBusyAuthoringNavigation()) {
      return;
    }
    if (review.proposal.operationId === "module.source_form_update_batch") {
      const prepared = prepareAiChatSourceUpdateReview({
        activeProjectId: activeProjectOption.projectId,
        activeProjectRoot: activeProjectOption.path,
        proposal: review.proposal,
        proposalProjectRoot: review.projectRoot,
        t
      });
      const familyAvailable = featureModules.some(
        (module) =>
          canonicalFamilyId(module.id) === canonicalFamilyId(prepared.familyId)
      );
      const tabId = workspaceTabIdForModuleSelection(prepared.familyId);
      if (
        !familyAvailable ||
        !workspaceTabs.some((tab) => tab.id === tabId)
      ) {
        throw new Error(t("chat.proposal.sourceUpdate.familyUnavailable"));
      }
      const sessionKey = moduleEditorSessionKey(
        activeProjectOption.path,
        prepared.familyId
      );
      assertAiChatSourceUpdateReviewAvailable({
        editorSessionStore,
        sessionKey,
        t
      });
      editorSessionStore.setSourceUpdate(sessionKey, prepared.state);
      setActiveModule(prepared.familyId);
      setActiveRail("projects");
      setProjectPanelOpen(true);
      setModuleSelectionTarget(null);
      openWorkspaceTab(tabId);
      moduleCreateIntentNonceRef.current += 1;
      aiOperationIntentNonceRef.current += 1;
      setModuleCreateIntent({
        ai: {
          nonce: aiOperationIntentNonceRef.current,
          operationId: "module.source_form_update_batch",
          role: review.role,
          sources: aiOperationIntentSources(review.sources)
        },
        familyId: prepared.familyId,
        mode: "source-update",
        nonce: moduleCreateIntentNonceRef.current
      });
      return;
    }
    if (review.proposal.operationId === "collection.scaffold") {
      const prepared = prepareAiChatCollectionReview({
        activeProjectId: activeProjectOption.projectId,
        activeProjectRoot: activeProjectOption.path,
        proposal: review.proposal,
        proposalProjectRoot: review.projectRoot,
        t,
        templates
      });
      const familyAvailable = featureModules.some(
        (module) =>
          canonicalFamilyId(module.id) === canonicalFamilyId(prepared.familyId)
      );
      const tabId = workspaceTabIdForModuleSelection(prepared.familyId);
      if (
        !familyAvailable ||
        !workspaceTabs.some((tab) => tab.id === tabId)
      ) {
        throw new Error(t("chat.proposal.collection.familyUnavailable"));
      }
      const sessionKey = moduleEditorSessionKey(
        activeProjectOption.path,
        prepared.familyId
      );
      assertAiChatCollectionReviewAvailable({
        editorSessionStore,
        sessionKey,
        t
      });
      editorSessionStore.setCollectionCreate(sessionKey, prepared.state);
      setActiveModule(prepared.familyId);
      setActiveRail("projects");
      setProjectPanelOpen(true);
      setModuleSelectionTarget(null);
      openWorkspaceTab(tabId);
      moduleCreateIntentNonceRef.current += 1;
      aiOperationIntentNonceRef.current += 1;
      setModuleCreateIntent({
        ai: {
          nonce: aiOperationIntentNonceRef.current,
          operationId: "collection.scaffold",
          role: review.role,
          sources: aiOperationIntentSources(review.sources)
        },
        familyId: prepared.familyId,
        mode: "collection",
        nonce: moduleCreateIntentNonceRef.current
      });
      return;
    }
    const prepared = prepareAiChatModuleBatchReview({
      activeProjectId: activeProjectOption.projectId,
      activeProjectRoot: activeProjectOption.path,
      proposal: review.proposal,
      proposalProjectRoot: review.projectRoot,
      t,
      templates
    });
    const familyAvailable = featureModules.some(
      (module) =>
        canonicalFamilyId(module.id) === canonicalFamilyId(prepared.familyId)
    );
    const tabId = workspaceTabIdForModuleSelection(prepared.familyId);
    if (
      !familyAvailable ||
      !workspaceTabs.some((tab) => tab.id === tabId)
    ) {
      throw new Error(t("chat.proposal.moduleBatch.familyUnavailable"));
    }
    const sessionKey = moduleEditorSessionKey(
      activeProjectOption.path,
      prepared.familyId
    );
    assertAiChatModuleBatchReviewAvailable({
      editorSessionStore,
      sessionKey,
      t
    });

    editorSessionStore.setBatchCreate(sessionKey, prepared.state);
    setActiveModule(prepared.familyId);
    setActiveRail("projects");
    setProjectPanelOpen(true);
    setModuleSelectionTarget(null);
    openWorkspaceTab(tabId);
    moduleCreateIntentNonceRef.current += 1;
    aiOperationIntentNonceRef.current += 1;
    setModuleCreateIntent({
      ai: {
        nonce: aiOperationIntentNonceRef.current,
        operationId: "module.create_batch",
        role: review.role,
        sources: aiOperationIntentSources(review.sources)
      },
      familyId: prepared.familyId,
      mode: "batch",
      nonce: moduleCreateIntentNonceRef.current
    });
  };

  const handleModuleCreateIntentConsumed = useCallback((nonce: number) => {
    setModuleCreateIntent((current) => (current?.nonce === nonce ? null : current));
  }, []);

  const handleSecondaryTabChange = (action: SetStateAction<string>) => {
    if (blockBusyAuthoringNavigation()) {
      return;
    }
    setSecondaryTab(action);
  };

  const handleCancelAuthoringClose = useCallback(() => {
    setAuthoringCloseIntent(null);
  }, []);

  const handleDiscardAuthoringClose = useCallback(() => {
    const intent = authoringCloseIntent;
    if (!intent || intent.kind !== "tab") {
      return;
    }
    try {
      const session = editorSessionStore
        .getSnapshot()
        .sessions.find((row) => row.key === intent.key);
      if (session?.busy) {
        return;
      }
      editorSessionStore.discard(intent.key);
      closeWorkspaceTabImmediately(intent.tabId);
      setAuthoringCloseIntent(null);
    } catch (error: unknown) {
      setAuthoringCloseIntent({
        ...intent,
        error: localizedParaDevServiceError(t, error)
      });
    }
  }, [
    authoringCloseIntent,
    closeWorkspaceTabImmediately,
    editorSessionStore,
    t
  ]);

  const authoringClosePrompt = useMemo(() => {
    if (!authoringCloseIntent) {
      return null;
    }
    const snapshot = editorSessionSnapshot;
    if (
      shouldCompleteAuthoringCloseIntent(authoringCloseIntent, snapshot)
    ) {
      return null;
    }
    const session =
      authoringCloseIntent.kind === "tab"
        ? snapshot.sessions.find((row) => row.key === authoringCloseIntent.key)
        : undefined;
    const busy =
      authoringCloseIntent.kind === "busy"
        ? true
        : session?.busy ?? false;
    const dirtySessionCount =
      session?.dirty ? 1 : 0;
    return {
      busy,
      dirtySessionCount,
      error:
        authoringCloseIntent.kind === "busy"
          ? undefined
          : authoringCloseIntent.error,
      onCancel: handleCancelAuthoringClose,
      onDiscard: handleDiscardAuthoringClose
    };
  }, [
    authoringCloseIntent,
    editorSessionSnapshot,
    handleCancelAuthoringClose,
    handleDiscardAuthoringClose
  ]);

  useEffect(() => {
    const intent = authoringCloseIntent;
    if (intent?.kind === "busy" && !editorSessionSnapshot.busy) {
      setAuthoringCloseIntent(null);
      return;
    }
    if (
      !shouldCompleteAuthoringCloseIntent(intent, editorSessionSnapshot)
    ) {
      return;
    }
    if (!intent || intent.kind !== "tab") {
      return;
    }
    try {
      editorSessionStore.discard(intent.key);
      closeWorkspaceTabImmediately(intent.tabId);
      setAuthoringCloseIntent(null);
    } catch (error: unknown) {
      setAuthoringCloseIntent({
        ...intent,
        error: localizedParaDevServiceError(t, error)
      });
    }
  }, [
    authoringCloseIntent,
    closeWorkspaceTabImmediately,
    editorSessionSnapshot,
    editorSessionStore,
    t
  ]);

  if (showProjectBootLoading || showProjectOnboarding) {
    return (
      <div className={`theme-${theme}`} lang={htmlLangForLocale(locale)}>
        <ProjectOnboarding
          checking={showProjectBootLoading}
          error={
            showProjectBootLoading
              ? ""
              : projectOpenError ||
                projectRecoveryError ||
                localizedProjectError
          }
          importing={projectImporting}
          onImportProject={handleImportProjectPackage}
          onOpenProject={handleOpenProject}
          opening={projectOpening}
          t={t}
        />
      </div>
    );
  }

  return (
    <AppShell
      activeBrowserError={activeBrowserError}
      activeBrowserLoading={activeBrowserLoading}
      activeFeature={activeFeature}
      activeOption={activeRail === "settings" ? activeConfig : activeWorkspaceTab?.kind === "diagram" ? activeWorkspaceTab.id : activeModule}
      activeProject={activeProjectOption}
      activeRail={activeRail}
      activeTab={activeTab}
      activeWorkspaceTab={activeWorkspaceTab}
      bootProgress={bootProgress}
      browser={browser}
      buildDiagnosticsGeneration={buildDiagnosticsRefreshByProjectRoot[activeProjectOption.path]?.generation ?? 0}
      buildDiagnosticsRefreshSource={buildDiagnosticsRefreshByProjectRoot[activeProjectOption.path]?.source ?? "live"}
      buildLifecycle={buildLifecycle}
      configPageSettings={configPageSettings}
      configPersistenceStatus={configPersistenceStatus}
      configOptions={visibleConfigOptions}
      dependencyBusyId={dependencyBusyId}
      dependencyStatusById={dependencyStatusById}
      featureModules={visibleFeatureModules}
      inspectorOpen={inspectorOpen}
      locale={locale}
      llmStatus={llmStatus}
      aiChatGateway={configPageSettings.llm.gateway}
      aiChatModel={configPageSettings.llm.model}
      aiChatDefaultRole={aiChatDefaultRole}
      aiChatDock={aiChatDock}
      aiChatOpen={aiChatOpen}
      aiChatPreset={configPageSettings.llm.preset}
      aiChatProfileLoadError={aiChatProfileLoadError}
      aiChatProfiles={aiChatProfiles}
      aiChatProvider={configPageSettings.llm.provider}
      aiChatSourceKindRows={aiChatSourceKindRows}
      aiChatSourceKinds={aiChatSourceKinds}
      aiChatSources={aiChatSources}
      authoringClosePrompt={authoringClosePrompt}
      buildAiOperationIntent={buildAiOperationIntent}
      buildTargetIntent={buildTargetIntent}
      moduleCreateIntent={moduleCreateIntent}
      onModuleCreateIntentConsumed={handleModuleCreateIntentConsumed}
      onBuildTarget={handleBuildTarget}
      onBuildTargetIntentConsumed={handleBuildTargetIntentConsumed}
      onCheckDependency={handleCheckDependency}
      onAiChatSend={handleAiChatSend}
      onAiChatDockChange={setAiChatDock}
      onAiChatOpenChange={setAiChatOpen}
      onAiChatOperationNavigate={handleAiChatOperationNavigate}
      onAiChatProposalReview={handleAiChatProposalReview}
      onCloseTab={handleCloseTab}
      onConfigPageSettingsChange={handleConfigPageSettingsChange}
      onProjectPreferredLanguageChange={handleProjectPreferredLanguageChange}
      onInstallDependency={handleInstallDependency}
      onResetAiChatProfile={handleResetAiChatProfile}
      onSaveAiChatProfile={handleSaveAiChatProfile}
      onModuleReorder={handleModuleReorder}
      onOpenModuleEntity={handleOpenModuleEntity}
      onOpenPath={handleOpenPath}
      onModuleSelectionTargetChange={handleModuleSelectionTargetChange}
      onImportProject={handleImportProjectPackage}
      onOpenProject={handleOpenProject}
      onBuildProjectRefresh={refreshBuildPageProject}
      onProjectRefresh={refreshDesktopState}
      onPinConfig={handlePinConfig}
      onPinModule={handlePinModule}
      onPinTab={handlePinTab}
      onSplitToggle={handleSplitToggle}
      onTestLlm={handleTestLlm}
      moduleSelectionTarget={moduleSelectionTarget}
      openTabs={openTabs}
      projectError={localizedProjectError}
      projectImporting={projectImporting}
      projectLoading={projectLoading}
      projectLanguageBusy={projectLanguageBusy}
      projectLanguageError={projectLanguageError}
      projectOpenError={projectOpenError}
      projectNotice={localizedRememberedProjectRecovery}
      projectNoticeDetail={localizedRememberedProjectRecoveryDetail}
      projectOpening={projectOpening}
      pathStatusByPath={pathStatusByPath}
      pathStatusErrorByPath={pathStatusErrorByPath}
      projectOptions={projectOptions}
      projectPanelOpen={projectPanelOpen}
      railItems={railItems}
      searchQuery={searchQuery}
      sessionStore={editorSessionStore}
      onSelectConfig={handleSelectConfig}
      onSelectModuleDiagram={handleSelectModuleDiagram}
      onSelectModule={handleSelectModule}
      onSelectProject={handleSelectProject}
      onSelectRail={handleSelectRail}
      onSelectSettings={handleSelectSettings}
      onSearchQueryChange={setSearchQuery}
      onTabSelect={handleSelectTab}
      openTarget={openTarget}
      setSecondaryTab={handleSecondaryTabChange}
      setInspectorOpen={setInspectorOpen}
      setLocale={setLocale}
      setOpenTarget={handleOpenTargetChange}
      setProjectPanelOpen={setProjectPanelOpen}
      setTheme={setTheme}
      secondaryTab={secondaryTab}
      secondaryBrowserError={secondaryBrowserError}
      secondaryBrowserLoading={secondaryBrowserLoading}
      secondaryWorkspaceTab={secondaryWorkspaceTab}
      splitView={splitView}
      surfaceRows={surfaceRows}
      templates={templates}
      t={t}
      theme={theme}
    />
  );
}

function openTargetLabelKey(openTarget: OpenPathTarget) {
  return OPEN_PATH_TARGETS.find((target) => target.id === openTarget)?.labelKey ?? "openTarget.vscode";
}

function workspacePreviewGroupForTab(tab: Pick<WorkspaceTab, "id" | "kind">): WorkspacePreviewGroup {
  return tab.kind === "diagram" ? "diagram" : "regular";
}

function workspacePreviewGroupForTabId(tabId: string): WorkspacePreviewGroup {
  return tabId.startsWith("diagram:") ? "diagram" : "regular";
}

export function browserScopeForWorkspaceTab(tab: WorkspaceTab | null, browser: ProjectBrowserPayload | null): ProjectBrowserScope | null {
  if (!tab || (tab.kind !== "diagram" && tab.kind !== "module")) {
    return null;
  }
  const familyId = tab.familyId ?? (tab.kind === "diagram" ? moduleIdForDiagramTabId(tab.id) : tab.id);
  if (tab.kind === "module" && canonicalFamilyId(familyId) !== "entity") {
    return null;
  }
  return { family: sdkFamilyForWorkspaceFamily(familyId, browser) };
}

function sourceBrowserScopeForOrdinaryModuleTab(
  tab: WorkspaceTab | null,
  browser: ProjectBrowserPayload | null
): ProjectBrowserScope | null {
  if (!tab || tab.kind !== "module") {
    return null;
  }
  const familyId = tab.familyId ?? tab.id;
  if (canonicalFamilyId(familyId) === "entity") {
    return null;
  }
  return { family: sdkFamilyForWorkspaceFamily(familyId, browser) };
}

/** Returns a source-browser fallback whenever the optional Catalog cannot be queried safely. */
export function sourceBrowserScopeForUnavailableCatalog(
  tab: WorkspaceTab | null,
  browser: ProjectBrowserPayload | null,
  status: Pick<ProjectCatalogStatusPayload, "code">
): ProjectBrowserScope | null {
  return status.code !== "catalog.present"
    ? sourceBrowserScopeForOrdinaryModuleTab(tab, browser)
    : null;
}

export function aiChatSourcesForWorkspace(
  tab: WorkspaceTab | null,
  target: WorkspaceModuleSelectionTarget | null,
  browser: ProjectBrowserPayload | null,
  t: Translator,
  templates: ProjectTemplatesPayload | null = null
): ParaDevAiChatSource[] {
  const templateSources = aiChatTemplateSources(templates, t);
  const diagnosticsSources = aiChatDiagnosticsSources(browser, t);
  if (!tab || (tab.kind !== "module" && tab.kind !== "diagram")) {
    return [...aiChatProjectWorkspaceSources(browser, t), ...templateSources, ...diagnosticsSources];
  }
  const familyId = tab.kind === "diagram" ? tab.familyId ?? moduleIdForDiagramTabId(tab.id) : tab.familyId ?? tab.id;
  const label = tab.titleKey ? t(tab.titleKey) : aiChatFamilyLabel(familyId, browser, t);
  const extraSources = [...templateSources, ...diagnosticsSources];
  if (target?.familyId === familyId && target.entityId) {
    const sourcePath = target.sourcePath?.trim() ?? "";
    if (sourcePath) {
      return [
        {
          id: `source:${sourcePath}`,
          kind: "source",
          label: `${label}: ${target.entityId}`,
          detail: sourcePath,
          path: sourcePath,
          ...(target.sourceContent !== undefined
            ? {
                content: target.sourceContent,
                contentChars: target.sourceContent.length,
                truncated: false
              }
            : {}),
          familyId,
          entityId: target.entityId
        },
        ...extraSources
      ];
    }
    return [
      {
        id: `workspace:${familyId}:${target.entityId}`,
        kind: "workspace",
        label: `${label}: ${target.entityId}`,
        familyId,
        entityId: target.entityId
      },
      ...extraSources
    ];
  }
  return [
    {
      id: `workspace:${familyId}`,
      kind: "workspace",
      label,
      familyId
    },
    ...extraSources
  ];
}

export function aiChatOperationNavigationTarget({
  activeModule,
  featureModules,
  operationId,
  role = "",
  sources
}: {
  activeModule: string;
  featureModules: readonly Pick<FeatureModule, "id">[];
  operationId: string;
  role?: string;
  sources: readonly ParaDevAiChatSource[];
}): AiChatOperationNavigationTarget | null {
  if (!isFrontendApiOperationId(operationId)) {
    return null;
  }
  const intentSources = aiOperationIntentSources(sources);
  if (operationId === "build.plan" || operationId === "build.start") {
    return { operationId, rail: "build", role, sources: intentSources };
  }
  if (
    operationId === "collection.scaffold" ||
    operationId === "module.draft" ||
    operationId === "module.create_batch"
  ) {
    const familyId = aiChatModuleDraftNavigationFamilyId(sources, activeModule, featureModules);
    return familyId
      ? {
          createMode:
            operationId === "module.create_batch"
              ? "batch"
              : operationId === "collection.scaffold"
                ? "collection"
                : "single",
          familyId,
          operationId,
          rail: "projects",
          role,
          sources: intentSources
        }
      : null;
  }
  return null;
}

function aiOperationIntentForTarget(target: AiChatOperationNavigationTarget, nonce: number): AiOperationIntent {
  return {
    nonce,
    operationId: target.operationId,
    role: target.role,
    sources: target.sources
  };
}

function aiOperationIntentSources(sources: readonly ParaDevAiChatSource[]): AiOperationIntentSource[] {
  return sources.map((source) =>
    compactAiOperationIntentSource({
      detail: source.detail,
      entityId: source.entityId,
      familyId: source.familyId,
      kind: source.kind,
      label: source.label,
      moduleId: source.moduleId,
      path: source.path,
      relativePath: source.relativePath,
      sourcePath: source.sourcePath
    })
  );
}

function compactAiOperationIntentSource(source: AiOperationIntentSource): AiOperationIntentSource {
  return Object.fromEntries(Object.entries(source).filter(([, value]) => value !== undefined && value !== "")) as AiOperationIntentSource;
}

function isFrontendApiOperationId(operationId: string): operationId is ParaDevFrontendApiOperationId {
  return (PARADEV_FRONTEND_API_OPERATION_IDS as readonly string[]).includes(operationId);
}

function aiChatModuleDraftNavigationFamilyId(
  sources: readonly ParaDevAiChatSource[],
  activeModule: string,
  featureModules: readonly Pick<FeatureModule, "id">[]
): string {
  const candidateFamilies = [
    ...sources.flatMap((source) => [source.familyId ?? "", source.moduleId ?? ""]),
    activeModule,
    featureModules[0]?.id ?? ""
  ]
    .map((familyId) => canonicalFamilyId(familyId))
    .filter(Boolean);
  const featureModule = candidateFamilies
    .map((candidate) => featureModules.find((module) => canonicalFamilyId(module.id) === candidate))
    .find((module): module is Pick<FeatureModule, "id"> => Boolean(module));
  return featureModule?.id ?? candidateFamilies[0] ?? "";
}

function moduleSelectionTargetsEqual(left: WorkspaceModuleSelectionTarget | null, right: WorkspaceModuleSelectionTarget | null): boolean {
  return (
    (left?.entityId ?? "") === (right?.entityId ?? "") &&
    (left?.familyId ?? "") === (right?.familyId ?? "") &&
    left?.sourceContent === right?.sourceContent &&
    (left?.sourcePath ?? "") === (right?.sourcePath ?? "")
  );
}

const AI_CHAT_TEMPLATE_LIMIT = 12;
const AI_CHAT_DIAGNOSTIC_LIMIT = 8;

function aiChatProjectWorkspaceSources(browser: ProjectBrowserPayload | null, t: Translator): ParaDevAiChatSource[] {
  if (!browser) {
    return [];
  }
  const label = browser.title || browser.project_id;
  const content = t("chat.context.project.summary", {
    families: String(browser.families.length),
    project: label,
    rows: String(aiChatProjectRowCount(browser))
  });
  return [
    {
      id: "workspace:project",
      kind: "workspace",
      label,
      content,
      contentChars: content.length,
      truncated: false
    }
  ];
}

function aiChatProjectRowCount(browser: ProjectBrowserPayload): number {
  const familyItemTotal = browser.families.reduce((total, family) => {
    const itemCount = Number.isFinite(family.item_count) ? Math.max(0, family.item_count) : 0;
    return total + itemCount;
  }, 0);
  return familyItemTotal > 0 || browser.items.length === 0 ? familyItemTotal : browser.items.length;
}

function aiChatTemplateSources(templates: ProjectTemplatesPayload | null, t: Translator): ParaDevAiChatSource[] {
  const templateRows = templates?.templates ?? [];
  if (templateRows.length === 0) {
    return [];
  }
  const content = aiChatTemplatesContent(templateRows, t);
  return [
    {
      id: "templates:project",
      kind: "templates",
      label: t("chat.source.templates", { count: String(templateRows.length) }),
      content,
      contentChars: content.length,
      truncated: templateRows.length > AI_CHAT_TEMPLATE_LIMIT
    }
  ];
}

function aiChatTemplatesContent(templates: ProjectTemplate[], t: Translator): string {
  const rows = templates.slice(0, AI_CHAT_TEMPLATE_LIMIT).map((template, index) => {
    const title = compactTemplateText(template.title || template.id);
    const family = compactTemplateText(template.family || "module");
    const source = compactTemplateText(template.source || "project");
    const fileCount = template.files?.length ?? 0;
    const files = t(fileCount === 1 ? "chat.context.template.file" : "chat.context.template.files", { count: String(fileCount) });
    const familyLabel = t("chat.context.template.family");
    const sourceLabel = t("chat.context.template.source");
    const argsLabel = t("chat.context.template.args");
    return `${index + 1}. ${template.id} - ${title} (${familyLabel}: ${family}, ${sourceLabel}: ${source}, ${files}, ${argsLabel}: ${aiChatTemplateArgs(template, t)})`;
  });
  if (templates.length > AI_CHAT_TEMPLATE_LIMIT) {
    rows.push(t("chat.context.templates.omitted", { count: String(templates.length - AI_CHAT_TEMPLATE_LIMIT) }));
  }
  return rows.join("\n");
}

function aiChatTemplateArgs(template: ProjectTemplate, t: Translator): string {
  const entries = Object.entries(template.args ?? {});
  if (entries.length === 0) {
    return t("chat.context.none");
  }
  return entries
    .map(([name, arg]) => {
      const parts = [name];
      if (arg.required) {
        parts.push(t("chat.context.template.required"));
      }
      const defaultValue = compactTemplateText(arg.default);
      if (defaultValue) {
        parts.push(t("chat.context.template.default", { value: defaultValue }));
      }
      if (arg.choices?.length) {
        parts.push(t("chat.context.template.choices", { choices: arg.choices.map(compactTemplateText).join("/") }));
      }
      return parts.join(" ");
    })
    .join("; ");
}

function compactTemplateText(value: unknown): string {
  return templateScalarText(value).replace(/\s+/g, " ").trim();
}

function aiChatDiagnosticsSources(browser: ProjectBrowserPayload | null, t: Translator): ParaDevAiChatSource[] {
  const diagnostics = browser?.diagnostics ?? [];
  if (diagnostics.length === 0) {
    return [];
  }
  const content = aiChatDiagnosticsContent(diagnostics, t);
  return [
    {
      id: "diagnostics:project",
      kind: "diagnostics",
      label: t("chat.source.diagnostics", { count: String(diagnostics.length) }),
      content,
      contentChars: content.length,
      truncated: diagnostics.length > AI_CHAT_DIAGNOSTIC_LIMIT
    }
  ];
}

function aiChatDiagnosticsContent(diagnostics: Array<Record<string, unknown>>, t: Translator): string {
  const rows = diagnostics.slice(0, AI_CHAT_DIAGNOSTIC_LIMIT).map((diagnostic, index) => {
    const severity = diagnosticField(diagnostic, "severity") || diagnosticField(diagnostic, "level") || t("chat.context.diagnostics.defaultSeverity");
    const code = diagnosticField(diagnostic, "code");
    const path =
      diagnosticField(diagnostic, "path") ||
      diagnosticField(diagnostic, "source_path") ||
      diagnosticField(diagnostic, "sourcePath") ||
      diagnosticField(diagnostic, "relative_path");
    const message = diagnosticField(diagnostic, "message") || diagnosticField(diagnostic, "detail") || code || t("chat.context.diagnostics.noMessage");
    const prefix = code ? `${severity} ${code}` : severity;
    return `${index + 1}. [${prefix}] ${path ? `${path}: ` : ""}${message}`;
  });
  if (diagnostics.length > AI_CHAT_DIAGNOSTIC_LIMIT) {
    rows.push(t("chat.context.diagnostics.omitted", { count: String(diagnostics.length - AI_CHAT_DIAGNOSTIC_LIMIT) }));
  }
  return rows.join("\n");
}

function diagnosticField(diagnostic: Record<string, unknown>, key: string): string {
  const value = diagnostic[key];
  return typeof value === "string" ? value.trim() : "";
}

export function scopedBrowserKey(projectRoot: string, scope: ProjectBrowserScope | null): string {
  return [projectRoot, scope?.family ?? "", scope?.moduleId ?? "", scope?.collectionId ?? ""].join("::");
}

export function claimSourceBrowserFallbackCheck(
  claimedKeys: Set<string>,
  key: string
): boolean {
  if (!key || claimedKeys.has(key)) {
    return false;
  }
  claimedKeys.add(key);
  return true;
}

export function isWorkspaceTabBrowserLoading(tab: WorkspaceTab | null, projectRoot: string, loadingByKey: Record<string, boolean>, browser: ProjectBrowserPayload | null): boolean {
  const scope = browserScopeForWorkspaceTab(tab, browser);
  if (!scope || !projectRoot) {
    return false;
  }
  return Boolean(loadingByKey[scopedBrowserKey(projectRoot, scope)]);
}

export function scopedBrowserErrorForWorkspaceTab(tab: WorkspaceTab | null, projectRoot: string, errorByKey: Record<string, string>, browser: ProjectBrowserPayload | null): string | null {
  const scope = browserScopeForWorkspaceTab(tab, browser);
  if (!scope || !projectRoot || browserHasScopedPayload(browser, scope)) {
    return null;
  }
  const error = errorByKey[scopedBrowserKey(projectRoot, scope)]?.trim();
  return error ? error : null;
}

export function scopedBrowserLoadErrorDetail(t: Translator, error: unknown): string {
  return t("workspace.module.loadFailed.body", { message: localizedParaDevServiceError(t, error) });
}

export function aiChatProfileLoadErrorDetail(t: Translator, error: unknown): string {
  return t("chat.profileLoadFailed", { message: localizedParaDevServiceError(t, error) });
}

export function pathStatusLoadErrorDetail(t: Translator, error: unknown): string {
  return t("config.projects.pathStatus.title.failed", { message: localizedParaDevServiceError(t, error) });
}

export function browserHasScopedPayload(browser: ProjectBrowserPayload | null, scope: ProjectBrowserScope | null): boolean {
  if (!browser || !scope?.family) {
    return false;
  }
  const familyId = workspaceFamilyIdForFamily(browser, scope.family);
  if (scope.moduleId) {
    return browser.items.some((item) => item.module_id === scope.moduleId || item.id === scope.moduleId);
  }
  if (scope.collectionId) {
    return browser.items.some((item) => item.collection_id === scope.collectionId || item.id === scope.collectionId);
  }
  return browser.items.some((item) => canonicalFamilyId(item.family_id, item.family) === familyId);
}

export function shouldCommitScopedBrowserPayload(
  payload: ProjectBrowserPayload,
  requestedProjectRoot: string,
  activeProjectRoot: string,
  refreshGeneration: number,
  latestRefreshGeneration: number
): boolean {
  const requestedRoot = requestedProjectRoot.trim();
  const activeRoot = activeProjectRoot.trim();
  return shouldCommitProjectRefresh(refreshGeneration, latestRefreshGeneration) && requestedRoot !== "" && activeRoot === requestedRoot && payload.root === requestedRoot;
}

export function projectBrowserBaseForRefresh(
  projectRoot: string,
  cachedBrowser: ProjectBrowserPayload | null,
  currentState: DesktopStatePayload | null
): ProjectBrowserPayload | null {
  if (isUnfilteredProjectBrowserPayload(cachedBrowser) && cachedBrowser.root === projectRoot) {
    return cachedBrowser;
  }
  const currentBrowser = currentState?.browser;
  return currentState?.active_project?.root === projectRoot && isUnfilteredProjectBrowserPayload(currentBrowser) && currentBrowser.root === projectRoot
    ? currentBrowser
    : null;
}

export function mergeProjectBrowserPayloadsForProject(projectRoot: string, ...payloads: Array<ProjectBrowserPayload | null | undefined>): ProjectBrowserPayload | null {
  const root = projectRoot.trim();
  if (!root) {
    return mergeProjectBrowserPayloads(...payloads);
  }
  return mergeProjectBrowserPayloads(...payloads.filter((payload) => !payload || payload.root === root));
}

export function mergeProjectBrowserPayloads(...payloads: Array<ProjectBrowserPayload | null | undefined>): ProjectBrowserPayload | null {
  const activePayloads = payloads.filter((payload): payload is ProjectBrowserPayload => Boolean(payload));
  if (activePayloads.length === 0) {
    return null;
  }
  const first = activePayloads[0];
  const familiesByKey = new Map<string, ProjectBrowserPayload["families"][number]>();
  const itemsById = new Map<string, ProjectBrowserPayload["items"][number]>();
  const diagnostics: ProjectBrowserPayload["diagnostics"] = [];
  for (const payload of activePayloads) {
    const payloadFamilyKeys = projectBrowserReplacementFamilyKeys(payload);
    for (const key of payloadFamilyKeys) {
      for (const [itemId, item] of itemsById) {
        if (canonicalFamilyId(item.family_id, item.family) === key) {
          itemsById.delete(itemId);
        }
      }
    }
    for (const family of payload.families) {
      const familyKey = canonicalFamilyId(family.id, family.family);
      if (payloadFamilyKeys.has(familyKey)) {
        familiesByKey.set(familyKey, family);
      }
    }
    for (const item of payload.items) {
      itemsById.set(item.id, item);
    }
    diagnostics.push(...payload.diagnostics);
  }
  return {
    ...first,
    families: [...familiesByKey.values()],
    items: [...itemsById.values()],
    diagnostics
  };
}

function projectBrowserReplacementFamilyKeys(
  payload: ProjectBrowserPayload
): Set<string> {
  if (Object.keys(payload.filters).length === 0) {
    return new Set(
      payload.families.map((family) =>
        canonicalFamilyId(family.id, family.family)
      )
    );
  }
  const requestedFamily = payload.filters.family?.trim() ?? "";
  const discovered = requestedFamily
    ? projectBrowserFamily(payload, requestedFamily)
    : undefined;
  if (discovered) {
    return new Set([canonicalFamilyId(discovered.id, discovered.family)]);
  }
  const itemFamilies = new Set(
    payload.items.map((item) =>
      canonicalFamilyId(item.family_id, item.family)
    )
  );
  if (itemFamilies.size > 0) {
    return itemFamilies;
  }
  return requestedFamily
    ? new Set([canonicalFamilyId(requestedFamily)])
    : new Set();
}

function removeScopedBrowserLoadingKey(current: Record<string, boolean>, key: string): Record<string, boolean> {
  if (!current[key]) {
    return current;
  }
  const next = { ...current };
  delete next[key];
  return next;
}

function removeScopedBrowserErrorKey(current: Record<string, string>, key: string): Record<string, string> {
  if (!current[key]) {
    return current;
  }
  const next = { ...current };
  delete next[key];
  return next;
}

function sdkFamilyForWorkspaceFamily(familyId: string, browser: ProjectBrowserPayload | null): string {
  const discovered = projectBrowserFamily(browser, familyId);
  if (discovered) {
    return discovered.family;
  }
  return familyId;
}

function aiChatFamilyLabel(familyId: string, browser: ProjectBrowserPayload | null, t: Translator): string {
  const titleKey = moduleTitleKeyForFamilyId(familyId, browser);
  if (titleKey) {
    return t(titleKey);
  }
  const discovered = projectBrowserFamily(browser, familyId);
  return discovered?.title || familyId;
}

function filterPanelOptions<T extends FeatureModule | PanelOption>(options: T[], query: string, t: Translator): T[] {
  const normalizedQuery = query.trim().toLowerCase();
  if (!normalizedQuery) {
    return options;
  }
  return options.filter((option) => {
    const title = option.titleKey ? t(option.titleKey) : option.label ?? option.id;
    return [option.id, title].some((value) => value.toLowerCase().includes(normalizedQuery));
  });
}

function moduleOrderKey(projectId: string) {
  return `${MODULE_ORDER_STORAGE_PREFIX}:${projectId}`;
}

function readInitialAppSettings(defaultProjectId: string, platform: OpenPathPlatform): AppSettingsPayload {
  const fallback = defaultAppSettings(defaultProjectId, platform);
  return normalizeAppSettings(readJsonStorageValue(APP_SETTINGS_STORAGE_KEY), fallback, platform, defaultProjectId);
}

export function applyDocumentLocale(documentLike: { documentElement: { lang: string } }, locale: Locale): void {
  documentLike.documentElement.lang = htmlLangForLocale(locale);
}

async function readPersistedAppSettings(defaultProjectId: string, platform: OpenPathPlatform): Promise<PersistedAppSettingsRead | null> {
  const fallback = readInitialAppSettings(defaultProjectId, platform);
  const config = await readAppConfig();
  const settings = config === null || config === undefined ? fallback : normalizeAppSettings(config, fallback, platform, defaultProjectId);
  const desktopConfigEntries = await Promise.all(PARADEV_DESKTOP_CONFIG_KEYS.map((key) => readDesktopConfigEntry(key)));
  const desktopConfigValues = Object.fromEntries(desktopConfigEntries.map((entry) => [entry.key, entry.value] as const)) as Partial<
    Record<DesktopConfigKey, unknown>
  >;
  const failedEntry = desktopConfigEntries.find((entry) => entry.error !== null);
  return {
    configLoadFailure: failedEntry ? configPersistenceLoadFailureStatus(failedEntry.key, failedEntry.error) : null,
    settings: {
      ...settings,
      configPage: applyDesktopConfigValuesToConfigPageSettings(settings.configPage, desktopConfigValues)
    }
  };
}

async function readDesktopConfigEntry(key: DesktopConfigKey): Promise<{ error: unknown | null; key: DesktopConfigKey; value: unknown }> {
  try {
    return { error: null, key, value: await readConfigValue(key) };
  } catch (error) {
    console.warn(`Failed to load ParaDev config value ${key}.`, error);
    return { error, key, value: undefined };
  }
}

function defaultAppSettings(defaultProjectId: string, platform: OpenPathPlatform): AppSettingsPayload {
  const legacyOrder = readModuleOrder(defaultProjectId);
  return {
    schema: APP_SETTINGS_SCHEMA,
    activeProjectId: defaultProjectId,
    activeProjectPath: "",
    chat: defaultChatSettings(),
    configPage: defaultConfigPageSettings(),
    theme: "light",
    locale: "zh",
    openTarget: readOpenTarget(platform),
    sidebars: {
      projectPanelOpen: true,
      inspectorOpen: false
    },
    moduleOrderByProject: legacyOrder.length > 0 ? { [defaultProjectId]: legacyOrder } : {},
    moduleDefaultsByProject: {}
  };
}

function normalizeAppSettings(value: unknown, fallback: AppSettingsPayload, platform: OpenPathPlatform, defaultProjectId: string): AppSettingsPayload {
  const record = isRecord(value) ? value : {};
  const sidebars = isRecord(record.sidebars) ? record.sidebars : {};
  const configPage = normalizeConfigPageSettings(record.configPage, fallback.configPage);
  const moduleDefaultsByProject = normalizeModuleDefaultsByProject(
    record.moduleDefaultsByProject,
    fallback.moduleDefaultsByProject,
    defaultProjectId,
    localModuleDefaultsForSettings(configPage)
  );
  return {
    schema: APP_SETTINGS_SCHEMA,
    activeProjectId: defaultProjectId,
    activeProjectPath: typeof record.activeProjectPath === "string" ? record.activeProjectPath.trim() : fallback.activeProjectPath,
    chat: normalizeChatSettings(record.chat, fallback.chat),
    configPage: configPageSettingsForProjectModuleDefaults(configPage, moduleDefaultsByProject, defaultProjectId),
    theme: isThemeName(record.theme) ? record.theme : fallback.theme,
    locale: isLocale(record.locale) ? record.locale : fallback.locale,
    openTarget: record.openTarget === undefined ? fallback.openTarget : normalizeOpenPathTarget(record.openTarget, platform),
    sidebars: {
      projectPanelOpen: typeof sidebars.projectPanelOpen === "boolean" ? sidebars.projectPanelOpen : fallback.sidebars.projectPanelOpen,
      inspectorOpen: typeof sidebars.inspectorOpen === "boolean" ? sidebars.inspectorOpen : fallback.sidebars.inspectorOpen
    },
    moduleOrderByProject: normalizeModuleOrderByProject(record.moduleOrderByProject, fallback.moduleOrderByProject),
    moduleDefaultsByProject
  };
}

function defaultChatSettings(): AiChatSettings {
  return {
    dock: "floating",
    open: false
  };
}

export function normalizeChatSettings(value: unknown, fallback: AiChatSettings = defaultChatSettings()): AiChatSettings {
  const record = isRecord(value) ? value : {};
  return {
    dock: record.dock === "side" || record.dock === "floating" ? record.dock : fallback.dock,
    open: typeof record.open === "boolean" ? record.open : false
  };
}

export function persistableAppSettingsPayload(settings: AppSettingsPayload): PersistableAppSettingsPayload {
  const { activeProjectId, configPage, moduleDefaultsByProject, ...payload } = settings;
  return {
    ...payload,
    moduleDefaultsByProject: moduleDefaultsByProjectForSettings(moduleDefaultsByProject, activeProjectId, configPage)
  };
}

export function configPageSettingsForProjectModuleDefaults(settings: ConfigPageSettings, moduleDefaultsByProject: ModuleDefaultsByProject, projectId: string): ConfigPageSettings {
  const rows = projectId ? moduleDefaultsByProject[projectId] ?? [] : [];
  const defaultsById = new Map(localModuleDefaultsForSettings(defaultConfigPageSettings()).map((row) => [row.id, row.value]));
  const valuesById = new Map(rows.map((row) => [row.id, row.value]));
  let changed = false;
  const moduleDefaults = settings.moduleDefaults.map((row) => {
    if (row.configKey) {
      return row;
    }
    const value = valuesById.get(row.id) ?? defaultsById.get(row.id);
    if (typeof value !== "number" || !Number.isFinite(value) || value < 1 || Math.round(value) === row.value) {
      return row;
    }
    changed = true;
    return { ...row, value: Math.round(value) };
  });
  return changed ? { ...settings, moduleDefaults } : settings;
}

function moduleDefaultsByProjectForSettings(moduleDefaultsByProject: ModuleDefaultsByProject, projectId: string, settings: ConfigPageSettings): ModuleDefaultsByProject {
  if (!projectId) {
    return moduleDefaultsByProject;
  }
  const rows = localModuleDefaultsForSettings(settings);
  if (moduleDefaultRowsEqual(moduleDefaultsByProject[projectId] ?? [], rows)) {
    return moduleDefaultsByProject;
  }
  return {
    ...moduleDefaultsByProject,
    [projectId]: rows
  };
}

function localModuleDefaultsForSettings(settings: ConfigPageSettings): PersistedModuleDefault[] {
  return settings.moduleDefaults.flatMap((row) => (row.configKey ? [] : [{ id: row.id, value: row.value }]));
}

function normalizeModuleDefaultsByProject(
  value: unknown,
  fallback: ModuleDefaultsByProject,
  legacyProjectId: string,
  legacyRows: PersistedModuleDefault[]
): ModuleDefaultsByProject {
  const next: ModuleDefaultsByProject = { ...fallback };
  let hasLegacyProjectRows = Array.isArray(next[legacyProjectId]) && next[legacyProjectId].length > 0;
  if (isRecord(value)) {
    for (const [projectId, rows] of Object.entries(value)) {
      const cleanProjectId = projectId.trim();
      if (!cleanProjectId) {
        continue;
      }
      const cleanRows = normalizePersistedModuleDefaultRows(rows);
      if (cleanRows.length === 0) {
        continue;
      }
      next[cleanProjectId] = cleanRows;
      hasLegacyProjectRows ||= cleanProjectId === legacyProjectId;
    }
  }
  if (!hasLegacyProjectRows && legacyRows.length > 0) {
    next[legacyProjectId] = legacyRows;
  }
  return next;
}

function normalizePersistedModuleDefaultRows(value: unknown): PersistedModuleDefault[] {
  if (!Array.isArray(value)) {
    return [];
  }
  const rowsById = new Map<string, PersistedModuleDefault>();
  for (const row of value) {
    if (!isRecord(row) || typeof row.id !== "string" || !row.id.trim()) {
      continue;
    }
    if (typeof row.value !== "number" || !Number.isFinite(row.value) || row.value < 1) {
      continue;
    }
    rowsById.set(row.id.trim(), { id: row.id.trim(), value: Math.round(row.value) });
  }
  return [...rowsById.values()];
}

function moduleDefaultRowsEqual(left: PersistedModuleDefault[], right: PersistedModuleDefault[]): boolean {
  if (left.length !== right.length) {
    return false;
  }
  return left.every((row, index) => row.id === right[index]?.id && row.value === right[index]?.value);
}

function configModuleDefaultValue(settings: ConfigPageSettings, id: string): number {
  return settings.moduleDefaults.find((row) => row.id === id)?.value ?? 1;
}

function configModuleDefaultsWithValue(rows: ConfigPageSettings["moduleDefaults"], id: string, value: number): ConfigPageSettings["moduleDefaults"] {
  return rows.map((row) => (row.id === id ? { ...row, value } : row));
}

function configProjectStatusPaths(project: ProjectOption, hoi4GameRoot: string): string[] {
  return Array.from(
    new Set(
      [project.path, ...(project.sourceRoots ?? []), buildOutputOpenPath(project), project.buildRoot, hoi4GameRoot]
        .map((path) => path?.trim() ?? "")
        .filter(Boolean)
    )
  );
}

function positiveConfigInteger(value: unknown, fallback: number): number {
  if (typeof value !== "number" || !Number.isFinite(value) || value < 1) {
    return fallback;
  }
  return Math.round(value);
}

function booleanConfig(value: unknown, fallback: boolean): boolean {
  return typeof value === "boolean" ? value : fallback;
}

function cliOutputConfig(value: unknown, fallback: ConfigPageSettings["cli"]["output"]): ConfigPageSettings["cli"]["output"] {
  return typeof value === "string" && CONFIG_CLI_OUTPUT_VALUES.includes(value as ConfigPageSettings["cli"]["output"])
    ? (value as ConfigPageSettings["cli"]["output"])
    : fallback;
}

function errorDetail(error: unknown, t?: Translator): string {
  if (t) {
    return localizedParaDevServiceError(t, error);
  }
  return error instanceof Error ? error.message : String(error);
}

function hoi4LaunchModeConfig(value: unknown, fallback: ConfigPageSettings["hoi4"]["launchMode"]): ConfigPageSettings["hoi4"]["launchMode"] {
  return typeof value === "string" && CONFIG_HOI4_LAUNCH_MODE_VALUES.includes(value as ConfigPageSettings["hoi4"]["launchMode"])
    ? (value as ConfigPageSettings["hoi4"]["launchMode"])
    : fallback;
}

function aiPresetConfig(value: unknown, fallback: string): string {
  return typeof value === "string" && CONFIG_AI_PRESET_VALUES.includes(value.trim()) ? value.trim() : fallback;
}

function aiChatRoleConfig(value: unknown, fallback: string): string {
  return aiTextConfig(value, fallback);
}

function aiTextConfig(value: unknown, fallback: string): string {
  return typeof value === "string" && value.trim().length > 0 ? value.trim() : fallback;
}

function optionalConfigText(value: unknown, fallback: string): string {
  return typeof value === "string" ? value.trim() : fallback;
}

function normalizeModuleOrderByProject(value: unknown, fallback: Record<string, string[]>): Record<string, string[]> {
  const next: Record<string, string[]> = { ...fallback };
  if (!isRecord(value)) {
    return next;
  }
  for (const [projectId, order] of Object.entries(value)) {
    if (!projectId.trim() || !Array.isArray(order)) {
      continue;
    }
    const cleanOrder = order.filter((item): item is string => typeof item === "string" && item.trim().length > 0);
    if (cleanOrder.length > 0) {
      next[projectId] = cleanOrder;
    }
  }
  return next;
}

function readModuleOrder(projectId: string): string[] {
  const stored = readStorageValue(moduleOrderKey(projectId));
  if (!stored) {
    return [];
  }
  try {
    const parsed = JSON.parse(stored);
    return Array.isArray(parsed) ? parsed.filter((value): value is string => typeof value === "string" && value.length > 0) : [];
  } catch {
    return [];
  }
}

function readOpenTarget(platform: OpenPathPlatform): OpenPathTarget {
  const stored = readStorageValue(OPEN_TARGET_STORAGE_KEY);
  if (stored === "default") {
    return normalizeOpenPathTarget(null, platform);
  }
  return normalizeOpenPathTarget(stored, platform);
}

function isThemeName(value: unknown): value is ThemeName {
  return value === "light" || value === "dark" || value === "anthropic";
}

function isLocale(value: unknown): value is Locale {
  return value === "en" || value === "zh";
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function readJsonStorageValue(key: string): unknown {
  const stored = readStorageValue(key);
  if (!stored) {
    return null;
  }
  try {
    return JSON.parse(stored);
  } catch {
    return null;
  }
}

function readStorageValue(key: string): string | null {
  if (typeof window === "undefined") {
    return null;
  }
  try {
    return window.localStorage.getItem(key);
  } catch {
    return null;
  }
}

function writeStorageValue(key: string, value: string) {
  if (typeof window === "undefined") {
    return;
  }
  try {
    window.localStorage.setItem(key, value);
  } catch {
    // Local persistence is best-effort in restricted webviews.
  }
}
