export type BuildDiagnostics = Array<Record<string, unknown>>;
export type BuildDiagnosticsRefreshSource = "live" | "published";

type BuildDiagnosticsLoader = () => Promise<BuildDiagnostics>;

type BuildDiagnosticsCacheEntry = {
  diagnostics: BuildDiagnostics | null;
  error: unknown | null;
  errorGeneration: number;
  inFlight: Promise<BuildDiagnostics> | null;
  loader: BuildDiagnosticsLoader;
  requestedGeneration: number;
  settledGeneration: number;
};

type LoadBuildDiagnosticsInput = {
  generation: number;
  load: BuildDiagnosticsLoader;
  projectRoot: string;
  strictMetadata: boolean;
};

const buildDiagnosticsCache = new Map<string, BuildDiagnosticsCacheEntry>();

export function readCachedBuildDiagnostics(
  projectRoot: string,
  strictMetadata: boolean
): BuildDiagnostics | null {
  return buildDiagnosticsCache.get(buildDiagnosticsCacheKey(projectRoot, strictMetadata))?.diagnostics ?? null;
}

export function loadCachedBuildDiagnostics({
  generation,
  load,
  projectRoot,
  strictMetadata
}: LoadBuildDiagnosticsInput): Promise<BuildDiagnostics> {
  const key = buildDiagnosticsCacheKey(projectRoot, strictMetadata);
  const normalizedGeneration = normalizeGeneration(generation);
  const entry = buildDiagnosticsCache.get(key) ?? createBuildDiagnosticsCacheEntry(load);
  entry.loader = load;
  entry.requestedGeneration = Math.max(entry.requestedGeneration, normalizedGeneration);
  buildDiagnosticsCache.set(key, entry);
  return settleRequestedBuildDiagnostics(entry);
}

export function clearBuildDiagnosticsCache(projectRoot?: string): void {
  const normalizedProjectRoot = projectRoot?.trim();
  if (!normalizedProjectRoot) {
    buildDiagnosticsCache.clear();
    return;
  }
  for (const key of buildDiagnosticsCache.keys()) {
    if (key.startsWith(`${normalizedProjectRoot}\u0000`)) {
      buildDiagnosticsCache.delete(key);
    }
  }
}

function createBuildDiagnosticsCacheEntry(loader: BuildDiagnosticsLoader): BuildDiagnosticsCacheEntry {
  return {
    diagnostics: null,
    error: null,
    errorGeneration: -1,
    inFlight: null,
    loader,
    requestedGeneration: -1,
    settledGeneration: -1
  };
}

function settleRequestedBuildDiagnostics(entry: BuildDiagnosticsCacheEntry): Promise<BuildDiagnostics> {
  if (entry.inFlight) {
    return entry.inFlight;
  }
  if (entry.settledGeneration >= entry.requestedGeneration) {
    return settledBuildDiagnostics(entry);
  }

  const runGeneration = entry.requestedGeneration;
  const load = entry.loader;
  const inFlight = Promise.resolve()
    .then(load)
    .then(
      (diagnostics) => {
        if (runGeneration >= entry.settledGeneration) {
          entry.diagnostics = diagnostics;
          entry.error = null;
          entry.errorGeneration = -1;
          entry.settledGeneration = runGeneration;
        }
      },
      (error: unknown) => {
        if (runGeneration >= entry.settledGeneration) {
          entry.error = error;
          entry.errorGeneration = runGeneration;
          entry.settledGeneration = runGeneration;
        }
      }
    )
    .then(() => {
      entry.inFlight = null;
      return entry.requestedGeneration > entry.settledGeneration
        ? settleRequestedBuildDiagnostics(entry)
        : settledBuildDiagnostics(entry);
    });
  entry.inFlight = inFlight;
  return inFlight;
}

function settledBuildDiagnostics(entry: BuildDiagnosticsCacheEntry): Promise<BuildDiagnostics> {
  if (entry.errorGeneration === entry.settledGeneration) {
    return Promise.reject(entry.error);
  }
  return Promise.resolve(entry.diagnostics ?? []);
}

function buildDiagnosticsCacheKey(projectRoot: string, strictMetadata: boolean): string {
  return `${projectRoot.trim()}\u0000${strictMetadata ? "strict" : "relaxed"}`;
}

function normalizeGeneration(generation: number): number {
  return Number.isFinite(generation) ? Math.max(0, Math.floor(generation)) : 0;
}
