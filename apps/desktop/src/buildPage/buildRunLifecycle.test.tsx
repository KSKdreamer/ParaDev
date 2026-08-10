/** @vitest-environment jsdom */

import { act, useState } from "react";
import { createRoot, type Root } from "react-dom/client";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import type { ProjectBuildRunPayload } from "../services/paradev";
import type { ProjectOption } from "../types";

const mocks = vi.hoisted(() => ({
  getProjectBuildRuns: vi.fn(),
  getProjectBuildStatus: vi.fn(),
  interruptProjectBuild: vi.fn(),
  startProjectBuild: vi.fn()
}));

vi.mock("../services/paradev", () => ({
  getProjectBuildRuns: mocks.getProjectBuildRuns,
  getProjectBuildStatus: mocks.getProjectBuildStatus,
  hasDesktopBackend: () => true,
  interruptProjectBuild: mocks.interruptProjectBuild,
  startProjectBuild: mocks.startProjectBuild
}));

import {
  buildRunsForProject,
  useBuildRunLifecycle,
  type BuildRunLifecycleController
} from "./buildRunLifecycle";

const projectAlpha: ProjectOption = {
  game: "hoi4",
  id: "alpha",
  name: "Alpha",
  path: "/workspace/alpha",
  projectId: "alpha"
};
const projectBeta: ProjectOption = {
  game: "hoi4",
  id: "beta",
  name: "Beta",
  path: "/workspace/beta",
  projectId: "beta"
};
const projectLate: ProjectOption = {
  game: "hoi4",
  id: "late",
  name: "Late",
  path: "/workspace/late",
  projectId: "late"
};
const sharedTarget = {
  family: "focus_tree",
  id: "focus_tree/SHARED",
  kind: "module" as const
};
const siblingTarget = {
  family: "focus_tree",
  id: "focus_tree/SIBLING",
  kind: "module" as const
};
const BUILD_RUN_CHECKPOINT_STORAGE_KEY = "paradev.build.run-checkpoints.v1";

type MountedController = {
  container: HTMLDivElement;
  root: Root;
};

type Deferred<Value> = {
  promise: Promise<Value>;
  reject: (reason: unknown) => void;
  resolve: (value: Value) => void;
};

const mountedControllers: MountedController[] = [];
const refreshProject = vi.fn(async (_projectRoot?: string, _fallbackProjectId?: string) => undefined);
let latestController: BuildRunLifecycleController | null = null;

beforeEach(() => {
  vi.useFakeTimers();
  window.localStorage.clear();
  mocks.getProjectBuildRuns.mockReset();
  mocks.getProjectBuildRuns.mockResolvedValue({ schema: "paradev.desktop.build-runs.v1", runs: [] });
  mocks.getProjectBuildStatus.mockReset();
  mocks.interruptProjectBuild.mockReset();
  mocks.startProjectBuild.mockReset();
  refreshProject.mockClear();
  latestController = null;
  (globalThis as typeof globalThis & { IS_REACT_ACT_ENVIRONMENT: boolean }).IS_REACT_ACT_ENVIRONMENT = true;
});

afterEach(() => {
  for (const mounted of mountedControllers.splice(0)) {
    act(() => mounted.root.unmount());
    mounted.container.remove();
  }
  vi.restoreAllMocks();
  vi.useRealTimers();
});

describe("useBuildRunLifecycle", () => {
  it("blocks starts after failed recovery and becomes ready after an explicit retry", async () => {
    mocks.getProjectBuildRuns
      .mockRejectedValueOnce(new Error("registry unavailable"))
      .mockResolvedValueOnce({ schema: "paradev.desktop.build-runs.v1", runs: [] });

    mountController();
    await flushAsyncWork();

    expect(controller().recoveryState).toBe("failed");
    await expect(controller().start({ projectRoot: projectAlpha.path }, projectAlpha)).rejects.toThrow(
      "Build run recovery must finish before a new build can start."
    );
    expect(mocks.startProjectBuild).not.toHaveBeenCalled();

    act(() => controller().retryRecovery());
    await flushAsyncWork();

    expect(controller().recoveryState).toBe("ready");
    expect(mocks.getProjectBuildRuns).toHaveBeenCalledTimes(2);
  });

  it("turns a running checkpoint missing from a new native registry into one durable interrupted row", async () => {
    const runningFull: ProjectBuildRunPayload = {
      ...runningPayload("alpha-full-run", projectAlpha.path, 1_000),
      mode: "full",
      target: null,
      terminalSequence: 41
    };
    vi.spyOn(Date, "now").mockReturnValue(5_000);
    mocks.startProjectBuild.mockResolvedValueOnce(runningFull);

    const firstMount = mountController();
    await flushAsyncWork();
    await act(async () => {
      await controller().start({ mode: "full", projectRoot: projectAlpha.path }, projectAlpha);
    });

    expect(storedBuildRunCheckpoints()).toMatchObject([
      { projectRoot: projectAlpha.path, runId: "alpha-full-run", state: "running", target: null }
    ]);
    expect(window.localStorage.getItem(BUILD_RUN_CHECKPOINT_STORAGE_KEY)).not.toContain("terminalSequence");
    unmountController(firstMount);

    const recoveredMount = mountController();
    await flushAsyncWork();

    expect(controller().runs).toMatchObject([
      {
        errorSummary: expect.stringContaining("closed or relaunched"),
        finishedAtMs: 5_000,
        runId: "alpha-full-run",
        state: "interrupted",
        target: null
      }
    ]);
    expect(controller().history).toMatchObject([
      {
        errorSummary: expect.stringContaining("closed or relaunched"),
        id: "alpha-full-run",
        status: "interrupted"
      }
    ]);
    expect(controller().history).toHaveLength(1);
    expect(storedBuildRunCheckpoints()).toMatchObject([{ runId: "alpha-full-run", state: "interrupted" }]);
    unmountController(recoveredMount);

    mountController();
    await flushAsyncWork();

    expect(controller().runs).toMatchObject([{ runId: "alpha-full-run", state: "interrupted" }]);
    expect(controller().history).toHaveLength(1);
  });

  it("lets an authoritative native running payload replace its persisted checkpoint", async () => {
    const checkpoint = runningPayload("alpha-run", projectAlpha.path, 1_000);
    mocks.startProjectBuild.mockResolvedValueOnce(checkpoint);

    const firstMount = mountController();
    await flushAsyncWork();
    await act(async () => {
      await controller().start({ projectRoot: projectAlpha.path, target: sharedTarget }, projectAlpha);
    });
    unmountController(firstMount);

    const authoritative = {
      ...checkpoint,
      progress: { label: "Compiling", percent: 64, phase: "compile" }
    };
    mocks.getProjectBuildRuns.mockResolvedValue({
      schema: "paradev.desktop.build-runs.v1",
      runs: [authoritative]
    });
    mountController();
    await flushAsyncWork();

    expect(controller().runs).toMatchObject([
      { progress: { percent: 64 }, runId: "alpha-run", state: "running" }
    ]);
    expect(controller().history).toEqual([]);
    expect(storedBuildRunCheckpoints()).toMatchObject([
      { progress: { percent: 64 }, runId: "alpha-run", state: "running" }
    ]);
  });

  it("lets an authoritative native terminal payload finish its persisted checkpoint", async () => {
    const checkpoint = runningPayload("alpha-run", projectAlpha.path, 1_000);
    mocks.startProjectBuild.mockResolvedValueOnce(checkpoint);

    const firstMount = mountController();
    await flushAsyncWork();
    await act(async () => {
      await controller().start({ projectRoot: projectAlpha.path, target: sharedTarget }, projectAlpha);
    });
    unmountController(firstMount);

    const completed: ProjectBuildRunPayload = {
      ...checkpoint,
      exitCode: 0,
      finishedAtMs: 3_000,
      progress: { label: "Complete", percent: 100, phase: "complete" },
      status: "completed",
      terminalSequence: 7
    };
    mocks.getProjectBuildRuns.mockResolvedValue({
      schema: "paradev.desktop.build-runs.v1",
      runs: [completed]
    });
    mountController();
    await flushAsyncWork();

    expect(controller().runs).toMatchObject([{ runId: "alpha-run", state: "completed" }]);
    expect(controller().history).toMatchObject([{ id: "alpha-run", status: "completed" }]);
    expect(controller().history[0]?.errorSummary).toBeUndefined();
    expect(storedBuildRunCheckpoints()).toMatchObject([{ runId: "alpha-run", state: "completed" }]);
    expect(window.localStorage.getItem(BUILD_RUN_CHECKPOINT_STORAGE_KEY)).not.toContain("terminalSequence");
  });

  it("treats unreadable presentation checkpoints as empty best-effort state", async () => {
    window.localStorage.setItem(BUILD_RUN_CHECKPOINT_STORAGE_KEY, "[]");
    vi.spyOn(Storage.prototype, "getItem").mockImplementation(() => {
      throw new DOMException("storage denied", "SecurityError");
    });

    mountController();
    await flushAsyncWork();

    expect(controller().recoveryState).toBe("ready");
    expect(controller().runs).toEqual([]);
  });

  it("keeps native run state usable when checkpoint writes are unavailable", async () => {
    const running = runningPayload("alpha-run", projectAlpha.path, 1_000);
    mocks.startProjectBuild.mockResolvedValueOnce(running);
    mountController();
    await flushAsyncWork();
    vi.spyOn(Storage.prototype, "setItem").mockImplementation(() => {
      throw new DOMException("storage denied", "SecurityError");
    });

    await act(async () => {
      await controller().start({ projectRoot: projectAlpha.path, target: sharedTarget }, projectAlpha);
    });

    expect(controller().runs).toMatchObject([{ runId: "alpha-run", state: "running" }]);
  });

  it("recovers multiple same-target runs without leaking them between projects", async () => {
    mocks.getProjectBuildRuns.mockResolvedValue({
      schema: "paradev.desktop.build-runs.v1",
      runs: [
        runningPayload("alpha-run", projectAlpha.path, 2_000),
        runningPayload("beta-run", projectBeta.path, 1_000)
      ]
    });

    mountController();
    await flushAsyncWork();

    expect(controller().recoveryState).toBe("ready");
    expect(controller().runs.map((run) => run.runId)).toEqual(["beta-run", "alpha-run"]);
    expect(buildRunsForProject(controller().runs, projectAlpha.path)).toMatchObject([
      { projectId: "alpha", projectRoot: projectAlpha.path, runId: "alpha-run", target: sharedTarget }
    ]);
    expect(buildRunsForProject(controller().runs, projectBeta.path)).toMatchObject([
      { projectId: "beta", projectRoot: projectBeta.path, runId: "beta-run", target: sharedTarget }
    ]);
  });

  it("prefers the active concrete run over retained terminals regardless of clock or list order", async () => {
    const alphaRunning = runningPayload("alpha-running", projectAlpha.path, 1_000);
    const betaRunning = runningPayload("beta-running", projectBeta.path, 1_000);
    const alphaTerminal: ProjectBuildRunPayload = {
      ...runningPayload("alpha-terminal", projectAlpha.path, 9_000),
      finishedAtMs: 10_000,
      status: "completed"
    };
    const betaTerminal: ProjectBuildRunPayload = {
      ...runningPayload("beta-terminal", projectBeta.path, 9_000),
      finishedAtMs: 10_000,
      status: "failed"
    };
    mocks.getProjectBuildRuns.mockResolvedValue({
      schema: "paradev.desktop.build-runs.v1",
      runs: [alphaRunning, alphaTerminal, betaTerminal, betaRunning]
    });

    mountController();
    await flushAsyncWork();

    expect(buildRunsForProject(controller().runs, projectAlpha.path)).toMatchObject([
      { runId: "alpha-running", state: "running" }
    ]);
    expect(buildRunsForProject(controller().runs, projectBeta.path)).toMatchObject([
      { runId: "beta-running", state: "running" }
    ]);
    expect(storedBuildRunCheckpoints().map((run) => run.runId).sort()).toEqual([
      "alpha-running",
      "beta-running"
    ]);
  });

  it("reconciles concrete active recovery over clock-newer optimistic state without admitting old terminals", async () => {
    const pendingActiveStart = deferred<ProjectBuildRunPayload>();
    const pendingTerminalStart = deferred<ProjectBuildRunPayload>();
    const recoveredActive = runningPayload("recovered-active", projectAlpha.path, 1_000);
    const retainedTerminal: ProjectBuildRunPayload = {
      ...runningPayload("retained-terminal", projectAlpha.path, 50_000),
      finishedAtMs: 60_000,
      status: "completed",
      target: siblingTarget
    };
    mocks.getProjectBuildRuns
      .mockResolvedValueOnce({ schema: "paradev.desktop.build-runs.v1", runs: [] })
      .mockResolvedValueOnce({
        schema: "paradev.desktop.build-runs.v1",
        runs: [recoveredActive, retainedTerminal]
      });
    mocks.startProjectBuild
      .mockReturnValueOnce(pendingActiveStart.promise)
      .mockReturnValueOnce(pendingTerminalStart.promise);
    vi.spyOn(Date, "now").mockReturnValue(10_000);

    mountController();
    await flushAsyncWork();
    let activeStartPromise!: Promise<ProjectBuildRunPayload>;
    act(() => {
      activeStartPromise = controller().start({ projectRoot: projectAlpha.path, target: sharedTarget }, projectAlpha);
      void controller().start({ projectRoot: projectAlpha.path, target: siblingTarget }, projectAlpha);
    });
    expect(controller().runs).toMatchObject([
      { runId: null, state: "running", target: sharedTarget },
      { runId: null, state: "running", target: siblingTarget }
    ]);
    await act(async () => {
      pendingActiveStart.reject(new Error("start response was lost"));
      await expect(activeStartPromise).rejects.toThrow("start response was lost");
    });
    expect(controller().runs.find((run) => run.target?.id === sharedTarget.id)).toMatchObject({
      runId: null,
      state: "failed"
    });
    expect(controller().errorsByProjectRoot[projectAlpha.path]).toMatchObject({
      kind: "start",
      message: "start response was lost"
    });

    act(() => controller().retryRecovery());
    await flushAsyncWork();

    expect(controller().runs.find((run) => run.target?.id === sharedTarget.id)).toMatchObject({
      runId: "recovered-active",
      startedAtMs: 1_000,
      state: "running"
    });
    expect(controller().runs.find((run) => run.target?.id === siblingTarget.id)).toMatchObject({
      runId: null,
      startedAtMs: 10_000,
      state: "running"
    });
    expect(controller().errorsByProjectRoot[projectAlpha.path]).toBeUndefined();
  });

  it("clears only the recovered start attempt and reveals a failed sibling attempt", async () => {
    const recoveredSibling = {
      ...runningPayload("recovered-sibling", projectAlpha.path, 1_000),
      target: siblingTarget
    };
    mocks.getProjectBuildRuns
      .mockResolvedValueOnce({ schema: "paradev.desktop.build-runs.v1", runs: [] })
      .mockResolvedValueOnce({ schema: "paradev.desktop.build-runs.v1", runs: [recoveredSibling] });
    mocks.startProjectBuild
      .mockRejectedValueOnce(new Error("shared target start failed"))
      .mockRejectedValueOnce(new Error("sibling target response was lost"));

    mountController();
    await flushAsyncWork();
    await act(async () => {
      await expect(
        controller().start({ projectRoot: projectAlpha.path, target: sharedTarget }, projectAlpha)
      ).rejects.toThrow("shared target start failed");
      await expect(
        controller().start({ projectRoot: projectAlpha.path, target: siblingTarget }, projectAlpha)
      ).rejects.toThrow("sibling target response was lost");
    });

    expect(controller().errorsByProjectRoot[projectAlpha.path]).toMatchObject({
      kind: "start",
      message: "sibling target response was lost"
    });

    act(() => controller().retryRecovery());
    await flushAsyncWork();

    expect(controller().runs.find((run) => run.target?.id === sharedTarget.id)).toMatchObject({
      runId: null,
      state: "failed"
    });
    expect(controller().runs.find((run) => run.target?.id === siblingTarget.id)).toMatchObject({
      runId: "recovered-sibling",
      state: "running"
    });
    expect(controller().errorsByProjectRoot[projectAlpha.path]).toMatchObject({
      kind: "start",
      message: "shared target start failed"
    });
  });

  it("keeps same-target starts for different projects independently addressable", async () => {
    mocks.startProjectBuild
      .mockResolvedValueOnce(runningPayload("alpha-run", projectAlpha.path, 1_000))
      .mockResolvedValueOnce(runningPayload("beta-run", projectBeta.path, 2_000));

    mountController();
    await flushAsyncWork();
    await act(async () => {
      await controller().start({ projectRoot: projectAlpha.path, target: sharedTarget }, projectAlpha);
      await controller().start({ projectRoot: projectBeta.path, target: sharedTarget }, projectBeta);
    });

    expect(mocks.startProjectBuild).toHaveBeenNthCalledWith(1, { projectRoot: projectAlpha.path, target: sharedTarget });
    expect(mocks.startProjectBuild).toHaveBeenNthCalledWith(2, { projectRoot: projectBeta.path, target: sharedTarget });
    expect(buildRunsForProject(controller().runs, projectAlpha.path)).toMatchObject([{ runId: "alpha-run" }]);
    expect(buildRunsForProject(controller().runs, projectBeta.path)).toMatchObject([{ runId: "beta-run" }]);
  });

  it("serializes polling so a slow status request cannot overlap itself", async () => {
    const firstStatus = deferred<ProjectBuildRunPayload>();
    const initial = runningPayload("alpha-run", projectAlpha.path, 1_000);
    mocks.getProjectBuildRuns.mockResolvedValue({ schema: "paradev.desktop.build-runs.v1", runs: [initial] });
    mocks.getProjectBuildStatus.mockReturnValueOnce(firstStatus.promise).mockResolvedValue(initial);

    mountController({ pollIntervalMs: 50 });
    await flushAsyncWork();

    act(() => vi.advanceTimersByTime(0));
    expect(mocks.getProjectBuildStatus).toHaveBeenCalledTimes(1);
    expect(mocks.getProjectBuildStatus).toHaveBeenLastCalledWith("alpha-run");

    act(() => vi.advanceTimersByTime(1_000));
    expect(mocks.getProjectBuildStatus).toHaveBeenCalledTimes(1);

    await act(async () => {
      firstStatus.resolve({
        ...initial,
        progress: { label: "Compiling", percent: 40, phase: "compile" }
      });
      await firstStatus.promise;
    });
    act(() => vi.advanceTimersByTime(49));
    expect(mocks.getProjectBuildStatus).toHaveBeenCalledTimes(1);
    await act(async () => {
      vi.advanceTimersByTime(1);
      await Promise.resolve();
    });
    expect(mocks.getProjectBuildStatus).toHaveBeenCalledTimes(2);
  });

  it("polls responsive sibling runs while another status request remains hung", async () => {
    const hungStatus = deferred<ProjectBuildRunPayload>();
    const alpha = runningPayload("alpha-run", projectAlpha.path, 1_000);
    const beta = runningPayload("beta-run", projectBeta.path, 2_000);
    mocks.getProjectBuildRuns.mockResolvedValue({ schema: "paradev.desktop.build-runs.v1", runs: [alpha, beta] });
    mocks.getProjectBuildStatus.mockImplementation((runId: string) =>
      runId === "alpha-run" ? hungStatus.promise : Promise.resolve(beta)
    );

    mountController({ pollIntervalMs: 50 });
    await flushAsyncWork();
    await act(async () => {
      await vi.advanceTimersByTimeAsync(200);
    });

    const requestedRunIds = mocks.getProjectBuildStatus.mock.calls.map(([runId]) => runId);
    expect(requestedRunIds.filter((runId) => runId === "alpha-run")).toHaveLength(1);
    expect(requestedRunIds.filter((runId) => runId === "beta-run").length).toBeGreaterThan(1);
  });

  it("keeps one run's status error when a same-project sibling succeeds", async () => {
    const failedStatus = deferred<ProjectBuildRunPayload>();
    const siblingStatus = deferred<ProjectBuildRunPayload>();
    const alpha = runningPayload("alpha-run", projectAlpha.path, 1_000);
    const sibling = { ...runningPayload("alpha-sibling-run", projectAlpha.path, 2_000), target: siblingTarget };
    mocks.getProjectBuildRuns.mockResolvedValue({ schema: "paradev.desktop.build-runs.v1", runs: [alpha, sibling] });
    mocks.getProjectBuildStatus.mockImplementation((runId: string) =>
      runId === alpha.runId ? failedStatus.promise : siblingStatus.promise
    );

    mountController({ pollIntervalMs: 50 });
    await flushAsyncWork();
    act(() => vi.advanceTimersByTime(0));

    act(() => failedStatus.reject(new Error("alpha status failed")));
    await flushAsyncWork();
    expect(controller().errorsByProjectRoot[projectAlpha.path]).toMatchObject({
      kind: "status",
      message: "alpha status failed",
      runId: "alpha-run"
    });

    act(() => siblingStatus.resolve(sibling));
    await flushAsyncWork();
    expect(controller().errorsByProjectRoot[projectAlpha.path]).toMatchObject({
      message: "alpha status failed",
      runId: "alpha-run"
    });
  });

  it("reveals a retained sibling failure after the latest failing run recovers", async () => {
    const firstAlphaStatus = deferred<ProjectBuildRunPayload>();
    const firstSiblingStatus = deferred<ProjectBuildRunPayload>();
    const hungAlphaStatus = deferred<ProjectBuildRunPayload>();
    const alpha = runningPayload("alpha-run", projectAlpha.path, 1_000);
    const sibling = { ...runningPayload("alpha-sibling-run", projectAlpha.path, 2_000), target: siblingTarget };
    let alphaCalls = 0;
    let siblingCalls = 0;
    mocks.getProjectBuildRuns.mockResolvedValue({ schema: "paradev.desktop.build-runs.v1", runs: [alpha, sibling] });
    mocks.getProjectBuildStatus.mockImplementation((runId: string) => {
      if (runId === alpha.runId) {
        alphaCalls += 1;
        return alphaCalls === 1 ? firstAlphaStatus.promise : hungAlphaStatus.promise;
      }
      siblingCalls += 1;
      return siblingCalls === 1 ? firstSiblingStatus.promise : Promise.resolve(sibling);
    });

    mountController({ pollIntervalMs: 50 });
    await flushAsyncWork();
    act(() => vi.advanceTimersByTime(0));

    act(() => firstAlphaStatus.reject(new Error("alpha status failed")));
    await flushAsyncWork();
    act(() => firstSiblingStatus.reject(new Error("sibling status failed")));
    await flushAsyncWork();
    expect(controller().errorsByProjectRoot[projectAlpha.path]).toMatchObject({
      message: "sibling status failed",
      runId: "alpha-sibling-run"
    });

    await act(async () => {
      await vi.advanceTimersByTimeAsync(50);
    });
    expect(controller().errorsByProjectRoot[projectAlpha.path]).toMatchObject({
      message: "alpha status failed",
      runId: "alpha-run"
    });
  });

  it("clears an interrupted run's status error and reveals a retained sibling status error", async () => {
    const alphaStatus = deferred<ProjectBuildRunPayload>();
    const siblingStatus = deferred<ProjectBuildRunPayload>();
    const alpha = runningPayload("alpha-run", projectAlpha.path, 1_000);
    const sibling = { ...runningPayload("alpha-sibling-run", projectAlpha.path, 2_000), target: siblingTarget };
    const interruptedSibling: ProjectBuildRunPayload = {
      ...sibling,
      finishedAtMs: 3_000,
      status: "interrupted"
    };
    mocks.getProjectBuildRuns.mockResolvedValue({ schema: "paradev.desktop.build-runs.v1", runs: [alpha, sibling] });
    mocks.getProjectBuildStatus.mockImplementation((runId: string) =>
      runId === alpha.runId ? alphaStatus.promise : siblingStatus.promise
    );
    mocks.interruptProjectBuild.mockResolvedValueOnce(interruptedSibling);

    mountController({ pollIntervalMs: 10_000 });
    await flushAsyncWork();
    act(() => vi.advanceTimersByTime(0));
    act(() => alphaStatus.reject(new Error("alpha status failed")));
    await flushAsyncWork();
    act(() => siblingStatus.reject(new Error("sibling status failed")));
    await flushAsyncWork();
    expect(controller().errorsByProjectRoot[projectAlpha.path]).toMatchObject({
      message: "sibling status failed",
      runId: "alpha-sibling-run"
    });

    await act(async () => {
      await controller().interrupt("alpha-sibling-run");
    });

    expect(controller().runs.find((run) => run.runId === "alpha-sibling-run")?.state).toBe("interrupted");
    expect(controller().errorsByProjectRoot[projectAlpha.path]).toMatchObject({
      kind: "status",
      message: "alpha status failed",
      runId: "alpha-run"
    });
  });

  it("does not restart a hung poll when a sibling becomes terminal", async () => {
    const hungStatus = deferred<ProjectBuildRunPayload>();
    const alpha = runningPayload("alpha-run", projectAlpha.path, 1_000);
    const sibling = { ...runningPayload("alpha-sibling-run", projectAlpha.path, 2_000), target: siblingTarget };
    const completedSibling: ProjectBuildRunPayload = {
      ...sibling,
      exitCode: 0,
      finishedAtMs: 3_000,
      status: "completed"
    };
    mocks.getProjectBuildRuns.mockResolvedValue({ schema: "paradev.desktop.build-runs.v1", runs: [alpha, sibling] });
    mocks.getProjectBuildStatus.mockImplementation((runId: string) =>
      runId === alpha.runId ? hungStatus.promise : Promise.resolve(completedSibling)
    );

    mountController({ pollIntervalMs: 50 });
    await flushAsyncWork();
    await act(async () => {
      await vi.advanceTimersByTimeAsync(200);
    });

    const requestedRunIds = mocks.getProjectBuildStatus.mock.calls.map(([runId]) => runId);
    expect(requestedRunIds.filter((runId) => runId === "alpha-run")).toHaveLength(1);
    expect(controller().runs.find((run) => run.runId === "alpha-sibling-run")?.state).toBe("completed");
  });

  it("ignores an old run's late status failure after a newer same-slot run replaces it", async () => {
    const oldStatus = deferred<ProjectBuildRunPayload>();
    const oldRun = runningPayload("alpha-old-run", projectAlpha.path, 1_000);
    const newRun = runningPayload("alpha-new-run", projectAlpha.path, 2_000);
    mocks.getProjectBuildRuns.mockResolvedValue({ schema: "paradev.desktop.build-runs.v1", runs: [oldRun] });
    mocks.getProjectBuildStatus.mockReturnValueOnce(oldStatus.promise);
    mocks.startProjectBuild.mockResolvedValueOnce(newRun);

    mountController();
    await flushAsyncWork();
    act(() => vi.advanceTimersByTime(0));
    await act(async () => {
      await controller().start({ projectRoot: projectAlpha.path, target: sharedTarget }, projectAlpha);
    });

    act(() => oldStatus.reject(new Error("stale old-run failure")));
    await flushAsyncWork();

    expect(controller().runs).toMatchObject([{ runId: "alpha-new-run", state: "running" }]);
    expect(controller().errorsByProjectRoot[projectAlpha.path]).toBeUndefined();
  });

  it("resets stale in-flight ownership so recovery can poll a hung run again", async () => {
    const hungStatus = deferred<ProjectBuildRunPayload>();
    const initial = runningPayload("alpha-run", projectAlpha.path, 1_000);
    mocks.getProjectBuildRuns.mockResolvedValue({ schema: "paradev.desktop.build-runs.v1", runs: [initial] });
    mocks.getProjectBuildStatus.mockReturnValueOnce(hungStatus.promise).mockResolvedValue(initial);

    mountController({ pollIntervalMs: 50 });
    await flushAsyncWork();
    act(() => vi.advanceTimersByTime(0));
    expect(mocks.getProjectBuildStatus).toHaveBeenCalledTimes(1);

    act(() => controller().retryRecovery());
    await flushAsyncWork();
    await act(async () => {
      vi.advanceTimersByTime(0);
      await Promise.resolve();
    });

    expect(controller().recoveryState).toBe("ready");
    expect(mocks.getProjectBuildStatus).toHaveBeenCalledTimes(2);
    expect(mocks.getProjectBuildStatus).toHaveBeenLastCalledWith("alpha-run");
  });

  it("terminates an exact polled run when the registry no longer retains it", async () => {
    const initial = runningPayload("alpha-run", projectAlpha.path, 1_000);
    mocks.getProjectBuildRuns.mockResolvedValue({ schema: "paradev.desktop.build-runs.v1", runs: [initial] });
    mocks.getProjectBuildStatus.mockResolvedValue({ schema: "paradev.desktop.build-run.v1", status: "idle" });

    mountController({ pollIntervalMs: 50 });
    await flushAsyncWork();
    await act(async () => {
      await vi.advanceTimersByTimeAsync(200);
    });

    expect(controller().runs).toMatchObject([
      {
        errorSummary: expect.stringContaining("no longer retains this run"),
        runId: "alpha-run",
        state: "failed"
      }
    ]);
    expect(controller().errorsByProjectRoot[projectAlpha.path]).toMatchObject({
      kind: "status",
      message: expect.stringContaining("no longer retains this run"),
      runId: "alpha-run"
    });
    expect(mocks.getProjectBuildStatus).toHaveBeenCalledTimes(1);
  });

  it("terminates an exact interrupted run when the registry returns idle", async () => {
    const initial = runningPayload("alpha-run", projectAlpha.path, 1_000);
    mocks.getProjectBuildRuns.mockResolvedValue({ schema: "paradev.desktop.build-runs.v1", runs: [initial] });
    mocks.interruptProjectBuild.mockResolvedValue({ schema: "paradev.desktop.build-run.v1", status: "idle" });

    mountController();
    await flushAsyncWork();
    await act(async () => {
      await controller().interrupt("alpha-run");
    });

    expect(controller().runs).toMatchObject([{ runId: "alpha-run", state: "failed" }]);
    expect(controller().errorsByProjectRoot[projectAlpha.path]).toMatchObject({
      kind: "status",
      runId: "alpha-run"
    });
  });

  it("does not let a late idle interrupt response terminate a newer slot occupant", async () => {
    const pendingInterrupt = deferred<ProjectBuildRunPayload>();
    const initial = runningPayload("alpha-old-run", projectAlpha.path, 1_000);
    const newer = runningPayload("alpha-new-run", projectAlpha.path, 2_000);
    mocks.getProjectBuildRuns.mockResolvedValue({ schema: "paradev.desktop.build-runs.v1", runs: [initial] });
    mocks.interruptProjectBuild.mockReturnValueOnce(pendingInterrupt.promise);
    mocks.startProjectBuild.mockResolvedValueOnce(newer);

    mountController();
    await flushAsyncWork();
    let interruptPromise!: Promise<ProjectBuildRunPayload>;
    act(() => {
      interruptPromise = controller().interrupt("alpha-old-run");
    });
    await act(async () => {
      await controller().start({ projectRoot: projectAlpha.path, target: sharedTarget }, projectAlpha);
      pendingInterrupt.resolve({ schema: "paradev.desktop.build-run.v1", status: "idle" });
      await interruptPromise;
    });

    expect(controller().runs).toMatchObject([{ runId: "alpha-new-run", state: "running" }]);
    expect(controller().errorsByProjectRoot[projectAlpha.path]).toBeUndefined();
  });

  it("keeps a newer same-millisecond start when the older attempt rejects late", async () => {
    const olderStart = deferred<ProjectBuildRunPayload>();
    const newer = runningPayload("alpha-new-run", projectAlpha.path, 3_000);
    mocks.startProjectBuild.mockReturnValueOnce(olderStart.promise).mockResolvedValueOnce(newer);

    mountController();
    await flushAsyncWork();

    let olderPromise!: Promise<ProjectBuildRunPayload>;
    act(() => {
      olderPromise = controller().start({ projectRoot: projectAlpha.path, target: sharedTarget }, projectAlpha);
    });
    await act(async () => {
      await controller().start({ projectRoot: projectAlpha.path, target: sharedTarget }, projectAlpha);
    });
    expect(controller().runs).toMatchObject([{ runId: "alpha-new-run", state: "running" }]);

    await act(async () => {
      olderStart.reject(new Error("older request failed"));
      await expect(olderPromise).rejects.toThrow("older request failed");
    });

    expect(controller().runs).toMatchObject([{ runId: "alpha-new-run", state: "running" }]);
    expect(controller().errorsByProjectRoot[projectAlpha.path]).toBeUndefined();
  });

  it("tracks an accepted concrete run after a newer same-target attempt fails first", async () => {
    const olderStart = deferred<ProjectBuildRunPayload>();
    const newerStart = deferred<ProjectBuildRunPayload>();
    const accepted = runningPayload("alpha-accepted-run", projectAlpha.path, 1_000);
    mocks.startProjectBuild.mockReturnValueOnce(olderStart.promise).mockReturnValueOnce(newerStart.promise);

    mountController();
    await flushAsyncWork();

    let olderPromise!: Promise<ProjectBuildRunPayload>;
    let newerPromise!: Promise<ProjectBuildRunPayload>;
    act(() => {
      olderPromise = controller().start({ projectRoot: projectAlpha.path, target: sharedTarget }, projectAlpha);
      newerPromise = controller().start({ projectRoot: projectAlpha.path, target: sharedTarget }, projectAlpha);
    });

    await act(async () => {
      newerStart.reject(new Error("newer start rejected"));
      await expect(newerPromise).rejects.toThrow("newer start rejected");
    });
    expect(controller().runs).toMatchObject([{ runId: null, state: "failed" }]);

    await act(async () => {
      olderStart.resolve(accepted);
      await olderPromise;
    });

    expect(controller().runs).toMatchObject([{ runId: "alpha-accepted-run", state: "running" }]);
  });

  it("tracks the first accepted concrete run while a newer same-target attempt is still pending", async () => {
    const olderStart = deferred<ProjectBuildRunPayload>();
    const newerStart = deferred<ProjectBuildRunPayload>();
    const accepted = runningPayload("alpha-accepted-run", projectAlpha.path, 1_000);
    mocks.startProjectBuild.mockReturnValueOnce(olderStart.promise).mockReturnValueOnce(newerStart.promise);

    mountController();
    await flushAsyncWork();
    let olderPromise!: Promise<ProjectBuildRunPayload>;
    let newerPromise!: Promise<ProjectBuildRunPayload>;
    act(() => {
      olderPromise = controller().start({ projectRoot: projectAlpha.path, target: sharedTarget }, projectAlpha);
      newerPromise = controller().start({ projectRoot: projectAlpha.path, target: sharedTarget }, projectAlpha);
    });

    await act(async () => {
      olderStart.resolve(accepted);
      await olderPromise;
    });
    expect(controller().runs).toMatchObject([{ runId: "alpha-accepted-run", state: "running" }]);

    await act(async () => {
      newerStart.reject(new Error("newer start rejected"));
      await expect(newerPromise).rejects.toThrow("newer start rejected");
    });

    expect(controller().runs).toMatchObject([{ runId: "alpha-accepted-run", state: "running" }]);
    expect(controller().errorsByProjectRoot[projectAlpha.path]).toBeUndefined();
  });

  it("preserves known run time and rejects null-time recovery displacement", async () => {
    const newer = runningPayload("alpha-new-run", projectAlpha.path, 3_000);
    const older = runningPayload("alpha-old-run", projectAlpha.path, 2_000);
    const sameRunWithoutTime = withoutStartedAt(newer);
    const differentRunWithoutTime = withoutStartedAt(runningPayload("alpha-unknown-time-run", projectAlpha.path, 4_000));
    mocks.getProjectBuildRuns
      .mockResolvedValueOnce({ schema: "paradev.desktop.build-runs.v1", runs: [newer] })
      .mockResolvedValueOnce({ schema: "paradev.desktop.build-runs.v1", runs: [sameRunWithoutTime, older] })
      .mockResolvedValueOnce({ schema: "paradev.desktop.build-runs.v1", runs: [differentRunWithoutTime] });

    mountController();
    await flushAsyncWork();
    act(() => controller().retryRecovery());
    await flushAsyncWork();

    expect(controller().runs).toMatchObject([{ runId: "alpha-new-run", startedAtMs: 3_000 }]);

    act(() => controller().retryRecovery());
    await flushAsyncWork();

    expect(controller().runs).toMatchObject([{ runId: "alpha-new-run", startedAtMs: 3_000 }]);
  });

  it("does not clear a newer interrupt error when an older status request succeeds", async () => {
    const pendingStatus = deferred<ProjectBuildRunPayload>();
    const initial = runningPayload("alpha-run", projectAlpha.path, 1_000);
    mocks.getProjectBuildRuns.mockResolvedValue({ schema: "paradev.desktop.build-runs.v1", runs: [initial] });
    mocks.getProjectBuildStatus.mockReturnValueOnce(pendingStatus.promise);
    mocks.interruptProjectBuild.mockRejectedValueOnce(new Error("interrupt denied"));

    mountController();
    await flushAsyncWork();
    act(() => vi.advanceTimersByTime(0));

    await act(async () => {
      await expect(controller().interrupt("alpha-run")).rejects.toThrow("interrupt denied");
    });
    expect(controller().errorsByProjectRoot[projectAlpha.path]).toMatchObject({ kind: "interrupt" });

    await act(async () => {
      pendingStatus.resolve(initial);
      await pendingStatus.promise;
      await Promise.resolve();
    });

    expect(controller().errorsByProjectRoot[projectAlpha.path]).toMatchObject({
      kind: "interrupt",
      message: "interrupt denied"
    });
  });

  it("does not clear a sibling status error when starting another target", async () => {
    const failedStatus = deferred<ProjectBuildRunPayload>();
    const initial = runningPayload("alpha-run", projectAlpha.path, 1_000);
    const sibling = { ...runningPayload("alpha-sibling-run", projectAlpha.path, 2_000), target: siblingTarget };
    mocks.getProjectBuildRuns.mockResolvedValue({ schema: "paradev.desktop.build-runs.v1", runs: [initial] });
    mocks.getProjectBuildStatus.mockReturnValueOnce(failedStatus.promise);
    mocks.startProjectBuild.mockResolvedValueOnce(sibling);

    mountController();
    await flushAsyncWork();
    act(() => vi.advanceTimersByTime(0));
    act(() => failedStatus.reject(new Error("alpha status failed")));
    await flushAsyncWork();

    await act(async () => {
      await controller().start({ projectRoot: projectAlpha.path, target: siblingTarget }, projectAlpha);
    });

    expect(controller().errorsByProjectRoot[projectAlpha.path]).toMatchObject({
      kind: "status",
      message: "alpha status failed",
      runId: "alpha-run"
    });
  });

  it("does not clear a refresh error when interrupting a sibling run", async () => {
    const running = runningPayload("alpha-run", projectAlpha.path, 1_000);
    const completedSibling: ProjectBuildRunPayload = {
      ...runningPayload("alpha-terminal", projectAlpha.path, 1_000),
      finishedAtMs: 2_000,
      status: "completed",
      target: siblingTarget
    };
    const interrupted: ProjectBuildRunPayload = {
      ...running,
      finishedAtMs: 3_000,
      status: "interrupted"
    };
    refreshProject.mockRejectedValueOnce(new Error("refresh failed"));
    mocks.getProjectBuildRuns.mockResolvedValue({
      schema: "paradev.desktop.build-runs.v1",
      runs: [running, completedSibling]
    });
    mocks.interruptProjectBuild.mockResolvedValueOnce(interrupted);

    mountController();
    await flushAsyncWork();
    expect(controller().errorsByProjectRoot[projectAlpha.path]).toMatchObject({
      kind: "refresh",
      message: "refresh failed"
    });

    await act(async () => {
      await controller().interrupt("alpha-run");
    });

    expect(controller().errorsByProjectRoot[projectAlpha.path]).toMatchObject({
      kind: "refresh",
      message: "refresh failed"
    });
  });

  it("clears only the requested refresh error and reveals a retained status failure", async () => {
    const failedStatus = deferred<ProjectBuildRunPayload>();
    const running = runningPayload("alpha-run", projectAlpha.path, 1_000);
    const completedSibling: ProjectBuildRunPayload = {
      ...runningPayload("alpha-terminal", projectAlpha.path, 1_000),
      finishedAtMs: 2_000,
      status: "completed",
      target: siblingTarget
    };
    refreshProject.mockRejectedValueOnce(new Error("refresh failed"));
    mocks.getProjectBuildRuns.mockResolvedValue({
      schema: "paradev.desktop.build-runs.v1",
      runs: [running, completedSibling]
    });
    mocks.getProjectBuildStatus.mockReturnValueOnce(failedStatus.promise);

    mountController();
    await flushAsyncWork();
    act(() => vi.advanceTimersByTime(0));
    act(() => failedStatus.reject(new Error("status failed")));
    await flushAsyncWork();
    expect(controller().errorsByProjectRoot[projectAlpha.path]?.kind).toBe("refresh");

    act(() => controller().clearError(projectAlpha.path, "refresh"));

    expect(controller().errorsByProjectRoot[projectAlpha.path]).toMatchObject({
      kind: "status",
      message: "status failed",
      runId: "alpha-run"
    });
  });

  it("keeps a newer same-target run when an older interrupt response arrives late", async () => {
    const pendingInterrupt = deferred<ProjectBuildRunPayload>();
    const initial = runningPayload("alpha-old-run", projectAlpha.path, 1_000);
    const interrupted: ProjectBuildRunPayload = {
      ...initial,
      finishedAtMs: 2_000,
      status: "interrupted"
    };
    const newer = runningPayload("alpha-new-run", projectAlpha.path, 3_000);
    mocks.getProjectBuildRuns.mockResolvedValue({ schema: "paradev.desktop.build-runs.v1", runs: [initial] });
    mocks.getProjectBuildStatus.mockResolvedValue(interrupted);
    mocks.interruptProjectBuild.mockReturnValueOnce(pendingInterrupt.promise);
    mocks.startProjectBuild.mockResolvedValueOnce(newer);

    mountController();
    await flushAsyncWork();

    let interruptPromise!: Promise<ProjectBuildRunPayload>;
    act(() => {
      interruptPromise = controller().interrupt("alpha-old-run");
    });
    await act(async () => {
      vi.advanceTimersByTime(0);
      await Promise.resolve();
      await Promise.resolve();
    });
    expect(controller().runs).toMatchObject([{ runId: "alpha-old-run", state: "interrupted" }]);

    await act(async () => {
      await controller().start({ projectRoot: projectAlpha.path, target: sharedTarget }, projectAlpha);
    });
    expect(controller().runs).toMatchObject([{ runId: "alpha-new-run", state: "running" }]);

    await act(async () => {
      pendingInterrupt.resolve(interrupted);
      await interruptPromise;
    });

    expect(controller().runs).toMatchObject([{ runId: "alpha-new-run", state: "running" }]);
  });

  it("keeps a newer same-target run when an older status response arrives late", async () => {
    const pendingStatus = deferred<ProjectBuildRunPayload>();
    const initial = runningPayload("alpha-old-run", projectAlpha.path, 1_000);
    const interrupted: ProjectBuildRunPayload = {
      ...initial,
      finishedAtMs: 2_000,
      status: "interrupted"
    };
    const newer = runningPayload("alpha-new-run", projectAlpha.path, 3_000);
    mocks.getProjectBuildRuns.mockResolvedValue({ schema: "paradev.desktop.build-runs.v1", runs: [initial] });
    mocks.getProjectBuildStatus.mockReturnValueOnce(pendingStatus.promise);
    mocks.interruptProjectBuild.mockResolvedValueOnce(interrupted);
    mocks.startProjectBuild.mockResolvedValueOnce(newer);

    mountController();
    await flushAsyncWork();
    act(() => vi.advanceTimersByTime(0));
    expect(mocks.getProjectBuildStatus).toHaveBeenCalledWith("alpha-old-run");

    await act(async () => {
      await controller().interrupt("alpha-old-run");
      await controller().start({ projectRoot: projectAlpha.path, target: sharedTarget }, projectAlpha);
      pendingStatus.resolve(initial);
      await pendingStatus.promise;
      await Promise.resolve();
    });

    expect(controller().runs).toMatchObject([{ runId: "alpha-new-run", state: "running" }]);
  });

  it("keeps a newer partial when a duplicate full completion response arrives late", async () => {
    const pendingFullStatus = deferred<ProjectBuildRunPayload>();
    const initialFull: ProjectBuildRunPayload = {
      ...runningPayload("alpha-full-run", projectAlpha.path, 1_000),
      mode: "full",
      target: null
    };
    const completedFull: ProjectBuildRunPayload = {
      ...initialFull,
      finishedAtMs: 2_000,
      status: "completed",
      terminalSequence: 0
    };
    const newerPartial = runningPayload("alpha-new-partial", projectAlpha.path, 3_000);
    mocks.getProjectBuildRuns.mockResolvedValue({ schema: "paradev.desktop.build-runs.v1", runs: [initialFull] });
    mocks.getProjectBuildStatus.mockReturnValueOnce(pendingFullStatus.promise);
    mocks.interruptProjectBuild.mockResolvedValueOnce(completedFull);
    mocks.startProjectBuild.mockResolvedValueOnce(newerPartial);

    mountController({ pollIntervalMs: 10_000 });
    await flushAsyncWork();
    act(() => vi.advanceTimersByTime(0));

    await act(async () => {
      await controller().interrupt("alpha-full-run");
      await controller().start({ projectRoot: projectAlpha.path, target: sharedTarget }, projectAlpha);
      pendingFullStatus.resolve(completedFull);
      await pendingFullStatus.promise;
      await Promise.resolve();
    });

    expect(controller().runs).toMatchObject([
      { runId: "alpha-full-run", state: "completed", target: null },
      { runId: "alpha-new-partial", state: "running", target: sharedTarget }
    ]);
  });

  it("does not let stale recovery replace a newer same-target run", async () => {
    const older = runningPayload("alpha-old-run", projectAlpha.path, 1_000);
    const newer = runningPayload("alpha-new-run", projectAlpha.path, 3_000);
    mocks.getProjectBuildRuns
      .mockResolvedValueOnce({ schema: "paradev.desktop.build-runs.v1", runs: [] })
      .mockResolvedValueOnce({ schema: "paradev.desktop.build-runs.v1", runs: [older] });
    mocks.startProjectBuild.mockResolvedValueOnce(newer);

    mountController();
    await flushAsyncWork();
    await act(async () => {
      await controller().start({ projectRoot: projectAlpha.path, target: sharedTarget }, projectAlpha);
    });

    act(() => controller().retryRecovery());
    await flushAsyncWork();

    expect(controller().recoveryState).toBe("ready");
    expect(controller().runs).toMatchObject([{ runId: "alpha-new-run", state: "running" }]);
  });

  it("clears stale project status errors after authoritative recovery succeeds", async () => {
    const initial = runningPayload("alpha-run", projectAlpha.path, 1_000);
    const completed: ProjectBuildRunPayload = {
      ...initial,
      exitCode: 0,
      finishedAtMs: 2_000,
      status: "completed"
    };
    mocks.getProjectBuildRuns
      .mockResolvedValueOnce({ schema: "paradev.desktop.build-runs.v1", runs: [initial] })
      .mockResolvedValueOnce({ schema: "paradev.desktop.build-runs.v1", runs: [completed] });
    mocks.getProjectBuildStatus.mockRejectedValueOnce(new Error("temporary status failure"));

    mountController();
    await flushAsyncWork();
    await act(async () => {
      vi.advanceTimersByTime(0);
      await Promise.resolve();
      await Promise.resolve();
    });
    expect(controller().errorsByProjectRoot[projectAlpha.path]).toMatchObject({
      kind: "status",
      message: "temporary status failure"
    });

    act(() => controller().retryRecovery());
    await flushAsyncWork();

    expect(controller().runs).toMatchObject([{ runId: "alpha-run", state: "completed" }]);
    expect(controller().errorsByProjectRoot[projectAlpha.path]).toBeUndefined();
  });

  it("records and refreshes one terminal run exactly once for its owning project", async () => {
    const initial = runningPayload("alpha-run", projectAlpha.path, 1_000);
    const completed: ProjectBuildRunPayload = {
      ...initial,
      exitCode: 0,
      finishedAtMs: 3_000,
      progress: { label: "Complete", percent: 100, phase: "complete" },
      status: "completed"
    };
    mocks.getProjectBuildRuns.mockResolvedValue({ schema: "paradev.desktop.build-runs.v1", runs: [initial] });
    mocks.getProjectBuildStatus.mockResolvedValue(completed);
    mocks.interruptProjectBuild.mockResolvedValue(completed);

    mountController();
    await flushAsyncWork();
    await act(async () => {
      vi.advanceTimersByTime(0);
      await Promise.resolve();
      await Promise.resolve();
    });

    expect(controller().runs).toMatchObject([{ projectId: "alpha", runId: "alpha-run", state: "completed" }]);
    expect(controller().history).toMatchObject([
      {
        durationMs: 2_000,
        id: "alpha-run",
        projectId: "alpha",
        status: "completed"
      }
    ]);
    expect(refreshProject).toHaveBeenCalledTimes(1);
    expect(refreshProject).toHaveBeenCalledWith(projectAlpha.path, "alpha");

    await act(async () => {
      await controller().interrupt("alpha-run");
    });

    expect(controller().history).toHaveLength(1);
    expect(refreshProject).toHaveBeenCalledTimes(1);
  });

  it("retains a late old partial terminal in history without reviving it past a full-build baseline", async () => {
    const oldPartial = runningPayload("old-partial", projectAlpha.path, 1_000);
    const pendingOldStatus = deferred<ProjectBuildRunPayload>();
    const completedFull: ProjectBuildRunPayload = {
      ...runningPayload("successful-full", projectAlpha.path, 2_000),
      finishedAtMs: 3_000,
      mode: "full",
      status: "completed",
      target: null,
      terminalSequence: 1
    };
    const lateFailure: ProjectBuildRunPayload = {
      ...oldPartial,
      errorSummary: "late old failure",
      finishedAtMs: 4_000,
      status: "failed",
      terminalSequence: 0
    };
    mocks.getProjectBuildRuns.mockResolvedValue({
      schema: "paradev.desktop.build-runs.v1",
      runs: [oldPartial]
    });
    mocks.getProjectBuildStatus.mockReturnValueOnce(pendingOldStatus.promise);
    mocks.startProjectBuild.mockResolvedValueOnce(completedFull);

    mountController({ pollIntervalMs: 10_000 });
    await flushAsyncWork();
    act(() => vi.advanceTimersByTime(0));
    await act(async () => {
      await controller().start({ mode: "full", projectRoot: projectAlpha.path }, projectAlpha);
      pendingOldStatus.resolve(lateFailure);
      await pendingOldStatus.promise;
      await Promise.resolve();
    });

    expect(controller().history.map((entry) => entry.id).sort()).toEqual(["old-partial", "successful-full"]);
    expect(controller().runs).toMatchObject([
      { runId: "successful-full", state: "completed", target: null }
    ]);
  });

  it("persists a full-success baseline across a later failed full and clock-rolled partial", async () => {
    const oldPartial: ProjectBuildRunPayload = {
      ...runningPayload("old-partial", projectAlpha.path, 9_000),
      errorSummary: "old partial failure",
      finishedAtMs: 10_000,
      status: "failed",
      terminalSequence: 0
    };
    const completedFull: ProjectBuildRunPayload = {
      ...runningPayload("successful-full", projectAlpha.path, 11_000),
      finishedAtMs: 12_000,
      mode: "full",
      status: "completed",
      target: null,
      terminalSequence: 1
    };
    const failedFull: ProjectBuildRunPayload = {
      ...runningPayload("failed-full", projectAlpha.path, 5_000),
      errorSummary: "later full failure",
      finishedAtMs: 6_000,
      mode: "full",
      status: "failed",
      target: null,
      terminalSequence: 2
    };
    const laterPartial: ProjectBuildRunPayload = {
      ...runningPayload("later-partial", projectAlpha.path, 4_000),
      errorSummary: "later partial failure",
      finishedAtMs: 4_500,
      status: "failed",
      target: siblingTarget,
      terminalSequence: 3
    };
    mocks.getProjectBuildRuns.mockResolvedValue({
      schema: "paradev.desktop.build-runs.v1",
      runs: [laterPartial, failedFull, oldPartial, completedFull]
    });

    mountController();
    await flushAsyncWork();

    expect(controller().runs.map((run) => run.runId).sort()).toEqual(["failed-full", "later-partial"]);
    expect(controller().runs.find((run) => run.runId === "failed-full")?.state).toBe("failed");
    expect(controller().runs.find((run) => run.runId === "later-partial")?.state).toBe("failed");
    expect(controller().runs.find((run) => run.runId === "old-partial")).toBeUndefined();
    expect(controller().fullBuildBaselines?.[projectAlpha.path]).toEqual({
      finishedAtMs: 12_000,
      terminalSequence: 1
    });
    expect(controller().history.map((entry) => entry.id).sort()).toEqual([
      "failed-full",
      "later-partial",
      "old-partial",
      "successful-full"
    ]);
  });

  it("restores a successful whole-project baseline from durable checkpoints", async () => {
    const completedFull: ProjectBuildRunPayload = {
      ...runningPayload("successful-full", projectAlpha.path, 11_000),
      finishedAtMs: 12_000,
      mode: "full",
      status: "completed",
      target: null,
      terminalSequence: 1
    };
    mocks.getProjectBuildRuns.mockResolvedValueOnce({
      schema: "paradev.desktop.build-runs.v1",
      runs: [completedFull]
    });

    const firstMount = mountController();
    await flushAsyncWork();

    expect(controller().fullBuildBaselines?.[projectAlpha.path]).toBeDefined();
    unmountController(firstMount);

    mountController();
    await flushAsyncWork();

    expect(controller().fullBuildBaselines?.[projectAlpha.path]).toEqual({
      finishedAtMs: 12_000,
      terminalSequence: null
    });
  });

  it("keeps a running partial recovered after a successful full-build baseline", async () => {
    const laterRunning: ProjectBuildRunPayload = {
      ...runningPayload("later-running-partial", projectAlpha.path, 100),
      target: siblingTarget
    };
    const completedFull: ProjectBuildRunPayload = {
      ...runningPayload("successful-full", projectAlpha.path, 9_000),
      finishedAtMs: 10_000,
      mode: "full",
      status: "completed",
      target: null,
      terminalSequence: 1
    };
    mocks.getProjectBuildRuns.mockResolvedValue({
      schema: "paradev.desktop.build-runs.v1",
      runs: [laterRunning, completedFull]
    });

    mountController();
    await flushAsyncWork();

    expect(controller().runs).toMatchObject([
      { runId: "later-running-partial", state: "running", target: siblingTarget },
      { runId: "successful-full", state: "completed", target: null }
    ]);
  });

  it("prunes terminal UI slots by causal sequence when wall-clock time rolls backward", async () => {
    const projectRoot = "/workspace/clock-rollback";
    const terminalRuns = Array.from({ length: 257 }, (_, terminalSequence): ProjectBuildRunPayload => {
      const startedAtMs = 10_000 - terminalSequence * 10;
      return {
        ...runningPayload(`clock-run-${terminalSequence}`, projectRoot, startedAtMs),
        finishedAtMs: startedAtMs + 5,
        status: "failed",
        target: {
          family: "focus_tree",
          id: `focus_tree/CLOCK_${terminalSequence}`,
          kind: "module"
        },
        terminalSequence
      };
    });
    mocks.getProjectBuildRuns.mockResolvedValue({
      schema: "paradev.desktop.build-runs.v1",
      runs: terminalRuns
    });

    mountController();
    await flushAsyncWork();

    expect(controller().runs).toHaveLength(256);
    expect(controller().runs.some((run) => run.runId === "clock-run-0")).toBe(false);
    expect(controller().runs.some((run) => run.runId === "clock-run-256")).toBe(true);
    expect(storedBuildRunCheckpoints()).toHaveLength(256);
    expect(window.localStorage.getItem(BUILD_RUN_CHECKPOINT_STORAGE_KEY)).not.toContain("terminalSequence");
  });

  it("keeps explicitly removed terminal history hidden after controller reload and recovery", async () => {
    const completed: ProjectBuildRunPayload = {
      ...runningPayload("alpha-run", projectAlpha.path, 1_000),
      exitCode: 0,
      finishedAtMs: 3_000,
      status: "completed"
    };
    mocks.getProjectBuildRuns.mockResolvedValue({ schema: "paradev.desktop.build-runs.v1", runs: [completed] });

    const firstMount = mountController();
    await flushAsyncWork();
    expect(controller().history).toMatchObject([{ id: "alpha-run", projectId: "alpha" }]);
    expect(refreshProject).toHaveBeenCalledTimes(1);

    act(() => controller().removeHistory("alpha-run"));
    expect(controller().history).toEqual([]);
    refreshProject.mockClear();
    unmountController(firstMount);

    mountController();
    await flushAsyncWork();
    expect(controller().history).toEqual([]);
    expect(refreshProject).not.toHaveBeenCalled();

    act(() => controller().retryRecovery());
    await flushAsyncWork();
    expect(controller().history).toEqual([]);
    expect(refreshProject).not.toHaveBeenCalled();
  });

  it("commits a completed run even when browser history storage rejects writes", async () => {
    const completed: ProjectBuildRunPayload = {
      ...runningPayload("alpha-run", projectAlpha.path, 1_000),
      exitCode: 0,
      finishedAtMs: 3_000,
      status: "completed"
    };
    vi.spyOn(Storage.prototype, "setItem").mockImplementation(() => {
      throw new DOMException("quota exceeded", "QuotaExceededError");
    });
    mocks.getProjectBuildRuns.mockResolvedValue({ schema: "paradev.desktop.build-runs.v1", runs: [completed] });

    mountController();
    await flushAsyncWork();

    expect(controller().runs).toMatchObject([{ runId: "alpha-run", state: "completed" }]);
    expect(controller().history).toMatchObject([{ id: "alpha-run", projectRoot: projectAlpha.path }]);
    expect(controller().errorsByProjectRoot[projectAlpha.path]).toBeUndefined();
  });

  it("bounds retained terminal runs and history while preserving the newest records", async () => {
    const runs = Array.from({ length: 300 }, (_, index): ProjectBuildRunPayload => ({
      ...runningPayload(`alpha-run-${index}`, projectAlpha.path, index + 1),
      finishedAtMs: index + 2,
      status: "completed",
      target: { ...sharedTarget, id: `focus_tree/TARGET_${index}` }
    }));
    mocks.getProjectBuildRuns.mockResolvedValue({ schema: "paradev.desktop.build-runs.v1", runs });

    mountController();
    await flushAsyncWork();

    expect(controller().runs).toHaveLength(256);
    expect(controller().history).toHaveLength(256);
    expect(controller().runs.some((run) => run.runId === "alpha-run-0")).toBe(false);
    expect(controller().runs.some((run) => run.runId === "alpha-run-299")).toBe(true);
  });

  it("bounds per-run status errors to the retained terminal run set", async () => {
    const runs = Array.from({ length: 300 }, (_, index): ProjectBuildRunPayload => ({
      ...runningPayload(`alpha-run-${index}`, projectAlpha.path, index + 1),
      target: { ...sharedTarget, id: `focus_tree/TARGET_${index}` }
    }));
    mocks.getProjectBuildRuns.mockResolvedValue({ schema: "paradev.desktop.build-runs.v1", runs });
    mocks.getProjectBuildStatus.mockResolvedValue({ schema: "paradev.desktop.build-run.v1", status: "idle" });

    mountController({ pollIntervalMs: 10_000 });
    await flushAsyncWork();
    await act(async () => {
      await vi.advanceTimersByTimeAsync(0);
    });

    expect(controller().runs).toHaveLength(256);
    let revealedErrors = 0;
    while (controller().errorsByProjectRoot[projectAlpha.path]) {
      const runId = controller().errorsByProjectRoot[projectAlpha.path]?.runId;
      expect(runId).toBeTruthy();
      act(() => controller().clearError(projectAlpha.path, "status", runId));
      revealedErrors += 1;
      if (revealedErrors > 300) {
        throw new Error("Status errors were not bounded to retained build runs.");
      }
    }
    expect(revealedErrors).toBe(256);
  });

  it("corrects recovered terminal history after its project metadata becomes available", async () => {
    const completed: ProjectBuildRunPayload = {
      ...runningPayload("late-run", projectLate.path, 1_000),
      exitCode: 0,
      finishedAtMs: 3_000,
      status: "completed"
    };
    mocks.getProjectBuildRuns.mockResolvedValue({ schema: "paradev.desktop.build-runs.v1", runs: [completed] });

    const mounted = mountController({ projects: [projectAlpha] });
    await flushAsyncWork();

    expect(controller().history).toMatchObject([{ id: "late-run", projectId: projectLate.path }]);
    expect(refreshProject).not.toHaveBeenCalled();

    act(() => mounted.root.render(<LifecycleHarness projects={[projectAlpha, projectLate]} />));
    await flushAsyncWork();

    expect(controller().history).toMatchObject([{ id: "late-run", projectId: "late" }]);
    expect(refreshProject).toHaveBeenCalledTimes(1);
    expect(refreshProject).toHaveBeenCalledWith(projectLate.path, "late");
  });

  it("clears the pending poll timer when its application owner unmounts", async () => {
    const clearTimeout = vi.spyOn(window, "clearTimeout");
    mocks.getProjectBuildRuns.mockResolvedValue({
      schema: "paradev.desktop.build-runs.v1",
      runs: [runningPayload("alpha-run", projectAlpha.path, 1_000)]
    });
    const mounted = mountController();
    await flushAsyncWork();

    expect(vi.getTimerCount()).toBeGreaterThan(0);
    unmountController(mounted);
    expect(clearTimeout).toHaveBeenCalled();

    act(() => vi.runAllTimers());
    expect(mocks.getProjectBuildStatus).not.toHaveBeenCalled();
  });

  it("keeps a pending full build interruptible across Build view unmount and remount", async () => {
    const pendingStart = deferred<ProjectBuildRunPayload>();
    const runningFullBuild: ProjectBuildRunPayload = {
      mode: "full",
      progress: { label: "Compiling", percent: 10, phase: "compile" },
      projectRoot: projectAlpha.path,
      runId: "alpha-full-run",
      schema: "paradev.desktop.build-run.v1",
      startedAtMs: 1_000,
      status: "running",
      target: null
    };
    const interruptedFullBuild: ProjectBuildRunPayload = {
      ...runningFullBuild,
      finishedAtMs: 2_000,
      status: "interrupted"
    };
    mocks.startProjectBuild.mockReturnValueOnce(pendingStart.promise);
    mocks.interruptProjectBuild.mockResolvedValueOnce(interruptedFullBuild);

    const mounted = mountConditionalController();
    await flushAsyncWork();

    let startPromise!: Promise<ProjectBuildRunPayload>;
    act(() => {
      startPromise = controller().start(
        { mode: "full", projectRoot: projectAlpha.path, target: null },
        projectAlpha
      );
    });
    expect(buildViewRun(mounted).dataset.runState).toBe("running");
    expect(buildViewRun(mounted).dataset.runId).toBe("");

    act(() => requiredElement<HTMLButtonElement>(mounted, '[data-testid="toggle-build-view"]').click());
    expect(mounted.container.querySelector('[data-testid="build-view-run"]')).toBeNull();

    await act(async () => {
      pendingStart.resolve(runningFullBuild);
      await startPromise;
    });
    expect(controller().runs).toMatchObject([
      {
        projectId: "alpha",
        projectRoot: projectAlpha.path,
        runId: "alpha-full-run",
        state: "running",
        target: null
      }
    ]);

    act(() => requiredElement<HTMLButtonElement>(mounted, '[data-testid="toggle-build-view"]').click());
    expect(buildViewRun(mounted).dataset).toMatchObject({ runId: "alpha-full-run", runState: "running" });
    expect(requiredElement<HTMLButtonElement>(mounted, '[data-testid="interrupt-run"]').disabled).toBe(false);

    await act(async () => {
      requiredElement<HTMLButtonElement>(mounted, '[data-testid="interrupt-run"]').click();
      await Promise.resolve();
      await Promise.resolve();
    });

    expect(mocks.interruptProjectBuild).toHaveBeenCalledOnce();
    expect(mocks.interruptProjectBuild).toHaveBeenCalledWith("alpha-full-run");
    expect(buildViewRun(mounted).dataset.runState).toBe("interrupted");
  });
});

function LifecycleHarness({
  pollIntervalMs = 1_200,
  projects = [projectAlpha, projectBeta]
}: {
  pollIntervalMs?: number;
  projects?: readonly ProjectOption[];
}) {
  latestController = useBuildRunLifecycle({
    onProjectRefresh: refreshProject,
    pollIntervalMs,
    projects
  });
  return <output data-recovery-state={latestController.recoveryState}>{latestController.runs.length}</output>;
}

function ConditionalBuildViewHarness() {
  const [showBuildView, setShowBuildView] = useState(true);
  const lifecycle = useBuildRunLifecycle({
    onProjectRefresh: refreshProject,
    projects: [projectAlpha, projectBeta]
  });
  latestController = lifecycle;

  return (
    <>
      <button data-testid="toggle-build-view" onClick={() => setShowBuildView((visible) => !visible)} type="button">
        Toggle Build view
      </button>
      {showBuildView ? <BuildLifecycleView lifecycle={lifecycle} /> : null}
    </>
  );
}

function BuildLifecycleView({ lifecycle }: { lifecycle: BuildRunLifecycleController }) {
  const fullRun = buildRunsForProject(lifecycle.runs, projectAlpha.path).find((run) => run.target === null);

  const interrupt = async () => {
    if (fullRun?.runId) {
      await lifecycle.interrupt(fullRun.runId);
    }
  };

  return (
    <section data-testid="build-view">
      <output
        data-run-id={fullRun?.runId ?? ""}
        data-run-state={fullRun?.state ?? "missing"}
        data-testid="build-view-run"
      >
        {fullRun?.runId ?? "No full build run"}
      </output>
      <button data-testid="interrupt-run" disabled={!fullRun?.runId} onClick={interrupt} type="button">
        Interrupt
      </button>
    </section>
  );
}

function mountController({
  pollIntervalMs,
  projects
}: {
  pollIntervalMs?: number;
  projects?: readonly ProjectOption[];
} = {}): MountedController {
  const container = document.createElement("div");
  document.body.append(container);
  const root = createRoot(container);
  const mounted = { container, root };
  mountedControllers.push(mounted);
  act(() => root.render(<LifecycleHarness pollIntervalMs={pollIntervalMs} projects={projects} />));
  return mounted;
}

function mountConditionalController(): MountedController {
  const container = document.createElement("div");
  document.body.append(container);
  const root = createRoot(container);
  const mounted = { container, root };
  mountedControllers.push(mounted);
  act(() => root.render(<ConditionalBuildViewHarness />));
  return mounted;
}

function unmountController(mounted: MountedController): void {
  const index = mountedControllers.indexOf(mounted);
  if (index >= 0) {
    mountedControllers.splice(index, 1);
  }
  act(() => mounted.root.unmount());
  mounted.container.remove();
}

function controller(): BuildRunLifecycleController {
  if (!latestController) {
    throw new Error("Build run lifecycle controller is not mounted.");
  }
  return latestController;
}

function buildViewRun(mounted: MountedController): HTMLOutputElement {
  return requiredElement<HTMLOutputElement>(mounted, '[data-testid="build-view-run"]');
}

function requiredElement<ElementType extends Element>(mounted: MountedController, selector: string): ElementType {
  const element = mounted.container.querySelector<ElementType>(selector);
  if (!element) {
    throw new Error(`Expected mounted controller to contain ${selector}.`);
  }
  return element;
}

async function flushAsyncWork(): Promise<void> {
  await act(async () => {
    await Promise.resolve();
    await Promise.resolve();
  });
}

function storedBuildRunCheckpoints(): Array<Record<string, unknown>> {
  const raw = window.localStorage.getItem(BUILD_RUN_CHECKPOINT_STORAGE_KEY);
  if (!raw) {
    throw new Error("Expected persisted build run checkpoints.");
  }
  const parsed: unknown = JSON.parse(raw);
  if (!Array.isArray(parsed) || parsed.some((value) => !value || typeof value !== "object" || Array.isArray(value))) {
    throw new Error("Persisted build run checkpoints have an invalid test shape.");
  }
  return parsed as Array<Record<string, unknown>>;
}

function runningPayload(runId: string, projectRoot: string, startedAtMs: number): ProjectBuildRunPayload {
  return {
    mode: "cached",
    progress: { label: "Compiling", percent: 10, phase: "compile" },
    projectRoot,
    runId,
    schema: "paradev.desktop.build-run.v1",
    startedAtMs,
    status: "running",
    target: sharedTarget
  };
}

function withoutStartedAt(payload: ProjectBuildRunPayload): ProjectBuildRunPayload {
  const { startedAtMs: _startedAtMs, ...withoutTime } = payload;
  return withoutTime;
}

function deferred<Value>(): Deferred<Value> {
  let reject!: (reason: unknown) => void;
  let resolve!: (value: Value) => void;
  const promise = new Promise<Value>((resolvePromise, rejectPromise) => {
    resolve = resolvePromise;
    reject = rejectPromise;
  });
  return { promise, reject, resolve };
}
