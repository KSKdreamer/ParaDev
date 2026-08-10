/** @vitest-environment jsdom */

import { act, useState } from "react";
import { createRoot, type Root } from "react-dom/client";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import type { BuildTarget } from "../buildPage/buildPageModel";
import { createTranslator } from "../i18n";
import type {
  ModuleDuplicatePayload,
  ModuleRemovePayload,
  ProjectCatalogQueryPayload,
  ProjectCatalogQueryRequest,
  ProjectCatalogRow,
} from "../services/paradev";
import type {
  CatalogMutationPayload,
  CatalogMutationResult,
  DraftApplyPayload,
  ModuleDraftPayload,
  ProjectBrowserPayload,
  ProjectTemplatesPayload,
  WorkspaceModuleSelectionTarget,
} from "../types";
import type { ModuleEntity } from "./model";

const mocks = vi.hoisted(() => ({
  applyProjectDraft: vi.fn(),
  createModuleDraft: vi.fn(),
  detailProps: [] as Array<Record<string, unknown>>,
  duplicateProps: [] as Array<Record<string, unknown>>,
  listProps: [] as Array<Record<string, unknown>>,
  loadProjectCatalogStatus: vi.fn(),
  planProjectSourceFormUpdates: vi.fn(),
  queryProjectCatalog: vi.fn(),
  removeModule: vi.fn(),
  renameModule: vi.fn(),
  refreshProjectCatalog: vi.fn(),
  sourceDraftRecoveryPathFromError: vi.fn(),
}));

vi.mock("../services/paradev", () => ({
  applyProjectDraft: mocks.applyProjectDraft,
  createModuleDraft: mocks.createModuleDraft,
  hasDesktopBackend: () => true,
  loadProjectCatalogStatus: mocks.loadProjectCatalogStatus,
  planProjectSourceFormUpdates: mocks.planProjectSourceFormUpdates,
  projectCatalogReadinessFromError: () => null,
  queryProjectCatalog: mocks.queryProjectCatalog,
  readTextSource: vi.fn(),
  removeModule: mocks.removeModule,
  refreshProjectCatalog: mocks.refreshProjectCatalog,
  renameModule: mocks.renameModule,
  sourceDraftRecoveryPathFromError: mocks.sourceDraftRecoveryPathFromError,
}));

vi.mock("../diagramEditor/ProjectDiagramView", () => ({
  ProjectDiagramView: () => <div data-testid="project-diagram" />,
}));

vi.mock("./ModuleEntityList", () => ({
  ModuleEntityList: (props: Record<string, unknown>) => {
    mocks.listProps.push(props);
    return <div data-testid="module-entity-list" />;
  },
}));

vi.mock("./ModuleEntityDetails", () => ({
  ModuleEntityDetails: (props: Record<string, unknown>) => {
    mocks.detailProps.push(props);
    return <div data-testid="module-entity-details" />;
  },
}));

vi.mock("./ModuleDuplicateDialog", () => ({
  ModuleDuplicateDialog: (props: Record<string, unknown>) => {
    mocks.duplicateProps.push(props);
    return <div data-testid="module-duplicate-dialog" />;
  },
}));

import { ModuleEditor } from "./ModuleEditor";
import {
  ModuleEditorSessionStore,
  moduleEditorSessionKey,
} from "./editorSessionStore";

const PROJECT_ROOT = "/workspace/projects/PIHC3";

const browser: ProjectBrowserPayload = {
  schema: "paradev.sdk.project-browser.v1",
  project_id: "PIHC3",
  title: "The Pony In The High Castle",
  root: PROJECT_ROOT,
  profile: "hoi4",
  filters: {},
  diagnostics: [],
  families: [
    {
      id: "scripted-effects",
      family: "scripted_effect",
      title: "Scripted effects",
      item_count: 8_279,
      source_count: 8_279,
      layouts: ["canonical"],
    },
  ],
  items: [],
};

const assetAuthoringBrowser: ProjectBrowserPayload = {
  ...browser,
  families: browser.families.map((family) => ({
    ...family,
    resource_slots: [
      {
        name: "assets",
        match: "*.mesh",
        required: false,
        many: true,
        regex: false,
        kind: "copy",
        shared: false,
        authoring_path: "{filename}",
      },
    ],
  })),
};

const entityAggregateBrowser: ProjectBrowserPayload = {
  ...browser,
  families: [
    {
      id: "entity",
      family: "entity",
      title: "Entities",
      item_count: 1,
      source_count: 2,
      layouts: ["canonical"],
    },
  ],
  items: [
    {
      id: "module:entity/HOI4DEV_ENTITIES",
      kind: "module",
      layout: "canonical",
      family_id: "entity",
      family: "entity",
      object_id: "HOI4DEV_ENTITIES",
      module_id: "entity/HOI4DEV_ENTITIES",
      title: "Shared entities",
      root: `${PROJECT_ROOT}/src/modules/entity/HOI4DEV_ENTITIES`,
      relative_root: "src/modules/entity/HOI4DEV_ENTITIES",
      source_count: 2,
      sources: [
        {
          slot: "pdx",
          name: "mesh.gfx",
          path: `${PROJECT_ROOT}/src/modules/entity/HOI4DEV_ENTITIES/gfx/models/viento/air/mesh.gfx`,
          relative_path:
            "src/modules/entity/HOI4DEV_ENTITIES/gfx/models/viento/air/mesh.gfx",
          extension: "gfx",
        },
        {
          slot: "assets",
          name: "mesh.mesh",
          path: `${PROJECT_ROOT}/src/modules/entity/HOI4DEV_ENTITIES/gfx/models/viento/air/mesh.mesh`,
          relative_path:
            "src/modules/entity/HOI4DEV_ENTITIES/gfx/models/viento/air/mesh.mesh",
          extension: "mesh",
          slot_kinds: ["copy"],
        },
      ],
    },
  ],
};

const technologySourceBrowser: ProjectBrowserPayload = {
  ...browser,
  families: [
    {
      id: "technologies",
      family: "technology",
      title: "Technologies",
      item_count: 300,
      source_count: 600,
      layouts: ["canonical"],
    },
  ],
  items: [
    {
      id: "module:technology/TECHNOLOGY_FIREARM_I",
      kind: "module",
      layout: "canonical",
      family_id: "technologies",
      family: "technology",
      object_id: "TECHNOLOGY_FIREARM_I",
      module_id: "technology/TECHNOLOGY_FIREARM_I",
      title: "Firearm I",
      root: `${PROJECT_ROOT}/src/modules/technology/TECHNOLOGY_FIREARM_I`,
      relative_root: "src/modules/technology/TECHNOLOGY_FIREARM_I",
      source_count: 1,
      sources: [
        {
          slot: "pdx",
          name: "def.pdx",
          path: `${PROJECT_ROOT}/src/modules/technology/TECHNOLOGY_FIREARM_I/def.pdx`,
          relative_path: "src/modules/technology/TECHNOLOGY_FIREARM_I/def.pdx",
          extension: "pdx",
        },
      ],
    },
  ],
};

const catalogTemplates: ProjectTemplatesPayload = {
  schema: "paradev.sdk.templates.v1",
  project_id: "PIHC3",
  profile: "hoi4",
  templates: [
    {
      id: "pihc3:scripted_effect/basic",
      title: "Scripted effect",
      family: "scripted_effect",
      source: "project",
      args: {
        title: { required: false, default: "New effect", advanced: false },
      },
      files: ["meta.yaml", "def.pdx"],
    },
  ],
};

type Deferred<Value> = {
  promise: Promise<Value>;
  resolve: (value: Value) => void;
  reject: (reason: unknown) => void;
};

type PendingCatalogQuery = {
  request: ProjectCatalogQueryRequest;
  response: Deferred<ProjectCatalogQueryPayload>;
};

type CapturedListProps = {
  allEntities: ModuleEntity[];
  catalogMissing: boolean;
  catalogPreparing: boolean;
  catalogSearch: boolean;
  entities: ModuleEntity[];
  hydratingEntityId: string;
  loadedCount: number;
  loadError: string;
  onCreate: () => boolean | Promise<boolean>;
  onLoadMore: () => void | Promise<void>;
  onPrepareCatalog: () => Promise<void>;
  onQueryChange: (value: string) => void;
  onRemoveSelected: () => void;
  onRetryLoad: () => void;
  onSelect: (entityId: string) => void;
  query: string;
  totalCount: number;
};

type CapturedDetailProps = {
  applyBusy: boolean;
  applyError: string;
  canApply: boolean;
  canDuplicate: boolean;
  entity: ModuleEntity | null;
  loading: boolean;
  onApply: (entityId: string) => void | Promise<void>;
  onAssetDrafts: (
    entityId: string,
    assets: NonNullable<ModuleEntity["drafts"]["assets"]>,
  ) => void;
  onBuildAffected?: () => void;
  onBuildModule?: () => void;
  onImageDraft: (
    entityId: string,
    image: NonNullable<ModuleEntity["drafts"]["image"]>,
  ) => void;
  onInfoDraft: (
    entityId: string,
    info: { objectId?: string; title?: string },
  ) => void;
  onGuidedTextDraft: (
    entityId: string,
    slot: string,
    change: {
      baseText: string;
      controlId: string;
      text: string;
      value: string | number | boolean;
    },
  ) => void;
  onDuplicate: () => void;
  onRestore: (entityId: string) => void;
  onTextDraft: (entityId: string, slot: string, value: string) => void;
  sourceReloadKey: number;
};

type CapturedDuplicateProps = {
  moduleId: string;
  objectId: string;
  onApplied: (payload: ModuleDuplicatePayload) => Promise<void>;
  onClose: () => void;
  projectRoot: string;
  sourceRoot?: string;
  title: string;
};

const mountedRoots: Array<{ container: HTMLDivElement; root: Root }> = [];
let latestWorkspaceSelection: WorkspaceModuleSelectionTarget | null = null;
let setWorkspaceSelection:
  ((target: WorkspaceModuleSelectionTarget | null) => void) | null = null;

beforeEach(() => {
  vi.useFakeTimers();
  mocks.detailProps.length = 0;
  mocks.duplicateProps.length = 0;
  mocks.listProps.length = 0;
  mocks.createModuleDraft.mockReset();
  mocks.applyProjectDraft.mockReset();
  mocks.loadProjectCatalogStatus.mockReset();
  mocks.loadProjectCatalogStatus.mockResolvedValue(catalogStatus("present"));
  mocks.queryProjectCatalog.mockReset();
  mocks.planProjectSourceFormUpdates.mockReset();
  mocks.removeModule.mockReset();
  mocks.renameModule.mockReset();
  mocks.refreshProjectCatalog.mockReset();
  mocks.refreshProjectCatalog.mockResolvedValue({ ok: true });
  mocks.sourceDraftRecoveryPathFromError.mockReset();
  mocks.sourceDraftRecoveryPathFromError.mockReturnValue(null);
  latestWorkspaceSelection = null;
  setWorkspaceSelection = null;
  (
    globalThis as typeof globalThis & { IS_REACT_ACT_ENVIRONMENT: boolean }
  ).IS_REACT_ACT_ENVIRONMENT = true;
});

afterEach(() => {
  for (const mounted of mountedRoots.splice(0)) {
    act(() => mounted.root.unmount());
    mounted.container.remove();
  }
  vi.restoreAllMocks();
  vi.useRealTimers();
});

describe("ModuleEditor Catalog lifecycle", () => {
  it("loads a lightweight first page and hydrates only the selected row", async () => {
    const queries = installControllableCatalogQueries();
    const onBuildTarget = vi.fn<(target: BuildTarget) => void>();
    renderEditor({ onBuildTarget });

    expect(queries).toHaveLength(1);
    expect(queries[0]?.request).toEqual({
      projectRoot: PROJECT_ROOT,
      entity: "module",
      tag: "scripted_effect",
      limit: 100,
      offset: 0,
      includeData: false,
    });

    const alpha = catalogRow("ALPHA", "hash-alpha");
    await resolveQuery(
      queries[0],
      catalogPayload([alpha], {
        filteredCount: 2,
        hasMore: true,
        nextOffset: 1,
      }),
    );

    expect(queries).toHaveLength(2);
    expect(queries[1]?.request).toEqual({
      projectRoot: PROJECT_ROOT,
      targetId: "module:hash-alpha",
      limit: 1,
      offset: 0,
      includeData: true,
    });

    await resolveQuery(
      queries[1],
      catalogPayload([hydratedCatalogRow("ALPHA", "hash-alpha")], {
        includeData: true,
      }),
    );

    expect(queries).toHaveLength(2);
    expect(latestListProps().allEntities.map((entity) => entity.id)).toEqual([
      "module:scripted_effect/ALPHA",
    ]);
    expect(latestDetailProps()).toMatchObject({
      entity: {
        id: "module:scripted_effect/ALPHA",
        title: "Alpha",
      },
      loading: false,
    });
    act(() => latestDetailProps().onBuildModule?.());
    act(() => latestDetailProps().onBuildAffected?.());
    expect(onBuildTarget).toHaveBeenNthCalledWith(1, {
      family: "scripted_effect",
      id: "scripted_effect/ALPHA",
      kind: "module",
    });
    expect(onBuildTarget).toHaveBeenNthCalledWith(2, {
      family: "scripted_effect",
      id: "scripted_effect",
      kind: "family",
    });
  });

  it("appends from next_offset without replacing the first page", async () => {
    const queries = installControllableCatalogQueries();
    renderEditor();

    await resolveQuery(
      queries[0],
      catalogPayload([catalogRow("ALPHA", "hash-alpha")], {
        filteredCount: 2,
        hasMore: true,
        nextOffset: 1,
      }),
    );
    await resolveQuery(
      queries[1],
      catalogPayload([hydratedCatalogRow("ALPHA", "hash-alpha")], {
        includeData: true,
      }),
    );

    act(() => {
      void latestListProps().onLoadMore();
    });

    expect(queries[2]?.request).toEqual({
      projectRoot: PROJECT_ROOT,
      entity: "module",
      tag: "scripted_effect",
      limit: 100,
      offset: 1,
      includeData: false,
    });

    await resolveQuery(
      queries[2],
      catalogPayload([catalogRow("BETA", "hash-beta")], {
        filteredCount: 2,
        offset: 1,
      }),
    );

    expect(latestListProps().allEntities.map((entity) => entity.id)).toEqual([
      "module:scripted_effect/ALPHA",
      "module:scripted_effect/BETA",
    ]);
    expect(latestListProps()).toMatchObject({ loadedCount: 2, totalCount: 2 });
  });

  it("ignores a stale same-scope first-page response after a reload generation", async () => {
    const queries = installControllableCatalogQueries();
    renderEditor();

    act(() => latestListProps().onRetryLoad());
    expect(queries).toHaveLength(2);

    await resolveQuery(
      queries[1],
      catalogPayload([catalogRow("BETA", "hash-beta")]),
    );
    expect(queries[2]?.request).toMatchObject({
      targetId: "module:hash-beta",
      includeData: true,
    });
    await resolveQuery(
      queries[2],
      catalogPayload([hydratedCatalogRow("BETA", "hash-beta")], {
        includeData: true,
      }),
    );

    await resolveQuery(
      queries[0],
      catalogPayload([catalogRow("ALPHA", "hash-alpha")]),
    );

    expect(latestListProps().allEntities.map((entity) => entity.id)).toEqual([
      "module:scripted_effect/BETA",
    ]);
    expect(mocks.queryProjectCatalog).toHaveBeenCalledTimes(3);
  });

  it("does not query the Catalog for a diagram surface", () => {
    installControllableCatalogQueries();
    renderEditor({ surface: "diagram" });

    expect(mocks.queryProjectCatalog).not.toHaveBeenCalled();
    expect(mocks.loadProjectCatalogStatus).not.toHaveBeenCalled();
    expect(mocks.refreshProjectCatalog).not.toHaveBeenCalled();
  });

  it("keeps a scoped entity aggregate selectable while its Catalog is missing", async () => {
    const queries = installControllableCatalogQueries();
    mocks.loadProjectCatalogStatus.mockResolvedValue(catalogStatus("missing"));
    renderEditor({ browser: entityAggregateBrowser, familyId: "entity" });

    expect(queries[0]?.request).toMatchObject({
      entity: "module",
      tag: "entity",
    });
    expect(latestListProps().allEntities.map((entity) => entity.id)).toEqual([
      "module:entity/HOI4DEV_ENTITIES",
    ]);
    expect(latestDetailProps().entity).toMatchObject({
      id: "module:entity/HOI4DEV_ENTITIES",
      sourceCount: 2,
      title: "Shared entities",
    });

    await rejectQuery(queries[0], new Error("catalog database does not exist"));
    await settleMicrotasks();

    expect(latestListProps()).toMatchObject({
      catalogMissing: true,
      catalogPreparing: false,
      catalogSearch: false,
    });
    expect(latestListProps().allEntities.map((entity) => entity.id)).toEqual([
      "module:entity/HOI4DEV_ENTITIES",
    ]);
    expect(latestDetailProps()).toMatchObject({
      entity: { id: "module:entity/HOI4DEV_ENTITIES" },
      loading: false,
    });
  });

  it("keeps a source-discovered Technology module buildable without preparing a missing Catalog", async () => {
    const queries = installControllableCatalogQueries();
    const onBuildTarget = vi.fn<(target: BuildTarget) => void>();
    mocks.loadProjectCatalogStatus.mockResolvedValue(catalogStatus("missing"));
    renderEditor({
      browser: technologySourceBrowser,
      familyId: "technologies",
      onBuildTarget,
    });

    expect(queries[0]?.request).toMatchObject({
      entity: "module",
      tag: "technology",
    });
    await rejectQuery(queries[0], new Error("catalog database does not exist"));
    await settleMicrotasks();

    expect(latestListProps()).toMatchObject({
      catalogMissing: true,
      catalogPreparing: false,
      catalogSearch: false,
    });
    expect(latestDetailProps().entity).toMatchObject({
      id: "module:technology/TECHNOLOGY_FIREARM_I",
      moduleId: "technology/TECHNOLOGY_FIREARM_I",
      title: "Firearm I",
    });
    act(() => latestListProps().onQueryChange("FIREARM"));
    expect(latestListProps()).toMatchObject({
      query: "FIREARM",
      entities: [
        expect.objectContaining({
          id: "module:technology/TECHNOLOGY_FIREARM_I",
        }),
      ],
    });
    expect(mocks.queryProjectCatalog).toHaveBeenCalledTimes(1);
    act(() => latestDetailProps().onBuildModule?.());
    expect(onBuildTarget).toHaveBeenCalledWith({
      family: "technology",
      id: "technology/TECHNOLOGY_FIREARM_I",
      kind: "module",
    });
    expect(mocks.refreshProjectCatalog).not.toHaveBeenCalled();
  });

  it("adopts a later source projection after missing-Catalog bypass without losing its retained draft", async () => {
    const queries = installControllableCatalogQueries();
    const sessionStore = new ModuleEditorSessionStore();
    const rerender = renderRefreshableEditor({
      browser: { ...technologySourceBrowser, items: [] },
      familyId: "technologies",
      sessionStore,
    });
    mocks.loadProjectCatalogStatus.mockResolvedValue(catalogStatus("missing"));

    expect(latestListProps().allEntities).toEqual([]);
    await rejectQuery(queries[0], new Error("catalog database does not exist"));
    await settleMicrotasks();

    expect(latestListProps()).toMatchObject({
      allEntities: [],
      catalogMissing: true,
      catalogSearch: false,
    });

    rerender({ browser: technologySourceBrowser });
    expect(latestDetailProps().entity).toMatchObject({
      id: "module:technology/TECHNOLOGY_FIREARM_I",
      title: "Firearm I",
    });

    act(() => {
      latestDetailProps().onTextDraft(
        "module:technology/TECHNOLOGY_FIREARM_I",
        "pdx",
        "technology = { cost = 3 }\n",
      );
    });
    rerender({
      browser: {
        ...technologySourceBrowser,
        items: technologySourceBrowser.items.map((item) => ({
          ...item,
          title: "Firearm I refreshed",
        })),
      },
    });

    expect(latestDetailProps().entity).toMatchObject({
      id: "module:technology/TECHNOLOGY_FIREARM_I",
      title: "Firearm I refreshed",
      draftState: "modified",
      drafts: {
        text: {
          pdx: "technology = { cost = 3 }\n",
        },
      },
    });
    expect(
      sessionStore.read(moduleEditorSessionKey(PROJECT_ROOT, "technologies"))
        ?.dirtyEntities,
    ).toEqual([
      expect.objectContaining({
        id: "module:technology/TECHNOLOGY_FIREARM_I",
        draftState: "modified",
      }),
    ]);
    expect(mocks.queryProjectCatalog).toHaveBeenCalledTimes(1);
    expect(mocks.loadProjectCatalogStatus).toHaveBeenCalledTimes(1);
    expect(mocks.refreshProjectCatalog).not.toHaveBeenCalled();
  });

  it("does not reload for create planning and reloads once after the scaffold writes", async () => {
    const queries = installControllableCatalogQueries();
    const onProjectRefresh = vi.fn(async () => undefined);
    mocks.createModuleDraft
      .mockResolvedValueOnce(moduleDraftPayload(false))
      .mockResolvedValueOnce(moduleDraftPayload(true));
    renderEditor({ onProjectRefresh, templates: catalogTemplates });

    await resolveQuery(
      queries[0],
      catalogPayload([catalogRow("ALPHA", "hash-alpha")]),
    );
    await resolveQuery(
      queries[1],
      catalogPayload([hydratedCatalogRow("ALPHA", "hash-alpha")], {
        includeData: true,
      }),
    );
    await act(async () => {
      expect(await latestListProps().onCreate()).toBe(true);
    });
    expect(
      queries.filter((query) => query.request.includeData === false),
    ).toHaveLength(1);
    const draftId = latestDetailProps().entity?.id;
    expect(draftId).toBe("scripted-effects:NEW_EFFECT");

    await act(async () => {
      await latestDetailProps().onApply(draftId ?? "");
    });

    expect(mocks.createModuleDraft).toHaveBeenNthCalledWith(
      2,
      expect.objectContaining({ objectId: "NEW_EFFECT", write: true }),
    );
    expect(
      queries.filter((query) => query.request.includeData === false),
    ).toHaveLength(2);
    expect(onProjectRefresh).toHaveBeenCalledTimes(1);
  });

  it("reloads once after a canonical rename and drops the old dirty row", async () => {
    const queries = installControllableCatalogQueries();
    const onProjectRefresh = vi.fn(async () => undefined);
    mocks.applyProjectDraft.mockResolvedValue(
      moduleRenameDraftPayload({
        schema: "paradev.hb.catalog-mutation.v1",
        status: "applied",
        code: "catalog.mutation.applied",
        database: `${PROJECT_ROOT}/.paradev/.cache/hb/catalog.sqlite`,
      }),
    );
    renderEditor({ onProjectRefresh });

    await resolveQuery(
      queries[0],
      catalogPayload([catalogRow("ALPHA", "hash-alpha")]),
    );
    await resolveQuery(
      queries[1],
      catalogPayload([hydratedCatalogRow("ALPHA", "hash-alpha")], {
        includeData: true,
      }),
    );
    act(() =>
      latestDetailProps().onInfoDraft("module:scripted_effect/ALPHA", {
        objectId: "RENAMED",
      }),
    );
    await act(async () => {
      await latestDetailProps().onApply("module:scripted_effect/ALPHA");
    });

    expect(mocks.applyProjectDraft).toHaveBeenCalledWith({
      projectId: "PIHC3",
      projectRoot: PROJECT_ROOT,
      moduleRename: {
        moduleId: "scripted_effect/ALPHA",
        objectId: "RENAMED",
        sourceRoot: `${PROJECT_ROOT}/src`,
      },
    });
    expect(
      queries.filter((query) => query.request.includeData === false),
    ).toHaveLength(2);
    expect(onProjectRefresh).toHaveBeenCalledTimes(1);

    await resolveQuery(
      queries[2],
      catalogPayload([catalogRow("RENAMED", "hash-renamed")]),
    );
    await resolveQuery(
      queries[3],
      catalogPayload([hydratedCatalogRow("RENAMED", "hash-renamed")], {
        includeData: true,
      }),
    );
    expect(latestListProps().allEntities.map((entity) => entity.id)).toEqual([
      "module:scripted_effect/RENAMED",
    ]);
  });

  it("opens duplication for a clean module, refreshes, and selects the duplicate", async () => {
    const queries = installControllableCatalogQueries();
    const onProjectRefresh = vi.fn(async () => undefined);
    renderEditor({ onProjectRefresh });

    await resolveQuery(
      queries[0],
      catalogPayload([catalogRow("ALPHA", "hash-alpha")]),
    );
    await resolveQuery(
      queries[1],
      catalogPayload([hydratedCatalogRow("ALPHA", "hash-alpha")], {
        includeData: true,
      }),
    );

    expect(latestDetailProps().canDuplicate).toBe(true);
    act(() => latestDetailProps().onDuplicate());
    expect(latestDuplicateProps()).toMatchObject({
      moduleId: "scripted_effect/ALPHA",
      objectId: "ALPHA",
      projectRoot: PROJECT_ROOT,
      sourceRoot: `${PROJECT_ROOT}/src`,
      title: "Alpha",
    });

    await act(async () => {
      await latestDuplicateProps().onApplied(
        moduleDuplicatePayload([
          {
            code: "module_duplicate.cleanup_pending",
            message: "Hidden transaction cleanup remains pending.",
            severity: "warning",
          },
        ]),
      );
    });

    expect(onProjectRefresh).toHaveBeenCalledWith(PROJECT_ROOT, "PIHC3");
    expect(queries[2]?.request).toMatchObject({
      entity: "module",
      tag: "scripted_effect",
      includeData: false,
    });
    await resolveQuery(
      queries[2],
      catalogPayload([
        catalogRow("ALPHA", "hash-alpha"),
        catalogRow("ALPHA_COPY", "hash-alpha-copy"),
      ]),
    );
    expect(queries[3]?.request).toMatchObject({
      targetId: "module:hash-alpha-copy",
      includeData: true,
    });
    await resolveQuery(
      queries[3],
      catalogPayload([hydratedCatalogRow("ALPHA_COPY", "hash-alpha-copy")], {
        filteredCount: 1,
        includeData: true,
      }),
    );
    expect(latestDetailProps().entity?.id).toBe(
      "module:scripted_effect/ALPHA_COPY",
    );
  });

  it("preserves residual source and title drafts after a partially acknowledged rename", async () => {
    const queries = installControllableCatalogQueries();
    mocks.applyProjectDraft.mockResolvedValue(
      moduleRenameDraftPayload(appliedCatalogMutation()),
    );
    renderEditor();

    await resolveQuery(
      queries[0],
      catalogPayload([catalogRow("ALPHA", "hash-alpha")]),
    );
    await resolveQuery(
      queries[1],
      catalogPayload([hydratedCatalogRow("ALPHA", "hash-alpha")], {
        includeData: true,
      }),
    );
    act(() => {
      latestDetailProps().onTextDraft(
        "module:scripted_effect/ALPHA",
        "def",
        "edited = yes\n",
      );
      latestDetailProps().onInfoDraft("module:scripted_effect/ALPHA", {
        objectId: "RENAMED",
        title: "Draft title",
      });
    });

    await act(async () => {
      await latestDetailProps().onApply("module:scripted_effect/ALPHA");
    });

    expect(mocks.applyProjectDraft).toHaveBeenCalledOnce();
    expect(latestDetailProps().entity).toMatchObject({
      id: "module:scripted_effect/RENAMED",
      draftState: "modified",
      drafts: {
        text: { def: "edited = yes\n" },
      },
      sourceSlots: [
        expect.objectContaining({
          path: `${PROJECT_ROOT}/src/modules/scripted_effect/RENAMED/def.pdx`,
        }),
      ],
    });
  });

  it("keeps the combined source and rename commit when Catalog reconciliation fails", async () => {
    const queries = installControllableCatalogQueries();
    mocks.applyProjectDraft.mockResolvedValue(
      moduleRenameDraftPayload(
        failedCatalogMutation("catalog write failed"),
        "RENAMED",
        "Draft title",
        [
          {
            path: `${PROJECT_ROOT}/src/modules/scripted_effect/ALPHA/def.pdx`,
            relative_path: "src/modules/scripted_effect/ALPHA/def.pdx",
            operation: "write_text",
            encoding: "utf-8",
          },
        ],
      ),
    );
    renderEditor();

    await resolveQuery(
      queries[0],
      catalogPayload([catalogRow("ALPHA", "hash-alpha")]),
    );
    await resolveQuery(
      queries[1],
      catalogPayload([hydratedCatalogRow("ALPHA", "hash-alpha")], {
        includeData: true,
      }),
    );
    act(() => {
      latestDetailProps().onTextDraft(
        "module:scripted_effect/ALPHA",
        "def",
        "edited = yes\n",
      );
      latestDetailProps().onInfoDraft("module:scripted_effect/ALPHA", {
        objectId: "RENAMED",
        title: "Draft title",
      });
    });

    await act(async () => {
      await latestDetailProps().onApply("module:scripted_effect/ALPHA");
    });

    expect(latestDetailProps().entity).toMatchObject({
      id: "module:scripted_effect/RENAMED",
      root: `${PROJECT_ROOT}/src/modules/scripted_effect/RENAMED - Draft title`,
      draftState: "clean",
      drafts: {
        text: {},
      },
    });
    expect(mocks.renameModule).not.toHaveBeenCalled();
    expect(document.body.textContent).toContain("catalog write failed");
  });

  it("refreshes project state after a source-only apply without reloading the Catalog", async () => {
    const queries = installControllableCatalogQueries();
    const onProjectRefresh = vi.fn(async () => undefined);
    mocks.applyProjectDraft.mockResolvedValue({
      schema: "paradev.rest.draft_apply.v1",
      project_id: "PIHC3",
      written: true,
      files: [
        {
          path: `${PROJECT_ROOT}/src/modules/scripted_effect/ALPHA/def.pdx`,
          relative_path: "src/modules/scripted_effect/ALPHA/def.pdx",
          operation: "write_text",
          encoding: "utf-8",
        },
      ],
    });
    renderEditor({ onProjectRefresh });

    await resolveQuery(
      queries[0],
      catalogPayload([catalogRow("ALPHA", "hash-alpha")]),
    );
    await resolveQuery(
      queries[1],
      catalogPayload([hydratedCatalogRow("ALPHA", "hash-alpha")], {
        includeData: true,
      }),
    );
    act(() =>
      latestDetailProps().onTextDraft(
        "module:scripted_effect/ALPHA",
        "def",
        "edited = yes\n",
      ),
    );
    await act(async () => {
      await latestDetailProps().onApply("module:scripted_effect/ALPHA");
    });

    expect(mocks.applyProjectDraft).toHaveBeenCalledTimes(1);
    expect(onProjectRefresh).toHaveBeenCalledWith(PROJECT_ROOT, "PIHC3");
    expect(
      queries.filter((query) => query.request.includeData === false),
    ).toHaveLength(1);
  });

  it("reconciles guided intent through the SDK planner before one guarded source apply", async () => {
    const queries = installControllableCatalogQueries();
    const onProjectRefresh = vi.fn(async () => undefined);
    const path = `${PROJECT_ROOT}/src/modules/scripted_effect/ALPHA/def.pdx`;
    const relativePath = "src/modules/scripted_effect/ALPHA/def.pdx";
    const baseText = "effect = { active = yes }\n";
    const text = "effect = { active = no }\n";
    const sourceEdit = {
      path,
      text,
      expectedSize: 26,
      expectedMtimeNs: "1770000000123456789",
    };
    mocks.planProjectSourceFormUpdates.mockResolvedValue({
      schema: "paradev.source-form-update-batch.v1",
      projectId: "PIHC3",
      changed: true,
      counts: { requested: 1, changed: 1, unchanged: 0 },
      updates: [
        {
          schema: "paradev.source-form-update.v1",
          projectId: "PIHC3",
          family: "scripted_effect",
          moduleId: "scripted_effect/ALPHA",
          path,
          relativePath,
          sourceFormat: "pdx",
          formContract: "test.scripted-effect.v1",
          changed: true,
          changes: [{ controlId: "active", previous: true, value: false }],
          sourceEdit,
        },
      ],
      sourceEdits: [sourceEdit],
    });
    mocks.applyProjectDraft.mockResolvedValue({
      schema: "paradev.rest.draft_apply.v1",
      project_id: "PIHC3",
      written: true,
      files: [
        {
          path,
          relative_path: relativePath,
          operation: "write_text",
          encoding: "utf-8",
        },
      ],
    });
    renderEditor({ onProjectRefresh });

    await resolveQuery(
      queries[0],
      catalogPayload([catalogRow("ALPHA", "hash-alpha")]),
    );
    await resolveQuery(
      queries[1],
      catalogPayload([hydratedCatalogRow("ALPHA", "hash-alpha")], {
        includeData: true,
      }),
    );
    act(() =>
      latestDetailProps().onGuidedTextDraft(
        "module:scripted_effect/ALPHA",
        "def",
        { baseText, controlId: "active", text, value: false },
      ),
    );
    await act(async () => {
      await latestDetailProps().onApply("module:scripted_effect/ALPHA");
    });

    expect(mocks.planProjectSourceFormUpdates).toHaveBeenCalledWith({
      projectId: "PIHC3",
      projectRoot: PROJECT_ROOT,
      updates: [
        {
          sourcePath: path,
          text: baseText,
          values: { active: false },
        },
      ],
    });
    expect(mocks.applyProjectDraft).toHaveBeenCalledWith({
      projectId: "PIHC3",
      projectRoot: PROJECT_ROOT,
      sourceEdits: [sourceEdit],
    });
    expect(latestDetailProps().entity?.drafts.sourceForms).toBeUndefined();
    expect(onProjectRefresh).toHaveBeenCalledWith(PROJECT_ROOT, "PIHC3");
  });

  it("blocks apply when an SDK guided plan does not match the visible draft", async () => {
    const queries = installControllableCatalogQueries();
    const path = `${PROJECT_ROOT}/src/modules/scripted_effect/ALPHA/def.pdx`;
    mocks.planProjectSourceFormUpdates.mockResolvedValue({
      schema: "paradev.source-form-update-batch.v1",
      projectId: "PIHC3",
      changed: true,
      counts: { requested: 1, changed: 1, unchanged: 0 },
      updates: [
        {
          schema: "paradev.source-form-update.v1",
          projectId: "PIHC3",
          family: "scripted_effect",
          moduleId: "scripted_effect/ALPHA",
          path,
          relativePath: "src/modules/scripted_effect/ALPHA/def.pdx",
          sourceFormat: "pdx",
          formContract: "test.scripted-effect.v1",
          changed: true,
          changes: [{ controlId: "active", previous: true, value: false }],
          sourceEdit: {
            path,
            text: "different = yes\n",
            expectedSize: 26,
            expectedMtimeNs: "1770000000123456789",
          },
        },
      ],
      sourceEdits: [
        {
          path,
          text: "different = yes\n",
          expectedSize: 26,
          expectedMtimeNs: "1770000000123456789",
        },
      ],
    });
    renderEditor();

    await resolveQuery(
      queries[0],
      catalogPayload([catalogRow("ALPHA", "hash-alpha")]),
    );
    await resolveQuery(
      queries[1],
      catalogPayload([hydratedCatalogRow("ALPHA", "hash-alpha")], {
        includeData: true,
      }),
    );
    act(() =>
      latestDetailProps().onGuidedTextDraft(
        "module:scripted_effect/ALPHA",
        "def",
        {
          baseText: "effect = { active = yes }\n",
          controlId: "active",
          text: "effect = { active = no }\n",
          value: false,
        },
      ),
    );
    await act(async () => {
      await latestDetailProps().onApply("module:scripted_effect/ALPHA");
    });

    expect(mocks.applyProjectDraft).not.toHaveBeenCalled();
    expect(latestDetailProps().applyError).toContain(
      "could not verify this draft against the project extension",
    );
  });

  it("renames the readable folder without creating metadata for a title-only draft", async () => {
    const queries = installControllableCatalogQueries();
    const onProjectRefresh = vi.fn(async () => undefined);
    mocks.applyProjectDraft.mockResolvedValue(
      moduleRenameDraftPayload(
        appliedCatalogMutation(),
        "ALPHA",
        'Alpha: "友谊"',
      ),
    );
    renderEditor({ onProjectRefresh });

    await resolveQuery(
      queries[0],
      catalogPayload([catalogRow("ALPHA", "hash-alpha")]),
    );
    await resolveQuery(
      queries[1],
      catalogPayload([hydratedCatalogRow("ALPHA", "hash-alpha")], {
        includeData: true,
      }),
    );

    expect(latestDetailProps().canApply).toBe(false);
    expect(mocks.applyProjectDraft).not.toHaveBeenCalled();
    act(() =>
      latestDetailProps().onInfoDraft("module:scripted_effect/ALPHA", {
        title: 'Alpha: "友谊"',
      }),
    );
    expect(latestDetailProps().canApply).toBe(true);

    await act(async () => {
      await latestDetailProps().onApply("module:scripted_effect/ALPHA");
    });

    expect(mocks.applyProjectDraft).toHaveBeenCalledWith({
      projectId: "PIHC3",
      projectRoot: PROJECT_ROOT,
      moduleRename: {
        moduleId: "scripted_effect/ALPHA",
        objectId: "ALPHA",
        sourceRoot: `${PROJECT_ROOT}/src`,
        title: 'Alpha: "友谊"',
      },
    });
    expect(onProjectRefresh).toHaveBeenCalledWith(PROJECT_ROOT, "PIHC3");
  });

  it("preserves a dirty source draft and surfaces the backend error when Apply is rejected", async () => {
    const queries = installControllableCatalogQueries();
    mocks.applyProjectDraft.mockRejectedValue(
      new Error("meta.yaml: invalid YAML"),
    );
    renderEditor();

    await resolveQuery(
      queries[0],
      catalogPayload([catalogRow("ALPHA", "hash-alpha")]),
    );
    await resolveQuery(
      queries[1],
      catalogPayload([hydratedCatalogRow("ALPHA", "hash-alpha")], {
        includeData: true,
      }),
    );
    act(() =>
      latestDetailProps().onTextDraft(
        "module:scripted_effect/ALPHA",
        "def",
        "invalid: [yaml\n",
      ),
    );
    expect(latestDetailProps().entity?.draftState).toBe("modified");

    await act(async () => {
      await latestDetailProps().onApply("module:scripted_effect/ALPHA");
    });

    expect(latestDetailProps().applyError).toBe("meta.yaml: invalid YAML");
    expect(latestDetailProps().entity?.draftState).toBe("modified");
    expect(latestDetailProps().entity?.drafts.text.def).toBe(
      "invalid: [yaml\n",
    );
  });

  it("retains the trusted source transaction path when draft recovery needs attention", async () => {
    const queries = installControllableCatalogQueries();
    const onBatchRecoveryPathsChange = vi.fn();
    const recoveryPath = `${PROJECT_ROOT}/.paradev/source-draft-transaction`;
    mocks.applyProjectDraft.mockRejectedValue(
      new Error(
        "Source draft crash recovery stopped because a file changed outside ParaDev.",
      ),
    );
    mocks.sourceDraftRecoveryPathFromError.mockReturnValue(recoveryPath);
    renderEditor({ onBatchRecoveryPathsChange });

    await resolveQuery(
      queries[0],
      catalogPayload([catalogRow("ALPHA", "hash-alpha")]),
    );
    await resolveQuery(
      queries[1],
      catalogPayload([hydratedCatalogRow("ALPHA", "hash-alpha")], {
        includeData: true,
      }),
    );
    act(() =>
      latestDetailProps().onTextDraft(
        "module:scripted_effect/ALPHA",
        "def",
        "draft text",
      ),
    );

    await act(async () => {
      await latestDetailProps().onApply("module:scripted_effect/ALPHA");
    });

    expect(mocks.sourceDraftRecoveryPathFromError).toHaveBeenCalledWith(
      expect.any(Error),
      PROJECT_ROOT,
    );
    expect(onBatchRecoveryPathsChange).toHaveBeenCalledWith([recoveryPath]);
    expect(latestDetailProps().applyError).toBe(
      "ParaDev preserved recovery data because project files changed during Apply. Do not apply another edit yet; open the recovery folder above and review the preserved files.",
    );
    expect(latestDetailProps().entity?.draftState).toBe("modified");
  });

  it("invalidates source projections when Restore discards a surviving entity draft", async () => {
    const queries = installControllableCatalogQueries();
    renderEditor();

    await resolveQuery(
      queries[0],
      catalogPayload([catalogRow("ALPHA", "hash-alpha")]),
    );
    await resolveQuery(
      queries[1],
      catalogPayload([hydratedCatalogRow("ALPHA", "hash-alpha")], {
        includeData: true,
      }),
    );
    const reloadKey = latestDetailProps().sourceReloadKey;
    const structuralDraft = '{"entities":[{"name":"OTHER"},{"name":"ALPHA"}]}';

    act(() =>
      latestDetailProps().onTextDraft(
        "module:scripted_effect/ALPHA",
        "def",
        structuralDraft,
      ),
    );
    expect(latestDetailProps().entity?.drafts.text.def).toBe(structuralDraft);
    act(() => latestDetailProps().onRestore("module:scripted_effect/ALPHA"));

    expect(latestDetailProps().entity?.draftState).toBe("clean");
    expect(latestDetailProps().entity?.drafts.text.def).toBeUndefined();
    expect(latestDetailProps().sourceReloadKey).toBe(reloadKey + 1);
  });

  it("applies raw binary asset drafts in one request and refreshes project sources", async () => {
    const queries = installControllableCatalogQueries();
    const onProjectRefresh = vi.fn(async () => undefined);
    const assetPath = "src/modules/scripted_effect/ALPHA/model.mesh";
    mocks.applyProjectDraft.mockResolvedValue({
      schema: "paradev.rest.draft_apply.v1",
      project_id: "PIHC3",
      written: true,
      files: [
        {
          path: `${PROJECT_ROOT}/${assetPath}`,
          relative_path: assetPath,
          operation: "replace_bytes",
        },
      ],
    });
    renderEditor({ browser: assetAuthoringBrowser, onProjectRefresh });

    await resolveQuery(
      queries[0],
      catalogPayload([catalogRow("ALPHA", "hash-alpha")]),
    );
    await resolveQuery(
      queries[1],
      catalogPayload([hydratedCatalogRow("ALPHA", "hash-alpha")], {
        includeData: true,
      }),
    );
    act(() =>
      latestDetailProps().onAssetDrafts("module:scripted_effect/ALPHA", [
        {
          fileName: "model.mesh",
          path: assetPath,
          contentBase64: "cGR4YXNzZXRp",
          size: 9,
        },
      ]),
    );
    expect(latestDetailProps().canApply).toBe(true);

    await act(async () => {
      await latestDetailProps().onApply("module:scripted_effect/ALPHA");
    });

    expect(mocks.applyProjectDraft).toHaveBeenCalledTimes(1);
    expect(mocks.applyProjectDraft).toHaveBeenCalledWith({
      projectId: "PIHC3",
      projectRoot: PROJECT_ROOT,
      sourceReplacements: [
        {
          path: assetPath,
          contentBase64: "cGR4YXNzZXRp",
          expectedAbsent: true,
        },
      ],
    });
    expect(onProjectRefresh).toHaveBeenCalledWith(PROJECT_ROOT, "PIHC3");
  });

  it("retains an image draft resource when the backend omits its file acknowledgement", async () => {
    const queries = installControllableCatalogQueries();
    const sessionStore = new ModuleEditorSessionStore();
    const sessionKey = moduleEditorSessionKey(PROJECT_ROOT, "scripted-effects");
    const imagePath = "src/modules/scripted_effect/ALPHA/icon.png";
    const previewUrl = "blob:catalog-image";
    const revokeObjectUrl = vi
      .spyOn(URL, "revokeObjectURL")
      .mockImplementation(() => undefined);
    mocks.applyProjectDraft.mockResolvedValue({
      schema: "paradev.rest.draft_apply.v1",
      project_id: "PIHC3",
      written: true,
      files: [],
      catalog_mutation: appliedCatalogMutation(),
    });
    renderEditor({ sessionStore });

    await resolveQuery(
      queries[0],
      catalogPayload([catalogRow("ALPHA", "hash-alpha")]),
    );
    await resolveQuery(
      queries[1],
      catalogPayload([hydratedCatalogRowWithImage("ALPHA", "hash-alpha")], {
        includeData: true,
      }),
    );
    act(() => {
      latestDetailProps().onImageDraft("module:scripted_effect/ALPHA", {
        contentBase64: "iVBORw0KGgo=",
        fileName: "icon.png",
        path: imagePath,
        previewUrl,
      });
    });

    await act(async () => {
      await latestDetailProps().onApply("module:scripted_effect/ALPHA");
    });

    expect(revokeObjectUrl).not.toHaveBeenCalled();
    expect(sessionStore.read(sessionKey)?.dirtyEntities[0]).toMatchObject({
      id: "module:scripted_effect/ALPHA",
      drafts: {
        image: {
          path: imagePath,
          previewUrl,
        },
      },
    });

    expect(sessionStore.discard(sessionKey)).toBe(true);
    expect(revokeObjectUrl).toHaveBeenCalledOnce();
    expect(revokeObjectUrl).toHaveBeenCalledWith(previewUrl);
  });

  it("commits an acknowledged image write before retryable resource cleanup", async () => {
    const queries = installControllableCatalogQueries();
    const sessionStore = new ModuleEditorSessionStore();
    const sessionKey = moduleEditorSessionKey(PROJECT_ROOT, "scripted-effects");
    const imagePath = "src/modules/scripted_effect/ALPHA/icon.png";
    const previewUrl = "blob:cleanup-failure";
    const revokeObjectUrl = vi
      .spyOn(URL, "revokeObjectURL")
      .mockImplementationOnce(() => {
        throw new Error("preview cleanup failed");
      })
      .mockImplementation(() => undefined);
    mocks.applyProjectDraft.mockResolvedValue({
      schema: "paradev.rest.draft_apply.v1",
      project_id: "PIHC3",
      written: true,
      files: [
        {
          path: `${PROJECT_ROOT}/${imagePath}`,
          relative_path: imagePath,
          operation: "replace_bytes",
        },
      ],
      catalog_mutation: appliedCatalogMutation(),
    });
    renderEditor({ sessionStore });

    await resolveQuery(
      queries[0],
      catalogPayload([catalogRow("ALPHA", "hash-alpha")]),
    );
    await resolveQuery(
      queries[1],
      catalogPayload([hydratedCatalogRowWithImage("ALPHA", "hash-alpha")], {
        includeData: true,
      }),
    );
    act(() => {
      latestDetailProps().onImageDraft("module:scripted_effect/ALPHA", {
        contentBase64: "iVBORw0KGgo=",
        fileName: "icon.png",
        path: imagePath,
        previewUrl,
      });
    });

    await act(async () => {
      await latestDetailProps().onApply("module:scripted_effect/ALPHA");
    });

    expect(revokeObjectUrl).toHaveBeenCalledOnce();
    expect(sessionStore.read(sessionKey)?.dirtyEntities).toEqual([]);
    expect(sessionStore.getSnapshot()).toMatchObject({
      busy: false,
      dirty: true,
    });

    let discarded = false;
    act(() => {
      discarded = sessionStore.discard(sessionKey);
    });
    expect(discarded).toBe(true);
    expect(revokeObjectUrl).toHaveBeenCalledTimes(2);
    expect(sessionStore.getSnapshot()).toEqual({
      busy: false,
      dirty: false,
      sessions: [],
    });
  });

  it("rejects draft mutations from stale callbacks while an apply is in flight", async () => {
    const queries = installControllableCatalogQueries();
    const applyResponse = deferred<DraftApplyPayload>();
    const assetPath = "src/modules/scripted_effect/ALPHA/model.mesh";
    const submittedAsset = {
      fileName: "model.mesh",
      path: assetPath,
      contentBase64: "c3VibWl0dGVk",
      size: 9,
    };
    mocks.applyProjectDraft.mockReturnValue(applyResponse.promise);
    renderEditor({ browser: assetAuthoringBrowser });

    await resolveQuery(
      queries[0],
      catalogPayload([catalogRow("ALPHA", "hash-alpha")]),
    );
    await resolveQuery(
      queries[1],
      catalogPayload([hydratedCatalogRow("ALPHA", "hash-alpha")], {
        includeData: true,
      }),
    );
    act(() =>
      latestDetailProps().onAssetDrafts("module:scripted_effect/ALPHA", [
        submittedAsset,
      ]),
    );
    const staleAssetDrafts = latestDetailProps().onAssetDrafts;
    const staleTextDraft = latestDetailProps().onTextDraft;
    const staleInfoDraft = latestDetailProps().onInfoDraft;

    let applyTask: Promise<void> | undefined;
    await act(async () => {
      applyTask = Promise.resolve(
        latestDetailProps().onApply("module:scripted_effect/ALPHA"),
      );
      await Promise.resolve();
    });
    expect(latestDetailProps().applyBusy).toBe(true);

    act(() => {
      staleAssetDrafts("module:scripted_effect/ALPHA", [
        {
          ...submittedAsset,
          contentBase64: "bmV3ZXI=",
          size: 5,
        },
      ]);
      staleTextDraft("module:scripted_effect/ALPHA", "def", "newer = yes\n");
      staleInfoDraft("module:scripted_effect/ALPHA", { title: "Newer title" });
    });
    expect(latestDetailProps().entity?.drafts).toEqual({
      text: {},
      assets: [submittedAsset],
    });

    await act(async () => {
      applyResponse.resolve({
        schema: "paradev.rest.draft_apply.v1",
        project_id: "PIHC3",
        written: true,
        files: [
          {
            path: `${PROJECT_ROOT}/${assetPath}`,
            relative_path: assetPath,
            operation: "replace_bytes",
          },
        ],
      });
      await applyTask;
    });

    expect(latestDetailProps().applyBusy).toBe(false);
    expect(latestDetailProps().entity?.drafts).toEqual({ text: {} });
    expect(latestDetailProps().entity?.draftState).toBe("clean");
  });

  it("keeps a removed module hidden and pauses stale Catalog reads when index synchronization fails", async () => {
    const queries = installControllableCatalogQueries();
    const onProjectRefresh = vi.fn(async () => undefined);
    mocks.removeModule.mockResolvedValue(
      moduleRemovePayload({
        catalog_mutation: {
          schema: "paradev.hb.catalog-mutation.v1",
          status: "failed",
          code: "catalog.mutation.failed",
          database: `${PROJECT_ROOT}/.paradev/.cache/hb/catalog.sqlite`,
          message: "catalog database is locked",
        },
      }),
    );
    renderEditor({ onProjectRefresh });

    await resolveQuery(
      queries[0],
      catalogPayload([catalogRow("ALPHA", "hash-alpha")]),
    );
    await resolveQuery(
      queries[1],
      catalogPayload([hydratedCatalogRow("ALPHA", "hash-alpha")], {
        includeData: true,
      }),
    );

    act(() => latestListProps().onRemoveSelected());
    expect(latestDetailProps().entity?.draftState).toBe("remove");
    await act(async () => {
      await latestDetailProps().onApply("module:scripted_effect/ALPHA");
    });

    expect(mocks.removeModule).toHaveBeenCalledWith({
      projectRoot: PROJECT_ROOT,
      moduleId: "scripted_effect/ALPHA",
      sourceRoot: `${PROJECT_ROOT}/src`,
    });
    expect(mocks.applyProjectDraft).not.toHaveBeenCalled();
    expect(onProjectRefresh).toHaveBeenCalledTimes(1);
    expect(
      queries.filter((query) => query.request.includeData === false),
    ).toHaveLength(1);
    expect(document.body.textContent).toContain(
      "The module changed, but the project index could not be updated: catalog database is locked",
    );
    expect(document.body.textContent).toContain(
      "Repair project index (~14 min)",
    );
    expect(latestListProps().allEntities).toEqual([]);
  });

  it("rejects a second apply while the first mutation is in flight", async () => {
    const queries = installControllableCatalogQueries();
    const failedRemoval = deferred<ModuleRemovePayload>();
    mocks.removeModule.mockReturnValue(failedRemoval.promise);
    renderEditor();

    await resolveQuery(
      queries[0],
      catalogPayload([catalogRow("ALPHA", "hash-alpha")]),
    );
    await resolveQuery(
      queries[1],
      catalogPayload([hydratedCatalogRow("ALPHA", "hash-alpha")], {
        includeData: true,
      }),
    );
    act(() => latestListProps().onRemoveSelected());
    let failedApply!: Promise<void>;
    let rejectedOverlap!: Promise<void>;
    act(() => {
      const apply = latestDetailProps().onApply;
      failedApply = Promise.resolve(apply("module:scripted_effect/ALPHA"));
      rejectedOverlap = Promise.resolve(apply("module:scripted_effect/ALPHA"));
    });

    await act(async () => {
      failedRemoval.resolve(
        moduleRemovePayload({
          catalog_mutation: {
            schema: "paradev.hb.catalog-mutation.v1",
            status: "failed",
            code: "catalog.mutation.failed",
            database: `${PROJECT_ROOT}/.paradev/.cache/hb/catalog.sqlite`,
            message: "first synchronization failed",
          },
        }),
      );
      await Promise.all([failedApply, rejectedOverlap]);
    });

    expect(mocks.removeModule).toHaveBeenCalledTimes(1);
    expect(
      queries.filter((query) => query.request.includeData === false),
    ).toHaveLength(1);
    expect(latestListProps().allEntities).toEqual([]);
    expect(document.body.textContent).toContain("first synchronization failed");
    expect(document.body.textContent).toContain(
      "Repair project index (~14 min)",
    );
  });

  it("rebuilds a failed mutation index only after the explicit long-running repair action", async () => {
    const queries = installControllableCatalogQueries();
    mocks.removeModule.mockResolvedValue(
      moduleRemovePayload({
        catalog_mutation: {
          schema: "paradev.hb.catalog-mutation.v1",
          status: "failed",
          code: "catalog.mutation.failed",
          database: `${PROJECT_ROOT}/.paradev/.cache/hb/catalog.sqlite`,
          message: "catalog database is locked",
        },
      }),
    );
    renderEditor();

    await resolveQuery(
      queries[0],
      catalogPayload([catalogRow("ALPHA", "hash-alpha")]),
    );
    await resolveQuery(
      queries[1],
      catalogPayload([hydratedCatalogRow("ALPHA", "hash-alpha")], {
        includeData: true,
      }),
    );
    act(() => latestListProps().onRemoveSelected());
    await act(async () => {
      await latestDetailProps().onApply("module:scripted_effect/ALPHA");
    });

    expect(mocks.refreshProjectCatalog).not.toHaveBeenCalled();
    expect(
      queries.filter((query) => query.request.includeData === false),
    ).toHaveLength(1);
    const repairButton = [...document.querySelectorAll("button")].find(
      (button) => button.textContent?.includes("Repair project index"),
    );
    expect(repairButton).toBeDefined();
    await act(async () => {
      repairButton?.click();
      await Promise.resolve();
    });

    expect(mocks.refreshProjectCatalog).toHaveBeenCalledWith({
      projectRoot: PROJECT_ROOT,
    });
    expect(
      queries.filter((query) => query.request.includeData === false),
    ).toHaveLength(2);
  });

  it("keeps a newly scaffolded module visible without querying a stale Catalog after synchronization fails", async () => {
    const queries = installControllableCatalogQueries();
    mocks.createModuleDraft
      .mockResolvedValueOnce(moduleDraftPayload(false))
      .mockResolvedValueOnce(
        moduleDraftPayload(true, {
          schema: "paradev.hb.catalog-mutation.v1",
          status: "failed",
          code: "catalog.mutation.failed",
          database: `${PROJECT_ROOT}/.paradev/.cache/hb/catalog.sqlite`,
          message: "catalog write failed",
        }),
      );
    renderEditor({ templates: catalogTemplates });

    await resolveQuery(
      queries[0],
      catalogPayload([catalogRow("ALPHA", "hash-alpha")]),
    );
    await resolveQuery(
      queries[1],
      catalogPayload([hydratedCatalogRow("ALPHA", "hash-alpha")], {
        includeData: true,
      }),
    );
    await act(async () => {
      expect(await latestListProps().onCreate()).toBe(true);
    });
    await act(async () => {
      await latestDetailProps().onApply("scripted-effects:NEW_EFFECT");
    });

    expect(
      queries.filter((query) => query.request.includeData === false),
    ).toHaveLength(1);
    expect(latestListProps().allEntities.map((entity) => entity.id)).toEqual([
      "module:scripted_effect/ALPHA",
      "module:scripted_effect/NEW_EFFECT",
    ]);
    expect(latestDetailProps().entity).toMatchObject({
      id: "module:scripted_effect/NEW_EFFECT",
      moduleId: "scripted_effect/NEW_EFFECT",
      draftState: "clean",
      root: `${PROJECT_ROOT}/src/modules/scripted_effect/NEW_EFFECT`,
    });
  });

  it("keeps a renamed module editable at its new paths without querying a stale Catalog", async () => {
    const queries = installControllableCatalogQueries();
    mocks.applyProjectDraft.mockResolvedValue(
      moduleRenameDraftPayload({
        schema: "paradev.hb.catalog-mutation.v1",
        status: "failed",
        code: "catalog.mutation.failed",
        database: `${PROJECT_ROOT}/.paradev/.cache/hb/catalog.sqlite`,
        message: "catalog write failed",
      }),
    );
    renderEditor();

    await resolveQuery(
      queries[0],
      catalogPayload([catalogRow("ALPHA", "hash-alpha")]),
    );
    await resolveQuery(
      queries[1],
      catalogPayload([hydratedCatalogRow("ALPHA", "hash-alpha")], {
        includeData: true,
      }),
    );
    act(() =>
      latestDetailProps().onInfoDraft("module:scripted_effect/ALPHA", {
        objectId: "RENAMED",
      }),
    );
    await act(async () => {
      await latestDetailProps().onApply("module:scripted_effect/ALPHA");
    });

    expect(
      queries.filter((query) => query.request.includeData === false),
    ).toHaveLength(1);
    expect(latestListProps().allEntities.map((entity) => entity.id)).toEqual([
      "module:scripted_effect/RENAMED",
    ]);
    expect(latestDetailProps().entity).toMatchObject({
      id: "module:scripted_effect/RENAMED",
      moduleId: "scripted_effect/RENAMED",
      root: `${PROJECT_ROOT}/src/modules/scripted_effect/RENAMED`,
      sourceSlots: [
        expect.objectContaining({
          path: `${PROJECT_ROOT}/src/modules/scripted_effect/RENAMED/def.pdx`,
        }),
      ],
    });
  });

  it("blocks later create, rename, and removal while a dirty Catalog still allows source edits", async () => {
    const queries = installControllableCatalogQueries();
    mocks.applyProjectDraft
      .mockResolvedValueOnce(
        moduleRenameDraftPayload({
          schema: "paradev.hb.catalog-mutation.v1",
          status: "failed",
          code: "catalog.mutation.failed",
          database: `${PROJECT_ROOT}/.paradev/.cache/hb/catalog.sqlite`,
          message: "catalog write failed",
        }),
      )
      .mockResolvedValueOnce({
        schema: "paradev.rest.draft_apply.v1",
        project_id: "PIHC3",
        written: true,
        files: [
          {
            path: `${PROJECT_ROOT}/src/modules/scripted_effect/RENAMED/def.pdx`,
            relative_path: "src/modules/scripted_effect/RENAMED/def.pdx",
            operation: "write_text",
            encoding: "utf-8",
          },
        ],
      });
    mocks.createModuleDraft.mockResolvedValue(moduleDraftPayload(false));
    renderEditor({ templates: catalogTemplates });

    await resolveQuery(
      queries[0],
      catalogPayload([catalogRow("ALPHA", "hash-alpha")]),
    );
    await resolveQuery(
      queries[1],
      catalogPayload([hydratedCatalogRow("ALPHA", "hash-alpha")], {
        includeData: true,
      }),
    );
    act(() =>
      latestDetailProps().onInfoDraft("module:scripted_effect/ALPHA", {
        objectId: "RENAMED",
      }),
    );
    await act(async () => {
      await latestDetailProps().onApply("module:scripted_effect/ALPHA");
    });

    act(() =>
      latestDetailProps().onTextDraft(
        "module:scripted_effect/RENAMED",
        "def",
        "edited = yes\n",
      ),
    );
    expect(latestDetailProps().canApply).toBe(true);
    await act(async () => {
      await latestDetailProps().onApply("module:scripted_effect/RENAMED");
    });
    expect(mocks.applyProjectDraft).toHaveBeenCalledTimes(2);

    act(() =>
      latestDetailProps().onInfoDraft("module:scripted_effect/RENAMED", {
        objectId: "RENAMED_AGAIN",
      }),
    );
    expect(latestDetailProps().canApply).toBe(false);
    await act(async () => {
      await latestDetailProps().onApply("module:scripted_effect/RENAMED");
    });
    expect(mocks.applyProjectDraft).toHaveBeenCalledTimes(2);
    expect(latestDetailProps().applyError).toContain(
      "Repair it before creating, renaming, or removing modules",
    );

    act(() => latestListProps().onRemoveSelected());
    expect(mocks.removeModule).not.toHaveBeenCalled();
    expect(latestDetailProps().entity?.draftState).toBe("modified");

    await act(async () => {
      expect(await latestListProps().onCreate()).toBe(true);
    });
    expect(latestDetailProps().entity?.draftState).toBe("new");
    expect(latestDetailProps().canApply).toBe(false);
    await act(async () => {
      await latestDetailProps().onApply(latestDetailProps().entity?.id ?? "");
    });
    expect(mocks.createModuleDraft).toHaveBeenCalledTimes(1);
    expect(latestDetailProps().applyError).toContain(
      "Repair it before creating, renaming, or removing modules",
    );
    expect(
      queries.filter((query) => query.request.includeData === false),
    ).toHaveLength(1);
  });

  it("preserves a completed rename and pauses Catalog browsing when synchronization is unverified", async () => {
    const queries = installControllableCatalogQueries();
    mocks.applyProjectDraft.mockResolvedValue(
      moduleRenameDraftPayload({
        schema: "paradev.desktop.catalog-mutation-unverified.v1",
        status: "unverified",
        code: "catalog.mutation.unverified",
        message:
          "The source rename completed, but the Catalog result was malformed.",
      }),
    );
    renderEditor();

    await resolveQuery(
      queries[0],
      catalogPayload([catalogRow("ALPHA", "hash-alpha")]),
    );
    await resolveQuery(
      queries[1],
      catalogPayload([hydratedCatalogRow("ALPHA", "hash-alpha")], {
        includeData: true,
      }),
    );
    act(() =>
      latestDetailProps().onInfoDraft("module:scripted_effect/ALPHA", {
        objectId: "RENAMED",
      }),
    );
    await act(async () => {
      await latestDetailProps().onApply("module:scripted_effect/ALPHA");
    });

    expect(
      queries.filter((query) => query.request.includeData === false),
    ).toHaveLength(1);
    expect(latestListProps().allEntities.map((entity) => entity.id)).toEqual([
      "module:scripted_effect/RENAMED",
    ]);
    expect(document.body.textContent).toContain(
      "could not confirm that the project index was updated",
    );
    expect(document.body.textContent).toContain(
      "Repair project index (~14 min)",
    );
  });

  it("keeps a not-configured Catalog offline after removal until preparation is explicitly requested", async () => {
    const queries = installControllableCatalogQueries();
    mocks.removeModule.mockResolvedValue(
      moduleRemovePayload({
        catalog_mutation: {
          schema: "paradev.hb.catalog-mutation.v1",
          status: "not_configured",
          code: "catalog.mutation.not_configured",
          database: `${PROJECT_ROOT}/.paradev/.cache/hb/catalog.sqlite`,
        },
      }),
    );
    renderEditor();

    await resolveQuery(
      queries[0],
      catalogPayload([catalogRow("ALPHA", "hash-alpha")]),
    );
    await resolveQuery(
      queries[1],
      catalogPayload([hydratedCatalogRow("ALPHA", "hash-alpha")], {
        includeData: true,
      }),
    );
    act(() => latestListProps().onRemoveSelected());
    await act(async () => {
      await latestDetailProps().onApply("module:scripted_effect/ALPHA");
    });

    expect(
      queries.filter((query) => query.request.includeData === false),
    ).toHaveLength(1);
    expect(mocks.refreshProjectCatalog).not.toHaveBeenCalled();
    expect(latestListProps()).toMatchObject({
      allEntities: [],
      catalogMissing: true,
      catalogPreparing: false,
    });
  });

  it("blocks rename and removal when one module ID belongs to two source roots", async () => {
    const queries = installControllableCatalogQueries();
    renderEditor();

    await resolveQuery(
      queries[0],
      catalogPayload(
        [
          hydratedCatalogRow("ALPHA", "hash-alpha-a", {
            sourceRoot: `${PROJECT_ROOT}/src-a`,
          }),
          hydratedCatalogRow("ALPHA", "hash-alpha-b", {
            sourceRoot: `${PROJECT_ROOT}/src-b`,
          }),
        ],
        { filteredCount: 2 },
      ),
    );

    expect(latestListProps().allEntities).toHaveLength(2);
    act(() => latestListProps().onRemoveSelected());
    expect(mocks.removeModule).not.toHaveBeenCalled();
    expect(latestDetailProps().applyError).toContain(
      "found scripted_effect/ALPHA in more than one source folder",
    );

    act(() =>
      latestDetailProps().onInfoDraft("module:scripted_effect/ALPHA", {
        objectId: "RENAMED",
      }),
    );
    await act(async () => {
      await latestDetailProps().onApply("module:scripted_effect/ALPHA");
    });
    expect(mocks.renameModule).not.toHaveBeenCalled();
    expect(latestDetailProps().applyError).toContain(
      "found scripted_effect/ALPHA in more than one source folder",
    );
    expect(queries).toHaveLength(1);
  });

  it("still applies a source-only edit when duplicate module IDs make only folder mutations ambiguous", async () => {
    const queries = installControllableCatalogQueries();
    mocks.applyProjectDraft.mockResolvedValue({
      schema: "paradev.rest.draft_apply.v1",
      project_id: "PIHC3",
      written: true,
      files: [
        {
          path: `${PROJECT_ROOT}/src-a/modules/scripted_effect/ALPHA/def.pdx`,
          relative_path: "src-a/modules/scripted_effect/ALPHA/def.pdx",
          operation: "write_text",
          encoding: "utf-8",
        },
      ],
    });
    renderEditor();

    await resolveQuery(
      queries[0],
      catalogPayload(
        [
          hydratedCatalogRow("ALPHA", "hash-alpha-a", {
            sourceRoot: `${PROJECT_ROOT}/src-a`,
          }),
          hydratedCatalogRow("ALPHA", "hash-alpha-b", {
            sourceRoot: `${PROJECT_ROOT}/src-b`,
          }),
        ],
        { filteredCount: 2 },
      ),
    );
    act(() =>
      latestDetailProps().onTextDraft(
        "module:scripted_effect/ALPHA",
        "def",
        "edited = yes\n",
      ),
    );
    await act(async () => {
      await latestDetailProps().onApply("module:scripted_effect/ALPHA");
    });

    expect(mocks.applyProjectDraft).toHaveBeenCalledWith({
      projectId: "PIHC3",
      projectRoot: PROJECT_ROOT,
      sourceEdits: [
        {
          path: `${PROJECT_ROOT}/src-a/modules/scripted_effect/ALPHA/def.pdx`,
          text: "edited = yes\n",
        },
      ],
    });
    expect(mocks.renameModule).not.toHaveBeenCalled();
    expect(mocks.removeModule).not.toHaveBeenCalled();
  });

  it("restores a bypassed family's local state and repair action after switching away and back", async () => {
    const queries = installControllableCatalogQueries();
    mocks.removeModule.mockResolvedValue(
      moduleRemovePayload({
        catalog_mutation: {
          schema: "paradev.hb.catalog-mutation.v1",
          status: "failed",
          code: "catalog.mutation.failed",
          database: `${PROJECT_ROOT}/.paradev/.cache/hb/catalog.sqlite`,
          message: "catalog database is locked",
        },
      }),
    );
    const renderFamily = renderSwitchableFamilyEditor();

    await resolveQuery(
      queries[0],
      catalogPayload([catalogRow("ALPHA", "hash-alpha")]),
    );
    await resolveQuery(
      queries[1],
      catalogPayload([hydratedCatalogRow("ALPHA", "hash-alpha")], {
        includeData: true,
      }),
    );
    act(() => latestListProps().onRemoveSelected());
    await act(async () => {
      await latestDetailProps().onApply("module:scripted_effect/ALPHA");
    });
    expect(latestListProps().allEntities).toEqual([]);

    renderFamily("characters");
    expect(queries[2]?.request).toMatchObject({
      entity: "module",
      tag: "character",
    });
    await resolveQuery(queries[2], catalogPayload([]));
    renderFamily("scripted-effects");

    expect(queries).toHaveLength(3);
    expect(latestListProps().allEntities).toEqual([]);
    expect(document.body.textContent).toContain("catalog database is locked");
    expect(document.body.textContent).toContain(
      "Repair project index (~14 min)",
    );
  });

  it("keeps a blocked canonical removal as a local draft without reloading", async () => {
    const queries = installControllableCatalogQueries();
    const onProjectRefresh = vi.fn(async () => undefined);
    mocks.removeModule.mockResolvedValue(
      moduleRemovePayload({
        blocked: true,
        removed: false,
        diagnostics: [{ message: "module removal is blocked" }],
      }),
    );
    renderEditor({ onProjectRefresh });

    await resolveQuery(
      queries[0],
      catalogPayload([catalogRow("ALPHA", "hash-alpha")]),
    );
    await resolveQuery(
      queries[1],
      catalogPayload([hydratedCatalogRow("ALPHA", "hash-alpha")], {
        includeData: true,
      }),
    );
    act(() => latestListProps().onRemoveSelected());
    await act(async () => {
      await latestDetailProps().onApply("module:scripted_effect/ALPHA");
    });

    expect(latestDetailProps().entity?.draftState).toBe("remove");
    expect(latestDetailProps().applyError).toBe("module removal is blocked");
    expect(
      queries.filter((query) => query.request.includeData === false),
    ).toHaveLength(1);
    expect(onProjectRefresh).not.toHaveBeenCalled();
  });

  it("reconciles a completed canonical removal after unmount", async () => {
    const queries = installControllableCatalogQueries();
    const removal = deferred<ReturnType<typeof moduleRemovePayload>>();
    const onProjectRefresh = vi.fn(async () => undefined);
    const sessionStore = new ModuleEditorSessionStore();
    const sessionKey = moduleEditorSessionKey(PROJECT_ROOT, "scripted-effects");
    mocks.removeModule.mockReturnValue(removal.promise);
    renderEditor({ onProjectRefresh, sessionStore });

    await resolveQuery(
      queries[0],
      catalogPayload([catalogRow("ALPHA", "hash-alpha")]),
    );
    await resolveQuery(
      queries[1],
      catalogPayload([hydratedCatalogRow("ALPHA", "hash-alpha")], {
        includeData: true,
      }),
    );
    act(() => latestListProps().onRemoveSelected());
    let apply!: Promise<void>;
    act(() => {
      apply = Promise.resolve(
        latestDetailProps().onApply("module:scripted_effect/ALPHA"),
      );
    });
    unmountLatestEditor();
    expect(sessionStore.read(sessionKey)?.dirtyEntities).toHaveLength(1);

    await act(async () => {
      removal.resolve(
        moduleRemovePayload({
          catalog_mutation: appliedCatalogMutation(),
        }),
      );
      await removal.promise;
      await apply;
    });

    expect(
      queries.filter((query) => query.request.includeData === false),
    ).toHaveLength(1);
    expect(onProjectRefresh).toHaveBeenCalledWith(PROJECT_ROOT, "PIHC3");
    expect(sessionStore.read(sessionKey)).toBeNull();
    expect(sessionStore.getSnapshot()).toEqual({
      busy: false,
      dirty: false,
      sessions: [],
    });
  });

  it("retains a failed removal Catalog mutation after unmount", async () => {
    const queries = installControllableCatalogQueries();
    const removal = deferred<ReturnType<typeof moduleRemovePayload>>();
    const onProjectRefresh = vi.fn(async () => undefined);
    const sessionStore = new ModuleEditorSessionStore();
    const sessionKey = moduleEditorSessionKey(PROJECT_ROOT, "scripted-effects");
    mocks.removeModule.mockReturnValue(removal.promise);
    renderEditor({ onProjectRefresh, sessionStore });

    await resolveQuery(
      queries[0],
      catalogPayload([catalogRow("ALPHA", "hash-alpha")]),
    );
    await resolveQuery(
      queries[1],
      catalogPayload([hydratedCatalogRow("ALPHA", "hash-alpha")], {
        includeData: true,
      }),
    );
    act(() => latestListProps().onRemoveSelected());
    let apply!: Promise<void>;
    act(() => {
      apply = Promise.resolve(
        latestDetailProps().onApply("module:scripted_effect/ALPHA"),
      );
    });
    unmountLatestEditor();

    await act(async () => {
      removal.resolve(
        moduleRemovePayload({
          catalog_mutation: failedCatalogMutation("catalog write failed"),
        }),
      );
      await removal.promise;
      await apply;
    });

    expect(onProjectRefresh).toHaveBeenCalledWith(PROJECT_ROOT, "PIHC3");
    expect(sessionStore.read(sessionKey)).toMatchObject({
      catalogMutationFailure: {
        status: "failed",
        message: "catalog write failed",
      },
      dirtyEntities: [],
    });
    expect(sessionStore.getSnapshot()).toMatchObject({
      busy: false,
      dirty: true,
    });
  });

  it("offers preparation only after a failed query is classified as a missing Catalog", async () => {
    const queries = installControllableCatalogQueries();
    mocks.loadProjectCatalogStatus.mockResolvedValue(catalogStatus("missing"));
    renderEditor();

    await rejectQuery(queries[0], new Error("catalog database does not exist"));
    await settleMicrotasks();

    expect(mocks.loadProjectCatalogStatus).toHaveBeenCalledWith({
      projectRoot: PROJECT_ROOT,
    });
    expect(mocks.refreshProjectCatalog).not.toHaveBeenCalled();
    expect(latestListProps()).toMatchObject({
      catalogMissing: true,
      catalogPreparing: false,
      loadError: "",
    });
    expect(latestDetailProps().loading).toBe(false);

    await act(async () => {
      await latestListProps().onPrepareCatalog();
    });

    expect(mocks.refreshProjectCatalog).toHaveBeenCalledTimes(1);
    expect(mocks.refreshProjectCatalog).toHaveBeenCalledWith({
      projectRoot: PROJECT_ROOT,
    });
    expect(queries).toHaveLength(2);
    expect(queries[1]?.request).toMatchObject({
      includeData: false,
      limit: 100,
      offset: 0,
    });

    await resolveQuery(
      queries[1],
      catalogPayload([catalogRow("ALPHA", "hash-alpha")]),
    );
    expect(queries[2]?.request).toMatchObject({
      includeData: true,
      limit: 1,
      targetId: "module:hash-alpha",
    });
    await resolveQuery(
      queries[2],
      catalogPayload([hydratedCatalogRow("ALPHA", "hash-alpha")], {
        includeData: true,
      }),
    );

    expect(mocks.queryProjectCatalog).toHaveBeenCalledTimes(3);
    expect(latestListProps().catalogMissing).toBe(false);
  });

  it("keeps a failed explicit preparation visible without retrying it automatically", async () => {
    const queries = installControllableCatalogQueries();
    mocks.loadProjectCatalogStatus.mockResolvedValue(catalogStatus("missing"));
    mocks.refreshProjectCatalog.mockRejectedValue(
      new Error("index preparation failed"),
    );
    renderEditor();

    await rejectQuery(queries[0], new Error("catalog database does not exist"));
    await settleMicrotasks();
    await act(async () => {
      await latestListProps().onPrepareCatalog();
    });

    expect(latestListProps()).toMatchObject({
      catalogMissing: true,
      catalogPreparing: false,
    });
    expect(latestListProps().loadError).toContain("index preparation failed");
    expect(mocks.refreshProjectCatalog).toHaveBeenCalledTimes(1);
    expect(mocks.queryProjectCatalog).toHaveBeenCalledTimes(1);
  });

  it("ignores explicit preparation settlement after the editor unmounts", async () => {
    const queries = installControllableCatalogQueries();
    const refresh = deferred<{ ok: boolean }>();
    mocks.loadProjectCatalogStatus.mockResolvedValue(catalogStatus("missing"));
    mocks.refreshProjectCatalog.mockReturnValue(refresh.promise);
    renderEditor();

    await rejectQuery(queries[0], new Error("catalog database does not exist"));
    await settleMicrotasks();
    let preparation!: Promise<void>;
    act(() => {
      preparation = latestListProps().onPrepareCatalog();
    });
    expect(latestListProps().catalogPreparing).toBe(true);
    unmountLatestEditor();

    await act(async () => {
      refresh.resolve({ ok: true });
      await refresh.promise;
      await preparation;
    });

    expect(mocks.refreshProjectCatalog).toHaveBeenCalledTimes(1);
    expect(mocks.queryProjectCatalog).toHaveBeenCalledTimes(1);
  });

  it.each(["present", "incomplete", "unreadable"] as const)(
    "retains the original query error and source fallback for a %s Catalog status",
    async (status) => {
      const queries = installControllableCatalogQueries();
      mocks.loadProjectCatalogStatus.mockResolvedValue(catalogStatus(status));
      renderEditor();

      await rejectQuery(queries[0], new Error("catalog schema is incomplete"));
      await settleMicrotasks();

      expect(latestListProps().catalogMissing).toBe(false);
      if (status === "present") {
        expect(latestListProps().loadError).toContain(
          "catalog schema is incomplete",
        );
      } else {
        expect(latestListProps()).toMatchObject({
          catalogSearch: false,
          loadError: "",
        });
        expect(document.body.textContent).toContain(
          "catalog schema is incomplete",
        );
        expect(document.body.textContent).toContain("Repair project index");
      }
      expect(mocks.refreshProjectCatalog).not.toHaveBeenCalled();
    },
  );

  it("ignores a stale missing-status result after an explicit reload", async () => {
    const queries = installControllableCatalogQueries();
    const status = deferred<ReturnType<typeof catalogStatus>>();
    mocks.loadProjectCatalogStatus.mockReturnValue(status.promise);
    renderEditor();

    await rejectQuery(queries[0], new Error("old query failure"));
    act(() => latestListProps().onRetryLoad());
    expect(queries).toHaveLength(2);

    await act(async () => {
      status.resolve(catalogStatus("missing"));
      await status.promise;
    });

    expect(latestListProps().catalogMissing).toBe(false);
    expect(mocks.refreshProjectCatalog).not.toHaveBeenCalled();
  });

  it("performs one hydrated name lookup for an external selection outside the loaded page", async () => {
    const queries = installControllableCatalogQueries();
    renderEditor({ selectedEntityId: "module:scripted_effect/OUTSIDE" });

    const firstPage = queries.find(
      (query) => query.request.includeData === false,
    );
    await resolveQuery(
      firstPage,
      catalogPayload([catalogRow("ALPHA", "hash-alpha")], { filteredCount: 2 }),
    );

    const nameLookup = queries.find(
      (query) => query.request.name === "scripted_effect/OUTSIDE",
    );
    expect(nameLookup?.request).toEqual({
      projectRoot: PROJECT_ROOT,
      entity: "module",
      tag: "scripted_effect",
      name: "scripted_effect/OUTSIDE",
      limit: 1,
      offset: 0,
      includeData: true,
    });

    await resolveQuery(
      nameLookup,
      catalogPayload([hydratedCatalogRow("OUTSIDE", "hash-outside")], {
        filteredCount: 1,
        includeData: true,
      }),
    );

    expect(
      queries.filter(
        (query) => query.request.name === "scripted_effect/OUTSIDE",
      ),
    ).toHaveLength(1);
    expect(
      queries.filter(
        (query) => query.request.targetId === "module:hash-outside",
      ),
    ).toHaveLength(0);
    expect(latestListProps().allEntities.map((entity) => entity.id)).toEqual([
      "module:scripted_effect/ALPHA",
      "module:scripted_effect/OUTSIDE",
    ]);
    expect(latestDetailProps().entity?.id).toBe(
      "module:scripted_effect/OUTSIDE",
    );
  });

  it("does not erase search when its own selected row is echoed back by the workspace", async () => {
    const queries = installControllableCatalogQueries();
    renderSelectionFeedbackEditor();

    await resolveQuery(
      queries[0],
      catalogPayload([
        catalogRow("ALPHA", "hash-alpha"),
        catalogRow("BETA", "hash-beta"),
      ]),
    );
    await resolveQuery(
      queries[1],
      catalogPayload([hydratedCatalogRow("ALPHA", "hash-alpha")], {
        includeData: true,
      }),
    );

    expect(latestListProps().query).toBe("");
    act(() => latestListProps().onQueryChange("BETA"));

    expect(latestListProps().query).toBe("BETA");
  });

  it("does not look up a newly created local draft when selection is echoed back", async () => {
    const queries = installControllableCatalogQueries();
    mocks.createModuleDraft.mockResolvedValue({
      schema: "paradev.rest.module_draft.v1",
      project_id: "PIHC3",
      family_id: "scripted-effects",
      draft_id: "draft-local",
      plan: {
        schema: "paradev.sdk.module_scaffold.v1",
        project_id: "PIHC3",
        template_id: "",
        family: "scripted_effect",
        object_id: "LOCAL_DRAFT",
        module_id: "scripted_effect/LOCAL_DRAFT",
        root: `${PROJECT_ROOT}/src/modules/scripted_effect/LOCAL_DRAFT`,
        values: { title: "Local draft" },
        blocked: false,
        written: false,
        diagnostics: [],
        files: [],
      },
    });
    renderSelectionFeedbackEditor();

    await resolveQuery(
      queries[0],
      catalogPayload([catalogRow("ALPHA", "hash-alpha")]),
    );
    await resolveQuery(
      queries[1],
      catalogPayload([hydratedCatalogRow("ALPHA", "hash-alpha")], {
        includeData: true,
      }),
    );

    await act(async () => {
      expect(await latestListProps().onCreate()).toBe(true);
    });

    expect(latestListProps().allEntities.map((entity) => entity.id)).toContain(
      "scripted-effects:LOCAL_DRAFT",
    );
    expect(latestDetailProps().entity?.id).toBe("scripted-effects:LOCAL_DRAFT");
    expect(
      queries.filter((query) => query.request.name?.includes("LOCAL_DRAFT")),
    ).toHaveLength(0);
  });

  it("ignores a prior selection hydration failure after selecting another row", async () => {
    const queries = installControllableCatalogQueries();
    renderEditor();

    await resolveQuery(
      queries[0],
      catalogPayload([
        catalogRow("ALPHA", "hash-alpha"),
        catalogRow("BETA", "hash-beta"),
      ]),
    );
    expect(queries[1]?.request.targetId).toBe("module:hash-alpha");

    act(() => latestListProps().onSelect("module:scripted_effect/BETA"));
    expect(queries[2]?.request.targetId).toBe("module:hash-beta");

    await rejectQuery(queries[1], new Error("stale alpha failure"));

    expect(latestListProps().loadError).toBe("");
    expect(latestListProps().hydratingEntityId).toBe(
      "module:scripted_effect/BETA",
    );

    await resolveQuery(
      queries[2],
      catalogPayload([hydratedCatalogRow("BETA", "hash-beta")], {
        includeData: true,
      }),
    );
    expect(latestDetailProps().entity?.id).toBe("module:scripted_effect/BETA");
  });

  it("ignores old hydration when a debounced search starts a new generation", async () => {
    const queries = installControllableCatalogQueries();
    renderEditor();

    await resolveQuery(
      queries[0],
      catalogPayload([catalogRow("ALPHA", "hash-alpha")]),
    );
    expect(queries[1]?.request.targetId).toBe("module:hash-alpha");

    act(() => latestListProps().onQueryChange("BETA"));
    act(() => vi.advanceTimersByTime(180));
    expect(queries[2]?.request).toMatchObject({
      name: "BETA",
      includeData: false,
    });

    await resolveQuery(
      queries[2],
      catalogPayload([catalogRow("BETA", "hash-beta")]),
    );
    expect(queries[3]?.request.targetId).toBe("module:hash-beta");

    await rejectQuery(queries[1], new Error("old generation failure"));
    expect(latestListProps().loadError).toBe("");
    expect(latestListProps().allEntities.map((entity) => entity.id)).toEqual([
      "module:scripted_effect/BETA",
    ]);
  });

  it("keeps a controlled external target while its off-page lookup is pending", async () => {
    const queries = installControllableCatalogQueries();
    renderSelectionFeedbackEditor();

    await resolveQuery(
      queries[0],
      catalogPayload([catalogRow("ALPHA", "hash-alpha")]),
    );
    await resolveQuery(
      queries[1],
      catalogPayload([hydratedCatalogRow("ALPHA", "hash-alpha")], {
        includeData: true,
      }),
    );
    expect(latestWorkspaceSelection?.entityId).toBe(
      "module:scripted_effect/ALPHA",
    );

    act(() =>
      setWorkspaceSelection?.({
        entityId: "module:scripted_effect/OUTSIDE",
        familyId: "scripted-effects",
      }),
    );

    const nameLookup = queries.find(
      (query) => query.request.name === "scripted_effect/OUTSIDE",
    );
    expect(nameLookup).toBeDefined();
    expect(latestWorkspaceSelection?.entityId).toBe(
      "module:scripted_effect/OUTSIDE",
    );

    await resolveQuery(
      nameLookup,
      catalogPayload([hydratedCatalogRow("OUTSIDE", "hash-outside")], {
        filteredCount: 1,
        includeData: true,
      }),
    );

    expect(latestWorkspaceSelection?.entityId).toBe(
      "module:scripted_effect/OUTSIDE",
    );
    expect(latestDetailProps().entity?.id).toBe(
      "module:scripted_effect/OUTSIDE",
    );
  });

  it("waits for explicit retry after the current row hydration fails", async () => {
    const queries = installControllableCatalogQueries();
    renderEditor();

    await resolveQuery(
      queries[0],
      catalogPayload([catalogRow("ALPHA", "hash-alpha")]),
    );
    await rejectQuery(queries[1], new Error("alpha hydration failed"));

    expect(latestListProps().loadError).toContain("alpha hydration failed");
    expect(
      queries.filter((query) => query.request.targetId === "module:hash-alpha"),
    ).toHaveLength(1);

    act(() => latestListProps().onQueryChange(" "));
    expect(
      queries.filter((query) => query.request.targetId === "module:hash-alpha"),
    ).toHaveLength(1);

    act(() => latestListProps().onRetryLoad());
    expect(queries.at(-1)?.request).toMatchObject({
      includeData: false,
      offset: 0,
    });
  });

  it("surfaces incomplete hydrated data without retrying it in a loop", async () => {
    const queries = installControllableCatalogQueries();
    renderEditor();

    await resolveQuery(
      queries[0],
      catalogPayload([catalogRow("ALPHA", "hash-alpha")]),
    );
    await resolveQuery(
      queries[1],
      catalogPayload([catalogRow("ALPHA", "hash-alpha")], {
        includeData: true,
      }),
    );

    expect(latestListProps().loadError).toContain("incomplete module data");
    expect(
      queries.filter((query) => query.request.targetId === "module:hash-alpha"),
    ).toHaveLength(1);
  });

  it("scopes a bounded hydration error to the row that failed", async () => {
    const queries = installControllableCatalogQueries();
    renderEditor();

    await resolveQuery(
      queries[0],
      catalogPayload([
        catalogRow("ALPHA", "hash-alpha"),
        catalogRow("BETA", "hash-beta"),
      ]),
    );
    expect(queries[1]?.request.targetId).toBe("module:hash-alpha");

    act(() => latestListProps().onSelect("module:scripted_effect/BETA"));
    await resolveQuery(
      queries[2],
      catalogPayload([hydratedCatalogRow("BETA", "hash-beta")], {
        includeData: true,
      }),
    );

    act(() => latestListProps().onSelect("module:scripted_effect/ALPHA"));
    await rejectQuery(queries[1], new Error("alpha only failure"));
    expect(latestListProps().loadError).toContain("alpha only failure");

    act(() => latestListProps().onSelect("module:scripted_effect/BETA"));
    expect(latestListProps().loadError).toBe("");

    act(() => latestListProps().onSelect("module:scripted_effect/ALPHA"));
    expect(latestListProps().loadError).toContain("alpha only failure");
    expect(mocks.queryProjectCatalog).toHaveBeenCalledTimes(3);
  });

  it("retains one row's error when another lightweight row begins hydrating", async () => {
    const queries = installControllableCatalogQueries();
    renderEditor();

    await resolveQuery(
      queries[0],
      catalogPayload([
        catalogRow("ALPHA", "hash-alpha"),
        catalogRow("BETA", "hash-beta"),
      ]),
    );
    await rejectQuery(queries[1], new Error("retained alpha failure"));
    expect(latestListProps().loadError).toContain("retained alpha failure");

    act(() => latestListProps().onSelect("module:scripted_effect/BETA"));
    expect(queries[2]?.request.targetId).toBe("module:hash-beta");
    expect(latestListProps().loadError).toBe("");

    act(() => latestListProps().onSelect("module:scripted_effect/ALPHA"));
    expect(latestListProps().loadError).toContain("retained alpha failure");
    expect(
      queries.filter((query) => query.request.targetId === "module:hash-alpha"),
    ).toHaveLength(1);
  });

  it("keeps a newer same-target hydration owned after an old finalizer settles", async () => {
    const queries = installControllableCatalogQueries();
    renderEditor();

    await resolveQuery(
      queries[0],
      catalogPayload([catalogRow("ALPHA", "hash-alpha")]),
    );
    expect(queries[1]?.request.targetId).toBe("module:hash-alpha");

    act(() => latestListProps().onRetryLoad());
    await resolveQuery(
      queries[2],
      catalogPayload([catalogRow("ALPHA", "hash-alpha")]),
    );
    expect(queries[3]?.request.targetId).toBe("module:hash-alpha");

    await resolveQuery(
      queries[1],
      catalogPayload([hydratedCatalogRow("ALPHA", "hash-alpha")], {
        includeData: true,
      }),
    );
    await rejectQuery(queries[3], new Error("new alpha failure"));

    expect(latestListProps().loadError).toContain("new alpha failure");
    expect(mocks.queryProjectCatalog).toHaveBeenCalledTimes(4);
  });

  it("cancels debounce and ignores page settlement after unmount", async () => {
    const queries = installControllableCatalogQueries();
    renderEditor();

    act(() => latestListProps().onQueryChange("BETA"));
    unmountLatestEditor();
    act(() => vi.advanceTimersByTime(180));
    await resolveQuery(
      queries[0],
      catalogPayload([catalogRow("ALPHA", "hash-alpha")]),
    );

    expect(mocks.queryProjectCatalog).toHaveBeenCalledTimes(1);
  });

  it("ignores selected-row hydration settlement after unmount", async () => {
    const queries = installControllableCatalogQueries();
    renderEditor();

    await resolveQuery(
      queries[0],
      catalogPayload([catalogRow("ALPHA", "hash-alpha")]),
    );
    expect(queries[1]?.request.targetId).toBe("module:hash-alpha");
    unmountLatestEditor();

    await resolveQuery(
      queries[1],
      catalogPayload([hydratedCatalogRow("ALPHA", "hash-alpha")], {
        includeData: true,
      }),
    );
    expect(mocks.queryProjectCatalog).toHaveBeenCalledTimes(2);
  });
});

function installControllableCatalogQueries(): PendingCatalogQuery[] {
  const queries: PendingCatalogQuery[] = [];
  mocks.queryProjectCatalog.mockImplementation(
    (request: ProjectCatalogQueryRequest) => {
      const response = deferred<ProjectCatalogQueryPayload>();
      queries.push({ request, response });
      return response.promise;
    },
  );
  return queries;
}

function renderEditor(
  overrides: Partial<React.ComponentProps<typeof ModuleEditor>> = {},
): void {
  const container = document.createElement("div");
  document.body.append(container);
  const root = createRoot(container);
  mountedRoots.push({ container, root });
  act(() => {
    root.render(
      <ModuleEditor
        browser={browser}
        familyId="scripted-effects"
        locale="en"
        onPinTab={() => undefined}
        onProjectRefresh={async () => undefined}
        openTarget="finder"
        templates={null}
        t={createTranslator("en")}
        theme="light"
        {...overrides}
      />,
    );
  });
}

function renderRefreshableEditor(
  initialOverrides: Partial<React.ComponentProps<typeof ModuleEditor>> = {},
): (overrides: Partial<React.ComponentProps<typeof ModuleEditor>>) => void {
  const container = document.createElement("div");
  document.body.append(container);
  const root = createRoot(container);
  mountedRoots.push({ container, root });
  const render = (
    overrides: Partial<React.ComponentProps<typeof ModuleEditor>>,
  ) => {
    act(() => {
      root.render(
        <ModuleEditor
          browser={browser}
          familyId="scripted-effects"
          locale="en"
          onPinTab={() => undefined}
          onProjectRefresh={async () => undefined}
          openTarget="finder"
          templates={null}
          t={createTranslator("en")}
          theme="light"
          {...initialOverrides}
          {...overrides}
        />,
      );
    });
  };
  render({});
  return render;
}

function renderSelectionFeedbackEditor(): void {
  const container = document.createElement("div");
  document.body.append(container);
  const root = createRoot(container);
  mountedRoots.push({ container, root });
  act(() => root.render(<SelectionFeedbackEditor />));
}

function renderSwitchableFamilyEditor(): (familyId: string) => void {
  const container = document.createElement("div");
  document.body.append(container);
  const root = createRoot(container);
  mountedRoots.push({ container, root });
  const switchableBrowser: ProjectBrowserPayload = {
    ...browser,
    families: [
      ...browser.families,
      {
        id: "characters",
        family: "character",
        title: "Characters",
        item_count: 0,
        source_count: 0,
        layouts: ["canonical"],
      },
    ],
  };
  const renderFamily = (familyId: string) => {
    act(() => {
      root.render(
        <ModuleEditor
          browser={switchableBrowser}
          familyId={familyId}
          locale="en"
          onPinTab={() => undefined}
          onProjectRefresh={async () => undefined}
          openTarget="finder"
          templates={null}
          t={createTranslator("en")}
          theme="light"
        />,
      );
    });
  };
  renderFamily("scripted-effects");
  return renderFamily;
}

function unmountLatestEditor(): void {
  const mounted = mountedRoots.pop();
  expect(mounted).toBeDefined();
  if (!mounted) {
    return;
  }
  act(() => mounted.root.unmount());
  mounted.container.remove();
}

function SelectionFeedbackEditor() {
  const [selection, setSelection] =
    useState<WorkspaceModuleSelectionTarget | null>(null);
  latestWorkspaceSelection = selection;
  setWorkspaceSelection = setSelection;
  return (
    <ModuleEditor
      browser={browser}
      familyId="scripted-effects"
      locale="en"
      onModuleSelectionTargetChange={setSelection}
      onPinTab={() => undefined}
      onProjectRefresh={async () => undefined}
      openTarget="finder"
      selectedEntityId={selection?.entityId ?? ""}
      selectedSourcePath={selection?.sourcePath ?? ""}
      templates={null}
      t={createTranslator("en")}
      theme="light"
    />
  );
}

function deferred<Value>(): Deferred<Value> {
  let resolve!: (value: Value) => void;
  let reject!: (reason: unknown) => void;
  const promise = new Promise<Value>((resolvePromise, rejectPromise) => {
    resolve = resolvePromise;
    reject = rejectPromise;
  });
  return { promise, resolve, reject };
}

function catalogStatus(
  status: "present" | "missing" | "incomplete" | "unreadable",
) {
  const codes = {
    present: "catalog.present",
    missing: "catalog.missing",
    incomplete: "catalog.incomplete",
    unreadable: "catalog.unreadable",
  } as const;
  return {
    schema: "paradev.hb.catalog-status.v1" as const,
    status,
    code: codes[status],
    project_id: "PIHC3",
    database: `${PROJECT_ROOT}/.paradev/.cache/hb/catalog.sqlite`,
  };
}

function moduleRemovePayload(
  overrides: Partial<ModuleRemovePayload> = {},
): ModuleRemovePayload {
  return {
    schema: "paradev.module.remove.v1",
    project_id: "PIHC3",
    module_id: "scripted_effect/ALPHA",
    family: "scripted_effect",
    source_root: `${PROJECT_ROOT}/src`,
    root: `${PROJECT_ROOT}/src/modules/scripted_effect/ALPHA`,
    relative_path: "src/modules/scripted_effect/ALPHA",
    blocked: false,
    removed: true,
    diagnostics: [],
    files: [],
    module: {},
    ...overrides,
  };
}

function moduleDuplicatePayload(
  diagnostics: Array<Record<string, unknown>> = [],
): ModuleDuplicatePayload {
  return {
    schema: "paradev.sdk.module_duplicate.v1",
    project_id: "PIHC3",
    source_module_id: "scripted_effect/ALPHA",
    module_id: "scripted_effect/ALPHA_COPY",
    family: "scripted_effect",
    object_id: "ALPHA_COPY",
    source_root: `${PROJECT_ROOT}/src`,
    destination_source_root: `${PROJECT_ROOT}/src`,
    source_module_root: `${PROJECT_ROOT}/src/modules/scripted_effect/ALPHA`,
    root: `${PROJECT_ROOT}/src/modules/scripted_effect/ALPHA_COPY`,
    source_relative_path: "src/modules/scripted_effect/ALPHA",
    relative_path: "src/modules/scripted_effect/ALPHA_COPY",
    status: "duplicated",
    blocked: false,
    applied: true,
    written: true,
    plan_hash: "a".repeat(64),
    identity_mode: "rewrite",
    identity_rewriter: "paradev.token-identity.v1",
    content_rewritten: false,
    paths_rewritten: false,
    diagnostics,
    directories: [],
    files: [],
    exclusions: [],
    totals: {
      directory_count: 0,
      file_count: 0,
      excluded_count: 0,
      size_bytes: 0,
      target_size_bytes: 0,
      rewritten_file_count: 0,
      renamed_path_count: 0,
    },
    source: {
      module_id: "scripted_effect/ALPHA",
      source_root: `${PROJECT_ROOT}/src`,
      root: `${PROJECT_ROOT}/src/modules/scripted_effect/ALPHA`,
      relative_path: "src/modules/scripted_effect/ALPHA",
      root_identity: [1, 1],
      modules_identity: [1, 2],
      family_identity: [1, 3],
      module_identity: [1, 4],
      tree_digest: "b".repeat(64),
      content_digest: "c".repeat(64),
      identity_rewriter: "paradev.token-identity.v1",
    },
    destination: {
      module_id: "scripted_effect/ALPHA_COPY",
      source_root: `${PROJECT_ROOT}/src`,
      root: `${PROJECT_ROOT}/src/modules/scripted_effect/ALPHA_COPY`,
      relative_path: "src/modules/scripted_effect/ALPHA_COPY",
      root_identity: [1, 1],
      modules_identity: [1, 2],
      family_identity: [1, 3],
      target_identity: [1, 5],
      entry_count: 1,
      entry_names_digest: "d".repeat(64),
      content_digest: "e".repeat(64),
    },
    catalog_mutation: {
      schema: "paradev.hb.catalog-mutation.v1",
      status: "applied",
      code: "catalog.mutation.applied",
      database: `${PROJECT_ROOT}/.paradev/.cache/hb/catalog.sqlite`,
    },
  };
}

function moduleDraftPayload(
  written: boolean,
  catalogMutation: CatalogMutationResult | undefined = written
    ? {
        schema: "paradev.hb.catalog-mutation.v1",
        status: "applied",
        code: "catalog.mutation.applied",
        database: `${PROJECT_ROOT}/.paradev/.cache/hb/catalog.sqlite`,
      }
    : undefined,
): ModuleDraftPayload {
  return {
    schema: "paradev.rest.module_draft.v1",
    project_id: "PIHC3",
    family_id: "scripted-effects",
    draft_id: "scripted-effects:NEW_EFFECT",
    plan: {
      schema: "paradev.sdk.module_scaffold.v1",
      project_id: "PIHC3",
      template_id: "pihc3:scripted_effect/basic",
      family: "scripted_effect",
      object_id: "NEW_EFFECT",
      module_id: "scripted_effect/NEW_EFFECT",
      root: `${PROJECT_ROOT}/src/modules/scripted_effect/NEW_EFFECT`,
      values: { object_id: "NEW_EFFECT", title: "New effect" },
      blocked: false,
      written,
      diagnostics: [],
      files: [],
      ...(catalogMutation ? { catalog_mutation: catalogMutation } : {}),
    },
  };
}

function moduleRenamePayload(
  catalogMutation: CatalogMutationResult,
  objectId = "RENAMED",
  title = "",
) {
  const folderName = title ? `${objectId} - ${title}` : objectId;
  return {
    schema: "paradev.module.rename.v1" as const,
    project_id: "PIHC3",
    previous_module_id: "scripted_effect/ALPHA",
    module_id: `scripted_effect/${objectId}`,
    family: "scripted_effect",
    previous_root: `${PROJECT_ROOT}/src/modules/scripted_effect/ALPHA`,
    root: `${PROJECT_ROOT}/src/modules/scripted_effect/${folderName}`,
    previous_relative_path: "src/modules/scripted_effect/ALPHA",
    relative_path: `src/modules/scripted_effect/${folderName}`,
    content_rewritten: false,
    module: {},
    catalog_mutation: catalogMutation,
  };
}

function moduleRenameDraftPayload(
  catalogMutation: CatalogMutationResult,
  objectId = "RENAMED",
  title = "",
  files: DraftApplyPayload["files"] = [],
): DraftApplyPayload {
  return {
    schema: "paradev.rest.draft_apply.v1",
    project_id: "PIHC3",
    written: true,
    files,
    catalog_mutation: catalogMutation,
    module_rename: moduleRenamePayload(catalogMutation, objectId, title),
  };
}

function appliedCatalogMutation(): CatalogMutationResult {
  return {
    schema: "paradev.hb.catalog-mutation.v1",
    status: "applied",
    code: "catalog.mutation.applied",
    database: `${PROJECT_ROOT}/.paradev/.cache/hb/catalog.sqlite`,
  };
}

function failedCatalogMutation(message: string): CatalogMutationResult {
  return {
    schema: "paradev.hb.catalog-mutation.v1",
    status: "failed",
    code: "catalog.mutation.failed",
    database: `${PROJECT_ROOT}/.paradev/.cache/hb/catalog.sqlite`,
    message,
  };
}

async function settleMicrotasks(): Promise<void> {
  await act(async () => {
    await Promise.resolve();
    await Promise.resolve();
  });
}

async function resolveQuery(
  query: PendingCatalogQuery | undefined,
  payload: ProjectCatalogQueryPayload,
): Promise<void> {
  expect(query).toBeDefined();
  await act(async () => {
    query?.response.resolve(payload);
    await query?.response.promise;
  });
}

async function rejectQuery(
  query: PendingCatalogQuery | undefined,
  error: Error,
): Promise<void> {
  expect(query).toBeDefined();
  await act(async () => {
    query?.response.reject(error);
    await expect(query?.response.promise).rejects.toThrow(error.message);
  });
}

function catalogRow(objectId: string, targetHash: string): ProjectCatalogRow {
  const moduleId = `scripted_effect/${objectId}`;
  return {
    object_id: `catalog:hoi4-module:module:${targetHash}`,
    target_id: `module:${targetHash}`,
    target_entity: "hoi4-module",
    name: moduleId,
    desc: "",
    tags: ["module", "scripted_effect", moduleId],
    active: true,
    workspace_id: "PIHC3-hoi4",
  };
}

function hydratedCatalogRow(
  objectId: string,
  targetHash: string,
  options: { sourceRoot?: string } = {},
): ProjectCatalogRow {
  const row = catalogRow(objectId, targetHash);
  const sourceRoot = options.sourceRoot ?? `${PROJECT_ROOT}/src`;
  const root = `${sourceRoot}/modules/scripted_effect/${objectId}`;
  return {
    ...row,
    data: {
      module_id: row.name,
      family: "scripted_effect",
      root,
      source_root: sourceRoot,
      source_slots: {
        def: ["def.pdx"],
      },
      metadata: {
        title: objectId.slice(0, 1) + objectId.slice(1).toLowerCase(),
      },
    },
  };
}

function hydratedCatalogRowWithImage(
  objectId: string,
  targetHash: string,
): ProjectCatalogRow {
  const row = hydratedCatalogRow(objectId, targetHash);
  return {
    ...row,
    data: {
      ...(row.data ?? {}),
      source_slots: {
        def: ["def.pdx"],
        icon: ["icon.png"],
      },
    },
  };
}

function catalogPayload(
  rows: ProjectCatalogRow[],
  options: {
    filteredCount?: number;
    hasMore?: boolean;
    includeData?: boolean;
    nextOffset?: number | null;
    offset?: number;
  } = {},
): ProjectCatalogQueryPayload {
  const offset = options.offset ?? 0;
  const includeData = options.includeData ?? false;
  return {
    schema: "paradev.hb.catalog-query.v1",
    project_id: "PIHC3",
    database: `${PROJECT_ROOT}/.paradev/.cache/hb/catalog.sqlite`,
    filters: {
      entity: "module",
      tag: "scripted_effect",
      limit: includeData ? 1 : 100,
      ...(offset ? { offset } : {}),
      include_data: includeData,
    },
    total_count: 1_116_679,
    filtered_count: options.filteredCount ?? rows.length,
    count: rows.length,
    data_included: includeData,
    page: {
      offset,
      limit: includeData ? 1 : 100,
      has_more: options.hasMore ?? false,
      next_offset: options.nextOffset ?? null,
    },
    rows,
  };
}

function latestListProps(): CapturedListProps {
  const props = mocks.listProps.at(-1);
  if (!props) {
    throw new Error("ModuleEntityList has not rendered");
  }
  return props as CapturedListProps;
}

function latestDetailProps(): CapturedDetailProps {
  const props = mocks.detailProps.at(-1);
  if (!props) {
    throw new Error("ModuleEntityDetails has not rendered");
  }
  return props as CapturedDetailProps;
}

function latestDuplicateProps(): CapturedDuplicateProps {
  const props = mocks.duplicateProps.at(-1);
  if (!props) {
    throw new Error("ModuleDuplicateDialog has not rendered");
  }
  return props as CapturedDuplicateProps;
}
