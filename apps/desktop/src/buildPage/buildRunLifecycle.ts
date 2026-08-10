import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import {
  getProjectBuildRuns,
  getProjectBuildStatus,
  hasDesktopBackend,
  interruptProjectBuild,
  startProjectBuild,
  type ProjectBuildRequest,
  type ProjectBuildRunPayload
} from "../services/paradev";
import type { ProjectOption } from "../types";
import {
  buildTargetKey,
  readBuildHistory,
  readBuildHistoryTombstones,
  recordBuildHistoryEntry,
  removeBuildHistoryEntry,
  type BuildHistoryEntry,
  type BuildMode,
  type BuildRuntime,
  type BuildTarget
} from "./buildPageModel";

const BUILD_STATUS_POLL_INTERVAL_MS = 1_200;
const BUILD_RUN_CHECKPOINT_STORAGE_KEY = "paradev.build.run-checkpoints.v1";
const MAX_RETAINED_BUILD_RUN_CHECKPOINTS = 256;
const MAX_RETAINED_FULL_BUILD_BASELINES = 256;
const MAX_RETAINED_TERMINAL_BUILD_RUNS = 256;
const MAX_RETAINED_TERMINAL_IDENTITIES = 768;
const CLOSED_BUILD_RECOVERY_MESSAGE =
  "This build was interrupted because ParaDev closed or relaunched before the native build registry reported a terminal result.";
const RUN_NO_LONGER_RETAINED_MESSAGE = "The build registry no longer retains this run; refresh the project and start it again.";

export type BuildLifecycleErrorKind = "interrupt" | "refresh" | "start" | "status";

export type BuildLifecycleError = {
  readonly kind: BuildLifecycleErrorKind;
  readonly message: string;
  readonly projectRoot: string | null;
  readonly runId?: string | null;
  readonly slotKey?: string;
  readonly startAttemptToken?: number;
};

export type BuildRunRecord = BuildRuntime & {
  readonly finishedAtMs?: number | null;
  readonly projectId: string;
  readonly projectRoot: string;
  readonly runId: string | null;
  readonly startedAtMs: number | null;
  readonly terminalSequence?: number | null;
};

export type BuildRunRecoveryState = "loading" | "ready" | "failed";

export type BuildRunLifecycleController = {
  readonly errorsByProjectRoot: Readonly<Record<string, BuildLifecycleError>>;
  readonly fullBuildBaselines?: Readonly<Record<string, FullBuildBaseline>>;
  readonly globalError: BuildLifecycleError | null;
  readonly history: readonly BuildHistoryEntry[];
  readonly recoveryState: BuildRunRecoveryState;
  readonly runs: readonly BuildRunRecord[];
  clearError: (projectRoot: string, kind?: BuildLifecycleErrorKind, runId?: string | null) => void;
  interrupt: (runId: string) => Promise<ProjectBuildRunPayload>;
  removeHistory: (id: string) => void;
  retryRecovery: () => void;
  start: (request: ProjectBuildRequest, project: ProjectOption) => Promise<ProjectBuildRunPayload>;
};

type StoredBuildRunRecord = BuildRunRecord & {
  readonly startAttemptToken: number | null;
};

type BuildRunStore = Record<string, StoredBuildRunRecord>;

type BuildRunCheckpoint = Omit<StoredBuildRunRecord, "startAttemptToken" | "terminalSequence">;

type StatusErrorsByProjectRoot = Map<string, Map<string, BuildLifecycleError>>;
type StartErrorsByProjectRoot = Map<string, Map<string, BuildLifecycleError>>;

export type FullBuildBaseline = {
  readonly finishedAtMs: number | null;
  readonly terminalSequence: number | null;
};

type StatusPollToken = {
  readonly generation: number;
  readonly request: number;
};

type BuildRunLifecycleOptions = {
  readonly onProjectRefresh: (projectRoot?: string, fallbackProjectId?: string) => Promise<void>;
  readonly pollIntervalMs?: number;
  readonly projects: readonly ProjectOption[];
};

/**
 * Owns desktop build processes for the lifetime of the application shell.
 *
 * The controller survives rail-view unmounts, serializes status polling, and
 * attributes terminal history and refresh work to the project that started the
 * run. The native/Python registry remains authoritative and is reconciled on
 * shell startup so a webview reload can recover every tracked partial build.
 */
export function useBuildRunLifecycle({
  onProjectRefresh,
  pollIntervalMs = BUILD_STATUS_POLL_INTERVAL_MS,
  projects
}: BuildRunLifecycleOptions): BuildRunLifecycleController {
  const desktopBackend = hasDesktopBackend();
  const initialHistoryRef = useRef<BuildHistoryEntry[] | null>(null);
  if (initialHistoryRef.current === null) {
    initialHistoryRef.current = readBuildHistory();
  }
  const initialRunsRef = useRef<BuildRunStore | null>(null);
  if (initialRunsRef.current === null) {
    initialRunsRef.current = readBuildRunCheckpoints();
  }
  const initialFullBuildBaselinesRef = useRef<Record<string, FullBuildBaseline> | null>(null);
  if (initialFullBuildBaselinesRef.current === null) {
    initialFullBuildBaselinesRef.current = deriveFullBuildBaselines(
      Object.values(initialRunsRef.current),
      {}
    );
  }
  const [history, setHistory] = useState<BuildHistoryEntry[]>(initialHistoryRef.current);
  const [runsByKey, setRunsByKey] = useState<BuildRunStore>(initialRunsRef.current);
  const [fullBuildBaselinesByProjectRoot, setFullBuildBaselinesByProjectRoot] = useState<
    Record<string, FullBuildBaseline>
  >(initialFullBuildBaselinesRef.current);
  const [errorsByProjectRoot, setErrorsByProjectRoot] = useState<Record<string, BuildLifecycleError>>({});
  const [globalError, setGlobalError] = useState<BuildLifecycleError | null>(null);
  const [recoveryState, setRecoveryState] = useState<BuildRunRecoveryState>(() => (desktopBackend ? "loading" : "ready"));
  const [recoveryRevision, setRecoveryRevision] = useState(0);
  const runsRef = useRef<BuildRunStore>(initialRunsRef.current);
  const unreconciledRunningCheckpointsRef = useRef(
    new Map(
      Object.values(initialRunsRef.current)
        .filter((run): run is StoredBuildRunRecord & { runId: string } => run.state === "running" && Boolean(run.runId))
        .map((run) => [run.runId, run])
    )
  );
  const fullBuildBaselinesRef = useRef<Record<string, FullBuildBaseline>>(
    initialFullBuildBaselinesRef.current
  );
  const supersededPartialRunIdsRef = useRef(new Set<string>());
  const startErrorsByProjectRootRef = useRef<StartErrorsByProjectRoot>(new Map());
  const statusErrorsByProjectRootRef = useRef<StatusErrorsByProjectRoot>(new Map());
  const projectsRef = useRef(projects);
  const refreshRef = useRef(onProjectRefresh);
  const historyTombstonesRef = useRef<Set<string> | null>(null);
  if (historyTombstonesRef.current === null) {
    historyTombstonesRef.current = new Set(readBuildHistoryTombstones());
  }
  const historyProjectIdsRef = useRef(
    new Map(initialHistoryRef.current.map((entry) => [entry.id, buildHistoryProjectIdentity(entry)]))
  );
  const terminalRefreshedRef = useRef(
    new Set([...initialHistoryRef.current.map((entry) => entry.id), ...(historyTombstonesRef.current ?? [])])
  );
  const nextStartAttemptTokenRef = useRef(0);
  const latestStartAttemptByKeyRef = useRef(new Map<string, number>());
  const statusPollGenerationRef = useRef(0);
  const statusPollRequestRef = useRef(0);
  const inFlightStatusRef = useRef(new Map<string, StatusPollToken>());
  const projectSignature = useMemo(
    () => projects.map((project) => `${project.path}\u0000${project.projectId || project.id}`).sort().join("\u0001"),
    [projects]
  );
  projectsRef.current = projects;
  refreshRef.current = onProjectRefresh;

  const updateRuns = useCallback((updater: (current: BuildRunStore) => BuildRunStore) => {
    const next = pruneBuildRunStore(updater(runsRef.current));
    runsRef.current = next;
    writeBuildRunCheckpoints(next);
    const statusErrorProjects = pruneStatusErrorsToRetainedRuns(statusErrorsByProjectRootRef.current, next);
    const startErrorProjects = pruneStartErrorsToRetainedAttempts(startErrorsByProjectRootRef.current, next);
    const changedErrorProjects = [...new Set([...startErrorProjects, ...statusErrorProjects])];
    if (changedErrorProjects.length > 0) {
      setErrorsByProjectRoot((current) =>
        changedErrorProjects.reduce(
          (errors, projectRoot) =>
            reconcileProjectOwnedError(
              errors,
              projectRoot,
              startErrorsByProjectRootRef.current,
              statusErrorsByProjectRootRef.current
            ),
          current
        )
      );
    }
    setRunsByKey(next);
  }, []);

  const recordStatusError = useCallback((projectRoot: string, runId: string, error: unknown) => {
    const lifecycleError = buildLifecycleError("status", projectRoot, error, runId);
    putProjectStatusError(statusErrorsByProjectRootRef.current, projectRoot, runId, lifecycleError);
    setErrorsByProjectRoot((current) =>
      reconcileProjectOwnedError(
        current,
        projectRoot,
        startErrorsByProjectRootRef.current,
        statusErrorsByProjectRootRef.current
      )
    );
  }, []);

  const clearStatusError = useCallback((projectRoot: string, runId: string) => {
    removeStoredProjectStatusError(statusErrorsByProjectRootRef.current, projectRoot, runId);
    setErrorsByProjectRoot((current) =>
      reconcileProjectOwnedError(
        current,
        projectRoot,
        startErrorsByProjectRootRef.current,
        statusErrorsByProjectRootRef.current
      )
    );
  }, []);

  const recordStartError = useCallback(
    (projectRoot: string, slotKey: string, startAttemptToken: number, error: unknown) => {
      const retained = runsRef.current[slotKey];
      if (retained?.runId !== null || retained.startAttemptToken !== startAttemptToken) {
        return;
      }
      const lifecycleError: BuildLifecycleError = {
        ...buildLifecycleError("start", projectRoot, error),
        slotKey,
        startAttemptToken
      };
      putProjectStartError(startErrorsByProjectRootRef.current, projectRoot, slotKey, lifecycleError);
      setErrorsByProjectRoot((current) =>
        reconcileProjectOwnedError(
          current,
          projectRoot,
          startErrorsByProjectRootRef.current,
          statusErrorsByProjectRootRef.current
        )
      );
    },
    []
  );

  const clearStartError = useCallback((projectRoot: string, slotKey: string, startAttemptToken?: number) => {
    removeStoredProjectStartError(startErrorsByProjectRootRef.current, projectRoot, slotKey, startAttemptToken);
    setErrorsByProjectRoot((current) =>
      reconcileProjectOwnedError(
        current,
        projectRoot,
        startErrorsByProjectRootRef.current,
        statusErrorsByProjectRootRef.current
      )
    );
  }, []);

  const syncHistoryTracking = useCallback(
    (nextHistory: readonly BuildHistoryEntry[], tombstones: ReadonlySet<string>) => {
      const retainedIds = new Set([...nextHistory.map((entry) => entry.id), ...tombstones]);
      historyProjectIdsRef.current = new Map(
        nextHistory.map((entry) => [entry.id, buildHistoryProjectIdentity(entry)])
      );
      terminalRefreshedRef.current = new Set(
        [...terminalRefreshedRef.current].filter((id) => retainedIds.has(id))
      );
      for (const id of tombstones) {
        terminalRefreshedRef.current.add(id);
      }
      trimSetToNewest(terminalRefreshedRef.current, MAX_RETAINED_TERMINAL_IDENTITIES);
    },
    []
  );

  const rememberFullBuildBaseline = useCallback((record: StoredBuildRunRecord) => {
    if (record.target || record.state !== "completed") {
      return;
    }
    const baseline: FullBuildBaseline = {
      finishedAtMs: record.finishedAtMs ?? record.startedAtMs,
      terminalSequence: record.terminalSequence ?? null
    };
    const current = fullBuildBaselinesRef.current[record.projectRoot];
    if (current && compareFullBuildBaselines(baseline, current) <= 0) {
      return;
    }
    const next = pruneFullBuildBaselines({
      ...fullBuildBaselinesRef.current,
      [record.projectRoot]: baseline
    });
    fullBuildBaselinesRef.current = next;
    setFullBuildBaselinesByProjectRoot(next);
  }, []);

  const rememberTerminal = useCallback((payload: ProjectBuildRunPayload, record: BuildRunRecord) => {
    if (!isTerminalBuildPayload(payload)) {
      return;
    }
    const entry = buildHistoryEntryFromPayload(payload, record);
    const terminalId = entry?.id ?? payload.runId ?? buildRunStoreKey(record.projectRoot, record.target);
    const wasRefreshed = terminalRefreshedRef.current.has(terminalId);
    if (
      entry &&
      !historyTombstonesRef.current?.has(terminalId) &&
      historyProjectIdsRef.current.get(terminalId) !== buildHistoryProjectIdentity(entry)
    ) {
      const nextHistory = recordBuildHistoryEntry(entry);
      setHistory(nextHistory);
      syncHistoryTracking(nextHistory, historyTombstonesRef.current ?? new Set());
    }
    const projectKnown = projectsRef.current.some((project) => project.path === record.projectRoot);
    if (!projectKnown || wasRefreshed) {
      return;
    }
    terminalRefreshedRef.current.add(terminalId);
    trimSetToNewest(terminalRefreshedRef.current, MAX_RETAINED_TERMINAL_IDENTITIES);
    refreshRef.current(record.projectRoot, record.projectId).catch((error: unknown) => {
      setErrorsByProjectRoot((current) => ({
        ...current,
        [record.projectRoot]: buildLifecycleError("refresh", record.projectRoot, error)
      }));
    });
  }, [syncHistoryTracking]);

  const commitPayload = useCallback(
    (
      payload: ProjectBuildRunPayload,
      fallback: StoredBuildRunRecord | null = null,
      project: ProjectOption | null = null
    ): StoredBuildRunRecord | null => {
      if (payload.status === "idle") {
        if (!fallback?.runId) {
          return null;
        }
        const fallbackKey = buildRunStoreKey(fallback.projectRoot, fallback.target);
        let unavailable: StoredBuildRunRecord | null = null;
        updateRuns((current) => {
          const existing = current[fallbackKey];
          if (!existing || existing.runId !== fallback.runId) {
            return current;
          }
          unavailable = {
            ...existing,
            errorSummary: RUN_NO_LONGER_RETAINED_MESSAGE,
            progress: null,
            startAttemptToken: null,
            state: "failed"
          };
          return { ...current, [fallbackKey]: unavailable };
        });
        if (unavailable) {
          recordStatusError(fallback.projectRoot, fallback.runId, new Error(RUN_NO_LONGER_RETAINED_MESSAGE));
        }
        return unavailable;
      }
      const record = buildRunRecordFromPayload(payload, fallback, project ?? projectForBuildPayload(payload, projectsRef.current));
      if (!record) {
        return null;
      }
      const key = buildRunStoreKey(record.projectRoot, record.target);
      const successfulFullBuild = !record.target && record.state === "completed";
      const liveFullBuildCompletion =
        successfulFullBuild &&
        fallback !== null &&
        !fallback.target &&
        isCurrentObservedRunningBuildRun(runsRef.current, fallback);
      if (successfulFullBuild) {
        rememberFullBuildBaseline(record);
        const baseline = fullBuildBaselinesRef.current[record.projectRoot];
        for (const candidate of Object.values(runsRef.current)) {
          if (
            candidate.projectRoot === record.projectRoot &&
            candidate.runId &&
            isPartialSupersededByBaseline(candidate, baseline, liveFullBuildCompletion)
          ) {
            supersededPartialRunIdsRef.current.add(candidate.runId);
          }
        }
        trimSetToNewest(supersededPartialRunIdsRef.current, MAX_RETAINED_TERMINAL_IDENTITIES);
      }
      const supersededPartial = isSupersededPartialRecord(
        record,
        fullBuildBaselinesRef.current[record.projectRoot],
        supersededPartialRunIdsRef.current
      );
      const fallbackKey = fallback ? buildRunStoreKey(fallback.projectRoot, fallback.target) : null;
      const recoveryCandidate = fallback ? undefined : runsRef.current[key];
      const recoveredStartAttempt =
        recoveryCandidate?.runId === null &&
        recoveryCandidate.startAttemptToken !== null &&
        record.runId !== null &&
        record.state === "running"
          ? {
              projectRoot: recoveryCandidate.projectRoot,
              slotKey: key,
              token: recoveryCandidate.startAttemptToken
            }
          : null;
      updateRuns((current) => {
        const retained = successfulFullBuild
          ? removeProjectPartialRuns(
              current,
              record.projectRoot,
              fullBuildBaselinesRef.current[record.projectRoot],
              liveFullBuildCompletion
            )
          : current;
        if (supersededPartial) {
          return retained;
        }
        const existing = retained[key];
        const fallbackRecord = fallbackKey ? retained[fallbackKey] : undefined;
        const committed = mergeBuildRunRecord(existing, record, fallback);
        const next = { ...retained, [key]: committed };
        if (existing && existing.startAttemptToken !== null && committed !== existing && committed.startAttemptToken === null) {
          clearStartAttempt(latestStartAttemptByKeyRef.current, key, existing.startAttemptToken);
        }
        if (fallback && fallbackKey && fallbackKey !== key && fallbackRecord && sameBuildRun(fallbackRecord, fallback)) {
          delete next[fallbackKey];
          if (fallbackRecord.startAttemptToken !== null) {
            clearStartAttempt(latestStartAttemptByKeyRef.current, fallbackKey, fallbackRecord.startAttemptToken);
          }
        }
        return next;
      });
      if (recoveredStartAttempt) {
        clearStartError(
          recoveredStartAttempt.projectRoot,
          recoveredStartAttempt.slotKey,
          recoveredStartAttempt.token
        );
      }
      rememberTerminal(payload, record);
      return record;
    },
    [clearStartError, recordStatusError, rememberFullBuildBaseline, rememberTerminal, updateRuns]
  );

  const retryRecovery = useCallback(() => {
    setGlobalError(null);
    setRecoveryState(desktopBackend ? "loading" : "ready");
    setRecoveryRevision((current) => current + 1);
  }, [desktopBackend]);

  useEffect(() => {
    if (!desktopBackend) {
      setRecoveryState("ready");
      setGlobalError(null);
      return;
    }
    let cancelled = false;
    setRecoveryState("loading");
    getProjectBuildRuns()
      .then((payload) => {
        if (cancelled) {
          return;
        }
        const authoritativeRunIds = new Set(
          payload.runs
            .map((run) => run.runId)
            .filter((runId): runId is string => typeof runId === "string" && Boolean(runId.trim()))
        );
        const authoritativeSlotKeys = new Set(
          payload.runs.flatMap((run) =>
            run.status !== "idle" && run.projectRoot
              ? [buildRunStoreKey(run.projectRoot, run.target ?? null)]
              : []
          )
        );
        for (const run of payload.runs) {
          commitPayload(run);
        }
        const recoveredAtMs = Date.now();
        for (const [runId, checkpoint] of unreconciledRunningCheckpointsRef.current) {
          if (authoritativeRunIds.has(runId)) {
            continue;
          }
          const interrupted = closedBuildCheckpointPayload(checkpoint, recoveredAtMs);
          const checkpointKey = buildRunStoreKey(checkpoint.projectRoot, checkpoint.target);
          if (authoritativeSlotKeys.has(checkpointKey)) {
            const record = buildRunRecordFromPayload(interrupted, checkpoint, null);
            if (record) {
              rememberTerminal(interrupted, record);
            }
            continue;
          }
          commitPayload(interrupted, checkpoint);
        }
        unreconciledRunningCheckpointsRef.current.clear();
        statusErrorsByProjectRootRef.current.clear();
        setErrorsByProjectRoot((current) => removeBuildLifecycleErrors(current, "status"));
        setGlobalError(null);
        setRecoveryState("ready");
      })
      .catch((error: unknown) => {
        if (cancelled) {
          return;
        }
        setGlobalError(buildLifecycleError("status", null, error));
        setRecoveryState("failed");
      });
    return () => {
      cancelled = true;
    };
  }, [commitPayload, desktopBackend, projectSignature, recoveryRevision, rememberTerminal]);

  useEffect(() => {
    if (!desktopBackend || recoveryState !== "ready") {
      return;
    }
    let cancelled = false;
    let timer: number | null = null;
    const generation = statusPollGenerationRef.current + 1;
    statusPollGenerationRef.current = generation;

    const poll = () => {
      const active = Object.values(runsRef.current).filter(
        (run): run is StoredBuildRunRecord & { runId: string } => run.state === "running" && Boolean(run.runId)
      );
      for (const run of active) {
        if (inFlightStatusRef.current.has(run.runId)) {
          continue;
        }
        const token: StatusPollToken = {
          generation,
          request: statusPollRequestRef.current + 1
        };
        statusPollRequestRef.current = token.request;
        inFlightStatusRef.current.set(run.runId, token);
        void getProjectBuildStatus(run.runId)
          .then((payload) => {
            if (!cancelled && inFlightStatusRef.current.get(run.runId) === token) {
              commitPayload(payload, run);
              if (payload.status !== "idle") {
                clearStatusError(run.projectRoot, run.runId);
              }
            }
          })
          .catch((error: unknown) => {
            if (
              !cancelled &&
              inFlightStatusRef.current.get(run.runId) === token &&
              isCurrentRunningBuildRun(runsRef.current, run)
            ) {
              recordStatusError(run.projectRoot, run.runId, error);
            }
          })
          .finally(() => {
            if (inFlightStatusRef.current.get(run.runId) === token) {
              inFlightStatusRef.current.delete(run.runId);
            }
          });
      }
      if (!cancelled) {
        timer = window.setTimeout(poll, pollIntervalMs);
      }
    };

    timer = window.setTimeout(poll, 0);
    return () => {
      cancelled = true;
      if (timer !== null) {
        window.clearTimeout(timer);
      }
      for (const [runId, token] of inFlightStatusRef.current) {
        if (token.generation === generation) {
          inFlightStatusRef.current.delete(runId);
        }
      }
    };
  }, [clearStatusError, commitPayload, desktopBackend, pollIntervalMs, recordStatusError, recoveryState]);

  const clearError = useCallback((projectRoot: string, kind?: BuildLifecycleErrorKind, runId?: string | null) => {
    if (!kind) {
      startErrorsByProjectRootRef.current.delete(projectRoot);
      statusErrorsByProjectRootRef.current.delete(projectRoot);
    } else if (kind === "start") {
      startErrorsByProjectRootRef.current.delete(projectRoot);
    } else if (kind === "status") {
      removeStoredProjectStatusError(statusErrorsByProjectRootRef.current, projectRoot, runId ?? undefined);
    }
    setErrorsByProjectRoot((current) =>
      removeMatchingProjectLifecycleError(
        current,
        projectRoot,
        startErrorsByProjectRootRef.current,
        statusErrorsByProjectRootRef.current,
        kind,
        runId
      )
    );
  }, []);

  const start = useCallback(
    async (request: ProjectBuildRequest, project: ProjectOption): Promise<ProjectBuildRunPayload> => {
      if (recoveryState !== "ready") {
        throw new Error("Build run recovery must finish before a new build can start.");
      }
      const target = request.target ?? null;
      const attemptToken = nextStartAttemptTokenRef.current + 1;
      nextStartAttemptTokenRef.current = attemptToken;
      const optimistic: StoredBuildRunRecord = {
        mode: request.mode ?? "cached",
        progress: null,
        projectId: project.projectId || project.id,
        projectRoot: project.path,
        runId: null,
        startAttemptToken: attemptToken,
        startedAtMs: Date.now(),
        state: "running",
        target,
        terminalSequence: null
      };
      const key = buildRunStoreKey(optimistic.projectRoot, target);
      latestStartAttemptByKeyRef.current.set(key, attemptToken);
      clearStartError(optimistic.projectRoot, key);
      updateRuns((current) => ({ ...current, [key]: optimistic }));
      try {
        const payload = await startProjectBuild(request);
        commitPayload(payload, optimistic, project);
        return payload;
      } catch (error: unknown) {
        const current = runsRef.current[key];
        if (latestStartAttemptByKeyRef.current.get(key) !== attemptToken || !current || !sameBuildRun(current, optimistic)) {
          throw error;
        }
        clearStartAttempt(latestStartAttemptByKeyRef.current, key, attemptToken);
        updateRuns((currentRuns) => {
          const existing = currentRuns[key];
          if (!existing || !sameBuildRun(existing, optimistic)) {
            return currentRuns;
          }
          return {
            ...currentRuns,
            [key]: { ...existing, state: "failed" }
          };
        });
        recordStartError(optimistic.projectRoot, key, attemptToken, error);
        throw error;
      }
    },
    [clearStartError, commitPayload, recordStartError, recoveryState, updateRuns]
  );

  const interrupt = useCallback(
    async (runId: string): Promise<ProjectBuildRunPayload> => {
      const record = Object.values(runsRef.current).find((candidate) => candidate.runId === runId) ?? null;
      if (record) {
        clearError(record.projectRoot, "interrupt", runId);
      }
      try {
        const payload = await interruptProjectBuild(runId);
        commitPayload(payload, record);
        if (record && isTerminalBuildPayload(payload) && isCurrentBuildRun(runsRef.current, record)) {
          clearStatusError(record.projectRoot, runId);
        }
        return payload;
      } catch (error: unknown) {
        if (record) {
          setErrorsByProjectRoot((current) => ({
            ...current,
            [record.projectRoot]: buildLifecycleError("interrupt", record.projectRoot, error, runId)
          }));
        }
        throw error;
      }
    },
    [clearError, clearStatusError, commitPayload]
  );

  const removeHistory = useCallback((id: string) => {
    const nextHistory = removeBuildHistoryEntry(id);
    setHistory(nextHistory);
    historyTombstonesRef.current = new Set(readBuildHistoryTombstones());
    syncHistoryTracking(nextHistory, historyTombstonesRef.current);
  }, [syncHistoryTracking]);

  const runs = useMemo(
    () => effectiveBuildRuns(Object.values(runsByKey), fullBuildBaselinesByProjectRoot).sort(compareBuildRunRecords),
    [fullBuildBaselinesByProjectRoot, runsByKey]
  );

  return useMemo(
    () => ({
      clearError,
      errorsByProjectRoot,
      fullBuildBaselines: fullBuildBaselinesByProjectRoot,
      globalError,
      history,
      interrupt,
      recoveryState,
      removeHistory,
      retryRecovery,
      runs,
      start
    }),
    [
      clearError,
      errorsByProjectRoot,
      fullBuildBaselinesByProjectRoot,
      globalError,
      history,
      interrupt,
      recoveryState,
      removeHistory,
      retryRecovery,
      runs,
      start
    ]
  );
}

export function buildRunsForProject(runs: readonly BuildRunRecord[], projectRoot: string): BuildRunRecord[] {
  return runs.filter((run) => run.projectRoot === projectRoot);
}

/**
 * Removes partial-slot state that predates the latest successful full build.
 *
 * Terminal sequence is the authoritative chronology within one native
 * registry lifetime; timestamps are only a compatibility fallback. Build
 * history remains intact even when an old partial slot is hidden from current
 * project state.
 */
export function effectiveBuildRuns(
  runs: readonly BuildRunRecord[],
  retainedBaselines: Readonly<Record<string, FullBuildBaseline>> = {}
): BuildRunRecord[] {
  const baselines = deriveFullBuildBaselines(runs, retainedBaselines);
  return runs.filter((run) => {
    if (!run.target) {
      return true;
    }
    const baseline = baselines[run.projectRoot];
    if (!baseline || run.state === "running" || run.runId === null) {
      return true;
    }
    if (run.terminalSequence !== null && run.terminalSequence !== undefined && baseline.terminalSequence !== null) {
      return run.terminalSequence > baseline.terminalSequence;
    }
    const partialAtMs = run.finishedAtMs ?? run.startedAtMs;
    return baseline.finishedAtMs === null || partialAtMs === null || partialAtMs >= baseline.finishedAtMs;
  });
}

function deriveFullBuildBaselines(
  runs: readonly BuildRunRecord[],
  retainedBaselines: Readonly<Record<string, FullBuildBaseline>>
): Record<string, FullBuildBaseline> {
  const baselines = { ...retainedBaselines };
  for (const run of runs) {
    if (run.target || run.state !== "completed") {
      continue;
    }
    const candidate: FullBuildBaseline = {
      finishedAtMs: run.finishedAtMs ?? run.startedAtMs,
      terminalSequence: run.terminalSequence ?? null
    };
    const current = baselines[run.projectRoot];
    if (!current || compareFullBuildBaselines(candidate, current) > 0) {
      baselines[run.projectRoot] = candidate;
    }
  }
  return baselines;
}

function compareFullBuildBaselines(left: FullBuildBaseline, right: FullBuildBaseline): number {
  if (left.terminalSequence !== null && right.terminalSequence !== null) {
    return left.terminalSequence - right.terminalSequence;
  }
  if (left.terminalSequence !== null) {
    return 1;
  }
  if (right.terminalSequence !== null) {
    return -1;
  }
  return (left.finishedAtMs ?? -1) - (right.finishedAtMs ?? -1);
}

function pruneFullBuildBaselines(
  baselines: Readonly<Record<string, FullBuildBaseline>>
): Record<string, FullBuildBaseline> {
  const entries = Object.entries(baselines);
  if (entries.length <= MAX_RETAINED_FULL_BUILD_BASELINES) {
    return { ...baselines };
  }
  entries.sort(([, left], [, right]) => compareFullBuildBaselines(right, left));
  return Object.fromEntries(entries.slice(0, MAX_RETAINED_FULL_BUILD_BASELINES));
}

function removeProjectPartialRuns(
  store: BuildRunStore,
  projectRoot: string,
  baseline: FullBuildBaseline | undefined,
  includeObservedRunning: boolean
): BuildRunStore {
  const next = Object.fromEntries(
    Object.entries(store).filter(
      ([, run]) =>
        run.projectRoot !== projectRoot ||
        !isPartialSupersededByBaseline(run, baseline, includeObservedRunning)
    )
  );
  return Object.keys(next).length === Object.keys(store).length ? store : next;
}

function isPartialSupersededByBaseline(
  record: StoredBuildRunRecord,
  baseline: FullBuildBaseline | undefined,
  includeObservedRunning = false
): boolean {
  if (!record.target || !baseline) {
    return false;
  }
  if (record.state === "running" || record.runId === null) {
    return includeObservedRunning;
  }
  if (record.terminalSequence !== null && record.terminalSequence !== undefined && baseline.terminalSequence !== null) {
    return record.terminalSequence <= baseline.terminalSequence;
  }
  const terminalAtMs = record.finishedAtMs ?? record.startedAtMs;
  return baseline.finishedAtMs !== null && terminalAtMs !== null && terminalAtMs < baseline.finishedAtMs;
}

function isSupersededPartialRecord(
  record: StoredBuildRunRecord,
  baseline: FullBuildBaseline | undefined,
  supersededRunIds: ReadonlySet<string>
): boolean {
  if (!record.target) {
    return false;
  }
  if (record.runId && supersededRunIds.has(record.runId)) {
    return true;
  }
  if (!baseline || record.state === "running" || record.runId === null) {
    return false;
  }
  return isPartialSupersededByBaseline(record, baseline);
}

function buildRunRecordFromPayload(
  payload: ProjectBuildRunPayload,
  fallback: StoredBuildRunRecord | null,
  project: ProjectOption | null
): StoredBuildRunRecord | null {
  if (payload.status === "idle") {
    return null;
  }
  const projectRoot = payload.projectRoot ?? fallback?.projectRoot ?? project?.path ?? "";
  if (!projectRoot) {
    return null;
  }
  const mode: BuildMode = payload.mode ?? fallback?.mode ?? "cached";
  const target = payload.target ?? fallback?.target ?? null;
  const base: StoredBuildRunRecord = {
    errorSummary: payload.errorSummary ?? fallback?.errorSummary ?? null,
    finishedAtMs: payload.finishedAtMs ?? fallback?.finishedAtMs ?? null,
    mode,
    progress: payload.progress ?? fallback?.progress ?? null,
    projectId: fallback?.projectId ?? project?.projectId ?? project?.id ?? projectRoot,
    projectRoot,
    runId: payload.runId ?? fallback?.runId ?? null,
    startAttemptToken: null,
    startedAtMs: payload.startedAtMs ?? fallback?.startedAtMs ?? null,
    state: payload.status,
    target,
    terminalSequence: payload.terminalSequence ?? fallback?.terminalSequence ?? null
  };
  if (payload.status === "completed" && !base.progress) {
    return {
      ...base,
      progress: { label: "Complete", percent: 100, phase: "complete" }
    };
  }
  return base;
}

function projectForBuildPayload(payload: ProjectBuildRunPayload, projects: readonly ProjectOption[]): ProjectOption | null {
  if (!payload.projectRoot) {
    return null;
  }
  return projects.find((project) => project.path === payload.projectRoot) ?? null;
}

function buildHistoryEntryFromPayload(payload: ProjectBuildRunPayload, record: BuildRunRecord): BuildHistoryEntry | null {
  if (!isTerminalBuildPayload(payload)) {
    return null;
  }
  const startedAtMs = payload.startedAtMs ?? record.startedAtMs;
  const finishedAtMs = payload.finishedAtMs ?? null;
  if (!startedAtMs || !finishedAtMs || finishedAtMs <= startedAtMs) {
    return null;
  }
  return {
    ...(payload.command?.length ? { command: payload.command } : {}),
    durationMs: finishedAtMs - startedAtMs,
    ...(payload.errorPath ? { errorPath: payload.errorPath } : {}),
    ...(payload.errorSummary ? { errorSummary: payload.errorSummary } : {}),
    ...(typeof payload.exitCode === "number" ? { exitCode: payload.exitCode } : {}),
    finishedAtMs,
    id: payload.runId ?? `${record.projectId}:${startedAtMs}:${finishedAtMs}`,
    mode: payload.mode ?? record.mode,
    ...(payload.outputPath ? { outputPath: payload.outputPath } : {}),
    projectId: record.projectId,
    projectRoot: record.projectRoot,
    startedAtMs,
    status: payload.status,
    target: payload.target ?? record.target ?? null
  };
}

function isTerminalBuildPayload(
  payload: ProjectBuildRunPayload
): payload is ProjectBuildRunPayload & { status: "completed" | "failed" | "interrupted" } {
  return isTerminalBuildState(payload.status);
}

function isTerminalBuildState(state: BuildRuntime["state"]): state is "completed" | "failed" | "interrupted" {
  return state === "completed" || state === "failed" || state === "interrupted";
}

function buildRunStoreKey(projectRoot: string, target: BuildTarget | null | undefined): string {
  return `${projectRoot}\u0000${buildTargetKey(target ?? null)}`;
}

function compareBuildRunRecords(left: BuildRunRecord, right: BuildRunRecord): number {
  return (left.startedAtMs ?? 0) - (right.startedAtMs ?? 0) || (left.runId ?? "").localeCompare(right.runId ?? "");
}

function mergeBuildRunRecord(
  existing: StoredBuildRunRecord | undefined,
  incoming: StoredBuildRunRecord,
  fallback: StoredBuildRunRecord | null
): StoredBuildRunRecord {
  if (!existing) {
    return incoming;
  }
  if (sameBuildRun(existing, incoming)) {
    if (isTerminalBuildState(existing.state) && !isTerminalBuildState(incoming.state)) {
      return existing;
    }
    return incoming.startedAtMs === null && existing.startedAtMs !== null
      ? { ...incoming, startedAtMs: existing.startedAtMs }
      : incoming;
  }
  if (!fallback && existing.runId === null && incoming.runId !== null) {
    return incoming.state === "running" ? incoming : existing;
  }
  if (
    existing.runId !== null &&
    incoming.runId !== null &&
    existing.runId !== incoming.runId
  ) {
    if (existing.state === "running" && isTerminalBuildState(incoming.state)) {
      return existing;
    }
    if (incoming.state === "running" && isTerminalBuildState(existing.state)) {
      return incoming;
    }
    if (
      isTerminalBuildState(existing.state) &&
      isTerminalBuildState(incoming.state) &&
      existing.terminalSequence !== null &&
      existing.terminalSequence !== undefined &&
      incoming.terminalSequence !== null &&
      incoming.terminalSequence !== undefined
    ) {
      return incoming.terminalSequence > existing.terminalSequence ? incoming : existing;
    }
  }
  if (fallback && incoming.runId !== null && existing.runId === null) {
    return incoming;
  }
  if (fallback) {
    return sameBuildRun(existing, fallback) ? incoming : existing;
  }
  if (incoming.startedAtMs === null) {
    return existing;
  }
  if (existing.startedAtMs === null) {
    return incoming;
  }
  return compareBuildRunRecords(incoming, existing) > 0 ? incoming : existing;
}

function sameBuildRun(left: StoredBuildRunRecord, right: StoredBuildRunRecord): boolean {
  if (left.runId !== null || right.runId !== null) {
    return left.runId !== null && left.runId === right.runId;
  }
  if (left.startAttemptToken !== null || right.startAttemptToken !== null) {
    return left.startAttemptToken !== null && left.startAttemptToken === right.startAttemptToken;
  }
  return left.startedAtMs !== null && left.startedAtMs === right.startedAtMs;
}

function buildLifecycleError(
  kind: BuildLifecycleErrorKind,
  projectRoot: string | null,
  error: unknown,
  runId?: string | null
): BuildLifecycleError {
  return {
    kind,
    message: error instanceof Error ? error.message : String(error),
    projectRoot,
    ...(runId === undefined ? {} : { runId })
  };
}

function removeRecordKey<T>(record: Readonly<Record<string, T>>, key: string): Record<string, T> {
  if (!(key in record)) {
    return record;
  }
  const next = { ...record };
  delete next[key];
  return next;
}

function removeBuildLifecycleErrors(
  errors: Readonly<Record<string, BuildLifecycleError>>,
  kind: BuildLifecycleErrorKind
): Record<string, BuildLifecycleError> {
  return Object.fromEntries(Object.entries(errors).filter(([, error]) => error.kind !== kind));
}

function putProjectStatusError(
  statusErrorsByProjectRoot: StatusErrorsByProjectRoot,
  projectRoot: string,
  runId: string,
  error: BuildLifecycleError
): void {
  const projectErrors = statusErrorsByProjectRoot.get(projectRoot) ?? new Map<string, BuildLifecycleError>();
  projectErrors.delete(runId);
  projectErrors.set(runId, error);
  statusErrorsByProjectRoot.set(projectRoot, projectErrors);
}

function removeStoredProjectStatusError(
  statusErrorsByProjectRoot: StatusErrorsByProjectRoot,
  projectRoot: string,
  runId?: string
): void {
  if (runId === undefined) {
    statusErrorsByProjectRoot.delete(projectRoot);
    return;
  }
  const projectErrors = statusErrorsByProjectRoot.get(projectRoot);
  if (!projectErrors) {
    return;
  }
  projectErrors.delete(runId);
  if (projectErrors.size === 0) {
    statusErrorsByProjectRoot.delete(projectRoot);
  }
}

function putProjectStartError(
  startErrorsByProjectRoot: StartErrorsByProjectRoot,
  projectRoot: string,
  slotKey: string,
  error: BuildLifecycleError
): void {
  const projectErrors = startErrorsByProjectRoot.get(projectRoot) ?? new Map<string, BuildLifecycleError>();
  projectErrors.delete(slotKey);
  projectErrors.set(slotKey, error);
  startErrorsByProjectRoot.set(projectRoot, projectErrors);
}

function removeStoredProjectStartError(
  startErrorsByProjectRoot: StartErrorsByProjectRoot,
  projectRoot: string,
  slotKey: string,
  startAttemptToken?: number
): void {
  const projectErrors = startErrorsByProjectRoot.get(projectRoot);
  const current = projectErrors?.get(slotKey);
  if (!projectErrors || !current || (startAttemptToken !== undefined && current.startAttemptToken !== startAttemptToken)) {
    return;
  }
  projectErrors.delete(slotKey);
  if (projectErrors.size === 0) {
    startErrorsByProjectRoot.delete(projectRoot);
  }
}

function reconcileProjectOwnedError(
  errors: Readonly<Record<string, BuildLifecycleError>>,
  projectRoot: string,
  startErrorsByProjectRoot: StartErrorsByProjectRoot,
  statusErrorsByProjectRoot: StatusErrorsByProjectRoot
): Record<string, BuildLifecycleError> {
  const current = errors[projectRoot];
  if (current && current.kind !== "start" && current.kind !== "status") {
    return errors;
  }
  const latest =
    latestProjectStartError(startErrorsByProjectRoot, projectRoot) ??
    latestProjectStatusError(statusErrorsByProjectRoot, projectRoot);
  if (!latest) {
    return removeRecordKey(errors, projectRoot);
  }
  if (current === latest) {
    return errors;
  }
  return {
    ...errors,
    [projectRoot]: latest
  };
}

function latestProjectStartError(
  startErrorsByProjectRoot: StartErrorsByProjectRoot,
  projectRoot: string
): BuildLifecycleError | null {
  const projectErrors = startErrorsByProjectRoot.get(projectRoot);
  if (!projectErrors || projectErrors.size === 0) {
    return null;
  }
  return [...projectErrors.values()].at(-1) ?? null;
}

function latestProjectStatusError(
  statusErrorsByProjectRoot: StatusErrorsByProjectRoot,
  projectRoot: string
): BuildLifecycleError | null {
  const projectErrors = statusErrorsByProjectRoot.get(projectRoot);
  if (!projectErrors || projectErrors.size === 0) {
    return null;
  }
  return [...projectErrors.values()].at(-1) ?? null;
}

function removeMatchingProjectLifecycleError(
  errors: Readonly<Record<string, BuildLifecycleError>>,
  projectRoot: string,
  startErrorsByProjectRoot: StartErrorsByProjectRoot,
  statusErrorsByProjectRoot: StatusErrorsByProjectRoot,
  kind?: BuildLifecycleErrorKind,
  runId?: string | null
): Record<string, BuildLifecycleError> {
  const current = errors[projectRoot];
  if (!current || (kind && current.kind !== kind) || (runId !== undefined && current.runId !== runId)) {
    return errors;
  }
  const withoutCurrent = removeRecordKey(errors, projectRoot);
  const latestOwned =
    latestProjectStartError(startErrorsByProjectRoot, projectRoot) ??
    latestProjectStatusError(statusErrorsByProjectRoot, projectRoot);
  return latestOwned ? { ...withoutCurrent, [projectRoot]: latestOwned } : withoutCurrent;
}

function readBuildRunCheckpoints(storage: Storage | null = buildRunCheckpointStorage()): BuildRunStore {
  if (!storage) {
    return {};
  }
  try {
    const raw = storage.getItem(BUILD_RUN_CHECKPOINT_STORAGE_KEY);
    if (!raw) {
      return {};
    }
    const parsed: unknown = JSON.parse(raw);
    if (!Array.isArray(parsed)) {
      return {};
    }
    const store: BuildRunStore = {};
    for (const value of parsed) {
      const checkpoint = parseBuildRunCheckpoint(value);
      if (!checkpoint) {
        continue;
      }
      const key = buildRunStoreKey(checkpoint.projectRoot, checkpoint.target);
      const existing = store[key];
      if (!existing || compareBuildRunCheckpointRecency(checkpoint, existing) >= 0) {
        store[key] = checkpoint;
      }
    }
    return buildRunCheckpointStore(Object.values(store));
  } catch {
    return {};
  }
}

function writeBuildRunCheckpoints(store: BuildRunStore, storage: Storage | null = buildRunCheckpointStorage()): void {
  if (!storage) {
    return;
  }
  const checkpoints = retainedBuildRunCheckpoints(Object.values(store)).map(buildRunCheckpointFromRecord);
  try {
    storage.setItem(BUILD_RUN_CHECKPOINT_STORAGE_KEY, JSON.stringify(checkpoints));
  } catch {
    // Renderer storage is best-effort presentation state; native process ownership remains authoritative.
  }
}

function buildRunCheckpointStorage(): Storage | null {
  try {
    return typeof window === "undefined" ? null : window.localStorage;
  } catch {
    return null;
  }
}

function buildRunCheckpointFromRecord(record: StoredBuildRunRecord): BuildRunCheckpoint {
  return {
    errorSummary: record.errorSummary ?? null,
    finishedAtMs: record.finishedAtMs ?? null,
    mode: record.mode,
    progress: record.progress,
    projectId: record.projectId,
    projectRoot: record.projectRoot,
    runId: record.runId,
    startedAtMs: record.startedAtMs,
    state: record.state,
    target: record.target ?? null
  };
}

function buildRunCheckpointStore(records: readonly StoredBuildRunRecord[]): BuildRunStore {
  return Object.fromEntries(
    retainedBuildRunCheckpoints(records).map((record) => [
      buildRunStoreKey(record.projectRoot, record.target),
      record
    ])
  );
}

function retainedBuildRunCheckpoints(records: readonly StoredBuildRunRecord[]): StoredBuildRunRecord[] {
  const concrete = records.filter((record): record is StoredBuildRunRecord & { runId: string } => Boolean(record.runId));
  const running = concrete
    .filter((record) => record.state === "running")
    .sort(compareBuildRunCheckpointRecency);
  if (running.length >= MAX_RETAINED_BUILD_RUN_CHECKPOINTS) {
    return running.slice(-MAX_RETAINED_BUILD_RUN_CHECKPOINTS);
  }
  const terminal = concrete
    .filter((record) => record.state !== "running")
    .sort(compareBuildRunCheckpointRecency)
    .slice(-(MAX_RETAINED_BUILD_RUN_CHECKPOINTS - running.length));
  return [...terminal, ...running].sort(compareBuildRunCheckpointRecency);
}

function compareBuildRunCheckpointRecency(left: BuildRunRecord, right: BuildRunRecord): number {
  const leftAtMs = left.finishedAtMs ?? left.startedAtMs ?? -1;
  const rightAtMs = right.finishedAtMs ?? right.startedAtMs ?? -1;
  return leftAtMs - rightAtMs || (left.runId ?? "").localeCompare(right.runId ?? "");
}

function parseBuildRunCheckpoint(value: unknown): StoredBuildRunRecord | null {
  if (!isUnknownRecord(value)) {
    return null;
  }
  const projectId = checkpointText(value.projectId);
  const projectRoot = checkpointText(value.projectRoot);
  const runId = checkpointText(value.runId);
  const mode = value.mode === "cached" || value.mode === "full" ? value.mode : null;
  const state = isCheckpointBuildState(value.state) ? value.state : null;
  const startedAtMs = checkpointNumber(value.startedAtMs);
  const finishedAtMs = checkpointNullableNumber(value.finishedAtMs);
  const progress = parseBuildRunCheckpointProgress(value.progress);
  const target = parseBuildRunCheckpointTarget(value.target);
  if (
    !projectId ||
    !projectRoot ||
    !runId ||
    !mode ||
    !state ||
    startedAtMs === null ||
    finishedAtMs === undefined ||
    progress === undefined ||
    target === undefined
  ) {
    return null;
  }
  if (value.errorSummary !== undefined && value.errorSummary !== null && typeof value.errorSummary !== "string") {
    return null;
  }
  return {
    errorSummary: typeof value.errorSummary === "string" ? value.errorSummary : null,
    finishedAtMs,
    mode,
    progress,
    projectId,
    projectRoot,
    runId,
    startAttemptToken: null,
    startedAtMs,
    state,
    target,
    terminalSequence: null
  };
}

function parseBuildRunCheckpointProgress(value: unknown): BuildRunRecord["progress"] | undefined {
  if (value === undefined || value === null) {
    return null;
  }
  if (!isUnknownRecord(value)) {
    return undefined;
  }
  const phase = checkpointText(value.phase);
  if (!phase) {
    return undefined;
  }
  const current = checkpointNullableText(value.current);
  const detail = checkpointNullableText(value.detail);
  const index = checkpointNullableNumber(value.index);
  const label = checkpointNullableText(value.label);
  const percent = checkpointNullableNumber(value.percent);
  const total = checkpointNullableNumber(value.total);
  if ([current, detail, index, label, percent, total].some((field) => field === undefined)) {
    return undefined;
  }
  return { current, detail, index, label, percent, phase, total };
}

function parseBuildRunCheckpointTarget(value: unknown): BuildTarget | null | undefined {
  if (value === undefined || value === null) {
    return null;
  }
  if (!isUnknownRecord(value)) {
    return undefined;
  }
  const id = checkpointText(value.id);
  const kind = value.kind;
  const family = checkpointNullableText(value.family);
  if (!id || (kind !== "module" && kind !== "collection" && kind !== "family") || family === undefined) {
    return undefined;
  }
  return { family, id, kind };
}

function checkpointText(value: unknown): string | null {
  return typeof value === "string" && Boolean(value.trim()) ? value : null;
}

function checkpointNullableText(value: unknown): string | null | undefined {
  return value === undefined || value === null ? null : typeof value === "string" ? value : undefined;
}

function checkpointNumber(value: unknown): number | null {
  return typeof value === "number" && Number.isFinite(value) && value >= 0 ? value : null;
}

function checkpointNullableNumber(value: unknown): number | null | undefined {
  return value === undefined || value === null ? null : checkpointNumber(value) ?? undefined;
}

function isCheckpointBuildState(value: unknown): value is Exclude<BuildRuntime["state"], "idle"> {
  return value === "running" || value === "interrupted" || value === "completed" || value === "failed";
}

function isUnknownRecord(value: unknown): value is Record<string, unknown> {
  return Boolean(value) && typeof value === "object" && !Array.isArray(value);
}

function closedBuildCheckpointPayload(
  checkpoint: StoredBuildRunRecord & { runId: string },
  recoveredAtMs: number
): ProjectBuildRunPayload {
  return {
    errorSummary: CLOSED_BUILD_RECOVERY_MESSAGE,
    finishedAtMs: Math.max(recoveredAtMs, (checkpoint.startedAtMs ?? 0) + 1),
    mode: checkpoint.mode,
    progress: checkpoint.progress,
    projectRoot: checkpoint.projectRoot,
    runId: checkpoint.runId,
    schema: "paradev.desktop.build-run.v1",
    startedAtMs: checkpoint.startedAtMs ?? undefined,
    status: "interrupted",
    target: checkpoint.target ?? null
  };
}

function buildHistoryProjectIdentity(entry: BuildHistoryEntry): string {
  return `${entry.projectRoot}\u0000${entry.projectId}`;
}

function trimSetToNewest(values: Set<string>, limit: number): void {
  while (values.size > limit) {
    const oldest = values.values().next().value as string | undefined;
    if (oldest === undefined) {
      return;
    }
    values.delete(oldest);
  }
}

function pruneBuildRunStore(store: BuildRunStore): BuildRunStore {
  const terminal = Object.entries(store)
    .filter(([, run]) => isTerminalBuildState(run.state))
    .sort(([, left], [, right]) => compareTerminalBuildRunRecords(left, right));
  const removeCount = terminal.length - MAX_RETAINED_TERMINAL_BUILD_RUNS;
  if (removeCount <= 0) {
    return store;
  }
  const next = { ...store };
  for (const [key] of terminal.slice(0, removeCount)) {
    delete next[key];
  }
  return next;
}

function compareTerminalBuildRunRecords(left: BuildRunRecord, right: BuildRunRecord): number {
  if (
    left.terminalSequence !== null &&
    left.terminalSequence !== undefined &&
    right.terminalSequence !== null &&
    right.terminalSequence !== undefined
  ) {
    return left.terminalSequence - right.terminalSequence;
  }
  if (left.terminalSequence !== null && left.terminalSequence !== undefined) {
    return 1;
  }
  if (right.terminalSequence !== null && right.terminalSequence !== undefined) {
    return -1;
  }
  return compareBuildRunRecords(left, right);
}

function pruneStatusErrorsToRetainedRuns(
  statusErrorsByProjectRoot: StatusErrorsByProjectRoot,
  store: BuildRunStore
): string[] {
  const retainedRunIdsByProject = new Map<string, Set<string>>();
  for (const run of Object.values(store)) {
    if (!run.runId) {
      continue;
    }
    const retained = retainedRunIdsByProject.get(run.projectRoot) ?? new Set<string>();
    retained.add(run.runId);
    retainedRunIdsByProject.set(run.projectRoot, retained);
  }
  const changedProjects: string[] = [];
  for (const [projectRoot, errorsByRunId] of statusErrorsByProjectRoot) {
    const retained = retainedRunIdsByProject.get(projectRoot);
    let changed = false;
    for (const runId of errorsByRunId.keys()) {
      if (!retained?.has(runId)) {
        errorsByRunId.delete(runId);
        changed = true;
      }
    }
    if (errorsByRunId.size === 0) {
      statusErrorsByProjectRoot.delete(projectRoot);
    }
    if (changed) {
      changedProjects.push(projectRoot);
    }
  }
  return changedProjects;
}

function pruneStartErrorsToRetainedAttempts(
  startErrorsByProjectRoot: StartErrorsByProjectRoot,
  store: BuildRunStore
): string[] {
  const changedProjects: string[] = [];
  for (const [projectRoot, errorsBySlotKey] of startErrorsByProjectRoot) {
    let changed = false;
    for (const [slotKey, error] of errorsBySlotKey) {
      const retained = store[slotKey];
      if (
        !retained ||
        retained.projectRoot !== projectRoot ||
        retained.runId !== null ||
        retained.startAttemptToken !== error.startAttemptToken
      ) {
        errorsBySlotKey.delete(slotKey);
        changed = true;
      }
    }
    if (errorsBySlotKey.size === 0) {
      startErrorsByProjectRoot.delete(projectRoot);
    }
    if (changed) {
      changedProjects.push(projectRoot);
    }
  }
  return changedProjects;
}

function isCurrentBuildRun(store: BuildRunStore, run: StoredBuildRunRecord): boolean {
  const current = store[buildRunStoreKey(run.projectRoot, run.target)];
  return run.runId !== null && current?.runId === run.runId;
}

function isCurrentObservedRunningBuildRun(store: BuildRunStore, run: StoredBuildRunRecord): boolean {
  const current = store[buildRunStoreKey(run.projectRoot, run.target)];
  return current?.state === "running" && sameBuildRun(current, run);
}

function isCurrentRunningBuildRun(store: BuildRunStore, run: StoredBuildRunRecord & { runId: string }): boolean {
  return isCurrentBuildRun(store, run) && store[buildRunStoreKey(run.projectRoot, run.target)]?.state === "running";
}

function clearStartAttempt(attempts: Map<string, number>, key: string, token: number): void {
  if (attempts.get(key) === token) {
    attempts.delete(key);
  }
}
