/** @vitest-environment jsdom */

import { act } from "react";
import { createRoot, type Root } from "react-dom/client";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { DESKTOP_CONFIG_KEYS } from "../desktopConfig";
import { createTranslator } from "../i18n";
import type { ProjectBrowserPayload, ProjectOption } from "../types";
import { BuildPage } from "./BuildPage";
import {
  clearBuildDiagnosticsCache,
  readCachedBuildDiagnostics,
  type BuildDiagnosticsRefreshSource
} from "./buildDiagnosticsCache";
import type { BuildTargetIntent } from "./buildPageModel";
import type { BuildRunLifecycleController, BuildRunRecord } from "./buildRunLifecycle";

const serviceMocks = vi.hoisted(() => ({
  loadHoi4LaunchReadiness: vi.fn(),
  loadProjectInspection: vi.fn(),
  openProjectPath: vi.fn(),
  readConfigValue: vi.fn(),
  runHoi4Game: vi.fn(),
  writeConfigValue: vi.fn()
}));

vi.mock("../services/paradev", async (importOriginal) => ({
  ...(await importOriginal<typeof import("../services/paradev")>()),
  hasDesktopBackend: () => true,
  loadHoi4LaunchReadiness: serviceMocks.loadHoi4LaunchReadiness,
  loadProjectInspection: serviceMocks.loadProjectInspection,
  openProjectPath: serviceMocks.openProjectPath,
  readConfigValue: serviceMocks.readConfigValue,
  runHoi4Game: serviceMocks.runHoi4Game,
  writeConfigValue: serviceMocks.writeConfigValue
}));

const alpha: ProjectOption = {
  game: "hoi4",
  id: "alpha",
  name: "Alpha",
  path: "/workspace/alpha",
  projectId: "shared-id"
};
const beta: ProjectOption = {
  game: "hoi4",
  id: "beta",
  name: "Beta",
  path: "/workspace/beta",
  projectId: "shared-id"
};

const mountedRoots: Array<{ container: HTMLDivElement; root: Root }> = [];

beforeEach(() => {
  clearBuildDiagnosticsCache();
  window.localStorage.clear();
  serviceMocks.loadHoi4LaunchReadiness.mockReset();
  serviceMocks.loadHoi4LaunchReadiness.mockResolvedValue(launchReadiness("ready", true, "Ready to launch."));
  serviceMocks.loadProjectInspection.mockReset();
  serviceMocks.loadProjectInspection.mockResolvedValue({ diagnostics: [] });
  serviceMocks.openProjectPath.mockReset();
  serviceMocks.openProjectPath.mockResolvedValue(undefined);
  serviceMocks.readConfigValue.mockReset();
  serviceMocks.readConfigValue.mockResolvedValue(null);
  serviceMocks.runHoi4Game.mockReset();
  serviceMocks.runHoi4Game.mockResolvedValue(undefined);
  serviceMocks.writeConfigValue.mockReset();
  serviceMocks.writeConfigValue.mockResolvedValue(undefined);
  (globalThis as typeof globalThis & { IS_REACT_ACT_ENVIRONMENT: boolean }).IS_REACT_ACT_ENVIRONMENT = true;
});

afterEach(() => {
  for (const mounted of mountedRoots.splice(0)) {
    act(() => mounted.root.unmount());
    mounted.container.remove();
  }
  vi.restoreAllMocks();
});

describe("BuildPage project-scoped actions", () => {
  it("waits for project and config readiness before one strict diagnostics request", async () => {
    serviceMocks.readConfigValue.mockImplementation(async (key: string) =>
      key === DESKTOP_CONFIG_KEYS.buildStrictMetadata ? true : null
    );
    const lifecycle = buildLifecycle();
    const mounted = mountBuildPage(alpha, lifecycle, async () => undefined, {
      buildDiagnosticsGeneration: 1,
      projectLoading: true
    });
    await flushAsyncWork();

    expect(serviceMocks.loadProjectInspection).not.toHaveBeenCalled();

    act(() =>
      renderBuildPage(mounted.root, alpha, lifecycle, async () => undefined, {
        buildDiagnosticsGeneration: 1,
        projectLoading: false
      })
    );
    await waitForBuildPageUpdate(() => serviceMocks.loadProjectInspection.mock.calls.length === 1);

    expect(serviceMocks.loadProjectInspection).toHaveBeenCalledWith({
      filters: { strictMetadata: true },
      kind: "diagnostics",
      projectRoot: alpha.path
    });
  });

  it("does not repeat diagnostics inspection for browser-only model updates", async () => {
    const lifecycle = buildLifecycle();
    const options = { buildDiagnosticsGeneration: 1 };
    const mounted = mountBuildPage(alpha, lifecycle, async () => undefined, options);
    await waitForBuildPageUpdate(() => serviceMocks.loadProjectInspection.mock.calls.length === 1);

    act(() =>
      renderBuildPage(mounted.root, alpha, lifecycle, async () => undefined, {
        ...options,
        browser: { ...browserForProject(alpha), title: "Updated browser identity" }
      })
    );
    await flushAsyncWork();

    expect(serviceMocks.loadProjectInspection).toHaveBeenCalledOnce();
  });

  it("revalidates diagnostics once for an explicit project generation", async () => {
    const lifecycle = buildLifecycle();
    const mounted = mountBuildPage(alpha, lifecycle, async () => undefined, {
      buildDiagnosticsGeneration: 1
    });
    await waitForBuildPageUpdate(() => serviceMocks.loadProjectInspection.mock.calls.length === 1);

    act(() =>
      renderBuildPage(mounted.root, alpha, lifecycle, async () => undefined, {
        buildDiagnosticsGeneration: 2
      })
    );
    await waitForBuildPageUpdate(() => serviceMocks.loadProjectInspection.mock.calls.length === 2);

    expect(serviceMocks.loadProjectInspection).toHaveBeenCalledTimes(2);
  });

  it("reads the emitted manifest instead of compiling again after a terminal build", async () => {
    const lifecycle = buildLifecycle();
    const mounted = mountBuildPage(alpha, lifecycle, async () => undefined, {
      buildDiagnosticsGeneration: 1
    });
    await waitForBuildPageUpdate(() => serviceMocks.loadProjectInspection.mock.calls.length === 1);

    act(() =>
      renderBuildPage(mounted.root, alpha, lifecycle, async () => undefined, {
        buildDiagnosticsGeneration: 2,
        buildDiagnosticsRefreshSource: "published"
      })
    );
    await waitForBuildPageUpdate(() => serviceMocks.loadProjectInspection.mock.calls.length === 2);

    expect(serviceMocks.loadProjectInspection.mock.calls[1]?.[0]).toEqual({
      filters: { published: true },
      kind: "diagnostics",
      projectRoot: alpha.path
    });
  });

  it("falls back to current browser diagnostics while a newer generation is pending", async () => {
    const lifecycle = buildLifecycle();
    const mounted = mountBuildPage(alpha, lifecycle, async () => undefined, {
      buildDiagnosticsGeneration: 1
    });
    await waitForBuildPageUpdate(() => serviceMocks.loadProjectInspection.mock.calls.length === 1);
    await flushAsyncWork();

    const pending = deferred<{ diagnostics: Array<Record<string, unknown>> }>();
    serviceMocks.loadProjectInspection.mockReturnValueOnce(pending.promise);
    const blockedBrowser: ProjectBrowserPayload = {
      ...browserForProject(alpha),
      diagnostics: [{ code: "entity.invalid_record", severity: "error" }]
    };
    act(() =>
      renderBuildPage(mounted.root, alpha, lifecycle, async () => undefined, {
        browser: blockedBrowser,
        buildDiagnosticsGeneration: 2
      })
    );
    await waitForBuildPageUpdate(() => serviceMocks.loadProjectInspection.mock.calls.length === 2);

    expect(overviewAction(mounted.container, "build.start").disabled).toBe(true);
  });

  it("rejects malformed diagnostics without caching them as a clean result", async () => {
    serviceMocks.loadProjectInspection.mockResolvedValueOnce({ diagnostics: null });
    const mounted = mountBuildPage(alpha, buildLifecycle(), async () => undefined, {
      buildDiagnosticsGeneration: 1
    });
    await waitForBuildPageUpdate(() =>
      mounted.container.textContent?.includes("Project diagnostics response must contain a diagnostics array.") === true
    );

    expect(readCachedBuildDiagnostics(alpha.path, false)).toBeNull();
    expect(readCachedBuildDiagnostics(alpha.path, true)).toBeNull();
    expect(serviceMocks.loadProjectInspection).toHaveBeenCalledOnce();
  });

  it("clears a diagnostics-owned error after a newer generation succeeds", async () => {
    serviceMocks.loadProjectInspection.mockRejectedValueOnce(new Error("first inspection failed"));
    const lifecycle = buildLifecycle();
    const mounted = mountBuildPage(alpha, lifecycle, async () => undefined, {
      buildDiagnosticsGeneration: 1
    });
    await waitForBuildPageUpdate(() =>
      mounted.container.textContent?.includes("first inspection failed") === true
    );

    act(() =>
      renderBuildPage(mounted.root, alpha, lifecycle, async () => undefined, {
        buildDiagnosticsGeneration: 2
      })
    );
    await waitForBuildPageUpdate(() => serviceMocks.loadProjectInspection.mock.calls.length === 2);
    await waitForBuildPageUpdate(() =>
      mounted.container.textContent?.includes("first inspection failed") === false
    );

    expect(serviceMocks.loadProjectInspection).toHaveBeenCalledTimes(2);
  });

  it("keeps an editor-requested family update safe when whole-project mode is full", async () => {
    window.localStorage.setItem("paradev.build.mode", "full");
    const lifecycle = buildLifecycle();
    const onBuildTargetIntentConsumed = vi.fn();
    const intent: BuildTargetIntent = {
      nonce: 1,
      projectRoot: alpha.path,
      target: { family: "entity", id: "entity", kind: "family" }
    };
    const mounted = mountBuildPage(alpha, lifecycle, async () => undefined, {
      buildTargetIntent: intent,
      onBuildTargetIntentConsumed
    });

    await waitForBuildPageUpdate(() =>
      mounted.container.querySelector("#build-lifecycle-confirmation input[type=checkbox]") !== null
    );

    expect(onBuildTargetIntentConsumed).toHaveBeenCalledOnce();
    expect(onBuildTargetIntentConsumed).toHaveBeenCalledWith(intent.nonce);
    expect(requiredElement<HTMLElement>(mounted.container, "#build-lifecycle-confirmation").dataset.paradevConfirmationTargetKey).toBe(
      "family:entity:entity"
    );
    expect(
      requiredElement<HTMLSelectElement>(
        mounted.container,
        'select[aria-label="Whole-project build mode"]'
      ).value
    ).toBe("full");
    expect(mounted.container.textContent).toContain(
      "Cleans ParaDev-owned generated output and build data, then compiles the whole project."
    );
    expect(mounted.container.textContent).toContain("Confirm safe partial update");
    expect(mounted.container.textContent).toContain(
      "The whole-project mode above does not apply."
    );

    act(() => requiredElement<HTMLInputElement>(mounted.container, "#build-lifecycle-confirmation input[type=checkbox]").click());
    const continueButton = requiredElement<HTMLButtonElement>(
      mounted.container,
      "#build-lifecycle-confirmation .build-lifecycle-confirmation-actions .primary"
    );
    await waitForBuildPageUpdate(() => !continueButton.disabled);
    act(() => continueButton.click());
    await flushAsyncWork();

    expect(lifecycle.start).toHaveBeenCalledOnce();
    expect(lifecycle.start.mock.calls[0]?.[0]).toMatchObject({
      mode: "cached",
      target: { family: "entity", id: "entity", kind: "family" }
    });
  });

  it("starts an exact module intent even when the dashboard renders family rows", async () => {
    const lifecycle = buildLifecycle();
    const onBuildTargetIntentConsumed = vi.fn();
    const intent: BuildTargetIntent = {
      nonce: 7,
      projectRoot: alpha.path,
      target: { family: "entity", id: "entity/ALPHA", kind: "module" }
    };
    const intentProps = {
      browser: browserForProject(alpha),
      buildTargetIntent: intent,
      onBuildTargetIntentConsumed
    };
    const mounted = mountBuildPage(alpha, lifecycle, async () => undefined, intentProps);
    await flushAsyncWork();

    expect(mounted.container.querySelector("#build-lifecycle-confirmation")).toBeNull();
    expect(onBuildTargetIntentConsumed).not.toHaveBeenCalled();

    act(() =>
      renderBuildPage(mounted.root, alpha, lifecycle, async () => undefined, {
        ...intentProps,
        browser: browserWithEntityModule(alpha)
      })
    );

    await waitForBuildPageUpdate(() =>
      mounted.container.querySelector("#build-lifecycle-confirmation input[type=checkbox]") !== null
    );

    expect(mounted.container.querySelectorAll(".build-entity-row")).toHaveLength(1);
    expect(
      requiredElement<HTMLElement>(
        mounted.container,
        "#build-lifecycle-confirmation"
      ).dataset.paradevConfirmationTargetKey
    ).toBe("module:entity:entity/ALPHA");
    expect(onBuildTargetIntentConsumed).toHaveBeenCalledWith(intent.nonce);

    act(() =>
      requiredElement<HTMLInputElement>(
        mounted.container,
        "#build-lifecycle-confirmation input[type=checkbox]"
      ).click()
    );
    const continueButton = requiredElement<HTMLButtonElement>(
      mounted.container,
      "#build-lifecycle-confirmation .build-lifecycle-confirmation-actions .primary"
    );
    await waitForBuildPageUpdate(() => !continueButton.disabled);
    act(() => continueButton.click());
    await flushAsyncWork();

    expect(lifecycle.start).toHaveBeenCalledOnce();
    expect(lifecycle.start.mock.calls[0]?.[0]).toMatchObject({
      mode: "cached",
      target: { family: "entity", id: "entity/ALPHA", kind: "module" }
    });
  });

  it("does not consume an editor build intent owned by another project", async () => {
    const onBuildTargetIntentConsumed = vi.fn();
    const mounted = mountBuildPage(alpha, buildLifecycle(), async () => undefined, {
      buildTargetIntent: {
        nonce: 2,
        projectRoot: beta.path,
        target: { family: "entity", id: "entity", kind: "family" }
      },
      onBuildTargetIntentConsumed
    });
    await flushAsyncWork();

    expect(mounted.container.querySelector("#build-lifecycle-confirmation")).toBeNull();
    expect(onBuildTargetIntentConsumed).not.toHaveBeenCalled();
  });

  it("waits until the requested family appears in the current build model", async () => {
    const onBuildTargetIntentConsumed = vi.fn();
    const lifecycle = buildLifecycle();
    const intentProps = {
      browser: { ...browserForProject(alpha), families: [] },
      buildTargetIntent: {
        nonce: 6,
        projectRoot: alpha.path,
        target: { family: "entity", id: "entity", kind: "family" as const }
      },
      onBuildTargetIntentConsumed
    };
    const mounted = mountBuildPage(alpha, lifecycle, async () => undefined, intentProps);
    await flushAsyncWork();

    expect(mounted.container.querySelector("#build-lifecycle-confirmation")).toBeNull();
    expect(onBuildTargetIntentConsumed).not.toHaveBeenCalled();

    act(() =>
      renderBuildPage(mounted.root, alpha, lifecycle, async () => undefined, {
        ...intentProps,
        browser: browserForProject(alpha)
      })
    );
    await waitForBuildPageUpdate(() => mounted.container.querySelector("#build-lifecycle-confirmation") !== null);

    expect(onBuildTargetIntentConsumed).toHaveBeenCalledOnce();
  });

  it("waits for lifecycle recovery before consuming an editor build intent", async () => {
    const target = { family: "entity", id: "entity", kind: "family" as const };
    const intent: BuildTargetIntent = { nonce: 3, projectRoot: alpha.path, target };
    const onBuildTargetIntentConsumed = vi.fn();
    const lifecycle = buildLifecycle({ recoveryState: "loading" });
    const intentProps = { buildTargetIntent: intent, onBuildTargetIntentConsumed };
    const mounted = mountBuildPage(alpha, lifecycle, async () => undefined, intentProps);
    await flushAsyncWork();

    expect(mounted.container.querySelector("#build-lifecycle-confirmation")).toBeNull();
    expect(onBuildTargetIntentConsumed).not.toHaveBeenCalled();

    act(() => renderBuildPage(mounted.root, alpha, { ...lifecycle, recoveryState: "ready" }, async () => undefined, intentProps));
    await waitForBuildPageUpdate(() => mounted.container.querySelector("#build-lifecycle-confirmation") !== null);

    expect(onBuildTargetIntentConsumed).toHaveBeenCalledOnce();
  });

  it("waits for an identical running family target before consuming the intent", async () => {
    const target = { family: "entity", id: "entity", kind: "family" as const };
    const intent: BuildTargetIntent = { nonce: 4, projectRoot: alpha.path, target };
    const onBuildTargetIntentConsumed = vi.fn();
    const lifecycle = buildLifecycle({ runs: [runningBuild(alpha, target, "entity-running", 1_000)] });
    const intentProps = { buildTargetIntent: intent, onBuildTargetIntentConsumed };
    const mounted = mountBuildPage(alpha, lifecycle, async () => undefined, intentProps);
    await flushAsyncWork();

    expect(mounted.container.querySelector("#build-lifecycle-confirmation")).toBeNull();
    expect(onBuildTargetIntentConsumed).not.toHaveBeenCalled();

    act(() => renderBuildPage(mounted.root, alpha, { ...lifecycle, runs: [] }, async () => undefined, intentProps));
    await waitForBuildPageUpdate(() => mounted.container.querySelector("#build-lifecycle-confirmation") !== null);

    expect(onBuildTargetIntentConsumed).toHaveBeenCalledOnce();
  });

  it("keeps a blocked project from opening or consuming an editor build intent", async () => {
    serviceMocks.loadProjectInspection.mockReturnValueOnce(new Promise(() => undefined));
    const target = { family: "entity", id: "entity", kind: "family" as const };
    const intent: BuildTargetIntent = { nonce: 5, projectRoot: alpha.path, target };
    const onBuildTargetIntentConsumed = vi.fn();
    const cleanBrowser = browserForProject(alpha);
    const blockedBrowser: ProjectBrowserPayload = {
      ...cleanBrowser,
      diagnostics: [{ code: "entity.invalid_record", message: "Repair the Entity record.", severity: "error" }]
    };
    const lifecycle = buildLifecycle();
    const intentProps = { browser: blockedBrowser, buildTargetIntent: intent, onBuildTargetIntentConsumed };
    const mounted = mountBuildPage(alpha, lifecycle, async () => undefined, intentProps);
    await flushAsyncWork();

    expect(mounted.container.querySelector("#build-lifecycle-confirmation")).toBeNull();
    expect(onBuildTargetIntentConsumed).not.toHaveBeenCalled();
    expect(overviewAction(mounted.container, "build.start").disabled).toBe(true);

    act(() => renderBuildPage(mounted.root, alpha, lifecycle, async () => undefined, { ...intentProps, browser: cleanBrowser }));
    await waitForBuildPageUpdate(() => mounted.container.querySelector("#build-lifecycle-confirmation") !== null);

    expect(onBuildTargetIntentConsumed).toHaveBeenCalledOnce();
  });

  it("does not reopen a late Alpha confirmation after switching to Beta", async () => {
    const lifecycle = buildLifecycle();
    const mounted = mountBuildPage(alpha, lifecycle);
    const startButton = overviewAction(mounted.container, "build.start");

    act(() => {
      startButton.click();
      renderBuildPage(mounted.root, beta, lifecycle);
    });
    await flushAsyncWork();

    expect(mounted.container.querySelector("#build-lifecycle-confirmation")).toBeNull();
    expect(lifecycle.start).not.toHaveBeenCalled();
  });

  it("keeps a pending and rejected Alpha start from disabling or alerting Beta", async () => {
    const pendingStart = deferred<Awaited<ReturnType<BuildRunLifecycleController["start"]>>>();
    const lifecycle = buildLifecycle({ start: vi.fn(() => pendingStart.promise) });
    const mounted = mountBuildPage(alpha, lifecycle);
    await confirmAction(mounted.container, "build.start");

    act(() => renderBuildPage(mounted.root, beta, lifecycle));
    const betaStart = overviewAction(mounted.container, "build.start");
    expect(betaStart.disabled).toBe(false);

    act(() => pendingStart.reject(new Error("Alpha start failed")));
    await flushAsyncWork();

    expect(mounted.container.textContent).not.toContain("Alpha start failed");
    expect(betaStart.disabled).toBe(false);
  });

  it("keeps a pending and rejected Alpha interrupt from alerting Beta", async () => {
    const pendingInterrupt = deferred<Awaited<ReturnType<BuildRunLifecycleController["interrupt"]>>>();
    const alphaRun = runningFullBuild(alpha);
    const lifecycle = buildLifecycle({
      interrupt: vi.fn(() => pendingInterrupt.promise),
      runs: [alphaRun]
    });
    const mounted = mountBuildPage(alpha, lifecycle);
    await confirmAction(mounted.container, "build.interrupt");

    act(() => renderBuildPage(mounted.root, beta, lifecycle));
    expect(overviewAction(mounted.container, "build.start").disabled).toBe(false);

    act(() => pendingInterrupt.reject(new Error("Alpha interrupt failed")));
    await flushAsyncWork();

    expect(mounted.container.textContent).not.toContain("Alpha interrupt failed");
  });

  it("interrupts each concurrent targeted run by its exact row action", async () => {
    const lifecycle = buildLifecycle({
      runs: [
        runningBuild(alpha, { family: "entity", id: "entity", kind: "family" }, "alpha-entity-run", 1_000),
        runningBuild(alpha, { family: "focus_tree", id: "focus_tree", kind: "family" }, "alpha-focus-run", 2_000)
      ]
    });
    const mounted = mountBuildPage(alpha, lifecycle, async () => undefined, {
      browser: browserWithFocusTree(alpha)
    });
    const overviewInterrupt = overviewAction(mounted.container, "build.interrupt");
    const entityInterrupt = entityAction(
      mounted.container,
      "build.interrupt",
      "family:entity:entity"
    );
    const focusInterrupt = entityAction(
      mounted.container,
      "build.interrupt",
      "family:focus_tree:focus_tree"
    );

    expect(overviewInterrupt.disabled).toBe(true);
    expect(entityInterrupt.disabled).toBe(false);
    expect(focusInterrupt.disabled).toBe(false);
    act(() => entityInterrupt.click());
    await waitForBuildPageUpdate(() => mounted.container.querySelector("#build-lifecycle-confirmation") !== null);

    const confirmation = requiredElement<HTMLElement>(
      mounted.container,
      "#build-lifecycle-confirmation"
    );
    expect(confirmation.dataset.paradevConfirmationTargetKey).toBe("family:entity:entity");
    expect(confirmation.dataset.paradevConfirmationRunId).toBe("alpha-entity-run");

    act(() =>
      requiredElement<HTMLInputElement>(
        mounted.container,
        "#build-lifecycle-confirmation input[type=checkbox]"
      ).click()
    );
    const continueButton = requiredElement<HTMLButtonElement>(
      mounted.container,
      "#build-lifecycle-confirmation .build-lifecycle-confirmation-actions .primary"
    );
    await waitForBuildPageUpdate(() => !continueButton.disabled);
    act(() => continueButton.click());
    await flushAsyncWork();

    expect(lifecycle.interrupt).toHaveBeenCalledOnce();
    expect(lifecycle.interrupt).toHaveBeenCalledWith("alpha-entity-run");
    await waitForBuildPageUpdate(() => !focusInterrupt.disabled);
    expect(focusInterrupt.dataset.paradevBuildRunId).toBe("alpha-focus-run");
  });

  it("keeps an exact running module update visible and interruptible when family rows hide modules", async () => {
    const moduleTarget = {
      family: "entity",
      id: "entity/ALPHA",
      kind: "module" as const
    };
    const moduleRun = {
      ...runningBuild(alpha, moduleTarget, "alpha-module-run", Date.now() - 65_000),
      progress: {
        detail: "Compiling entity/ALPHA",
        percent: 42,
        phase: "entity_compile"
      }
    };
    const lifecycle = buildLifecycle({ runs: [moduleRun] });
    const mounted = mountBuildPage(alpha, lifecycle, async () => undefined, {
      browser: browserWithEntityModule(alpha)
    });
    const activeRow = requiredElement<HTMLElement>(
      mounted.container,
      '.build-active-partial-row[data-paradev-build-target-key="module:entity:entity/ALPHA"]'
    );
    const interrupt = requiredElement<HTMLButtonElement>(
      activeRow,
      'button[data-paradev-operation-id="build.interrupt"]'
    );

    expect(activeRow.textContent).toContain("Module · entity · entity/ALPHA");
    expect(activeRow.textContent).toContain("Compiling entity/ALPHA");
    expect(activeRow.textContent).toContain("42%");
    expect(mounted.container.textContent).not.toContain("-- : --");
    expect(interrupt.dataset.paradevBuildRunId).toBe("alpha-module-run");
    expect(interrupt.disabled).toBe(false);

    act(() => interrupt.click());
    await waitForBuildPageUpdate(() => mounted.container.querySelector("#build-lifecycle-confirmation") !== null);

    const confirmation = requiredElement<HTMLElement>(
      mounted.container,
      "#build-lifecycle-confirmation"
    );
    expect(confirmation.dataset.paradevConfirmationTargetKey).toBe(
      "module:entity:entity/ALPHA"
    );
    expect(confirmation.dataset.paradevConfirmationRunId).toBe("alpha-module-run");

    act(() =>
      requiredElement<HTMLInputElement>(
        mounted.container,
        "#build-lifecycle-confirmation input[type=checkbox]"
      ).click()
    );
    const continueButton = requiredElement<HTMLButtonElement>(
      mounted.container,
      "#build-lifecycle-confirmation .build-lifecycle-confirmation-actions .primary"
    );
    await waitForBuildPageUpdate(() => !continueButton.disabled);
    act(() => continueButton.click());
    await flushAsyncWork();

    expect(lifecycle.interrupt).toHaveBeenCalledOnce();
    expect(lifecycle.interrupt).toHaveBeenCalledWith("alpha-module-run");
  });

  it("dismisses a whole-project confirmation when an optimistic running slot has no run id yet", async () => {
    const lifecycle = buildLifecycle();
    const mounted = mountBuildPage(alpha, lifecycle);
    const start = overviewAction(mounted.container, "build.start");

    await waitForBuildPageUpdate(() => !start.disabled);
    act(() => start.click());
    await waitForBuildPageUpdate(
      () => mounted.container.querySelector("#build-lifecycle-confirmation") !== null
    );

    const optimisticRun = {
      ...runningBuild(alpha, null, "unused", Date.now()),
      runId: null
    };
    act(() =>
      renderBuildPage(
        mounted.root,
        alpha,
        { ...lifecycle, runs: [optimisticRun] }
      )
    );
    await waitForBuildPageUpdate(
      () => mounted.container.querySelector("#build-lifecycle-confirmation") === null
    );
  });

  it("keeps a target confirmation when an unrelated partial run starts", async () => {
    const lifecycle = buildLifecycle();
    const mounted = mountBuildPage(alpha, lifecycle, async () => undefined, {
      browser: browserWithFocusTree(alpha)
    });
    const focusUpdate = entityAction(
      mounted.container,
      "build.start",
      "family:focus_tree:focus_tree"
    );

    await waitForBuildPageUpdate(() => !focusUpdate.disabled);
    act(() => focusUpdate.click());
    await waitForBuildPageUpdate(
      () => mounted.container.querySelector("#build-lifecycle-confirmation") !== null
    );

    const unrelatedRun = runningBuild(
      alpha,
      { family: "entity", id: "entity", kind: "family" },
      "entity-unrelated-run",
      Date.now()
    );
    act(() =>
      renderBuildPage(
        mounted.root,
        alpha,
        { ...lifecycle, runs: [unrelatedRun] },
        async () => undefined,
        { browser: browserWithFocusTree(alpha) }
      )
    );
    await flushAsyncWork();

    expect(
      requiredElement<HTMLElement>(
        mounted.container,
        "#build-lifecycle-confirmation"
      ).dataset.paradevConfirmationTargetKey
    ).toBe("family:focus_tree:focus_tree");
  });

  it("maps a recovered family run without redundant family metadata to its row", async () => {
    const lifecycle = buildLifecycle({
      runs: [
        runningBuild(
          alpha,
          { id: "entity", kind: "family" },
          "alpha-recovered-entity-run",
          1_000
        )
      ]
    });
    const mounted = mountBuildPage(alpha, lifecycle);
    const entityInterrupt = entityAction(
      mounted.container,
      "build.interrupt",
      "family:entity:entity"
    );

    expect(entityInterrupt.disabled).toBe(false);
    expect(entityInterrupt.dataset.paradevBuildRunId).toBe("alpha-recovered-entity-run");
    expect(
      mounted.container.querySelector(
        '.build-entity-row button[data-paradev-operation-id="build.start"][data-paradev-build-target-key="family:entity:entity"]'
      )
    ).toBeNull();

    act(() => entityInterrupt.click());
    await waitForBuildPageUpdate(() => mounted.container.querySelector("#build-lifecycle-confirmation") !== null);

    const confirmation = requiredElement<HTMLElement>(
      mounted.container,
      "#build-lifecycle-confirmation"
    );
    expect(confirmation.dataset.paradevConfirmationRunId).toBe("alpha-recovered-entity-run");
  });

  it("keeps a distinct sibling rebuild available while another target is running", async () => {
    const lifecycle = buildLifecycle({
      runs: [runningBuild(alpha, { family: "entity", id: "entity", kind: "family" }, "alpha-entity-run", 1_000)]
    });
    const mounted = mountBuildPage(alpha, lifecycle, async () => undefined, {
      browser: browserWithFocusTree(alpha)
    });
    const entityInterrupt = entityAction(
      mounted.container,
      "build.interrupt",
      "family:entity:entity"
    );
    const focusRebuild = entityAction(
      mounted.container,
      "build.start",
      "family:focus_tree:focus_tree"
    );

    expect(overviewAction(mounted.container, "build.interrupt").disabled).toBe(true);
    expect(entityInterrupt.disabled).toBe(false);
    await waitForBuildPageUpdate(() => !focusRebuild.disabled);
    expect(focusRebuild.disabled).toBe(false);
    act(() => focusRebuild.click());
    await waitForBuildPageUpdate(() => mounted.container.querySelector("#build-lifecycle-confirmation") !== null);

    expect(
      requiredElement<HTMLElement>(mounted.container, "#build-lifecycle-confirmation").dataset
        .paradevConfirmationTargetKey
    ).toBe("family:focus_tree:focus_tree");
    act(() =>
      requiredElement<HTMLInputElement>(
        mounted.container,
        "#build-lifecycle-confirmation input[type=checkbox]"
      ).click()
    );
    const continueButton = requiredElement<HTMLButtonElement>(
      mounted.container,
      "#build-lifecycle-confirmation .build-lifecycle-confirmation-actions .primary"
    );
    await waitForBuildPageUpdate(() => !continueButton.disabled);
    act(() => continueButton.click());
    await flushAsyncWork();

    expect(lifecycle.start).toHaveBeenCalledOnce();
    expect(lifecycle.start.mock.calls[0]?.[0]).toMatchObject({
      mode: "cached",
      target: { family: "focus_tree", id: "focus_tree", kind: "family" }
    });
    expect(lifecycle.interrupt).not.toHaveBeenCalled();
  });

  it("retries a failed automatic refresh deliberately and clears only refresh-kind lifecycle state", async () => {
    const clearError = vi.fn();
    const retryRecovery = vi.fn();
    const onProjectRefresh = vi.fn(async () => undefined);
    const lifecycle = buildLifecycle({
      clearError,
      errorsByProjectRoot: {
        [alpha.path]: { kind: "refresh", message: "Automatic refresh failed", projectRoot: alpha.path }
      },
      retryRecovery
    });
    const mounted = mountBuildPage(alpha, lifecycle, onProjectRefresh);

    act(() => requiredElement<HTMLButtonElement>(mounted.container, ".build-refresh-button").click());
    await flushAsyncWork();

    expect(onProjectRefresh).toHaveBeenCalledOnce();
    expect(onProjectRefresh).toHaveBeenCalledWith(alpha.path, alpha.id);
    expect(retryRecovery).toHaveBeenCalledOnce();
    expect(clearError).toHaveBeenCalledWith(alpha.path, "refresh");
  });

  it("renders real compiler progress detail and counts only while a build is running", async () => {
    const runningFull: BuildRunRecord = {
      ...runningFullBuild(alpha),
      progress: {
        detail: "Wrote output/common/ideas/PIHC3_ideas.txt",
        index: 31,
        label: "Writing artifacts",
        percent: 62,
        phase: "artifact_generation",
        total: 50
      }
    };
    const lifecycle = buildLifecycle({ runs: [runningFull] });
    const mounted = mountBuildPage(alpha, lifecycle);

    await waitForBuildPageUpdate(() => mounted.container.querySelector(".build-progress-detail") !== null);

    const detail = requiredElement<HTMLElement>(mounted.container, ".build-progress-detail");
    expect(detail.textContent).toContain("Wrote output/common/ideas/PIHC3_ideas.txt");
    expect(detail.textContent).toContain("31 / 50");
    expect(requiredElement<HTMLElement>(detail, "span").title).toBe(
      "Wrote output/common/ideas/PIHC3_ideas.txt"
    );

    act(() =>
      renderBuildPage(mounted.root, alpha, {
        ...lifecycle,
        runs: [{ ...runningFull, finishedAtMs: 2_000, state: "completed", terminalSequence: 1 }]
      })
    );
    await waitForBuildPageUpdate(() => mounted.container.querySelector(".build-progress-detail") === null);
  });

  it("keeps a failed manual refresh visible and lets failed global recovery outrank it", async () => {
    const clearError = vi.fn();
    const onProjectRefresh = vi.fn(async () => {
      throw new Error("Manual project refresh failed");
    });
    const lifecycle = buildLifecycle({ clearError });
    const mounted = mountBuildPage(alpha, lifecycle, onProjectRefresh);

    act(() => requiredElement<HTMLButtonElement>(mounted.container, ".build-refresh-button").click());
    await flushAsyncWork();

    expect(mounted.container.textContent).toContain("Manual project refresh failed");
    expect(clearError).not.toHaveBeenCalled();

    act(() =>
      renderBuildPage(
        mounted.root,
        alpha,
        {
          ...lifecycle,
          globalError: { kind: "status", message: "Build registry unavailable", projectRoot: null },
          recoveryState: "failed"
        },
        onProjectRefresh
      )
    );

    expect(mounted.container.textContent).toContain("Build registry unavailable");
    expect(mounted.container.textContent).not.toContain("Manual project refresh failed");
  });

  it("enables Run from a durable publication ledger with empty renderer storage", async () => {
    expect(window.localStorage.length).toBe(0);
    const mounted = mountBuildPage(alpha, buildLifecycle());

    await waitForBuildPageUpdate(
      () => requiredElement<HTMLButtonElement>(mounted.container, ".build-overview-actions .success").disabled === false
    );

    expect(serviceMocks.loadHoi4LaunchReadiness).toHaveBeenCalledWith(alpha.path);
    expect(mounted.container.querySelector(".build-launch-baseline-note")).toBeNull();
  });

  it.each([
    [
      "whole_project_baseline_missing",
      "Complete a whole-project build before starting HOI4."
    ],
    [
      "publication_incomplete",
      "Complete a whole-project build before starting HOI4."
    ],
    [
      "launcher_path_mismatch",
      "The HOI4 launcher registration is stale or unreadable."
    ]
  ])("keeps Run disabled for authoritative %s readiness", async (code, expectedDetail) => {
    serviceMocks.loadHoi4LaunchReadiness.mockResolvedValueOnce(
      launchReadiness(code, false, "Backend-only launch reason.")
    );
    const mounted = mountBuildPage(alpha, buildLifecycle());

    await waitForBuildPageUpdate(
      () =>
        requiredElement<HTMLElement>(mounted.container, ".build-launch-baseline-note").dataset
          .paradevLaunchReadinessCode === code
    );

    expect(requiredElement<HTMLButtonElement>(mounted.container, ".build-overview-actions .success").disabled).toBe(true);
    expect(mounted.container.textContent).toContain(expectedDetail);
    expect(mounted.container.textContent).not.toContain("Backend-only launch reason.");
  });

  it("keeps Run disabled after a readiness read error and retries through Refresh", async () => {
    serviceMocks.loadHoi4LaunchReadiness
      .mockRejectedValueOnce(new Error("publication ledger read failed"))
      .mockResolvedValueOnce(launchReadiness("ready", true, "Ready to launch."));
    const onProjectRefresh = vi.fn(async () => undefined);
    const mounted = mountBuildPage(alpha, buildLifecycle(), onProjectRefresh);

    await waitForBuildPageUpdate(
      () =>
        requiredElement<HTMLElement>(mounted.container, ".build-launch-baseline-note").dataset
          .paradevLaunchReadinessStatus === "failed"
    );

    expect(requiredElement<HTMLButtonElement>(mounted.container, ".build-overview-actions .success").disabled).toBe(true);
    expect(mounted.container.textContent).toContain("publication ledger read failed");
    expect(mounted.container.textContent).toContain("Use Refresh to retry");

    act(() => requiredElement<HTMLButtonElement>(mounted.container, ".build-refresh-button").click());
    await waitForBuildPageUpdate(
      () =>
        serviceMocks.loadHoi4LaunchReadiness.mock.calls.length === 2 &&
        requiredElement<HTMLButtonElement>(mounted.container, ".build-overview-actions .success").disabled === false
    );

    expect(onProjectRefresh).toHaveBeenCalledWith(alpha.path, alpha.id);
  });

  it("refreshes authoritative readiness after a successful whole-project build", async () => {
    serviceMocks.loadHoi4LaunchReadiness
      .mockResolvedValueOnce(
        launchReadiness(
          "whole_project_baseline_missing",
          false,
          "Build the whole project once before launching."
        )
      )
      .mockResolvedValueOnce(launchReadiness("ready", true, "Ready to launch."));
    const lifecycle = buildLifecycle();
    const mounted = mountBuildPage(alpha, lifecycle);
    await waitForBuildPageUpdate(() => serviceMocks.loadHoi4LaunchReadiness.mock.calls.length === 1);
    expect(requiredElement<HTMLButtonElement>(mounted.container, ".build-overview-actions .success").disabled).toBe(true);

    const completedFull: BuildRunRecord = {
      ...runningBuild(alpha, null, "completed-full", 3_000),
      finishedAtMs: 4_000,
      state: "completed",
      terminalSequence: 1
    };
    act(() => renderBuildPage(mounted.root, alpha, { ...lifecycle, runs: [completedFull] }));

    await waitForBuildPageUpdate(
      () =>
        serviceMocks.loadHoi4LaunchReadiness.mock.calls.length === 2 &&
        requiredElement<HTMLButtonElement>(mounted.container, ".build-overview-actions .success").disabled === false
    );
  });

  it("enables Run Game after a clean full baseline but disables it for a later partial failure", async () => {
    const target = { family: "achievement", id: "achievement", kind: "family" as const };
    const completedFull: BuildRunRecord = {
      ...runningBuild(alpha, null, "successful-full", 1_000),
      finishedAtMs: 2_000,
      state: "completed"
    };
    const staleFailure: BuildRunRecord = {
      ...runningBuild(alpha, target, "stale-partial-failure", 500),
      state: "failed"
    };
    const laterFailure: BuildRunRecord = {
      ...runningBuild(alpha, target, "later-partial-failure", 3_000),
      state: "failed"
    };
    const lifecycle = buildLifecycle({ runs: [completedFull, staleFailure] });
    const mounted = mountBuildPage(alpha, lifecycle);
    await flushAsyncWork();

    expect(requiredElement<HTMLButtonElement>(mounted.container, ".build-overview-actions .success").disabled).toBe(false);

    act(() => renderBuildPage(mounted.root, alpha, { ...lifecycle, runs: [completedFull, laterFailure] }));
    await flushAsyncWork();

    expect(requiredElement<HTMLButtonElement>(mounted.container, ".build-overview-actions .success").disabled).toBe(true);
  });
});

function buildLifecycle(
  overrides: Partial<BuildRunLifecycleController> = {}
): BuildRunLifecycleController & {
  clearError: ReturnType<typeof vi.fn>;
  interrupt: ReturnType<typeof vi.fn>;
  retryRecovery: ReturnType<typeof vi.fn>;
  start: ReturnType<typeof vi.fn>;
} {
  return {
    clearError: vi.fn(),
    errorsByProjectRoot: {},
    globalError: null,
    history: [],
    interrupt: vi.fn(async () => ({ schema: "paradev.desktop.build-run.v1", status: "idle" as const })),
    recoveryState: "ready",
    removeHistory: vi.fn(),
    retryRecovery: vi.fn(),
    runs: [],
    start: vi.fn(async () => ({ schema: "paradev.desktop.build-run.v1", status: "idle" as const })),
    ...overrides
  } as BuildRunLifecycleController & {
    clearError: ReturnType<typeof vi.fn>;
    interrupt: ReturnType<typeof vi.fn>;
    retryRecovery: ReturnType<typeof vi.fn>;
    start: ReturnType<typeof vi.fn>;
  };
}

type BuildPageRenderOptions = {
  browser?: ProjectBrowserPayload;
  buildDiagnosticsGeneration?: number;
  buildDiagnosticsRefreshSource?: BuildDiagnosticsRefreshSource;
  buildTargetIntent?: BuildTargetIntent | null;
  onBuildTargetIntentConsumed?: (nonce: number) => void;
  projectLoading?: boolean;
};

function mountBuildPage(
  project: ProjectOption,
  lifecycle: BuildRunLifecycleController,
  onProjectRefresh: (projectRoot?: string, fallbackProjectId?: string) => Promise<void> = async () => undefined,
  intentProps: BuildPageRenderOptions = {}
) {
  const container = document.createElement("div");
  document.body.append(container);
  const root = createRoot(container);
  const mounted = { container, root };
  mountedRoots.push(mounted);
  act(() => renderBuildPage(root, project, lifecycle, onProjectRefresh, intentProps));
  return mounted;
}

function renderBuildPage(
  root: Root,
  project: ProjectOption,
  lifecycle: BuildRunLifecycleController,
  onProjectRefresh: (projectRoot?: string, fallbackProjectId?: string) => Promise<void> = async () => undefined,
  intentProps: BuildPageRenderOptions = {}
): void {
  root.render(
    <BuildPage
      activeProject={project}
      browser={intentProps.browser ?? browserForProject(project)}
      buildDiagnosticsGeneration={intentProps.buildDiagnosticsGeneration}
      buildDiagnosticsRefreshSource={intentProps.buildDiagnosticsRefreshSource}
      buildLifecycle={lifecycle}
      buildTargetIntent={intentProps.buildTargetIntent}
      onBuildTargetIntentConsumed={intentProps.onBuildTargetIntentConsumed}
      onProjectRefresh={onProjectRefresh}
      openTarget="finder"
      projectLoading={intentProps.projectLoading ?? false}
      t={createTranslator("en")}
    />
  );
}

async function confirmAction(container: HTMLElement, operationId: "build.interrupt" | "build.start"): Promise<void> {
  await waitForBuildPageUpdate(() => !overviewAction(container, operationId).disabled);
  act(() => overviewAction(container, operationId).click());
  await waitForBuildPageUpdate(() =>
    container.querySelector("#build-lifecycle-confirmation input[type=checkbox]") !== null
  );
  act(() => requiredElement<HTMLInputElement>(container, "#build-lifecycle-confirmation input[type=checkbox]").click());
  const continueButton = requiredElement<HTMLButtonElement>(
    container,
    "#build-lifecycle-confirmation .build-lifecycle-confirmation-actions .primary"
  );
  await waitForBuildPageUpdate(() => !continueButton.disabled);
  act(() => continueButton.click());
  await flushAsyncWork();
}

async function waitForBuildPageUpdate(ready: () => boolean): Promise<void> {
  const maxEventLoopTurns = 100;
  for (let attempt = 0; attempt < maxEventLoopTurns; attempt += 1) {
    await act(async () => {
      await new Promise<void>((resolve) => window.setTimeout(resolve, 0));
    });
    if (ready()) {
      return;
    }
  }
  throw new Error(`BuildPage did not settle within ${maxEventLoopTurns} event-loop turns.`);
}

function overviewAction(container: HTMLElement, operationId: string): HTMLButtonElement {
  return requiredElement<HTMLButtonElement>(
    container,
    `.build-overview-actions button[data-paradev-operation-id="${operationId}"]`
  );
}

function entityAction(
  container: HTMLElement,
  operationId: string,
  targetKey: string
): HTMLButtonElement {
  return requiredElement<HTMLButtonElement>(
    container,
    `.build-entity-row button[data-paradev-operation-id="${operationId}"][data-paradev-build-target-key="${targetKey}"]`
  );
}

function requiredElement<ElementType extends Element>(container: HTMLElement, selector: string): ElementType {
  const element = container.querySelector<ElementType>(selector);
  if (!element) {
    throw new Error(`Expected BuildPage to contain ${selector}.`);
  }
  return element;
}

function runningFullBuild(project: ProjectOption): BuildRunRecord {
  return runningBuild(project, null, "alpha-full-run", 1_000);
}

function runningBuild(
  project: ProjectOption,
  target: BuildRunRecord["target"],
  runId: string,
  startedAtMs: number
): BuildRunRecord {
  return {
    mode: "cached",
    progress: null,
    projectId: project.projectId || project.id,
    projectRoot: project.path,
    runId,
    startedAtMs,
    state: "running",
    target
  };
}

function browserForProject(project: ProjectOption): ProjectBrowserPayload {
  return {
    diagnostics: [],
    families: [
      {
        family: "entity",
        id: "entity",
        item_count: 135,
        layouts: ["aggregate", "legacy_record"],
        source_count: 135,
        title: "Entity"
      }
    ],
    filters: {},
    items: [],
    profile: "hoi4",
    project_id: project.projectId || project.id,
    root: project.path,
    schema: "paradev.sdk.project-browser.v1",
    title: project.name
  };
}

function launchReadiness(code: string, ready: boolean, reason: string) {
  return {
    schema: "paradev.desktop.hoi4-launch-readiness.v1" as const,
    code,
    game: "hoi4",
    outputRoot: "/mods/alpha",
    projectId: alpha.projectId,
    projectRoot: alpha.path,
    ready,
    reason
  };
}

function browserWithFocusTree(project: ProjectOption): ProjectBrowserPayload {
  const browser = browserForProject(project);
  return {
    ...browser,
    families: [
      ...browser.families,
      {
        family: "focus_tree",
        id: "focus_tree",
        item_count: 42,
        layouts: ["aggregate"],
        source_count: 42,
        title: "Focus Tree"
      }
    ]
  };
}

function browserWithEntityModule(project: ProjectOption): ProjectBrowserPayload {
  const browser = browserForProject(project);
  return {
    ...browser,
    items: [
      {
        family: "entity",
        family_id: "entity",
        id: "module:entity/ALPHA",
        kind: "module",
        layout: "canonical",
        module_id: "entity/ALPHA",
        object_id: "ALPHA",
        relative_root: "src/modules/entity/ALPHA",
        root: `${project.path}/src/modules/entity/ALPHA`,
        source_count: 1,
        sources: [],
        title: "Alpha"
      }
    ]
  };
}

async function flushAsyncWork(): Promise<void> {
  await act(async () => {
    await Promise.resolve();
    await Promise.resolve();
  });
}

function deferred<Value>() {
  let reject!: (reason: unknown) => void;
  let resolve!: (value: Value) => void;
  const promise = new Promise<Value>((resolvePromise, rejectPromise) => {
    resolve = resolvePromise;
    reject = rejectPromise;
  });
  return { promise, reject, resolve };
}
