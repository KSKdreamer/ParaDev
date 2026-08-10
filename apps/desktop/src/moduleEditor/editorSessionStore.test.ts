import { describe, expect, it, vi } from "vitest";
import { createDiagramHistory } from "../diagramEditor/diagramHistory";
import type { DiagramDocument } from "../diagramEditor/layoutModel";
import {
  ModuleEditorSessionStore,
  moduleEditorSessionKey
} from "./editorSessionStore";
import type { ModuleEntity } from "./model";

const PROJECT_ROOT = "/workspace/projects/PIHC3";
const SOURCE_PATH = `${PROJECT_ROOT}/src/modules/idea/IDEA_ALPHA/def.pdx`;

describe("ModuleEditorSessionStore", () => {
  it("normalizes stable family IDs while isolating canonical project roots", () => {
    const store = new ModuleEditorSessionStore();
    const primary = moduleEditorSessionKey(` ${PROJECT_ROOT} `, "ideas");
    const alias = moduleEditorSessionKey(PROJECT_ROOT, "ideas");
    const checkout = moduleEditorSessionKey(
      "/workspace/checkouts/PIHC3",
      "ideas"
    );

    expect(primary).toBe(alias);
    expect(checkout).not.toBe(primary);

    store.setDirtyEntities(primary, [modifiedEntity("IDEA_ALPHA")]);

    expect(store.read(primary)?.familyId).toBe("ideas");
    expect(store.read(checkout)).toBeNull();
    expect(store.getSnapshot().sessions).toHaveLength(1);
  });

  it("retains immutable dirty rows and merges them over fresh SDK rows", () => {
    const store = new ModuleEditorSessionStore();
    const key = moduleEditorSessionKey(PROJECT_ROOT, "ideas");
    const dirty = modifiedEntity("IDEA_ALPHA", "draft = yes\n");
    const unsaved = {
      ...modifiedEntity("IDEA_NEW", "new = yes\n"),
      draftState: "new" as const,
      root: ""
    };
    const clean = cleanEntity("IDEA_BETA");

    store.setDirtyEntities(key, [dirty, unsaved, clean]);
    dirty.drafts.text.def = "mutated after transfer\n";
    const state = store.read(key);

    expect(state?.dirtyEntities.map((entity) => entity.id)).toEqual([
      "module:idea/IDEA_ALPHA",
      "module:idea/IDEA_NEW"
    ]);
    expect(state?.dirtyEntities[0]?.drafts.text.def).toBe("draft = yes\n");
    expect(Object.isFrozen(state)).toBe(true);
    expect(Object.isFrozen(state?.dirtyEntities)).toBe(true);
    expect(Object.isFrozen(state?.dirtyEntities[0]?.drafts.text)).toBe(true);

    const restored = store.restoreEntities(key, [
      {
        ...cleanEntity("IDEA_ALPHA"),
        title: "Fresh SDK title",
        root: `${PROJECT_ROOT}/src/modules/idea/IDEA_ALPHA - Fresh`
      },
      clean
    ]);

    expect(restored).toHaveLength(3);
    expect(restored[0]).toMatchObject({
      id: "module:idea/IDEA_ALPHA",
      title: "Fresh SDK title",
      root: `${PROJECT_ROOT}/src/modules/idea/IDEA_ALPHA - Fresh`,
      draftState: "modified",
      drafts: { text: { def: "draft = yes\n" } }
    });
    expect(restored[2]?.id).toBe("module:idea/IDEA_NEW");
  });

  it("publishes stable dirty/busy summaries separately from session data", () => {
    const store = new ModuleEditorSessionStore();
    const key = moduleEditorSessionKey(PROJECT_ROOT, "ideas");
    const globalListener = vi.fn();
    const sessionListener = vi.fn();
    const { getSnapshot, subscribe } = store;
    const unsubscribeGlobal = subscribe(globalListener);
    const unsubscribeSession = store.subscribeSession(key, sessionListener);
    const emptySnapshot = getSnapshot();

    store.setInlineCreate(key, {
      templateId: "hoi4.idea",
      objectId: "",
      values: {},
      showAdvanced: true
    });

    expect(sessionListener).toHaveBeenCalledTimes(1);
    expect(globalListener).not.toHaveBeenCalled();
    expect(getSnapshot()).toBe(emptySnapshot);

    store.setInlineCreate(key, {
      templateId: "hoi4.idea",
      objectId: "IDEA_NEW",
      values: {},
      showAdvanced: true
    });

    expect(sessionListener).toHaveBeenCalledTimes(2);
    expect(globalListener).toHaveBeenCalledTimes(1);
    expect(store.getSnapshot()).toMatchObject({
      dirty: true,
      busy: false,
      sessions: [
        {
          key,
          dirty: true,
          busy: false,
          inlineCreateDirty: true
        }
      ]
    });

    const finish = store.beginBusy(key);
    expect(globalListener).toHaveBeenCalledTimes(2);
    expect(sessionListener).toHaveBeenCalledTimes(3);
    expect(store.read(key)?.busy).toBe(true);
    expect(store.getSnapshot()).toMatchObject({ dirty: true, busy: true });

    finish();
    finish();
    expect(globalListener).toHaveBeenCalledTimes(3);
    expect(sessionListener).toHaveBeenCalledTimes(4);
    expect(store.read(key)?.busy).toBe(false);
    expect(store.getSnapshot()).toMatchObject({ dirty: true, busy: false });

    unsubscribeGlobal();
    unsubscribeSession();
    store.setInlineCreate(key, null);
    expect(globalListener).toHaveBeenCalledTimes(3);
    expect(sessionListener).toHaveBeenCalledTimes(4);
  });

  it("ignores deleted form values while retaining meaningful falsy values", () => {
    const store = new ModuleEditorSessionStore();
    const key = moduleEditorSessionKey(PROJECT_ROOT, "ideas");
    const inline = {
      templateId: "hoi4.idea",
      objectId: "",
      showAdvanced: false
    };
    const pristineValues = runtimeFormValues({
      optional: undefined,
      title: ""
    });

    store.setInlineCreate(key, {
      ...inline,
      values: runtimeFormValues({ title: "Typed, then deleted" })
    });
    expect(store.getSnapshot().sessions[0]).toMatchObject({
      inlineCreateDirty: true
    });

    store.setInlineCreate(key, { ...inline, values: pristineValues });
    expect(store.getSnapshot()).toMatchObject({
      dirty: false,
      sessions: []
    });

    store.setInlineCreate(key, {
      ...inline,
      values: runtimeFormValues({ enabled: false })
    });
    expect(store.getSnapshot().sessions[0]).toMatchObject({
      inlineCreateDirty: true
    });

    store.setInlineCreate(key, {
      ...inline,
      values: runtimeFormValues({ cost: 0 })
    });
    expect(store.getSnapshot().sessions[0]).toMatchObject({
      inlineCreateDirty: true
    });

    store.setInlineCreate(key, { ...inline, values: pristineValues });
    const pristineBatch = {
      open: true,
      pristineSourceRoot: `${PROJECT_ROOT}/src`,
      pristineTemplateId: "pihc3:idea/basic",
      rows: [
        {
          key: 1,
          objectId: "",
          templateId: "pihc3:idea/basic",
          values: pristineValues
        }
      ],
      showAdvanced: false,
      sourceRoot: `${PROJECT_ROOT}/src`
    };

    store.setBatchCreate(key, {
      ...pristineBatch,
      rows: [
        {
          ...pristineBatch.rows[0],
          values: runtimeFormValues({ title: "Typed, then deleted" })
        }
      ]
    });
    expect(store.getSnapshot().sessions[0]).toMatchObject({
      batchCreateDirty: true,
      inlineCreateDirty: false
    });

    store.setBatchCreate(key, pristineBatch);
    expect(store.getSnapshot()).toMatchObject({
      dirty: false,
      sessions: []
    });

    store.setBatchCreate(key, {
      ...pristineBatch,
      rows: [
        {
          ...pristineBatch.rows[0],
          values: runtimeFormValues({ enabled: false })
        }
      ]
    });
    expect(store.getSnapshot().sessions[0]).toMatchObject({
      batchCreateDirty: true
    });

    store.setBatchCreate(key, {
      ...pristineBatch,
      rows: [
        {
          ...pristineBatch.rows[0],
          values: runtimeFormValues({ cost: 0 })
        }
      ]
    });
    expect(store.getSnapshot().sessions[0]).toMatchObject({
      batchCreateDirty: true
    });

    store.setBatchCreate(key, pristineBatch);
    expect(store.getSnapshot()).toMatchObject({
      dirty: false,
      sessions: []
    });
  });

  it("retains collection scaffold input and exposes it to close guards", () => {
    const store = new ModuleEditorSessionStore();
    const key = moduleEditorSessionKey(PROJECT_ROOT, "focuses");
    const pristine = {
      open: true,
      pristineSourceRoot: `${PROJECT_ROOT}/src`,
      pristineTemplateId: "pihc3:focus-tree/basic",
      templateId: "pihc3:focus-tree/basic",
      collectionId: "",
      values: {},
      showAdvanced: false,
      sourceRoot: `${PROJECT_ROOT}/src`
    };

    store.setCollectionCreate(key, pristine);
    expect(store.read(key)?.collectionCreate).toEqual(pristine);
    expect(store.getSnapshot()).toEqual({
      dirty: false,
      busy: false,
      sessions: []
    });

    store.setCollectionCreate(key, {
      ...pristine,
      collectionId: "C99_AI_REVIEW",
      values: { country_tag: "C99", title: "AI Review Tree" }
    });

    expect(store.getSnapshot().sessions[0]).toMatchObject({
      key,
      dirty: true,
      collectionCreateDirty: true,
      batchCreateDirty: false,
      inlineCreateDirty: false
    });
    expect(Object.isFrozen(store.read(key)?.collectionCreate?.values)).toBe(
      true
    );
  });

  it("retains clean diagram continuity but marks only changed metadata ids dirty", () => {
    const store = new ModuleEditorSessionStore();
    const key = moduleEditorSessionKey(PROJECT_ROOT, "focuses");
    const base = diagramDocument(0);
    const moved = diagramDocument(2);
    const cleanHistory = createDiagramHistory(base);
    const dirtyHistory = {
      future: [],
      past: [base],
      present: moved
    };

    store.setDiagram(key, "focus-tree:C08", cleanHistory);

    expect(store.read(key)?.diagrams).toHaveLength(1);
    expect(store.getSnapshot().dirty).toBe(false);

    store.setDiagram(
      key,
      "focus-tree:C08",
      dirtyHistory,
      ["FOCUS_B", "FOCUS_A", "FOCUS_A", ""]
    );

    const diagram = store.read(key)?.diagrams[0];
    expect(diagram?.changedEntityIds).toEqual(["FOCUS_A", "FOCUS_B"]);
    expect(Object.isFrozen(diagram?.history)).toBe(true);
    expect(Object.isFrozen(diagram?.history.past)).toBe(true);
    expect(store.getSnapshot().sessions[0]).toMatchObject({
      familyId: "focuses",
      dirtyDiagramEntityIds: ["FOCUS_A", "FOCUS_B"]
    });

    store.setDiagram(key, "focus-tree:C08", null);
    expect(store.read(key)).toBeNull();
    const emptySnapshot = store.getSnapshot();
    expect(store.getSnapshot()).toBe(emptySnapshot);
    expect(emptySnapshot).toMatchObject({
      dirty: false,
      busy: false,
      sessions: []
    });
  });

  it("retains batch rows while deriving dirty state from authored changes", () => {
    const store = new ModuleEditorSessionStore();
    const key = moduleEditorSessionKey(PROJECT_ROOT, "ideas");
    const pristine = {
      open: true,
      pristineSourceRoot: `${PROJECT_ROOT}/src`,
      pristineTemplateId: "pihc3:idea/basic",
      rows: [
        {
          key: 1,
          objectId: "",
          templateId: "pihc3:idea/basic",
          values: {}
        }
      ],
      showAdvanced: false,
      sourceRoot: `${PROJECT_ROOT}/src`
    };

    store.setBatchCreate(key, pristine);
    expect(store.read(key)?.batchCreate?.open).toBe(true);
    expect(store.getSnapshot().dirty).toBe(false);

    store.setBatchCreate(key, {
      ...pristine,
      rows: [{ ...pristine.rows[0], objectId: "IDEA_BATCH" }]
    });
    expect(store.getSnapshot().sessions[0]).toMatchObject({
      batchCreateDirty: true,
      dirty: true
    });

    store.setBatchCreate(key, null);
    expect(store.read(key)).toBeNull();
    expect(store.getSnapshot().dirty).toBe(false);
  });

  it("retains an exact source-update review as guarded unsaved work", () => {
    const store = new ModuleEditorSessionStore();
    const key = moduleEditorSessionKey(PROJECT_ROOT, "ideas");
    const state = {
      open: true,
      requests: [
        {
          source_path: "src/modules/idea/IDEA_ALPHA/def.pdx",
          module_id: "idea/IDEA_ALPHA",
          values: { "pdx-control-002": 2 },
          control_labels: { "pdx-control-002": "Country resource crystals" }
        }
      ],
      plan: {
        schema: "paradev.source-form-update-batch.v1" as const,
        projectId: "PIHC3",
        changed: false,
        counts: { requested: 1, changed: 0, unchanged: 1 },
        updates: [],
        sourceEdits: []
      }
    };

    store.setSourceUpdate(key, state);

    expect(store.read(key)?.sourceUpdate).toEqual(state);
    expect(Object.isFrozen(store.read(key)?.sourceUpdate?.requests)).toBe(true);
    expect(store.getSnapshot().sessions[0]).toMatchObject({
      key,
      dirty: true,
      sourceUpdateDirty: true
    });

    store.setSourceUpdate(key, null);
    expect(store.read(key)).toBeNull();
    expect(store.getSnapshot()).toEqual({
      dirty: false,
      busy: false,
      sessions: []
    });
  });

  it("refuses busy discard and releases owned resources exactly once", () => {
    const store = new ModuleEditorSessionStore();
    const key = moduleEditorSessionKey(PROJECT_ROOT, "ideas");
    const dispose = vi.fn();
    store.setDirtyEntities(key, [modifiedEntity("IDEA_ALPHA")]);
    store.ownResource(key, "blob:idea-alpha", dispose);
    const finish = store.beginBusy(key);

    expect(() => store.discard(key)).toThrow(
      "Cannot discard busy module editor session"
    );
    expect(dispose).not.toHaveBeenCalled();
    expect(store.read(key)).not.toBeNull();

    finish();
    expect(store.discard(key)).toBe(true);
    expect(dispose).toHaveBeenCalledTimes(1);
    expect(store.discard(key)).toBe(false);
    expect(store.read(key)).toBeNull();
    expect(store.getSnapshot()).toEqual({
      dirty: false,
      busy: false,
      sessions: []
    });
  });

  it("retains drafts and failed resource ownership when cleanup fails", () => {
    const store = new ModuleEditorSessionStore();
    const key = moduleEditorSessionKey(PROJECT_ROOT, "ideas");
    const released = vi.fn();
    const failed = vi
      .fn()
      .mockImplementationOnce(() => {
        throw new Error("blob release failed");
      })
      .mockImplementationOnce(() => undefined);
    store.setDirtyEntities(key, [modifiedEntity("IDEA_ALPHA")]);
    store.ownResource(key, "blob:released", released);
    store.ownResource(key, "blob:failed", failed);

    expect(() => store.discard(key)).toThrow(AggregateError);
    expect(released).toHaveBeenCalledTimes(1);
    expect(failed).toHaveBeenCalledTimes(1);
    expect(store.read(key)?.dirtyEntities).toHaveLength(1);
    expect(store.getSnapshot().dirty).toBe(true);

    expect(store.discard(key)).toBe(true);
    expect(released).toHaveBeenCalledTimes(1);
    expect(failed).toHaveBeenCalledTimes(2);
    expect(store.getSnapshot().dirty).toBe(false);
  });

  it("retains a Catalog repair requirement until it is explicitly cleared", () => {
    const store = new ModuleEditorSessionStore();
    const key = moduleEditorSessionKey(PROJECT_ROOT, "ideas");

    store.setCatalogMutationFailure(key, {
      status: "failed",
      message: "catalog database is locked"
    });

    expect(store.read(key)?.catalogMutationFailure).toEqual({
      status: "failed",
      message: "catalog database is locked"
    });
    expect(store.getSnapshot()).toMatchObject({
      dirty: true,
      sessions: [{ key, dirty: true }]
    });

    store.setCatalogMutationFailure(key, null);

    expect(store.read(key)).toBeNull();
    expect(store.getSnapshot()).toEqual({
      dirty: false,
      busy: false,
      sessions: []
    });
  });

  it("preflights busy sessions before discardAll mutates any session", () => {
    const store = new ModuleEditorSessionStore();
    const ideas = moduleEditorSessionKey(PROJECT_ROOT, "ideas");
    const focuses = moduleEditorSessionKey(PROJECT_ROOT, "focuses");
    store.setDirtyEntities(ideas, [modifiedEntity("IDEA_ALPHA")]);
    store.setDirtyEntities(focuses, [modifiedEntity("FOCUS_ALPHA")]);
    const finish = store.beginBusy(focuses);

    expect(() => store.discardAll()).toThrow(
      "Cannot discard module editor sessions"
    );
    expect(store.read(ideas)).not.toBeNull();
    expect(store.read(focuses)).not.toBeNull();

    finish();
    expect(store.discardAll()).toBe(2);
    expect(store.getSnapshot().sessions).toHaveLength(0);
  });
});

function cleanEntity(objectId: string): ModuleEntity {
  return {
    id: `module:idea/${objectId}`,
    familyId: "ideas",
    family: "idea",
    moduleId: `idea/${objectId}`,
    objectId,
    title: objectId,
    subtitle: objectId,
    root: `${PROJECT_ROOT}/src/modules/idea/${objectId}`,
    relativeRoot: `src/modules/idea/${objectId}`,
    sourceRoot: `${PROJECT_ROOT}/src`,
    layout: "canonical",
    sourceCount: 1,
    sourceSlots: [
      {
        slot: "def",
        name: "def.pdx",
        path: SOURCE_PATH.replace("IDEA_ALPHA", objectId),
        relative_path: `src/modules/idea/${objectId}/def.pdx`,
        extension: "pdx",
        draftKey: "def",
        editorKind: "code"
      }
    ],
    tags: [],
    draftState: "clean",
    drafts: { text: {} }
  };
}

function modifiedEntity(
  objectId: string,
  text = "edited = yes\n"
): ModuleEntity {
  return {
    ...cleanEntity(objectId),
    draftState: "modified",
    drafts: { text: { def: text } }
  };
}

function diagramDocument(x: number): DiagramDocument {
  return {
    schemaVersion: 1,
    gridSizePx: 24,
    nodes: [
      {
        id: "FOCUS_A",
        order: 0,
        mode: "absolute",
        fixed: true,
        x,
        y: 0,
        width: 4,
        height: 2
      }
    ],
    edges: []
  };
}

function runtimeFormValues(
  values: Readonly<Record<string, unknown>>
): Readonly<Record<string, string>> {
  return values as Readonly<Record<string, string>>;
}
