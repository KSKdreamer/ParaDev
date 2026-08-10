import type { LucideIcon } from "lucide-react";
import type { TranslationKey } from "./i18n";

export type ThemeName = "light" | "dark" | "anthropic";

export type RailItem = {
  id: string;
  labelKey: TranslationKey;
  icon: LucideIcon;
};

export type ModuleStatus = "ready" | "scaffold" | "planned" | "offline";

export type FeatureModule = {
  id: string;
  diagram?: ProjectDiagramCapability;
  groupKey?: TranslationKey;
  titleKey?: TranslationKey;
  label?: string;
  descriptionKey?: TranslationKey;
  status: ModuleStatus;
  count?: number;
};

export type PanelOption = {
  id: string;
  groupKey?: TranslationKey;
  titleKey?: TranslationKey;
  label?: string;
  count?: number;
};

export type WorkspaceTab = {
  id: string;
  dirty?: boolean;
  familyId?: string;
  titleKey?: TranslationKey;
  title?: string;
  subtitleKey?: TranslationKey;
  kind: "module" | "diagram" | "surface" | "config";
  pinned?: boolean;
};

export type WorkspaceModuleSelectionTarget = {
  entityId: string;
  familyId: string;
  sourceContent?: string;
  sourcePath?: string;
};

export type AiOperationIntentSource = {
  detail?: string;
  entityId?: string;
  familyId?: string;
  kind: string;
  label?: string;
  moduleId?: string;
  path?: string;
  relativePath?: string;
  sourcePath?: string;
};

export type AiOperationIntent = {
  nonce: number;
  operationId: string;
  role: string;
  sources: AiOperationIntentSource[];
};

export type ModuleCreateIntent = {
  ai?: AiOperationIntent;
  familyId: string;
  mode?: "batch" | "collection" | "single" | "source-update";
  nonce: number;
};

export type BootProgressState = {
  label: string;
  detail: string;
  status?: "error" | "normal";
  value: number;
};

export type ProjectOption = {
  /** Path-backed identity for selecting one concrete checkout in the desktop shell. */
  id: string;
  /** Logical project identity declared by the project's manifest. */
  projectId: string;
  name: string;
  path: string;
  descriptor?: ProjectDescriptor;
  version?: string;
  game?: string;
  preferredLanguage?: string;
  manifest?: string;
  sourceRoots?: string[];
  outputRoot?: string;
  buildRoot?: string;
  status?: ModuleStatus;
};

export type ProjectDescriptor = Record<string, string | string[]>;

export type SurfaceRow = {
  id: string;
  titleKey: TranslationKey;
  runtime: string;
  status: ModuleStatus;
  path: string;
};

export type ProjectBrowserSource = {
  slot: string;
  slot_kinds?: string[];
  name: string;
  path: string;
  relative_path: string;
  extension: string;
  exists?: boolean;
  size?: number;
  mtime_ns?: string;
};

export type ProjectBrowserResourceSlot = {
  name: string;
  match: string;
  required: boolean;
  many: boolean;
  regex: boolean;
  kind?: string;
  shared: boolean;
  authoring_path?: string;
};

export type ProjectBrowserItem = {
  id: string;
  kind: "module" | "collection" | "source_folder";
  layout: "canonical" | "family_root";
  family_id: string;
  family: string;
  object_id: string;
  module_id?: string;
  collection_id?: string;
  title: string;
  localized_titles?: Record<string, string>;
  title_keys?: string[];
  root: string;
  relative_root: string;
  source_root?: string;
  source_root_relative_path?: string;
  source_count: number;
  sources: ProjectBrowserSource[];
  image_targets?: ProjectBrowserSource[];
  resource_slots?: ProjectBrowserResourceSlot[];
  metadata?: Record<string, unknown>;
  active?: boolean;
};

export type ProjectBrowserFamily = {
  id: string;
  family: string;
  title: string;
  group?: "country" | "military" | "world" | "events" | "shared" | "other";
  aliases?: string[];
  title_key?: string;
  visible?: boolean;
  item_count: number;
  source_count: number;
  layouts: string[];
  resource_slots?: ProjectBrowserResourceSlot[];
  diagram?: ProjectDiagramCapability;
};

export type ProjectBrowserGroup = {
  id: string;
  family: string;
  item_count: number;
  module_count: number;
  collection_count: number;
};

export type ProjectDiagramCapability = {
  id: string;
  aliases: string[];
  renderer: string;
  title: string;
  editable: boolean;
  authoring_kind?: string;
  scope_authoring_kind?: string;
  selection_defaults?: ProjectDiagramSelectionDefault[];
  node_authoring?: ProjectDiagramNodeAuthoring;
  relationships?: ProjectDiagramRelationship[];
  initial_scope?: "project" | "selected-entity";
  show_when_source_hidden?: boolean;
};

export type ProjectDiagramRelationship = {
  kind: string;
  label: string;
  visual_kind: "dependency" | "path" | "reference" | "tree";
  selected_endpoint: "source" | "target";
  owner_endpoint: "source" | "target";
  symmetric: boolean;
  cardinality: "many" | "one";
};

export type ProjectDiagramSelectionDefault = {
  field: string;
  source: string;
  offset?: number;
  template?: string;
};

export type ProjectDiagramNodeAuthoring = {
  title: string;
  description: string;
  fields: ProjectDiagramNodeField[];
  selection_defaults: ProjectDiagramSelectionDefault[];
  requires_selection: boolean;
};

export type ProjectDiagramNodeField = {
  name: string;
  label: string;
  kind: "boolean" | "number" | "text" | "textarea";
  required: boolean;
  default?: string | number | boolean;
  description?: string;
  advanced?: boolean;
};

export type ProjectBrowserPayload = {
  schema: "paradev.sdk.project-browser.v1";
  project_id: string;
  title: string;
  root: string;
  profile: string;
  filters: Record<string, string>;
  families: ProjectBrowserFamily[];
  groups?: ProjectBrowserGroup[];
  items: ProjectBrowserItem[];
  diagnostics: Array<Record<string, unknown>>;
};

export type ProjectTemplateScalar = string | number | boolean;

export type ProjectTemplateArg = {
  required: boolean;
  default: ProjectTemplateScalar;
  advanced: boolean;
  type?: string;
  label?: string;
  description?: string;
  description_source?: "declared" | "generated" | string;
  choices?: ProjectTemplateScalar[];
  reference?: ProjectTemplateArgReference;
};

export type ProjectTemplateArgReference = {
  kind: "module" | "collection";
  family: string;
};

export type ProjectTemplateFormField = ProjectTemplateArg & {
  name: string;
  target: "values" | string;
  label: string;
};

export type ProjectTemplate = {
  id: string;
  title: string;
  family: string;
  family_id?: string;
  kind?: "module" | "collection";
  source: "builtin" | "project" | string;
  directory?: string;
  authoring_ready?: boolean;
  diagnostic_codes?: string[];
  args: Record<string, ProjectTemplateArg>;
  form?: {
    fields: ProjectTemplateFormField[];
  };
  files: string[];
};

export type ProjectTemplateSourceRoot = {
  path: string;
  relative_path: string;
  default: boolean;
};

export type ProjectTemplatesPayload = {
  schema: "paradev.sdk.templates.v1";
  project_id: string;
  profile: string;
  preferred_language?: string;
  source_roots?: ProjectTemplateSourceRoot[];
  templates: ProjectTemplate[];
};

export type CatalogMutationPayload =
  | {
      schema: "paradev.hb.catalog-mutation.v1";
      status: "applied";
      code: "catalog.mutation.applied";
      database: string;
    }
  | {
      schema: "paradev.hb.catalog-mutation.v1";
      status: "not_configured";
      code: "catalog.mutation.not_configured";
      database: string;
    }
  | {
      schema: "paradev.hb.catalog-mutation.v1";
      status: "failed";
      code: "catalog.mutation.failed";
      database: string;
      message: string;
    };

export type CatalogMutationUnverifiedPayload = {
  schema: "paradev.desktop.catalog-mutation-unverified.v1";
  status: "unverified";
  code: "catalog.mutation.unverified";
  message: string;
};

export type CatalogMutationResult =
  CatalogMutationPayload | CatalogMutationUnverifiedPayload;

export type ModuleScaffoldPlan = {
  schema: "paradev.sdk.module_scaffold.v1";
  project_id: string;
  template_id: string;
  family: string;
  object_id: string;
  module_id: string;
  source_root?: string;
  root: string;
  folder_name?: string;
  values: Record<string, string>;
  blocked: boolean;
  written: boolean;
  diagnostics: Array<Record<string, unknown>>;
  files: ModuleScaffoldFile[];
  catalog_mutation?: CatalogMutationResult;
};

export type ModuleScaffoldFile = {
  path: string;
  relative_path: string;
  module_path: string;
  action: "create" | "exists" | "overwrite" | "blocked";
};

export type SourceTextEdit = {
  path: string;
  text: string;
  expectedSize?: number;
  expectedMtimeNs?: string;
};

export type SourceRemoval = {
  path: string;
  expectedSize?: number;
  expectedMtimeNs?: string;
};

export type SourceFormText =
  string | ({ default: string } & Record<string, string>);

export type SourceFormScalar = string | number | boolean;

export type JsonSourceFormPatch = {
  op: "replace-json-scalar";
  path: Array<string | number>;
};

export type PdxSourceFormPathSegment = {
  key: string;
  occurrence: number;
};

export type PdxSourceFormPatch = {
  op: "replace-pdx-scalar";
  path: PdxSourceFormPathSegment[];
  span: {
    start: number;
    end: number;
  };
  expected: string;
  scalar_kind: "boolean" | "identifier" | "number" | "string";
  source_length: number;
};

export type PdxIntegerListSourceFormPatch = {
  op: "replace-pdx-integer-list";
  path: PdxSourceFormPathSegment[];
  span: {
    start: number;
    end: number;
  };
  expected: string;
  item_kind: "integer";
  columns: number;
  minimum: number;
  layout: {
    prefix: string;
    column_separator: string;
    row_separator: string;
    suffix: string;
  };
  source_length: number;
};

export type PdxBlockBodySourceFormPatch = {
  op: "replace-pdx-block-body";
  path: PdxSourceFormPathSegment[];
  span: {
    start: number;
    end: number;
  };
  expected: string;
  layout: {
    prefix: string;
    line_prefix: string;
    suffix: string;
  };
  source_length: number;
};

export type LocSourceFormPatch = {
  op: "replace-loc-text";
  path: {
    language: string;
    key: string;
    occurrence: number;
  };
  span: {
    start: number;
    end: number;
  };
  expected: string;
  style: "inline" | "section" | "yaml";
  newline: "\n" | "\r\n";
  source_length: number;
};

export type SourceFormPatch =
  | JsonSourceFormPatch
  | LocSourceFormPatch
  | PdxBlockBodySourceFormPatch
  | PdxIntegerListSourceFormPatch
  | PdxSourceFormPatch;

export type SourceFormChoice = {
  label: SourceFormText;
  value: SourceFormScalar;
};

type SourceFormControlBase = {
  id: string;
  label: SourceFormText;
  description?: SourceFormText;
  description_source?: "declared" | "generated";
};

type SourceFormReadonlyControl = SourceFormControlBase & {
  control: "readonly";
  value: SourceFormScalar;
  patch?: never;
  choices?: never;
  min?: never;
  max?: never;
  step?: never;
  placeholder?: never;
};

type SourceFormTextControl = SourceFormControlBase & {
  control: "text";
  value: string;
  patch: SourceFormPatch;
  multiline?: boolean;
  choices?: never;
  min?: never;
  max?: never;
  step?: never;
  placeholder?: SourceFormText;
};

type SourceFormNumberControl = SourceFormControlBase & {
  control: "number";
  value: number;
  patch: SourceFormPatch;
  choices?: never;
  min?: number;
  max?: number;
  step?: number;
  placeholder?: SourceFormText;
};

type SourceFormBooleanControl = SourceFormControlBase & {
  control: "boolean";
  value: boolean;
  patch: SourceFormPatch;
  choices?: never;
  min?: never;
  max?: never;
  step?: never;
  placeholder?: never;
};

type SourceFormChoiceControl = SourceFormControlBase & {
  control: "choice";
  value: SourceFormScalar;
  patch: SourceFormPatch;
  choices: SourceFormChoice[];
  min?: never;
  max?: never;
  step?: never;
  placeholder?: SourceFormText;
};

export type SourceFormControl =
  | SourceFormReadonlyControl
  | SourceFormTextControl
  | SourceFormNumberControl
  | SourceFormBooleanControl
  | SourceFormChoiceControl;

export type SourceFormSection = {
  id: string;
  label: SourceFormText;
  description?: SourceFormText;
  controls?: SourceFormControl[];
  sections?: SourceFormSection[];
};

export type SourceFormPayload = {
  schema: "paradev.source-form.v1";
  contract: string;
  project_id: string;
  family: string;
  module_id: string;
  path: string;
  relative_path: string;
  module_relative_path: string;
  source_root: string;
  source_format: "json" | "loc" | "pdx";
  label?: SourceFormText;
  description?: SourceFormText;
  query?: string;
  coverage?: {
    truncated: boolean;
    shown_controls: number;
    total_controls: number;
  };
  sections: SourceFormSection[];
};

export type ReadProjectSourceFormRequest = {
  projectId: string;
  projectRoot: string;
  sourcePath: string;
  text: string;
  query?: string;
};

export type SourceFormUpdateRequest = {
  sourcePath: string;
  values: Record<string, SourceFormScalar>;
  /** Optional unsaved Code-mode source used as the Registry update base. */
  text?: string;
  /** Optional bounded query used to resolve a control outside the default window. */
  query?: string;
};

export type PlanProjectSourceFormUpdatesRequest = {
  projectId: string;
  projectRoot: string;
  updates: SourceFormUpdateRequest[];
};

export type SourceFormUpdateChange = {
  controlId: string;
  previous: SourceFormScalar;
  value: SourceFormScalar;
};

export type SourceFormUpdatePlan = {
  schema: "paradev.source-form-update.v1";
  projectId: string;
  family: string;
  moduleId: string;
  path: string;
  relativePath: string;
  sourceFormat: "json" | "loc" | "pdx";
  formContract: string;
  changed: boolean;
  changes: SourceFormUpdateChange[];
  sourceEdit: SourceTextEdit;
};

export type SourceFormUpdateBatchPlan = {
  schema: "paradev.source-form-update-batch.v1";
  projectId: string;
  changed: boolean;
  counts: {
    requested: number;
    changed: number;
    unchanged: number;
  };
  updates: SourceFormUpdatePlan[];
  sourceEdits: SourceTextEdit[];
};

export type ProjectLocalizationDraft = {
  sourcePath: string;
  text: string;
};

export type ProjectLocalizationWorkspaceRequest = {
  projectId: string;
  projectRoot: string;
  targetKind: "module" | "collection";
  targetId: string;
  family?: string;
  sourceRoot?: string;
  drafts?: ProjectLocalizationDraft[];
  limit?: number;
};

export type ProjectLocalizationOperation =
  | {
      op: "set";
      language: string;
      key: string;
      value: string;
      source_path?: string;
    }
  | {
      op: "add";
      key?: string;
      languages?: string[];
      source_path?: string;
    }
  | { op: "rename"; key: string; new_key: string }
  | { op: "remove"; key: string };

export type PlanProjectLocalizationUpdateRequest =
  ProjectLocalizationWorkspaceRequest & {
    operation: ProjectLocalizationOperation;
  };

export type ProjectLocalizationCell = {
  text: string;
  source_path: string;
  relative_path: string;
  slot: string;
  occurrence: number;
};

export type ProjectLocalizationWorkspace = {
  schema: "paradev.localization-workspace.v2";
  project_id: string;
  target: {
    kind: "module" | "collection";
    id: string;
    family: string;
    object_id: string;
  };
  source_root: string;
  languages: string[];
  rows: Array<{
    key: string;
    values: Record<string, ProjectLocalizationCell>;
  }>;
  sources: Array<{
    path: string;
    relative_path: string;
    unit_relative_path: string;
    slot: string;
    source_format: "ini" | "yaml";
    languages: string[];
    size: number;
    mtime_ns: string;
  }>;
  coverage: {
    truncated: boolean;
    shown_rows: number;
    total_rows: number;
  };
};

export type ProjectLocalizationUpdatePlan = {
  schema: "paradev.localization-update-plan.v2";
  project_id: string;
  target: ProjectLocalizationWorkspace["target"];
  source_root: string;
  operation: ProjectLocalizationOperation;
  changed: boolean;
  changes: Array<Record<string, unknown>>;
  source_edits: Array<{
    path: string;
    text: string;
    expected_size: number;
    expected_mtime_ns: string;
  }>;
  workspace: ProjectLocalizationWorkspace;
};

export type ModuleBatchEdit = {
  module_id: string;
  relative_path: string;
  text: string;
  source_root?: string;
  create?: boolean;
  encoding?: string;
};

export type ModuleBatchRequestTarget = {
  edit_index: number;
  module_id: string;
  family: string;
  object_id: string;
  relative_path: string;
  target_relative_path: string;
  exists: boolean;
  created: boolean;
  changed: boolean;
  create: boolean;
  encoding: string;
  size_bytes: number;
  source_root?: string;
};

export type ModuleBatchRequestPayload = {
  schema: "paradev.module.batch_edit_request.v1";
  project_id: string;
  create: boolean;
  encoding: string;
  edit_count: number;
  summary: {
    edit_count: number;
    module_count: number;
    source_root_count: number;
    existing_target_count: number;
    missing_target_count: number;
    changed_target_count: number;
    unchanged_target_count: number;
    create_enabled_count: number;
    encoding_count: number;
  };
  edits: ModuleBatchEdit[];
  index: Record<string, Record<string, number[]>>;
  targets: ModuleBatchRequestTarget[];
  target_index: Record<string, Record<string, number[]>>;
};

export type SourceReplacementTargetFormat =
  "dds" | "tga" | "jpg" | "jpeg" | "webp" | "bmp";

export type SourceReplacement = {
  path: string;
  contentBase64: string;
  contentFormat?: "png";
  targetFormat?: SourceReplacementTargetFormat;
  expectedSize?: number;
  expectedMtimeNs?: string;
  expectedAbsent?: boolean;
};

export type DraftApplyFile = {
  path: string;
  relative_path: string;
  operation: "write_text" | "remove_file" | "replace_bytes" | string;
  encoding?: "utf-8" | string;
};

export type DraftApplyPayload = {
  schema: "paradev.rest.draft_apply.v1";
  project_id: string;
  written: boolean;
  files: DraftApplyFile[];
  catalog_mutation?: CatalogMutationResult;
  module_rename?: {
    schema: "paradev.module.rename.v1";
    project_id: string;
    previous_module_id: string;
    module_id: string;
    family: string;
    previous_root: string;
    root: string;
    previous_relative_path: string;
    relative_path: string;
    content_rewritten: boolean;
    module: Record<string, unknown>;
    catalog_mutation: CatalogMutationResult;
  };
};

export type ProjectSourceTextPayload = {
  schema: "paradev.rest.source_text.v1";
  project_id: string;
  path: string;
  relative_path: string;
  encoding: "utf-8";
  size: number;
  mtime_ns: string;
  text: string;
};

export type ModuleDraftPayload = {
  schema: "paradev.rest.module_draft.v1";
  project_id: string;
  family_id: string;
  draft_id: string;
  plan: ModuleScaffoldPlan;
};

export type PdxLspPosition = {
  line: number;
  character: number;
  offset: number;
};

export type PdxLspCompletionRequest = {
  text: string;
  line: number;
  character: number;
  offset?: number;
  uri?: string;
  path?: string;
  projectPath?: string;
  database?: string;
  gameRoot?: string;
  limit?: number;
};

export type PdxLspCompletionItem = {
  label: string;
  kind?: number;
  detail?: string;
  documentation?: string | { kind?: string; value?: string };
  data?: Record<string, unknown>;
};

export type PdxLspCompletionPayload = {
  schema: "paradev.lsp.completion.v1";
  method: "textDocument/completion";
  ok: boolean;
  prefix: string;
  isIncomplete: boolean;
  items: PdxLspCompletionItem[];
  diagnostics: Array<Record<string, unknown>>;
};

export type PdxLspSemanticTokensRequest = {
  text: string;
  uri?: string;
  path?: string;
};

export type PdxLspSemanticToken = {
  line: number;
  character: number;
  length: number;
  token_type: string;
  token_modifiers: string[];
};

export type PdxLspSemanticTokensPayload = {
  schema: "paradev.lsp.semantic-tokens.v1";
  method: "textDocument/semanticTokens/full";
  ok: boolean;
  legend: {
    tokenTypes: string[];
    tokenModifiers: string[];
  };
  data: number[];
  tokens: PdxLspSemanticToken[];
  diagnostics: Array<Record<string, unknown>>;
};

export type DesktopProjectRow = {
  id?: string;
  project_id: string;
  title: string;
  game: string;
  preferred_language?: string;
  root: string;
  manifest: string;
  source_roots: string[];
  descriptor?: ProjectDescriptor;
  version?: string;
  output_root?: string;
  build_root?: string;
  status?: ModuleStatus;
};

export type DesktopStatePayload = {
  schema: "paradev.desktop.state.v1";
  projects: DesktopProjectRow[];
  active_project: DesktopProjectRow | null;
  browser: ProjectBrowserPayload | null;
  templates: ProjectTemplatesPayload | null;
  diagnostics: Array<Record<string, unknown>>;
};
