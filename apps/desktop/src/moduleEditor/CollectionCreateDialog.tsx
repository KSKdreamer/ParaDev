import {
  useEffect,
  useMemo,
  useRef,
  useState,
  type KeyboardEvent as ReactKeyboardEvent
} from "react";
import {
  AlertTriangle,
  CheckCircle2,
  Plus,
  RefreshCw,
  X
} from "lucide-react";
import { SelectField } from "../components/ui/SelectField";
import { localizedParaDevServiceError } from "../desktopBridgeErrors";
import type { Translator } from "../i18n";
import {
  scaffoldCollection,
  type CollectionScaffoldPayload,
  type ScaffoldCollectionRequest
} from "../services/paradev";
import type {
  ProjectTemplate,
  ProjectTemplateSourceRoot
} from "../types";
import {
  buildTemplateCreateFields,
  type TemplateCreateField
} from "./model";
import type { ModuleEditorCollectionCreateState } from "./editorSessionStore";

type CollectionCreateDialogProps = {
  initialState?: ModuleEditorCollectionCreateState | null;
  onApplied: (
    payload: CollectionScaffoldPayload
  ) => void | Promise<void>;
  onBusyStart?: () => () => void;
  onClose: () => void;
  onDraftChange?: (
    state: ModuleEditorCollectionCreateState | null
  ) => void;
  onPostWriteError?: (cause: unknown) => void;
  projectRoot: string;
  sourceRoots: ProjectTemplateSourceRoot[];
  t: Translator;
  templates: ProjectTemplate[];
};

type FrozenCollectionRequest = Omit<
  ScaffoldCollectionRequest,
  "planHash" | "write"
>;

const COLLECTION_IDENTIFIER = /^[A-Za-z_][A-Za-z0-9_.-]*$/;

export function CollectionCreateDialog({
  initialState = null,
  onApplied,
  onBusyStart,
  onClose,
  onDraftChange,
  onPostWriteError,
  projectRoot,
  sourceRoots,
  t,
  templates
}: CollectionCreateDialogProps) {
  const previouslyFocused = useRef<HTMLElement | null>(
    typeof document !== "undefined" &&
      document.activeElement instanceof HTMLElement
      ? document.activeElement
      : null
  );
  const dialogRef = useRef<HTMLElement>(null);
  const collectionIdRef = useRef<HTMLInputElement>(null);
  const pristineSourceRoot =
    sourceRoots.find((row) => row.default)?.path ??
    sourceRoots[0]?.path ??
    "";
  const pristineTemplateId = templates[0]?.id ?? "";
  const initialPreview = validInitialCollectionPreview(
    initialState,
    projectRoot
  );
  const [templateId, setTemplateId] = useState(
    initialState?.templateId.trim() || pristineTemplateId
  );
  const template =
    templates.find((row) => row.id === templateId) ??
    templates[0] ??
    null;
  const collectionTitle =
    template?.title ?? t("workspace.module.editor.collection");
  const fields = useMemo(
    () => buildTemplateCreateFields(template),
    [template]
  );
  const allFields = [...fields.primary, ...fields.advanced];
  const [collectionId, setCollectionId] = useState(
    initialState?.collectionId ?? ""
  );
  const [values, setValues] = useState<Record<string, string>>(
    initialState ? { ...initialState.values } : {}
  );
  const [sourceRoot, setSourceRoot] = useState(
    initialState?.sourceRoot.trim() || pristineSourceRoot
  );
  const [showAdvanced, setShowAdvanced] = useState(
    initialState?.showAdvanced ?? false
  );
  const [busy, setBusy] = useState<"apply" | "plan" | "">("");
  const [error, setError] = useState("");
  const [plan, setPlan] =
    useState<CollectionScaffoldPayload | null>(
      initialPreview?.plan ?? null
    );
  const [frozenRequest, setFrozenRequest] =
    useState<FrozenCollectionRequest | null>(
      initialPreview?.request ?? null
    );
  const [reviewed, setReviewed] = useState(false);

  useEffect(() => {
    collectionIdRef.current?.focus();
    return () => {
      if (previouslyFocused.current?.isConnected) {
        previouslyFocused.current.focus();
      }
    };
  }, []);

  useEffect(() => {
    if (!onDraftChange) {
      return;
    }
    onDraftChange({
      open: true,
      ...(plan && frozenRequest && !plan.written
        ? {
            preview: {
              plan,
              request: frozenRequest
            }
          }
        : {}),
      pristineSourceRoot,
      pristineTemplateId,
      templateId,
      collectionId,
      values,
      showAdvanced,
      sourceRoot
    });
  }, [
    collectionId,
    frozenRequest,
    onDraftChange,
    plan,
    pristineSourceRoot,
    pristineTemplateId,
    showAdvanced,
    sourceRoot,
    templateId,
    values
  ]);

  const invalidatePlan = () => {
    if (busy) {
      return;
    }
    setPlan(null);
    setFrozenRequest(null);
    setReviewed(false);
    setError("");
  };

  const requestFromDraft = (): FrozenCollectionRequest | null => {
    const cleanId = collectionId.trim();
    if (!COLLECTION_IDENTIFIER.test(cleanId)) {
      setError(
        t("workspace.diagram.collectionCreate.invalidId", {
          title: collectionTitle
        })
      );
      return null;
    }
    if (!template) {
      setError(
        t("workspace.diagram.collectionCreate.noTemplate", {
          title: collectionTitle
        })
      );
      return null;
    }
    const normalizedValues: Record<string, string> = {};
    for (const field of allFields) {
      const value = values[field.name]?.trim() ?? "";
      if (field.required && !value && !field.defaultValue) {
        setError(
          t("workspace.module.editor.create.validation.required", {
            field: field.label
          })
        );
        return null;
      }
      if (value) {
        normalizedValues[field.name] = value;
      }
    }
    return {
      projectRoot,
      templateId: template.id,
      collectionId: cleanId,
      values: normalizedValues,
      sourceRoot: sourceRoot || null,
      force: false
    };
  };

  const handlePlan = async () => {
    if (busy) {
      return;
    }
    const request = requestFromDraft();
    if (!request) {
      return;
    }
    const finishBusy = onBusyStart?.() ?? (() => undefined);
    setBusy("plan");
    setError("");
    setReviewed(false);
    try {
      const payload = await scaffoldCollection(request);
      setPlan(payload);
      setFrozenRequest(request);
      if (payload.blocked) {
        setError(collectionDiagnostic(payload, t));
      }
    } catch (cause: unknown) {
      setPlan(null);
      setFrozenRequest(null);
      setError(localizedParaDevServiceError(t, cause));
    } finally {
      finishBusy();
      setBusy("");
    }
  };

  const handleApply = async () => {
    if (
      busy ||
      !reviewed ||
      !plan ||
      plan.blocked ||
      !frozenRequest
    ) {
      return;
    }
    const finishBusy = onBusyStart?.() ?? (() => undefined);
    setBusy("apply");
    setError("");
    let written = false;
    try {
      const payload = await scaffoldCollection({
        ...frozenRequest,
        write: true,
        planHash: plan.plan_hash
      });
      setPlan(payload);
      setReviewed(false);
      if (payload.blocked || !payload.written) {
        setFrozenRequest(null);
        setError(collectionDiagnostic(payload, t));
        return;
      }
      written = true;
      setFrozenRequest(null);
      onDraftChange?.(null);
      try {
        await onApplied(payload);
      } catch (cause: unknown) {
        onPostWriteError?.(cause);
      }
    } catch (cause: unknown) {
      setError(localizedParaDevServiceError(t, cause));
    } finally {
      finishBusy();
      setBusy("");
    }
    if (written) {
      onClose();
    }
  };

  const handleDialogKeyDown = (
    event: ReactKeyboardEvent<HTMLElement>
  ) => {
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
    const activeIndex = focusable.indexOf(
      document.activeElement as HTMLElement
    );
    if (event.shiftKey && activeIndex <= 0) {
      event.preventDefault();
      focusable.at(-1)?.focus();
    } else if (
      !event.shiftKey &&
      (activeIndex < 0 || activeIndex === focusable.length - 1)
    ) {
      event.preventDefault();
      focusable[0]?.focus();
    }
  };

  return (
    <div className="module-batch-backdrop" role="presentation">
      <section
        aria-labelledby="collection-create-title"
        aria-modal="true"
        className="module-batch-dialog single"
        onKeyDown={handleDialogKeyDown}
        ref={dialogRef}
        role="dialog"
      >
        <header className="module-batch-heading">
          <span>
            <small>
              {t("workspace.diagram.collectionCreate.eyebrow")}
            </small>
            <h3 id="collection-create-title">
              {t("workspace.diagram.collectionCreate.title", {
                title: collectionTitle
              })}
            </h3>
            <p>
              {t("workspace.diagram.collectionCreate.detail", {
                title: collectionTitle
              })}
            </p>
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
            {t("workspace.diagram.collectionCreate.guidance", {
              title: collectionTitle
            })}
          </p>
          <div>
            {sourceRoots.length > 1 ? (
              <SelectField
                disabled={Boolean(busy) || Boolean(plan)}
                label={t("workspace.module.editor.batch.sourceRoot")}
                onChange={(event) => {
                  invalidatePlan();
                  setSourceRoot(event.target.value);
                }}
                options={sourceRoots.map((row) => ({
                  label: row.relative_path || row.path,
                  value: row.path
                }))}
                value={sourceRoot}
                variant="compact"
              />
            ) : null}
            {fields.advanced.length > 0 && !plan ? (
              <button
                aria-expanded={showAdvanced}
                className="toolbar-button subtle"
                disabled={Boolean(busy)}
                onClick={() => setShowAdvanced((current) => !current)}
                type="button"
              >
                {t(
                  showAdvanced
                    ? "workspace.module.editor.batch.hideAdvanced"
                    : "workspace.module.editor.batch.showAdvanced"
                )}
              </button>
            ) : null}
          </div>
        </div>

        <div className="module-batch-body">
          {!plan ? (
            <div className="module-batch-rows">
              <div className="module-batch-row">
                <div className="module-batch-row-identity">
                  <label className="module-create-field">
                    <small>
                      {t("workspace.diagram.collectionCreate.collectionId", {
                        title: collectionTitle
                      })}
                    </small>
                    <input
                      aria-label={t(
                        "workspace.diagram.collectionCreate.collectionId",
                        { title: collectionTitle }
                      )}
                      disabled={Boolean(busy)}
                      onChange={(event) => {
                        invalidatePlan();
                        setCollectionId(event.target.value);
                      }}
                      ref={collectionIdRef}
                      value={collectionId}
                    />
                  </label>
                  {templates.length > 1 ? (
                    <SelectField
                      disabled={Boolean(busy)}
                      label={t("workspace.module.editor.create.template")}
                      onChange={(event) => {
                        invalidatePlan();
                        setTemplateId(event.target.value);
                        setValues({});
                      }}
                      options={templates.map((row) => ({
                        label: row.title,
                        value: row.id
                      }))}
                      value={template?.id ?? ""}
                      variant="compact"
                    />
                  ) : (
                    <span className="module-batch-template">
                      <small>
                        {t("workspace.module.editor.create.template")}
                      </small>
                      <strong>{template?.title ?? ""}</strong>
                    </span>
                  )}
                </div>
                <div className="module-batch-fields">
                  {fields.primary.map((field) => (
                    <CollectionTemplateField
                      disabled={Boolean(busy)}
                      field={field}
                      key={field.name}
                      onChange={(value) => {
                        invalidatePlan();
                        setValues((current) => ({
                          ...current,
                          [field.name]: value
                        }));
                      }}
                      t={t}
                      value={values[field.name] ?? ""}
                    />
                  ))}
                </div>
                {showAdvanced && fields.advanced.length > 0 ? (
                  <div className="module-batch-fields advanced">
                    {fields.advanced.map((field) => (
                      <CollectionTemplateField
                        disabled={Boolean(busy)}
                        field={field}
                        key={field.name}
                        onChange={(value) => {
                          invalidatePlan();
                          setValues((current) => ({
                            ...current,
                            [field.name]: value
                          }));
                        }}
                        t={t}
                        value={values[field.name] ?? ""}
                      />
                    ))}
                  </div>
                ) : null}
              </div>
            </div>
          ) : (
            <section
              className="module-batch-result"
              role={plan.blocked ? "alert" : "status"}
            >
              <div>
                {plan.blocked ? (
                  <AlertTriangle aria-hidden="true" size={18} />
                ) : (
                  <CheckCircle2 aria-hidden="true" size={18} />
                )}
                <span>
                  <strong>
                    {t(
                      plan.blocked
                        ? "workspace.diagram.collectionCreate.blocked"
                        : "workspace.diagram.collectionCreate.ready",
                      { title: collectionTitle }
                    )}
                  </strong>
                  <small>{plan.folder_name}</small>
                </span>
              </div>
              <ul>
                {plan.files.map((file, index) => (
                  <li key={`${String(file.relative_path)}:${index}`}>
                    <code>{String(file.relative_path ?? file.path ?? "")}</code>
                  </li>
                ))}
              </ul>
              {!plan.blocked ? (
                <label className="module-batch-review-confirmation">
                  <input
                    checked={reviewed}
                    disabled={Boolean(busy)}
                    onChange={(event) => setReviewed(event.target.checked)}
                    type="checkbox"
                  />
                  <span>
                    {t("workspace.diagram.collectionCreate.confirm", {
                      title: collectionTitle
                    })}
                  </span>
                </label>
              ) : null}
            </section>
          )}

          {error ? (
            <p className="module-batch-error" role="alert">
              {error}
            </p>
          ) : null}
        </div>

        <footer className="module-dialog-actions module-batch-actions">
          <button
            className="toolbar-button subtle"
            disabled={Boolean(busy)}
            onClick={plan ? invalidatePlan : onClose}
            type="button"
          >
            {plan
              ? t("workspace.diagram.collectionCreate.back")
              : t("workspace.module.editor.cancel")}
          </button>
          {plan && !plan.blocked ? (
            <button
              className="toolbar-button primary"
              disabled={Boolean(busy) || !reviewed}
              onClick={() => void handleApply()}
              type="button"
            >
              {busy === "apply" ? (
                <RefreshCw aria-hidden="true" className="spin" size={14} />
              ) : (
                <Plus aria-hidden="true" size={14} />
              )}
              {t(
                busy === "apply"
                  ? "workspace.diagram.collectionCreate.applying"
                  : "workspace.diagram.collectionCreate.apply",
                { title: collectionTitle }
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
                <RefreshCw aria-hidden="true" className="spin" size={14} />
              ) : (
                <Plus aria-hidden="true" size={14} />
              )}
              {t(
                busy === "plan"
                  ? "workspace.diagram.collectionCreate.reviewing"
                  : "workspace.diagram.collectionCreate.review"
              )}
            </button>
          )}
        </footer>
      </section>
    </div>
  );
}

function validInitialCollectionPreview(
  state: ModuleEditorCollectionCreateState | null,
  projectRoot: string
): ModuleEditorCollectionCreateState["preview"] | null {
  const preview = state?.preview;
  if (
    !preview ||
    preview.plan.schema !== "paradev.sdk.collection_scaffold.v1" ||
    preview.plan.kind !== "collection" ||
    preview.plan.written ||
    preview.request.projectRoot !== projectRoot ||
    preview.request.templateId !== state.templateId ||
    preview.request.collectionId !== state.collectionId ||
    (preview.request.sourceRoot ?? "") !== state.sourceRoot ||
    preview.plan.template_id !== state.templateId ||
    preview.plan.collection_id !== state.collectionId ||
    preview.plan.source_root !== state.sourceRoot
  ) {
    return null;
  }
  return preview;
}

function CollectionTemplateField({
  disabled,
  field,
  onChange,
  t,
  value
}: {
  disabled: boolean;
  field: TemplateCreateField;
  onChange: (value: string) => void;
  t: Translator;
  value: string;
}) {
  const label = `${field.label}${field.required ? " *" : ""}`;
  const placeholder = field.defaultValue
    ? t("workspace.module.editor.batch.defaultValue", {
        value: field.defaultValue
      })
    : "";
  return (
    <label className="module-create-field">
      <small>{label}</small>
      {field.choices.length > 0 || field.type === "choice" ? (
        <SelectField
          disabled={disabled}
          label={field.label}
          onChange={(event) => onChange(event.target.value)}
          options={[
            {
              label:
                placeholder ||
                t("workspace.module.editor.batch.templateDefault"),
              value: ""
            },
            ...field.choices.map((choice) => ({
              label: choice,
              value: choice
            }))
          ]}
          value={value}
          variant="compact"
        />
      ) : field.type === "text" ? (
        <textarea
          aria-label={field.label}
          disabled={disabled}
          onChange={(event) => onChange(event.target.value)}
          placeholder={placeholder}
          rows={3}
          value={value}
        />
      ) : (
        <input
          aria-label={field.label}
          disabled={disabled}
          inputMode={field.type === "number" ? "decimal" : undefined}
          onChange={(event) => onChange(event.target.value)}
          placeholder={placeholder}
          type={field.type === "number" ? "number" : "text"}
          value={value}
        />
      )}
      {field.description ? <span>{field.description}</span> : null}
    </label>
  );
}

function collectionDiagnostic(
  payload: CollectionScaffoldPayload,
  t: Translator
): string {
  const diagnostic = payload.diagnostics.find(
    (row) =>
      row.severity === "error" &&
      typeof row.message === "string" &&
      row.message.trim()
  );
  return typeof diagnostic?.message === "string"
    ? diagnostic.message
    : t("workspace.diagram.collectionCreate.blocked", {
        title: payload.family
      });
}

function dialogFocusableElements(
  dialog: HTMLElement | null
): HTMLElement[] {
  if (!dialog) {
    return [];
  }
  return [
    ...dialog.querySelectorAll<HTMLElement>(
      'button:not([disabled]), input:not([disabled]), select:not([disabled]), textarea:not([disabled]), a[href], [tabindex]:not([tabindex="-1"])'
    )
  ].filter(
    (element) =>
      !element.hasAttribute("hidden") &&
      element.getAttribute("aria-hidden") !== "true"
  );
}
