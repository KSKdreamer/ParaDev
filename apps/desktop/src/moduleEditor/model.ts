import type {
  DraftApplyPayload,
  ModuleScaffoldFile,
  ModuleScaffoldPlan,
  ProjectBrowserItem,
  ProjectBrowserPayload,
  ProjectBrowserResourceSlot,
  ProjectBrowserSource,
  ProjectTemplate,
  ProjectTemplateArgReference,
  ProjectTemplatesPayload,
  SourceFormScalar,
  SourceFormUpdateBatchPlan,
  SourceFormUpdateRequest,
  SourceReplacement,
  SourceReplacementTargetFormat,
  SourceTextEdit,
} from "../types";
import { templateScalarText } from "../templateValues";
import type { Locale } from "../i18n";
import { canonicalFamilyId } from "../projectModules";

export type ModuleDraftState = "clean" | "modified" | "new" | "remove";

export type ModuleSortOrder = "title" | "id" | "sourceCount" | "draftState";

export type ModuleEntityTag = {
  label: string;
  tone: "layout" | "source" | "metadata" | "draft";
};

export type ModuleSourceSlot = ProjectBrowserSource & {
  draftKey: string;
  editorKind: "code" | "localization" | "image" | "asset";
};

export type ModuleSourceRevision = {
  sourceKey: string;
  path: string;
  relativePath: string;
  size: number;
  mtimeNs: string;
};

export type ModuleEntityDrafts = {
  text: Record<string, string>;
  /** Registry control intent awaiting an SDK-owned source-form update plan. */
  sourceForms?: Record<string, ModuleSourceFormDraft>;
  assets?: ModuleAssetDraft[];
  info?: {
    objectId?: string;
    title?: string;
  };
  create?: {
    templateId: string;
    values: Record<string, string>;
    advancedFields: string[];
  };
  image?: {
    fileName: string;
    sourceKey?: string;
    path?: string;
    expectedAbsent?: true;
    previewUrl: string;
    contentBase64?: string;
    width?: number;
    height?: number;
    crop?: {
      x: number;
      y: number;
      width: number;
      height: number;
    };
  };
};

export type ModuleSourceFormDraft = {
  baseText: string;
  baseWasDraft: boolean;
  values: Record<string, SourceFormScalar>;
};

export type GuidedTextDraftChange = {
  baseText: string;
  controlId: string;
  text: string;
  value: SourceFormScalar;
};

export type ModuleSourceFormUpdate = SourceFormUpdateRequest & {
  sourceKey: string;
};

export type SourceFormPlanMergeResult =
  | { ok: true; sourceEdits: SourceTextEdit[] }
  | {
      ok: false;
      reason:
        | "missing-plan"
        | "unexpected-plan"
        | "text-mismatch"
        | "revision-missing";
    };

export type ModuleAssetDraft = {
  contentBase64: string;
  fileName: string;
  path: string;
  size: number;
  slotName?: string;
  sourceKey?: string;
};

export type ModuleAssetDraftTarget = {
  modulePath: string;
  path: string;
  slotName: string;
};

export type ModuleEntity = {
  id: string;
  kind?: ProjectBrowserItem["kind"];
  familyId: string;
  family: string;
  moduleId?: string;
  collectionId?: string;
  objectId: string;
  title: string;
  titleKeys?: string[];
  subtitle: string;
  root: string;
  relativeRoot: string;
  sourceRoot?: string;
  layout: "canonical" | "family_root";
  sourceCount: number;
  sourceSlots: ModuleSourceSlot[];
  resourceSlots?: ProjectBrowserResourceSlot[];
  metadata?: Record<string, unknown>;
  active?: boolean;
  previewSource?: ModuleSourceSlot;
  tags: ModuleEntityTag[];
  /** Revisions captured when an existing source row first becomes dirty. */
  draftSourceRevisions?: ModuleSourceRevision[];
  /** Local draft no longer matches the latest authoritative project sources. */
  sourceConflict?: "missing" | "changed";
  draftState: ModuleDraftState;
  drafts: ModuleEntityDrafts;
};

export type ModuleEntityMergeOptions = {
  /**
   * Full project-browser rows used to prove source revisions and true absence.
   *
   * A paged or searched Catalog result must omit this option rather than
   * treating rows outside the current subset as deleted.
   */
  authoritativeEntities?: readonly ModuleEntity[];
};

export type ModuleEntityQuery = {
  query: string;
  sort: ModuleSortOrder;
};

export type ModuleEntitySelectionMode = "replace" | "add" | "toggle";

export type ModuleEntityRangeAction = "select" | "deselect";

export type ModuleEntitySelectionState = {
  allSelected: boolean;
  allVisibleSelected: boolean;
  hasFilteredScope: boolean;
  hiddenSelectedCount: number;
  selectedCount: number;
  someVisibleSelected: boolean;
  totalCount: number;
  visibleCount: number;
  visibleSelectedCount: number;
};

const IMAGE_REPLACEMENT_TARGET_FORMATS: ReadonlySet<SourceReplacementTargetFormat> =
  new Set(["dds", "tga", "jpg", "jpeg", "webp", "bmp"]);
const IMAGE_EDITOR_PREVIEW_FORMATS = new Set([
  "png",
  "jpg",
  "jpeg",
  "webp",
  "bmp",
]);
const BROWSER_THUMBNAIL_FORMATS = new Set([
  "png",
  "jpg",
  "jpeg",
  "webp",
  "gif",
  "bmp",
  "svg",
]);

export type TemplateCreateField = {
  name: string;
  label: string;
  description: string;
  descriptionSource?: "declared" | "generated" | string;
  required: boolean;
  defaultValue: string;
  advanced: boolean;
  type: string;
  choices: string[];
  reference?: ProjectTemplateArgReference;
};

export type TemplateCreateReferenceOption = {
  label: string;
  value: string;
};

export type TemplateCreateFields = {
  primary: TemplateCreateField[];
  advanced: TemplateCreateField[];
};

export type CreateDraftInput = {
  objectId: string;
  title: string;
  values: Record<string, string>;
  advancedFields: string[];
};

export type ModuleLocalizationTextSource = {
  slot: string;
  language?: string;
  text: string;
};

export type ModuleLocalizationCell = {
  slot: string;
  text: string;
};

export type ModuleLocalizationRow = {
  key: string;
  values: Record<string, ModuleLocalizationCell>;
};

export type ModuleLocalizationTable = {
  languages: string[];
  rows: ModuleLocalizationRow[];
};

type ModuleEntityDisplayRule = {
  title: "resolvedTitle" | "objectId";
  subtitle: "objectId" | "itemId";
};

const IMAGE_EXTENSIONS = new Set([
  "bmp",
  "dds",
  "jpg",
  "jpeg",
  "png",
  "tga",
  "webp",
]);
const CODE_EXTENSIONS = new Set([
  "asset",
  "csv",
  "fnt",
  "gfx",
  "gui",
  "json",
  "lua",
  "pdx",
  "txt",
  "xml",
]);
const THUMBNAIL_CACHE_VERSION = "v1";
const DEFAULT_ENTITY_DISPLAY_RULE: ModuleEntityDisplayRule = {
  title: "resolvedTitle",
  subtitle: "objectId",
};
const ENTITY_DISPLAY_RULE_BY_FAMILY: Record<string, ModuleEntityDisplayRule> =
  {};
const DRAFT_STATE_ORDER: Record<ModuleDraftState, number> = {
  new: 0,
  modified: 1,
  remove: 2,
  clean: 3,
};
const SOURCE_FOCUS_COLLECTION_KEYS = ["source_focuses", "sourceFocuses"];
const SOURCE_FOCUS_ID_KEYS = [
  "id",
  "focus_id",
  "focusId",
  "object_id",
  "objectId",
];

export function buildModuleEntities(
  browser: ProjectBrowserPayload,
  familyId: string,
  locale: Locale = "en",
): ModuleEntity[] {
  return browser.items
    .filter(
      (item) =>
        canonicalFamilyId(item.family_id, item.family) ===
        canonicalFamilyId(familyId),
    )
    .sort((left, right) => compareBrowserItemsForDisplay(left, right, locale))
    .map((item) => {
      const sourceSlots = sourceSlotsForItem(item);
      const display = moduleEntityDisplay(item, locale);
      const active = item.active ?? item.metadata?.inactive !== true;
      return {
        id: item.id,
        kind: item.kind,
        familyId: item.family_id,
        family: item.family,
        moduleId: moduleIdForItem(item),
        collectionId: item.collection_id,
        objectId: item.object_id,
        title: display.title,
        titleKeys: [...(item.title_keys ?? [])],
        subtitle: display.subtitle,
        root: item.root,
        relativeRoot: item.relative_root,
        sourceRoot: item.source_root,
        layout: item.layout,
        sourceCount: item.source_count,
        sourceSlots,
        resourceSlots: [...(item.resource_slots ?? [])],
        metadata: item.metadata,
        active,
        previewSource: previewSourceForItem(item),
        tags: buildTags(active),
        draftState: "clean",
        drafts: { text: {} },
      };
    });
}

export function mergeModuleEntitiesPreservingDrafts(
  current: readonly ModuleEntity[],
  incoming: readonly ModuleEntity[],
  options: ModuleEntityMergeOptions = {},
): ModuleEntity[] {
  const currentById = new Map(current.map((entity) => [entity.id, entity]));
  const incomingIds = new Set(incoming.map((entity) => entity.id));
  const authoritativeById =
    options.authoritativeEntities === undefined
      ? null
      : new Map(
          options.authoritativeEntities.map((entity) => [entity.id, entity]),
        );
  const refreshed = incoming.map((entity) => {
    const existing = currentById.get(entity.id);
    const authoritative = authoritativeById?.get(entity.id);
    const refreshedEntity = authoritative
      ? entityWithAuthoritativeSources(entity, authoritative)
      : entity;
    if (!existing || existing.draftState === "clean") {
      return refreshedEntity;
    }
    return mergeDirtyModuleEntity(existing, refreshedEntity);
  });
  const retainedDrafts = current
    .filter(
      (entity) => entity.draftState !== "clean" && !incomingIds.has(entity.id),
    )
    .map((entity) => {
      if (entity.draftState === "new") {
        return entity;
      }
      const authoritative = authoritativeById?.get(entity.id);
      if (authoritative) {
        return mergeDirtyModuleEntity(entity, authoritative);
      }
      if (authoritativeById) {
        return { ...entity, sourceConflict: "missing" as const };
      }
      return entity;
    });
  return [...refreshed, ...retainedDrafts];
}

function entityWithAuthoritativeSources(
  entity: ModuleEntity,
  authoritative: ModuleEntity,
): ModuleEntity {
  return {
    ...entity,
    sourceCount: authoritative.sourceCount,
    sourceSlots: authoritative.sourceSlots,
    resourceSlots: authoritative.resourceSlots,
    previewSource: authoritative.previewSource ?? entity.previewSource,
  };
}

function mergeDirtyModuleEntity(
  existing: ModuleEntity,
  incoming: ModuleEntity,
): ModuleEntity {
  const draftSourceRevisions =
    existing.draftSourceRevisions ?? sourceRevisionsForEntity(existing);
  const sourceConflict =
    sourceRevisionsChanged(
      draftSourceRevisions,
      incoming,
      existing.sourceConflict,
      existing.draftState === "remove",
    ) || expectedAbsentImageTargetAppeared(existing, incoming)
      ? ("changed" as const)
      : undefined;
  return {
    ...incoming,
    ...(draftSourceRevisions.length > 0 ? { draftSourceRevisions } : {}),
    ...(sourceConflict ? { sourceConflict } : {}),
    draftState: existing.draftState,
    drafts: existing.drafts,
  };
}

function expectedAbsentImageTargetAppeared(
  existing: ModuleEntity,
  incoming: ModuleEntity,
): boolean {
  const draft = existing.drafts.image;
  if (!draft?.expectedAbsent || !draft.path) {
    return false;
  }
  const target = moduleSourcePathIdentity(draft.path);
  return incoming.sourceSlots.some(
    (source) =>
      source.exists !== false &&
      [source.path, source.relative_path].some(
        (path) => path && moduleSourcePathIdentity(path) === target,
      ),
  );
}

function sourceRevisionsChanged(
  baseline: readonly ModuleSourceRevision[],
  incoming: ModuleEntity,
  existingConflict: ModuleEntity["sourceConflict"],
  removalDraft: boolean,
): boolean {
  if (baseline.length === 0) {
    return false;
  }
  const current = sourceRevisionsForEntity(incoming);
  if (current.length === 0) {
    return existingConflict === "changed";
  }
  const currentByPath = new Map(
    current.map((revision) => [
      moduleSourcePathIdentity(revision.path || revision.relativePath),
      revision,
    ]),
  );
  if (
    baseline.some((revision) => {
      const currentRevision = currentByPath.get(
        moduleSourcePathIdentity(revision.path || revision.relativePath),
      );
      return (
        !currentRevision ||
        currentRevision.size !== revision.size ||
        currentRevision.mtimeNs !== revision.mtimeNs
      );
    })
  ) {
    return true;
  }
  return removalDraft && current.length !== baseline.length;
}

function sourceRevisionsForEntity(
  entity: Pick<ModuleEntity, "sourceSlots">,
): ModuleSourceRevision[] {
  const revisions = new Map<string, ModuleSourceRevision>();
  for (const source of entity.sourceSlots) {
    const path = source.path.trim();
    const relativePath = source.relative_path.trim();
    if (
      (!path && !relativePath) ||
      source.size === undefined ||
      source.mtime_ns === undefined
    ) {
      continue;
    }
    const revision = {
      sourceKey: source.draftKey,
      path,
      relativePath,
      size: source.size,
      mtimeNs: source.mtime_ns,
    };
    revisions.set(moduleSourcePathIdentity(path || relativePath), revision);
  }
  return [...revisions.values()].sort((left, right) =>
    moduleSourcePathIdentity(left.path || left.relativePath).localeCompare(
      moduleSourcePathIdentity(right.path || right.relativePath),
    ),
  );
}

export function filterAndSortEntities(
  entities: ModuleEntity[],
  query: ModuleEntityQuery,
): ModuleEntity[] {
  const normalizedQuery = normalize(query.query);
  const filtered = normalizedQuery
    ? entities.filter((entity) =>
        searchableText(entity).includes(normalizedQuery),
      )
    : entities;

  return [...filtered].sort((left, right) =>
    compareEntities(left, right, query.sort),
  );
}

export function resolveModuleEntitySelection(
  currentId: string,
  entities: Pick<ModuleEntity, "id">[],
  visibleEntities: Pick<ModuleEntity, "id">[],
): string {
  if (entities.length === 0) {
    return "";
  }
  if (currentId && entities.some((entity) => entity.id === currentId)) {
    return currentId;
  }
  return visibleEntities[0]?.id ?? entities[0].id;
}

export function resolveModuleEntityQueryAfterExternalSelection(
  query: string,
  selectedId: string,
  visibleEntities: Pick<ModuleEntity, "id">[],
): string {
  if (!query.trim() || !selectedId) {
    return query;
  }
  return visibleEntities.some((entity) => entity.id === selectedId)
    ? query
    : "";
}

export function moduleEntityThumbnailSource(
  entity: ModuleEntity,
): ModuleSourceSlot | null {
  const explicitPreview = sourceWithThumbnailPath(entity.previewSource);
  const imageSources = entity.sourceSlots.filter(
    (source) =>
      sourceWithThumbnailPath(source) &&
      (source.editorKind === "image" ||
        BROWSER_THUMBNAIL_FORMATS.has(imageSourceFormat(source))),
  );
  return (
    [explicitPreview, ...imageSources].find(isBrowserThumbnailSource) ??
    explicitPreview ??
    imageSources[0] ??
    null
  );
}

function sourceWithThumbnailPath(
  source: ModuleSourceSlot | undefined,
): ModuleSourceSlot | null {
  return source &&
    source.exists !== false &&
    (source.path || source.relative_path)
    ? source
    : null;
}

function isBrowserThumbnailSource(
  source: ModuleSourceSlot | null,
): source is ModuleSourceSlot {
  return Boolean(
    source && BROWSER_THUMBNAIL_FORMATS.has(imageSourceFormat(source)),
  );
}

export function moduleEntityThumbnailCacheKey(
  entity: ModuleEntity,
  source: ModuleSourceSlot | null,
  sideLength: number,
): string {
  if (!source) {
    return "";
  }
  return [
    THUMBNAIL_CACHE_VERSION,
    String(sideLength),
    entity.id,
    source.relative_path || source.path || source.name,
    source.size === undefined ? "" : String(source.size),
    source.mtime_ns ?? "",
  ].join("|");
}

export function selectCreateTemplates(
  templates: ProjectTemplatesPayload | null,
  family: string,
): ProjectTemplate[] {
  const matches =
    templates?.templates.filter(
      (template) =>
        (template.kind ?? "module") === "module" &&
        template.authoring_ready !== false &&
        templateMatchesFamily(template, family),
    ) ?? [];
  if (matches.length === 0) {
    return [];
  }
  const projectMatches = matches.filter(
    (template) => template.source === "project",
  );
  const otherMatches = matches.filter(
    (template) => template.source !== "project",
  );
  return projectMatches.length > 0
    ? [...projectMatches, ...otherMatches]
    : matches;
}

export function selectCollectionCreateTemplates(
  templates: ProjectTemplatesPayload | null,
  family: string,
): ProjectTemplate[] {
  const matches =
    templates?.templates.filter(
      (template) =>
        template.kind === "collection" &&
        template.authoring_ready !== false &&
        templateMatchesFamily(template, family),
    ) ?? [];
  const projectMatches = matches.filter(
    (template) => template.source === "project",
  );
  const otherMatches = matches.filter(
    (template) => template.source !== "project",
  );
  return projectMatches.length > 0
    ? [...projectMatches, ...otherMatches]
    : matches;
}

export function selectCreateTemplate(
  templates: ProjectTemplatesPayload | null,
  family: string,
  templateId = "",
): ProjectTemplate | null {
  const candidates = selectCreateTemplates(templates, family);
  if (candidates.length === 0) {
    return null;
  }
  if (templateId) {
    return (
      candidates.find((template) => template.id === templateId) ?? candidates[0]
    );
  }
  return candidates[0];
}

export function buildTemplateCreateFields(
  template: ProjectTemplate | null,
): TemplateCreateFields {
  const formFields = template?.form?.fields ?? [];
  const sourceFields =
    formFields.length > 0
      ? formFields
      : Object.entries(template?.args ?? {}).map(([name, arg]) => ({
          name,
          target: "values",
          label: arg.label || humanizeCreateFieldName(name),
          ...arg,
        }));
  const fields = sourceFields.map<TemplateCreateField>((field) => ({
    name: field.name,
    label: field.label || humanizeCreateFieldName(field.name),
    description: field.description ?? "",
    descriptionSource: field.description_source ?? "generated",
    required: field.required,
    defaultValue: templateScalarText(field.default),
    advanced: field.advanced,
    type: field.type ?? "string",
    choices: (field.choices ?? []).map(templateScalarText),
    reference: field.reference,
  }));
  return {
    primary: fields.filter((field) => !field.advanced),
    advanced: fields.filter((field) => field.advanced),
  };
}

/** Resolve extension-declared references from the already loaded project browser. */
export function templateCreateReferenceOptions(
  field: TemplateCreateField,
  items: readonly ProjectBrowserItem[],
): TemplateCreateReferenceOption[] {
  if (!field.reference) {
    return [];
  }
  const family = canonicalFamilyId(field.reference.family);
  const options = new Map<string, string>();
  for (const item of items) {
    if (
      item.kind !== field.reference.kind ||
      canonicalFamilyId(item.family, item.family_id) !== family
    ) {
      continue;
    }
    const value =
      item.kind === "collection"
        ? (item.collection_id ?? item.object_id)
        : item.object_id;
    if (!value) {
      continue;
    }
    const title = item.title.trim();
    options.set(value, title && title !== value ? `${title} — ${value}` : value);
  }
  return [...options]
    .map(([value, label]) => ({ label, value }))
    .sort(
      (left, right) =>
        left.label.localeCompare(right.label) ||
        left.value.localeCompare(right.value),
    );
}

function humanizeCreateFieldName(name: string): string {
  const words = name.trim().replace(/[_-]+/g, " ");
  if (!words) {
    return name;
  }
  return words.charAt(0).toUpperCase() + words.slice(1);
}

function moduleEntityDisplay(
  item: ProjectBrowserItem,
  locale: Locale,
): Pick<ModuleEntity, "title" | "subtitle"> {
  const rule =
    ENTITY_DISPLAY_RULE_BY_FAMILY[
      canonicalFamilyId(item.family_id, item.family)
    ] ?? DEFAULT_ENTITY_DISPLAY_RULE;
  const localizedTitle = localizedEntityTitle(item, locale);
  return {
    title:
      rule.title === "resolvedTitle"
        ? (localizedTitle ?? (cleanDisplayText(item.title) || item.object_id))
        : item.object_id,
    subtitle: rule.subtitle === "objectId" ? item.object_id : item.id,
  };
}

function localizedEntityTitle(
  item: ProjectBrowserItem,
  locale: Locale,
): string | null {
  const titles = item.localized_titles;
  if (!titles) {
    return null;
  }
  const selectedLanguage = normalizeLocalizationLanguage(locale);
  return (
    cleanDisplayText(titles[selectedLanguage] ?? "") ||
    cleanDisplayText(titles.l_english ?? "") ||
    item.object_id
  );
}

export function buildCreateDraftInput(
  template: ProjectTemplate | null,
  objectIdValue: string,
  values: Record<string, string>,
  fallbackTitle = "New object",
  fallbackObjectId = "",
): CreateDraftInput {
  const objectId = sanitizeIdentifier(objectIdValue || fallbackObjectId);
  const templateFields = buildTemplateCreateFields(template);
  const context = {
    object_id: objectId,
    family: template?.family ?? "object",
    family_tag: familyTag(objectId, template?.family ?? "object"),
    title:
      normalizeCreateValue(values.title) || fallbackTitle.trim() || objectId,
  };
  const mergedValues: Record<string, string> = { object_id: objectId };

  for (const field of [...templateFields.primary, ...templateFields.advanced]) {
    const value = normalizeCreateValue(values[field.name]);
    mergedValues[field.name] =
      value || renderCreateDefault(field.defaultValue, context);
  }

  const title =
    normalizeCreateValue(mergedValues.title) ||
    fallbackTitle.trim() ||
    objectId;
  mergedValues.title = title;

  return {
    objectId,
    title,
    values: mergedValues,
    advancedFields: templateFields.advanced.map((field) => field.name),
  };
}

export function applyTextDraft(
  entity: ModuleEntity,
  sourceKey: string,
  value: string,
): ModuleEntity {
  if (entity.draftState === "new" || entity.draftState === "remove") {
    return entity;
  }
  const sourceForms = Object.fromEntries(
    Object.entries(entity.drafts.sourceForms ?? {}).filter(
      ([key]) => key !== sourceKey,
    ),
  );
  return retainDraftSourceRevisions(entity, {
    ...entity,
    draftState: "modified",
    drafts: {
      ...entity.drafts,
      text: {
        ...entity.drafts.text,
        [sourceKey]: value,
      },
      ...(Object.keys(sourceForms).length > 0
        ? { sourceForms }
        : { sourceForms: undefined }),
    },
  });
}

export function applyGuidedTextDraft(
  entity: ModuleEntity,
  sourceKey: string,
  change: GuidedTextDraftChange,
): ModuleEntity {
  if (entity.draftState === "new" || entity.draftState === "remove") {
    return entity;
  }
  const current = entity.drafts.sourceForms?.[sourceKey];
  const formDraft: ModuleSourceFormDraft = current
    ? {
        ...current,
        values: { ...current.values, [change.controlId]: change.value },
      }
    : {
        baseText: change.baseText,
        baseWasDraft: Object.prototype.hasOwnProperty.call(
          entity.drafts.text,
          sourceKey,
        ),
        values: { [change.controlId]: change.value },
      };
  const text = { ...entity.drafts.text };
  const sourceForms = { ...entity.drafts.sourceForms };
  if (change.text === formDraft.baseText) {
    delete sourceForms[sourceKey];
    if (formDraft.baseWasDraft) {
      text[sourceKey] = formDraft.baseText;
    } else {
      delete text[sourceKey];
    }
  } else {
    text[sourceKey] = change.text;
    sourceForms[sourceKey] = formDraft;
  }
  const drafts: ModuleEntityDrafts = {
    ...entity.drafts,
    text,
    ...(Object.keys(sourceForms).length > 0
      ? { sourceForms }
      : { sourceForms: undefined }),
  };
  return retainDraftSourceRevisions(entity, {
    ...entity,
    draftState: draftStateForDrafts(drafts),
    drafts,
  });
}

export function applyInfoDraft(
  entity: ModuleEntity,
  draft: NonNullable<ModuleEntityDrafts["info"]>,
): ModuleEntity {
  if (entity.draftState === "new" || entity.draftState === "remove") {
    return entity;
  }
  const info = normalizedInfoDraft(entity, draft);
  const { info: _discarded, ...draftsWithoutInfo } = entity.drafts;
  const drafts = info ? { ...entity.drafts, info } : draftsWithoutInfo;
  return retainDraftSourceRevisions(entity, {
    ...entity,
    draftState: draftStateForDrafts(drafts),
    drafts,
  });
}

export function applyImageDraft(
  entity: ModuleEntity,
  image: NonNullable<ModuleEntityDrafts["image"]>,
): ModuleEntity {
  if (entity.draftState === "new" || entity.draftState === "remove") {
    return entity;
  }
  const source = image.sourceKey
    ? entity.sourceSlots.find(
        (item) =>
          item.draftKey === image.sourceKey && item.editorKind === "image",
      )
    : entity.sourceSlots.find((item) => item.editorKind === "image");
  if (!source || !canReplaceImageSource(source)) {
    return entity;
  }
  const targetPath = image.path || defaultImageDraftPath(entity, source);
  if (!targetPath || !imageReplacementPathMatchesSource(targetPath, source)) {
    return entity;
  }
  const imageDraft =
    source.exists === false
      ? { ...image, expectedAbsent: true as const }
      : image;
  return retainDraftSourceRevisions(entity, {
    ...entity,
    draftState: "modified",
    drafts: {
      ...entity.drafts,
      image: imageDraft,
    },
  });
}

export function createDraftEntity(
  familyId: string,
  existing: ModuleEntity[],
  title = "New object",
  template: ProjectTemplate | null = null,
  createInput: CreateDraftInput | null = null,
): ModuleEntity {
  const generatedObjectId = nextDraftObjectId(familyId, existing, template);
  const objectId = createInput?.objectId || generatedObjectId;
  const draftTitle = title.trim() || objectId;
  const renderedTemplateFiles = template
    ? template.files.map((file) =>
        renderCreateDefault(file, {
          ...(createInput?.values ?? {}),
          family: template.family,
          family_tag: familyTag(objectId, template.family),
          object_id: objectId,
          title: draftTitle,
        }),
      )
    : [];
  const sourceSlots = template
    ? sourceSlotsWithDraftKeys(
        renderedTemplateFiles.map(sourceSlotFromTemplateFile),
        renderedTemplateFiles,
      )
    : defaultDraftSourceSlots();
  const sourceCount = sourceSlots.length;
  const familyPrototype = existing.find(
    (entity) =>
      canonicalFamilyId(entity.familyId, entity.family) ===
      canonicalFamilyId(familyId),
  );

  return {
    id: `${familyId}:${objectId}`,
    familyId,
    family: template?.family ?? familyId,
    objectId,
    title: draftTitle,
    titleKeys: [...(familyPrototype?.titleKeys ?? [])],
    subtitle: objectId,
    root: "",
    relativeRoot: "",
    layout: "canonical",
    sourceCount,
    sourceSlots,
    resourceSlots: familyPrototype?.resourceSlots,
    active: true,
    tags: buildTags(true),
    draftState: "new",
    drafts: {
      text: buildDraftText(sourceSlots),
      ...(template && createInput
        ? {
            create: {
              templateId: template.id,
              values: createInput.values,
              advancedFields: createInput.advancedFields,
            },
          }
        : {}),
    },
  };
}

export function canApplyScaffoldDraft(entity: ModuleEntity | null): boolean {
  return Boolean(
    entity &&
    !entity.sourceConflict &&
    entity.draftState === "new" &&
    entity.drafts.create,
  );
}

export function shouldRefreshAfterScaffoldApply(
  plan: ModuleScaffoldPlan,
): boolean {
  return plan.written && !plan.blocked;
}

export function canApplySourceTextDraft(entity: ModuleEntity | null): boolean {
  return !entity?.sourceConflict && sourceTextEditsForEntity(entity).length > 0;
}

export function canApplyRemovalDraft(entity: ModuleEntity | null): boolean {
  return Boolean(
    entity?.draftState === "remove" &&
    !entity.sourceConflict &&
    entity.layout === "canonical" &&
    (entity.kind === "collection"
      ? entity.collectionId?.trim()
      : entity.moduleId?.trim()) &&
    entity.root.trim(),
  );
}

export function canApplyImageDraft(entity: ModuleEntity | null): boolean {
  return (
    !entity?.sourceConflict && sourceReplacementsForEntity(entity).length > 0
  );
}

export function canApplyAssetDraft(entity: ModuleEntity | null): boolean {
  const drafts = entity?.drafts.assets ?? [];
  return (
    !entity?.sourceConflict &&
    drafts.length > 0 &&
    sourceAssetReplacementsForEntity(entity).length === drafts.length
  );
}

export function hasBlockingAssetDraft(
  entity: ModuleEntity | null | undefined,
): boolean {
  return (
    (entity?.drafts.assets?.length ?? 0) > 0 &&
    !canApplyAssetDraft(entity ?? null)
  );
}

export function canApplyInfoDraft(entity: ModuleEntity | null): boolean {
  const info = entity?.drafts.info;
  const objectIdWasEdited = Boolean(
    info && Object.prototype.hasOwnProperty.call(info, "objectId"),
  );
  const objectId = objectIdWasEdited
    ? (info?.objectId?.trim() ?? "")
    : (entity?.objectId ?? "");
  const titleWasEdited = Boolean(
    info && Object.prototype.hasOwnProperty.call(info, "title"),
  );
  const title = info?.title?.trim() ?? "";
  const objectIdChanged = Boolean(
    entity && objectIdWasEdited && objectId !== entity.objectId,
  );
  const titleChanged = Boolean(
    entity && titleWasEdited && title && title !== entity.title.trim(),
  );
  return Boolean(
    entity &&
    !entity.sourceConflict &&
    objectId &&
    (!titleWasEdited || title) &&
    (objectIdChanged || titleChanged) &&
    entity.layout === "canonical" &&
    (entity.kind === "collection"
      ? entity.collectionId && objectIdChanged
      : entity.moduleId),
  );
}

export function sourceTextEditsForEntity(
  entity: ModuleEntity | null,
): SourceTextEdit[] {
  if (
    !entity ||
    entity.sourceConflict ||
    entity.draftState === "new" ||
    entity.draftState === "remove"
  ) {
    return [];
  }
  return Object.entries(entity.drafts.text).flatMap(([sourceKey, text]) => {
    const source = entity.sourceSlots.find(
      (item) => item.draftKey === sourceKey,
    );
    if (
      !source?.path ||
      (source.editorKind !== "code" && source.editorKind !== "localization")
    ) {
      return [];
    }
    return [
      {
        path: source.path,
        text,
        ...sourceRevisionPrecondition(entity, source.path, sourceKey),
      },
    ];
  });
}

export function sourceFormUpdatesForEntity(
  entity: ModuleEntity | null,
): ModuleSourceFormUpdate[] {
  if (
    !entity ||
    entity.sourceConflict ||
    entity.draftState === "new" ||
    entity.draftState === "remove"
  ) {
    return [];
  }
  return Object.entries(entity.drafts.sourceForms ?? {}).flatMap(
    ([sourceKey, draft]) => {
      const source = entity.sourceSlots.find(
        (item) => item.draftKey === sourceKey && item.editorKind === "code",
      );
      if (!source?.path || Object.keys(draft.values).length === 0) {
        return [];
      }
      return [
        {
          sourceKey,
          sourcePath: source.path,
          text: draft.baseText,
          values: { ...draft.values },
        },
      ];
    },
  );
}

export function sourceTextEditsWithSourceFormPlan(
  entity: ModuleEntity,
  plan: SourceFormUpdateBatchPlan,
): SourceFormPlanMergeResult {
  const requests = sourceFormUpdatesForEntity(entity);
  if (requests.length === 0) {
    return plan.updates.length === 0
      ? { ok: true, sourceEdits: sourceTextEditsForEntity(entity) }
      : { ok: false, reason: "unexpected-plan" };
  }
  if (plan.updates.length !== requests.length) {
    return { ok: false, reason: "missing-plan" };
  }
  if (plan.sourceEdits.length !== requests.length) {
    return { ok: false, reason: "missing-plan" };
  }
  const guidedPaths = new Set<string>();
  for (let index = 0; index < requests.length; index += 1) {
    const request = requests[index];
    const planned = plan.updates[index];
    if (
      !planned ||
      moduleSourcePathIdentity(planned.path) !==
        moduleSourcePathIdentity(request.sourcePath)
    ) {
      return {
        ok: false,
        reason: planned ? "unexpected-plan" : "missing-plan",
      };
    }
    if (!planned.changed) {
      return { ok: false, reason: "missing-plan" };
    }
    const visibleText = entity.drafts.text[request.sourceKey];
    if (
      typeof visibleText !== "string" ||
      planned.sourceEdit.text !== visibleText
    ) {
      return { ok: false, reason: "text-mismatch" };
    }
    if (
      planned.sourceEdit.expectedSize === undefined ||
      planned.sourceEdit.expectedMtimeNs === undefined
    ) {
      return { ok: false, reason: "revision-missing" };
    }
    const batchEdit = plan.sourceEdits[index];
    if (
      !batchEdit ||
      moduleSourcePathIdentity(batchEdit.path) !==
        moduleSourcePathIdentity(planned.sourceEdit.path) ||
      batchEdit.text !== planned.sourceEdit.text ||
      batchEdit.expectedSize !== planned.sourceEdit.expectedSize ||
      batchEdit.expectedMtimeNs !== planned.sourceEdit.expectedMtimeNs
    ) {
      return { ok: false, reason: "unexpected-plan" };
    }
    guidedPaths.add(moduleSourcePathIdentity(request.sourcePath));
  }
  const rawEdits = sourceTextEditsForEntity(entity).filter(
    (edit) => !guidedPaths.has(moduleSourcePathIdentity(edit.path)),
  );
  return { ok: true, sourceEdits: [...rawEdits, ...plan.sourceEdits] };
}

export function sourceReplacementsForEntity(
  entity: ModuleEntity | null,
): SourceReplacement[] {
  if (
    !entity ||
    entity.sourceConflict ||
    entity.draftState === "new" ||
    entity.draftState === "remove" ||
    !entity.drafts.image?.contentBase64
  ) {
    return [];
  }
  const source = entity.drafts.image.sourceKey
    ? entity.sourceSlots.find(
        (item) =>
          item.draftKey === entity.drafts.image?.sourceKey &&
          item.editorKind === "image",
      )
    : entity.sourceSlots.find((item) => item.editorKind === "image");
  if (!source || !canReplaceImageSource(source)) {
    return [];
  }
  const path =
    entity.drafts.image.path || defaultImageDraftPath(entity, source);
  if (!path || !imageReplacementPathMatchesSource(path, source)) {
    return [];
  }
  const targetFormat = imageSourceFormat(source);
  const revisionPrecondition = entity.drafts.image.expectedAbsent
    ? { expectedAbsent: true as const }
    : sourceReplacementPrecondition(entity, path, source?.draftKey);
  if (targetFormat === "png") {
    return [
      {
        path,
        contentBase64: entity.drafts.image.contentBase64,
        ...revisionPrecondition,
      },
    ];
  }
  if (!isImageReplacementTargetFormat(targetFormat)) {
    return [];
  }
  return [
    {
      path,
      contentBase64: entity.drafts.image.contentBase64,
      contentFormat: "png",
      targetFormat,
      ...revisionPrecondition,
    },
  ];
}

export function sourceAssetReplacementsForEntity(
  entity: ModuleEntity | null,
): SourceReplacement[] {
  if (
    !entity ||
    entity.sourceConflict ||
    entity.draftState === "new" ||
    entity.draftState === "remove"
  ) {
    return [];
  }
  const drafts = entity.drafts.assets ?? [];
  if (
    drafts.some(
      (draft) =>
        !draft.contentBase64 ||
        !draft.path ||
        assetDraftPathError(entity, draft),
    )
  ) {
    return [];
  }
  return drafts.map((draft) => ({
    path: draft.path,
    contentBase64: draft.contentBase64,
    ...sourceReplacementPrecondition(entity, draft.path, draft.sourceKey),
  }));
}

export function assetSourcesForEntity(
  entity: ModuleEntity | null,
): ModuleSourceSlot[] {
  if (!entity) {
    return [];
  }
  return entity.sourceSlots.filter(
    (source) =>
      source.editorKind === "asset" &&
      (source.slot_kinds ?? []).includes("copy"),
  );
}

export function supportsAssetDrafts(entity: ModuleEntity | null): boolean {
  if (!entity) {
    return false;
  }
  if (
    assetSourcesForEntity(entity).length > 0 ||
    (entity.drafts.assets?.length ?? 0) > 0
  ) {
    return true;
  }
  return (entity.resourceSlots ?? []).some((slot) => slot.kind === "copy");
}

export function applyAssetDrafts(
  entity: ModuleEntity,
  assets: ModuleAssetDraft[],
): ModuleEntity {
  if (entity.draftState === "new" || entity.draftState === "remove") {
    return entity;
  }
  const validAssets = assets.filter(
    (draft) => draft.contentBase64 && draft.fileName,
  );
  const drafts = { ...entity.drafts };
  if (validAssets.length > 0) {
    drafts.assets = validAssets;
  } else {
    delete drafts.assets;
  }
  return retainDraftSourceRevisions(entity, {
    ...entity,
    draftState: draftStateForDrafts(drafts),
    drafts,
  });
}

export function defaultAssetDraftPath(
  entity: ModuleEntity,
  fileName: string,
): string {
  return assetDraftTargetForFile(entity, fileName)?.path ?? "";
}

export function assetDraftTargetForFile(
  entity: ModuleEntity,
  fileName: string,
): ModuleAssetDraftTarget | null {
  const candidates = assetDraftTargetsForFile(entity, fileName);
  return candidates.length === 1 ? candidates[0] : null;
}

/**
 * Resolves safe asset destinations from Registry copy slots without embedding
 * module-family rules in the desktop. Explicit authoring templates take
 * precedence; aggregate slots fall back to directories already owned by the
 * same Registry slot.
 */
export function assetDraftTargetsForFile(
  entity: ModuleEntity,
  fileName: string,
): ModuleAssetDraftTarget[] {
  const cleanName = assetFileName(fileName);
  if (!cleanName) {
    return [];
  }
  const extension = imagePathExtension(cleanName);
  const stem = extension
    ? cleanName.slice(0, -(extension.length + 1))
    : cleanName;
  const copySlots = (entity.resourceSlots ?? []).filter(
    (slot) => slot.kind === "copy",
  );
  const declaredCandidates = copySlots.flatMap((slot) => {
    if (slot.kind !== "copy" || !slot.authoring_path) {
      return [];
    }
    const renderedPath = renderAssetAuthoringPath(slot.authoring_path, {
      extension,
      filename: cleanName,
      object_id: entity.objectId,
      stem,
    });
    const modulePath = cleanRelativePath(renderedPath);
    if (!modulePath || !resourceSlotMatchesPath(slot, modulePath)) {
      return [];
    }
    const target = assetDraftTargetForModulePath(entity, slot, modulePath);
    return target ? [target] : [];
  });
  if (declaredCandidates.length > 0) {
    return uniqueAssetDraftTargets(declaredCandidates);
  }

  const existingSources = assetSourcesForEntity(entity);
  const inferredCandidates = existingSources.flatMap((source) => {
    const sourceModulePath = assetModuleRelativePath(
      entity,
      source.relative_path || source.path,
    );
    if (!sourceModulePath.includes("/")) {
      return [];
    }
    const parentPath = sourceModulePath.slice(
      0,
      sourceModulePath.lastIndexOf("/"),
    );
    const modulePath = cleanRelativePath(joinSourcePath(parentPath, cleanName));
    if (!modulePath) {
      return [];
    }
    return copySlots.flatMap((slot) => {
      if (
        slot.name !== source.slot ||
        !resourceSlotMatchesPath(slot, modulePath)
      ) {
        return [];
      }
      const target = assetDraftTargetForModulePath(entity, slot, modulePath);
      if (
        !target ||
        existingSources.some((item) =>
          assetDraftPathMatchesSource(target.path, item),
        )
      ) {
        return [];
      }
      return [target];
    });
  });
  return uniqueAssetDraftTargets(inferredCandidates);
}

function assetDraftTargetForModulePath(
  entity: ModuleEntity,
  slot: ProjectBrowserResourceSlot,
  modulePath: string,
): ModuleAssetDraftTarget | null {
  if (!resourceSlotMatchesPath(slot, modulePath)) {
    return null;
  }
  const path = entity.relativeRoot
    ? joinSourcePath(entity.relativeRoot, modulePath)
    : entity.root
      ? joinRootPath(entity.root, modulePath)
      : "";
  return path ? { modulePath, path, slotName: slot.name } : null;
}

function uniqueAssetDraftTargets(
  candidates: ModuleAssetDraftTarget[],
): ModuleAssetDraftTarget[] {
  const unique = new Map<string, ModuleAssetDraftTarget>();
  for (const candidate of candidates.sort((left, right) =>
    left.modulePath.localeCompare(right.modulePath),
  )) {
    const key = normalizedComparablePath(candidate.path);
    if (key && !unique.has(key)) {
      unique.set(key, candidate);
    }
  }
  return [...unique.values()];
}

export function assetDraftPathError(
  entity: ModuleEntity,
  draft: Pick<ModuleAssetDraft, "fileName" | "path" | "slotName" | "sourceKey">,
): "duplicate" | "empty" | "format" | "outside" | "slot" | "source" | "" {
  if (!draft.path.trim()) {
    return "empty";
  }
  if (imagePathExtension(draft.fileName) !== imagePathExtension(draft.path)) {
    return "format";
  }
  if (draft.sourceKey) {
    const source = assetSourcesForEntity(entity).find(
      (item) => item.draftKey === draft.sourceKey,
    );
    if (!source || !assetDraftPathMatchesSource(draft.path, source)) {
      return "source";
    }
  } else if (
    assetSourcesForEntity(entity).some((source) =>
      assetDraftPathMatchesSource(draft.path, source),
    )
  ) {
    return "source";
  } else if (!assetDraftPathBelongsToEntity(entity, draft.path)) {
    return "outside";
  } else {
    const modulePath = assetModuleRelativePath(entity, draft.path);
    const matchingSlots = (entity.resourceSlots ?? []).filter(
      (slot) =>
        slot.kind === "copy" &&
        (!draft.slotName || slot.name === draft.slotName) &&
        Boolean(modulePath && resourceSlotMatchesPath(slot, modulePath)),
    );
    if (matchingSlots.length === 0) {
      return "slot";
    }
  }
  const target = assetDraftTargetIdentity(entity, draft.path);
  const duplicateAssetCount = (entity.drafts.assets ?? []).filter(
    (candidate) => assetDraftTargetIdentity(entity, candidate.path) === target,
  ).length;
  const imageTarget = sourceReplacementsForEntity(entity)[0]?.path;
  return duplicateAssetCount > 1 ||
    (imageTarget && assetDraftTargetIdentity(entity, imageTarget) === target)
    ? "duplicate"
    : "";
}

export function assetDraftTargetIdentity(
  entity: ModuleEntity,
  path: string,
): string {
  const target = normalizedComparablePath(path);
  const relativeRoot = normalizedComparablePath(entity.relativeRoot);
  const absoluteRoot = normalizedComparablePath(entity.root);
  if (!target || !relativeRoot || !absoluteRoot.endsWith(`/${relativeRoot}`)) {
    return target;
  }
  const projectRoot = absoluteRoot.slice(0, -(relativeRoot.length + 1));
  return target.startsWith(`${projectRoot}/`)
    ? target.slice(projectRoot.length + 1)
    : target;
}

export function defaultImageDraftPath(
  entity: ModuleEntity,
  source: ModuleSourceSlot | null,
): string {
  void entity;
  return source?.path || source?.relative_path || "";
}

export function canReplaceImageSource(
  source: ModuleSourceSlot | null,
): boolean {
  if (!source || !(source.path || source.relative_path)) {
    return false;
  }
  const format = imageSourceFormat(source);
  return format === "png" || isImageReplacementTargetFormat(format);
}

export function imageSourceRequiresConversion(
  source: ModuleSourceSlot | null,
): boolean {
  const format = imageSourceFormat(source);
  return Boolean(
    source &&
    (source.path || source.relative_path) &&
    isImageReplacementTargetFormat(format),
  );
}

export function canPreviewImageSourceInEditor(
  source: ModuleSourceSlot | null,
): boolean {
  if (!source || !(source.path || source.relative_path)) {
    return true;
  }
  return IMAGE_EDITOR_PREVIEW_FORMATS.has(imageSourceFormat(source));
}

export function imageSourceFormat(source: ModuleSourceSlot | null): string {
  if (!source) {
    return "";
  }
  return (
    imagePathExtension(source.path || source.relative_path || source.name) ||
    normalizedExtension(source.extension)
  );
}

export type ModuleTitleLocalizationTarget = {
  key: string;
  language: string;
  slot: string;
};

export function moduleTitleLocalizationTarget(
  entity: ModuleEntity,
  locale: Locale,
  sources: readonly ModuleLocalizationTextSource[],
  table: ModuleLocalizationTable,
): ModuleTitleLocalizationTarget | null {
  const keys = (entity.titleKeys ?? [])
    .map((key) => key.trim())
    .filter(Boolean);
  if (keys.length === 0 || sources.length === 0) {
    return null;
  }
  const preferredLanguage = normalizeLocalizationLanguage(locale);
  const sourceLanguages = sources.map((source) =>
    localizationLanguageForText(source.text, source.language),
  );
  const languages = [preferredLanguage, "l_english", ...sourceLanguages].filter(
    (language, index, rows) => rows.indexOf(language) === index,
  );

  for (const language of languages) {
    for (const key of keys) {
      const cell = table.rows.find((row) => row.key === key)?.values[language];
      if (cell) {
        return { key, language, slot: cell.slot };
      }
    }
  }

  const preferredSourceIndex = sourceLanguages.indexOf(preferredLanguage);
  const englishSourceIndex = sourceLanguages.indexOf("l_english");
  const sourceIndex =
    preferredSourceIndex >= 0
      ? preferredSourceIndex
      : englishSourceIndex >= 0
        ? englishSourceIndex
        : 0;
  const source = sources[sourceIndex];
  return {
    key: keys[0],
    language: sourceLanguages[sourceIndex] ?? preferredLanguage,
    slot: source.slot,
  };
}

export function updateMetadataTitleText(text: string, title: string): string {
  const lines = text.split(/\r?\n/);
  const titleLine = /^(\s*(?:title|label|name)\s*:\s*).*$/;
  const replacement = `$1${yamlQuotedString(title.trim())}`;

  for (let index = 0; index < lines.length; index += 1) {
    if (titleLine.test(lines[index])) {
      lines[index] = lines[index].replace(titleLine, replacement);
      return joinLocalizationLines(lines, text);
    }
  }

  const withoutTrailingEmpty = lines.at(-1) === "" ? lines.slice(0, -1) : lines;
  return (
    [`title: ${yamlQuotedString(title.trim())}`, ...withoutTrailingEmpty].join(
      "\n",
    ) + "\n"
  );
}

export function localizationLanguageForText(
  text: string,
  fallback = "l_english",
): string {
  return localizationLanguage(text, fallback);
}

export function applySourceTextPlanToEntity(
  entity: ModuleEntity,
  payload: DraftApplyPayload,
): ModuleEntity {
  const writtenPaths = new Set(
    payload.files.flatMap((file) =>
      [file.path, file.relative_path].filter(Boolean),
    ),
  );
  const text = Object.fromEntries(
    Object.entries(entity.drafts.text).filter(([sourceKey]) => {
      const source = entity.sourceSlots.find(
        (item) => item.draftKey === sourceKey,
      );
      if (!source) {
        return true;
      }
      return ![source.path, source.relative_path].some(
        (path) => path && writtenPaths.has(path),
      );
    }),
  );
  const sourceForms = Object.fromEntries(
    Object.entries(entity.drafts.sourceForms ?? {}).filter(([sourceKey]) => {
      const source = entity.sourceSlots.find(
        (item) => item.draftKey === sourceKey,
      );
      if (!source) {
        return true;
      }
      return ![source.path, source.relative_path].some(
        (path) => path && writtenPaths.has(path),
      );
    }),
  );
  const metadataSource = entity.sourceSlots.find(
    (source) => source.slot === "meta",
  );
  const metadataWasWritten = Boolean(
    metadataSource &&
    [metadataSource.path, metadataSource.relative_path].some(
      (path) => path && writtenPaths.has(path),
    ),
  );
  const info = entity.drafts.info ? { ...entity.drafts.info } : undefined;
  const folderTitleRenamePending = Boolean(
    metadataWasWritten &&
    info?.title?.trim() &&
    entity.layout === "canonical" &&
    entity.moduleId,
  );
  const writtenTitle =
    metadataWasWritten && !folderTitleRenamePending ? info?.title : undefined;
  if (metadataWasWritten && info && !folderTitleRenamePending) {
    delete info.title;
  }
  const nextInfo = info && Object.keys(info).length > 0 ? info : undefined;
  const drafts: ModuleEntityDrafts = {
    ...entity.drafts,
    text,
    ...(Object.keys(sourceForms).length > 0
      ? { sourceForms }
      : { sourceForms: undefined }),
  };
  if (nextInfo) {
    drafts.info = nextInfo;
  } else {
    delete drafts.info;
  }
  return reconcileAppliedDraftEntity(entity, payload, drafts, {
    title: writtenTitle ?? entity.title,
  });
}

export function applyImageReplacementPlanToEntity(
  entity: ModuleEntity,
  payload: DraftApplyPayload,
): ModuleEntity {
  const replacedPaths = new Set(
    payload.files
      .filter((file) => file.operation === "replace_bytes")
      .flatMap((file) =>
        [file.path, file.relative_path]
          .filter(Boolean)
          .map((path) => assetDraftTargetIdentity(entity, path)),
      ),
  );
  const replacementTargets = [
    entity.drafts.image?.path,
    ...entity.sourceSlots
      .filter((source) => source.editorKind === "image")
      .flatMap((source) => [source.path, source.relative_path]),
  ];
  const imageWasReplaced = replacementTargets.some(
    (path) => path && replacedPaths.has(assetDraftTargetIdentity(entity, path)),
  );
  if (!imageWasReplaced) {
    return entity;
  }
  const { image: _image, ...drafts } = entity.drafts;
  return reconcileAppliedDraftEntity(entity, payload, drafts);
}

export function applyAssetReplacementPlanToEntity(
  entity: ModuleEntity,
  payload: DraftApplyPayload,
): ModuleEntity {
  const replacedPaths = new Set(
    payload.files
      .filter((file) => file.operation === "replace_bytes")
      .flatMap((file) =>
        [file.path, file.relative_path]
          .filter(Boolean)
          .map((path) => assetDraftTargetIdentity(entity, path)),
      ),
  );
  const remainingAssets = (entity.drafts.assets ?? []).filter(
    (draft) => !replacedPaths.has(assetDraftTargetIdentity(entity, draft.path)),
  );
  if (remainingAssets.length === (entity.drafts.assets ?? []).length) {
    return entity;
  }
  const drafts = { ...entity.drafts };
  if (remainingAssets.length > 0) {
    drafts.assets = remainingAssets;
  } else {
    delete drafts.assets;
  }
  return reconcileAppliedDraftEntity(entity, payload, drafts);
}

export function applyScaffoldPlanToEntity(
  entity: ModuleEntity,
  plan: ModuleScaffoldPlan,
): ModuleEntity {
  const sourceSlots = sourceSlotsWithDraftKeys(
    plan.files.map(sourceSlotFromScaffoldFile),
  );
  const sourceCount = sourceSlots.length;
  const objectId = plan.object_id || entity.objectId;
  const title = plan.values.title?.trim() || entity.title || objectId;

  return {
    ...entity,
    id: `module:${plan.module_id}`,
    family: plan.family || entity.family,
    moduleId: plan.module_id,
    objectId,
    title,
    subtitle: objectId,
    root: plan.root,
    relativeRoot: relativeRootFromPlan(plan),
    layout: "canonical",
    sourceCount,
    sourceSlots,
    active: true,
    tags: buildTags(true),
    draftState: "clean",
    drafts: { text: {} },
  };
}

export function nextDraftObjectId(
  familyId: string,
  existing: ModuleEntity[],
  template: ProjectTemplate | null = null,
): string {
  return `${sanitizeIdentifier(template?.family ?? familyId)}_DRAFT_${String(existing.length + 1).padStart(3, "0")}`;
}

export function markEntitiesForRemoval(
  entities: ModuleEntity[],
  ids: Set<string>,
): ModuleEntity[] {
  return entities.flatMap((entity) => {
    if (!ids.has(entity.id)) {
      return [entity];
    }
    return entity.draftState === "new"
      ? []
      : [
          retainDraftSourceRevisions(entity, {
            ...entity,
            draftState: "remove" as const,
          }),
        ];
  });
}

export function buildModuleEntitySelectionState(
  allEntities: Pick<ModuleEntity, "id">[],
  visibleEntities: Pick<ModuleEntity, "id">[],
  selectedIds: Set<string>,
): ModuleEntitySelectionState {
  const allIds = new Set(allEntities.map((entity) => entity.id));
  const visibleIds = visibleEntities.map((entity) => entity.id);
  const selectedCount = [...selectedIds].filter((id) => allIds.has(id)).length;
  const visibleSelectedCount = visibleIds.filter((id) =>
    selectedIds.has(id),
  ).length;
  const totalCount = allEntities.length;
  const visibleCount = visibleEntities.length;

  return {
    allSelected: totalCount > 0 && selectedCount === totalCount,
    allVisibleSelected:
      visibleCount > 0 && visibleSelectedCount === visibleCount,
    hasFilteredScope: visibleCount !== totalCount,
    hiddenSelectedCount: Math.max(0, selectedCount - visibleSelectedCount),
    selectedCount,
    someVisibleSelected: visibleSelectedCount > 0,
    totalCount,
    visibleCount,
    visibleSelectedCount,
  };
}

export function selectModuleEntityScope(
  selectedIds: Set<string>,
  scopeIds: string[],
  mode: ModuleEntitySelectionMode,
): Set<string> {
  const scope = [...new Set(scopeIds.filter(Boolean))];
  if (mode === "replace") {
    return new Set(scope);
  }

  const next = new Set(selectedIds);
  if (mode === "add") {
    for (const id of scope) {
      next.add(id);
    }
    return next;
  }

  if (scope.length > 0 && scope.every((id) => next.has(id))) {
    for (const id of scope) {
      next.delete(id);
    }
    return next;
  }

  for (const id of scope) {
    next.add(id);
  }
  return next;
}

export function selectModuleEntityRange(
  selectedIds: Set<string>,
  orderedIds: string[],
  anchorId: string,
  targetId: string,
  action: ModuleEntityRangeAction,
): Set<string> {
  const ordered = [...new Set(orderedIds.filter(Boolean))];
  const targetIndex = ordered.indexOf(targetId);
  if (targetIndex < 0) {
    return new Set(selectedIds);
  }

  const anchorIndex = ordered.indexOf(anchorId);
  const start = Math.min(
    anchorIndex < 0 ? targetIndex : anchorIndex,
    targetIndex,
  );
  const end = Math.max(
    anchorIndex < 0 ? targetIndex : anchorIndex,
    targetIndex,
  );
  const range = ordered.slice(start, end + 1);
  const next = new Set(selectedIds);

  for (const id of range) {
    if (action === "select") {
      next.add(id);
    } else {
      next.delete(id);
    }
  }
  return next;
}

function toModuleSourceSlot(source: ProjectBrowserSource): ModuleSourceSlot {
  return {
    ...source,
    draftKey: source.slot,
    editorKind: sourceEditorKind(source),
  };
}

function sourceSlotsForItem(item: ProjectBrowserItem): ModuleSourceSlot[] {
  const existingPaths = new Set(
    item.sources.flatMap((source) =>
      [source.path, source.relative_path]
        .filter(Boolean)
        .map(moduleSourcePathIdentity),
    ),
  );
  const declaredTargets = (item.image_targets ?? []).filter(
    (source) =>
      source.exists === false &&
      ![source.path, source.relative_path].some(
        (path) => path && existingPaths.has(moduleSourcePathIdentity(path)),
      ),
  );
  const slots = [...item.sources, ...declaredTargets].map(toModuleSourceSlot);
  return sourceSlotsWithDraftKeys([
    ...slots,
    ...sourceFocusInfoSlotsForItem(item, slots),
  ]);
}

function previewSourceForItem(
  item: ProjectBrowserItem,
): ModuleSourceSlot | undefined {
  const metadata = recordValue(item.metadata);
  const settings = recordValue(metadata.settings);
  const sourcePath = cleanRelativePath(
    stringForKeys(settings, ["preview_image_path", "previewImagePath"]),
  );
  if (!sourcePath) {
    return undefined;
  }
  const name = sourcePath.split("/").at(-1) ?? sourcePath;
  const extension = name.includes(".")
    ? `.${name.split(".").at(-1) ?? ""}`
    : "";
  const declaredTarget = item.image_targets?.find((target) =>
    [target.relative_path, target.path].some(
      (path) =>
        path &&
        (moduleSourcePathIdentity(path) ===
          moduleSourcePathIdentity(sourcePath) ||
          moduleSourcePathIdentity(path).endsWith(
            `/${moduleSourcePathIdentity(sourcePath)}`,
          )),
    ),
  );
  return toModuleSourceSlot({
    slot: "preview",
    name,
    path: item.root ? joinRootPath(item.root, sourcePath) : "",
    relative_path: item.relative_root
      ? joinSourcePath(item.relative_root, sourcePath)
      : sourcePath,
    extension,
    ...(declaredTarget?.exists === false ? { exists: false } : {}),
  });
}

function sourceFocusInfoSlotsForItem(
  item: ProjectBrowserItem,
  existingSlots: ModuleSourceSlot[],
): ModuleSourceSlot[] {
  if (canonicalFamilyId(item.family_id, item.family) !== "focuses") {
    return [];
  }
  const existingPaths = new Set(
    existingSlots.flatMap((slot) =>
      [slot.path, slot.relative_path].filter(Boolean),
    ),
  );
  return sourceFocusRecordsForItem(item).flatMap((record) => {
    const id = stringForKeys(record, SOURCE_FOCUS_ID_KEYS);
    const sourcePath = sourceFocusInfoRelativePath(
      stringForKeys(record, ["source_path", "sourcePath", "folder"]),
    );
    const relativePath = sourcePath
      ? joinSourcePath(item.relative_root, sourcePath)
      : "";
    if (!id || !sourcePath || existingPaths.has(relativePath)) {
      return [];
    }
    existingPaths.add(relativePath);
    return [
      toModuleSourceSlot({
        slot: `focus:${id}:info`,
        name: `${id} info.json`,
        path: item.root ? joinRootPath(item.root, sourcePath) : "",
        relative_path: relativePath,
        extension: "json",
      }),
    ];
  });
}

function sourceFocusRecordsForItem(
  item: ProjectBrowserItem,
): Record<string, unknown>[] {
  const metadata = recordValue(item.metadata);
  const settings = recordValue(metadata.settings);
  for (const source of [settings, metadata]) {
    for (const key of SOURCE_FOCUS_COLLECTION_KEYS) {
      const records = recordList(source[key]);
      if (records.length > 0) {
        return records;
      }
    }
  }
  return [];
}

function sourceFocusInfoRelativePath(value: string): string {
  const clean = cleanRelativePath(value);
  if (!clean) {
    return "";
  }
  const withInfo = clean.endsWith("/info.json") ? clean : `${clean}/info.json`;
  return withInfo.startsWith("legacy/") ? withInfo : `legacy/${withInfo}`;
}

function recordValue(value: unknown): Record<string, unknown> {
  return value && typeof value === "object" && !Array.isArray(value)
    ? (value as Record<string, unknown>)
    : {};
}

function recordList(value: unknown): Record<string, unknown>[] {
  return Array.isArray(value)
    ? value.map(recordValue).filter((record) => Object.keys(record).length > 0)
    : [];
}

function stringForKeys(
  record: Record<string, unknown>,
  keys: string[],
): string {
  for (const key of keys) {
    const value = record[key];
    if (typeof value === "string" && value.trim()) {
      return value.trim();
    }
  }
  return "";
}

function cleanRelativePath(value: string): string {
  const clean = value
    .replace(/\\/g, "/")
    .replace(/^\/+/, "")
    .replace(/\/+$/, "");
  if (!clean || clean.includes("://")) {
    return "";
  }
  const parts = clean.split("/");
  return parts.some((part) => !part || part === "." || part === "..")
    ? ""
    : parts.join("/");
}

function joinSourcePath(...parts: string[]): string {
  return parts
    .map((part) => part.replace(/\\/g, "/").replace(/^\/+|\/+$/g, ""))
    .filter(Boolean)
    .join("/");
}

function joinRootPath(root: string, relativePath: string): string {
  const cleanRoot = root.replace(/\\/g, "/").replace(/\/+$/g, "");
  const cleanRelative = relativePath.replace(/\\/g, "/").replace(/^\/+/g, "");
  return cleanRoot && cleanRelative
    ? `${cleanRoot}/${cleanRelative}`
    : cleanRoot || cleanRelative;
}

function defaultDraftSourceSlots(): ModuleSourceSlot[] {
  return sourceSlotsWithDraftKeys([
    toModuleSourceSlot({
      slot: "def",
      name: "def.pdx",
      path: "",
      relative_path: "",
      extension: ".pdx",
    }),
    toModuleSourceSlot({
      slot: "loc",
      name: "main.loc",
      path: "",
      relative_path: "",
      extension: ".loc",
    }),
  ]);
}

function sourceSlotFromTemplateFile(file: string): ModuleSourceSlot {
  const name = file.split("/").at(-1) ?? file;
  const extension = file.includes(".")
    ? `.${file.split(".").at(-1) ?? ""}`
    : "";
  return toModuleSourceSlot({
    slot: slotFromTemplateFile(name, extension),
    name,
    path: "",
    relative_path: "",
    extension,
  });
}

function sourceSlotFromScaffoldFile(
  file: ModuleScaffoldFile,
): ModuleSourceSlot {
  const modulePath = file.module_path || file.relative_path;
  const name = modulePath.split("/").at(-1) ?? modulePath;
  const extension = name.includes(".")
    ? `.${name.split(".").at(-1) ?? ""}`
    : "";
  return toModuleSourceSlot({
    slot: slotFromTemplateFile(name, extension),
    name,
    path: file.path,
    relative_path: file.relative_path,
    extension,
  });
}

function moduleIdForItem(item: ProjectBrowserItem): string | undefined {
  if (item.module_id?.includes("/")) {
    return item.module_id;
  }
  if (item.layout === "canonical") {
    return `${item.family}/${item.object_id}`;
  }
  return item.module_id;
}

function normalizedInfoDraft(
  entity: ModuleEntity,
  draft: NonNullable<ModuleEntityDrafts["info"]>,
): NonNullable<ModuleEntityDrafts["info"]> | undefined {
  const objectId =
    draft.objectId === undefined
      ? undefined
      : sanitizeIdentifier(draft.objectId);
  const title = draft.title === undefined ? undefined : draft.title.trim();
  const info: NonNullable<ModuleEntityDrafts["info"]> = {};
  if (objectId && objectId !== entity.objectId) {
    info.objectId = objectId;
  }
  if (title && title !== entity.title) {
    info.title = title;
  }
  return Object.keys(info).length > 0 ? info : undefined;
}

function retainDraftSourceRevisions(
  previous: ModuleEntity,
  next: ModuleEntity,
): ModuleEntity {
  if (next.draftState === "clean" || next.draftState === "new") {
    const {
      draftSourceRevisions: _draftSourceRevisions,
      sourceConflict: _sourceConflict,
      ...clean
    } = next;
    return clean;
  }
  const currentRevisions = sourceRevisionsForEntity(previous);
  const revisions = previous.draftSourceRevisions
    ? mergeNewDraftSourceRevisions(
        previous.draftSourceRevisions,
        currentRevisions,
        draftSourceReferences(previous),
        draftSourceReferences(next),
      )
    : currentRevisions;
  return revisions.length > 0
    ? { ...next, draftSourceRevisions: revisions }
    : next;
}

function draftSourceReferences(entity: ModuleEntity): {
  paths: Set<string>;
  sourceKeys: Set<string>;
} {
  const paths = new Set<string>();
  const sourceKeys = new Set(Object.keys(entity.drafts.text));
  const addReference = (sourceKey?: string, path?: string) => {
    if (sourceKey) {
      sourceKeys.add(sourceKey);
    }
    if (path) {
      paths.add(moduleSourcePathIdentity(path));
    }
  };
  addReference(entity.drafts.image?.sourceKey, entity.drafts.image?.path);
  for (const asset of entity.drafts.assets ?? []) {
    addReference(asset.sourceKey, asset.path);
  }
  if (entity.draftState === "remove") {
    for (const revision of sourceRevisionsForEntity(entity)) {
      addReference(revision.sourceKey, revision.path || revision.relativePath);
    }
  }
  return { paths, sourceKeys };
}

function mergeNewDraftSourceRevisions(
  retained: readonly ModuleSourceRevision[],
  current: readonly ModuleSourceRevision[],
  previousReferences: ReturnType<typeof draftSourceReferences>,
  nextReferences: ReturnType<typeof draftSourceReferences>,
): ModuleSourceRevision[] {
  const revisions = new Map(
    retained.map((revision) => [
      moduleSourcePathIdentity(revision.path || revision.relativePath),
      revision,
    ]),
  );
  for (const revision of current) {
    const pathIdentity = moduleSourcePathIdentity(
      revision.path || revision.relativePath,
    );
    const newlyDrafted =
      (nextReferences.sourceKeys.has(revision.sourceKey) &&
        !previousReferences.sourceKeys.has(revision.sourceKey)) ||
      (nextReferences.paths.has(pathIdentity) &&
        !previousReferences.paths.has(pathIdentity));
    if (newlyDrafted && !revisions.has(pathIdentity)) {
      revisions.set(pathIdentity, revision);
    }
  }
  return [...revisions.values()].sort((left, right) =>
    moduleSourcePathIdentity(left.path || left.relativePath).localeCompare(
      moduleSourcePathIdentity(right.path || right.relativePath),
    ),
  );
}

function reconcileAppliedDraftEntity(
  entity: ModuleEntity,
  payload: DraftApplyPayload,
  drafts: ModuleEntityDrafts,
  changes: Partial<Pick<ModuleEntity, "title">> = {},
): ModuleEntity {
  const {
    draftSourceRevisions: _draftSourceRevisions,
    sourceConflict: _sourceConflict,
    ...base
  } = entity;
  const draftState = draftStateForDrafts(drafts);
  const next = {
    ...base,
    ...changes,
    draftState,
    drafts,
  };
  if (draftState === "clean") {
    return next;
  }
  const writtenPaths = new Set(
    payload.files.flatMap((file) =>
      [file.path, file.relative_path]
        .filter(Boolean)
        .map(moduleSourcePathIdentity),
    ),
  );
  const remainingRevisions = (
    entity.draftSourceRevisions ?? sourceRevisionsForEntity(entity)
  ).filter(
    (revision) =>
      ![revision.path, revision.relativePath].some(
        (path) => path && writtenPaths.has(moduleSourcePathIdentity(path)),
      ),
  );
  return remainingRevisions.length > 0
    ? { ...next, draftSourceRevisions: remainingRevisions }
    : next;
}

function sourceRevisionPrecondition(
  entity: ModuleEntity,
  path: string,
  sourceKey?: string,
): Pick<SourceTextEdit, "expectedSize" | "expectedMtimeNs"> {
  const pathIdentity = moduleSourcePathIdentity(path);
  const revision = entity.draftSourceRevisions?.find(
    (candidate) =>
      [candidate.path, candidate.relativePath].some(
        (candidatePath) =>
          candidatePath &&
          moduleSourcePathIdentity(candidatePath) === pathIdentity,
      ) || Boolean(sourceKey && candidate.sourceKey === sourceKey),
  );
  return revision
    ? {
        expectedSize: revision.size,
        expectedMtimeNs: revision.mtimeNs,
      }
    : {};
}

function sourceReplacementPrecondition(
  entity: ModuleEntity,
  path: string,
  sourceKey?: string,
): Pick<
  SourceReplacement,
  "expectedSize" | "expectedMtimeNs" | "expectedAbsent"
> {
  const revision = sourceRevisionPrecondition(entity, path, sourceKey);
  if (
    revision.expectedSize !== undefined &&
    revision.expectedMtimeNs !== undefined
  ) {
    return revision;
  }
  const pathIdentity = moduleSourcePathIdentity(path);
  const existingSource = entity.sourceSlots.some(
    (source) =>
      source.exists !== false &&
      Boolean(source.path || source.relative_path) &&
      (Boolean(sourceKey && source.draftKey === sourceKey) ||
        [source.path, source.relative_path].some(
          (candidatePath) =>
            candidatePath &&
            moduleSourcePathIdentity(candidatePath) === pathIdentity,
        )),
  );
  return existingSource ? {} : { expectedAbsent: true };
}

function draftStateForDrafts(drafts: ModuleEntityDrafts): ModuleDraftState {
  return Object.keys(drafts.text).length > 0 ||
    drafts.image ||
    drafts.info ||
    (drafts.assets?.length ?? 0) > 0
    ? "modified"
    : "clean";
}

function relativeRootFromPlan(plan: ModuleScaffoldPlan): string {
  const file = plan.files.find(
    (item) => item.relative_path && item.module_path,
  );
  if (!file) {
    return "";
  }
  const suffix = `/${file.module_path}`;
  return file.relative_path.endsWith(suffix)
    ? file.relative_path.slice(0, -suffix.length)
    : file.relative_path.replace(/\/[^/]*$/, "");
}

function buildDraftText(
  sourceSlots: ModuleSourceSlot[],
): Record<string, string> {
  return Object.fromEntries(
    sourceSlots
      .filter(
        (source) =>
          source.editorKind === "code" || source.editorKind === "localization",
      )
      .map((source) => [source.draftKey, ""]),
  );
}

function slotFromTemplateFile(name: string, extension: string): string {
  if (name === "meta.yaml" || name === "meta.yml") {
    return "meta";
  }
  if (name === "def.pdx" || name === "def.txt") {
    return "def";
  }
  if (extension === ".loc" || extension === ".yml" || extension === ".yaml") {
    return "loc";
  }
  return name.replace(/\.[^.]+$/, "") || "source";
}

function sourceEditorKind(
  source: ProjectBrowserSource,
): ModuleSourceSlot["editorKind"] {
  const slot = source.slot.toLowerCase();
  const extension = normalizedExtension(source.extension);
  if (IMAGE_EXTENSIONS.has(extension)) {
    return "image";
  }
  if (slot === "meta") {
    return "code";
  }
  if (
    slot === "loc" ||
    slot.includes("local") ||
    extension === "loc" ||
    extension === "yml" ||
    extension === "yaml"
  ) {
    return "localization";
  }
  if (CODE_EXTENSIONS.has(extension) || slot === "def") {
    return "code";
  }
  if (slot === "icon" || slot === "image") {
    return "image";
  }
  return "asset";
}

function sourceSlotsWithDraftKeys(
  sourceSlots: ModuleSourceSlot[],
  sourceIdentities: readonly string[] = [],
): ModuleSourceSlot[] {
  const slotCounts = new Map<string, number>();
  for (const source of sourceSlots) {
    slotCounts.set(source.slot, (slotCounts.get(source.slot) ?? 0) + 1);
  }

  const usedKeys = new Set(
    sourceSlots
      .filter((source) => slotCounts.get(source.slot) === 1)
      .map((source) => source.slot),
  );
  return sourceSlots.map((source, index) => {
    if (slotCounts.get(source.slot) === 1) {
      return { ...source, draftKey: source.slot };
    }
    const identity =
      normalizedSourceIdentity(
        sourceIdentities[index] ||
          source.relative_path ||
          source.path ||
          source.name,
      ) || "source";
    const baseKey = `${source.slot}::${identity}`;
    let draftKey = baseKey;
    let suffix = 2;
    while (usedKeys.has(draftKey)) {
      draftKey = `${baseKey}#${suffix}`;
      suffix += 1;
    }
    usedKeys.add(draftKey);
    return { ...source, draftKey };
  });
}

function normalizedSourceIdentity(value: string): string {
  return value
    .trim()
    .replace(/\\/g, "/")
    .replace(/^\/+/, "")
    .replace(/\/+$/, "");
}

function moduleSourcePathIdentity(value: string): string {
  const normalized = value.trim().replace(/\\/g, "/").replace(/\/+$/, "");
  return /^[A-Za-z]:\//.test(normalized) || normalized.startsWith("//")
    ? normalized.toLowerCase()
    : normalized;
}

function buildTags(active: boolean): ModuleEntityTag[] {
  return active
    ? []
    : [{ label: "Inactive", tone: "metadata" }];
}

function normalizedExtension(extension: string): string {
  return extension.trim().toLowerCase().replace(/^\./, "");
}

function imagePathExtension(path: string): string {
  const cleanPath = path.trim().split(/[?#]/, 1)[0] ?? "";
  return normalizedExtension(cleanPath.match(/\.([^/.\\]+)$/)?.[1] ?? "");
}

function isImageReplacementTargetFormat(
  format: string,
): format is SourceReplacementTargetFormat {
  return IMAGE_REPLACEMENT_TARGET_FORMATS.has(
    format as SourceReplacementTargetFormat,
  );
}

function imageReplacementPathMatchesSource(
  path: string,
  source: ModuleSourceSlot,
): boolean {
  if (!(source.path || source.relative_path)) {
    return false;
  }
  const target = normalizedComparablePath(path);
  return [source.path, source.relative_path].some(
    (candidate) => candidate && normalizedComparablePath(candidate) === target,
  );
}

function assetDraftPathMatchesSource(
  path: string,
  source: ModuleSourceSlot,
): boolean {
  const target = normalizedComparablePath(path);
  return [source.path, source.relative_path].some(
    (candidate) => candidate && normalizedComparablePath(candidate) === target,
  );
}

function assetDraftPathBelongsToEntity(
  entity: ModuleEntity,
  path: string,
): boolean {
  const target = normalizedComparablePath(path);
  if (
    !target ||
    target.split("/").some((part) => part === "." || part === "..")
  ) {
    return false;
  }
  const absolute = /^(?:[A-Za-z]:\/|\/)/.test(path.trim().replace(/\\/g, "/"));
  const root = normalizedComparablePath(
    absolute ? entity.root : entity.relativeRoot,
  );
  return Boolean(root && (target === root || target.startsWith(`${root}/`)));
}

function assetFileName(value: string): string {
  const name = value.trim().replace(/\\/g, "/").split("/").at(-1) ?? "";
  return !name || name === "." || name === ".." ? "" : name;
}

function renderAssetAuthoringPath(
  template: string,
  values: Record<"extension" | "filename" | "object_id" | "stem", string>,
): string {
  const rendered = template.replace(
    /\{(extension|filename|object_id|stem)\}/g,
    (_placeholder, key: keyof typeof values) => values[key],
  );
  return /[{}]/.test(rendered) ? "" : rendered;
}

function assetModuleRelativePath(entity: ModuleEntity, path: string): string {
  const target = path.trim().replace(/\\/g, "/").replace(/\/+$/, "");
  for (const rawRoot of [entity.relativeRoot, entity.root]) {
    const root = rawRoot.trim().replace(/\\/g, "/").replace(/\/+$/, "");
    if (!root) {
      continue;
    }
    const normalizedTarget = target.normalize("NFC").toLocaleLowerCase("en-US");
    const normalizedRoot = root.normalize("NFC").toLocaleLowerCase("en-US");
    if (normalizedTarget.startsWith(`${normalizedRoot}/`)) {
      return cleanRelativePath(target.slice(root.length + 1));
    }
  }
  return "";
}

function resourceSlotMatchesPath(
  slot: ProjectBrowserResourceSlot,
  path: string,
): boolean {
  if (slot.regex) {
    try {
      return new RegExp(slot.match).test(path);
    } catch {
      return false;
    }
  }
  if (!["*", "?", "["].some((character) => slot.match.includes(character))) {
    return path === slot.match;
  }
  try {
    return resourceGlobPattern(slot.match).test(path);
  } catch {
    return false;
  }
}

function resourceGlobPattern(pattern: string): RegExp {
  let expression = "^";
  for (let index = 0; index < pattern.length; index += 1) {
    const character = pattern[index];
    if (character === "*" && pattern[index + 1] === "*") {
      const followedBySlash = pattern[index + 2] === "/";
      expression += followedBySlash ? "(?:.*/)?" : ".*";
      index += followedBySlash ? 2 : 1;
      continue;
    }
    if (character === "*") {
      expression += "[^/]*";
      continue;
    }
    if (character === "?") {
      expression += "[^/]";
      continue;
    }
    if (character === "[") {
      const end = pattern.indexOf("]", index + 1);
      if (end > index + 1) {
        const content = pattern.slice(index + 1, end);
        expression += `[${content.startsWith("!") ? `^${content.slice(1)}` : content}]`;
        index = end;
        continue;
      }
    }
    expression += escapeRegExp(character);
  }
  return new RegExp(`${expression}$`);
}

function normalizedComparablePath(path: string): string {
  const value = path.trim().replace(/\\/g, "/");
  const prefix = value.startsWith("//")
    ? "//"
    : value.startsWith("/")
      ? "/"
      : "";
  const normalized = `${prefix}${value.replace(/^\/+/, "").replace(/\/+/g, "/").replace(/\/+$/, "")}`;
  return normalized.normalize("NFC").toLocaleLowerCase("en-US");
}

function localizationLanguage(text: string, fallback = "l_english"): string {
  const yaml = text.match(/^\s*(l_[\w-]+)\s*:\s*$/m)?.[1];
  if (yaml) {
    return yaml;
  }
  const bracketLoc = text.match(/^\s*\[([A-Za-z][\w-]*)\.[^\]]+\]\s*$/m)?.[1];
  if (bracketLoc) {
    return normalizeLocalizationLanguage(bracketLoc);
  }
  const ini = text.match(/^\s*\[([^\].]+)\]\s*$/m)?.[1];
  return normalizeLocalizationLanguage(ini || fallback);
}

export function normalizeLocalizationLanguage(value: string): string {
  const normalized = value
    .trim()
    .toLowerCase()
    .replace(/[\s-]+/g, "_");
  if (!normalized) {
    return "l_english";
  }
  if (normalized.startsWith("l_")) {
    return normalized;
  }
  if (normalized === "en" || normalized === "english") {
    return "l_english";
  }
  if (
    normalized === "zh" ||
    normalized === "cn" ||
    normalized === "chinese" ||
    normalized === "simp_chinese"
  ) {
    return "l_simp_chinese";
  }
  return `l_${normalized}`;
}

function yamlQuotedString(value: string): string {
  return JSON.stringify(value);
}

function joinLocalizationLines(lines: string[], original: string): string {
  const joined = lines.join("\n");
  return original.endsWith("\n") && !joined.endsWith("\n")
    ? `${joined}\n`
    : joined;
}

function escapeRegExp(value: string): string {
  return value.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}

function compareEntities(
  left: ModuleEntity,
  right: ModuleEntity,
  sort: ModuleSortOrder,
): number {
  if (sort === "sourceCount") {
    return (
      right.sourceCount - left.sourceCount || compareEntityIdentity(left, right)
    );
  }
  if (sort === "id") {
    return (
      compareText(left.objectId, right.objectId) ||
      compareText(left.title, right.title) ||
      compareText(left.id, right.id)
    );
  }
  if (sort === "draftState") {
    return (
      DRAFT_STATE_ORDER[left.draftState] -
        DRAFT_STATE_ORDER[right.draftState] ||
      compareEntityIdentity(left, right)
    );
  }
  return compareEntityIdentity(left, right);
}

function compareBrowserItemsForDisplay(
  left: ProjectBrowserItem,
  right: ProjectBrowserItem,
  locale: Locale,
): number {
  const leftDisplay = moduleEntityDisplay(left, locale);
  const rightDisplay = moduleEntityDisplay(right, locale);
  return (
    compareText(leftDisplay.title, rightDisplay.title) ||
    compareText(left.object_id, right.object_id) ||
    compareText(left.id, right.id)
  );
}

function compareEntityIdentity(
  left: ModuleEntity,
  right: ModuleEntity,
): number {
  return (
    compareText(left.title, right.title) ||
    compareText(left.objectId, right.objectId) ||
    compareText(left.id, right.id)
  );
}

function searchableText(entity: ModuleEntity): string {
  return normalize(
    [
      entity.title,
      entity.subtitle,
      entity.objectId,
      entity.relativeRoot,
      entity.layout,
      entity.tags.map((tag) => tag.label).join(" "),
      entity.sourceSlots
        .map(
          (source) => `${source.slot} ${source.name} ${source.relative_path}`,
        )
        .join(" "),
    ].join(" "),
  );
}

function compareText(left: string, right: string): number {
  return left.localeCompare(right, undefined, {
    numeric: true,
    sensitivity: "base",
  });
}

function normalize(value: string): string {
  return value.trim().toLowerCase();
}

function cleanDisplayText(value: string): string {
  return value.trim();
}

function normalizeCreateValue(value: string | undefined): string {
  return value?.trim() ?? "";
}

function sanitizeIdentifier(value: string): string {
  const sanitized = value
    .toUpperCase()
    .replace(/[^A-Z0-9]+/g, "_")
    .replace(/^_+|_+$/g, "");
  return sanitized || "OBJECT";
}

function familyTag(objectId: string, family: string): string {
  const prefix = `${sanitizeIdentifier(family)}_`;
  return objectId.startsWith(prefix) ? objectId.slice(prefix.length) : objectId;
}

function renderCreateDefault(
  value: string,
  context: Record<string, string>,
): string {
  let rendered = "";

  for (let index = 0; index < value.length;) {
    const character = value[index];
    const nextCharacter = value[index + 1];

    if (character === "{" && nextCharacter === "{") {
      rendered += "{";
      index += 2;
      continue;
    }
    if (character === "}" && nextCharacter === "}") {
      rendered += "}";
      index += 2;
      continue;
    }
    if (character === "{") {
      const closingBrace = value.indexOf("}", index + 1);
      if (closingBrace >= 0) {
        const key = value.slice(index + 1, closingBrace);
        if (/^[a-z_]+$/.test(key)) {
          rendered += context[key] ?? value.slice(index, closingBrace + 1);
          index = closingBrace + 1;
          continue;
        }
      }
    }

    rendered += character;
    index += 1;
  }

  return rendered;
}

function templateMatchesFamily(
  template: ProjectTemplate,
  family: string,
): boolean {
  const cleanFamily = canonicalFamilyId(family);
  return [template.family, template.family_id].some(
    (candidate) =>
      typeof candidate === "string" &&
      canonicalFamilyId(candidate) === cleanFamily,
  );
}
