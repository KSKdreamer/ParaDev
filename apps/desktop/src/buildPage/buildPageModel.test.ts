import { describe, expect, it } from "vitest";
import { DESKTOP_CONFIG_KEYS } from "../desktopConfig";
import { PARADEV_DESKTOP_CONFIG_DEFAULTS, PARADEV_DESKTOP_CONFIG_ROWS } from "../generated/desktopContract";
import type { ProjectBrowserPayload, ProjectOption } from "../types";
import {
  BUILD_HOI4_LAUNCH_MODE_VALUES,
  BUILD_PARALLELISM_MIN,
  averageBuildDurationMs,
  buildBuildDashboardModel,
  buildFamilyTargetForBrowser,
  buildOverviewRuntime,
  buildOutputOpenPath,
  buildParallelismFromConfig,
  buildRunGameDisabled,
  formatBuildDuration,
  hoi4LaunchModeFromConfig,
  hoi4GameRootFromConfig,
  nextBuildRuntime,
  readBuildHistory,
  readBuildHistoryTombstones,
  readBuildPageSettings,
  recordBuildHistoryEntry,
  removeBuildHistoryEntry,
  resolveBuildTargetForBrowser,
  sameBuildTarget,
  strictMetadataFromConfig,
  writeBuildPageSettings
} from "./buildPageModel";

const pihc3Project: ProjectOption = {
  id: "PIHC3",
  projectId: "PIHC3",
  name: "Project Ideology in Hearts of Iron III",
  path: "/workspace/projects/PIHC3",
  game: "hoi4",
  manifest: "/workspace/projects/PIHC3/paradev.yaml",
  outputRoot: "/Users/magolor/Documents/Paradox Interactive/Hearts of Iron IV/mod/PIHC3"
};

const pihc3Browser: ProjectBrowserPayload = {
  schema: "paradev.sdk.project-browser.v1",
  project_id: "PIHC3",
  title: "Project Ideology in Hearts of Iron III",
  root: "/workspace/projects/PIHC3",
  profile: "hoi4",
  filters: {},
  families: [
    { id: "focus-tree", family: "focus_tree", aliases: ["focuses"], title: "National Focuses", item_count: 42, source_count: 126, layouts: ["canonical"] },
    { id: "technology", family: "technology", title: "Technologies", item_count: 18, source_count: 39, layouts: ["canonical"] },
    { id: "idea", family: "idea", title: "Ideas", item_count: 64, source_count: 71, layouts: ["canonical"] }
  ],
  items: [
    {
      id: "focus_tree/GER_main",
      kind: "module",
      layout: "canonical",
      family_id: "focus-tree",
      family: "focus_tree",
      object_id: "GER_main",
      module_id: "focus_tree/GER_main",
      title: "German focus tree",
      root: "/workspace/projects/PIHC3/src/focus_tree/GER_main",
      relative_root: "src/focus_tree/GER_main",
      source_count: 3,
      sources: [
        { slot: "focuses", name: "focuses.txt", path: "/workspace/projects/PIHC3/src/focus_tree/GER_main/focuses.txt", relative_path: "focuses.txt", extension: ".txt" },
        { slot: "localization", name: "focus_l_english.yml", path: "/workspace/projects/PIHC3/src/focus_tree/GER_main/focus_l_english.yml", relative_path: "focus_l_english.yml", extension: ".yml" },
        { slot: "metadata", name: "paradev.yaml", path: "/workspace/projects/PIHC3/src/focus_tree/GER_main/paradev.yaml", relative_path: "paradev.yaml", extension: ".yaml" }
      ]
    },
    {
      id: "GER",
      kind: "collection",
      layout: "canonical",
      family_id: "countries",
      family: "country",
      object_id: "GER",
      collection_id: "GER",
      title: "Germany",
      root: "/workspace/projects/PIHC3/src/country/GER",
      relative_root: "src/country/GER",
      source_count: 1,
      sources: [
        { slot: "metadata", name: "paradev.yaml", path: "/workspace/projects/PIHC3/src/country/GER/paradev.yaml", relative_path: "paradev.yaml", extension: ".yaml" }
      ]
    }
  ],
  diagnostics: [
    { code: "decision.missing_collection", severity: "warning" },
    { code: "sprite.unreadable_source", severity: "error" }
  ]
};

describe("build dashboard model", () => {
  it("matches build targets with the same identity as the Python and native registries", () => {
    expect(sameBuildTarget(null, undefined)).toBe(true);
    expect(
      sameBuildTarget(
        { family: "focus_tree", id: "focus_tree/GER_main", kind: "module" },
        { id: "focus_tree/GER_main", kind: "module" }
      )
    ).toBe(true);
    expect(
      sameBuildTarget(
        { family: "legacy_family", id: "focus_tree", kind: "family" },
        { family: "focus_tree", id: "focus_tree", kind: "family" }
      )
    ).toBe(true);
    expect(
      sameBuildTarget(
        { family: "focus_tree", id: "shared", kind: "collection" },
        { id: "shared", kind: "collection" }
      )
    ).toBe(true);
    expect(
      sameBuildTarget(
        { family: "focus_tree", id: "shared", kind: "collection" },
        { family: "idea", id: "shared", kind: "collection" }
      )
    ).toBe(false);
    expect(
      sameBuildTarget(
        { id: "focus_tree/GER_main", kind: "module" },
        { id: "focus_tree/ITA_main", kind: "module" }
      )
    ).toBe(false);
    expect(
      sameBuildTarget(
        { id: "focus_tree", kind: "family" },
        { id: "focus_tree", kind: "module" }
      )
    ).toBe(false);
  });

  it("resolves editor family ids to the build-authoritative family target", () => {
    expect(buildFamilyTargetForBrowser(pihc3Browser, "focuses")).toEqual({
      family: "focus_tree",
      id: "focus_tree",
      kind: "family"
    });
    expect(buildFamilyTargetForBrowser(pihc3Browser, "technology")).toEqual({
      family: "technology",
      id: "technology",
      kind: "family"
    });
    expect(
      buildFamilyTargetForBrowser(
        {
          ...pihc3Browser,
          families: [
            { id: "focus", family: "focus", title: "Focus", item_count: 1, source_count: 1, layouts: [] },
            ...pihc3Browser.families
          ]
        },
        "focus_tree"
      )
    ).toEqual({ family: "focus_tree", id: "focus_tree", kind: "family" });
    expect(buildFamilyTargetForBrowser({ ...pihc3Browser, families: [] }, "focuses")).toBeNull();
  });

  it("resolves module intents from browser items when dashboard rows collapse to families", () => {
    expect(
      resolveBuildTargetForBrowser(pihc3Browser, {
        family: "focuses",
        id: "module:focus_tree/GER_main",
        kind: "module"
      })
    ).toEqual({
      family: "focus_tree",
      id: "focus_tree/GER_main",
      kind: "module"
    });
    expect(
      resolveBuildTargetForBrowser(pihc3Browser, {
        family: "focus_tree",
        id: "GER_main",
        kind: "module"
      })
    ).toEqual({
      family: "focus_tree",
      id: "focus_tree/GER_main",
      kind: "module"
    });
    expect(
      resolveBuildTargetForBrowser(pihc3Browser, {
        family: "technology",
        id: "focus_tree/GER_main",
        kind: "module"
      })
    ).toBeNull();
    expect(
      resolveBuildTargetForBrowser(pihc3Browser, {
        family: "focus_tree",
        id: "focus_tree/MISSING",
        kind: "module"
      })
    ).toBeNull();
  });

  it("derives a compact build dashboard from real browser counts and family buildables", () => {
    const model = buildBuildDashboardModel({
      browser: pihc3Browser,
      mode: "cached",
      project: pihc3Project,
      runtime: { mode: "cached", progress: null, state: "idle" }
    });

    expect(model.projectId).toBe("PIHC3");
    expect(model.summary.moduleCount).toBe(124);
    expect(model.summary.collectionCount).toBe(1);
    expect(model.summary.sourceCount).toBe(236);
    expect(model.summary.diagnosticCount).toBe(2);
    expect(model.summary.errorCount).toBe(1);
    expect(model.summary.blocked).toBe(true);
    expect(model.entities.map((entity) => entity.id)).toEqual(["focus_tree", "technology", "idea"]);
    expect(model.entities[0]).toMatchObject({
      kind: "family",
      progressLabel: "126 / 126 sources",
      progressPercent: 100,
      sourceCount: 126,
      title: "National Focuses",
      target: { family: "focus_tree", id: "focus_tree", kind: "family" }
    });
    expect("cacheHitRate" in model).toBe(false);
    expect("operations" in model).toBe(false);
    expect("pipeline" in model).toBe(false);
    expect("scripts" in model).toBe(false);
  });

  it("uses authoritative summary groups to separate modules from collections", () => {
    const summaryBrowser: ProjectBrowserPayload = {
      ...pihc3Browser,
      groups: [
        {
          collection_count: 2,
          family: "focus_tree",
          id: "focus-tree",
          item_count: 42,
          module_count: 40
        },
        {
          collection_count: 0,
          family: "technology",
          id: "technology",
          item_count: 18,
          module_count: 18
        },
        {
          collection_count: 1,
          family: "idea",
          id: "idea",
          item_count: 64,
          module_count: 63
        }
      ],
      items: []
    };

    const model = buildBuildDashboardModel({
      browser: summaryBrowser,
      mode: "cached",
      project: pihc3Project,
      runtime: { mode: "cached", progress: null, state: "idle" }
    });

    expect(model.summary.moduleCount).toBe(121);
    expect(model.summary.collectionCount).toBe(3);
    expect(model.summary.moduleCount + model.summary.collectionCount).toBe(124);
  });

  it("treats ready compiler state as fully complete", () => {
    const model = buildBuildDashboardModel({
      browser: { ...pihc3Browser, diagnostics: [] },
      mode: "cached",
      project: pihc3Project,
      runtime: { mode: "cached", progress: null, state: "idle" }
    });

    expect(model.status).toMatchObject({
      progress: 100,
      state: "ready"
    });
    expect(model.progress.percent).toBe(100);
  });

  it.each(["failed", "interrupted"] as const)(
    "shows a %s build with no compiler snapshot at zero progress",
    (state) => {
      const target = { family: "focus_tree", id: "focus_tree", kind: "family" as const };
      const runtime = { mode: "cached" as const, progress: null, state, target };
      const model = buildBuildDashboardModel({
        browser: { ...pihc3Browser, diagnostics: [] },
        mode: "cached",
        project: pihc3Project,
        runtime,
        runtimes: [runtime]
      });

      expect(model.status).toMatchObject({ progress: 0, state });
      expect(model.progress.percent).toBe(0);
      expect(model.entities[0]).toMatchObject({ progressPercent: 0, status: state });
    }
  );

  it("shows a newly started compiler as waiting at zero progress", () => {
    const model = buildBuildDashboardModel({
      browser: { ...pihc3Browser, diagnostics: [] },
      mode: "cached",
      project: pihc3Project,
      runtime: { mode: "cached", progress: null, state: "running" }
    });

    expect(model.status).toMatchObject({ progress: 0, state: "running" });
    expect(model.progress).toMatchObject({ percent: 0, phase: "waiting" });
  });

  it("uses SDK build diagnostics as the blocked source of truth when available", () => {
    const blocked = buildBuildDashboardModel({
      browser: { ...pihc3Browser, diagnostics: [] },
      buildDiagnostics: [{ code: "metadata.unknown_key", severity: "error" }],
      mode: "cached",
      project: pihc3Project,
      runtime: { mode: "cached", progress: null, state: "idle" }
    });
    const ready = buildBuildDashboardModel({
      browser: pihc3Browser,
      buildDiagnostics: [],
      mode: "cached",
      project: pihc3Project,
      runtime: { mode: "cached", progress: null, state: "idle" }
    });

    expect(blocked.summary).toMatchObject({ blocked: true, diagnosticCount: 1, errorCount: 1 });
    expect(blocked.status.state).toBe("blocked");
    expect(blocked.entities.every((entity) => entity.status === "blocked")).toBe(true);
    expect(ready.summary).toMatchObject({ blocked: false, diagnosticCount: 0, errorCount: 0 });
    expect(ready.status.state).toBe("ready");
  });

  it("uses compiler progress payloads without simulating cache or time estimates", () => {
    const model = buildBuildDashboardModel({
      browser: pihc3Browser,
      mode: "cached",
      project: pihc3Project,
      runtime: {
        mode: "cached",
        progress: {
          phase: "artifact_generation",
          label: "Writing artifacts",
          detail: "Writing output files",
          index: 31,
          total: 50,
          percent: 62
        },
        state: "running"
      }
    });

    expect(model.status.label).toBe("Compilation running");
    expect(model.status.progress).toBe(62);
    expect(model.progress).toMatchObject({
      label: "Writing artifacts",
      countLabel: "31 / 50",
      percent: 62
    });
  });

  it("shows active source progress on the independently rebuilt family row", () => {
    const model = buildBuildDashboardModel({
      browser: pihc3Browser,
      mode: "cached",
      project: pihc3Project,
      runtime: {
        mode: "cached",
        progress: {
          phase: "source_compile",
          index: 42,
          percent: 33,
          total: 126
        },
        state: "running",
        target: {
          family: "focus_tree",
          id: "focus_tree",
          kind: "family"
        }
      }
    });

    expect(model.entities[0]).toMatchObject({
      id: "focus_tree",
      progressLabel: "42 / 126 sources",
      progressPercent: 33
    });
    expect(model.entities[1]).toMatchObject({
      id: "technology",
      progressLabel: "39 / 39 sources",
      progressPercent: 100
    });
  });

  it("surfaces the latest partial failure on its entity without reviving stale failures", () => {
    const target = { family: "focus_tree", id: "focus_tree", kind: "family" as const };
    const failed = {
      errorSummary: "Focus compilation failed at C01_MAIN.",
      mode: "cached" as const,
      progress: { phase: "source_compile", percent: 25 },
      state: "failed" as const,
      target
    };
    const completed = {
      mode: "cached" as const,
      progress: { phase: "complete", percent: 100 },
      state: "completed" as const,
      target
    };

    const failedModel = buildBuildDashboardModel({
      browser: { ...pihc3Browser, diagnostics: [] },
      mode: "cached",
      project: pihc3Project,
      runtime: failed,
      runtimes: [failed]
    });
    const recoveredModel = buildBuildDashboardModel({
      browser: { ...pihc3Browser, diagnostics: [] },
      mode: "cached",
      project: pihc3Project,
      runtime: completed,
      runtimes: [failed, completed]
    });

    expect(failedModel.status.state).toBe("failed");
    expect(failedModel.entities[0]).toMatchObject({
      detail: "Focus compilation failed at C01_MAIN.",
      progressPercent: 25,
      status: "failed"
    });
    expect(recoveredModel.entities[0].status).toBe("ready");
  });

  it("keeps project health adverse while exposing a causally later successful partial result", () => {
    const target = { family: "focus_tree", id: "focus_tree", kind: "family" as const };
    const interruptedFull = {
      finishedAtMs: 10_000,
      mode: "cached" as const,
      progress: { phase: "source_compile", percent: 40 },
      startedAtMs: 1_000,
      state: "interrupted" as const,
      target: null,
      terminalSequence: 10
    };
    const completedPartial = {
      // The native monotonic sequence remains authoritative if the wall clock rolls back.
      finishedAtMs: 950,
      mode: "cached" as const,
      progress: { phase: "complete", percent: 100 },
      startedAtMs: 900,
      state: "completed" as const,
      target,
      terminalSequence: 11
    };
    const runtimes = [interruptedFull, completedPartial];
    const model = buildBuildDashboardModel({
      browser: { ...pihc3Browser, diagnostics: [] },
      mode: "cached",
      project: pihc3Project,
      runtime: buildOverviewRuntime(runtimes, "cached"),
      runtimes
    });

    expect(model.status.state).toBe("interrupted");
    expect(model.latestPartialResult).toEqual({
      durationMs: 50,
      finishedAtMs: 950,
      state: "completed",
      target
    });
  });

  it("hides an older partial result after a newer full-project result", () => {
    const partial = {
      finishedAtMs: 2_000,
      mode: "cached" as const,
      progress: { phase: "complete", percent: 100 },
      startedAtMs: 1_000,
      state: "completed" as const,
      target: { family: "focus_tree", id: "focus_tree", kind: "family" as const },
      terminalSequence: null
    };
    const full = {
      finishedAtMs: 4_000,
      mode: "cached" as const,
      progress: { phase: "complete", percent: 100 },
      startedAtMs: 3_000,
      state: "completed" as const,
      target: null,
      terminalSequence: null
    };
    const model = buildBuildDashboardModel({
      browser: { ...pihc3Browser, diagnostics: [] },
      mode: "cached",
      project: pihc3Project,
      runtime: buildOverviewRuntime([partial, full], "cached"),
      runtimes: [partial, full]
    });

    expect(model.status.state).toBe("completed");
    expect(model.latestPartialResult).toBeNull();
  });

  it("uses timestamps when only the older partial result has a terminal sequence", () => {
    const target = { family: "focus_tree", id: "focus_tree", kind: "family" as const };
    const olderPartial = {
      finishedAtMs: 2_000,
      mode: "cached" as const,
      progress: { phase: "complete", percent: 100 },
      runId: "older-partial",
      startedAtMs: 1_000,
      state: "completed" as const,
      target,
      terminalSequence: 7
    };
    const newerFull = {
      finishedAtMs: 4_000,
      mode: "cached" as const,
      progress: { phase: "complete", percent: 100 },
      runId: "newer-full-checkpoint",
      startedAtMs: 3_000,
      state: "completed" as const,
      target: null,
      terminalSequence: null
    };
    const runtimes = [olderPartial, newerFull];
    const model = buildBuildDashboardModel({
      browser: { ...pihc3Browser, diagnostics: [] },
      mode: "cached",
      project: pihc3Project,
      runtime: buildOverviewRuntime(runtimes, "cached"),
      runtimes
    });

    expect(buildOverviewRuntime(runtimes, "cached")).toBe(newerFull);
    expect(model.latestPartialResult).toBeNull();
  });

  it("uses timestamps when only the older full result has a terminal sequence", () => {
    const target = { family: "focus_tree", id: "focus_tree", kind: "family" as const };
    const olderFull = {
      finishedAtMs: 2_000,
      mode: "cached" as const,
      progress: { phase: "complete", percent: 100 },
      runId: "older-full",
      startedAtMs: 1_000,
      state: "completed" as const,
      target: null,
      terminalSequence: 7
    };
    const newerPartial = {
      finishedAtMs: 4_000,
      mode: "cached" as const,
      progress: { phase: "complete", percent: 100 },
      runId: "newer-partial-checkpoint",
      startedAtMs: 3_000,
      state: "completed" as const,
      target,
      terminalSequence: null
    };
    const runtimes = [olderFull, newerPartial];
    const model = buildBuildDashboardModel({
      browser: { ...pihc3Browser, diagnostics: [] },
      mode: "cached",
      project: pihc3Project,
      runtime: buildOverviewRuntime(runtimes, "cached"),
      runtimes
    });

    expect(buildOverviewRuntime(runtimes, "cached")).toBe(newerPartial);
    expect(model.latestPartialResult).toEqual({
      durationMs: 1_000,
      finishedAtMs: 4_000,
      state: "completed",
      target
    });
  });

  it("hides a terminal partial result while a newer full build is running", () => {
    const partial = {
      finishedAtMs: 2_000,
      mode: "cached" as const,
      progress: { phase: "complete", percent: 100 },
      runId: "completed-focus",
      startedAtMs: 1_000,
      state: "completed" as const,
      target: { family: "focus_tree", id: "focus_tree", kind: "family" as const },
      terminalSequence: null
    };
    const runningFull = {
      mode: "full" as const,
      progress: { phase: "discover_modules", percent: 10 },
      runId: "running-full",
      startedAtMs: 3_000,
      state: "running" as const,
      target: null
    };
    const model = buildBuildDashboardModel({
      browser: { ...pihc3Browser, diagnostics: [] },
      mode: "full",
      project: pihc3Project,
      runtime: buildOverviewRuntime([partial, runningFull], "full"),
      runtimes: [partial, runningFull]
    });

    expect(model.status.state).toBe("running");
    expect(model.latestPartialResult).toBeNull();
  });

  it("hides stale terminal activity after a newer build attempt fails before starting", () => {
    const partial = {
      finishedAtMs: 2_000,
      mode: "cached" as const,
      progress: { phase: "complete", percent: 100 },
      runId: "completed-focus",
      startedAtMs: 1_000,
      state: "completed" as const,
      target: { family: "focus_tree", id: "focus_tree", kind: "family" as const },
      terminalSequence: 20
    };
    const rejectedAttempt = {
      mode: "cached" as const,
      progress: null,
      runId: null,
      startedAtMs: 3_000,
      state: "failed" as const,
      target: { family: "technology", id: "technology", kind: "family" as const },
      terminalSequence: null
    };
    const model = buildBuildDashboardModel({
      browser: { ...pihc3Browser, diagnostics: [] },
      mode: "cached",
      project: pihc3Project,
      runtime: buildOverviewRuntime([partial, rejectedAttempt], "cached"),
      runtimes: [partial, rejectedAttempt]
    });

    expect(model.status.state).toBe("failed");
    expect(model.latestPartialResult).toBeNull();
  });

  it("shows a later terminal partial result after an older rejected sibling attempt", () => {
    const rejectedAttempt = {
      mode: "cached" as const,
      progress: null,
      runId: null,
      startedAtMs: 1_000,
      state: "failed" as const,
      target: { family: "technology", id: "technology", kind: "family" as const },
      terminalSequence: null
    };
    const laterPartial = {
      finishedAtMs: 4_000,
      mode: "cached" as const,
      progress: { phase: "complete", percent: 100 },
      runId: "completed-focus",
      startedAtMs: 3_000,
      state: "completed" as const,
      target: { family: "focus_tree", id: "focus_tree", kind: "family" as const },
      terminalSequence: 20
    };
    const model = buildBuildDashboardModel({
      browser: { ...pihc3Browser, diagnostics: [] },
      mode: "cached",
      project: pihc3Project,
      runtime: buildOverviewRuntime([rejectedAttempt, laterPartial], "cached"),
      runtimes: [rejectedAttempt, laterPartial]
    });

    expect(model.status.state).toBe("failed");
    expect(model.latestPartialResult).toMatchObject({
      state: "completed",
      target: laterPartial.target
    });
  });

  it("does not present a rejected start as a finished partial rebuild", () => {
    const rejectedAttempt = {
      mode: "cached" as const,
      progress: null,
      runId: null,
      startedAtMs: 3_000,
      state: "failed" as const,
      target: { family: "technology", id: "technology", kind: "family" as const },
      terminalSequence: null
    };
    const model = buildBuildDashboardModel({
      browser: { ...pihc3Browser, diagnostics: [] },
      mode: "cached",
      project: pihc3Project,
      runtime: buildOverviewRuntime([rejectedAttempt], "cached"),
      runtimes: [rejectedAttempt]
    });

    expect(model.status.state).toBe("failed");
    expect(model.latestPartialResult).toBeNull();
  });

  it("stores all build histories while cached estimates use only the latest cached full build", () => {
    const storage = new MemoryStorage();
    const startedAtMs = 1_000;

    [10, 20, 30, 40, 50, 60].forEach((seconds, index) => {
      recordBuildHistoryEntry(
        {
          durationMs: seconds * 1000,
          finishedAtMs: startedAtMs + seconds * 1000,
          id: `build-${index + 1}`,
          mode: "cached",
          projectId: "PIHC3",
          projectRoot: pihc3Project.path,
          startedAtMs,
          status: "completed"
        },
        storage
      );
    });
    recordBuildHistoryEntry(
      {
        durationMs: 5_000,
        finishedAtMs: 90_000,
        id: "failed-build",
        mode: "cached",
        projectId: "PIHC3",
        projectRoot: pihc3Project.path,
        startedAtMs,
        status: "failed"
      },
      storage
    );

    const history = readBuildHistory(storage);

    expect(history).toHaveLength(7);
    expect(averageBuildDurationMs(history, pihc3Project.path)).toBe(40_000);
    expect(formatBuildDuration(40_000)).toBe("40s");
    expect(
      buildBuildDashboardModel({
        browser: pihc3Browser,
        history,
        mode: "cached",
        project: pihc3Project,
        runtime: { mode: "cached", progress: null, state: "idle" }
      }).estimate
    ).toMatchObject({
      durationLabel: "1m",
      sampleCount: 1
    });
  });

  it("keeps explicit history removals durable with a bounded tombstone set", () => {
    const storage = new MemoryStorage();
    const removedEntry = {
      durationMs: 1_000,
      finishedAtMs: 2_000,
      id: "deleted-build",
      mode: "cached" as const,
      projectId: "PIHC3",
      projectRoot: pihc3Project.path,
      startedAtMs: 1_000,
      status: "completed" as const
    };

    recordBuildHistoryEntry(removedEntry, storage);
    expect(readBuildHistory(storage)).toHaveLength(1);

    expect(removeBuildHistoryEntry(removedEntry.id, storage)).toEqual([]);
    expect(readBuildHistoryTombstones(storage)).toContain(removedEntry.id);
    expect(recordBuildHistoryEntry(removedEntry, storage)).toEqual([]);

    for (let index = 0; index < 600; index += 1) {
      removeBuildHistoryEntry(`removed-${index}`, storage);
    }
    const tombstones = readBuildHistoryTombstones(storage);
    expect(tombstones).toHaveLength(512);
    expect(tombstones).not.toContain("removed-0");
    expect(tombstones).toContain("removed-599");
  });

  it("bounds persisted history to the newest 256 records", () => {
    const storage = new MemoryStorage();
    for (let index = 0; index < 300; index += 1) {
      recordBuildHistoryEntry(
        {
          durationMs: 1_000,
          finishedAtMs: index + 2,
          id: `build-${index}`,
          mode: "cached",
          projectId: "PIHC3",
          projectRoot: pihc3Project.path,
          startedAtMs: index + 1,
          status: "completed"
        },
        storage
      );
    }

    const history = readBuildHistory(storage);
    expect(history).toHaveLength(256);
    expect(history[0]?.id).toBe("build-44");
    expect(history.at(-1)?.id).toBe("build-299");
  });

  it("keeps histories and estimates isolated by project root when manifest ids collide", () => {
    const cloneRoot = "/workspace/clones/PIHC3";
    const history = [
      {
        durationMs: 10_000,
        finishedAtMs: 11_000,
        id: "original-build",
        mode: "cached" as const,
        projectId: "PIHC3",
        projectRoot: pihc3Project.path,
        startedAtMs: 1_000,
        status: "completed" as const
      },
      {
        command: ["private-clone-command"],
        durationMs: 90_000,
        finishedAtMs: 91_000,
        id: "clone-build",
        mode: "cached" as const,
        outputPath: "/private/clone/output",
        projectId: "PIHC3",
        projectRoot: cloneRoot,
        startedAtMs: 1_000,
        status: "completed" as const
      }
    ];

    expect(averageBuildDurationMs(history, pihc3Project.path)).toBe(10_000);
    expect(averageBuildDurationMs(history, cloneRoot)).toBe(90_000);
    expect(
      buildBuildDashboardModel({
        browser: pihc3Browser,
        history,
        mode: "cached",
        project: pihc3Project,
        runtime: { mode: "cached", progress: null, state: "idle" }
      }).estimate.durationMs
    ).toBe(10_000);
  });

  it("treats throwing browser storage as best-effort", () => {
    const storage = new ThrowingStorage();
    const entry = {
      durationMs: 1_000,
      finishedAtMs: 2_000,
      id: "completed-build",
      mode: "cached" as const,
      projectId: "PIHC3",
      projectRoot: pihc3Project.path,
      startedAtMs: 1_000,
      status: "completed" as const
    };

    expect(() => readBuildHistory(storage)).not.toThrow();
    expect(recordBuildHistoryEntry(entry, storage)).toMatchObject([entry]);
    expect(() => removeBuildHistoryEntry(entry.id, storage)).not.toThrow();
  });

  it("uses the latest five completed full builds for full rebuild estimates", () => {
    const storage = new MemoryStorage();
    const startedAtMs = 1_000;

    [10, 20, 30, 40, 50, 60].forEach((seconds, index) => {
      recordBuildHistoryEntry(
        {
          durationMs: seconds * 1000,
          finishedAtMs: startedAtMs + seconds * 1000,
          id: `full-build-${index + 1}`,
          mode: "full",
          projectId: "PIHC3",
          projectRoot: pihc3Project.path,
          startedAtMs,
          status: "completed"
        },
        storage
      );
    });

    const history = readBuildHistory(storage);

    expect(
      buildBuildDashboardModel({
        browser: pihc3Browser,
        history,
        mode: "full",
        project: pihc3Project,
        runtime: { mode: "full", progress: null, state: "idle" }
      }).estimate
    ).toMatchObject({
      durationLabel: "40s",
      sampleCount: 5
    });
  });

  it("excludes partial rebuilds from full-build duration estimates", () => {
    const storage = new MemoryStorage();
    const startedAtMs = 1_000;

    [3, 5, 7, 11, 13].forEach((seconds, index) => {
      recordBuildHistoryEntry(
        {
          durationMs: seconds * 1000,
          finishedAtMs: startedAtMs + seconds * 1000,
          id: `partial-build-${index + 1}`,
          mode: "cached",
          projectId: "PIHC3",
          projectRoot: pihc3Project.path,
          startedAtMs,
          status: "completed",
          target: {
            family: "focus_tree",
            id: `focus_tree/GER_${index + 1}`,
            kind: "module"
          }
        },
        storage
      );
    });
    recordBuildHistoryEntry(
      {
        durationMs: 42_000,
        finishedAtMs: 120_000,
        id: "full-build",
        mode: "cached",
        projectId: "PIHC3",
        projectRoot: pihc3Project.path,
        startedAtMs,
        status: "completed",
        target: null
      },
      storage
    );

    const history = readBuildHistory(storage);

    expect(history).toHaveLength(6);
    expect(averageBuildDurationMs(history, pihc3Project.path, "cached")).toBe(42_000);
    expect(
      buildBuildDashboardModel({
        browser: pihc3Browser,
        history,
        mode: "cached",
        project: pihc3Project,
        runtime: { mode: "cached", progress: null, state: "idle" }
      }).estimate
    ).toMatchObject({
      durationLabel: "42s",
      sampleCount: 1
    });

    expect(
      buildBuildDashboardModel({
        browser: pihc3Browser,
        history,
        mode: "cached",
        project: pihc3Project,
        runtime: {
          mode: "cached",
          progress: { phase: "source_compile", percent: 25 },
          state: "running",
          target: { family: "focus_tree", id: "focus_tree", kind: "family" }
        }
      }).estimate
    ).toMatchObject({
      durationLabel: "",
      sampleCount: 0
    });
  });

  it("normalizes native history records for full-build estimates", () => {
    const storage = new MemoryStorage();
    storage.setItem(
      "paradev.build.history.v2",
      JSON.stringify([
        {
          duration_ms: 11_000,
          finished_at_ms: 12_000,
          mode: "full",
          project_id: "PIHC3",
          project_root: pihc3Project.path,
          run_id: "native-build-1",
          started_at_ms: 1_000,
          status: "success",
          target: null
        },
        {
          duration_ms: 13_000,
          finished_at_ms: 24_000,
          mode: "full",
          project_id: "PIHC3",
          project_root: pihc3Project.path,
          run_id: "native-build-2",
          started_at_ms: 11_000,
          status: "completed",
          target: null
        }
      ])
    );

    const history = readBuildHistory(storage);

    expect(history).toHaveLength(2);
    expect(history[0]).toMatchObject({
      durationMs: 11_000,
      id: "native-build-1",
      projectId: "PIHC3",
      status: "completed"
    });
    expect(
      buildBuildDashboardModel({
        browser: pihc3Browser,
        history,
        mode: "full",
        project: pihc3Project,
        runtime: { mode: "full", progress: null, state: "idle" }
      }).estimate
    ).toMatchObject({
      durationLabel: "12s",
      sampleCount: 2
    });
  });

  it("preserves failed build reasons from native history records", () => {
    const storage = new MemoryStorage();
    storage.setItem(
      "paradev.build.history.v2",
      JSON.stringify([
        {
          command: ["uv", "run", "paradev", "build"],
          duration_ms: 7_000,
          error_path: "/tmp/paradev-build/build-1.stderr.log",
          error_summary: "RuntimeError: metadata schema unavailable.",
          exit_code: 2,
          finished_at_ms: 8_000,
          mode: "cached",
          output_path: "/tmp/paradev-build/build-1.json",
          project_id: "PIHC3",
          project_root: pihc3Project.path,
          run_id: "failed-build",
          started_at_ms: 1_000,
          status: "failed",
          target: null
        }
      ])
    );

    const history = readBuildHistory(storage);

    expect(history[0]).toMatchObject({
      command: ["uv", "run", "paradev", "build"],
      errorPath: "/tmp/paradev-build/build-1.stderr.log",
      errorSummary: "RuntimeError: metadata schema unavailable.",
      exitCode: 2,
      id: "failed-build",
      outputPath: "/tmp/paradev-build/build-1.json",
      status: "failed"
    });
  });

  it("resolves the compiled output path from project metadata before falling back to HOI4 defaults", () => {
    expect(buildOutputOpenPath(pihc3Project)).toBe("/Users/magolor/Documents/Paradox Interactive/Hearts of Iron IV/mod/PIHC3");
    expect(
      buildOutputOpenPath({
        ...pihc3Project,
        outputRoot: undefined,
        path: "/Users/magolor/Utils/ParaDev-3/projects/PIHC3"
      })
    ).toBe("/Users/magolor/Documents/Paradox Interactive/Hearts of Iron IV/mod/PIHC3");
  });

  it("advances only real desktop build states", () => {
    const initial = { mode: "cached", progress: null, state: "idle" } as const;
    const running = nextBuildRuntime(initial, "start", "full");
    const interrupted = nextBuildRuntime(running, "interrupt");

    expect(running).toMatchObject({ mode: "full", progress: null, state: "running" });
    expect(interrupted).toMatchObject({ mode: "full", state: "interrupted" });
  });

  it("persists only local build dropdown settings with safe defaults", () => {
    const storage = new MemoryStorage();
    const sdkBackedDefaults = {
      buildMode: "cached",
      launchMode: PARADEV_DESKTOP_CONFIG_DEFAULTS[DESKTOP_CONFIG_KEYS.hoi4LaunchMode],
      parallelism: PARADEV_DESKTOP_CONFIG_DEFAULTS[DESKTOP_CONFIG_KEYS.buildParallelism],
      strictMetadata: PARADEV_DESKTOP_CONFIG_DEFAULTS[DESKTOP_CONFIG_KEYS.buildStrictMetadata]
    };
    storage.setItem("paradev.build.launchMode", "local");
    storage.setItem("paradev.build.strictMetadata", "true");

    expect(readBuildPageSettings(storage)).toEqual(sdkBackedDefaults);

    writeBuildPageSettings({ buildMode: "full", launchMode: "local", parallelism: 4, strictMetadata: false }, storage);

    expect(readBuildPageSettings(storage)).toEqual({ ...sdkBackedDefaults, buildMode: "full" });
    expect(storage.getItem("paradev.build.launchMode")).toBeNull();
    expect(storage.getItem("paradev.build.strictMetadata")).toBeNull();

    storage.setItem("paradev.build.mode", "partial");
    storage.setItem("paradev.build.launchMode", "baseGame");
    storage.setItem("paradev.build.strictMetadata", "yes");

    expect(readBuildPageSettings(storage)).toEqual(sdkBackedDefaults);
  });

  it("derives SDK-backed build defaults from generated desktop config metadata", () => {
    const parallelismRow = PARADEV_DESKTOP_CONFIG_ROWS.find((row) => row.key === DESKTOP_CONFIG_KEYS.buildParallelism);
    const launchModeRow = PARADEV_DESKTOP_CONFIG_ROWS.find((row) => row.key === DESKTOP_CONFIG_KEYS.hoi4LaunchMode);

    expect(readBuildPageSettings(new MemoryStorage())).toEqual({
      buildMode: "cached",
      launchMode: PARADEV_DESKTOP_CONFIG_DEFAULTS[DESKTOP_CONFIG_KEYS.hoi4LaunchMode],
      parallelism: PARADEV_DESKTOP_CONFIG_DEFAULTS[DESKTOP_CONFIG_KEYS.buildParallelism],
      strictMetadata: PARADEV_DESKTOP_CONFIG_DEFAULTS[DESKTOP_CONFIG_KEYS.buildStrictMetadata]
    });
    expect(BUILD_HOI4_LAUNCH_MODE_VALUES).toEqual(launchModeRow && "choices" in launchModeRow ? launchModeRow.choices : []);
    expect(BUILD_PARALLELISM_MIN).toBe(parallelismRow && "minimum" in parallelismRow ? parallelismRow.minimum : 1);
  });

  it("normalizes HOI4 launch mode values from desktop config", () => {
    expect(hoi4LaunchModeFromConfig("local", "steam")).toBe("local");
    expect(hoi4LaunchModeFromConfig("steam", "local")).toBe("steam");
    expect(hoi4LaunchModeFromConfig("baseGame", "local")).toBe("local");
  });

  it("normalizes HOI4 game roots from desktop config", () => {
    expect(hoi4GameRootFromConfig("  /Games/Hearts of Iron IV  ", "")).toBe("/Games/Hearts of Iron IV");
    expect(hoi4GameRootFromConfig("", "/Games/Hearts of Iron IV")).toBe("");
    expect(hoi4GameRootFromConfig(394360, "/Games/Hearts of Iron IV")).toBe("/Games/Hearts of Iron IV");
  });

  it("normalizes strict metadata values from desktop config", () => {
    expect(strictMetadataFromConfig(true, false)).toBe(true);
    expect(strictMetadataFromConfig(false, true)).toBe(false);
    expect(strictMetadataFromConfig("true", false)).toBe(false);
    expect(strictMetadataFromConfig(null, true)).toBe(true);
  });

  it("normalizes build parallelism values from desktop config", () => {
    expect(buildParallelismFromConfig(4, 1)).toBe(4);
    expect(buildParallelismFromConfig(2.6, 1)).toBe(3);
    expect(buildParallelismFromConfig("8", 1)).toBe(1);
    expect(buildParallelismFromConfig(0, 4)).toBe(4);
    expect(buildParallelismFromConfig(Number.NaN, 5)).toBe(5);
  });

  it("keeps the HOI4 run action disabled until desktop launch config is ready", () => {
    expect(
      buildRunGameDisabled({
        actionPending: false,
        buildBlocked: false,
        desktopBackend: true,
        hasAdverseBuildState: false,
        hasRunningBuilds: false,
        launchReady: true,
        launchModeReady: false
      })
    ).toBe(true);
    expect(
      buildRunGameDisabled({
        actionPending: false,
        buildBlocked: false,
        desktopBackend: true,
        hasAdverseBuildState: false,
        hasRunningBuilds: false,
        launchReady: true,
        launchModeReady: true
      })
    ).toBe(false);
    expect(
      buildRunGameDisabled({
        actionPending: false,
        buildBlocked: false,
        desktopBackend: true,
        hasAdverseBuildState: true,
        hasRunningBuilds: false,
        launchReady: true,
        launchModeReady: true
      })
    ).toBe(true);
    expect(
      buildRunGameDisabled({
        actionPending: false,
        buildBlocked: true,
        desktopBackend: true,
        hasAdverseBuildState: false,
        hasRunningBuilds: false,
        launchReady: true,
        launchModeReady: true
      })
    ).toBe(true);
    expect(
      buildRunGameDisabled({
        actionPending: false,
        buildBlocked: false,
        desktopBackend: true,
        hasAdverseBuildState: false,
        hasRunningBuilds: false,
        launchReady: false,
        launchModeReady: true
      })
    ).toBe(true);
  });
});

class MemoryStorage implements Storage {
  private readonly values = new Map<string, string>();

  get length(): number {
    return this.values.size;
  }

  clear() {
    this.values.clear();
  }

  getItem(key: string) {
    return this.values.get(key) ?? null;
  }

  key(index: number) {
    return [...this.values.keys()][index] ?? null;
  }

  removeItem(key: string) {
    this.values.delete(key);
  }

  setItem(key: string, value: string) {
    this.values.set(key, value);
  }
}

class ThrowingStorage implements Storage {
  get length(): number {
    throw new DOMException("storage unavailable", "SecurityError");
  }

  clear() {
    throw new DOMException("storage unavailable", "SecurityError");
  }

  getItem(_key: string): string | null {
    throw new DOMException("storage unavailable", "SecurityError");
  }

  key(_index: number): string | null {
    throw new DOMException("storage unavailable", "SecurityError");
  }

  removeItem(_key: string) {
    throw new DOMException("storage unavailable", "SecurityError");
  }

  setItem(_key: string, _value: string) {
    throw new DOMException("storage unavailable", "SecurityError");
  }
}
