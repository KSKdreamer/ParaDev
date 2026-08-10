/** @vitest-environment jsdom */

import { act } from "react";
import { createRoot, type Root } from "react-dom/client";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import type {
  DiagramDocument,
  DiagramMoveDelta,
} from "../diagramEditor/layoutModel";
import { createTranslator } from "../i18n";
import type {
  ModuleDiagramEditPayload,
  ModuleDiagramPayload,
} from "../services/paradev";
import type {
  ModuleCreateIntent,
  ProjectBrowserPayload,
  ProjectDiagramRelationship,
  ProjectTemplatesPayload,
} from "../types";
import type { ModuleEntity } from "./model";

const mocks = vi.hoisted(() => ({
  applyProjectDraft: vi.fn(),
  batchProps: [] as Array<Record<string, unknown>>,
  collectionProps: [] as Array<Record<string, unknown>>,
  desktopBackend: false,
  detailProps: [] as Array<Record<string, unknown>>,
  diagramPayloads: new Map<string, ModuleDiagramPayload>(),
  diagramProps: [] as Array<Record<string, unknown>>,
  editModuleDiagram: vi.fn(),
  listProps: [] as Array<Record<string, unknown>>,
  loadProjectCatalogStatus: vi.fn(),
  loadModuleDiagram: vi.fn(),
  nodeProps: [] as Array<Record<string, unknown>>,
  queryProjectCatalog: vi.fn(),
  readTextSource: vi.fn(),
  sourceUpdateProps: [] as Array<Record<string, unknown>>,
  sourceDraftRecoveryPathFromError: vi.fn(),
}));

vi.mock("../services/paradev", () => ({
  applyProjectDraft: mocks.applyProjectDraft,
  createModuleDraft: vi.fn(),
  editModuleDiagram: mocks.editModuleDiagram,
  hasDesktopBackend: () => mocks.desktopBackend,
  loadProjectCatalogStatus: mocks.loadProjectCatalogStatus,
  loadModuleDiagram: mocks.loadModuleDiagram,
  projectCatalogReadinessFromError: () => null,
  queryProjectCatalog: mocks.queryProjectCatalog,
  readTextSource: mocks.readTextSource,
  refreshProjectCatalog: vi.fn(),
  removeModule: vi.fn(),
  renameModule: vi.fn(),
  sourceDraftRecoveryPathFromError: mocks.sourceDraftRecoveryPathFromError,
}));

vi.mock("../diagramEditor/ProjectDiagramView", () => ({
  ProjectDiagramView: (props: Record<string, unknown>) => {
    mocks.diagramProps.push(props);
    return <div data-testid="project-diagram" />;
  },
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

vi.mock("./ModuleCreateDialog", () => ({
  ModuleCreateDialog: (props: Record<string, unknown>) => {
    mocks.batchProps.push(props);
    return <div data-testid="module-batch-dialog" />;
  },
}));

vi.mock("./CollectionCreateDialog", () => ({
  CollectionCreateDialog: (props: Record<string, unknown>) => {
    mocks.collectionProps.push(props);
    return <div data-testid="collection-create-dialog" />;
  },
}));

vi.mock("./DiagramNodeCreateDialog", () => ({
  DiagramNodeCreateDialog: (props: Record<string, unknown>) => {
    mocks.nodeProps.push(props);
    return <div data-testid="diagram-node-create-dialog" />;
  },
}));

vi.mock("./SourceUpdateReviewDialog", () => ({
  SourceUpdateReviewDialog: (props: Record<string, unknown>) => {
    mocks.sourceUpdateProps.push(props);
    return <div data-testid="source-update-review-dialog" />;
  },
}));

import { ModuleEditor } from "./ModuleEditor";
import {
  ModuleEditorSessionStore,
  moduleEditorSessionKey,
  type ModuleEditorBatchCreateState,
  type ModuleEditorCollectionCreateState,
  type ModuleEditorSourceUpdateState,
} from "./editorSessionStore";

const PROJECT_ROOT = "/workspace/projects/PIHC3";
const CHECKOUT_ROOT = "/workspace/checkouts/PIHC3";
const ENTITY_ID = "module:technology/TECH_ALPHA";
const BLOB_URL = "blob:technology-preview";
const TEXT_DRAFT = "technology = { cost = 2 }\n";

const templates: ProjectTemplatesPayload = {
  schema: "paradev.sdk.templates.v1",
  project_id: "PIHC3",
  profile: "hoi4",
  templates: [
    {
      id: "pihc3:technology/basic",
      title: "Technology",
      family: "technology",
      source: "project",
      args: {
        title: {
          required: false,
          default: "",
          advanced: false,
        },
      },
      files: ["def.pdx"],
    },
  ],
};

const mioTemplates: ProjectTemplatesPayload = {
  schema: "paradev.sdk.templates.v1",
  project_id: "PIHC3",
  profile: "hoi4",
  templates: [
    {
      id: "pihc3:military_industrial_organization/basic",
      title: "Military Industrial Organization",
      family: "military_industrial_organization",
      source: "project",
      args: {
        title: {
          required: true,
          default: "",
          advanced: false,
        },
      },
      files: [
        "common/military_industrial_organization/organizations/{object_id}.txt",
      ],
    },
  ],
};

const focusCollectionTemplates: ProjectTemplatesPayload = {
  schema: "paradev.sdk.templates.v1",
  project_id: "PIHC3",
  profile: "hoi4",
  source_roots: [
    {
      path: `${PROJECT_ROOT}/src`,
      relative_path: "src",
      default: true,
    },
  ],
  templates: [
    {
      id: "pihc3:focus-tree/basic",
      title: "Focus tree",
      family: "focus_tree",
      family_id: "focuses",
      kind: "collection",
      source: "project",
      authoring_ready: true,
      args: {
        country_tag: {
          required: true,
          default: "",
          advanced: false,
        },
        title: {
          required: true,
          default: "",
          advanced: false,
        },
      },
      files: ["tree.txt"],
    },
  ],
};

type CapturedListProps = {
  createBusy: boolean;
  createIntent: ModuleCreateIntent | null;
  createObjectId: string;
  createValues: Record<string, string>;
  onCreateObjectIdChange: (value: string) => void;
  onCreateValueChange: (name: string, value: string) => void;
  onOpenBatch: () => void;
};

type CapturedDetailProps = {
  applyBusy: boolean;
  entity: ModuleEntity | null;
  onImageDraft: (
    entityId: string,
    image: NonNullable<ModuleEntity["drafts"]["image"]>,
  ) => void;
  onTextDraft: (entityId: string, slot: string, value: string) => void;
};

type CapturedDiagramProps = {
  createNodeLabel?: string;
  diagramApplyBusy: boolean;
  diagramApplyError?: string;
  diagramChangedEntities?: Array<{
    id: string;
    path?: string;
    title?: string;
  }>;
  document: DiagramDocument;
  onDiagramApply?: () => void | Promise<void>;
  onDiagramCreateNode?: () => void;
  onDiagramDiscard?: () => void;
  onDiagramImportJson?: () => void;
  onDiagramPinAll?: () => void;
  onNodeAddDependency?: (targetId: string, sourceId: string) => void;
  onNodeAddReference?: (sourceId: string, targetId: string) => void;
  onNodeClearParent?: (nodeId: string) => void;
  onNodeInsertChild?: (nodeId: string) => void;
  onNodeMove?: (nodeId: string, delta: DiagramMoveDelta) => void;
  onNodeMoveRelayoutDescendants?: (
    nodeId: string,
    delta: DiagramMoveDelta,
  ) => void;
  onNodeRemoveDependency?: (targetId: string, sourceId: string) => void;
  onNodeRemoveOnly?: (nodeId: string) => void;
  onNodeRemoveReference?: (sourceId: string, targetId: string) => void;
  onNodeSetRelationship?: (
    relationship: ProjectDiagramRelationship,
    selectedNodeId: string,
    relatedNodeId: string,
    present: boolean,
  ) => void;
  onNodeOpenModule?: (nodeId: string, sourcePath?: string) => void;
  onNodeSelect?: (nodeId: string) => void;
  onNodeSetPosition?: (
    nodeId: string,
    position: { x: number; y: number },
  ) => void;
  onNodeSetParent?: (nodeId: string, parentId: string) => void;
  relationshipActions?: readonly ProjectDiagramRelationship[];
  onDiagramViewportSave?: (viewport: {
    x: number;
    y: number;
    zoom: number;
  }) => void;
  readOnly?: boolean;
  readOnlyReason?: string;
};

type CapturedBatchProps = {
  dialogText?: {
    guidance?: string;
    title: string;
  };
  initialState: ModuleEditorBatchCreateState | null;
  initialValues?: Record<string, string>;
  mode?: "batch" | "single";
  onApplied: (
    payload: import("../services/paradev").ModuleCreateBatchPayload,
  ) => void | Promise<void>;
  onDraftChange: (state: ModuleEditorBatchCreateState | null) => void;
};

type CapturedCollectionProps = {
  initialState: ModuleEditorCollectionCreateState | null;
  onDraftChange: (
    state: ModuleEditorCollectionCreateState | null
  ) => void;
};

type CapturedNodeProps = {
  authoring: {
    title: string;
  };
  contextValues: Record<string, unknown>;
  family: string;
  onApplied: (payload: ModuleDiagramEditPayload) => void | Promise<void>;
};

type CapturedSourceUpdateProps = {
  initialState: ModuleEditorSourceUpdateState;
  onApplied: (
    payload: import("../types").DraftApplyPayload,
  ) => void | Promise<void>;
  onClose: () => void;
};

type MountedEditor = {
  container: HTMLDivElement;
  mounted: boolean;
  root: Root;
};

const mountedEditors: MountedEditor[] = [];

beforeEach(() => {
  mocks.applyProjectDraft.mockReset();
  mocks.batchProps.length = 0;
  mocks.collectionProps.length = 0;
  mocks.desktopBackend = false;
  mocks.detailProps.length = 0;
  mocks.diagramPayloads.clear();
  mocks.diagramProps.length = 0;
  mocks.editModuleDiagram.mockReset();
  mocks.listProps.length = 0;
  mocks.loadProjectCatalogStatus.mockReset();
  mocks.loadProjectCatalogStatus.mockResolvedValue({
    schema: "paradev.hb.catalog-status.v1",
    project_id: "PIHC3",
    database: "",
    status: "missing",
    code: "catalog.missing",
  });
  mocks.loadModuleDiagram.mockReset();
  mocks.nodeProps.length = 0;
  mocks.loadModuleDiagram.mockImplementation(
    async (request: { projectRoot: string }) => {
      const payload = mocks.diagramPayloads.get(request.projectRoot);
      if (!payload) {
        throw new Error("Missing test diagram payload.");
      }
      return payload;
    },
  );
  mocks.queryProjectCatalog.mockReset();
  mocks.readTextSource.mockReset();
  mocks.sourceUpdateProps.length = 0;
  mocks.sourceDraftRecoveryPathFromError.mockReset();
  mocks.sourceDraftRecoveryPathFromError.mockReturnValue(null);
  (
    globalThis as typeof globalThis & {
      IS_REACT_ACT_ENVIRONMENT: boolean;
    }
  ).IS_REACT_ACT_ENVIRONMENT = true;
});

afterEach(() => {
  for (const mounted of mountedEditors.splice(0)) {
    unmountEditor(mounted);
  }
  vi.restoreAllMocks();
});

describe("ModuleEditor retained session lifecycle", () => {
  it("locks every view of one session while an authoring write is active", async () => {
    const store = new ModuleEditorSessionStore();
    const browser = browserForRoot(PROJECT_ROOT, "PIHC3");
    const moduleEditor = mountEditor(browser, store);
    const diagramEditor = mountEditor(browser, store, "diagram");
    await flushDiagramLoad();
    const key = moduleEditorSessionKey(PROJECT_ROOT, "technologies");
    let finishBusy: () => void = () => undefined;

    act(() => {
      finishBusy = store.beginBusy(key);
    });

    expect(latestListProps().createBusy).toBe(true);
    expect(latestDetailProps().applyBusy).toBe(true);
    expect(latestDiagramProps().diagramApplyBusy).toBe(true);
    expect(
      moduleEditor.container
        .querySelector(".module-editor")
        ?.hasAttribute("inert"),
    ).toBe(true);
    expect(
      diagramEditor.container
        .querySelector(".module-editor")
        ?.hasAttribute("inert"),
    ).toBe(false);
    expect(
      diagramEditor.container
        .querySelector(".diagram-editor-background")
        ?.hasAttribute("inert"),
    ).toBe(true);

    act(() => finishBusy());

    expect(latestListProps().createBusy).toBe(false);
    expect(latestDetailProps().applyBusy).toBe(false);
    expect(latestDiagramProps().diagramApplyBusy).toBe(false);
    expect(
      moduleEditor.container
        .querySelector(".module-editor")
        ?.hasAttribute("inert"),
    ).toBe(false);
    expect(
      diagramEditor.container
        .querySelector(".module-editor")
        ?.hasAttribute("inert"),
    ).toBe(false);
    expect(
      diagramEditor.container
        .querySelector(".diagram-editor-background")
        ?.hasAttribute("inert"),
    ).toBe(false);
  });

  it("preserves viewport continuity and blocks a stale source-backed draft", async () => {
    const store = new ModuleEditorSessionStore();
    const originalBrowser = browserForRoot(PROJECT_ROOT, "PIHC3");
    const refreshedBrowser = browserWithExtraTechnology(PROJECT_ROOT, "PIHC3");
    const mounted = mountEditor(originalBrowser, store, "diagram");
    await flushDiagramLoad();

    act(() => {
      latestDiagramProps().onDiagramViewportSave?.({
        x: 120,
        y: -40,
        zoom: 1.25,
      });
    });
    renderMountedEditor(mounted, refreshedBrowser, store, "diagram");
    await flushDiagramLoad();
    expect(latestDiagramProps().document.nodes).toHaveLength(2);
    expect(latestDiagramProps().document.viewport).toEqual({
      x: 120,
      y: -40,
      zoom: 1.25,
    });

    act(() => {
      latestDiagramProps().onNodeMove?.("TECH_ALPHA", {
        dx: 1,
        dy: 0,
      });
    });
    renderMountedEditor(
      mounted,
      browserWithExtraTechnology(PROJECT_ROOT, "PIHC3", true),
      store,
      "diagram",
    );
    await flushDiagramLoad();

    expect(latestDiagramProps().document.nodes).toHaveLength(2);
    expect(latestDiagramProps().onDiagramApply).toBeUndefined();
    expect(latestDiagramProps().onNodeMove).toBeTypeOf("function");
    expect(latestDiagramProps().diagramApplyError).toContain(
      "Project sources changed",
    );
  });

  it("routes technology diagram writes through the source-backed SDK plan", async () => {
    const store = new ModuleEditorSessionStore();
    const browser = browserWithMetadataSource(PROJECT_ROOT, "PIHC3");
    mocks.desktopBackend = true;
    const mounted = mountEditor(browser, store, "diagram");
    await flushDiagramLoad();

    expect(latestDiagramProps().onNodeMove).toBeTypeOf("function");
    expect(latestDiagramProps().onDiagramApply).toBeTypeOf("function");
    expect(mocks.readTextSource).not.toHaveBeenCalled();
    expect(mocks.applyProjectDraft).not.toHaveBeenCalled();

    mocks.editModuleDiagram
      .mockResolvedValueOnce({
        schema: "paradev.sdk.module_diagram_edit.v1",
        project_id: "PIHC3",
        blocked: false,
        written: false,
        plan_hash: "reviewed-plan",
        diagnostics: [],
      })
      .mockResolvedValueOnce({
        schema: "paradev.sdk.module_diagram_edit.v1",
        project_id: "PIHC3",
        blocked: false,
        written: true,
        applied: true,
        plan_hash: "reviewed-plan",
        diagnostics: [],
      });
    act(() => {
      latestDiagramProps().onNodeMove?.("TECH_ALPHA", {
        dx: 1,
        dy: 0,
      });
    });
    await act(async () => {
      await latestDiagramProps().onDiagramApply?.();
    });

    expect(mocks.editModuleDiagram).toHaveBeenCalledTimes(2);
    expect(mocks.editModuleDiagram.mock.calls[0]?.[0]).toMatchObject({
      family: "technology",
      positionIntents: [
        {
          technology_id: "TECH_ALPHA",
          x: 2,
          y: 1,
          source_revision: "sha256:TECH_ALPHA",
        },
      ],
    });
    expect(mocks.editModuleDiagram.mock.calls[1]?.[0]).toMatchObject({
      planHash: "reviewed-plan",
      write: true,
    });
    expect(mocks.applyProjectDraft).not.toHaveBeenCalled();

    unmountEditor(mounted);
    mountEditor(browser, store, "diagram");
    await flushDiagramLoad();
    expect(mocks.applyProjectDraft).not.toHaveBeenCalled();
  });

  it("renders and applies an external Registry graph without a family switch", async () => {
    const store = new ModuleEditorSessionStore();
    const browser = genericGraphBrowserForRoot(PROJECT_ROOT, "PIHC3");
    mocks.desktopBackend = true;
    const mounted = mountGenericGraphEditor(browser, store);
    await flushDiagramLoad();

    expect(mocks.loadModuleDiagram).toHaveBeenCalledWith({
      projectRoot: PROJECT_ROOT,
      family: "external_graph",
      profile: "hoi4",
    });
    expect(latestDiagramProps().document.nodes).toMatchObject([
      { id: "EXT_A", title: "External A", x: 1, y: 2 },
      { id: "EXT_B", title: "External B", x: 4, y: 2 },
    ]);
    expect(latestDiagramProps().onNodeMove).toBeTypeOf("function");
    expect(latestDiagramProps().onNodeSetRelationship).toBeTypeOf("function");
    expect(latestDiagramProps().onDiagramApply).toBeTypeOf("function");

    mocks.editModuleDiagram
      .mockResolvedValueOnce({
        schema: "paradev.sdk.module_diagram_edit.v1",
        project_id: "PIHC3",
        blocked: false,
        written: false,
        plan_hash: "external-plan",
        diagnostics: [],
      })
      .mockResolvedValueOnce({
        schema: "paradev.sdk.module_diagram_edit.v1",
        project_id: "PIHC3",
        blocked: false,
        written: true,
        plan_hash: "external-plan",
        diagnostics: [],
      });
    act(() => {
      latestDiagramProps().onNodeMove?.("EXT_A", { dx: 1, dy: 0 });
    });
    act(() => {
      const diagram = latestDiagramProps();
      diagram.onNodeSetRelationship?.(
        diagram.relationshipActions![0],
        "EXT_A",
        "EXT_B",
        true,
      );
    });
    await act(async () => {
      await latestDiagramProps().onDiagramApply?.();
    });

    expect(mocks.editModuleDiagram.mock.calls[0]?.[0]).toMatchObject({
      family: "external_graph",
      positionIntents: [
        {
          node_id: "EXT_A",
          source_revision: "sha256:EXT_A",
          x: 2,
          y: 2,
        },
      ],
      edgeIntents: [
        {
          kind: "custom_link",
          present: true,
          source_id: "EXT_A",
          source_revision: "sha256:EXT_A",
          target_id: "EXT_B",
        },
      ],
    });
    expect(mocks.editModuleDiagram.mock.calls[1]?.[0]).toMatchObject({
      planHash: "external-plan",
      write: true,
    });

    unmountEditor(mounted);
  });

  it("retains source recovery data when a tree edit cannot recover automatically", async () => {
    const store = new ModuleEditorSessionStore();
    const browser = browserWithMetadataSource(PROJECT_ROOT, "PIHC3");
    const onBatchRecoveryPathsChange = vi.fn();
    const recoveryPath =
      `${PROJECT_ROOT}/.paradev/source-draft-transaction`;
    mocks.desktopBackend = true;
    mocks.sourceDraftRecoveryPathFromError.mockReturnValue(recoveryPath);
    const mounted = mountEditor(browser, store, "diagram", {
      onBatchRecoveryPathsChange,
    });
    await flushDiagramLoad();
    mocks.editModuleDiagram
      .mockResolvedValueOnce({
        schema: "paradev.sdk.module_diagram_edit.v1",
        project_id: "PIHC3",
        blocked: false,
        written: false,
        plan_hash: "reviewed-plan",
        diagnostics: [],
      })
      .mockRejectedValueOnce(
        new Error(
          "Source draft crash recovery stopped because a file changed outside ParaDev.",
        ),
      );
    act(() => {
      latestDiagramProps().onNodeMove?.("TECH_ALPHA", {
        dx: 1,
        dy: 0,
      });
    });

    await act(async () => {
      await latestDiagramProps().onDiagramApply?.();
    });

    expect(onBatchRecoveryPathsChange).toHaveBeenCalledWith([
      recoveryPath,
    ]);
    expect(latestDiagramProps().diagramApplyError).toBe(
      "ParaDev preserved recovery data because project files changed during Apply. Do not apply another edit yet; open the recovery folder above and review the preserved files.",
    );
    expect(latestDiagramProps().document.nodes[0]?.x).toBe(2);
    unmountEditor(mounted);
  });

  it("opens registered single-module Technology creation from the graph", async () => {
    const store = new ModuleEditorSessionStore();
    const browser = browserForRoot(PROJECT_ROOT, "PIHC3");
    mocks.desktopBackend = true;
    mountEditor(browser, store, "diagram");
    await flushDiagramLoad();

    expect(latestDiagramProps()).toMatchObject({
      createNodeLabel: "Create in Technologies",
    });
    expect(latestDiagramProps().onDiagramCreateNode).toBeTypeOf("function");

    act(() => latestDiagramProps().onDiagramCreateNode?.());

    expect(latestBatchProps()).toMatchObject({
      dialogText: {
        title: "Create in Technologies",
      },
      initialValues: {
        dependencies: "dependencies = {\n\t\t\tTECH_ALPHA = 1\n\t\t}",
        folder: "infantry_folder",
        x: "1",
        y: "3",
      },
      mode: "single",
    });
    expect(latestBatchProps().dialogText?.guidance).toContain(
      "active project extension",
    );

    await act(async () => {
      await latestBatchProps().onApplied({
        schema: "paradev.sdk.module_batch.v1",
        project_id: "PIHC3",
        source_root: `${PROJECT_ROOT}/src`,
        plan_hash: "a".repeat(64),
        blocked: false,
        applied: true,
        written: true,
        requested_count: 1,
        counts: {
          create: 0,
          created: 1,
          unchanged: 0,
          blocked: 0,
        },
        diagnostics: [],
        modules: [
          {
            status: "created",
            object_id: "TECH_NEW",
            module_id: "technology/TECH_NEW",
          },
        ],
      });
    });
    await flushDiagramLoad();

    expect(mocks.loadModuleDiagram).toHaveBeenCalledTimes(2);
  });

  it("opens registered in-place MIO trait creation from the selected graph node", async () => {
    const store = new ModuleEditorSessionStore();
    const browser = mioBrowserForRoot(PROJECT_ROOT, "PIHC3");
    mocks.desktopBackend = true;
    mountMioEditor(browser, store, undefined, "", mioTemplates);
    await flushDiagramLoad();

    act(() => latestDiagramProps().onNodeSelect?.("C01_ORG::trait::ROOT"));
    expect(latestDiagramProps()).toMatchObject({
      createNodeLabel: "Add MIO trait",
    });
    expect(latestDiagramProps().onDiagramCreateNode).toBeTypeOf("function");
    act(() => latestDiagramProps().onDiagramCreateNode?.());

    expect(latestNodeProps()).toMatchObject({
      authoring: {
        title: "Add MIO trait",
      },
      contextValues: {
        organization_id: "C01_ORG",
        parent_trait_id: "ROOT",
        source_path:
          "src/modules/military_industrial_organization/C01/common/military_industrial_organization/organizations/C01.txt",
        source_revision: "sha256:mio-source",
        x: 0,
        y: 1,
      },
      family: "military_industrial_organization",
    });
    expect(mocks.batchProps).toHaveLength(0);

    await act(async () => {
      await latestNodeProps().onApplied({
        schema: "paradev.sdk.module_diagram_edit.v1",
        provider_schema: "paradev.hoi4.mio-trait-creation-plan.v1",
        project_id: "PIHC3",
        project_root: PROJECT_ROOT,
        profile: "hoi4",
        family: "military_industrial_organization",
        status: "applied",
        plan_hash: "b".repeat(64),
        blocked: false,
        applied: true,
        written: true,
        drafts: [],
        source_replacements: [],
        diagnostics: [],
        files: [],
        created_scope_id: "C01_ORG",
        created_node_id: "C01_ORG::trait::NEW_TRAIT",
      });
    });
    await flushDiagramLoad();

    expect(mocks.loadModuleDiagram).toHaveBeenCalledTimes(2);
  });

  it("loads and applies Focus positions and relations through the generic source-backed bridge", async () => {
    const store = new ModuleEditorSessionStore();
    const browser = focusBrowserForRoot(PROJECT_ROOT, "PIHC3");
    mocks.desktopBackend = true;
    const mounted = mountFocusEditor(browser, store);
    await flushDiagramLoad();

    expect(mocks.loadModuleDiagram).toHaveBeenCalledWith({
      projectRoot: PROJECT_ROOT,
      family: "focus_tree",
      profile: "hoi4",
    });
    const loaded = latestDiagramProps();
    expect(loaded.document.nodes.map((node) => node.id)).toEqual([
      "FOCUS_CHILD",
      "FOCUS_OTHER",
      "FOCUS_ROOT",
    ]);
    expect(
      loaded.document.nodes.some((node) => node.id === "LEGACY_METADATA_ONLY"),
    ).toBe(false);
    expect(
      loaded.document.nodes.find((node) => node.id === "FOCUS_CHILD"),
    ).toMatchObject({
      mode: "relative",
      parentId: "FOCUS_ROOT",
      dx: 2,
      dy: 1,
    });
    expect(loaded.onNodeMove).toBeTypeOf("function");
    expect(loaded.onNodeAddDependency).toBeUndefined();
    expect(loaded.onNodeAddReference).toBeUndefined();
    expect(loaded.onNodeRemoveDependency).toBeUndefined();
    expect(loaded.onNodeRemoveReference).toBeUndefined();
    expect(loaded.onNodeSetRelationship).toBeTypeOf("function");
    expect(loaded.relationshipActions?.map((action) => action.kind)).toEqual([
      "prerequisite",
      "mutually_exclusive",
    ]);
    expect(loaded.onDiagramApply).toBeTypeOf("function");
    expect(loaded.onNodeClearParent).toBeUndefined();
    expect(loaded.onNodeInsertChild).toBeUndefined();
    expect(loaded.onNodeMoveRelayoutDescendants).toBeUndefined();
    expect(loaded.onNodeRemoveOnly).toBeUndefined();
    expect(loaded.onNodeSetParent).toBeUndefined();

    mocks.editModuleDiagram
      .mockResolvedValueOnce({
        schema: "paradev.sdk.module_diagram_edit.v1",
        project_id: "PIHC3",
        blocked: false,
        written: false,
        plan_hash: "focus-reviewed-plan",
        diagnostics: [],
      })
      .mockResolvedValueOnce({
        schema: "paradev.sdk.module_diagram_edit.v1",
        project_id: "PIHC3",
        blocked: false,
        written: true,
        applied: true,
        plan_hash: "focus-reviewed-plan",
        diagnostics: [],
      });
    act(() => {
      latestDiagramProps().onNodeMove?.("FOCUS_CHILD", {
        dx: 1,
        dy: -1,
      });
    });
    act(() => {
      latestDiagramProps().onNodeSetRelationship?.(
        loaded.relationshipActions![0],
        "FOCUS_CHILD",
        "FOCUS_ROOT",
        false,
      );
    });
    act(() => {
      latestDiagramProps().onNodeSetRelationship?.(
        loaded.relationshipActions![1],
        "FOCUS_CHILD",
        "FOCUS_OTHER",
        false,
      );
    });
    act(() => {
      latestDiagramProps().onNodeSetRelationship?.(
        loaded.relationshipActions![1],
        "FOCUS_ROOT",
        "FOCUS_OTHER",
        true,
      );
    });

    expect(latestDiagramProps().diagramChangedEntities).toEqual([
      {
        id: "FOCUS_CHILD",
        path: "src/modules/focus_tree/ALPHA_TREE/def.txt",
        title: "FOCUS CHILD",
      },
      {
        id: "FOCUS_OTHER",
        path: "src/modules/focus_tree/ALPHA_TREE/def.txt",
        title: "FOCUS OTHER",
      },
      {
        id: "FOCUS_ROOT",
        path: "src/modules/focus_tree/ALPHA_TREE/def.txt",
        title: "FOCUS ROOT",
      },
    ]);
    await act(async () => {
      await latestDiagramProps().onDiagramApply?.();
    });

    expect(mocks.editModuleDiagram).toHaveBeenCalledTimes(2);
    expect(mocks.editModuleDiagram.mock.calls[0]?.[0]).toEqual({
      projectRoot: PROJECT_ROOT,
      family: "focus_tree",
      profile: "hoi4",
      positionIntents: [
        {
          focus_id: "FOCUS_CHILD",
          x: 3,
          y: 0,
          source_revision: "sha256:alpha",
        },
      ],
      edgeIntents: [
        {
          kind: "prerequisite",
          source_id: "FOCUS_ROOT",
          target_id: "FOCUS_CHILD",
          present: false,
          source_revision: "sha256:alpha",
        },
        {
          kind: "mutually_exclusive",
          source_id: "FOCUS_CHILD",
          target_id: "FOCUS_OTHER",
          present: false,
          source_revision: "sha256:mutex-review",
        },
        {
          kind: "mutually_exclusive",
          source_id: "FOCUS_OTHER",
          target_id: "FOCUS_ROOT",
          present: true,
          source_revision: "sha256:alpha",
        },
      ],
    });
    expect(mocks.editModuleDiagram.mock.calls[1]?.[0]).toMatchObject({
      family: "focus_tree",
      planHash: "focus-reviewed-plan",
      write: true,
    });
    expect(mocks.readTextSource).not.toHaveBeenCalled();
    expect(mocks.applyProjectDraft).not.toHaveBeenCalled();

    unmountEditor(mounted);
  });

  it("loads and applies exact PIHC3 MIO positions and provider relationships", async () => {
    const store = new ModuleEditorSessionStore();
    const browser = mioBrowserForRoot(PROJECT_ROOT, "PIHC3");
    const onOpenModuleEntity = vi.fn();
    mocks.desktopBackend = true;
    const mounted = mountMioEditor(browser, store, onOpenModuleEntity);

    await flushDiagramLoad();

    expect(mocks.loadModuleDiagram).toHaveBeenCalledWith({
      projectRoot: PROJECT_ROOT,
      family: "military_industrial_organization",
      profile: "hoi4",
    });
    const props = latestDiagramProps();
    expect(props.document.nodes.map((node) => node.id)).toEqual([
      "C01_ORG::trait::CHILD",
      "C01_ORG::trait::ROOT",
    ]);
    expect(props.document.edges).toEqual([
      {
        id: "relative_position:C01_ORG::trait::ROOT->C01_ORG::trait::CHILD",
        kind: "tree",
        label: "Relative position",
        relationshipKind: "relative_position",
        source: "C01_ORG::trait::ROOT",
        target: "C01_ORG::trait::CHILD",
      },
    ]);
    expect(props.readOnly).toBe(false);
    expect(props.onDiagramApply).toBeTypeOf("function");
    expect(props.onDiagramImportJson).toBeUndefined();
    expect(props.onDiagramPinAll).toBeUndefined();
    expect(props.onNodeAddDependency).toBeUndefined();
    expect(props.onNodeMove).toBeTypeOf("function");
    expect(props.onNodeMoveRelayoutDescendants).toBeUndefined();
    expect(props.onNodeRemoveDependency).toBeUndefined();
    expect(props.onNodeSetRelationship).toBeTypeOf("function");
    expect(props.relationshipActions?.map((action) => action.kind)).toEqual([
      "relative_position",
      "any_parent",
    ]);
    expect(props.onNodeSetPosition).toBeTypeOf("function");
    const exactSourcePath =
      "src/modules/military_industrial_organization/C01/common/military_industrial_organization/organizations/C01.txt";
    act(() => {
      props.onNodeOpenModule?.("C01_ORG::trait::CHILD", exactSourcePath);
    });
    expect(onOpenModuleEntity).toHaveBeenCalledWith({
      entityId: "module:mio/C01",
      familyId: "military-industrial-organizations",
      sourcePath: exactSourcePath,
    });

    mocks.editModuleDiagram
      .mockResolvedValueOnce({
        schema: "paradev.sdk.module_diagram_edit.v1",
        project_id: "PIHC3",
        blocked: false,
        written: false,
        plan_hash: "mio-reviewed-plan",
        diagnostics: [],
      })
      .mockResolvedValueOnce({
        schema: "paradev.sdk.module_diagram_edit.v1",
        project_id: "PIHC3",
        blocked: false,
        written: true,
        applied: true,
        plan_hash: "mio-reviewed-plan",
        diagnostics: [],
      });
    act(() => {
      latestDiagramProps().onNodeMove?.("C01_ORG::trait::CHILD", {
        dx: 1,
        dy: -1,
      });
    });
    act(() => {
      latestDiagramProps().onNodeSetRelationship?.(
        props.relationshipActions![1],
        "C01_ORG::trait::CHILD",
        "C01_ORG::trait::ROOT",
        true,
      );
    });
    expect(latestDiagramProps().diagramChangedEntities).toEqual([
      {
        id: "C01_ORG::trait::CHILD",
        path: "src/modules/military_industrial_organization/C01/common/military_industrial_organization/organizations/C01.txt",
        title: "Child trait",
      },
      {
        id: "C01_ORG::trait::ROOT",
        path: "src/modules/military_industrial_organization/C01/common/military_industrial_organization/organizations/C01.txt",
        title: "Root trait",
      },
    ]);
    await act(async () => {
      await latestDiagramProps().onDiagramApply?.();
    });

    expect(mocks.editModuleDiagram).toHaveBeenCalledTimes(2);
    expect(mocks.editModuleDiagram.mock.calls[0]?.[0]).toEqual({
      projectRoot: PROJECT_ROOT,
      family: "military_industrial_organization",
      profile: "hoi4",
      positionIntents: [
        {
          organization_id: "C01_ORG",
          trait_id: "CHILD",
          x: 1,
          y: 0,
          source_revision: "sha256:mio-source",
        },
      ],
      edgeIntents: [
        {
          kind: "any_parent",
          organization_id: "C01_ORG",
          present: true,
          source_id: "ROOT",
          source_revision: "sha256:mio-source",
          target_id: "CHILD",
        },
      ],
    });
    expect(mocks.editModuleDiagram.mock.calls[1]?.[0]).toMatchObject({
      family: "military_industrial_organization",
      planHash: "mio-reviewed-plan",
      write: true,
    });
    expect(mocks.applyProjectDraft).not.toHaveBeenCalled();
    expect(mocks.readTextSource).not.toHaveBeenCalled();

    unmountEditor(mounted);
  });

  it("scopes MIO editing to one localized organization and blocks dirty switches", async () => {
    const store = new ModuleEditorSessionStore();
    const browser = mioBrowserForRoot(PROJECT_ROOT, "PIHC3");
    const mounted = mountMioEditor(browser, store);

    await flushDiagramLoad();

    const scope = mounted.container.querySelector<HTMLSelectElement>(
      'select[aria-label="Military Industrial Organization diagram scope"]',
    );
    expect(scope).not.toBeNull();
    expect(
      [...(scope?.options ?? [])].map((option) => ({
        text: option.text,
        value: option.value,
      })),
    ).toEqual([
      {
        text: "Canterlot Works — C01_ORG",
        value: "C01_ORG",
      },
      {
        text: "Canterlot Engines — C01_SECOND",
        value: "C01_SECOND",
      },
    ]);
    expect(latestDiagramProps().document.nodes.map((node) => node.id)).toEqual([
      "C01_ORG::trait::CHILD",
      "C01_ORG::trait::ROOT",
    ]);

    act(() => {
      latestDiagramProps().onNodeMove?.("C01_ORG::trait::CHILD", {
        dx: 1,
        dy: 0,
      });
    });
    expect(scope?.disabled).toBe(false);
    act(() => {
      if (scope) {
        scope.value = "C01_SECOND";
        scope.dispatchEvent(new Event("change", { bubbles: true }));
      }
    });
    expect(latestDiagramProps().document.nodes.map((node) => node.id)).toEqual([
      "C01_SECOND::trait::CHILD",
      "C01_SECOND::trait::ROOT",
    ]);

    act(() => {
      latestDiagramProps().onNodeMove?.("C01_SECOND::trait::CHILD", {
        dx: 1,
        dy: 0,
      });
    });
    expect(scope?.disabled).toBe(false);
    act(() => {
      if (scope) {
        scope.value = "C01_ORG";
        scope.dispatchEvent(new Event("change", { bubbles: true }));
      }
    });
    expect(latestDiagramProps().document.nodes.map((node) => node.id)).toEqual([
      "C01_ORG::trait::CHILD",
      "C01_ORG::trait::ROOT",
    ]);
    expect(
      latestDiagramProps().document.nodes.find(
        (node) => node.id === "C01_ORG::trait::CHILD",
      )?.dx,
    ).toBe(1);

    act(() => {
      if (scope) {
        scope.value = "C01_SECOND";
        scope.dispatchEvent(new Event("change", { bubbles: true }));
      }
    });
    expect(
      latestDiagramProps().document.nodes.find(
        (node) => node.id === "C01_SECOND::trait::CHILD",
      )?.dx,
    ).toBe(1);
    act(() => {
      latestDiagramProps().onDiagramDiscard?.();
    });
    act(() => {
      if (scope) {
        scope.value = "C01_ORG";
        scope.dispatchEvent(new Event("change", { bubbles: true }));
      }
    });
    expect(latestDiagramProps().document.nodes.map((node) => node.id)).toEqual([
      "C01_ORG::trait::CHILD",
      "C01_ORG::trait::ROOT",
    ]);
    expect(
      latestDiagramProps().document.nodes.find(
        (node) => node.id === "C01_ORG::trait::CHILD",
      )?.dx,
    ).toBe(1);
    act(() => {
      latestDiagramProps().onDiagramDiscard?.();
    });
  });

  it("preserves a sibling MIO draft as stale after applying a shared source file", async () => {
    const store = new ModuleEditorSessionStore();
    const browser = mioBrowserForRoot(PROJECT_ROOT, "PIHC3");
    mocks.desktopBackend = true;
    const mounted = mountMioEditor(browser, store);

    await flushDiagramLoad();

    const scope = mounted.container.querySelector<HTMLSelectElement>(
      'select[aria-label="Military Industrial Organization diagram scope"]',
    );
    act(() => {
      latestDiagramProps().onNodeMove?.("C01_ORG::trait::CHILD", {
        dx: 1,
        dy: 0,
      });
      if (scope) {
        scope.value = "C01_SECOND";
        scope.dispatchEvent(new Event("change", { bubbles: true }));
      }
    });
    act(() => {
      latestDiagramProps().onNodeMove?.("C01_SECOND::trait::CHILD", {
        dx: 1,
        dy: 0,
      });
    });

    mocks.editModuleDiagram
      .mockResolvedValueOnce({
        schema: "paradev.sdk.module_diagram_edit.v1",
        project_id: "PIHC3",
        blocked: false,
        written: false,
        plan_hash: "mio-shared-source-plan",
        diagnostics: [],
      })
      .mockImplementationOnce(async () => {
        const updated = mioDiagramForBrowser(browser);
        updated.nodes = updated.nodes.map((node) => ({
          ...node,
          source_revision: "sha256:mio-source-updated",
        }));
        mocks.diagramPayloads.set(browser.root, updated);
        return {
          schema: "paradev.sdk.module_diagram_edit.v1",
          project_id: "PIHC3",
          blocked: false,
          written: true,
          applied: true,
          plan_hash: "mio-shared-source-plan",
          diagnostics: [],
        };
      });

    await act(async () => {
      await latestDiagramProps().onDiagramApply?.();
    });
    await flushDiagramLoad();

    act(() => {
      if (scope) {
        scope.value = "C01_ORG";
        scope.dispatchEvent(new Event("change", { bubbles: true }));
      }
    });

    expect(
      latestDiagramProps().document.nodes.find(
        (node) => node.id === "C01_ORG::trait::CHILD",
      )?.dx,
    ).toBe(1);
    expect(latestDiagramProps().onDiagramApply).toBeUndefined();
    expect(latestDiagramProps().diagramApplyError).toContain(
      "Project sources changed after this diagram draft began",
    );
  });

  it("shows an honest empty MIO tree state for modules that own no diagrammable organization", async () => {
    const store = new ModuleEditorSessionStore();
    const browser = mioBrowserForRoot(PROJECT_ROOT, "PIHC3");
    const policyBrowser: ProjectBrowserPayload = {
      ...browser,
      families: browser.families.map((family) =>
        family.diagram
          ? {
              ...family,
              diagram: {
                ...family.diagram,
                initial_scope: "selected-entity",
              },
            }
          : family,
      ),
      items: browser.items.map((item) => ({
        ...item,
        id: "module:mio/POLICIES",
        module_id: "mio/POLICIES",
        object_id: "POLICIES",
        title: "MIO policies",
      })),
    };
    mountMioEditor(policyBrowser, store, undefined, "module:mio/POLICIES");

    await flushDiagramLoad();

    expect(latestDiagramProps().document.nodes).toEqual([]);
    expect(latestDiagramProps().document.edges).toEqual([]);
    expect(document.body.textContent).toContain(
      "This module contains no MIO organization with a trait tree.",
    );
    expect(
      document.querySelector(
        'select[aria-label="Military Industrial Organization diagram scope"]',
      ),
    ).toBeNull();
  });

  it("keeps project-wide MIO diagrams reachable when the implicit first module owns no tree", async () => {
    const store = new ModuleEditorSessionStore();
    const browser = mioBrowserForRoot(PROJECT_ROOT, "PIHC3");
    const globalBrowser: ProjectBrowserPayload = {
      ...browser,
      items: browser.items.map((item) => ({
        ...item,
        id: "module:mio/AI_BONUS_WEIGHTS",
        module_id: "mio/AI_BONUS_WEIGHTS",
        object_id: "AI_BONUS_WEIGHTS",
        title: "AI bonus weights",
      })),
    };
    const mounted = mountMioEditor(
      globalBrowser,
      store,
      undefined,
      "module:mio/AI_BONUS_WEIGHTS",
    );

    await flushDiagramLoad();

    expect(latestDiagramProps().document.nodes.map((node) => node.id)).toEqual([
      "C01_ORG::trait::CHILD",
      "C01_ORG::trait::ROOT",
    ]);
    const scope = mounted.container.querySelector<HTMLSelectElement>(
      'select[aria-label="Military Industrial Organization diagram scope"]',
    );
    expect([...(scope?.options ?? [])].map((option) => option.value)).toEqual([
      "C01_ORG",
      "C01_SECOND",
    ]);
    expect(document.body.textContent).not.toContain(
      "This module contains no MIO organization with a trait tree.",
    );
    expect(document.body.textContent).toContain(
      "2 organizations in this project",
    );
  });

  it("hydrates a reused editor scope before normalizing its create form", () => {
    const store = new ModuleEditorSessionStore();
    const primaryKey = moduleEditorSessionKey(PROJECT_ROOT, "technologies");
    const checkoutKey = moduleEditorSessionKey(CHECKOUT_ROOT, "technologies");
    store.setInlineCreate(primaryKey, {
      objectId: "PRIMARY_DRAFT",
      showAdvanced: false,
      templateId: "pihc3:technology/basic",
      values: { title: "Primary draft" },
    });
    store.setInlineCreate(checkoutKey, {
      objectId: "CHECKOUT_DRAFT",
      showAdvanced: true,
      templateId: "pihc3:technology/basic",
      values: { title: "Checkout draft" },
    });

    const mounted = mountEditor(browserForRoot(PROJECT_ROOT, "PIHC3"), store);
    expect(latestListProps()).toMatchObject({
      createObjectId: "PRIMARY_DRAFT",
      createValues: { title: "Primary draft" },
    });

    renderMountedEditor(
      mounted,
      browserForRoot(CHECKOUT_ROOT, "PIHC3_CHECKOUT"),
      store,
      "module",
      null,
    );
    expect(latestListProps()).toMatchObject({
      createObjectId: "CHECKOUT_DRAFT",
      createValues: { title: "Checkout draft" },
    });
    expect(store.read(primaryKey)?.inlineCreate?.objectId).toBe(
      "PRIMARY_DRAFT",
    );
    expect(store.read(checkoutKey)?.inlineCreate?.objectId).toBe(
      "CHECKOUT_DRAFT",
    );

    renderMountedEditor(
      mounted,
      browserForRoot(CHECKOUT_ROOT, "PIHC3_CHECKOUT"),
      store,
    );
    renderMountedEditor(mounted, browserForRoot(PROJECT_ROOT, "PIHC3"), store);
    expect(latestListProps()).toMatchObject({
      createObjectId: "PRIMARY_DRAFT",
      createValues: { title: "Primary draft" },
    });
    expect(store.read(checkoutKey)?.inlineCreate).toMatchObject({
      objectId: "CHECKOUT_DRAFT",
      values: { title: "Checkout draft" },
    });
  });

  it("opens a batch intent on an already-mounted family and consumes its nonce once", () => {
    const store = new ModuleEditorSessionStore();
    const browser = browserForRoot(PROJECT_ROOT, "PIHC3");
    const mounted = mountEditor(browser, store);
    const onIntentConsumed = vi.fn();
    const intent: ModuleCreateIntent = {
      familyId: "technologies",
      mode: "batch",
      nonce: 41,
    };

    expect(mocks.batchProps).toHaveLength(0);

    renderMountedEditor(mounted, browser, store, "module", templates, {
      moduleCreateIntent: intent,
      onModuleCreateIntentConsumed: onIntentConsumed,
    });

    expect(mocks.batchProps.length).toBeGreaterThan(0);
    expect(latestListProps().createIntent).toBeNull();
    expect(onIntentConsumed).toHaveBeenCalledOnce();
    expect(onIntentConsumed).toHaveBeenCalledWith(41);

    renderMountedEditor(mounted, browser, store, "module", templates, {
      moduleCreateIntent: { ...intent },
      onModuleCreateIntentConsumed: onIntentConsumed,
    });

    expect(latestListProps().createIntent).toBeNull();
    expect(onIntentConsumed).toHaveBeenCalledOnce();
  });

  it("opens an AI collection intent from retained state and consumes its nonce once", () => {
    mocks.desktopBackend = true;
    const store = new ModuleEditorSessionStore();
    const browser = focusBrowserForRoot(PROJECT_ROOT, "PIHC3");
    const key = moduleEditorSessionKey(PROJECT_ROOT, "focuses");
    const retained: ModuleEditorCollectionCreateState = {
      open: true,
      pristineSourceRoot: `${PROJECT_ROOT}/src`,
      pristineTemplateId: "pihc3:focus-tree/basic",
      templateId: "pihc3:focus-tree/basic",
      collectionId: "C99_AI_REVIEW",
      values: { country_tag: "C99", title: "AI Review Tree" },
      showAdvanced: false,
      sourceRoot: `${PROJECT_ROOT}/src`,
    };
    store.setCollectionCreate(key, retained);
    const onIntentConsumed = vi.fn();
    const intent: ModuleCreateIntent = {
      familyId: "focuses",
      mode: "collection",
      nonce: 42,
    };

    mountFocusEditor(browser, store, focusCollectionTemplates, {
      moduleCreateIntent: intent,
      onModuleCreateIntentConsumed: onIntentConsumed,
    });

    expect(mocks.collectionProps.length).toBeGreaterThan(0);
    expect(
      (mocks.collectionProps.at(-1) as CapturedCollectionProps).initialState
    ).toEqual(retained);
    expect(onIntentConsumed).toHaveBeenCalledOnce();
    expect(onIntentConsumed).toHaveBeenCalledWith(42);
  });

  it("opens a retained AI source plan, consumes its intent, and refreshes after apply", async () => {
    const store = new ModuleEditorSessionStore();
    const browser = browserForRoot(PROJECT_ROOT, "PIHC3");
    const key = moduleEditorSessionKey(PROJECT_ROOT, "technologies");
    const retained: ModuleEditorSourceUpdateState = {
      open: true,
      requests: [
        {
          source_path: "src/modules/technology/TECH_ALPHA/def.pdx",
          module_id: "technology/TECH_ALPHA",
          values: { cost: 2 },
          control_labels: { cost: "Research cost" },
        },
      ],
      plan: {
        schema: "paradev.source-form-update-batch.v1",
        projectId: "PIHC3",
        changed: true,
        counts: { requested: 1, changed: 1, unchanged: 0 },
        updates: [],
        sourceEdits: [],
      },
    };
    store.setSourceUpdate(key, retained);
    const mounted = mountEditor(browser, store);
    const onIntentConsumed = vi.fn();
    const onProjectRefresh = vi.fn().mockResolvedValue(undefined);

    renderMountedEditor(mounted, browser, store, "module", templates, {
      moduleCreateIntent: {
        familyId: "technologies",
        mode: "source-update",
        nonce: 43,
      },
      onModuleCreateIntentConsumed: onIntentConsumed,
      onProjectRefresh,
    });

    expect(mocks.sourceUpdateProps.length).toBeGreaterThan(0);
    expect(
      (mocks.sourceUpdateProps.at(-1) as CapturedSourceUpdateProps).initialState,
    ).toEqual(retained);
    expect(latestListProps().createIntent).toBeNull();
    expect(onIntentConsumed).toHaveBeenCalledOnce();
    expect(onIntentConsumed).toHaveBeenCalledWith(43);

    await act(async () => {
      await (
        mocks.sourceUpdateProps.at(-1) as CapturedSourceUpdateProps
      ).onApplied({
        schema: "paradev.rest.draft_apply.v1",
        project_id: "PIHC3",
        written: true,
        files: [],
      });
    });

    expect(store.read(key)?.sourceUpdate).toBeNull();
    expect(store.getSnapshot().sessions).toEqual([]);
    expect(onProjectRefresh).toHaveBeenCalledWith(PROJECT_ROOT, "PIHC3");
  });

  it("retains one root's authoring state across module and diagram remounts", async () => {
    const store = new ModuleEditorSessionStore();
    const browser = browserForRoot(PROJECT_ROOT, "PIHC3");
    const primaryBrowser = {
      ...browser,
      items: browser.items.map((item) => ({
        ...item,
        source_count: item.source_count + 1,
        sources: [
          ...item.sources,
          {
            slot: "preview",
            name: "icon.png",
            path: `${item.root}/icon.png`,
            relative_path: `${item.relative_root}/icon.png`,
            extension: "png",
          },
        ],
      })),
    };
    const primaryKey = moduleEditorSessionKey(PROJECT_ROOT, "technologies");
    const checkoutKey = moduleEditorSessionKey(CHECKOUT_ROOT, "technologies");
    const revokeObjectUrl = vi
      .spyOn(URL, "revokeObjectURL")
      .mockImplementation(() => undefined);

    let mounted = mountEditor(primaryBrowser, store);

    act(() => {
      latestDetailProps().onTextDraft(ENTITY_ID, "def", TEXT_DRAFT);
    });
    act(() => {
      latestListProps().onCreateObjectIdChange("TECH_DRAFT");
    });
    act(() => {
      latestListProps().onCreateValueChange("title", "Retained technology");
    });
    act(() => {
      latestDetailProps().onImageDraft(ENTITY_ID, {
        contentBase64: "iVBORw0KGgo=",
        fileName: "icon.png",
        path: "src/modules/technology/TECH_ALPHA/icon.png",
        previewUrl: BLOB_URL,
      });
    });
    act(() => {
      latestListProps().onOpenBatch();
    });
    const batchState: ModuleEditorBatchCreateState = {
      open: true,
      pristineSourceRoot: `${PROJECT_ROOT}/src`,
      pristineTemplateId: "pihc3:technology/basic",
      rows: [
        {
          key: 1,
          objectId: "TECH_BATCH",
          templateId: "pihc3:technology/basic",
          values: { title: "Retained batch technology" },
        },
      ],
      showAdvanced: true,
      sourceRoot: `${PROJECT_ROOT}/src`,
    };
    act(() => {
      latestBatchProps().onDraftChange(batchState);
    });

    expect(store.read(primaryKey)).toMatchObject({
      dirtyEntities: [
        {
          id: ENTITY_ID,
          drafts: {
            image: { previewUrl: BLOB_URL },
            text: { def: TEXT_DRAFT },
          },
        },
      ],
      inlineCreate: {
        objectId: "TECH_DRAFT",
        values: { title: "Retained technology" },
      },
      batchCreate: batchState,
    });
    expect(store.getSnapshot().sessions).toHaveLength(1);

    unmountEditor(mounted);
    expect(revokeObjectUrl).not.toHaveBeenCalled();

    mounted = mountEditor(primaryBrowser, store);

    expect(latestDetailProps().entity).toMatchObject({
      id: ENTITY_ID,
      draftState: "modified",
      drafts: {
        image: { previewUrl: BLOB_URL },
        text: { def: TEXT_DRAFT },
      },
    });
    expect(latestListProps()).toMatchObject({
      createObjectId: "TECH_DRAFT",
      createValues: { title: "Retained technology" },
    });
    expect(latestBatchProps().initialState).toEqual(batchState);

    unmountEditor(mounted);
    expect(revokeObjectUrl).not.toHaveBeenCalled();

    mounted = mountEditor(primaryBrowser, store, "diagram");
    await flushDiagramLoad();
    expect(latestDiagramProps().document.nodes).toHaveLength(1);
    expect(store.getSnapshot().sessions).toHaveLength(1);

    act(() => {
      latestDiagramProps().onNodeMove?.("TECH_ALPHA", { dx: 1, dy: 0 });
    });

    expect(store.getSnapshot().sessions).toEqual([
      expect.objectContaining({
        key: primaryKey,
        dirty: true,
        dirtyDiagramEntityIds: [ENTITY_ID],
        dirtyEntityIds: [ENTITY_ID],
        inlineCreateDirty: true,
        projectRoot: PROJECT_ROOT,
      }),
    ]);

    unmountEditor(mounted);
    expect(revokeObjectUrl).not.toHaveBeenCalled();

    mounted = mountEditor(
      browserForRoot(CHECKOUT_ROOT, "PIHC3_CHECKOUT"),
      store,
    );

    expect(latestDetailProps().entity).toMatchObject({
      id: ENTITY_ID,
      draftState: "clean",
      drafts: { text: {} },
    });
    expect(latestDetailProps().entity?.drafts.image).toBeUndefined();
    expect(latestListProps()).toMatchObject({
      createObjectId: "",
      createValues: {},
    });
    expect(store.getSnapshot().sessions).toHaveLength(1);
    expect(store.getSnapshot().sessions[0]?.key).toBe(primaryKey);

    act(() => {
      latestDetailProps().onTextDraft(ENTITY_ID, "def", "checkout = yes\n");
    });

    expect(
      store.getSnapshot().sessions.map((session) => session.projectRoot),
    ).toEqual([CHECKOUT_ROOT, PROJECT_ROOT]);
    expect(store.read(primaryKey)?.dirtyEntities[0]?.drafts.text.def).toBe(
      TEXT_DRAFT,
    );
    expect(store.read(checkoutKey)?.dirtyEntities[0]?.drafts.text.def).toBe(
      "checkout = yes\n",
    );

    expect(store.discard(primaryKey)).toBe(true);
    expect(revokeObjectUrl).toHaveBeenCalledOnce();
    expect(revokeObjectUrl).toHaveBeenCalledWith(BLOB_URL);
    expect(store.read(primaryKey)).toBeNull();
    expect(store.getSnapshot().sessions).toEqual([
      expect.objectContaining({
        key: checkoutKey,
        projectRoot: CHECKOUT_ROOT,
      }),
    ]);

    unmountEditor(mounted);
    expect(store.discard(checkoutKey)).toBe(true);
  });
});

function mountEditor(
  browser: ProjectBrowserPayload,
  store: ModuleEditorSessionStore,
  surface: "diagram" | "module" = "module",
  options: {
    onBatchRecoveryPathsChange?: (paths: string[]) => void;
  } = {},
): MountedEditor {
  const container = document.createElement("div");
  document.body.append(container);
  const root = createRoot(container);
  const mounted = { container, mounted: true, root };
  mountedEditors.push(mounted);
  renderMountedEditor(
    mounted,
    browser,
    store,
    surface,
    templates,
    options,
  );
  return mounted;
}

function mountMioEditor(
  browser: ProjectBrowserPayload,
  store: ModuleEditorSessionStore,
  onOpenModuleEntity?: (target: {
    entityId: string;
    familyId: string;
    sourcePath?: string;
  }) => void,
  selectedEntityId = "",
  projectTemplates: ProjectTemplatesPayload | null = null,
): MountedEditor {
  const container = document.createElement("div");
  document.body.append(container);
  const root = createRoot(container);
  const mounted = { container, mounted: true, root };
  mountedEditors.push(mounted);
  mocks.diagramPayloads.set(browser.root, mioDiagramForBrowser(browser));
  act(() => {
    root.render(
      <ModuleEditor
        browser={browser}
        familyId="military-industrial-organizations"
        locale="en"
        onOpenModuleEntity={onOpenModuleEntity}
        onPinTab={() => undefined}
        onProjectRefresh={async () => undefined}
        openTarget="finder"
        selectedEntityId={selectedEntityId}
        sessionStore={store}
        surface="diagram"
        t={createTranslator("en")}
        templates={projectTemplates}
        theme="light"
      />,
    );
  });
  return mounted;
}

function mountFocusEditor(
  browser: ProjectBrowserPayload,
  store: ModuleEditorSessionStore,
  projectTemplates: ProjectTemplatesPayload | null = null,
  options: {
    moduleCreateIntent?: ModuleCreateIntent;
    onModuleCreateIntentConsumed?: (nonce: number) => void;
  } = {},
): MountedEditor {
  const container = document.createElement("div");
  document.body.append(container);
  const root = createRoot(container);
  const mounted = { container, mounted: true, root };
  mountedEditors.push(mounted);
  mocks.diagramPayloads.set(browser.root, focusDiagramForBrowser(browser));
  act(() => {
    root.render(
      <ModuleEditor
        browser={browser}
        familyId="focuses"
        locale="en"
        {...(options.moduleCreateIntent
          ? { moduleCreateIntent: options.moduleCreateIntent }
          : {})}
        {...(options.onModuleCreateIntentConsumed
          ? {
              onModuleCreateIntentConsumed:
                options.onModuleCreateIntentConsumed,
            }
          : {})}
        onPinTab={() => undefined}
        onProjectRefresh={async () => undefined}
        openTarget="finder"
        sessionStore={store}
        surface="diagram"
        t={createTranslator("en")}
        templates={projectTemplates}
        theme="light"
      />,
    );
  });
  return mounted;
}

function mountGenericGraphEditor(
  browser: ProjectBrowserPayload,
  store: ModuleEditorSessionStore,
): MountedEditor {
  const container = document.createElement("div");
  document.body.append(container);
  const root = createRoot(container);
  const mounted = { container, mounted: true, root };
  mountedEditors.push(mounted);
  mocks.diagramPayloads.set(browser.root, genericGraphDiagramForBrowser(browser));
  act(() => {
    root.render(
      <ModuleEditor
        browser={browser}
        familyId="demo"
        locale="en"
        onPinTab={() => undefined}
        onProjectRefresh={async () => undefined}
        openTarget="finder"
        sessionStore={store}
        surface="diagram"
        t={createTranslator("en")}
        templates={null}
        theme="light"
      />,
    );
  });
  return mounted;
}

function renderMountedEditor(
  mounted: MountedEditor,
  browser: ProjectBrowserPayload,
  store: ModuleEditorSessionStore,
  surface: "diagram" | "module" = "module",
  projectTemplates: ProjectTemplatesPayload | null = templates,
  options: {
    moduleCreateIntent?: ModuleCreateIntent;
    onModuleCreateIntentConsumed?: (nonce: number) => void;
    onBatchRecoveryPathsChange?: (paths: string[]) => void;
    onProjectRefresh?: (
      projectRoot?: string,
      fallbackProjectId?: string,
    ) => Promise<void>;
  } = {},
): void {
  mocks.diagramPayloads.set(browser.root, moduleDiagramForBrowser(browser));
  act(() => {
    mounted.root.render(
      <ModuleEditor
        browser={browser}
        familyId="technologies"
        locale="en"
        {...(options.moduleCreateIntent
          ? { moduleCreateIntent: options.moduleCreateIntent }
          : {})}
        {...(options.onModuleCreateIntentConsumed
          ? {
              onModuleCreateIntentConsumed:
                options.onModuleCreateIntentConsumed,
            }
          : {})}
        {...(options.onBatchRecoveryPathsChange
          ? {
              onBatchRecoveryPathsChange:
                options.onBatchRecoveryPathsChange,
            }
          : {})}
        onPinTab={() => undefined}
        onProjectRefresh={options.onProjectRefresh ?? (async () => undefined)}
        openTarget="finder"
        sessionStore={store}
        surface={surface}
        t={createTranslator("en")}
        templates={projectTemplates}
        theme="light"
      />,
    );
  });
}

async function flushDiagramLoad(): Promise<void> {
  await act(async () => {
    await Promise.resolve();
    await Promise.resolve();
  });
}

function unmountEditor(mounted: MountedEditor): void {
  if (!mounted.mounted) {
    return;
  }
  mounted.mounted = false;
  act(() => mounted.root.unmount());
  mounted.container.remove();
}

function browserForRoot(
  root: string,
  projectId: string,
): ProjectBrowserPayload {
  return {
    schema: "paradev.sdk.project-browser.v1",
    project_id: projectId,
    title: projectId,
    root,
    profile: "hoi4",
    filters: {},
    diagnostics: [],
    families: [
      {
        id: "technologies",
        family: "technology",
        title: "Technologies",
        item_count: 1,
        source_count: 1,
        layouts: ["canonical"],
        diagram: {
          id: "technology",
          aliases: ["technologies"],
          renderer: "technology",
          title: "Technology tree",
          editable: true,
          authoring_kind: "module",
          selection_defaults: [
            { field: "folder", source: "folder" },
            { field: "x", source: "x" },
            { field: "y", source: "y", offset: 2 },
            {
              field: "dependencies",
              source: "id",
              template: "dependencies = {\n\t\t\t{value} = 1\n\t\t}",
            },
          ],
          relationships: [
            {
              cardinality: "many",
              kind: "dependency",
              label: "Prerequisite",
              owner_endpoint: "target",
              selected_endpoint: "target",
              symmetric: false,
              visual_kind: "dependency",
            },
            {
              cardinality: "many",
              kind: "path",
              label: "Unlock path",
              owner_endpoint: "source",
              selected_endpoint: "source",
              symmetric: false,
              visual_kind: "path",
            },
          ],
        },
      },
    ],
    items: [
      {
        id: ENTITY_ID,
        kind: "module",
        layout: "canonical",
        family_id: "technologies",
        family: "technology",
        object_id: "TECH_ALPHA",
        module_id: "technology/TECH_ALPHA",
        title: "Alpha technology",
        root: `${root}/src/modules/technology/TECH_ALPHA`,
        relative_root: "src/modules/technology/TECH_ALPHA",
        source_root: `${root}/src`,
        source_count: 1,
        sources: [
          {
            slot: "def",
            name: "def.pdx",
            path: `${root}/src/modules/technology/TECH_ALPHA/def.pdx`,
            relative_path: "src/modules/technology/TECH_ALPHA/def.pdx",
            extension: "pdx",
          },
        ],
        metadata: {
          settings: {
            folder_position: { x: 1, y: 1 },
          },
        },
      },
    ],
  };
}

function genericGraphBrowserForRoot(
  root: string,
  projectId: string,
): ProjectBrowserPayload {
  const relativeRoot = "src/modules/demo/EXT_A";
  return {
    schema: "paradev.sdk.project-browser.v1",
    project_id: projectId,
    title: projectId,
    root,
    profile: "hoi4",
    filters: { family: "demo" },
    diagnostics: [],
    families: [
      {
        id: "demo",
        family: "demo",
        title: "External graph",
        item_count: 2,
        source_count: 2,
        layouts: ["canonical"],
        diagram: {
          id: "external_graph",
          aliases: [],
          renderer: "graph",
          title: "External graph",
          editable: true,
          relationships: [
            {
              cardinality: "many",
              kind: "custom_link",
              label: "Custom link",
              owner_endpoint: "source",
              selected_endpoint: "source",
              symmetric: false,
              visual_kind: "reference",
            },
          ],
        },
      },
    ],
    items: [
      {
        id: "module:demo/EXT_A",
        kind: "module",
        layout: "canonical",
        family_id: "demo",
        family: "demo",
        object_id: "EXT_A",
        module_id: "demo/EXT_A",
        title: "External A",
        root: `${root}/${relativeRoot}`,
        relative_root: relativeRoot,
        source_count: 1,
        sources: [],
      },
      {
        id: "module:demo/EXT_B",
        kind: "module",
        layout: "canonical",
        family_id: "demo",
        family: "demo",
        object_id: "EXT_B",
        module_id: "demo/EXT_B",
        title: "External B",
        root: `${root}/src/modules/demo/EXT_B`,
        relative_root: "src/modules/demo/EXT_B",
        source_count: 1,
        sources: [],
      },
    ],
  };
}

function genericGraphDiagramForBrowser(
  browser: ProjectBrowserPayload,
): ModuleDiagramPayload {
  return {
    schema: "paradev.sdk.module_diagram.v1",
    provider_schema: "example.external.graph.v1",
    project_id: browser.project_id,
    project_root: browser.root,
    profile: browser.profile,
    family: "demo",
    source_kind: "project_extension",
    editable: true,
    nodes: [
      {
        id: "EXT_A",
        x: 1,
        y: 2,
        source_path: "src/modules/demo/EXT_A/def.pdx",
        source_revision: "sha256:EXT_A",
        localized_titles: { en: "External A" },
      },
      {
        id: "EXT_B",
        x: 4,
        y: 2,
        source_path: "src/modules/demo/EXT_B/def.pdx",
        source_revision: "sha256:EXT_B",
        localized_titles: { en: "External B" },
      },
    ],
    edges: [],
    diagnostics: [],
    summary: { node_count: 2 },
  };
}

function mioBrowserForRoot(
  root: string,
  projectId: string,
): ProjectBrowserPayload {
  const family = "military_industrial_organization";
  const relativeRoot = "src/modules/military_industrial_organization/C01";
  return {
    schema: "paradev.sdk.project-browser.v1",
    project_id: projectId,
    title: projectId,
    root,
    profile: "hoi4",
    filters: { family },
    diagnostics: [],
    families: [
      {
        id: "military-industrial-organizations",
        family,
        title: "Military Industrial Organization",
        visible: true,
        item_count: 1,
        source_count: 1,
        layouts: ["canonical"],
        diagram: {
          id: "military_industrial_organization",
          aliases: ["mio"],
          renderer: "mio-trait",
          title: "Military Industrial Organization tree",
          editable: true,
          authoring_kind: "diagram-node",
          initial_scope: "project",
          scope_authoring_kind: "collection",
          node_authoring: {
            title: "Add MIO trait",
            description: "Create a trait in the selected organization.",
            fields: [
              {
                name: "trait_id",
                label: "Trait ID",
                kind: "text",
                required: true,
              },
              {
                name: "title",
                label: "Title",
                kind: "text",
                required: true,
              },
            ],
            selection_defaults: [
              {
                field: "organization_id",
                source: "organization_id",
              },
              {
                field: "parent_trait_id",
                source: "trait_id",
              },
              { field: "source_path", source: "source_path" },
              {
                field: "source_revision",
                source: "source_revision",
              },
              { field: "x", source: "x" },
              { field: "y", source: "y", offset: 1 },
            ],
            requires_selection: true,
          },
          relationships: [
            {
              cardinality: "one",
              kind: "relative_position",
              label: "Relative-position parent",
              owner_endpoint: "target",
              selected_endpoint: "target",
              symmetric: false,
              visual_kind: "tree",
            },
            {
              cardinality: "many",
              kind: "any_parent",
              label: "Any parent",
              owner_endpoint: "target",
              selected_endpoint: "target",
              symmetric: false,
              visual_kind: "dependency",
            },
          ],
        },
      },
    ],
    items: [
      {
        id: "module:mio/C01",
        kind: "module",
        layout: "canonical",
        family_id: "military-industrial-organizations",
        family,
        object_id: "C01",
        module_id: "mio/C01",
        title: "C01 MIO",
        root: `${root}/${relativeRoot}`,
        relative_root: relativeRoot,
        source_root: `${root}/src`,
        source_count: 1,
        sources: [
          {
            slot: "pdx",
            name: "C01.txt",
            path: `${root}/${relativeRoot}/common/military_industrial_organization/organizations/C01.txt`,
            relative_path: `${relativeRoot}/common/military_industrial_organization/organizations/C01.txt`,
            extension: "txt",
          },
        ],
      },
    ],
  };
}

function focusBrowserForRoot(
  root: string,
  projectId: string,
): ProjectBrowserPayload {
  const relativeRoot = "src/modules/focus_tree/ALPHA_TREE";
  return {
    schema: "paradev.sdk.project-browser.v1",
    project_id: projectId,
    title: projectId,
    root,
    profile: "hoi4",
    filters: { family: "focus_tree" },
    diagnostics: [],
    families: [
      {
        id: "focuses",
        family: "focus_tree",
        title: "Focus trees",
        item_count: 1,
        source_count: 1,
        layouts: ["canonical"],
        diagram: {
          id: "focus_tree",
          aliases: ["focus", "focuses"],
          renderer: "focus-tree",
          title: "Focus tree",
          editable: true,
          authoring_kind: "diagram-node",
          scope_authoring_kind: "collection",
          relationships: [
            {
              cardinality: "many",
              kind: "prerequisite",
              label: "Prerequisite",
              owner_endpoint: "target",
              selected_endpoint: "target",
              symmetric: false,
              visual_kind: "dependency",
            },
            {
              cardinality: "many",
              kind: "mutually_exclusive",
              label: "Mutually exclusive",
              owner_endpoint: "source",
              selected_endpoint: "source",
              symmetric: true,
              visual_kind: "reference",
            },
          ],
        },
      },
    ],
    items: [
      {
        id: "module:focus_tree/ALPHA_TREE",
        kind: "module",
        layout: "canonical",
        family_id: "focuses",
        family: "focus_tree",
        object_id: "ALPHA_TREE",
        module_id: "focus_tree/ALPHA_TREE",
        title: "Alpha tree",
        root: `${root}/${relativeRoot}`,
        relative_root: relativeRoot,
        source_root: `${root}/src`,
        source_count: 1,
        sources: [
          {
            slot: "def",
            name: "def.txt",
            path: `${root}/${relativeRoot}/def.txt`,
            relative_path: `${relativeRoot}/def.txt`,
            extension: "txt",
          },
        ],
        metadata: {
          settings: {
            focuses: [
              {
                id: "LEGACY_METADATA_ONLY",
                x: 99,
                y: 99,
              },
            ],
          },
        },
      },
    ],
  };
}

function browserWithExtraTechnology(
  root: string,
  projectId: string,
  includeGamma = false,
): ProjectBrowserPayload {
  const browser = browserForRoot(root, projectId);
  const extraIds = includeGamma ? ["TECH_BETA", "TECH_GAMMA"] : ["TECH_BETA"];
  return {
    ...browser,
    families: browser.families.map((family) => ({
      ...family,
      item_count: 1 + extraIds.length,
      source_count: 1 + extraIds.length,
    })),
    items: [
      ...browser.items,
      ...extraIds.map((objectId, index) => ({
        ...browser.items[0],
        id: `module:technology/${objectId}`,
        module_id: `technology/${objectId}`,
        object_id: objectId,
        root: `${root}/src/modules/technology/${objectId}`,
        relative_root: `src/modules/technology/${objectId}`,
        title: `${objectId} technology`,
        sources: [
          {
            ...browser.items[0].sources[0],
            name: "def.pdx",
            path: `${root}/src/modules/technology/${objectId}/def.pdx`,
            relative_path: `src/modules/technology/${objectId}/def.pdx`,
          },
        ],
        metadata: {
          settings: {
            folder_position: { x: index + 2, y: 1 },
          },
        },
      })),
    ],
  };
}

function browserWithMetadataSource(
  root: string,
  projectId: string,
): ProjectBrowserPayload {
  const browser = browserForRoot(root, projectId);
  return {
    ...browser,
    items: browser.items.map((item) => ({
      ...item,
      source_count: 1,
      sources: [
        {
          slot: "meta",
          name: "meta.yaml",
          path: `${root}/src/modules/technology/TECH_ALPHA/meta.yaml`,
          relative_path: "src/modules/technology/TECH_ALPHA/meta.yaml",
          extension: "yaml",
        },
      ],
    })),
  };
}

function moduleDiagramForBrowser(
  browser: ProjectBrowserPayload,
): ModuleDiagramPayload {
  const items = browser.items.filter(
    (item) => item.kind === "module" && item.family === "technology",
  );
  return {
    schema: "paradev.sdk.module_diagram.v1",
    provider_schema: "paradev.hoi4.technology-diagram-projection.v1",
    project_id: browser.project_id,
    project_root: browser.root,
    profile: browser.profile,
    family: "technology",
    source_kind: "module_def_pdx",
    editable: true,
    sources: [],
    nodes: items.map((item, index) => {
      const settings =
        item.metadata?.settings && typeof item.metadata.settings === "object"
          ? (item.metadata.settings as Record<string, unknown>)
          : {};
      const position =
        settings.folder_position && typeof settings.folder_position === "object"
          ? (settings.folder_position as Record<string, unknown>)
          : {};
      const source =
        item.sources.find((row) => row.slot === "def") ?? item.sources[0];
      return {
        id: item.object_id,
        folder: "infantry_folder",
        x: typeof position.x === "number" ? position.x : index + 1,
        y: typeof position.y === "number" ? position.y : 1,
        source_path: source?.relative_path || `${item.relative_root}/def.txt`,
        source_revision: `sha256:${item.object_id}`,
        editable: true,
      };
    }),
    edges: [],
    diagnostics: [],
    summary: {
      source_count: items.length,
      node_count: items.length,
      edge_count: 0,
    },
  };
}

function mioDiagramForBrowser(
  browser: ProjectBrowserPayload,
): ModuleDiagramPayload {
  const family = "military_industrial_organization";
  const sourcePath =
    "src/modules/military_industrial_organization/C01/common/military_industrial_organization/organizations/C01.txt";
  return {
    schema: "paradev.sdk.module_diagram.v1",
    provider_schema: "paradev.hoi4.mio-trait-diagram-projection.v1",
    project_id: browser.project_id,
    project_root: browser.root,
    profile: browser.profile,
    family,
    source_kind: "module_pdx_source",
    editable: true,
    module_ids: ["mio/C01"],
    organizations: [
      {
        id: "C01_ORG",
        organization_id: "C01_ORG",
        module_id: "mio/C01",
        name_key: "C01_ORG_NAME",
        localized_titles: {
          l_english: "Canterlot Works",
        },
      },
      {
        id: "C01_SECOND",
        organization_id: "C01_SECOND",
        module_id: "mio/C01",
        name_key: "C01_SECOND_NAME",
        localized_titles: {
          l_english: "Canterlot Engines",
        },
      },
    ],
    nodes: [
      {
        id: "C01_ORG::trait::CHILD",
        kind: "trait",
        module_id: "mio/C01",
        organization_id: "C01_ORG",
        trait_id: "CHILD",
        name_key: "C01_CHILD",
        localized_titles: {
          l_english: "Child trait",
        },
        position: { x: 0, y: 1 },
        source_path: sourcePath,
        source_revision: "sha256:mio-source",
        editable: true,
      },
      {
        id: "C01_ORG::trait::ROOT",
        kind: "trait",
        module_id: "mio/C01",
        organization_id: "C01_ORG",
        trait_id: "ROOT",
        name_key: "C01_ROOT",
        localized_titles: {
          l_english: "Root trait",
        },
        x: 0,
        y: 0,
        position: { x: 0, y: 0 },
        source_path: sourcePath,
        source_revision: "sha256:mio-source",
        editable: true,
      },
      {
        id: "C01_SECOND::trait::CHILD",
        kind: "trait",
        module_id: "mio/C01",
        organization_id: "C01_SECOND",
        trait_id: "CHILD",
        name_key: "C01_SECOND_CHILD",
        localized_titles: {
          l_english: "Engine child",
        },
        position: { x: 0, y: 1 },
        source_path: sourcePath,
        source_revision: "sha256:mio-source",
        editable: true,
      },
      {
        id: "C01_SECOND::trait::ROOT",
        kind: "trait",
        module_id: "mio/C01",
        organization_id: "C01_SECOND",
        trait_id: "ROOT",
        name_key: "C01_SECOND_ROOT",
        localized_titles: {
          l_english: "Engine root",
        },
        position: { x: 0, y: 0 },
        source_path: sourcePath,
        source_revision: "sha256:mio-source",
        editable: true,
      },
    ],
    edges: [
      {
        id: "relative_position:C01_ORG::trait::ROOT->C01_ORG::trait::CHILD",
        kind: "relative_position",
        organization_id: "C01_ORG",
        source: "C01_ORG::trait::ROOT",
        target: "C01_ORG::trait::CHILD",
      },
      {
        id: "relative_position:C01_SECOND::trait::ROOT->C01_SECOND::trait::CHILD",
        kind: "relative_position",
        organization_id: "C01_SECOND",
        source: "C01_SECOND::trait::ROOT",
        target: "C01_SECOND::trait::CHILD",
      },
    ],
    diagnostics: [],
    summary: {
      organization_count: 2,
      trait_count: 4,
      edge_count: 2,
    },
  };
}

function focusDiagramForBrowser(
  browser: ProjectBrowserPayload,
): ModuleDiagramPayload {
  const sourcePath = "src/modules/focus_tree/ALPHA_TREE/def.txt";
  return {
    schema: "paradev.sdk.module_diagram.v1",
    provider_schema: "paradev.hoi4.focus-tree-diagram-projection.v1",
    project_id: browser.project_id,
    project_root: browser.root,
    profile: browser.profile,
    family: "focus_tree",
    source_kind: "module_def_pdx",
    editable: true,
    sources: [],
    trees: [
      {
        id: "ALPHA_TREE",
        source_path: sourcePath,
        source_revision: "sha256:alpha",
        node_count: 3,
        edge_count: 2,
        editable: true,
      },
    ],
    nodes: [
      {
        id: "FOCUS_CHILD",
        tree_id: "ALPHA_TREE",
        x: 2,
        y: 1,
        relative_position_id: "FOCUS_ROOT",
        source_path: sourcePath,
        source_revision: "sha256:alpha",
        editable: true,
      },
      {
        id: "FOCUS_OTHER",
        tree_id: "ALPHA_TREE",
        x: 4,
        y: 1,
        source_path: sourcePath,
        source_revision: "sha256:alpha",
        editable: true,
      },
      {
        id: "FOCUS_ROOT",
        tree_id: "ALPHA_TREE",
        x: 10,
        y: 0,
        source_path: sourcePath,
        source_revision: "sha256:alpha",
        editable: true,
      },
    ],
    edges: [
      {
        id: "mutually_exclusive:FOCUS_CHILD->FOCUS_OTHER",
        kind: "mutually_exclusive",
        source: "FOCUS_CHILD",
        target: "FOCUS_OTHER",
        source_path: sourcePath,
        source_paths: [sourcePath],
        source_revision: "sha256:mutex-review",
        declaration_count: 2,
        editable: true,
      },
      {
        id: "prerequisite:FOCUS_ROOT->FOCUS_CHILD",
        kind: "prerequisite",
        source: "FOCUS_ROOT",
        target: "FOCUS_CHILD",
        source_path: sourcePath,
        source_paths: [sourcePath],
        source_revision: "sha256:alpha",
        declaration_count: 1,
        editable: true,
      },
    ],
    diagnostics: [],
    summary: {
      source_count: 1,
      tree_count: 1,
      node_count: 3,
      edge_count: 2,
    },
  };
}

function latestListProps(): CapturedListProps {
  const props = mocks.listProps.at(-1);
  if (!props) {
    throw new Error("ModuleEntityList has not rendered.");
  }
  return props as CapturedListProps;
}

function latestDetailProps(): CapturedDetailProps {
  const props = mocks.detailProps.at(-1);
  if (!props) {
    throw new Error("ModuleEntityDetails has not rendered.");
  }
  return props as CapturedDetailProps;
}

function latestDiagramProps(): CapturedDiagramProps {
  const props = mocks.diagramProps.at(-1);
  if (!props) {
    throw new Error("ProjectDiagramView has not rendered.");
  }
  return props as CapturedDiagramProps;
}

function latestBatchProps(): CapturedBatchProps {
  const props = mocks.batchProps.at(-1);
  if (!props) {
    throw new Error("Module batch dialog props were not captured.");
  }
  return props as unknown as CapturedBatchProps;
}

function latestNodeProps(): CapturedNodeProps {
  const props = mocks.nodeProps.at(-1);
  if (!props) {
    throw new Error("Diagram node create dialog props were not captured.");
  }
  return props as CapturedNodeProps;
}
