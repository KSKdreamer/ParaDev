import {
  Component,
  type ErrorInfo,
  type ReactNode
} from "react";
import { RefreshCw, RotateCcw, TriangleAlert } from "lucide-react";
import { APP_SETTINGS_STORAGE_KEY } from "../appSettingsStorage";
import {
  createTranslator,
  htmlLangForLocale,
  type Locale
} from "../i18n";
import type { ThemeName } from "../types";

const RENDERER_FAILURE_LOG_MESSAGE =
  "ParaDev renderer failure captured.";
const KNOWN_ERROR_NAMES = new Set([
  "AggregateError",
  "Error",
  "EvalError",
  "RangeError",
  "ReferenceError",
  "SyntaxError",
  "TypeError",
  "URIError"
]);

export type RendererFailureKind =
  | "react-render"
  | "unhandled-rejection"
  | "window-error";

export type RendererFailureReport = {
  schema: "paradev.desktop.renderer-failure.v1";
  kind: RendererFailureKind;
  errorName: string;
  components: string[];
};

type RendererErrorBoundaryProps = {
  children: ReactNode;
  reloadApplication?: () => void;
};

type RendererErrorBoundaryState = {
  failed: boolean;
};

type RendererRecoveryPreferences = {
  locale: Locale;
  theme: ThemeName;
};

export class RendererErrorBoundary extends Component<
  RendererErrorBoundaryProps,
  RendererErrorBoundaryState
> {
  state: RendererErrorBoundaryState = {
    failed: false
  };

  private removeWindowFailureReporting: (() => void) | null = null;

  static getDerivedStateFromError(): RendererErrorBoundaryState {
    return { failed: true };
  }

  componentDidMount(): void {
    this.removeWindowFailureReporting =
      installWindowRendererFailureReporting();
  }

  componentDidCatch(error: unknown, info: ErrorInfo): void {
    reportRendererFailure("react-render", error, info.componentStack ?? "");
  }

  componentWillUnmount(): void {
    this.removeWindowFailureReporting?.();
    this.removeWindowFailureReporting = null;
  }

  private retryInterface = (): void => {
    this.setState({ failed: false });
  };

  private reloadApplication = (): void => {
    if (this.props.reloadApplication) {
      this.props.reloadApplication();
      return;
    }
    if (typeof window !== "undefined") {
      window.location.reload();
    }
  };

  render(): ReactNode {
    if (!this.state.failed) {
      return this.props.children;
    }

    const preferences = rendererRecoveryPreferences();
    const t = createTranslator(preferences.locale);

    return (
      <main
        className={`project-onboarding renderer-recovery theme-${preferences.theme}`}
        lang={htmlLangForLocale(preferences.locale)}
      >
        <section
          aria-labelledby="renderer-recovery-title"
          className="project-onboarding-card renderer-recovery-card"
          role="alert"
        >
          <div aria-hidden="true" className="project-onboarding-mark">
            <TriangleAlert size={28} />
          </div>
          <p className="project-onboarding-eyebrow">
            {t("app.failure.eyebrow")}
          </p>
          <h1 id="renderer-recovery-title">{t("app.failure.title")}</h1>
          <p className="project-onboarding-detail">
            {t("app.failure.detail")}
          </p>
          <p className="renderer-recovery-report">
            {t("app.failure.reported")}
          </p>
          <div className="renderer-recovery-actions">
            <button
              className="toolbar-button primary project-onboarding-action"
              onClick={this.retryInterface}
              type="button"
            >
              <RotateCcw aria-hidden="true" size={16} />
              {t("app.failure.retry")}
            </button>
            <button
              className="toolbar-button project-onboarding-action"
              onClick={this.reloadApplication}
              type="button"
            >
              <RefreshCw aria-hidden="true" size={16} />
              {t("app.failure.reload")}
            </button>
          </div>
          <small className="project-onboarding-hint">
            {t("app.failure.hint")}
          </small>
        </section>
      </main>
    );
  }
}

export function installWindowRendererFailureReporting(
  target: Window | null =
    typeof window === "undefined" ? null : window
): () => void {
  if (!target) {
    return () => undefined;
  }
  const reportWindowError = (event: ErrorEvent) => {
    reportRendererFailure("window-error", event.error);
  };
  const reportUnhandledRejection = (event: PromiseRejectionEvent) => {
    reportRendererFailure("unhandled-rejection", event.reason);
  };
  target.addEventListener("error", reportWindowError);
  target.addEventListener("unhandledrejection", reportUnhandledRejection);
  return () => {
    target.removeEventListener("error", reportWindowError);
    target.removeEventListener(
      "unhandledrejection",
      reportUnhandledRejection
    );
  };
}

export function reportRendererFailure(
  kind: RendererFailureKind,
  error: unknown,
  componentStack = ""
): RendererFailureReport {
  const report: RendererFailureReport = {
    schema: "paradev.desktop.renderer-failure.v1",
    kind,
    errorName: safeErrorName(error),
    components: safeComponentNames(componentStack)
  };
  try {
    console.error(RENDERER_FAILURE_LOG_MESSAGE, report);
  } catch {
    // Recovery reporting must never replace the original failure.
  }
  return report;
}

export function rendererRecoveryPreferences(
  storage?: Pick<Storage, "getItem"> | null,
  documentLanguage =
    typeof document === "undefined" ? "en" : document.documentElement.lang
): RendererRecoveryPreferences {
  const fallback: RendererRecoveryPreferences = {
    locale: documentLanguage.toLowerCase().startsWith("zh") ? "zh" : "en",
    theme: "anthropic"
  };
  const selectedStorage =
    storage === undefined ? safeWindowStorage() : storage;
  if (!selectedStorage) {
    return fallback;
  }
  try {
    const raw = selectedStorage.getItem(APP_SETTINGS_STORAGE_KEY);
    if (!raw) {
      return fallback;
    }
    const value = JSON.parse(raw) as unknown;
    if (!isRecord(value)) {
      return fallback;
    }
    return {
      locale: value.locale === "en" || value.locale === "zh"
        ? value.locale
        : fallback.locale,
      theme:
        value.theme === "light" ||
        value.theme === "dark" ||
        value.theme === "anthropic"
          ? value.theme
          : fallback.theme
    };
  } catch {
    return fallback;
  }
}

function safeErrorName(error: unknown): string {
  const name =
    error instanceof Error && typeof error.name === "string"
      ? error.name
      : "";
  return KNOWN_ERROR_NAMES.has(name) ? name : "UnknownError";
}

function safeComponentNames(componentStack: string): string[] {
  const names = componentStack
    .split("\n")
    .flatMap((line) => {
      const match = line.match(/^\s*at\s+([A-Za-z][\w.$-]*)/);
      return match?.[1] ? [match[1]] : [];
    });
  return [...new Set(names)].slice(0, 12);
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return Boolean(value) && typeof value === "object" && !Array.isArray(value);
}

function safeWindowStorage(): Pick<Storage, "getItem"> | null {
  if (typeof window === "undefined") {
    return null;
  }
  try {
    return window.localStorage;
  } catch {
    return null;
  }
}
