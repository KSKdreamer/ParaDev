import { readFileSync } from "node:fs";
import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";
import { getFrontendApiActionDetail } from "../data/frontendApi";
import { createTranslator } from "../i18n";
import type { ProjectBrowserPayload, ProjectOption } from "../types";
import {
  BuildActionAlert,
  BuildHistoryList,
  BuildLatestPartialResult,
  BuildLifecycleConfirmation,
  BuildPage,
  buildActionErrorDetail,
  buildHistoryForProject,
  buildLaunchReadinessDetail,
  buildModeDetail,
  buildProgressPhaseLabel,
  buildLaunchModeDetail,
  buildLifecycleActionContract,
  buildLifecycleConfirmationValuesKey,
  buildLifecycleSubmittedValuesForBuildPage,
  buildStartRequestForBuildPage,
  createBuildLifecycleConfirmationState,
  isBuildLifecyclePanelConfirmed
} from "./BuildPage";
import { BUILD_HOI4_LAUNCH_MODE_VALUES, BUILD_PARALLELISM_MIN, type BuildHistoryEntry, type BuildTarget } from "./buildPageModel";
import type { BuildRunLifecycleController, BuildRunRecord } from "./buildRunLifecycle";

const project: ProjectOption = {
  id: "PIHC3",
  projectId: "PIHC3",
  name: "The Pony In The High Castle",
  path: "/workspace/projects/PIHC3",
  game: "hoi4"
};

const otherProject: ProjectOption = {
  id: "OTHER",
  projectId: "OTHER",
  name: "Other Mod",
  path: "/workspace/projects/Other",
  game: "hoi4"
};

const familyOnlyBrowser: ProjectBrowserPayload = {
  schema: "paradev.sdk.project-browser.v1",
  project_id: "PIHC3",
  title: "The Pony In The High Castle",
  root: "/workspace/projects/PIHC3",
  profile: "hoi4",
  filters: {},
  families: [
    {
      family: "achievement",
      id: "achievements",
      item_count: 49,
      layouts: ["canonical"],
      source_count: 245,
      title: "Achievements",
      group: "events",
      title_key: "modules.achievements.title"
    }
  ],
  items: [],
  diagnostics: []
};

const buildLifecycle: BuildRunLifecycleController = {
  clearError: () => undefined,
  errorsByProjectRoot: {},
  globalError: null,
  history: [],
  interrupt: async () => ({ schema: "paradev.desktop.build-run.v1", status: "idle" }),
  recoveryState: "ready",
  removeHistory: () => undefined,
  retryRecovery: () => undefined,
  runs: [],
  start: async () => ({ schema: "paradev.desktop.build-run.v1", status: "idle" })
};

describe("BuildPage", () => {
  it("localizes actionable launch-readiness codes without exposing backend English", () => {
    const detail = buildLaunchReadinessDetail(createTranslator("zh"), {
      schema: "paradev.desktop.hoi4-launch-readiness.v1",
      code: "output_not_launcher_visible",
      game: "hoi4",
      outputRoot: "C:\\Mods\\PIHC3",
      projectId: "PIHC3",
      projectRoot: "C:\\Projects\\PIHC3",
      ready: false,
      reason: "Backend-only English reason."
    });

    expect(detail).toContain("不在 HOI4 当前用户 Mod 目录中");
    expect(detail).toContain("C:\\Mods\\PIHC3");
    expect(detail).not.toContain("Backend-only English reason.");
  });

  it("distinguishes whole-project modes from safe partial updates in both locales", () => {
    const render = (locale: "en" | "zh") =>
      renderToStaticMarkup(
        <BuildPage
          activeProject={project}
          buildLifecycle={buildLifecycle}
          browser={familyOnlyBrowser}
          onProjectRefresh={async () => undefined}
          openTarget="finder"
          projectLoading={false}
          t={createTranslator(locale)}
        />
      );

    const english = render("en");
    expect(english).toContain("Whole-project mode");
    expect(english).toContain("Update existing output");
    expect(english).toContain("Clean output and rebuild");
    expect(english).toContain(
      "Compiles the whole project and safely updates generated files without cleaning the output first."
    );
    expect(english).toContain("Safe partial update");
    expect(buildModeDetail(createTranslator("en"), "full")).toBe(
      "Cleans ParaDev-owned generated output and build data, then compiles the whole project."
    );

    const chinese = render("zh");
    expect(chinese).toContain("全项目模式");
    expect(chinese).toContain("更新现有输出");
    expect(chinese).toContain("清理输出并重建");
    expect(chinese).toContain("编译整个项目并安全更新生成文件，不会先清理输出目录。");
    expect(chinese).toContain("安全局部更新");
    expect(buildModeDetail(createTranslator("zh"), "full")).toBe(
      "先清理 ParaDev 拥有的生成输出和构建数据，再编译整个项目。"
    );
  });

  it("uses editor module translations for buildable family rows without a Family prefix", () => {
    const html = renderToStaticMarkup(
      <BuildPage
        activeProject={project}
        buildLifecycle={buildLifecycle}
        browser={familyOnlyBrowser}
        onProjectRefresh={async () => undefined}
        openTarget="finder"
        projectLoading={false}
        t={createTranslator("zh")}
      />
    );

    expect(html).toContain("成就");
    expect(html).not.toContain("Achievement");
    expect(html).not.toContain("族 ·");
  });

  it("renders compact build actions and no duplicated ready detail text", () => {
    const html = renderToStaticMarkup(
      <BuildPage
        activeProject={project}
        buildLifecycle={buildLifecycle}
        browser={familyOnlyBrowser}
        onProjectRefresh={async () => undefined}
        openTarget="finder"
        projectLoading={false}
        t={createTranslator("zh")}
      />
    );

    expect(html).toContain("构建");
    expect(html).toContain("中断");
    expect(html).toContain("打开");
    expect(html).toContain("运行");
    expect(html).toContain('data-paradev-config-key="paradev.build.parallelism"');
    expect(html).toContain('data-paradev-config-key="paradev.hoi4.launch_mode"');
    expect(html).toContain(`min="${BUILD_PARALLELISM_MIN}"`);
    for (const value of BUILD_HOI4_LAUNCH_MODE_VALUES) {
      expect(html).toContain(`value="${value}"`);
    }
    expect(html).toContain('data-paradev-operation-id="build.start"');
    expect(html).toContain('data-paradev-sdk-call="desktop_start_build"');
    expect(html).toContain('data-paradev-rest-method="POST"');
    expect(html).toContain('data-paradev-rest-path="/desktop/builds"');
    expect(html).toContain('data-paradev-status-operation-id="build.status"');
    expect(html).toContain('data-paradev-status-sdk-call="desktop_build_status"');
    expect(html).toContain('data-paradev-status-rest-method="GET"');
    expect(html).toContain('data-paradev-status-rest-path="/desktop/builds/status"');
    expect(html).toContain('data-paradev-operation-id="build.interrupt"');
    expect(html).toContain('data-paradev-sdk-call="desktop_interrupt_build"');
    expect(html).toContain('data-paradev-rest-path="/desktop/builds/interrupt"');
    expect(html).toContain("Steam/默认");
    expect(html).toContain('aria-label="准备就绪"');
    expect(html).not.toContain("build-lifecycle-confirmation");
    expect(html).not.toContain("开始构建");
    expect(html).not.toContain("运行 HOI4");
    expect(html).not.toContain("当前项目可以开始构建。");
    expect(html).toContain("-- : --");
  });

  it("keeps selected-project build controls independent from another project run", () => {
    const otherProjectHtml = renderToStaticMarkup(
      <BuildPage
        activeProject={project}
        buildLifecycle={{ ...buildLifecycle, runs: [runningBuildRecord(otherProject, null, "other-full")] }}
        browser={familyOnlyBrowser}
        onProjectRefresh={async () => undefined}
        openTarget="finder"
        projectLoading={false}
        t={createTranslator("en")}
      />
    );
    const selectedProjectHtml = renderToStaticMarkup(
      <BuildPage
        activeProject={project}
        buildLifecycle={{ ...buildLifecycle, runs: [runningBuildRecord(project, null, "selected-full")] }}
        browser={familyOnlyBrowser}
        onProjectRefresh={async () => undefined}
        openTarget="finder"
        projectLoading={false}
        t={createTranslator("en")}
      />
    );

    expect(buildStartButtonTags(otherProjectHtml)).not.toHaveLength(0);
    expect(buildStartButtonTags(otherProjectHtml).every((tag) => !tag.includes("disabled"))).toBe(true);
    expect(buildStartButtonTags(selectedProjectHtml).every((tag) => tag.includes("disabled"))).toBe(true);
  });

  it("prioritizes the blocking global recovery failure over stale project errors", () => {
    const html = renderToStaticMarkup(
      <BuildPage
        activeProject={project}
        buildLifecycle={{
          ...buildLifecycle,
          errorsByProjectRoot: {
            [project.path]: { kind: "refresh", message: "stale project refresh error", projectRoot: project.path }
          },
          globalError: { kind: "status", message: "build registry unavailable", projectRoot: null },
          recoveryState: "failed"
        }}
        browser={familyOnlyBrowser}
        onProjectRefresh={async () => undefined}
        openTarget="finder"
        projectLoading={false}
        t={createTranslator("en")}
      />
    );

    expect(html).toContain("build registry unavailable");
    expect(html).not.toContain("stale project refresh error");
  });

  it("shows the latest partial failure in the overview and affected entity", () => {
    const failedTarget = { family: "achievement", id: "achievement", kind: "family" as const };
    const failedRun: BuildRunRecord = {
      ...runningBuildRecord(project, failedTarget, "failed-partial"),
      errorSummary: "Achievement compilation failed.",
      progress: { phase: "source_compile", percent: 25 },
      state: "failed"
    };
    const html = renderToStaticMarkup(
      <BuildPage
        activeProject={project}
        buildLifecycle={{ ...buildLifecycle, runs: [failedRun] }}
        browser={familyOnlyBrowser}
        onProjectRefresh={async () => undefined}
        openTarget="finder"
        projectLoading={false}
        t={createTranslator("en")}
      />
    );

    expect(html).toContain("Compilation failed");
    expect(html).toContain("Achievement compilation failed.");
    expect(html).not.toContain('aria-label="Ready"');
  });

  it("shows a whole-project compiler failure without requiring history expansion", () => {
    const failedRun: BuildRunRecord = {
      ...runningBuildRecord(project, null, "failed-full"),
      errorSummary: "Output ownership could not be verified.",
      progress: { phase: "validating_publication", percent: 75 },
      state: "failed"
    };
    const html = renderToStaticMarkup(
      <BuildPage
        activeProject={project}
        buildLifecycle={{ ...buildLifecycle, runs: [failedRun] }}
        browser={familyOnlyBrowser}
        onProjectRefresh={async () => undefined}
        openTarget="finder"
        projectLoading={false}
        t={createTranslator("en")}
      />
    );

    expect(html).toContain('role="alert"');
    expect(html).toContain("Output ownership could not be verified.");
  });

  it("keeps an adverse target in the overview after a sibling target completes later", () => {
    const failedTarget = { family: "achievement", id: "achievement", kind: "family" as const };
    const completedTarget = { family: "focus_tree", id: "focus_tree", kind: "family" as const };
    const failedRun: BuildRunRecord = {
      ...runningBuildRecord(project, failedTarget, "failed-achievement"),
      errorSummary: "Achievement compilation failed.",
      progress: { phase: "source_compile", percent: 25 },
      state: "failed"
    };
    const completedRun: BuildRunRecord = {
      ...runningBuildRecord(project, completedTarget, "completed-focus-tree"),
      progress: { phase: "complete", percent: 100 },
      startedAtMs: 2_000,
      state: "completed"
    };
    const html = renderToStaticMarkup(
      <BuildPage
        activeProject={project}
        buildLifecycle={{ ...buildLifecycle, runs: [failedRun, completedRun] }}
        browser={browserWithSecondFamily()}
        onProjectRefresh={async () => undefined}
        openTarget="finder"
        projectLoading={false}
        t={createTranslator("en")}
      />
    );

    expect(html).toContain('class="build-overview-card build-state-failed"');
    expect(html).toContain('class="build-entity-row failed"');
    expect(html).toContain('class="build-entity-row ready"');
    expect(html).toContain("Achievement compilation failed.");
    expect(html).toContain("National Focuses rebuilt successfully");
    expect(html).toContain("This rebuild checked only National Focuses.");
  });

  it("shows a successful family rebuild without clearing an interrupted full-build status", () => {
    const target = { family: "achievement", id: "achievement", kind: "family" as const };
    const interruptedFull: BuildRunRecord = {
      finishedAtMs: 2_000,
      mode: "cached",
      progress: { phase: "source_compile", percent: 40 },
      projectId: project.projectId || project.id,
      projectRoot: project.path,
      runId: "interrupted-full",
      startedAtMs: 1_000,
      state: "interrupted",
      target: null,
      terminalSequence: 30
    };
    const completedFamily: BuildRunRecord = {
      finishedAtMs: 4_000,
      mode: "cached",
      progress: { phase: "complete", percent: 100 },
      projectId: project.projectId || project.id,
      projectRoot: project.path,
      runId: "completed-achievement",
      startedAtMs: 3_000,
      state: "completed",
      target,
      terminalSequence: 31
    };
    const html = renderToStaticMarkup(
      <BuildPage
        activeProject={project}
        buildLifecycle={{ ...buildLifecycle, runs: [interruptedFull, completedFamily] }}
        browser={familyOnlyBrowser}
        onProjectRefresh={async () => undefined}
        openTarget="finder"
        projectLoading={false}
        t={createTranslator("en")}
      />
    );

    expect(html).toContain('class="build-overview-card build-state-interrupted"');
    expect(html).toContain('data-paradev-latest-partial-result="completed"');
    expect(html).toContain('aria-live="polite"');
    expect(html).toContain("Achievements rebuilt successfully");
    expect(html).toContain("This rebuild checked only Achievements. Use Build for a whole-project check.");
    expect(runGameButtonTag(html)).toContain("disabled");
  });

  it("does not leak a latest partial result across project roots with the same project id", () => {
    const clone = { ...project, path: "/workspace/clones/PIHC3" };
    const completedFamily: BuildRunRecord = {
      ...runningBuildRecord(project, { family: "achievement", id: "achievement", kind: "family" }, "completed-achievement"),
      finishedAtMs: 2_000,
      state: "completed",
      terminalSequence: 1
    };
    const html = renderToStaticMarkup(
      <BuildPage
        activeProject={clone}
        buildLifecycle={{ ...buildLifecycle, runs: [completedFamily] }}
        browser={{ ...familyOnlyBrowser, root: clone.path }}
        onProjectRefresh={async () => undefined}
        openTarget="finder"
        projectLoading={false}
        t={createTranslator("en")}
      />
    );

    expect(html).not.toContain("build-latest-partial-result");
    expect(html).not.toContain("rebuilt successfully");
  });

  it("hides a stale partial result while a full-project build is running", () => {
    const completedFamily: BuildRunRecord = {
      ...runningBuildRecord(project, { family: "achievement", id: "achievement", kind: "family" }, "completed-achievement"),
      finishedAtMs: 2_000,
      state: "completed",
      terminalSequence: 1
    };
    const runningFull: BuildRunRecord = {
      ...runningBuildRecord(project, null, "running-full"),
      mode: "full",
      progress: { phase: "discover_modules", percent: 10 },
      startedAtMs: 3_000
    };
    const html = renderToStaticMarkup(
      <BuildPage
        activeProject={project}
        buildLifecycle={{ ...buildLifecycle, runs: [completedFamily, runningFull] }}
        browser={familyOnlyBrowser}
        onProjectRefresh={async () => undefined}
        openTarget="finder"
        projectLoading={false}
        t={createTranslator("en")}
      />
    );

    expect(html).toContain("Compilation running");
    expect(html).not.toContain("build-latest-partial-result");
    expect(html).not.toContain("Use Build for a whole-project check");
  });

  it("uses a successful full build as a clean baseline over older adverse partial slots", () => {
    const achievementTarget = { family: "achievement", id: "achievement", kind: "family" as const };
    const focusTarget = { family: "focus_tree", id: "focus_tree", kind: "family" as const };
    const failedAchievement: BuildRunRecord = {
      ...runningBuildRecord(project, achievementTarget, "old-failed-achievement"),
      errorSummary: "Old achievement failure must stay hidden.",
      state: "failed"
    };
    const interruptedFocus: BuildRunRecord = {
      ...runningBuildRecord(project, focusTarget, "old-interrupted-focus"),
      errorSummary: "Old focus interruption must stay hidden.",
      startedAtMs: 1_500,
      state: "interrupted"
    };
    const completedFull: BuildRunRecord = {
      finishedAtMs: 3_000,
      mode: "full",
      progress: { label: "Complete", percent: 100, phase: "complete" },
      projectId: project.projectId || project.id,
      projectRoot: project.path,
      runId: "successful-full",
      startedAtMs: 2_000,
      state: "completed",
      target: null
    };
    const html = renderToStaticMarkup(
      <BuildPage
        activeProject={project}
        buildLifecycle={{
          ...buildLifecycle,
          // Old terminal responses can arrive after the full-build response.
          runs: [completedFull, failedAchievement, interruptedFocus]
        }}
        browser={browserWithSecondFamily()}
        onProjectRefresh={async () => undefined}
        openTarget="finder"
        projectLoading={false}
        t={createTranslator("en")}
      />
    );

    expect(html).toContain('class="build-overview-card build-state-completed"');
    expect(html.match(/class="build-entity-row ready"/g)).toHaveLength(2);
    expect(html).not.toContain("Old achievement failure must stay hidden.");
    expect(html).not.toContain("Old focus interruption must stay hidden.");
  });

  it("surfaces a partial failure that starts after the successful full-build baseline", () => {
    const failedTarget = { family: "achievement", id: "achievement", kind: "family" as const };
    const completedFull: BuildRunRecord = {
      finishedAtMs: 2_000,
      mode: "full",
      progress: { label: "Complete", percent: 100, phase: "complete" },
      projectId: project.projectId || project.id,
      projectRoot: project.path,
      runId: "successful-full",
      startedAtMs: 1_000,
      state: "completed",
      target: null
    };
    const laterFailure: BuildRunRecord = {
      ...runningBuildRecord(project, failedTarget, "later-failed-achievement"),
      errorSummary: "New achievement failure remains actionable.",
      startedAtMs: 3_000,
      state: "failed"
    };
    const html = renderToStaticMarkup(
      <BuildPage
        activeProject={project}
        buildLifecycle={{ ...buildLifecycle, runs: [completedFull, laterFailure] }}
        browser={familyOnlyBrowser}
        onProjectRefresh={async () => undefined}
        openTarget="finder"
        projectLoading={false}
        t={createTranslator("en")}
      />
    );

    expect(html).toContain('class="build-overview-card build-state-failed"');
    expect(html).toContain('class="build-entity-row failed"');
    expect(html).toContain("New achievement failure remains actionable.");
  });

  it("filters clone histories by project root even when manifest ids collide", () => {
    const original: BuildHistoryEntry = {
      durationMs: 1_000,
      finishedAtMs: 2_000,
      id: "original",
      mode: "cached",
      projectId: "PIHC3",
      projectRoot: project.path,
      startedAtMs: 1_000,
      status: "completed"
    };
    const clone: BuildHistoryEntry = {
      ...original,
      command: ["private-clone-command"],
      id: "clone",
      outputPath: "/private/clone/output",
      projectRoot: "/workspace/clones/PIHC3"
    };

    expect(buildHistoryForProject([clone, original], project.path)).toEqual([original]);
  });

  it("renders passive AI handoff notices for build plan and start intents", () => {
    const planHtml = renderToStaticMarkup(
      <BuildPage
        activeProject={project}
        buildLifecycle={buildLifecycle}
        aiOperationIntent={{
          nonce: 1,
          operationId: "build.plan",
          role: "build",
          sources: [{ kind: "diagnostics", label: "3 diagnostics" }]
        }}
        browser={familyOnlyBrowser}
        onProjectRefresh={async () => undefined}
        openTarget="finder"
        projectLoading={false}
        t={createTranslator("en")}
      />
    );
    const startHtml = renderToStaticMarkup(
      <BuildPage
        activeProject={project}
        buildLifecycle={buildLifecycle}
        aiOperationIntent={{
          nonce: 2,
          operationId: "build.start",
          role: "build",
          sources: [{ familyId: "focus_tree", kind: "workspace", label: "National Focuses" }]
        }}
        browser={familyOnlyBrowser}
        onProjectRefresh={async () => undefined}
        openTarget="finder"
        projectLoading={false}
        t={createTranslator("en")}
      />
    );

    expect(planHtml).toContain('data-paradev-ai-operation-id="build.plan"');
    expect(planHtml).toContain('data-paradev-ai-operation-passive="true"');
    expect(planHtml).toContain("Build plan context is open. No build is running");
    expect(planHtml).toContain("Context: 3 diagnostics");
    expect(planHtml).not.toContain("build-lifecycle-confirmation");
    expect(startHtml).toContain('data-paradev-ai-operation-id="build.start"');
    expect(startHtml).toContain("No build started; the normal confirmation is still required.");
    expect(startHtml).toContain("Context: National Focuses");
    expect(startHtml).not.toContain("build-lifecycle-confirmation");
  });

  it("derives build lifecycle contracts from generated frontend API metadata", () => {
    const source = readFileSync(new URL("./BuildPage.tsx", import.meta.url), "utf-8");

    expect(source).not.toContain('confirmationTitle: "Confirm Build Start"');
    expect(source).not.toContain('summary: "Start one desktop build run through the Python desktop facade."');
    expect(source).not.toContain('sdkCall: "desktop_start_build"');
    expect(buildLifecycleActionContract("start")).toEqual({
      confirmationDefaultConfirmed: false,
      confirmationRequired: true,
      confirmationScope: "project-files",
      confirmationStyle: "write",
      confirmationTitle: "Confirm Build Start",
      operationId: "build.start",
      payload: "paradev.desktop.build-run.v1",
      restMethod: "POST",
      restPath: "/desktop/builds",
      sdkCall: "desktop_start_build",
      summary: "Start one desktop build run through the Python desktop facade."
    });
    expect(buildLifecycleActionContract("status")).toEqual({
      confirmationDefaultConfirmed: true,
      confirmationRequired: false,
      confirmationScope: "none",
      confirmationStyle: "none",
      confirmationTitle: "Build Status",
      operationId: "build.status",
      payload: "paradev.desktop.build-run.v1",
      restMethod: "GET",
      restPath: "/desktop/builds/status",
      sdkCall: "desktop_build_status",
      summary: "Return active or retained terminal status for one exact desktop build run."
    });
    expect(buildLifecycleActionContract("interrupt")).toEqual({
      confirmationDefaultConfirmed: false,
      confirmationRequired: true,
      confirmationScope: "project-files",
      confirmationStyle: "write",
      confirmationTitle: "Confirm Build Interrupt",
      operationId: "build.interrupt",
      payload: "paradev.desktop.build-run.v1",
      restMethod: "POST",
      restPath: "/desktop/builds/interrupt",
      sdkCall: "desktop_interrupt_build",
      summary: "Interrupt one exact active desktop build run or return its retained terminal status."
    });
    expectBuildLifecycleContractMatchesGenerated("start");
    expectBuildLifecycleContractMatchesGenerated("status");
    expectBuildLifecycleContractMatchesGenerated("interrupt");
  });

  it("renders a compact localized confirmation strip backed by generated action run state", async () => {
    const values = buildLifecycleSubmittedValuesForBuildPage({
      action: "start",
      mode: "full",
      parallelism: 4,
      project,
      strictMetadata: true,
      target: null
    });
    const confirmation = await createBuildLifecycleConfirmationState("start", null, values, false);
    const html = renderToStaticMarkup(
      <BuildLifecycleConfirmation
        busy={false}
        confirmation={confirmation}
        onAcceptedChange={() => undefined}
        onCancel={() => undefined}
        onConfirm={() => undefined}
        t={createTranslator("zh")}
      />
    );

    expect(confirmation.panel.run_state).toMatchObject({
      confirmation_satisfied: false,
      disabled: true,
      detail: "Requires confirmation: Confirm Build Start"
    });
    expect(html).toContain('id="build-lifecycle-confirmation"');
    expect(html).toContain('data-paradev-confirmation-operation-id="build.start"');
    expect(html).toContain('data-paradev-confirmation-scope="project-files"');
    expect(html).toContain('data-paradev-confirmation-style="write"');
    expect(html).toContain('data-paradev-confirmation-sdk-title="Confirm Build Start"');
    expect(html).toContain('data-paradev-confirmation-run-detail="Requires confirmation: Confirm Build Start"');
    expect(html).toContain('data-paradev-confirmation-satisfied="false"');
    expect(html).toContain('data-paradev-confirmation-target-key="full"');
    expect(html).toContain("确认全项目构建");
    expect(html).toContain("先清理 ParaDev 拥有的生成输出和构建数据，再编译整个项目。");
    expect(html).toContain("取消");
    expect(html).toContain("继续");
    expect(html).toMatch(/<button class="toolbar-button primary"[^>]*disabled=""/);

    const accepted = await createBuildLifecycleConfirmationState("start", null, values, true);
    expect(accepted.panel.run_state).toMatchObject({
      confirmation_satisfied: true,
      disabled: false,
      detail: "Not run"
    });
    expect(
      isBuildLifecyclePanelConfirmed(
        accepted,
        "start",
        "full",
        buildLifecycleConfirmationValuesKey("start", null, values)
      )
    ).toBe(true);
  });

  it("keeps partial rebuild confirmation scoped to the selected target", async () => {
    const firstTarget: BuildTarget = { kind: "module", id: "focus_tree/C01_MAIN", family: "focus_tree" };
    const secondTarget: BuildTarget = { kind: "module", id: "event/E01_MAIN", family: "event" };
    const values = buildLifecycleSubmittedValuesForBuildPage({
      action: "start",
      mode: "cached",
      parallelism: 2,
      project,
      strictMetadata: false,
      target: firstTarget
    });
    const accepted = await createBuildLifecycleConfirmationState("start", firstTarget, values, true);
    const english = renderToStaticMarkup(
      <BuildLifecycleConfirmation
        busy={false}
        confirmation={accepted}
        onAcceptedChange={() => undefined}
        onCancel={() => undefined}
        onConfirm={() => undefined}
        t={createTranslator("en")}
      />
    );
    const chinese = renderToStaticMarkup(
      <BuildLifecycleConfirmation
        busy={false}
        confirmation={accepted}
        onAcceptedChange={() => undefined}
        onCancel={() => undefined}
        onConfirm={() => undefined}
        t={createTranslator("zh")}
      />
    );

    expect(accepted.targetKey).toBe("module:focus_tree:focus_tree/C01_MAIN");
    expect(english).toContain("Confirm safe partial update");
    expect(english).toContain(
      "Update only focus_tree/C01_MAIN without cleaning generated roots. The whole-project mode above does not apply."
    );
    expect(chinese).toContain("确认安全局部更新");
    expect(chinese).toContain(
      "仅更新 focus_tree/C01_MAIN，不会清理生成目录。上方的全项目模式不适用于局部更新。"
    );
    expect(
      isBuildLifecyclePanelConfirmed(
        accepted,
        "start",
        "module:focus_tree:focus_tree/C01_MAIN",
        buildLifecycleConfirmationValuesKey("start", firstTarget, values)
      )
    ).toBe(true);
    expect(
      isBuildLifecyclePanelConfirmed(
        accepted,
        "start",
        "module:event:event/E01_MAIN",
        buildLifecycleConfirmationValuesKey("start", secondTarget, values)
      )
    ).toBe(false);
    expect(buildLifecycleSubmittedValuesForBuildPage({
      action: "start",
      mode: "cached",
      parallelism: 2,
      project,
      strictMetadata: false,
      target: secondTarget
    })).toMatchObject({
      target: secondTarget
    });
  });

  it("explains which HOI4 launch target will be used", () => {
    expect(buildLaunchModeDetail(createTranslator("en"), "steam", "")).toBe("Steam/default");
    expect(buildLaunchModeDetail(createTranslator("zh"), "local", "/Games/Hearts of Iron IV")).toBe("本地目录：/Games/Hearts of Iron IV");
    expect(buildLaunchModeDetail(createTranslator("zh"), "local", "")).toBe("请在配置中设置 HOI4 游戏目录");
  });

  it("humanizes unknown backend build progress phases", () => {
    expect(buildProgressPhaseLabel(createTranslator("en"), "asset_hash_refresh", 0)).toBe("Asset hash refresh");
    expect(buildProgressPhaseLabel(createTranslator("zh"), "asset_hash_refresh", 0)).toBe("阶段：Asset hash refresh");
    expect(buildProgressPhaseLabel(createTranslator("en"), "waiting", 0)).toBe("Starting compiler");
    expect(buildProgressPhaseLabel(createTranslator("zh"), "waiting", 0)).toBe("正在启动编译器");
    expect(buildProgressPhaseLabel(createTranslator("en"), "validating_publication", 0)).toBe("Validating publication");
    expect(buildProgressPhaseLabel(createTranslator("zh"), "validating_publication", 0)).toBe("验证发布安全性");
    expect(buildProgressPhaseLabel(createTranslator("zh"), "", 0)).toBe("准备就绪");
  });

  it("renders and forwards the strict metadata build option", () => {
    const target: BuildTarget = { kind: "module", id: "focus_tree/C01_MAIN", family: "focus_tree" };
    const html = renderToStaticMarkup(
      <BuildPage
        activeProject={project}
        buildLifecycle={buildLifecycle}
        browser={familyOnlyBrowser}
        onProjectRefresh={async () => undefined}
        openTarget="finder"
        projectLoading={false}
        t={createTranslator("en")}
      />
    );

    expect(html).toContain('data-paradev-build-strict-metadata="true"');
    expect(html).toContain('data-paradev-config-key="paradev.build.strict_metadata"');
    expect(html).toContain("Strict metadata");
    expect(buildStartRequestForBuildPage(project, "full", null, true, 4)).toEqual({
      projectRoot: "/workspace/projects/PIHC3",
      mode: "full",
      parallelism: 4,
      profile: "hoi4",
      strictMetadata: true,
      target: null
    });
    expect(buildStartRequestForBuildPage(project, "cached", target, false, 2)).toEqual({
      projectRoot: "/workspace/projects/PIHC3",
      mode: "cached",
      parallelism: 2,
      profile: "hoi4",
      strictMetadata: false,
      target
    });
  });

  it("shows actionable blocking diagnostics instead of only a counter", () => {
    const html = renderToStaticMarkup(
      <BuildPage
        activeProject={project}
        buildLifecycle={buildLifecycle}
        browser={{
          ...familyOnlyBrowser,
          diagnostics: [
            {
              code: "metadata.unknown_key",
              message: "Module focus/GER_sample has unsupported metadata key legacy_hint.",
              severity: "error",
              source: {
                family: "focus",
                module_id: "focus/GER_sample",
                path: "/workspace/projects/PIHC3/src/modules/focus/GER_sample/meta.yaml",
                slot: "metadata"
              },
              source_path: "meta.yaml"
            },
            {
              code: "localization.duplicate_key",
              message: "Duplicate localization key PIHC_TEST.",
              severity: "warning",
              source_path: "main.loc"
            }
          ]
        }}
        onProjectRefresh={async () => undefined}
        openTarget="finder"
        projectLoading={false}
        t={createTranslator("en")}
      />
    );

    expect(html).toContain("Fix these diagnostics before building");
    expect(html).toContain("Module focus/GER_sample has unsupported metadata key legacy_hint.");
    expect(html).toContain("metadata.unknown_key");
    expect(html).toContain("focus/GER_sample");
    expect(html).toContain("meta.yaml");
    expect(html).not.toContain("Duplicate localization key PIHC_TEST.");
    expect(runGameButtonTag(html)).toContain("disabled");
  });

  it("shows failed build reasons and command details when history is expanded", () => {
    const failedEntry: BuildHistoryEntry = {
      command: ["uv", "run", "paradev", "build"],
      durationMs: 7_000,
      errorPath: "/tmp/paradev-build/build-1.stderr.log",
      errorSummary: "RuntimeError: metadata schema unavailable.",
      exitCode: 2,
      finishedAtMs: 8_000,
      id: "failed-build",
      mode: "cached",
      outputPath: "/tmp/paradev-build/build-1.json",
      projectId: "PIHC3",
      projectRoot: project.path,
      startedAtMs: 1_000,
      status: "failed",
      target: null
    };

    const html = renderToStaticMarkup(
      <BuildHistoryList
        entries={[failedEntry]}
        expandedIds={new Set(["failed-build"])}
        onRemove={() => undefined}
        onToggle={() => undefined}
        t={createTranslator("zh")}
      />
    );

    expect(html).toContain("RuntimeError: metadata schema unavailable.");
    expect(html).toContain("uv run paradev build");
    expect(html).toContain("7 秒");
    expect(html).toContain(formatExpectedZhTimestamp(failedEntry.finishedAtMs));
    expect(html).not.toMatch(/\b(?:AM|PM)\b/);
    expect(html).not.toContain("7s");
    expect(html).toContain("错误日志");
    expect(html).toContain("输出");
  });

  it("names targeted history rows and exposes disclosure state", () => {
    const entry: BuildHistoryEntry = {
      durationMs: 12_000,
      finishedAtMs: 20_000,
      id: "entity-rebuild",
      mode: "cached",
      projectId: "PIHC3",
      projectRoot: project.path,
      startedAtMs: 8_000,
      status: "completed",
      target: { family: "entity", id: "entity", kind: "family" }
    };
    const html = renderToStaticMarkup(
      <BuildHistoryList
        entries={[entry]}
        expandedIds={new Set()}
        onRemove={() => undefined}
        onToggle={() => undefined}
        t={createTranslator("en")}
      />
    );

    expect(html).toContain("Partial rebuild · Family · entity");
    expect(html).toContain('aria-expanded="false"');
    expect(html).toContain('aria-controls="build-history-details-0"');
  });

  it("renders a localized visible alert for failed build actions", () => {
    const html = renderToStaticMarkup(<BuildActionAlert detail="HOI4 app is missing." t={createTranslator("zh")} />);

    expect(html).toContain('role="alert"');
    expect(html).toContain("构建操作失败");
    expect(html).toContain("HOI4 app is missing.");
  });

  it.each([
    ["failed", "实体重构建失败", "请在构建历史中检查并修复实体"],
    ["interrupted", "实体重构建已中断", "请重试实体"]
  ] as const)("renders a durable localized %s partial result", (state, title, nextStep) => {
    const html = renderToStaticMarkup(
      <BuildLatestPartialResult
        result={{
          durationMs: 12_000,
          finishedAtMs: 20_000,
          state,
          target: { family: "entity", id: "entity", kind: "family" }
        }}
        targetLabel="实体"
        t={createTranslator("zh")}
      />
    );

    expect(html).toContain('role="status"');
    expect(html).toContain(`data-paradev-latest-partial-result="${state}"`);
    expect(html).toContain(title);
    expect(html).toContain(nextStep);
    expect(html).toContain("12 秒");
  });

  it("formats bridge errors for the action a modder attempted", () => {
    expect(buildActionErrorDetail(createTranslator("en"), "openOutput", new Error("Open path does not exist."))).toBe(
      "Output folder could not be opened: Open path does not exist."
    );
    expect(
      buildActionErrorDetail(createTranslator("zh"), "openOutput", new Error("Opening local paths requires the ParaDev desktop application."))
    ).toBe("无法打开输出目录：此操作需要使用 ParaDev 桌面应用。");
    expect(
      buildActionErrorDetail(createTranslator("zh"), "runGame", new Error("Launching HOI4 requires the ParaDev desktop application."))
    ).toBe("HOI4 启动失败：此操作需要使用 ParaDev 桌面应用。");
    expect(
      buildActionErrorDetail(createTranslator("en"), "configRead", new Error("Reading ParaDev config values requires the ParaDev desktop application."))
    ).toBe("Build settings could not be loaded: This action requires the ParaDev desktop application.");
    expect(
      buildActionErrorDetail(createTranslator("zh"), "configWrite", new Error("Writing ParaDev config values requires the ParaDev desktop application."))
    ).toBe("构建设置保存失败：此操作需要使用 ParaDev 桌面应用。");
    expect(buildActionErrorDetail(createTranslator("zh"), "runGame", "Steam is unavailable.")).toBe("HOI4 启动失败：Steam is unavailable.");
  });

  it("keeps SDK-backed config read and write failures visible", () => {
    const source = readFileSync(new URL("./BuildPage.tsx", import.meta.url), "utf-8");

    expect(source).not.toContain(".catch(() => undefined)");
    expect(source).toContain('buildActionErrorDetail(t, "configRead", error)');
    expect(source).toContain('buildActionErrorDetail(t, "configWrite", error)');
  });
});

function runningBuildRecord(projectOption: ProjectOption, target: BuildTarget | null, runId: string): BuildRunRecord {
  return {
    mode: "cached",
    progress: null,
    projectId: projectOption.projectId || projectOption.id,
    projectRoot: projectOption.path,
    runId,
    startedAtMs: 1_000,
    state: "running",
    target
  };
}

function browserWithSecondFamily(): ProjectBrowserPayload {
  return {
    ...familyOnlyBrowser,
    families: [
      ...familyOnlyBrowser.families,
      {
        family: "focus_tree",
        id: "focus-tree",
        item_count: 3,
        layouts: ["canonical"],
        source_count: 12,
        title: "National Focuses"
      }
    ]
  };
}

function buildStartButtonTags(markup: string): string[] {
  return markup.match(/<button[^>]*data-paradev-operation-id="build.start"[^>]*>/g) ?? [];
}

function runGameButtonTag(markup: string): string {
  return markup.match(/<button class="toolbar-button success"[^>]*>/)?.[0] ?? "";
}

function formatExpectedZhTimestamp(timestampMs: number): string {
  const date = new Date(timestampMs);
  return [
    `${date.getFullYear()}年${pad2(date.getMonth() + 1)}月${pad2(date.getDate())}日`,
    `${pad2(date.getHours())}:${pad2(date.getMinutes())}:${pad2(date.getSeconds())}`
  ].join(" ");
}

function pad2(value: number): string {
  return String(value).padStart(2, "0");
}

function expectBuildLifecycleContractMatchesGenerated(name: "interrupt" | "start" | "status") {
  const contract = buildLifecycleActionContract(name);
  const detail = getFrontendApiActionDetail(contract.operationId);
  expect(contract).toEqual({
    confirmationDefaultConfirmed: detail.execution.confirmation.default_confirmed,
    confirmationRequired: detail.execution.confirmation.required,
    confirmationScope: detail.execution.confirmation.scope,
    confirmationStyle: detail.execution.confirmation.style,
    confirmationTitle: detail.execution.confirmation.title,
    operationId: detail.operation.id,
    payload: detail.action.payload,
    restMethod: detail.bindings?.rest?.method,
    restPath: detail.bindings?.rest?.path,
    sdkCall: detail.bindings?.sdk?.call,
    summary: detail.action.summary
  });
}
