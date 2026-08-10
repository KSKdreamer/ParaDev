import type { Dispatch, SetStateAction } from "react";
import { AgentAuthoringPage } from "../agentAuthoring/AgentAuthoringPage";
import { BuildPage } from "../buildPage/BuildPage";
import type { BuildDiagnosticsRefreshSource } from "../buildPage/buildDiagnosticsCache";
import type { BuildTarget, BuildTargetIntent } from "../buildPage/buildPageModel";
import type { BuildRunLifecycleController } from "../buildPage/buildRunLifecycle";
import { ProjectManagementPage } from "../projectManagement/ProjectManagementPage";
import {
  FloatingChatShell,
  type AiChatOperationNavigation,
  type AiChatProposalReview,
  type AiChatSendResult
} from "./FloatingChatShell";
import { ProjectPanel } from "./ProjectPanel";
import { Rail } from "./Rail";
import { TopBar } from "./TopBar";
import { UnsavedChangesDialog } from "./UnsavedChangesDialog";
import { Workspace } from "./Workspace";
import type { ConfigDependencyStatus, ConfigLlmStatus, ConfigPageSettings, ConfigPersistenceStatus } from "../configPage/model";
import { htmlLangForLocale, type Locale, type Translator } from "../i18n";
import type { ModuleEditorSessionStore } from "../moduleEditor/editorSessionStore";
import type { DesktopPathStatusPayload, OpenPathTarget, ParaDevAiChatProfile, ParaDevAiChatProfileWrite, ParaDevAiChatSource, ParaDevAiChatSourceKindRow } from "../services/paradev";
import type { AiOperationIntent, BootProgressState, FeatureModule, ModuleCreateIntent, PanelOption, ProjectBrowserPayload, ProjectOption, ProjectTemplatesPayload, RailItem, SurfaceRow, ThemeName, WorkspaceModuleSelectionTarget, WorkspaceTab } from "../types";

type AppShellProps = {
  activeBrowserError?: string | null;
  activeBrowserLoading: boolean;
  activeFeature: FeatureModule;
  activeOption: string;
  activeProject: ProjectOption;
  activeRail: string;
  activeTab: string;
  activeWorkspaceTab: WorkspaceTab | null;
  bootProgress: BootProgressState | null;
  browser: ProjectBrowserPayload | null;
  buildDiagnosticsGeneration?: number;
  buildDiagnosticsRefreshSource?: BuildDiagnosticsRefreshSource;
  buildLifecycle: BuildRunLifecycleController;
  configPageSettings: ConfigPageSettings;
  configPersistenceStatus?: ConfigPersistenceStatus;
  configOptions: PanelOption[];
  dependencyBusyId: string;
  dependencyStatusById: Record<string, ConfigDependencyStatus>;
  featureModules: FeatureModule[];
  inspectorOpen: boolean;
  locale: Locale;
  llmStatus: ConfigLlmStatus | null;
  aiChatDefaultRole: string;
  aiChatDock: AiChatDock;
  aiChatGateway: string;
  aiChatModel: string;
  aiChatOpen: boolean;
  aiChatPreset: string;
  aiChatProfileLoadError?: string | null;
  aiChatProfiles: ParaDevAiChatProfile[];
  aiChatProvider: string;
  aiChatSourceKindRows?: ParaDevAiChatSourceKindRow[];
  aiChatSourceKinds?: string[];
  aiChatSources: ParaDevAiChatSource[];
  authoringClosePrompt?: {
    busy: boolean;
    dirtySessionCount: number;
    error?: string;
    onCancel: () => void;
    onDiscard: () => void;
  } | null;
  buildAiOperationIntent?: AiOperationIntent | null;
  buildTargetIntent?: BuildTargetIntent | null;
  moduleCreateIntent?: ModuleCreateIntent | null;
  onBuildTarget?: (target: BuildTarget) => void;
  onBuildTargetIntentConsumed?: (nonce: number) => void;
  onModuleCreateIntentConsumed?: (nonce: number) => void;
  onCheckDependency: (id: string) => void;
  onAiChatSend: (prompt: string, role: string, sources: ParaDevAiChatSource[]) => Promise<AiChatSendResult>;
  onAiChatDockChange: (dock: AiChatDock) => void;
  onAiChatOpenChange: (open: boolean) => void;
  onAiChatOperationNavigate: (navigation: AiChatOperationNavigation) => void;
  onAiChatProposalReview?: (proposal: AiChatProposalReview) => void | Promise<void>;
  onCloseTab: (id: string) => void;
  onConfigPageSettingsChange: (settings: ConfigPageSettings) => void;
  onInstallDependency: (id: string) => void;
  onImportProject: () => void;
  onResetAiChatProfile: (profileId: string) => void;
  onSaveAiChatProfile: (profileId: string, profile: ParaDevAiChatProfileWrite) => void;
  onModuleReorder: (fromId: string, toId: string) => void;
  onOpenProject: () => void;
  onOpenPath: (path: string) => void;
  onOpenModuleEntity?: (target: WorkspaceModuleSelectionTarget) => void;
  onModuleSelectionTargetChange?: (target: WorkspaceModuleSelectionTarget | null) => void;
  onBuildProjectRefresh: (projectRoot?: string, fallbackProjectId?: string) => Promise<void>;
  onProjectRefresh: (projectRoot?: string, fallbackProjectId?: string) => Promise<void>;
  onProjectPreferredLanguageChange?: (preferredLanguage: string) => void | Promise<void>;
  onPinConfig: (id: string) => void;
  onPinModule: (id: string) => void;
  onPinTab: (id: string) => void;
  onSplitToggle: () => void;
  onTestLlm: () => void;
  onTabSelect: (id: string) => void;
  openTabs: WorkspaceTab[];
  moduleSelectionTarget?: WorkspaceModuleSelectionTarget | null;
  openTarget: OpenPathTarget;
  pathStatusByPath?: Record<string, DesktopPathStatusPayload>;
  pathStatusErrorByPath?: Record<string, string>;
  projectOptions: ProjectOption[];
  projectPanelOpen: boolean;
  railItems: RailItem[];
  searchQuery: string;
  sessionStore?: ModuleEditorSessionStore;
  onSelectConfig: (id: string) => void;
  onSelectModule: (id: string) => void;
  onSelectProject: (id: string) => void;
  onSelectRail: (id: string) => void;
  onSelectSettings: () => void;
  onSearchQueryChange: (query: string) => void;
  setSecondaryTab: Dispatch<SetStateAction<string>>;
  onSelectModuleDiagram: (id: string) => void;
  setInspectorOpen: Dispatch<SetStateAction<boolean>>;
  setLocale: Dispatch<SetStateAction<Locale>>;
  setOpenTarget: (target: OpenPathTarget) => void;
  setProjectPanelOpen: Dispatch<SetStateAction<boolean>>;
  setTheme: Dispatch<SetStateAction<ThemeName>>;
  projectError: string;
  projectImporting: boolean;
  projectLoading: boolean;
  projectLanguageBusy?: boolean;
  projectLanguageError?: string;
  projectNotice?: string;
  projectNoticeDetail?: string;
  projectOpenError: string;
  projectOpening: boolean;
  secondaryTab: string;
  secondaryBrowserError?: string | null;
  secondaryBrowserLoading: boolean;
  secondaryWorkspaceTab: WorkspaceTab | null;
  splitView: boolean;
  surfaceRows: SurfaceRow[];
  templates: ProjectTemplatesPayload | null;
  t: Translator;
  theme: ThemeName;
};

type AiChatDock = "floating" | "side";

const DEVELOPER_SURFACE_TAB: WorkspaceTab = {
  id: "developer-surfaces",
  kind: "surface",
  pinned: true,
  titleKey: "rail.developer"
};

export function AppShell({
  activeBrowserError,
  activeBrowserLoading,
  activeFeature,
  activeOption,
  activeProject,
  activeRail,
  activeTab,
  activeWorkspaceTab,
  bootProgress,
  browser,
  buildDiagnosticsGeneration = 0,
  buildDiagnosticsRefreshSource = "live",
  buildLifecycle,
  configPageSettings,
  configPersistenceStatus,
  configOptions,
  dependencyBusyId,
  dependencyStatusById,
  featureModules,
  inspectorOpen,
  locale,
  llmStatus,
  aiChatDefaultRole,
  aiChatDock,
  aiChatGateway,
  aiChatModel,
  aiChatOpen,
  aiChatPreset,
  aiChatProfileLoadError,
  aiChatProfiles,
  aiChatProvider,
  aiChatSourceKindRows = [],
  aiChatSourceKinds = [],
  aiChatSources,
  authoringClosePrompt = null,
  buildAiOperationIntent = null,
  buildTargetIntent = null,
  moduleCreateIntent = null,
  onBuildTarget,
  onBuildTargetIntentConsumed,
  onModuleCreateIntentConsumed,
  onCheckDependency,
  onAiChatSend,
  onAiChatDockChange,
  onAiChatOpenChange,
  onAiChatOperationNavigate,
  onAiChatProposalReview,
  onCloseTab,
  onConfigPageSettingsChange,
  onInstallDependency,
  onImportProject,
  onResetAiChatProfile,
  onSaveAiChatProfile,
  onModuleReorder,
  onOpenModuleEntity,
  onOpenPath,
  onModuleSelectionTargetChange,
  onOpenProject,
  onBuildProjectRefresh,
  onProjectRefresh,
  onProjectPreferredLanguageChange,
  onPinConfig,
  onPinModule,
  onPinTab,
  onSplitToggle,
  onTestLlm,
  onTabSelect,
  openTabs,
  moduleSelectionTarget,
  openTarget,
  pathStatusByPath,
  pathStatusErrorByPath,
  projectOptions,
  projectPanelOpen,
  railItems,
  searchQuery,
  sessionStore,
  onSelectConfig,
  onSelectModuleDiagram,
  onSelectModule,
  onSelectProject,
  onSelectRail,
  onSelectSettings,
  onSearchQueryChange,
  setSecondaryTab,
  setInspectorOpen,
  setLocale,
  setOpenTarget,
  setProjectPanelOpen,
  setTheme,
  projectError,
  projectImporting,
  projectLoading,
  projectLanguageBusy,
  projectLanguageError,
  projectNotice = "",
  projectNoticeDetail = "",
  projectOpenError,
  projectOpening,
  secondaryTab,
  secondaryBrowserError,
  secondaryBrowserLoading,
  secondaryWorkspaceTab,
  splitView,
  surfaceRows,
  templates,
  t,
  theme
}: AppShellProps) {
  const panelMode = activeRail === "settings" ? "config" : activeRail === "projects" ? "modules" : null;
  const managementPageActive = activeRail === "management";
  const buildPageActive = activeRail === "build";
  const agentsPageActive = activeRail === "agents";
  const developerPageActive = activeRail === "developer";
  const pagePlaceholder = developerPageActive ? null : railPagePlaceholder(activeRail, t);
  const workspaceActiveTab = developerPageActive ? DEVELOPER_SURFACE_TAB.id : activeTab;
  const workspaceOpenTabs = developerPageActive ? [DEVELOPER_SURFACE_TAB] : openTabs;
  const workspaceTab = developerPageActive ? DEVELOPER_SURFACE_TAB : activeWorkspaceTab;
  const projectPanelVisible = panelMode !== null && projectPanelOpen;
  const bootStatus = bootProgress?.status ?? "normal";
  const shellBlocked = Boolean(bootProgress) && bootStatus !== "error";
  const chatAvoidInspector =
    inspectorOpen &&
    !managementPageActive &&
    !buildPageActive &&
    !agentsPageActive;
  const chatSideOpen = !shellBlocked && aiChatOpen && aiChatDock === "side";
  const mainShellClassName = panelMode === null ? "main-shell main-shell-full" : "main-shell";
  const appClassName = [
    "app",
    `theme-${theme}`,
    chatSideOpen ? "chat-side-open" : "",
    projectPanelVisible ? "" : "project-panel-collapsed",
    bootProgress ? (bootStatus === "error" ? "app-boot-error" : "app-booting") : ""
  ]
    .filter(Boolean)
    .join(" ");
  const appBusy = shellBlocked ? true : undefined;

  return (
    <div aria-busy={appBusy} className={appClassName} lang={htmlLangForLocale(locale)}>
      <Rail activeRail={activeRail} blocked={shellBlocked} items={railItems} onSelect={onSelectRail} onSettingsSelect={onSelectSettings} t={t} theme={theme} />
      {panelMode ? (
        <ProjectPanel
          activeOption={activeOption}
          activeProject={activeProject}
          blocked={shellBlocked}
          isOpen={projectPanelVisible}
          mode={panelMode}
          onImportProject={onImportProject}
          onOpenProject={onOpenProject}
          onReorderOptions={panelMode === "modules" ? onModuleReorder : undefined}
          onPinOption={panelMode === "config" ? onPinConfig : onPinModule}
          onSelectOption={panelMode === "config" ? onSelectConfig : onSelectModule}
          onSelectProject={onSelectProject}
          options={panelMode === "config" ? configOptions : featureModules}
          projectError={projectError}
          projectImporting={projectImporting}
          projectLoading={projectLoading}
          projectNotice={projectNotice}
          projectNoticeDetail={projectNoticeDetail}
          projectOpenError={projectOpenError}
          projectOpening={projectOpening}
          projectOptions={projectOptions}
          t={t}
        />
      ) : null}
      <main aria-hidden={shellBlocked ? true : undefined} className={mainShellClassName} inert={shellBlocked ? true : undefined}>
        <TopBar
          inspectorOpen={inspectorOpen}
          locale={locale}
          onInspectorToggle={() => setInspectorOpen((open) => !open)}
          onLocaleChange={setLocale}
          onOpenTargetChange={setOpenTarget}
          onProjectPanelToggle={() => setProjectPanelOpen((open) => !open)}
          onSearchQueryChange={onSearchQueryChange}
          onThemeChange={setTheme}
          projectPanelAvailable={panelMode !== null}
          projectPanelOpen={projectPanelVisible}
          openTarget={openTarget}
          searchQuery={searchQuery}
          t={t}
          theme={theme}
        />
        {managementPageActive ? (
          <ProjectManagementPage
            activeProject={activeProject}
            browser={browser}
            onActivateProject={onSelectProject}
            onOpenBuildPage={() => onSelectRail("build")}
            openTarget={openTarget}
            projectOptions={projectOptions}
            t={t}
          />
        ) : buildPageActive ? (
          <BuildPage
            activeProject={activeProject}
            aiOperationIntent={buildAiOperationIntent}
            browser={browser}
            buildDiagnosticsGeneration={buildDiagnosticsGeneration}
            buildDiagnosticsRefreshSource={buildDiagnosticsRefreshSource}
            buildLifecycle={buildLifecycle}
            buildTargetIntent={buildTargetIntent}
            key={activeProject.path}
            onBuildTargetIntentConsumed={onBuildTargetIntentConsumed}
            onProjectRefresh={onBuildProjectRefresh}
            openTarget={openTarget}
            projectLoading={projectLoading}
            t={t}
          />
        ) : agentsPageActive ? (
          <AgentAuthoringPage
            activeProject={activeProject}
            browser={browser}
            onOpenAiChat={() => onAiChatOpenChange(true)}
            onOpenEditing={() => onSelectRail("projects")}
            templates={templates}
            t={t}
          />
        ) : (
          <Workspace
            activeBrowserError={activeBrowserError}
            activeBrowserLoading={activeBrowserLoading}
            activeFeature={activeFeature}
            activeProject={activeProject}
            activeTab={workspaceActiveTab}
            activeWorkspaceTab={workspaceTab}
            aiChatDefaultRole={aiChatDefaultRole}
            aiChatProfileLoadError={aiChatProfileLoadError}
            aiChatProfiles={aiChatProfiles}
            aiChatSourceKindRows={aiChatSourceKindRows}
            aiChatSourceKinds={aiChatSourceKinds}
            browser={browser}
            configPageSettings={configPageSettings}
            configPersistenceStatus={configPersistenceStatus}
            dependencyBusyId={dependencyBusyId}
            dependencyStatusById={dependencyStatusById}
            inspectorOpen={inspectorOpen}
            locale={locale}
            llmStatus={llmStatus}
            pagePlaceholder={pagePlaceholder}
            onCheckDependency={onCheckDependency}
            onBuildTarget={onBuildTarget}
            onCloseTab={onCloseTab}
            onConfigPageSettingsChange={onConfigPageSettingsChange}
            onInstallDependency={onInstallDependency}
            onOpenDiagramTab={onSelectModuleDiagram}
            onOpenModuleEntity={onOpenModuleEntity}
            onOpenPath={onOpenPath}
            onModuleSelectionTargetChange={onModuleSelectionTargetChange}
            onLocaleChange={setLocale}
            onOpenTargetChange={setOpenTarget}
            onProjectRefresh={onProjectRefresh}
            onProjectPreferredLanguageChange={onProjectPreferredLanguageChange}
            onResetAiChatProfile={onResetAiChatProfile}
            onSaveAiChatProfile={onSaveAiChatProfile}
            onTestLlm={onTestLlm}
            moduleSelectionTarget={moduleSelectionTarget}
            moduleCreateIntent={moduleCreateIntent}
            onModuleCreateIntentConsumed={onModuleCreateIntentConsumed}
            openTarget={openTarget}
            pathStatusByPath={pathStatusByPath}
            pathStatusErrorByPath={pathStatusErrorByPath}
            onThemeChange={setTheme}
            onTabPin={onPinTab}
            onSplitToggle={onSplitToggle}
            onTabSelect={onTabSelect}
            openTabs={workspaceOpenTabs}
            projectOptions={projectOptions}
            projectLanguageBusy={projectLanguageBusy}
            projectLanguageError={projectLanguageError}
            secondaryTab={secondaryTab}
            secondaryBrowserError={secondaryBrowserError}
            secondaryBrowserLoading={secondaryBrowserLoading}
            secondaryWorkspaceTab={secondaryWorkspaceTab}
            sessionStore={sessionStore}
            setSecondaryTab={setSecondaryTab}
            splitView={splitView}
            surfaceRows={surfaceRows}
            templates={templates}
            t={t}
            theme={theme}
          />
        )}
      </main>
      <FloatingChatShell
        activeProjectName={activeProject.name}
        avoidInspector={aiChatDock === "floating" && chatAvoidInspector}
        blocked={shellBlocked}
        contextSources={aiChatSources}
        defaultRole={aiChatDefaultRole}
        dock={aiChatDock}
        gateway={aiChatGateway}
        model={aiChatModel}
        onDockChange={onAiChatDockChange}
        onOpenChange={onAiChatOpenChange}
        onOperationNavigate={onAiChatOperationNavigate}
        onProposalReview={onAiChatProposalReview}
        onSend={onAiChatSend}
        open={aiChatOpen}
        preset={aiChatPreset}
        profileLoadError={aiChatProfileLoadError}
        profiles={aiChatProfiles}
        provider={aiChatProvider}
        key={activeProject.path || activeProject.id}
        sourceKindRows={aiChatSourceKindRows}
        t={t}
      />
      {bootProgress ? <BootProgress progress={bootProgress} t={t} /> : null}
      {authoringClosePrompt ? (
        <UnsavedChangesDialog
          busy={authoringClosePrompt.busy}
          dirtySessionCount={authoringClosePrompt.dirtySessionCount}
          error={authoringClosePrompt.error}
          onCancel={authoringClosePrompt.onCancel}
          onDiscard={authoringClosePrompt.onDiscard}
          t={t}
        />
      ) : null}
    </div>
  );
}

function BootProgress({ progress, t }: { progress: BootProgressState; t: Translator }) {
  const value = Math.max(0, Math.min(100, Math.round(progress.value)));
  const status = progress.status ?? "normal";
  const ariaLive = status === "error" ? "assertive" : "polite";
  const className = status === "error" ? "boot-progress boot-progress-error" : "boot-progress";
  const role = status === "error" ? "alert" : "status";

  return (
    <div aria-live={ariaLive} className={className} role={role}>
      <div className={status === "error" ? "boot-progress-card" : "boot-progress-loader"}>
        <div className="boot-progress-dots" aria-hidden="true">
          <span />
          <span />
          <span />
        </div>
        {status === "error" ? (
          <div className="boot-progress-copy">
            <p className="label">{progress.label}</p>
            <strong>{progress.detail}</strong>
          </div>
        ) : null}
        <div
          aria-label={t("app.boot.progress.aria")}
          aria-valuemax={100}
          aria-valuemin={0}
          aria-valuenow={value}
          className="boot-progress-track"
          role="progressbar"
        >
          <span style={{ width: `${value}%` }} />
        </div>
      </div>
    </div>
  );
}

function railPagePlaceholder(activeRail: string, t: Translator) {
  if (activeRail === "management") {
    return {
      title: t("workspace.page.management.title"),
      body: t("workspace.page.management.body")
    };
  }
  if (activeRail === "developer") {
    return {
      title: t("workspace.page.developer.title"),
      body: t("workspace.page.developer.body")
    };
  }
  return null;
}
