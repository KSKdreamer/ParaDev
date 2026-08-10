import type { ProjectBrowserPayload } from "./types";
import { hasDesktopBackend, readProjectBrowserCache, writeProjectBrowserCache } from "./services/paradev";

const PROJECT_BROWSER_CACHE_SCHEMA = "paradev.desktop.project-browser-cache.v1";
const PROJECT_BROWSER_CACHE_PREFIX = "paradev.projectBrowser";

type ProjectBrowserCacheEntry = {
  schema: typeof PROJECT_BROWSER_CACHE_SCHEMA;
  root: string;
  payload: ProjectBrowserPayload;
};

type ProjectBrowserCacheStorage = Pick<Storage, "getItem" | "removeItem" | "setItem">;

export async function readCachedProjectBrowser(projectRoot: string, storage?: ProjectBrowserCacheStorage | null): Promise<ProjectBrowserPayload | null> {
  if (storage === undefined && hasDesktopBackend()) {
    try {
      const payload = await readProjectBrowserCache(projectRoot);
      return isUnfilteredProjectBrowserPayload(payload) && normalizeRoot(payload.root) === normalizeRoot(projectRoot) ? payload : null;
    } catch {
      return null;
    }
  }
  const backend = storage === undefined ? null : storage;
  const key = projectBrowserCacheKey(projectRoot);
  if (!key || !backend) {
    return null;
  }
  const stored = backend.getItem(key);
  if (!stored) {
    return null;
  }
  try {
    const entry = JSON.parse(stored) as unknown;
    if (!isProjectBrowserCacheEntry(entry) || normalizeRoot(entry.root) !== normalizeRoot(projectRoot)) {
      backend.removeItem(key);
      return null;
    }
    return entry.payload;
  } catch {
    backend.removeItem(key);
    return null;
  }
}

export async function writeCachedProjectBrowser(payload: ProjectBrowserPayload, storage?: ProjectBrowserCacheStorage | null): Promise<void> {
  if (!isUnfilteredProjectBrowserPayload(payload)) {
    return;
  }
  if (storage === undefined && hasDesktopBackend()) {
    try {
      await writeProjectBrowserCache(payload);
    } catch {
      // Browser cache persistence is best-effort; startup must not depend on it.
    }
    return;
  }
  const backend = storage === undefined ? null : storage;
  const key = projectBrowserCacheKey(payload.root);
  if (!key || !backend) {
    return;
  }
  const entry: ProjectBrowserCacheEntry = {
    schema: PROJECT_BROWSER_CACHE_SCHEMA,
    root: payload.root,
    payload
  };
  try {
    backend.setItem(key, JSON.stringify(entry));
  } catch {
    // Browser cache persistence is best-effort; startup must not depend on it.
  }
}

function projectBrowserCacheKey(projectRoot: string): string {
  const root = normalizeRoot(projectRoot);
  return root ? `${PROJECT_BROWSER_CACHE_PREFIX}:${root}` : "";
}

function isProjectBrowserCacheEntry(value: unknown): value is ProjectBrowserCacheEntry {
  if (!isRecord(value) || value.schema !== PROJECT_BROWSER_CACHE_SCHEMA || typeof value.root !== "string") {
    return false;
  }
  return isUnfilteredProjectBrowserPayload(value.payload);
}

function isProjectBrowserPayload(value: unknown): value is ProjectBrowserPayload {
  return (
    isRecord(value) &&
    value.schema === "paradev.sdk.project-browser.v1" &&
    typeof value.project_id === "string" &&
    typeof value.title === "string" &&
    typeof value.root === "string" &&
    typeof value.profile === "string" &&
    isStringRecord(value.filters) &&
    Array.isArray(value.families) &&
    value.families.every(isProjectBrowserFamily) &&
    (value.groups === undefined ||
      (Array.isArray(value.groups) && value.groups.every(isProjectBrowserGroup))) &&
    Array.isArray(value.items) &&
    Array.isArray(value.diagnostics)
  );
}

function isProjectBrowserGroup(value: unknown): boolean {
  return (
    isRecord(value) &&
    typeof value.id === "string" &&
    typeof value.family === "string" &&
    isNonNegativeFiniteNumber(value.item_count) &&
    isNonNegativeFiniteNumber(value.module_count) &&
    isNonNegativeFiniteNumber(value.collection_count)
  );
}

function isProjectBrowserFamily(value: unknown): boolean {
  return isRecord(value) && typeof value.visible === "boolean";
}

/** Returns whether a browser payload is a complete, unscoped SDK response safe to cache as a project base. */
export function isUnfilteredProjectBrowserPayload(value: unknown): value is ProjectBrowserPayload {
  return isProjectBrowserPayload(value) && Object.keys(value.filters).length === 0;
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function isNonNegativeFiniteNumber(value: unknown): value is number {
  return typeof value === "number" && Number.isFinite(value) && value >= 0;
}

function isStringRecord(value: unknown): value is Record<string, string> {
  return isRecord(value) && Object.values(value).every((entry) => typeof entry === "string");
}

function normalizeRoot(value: string): string {
  return value.trim().replace(/\\/g, "/").replace(/\/+$/g, "");
}
