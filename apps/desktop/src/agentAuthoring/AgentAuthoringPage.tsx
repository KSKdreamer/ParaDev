import {
  Bot,
  Check,
  CheckCircle2,
  CircleDashed,
  Clipboard,
  Code2,
  FileText,
  GitBranch,
  Layers3,
  MessageSquareText,
  ShieldCheck,
  Sparkles
} from "lucide-react";
import { useEffect, useState, type ReactNode } from "react";
import { IconButton } from "../components/ui/IconButton";
import type { Translator } from "../i18n";
import type {
  ProjectBrowserPayload,
  ProjectOption,
  ProjectTemplatesPayload
} from "../types";
import {
  fallbackAgentAuthoringInfo,
  loadAgentAuthoringInfo,
  mcpCommandText,
  type AgentAuthoringSkillRuntime
} from "./service";

type AgentAuthoringPageProps = {
  activeProject: ProjectOption;
  browser: ProjectBrowserPayload | null;
  onOpenAiChat: () => void;
  onOpenEditing: () => void;
  templates: ProjectTemplatesPayload | null;
  t: Translator;
};

type CopyTarget = "command" | "prompt" | null;

export function AgentAuthoringPage({
  activeProject,
  browser,
  onOpenAiChat,
  onOpenEditing,
  templates,
  t
}: AgentAuthoringPageProps) {
  const [copiedTarget, setCopiedTarget] = useState<CopyTarget>(null);
  const [copyError, setCopyError] = useState("");
  const [runtimeError, setRuntimeError] = useState("");
  const [runtimeLoading, setRuntimeLoading] = useState(true);
  const [runtimeInfo, setRuntimeInfo] = useState(() =>
    fallbackAgentAuthoringInfo(activeProject.path)
  );
  const metrics = agentAuthoringMetrics(browser, templates);
  const mcpCommand = mcpCommandText(runtimeInfo.mcp);
  const projectPrompt = agentPrompt(activeProject, runtimeInfo.skill);
  const runtimeReady =
    runtimeInfo.mcp.available && runtimeInfo.skill.available;

  useEffect(() => {
    let cancelled = false;
    setRuntimeLoading(true);
    setRuntimeError("");
    setRuntimeInfo(fallbackAgentAuthoringInfo(activeProject.path));
    void loadAgentAuthoringInfo(activeProject.path)
      .then((payload) => {
        if (!cancelled) {
          setRuntimeInfo(payload);
        }
      })
      .catch(() => {
        if (!cancelled) {
          setRuntimeError(t("agents.runtime.error"));
        }
      })
      .finally(() => {
        if (!cancelled) {
          setRuntimeLoading(false);
        }
      });
    return () => {
      cancelled = true;
    };
  }, [activeProject.path, t]);

  const handleCopy = async (target: Exclude<CopyTarget, null>, value: string) => {
    setCopyError("");
    try {
      if (!navigator.clipboard?.writeText) {
        throw new Error("clipboard unavailable");
      }
      await navigator.clipboard.writeText(value);
      setCopiedTarget(target);
    } catch {
      setCopiedTarget(null);
      setCopyError(t("agents.copy.error"));
    }
  };

  return (
    <section className="agents-page" aria-label={t("agents.aria")}>
      <header className="agents-page-header">
        <div>
          <p className="label">{t("agents.header.label")}</p>
          <h2>{t("agents.header.title")}</h2>
          <p>
            <strong>{activeProject.name}</strong>
            <span>{t("agents.header.detail")}</span>
          </p>
        </div>
        <button className="toolbar-button primary" onClick={onOpenAiChat} type="button">
          <MessageSquareText aria-hidden="true" size={14} />
          {t("agents.action.openChat")}
        </button>
      </header>

      <div className="agents-metrics" aria-label={t("agents.metrics.aria")}>
        <AgentMetric
          icon={<Layers3 aria-hidden="true" size={16} />}
          label={t("agents.metrics.families")}
          value={metrics.familyCount}
        />
        <AgentMetric
          icon={<Sparkles aria-hidden="true" size={16} />}
          label={t("agents.metrics.templates")}
          value={metrics.authoringTemplateCount}
        />
        <AgentMetric
          icon={<GitBranch aria-hidden="true" size={16} />}
          label={t("agents.metrics.diagrams")}
          value={metrics.diagramFamilyCount}
        />
      </div>

      <div className="agents-content-grid">
        <section className="agents-section agents-ai-section">
          <div className="agents-section-heading">
            <span className="panel-icon">
              <Bot aria-hidden="true" size={16} />
            </span>
            <div>
              <p className="label">{t("agents.ai.label")}</p>
              <h3>{t("agents.ai.title")}</h3>
            </div>
          </div>
          <p>{t("agents.ai.body")}</p>
          <div className="agents-safety-note">
            <ShieldCheck aria-hidden="true" size={16} />
            <span>{t("agents.ai.safety")}</span>
          </div>
          <div className="agents-example">
            <p className="label">{t("agents.example.label")}</p>
            <blockquote>{t("agents.example.prompt")}</blockquote>
          </div>
          <button className="toolbar-button" onClick={onOpenEditing} type="button">
            <Layers3 aria-hidden="true" size={14} />
            {t("agents.action.openEditing")}
          </button>
        </section>

        <section className="agents-section">
          <div className="agents-section-heading">
            <span className="panel-icon">
              <Code2 aria-hidden="true" size={16} />
            </span>
            <div>
              <p className="label">{t("agents.external.label")}</p>
              <h3>{t("agents.external.title")}</h3>
            </div>
          </div>
          <p>{t("agents.external.body")}</p>
          <div
            className={
              runtimeReady
                ? "agents-runtime-status ready"
                : "agents-runtime-status"
            }
          >
            {runtimeReady ? (
              <CheckCircle2 aria-hidden="true" size={15} />
            ) : (
              <CircleDashed aria-hidden="true" size={15} />
            )}
            <span>
              <strong>
                {runtimeLoading
                  ? t("agents.runtime.loading")
                  : runtimeReady
                    ? t("agents.runtime.ready")
                    : t("agents.runtime.fallback")}
              </strong>
              <small>{t("agents.runtime.detail")}</small>
            </span>
          </div>
          <CopyRow
            copied={copiedTarget === "command"}
            label={t("agents.external.command")}
            onCopy={() => void handleCopy("command", mcpCommand)}
            t={t}
            value={mcpCommand}
          />
          {runtimeInfo.mcp.cwd ? (
            <small className="agents-runtime-cwd">
              {t("agents.runtime.cwd")} <code>{runtimeInfo.mcp.cwd}</code>
            </small>
          ) : null}
          <div className="agents-skill">
            <FileText aria-hidden="true" size={16} />
            <span>
              <strong>{runtimeInfo.skill.invocation}</strong>
              <small>{t("agents.skill.body")}</small>
              <code>{runtimeInfo.skill.path}</code>
            </span>
          </div>
          <CopyRow
            copied={copiedTarget === "prompt"}
            label={t("agents.prompt.label")}
            onCopy={() => void handleCopy("prompt", projectPrompt)}
            t={t}
            value={projectPrompt}
          />
          {copyError ? (
            <small className="agents-copy-error" role="alert">
              {copyError}
            </small>
          ) : null}
          {runtimeError ? (
            <small className="agents-copy-error" role="alert">
              {runtimeError}
            </small>
          ) : null}
        </section>
      </div>

      <section className="agents-workflow" aria-label={t("agents.workflow.aria")}>
        <div>
          <p className="label">{t("agents.workflow.label")}</p>
          <h3>{t("agents.workflow.title")}</h3>
        </div>
        <ol>
          <AgentWorkflowStep
            body={t("agents.workflow.discover.body")}
            index="1"
            title={t("agents.workflow.discover.title")}
          />
          <AgentWorkflowStep
            body={t("agents.workflow.plan.body")}
            index="2"
            title={t("agents.workflow.plan.title")}
          />
          <AgentWorkflowStep
            body={t("agents.workflow.review.body")}
            index="3"
            title={t("agents.workflow.review.title")}
          />
          <AgentWorkflowStep
            body={t("agents.workflow.apply.body")}
            index="4"
            title={t("agents.workflow.apply.title")}
          />
        </ol>
      </section>
    </section>
  );
}

function AgentMetric({
  icon,
  label,
  value
}: {
  icon: ReactNode;
  label: string;
  value: number | null;
}) {
  return (
    <div className="agents-metric">
      <span className="panel-icon">{icon}</span>
      <span>
        <strong>{value ?? "—"}</strong>
        <small>{label}</small>
      </span>
    </div>
  );
}

function CopyRow({
  copied,
  label,
  onCopy,
  t,
  value
}: {
  copied: boolean;
  label: string;
  onCopy: () => void;
  t: Translator;
  value: string;
}) {
  const actionLabel = copied
    ? t("agents.copy.copied")
    : t("agents.copy.action", { label });
  return (
    <div className="agents-copy-row">
      <span>
        <small>{label}</small>
        <code>{value}</code>
      </span>
      <IconButton label={actionLabel} onClick={onCopy}>
        {copied ? <Check aria-hidden="true" size={14} /> : <Clipboard aria-hidden="true" size={14} />}
      </IconButton>
    </div>
  );
}

function AgentWorkflowStep({
  body,
  index,
  title
}: {
  body: string;
  index: string;
  title: string;
}) {
  return (
    <li>
      <span aria-hidden="true">{index}</span>
      <div>
        <strong>{title}</strong>
        <small>{body}</small>
      </div>
    </li>
  );
}

export function agentAuthoringMetrics(
  browser: ProjectBrowserPayload | null,
  templates: ProjectTemplatesPayload | null
) {
  return {
    familyCount: browser
      ? browser.families.filter((family) => family.visible !== false).length
      : null,
    authoringTemplateCount: templates
      ? templates.templates.filter((template) => template.authoring_ready === true)
          .length
      : null,
    diagramFamilyCount: browser
      ? browser.families.filter(
          (family) => family.visible !== false && Boolean(family.diagram)
        ).length
      : null
  };
}

export function agentPrompt(
  project: ProjectOption,
  skill: Pick<AgentAuthoringSkillRuntime, "invocation" | "path"> = {
    invocation: "$paradev-authoring",
    path: ".agents/skills/paradev-authoring/SKILL.md"
  }
) {
  const identity = project.path || project.projectId || project.id;
  return `Use ${skill.invocation} from ${skill.path} to author modules and collections for ${project.name} at ${identity}. Discover Registry templates first, dry-plan every change, and wait for my review before applying it.`;
}
