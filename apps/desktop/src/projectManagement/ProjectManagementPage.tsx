import { CheckCircle2, ChevronDown, ChevronRight, FileCode2, FolderOpen, Hammer, Power } from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import { localizedParaDevServiceError } from "../desktopBridgeErrors";
import type { TranslationKey, Translator } from "../i18n";
import { hasDesktopBackend, openProjectPath, type OpenPathTarget } from "../services/paradev";
import type { ModuleStatus, ProjectBrowserPayload, ProjectOption } from "../types";

type ProjectManagementPageProps = {
  activeProject: ProjectOption;
  browser: ProjectBrowserPayload | null;
  onActivateProject: (id: string) => void;
  onOpenBuildPage: () => void;
  openTarget: OpenPathTarget;
  projectOptions: ProjectOption[];
  t: Translator;
};

type ProjectPathRow = {
  id: string;
  kind: "root" | "source" | "output" | "build" | "manifest";
  labelKey: TranslationKey;
  labelParams?: Record<string, string | number>;
  path: string;
};

const statusKey: Record<ModuleStatus, TranslationKey> = {
  ready: "status.ready",
  scaffold: "status.scaffold",
  planned: "status.planned",
  offline: "status.offline"
};

export function ProjectManagementPage({ activeProject, browser, onActivateProject, onOpenBuildPage, openTarget, projectOptions, t }: ProjectManagementPageProps) {
  const activeProjectKey = projectIdentity(activeProject);
  const projects = useMemo(() => normalizeProjects(projectOptions, activeProject), [activeProject, projectOptions]);
  const [expandedProjectKeys, setExpandedProjectKeys] = useState<Set<string>>(() => new Set(activeProjectKey ? [activeProjectKey] : []));
  const [openError, setOpenError] = useState("");
  const desktopBackend = hasDesktopBackend();

  useEffect(() => {
    if (!activeProjectKey) {
      return;
    }
    setExpandedProjectKeys((current) => {
      if (current.has(activeProjectKey)) {
        return current;
      }
      const next = new Set(current);
      next.add(activeProjectKey);
      return next;
    });
  }, [activeProjectKey]);

  const toggleProject = (projectKey: string) => {
    setExpandedProjectKeys((current) => {
      const next = new Set(current);
      if (next.has(projectKey)) {
        next.delete(projectKey);
      } else {
        next.add(projectKey);
      }
      return next;
    });
  };

  const handleOpenPath = (path: string) => {
    if (!desktopBackend || !path) {
      return;
    }
    setOpenError("");
    openProjectPath(path, openTarget).catch((error: unknown) => {
      setOpenError(projectManagementOpenError(t, error));
    });
  };

  return (
    <section className="management-page" aria-label={t("management.aria")}>
      <header className="management-page-header">
        <div>
          <p className="label">{t("management.header.label")}</p>
          <h2>{t("management.header.title")}</h2>
          <p>
            <strong>{projects.length}</strong>
            <span>{t("management.header.detail", { count: projects.length })}</span>
          </p>
        </div>
      </header>

      <div className="management-project-list">
        {projects.map((project, projectIndex) => {
          const projectKey = projectIdentity(project);
          const projectDetailsId = `management-project-${projectIndex}`;
          const expanded = expandedProjectKeys.has(projectKey);
          const active = projectKey === activeProjectKey;
          const pathRows = projectPathRows(project);
          const stats = projectStats(project, active, browser);
          return (
            <article className={expanded ? "management-project-card expanded" : "management-project-card"} key={projectKey}>
              <button
                aria-controls={projectDetailsId}
                aria-expanded={expanded}
                className="management-project-toggle"
                onClick={() => toggleProject(projectKey)}
                type="button"
              >
                <span className="management-project-caret">{expanded ? <ChevronDown aria-hidden="true" size={16} /> : <ChevronRight aria-hidden="true" size={16} />}</span>
                <span className="management-project-title">
                  <strong>{project.name}</strong>
                  <small>{project.path}</small>
                </span>
                <span className="management-project-meta">
                  <span>
                    <small>{t("management.field.game")}</small>
                    <strong>{projectGameLabel(project.game, t)}</strong>
                  </span>
                  <span>
                    <small>{t("management.field.version")}</small>
                    <strong>{projectVersion(project) || t("management.version.unset")}</strong>
                  </span>
                </span>
                <span className={`status-pill ${active ? "ready" : project.status ?? "planned"}`}>{active ? t("management.status.active") : t("management.status.inactive")}</span>
              </button>

              {expanded ? (
                <div className="management-project-details" id={projectDetailsId}>
                  <div className="management-project-actions">
                    <button className="toolbar-button primary" disabled={active} onClick={() => onActivateProject(project.id)} type="button">
                      <Power aria-hidden="true" size={14} />
                      {active ? t("management.action.active") : t("management.action.activate")}
                    </button>
                    <button className="toolbar-button" onClick={onOpenBuildPage} type="button">
                      <Hammer aria-hidden="true" size={14} />
                      {t("management.action.build")}
                    </button>
                  </div>

                  <dl className="management-info-grid">
                    <div>
                      <dt>{t("management.field.projectRoot")}</dt>
                      <dd>{project.path}</dd>
                    </div>
                    <div>
                      <dt>{t("management.field.status")}</dt>
                      <dd>{active ? t("management.status.active") : projectStatusLabel(project, t)}</dd>
                    </div>
                    <div>
                      <dt>{t("management.field.sources")}</dt>
                      <dd>{t("management.value.count", { count: stats.sourceCount })}</dd>
                    </div>
                    <div>
                      <dt>{t("management.field.objects")}</dt>
                      <dd>{t("management.value.count", { count: stats.objectCount })}</dd>
                    </div>
                  </dl>

                  <div className="management-path-list" aria-label={t("management.paths.aria")}>
                    {pathRows.map((row) => (
                      <button className="management-path-row" disabled={!desktopBackend} key={`${projectKey}:${row.id}`} onClick={() => handleOpenPath(row.path)} title={row.path} type="button">
                        <span className="panel-icon">{row.kind === "source" ? <FileCode2 aria-hidden="true" size={15} /> : <FolderOpen aria-hidden="true" size={15} />}</span>
                        <span>
                          <strong>{t(row.labelKey, row.labelParams)}</strong>
                          <code>{row.path}</code>
                        </span>
                      </button>
                    ))}
                  </div>

                  {openError ? (
                    <small className="project-path error management-open-error" role="alert">
                      {openError}
                    </small>
                  ) : null}

                  {active ? (
                    <p className="management-active-note">
                      <CheckCircle2 aria-hidden="true" size={14} />
                      {t("management.active.detail", { project: project.name })}
                    </p>
                  ) : null}
                </div>
              ) : null}
            </article>
          );
        })}
      </div>
    </section>
  );
}

function normalizeProjects(projectOptions: ProjectOption[], activeProject: ProjectOption): ProjectOption[] {
  if (projectOptions.length === 0) {
    return [activeProject];
  }
  const activeProjectKey = projectIdentity(activeProject);
  if (projectOptions.some((project) => projectIdentity(project) === activeProjectKey)) {
    return projectOptions;
  }
  return [activeProject, ...projectOptions];
}

function projectIdentity(project: ProjectOption): string {
  return project.id;
}

function projectVersion(project: ProjectOption): string {
  return project.version?.trim() || descriptorVersion(project.descriptor?.mod_version) || "";
}

function projectGameLabel(game: string | undefined, t: Translator): string {
  const gameId = game?.trim();
  if (!gameId) {
    return t("management.value.unknown");
  }
  if (gameId.toLowerCase() === "hoi4") {
    return t("management.game.hoi4");
  }
  return gameId;
}

function descriptorVersion(value: string | string[] | undefined): string | undefined {
  if (typeof value !== "string") {
    return undefined;
  }
  const text = value.trim();
  if (!text) {
    return undefined;
  }
  return text.length > 1 && ["v", "V"].includes(text[0] ?? "") && /\d/.test(text[1] ?? "") ? text.slice(1) : text;
}

function projectPathRows(project: ProjectOption): ProjectPathRow[] {
  const rows: ProjectPathRow[] = [{ id: "root", kind: "root", labelKey: "management.path.root", path: project.path }];
  const sourceRoots = project.sourceRoots ?? [];
  sourceRoots.forEach((sourceRoot, index) => {
    rows.push({
      id: `source:${index}`,
      kind: "source",
      labelKey: sourceRoots.length > 1 ? "management.path.sourceIndexed" : "management.path.source",
      labelParams: { index: index + 1 },
      path: sourceRoot
    });
  });
  if (project.outputRoot) {
    rows.push({ id: "output", kind: "output", labelKey: "management.path.output", path: project.outputRoot });
  }
  if (project.buildRoot) {
    rows.push({ id: "build", kind: "build", labelKey: "management.path.build", path: project.buildRoot });
  }
  if (project.manifest) {
    rows.push({ id: "manifest", kind: "manifest", labelKey: "management.path.manifest", path: project.manifest });
  }
  return rows;
}

function projectStats(project: ProjectOption, active: boolean, browser: ProjectBrowserPayload | null): { objectCount: number; sourceCount: number } {
  if (!active || !browser || browser.project_id !== project.projectId || browser.root !== project.path) {
    return {
      objectCount: 0,
      sourceCount: project.sourceRoots?.length ?? 0
    };
  }
  return {
    objectCount: browser.items.length,
    sourceCount: browser.items.reduce((count, item) => count + item.source_count, 0)
  };
}

function projectStatusLabel(project: ProjectOption, t: Translator): string {
  return project.status ? t(statusKey[project.status]) : t("management.status.inactive");
}

export function projectManagementOpenError(t: Translator, error: unknown): string {
  return t("project.openFailed", { message: localizedParaDevServiceError(t, error) });
}
