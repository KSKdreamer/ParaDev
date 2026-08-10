import { RefreshCw, X } from "lucide-react";
import { useState } from "react";
import type { Locale, Translator } from "../i18n";
import {
  applyProjectDraft,
  type ParaDevAiChatSourceFormUpdateRequest
} from "../services/paradev";
import type {
  DraftApplyPayload,
  SourceFormScalar,
  SourceFormUpdatePlan
} from "../types";
import { localizedParaDevServiceError } from "../desktopBridgeErrors";
import type { ModuleEditorSourceUpdateState } from "./editorSessionStore";
import { localizedSourceFormText } from "./sourceFormText";

type SourceUpdateReviewDialogProps = {
  initialState: ModuleEditorSourceUpdateState;
  locale: Locale;
  onApplied: (payload: DraftApplyPayload) => Promise<void> | void;
  onBusyStart: () => () => void;
  onClose: () => void;
  projectRoot: string;
  t: Translator;
};

/** Review and atomically apply one exact Registry-owned AI Guided plan. */
export function SourceUpdateReviewDialog({
  initialState,
  locale,
  onApplied,
  onBusyStart,
  onClose,
  projectRoot,
  t
}: SourceUpdateReviewDialogProps) {
  const [busy, setBusy] = useState(false);
  const [confirmed, setConfirmed] = useState(false);
  const [error, setError] = useState("");
  const { plan, requests } = initialState;

  const handleApply = async () => {
    if (busy || !confirmed || !plan.changed || plan.sourceEdits.length === 0) {
      return;
    }
    const finishBusy = onBusyStart();
    setBusy(true);
    setError("");
    try {
      const payload = await applyProjectDraft({
        projectId: plan.projectId,
        projectRoot,
        sourceEdits: plan.sourceEdits
      });
      await onApplied(payload);
    } catch (cause: unknown) {
      setError(localizedParaDevServiceError(t, cause));
    } finally {
      finishBusy();
      setBusy(false);
    }
  };

  return (
    <div className="module-batch-backdrop" role="presentation">
      <section
        aria-labelledby="source-update-review-title"
        aria-modal="true"
        className="module-batch-dialog source-update-review-dialog"
        data-paradev-source-update-review="true"
        role="dialog"
      >
        <header className="module-batch-heading">
          <div>
            <span>{t("workspace.module.editor.sourceUpdate.eyebrow")}</span>
            <h3 id="source-update-review-title">
              {t("workspace.module.editor.sourceUpdate.title")}
            </h3>
            <p>
              {t("workspace.module.editor.sourceUpdate.detail", {
                changed: String(plan.counts.changed),
                requested: String(plan.counts.requested)
              })}
            </p>
          </div>
          <button
            aria-label={t("workspace.module.editor.sourceUpdate.close")}
            className="icon-button"
            disabled={busy}
            onClick={onClose}
            title={t("workspace.module.editor.sourceUpdate.close")}
            type="button"
          >
            <X aria-hidden="true" size={16} />
          </button>
        </header>

        <div className="module-batch-body source-update-review-body">
          <div className="source-update-review-list">
            {plan.updates.map((update, index) => (
              <SourceUpdateReviewRow
                key={update.path}
                locale={locale}
                request={requests[index]}
                t={t}
                update={update}
              />
            ))}
          </div>
          {error ? (
            <p className="module-batch-error" role="alert">
              {error}
            </p>
          ) : null}
        </div>

        <footer className="module-dialog-actions module-batch-actions">
          {plan.changed ? (
            <label className="module-batch-review-confirmation">
              <input
                checked={confirmed}
                disabled={busy}
                onChange={(event) => setConfirmed(event.currentTarget.checked)}
                type="checkbox"
              />
              <span>
                {t("workspace.module.editor.sourceUpdate.confirm", {
                  count: String(plan.counts.changed)
                })}
              </span>
            </label>
          ) : (
            <p>{t("workspace.module.editor.sourceUpdate.unchanged")}</p>
          )}
          <button
            className="toolbar-button subtle"
            disabled={busy}
            onClick={onClose}
            type="button"
          >
            {t("workspace.module.editor.sourceUpdate.cancel")}
          </button>
          <button
            className="toolbar-button primary"
            data-paradev-source-update-apply="true"
            disabled={busy || !confirmed || !plan.changed}
            onClick={() => void handleApply()}
            type="button"
          >
            {busy ? (
              <RefreshCw
                aria-hidden="true"
                className="module-batch-spinner"
                size={14}
              />
            ) : null}
            {t(
              busy
                ? "workspace.module.editor.sourceUpdate.applying"
                : "workspace.module.editor.sourceUpdate.apply"
            )}
          </button>
        </footer>
      </section>
    </div>
  );
}

function SourceUpdateReviewRow({
  locale,
  request,
  t,
  update
}: {
  locale: Locale;
  request: ParaDevAiChatSourceFormUpdateRequest | undefined;
  t: Translator;
  update: SourceFormUpdatePlan;
}) {
  return (
    <article
      className="source-update-review-row"
      data-paradev-source-update-path={update.relativePath}
    >
      <header>
        <strong>{request?.module_id ?? update.moduleId}</strong>
        <code>{update.relativePath}</code>
      </header>
      {update.changes.length > 0 ? (
        <dl>
          {update.changes.map((change) => (
            <div key={change.controlId}>
              <dt>
                {request?.control_labels[change.controlId]
                  ? localizedSourceFormText(
                      request.control_labels[change.controlId],
                      locale
                    )
                  : change.controlId}
              </dt>
              <dd>
                <span>{sourceUpdateValue(change.previous, t)}</span>
                <span aria-hidden="true">→</span>
                <strong>{sourceUpdateValue(change.value, t)}</strong>
              </dd>
            </div>
          ))}
        </dl>
      ) : (
        <p>{t("workspace.module.editor.sourceUpdate.fileUnchanged")}</p>
      )}
    </article>
  );
}

function sourceUpdateValue(value: SourceFormScalar, t: Translator): string {
  if (value === true) {
    return t("workspace.module.editor.sourceUpdate.boolean.true");
  }
  if (value === false) {
    return t("workspace.module.editor.sourceUpdate.boolean.false");
  }
  return String(value);
}
