import { type FormEvent, useEffect, useId, useMemo, useRef, useState } from "react";
import { ArrowRight, Bot, MessageCircle, PanelRightClose, PanelRightOpen, Send, User, X } from "lucide-react";
import { aiChatProfileDetail, aiChatProfileLabel, frontendAiChatContextKindsForProfileKind } from "../aiChatProfileText";
import { aiChatContextSourceLabel } from "../aiChatSourceKindText";
import type { AiChatSourceKindRowLike } from "../aiChatSourceKindText";
import { aiChatProfileOperationCards } from "../aiChatOperations";
import { aiRouteLabelWithPreset } from "../aiRouteText";
import { localizedParaDevServiceError } from "../desktopBridgeErrors";
import type { Translator } from "../i18n";
import type {
  ParaDevAiChatProposal,
  ParaDevAiChatProfile,
  ParaDevAiChatSource,
  ParaDevAiChatSourceKindRow
} from "../services/paradev";
import { SelectField } from "./ui/SelectField";

type ChatMessage = {
  id: number;
  proposal?: AiChatProposalReview;
  role: "assistant" | "user";
  text: string;
};

type AiChatRouteLabelInput = {
  gateway: string;
  model: string;
  preset: string;
  provider: string;
  t: Translator;
};

type FloatingChatShellProps = {
  activeProjectName: string;
  avoidInspector?: boolean;
  blocked?: boolean;
  contextSources?: ParaDevAiChatSource[];
  defaultRole?: string;
  dock?: FloatingChatDock;
  gateway: string;
  sourceKindRows?: ParaDevAiChatSourceKindRow[];
  onDockChange?: (dock: FloatingChatDock) => void;
  onOpenChange?: (open: boolean) => void;
  onOperationNavigate?: (navigation: AiChatOperationNavigation) => void;
  onProposalReview?: (proposal: AiChatProposalReview) => void | Promise<void>;
  model: string;
  onSend: (prompt: string, role: string, sources: ParaDevAiChatSource[]) => Promise<AiChatSendResult>;
  open?: boolean;
  preset: string;
  profileLoadError?: string | null;
  profiles?: ParaDevAiChatProfile[];
  provider: string;
  t: Translator;
};

export type FloatingChatDock = "floating" | "side";

export type AiChatOperationNavigation = {
  operationId: string;
  role: string;
  sources: ParaDevAiChatSource[];
};

export type AiChatProposalReview = {
  projectRoot: string;
  proposal: ParaDevAiChatProposal;
  role: string;
  sources: ParaDevAiChatSource[];
};

export type AiChatSendResult =
  | string
  | {
      proposal?: AiChatProposalReview;
      text: string;
    };

export type ChatComposerKeyState = {
  altKey?: boolean;
  ctrlKey?: boolean;
  isComposing?: boolean;
  key: string;
  metaKey?: boolean;
  shiftKey?: boolean;
};

export function shouldSubmitAiChatComposerKey(state: ChatComposerKeyState): boolean {
  return state.key === "Enter" && !state.shiftKey && !state.altKey && !state.isComposing && Boolean(state.metaKey || state.ctrlKey);
}

export function aiChatRouteLabel({ gateway, model, preset, provider, t }: AiChatRouteLabelInput): string {
  return aiRouteLabelWithPreset({ gateway, model, preset, provider, t });
}

export function FloatingChatShell({
  activeProjectName,
  avoidInspector = false,
  blocked = false,
  contextSources = [],
  defaultRole = "chat",
  dock = "floating",
  gateway,
  model,
  onDockChange,
  onOpenChange,
  onOperationNavigate,
  onProposalReview,
  onSend,
  open = false,
  preset,
  profileLoadError = null,
  profiles = [],
  provider,
  sourceKindRows = [],
  t
}: FloatingChatShellProps) {
  const [internalOpen, setInternalOpen] = useState(open);
  const [draft, setDraft] = useState("");
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const sourceOptions = useMemo(() => normalizedContextSources(contextSources), [contextSources]);
  const [selectedRole, setSelectedRole] = useState(() => initialSelectedRole(profiles, defaultRole));
  const appliedDefaultRoleRef = useRef(defaultRole);
  const selectedProfile = useMemo(() => profiles.find((profile) => profile.id === selectedRole), [profiles, selectedRole]);
  const roleOptions = useMemo(() => profiles.map((profile) => ({ label: aiChatProfileLabel(profile, t), value: profile.id })), [profiles, t]);
  const [selectedSourceIds, setSelectedSourceIds] = useState<string[]>(() => defaultSelectedSourceIds(sourceOptions, selectedProfile, sourceKindRows));
  const roleDetailId = useId();
  const previousSourceOptionsRef = useRef(sourceOptions);
  const previousRoleRef = useRef(selectedRole);
  const [sending, setSending] = useState(false);
  const [reviewingProposalId, setReviewingProposalId] = useState<number | null>(null);
  const [error, setError] = useState("");
  const isOpen = onOpenChange ? open : internalOpen;

  useEffect(() => {
    setInternalOpen(open);
  }, [open]);

  useEffect(() => {
    if (profiles.length === 0) {
      return;
    }
    const defaultChanged = appliedDefaultRoleRef.current !== defaultRole;
    setSelectedRole((current) => {
      if (defaultChanged && profiles.some((profile) => profile.id === defaultRole)) {
        return defaultRole;
      }
      return profiles.some((profile) => profile.id === current) ? current : initialSelectedRole(profiles, defaultRole);
    });
    appliedDefaultRoleRef.current = defaultRole;
  }, [defaultRole, profiles]);

  useEffect(() => {
    setSelectedSourceIds((current) => {
      if (previousRoleRef.current !== selectedRole) {
        return defaultSelectedSourceIds(sourceOptions, selectedProfile, sourceKindRows);
      }
      return nextSelectedSourceIdsForContextChange(current, previousSourceOptionsRef.current, sourceOptions, selectedProfile, sourceKindRows);
    });
    previousSourceOptionsRef.current = sourceOptions;
    previousRoleRef.current = selectedRole;
  }, [sourceKindRows, sourceOptions, selectedProfile, selectedRole]);

  if (blocked) {
    return null;
  }

  const shellClassName = ["ai-chat-shell", isOpen ? "open" : "", dock === "side" ? "dock-side" : "", avoidInspector ? "avoid-inspector" : ""].filter(Boolean).join(" ");
  const trimmedDraft = draft.trim();
  const selectedSources = sourceOptions.filter((source) => selectedSourceIds.includes(chatSourceId(source)));
  const selectedContextSummary = aiChatSelectedContextSummary(selectedSources, t, sourceKindRows);
  const dockToggleLabel = dock === "side" ? t("chat.float") : t("chat.dockSide");
  const routeLabel = aiChatRouteLabel({ gateway, model, preset, provider, t });
  const selectedProfileDetail = selectedProfile ? aiChatProfileDetail(selectedProfile, t) : "";
  const operationCards = aiChatProfileOperationCards(selectedProfile, t);

  const setOpen = (nextOpen: boolean) => {
    if (onOpenChange) {
      onOpenChange(nextOpen);
      return;
    }
    setInternalOpen(nextOpen);
  };

  const handleDockToggle = () => {
    onDockChange?.(dock === "side" ? "floating" : "side");
  };

  const handleRoleChange = (role: string) => {
    setSelectedRole(role);
    setSelectedSourceIds(defaultSelectedSourceIds(sourceOptions, profiles.find((profile) => profile.id === role), sourceKindRows));
  };

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!trimmedDraft || sending) {
      return;
    }

    const prompt = trimmedDraft;
    const id = Date.now();
    setMessages((current) => [...current, { id, role: "user", text: prompt }]);
    setDraft("");
    setSending(true);
    setError("");

    try {
      const result = await onSend(prompt, selectedRole, selectedSources);
      const reply = typeof result === "string" ? result : result.text;
      const proposal = typeof result === "string" ? undefined : result.proposal;
      setMessages((current) => [
        ...current,
        {
          id: id + 1,
          ...(proposal ? { proposal } : {}),
          role: "assistant",
          text: reply.trim() || t("chat.emptyReply")
        }
      ]);
    } catch (caught: unknown) {
      setError(localizedParaDevServiceError(t, caught));
    } finally {
      setSending(false);
    }
  };

  const handleProposalReview = async (
    messageId: number,
    proposal: AiChatProposalReview
  ) => {
    if (!onProposalReview || reviewingProposalId !== null) {
      return;
    }
    setReviewingProposalId(messageId);
    setError("");
    try {
      await onProposalReview(proposal);
    } catch (caught: unknown) {
      setError(localizedParaDevServiceError(t, caught));
    } finally {
      setReviewingProposalId(null);
    }
  };

  return (
    <aside className={shellClassName} data-paradev-chat-dock={dock} data-paradev-chat-shell="true">
      {isOpen ? (
        <section aria-label={t("chat.panel.aria")} className="ai-chat-panel" data-paradev-chat-panel="true">
          <header className="ai-chat-header">
            <span className="ai-chat-title">
              <Bot aria-hidden="true" size={16} />
              <span>{t("chat.title")}</span>
            </span>
            <span className="ai-chat-header-actions">
              <button
                aria-label={dockToggleLabel}
                className="icon-button ai-chat-dock-toggle"
                data-paradev-chat-dock-toggle="true"
                onClick={handleDockToggle}
                title={dockToggleLabel}
                type="button"
              >
                {dock === "side" ? <PanelRightOpen aria-hidden="true" size={15} /> : <PanelRightClose aria-hidden="true" size={15} />}
              </button>
              <button aria-label={t("chat.close")} className="icon-button ai-chat-close" onClick={() => setOpen(false)} title={t("chat.close")} type="button">
                <X aria-hidden="true" size={15} />
              </button>
            </span>
          </header>
          <div className="ai-chat-route">
            <span>{activeProjectName}</span>
            <span title={routeLabel}>{routeLabel}</span>
          </div>
          {profileLoadError ? (
            <p className="ai-chat-error" role="alert">
              {profileLoadError}
            </p>
          ) : null}
          {profiles.length > 0 ? (
            <div className="ai-chat-role">
              <span>{t("chat.role")}</span>
              <div className="ai-chat-role-control">
                <SelectField
                  className="ai-chat-role-select"
                  data-paradev-chat-role="true"
                  aria-describedby={selectedProfileDetail ? roleDetailId : undefined}
                  label={t("chat.role")}
                  onChange={(event) => handleRoleChange(event.currentTarget.value)}
                  options={roleOptions}
                  value={selectedRole}
                  variant="compact"
                />
                {selectedProfileDetail ? (
                  <small id={roleDetailId} title={selectedProfileDetail}>
                    {selectedProfileDetail}
                  </small>
                ) : null}
              </div>
            </div>
          ) : null}
          {operationCards.length > 0 ? (
            <div className="ai-chat-operation-row">
              <span>{t("chat.operations")}</span>
              <div className="ai-chat-operation-list">
                <small className="ai-chat-operation-note">{t("chat.operation.note")}</small>
                {operationCards.map((card) => (
                  <button
                    aria-label={t("chat.operation.openAria", {
                      safety: aiChatOperationSafetyLabel(card.operation.id, t),
                      title: aiChatOperationOpenLabel(card.operation.id, t)
                    })}
                    className="ai-chat-operation-card"
                    data-paradev-chat-operation-action="navigate"
                    data-paradev-chat-operation-id={card.operation.id}
                    data-paradev-chat-operation-mutates={card.mutates ? "true" : "false"}
                    data-paradev-chat-operation-passive="true"
                    data-paradev-chat-operation-rest={card.restLabel}
                    data-paradev-chat-operation-sdk={card.sdkLabel}
                    disabled={!onOperationNavigate}
                    key={card.operation.id}
                    onClick={() => onOperationNavigate?.({ operationId: card.operation.id, role: selectedRole, sources: selectedSources })}
                    title={`${aiChatOperationOpenLabel(card.operation.id, t)} · ${aiChatOperationSafetyLabel(card.operation.id, t)} · ${card.actionTitle} · ${card.operation.summary}`}
                    type="button"
                  >
                    <span className="ai-chat-operation-heading">
                      <strong>{card.actionTitle}</strong>
                      <code>{card.operation.id}</code>
                    </span>
                    <small>{card.operation.summary}</small>
                    <small className="ai-chat-operation-safety">{aiChatOperationSafetyLabel(card.operation.id, t)}</small>
                    <span className="ai-chat-operation-meta">
                      <span className={["ai-chat-operation-badge", card.mutates ? "write" : "read"].filter(Boolean).join(" ")}>
                        {card.mutates ? t("chat.operation.writeCapable") : t("chat.operation.readOnly")}
                      </span>
                      <span className="ai-chat-operation-open">
                        {aiChatOperationOpenLabel(card.operation.id, t)}
                        <ArrowRight aria-hidden="true" size={12} />
                      </span>
                      {card.sdkLabel ? <code>{card.sdkLabel}</code> : null}
                    </span>
                  </button>
                ))}
              </div>
            </div>
          ) : null}
          {sourceOptions.length > 0 ? (
            <div className="ai-chat-source-row">
              <span>{t("chat.sources")}</span>
              <div className="ai-chat-source-controls">
                <div className="ai-chat-source-list">
                  {sourceOptions.map((source) => {
                    const sourceId = chatSourceId(source);
                    const selected = selectedSourceIds.includes(sourceId);
                    const label = chatSourceLabel(source, t, sourceKindRows);
                    const detail = chatSourceDetail(source, label);
                    const title = detail ? `${label} · ${detail}` : label;
                    return (
                      <label
                        className={["ai-chat-source-option", selected ? "selected" : ""].filter(Boolean).join(" ")}
                        data-paradev-chat-source-selected={selected ? "true" : "false"}
                        key={sourceId}
                        title={title}
                      >
                        <input
                          aria-label={t("chat.source.toggle", { label: detail ? `${label} (${detail})` : label })}
                          checked={selected}
                          data-paradev-chat-source="true"
                          data-paradev-chat-source-kind={source.kind}
                          onChange={() => {
                            setSelectedSourceIds((current) =>
                              current.includes(sourceId) ? current.filter((id) => id !== sourceId) : [...current, sourceId]
                            );
                          }}
                          type="checkbox"
                        />
                        <span className="ai-chat-source-text">
                          <span className="ai-chat-source-label">{label}</span>
                          {detail ? <small className="ai-chat-source-detail">{detail}</small> : null}
                        </span>
                      </label>
                    );
                  })}
                </div>
                <small
                  className={["ai-chat-context-summary", selectedSources.length === 0 ? "empty" : ""].filter(Boolean).join(" ")}
                  data-paradev-chat-context-summary="true"
                >
                  {selectedContextSummary}
                </small>
              </div>
            </div>
          ) : null}
          <div aria-live="polite" className="ai-chat-transcript">
            {messages.length === 0 ? (
              <p className="ai-chat-empty">{t("chat.empty")}</p>
            ) : (
              messages.map((message) => (
                <article className={`ai-chat-message ${message.role}`} key={message.id}>
                  <span className="ai-chat-message-role">
                    {message.role === "user" ? <User aria-hidden="true" size={13} /> : <Bot aria-hidden="true" size={13} />}
                    {message.role === "user" ? t("chat.you") : t("chat.ai")}
                  </span>
                  <p>{message.text}</p>
                  {message.role === "assistant" && message.proposal ? (
                    <div
                      className="ai-chat-proposal"
                      data-paradev-chat-proposal={
                        message.proposal.proposal.operationId
                      }
                    >
                      <small>
                        {aiChatProposalDetail(message.proposal.proposal, t)}
                      </small>
                      <button
                        aria-label={aiChatProposalReviewAria(
                          message.proposal.proposal,
                          t
                        )}
                        className="ai-chat-proposal-review"
                        data-paradev-chat-proposal-action="review"
                        disabled={
                          !onProposalReview ||
                          reviewingProposalId !== null
                        }
                        onClick={() => {
                          if (message.proposal) {
                            void handleProposalReview(message.id, message.proposal);
                          }
                        }}
                        type="button"
                      >
                        {aiChatProposalReviewLabel(
                          message.proposal.proposal,
                          t
                        )}
                        <ArrowRight aria-hidden="true" size={12} />
                      </button>
                    </div>
                  ) : null}
                </article>
              ))
            )}
            {error ? <p className="ai-chat-error">{t("chat.error", { message: error })}</p> : null}
          </div>
          <form className="ai-chat-composer" onSubmit={handleSubmit}>
            <textarea
              aria-label={t("chat.input.aria")}
              className="ai-chat-input"
              data-paradev-chat-input="true"
              onChange={(event) => setDraft(event.currentTarget.value)}
              onKeyDown={(event) => {
                if (shouldSubmitAiChatComposerKey(event)) {
                  event.preventDefault();
                  event.currentTarget.form?.requestSubmit();
                }
              }}
              placeholder={t("chat.input.placeholder")}
              rows={3}
              value={draft}
            />
            <button
              aria-label={sending ? t("chat.sending") : t("chat.send")}
              className="ai-chat-send"
              data-paradev-chat-send="true"
              disabled={!trimmedDraft || sending}
              title={sending ? t("chat.sending") : t("chat.send")}
              type="submit"
            >
              <Send aria-hidden="true" size={15} />
            </button>
          </form>
        </section>
      ) : (
        <button
          aria-expanded="false"
          aria-label={t("chat.open")}
          className="ai-chat-launcher"
          data-paradev-chat-launcher="true"
          onClick={() => setOpen(true)}
          title={t("chat.open")}
          type="button"
        >
          <MessageCircle aria-hidden="true" size={20} />
        </button>
      )}
    </aside>
  );
}

function aiChatOperationOpenLabel(operationId: string, t: Translator): string {
  if (operationId === "module.create_batch") {
    return t("chat.operation.open.moduleCreateBatch");
  }
  if (operationId === "module.draft") {
    return t("chat.operation.open.moduleDraft");
  }
  if (operationId === "collection.scaffold") {
    return t("chat.operation.open.collectionScaffold");
  }
  if (operationId === "build.plan") {
    return t("chat.operation.open.buildPlan");
  }
  if (operationId === "build.start") {
    return t("chat.operation.open.buildStart");
  }
  return t("chat.operation.open.default");
}

function aiChatOperationSafetyLabel(operationId: string, t: Translator): string {
  if (operationId === "module.create_batch") {
    return t("chat.operation.safety.moduleCreateBatch");
  }
  if (operationId === "module.draft") {
    return t("chat.operation.safety.moduleDraft");
  }
  if (operationId === "collection.scaffold") {
    return t("chat.operation.safety.collectionScaffold");
  }
  if (operationId === "build.start") {
    return t("chat.operation.safety.buildStart");
  }
  if (operationId === "build.plan") {
    return t("chat.operation.safety.buildPlan");
  }
  return t("chat.operation.safety.default");
}

function aiChatProposalDetail(
  proposal: ParaDevAiChatProposal,
  t: Translator
): string {
  if (proposal.operationId === "module.create_batch") {
    return t("chat.proposal.moduleBatch.detail", {
      count: String(proposal.requests.length)
    });
  }
  if (proposal.operationId === "module.source_form_update_batch") {
    return t("chat.proposal.sourceUpdate.detail", {
      changed: String(proposal.plan.counts.changed),
      requested: String(proposal.plan.counts.requested)
    });
  }
  return t("chat.proposal.collection.detail", {
    id: proposal.request.collection_id
  });
}

function aiChatProposalReviewAria(
  proposal: ParaDevAiChatProposal,
  t: Translator
): string {
  if (proposal.operationId === "module.create_batch") {
    return t("chat.proposal.moduleBatch.reviewAria", {
      count: String(proposal.requests.length)
    });
  }
  if (proposal.operationId === "module.source_form_update_batch") {
    return t("chat.proposal.sourceUpdate.reviewAria", {
      count: String(proposal.plan.counts.changed)
    });
  }
  return t("chat.proposal.collection.reviewAria", {
    id: proposal.request.collection_id
  });
}

function aiChatProposalReviewLabel(
  proposal: ParaDevAiChatProposal,
  t: Translator
): string {
  if (proposal.operationId === "module.create_batch") {
    return t("chat.proposal.moduleBatch.review", {
      count: String(proposal.requests.length)
    });
  }
  if (proposal.operationId === "module.source_form_update_batch") {
    return t("chat.proposal.sourceUpdate.review", {
      count: String(proposal.plan.counts.changed)
    });
  }
  return t("chat.proposal.collection.review", {
    id: proposal.request.collection_id
  });
}

function chatSourceLabel(source: ParaDevAiChatSource, t: Translator, sourceKindRows: readonly AiChatSourceKindRowLike[] = []): string {
  return aiChatContextSourceLabel(source, t, sourceKindRows);
}

function chatSourceDetail(source: ParaDevAiChatSource, label: string): string {
  const detail = (source.detail || source.relativePath || source.path || "").trim();
  return detail && detail !== label ? detail : "";
}

export function aiChatSelectedContextSummary(
  selectedSources: ParaDevAiChatSource[],
  t: Translator,
  sourceKindRows: readonly AiChatSourceKindRowLike[] = []
): string {
  if (selectedSources.length === 0) {
    return t("chat.context.summary.empty");
  }
  const labels = uniqueChatContextSummaryLabels(
    selectedSources.map((source) => (source.kind === "source" ? t("chat.context.summary.selectedFile") : chatSourceLabel(source, t, sourceKindRows)))
  );
  return t("chat.context.summary.attached", { sources: labels.join(", ") });
}

function normalizedContextSources(sources: ParaDevAiChatSource[]): ParaDevAiChatSource[] {
  return sources
    .filter((source) => source && typeof source.kind === "string" && source.kind.trim())
    .map((source, index) => ({
      ...source,
      id: source.id || source.relativePath || source.path || `${source.kind}:${index}`,
      kind: source.kind.trim()
    }));
}

export function nextSelectedSourceIdsForContextChange(
  currentSelectedIds: string[],
  previousSources: ParaDevAiChatSource[],
  nextSources: ParaDevAiChatSource[],
  profile?: ParaDevAiChatProfile,
  sourceKindRows: readonly AiChatSourceKindRowLike[] = []
): string[] {
  const selectedIds = new Set(currentSelectedIds);
  const previousKindCounts = sourceKindCounts(previousSources);
  const nextKindCounts = sourceKindCounts(nextSources);
  const selectedKinds = new Set(previousSources.filter((source) => selectedIds.has(chatSourceId(source))).map((source) => source.kind));
  const profileDefaultKinds = new Set((profile?.sourceKinds ?? []).flatMap((kind) => frontendAiChatContextKindsForProfileKind(kind, sourceKindRows)));

  return nextSources
    .filter((source) => {
      const sourceId = chatSourceId(source);
      if (selectedIds.has(sourceId)) {
        return true;
      }
      if ((previousKindCounts.get(source.kind) ?? 0) > 0) {
        return selectedKinds.has(source.kind) && previousKindCounts.get(source.kind) === 1 && nextKindCounts.get(source.kind) === 1;
      }
      return profileDefaultKinds.has(source.kind);
    })
    .map(chatSourceId);
}

function initialSelectedRole(profiles: ParaDevAiChatProfile[], defaultRole: string): string {
  return profiles.some((profile) => profile.id === defaultRole) ? defaultRole : profiles[0]?.id ?? (defaultRole || "chat");
}

function defaultSelectedSourceIds(
  sources: ParaDevAiChatSource[],
  profile?: ParaDevAiChatProfile,
  sourceKindRows: readonly AiChatSourceKindRowLike[] = []
): string[] {
  if (!profile) {
    return sources.map(chatSourceId);
  }
  const allowedKinds = new Set(profile.sourceKinds.flatMap((kind) => frontendAiChatContextKindsForProfileKind(kind, sourceKindRows)));
  return sources.filter((source) => allowedKinds.has(source.kind)).map(chatSourceId);
}

function chatSourceId(source: ParaDevAiChatSource): string {
  return source.id || source.relativePath || source.path || source.kind;
}

function sourceKindCounts(sources: ParaDevAiChatSource[]): Map<string, number> {
  const counts = new Map<string, number>();
  for (const source of sources) {
    counts.set(source.kind, (counts.get(source.kind) ?? 0) + 1);
  }
  return counts;
}

function uniqueChatContextSummaryLabels(labels: string[]): string[] {
  const seen = new Set<string>();
  const uniqueLabels: string[] = [];
  for (const label of labels) {
    const trimmed = label.trim();
    if (trimmed && !seen.has(trimmed)) {
      seen.add(trimmed);
      uniqueLabels.push(trimmed);
    }
  }
  return uniqueLabels;
}
