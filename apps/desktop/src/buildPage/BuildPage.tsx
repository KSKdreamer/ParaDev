import {
  AlertTriangle,
  Box,
  CheckCircle2,
  ChevronDown,
  ChevronRight,
  Clock3,
  Ellipsis,
  FileText,
  FolderOpen,
  Hammer,
  History,
  Play,
  RefreshCw,
  Square,
  TerminalSquare,
  Trash2,
  XCircle
} from "lucide-react";
import type { ReactNode } from "react";
import { useEffect, useMemo, useRef, useState } from "react";
import { SelectField } from "../components/ui/SelectField";
import type { FrontendApiAction, FrontendApiActionPanelState, FrontendApiRestPlanResult, FrontendApiSubmittedValues } from "../data/frontendApi";
import { DESKTOP_CONFIG_KEYS } from "../desktopConfig";
import { localizeDesktopBridgeError } from "../desktopBridgeErrors";
import { PARADEV_FRONTEND_API_CONTRACT } from "../generated/frontendApi";
import type { ParaDevFrontendApiOperationId } from "../generated/frontendApi";
import type { TranslationKey, Translator } from "../i18n";
import {
  hasDesktopBackend,
  loadHoi4LaunchReadiness,
  loadProjectInspection,
  openProjectPath,
  readConfigValue,
  runHoi4Game,
  writeConfigValue,
  type Hoi4LaunchReadinessPayload,
  type OpenPathTarget,
  type ProjectBuildRequest
} from "../services/paradev";
import type { AiOperationIntent, ProjectBrowserPayload, ProjectOption } from "../types";
import {
  loadCachedBuildDiagnostics,
  type BuildDiagnosticsRefreshSource
} from "./buildDiagnosticsCache";
import {
  BUILD_RUN_FULL_KEY,
  BUILD_HOI4_LAUNCH_MODE_VALUES,
  BUILD_PARALLELISM_MIN,
  buildBuildDashboardModel,
  buildOverviewRuntime,
  buildOutputOpenPath,
  buildParallelismFromConfig,
  buildRunGameDisabled,
  buildTargetKey,
  hoi4GameRootFromConfig,
  hoi4LaunchModeFromConfig,
  readBuildPageSettings,
  resolveBuildTargetForBrowser,
  sameBuildTarget,
  strictMetadataFromConfig,
  writeBuildPageSettings,
  type BuildEntityRow,
  type BuildHistoryEntry,
  type BuildMode,
  type BuildPartialResult,
  type BuildRunState,
  type BuildTarget,
  type BuildTargetIntent,
  type Hoi4LaunchMode
} from "./buildPageModel";
import {
  buildRunsForProject,
  effectiveBuildRuns,
  type BuildRunLifecycleController,
  type BuildRunRecord
} from "./buildRunLifecycle";

type BuildPageProps = {
  activeProject: ProjectOption;
  aiOperationIntent?: AiOperationIntent | null;
  browser: ProjectBrowserPayload | null;
  buildDiagnosticsGeneration?: number;
  buildDiagnosticsRefreshSource?: BuildDiagnosticsRefreshSource;
  buildLifecycle: BuildRunLifecycleController;
  buildTargetIntent?: BuildTargetIntent | null;
  onBuildTargetIntentConsumed?: (nonce: number) => void;
  onProjectRefresh: (projectRoot?: string, fallbackProjectId?: string) => Promise<void>;
  openTarget: OpenPathTarget;
  projectLoading: boolean;
  t: Translator;
};

type BuildTab = "items" | "history";
export type BuildLifecycleActionName = "start" | "status" | "interrupt";
export type BuildLifecycleConfirmationState = {
  action: Exclude<BuildLifecycleActionName, "status">;
  panel: FrontendApiActionPanelState;
  target: BuildTarget | null;
  targetKey: string;
  values: FrontendApiSubmittedValues;
  valuesKey: string;
};
type BuildActionErrorKind = "start" | "status" | "refresh" | "openOutput" | "runGame" | "interrupt" | "diagnostics" | "configRead" | "configWrite";
type ProjectActionError = {
  detail: string;
  token: number;
};
type BuildDiagnosticsResult = {
  diagnostics: Array<Record<string, unknown>>;
  generation: number;
  projectRoot: string;
  strictMetadata: boolean;
};
type BuildDiagnosticsFailure = {
  error: unknown;
  generation: number;
  strictMetadata: boolean;
};
type Hoi4LaunchReadinessLoadState = {
  error?: unknown;
  payload?: Hoi4LaunchReadinessPayload;
  projectRoot: string;
  status: "failed" | "loaded" | "loading" | "unavailable";
};
type BuildDiagnosticItem = {
  code: string;
  key: string;
  message: string;
  path: string;
  severity: string;
  target: string;
};

const MAX_BLOCKING_DIAGNOSTICS = 3;
const BUILD_LIFECYCLE_ACTION_OPERATION_IDS = {
  interrupt: "build.interrupt",
  start: "build.start",
  status: "build.status"
} as const satisfies Record<BuildLifecycleActionName, ParaDevFrontendApiOperationId>;
const BUILD_START_ACTION_CONTRACT = buildLifecycleActionContract("start");
const BUILD_STATUS_ACTION_CONTRACT = buildLifecycleActionContract("status");
const BUILD_INTERRUPT_ACTION_CONTRACT = buildLifecycleActionContract("interrupt");

export type BuildLifecycleActionContract = {
  readonly operationId: ParaDevFrontendApiOperationId;
  readonly summary: string;
  readonly sdkCall: string;
  readonly restMethod: string;
  readonly restPath: string;
  readonly payload: string;
  readonly confirmationDefaultConfirmed: boolean;
  readonly confirmationRequired: boolean;
  readonly confirmationScope: string;
  readonly confirmationStyle: string;
  readonly confirmationTitle: string;
};

export function BuildPage({ activeProject, aiOperationIntent = null, browser, buildDiagnosticsGeneration = 0, buildDiagnosticsRefreshSource = "live", buildLifecycle, buildTargetIntent = null, onBuildTargetIntentConsumed, onProjectRefresh, openTarget, projectLoading, t }: BuildPageProps) {
  const desktopBackend = hasDesktopBackend();
  const [settings, setSettings] = useState(() => readBuildPageSettings());
  const [activeTab, setActiveTab] = useState<BuildTab>("items");
  const [expandedHistoryIds, setExpandedHistoryIds] = useState<Set<string>>(() => new Set());
  const [pendingActionByProjectRoot, setPendingActionByProjectRoot] = useState<Record<string, number>>({});
  const [actionErrorByProjectRoot, setActionErrorByProjectRoot] = useState<Record<string, ProjectActionError>>({});
  const [lifecycleConfirmation, setLifecycleConfirmation] = useState<BuildLifecycleConfirmationState | null>(null);
  const [buildDiagnosticsResult, setBuildDiagnosticsResult] = useState<BuildDiagnosticsResult | null>(null);
  const [buildDiagnosticsErrorByProjectRoot, setBuildDiagnosticsErrorByProjectRoot] = useState<Record<string, BuildDiagnosticsFailure>>({});
  const [launchModeReady, setLaunchModeReady] = useState(() => !desktopBackend);
  const [launchGameRoot, setLaunchGameRoot] = useState("");
  const [launchReadinessRefreshGeneration, setLaunchReadinessRefreshGeneration] = useState(0);
  const [launchReadinessState, setLaunchReadinessState] = useState<Hoi4LaunchReadinessLoadState>(() => ({
    projectRoot: activeProject.path,
    status: desktopBackend ? "loading" : "unavailable"
  }));
  const [nowMs, setNowMs] = useState(() => Date.now());
  const activeProjectPathRef = useRef(activeProject.path);
  const consumedBuildTargetIntentNonceRef = useRef(0);
  const confirmationRequestTokenRef = useRef(0);
  const latestActionTokenByScopeRef = useRef(new Map<string, number>());
  const actionScopeByTokenRef = useRef(new Map<number, string>());
  const nextActionTokenRef = useRef(0);
  activeProjectPathRef.current = activeProject.path;
  const actionPending = pendingActionByProjectRoot[activeProject.path] !== undefined;
  const buildDiagnosticsFailure = buildDiagnosticsErrorByProjectRoot[activeProject.path];
  const buildDiagnosticsError =
    buildDiagnosticsFailure?.generation === buildDiagnosticsGeneration &&
    buildDiagnosticsFailure.strictMetadata === settings.strictMetadata &&
    launchModeReady &&
    !projectLoading
      ? buildDiagnosticsFailure.error
      : undefined;
  const actionError = actionErrorByProjectRoot[activeProject.path]?.detail ?? (
    buildDiagnosticsError !== undefined ? buildActionErrorDetail(t, "diagnostics", buildDiagnosticsError) : null
  );
  const history = buildLifecycle.history;
  const projectRunRecords = useMemo(
    () => effectiveBuildRuns(buildRunsForProject(buildLifecycle.runs, activeProject.path)),
    [activeProject.path, buildLifecycle.runs]
  );
  const outputOpenPath = useMemo(() => buildOutputOpenPath(activeProject), [activeProject]);
  const buildModeOptions = useMemo(
    () => [
      { label: t("build.mode.cached"), value: "cached" },
      { label: t("build.mode.full"), value: "full" }
    ],
    [t]
  );
  const launchModeOptions = useMemo(
    () => BUILD_HOI4_LAUNCH_MODE_VALUES.map((value) => ({ label: buildLaunchModeOptionLabel(t, value), value })),
    [t]
  );
  const runtimeRecords = projectRunRecords;
  const fullRun = runtimeRecords.find((run) => !run.target);
  const runningRuns = useMemo(() => runtimeRecords.filter((run) => run.state === "running"), [runtimeRecords]);
  const fullInterruptRun = fullRun?.state === "running" ? fullRun : undefined;
  const runningRunIdentitiesKey = useMemo(
    () =>
      runningRuns
        .map((run) => `${run.runId ?? "<pending>"}\u0000${buildTargetKey(run.target)}`)
        .sort()
        .join("\n"),
    [runningRuns]
  );
  const runningPartialRuns = useMemo(
    () => runningRuns.filter((run) => run.target),
    [runningRuns]
  );
  const runningPartialCount = runningPartialRuns.length;
  const hasRunningBuilds = runningRuns.length > 0;
  const hasFullRunningBuild = runningRuns.some((run) => !run.target);
  const activeLaunchReadiness =
    launchReadinessState.projectRoot === activeProject.path ? launchReadinessState : undefined;
  const launchReady =
    activeLaunchReadiness?.status === "loaded" && activeLaunchReadiness.payload?.ready === true;
  const terminalBuildRefreshKey = useMemo(
    () =>
      runtimeRecords
        .filter((run) => run.state === "completed" || run.state === "failed" || run.state === "interrupted")
        .map((run) => `${run.runId ?? ""}:${run.state}:${run.terminalSequence ?? run.finishedAtMs ?? ""}`)
        .sort()
        .join("\n"),
    [runtimeRecords]
  );
  const recoveryReady = buildLifecycle.recoveryState === "ready";
  const buildControlsPending = actionPending || !recoveryReady;
  const overviewRuntime = useMemo(() => buildOverviewRuntime(runtimeRecords, settings.buildMode), [runtimeRecords, settings.buildMode]);
  const hasAdverseBuildState = overviewRuntime.state === "failed" || overviewRuntime.state === "interrupted";
  const buildDiagnostics =
    buildDiagnosticsResult?.projectRoot === activeProject.path &&
    buildDiagnosticsResult.generation === buildDiagnosticsGeneration &&
    buildDiagnosticsResult.strictMetadata === settings.strictMetadata &&
    launchModeReady &&
    !projectLoading
      ? buildDiagnosticsResult.diagnostics
      : null;
  const model = useMemo(
    () =>
      buildBuildDashboardModel({
        browser,
        buildDiagnostics,
        history,
        mode: settings.buildMode,
        project: activeProject,
        runtime: overviewRuntime,
        runtimes: runtimeRecords.length > 0 ? runtimeRecords : [overviewRuntime]
      }),
    [activeProject, browser, buildDiagnostics, history, overviewRuntime, runtimeRecords, settings.buildMode]
  );
  const blockingDiagnostics = useMemo(() => buildBlockingDiagnosticItems(buildDiagnostics ?? browser?.diagnostics ?? []), [browser, buildDiagnostics]);
  const projectHistory = useMemo(
    () => buildHistoryForProject(history, activeProject.path),
    [activeProject.path, history]
  );
  const estimateLabel = model.estimate.durationMs === null ? "" : formatBuildDurationText(t, model.estimate.durationMs);
  const timeText = useMemo(
    () => buildTimeText(t, estimateLabel, fullRun, projectHistory, nowMs, runningRuns),
    [estimateLabel, fullRun, nowMs, projectHistory, runningRuns, t]
  );
  const globalRecoveryError = buildLifecycle.recoveryState === "failed" ? buildLifecycle.globalError : null;
  const lifecycleError = globalRecoveryError ??
    buildLifecycle.errorsByProjectRoot[activeProject.path] ??
    buildLifecycle.globalError;
  const lifecycleErrorDetail = lifecycleError
    ? buildActionErrorDetail(t, lifecycleError.kind, new Error(lifecycleError.message))
    : null;
  const visibleActionError = globalRecoveryError ? lifecycleErrorDetail : actionError ?? lifecycleErrorDetail;
  const launchReadinessNote = !desktopBackend
    ? null
    : !activeLaunchReadiness || activeLaunchReadiness.status === "loading"
      ? t("build.launch.readinessChecking")
      : activeLaunchReadiness.status === "failed"
        ? t("build.launch.readinessFailed", {
            message: localizeDesktopBridgeError(t, buildErrorMessage(activeLaunchReadiness.error))
          })
        : activeLaunchReadiness.payload?.ready
          ? null
          : activeLaunchReadiness.payload
            ? buildLaunchReadinessDetail(t, activeLaunchReadiness.payload)
            : t("build.launch.requiresWholeProject");
  const latestPartialTargetLabel = model.latestPartialResult
    ? buildPartialResultTargetLabel(t, model.latestPartialResult, model.entities)
    : "";

  const issueActionToken = (projectRoot: string, operation: BuildActionErrorKind) => {
    const token = nextActionTokenRef.current + 1;
    nextActionTokenRef.current = token;
    const scope = `${projectRoot}\u0000${operation}`;
    const previousToken = latestActionTokenByScopeRef.current.get(scope);
    if (previousToken !== undefined) {
      actionScopeByTokenRef.current.delete(previousToken);
    }
    latestActionTokenByScopeRef.current.set(scope, token);
    actionScopeByTokenRef.current.set(token, scope);
    return token;
  };

  const clearProjectActionError = (projectRoot: string, token?: number) => {
    setActionErrorByProjectRoot((current) => {
      if (!(projectRoot in current) || (token !== undefined && current[projectRoot]?.token !== token)) {
        return current;
      }
      return removeProjectStateKey(current, projectRoot);
    });
  };

  const recordProjectActionError = (projectRoot: string, token: number, detail: string) => {
    const scope = actionScopeByTokenRef.current.get(token);
    if (!scope || latestActionTokenByScopeRef.current.get(scope) !== token) {
      return;
    }
    setActionErrorByProjectRoot((current) => {
      if ((current[projectRoot]?.token ?? -1) > token) {
        return current;
      }
      return { ...current, [projectRoot]: { detail, token } };
    });
  };

  const beginPendingAction = (projectRoot: string, operation: BuildActionErrorKind) => {
    const token = issueActionToken(projectRoot, operation);
    clearProjectActionError(projectRoot);
    setPendingActionByProjectRoot((current) => ({ ...current, [projectRoot]: token }));
    return token;
  };

  const finishPendingAction = (projectRoot: string, token: number) => {
    setPendingActionByProjectRoot((current) =>
      current[projectRoot] === token ? removeProjectStateKey(current, projectRoot) : current
    );
  };

  useEffect(() => {
    writeBuildPageSettings(settings);
  }, [settings]);

  useEffect(() => {
    if (aiOperationIntent) {
      setActiveTab("items");
    }
  }, [aiOperationIntent?.nonce]);

  useEffect(() => {
    confirmationRequestTokenRef.current += 1;
    setLifecycleConfirmation(null);
  }, [activeProject.path, settings.buildMode, settings.parallelism, settings.strictMetadata]);

  useEffect(() => {
    setLifecycleConfirmation((current) => {
      if (!current || buildLifecycleConfirmationMatchesRunningState(current, runningRuns)) {
        return current;
      }
      confirmationRequestTokenRef.current += 1;
      return null;
    });
  }, [runningRunIdentitiesKey]);

  useEffect(() => {
    const projectRoot = activeProject.path;
    if (!desktopBackend) {
      setLaunchReadinessState({ projectRoot, status: "unavailable" });
      return;
    }
    let cancelled = false;
    setLaunchReadinessState({ projectRoot, status: "loading" });
    loadHoi4LaunchReadiness(projectRoot)
      .then((payload) => {
        if (!cancelled) {
          setLaunchReadinessState({ payload, projectRoot, status: "loaded" });
        }
      })
      .catch((error: unknown) => {
        if (!cancelled) {
          setLaunchReadinessState({ error, projectRoot, status: "failed" });
        }
      });
    return () => {
      cancelled = true;
    };
  }, [
    activeProject.path,
    desktopBackend,
    launchReadinessRefreshGeneration,
    terminalBuildRefreshKey
  ]);

  useEffect(() => {
    const projectRoot = activeProject.path;
    const clearBuildDiagnosticsError = () => {
      setBuildDiagnosticsErrorByProjectRoot((current) => removeProjectStateKey(current, projectRoot));
    };
    if (!desktopBackend) {
      setBuildDiagnosticsResult(null);
      clearBuildDiagnosticsError();
      return;
    }
    if (!launchModeReady || projectLoading) {
      setBuildDiagnosticsResult(null);
      clearBuildDiagnosticsError();
      return;
    }
    let cancelled = false;
    setBuildDiagnosticsResult(null);
    clearBuildDiagnosticsError();
    loadCachedBuildDiagnostics({
      generation: buildDiagnosticsGeneration,
      projectRoot,
      strictMetadata: settings.strictMetadata,
      load: async () => {
        const payload = await loadProjectInspection({
          projectRoot,
          kind: "diagnostics",
          filters:
            buildDiagnosticsRefreshSource === "published"
              ? { published: true }
              : { strictMetadata: settings.strictMetadata }
        });
        if (!Array.isArray(payload.diagnostics)) {
          throw new Error("Project diagnostics response must contain a diagnostics array.");
        }
        return payload.diagnostics;
      }
    })
      .then((diagnostics) => {
        if (!cancelled) {
          setBuildDiagnosticsResult({
            diagnostics,
            generation: buildDiagnosticsGeneration,
            projectRoot,
            strictMetadata: settings.strictMetadata
          });
          clearBuildDiagnosticsError();
        }
      })
      .catch((error: unknown) => {
        if (!cancelled) {
          setBuildDiagnosticsResult(null);
          setBuildDiagnosticsErrorByProjectRoot((current) => ({
            ...current,
            [projectRoot]: {
              error,
              generation: buildDiagnosticsGeneration,
              strictMetadata: settings.strictMetadata
            }
          }));
        }
      });
    return () => {
      cancelled = true;
    };
  }, [activeProject.path, buildDiagnosticsGeneration, buildDiagnosticsRefreshSource, desktopBackend, launchModeReady, projectLoading, settings.strictMetadata]);

  useEffect(() => {
    if (!desktopBackend) {
      setLaunchModeReady(true);
      return;
    }
    const projectRoot = activeProjectPathRef.current;
    const actionToken = issueActionToken(projectRoot, "configRead");
    setLaunchModeReady(false);
    let cancelled = false;
    Promise.all([
      readConfigValue(DESKTOP_CONFIG_KEYS.hoi4LaunchMode),
      readConfigValue(DESKTOP_CONFIG_KEYS.hoi4GameRoot),
      readConfigValue(DESKTOP_CONFIG_KEYS.buildStrictMetadata),
      readConfigValue(DESKTOP_CONFIG_KEYS.buildParallelism)
    ])
      .then(([launchMode, gameRoot, strictMetadata, parallelism]) => {
        if (cancelled) {
          return;
        }
        setSettings((current) => ({
          ...current,
          launchMode: hoi4LaunchModeFromConfig(launchMode, current.launchMode),
          parallelism: buildParallelismFromConfig(parallelism, current.parallelism),
          strictMetadata: strictMetadataFromConfig(strictMetadata, current.strictMetadata)
        }));
        setLaunchGameRoot((current) => hoi4GameRootFromConfig(gameRoot, current));
      })
      .catch((error: unknown) => {
        if (!cancelled) {
          recordProjectActionError(projectRoot, actionToken, buildActionErrorDetail(t, "configRead", error));
        }
      })
      .finally(() => {
        if (!cancelled) {
          setLaunchModeReady(true);
        }
      });
    return () => {
      cancelled = true;
    };
  }, [desktopBackend]);

  useEffect(() => {
    if (!hasRunningBuilds) {
      return;
    }
    setNowMs(Date.now());
    const timer = window.setInterval(() => setNowMs(Date.now()), 1000);
    return () => window.clearInterval(timer);
  }, [hasRunningBuilds, runningRunIdentitiesKey]);

  const setBuildMode = (buildMode: BuildMode) => {
    setSettings((current) => ({ ...current, buildMode }));
  };

  const setStrictMetadata = (strictMetadata: boolean) => {
    setSettings((current) => ({ ...current, strictMetadata }));
    if (desktopBackend) {
      const projectRoot = activeProject.path;
      const actionToken = issueActionToken(projectRoot, "configWrite");
      writeConfigValue(DESKTOP_CONFIG_KEYS.buildStrictMetadata, strictMetadata).catch((error: unknown) => {
        recordProjectActionError(projectRoot, actionToken, buildActionErrorDetail(t, "configWrite", error));
      });
    }
  };

  const setBuildParallelism = (parallelism: number) => {
    const cleanParallelism = buildParallelismFromConfig(parallelism, settings.parallelism);
    setSettings((current) => ({ ...current, parallelism: cleanParallelism }));
    if (desktopBackend) {
      const projectRoot = activeProject.path;
      const actionToken = issueActionToken(projectRoot, "configWrite");
      writeConfigValue(DESKTOP_CONFIG_KEYS.buildParallelism, cleanParallelism).catch((error: unknown) => {
        recordProjectActionError(projectRoot, actionToken, buildActionErrorDetail(t, "configWrite", error));
      });
    }
  };

  const setLaunchMode = (launchMode: Hoi4LaunchMode) => {
    setSettings((current) => ({ ...current, launchMode }));
    if (desktopBackend) {
      const projectRoot = activeProject.path;
      const actionToken = issueActionToken(projectRoot, "configWrite");
      writeConfigValue(DESKTOP_CONFIG_KEYS.hoi4LaunchMode, launchMode).catch((error: unknown) => {
        recordProjectActionError(projectRoot, actionToken, buildActionErrorDetail(t, "configWrite", error));
      });
    }
  };

  const openLifecycleConfirmation = (
    action: Exclude<BuildLifecycleActionName, "status">,
    target: BuildTarget | null = null,
    selectedInterruptRun?: BuildRunRecord
  ) => {
    const projectRoot = activeProject.path;
    const requestToken = confirmationRequestTokenRef.current + 1;
    confirmationRequestTokenRef.current = requestToken;
    const actionToken = issueActionToken(projectRoot, action);
    const activeInterruptRun = action === "interrupt" ? selectedInterruptRun : undefined;
    if (action === "interrupt" && (!activeInterruptRun || activeInterruptRun.state !== "running")) {
      return;
    }
    const values = buildLifecycleSubmittedValuesForBuildPage({
      action,
      mode: activeInterruptRun?.mode ?? (target ? "cached" : settings.buildMode),
      parallelism: settings.parallelism,
      project: activeProject,
      runId: activeInterruptRun?.runId ?? null,
      strictMetadata: settings.strictMetadata,
      target
    });
    createBuildLifecycleConfirmationState(action, target, values, false)
      .then((state) => {
        if (confirmationRequestTokenRef.current === requestToken && activeProjectPathRef.current === projectRoot) {
          setLifecycleConfirmation(state);
        }
      })
      .catch((error: unknown) => {
        if (confirmationRequestTokenRef.current === requestToken) {
          recordProjectActionError(projectRoot, actionToken, buildActionErrorDetail(t, action, error));
        }
      });
  };

  const canRequestStart = (target: BuildTarget | null): boolean => {
    if (!launchModeReady || projectLoading || model.summary.blocked || buildControlsPending) {
      return false;
    }
    if (!target) {
      return !hasRunningBuilds;
    }
    const resolvedTarget = resolveBuildTargetForBrowser(browser, target);
    if (!resolvedTarget) {
      return false;
    }
    return !hasFullRunningBuild && !runningRuns.some((run) => sameBuildTarget(run.target, resolvedTarget));
  };

  const handleStart = (target: BuildTarget | null = null): boolean => {
    const resolvedTarget = target ? resolveBuildTargetForBrowser(browser, target) : null;
    if (target && !resolvedTarget) {
      return false;
    }
    const key = buildTargetKey(resolvedTarget);
    const mode: BuildMode = resolvedTarget ? "cached" : settings.buildMode;
    if (!desktopBackend || !canRequestStart(resolvedTarget)) {
      return false;
    }
    const values = buildLifecycleSubmittedValuesForBuildPage({
      action: "start",
      mode,
      parallelism: settings.parallelism,
      project: activeProject,
      strictMetadata: settings.strictMetadata,
      target: resolvedTarget
    });
    const valuesKey = buildLifecycleConfirmationValuesKey("start", resolvedTarget, values);
    if (!isBuildLifecyclePanelConfirmed(lifecycleConfirmation, "start", key, valuesKey)) {
      openLifecycleConfirmation("start", resolvedTarget);
      return true;
    }
    const projectRoot = activeProject.path;
    const actionToken = beginPendingAction(projectRoot, "start");
    setLifecycleConfirmation(null);
    buildLifecycle
      .start(buildStartRequestForBuildPage(activeProject, mode, resolvedTarget, settings.strictMetadata, settings.parallelism), activeProject)
      .then(() => clearProjectActionError(projectRoot, actionToken))
      .catch((error: unknown) =>
        recordProjectActionError(projectRoot, actionToken, buildActionErrorDetail(t, "start", error))
      )
      .finally(() => finishPendingAction(projectRoot, actionToken));
    return true;
  };

  useEffect(() => {
    if (
      !buildTargetIntent ||
      !desktopBackend ||
      buildTargetIntent.projectRoot !== activeProject.path ||
      consumedBuildTargetIntentNonceRef.current === buildTargetIntent.nonce ||
      !canRequestStart(buildTargetIntent.target)
    ) {
      return;
    }
    setActiveTab("items");
    if (!handleStart(buildTargetIntent.target)) {
      return;
    }
    consumedBuildTargetIntentNonceRef.current = buildTargetIntent.nonce;
    onBuildTargetIntentConsumed?.(buildTargetIntent.nonce);
  }, [activeProject.path, browser, buildControlsPending, buildTargetIntent, desktopBackend, hasFullRunningBuild, hasRunningBuilds, launchModeReady, model.summary.blocked, onBuildTargetIntentConsumed, projectLoading, runningRuns]);

  const handleRefresh = () => {
    const projectRoot = activeProject.path;
    const actionToken = issueActionToken(projectRoot, "refresh");
    clearProjectActionError(projectRoot);
    buildLifecycle.retryRecovery();
    setLaunchReadinessRefreshGeneration((current) => current + 1);
    onProjectRefresh(projectRoot, activeProject.id)
      .then(() => {
        clearProjectActionError(projectRoot, actionToken);
        buildLifecycle.clearError(projectRoot, "refresh");
      })
      .catch((error: unknown) =>
        recordProjectActionError(projectRoot, actionToken, buildActionErrorDetail(t, "refresh", error))
      );
  };

  const handleOpenOutput = () => {
    if (!desktopBackend) {
      return;
    }
    const projectRoot = activeProject.path;
    const actionToken = beginPendingAction(projectRoot, "openOutput");
    openProjectPath(outputOpenPath, openTarget)
      .then(() => clearProjectActionError(projectRoot, actionToken))
      .catch((error: unknown) =>
        recordProjectActionError(projectRoot, actionToken, buildActionErrorDetail(t, "openOutput", error))
      )
      .finally(() => finishPendingAction(projectRoot, actionToken));
  };

  const handleRunGame = () => {
    if (buildRunGameDisabled({
      actionPending: buildControlsPending,
      buildBlocked: model.summary.blocked,
      desktopBackend,
      hasAdverseBuildState,
      hasRunningBuilds,
      launchReady,
      launchModeReady
    })) {
      return;
    }
    const projectRoot = activeProject.path;
    const actionToken = beginPendingAction(projectRoot, "runGame");
    runHoi4Game({ projectRoot: activeProject.path, mode: settings.launchMode, gameRoot: launchGameRoot || undefined })
      .then(() => clearProjectActionError(projectRoot, actionToken))
      .catch((error: unknown) =>
        recordProjectActionError(projectRoot, actionToken, buildActionErrorDetail(t, "runGame", error))
      )
      .finally(() => finishPendingAction(projectRoot, actionToken));
  };

  const handleInterrupt = (requestedRun: BuildRunRecord): boolean => {
    const interruptingRun = runningRuns.find((run) => run.runId === requestedRun.runId);
    if (!desktopBackend || !interruptingRun?.runId) {
      return false;
    }
    const target = interruptingRun.target ?? null;
    const values = buildLifecycleSubmittedValuesForBuildPage({
      action: "interrupt",
      mode: interruptingRun.mode,
      parallelism: settings.parallelism,
      project: activeProject,
      runId: interruptingRun.runId,
      strictMetadata: settings.strictMetadata,
      target
    });
    const targetKey = buildTargetKey(target);
    const valuesKey = buildLifecycleConfirmationValuesKey("interrupt", target, values);
    if (!isBuildLifecyclePanelConfirmed(lifecycleConfirmation, "interrupt", targetKey, valuesKey)) {
      openLifecycleConfirmation("interrupt", target, interruptingRun);
      return true;
    }
    const projectRoot = activeProject.path;
    const actionToken = beginPendingAction(projectRoot, "interrupt");
    setLifecycleConfirmation(null);
    buildLifecycle
      .interrupt(interruptingRun.runId)
      .then(() => clearProjectActionError(projectRoot, actionToken))
      .catch((error: unknown) =>
        recordProjectActionError(projectRoot, actionToken, buildActionErrorDetail(t, "interrupt", error))
      )
      .finally(() => finishPendingAction(projectRoot, actionToken));
    return true;
  };

  const toggleHistory = (id: string) => {
    setExpandedHistoryIds((current) => {
      const next = new Set(current);
      if (next.has(id)) {
        next.delete(id);
      } else {
        next.add(id);
      }
      return next;
    });
  };

  const handleRemoveHistory = (id: string) => {
    setExpandedHistoryIds((current) => {
      const next = new Set(current);
      next.delete(id);
      return next;
    });
    buildLifecycle.removeHistory(id);
  };

  const setLifecycleConfirmationAccepted = (accepted: boolean) => {
    if (!lifecycleConfirmation) {
      return;
    }
    const current = lifecycleConfirmation;
    const activeInterruptRun =
      current.action === "interrupt"
        ? runningRuns.find((run) => run.runId === current.values.run_id)
        : undefined;
    if (
      current.action === "interrupt" &&
      (!activeInterruptRun || !sameBuildTarget(activeInterruptRun.target, current.target))
    ) {
      setLifecycleConfirmation(null);
      return;
    }
    const expectedValues = buildLifecycleSubmittedValuesForBuildPage({
      action: current.action,
      mode: activeInterruptRun?.mode ?? (current.target ? "cached" : settings.buildMode),
      parallelism: settings.parallelism,
      project: activeProject,
      runId: activeInterruptRun?.runId ?? null,
      strictMetadata: settings.strictMetadata,
      target: current.target
    });
    const expectedValuesKey = buildLifecycleConfirmationValuesKey(current.action, current.target, expectedValues);
    if (current.valuesKey !== expectedValuesKey) {
      setLifecycleConfirmation(null);
      return;
    }
    const projectRoot = activeProject.path;
    const requestToken = confirmationRequestTokenRef.current + 1;
    confirmationRequestTokenRef.current = requestToken;
    const actionToken = issueActionToken(projectRoot, current.action);
    createBuildLifecycleConfirmationState(current.action, current.target, current.values, accepted)
      .then((state) => {
        if (confirmationRequestTokenRef.current !== requestToken || activeProjectPathRef.current !== projectRoot) {
          return;
        }
        setLifecycleConfirmation((latest) =>
          latest?.action === current.action && latest.valuesKey === current.valuesKey && latest.targetKey === current.targetKey
            ? state
            : latest
        );
      })
      .catch((error: unknown) => {
        if (confirmationRequestTokenRef.current === requestToken) {
          recordProjectActionError(projectRoot, actionToken, buildActionErrorDetail(t, current.action, error));
        }
      });
  };

  const confirmLifecycleAction = () => {
    if (!lifecycleConfirmation || lifecycleConfirmation.panel.run_state.disabled) {
      return;
    }
    if (lifecycleConfirmation.action === "start") {
      handleStart(lifecycleConfirmation.target);
      return;
    }
    const run = runningRuns.find((candidate) => candidate.runId === lifecycleConfirmation.values.run_id);
    if (!run) {
      setLifecycleConfirmation(null);
      return;
    }
    handleInterrupt(run);
  };

  return (
    <section className="build-page" aria-label={t("build.aria")}>
      <header className="build-page-header">
        <div>
          <p className="label">{t("build.header.label")}</p>
          <h2>{t("build.header.title")}</h2>
          <p>
            <strong>{activeProject.name}</strong>
            <span>{activeProject.path}</span>
          </p>
        </div>
        <div className="build-header-actions">
          <LabeledSelect
            detail={buildModeDetail(t, settings.buildMode)}
            label={t("build.mode.label")}
            onChange={(value) => setBuildMode(value as BuildMode)}
            options={buildModeOptions}
            title={t("build.mode.aria")}
            value={settings.buildMode}
          />
          <LabeledSelect
            configKey={DESKTOP_CONFIG_KEYS.hoi4LaunchMode}
            detail={buildLaunchModeDetail(t, settings.launchMode, launchGameRoot)}
            label={t("build.launchMode.label")}
            onChange={(value) => setLaunchMode(value as Hoi4LaunchMode)}
            options={launchModeOptions}
            title={t("build.launchMode.aria")}
            value={settings.launchMode}
          />
          <label className="build-number-group" title={t("build.parallelism.aria")}>
            <span>{t("build.parallelism.label")}</span>
            <input
              aria-label={t("build.parallelism.aria")}
              data-paradev-config-key={DESKTOP_CONFIG_KEYS.buildParallelism}
              min={BUILD_PARALLELISM_MIN}
              onChange={(event) => setBuildParallelism(Number(event.target.value))}
              type="number"
              value={settings.parallelism}
            />
          </label>
          <label className="build-strict-metadata-toggle" data-paradev-build-strict-metadata="true" title={t("build.strictMetadata.aria")}>
            <input
              checked={settings.strictMetadata}
              data-paradev-config-key={DESKTOP_CONFIG_KEYS.buildStrictMetadata}
              onChange={(event) => setStrictMetadata(event.target.checked)}
              type="checkbox"
            />
            <span>{t("build.strictMetadata.label")}</span>
          </label>
          <button className="toolbar-button build-refresh-button" disabled={projectLoading || buildLifecycle.recoveryState === "loading"} onClick={handleRefresh} type="button">
            <RefreshCw aria-hidden="true" size={14} />
            {t("build.action.refresh")}
          </button>
        </div>
      </header>

      <BuildAiHandoff intent={aiOperationIntent} t={t} />

      <section
        className={`build-overview-card build-state-${model.status.state}`}
        aria-label={t("build.status.label")}
        data-paradev-status-operation-id={BUILD_STATUS_ACTION_CONTRACT.operationId}
        data-paradev-status-sdk-call={BUILD_STATUS_ACTION_CONTRACT.sdkCall}
        data-paradev-status-rest-method={BUILD_STATUS_ACTION_CONTRACT.restMethod}
        data-paradev-status-rest-path={BUILD_STATUS_ACTION_CONTRACT.restPath}
        data-paradev-status-payload={BUILD_STATUS_ACTION_CONTRACT.payload}
        data-paradev-status-confirmation-required={String(BUILD_STATUS_ACTION_CONTRACT.confirmationRequired)}
      >
        <div className="build-overview-status">
          <span className="panel-icon">
            <BuildStatusIcon label={buildStatusTitle(t, model.status.state, runningPartialCount)} state={model.status.state} />
          </span>
          <div>
            <p className="label">{t("build.status.label")}</p>
            <h3>{buildStatusTitle(t, model.status.state, runningPartialCount)}</h3>
          </div>
          <span className={statusPillClass(model.status.state)}>{statusPillLabel(t, model.status.state)}</span>
        </div>
        <BuildActionAlert detail={visibleActionError} t={t} />
        <BuildLatestPartialResult result={model.latestPartialResult} targetLabel={latestPartialTargetLabel} t={t} />
        <BuildActivePartialRuns
          actionPending={actionPending}
          confirmation={lifecycleConfirmation}
          nowMs={nowMs}
          onInterrupt={handleInterrupt}
          runs={runningPartialRuns}
          t={t}
        />
        <div className="build-overview-body">
          <div className="build-progress-main">
            <div className="build-progress-header">
              <span className="build-progress-title">
                <BuildStatusIcon label={buildStatusTitle(t, model.status.state, runningPartialCount)} state={model.status.state} />
                <span>{model.status.state === "running" ? buildProgressPhaseLabel(t, model.progress.phase, runningPartialCount) : buildStatusTitle(t, model.status.state, runningPartialCount)}</span>
              </span>
              <strong>{Math.round(model.status.progress)}%</strong>
            </div>
            <div
              className="build-progress-track"
              role="progressbar"
              aria-valuemin={0}
              aria-valuemax={100}
              aria-valuenow={Math.round(model.status.progress)}
              aria-label={t("build.progress.label")}
            >
              <span style={{ width: `${model.status.progress}%` }} />
            </div>
            {model.status.state === "running" ? (
              <p
                aria-atomic="true"
                aria-live="polite"
                className="build-progress-detail"
              >
                <span title={model.progress.detail}>{model.progress.detail}</span>
                {model.progress.countLabel ? <strong>{model.progress.countLabel}</strong> : null}
              </p>
            ) : model.status.state === "failed" ||
              model.status.state === "interrupted" ||
              model.status.state === "blocked" ? (
              <p
                aria-atomic="true"
                aria-live="assertive"
                className="build-progress-detail"
                role="alert"
              >
                <span title={model.status.detail}>{model.status.detail}</span>
              </p>
            ) : null}
            <div className="build-progress-meta">
              <span className="build-time-display">
                <Clock3 aria-hidden="true" size={13} />
                {timeText}
              </span>
            </div>
          </div>
          <div className="build-overview-actions">
            <button
              className="toolbar-button primary"
              data-paradev-confirmation-required={String(BUILD_START_ACTION_CONTRACT.confirmationRequired)}
              data-paradev-operation-id={BUILD_START_ACTION_CONTRACT.operationId}
              data-paradev-payload={BUILD_START_ACTION_CONTRACT.payload}
              data-paradev-rest-method={BUILD_START_ACTION_CONTRACT.restMethod}
              data-paradev-rest-path={BUILD_START_ACTION_CONTRACT.restPath}
              data-paradev-sdk-call={BUILD_START_ACTION_CONTRACT.sdkCall}
              disabled={!canRequestStart(null)}
              aria-describedby={lifecycleConfirmation?.action === "start" ? "build-lifecycle-confirmation" : undefined}
              onClick={() => handleStart()}
              type="button"
            >
              <Hammer aria-hidden="true" size={14} />
              {t("build.action.start")}
            </button>
            <button
              className="toolbar-button danger"
              data-paradev-confirmation-required={String(BUILD_INTERRUPT_ACTION_CONTRACT.confirmationRequired)}
              data-paradev-operation-id={BUILD_INTERRUPT_ACTION_CONTRACT.operationId}
              data-paradev-payload={BUILD_INTERRUPT_ACTION_CONTRACT.payload}
              data-paradev-rest-method={BUILD_INTERRUPT_ACTION_CONTRACT.restMethod}
              data-paradev-rest-path={BUILD_INTERRUPT_ACTION_CONTRACT.restPath}
              data-paradev-sdk-call={BUILD_INTERRUPT_ACTION_CONTRACT.sdkCall}
              disabled={actionPending || !fullInterruptRun?.runId}
              aria-describedby={
                lifecycleConfirmation?.action === "interrupt" &&
                lifecycleConfirmation.targetKey === BUILD_RUN_FULL_KEY
                  ? "build-lifecycle-confirmation"
                  : undefined
              }
              onClick={() => {
                if (fullInterruptRun) {
                  handleInterrupt(fullInterruptRun);
                }
              }}
              type="button"
            >
              <Square aria-hidden="true" size={13} />
              {t("build.action.interrupt")}
            </button>
            <button className="toolbar-button" disabled={actionPending} onClick={handleOpenOutput} title={outputOpenPath} type="button">
              <FolderOpen aria-hidden="true" size={14} />
              {t("build.action.open")}
            </button>
            <button
              className="toolbar-button success"
              disabled={buildRunGameDisabled({
                actionPending: buildControlsPending,
                buildBlocked: model.summary.blocked,
                desktopBackend,
                hasAdverseBuildState,
                hasRunningBuilds,
                launchReady,
                launchModeReady
              })}
              aria-describedby={
                !launchReady
                  ? "build-launch-whole-project-baseline"
                  : undefined
              }
              onClick={handleRunGame}
              type="button"
            >
              <Play aria-hidden="true" size={14} />
              {t("build.action.runGame")}
            </button>
          </div>
        </div>
        {launchReadinessNote ? (
          <p
            className="build-launch-baseline-note"
            data-paradev-launch-readiness-code={activeLaunchReadiness?.payload?.code}
            data-paradev-launch-readiness-status={activeLaunchReadiness?.status ?? "loading"}
            id="build-launch-whole-project-baseline"
          >
            {launchReadinessNote}
          </p>
        ) : null}
        {lifecycleConfirmation ? (
          <BuildLifecycleConfirmation
            busy={actionPending}
            confirmation={lifecycleConfirmation}
            onAcceptedChange={setLifecycleConfirmationAccepted}
            onCancel={() => setLifecycleConfirmation(null)}
            onConfirm={confirmLifecycleAction}
            t={t}
          />
        ) : null}
        <div className="build-overview-metrics">
          <Metric icon={<Box aria-hidden="true" size={16} />} label={t("build.metric.modules")} value={model.summary.moduleCount} />
          <Metric icon={<History aria-hidden="true" size={16} />} label={t("build.metric.collections")} value={model.summary.collectionCount} />
          <Metric icon={<TerminalSquare aria-hidden="true" size={16} />} label={t("build.metric.sources")} value={model.summary.sourceCount} />
          <Metric icon={<FileText aria-hidden="true" size={16} />} label={t("build.metric.diagnostics")} value={`${model.summary.errorCount}/${model.summary.diagnosticCount}`} />
        </div>
        <BuildBlockingDiagnostics diagnostics={blockingDiagnostics} total={model.summary.errorCount} t={t} />
      </section>

      <section className="build-panel build-tab-panel">
        <div className="build-tab-header" role="tablist" aria-label={t("build.tabs.aria")}>
          <button
            aria-controls="build-items-panel"
            aria-selected={activeTab === "items"}
            className={activeTab === "items" ? "active" : ""}
            id="build-items-tab"
            onClick={() => setActiveTab("items")}
            role="tab"
            type="button"
          >
            {t("build.tabs.items")}
          </button>
          <button
            aria-controls="build-history-panel"
            aria-selected={activeTab === "history"}
            className={activeTab === "history" ? "active" : ""}
            id="build-history-tab"
            onClick={() => setActiveTab("history")}
            role="tab"
            type="button"
          >
            {t("build.tabs.history")}
          </button>
        </div>
        {activeTab === "items" ? (
          <div aria-labelledby="build-items-tab" className="build-tab-body" id="build-items-panel" role="tabpanel">
            <div className="build-entity-list">
              {model.entities.map((entity) => {
                const entityTargetKey = buildTargetKey(entity.target);
                const runningEntityRun = runningRuns.find((run) => sameBuildTarget(run.target, entity.target));
                return (
                  <BuildEntity
                    action={
                      runningEntityRun
                        ? {
                            ariaLabel: t("build.action.interruptTarget", {
                              target: buildEntityTitle(t, entity)
                            }),
                            confirmationActive:
                              lifecycleConfirmation?.action === "interrupt" &&
                              lifecycleConfirmation.values.run_id === runningEntityRun.runId &&
                              sameBuildTarget(lifecycleConfirmation.target, entity.target),
                            disabled: actionPending,
                            kind: "interrupt",
                            label: t("build.action.interrupt"),
                            onClick: () => handleInterrupt(runningEntityRun),
                            runId: runningEntityRun.runId ?? undefined,
                            targetKey: entityTargetKey
                          }
                        : {
                            confirmationActive:
                              lifecycleConfirmation?.action === "start" &&
                              sameBuildTarget(lifecycleConfirmation.target, entity.target),
                            disabled: !canRequestStart(entity.target),
                            kind: "rebuild",
                            label: t("build.action.partialUpdate"),
                            onClick: () => handleStart(entity.target),
                            targetKey: entityTargetKey
                          }
                    }
                    entity={entity}
                    key={`${entity.kind}:${entity.id}`}
                    subtitle={buildEntitySubtitle(t, entity)}
                    sourceLabel={t("build.entity.sourceProgress", { current: entity.progressCurrent, total: entity.progressTotal })}
                    title={buildEntityTitle(t, entity)}
                  />
                );
              })}
            </div>
          </div>
        ) : (
          <div aria-labelledby="build-history-tab" className="build-tab-body" id="build-history-panel" role="tabpanel">
            <BuildHistoryList
              entries={projectHistory}
              expandedIds={expandedHistoryIds}
              onRemove={handleRemoveHistory}
              onToggle={toggleHistory}
              t={t}
            />
          </div>
        )}
      </section>
    </section>
  );
}

export function buildLifecycleActionContract(name: BuildLifecycleActionName): BuildLifecycleActionContract {
  const action = generatedBuildLifecycleAction(name);
  const confirmation = action.execution.confirmation;
  return {
    confirmationDefaultConfirmed: confirmation.default_confirmed,
    confirmationRequired: confirmation.required,
    confirmationScope: confirmation.scope,
    confirmationStyle: confirmation.style,
    confirmationTitle: confirmation.title,
    operationId: action.operation_id,
    payload: action.payload ?? "",
    restMethod: frontendApiBindingText(action.bindings?.rest?.method),
    restPath: frontendApiBindingText(action.bindings?.rest?.path),
    sdkCall: frontendApiBindingText(action.bindings?.sdk?.call),
    summary: action.summary
  };
}

export function buildHistoryForProject(
  history: readonly BuildHistoryEntry[],
  projectRoot: string
): BuildHistoryEntry[] {
  return history.filter((entry) => entry.projectRoot === projectRoot).slice().sort(compareHistoryDesc);
}

function generatedBuildLifecycleAction(name: BuildLifecycleActionName): FrontendApiAction {
  const operationId = BUILD_LIFECYCLE_ACTION_OPERATION_IDS[name];
  const action = (PARADEV_FRONTEND_API_CONTRACT.workspace.sections as readonly { actions: readonly FrontendApiAction[] }[])
    .flatMap((section) => section.actions)
    .find((candidate) => candidate.operation_id === operationId);
  if (!action) {
    throw new Error(`Generated frontend API is missing build lifecycle action: ${operationId}.`);
  }
  return action;
}

function frontendApiBindingText(value: unknown): string {
  return typeof value === "string" ? value : "";
}

export async function createBuildLifecycleConfirmationState(
  action: Exclude<BuildLifecycleActionName, "status">,
  target: BuildTarget | null,
  values: FrontendApiSubmittedValues,
  accepted: boolean
): Promise<BuildLifecycleConfirmationState> {
  const { getFrontendApiActionPanelState } = await import("../data/frontendApi");
  const contract = buildLifecycleActionContract(action);
  const confirmationStates = accepted ? { [contract.operationId]: true } : {};
  const panel = getFrontendApiActionPanelState({
    operationId: contract.operationId,
    values,
    restPlanResult: buildLifecycleRestPlanResult(contract, values),
    confirmationStates
  });
  const targetKey = buildTargetKey(target);
  return {
    action,
    panel,
    target,
    targetKey,
    values,
    valuesKey: buildLifecycleConfirmationValuesKey(action, target, values)
  };
}

export function buildLifecycleConfirmationValuesKey(
  action: Exclude<BuildLifecycleActionName, "status">,
  target: BuildTarget | null,
  values: FrontendApiSubmittedValues
): string {
  return JSON.stringify({
    operation_id: buildLifecycleActionContract(action).operationId,
    target_key: buildTargetKey(target),
    values
  });
}

export function buildLifecycleSubmittedValuesForBuildPage({
  action,
  mode,
  parallelism,
  project,
  runId,
  strictMetadata,
  target
}: {
  action: Exclude<BuildLifecycleActionName, "status">;
  mode: BuildMode;
  parallelism: number;
  project: ProjectOption;
  runId?: string | null;
  strictMetadata: boolean;
  target: BuildTarget | null;
}): FrontendApiSubmittedValues {
  if (action === "interrupt") {
    return compactBuildLifecycleValues({
      run_id: runId
    });
  }
  return compactBuildLifecycleValues({
    project_root: project.path,
    mode,
    profile: project.game || "hoi4",
    strict_metadata: strictMetadata,
    parallelism,
    target
  });
}

export function buildLifecycleRestPlanResult(
  contract: BuildLifecycleActionContract,
  values: FrontendApiSubmittedValues
): FrontendApiRestPlanResult {
  const body = contract.restMethod === "GET" ? {} : values;
  const query = contract.restMethod === "GET" ? values : {};
  return {
    status: "ready",
    payload: {
      schema: "paradev.sdk.frontend-api.rest-request.v1",
      operation_id: contract.operationId,
      method: contract.restMethod,
      path: contract.restPath,
      query,
      body,
      binding: {
        method: contract.restMethod,
        path: contract.restPath,
        query: {}
      },
      normalized: {
        schema: "paradev.sdk.frontend-api.inputs.v1",
        operation_id: contract.operationId,
        values,
        project: {},
        parameters: body,
        selectors: {},
        projections: {}
      }
    }
  };
}

export function isBuildLifecyclePanelConfirmed(
  confirmation: BuildLifecycleConfirmationState | null,
  action: Exclude<BuildLifecycleActionName, "status">,
  targetKey: string,
  valuesKey: string
): boolean {
  return (
    confirmation?.action === action &&
    confirmation.targetKey === targetKey &&
    confirmation.valuesKey === valuesKey &&
    confirmation.panel.confirmation_satisfied === true &&
    confirmation.panel.run_state.disabled === false
  );
}

function compactBuildLifecycleValues(values: Record<string, unknown>): FrontendApiSubmittedValues {
  return Object.fromEntries(Object.entries(values).filter(([, value]) => value !== undefined && value !== null && value !== ""));
}

function buildLifecycleConfirmationMatchesRunningState(
  confirmation: BuildLifecycleConfirmationState,
  runningRuns: readonly BuildRunRecord[]
): boolean {
  if (confirmation.action === "interrupt") {
    const runId = confirmation.values.run_id;
    return (
      typeof runId === "string" &&
      runningRuns.some(
        (run) =>
          run.runId === runId &&
          sameBuildTarget(run.target, confirmation.target)
      )
    );
  }
  if (!confirmation.target) {
    return runningRuns.length === 0;
  }
  return !runningRuns.some(
    (run) =>
      !run.target ||
      sameBuildTarget(run.target, confirmation.target)
  );
}

function aiOperationIntentSourceSummary(intent: AiOperationIntent, t: Translator): string {
  if (intent.sources.length === 0) {
    return t("chat.context.none");
  }
  const labels = intent.sources.slice(0, 3).map((source) => source.label || source.relativePath || source.sourcePath || source.path || source.familyId || source.kind);
  const suffix = intent.sources.length > labels.length ? ` +${intent.sources.length - labels.length}` : "";
  return `${labels.join(", ")}${suffix}`;
}

export function BuildLifecycleConfirmation({
  busy,
  confirmation,
  onAcceptedChange,
  onCancel,
  onConfirm,
  t
}: {
  busy: boolean;
  confirmation: BuildLifecycleConfirmationState;
  onAcceptedChange: (accepted: boolean) => void;
  onCancel: () => void;
  onConfirm: () => void;
  t: Translator;
}) {
  const actionConfirmation = confirmation.panel.confirmation;
  const runState = confirmation.panel.run_state;
  const copy = buildLifecycleConfirmationCopy(t, confirmation);
  return (
    <div
      aria-label={t("build.confirmation.aria")}
      aria-live="polite"
      className="build-lifecycle-confirmation"
      data-paradev-confirmation-default-confirmed={String(actionConfirmation.default_confirmed)}
      data-paradev-confirmation-operation-id={confirmation.panel.operation_id}
      data-paradev-confirmation-required={String(actionConfirmation.required)}
      data-paradev-confirmation-run-detail={runState.detail}
      data-paradev-confirmation-run-status={runState.status}
      data-paradev-confirmation-satisfied={String(confirmation.panel.confirmation_satisfied)}
      data-paradev-confirmation-scope={actionConfirmation.scope}
      data-paradev-confirmation-sdk-title={actionConfirmation.title}
      data-paradev-confirmation-style={actionConfirmation.style}
      data-paradev-confirmation-summary={actionConfirmation.summary}
      data-paradev-confirmation-target-key={confirmation.targetKey}
      data-paradev-confirmation-run-id={
        typeof confirmation.values.run_id === "string" ? confirmation.values.run_id : undefined
      }
      id="build-lifecycle-confirmation"
    >
      <label className="build-lifecycle-confirmation-label">
        <input checked={confirmation.panel.confirmation_satisfied} disabled={busy} onChange={(event) => onAcceptedChange(event.target.checked)} type="checkbox" />
        <span>
          <strong>{copy.title}</strong>
          <small>{copy.detail}</small>
        </span>
      </label>
      <div className="build-lifecycle-confirmation-actions">
        <button className="toolbar-button subtle" disabled={busy} onClick={onCancel} type="button">
          {t("build.confirmation.cancel")}
        </button>
        <button className="toolbar-button primary" disabled={busy || runState.disabled} onClick={onConfirm} type="button">
          {t("build.confirmation.continue")}
        </button>
      </div>
    </div>
  );
}

function buildLifecycleConfirmationCopy(
  t: Translator,
  confirmation: BuildLifecycleConfirmationState
): { detail: string; title: string } {
  if (confirmation.action === "interrupt") {
    return {
      detail: t("build.confirmation.interrupt.detail"),
      title: t("build.confirmation.interrupt.title")
    };
  }
  if (confirmation.target) {
    return {
      detail: t("build.confirmation.start.partial.detail", {
        target: confirmation.target.id
      }),
      title: t("build.confirmation.start.partial.title")
    };
  }
  const mode = confirmation.values.mode === "full" ? "full" : "cached";
  return {
    detail: t(
      mode === "full"
        ? "build.confirmation.start.detail.full"
        : "build.confirmation.start.detail.cached"
    ),
    title: t("build.confirmation.start.title")
  };
}

export function BuildActionAlert({ detail, t }: { detail: string | null | undefined; t: Translator }) {
  if (!detail) {
    return null;
  }
  return (
    <div className="build-action-alert" role="alert">
      <AlertTriangle aria-hidden="true" size={15} />
      <span>
        <strong>{t("build.actionError.title")}</strong>
        <small>{detail}</small>
      </span>
    </div>
  );
}

export function BuildLatestPartialResult({
  result,
  targetLabel,
  t
}: {
  result: BuildPartialResult | null;
  targetLabel: string;
  t: Translator;
}) {
  if (!result) {
    return null;
  }
  const meta = [
    result.durationMs === null ? "" : formatBuildDurationText(t, result.durationMs),
    result.finishedAtMs === null ? "" : formatTimestampText(t, result.finishedAtMs)
  ].filter(Boolean).join(" · ");
  return (
    <div
      aria-atomic="true"
      aria-live="polite"
      className={`build-latest-partial-result ${result.state}`}
      data-paradev-latest-partial-result={result.state}
      role="status"
    >
      <HistoryStatusIcon status={result.state} />
      <span>
        <small className="build-latest-partial-label">{t("build.latestPartial.label")}</small>
        <strong>{partialResultTitle(t, result.state, targetLabel)}</strong>
        {meta ? <small>{meta}</small> : null}
        <small>{partialResultNextStep(t, result.state, targetLabel)}</small>
      </span>
      <span className={historyPillClass(result.state)}>{historyStatusLabel(t, result.state)}</span>
    </div>
  );
}

function BuildAiHandoff({ intent, t }: { intent: AiOperationIntent | null; t: Translator }) {
  if (!intent || (intent.operationId !== "build.plan" && intent.operationId !== "build.start")) {
    return null;
  }
  const detailKey: TranslationKey = intent.operationId === "build.plan" ? "build.aiHandoff.plan.detail" : "build.aiHandoff.start.detail";
  return (
    <section className="build-ai-handoff" data-paradev-ai-operation-id={intent.operationId} data-paradev-ai-operation-passive="true">
      <span>
        <strong>{t("build.aiHandoff.title", { operation: intent.operationId })}</strong>
        <small>{t(detailKey)}</small>
      </span>
      <div className="build-ai-handoff-meta">
        <code>{t("build.aiHandoff.role", { role: intent.role || t("chat.route.default") })}</code>
        <code>{t("build.aiHandoff.context", { sources: aiOperationIntentSourceSummary(intent, t) })}</code>
      </div>
    </section>
  );
}

function BuildBlockingDiagnostics({ diagnostics, total, t }: { diagnostics: BuildDiagnosticItem[]; total: number; t: Translator }) {
  if (diagnostics.length === 0) {
    return null;
  }
  const hiddenCount = Math.max(0, total - diagnostics.length);
  return (
    <div className="build-diagnostics-list" aria-label={t("build.diagnostics.blockingTitle")}>
      <div className="build-diagnostics-header">
        <span>
          <strong>{t("build.diagnostics.blockingTitle")}</strong>
          <small>{t("build.diagnostics.blockingDetail", { count: total })}</small>
        </span>
      </div>
      {diagnostics.map((diagnostic) => (
        <article className="build-diagnostic-row" key={diagnostic.key}>
          <span className="status-pill offline">{buildDiagnosticSeverityLabel(t, diagnostic.severity)}</span>
          <span>
            <strong>{diagnostic.message}</strong>
            <small>
              <code>{diagnostic.code}</code>
              {diagnostic.target ? <em>{diagnostic.target}</em> : null}
              {diagnostic.path ? <em>{diagnostic.path}</em> : null}
            </small>
          </span>
        </article>
      ))}
      {hiddenCount > 0 ? <p className="build-diagnostics-more">{t("build.diagnostics.more", { count: hiddenCount })}</p> : null}
    </div>
  );
}

function LabeledSelect<T extends string>({
  configKey,
  detail,
  label,
  onChange,
  options,
  title,
  value
}: {
  configKey?: string;
  detail?: string;
  label: string;
  onChange: (value: T) => void;
  options: { label: string; value: T }[];
  title: string;
  value: T;
}) {
  return (
    <div className="build-select-group">
      <span>{label}</span>
      <SelectField
        className="build-header-select"
        data-paradev-config-key={configKey}
        label={title}
        onChange={(event) => onChange(event.target.value as T)}
        options={options}
        value={value}
      />
      {detail ? <small className="build-select-detail">{detail}</small> : null}
    </div>
  );
}

export function buildLaunchModeDetail(t: Translator, launchMode: Hoi4LaunchMode, gameRoot: string): string {
  if (launchMode === "local") {
    return gameRoot ? t("build.launchMode.detail.local", { gameRoot }) : t("build.launchMode.detail.localMissing");
  }
  return t("build.launchMode.detail.steam");
}

export function buildLaunchReadinessDetail(
  t: Translator,
  readiness: Hoi4LaunchReadinessPayload
): string {
  switch (readiness.code) {
    case "unsupported_game":
      return t("build.launch.readiness.unsupportedGame");
    case "generated_descriptor_missing":
      return t("build.launch.readiness.generatedDescriptorMissing");
    case "output_not_launcher_visible":
      return t("build.launch.readiness.outputNotVisible", {
        outputRoot: readiness.outputRoot
      });
    case "launcher_descriptor_missing":
      return t("build.launch.readiness.launcherDescriptorMissing");
    case "publication_invalid":
      return t("build.launch.readiness.publicationInvalid");
    case "publication_incomplete":
    case "whole_project_baseline_missing":
      return t("build.launch.readiness.wholeProjectRequired");
    case "launcher_descriptor_unreadable":
    case "launcher_path_invalid":
    case "launcher_path_mismatch":
    case "launcher_path_missing":
      return t("build.launch.readiness.launcherRepair");
    case "ready":
      return readiness.reason;
    default:
      return readiness.reason;
  }
}

export function buildModeDetail(t: Translator, mode: BuildMode): string {
  return mode === "full"
    ? t("build.mode.detail.full")
    : t("build.mode.detail.cached");
}

function buildLaunchModeOptionLabel(t: Translator, launchMode: Hoi4LaunchMode): string {
  return launchMode === "local" ? t("build.launchMode.local") : t("build.launchMode.steam");
}

type BuildEntityAction = {
  ariaLabel?: string;
  confirmationActive: boolean;
  disabled: boolean;
  kind: "interrupt" | "rebuild";
  label: string;
  onClick: () => void;
  runId?: string;
  targetKey: string;
};

function BuildEntity({
  action,
  entity,
  sourceLabel,
  subtitle,
  title
}: {
  action: BuildEntityAction;
  entity: BuildEntityRow;
  sourceLabel: string;
  subtitle: string;
  title: string;
}) {
  const contract =
    action.kind === "interrupt" ? BUILD_INTERRUPT_ACTION_CONTRACT : BUILD_START_ACTION_CONTRACT;
  return (
    <div className={`build-entity-row ${entity.status}`}>
      <span>
        <strong>{title}</strong>
        <small>{subtitle}</small>
      </span>
      <span className="build-entity-progress">
        <span className="build-progress-track" aria-hidden="true">
          <span style={{ width: `${entity.progressPercent}%` }} />
        </span>
        <code>{sourceLabel}</code>
      </span>
      <button
        aria-label={action.ariaLabel}
        aria-describedby={action.confirmationActive ? "build-lifecycle-confirmation" : undefined}
        className={`toolbar-button${action.kind === "interrupt" ? " danger" : ""}`}
        data-paradev-build-run-id={action.runId}
        data-paradev-build-target-key={action.targetKey}
        data-paradev-confirmation-required={String(contract.confirmationRequired)}
        data-paradev-operation-id={contract.operationId}
        data-paradev-payload={contract.payload}
        data-paradev-rest-method={contract.restMethod}
        data-paradev-rest-path={contract.restPath}
        data-paradev-sdk-call={contract.sdkCall}
        disabled={action.disabled || (action.kind === "rebuild" && entity.status === "blocked")}
        onClick={action.onClick}
        type="button"
      >
        {action.kind === "interrupt" ? (
          <Square aria-hidden="true" size={13} />
        ) : (
          <RefreshCw aria-hidden="true" size={13} />
        )}
        {action.label}
      </button>
    </div>
  );
}

function BuildActivePartialRuns({
  actionPending,
  confirmation,
  nowMs,
  onInterrupt,
  runs,
  t
}: {
  actionPending: boolean;
  confirmation: BuildLifecycleConfirmationState | null;
  nowMs: number;
  onInterrupt: (run: BuildRunRecord) => void;
  runs: readonly BuildRunRecord[];
  t: Translator;
}) {
  if (runs.length === 0) {
    return null;
  }
  return (
    <div
      aria-label={t("build.activePartial.aria")}
      className="build-active-partial-list"
      role="list"
    >
      {runs.map((run) => {
        const target = run.target;
        if (!target) {
          return null;
        }
        const targetKey = buildTargetKey(target);
        const progressPercent = normalizedBuildProgressPercent(run.progress?.percent);
        const phase = buildProgressPhaseLabel(t, run.progress?.phase ?? "waiting", 1);
        const detail = run.progress?.detail?.trim() || phase;
        const elapsed = typeof run.startedAtMs === "number"
          ? formatBuildDurationText(t, Math.max(0, nowMs - run.startedAtMs))
          : t("build.activePartial.elapsedUnknown");
        const confirmationActive =
          confirmation?.action === "interrupt" &&
          confirmation.values.run_id === run.runId &&
          sameBuildTarget(confirmation.target, target);
        return (
          <div
            className="build-active-partial-row"
            data-paradev-build-run-id={run.runId ?? undefined}
            data-paradev-build-target-key={targetKey}
            key={run.runId ?? targetKey}
            role="listitem"
          >
            <span className="build-active-partial-copy">
              <small>{t("build.activePartial.label")}</small>
              <strong title={buildTargetLabel(t, target)}>{buildTargetLabel(t, target)}</strong>
              <span title={detail}>
                {t("build.activePartial.meta", {
                  detail,
                  elapsed,
                  percent: Math.round(progressPercent)
                })}
              </span>
            </span>
            <span
              aria-label={t("build.activePartial.progress", {
                target: buildTargetLabel(t, target)
              })}
              aria-valuemax={100}
              aria-valuemin={0}
              aria-valuenow={Math.round(progressPercent)}
              className="build-progress-track"
              role="progressbar"
            >
              <span style={{ width: `${progressPercent}%` }} />
            </span>
            <button
              aria-label={t("build.action.interruptTarget", {
                target: buildTargetLabel(t, target)
              })}
              aria-describedby={confirmationActive ? "build-lifecycle-confirmation" : undefined}
              className="toolbar-button danger"
              data-paradev-build-run-id={run.runId ?? undefined}
              data-paradev-build-target-key={targetKey}
              data-paradev-confirmation-required={String(BUILD_INTERRUPT_ACTION_CONTRACT.confirmationRequired)}
              data-paradev-operation-id={BUILD_INTERRUPT_ACTION_CONTRACT.operationId}
              data-paradev-payload={BUILD_INTERRUPT_ACTION_CONTRACT.payload}
              data-paradev-rest-method={BUILD_INTERRUPT_ACTION_CONTRACT.restMethod}
              data-paradev-rest-path={BUILD_INTERRUPT_ACTION_CONTRACT.restPath}
              data-paradev-sdk-call={BUILD_INTERRUPT_ACTION_CONTRACT.sdkCall}
              disabled={actionPending || !run.runId}
              onClick={() => onInterrupt(run)}
              type="button"
            >
              <Square aria-hidden="true" size={13} />
              {t("build.action.interrupt")}
            </button>
          </div>
        );
      })}
    </div>
  );
}

export function BuildHistoryList({
  entries,
  expandedIds,
  onRemove,
  onToggle,
  t
}: {
  entries: BuildHistoryEntry[];
  expandedIds: Set<string>;
  onRemove: (id: string) => void;
  onToggle: (id: string) => void;
  t: Translator;
}) {
  if (entries.length === 0) {
    return <p className="build-empty-state">{t("build.history.empty")}</p>;
  }
  return (
    <div className="build-history-list">
      {entries.map((entry, index) => {
        const expanded = expandedIds.has(entry.id);
        const detailsId = `build-history-details-${index}`;
        return (
          <article className={`build-history-row ${historyRowClass(entry.status)}`} key={entry.id}>
            <button
              aria-controls={detailsId}
              aria-expanded={expanded}
              className="build-history-summary"
              onClick={() => onToggle(entry.id)}
              type="button"
            >
              {expanded ? <ChevronDown aria-hidden="true" size={15} /> : <ChevronRight aria-hidden="true" size={15} />}
              <HistoryStatusIcon status={entry.status} />
              <span>
                <strong>{historyTitle(t, entry)}</strong>
                <small>
                  {formatTimestampText(t, entry.finishedAtMs)} · {formatBuildDurationText(t, entry.durationMs)}
                </small>
              </span>
            </button>
            <span className={`build-history-status ${historyPillClass(entry.status)}`}>{historyStatusLabel(t, entry.status)}</span>
            <button
              className="toolbar-button icon-only danger build-history-remove"
              aria-label={t("build.history.remove", { id: entry.id })}
              onClick={() => onRemove(entry.id)}
              title={t("build.action.remove")}
              type="button"
            >
              <Trash2 aria-hidden="true" size={14} />
            </button>
            {expanded ? (
              <dl className="build-history-details" id={detailsId}>
                <div>
                  <dt>{t("build.history.detail.runId")}</dt>
                  <dd>{entry.id}</dd>
                </div>
                <div>
                  <dt>{t("build.history.detail.target")}</dt>
                  <dd>{buildTargetLabel(t, entry.target ?? null)}</dd>
                </div>
                <div>
                  <dt>{t("build.history.detail.mode")}</dt>
                  <dd>{buildModeLabel(t, entry.mode)}</dd>
                </div>
                <div>
                  <dt>{t("build.history.detail.duration")}</dt>
                  <dd>{formatBuildDurationText(t, entry.durationMs)}</dd>
                </div>
                <div>
                  <dt>{t("build.history.detail.started")}</dt>
                  <dd>{formatTimestampText(t, entry.startedAtMs)}</dd>
                </div>
                <div>
                  <dt>{t("build.history.detail.finished")}</dt>
                  <dd>{formatTimestampText(t, entry.finishedAtMs)}</dd>
                </div>
                {entry.status === "failed" || entry.errorSummary || entry.exitCode !== undefined ? (
                  <div className="build-history-detail-wide">
                    <dt>{t("build.history.detail.reason")}</dt>
                    <dd title={buildHistoryReason(t, entry)}>{buildHistoryReason(t, entry)}</dd>
                  </div>
                ) : null}
                {entry.command?.length ? (
                  <div className="build-history-detail-wide">
                    <dt>{t("build.history.detail.command")}</dt>
                    <dd title={entry.command.join(" ")}>{entry.command.join(" ")}</dd>
                  </div>
                ) : null}
                {entry.outputPath ? (
                  <div>
                    <dt>{t("build.history.detail.output")}</dt>
                    <dd title={entry.outputPath}>{entry.outputPath}</dd>
                  </div>
                ) : null}
                {entry.errorPath ? (
                  <div>
                    <dt>{t("build.history.detail.errorLog")}</dt>
                    <dd title={entry.errorPath}>{entry.errorPath}</dd>
                  </div>
                ) : null}
              </dl>
            ) : null}
          </article>
        );
      })}
    </div>
  );
}

function Metric({ icon, label, value }: { icon: ReactNode; label: string; value: number | string }) {
  return (
    <div className="build-metric">
      <span className="panel-icon">{icon}</span>
      <span>
        <small>{label}</small>
        <strong>{value}</strong>
      </span>
    </div>
  );
}

function BuildStatusIcon({ label, state }: { label: string; state: BuildRunState | "blocked" | "ready" }) {
  if (state === "running") {
    return (
      <span className="build-status-mark running" aria-label={label} role="img">
        <Ellipsis aria-hidden="true" size={17} />
      </span>
    );
  }
  if (state === "failed") {
    return (
      <span className="build-status-mark failed" aria-label={label} role="img">
        <XCircle aria-hidden="true" size={17} />
      </span>
    );
  }
  if (state === "blocked" || state === "interrupted") {
    return (
      <span className="build-status-mark warning" aria-label={label} role="img">
        <AlertTriangle aria-hidden="true" size={17} />
      </span>
    );
  }
  return (
    <span className="build-status-mark ready" aria-label={label} role="img">
      <CheckCircle2 aria-hidden="true" size={17} />
    </span>
  );
}

function HistoryStatusIcon({ status }: { status: BuildHistoryEntry["status"] }) {
  if (status === "failed") {
    return <XCircle aria-hidden="true" className="build-history-mark failed" size={15} />;
  }
  if (status === "interrupted") {
    return <AlertTriangle aria-hidden="true" className="build-history-mark warning" size={15} />;
  }
  return <CheckCircle2 aria-hidden="true" className="build-history-mark ready" size={15} />;
}

function buildTimeText(
  t: Translator,
  estimateLabel: string,
  fullRun: BuildRunRecord | undefined,
  projectHistory: readonly BuildHistoryEntry[],
  nowMs: number,
  runningRuns: readonly BuildRunRecord[]
): string {
  const runningStartedAtMs = runningRuns.reduce<number | null>((earliest, run) => {
    if (typeof run.startedAtMs !== "number") {
      return earliest;
    }
    return earliest === null ? run.startedAtMs : Math.min(earliest, run.startedAtMs);
  }, null);
  const elapsedLabel = runningStartedAtMs !== null
    ? formatBuildDurationText(t, Math.max(0, nowMs - runningStartedAtMs))
    : latestFullElapsedLabel(t, projectHistory, fullRun?.runId ?? null);
  const runningPartialOnly = runningRuns.some((run) => run.target) && fullRun?.state !== "running";
  return `${elapsedLabel || "--"} : ${runningPartialOnly ? "--" : estimateLabel || "--"}`;
}

function latestFullElapsedLabel(t: Translator, projectHistory: readonly BuildHistoryEntry[], runId: string | null): string {
  const entry = runId
    ? projectHistory.find((history) => history.id === runId && !history.target)
    : projectHistory.find((history) => !history.target && history.status === "completed");
  return entry ? formatBuildDurationText(t, entry.durationMs) : "";
}

function formatBuildDurationText(t: Translator, durationMs: number): string {
  const totalSeconds = Math.max(1, Math.round(durationMs / 1000));
  if (totalSeconds < 60) {
    return t("build.duration.seconds", { count: totalSeconds });
  }
  const minutes = Math.floor(totalSeconds / 60);
  const seconds = totalSeconds % 60;
  if (minutes < 60) {
    return seconds > 0
      ? t("build.duration.minutesSeconds", { minutes, seconds })
      : t("build.duration.minutes", { count: minutes });
  }
  const hours = Math.floor(minutes / 60);
  const remainingMinutes = minutes % 60;
  return remainingMinutes > 0
    ? t("build.duration.hoursMinutes", { hours, minutes: remainingMinutes })
    : t("build.duration.hours", { count: hours });
}

function normalizedBuildProgressPercent(value: number | null | undefined): number {
  return typeof value === "number" && Number.isFinite(value)
    ? Math.max(0, Math.min(100, value))
    : 0;
}

export function buildStartRequestForBuildPage(
  activeProject: ProjectOption,
  mode: BuildMode,
  target: BuildTarget | null,
  strictMetadata: boolean,
  parallelism: number
): ProjectBuildRequest {
  return {
    projectRoot: activeProject.path,
    mode,
    parallelism,
    profile: activeProject.game ?? "hoi4",
    strictMetadata,
    target
  };
}

export function buildActionErrorDetail(t: Translator, action: BuildActionErrorKind, error: unknown): string {
  const message = localizeDesktopBridgeError(t, buildErrorMessage(error));
  if (action === "openOutput") {
    return t("build.openOutput.failed", { message });
  }
  if (action === "runGame") {
    return t("build.launch.failed", { message });
  }
  if (action === "interrupt") {
    return t("build.interrupt.failed", { message });
  }
  if (action === "status") {
    return t("build.status.failed", { message });
  }
  if (action === "refresh") {
    return t("build.refresh.failed", { message });
  }
  if (action === "diagnostics") {
    return t("build.diagnostics.failed", { message });
  }
  if (action === "configRead") {
    return t("build.configRead.failed", { message });
  }
  if (action === "configWrite") {
    return t("build.configWrite.failed", { message });
  }
  return t("build.start.failed", { message });
}

function buildErrorMessage(error: unknown): string {
  if (error instanceof Error) {
    return error.message;
  }
  if (typeof error === "string") {
    return error;
  }
  return String(error);
}

function buildBlockingDiagnosticItems(diagnostics: ReadonlyArray<Record<string, unknown>>): BuildDiagnosticItem[] {
  return diagnostics
    .filter((diagnostic) => diagnosticSeverity(diagnostic) === "error")
    .slice(0, MAX_BLOCKING_DIAGNOSTICS)
    .map((diagnostic, index) => ({
      code: diagnosticText(diagnostic.code) || "diagnostic",
      key: `${diagnosticText(diagnostic.code) || "diagnostic"}:${diagnosticPath(diagnostic)}:${index}`,
      message: diagnosticText(diagnostic.message) || diagnosticText(diagnostic.code) || "diagnostic",
      path: diagnosticPath(diagnostic),
      severity: diagnosticSeverity(diagnostic),
      target: diagnosticTarget(diagnostic)
    }));
}

function diagnosticSeverity(diagnostic: Record<string, unknown>): string {
  const severity = diagnosticText(diagnostic.severity ?? diagnostic.level).toLowerCase();
  return severity || "error";
}

function diagnosticTarget(diagnostic: Record<string, unknown>): string {
  const source = diagnosticRecord(diagnostic.source);
  return (
    diagnosticText(diagnostic.module_id ?? source?.module_id) ||
    diagnosticText(diagnostic.collection_id ?? source?.collection_id) ||
    diagnosticText(diagnostic.family ?? source?.family) ||
    diagnosticText(diagnostic.owner)
  );
}

function diagnosticPath(diagnostic: Record<string, unknown>): string {
  const source = diagnosticRecord(diagnostic.source);
  return diagnosticText(diagnostic.source_path) || diagnosticText(source?.path) || diagnosticText(diagnostic.artifact_path);
}

function diagnosticRecord(value: unknown): Record<string, unknown> | null {
  return value && typeof value === "object" && !Array.isArray(value) ? (value as Record<string, unknown>) : null;
}

function diagnosticText(value: unknown): string {
  return typeof value === "string" ? value.trim() : "";
}

function buildDiagnosticSeverityLabel(t: Translator, severity: string): string {
  if (severity === "warning") {
    return t("build.diagnostics.severity.warning");
  }
  return t("build.diagnostics.severity.error");
}

function buildStatusTitle(t: Translator, state: BuildRunState | "blocked" | "ready", runningPartialCount: number): string {
  if (state === "running" && runningPartialCount > 0) {
    return t("build.status.title.parallel");
  }
  switch (state) {
    case "running":
      return t("build.status.title.running");
    case "interrupted":
      return t("build.status.title.interrupted");
    case "completed":
      return t("build.status.title.completed");
    case "failed":
      return t("build.status.title.failed");
    case "blocked":
      return t("build.status.title.blocked");
    case "ready":
    case "idle":
      return t("build.status.title.ready");
    default:
      return t("build.status.title.ready");
  }
}

function statusPillLabel(t: Translator, state: BuildRunState | "blocked" | "ready"): string {
  if (state === "running") {
    return t("build.status.pill.active");
  }
  if (state === "blocked" || state === "interrupted" || state === "failed") {
    return t("build.status.pill.blocked");
  }
  return t("build.status.pill.ready");
}

export function buildProgressPhaseLabel(t: Translator, phase: string, runningPartialCount: number): string {
  switch (phase) {
    case "artifact_generation":
      return t("build.progress.phase.artifactGeneration");
    case "basic_copy":
      return t("build.progress.phase.basicCopy");
    case "collection_compile":
      return t("build.progress.phase.collectionCompile");
    case "complete":
      return t("build.progress.phase.complete");
    case "discover_collections":
      return t("build.progress.phase.discoverCollections");
    case "discover_modules":
      return t("build.progress.phase.discoverModules");
    case "entity_compile":
    case "source_compile":
      return t("build.progress.phase.entityCompile");
    case "load_project":
      return t("build.progress.phase.loadProject");
    case "parallel_partial":
      return t("build.progress.phase.parallelPartial", { count: runningPartialCount });
    case "post_processing":
      return t("build.progress.phase.postProcessing");
    case "validating_publication":
      return t("build.progress.phase.validatingPublication");
    case "waiting":
      return t("build.progress.phase.waiting");
    case "idle":
      return t("build.progress.phase.ready");
    default:
      {
        const fallbackPhase = humanizeBuildProgressPhase(phase);
        return fallbackPhase ? t("build.progress.phase.custom", { phase: fallbackPhase }) : t("build.progress.phase.ready");
      }
  }
}

function humanizeBuildProgressPhase(phase: string): string {
  const normalized = phase.trim().replace(/[_-]+/g, " ").replace(/\s+/g, " ");
  return normalized ? normalized.charAt(0).toUpperCase() + normalized.slice(1) : "";
}

function buildEntityTitle(t: Translator, entity: BuildEntityRow): string {
  return entity.titleKey ? t(entity.titleKey) : entity.title;
}

function buildEntitySubtitle(t: Translator, entity: BuildEntityRow): string {
  const detail = buildEntityDetail(t, entity);
  if (entity.kind === "family") {
    return detail;
  }
  const familyLabel = entity.familyTitleKey ? t(entity.familyTitleKey) : entity.family;
  return `${familyLabel} · ${detail}`;
}

function buildEntityDetail(t: Translator, entity: BuildEntityRow): string {
  if (entity.status === "failed" || entity.status === "interrupted") {
    return entity.detail;
  }
  if (entity.kind === "family") {
    return t("build.entity.familyDetail", { modules: entity.moduleCount, sources: entity.sourceCount });
  }
  return t("build.entity.detail", { path: entity.relativeRoot, sources: entity.sourceCount });
}

function historyTitle(t: Translator, entry: BuildHistoryEntry): string {
  return entry.target
    ? `${t("build.history.mode.partial")} · ${buildTargetLabel(t, entry.target)}`
    : t("build.history.mode.full");
}

function buildPartialResultTargetLabel(t: Translator, result: BuildPartialResult, entities: readonly BuildEntityRow[]): string {
  const entity = entities.find((candidate) => sameBuildTarget(candidate.target, result.target));
  return entity ? buildEntityTitle(t, entity) : buildTargetLabel(t, result.target);
}

function partialResultTitle(t: Translator, state: BuildPartialResult["state"], target: string): string {
  if (state === "completed") {
    return t("build.latestPartial.title.completed", { target });
  }
  if (state === "interrupted") {
    return t("build.latestPartial.title.interrupted", { target });
  }
  return t("build.latestPartial.title.failed", { target });
}

function partialResultNextStep(t: Translator, state: BuildPartialResult["state"], target: string): string {
  if (state === "completed") {
    return t("build.latestPartial.next.completed", { target });
  }
  if (state === "interrupted") {
    return t("build.latestPartial.next.interrupted", { target });
  }
  return t("build.latestPartial.next.failed", { target });
}

function buildTargetLabel(t: Translator, target: BuildTarget | null): string {
  if (!target) {
    return t("build.history.target.full");
  }
  const kind = buildKindLabel(t, target.kind);
  return target.family && target.family !== target.id
    ? `${kind} · ${target.family} · ${target.id}`
    : `${kind} · ${target.id}`;
}

function buildKindLabel(t: Translator, kind: BuildTarget["kind"]): string {
  if (kind === "collection") {
    return t("build.kind.collection");
  }
  if (kind === "family") {
    return t("build.kind.family");
  }
  return t("build.kind.module");
}

function historyStatusLabel(t: Translator, status: BuildHistoryEntry["status"]): string {
  if (status === "completed") {
    return t("build.history.status.completed");
  }
  if (status === "interrupted") {
    return t("build.history.status.interrupted");
  }
  return t("build.history.status.failed");
}

function historyPillClass(status: BuildHistoryEntry["status"]) {
  if (status === "completed") {
    return "status-pill ready";
  }
  if (status === "interrupted") {
    return "status-pill planned";
  }
  return "status-pill offline";
}

function historyRowClass(status: BuildHistoryEntry["status"]) {
  if (status === "completed") {
    return "ready";
  }
  if (status === "interrupted") {
    return "warning";
  }
  return "blocked";
}

function buildModeLabel(t: Translator, mode: BuildMode): string {
  return mode === "full" ? t("build.mode.full") : t("build.mode.cached");
}

function buildHistoryReason(t: Translator, entry: BuildHistoryEntry): string {
  if (entry.errorSummary) {
    return entry.errorSummary;
  }
  if (entry.exitCode !== undefined) {
    return t("build.history.detail.exitCode", { code: entry.exitCode });
  }
  if (entry.status === "interrupted") {
    return t("build.history.detail.interruptedReason");
  }
  return t("build.history.detail.noReason");
}

function statusPillClass(state: BuildRunState | "blocked" | "ready") {
  if (state === "blocked" || state === "interrupted" || state === "failed") {
    return "status-pill offline";
  }
  if (state === "running") {
    return "status-pill scaffold";
  }
  return "status-pill ready";
}

function compareHistoryDesc(left: BuildHistoryEntry, right: BuildHistoryEntry): number {
  return right.finishedAtMs - left.finishedAtMs;
}

function formatTimestampText(t: Translator, timestampMs: number): string {
  const date = new Date(timestampMs);
  return t("build.timestamp.full", {
    day: pad2(date.getDate()),
    hour: pad2(date.getHours()),
    minute: pad2(date.getMinutes()),
    month: pad2(date.getMonth() + 1),
    second: pad2(date.getSeconds()),
    year: date.getFullYear()
  });
}

function pad2(value: number): string {
  return String(value).padStart(2, "0");
}

function removeProjectStateKey<Value>(record: Readonly<Record<string, Value>>, key: string): Record<string, Value> {
  if (!(key in record)) {
    return record;
  }
  const next = { ...record };
  delete next[key];
  return next;
}
