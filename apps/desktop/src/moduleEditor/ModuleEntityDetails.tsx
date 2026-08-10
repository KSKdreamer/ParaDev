import { lazy, Suspense, useCallback, useEffect, useMemo, useRef, useState, type CSSProperties } from "react";
import { CopyPlus, FolderOpen, Hammer, Plus, Power, RefreshCw, RotateCcw, Save, Trash2 } from "lucide-react";
import { SelectField } from "../components/ui/SelectField";
import { localizedParaDevServiceError } from "../desktopBridgeErrors";
import { htmlLangForLocale, type Locale, type TranslationKey, type Translator } from "../i18n";
import { canonicalFamilyId } from "../projectModules";
import { openProjectPath, planProjectLocalizationUpdate, readBinarySource, readProjectLocalizationWorkspace, readProjectSourceForm, readTextSource, type BinarySourcePayload, type OpenPathTarget } from "../services/paradev";
import type { ProjectLocalizationOperation, ProjectLocalizationWorkspace, SourceFormPayload, ThemeName } from "../types";
import { AssetDraftEditor } from "./AssetDraftEditor";
import {
  assetSourcesForEntity,
  canPreviewImageSourceInEditor,
  canReplaceImageSource,
  defaultImageDraftPath,
  imageSourceFormat,
  localizationLanguageForText,
  moduleTitleLocalizationTarget,
  supportsAssetDrafts,
  updateMetadataTitleText,
  type ModuleDraftState,
  type ModuleAssetDraft,
  type ModuleEntity,
  type ModuleEntityDrafts,
  type ModuleLocalizationTable,
  type ModuleSourceSlot
} from "./model";
import { groupModuleEditableSources } from "./sourceDisclosure";
import type { GuidedSourceFormChange } from "./GuidedSourceForm";

type ModuleEntityDetailsProps = {
  applyBusy: boolean;
  applyError: string;
  buildAffectedFamilyTitle?: string;
  buildTargetKind?: "module" | "collection";
  canApply: boolean;
  canChangeActivity?: boolean;
  canChangeCollection?: boolean;
  canDuplicate?: boolean;
  collectionOptions?: Array<{ label: string; value: string }>;
  entity: ModuleEntity | null;
  gameRoot?: string;
  loading?: boolean;
  activeDiagramNodeId: string;
  projectId: string;
  projectRoot: string;
  sourceReloadKey: number;
  targetSourcePath?: string;
  locale: Locale;
  t: Translator;
  theme: ThemeName;
  onActiveSourcePathChange?: (entityId: string, sourcePath: string) => void;
  onApply: (entityId: string) => void;
  onAssetDrafts?: (entityId: string, assets: ModuleAssetDraft[]) => void;
  onBuildAffected?: () => void;
  onBuildModule?: () => void;
  onActivityChange?: (active: boolean) => void;
  onCollectionChange?: (collectionId: string) => void;
  onDuplicate?: () => void;
  onInfoDraft: (entityId: string, info: NonNullable<ModuleEntityDrafts["info"]>) => void;
  onImageDraft: (entityId: string, image: NonNullable<ModuleEntityDrafts["image"]>) => void;
  onGuidedTextDraft?: (entityId: string, sourceKey: string, change: GuidedSourceFormChange) => void;
  openTarget: OpenPathTarget;
  onRefresh: () => void;
  onRestore: (entityId: string) => void;
  onTextDraft: (entityId: string, sourceKey: string, value: string) => void;
};

const SourceCodeEditor = lazy(() => import("./SourceCodeEditor").then((module) => ({ default: module.SourceCodeEditor })));
const GuidedSourceForm = lazy(() => import("./GuidedSourceForm").then((module) => ({ default: module.GuidedSourceForm })));
const ImageDraftEditor = lazy(() => import("./ImageDraftEditor").then((module) => ({ default: module.ImageDraftEditor })));
const INFO_SLOT = "info";
const IMAGE_SLOT = "image";
const ASSET_SLOT = "assets";
const SOURCE_TAB_PICKER_THRESHOLD = 10;
type SourceFormMode = "guided" | "code";
type SourceFormLoadState = {
  sourceIdentity: string;
  status: "idle" | "loading" | "supported" | "unsupported" | "error" | "retry";
  form: SourceFormPayload | null;
  projectedText: string;
  error: string;
  enterGuidedOnSuccess: boolean;
};
type LocalizationWorkspaceState = {
  identity: string;
  status: "idle" | "loading" | "ready" | "error";
  workspace: ProjectLocalizationWorkspace | null;
  error: string;
};
const draftStateTranslationKey: Record<ModuleDraftState, TranslationKey> = {
  clean: "workspace.module.editor.draft.clean",
  modified: "workspace.module.editor.draft.modified",
  new: "workspace.module.editor.draft.new",
  remove: "workspace.module.editor.draft.remove"
};

export function ModuleEntityDetails({ activeDiagramNodeId, applyBusy, applyError, buildAffectedFamilyTitle, buildTargetKind = "module", canApply, canChangeActivity = false, canChangeCollection = false, canDuplicate = false, collectionOptions = [], entity, gameRoot, loading = false, locale, openTarget, projectId, projectRoot, sourceReloadKey, targetSourcePath = "", t, theme, onActiveSourcePathChange, onActivityChange, onApply, onAssetDrafts, onBuildAffected, onBuildModule, onCollectionChange, onDuplicate, onGuidedTextDraft, onImageDraft, onInfoDraft, onRefresh, onRestore, onTextDraft }: ModuleEntityDetailsProps) {
  const [activeSourceKey, setActiveSourceKey] = useState(() => activeSourceKeyForSourcePath(entity, targetSourcePath));
  const [selectedImageSourceKey, setSelectedImageSourceKey] = useState(() => imageSourceKeyForSourcePath(entity, targetSourcePath));
  const [loadedText, setLoadedText] = useState<Record<string, string>>({});
  const [imagePreviewUrl, setImagePreviewUrl] = useState("");
  const [imageLoadError, setImageLoadError] = useState("");
  const [loadError, setLoadError] = useState("");
  const [openError, setOpenError] = useState("");
  const [sourceFormState, setSourceFormState] = useState<SourceFormLoadState>({
    sourceIdentity: "",
    status: "idle",
    form: null,
    projectedText: "",
    error: "",
    enterGuidedOnSuccess: false
  });
  const [sourceFormModeBySource, setSourceFormModeBySource] = useState<Record<string, SourceFormMode>>({});
  const sourceFormRequestId = useRef(0);
  const [localizationWorkspaceState, setLocalizationWorkspaceState] = useState<LocalizationWorkspaceState>({
    identity: "",
    status: "idle",
    workspace: null,
    error: ""
  });
  const [localizationPending, setLocalizationPending] = useState(0);
  const localizationWorkspaceRequestId = useRef(0);
  const localizationOperationGeneration = useRef(0);
  const localizationOperationChain = useRef<Promise<void>>(Promise.resolve());
  const claimedTextLoads = useRef(new Set<string>());
  const textLoadContext = `${projectId}\u0000${projectRoot}\u0000${entity?.id ?? ""}\u0000${sourceReloadKey}`;
  const claimedTextLoadContextRef = useRef("");
  if (claimedTextLoadContextRef.current !== textLoadContext) {
    claimedTextLoadContextRef.current = textLoadContext;
    claimedTextLoads.current.clear();
  }
  const textLoadContextRef = useRef(textLoadContext);
  textLoadContextRef.current = textLoadContext;
  const editableSourceGroups = useMemo(
    () => groupModuleEditableSources(entity?.sourceSlots ?? []),
    [entity?.sourceSlots]
  );
  const editableSources = useMemo(
    () => [...editableSourceGroups.primary, ...editableSourceGroups.metadata],
    [editableSourceGroups]
  );
  const metadataSource = editableSourceGroups.metadata[0] ?? null;
  const localizationSources = useMemo(
    () => editableSourceGroups.primary.filter((source) => source.editorKind === "localization"),
    [editableSourceGroups]
  );
  const imageSources = useMemo(() => entity?.sourceSlots.filter((source) => source.editorKind === "image") ?? [], [entity?.sourceSlots]);
  const assetSources = useMemo(() => assetSourcesForEntity(entity), [entity]);
  const selectedImageSource = useMemo(() => imageSources.find((source) => source.draftKey === selectedImageSourceKey) ?? imageSources[0] ?? null, [imageSources, selectedImageSourceKey]);
  const selectedImagePath = entity ? defaultImageDraftPath(entity, selectedImageSource) : "";
  const imageReplacementUnavailableReason = !selectedImagePath
    ? t("workspace.module.editor.imageTargetUnavailable")
    : selectedImageSource && !canReplaceImageSource(selectedImageSource)
      ? t("workspace.module.editor.imageFormatUnsupported", { format: imageSourceFormat(selectedImageSource).toUpperCase() || selectedImageSource.name })
      : "";
  const selectedImageDraft = useMemo(() => imageDraftForSource(entity, selectedImageSource), [entity, selectedImageSource]);
  const imageEditorEntity = useMemo(() => {
    if (!entity || !entity.drafts.image || selectedImageDraft) {
      return entity;
    }
    const { image: _discarded, ...drafts } = entity.drafts;
    return { ...entity, drafts };
  }, [entity, selectedImageDraft]);
  const activeSource = useMemo(() => {
    if (activeSourceKey === INFO_SLOT || activeSourceKey === IMAGE_SLOT || activeSourceKey === ASSET_SLOT) {
      return null;
    }
    return entity?.sourceSlots.find((source) => source.draftKey === activeSourceKey) ?? entity?.sourceSlots[0] ?? null;
  }, [activeSourceKey, entity]);
  const textSourcesToLoad = useMemo(() => {
    const sources = new Map<string, ModuleSourceSlot>();
    for (const source of localizationSources) {
      if (source.path) {
        sources.set(source.path, source);
      }
    }
    if (metadataSource?.path) {
      sources.set(metadataSource.path, metadataSource);
    }
    if (activeSource?.path && (activeSource.editorKind === "code" || activeSource.editorKind === "localization")) {
      sources.set(activeSource.path, activeSource);
    }
    return [...sources.values()];
  }, [activeSource, localizationSources, metadataSource]);
  const localizationDraftSources = useMemo(
    () =>
      localizationSources
        .map((source) => {
          const text = entity?.drafts.text[source.draftKey] ?? loadedText[source.path] ?? "";
          const language = localizationLanguageForText(text, languageFromSource(source));
          return { source, language, text };
        }),
    [entity?.drafts.text, loadedText, localizationSources]
  );
  const localizationDraftRequest = useMemo(
    () => localizationDraftSources.flatMap(({ source, text }) => {
      const sourcePath = source.path || source.relative_path;
      return sourcePath && (entity?.drafts.text[source.draftKey] !== undefined || loadedText[source.path] !== undefined)
        ? [{ sourcePath, text }]
        : [];
    }),
    [entity?.drafts.text, loadedText, localizationDraftSources]
  );
  const localizationDraftRequestRef = useRef(localizationDraftRequest);
  localizationDraftRequestRef.current = localizationDraftRequest;
  const localizationWorkspace = localizationWorkspaceState.workspace;
  const localizationTarget = useMemo(() => (
    entity?.kind === "collection" && entity.collectionId
      ? {
          targetKind: "collection" as const,
          targetId: entity.collectionId,
          family: entity.family
        }
      : entity?.moduleId
        ? {
            targetKind: "module" as const,
            targetId: entity.moduleId,
            family: entity.family
          }
        : null
  ), [entity?.collectionId, entity?.family, entity?.kind, entity?.moduleId]);
  const localizationTable = useMemo<ModuleLocalizationTable>(() => ({
    languages: localizationWorkspace?.languages ?? [],
    rows: (localizationWorkspace?.rows ?? []).map((row) => ({
      key: row.key,
      values: Object.fromEntries(
        Object.entries(row.values).map(([language, cell]) => {
          const source = localizationSources.find((candidate) => candidate.path === cell.source_path || candidate.relative_path === cell.relative_path);
          return [language, { slot: source?.draftKey ?? cell.source_path, text: cell.text }];
        })
      )
    }))
  }), [localizationSources, localizationWorkspace]);
  const editorValue = entity && activeSource ? entity.drafts.text[activeSource.draftKey] ?? loadedText[activeSource.path] ?? "" : "";
  const activeSourcePath = activeSource?.relative_path || activeSource?.path || (activeSourceKey === IMAGE_SLOT ? selectedImageSource?.relative_path || selectedImageSource?.path : activeSourceKey === ASSET_SLOT ? targetSourcePath || assetSources[0]?.relative_path || assetSources[0]?.path : "") || "";
  const activeSourceRequestPath = activeSource?.path || activeSource?.relative_path || "";
  const activeSourceIdentity = entity && activeSource ? `${projectRoot}\u0000${entity.id}\u0000${activeSource.draftKey}` : "";
  const activeSourceIsText = activeSource?.editorKind === "code" || activeSource?.editorKind === "localization";
  const sourceFormEligible = Boolean(
    activeSourceIsText
      && activeSourceRequestPath
  );
  const activeSourceTextReady = Boolean(
    entity
      && activeSource
      && (
        Object.prototype.hasOwnProperty.call(entity.drafts.text, activeSource.draftKey)
        || (activeSource.path && Object.prototype.hasOwnProperty.call(loadedText, activeSource.path))
      )
  );
  const editorValueRef = useRef(editorValue);
  editorValueRef.current = editorValue;
  const translatorRef = useRef(t);
  translatorRef.current = t;
  const activeSourceFormState = sourceFormState.sourceIdentity === activeSourceIdentity
    ? sourceFormState
    : {
        sourceIdentity: activeSourceIdentity,
        status: "idle" as const,
        form: null,
        projectedText: "",
        error: "",
        enterGuidedOnSuccess: false
      };
  const sourceFormModeExplicit = Object.prototype.hasOwnProperty.call(sourceFormModeBySource, activeSourceIdentity);
  const sourceFormMode = sourceFormModeBySource[activeSourceIdentity] ?? "code";

  const requestSourceForm = useCallback((text: string, forceGuided: boolean, query?: string) => {
    if (!activeSourceIdentity || !activeSourceRequestPath || !sourceFormEligible) {
      return;
    }
    const requestId = ++sourceFormRequestId.current;
    setSourceFormState((current) => ({
      sourceIdentity: activeSourceIdentity,
      status: "loading",
      form: current.sourceIdentity === activeSourceIdentity ? current.form : null,
      projectedText: current.sourceIdentity === activeSourceIdentity && current.form
        ? current.projectedText
        : text,
      error: "",
      enterGuidedOnSuccess: forceGuided
    }));
    void readProjectSourceForm({
      projectId,
      projectRoot,
      sourcePath: activeSourceRequestPath,
      text,
      ...(query ? { query } : {})
    })
      .then((form) => {
        if (sourceFormRequestId.current !== requestId) {
          return;
        }
        if (editorValueRef.current !== text) {
          setSourceFormState({
            sourceIdentity: activeSourceIdentity,
            status: "error",
            form: null,
            projectedText: "",
            error: translatorRef.current("workspace.module.editor.guidedStale"),
            enterGuidedOnSuccess: false
          });
          setSourceFormModeBySource((current) => ({ ...current, [activeSourceIdentity]: "code" }));
          return;
        }
        if (!form) {
          setSourceFormState({
            sourceIdentity: activeSourceIdentity,
            status: "unsupported",
            form: null,
            projectedText: "",
            error: "",
            enterGuidedOnSuccess: false
          });
          setSourceFormModeBySource((current) => ({ ...current, [activeSourceIdentity]: "code" }));
          return;
        }
        setSourceFormState({
          sourceIdentity: activeSourceIdentity,
          status: "supported",
          form,
          projectedText: text,
          error: "",
          enterGuidedOnSuccess: false
        });
        setSourceFormModeBySource((current) => {
          if (!forceGuided && current[activeSourceIdentity]) {
            return current;
          }
          return { ...current, [activeSourceIdentity]: "guided" };
        });
      })
      .catch((error: unknown) => {
        if (sourceFormRequestId.current !== requestId) {
          return;
        }
        if (editorValueRef.current !== text) {
          setSourceFormState({
            sourceIdentity: activeSourceIdentity,
            status: "error",
            form: null,
            projectedText: "",
            error: translatorRef.current("workspace.module.editor.guidedStale"),
            enterGuidedOnSuccess: false
          });
          setSourceFormModeBySource((current) => ({ ...current, [activeSourceIdentity]: "code" }));
          return;
        }
        setSourceFormState({
          sourceIdentity: activeSourceIdentity,
          status: "error",
          form: null,
          projectedText: "",
          error: translatorRef.current("workspace.module.editor.guidedError", {
            message: localizedParaDevServiceError(translatorRef.current, error)
          }),
          enterGuidedOnSuccess: false
        });
        setSourceFormModeBySource((current) => ({ ...current, [activeSourceIdentity]: "code" }));
      });
  }, [activeSourceIdentity, activeSourceRequestPath, projectId, projectRoot, sourceFormEligible]);

  useEffect(() => {
    if (!sourceFormEligible || !activeSourceTextReady || !activeSourceIdentity) {
      sourceFormRequestId.current += 1;
      return;
    }
    requestSourceForm(editorValueRef.current, false);
    return () => {
      sourceFormRequestId.current += 1;
    };
  }, [activeSourceIdentity, activeSourceTextReady, requestSourceForm, sourceFormEligible, sourceReloadKey]);

  useEffect(() => {
    setActiveSourceKey(activeSourceKeyForSourcePath(entity, targetSourcePath));
    setSelectedImageSourceKey(imageSourceKeyForSourcePath(entity, targetSourcePath));
    setLoadError("");
    setOpenError("");
  }, [entity?.id, targetSourcePath]);

  useEffect(() => {
    textLoadContextRef.current = textLoadContext;
    setLoadedText((current) =>
      Object.keys(current).length === 0 ? current : {}
    );
    setImagePreviewUrl("");
    setImageLoadError("");
    setLoadError("");
    return () => {
      if (textLoadContextRef.current === textLoadContext) {
        textLoadContextRef.current = "";
      }
    };
  }, [textLoadContext]);

  useEffect(() => {
    if (!entity) {
      return;
    }
    const unloaded = textSourcesToLoad.filter((source) => {
      const requestKey = `${textLoadContext}\u0000${source.path}`;
      return source.path
        && loadedText[source.path] === undefined
        && entity.drafts.text[source.draftKey] === undefined
        && !claimedTextLoads.current.has(requestKey);
    });
    if (unloaded.length === 0) {
      return;
    }

    setLoadError("");
    for (const source of unloaded) {
      const requestKey = `${textLoadContext}\u0000${source.path}`;
      claimedTextLoads.current.add(requestKey);
      void readTextSource(projectRoot, source.path, projectId)
        .then((value) => {
          if (textLoadContextRef.current === textLoadContext) {
            setLoadedText((current) => ({ ...current, [source.path]: value }));
          }
        })
        .catch((error: unknown) => {
          if (textLoadContextRef.current === textLoadContext) {
            setLoadError(localizedParaDevServiceError(t, error));
          }
        });
    }
  }, [entity, loadedText, projectId, projectRoot, textLoadContext, textSourcesToLoad, t]);

  useEffect(() => {
    localizationOperationGeneration.current += 1;
    localizationOperationChain.current = Promise.resolve();
    setLocalizationPending(0);
  }, [entity?.id, projectId, projectRoot, sourceReloadKey]);

  useEffect(() => {
    const identity = localizationTarget
      ? `${projectId}\u0000${projectRoot}\u0000${localizationTarget.targetKind}\u0000${localizationTarget.targetId}\u0000${sourceReloadKey}`
      : "";
    if (
      !entity ||
      !localizationTarget ||
      entity.draftState === "new" ||
      localizationSources.length === 0
    ) {
      localizationWorkspaceRequestId.current += 1;
      setLocalizationWorkspaceState({ identity, status: "idle", workspace: null, error: "" });
      return;
    }
    if (localizationDraftRequest.length !== localizationSources.length) {
      setLocalizationWorkspaceState((current) => ({
        identity,
        status: "loading",
        workspace: current.identity === identity ? current.workspace : null,
        error: ""
      }));
      return;
    }
    const requestId = localizationWorkspaceRequestId.current + 1;
    localizationWorkspaceRequestId.current = requestId;
    setLocalizationWorkspaceState((current) => ({
      identity,
      status: "loading",
      workspace: current.identity === identity ? current.workspace : null,
      error: ""
    }));
    void readProjectLocalizationWorkspace({
      projectId,
      projectRoot,
      ...localizationTarget,
      ...(entity.sourceRoot ? { sourceRoot: entity.sourceRoot } : {}),
      drafts: localizationDraftRequest
    }).then((workspace) => {
      if (localizationWorkspaceRequestId.current === requestId) {
        setLocalizationWorkspaceState({ identity, status: "ready", workspace, error: "" });
      }
    }).catch((error: unknown) => {
      if (localizationWorkspaceRequestId.current === requestId) {
        setLocalizationWorkspaceState({
          identity,
          status: "error",
          workspace: null,
          error: localizedParaDevServiceError(translatorRef.current, error)
        });
      }
    });
  }, [entity?.draftState, entity?.id, entity?.sourceRoot, localizationDraftRequest, localizationSources.length, localizationTarget, projectId, projectRoot, sourceReloadKey]);

  useEffect(() => {
    if (
      !entity ||
      !selectedImageSource?.path ||
      selectedImageSource.exists === false ||
      selectedImageDraft?.previewUrl ||
      !canPreviewImageSourceInEditor(selectedImageSource)
    ) {
      setImagePreviewUrl("");
      setImageLoadError("");
      return;
    }

    let cancelled = false;
    setImagePreviewUrl("");
    setImageLoadError("");
    const previewPaths = [...new Set([selectedImagePath, selectedImageSource.path].filter(Boolean))];
    void (async () => {
      let lastError: unknown = null;
      for (const path of previewPaths) {
        try {
          const payload = await readBinarySource(projectRoot, path);
          if (!cancelled) {
            setImagePreviewUrl(binarySourceDataUrl(payload));
          }
          return;
        } catch (error) {
          lastError = error;
        }
      }
      if (!cancelled && lastError) {
        setImagePreviewUrl("");
        setImageLoadError(localizedParaDevServiceError(t, lastError));
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [entity, projectRoot, selectedImageDraft?.previewUrl, selectedImagePath, selectedImageSource?.path, sourceReloadKey, t]);

  useEffect(() => {
    if (
      !entity
      || localizationSources.length > 0
      || !metadataSource?.path
      || !entity.drafts.info?.title
      || entity.drafts.text[metadataSource.draftKey] !== undefined
    ) {
      return;
    }
    const metadataText = loadedText[metadataSource.path];
    if (metadataText !== undefined) {
      onTextDraft(entity.id, metadataSource.draftKey, updateMetadataTitleText(metadataText, entity.drafts.info.title));
    }
  }, [entity, loadedText, localizationSources.length, metadataSource, onTextDraft]);

  if (loading) {
    return (
      <section aria-busy="true" aria-live="polite" className="module-entity-details empty" lang={htmlLangForLocale(locale)} role="status">
        <h3>{t("workspace.module.editor.catalogHydrating")}</h3>
      </section>
    );
  }

  if (!entity) {
    return (
      <section className="module-entity-details empty" lang={htmlLangForLocale(locale)}>
        <h3>{t("workspace.module.editor.noSelection")}</h3>
      </section>
    );
  }
  const entityActive = entity.active !== false;

  const isTextSource = activeSourceIsText;
  const sourceFormModeVisible = sourceFormEligible && ["loading", "supported", "error", "retry"].includes(activeSourceFormState.status);
  const showGuidedSourceForm = sourceFormMode === "guided"
    && (
      activeSourceFormState.status === "supported"
      || (
        activeSourceFormState.status === "loading"
        && activeSourceFormState.form?.source_format !== "json"
      )
    )
    && activeSourceFormState.form !== null;
  const sourceEditorHasChrome = Boolean(loadError || sourceFormModeVisible || activeSourceFormState.error);
  const sourcePickerActive = editableSources.length > SOURCE_TAB_PICKER_THRESHOLD;
  const sourcePickerValue = activeSource ? activeSource.draftKey : "";
  const sourcePickerPath = activeSource ? activeSource.relative_path || activeSource.path : "";
  const canOpenPath = Boolean(entity.root);
  const isNewScaffold = entity.draftState === "new";
  const isEntityFamily = canonicalFamilyId(entity.familyId, entity.family) === "entity";
  const showImageTab = !isEntityFamily || imageSources.length > 0;
  const showAssetTab = supportsAssetDrafts(entity);
  const displayObjectId = entity.drafts.info?.objectId ?? entity.objectId;
  const displayTitle = entity.drafts.info?.title ?? entity.title;
  const displayPath = entity.relativeRoot || entity.root || t("workspace.module.editor.unsavedPath");
  const queueLocalizationOperation = (operation: ProjectLocalizationOperation) => {
    if (!localizationTarget || localizationSources.length === 0) {
      return;
    }
    const generation = localizationOperationGeneration.current;
    setLocalizationPending((count) => count + 1);
    const previous = localizationOperationChain.current.catch(() => undefined);
    const task = previous.then(async () => {
      if (localizationOperationGeneration.current !== generation) {
        return;
      }
      const plan = await planProjectLocalizationUpdate({
        projectId,
        projectRoot,
        ...localizationTarget,
        ...(entity.sourceRoot ? { sourceRoot: entity.sourceRoot } : {}),
        drafts: localizationDraftRequestRef.current,
        operation
      });
      if (localizationOperationGeneration.current !== generation) {
        return;
      }
      localizationWorkspaceRequestId.current += 1;
      const nextDrafts = new Map(
        localizationDraftRequestRef.current.map((draft) => [draft.sourcePath, draft.text])
      );
      for (const edit of plan.source_edits) {
        const source = localizationSources.find((candidate) =>
          candidate.path === edit.path || candidate.relative_path === edit.path
        );
        if (!source) {
          throw new Error(`Localization plan returned an unknown source: ${edit.path}`);
        }
        nextDrafts.set(source.path || source.relative_path, edit.text);
        onTextDraft(entity.id, source.draftKey, edit.text);
      }
      localizationDraftRequestRef.current = [...nextDrafts].map(([sourcePath, text]) => ({ sourcePath, text }));
      setLocalizationWorkspaceState((current) => ({
        identity: current.identity,
        status: "ready",
        workspace: plan.workspace,
        error: ""
      }));
    }).catch((error: unknown) => {
      if (localizationOperationGeneration.current === generation) {
        setLocalizationWorkspaceState((current) => ({
          ...current,
          status: "error",
          error: localizedParaDevServiceError(t, error)
        }));
      }
    }).finally(() => {
      if (localizationOperationGeneration.current === generation) {
        setLocalizationPending((count) => Math.max(0, count - 1));
      }
    });
    localizationOperationChain.current = task;
  };
  const handleGuidedMode = () => {
    if (sourceFormMode === "guided" && activeSourceFormState.status === "supported") {
      return;
    }
    requestSourceForm(editorValue, true, activeSourceFormState.form?.query);
  };
  const handleCodeMode = () => {
    if (
      (sourceFormMode === "code" && activeSourceFormState.status !== "loading")
      || (
        sourceFormMode === "code"
        && activeSourceFormState.status === "loading"
        && !activeSourceFormState.enterGuidedOnSuccess
        && sourceFormModeExplicit
      )
    ) {
      return;
    }
    setSourceFormModeBySource((current) => ({ ...current, [activeSourceIdentity]: "code" }));
    if (activeSourceFormState.status !== "loading" || !activeSourceFormState.enterGuidedOnSuccess) {
      return;
    }
    sourceFormRequestId.current += 1;
    setSourceFormState((current) => current.sourceIdentity === activeSourceIdentity && current.status === "loading"
      ? {
          ...current,
          status: current.form ? "supported" : "retry",
          error: "",
          enterGuidedOnSuccess: false
        }
      : current);
  };
  const handleGuidedSourceChange = (change: GuidedSourceFormChange) => {
    if (!activeSource) {
      return;
    }
    if (onGuidedTextDraft) {
      onGuidedTextDraft(entity.id, activeSource.draftKey, change);
    } else {
      onTextDraft(entity.id, activeSource.draftKey, change.text);
    }
    if (activeSourceFormState.form?.source_format !== "json") {
      editorValueRef.current = change.text;
      requestSourceForm(change.text, true, activeSourceFormState.form?.query);
    }
  };
  const handleLocalizationChange = (language: string, key: string, value: string, sourceKey?: string) => {
    const source =
      localizationSources.find((item) => item.draftKey === sourceKey) ??
      localizationDraftSources.find((item) => item.language === language)?.source ??
      localizationSources[0];
    if (!source) {
      return;
    }
    queueLocalizationOperation({
      op: "set",
      language,
      key,
      value,
      source_path: source.path || source.relative_path
    });
  };
  const handleLocalizationKeyChange = (oldKey: string, value: string) => {
    if (value.trim() && value.trim() !== oldKey) {
      queueLocalizationOperation({ op: "rename", key: oldKey, new_key: value });
    }
  };
  const handleLocalizationRowAdd = () => {
    queueLocalizationOperation({ op: "add" });
  };
  const handleLocalizationRowRemove = (key: string) => {
    queueLocalizationOperation({ op: "remove", key });
  };
  const handleTitleChange = (value: string) => {
    onInfoDraft(entity.id, { objectId: displayObjectId, title: value });
  };
  const handleTitleCommit = (value: string) => {
    const localizationTarget = moduleTitleLocalizationTarget(
      entity,
      locale,
      localizationDraftSources.map((item) => ({
        slot: item.source.draftKey,
        language: item.language,
        text: item.text
      })),
      localizationTable
    );
    if (localizationTarget) {
      handleLocalizationChange(
        localizationTarget.language,
        localizationTarget.key,
        value,
        localizationTarget.slot
      );
      return;
    }
    if (localizationSources.length > 0) {
      return;
    }
    if (!metadataSource?.path) {
      return;
    }
    const currentText = entity.drafts.text[metadataSource.draftKey] ?? loadedText[metadataSource.path];
    if (currentText !== undefined) {
      onTextDraft(entity.id, metadataSource.draftKey, updateMetadataTitleText(currentText, value));
    }
  };
  const handleActiveSourceKeyChange = (nextSourceKey: string) => {
    if (nextSourceKey === activeSourceKey) {
      return;
    }
    setActiveSourceKey(nextSourceKey);
    onActiveSourcePathChange?.(
      entity.id,
      sourcePathForActiveSourceKey(
        entity,
        nextSourceKey,
        selectedImageSourceKey,
        targetSourcePath
      )
    );
  };
  const handleSelectedImageSourceKeyChange = (nextSourceKey: string) => {
    if (nextSourceKey === selectedImageSourceKey) {
      return;
    }
    setSelectedImageSourceKey(nextSourceKey);
    if (activeSourceKey === IMAGE_SLOT) {
      onActiveSourcePathChange?.(
        entity.id,
        sourcePathForActiveSourceKey(
          entity,
          IMAGE_SLOT,
          nextSourceKey,
          targetSourcePath
        )
      );
    }
  };

  return (
    <section aria-busy={applyBusy || localizationPending > 0 || undefined} className="module-entity-details" aria-label={t("workspace.module.editor.detailsAria")} lang={htmlLangForLocale(locale)}>
      <header className="entity-header">
        <div className="entity-title-cell">
          <h3>{displayTitle}</h3>
          {activeDiagramNodeId ? (
            <span className="entity-selected-node" title={activeDiagramNodeId}>
              {t("workspace.module.editor.activeDiagramNode", { id: activeDiagramNodeId })}
            </span>
          ) : null}
        </div>
        <div className="open-path-group">
          <button aria-label={t("workspace.module.editor.refreshEntity")} className="toolbar-button icon-only" disabled={applyBusy} onClick={onRefresh} title={t("workspace.module.editor.refreshEntity")} type="button">
            <RefreshCw aria-hidden="true" size={14} />
          </button>
          <button
            aria-label={t("workspace.module.editor.openFolder")}
            className="toolbar-button icon-only"
            disabled={!canOpenPath}
            onClick={() => {
              setOpenError("");
              openProjectPath(entity.root, openTarget).catch((error: unknown) => {
                setOpenError(t("workspace.module.editor.openFailed", { message: localizedParaDevServiceError(t, error) }));
              });
            }}
            title={t("workspace.module.editor.openFolder")}
            type="button"
          >
            <FolderOpen aria-hidden="true" size={14} />
          </button>
        </div>
      </header>

      <div className="source-tab-strip" role="tablist" aria-label={t("workspace.module.editor.sourceTabs")}>
        <button className={activeSourceKey === INFO_SLOT ? "source-tab selected" : "source-tab"} onClick={() => handleActiveSourceKeyChange(INFO_SLOT)} type="button">
          {t("workspace.module.editor.info")}
        </button>
        {sourcePickerActive ? (
          <>
            <div className="source-tab-source-picker">
              <span>{t("workspace.module.editor.sourceFile")}</span>
              <SelectField
                className="source-tab-source-select"
                controlTitle={sourcePickerPath || t("workspace.module.editor.sourceFile")}
                disabled={isNewScaffold}
                label={t("workspace.module.editor.sourceFile")}
                onChange={(event) => handleActiveSourceKeyChange(event.target.value)}
                options={editableSources.map((source) => ({
                  label: sourceTabLabel(source, editableSources, t),
                  value: source.draftKey
                }))}
                value={sourcePickerValue}
                variant="compact"
              />
            </div>
            {sourcePickerPath ? (
              <code className="source-tab-source-path" title={sourcePickerPath}>
                {sourcePickerPath}
              </code>
            ) : null}
          </>
        ) : (
          editableSourceGroups.primary.map((source) => (
            <button className={source.draftKey === activeSourceKey ? "source-tab selected" : "source-tab"} disabled={isNewScaffold} key={`${entity.id}:${source.draftKey}`} onClick={() => handleActiveSourceKeyChange(source.draftKey)} type="button">
              {sourceTabLabel(source, editableSources, t)}
            </button>
          ))
        )}
        {showImageTab ? (
          <button className={activeSourceKey === IMAGE_SLOT ? "source-tab selected" : "source-tab"} disabled={isNewScaffold} onClick={() => handleActiveSourceKeyChange(IMAGE_SLOT)} type="button">
            {t("workspace.module.editor.image")}
          </button>
        ) : null}
        {showAssetTab ? (
          <button className={activeSourceKey === ASSET_SLOT ? "source-tab selected" : "source-tab"} disabled={isNewScaffold} onClick={() => handleActiveSourceKeyChange(ASSET_SLOT)} type="button">
            {t("workspace.module.editor.assets")}
          </button>
        ) : null}
        {activeSourceKey === IMAGE_SLOT && imageSources.length > 1 ? (
          <div className="source-tab-source-picker image-source-picker">
            <span>{t("workspace.module.editor.image")}</span>
            <SelectField
              className="source-tab-source-select"
              controlTitle={selectedImageSource?.relative_path || selectedImageSource?.path || t("workspace.module.editor.image")}
              label={t("workspace.module.editor.image")}
              onChange={(event) => handleSelectedImageSourceKeyChange(event.target.value)}
              options={imageSources.map((source) => ({
                label: imageSourceLabel(source, imageSources),
                value: source.draftKey
              }))}
              value={selectedImageSource?.draftKey ?? ""}
              variant="compact"
            />
          </div>
        ) : null}
        {!sourcePickerActive
          ? editableSourceGroups.metadata.map((source) => (
              <button
                className={source.draftKey === activeSourceKey ? "source-tab source-tab-advanced selected" : "source-tab source-tab-advanced"}
                disabled={isNewScaffold}
                key={`${entity.id}:${source.draftKey}`}
                onClick={() => handleActiveSourceKeyChange(source.draftKey)}
                title={t("workspace.module.editor.advancedMetadataTitle", {
                  file: source.name || "meta.yaml"
                })}
                type="button"
              >
                {sourceTabLabel(source, editableSources, t)}
              </button>
            ))
          : null}
      </div>

      <div className="entity-editor-body" inert={applyBusy ? true : undefined}>
        {activeSourceKey === INFO_SLOT ? (
          <ModuleEntityInfoPanel
          imageError={imageLoadError}
          imagePreviewUrl={selectedImageDraft?.previewUrl ?? imagePreviewUrl}
          imageSource={selectedImageSource}
          imageLocked={isNewScaffold || !showImageTab}
          locked={isNewScaffold}
          localizationTable={localizationTable}
          collectionId={entity.collectionId ?? ""}
          collectionLocked={!canChangeCollection || applyBusy}
          collectionOptions={collectionOptions}
          localizationBusy={localizationPending > 0 || localizationWorkspaceState.status === "loading"}
          loadError={localizationWorkspaceState.error || loadError}
          onImageClick={() => handleActiveSourceKeyChange(IMAGE_SLOT)}
          onObjectIdChange={(value) => onInfoDraft(entity.id, { objectId: value, title: displayTitle })}
          onLocalizationChange={handleLocalizationChange}
          onLocalizationKeyChange={handleLocalizationKeyChange}
          onLocalizationRowAdd={handleLocalizationRowAdd}
          onLocalizationRowRemove={handleLocalizationRowRemove}
          onCollectionChange={onCollectionChange}
          onTitleChange={handleTitleChange}
          onTitleCommit={handleTitleCommit}
          canAddLocalizationRow={!isNewScaffold && localizationSources.length > 0 && localizationWorkspaceState.status === "ready" && localizationPending === 0}
          objectId={displayObjectId}
          pathValue={displayPath}
          t={t}
          title={displayTitle}
          />
        ) : isNewScaffold ? (
          <div aria-live="polite" className="scaffold-source-locked" role="status">
            <strong>{t("workspace.module.editor.scaffoldFirstTitle")}</strong>
            <p>{t("workspace.module.editor.scaffoldFirstBody")}</p>
          </div>
        ) : activeSourceKey === ASSET_SLOT ? (
          <AssetDraftEditor
            entity={entity}
            key={entity.id}
            onAssetDrafts={(assets) => onAssetDrafts?.(entity.id, assets)}
            sources={assetSources}
            t={t}
          />
        ) : isTextSource && activeSource ? (
          <div className={sourceEditorHasChrome ? "source-editor-panel has-chrome" : "source-editor-panel"}>
            {sourceEditorHasChrome ? (
              <div className="source-editor-chrome">
                {loadError ? <small className="project-path error">{loadError}</small> : null}
                {sourceFormModeVisible ? (
                  <div className="source-form-mode-row">
                    <div className="source-form-mode segmented" role="group" aria-label={t("workspace.module.editor.sourceFile")}>
                      <button
                        aria-pressed={sourceFormMode === "guided"}
                        className={sourceFormMode === "guided" ? "selected" : ""}
                        disabled={activeSourceFormState.status === "loading"}
                        onClick={handleGuidedMode}
                        type="button"
                      >
                        {t("workspace.module.editor.guided")}
                      </button>
                      <button
                        aria-pressed={sourceFormMode === "code"}
                        className={sourceFormMode === "code" ? "selected" : ""}
                        onClick={handleCodeMode}
                        type="button"
                      >
                        {t("workspace.module.editor.code")}
                      </button>
                    </div>
                    {activeSourceFormState.status === "loading" ? (
                      <small aria-live="polite" className="source-form-loading" role="status">
                        {t("workspace.module.editor.guidedLoading")}
                      </small>
                    ) : null}
                  </div>
                ) : null}
                {activeSourceFormState.error ? <small className="project-path error" role="alert">{activeSourceFormState.error}</small> : null}
              </div>
            ) : null}
            <Suspense fallback={<div className="editor-loading">{t("workspace.module.editor.loadingEditor")}</div>}>
              {showGuidedSourceForm && activeSourceFormState.form ? (
                <GuidedSourceForm
                  disabled={activeSourceFormState.status === "loading"}
                  form={activeSourceFormState.form}
                  locale={locale}
                  onChange={handleGuidedSourceChange}
                  onSearch={(query) => requestSourceForm(editorValueRef.current, true, query)}
                  text={
                    activeSourceFormState.status === "loading"
                      ? activeSourceFormState.projectedText
                      : editorValue
                  }
                  t={t}
                />
              ) : (
                <SourceCodeEditor
                  gameRoot={gameRoot}
                  kind={activeSource.editorKind}
                  onChange={(value) => onTextDraft(entity.id, activeSource.draftKey, value)}
                  projectRoot={projectRoot}
                  sourcePath={activeSource.path || activeSource.relative_path}
                  theme={theme}
                  value={editorValue}
                />
              )}
            </Suspense>
          </div>
        ) : imageReplacementUnavailableReason ? (
          <div aria-live="polite" className="image-editor-unavailable" role="status">
            <p>{imageReplacementUnavailableReason}</p>
            {selectedImageSource?.relative_path || selectedImageSource?.path ? (
              <code>{selectedImageSource.relative_path || selectedImageSource.path}</code>
            ) : null}
          </div>
        ) : (
          <Suspense fallback={<div className="editor-loading">{t("workspace.module.editor.loadingEditor")}</div>}>
            <ImageDraftEditor
              defaultSavePath={selectedImagePath}
              entity={imageEditorEntity ?? entity}
              initialImageSource={imagePreviewUrl}
              key={`${entity.id}:${selectedImageSource?.draftKey ?? "draft"}`}
              onImageDraft={(image) => {
                const path = image.path || selectedImagePath;
                onImageDraft(entity.id, {
                  ...image,
                  ...(selectedImageSource ? { sourceKey: selectedImageSource.draftKey } : {}),
                  ...(path ? { path } : {})
                });
              }}
              source={selectedImageSource}
              t={t}
              theme={theme}
            />
          </Suspense>
        )}
      </div>

      <footer className="entity-footer">
        <div className="entity-footer-status">
          {!entityActive ? (
            <span className="status-pill scaffold">
              {t("workspace.module.editor.activity.inactive")}
            </span>
          ) : null}
          <span className={`status-pill ${entity.sourceConflict ? "error" : entity.draftState === "clean" ? "ready" : "scaffold"}`}>
            {t(
              entity.sourceConflict
                ? entity.sourceConflict === "missing"
                  ? "workspace.module.editor.sourceMissingStatus"
                  : "workspace.module.editor.sourceChangedStatus"
                : draftStateTranslationKey[entity.draftState]
            )}
          </span>
          {entity.sourceConflict ? (
            <small className="project-path error" role="alert">
              {t(
                entity.sourceConflict === "missing"
                  ? "workspace.module.editor.sourceMissing"
                  : "workspace.module.editor.sourceChanged"
              )}
            </small>
          ) : null}
          {openError ? <small className="project-path error">{openError}</small> : null}
          {applyError ? <small className="project-path error" role="alert">{t("workspace.module.editor.applyFailed", { message: applyError })}</small> : null}
        </div>
        <div className="entity-footer-actions">
          {onActivityChange ? (
            <button
              className="toolbar-button"
              disabled={applyBusy || !canChangeActivity}
              onClick={() => onActivityChange(!entityActive)}
              title={t(
                entityActive
                  ? "workspace.module.editor.activity.deactivateTitle"
                  : "workspace.module.editor.activity.activateTitle",
              )}
              type="button"
            >
              <Power aria-hidden="true" size={14} />
              {t(
                entityActive
                  ? "workspace.module.editor.activity.deactivate"
                  : "workspace.module.editor.activity.activate",
              )}
            </button>
          ) : null}
          {onDuplicate ? (
            <button
              className="toolbar-button"
              disabled={applyBusy || entity.draftState !== "clean" || !canDuplicate}
              onClick={onDuplicate}
              title={t(
                entity.draftState !== "clean"
                  ? "workspace.module.editor.duplicate.dirty"
                  : canDuplicate
                    ? "workspace.module.editor.duplicate.openTitle"
                    : "workspace.module.editor.duplicate.unavailable"
              )}
              type="button"
            >
              <CopyPlus aria-hidden="true" size={14} />
              {t("workspace.module.editor.duplicate.open")}
            </button>
          ) : null}
          {onBuildModule ? (
            <button
              className="toolbar-button"
              data-paradev-build-target-kind={buildTargetKind}
              disabled={applyBusy || entity.draftState !== "clean" || !entityActive}
              onClick={onBuildModule}
              title={t(
                !entityActive
                  ? "workspace.module.editor.activity.buildInactive"
                  : entity.draftState === "clean"
                    ? buildTargetKind === "collection"
                      ? "workspace.module.editor.buildCollectionTitle"
                      : "workspace.module.editor.buildModuleTitle"
                    : buildTargetKind === "collection"
                      ? "workspace.module.editor.buildCollectionDirty"
                      : "workspace.module.editor.buildModuleDirty",
                { module: entity.objectId, collection: entity.objectId }
              )}
              type="button"
            >
              <Hammer aria-hidden="true" size={14} />
              {t(
                buildTargetKind === "collection"
                  ? "workspace.module.editor.buildCollection"
                  : "workspace.module.editor.buildModule"
              )}
            </button>
          ) : null}
          {onBuildAffected ? (
            <button
              className="toolbar-button"
              data-paradev-build-target-kind="family"
              disabled={applyBusy || entity.draftState !== "clean"}
              onClick={onBuildAffected}
              title={t(
                entity.draftState === "clean"
                  ? "workspace.module.editor.buildAffectedTitle"
                  : "workspace.module.editor.buildAffectedDirty",
                { family: buildAffectedFamilyTitle || entity.family }
              )}
              type="button"
            >
              <Hammer aria-hidden="true" size={14} />
              {t("workspace.module.editor.buildAffected", { family: buildAffectedFamilyTitle || entity.family })}
            </button>
          ) : null}
          <button className="toolbar-button warning" disabled={applyBusy || entity.draftState === "clean"} onClick={() => onRestore(entity.id)} type="button">
            <RotateCcw aria-hidden="true" size={14} />
            {t("workspace.module.editor.restore")}
          </button>
          <button
            className="toolbar-button primary"
            disabled={!canApply || applyBusy || localizationPending > 0}
            onClick={() => onApply(entity.id)}
            title={
              entity.sourceConflict
                ? t(
                    entity.sourceConflict === "missing"
                      ? "workspace.module.editor.sourceMissing"
                      : "workspace.module.editor.sourceChanged"
                  )
                : canApply
                  ? t("workspace.module.editor.applyTitle")
                  : t("workspace.module.editor.saveDisabled")
            }
            type="button"
          >
            <Save aria-hidden="true" size={14} />
            {applyBusy ? t("workspace.module.editor.applying") : t("workspace.module.editor.saveDraft")}
          </button>
        </div>
      </footer>
    </section>
  );
}

function ModuleEntityInfoPanel({
  canAddLocalizationRow,
  collectionId,
  collectionLocked,
  collectionOptions,
  imageError,
  imagePreviewUrl,
  imageSource,
  imageLocked,
  localizationBusy,
  localizationTable,
  locked,
  loadError,
  onImageClick,
  onCollectionChange,
  onObjectIdChange,
  onLocalizationChange,
  onLocalizationKeyChange,
  onLocalizationRowAdd,
  onLocalizationRowRemove,
  onTitleChange,
  onTitleCommit,
  objectId,
  pathValue,
  title,
  t
}: {
  canAddLocalizationRow: boolean;
  collectionId: string;
  collectionLocked: boolean;
  collectionOptions: Array<{ label: string; value: string }>;
  imageError: string;
  imagePreviewUrl: string;
  imageSource: ModuleSourceSlot | null;
  imageLocked: boolean;
  localizationBusy: boolean;
  localizationTable: ModuleLocalizationTable;
  locked: boolean;
  loadError: string;
  onImageClick: () => void;
  onCollectionChange?: (collectionId: string) => void;
  onObjectIdChange: (value: string) => void;
  onLocalizationChange: (language: string, key: string, value: string, slot?: string) => void;
  onLocalizationKeyChange: (oldKey: string, value: string) => void;
  onLocalizationRowAdd: () => void;
  onLocalizationRowRemove: (key: string) => void;
  onTitleChange: (value: string) => void;
  onTitleCommit: (value: string) => void;
  objectId: string;
  pathValue: string;
  t: Translator;
  title: string;
}) {
  const objectIdInputSize = Math.max(10, Math.min(44, objectId.length + 1));
  return (
    <div className="entity-info-panel">
      {locked ? (
        <div aria-live="polite" className="scaffold-info-notice" role="status">
          <strong>{t("workspace.module.editor.scaffoldFirstTitle")}</strong>
          <span>{t("workspace.module.editor.scaffoldFirstBody")}</span>
        </div>
      ) : null}
      <section className="entity-info-section entity-identity-section">
        <div className="entity-info-section-heading">
          <strong>{t("workspace.module.editor.info")}</strong>
        </div>
        <div className="entity-info-main">
          <div className="entity-info-fields" aria-label={t("workspace.module.editor.info")}>
            <label className="entity-info-field object-id-field" style={{ "--entity-id-input-width": `${objectIdInputSize}ch` } as CSSProperties}>
              <span>{t("workspace.module.editor.objectId")}</span>
              <input onChange={(event) => onObjectIdChange(event.target.value)} readOnly={locked} size={objectIdInputSize} spellCheck={false} value={objectId} />
            </label>
            <label className="entity-info-field">
              <span>{t("workspace.module.editor.name")}</span>
              <input onBlur={(event) => onTitleCommit(event.currentTarget.value)} onChange={(event) => onTitleChange(event.target.value)} readOnly={locked} value={title} />
            </label>
            {collectionOptions.length > 0 || collectionId ? (
              <div className="entity-info-field">
                <span>{t("workspace.module.editor.collection")}</span>
                <SelectField
                  disabled={collectionLocked}
                  label={t("workspace.module.editor.collection")}
                  onChange={(event) => onCollectionChange?.(event.target.value)}
                  options={[
                    {
                      label: t("workspace.module.editor.collectionNone"),
                      value: ""
                    },
                    ...collectionOptions
                  ]}
                  value={collectionId}
                />
              </div>
            ) : null}
            <label className="entity-info-field entity-info-path-field">
              <span>{t("workspace.module.editor.path")}</span>
              <input readOnly title={pathValue} value={pathValue} />
            </label>
          </div>
          <div className="entity-profile-column">
            <button className="entity-profile-image" disabled={imageLocked} onClick={onImageClick} title={t("workspace.module.editor.imageJump")} type="button">
              {imagePreviewUrl ? <img alt="" src={imagePreviewUrl} /> : <span>{imageSource?.name ?? t("workspace.module.editor.noImage")}</span>}
            </button>
            {imageError ? <small className="project-path error">{imageError}</small> : null}
          </div>
        </div>
      </section>
      <section className="entity-info-section entity-localization-panel">
        <div className="entity-info-section-heading">
          <span className="entity-info-heading-title">
            <strong>{t("workspace.module.editor.translations")}</strong>
            <small className="translation-key-hint">{t("workspace.module.editor.translationAliasHint", { object: objectId })}</small>
          </span>
          <span className="entity-info-heading-actions">
            <button
              aria-label={t("workspace.module.editor.addTranslationRow")}
              className="toolbar-button icon-only entity-localization-action"
              disabled={!canAddLocalizationRow}
              onClick={onLocalizationRowAdd}
              title={t("workspace.module.editor.addTranslationRow")}
              type="button"
            >
              <Plus aria-hidden="true" size={13} />
            </button>
          </span>
          {loadError ? <small className="project-path error">{loadError}</small> : null}
        </div>
        {localizationTable.rows.length > 0 ? (
          <div className="entity-localization-table" style={{ "--language-count": localizationTable.languages.length } as CSSProperties}>
            <div className="entity-localization-row header">
              <span>{t("workspace.module.editor.translationKey")}</span>
              {localizationTable.languages.map((language) => (
                <span key={language} title={language}>
                  {localizationLanguageLabel(language, t)}
                </span>
              ))}
              <span className="entity-localization-row-action" aria-hidden="true" />
            </div>
            {localizationTable.rows.map((row) => (
              <div className="entity-localization-row" key={row.key}>
                <textarea
                  aria-label={`${t("workspace.module.editor.translationKey")} ${row.key}`}
                  className="entity-localization-key-input"
                  defaultValue={row.key}
                  disabled={localizationBusy}
                  onBlur={(event) => onLocalizationKeyChange(row.key, event.currentTarget.value)}
                  onKeyDown={(event) => {
                    if (event.key === "Enter" && !event.shiftKey) {
                      event.preventDefault();
                      event.currentTarget.blur();
                    }
                  }}
                  rows={localizationTextareaRows(row.key, 26)}
                  spellCheck={false}
                />
                {localizationTable.languages.map((language) => (
                  <textarea
                    aria-label={`${row.key} ${localizationLanguageLabel(language, t)}`}
                    defaultValue={row.values[language]?.text ?? ""}
                    disabled={localizationBusy}
                    key={`${row.key}:${language}:${row.values[language]?.text ?? ""}`}
                    onBlur={(event) => onLocalizationChange(language, row.key, event.currentTarget.value, row.values[language]?.slot)}
                    rows={localizationTextareaRows(row.values[language]?.text ?? "")}
                  />
                ))}
                <span className="entity-localization-row-action">
                  <button
                    aria-label={t("workspace.module.editor.removeTranslationRow", { key: row.key })}
                    className="toolbar-button icon-only entity-localization-action"
                    disabled={localizationBusy}
                    onClick={() => onLocalizationRowRemove(row.key)}
                    title={t("workspace.module.editor.removeTranslationRow", { key: row.key })}
                    type="button"
                  >
                    <Trash2 aria-hidden="true" size={12} />
                  </button>
                </span>
              </div>
            ))}
          </div>
        ) : (
          <div className="entity-localization-empty">{t("workspace.module.editor.noTranslations")}</div>
        )}
      </section>
    </div>
  );
}

function localizationTextareaRows(value: string, charsPerLine = 36): number {
  const rows = value.split(/\r?\n/).reduce((count, line) => count + Math.max(1, Math.ceil(line.length / charsPerLine)), 0);
  return Math.max(1, Math.min(12, rows));
}

const LOCALIZATION_LANGUAGE_LABEL_KEYS: Partial<Record<string, TranslationKey>> = {
  l_english: "workspace.module.editor.language.english",
  l_french: "workspace.module.editor.language.french",
  l_german: "workspace.module.editor.language.german",
  l_russian: "workspace.module.editor.language.russian",
  l_simp_chinese: "workspace.module.editor.language.simpChinese",
  l_spanish: "workspace.module.editor.language.spanish"
};

function localizationLanguageLabel(language: string, t: Translator): string {
  const key = LOCALIZATION_LANGUAGE_LABEL_KEYS[language];
  return key ? t(key) : language;
}

function binarySourceDataUrl(payload: BinarySourcePayload): string {
  const bytes = Uint8Array.from(payload.bytes);
  let binary = "";
  const chunkSize = 0x8000;
  for (let index = 0; index < bytes.length; index += chunkSize) {
    binary += String.fromCharCode(...bytes.subarray(index, index + chunkSize));
  }
  return `data:${payload.mimeType || "application/octet-stream"};base64,${window.btoa(binary)}`;
}

function sourceSlotLabel(source: ModuleSourceSlot, t: Translator): string {
  const slot = source.slot;
  if (slot === "def") {
    return t("workspace.module.editor.slot.def");
  }
  if (slot === "loc") {
    return t("workspace.module.editor.slot.loc");
  }
  if (slot === "meta") {
    return t("workspace.module.editor.advancedMetadata");
  }
  if (slot.startsWith("focus:") && slot.endsWith(":info")) {
    return t("workspace.module.editor.slot.focusInfo", { id: slot.slice("focus:".length, -":info".length) });
  }
  if (source.editorKind === "localization") {
    return t("workspace.module.editor.slot.localizationLanguage", {
      language: localizationLanguageLabel(languageFromSource(source), t)
    });
  }
  return slot;
}

function sourceTabLabel(source: ModuleSourceSlot, sources: ModuleSourceSlot[], t: Translator): string {
  const matchingSlotSources = sources.filter((item) => item.slot === source.slot);
  const label = matchingSlotSources.length > 1 && source.editorKind === "localization"
    ? t("workspace.module.editor.slot.localizationLanguage", {
        language: localizationLanguageLabel(languageFromSource(source), t)
      })
    : sourceSlotLabel(source, t);
  if (matchingSlotSources.length < 2) {
    return label;
  }
  const matchingNameCount = matchingSlotSources.filter((item) => item.name === source.name).length;
  const identity = matchingNameCount > 1 ? source.relative_path || source.path || sourceIdentityFromDraftKey(source) || source.name : source.name;
  return identity ? `${label} · ${identity}` : label;
}

function imageSourceLabel(source: ModuleSourceSlot, sources: ModuleSourceSlot[]): string {
  const matchingNameCount = sources.filter((item) => item.name === source.name).length;
  return matchingNameCount > 1 ? source.relative_path || source.path || sourceIdentityFromDraftKey(source) || source.name : source.name || source.slot;
}

function sourceIdentityFromDraftKey(source: ModuleSourceSlot): string {
  const prefix = `${source.slot}::`;
  return source.draftKey.startsWith(prefix) ? source.draftKey.slice(prefix.length) : "";
}

function activeSourceKeyForSourcePath(entity: ModuleEntity | null, targetSourcePath: string): string {
  const source = sourceSlotForTargetPath(entity?.sourceSlots ?? [], targetSourcePath);
  if (!source) {
    return INFO_SLOT;
  }
  if (source.editorKind === "image") {
    return IMAGE_SLOT;
  }
  return assetSourcesForEntity(entity).some((item) => item.draftKey === source.draftKey) ? ASSET_SLOT : source.draftKey;
}

function sourcePathForActiveSourceKey(
  entity: ModuleEntity,
  activeSourceKey: string,
  selectedImageSourceKey: string,
  targetSourcePath: string
): string {
  let source: ModuleSourceSlot | null | undefined;
  if (activeSourceKey === INFO_SLOT) {
    return "";
  }
  if (activeSourceKey === IMAGE_SLOT) {
    source = entity.sourceSlots.find(
      (item) =>
        item.editorKind === "image"
        && item.draftKey === selectedImageSourceKey
    ) ?? entity.sourceSlots.find((item) => item.editorKind === "image");
  } else if (activeSourceKey === ASSET_SLOT) {
    const sources = assetSourcesForEntity(entity);
    source = sourceSlotForTargetPath(sources, targetSourcePath) ?? sources[0];
  } else {
    source = entity.sourceSlots.find(
      (item) => item.draftKey === activeSourceKey
    );
  }
  return source?.relative_path || source?.path || "";
}

function imageSourceKeyForSourcePath(entity: ModuleEntity | null, targetSourcePath: string): string {
  const sources = entity?.sourceSlots ?? [];
  const source = sourceSlotForTargetPath(sources, targetSourcePath);
  if (source?.editorKind === "image") {
    return source.draftKey;
  }
  return sources.find((item) => item.editorKind === "image")?.draftKey ?? "";
}

function imageDraftForSource(entity: ModuleEntity | null, source: ModuleSourceSlot | null): NonNullable<ModuleEntityDrafts["image"]> | undefined {
  const draft = entity?.drafts.image;
  if (!entity || !draft || !source) {
    return draft;
  }
  if (draft.sourceKey) {
    return draft.sourceKey === source.draftKey ? draft : undefined;
  }
  if (draft.path) {
    const draftPath = normalizedSourcePath(draft.path);
    const sourcePaths = [defaultImageDraftPath(entity, source), source.path, source.relative_path].map(normalizedSourcePath);
    if (sourcePaths.includes(draftPath)) {
      return draft;
    }
  }
  const firstImageSource = entity.sourceSlots.find((item) => item.editorKind === "image");
  return firstImageSource?.draftKey === source.draftKey ? draft : undefined;
}

function sourceSlotForTargetPath(sourceSlots: ModuleSourceSlot[], targetSourcePath: string): ModuleSourceSlot | null {
  const target = normalizedSourcePath(targetSourcePath);
  if (!target) {
    return null;
  }
  return sourceSlots.find((source) => [source.path, source.relative_path].some((path) => normalizedSourcePath(path) === target)) ?? null;
}

function normalizedSourcePath(value: string | undefined): string {
  return (value ?? "").replace(/\\/g, "/").replace(/^\/+/, "").replace(/\/+$/, "");
}

function languageFromSource(source: ModuleSourceSlot): string {
  const path = `${source.relative_path} ${source.name}`.toLowerCase();
  if (path.includes("simp_chinese") || path.includes("chinese") || path.includes("/zh")) {
    return "l_simp_chinese";
  }
  if (path.includes("french")) {
    return "l_french";
  }
  if (path.includes("german")) {
    return "l_german";
  }
  if (path.includes("russian")) {
    return "l_russian";
  }
  if (path.includes("spanish")) {
    return "l_spanish";
  }
  return "l_english";
}
