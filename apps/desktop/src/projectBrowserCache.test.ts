import { describe, expect, it } from "vitest";
import { isUnfilteredProjectBrowserPayload, readCachedProjectBrowser, writeCachedProjectBrowser } from "./projectBrowserCache";
import type { ProjectBrowserPayload } from "./types";

function browserPayload(root = "/tmp/PIHC3"): ProjectBrowserPayload {
  return {
    schema: "paradev.sdk.project-browser.v1",
    project_id: "PIHC3",
    title: "PIHC3",
    root,
    profile: "hoi4",
    filters: {},
    families: [{ id: "ideas", family: "idea", title: "Ideas", visible: true, item_count: 12, source_count: 24, layouts: ["canonical"] }],
    groups: [
      {
        collection_count: 2,
        family: "idea",
        id: "ideas",
        item_count: 12,
        module_count: 10
      }
    ],
    items: [],
    diagnostics: []
  };
}

function storage(): Storage {
  const values = new Map<string, string>();
  return {
    clear: () => values.clear(),
    getItem: (key: string) => values.get(key) ?? null,
    key: (index: number) => [...values.keys()][index] ?? null,
    removeItem: (key: string) => values.delete(key),
    setItem: (key: string, value: string) => {
      values.set(key, value);
    },
    get length() {
      return values.size;
    }
  };
}

describe("project browser cache", () => {
  it("persists and restores a versioned browser payload by project root", async () => {
    const backend = storage();
    const payload = browserPayload();

    await writeCachedProjectBrowser(payload, backend);

    await expect(readCachedProjectBrowser("/tmp/PIHC3", backend)).resolves.toEqual(payload);
  });

  it("ignores cached browser payloads for a different project root", async () => {
    const backend = storage();

    await writeCachedProjectBrowser(browserPayload("/tmp/PIHC3"), backend);

    await expect(readCachedProjectBrowser("/tmp/Other", backend)).resolves.toBeNull();
  });

  it("drops corrupt cache entries instead of blocking startup", async () => {
    const backend = storage();
    backend.setItem("paradev.projectBrowser:/tmp/PIHC3", "{");

    await expect(readCachedProjectBrowser("/tmp/PIHC3", backend)).resolves.toBeNull();
    expect(backend.getItem("paradev.projectBrowser:/tmp/PIHC3")).toBeNull();
  });

  it("rejects and purges filtered SDK payloads from the project-wide cache", async () => {
    const backend = storage();
    const filtered = { ...browserPayload(), filters: { family: "entity" } };
    const key = "paradev.projectBrowser:/tmp/PIHC3";
    backend.setItem(
      key,
      JSON.stringify({ schema: "paradev.desktop.project-browser-cache.v1", root: filtered.root, payload: filtered })
    );

    expect(isUnfilteredProjectBrowserPayload(filtered)).toBe(false);
    await expect(readCachedProjectBrowser("/tmp/PIHC3", backend)).resolves.toBeNull();
    expect(backend.getItem(key)).toBeNull();
  });

  it("rejects and purges legacy payloads without the required SDK filters map", async () => {
    const backend = storage();
    const { filters: _filters, ...legacyPayload } = browserPayload();
    const key = "paradev.projectBrowser:/tmp/PIHC3";
    backend.setItem(
      key,
      JSON.stringify({ schema: "paradev.desktop.project-browser-cache.v1", root: legacyPayload.root, payload: legacyPayload })
    );

    await expect(readCachedProjectBrowser("/tmp/PIHC3", backend)).resolves.toBeNull();
    expect(backend.getItem(key)).toBeNull();
  });

  it("rejects and purges legacy family rows without navigation visibility", async () => {
    const backend = storage();
    const payload = browserPayload();
    const legacyPayload = { ...payload, families: payload.families.map(({ visible: _visible, ...family }) => family) };
    const key = "paradev.projectBrowser:/tmp/PIHC3";
    backend.setItem(
      key,
      JSON.stringify({ schema: "paradev.desktop.project-browser-cache.v1", root: legacyPayload.root, payload: legacyPayload })
    );

    expect(isUnfilteredProjectBrowserPayload(legacyPayload)).toBe(false);
    await expect(readCachedProjectBrowser("/tmp/PIHC3", backend)).resolves.toBeNull();
    expect(backend.getItem(key)).toBeNull();
  });

  it("rejects a cached payload with malformed authoritative group counts", async () => {
    const backend = storage();
    const payload = browserPayload();
    const malformedPayload = {
      ...payload,
      groups: payload.groups?.map((group) => ({
        ...group,
        collection_count: -1
      }))
    };
    const key = "paradev.projectBrowser:/tmp/PIHC3";
    backend.setItem(
      key,
      JSON.stringify({
        schema: "paradev.desktop.project-browser-cache.v1",
        root: malformedPayload.root,
        payload: malformedPayload
      })
    );

    expect(isUnfilteredProjectBrowserPayload(malformedPayload)).toBe(false);
    await expect(readCachedProjectBrowser("/tmp/PIHC3", backend)).resolves.toBeNull();
    expect(backend.getItem(key)).toBeNull();
  });

  it("does not persist filtered SDK responses", async () => {
    const backend = storage();

    await writeCachedProjectBrowser({ ...browserPayload(), filters: { family: "entity" } }, backend);

    expect(backend.length).toBe(0);
  });
});
