import { FolderOpen, PackagePlus } from "lucide-react";
import type { TranslationKey, Translator } from "../i18n";
import { moduleNavigationGroupKey, moduleNavigationGroupOrder } from "../moduleNavigationGroups";
import type { PanelOption, ProjectOption } from "../types";
import { IconButton } from "./ui/IconButton";
import { OptionList } from "./ui/OptionList";
import { SelectField } from "./ui/SelectField";

type ProjectPanelProps = {
  activeOption: string;
  activeProject: ProjectOption;
  blocked?: boolean;
  diagramOptions?: PanelOption[];
  isOpen: boolean;
  mode: "modules" | "config";
  onImportProject: () => void;
  onOpenProject: () => void;
  onPinOption?: (id: string) => void;
  onReorderOptions?: (fromId: string, toId: string) => void;
  onSelectOption: (id: string) => void;
  onSelectProject: (id: string) => void;
  options: PanelOption[];
  projectError: string;
  projectImporting: boolean;
  projectLoading: boolean;
  projectNotice?: string;
  projectNoticeDetail?: string;
  projectOpenError: string;
  projectOpening: boolean;
  projectOptions: ProjectOption[];
  t: Translator;
};

const panelTitleKey: Record<ProjectPanelProps["mode"], TranslationKey> = {
  modules: "modules.section.title",
  config: "config.section.title"
};

const panelAriaKey: Record<ProjectPanelProps["mode"], TranslationKey> = {
  modules: "panel.project.aria",
  config: "panel.config.aria"
};

export function ProjectPanel({
  activeOption,
  activeProject,
  blocked = false,
  isOpen,
  mode,
  onImportProject,
  onOpenProject,
  onPinOption,
  onReorderOptions,
  onSelectOption,
  onSelectProject,
  options,
  projectError,
  projectImporting,
  projectLoading,
  projectNotice = "",
  projectNoticeDetail = "",
  projectOpenError,
  projectOpening,
  projectOptions,
  t
}: ProjectPanelProps) {
  const projectBusy = projectImporting || projectOpening || projectLoading;
  const projectBusyStatus = projectImporting
    ? t("project.onboarding.installing")
    : projectOpening
      ? t("project.openingProject", { project: activeProject.name })
      : projectLoading
        ? t("project.loadingProject", { project: activeProject.name })
        : "";
  const projectPathStatus =
    projectError || projectOpenError || projectNotice || activeProject.path;
  const projectPathDetail =
    projectError ||
    projectOpenError ||
    projectNoticeDetail ||
    projectNotice ||
    activeProject.path;
  const projectPathClassName =
    projectError || projectOpenError
      ? "project-path error"
      : projectNotice
        ? "project-path notice"
        : "project-path";
  const panelHidden = blocked || !isOpen;
  const panelOptions = mode === "modules" ? orderedModuleOptions(options) : options;

  return (
    <aside aria-hidden={panelHidden} className={isOpen ? "project-panel" : "project-panel collapsed"} inert={panelHidden} aria-label={t(panelAriaKey[mode])}>
      <div aria-busy={projectBusy} className="project-picker">
        <p className="label">{t("project.active.label")}</p>
        <div className="project-picker-row">
          <SelectField
            className="project-select-field"
            controlTitle={activeProject.name}
            disabled={projectBusy}
            label={t("project.active.aria")}
            onChange={(event) => onSelectProject(event.target.value)}
            options={projectSelectOptions(projectOptions)}
            value={activeProject.id}
          />
          <IconButton
            disabled={projectBusy}
            label={t("project.onboarding.installAction")}
            onClick={onImportProject}
          >
            <PackagePlus aria-hidden="true" size={16} />
          </IconButton>
          <IconButton disabled={projectBusy} label={t("project.action.open")} onClick={onOpenProject}>
            <FolderOpen aria-hidden="true" size={16} />
          </IconButton>
        </div>
        {projectBusy ? (
          <div aria-live="polite" className="project-picker-progress" role="status">
            <span aria-hidden="true" className="project-picker-progress-orbit">
              <span />
              <span />
              <span />
            </span>
            <span>{projectBusyStatus}</span>
          </div>
        ) : null}
        <small
          aria-live={projectNotice ? "polite" : undefined}
          className={projectPathClassName}
          role={projectNotice ? "status" : undefined}
          title={projectPathDetail}
        >
          {projectPathStatus}
        </small>
      </div>

      <section className="panel-section">
        <div className="section-title">
          <span>{t(panelTitleKey[mode])}</span>
          <small>{options.length}</small>
        </div>
        <OptionList
          activeId={activeOption}
          defaultCollapsedGroupKeys={moduleNavigationGroupOrder}
          grouped
          items={panelOptions}
          onDoubleSelect={onPinOption}
          onReorder={onReorderOptions}
          onSelect={onSelectOption}
          reorderable={Boolean(onReorderOptions)}
          t={t}
        />
      </section>
    </aside>
  );
}

function orderedModuleOptions(options: readonly PanelOption[]): PanelOption[] {
  const groupOrder = new Map<TranslationKey, number>(
    moduleNavigationGroupOrder.map((groupKey, index) => [groupKey, index])
  );
  return options
    .map((option, index) => ({
      index,
      option: {
        ...option,
        groupKey: option.groupKey ?? moduleNavigationGroupKey(undefined)
      }
    }))
    .sort(
      (left, right) =>
        (groupOrder.get(left.option.groupKey) ?? moduleNavigationGroupOrder.length) -
          (groupOrder.get(right.option.groupKey) ?? moduleNavigationGroupOrder.length) ||
        left.index - right.index
    )
    .map(({ option }) => option);
}

export function projectSelectOptions(projectOptions: readonly ProjectOption[]): Array<{ label: string; value: string }> {
  const projectIdCounts = new Map<string, number>();
  for (const project of projectOptions) {
    projectIdCounts.set(project.projectId, (projectIdCounts.get(project.projectId) ?? 0) + 1);
  }
  return projectOptions.map((project) => ({
    label: projectIdCounts.get(project.projectId) === 1 ? project.name : `${project.name} — ${project.path}`,
    value: project.id
  }));
}
