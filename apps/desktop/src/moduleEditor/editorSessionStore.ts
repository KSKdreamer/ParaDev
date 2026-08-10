import type { DiagramHistory } from "../diagramEditor/diagramHistory";
import { moduleCatalogFamilyKey } from "../moduleCatalog";
import { canonicalFamilyId } from "../projectModules";
import type {
  CollectionScaffoldPayload,
  ModuleCreateBatchPayload,
  ModuleCreateBatchRow,
  ParaDevAiChatSourceFormUpdateRequest,
  ScaffoldCollectionRequest
} from "../services/paradev";
import type { SourceFormUpdateBatchPlan } from "../types";
import { mergeModuleEntitiesPreservingDrafts, type ModuleEntity } from "./model";

declare const moduleEditorSessionKeyBrand: unique symbol;

/** Opaque identity for one project's canonical module-family editor session. */
export type ModuleEditorSessionKey = string & {
  readonly [moduleEditorSessionKeyBrand]: true;
};

/** Inline create-form state retained independently from its rendered editor. */
export type ModuleEditorInlineCreateState = Readonly<{
  templateId: string;
  objectId: string;
  values: Readonly<Record<string, string>>;
  showAdvanced: boolean;
}>;

/** One retained row in the transactional multi-module authoring dialog. */
export type ModuleEditorBatchCreateRow = Readonly<{
  key: number;
  objectId: string;
  templateId: string;
  values: Readonly<Record<string, string>>;
}>;

/** Restorable user input for one transactional multi-module authoring dialog. */
export type ModuleEditorBatchCreateState = Readonly<{
  open: boolean;
  preview?: Readonly<{
    modules: readonly ModuleCreateBatchRow[];
    plan: ModuleCreateBatchPayload;
    sourceRoot: string | null;
  }>;
  pristineSourceRoot: string;
  pristineTemplateId: string;
  rows: readonly ModuleEditorBatchCreateRow[];
  showAdvanced: boolean;
  sourceRoot: string;
}>;

/** Restorable user input and exact dry plan for one collection scaffold. */
export type ModuleEditorCollectionCreateState = Readonly<{
  open: boolean;
  preview?: Readonly<{
    plan: CollectionScaffoldPayload;
    request: Omit<ScaffoldCollectionRequest, "planHash" | "write">;
  }>;
  pristineSourceRoot: string;
  pristineTemplateId: string;
  templateId: string;
  collectionId: string;
  values: Readonly<Record<string, string>>;
  showAdvanced: boolean;
  sourceRoot: string;
}>;

/** Exact Registry-owned AI source-update plan retained for explicit review. */
export type ModuleEditorSourceUpdateState = Readonly<{
  open: boolean;
  requests: readonly ParaDevAiChatSourceFormUpdateRequest[];
  plan: SourceFormUpdateBatchPlan;
}>;

/** One retained diagram history and the source entities it would currently change. */
export type ModuleEditorDiagramState = Readonly<{
  baseFingerprint: string;
  scopeKey: string;
  history: DiagramHistory;
  changedEntityIds: readonly string[];
}>;

/** Retained repair state after source files were written but Catalog was not. */
export type ModuleEditorCatalogMutationFailure = Readonly<{
  status: "failed" | "unverified";
  message: string;
}>;

/** Immutable authoring state retained for one project and module family. */
export type ModuleEditorSessionState = Readonly<{
  key: ModuleEditorSessionKey;
  projectRoot: string;
  familyId: string;
  busy: boolean;
  dirtyEntities: readonly ModuleEntity[];
  inlineCreate: ModuleEditorInlineCreateState | null;
  batchCreate: ModuleEditorBatchCreateState | null;
  collectionCreate: ModuleEditorCollectionCreateState | null;
  sourceUpdate: ModuleEditorSourceUpdateState | null;
  diagrams: readonly ModuleEditorDiagramState[];
  catalogMutationFailure: ModuleEditorCatalogMutationFailure | null;
}>;

/** Dirty and busy facts suitable for tabs, navigation guards, and close guards. */
export type ModuleEditorSessionSummary = Readonly<{
  key: ModuleEditorSessionKey;
  projectRoot: string;
  familyId: string;
  dirty: boolean;
  busy: boolean;
  dirtyEntityIds: readonly string[];
  dirtyDiagramEntityIds: readonly string[];
  inlineCreateDirty: boolean;
  batchCreateDirty: boolean;
  collectionCreateDirty: boolean;
  sourceUpdateDirty: boolean;
}>;

/** Stable immutable snapshot observed by application-level session guards. */
export type ModuleEditorSessionStoreSnapshot = Readonly<{
  dirty: boolean;
  busy: boolean;
  sessions: readonly ModuleEditorSessionSummary[];
}>;

type Listener = () => void;
type ResourceDisposer = () => void;

type SessionRecord = {
  readonly key: ModuleEditorSessionKey;
  readonly projectRoot: string;
  readonly familyId: string;
  dirtyEntities: readonly ModuleEntity[];
  inlineCreate: ModuleEditorInlineCreateState | null;
  batchCreate: ModuleEditorBatchCreateState | null;
  collectionCreate: ModuleEditorCollectionCreateState | null;
  sourceUpdate: ModuleEditorSourceUpdateState | null;
  diagrams: Map<string, ModuleEditorDiagramState>;
  catalogMutationFailure: ModuleEditorCatalogMutationFailure | null;
  resources: Map<string, ResourceDisposer>;
  busyCount: number;
  state: ModuleEditorSessionState;
};

const EMPTY_STORE_SNAPSHOT: ModuleEditorSessionStoreSnapshot = Object.freeze({
  dirty: false,
  busy: false,
  sessions: Object.freeze([])
});

/**
 * Creates the canonical editor-session key for an SDK-resolved project root.
 *
 * The project root remains case-sensitive because the SDK supplies its
 * canonical filesystem identity. Family aliases normalize through the shared
 * frontend family resolver.
 */
export function moduleEditorSessionKey(
  projectRoot: string,
  familyId: string
): ModuleEditorSessionKey {
  const root = projectRoot.trim();
  const family = canonicalFamilyId(familyId);
  if (!root) {
    throw new Error("Module editor session project root must not be empty.");
  }
  if (!family) {
    throw new Error("Module editor session family must not be empty.");
  }
  return moduleCatalogFamilyKey(root, family) as ModuleEditorSessionKey;
}

/**
 * Owns in-memory module authoring sessions above individual React editors.
 *
 * Session values are cloned and frozen on write. Global subscribers observe
 * only dirty/busy summary changes, while keyed subscribers observe retained
 * authoring-state changes. Owned resources are released only by explicit
 * release or discard, never merely because one editor view unmounts.
 */
export class ModuleEditorSessionStore {
  readonly #records = new Map<ModuleEditorSessionKey, SessionRecord>();
  readonly #listeners = new Set<Listener>();
  readonly #sessionListeners = new Map<ModuleEditorSessionKey, Set<Listener>>();
  #snapshot = EMPTY_STORE_SNAPSHOT;

  /** Returns the referentially stable dirty/busy snapshot. */
  readonly getSnapshot = (): ModuleEditorSessionStoreSnapshot =>
    this.#snapshot;

  /** Subscribes to changes in application-level dirty or busy facts. */
  readonly subscribe = (listener: Listener): (() => void) => {
    this.#listeners.add(listener);
    return () => {
      this.#listeners.delete(listener);
    };
  };

  /** Subscribes to retained authoring-state changes for one session. */
  subscribeSession(
    key: ModuleEditorSessionKey,
    listener: Listener
  ): () => void {
    assertModuleEditorSessionKey(key);
    const listeners = this.#sessionListeners.get(key) ?? new Set<Listener>();
    listeners.add(listener);
    this.#sessionListeners.set(key, listeners);
    return () => {
      listeners.delete(listener);
      if (listeners.size === 0) {
        this.#sessionListeners.delete(key);
      }
    };
  }

  /** Returns the current immutable retained state, or `null` when absent. */
  read(key: ModuleEditorSessionKey): ModuleEditorSessionState | null {
    assertModuleEditorSessionKey(key);
    return this.#records.get(key)?.state ?? null;
  }

  /**
   * Retains only source-changing entities from the editor's current model.
   *
   * Clean SDK rows remain backend-owned and are deliberately not duplicated.
   */
  setDirtyEntities(
    key: ModuleEditorSessionKey,
    entities: readonly ModuleEntity[]
  ): void {
    assertModuleEditorSessionKey(key);
    const dirtyEntities = entities.filter(
      (entity) => entity.draftState !== "clean"
    );
    const current = this.#records.get(key);
    if (!current && dirtyEntities.length === 0) {
      return;
    }
    const record = current ?? this.#createRecord(key);
    const next = immutableClone(dirtyEntities);
    if (sameData(record.dirtyEntities, next)) {
      return;
    }
    record.dirtyEntities = next;
    this.#publishSessionChange(key);
  }

  /**
   * Merges retained dirty rows over a fresh SDK-owned entity collection.
   *
   * Matching backend rows contribute current paths and metadata; retained
   * drafts contribute only their local draft state.
   */
  restoreEntities(
    key: ModuleEditorSessionKey,
    incoming: readonly ModuleEntity[],
    authoritativeEntities?: readonly ModuleEntity[]
  ): ModuleEntity[] {
    assertModuleEditorSessionKey(key);
    const dirtyEntities = this.#records.get(key)?.dirtyEntities ?? [];
    return mergeModuleEntitiesPreservingDrafts(dirtyEntities, incoming, {
      ...(authoritativeEntities === undefined
        ? {}
        : { authoritativeEntities })
    });
  }

  /** Retains or clears the inline create form for one session. */
  setInlineCreate(
    key: ModuleEditorSessionKey,
    state: ModuleEditorInlineCreateState | null
  ): void {
    assertModuleEditorSessionKey(key);
    const current = this.#records.get(key);
    if (!current && state === null) {
      return;
    }
    const record = current ?? this.#createRecord(key);
    const next = state === null ? null : immutableClone(state);
    if (sameData(record.inlineCreate, next)) {
      return;
    }
    record.inlineCreate = next;
    this.#publishSessionChange(key);
  }

  /** Retains or clears the transactional multi-module authoring form. */
  setBatchCreate(
    key: ModuleEditorSessionKey,
    state: ModuleEditorBatchCreateState | null
  ): void {
    assertModuleEditorSessionKey(key);
    const current = this.#records.get(key);
    if (!current && state === null) {
      return;
    }
    const record = current ?? this.#createRecord(key);
    const next = state === null ? null : immutableClone(state);
    if (sameData(record.batchCreate, next)) {
      return;
    }
    record.batchCreate = next;
    this.#publishSessionChange(key);
  }

  /** Retains or clears the guarded collection authoring form. */
  setCollectionCreate(
    key: ModuleEditorSessionKey,
    state: ModuleEditorCollectionCreateState | null
  ): void {
    assertModuleEditorSessionKey(key);
    const current = this.#records.get(key);
    if (!current && state === null) {
      return;
    }
    const record = current ?? this.#createRecord(key);
    const next = state === null ? null : immutableClone(state);
    if (sameData(record.collectionCreate, next)) {
      return;
    }
    record.collectionCreate = next;
    this.#publishSessionChange(key);
  }

  /** Retains or clears one exact AI-guided source-update review. */
  setSourceUpdate(
    key: ModuleEditorSessionKey,
    state: ModuleEditorSourceUpdateState | null
  ): void {
    assertModuleEditorSessionKey(key);
    const current = this.#records.get(key);
    if (!current && state === null) {
      return;
    }
    const record = current ?? this.#createRecord(key);
    const next = state === null ? null : immutableClone(state);
    if (sameData(record.sourceUpdate, next)) {
      return;
    }
    record.sourceUpdate = next;
    this.#publishSessionChange(key);
  }

  /** Retains or clears a Catalog repair requirement across editor remounts. */
  setCatalogMutationFailure(
    key: ModuleEditorSessionKey,
    failure: ModuleEditorCatalogMutationFailure | null
  ): void {
    assertModuleEditorSessionKey(key);
    const current = this.#records.get(key);
    if (!current && failure === null) {
      return;
    }
    const record = current ?? this.#createRecord(key);
    const next = failure === null ? null : immutableClone(failure);
    if (sameData(record.catalogMutationFailure, next)) {
      return;
    }
    record.catalogMutationFailure = next;
    this.#publishSessionChange(key);
  }

  /**
   * Retains or clears a diagram history within a family session.
   *
   * `changedEntityIds` must come from the diagram metadata comparison; view
   * selection and viewport movement therefore remain clean continuity state.
   */
  setDiagram(
    key: ModuleEditorSessionKey,
    scopeKey: string,
    history: DiagramHistory | null,
    changedEntityIds: readonly string[] = [],
    baseFingerprint = ""
  ): void {
    assertModuleEditorSessionKey(key);
    const scope = scopeKey.trim();
    if (!scope) {
      throw new Error("Module editor diagram scope must not be empty.");
    }
    const current = this.#records.get(key);
    if (!current && history === null) {
      return;
    }
    const record = current ?? this.#createRecord(key);
    if (history === null) {
      if (!record.diagrams.delete(scope)) {
        return;
      }
      this.#publishSessionChange(key);
      return;
    }
    const next = immutableClone({
      baseFingerprint,
      scopeKey: scope,
      history,
      changedEntityIds: normalizedIds(changedEntityIds)
    } satisfies ModuleEditorDiagramState);
    if (sameData(record.diagrams.get(scope), next)) {
      return;
    }
    record.diagrams.set(scope, next);
    this.#publishSessionChange(key);
  }

  /**
   * Marks one authoring operation busy and returns its idempotent completion.
   *
   * Busy sessions cannot be discarded because their backend result is still
   * capable of changing project sources.
   */
  beginBusy(key: ModuleEditorSessionKey): () => void {
    assertModuleEditorSessionKey(key);
    const record = this.#records.get(key) ?? this.#createRecord(key);
    record.busyCount += 1;
    this.#publishSessionChange(key);
    let active = true;
    return () => {
      if (!active) {
        return;
      }
      active = false;
      const current = this.#records.get(key);
      if (!current || current.busyCount === 0) {
        return;
      }
      current.busyCount -= 1;
      this.#publishSessionChange(key);
    };
  }

  /**
   * Transfers cleanup ownership for a session resource into the store.
   *
   * Replacing an existing identifier first releases its previous resource.
   */
  ownResource(
    key: ModuleEditorSessionKey,
    resourceId: string,
    dispose: ResourceDisposer
  ): void {
    assertModuleEditorSessionKey(key);
    const id = requiredResourceId(resourceId);
    const record = this.#records.get(key) ?? this.#createRecord(key);
    const previous = record.resources.get(id);
    if (previous === dispose) {
      return;
    }
    previous?.();
    record.resources.set(id, dispose);
  }

  /** Releases one owned resource immediately, retaining other session state. */
  releaseResource(key: ModuleEditorSessionKey, resourceId: string): void {
    assertModuleEditorSessionKey(key);
    const id = requiredResourceId(resourceId);
    const record = this.#records.get(key);
    const dispose = record?.resources.get(id);
    if (!record || !dispose) {
      return;
    }
    dispose();
    record.resources.delete(id);
    if (this.#removeRecordIfEmpty(key)) {
      this.#publishSessionRemoval(key);
    }
  }

  /** Moves one owned resource identifier without disposing the resource. */
  moveResource(
    key: ModuleEditorSessionKey,
    resourceId: string,
    nextResourceId: string
  ): void {
    assertModuleEditorSessionKey(key);
    const currentId = requiredResourceId(resourceId);
    const nextId = requiredResourceId(nextResourceId);
    if (currentId === nextId) {
      return;
    }
    const record = this.#records.get(key);
    const dispose = record?.resources.get(currentId);
    if (!record || !dispose) {
      return;
    }
    const existing = record.resources.get(nextId);
    if (existing && existing !== dispose) {
      throw new Error(
        `Module editor session resource already exists: ${nextId}.`
      );
    }
    record.resources.delete(currentId);
    record.resources.set(nextId, dispose);
  }

  /**
   * Discards one non-busy session after releasing every owned resource.
   *
   * Cleanup failures retain the draft and failed resource ownership so the
   * caller can report the failure and retry without silently losing work.
   */
  discard(key: ModuleEditorSessionKey): boolean {
    assertModuleEditorSessionKey(key);
    const record = this.#records.get(key);
    if (!record) {
      return false;
    }
    if (record.busyCount > 0) {
      throw new Error(
        `Cannot discard busy module editor session: ${record.familyId}.`
      );
    }
    const failures: unknown[] = [];
    for (const [resourceId, dispose] of [...record.resources]) {
      try {
        dispose();
        record.resources.delete(resourceId);
      } catch (error: unknown) {
        failures.push(error);
      }
    }
    if (failures.length > 0) {
      throw new AggregateError(
        failures,
        `Could not release every resource owned by module editor session ${record.familyId}.`
      );
    }
    this.#records.delete(key);
    this.#publishSessionRemoval(key);
    return true;
  }

  /**
   * Discards every session after proving that none has work in flight.
   *
   * Individual cleanup failures are aggregated after all other sessions have
   * had their cleanup attempted.
   */
  discardAll(): number {
    const busy = [...this.#records.values()].filter(
      (record) => record.busyCount > 0
    );
    if (busy.length > 0) {
      throw new Error(
        `Cannot discard module editor sessions while ${busy.length} authoring operation${busy.length === 1 ? " is" : "s are"} running.`
      );
    }
    let discarded = 0;
    const failures: unknown[] = [];
    for (const key of [...this.#records.keys()]) {
      try {
        if (this.discard(key)) {
          discarded += 1;
        }
      } catch (error: unknown) {
        failures.push(error);
      }
    }
    if (failures.length > 0) {
      throw new AggregateError(
        failures,
        "Could not discard every module editor session."
      );
    }
    return discarded;
  }

  #createRecord(key: ModuleEditorSessionKey): SessionRecord {
    const { projectRoot, familyId } = sessionIdentity(key);
    const record: SessionRecord = {
      key,
      projectRoot,
      familyId,
      dirtyEntities: Object.freeze([]),
      inlineCreate: null,
      batchCreate: null,
      collectionCreate: null,
      sourceUpdate: null,
      diagrams: new Map(),
      catalogMutationFailure: null,
      resources: new Map(),
      busyCount: 0,
      state: emptySessionState(key, projectRoot, familyId)
    };
    this.#records.set(key, record);
    return record;
  }

  #publishSessionChange(key: ModuleEditorSessionKey): void {
    if (!this.#removeRecordIfEmpty(key)) {
      const record = this.#records.get(key);
      if (record) {
        record.state = sessionState(record);
      }
    }
    this.#refreshSnapshot();
    this.#emitSession(key);
  }

  #publishSessionRemoval(key: ModuleEditorSessionKey): void {
    this.#refreshSnapshot();
    this.#emitSession(key);
  }

  #removeRecordIfEmpty(key: ModuleEditorSessionKey): boolean {
    const record = this.#records.get(key);
    if (!record || !isEmptyRecord(record)) {
      return false;
    }
    this.#records.delete(key);
    return true;
  }

  #refreshSnapshot(): void {
    const sessions = [...this.#records.values()]
      .map(sessionSummary)
      .filter((session) => session.dirty || session.busy)
      .sort((left, right) => left.key.localeCompare(right.key));
    const next: ModuleEditorSessionStoreSnapshot = Object.freeze({
      dirty: sessions.some((session) => session.dirty),
      busy: sessions.some((session) => session.busy),
      sessions: Object.freeze(sessions)
    });
    if (sameData(this.#snapshot, next)) {
      return;
    }
    this.#snapshot = next;
    for (const listener of [...this.#listeners]) {
      listener();
    }
  }

  #emitSession(key: ModuleEditorSessionKey): void {
    const listeners = this.#sessionListeners.get(key);
    if (!listeners) {
      return;
    }
    for (const listener of [...listeners]) {
      listener();
    }
  }
}

function sessionIdentity(
  key: ModuleEditorSessionKey
): { projectRoot: string; familyId: string } {
  const separator = key.lastIndexOf("::");
  if (separator <= 0 || separator === key.length - 2) {
    throw new Error("Invalid module editor session key.");
  }
  return {
    projectRoot: key.slice(0, separator),
    familyId: key.slice(separator + 2)
  };
}

function assertModuleEditorSessionKey(key: ModuleEditorSessionKey): void {
  sessionIdentity(key);
}

function emptySessionState(
  key: ModuleEditorSessionKey,
  projectRoot: string,
  familyId: string
): ModuleEditorSessionState {
  return Object.freeze({
    key,
    projectRoot,
    familyId,
    busy: false,
    dirtyEntities: Object.freeze([]),
    inlineCreate: null,
    batchCreate: null,
    collectionCreate: null,
    sourceUpdate: null,
    diagrams: Object.freeze([]),
    catalogMutationFailure: null
  });
}

function sessionState(record: SessionRecord): ModuleEditorSessionState {
  return Object.freeze({
    key: record.key,
    projectRoot: record.projectRoot,
    familyId: record.familyId,
    busy: record.busyCount > 0,
    dirtyEntities: record.dirtyEntities,
    inlineCreate: record.inlineCreate,
    batchCreate: record.batchCreate,
    collectionCreate: record.collectionCreate,
    sourceUpdate: record.sourceUpdate,
    catalogMutationFailure: record.catalogMutationFailure,
    diagrams: Object.freeze(
      [...record.diagrams.values()].sort((left, right) =>
        left.scopeKey.localeCompare(right.scopeKey)
      )
    )
  });
}

function sessionSummary(record: SessionRecord): ModuleEditorSessionSummary {
  const dirtyEntityIds = normalizedIds(
    record.dirtyEntities.map((entity) => entity.id)
  );
  const dirtyDiagramEntityIds = normalizedIds(
    [...record.diagrams.values()].flatMap(
      (diagram) => diagram.changedEntityIds
    )
  );
  const inlineCreateDirty = isInlineCreateDirty(record.inlineCreate);
  const batchCreateDirty = isBatchCreateDirty(record.batchCreate);
  const collectionCreateDirty = isCollectionCreateDirty(
    record.collectionCreate
  );
  const sourceUpdateDirty = record.sourceUpdate !== null;
  return Object.freeze({
    key: record.key,
    projectRoot: record.projectRoot,
    familyId: record.familyId,
    dirty:
      dirtyEntityIds.length > 0 ||
      dirtyDiagramEntityIds.length > 0 ||
      inlineCreateDirty ||
      batchCreateDirty ||
      collectionCreateDirty ||
      sourceUpdateDirty ||
      record.catalogMutationFailure !== null ||
      record.resources.size > 0,
    busy: record.busyCount > 0,
    dirtyEntityIds: Object.freeze(dirtyEntityIds),
    dirtyDiagramEntityIds: Object.freeze(dirtyDiagramEntityIds),
    inlineCreateDirty,
    batchCreateDirty,
    collectionCreateDirty,
    sourceUpdateDirty
  });
}

function isInlineCreateDirty(
  state: ModuleEditorInlineCreateState | null
): boolean {
  return Boolean(
    state &&
      (state.objectId.length > 0 || hasMeaningfulFormValues(state.values))
  );
}

function isBatchCreateDirty(
  state: ModuleEditorBatchCreateState | null
): boolean {
  if (!state) {
    return false;
  }
  if (
    state.sourceRoot !== state.pristineSourceRoot ||
    state.rows.length !== 1
  ) {
    return true;
  }
  const row = state.rows[0];
  return Boolean(
    row &&
      (row.objectId.length > 0 ||
        row.templateId !== state.pristineTemplateId ||
        hasMeaningfulFormValues(row.values))
  );
}

function isCollectionCreateDirty(
  state: ModuleEditorCollectionCreateState | null
): boolean {
  return Boolean(
    state &&
      (state.sourceRoot !== state.pristineSourceRoot ||
        state.templateId !== state.pristineTemplateId ||
        state.collectionId.length > 0 ||
        hasMeaningfulFormValues(state.values))
  );
}

function hasMeaningfulFormValues(
  values: Readonly<Record<string, unknown>>
): boolean {
  return Object.values(values).some(
    (value) => value !== "" && value !== undefined
  );
}

function isEmptyRecord(record: SessionRecord): boolean {
  return (
    record.dirtyEntities.length === 0 &&
    record.inlineCreate === null &&
    record.batchCreate === null &&
    record.collectionCreate === null &&
    record.sourceUpdate === null &&
    record.diagrams.size === 0 &&
    record.catalogMutationFailure === null &&
    record.resources.size === 0 &&
    record.busyCount === 0
  );
}

function requiredResourceId(value: string): string {
  const resourceId = value.trim();
  if (!resourceId) {
    throw new Error("Module editor session resource id must not be empty.");
  }
  return resourceId;
}

function normalizedIds(values: readonly string[]): string[] {
  return [
    ...new Set(values.map((value) => value.trim()).filter(Boolean))
  ].sort();
}

function immutableClone<T>(value: T): T {
  const clone = structuredClone(value);
  deepFreeze(clone, new WeakSet());
  return clone;
}

function deepFreeze(value: unknown, seen: WeakSet<object>): void {
  if (!value || typeof value !== "object" || seen.has(value)) {
    return;
  }
  seen.add(value);
  for (const child of Object.values(value)) {
    deepFreeze(child, seen);
  }
  Object.freeze(value);
}

function sameData(left: unknown, right: unknown): boolean {
  return JSON.stringify(left) === JSON.stringify(right);
}
