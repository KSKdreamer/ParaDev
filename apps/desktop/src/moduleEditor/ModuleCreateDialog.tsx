import {
  useEffect,
  useMemo,
  useRef,
  useState,
  type KeyboardEvent as ReactKeyboardEvent
} from "react";
import { AlertTriangle, CheckCircle2, FolderOpen, Plus, RefreshCw, Trash2, X } from "lucide-react";
import { SelectField } from "../components/ui/SelectField";
import { localizedParaDevServiceError } from "../desktopBridgeErrors";
import type { TranslationKey, Translator } from "../i18n";
import {
  createModules,
  openProjectPath,
  type ModuleCreateBatchPayload,
  type ModuleCreateBatchRow,
  type OpenPathTarget
} from "../services/paradev";
import type {
  ProjectBrowserItem,
  ProjectTemplate,
  ProjectTemplateSourceRoot
} from "../types";
import type {
  ModuleEditorBatchCreateRow,
  ModuleEditorBatchCreateState
} from "./editorSessionStore";
import {
  buildTemplateCreateFields,
  templateCreateReferenceOptions,
  type TemplateCreateField
} from "./model";

const MAX_BATCH_SIZE = 256;

type ModuleCreateDialogProps = {
  dialogText?: {
    detail: string;
    eyebrow: string;
    guidance?: string;
    title: string;
  };
  familyTitle: string;
  initialValues?: Readonly<Record<string, string>>;
  initialState?: ModuleEditorBatchCreateState | null;
  mode?: "batch" | "single";
  onApplied: (payload: ModuleCreateBatchPayload) => void | Promise<void>;
  onBusyStart?: () => () => void;
  onClose: () => void;
  onDraftChange?: (state: ModuleEditorBatchCreateState | null) => void;
  onRecoveryPathsChange: (paths: string[]) => void;
  openTarget: OpenPathTarget;
  projectId: string;
  projectRoot: string;
  recoveryPaths: string[];
  referenceItems?: readonly ProjectBrowserItem[];
  sourceRoots: ProjectTemplateSourceRoot[];
  t: Translator;
  templates: ProjectTemplate[];
};

type BatchFieldIssue = "number" | "required";

type BatchRowValidation = {
  fields: Record<string, BatchFieldIssue>;
  objectId?: "duplicate" | "required";
};

type BatchDiagnosticView = {
  code: string;
  message: string;
  moduleId: string;
  path: string;
  recoveryPath: string;
  severity: string;
};

const statusLabelKeys: Record<string, TranslationKey> = {
  blocked: "workspace.module.editor.batch.status.blocked",
  create: "workspace.module.editor.batch.status.create",
  created: "workspace.module.editor.batch.status.created",
  unchanged: "workspace.module.editor.batch.status.unchanged"
};

export function ModuleCreateDialog({
  dialogText,
  familyTitle,
  initialValues = {},
  initialState = null,
  mode = "batch",
  onApplied,
  onBusyStart,
  onClose,
  onDraftChange,
  onRecoveryPathsChange,
  openTarget,
  projectId,
  projectRoot,
  recoveryPaths,
  referenceItems = [],
  sourceRoots,
  t,
  templates
}: ModuleCreateDialogProps) {
  const single = mode === "single";
  const previouslyFocused = useRef<HTMLElement | null>(
    typeof document !== "undefined" &&
      document.activeElement instanceof HTMLElement
      ? document.activeElement
      : null
  );
  const dialogRef = useRef<HTMLElement>(null);
  const pristineTemplateId = templates[0]?.id ?? "";
  const pristineSourceRoot =
    sourceRoots.find((row) => row.default)?.path ?? sourceRoots[0]?.path ?? "";
  const initialRows =
    initialState?.rows.length
      ? initialState.rows.map(cloneBatchDraftRow)
      : [
          newBatchDraftRow(
            1,
            pristineTemplateId,
            single ? initialValues : {}
          )
        ];
  const initialPreview =
    initialState?.preview &&
    initialState.preview.plan.schema === "paradev.sdk.module_batch.v1" &&
    !initialState.preview.plan.applied &&
    !initialState.preview.plan.written &&
    initialState.preview.plan.requested_count === initialState.preview.modules.length
      ? initialState.preview
      : null;
  const nextRowKey = useRef(
    Math.max(0, ...initialRows.map((row) => row.key)) + 1
  );
  const [rows, setRows] = useState<ModuleEditorBatchCreateRow[]>(initialRows);
  const [validation, setValidation] = useState<Record<number, BatchRowValidation>>({});
  const [showAdvanced, setShowAdvanced] = useState(
    initialState?.showAdvanced ??
      (single &&
        templateFields(templates[0]).advanced.some(
          (field) => initialValues[field.name] !== undefined
        ))
  );
  const [busy, setBusy] = useState<"apply" | "plan" | "">("");
  const [error, setError] = useState("");
  const [result, setResult] = useState<ModuleCreateBatchPayload | null>(
    initialPreview?.plan ?? null
  );
  const [plannedModules, setPlannedModules] = useState<ModuleCreateBatchRow[] | null>(
    initialPreview && !initialPreview.plan.blocked
      ? cloneBatchModules(initialPreview.modules)
      : null
  );
  const [plannedSourceRoot, setPlannedSourceRoot] = useState<string | null>(
    initialPreview && !initialPreview.plan.blocked
      ? initialPreview.sourceRoot
      : null
  );
  const [sourceRoot, setSourceRoot] = useState(
    initialState?.sourceRoot.trim() || pristineSourceRoot
  );
  const [recoveryOpenError, setRecoveryOpenError] = useState("");
  const templatesById = useMemo(
    () => new Map(templates.map((template) => [template.id, template])),
    [templates]
  );
  const applied = result?.applied === true;
  const readyToApply = Boolean(result && !result.blocked && plannedModules);
  const diagnostics = result ? batchDiagnostics(result) : [];

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

  useEffect(() => {
    if (!onDraftChange) {
      return;
    }
    if (applied) {
      onDraftChange(null);
      return;
    }
    onDraftChange({
      open: true,
      pristineSourceRoot,
      pristineTemplateId,
      rows,
      showAdvanced,
      sourceRoot
    });
  }, [
    applied,
    onDraftChange,
    pristineSourceRoot,
    pristineTemplateId,
    rows,
    showAdvanced,
    sourceRoot
  ]);

  const invalidatePlan = () => {
    setResult(null);
    setPlannedModules(null);
    setPlannedSourceRoot(null);
    setError("");
    setValidation({});
  };

  const updateRow = (
    key: number,
    update: (row: ModuleEditorBatchCreateRow) => ModuleEditorBatchCreateRow
  ) => {
    if (busy || applied) {
      return;
    }
    invalidatePlan();
    setRows((current) => current.map((row) => (row.key === key ? update(row) : row)));
  };

  const addRow = () => {
    if (busy || rows.length >= MAX_BATCH_SIZE || applied) {
      return;
    }
    invalidatePlan();
    const key = nextRowKey.current;
    nextRowKey.current += 1;
    setRows((current) => [...current, newBatchDraftRow(key, templates[0]?.id ?? "")]);
  };

  const removeRow = (key: number) => {
    if (busy || rows.length <= 1 || applied) {
      return;
    }
    invalidatePlan();
    setRows((current) => current.filter((row) => row.key !== key));
  };

  const rememberRecoveryPaths = (payload: ModuleCreateBatchPayload) => {
    const paths = batchDiagnostics(payload)
      .map((diagnostic) => diagnostic.recoveryPath)
      .filter(Boolean);
    if (paths.length === 0) {
      return;
    }
    onRecoveryPathsChange([...new Set([...recoveryPaths, ...paths])]);
  };

  const handlePreview = async () => {
    if (busy || applied) {
      return;
    }
    const checked = validateBatchRows(rows, templatesById);
    setValidation(checked.validation);
    if (!checked.modules) {
      if (
        rows.some((row) =>
          templateFields(templatesById.get(row.templateId)).advanced.some(
            (field) => checked.validation[row.key]?.fields[field.name]
          )
        )
      ) {
        setShowAdvanced(true);
      }
      setError(
        t(
          single
            ? "workspace.module.editor.single.validation.fix"
            : "workspace.module.editor.batch.validation.fix"
        )
      );
      return;
    }
    const snapshot = cloneBatchModules(checked.modules);
    const finishBusy = onBusyStart?.() ?? (() => undefined);
    setBusy("plan");
    setError("");
    try {
      const payload = await createModules({
        projectId,
        projectRoot,
        modules: snapshot,
        sourceRoot: sourceRoot || undefined,
        write: false
      });
      rememberRecoveryPaths(payload);
      setResult(payload);
      setPlannedModules(payload.blocked ? null : snapshot);
      setPlannedSourceRoot(payload.blocked ? null : sourceRoot || null);
    } catch (cause: unknown) {
      setResult(null);
      setPlannedModules(null);
      setPlannedSourceRoot(null);
      setError(localizedParaDevServiceError(t, cause));
    } finally {
      finishBusy();
      setBusy("");
    }
  };

  const handleApply = async () => {
    if (busy || !result || result.blocked || !plannedModules || applied) {
      return;
    }
    const finishBusy = onBusyStart?.() ?? (() => undefined);
    setBusy("apply");
    setError("");
    try {
      const payload = await createModules({
        projectId,
        projectRoot,
        modules: cloneBatchModules(plannedModules),
        sourceRoot: plannedSourceRoot,
        write: true,
        planHash: result.plan_hash
      });
      rememberRecoveryPaths(payload);
      setResult(payload);
      setPlannedModules(null);
      setPlannedSourceRoot(null);
      if (payload.applied) {
        try {
          await onApplied(payload);
        } catch (cause: unknown) {
          setError(
            t("workspace.module.editor.batch.refreshFailed", {
              message: localizedParaDevServiceError(t, cause)
            })
          );
        }
      }
    } catch (cause: unknown) {
      setPlannedModules(null);
      setPlannedSourceRoot(null);
      setError(localizedParaDevServiceError(t, cause));
    } finally {
      finishBusy();
      setBusy("");
    }
  };

  const handleOpenRecoveryPath = async (path: string) => {
    setRecoveryOpenError("");
    try {
      await openProjectPath(path, openTarget);
    } catch (cause: unknown) {
      setRecoveryOpenError(localizedParaDevServiceError(t, cause));
    }
  };

  const handleDialogKeyDown = (event: ReactKeyboardEvent<HTMLElement>) => {
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
    const activeIndex = focusable.indexOf(document.activeElement as HTMLElement);
    if (event.shiftKey && activeIndex <= 0) {
      event.preventDefault();
      focusable.at(-1)?.focus();
    } else if (!event.shiftKey && (activeIndex < 0 || activeIndex === focusable.length - 1)) {
      event.preventDefault();
      focusable[0]?.focus();
    }
  };

  const dominantAction = applied ? (
    <button className="toolbar-button primary" onClick={onClose} type="button">
      <CheckCircle2 aria-hidden="true" size={14} />
      {t("workspace.module.editor.batch.done")}
    </button>
  ) : readyToApply ? (
    <button className="toolbar-button primary" disabled={Boolean(busy)} onClick={() => void handleApply()} type="button">
      {busy === "apply" ? <RefreshCw aria-hidden="true" className="module-batch-spinner" size={14} /> : <CheckCircle2 aria-hidden="true" size={14} />}
      {t(
        busy === "apply"
          ? single
            ? "workspace.module.editor.single.applying"
            : "workspace.module.editor.batch.applying"
          : single
            ? "workspace.module.editor.single.apply"
            : "workspace.module.editor.batch.apply",
        { count: String(result?.requested_count ?? rows.length) }
      )}
    </button>
  ) : (
    <button className="toolbar-button primary" disabled={Boolean(busy)} onClick={() => void handlePreview()} type="button">
      {busy === "plan" ? <RefreshCw aria-hidden="true" className="module-batch-spinner" size={14} /> : null}
      {t(
        busy === "plan"
          ? single
            ? "workspace.module.editor.single.previewing"
            : "workspace.module.editor.batch.previewing"
          : result
            ? single
              ? "workspace.module.editor.single.previewAgain"
              : "workspace.module.editor.batch.previewAgain"
            : single
              ? "workspace.module.editor.single.preview"
              : "workspace.module.editor.batch.preview"
      )}
    </button>
  );

  return (
    <div className="module-batch-backdrop" role="presentation">
      <section
        aria-labelledby="module-batch-title"
        aria-modal="true"
        className={`module-batch-dialog${single ? " single" : ""}`}
        onKeyDown={handleDialogKeyDown}
        ref={dialogRef}
        role="dialog"
      >
        <header className="module-batch-heading">
          <span>
            <small>
              {dialogText?.eyebrow ??
                t("workspace.module.editor.batch.eyebrow")}
            </small>
            <h3 id="module-batch-title">
              {dialogText?.title ??
                t("workspace.module.editor.batch.title", {
                  title: familyTitle
                })}
            </h3>
            <p>
              {dialogText?.detail ??
                t("workspace.module.editor.batch.detail")}
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
          {single ? (
            <p className="module-batch-guidance">
              {dialogText?.guidance ??
                t("workspace.module.editor.single.guidance")}
            </p>
          ) : (
            <span>
              <strong>
                {t("workspace.module.editor.batch.moduleCount", {
                  count: String(rows.length)
                })}
              </strong>
              <small>
                {t("workspace.module.editor.batch.moduleCountLimit", {
                  count: String(MAX_BATCH_SIZE)
                })}
              </small>
            </span>
          )}
          <div>
            {sourceRoots.length > 1 ? (
              <SelectField
                disabled={applied || Boolean(busy)}
                label={t("workspace.module.editor.batch.sourceRoot")}
                onChange={(event) => {
                  if (busy || applied) {
                    return;
                  }
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
            {rows.some((row) => templateFields(templatesById.get(row.templateId)).advanced.length > 0) ? (
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
                    : "workspace.module.editor.batch.showAdvanced"
                )}
              </button>
            ) : null}
            {!single ? (
              <button
                className="toolbar-button subtle"
                disabled={
                  applied ||
                  Boolean(busy) ||
                  rows.length >= MAX_BATCH_SIZE
                }
                onClick={addRow}
                type="button"
              >
                <Plus aria-hidden="true" size={14} />
                {t("workspace.module.editor.batch.add")}
              </button>
            ) : null}
          </div>
        </div>

        <div className="module-batch-body">
          {!applied ? (
            <ol
              aria-label={t(
                single
                  ? "workspace.module.editor.single.rows"
                  : "workspace.module.editor.batch.rows"
              )}
              className="module-batch-rows"
            >
              {rows.map((row, index) => {
                const template = templatesById.get(row.templateId);
                const fields = templateFields(template);
                const rowValidation = validation[row.key];
                return (
                  <li className="module-batch-row" key={row.key}>
                    {!single ? (
                      <div className="module-batch-row-heading">
                        <strong>
                          {t("workspace.module.editor.batch.row", {
                            index: String(index + 1)
                          })}
                        </strong>
                        <button
                          aria-label={t(
                            "workspace.module.editor.batch.removeRow",
                            {
                              index: String(index + 1)
                            }
                          )}
                          className="toolbar-button icon-only danger"
                          disabled={Boolean(busy) || rows.length <= 1}
                          onClick={() => removeRow(row.key)}
                          title={t(
                            "workspace.module.editor.batch.removeRow",
                            {
                              index: String(index + 1)
                            }
                          )}
                          type="button"
                        >
                          <Trash2 aria-hidden="true" size={13} />
                        </button>
                      </div>
                    ) : null}
                    <div className="module-batch-row-identity">
                      <label className="module-create-field">
                        <small>{t("workspace.module.editor.create.objectId")}</small>
                        <input
                          aria-invalid={Boolean(rowValidation?.objectId) || undefined}
                          aria-label={t(
                            single
                              ? "workspace.module.editor.single.objectId"
                              : "workspace.module.editor.batch.objectId",
                            { index: String(index + 1) }
                          )}
                          autoFocus={index === 0}
                          disabled={Boolean(busy)}
                          onChange={(event) =>
                            updateRow(row.key, (current) => ({
                              ...current,
                              objectId: event.target.value
                            }))
                          }
                          value={row.objectId}
                        />
                        {rowValidation?.objectId ? (
                          <span className="module-create-field-error" role="alert">
                            {t(
                              rowValidation.objectId === "duplicate"
                                ? "workspace.module.editor.batch.validation.duplicate"
                                : "workspace.module.editor.create.validation.required",
                              rowValidation.objectId === "duplicate"
                                ? { objectId: row.objectId.trim() }
                                : { field: t("workspace.module.editor.create.objectId") }
                            )}
                          </span>
                        ) : null}
                      </label>
                      <span className="module-batch-template">
                        <small>{t("workspace.module.editor.create.template")}</small>
                        {templates.length > 1 ? (
                          <SelectField
                            disabled={Boolean(busy)}
                            label={t(
                              single
                                ? "workspace.module.editor.single.template"
                                : "workspace.module.editor.batch.template",
                              { index: String(index + 1) }
                            )}
                            onChange={(event) =>
                              updateRow(row.key, (current) => ({
                                ...current,
                                templateId: event.target.value,
                                values: single
                                  ? { ...initialValues }
                                  : {}
                              }))
                            }
                            options={templates.map((item) => ({
                              label: item.title,
                              value: item.id
                            }))}
                            value={row.templateId}
                            variant="compact"
                          />
                        ) : (
                          <strong>{template?.title ?? row.templateId}</strong>
                        )}
                      </span>
                    </div>
                    <div className="module-batch-fields">
                      {fields.primary.map((field) => (
                        <BatchTemplateField
                          disabled={Boolean(busy)}
                          field={field}
                          issue={rowValidation?.fields[field.name]}
                          key={field.name}
                          onChange={(value) =>
                            updateRow(row.key, (current) => ({
                              ...current,
                              values: { ...current.values, [field.name]: value }
                            }))
                          }
                          rowIndex={index}
                          referenceItems={referenceItems}
                          single={single}
                          t={t}
                          value={row.values[field.name] ?? ""}
                        />
                      ))}
                    </div>
                    {showAdvanced && fields.advanced.length > 0 ? (
                      <div className="module-batch-fields advanced">
                        {fields.advanced.map((field) => (
                          <BatchTemplateField
                            disabled={Boolean(busy)}
                            field={field}
                            issue={rowValidation?.fields[field.name]}
                            key={field.name}
                            onChange={(value) =>
                              updateRow(row.key, (current) => ({
                                ...current,
                                values: { ...current.values, [field.name]: value }
                              }))
                            }
                            rowIndex={index}
                            referenceItems={referenceItems}
                            single={single}
                            t={t}
                            value={row.values[field.name] ?? ""}
                          />
                        ))}
                      </div>
                    ) : null}
                  </li>
                );
              })}
            </ol>
          ) : null}

          {result ? (
            <BatchResult
              diagnostics={diagnostics}
              result={result}
              single={single}
              t={t}
            />
          ) : null}

          {recoveryPaths.length > 0 ? (
            <section className="module-batch-recovery" role="alert">
              <div>
                <AlertTriangle aria-hidden="true" size={18} />
                <span>
                  <strong>{t("workspace.module.editor.batch.recoveryTitle")}</strong>
                  <small>{t("workspace.module.editor.batch.recoveryDetail")}</small>
                </span>
                <button
                  className="toolbar-button subtle module-batch-recovery-dismiss"
                  onClick={() => {
                    setRecoveryOpenError("");
                    onRecoveryPathsChange([]);
                  }}
                  type="button"
                >
                  {t("workspace.module.editor.batch.dismissRecovery")}
                </button>
              </div>
              <ul>
                {recoveryPaths.map((path) => (
                  <li key={path}>
                    <code title={path}>{path}</code>
                    <button
                      className="toolbar-button subtle"
                      onClick={() => void handleOpenRecoveryPath(path)}
                      type="button"
                    >
                      <FolderOpen aria-hidden="true" size={13} />
                      {t("workspace.module.editor.batch.openRecovery")}
                    </button>
                  </li>
                ))}
              </ul>
              {recoveryOpenError ? (
                <small className="module-batch-recovery-error">{recoveryOpenError}</small>
              ) : null}
            </section>
          ) : null}

          {error ? (
            <p className="module-batch-error" role="alert">
              {error}
            </p>
          ) : null}
        </div>

        <footer className="module-dialog-actions module-batch-actions">
          {!applied ? (
            <button
              className="toolbar-button subtle"
              disabled={Boolean(busy)}
              onClick={onClose}
              type="button"
            >
              {t("workspace.module.editor.cancel")}
            </button>
          ) : null}
          {dominantAction}
        </footer>
      </section>
    </div>
  );
}

function dialogFocusableElements(dialog: HTMLElement | null): HTMLElement[] {
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

function BatchTemplateField({
  disabled,
  field,
  issue,
  onChange,
  rowIndex,
  referenceItems,
  single,
  t,
  value
}: {
  disabled: boolean;
  field: TemplateCreateField;
  issue?: BatchFieldIssue;
  onChange: (value: string) => void;
  rowIndex: number;
  referenceItems: readonly ProjectBrowserItem[];
  single: boolean;
  t: Translator;
  value: string;
}) {
  const label = `${field.label}${field.required ? " *" : ""}`;
  const ariaLabel = t(
    single
      ? "workspace.module.editor.single.field"
      : "workspace.module.editor.batch.field",
    {
      field: field.label,
      index: String(rowIndex + 1)
    }
  );
  const placeholder = field.defaultValue
    ? t("workspace.module.editor.batch.defaultValue", { value: field.defaultValue })
    : "";
  const referenceOptions = templateCreateReferenceOptions(
    field,
    referenceItems
  );
  const referenceListId = referenceOptions.length
    ? `module-create-reference-${rowIndex}-${field.name.replace(/[^A-Za-z0-9_-]/g, "-")}`
    : undefined;
  let control;
  if (field.choices.length > 0 || field.type === "choice") {
    control = (
      <SelectField
        disabled={disabled}
        label={ariaLabel}
        onChange={(event) => onChange(event.target.value)}
        options={[
          { label: placeholder || t("workspace.module.editor.batch.templateDefault"), value: "" },
          ...field.choices.map((choice) => ({ label: choice, value: choice }))
        ]}
        value={value}
        variant="compact"
      />
    );
  } else if (field.type === "boolean") {
    control = (
      <SelectField
        disabled={disabled}
        label={ariaLabel}
        onChange={(event) => onChange(event.target.value)}
        options={[
          { label: placeholder || t("workspace.module.editor.batch.templateDefault"), value: "" },
          { label: t("workspace.module.editor.batch.boolean.true"), value: "true" },
          { label: t("workspace.module.editor.batch.boolean.false"), value: "false" }
        ]}
        value={value}
        variant="compact"
      />
    );
  } else if (field.type === "text") {
    control = (
      <textarea
        aria-invalid={Boolean(issue) || undefined}
        aria-label={ariaLabel}
        disabled={disabled}
        onChange={(event) => onChange(event.target.value)}
        placeholder={placeholder}
        rows={2}
        value={value}
      />
    );
  } else {
    control = (
      <input
        aria-invalid={Boolean(issue) || undefined}
        aria-label={ariaLabel}
        data-template-field-type={field.type}
        disabled={disabled}
        list={referenceListId}
        onChange={(event) => onChange(event.target.value)}
        placeholder={placeholder}
        step={field.type === "number" ? "any" : undefined}
        type={field.type === "number" ? "number" : "text"}
        value={value}
      />
    );
  }
  return (
    <div className="module-create-field">
      <small>{label}</small>
      {control}
      {referenceListId ? (
        <datalist id={referenceListId}>
          {referenceOptions.map((option) => (
            <option key={option.value} label={option.label} value={option.value} />
          ))}
        </datalist>
      ) : null}
      {field.description ? (
        <span
          className="module-create-field-description"
          data-description-source={field.descriptionSource ?? "generated"}
        >
          {field.description}
        </span>
      ) : null}
      {issue ? (
        <span className="module-create-field-error" role="alert">
          {t(
            issue === "number"
              ? "workspace.module.editor.create.validation.number"
              : "workspace.module.editor.create.validation.required",
            { field: field.label }
          )}
        </span>
      ) : null}
    </div>
  );
}

function BatchResult({
  diagnostics,
  result,
  single,
  t
}: {
  diagnostics: BatchDiagnosticView[];
  result: ModuleCreateBatchPayload;
  single: boolean;
  t: Translator;
}) {
  const state = result.applied ? "applied" : result.blocked ? "blocked" : "ready";
  const headingKey: TranslationKey =
    state === "applied"
      ? "workspace.module.editor.batch.resultApplied"
      : state === "blocked"
        ? single
          ? "workspace.module.editor.single.resultBlocked"
          : "workspace.module.editor.batch.resultBlocked"
        : "workspace.module.editor.batch.resultReady";
  const detailKey: TranslationKey =
    state === "applied"
      ? result.written
        ? single
          ? "workspace.module.editor.single.resultAppliedDetail"
          : "workspace.module.editor.batch.resultAppliedDetail"
        : "workspace.module.editor.batch.resultUnchangedDetail"
      : state === "blocked"
        ? single
          ? "workspace.module.editor.single.resultBlockedDetail"
          : "workspace.module.editor.batch.resultBlockedDetail"
        : "workspace.module.editor.batch.resultReadyDetail";
  return (
    <section aria-live="polite" className={`module-batch-result ${state}`}>
      <header>
        {state === "blocked" ? (
          <AlertTriangle aria-hidden="true" size={18} />
        ) : (
          <CheckCircle2 aria-hidden="true" size={18} />
        )}
        <span>
          <strong>{t(headingKey)}</strong>
          <small>{t(detailKey)}</small>
        </span>
      </header>
      <div className="module-batch-counts">
        {(["create", "created", "unchanged", "blocked"] as const).map((status) =>
          result.counts[status] > 0 ? (
            <span className={`module-batch-count ${status}`} key={status}>
              {t(statusLabelKeys[status])}: {result.counts[status]}
            </span>
          ) : null
        )}
      </div>
      <div className="module-batch-plan-hash">
        <small>{t("workspace.module.editor.batch.planHash")}</small>
        <code title={result.plan_hash}>{result.plan_hash}</code>
      </div>
      <div className="module-batch-plan-hash">
        <small>{t("workspace.module.editor.batch.sourceRoot")}</small>
        <code title={result.source_root}>{result.source_root}</code>
      </div>
      <ul aria-label={t("workspace.module.editor.batch.reviewRows")} className="module-batch-review-rows">
        {result.modules.map((module, index) => {
          const moduleId = recordText(module, "module_id") || recordText(module, "object_id") || String(index + 1);
          const status = recordText(module, "status") || "blocked";
          return (
            <li key={`${moduleId}:${index}`}>
              <span>
                <strong>{moduleId}</strong>
                <small>
                  {t("workspace.module.editor.batch.fileCount", {
                    count: String(recordArray(module, "files").length)
                  })}
                </small>
              </span>
              <span className={`module-batch-status ${status}`}>
                {t(statusLabelKeys[status] ?? "workspace.module.editor.batch.status.blocked")}
              </span>
            </li>
          );
        })}
      </ul>
      {diagnostics.length > 0 ? (
        <div className="module-batch-diagnostics">
          <strong>{t("workspace.module.editor.batch.diagnostics")}</strong>
          <ul>
            {diagnostics.map((diagnostic, index) => (
              <li className={diagnostic.severity === "error" ? "error" : "warning"} key={`${diagnostic.code}:${diagnostic.moduleId}:${index}`}>
                <span>
                  <code>{diagnostic.code}</code>
                  {diagnostic.moduleId ? <small>{diagnostic.moduleId}</small> : null}
                </span>
                <p>{diagnostic.message}</p>
                {diagnostic.path && diagnostic.path !== diagnostic.recoveryPath ? (
                  <code title={diagnostic.path}>{diagnostic.path}</code>
                ) : null}
              </li>
            ))}
          </ul>
        </div>
      ) : null}
    </section>
  );
}

function newBatchDraftRow(
  key: number,
  templateId: string,
  values: Readonly<Record<string, string>> = {}
): ModuleEditorBatchCreateRow {
  return {
    key,
    objectId: "",
    templateId,
    values: { ...values }
  };
}

function cloneBatchDraftRow(
  row: ModuleEditorBatchCreateRow
): ModuleEditorBatchCreateRow {
  return {
    ...row,
    values: { ...row.values }
  };
}

function templateFields(template: ProjectTemplate | undefined) {
  return buildTemplateCreateFields(template ?? null);
}

function validateBatchRows(
  rows: ModuleEditorBatchCreateRow[],
  templatesById: ReadonlyMap<string, ProjectTemplate>
): {
  modules: ModuleCreateBatchRow[] | null;
  validation: Record<number, BatchRowValidation>;
} {
  const validation: Record<number, BatchRowValidation> = {};
  const targets = new Map<string, number[]>();
  const modules: ModuleCreateBatchRow[] = [];
  let invalid = false;

  for (const row of rows) {
    const template = templatesById.get(row.templateId);
    const objectId = row.objectId.trim();
    const fields = templateFields(template);
    const fieldIssues: Record<string, BatchFieldIssue> = {};
    if (!objectId || !template) {
      invalid = true;
      validation[row.key] = {
        fields: fieldIssues,
        objectId: "required"
      };
      continue;
    }
    for (const field of [...fields.primary, ...fields.advanced]) {
      const value = row.values[field.name]?.trim() ?? "";
      if (field.required && !value && !field.defaultValue.trim()) {
        fieldIssues[field.name] = "required";
      } else if (field.type === "number" && value && !Number.isFinite(Number(value))) {
        fieldIssues[field.name] = "number";
      }
    }
    if (Object.keys(fieldIssues).length > 0) {
      invalid = true;
      validation[row.key] = { fields: fieldIssues };
    }
    const target = `${template.family}/${objectId}`.normalize("NFC").toLowerCase();
    targets.set(target, [...(targets.get(target) ?? []), row.key]);
    modules.push({
      template_id: template.id,
      object_id: objectId,
      values: batchValues(row, [...fields.primary, ...fields.advanced])
    });
  }

  for (const keys of targets.values()) {
    if (keys.length < 2) {
      continue;
    }
    invalid = true;
    for (const key of keys) {
      validation[key] = {
        fields: validation[key]?.fields ?? {},
        objectId: "duplicate"
      };
    }
  }
  return {
    modules: invalid || modules.length !== rows.length ? null : modules,
    validation
  };
}

function batchValues(
  row: ModuleEditorBatchCreateRow,
  fields: TemplateCreateField[]
): Record<string, unknown> {
  const values: Record<string, unknown> = {};
  for (const field of fields) {
    const value = row.values[field.name]?.trim() ?? "";
    if (!value) {
      continue;
    }
    values[field.name] =
      field.type === "boolean"
        ? value === "true"
        : field.type === "number"
          ? Number(value)
          : value;
  }
  return values;
}

function cloneBatchModules(modules: readonly ModuleCreateBatchRow[]): ModuleCreateBatchRow[] {
  return modules.map((module) => {
    const common = {
      object_id: module.object_id,
      values: { ...(module.values ?? {}) }
    };
    if (typeof module.template_id === "string") {
      return { ...common, template_id: module.template_id };
    }
    if (typeof module.family === "string") {
      return { ...common, family: module.family };
    }
    return { ...common, family_or_template: module.family_or_template };
  });
}

function batchDiagnostics(payload: ModuleCreateBatchPayload): BatchDiagnosticView[] {
  const diagnostics = payload.diagnostics.map((diagnostic) => diagnosticView(diagnostic, ""));
  for (const module of payload.modules) {
    const moduleId = recordText(module, "module_id") || recordText(module, "object_id");
    diagnostics.push(
      ...recordArray(module, "diagnostics").map((diagnostic) => diagnosticView(diagnostic, moduleId))
    );
    const catalogMutation = recordValue(module, "catalog_mutation");
    if (
      isRecord(catalogMutation) &&
      (catalogMutation.status === "failed" || catalogMutation.status === "unverified")
    ) {
      diagnostics.push({
        code: recordText(catalogMutation, "code") || "catalog.mutation.unverified",
        message: recordText(catalogMutation, "message"),
        moduleId,
        path: recordText(catalogMutation, "database"),
        recoveryPath: "",
        severity: "warning"
      });
    }
  }
  return diagnostics;
}

function diagnosticView(diagnostic: Record<string, unknown>, moduleId: string): BatchDiagnosticView {
  return {
    code: recordText(diagnostic, "code") || "module_batch.unknown",
    message: recordText(diagnostic, "message"),
    moduleId: recordText(diagnostic, "module_id") || moduleId,
    path: recordText(diagnostic, "path"),
    recoveryPath: recordText(diagnostic, "recovery_path"),
    severity: recordText(diagnostic, "severity") || "error"
  };
}

function recordArray(value: Record<string, unknown>, key: string): Record<string, unknown>[] {
  const candidate = value[key];
  return Array.isArray(candidate) ? candidate.filter(isRecord) : [];
}

function recordText(value: Record<string, unknown>, key: string): string {
  const candidate = value[key];
  return typeof candidate === "string" ? candidate : "";
}

function recordValue(value: Record<string, unknown>, key: string): unknown {
  return value[key];
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return value !== null && typeof value === "object" && !Array.isArray(value);
}
