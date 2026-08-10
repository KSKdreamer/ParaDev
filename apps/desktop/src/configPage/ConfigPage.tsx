import { CheckCircle2, CircleDashed, Download, FlaskConical, FolderOpen, Gauge, Images, MonitorCog, RefreshCw, RotateCcw, Save, ServerCog, SlidersHorizontal, Terminal, TriangleAlert } from "lucide-react";
import { useEffect, useState, type ReactNode } from "react";
import { aiChatProfileOperationCards } from "../aiChatOperations";
import { DEFAULT_AI_CHAT_PROFILE_SOURCE_KINDS, aiChatProfileDraftDetail, aiChatProfileDraftLabel, aiChatProfileDraftPrompt, aiChatProfileSaveDraft, canonicalAiChatProfileSourceKinds, hasAiChatProfileDraftChanges } from "../aiChatProfileText";
import { aiChatProfileSourceKindLabel, type AiChatSourceKindRowLike } from "../aiChatSourceKindText";
import { aiRouteLabelWithPreset, aiRoutePartLabel } from "../aiRouteText";
import { buildOutputOpenPath } from "../buildPage/buildPageModel";
import { DESKTOP_CONFIG_KEYS, desktopConfigMinimum, type DesktopConfigKey } from "../desktopConfig";
import type { Locale, TranslationKey, Translator } from "../i18n";
import { OPEN_PATH_TARGETS, type OpenPathTarget } from "../openPathTargets";
import type { DesktopPathStatusPayload, ParaDevAiChatProfile, ParaDevAiChatProfileWrite, ParaDevAiChatSourceKindRow } from "../services/paradev";
import type { ProjectBrowserPayload, ProjectOption, ThemeName } from "../types";
import { SelectField } from "../components/ui/SelectField";
import { CONFIG_CLI_OUTPUT_VALUES, CONFIG_HOI4_LAUNCH_MODE_VALUES, defaultConfigLlmStatus, defaultConfigPersistenceStatus, LLM_PRESET_ROWS, type ConfigCliOutput, type ConfigDependencyStatus, type ConfigHoi4LaunchMode, type ConfigLlmStatus, type ConfigPageSettings, type ConfigPersistenceStatus } from "./model";

const BUILD_PARALLELISM_MIN = desktopConfigMinimum(DESKTOP_CONFIG_KEYS.buildParallelism);
const LOCAL_MODULE_DEFAULT_MIN = 1;

type ConfigPageProps = {
  activeConfigId: string;
  activeProject: ProjectOption;
  aiChatDefaultRole?: string;
  aiChatProfileLoadError?: string | null;
  aiChatProfiles?: ParaDevAiChatProfile[];
  aiChatSourceKindRows?: ParaDevAiChatSourceKindRow[];
  aiChatSourceKinds?: string[];
  browser?: ProjectBrowserPayload | null;
  dependencyBusyId: string;
  dependencyStatusById: Record<string, ConfigDependencyStatus>;
  locale: Locale;
  llmStatus?: ConfigLlmStatus | null;
  onCheckDependency: (id: string) => void;
  onInstallDependency: (id: string) => void;
  onLocaleChange: (locale: Locale) => void;
  onOpenPath?: (path: string) => void;
  onOpenTargetChange: (target: OpenPathTarget) => void;
  onPreferredLanguageChange?: (preferredLanguage: string) => void | Promise<void>;
  onResetAiChatProfile?: (profileId: string) => void;
  onSaveAiChatProfile?: (profileId: string, profile: ParaDevAiChatProfileWrite) => void;
  onSettingsChange?: (settings: ConfigPageSettings) => void;
  onTestLlm: () => void;
  onThemeChange: (theme: ThemeName) => void;
  openTarget: OpenPathTarget;
  pathStatusByPath?: Record<string, DesktopPathStatusPayload>;
  pathStatusErrorByPath?: Record<string, string>;
  persistenceStatus?: ConfigPersistenceStatus;
  preferredLanguageBusy?: boolean;
  preferredLanguageError?: string;
  projectOptions: ProjectOption[];
  settings: ConfigPageSettings;
  t: Translator;
  theme: ThemeName;
};

const themeIds: ThemeName[] = ["light", "dark", "anthropic"];
const themeLabelKey: Record<ThemeName, TranslationKey> = {
  anthropic: "theme.anthropic",
  dark: "theme.dark",
  light: "theme.light"
};

export function ConfigPage({
  activeConfigId,
  activeProject,
  aiChatDefaultRole: loadedAiChatDefaultRole = "chat",
  aiChatProfileLoadError = null,
  aiChatProfiles = [],
  aiChatSourceKindRows = [],
  aiChatSourceKinds = [],
  browser,
  dependencyBusyId,
  dependencyStatusById,
  locale,
  llmStatus,
  onCheckDependency,
  onInstallDependency,
  onLocaleChange,
  onOpenPath,
  onOpenTargetChange,
  onPreferredLanguageChange,
  onResetAiChatProfile,
  onSaveAiChatProfile,
  onSettingsChange,
  onTestLlm,
  onThemeChange,
  openTarget,
  pathStatusByPath = {},
  pathStatusErrorByPath = {},
  persistenceStatus,
  preferredLanguageBusy = false,
  preferredLanguageError = "",
  projectOptions,
  settings,
  t,
  theme
}: ConfigPageProps) {
  const status = llmStatus ?? defaultConfigLlmStatus(settings.llm);
  const persistence = persistenceStatus ?? defaultConfigPersistenceStatus();
  const pageTitle = configTitle(activeConfigId, t);
  const configFieldHelper = t("config.field.sdkBacked");
  const aiConfigFieldHelper = t("config.field.aiRoute");
  const aiChatSourceKindOptions =
    aiChatSourceKindRows.length > 0 ? aiChatSourceKindRows.map((row) => row.id) : aiChatSourceKinds.length > 0 ? aiChatSourceKinds : Array.from(DEFAULT_AI_CHAT_PROFILE_SOURCE_KINDS);
  const openTargetLabel = openPathTargetLabel(openTarget, t);
  const outputOpenPath = buildOutputOpenPath(activeProject);
  const [profileDrafts, setProfileDrafts] = useState<Record<string, ParaDevAiChatProfileWrite>>({});

  useEffect(() => {
    setProfileDrafts(
      Object.fromEntries(
        aiChatProfiles.map((profile) => [
          profile.id,
          {
            detail: profile.detail,
            label: profile.label,
            prompt: profile.prompt,
            sourceKinds: profile.sourceKinds
          }
        ])
      )
    );
  }, [aiChatProfiles]);

  const effectiveAiChatDefaultRole = settings.chat.defaultRole || loadedAiChatDefaultRole;
  const aiChatProfileOptions =
    aiChatProfiles.length > 0
      ? aiChatProfiles.map((profile) => {
          const draft = profileDrafts[profile.id] ?? profile;
          return { label: aiChatProfileDraftLabel(profile, draft, t), value: profile.id };
        })
      : [{ label: effectiveAiChatDefaultRole, value: effectiveAiChatDefaultRole }];
  const localModuleDefaults = settings.moduleDefaults.filter((row) => !row.configKey);
  const sharedModuleDefaults = settings.moduleDefaults.filter((row) => row.configKey);

  return (
    <section className="config-page" aria-label={pageTitle}>
      <header className="config-page-header">
        <div>
          <p className="label">{t("config.page.label")}</p>
          <h2>{pageTitle}</h2>
        </div>
        <ConfigPersistenceIndicator persistence={persistence} t={t} />
      </header>

      {activeConfigId === "config-general" ? (
        <div className="config-section-stack">
          <SettingsPanel icon={<SlidersHorizontal aria-hidden="true" size={16} />} title={t("config.general.workspace.title")}>
            <SettingRow detail={t("config.general.project.detail")} label={t("config.general.project.label")}>
              <strong>{activeProject.name}</strong>
            </SettingRow>
            <SettingRow detail={t("config.general.projectRoot.detail")} label={t("config.general.projectRoot.label")}>
              <code>{activeProject.path}</code>
            </SettingRow>
            <SettingRow detail={t("config.general.language.detail")} label={t("config.general.language.label")}>
              <SelectField
                className="config-inline-select"
                label={t("locale.aria")}
                onChange={(event) => onLocaleChange(event.target.value as Locale)}
                options={[
                  { label: t("locale.en"), value: "en" },
                  { label: t("locale.zh"), value: "zh" }
                ]}
                value={locale}
                variant="compact"
              />
            </SettingRow>
            <SettingRow detail={t("config.general.openTarget.detail")} label={t("config.general.openTarget.label")}>
              <SelectField
                className="config-inline-select config-open-target-select"
                label={t("openTarget.aria")}
                onChange={(event) => onOpenTargetChange(event.target.value as OpenPathTarget)}
                options={OPEN_PATH_TARGETS.map((target) => ({ label: t(target.labelKey), value: target.id }))}
                value={openTarget}
                variant="compact"
              />
            </SettingRow>
          </SettingsPanel>
          <SettingsPanel icon={<MonitorCog aria-hidden="true" size={16} />} title={t("config.general.state.title")}>
            <MetricGrid
              rows={[
                [t("config.general.state.projects"), projectOptions.length],
                [t("config.general.state.objects"), browser?.items.length ?? 0],
                [t("config.general.state.families"), browser?.families.length ?? 0]
              ]}
            />
          </SettingsPanel>
          <SettingsPanel icon={<Terminal aria-hidden="true" size={16} />} title={t("config.general.commandDefaults.title")}>
            <SettingRow detail={t("config.general.projectName.detail")} label={t("config.general.projectName.label")}>
              <ConfigRouteTextField
                configKey={DESKTOP_CONFIG_KEYS.projectName}
                helper={configFieldHelper}
                label={t("config.general.projectName.label")}
                onChange={(name) =>
                  onSettingsChange?.({
                    ...settings,
                    project: {
                      ...settings.project,
                      name
                    }
                  })
                }
                value={settings.project.name}
              />
            </SettingRow>
            <SettingRow detail={t("config.general.cliOutput.detail")} label={t("config.general.cliOutput.label")}>
              <label className="config-select-with-key">
                <SelectField
                  className="config-inline-select"
                  data-paradev-config-key={DESKTOP_CONFIG_KEYS.cliOutput}
                  label={t("config.general.cliOutput.label")}
                  onChange={(event) =>
                    onSettingsChange?.({
                      ...settings,
                      cli: {
                        ...settings.cli,
                        output: event.target.value as ConfigCliOutput
                      }
                    })
                  }
                  options={CONFIG_CLI_OUTPUT_VALUES.map((value) => ({ label: cliOutputOptionLabel(value, t), value }))}
                  value={settings.cli.output}
                  variant="compact"
                />
                <small>{configFieldHelper}</small>
              </label>
            </SettingRow>
          </SettingsPanel>
        </div>
      ) : null}

      {activeConfigId === "config-appearance" ? (
        <div className="config-section-stack">
          <SettingsPanel icon={<MonitorCog aria-hidden="true" size={16} />} title={t("config.appearance.theme.title")}>
            <div className="config-theme-grid">
              {themeIds.map((themeId) => (
                <button className={themeId === theme ? "config-theme-option selected" : "config-theme-option"} key={themeId} onClick={() => onThemeChange(themeId)} type="button">
                  <span className={`config-theme-swatch theme-swatch-${themeId}`} />
                  <strong>{t(themeLabelKey[themeId])}</strong>
                  <small>{themeId === theme ? t("config.appearance.theme.active") : t("config.appearance.theme.apply")}</small>
                </button>
              ))}
            </div>
          </SettingsPanel>
        </div>
      ) : null}

      {activeConfigId === "config-models" ? (
        <div className="config-section-stack">
          <SettingsPanel icon={<ServerCog aria-hidden="true" size={16} />} title={t("config.models.heavenbase.title")}>
            <div className="config-llm-summary">
              <div>
                <p className="label">{t("config.models.activePreset")}</p>
                <h3>{llmPresetTitle(settings.llm.preset, t)}</h3>
                <p>
                  {t("config.models.activeRouteValue", {
                    route: aiRouteLabelWithPreset({
                      gateway: settings.llm.gateway,
                      model: settings.llm.model,
                      preset: settings.llm.preset,
                      provider: settings.llm.provider,
                      t
                    })
                  })}
                </p>
                <p>{t("config.models.heavenbase.detail")}</p>
              </div>
              <span className={`status-pill ${statusPillClass(status.status)}`}>{statusLabel(status.status, t)}</span>
            </div>
            <div className="config-route-primary-grid">
              <ConfigRouteSelectField
                configKey={DESKTOP_CONFIG_KEYS.aiPreset}
                helper={aiConfigFieldHelper}
                label={t("config.models.preset")}
                onChange={(value) =>
                  onSettingsChange?.({
                    ...settings,
                    llm: { ...settings.llm, preset: value }
                  })
                }
                options={LLM_PRESET_ROWS.map((row) => ({ label: t(row.labelKey), value: row.preset }))}
                value={settings.llm.preset}
              />
              <ConfigRouteTextField
                configKey={DESKTOP_CONFIG_KEYS.aiKeyEnv}
                helper={aiConfigFieldHelper}
                label={t("config.models.keySource")}
                onChange={(value) =>
                  onSettingsChange?.({
                    ...settings,
                    llm: { ...settings.llm, keyEnv: value }
                  })
                }
                value={settings.llm.keyEnv}
              />
              <ConfigRouteTextField
                configKey={DESKTOP_CONFIG_KEYS.aiBaseUrl}
                helper={aiConfigFieldHelper}
                label={t("config.models.baseUrl")}
                onChange={(value) =>
                  onSettingsChange?.({
                    ...settings,
                    llm: { ...settings.llm, baseUrl: value }
                  })
                }
                value={settings.llm.baseUrl}
              />
              <KeyValue label={t("config.models.resolvedBaseUrl")} value={status.baseUrl || t("config.value.pending")} />
            </div>
            <div className="config-route-advanced" data-paradev-route-overrides="advanced">
              <div className="config-route-advanced-heading">
                <span>
                  <strong>{t("config.models.advancedOverrides.title")}</strong>
                  <small>{t("config.models.advancedOverrides.detail")}</small>
                </span>
              </div>
              <div className="config-kv-grid config-route-override-grid">
                <ConfigRouteTextField
                  configKey={DESKTOP_CONFIG_KEYS.aiModel}
                  helper={aiConfigFieldHelper}
                  label={t("config.models.model")}
                  onChange={(value) =>
                    onSettingsChange?.({
                      ...settings,
                      llm: { ...settings.llm, model: value }
                    })
                  }
                  value={settings.llm.model}
                />
                <ConfigRouteTextField
                  configKey={DESKTOP_CONFIG_KEYS.aiProvider}
                  helper={aiConfigFieldHelper}
                  label={t("config.models.provider")}
                  onChange={(value) =>
                    onSettingsChange?.({
                      ...settings,
                      llm: { ...settings.llm, provider: value }
                    })
                  }
                  value={settings.llm.provider}
                />
                <ConfigRouteTextField
                  configKey={DESKTOP_CONFIG_KEYS.aiGateway}
                  helper={aiConfigFieldHelper}
                  label={t("config.models.gateway")}
                  onChange={(value) =>
                    onSettingsChange?.({
                      ...settings,
                      llm: { ...settings.llm, gateway: value }
                    })
                  }
                  value={settings.llm.gateway}
                />
              </div>
            </div>
            <div className="config-action-row">
              <button className="toolbar-button primary" onClick={onTestLlm} type="button">
                <FlaskConical aria-hidden="true" size={14} />
                {t("config.models.testRoute")}
              </button>
              <p>{llmTestDetail(status, t)}</p>
            </div>
          </SettingsPanel>
          <SettingsPanel icon={<Gauge aria-hidden="true" size={16} />} title={t("config.models.presets.title")}>
            <div className="config-table">
              {LLM_PRESET_ROWS.map((row) => (
                <div className="config-table-row" key={row.preset}>
                  <span>
                    <strong>{t(row.labelKey)}</strong>
                    <small>{t(row.detailKey)}</small>
                  </span>
                  <code>{row.preset}</code>
                  <code>{aiRoutePartLabel(row.model, t)}</code>
                </div>
              ))}
            </div>
          </SettingsPanel>
          <SettingsPanel icon={<SlidersHorizontal aria-hidden="true" size={16} />} title={t("config.models.chatProfiles.title")}>
            <SettingRow detail={t("config.models.chatProfiles.defaultRoleDetail")} label={t("config.models.chatProfiles.defaultRoleLabel")}>
              <ConfigRouteSelectField
                configKey={DESKTOP_CONFIG_KEYS.aiChatDefaultRole}
                helper={aiConfigFieldHelper}
                label={t("config.models.chatProfiles.defaultRoleLabel")}
                onChange={(value) =>
                  onSettingsChange?.({
                    ...settings,
                    chat: { ...settings.chat, defaultRole: value }
                  })
                }
                options={aiChatProfileOptions}
                value={effectiveAiChatDefaultRole}
              />
            </SettingRow>
            {aiChatProfileLoadError ? (
              <small className="project-path error config-ai-profile-load-error" role="alert">
                {aiChatProfileLoadError}
              </small>
            ) : null}
            <div className="config-ai-profile-grid">
              {aiChatProfiles.map((profile) => {
                const draft = profileDrafts[profile.id] ?? profile;
                const draftDetail = aiChatProfileDraftDetail(profile, draft, t);
                const draftLabel = aiChatProfileDraftLabel(profile, draft, t);
                const draftPrompt = aiChatProfileDraftPrompt(profile, draft, t);
                const profileBadge = aiChatProfileBadgeLabel(profile.id, effectiveAiChatDefaultRole, draftLabel, t);
                const selectedSourceKinds = draft.sourceKinds ?? profile.sourceKinds;
                const sourceKinds = sourceKindLabels(selectedSourceKinds, t, aiChatSourceKindRows);
                const hasDraftChanges = hasAiChatProfileDraftChanges(profile, draft, t, aiChatSourceKindOptions);
                const operationCards = aiChatProfileOperationCards(profile, t);
                return (
                  <div className="config-ai-profile-row" key={profile.id}>
                    <div className="config-ai-profile-heading">
                      <span>
                        <strong>{draftLabel}</strong>
                        <small>{draftDetail}</small>
                      </span>
                      <small className="config-ai-profile-badge">{profileBadge}</small>
                    </div>
                    {operationCards.length > 0 ? (
                      <div className="config-ai-profile-operation-strip" data-paradev-ai-profile-operation-count={operationCards.length}>
                        <span>{t("config.models.chatProfiles.operations")}</span>
                        <div>
                          {operationCards.map((card) => (
                            <code
                              data-paradev-ai-profile-id={profile.id}
                              data-paradev-ai-profile-operation-id={card.operation.id}
                              data-paradev-ai-profile-operation-passive="true"
                              key={card.operation.id}
                              title={`${card.actionTitle} · ${card.operation.summary}`}
                            >
                              {card.operation.id}
                            </code>
                          ))}
                        </div>
                        <small>{t("config.models.chatProfiles.operationsDetail")}</small>
                      </div>
                    ) : null}
                    <div className="config-ai-profile-fields">
                      <label>
                        <span>{t("config.models.chatProfiles.label")}</span>
                        <input
                          onChange={(event) => setProfileDrafts((current) => ({ ...current, [profile.id]: { ...draft, label: event.target.value } }))}
                          value={draftLabel}
                        />
                      </label>
                      <label>
                        <span>{t("config.models.chatProfiles.detail")}</span>
                        <input
                          onChange={(event) => setProfileDrafts((current) => ({ ...current, [profile.id]: { ...draft, detail: event.target.value } }))}
                          value={draftDetail}
                        />
                      </label>
                    </div>
                    <label className="config-ai-profile-prompt">
                      <span>{t("config.models.chatProfiles.prompt")}</span>
                      <textarea
                        data-paradev-ai-profile-prompt={profile.id}
                        onChange={(event) => setProfileDrafts((current) => ({ ...current, [profile.id]: { ...draft, prompt: event.target.value } }))}
                        value={draftPrompt}
                      />
                    </label>
                    <div className="config-ai-profile-sources">
                      <span>{t("config.models.chatProfiles.sources")}</span>
                      <div className="config-ai-profile-source-list" data-paradev-ai-profile-source-kinds={aiChatSourceKindOptions.join(",")}>
                        {aiChatSourceKindOptions.map((kind) => {
                          const label = sourceKindLabel(kind, t, aiChatSourceKindRows);
                          const selected = selectedSourceKinds.includes(kind);
                          return (
                            <label
                              className={["config-ai-profile-source-option", selected ? "selected" : ""].filter(Boolean).join(" ")}
                              data-paradev-ai-profile-source-selected={selected ? "true" : "false"}
                              key={kind}
                            >
                              <input
                                aria-label={t("config.models.chatProfiles.sourceToggle", { profile: draftLabel, source: label })}
                                checked={selected}
                                data-paradev-ai-profile-id={profile.id}
                                data-paradev-ai-profile-source-kind={kind}
                                data-paradev-ai-profile-source-selected={selected ? "true" : "false"}
                                onChange={() =>
                                  setProfileDrafts((current) => ({
                                    ...current,
                                    [profile.id]: {
                                      ...(current[profile.id] ?? draft),
                                      sourceKinds: toggleSourceKind(current[profile.id]?.sourceKinds ?? selectedSourceKinds, kind, aiChatSourceKindOptions)
                                    }
                                  }))
                                }
                                type="checkbox"
                              />
                              <span>{label}</span>
                            </label>
                          );
                        })}
                      </div>
                      <small>{t("config.models.chatProfiles.sourcesDetail", { sources: sourceKinds })}</small>
                    </div>
                    <div className="config-ai-profile-footer">
                      <small>{sourceKinds}</small>
                      <div className="config-ai-profile-actions">
                        <button
                          aria-label={t("config.models.chatProfiles.resetAria", { profile: draftLabel })}
                          className="toolbar-button"
                          data-paradev-ai-profile-action="reset"
                          onClick={() => onResetAiChatProfile?.(profile.id)}
                          title={t("config.models.chatProfiles.resetAria", { profile: draftLabel })}
                          type="button"
                        >
                          <RotateCcw aria-hidden="true" size={14} />
                          {t("config.models.chatProfiles.reset")}
                        </button>
                        <button
                          className="toolbar-button primary"
                          data-paradev-ai-profile-action="save"
                          disabled={!hasDraftChanges}
                          onClick={() => onSaveAiChatProfile?.(profile.id, aiChatProfileSaveDraft(profile, draft, t, aiChatSourceKindOptions))}
                          type="button"
                        >
                          <Save aria-hidden="true" size={14} />
                          {t("config.models.chatProfiles.save")}
                        </button>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </SettingsPanel>
        </div>
      ) : null}

      {activeConfigId === "config-projects" ? (
        <div className="config-section-stack">
          <SettingsPanel icon={<SlidersHorizontal aria-hidden="true" size={16} />} title={t("config.projects.authoring.title")}>
            <SettingRow detail={t("config.projects.preferredLanguage.detail")} label={t("config.projects.preferredLanguage.label")}>
              <div className="config-project-language-control">
                <SelectField
                  className="config-inline-select"
                  disabled={preferredLanguageBusy || !activeProject.path.trim()}
                  label={t("config.projects.preferredLanguage.field")}
                  onChange={(event) => void onPreferredLanguageChange?.(event.target.value)}
                  options={projectLanguageOptions(t)}
                  value={activeProject.preferredLanguage ?? "en"}
                  variant="compact"
                />
                {preferredLanguageBusy ? (
                  <small role="status">{t("config.projects.preferredLanguage.saving")}</small>
                ) : null}
                {preferredLanguageError ? (
                  <small className="project-path error" role="alert">{preferredLanguageError}</small>
                ) : null}
              </div>
            </SettingRow>
          </SettingsPanel>
          <SettingsPanel icon={<Terminal aria-hidden="true" size={16} />} title={t("config.projects.paths.title")}>
            <SettingRow detail={activeProject.path} label={t("management.path.root")}>
              <PathActionValue
                display={<code>{activeProject.path}</code>}
                label={t("config.projects.pathLabel.root")}
                onOpenPath={onOpenPath}
                openTargetLabel={openTargetLabel}
                path={activeProject.path}
                pathStatusErrorByPath={pathStatusErrorByPath}
                pathStatusByPath={pathStatusByPath}
                t={t}
              />
            </SettingRow>
            <SettingRow detail={(activeProject.sourceRoots ?? []).join(", ") || t("config.value.pending")} label={t("management.path.source")}>
              <PathActionValue
                display={<span>{t("config.projects.pathCount.sourceRoots", { count: activeProject.sourceRoots?.length ?? 0 })}</span>}
                label={t("config.projects.pathLabel.source")}
                onOpenPath={onOpenPath}
                openTargetLabel={openTargetLabel}
                pathStatusErrorByPath={pathStatusErrorByPath}
                pathStatusByPath={pathStatusByPath}
                paths={activeProject.sourceRoots ?? []}
                t={t}
              />
            </SettingRow>
            <SettingRow detail={outputOpenPath || t("config.value.pending")} label={t("management.path.output")}>
              <PathActionValue
                display={<span>{t("status.ready")}</span>}
                label={t("config.projects.pathLabel.output")}
                onOpenPath={onOpenPath}
                openTargetLabel={openTargetLabel}
                path={outputOpenPath}
                pathStatusErrorByPath={pathStatusErrorByPath}
                pathStatusByPath={pathStatusByPath}
                statusMode="generated"
                t={t}
              />
            </SettingRow>
            <SettingRow detail={activeProject.buildRoot ?? t("config.value.pending")} label={t("management.path.build")}>
              <PathActionValue
                display={<span>{t("status.scaffold")}</span>}
                label={t("config.projects.pathLabel.build")}
                onOpenPath={onOpenPath}
                openTargetLabel={openTargetLabel}
                path={activeProject.buildRoot}
                pathStatusErrorByPath={pathStatusErrorByPath}
                pathStatusByPath={pathStatusByPath}
                statusMode="generated"
                t={t}
              />
            </SettingRow>
            <SettingRow detail={t("config.projects.hoi4LaunchMode.detail")} label={t("config.projects.hoi4LaunchMode.label")}>
              <ConfigRouteSelectField
                configKey={DESKTOP_CONFIG_KEYS.hoi4LaunchMode}
                helper={configFieldHelper}
                label={t("config.projects.hoi4LaunchMode.field")}
                onChange={(launchMode) =>
                  onSettingsChange?.({
                    ...settings,
                    hoi4: {
                      ...settings.hoi4,
                      launchMode: launchMode as ConfigHoi4LaunchMode
                    }
                  })
                }
                options={CONFIG_HOI4_LAUNCH_MODE_VALUES.map((value) => ({ label: hoi4LaunchModeOptionLabel(value, t), value }))}
                value={settings.hoi4.launchMode}
              />
            </SettingRow>
            <SettingRow detail={t("config.projects.hoi4GameRoot.detail")} label={t("config.projects.hoi4GameRoot.label")}>
              <ConfigRouteTextField
                configKey={DESKTOP_CONFIG_KEYS.hoi4GameRoot}
                helper={configFieldHelper}
                label={t("config.projects.hoi4GameRoot.field")}
                onChange={(gameRoot) =>
                  onSettingsChange?.({
                    ...settings,
                    hoi4: {
                      ...settings.hoi4,
                      gameRoot
                    }
                  })
                }
                placeholder={t("config.projects.hoi4GameRoot.placeholder")}
                action={
                  <span className="config-path-inline-actions">
                    <PathStatusPill
                      error={pathStatusErrorForPath(settings.hoi4.gameRoot, pathStatusErrorByPath)}
                      mode={settings.hoi4.gameRoot.trim() ? "required" : "steam"}
                      status={pathStatusForPath(settings.hoi4.gameRoot, pathStatusByPath)}
                      t={t}
                    />
                    {settings.hoi4.gameRoot.trim() ? (
                      <PathOpenButton
                        label={t("config.projects.pathLabel.hoi4Root")}
                        onOpenPath={onOpenPath}
                        openTargetLabel={openTargetLabel}
                        path={settings.hoi4.gameRoot}
                        error={pathStatusErrorForPath(settings.hoi4.gameRoot, pathStatusErrorByPath)}
                        status={pathStatusForPath(settings.hoi4.gameRoot, pathStatusByPath)}
                        t={t}
                      />
                    ) : null}
                  </span>
                }
                value={settings.hoi4.gameRoot}
              />
            </SettingRow>
          </SettingsPanel>
          <SettingsPanel icon={<Gauge aria-hidden="true" size={16} />} title={t("config.projects.buildDefaults.title")}>
            <SettingRow detail={t("config.projects.parallelism.detail")} label={t("config.projects.parallelism.label")}>
              <label className="config-number-field">
                <input
                  data-paradev-config-key={DESKTOP_CONFIG_KEYS.buildParallelism}
                  min={BUILD_PARALLELISM_MIN}
                  onChange={(event) =>
                    onSettingsChange?.({
                      ...settings,
                      build: {
                        ...settings.build,
                        parallelism: Number(event.target.value) || settings.build.parallelism
                      }
                    })
                  }
                  type="number"
                  value={settings.build.parallelism}
                />
                <small>{configFieldHelper}</small>
              </label>
            </SettingRow>
            <SettingRow detail={t("config.projects.strictMetadata.detail")} label={t("config.projects.strictMetadata.label")}>
              <label className="config-checkbox-field">
                <input
                  checked={settings.build.strictMetadata}
                  data-paradev-config-key={DESKTOP_CONFIG_KEYS.buildStrictMetadata}
                  onChange={(event) =>
                    onSettingsChange?.({
                      ...settings,
                      build: {
                        ...settings.build,
                        strictMetadata: event.target.checked
                      }
                    })
                  }
                  type="checkbox"
                />
                <span>{t("config.projects.strictMetadata.enabled")}</span>
                <small>{configFieldHelper}</small>
              </label>
            </SettingRow>
          </SettingsPanel>
        </div>
      ) : null}

      {activeConfigId === "config-module-defaults" ? (
        <div className="config-section-stack">
          <SettingsPanel icon={<Gauge aria-hidden="true" size={16} />} title={t("config.moduleDefaults.sizes.title")}>
            <p>{t("config.moduleDefaults.sizes.detail", { project: activeProject.name })}</p>
            <ModuleDefaultTable configFieldHelper={configFieldHelper} onSettingsChange={onSettingsChange} rows={localModuleDefaults} settings={settings} t={t} />
          </SettingsPanel>
          {sharedModuleDefaults.length > 0 ? (
            <SettingsPanel icon={<Images aria-hidden="true" size={16} />} title={t("config.moduleDefaults.cache.title")}>
              <p>{t("config.moduleDefaults.cache.detail")}</p>
              <ModuleDefaultTable configFieldHelper={configFieldHelper} onSettingsChange={onSettingsChange} rows={sharedModuleDefaults} settings={settings} t={t} />
            </SettingsPanel>
          ) : null}
        </div>
      ) : null}

      {activeConfigId === "config-dependencies" ? (
        <div className="config-section-stack">
          <SettingsPanel icon={<Download aria-hidden="true" size={16} />} title={t("config.dependencies.title")}>
            <DependencyRow busy={dependencyBusyId === "imagemagick"} status={dependencyStatusById.imagemagick} t={t} onCheck={() => onCheckDependency("imagemagick")} onInstall={() => onInstallDependency("imagemagick")} />
          </SettingsPanel>
        </div>
      ) : null}
    </section>
  );
}

function SettingsPanel({ children, icon, title }: { children: ReactNode; icon: ReactNode; title: string }) {
  return (
    <section className="config-panel">
      <div className="config-panel-heading">
        <span className="panel-icon">{icon}</span>
        <h3>{title}</h3>
      </div>
      {children}
    </section>
  );
}

function ModuleDefaultTable({
  configFieldHelper,
  onSettingsChange,
  rows,
  settings,
  t
}: {
  configFieldHelper: string;
  onSettingsChange?: (settings: ConfigPageSettings) => void;
  rows: ConfigPageSettings["moduleDefaults"];
  settings: ConfigPageSettings;
  t: Translator;
}) {
  return (
    <div className="config-table">
      {rows.map((row) => (
        <div className="config-table-row module-default-row" key={row.id}>
          <span>
            <strong>{t(row.labelKey)}</strong>
            <small>{t(row.detailKey)}</small>
          </span>
          <label>
            <input
              data-paradev-config-key={row.configKey}
              min={moduleDefaultMinimum(row)}
              onChange={(event) =>
                onSettingsChange?.({
                  ...settings,
                  moduleDefaults: settings.moduleDefaults.map((item) => (item.id === row.id ? { ...item, value: Number(event.target.value) || item.value } : item))
                })
              }
              type="number"
              value={row.value}
            />
            <small>{row.unit}</small>
            <small className="config-field-helper">{row.configKey ? configFieldHelper : t("config.field.desktopOnly")}</small>
          </label>
        </div>
      ))}
    </div>
  );
}

function ConfigPersistenceIndicator({ persistence, t }: { persistence: ConfigPersistenceStatus; t: Translator }) {
  const detail = configPersistenceDetail(persistence, t);
  return (
    <span className="config-persistence-status" role={persistence.state === "error" ? "alert" : undefined}>
      <span className={`status-pill ${configPersistencePillClass(persistence.state)}`}>{t(persistence.labelKey, persistence.labelParams)}</span>
      {detail ? <small>{detail}</small> : null}
    </span>
  );
}

function configPersistenceDetail(persistence: ConfigPersistenceStatus, t: Translator) {
  if (persistence.state === "error") {
    return persistence.detail ?? t("config.page.saveFailedDetail");
  }
  return persistence.detail ?? "";
}

function SettingRow({ children, detail, label }: { children: ReactNode; detail: string; label: string }) {
  return (
    <div className="config-setting-row">
      <span>
        <strong>{label}</strong>
        <small>{detail}</small>
      </span>
      <div>{children}</div>
    </div>
  );
}

function KeyValue({ label, value }: { label: string; value: string }) {
  return (
    <div className="config-kv">
      <small>{label}</small>
      <code>{value}</code>
    </div>
  );
}

function cliOutputOptionLabel(value: ConfigCliOutput, t: Translator): string {
  return value === "json" ? t("config.general.cliOutput.json") : t("config.general.cliOutput.yaml");
}

function hoi4LaunchModeOptionLabel(value: ConfigHoi4LaunchMode, t: Translator): string {
  return value === "local" ? t("config.projects.hoi4LaunchMode.local") : t("config.projects.hoi4LaunchMode.steam");
}

const PROJECT_LANGUAGE_ROWS = [
  ["en", "config.projects.preferredLanguage.english"],
  ["fr", "config.projects.preferredLanguage.french"],
  ["de", "config.projects.preferredLanguage.german"],
  ["ru", "config.projects.preferredLanguage.russian"],
  ["es", "config.projects.preferredLanguage.spanish"],
  ["pl", "config.projects.preferredLanguage.polish"],
  ["pt_br", "config.projects.preferredLanguage.brazilianPortuguese"],
  ["zh", "config.projects.preferredLanguage.simplifiedChinese"],
  ["ja", "config.projects.preferredLanguage.japanese"],
  ["ko", "config.projects.preferredLanguage.korean"]
] as const satisfies ReadonlyArray<readonly [string, TranslationKey]>;

function projectLanguageOptions(t: Translator) {
  return PROJECT_LANGUAGE_ROWS.map(([value, labelKey]) => ({
    label: t(labelKey),
    value
  }));
}

function moduleDefaultMinimum(row: ConfigPageSettings["moduleDefaults"][number]): number {
  return row.configKey ? desktopConfigMinimum(row.configKey, LOCAL_MODULE_DEFAULT_MIN) : LOCAL_MODULE_DEFAULT_MIN;
}

type PathStatusMode = "generated" | "required" | "steam";

function PathActionValue({
  display,
  label,
  onOpenPath,
  openTargetLabel,
  path,
  pathStatusErrorByPath,
  pathStatusByPath,
  paths,
  statusMode = "required",
  t
}: {
  display: ReactNode;
  label: string;
  onOpenPath?: (path: string) => void;
  openTargetLabel: string;
  path?: string;
  pathStatusErrorByPath: Record<string, string>;
  pathStatusByPath: Record<string, DesktopPathStatusPayload>;
  paths?: string[];
  statusMode?: PathStatusMode;
  t: Translator;
}) {
  const cleanPaths = (paths ?? (path ? [path] : [])).map((row) => row.trim()).filter(Boolean);
  const statuses = cleanPaths.map((row) => pathStatusForPath(row, pathStatusByPath));
  const errors = cleanPaths.map((row) => pathStatusErrorForPath(row, pathStatusErrorByPath));
  return (
    <span className="config-path-action-value">
      {display}
      <PathStatusPill
        error={cleanPaths.length === 1 ? errors[0] : undefined}
        errors={errors}
        mode={statusMode}
        status={cleanPaths.length === 1 ? statuses[0] : undefined}
        statuses={statuses}
        t={t}
        total={cleanPaths.length}
      />
      {cleanPaths.map((row, index) => {
        const status = statuses[index];
        const error = errors[index];
        return (
          <PathOpenButton
            error={error}
            index={cleanPaths.length > 1 ? index + 1 : undefined}
            key={`${row}:${index}`}
            label={label}
            onOpenPath={onOpenPath}
            openTargetLabel={openTargetLabel}
            path={row}
            status={status}
            t={t}
          />
        );
      })}
    </span>
  );
}

function PathOpenButton({
  error,
  index,
  label,
  onOpenPath,
  openTargetLabel,
  path,
  status,
  t
}: {
  error?: string;
  index?: number;
  label: string;
  onOpenPath?: (path: string) => void;
  openTargetLabel: string;
  path: string;
  status?: DesktopPathStatusPayload;
  t: Translator;
}) {
  const cleanPath = path.trim();
  const title = index
    ? t("config.projects.openPathIndexed", { index, label, path: cleanPath, target: openTargetLabel })
    : t("config.projects.openPathWithPath", { label, path: cleanPath, target: openTargetLabel });
  const disabled = !onOpenPath || !cleanPath || Boolean(error) || status?.openable === false;
  return (
    <button aria-label={title} className="config-path-open-button" data-config-open-path={cleanPath} disabled={disabled} onClick={() => onOpenPath?.(cleanPath)} title={title} type="button">
      <FolderOpen aria-hidden="true" size={13} />
    </button>
  );
}

function PathStatusPill({
  error,
  errors,
  mode,
  status,
  statuses,
  t,
  total
}: {
  error?: string;
  errors?: Array<string | undefined>;
  mode: PathStatusMode;
  status?: DesktopPathStatusPayload;
  statuses?: Array<DesktopPathStatusPayload | undefined>;
  t: Translator;
  total?: number;
}) {
  const summary = pathStatusSummary(mode, status, statuses, total, t, error, errors);
  return (
    <span aria-live="polite" className={`config-path-status ${summary.className}`} title={summary.title}>
      {summary.label}
    </span>
  );
}

function ConfigRouteTextField({
  action,
  configKey,
  helper,
  label,
  onChange,
  placeholder,
  value
}: {
  action?: ReactNode;
  configKey: DesktopConfigKey;
  helper: string;
  label: string;
  onChange: (value: string) => void;
  placeholder?: string;
  value: string;
}) {
  return (
    <label className="config-route-field">
      <span>{label}</span>
      <span className="config-route-input-row">
        <input data-paradev-config-key={configKey} onChange={(event) => onChange(event.target.value)} placeholder={placeholder} value={value} />
        {action}
      </span>
      <small>{helper}</small>
    </label>
  );
}

function pathStatusForPath(path: string | undefined, statuses: Record<string, DesktopPathStatusPayload>): DesktopPathStatusPayload | undefined {
  const cleanPath = path?.trim();
  return cleanPath ? statuses[cleanPath] : undefined;
}

function pathStatusErrorForPath(path: string | undefined, errors: Record<string, string>): string | undefined {
  const cleanPath = path?.trim();
  return cleanPath ? errors[cleanPath] : undefined;
}

function pathStatusSummary(
  mode: PathStatusMode,
  status: DesktopPathStatusPayload | undefined,
  statuses: Array<DesktopPathStatusPayload | undefined> | undefined,
  total: number | undefined,
  t: Translator,
  error?: string,
  errors?: Array<string | undefined>
): { className: string; label: string; title: string } {
  if (mode === "steam") {
    return {
      className: "neutral",
      label: t("config.projects.pathStatus.steam"),
      title: t("config.projects.pathStatus.title.steam")
    };
  }
  const firstError = error ?? errors?.find((row): row is string => Boolean(row));
  if (firstError) {
    return {
      className: "warning",
      label: t("config.projects.pathStatus.failed"),
      title: firstError
    };
  }
  if (statuses && total && total > 1) {
    const readyCount = statuses.filter((row) => row?.openable && row.readable).length;
    if (readyCount === total) {
      return {
        className: "ready",
        label: t("config.projects.pathStatus.ready"),
        title: t("config.projects.pathStatus.title.ready")
      };
    }
    return {
      className: readyCount > 0 ? "warning" : "missing",
      label: t("config.projects.pathStatus.partial", { ready: readyCount, total }),
      title: t("config.projects.pathStatus.title.partial", { ready: readyCount, total })
    };
  }
  if (!status) {
    return {
      className: "checking",
      label: t("config.projects.pathStatus.checking"),
      title: t("config.projects.pathStatus.title.checking")
    };
  }
  if (status.openable && status.readable) {
    return {
      className: "ready",
      label: t("config.projects.pathStatus.ready"),
      title: t("config.projects.pathStatus.title.ready")
    };
  }
  if (mode === "generated" && !status.exists) {
    return {
      className: "neutral",
      label: t("config.projects.pathStatus.generated"),
      title: t("config.projects.pathStatus.title.generated")
    };
  }
  if (!status.exists) {
    return {
      className: "missing",
      label: t("config.projects.pathStatus.missing"),
      title: t("config.projects.pathStatus.title.missing")
    };
  }
  if (!status.readable) {
    return {
      className: "warning",
      label: t("config.projects.pathStatus.unreadable"),
      title: t("config.projects.pathStatus.title.unreadable")
    };
  }
  return {
    className: "warning",
    label: t("config.projects.pathStatus.wrongKind"),
    title: t("config.projects.pathStatus.title.wrongKind")
  };
}

function ConfigRouteSelectField({
  configKey,
  helper,
  label,
  onChange,
  options,
  value
}: {
  configKey: DesktopConfigKey;
  helper: string;
  label: string;
  onChange: (value: string) => void;
  options: Array<{ label: string; value: string }>;
  value: string;
}) {
  return (
    <div className="config-route-field">
      <span>{label}</span>
      <SelectField
        className="config-inline-select"
        data-paradev-config-key={configKey}
        label={label}
        onChange={(event) => onChange(event.target.value)}
        options={options}
        value={value}
        variant="compact"
      />
      <small>{helper}</small>
    </div>
  );
}

function MetricGrid({ rows }: { rows: Array<[string, number]> }) {
  return (
    <div className="config-metric-grid">
      {rows.map(([label, value]) => (
        <div className="config-metric" key={label}>
          <strong>{value}</strong>
          <small>{label}</small>
        </div>
      ))}
    </div>
  );
}

function DependencyRow({ busy, onCheck, onInstall, status, t }: { busy: boolean; onCheck: () => void; onInstall: () => void; status?: ConfigDependencyStatus; t: Translator }) {
  const current = status ?? {
    schema: "paradev.desktop.dependency.v1" as const,
    id: "imagemagick",
    installed: false,
    installCommand: ["brew", "install", "imagemagick"],
    installSupported: true,
    label: "ImageMagick",
    status: "unknown" as const
  };
  const command = current.installCommand.join(" ");
  const icon = current.installed ? <CheckCircle2 aria-hidden="true" size={14} /> : current.status === "error" ? <TriangleAlert aria-hidden="true" size={14} /> : <CircleDashed aria-hidden="true" size={14} />;

  return (
    <div className="config-dependency-row">
      <div>
        <span className={`status-pill ${current.installed ? "ready" : current.status === "error" ? "offline" : "planned"}`}>
          {icon}
          {current.installed ? t("config.dependencies.status.installed") : statusLabel(current.status, t)}
        </span>
        <h3>{current.label}</h3>
        <p>{current.detail ?? t("config.dependencies.imagemagick.detail")}</p>
        <div className="config-kv-grid">
          <KeyValue label={t("config.dependencies.path")} value={current.path || t("config.value.pending")} />
          <KeyValue label={t("config.dependencies.version")} value={current.version || t("config.value.pending")} />
          <KeyValue label={t("config.dependencies.installCommand")} value={command || t("config.value.pending")} />
        </div>
      </div>
      <div className="config-dependency-actions">
        <button className="toolbar-button" disabled={busy} onClick={onCheck} type="button">
          <RefreshCw aria-hidden="true" size={14} />
          {t("config.dependencies.check")}
        </button>
        <button className="toolbar-button primary" disabled={busy || current.installed || !current.installSupported} onClick={onInstall} type="button">
          <Download aria-hidden="true" size={14} />
          {t("config.dependencies.install")}
        </button>
      </div>
    </div>
  );
}

function configTitle(activeConfigId: string, t: Translator): string {
  const keyById: Record<string, Parameters<Translator>[0]> = {
    "config-appearance": "config.appearance.title",
    "config-dependencies": "config.dependencies.title",
    "config-general": "config.general.title",
    "config-models": "config.models.title",
    "config-module-defaults": "config.moduleDefaults.title",
    "config-projects": "config.projects.title"
  };
  return t(keyById[activeConfigId] ?? "config.general.title");
}

function openPathTargetLabel(openTarget: OpenPathTarget, t: Translator): string {
  return t(OPEN_PATH_TARGETS.find((target) => target.id === openTarget)?.labelKey ?? "openTarget.vscode");
}

function statusLabel(status: string, t: Translator): string {
  if (status === "ready") {
    return t("status.ready");
  }
  if (status === "warning") {
    return t("config.status.warning");
  }
  if (status === "error") {
    return t("config.status.error");
  }
  if (status === "missing") {
    return t("config.status.missing");
  }
  return t("config.status.unknown");
}

function statusPillClass(status: string): string {
  if (status === "ready") {
    return "ready";
  }
  if (status === "warning") {
    return "planned";
  }
  if (status === "error") {
    return "offline";
  }
  return "scaffold";
}

function configPersistencePillClass(state: string): string {
  if (state === "error") {
    return "offline";
  }
  if (state === "saving") {
    return "planned";
  }
  return "scaffold";
}

function llmPresetTitle(preset: string, t: Translator): string {
  const row = LLM_PRESET_ROWS.find((item) => item.preset === preset);
  return row ? t(row.labelKey) : preset || t("config.models.presets.chat.label");
}

function llmTestDetail(status: ConfigLlmStatus, t: Translator): string {
  const detail = status.testDetail.trim();
  if (!detail) {
    return t("config.models.testHint");
  }
  const runningDetail = llmTestRunningDetail(status.gateway, status.provider, status.model, status.preset, t);
  if (detail === runningDetail || detail === legacyLlmTestRunningDetail(status.provider, status.model, t)) {
    return runningDetail;
  }
  if (status.status === "ready") {
    return t("config.models.testResult.ready");
  }
  if (status.status === "error") {
    return t("config.models.testResult.error");
  }
  if (status.status === "warning") {
    return status.resultCode === "empty_response" ? t("config.models.testResult.empty") : t("config.models.testResult.warning");
  }
  return t("config.models.testHint");
}

function llmTestRunningDetail(gateway: string, provider: string, model: string, preset: string, t: Translator): string {
  return t("config.models.testRunning", { route: aiRouteLabelWithPreset({ gateway, model, preset, provider, t }) });
}

function legacyLlmTestRunningDetail(provider: string, model: string, t: Translator): string {
  return t("config.models.testRunning", { route: `${provider} / ${model}` });
}

function aiChatProfileBadgeLabel(profileId: string, defaultRole: string, profileLabel: string, t: Translator): string {
  return profileId === defaultRole ? `${profileLabel} · ${t("config.models.chatProfiles.defaultRole")}` : profileLabel;
}

function sourceKindLabels(sourceKinds: string[], t: Translator, sourceKindRows: readonly AiChatSourceKindRowLike[] = []): string {
  const labels = sourceKinds.map((kind) => sourceKindLabel(kind, t, sourceKindRows)).filter(Boolean);
  return labels.length > 0 ? labels.join(" / ") : t("config.models.chatProfiles.noSources");
}

function sourceKindLabel(kind: string, t: Translator, sourceKindRows: readonly AiChatSourceKindRowLike[] = []): string {
  return aiChatProfileSourceKindLabel(kind, t, sourceKindRows);
}

function toggleSourceKind(sourceKinds: string[], kind: string, sourceKindOrder: readonly string[]): string[] {
  return canonicalAiChatProfileSourceKinds(sourceKinds.includes(kind) ? sourceKinds.filter((sourceKind) => sourceKind !== kind) : [...sourceKinds, kind], sourceKindOrder);
}
