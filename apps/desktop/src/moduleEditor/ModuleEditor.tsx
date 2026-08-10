import { useCallback, useEffect, useMemo, useRef, useState, useSyncExternalStore, type ChangeEvent, type SetStateAction } from "react";
import { Plus, RefreshCw } from "lucide-react";
import type { BuildTarget } from "../buildPage/buildPageModel";
import { SelectField } from "../components/ui/SelectField";
import { localizedParaDevServiceError } from "../desktopBridgeErrors";
import { applyDiagramHistoryUpdate, applyDiagramPresentUpdate, canRedoDiagramHistory, canUndoDiagramHistory, createDiagramHistory, diagramDocumentFingerprint, redoDiagramHistory, undoDiagramHistory } from "../diagramEditor/diagramHistory";
import type { DiagramHistory } from "../diagramEditor/diagramHistory";
import { importDiagramJsonDraft } from "../diagramEditor/diagramJsonImport";
import { doctrineDiagramNodeEditable } from "../diagramEditor/doctrineDiagram";
import { ProjectDiagramView, type DiagramChangedEntity } from "../diagramEditor/ProjectDiagramView";
import { mioDiagramNodeEditable, mioDiagramOrganizationOptions } from "../diagramEditor/mioDiagram";
import { buildProjectDiagramDocument, type ProjectDiagramNodePayload } from "../diagramEditor/projectDiagram";
import { autoLayoutDiagramDescendants, autoLayoutDiagramDocument, autoLayoutDiagramNode, autoLayoutDiagramSubtree, clearDiagramTreeParent, insertDiagramChildNode, insertDiagramRootNode, makeDiagramSelectedNodeRelative, makeDiagramSubtreeRelative, moveDiagramNode, moveDiagramNodeKeepingDescendants, moveDiagramNodeRelayoutDescendants, moveDiagramSubtree, pinDiagramDocument, pinDiagramSelectedNode, pinDiagramSubtree, removeDiagramNodeOnly, removeDiagramSubtree, reorderDiagramSibling, setDiagramDependencyEdge, setDiagramNodeLayoutHints, setDiagramNodePosition, setDiagramPathEdge, setDiagramReferenceEdge, setDiagramTreeParent, setDiagramViewport, unpinDiagramDocument, unpinDiagramSelectedNode, unpinDiagramSubtree } from "../diagramEditor/layoutModel";
import type { DiagramNodeLayoutHints } from "../diagramEditor/layoutModel";
import type { DiagramChildNodeInput, DiagramDocument, DiagramMoveDelta, DiagramNode, DiagramViewport } from "../diagramEditor/layoutModel";
import { sourceBackedDiagramAdapter, type SourceBackedDiagramAdapterContext } from "../diagramEditor/sourceBackedDiagramAdapters";
import type { Locale, Translator } from "../i18n";
import { canonicalFamilyId, moduleTitleKeyForFamily, projectBrowserFamily, projectDiagramFamilyCapability, projectDiagramNodeIntent, projectDiagramSelectionValues, projectDiagramTitleKeyForFamilyId, supportsProjectDiagramFamily } from "../projectModules";
import { applyProjectDraft, createModuleDraft, editModuleDiagram, hasDesktopBackend, loadModuleDiagram, planProjectSourceFormUpdates, readTextSource, removeCollection, removeModule, renameCollection, setModuleActive, setModuleCollection, sourceDraftRecoveryPathFromError, type CollectionRenamePayload, type CollectionScaffoldPayload, type ModuleCreateBatchPayload, type ModuleDiagramEdgeIntent, type ModuleDiagramEditPayload, type ModuleDiagramPayload, type ModuleDiagramPositionIntent, type ModuleDuplicatePayload, type ModuleRenamePayload, type OpenPathTarget } from "../services/paradev";
import type { CatalogMutationResult, DraftApplyPayload, ModuleCreateIntent, ProjectBrowserItem, ProjectBrowserPayload, ProjectDiagramRelationship, ProjectTemplatesPayload, SourceTextEdit, ThemeName, WorkspaceModuleSelectionTarget } from "../types";
import { buildDiagramMetadataTextDrafts, changedDiagramMetadataEntityIds, changedDiagramMetadataSourceInfoPaths, changedDiagramMetadataSourceInfoRefs, sourceTextEditsForDiagramMetadataDrafts } from "./diagramMetadata";
import type { DiagramMetadataTextDraft } from "./diagramMetadata";
import { diagramNodeIdForEntity, entityIdForDiagramNode } from "./diagramSelection";
import { applyAssetDrafts, applyAssetReplacementPlanToEntity, applyImageReplacementPlanToEntity, applyScaffoldPlanToEntity, applySourceTextPlanToEntity, applyImageDraft, applyGuidedTextDraft, applyInfoDraft, applyTextDraft, buildCreateDraftInput, buildModuleEntities, buildTemplateCreateFields, canApplyAssetDraft, canApplyImageDraft, canApplyInfoDraft, canApplySourceTextDraft, canApplyRemovalDraft, canApplyScaffoldDraft, createDraftEntity, filterAndSortEntities, hasBlockingAssetDraft, markEntitiesForRemoval, nextDraftObjectId, resolveModuleEntityQueryAfterExternalSelection, resolveModuleEntitySelection, selectCollectionCreateTemplates, selectCreateTemplates, selectCreateTemplate, sourceAssetReplacementsForEntity, sourceReplacementsForEntity, sourceFormUpdatesForEntity, sourceTextEditsForEntity, sourceTextEditsWithSourceFormPlan, shouldRefreshAfterScaffoldApply, type ModuleEntity, type ModuleAssetDraft, type ModuleEntityDrafts } from "./model";
import { ModuleEntityDetails } from "./ModuleEntityDetails";
import { ModuleEntityList } from "./ModuleEntityList";
import { ModuleCreateDialog } from "./ModuleCreateDialog";
import { ModuleDuplicateDialog } from "./ModuleDuplicateDialog";
import { CollectionCreateDialog } from "./CollectionCreateDialog";
import { DiagramNodeCreateDialog } from "./DiagramNodeCreateDialog";
import { SourceUpdateReviewDialog } from "./SourceUpdateReviewDialog";
import { ModuleEditorSessionStore, moduleEditorSessionKey, type ModuleEditorBatchCreateState, type ModuleEditorCatalogMutationFailure, type ModuleEditorCollectionCreateState, type ModuleEditorDiagramState, type ModuleEditorInlineCreateState, type ModuleEditorSessionKey, type ModuleEditorSourceUpdateState } from "./editorSessionStore";
import { moduleFamilySummary } from "./moduleFamilySummary";
import { useModuleCatalogFamily } from "./useModuleCatalogFamily";

type ModuleEditorProps = {
  batchRecoveryPaths?: string[];
  browser: ProjectBrowserPayload | null;
  familyId: string;
  familyTitle?: string;
  gameRoot?: string;
  loadError?: string | null;
  loading?: boolean;
  moduleCreateIntent?: ModuleCreateIntent | null;
  onBuildTarget?: (target: BuildTarget) => void;
  onBatchRecoveryPathsChange?: (paths: string[]) => void;
  onModuleCreateIntentConsumed?: (nonce: number) => void;
  onPinTab: () => void;
  onOpenModuleEntity?: (target: WorkspaceModuleSelectionTarget) => void;
  onModuleSelectionTargetChange?: (target: WorkspaceModuleSelectionTarget | null) => void;
  onProjectRefresh: (projectRoot?: string, fallbackProjectId?: string) => Promise<void>;
  openTarget: OpenPathTarget;
  projectRoot?: string;
  selectedEntityId?: string;
  selectedSourcePath?: string;
  sessionStore?: ModuleEditorSessionStore;
  surface?: "diagram" | "module";
  templates: ProjectTemplatesPayload | null;
  locale: Locale;
  t: Translator;
  theme: ThemeName;
};

export function ModuleEditor({ batchRecoveryPaths = [], browser, familyId, familyTitle: familyTitleOverride = "", gameRoot, loadError = null, loading = false, moduleCreateIntent = null, onBatchRecoveryPathsChange = () => undefined, onBuildTarget, onModuleCreateIntentConsumed, onOpenModuleEntity, onModuleSelectionTargetChange, onPinTab, onProjectRefresh, openTarget, projectRoot = "", selectedEntityId = "", selectedSourcePath = "", sessionStore, surface = "module", templates, locale, t, theme }: ModuleEditorProps) {
  const [localSessionStore] = useState(() => new ModuleEditorSessionStore());
  const editorSessionStore = sessionStore ?? localSessionStore;
  const sessionProjectRoot = browser?.root.trim() || projectRoot.trim() || "paradev://unavailable";
  const sessionKey = moduleEditorSessionKey(sessionProjectRoot, familyId);
  const subscribeToSession = useCallback((listener: () => void) => editorSessionStore.subscribeSession(sessionKey, listener), [editorSessionStore, sessionKey]);
  const retainedSession = useSyncExternalStore(
    subscribeToSession,
    () => editorSessionStore.read(sessionKey),
    () => null,
  );
  const sessionBusy = retainedSession?.busy ?? false;
  const retainedCatalogMutationFailure = retainedSession?.catalogMutationFailure ?? null;
  const family = projectBrowserFamily(browser, familyId);
  const [query, setQuery] = useState("");
  const [activityFilter, setActivityFilter] = useState<"all" | "active" | "inactive">("all");
  const [selectedId, setSelectedId] = useState(selectedEntityId);
  const [externalSelectionEntityId, setExternalSelectionEntityId] = useState(selectedEntityId);
  const latestEntities = useRef<ModuleEntity[]>([]);
  const handleExternalSelectionMissing = useCallback((entityId: string) => {
    setExternalSelectionEntityId((current) => (current === entityId ? "" : current));
    setSelectedId((current) =>
      current === entityId
        ? (filterAndSortEntities(latestEntities.current, {
            query: "",
            sort: "title",
          })[0]?.id ?? "")
        : current,
    );
  }, []);
  const catalog = useModuleCatalogFamily({
    browser,
    ...(retainedCatalogMutationFailure
      ? {
          catalogMutationBypass: retainedCatalogMutationFailure.status === "failed" ? ("failed" as const) : ("unknown" as const),
        }
      : {}),
    externalSelectionEntityId,
    familyId,
    onExternalSelectionMissing: handleExternalSelectionMissing,
    query,
    selectedId,
    surface,
    t,
  });
  const catalogReconcileMutation = useRef(catalog.reconcileMutation);
  catalogReconcileMutation.current = catalog.reconcileMutation;
  const sourceEntities = useMemo(() => (browser ? buildModuleEntities(browser, familyId, locale) : []), [browser, familyId, locale]);
  const baseEntities = useMemo(() => (catalog.effectiveBrowser === browser ? sourceEntities : catalog.effectiveBrowser ? buildModuleEntities(catalog.effectiveBrowser, familyId, locale) : []), [browser, catalog.effectiveBrowser, familyId, locale, sourceEntities]);
  const authoritativeEntities = useMemo(() => {
    if (!browser || Object.keys(browser.filters).length > 0) {
      return undefined;
    }
    const browserFamily = projectBrowserFamily(browser, familyId);
    return browserFamily && sourceEntities.length === browserFamily.item_count ? sourceEntities : undefined;
  }, [browser, familyId, sourceEntities]);
  const templateFamily = family?.family ?? familyId;
  const familyTitleKey = moduleTitleKeyForFamily(family);
  const familyTitle = familyTitleKey ? t(familyTitleKey) : family?.title || familyTitleOverride || familyId;
  const diagramTitleKey = projectDiagramTitleKeyForFamilyId(browser, familyId);
  const sourceBackedDiagramCapability = surface === "diagram" ? projectDiagramFamilyCapability(browser, familyId) : undefined;
  const diagramTitle = diagramTitleKey ? t(diagramTitleKey) : (sourceBackedDiagramCapability?.title ?? familyTitle);
  const metadataDiagramEditable = sourceBackedDiagramCapability?.editable ?? false;
  const sourceBackedDiagram = sourceBackedDiagramCapability?.sourceBacked === true;
  const diagramAdapter = sourceBackedDiagramAdapter(sourceBackedDiagramCapability?.renderer);
  const sourceBackedTechnologyDiagram = sourceBackedDiagram && sourceBackedDiagramCapability?.renderer === "technology";
  const sourceBackedFocusDiagram = sourceBackedDiagram && sourceBackedDiagramCapability?.renderer === "focus-tree";
  const sourceBackedMioDiagram = sourceBackedDiagram && sourceBackedDiagramCapability?.renderer === "mio-trait";
  const projectScopedMioDiagram = sourceBackedMioDiagram && sourceBackedDiagramCapability.initialScope === "project";
  const sourceBackedDoctrineDiagram = sourceBackedDiagram && sourceBackedDiagramCapability?.renderer === "doctrine";
  const sourceBackedModuleDiagram = sourceBackedDiagram && sourceBackedDiagramCapability?.authoringKind === "module";
  const sourceBackedNodeDiagram = sourceBackedDiagram && sourceBackedDiagramCapability?.authoringKind === "diagram-node";
  const createTemplates = useMemo(() => selectCreateTemplates(templates, templateFamily), [templateFamily, templates]);
  const collectionCreateTemplates = useMemo(() => selectCollectionCreateTemplates(templates, templateFamily), [templateFamily, templates]);
  const createUnavailableReason = createTemplates.length === 0 ? t("workspace.module.editor.create.unavailable", { title: familyTitle }) : "";
  const retainedInlineCreate = retainedSession?.inlineCreate ?? null;
  const retainedSourceUpdate = retainedSession?.sourceUpdate ?? null;
  const [createTemplateId, setCreateTemplateId] = useState(retainedInlineCreate?.templateId ?? "");
  const createTemplate = useMemo(() => selectCreateTemplate(templates, templateFamily, createTemplateId), [createTemplateId, templateFamily, templates]);
  const createFields = useMemo(() => buildTemplateCreateFields(createTemplate), [createTemplate]);
  const [entities, setEntities] = useState<ModuleEntity[]>(() => editorSessionStore.restoreEntities(sessionKey, baseEntities, authoritativeEntities));
  const entityScopeKey = sessionKey;
  const editorScopeKey = useRef(entityScopeKey);
  const editorScopeToken = useRef(Symbol(entityScopeKey));
  const editorMounted = useRef(true);
  if (editorScopeKey.current !== entityScopeKey) {
    editorScopeKey.current = entityScopeKey;
    editorScopeToken.current = Symbol(entityScopeKey);
  }
  const activeEntityScopeKey = useRef(entityScopeKey);
  const syncedSourceEntitiesByScope = useRef(new Map<ModuleEditorSessionKey, ModuleEntity[]>());
  latestEntities.current = entities;
  const [createObjectId, setCreateObjectId] = useState(retainedInlineCreate?.objectId ?? "");
  const [createValues, setCreateValues] = useState<Record<string, string>>(() => ({ ...(retainedInlineCreate?.values ?? {}) }));
  const [createFormScopeKey, setCreateFormScopeKey] = useState<ModuleEditorSessionKey>(entityScopeKey);
  const [createBusy, setCreateBusy] = useState(false);
  const [createError, setCreateError] = useState("");
  const [batchDialogOpen, setBatchDialogOpen] = useState(retainedSession?.batchCreate?.open ?? false);
  const [collectionCreateOpen, setCollectionCreateOpen] = useState(retainedSession?.collectionCreate?.open ?? false);
  const [duplicateTarget, setDuplicateTarget] = useState<Pick<ModuleEntity, "id" | "moduleId" | "objectId" | "sourceRoot" | "title"> | null>(null);
  const lastBatchCreateIntentNonceRef = useRef(0);
  const lastCollectionCreateIntentNonceRef = useRef(0);
  const lastSourceUpdateIntentNonceRef = useRef(0);
  const [applyBusyId, setApplyBusyId] = useState("");
  const applyBusyEntityCountsRef = useRef(new Map<string, number>());
  const [applyError, setApplyError] = useState("");
  const catalogMutationWarning = retainedCatalogMutationFailureWarning(t, retainedCatalogMutationFailure);
  const retainCatalogMutationFailureForScope = useCallback(
    (mutation: CatalogMutationResult | null | undefined) => {
      const failure = catalogMutationFailureForSession(mutation);
      if (failure !== null) {
        editorSessionStore.setCatalogMutationFailure(sessionKey, failure);
      }
    },
    [editorSessionStore, sessionKey],
  );
  const reconcileCatalogMutationForScope = useCallback(
    (mutation: CatalogMutationResult | null | undefined) => {
      const failure = catalogMutationFailureForSession(mutation);
      const result = catalogReconcileMutation.current(mutation);
      if (result === "latched" && failure === null) {
        return;
      }
      editorSessionStore.setCatalogMutationFailure(sessionKey, failure);
    },
    [editorSessionStore, sessionKey],
  );
  const [diagramApplyBusy, setDiagramApplyBusy] = useState(false);
  const [diagramApplyError, setDiagramApplyError] = useState("");
  const [diagramModuleCreateOpen, setDiagramModuleCreateOpen] = useState(false);
  const [diagramNodeCreateOpen, setDiagramNodeCreateOpen] = useState(false);
  const [diagramMetadataDraftEntities, setDiagramMetadataDraftEntities] = useState<DiagramChangedEntity[] | null>(null);
  const [moduleDiagramPayload, setModuleDiagramPayload] = useState<ModuleDiagramPayload | null>(null);
  const [moduleDiagramLoadError, setModuleDiagramLoadError] = useState("");
  const [moduleDiagramLoading, setModuleDiagramLoading] = useState(false);
  const [moduleDiagramReloadKey, setModuleDiagramReloadKey] = useState(0);
  const [sourceReloadKey, setSourceReloadKey] = useState(0);
  const [showAdvancedCreate, setShowAdvancedCreate] = useState(retainedInlineCreate?.showAdvanced ?? false);
  const [selectedDiagramNodeId, setSelectedDiagramNodeId] = useState("");
  const [openedDiagramNodeId, setOpenedDiagramNodeId] = useState("");
  const [selectedMioOrganizationId, setSelectedMioOrganizationId] = useState("");
  const [diagramHistory, setDiagramHistory] = useState(() => createDiagramHistory(null));
  const latestDiagramHistory = useRef(diagramHistory);
  latestDiagramHistory.current = diagramHistory;
  const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set());
  const [activeSourceContext, setActiveSourceContext] = useState({
    entityId: "",
    sourcePath: "",
  });
  const lastSelectionTargetKey = useRef("");
  const lastReceivedSelectionTargetKey = useRef("");
  const pendingExternalSelectionTargetKey = useRef("");
  const commitEntities = useCallback(
    (action: SetStateAction<ModuleEntity[]>) => {
      const current = latestEntities.current;
      const next = typeof action === "function" ? action(current) : action;
      latestEntities.current = next;
      editorSessionStore.setDirtyEntities(sessionKey, next);
      setEntities(next);
    },
    [editorSessionStore, sessionKey],
  );
  const retainInlineCreate = useCallback(
    (state: ModuleEditorInlineCreateState | null) => {
      editorSessionStore.setInlineCreate(sessionKey, state);
    },
    [editorSessionStore, sessionKey],
  );
  const retainBatchCreate = useCallback(
    (state: ModuleEditorBatchCreateState | null) => {
      editorSessionStore.setBatchCreate(sessionKey, state);
    },
    [editorSessionStore, sessionKey],
  );
  const retainCollectionCreate = useCallback(
    (state: ModuleEditorCollectionCreateState | null) => {
      editorSessionStore.setCollectionCreate(sessionKey, state);
    },
    [editorSessionStore, sessionKey],
  );
  const retainSourceUpdate = useCallback(
    (state: ModuleEditorSourceUpdateState | null) => {
      editorSessionStore.setSourceUpdate(sessionKey, state);
    },
    [editorSessionStore, sessionKey],
  );
  useEffect(() => {
    if (!moduleCreateIntent || moduleCreateIntent.mode !== "batch" || canonicalFamilyId(moduleCreateIntent.familyId) !== canonicalFamilyId(familyId)) {
      return;
    }
    if (lastBatchCreateIntentNonceRef.current !== moduleCreateIntent.nonce) {
      lastBatchCreateIntentNonceRef.current = moduleCreateIntent.nonce;
      const retained = editorSessionStore.read(sessionKey)?.batchCreate;
      if (retained && !retained.open) {
        retainBatchCreate({ ...retained, open: true });
      }
      setBatchDialogOpen(true);
      onModuleCreateIntentConsumed?.(moduleCreateIntent.nonce);
    }
  }, [editorSessionStore, familyId, moduleCreateIntent, onModuleCreateIntentConsumed, retainBatchCreate, sessionKey]);
  useEffect(() => {
    if (!moduleCreateIntent || moduleCreateIntent.mode !== "collection" || canonicalFamilyId(moduleCreateIntent.familyId) !== canonicalFamilyId(familyId)) {
      return;
    }
    if (lastCollectionCreateIntentNonceRef.current !== moduleCreateIntent.nonce) {
      lastCollectionCreateIntentNonceRef.current = moduleCreateIntent.nonce;
      const retained = editorSessionStore.read(sessionKey)?.collectionCreate;
      if (retained && !retained.open) {
        retainCollectionCreate({ ...retained, open: true });
      }
      setCollectionCreateOpen(true);
      onModuleCreateIntentConsumed?.(moduleCreateIntent.nonce);
    }
  }, [editorSessionStore, familyId, moduleCreateIntent, onModuleCreateIntentConsumed, retainCollectionCreate, sessionKey]);
  useEffect(() => {
    if (!moduleCreateIntent || moduleCreateIntent.mode !== "source-update" || canonicalFamilyId(moduleCreateIntent.familyId) !== canonicalFamilyId(familyId)) {
      return;
    }
    if (lastSourceUpdateIntentNonceRef.current !== moduleCreateIntent.nonce) {
      lastSourceUpdateIntentNonceRef.current = moduleCreateIntent.nonce;
      onModuleCreateIntentConsumed?.(moduleCreateIntent.nonce);
    }
  }, [familyId, moduleCreateIntent, onModuleCreateIntentConsumed]);
  const filteredEntities = useMemo(
    () =>
      filterAndSortEntities(
        entities.filter((entity) => (activityFilter === "all" ? true : activityFilter === "active" ? entity.active !== false : entity.active === false)),
        { query, sort: "title" },
      ),
    [activityFilter, entities, query],
  );
  const familySummary = moduleFamilySummary(
    {
      filtered: activityFilter !== "all" || Boolean(query.trim()),
      loadedCount: catalog.loadedCount ?? entities.length,
      sourceCount: family?.source_count ?? 0,
      totalCount: catalog.totalCount ?? entities.length,
      visibleCount: filteredEntities.length,
    },
    t,
  );
  const selectedEntity = entities.find((entity) => entity.id === selectedId) ?? (catalog.enabled && selectedEntityId && selectedId === selectedEntityId ? null : (filteredEntities[0] ?? null));
  const selectedBuildFamily = selectedEntity?.family.trim() ?? "";
  const selectedBuildTarget = selectedEntity?.moduleId?.trim() ? { id: selectedEntity.moduleId.trim(), kind: "module" as const } : selectedEntity?.collectionId?.trim() ? { id: selectedEntity.collectionId.trim(), kind: "collection" as const } : null;
  const selectedEntityCanApply = !hasBlockingAssetDraft(selectedEntity) && (canApplyScaffoldDraft(selectedEntity) || canApplyAssetDraft(selectedEntity) || canApplySourceTextDraft(selectedEntity) || canApplyRemovalDraft(selectedEntity) || canApplyImageDraft(selectedEntity) || canApplyInfoDraft(selectedEntity));
  const selectedEntityMutationBlocked = catalog.catalogMutationDirty && isModuleIdentityMutationDraft(selectedEntity);
  const selectedEntityCanDuplicate = Boolean(selectedEntity && selectedEntity.draftState === "clean" && selectedEntity.moduleId && !catalog.catalogPreparing && !catalog.catalogMutationDirty && !hasAmbiguousModuleMutationTarget(entities, selectedEntity) && hasDesktopBackend());
  const selectedCollectionOptions = useMemo(() => {
    if (!browser || !selectedEntity?.moduleId) {
      return [];
    }
    return browser.items
      .filter((item) => item.kind === "collection" && item.family === selectedEntity.family && (!selectedEntity.sourceRoot || item.source_root === selectedEntity.sourceRoot) && Boolean(item.collection_id))
      .map((item) => ({
        label: item.title || item.collection_id || item.object_id,
        value: item.collection_id || item.object_id,
      }))
      .sort((left, right) => left.label.localeCompare(right.label, locale));
  }, [browser, locale, selectedEntity]);
  const selectedEntityCanChangeCollection = Boolean(selectedEntity?.moduleId && selectedEntity.draftState === "clean" && !catalog.catalogPreparing && !catalog.catalogMutationDirty && !hasAmbiguousModuleMutationTarget(entities, selectedEntity) && hasDesktopBackend());
  const selectedEntityCanChangeActivity = Boolean(selectedEntity?.moduleId && selectedEntity.draftState === "clean" && !catalog.catalogPreparing && !catalog.catalogMutationDirty && !hasAmbiguousModuleMutationTarget(entities, selectedEntity) && hasDesktopBackend());
  const moduleDiagramProjectRoot = browser?.root ?? "";
  const moduleDiagramProfile = browser?.profile ?? "hoi4";
  const moduleDiagramFamily = sourceBackedDiagramCapability?.sdkFamily ?? "";
  useEffect(() => {
    let cancelled = false;
    if (!sourceBackedDiagram || !moduleDiagramProjectRoot || !moduleDiagramFamily) {
      setModuleDiagramPayload(null);
      setModuleDiagramLoadError("");
      setModuleDiagramLoading(false);
      return () => {
        cancelled = true;
      };
    }
    setModuleDiagramLoading(true);
    setModuleDiagramLoadError("");
    void loadModuleDiagram({
      projectRoot: moduleDiagramProjectRoot,
      family: moduleDiagramFamily,
      profile: moduleDiagramProfile,
    })
      .then((payload) => {
        if (!cancelled) {
          setModuleDiagramPayload(payload);
        }
      })
      .catch((error: unknown) => {
        if (!cancelled) {
          setModuleDiagramPayload(null);
          setModuleDiagramLoadError(localizedParaDevServiceError(t, error));
        }
      })
      .finally(() => {
        if (!cancelled) {
          setModuleDiagramLoading(false);
        }
      });
    return () => {
      cancelled = true;
    };
  }, [browser, moduleDiagramFamily, moduleDiagramProfile, moduleDiagramProjectRoot, moduleDiagramReloadKey, sourceBackedDiagram, t]);
  const diagramScopeEntities = useMemo(() => {
    if (surface !== "diagram" || !supportsDiagramFocusTreeEdits(familyId)) {
      return [];
    }
    const ordered = filterAndSortEntities(entities, {
      query: "",
      sort: "title",
    });
    if (sourceBackedDiagramCapability?.scopeAuthoringKind !== "collection") {
      return ordered;
    }
    const collections = ordered.filter((entity) => entity.kind === "collection");
    return collections.length > 0 ? collections : ordered;
  }, [entities, familyId, sourceBackedDiagramCapability?.scopeAuthoringKind, surface]);
  const activeDiagramScopeEntity = diagramScopeEntities.find((entity) => entity.id === selectedEntity?.id) ?? diagramScopeEntities[0] ?? selectedEntity;
  const explicitlySelectedMioModuleId = !projectScopedMioDiagram && selectedEntityId ? (entities.find((entity) => entity.id === selectedEntityId)?.moduleId ?? selectedEntity?.moduleId ?? "") : "";
  const mioOrganizationOptions = useMemo(() => (sourceBackedMioDiagram && moduleDiagramPayload ? mioDiagramOrganizationOptions(moduleDiagramPayload, locale, explicitlySelectedMioModuleId) : []), [locale, moduleDiagramPayload, explicitlySelectedMioModuleId, sourceBackedMioDiagram]);
  const activeMioOrganizationId = mioOrganizationOptions.some((option) => option.id === selectedMioOrganizationId) ? selectedMioOrganizationId : (mioOrganizationOptions[0]?.id ?? "");
  useEffect(() => {
    setSelectedMioOrganizationId((current) => (current === activeMioOrganizationId ? current : activeMioOrganizationId));
  }, [activeMioOrganizationId]);
  const showDiagramScopeSelector = sourceBackedMioDiagram ? mioOrganizationOptions.length > 1 : diagramScopeEntities.length > 1 || (sourceBackedDiagramCapability?.scopeAuthoringKind === "collection" && collectionCreateTemplates.length > 0 && hasDesktopBackend());
  const mioDiagramScopeEmpty = sourceBackedMioDiagram && moduleDiagramPayload !== null && !moduleDiagramLoading && mioOrganizationOptions.length === 0;
  const diagramBrowser = useMemo(() => browserForDiagramEntity(browser, activeDiagramScopeEntity, surface, familyId), [activeDiagramScopeEntity, browser, surface, familyId]);
  const diagramProjection = useMemo(() => {
    try {
      if (sourceBackedDiagram && !diagramAdapter) {
        throw new Error(
          t("workspace.diagram.rendererUnsupported", {
            renderer: sourceBackedDiagramCapability?.renderer ?? "unknown",
          }),
        );
      }
      const document = sourceBackedDiagram
        ? moduleDiagramPayload && diagramBrowser && diagramAdapter
          ? diagramAdapter.buildDocument({
              browser: diagramBrowser,
              locale,
              payload: moduleDiagramPayload,
              ...(sourceBackedMioDiagram ? { scopeId: activeMioOrganizationId } : {}),
            })
          : null
        : diagramBrowser && supportsProjectDiagramFamily(browser, familyId)
          ? buildProjectDiagramDocument(diagramBrowser, familyId, {
              locale,
            })
          : null;
      return { document, error: "" };
    } catch (error: unknown) {
      return {
        document: null,
        error: error instanceof Error ? error.message : String(error),
      };
    }
  }, [browser, diagramBrowser, diagramAdapter, activeMioOrganizationId, familyId, locale, moduleDiagramPayload, sourceBackedDiagram, sourceBackedDiagramCapability?.renderer, sourceBackedMioDiagram, t]);
  const baseDiagramDocument = diagramProjection.document;
  const moduleDiagramDisplayError = moduleDiagramLoadError || diagramProjection.error;
  const diagramCapabilityResolved = !sourceBackedDiagram || moduleDiagramPayload !== null || Boolean(moduleDiagramDisplayError);
  const diagramEditable = sourceBackedDiagram ? Boolean(diagramAdapter && moduleDiagramPayload?.editable === true) : metadataDiagramEditable;
  const diagramReadOnlyReason = !diagramEditable && sourceBackedDiagramCapability?.readOnlyReasonKey ? t(sourceBackedDiagramCapability.readOnlyReasonKey) : "";
  const diagramSessionScopeKey = sourceBackedMioDiagram && activeMioOrganizationId ? `mio:${activeMioOrganizationId}` : supportsDiagramFocusTreeEdits(familyId) && activeDiagramScopeEntity ? activeDiagramScopeEntity.id : canonicalFamilyId(familyId);
  const activeDiagramSessionScopeKey = useRef(diagramSessionScopeKey);
  const retainedDiagram = retainedSession?.diagrams.find((diagram) => diagram.scopeKey === diagramSessionScopeKey);
  const restorableDiagram = diagramCapabilityResolved && !diagramEditable && retainedDiagram && retainedDiagram.changedEntityIds.length > 0 ? { ...retainedDiagram, changedEntityIds: [] } : retainedDiagram;
  const baseDiagramFingerprint = useMemo(() => diagramDocumentFingerprint(baseDiagramDocument), [baseDiagramDocument]);
  const diagramDraftBaseFingerprint = restorableDiagram && restorableDiagram.changedEntityIds.length > 0 ? restorableDiagram.baseFingerprint : baseDiagramFingerprint;
  const diagramBaseConflict = Boolean(restorableDiagram && restorableDiagram.changedEntityIds.length > 0 && restorableDiagram.baseFingerprint && baseDiagramDocument && restorableDiagram.baseFingerprint !== baseDiagramFingerprint);
  const diagramDraft = diagramHistory.present;
  const diagramDocument = diagramDraft ?? baseDiagramDocument;
  const sourceBackedDiagramContext = useMemo<SourceBackedDiagramAdapterContext | undefined>(
    () =>
      sourceBackedDiagram && moduleDiagramPayload && diagramBrowser
        ? {
            browser: diagramBrowser,
            locale,
            payload: moduleDiagramPayload,
            ...(sourceBackedMioDiagram ? { scopeId: activeMioOrganizationId } : {}),
          }
        : undefined,
    [activeMioOrganizationId, diagramBrowser, locale, moduleDiagramPayload, sourceBackedDiagram, sourceBackedMioDiagram],
  );
  const sourceBackedDiagramChanges = useMemo(() => {
    if (!sourceBackedDiagram || !diagramAdapter || !sourceBackedDiagramContext || !baseDiagramDocument || !diagramDraft) {
      return { ids: [] as string[], error: "" };
    }
    try {
      return {
        ids: diagramAdapter.changedNodeIds(sourceBackedDiagramContext, baseDiagramDocument, diagramDraft),
        error: "",
      };
    } catch (error: unknown) {
      return {
        ids: [`${moduleDiagramFamily || "diagram"}-invalid-draft`],
        error: error instanceof Error ? error.message : String(error),
      };
    }
  }, [baseDiagramDocument, diagramAdapter, diagramDraft, moduleDiagramFamily, sourceBackedDiagram, sourceBackedDiagramContext]);
  const diagramMetadataChangedEntityIds = useMemo(() => (sourceBackedDiagram ? sourceBackedDiagramChanges.ids : baseDiagramDocument && diagramDraft ? changedDiagramMetadataEntityIds(baseDiagramDocument, diagramDraft) : []), [baseDiagramDocument, diagramDraft, sourceBackedDiagram, sourceBackedDiagramChanges.ids]);
  const diagramMetadataChangedEntities = useMemo<DiagramChangedEntity[]>(
    () =>
      sourceBackedDiagram
        ? diagramAdapter && baseDiagramDocument
          ? sourceBackedDiagramChanges.ids.map((id) => {
              const node = baseDiagramDocument.nodes.find((candidate) => candidate.id === id);
              const path = diagramAdapter.sourcePath(baseDiagramDocument, id);
              return {
                id,
                ...(path ? { path } : {}),
                ...(node?.title ? { title: node.title } : {}),
              };
            })
          : []
        : buildDiagramChangedEntities(baseDiagramDocument, diagramDraft, entities),
    [baseDiagramDocument, diagramAdapter, diagramDraft, entities, sourceBackedDiagram, sourceBackedDiagramChanges.ids],
  );
  const diagramDirty = diagramMetadataChangedEntityIds.length > 0;
  const commitDiagramHistory = useCallback(
    (action: SetStateAction<DiagramHistory>) => {
      const current = latestDiagramHistory.current;
      const next = typeof action === "function" ? action(current) : action;
      let changedEntityIds: string[] = [];
      if (baseDiagramDocument && next.present) {
        try {
          const changedNodeIds = sourceBackedDiagram && diagramAdapter && sourceBackedDiagramContext ? diagramAdapter.changedNodeIds(sourceBackedDiagramContext, baseDiagramDocument, next.present) : changedDiagramMetadataEntityIds(baseDiagramDocument, next.present);
          changedEntityIds = sourceBackedDiagram ? sourceBackedDiagramSessionEntityIds(baseDiagramDocument, changedNodeIds) : changedNodeIds;
        } catch {
          changedEntityIds = [`${moduleDiagramFamily || "diagram"}-invalid-draft`];
        }
      }
      latestDiagramHistory.current = next;
      editorSessionStore.setDiagram(sessionKey, diagramSessionScopeKey, next, changedEntityIds, diagramDraftBaseFingerprint);
      setDiagramHistory(next);
    },
    [baseDiagramDocument, diagramAdapter, diagramDraftBaseFingerprint, diagramSessionScopeKey, editorSessionStore, moduleDiagramFamily, sessionKey, sourceBackedDiagram, sourceBackedDiagramContext],
  );
  const diagramChangedEntitiesForView = diagramMetadataDraftEntities ?? diagramMetadataChangedEntities;
  const showDiagram = surface === "diagram" && shouldShowProjectDiagram(browser, familyId, diagramDocument);
  const selectedDiagramNodeIdForEditor = useMemo(() => diagramNodeIdForEntity(selectedEntity, diagramDocument, selectedDiagramNodeId), [diagramDocument, selectedDiagramNodeId, selectedEntity]);
  const selectedRawDiagramNode = useMemo(() => moduleDiagramPayload?.nodes.find((node) => node.id === selectedDiagramNodeIdForEditor), [moduleDiagramPayload, selectedDiagramNodeIdForEditor]);
  const diagramModuleInitialValues = useMemo(() => projectDiagramSelectionValues(sourceBackedDiagramCapability, selectedRawDiagramNode), [selectedRawDiagramNode, sourceBackedDiagramCapability]);
  const diagramNodeInitialIntent = useMemo(() => projectDiagramNodeIntent(sourceBackedDiagramCapability, selectedRawDiagramNode), [selectedRawDiagramNode, sourceBackedDiagramCapability]);
  useEffect(() => {
    setCollectionCreateOpen(editorSessionStore.read(entityScopeKey)?.collectionCreate?.open ?? false);
  }, [editorSessionStore, entityScopeKey]);
  useEffect(() => {
    setDiagramNodeCreateOpen(false);
  }, [selectedDiagramNodeIdForEditor]);
  const selectedEmbeddedDiagramNodeId = selectedEntity && selectedDiagramNodeIdForEditor && selectedDiagramNodeIdForEditor !== selectedEntity.objectId && selectedDiagramNodeIdForEditor !== selectedEntity.moduleId ? selectedDiagramNodeIdForEditor : "";
  const createFallbackTitle = t("workspace.module.editor.newTitle", {
    title: familyTitle,
  });
  const createFallbackObjectId = useMemo(() => nextDraftObjectId(familyId, entities, createTemplate), [createTemplate, entities, familyId]);
  const createInput = useMemo(() => buildCreateDraftInput(createTemplate, createObjectId, createValues, createFallbackTitle, createFallbackObjectId), [createFallbackObjectId, createFallbackTitle, createObjectId, createTemplate, createValues]);
  const selectedSourceContextPath = activeSourceContext.entityId === selectedEntity?.id ? activeSourceContext.sourcePath : "";
  const externalSourceContextPath = selectedEntity?.id === selectedEntityId ? selectedSourcePath : "";
  const selectionTarget = useMemo(() => moduleSelectionTargetForEntity(selectedEntity, familyId, selectedSourceContextPath || externalSourceContextPath), [externalSourceContextPath, familyId, selectedEntity, selectedSourceContextPath]);
  const handleActiveSourcePathChange = useCallback((entityId: string, sourcePath: string) => {
    setActiveSourceContext((current) => (current.entityId === entityId && current.sourcePath === sourcePath ? current : { entityId, sourcePath }));
  }, []);

  useEffect(() => {
    editorMounted.current = true;
    return () => {
      editorMounted.current = false;
      editorScopeToken.current = Symbol("unmounted");
    };
  }, []);

  useEffect(() => {
    setCreateBusy(false);
    setCreateError("");
    applyBusyEntityCountsRef.current.clear();
    setApplyBusyId("");
    setApplyError("");
    setDiagramApplyBusy(false);
    setDiagramApplyError("");
    setCollectionCreateOpen(editorSessionStore.read(entityScopeKey)?.collectionCreate?.open ?? false);
    setDiagramModuleCreateOpen(false);
    setDiagramNodeCreateOpen(false);
  }, [editorSessionStore, entityScopeKey]);

  useEffect(() => {
    const scopeChanged = activeEntityScopeKey.current !== entityScopeKey;
    const previousScopeKey = activeEntityScopeKey.current;
    const previousSourceEntities = syncedSourceEntitiesByScope.current.get(entityScopeKey);
    const sourceEntitiesChanged = previousSourceEntities === undefined || !sameSerializableData(previousSourceEntities, sourceEntities);
    if (scopeChanged) {
      editorSessionStore.setDirtyEntities(previousScopeKey, latestEntities.current);
      activeEntityScopeKey.current = entityScopeKey;
    }
    if (catalog.bypassed) {
      if (!scopeChanged && !sourceEntitiesChanged) {
        return;
      }
      const next = editorSessionStore.restoreEntities(entityScopeKey, sourceEntities, authoritativeEntities);
      if (!sameSerializableData(latestEntities.current, next)) {
        latestEntities.current = next;
        setEntities(next);
      }
      syncedSourceEntitiesByScope.current.set(entityScopeKey, sourceEntities);
      setSelectedId((selected) => (next.some((entity) => entity.id === selected) ? selected : selectedEntityId && next.some((entity) => entity.id === selectedEntityId) ? selectedEntityId : (filterAndSortEntities(next, { query: "", sort: "title" })[0]?.id ?? "")));
      if (scopeChanged) {
        setSelectedDiagramNodeId("");
        setOpenedDiagramNodeId("");
        setSelectedIds(new Set());
        setQuery("");
      }
      return;
    }
    const next = editorSessionStore.restoreEntities(entityScopeKey, baseEntities, authoritativeEntities);
    if (!sameSerializableData(latestEntities.current, next)) {
      latestEntities.current = next;
      setEntities(next);
    }
    if (catalog.effectiveBrowser === browser) {
      syncedSourceEntitiesByScope.current.set(entityScopeKey, sourceEntities);
    }
    setSelectedId((selected) => (next.some((entity) => entity.id === selected) ? selected : selectedEntityId && (catalog.enabled || next.some((entity) => entity.id === selectedEntityId)) ? selectedEntityId : (filterAndSortEntities(next, { query: "", sort: "title" })[0]?.id ?? "")));
    if (scopeChanged || surface === "diagram") {
      setSelectedDiagramNodeId("");
      setOpenedDiagramNodeId("");
      setSelectedIds(new Set());
    }
    if (scopeChanged) {
      setQuery("");
    }
  }, [authoritativeEntities, baseEntities, browser, catalog.bypassed, catalog.effectiveBrowser, catalog.enabled, editorSessionStore, entityScopeKey, retainedSession, selectedEntityId, sourceEntities, surface]);

  useEffect(() => {
    const scopeChanged = activeDiagramSessionScopeKey.current !== diagramSessionScopeKey;
    activeDiagramSessionScopeKey.current = diagramSessionScopeKey;
    const nextHistory = restoredDiagramHistory(restorableDiagram, baseDiagramDocument);
    if (diagramCapabilityResolved && !diagramEditable && retainedDiagram && retainedDiagram.changedEntityIds.length > 0) {
      editorSessionStore.setDiagram(sessionKey, diagramSessionScopeKey, nextHistory, [], baseDiagramFingerprint);
    }
    if (!sameSerializableData(latestDiagramHistory.current, nextHistory)) {
      latestDiagramHistory.current = nextHistory;
      setDiagramHistory(nextHistory);
    }
    const nextNodeIds = new Set(nextHistory.present?.nodes.map((node) => node.id) ?? []);
    setSelectedDiagramNodeId((current) => (scopeChanged || (current && !nextNodeIds.has(current)) ? "" : current));
    setOpenedDiagramNodeId((current) => (scopeChanged || (current && !nextNodeIds.has(current)) ? "" : current));
  }, [baseDiagramDocument, baseDiagramFingerprint, diagramCapabilityResolved, diagramEditable, diagramSessionScopeKey, editorSessionStore, restorableDiagram, retainedDiagram, sessionKey]);

  useEffect(() => {
    let cancelled = false;
    setDiagramMetadataDraftEntities(null);
    if (sourceBackedDiagram || !browser || !baseDiagramDocument || !diagramDraft || !diagramDirty || !hasDesktopBackend()) {
      return () => {
        cancelled = true;
      };
    }
    void loadDiagramMetadataTextDrafts(browser.project_id, browser.root, baseDiagramDocument, diagramDraft, entities)
      .then((drafts) => {
        if (!cancelled) {
          setDiagramMetadataDraftEntities(buildDiagramChangedEntitiesWithDraftTexts(diagramMetadataChangedEntities, drafts, entities));
        }
      })
      .catch(() => {
        if (!cancelled) {
          setDiagramMetadataDraftEntities(null);
        }
      });
    return () => {
      cancelled = true;
    };
  }, [baseDiagramDocument, browser, diagramDirty, diagramDraft, diagramMetadataChangedEntities, entities, sourceBackedDiagram]);

  useEffect(() => {
    const inlineCreate = editorSessionStore.read(entityScopeKey)?.inlineCreate;
    setCreateTemplateId(inlineCreate?.templateId ?? "");
    setCreateObjectId(inlineCreate?.objectId ?? "");
    setCreateValues({ ...(inlineCreate?.values ?? {}) });
    setShowAdvancedCreate(inlineCreate?.showAdvanced ?? false);
    setBatchDialogOpen(editorSessionStore.read(entityScopeKey)?.batchCreate?.open ?? false);
    setDuplicateTarget(null);
    setCreateFormScopeKey(entityScopeKey);
  }, [editorSessionStore, entityScopeKey]);

  useEffect(() => {
    if (createFormScopeKey !== entityScopeKey || !projectTemplatesMatchEditorScope(templates, browser, sessionProjectRoot)) {
      return;
    }
    if (createTemplates.length === 0) {
      return;
    }
    if (!createTemplates.some((template) => template.id === createTemplateId)) {
      const nextTemplateId = createTemplates[0].id;
      setCreateTemplateId(nextTemplateId);
      retainInlineCreate({
        templateId: nextTemplateId,
        objectId: createObjectId,
        values: createValues,
        showAdvanced: showAdvancedCreate,
      });
    }
  }, [createFormScopeKey, createObjectId, createTemplateId, createTemplates, createValues, entityScopeKey, retainInlineCreate, showAdvancedCreate, templates]);

  useEffect(() => {
    setSelectedId((current) => (catalog.enabled && externalSelectionEntityId && !entities.some((entity) => entity.id === externalSelectionEntityId) ? externalSelectionEntityId : catalog.enabled && selectedEntityId && !entities.some((entity) => entity.id === selectedEntityId) ? selectedEntityId : resolveModuleEntitySelection(current, entities, filteredEntities)));
  }, [catalog.enabled, entities, externalSelectionEntityId, filteredEntities, selectedEntityId]);

  useEffect(() => {
    setApplyError("");
  }, [familyId, selectedId]);

  useEffect(() => {
    if (!onModuleSelectionTargetChange) {
      return;
    }
    if (!selectionTarget && externalSelectionEntityId) {
      return;
    }
    const key = selectionTargetKey(selectionTarget);
    if (key === lastSelectionTargetKey.current) {
      return;
    }
    lastSelectionTargetKey.current = key;
    onModuleSelectionTargetChange(selectionTarget);
  }, [externalSelectionEntityId, onModuleSelectionTargetChange, selectionTarget]);

  useEffect(() => {
    const receivedTargetKey = selectionTargetKey(
      selectedEntityId
        ? {
            entityId: selectedEntityId,
            familyId,
            ...(selectedSourcePath ? { sourcePath: selectedSourcePath } : {}),
          }
        : null,
    );
    if (lastReceivedSelectionTargetKey.current !== receivedTargetKey) {
      lastReceivedSelectionTargetKey.current = receivedTargetKey;
      const externalTarget = Boolean(receivedTargetKey && receivedTargetKey !== lastSelectionTargetKey.current);
      pendingExternalSelectionTargetKey.current = externalTarget ? receivedTargetKey : "";
      setExternalSelectionEntityId(externalTarget ? selectedEntityId : "");
    }
    if (!receivedTargetKey || pendingExternalSelectionTargetKey.current !== receivedTargetKey || !entities.some((entity) => entity.id === selectedEntityId)) {
      return;
    }
    pendingExternalSelectionTargetKey.current = "";
    setExternalSelectionEntityId((current) => (current === selectedEntityId ? "" : current));
    setSelectedId(selectedEntityId);
    setSelectedIds(new Set());
    setQuery((current) => resolveModuleEntityQueryAfterExternalSelection(current, selectedEntityId, filteredEntities));
  }, [entities, familyId, filteredEntities, selectedEntityId, selectedSourcePath]);

  useEffect(() => {
    const entityIds = new Set(entities.map((entity) => entity.id));
    setSelectedIds((current) => {
      if ([...current].every((id) => entityIds.has(id))) {
        return current;
      }
      return new Set([...current].filter((id) => entityIds.has(id)));
    });
  }, [entities]);

  const isCurrentEditorOperation = (token: symbol): boolean => editorMounted.current && editorScopeToken.current === token;
  const sessionOperationBusy = (): boolean => editorSessionStore.read(sessionKey)?.busy ?? false;

  const handleCreate = async (): Promise<boolean> => {
    if (!browser || createBusy || sessionOperationBusy()) {
      return false;
    }
    if (catalog.catalogPreparing) {
      setCreateError(t("workspace.module.editor.catalogMutationPreparing"));
      return false;
    }
    const operationToken = editorScopeToken.current;
    let draftInput = createInput;
    if (hasDesktopBackend()) {
      const finishBusy = editorSessionStore.beginBusy(sessionKey);
      setCreateBusy(true);
      setCreateError("");
      try {
        const payload = await createModuleDraft({
          projectId: browser.project_id,
          projectRoot: browser.root,
          familyId,
          templateId: createTemplate?.id ?? null,
          objectId: createInput.objectId,
          values: createInput.values,
          write: false,
          force: false,
        });
        if (!isCurrentEditorOperation(operationToken)) {
          return false;
        }
        if (payload.plan.blocked) {
          setCreateError(diagnosticSummary(t, payload.plan.diagnostics));
          return false;
        }
        draftInput = {
          ...createInput,
          objectId: payload.plan.object_id,
          title: payload.plan.values.title ?? createInput.title,
          values: payload.plan.values,
        };
      } catch (error: unknown) {
        if (isCurrentEditorOperation(operationToken)) {
          setCreateError(localizedParaDevServiceError(t, error));
        }
        return false;
      } finally {
        finishBusy();
        if (isCurrentEditorOperation(operationToken)) {
          setCreateBusy(false);
        }
      }
    }
    if (!isCurrentEditorOperation(operationToken)) {
      return false;
    }
    const draft = createDraftEntity(familyId, entities, draftInput.title, createTemplate, draftInput);
    onPinTab();
    commitEntities((current) => [...current, draft]);
    setSelectedId(draft.id);
    setSelectedIds(new Set());
    setCreateObjectId("");
    setCreateValues({});
    retainInlineCreate(null);
    setCreateError("");
    setShowAdvancedCreate(false);
    return true;
  };

  const handleApplyEntity = async (entityId: string) => {
    if (!browser || applyBusyId || sessionOperationBusy()) {
      return;
    }
    if (catalog.catalogPreparing) {
      setApplyError(t("workspace.module.editor.catalogMutationPreparing"));
      return;
    }
    const operationToken = editorScopeToken.current;
    const entity = entities.find((row) => row.id === entityId);
    if (entity?.sourceConflict) {
      setApplyError(t(entity.sourceConflict === "missing" ? "workspace.module.editor.sourceMissing" : "workspace.module.editor.sourceChanged"));
      return;
    }
    if (hasBlockingAssetDraft(entity)) {
      setApplyError(t("workspace.module.editor.assetResolveErrors"));
      return;
    }
    if (!entity || (!canApplyScaffoldDraft(entity) && !canApplyAssetDraft(entity) && !canApplySourceTextDraft(entity) && !canApplyRemovalDraft(entity) && !canApplyImageDraft(entity) && !canApplyInfoDraft(entity))) {
      setApplyError(t("workspace.module.editor.applyUnsupported"));
      return;
    }
    if (catalog.catalogMutationDirty && isModuleIdentityMutationDraft(entity)) {
      setApplyError(t("workspace.module.editor.catalogMutationDirtyBlocked"));
      return;
    }
    if (!hasDesktopBackend()) {
      setApplyError(t("workspace.module.editor.applyRequiresDesktop"));
      return;
    }
    if ((canApplyRemovalDraft(entity) || canApplyInfoDraft(entity)) && hasAmbiguousEntityMutationTarget(entities, entity)) {
      setApplyError(
        t("workspace.module.editor.ambiguousEntityMutation", {
          id: entity.moduleId ?? entity.collectionId ?? entity.id,
        }),
      );
      return;
    }

    applyBusyEntityCountsRef.current.set(entity.id, (applyBusyEntityCountsRef.current.get(entity.id) ?? 0) + 1);
    setApplyBusyId(entity.id);
    setApplyError("");
    const finishBusy = editorSessionStore.beginBusy(sessionKey);
    let operationEntities = entities;
    let pendingRefreshProjectId = "";
    const commitOperationEntities = (update: (current: ModuleEntity[]) => ModuleEntity[]) => {
      operationEntities = update(operationEntities);
      editorSessionStore.setDirtyEntities(sessionKey, operationEntities);
      if (isCurrentEditorOperation(operationToken)) {
        latestEntities.current = operationEntities;
        setEntities(operationEntities);
      }
    };
    const refreshWrittenProject = async (projectId: string) => {
      pendingRefreshProjectId = "";
      await onProjectRefresh(browser.root, projectId);
    };
    const reportResourceCleanupFailure = (error: unknown) => {
      if (isCurrentEditorOperation(operationToken)) {
        setApplyError(localizedParaDevServiceError(t, error));
      }
    };
    const releaseCommittedImageResource = (draftEntity: ModuleEntity | undefined) => {
      try {
        releaseImageDraftResource(editorSessionStore, sessionKey, draftEntity);
      } catch (error: unknown) {
        reportResourceCleanupFailure(error);
      }
    };
    const moveCommittedImageResource = (previousEntity: ModuleEntity, nextEntity: ModuleEntity) => {
      try {
        moveImageDraftResource(editorSessionStore, sessionKey, previousEntity, nextEntity);
      } catch (error: unknown) {
        reportResourceCleanupFailure(error);
      }
    };
    try {
      if (canApplyRemovalDraft(entity)) {
        const payload =
          entity.kind === "collection" && entity.collectionId
            ? await removeCollection({
                projectRoot: browser.root,
                collectionId: entity.collectionId,
                family: entity.family,
                sourceRoot: entity.sourceRoot,
              })
            : await removeModule({
                projectRoot: browser.root,
                moduleId: entity.moduleId ?? "",
                sourceRoot: entity.sourceRoot,
              });
        if (payload.blocked) {
          if (isCurrentEditorOperation(operationToken)) {
            setApplyError(diagnosticSummary(t, payload.diagnostics));
          }
          return;
        }
        if (!payload.removed) {
          if (isCurrentEditorOperation(operationToken)) {
            setApplyError(t("workspace.module.editor.applyDidNotWrite"));
          }
          return;
        }
        pendingRefreshProjectId = payload.project_id;
        commitOperationEntities((current) => current.filter((row) => row.id !== entity.id));
        releaseCommittedImageResource(entity);
        retainCatalogMutationFailureForScope(payload.catalog_mutation);
        if (isCurrentEditorOperation(operationToken)) {
          setSelectedId("");
          reconcileCatalogMutationForScope(payload.catalog_mutation);
        }
        await refreshWrittenProject(payload.project_id);
        return;
      }
      if (canApplySourceTextDraft(entity) || canApplyAssetDraft(entity) || canApplyImageDraft(entity) || canApplyInfoDraft(entity)) {
        let nextEntity = entity;
        let sourceEdits = sourceTextEditsForEntity(entity);
        const sourceFormUpdates = sourceFormUpdatesForEntity(entity);
        if (sourceFormUpdates.length > 0) {
          const sourceFormPlan = await planProjectSourceFormUpdates({
            projectId: browser.project_id,
            projectRoot: browser.root,
            updates: sourceFormUpdates.map(({ sourceKey: _sourceKey, ...update }) => update),
          });
          const merged = sourceTextEditsWithSourceFormPlan(entity, sourceFormPlan);
          if (!merged.ok) {
            if (isCurrentEditorOperation(operationToken)) {
              setApplyError(t("workspace.module.editor.guidedPlanMismatch"));
            }
            return;
          }
          sourceEdits = merged.sourceEdits;
        }
        const imageReplacements = sourceReplacementsForEntity(entity);
        const assetReplacements = sourceAssetReplacementsForEntity(entity);
        const wroteSourceText = sourceEdits.length > 0;
        const wroteImage = imageReplacements.length > 0;
        const wroteAssets = assetReplacements.length > 0;
        const writesIdentity = canApplyInfoDraft(entity);
        const writesModuleIdentity = writesIdentity && Boolean(entity.moduleId);
        const writesCollectionIdentity = writesIdentity && entity.kind === "collection" && Boolean(entity.collectionId);
        let moduleRename:
          | {
              moduleId: string;
              objectId: string;
              sourceRoot?: string;
              title?: string;
            }
          | undefined;
        if (writesModuleIdentity) {
          const objectId = entity.drafts.info?.objectId?.trim() || entity.objectId;
          const title = entity.drafts.info?.title?.trim();
          if (!objectId || !entity.moduleId) {
            if (isCurrentEditorOperation(operationToken)) {
              setApplyError(t("workspace.module.editor.applyUnsupported"));
            }
            return;
          }
          moduleRename = {
            moduleId: entity.moduleId,
            objectId,
            ...(entity.sourceRoot ? { sourceRoot: entity.sourceRoot } : {}),
            ...(title ? { title } : {}),
          };
        }
        const collectionTargetId = writesCollectionIdentity ? entity.drafts.info?.objectId?.trim() || entity.objectId : "";
        if (writesCollectionIdentity && (!collectionTargetId || !entity.collectionId)) {
          if (isCurrentEditorOperation(operationToken)) {
            setApplyError(t("workspace.module.editor.applyUnsupported"));
          }
          return;
        }
        let appliedImageResource: ModuleEntity | undefined;
        if (wroteSourceText || wroteImage || wroteAssets || moduleRename) {
          const payload = await applyProjectDraft({
            projectId: browser.project_id,
            projectRoot: browser.root,
            ...(wroteSourceText ? { sourceEdits } : {}),
            ...(wroteImage || wroteAssets
              ? {
                  sourceReplacements: [...imageReplacements, ...assetReplacements],
                }
              : {}),
            ...(moduleRename ? { moduleRename } : {}),
          });
          if (!payload.written) {
            if (isCurrentEditorOperation(operationToken)) {
              setApplyError(t("workspace.module.editor.applyDidNotWrite"));
            }
            return;
          }
          pendingRefreshProjectId = payload.project_id;
          retainCatalogMutationFailureForScope(payload.catalog_mutation);
          if (isCurrentEditorOperation(operationToken)) {
            reconcileCatalogMutationForScope(payload.catalog_mutation);
          }
          if (wroteSourceText) {
            nextEntity = applySourceTextPlanToEntity(nextEntity, payload);
          }
          if (wroteImage) {
            const imageDraftEntity = nextEntity;
            nextEntity = applyImageReplacementPlanToEntity(nextEntity, payload);
            if (imageDraftEntity.drafts.image && !nextEntity.drafts.image) {
              appliedImageResource = entity;
            }
          }
          if (wroteAssets) {
            nextEntity = applyAssetReplacementPlanToEntity(nextEntity, payload);
          }
          if (moduleRename) {
            if (!payload.module_rename) {
              if (isCurrentEditorOperation(operationToken)) {
                setApplyError(t("workspace.module.editor.applyDidNotWrite"));
              }
              await refreshWrittenProject(payload.project_id);
              return;
            }
            const previousEntity = nextEntity;
            nextEntity = renamedModuleEntity(nextEntity, payload.module_rename);
            moveCommittedImageResource(previousEntity, nextEntity);
          }
        }
        if (writesCollectionIdentity && entity.collectionId) {
          const payload = await renameCollection({
            projectRoot: browser.root,
            collectionId: entity.collectionId,
            targetId: collectionTargetId,
            family: entity.family,
            sourceRoot: entity.sourceRoot,
          });
          pendingRefreshProjectId = payload.project_id;
          retainCatalogMutationFailureForScope(payload.catalog_mutation);
          if (isCurrentEditorOperation(operationToken)) {
            reconcileCatalogMutationForScope(payload.catalog_mutation);
          }
          nextEntity = renamedCollectionEntity(nextEntity, payload);
        }
        commitOperationEntities((current) => current.map((row) => (row.id === entity.id ? nextEntity : row)));
        releaseCommittedImageResource(appliedImageResource);
        if (wroteSourceText && isCurrentEditorOperation(operationToken)) {
          setSourceReloadKey((current) => current + 1);
        }
        if ((moduleRename || writesCollectionIdentity) && isCurrentEditorOperation(operationToken)) {
          setSelectedId(nextEntity.id);
        }
        if (wroteSourceText || wroteImage || wroteAssets || moduleRename || writesCollectionIdentity) {
          await refreshWrittenProject(pendingRefreshProjectId || browser.project_id);
        }
        return;
      }
      if (!entity.drafts.create) {
        setApplyError(t("workspace.module.editor.applyUnsupported"));
        return;
      }
      const payload = await createModuleDraft({
        projectId: browser.project_id,
        projectRoot: browser.root,
        familyId,
        templateId: entity.drafts.create.templateId,
        objectId: entity.objectId,
        values: entity.drafts.create.values,
        write: true,
        force: false,
      });
      if (payload.plan.blocked) {
        if (isCurrentEditorOperation(operationToken)) {
          setApplyError(diagnosticSummary(t, payload.plan.diagnostics));
        }
        return;
      }
      if (!payload.plan.written) {
        if (isCurrentEditorOperation(operationToken)) {
          setApplyError(t("workspace.module.editor.applyDidNotWrite"));
        }
        return;
      }
      pendingRefreshProjectId = payload.project_id;
      const appliedEntity = applyScaffoldPlanToEntity(entity, payload.plan);
      commitOperationEntities((current) => current.map((row) => (row.id === entity.id ? appliedEntity : row)));
      retainCatalogMutationFailureForScope(payload.plan.catalog_mutation);
      if (isCurrentEditorOperation(operationToken)) {
        setSelectedId(appliedEntity.id);
        reconcileCatalogMutationForScope(payload.plan.catalog_mutation);
      }
      if (shouldRefreshAfterScaffoldApply(payload.plan)) {
        await refreshWrittenProject(payload.project_id);
      }
    } catch (error: unknown) {
      if (pendingRefreshProjectId) {
        try {
          await refreshWrittenProject(pendingRefreshProjectId);
        } catch {
          // The original mutation failure remains the most actionable error.
        }
      }
      if (isCurrentEditorOperation(operationToken)) {
        const recoveryPath = sourceDraftRecoveryPathFromError(error, browser.root);
        if (recoveryPath) {
          onBatchRecoveryPathsChange([...new Set([...batchRecoveryPaths, recoveryPath])]);
        }
        setApplyError(recoveryPath ? t("workspace.module.editor.sourceRecoveryRequired") : localizedParaDevServiceError(t, error));
      }
    } finally {
      finishBusy();
      if (isCurrentEditorOperation(operationToken)) {
        const remainingApplyCount = (applyBusyEntityCountsRef.current.get(entity.id) ?? 1) - 1;
        if (remainingApplyCount > 0) {
          applyBusyEntityCountsRef.current.set(entity.id, remainingApplyCount);
        } else {
          applyBusyEntityCountsRef.current.delete(entity.id);
          setApplyBusyId("");
        }
      }
    }
  };

  const handleCreateValueChange = (name: string, value: string) => {
    if (sessionOperationBusy()) {
      return;
    }
    onPinTab();
    const next = { ...createValues, [name]: value };
    setCreateValues(next);
    retainInlineCreate({
      templateId: createTemplateId,
      objectId: createObjectId,
      values: next,
      showAdvanced: showAdvancedCreate,
    });
  };

  const handleBatchApplied = async (payload: ModuleCreateBatchPayload) => {
    retainBatchCreate(null);
    for (const row of payload.modules) {
      if (row.status === "created") {
        reconcileCatalogMutationForScope(batchCatalogMutation(row));
      }
    }
    await onProjectRefresh(browser?.root, payload.project_id);
  };

  const handleBatchDialogClose = () => {
    if (sessionOperationBusy()) {
      return;
    }
    const retained = editorSessionStore.read(sessionKey)?.batchCreate;
    if (retained) {
      retainBatchCreate({ ...retained, open: false });
    }
    setBatchDialogOpen(false);
  };

  const handleCollectionDialogClose = () => {
    if (sessionOperationBusy()) {
      return;
    }
    const retained = editorSessionStore.read(sessionKey)?.collectionCreate;
    if (retained) {
      retainCollectionCreate({ ...retained, open: false });
    }
    setCollectionCreateOpen(false);
  };

  const handleSourceUpdateDialogClose = () => {
    if (!sessionOperationBusy()) {
      retainSourceUpdate(null);
    }
  };

  const handleSourceUpdateApplied = async (payload: DraftApplyPayload) => {
    retainSourceUpdate(null);
    setSourceReloadKey((current) => current + 1);
    setModuleDiagramReloadKey((current) => current + 1);
    try {
      await onProjectRefresh(browser?.root, payload.project_id);
    } catch (cause: unknown) {
      const message = t("workspace.module.editor.sourceUpdate.refreshFailed", {
        message: localizedParaDevServiceError(t, cause),
      });
      setApplyError(message);
      setDiagramApplyError(message);
    }
  };

  const handleOpenDuplicate = () => {
    if (sessionOperationBusy() || !selectedEntity || selectedEntity.draftState !== "clean" || !selectedEntity.moduleId) {
      return;
    }
    if (catalog.catalogPreparing) {
      setApplyError(t("workspace.module.editor.catalogMutationPreparing"));
      return;
    }
    if (catalog.catalogMutationDirty) {
      setApplyError(t("workspace.module.editor.catalogMutationDirtyBlocked"));
      return;
    }
    if (hasAmbiguousModuleMutationTarget(entities, selectedEntity)) {
      setApplyError(
        t("workspace.module.editor.ambiguousModuleMutation", {
          moduleId: selectedEntity.moduleId,
        }),
      );
      return;
    }
    if (!hasDesktopBackend()) {
        setApplyError(t("desktop.error.desktopApplicationRequired"));
      return;
    }
    setApplyError("");
    setDuplicateTarget(selectedEntity);
  };

  const handleDuplicateApplied = async (payload: ModuleDuplicatePayload) => {
    retainCatalogMutationFailureForScope(payload.catalog_mutation);
    reconcileCatalogMutationForScope(payload.catalog_mutation);
    try {
      await onProjectRefresh(browser?.root, payload.project_id);
      const entityId = `module:${payload.module_id}`;
      setSelectedId(entityId);
      setExternalSelectionEntityId(entityId);
      setSelectedIds(new Set());
      setQuery("");
    } catch (cause: unknown) {
      setApplyError(
        t("workspace.module.editor.duplicate.refreshFailed", {
          message: localizedParaDevServiceError(t, cause),
        }),
      );
    }
  };

  const handleDuplicateDialogClose = () => {
    if (!sessionOperationBusy()) {
      setDuplicateTarget(null);
    }
  };

  const handleCollectionChange = async (collectionId: string) => {
    if (sessionOperationBusy() || !selectedEntity?.moduleId || !selectedEntityCanChangeCollection) {
      return;
    }
    const operationToken = editorScopeToken.current;
    const finishBusy = editorSessionStore.beginBusy(sessionKey);
    setApplyError("");
    try {
      const payload = await setModuleCollection({
        projectRoot: browser?.root ?? projectRoot,
        moduleId: selectedEntity.moduleId,
        collectionId: collectionId || null,
        sourceRoot: selectedEntity.sourceRoot,
      });
      if (!isCurrentEditorOperation(operationToken)) {
        return;
      }
      retainCatalogMutationFailureForScope(payload.catalog_mutation);
      reconcileCatalogMutationForScope(payload.catalog_mutation);
      await onProjectRefresh(browser?.root, payload.project_id);
      if (isCurrentEditorOperation(operationToken)) {
        setSourceReloadKey((current) => current + 1);
      }
    } catch (error: unknown) {
      if (isCurrentEditorOperation(operationToken)) {
        setApplyError(localizedParaDevServiceError(t, error));
      }
    } finally {
      finishBusy();
    }
  };

  const handleActivityChange = async (active: boolean) => {
    if (sessionOperationBusy() || !selectedEntity?.moduleId || !selectedEntityCanChangeActivity) {
      return;
    }
    const operationToken = editorScopeToken.current;
    const finishBusy = editorSessionStore.beginBusy(sessionKey);
    setApplyError("");
    try {
      const payload = await setModuleActive({
        projectRoot: browser?.root ?? projectRoot,
        moduleId: selectedEntity.moduleId,
        active,
        sourceRoot: selectedEntity.sourceRoot,
      });
      if (!isCurrentEditorOperation(operationToken)) {
        return;
      }
      retainCatalogMutationFailureForScope(payload.catalog_mutation);
      reconcileCatalogMutationForScope(payload.catalog_mutation);
      await onProjectRefresh(browser?.root, payload.project_id);
      if (isCurrentEditorOperation(operationToken)) {
        setSourceReloadKey((current) => current + 1);
      }
    } catch (error: unknown) {
      if (isCurrentEditorOperation(operationToken)) {
        setApplyError(localizedParaDevServiceError(t, error));
      }
    } finally {
      finishBusy();
    }
  };

  if (loading) {
    return (
      <div aria-busy="true" aria-live="polite" className="empty-tab-panel module-loading-panel" role="status">
        <span aria-hidden="true" className="module-loading-spinner" />
        <p className="label">{surface === "diagram" ? t("workspace.diagram.title") : t("workspace.module.label")}</p>
        <h3>{surface === "diagram" ? t("workspace.diagram.loading.title", { title: familyTitle }) : t("workspace.module.loading.title", { title: familyTitle })}</h3>
        <p>{surface === "diagram" ? t("workspace.diagram.loading.body") : t("workspace.module.loading.body")}</p>
      </div>
    );
  }

  if (loadError) {
    return (
      <div className="empty-tab-panel module-load-error-panel" role="alert">
        <p className="label">{surface === "diagram" ? t("workspace.diagram.title") : t("workspace.module.label")}</p>
        <h3>{surface === "diagram" ? t("workspace.diagram.loadFailed.title") : t("workspace.module.loadFailed.title")}</h3>
        <p>{loadError}</p>
      </div>
    );
  }

  if (!browser) {
    return (
      <div className="empty-tab-panel">
        <p className="label">{surface === "diagram" ? t("workspace.diagram.title") : t("workspace.module.label")}</p>
        <h3>{t("workspace.module.unavailable.title")}</h3>
        <p>{t("workspace.module.unavailable.body")}</p>
      </div>
    );
  }

  const updateEntity = (entityId: string, updater: (entity: ModuleEntity) => ModuleEntity) => {
    if (sessionOperationBusy() || applyBusyEntityCountsRef.current.has(entityId)) {
      return;
    }
    commitEntities((current) => current.map((entity) => (entity.id === entityId ? updater(entity) : entity)));
  };

  const handleRemoveSelected = () => {
    if (sessionOperationBusy()) {
      return;
    }
    const ids = selectedIds.size > 0 ? selectedIds : new Set(selectedId ? [selectedId] : []);
    if ([...ids].some((id) => applyBusyEntityCountsRef.current.has(id))) {
      return;
    }
    if (catalog.catalogMutationDirty) {
      setApplyError(t("workspace.module.editor.catalogMutationDirtyBlocked"));
      return;
    }
    const ambiguousTarget = entities.find((entity) => ids.has(entity.id) && hasAmbiguousEntityMutationTarget(entities, entity));
    if (ambiguousTarget) {
      setApplyError(
        t("workspace.module.editor.ambiguousEntityMutation", {
          id: ambiguousTarget.moduleId ?? ambiguousTarget.collectionId ?? ambiguousTarget.id,
        }),
      );
      return;
    }
    if (ids.size > 0) {
      onPinTab();
    }
    commitEntities((current) => markEntitiesForRemoval(current, ids));
    setSelectedIds(new Set());
  };

  const handleRestore = (entityId: string) => {
    if (sessionOperationBusy() || applyBusyEntityCountsRef.current.has(entityId)) {
      return;
    }
    onPinTab();
    const cleanEntity = baseEntities.find((entity) => entity.id === entityId);
    const currentEntity = entities.find((entity) => entity.id === entityId);
    releaseImageDraftResource(editorSessionStore, sessionKey, currentEntity);
    if (cleanEntity) {
      setSourceReloadKey((current) => current + 1);
    }
    commitEntities((current) => {
      if (!cleanEntity) {
        return current.filter((entity) => entity.id !== entityId);
      }
      return current.map((entity) => (entity.id === entityId ? cleanEntity : entity));
    });
  };

  const handleImageDraft = (entityId: string, image: NonNullable<ModuleEntityDrafts["image"]>) => {
    if (sessionOperationBusy() || applyBusyEntityCountsRef.current.has(entityId)) {
      return;
    }
    const currentEntity = entities.find((entity) => entity.id === entityId);
    const previousUrl = currentEntity?.drafts.image?.previewUrl ?? "";
    if (previousUrl !== image.previewUrl) {
      releaseImageDraftResource(editorSessionStore, sessionKey, currentEntity);
    }
    if (image.previewUrl.startsWith("blob:") && previousUrl !== image.previewUrl) {
      const resourceId = imageDraftResourceId(entityId, image.previewUrl);
      editorSessionStore.ownResource(sessionKey, resourceId, () => {
        URL.revokeObjectURL(image.previewUrl);
      });
    }
    onPinTab();
    updateEntity(entityId, (entity) => applyImageDraft(entity, image));
  };

  const handleAssetDrafts = (entityId: string, assets: ModuleAssetDraft[]) => {
    if (sessionOperationBusy() || applyBusyEntityCountsRef.current.has(entityId)) {
      return;
    }
    onPinTab();
    updateEntity(entityId, (entity) => applyAssetDrafts(entity, assets));
  };

  const handleInfoDraft = (entityId: string, info: NonNullable<ModuleEntityDrafts["info"]>) => {
    if (sessionOperationBusy() || applyBusyEntityCountsRef.current.has(entityId)) {
      return;
    }
    onPinTab();
    updateEntity(entityId, (entity) => applyInfoDraft(entity, info));
  };

  const handleRefreshModule = () => {
    if (sessionOperationBusy() || applyBusyEntityCountsRef.current.has(selectedId)) {
      return;
    }
    setSourceReloadKey((current) => current + 1);
    void onProjectRefresh(browser.root, browser.project_id);
  };

  const handleRepairCatalog = async () => {
    if (sessionOperationBusy()) {
      return;
    }
    if (await catalog.repairCatalog()) {
      editorSessionStore.setCatalogMutationFailure(sessionKey, null);
    }
  };

  const handleSelectEntity = (entityId: string) => {
    setSelectedDiagramNodeId("");
    setOpenedDiagramNodeId("");
    setSelectedId(entityId);
  };

  const handleSelectDiagramScope = (event: ChangeEvent<HTMLSelectElement>) => {
    if (sessionOperationBusy() || diagramApplyBusy || (!sourceBackedMioDiagram && diagramDirty)) {
      return;
    }
    const value = event.currentTarget.value;
    if (sourceBackedMioDiagram) {
      if (!mioOrganizationOptions.some((option) => option.id === value)) {
        return;
      }
      setSelectedMioOrganizationId(value);
      setSelectedDiagramNodeId("");
      setOpenedDiagramNodeId("");
    } else {
      handleSelectEntity(value);
    }
    setDiagramApplyError("");
  };

  const handleSelectDiagramEntity = (entityId: string) => {
    setSelectedId(entityId);
    setQuery((current) => resolveModuleEntityQueryAfterExternalSelection(current, entityId, filteredEntities));
  };

  const updateDiagramDocument = (update: (current: DiagramDocument) => DiagramDocument): boolean => {
    if (sessionOperationBusy()) {
      return false;
    }
    const result = applyDiagramHistoryUpdate(diagramHistory, baseDiagramDocument, update);
    if (!result.changed) {
      return false;
    }
    commitDiagramHistory(result.history);
    return true;
  };

  const handleSelectDiagramNode = (nodeId: string) => {
    setSelectedDiagramNodeId(nodeId);
    setOpenedDiagramNodeId((current) => (current === nodeId ? current : ""));
    if (!diagramDocument) {
      return;
    }
    const entityId = entityIdForDiagramNode(entities, diagramDocument, nodeId);
    if (entityId) {
      handleSelectDiagramEntity(entityId);
    }
  };

  const handleOpenDiagramNode = (nodeId: string) => {
    handleSelectDiagramNode(nodeId);
    setOpenedDiagramNodeId(nodeId);
  };

  const handleOpenDiagramNodeModule = (nodeId: string, sourcePath = "") => {
    if (!diagramDocument) {
      return;
    }
    const entityId = entityIdForDiagramNode(entities, diagramDocument, nodeId);
    if (!entityId) {
      return;
    }
    handleSelectDiagramEntity(entityId);
    setOpenedDiagramNodeId("");
    onOpenModuleEntity?.({ entityId, familyId, sourcePath });
  };

  const handleMoveDiagramNode = (nodeId: string, delta: DiagramMoveDelta) => {
    if ((sourceBackedMioDiagram || sourceBackedDoctrineDiagram) && (!diagramDocument || !(sourceBackedMioDiagram ? mioDiagramNodeEditable(diagramDocument, nodeId) : doctrineDiagramNodeEditable(diagramDocument, nodeId)))) {
      setDiagramApplyError(sourceBackedMioDiagram ? t("workspace.diagram.mio.positionUnavailable") : t("workspace.diagram.readOnly"));
      return;
    }
    const changed = updateDiagramDocument((current) => moveDiagramNode(current, nodeId, delta));
    if (!changed) {
      return;
    }
    onPinTab();
    setDiagramApplyError("");
    setSelectedDiagramNodeId(nodeId);
  };

  const handleMoveDiagramSubtree = (nodeId: string, delta: DiagramMoveDelta) => {
    const changed = updateDiagramDocument((current) => moveDiagramSubtree(current, nodeId, delta));
    if (!changed) {
      return;
    }
    onPinTab();
    setDiagramApplyError("");
    setSelectedDiagramNodeId(nodeId);
  };

  const handleMoveDiagramNodeKeepingDescendants = (nodeId: string, delta: DiagramMoveDelta) => {
    const changed = updateDiagramDocument((current) => moveDiagramNodeKeepingDescendants(current, nodeId, delta));
    if (!changed) {
      return;
    }
    onPinTab();
    setDiagramApplyError("");
    setSelectedDiagramNodeId(nodeId);
  };

  const handleMoveDiagramNodeRelayoutDescendants = (nodeId: string, delta: DiagramMoveDelta) => {
    const changed = updateDiagramDocument((current) => moveDiagramNodeRelayoutDescendants(current, nodeId, delta));
    if (!changed) {
      return;
    }
    onPinTab();
    setDiagramApplyError("");
    setSelectedDiagramNodeId(nodeId);
  };

  const handleReorderDiagramSibling = (nodeId: string, direction: -1 | 1) => {
    const changed = updateDiagramDocument((current) => reorderDiagramSibling(current, nodeId, direction));
    if (!changed) {
      return;
    }
    onPinTab();
    setDiagramApplyError("");
    setSelectedDiagramNodeId(nodeId);
  };

  const handleAddDiagramDependency = (targetId: string, sourceId: string) => {
    const changed = updateDiagramDocument((current) => setDiagramDependencyEdge(current, sourceId, targetId, true));
    if (!changed) {
      return;
    }
    onPinTab();
    setDiagramApplyError("");
    setSelectedDiagramNodeId(targetId);
  };

  const handleAddDiagramUnlock = (sourceId: string, targetId: string) => {
    const changed = updateDiagramDocument((current) => (sourceBackedTechnologyDiagram || sourceBackedDoctrineDiagram ? setDiagramPathEdge(current, sourceId, targetId, true) : setDiagramDependencyEdge(current, sourceId, targetId, true)));
    if (!changed) {
      return;
    }
    onPinTab();
    setDiagramApplyError("");
    setSelectedDiagramNodeId(sourceId);
  };

  const handleRemoveDiagramDependency = (targetId: string, sourceId: string) => {
    const changed = updateDiagramDocument((current) => setDiagramDependencyEdge(current, sourceId, targetId, false));
    if (!changed) {
      return;
    }
    onPinTab();
    setDiagramApplyError("");
    setSelectedDiagramNodeId(targetId);
  };

  const handleRemoveDiagramUnlock = (sourceId: string, targetId: string) => {
    const changed = updateDiagramDocument((current) => (sourceBackedTechnologyDiagram || sourceBackedDoctrineDiagram ? setDiagramPathEdge(current, sourceId, targetId, false) : setDiagramDependencyEdge(current, sourceId, targetId, false)));
    if (!changed) {
      return;
    }
    onPinTab();
    setDiagramApplyError("");
    setSelectedDiagramNodeId(sourceId);
  };

  const handleAddDiagramReference = (sourceId: string, targetId: string) => {
    const changed = updateDiagramDocument((current) => setDiagramReferenceEdge(current, sourceId, targetId, true));
    if (!changed) {
      return;
    }
    onPinTab();
    setDiagramApplyError("");
    setSelectedDiagramNodeId(sourceId);
  };

  const handleRemoveDiagramReference = (sourceId: string, targetId: string) => {
    const changed = updateDiagramDocument((current) => setDiagramReferenceEdge(current, sourceId, targetId, false));
    if (!changed) {
      return;
    }
    onPinTab();
    setDiagramApplyError("");
    setSelectedDiagramNodeId(sourceId);
  };

  const handleSetProviderDiagramRelationship = (relationship: ProjectDiagramRelationship, selectedNodeId: string, relatedNodeId: string, present: boolean) => {
    if (!diagramAdapter) {
      setDiagramApplyError(
        t("workspace.diagram.rendererUnsupported", {
          renderer: sourceBackedDiagramCapability?.renderer ?? "unknown",
        }),
      );
      return;
    }
    const changed = updateDiagramDocument((current) => diagramAdapter.setRelationship(current, relationship, selectedNodeId, relatedNodeId, present));
    if (!changed) {
      return;
    }
    onPinTab();
    setDiagramApplyError("");
    setSelectedDiagramNodeId(selectedNodeId);
  };

  const handleSetDiagramParent = (nodeId: string, parentId: string) => {
    const changed = updateDiagramDocument((current) => setDiagramTreeParent(current, nodeId, parentId));
    if (!changed) {
      return;
    }
    onPinTab();
    setDiagramApplyError("");
    setSelectedDiagramNodeId(nodeId);
  };

  const handleClearDiagramParent = (nodeId: string) => {
    const changed = updateDiagramDocument((current) => clearDiagramTreeParent(current, nodeId));
    if (!changed) {
      return;
    }
    onPinTab();
    setDiagramApplyError("");
    setSelectedDiagramNodeId(nodeId);
  };

  const handleRemoveDiagramNodeOnly = (nodeId: string) => {
    let nextDocument: DiagramDocument | null = null;
    let nextSelectedNodeId = "";
    const changed = updateDiagramDocument((current) => {
      const node = current.nodes.find((candidate) => candidate.id === nodeId);
      const child = current.nodes.find((candidate) => candidate.parentId === nodeId);
      const next = removeDiagramNodeOnly(current, nodeId);
      if (next === current) {
        return current;
      }
      nextDocument = next;
      nextSelectedNodeId = child && next.nodes.some((candidate) => candidate.id === child.id) ? child.id : node?.parentId && next.nodes.some((candidate) => candidate.id === node.parentId) ? node.parentId : (next.nodes[0]?.id ?? "");
      return next;
    });
    if (!changed) {
      return;
    }
    onPinTab();
    setDiagramApplyError("");
    setSelectedDiagramNodeId(nextSelectedNodeId);
    const entityId = nextDocument && nextSelectedNodeId ? entityIdForDiagramNode(entities, nextDocument, nextSelectedNodeId) : "";
    if (entityId) {
      handleSelectDiagramEntity(entityId);
    }
  };

  const handleRemoveDiagramSubtree = (nodeId: string) => {
    let nextDocument: DiagramDocument | null = null;
    let nextSelectedNodeId = "";
    const changed = updateDiagramDocument((current) => {
      const node = current.nodes.find((candidate) => candidate.id === nodeId);
      const next = removeDiagramSubtree(current, nodeId);
      if (next === current) {
        return current;
      }
      nextDocument = next;
      nextSelectedNodeId = node?.parentId && next.nodes.some((candidate) => candidate.id === node.parentId) ? node.parentId : (next.nodes[0]?.id ?? "");
      return next;
    });
    if (!changed) {
      return;
    }
    onPinTab();
    setDiagramApplyError("");
    setSelectedDiagramNodeId(nextSelectedNodeId);
    const entityId = nextDocument && nextSelectedNodeId ? entityIdForDiagramNode(entities, nextDocument, nextSelectedNodeId) : "";
    if (entityId) {
      handleSelectDiagramEntity(entityId);
    }
  };

  const handleInsertDiagramChild = (nodeId: string) => {
    let insertedNodeId = "";
    let insertedEntityId = "";
    const changed = updateDiagramDocument((current) => {
      const parent = current.nodes.find((candidate) => candidate.id === nodeId);
      const payload = parent ? asProjectDiagramNodePayload(parent.payload) : null;
      if (!parent || payload?.embeddedKind !== "focus") {
        return current;
      }
      insertedNodeId = nextDiagramFocusChildId(current, parent.id);
      insertedEntityId = payload.itemId;
      return insertDiagramChildNode(current, parent.id, {
        id: insertedNodeId,
        mode: "auto",
        width: parent.width,
        height: parent.height,
        title: titleFromDiagramIdentifier(insertedNodeId),
        ...(parent.imageUrl ? { imageUrl: parent.imageUrl } : {}),
        payload: {
          ...payload,
          embeddedId: insertedNodeId,
          embeddedKind: "focus" as const,
        },
      });
    });
    if (!changed) {
      return;
    }
    onPinTab();
    setDiagramApplyError("");
    setSelectedDiagramNodeId(insertedNodeId);
    if (insertedEntityId) {
      handleSelectDiagramEntity(insertedEntityId);
    }
  };

  const handleInsertDiagramRoot = () => {
    let insertedNodeId = "";
    let insertedEntityId = "";
    const changed = updateDiagramDocument((current) => {
      const input = rootDiagramFocusNodeInput(current);
      const payload = input ? asProjectDiagramNodePayload(input.payload) : null;
      if (!input || !payload) {
        return current;
      }
      insertedNodeId = input.id;
      insertedEntityId = payload.itemId;
      return insertDiagramRootNode(current, input);
    });
    if (!changed) {
      return;
    }
    onPinTab();
    setDiagramApplyError("");
    setSelectedDiagramNodeId(insertedNodeId);
    if (insertedEntityId) {
      handleSelectDiagramEntity(insertedEntityId);
    }
  };

  const handleAutoLayoutDiagramNode = (nodeId: string) => {
    const changed = updateDiagramDocument((current) => autoLayoutDiagramNode(current, nodeId));
    if (!changed) {
      return;
    }
    onPinTab();
    setDiagramApplyError("");
    setSelectedDiagramNodeId(nodeId);
  };

  const handleAutoLayoutDiagramSubtree = (nodeId: string) => {
    const changed = updateDiagramDocument((current) => autoLayoutDiagramSubtree(current, nodeId));
    if (!changed) {
      return;
    }
    onPinTab();
    setDiagramApplyError("");
    setSelectedDiagramNodeId(nodeId);
  };

  const handleAutoLayoutDiagramDescendants = (nodeId: string) => {
    const changed = updateDiagramDocument((current) => autoLayoutDiagramDescendants(current, nodeId));
    if (!changed) {
      return;
    }
    onPinTab();
    setDiagramApplyError("");
    setSelectedDiagramNodeId(nodeId);
  };

  const handleAutoLayoutDiagram = () => {
    const changed = updateDiagramDocument(autoLayoutDiagramDocument);
    if (!changed) {
      return;
    }
    onPinTab();
    setDiagramApplyError("");
  };

  const handleUnpinDiagram = () => {
    const changed = updateDiagramDocument(unpinDiagramDocument);
    if (!changed) {
      return;
    }
    onPinTab();
    setDiagramApplyError("");
  };

  const handlePinDiagram = () => {
    const changed = updateDiagramDocument(pinDiagramDocument);
    if (!changed) {
      return;
    }
    onPinTab();
    setDiagramApplyError("");
  };

  const handlePinDiagramNode = (nodeId: string) => {
    const changed = updateDiagramDocument((current) => pinDiagramSelectedNode(current, nodeId));
    if (!changed) {
      return;
    }
    onPinTab();
    setDiagramApplyError("");
    setSelectedDiagramNodeId(nodeId);
  };

  const handleUnpinDiagramNode = (nodeId: string) => {
    const changed = updateDiagramDocument((current) => unpinDiagramSelectedNode(current, nodeId));
    if (!changed) {
      return;
    }
    onPinTab();
    setDiagramApplyError("");
    setSelectedDiagramNodeId(nodeId);
  };

  const handleMakeDiagramNodeRelative = (nodeId: string) => {
    const changed = updateDiagramDocument((current) => makeDiagramSelectedNodeRelative(current, nodeId));
    if (!changed) {
      return;
    }
    onPinTab();
    setDiagramApplyError("");
    setSelectedDiagramNodeId(nodeId);
  };

  const handleMakeDiagramSubtreeRelative = (nodeId: string) => {
    const changed = updateDiagramDocument((current) => makeDiagramSubtreeRelative(current, nodeId));
    if (!changed) {
      return;
    }
    onPinTab();
    setDiagramApplyError("");
    setSelectedDiagramNodeId(nodeId);
  };

  const handlePinDiagramSubtree = (nodeId: string) => {
    const changed = updateDiagramDocument((current) => pinDiagramSubtree(current, nodeId));
    if (!changed) {
      return;
    }
    onPinTab();
    setDiagramApplyError("");
    setSelectedDiagramNodeId(nodeId);
  };

  const handleUnpinDiagramSubtree = (nodeId: string) => {
    const changed = updateDiagramDocument((current) => unpinDiagramSubtree(current, nodeId));
    if (!changed) {
      return;
    }
    onPinTab();
    setDiagramApplyError("");
    setSelectedDiagramNodeId(nodeId);
  };

  const handleSetDiagramNodePosition = (nodeId: string, position: { x: number; y: number }) => {
    if ((sourceBackedMioDiagram || sourceBackedDoctrineDiagram) && (!diagramDocument || !(sourceBackedMioDiagram ? mioDiagramNodeEditable(diagramDocument, nodeId) : doctrineDiagramNodeEditable(diagramDocument, nodeId)))) {
      setDiagramApplyError(sourceBackedMioDiagram ? t("workspace.diagram.mio.positionUnavailable") : t("workspace.diagram.readOnly"));
      return;
    }
    const changed = updateDiagramDocument((current) => setDiagramNodePosition(current, nodeId, position));
    if (!changed) {
      return;
    }
    onPinTab();
    setDiagramApplyError("");
    setSelectedDiagramNodeId(nodeId);
  };

  const handleSetDiagramNodeLayoutHints = (nodeId: string, hints: DiagramNodeLayoutHints) => {
    const changed = updateDiagramDocument((current) => setDiagramNodeLayoutHints(current, nodeId, hints));
    if (!changed) {
      return;
    }
    onPinTab();
    setDiagramApplyError("");
    setSelectedDiagramNodeId(nodeId);
  };

  const handleSaveDiagramViewport = (viewport: DiagramViewport) => {
    if (sessionOperationBusy()) {
      return;
    }
    const result = applyDiagramPresentUpdate(diagramHistory, baseDiagramDocument, (current) => setDiagramViewport(current, viewport));
    if (!result.changed) {
      return;
    }
    commitDiagramHistory(result.history);
    setDiagramApplyError("");
  };

  const handleImportDiagramJson = (text: string) => {
    if (sessionOperationBusy()) {
      return;
    }
    const result = importDiagramJsonDraft(diagramHistory, baseDiagramDocument, text, t);
    if (!result.ok) {
      setDiagramApplyError(result.error);
      return;
    }
    if (!result.changed) {
      return;
    }
    onPinTab();
    commitDiagramHistory(result.history);
    setDiagramApplyError("");
    setSelectedDiagramNodeId((current) => (result.document.nodes.some((node) => node.id === current) ? current : (result.document.nodes[0]?.id ?? "")));
  };

  const handleUndoDiagram = () => {
    if (sessionOperationBusy()) {
      return;
    }
    onPinTab();
    setDiagramApplyError("");
    commitDiagramHistory(undoDiagramHistory);
  };

  const handleRedoDiagram = () => {
    if (sessionOperationBusy()) {
      return;
    }
    onPinTab();
    setDiagramApplyError("");
    commitDiagramHistory(redoDiagramHistory);
  };

  const handleDiscardDiagramDraft = () => {
    if (!baseDiagramDocument || sessionOperationBusy()) {
      return;
    }
    setDiagramApplyError("");
    commitDiagramHistory(createDiagramHistory(baseDiagramDocument));
  };

  const handleApplyDiagramDraft = async () => {
    if (!browser || !baseDiagramDocument || !diagramDraft || diagramApplyBusy || sessionOperationBusy()) {
      return;
    }
    if (diagramBaseConflict) {
      setDiagramApplyError(t("workspace.diagram.sourceConflict"));
      return;
    }
    if (sourceBackedDiagram && sourceBackedDiagramChanges.error) {
      setDiagramApplyError(sourceBackedDiagramChanges.error);
      return;
    }
    if (sourceBackedDiagram && (!diagramAdapter || !sourceBackedDiagramContext)) {
      setDiagramApplyError(diagramReadOnlyReason || t("workspace.diagram.readOnly"));
      return;
    }
    if (!hasDesktopBackend()) {
      setDiagramApplyError(t("workspace.module.editor.applyRequiresDesktop"));
      return;
    }
    const operationToken = editorScopeToken.current;
    const finishBusy = editorSessionStore.beginBusy(sessionKey);
    setDiagramApplyBusy(true);
    setDiagramApplyError("");
    try {
      const payload =
        sourceBackedDiagram && diagramAdapter && sourceBackedDiagramContext
          ? await applySourceBackedDiagramIntents(browser.root, moduleDiagramProfile, moduleDiagramFamily, diagramAdapter.editIntents(sourceBackedDiagramContext, baseDiagramDocument, diagramDraft))
          : await applyMetadataDiagramDraft(
              browser.project_id,
              browser.root,
              baseDiagramDocument,
              diagramDraft,
              diagramMetadataChangedEntities,
              entities,
              (rows) => {
                if (isCurrentEditorOperation(operationToken)) {
                  setDiagramMetadataDraftEntities(rows);
                }
              },
              t,
            );
      if (!isCurrentEditorOperation(operationToken)) {
        return;
      }
      if (!payload.written) {
        if (isCurrentEditorOperation(operationToken)) {
          setDiagramApplyError(payload.error || t("workspace.module.editor.applyDidNotWrite"));
        }
        return;
      }
      retainCatalogMutationFailureForScope(payload.catalog_mutation);
      if (isCurrentEditorOperation(operationToken)) {
        reconcileCatalogMutationForScope(payload.catalog_mutation);
        const catalogWarning = catalogMutationFailureWarning(t, payload.catalog_mutation);
        if (catalogWarning) {
          setDiagramApplyError(catalogWarning);
        }
      }
      editorSessionStore.setDiagram(sessionKey, diagramSessionScopeKey, null);
      if (isCurrentEditorOperation(operationToken)) {
        setDiagramHistory(createDiagramHistory(null));
        if (sourceBackedDiagram) {
          setModuleDiagramReloadKey((current) => current + 1);
        }
      }
      await onProjectRefresh(browser.root, payload.project_id);
    } catch (error: unknown) {
      if (isCurrentEditorOperation(operationToken)) {
        const recoveryPath = sourceDraftRecoveryPathFromError(error, browser.root);
        if (recoveryPath) {
          onBatchRecoveryPathsChange([...new Set([...batchRecoveryPaths, recoveryPath])]);
        }
        setDiagramApplyError(recoveryPath ? t("workspace.module.editor.sourceRecoveryRequired") : localizedParaDevServiceError(t, error));
      }
    } finally {
      finishBusy();
      if (isCurrentEditorOperation(operationToken)) {
        setDiagramApplyBusy(false);
      }
    }
  };

  const handleCollectionCreated = async (payload: CollectionScaffoldPayload) => {
    retainCollectionCreate(null);
    setModuleDiagramReloadKey((current) => current + 1);
    await onProjectRefresh(browser?.root, payload.project_id);
    setSelectedId(`collection:${payload.family}/${payload.collection_id}`);
  };

  const handleDiagramModuleCreated = async (payload: ModuleCreateBatchPayload) => {
    let objectId = "";
    for (const row of payload.modules) {
      if (row.status === "created") {
        reconcileCatalogMutationForScope(batchCatalogMutation(row));
      }
      const rowObjectId = typeof row.object_id === "string" ? row.object_id.trim() : "";
      if (!objectId && rowObjectId) {
        objectId = rowObjectId;
      }
    }
    if (objectId) {
      if (sourceBackedMioDiagram) {
        setSelectedMioOrganizationId(objectId);
        setSelectedDiagramNodeId("");
      } else {
        setSelectedDiagramNodeId(objectId);
      }
    }
    setModuleDiagramReloadKey((current) => current + 1);
    try {
      await onProjectRefresh(browser?.root, payload.project_id);
    } catch (cause: unknown) {
      setDiagramApplyError(
        t("workspace.diagram.moduleCreate.refreshFailed", {
          title: familyTitle,
          message: localizedParaDevServiceError(t, cause),
        }),
      );
    }
  };

  const handleDiagramNodeCreated = async (payload: ModuleDiagramEditPayload) => {
    retainCatalogMutationFailureForScope(payload.catalog_mutation);
    reconcileCatalogMutationForScope(payload.catalog_mutation);
    if (payload.created_scope_id) {
      setSelectedMioOrganizationId(payload.created_scope_id);
    }
    if (payload.created_node_id) {
      setSelectedDiagramNodeId(payload.created_node_id);
    }
    setModuleDiagramReloadKey((current) => current + 1);
    try {
      await onProjectRefresh(browser?.root, payload.project_id);
    } catch (cause: unknown) {
      setDiagramApplyError(
        t("workspace.diagram.moduleCreate.refreshFailed", {
          title: sourceBackedDiagramCapability?.nodeAuthoring?.title ?? familyTitle,
          message: localizedParaDevServiceError(t, cause),
        }),
      );
    }
  };

  const canCreateDiagramModule = sourceBackedModuleDiagram && createTemplates.length > 0 && !diagramDirty && hasDesktopBackend();
  const canCreateDiagramNode = sourceBackedNodeDiagram && sourceBackedDiagramCapability?.nodeAuthoring !== undefined && diagramNodeInitialIntent !== null && !diagramDirty && hasDesktopBackend();

  const diagramPanel =
    showDiagram && diagramDocument ? (
      <ProjectDiagramView
        diagramApplyBusy={diagramApplyBusy || sessionBusy}
        diagramApplyError={diagramBaseConflict ? t("workspace.diagram.sourceConflict") : diagramApplyError || catalogMutationWarning}
        diagramChangedEntities={diagramChangedEntitiesForView}
        diagramCanRedo={canRedoDiagramHistory(diagramHistory)}
        diagramCanUndo={canUndoDiagramHistory(diagramHistory)}
        diagramChangedEntityIds={diagramMetadataChangedEntityIds}
        diagramDirty={diagramDirty}
        document={diagramDocument}
        createNodeLabel={canCreateDiagramNode ? (sourceBackedDiagramCapability?.nodeAuthoring?.title ?? "") : sourceBackedModuleDiagram ? t("workspace.diagram.addModule", { title: familyTitle }) : ""}
        onDiagramApply={diagramEditable && !diagramBaseConflict ? handleApplyDiagramDraft : undefined}
        onDiagramAutoLayout={diagramEditable && !sourceBackedDiagram ? handleAutoLayoutDiagram : undefined}
        onDiagramCreateNode={canCreateDiagramNode ? () => setDiagramNodeCreateOpen(true) : canCreateDiagramModule ? () => setDiagramModuleCreateOpen(true) : undefined}
        onDiagramDiscard={diagramEditable ? handleDiscardDiagramDraft : undefined}
        onDiagramInsertRoot={diagramEditable && !sourceBackedDiagram && supportsDiagramFocusTreeEdits(familyId) ? handleInsertDiagramRoot : undefined}
        onDiagramImportJson={diagramEditable && !sourceBackedDiagram ? handleImportDiagramJson : undefined}
        onDiagramPinAll={diagramEditable && !sourceBackedDiagram ? handlePinDiagram : undefined}
        onDiagramRedo={diagramEditable ? handleRedoDiagram : undefined}
        onDiagramUndo={diagramEditable ? handleUndoDiagram : undefined}
        onDiagramUnpinAll={diagramEditable && !sourceBackedDiagram ? handleUnpinDiagram : undefined}
        onDiagramViewportSave={handleSaveDiagramViewport}
        onNodeAddDependency={diagramEditable && !sourceBackedDiagram ? handleAddDiagramDependency : undefined}
        onNodeAddReference={diagramEditable && !sourceBackedDiagram ? handleAddDiagramReference : undefined}
        onNodeAddUnlock={diagramEditable && !sourceBackedDiagram ? handleAddDiagramUnlock : undefined}
        onNodeClearParent={diagramEditable && !sourceBackedDiagram && supportsDiagramFocusTreeEdits(familyId) ? handleClearDiagramParent : undefined}
        onNodeAutoLayout={diagramEditable && !sourceBackedDiagram ? handleAutoLayoutDiagramNode : undefined}
        onNodeAutoLayoutDescendants={diagramEditable && !sourceBackedDiagram ? handleAutoLayoutDiagramDescendants : undefined}
        onNodeAutoLayoutSubtree={diagramEditable && !sourceBackedDiagram ? handleAutoLayoutDiagramSubtree : undefined}
        onNodeInsertChild={diagramEditable && !sourceBackedDiagram && supportsDiagramFocusTreeEdits(familyId) ? handleInsertDiagramChild : undefined}
        onNodeMove={diagramEditable ? handleMoveDiagramNode : undefined}
        onNodeMoveKeepingDescendants={diagramEditable && !sourceBackedMioDiagram ? handleMoveDiagramNodeKeepingDescendants : undefined}
        onNodeMoveRelayoutDescendants={diagramEditable && !sourceBackedFocusDiagram && !sourceBackedMioDiagram ? handleMoveDiagramNodeRelayoutDescendants : undefined}
        onNodeMoveSubtree={diagramEditable && !sourceBackedMioDiagram ? handleMoveDiagramSubtree : undefined}
        onNodeMakeRelative={diagramEditable && !sourceBackedDiagram ? handleMakeDiagramNodeRelative : undefined}
        onNodeMakeSubtreeRelative={diagramEditable && !sourceBackedDiagram ? handleMakeDiagramSubtreeRelative : undefined}
        onNodeInfoClose={() => setOpenedDiagramNodeId("")}
        onNodeOpen={handleOpenDiagramNode}
        onNodeOpenModule={onOpenModuleEntity ? handleOpenDiagramNodeModule : undefined}
        onNodePin={diagramEditable && !sourceBackedDiagram ? handlePinDiagramNode : undefined}
        onNodePinSubtree={diagramEditable && !sourceBackedDiagram ? handlePinDiagramSubtree : undefined}
        onNodeReorderSibling={diagramEditable && !sourceBackedDiagram ? handleReorderDiagramSibling : undefined}
        onNodeRemoveDependency={diagramEditable && !sourceBackedDiagram ? handleRemoveDiagramDependency : undefined}
        onNodeRemoveOnly={diagramEditable && !sourceBackedDiagram && supportsDiagramFocusTreeEdits(familyId) ? handleRemoveDiagramNodeOnly : undefined}
        onNodeRemoveReference={diagramEditable && !sourceBackedDiagram ? handleRemoveDiagramReference : undefined}
        onNodeRemoveUnlock={diagramEditable && !sourceBackedDiagram ? handleRemoveDiagramUnlock : undefined}
        onNodeRemoveSubtree={diagramEditable && !sourceBackedDiagram && supportsDiagramFocusTreeEdits(familyId) ? handleRemoveDiagramSubtree : undefined}
        onNodeSelect={handleSelectDiagramNode}
        onNodeSetLayoutHints={diagramEditable && !sourceBackedDiagram && supportsDiagramFocusTreeEdits(familyId) ? handleSetDiagramNodeLayoutHints : undefined}
        onNodeSetPosition={diagramEditable ? handleSetDiagramNodePosition : undefined}
        onNodeSetParent={diagramEditable && !sourceBackedDiagram && supportsDiagramFocusTreeEdits(familyId) ? handleSetDiagramParent : undefined}
        onNodeSetRelationship={diagramEditable && sourceBackedDiagram && sourceBackedDiagramCapability?.relationships.length ? handleSetProviderDiagramRelationship : undefined}
        onNodeUnpin={diagramEditable && !sourceBackedDiagram ? handleUnpinDiagramNode : undefined}
        onNodeUnpinSubtree={diagramEditable && !sourceBackedDiagram ? handleUnpinDiagramSubtree : undefined}
        openedNodeId={openedDiagramNodeId}
        projectRoot={browser.root}
        readOnly={!diagramEditable}
        readOnlyReason={diagramReadOnlyReason}
        relationshipActions={sourceBackedDiagramCapability?.relationships}
        selectedNodeId={selectedDiagramNodeIdForEditor || activeDiagramScopeEntity?.objectId || ""}
        t={t}
        title={diagramTitle}
      />
    ) : (
      <div className="project-diagram-panel empty">
        <div className="project-diagram-header">
          <div className="project-diagram-title">
            <span>{t("workspace.diagram.title")}</span>
            <small>{moduleDiagramLoading ? t("workspace.diagram.loading.body") : moduleDiagramDisplayError || t("workspace.diagram.empty")}</small>
          </div>
          {canCreateDiagramModule ? (
            <button className="toolbar-button project-diagram-add-node" onClick={() => setDiagramModuleCreateOpen(true)} type="button">
              <Plus aria-hidden="true" size={14} />
              {t("workspace.diagram.addModule", {
                title: familyTitle,
              })}
            </button>
          ) : null}
        </div>
      </div>
    );

  const diagramScopeSelector = showDiagramScopeSelector ? (
    <div className="diagram-scope-bar">
      {sourceBackedMioDiagram || diagramScopeEntities.length > 0 ? (
        <div className="diagram-scope-select">
          <SelectField
            className="diagram-scope-control"
            controlTitle={diagramDirty ? t(sourceBackedMioDiagram ? "workspace.diagram.mio.scopeDirtyTitle" : "workspace.diagram.scopeDirtyTitle") : t(sourceBackedMioDiagram ? "workspace.diagram.mio.scopeAria" : "workspace.diagram.scopeAria")}
            disabled={sourceBackedMioDiagram ? diagramApplyBusy || sessionBusy : diagramDirty}
            label={t(sourceBackedMioDiagram ? "workspace.diagram.mio.scopeAria" : "workspace.diagram.scopeAria")}
            onChange={handleSelectDiagramScope}
            options={
              sourceBackedMioDiagram
                ? mioOrganizationOptions.map((option) => ({
                    label: option.title === option.id ? option.id : `${option.title} — ${option.id}`,
                    value: option.id,
                  }))
                : diagramScopeEntities.map((entity) => ({
                    label: entity.title || entity.objectId,
                    value: entity.id,
                  }))
            }
            prefix={t(sourceBackedMioDiagram ? "workspace.diagram.mio.scopeLabel" : "workspace.diagram.scopeLabel")}
            value={sourceBackedMioDiagram ? activeMioOrganizationId : (activeDiagramScopeEntity?.id ?? "")}
          />
        </div>
      ) : (
        <span role="status">{t("workspace.diagram.empty")}</span>
      )}
      <div className="diagram-scope-actions">
        <span className="diagram-scope-count">
          {t(sourceBackedMioDiagram ? (projectScopedMioDiagram ? "workspace.diagram.mio.projectScopeCount" : "workspace.diagram.mio.scopeCount") : "workspace.diagram.scopeCount", {
            count: sourceBackedMioDiagram ? mioOrganizationOptions.length : diagramScopeEntities.length,
          })}
        </span>
        {sourceBackedDiagramCapability?.scopeAuthoringKind === "collection" && collectionCreateTemplates.length > 0 && hasDesktopBackend() ? (
          <button
            className="toolbar-button subtle"
            disabled={diagramDirty || sessionBusy}
            onClick={() => {
              setCollectionCreateOpen(true);
              const retained = editorSessionStore.read(sessionKey)?.collectionCreate;
              if (retained) {
                retainCollectionCreate({ ...retained, open: true });
              }
            }}
            type="button"
          >
            <Plus aria-hidden="true" size={14} />
            {t("workspace.diagram.collectionCreate.open")}
          </button>
        ) : null}
      </div>
    </div>
  ) : mioDiagramScopeEmpty ? (
    <div className="diagram-scope-bar diagram-scope-empty" role="status">
      <span>{t(projectScopedMioDiagram ? "workspace.diagram.mio.projectScopeEmpty" : "workspace.diagram.mio.scopeEmpty")}</span>
    </div>
  ) : null;

  if (surface === "diagram") {
    return (
      <div aria-busy={sessionBusy || undefined} className={["module-editor", "diagram-editor", diagramScopeSelector ? "has-diagram-scope" : ""].filter(Boolean).join(" ")}>
        <div className="diagram-editor-background" inert={sessionBusy ? true : undefined}>
          {diagramScopeSelector}
          {diagramPanel}
        </div>
        {collectionCreateOpen && browser && collectionCreateTemplates.length > 0 ? (
          <CollectionCreateDialog
            initialState={editorSessionStore.read(sessionKey)?.collectionCreate}
            onApplied={handleCollectionCreated}
            onBusyStart={() => editorSessionStore.beginBusy(sessionKey)}
            onClose={handleCollectionDialogClose}
            onDraftChange={retainCollectionCreate}
            onPostWriteError={(cause) =>
              setDiagramApplyError(
                t("workspace.diagram.collectionCreate.refreshFailed", {
                  message: localizedParaDevServiceError(t, cause),
                }),
              )
            }
            projectRoot={browser.root}
            sourceRoots={templates?.source_roots ?? []}
            t={t}
            templates={collectionCreateTemplates}
          />
        ) : null}
        {retainedSourceUpdate?.open && browser ? <SourceUpdateReviewDialog initialState={retainedSourceUpdate} locale={locale} onApplied={handleSourceUpdateApplied} onBusyStart={() => editorSessionStore.beginBusy(sessionKey)} onClose={handleSourceUpdateDialogClose} projectRoot={browser.root} t={t} /> : null}
        {diagramModuleCreateOpen && browser && sourceBackedModuleDiagram && createTemplates.length > 0 ? (
          <ModuleCreateDialog
            dialogText={{
              detail: t("workspace.diagram.moduleCreate.detail", {
                title: familyTitle,
              }),
              eyebrow: t("workspace.diagram.moduleCreate.eyebrow"),
              guidance: t("workspace.diagram.moduleCreate.guidance"),
              title: t("workspace.diagram.moduleCreate.title", {
                title: familyTitle,
              }),
            }}
            familyTitle={familyTitle}
            initialValues={diagramModuleInitialValues}
            key={`${browser.root}:${familyId}:diagram-create`}
            mode="single"
            onApplied={handleDiagramModuleCreated}
            onBusyStart={() => editorSessionStore.beginBusy(sessionKey)}
            onClose={() => setDiagramModuleCreateOpen(false)}
            onRecoveryPathsChange={onBatchRecoveryPathsChange}
            openTarget={openTarget}
            projectId={browser.project_id}
            projectRoot={browser.root}
            recoveryPaths={batchRecoveryPaths}
            referenceItems={browser.items}
            sourceRoots={templates?.source_roots ?? []}
            t={t}
            templates={createTemplates}
          />
        ) : null}
        {diagramNodeCreateOpen && browser && canCreateDiagramNode && sourceBackedDiagramCapability?.nodeAuthoring && diagramNodeInitialIntent ? <DiagramNodeCreateDialog authoring={sourceBackedDiagramCapability.nodeAuthoring} contextValues={diagramNodeInitialIntent} family={moduleDiagramFamily} key={`${browser.root}:${familyId}:diagram-node-create`} onApplied={handleDiagramNodeCreated} onBusyStart={() => editorSessionStore.beginBusy(sessionKey)} onClose={() => setDiagramNodeCreateOpen(false)} profile={moduleDiagramProfile} projectRoot={browser.root} t={t} /> : null}
      </div>
    );
  }

  return (
    <div aria-busy={sessionBusy || undefined} className="module-editor" inert={sessionBusy ? true : undefined}>
      <div className="module-editor-grid">
        <ModuleEntityList
          activityFilter={activityFilter}
          allEntities={entities}
          catalogMissing={catalog.catalogMissing}
          catalogPreparing={catalog.catalogPreparing}
          catalogSearch={catalog.enabled}
          createAdvancedFields={createFields.advanced}
          createObjectId={createObjectId}
          createObjectIdPreview={createInput.objectId}
          createPrimaryFields={createFields.primary}
          createPreviewValues={createInput.values}
          createBusy={createBusy || sessionBusy}
          createError={createError}
          createTemplateId={createTemplate?.id ?? ""}
          createTemplateOptions={createTemplates.map((template) => ({
            label: template.title,
            value: template.id,
          }))}
          createTemplateTitle={createTemplate?.title ?? familyTitle}
          createUnavailableReason={createUnavailableReason}
          batchUnavailableReason={createUnavailableReason || (!hasDesktopBackend() ? t("workspace.module.editor.batch.requiresDesktop") : "")}
          createValues={createValues}
          createIntent={moduleCreateIntent && moduleCreateIntent.mode !== "batch" && moduleCreateIntent.mode !== "collection" && moduleCreateIntent.mode !== "source-update" && canonicalFamilyId(moduleCreateIntent.familyId) === canonicalFamilyId(familyId) ? moduleCreateIntent : null}
          entities={filteredEntities}
          hasMore={catalog.hasMore}
          hydratingEntityId={catalog.hydratingEntityId}
          loadError={catalog.loadError}
          loadedCount={catalog.loadedCount ?? entities.length}
          loading={catalog.loading}
          locale={locale}
          onActivityFilterChange={setActivityFilter}
          onCreateIntentConsumed={onModuleCreateIntentConsumed}
          projectRoot={browser?.root ?? ""}
          onCreate={handleCreate}
          onOpenBatch={() => {
            if (sessionOperationBusy()) {
              return;
            }
            onPinTab();
            setBatchDialogOpen(true);
            const retained = editorSessionStore.read(sessionKey)?.batchCreate;
            if (retained) {
              retainBatchCreate({ ...retained, open: true });
            }
          }}
          collectionCreateLabel={t("workspace.diagram.collectionCreate.open")}
          onOpenCollectionCreate={
            collectionCreateTemplates.length > 0 && hasDesktopBackend()
              ? () => {
                  if (!sessionOperationBusy()) {
                    onPinTab();
                    setCollectionCreateOpen(true);
                    const retained = editorSessionStore.read(sessionKey)?.collectionCreate;
                    if (retained) {
                      retainCollectionCreate({ ...retained, open: true });
                    }
                  }
                }
              : undefined
          }
          onCreateObjectIdChange={(value) => {
            if (sessionOperationBusy()) {
              return;
            }
            onPinTab();
            setCreateObjectId(value);
            retainInlineCreate({
              templateId: createTemplateId,
              objectId: value,
              values: createValues,
              showAdvanced: showAdvancedCreate,
            });
          }}
          onCreateValueChange={handleCreateValueChange}
          onLoadMore={catalog.loadMore}
          onPrepareCatalog={catalog.prepareCatalog}
          onCreateTemplateChange={(value) => {
            if (sessionOperationBusy()) {
              return;
            }
            onPinTab();
            setCreateTemplateId(value);
            setCreateObjectId("");
            setCreateValues({});
            setShowAdvancedCreate(false);
            retainInlineCreate({
              templateId: value,
              objectId: "",
              values: {},
              showAdvanced: false,
            });
          }}
          onQueryChange={setQuery}
          onRemoveSelected={handleRemoveSelected}
          onRetryLoad={catalog.retry}
          onSelect={handleSelectEntity}
          onSelectionChange={setSelectedIds}
          onShowAdvancedCreateChange={(showAdvanced) => {
            if (sessionOperationBusy()) {
              return;
            }
            setShowAdvancedCreate(showAdvanced);
            retainInlineCreate({
              templateId: createTemplateId,
              objectId: createObjectId,
              values: createValues,
              showAdvanced,
            });
          }}
          query={query}
          referenceItems={catalog.effectiveBrowser?.items ?? browser?.items ?? []}
          selectedId={selectedEntity?.id ?? ""}
          selectedIds={selectedIds}
          showAdvancedCreate={showAdvancedCreate}
          t={t}
          totalCount={catalog.totalCount ?? entities.length}
        />
        <ModuleEntityDetails
          activeDiagramNodeId={selectedEmbeddedDiagramNodeId}
          applyBusy={sessionBusy || applyBusyId === selectedEntity?.id}
          applyError={applyError}
          buildAffectedFamilyTitle={familyTitle}
          canApply={!catalog.catalogPreparing && !selectedEntityMutationBlocked && hasDesktopBackend() && selectedEntityCanApply}
          canChangeActivity={selectedEntityCanChangeActivity}
          canChangeCollection={selectedEntityCanChangeCollection}
          canDuplicate={selectedEntityCanDuplicate}
          collectionOptions={selectedCollectionOptions}
          entity={selectedEntity}
          gameRoot={gameRoot}
          loading={Boolean(selectedId) && catalog.hydratingEntityId === selectedId && !catalog.loadError}
          locale={locale}
          onBuildAffected={
            onBuildTarget && selectedBuildFamily
              ? () =>
                  onBuildTarget({
                    family: selectedBuildFamily,
                    id: selectedBuildFamily,
                    kind: "family",
                  })
              : undefined
          }
          buildTargetKind={selectedBuildTarget?.kind}
          onBuildModule={
            onBuildTarget && selectedBuildFamily && selectedBuildTarget
              ? () =>
                  onBuildTarget({
                    family: selectedBuildFamily,
                    id: selectedBuildTarget.id,
                    kind: selectedBuildTarget.kind,
                  })
              : undefined
          }
          onActivityChange={selectedEntity?.moduleId ? handleActivityChange : undefined}
          onDuplicate={handleOpenDuplicate}
          onCollectionChange={handleCollectionChange}
          onActiveSourcePathChange={handleActiveSourcePathChange}
          onApply={handleApplyEntity}
          onAssetDrafts={handleAssetDrafts}
          onImageDraft={handleImageDraft}
          onInfoDraft={handleInfoDraft}
          onGuidedTextDraft={(entityId, sourceKey, change) => {
            onPinTab();
            updateEntity(entityId, (entity) => applyGuidedTextDraft(entity, sourceKey, change));
          }}
          onRefresh={handleRefreshModule}
          onRestore={handleRestore}
          onTextDraft={(entityId, sourceKey, value) => {
            onPinTab();
            updateEntity(entityId, (entity) => applyTextDraft(entity, sourceKey, value));
          }}
          openTarget={openTarget}
          projectId={browser.project_id}
          projectRoot={browser.root}
          sourceReloadKey={sourceReloadKey}
          targetSourcePath={selectedSourcePath}
          t={t}
          theme={theme}
        />
      </div>
      {batchDialogOpen && browser && createTemplates.length > 0 ? <ModuleCreateDialog familyTitle={familyTitle} initialState={editorSessionStore.read(sessionKey)?.batchCreate} key={`${browser.root}:${familyId}`} onApplied={handleBatchApplied} onBusyStart={() => editorSessionStore.beginBusy(sessionKey)} onClose={handleBatchDialogClose} onDraftChange={retainBatchCreate} onRecoveryPathsChange={onBatchRecoveryPathsChange} openTarget={openTarget} projectId={browser.project_id} projectRoot={browser.root} recoveryPaths={batchRecoveryPaths} referenceItems={browser.items} sourceRoots={templates?.source_roots ?? []} t={t} templates={createTemplates} /> : null}
      {collectionCreateOpen && browser && collectionCreateTemplates.length > 0 ? (
        <CollectionCreateDialog
          initialState={editorSessionStore.read(sessionKey)?.collectionCreate}
          onApplied={handleCollectionCreated}
          onBusyStart={() => editorSessionStore.beginBusy(sessionKey)}
          onClose={handleCollectionDialogClose}
          onDraftChange={retainCollectionCreate}
          onPostWriteError={(cause) =>
            setApplyError(
              t("workspace.diagram.collectionCreate.refreshFailed", {
                message: localizedParaDevServiceError(t, cause),
              }),
            )
          }
          projectRoot={browser.root}
          sourceRoots={templates?.source_roots ?? []}
          t={t}
          templates={collectionCreateTemplates}
        />
      ) : null}
      {retainedSourceUpdate?.open && browser ? <SourceUpdateReviewDialog initialState={retainedSourceUpdate} locale={locale} onApplied={handleSourceUpdateApplied} onBusyStart={() => editorSessionStore.beginBusy(sessionKey)} onClose={handleSourceUpdateDialogClose} projectRoot={browser.root} t={t} /> : null}
      {duplicateTarget?.moduleId && browser ? <ModuleDuplicateDialog moduleId={duplicateTarget.moduleId} objectId={duplicateTarget.objectId} onApplied={handleDuplicateApplied} onBusyStart={() => editorSessionStore.beginBusy(sessionKey)} onClose={handleDuplicateDialogClose} projectRoot={browser.root} sourceRoot={duplicateTarget.sourceRoot} sourceRoots={templates?.source_roots ?? []} t={t} title={duplicateTarget.title} /> : null}
      <footer className="module-editor-footer">
        <small aria-live="polite">{familySummary}</small>
        <div className="module-editor-footer-actions">
          {catalogMutationWarning || catalog.repairError ? (
            <>
              {catalogMutationWarning ? (
                <small className="project-path error" role="alert" title={catalogMutationWarning}>
                  {catalogMutationWarning}
                </small>
              ) : null}
              {catalog.repairError ? (
                <small className="project-path error" role="alert">
                  {catalog.repairError}
                </small>
              ) : null}
              <button className="toolbar-button subtle" disabled={catalog.catalogPreparing} onClick={() => void handleRepairCatalog()} title={t("workspace.module.editor.catalogRepairWarning")} type="button">
                <RefreshCw aria-hidden="true" size={14} />
                {t(catalog.catalogPreparing ? "workspace.module.editor.catalogPreparing" : "workspace.module.editor.catalogRepair")}
              </button>
            </>
          ) : null}
          <button className="toolbar-button" onClick={handleRefreshModule} title={t("workspace.module.editor.refreshModule")} type="button">
            <RefreshCw aria-hidden="true" size={14} />
            {t("workspace.module.editor.refreshModule")}
          </button>
          <code>{browser.project_id}</code>
        </div>
      </footer>
    </div>
  );
}

function imageDraftResourceId(entityId: string, previewUrl: string): string {
  return `image-draft:${entityId}:${previewUrl}`;
}

function releaseImageDraftResource(store: ModuleEditorSessionStore, key: ModuleEditorSessionKey, entity: ModuleEntity | undefined): void {
  const previewUrl = entity?.drafts.image?.previewUrl ?? "";
  if (!entity || !previewUrl.startsWith("blob:")) {
    return;
  }
  store.releaseResource(key, imageDraftResourceId(entity.id, previewUrl));
}

function moveImageDraftResource(store: ModuleEditorSessionStore, key: ModuleEditorSessionKey, previousEntity: ModuleEntity, nextEntity: ModuleEntity): void {
  const previewUrl = previousEntity.drafts.image?.previewUrl ?? "";
  if (!previewUrl.startsWith("blob:") || nextEntity.drafts.image?.previewUrl !== previewUrl) {
    return;
  }
  store.moveResource(key, imageDraftResourceId(previousEntity.id, previewUrl), imageDraftResourceId(nextEntity.id, previewUrl));
}

export function diagnosticSummary(t: Translator, diagnostics: Array<Record<string, unknown>>): string {
  const message = diagnostics.find((diagnostic) => typeof diagnostic.message === "string")?.message;
  return typeof message === "string" && message.trim() ? message : t("workspace.module.editor.draftPlanBlocked");
}

function isModuleIdentityMutationDraft(entity: ModuleEntity | null): boolean {
  return canApplyScaffoldDraft(entity) || canApplyRemovalDraft(entity) || canApplyInfoDraft(entity);
}

function hasAmbiguousModuleMutationTarget(entities: readonly ModuleEntity[], target: Pick<ModuleEntity, "id" | "moduleId" | "root" | "sourceRoot">): boolean {
  const moduleId = target.moduleId?.trim();
  if (!moduleId) {
    return false;
  }
  const matching = entities.filter((entity) => entity.moduleId?.trim() === moduleId);
  if (matching.length < 2) {
    return false;
  }
  return new Set(matching.map(moduleMutationSourceIdentity)).size > 1;
}

function hasAmbiguousEntityMutationTarget(entities: readonly ModuleEntity[], target: Pick<ModuleEntity, "collectionId" | "family" | "id" | "moduleId" | "root" | "sourceRoot">): boolean {
  if (target.moduleId) {
    return hasAmbiguousModuleMutationTarget(entities, target);
  }
  const collectionId = target.collectionId?.trim();
  if (!collectionId) {
    return false;
  }
  const matching = entities.filter((entity) => entity.collectionId?.trim() === collectionId && entity.family === target.family);
  if (matching.length < 2) {
    return false;
  }
  return new Set(matching.map(moduleMutationSourceIdentity)).size > 1;
}

function moduleMutationSourceIdentity(entity: Pick<ModuleEntity, "root" | "sourceRoot">): string {
  return [entity.sourceRoot ?? "", entity.root]
    .map((path) => {
      const normalized = path.trim().replace(/\\/g, "/").replace(/\/+$/, "");
      return /^[A-Za-z]:\//.test(normalized) || normalized.startsWith("//") ? normalized.toLowerCase() : normalized;
    })
    .join("\u0000");
}

function renamedModuleEntity(entity: ModuleEntity, payload: ModuleRenamePayload): ModuleEntity {
  const objectId = moduleObjectId(payload.module_id);
  const sourceSlots = entity.sourceSlots.map((source) => ({
    ...source,
    path: movedModulePath(source.path, payload.previous_root, payload.root),
    relative_path: movedModulePath(source.relative_path, payload.previous_relative_path, payload.relative_path),
  }));
  const previewSource = entity.previewSource
    ? {
        ...entity.previewSource,
        path: movedModulePath(entity.previewSource.path, payload.previous_root, payload.root),
        relative_path: movedModulePath(entity.previewSource.relative_path, payload.previous_relative_path, payload.relative_path),
      }
    : undefined;
  const info = entity.drafts.info ? { ...entity.drafts.info } : undefined;
  const title = info?.title?.trim() || entity.title;
  if (info) {
    delete info.objectId;
    delete info.title;
  }
  const drafts: ModuleEntityDrafts = {
    ...entity.drafts,
    text: { ...entity.drafts.text },
  };
  if (info && Object.keys(info).length > 0) {
    drafts.info = info;
  } else {
    delete drafts.info;
  }
  if (drafts.image?.path) {
    drafts.image = {
      ...drafts.image,
      path: movedModulePath(drafts.image.path, payload.previous_root, payload.root),
    };
  }
  if (drafts.assets) {
    drafts.assets = drafts.assets.map((asset) => ({
      ...asset,
      path: movedModulePath(asset.path, payload.previous_root, payload.root),
    }));
  }
  const draftState = moduleDraftStateForDrafts(drafts);
  const draftSourceRevisions = (entity.draftSourceRevisions ?? []).map((revision) => ({
    ...revision,
    path: movedModulePath(revision.path, payload.previous_root, payload.root),
    relativePath: movedModulePath(revision.relativePath, payload.previous_relative_path, payload.relative_path),
  }));
  const { draftSourceRevisions: _draftSourceRevisions, sourceConflict: _sourceConflict, ...base } = entity;
  return {
    ...base,
    id: `module:${payload.module_id}`,
    family: payload.family,
    moduleId: payload.module_id,
    objectId,
    title,
    subtitle: objectId,
    root: payload.root,
    relativeRoot: payload.relative_path,
    sourceSlots,
    previewSource,
    ...(draftState !== "clean" && draftSourceRevisions.length > 0 ? { draftSourceRevisions } : {}),
    draftState,
    drafts,
  };
}

function renamedCollectionEntity(entity: ModuleEntity, payload: CollectionRenamePayload): ModuleEntity {
  const objectId = payload.collection_id;
  const sourceSlots = entity.sourceSlots.map((source) => ({
    ...source,
    path: movedModulePath(source.path, payload.previous_root, payload.root),
    relative_path: movedModulePath(source.relative_path, payload.previous_relative_path, payload.relative_path),
  }));
  const previewSource = entity.previewSource
    ? {
        ...entity.previewSource,
        path: movedModulePath(entity.previewSource.path, payload.previous_root, payload.root),
        relative_path: movedModulePath(entity.previewSource.relative_path, payload.previous_relative_path, payload.relative_path),
      }
    : undefined;
  const info = entity.drafts.info ? { ...entity.drafts.info } : undefined;
  const title = info?.title?.trim() || entity.title;
  if (info) {
    delete info.objectId;
    delete info.title;
  }
  const drafts: ModuleEntityDrafts = {
    ...entity.drafts,
    text: { ...entity.drafts.text },
  };
  if (info && Object.keys(info).length > 0) {
    drafts.info = info;
  } else {
    delete drafts.info;
  }
  if (drafts.image?.path) {
    drafts.image = {
      ...drafts.image,
      path: movedModulePath(drafts.image.path, payload.previous_root, payload.root),
    };
  }
  if (drafts.assets) {
    drafts.assets = drafts.assets.map((asset) => ({
      ...asset,
      path: movedModulePath(asset.path, payload.previous_root, payload.root),
    }));
  }
  const draftState = moduleDraftStateForDrafts(drafts);
  const draftSourceRevisions = (entity.draftSourceRevisions ?? []).map((revision) => ({
    ...revision,
    path: movedModulePath(revision.path, payload.previous_root, payload.root),
    relativePath: movedModulePath(revision.relativePath, payload.previous_relative_path, payload.relative_path),
  }));
  const { draftSourceRevisions: _draftSourceRevisions, sourceConflict: _sourceConflict, ...base } = entity;
  return {
    ...base,
    id: `collection:${payload.family}/${payload.collection_id}`,
    kind: "collection",
    family: payload.family,
    collectionId: payload.collection_id,
    objectId,
    title,
    subtitle: objectId,
    root: payload.root,
    relativeRoot: payload.relative_path,
    sourceSlots,
    previewSource,
    ...(draftState !== "clean" && draftSourceRevisions.length > 0 ? { draftSourceRevisions } : {}),
    draftState,
    drafts,
  };
}

function moduleDraftStateForDrafts(drafts: ModuleEntityDrafts): ModuleEntity["draftState"] {
  return Object.keys(drafts.text).length > 0 || drafts.image || drafts.info || (drafts.assets?.length ?? 0) > 0 ? "modified" : "clean";
}

function movedModulePath(path: string, previousRoot: string, root: string): string {
  const normalizedPath = path.replace(/\\/g, "/");
  const normalizedPreviousRoot = previousRoot.replace(/\\/g, "/").replace(/\/+$/, "");
  const normalizedRoot = root.replace(/\\/g, "/").replace(/\/+$/, "");
  if (normalizedPath === normalizedPreviousRoot) {
    return normalizedRoot;
  }
  return normalizedPath.startsWith(`${normalizedPreviousRoot}/`) ? `${normalizedRoot}${normalizedPath.slice(normalizedPreviousRoot.length)}` : normalizedPath;
}

function moduleObjectId(moduleId: string): string {
  const separator = moduleId.indexOf("/");
  return separator >= 0 ? moduleId.slice(separator + 1) : moduleId;
}

function catalogMutationFailureWarning(t: Translator, mutation: CatalogMutationResult | null | undefined): string {
  if (!mutation || mutation.status === "unverified") {
    return t("workspace.module.editor.catalogMutationUnknown");
  }
  return mutation.status === "failed"
    ? t("workspace.module.editor.catalogMutationFailed", {
        message: mutation.message,
      })
    : "";
}

function catalogMutationFailureForSession(mutation: CatalogMutationResult | null | undefined): ModuleEditorCatalogMutationFailure | null {
  if (!mutation || mutation.status === "unverified") {
    return {
      status: "unverified",
      message: mutation?.message ?? "",
    };
  }
  return mutation.status === "failed" ? { status: "failed", message: mutation.message } : null;
}

function retainedCatalogMutationFailureWarning(t: Translator, failure: ModuleEditorCatalogMutationFailure | null): string {
  if (!failure) {
    return "";
  }
  return failure.status === "failed"
    ? t("workspace.module.editor.catalogMutationFailed", {
        message: failure.message,
      })
    : t("workspace.module.editor.catalogMutationUnknown");
}

function batchCatalogMutation(row: Record<string, unknown>): CatalogMutationResult | undefined {
  const mutation = row.catalog_mutation;
  if (!mutation || typeof mutation !== "object" || Array.isArray(mutation)) {
    return undefined;
  }
  const value = mutation as Record<string, unknown>;
  if (value.schema === "paradev.desktop.catalog-mutation-unverified.v1" && value.status === "unverified" && value.code === "catalog.mutation.unverified" && typeof value.message === "string" && value.message.trim()) {
    return {
      schema: value.schema,
      status: value.status,
      code: value.code,
      message: value.message,
    };
  }
  if (value.schema !== "paradev.hb.catalog-mutation.v1" || typeof value.database !== "string" || !value.database.trim()) {
    return undefined;
  }
  if (value.status === "applied" && value.code === "catalog.mutation.applied") {
    return {
      schema: value.schema,
      status: value.status,
      code: value.code,
      database: value.database,
    };
  }
  if (value.status === "not_configured" && value.code === "catalog.mutation.not_configured") {
    return {
      schema: value.schema,
      status: value.status,
      code: value.code,
      database: value.database,
    };
  }
  if (value.status === "failed" && value.code === "catalog.mutation.failed" && typeof value.message === "string" && value.message.trim()) {
    return {
      schema: value.schema,
      status: value.status,
      code: value.code,
      database: value.database,
      message: value.message,
    };
  }
  return undefined;
}

function supportsDiagramFocusTreeEdits(familyId: string): boolean {
  return canonicalFamilyId(familyId) === "focuses";
}

export function shouldShowProjectDiagram(browser: ProjectBrowserPayload | null, familyId: string, document: DiagramDocument | null): boolean {
  return Boolean(document) && supportsProjectDiagramFamily(browser, familyId);
}

function browserForDiagramEntity(browser: ProjectBrowserPayload | null, entity: Pick<ModuleEntity, "collectionId" | "id" | "kind" | "moduleId" | "objectId"> | null, surface: ModuleEditorProps["surface"], familyId: string): ProjectBrowserPayload | null {
  if (!browser || surface !== "diagram" || !entity || canonicalFamilyId(familyId) !== "focuses") {
    return browser;
  }
  const collectionId = entity.kind === "collection" ? entity.collectionId || entity.objectId : "";
  const items = browser.items.filter((item) => browserItemMatchesDiagramEntity(item, entity) || Boolean(collectionId && item.kind === "module" && item.collection_id === collectionId));
  return { ...browser, items };
}

function browserItemMatchesDiagramEntity(item: ProjectBrowserItem, entity: Pick<ModuleEntity, "id" | "moduleId" | "objectId">): boolean {
  const canonicalModuleId = `${item.family}/${item.object_id}`;
  return [item.id, item.object_id, item.module_id, canonicalModuleId].some((id) => Boolean(id) && [entity.id, entity.objectId, entity.moduleId].includes(id));
}

export function moduleSelectionTargetForEntity(entity: ModuleEntity | null, familyId: string, sourcePathOverride = ""): WorkspaceModuleSelectionTarget | null {
  if (!entity) {
    return null;
  }
  const sourcePath = sourcePathOverride.trim() || sourcePathForSelection(entity);
  const sourceContent = sourcePath ? sourceContentForSelection(entity, sourcePath) : undefined;
  return {
    entityId: entity.id,
    familyId,
    ...(sourceContent !== undefined ? { sourceContent } : {}),
    ...(sourcePath ? { sourcePath } : {}),
  };
}

function sourcePathForSelection(entity: ModuleEntity): string {
  const editable = entity.sourceSlots.find((source) => source.editorKind === "code" || source.editorKind === "localization");
  const source = editable ?? entity.sourceSlots.find((item) => Boolean(item.relative_path || item.path));
  return source?.relative_path || source?.path || "";
}

function sourceContentForSelection(entity: ModuleEntity, sourcePath: string): string | undefined {
  const source = entity.sourceSlots.find((item) => [item.relative_path, item.path].includes(sourcePath));
  if (!source || !Object.prototype.hasOwnProperty.call(entity.drafts.text, source.draftKey)) {
    return undefined;
  }
  return entity.drafts.text[source.draftKey];
}

function selectionTargetKey(target: WorkspaceModuleSelectionTarget | null): string {
  const sourceContent = target?.sourceContent === undefined ? "<unset>" : target.sourceContent;
  return [target?.familyId ?? "", target?.entityId ?? "", target?.sourcePath ?? "", sourceContent].join("\n");
}

export function buildDiagramChangedEntities(baseDocument: DiagramDocument | null, draftDocument: DiagramDocument | null, entities: Pick<ModuleEntity, "id" | "relativeRoot" | "root" | "sourceSlots" | "title">[]): DiagramChangedEntity[] {
  if (!baseDocument || !draftDocument) {
    return [];
  }
  const entitiesById = new Map(entities.map((entity) => [entity.id, entity]));
  const rows: DiagramChangedEntity[] = [];
  for (const id of changedDiagramMetadataEntityIds(baseDocument, draftDocument)) {
    const entity = entitiesById.get(id);
    const source = entity?.sourceSlots.find((slot) => slot.slot === "meta");
    rows.push({
      id,
      ...(source?.relative_path ? { path: source.relative_path } : source?.path ? { path: source.path } : {}),
      ...(entity?.title ? { title: entity.title } : {}),
    });
  }
  for (const ref of changedDiagramMetadataSourceInfoRefs(baseDocument, draftDocument)) {
    const entity = entitiesById.get(ref.entityId);
    rows.push({
      id: ref.entityId,
      path: diagramChangedSourceDisplayPath(entity, ref.path),
      ...(entity?.title ? { title: entity.title } : {}),
    });
  }
  return dedupeDiagramChangedEntities(rows);
}

export function buildDiagramChangedEntitiesWithDraftTexts(rows: DiagramChangedEntity[], drafts: DiagramMetadataTextDraft[], entities: Pick<ModuleEntity, "id" | "relativeRoot" | "root" | "sourceSlots">[]): DiagramChangedEntity[] {
  if (rows.length === 0) {
    return rows;
  }
  const draftTextByKey = new Map<string, string>();
  const entitiesById = new Map(entities.map((entity) => [entity.id, entity]));
  const entitiesWithSourceDrafts = new Set<string>();
  for (const draft of drafts) {
    const entity = entitiesById.get(draft.entityId);
    if (draft.path) {
      entitiesWithSourceDrafts.add(draft.entityId);
    }
    for (const path of diagramMetadataDraftDisplayPaths(draft, entity)) {
      draftTextByKey.set(diagramChangedEntityKey(draft.entityId, path), draft.text);
    }
  }
  return rows.flatMap((row) => {
    if (!row.path) {
      return [row];
    }
    const draftKey = diagramChangedEntityKey(row.id, row.path);
    if (!draftTextByKey.has(draftKey)) {
      const entity = entitiesById.get(row.id);
      if (entitiesWithSourceDrafts.has(row.id) && diagramChangedRowIsMetaPath(row, entity)) {
        return [];
      }
      return [{ ...row, draftUnavailable: true }];
    }
    const draftText = draftTextByKey.get(draftKey) ?? "";
    return [draftText ? { ...row, draftText } : row];
  });
}

export type DiagramApplyDraftPlan =
  | {
      ok: false;
      reason: "draft-unavailable" | "no-changes";
      rows: DiagramChangedEntity[];
    }
  | {
      ok: true;
      rows: DiagramChangedEntity[];
      sourceEdits: SourceTextEdit[];
    };

export function buildDiagramApplyDraftPlan(rows: DiagramChangedEntity[], drafts: DiagramMetadataTextDraft[], entities: Pick<ModuleEntity, "id" | "relativeRoot" | "root" | "sourceSlots">[]): DiagramApplyDraftPlan {
  const rowsWithDrafts = buildDiagramChangedEntitiesWithDraftTexts(rows, drafts, entities);
  if (rowsWithDrafts.some((row) => row.draftUnavailable)) {
    return { ok: false, reason: "draft-unavailable", rows: rowsWithDrafts };
  }
  const sourceEdits = sourceTextEditsForDiagramMetadataDrafts(entities, drafts);
  if (sourceEdits.length === 0) {
    return { ok: false, reason: "no-changes", rows: rowsWithDrafts };
  }
  return { ok: true, rows: rowsWithDrafts, sourceEdits };
}

type DiagramApplyServiceResult = {
  project_id: string;
  written: boolean;
  error: string;
  catalog_mutation?: CatalogMutationResult;
};

async function applySourceBackedDiagramIntents(
  projectRoot: string,
  profile: string,
  family: string,
  intents: {
    positionIntents: ModuleDiagramPositionIntent[];
    edgeIntents: ModuleDiagramEdgeIntent[];
  },
): Promise<DiagramApplyServiceResult> {
  const request = {
    projectRoot,
    family,
    profile,
    positionIntents: intents.positionIntents,
    edgeIntents: intents.edgeIntents,
  };
  const plan = await editModuleDiagram(request);
  if (plan.blocked) {
    return {
      project_id: plan.project_id,
      written: false,
      error: moduleDiagramDiagnosticMessage(plan.diagnostics),
    };
  }
  const applied = await editModuleDiagram({
    ...request,
    write: true,
    planHash: plan.plan_hash,
  });
  return {
    project_id: applied.project_id,
    written: applied.written,
    error: applied.blocked ? moduleDiagramDiagnosticMessage(applied.diagnostics) : "",
    ...(applied.catalog_mutation ? { catalog_mutation: applied.catalog_mutation } : {}),
  };
}

async function applyMetadataDiagramDraft(projectId: string, projectRoot: string, baseDocument: DiagramDocument, draftDocument: DiagramDocument, changedEntities: DiagramChangedEntity[], entities: ModuleEntity[], onRows: (rows: DiagramChangedEntity[]) => void, t: Translator): Promise<DiagramApplyServiceResult> {
  const drafts = await loadDiagramMetadataTextDrafts(projectId, projectRoot, baseDocument, draftDocument, entities);
  const applyPlan = buildDiagramApplyDraftPlan(changedEntities, drafts, entities);
  onRows(applyPlan.rows);
  if (!applyPlan.ok) {
    return {
      project_id: projectId,
      written: false,
      error: t(applyPlan.reason === "draft-unavailable" ? "workspace.diagram.applyDraftUnavailable" : "workspace.diagram.applyNoChanges"),
    };
  }
  const payload = await applyProjectDraft({
    projectId,
    projectRoot,
    sourceEdits: applyPlan.sourceEdits,
  });
  return { ...payload, error: "" };
}

function moduleDiagramDiagnosticMessage(diagnostics: Array<Record<string, unknown>>): string {
  const diagnostic = diagnostics.find((row) => row.severity === "error" && typeof row.message === "string");
  return typeof diagnostic?.message === "string" ? diagnostic.message : "The source-backed diagram edit was blocked. Refresh the diagram and review its diagnostics.";
}

async function loadDiagramMetadataTextDrafts(projectId: string, projectRoot: string, baseDocument: DiagramDocument, draftDocument: DiagramDocument, entities: ModuleEntity[]): Promise<DiagramMetadataTextDraft[]> {
  const changedEntityIds = changedDiagramMetadataEntityIds(baseDocument, draftDocument);
  const metadataTextByEntityId = Object.fromEntries(
    await Promise.all(
      entities
        .filter((entity) => changedEntityIds.includes(entity.id))
        .map(async (entity) => {
          const source = entity.sourceSlots.find((slot) => slot.slot === "meta");
          return [entity.id, source?.path ? await readTextSource(projectRoot, source.path, projectId) : ""] as const;
        }),
    ),
  );
  const sourceTextByPath = Object.fromEntries(
    (
      await Promise.all(
        changedDiagramMetadataSourceInfoPaths(baseDocument, draftDocument).map(async (path) => {
          try {
            return [path, await readTextSource(projectRoot, path, projectId)] as const;
          } catch {
            return null;
          }
        }),
      )
    ).filter((entry): entry is readonly [string, string] => entry !== null),
  );
  return buildDiagramMetadataTextDrafts({
    baseDocument,
    draftDocument,
    entities,
    metadataTextByEntityId,
    sourceTextByPath,
  });
}

function diagramMetadataDraftDisplayPaths(draft: DiagramMetadataTextDraft, entity: Pick<ModuleEntity, "relativeRoot" | "root" | "sourceSlots"> | undefined): string[] {
  if (draft.path) {
    return uniqueStrings([draft.path, diagramChangedSourceDisplayPath(entity, draft.path)].map(normalizeDisplayPath).filter(Boolean));
  }
  const source = entity?.sourceSlots.find((slot) => slot.slot === draft.slot);
  return uniqueStrings([source?.relative_path, source?.path].map((path) => normalizeDisplayPath(path ?? "")).filter(Boolean));
}

function diagramChangedRowIsMetaPath(row: DiagramChangedEntity, entity: Pick<ModuleEntity, "sourceSlots"> | undefined): boolean {
  if (!row.path) {
    return false;
  }
  const source = entity?.sourceSlots.find((slot) => slot.slot === "meta");
  const rowPath = normalizeDisplayPath(row.path);
  return [source?.relative_path, source?.path].some((path) => normalizeDisplayPath(path ?? "") === rowPath);
}

function diagramChangedEntityKey(id: string, path: string): string {
  return `${id}\0${normalizeDisplayPath(path)}`;
}

function uniqueStrings(values: string[]): string[] {
  return [...new Set(values)];
}

function dedupeDiagramChangedEntities(rows: DiagramChangedEntity[]): DiagramChangedEntity[] {
  const seen = new Set<string>();
  return rows.filter((row) => {
    const key = `${row.id}\0${row.path ?? ""}`;
    if (seen.has(key)) {
      return false;
    }
    seen.add(key);
    return true;
  });
}

function diagramChangedSourceDisplayPath(entity: Pick<ModuleEntity, "relativeRoot" | "root"> | undefined, path: string): string {
  const cleanPath = normalizeDisplayPath(path);
  const root = normalizeDisplayPath(entity?.root ?? "");
  if (entity?.relativeRoot && root && cleanPath.startsWith(`${root}/`)) {
    return `${entity.relativeRoot}/${cleanPath.slice(root.length + 1)}`;
  }
  return cleanPath;
}

function normalizeDisplayPath(path: string): string {
  return path.trim().replace(/\\/g, "/").replace(/\/+$/, "");
}

function projectTemplatesMatchEditorScope(templates: ProjectTemplatesPayload | null, browser: ProjectBrowserPayload | null, projectRoot: string): boolean {
  if (!templates || !browser || browser.root !== projectRoot || templates.project_id !== browser.project_id) {
    return false;
  }
  if (!templates.source_roots?.length) {
    return true;
  }
  const root = normalizeDisplayPath(projectRoot);
  return templates.source_roots.some((sourceRoot) => {
    const path = normalizeDisplayPath(sourceRoot.path);
    return path === root || path.startsWith(`${root}/`);
  });
}

function sameSerializableData(left: unknown, right: unknown): boolean {
  return Object.is(left, right) || JSON.stringify(left) === JSON.stringify(right);
}

function restoredDiagramHistory(retained: ModuleEditorDiagramState | undefined, base: DiagramDocument | null): DiagramHistory {
  if (!retained) {
    return createDiagramHistory(base);
  }
  if (retained.changedEntityIds.length > 0) {
    return retained.history;
  }
  const retainedViewport = retained.history.present?.viewport;
  return createDiagramHistory(base && retainedViewport ? { ...base, viewport: { ...retainedViewport } } : base);
}

export function rootDiagramFocusNodeInput(document: DiagramDocument): DiagramChildNodeInput | null {
  const template = diagramRootFocusTemplateNode(document);
  const payload = template ? asProjectDiagramNodePayload(template.payload) : null;
  if (!template || !payload) {
    return null;
  }
  const id = nextDiagramFocusRootId(document);
  return {
    id,
    mode: "auto",
    width: template.width,
    height: template.height,
    title: titleFromDiagramIdentifier(id),
    ...(template.imageUrl ? { imageUrl: template.imageUrl } : {}),
    payload: { ...payload, embeddedId: id, embeddedKind: "focus" as const },
  };
}

function diagramRootFocusTemplateNode(document: DiagramDocument): DiagramNode | null {
  return document.nodes.find((node) => asProjectDiagramNodePayload(node.payload)?.embeddedKind === "focus") ?? document.nodes.find((node) => isFocusTreeContextPayload(asProjectDiagramNodePayload(node.payload))) ?? null;
}

function isFocusTreeContextPayload(payload: ProjectDiagramNodePayload | null): payload is ProjectDiagramNodePayload {
  if (!payload) {
    return false;
  }
  return canonicalFamilyId(payload.familyId, payload.family) === "focuses";
}

function nextDiagramFocusChildId(document: DiagramDocument, parentId: string): string {
  const existingIds = new Set(document.nodes.map((node) => node.id));
  const baseId = `${cleanDiagramIdentifier(parentId)}_CHILD`;
  if (!existingIds.has(baseId)) {
    return baseId;
  }
  for (let index = 2; ; index += 1) {
    const candidate = `${baseId}_${index}`;
    if (!existingIds.has(candidate)) {
      return candidate;
    }
  }
}

function nextDiagramFocusRootId(document: DiagramDocument): string {
  const existingIds = new Set(document.nodes.map((node) => node.id));
  const baseId = "FOCUS_NEW_ROOT";
  if (!existingIds.has(baseId)) {
    return baseId;
  }
  for (let index = 2; ; index += 1) {
    const candidate = `${baseId}_${index}`;
    if (!existingIds.has(candidate)) {
      return candidate;
    }
  }
}

function cleanDiagramIdentifier(value: string): string {
  return (
    value
      .trim()
      .replace(/[^A-Za-z0-9]+/g, "_")
      .replace(/^_+|_+$/g, "")
      .toUpperCase() || "FOCUS"
  );
}

function titleFromDiagramIdentifier(identifier: string): string {
  return (
    identifier
      .replace(/_desc$/i, "")
      .replace(/[-_]+/g, " ")
      .replace(/\s+/g, " ")
      .trim() || identifier
  );
}

function sourceBackedDiagramSessionEntityIds(document: DiagramDocument, nodeIds: string[]): string[] {
  const nodesById = new Map(document.nodes.map((node) => [node.id, node]));
  return [
    ...new Set(
      nodeIds.map((nodeId) => {
        const payload = asProjectDiagramNodePayload(nodesById.get(nodeId)?.payload);
        return payload?.itemId || nodeId;
      }),
    ),
  ].sort();
}

function asProjectDiagramNodePayload(value: DiagramNode["payload"]): ProjectDiagramNodePayload | null {
  if (!value || typeof value !== "object" || Array.isArray(value)) {
    return null;
  }
  const payload = value as Partial<ProjectDiagramNodePayload>;
  return typeof payload.itemId === "string" && typeof payload.objectId === "string" ? (payload as ProjectDiagramNodePayload) : null;
}
