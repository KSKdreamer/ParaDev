import { beforeEach, describe, expect, it, vi } from "vitest";
import {
  clearBuildDiagnosticsCache,
  loadCachedBuildDiagnostics,
  readCachedBuildDiagnostics,
  type BuildDiagnostics
} from "./buildDiagnosticsCache";

beforeEach(() => clearBuildDiagnosticsCache());

describe("build diagnostics cache", () => {
  it("reuses one settled result for an unchanged project generation", async () => {
    const diagnostics = [{ code: "entity.valid", severity: "info" }];
    const load = vi.fn(async () => diagnostics);
    const request = { generation: 1, load, projectRoot: "/workspace/PIHC3", strictMetadata: true };

    await expect(loadCachedBuildDiagnostics(request)).resolves.toEqual(diagnostics);
    await expect(loadCachedBuildDiagnostics(request)).resolves.toEqual(diagnostics);

    expect(load).toHaveBeenCalledOnce();
    expect(readCachedBuildDiagnostics(request.projectRoot, request.strictMetadata)).toEqual(diagnostics);
  });

  it("shares one in-flight request across rail remount callers", async () => {
    const pending = deferred<BuildDiagnostics>();
    const load = vi.fn(() => pending.promise);
    const request = { generation: 2, load, projectRoot: "/workspace/PIHC3", strictMetadata: false };

    const first = loadCachedBuildDiagnostics(request);
    const second = loadCachedBuildDiagnostics(request);
    await Promise.resolve();
    expect(load).toHaveBeenCalledOnce();

    pending.resolve([]);
    await expect(Promise.all([first, second])).resolves.toEqual([[], []]);
  });

  it("serializes a newer generation behind an existing dry inspection", async () => {
    const first = deferred<BuildDiagnostics>();
    const second = deferred<BuildDiagnostics>();
    const load = vi.fn()
      .mockImplementationOnce(() => first.promise)
      .mockImplementationOnce(() => second.promise);
    const baseRequest = { load, projectRoot: "/workspace/PIHC3", strictMetadata: true };

    const firstResult = loadCachedBuildDiagnostics({ ...baseRequest, generation: 3 });
    await Promise.resolve();
    const latestResult = loadCachedBuildDiagnostics({ ...baseRequest, generation: 4 });
    const newestResult = loadCachedBuildDiagnostics({ ...baseRequest, generation: 5 });
    expect(load).toHaveBeenCalledOnce();

    first.resolve([{ code: "old" }]);
    await waitFor(() => load.mock.calls.length === 2);
    expect(readCachedBuildDiagnostics(baseRequest.projectRoot, baseRequest.strictMetadata)).toEqual([{ code: "old" }]);

    second.resolve([{ code: "new" }]);
    await expect(Promise.all([firstResult, latestResult, newestResult])).resolves.toEqual([
      [{ code: "new" }],
      [{ code: "new" }],
      [{ code: "new" }]
    ]);
    expect(readCachedBuildDiagnostics(baseRequest.projectRoot, baseRequest.strictMetadata)).toEqual([{ code: "new" }]);
  });

  it("retains stale diagnostics when the newest revalidation fails", async () => {
    const load = vi.fn()
      .mockResolvedValueOnce([{ code: "last-good" }])
      .mockRejectedValueOnce(new Error("inspection failed"));
    const baseRequest = { load, projectRoot: "/workspace/PIHC3", strictMetadata: true };

    await loadCachedBuildDiagnostics({ ...baseRequest, generation: 5 });
    await expect(loadCachedBuildDiagnostics({ ...baseRequest, generation: 6 })).rejects.toThrow("inspection failed");

    expect(readCachedBuildDiagnostics(baseRequest.projectRoot, baseRequest.strictMetadata)).toEqual([
      { code: "last-good" }
    ]);
    await expect(loadCachedBuildDiagnostics({ ...baseRequest, generation: 6 })).rejects.toThrow("inspection failed");
    expect(load).toHaveBeenCalledTimes(2);
  });
});

function deferred<Value>() {
  let resolve!: (value: Value) => void;
  let reject!: (reason: unknown) => void;
  const promise = new Promise<Value>((resolvePromise, rejectPromise) => {
    resolve = resolvePromise;
    reject = rejectPromise;
  });
  return { promise, reject, resolve };
}

async function waitFor(predicate: () => boolean): Promise<void> {
  for (let attempt = 0; attempt < 20; attempt += 1) {
    if (predicate()) {
      return;
    }
    await Promise.resolve();
  }
  throw new Error("Timed out waiting for condition.");
}
