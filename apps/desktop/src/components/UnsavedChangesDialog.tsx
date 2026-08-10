import { useEffect, useRef, type KeyboardEvent as ReactKeyboardEvent } from "react";
import { AlertTriangle } from "lucide-react";
import type { Translator } from "../i18n";

type UnsavedChangesDialogProps = {
  busy: boolean;
  dirtySessionCount: number;
  error?: string;
  onCancel: () => void;
  onDiscard: () => void;
  t: Translator;
};

export function UnsavedChangesDialog({
  busy,
  dirtySessionCount,
  error,
  onCancel,
  onDiscard,
  t
}: UnsavedChangesDialogProps) {
  const dialogRef = useRef<HTMLElement>(null);
  const keepEditingRef = useRef<HTMLButtonElement>(null);
  const previouslyFocused = useRef<HTMLElement | null>(null);
  const closeFailureOnly = !busy && dirtySessionCount === 0 && Boolean(error);
  const cleanReady = !busy && dirtySessionCount === 0 && !error;

  useEffect(() => {
    if (cleanReady) {
      return;
    }
    previouslyFocused.current =
      document.activeElement instanceof HTMLElement ? document.activeElement : null;
    keepEditingRef.current?.focus();
    return () => {
      if (previouslyFocused.current?.isConnected) {
        previouslyFocused.current.focus();
      }
    };
  }, [cleanReady]);

  const handleKeyDown = (event: ReactKeyboardEvent<HTMLElement>) => {
    if (event.key === "Escape") {
      event.preventDefault();
      onCancel();
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

  if (cleanReady) {
    return null;
  }

  return (
    <div className="unsaved-changes-backdrop" role="presentation">
      <section
        aria-describedby="unsaved-changes-detail"
        aria-labelledby="unsaved-changes-title"
        aria-modal="true"
        className="unsaved-changes-dialog"
        onKeyDown={handleKeyDown}
        ref={dialogRef}
        role="alertdialog"
      >
        <header>
          <span className="panel-icon warning">
            <AlertTriangle aria-hidden="true" size={18} />
          </span>
          <div>
            <h2 id="unsaved-changes-title">
              {t(
                closeFailureOnly
                  ? "workspace.unsaved.tabCloseFailedTitle"
                  : "workspace.unsaved.title"
              )}
            </h2>
            <p id="unsaved-changes-detail">
              {closeFailureOnly
                ? t(
                    "workspace.unsaved.tabCloseFailedDetail"
                  )
                : busy
                ? t("workspace.unsaved.busy")
                : t("workspace.unsaved.tabDetail")}
            </p>
            {error ? (
              <p className="unsaved-changes-error" role="alert">
                {error}
              </p>
            ) : null}
          </div>
        </header>
        <footer>
          <button
            className="toolbar-button primary"
            onClick={onCancel}
            ref={keepEditingRef}
            type="button"
          >
            {t(
              closeFailureOnly
                ? "workspace.unsaved.keepTabOpen"
                : "workspace.unsaved.keepEditing"
            )}
          </button>
          <button
            className="toolbar-button danger"
            disabled={busy}
            onClick={onDiscard}
            type="button"
          >
            {t(
              closeFailureOnly
                ? "workspace.unsaved.tryCloseTabAgain"
                : "workspace.unsaved.discardAndClose"
            )}
          </button>
        </footer>
      </section>
    </div>
  );
}

function dialogFocusableElements(root: HTMLElement | null): HTMLElement[] {
  if (!root) {
    return [];
  }
  return Array.from(
    root.querySelectorAll<HTMLElement>(
      'button:not(:disabled), [href], input:not(:disabled), select:not(:disabled), textarea:not(:disabled), [tabindex]:not([tabindex="-1"])'
    )
  ).filter((element) => !element.hasAttribute("hidden"));
}
