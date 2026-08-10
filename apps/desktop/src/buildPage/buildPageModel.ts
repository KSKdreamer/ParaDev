import { DESKTOP_CONFIG_KEYS, desktopConfigChoices, desktopConfigDefault, desktopConfigMinimum, type DesktopConfigKey } from "../desktopConfig";
import type { TranslationKey } from "../i18n";
import { canonicalFamilyId, moduleTitleKeyForFamily, projectBrowserFamily } from "../projectModules";
import type { ProjectBrowserFamily, ProjectBrowserItem, ProjectBrowserPayload, ProjectOption } from "../types";

export type BuildMode = "cached" | "full";
export type Hoi4LaunchMode = "steam" | "local";
export type BuildRunState = "idle" | "running" | "interrupted" | "completed" | "failed";
export type BuildRuntimeCommand = "start" | "interrupt" | "complete";
export type BuildTargetKind = "module" | "collection" | "family";

export type BuildTarget = {
  family?: string | null;
  id: string;
  kind: BuildTargetKind;
};

export type BuildTargetIntent = {
  nonce: number;
  projectRoot: string;
  target: BuildTarget;
};

export type BuildProgressSnapshot = {
  current?: string | null;
  detail?: string | null;
  index?: number | null;
  label?: string | null;
  percent?: number | null;
  phase: string;
  total?: number | null;
};

export type BuildRuntime = {
  errorSummary?: string | null;
  finishedAtMs?: number | null;
  mode: BuildMode;
  progress: BuildProgressSnapshot | null;
  runId?: string | null;
  startedAtMs?: number | null;
  state: BuildRunState;
  target?: BuildTarget | null;
  terminalSequence?: number | null;
};

export type BuildDashboardInput = {
  buildDiagnostics?: ReadonlyArray<Record<string, unknown>> | null;
  browser: ProjectBrowserPayload | null;
  history?: readonly BuildHistoryEntry[];
  mode: BuildMode;
  project: ProjectOption;
  runtime: BuildRuntime;
  runtimes?: readonly BuildRuntime[];
};

export type BuildDashboardSummary = {
  blocked: boolean;
  buildableEntityCount: number;
  collectionCount: number;
  diagnosticCount: number;
  errorCount: number;
  moduleCount: number;
  sourceCount: number;
  warningCount: number;
};

export type BuildEntityRow = {
  detail: string;
  family: string;
  id: string;
  kind: BuildTargetKind;
  moduleCount: number;
  familyTitleKey?: TranslationKey;
  progressLabel: string;
  progressCurrent: number;
  progressPercent: number;
  progressTotal: number;
  relativeRoot: string;
  sourceCount: number;
  sourceSlotCount: number;
  status: "ready" | "blocked" | "failed" | "interrupted";
  target: BuildTarget;
  title: string;
  titleKey?: TranslationKey;
};

export type BuildProgressDisplay = {
  countLabel: string;
  detail: string;
  label: string;
  percent: number;
  phase: string;
};

export type BuildHistoryStatus = Extract<BuildRunState, "completed" | "failed" | "interrupted">;

export type BuildPartialResult = {
  durationMs: number | null;
  finishedAtMs: number | null;
  state: BuildHistoryStatus;
  target: BuildTarget;
};

export type BuildHistoryEntry = {
  command?: string[];
  durationMs: number;
  errorPath?: string;
  errorSummary?: string;
  exitCode?: number;
  finishedAtMs: number;
  id: string;
  mode: BuildMode;
  outputPath?: string;
  projectId: string;
  projectRoot: string;
  startedAtMs: number;
  status: BuildHistoryStatus;
  target?: BuildTarget | null;
};

export type BuildEstimateDisplay = {
  durationLabel: string;
  durationMs: number | null;
  sampleCount: number;
};

export type BuildDashboardModel = {
  entities: BuildEntityRow[];
  estimate: BuildEstimateDisplay;
  latestPartialResult: BuildPartialResult | null;
  progress: BuildProgressDisplay;
  projectId: string;
  status: {
    detail: string;
    label: string;
    progress: number;
    state: BuildRunState | "blocked" | "ready";
  };
  summary: BuildDashboardSummary;
};

export type BuildPageSettings = {
  buildMode: BuildMode;
  launchMode: Hoi4LaunchMode;
  parallelism: number;
  strictMetadata: boolean;
};

export const BUILD_RUN_FULL_KEY = "full";

const BUILD_MODE_STORAGE_KEY = "paradev.build.mode";
const BUILD_STRICT_METADATA_STORAGE_KEY = "paradev.build.strictMetadata";
const LEGACY_LAUNCH_MODE_STORAGE_KEY = "paradev.build.launchMode";
const BUILD_HISTORY_STORAGE_KEY = "paradev.build.history.v2";
const BUILD_HISTORY_TOMBSTONES_STORAGE_KEY = "paradev.build.history-tombstones.v1";
const BUILD_HISTORY_LIMIT = 256;
const BUILD_HISTORY_TOMBSTONE_LIMIT = 512;
export const BUILD_HOI4_LAUNCH_MODE_VALUES = desktopConfigChoices(DESKTOP_CONFIG_KEYS.hoi4LaunchMode) as readonly Hoi4LaunchMode[];
export const BUILD_PARALLELISM_MIN = desktopConfigMinimum(DESKTOP_CONFIG_KEYS.buildParallelism);
const DEFAULT_SETTINGS: BuildPageSettings = {
  buildMode: "cached",
  launchMode: desktopChoiceDefault(DESKTOP_CONFIG_KEYS.hoi4LaunchMode, BUILD_HOI4_LAUNCH_MODE_VALUES),
  parallelism: desktopNumberDefault(DESKTOP_CONFIG_KEYS.buildParallelism, BUILD_PARALLELISM_MIN),
  strictMetadata: desktopBooleanDefault(DESKTOP_CONFIG_KEYS.buildStrictMetadata)
};

function desktopNumberDefault(key: DesktopConfigKey, fallback: number): number {
  const value = desktopConfigDefault(key);
  return typeof value === "number" && Number.isFinite(value) ? Math.round(value) : fallback;
}

function desktopBooleanDefault(key: DesktopConfigKey): boolean {
  const value: unknown = desktopConfigDefault(key);
  return typeof value === "boolean" ? value : false;
}

function desktopChoiceDefault<T extends string>(key: DesktopConfigKey, choices: readonly T[]): T {
  const value = desktopConfigDefault(key);
  return typeof value === "string" && choices.includes(value as T) ? (value as T) : choices[0];
}

export function buildBuildDashboardModel({ browser, buildDiagnostics, history = [], mode, project, runtime, runtimes }: BuildDashboardInput): BuildDashboardModel {
  const projectId = project.projectId || project.id;
  const diagnosticCounts = buildDiagnosticCounts(buildDiagnostics ?? browser?.diagnostics ?? []);
  const runtimeRows = runtimes ?? [runtime];
  const entities = buildEntityRows(browser, diagnosticCounts.errorCount > 0, runtimeRows);
  const summary: BuildDashboardSummary = {
    blocked: diagnosticCounts.errorCount > 0,
    buildableEntityCount: entities.length,
    collectionCount: buildCollectionCount(browser),
    diagnosticCount: diagnosticCounts.diagnosticCount,
    errorCount: diagnosticCounts.errorCount,
    moduleCount: buildModuleCount(browser),
    sourceCount: buildSourceCount(browser),
    warningCount: diagnosticCounts.warningCount
  };
  const progress = buildProgressDisplay(runtime.progress, runtime.state);
  const estimate = buildEstimateDisplay(history, project.path, mode, runtime, runtimeRows);

  return {
    entities,
    estimate,
    latestPartialResult: latestPartialBuildResult(runtimeRows),
    progress,
    projectId,
    status: buildStatus(runtime, summary, progress),
    summary
  };
}

/**
 * Selects the terminal partial result that happened most recently.
 *
 * Native terminal sequence is authoritative within one registry lifetime.
 * Persisted presentation checkpoints intentionally omit it, so wall-clock
 * timestamps remain the compatibility fallback after a renderer reload.
 * A newer full result hides the partial result because it verifies a broader
 * scope and becomes the latest finished activity.
 */
export function latestPartialBuildResult(runtimes: readonly BuildRuntime[]): BuildPartialResult | null {
  if (runtimes.some((runtime) => runtime.state === "running")) {
    return null;
  }
  const latestTerminal = runtimes
    .filter(
      (runtime): runtime is BuildRuntime & { state: BuildHistoryStatus } =>
        isTerminalBuildRuntime(runtime) && !isUnstartedFailedBuildAttempt(runtime)
    )
    .slice()
    .sort(compareBuildRuntimeChronology)
    .at(-1);
  if (!latestTerminal?.target) {
    return null;
  }
  if (
    runtimes.some(
      (runtime) =>
        isUnstartedFailedBuildAttempt(runtime) &&
        isFallbackActivityLater(runtime, latestTerminal)
    )
  ) {
    return null;
  }
  const startedAtMs = safeRuntimeTimestamp(latestTerminal.startedAtMs);
  const finishedAtMs = safeRuntimeTimestamp(latestTerminal.finishedAtMs);
  return {
    durationMs:
      startedAtMs !== null && finishedAtMs !== null && finishedAtMs >= startedAtMs
        ? finishedAtMs - startedAtMs
        : null,
    finishedAtMs,
    state: latestTerminal.state,
    target: latestTerminal.target
  };
}

function isUnstartedFailedBuildAttempt(runtime: BuildRuntime): boolean {
  return (
    runtime.state === "failed" &&
    runtime.runId === null &&
    safeRuntimeTimestamp(runtime.finishedAtMs) === null &&
    safeRuntimeSequence(runtime.terminalSequence) === null
  );
}

function isFallbackActivityLater(candidate: BuildRuntime, baseline: BuildRuntime): boolean {
  const candidateAtMs = safeRuntimeTimestamp(candidate.finishedAtMs) ?? safeRuntimeTimestamp(candidate.startedAtMs);
  const baselineAtMs = safeRuntimeTimestamp(baseline.finishedAtMs) ?? safeRuntimeTimestamp(baseline.startedAtMs);
  return candidateAtMs === null || baselineAtMs === null || candidateAtMs > baselineAtMs;
}

/** Selects the authoritative project-overview runtime without hiding adverse slots. */
export function buildOverviewRuntime(runtimes: readonly BuildRuntime[], mode: BuildMode): BuildRuntime {
  const full = runtimes.find((run) => buildTargetKey(run.target) === BUILD_RUN_FULL_KEY);
  if (full?.state === "running") {
    return full;
  }
  const partialRuns = runtimes.filter((run) => run.state === "running" && run.target);
  if (partialRuns.length > 0) {
    const percent = Math.round(partialRuns.reduce((total, run) => total + (run.progress?.percent ?? 0), 0) / partialRuns.length);
    return {
      mode: partialRuns[0]?.mode ?? mode,
      progress: {
        detail: "parallel_partial",
        index: partialRuns.length,
        label: "parallel_partial",
        percent,
        phase: "parallel_partial",
        total: partialRuns.length
      },
      state: "running",
      target: null
    };
  }
  const terminalRuns = runtimes
    .filter((run) => isTerminalBuildRuntime(run))
    .slice()
    .sort(compareBuildRuntimeChronology);
  const latestTerminal = terminalRuns
    .filter((run) => run.state === "failed" || run.state === "interrupted")
    .at(-1) ?? terminalRuns.at(-1);
  return latestTerminal ?? { mode, progress: null, state: "idle", target: null };
}

function isTerminalBuildRuntime(runtime: BuildRuntime): boolean {
  return runtime.state === "completed" || runtime.state === "failed" || runtime.state === "interrupted";
}

function compareBuildRuntimeChronology(left: BuildRuntime, right: BuildRuntime): number {
  const leftSequence = safeRuntimeSequence(left.terminalSequence);
  const rightSequence = safeRuntimeSequence(right.terminalSequence);
  if (leftSequence !== null && rightSequence !== null) {
    return leftSequence - rightSequence;
  }
  return (
    (safeRuntimeTimestamp(left.finishedAtMs) ?? safeRuntimeTimestamp(left.startedAtMs) ?? -1) -
    (safeRuntimeTimestamp(right.finishedAtMs) ?? safeRuntimeTimestamp(right.startedAtMs) ?? -1)
  );
}

function safeRuntimeTimestamp(value: number | null | undefined): number | null {
  return typeof value === "number" && Number.isFinite(value) && value >= 0 ? value : null;
}

function safeRuntimeSequence(value: number | null | undefined): number | null {
  return typeof value === "number" && Number.isSafeInteger(value) && value >= 0 ? value : null;
}

export function nextBuildRuntime(current: BuildRuntime, command: BuildRuntimeCommand, mode: BuildMode = current.mode, target: BuildTarget | null = null): BuildRuntime {
  if (command === "start") {
    return { mode, progress: null, state: "running", target };
  }
  if (command === "interrupt" && current.state === "running") {
    return { ...current, state: "interrupted" };
  }
  if (command === "complete") {
    return { ...current, progress: { phase: "complete", label: "Complete", percent: 100 }, state: "completed" };
  }
  return current;
}

export function readBuildPageSettings(storage: Storage | null | undefined = browserStorage()): BuildPageSettings {
  if (!storage) {
    return DEFAULT_SETTINGS;
  }
  return {
    buildMode: parseBuildMode(storage.getItem(BUILD_MODE_STORAGE_KEY)),
    launchMode: DEFAULT_SETTINGS.launchMode,
    parallelism: DEFAULT_SETTINGS.parallelism,
    strictMetadata: DEFAULT_SETTINGS.strictMetadata
  };
}

export function writeBuildPageSettings(settings: BuildPageSettings, storage: Storage | null | undefined = browserStorage()): void {
  if (!storage) {
    return;
  }
  storage.setItem(BUILD_MODE_STORAGE_KEY, settings.buildMode);
  storage.removeItem(BUILD_STRICT_METADATA_STORAGE_KEY);
  storage.removeItem(LEGACY_LAUNCH_MODE_STORAGE_KEY);
}

export function hoi4LaunchModeFromConfig(value: unknown, fallback: Hoi4LaunchMode = DEFAULT_SETTINGS.launchMode): Hoi4LaunchMode {
  return typeof value === "string" && BUILD_HOI4_LAUNCH_MODE_VALUES.includes(value as Hoi4LaunchMode) ? (value as Hoi4LaunchMode) : fallback;
}

export function hoi4GameRootFromConfig(value: unknown, fallback = ""): string {
  return typeof value === "string" ? value.trim() : fallback;
}

export function strictMetadataFromConfig(value: unknown, fallback = DEFAULT_SETTINGS.strictMetadata): boolean {
  return typeof value === "boolean" ? value : fallback;
}

export function buildParallelismFromConfig(value: unknown, fallback = DEFAULT_SETTINGS.parallelism): number {
  if (typeof value !== "number" || !Number.isFinite(value) || value < BUILD_PARALLELISM_MIN) {
    return fallback;
  }
  return Math.round(value);
}

export function buildRunGameDisabled({
  actionPending,
  buildBlocked,
  desktopBackend,
  hasAdverseBuildState,
  hasRunningBuilds,
  launchReady,
  launchModeReady
}: {
  actionPending: boolean;
  buildBlocked: boolean;
  desktopBackend: boolean;
  hasAdverseBuildState: boolean;
  hasRunningBuilds: boolean;
  launchReady: boolean;
  launchModeReady: boolean;
}): boolean {
  return (
    actionPending ||
    buildBlocked ||
    hasAdverseBuildState ||
    hasRunningBuilds ||
    !launchReady ||
    !desktopBackend ||
    !launchModeReady
  );
}

export function readBuildHistory(storage: Storage | null | undefined = browserStorage()): BuildHistoryEntry[] {
  if (!storage) {
    return [];
  }
  const tombstones = new Set(readBuildHistoryTombstones(storage));
  const raw = safeStorageGetItem(storage, BUILD_HISTORY_STORAGE_KEY);
  if (!raw) {
    return [];
  }
  try {
    const parsed = JSON.parse(raw);
    if (!Array.isArray(parsed)) {
      return [];
    }
    return parsed
      .map(normalizeBuildHistoryEntry)
      .filter((entry): entry is BuildHistoryEntry => entry !== null)
      .filter((entry) => !tombstones.has(entry.id))
      .sort(compareBuildHistoryEntries)
      .slice(-BUILD_HISTORY_LIMIT);
  } catch {
    return [];
  }
}

/** Returns the bounded run-id set explicitly removed from build history. */
export function readBuildHistoryTombstones(storage: Storage | null | undefined = browserStorage()): string[] {
  if (!storage) {
    return [];
  }
  const raw = safeStorageGetItem(storage, BUILD_HISTORY_TOMBSTONES_STORAGE_KEY);
  if (!raw) {
    return [];
  }
  try {
    return normalizeBuildHistoryTombstones(JSON.parse(raw));
  } catch {
    return [];
  }
}

export function recordBuildHistoryEntry(
  entry: BuildHistoryEntry,
  storage: Storage | null | undefined = browserStorage()
): BuildHistoryEntry[] {
  const clean = normalizeBuildHistoryEntry(entry);
  if (!clean) {
    return readBuildHistory(storage);
  }
  if (readBuildHistoryTombstones(storage).includes(clean.id)) {
    return readBuildHistory(storage);
  }
  const next = readBuildHistory(storage)
    .filter((candidate) => candidate.id !== clean.id)
    .concat(clean)
    .sort(compareBuildHistoryEntries)
    .slice(-BUILD_HISTORY_LIMIT);
  writeBuildHistory(next, storage);
  return next;
}

export function writeBuildHistory(history: readonly BuildHistoryEntry[], storage: Storage | null | undefined = browserStorage()): void {
  if (!storage) {
    return;
  }
  const tombstones = new Set(readBuildHistoryTombstones(storage));
  const clean = history
    .map(normalizeBuildHistoryEntry)
    .filter((entry): entry is BuildHistoryEntry => entry !== null)
    .filter((entry) => !tombstones.has(entry.id))
    .sort(compareBuildHistoryEntries)
    .slice(-BUILD_HISTORY_LIMIT);
  safeStorageSetItem(storage, BUILD_HISTORY_STORAGE_KEY, JSON.stringify(clean));
}

export function removeBuildHistoryEntry(id: string, storage: Storage | null | undefined = browserStorage()): BuildHistoryEntry[] {
  const cleanId = historyText(id);
  if (!cleanId) {
    return readBuildHistory(storage);
  }
  writeBuildHistoryTombstone(cleanId, storage);
  const next = readBuildHistory(storage).filter((entry) => entry.id !== cleanId);
  writeBuildHistory(next, storage);
  return next;
}

export function averageBuildDurationMs(history: readonly BuildHistoryEntry[], projectRoot: string, mode?: BuildMode): number | null {
  const matches = completedHistorySamples(history, projectRoot, mode);
  const active = matches.length > 0 ? matches : completedHistorySamples(history, projectRoot);
  const latest = active.slice(-5);
  if (latest.length === 0) {
    return null;
  }
  return Math.round(latest.reduce((total, entry) => total + entry.durationMs, 0) / latest.length);
}

export function buildTargetKey(target: BuildTarget | null | undefined): string {
  if (!target) {
    return BUILD_RUN_FULL_KEY;
  }
  return `${target.kind}:${target.family ?? ""}:${target.id}`;
}

/**
 * Matches the target identity enforced by the Python and native build registries.
 *
 * The optional family only scopes collection ids. A family-less collection
 * target is the registry's compatibility wildcard for the same collection id.
 */
export function sameBuildTarget(
  left: BuildTarget | null | undefined,
  right: BuildTarget | null | undefined
): boolean {
  if (!left || !right) {
    return !left && !right;
  }
  if (left.kind !== right.kind || left.id !== right.id) {
    return false;
  }
  return (
    left.kind !== "collection" ||
    left.family == null ||
    right.family == null ||
    left.family === right.family
  );
}

export function buildFamilyTargetForBrowser(
  browser: ProjectBrowserPayload | null | undefined,
  familyId: string
): BuildTarget | null {
  const requestedBuildFamily = familyId.trim();
  const family = projectBrowserFamily(browser ?? null, requestedBuildFamily);
  const buildFamilyId = (family?.family || family?.id || "").trim();
  return buildFamilyId
    ? { family: buildFamilyId, id: buildFamilyId, kind: "family" }
    : null;
}

/**
 * Resolves a requested partial-build target to the SDK browser's canonical id.
 *
 * Build dashboard rows collapse to families when family summaries are
 * available, so module and collection intents must resolve against browser
 * items rather than the rendered row list.
 */
export function resolveBuildTargetForBrowser(
  browser: ProjectBrowserPayload | null | undefined,
  target: BuildTarget
): BuildTarget | null {
  if (!browser || !target.id.trim()) {
    return null;
  }
  if (target.kind === "family") {
    const resolved =
      buildFamilyTargetForBrowser(browser, target.id) ??
      buildFamilyTargetForBrowser(browser, target.family ?? "");
    const requestedFamily = target.family?.trim()
      ? projectBrowserFamily(browser, target.family)?.family ?? target.family
      : null;
    return resolved && buildFamiliesMatch(resolved.family, requestedFamily)
      ? resolved
      : null;
  }

  const requestedId = normalizedRequestedBuildTargetId(target);
  const requestedFamily = target.family?.trim()
    ? projectBrowserFamily(browser, target.family)?.family ?? target.family
    : null;
  return (
    browser.items
      .map(buildTargetForBrowserItem)
      .find(
        (candidate) =>
          candidate?.kind === target.kind &&
          candidate.id === requestedId &&
          buildFamiliesMatch(candidate.family, requestedFamily)
      ) ?? null
  );
}

export function formatBuildDuration(durationMs: number): string {
  const totalSeconds = Math.max(1, Math.round(durationMs / 1000));
  if (totalSeconds < 60) {
    return `${totalSeconds}s`;
  }
  const minutes = Math.floor(totalSeconds / 60);
  const seconds = totalSeconds % 60;
  if (minutes < 60) {
    return seconds > 0 ? `${minutes}m ${seconds}s` : `${minutes}m`;
  }
  const hours = Math.floor(minutes / 60);
  const remainingMinutes = minutes % 60;
  return remainingMinutes > 0 ? `${hours}h ${remainingMinutes}m` : `${hours}h`;
}

function buildModuleCount(browser: ProjectBrowserPayload | null): number {
  if (!browser) {
    return 0;
  }
  const familyCount = browser.groups?.length
    ? browser.groups.reduce(
        (total, group) => total + safeCount(group.module_count),
        0
      )
    : browser.families.reduce(
        (total, family) => total + safeCount(family.item_count),
        0
      );
  const itemCount = browser.items.filter((item) => item.kind === "module").length;
  return Math.max(familyCount, itemCount);
}

function buildCollectionCount(browser: ProjectBrowserPayload | null): number {
  if (!browser) {
    return 0;
  }
  const groupCount = browser.groups?.reduce(
    (total, group) => total + safeCount(group.collection_count),
    0
  ) ?? 0;
  const itemCount = browser.items.filter((item) => item.kind === "collection").length;
  return Math.max(groupCount, itemCount);
}

function buildSourceCount(browser: ProjectBrowserPayload | null): number {
  if (!browser) {
    return 0;
  }
  const familyCount = browser.families.reduce((total, family) => total + safeCount(family.source_count), 0);
  const itemCount = browser.items.reduce((total, item) => total + safeCount(item.source_count), 0);
  return Math.max(familyCount, itemCount);
}

function buildEntityRows(browser: ProjectBrowserPayload | null, blocked: boolean, runtimes: readonly BuildRuntime[]): BuildEntityRow[] {
  if (!browser) {
    return [];
  }
  if (browser.families.length > 0) {
    return browser.families.map((family) => buildFamilyEntityRow(family, blocked, runtimes));
  }
  const itemRows = browser.items
    .filter((item) => item.kind === "module" || item.kind === "collection")
    .map((item) => buildItemEntityRow(item, blocked, runtimes));
  return itemRows;
}

function buildItemEntityRow(item: ProjectBrowserItem, blocked: boolean, runtimes: readonly BuildRuntime[]): BuildEntityRow {
  const target = item.kind === "collection"
    ? { family: item.family, id: item.collection_id || item.id, kind: "collection" as const }
    : { family: item.family, id: item.module_id || item.id, kind: "module" as const };
  const sourceCount = safeCount(item.source_count);
  const targetRuntime = latestBuildTargetRuntime(runtimes, target);
  const progress = buildEntityProgress(sourceCount, target, runtimes);
  return {
    detail: buildEntityRuntimeDetail(`${sourceLabel(item.source_count)} in ${item.relative_root}`, targetRuntime),
    family: item.family,
    id: target.id,
    kind: target.kind,
    moduleCount: 1,
    progressLabel: progress.label,
    progressCurrent: progress.current,
    progressPercent: progress.percent,
    progressTotal: progress.total,
    relativeRoot: item.relative_root,
    sourceCount,
    sourceSlotCount: new Set(item.sources.map((source) => source.slot)).size,
    status: blocked ? "blocked" : buildEntityRuntimeStatus(targetRuntime),
    target,
    title: item.title || target.id
  };
}

function buildTargetForBrowserItem(item: ProjectBrowserItem): BuildTarget | null {
  const family = (item.family || item.family_id).trim();
  if (!family) {
    return null;
  }
  if (item.kind === "collection") {
    const collectionId = (
      item.collection_id ||
      stripBuildTargetKindPrefix(item.id, "collection")
    ).trim();
    return collectionId
      ? { family, id: collectionId, kind: "collection" }
      : null;
  }
  if (item.kind !== "module") {
    return null;
  }

  const browserId = stripBuildTargetKindPrefix(item.id, "module");
  const declaredId = item.module_id?.trim() ?? "";
  const canonicalId =
    [declaredId, browserId].find((candidate) => candidate.includes("/")) ??
    (item.object_id.trim() ? `${family}/${item.object_id.trim()}` : declaredId || browserId);
  return canonicalId
    ? { family, id: canonicalId, kind: "module" }
    : null;
}

function normalizedRequestedBuildTargetId(target: BuildTarget): string {
  const requestedId = stripBuildTargetKindPrefix(target.id, target.kind);
  if (target.kind !== "module" || requestedId.includes("/") || !target.family?.trim()) {
    return requestedId;
  }
  return `${target.family.trim()}/${requestedId}`;
}

function stripBuildTargetKindPrefix(value: string, kind: BuildTargetKind): string {
  const clean = value.trim();
  const prefix = `${kind}:`;
  return clean.startsWith(prefix) ? clean.slice(prefix.length) : clean;
}

function buildFamiliesMatch(left: string | null | undefined, right: string | null | undefined): boolean {
  if (!right?.trim()) {
    return true;
  }
  if (!left?.trim()) {
    return false;
  }
  return canonicalFamilyId(left) === canonicalFamilyId(right);
}

function buildFamilyEntityRow(family: ProjectBrowserFamily, blocked: boolean, runtimes: readonly BuildRuntime[]): BuildEntityRow {
  const familyId = family.family || family.id;
  const sourceCount = safeCount(family.source_count);
  const target = { family: familyId, id: familyId, kind: "family" as const };
  const targetRuntime = latestBuildTargetRuntime(runtimes, target);
  const progress = buildEntityProgress(sourceCount, target, runtimes);
  const titleKey = moduleTitleKeyForFamily(family);
  return {
    detail: buildEntityRuntimeDetail(
      `${safeCount(family.item_count)} modules, ${sourceLabel(family.source_count)}`,
      targetRuntime
    ),
    family: familyId,
    familyTitleKey: titleKey,
    id: familyId,
    kind: "family",
    moduleCount: safeCount(family.item_count),
    progressLabel: progress.label,
    progressCurrent: progress.current,
    progressPercent: progress.percent,
    progressTotal: progress.total,
    relativeRoot: "",
    sourceCount,
    sourceSlotCount: 0,
    status: blocked ? "blocked" : buildEntityRuntimeStatus(targetRuntime),
    target,
    title: family.title || familyId,
    titleKey
  };
}

function buildEntityProgress(sourceCount: number, target: BuildTarget, runtimes: readonly BuildRuntime[]): { current: number; label: string; percent: number; total: number } {
  const runtime = latestBuildTargetRuntime(runtimes, target);
  if (runtime?.state === "running" || runtime?.state === "failed" || runtime?.state === "interrupted") {
    const total = Math.max(0, safeNullableCount(runtime.progress?.total) ?? sourceCount);
    const progressPercent = clampPercent(runtime.progress?.percent);
    const index = safeNullableCount(runtime.progress?.index);
    const current = Math.min(total, index ?? Math.round((total * progressPercent) / 100));
    return {
      current,
      label: sourceProgressLabel(current, total),
      percent: total > 0 ? progressPercent : 0,
      total
    };
  }
  return {
    current: sourceCount,
    label: sourceProgressLabel(sourceCount, sourceCount),
    percent: sourceCount > 0 ? 100 : 0,
    total: sourceCount
  };
}

function latestBuildTargetRuntime(runtimes: readonly BuildRuntime[], target: BuildTarget): BuildRuntime | null {
  for (let index = runtimes.length - 1; index >= 0; index -= 1) {
    const runtime = runtimes[index];
    if (sameBuildTarget(runtime?.target, target)) {
      return runtime ?? null;
    }
  }
  return null;
}

function buildEntityRuntimeStatus(runtime: BuildRuntime | null): BuildEntityRow["status"] {
  if (runtime?.state === "failed" || runtime?.state === "interrupted") {
    return runtime.state;
  }
  return "ready";
}

function buildEntityRuntimeDetail(base: string, runtime: BuildRuntime | null): string {
  if (runtime?.state === "failed") {
    return runtime.errorSummary || "The latest rebuild failed. Review the build history and retry.";
  }
  if (runtime?.state === "interrupted") {
    return runtime.errorSummary || "The latest rebuild was interrupted before completion.";
  }
  return base;
}

function buildDiagnosticCounts(diagnostics: ReadonlyArray<Record<string, unknown>>) {
  let errorCount = 0;
  let warningCount = 0;
  diagnostics.forEach((diagnostic) => {
    const severity = String(diagnostic.severity ?? diagnostic.level ?? "").toLowerCase();
    if (severity === "error" || severity === "fatal") {
      errorCount += 1;
    } else if (severity === "warning" || severity === "warn") {
      warningCount += 1;
    }
  });
  return {
    diagnosticCount: diagnostics.length,
    errorCount,
    warningCount
  };
}

function buildProgressDisplay(progress: BuildProgressSnapshot | null, state: BuildRunState): BuildProgressDisplay {
  if (!progress) {
    return {
      countLabel: "",
      detail: "Waiting for compiler progress",
      label: "Ready",
      percent: state === "idle" || state === "completed" ? 100 : 0,
      phase: state === "running" ? "waiting" : "idle"
    };
  }
  return {
    countLabel: progressCountLabel(progress),
    detail: progress.detail || progress.current || progressPhaseLabel(progress.phase),
    label: progress.label || progressPhaseLabel(progress.phase),
    percent: clampPercent(progress.percent),
    phase: progress.phase
  };
}

function buildStatus(runtime: BuildRuntime, summary: BuildDashboardSummary, progress: BuildProgressDisplay): BuildDashboardModel["status"] {
  if (runtime.state === "running") {
    return {
      detail: progress.countLabel ? `${progress.detail} (${progress.countLabel})` : progress.detail,
      label: "Compilation running",
      progress: progress.percent,
      state: "running"
    };
  }
  if (runtime.state === "interrupted") {
    return {
      detail: runtime.errorSummary || "The current compilation run was interrupted before completion.",
      label: "Compilation interrupted",
      progress: progress.percent,
      state: "interrupted"
    };
  }
  if (runtime.state === "completed") {
    return {
      detail: "Compilation finished and build data can be refreshed.",
      label: "Compilation complete",
      progress: 100,
      state: "completed"
    };
  }
  if (runtime.state === "failed") {
    return {
      detail: runtime.errorSummary || "The native compilation command failed. Check the build error log from the latest run.",
      label: "Compilation failed",
      progress: progress.percent,
      state: "failed"
    };
  }
  if (summary.blocked) {
    return {
      detail: `${summary.errorCount} blocking diagnostic${summary.errorCount === 1 ? "" : "s"} must be fixed before artifact emission.`,
      label: "Compilation blocked",
      progress: 0,
      state: "blocked"
    };
  }
  return {
    detail: "Ready to compile the current project.",
    label: "Ready",
    progress: 100,
    state: "ready"
  };
}

function buildEstimateDisplay(history: readonly BuildHistoryEntry[], projectRoot: string, mode: BuildMode, runtime: BuildRuntime, runtimes: readonly BuildRuntime[]): BuildEstimateDisplay {
  const hasPartialRuntime = Boolean(runtime.target) || runtime.progress?.phase === "parallel_partial" || runtimes.some((entry) => entry.state === "running" && entry.target);
  if (hasPartialRuntime) {
    return {
      durationLabel: "",
      durationMs: null,
      sampleCount: 0
    };
  }
  const sampleLimit = mode === "cached" ? 1 : 5;
  const samples = completedHistorySamples(history, projectRoot, mode).slice(-sampleLimit);
  const durationMs = samples.length === 0 ? null : Math.round(samples.reduce((total, entry) => total + entry.durationMs, 0) / samples.length);
  return {
    durationLabel: durationMs === null ? "" : formatBuildDuration(durationMs),
    durationMs,
    sampleCount: samples.length
  };
}

export function buildOutputOpenPath(project: ProjectOption): string {
  const home = userHomeFromPath(project.path);
  const outputRoot = expandHomePath(project.outputRoot, home);
  if (outputRoot) {
    return outputRoot;
  }
  const projectId = project.projectId || project.id;
  if ((project.game ?? "hoi4") === "hoi4" && home) {
    return `${home}/Documents/Paradox Interactive/Hearts of Iron IV/mod/${projectId}`;
  }
  return `${project.path.replace(/\/+$/, "")}/build/mod`;
}

function parseBuildMode(value: string | null): BuildMode {
  return value === "full" ? "full" : "cached";
}

function parseLaunchMode(value: string | null): Hoi4LaunchMode {
  return value === "local" ? "local" : "steam";
}

function browserStorage(): Storage | null {
  if (typeof window === "undefined") {
    return null;
  }
  try {
    return window.localStorage;
  } catch {
    return null;
  }
}

function expandHomePath(path: string | null | undefined, home: string | null): string | null {
  if (!path?.trim()) {
    return null;
  }
  const clean = path.trim();
  if (clean === "~") {
    return home;
  }
  if (clean.startsWith("~/")) {
    return home ? `${home}${clean.slice(1)}` : null;
  }
  return clean;
}

function userHomeFromPath(path: string): string | null {
  const match = path.match(/^\/Users\/[^/]+/);
  return match?.[0] ?? null;
}

function safeCount(value: number): number {
  return Number.isFinite(value) ? Math.max(0, Math.floor(value)) : 0;
}

function sourceLabel(count: number): string {
  const safe = safeCount(count);
  return `${safe} source${safe === 1 ? "" : "s"}`;
}

function sourceProgressLabel(current: number, total: number): string {
  return `${current} / ${total} source${total === 1 ? "" : "s"}`;
}

function progressCountLabel(progress: BuildProgressSnapshot): string {
  const index = safeNullableCount(progress.index);
  const total = safeNullableCount(progress.total);
  if (index === null || total === null || total <= 0) {
    return "";
  }
  return `${index} / ${total}`;
}

function safeNullableCount(value: number | null | undefined): number | null {
  if (value === null || value === undefined || !Number.isFinite(value)) {
    return null;
  }
  return Math.max(0, Math.floor(value));
}

function clampPercent(value: number | null | undefined): number {
  if (value === null || value === undefined || !Number.isFinite(value)) {
    return 0;
  }
  return Math.max(0, Math.min(100, Math.round(value)));
}

function progressPhaseLabel(phase: string): string {
  const labels: Record<string, string> = {
    artifact_generation: "Writing artifacts",
    basic_copy: "Copying static files",
    collection_compile: "Compiling collections",
    complete: "Complete",
    discover_collections: "Finding collections",
    discover_modules: "Finding modules",
    entity_compile: "Compiling entities",
    post_processing: "Post-processing",
    validating_publication: "Validating publication"
  };
  return labels[phase] ?? phase.replaceAll("_", " ");
}

function normalizeBuildHistoryEntry(value: unknown): BuildHistoryEntry | null {
  if (!value || typeof value !== "object") {
    return null;
  }
  const row = value as Partial<BuildHistoryEntry> & Record<string, unknown>;
  const id = historyText(row.id) || historyText(row.runId) || historyText(row.run_id);
  const projectId = historyText(row.projectId) || historyText(row.project_id);
  const projectRoot = historyText(row.projectRoot) || historyText(row.project_root);
  const mode = parseBuildMode(historyText(row.mode) || historyText(row.buildMode) || historyText(row.build_mode));
  const status = normalizeHistoryStatus(row.status);
  const startedAtMs = safeHistoryTimestamp(row.startedAtMs ?? row.started_at_ms);
  const finishedAtMs = safeHistoryTimestamp(row.finishedAtMs ?? row.finished_at_ms);
  if (startedAtMs === null || finishedAtMs === null) {
    return null;
  }
  const durationMs = safeDuration(row.durationMs ?? row.duration_ms ?? finishedAtMs - startedAtMs);
  if (!id || !projectId || !projectRoot || !status || durationMs === null) {
    return null;
  }
  const command = normalizeCommand(row.command);
  const errorPath = historyText(row.errorPath) || historyText(row.error_path);
  const errorSummary = historyText(row.errorSummary) || historyText(row.error_summary);
  const exitCode = safeNullableInteger(row.exitCode ?? row.exit_code);
  const outputPath = historyText(row.outputPath) || historyText(row.output_path);
  return {
    ...(command.length > 0 ? { command } : {}),
    durationMs,
    ...(errorPath ? { errorPath } : {}),
    ...(errorSummary ? { errorSummary } : {}),
    ...(exitCode !== null ? { exitCode } : {}),
    finishedAtMs,
    id,
    mode,
    ...(outputPath ? { outputPath } : {}),
    projectId,
    projectRoot,
    startedAtMs,
    status,
    target: normalizeBuildTarget(row.target)
  };
}

function normalizeBuildHistoryTombstones(value: unknown): string[] {
  if (!Array.isArray(value)) {
    return [];
  }
  const newest: string[] = [];
  const seen = new Set<string>();
  for (let index = value.length - 1; index >= 0 && newest.length < BUILD_HISTORY_TOMBSTONE_LIMIT; index -= 1) {
    const candidate = value[index];
    const id = historyText(
      typeof candidate === "string"
        ? candidate
        : candidate && typeof candidate === "object"
          ? (candidate as Record<string, unknown>).id
          : null
    );
    if (!id || seen.has(id)) {
      continue;
    }
    seen.add(id);
    newest.push(id);
  }
  return newest.reverse();
}

function writeBuildHistoryTombstone(id: string, storage: Storage | null | undefined): void {
  if (!storage) {
    return;
  }
  const next = readBuildHistoryTombstones(storage).filter((candidate) => candidate !== id);
  next.push(id);
  safeStorageSetItem(storage, BUILD_HISTORY_TOMBSTONES_STORAGE_KEY, JSON.stringify(normalizeBuildHistoryTombstones(next)));
}

function normalizeHistoryStatus(value: unknown): BuildHistoryStatus | null {
  if (value === "completed" || value === "failed" || value === "interrupted") {
    return value;
  }
  if (value === "success") {
    return "completed";
  }
  if (value === "failure" || value === "error") {
    return "failed";
  }
  if (value === "cancelled" || value === "canceled") {
    return "interrupted";
  }
  return null;
}

function normalizeBuildTarget(value: unknown): BuildTarget | null {
  if (!value || typeof value !== "object") {
    return null;
  }
  const row = value as Partial<BuildTarget>;
  if (row.kind !== "module" && row.kind !== "collection" && row.kind !== "family") {
    return null;
  }
  if (typeof row.id !== "string" || !row.id.trim()) {
    return null;
  }
  return {
    family: typeof row.family === "string" && row.family.trim() ? row.family.trim() : null,
    id: row.id.trim(),
    kind: row.kind
  };
}

function safeHistoryTimestamp(value: unknown): number | null {
  return typeof value === "number" && Number.isFinite(value) && value >= 0 ? Math.round(value) : null;
}

function safeDuration(value: unknown): number | null {
  return typeof value === "number" && Number.isFinite(value) && value > 0 ? Math.round(value) : null;
}

function safeNullableInteger(value: unknown): number | null {
  return typeof value === "number" && Number.isFinite(value) ? Math.round(value) : null;
}

function historyText(value: unknown): string | null {
  return typeof value === "string" && value.trim() ? value.trim() : null;
}

function normalizeCommand(value: unknown): string[] {
  if (!Array.isArray(value)) {
    return [];
  }
  return value.map(historyText).filter((part): part is string => part !== null);
}

function completedHistorySamples(history: readonly BuildHistoryEntry[], projectRoot: string, mode?: BuildMode): BuildHistoryEntry[] {
  return history
    .filter((entry) => entry.projectRoot === projectRoot && entry.status === "completed" && entry.durationMs > 0 && !entry.target && (!mode || entry.mode === mode))
    .sort(compareBuildHistoryEntries);
}

function safeStorageGetItem(storage: Storage, key: string): string | null {
  try {
    return storage.getItem(key);
  } catch {
    return null;
  }
}

function safeStorageSetItem(storage: Storage, key: string, value: string): void {
  try {
    storage.setItem(key, value);
  } catch {
    // Browser privacy/quota failures must not turn a completed native build into a lifecycle failure.
  }
}

function compareBuildHistoryEntries(left: BuildHistoryEntry, right: BuildHistoryEntry): number {
  return left.finishedAtMs - right.finishedAtMs;
}
