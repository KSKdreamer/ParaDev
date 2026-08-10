import {
  useEffect,
  useMemo,
  useRef,
  useState,
  type KeyboardEvent as ReactKeyboardEvent,
} from "react";
import { AlertTriangle, CheckCircle2, RefreshCw, X } from "lucide-react";
import { SelectField } from "../components/ui/SelectField";
import { localizedParaDevServiceError } from "../desktopBridgeErrors";
import type { Translator } from "../i18n";
import {
  editModuleDiagram,
  type ModuleDiagramEditPayload,
} from "../services/paradev";
import type {
  ProjectDiagramNodeAuthoring,
  ProjectDiagramNodeField,
} from "../types";

type DiagramNodeCreateDialogProps = {
  authoring: ProjectDiagramNodeAuthoring;
  contextValues: Readonly<Record<string, unknown>>;
  family: string;
  onApplied: (payload: ModuleDiagramEditPayload) => void | Promise<void>;
  onBusyStart?: () => () => void;
  onClose: () => void;
  profile?: string;
  projectRoot: string;
  t: Translator;
};

type FieldIssue = "number" | "required";

export function DiagramNodeCreateDialog({
  authoring,
  contextValues,
  family,
  onApplied,
  onBusyStart,
  onClose,
  profile,
  projectRoot,
  t,
}: DiagramNodeCreateDialogProps) {
  const previouslyFocused = useRef<HTMLElement | null>(
    typeof document !== "undefined" &&
      document.activeElement instanceof HTMLElement
      ? document.activeElement
      : null,
  );
  const dialogRef = useRef<HTMLElement>(null);
  const [values, setValues] = useState<Record<string, string>>(() =>
    initialFieldValues(authoring.fields, contextValues),
  );
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [issues, setIssues] = useState<Record<string, FieldIssue>>({});
  const [busy, setBusy] = useState<"apply" | "plan" | "">("");
  const [error, setError] = useState("");
  const [result, setResult] = useState<ModuleDiagramEditPayload | null>(null);
  const [plannedIntent, setPlannedIntent] = useState<Record<
    string,
    unknown
  > | null>(null);
  const primaryFields = useMemo(
    () => authoring.fields.filter((field) => !field.advanced),
    [authoring.fields],
  );
  const advancedFields = useMemo(
    () => authoring.fields.filter((field) => field.advanced),
    [authoring.fields],
  );
  const applied = result?.applied === true;
  const readyToApply = Boolean(result && !result.blocked && plannedIntent);

  useEffect(() => {
    const dialog = dialogRef.current;
    if (dialog && !dialog.contains(document.activeElement)) {
      dialogFocusableElements(dialog)[0]?.focus();
    }
    return () => {
      if (previouslyFocused.current?.isConnected) {
        previouslyFocused.current.focus();
      }
    };
  }, []);

  const invalidatePlan = () => {
    setResult(null);
    setPlannedIntent(null);
    setIssues({});
    setError("");
  };

  const updateValue = (name: string, value: string) => {
    if (busy || applied) {
      return;
    }
    invalidatePlan();
    setValues((current) => ({ ...current, [name]: value }));
  };

  const handlePlan = async () => {
    if (busy || applied) {
      return;
    }
    const checked = nodeIntent(authoring.fields, values, contextValues);
    setIssues(checked.issues);
    if (!checked.intent) {
      if (
        advancedFields.some((field) => checked.issues[field.name] !== undefined)
      ) {
        setShowAdvanced(true);
      }
      setError(t("workspace.module.editor.single.validation.fix"));
      return;
    }
    const snapshot = { ...checked.intent };
    const finishBusy = onBusyStart?.() ?? (() => undefined);
    setBusy("plan");
    setError("");
    try {
      const payload = await editModuleDiagram({
        projectRoot,
        family,
        profile,
        nodeIntents: [snapshot],
        write: false,
      });
      setResult(payload);
      setPlannedIntent(payload.blocked ? null : snapshot);
    } catch (cause: unknown) {
      setResult(null);
      setPlannedIntent(null);
      setError(localizedParaDevServiceError(t, cause));
    } finally {
      finishBusy();
      setBusy("");
    }
  };

  const handleApply = async () => {
    if (busy || !result || result.blocked || !plannedIntent || applied) {
      return;
    }
    const finishBusy = onBusyStart?.() ?? (() => undefined);
    setBusy("apply");
    setError("");
    try {
      const payload = await editModuleDiagram({
        projectRoot,
        family,
        profile,
        nodeIntents: [{ ...plannedIntent }],
        write: true,
        planHash: result.plan_hash,
      });
      setResult(payload);
      setPlannedIntent(null);
      if (payload.applied) {
        await onApplied(payload);
      }
    } catch (cause: unknown) {
      setPlannedIntent(null);
      setError(localizedParaDevServiceError(t, cause));
    } finally {
      finishBusy();
      setBusy("");
    }
  };

  const handleKeyDown = (event: ReactKeyboardEvent<HTMLElement>) => {
    if (event.key === "Escape") {
      if (!busy) {
        event.preventDefault();
        onClose();
      }
      return;
    }
    if (event.key !== "Tab") {
      return;
    }
    const focusable = dialogFocusableElements(dialogRef.current);
    if (focusable.length === 0) {
      event.preventDefault();
      return;
    }
    const active = focusable.indexOf(document.activeElement as HTMLElement);
    if (event.shiftKey && active <= 0) {
      event.preventDefault();
      focusable.at(-1)?.focus();
    } else if (
      !event.shiftKey &&
      (active < 0 || active === focusable.length - 1)
    ) {
      event.preventDefault();
      focusable[0]?.focus();
    }
  };

  return (
    <div className="module-batch-backdrop" role="presentation">
      <section
        aria-labelledby="diagram-node-create-title"
        aria-modal="true"
        className="module-batch-dialog single"
        onKeyDown={handleKeyDown}
        ref={dialogRef}
        role="dialog"
      >
        <header className="module-batch-heading">
          <span>
            <small>{t("workspace.diagram.nodeCreate.eyebrow")}</small>
            <h3 id="diagram-node-create-title">{authoring.title}</h3>
            <p>{authoring.description}</p>
          </span>
          <button
            aria-label={t("workspace.module.editor.cancel")}
            className="toolbar-button icon-only"
            disabled={Boolean(busy)}
            onClick={onClose}
            title={t("workspace.module.editor.cancel")}
            type="button"
          >
            <X aria-hidden="true" size={14} />
          </button>
        </header>

        <div className="module-batch-toolbar">
          <p className="module-batch-guidance">
            {t("workspace.diagram.nodeCreate.guidance")}
          </p>
          {advancedFields.length > 0 ? (
            <button
              aria-expanded={showAdvanced}
              className="toolbar-button subtle"
              disabled={applied || Boolean(busy)}
              onClick={() => setShowAdvanced((current) => !current)}
              type="button"
            >
              {t(
                showAdvanced
                  ? "workspace.module.editor.batch.hideAdvanced"
                  : "workspace.module.editor.batch.showAdvanced",
              )}
            </button>
          ) : null}
        </div>

        <div className="module-batch-body">
          {!applied ? (
            <div className="module-batch-row">
              <div className="module-create-fields">
                {primaryFields.map((field, index) => (
                  <NodeField
                    autoFocus={index === 0}
                    busy={Boolean(busy)}
                    field={field}
                    issue={issues[field.name]}
                    key={field.name}
                    onChange={updateValue}
                    t={t}
                    value={values[field.name] ?? ""}
                  />
                ))}
                {showAdvanced
                  ? advancedFields.map((field) => (
                      <NodeField
                        busy={Boolean(busy)}
                        field={field}
                        issue={issues[field.name]}
                        key={field.name}
                        onChange={updateValue}
                        t={t}
                        value={values[field.name] ?? ""}
                      />
                    ))
                  : null}
              </div>
            </div>
          ) : null}

          {result ? (
            <>
              <div
                className={`module-batch-result ${
                  result.blocked ? "blocked" : "ready"
                }`}
                role="status"
              >
                <strong>{result.status}</strong>
                <span>
                  {result.drafts.length} source file
                  {result.drafts.length === 1 ? "" : "s"}
                </span>
              </div>
              <div className="module-batch-plan-hash">
                <small>{t("workspace.module.editor.batch.planHash")}</small>
                <code title={result.plan_hash}>{result.plan_hash}</code>
              </div>
              {result.source_replacements.length > 0 ? (
                <section className="diagram-node-create-review">
                  <strong>
                    {t("workspace.diagram.nodeCreate.reviewTitle")}
                  </strong>
                  <ul>
                    {result.source_replacements.map((replacement, index) => {
                      const path = recordText(replacement, "path") || "?";
                      const start = recordNumber(replacement, "start");
                      const end = recordNumber(replacement, "end");
                      const text = recordText(replacement, "replacement");
                      return (
                        <li key={`${path}:${start}:${end}:${index}`}>
                          <details>
                            <summary>
                              {t("workspace.diagram.nodeCreate.replacement", {
                                path,
                                start: String(start),
                                end: String(end),
                              })}
                            </summary>
                            <pre>{text}</pre>
                          </details>
                        </li>
                      );
                    })}
                  </ul>
                </section>
              ) : null}
            </>
          ) : null}
          {result?.diagnostics.length ? (
            <ul className="module-batch-diagnostics">
              {result.diagnostics.map((diagnostic, index) => (
                <li key={`${String(diagnostic.code)}:${index}`}>
                  <AlertTriangle aria-hidden="true" size={14} />
                  <span>
                    <strong>
                      {String(diagnostic.code ?? "module_diagram.node_create")}
                    </strong>
                    <small>{String(diagnostic.message ?? "")}</small>
                  </span>
                </li>
              ))}
            </ul>
          ) : null}
          {error ? (
            <p className="module-batch-error" role="alert">
              <AlertTriangle aria-hidden="true" size={14} />
              {error}
            </p>
          ) : null}
        </div>

        <footer className="module-batch-footer">
          <button
            className="toolbar-button subtle"
            disabled={Boolean(busy)}
            onClick={onClose}
            type="button"
          >
            {t("workspace.module.editor.cancel")}
          </button>
          {applied ? (
            <button
              className="toolbar-button primary"
              onClick={onClose}
              type="button"
            >
              <CheckCircle2 aria-hidden="true" size={14} />
              {t("workspace.module.editor.batch.done")}
            </button>
          ) : readyToApply ? (
            <button
              className="toolbar-button primary"
              disabled={Boolean(busy)}
              onClick={() => void handleApply()}
              type="button"
            >
              {busy === "apply" ? (
                <RefreshCw
                  aria-hidden="true"
                  className="module-batch-spinner"
                  size={14}
                />
              ) : (
                <CheckCircle2 aria-hidden="true" size={14} />
              )}
              {t(
                busy === "apply"
                  ? "workspace.diagram.nodeCreate.applying"
                  : "workspace.diagram.nodeCreate.apply",
              )}
            </button>
          ) : (
            <button
              className="toolbar-button primary"
              disabled={Boolean(busy)}
              onClick={() => void handlePlan()}
              type="button"
            >
              {busy === "plan" ? (
                <RefreshCw
                  aria-hidden="true"
                  className="module-batch-spinner"
                  size={14}
                />
              ) : null}
              {t(
                busy === "plan"
                  ? "workspace.diagram.nodeCreate.previewing"
                  : result
                    ? "workspace.diagram.nodeCreate.previewAgain"
                    : "workspace.diagram.nodeCreate.preview",
              )}
            </button>
          )}
        </footer>
      </section>
    </div>
  );
}

function NodeField({
  autoFocus = false,
  busy,
  field,
  issue,
  onChange,
  t,
  value,
}: {
  autoFocus?: boolean;
  busy: boolean;
  field: ProjectDiagramNodeField;
  issue?: FieldIssue;
  onChange: (name: string, value: string) => void;
  t: Translator;
  value: string;
}) {
  const error = issue
    ? t(
        issue === "number"
          ? "workspace.module.editor.create.validation.number"
          : "workspace.module.editor.create.validation.required",
        { field: field.label },
      )
    : "";
  return (
    <label className="module-create-field">
      <small>{field.label}</small>
      {field.kind === "boolean" ? (
        <SelectField
          disabled={busy}
          label={field.label}
          onChange={(event) => onChange(field.name, event.target.value)}
          options={[
            { label: "True", value: "true" },
            { label: "False", value: "false" },
          ]}
          value={value}
          variant="compact"
        />
      ) : field.kind === "textarea" ? (
        <textarea
          aria-invalid={Boolean(issue) || undefined}
          autoFocus={autoFocus}
          disabled={busy}
          onChange={(event) => onChange(field.name, event.target.value)}
          value={value}
        />
      ) : (
        <input
          aria-invalid={Boolean(issue) || undefined}
          autoFocus={autoFocus}
          disabled={busy}
          onChange={(event) => onChange(field.name, event.target.value)}
          type={field.kind === "number" ? "number" : "text"}
          value={value}
        />
      )}
      {field.description ? (
        <span className="module-create-field-help">{field.description}</span>
      ) : null}
      {error ? (
        <span className="module-create-field-error" role="alert">
          {error}
        </span>
      ) : null}
    </label>
  );
}

function initialFieldValues(
  fields: readonly ProjectDiagramNodeField[],
  contextValues: Readonly<Record<string, unknown>>,
): Record<string, string> {
  return Object.fromEntries(
    fields.map((field) => {
      const inherited = contextValues[field.name];
      const value = inherited !== undefined ? inherited : field.default;
      return [field.name, value === undefined ? "" : String(value)];
    }),
  );
}

function nodeIntent(
  fields: readonly ProjectDiagramNodeField[],
  values: Readonly<Record<string, string>>,
  contextValues: Readonly<Record<string, unknown>>,
): {
  intent: Record<string, unknown> | null;
  issues: Record<string, FieldIssue>;
} {
  const intent: Record<string, unknown> = {
    ...contextValues,
  };
  const issues: Record<string, FieldIssue> = {};
  for (const field of fields) {
    const raw = values[field.name]?.trim() ?? "";
    if (!raw) {
      if (field.required) {
        issues[field.name] = "required";
      }
      continue;
    }
    if (field.kind === "number") {
      const value = Number(raw);
      if (!Number.isFinite(value)) {
        issues[field.name] = "number";
      } else {
        intent[field.name] = value;
      }
    } else if (field.kind === "boolean") {
      intent[field.name] = raw === "true";
    } else {
      intent[field.name] = raw;
    }
  }
  return {
    intent: Object.keys(issues).length ? null : intent,
    issues,
  };
}

function dialogFocusableElements(dialog: HTMLElement | null): HTMLElement[] {
  if (!dialog) {
    return [];
  }
  return Array.from(
    dialog.querySelectorAll<HTMLElement>(
      "button:not([disabled]), input:not([disabled]), select:not([disabled]), textarea:not([disabled])",
    ),
  );
}

function recordText(value: Record<string, unknown>, field: string): string {
  const item = value[field];
  return typeof item === "string" ? item : "";
}

function recordNumber(value: Record<string, unknown>, field: string): number {
  const item = value[field];
  return typeof item === "number" && Number.isFinite(item) ? item : 0;
}
