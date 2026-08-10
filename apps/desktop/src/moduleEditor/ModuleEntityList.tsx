import { useEffect, useId, useMemo, useRef, useState, type FormEvent } from "react";
import { Check, CheckCheck, ChevronDown, ChevronUp, Database, GitBranch, ListFilter, ListPlus, Plus, RefreshCw, Search, SlidersHorizontal, Trash2, X } from "lucide-react";
import { htmlLangForLocale, type Locale, type TranslationKey, type Translator } from "../i18n";
import type { ModuleCreateIntent, ProjectBrowserItem } from "../types";
import { SelectField } from "../components/ui/SelectField";
import { buildModuleEntitySelectionState, selectModuleEntityRange, selectModuleEntityScope, templateCreateReferenceOptions, type ModuleDraftState, type ModuleEntity, type TemplateCreateField } from "./model";
import { ModuleEntityThumbnail } from "./ModuleEntityThumbnail";

type ModuleEntityListProps = {
  activityFilter?: "all" | "active" | "inactive";
  allEntities: ModuleEntity[];
  catalogMissing?: boolean;
  catalogPreparing?: boolean;
  catalogSearch?: boolean;
  createAdvancedFields: TemplateCreateField[];
  createObjectId: string;
  createObjectIdPreview: string;
  createPrimaryFields: TemplateCreateField[];
  createPreviewValues: Record<string, string>;
  createBusy: boolean;
  createError: string;
  createTemplateId: string;
  createTemplateOptions: Array<{ label: string; value: string }>;
  createTemplateTitle: string;
  createUnavailableReason?: string;
  batchUnavailableReason?: string;
  createValues: Record<string, string>;
  createIntent?: ModuleCreateIntent | null;
  entities: ModuleEntity[];
  hasMore?: boolean;
  hydratingEntityId?: string;
  loadError?: string;
  loadedCount?: number;
  loading?: boolean;
  projectRoot: string;
  query: string;
  referenceItems?: readonly ProjectBrowserItem[];
  selectedId: string;
  selectedIds: Set<string>;
  showAdvancedCreate: boolean;
  locale: Locale;
  t: Translator;
  onActivityFilterChange?: (value: "all" | "active" | "inactive") => void;
  onCreate: () => boolean | Promise<boolean>;
  onOpenBatch?: () => void;
  onOpenCollectionCreate?: () => void;
  collectionCreateLabel?: string;
  onCreateIntentConsumed?: (nonce: number) => void;
  onCreateObjectIdChange: (value: string) => void;
  onCreateValueChange: (name: string, value: string) => void;
  onLoadMore?: () => void | Promise<void>;
  onPrepareCatalog?: () => void | Promise<void>;
  onCreateTemplateChange: (value: string) => void;
  onShowAdvancedCreateChange: (show: boolean) => void;
  onQueryChange: (value: string) => void;
  onRemoveSelected: () => void;
  onRetryLoad?: () => void;
  onSelect: (id: string) => void;
  onSelectionChange: (ids: Set<string>) => void;
  totalCount?: number;
};

const draftKey: Record<ModuleDraftState, TranslationKey> = {
  clean: "workspace.module.editor.draft.clean",
  modified: "workspace.module.editor.draft.modified",
  new: "workspace.module.editor.draft.new",
  remove: "workspace.module.editor.draft.remove",
};

const DIRECT_RESULT_BATCH_SIZE = 100;

export function ModuleEntityList({
  activityFilter = "all",
  allEntities,
  catalogMissing = false,
  catalogPreparing = false,
  catalogSearch = false,
  createAdvancedFields,
  createObjectId,
  createObjectIdPreview,
  createPrimaryFields,
  createPreviewValues,
  createBusy,
  createError,
  createTemplateId,
  createTemplateOptions,
  createTemplateTitle,
  createUnavailableReason = "",
  batchUnavailableReason = "",
  createValues,
  createIntent = null,
  entities,
  hasMore = false,
  hydratingEntityId = "",
  loadError = "",
  loadedCount = allEntities.length,
  loading = false,
  locale,
  projectRoot,
  query,
  referenceItems = [],
  selectedId,
  selectedIds,
  showAdvancedCreate,
  t,
  onActivityFilterChange = () => undefined,
  onCreate,
  onOpenBatch,
  onOpenCollectionCreate,
  collectionCreateLabel = "",
  onCreateIntentConsumed,
  onCreateObjectIdChange,
  onCreateValueChange,
  onLoadMore,
  onPrepareCatalog,
  onCreateTemplateChange,
  onShowAdvancedCreateChange,
  onQueryChange,
  onRemoveSelected,
  onRetryLoad,
  onSelect,
  onSelectionChange,
  totalCount = allEntities.length,
}: ModuleEntityListProps) {
  const entityListId = useId();
  const createUnavailableId = `${entityListId}-create-unavailable`;
  const allEntityIds = useMemo(() => allEntities.map((entity) => entity.id), [allEntities]);
  const visibleEntityIds = useMemo(() => entities.map((entity) => entity.id), [entities]);
  const selection = useMemo(() => buildModuleEntitySelectionState(allEntities, entities, selectedIds), [allEntities, entities, selectedIds]);
  const visibleSelectionRef = useRef<HTMLInputElement>(null);
  const selectionAnchorRef = useRef("");
  const removalTargets = selectedIds.size > 0 ? allEntities.filter((entity) => selectedIds.has(entity.id)) : allEntities.filter((entity) => entity.id === selectedId);
  const removeCount = removalTargets.length;
  const removeDisabled = removeCount === 0;
  const persistedRemovalCount = removalTargets.filter((entity) => entity.root.trim()).length;
  const resultSummary = selection.hasFilteredScope
    ? t("workspace.module.editor.filteredResultsSummary", {
        total: String(selection.totalCount),
        visible: String(selection.visibleCount),
      })
    : t("workspace.module.editor.resultsSummary", {
        count: String(selection.visibleCount),
      });
  const selectionSummary = selection.selectedCount > 0 ? `${t("workspace.module.editor.selectedSummary", { count: String(selection.selectedCount) })} · ${resultSummary}` : resultSummary;
  const removeTitle =
    selectedIds.size > 0
      ? removeCount > 1
        ? t("workspace.module.editor.removeCount", {
            count: String(removeCount),
          })
        : t("workspace.module.editor.removeSelection")
      : t("workspace.module.editor.removeCurrent");
  const selectVisibleTitle = selection.allVisibleSelected ? t("workspace.module.editor.clearVisibleSelection") : t("workspace.module.editor.selectVisible");
  const listClasses = ["module-entity-list", selection.selectedCount > 0 ? "selection-active" : ""].filter(Boolean).join(" ");
  const announcedTotalCount = Math.max(totalCount, allEntities.length, entities.length);
  const announcedLoadedCount = Math.min(Math.max(loadedCount, 0), announcedTotalCount);
  const initialLoading = loading && entities.length === 0;
  const showPagingFooter = !catalogMissing && !initialLoading && (loading || Boolean(loadError) || hasMore || announcedLoadedCount < announcedTotalCount);
  const pagingSummary = t("workspace.module.editor.catalogLoadedSummary", {
    loaded: String(announcedLoadedCount),
    total: String(announcedTotalCount),
  });
  const emptyMessage = initialLoading ? t("workspace.module.editor.catalogLoading") : query.trim() ? t("workspace.module.editor.resultsSummary", { count: "0" }) : t("workspace.module.editor.emptyEntities");
  const directDisclosureScope = `${projectRoot}\u0000${activityFilter}\u0000${query.trim()}`;
  const [directDisclosure, setDirectDisclosure] = useState(() => ({
    limit: DIRECT_RESULT_BATCH_SIZE,
    scope: directDisclosureScope,
  }));
  const directResultLimit = directDisclosure.scope === directDisclosureScope ? directDisclosure.limit : DIRECT_RESULT_BATCH_SIZE;
  const directBaseCount = catalogSearch ? entities.length : Math.min(directResultLimit, entities.length);
  const renderedEntities = useMemo(() => {
    if (catalogSearch || entities.length <= directBaseCount) {
      return entities;
    }
    const directEntities = entities.slice(0, directBaseCount);
    const selectedEntity = entities.find((entity) => entity.id === selectedId);
    if (selectedEntity && !directEntities.some((entity) => entity.id === selectedEntity.id)) {
      directEntities.push(selectedEntity);
    }
    return directEntities;
  }, [catalogSearch, directBaseCount, entities, selectedId]);
  const directRemainingCount = catalogSearch ? 0 : Math.max(entities.length - directBaseCount, 0);
  const showDirectFooter = !initialLoading && directRemainingCount > 0;
  const directResultSummary = t("workspace.module.editor.directShownSummary", {
    shown: String(renderedEntities.length),
    total: String(entities.length),
  });
  const [actionDialog, setActionDialog] = useState<"create" | "remove" | null>(() => (createIntent && !createUnavailableReason ? "create" : null));
  const [activeCreateIntent, setActiveCreateIntent] = useState<ModuleCreateIntent | null>(() => (createUnavailableReason ? null : createIntent));
  const [createValidation, setCreateValidation] = useState<TemplateCreateValidation>(() => emptyTemplateCreateValidation());
  const lastCreateIntentNonceRef = useRef(createIntent?.nonce ?? 0);

  useEffect(() => {
    if (visibleSelectionRef.current) {
      visibleSelectionRef.current.indeterminate = selection.someVisibleSelected && !selection.allVisibleSelected;
    }
  }, [selection.allVisibleSelected, selection.someVisibleSelected]);

  useEffect(() => {
    if (!createIntent) {
      return;
    }
    if (lastCreateIntentNonceRef.current !== createIntent.nonce) {
      lastCreateIntentNonceRef.current = createIntent.nonce;
      setCreateValidation(emptyTemplateCreateValidation());
      setActiveCreateIntent(createUnavailableReason ? null : createIntent);
      setActionDialog(createUnavailableReason ? null : "create");
    }
    onCreateIntentConsumed?.(createIntent.nonce);
  }, [createIntent, createUnavailableReason, onCreateIntentConsumed]);

  useEffect(() => {
    setCreateValidation(emptyTemplateCreateValidation());
  }, [createTemplateId]);

  useEffect(() => {
    if (!createUnavailableReason) {
      return;
    }
    setActiveCreateIntent(null);
    setActionDialog((current) => (current === "create" ? null : current));
  }, [createUnavailableReason]);

  const closeCreateDialog = () => {
    setCreateValidation(emptyTemplateCreateValidation());
    setActiveCreateIntent(null);
    setActionDialog(null);
  };

  const handleCreateSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (createUnavailableReason) {
      return;
    }
    const validation = validateTemplateCreateForm(createObjectId, createObjectIdPreview, [...createPrimaryFields, ...createAdvancedFields], createValues, createPreviewValues);
    setCreateValidation(validation);
    if (validation.objectId || Object.keys(validation.fields).length > 0) {
      if (createAdvancedFields.some((field) => validation.fields[field.name])) {
        onShowAdvancedCreateChange(true);
      }
      return;
    }
    const created = await onCreate();
    if (created) {
      closeCreateDialog();
    }
  };

  const selectScope = (scopeIds: string[], mode: "replace" | "add" | "toggle") => {
    onSelectionChange(selectModuleEntityScope(selectedIds, scopeIds, mode));
    if (scopeIds.length > 0) {
      selectionAnchorRef.current = scopeIds[scopeIds.length - 1];
    }
  };

  const clearSelection = () => onSelectionChange(new Set());

  const anchorForRange = (targetId: string) => {
    if (visibleEntityIds.includes(selectionAnchorRef.current)) {
      return selectionAnchorRef.current;
    }
    if (visibleEntityIds.includes(selectedId)) {
      return selectedId;
    }
    return visibleEntityIds.find((id) => selectedIds.has(id)) ?? targetId;
  };

  const selectRange = (targetId: string, action: "select" | "deselect") => {
    const anchorId = anchorForRange(targetId);
    onSelectionChange(selectModuleEntityRange(selectedIds, visibleEntityIds, anchorId, targetId, action));
    selectionAnchorRef.current = targetId;
  };

  const selectSingle = (targetId: string, selected: boolean) => {
    const next = new Set(selectedIds);
    if (selected) {
      next.add(targetId);
    } else {
      next.delete(targetId);
    }
    selectionAnchorRef.current = targetId;
    onSelectionChange(next);
  };

  return (
    <aside className={listClasses} aria-label={t("workspace.module.editor.listAria")} lang={htmlLangForLocale(locale)}>
      <div className="module-entity-tools">
        <label className="module-search-field">
          <Search aria-hidden="true" size={14} />
          <input aria-describedby={catalogMissing ? `${entityListId}-catalog-recovery` : undefined} aria-label={t(catalogSearch ? "workspace.module.editor.searchCatalogAria" : "workspace.module.editor.searchAria")} disabled={catalogPreparing || (catalogMissing && catalogSearch)} onChange={(event) => onQueryChange(event.target.value)} placeholder={t(catalogSearch ? "workspace.module.editor.searchCatalog" : "workspace.module.editor.search")} value={query} />
        </label>
        <SelectField
          className="module-activity-filter"
          controlTitle={t("workspace.module.editor.activity.filter")}
          label={t("workspace.module.editor.activity.filter")}
          onChange={(event) => onActivityFilterChange(event.target.value as "all" | "active" | "inactive")}
          options={[
            {
              label: t("workspace.module.editor.activity.filterAll"),
              value: "all",
            },
            {
              label: t("workspace.module.editor.activity.filterActive"),
              value: "active",
            },
            {
              label: t("workspace.module.editor.activity.filterInactive"),
              value: "inactive",
            },
          ]}
          value={activityFilter}
          variant="compact"
        />
        <div className="module-tool-actions">
          <button
            aria-describedby={createUnavailableReason ? createUnavailableId : undefined}
            aria-label={t("workspace.module.editor.new")}
            className="toolbar-button icon-only primary"
            disabled={catalogPreparing || Boolean(createUnavailableReason)}
            onClick={() => {
              setCreateValidation(emptyTemplateCreateValidation());
              setActiveCreateIntent(null);
              setActionDialog("create");
            }}
            title={createUnavailableReason || t("workspace.module.editor.new")}
            type="button"
          >
            <Plus aria-hidden="true" size={14} />
          </button>
          {onOpenCollectionCreate ? (
            <button aria-label={collectionCreateLabel} className="toolbar-button icon-only" disabled={catalogPreparing} onClick={onOpenCollectionCreate} title={collectionCreateLabel} type="button">
              <GitBranch aria-hidden="true" size={14} />
            </button>
          ) : null}
          {onOpenBatch ? (
            <button aria-label={t("workspace.module.editor.batch.open")} className="toolbar-button icon-only" disabled={catalogPreparing || Boolean(batchUnavailableReason)} onClick={onOpenBatch} title={batchUnavailableReason || t("workspace.module.editor.batch.open")} type="button">
              <ListPlus aria-hidden="true" size={14} />
            </button>
          ) : null}
          <button aria-label={removeTitle} className="toolbar-button icon-only danger" disabled={removeDisabled} onClick={() => setActionDialog("remove")} title={removeTitle} type="button">
            <Trash2 aria-hidden="true" size={14} />
          </button>
        </div>
      </div>

      {selection.selectedCount > 0 ? (
        <div className="module-selection-bar" aria-label={t("workspace.module.editor.selectionTools")}>
          <label className="module-selection-check" title={selectVisibleTitle}>
            <input ref={visibleSelectionRef} aria-label={selectVisibleTitle} checked={selection.allVisibleSelected} disabled={selection.visibleCount === 0} onChange={() => selectScope(visibleEntityIds, "toggle")} type="checkbox" />
          </label>
          <span className="module-selection-summary" title={selectionSummary}>
            {selectionSummary}
          </span>
          <div className="module-selection-actions">
            <button aria-label={t("workspace.module.editor.selectFiltered")} className="toolbar-button icon-only" disabled={!query.trim() || selection.visibleCount === 0 || selection.allVisibleSelected} onClick={() => selectScope(visibleEntityIds, "replace")} title={t("workspace.module.editor.selectFiltered")} type="button">
              <ListFilter aria-hidden="true" size={13} />
            </button>
            <button aria-label={t("workspace.module.editor.selectAll")} className="toolbar-button icon-only" disabled={selection.totalCount === 0 || selection.allSelected} onClick={() => selectScope(allEntityIds, "replace")} title={t("workspace.module.editor.selectAll")} type="button">
              <CheckCheck aria-hidden="true" size={13} />
            </button>
            <button aria-label={t("workspace.module.editor.clearSelection")} className="toolbar-button icon-only" disabled={selection.selectedCount === 0} onClick={clearSelection} title={t("workspace.module.editor.clearSelection")} type="button">
              <X aria-hidden="true" size={13} />
            </button>
          </div>
        </div>
      ) : null}

      {actionDialog === "create" ? (
        <div className="module-action-backdrop" role="presentation">
          <form aria-labelledby="module-create-title" aria-modal="true" className="module-action-dialog module-create-form dialog" onSubmit={handleCreateSubmit} role="dialog">
            <div className="module-dialog-heading">
              <span>
                <small>{t("workspace.module.editor.create.template")}</small>
                <h3 id="module-create-title">{t("workspace.module.editor.new")}</h3>
              </span>
              <button aria-label={t("workspace.module.editor.cancel")} className="toolbar-button icon-only" onClick={closeCreateDialog} title={t("workspace.module.editor.cancel")} type="button">
                <X aria-hidden="true" size={14} />
              </button>
            </div>
            <div className="module-create-header">
              <span>
                <small>{t("workspace.module.editor.create.template")}</small>
                {createTemplateOptions.length > 1 ? (
                  <SelectField
                    className="module-create-template-select"
                    label={t("workspace.module.editor.create.template")}
                    onChange={(event) => {
                      setCreateValidation(emptyTemplateCreateValidation());
                      onCreateTemplateChange(event.target.value);
                    }}
                    options={createTemplateOptions}
                    value={createTemplateId}
                  />
                ) : (
                  <strong>{createTemplateTitle}</strong>
                )}
              </span>
              {createAdvancedFields.length > 0 ? (
                <button aria-expanded={showAdvancedCreate} className="module-create-advanced-toggle" onClick={() => onShowAdvancedCreateChange(!showAdvancedCreate)} title={showAdvancedCreate ? t("workspace.module.editor.create.hideAdvanced") : t("workspace.module.editor.create.showAdvanced")} type="button">
                  <SlidersHorizontal aria-hidden="true" size={13} />
                  {showAdvancedCreate ? <ChevronUp aria-hidden="true" size={13} /> : <ChevronDown aria-hidden="true" size={13} />}
                </button>
              ) : null}
            </div>
            <ModuleCreateAiHandoff intent={activeCreateIntent?.ai ?? null} t={t} />
            <label className="module-create-field">
              <small>{t("workspace.module.editor.create.objectId")}</small>
              <input
                aria-invalid={createValidation.objectId || undefined}
                aria-label={t("workspace.module.editor.create.objectId")}
                aria-required="true"
                autoFocus
                onChange={(event) => {
                  setCreateValidation((current) => ({
                    ...current,
                    objectId: false,
                  }));
                  onCreateObjectIdChange(event.target.value);
                }}
                placeholder={createObjectIdPreview}
                value={createObjectId}
              />
              {createValidation.objectId ? (
                <span className="module-create-field-error" role="alert">
                  {t("workspace.module.editor.create.validation.required", {
                    field: t("workspace.module.editor.create.objectId"),
                  })}
                </span>
              ) : null}
            </label>
            <div className="module-create-fields">
              {createPrimaryFields.map((field) => (
                <TemplateCreateInput
                  field={field}
                  key={field.name}
                  onChange={(name, value) => {
                    setCreateValidation((current) => clearTemplateCreateFieldValidation(current, name));
                    onCreateValueChange(name, value);
                  }}
                  previewValue={createPreviewValues[field.name] ?? field.defaultValue}
                  referenceItems={referenceItems}
                  validationIssue={createValidation.fields[field.name]}
                  value={createValues[field.name] ?? ""}
                  t={t}
                />
              ))}
            </div>
            {showAdvancedCreate && createAdvancedFields.length > 0 ? (
              <div className="module-create-fields advanced">
                {createAdvancedFields.map((field) => (
                  <TemplateCreateInput
                    field={field}
                    key={field.name}
                    onChange={(name, value) => {
                      setCreateValidation((current) => clearTemplateCreateFieldValidation(current, name));
                      onCreateValueChange(name, value);
                    }}
                    previewValue={createPreviewValues[field.name] ?? field.defaultValue}
                    referenceItems={referenceItems}
                    validationIssue={createValidation.fields[field.name]}
                    value={createValues[field.name] ?? ""}
                    t={t}
                  />
                ))}
              </div>
            ) : null}
            {createError ? <p className="module-create-error">{createError}</p> : null}
            <div className="module-dialog-actions">
              <button className="toolbar-button subtle" onClick={closeCreateDialog} type="button">
                {t("workspace.module.editor.cancel")}
              </button>
              <button className="toolbar-button primary" disabled={createBusy || catalogPreparing} type="submit">
                <Plus aria-hidden="true" size={14} />
                {t("workspace.module.editor.new")}
              </button>
            </div>
          </form>
        </div>
      ) : null}

      {actionDialog === "remove" ? (
        <div className="module-action-backdrop" role="presentation">
          <div aria-labelledby="module-remove-title" aria-modal="true" className="module-action-dialog" role="dialog">
            <div className="module-dialog-heading">
              <span>
                <small>{t("workspace.module.editor.entities")}</small>
                <h3 id="module-remove-title">{t("workspace.module.editor.remove")}</h3>
              </span>
              <button aria-label={t("workspace.module.editor.cancel")} className="toolbar-button icon-only" onClick={() => setActionDialog(null)} title={t("workspace.module.editor.cancel")} type="button">
                <X aria-hidden="true" size={14} />
              </button>
            </div>
            <p>
              {selectedIds.size > 0
                ? t("workspace.module.editor.removeSelectionConfirm", {
                    count: String(removeCount),
                  })
                : t("workspace.module.editor.removeCurrentConfirm", {
                    title: removalTargets[0]?.title ?? "",
                  })}
            </p>
            {persistedRemovalCount > 0 ? <p role="alert">{t("workspace.module.editor.removePermanentWarning")}</p> : null}
            {removalTargets.length > 0 ? (
              <ul className="module-remove-targets">
                {removalTargets.slice(0, 4).map((entity) => (
                  <li key={moduleEntityRenderKey(entity)}>
                    <strong>{entity.title}</strong>
                    <small>{entity.subtitle}</small>
                    {entity.root ? (
                      <small title={entity.root}>
                        {t("workspace.module.editor.removeTargetDetail", {
                          count: String(entity.sourceCount),
                          root: entity.root,
                        })}
                      </small>
                    ) : null}
                  </li>
                ))}
                {removalTargets.length > 4 ? (
                  <li>
                    <strong>
                      {t("workspace.module.editor.removeMoreTargets", {
                        count: String(removalTargets.length - 4),
                      })}
                    </strong>
                  </li>
                ) : null}
              </ul>
            ) : null}
            {selectedIds.size > 0 && selection.hiddenSelectedCount > 0 ? (
              <small className="module-remove-note">
                {t("workspace.module.editor.hiddenSelectionNote", {
                  count: String(selection.hiddenSelectedCount),
                })}
              </small>
            ) : null}
            <div className="module-dialog-actions">
              <button className="toolbar-button subtle" onClick={() => setActionDialog(null)} type="button">
                {t("workspace.module.editor.cancel")}
              </button>
              <button
                className="toolbar-button danger"
                onClick={() => {
                  onRemoveSelected();
                  setActionDialog(null);
                }}
                type="button"
              >
                <Trash2 aria-hidden="true" size={14} />
                {t("workspace.module.editor.removeConfirmAction")}
              </button>
            </div>
          </div>
        </div>
      ) : null}

      <div className="module-entity-scroll">
        {createUnavailableReason ? (
          <p className="module-create-unavailable" id={createUnavailableId} role="status">
            {createUnavailableReason}
          </p>
        ) : null}
        {catalogMissing ? (
          <div aria-busy={catalogPreparing} className="module-catalog-recovery">
            <div className="module-catalog-recovery-heading">
              <Database aria-hidden="true" size={20} />
              <span aria-live="polite">
                <strong>{t("workspace.module.editor.catalogMissingTitle")}</strong>
                <small id={`${entityListId}-catalog-recovery`}>{t("workspace.module.editor.catalogMissingDetail")}</small>
              </span>
            </div>
            <p>{t("workspace.module.editor.catalogPrepareWarning")}</p>
            {loadError ? (
              <small className="module-catalog-recovery-error" role="alert">
                {loadError}
              </small>
            ) : null}
            <button className="toolbar-button" disabled={catalogPreparing || !onPrepareCatalog} onClick={() => void onPrepareCatalog?.()} type="button">
              <RefreshCw aria-hidden="true" className={catalogPreparing ? "module-catalog-recovery-spinner" : undefined} size={14} />
              {t(catalogPreparing ? "workspace.module.editor.catalogPreparing" : "workspace.module.editor.catalogPrepare")}
            </button>
            {catalogPreparing ? (
              <span className="module-catalog-recovery-status" role="status">
                {t("workspace.module.editor.catalogPreparing")}
              </span>
            ) : null}
          </div>
        ) : null}
        {!catalogMissing || entities.length > 0 ? (
          <>
            <div aria-busy={loading} className="module-entity-results" id={entityListId}>
              {entities.length > 0 ? (
                <ul aria-label={t("workspace.module.editor.entities")} className="module-entity-options">
                  {renderedEntities.map((entity) => {
                    const checked = selectedIds.has(entity.id);
                    const rowClasses = ["module-entity-row", entity.id === selectedId ? "selected" : "", checked ? "checked" : ""].filter(Boolean).join(" ");
                    return (
                      <li aria-busy={hydratingEntityId === entity.id} className={rowClasses} key={moduleEntityRenderKey(entity)}>
                        <button
                          aria-current={entity.id === selectedId ? "true" : undefined}
                          className="module-entity-activate"
                          onClick={() => {
                            selectionAnchorRef.current = entity.id;
                            onSelect(entity.id);
                          }}
                          type="button"
                        >
                          <ModuleEntityThumbnail entity={entity} projectRoot={projectRoot} />
                          <span className="module-entity-main">
                            <span>
                              <strong>{entity.title}</strong>
                              <small>{entity.subtitle}</small>
                            </span>
                            {entity.tags.length > 0 ? (
                              <span className="module-tag-row">
                                {entity.tags.slice(0, 5).map((tag) => (
                                  <code className={`module-tag ${tag.tone}`} key={`${entity.id}:${tag.label}`}>
                                    {tag.label}
                                  </code>
                                ))}
                              </span>
                            ) : null}
                          </span>
                        </button>
                        <label
                          className="module-entity-check"
                          title={t("workspace.module.editor.selectEntity", {
                            title: entity.title,
                          })}
                        >
                          <input
                            aria-label={t("workspace.module.editor.selectEntity", { title: entity.title })}
                            checked={checked}
                            onChange={(event) => {
                              const nativeEvent = event.nativeEvent as MouseEvent | KeyboardEvent;
                              if ("shiftKey" in nativeEvent && nativeEvent.shiftKey) {
                                selectRange(entity.id, event.target.checked ? "select" : "deselect");
                              } else {
                                selectSingle(entity.id, event.target.checked);
                              }
                            }}
                            type="checkbox"
                          />
                          <span className="module-entity-check-box">{checked ? <Check aria-hidden="true" size={13} /> : null}</span>
                        </label>
                        {entity.draftState !== "clean" ? <span className={`draft-dot ${entity.draftState}${entity.sourceConflict ? " conflict" : ""}`} title={t(entity.sourceConflict ? (entity.sourceConflict === "missing" ? "workspace.module.editor.sourceMissingStatus" : "workspace.module.editor.sourceChangedStatus") : draftKey[entity.draftState])} /> : null}
                      </li>
                    );
                  })}
                </ul>
              ) : (
                <p aria-live="polite" className="module-list-empty">
                  {emptyMessage}
                </p>
              )}
            </div>
            {showDirectFooter ? (
              <div className="module-catalog-footer">
                <span aria-live="polite" role="status">
                  {directResultSummary}
                </span>
                <button
                  aria-controls={entityListId}
                  className="toolbar-button subtle"
                  onClick={() =>
                    setDirectDisclosure({
                      limit: directBaseCount + DIRECT_RESULT_BATCH_SIZE,
                      scope: directDisclosureScope,
                    })
                  }
                  type="button"
                >
                  {t("workspace.module.editor.directShowMore")}
                </button>
              </div>
            ) : null}
            {showPagingFooter ? (
              <div className="module-catalog-footer">
                <span aria-live="polite" role="status">
                  {pagingSummary}
                  {loading ? ` · ${t("workspace.module.editor.catalogLoading")}` : ""}
                </span>
                {loadError ? <small role="alert">{loadError}</small> : null}
                {!loading && (loadError ? onRetryLoad : hasMore ? onLoadMore : null) ? (
                  <button aria-controls={entityListId} className="toolbar-button subtle" onClick={() => (loadError ? onRetryLoad?.() : void onLoadMore?.())} type="button">
                    {loadError ? t("workspace.module.editor.catalogRetry") : t("workspace.module.editor.catalogLoadMore")}
                  </button>
                ) : null}
              </div>
            ) : null}
          </>
        ) : null}
      </div>
    </aside>
  );
}

function moduleEntityRenderKey(entity: Pick<ModuleEntity, "id" | "root" | "sourceRoot">): string {
  return `${entity.id}\u0000${entity.sourceRoot ?? ""}\u0000${entity.root}`;
}

function ModuleCreateAiHandoff({ intent, t }: { intent: ModuleCreateIntent["ai"] | null; t: Translator }) {
  if (!intent) {
    return null;
  }
  return (
    <div className="module-create-ai-handoff" data-paradev-ai-operation-id={intent.operationId} data-paradev-ai-operation-passive="true">
      <span>
        <strong>
          {t("workspace.module.editor.aiHandoff.title", {
            operation: intent.operationId,
          })}
        </strong>
        <small>{t("workspace.module.editor.aiHandoff.moduleDraft.detail")}</small>
      </span>
      <div className="module-create-ai-handoff-meta">
        <code>
          {t("workspace.module.editor.aiHandoff.role", {
            role: intent.role || t("chat.route.default"),
          })}
        </code>
        <code>
          {t("workspace.module.editor.aiHandoff.context", {
            sources: moduleCreateIntentSourceSummary(intent, t),
          })}
        </code>
      </div>
    </div>
  );
}

function moduleCreateIntentSourceSummary(intent: NonNullable<ModuleCreateIntent["ai"]>, t: Translator): string {
  if (intent.sources.length === 0) {
    return t("chat.context.none");
  }
  const labels = intent.sources.slice(0, 3).map((source) => source.label || source.relativePath || source.sourcePath || source.path || source.familyId || source.kind);
  const suffix = intent.sources.length > labels.length ? ` +${intent.sources.length - labels.length}` : "";
  return `${labels.join(", ")}${suffix}`;
}

type TemplateCreateValidationIssue = "boolean" | "choice" | "number" | "required";

type TemplateCreateValidation = {
  objectId: boolean;
  fields: Record<string, TemplateCreateValidationIssue>;
};

export function validateTemplateCreateForm(objectId: string, objectIdPreview: string, fields: TemplateCreateField[], values: Record<string, string>, previewValues: Record<string, string>): TemplateCreateValidation {
  const issues: Record<string, TemplateCreateValidationIssue> = {};
  for (const field of fields) {
    const value = resolvedTemplateCreateValue(field, values, previewValues);
    if (!value) {
      if (field.required) {
        issues[field.name] = "required";
      }
      continue;
    }
    if (field.type === "number" && !Number.isFinite(Number(value))) {
      issues[field.name] = "number";
    } else if ((field.type === "choice" || field.choices.length > 0) && !field.choices.includes(value)) {
      issues[field.name] = "choice";
    } else if (field.type === "boolean" && !["false", "true"].includes(value.toLowerCase())) {
      issues[field.name] = "boolean";
    }
  }
  return {
    objectId: !(objectId.trim() || objectIdPreview.trim()),
    fields: issues,
  };
}

function TemplateCreateInput({ field, previewValue, referenceItems, validationIssue, value, onChange, t }: { field: TemplateCreateField; previewValue: string; referenceItems: readonly ProjectBrowserItem[]; validationIssue?: TemplateCreateValidationIssue; value: string; onChange: (name: string, value: string) => void; t: Translator }) {
  const inputId = useId();
  const referenceOptions = templateCreateReferenceOptions(field, referenceItems);
  const referenceListId = referenceOptions.length > 0 ? `${inputId}-reference` : undefined;
  const descriptionId = `${inputId}-description`;
  const errorId = `${inputId}-error`;
  const fieldLabel = field.required ? `${field.label} *` : field.label;
  const describedBy = [field.description ? descriptionId : "", validationIssue ? errorId : ""].filter(Boolean).join(" ") || undefined;
  const commonProps = {
    "aria-describedby": describedBy,
    "aria-invalid": Boolean(validationIssue) || undefined,
    "aria-label": field.label,
    "aria-required": field.required || undefined,
    id: inputId,
    name: field.name,
    title: field.description || undefined,
  };
  const resolvedValue = value.trim() || previewValue.trim() || field.defaultValue.trim();
  const fieldType = field.choices.length > 0 ? "choice" : field.type;
  const control =
    fieldType === "text" ? (
      <textarea {...commonProps} onChange={(event) => onChange(field.name, event.target.value)} placeholder={previewValue || field.label} rows={3} value={value} />
    ) : fieldType === "choice" ? (
      <select {...commonProps} disabled={field.choices.length === 0} onChange={(event) => onChange(field.name, event.target.value)} value={field.choices.includes(resolvedValue) ? resolvedValue : ""}>
        {!field.choices.includes(resolvedValue) ? (
          <option value="">
            {t("workspace.module.editor.create.choicePlaceholder", {
              field: field.label,
            })}
          </option>
        ) : null}
        {field.choices.map((choice) => (
          <option key={choice} value={choice}>
            {choice}
          </option>
        ))}
      </select>
    ) : fieldType === "boolean" ? (
      <span className="module-create-checkbox">
        <input {...commonProps} checked={resolvedValue.toLowerCase() === "true"} onChange={(event) => onChange(field.name, String(event.target.checked))} type="checkbox" />
        <span>{fieldLabel}</span>
      </span>
    ) : (
      <input {...commonProps} autoComplete="off" data-template-field-type={fieldType} inputMode={fieldType === "number" ? "decimal" : undefined} list={referenceListId} onChange={(event) => onChange(field.name, event.target.value)} placeholder={previewValue || (fieldType === "asset" ? t("workspace.module.editor.create.assetPlaceholder") : field.label)} spellCheck={fieldType === "asset" ? false : undefined} step={fieldType === "number" ? "any" : undefined} type={fieldType === "number" ? "number" : "text"} value={value} />
    );
  return (
    <label className="module-create-field">
      {fieldType === "boolean" ? null : <small>{fieldLabel}</small>}
      {field.description ? (
        <span className="module-create-field-description" id={descriptionId}>
          {field.description}
        </span>
      ) : null}
      {control}
      {referenceListId ? (
        <datalist id={referenceListId}>
          {referenceOptions.map((option) => (
            <option key={option.value} label={option.label} value={option.value} />
          ))}
        </datalist>
      ) : null}
      {validationIssue ? (
        <span className="module-create-field-error" id={errorId} role="alert">
          {templateCreateValidationMessage(validationIssue, field.label, t)}
        </span>
      ) : null}
    </label>
  );
}

function emptyTemplateCreateValidation(): TemplateCreateValidation {
  return { objectId: false, fields: {} };
}

function clearTemplateCreateFieldValidation(validation: TemplateCreateValidation, fieldName: string): TemplateCreateValidation {
  if (!validation.fields[fieldName]) {
    return validation;
  }
  const fields = { ...validation.fields };
  delete fields[fieldName];
  return { ...validation, fields };
}

function resolvedTemplateCreateValue(field: TemplateCreateField, values: Record<string, string>, previewValues: Record<string, string>): string {
  return values[field.name]?.trim() || previewValues[field.name]?.trim() || field.defaultValue.trim();
}

function templateCreateValidationMessage(issue: TemplateCreateValidationIssue, field: string, t: Translator): string {
  return t(`workspace.module.editor.create.validation.${issue}`, { field });
}
