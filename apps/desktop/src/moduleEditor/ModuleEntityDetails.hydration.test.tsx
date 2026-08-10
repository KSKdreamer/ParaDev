/** @vitest-environment jsdom */

import {
  act,
  Profiler,
  StrictMode,
  useCallback,
  useState
} from "react";
import {
  createRoot,
  type Root,
  type RootOptions
} from "react-dom/client";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { createTranslator } from "../i18n";
import type {
  PlanProjectLocalizationUpdateRequest,
  ProjectBrowserPayload,
  ProjectLocalizationWorkspace,
  ProjectLocalizationWorkspaceRequest
} from "../types";
import { buildModuleEntities } from "./model";
import { ModuleEntityDetails } from "./ModuleEntityDetails";

const serviceMocks = vi.hoisted(() => ({
  planProjectLocalizationUpdate: vi.fn(),
  readBinarySource: vi.fn(),
  readProjectLocalizationWorkspace: vi.fn(),
  readTextSource: vi.fn()
}));

vi.mock("../services/paradev", async (importOriginal) => ({
  ...(await importOriginal<typeof import("../services/paradev")>()),
  planProjectLocalizationUpdate: serviceMocks.planProjectLocalizationUpdate,
  readBinarySource: serviceMocks.readBinarySource,
  readProjectLocalizationWorkspace: serviceMocks.readProjectLocalizationWorkspace,
  readTextSource: serviceMocks.readTextSource
}));

vi.mock("./SourceCodeEditor", () => ({
  SourceCodeEditor: ({ value }: { value: string }) => (
    <textarea aria-label="mock source editor" readOnly value={value} />
  )
}));

vi.mock("./ImageDraftEditor", () => ({
  ImageDraftEditor: () => <div>mock image editor</div>
}));

const mountedRoots: Array<{ container: HTMLDivElement; root: Root }> = [];
const projectRoot = "/workspace/PIHC3";
const moduleRoot =
  `${projectRoot}/src/modules/technology/TECHNOLOGY_FIREARM_I - 早期火器 I`;
const definitionPath = `${moduleRoot}/def.txt`;
const definitionRelativePath =
  "src/modules/technology/TECHNOLOGY_FIREARM_I - 早期火器 I/def.txt";
const localizationPath = `${moduleRoot}/main.loc`;
const descriptionLocalizationPath = `${moduleRoot}/description.loc`;
const metadataPath = `${moduleRoot}/meta.yaml`;

beforeEach(() => {
  (
    globalThis as typeof globalThis & {
      IS_REACT_ACT_ENVIRONMENT: boolean;
    }
  ).IS_REACT_ACT_ENVIRONMENT = true;
  serviceMocks.readBinarySource.mockReset();
  serviceMocks.readBinarySource.mockImplementation(
    () => new Promise(() => undefined)
  );
  serviceMocks.readProjectLocalizationWorkspace.mockReset();
  serviceMocks.readProjectLocalizationWorkspace.mockImplementation(
    async (request: ProjectLocalizationWorkspaceRequest) =>
      localizationWorkspace(request)
  );
  serviceMocks.planProjectLocalizationUpdate.mockReset();
  serviceMocks.planProjectLocalizationUpdate.mockImplementation(
    async (request: PlanProjectLocalizationUpdateRequest) =>
      localizationUpdatePlan(request)
  );
  serviceMocks.readTextSource.mockReset();
});

afterEach(() => {
  for (const mounted of mountedRoots.splice(0)) {
    act(() => mounted.root.unmount());
    mounted.container.remove();
  }
  vi.restoreAllMocks();
});

describe("ModuleEntityDetails source hydration", () => {
  it("does not read a family-declared image target before it exists", async () => {
    serviceMocks.readTextSource.mockImplementation(
      () => new Promise(() => undefined)
    );
    const icon = source("preview", "icon.png");
    const [entity] = buildModuleEntities(
      {
        ...technologyBrowser,
        items: [
          {
            ...technologyBrowser.items[0],
            source_count: technologyBrowser.items[0].source_count - 1,
            sources: technologyBrowser.items[0].sources.filter(
              (item) => item.relative_path !== icon.relative_path
            ),
            image_targets: [{ ...icon, exists: false }]
          }
        ]
      },
      "technologies"
    );
    const mounted = createMountedRoot();

    act(() => {
      mounted.root.render(
        details(entity, false, icon.relative_path)
      );
    });
    await flushAsyncWork();

    expect(serviceMocks.readBinarySource).not.toHaveBeenCalled();
    expect(mounted.container.textContent).toContain("icon.png");
    expect(mounted.container.textContent).not.toContain(
      "目前无法创建图片"
    );
  });

  it("keeps the real Technology selection stable under StrictMode", async () => {
    const uncaughtErrors: unknown[] = [];
    serviceMocks.readTextSource.mockImplementation(
      async (_projectRoot: string, sourcePath: string) =>
        sourcePath === localizationPath
          ? "[en.TECHNOLOGY_FIREARM_I]\nEarly Firearm I\n"
          : sourcePath === metadataPath
            ? "title: 早期火器 I\n"
            : "technologies = { TECHNOLOGY_FIREARM_I = {} }\n"
    );
    const entity = buildModuleEntities(technologyBrowser, "technologies")[0];
    const onActiveSourcePathChange = vi.fn();
    const mounted = createMountedRoot({
      onUncaughtError: (error) => uncaughtErrors.push(error)
    });
    let commitCount = 0;
    const onRender = () => {
      commitCount += 1;
    };
    const selection = () => (
      <Profiler id="firearm-details" onRender={onRender}>
        <StrictMode>
          <div key={entity.id}>
            {details(
              { ...entity },
              false,
              definitionRelativePath,
              onActiveSourcePathChange
            )}
          </div>
        </StrictMode>
      </Profiler>
    );

    act(() => {
      mounted.root.render(
        <Profiler id="firearm-details" onRender={onRender}>
          <StrictMode>
            <div key="loading">{details(null, true)}</div>
          </StrictMode>
        </Profiler>
      );
    });
    act(() => {
      mounted.root.render(selection());
    });
    await flushAsyncWork();

    const commitsAfterSelection = commitCount;
    const activeSourceCallsAfterSelection =
      onActiveSourcePathChange.mock.calls.length;
    const parentRerenders = 4;
    for (let rerender = 0; rerender < parentRerenders; rerender += 1) {
      act(() => {
        mounted.root.render(selection());
      });
      await flushAsyncWork();
    }

    expect(uncaughtErrors).toEqual([]);
    expect(commitCount - commitsAfterSelection).toBe(parentRerenders);
    expect(onActiveSourcePathChange).toHaveBeenCalledTimes(
      activeSourceCallsAfterSelection
    );
    expect(serviceMocks.readTextSource).toHaveBeenCalledTimes(3);
    expect(serviceMocks.readTextSource).toHaveBeenCalledWith(
      projectRoot,
      definitionPath,
      "PIHC3"
    );
    expect(mounted.container.textContent).toContain(
      "TECHNOLOGY_FIREARM_I"
    );
    expect(mounted.container.textContent).not.toContain(
      "ParaDev 需要恢复"
    );
  });

  it("writes the Name field through the Registry-owned localization key", async () => {
    serviceMocks.readTextSource.mockImplementation(
      async (_projectRoot: string, sourcePath: string) =>
        sourcePath === localizationPath
          ? "[en.TECHNOLOGY_FIREARM_I]\nEarly Firearm I\n\n[zh.TECHNOLOGY_FIREARM_I]\n早期火器 I\n"
          : sourcePath === metadataPath
            ? "collection: TECHNOLOGY_INFANTRY\n"
            : ""
    );
    const entity = buildModuleEntities(technologyBrowser, "technologies")[0];
    const onInfoDraft = vi.fn();
    const onTextDraft = vi.fn();
    const mounted = createMountedRoot();
    function NameHarness() {
      const [current, setCurrent] = useState(entity);
      return (
        <ModuleEntityDetails
          activeDiagramNodeId=""
          applyBusy={false}
          applyError=""
          canApply={false}
          entity={current}
          locale="zh"
          onApply={() => undefined}
          onImageDraft={() => undefined}
          onInfoDraft={(entityId, info) => {
            onInfoDraft(entityId, info);
            setCurrent((row) => ({
              ...row,
              title: info.title ?? row.title,
              drafts: { ...row.drafts, info }
            }));
          }}
          onRefresh={() => undefined}
          onRestore={() => undefined}
          onTextDraft={onTextDraft}
          openTarget="finder"
          projectId="PIHC3"
          projectRoot={projectRoot}
          sourceReloadKey={0}
          t={createTranslator("zh")}
          theme="light"
        />
      );
    }

    act(() => {
      mounted.root.render(<NameHarness />);
    });
    await flushAsyncWork();

    const inputs = mounted.container.querySelectorAll<HTMLInputElement>(
      ".entity-info-field input"
    );
    const nameInput = inputs[1];
    expect(nameInput).toBeDefined();
    setInputValue(nameInput, "新火器");
    act(() => {
      nameInput.dispatchEvent(new FocusEvent("focusout", { bubbles: true }));
    });
    await flushAsyncWork();

    expect(onInfoDraft).toHaveBeenCalledWith(entity.id, {
      objectId: "TECHNOLOGY_FIREARM_I",
      title: "新火器"
    });
    expect(onTextDraft).toHaveBeenCalledWith(
      entity.id,
      "loc",
      expect.stringContaining("[zh.TECHNOLOGY_FIREARM_I]\n新火器")
    );
    expect(onTextDraft).not.toHaveBeenCalledWith(
      entity.id,
      "meta",
      expect.any(String)
    );
  });

  it("opens the same localization table for a collection source unit", async () => {
    const collectionId = "DECISION_CATEGORY_TEST";
    const collectionRoot = `${projectRoot}/src/collections/decision/${collectionId} - 测试分类`;
    const collectionLocalizationPath = `${collectionRoot}/main.loc`;
    const [moduleEntity] = buildModuleEntities(technologyBrowser, "technologies");
    const entity: TechnologyEntity = {
      ...moduleEntity,
      id: `collection:decision/${collectionId}`,
      kind: "collection",
      familyId: "decisions",
      family: "decision",
      moduleId: undefined,
      collectionId,
      objectId: collectionId,
      title: "测试分类",
      titleKeys: [collectionId],
      root: collectionRoot,
      relativeRoot: `src/collections/decision/${collectionId} - 测试分类`,
      sourceCount: 1,
      sourceSlots: [{
        slot: "loc",
        name: "main.loc",
        path: collectionLocalizationPath,
        relative_path: `src/collections/decision/${collectionId} - 测试分类/main.loc`,
        extension: "loc",
        draftKey: "loc",
        editorKind: "localization"
      }],
      previewSource: undefined
    };
    serviceMocks.readTextSource.mockResolvedValue(
      `[en.${collectionId}]\nTest category\n\n[zh.${collectionId}]\n测试分类\n`
    );
    serviceMocks.readProjectLocalizationWorkspace.mockImplementation(
      async (request: ProjectLocalizationWorkspaceRequest) =>
        localizationWorkspace(request, "Test category", "测试分类")
    );
    const mounted = createMountedRoot();

    act(() => {
      mounted.root.render(details(entity, false));
    });
    await flushAsyncWork();

    expect(serviceMocks.readProjectLocalizationWorkspace).toHaveBeenCalledWith(
      expect.objectContaining({
        projectId: "PIHC3",
        projectRoot,
        targetKind: "collection",
        targetId: collectionId,
        family: "decision"
      })
    );
    expect(mounted.container.textContent).toContain("Test category");
    expect(mounted.container.textContent).toContain("测试分类");
  });

  it("recovers after a planner error and keeps multi-file localization edits on their owning source", async () => {
    const descriptionSource = source("loc", "description.loc");
    const browser: ProjectBrowserPayload = {
      ...technologyBrowser,
      items: [{
        ...technologyBrowser.items[0],
        source_count: technologyBrowser.items[0].source_count + 1,
        sources: [
          ...technologyBrowser.items[0].sources,
          descriptionSource
        ]
      }],
      families: [{
        ...technologyBrowser.families[0],
        source_count: technologyBrowser.families[0].source_count + 1
      }]
    };
    serviceMocks.readTextSource.mockImplementation(
      async (_projectRoot: string, sourcePath: string) =>
        sourcePath === localizationPath
          ? "[en.TECHNOLOGY_FIREARM_I]\nEarly Firearm I\n\n[zh.TECHNOLOGY_FIREARM_I]\n早期火器 I\n"
          : sourcePath === descriptionLocalizationPath
            ? "[en.TECHNOLOGY_FIREARM_I_desc]\nOld description\n\n[zh.TECHNOLOGY_FIREARM_I_desc]\n旧描述\n"
            : sourcePath === metadataPath
              ? "collection: TECHNOLOGY_INFANTRY\n"
              : ""
    );
    serviceMocks.readProjectLocalizationWorkspace.mockImplementation(
      async (request: ProjectLocalizationWorkspaceRequest) =>
        multiLocalizationWorkspace(request)
    );
    let plannerAttempts = 0;
    serviceMocks.planProjectLocalizationUpdate.mockImplementation(
      async (request: PlanProjectLocalizationUpdateRequest) => {
        plannerAttempts += 1;
        if (plannerAttempts === 1) {
          throw new Error("temporary localization planner failure");
        }
        const draft = request.drafts?.find(
          (item) => item.sourcePath === descriptionLocalizationPath
        );
        if (!draft || request.operation.op !== "set") {
          throw new Error("missing description localization draft");
        }
        const text = draft.text.replace(
          new RegExp(`(\\[zh\\.${request.operation.key}\\]\\r?\\n)[^\\r\\n]*`),
          `$1${request.operation.value}`
        );
        return {
          schema: "paradev.localization-update-plan.v2" as const,
          project_id: request.projectId,
          target: {
            kind: request.targetKind,
            id: request.targetId,
            family: "technology",
            object_id: "TECHNOLOGY_FIREARM_I"
          },
          source_root: `${request.projectRoot}/src`,
          operation: request.operation,
          changed: true,
          changes: [],
          source_edits: [{
            path: descriptionLocalizationPath,
            text,
            expected_size: draft.text.length,
            expected_mtime_ns: "2"
          }],
          workspace: multiLocalizationWorkspace(request, "新描述")
        };
      }
    );
    const entity = buildModuleEntities(browser, "technologies")[0];
    const ownedDescriptionSource = requiredSource(entity, "description.loc");
    const onTextDraft = vi.fn();
    const mounted = createMountedRoot();

    act(() => {
      mounted.root.render(
        <ModuleEntityDetails
          activeDiagramNodeId=""
          applyBusy={false}
          applyError=""
          canApply={false}
          entity={entity}
          locale="zh"
          onApply={() => undefined}
          onImageDraft={() => undefined}
          onInfoDraft={() => undefined}
          onRefresh={() => undefined}
          onRestore={() => undefined}
          onTextDraft={onTextDraft}
          openTarget="finder"
          projectId="PIHC3"
          projectRoot={projectRoot}
          sourceReloadKey={0}
          t={createTranslator("zh")}
          theme="light"
        />
      );
    });
    await flushAsyncWork();

    const rows = mounted.container.querySelectorAll<HTMLDivElement>(
      ".entity-localization-row:not(.header)"
    );
    const descriptionTextareas = rows[1]?.querySelectorAll<HTMLTextAreaElement>(
      "textarea"
    );
    const englishDescription = descriptionTextareas?.[1];
    const chineseDescription = descriptionTextareas?.[2];
    if (!englishDescription || !chineseDescription) {
      throw new Error("missing multi-file localization description editors");
    }

    setTextareaValue(englishDescription, "First attempt");
    act(() => {
      englishDescription.dispatchEvent(new FocusEvent("focusout", { bubbles: true }));
    });
    await flushAsyncWork();

    expect(mounted.container.textContent).toContain(
      "temporary localization planner failure"
    );
    expect(onTextDraft).not.toHaveBeenCalled();

    setTextareaValue(chineseDescription, "新描述");
    act(() => {
      chineseDescription.dispatchEvent(new FocusEvent("focusout", { bubbles: true }));
    });
    await flushAsyncWork();

    expect(serviceMocks.planProjectLocalizationUpdate).toHaveBeenCalledTimes(2);
    expect(serviceMocks.planProjectLocalizationUpdate).toHaveBeenLastCalledWith(
      expect.objectContaining({
        operation: expect.objectContaining({
          op: "set",
          key: "TECHNOLOGY_FIREARM_I_desc",
          language: "l_simp_chinese",
          source_path: descriptionLocalizationPath,
          value: "新描述"
        })
      })
    );
    expect(onTextDraft).toHaveBeenCalledWith(
      entity.id,
      ownedDescriptionSource.draftKey,
      expect.stringContaining("[zh.TECHNOLOGY_FIREARM_I_desc]\n新描述")
    );
    expect(mounted.container.textContent).not.toContain(
      "temporary localization planner failure"
    );
  });

  it("receives controlled GFX and DDS targets without echoing stale local selection", async () => {
    const uncaughtErrors: unknown[] = [];
    const publishedSources = vi.fn();
    serviceMocks.readTextSource.mockImplementation(
      () => new Promise(() => undefined)
    );
    const firearm = buildModuleEntities(technologyBrowser, "technologies")[0];
    const trombone = technologyVariant(
      firearm,
      "TECHNOLOGY_TROMBONE",
      "Trombone"
    );
    const firearmGfx = requiredSource(firearm, ".gfx");
    const firearmDds = requiredSource(firearm, ".dds");
    const firearmIcon = requiredSource(firearm, "icon.png");
    const tromboneGfx = requiredSource(trombone, ".gfx");
    const mounted = createMountedRoot({
      onUncaughtError: (error) => uncaughtErrors.push(error)
    });
    let commitCount = 0;

    act(() => {
      mounted.root.render(
        <Profiler
          id="controlled-source-details"
          onRender={() => {
            commitCount += 1;
          }}
        >
          <StrictMode>
            <ControlledSourceEchoHarness
              firearm={firearm}
              firearmDdsPath={firearmDds.relative_path}
              firearmGfxPath={firearmGfx.relative_path}
              onPublish={publishedSources}
              trombone={trombone}
              tromboneGfxPath={tromboneGfx.relative_path}
            />
          </StrictMode>
        </Profiler>
      );
    });
    await flushAsyncWork();

    const commitsBeforeExternalTargets = commitCount;
    act(() => {
      requiredElement<HTMLButtonElement>(
        mounted.container,
        '[data-testid="receive-firearm-gfx"]'
      ).click();
    });
    await flushAsyncWork();
    act(() => {
      requiredElement<HTMLButtonElement>(
        mounted.container,
        '[data-testid="receive-firearm-dds"]'
      ).click();
    });
    await flushAsyncWork();

    expect(uncaughtErrors).toEqual([]);
    expect(publishedSources).not.toHaveBeenCalled();
    expect(commitCount - commitsBeforeExternalTargets).toBeGreaterThanOrEqual(4);
    expect(commitCount - commitsBeforeExternalTargets).toBeLessThanOrEqual(6);

    const imageSourcePicker = requiredElement<HTMLSelectElement>(
      mounted.container,
      ".image-source-picker select"
    );
    expect(imageSourcePicker.value).toBe(firearmDds.draftKey);
    act(() => {
      imageSourcePicker.value = firearmIcon.draftKey;
      imageSourcePicker.dispatchEvent(new Event("change", { bubbles: true }));
    });
    await flushAsyncWork();

    expect(publishedSources).toHaveBeenCalledOnce();
    expect(publishedSources).toHaveBeenCalledWith(
      firearm.id,
      firearmIcon.relative_path
    );
    expect(uncaughtErrors).toEqual([]);
  });

  it("explains that image creation is unavailable when Technology has no exact source target", async () => {
    serviceMocks.readTextSource.mockImplementation(
      () => new Promise(() => undefined)
    );
    const technology = buildModuleEntities(
      technologyBrowser,
      "technologies"
    )[0];
    const withoutImageTarget = {
      ...technology,
      sourceSlots: technology.sourceSlots.filter(
        (source) => source.editorKind !== "image"
      )
    };
    const mounted = createMountedRoot();

    act(() => {
      mounted.root.render(details(withoutImageTarget, false));
    });
    await flushAsyncWork();

    const imageTab = [...mounted.container.querySelectorAll<HTMLButtonElement>(
      "button.source-tab"
    )].find((button) => button.textContent === "图片");
    if (!imageTab) {
      throw new Error("missing Image tab");
    }
    act(() => imageTab.click());
    await flushAsyncWork();

    const unavailable = requiredElement<HTMLDivElement>(
      mounted.container,
      ".image-editor-unavailable"
    );
    expect(unavailable.getAttribute("role")).toBe("status");
    expect(unavailable.textContent).toContain(
      "项目 SDK 未为此模块提供由其系列定义的明确目标路径"
    );
    expect(unavailable.textContent).toContain("ParaDev 不会猜测文件名");
    expect(unavailable.textContent).not.toContain(
      "TECHNOLOGY_FIREARM_I.png"
    );
    expect(mounted.container.querySelector(".image-draft-editor")).toBeNull();
  });

  it("hydrates every source in a real six-source Technology row exactly once", async () => {
    const localization = deferred<string>();
    const metadata = deferred<string>();
    serviceMocks.readTextSource.mockImplementation(
      (_projectRoot: string, sourcePath: string) => {
        if (sourcePath === localizationPath) {
          return localization.promise;
        }
        if (sourcePath === metadataPath) {
          return metadata.promise;
        }
        throw new Error(`unexpected source: ${sourcePath}`);
      }
    );
    const entity = buildModuleEntities(technologyBrowser, "technologies")[0];
    const mounted = createMountedRoot();

    act(() => {
      mounted.root.render(details(null, true));
    });
    act(() => {
      mounted.root.render(details(entity, false));
    });
    await flushAsyncWork();

    expect(serviceMocks.readTextSource).toHaveBeenCalledTimes(2);
    expect(serviceMocks.readTextSource).toHaveBeenCalledWith(
      projectRoot,
      localizationPath,
      "PIHC3"
    );
    expect(serviceMocks.readTextSource).toHaveBeenCalledWith(
      projectRoot,
      metadataPath,
      "PIHC3"
    );

    localization.resolve(
      [
        "[en.TECHNOLOGY_FIREARM_I]",
        "Early Firearm I",
        "",
        "[en.TECHNOLOGY_FIREARM_I_desc]",
        "Early Firearm I",
        "",
        "[zh.TECHNOLOGY_FIREARM_I]",
        "早期火器 I",
        "",
        "[zh.TECHNOLOGY_FIREARM_I_desc]",
        "早期火器 I",
        ""
      ].join("\n")
    );
    await flushAsyncWork();

    expect(serviceMocks.readTextSource).toHaveBeenCalledTimes(2);
    expect(mounted.container.textContent).toContain("Early Firearm I");
    expect(mounted.container.textContent).toContain("早期火器 I");
    expect(
      requiredElement<HTMLElement>(
        mounted.container,
        '.entity-localization-row.header span[title="l_english"]'
      ).textContent
    ).toBe("英语");
    expect(
      requiredElement<HTMLElement>(
        mounted.container,
        '.entity-localization-row.header span[title="l_simp_chinese"]'
      ).textContent
    ).toBe("简体中文");

    metadata.resolve("title: 早期火器 I\n");
    await flushAsyncWork();

    expect(serviceMocks.readTextSource).toHaveBeenCalledTimes(2);
    expect(mounted.container.textContent).toContain(
      "TECHNOLOGY_FIREARM_I"
    );
    expect(mounted.container.textContent).not.toContain(
      "ParaDev 需要恢复"
    );
  });

  it("keeps one failed source actionable without retrying it when a sibling resolves", async () => {
    const localization = deferred<string>();
    const metadata = deferred<string>();
    serviceMocks.readTextSource.mockImplementation(
      (_projectRoot: string, sourcePath: string) =>
        sourcePath === localizationPath
          ? localization.promise
          : metadata.promise
    );
    const entity = buildModuleEntities(technologyBrowser, "technologies")[0];
    const mounted = createMountedRoot();

    act(() => {
      mounted.root.render(details(entity, false));
    });
    await flushAsyncWork();

    localization.reject(new Error("main.loc could not be read"));
    await flushAsyncWork();
    expect(mounted.container.textContent).toContain(
      "main.loc could not be read"
    );

    metadata.resolve("title: 早期火器 I\n");
    await flushAsyncWork();

    expect(serviceMocks.readTextSource).toHaveBeenCalledTimes(2);
    expect(mounted.container.textContent).toContain(
      "main.loc could not be read"
    );
  });
});

type TechnologyEntity = ReturnType<typeof buildModuleEntities>[number];

function ControlledSourceEchoHarness({
  firearm,
  firearmDdsPath,
  firearmGfxPath,
  onPublish,
  trombone,
  tromboneGfxPath
}: {
  firearm: TechnologyEntity;
  firearmDdsPath: string;
  firearmGfxPath: string;
  onPublish: (entityId: string, sourcePath: string) => void;
  trombone: TechnologyEntity;
  tromboneGfxPath: string;
}) {
  const [received, setReceived] = useState({
    entity: "trombone" as "firearm" | "trombone",
    sourcePath: tromboneGfxPath
  });
  const handleSourcePathChange = useCallback(
    (entityId: string, sourcePath: string) => {
      onPublish(entityId, sourcePath);
      setReceived((current) =>
        current.sourcePath === sourcePath
          ? current
          : { ...current, sourcePath }
      );
    },
    [onPublish]
  );
  const entity = {
    ...(received.entity === "firearm" ? firearm : trombone)
  };

  return (
    <>
      <button
        data-testid="receive-firearm-gfx"
        onClick={() =>
          setReceived({ entity: "firearm", sourcePath: firearmGfxPath })
        }
        type="button"
      >
        Receive Firearm GFX
      </button>
      <button
        data-testid="receive-firearm-dds"
        onClick={() =>
          setReceived({ entity: "firearm", sourcePath: firearmDdsPath })
        }
        type="button"
      >
        Receive Firearm DDS
      </button>
      {details(
        entity,
        false,
        received.sourcePath,
        handleSourcePathChange
      )}
    </>
  );
}

function details(
  entity: TechnologyEntity | null,
  loading: boolean,
  targetSourcePath = "",
  onActiveSourcePathChange?: (entityId: string, sourcePath: string) => void
) {
  return (
    <ModuleEntityDetails
      activeDiagramNodeId=""
      applyBusy={false}
      applyError=""
      canApply={false}
      entity={entity}
      loading={loading}
      locale="zh"
      onActiveSourcePathChange={onActiveSourcePathChange}
      onApply={() => undefined}
      onImageDraft={() => undefined}
      onInfoDraft={() => undefined}
      onRefresh={() => undefined}
      onRestore={() => undefined}
      onTextDraft={() => undefined}
      openTarget="finder"
      projectId="PIHC3"
      projectRoot={projectRoot}
      sourceReloadKey={0}
      targetSourcePath={targetSourcePath}
      t={createTranslator("zh")}
      theme="light"
    />
  );
}

function requiredElement<T extends Element>(
  container: ParentNode,
  selector: string
): T {
  const element = container.querySelector<T>(selector);
  if (!element) {
    throw new Error(`missing element: ${selector}`);
  }
  return element;
}

function setInputValue(input: HTMLInputElement, value: string): void {
  const setter = Object.getOwnPropertyDescriptor(
    HTMLInputElement.prototype,
    "value"
  )?.set;
  if (!setter) {
    throw new Error("Missing HTMLInputElement value setter.");
  }
  act(() => {
    setter.call(input, value);
    input.dispatchEvent(new Event("input", { bubbles: true }));
  });
}

function setTextareaValue(textarea: HTMLTextAreaElement, value: string): void {
  const setter = Object.getOwnPropertyDescriptor(
    HTMLTextAreaElement.prototype,
    "value"
  )?.set;
  if (!setter) {
    throw new Error("Missing HTMLTextAreaElement value setter.");
  }
  act(() => {
    setter.call(textarea, value);
    textarea.dispatchEvent(new Event("input", { bubbles: true }));
  });
}

function requiredSource(
  entity: TechnologyEntity,
  pathSuffix: string
) {
  const source = entity.sourceSlots.find(
    (item) =>
      item.path.endsWith(pathSuffix)
      || item.relative_path.endsWith(pathSuffix)
  );
  if (!source) {
    throw new Error(`missing source ending in ${pathSuffix}`);
  }
  return source;
}

function technologyVariant(
  entity: TechnologyEntity,
  objectId: string,
  title: string
): TechnologyEntity {
  const replaceIdentity = (value: string) =>
    value
      .replaceAll(entity.objectId, objectId)
      .replaceAll(entity.title, title);
  const sourceSlots = entity.sourceSlots.map((source) => ({
    ...source,
    draftKey: replaceIdentity(source.draftKey),
    name: replaceIdentity(source.name),
    path: replaceIdentity(source.path),
    relative_path: replaceIdentity(source.relative_path)
  }));
  return {
    ...entity,
    id: `module:technology/${objectId}`,
    moduleId: `technology/${objectId}`,
    objectId,
    relativeRoot: replaceIdentity(entity.relativeRoot),
    root: replaceIdentity(entity.root),
    sourceSlots,
    title
  };
}

function createMountedRoot(options?: RootOptions) {
  const container = document.createElement("div");
  document.body.append(container);
  const root = createRoot(container, options);
  const mounted = { container, root };
  mountedRoots.push(mounted);
  return mounted;
}

async function flushAsyncWork(): Promise<void> {
  await act(async () => {
    await Promise.resolve();
    await Promise.resolve();
    await Promise.resolve();
  });
}

function deferred<T>() {
  let resolve!: (value: T | PromiseLike<T>) => void;
  let reject!: (reason?: unknown) => void;
  const promise = new Promise<T>((resolvePromise, rejectPromise) => {
    resolve = resolvePromise;
    reject = rejectPromise;
  });
  return { promise, reject, resolve };
}

function localizationWorkspace(
  request: ProjectLocalizationWorkspaceRequest,
  title = "Early Firearm I",
  chineseTitle = "早期火器 I"
): ProjectLocalizationWorkspace {
  const objectId = request.targetKind === "module"
    ? request.targetId.split("/").at(-1) ?? request.targetId
    : request.targetId;
  const family = request.family
    ?? (request.targetKind === "module" ? request.targetId.split("/")[0] : undefined)
    ?? "technology";
  const sourcePath = request.drafts?.[0]?.sourcePath ?? localizationPath;
  return {
    schema: "paradev.localization-workspace.v2",
    project_id: request.projectId,
    target: {
      kind: request.targetKind,
      id: request.targetId,
      family,
      object_id: objectId
    },
    source_root: `${request.projectRoot}/src`,
    languages: ["l_english", "l_simp_chinese"],
    rows: [
      {
        key: objectId,
        values: {
          l_english: {
            text: title,
            source_path: sourcePath,
            relative_path: sourcePath,
            slot: "loc",
            occurrence: 0
          },
          l_simp_chinese: {
            text: chineseTitle,
            source_path: sourcePath,
            relative_path: sourcePath,
            slot: "loc",
            occurrence: 0
          }
        }
      }
    ],
    sources: [
      {
        path: sourcePath,
        relative_path: sourcePath,
        unit_relative_path: "main.loc",
        slot: "loc",
        source_format: "ini",
        languages: ["l_english", "l_simp_chinese"],
        size: request.drafts?.[0]?.text.length ?? 0,
        mtime_ns: "1"
      }
    ],
    coverage: { truncated: false, shown_rows: 1, total_rows: 1 }
  };
}

function multiLocalizationWorkspace(
  request: ProjectLocalizationWorkspaceRequest,
  chineseDescription = "旧描述"
): ProjectLocalizationWorkspace {
  const titleDraft = request.drafts?.find(
    (item) => item.sourcePath === localizationPath
  );
  const descriptionDraft = request.drafts?.find(
    (item) => item.sourcePath === descriptionLocalizationPath
  );
  return {
    schema: "paradev.localization-workspace.v2",
    project_id: request.projectId,
    target: {
      kind: request.targetKind,
      id: request.targetId,
      family: request.family ?? "technology",
      object_id: "TECHNOLOGY_FIREARM_I"
    },
    source_root: `${request.projectRoot}/src`,
    languages: ["l_english", "l_simp_chinese"],
    rows: [
      {
        key: "TECHNOLOGY_FIREARM_I",
        values: {
          l_english: {
            text: "Early Firearm I",
            source_path: localizationPath,
            relative_path: localizationPath,
            slot: "loc",
            occurrence: 0
          },
          l_simp_chinese: {
            text: "早期火器 I",
            source_path: localizationPath,
            relative_path: localizationPath,
            slot: "loc",
            occurrence: 0
          }
        }
      },
      {
        key: "TECHNOLOGY_FIREARM_I_desc",
        values: {
          l_english: {
            text: "Old description",
            source_path: descriptionLocalizationPath,
            relative_path: descriptionLocalizationPath,
            slot: "loc",
            occurrence: 0
          },
          l_simp_chinese: {
            text: chineseDescription,
            source_path: descriptionLocalizationPath,
            relative_path: descriptionLocalizationPath,
            slot: "loc",
            occurrence: 0
          }
        }
      }
    ],
    sources: [
      {
        path: localizationPath,
        relative_path: localizationPath,
        unit_relative_path: "main.loc",
        slot: "loc",
        source_format: "ini",
        languages: ["l_english", "l_simp_chinese"],
        size: titleDraft?.text.length ?? 0,
        mtime_ns: "1"
      },
      {
        path: descriptionLocalizationPath,
        relative_path: descriptionLocalizationPath,
        unit_relative_path: "description.loc",
        slot: "loc",
        source_format: "ini",
        languages: ["l_english", "l_simp_chinese"],
        size: descriptionDraft?.text.length ?? 0,
        mtime_ns: "2"
      }
    ],
    coverage: { truncated: false, shown_rows: 2, total_rows: 2 }
  };
}

function localizationUpdatePlan(request: PlanProjectLocalizationUpdateRequest) {
  const draft = request.drafts?.[0];
  const operation = request.operation;
  const value = operation.op === "set" ? operation.value : "早期火器 I";
  const sourceText = draft?.text ?? "";
  const text = operation.op === "set"
    ? sourceText.replace(
        new RegExp(`(\\[zh\\.${operation.key}\\]\\r?\\n)[^\\r\\n]*`),
        `$1${operation.value}`
      )
    : sourceText;
  const workspace = localizationWorkspace(request, "Early Firearm I", value);
  return {
    schema: "paradev.localization-update-plan.v2" as const,
    project_id: request.projectId,
    target: workspace.target,
    source_root: workspace.source_root,
    operation,
    changed: text !== sourceText,
    changes: [],
    source_edits: draft
      ? [{ path: draft.sourcePath, text, expected_size: sourceText.length, expected_mtime_ns: "1" }]
      : [],
    workspace
  };
}

const technologyBrowser: ProjectBrowserPayload = {
  schema: "paradev.sdk.project-browser.v1",
  project_id: "PIHC3",
  title: "The Pony In The High Castle",
  profile: "hoi4",
  root: projectRoot,
  filters: {},
  items: [
    {
      id: "module:technology/TECHNOLOGY_FIREARM_I",
      kind: "module",
      layout: "canonical",
      family_id: "technologies",
      family: "technology",
      object_id: "TECHNOLOGY_FIREARM_I",
      module_id: "technology/TECHNOLOGY_FIREARM_I",
      title: "早期火器 I",
      localized_titles: {
        l_english: "Early Firearm I",
        l_simp_chinese: "早期火器 I"
      },
      title_keys: ["TECHNOLOGY_FIREARM_I"],
      root: moduleRoot,
      relative_root:
        "src/modules/technology/TECHNOLOGY_FIREARM_I - 早期火器 I",
      source_count: 6,
      sources: [
        source(
          "compiled_assets",
          "gfx/interface/technologies/TECHNOLOGY_FIREARM_I_medium.dds"
        ),
        source(
          "compiled_assets",
          "interface/technologies/TECHNOLOGY_FIREARM_I.gfx"
        ),
        source("def", "def.txt"),
        source("loc", "main.loc"),
        source("meta", "meta.yaml"),
        source("preview", "icon.png")
      ]
    }
  ],
  families: [
    {
      id: "technologies",
      family: "technology",
      title: "Technologies",
      item_count: 1,
      source_count: 6,
      layouts: ["canonical"]
    }
  ],
  diagnostics: []
};

function source(slot: string, relativeToModule: string) {
  const name = relativeToModule.split("/").at(-1) ?? relativeToModule;
  const relativePath =
    `src/modules/technology/TECHNOLOGY_FIREARM_I - 早期火器 I/${relativeToModule}`;
  return {
    slot,
    name,
    path: `${projectRoot}/${relativePath}`,
    relative_path: relativePath,
    extension: name.split(".").at(-1) ?? ""
  };
}
