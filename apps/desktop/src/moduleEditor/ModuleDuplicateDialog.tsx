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
  CopyPlus,
  FileText,
  FolderTree,
  RefreshCw,
  X
} from "lucide-react";
import { SelectField } from "../components/ui/SelectField";
import { localizedParaDevServiceError } from "../desktopBridgeErrors";
import type { Translator } from "../i18n";
import {
  duplicateModule,
  type ModuleDuplicatePayload
} from "../services/paradev";
import type { ProjectTemplateSourceRoot } from "../types";

type ModuleDuplicateDialogProps = {
  moduleId: string;
  objectId: string;
  onApplied: (payload: ModuleDuplicatePayload) => Promise<void>;
  onBusyStart?: () => () => void;
  onClose: () => void;
  projectRoot: string;
  sourceRoot?: string;
  sourceRoots: ProjectTemplateSourceRoot[];
  t: Translator;
  title: string;
};

type FrozenDuplicateRequest = {
  destinationSourceRoot?: string;
  objectId: string;
};

export function ModuleDuplicateDialog({
  moduleId,
  objectId,
  onApplied,
  onBusyStart,
  onClose,
  projectRoot,
  sourceRoot,
  sourceRoots,
  t,
  title
}: ModuleDuplicateDialogProps) {
  const previouslyFocused = useRef<HTMLElement | null>(
    typeof document !== "undefined" &&
      document.activeElement instanceof HTMLElement
      ? document.activeElement
      : null
  );
  const dialogRef = useRef<HTMLElement>(null);
  const objectIdRef = useRef<HTMLInputElement>(null);
  const [targetObjectId, setTargetObjectId] = useState(
    suggestedDuplicateObjectId(objectId)
  );
  const [destinationSourceRoot, setDestinationSourceRoot] = useState("");
  const [busy, setBusy] = useState<"apply" | "plan" | "">("");
  const [error, setError] = useState("");
  const [plan, setPlan] = useState<ModuleDuplicatePayload | null>(null);
  const [frozenRequest, setFrozenRequest] =
    useState<FrozenDuplicateRequest | null>(null);
  const destinationOptions = useMemo(
    () => duplicateDestinationOptions(sourceRoots, sourceRoot, t),
    [sourceRoot, sourceRoots, t]
  );
  const readyToApply = Boolean(
    plan && frozenRequest && !plan.blocked && plan.status === "planned"
  );

  useEffect(() => {
    objectIdRef.current?.focus();
    objectIdRef.current?.select();
    return () => {
      if (previouslyFocused.current?.isConnected) {
        previouslyFocused.current.focus();
      }
    };
  }, []);

  const invalidatePlan = () => {
    if (busy) {
      return;
    }
    setPlan(null);
    setFrozenRequest(null);
    setError("");
  };

  const handlePreview = async () => {
    if (busy) {
      return;
    }
    const nextObjectId = targetObjectId.trim();
    if (!nextObjectId) {
      setError(t("workspace.module.editor.duplicate.objectIdRequired"));
      objectIdRef.current?.focus();
      return;
    }
    if (nextObjectId === objectId.trim()) {
      setError(t("workspace.module.editor.duplicate.objectIdUnchanged"));
      objectIdRef.current?.focus();
      return;
    }
    const request: FrozenDuplicateRequest = {
      objectId: nextObjectId,
      ...(destinationSourceRoot
        ? { destinationSourceRoot }
        : {})
    };
    setBusy("plan");
    setError("");
    const finishBusy = onBusyStart?.() ?? (() => undefined);
    try {
      const payload = await duplicateModule({
        projectRoot,
        moduleId,
        objectId: request.objectId,
        ...(sourceRoot ? { sourceRoot } : {}),
        ...(request.destinationSourceRoot
          ? { destinationSourceRoot: request.destinationSourceRoot }
          : {}),
        identity: "rewrite",
        write: false
      });
      setPlan(payload);
      setFrozenRequest(payload.blocked ? null : request);
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
    if (busy || !plan || !frozenRequest || plan.blocked) {
      return;
    }
    setBusy("apply");
    setError("");
    const finishBusy = onBusyStart?.() ?? (() => undefined);
    let applied = false;
    try {
      const payload = await duplicateModule({
        projectRoot,
        moduleId,
        objectId: frozenRequest.objectId,
        ...(sourceRoot ? { sourceRoot } : {}),
        ...(frozenRequest.destinationSourceRoot
          ? { destinationSourceRoot: frozenRequest.destinationSourceRoot }
          : {}),
        identity: "rewrite",
        write: true,
        planHash: plan.plan_hash
      });
      if (payload.blocked || !payload.written) {
        setPlan(payload);
        setFrozenRequest(null);
        return;
      }
      await onApplied(payload);
      if (payload.diagnostics.length > 0) {
        setPlan(payload);
        setFrozenRequest(null);
      } else {
        applied = true;
      }
    } catch (cause: unknown) {
      setError(localizedParaDevServiceError(t, cause));
    } finally {
      finishBusy();
      setBusy("");
    }
    if (applied) {
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
    <div className="module-duplicate-backdrop" role="presentation">
      <section
        aria-describedby="module-duplicate-detail"
        aria-labelledby="module-duplicate-title"
        aria-modal="true"
        className="module-duplicate-dialog"
        onKeyDown={handleDialogKeyDown}
        ref={dialogRef}
        role="dialog"
      >
        <header className="module-duplicate-heading">
          <span>
            <small>{t("workspace.module.editor.duplicate.eyebrow")}</small>
            <h3 id="module-duplicate-title">
              {t("workspace.module.editor.duplicate.title", { title })}
            </h3>
            <p id="module-duplicate-detail">
              {t("workspace.module.editor.duplicate.detail")}
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

        <div className="module-duplicate-fields">
          <label>
            <span>{t("workspace.module.editor.duplicate.objectId")}</span>
            <input
              aria-label={t("workspace.module.editor.duplicate.objectId")}
              disabled={Boolean(busy)}
              onChange={(event) => {
                invalidatePlan();
                setTargetObjectId(event.target.value);
              }}
              ref={objectIdRef}
              spellCheck={false}
              value={targetObjectId}
            />
          </label>
          <label>
            <span>{t("workspace.module.editor.duplicate.source")}</span>
            <input
              aria-label={t("workspace.module.editor.duplicate.source")}
              readOnly
              value={moduleId}
            />
          </label>
          <div className="module-duplicate-destination">
            <span>{t("workspace.module.editor.duplicate.destinationRoot")}</span>
            <SelectField
              disabled={Boolean(busy)}
              label={t("workspace.module.editor.duplicate.destinationRoot")}
              onChange={(event) => {
                invalidatePlan();
                setDestinationSourceRoot(event.target.value);
              }}
              options={destinationOptions}
              value={destinationSourceRoot}
            />
          </div>
        </div>

        {plan ? (
          <DuplicatePlanReview plan={plan} t={t} />
        ) : (
          <div className="module-duplicate-placeholder">
            <CopyPlus aria-hidden="true" size={18} />
            <p>{t("workspace.module.editor.duplicate.previewFirst")}</p>
          </div>
        )}

        {error ? (
          <p className="module-duplicate-error" role="alert">
            {error}
          </p>
        ) : null}

        <footer className="module-dialog-actions module-duplicate-actions">
          <button
            className="toolbar-button subtle"
            disabled={Boolean(busy)}
            onClick={onClose}
            type="button"
          >
            {t("workspace.module.editor.cancel")}
          </button>
          {plan?.status === "duplicated" ? (
            <button
              className="toolbar-button primary"
              disabled={Boolean(busy)}
              onClick={onClose}
              type="button"
            >
              <CheckCircle2 aria-hidden="true" size={14} />
              {t("workspace.module.editor.duplicate.done")}
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
                  ? "workspace.module.editor.duplicate.applying"
                  : "workspace.module.editor.duplicate.apply"
              )}
            </button>
          ) : (
            <button
              className="toolbar-button primary"
              disabled={Boolean(busy)}
              onClick={() => void handlePreview()}
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
                  ? "workspace.module.editor.duplicate.previewing"
                  : plan
                    ? "workspace.module.editor.duplicate.previewAgain"
                    : "workspace.module.editor.duplicate.preview"
              )}
            </button>
          )}
        </footer>
      </section>
    </div>
  );
}

function DuplicatePlanReview({
  plan,
  t
}: {
  plan: ModuleDuplicatePayload;
  t: Translator;
}) {
  const diagnostics = plan.diagnostics
    .map((row) => ({
      message: recordText(row, "message") || recordText(row, "code"),
      severity: recordText(row, "severity")
    }))
    .filter((row) => Boolean(row.message));
  const completed = plan.status === "duplicated";
  return (
    <div
      aria-live={plan.blocked ? undefined : "polite"}
      className={`module-duplicate-review${plan.blocked ? " blocked" : ""}`}
      role={plan.blocked ? "alert" : undefined}
    >
      <header>
        {plan.blocked ? (
          <AlertTriangle aria-hidden="true" size={16} />
        ) : (
          <CheckCircle2 aria-hidden="true" size={16} />
        )}
        <span>
          <strong>
            {t(
              plan.blocked
                ? "workspace.module.editor.duplicate.blocked"
                : completed
                  ? "workspace.module.editor.duplicate.completed"
                  : "workspace.module.editor.duplicate.ready"
            )}
          </strong>
          <small>
            {t(
              plan.blocked
                ? "workspace.module.editor.duplicate.blockedDetail"
                : completed
                  ? "workspace.module.editor.duplicate.completedDetail"
                  : "workspace.module.editor.duplicate.readyDetail"
            )}
          </small>
        </span>
      </header>
      <div className="module-duplicate-route">
        <code>{plan.source_module_id}</code>
        <span aria-hidden="true">→</span>
        <code>{plan.module_id}</code>
      </div>
      <div className="module-duplicate-totals">
        <span>
          <FolderTree aria-hidden="true" size={14} />
          {t("workspace.module.editor.duplicate.directoryCount", {
            count: plan.totals.directory_count
          })}
        </span>
        <span>
          <FileText aria-hidden="true" size={14} />
          {t("workspace.module.editor.duplicate.fileCount", {
            count: plan.totals.file_count
          })}
        </span>
        <span>
          {t("workspace.module.editor.duplicate.byteCount", {
            count: formatBytes(plan.totals.target_size_bytes)
          })}
        </span>
      </div>
      {!plan.blocked ? (
        plan.identity_mode === "rewrite" ? (
          <div className="module-duplicate-identity">
            <CheckCircle2 aria-hidden="true" size={15} />
            <p>
              {t("workspace.module.editor.duplicate.identityRewrite", {
                files: plan.totals.rewritten_file_count,
                paths: plan.totals.renamed_path_count
              })}
            </p>
          </div>
        ) : (
          <div className="module-duplicate-warning">
            <AlertTriangle aria-hidden="true" size={15} />
            <p>{t("workspace.module.editor.duplicate.literalWarning")}</p>
          </div>
        )
      ) : null}
      {plan.exclusions.length > 0 ? (
        <details>
          <summary>
            {t("workspace.module.editor.duplicate.exclusions", {
              count: plan.exclusions.length
            })}
          </summary>
          <ul>
            {plan.exclusions.map((row, index) => (
              <li key={`${recordText(row, "relative_path")}:${index}`}>
                <code>
                  {recordText(row, "relative_path") ||
                    t("workspace.module.editor.duplicate.systemMetadata")}
                </code>
                {recordText(row, "reason") ? (
                  <span>{recordText(row, "reason")}</span>
                ) : null}
              </li>
            ))}
          </ul>
        </details>
      ) : null}
      {diagnostics.length > 0 ? (
        <ul className="module-duplicate-diagnostics">
          {diagnostics.map((diagnostic, index) => (
            <li
              className={
                diagnostic.severity === "warning" ? "warning" : undefined
              }
              key={`${diagnostic.message}:${index}`}
            >
              {diagnostic.message}
            </li>
          ))}
        </ul>
      ) : null}
      <small className="module-duplicate-plan-hash">
        {t("workspace.module.editor.duplicate.planHash")}
        <code>{plan.plan_hash}</code>
      </small>
    </div>
  );
}

function duplicateDestinationOptions(
  sourceRoots: ProjectTemplateSourceRoot[],
  sourceRoot: string | undefined,
  t: Translator
): Array<{ label: string; value: string }> {
  const options = [
    {
      label: t("workspace.module.editor.duplicate.sameSourceRoot"),
      value: ""
    }
  ];
  const seen = new Set<string>([sourceRoot?.trim() ?? ""]);
  for (const row of sourceRoots) {
    const path = row.path.trim();
    if (!path || seen.has(path)) {
      continue;
    }
    seen.add(path);
    options.push({
      label: row.relative_path || row.path,
      value: row.path
    });
  }
  return options;
}

function suggestedDuplicateObjectId(objectId: string): string {
  const normalized = objectId.trim();
  const usesUppercaseIdentifiers =
    /[A-Z]/.test(normalized) && normalized === normalized.toUpperCase();
  return `${normalized}${usesUppercaseIdentifiers ? "_COPY" : "_copy"}`;
}

function recordText(row: Record<string, unknown>, key: string): string {
  return typeof row[key] === "string" ? row[key].trim() : "";
}

function formatBytes(bytes: number): string {
  if (bytes < 1024) {
    return `${bytes} B`;
  }
  const units = ["KiB", "MiB", "GiB"];
  let value = bytes / 1024;
  let unit = units[0];
  for (const candidate of units.slice(1)) {
    if (value < 1024) {
      break;
    }
    value /= 1024;
    unit = candidate;
  }
  return `${value.toFixed(value >= 10 ? 0 : 1)} ${unit}`;
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
