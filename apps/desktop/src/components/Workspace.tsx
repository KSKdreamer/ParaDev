import { lazy, Suspense, useCallback, useMemo, useState } from "react";
import { AlertTriangle, CheckCircle2, CircleDashed, Columns2, FolderOpen, GitBranch, PanelTopOpen, SplitSquareHorizontal, X } from "lucide-react";
import type { BuildTarget } from "../buildPage/buildPageModel";
import { localizedParaDevServiceError } from "../desktopBridgeErrors";
import type { Locale, TranslationKey, Translator } from "../i18n";
import { diagramTabIdForModule, moduleIdForDiagramTabId, moduleTitleKeyForFamilyId, projectBrowserFamily, projectBrowserForFamily, projectDiagramTitleKeyForFamilyId, supportsProjectDiagramFamily } from "../projectModules";
import { openProjectPath, type DesktopPathStatusPayload, type OpenPathTarget, type ParaDevAiChatProfile, type ParaDevAiChatProfileWrite, type ParaDevAiChatSourceKindRow } from "../services/paradev";
import type { FeatureModule, ModuleCreateIntent, ModuleStatus, ProjectBrowserPayload, ProjectOption, ProjectTemplatesPayload, SurfaceRow, ThemeName, WorkspaceModuleSelectionTarget, WorkspaceTab } from "../types";
import { ConfigPage } from "../configPage/ConfigPage";
import type { ConfigDependencyStatus, ConfigLlmStatus, ConfigPageSettings, ConfigPersistenceStatus } from "../configPage/model";
import {
  moduleEditorSessionKey,
  type ModuleEditorSessionStore
} from "../moduleEditor/editorSessionStore";
import { IconButton } from "./ui/IconButton";
import { SelectField } from "./ui/SelectField";

const ModuleEditor = lazy(() => import("../moduleEditor/ModuleEditor").then((module) => ({ default: module.ModuleEditor })));

const statusKey: Record<ModuleStatus, TranslationKey> = {
  ready: "status.ready",
  scaffold: "status.scaffold",
  planned: "status.planned",
  offline: "status.offline"
};

type WorkspaceProps = {
  activeBrowserError?: string | null;
  activeBrowserLoading?: boolean;
  activeFeature: FeatureModule;
  aiChatDefaultRole: string;
  aiChatProfileLoadError?: string | null;
  aiChatProfiles: ParaDevAiChatProfile[];
  aiChatSourceKindRows?: ParaDevAiChatSourceKindRow[];
  aiChatSourceKinds?: string[];
  activeTab: string;
  activeWorkspaceTab: WorkspaceTab | null;
  browser: ProjectBrowserPayload | null;
  configPageSettings: ConfigPageSettings;
  configPersistenceStatus?: ConfigPersistenceStatus;
  dependencyBusyId: string;
  dependencyStatusById: Record<string, ConfigDependencyStatus>;
  inspectorOpen: boolean;
  locale: Locale;
  llmStatus: ConfigLlmStatus | null;
  pagePlaceholder?: WorkspacePagePlaceholder | null;
  onCloseTab: (id: string) => void;
  onBuildTarget?: (target: BuildTarget) => void;
  onProjectRefresh: (projectRoot?: string, fallbackProjectId?: string) => Promise<void>;
  onProjectPreferredLanguageChange?: (preferredLanguage: string) => void | Promise<void>;
  onOpenDiagramTab?: (id: string) => void;
  onOpenPath: (path: string) => void;
  onOpenModuleEntity?: (target: WorkspaceModuleSelectionTarget) => void;
  onModuleSelectionTargetChange?: (target: WorkspaceModuleSelectionTarget | null) => void;
  onCheckDependency: (id: string) => void;
  onConfigPageSettingsChange: (settings: ConfigPageSettings) => void;
  onInstallDependency: (id: string) => void;
  onSplitToggle: () => void;
  onTestLlm: () => void;
  onTabPin: (id: string) => void;
  onTabSelect: (id: string) => void;
  moduleCreateIntent?: ModuleCreateIntent | null;
  onModuleCreateIntentConsumed?: (nonce: number) => void;
  moduleSelectionTarget?: WorkspaceModuleSelectionTarget | null;
  openTarget: OpenPathTarget;
  pathStatusByPath?: Record<string, DesktopPathStatusPayload>;
  pathStatusErrorByPath?: Record<string, string>;
  openTabs: WorkspaceTab[];
  activeProject: ProjectOption;
  onLocaleChange: (locale: Locale) => void;
  onOpenTargetChange: (target: OpenPathTarget) => void;
  onThemeChange: (theme: ThemeName) => void;
  onResetAiChatProfile: (profileId: string) => void;
  onSaveAiChatProfile: (profileId: string, profile: ParaDevAiChatProfileWrite) => void;
  projectOptions: ProjectOption[];
  projectLanguageBusy?: boolean;
  projectLanguageError?: string;
  secondaryTab: string;
  secondaryBrowserError?: string | null;
  secondaryBrowserLoading?: boolean;
  secondaryWorkspaceTab: WorkspaceTab | null;
  sessionStore?: ModuleEditorSessionStore;
  setSecondaryTab: (id: string) => void;
  splitView: boolean;
  surfaceRows: SurfaceRow[];
  templates: ProjectTemplatesPayload | null;
  t: Translator;
  theme: ThemeName;
};

export type WorkspacePagePlaceholder = {
  body: string;
  title: string;
};

export function Workspace({
  activeBrowserError = null,
  activeBrowserLoading = false,
  activeFeature,
  aiChatDefaultRole,
  aiChatProfileLoadError = null,
  aiChatProfiles,
  aiChatSourceKindRows = [],
  aiChatSourceKinds = [],
  activeProject,
  activeTab,
  activeWorkspaceTab,
  browser,
  configPageSettings,
  configPersistenceStatus,
  dependencyBusyId,
  dependencyStatusById,
  inspectorOpen,
  locale,
  llmStatus,
  pagePlaceholder,
  onCheckDependency,
  onBuildTarget,
  onCloseTab,
  onConfigPageSettingsChange,
  onInstallDependency,
  onOpenDiagramTab,
  onOpenPath,
  onOpenModuleEntity,
  onModuleSelectionTargetChange,
  onLocaleChange,
  onOpenTargetChange,
  onProjectRefresh,
  onProjectPreferredLanguageChange,
  onResetAiChatProfile,
  onSaveAiChatProfile,
  onTestLlm,
  onSplitToggle,
  onTabPin,
  onTabSelect,
  onThemeChange,
  moduleCreateIntent = null,
  onModuleCreateIntentConsumed,
  moduleSelectionTarget,
  openTarget,
  pathStatusByPath,
  pathStatusErrorByPath,
  openTabs,
  projectOptions,
  projectLanguageBusy,
  projectLanguageError,
  secondaryTab,
  secondaryBrowserError = null,
  secondaryBrowserLoading = false,
  secondaryWorkspaceTab,
  sessionStore,
  setSecondaryTab,
  splitView,
  surfaceRows,
  templates,
  t,
  theme
}: WorkspaceProps) {
  const splitDisabled = openTabs.length < 2;
  const activeProjectRoot = activeProject?.path ?? browser?.root ?? "";
  const [moduleBatchRecoveryPathsByProject, setModuleBatchRecoveryPathsByProject] =
    useState<Record<string, string[]>>({});
  const [
    moduleBatchRecoveryOpenErrorsByProject,
    setModuleBatchRecoveryOpenErrorsByProject
  ] = useState<Record<string, string>>({});
  const handleModuleBatchRecoveryPathsChange = useCallback(
    (projectRoot: string, paths: string[]) => {
      if (!projectRoot) {
        return;
      }
      setModuleBatchRecoveryPathsByProject((current) => {
        if (paths.length > 0) {
          return { ...current, [projectRoot]: paths };
        }
        if (!Object.hasOwn(current, projectRoot)) {
          return current;
        }
        const next = { ...current };
        delete next[projectRoot];
        return next;
      });
    },
    []
  );
  const activeModuleBatchRecoveryPaths =
    moduleBatchRecoveryPathsByProject[activeProjectRoot] ?? [];
  const activeModuleBatchRecoveryOpenError =
    moduleBatchRecoveryOpenErrorsByProject[activeProjectRoot] ?? "";
  const handleModuleBatchRecoveryPathOpen = useCallback(
    async (path: string) => {
      const projectRoot = activeProjectRoot;
      setModuleBatchRecoveryOpenErrorsByProject((current) => ({
        ...current,
        [projectRoot]: ""
      }));
      try {
        await openProjectPath(path, openTarget);
      } catch (cause: unknown) {
        setModuleBatchRecoveryOpenErrorsByProject((current) => ({
          ...current,
          [projectRoot]: localizedParaDevServiceError(t, cause)
        }));
      }
    },
    [activeProjectRoot, openTarget, t]
  );

  return (
    <section className={inspectorOpen ? "workspace-grid inspector-visible" : "workspace-grid inspector-collapsed"} aria-label={t("workspace.aria")}>
      <div
        className={
          activeModuleBatchRecoveryPaths.length > 0 && !pagePlaceholder
            ? "workspace-primary recovery-visible"
            : "workspace-primary"
        }
      >
        {pagePlaceholder ? (
          <div className="workspace-empty page-placeholder">
            <span className="panel-icon">
              <SplitSquareHorizontal aria-hidden="true" size={18} />
            </span>
            <h2>{pagePlaceholder.title}</h2>
            <p>{pagePlaceholder.body}</p>
          </div>
        ) : (
          <>
            <div className="tab-strip" role="tablist" aria-label={t("workspace.tabs.aria")}>
              <div className="tab-list">
                {openTabs.map((tab) => {
                  const tabTitle = workspaceTabTitle(tab, t, browser);
                  const tabTooltip = tab.pinned ? tabTitle : t("workspace.tabs.previewTitle", { title: tabTitle });
                  const classes = ["tab", tab.kind === "diagram" ? "diagram-tab" : "", tab.id === activeTab ? "selected" : "", tab.pinned ? "pinned" : "preview"].filter(Boolean).join(" ");
                  return (
                    <div className={classes} key={tab.id} role="presentation">
                      <button
                        aria-label={tab.dirty ? t("workspace.tabs.unsaved", { title: tabTitle }) : undefined}
                        aria-selected={tab.id === activeTab}
                        className="tab-main"
                        data-tab-kind={tab.kind}
                        onClick={() => onTabSelect(tab.id)}
                        onDoubleClick={() => onTabPin(tab.id)}
                        role="tab"
                        title={tabTooltip}
                        type="button"
                      >
                        {tab.kind === "diagram" ? <GitBranch aria-hidden="true" className="tab-kind-icon" size={13} /> : null}
                        {tab.dirty ? <span aria-hidden="true" className="tab-dirty-indicator" /> : null}
                        <strong>{tabTitle}</strong>
                      </button>
                      <button aria-label={t("workspace.action.closeTab", { title: tabTitle })} className="tab-close" onClick={() => onCloseTab(tab.id)} title={t("workspace.action.closeTab", { title: tabTitle })} type="button">
                        <X aria-hidden="true" size={13} />
                      </button>
                    </div>
                  );
                })}
              </div>
              <div className="tab-actions">
                <IconButton
                  disabled={splitDisabled}
                  label={splitDisabled ? t("workspace.action.splitDisabled") : splitView ? t("workspace.action.closeSplit") : t("workspace.action.splitRight")}
                  onClick={onSplitToggle}
                  selected={splitView}
                >
                  <Columns2 aria-hidden="true" size={15} />
                </IconButton>
              </div>
            </div>

            {activeModuleBatchRecoveryPaths.length > 0 ? (
              <section
                className="module-batch-recovery module-batch-workspace-recovery"
                role="alert"
              >
                <div>
                  <AlertTriangle aria-hidden="true" size={18} />
                  <span>
                    <strong>{t("workspace.module.editor.batch.recoveryTitle")}</strong>
                    <small>{t("workspace.module.editor.batch.recoveryDetail")}</small>
                  </span>
                  <button
                    className="toolbar-button subtle module-batch-recovery-dismiss"
                    onClick={() => {
                      handleModuleBatchRecoveryPathsChange(activeProjectRoot, []);
                      setModuleBatchRecoveryOpenErrorsByProject((current) => ({
                        ...current,
                        [activeProjectRoot]: ""
                      }));
                    }}
                    type="button"
                  >
                    {t("workspace.module.editor.batch.dismissRecovery")}
                  </button>
                </div>
                <ul>
                  {activeModuleBatchRecoveryPaths.map((path) => (
                    <li key={path}>
                      <code title={path}>{path}</code>
                      <button
                        className="toolbar-button subtle"
                        onClick={() => void handleModuleBatchRecoveryPathOpen(path)}
                        type="button"
                      >
                        <FolderOpen aria-hidden="true" size={13} />
                        {t("workspace.module.editor.batch.openRecovery")}
                      </button>
                    </li>
                  ))}
                </ul>
                {activeModuleBatchRecoveryOpenError ? (
                  <small className="module-batch-recovery-error">
                    {activeModuleBatchRecoveryOpenError}
                  </small>
                ) : null}
              </section>
            ) : null}

            {activeWorkspaceTab ? (
              <div className={splitView && secondaryWorkspaceTab ? "workspace-split split-visible" : "workspace-split"}>
                <WorkspacePane
                  activeFeature={activeFeature}
                  activeProject={activeProject}
                  aiChatDefaultRole={aiChatDefaultRole}
                  aiChatProfileLoadError={aiChatProfileLoadError}
                  aiChatProfiles={aiChatProfiles}
                  aiChatSourceKindRows={aiChatSourceKindRows}
                  aiChatSourceKinds={aiChatSourceKinds}
                  browser={browser}
                  browserError={activeBrowserError}
                  browserLoading={activeBrowserLoading}
                  configPageSettings={configPageSettings}
                  configPersistenceStatus={configPersistenceStatus}
                  dependencyBusyId={dependencyBusyId}
                  dependencyStatusById={dependencyStatusById}
                  locale={locale}
                  llmStatus={llmStatus}
                  moduleBatchRecoveryPathsByProject={moduleBatchRecoveryPathsByProject}
                  moduleCreateIntent={moduleCreateIntent}
                  onModuleCreateIntentConsumed={onModuleCreateIntentConsumed}
                  moduleSelectionTarget={moduleSelectionTarget}
                  onCheckDependency={onCheckDependency}
                  onBuildTarget={onBuildTarget}
                  onConfigPageSettingsChange={onConfigPageSettingsChange}
                  onInstallDependency={onInstallDependency}
                  onLocaleChange={onLocaleChange}
                  onPinTab={() => onTabPin(activeWorkspaceTab.id)}
                  onOpenDiagramTab={onOpenDiagramTab}
                  onOpenPath={onOpenPath}
                  onOpenModuleEntity={onOpenModuleEntity}
                  onModuleSelectionTargetChange={onModuleSelectionTargetChange}
                  onModuleBatchRecoveryPathsChange={handleModuleBatchRecoveryPathsChange}
                  onOpenTargetChange={onOpenTargetChange}
                  onProjectRefresh={onProjectRefresh}
                  onProjectPreferredLanguageChange={onProjectPreferredLanguageChange}
                  onResetAiChatProfile={onResetAiChatProfile}
                  onSaveAiChatProfile={onSaveAiChatProfile}
                  onTestLlm={onTestLlm}
                  onThemeChange={onThemeChange}
                  openTarget={openTarget}
                  pathStatusByPath={pathStatusByPath}
                  pathStatusErrorByPath={pathStatusErrorByPath}
                  paneLabel={t("workspace.primary")}
                  projectOptions={projectOptions}
                  projectLanguageBusy={projectLanguageBusy}
                  projectLanguageError={projectLanguageError}
                  sessionStore={sessionStore}
                  surfaceRows={surfaceRows}
                  tab={activeWorkspaceTab}
                  templates={templates}
                  t={t}
                  theme={theme}
                />
                {splitView && secondaryWorkspaceTab ? (
                  <div className="workspace-pane secondary-pane">
                    <div className="secondary-tab-select">
                      <span>
                        <PanelTopOpen aria-hidden="true" size={15} />
                        {t("workspace.split.label")}
                      </span>
                      <SelectField
                        className="split-select"
                        label={t("workspace.split.tabAria")}
                        onChange={(event) => setSecondaryTab(event.target.value)}
                        options={openTabs
                          .filter((tab) => tab.id !== activeTab)
                          .map((tab) => ({ label: workspaceTabTitle(tab, t, browser), value: tab.id }))}
                        value={secondaryTab}
                        variant="compact"
                      />
                    </div>
                    <WorkspacePane
                      activeFeature={activeFeature}
                      activeProject={activeProject}
                      aiChatDefaultRole={aiChatDefaultRole}
                      aiChatProfileLoadError={aiChatProfileLoadError}
                      aiChatProfiles={aiChatProfiles}
                      aiChatSourceKindRows={aiChatSourceKindRows}
                      aiChatSourceKinds={aiChatSourceKinds}
                      browser={browser}
                      browserError={secondaryBrowserError}
                      browserLoading={secondaryBrowserLoading}
                      configPageSettings={configPageSettings}
                      configPersistenceStatus={configPersistenceStatus}
                      dependencyBusyId={dependencyBusyId}
                      dependencyStatusById={dependencyStatusById}
                      locale={locale}
                      llmStatus={llmStatus}
                      moduleBatchRecoveryPathsByProject={moduleBatchRecoveryPathsByProject}
                      moduleSelectionTarget={moduleSelectionTarget}
                      onCheckDependency={onCheckDependency}
                      onBuildTarget={onBuildTarget}
                      onConfigPageSettingsChange={onConfigPageSettingsChange}
                      onInstallDependency={onInstallDependency}
                      onLocaleChange={onLocaleChange}
                      onPinTab={() => onTabPin(secondaryWorkspaceTab.id)}
                      onOpenDiagramTab={onOpenDiagramTab}
                      onOpenPath={onOpenPath}
                      onOpenModuleEntity={onOpenModuleEntity}
                      onModuleSelectionTargetChange={onModuleSelectionTargetChange}
                      onModuleBatchRecoveryPathsChange={handleModuleBatchRecoveryPathsChange}
                      onOpenTargetChange={onOpenTargetChange}
                      onProjectRefresh={onProjectRefresh}
                      onProjectPreferredLanguageChange={onProjectPreferredLanguageChange}
                      onResetAiChatProfile={onResetAiChatProfile}
                      onSaveAiChatProfile={onSaveAiChatProfile}
                      onTestLlm={onTestLlm}
                      onThemeChange={onThemeChange}
                      openTarget={openTarget}
                      pathStatusByPath={pathStatusByPath}
                      pathStatusErrorByPath={pathStatusErrorByPath}
                      paneLabel={t("workspace.secondary")}
                      projectOptions={projectOptions}
                      projectLanguageBusy={projectLanguageBusy}
                      projectLanguageError={projectLanguageError}
                      sessionStore={sessionStore}
                      surfaceRows={surfaceRows}
                      tab={secondaryWorkspaceTab}
                      templates={templates}
                      t={t}
                      theme={theme}
                    />
                  </div>
                ) : null}
              </div>
            ) : (
              <div className="workspace-empty">
                <span className="panel-icon">
                  <SplitSquareHorizontal aria-hidden="true" size={18} />
                </span>
                <h2>{t("workspace.empty.title")}</h2>
                <p>{t("workspace.empty.line")}</p>
              </div>
            )}
          </>
        )}
      </div>

      <aside aria-hidden={!inspectorOpen} className={inspectorOpen ? "inspector" : "inspector collapsed"} inert={!inspectorOpen} aria-label={t("panel.inspector.aria")}>
        <div className="inspector-header">
          <p className="label">{t("inspector.label")}</p>
        </div>
        <div className="inspector-stack" />
      </aside>
    </section>
  );
}

type WorkspacePaneProps = {
  activeFeature: FeatureModule;
  activeProject: ProjectOption;
  aiChatDefaultRole: string;
  aiChatProfileLoadError?: string | null;
  aiChatProfiles: ParaDevAiChatProfile[];
  aiChatSourceKindRows?: ParaDevAiChatSourceKindRow[];
  aiChatSourceKinds?: string[];
  browser: ProjectBrowserPayload | null;
  browserError?: string | null;
  browserLoading?: boolean;
  configPageSettings: ConfigPageSettings;
  configPersistenceStatus?: ConfigPersistenceStatus;
  dependencyBusyId: string;
  dependencyStatusById: Record<string, ConfigDependencyStatus>;
  locale: Locale;
  llmStatus: ConfigLlmStatus | null;
  moduleBatchRecoveryPathsByProject: Record<string, string[]>;
  moduleSelectionTarget?: WorkspaceModuleSelectionTarget | null;
  moduleCreateIntent?: ModuleCreateIntent | null;
  onModuleCreateIntentConsumed?: (nonce: number) => void;
  onCheckDependency: (id: string) => void;
  onBuildTarget?: (target: BuildTarget) => void;
  onConfigPageSettingsChange: (settings: ConfigPageSettings) => void;
  onInstallDependency: (id: string) => void;
  onLocaleChange: (locale: Locale) => void;
  onPinTab: () => void;
  onOpenDiagramTab?: (id: string) => void;
  onOpenPath: (path: string) => void;
  onOpenModuleEntity?: (target: WorkspaceModuleSelectionTarget) => void;
  onModuleSelectionTargetChange?: (target: WorkspaceModuleSelectionTarget | null) => void;
  onModuleBatchRecoveryPathsChange: (projectRoot: string, paths: string[]) => void;
  onOpenTargetChange: (target: OpenPathTarget) => void;
  onProjectRefresh: (projectRoot?: string, fallbackProjectId?: string) => Promise<void>;
  onProjectPreferredLanguageChange?: (preferredLanguage: string) => void | Promise<void>;
  onResetAiChatProfile: (profileId: string) => void;
  onSaveAiChatProfile: (profileId: string, profile: ParaDevAiChatProfileWrite) => void;
  onTestLlm: () => void;
  onThemeChange: (theme: ThemeName) => void;
  openTarget: OpenPathTarget;
  pathStatusByPath?: Record<string, DesktopPathStatusPayload>;
  pathStatusErrorByPath?: Record<string, string>;
  paneLabel: string;
  projectOptions: ProjectOption[];
  projectLanguageBusy?: boolean;
  projectLanguageError?: string;
  sessionStore?: ModuleEditorSessionStore;
  surfaceRows: SurfaceRow[];
  tab: WorkspaceTab;
  templates: ProjectTemplatesPayload | null;
  t: Translator;
  theme: ThemeName;
};

function WorkspacePane({
  activeFeature,
  activeProject,
  aiChatDefaultRole,
  aiChatProfileLoadError = null,
  aiChatProfiles,
  aiChatSourceKindRows = [],
  aiChatSourceKinds = [],
  browser,
  browserError = null,
  browserLoading = false,
  configPageSettings,
  configPersistenceStatus,
  dependencyBusyId,
  dependencyStatusById,
  locale,
  llmStatus,
  moduleBatchRecoveryPathsByProject,
  moduleCreateIntent = null,
  onModuleCreateIntentConsumed,
  moduleSelectionTarget,
  onCheckDependency,
  onBuildTarget,
  onConfigPageSettingsChange,
  onInstallDependency,
  onLocaleChange,
  onOpenDiagramTab,
  onOpenPath,
  onOpenModuleEntity,
  onModuleSelectionTargetChange,
  onModuleBatchRecoveryPathsChange,
  onOpenTargetChange,
  onPinTab,
  onProjectRefresh,
  onProjectPreferredLanguageChange,
  onResetAiChatProfile,
  onSaveAiChatProfile,
  onTestLlm,
  onThemeChange,
  openTarget,
  pathStatusByPath,
  pathStatusErrorByPath,
  paneLabel,
  projectOptions,
  projectLanguageBusy,
  projectLanguageError,
  sessionStore,
  surfaceRows,
  tab,
  templates,
  t,
  theme
}: WorkspacePaneProps) {
  const tabTitle = workspaceTabTitle(tab, t, browser);
  const tabSubtitle = tab.subtitleKey ? t(tab.subtitleKey) : "";
  const moduleSurface = tab.kind === "module" || tab.kind === "diagram";
  const diagramSurface = tab.kind === "diagram";
  const familyId = diagramSurface ? tab.familyId ?? moduleIdForDiagramTabId(tab.id) : tab.id;
  const gameRoot = configPageSettings?.hoi4?.gameRoot ?? "";
  const moduleBrowser = useMemo(
    () => (moduleSurface ? projectBrowserForFamily(browser, familyId) : browser),
    [browser, familyId, moduleSurface]
  );
  const moduleEditorSurface = diagramSurface ? "diagram" : "module";
  const moduleEditorProjectRoot =
    moduleBrowser?.root.trim() ||
    activeProject?.path.trim() ||
    "paradev://unavailable";
  const moduleEditorIdentityKey = moduleSurface
    ? `${moduleEditorSessionKey(moduleEditorProjectRoot, familyId)}::${moduleEditorSurface}`
    : "";
  const projectRecoveryKey = activeProject?.path ?? moduleBrowser?.root ?? "";
  const familyTitleKey = moduleTitleKeyForFamilyId(familyId, browser);
  const familyTitle = familyTitleKey
    ? t(familyTitleKey)
    : tab.title ?? projectBrowserFamily(browser, familyId)?.title ?? familyId;
  const diagramTitleKey = projectDiagramTitleKeyForFamilyId(browser, familyId);
  const diagramTitle = diagramTitleKey ? t(diagramTitleKey) : familyTitle;
  const openDiagramTabId = !diagramSurface && supportsProjectDiagramFamily(browser, familyId) ? diagramTabIdForModule(familyId) : "";
  const panelClassName = moduleSurface
    ? [
        "workspace-panel module-workspace-panel",
        diagramSurface ? "diagram-workspace-panel" : "",
        openDiagramTabId && onOpenDiagramTab ? "module-diagram-action-visible" : ""
      ]
        .filter(Boolean)
        .join(" ")
    : "workspace-panel";

  return (
    <div className={panelClassName}>
      {moduleSurface ? null : (
        <div className="workspace-heading">
          <span className="panel-icon">
            <SplitSquareHorizontal aria-hidden="true" size={17} />
          </span>
          <div>
            <p className="label">{paneLabel}</p>
            <h2>{tabTitle}</h2>
          </div>
        </div>
      )}

      {moduleSurface ? (
        <>
          {openDiagramTabId && onOpenDiagramTab ? (
            <div className="workspace-module-actions">
              <button className="toolbar-button workspace-open-diagram" onClick={() => onOpenDiagramTab(openDiagramTabId)} title={t("workspace.diagram.openTree", { title: diagramTitle })} type="button">
                <GitBranch aria-hidden="true" size={13} />
                {t("workspace.diagram.openTree", { title: diagramTitle })}
              </button>
            </div>
          ) : null}
          <Suspense fallback={<div className="editor-loading">{t("workspace.module.editor.loadingEditor")}</div>}>
            <ModuleEditor
              batchRecoveryPaths={
                moduleBatchRecoveryPathsByProject[projectRecoveryKey] ?? []
              }
              browser={moduleBrowser}
              familyId={familyId}
              familyTitle={familyTitle}
              gameRoot={gameRoot}
              key={moduleEditorIdentityKey}
              loadError={browserError}
              loading={browserLoading}
              locale={locale}
              onBuildTarget={onBuildTarget}
              onOpenModuleEntity={onOpenModuleEntity}
              onModuleSelectionTargetChange={onModuleSelectionTargetChange}
              onBatchRecoveryPathsChange={(paths) =>
                onModuleBatchRecoveryPathsChange(projectRecoveryKey, paths)
              }
              onPinTab={onPinTab}
              onProjectRefresh={onProjectRefresh}
              openTarget={openTarget}
              projectRoot={moduleEditorProjectRoot}
              moduleCreateIntent={moduleCreateIntent}
              onModuleCreateIntentConsumed={onModuleCreateIntentConsumed}
              selectedEntityId={moduleSelectionTarget?.familyId === familyId ? moduleSelectionTarget.entityId : ""}
              selectedSourcePath={moduleSelectionTarget?.familyId === familyId ? moduleSelectionTarget.sourcePath ?? "" : ""}
              sessionStore={sessionStore}
              surface={moduleEditorSurface}
              templates={templates}
              t={t}
              theme={theme}
            />
          </Suspense>
        </>
      ) : tab.kind === "config" ? (
        <ConfigPage
          activeConfigId={tab.id}
          activeProject={activeProject}
          aiChatDefaultRole={aiChatDefaultRole}
          aiChatProfileLoadError={aiChatProfileLoadError}
          aiChatProfiles={aiChatProfiles}
          aiChatSourceKindRows={aiChatSourceKindRows}
          aiChatSourceKinds={aiChatSourceKinds}
          browser={browser}
          dependencyBusyId={dependencyBusyId}
          dependencyStatusById={dependencyStatusById}
          locale={locale}
          llmStatus={llmStatus}
          onCheckDependency={onCheckDependency}
          onInstallDependency={onInstallDependency}
          onLocaleChange={onLocaleChange}
          onOpenPath={onOpenPath}
          onOpenTargetChange={onOpenTargetChange}
          onPreferredLanguageChange={onProjectPreferredLanguageChange}
          pathStatusByPath={pathStatusByPath ?? {}}
          pathStatusErrorByPath={pathStatusErrorByPath ?? {}}
          persistenceStatus={configPersistenceStatus}
          onResetAiChatProfile={onResetAiChatProfile}
          onSaveAiChatProfile={onSaveAiChatProfile}
          onSettingsChange={onConfigPageSettingsChange}
          onTestLlm={onTestLlm}
          onThemeChange={onThemeChange}
          openTarget={openTarget}
          projectOptions={projectOptions}
          preferredLanguageBusy={projectLanguageBusy}
          preferredLanguageError={projectLanguageError}
          settings={configPageSettings}
          t={t}
          theme={theme}
        />
      ) : (
        <div className="empty-tab-panel">
          <p className="label">{tab.kind}</p>
          <h3>{t("workspace.scaffold.title", { title: tabTitle })}</h3>
          <p>{t("workspace.scaffold.body", { subtitle: tabSubtitle || tabTitle })}</p>
        </div>
      )}

      {tab.kind === "surface" ? (
        <SurfaceTable surfaceRows={surfaceRows} t={t} />
      ) : moduleSurface || tab.kind === "config" ? null : (
        <>
          <div className="focus-band">
            <div>
              <p className="label">{t("workspace.selectedModule.label")}</p>
              <h3>{featureTitle(activeFeature, t)}</h3>
              {activeFeature.descriptionKey ? <p>{t(activeFeature.descriptionKey)}</p> : null}
            </div>
            <span className={`status-pill ${activeFeature.status}`}>{t(statusKey[activeFeature.status])}</span>
          </div>

          <SurfaceTable surfaceRows={surfaceRows} t={t} />
        </>
      )}
    </div>
  );
}

function SurfaceTable({ surfaceRows, t }: { surfaceRows: SurfaceRow[]; t: Translator }) {
  return (
    <div className="surface-table" role="table" aria-label={t("workspace.surface.tableAria")}>
      <div className="surface-row header" role="row">
        <span>{t("workspace.surface.column.surface")}</span>
        <span>{t("workspace.surface.column.runtime")}</span>
        <span>{t("workspace.surface.column.status")}</span>
      </div>
      {surfaceRows.slice(0, 7).map((surface) => (
        <div className="surface-row" key={surface.id} role="row">
          <span>
            <strong>{t(surface.titleKey)}</strong>
            <small>{surface.path}</small>
          </span>
          <code>{surface.runtime}</code>
          <span className={`status-pill ${surface.status}`}>
            {surface.status === "ready" ? <CheckCircle2 aria-hidden="true" size={13} /> : <CircleDashed aria-hidden="true" size={13} />}
            {t(statusKey[surface.status])}
          </span>
        </div>
      ))}
    </div>
  );
}

function workspaceTabTitle(
  tab: WorkspaceTab,
  t: Translator,
  browser: ProjectBrowserPayload | null
) {
  if (tab.kind === "diagram") {
    const familyId = tab.familyId ?? moduleIdForDiagramTabId(tab.id);
    const diagramTitleKey = projectDiagramTitleKeyForFamilyId(browser, familyId);
    if (diagramTitleKey) {
      return t(diagramTitleKey);
    }
    const titleKey = moduleTitleKeyForFamilyId(familyId, browser);
    const title = titleKey
      ? t(titleKey)
      : tab.title ?? projectBrowserFamily(browser, familyId)?.title ?? familyId;
    return t("workspace.diagram.tabTitle", { title });
  }
  return tab.titleKey ? t(tab.titleKey) : tab.title ?? tab.id;
}

function featureTitle(feature: FeatureModule, t: Translator) {
  return feature.titleKey ? t(feature.titleKey) : feature.label ?? feature.id;
}
