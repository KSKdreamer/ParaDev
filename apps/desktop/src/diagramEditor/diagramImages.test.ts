import { describe, expect, it, vi } from "vitest";
import { diagramImageCacheKey, diagramImageHydrationSideLength, isDirectDiagramImageUrl, loadDiagramImageUrls } from "./diagramImages";
import type { DiagramNode } from "./layoutModel";

function localImageNodes(count: number): DiagramNode[] {
  return Array.from({ length: count }, (_, index) => ({
    id: `TECH_${index.toString().padStart(3, "0")}`,
    order: index,
    mode: "absolute",
    x: index,
    y: 0,
    width: 4,
    height: 2,
    imageUrl: `src/modules/technology/TECH_${index.toString().padStart(3, "0")}/icon.png`
  }));
}

function deferred<Value>(): {
  promise: Promise<Value>;
  reject: (reason: unknown) => void;
  resolve: (value: Value) => void;
} {
  let reject!: (reason: unknown) => void;
  let resolve!: (value: Value) => void;
  const promise = new Promise<Value>((resolvePromise, rejectPromise) => {
    resolve = resolvePromise;
    reject = rejectPromise;
  });
  return { promise, reject, resolve };
}

describe("diagram image loading", () => {
  it("identifies browser-addressable image URLs that do not need source hydration", () => {
    expect(isDirectDiagramImageUrl("asset://focus.png")).toBe(true);
    expect(isDirectDiagramImageUrl("data:image/png;base64,cG5n")).toBe(true);
    expect(isDirectDiagramImageUrl("blob:focus")).toBe(true);
    expect(isDirectDiagramImageUrl("https://example.test/focus.png")).toBe(true);
    expect(isDirectDiagramImageUrl("/workspace/projects/PIHC3/icon.png")).toBe(false);
    expect(isDirectDiagramImageUrl("src/modules/technology/TECH_ALPHA/icon.png")).toBe(false);
  });

  it("loads local diagram node image paths through the thumbnail cache pipeline", async () => {
    const nodes: DiagramNode[] = [
      { id: "TECH_ALPHA", order: 0, mode: "absolute", x: 0, y: 0, width: 4, height: 2, imageUrl: "src/modules/technology/TECH_ALPHA/icon.png" },
      { id: "TECH_BETA", order: 1, mode: "absolute", x: 1, y: 0, width: 4, height: 2, imageUrl: "asset://tech-beta.png" },
      { id: "TECH_EMPTY", order: 2, mode: "auto", width: 4, height: 2 }
    ];
    const calls: Array<{ cacheKey: string; sourcePaths: string[]; transform: string }> = [];
    const urls = await loadDiagramImageUrls(
      {
        nodes,
        projectRoot: "/workspace/projects/PIHC3",
        sideLength: 30
      },
      async (request) => {
        calls.push({ cacheKey: request.cacheKey, sourcePaths: request.sourcePaths, transform: typeof request.transform });
        return "data:image/png;base64,dGVjaA==";
      }
    );

    expect(urls).toEqual({ TECH_ALPHA: "data:image/png;base64,dGVjaA==" });
    expect(calls).toEqual([
      {
        cacheKey: "v1|diagram|60|TECH_ALPHA|src/modules/technology/TECH_ALPHA/icon.png",
        sourcePaths: ["src/modules/technology/TECH_ALPHA/icon.png"],
        transform: "function"
      }
    ]);
    expect(diagramImageHydrationSideLength(30)).toBe(60);
    expect(diagramImageCacheKey(nodes[0], 60)).toBe("v1|diagram|60|TECH_ALPHA|src/modules/technology/TECH_ALPHA/icon.png");
  });

  it("uses per-node thumbnail sizes so compact focus previews stay below a 2x2 grid tile", async () => {
    const nodes: DiagramNode[] = [
      {
        id: "FOCUS_C08_UPRISE",
        order: 0,
        mode: "absolute",
        x: 0,
        y: 0,
        width: 2,
        height: 2,
        imageUrl: "src/modules/focus_tree/C08_MAIN/icons/FOCUS_C08_UPRISE.png",
        payload: { embeddedKind: "focus" }
      },
      { id: "TECH_ALPHA", order: 1, mode: "absolute", x: 4, y: 0, width: 4, height: 2, imageUrl: "src/modules/technology/TECH_ALPHA/icon.png" }
    ];
    const cacheKeys: string[] = [];
    const urls = await loadDiagramImageUrls(
      {
        nodes,
        projectRoot: "/workspace/projects/PIHC3",
        sideLength: (node) => (node.payload && typeof node.payload === "object" ? 34 : 30)
      },
      async (request) => {
        cacheKeys.push(request.cacheKey);
        return `data:image/png;base64,${request.cacheKey.includes("|68|") ? "Zm9jdXM=" : "dGVjaA=="}`;
      }
    );

    expect(urls).toEqual({
      FOCUS_C08_UPRISE: "data:image/png;base64,Zm9jdXM=",
      TECH_ALPHA: "data:image/png;base64,dGVjaA=="
    });
    expect(cacheKeys).toEqual([
      "v1|diagram|68|FOCUS_C08_UPRISE|src/modules/focus_tree/C08_MAIN/icons/FOCUS_C08_UPRISE.png",
      "v1|diagram|60|TECH_ALPHA|src/modules/technology/TECH_ALPHA/icon.png"
    ]);
  });

  it("keeps hydrated node images when a neighboring local icon cannot be loaded", async () => {
    const nodes: DiagramNode[] = [
      {
        id: "FOCUS_C08_READY",
        order: 0,
        mode: "absolute",
        x: 0,
        y: 0,
        width: 1,
        height: 1,
        imageUrl: "src/modules/focus_tree/C08_MAIN/icons/FOCUS_C08_READY.png",
        payload: { embeddedKind: "focus" }
      },
      {
        id: "FOCUS_C08_MISSING",
        order: 1,
        mode: "absolute",
        x: 1,
        y: 0,
        width: 1,
        height: 1,
        imageUrl: "src/modules/focus_tree/C08_MAIN/icons/FOCUS_C08_MISSING.png",
        payload: { embeddedKind: "focus" }
      }
    ];

    const urls = await loadDiagramImageUrls(
      {
        nodes,
        projectRoot: "/workspace/projects/PIHC3",
        sideLength: 34
      },
      async (request) => {
        if (request.cacheKey.includes("FOCUS_C08_MISSING")) {
          throw new Error("missing migrated focus preview");
        }
        return "data:image/png;base64,cmVhZHk=";
      }
    );

    expect(urls).toEqual({
      FOCUS_C08_READY: "data:image/png;base64,cmVhZHk="
    });
  });

  it("reports per-node local image hydration progress", async () => {
    const nodes: DiagramNode[] = [
      {
        id: "FOCUS_READY",
        order: 0,
        mode: "absolute",
        x: 0,
        y: 0,
        width: 1,
        height: 1,
        imageUrl: "src/modules/focus_tree/C08_MAIN/icons/FOCUS_READY.png",
        payload: { embeddedKind: "focus" }
      },
      {
        id: "FOCUS_MISSING",
        order: 1,
        mode: "absolute",
        x: 1,
        y: 0,
        width: 1,
        height: 1,
        imageUrl: "src/modules/focus_tree/C08_MAIN/icons/FOCUS_MISSING.png",
        payload: { embeddedKind: "focus" }
      }
    ];
    const progress: Array<{ completed: number; hydrated: number; total: number }> = [];

    await loadDiagramImageUrls(
      {
        nodes,
        onProgress: (entry) => progress.push(entry),
        projectRoot: "/workspace/projects/PIHC3",
        sideLength: 34
      },
      async (request) => (request.cacheKey.includes("FOCUS_MISSING") ? "" : "data:image/png;base64,cmVhZHk=")
    );

    expect(progress).toEqual([
      { completed: 0, hydrated: 0, total: 2 },
      { completed: 1, hydrated: 1, total: 2 },
      { completed: 2, hydrated: 1, total: 2 }
    ]);
  });

  it("bounds PIHC3-scale hydration to four native and image-decoder requests", async () => {
    const nodes = localImageNodes(281);
    let active = 0;
    let maximumActive = 0;
    let release!: () => void;
    const gate = new Promise<void>((resolve) => {
      release = resolve;
    });

    const resultPromise = loadDiagramImageUrls(
      {
        nodes,
        projectRoot: "/workspace/projects/PIHC3",
        sideLength: 30
      },
      async (request) => {
        active += 1;
        maximumActive = Math.max(maximumActive, active);
        await gate;
        active -= 1;
        return `hydrated:${request.cacheKey}`;
      }
    );

    expect(active).toBe(4);
    expect(maximumActive).toBe(4);
    release();
    const urls = await resultPromise;

    expect(maximumActive).toBe(4);
    expect(active).toBe(0);
    expect(Object.keys(urls)).toEqual(nodes.map((node) => node.id));
  });

  it("isolates out-of-order failures while reporting monotonic progress totals", async () => {
    const nodes = localImageNodes(7);
    const jobs = new Map<string, ReturnType<typeof deferred<string>>>();
    const started: string[] = [];
    const progress: Array<{ completed: number; hydrated: number; total: number }> = [];
    const resultPromise = loadDiagramImageUrls(
      {
        nodes,
        onProgress: (entry) => progress.push(entry),
        projectRoot: "/workspace/projects/PIHC3",
        sideLength: 30
      },
      (request) => {
        const nodeId = request.cacheKey.split("|")[3];
        if (!nodeId) throw new Error("missing node identity in diagram image cache key");
        const job = deferred<string>();
        jobs.set(nodeId, job);
        started.push(nodeId);
        return job.promise;
      }
    );

    expect(started).toEqual(["TECH_000", "TECH_001", "TECH_002", "TECH_003"]);
    jobs.get("TECH_002")?.reject(new Error("corrupt technology icon"));
    await vi.waitFor(() => expect(started).toContain("TECH_004"));
    jobs.get("TECH_000")?.resolve("hydrated:TECH_000");
    await vi.waitFor(() => expect(started).toContain("TECH_005"));
    jobs.get("TECH_004")?.resolve("hydrated:TECH_004");
    await vi.waitFor(() => expect(started).toContain("TECH_006"));
    jobs.get("TECH_006")?.resolve("hydrated:TECH_006");
    jobs.get("TECH_001")?.resolve("hydrated:TECH_001");
    jobs.get("TECH_005")?.resolve("hydrated:TECH_005");
    jobs.get("TECH_003")?.resolve("hydrated:TECH_003");

    const urls = await resultPromise;

    expect(Object.keys(urls)).toEqual(["TECH_000", "TECH_001", "TECH_003", "TECH_004", "TECH_005", "TECH_006"]);
    expect(progress).toHaveLength(nodes.length + 1);
    expect(progress.map((entry) => entry.completed)).toEqual([0, 1, 2, 3, 4, 5, 6, 7]);
    expect(progress.every((entry) => entry.total === nodes.length)).toBe(true);
    expect(progress.at(-1)).toEqual({ completed: nodes.length, hydrated: nodes.length - 1, total: nodes.length });
    for (const [index, entry] of progress.entries()) {
      const previous = progress[index - 1];
      if (!previous) continue;
      expect(entry.completed).toBeGreaterThanOrEqual(previous.completed);
      expect(entry.hydrated).toBeGreaterThanOrEqual(previous.hydrated);
      expect(entry.hydrated).toBeLessThanOrEqual(entry.completed);
    }
  });
});
