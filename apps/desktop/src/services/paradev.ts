import type {
  FrontendApiJsonRequestInit,
  FrontendApiRestRequestPlan,
} from "../data/frontendApi";
import { projectOptions } from "../data/shell";
import {
  PARADEV_DESKTOP_AI_CHAT_PROFILES,
  PARADEV_DESKTOP_AI_CHAT_SOURCE_KIND_ROWS,
  PARADEV_DESKTOP_AI_CHAT_SOURCE_KINDS,
} from "../generated/desktopContract";
import type { ParaDevFrontendApiOperationId } from "../generated/frontendApi";
import type { TranslationKey } from "../i18n";
import type { OpenPathTarget } from "../openPathTargets";
import type {
  CatalogMutationPayload,
  CatalogMutationResult,
  DesktopProjectRow,
  DesktopStatePayload,
  DraftApplyPayload,
  ModuleBatchEdit,
  ModuleBatchRequestPayload,
  ModuleDraftPayload,
  PdxLspCompletionPayload,
  PdxLspCompletionRequest,
  PdxLspSemanticTokensPayload,
  PdxLspSemanticTokensRequest,
  PlanProjectSourceFormUpdatesRequest,
  PlanProjectLocalizationUpdateRequest,
  ProjectBrowserPayload,
  ProjectLocalizationOperation,
  ProjectLocalizationUpdatePlan,
  ProjectLocalizationWorkspace,
  ProjectLocalizationWorkspaceRequest,
  ProjectSourceTextPayload,
  ReadProjectSourceFormRequest,
  SourceFormChoice,
  SourceFormControl,
  SourceFormPayload,
  SourceFormPatch,
  SourceFormScalar,
  SourceFormSection,
  SourceFormText,
  SourceFormUpdateBatchPlan,
  SourceFormUpdateChange,
  SourceFormUpdatePlan,
  SourceFormUpdateRequest,
  SourceReplacement,
  SourceRemoval,
  SourceTextEdit,
} from "../types";
export type { OpenPathTarget } from "../openPathTargets";

export type ParaDevRequestOptions = {
  signal?: AbortSignal;
};

export type LoadDesktopStateOptions = {
  includeBrowser?: boolean;
};

export type ProjectPackageCatalogRow = {
  id: string;
  label: string;
  game: string;
  archive_name: string;
  archive_sha256: string;
  archive_size: number;
  project_id: string;
  project_version: string;
  top_level_folder: string;
  entry_count: number;
  file_count: number;
  directory_count: number;
  uncompressed_size: number;
  compressed_size: number;
  max_member_path_code_units: number;
};

export type ProjectPackageInstallPayload = {
  schema: "paradev.desktop.project-package-install.v1";
  status: "installed" | "existing";
  installed: boolean;
  project_root: string;
  package: ProjectPackageCatalogRow;
  project: DesktopProjectRow;
};

export type LoadProjectBrowserRequest = {
  projectRoot: string;
  family?: string | null;
  moduleId?: string | null;
  collectionId?: string | null;
  summary?: boolean;
};

export type ModuleDiagramNode = {
  id: string;
  compiled_id?: string | null;
  tree_id?: string;
  folder?: string | null;
  x?: number | null;
  y?: number | null;
  source_path: string;
  source_revision?: string;
  definition_source_revision?: string;
  diagram_source_path?: string;
  editable?: boolean;
  source_span?: Record<string, number>;
  kind?: string;
  module_id?: string | null;
  organization_id?: string;
  trait_id?: string;
  name_key?: string;
  localized_titles?: Record<string, string>;
  localized_descriptions?: Record<string, string>;
  image_path?: string;
  token?: string;
  icon?: string;
  position?: {
    x: number;
    y: number;
  };
  relative_position_id?: string;
  any_parent_ids?: string[];
  all_parent_ids?: string[];
  mutually_exclusive_ids?: string[];
};

export type ModuleDiagramEdge = {
  id: string;
  kind: string;
  source: string;
  target: string;
  owner_id?: string;
  organization_id?: string;
  source_path?: string;
  source_paths?: string[];
  source_revision?: string;
  tree_id?: string;
  owner_ids?: string[];
  relation_groups?: Array<{
    owner_id: string;
    group_index: number;
  }>;
  declaration_count?: number;
  editable?: boolean;
};

export type ModuleDiagramTree = {
  id: string;
  source_path: string;
  source_revision: string;
  node_count: number;
  edge_count: number;
  editable: boolean;
  source_span?: Record<string, number>;
};

export type ModuleDiagramPayload = {
  schema: "paradev.sdk.module_diagram.v1";
  provider_schema: string;
  project_id: string;
  project_root: string;
  profile: string;
  family: string;
  source_kind: string;
  editable: boolean;
  sources?: Array<{
    path: string;
    source_revision: string;
    sha256: string;
    size: number;
  }>;
  module_id?: string | null;
  module_ids?: string[];
  organizations?: Array<Record<string, unknown>>;
  trees?: ModuleDiagramTree[];
  traits?: ModuleDiagramNode[];
  nodes: ModuleDiagramNode[];
  edges: ModuleDiagramEdge[];
  diagnostics: Array<Record<string, unknown>>;
  summary: Record<string, unknown>;
};

export type TechnologyModuleDiagramPositionIntent = {
  technology_id: string;
  x: number;
  y: number;
  source_revision: string;
};

export type FocusTreeModuleDiagramPositionIntent = {
  focus_id: string;
  x: number;
  y: number;
  source_revision: string;
};

export type DoctrineModuleDiagramPositionIntent = {
  doctrine_id: string;
  x: number;
  y: number;
  source_revision: string;
};

export type MioModuleDiagramPositionIntent = {
  organization_id: string;
  trait_id: string;
  x: number;
  y: number;
  source_revision: string;
};

export type GenericModuleDiagramPositionIntent = {
  node_id: string;
  x: number;
  y: number;
  source_revision: string;
};

export type ModuleDiagramPositionIntent =
  | TechnologyModuleDiagramPositionIntent
  | FocusTreeModuleDiagramPositionIntent
  | DoctrineModuleDiagramPositionIntent
  | MioModuleDiagramPositionIntent
  | GenericModuleDiagramPositionIntent;

export type TechnologyModuleDiagramEdgeIntent = {
  kind: "dependency" | "path";
  source_id: string;
  target_id: string;
  present: boolean;
  source_revision: string;
};

export type FocusTreeModuleDiagramEdgeIntent = {
  kind: "prerequisite" | "mutually_exclusive";
  source_id: string;
  target_id: string;
  present: boolean;
  source_revision: string;
};

export type DoctrineModuleDiagramEdgeIntent = {
  kind: "path" | "mutually_exclusive";
  source_id: string;
  target_id: string;
  present: boolean;
  source_revision: string;
};

export type MioModuleDiagramEdgeIntent = {
  kind:
    "relative_position" | "any_parent" | "all_parent" | "mutually_exclusive";
  organization_id: string;
  source_id: string;
  target_id: string;
  present: boolean;
  source_revision: string;
};

export type GenericModuleDiagramEdgeIntent = {
  kind: string;
  source_id: string;
  target_id: string;
  present: boolean;
  source_revision: string;
};

export type ModuleDiagramEdgeIntent =
  | TechnologyModuleDiagramEdgeIntent
  | FocusTreeModuleDiagramEdgeIntent
  | DoctrineModuleDiagramEdgeIntent
  | MioModuleDiagramEdgeIntent
  | GenericModuleDiagramEdgeIntent;

export type LoadModuleDiagramRequest = {
  projectRoot: string;
  family: string;
  profile?: string | null;
};

export type EditModuleDiagramRequest = LoadModuleDiagramRequest & {
  positionIntents?: ModuleDiagramPositionIntent[];
  edgeIntents?: ModuleDiagramEdgeIntent[];
  nodeIntents?: Array<Record<string, unknown>>;
  write?: boolean;
  planHash?: string | null;
};

export type ModuleDiagramEditPayload = {
  schema: "paradev.sdk.module_diagram_edit.v1";
  provider_schema: string;
  project_id: string;
  project_root: string;
  profile: string;
  family: string;
  status: "blocked" | "planned" | "unchanged" | "applied";
  plan_hash: string;
  blocked: boolean;
  applied: boolean;
  written: boolean;
  drafts: Array<Record<string, unknown>>;
  source_replacements: Array<Record<string, unknown>>;
  diagnostics: Array<Record<string, unknown>>;
  files: Array<Record<string, unknown>>;
  validation?: Record<string, unknown>;
  catalog_mutation?: CatalogMutationResult;
  created_node_id?: string;
  created_scope_id?: string;
};

export type LoadProjectInspectionRequest = {
  projectRoot: string;
  kind: string;
  filters?: Record<string, unknown>;
};

export type ProjectInspectionPayload = Record<string, unknown> & {
  diagnostics?: Array<Record<string, unknown>>;
  index?: Record<string, unknown>;
  project_id?: string;
  schema?: string;
};

export const PROJECT_CATALOG_QUERY_DEFAULT_LIMIT = 100;
export const PROJECT_CATALOG_QUERY_MAX_LIMIT = 200;
export const PROJECT_CATALOG_QUERY_MAX_HYDRATED_LIMIT = 1;
export const PROJECT_CATALOG_QUERY_MAX_OFFSET = 4_294_967_295;

export type ProjectCatalogQueryRequest = {
  projectRoot: string;
  entity?: string | null;
  targetId?: string | null;
  name?: string | null;
  tag?: string | null;
  limit?: number;
  offset?: number;
  includeData?: boolean;
};

type NormalizedProjectCatalogQueryRequest = {
  projectRoot: string;
  entity?: string;
  targetId?: string;
  name?: string;
  tag?: string;
  limit: number;
  offset: number;
  includeData: boolean;
};

export type ProjectCatalogRow = {
  object_id: string;
  target_id: string;
  target_entity: string;
  name: string;
  desc: string;
  tags: string[];
  active: boolean;
  workspace_id: string;
  data?: Record<string, unknown>;
};

export type ProjectCatalogQueryFilters = {
  entity?: string;
  target_id?: string;
  name?: string;
  tag?: string;
  limit?: number;
  offset?: number;
  include_data?: boolean;
};

export type ProjectCatalogQueryPayload = {
  schema: "paradev.hb.catalog-query.v1";
  project_id: string;
  database: string;
  filters: ProjectCatalogQueryFilters;
  total_count: number;
  filtered_count: number;
  count: number;
  data_included: boolean;
  page: {
    offset: number;
    limit: number;
    has_more: boolean;
    next_offset: number | null;
  };
  rows: ProjectCatalogRow[];
};

export type ProjectCatalogStatusRequest = {
  projectRoot: string;
};

export type ProjectCatalogStatus =
  "present" | "missing" | "incomplete" | "unreadable";

export type ProjectCatalogStatusCode =
  | "catalog.present"
  | "catalog.missing"
  | "catalog.incomplete"
  | "catalog.unreadable";

type ProjectCatalogStatusState =
  | { status: "present"; code: "catalog.present" }
  | { status: "missing"; code: "catalog.missing" }
  | { status: "incomplete"; code: "catalog.incomplete" }
  | { status: "unreadable"; code: "catalog.unreadable" };

export type ProjectCatalogStatusPayload = {
  schema: "paradev.hb.catalog-status.v1";
  project_id: string;
  database: string;
} & ProjectCatalogStatusState;

const projectCatalogStatusRequests = new Map<
  string,
  Promise<ProjectCatalogStatusPayload>
>();

class ProjectCatalogReadinessError extends Error {
  readonly status: ProjectCatalogStatusPayload;

  constructor(status: ProjectCatalogStatusPayload) {
    super(projectCatalogReadinessMessage(status));
    this.name = "ProjectCatalogReadinessError";
    this.status = status;
  }
}

export type ProjectCatalogRefreshRequest = {
  projectRoot: string;
  profile?: string | null;
};

export type ProjectCatalogRefreshPayload = {
  schema: "paradev.hb.catalog-refresh.v1";
  project_id: string;
  game: string;
  profile: string;
  workspace_id: string;
  registered_entities: string[];
  enabled_extensions: Record<string, unknown>;
  preview_counts: Record<string, number>;
  row_counts: Record<string, number>;
  catalog_count: number;
  catalog_counts: Record<string, number>;
  metaschema_entity_count: number;
  ok: boolean;
  database: string;
  removed: string[];
  recovered: string[];
};

export type ProjectBrowserCacheWriteRequest = {
  projectRoot: string;
  payload: ProjectBrowserPayload;
};

export type CreateModuleDraftRequest = {
  projectId: string;
  projectRoot: string;
  familyId: string;
  templateId?: string | null;
  objectId: string;
  values: Record<string, string>;
  write?: boolean;
  force?: boolean;
};

type ModuleCreateBatchSelector =
  | { family: string; template_id?: never; family_or_template?: never }
  | { family?: never; template_id: string; family_or_template?: never }
  | { family?: never; template_id?: never; family_or_template: string };

export type ModuleCreateBatchRow = ModuleCreateBatchSelector & {
  object_id: string;
  values?: Record<string, unknown>;
};

export type CreateModulesRequest = {
  projectId: string;
  projectRoot: string;
  modules: ModuleCreateBatchRow[];
  sourceRoot?: string | null;
  write?: boolean;
  planHash?: string | null;
};

export type ModuleCreateBatchPayload = {
  schema: "paradev.sdk.module_batch.v1";
  project_id: string;
  source_root: string;
  plan_hash: string;
  blocked: boolean;
  applied: boolean;
  written: boolean;
  requested_count: number;
  counts: {
    create: number;
    created: number;
    unchanged: number;
    blocked: number;
  };
  diagnostics: Array<Record<string, unknown>>;
  modules: Array<Record<string, unknown>>;
};

export type ScaffoldCollectionRequest = {
  projectRoot: string;
  templateId: string;
  collectionId: string;
  values: Record<string, string>;
  sourceRoot?: string | null;
  write?: boolean;
  force?: boolean;
  planHash?: string | null;
};

export type CollectionScaffoldPayload = {
  schema: "paradev.sdk.collection_scaffold.v1";
  project_id: string;
  template_id: string;
  kind: "collection";
  family: string;
  object_id: string;
  collection_id: string;
  folder_name: string;
  source_root: string;
  root: string;
  values: Record<string, string>;
  blocked: boolean;
  written: boolean;
  applied?: boolean;
  plan_hash: string;
  diagnostics: Array<Record<string, unknown>>;
  files: Array<Record<string, unknown>>;
  authoring_plan: Record<string, unknown>;
};

export type RenameCollectionRequest = {
  projectRoot: string;
  collectionId: string;
  targetId: string;
  family?: string;
  sourceRoot?: string;
};

export type CollectionRenamePayload = {
  schema: "paradev.collection.rename.v1";
  project_id: string;
  previous_collection_id: string;
  collection_id: string;
  family: string;
  source_root: string;
  previous_root: string;
  root: string;
  previous_relative_path: string;
  relative_path: string;
  content_rewritten: boolean;
  member_count: number;
  members: string[];
  files: Array<Record<string, unknown>>;
  collection: Record<string, unknown>;
  catalog_mutation?: CatalogMutationResult;
};

export type RemoveCollectionRequest = {
  projectRoot: string;
  collectionId: string;
  family?: string;
  sourceRoot?: string;
};

export type CollectionRemovePayload = {
  schema: "paradev.collection.remove.v1";
  project_id: string;
  collection_id: string;
  family: string;
  source_root: string;
  root: string;
  relative_path: string;
  status: "planned" | "blocked" | "removed";
  write: boolean;
  blocked: boolean;
  applied: boolean;
  written: boolean;
  removed: boolean;
  plan_hash: string;
  diagnostics: Array<Record<string, unknown>>;
  files: Array<Record<string, unknown>>;
  members: string[];
  member_files: Array<Record<string, unknown>>;
  counts: {
    members_preserved: number;
    member_metadata_files: number;
    descriptor_files: number;
  };
  collection: Record<string, unknown>;
  catalog_mutation?: CatalogMutationResult;
};

export type ParaDevAiChatModuleBatchRequest = {
  template_id: string;
  object_id: string;
  values: Record<string, string | number | boolean>;
};

export type ParaDevAiChatModuleBatchProposal = {
  schema: "paradev.desktop.ai-chat-proposal.v1";
  operationId: "module.create_batch";
  familyId: string;
  sourceRoot: string;
  requests: ParaDevAiChatModuleBatchRequest[];
  plan: ModuleCreateBatchPayload;
};

export type ParaDevAiChatCollectionScaffoldRequest = {
  template_id: string;
  collection_id: string;
  values: Record<string, string>;
};

export type ParaDevAiChatCollectionScaffoldProposal = {
  schema: "paradev.desktop.ai-chat-proposal.v1";
  operationId: "collection.scaffold";
  familyId: string;
  sourceRoot: string;
  request: ParaDevAiChatCollectionScaffoldRequest;
  plan: CollectionScaffoldPayload;
};

export type ParaDevAiChatSourceFormUpdateRequest = {
  source_path: string;
  module_id: string;
  values: Record<string, SourceFormScalar>;
  control_labels: Record<string, SourceFormText>;
};

export type ParaDevAiChatSourceFormUpdateProposal = {
  schema: "paradev.desktop.ai-chat-proposal.v1";
  operationId: "module.source_form_update_batch";
  familyId: string;
  requests: ParaDevAiChatSourceFormUpdateRequest[];
  plan: SourceFormUpdateBatchPlan;
};

export type ParaDevAiChatProposal =
  | ParaDevAiChatModuleBatchProposal
  | ParaDevAiChatCollectionScaffoldProposal
  | ParaDevAiChatSourceFormUpdateProposal;

export type ApplyProjectDraftRequest = {
  projectId: string;
  projectRoot: string;
  sourceEdits?: SourceTextEdit[];
  sourceRemovals?: Array<string | SourceRemoval>;
  sourceReplacements?: SourceReplacement[];
  moduleRename?: {
    moduleId: string;
    objectId: string;
    sourceRoot?: string;
    title?: string;
  };
};

export type CreateModuleBatchRequest = {
  projectRoot: string;
  edits: ModuleBatchEdit[];
  create?: boolean;
  encoding?: string;
};

export type BinarySourcePayload = {
  schema: "paradev.desktop.binary-source.v1";
  path: string;
  mimeType: string;
  bytes: number[];
};

export type ThumbnailCacheWriteRequest = {
  projectRoot: string;
  cacheKey: string;
  bytes: number[];
};

export type ProjectPreferredLanguageRequest = {
  projectRoot: string;
  preferredLanguage: string;
  write?: boolean;
  planHash?: string;
};

export type ProjectPreferredLanguagePayload = {
  schema: "paradev.project.preferred-language.v1";
  project_id: string;
  manifest: string;
  previous_language: string;
  preferred_language: string;
  changed: boolean;
  written: boolean;
  blocked: boolean;
  diagnostics: Array<Record<string, unknown>>;
  plan_hash: string;
  revision: {
    size: number;
    sha256: string;
  };
  project?: DesktopProjectRow;
};

export type RenameModuleRequest = {
  projectRoot: string;
  moduleId: string;
  objectId: string;
  sourceRoot?: string;
  title?: string;
};

export type DuplicateModuleRequest = {
  projectRoot: string;
  moduleId: string;
  objectId: string;
  sourceRoot?: string;
  destinationSourceRoot?: string;
  identity?: "rewrite" | "preserve";
  write?: boolean;
  planHash?: string;
};

export type SetModuleCollectionRequest = {
  projectRoot: string;
  moduleId: string;
  collectionId?: string | null;
  sourceRoot?: string | null;
};

type ModuleCollectionMutationFile = {
  path: string;
  relative_path: string;
  layer: "visible" | "hidden";
  action: "create" | "update" | "remove";
  before_sha256: string | null;
  after_sha256: string | null;
};

export type ModuleCollectionPayload = {
  schema: "paradev.sdk.module_collection_update.v1";
  project_id: string;
  project_root: string;
  module_id: string;
  family: string;
  source_root: string;
  previous_collection_id: string | null;
  collection_id: string | null;
  changed: boolean;
  blocked: boolean;
  applied: boolean;
  written: boolean;
  status: "planned" | "blocked" | "unchanged" | "updated";
  plan_hash: string;
  diagnostics: Array<Record<string, unknown>>;
  files: ModuleCollectionMutationFile[];
  module?: Record<string, unknown>;
  collection?: Record<string, unknown>;
  catalog_mutation?: CatalogMutationResult;
};

export type SetModuleActiveRequest = {
  projectRoot: string;
  moduleId: string;
  active: boolean;
  sourceRoot?: string | null;
};

export type ModuleActivityPayload = {
  schema: "paradev.sdk.module_activity_update.v1";
  project_id: string;
  project_root: string;
  module_id: string;
  family: string;
  source_root: string;
  previous_active: boolean;
  active: boolean;
  changed: boolean;
  blocked: boolean;
  applied: boolean;
  written: boolean;
  status: "planned" | "blocked" | "unchanged" | "updated";
  plan_hash: string;
  diagnostics: Array<Record<string, unknown>>;
  files: ModuleCollectionMutationFile[];
  module?: Record<string, unknown>;
  catalog_mutation?: CatalogMutationResult;
};

export type ModuleDuplicateIdentity = [number, number];

export type ModuleDuplicateDirectory = {
  relative_path: string;
  target_relative_path: string;
  kind: "directory";
  identity: ModuleDuplicateIdentity;
  mode: number;
  mtime_ns: string;
  action: "copy" | "rename";
};

export type ModuleDuplicateFile = {
  relative_path: string;
  target_relative_path: string;
  kind: "file";
  identity: ModuleDuplicateIdentity;
  mode: number;
  mtime_ns: string;
  size_bytes: number;
  sha256: string;
  target_size_bytes: number;
  target_sha256: string;
  content_rewritten: boolean;
  action: "copy" | "rename" | "rewrite" | "rewrite_and_rename";
};

export type ModuleDuplicateExclusion = {
  relative_path: ".paradev";
  kind: "directory" | "file" | "symlink" | "special";
  identity: ModuleDuplicateIdentity;
  mode: number;
  mtime_ns: string;
  reason: "module_local_system_tree";
  action: "exclude";
};

export type ModuleDuplicateTotals = {
  directory_count: number;
  file_count: number;
  excluded_count: number;
  size_bytes: number;
  target_size_bytes: number;
  rewritten_file_count: number;
  renamed_path_count: number;
};

export type ModuleDuplicateSource = {
  module_id: string;
  source_root: string;
  root: string;
  relative_path: string;
  root_identity: ModuleDuplicateIdentity | null;
  modules_identity: ModuleDuplicateIdentity | null;
  family_identity: ModuleDuplicateIdentity | null;
  module_identity: ModuleDuplicateIdentity | null;
  tree_digest: string | null;
  content_digest: string | null;
  identity_rewriter: string | null;
};

export type ModuleDuplicateDestination = {
  module_id: string;
  source_root: string;
  root: string;
  relative_path: string;
  root_identity: ModuleDuplicateIdentity | null;
  modules_identity: ModuleDuplicateIdentity | null;
  family_identity: ModuleDuplicateIdentity | null;
  target_identity: ModuleDuplicateIdentity | null;
  entry_count: number;
  entry_names_digest: string | null;
  content_digest: string | null;
};

export type ModuleDuplicatePayload = {
  schema: "paradev.sdk.module_duplicate.v1";
  project_id: string;
  source_module_id: string;
  module_id: string;
  family: string;
  object_id: string;
  source_root: string;
  destination_source_root: string;
  source_module_root: string;
  root: string;
  source_relative_path: string;
  relative_path: string;
  status: "planned" | "duplicated" | "blocked";
  blocked: boolean;
  applied: boolean;
  written: boolean;
  plan_hash: string;
  identity_mode: "rewrite" | "preserve";
  identity_rewriter: string | null;
  content_rewritten: boolean;
  paths_rewritten: boolean;
  diagnostics: Array<Record<string, unknown>>;
  directories: ModuleDuplicateDirectory[];
  files: ModuleDuplicateFile[];
  exclusions: ModuleDuplicateExclusion[];
  totals: ModuleDuplicateTotals;
  source: ModuleDuplicateSource;
  destination: ModuleDuplicateDestination;
  catalog_mutation?: CatalogMutationResult;
};

export type ModuleRenamePayload = {
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

export type RemoveModuleRequest = {
  projectRoot: string;
  moduleId: string;
  sourceRoot?: string;
};

export type ModuleRemoveCleanupPayload = {
  schema: "paradev.module.remove-cleanup.v1";
  status: "pending";
  code: "module_remove.cleanup_pending";
  path: string;
  relative_path: string;
  message: string;
};

export type ModuleRemovePayload = {
  schema: "paradev.module.remove.v1";
  project_id: string;
  module_id: string;
  family: string;
  source_root: string;
  root: string;
  relative_path: string;
  blocked: boolean;
  removed: boolean;
  diagnostics: Array<Record<string, unknown>>;
  files: Array<Record<string, unknown>>;
  module: Record<string, unknown>;
  catalog_mutation?: CatalogMutationResult;
  cleanup?: ModuleRemoveCleanupPayload;
};

export type ProjectBuildMode = "cached" | "full";

export type ProjectBuildTarget = {
  family?: string | null;
  id: string;
  kind: "module" | "collection" | "family";
};

export type ProjectBuildProgressPayload = {
  current?: string | null;
  detail?: string | null;
  index?: number | null;
  label?: string | null;
  percent?: number | null;
  phase: string;
  total?: number | null;
};

export type ProjectBuildRequest = {
  parallelism?: number | null;
  projectRoot: string;
  mode?: ProjectBuildMode;
  profile?: string | null;
  strictMetadata?: boolean;
  target?: ProjectBuildTarget | null;
};

export type ProjectBuildRunPayload = {
  schema: "paradev.desktop.build-run.v1";
  command?: string[];
  errorPath?: string | null;
  errorSummary?: string | null;
  exitCode?: number | null;
  finishedAtMs?: number | null;
  mode?: ProjectBuildMode;
  outputPath?: string | null;
  progress?: ProjectBuildProgressPayload | null;
  progressPath?: string | null;
  projectRoot?: string;
  runId?: string | null;
  startedAtMs?: number | null;
  status: "idle" | "running" | "completed" | "failed" | "interrupted";
  target?: ProjectBuildTarget | null;
  terminalSequence?: number | null;
};

export type ProjectBuildRunsPayload = {
  schema: "paradev.desktop.build-runs.v1";
  runs: ProjectBuildRunPayload[];
};

export type Hoi4LaunchMode = "steam" | "local";

export type Hoi4LaunchReadinessCode =
  | "generated_descriptor_missing"
  | "launcher_descriptor_missing"
  | "launcher_descriptor_unreadable"
  | "launcher_path_invalid"
  | "launcher_path_mismatch"
  | "launcher_path_missing"
  | "output_not_launcher_visible"
  | "publication_incomplete"
  | "publication_invalid"
  | "ready"
  | "unsupported_game"
  | "whole_project_baseline_missing";

export type Hoi4LaunchReadinessPayload = {
  schema: "paradev.desktop.hoi4-launch-readiness.v1";
  code: Hoi4LaunchReadinessCode;
  game: string;
  outputRoot: string;
  projectId: string;
  projectRoot: string;
  ready: boolean;
  reason: string;
};

export type Hoi4LaunchRequest = {
  projectRoot?: string;
  gameRoot?: string | null;
  mode?: Hoi4LaunchMode;
};

export type Hoi4LaunchPayload = {
  schema: "paradev.desktop.game-launch.v1";
  command: string[];
  game: "hoi4";
  gameRoot: string;
  mode: Hoi4LaunchMode;
  status: "started";
};

export type DesktopDependencyStatus = {
  schema: "paradev.desktop.dependency.v1";
  detail?: string | null;
  id: string;
  installCommand: string[];
  installed: boolean;
  installSupported: boolean;
  label: string;
  path?: string | null;
  status: "ready" | "missing" | "installing" | "error" | "unknown";
  version?: string | null;
};

export type HeavenBaseLlmTestRequest = {
  baseUrl?: string;
  gateway: string;
  keyEnv?: string;
  model: string;
  preset?: string;
  provider: string;
};

export type HeavenBaseLlmTestResultCode =
  "ok" | "empty_response" | "unexpected_response" | "exception" | "unknown";

export type HeavenBaseLlmTestPayload = {
  schema?: "paradev.desktop.llm-test.v1";
  baseUrl?: string | null;
  checkedAt?: string;
  detail?: string;
  gateway: string;
  keySource: string;
  model: string;
  preset: string;
  provider: string;
  resultCode?: HeavenBaseLlmTestResultCode;
  status: "ready" | "warning" | "error" | "unknown";
  testDetail: string;
  testedAt: string;
};

export type ParaDevAiChatRequest = {
  baseUrl?: string;
  gateway: string;
  keyEnv?: string;
  model: string;
  preset?: string;
  provider: string;
  prompt: string;
  projectRoot?: string;
  role?: string;
  sources?: ParaDevAiChatSource[];
};

export type ParaDevAiChatSource = {
  contentChars?: number;
  content?: string;
  detail?: string;
  entityId?: string;
  familyId?: string;
  id?: string;
  kind: string;
  label?: string;
  moduleId?: string;
  path?: string;
  relativePath?: string;
  sourcePath?: string;
  truncated?: boolean;
};

export type ParaDevAiChatOperationCard = {
  id: ParaDevFrontendApiOperationId;
  mutates: boolean;
  rest: string;
  sdk: string;
  summary: string;
  title: string;
};

export type ParaDevAiChatProfile = {
  detail: string;
  detailKey?: TranslationKey;
  id: string;
  label: string;
  labelKey?: TranslationKey;
  operationCards?: readonly ParaDevAiChatOperationCard[];
  operationIds?: readonly ParaDevFrontendApiOperationId[];
  prompt: string;
  promptKey?: TranslationKey;
  sourceKinds: string[];
};

export type ParaDevAiChatProfileWrite = Partial<
  Pick<ParaDevAiChatProfile, "detail" | "label" | "prompt" | "sourceKinds">
>;

export type ParaDevAiChatSourceKindRow = {
  frontendKinds: string[];
  id: string;
  label: string;
  labelKey?: TranslationKey;
};

export type ParaDevAiChatProfilesPayload = {
  schema?: "paradev.desktop.ai-chat-profiles.v1";
  defaultRole: string;
  profiles: ParaDevAiChatProfile[];
  projectRoot: string;
  sourceKindRows?: ParaDevAiChatSourceKindRow[];
  sourceKinds: string[];
};

export type ParaDevAiChatPayload = {
  schema?: "paradev.desktop.ai-chat.v1";
  baseUrl?: string | null;
  checkedAt?: string;
  detail?: string;
  gateway: string;
  keySource: string;
  model: string;
  preset?: string | null;
  projectRoot: string;
  prompt: string;
  provider: string;
  proposal?: ParaDevAiChatProposal;
  reply: string;
  role: string;
  sources: ParaDevAiChatSource[];
  status: "ready" | "warning" | "error" | "unknown";
};

export type DesktopConfigValuePayload = {
  schema: "paradev.desktop.config-value.v1";
  key: string;
  value: unknown;
};

export type DesktopPathStatusPayload = {
  schema: "paradev.desktop.path-status.v1";
  inputPath: string;
  path: string;
  exists: boolean;
  kind: "directory" | "file" | "missing" | "other";
  readable: boolean;
  openable: boolean;
};

function nativeBridgeBaseUrl() {
  if (typeof window !== "undefined") {
    const runtimeConfig = (
      window as Window & {
        __PARADEV_RUNTIME_CONFIG__?: { nativeBridgeBaseUrl?: unknown };
      }
    ).__PARADEV_RUNTIME_CONFIG__;
    const runtimeValue = runtimeConfig?.nativeBridgeBaseUrl;
    if (typeof runtimeValue === "string" && runtimeValue.trim()) {
      const normalized = runtimeValue.trim().replace(/\/+$/, "");
      try {
        if (new URL(normalized).origin === window.location.origin) {
          return normalized;
        }
      } catch {
        // Ignore malformed runtime configuration and continue to the dev fallback.
      }
    }
  }
  const buildValue = import.meta.env.VITE_PARADEV_NATIVE_BRIDGE_URL as
    string | undefined;
  return buildValue?.trim().replace(/\/+$/, "") || "";
}

function hasNativeBridge() {
  return nativeBridgeBaseUrl() !== "";
}

export function hasDesktopBackend() {
  return hasNativeBridge();
}

function fallbackProjectRows(): DesktopProjectRow[] {
  return projectOptions.map((project) => ({
    id: project.id,
    project_id: project.projectId,
    title: project.name,
    game: project.game ?? "hoi4",
    preferred_language: project.preferredLanguage,
    root: project.path,
    manifest: project.manifest ?? `${project.path}/paradev.yaml`,
    source_roots: project.sourceRoots ?? [],
    descriptor: project.descriptor ?? {},
    version: project.version,
    output_root: project.outputRoot ?? `${project.path}/build/mod`,
    build_root: project.buildRoot ?? `${project.path}/.paradev/.cache/build`,
    status: project.status ?? "ready",
  }));
}

function fallbackDesktopState(projectRoot?: string): DesktopStatePayload {
  const projects = fallbackProjectRows();
  const activeProject =
    projects.find((project) => project.root === projectRoot) ??
    projects[0] ??
    null;
  return {
    schema: "paradev.desktop.state.v1",
    projects,
    active_project: activeProject,
    browser: null,
    templates: null,
    diagnostics: [],
  };
}

function fallbackDesktopPathStatus(path: string): DesktopPathStatusPayload {
  const cleanPath = path.trim();
  return {
    schema: "paradev.desktop.path-status.v1",
    inputPath: cleanPath,
    path: cleanPath,
    exists: false,
    kind: "missing",
    readable: false,
    openable: false,
  };
}

export async function loadDesktopState(
  projectRoot?: string,
  options: LoadDesktopStateOptions = {},
): Promise<DesktopStatePayload> {
  if (hasNativeBridge()) {
    return await bridgeGetJson<DesktopStatePayload>(
      "/desktop/state",
      compactBody({
        project_path: projectRoot,
        include_browser: String(options.includeBrowser ?? false),
      }),
    );
  }
  return fallbackDesktopState(projectRoot);
}

export async function loadProjectBrowser(
  request: LoadProjectBrowserRequest,
): Promise<ProjectBrowserPayload> {
  if (hasNativeBridge()) {
    return await bridgeGetJson<ProjectBrowserPayload>(
      "/projects/browser",
      compactBody({
        path: request.projectRoot,
        family: request.family,
        module_id: request.moduleId,
        collection_id: request.collectionId,
        summary: request.summary ? "true" : undefined,
      }),
    );
  }
  throw new Error(
    "Loading scoped project browser data requires the ParaDev desktop application.",
  );
}

export async function loadModuleDiagram(
  request: LoadModuleDiagramRequest,
): Promise<ModuleDiagramPayload> {
  if (hasNativeBridge()) {
    return await bridgeGetJson<ModuleDiagramPayload>(
      "/projects/modules/diagram",
      compactBody({
        path: request.projectRoot,
        family: request.family,
        profile: request.profile,
      }),
    );
  }
  throw new Error(
    "Loading source-backed module diagrams requires the ParaDev desktop application.",
  );
}

export async function editModuleDiagram(
  request: EditModuleDiagramRequest,
): Promise<ModuleDiagramEditPayload> {
  if (hasNativeBridge()) {
    return await bridgePostJson<ModuleDiagramEditPayload>(
      "/projects/modules/diagram/edit",
      compactBody({
        project_root: request.projectRoot,
        family: request.family,
        profile: request.profile,
        position_intents: request.positionIntents ?? [],
        edge_intents: request.edgeIntents ?? [],
        node_intents: request.nodeIntents ?? [],
        write: request.write ?? false,
        plan_hash: request.planHash,
      }),
    );
  }
  throw new Error(
    "Editing source-backed module diagrams requires the ParaDev desktop application.",
  );
}

export async function loadProjectInspection(
  request: LoadProjectInspectionRequest,
): Promise<ProjectInspectionPayload> {
  if (hasNativeBridge()) {
    return await bridgeGetJson<ProjectInspectionPayload>(
      "/projects/inspect",
      compactBody({
        path: request.projectRoot,
        kind: request.kind,
        ...projectInspectionRestFilters(request.filters ?? {}),
      }),
    );
  }
  throw new Error(
    "Loading project inspections requires the ParaDev desktop application.",
  );
}

export async function queryProjectCatalog(
  request: ProjectCatalogQueryRequest,
): Promise<ProjectCatalogQueryPayload> {
  const normalized = normalizeProjectCatalogQueryRequest(request);
  const status = await loadProjectCatalogStatus({
    projectRoot: normalized.projectRoot,
  });
  if (status.code !== "catalog.present") {
    throw new ProjectCatalogReadinessError(status);
  }
  if (hasNativeBridge()) {
    return await bridgeGetJson<ProjectCatalogQueryPayload>(
      "/projects/inspect",
      compactBody({
        path: normalized.projectRoot,
        kind: "catalog-query",
        entity: normalized.entity,
        target_id: normalized.targetId,
        name: normalized.name,
        tag: normalized.tag,
        limit: normalized.limit,
        offset: normalized.offset,
        include_data: normalized.includeData,
      }),
    );
  }
  throw new Error(
    "Querying the project catalog requires the ParaDev desktop application.",
  );
}

export async function loadProjectCatalogStatus(
  request: ProjectCatalogStatusRequest,
): Promise<ProjectCatalogStatusPayload> {
  const normalized = {
    projectRoot: normalizedProjectCatalogRoot(request.projectRoot),
  };
  const activeRequest = projectCatalogStatusRequests.get(
    normalized.projectRoot,
  );
  if (activeRequest) {
    return await activeRequest;
  }
  const pendingRequest = loadProjectCatalogStatusUncached(normalized);
  projectCatalogStatusRequests.set(normalized.projectRoot, pendingRequest);
  try {
    return await pendingRequest;
  } finally {
    if (
      projectCatalogStatusRequests.get(normalized.projectRoot) ===
      pendingRequest
    ) {
      projectCatalogStatusRequests.delete(normalized.projectRoot);
    }
  }
}

export function projectCatalogReadinessFromError(
  error: unknown,
): ProjectCatalogStatusPayload | null {
  return error instanceof ProjectCatalogReadinessError ? error.status : null;
}

export async function refreshProjectCatalog(
  request: ProjectCatalogRefreshRequest,
): Promise<ProjectCatalogRefreshPayload> {
  const normalized = normalizeProjectCatalogRefreshRequest(request);
  if (hasNativeBridge()) {
    return await bridgePutQueryJson<ProjectCatalogRefreshPayload>(
      "/projects/catalog",
      compactBody({
        path: normalized.projectRoot,
        profile: normalized.profile,
      }),
    );
  }
  throw new Error(
    "Refreshing the project catalog requires the ParaDev desktop application.",
  );
}

export async function readProjectBrowserCache(
  projectRoot: string,
): Promise<ProjectBrowserPayload | null> {
  if (hasNativeBridge()) {
    return await bridgeGetJson<ProjectBrowserPayload | null>(
      "/desktop/project-browser-cache",
      { project_root: projectRoot },
    );
  }
  throw new Error(
    "Project browser cache loading requires the ParaDev desktop application.",
  );
}

export async function writeProjectBrowserCache(
  payload: ProjectBrowserPayload,
): Promise<ProjectBrowserPayload> {
  const request: ProjectBrowserCacheWriteRequest = {
    projectRoot: payload.root,
    payload,
  };
  if (hasNativeBridge()) {
    return await bridgePutJson<ProjectBrowserPayload>(
      "/desktop/project-browser-cache",
      request,
    );
  }
  throw new Error(
    "Project browser cache writing requires the ParaDev desktop application.",
  );
}

export async function createModuleDraft(
  request: CreateModuleDraftRequest,
): Promise<ModuleDraftPayload> {
  let payload: unknown;
  if (hasNativeBridge()) {
    payload = await createModuleDraftThroughFrontendApiRest(request);
  } else {
    throw new Error("Creating module drafts requires the ParaDev desktop application.");
  }
  return moduleDraftPayload(payload, request);
}

export async function createModules(
  request: CreateModulesRequest,
): Promise<ModuleCreateBatchPayload> {
  let payload: unknown;
  if (hasNativeBridge()) {
    payload = await createModulesThroughFrontendApiRest(request);
  } else {
    throw new Error(
      "Creating module batches requires the ParaDev desktop application.",
    );
  }
  return moduleCreateBatchPayload(payload, request);
}

export async function scaffoldCollection(
  request: ScaffoldCollectionRequest,
): Promise<CollectionScaffoldPayload> {
  let payload: unknown;
  if (hasNativeBridge()) {
    payload = await scaffoldCollectionThroughFrontendApiRest(request);
  } else {
    throw new Error(
      "Creating collection templates requires the ParaDev desktop application.",
    );
  }
  return collectionScaffoldPayload(payload, request);
}

export async function renameCollection(
  request: RenameCollectionRequest,
): Promise<CollectionRenamePayload> {
  let payload: unknown;
  if (hasNativeBridge()) {
    payload = await renameCollectionThroughFrontendApiRest(request);
  } else {
    throw new Error(
      "Renaming collection folders requires the ParaDev desktop application.",
    );
  }
  return collectionRenamePayload(payload, request);
}

export async function removeCollection(
  request: RemoveCollectionRequest,
): Promise<CollectionRemovePayload> {
  const plan = await requestCollectionRemoval({
    ...request,
    write: false,
  });
  if (plan.blocked) {
    throw new Error(collectionRemoveDiagnostic(plan));
  }
  const applied = await requestCollectionRemoval({
    ...request,
    write: true,
    planHash: plan.plan_hash,
  });
  if (applied.blocked) {
    throw new Error(collectionRemoveDiagnostic(applied));
  }
  return applied;
}

async function requestCollectionRemoval(
  request: RemoveCollectionRequest & {
    write: boolean;
    planHash?: string;
  },
): Promise<CollectionRemovePayload> {
  let payload: unknown;
  if (hasNativeBridge()) {
    payload = await removeCollectionThroughFrontendApiRest(request);
  } else {
    throw new Error(
      "Removing collection folders requires the ParaDev desktop application.",
    );
  }
  return collectionRemovePayload(payload, request);
}

export async function applyProjectDraft(
  request: ApplyProjectDraftRequest,
): Promise<DraftApplyPayload> {
  if (hasNativeBridge()) {
    return await applyProjectDraftThroughFrontendApiRest(request);
  }
  throw new Error("Applying project drafts requires the ParaDev desktop application.");
}

export function sourceDraftRecoveryPathFromError(
  error: unknown,
  projectRoot: string,
): string | null {
  const message =
    error instanceof Error
      ? error.message
      : typeof error === "string"
        ? error
        : String(error);
  if (!/\bSource draft\b[\s\S]*\brecovery\b/i.test(message)) {
    return null;
  }
  try {
    const root = normalizedPayloadPath(
      projectRoot,
      "source draft recovery project root",
      true,
    );
    return joinedPayloadPath(
      root,
      normalizedPayloadPath(
        ".paradev/source-draft-transaction",
        "source draft recovery directory",
        false,
      ),
      "source draft recovery directory",
    ).value;
  } catch {
    return null;
  }
}

export async function createModuleBatchRequest(
  request: CreateModuleBatchRequest,
): Promise<ModuleBatchRequestPayload> {
  if (hasNativeBridge()) {
    return await bridgePostJson<ModuleBatchRequestPayload>(
      "/desktop/modules/batch-request",
      request,
    );
  }
  throw new Error(
    "Creating module batch request previews requires the ParaDev desktop application.",
  );
}

export async function readTextSource(
  projectRoot: string,
  sourcePath: string,
  projectId?: string,
): Promise<string> {
  if (hasNativeBridge()) {
    return await readTextSourceThroughFrontendApiRest(
      projectRoot,
      sourcePath,
      projectId,
    );
  }
  throw new Error("Local source loading requires the ParaDev desktop application.");
}

export async function readProjectSourceForm(
  request: ReadProjectSourceFormRequest,
): Promise<SourceFormPayload | null> {
  const normalized = normalizedSourceFormRequest(request);
  let payload: unknown;
  if (hasNativeBridge()) {
    payload = await readProjectSourceFormThroughFrontendApiRest(normalized);
  } else {
    throw new Error(
      "Loading project source forms requires the ParaDev desktop application.",
    );
  }
  return sourceFormPayload(payload, normalized);
}

export async function planProjectSourceFormUpdates(
  request: PlanProjectSourceFormUpdatesRequest,
): Promise<SourceFormUpdateBatchPlan> {
  const normalized = normalizedSourceFormUpdateBatchRequest(request);
  let payload: unknown;
  if (hasNativeBridge()) {
    payload = await bridgePostJson<unknown>(
      "/desktop/sources/form-updates/plan",
      normalized,
    );
  } else {
    throw new Error(
      "Planning guided project source updates requires the ParaDev desktop application.",
    );
  }
  return sourceFormUpdateBatchPlan(payload, normalized);
}

export async function readProjectLocalizationWorkspace(
  request: ProjectLocalizationWorkspaceRequest,
): Promise<ProjectLocalizationWorkspace> {
  const normalized = normalizedProjectLocalizationRequest(request);
  let payload: unknown;
  if (hasNativeBridge()) {
    payload = await bridgePostJson<unknown>(
      "/desktop/localization/workspace",
      normalized,
    );
  } else {
    throw new Error(
      "Loading project localization requires the ParaDev desktop application.",
    );
  }
  return projectLocalizationWorkspace(payload, normalized);
}

export async function planProjectLocalizationUpdate(
  request: PlanProjectLocalizationUpdateRequest,
): Promise<ProjectLocalizationUpdatePlan> {
  const normalized = normalizedProjectLocalizationUpdateRequest(request);
  let payload: unknown;
  if (hasNativeBridge()) {
    payload = await bridgePostJson<unknown>(
      "/desktop/localization/plan",
      normalized,
    );
  } else {
    throw new Error(
      "Planning project localization updates requires the ParaDev desktop application.",
    );
  }
  return projectLocalizationUpdatePlan(payload, normalized);
}

export async function readBinarySource(
  projectRoot: string,
  sourcePath: string,
): Promise<BinarySourcePayload> {
  if (hasNativeBridge()) {
    return await bridgePostJson<BinarySourcePayload>(
      "/desktop/sources/binary",
      { projectRoot, sourcePath },
    );
  }
  throw new Error("Local source loading requires the ParaDev desktop application.");
}

export async function readThumbnailCache(
  projectRoot: string,
  cacheKey: string,
): Promise<BinarySourcePayload | null> {
  let payload: unknown;
  if (hasNativeBridge()) {
    payload = await bridgeGetJson<unknown>("/desktop/thumbnail-cache", {
      project_root: projectRoot,
      cache_key: cacheKey,
    });
  } else {
    throw new Error(
      "Thumbnail cache loading requires the ParaDev desktop application.",
    );
  }
  return thumbnailCachePayload(payload);
}

export async function writeThumbnailCache(
  request: ThumbnailCacheWriteRequest,
): Promise<BinarySourcePayload> {
  if (hasNativeBridge()) {
    return await bridgePutJson<BinarySourcePayload>(
      "/desktop/thumbnail-cache",
      request,
    );
  }
  throw new Error("Thumbnail cache writing requires the ParaDev desktop application.");
}

export async function renameModule(
  request: RenameModuleRequest,
): Promise<ModuleRenamePayload> {
  let payload: unknown;
  if (hasNativeBridge()) {
    payload = await renameModuleThroughFrontendApiRest(request);
  } else {
    throw new Error(
      "Renaming module folders requires the ParaDev desktop application.",
    );
  }
  return moduleRenamePayload(payload, request);
}

export async function setProjectPreferredLanguage(
  projectRoot: string,
  preferredLanguage: string,
): Promise<ProjectPreferredLanguagePayload> {
  const request = {
    projectRoot,
    preferredLanguage,
    write: false,
  } satisfies ProjectPreferredLanguageRequest;
  const plan = await requestProjectPreferredLanguage(request);
  if (plan.blocked) {
    throw new Error(projectPreferredLanguageDiagnostic(plan));
  }
  const applied = await requestProjectPreferredLanguage({
    ...request,
    write: true,
    planHash: plan.plan_hash,
  });
  if (applied.blocked) {
    throw new Error(projectPreferredLanguageDiagnostic(applied));
  }
  return applied;
}

async function requestProjectPreferredLanguage(
  request: ProjectPreferredLanguageRequest,
): Promise<ProjectPreferredLanguagePayload> {
  let payload: unknown;
  if (hasNativeBridge()) {
    payload = await projectPreferredLanguageThroughFrontendApiRest(request);
  } else {
    throw new Error(
      "Changing the project authoring language requires the ParaDev desktop application.",
    );
  }
  return projectPreferredLanguagePayload(payload, request);
}

export async function duplicateModule(
  request: DuplicateModuleRequest,
): Promise<ModuleDuplicatePayload> {
  let payload: unknown;
  if (hasNativeBridge()) {
    payload = await duplicateModuleThroughFrontendApiRest(request);
  } else {
    throw new Error(
      "Duplicating module folders requires the ParaDev desktop application.",
    );
  }
  return moduleDuplicatePayload(payload, request);
}

export async function setModuleCollection(
  request: SetModuleCollectionRequest,
): Promise<ModuleCollectionPayload> {
  const plan = await requestModuleCollection({
    ...request,
    write: false,
  });
  if (plan.blocked) {
    throw new Error(moduleCollectionDiagnostic(plan));
  }
  const applied = await requestModuleCollection({
    ...request,
    write: true,
    planHash: plan.plan_hash,
  });
  if (applied.blocked) {
    throw new Error(moduleCollectionDiagnostic(applied));
  }
  return applied;
}

async function requestModuleCollection(
  request: SetModuleCollectionRequest & {
    write: boolean;
    planHash?: string;
  },
): Promise<ModuleCollectionPayload> {
  let payload: unknown;
  if (hasNativeBridge()) {
    payload = await moduleCollectionThroughFrontendApiRest(request);
  } else {
    throw new Error(
      "Changing module collection membership requires the ParaDev desktop application.",
    );
  }
  return moduleCollectionPayload(payload, request);
}

export async function setModuleActive(
  request: SetModuleActiveRequest,
): Promise<ModuleActivityPayload> {
  const plan = await requestModuleActivity({
    ...request,
    write: false,
  });
  if (plan.blocked) {
    throw new Error(moduleActivityDiagnostic(plan));
  }
  const applied = await requestModuleActivity({
    ...request,
    write: true,
    planHash: plan.plan_hash,
  });
  if (applied.blocked) {
    throw new Error(moduleActivityDiagnostic(applied));
  }
  return applied;
}

async function requestModuleActivity(
  request: SetModuleActiveRequest & {
    write: boolean;
    planHash?: string;
  },
): Promise<ModuleActivityPayload> {
  let payload: unknown;
  if (hasNativeBridge()) {
    payload = await moduleActivityThroughFrontendApiRest(request);
  } else {
    throw new Error(
      "Changing module activity requires the ParaDev desktop application.",
    );
  }
  return moduleActivityPayload(payload, request);
}

export async function removeModule(
  request: RemoveModuleRequest,
): Promise<ModuleRemovePayload> {
  let payload: unknown;
  if (hasNativeBridge()) {
    payload = await removeModuleThroughFrontendApiRest(request);
  } else {
    throw new Error(
      "Removing module folders requires the ParaDev desktop application.",
    );
  }
  return moduleRemovePayload(payload, request);
}

export async function startProjectBuild(
  request: ProjectBuildRequest,
): Promise<ProjectBuildRunPayload> {
  if (hasNativeBridge()) {
    return await startProjectBuildThroughFrontendApiRest(request);
  }
  throw new Error("Starting project builds requires the ParaDev desktop application.");
}

export async function getProjectBuildRuns(
  projectRoot?: string,
): Promise<ProjectBuildRunsPayload> {
  if (hasNativeBridge()) {
    return await getProjectBuildRunsThroughFrontendApiRest(projectRoot);
  }
  throw new Error(
    "Reading active project builds requires the ParaDev desktop application.",
  );
}

export async function getProjectBuildStatus(
  runId?: string | null,
): Promise<ProjectBuildRunPayload> {
  const normalizedRunId = normalizedBuildRunId(runId);
  if (hasNativeBridge()) {
    return await getProjectBuildStatusThroughFrontendApiRest(normalizedRunId);
  }
  throw new Error(
    "Reading project build status requires the ParaDev desktop application.",
  );
}

export async function interruptProjectBuild(
  runId?: string | null,
): Promise<ProjectBuildRunPayload> {
  const normalizedRunId = normalizedBuildRunId(runId);
  if (hasNativeBridge()) {
    return await interruptProjectBuildThroughFrontendApiRest(normalizedRunId);
  }
  throw new Error(
    "Interrupting project builds requires the ParaDev desktop application.",
  );
}

export async function loadHoi4LaunchReadiness(
  projectRoot: string,
): Promise<Hoi4LaunchReadinessPayload> {
  if (hasNativeBridge()) {
    return await bridgeGetJson<Hoi4LaunchReadinessPayload>(
      "/desktop/hoi4-launch-readiness",
      {
        project_root: projectRoot,
      },
    );
  }
  throw new Error(
    "Checking HOI4 launch readiness requires the ParaDev desktop application.",
  );
}

export async function runHoi4Game(
  request: Hoi4LaunchRequest = {},
): Promise<Hoi4LaunchPayload> {
  if (hasNativeBridge()) {
    return await bridgePostJson<Hoi4LaunchPayload>(
      "/desktop/run-hoi4",
      request,
    );
  }
  throw new Error("Launching HOI4 requires the ParaDev desktop application.");
}

export async function checkDesktopDependency(
  dependencyId: string,
): Promise<DesktopDependencyStatus> {
  if (hasNativeBridge()) {
    return await bridgeGetJson<DesktopDependencyStatus>(
      `/desktop/dependencies/${encodeURIComponent(dependencyId)}`,
    );
  }
  throw new Error(
    "Checking desktop dependencies requires the ParaDev desktop application.",
  );
}

export async function installDesktopDependency(
  dependencyId: string,
): Promise<DesktopDependencyStatus> {
  if (hasNativeBridge()) {
    return await bridgePostJson<DesktopDependencyStatus>(
      `/desktop/dependencies/${encodeURIComponent(dependencyId)}/install`,
      {},
    );
  }
  throw new Error(
    "Installing desktop dependencies requires the ParaDev desktop application.",
  );
}

export async function testHeavenBaseLlmRoute(
  request: HeavenBaseLlmTestRequest,
): Promise<HeavenBaseLlmTestPayload> {
  const body = compactBody({
    provider: request.provider,
    model: request.model,
    gateway: request.gateway,
    preset: request.preset,
    keyEnv: request.keyEnv,
    baseUrl: request.baseUrl,
  });
  if (hasNativeBridge()) {
    const payload = await bridgePostJson<HeavenBaseLlmTestPayload>(
      "/desktop/llm/test",
      body,
    );
    return normalizeHeavenBaseLlmTestPayload(payload, request);
  }
  throw new Error(
    "Testing HeavenBase LLM routes requires the ParaDev desktop application.",
  );
}

export async function chatWithParaDevAi(
  request: ParaDevAiChatRequest,
): Promise<ParaDevAiChatPayload> {
  const body = compactBody({
    provider: request.provider,
    model: request.model,
    gateway: request.gateway,
    preset: request.preset,
    keyEnv: request.keyEnv,
    baseUrl: request.baseUrl,
    prompt: request.prompt,
    role: request.role,
    projectRoot: request.projectRoot,
    sources: request.sources,
  });
  if (hasNativeBridge()) {
    const payload = await chatWithParaDevAiThroughFrontendApiRest(request);
    return normalizeParaDevAiChatPayload(payload, request);
  }
  throw new Error("AI chat requires the ParaDev desktop application.");
}

export async function loadParaDevAiChatProfiles(
  projectRoot = "",
): Promise<ParaDevAiChatProfilesPayload> {
  if (hasNativeBridge()) {
    const payload =
      await loadParaDevAiChatProfilesThroughFrontendApiRest(projectRoot);
    return normalizeParaDevAiChatProfilesPayload(payload, projectRoot);
  }
  return fallbackParaDevAiChatProfilesPayload(projectRoot);
}

export async function writeParaDevAiChatProfile(
  profileId: string,
  profile: ParaDevAiChatProfileWrite,
  projectRoot = "",
): Promise<ParaDevAiChatProfilesPayload> {
  if (hasNativeBridge()) {
    const payload = await writeParaDevAiChatProfileThroughFrontendApiRest(
      profileId,
      profile,
      projectRoot,
    );
    return normalizeParaDevAiChatProfilesPayload(payload, projectRoot);
  }
  throw new Error("Writing AI chat profiles requires the ParaDev desktop application.");
}

export async function resetParaDevAiChatProfile(
  profileId: string,
  projectRoot = "",
): Promise<ParaDevAiChatProfilesPayload> {
  if (hasNativeBridge()) {
    const payload = await resetParaDevAiChatProfileThroughFrontendApiRest(
      profileId,
      projectRoot,
    );
    return normalizeParaDevAiChatProfilesPayload(payload, projectRoot);
  }
  throw new Error(
    "Resetting AI chat profiles requires the ParaDev desktop application.",
  );
}

export async function openProjectPath(
  path: string,
  target: OpenPathTarget,
): Promise<void> {
  if (hasNativeBridge()) {
    await bridgePostJson("/desktop/open-path", { path, target });
    return;
  }
  throw new Error("Opening local paths requires the ParaDev desktop application.");
}

export async function selectProjectPath(): Promise<string | null> {
  if (hasNativeBridge()) {
    const payload = await bridgePostJson<{
      schema: "paradev.desktop.project-selection.v1";
      path: unknown;
    }>("/desktop/select-project");
    if (payload.schema !== "paradev.desktop.project-selection.v1") {
      throw new Error("ParaDev returned an invalid project-selection response.");
    }
    if (payload.path === null) {
      return null;
    }
    if (typeof payload.path !== "string" || !payload.path.trim()) {
      throw new Error("ParaDev returned an invalid project-selection path.");
    }
    return payload.path;
  }
  throw new Error(
    "Selecting a project folder requires the ParaDev desktop application.",
  );
}

export async function importProjectPackage(): Promise<ProjectPackageInstallPayload | null> {
  if (hasNativeBridge()) {
    return projectPackageInstallPayload(
      await bridgePostJson<unknown>("/desktop/import-project-package"),
    );
  }
  throw new Error(
    "Installing a project package requires the ParaDev desktop application.",
  );
}

export async function loadDesktopPathStatus(
  path: string,
): Promise<DesktopPathStatusPayload> {
  if (hasNativeBridge()) {
    return await bridgeGetJson<DesktopPathStatusPayload>(
      "/desktop/path-status",
      { path },
    );
  }
  return fallbackDesktopPathStatus(path);
}

export async function readAppConfig(): Promise<unknown> {
  if (hasNativeBridge()) {
    return await bridgeGetJson<unknown>("/desktop/app-config");
  }
  return null;
}

export async function writeAppConfig(
  config: Record<string, unknown>,
): Promise<void> {
  if (hasNativeBridge()) {
    await bridgePutJson("/desktop/app-config", config);
  }
}

export async function readConfigValue(key: string): Promise<unknown> {
  if (hasNativeBridge()) {
    return configValue(
      await bridgeGetJson<DesktopConfigValuePayload>("/desktop/config-value", {
        key,
      }),
      key,
    );
  }
  throw new Error(
    "Reading ParaDev config values requires the ParaDev desktop application.",
  );
}

export async function writeConfigValue(
  key: string,
  value: unknown,
): Promise<unknown> {
  if (hasNativeBridge()) {
    return configValue(
      await bridgePutJson<DesktopConfigValuePayload>("/desktop/config-value", {
        key,
        value,
      }),
      key,
    );
  }
  throw new Error(
    "Writing ParaDev config values requires the ParaDev desktop application.",
  );
}

export async function requestPdxLspCompletion(
  request: PdxLspCompletionRequest,
  options: ParaDevRequestOptions = {},
): Promise<PdxLspCompletionPayload> {
  return await postJson<PdxLspCompletionPayload>(
    "/lsp/completion",
    lspCompletionBody(request),
    options,
  );
}

export async function requestPdxLspSemanticTokens(
  request: PdxLspSemanticTokensRequest,
  options: ParaDevRequestOptions = {},
): Promise<PdxLspSemanticTokensPayload> {
  return await postJson<PdxLspSemanticTokensPayload>(
    "/lsp/semantic-tokens",
    lspSemanticTokensBody(request),
    options,
  );
}

async function postJson<T>(
  url: string,
  body: Record<string, unknown>,
  options: ParaDevRequestOptions = {},
): Promise<T> {
  const response = await fetch(restUrl(url), {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify(body),
    signal: options.signal,
  });
  if (!response.ok) {
    throw new Error(
      `ParaDev REST request failed: ${response.status} ${response.statusText}`,
    );
  }
  return (await response.json()) as T;
}

async function bridgeGetJson<T>(
  path: string,
  query: Record<string, unknown> = {},
): Promise<T> {
  const response = await fetch(bridgeUrl(path, query), { method: "GET" });
  return await bridgeResponseJson<T>(response);
}

async function bridgePostJson<T>(
  path: string,
  body: Record<string, unknown> = {},
): Promise<T> {
  return await bridgeBodyJson<T>(path, "POST", body);
}

async function bridgePutJson<T>(
  path: string,
  body: Record<string, unknown> = {},
): Promise<T> {
  return await bridgeBodyJson<T>(path, "PUT", body);
}

async function bridgePutQueryJson<T>(
  path: string,
  query: Record<string, unknown> = {},
): Promise<T> {
  const response = await fetch(bridgeUrl(path, query), { method: "PUT" });
  return await bridgeResponseJson<T>(response);
}

async function bridgeDeleteJson<T>(
  path: string,
  query: Record<string, unknown> = {},
): Promise<T> {
  const response = await fetch(bridgeUrl(path, query), { method: "DELETE" });
  return await bridgeResponseJson<T>(response);
}

async function bridgePatchJson<T>(
  path: string,
  body: Record<string, unknown> = {},
): Promise<T> {
  return await bridgeBodyJson<T>(path, "PATCH", body);
}

async function bridgeBodyJson<T>(
  path: string,
  method: "PATCH" | "POST" | "PUT",
  body: Record<string, unknown>,
): Promise<T> {
  const response = await fetch(bridgeUrl(path), {
    body: JSON.stringify(body),
    headers: { "content-type": "application/json" },
    method,
  });
  return await bridgeResponseJson<T>(response);
}

async function frontendApiRequestJson<T>(
  request: FrontendApiJsonRequestInit,
): Promise<T> {
  const response = await fetch(restUrl(request.url), request.init);
  return await bridgeResponseJson<T>(response);
}

async function renameModuleThroughFrontendApiRest(
  request: RenameModuleRequest,
): Promise<ModuleRenamePayload> {
  const {
    buildFrontendApiRestExecutionRequest,
    buildFrontendApiRestPlanRequest,
  } = await import("../data/frontendApi");
  const plan = await frontendApiRequestJson<FrontendApiRestRequestPlan>(
    buildFrontendApiRestPlanRequest(
      "module.rename",
      renameModuleFrontendApiValues(request),
    ),
  );
  return await frontendApiRequestJson<ModuleRenamePayload>(
    buildFrontendApiRestExecutionRequest(plan),
  );
}

async function renameCollectionThroughFrontendApiRest(
  request: RenameCollectionRequest,
): Promise<CollectionRenamePayload> {
  const {
    buildFrontendApiRestExecutionRequest,
    buildFrontendApiRestPlanRequest,
  } = await import("../data/frontendApi");
  const plan = await frontendApiRequestJson<FrontendApiRestRequestPlan>(
    buildFrontendApiRestPlanRequest(
      "collection.rename",
      renameCollectionFrontendApiValues(request),
    ),
  );
  return await frontendApiRequestJson<CollectionRenamePayload>(
    buildFrontendApiRestExecutionRequest(plan),
  );
}

async function scaffoldCollectionThroughFrontendApiRest(
  request: ScaffoldCollectionRequest,
): Promise<CollectionScaffoldPayload> {
  const {
    buildFrontendApiRestExecutionRequest,
    buildFrontendApiRestPlanRequest,
  } = await import("../data/frontendApi");
  const plan = await frontendApiRequestJson<FrontendApiRestRequestPlan>(
    buildFrontendApiRestPlanRequest(
      "collection.scaffold",
      scaffoldCollectionFrontendApiValues(request),
    ),
  );
  return await frontendApiRequestJson<CollectionScaffoldPayload>(
    buildFrontendApiRestExecutionRequest(plan),
  );
}

async function removeCollectionThroughFrontendApiRest(
  request: RemoveCollectionRequest & {
    write: boolean;
    planHash?: string;
  },
): Promise<CollectionRemovePayload> {
  const {
    buildFrontendApiRestExecutionRequest,
    buildFrontendApiRestPlanRequest,
  } = await import("../data/frontendApi");
  const plan = await frontendApiRequestJson<FrontendApiRestRequestPlan>(
    buildFrontendApiRestPlanRequest(
      "collection.remove",
      removeCollectionFrontendApiValues(request),
    ),
  );
  return await frontendApiRequestJson<CollectionRemovePayload>(
    buildFrontendApiRestExecutionRequest(plan),
  );
}

async function projectPreferredLanguageThroughFrontendApiRest(
  request: ProjectPreferredLanguageRequest,
): Promise<ProjectPreferredLanguagePayload> {
  const {
    buildFrontendApiRestExecutionRequest,
    buildFrontendApiRestPlanRequest,
  } = await import("../data/frontendApi");
  const plan = await frontendApiRequestJson<FrontendApiRestRequestPlan>(
    buildFrontendApiRestPlanRequest(
      "project.language",
      projectPreferredLanguageFrontendApiValues(request),
    ),
  );
  return await frontendApiRequestJson<ProjectPreferredLanguagePayload>(
    buildFrontendApiRestExecutionRequest(plan),
  );
}

async function duplicateModuleThroughFrontendApiRest(
  request: DuplicateModuleRequest,
): Promise<ModuleDuplicatePayload> {
  const {
    buildFrontendApiRestExecutionRequest,
    buildFrontendApiRestPlanRequest,
  } = await import("../data/frontendApi");
  const plan = await frontendApiRequestJson<FrontendApiRestRequestPlan>(
    buildFrontendApiRestPlanRequest(
      "module.duplicate",
      duplicateModuleFrontendApiValues(request),
    ),
  );
  return await frontendApiRequestJson<ModuleDuplicatePayload>(
    buildFrontendApiRestExecutionRequest(plan),
  );
}

async function moduleCollectionThroughFrontendApiRest(
  request: SetModuleCollectionRequest & {
    write: boolean;
    planHash?: string;
  },
): Promise<ModuleCollectionPayload> {
  const {
    buildFrontendApiRestExecutionRequest,
    buildFrontendApiRestPlanRequest,
  } = await import("../data/frontendApi");
  const plan = await frontendApiRequestJson<FrontendApiRestRequestPlan>(
    buildFrontendApiRestPlanRequest(
      "module.collection.set",
      moduleCollectionFrontendApiValues(request),
    ),
  );
  return await frontendApiRequestJson<ModuleCollectionPayload>(
    buildFrontendApiRestExecutionRequest(plan),
  );
}

async function moduleActivityThroughFrontendApiRest(
  request: SetModuleActiveRequest & {
    write: boolean;
    planHash?: string;
  },
): Promise<ModuleActivityPayload> {
  const {
    buildFrontendApiRestExecutionRequest,
    buildFrontendApiRestPlanRequest,
  } = await import("../data/frontendApi");
  const plan = await frontendApiRequestJson<FrontendApiRestRequestPlan>(
    buildFrontendApiRestPlanRequest(
      "module.activity.set",
      moduleActivityFrontendApiValues(request),
    ),
  );
  return await frontendApiRequestJson<ModuleActivityPayload>(
    buildFrontendApiRestExecutionRequest(plan),
  );
}

async function removeModuleThroughFrontendApiRest(
  request: RemoveModuleRequest,
): Promise<ModuleRemovePayload> {
  const {
    buildFrontendApiRestExecutionRequest,
    buildFrontendApiRestPlanRequest,
  } = await import("../data/frontendApi");
  const plan = await frontendApiRequestJson<FrontendApiRestRequestPlan>(
    buildFrontendApiRestPlanRequest(
      "module.remove",
      removeModuleFrontendApiValues(request),
    ),
  );
  return await frontendApiRequestJson<ModuleRemovePayload>(
    buildFrontendApiRestExecutionRequest(plan),
  );
}

async function createModuleDraftThroughFrontendApiRest(
  request: CreateModuleDraftRequest,
): Promise<ModuleDraftPayload> {
  const {
    buildFrontendApiRestExecutionRequest,
    buildFrontendApiRestPlanRequest,
  } = await import("../data/frontendApi");
  const plan = await frontendApiRequestJson<FrontendApiRestRequestPlan>(
    buildFrontendApiRestPlanRequest(
      "module.draft",
      moduleDraftFrontendApiValues(request),
    ),
  );
  return await frontendApiRequestJson<ModuleDraftPayload>(
    buildFrontendApiRestExecutionRequest(plan),
  );
}

async function createModulesThroughFrontendApiRest(
  request: CreateModulesRequest,
): Promise<ModuleCreateBatchPayload> {
  const {
    buildFrontendApiRestExecutionRequest,
    buildFrontendApiRestPlanRequest,
  } = await import("../data/frontendApi");
  const plan = await frontendApiRequestJson<FrontendApiRestRequestPlan>(
    buildFrontendApiRestPlanRequest(
      "module.create_batch",
      moduleCreateBatchFrontendApiValues(request),
    ),
  );
  return await frontendApiRequestJson<ModuleCreateBatchPayload>(
    buildFrontendApiRestExecutionRequest(plan),
  );
}

async function readTextSourceThroughFrontendApiRest(
  projectRoot: string,
  sourcePath: string,
  projectId?: string,
): Promise<string> {
  if (!projectId) {
    throw new Error(
      "Reading project source text through the native web bridge requires a project id.",
    );
  }
  const {
    buildFrontendApiRestExecutionRequest,
    buildFrontendApiRestPlanRequest,
  } = await import("../data/frontendApi");
  const plan = await frontendApiRequestJson<FrontendApiRestRequestPlan>(
    buildFrontendApiRestPlanRequest(
      "project.source_text",
      sourceTextFrontendApiValues(projectRoot, sourcePath, projectId),
    ),
  );
  const payload = await frontendApiRequestJson<
    ProjectSourceTextPayload | string
  >(buildFrontendApiRestExecutionRequest(plan));
  return typeof payload === "string" ? payload : payload.text;
}

async function readProjectSourceFormThroughFrontendApiRest(
  request: ReadProjectSourceFormRequest,
): Promise<unknown> {
  const {
    buildFrontendApiRestExecutionRequest,
    buildFrontendApiRestPlanRequest,
  } = await import("../data/frontendApi");
  const plan = await frontendApiRequestJson<FrontendApiRestRequestPlan>(
    buildFrontendApiRestPlanRequest(
      "project.source_form",
      sourceFormFrontendApiValues(request),
    ),
  );
  return await frontendApiRequestJson<unknown>(
    buildFrontendApiRestExecutionRequest(plan),
  );
}

async function applyProjectDraftThroughFrontendApiRest(
  request: ApplyProjectDraftRequest,
): Promise<DraftApplyPayload> {
  const {
    buildFrontendApiRestExecutionRequest,
    buildFrontendApiRestPlanRequest,
  } = await import("../data/frontendApi");
  const plan = await frontendApiRequestJson<FrontendApiRestRequestPlan>(
    buildFrontendApiRestPlanRequest(
      "project.draft_apply",
      draftApplyFrontendApiValues(request),
    ),
  );
  return await frontendApiRequestJson<DraftApplyPayload>(
    buildFrontendApiRestExecutionRequest(plan),
  );
}

async function startProjectBuildThroughFrontendApiRest(
  request: ProjectBuildRequest,
): Promise<ProjectBuildRunPayload> {
  const {
    buildFrontendApiRestExecutionRequest,
    buildFrontendApiRestPlanRequest,
  } = await import("../data/frontendApi");
  const plan = await frontendApiRequestJson<FrontendApiRestRequestPlan>(
    buildFrontendApiRestPlanRequest(
      "build.start",
      projectBuildFrontendApiValues(request),
    ),
  );
  return await frontendApiRequestJson<ProjectBuildRunPayload>(
    buildFrontendApiRestExecutionRequest(plan),
  );
}

async function getProjectBuildRunsThroughFrontendApiRest(
  projectRoot?: string,
): Promise<ProjectBuildRunsPayload> {
  const {
    buildFrontendApiRestExecutionRequest,
    buildFrontendApiRestPlanRequest,
  } = await import("../data/frontendApi");
  const plan = await frontendApiRequestJson<FrontendApiRestRequestPlan>(
    buildFrontendApiRestPlanRequest(
      "build.runs",
      projectBuildRunsFrontendApiValues(projectRoot),
    ),
  );
  return await frontendApiRequestJson<ProjectBuildRunsPayload>(
    buildFrontendApiRestExecutionRequest(plan),
  );
}

async function getProjectBuildStatusThroughFrontendApiRest(
  runId?: string | null,
): Promise<ProjectBuildRunPayload> {
  const {
    buildFrontendApiRestExecutionRequest,
    buildFrontendApiRestPlanRequest,
  } = await import("../data/frontendApi");
  const plan = await frontendApiRequestJson<FrontendApiRestRequestPlan>(
    buildFrontendApiRestPlanRequest(
      "build.status",
      projectBuildRunFrontendApiValues(runId),
    ),
  );
  return await frontendApiRequestJson<ProjectBuildRunPayload>(
    buildFrontendApiRestExecutionRequest(plan),
  );
}

async function interruptProjectBuildThroughFrontendApiRest(
  runId?: string | null,
): Promise<ProjectBuildRunPayload> {
  const {
    buildFrontendApiRestExecutionRequest,
    buildFrontendApiRestPlanRequest,
  } = await import("../data/frontendApi");
  const plan = await frontendApiRequestJson<FrontendApiRestRequestPlan>(
    buildFrontendApiRestPlanRequest(
      "build.interrupt",
      projectBuildRunFrontendApiValues(runId),
    ),
  );
  return await frontendApiRequestJson<ProjectBuildRunPayload>(
    buildFrontendApiRestExecutionRequest(plan),
  );
}

async function chatWithParaDevAiThroughFrontendApiRest(
  request: ParaDevAiChatRequest,
): Promise<ParaDevAiChatPayload> {
  const {
    buildFrontendApiRestExecutionRequest,
    buildFrontendApiRestPlanRequest,
  } = await import("../data/frontendApi");
  const plan = await frontendApiRequestJson<FrontendApiRestRequestPlan>(
    buildFrontendApiRestPlanRequest(
      "ai.chat",
      aiChatFrontendApiValues(request),
    ),
  );
  return await frontendApiRequestJson<ParaDevAiChatPayload>(
    buildFrontendApiRestExecutionRequest(plan),
  );
}

async function loadParaDevAiChatProfilesThroughFrontendApiRest(
  projectRoot: string,
): Promise<ParaDevAiChatProfilesPayload> {
  const {
    buildFrontendApiRestExecutionRequest,
    buildFrontendApiRestPlanRequest,
  } = await import("../data/frontendApi");
  const plan = await frontendApiRequestJson<FrontendApiRestRequestPlan>(
    buildFrontendApiRestPlanRequest(
      "ai.profiles",
      aiChatProfilesFrontendApiValues(projectRoot),
    ),
  );
  return await frontendApiRequestJson<ParaDevAiChatProfilesPayload>(
    buildFrontendApiRestExecutionRequest(plan),
  );
}

async function writeParaDevAiChatProfileThroughFrontendApiRest(
  profileId: string,
  profile: ParaDevAiChatProfileWrite,
  projectRoot: string,
): Promise<ParaDevAiChatProfilesPayload> {
  const {
    buildFrontendApiRestExecutionRequest,
    buildFrontendApiRestPlanRequest,
  } = await import("../data/frontendApi");
  const plan = await frontendApiRequestJson<FrontendApiRestRequestPlan>(
    buildFrontendApiRestPlanRequest(
      "ai.profile.write",
      aiChatProfileFrontendApiValues(profileId, profile, projectRoot),
    ),
  );
  return await frontendApiRequestJson<ParaDevAiChatProfilesPayload>(
    buildFrontendApiRestExecutionRequest(plan),
  );
}

async function resetParaDevAiChatProfileThroughFrontendApiRest(
  profileId: string,
  projectRoot: string,
): Promise<ParaDevAiChatProfilesPayload> {
  const {
    buildFrontendApiRestExecutionRequest,
    buildFrontendApiRestPlanRequest,
  } = await import("../data/frontendApi");
  const plan = await frontendApiRequestJson<FrontendApiRestRequestPlan>(
    buildFrontendApiRestPlanRequest(
      "ai.profile.reset",
      aiChatProfileResetFrontendApiValues(profileId, projectRoot),
    ),
  );
  return await frontendApiRequestJson<ParaDevAiChatProfilesPayload>(
    buildFrontendApiRestExecutionRequest(plan),
  );
}

function normalizeHeavenBaseLlmTestPayload(
  payload: HeavenBaseLlmTestPayload,
  request: HeavenBaseLlmTestRequest,
): HeavenBaseLlmTestPayload {
  return {
    schema: payload.schema,
    baseUrl: payload.baseUrl ?? request.baseUrl ?? "",
    gateway: payload.gateway || request.gateway,
    keySource: payload.keySource || "",
    model: payload.model || request.model,
    preset: payload.preset || request.preset || "",
    provider: payload.provider || request.provider,
    resultCode: isLlmResultCode(payload.resultCode)
      ? payload.resultCode
      : "unknown",
    status: isLlmStatus(payload.status) ? payload.status : "unknown",
    testDetail: payload.testDetail || payload.detail || "",
    testedAt: payload.testedAt || payload.checkedAt || "",
  };
}

function normalizeParaDevAiChatPayload(
  payload: ParaDevAiChatPayload,
  request: ParaDevAiChatRequest,
): ParaDevAiChatPayload {
  const projectRoot = payload.projectRoot || request.projectRoot || "";
  const proposal =
    payload.proposal === undefined || payload.proposal === null
      ? undefined
      : paraDevAiChatProposal(payload.proposal, projectRoot);
  return {
    schema: payload.schema,
    baseUrl: payload.baseUrl ?? request.baseUrl ?? "",
    checkedAt: payload.checkedAt ?? "",
    detail: payload.detail ?? "",
    gateway: payload.gateway || request.gateway,
    keySource: payload.keySource || "",
    model: payload.model || request.model,
    preset: payload.preset || request.preset || "",
    projectRoot,
    prompt: payload.prompt || request.prompt,
    provider: payload.provider || request.provider,
    ...(proposal ? { proposal } : {}),
    reply: payload.reply || "",
    role: payload.role || request.role || "chat",
    sources: normalizeParaDevAiChatSources(payload.sources ?? request.sources),
    status: isLlmStatus(payload.status) ? payload.status : "unknown",
  };
}

function paraDevAiChatProposal(
  value: unknown,
  projectRoot: string,
): ParaDevAiChatProposal {
  if (!isUnknownRecord(value)) {
    throw new Error("ParaDev AI chat proposal must be an object.");
  }
  if (value.operationId === "module.create_batch") {
    return paraDevAiChatModuleBatchProposal(value, projectRoot);
  }
  if (value.operationId === "collection.scaffold") {
    return paraDevAiChatCollectionScaffoldProposal(value, projectRoot);
  }
  if (value.operationId === "module.source_form_update_batch") {
    return paraDevAiChatSourceFormUpdateProposal(value, projectRoot);
  }
  throw new Error(
    "ParaDev AI chat proposal has an unsupported schema or operation.",
  );
}

function paraDevAiChatSourceFormUpdateProposal(
  value: Record<string, unknown>,
  projectRoot: string,
): ParaDevAiChatSourceFormUpdateProposal {
  const proposalKeys = [
    "schema",
    "operationId",
    "familyId",
    "requests",
    "plan",
  ];
  if (
    Object.keys(value).length !== proposalKeys.length ||
    proposalKeys.some((key) => !Object.hasOwn(value, key))
  ) {
    throw new Error(
      "ParaDev AI chat source-update proposal did not match the exact payload shape.",
    );
  }
  if (
    value.schema !== "paradev.desktop.ai-chat-proposal.v1" ||
    value.operationId !== "module.source_form_update_batch"
  ) {
    throw new Error(
      "ParaDev AI chat proposal has an unsupported schema or operation.",
    );
  }
  if (!projectRoot.trim()) {
    throw new Error(
      "ParaDev AI chat source-update proposal requires an active project root.",
    );
  }
  const normalizedProjectRoot = normalizedPayloadPath(
    projectRoot,
    "AI chat source-update proposal projectRoot",
    true,
  );
  const familyId = requiredPayloadString(
    value,
    "familyId",
    "AI chat source-update proposal",
  ).trim();
  const requestRows = requiredPayloadRecordArray(
    value,
    "requests",
    "AI chat source-update proposal",
  );
  if (requestRows.length === 0 || requestRows.length > 16) {
    throw new Error(
      "ParaDev AI chat source-update requests must contain between 1 and 16 source files.",
    );
  }
  const seenPaths = new Set<string>();
  const requests = requestRows.map((row, index) => {
    const label = `AI chat source-update request ${index}`;
    const requestKeys = [
      "source_path",
      "module_id",
      "values",
      "control_labels",
    ];
    if (
      Object.keys(row).length !== requestKeys.length ||
      requestKeys.some((key) => !Object.hasOwn(row, key))
    ) {
      throw new Error(`ParaDev ${label} did not match the exact payload shape.`);
    }
    const sourcePath = normalizedPayloadPath(
      requiredPayloadString(row, "source_path", label),
      `${label} source_path`,
      false,
    );
    if (seenPaths.has(sourcePath.value)) {
      throw new Error(
        "ParaDev AI chat source-update proposal repeats a source path.",
      );
    }
    seenPaths.add(sourcePath.value);
    const moduleId = requiredPayloadString(row, "module_id", label).trim();
    if (!moduleId.startsWith(`${familyId}/`)) {
      throw new Error(
        "ParaDev AI chat source-update proposal must target exactly one module family.",
      );
    }
    const rawValues = requiredPayloadRecord(row, "values", label);
    const rawLabels = requiredPayloadRecord(row, "control_labels", label);
    if (Object.keys(rawValues).length === 0) {
      throw new Error(`ParaDev ${label} values must not be empty.`);
    }
    if (
      Object.keys(rawValues).length !== Object.keys(rawLabels).length ||
      Object.keys(rawValues).some(
        (controlId) => !controlId.trim() || !Object.hasOwn(rawLabels, controlId),
      )
    ) {
      throw new Error(
        `ParaDev ${label} control labels do not match its requested values.`,
      );
    }
    const values = Object.fromEntries(
      Object.entries(rawValues).map(([controlId, replacement]) => [
        controlId,
        sourceFormScalar(replacement, `${label} value ${controlId}`),
      ]),
    );
    const controlLabels = Object.fromEntries(
      Object.entries(rawLabels).map(([controlId, controlLabel]) => [
        controlId,
        sourceFormText(controlLabel, `${label} label ${controlId}`),
      ]),
    );
    return {
      source_path: sourcePath.value,
      module_id: moduleId,
      values,
      control_labels: controlLabels,
    };
  });
  const rawPlan = requiredPayloadRecord(
    value,
    "plan",
    "AI chat source-update proposal",
  );
  const projectId = requiredPayloadString(
    rawPlan,
    "project_id",
    "AI chat source-update proposal plan",
  );
  const plan = sourceFormUpdateBatchPlan(rawPlan, {
    projectId,
    projectRoot: normalizedProjectRoot.value,
    updates: requests.map((request) => ({
      sourcePath: request.source_path,
      values: request.values,
    })),
  });
  if (
    plan.updates.some(
      (update, index) =>
        update.family !== familyId ||
        update.moduleId !== requests[index]?.module_id ||
        !payloadPathsEqual(
          normalizedPayloadPath(
            update.relativePath,
            `AI chat source-update plan row ${index} relative path`,
            false,
          ),
          normalizedPayloadPath(
            requests[index]?.source_path ?? "",
            `AI chat source-update request ${index} relative path`,
            false,
          ),
        ),
    )
  ) {
    throw new Error(
      "ParaDev AI chat source-update proposal does not match its exact SDK plan.",
    );
  }
  return {
    schema: "paradev.desktop.ai-chat-proposal.v1",
    operationId: "module.source_form_update_batch",
    familyId,
    requests,
    plan,
  };
}

function paraDevAiChatModuleBatchProposal(
  value: unknown,
  projectRoot: string,
): ParaDevAiChatModuleBatchProposal {
  if (!isUnknownRecord(value)) {
    throw new Error("ParaDev AI chat proposal must be an object.");
  }
  const proposalKeys = [
    "schema",
    "operationId",
    "familyId",
    "sourceRoot",
    "requests",
    "plan",
  ];
  if (
    Object.keys(value).length !== proposalKeys.length ||
    proposalKeys.some((key) => !Object.hasOwn(value, key))
  ) {
    throw new Error(
      "ParaDev AI chat proposal did not match the exact payload shape.",
    );
  }
  if (
    value.schema !== "paradev.desktop.ai-chat-proposal.v1" ||
    value.operationId !== "module.create_batch"
  ) {
    throw new Error(
      "ParaDev AI chat proposal has an unsupported schema or operation.",
    );
  }
  if (!projectRoot.trim()) {
    throw new Error(
      "ParaDev AI chat module proposal requires an active project root.",
    );
  }
  normalizedPayloadPath(projectRoot, "AI chat proposal projectRoot", true);
  const familyId = requiredPayloadString(
    value,
    "familyId",
    "AI chat proposal",
  ).trim();
  const sourceRoot = requiredPayloadString(
    value,
    "sourceRoot",
    "AI chat proposal",
  );
  const normalizedSourceRoot = normalizedPayloadPath(
    sourceRoot,
    "AI chat proposal sourceRoot",
    true,
  );
  const requestRows = requiredPayloadRecordArray(
    value,
    "requests",
    "AI chat proposal",
  );
  if (requestRows.length === 0 || requestRows.length > 256) {
    throw new Error(
      "ParaDev AI chat proposal requests must contain between 1 and 256 modules.",
    );
  }
  const portableObjectIds = new Set<string>();
  const requests = requestRows.map((row, index) => {
    const label = `AI chat proposal request ${index}`;
    const requestKeys = ["template_id", "object_id", "values"];
    if (
      Object.keys(row).length !== requestKeys.length ||
      requestKeys.some((key) => !Object.hasOwn(row, key))
    ) {
      throw new Error(
        `ParaDev ${label} did not match the exact payload shape.`,
      );
    }
    const templateId = requiredPayloadString(row, "template_id", label).trim();
    const objectId = requiredPayloadString(row, "object_id", label).trim();
    const portableObjectId = objectId
      .normalize("NFC")
      .toLocaleLowerCase("en-US");
    if (portableObjectIds.has(portableObjectId)) {
      throw new Error(
        "ParaDev AI chat proposal repeats a portable module object id.",
      );
    }
    portableObjectIds.add(portableObjectId);
    const rawValues = requiredPayloadRecord(row, "values", label);
    const values = Object.fromEntries(
      Object.entries(rawValues).map(([key, field]) => {
        if (
          !key.trim() ||
          (typeof field !== "string" &&
            typeof field !== "boolean" &&
            !(
              typeof field === "number" &&
              Number.isFinite(field) &&
              (!Number.isInteger(field) || Number.isSafeInteger(field))
            ))
        ) {
          throw new Error(
            `ParaDev ${label} values must contain named finite JSON scalars.`,
          );
        }
        return [key, field];
      }),
    ) as Record<string, string | number | boolean>;
    return {
      template_id: templateId,
      object_id: objectId,
      values,
    };
  });
  const rawPlan = requiredPayloadRecord(value, "plan", "AI chat proposal");
  const projectId = requiredPayloadString(
    rawPlan,
    "project_id",
    "AI chat proposal plan",
  );
  const plan = moduleCreateBatchPayload(rawPlan, {
    projectId,
    projectRoot,
    modules: requests,
    sourceRoot,
    write: false,
  });
  if (
    !payloadPathsEqual(
      normalizedSourceRoot,
      normalizedPayloadPath(
        plan.source_root,
        "AI chat proposal plan source_root",
        true,
      ),
    )
  ) {
    throw new Error(
      "ParaDev AI chat proposal source root does not match its plan.",
    );
  }
  if (
    plan.modules.some(
      (row) => typeof row.family !== "string" || row.family.trim() !== familyId,
    )
  ) {
    throw new Error(
      "ParaDev AI chat proposal must contain exactly one module family.",
    );
  }
  return {
    schema: "paradev.desktop.ai-chat-proposal.v1",
    operationId: "module.create_batch",
    familyId,
    sourceRoot,
    requests,
    plan,
  };
}

function paraDevAiChatCollectionScaffoldProposal(
  value: Record<string, unknown>,
  projectRoot: string,
): ParaDevAiChatCollectionScaffoldProposal {
  const proposalKeys = [
    "schema",
    "operationId",
    "familyId",
    "sourceRoot",
    "request",
    "plan",
  ];
  if (
    Object.keys(value).length !== proposalKeys.length ||
    proposalKeys.some((key) => !Object.hasOwn(value, key))
  ) {
    throw new Error(
      "ParaDev AI chat collection proposal did not match the exact payload shape.",
    );
  }
  if (
    value.schema !== "paradev.desktop.ai-chat-proposal.v1" ||
    value.operationId !== "collection.scaffold"
  ) {
    throw new Error(
      "ParaDev AI chat proposal has an unsupported schema or operation.",
    );
  }
  if (!projectRoot.trim()) {
    throw new Error(
      "ParaDev AI chat collection proposal requires an active project root.",
    );
  }
  normalizedPayloadPath(projectRoot, "AI chat proposal projectRoot", true);
  const familyId = requiredPayloadString(
    value,
    "familyId",
    "AI chat collection proposal",
  ).trim();
  const sourceRoot = requiredPayloadString(
    value,
    "sourceRoot",
    "AI chat collection proposal",
  );
  const request = requiredPayloadRecord(
    value,
    "request",
    "AI chat collection proposal",
  );
  const requestKeys = ["template_id", "collection_id", "values"];
  if (
    Object.keys(request).length !== requestKeys.length ||
    requestKeys.some((key) => !Object.hasOwn(request, key))
  ) {
    throw new Error(
      "ParaDev AI chat collection request did not match the exact payload shape.",
    );
  }
  const templateId = requiredPayloadString(
    request,
    "template_id",
    "AI chat collection request",
  ).trim();
  const collectionId = requiredPayloadString(
    request,
    "collection_id",
    "AI chat collection request",
  ).trim();
  const values = requiredPayloadStringRecord(
    request,
    "values",
    "AI chat collection request",
  );
  const rawPlan = requiredPayloadRecord(
    value,
    "plan",
    "AI chat collection proposal",
  );
  const plan = collectionScaffoldPayload(rawPlan, {
    projectRoot,
    templateId,
    collectionId,
    values,
    sourceRoot,
    write: false,
    force: false,
  });
  if (plan.family.trim() !== familyId) {
    throw new Error(
      "ParaDev AI chat collection proposal family does not match its plan.",
    );
  }
  return {
    schema: "paradev.desktop.ai-chat-proposal.v1",
    operationId: "collection.scaffold",
    familyId,
    sourceRoot,
    request: {
      template_id: templateId,
      collection_id: collectionId,
      values,
    },
    plan,
  };
}

function normalizeParaDevAiChatSources(
  sources: ParaDevAiChatSource[] | undefined,
): ParaDevAiChatSource[] {
  if (!Array.isArray(sources)) {
    return [];
  }
  return sources
    .filter(
      (source) =>
        source && typeof source.kind === "string" && source.kind.trim(),
    )
    .map((source) => ({
      ...source,
      kind: source.kind.trim(),
      ...(source.label ? { label: source.label } : {}),
    }));
}

function normalizeParaDevAiChatProfilesPayload(
  payload: ParaDevAiChatProfilesPayload,
  projectRoot: string,
): ParaDevAiChatProfilesPayload {
  const fallback = fallbackParaDevAiChatProfilesPayload(projectRoot);
  const profiles = Array.isArray(payload.profiles) ? payload.profiles : [];
  const normalizedProfiles = profiles.map((profile) => ({
    detail: profile.detail || "",
    detailKey: profile.detailKey,
    id: profile.id || "chat",
    label: profile.label || profile.id || "Chat",
    labelKey: profile.labelKey,
    operationCards: normalizeParaDevAiChatOperationCards(
      profile.operationCards,
    ),
    operationIds: Array.isArray(profile.operationIds)
      ? profile.operationIds.filter(
          (operationId): operationId is ParaDevFrontendApiOperationId =>
            typeof operationId === "string" && operationId.trim().length > 0,
        )
      : undefined,
    prompt: profile.prompt || "",
    promptKey: profile.promptKey,
    sourceKinds: Array.isArray(profile.sourceKinds) ? profile.sourceKinds : [],
  }));
  const normalizedSourceKinds = Array.isArray(payload.sourceKinds)
    ? payload.sourceKinds
        .filter(
          (sourceKind) => typeof sourceKind === "string" && sourceKind.trim(),
        )
        .map((sourceKind) => sourceKind.trim())
    : [];
  const normalizedSourceKindRows = Array.isArray(payload.sourceKindRows)
    ? payload.sourceKindRows
        .filter((row) => row && typeof row.id === "string" && row.id.trim())
        .map((row) => ({
          frontendKinds: Array.isArray(row.frontendKinds)
            ? row.frontendKinds
                .filter((kind) => typeof kind === "string" && kind.trim())
                .map((kind) => kind.trim())
            : [],
          id: row.id.trim(),
          label: row.label || row.id.trim(),
          labelKey: row.labelKey,
        }))
    : [];
  const resolvedProfiles =
    normalizedProfiles.length > 0 ? normalizedProfiles : fallback.profiles;
  return {
    schema: payload.schema ?? fallback.schema,
    defaultRole: payload.defaultRole || resolvedProfiles[0]?.id || "chat",
    profiles: resolvedProfiles,
    projectRoot: payload.projectRoot || projectRoot || "",
    sourceKindRows:
      normalizedSourceKindRows.length > 0
        ? normalizedSourceKindRows
        : fallback.sourceKindRows,
    sourceKinds:
      normalizedSourceKinds.length > 0
        ? normalizedSourceKinds
        : fallback.sourceKinds,
  };
}

function normalizeParaDevAiChatOperationCards(
  cards: readonly ParaDevAiChatOperationCard[] | undefined,
): ParaDevAiChatOperationCard[] | undefined {
  if (!Array.isArray(cards)) {
    return undefined;
  }
  const normalizedCards = cards
    .filter((card) => card && typeof card.id === "string" && card.id.trim())
    .map((card) => ({
      id: card.id.trim() as ParaDevFrontendApiOperationId,
      mutates: card.mutates === true,
      rest: card.rest || "",
      sdk: card.sdk || "",
      summary: card.summary || "",
      title: card.title || card.id,
    }));
  return normalizedCards.length > 0 ? normalizedCards : undefined;
}

export function fallbackParaDevAiChatProfilesPayload(
  projectRoot: string,
): ParaDevAiChatProfilesPayload {
  return {
    schema: "paradev.desktop.ai-chat-profiles.v1",
    defaultRole: "chat",
    projectRoot,
    sourceKindRows: PARADEV_DESKTOP_AI_CHAT_SOURCE_KIND_ROWS.map((row) => ({
      ...row,
      frontendKinds: Array.from(row.frontendKinds),
    })),
    sourceKinds: Array.from(PARADEV_DESKTOP_AI_CHAT_SOURCE_KINDS),
    profiles: PARADEV_DESKTOP_AI_CHAT_PROFILES.map((profile) => ({
      ...profile,
      sourceKinds: Array.from(profile.sourceKinds),
    })),
  };
}

function configValue(payload: DesktopConfigValuePayload, key: string): unknown {
  if (
    payload.schema !== "paradev.desktop.config-value.v1" ||
    payload.key !== key
  ) {
    throw new Error(`ParaDev desktop config response did not match ${key}.`);
  }
  return payload.value;
}

function thumbnailCachePayload(value: unknown): BinarySourcePayload | null {
  if (value === null) {
    return null;
  }
  if (
    !isUnknownRecord(value) ||
    value.schema !== "paradev.desktop.binary-source.v1" ||
    typeof value.path !== "string" ||
    !value.path.trim() ||
    value.mimeType !== "image/png" ||
    !Array.isArray(value.bytes) ||
    value.bytes.length === 0 ||
    !value.bytes.every(
      (byte) =>
        Number.isSafeInteger(byte) && Number(byte) >= 0 && Number(byte) <= 255,
    )
  ) {
    throw new Error("ParaDev returned an invalid thumbnail-cache response.");
  }
  return value as BinarySourcePayload;
}

function projectPackageInstallPayload(
  value: unknown,
): ProjectPackageInstallPayload | null {
  if (value === null) {
    return null;
  }
  if (
    !isUnknownRecord(value) ||
    value.schema !== "paradev.desktop.project-package-install.v1"
  ) {
    throw new Error(
      "ParaDev returned an invalid project-package installation response.",
    );
  }
  const status = value.status;
  if (
    (status !== "installed" && status !== "existing") ||
    typeof value.installed !== "boolean" ||
    value.installed !== (status === "installed") ||
    typeof value.project_root !== "string" ||
    !value.project_root.trim() ||
    !isProjectPackageCatalogRow(value.package) ||
    !isDesktopProjectRow(value.project) ||
    value.project.root !== value.project_root
  ) {
    throw new Error(
      "ParaDev returned an inconsistent project-package installation response.",
    );
  }
  return value as ProjectPackageInstallPayload;
}

function isProjectPackageCatalogRow(
  value: unknown,
): value is ProjectPackageCatalogRow {
  if (!isUnknownRecord(value)) {
    return false;
  }
  const stringFields = [
    "id",
    "label",
    "game",
    "archive_name",
    "archive_sha256",
    "project_id",
    "project_version",
    "top_level_folder",
  ] as const;
  const integerFields = [
    "archive_size",
    "entry_count",
    "file_count",
    "directory_count",
    "uncompressed_size",
    "compressed_size",
    "max_member_path_code_units",
  ] as const;
  return (
    stringFields.every(
      (field) =>
        typeof value[field] === "string" && value[field].trim().length > 0,
    ) &&
    integerFields.every(
      (field) =>
        Number.isSafeInteger(value[field]) && Number(value[field]) >= 0,
    ) &&
    /^[0-9a-f]{64}$/.test(String(value.archive_sha256))
  );
}

function isDesktopProjectRow(value: unknown): value is DesktopProjectRow {
  return (
    isUnknownRecord(value) &&
    ["project_id", "title", "game", "root", "manifest"].every(
      (field) =>
        typeof value[field] === "string" && value[field].trim().length > 0,
    ) &&
    Array.isArray(value.source_roots) &&
    value.source_roots.every((path) => typeof path === "string")
  );
}

function isLlmStatus(
  value: string,
): value is HeavenBaseLlmTestPayload["status"] {
  return (
    value === "ready" ||
    value === "warning" ||
    value === "error" ||
    value === "unknown"
  );
}

function isLlmResultCode(value: unknown): value is HeavenBaseLlmTestResultCode {
  return (
    value === "ok" ||
    value === "empty_response" ||
    value === "unexpected_response" ||
    value === "exception" ||
    value === "unknown"
  );
}

async function bridgeResponseJson<T>(response: Response): Promise<T> {
  if (!response.ok) {
    throw new Error(await bridgeErrorMessage(response));
  }
  return (await response.json()) as T;
}

async function bridgeErrorMessage(response: Response): Promise<string> {
  const fallback = `ParaDev native bridge request failed: ${response.status} ${response.statusText}`;
  const detail = await bridgeResponseErrorDetail(response);
  return detail ? `${fallback}: ${detail}` : fallback;
}

async function bridgeResponseErrorDetail(response: Response): Promise<string> {
  try {
    return bridgeErrorDetailFromPayload(await response.json());
  } catch {
    return "";
  }
}

function bridgeErrorDetailFromPayload(payload: unknown): string {
  if (typeof payload === "string") {
    return payload;
  }
  if (!payload || typeof payload !== "object") {
    return "";
  }
  const record = payload as Record<string, unknown>;
  if (typeof record.detail === "string" && record.detail.trim()) {
    return record.detail;
  }
  if (typeof record.message === "string" && record.message.trim()) {
    return record.message;
  }
  return "";
}

function bridgeUrl(path: string, query: Record<string, unknown> = {}): string {
  const url = new URL(
    `${nativeBridgeBaseUrl()}${path.startsWith("/") ? path : `/${path}`}`,
  );
  Object.entries(query).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== "") {
      url.searchParams.append(key, String(value));
    }
  });
  return url.toString();
}

function restUrl(path: string): string {
  if (path.startsWith("/") && hasNativeBridge()) {
    return bridgeUrl(path);
  }
  return path;
}

function lspCompletionBody(
  request: PdxLspCompletionRequest,
): Record<string, unknown> {
  return compactBody({
    text: request.text,
    line: request.line,
    character: request.character,
    offset: request.offset,
    uri: request.uri,
    path: request.path,
    project_path: request.projectPath,
    database: request.database,
    game_root: request.gameRoot,
    limit: request.limit,
  });
}

function lspSemanticTokensBody(
  request: PdxLspSemanticTokensRequest,
): Record<string, unknown> {
  return compactBody({
    text: request.text,
    uri: request.uri,
    path: request.path,
  });
}

function renameModuleFrontendApiValues(
  request: RenameModuleRequest,
): Record<string, unknown> {
  return compactBody({
    path: request.projectRoot,
    module_id: request.moduleId,
    object_id: request.objectId,
    title: request.title,
    source_root: request.sourceRoot,
  });
}

function renameCollectionFrontendApiValues(
  request: RenameCollectionRequest,
): Record<string, unknown> {
  return compactBody({
    path: request.projectRoot,
    collection_id: request.collectionId,
    target_id: request.targetId,
    family: request.family,
    source_root: request.sourceRoot,
  });
}

function scaffoldCollectionFrontendApiValues(
  request: ScaffoldCollectionRequest,
): Record<string, unknown> {
  return compactBody({
    path: request.projectRoot,
    template_id: request.templateId,
    collection_id: request.collectionId,
    source_root: request.sourceRoot,
    values: request.values,
    write: request.write,
    force: request.force,
    plan_hash: request.planHash,
  });
}

function removeCollectionFrontendApiValues(
  request: RemoveCollectionRequest & {
    write: boolean;
    planHash?: string;
  },
): Record<string, unknown> {
  return compactBody({
    path: request.projectRoot,
    collection_id: request.collectionId,
    family: request.family,
    source_root: request.sourceRoot,
    write: request.write,
    plan_hash: request.planHash,
  });
}

function projectPreferredLanguageFrontendApiValues(
  request: ProjectPreferredLanguageRequest,
): Record<string, unknown> {
  return compactBody({
    path: request.projectRoot,
    preferred_language: request.preferredLanguage,
    write: request.write,
    plan_hash: request.planHash,
  });
}

function duplicateModuleFrontendApiValues(
  request: DuplicateModuleRequest,
): Record<string, unknown> {
  return compactBody({
    path: request.projectRoot,
    module_id: request.moduleId,
    object_id: request.objectId,
    source_root: request.sourceRoot,
    destination_source_root: request.destinationSourceRoot,
    identity: request.identity,
    write: request.write,
    plan_hash: request.planHash,
  });
}

function moduleCollectionFrontendApiValues(
  request: SetModuleCollectionRequest & {
    write: boolean;
    planHash?: string;
  },
): Record<string, unknown> {
  return compactBody({
    path: request.projectRoot,
    module_id: request.moduleId,
    collection_id: request.collectionId,
    source_root: request.sourceRoot,
    write: request.write,
    plan_hash: request.planHash,
  });
}

function moduleActivityFrontendApiValues(
  request: SetModuleActiveRequest & {
    write: boolean;
    planHash?: string;
  },
): Record<string, unknown> {
  return compactBody({
    path: request.projectRoot,
    module_id: request.moduleId,
    active: request.active,
    source_root: request.sourceRoot,
    write: request.write,
    plan_hash: request.planHash,
  });
}

function removeModuleFrontendApiValues(
  request: RemoveModuleRequest,
): Record<string, unknown> {
  return compactBody({
    path: request.projectRoot,
    module_id: request.moduleId,
    source_root: request.sourceRoot,
    write: true,
  });
}

function moduleDraftFrontendApiValues(
  request: CreateModuleDraftRequest,
): Record<string, unknown> {
  return compactBody({
    project_id: request.projectId,
    family_id: request.familyId,
    path: request.projectRoot,
    template_id: request.templateId,
    object_id: request.objectId,
    values: request.values,
    write: request.write,
    force: request.force,
  });
}

function moduleCreateBatchFrontendApiValues(
  request: CreateModulesRequest,
): Record<string, unknown> {
  return compactBody({
    project_id: request.projectId,
    path: request.projectRoot,
    modules: request.modules,
    source_root: request.sourceRoot,
    write: request.write,
    plan_hash: request.planHash,
  });
}

function sourceTextFrontendApiValues(
  projectRoot: string,
  sourcePath: string,
  projectId: string,
): Record<string, unknown> {
  return compactBody({
    project_id: projectId,
    path: projectRoot,
    source_path: sourcePath,
  });
}

function sourceFormFrontendApiValues(
  request: ReadProjectSourceFormRequest,
): Record<string, unknown> {
  return {
    project_id: request.projectId,
    path: request.projectRoot,
    source_path: request.sourcePath,
    text: request.text,
    ...(request.query ? { query: request.query } : {}),
  };
}

function draftApplyFrontendApiValues(
  request: ApplyProjectDraftRequest,
): Record<string, unknown> {
  return compactBody({
    project_id: request.projectId,
    path: request.projectRoot,
    source_edits: request.sourceEdits?.map(sourceTextEditFrontendApiValue),
    source_removals: request.sourceRemovals?.map(sourceRemovalFrontendApiValue),
    source_replacements: request.sourceReplacements?.map(
      sourceReplacementFrontendApiValue,
    ),
    module_rename: request.moduleRename
      ? compactBody({
          module_id: request.moduleRename.moduleId,
          object_id: request.moduleRename.objectId,
          source_root: request.moduleRename.sourceRoot,
          title: request.moduleRename.title,
        })
      : undefined,
  });
}

function projectBuildFrontendApiValues(
  request: ProjectBuildRequest,
): Record<string, unknown> {
  return compactBody({
    project_root: request.projectRoot,
    mode: request.mode,
    profile: request.profile,
    strict_metadata: request.strictMetadata,
    parallelism: request.parallelism,
    target: request.target,
  });
}

function projectBuildRunsFrontendApiValues(
  projectRoot?: string,
): Record<string, unknown> {
  return compactBody({
    project_root: projectRoot,
  });
}

function normalizedBuildRunId(runId?: string | null): string | undefined {
  if (runId === undefined || runId === null) {
    return undefined;
  }
  const normalized = runId.trim();
  if (!normalized) {
    throw new Error("Build run ID cannot be empty.");
  }
  return normalized;
}

function projectBuildRunFrontendApiValues(
  runId?: string | null,
): Record<string, unknown> {
  return compactBody({
    run_id: runId,
  });
}

function aiChatFrontendApiValues(
  request: ParaDevAiChatRequest,
): Record<string, unknown> {
  return compactBody({
    provider: request.provider,
    model: request.model,
    gateway: request.gateway,
    preset: request.preset,
    key_env: request.keyEnv,
    base_url: request.baseUrl,
    prompt: request.prompt,
    role: request.role,
    project_root: request.projectRoot,
    sources: request.sources,
  });
}

function aiChatProfilesFrontendApiValues(
  projectRoot: string,
): Record<string, unknown> {
  return compactBody({
    project_root: projectRoot,
  });
}

function aiChatProfileFrontendApiValues(
  profileId: string,
  profile: ParaDevAiChatProfileWrite,
  projectRoot: string,
): Record<string, unknown> {
  return compactBody({
    profile_id: profileId,
    profile: compactBody({
      label: profile.label,
      detail: profile.detail,
      prompt: profile.prompt,
      sourceKinds: profile.sourceKinds,
    }),
    project_root: projectRoot,
  });
}

function aiChatProfileResetFrontendApiValues(
  profileId: string,
  projectRoot: string,
): Record<string, unknown> {
  return compactBody({
    profile_id: profileId,
    project_root: projectRoot,
  });
}

function projectInspectionRestFilters(
  filters: Record<string, unknown>,
): Record<string, unknown> {
  return Object.fromEntries(
    Object.entries(filters).map(([key, value]) => [
      projectInspectionRestFilterName(key),
      value,
    ]),
  );
}

function normalizeProjectCatalogQueryRequest(
  request: ProjectCatalogQueryRequest,
): NormalizedProjectCatalogQueryRequest {
  const limit = request.limit ?? PROJECT_CATALOG_QUERY_DEFAULT_LIMIT;
  if (
    !Number.isInteger(limit) ||
    limit < 1 ||
    limit > PROJECT_CATALOG_QUERY_MAX_LIMIT
  ) {
    throw new Error(
      `Project catalog query limit must be an integer from 1 to ${PROJECT_CATALOG_QUERY_MAX_LIMIT}.`,
    );
  }
  const offset = request.offset ?? 0;
  if (
    !Number.isSafeInteger(offset) ||
    offset < 0 ||
    offset > PROJECT_CATALOG_QUERY_MAX_OFFSET
  ) {
    throw new Error(
      `Project catalog query offset must be an integer from 0 to ${PROJECT_CATALOG_QUERY_MAX_OFFSET}.`,
    );
  }
  const includeData = request.includeData ?? false;
  if (includeData && limit !== PROJECT_CATALOG_QUERY_MAX_HYDRATED_LIMIT) {
    throw new Error(
      `Hydrated project catalog queries must have limit ${PROJECT_CATALOG_QUERY_MAX_HYDRATED_LIMIT}.`,
    );
  }
  return {
    projectRoot: normalizedProjectCatalogRoot(request.projectRoot),
    entity: normalizedCatalogFilter(request.entity),
    targetId: normalizedCatalogFilter(request.targetId),
    name: normalizedCatalogFilter(request.name),
    tag: normalizedCatalogFilter(request.tag),
    limit,
    offset,
    includeData,
  };
}

function normalizeProjectCatalogRefreshRequest(
  request: ProjectCatalogRefreshRequest,
): ProjectCatalogRefreshRequest {
  const profile = normalizedCatalogFilter(request.profile);
  return {
    projectRoot: normalizedProjectCatalogRoot(request.projectRoot),
    ...(profile ? { profile } : {}),
  };
}

const SOURCE_FORM_PAYLOAD_FIELDS = new Set([
  "schema",
  "contract",
  "project_id",
  "family",
  "module_id",
  "path",
  "relative_path",
  "module_relative_path",
  "source_root",
  "source_format",
  "label",
  "description",
  "query",
  "coverage",
  "sections",
]);
const SOURCE_FORM_SECTION_FIELDS = new Set([
  "id",
  "label",
  "description",
  "controls",
  "sections",
]);
const SOURCE_FORM_CONTROL_FIELDS = new Set([
  "id",
  "label",
  "description",
  "description_source",
  "control",
  "value",
  "patch",
  "choices",
  "min",
  "max",
  "step",
  "placeholder",
  "multiline",
]);
const SOURCE_FORM_CHOICE_FIELDS = new Set(["label", "value"]);
const SOURCE_FORM_JSON_PATCH_FIELDS = new Set(["op", "path"]);
const SOURCE_FORM_PDX_PATCH_FIELDS = new Set([
  "op",
  "path",
  "span",
  "expected",
  "scalar_kind",
  "source_length",
]);
const SOURCE_FORM_PDX_INTEGER_LIST_PATCH_FIELDS = new Set([
  "op",
  "path",
  "span",
  "expected",
  "item_kind",
  "columns",
  "minimum",
  "layout",
  "source_length",
]);
const SOURCE_FORM_PDX_BLOCK_BODY_PATCH_FIELDS = new Set([
  "op",
  "path",
  "span",
  "expected",
  "layout",
  "source_length",
]);
const SOURCE_FORM_PDX_INTEGER_LIST_LAYOUT_FIELDS = new Set([
  "prefix",
  "column_separator",
  "row_separator",
  "suffix",
]);
const SOURCE_FORM_PDX_BLOCK_BODY_LAYOUT_FIELDS = new Set([
  "prefix",
  "line_prefix",
  "suffix",
]);
const SOURCE_FORM_PDX_PATH_FIELDS = new Set(["key", "occurrence"]);
const SOURCE_FORM_PDX_SPAN_FIELDS = new Set(["start", "end"]);
const SOURCE_FORM_LOC_PATCH_FIELDS = new Set([
  "op",
  "path",
  "span",
  "expected",
  "style",
  "newline",
  "source_length",
]);
const SOURCE_FORM_LOC_PATH_FIELDS = new Set([
  "language",
  "key",
  "occurrence",
]);
const SOURCE_FORM_LOC_SPAN_FIELDS = new Set(["start", "end"]);
const SOURCE_FORM_UPDATE_BATCH_FIELDS = new Set([
  "schema",
  "project_id",
  "changed",
  "counts",
  "updates",
  "source_edits",
]);
const SOURCE_FORM_UPDATE_COUNTS_FIELDS = new Set([
  "requested",
  "changed",
  "unchanged",
]);
const SOURCE_FORM_UPDATE_FIELDS = new Set([
  "schema",
  "project_id",
  "family",
  "module_id",
  "path",
  "relative_path",
  "source_format",
  "form_contract",
  "changed",
  "changes",
  "source_edit",
]);
const SOURCE_FORM_UPDATE_CHANGE_FIELDS = new Set([
  "control_id",
  "previous",
  "value",
]);
const SOURCE_FORM_UPDATE_EDIT_FIELDS = new Set([
  "path",
  "text",
  "expected_size",
  "expected_mtime_ns",
]);
const LOCALIZATION_WORKSPACE_FIELDS = new Set([
  "schema",
  "project_id",
  "target",
  "source_root",
  "languages",
  "rows",
  "sources",
  "coverage",
]);
const LOCALIZATION_SOURCE_FIELDS = new Set([
  "path",
  "relative_path",
  "unit_relative_path",
  "slot",
  "source_format",
  "languages",
  "size",
  "mtime_ns",
]);
const LOCALIZATION_ROW_FIELDS = new Set(["key", "values"]);
const LOCALIZATION_CELL_FIELDS = new Set([
  "text",
  "source_path",
  "relative_path",
  "slot",
  "occurrence",
]);
const LOCALIZATION_COVERAGE_FIELDS = new Set([
  "truncated",
  "shown_rows",
  "total_rows",
]);
const LOCALIZATION_TARGET_FIELDS = new Set([
  "kind",
  "id",
  "family",
  "object_id",
]);
const LOCALIZATION_PLAN_FIELDS = new Set([
  "schema",
  "project_id",
  "target",
  "source_root",
  "operation",
  "changed",
  "changes",
  "source_edits",
  "workspace",
]);

function normalizedProjectLocalizationRequest(
  request: ProjectLocalizationWorkspaceRequest,
): ProjectLocalizationWorkspaceRequest {
  const projectId = request.projectId.trim();
  const targetKind = request.targetKind;
  const targetId = request.targetId.trim();
  if (!projectId) {
    throw new Error("Project localization requests require a project id.");
  }
  if (targetKind !== "module" && targetKind !== "collection") {
    throw new Error("Project localization requests require a module or collection target kind.");
  }
  if (!targetId || (targetKind === "module" && !/^[^/\s]+\/[^/\s]+$/.test(targetId))) {
    throw new Error("Project localization requests require a valid target id.");
  }
  const projectRoot = normalizedPayloadPath(
    request.projectRoot.trim(),
    "project localization request projectRoot",
    true,
  ).value;
  const sourceRoot = request.sourceRoot?.trim();
  const family = request.family?.trim();
  const drafts = request.drafts ?? [];
  if (!Array.isArray(drafts) || drafts.length > 256) {
    throw new Error("Project localization requests support at most 256 source drafts.");
  }
  const seen = new Set<string>();
  const normalizedDrafts = drafts.map((draft, index) => {
    const sourcePath = normalizedPayloadPath(
      draft.sourcePath,
      `project localization request drafts[${index}].sourcePath`,
    ).value;
    const key = payloadPathKey(normalizedPayloadPath(sourcePath, "project localization draft path"));
    if (seen.has(key)) {
      throw new Error("Project localization requests cannot repeat a source draft path.");
    }
    seen.add(key);
    if (typeof draft.text !== "string") {
      throw new Error(`Project localization request drafts[${index}].text must be source text.`);
    }
    return { sourcePath, text: draft.text };
  });
  const limit = request.limit ?? 512;
  if (!Number.isSafeInteger(limit) || limit < 1 || limit > 2048) {
    throw new Error("Project localization request limit must be from 1 to 2048.");
  }
  return {
    projectId,
    projectRoot,
    targetKind,
    targetId,
    ...(family ? { family } : {}),
    ...(sourceRoot
      ? {
          sourceRoot: normalizedPayloadPath(
            sourceRoot,
            "project localization request sourceRoot",
            true,
          ).value,
        }
      : {}),
    drafts: normalizedDrafts,
    limit,
  };
}

function normalizedProjectLocalizationUpdateRequest(
  request: PlanProjectLocalizationUpdateRequest,
): PlanProjectLocalizationUpdateRequest {
  return {
    ...normalizedProjectLocalizationRequest(request),
    operation: normalizedProjectLocalizationOperation(request.operation),
  };
}

function normalizedProjectLocalizationOperation(
  operation: ProjectLocalizationOperation,
): ProjectLocalizationOperation {
  if (!isUnknownRecord(operation)) {
    throw new Error("Project localization operation must be an object.");
  }
  const op = operation.op;
  const key = typeof operation.key === "string" ? operation.key.trim() : "";
  if (op === "set") {
    if (!key || typeof operation.language !== "string" || typeof operation.value !== "string") {
      throw new Error("Project localization set requires language, key, and text value.");
    }
    return {
      op,
      language: operation.language.trim(),
      key,
      value: operation.value,
      ...(typeof operation.source_path === "string" && operation.source_path.trim()
        ? { source_path: normalizedPayloadPath(operation.source_path, "localization source_path").value }
        : {}),
    };
  }
  if (op === "add") {
    if (operation.languages !== undefined && (!Array.isArray(operation.languages) || operation.languages.some((value) => typeof value !== "string" || !value.trim()))) {
      throw new Error("Project localization add languages must be non-empty text values.");
    }
    return {
      op,
      ...(key ? { key } : {}),
      ...(operation.languages === undefined
        ? {}
        : { languages: operation.languages.map((value) => value.trim()) }),
      ...(typeof operation.source_path === "string" && operation.source_path.trim()
        ? { source_path: normalizedPayloadPath(operation.source_path, "localization source_path").value }
        : {}),
    };
  }
  if (op === "rename") {
    const newKey = typeof operation.new_key === "string" ? operation.new_key.trim() : "";
    if (!key || !newKey) {
      throw new Error("Project localization rename requires key and new_key.");
    }
    return { op, key, new_key: newKey };
  }
  if (op === "remove" && key) {
    return { op, key };
  }
  throw new Error("Project localization operation op must be set, add, rename, or remove.");
}

function projectLocalizationWorkspace(
  value: unknown,
  request: ProjectLocalizationWorkspaceRequest,
): ProjectLocalizationWorkspace {
  if (!isUnknownRecord(value)) {
    throw new Error("ParaDev project localization workspace must be an object.");
  }
  validateSourceFormFields(value, LOCALIZATION_WORKSPACE_FIELDS, "project localization workspace");
  if (value.schema !== "paradev.localization-workspace.v2") {
    throw new Error("ParaDev project localization workspace has an unsupported schema.");
  }
  const projectId = requiredPayloadString(value, "project_id", "project localization workspace");
  const targetValue = requiredPayloadRecord(value, "target", "project localization workspace");
  validateSourceFormFields(targetValue, LOCALIZATION_TARGET_FIELDS, "project localization workspace target");
  const targetKind = requiredPayloadString(targetValue, "kind", "project localization workspace target");
  const targetId = requiredPayloadString(targetValue, "id", "project localization workspace target");
  if (
    (targetKind !== "module" && targetKind !== "collection")
    || projectId !== request.projectId
    || targetKind !== request.targetKind
    || targetId !== request.targetId
  ) {
    throw new Error("ParaDev project localization workspace identity does not match the request.");
  }
  const target: ProjectLocalizationWorkspace["target"] = {
    kind: targetKind,
    id: targetId,
    family: requiredPayloadString(targetValue, "family", "project localization workspace target"),
    object_id: requiredPayloadString(targetValue, "object_id", "project localization workspace target"),
  };
  if (request.family && target.family !== request.family) {
    throw new Error("ParaDev project localization workspace family does not match the request.");
  }
  if (!Array.isArray(value.languages)) {
    throw new Error("ParaDev project localization workspace languages must be an array.");
  }
  const languages = value.languages.map((language, index) => {
    if (typeof language !== "string" || !language.startsWith("l_")) {
      throw new Error(`ParaDev project localization workspace language ${index} is invalid.`);
    }
    return language;
  });
  if (new Set(languages).size !== languages.length) {
    throw new Error("ParaDev project localization workspace repeats a language.");
  }
  if (!Array.isArray(value.sources)) {
    throw new Error("ParaDev project localization workspace sources must be an array.");
  }
  const sourcePaths = new Set<string>();
  const sources = value.sources.map((source, index) => {
    const label = `project localization workspace sources[${index}]`;
    if (!isUnknownRecord(source)) {
      throw new Error(`ParaDev ${label} must be an object.`);
    }
    validateSourceFormFields(source, LOCALIZATION_SOURCE_FIELDS, label);
    const path = normalizedPayloadPath(requiredPayloadString(source, "path", label), `${label} path`, true).value;
    if (sourcePaths.has(path)) {
      throw new Error("ParaDev project localization workspace repeats a source path.");
    }
    sourcePaths.add(path);
    if (!Array.isArray(source.languages) || source.languages.some((language) => typeof language !== "string" || !languages.includes(language))) {
      throw new Error(`ParaDev ${label} languages contradict the workspace.`);
    }
    if (source.source_format !== "ini" && source.source_format !== "yaml") {
      throw new Error(`ParaDev ${label} source_format is unsupported.`);
    }
    const sourceFormat: "ini" | "yaml" = source.source_format;
    const mtime = requiredPayloadString(source, "mtime_ns", label);
    if (!/^\d+$/.test(mtime)) {
      throw new Error(`ParaDev ${label} mtime_ns must be an integer string.`);
    }
    return {
      path,
      relative_path: normalizedPayloadPath(requiredPayloadString(source, "relative_path", label), `${label} relative_path`, false).value,
      unit_relative_path: normalizedPayloadPath(requiredPayloadString(source, "unit_relative_path", label), `${label} unit_relative_path`, false).value,
      slot: requiredPayloadString(source, "slot", label),
      source_format: sourceFormat,
      languages: [...source.languages] as string[],
      size: requiredPayloadNonnegativeInteger(source, "size", label),
      mtime_ns: mtime,
    };
  });
  if (!Array.isArray(value.rows)) {
    throw new Error("ParaDev project localization workspace rows must be an array.");
  }
  const rowKeys = new Set<string>();
  const rows = value.rows.map((row, index) => {
    const label = `project localization workspace rows[${index}]`;
    if (!isUnknownRecord(row)) {
      throw new Error(`ParaDev ${label} must be an object.`);
    }
    validateSourceFormFields(row, LOCALIZATION_ROW_FIELDS, label);
    const key = requiredPayloadString(row, "key", label);
    if (rowKeys.has(key) || !isUnknownRecord(row.values)) {
      throw new Error(`ParaDev ${label} has a repeated key or invalid values.`);
    }
    rowKeys.add(key);
    const values: Record<string, ProjectLocalizationWorkspace["rows"][number]["values"][string]> = {};
    for (const [language, cell] of Object.entries(row.values)) {
      const cellLabel = `${label} values.${language}`;
      if (!languages.includes(language) || !isUnknownRecord(cell)) {
        throw new Error(`ParaDev ${cellLabel} is invalid.`);
      }
      validateSourceFormFields(cell, LOCALIZATION_CELL_FIELDS, cellLabel);
      const sourcePath = normalizedPayloadPath(requiredPayloadString(cell, "source_path", cellLabel), `${cellLabel} source_path`, true).value;
      if (!sourcePaths.has(sourcePath)) {
        throw new Error(`ParaDev ${cellLabel} references an unknown source.`);
      }
      if (typeof cell.text !== "string") {
        throw new Error(`ParaDev ${cellLabel} text must be a string.`);
      }
      values[language] = {
        text: cell.text,
        source_path: sourcePath,
        relative_path: normalizedPayloadPath(requiredPayloadString(cell, "relative_path", cellLabel), `${cellLabel} relative_path`, false).value,
        slot: requiredPayloadString(cell, "slot", cellLabel),
        occurrence: requiredPayloadNonnegativeInteger(cell, "occurrence", cellLabel),
      };
    }
    return { key, values };
  });
  const coverageValue = requiredPayloadRecord(value, "coverage", "project localization workspace");
  validateSourceFormFields(coverageValue, LOCALIZATION_COVERAGE_FIELDS, "project localization workspace coverage");
  const shownRows = requiredPayloadNonnegativeInteger(coverageValue, "shown_rows", "project localization workspace coverage");
  const totalRows = requiredPayloadNonnegativeInteger(coverageValue, "total_rows", "project localization workspace coverage");
  const truncated = requiredPayloadBoolean(coverageValue, "truncated", "project localization workspace coverage");
  if (shownRows !== rows.length || shownRows > totalRows || truncated !== (shownRows < totalRows)) {
    throw new Error("ParaDev project localization workspace coverage is inconsistent.");
  }
  return {
    schema: value.schema,
    project_id: projectId,
    target,
    source_root: normalizedPayloadPath(requiredPayloadString(value, "source_root", "project localization workspace"), "project localization workspace source_root", true).value,
    languages,
    rows,
    sources,
    coverage: { truncated, shown_rows: shownRows, total_rows: totalRows },
  };
}

function projectLocalizationUpdatePlan(
  value: unknown,
  request: PlanProjectLocalizationUpdateRequest,
): ProjectLocalizationUpdatePlan {
  if (!isUnknownRecord(value)) {
    throw new Error("ParaDev project localization update plan must be an object.");
  }
  validateSourceFormFields(value, LOCALIZATION_PLAN_FIELDS, "project localization update plan");
  if (value.schema !== "paradev.localization-update-plan.v2") {
    throw new Error("ParaDev project localization update plan has an unsupported schema.");
  }
  const workspace = projectLocalizationWorkspace(value.workspace, request);
  const target = requiredPayloadRecord(value, "target", "project localization update plan");
  validateSourceFormFields(target, LOCALIZATION_TARGET_FIELDS, "project localization update plan target");
  if (
    target.kind !== workspace.target.kind
    || target.id !== workspace.target.id
    || target.family !== workspace.target.family
    || target.object_id !== workspace.target.object_id
  ) {
    throw new Error("ParaDev project localization update target contradicts its workspace.");
  }
  if (!isUnknownRecord(value.operation) || value.operation.op !== request.operation.op) {
    throw new Error("ParaDev project localization update operation contradicts the request.");
  }
  if (!Array.isArray(value.changes) || value.changes.some((change) => !isUnknownRecord(change))) {
    throw new Error("ParaDev project localization update changes must be objects.");
  }
  if (!Array.isArray(value.source_edits)) {
    throw new Error("ParaDev project localization update source_edits must be an array.");
  }
  const sourceEdits = value.source_edits.map((edit, index) => {
    const normalized = sourceFormUpdateSourceEdit(edit, `project localization update source_edits[${index}]`);
    return {
      path: normalized.path,
      text: normalized.text,
      expected_size: normalized.expectedSize ?? 0,
      expected_mtime_ns: normalized.expectedMtimeNs ?? "",
    };
  });
  const changed = requiredPayloadBoolean(value, "changed", "project localization update plan");
  if (changed !== (sourceEdits.length > 0)) {
    throw new Error("ParaDev project localization update changed state is inconsistent.");
  }
  return {
    schema: value.schema,
    project_id: workspace.project_id,
    target: workspace.target,
    source_root: workspace.source_root,
    operation: value.operation as ProjectLocalizationOperation,
    changed,
    changes: value.changes as Array<Record<string, unknown>>,
    source_edits: sourceEdits,
    workspace,
  };
}

function normalizedSourceFormUpdateBatchRequest(
  request: PlanProjectSourceFormUpdatesRequest,
): PlanProjectSourceFormUpdatesRequest {
  const projectId = request.projectId.trim();
  if (!projectId) {
    throw new Error("Guided source update requests require a project id.");
  }
  const projectRoot = normalizedPayloadPath(
    request.projectRoot.trim(),
    "guided source update request projectRoot",
    true,
  ).value;
  if (!Array.isArray(request.updates) || request.updates.length === 0) {
    throw new Error("Guided source update requests require at least one update.");
  }
  if (request.updates.length > 256) {
    throw new Error("Guided source update requests support at most 256 source files.");
  }
  const paths = new Set<string>();
  const updates = request.updates.map((update, index) => {
    if (!isUnknownRecord(update)) {
      throw new Error(`Guided source update ${index} must be an object.`);
    }
    validateSourceFormFields(
      update,
      new Set(["sourcePath", "values", "text", "query"]),
      `guided source update request updates[${index}]`,
    );
    if (typeof update.sourcePath !== "string") {
      throw new Error(
        `Guided source update request updates[${index}].sourcePath must be a path.`,
      );
    }
    const sourcePath = normalizedPayloadPath(
      update.sourcePath.trim(),
      `guided source update request updates[${index}].sourcePath`,
    ).value;
    const pathKey = payloadPathKey(
      normalizedPayloadPath(sourcePath, "guided source update request source path"),
    );
    if (paths.has(pathKey)) {
      throw new Error("Guided source update requests cannot repeat a source path.");
    }
    paths.add(pathKey);
    if (!isUnknownRecord(update.values) || Object.keys(update.values).length === 0) {
      throw new Error(
        `Guided source update request updates[${index}].values must be a non-empty object.`,
      );
    }
    const values: Record<string, SourceFormScalar> = {};
    for (const [controlId, value] of Object.entries(update.values)) {
      if (!controlId.trim()) {
        throw new Error(
          `Guided source update request updates[${index}].values requires non-empty control ids.`,
        );
      }
      values[controlId] = sourceFormScalar(
        value,
        `guided source update request updates[${index}].values.${controlId}`,
      );
    }
    if (update.text !== undefined && typeof update.text !== "string") {
      throw new Error(
        `Guided source update request updates[${index}].text must be source text.`,
      );
    }
    const query = normalizedSourceFormQuery(update.query);
    return {
      sourcePath,
      values,
      ...(update.text === undefined ? {} : { text: update.text }),
      ...(query ? { query } : {}),
    } satisfies SourceFormUpdateRequest;
  });
  return { projectId, projectRoot, updates };
}

function sourceFormUpdateBatchPlan(
  value: unknown,
  request: PlanProjectSourceFormUpdatesRequest,
): SourceFormUpdateBatchPlan {
  if (!isUnknownRecord(value)) {
    throw new Error("ParaDev guided source update response must be an object.");
  }
  validateSourceFormFields(
    value,
    SOURCE_FORM_UPDATE_BATCH_FIELDS,
    "guided source update response",
  );
  if (value.schema !== "paradev.source-form-update-batch.v1") {
    throw new Error("ParaDev guided source update response has an unsupported schema.");
  }
  const projectId = requiredPayloadString(
    value,
    "project_id",
    "guided source update response",
  );
  if (projectId !== request.projectId) {
    throw new Error("ParaDev guided source update response project identity does not match the request.");
  }
  const countsValue = requiredPayloadRecord(
    value,
    "counts",
    "guided source update response",
  );
  validateSourceFormFields(
    countsValue,
    SOURCE_FORM_UPDATE_COUNTS_FIELDS,
    "guided source update response counts",
  );
  const counts = {
    requested: requiredPayloadNonnegativeInteger(
      countsValue,
      "requested",
      "guided source update response counts",
    ),
    changed: requiredPayloadNonnegativeInteger(
      countsValue,
      "changed",
      "guided source update response counts",
    ),
    unchanged: requiredPayloadNonnegativeInteger(
      countsValue,
      "unchanged",
      "guided source update response counts",
    ),
  };
  if (
    counts.requested !== request.updates.length ||
    counts.changed + counts.unchanged !== counts.requested
  ) {
    throw new Error("ParaDev guided source update response counts are inconsistent.");
  }
  if (!Array.isArray(value.updates) || value.updates.length !== request.updates.length) {
    throw new Error("ParaDev guided source update response must contain one ordered plan per request.");
  }
  const updates = value.updates.map((update, index) =>
    sourceFormUpdatePlan(update, request, request.updates[index], index),
  );
  const changedPlans = updates.filter((update) => update.changed);
  const changed = requiredPayloadBoolean(
    value,
    "changed",
    "guided source update response",
  );
  if (counts.changed !== changedPlans.length || changed !== (changedPlans.length > 0)) {
    throw new Error("ParaDev guided source update response changed state is inconsistent.");
  }
  if (!Array.isArray(value.source_edits) || value.source_edits.length !== changedPlans.length) {
    throw new Error("ParaDev guided source update response source_edits are inconsistent.");
  }
  const sourceEdits = value.source_edits.map((edit, index) => {
    const normalized = sourceFormUpdateSourceEdit(
      edit,
      `guided source update response source_edits[${index}]`,
    );
    if (!sameSourceTextEdit(normalized, changedPlans[index].sourceEdit)) {
      throw new Error("ParaDev guided source update response source_edits do not match its changed plans.");
    }
    return normalized;
  });
  return {
    schema: value.schema,
    projectId,
    changed,
    counts,
    updates,
    sourceEdits,
  };
}

function sourceFormUpdatePlan(
  value: unknown,
  request: PlanProjectSourceFormUpdatesRequest,
  requestedUpdate: SourceFormUpdateRequest,
  index: number,
): SourceFormUpdatePlan {
  const label = `guided source update response updates[${index}]`;
  if (!isUnknownRecord(value)) {
    throw new Error(`ParaDev ${label} must be an object.`);
  }
  validateSourceFormFields(value, SOURCE_FORM_UPDATE_FIELDS, label);
  if (value.schema !== "paradev.source-form-update.v1") {
    throw new Error(`ParaDev ${label} has an unsupported schema.`);
  }
  const projectId = requiredPayloadString(value, "project_id", label);
  if (projectId !== request.projectId) {
    throw new Error(`ParaDev ${label} project identity does not match the request.`);
  }
  const path = normalizedPayloadPath(
    requiredPayloadString(value, "path", label),
    `${label} path`,
    true,
  );
  const relativePath = normalizedPayloadPath(
    requiredPayloadString(value, "relative_path", label),
    `${label} relative_path`,
    false,
  );
  const root = normalizedPayloadPath(request.projectRoot, `${label} project root`, true);
  const derivedRelativePath = payloadPathRelativeTo(root, path);
  if (
    derivedRelativePath === undefined ||
    !payloadPathsEqual(
      normalizedPayloadPath(derivedRelativePath, `${label} derived relative path`, false),
      relativePath,
    )
  ) {
    throw new Error(`ParaDev ${label} path is outside the requested project or contradicts relative_path.`);
  }
  const requestedPath = normalizedPayloadPath(
    requestedUpdate.sourcePath,
    `${label} requested source path`,
  );
  if (!payloadPathsEqual(requestedPath, requestedPath.absolute ? path : relativePath)) {
    throw new Error(`ParaDev ${label} source identity does not match the request.`);
  }
  const sourceFormat = value.source_format;
  if (sourceFormat !== "json" && sourceFormat !== "loc" && sourceFormat !== "pdx") {
    throw new Error(`ParaDev ${label} has an unsupported source_format.`);
  }
  if (!Array.isArray(value.changes)) {
    throw new Error(`ParaDev ${label} requires a changes array.`);
  }
  const changes = value.changes.map((change, changeIndex) =>
    sourceFormUpdateChange(
      change,
      requestedUpdate,
      `${label} changes[${changeIndex}]`,
    ),
  );
  const changed = requiredPayloadBoolean(value, "changed", label);
  if (changed !== (changes.length > 0)) {
    throw new Error(`ParaDev ${label} changed state is inconsistent.`);
  }
  const sourceEdit = sourceFormUpdateSourceEdit(value.source_edit, `${label} source_edit`);
  if (!payloadPathsEqual(path, normalizedPayloadPath(sourceEdit.path, `${label} source_edit path`, true))) {
    throw new Error(`ParaDev ${label} source_edit path does not match its source.`);
  }
  return {
    schema: value.schema,
    projectId,
    family: requiredPayloadString(value, "family", label),
    moduleId: requiredPayloadString(value, "module_id", label),
    path: path.value,
    relativePath: relativePath.value,
    sourceFormat,
    formContract: requiredPayloadString(value, "form_contract", label),
    changed,
    changes,
    sourceEdit,
  };
}

function sourceFormUpdateChange(
  value: unknown,
  request: SourceFormUpdateRequest,
  label: string,
): SourceFormUpdateChange {
  if (!isUnknownRecord(value)) {
    throw new Error(`ParaDev ${label} must be an object.`);
  }
  validateSourceFormFields(value, SOURCE_FORM_UPDATE_CHANGE_FIELDS, label);
  const controlId = requiredPayloadString(value, "control_id", label);
  if (!Object.hasOwn(request.values, controlId)) {
    throw new Error(`ParaDev ${label} references a control not present in the request.`);
  }
  const previous = sourceFormScalar(value.previous, `${label} previous`);
  const replacement = sourceFormScalar(value.value, `${label} value`);
  if (!Object.is(replacement, request.values[controlId])) {
    throw new Error(`ParaDev ${label} value does not match the request.`);
  }
  return { controlId, previous, value: replacement };
}

function sourceFormUpdateSourceEdit(value: unknown, label: string): SourceTextEdit {
  if (!isUnknownRecord(value)) {
    throw new Error(`ParaDev ${label} must be an object.`);
  }
  validateSourceFormFields(value, SOURCE_FORM_UPDATE_EDIT_FIELDS, label);
  const path = normalizedPayloadPath(
    requiredPayloadString(value, "path", label),
    `${label} path`,
    true,
  ).value;
  if (typeof value.text !== "string") {
    throw new Error(`ParaDev ${label} requires source text.`);
  }
  const expectedSize = requiredPayloadNonnegativeInteger(value, "expected_size", label);
  const expectedMtimeNs = requiredPayloadString(value, "expected_mtime_ns", label);
  if (!/^\d+$/.test(expectedMtimeNs)) {
    throw new Error(`ParaDev ${label} expected_mtime_ns must be a nonnegative integer string.`);
  }
  return { path, text: value.text, expectedSize, expectedMtimeNs };
}

function sameSourceTextEdit(left: SourceTextEdit, right: SourceTextEdit): boolean {
  return (
    left.path === right.path &&
    left.text === right.text &&
    left.expectedSize === right.expectedSize &&
    left.expectedMtimeNs === right.expectedMtimeNs
  );
}

function normalizedSourceFormRequest(
  request: ReadProjectSourceFormRequest,
): ReadProjectSourceFormRequest {
  const projectId = request.projectId.trim();
  if (!projectId) {
    throw new Error("Project source form requests require a project id.");
  }
  const projectRootText = request.projectRoot.trim();
  if (!projectRootText) {
    throw new Error("Project source form requests require a project root.");
  }
  const projectRoot = normalizedPayloadPath(
    projectRootText,
    "project source form request projectRoot",
    true,
  ).value;
  const sourcePath = normalizedPayloadPath(
    request.sourcePath,
    "project source form request sourcePath",
  ).value;
  if (typeof request.text !== "string") {
    throw new Error("Project source form requests require source text.");
  }
  const query = normalizedSourceFormQuery(request.query);
  return {
    projectId,
    projectRoot,
    sourcePath,
    text: request.text,
    ...(query ? { query } : {}),
  };
}

function normalizedSourceFormQuery(value: unknown): string {
  if (value === undefined || value === null) {
    return "";
  }
  if (typeof value !== "string") {
    throw new Error("Project source form query must be text.");
  }
  const query = value.trim();
  if (query.length > 200) {
    throw new Error("Project source form query must contain at most 200 characters.");
  }
  return query;
}

function sourceFormPayload(
  value: unknown,
  request: ReadProjectSourceFormRequest,
): SourceFormPayload | null {
  if (value === null) {
    return null;
  }
  if (!isUnknownRecord(value)) {
    throw new Error(
      "ParaDev project source form response must be an object or null.",
    );
  }
  validateSourceFormFields(
    value,
    SOURCE_FORM_PAYLOAD_FIELDS,
    "project source form response",
  );
  if (value.schema !== "paradev.source-form.v1") {
    throw new Error(
      "ParaDev project source form response has an unsupported schema.",
    );
  }
  const projectId = requiredPayloadString(
    value,
    "project_id",
    "project source form response",
  );
  if (projectId !== request.projectId) {
    throw new Error(
      "ParaDev project source form response project identity does not match the request.",
    );
  }
  const path = requiredPayloadString(
    value,
    "path",
    "project source form response",
  );
  const relativePath = requiredPayloadString(
    value,
    "relative_path",
    "project source form response",
  );
  const responsePath = normalizedPayloadPath(
    path,
    "project source form response path",
    true,
  );
  const responseRelativePath = normalizedPayloadPath(
    relativePath,
    "project source form response relative_path",
    false,
  );
  const requestRoot = normalizedPayloadPath(
    request.projectRoot,
    "project source form request projectRoot",
  );
  if (requestRoot.absolute) {
    const derivedRelativePath = payloadPathRelativeTo(
      requestRoot,
      responsePath,
    );
    if (
      derivedRelativePath === undefined ||
      !payloadPathsEqual(
        normalizedPayloadPath(
          derivedRelativePath,
          "project source form response project-relative path",
          false,
        ),
        responseRelativePath,
      )
    ) {
      throw new Error(
        "ParaDev project source form response path is outside the requested project or contradicts relative_path.",
      );
    }
  }
  const requestPath = normalizedPayloadPath(
    request.sourcePath,
    "project source form request sourcePath",
  );
  if (
    !payloadPathsEqual(
      requestPath,
      requestPath.absolute ? responsePath : responseRelativePath,
    )
  ) {
    throw new Error(
      "ParaDev project source form response source identity does not match the request.",
    );
  }
  const family = requiredPayloadString(
    value,
    "family",
    "project source form response",
  );
  const moduleId = requiredPayloadString(
    value,
    "module_id",
    "project source form response",
  );
  const moduleRelativePath = requiredPayloadString(
    value,
    "module_relative_path",
    "project source form response",
  );
  normalizedPayloadPath(
    moduleRelativePath,
    "project source form response module_relative_path",
    false,
  );
  const sourceRoot = requiredPayloadString(
    value,
    "source_root",
    "project source form response",
  );
  normalizedPayloadPath(
    sourceRoot,
    "project source form response source_root",
    true,
  );
  const contract = requiredPayloadString(
    value,
    "contract",
    "project source form response",
  );
  if (
    value.source_format !== "json" &&
    value.source_format !== "loc" &&
    value.source_format !== "pdx"
  ) {
    throw new Error(
      "ParaDev project source form response has an unsupported source_format.",
    );
  }
  const sourceFormat = value.source_format;
  const label =
    value.label === undefined
      ? undefined
      : sourceFormText(value.label, "project source form response label");
  const description =
    value.description === undefined
      ? undefined
      : sourceFormText(
          value.description,
          "project source form response description",
        );
  const query = value.query === undefined
    ? undefined
    : requiredPayloadString(value, "query", "project source form response");
  if ((query ?? "") !== (request.query ?? "")) {
    throw new Error(
      "ParaDev project source form response query does not match the request.",
    );
  }
  if (
    !Array.isArray(value.sections)
    || (value.sections.length === 0 && query === undefined)
  ) {
    throw new Error(
      "ParaDev project source form response requires a non-empty sections array.",
    );
  }
  const sectionIds = new Set<string>();
  const controlIds = new Set<string>();
  const sections = value.sections.map((section, index) =>
    sourceFormSection(
      section,
      `project source form response sections[${index}]`,
      sectionIds,
      controlIds,
    ),
  );
  let coverage: SourceFormPayload["coverage"];
  if (value.coverage !== undefined) {
    if (!isUnknownRecord(value.coverage)) {
      throw new Error("ParaDev project source form response coverage must be an object.");
    }
    validateSourceFormFields(
      value.coverage,
      new Set(["truncated", "shown_controls", "total_controls"]),
      "project source form response coverage",
    );
    if (typeof value.coverage.truncated !== "boolean") {
      throw new Error("ParaDev project source form response coverage truncated must be a boolean.");
    }
    const shownControls = sourceFormNonNegativeSafeInteger(
      value.coverage.shown_controls,
      "project source form response coverage shown_controls",
    );
    const totalControls = sourceFormNonNegativeSafeInteger(
      value.coverage.total_controls,
      "project source form response coverage total_controls",
    );
    if (shownControls !== controlIds.size || shownControls > totalControls) {
      throw new Error("ParaDev project source form response coverage contradicts its projected controls.");
    }
    if (value.coverage.truncated !== (shownControls < totalControls)) {
      throw new Error("ParaDev project source form response coverage truncated flag is inconsistent.");
    }
    coverage = {
      truncated: value.coverage.truncated,
      shown_controls: shownControls,
      total_controls: totalControls,
    };
  }
  const expectedPatchOperations: ReadonlySet<SourceFormPatch["op"]> = {
    json: new Set<SourceFormPatch["op"]>(["replace-json-scalar"]),
    loc: new Set<SourceFormPatch["op"]>(["replace-loc-text"]),
    pdx: new Set<SourceFormPatch["op"]>([
      "replace-pdx-scalar",
      "replace-pdx-integer-list",
      "replace-pdx-block-body",
    ]),
  }[sourceFormat];
  const mismatchedPatch = sourceFormPatchOperations(sections).find(
    (operation) => !expectedPatchOperations.has(operation),
  );
  if (mismatchedPatch) {
    const expected = [...expectedPatchOperations].sort().join(" or ");
    throw new Error(
      `ParaDev ${sourceFormat} source forms must use ${expected} patches, not ${mismatchedPatch}.`,
    );
  }
  return {
    schema: value.schema,
    contract,
    project_id: projectId,
    family,
    module_id: moduleId,
    path: responsePath.value,
    relative_path: responseRelativePath.value,
    module_relative_path: moduleRelativePath,
    source_root: sourceRoot,
    source_format: sourceFormat,
    ...(label === undefined ? {} : { label }),
    ...(description === undefined ? {} : { description }),
    ...(query === undefined ? {} : { query }),
    ...(coverage === undefined ? {} : { coverage }),
    sections,
  };
}

function sourceFormText(value: unknown, label: string): SourceFormText {
  if (typeof value === "string") {
    if (!value.trim()) {
      throw new Error(`ParaDev ${label} cannot be empty.`);
    }
    return value;
  }
  if (
    !isUnknownRecord(value) ||
    typeof value.default !== "string" ||
    !value.default.trim()
  ) {
    throw new Error(
      `ParaDev ${label} must be text or a localized text object with a default.`,
    );
  }
  const localized: Record<string, string> = {};
  for (const [locale, text] of Object.entries(value)) {
    if (!locale.trim() || typeof text !== "string" || !text.trim()) {
      throw new Error(
        `ParaDev ${label} localized entries must use non-empty text keys and values.`,
      );
    }
    localized[locale] = text;
  }
  return localized as SourceFormText;
}

function sourceFormScalar(value: unknown, label: string): SourceFormScalar {
  if (typeof value === "string" || typeof value === "boolean") {
    return value;
  }
  if (typeof value === "number" && Number.isFinite(value)) {
    return value;
  }
  throw new Error(`ParaDev ${label} must be a finite JSON scalar.`);
}

function sourceFormPatch(value: unknown, label: string): SourceFormPatch {
  if (!isUnknownRecord(value)) {
    throw new Error(`ParaDev ${label} must be a source scalar patch object.`);
  }
  if (value.op === "replace-json-scalar") {
    validateSourceFormFields(value, SOURCE_FORM_JSON_PATCH_FIELDS, label);
    if (!Array.isArray(value.path) || value.path.length === 0) {
      throw new Error(
        `ParaDev ${label} must be a replace-json-scalar patch with a non-empty path.`,
      );
    }
    const path = value.path.map((segment, index) => {
      if (typeof segment === "string" && segment.trim()) {
        return segment;
      }
      if (
        typeof segment === "number" &&
        Number.isSafeInteger(segment) &&
        segment >= 0
      ) {
        return segment;
      }
      throw new Error(
        `ParaDev ${label} path segment ${index} must be non-empty text or a non-negative integer.`,
      );
    });
    return { op: value.op, path };
  }
  if (value.op === "replace-loc-text") {
    validateSourceFormFields(value, SOURCE_FORM_LOC_PATCH_FIELDS, label);
    if (!isUnknownRecord(value.path)) {
      throw new Error(`ParaDev ${label} replace-loc-text path must be an object.`);
    }
    validateSourceFormFields(
      value.path,
      SOURCE_FORM_LOC_PATH_FIELDS,
      `${label} path`,
    );
    const language = requiredPayloadString(value.path, "language", `${label} path`);
    const key = requiredPayloadString(value.path, "key", `${label} path`);
    if (!language.startsWith("l_")) {
      throw new Error(`ParaDev ${label} localization language must be canonical.`);
    }
    const occurrence = sourceFormNonNegativeSafeInteger(
      value.path.occurrence,
      `${label} path occurrence`,
    );
    if (!isUnknownRecord(value.span)) {
      throw new Error(`ParaDev ${label} span must be an object.`);
    }
    validateSourceFormFields(
      value.span,
      SOURCE_FORM_LOC_SPAN_FIELDS,
      `${label} span`,
    );
    const start = sourceFormNonNegativeSafeInteger(
      value.span.start,
      `${label} span start`,
    );
    const end = sourceFormNonNegativeSafeInteger(
      value.span.end,
      `${label} span end`,
    );
    if (end < start) {
      throw new Error(`ParaDev ${label} span end must not be less than start.`);
    }
    if (typeof value.expected !== "string") {
      throw new Error(`ParaDev ${label} expected must be text.`);
    }
    if (value.expected.length !== end - start) {
      throw new Error(
        `ParaDev ${label} span length must match expected in UTF-16 code units.`,
      );
    }
    if (
      value.style !== "inline" &&
      value.style !== "section" &&
      value.style !== "yaml"
    ) {
      throw new Error(`ParaDev ${label} localization style is unsupported.`);
    }
    if (value.newline !== "\n" && value.newline !== "\r\n") {
      throw new Error(`ParaDev ${label} localization newline is unsupported.`);
    }
    if (value.style !== "section" && /[\r\n]/.test(value.expected)) {
      throw new Error(`ParaDev ${label} ${value.style} expected text must stay on one line.`);
    }
    const sourceLength = sourceFormNonNegativeSafeInteger(
      value.source_length,
      `${label} source_length`,
    );
    if (end > sourceLength) {
      throw new Error(`ParaDev ${label} span must stay inside source_length.`);
    }
    return {
      op: value.op,
      path: { language, key, occurrence },
      span: { start, end },
      expected: value.expected,
      style: value.style,
      newline: value.newline,
      source_length: sourceLength,
    };
  }
  if (value.op === "replace-pdx-integer-list") {
    return sourceFormPdxIntegerListPatch(value, label);
  }
  if (value.op === "replace-pdx-block-body") {
    return sourceFormPdxBlockBodyPatch(value, label);
  }
  if (value.op !== "replace-pdx-scalar") {
    throw new Error(
      `ParaDev ${label} has an unsupported scalar patch operation.`,
    );
  }
  validateSourceFormFields(value, SOURCE_FORM_PDX_PATCH_FIELDS, label);
  if (!Array.isArray(value.path) || value.path.length === 0) {
    throw new Error(
      `ParaDev ${label} replace-pdx-scalar path must be a non-empty array.`,
    );
  }
  const path = value.path.map((segment, index) => {
    const segmentLabel = `${label} path[${index}]`;
    if (!isUnknownRecord(segment)) {
      throw new Error(`ParaDev ${segmentLabel} must be an object.`);
    }
    validateSourceFormFields(
      segment,
      SOURCE_FORM_PDX_PATH_FIELDS,
      segmentLabel,
    );
    const key = requiredPayloadString(segment, "key", segmentLabel);
    if (
      typeof segment.occurrence !== "number" ||
      !Number.isSafeInteger(segment.occurrence) ||
      segment.occurrence < 0
    ) {
      throw new Error(
        `ParaDev ${segmentLabel} occurrence must be a non-negative safe integer.`,
      );
    }
    return { key, occurrence: segment.occurrence };
  });
  if (!isUnknownRecord(value.span)) {
    throw new Error(`ParaDev ${label} span must be an object.`);
  }
  validateSourceFormFields(
    value.span,
    SOURCE_FORM_PDX_SPAN_FIELDS,
    `${label} span`,
  );
  const start = sourceFormNonNegativeSafeInteger(
    value.span.start,
    `${label} span start`,
  );
  const end = sourceFormNonNegativeSafeInteger(
    value.span.end,
    `${label} span end`,
  );
  if (end <= start) {
    throw new Error(`ParaDev ${label} span end must be greater than start.`);
  }
  if (typeof value.expected !== "string" || !value.expected) {
    throw new Error(`ParaDev ${label} expected must be non-empty text.`);
  }
  if (value.expected.length !== end - start) {
    throw new Error(
      `ParaDev ${label} span length must match expected in UTF-16 code units.`,
    );
  }
  if (
    value.scalar_kind !== "boolean" &&
    value.scalar_kind !== "identifier" &&
    value.scalar_kind !== "number" &&
    value.scalar_kind !== "string"
  ) {
    throw new Error(`ParaDev ${label} scalar_kind is unsupported.`);
  }
  const sourceLength = sourceFormNonNegativeSafeInteger(
    value.source_length,
    `${label} source_length`,
  );
  if (end > sourceLength) {
    throw new Error(`ParaDev ${label} span must stay inside source_length.`);
  }
  return {
    op: value.op,
    path,
    span: { start, end },
    expected: value.expected,
    scalar_kind: value.scalar_kind,
    source_length: sourceLength,
  };
}

function sourceFormPdxIntegerListPatch(
  value: Record<string, unknown>,
  label: string,
): SourceFormPatch {
  validateSourceFormFields(
    value,
    SOURCE_FORM_PDX_INTEGER_LIST_PATCH_FIELDS,
    label,
  );
  if (!Array.isArray(value.path) || value.path.length === 0) {
    throw new Error(
      `ParaDev ${label} replace-pdx-integer-list path must be a non-empty array.`,
    );
  }
  const path = value.path.map((segment, index) => {
    const segmentLabel = `${label} path[${index}]`;
    if (!isUnknownRecord(segment)) {
      throw new Error(`ParaDev ${segmentLabel} must be an object.`);
    }
    validateSourceFormFields(
      segment,
      SOURCE_FORM_PDX_PATH_FIELDS,
      segmentLabel,
    );
    const key = requiredPayloadString(segment, "key", segmentLabel);
    const occurrence = sourceFormNonNegativeSafeInteger(
      segment.occurrence,
      `${segmentLabel} occurrence`,
    );
    return { key, occurrence };
  });
  if (!isUnknownRecord(value.span)) {
    throw new Error(`ParaDev ${label} span must be an object.`);
  }
  validateSourceFormFields(
    value.span,
    SOURCE_FORM_PDX_SPAN_FIELDS,
    `${label} span`,
  );
  const start = sourceFormNonNegativeSafeInteger(
    value.span.start,
    `${label} span start`,
  );
  const end = sourceFormNonNegativeSafeInteger(
    value.span.end,
    `${label} span end`,
  );
  if (end <= start) {
    throw new Error(`ParaDev ${label} span end must be greater than start.`);
  }
  if (typeof value.expected !== "string" || !value.expected.trim()) {
    throw new Error(`ParaDev ${label} expected must contain at least one integer.`);
  }
  if (value.expected.length !== end - start) {
    throw new Error(
      `ParaDev ${label} span length must match expected in UTF-16 code units.`,
    );
  }
  if (value.item_kind !== "integer") {
    throw new Error(`ParaDev ${label} item_kind must be integer.`);
  }
  if (
    typeof value.columns !== "number" ||
    !Number.isSafeInteger(value.columns) ||
    value.columns < 1 ||
    value.columns > 16
  ) {
    throw new Error(`ParaDev ${label} columns must be an integer from 1 to 16.`);
  }
  if (typeof value.minimum !== "number" || !Number.isSafeInteger(value.minimum)) {
    throw new Error(`ParaDev ${label} minimum must be a safe integer.`);
  }
  if (!isUnknownRecord(value.layout)) {
    throw new Error(`ParaDev ${label} layout must be an object.`);
  }
  validateSourceFormFields(
    value.layout,
    SOURCE_FORM_PDX_INTEGER_LIST_LAYOUT_FIELDS,
    `${label} layout`,
  );
  const layout = {
    prefix: sourceFormPdxWhitespace(value.layout.prefix, `${label} layout prefix`),
    column_separator: sourceFormPdxWhitespace(
      value.layout.column_separator,
      `${label} layout column_separator`,
      true,
    ),
    row_separator: sourceFormPdxWhitespace(
      value.layout.row_separator,
      `${label} layout row_separator`,
      true,
    ),
    suffix: sourceFormPdxWhitespace(value.layout.suffix, `${label} layout suffix`),
  };
  validateSourceFormPdxIntegerList(
    value.expected,
    value.columns,
    value.minimum,
    `${label} expected`,
  );
  const sourceLength = sourceFormNonNegativeSafeInteger(
    value.source_length,
    `${label} source_length`,
  );
  if (end > sourceLength) {
    throw new Error(`ParaDev ${label} span must stay inside source_length.`);
  }
  return {
    op: "replace-pdx-integer-list",
    path,
    span: { start, end },
    expected: value.expected,
    item_kind: "integer",
    columns: value.columns,
    minimum: value.minimum,
    layout,
    source_length: sourceLength,
  };
}

function sourceFormPdxBlockBodyPatch(
  value: Record<string, unknown>,
  label: string,
): SourceFormPatch {
  validateSourceFormFields(
    value,
    SOURCE_FORM_PDX_BLOCK_BODY_PATCH_FIELDS,
    label,
  );
  if (!Array.isArray(value.path) || value.path.length === 0) {
    throw new Error(
      `ParaDev ${label} replace-pdx-block-body path must be a non-empty array.`,
    );
  }
  const path = value.path.map((segment, index) => {
    const segmentLabel = `${label} path[${index}]`;
    if (!isUnknownRecord(segment)) {
      throw new Error(`ParaDev ${segmentLabel} must be an object.`);
    }
    validateSourceFormFields(
      segment,
      SOURCE_FORM_PDX_PATH_FIELDS,
      segmentLabel,
    );
    const key = requiredPayloadString(segment, "key", segmentLabel);
    const occurrence = sourceFormNonNegativeSafeInteger(
      segment.occurrence,
      `${segmentLabel} occurrence`,
    );
    return { key, occurrence };
  });
  if (!isUnknownRecord(value.span)) {
    throw new Error(`ParaDev ${label} span must be an object.`);
  }
  validateSourceFormFields(
    value.span,
    SOURCE_FORM_PDX_SPAN_FIELDS,
    `${label} span`,
  );
  const start = sourceFormNonNegativeSafeInteger(
    value.span.start,
    `${label} span start`,
  );
  const end = sourceFormNonNegativeSafeInteger(
    value.span.end,
    `${label} span end`,
  );
  if (end < start) {
    throw new Error(`ParaDev ${label} span end must not be less than start.`);
  }
  if (typeof value.expected !== "string") {
    throw new Error(`ParaDev ${label} expected must be text.`);
  }
  if (value.expected.length !== end - start) {
    throw new Error(
      `ParaDev ${label} span length must match expected in UTF-16 code units.`,
    );
  }
  if (!isUnknownRecord(value.layout)) {
    throw new Error(`ParaDev ${label} layout must be an object.`);
  }
  validateSourceFormFields(
    value.layout,
    SOURCE_FORM_PDX_BLOCK_BODY_LAYOUT_FIELDS,
    `${label} layout`,
  );
  const layout = {
    prefix: sourceFormPdxWhitespace(value.layout.prefix, `${label} layout prefix`),
    line_prefix: sourceFormPdxWhitespace(
      value.layout.line_prefix,
      `${label} layout line_prefix`,
      true,
    ),
    suffix: sourceFormPdxWhitespace(value.layout.suffix, `${label} layout suffix`),
  };
  const sourceLength = sourceFormNonNegativeSafeInteger(
    value.source_length,
    `${label} source_length`,
  );
  if (end > sourceLength) {
    throw new Error(`ParaDev ${label} span must stay inside source_length.`);
  }
  return {
    op: "replace-pdx-block-body",
    path,
    span: { start, end },
    expected: value.expected,
    layout,
    source_length: sourceLength,
  };
}

function sourceFormPdxWhitespace(
  value: unknown,
  label: string,
  required = false,
): string {
  if (
    typeof value !== "string" ||
    value.length > 256 ||
    /[^\t\n\r ]/u.test(value) ||
    (required && !value)
  ) {
    throw new Error(`ParaDev ${label} must contain at most 256 whitespace characters.`);
  }
  return value;
}

function validateSourceFormPdxIntegerList(
  value: string,
  columns: number,
  minimum: number,
  label: string,
): void {
  const tokens = value.trim().split(/\s+/u).filter(Boolean);
  if (tokens.length === 0) {
    throw new Error(`ParaDev ${label} must contain at least one integer.`);
  }
  for (const token of tokens) {
    const number = /^-?\d+$/u.test(token) ? Number(token) : Number.NaN;
    if (!Number.isSafeInteger(number) || number < minimum) {
      throw new Error(
        `ParaDev ${label} values must be safe decimal integers of at least ${minimum}.`,
      );
    }
  }
  if (tokens.length % columns !== 0) {
    throw new Error(
      `ParaDev ${label} must contain exactly ${columns} integers per row.`,
    );
  }
}

function sourceFormPatchOperations(
  sections: SourceFormSection[],
): SourceFormPatch["op"][] {
  const operations: SourceFormPatch["op"][] = [];
  const stack = [...sections];
  while (stack.length > 0) {
    const section = stack.pop();
    if (!section) {
      continue;
    }
    for (const control of section.controls ?? []) {
      if (control.patch && !operations.includes(control.patch.op)) {
        operations.push(control.patch.op);
      }
    }
    stack.push(...(section.sections ?? []));
  }
  return operations;
}

function sourceFormNonNegativeSafeInteger(
  value: unknown,
  label: string,
): number {
  if (typeof value !== "number" || !Number.isSafeInteger(value) || value < 0) {
    throw new Error(`ParaDev ${label} must be a non-negative safe integer.`);
  }
  return value;
}

function sourceFormChoice(value: unknown, label: string): SourceFormChoice {
  if (!isUnknownRecord(value)) {
    throw new Error(`ParaDev ${label} must be an object.`);
  }
  validateSourceFormFields(value, SOURCE_FORM_CHOICE_FIELDS, label);
  return {
    label: sourceFormText(value.label, `${label} label`),
    value: sourceFormScalar(value.value, `${label} value`),
  };
}

function sourceFormControl(
  value: unknown,
  label: string,
  controlIds: Set<string>,
): SourceFormControl {
  if (!isUnknownRecord(value)) {
    throw new Error(`ParaDev ${label} must be an object.`);
  }
  validateSourceFormFields(value, SOURCE_FORM_CONTROL_FIELDS, label);
  const id = requiredPayloadString(value, "id", label);
  if (controlIds.has(id)) {
    throw new Error(
      `ParaDev project source form response repeats control id ${id}.`,
    );
  }
  controlIds.add(id);
  const control = value.control;
  if (
    control !== "readonly" &&
    control !== "text" &&
    control !== "number" &&
    control !== "boolean" &&
    control !== "choice"
  ) {
    throw new Error(`ParaDev ${label} has an unsupported control kind.`);
  }
  const scalar = sourceFormScalar(value.value, `${label} value`);
  if (
    (control === "text" && typeof scalar !== "string") ||
    (control === "number" && typeof scalar !== "number") ||
    (control === "boolean" && typeof scalar !== "boolean")
  ) {
    throw new Error(`ParaDev ${label} value does not match its control kind.`);
  }
  const patch =
    value.patch === undefined
      ? undefined
      : sourceFormPatch(value.patch, `${label} patch`);
  if ((control === "readonly") === (patch !== undefined)) {
    throw new Error(
      `ParaDev ${label} must define a patch exactly when it is editable.`,
    );
  }
  let choices: SourceFormChoice[] | undefined;
  if (value.choices !== undefined) {
    if (!Array.isArray(value.choices)) {
      throw new Error(`ParaDev ${label} choices must be an array.`);
    }
    choices = value.choices.map((choice, index) =>
      sourceFormChoice(choice, `${label} choices[${index}]`),
    );
    if (
      choices.some((choice, index) =>
        choices
          ?.slice(0, index)
          .some(
            (previous) =>
              typeof previous.value === typeof choice.value &&
              previous.value === choice.value,
          ),
      )
    ) {
      throw new Error(`ParaDev ${label} choices must not repeat values.`);
    }
  }
  if (control === "choice" ? !choices?.length : choices !== undefined) {
    throw new Error(`ParaDev ${label} choices do not match its control kind.`);
  }
  if (
    control === "choice" &&
    choices?.some((choice) => typeof choice.value !== typeof scalar)
  ) {
    throw new Error(
      `ParaDev ${label} choices must use the same JSON scalar kind as its value.`,
    );
  }
  if (
    control === "choice" &&
    !choices?.some(
      (choice) =>
        typeof choice.value === typeof scalar && choice.value === scalar,
    )
  ) {
    throw new Error(`ParaDev ${label} value must match one of its choices.`);
  }
  const min = sourceFormOptionalNumber(value.min, `${label} min`);
  const max = sourceFormOptionalNumber(value.max, `${label} max`);
  const step = sourceFormOptionalNumber(value.step, `${label} step`);
  if (step !== undefined && step <= 0) {
    throw new Error(`ParaDev ${label} step must be greater than zero.`);
  }
  if (min !== undefined && max !== undefined && min > max) {
    throw new Error(`ParaDev ${label} min cannot be greater than max.`);
  }
  if (
    control !== "number" &&
    (min !== undefined || max !== undefined || step !== undefined)
  ) {
    throw new Error(
      `ParaDev ${label} numeric bounds require a number control.`,
    );
  }
  const description =
    value.description === undefined
      ? undefined
      : sourceFormText(value.description, `${label} description`);
  let descriptionSource: "declared" | "generated" | undefined;
  if (value.description_source !== undefined) {
    if (value.description_source !== "declared" && value.description_source !== "generated") {
      throw new Error(`ParaDev ${label} description_source is unsupported.`);
    }
    if (description === undefined) {
      throw new Error(`ParaDev ${label} description_source requires a description.`);
    }
    descriptionSource = value.description_source;
  }
  const placeholder =
    value.placeholder === undefined
      ? undefined
      : sourceFormText(value.placeholder, `${label} placeholder`);
  if (
    placeholder !== undefined &&
    control !== "text" &&
    control !== "number" &&
    control !== "choice"
  ) {
    throw new Error(
      `ParaDev ${label} placeholder requires a text, number, or choice control.`,
    );
  }
  let multiline: boolean | undefined;
  if (value.multiline !== undefined) {
    if (typeof value.multiline !== "boolean") {
      throw new Error(`ParaDev ${label} multiline must be a boolean.`);
    }
    if (control !== "text") {
      throw new Error(`ParaDev ${label} multiline requires a text control.`);
    }
    multiline = value.multiline;
  }
  const common = {
    id,
    label: sourceFormText(value.label, `${label} label`),
    ...(description === undefined ? {} : { description }),
    ...(descriptionSource === undefined ? {} : { description_source: descriptionSource }),
  };
  if (control === "readonly") {
    return { ...common, control, value: scalar };
  }
  if (!patch) {
    throw new Error(
      `ParaDev ${label} must define a patch when it is editable.`,
    );
  }
  if (control === "text") {
    if (typeof scalar !== "string") {
      throw new Error(
        `ParaDev ${label} value does not match its text control kind.`,
      );
    }
    return {
      ...common,
      control,
      value: scalar,
      patch,
      ...(multiline === undefined ? {} : { multiline }),
      ...(placeholder === undefined ? {} : { placeholder }),
    };
  }
  if (control === "number") {
    if (typeof scalar !== "number") {
      throw new Error(
        `ParaDev ${label} value does not match its number control kind.`,
      );
    }
    return {
      ...common,
      control,
      value: scalar,
      patch,
      ...(min === undefined ? {} : { min }),
      ...(max === undefined ? {} : { max }),
      ...(step === undefined ? {} : { step }),
      ...(placeholder === undefined ? {} : { placeholder }),
    };
  }
  if (control === "boolean") {
    if (typeof scalar !== "boolean") {
      throw new Error(
        `ParaDev ${label} value does not match its boolean control kind.`,
      );
    }
    return { ...common, control, value: scalar, patch };
  }
  if (!choices) {
    throw new Error(
      `ParaDev ${label} must define choices for its choice control kind.`,
    );
  }
  return {
    ...common,
    control,
    value: scalar,
    patch,
    choices,
    ...(placeholder === undefined ? {} : { placeholder }),
  };
}

function sourceFormOptionalNumber(
  value: unknown,
  label: string,
): number | undefined {
  if (value === undefined) {
    return undefined;
  }
  if (typeof value !== "number" || !Number.isFinite(value)) {
    throw new Error(`ParaDev ${label} must be a finite number.`);
  }
  return value;
}

function sourceFormSection(
  value: unknown,
  label: string,
  sectionIds: Set<string>,
  controlIds: Set<string>,
): SourceFormSection {
  if (!isUnknownRecord(value)) {
    throw new Error(`ParaDev ${label} must be an object.`);
  }
  validateSourceFormFields(value, SOURCE_FORM_SECTION_FIELDS, label);
  const id = requiredPayloadString(value, "id", label);
  if (sectionIds.has(id)) {
    throw new Error(
      `ParaDev project source form response repeats section id ${id}.`,
    );
  }
  sectionIds.add(id);
  let controls: SourceFormControl[] | undefined;
  if (value.controls !== undefined) {
    if (!Array.isArray(value.controls) || value.controls.length === 0) {
      throw new Error(
        `ParaDev ${label} controls must be a non-empty array when present.`,
      );
    }
    controls = value.controls.map((control, index) =>
      sourceFormControl(control, `${label} controls[${index}]`, controlIds),
    );
  }
  let sections: SourceFormSection[] | undefined;
  if (value.sections !== undefined) {
    if (!Array.isArray(value.sections) || value.sections.length === 0) {
      throw new Error(
        `ParaDev ${label} sections must be a non-empty array when present.`,
      );
    }
    sections = value.sections.map((section, index) =>
      sourceFormSection(
        section,
        `${label} sections[${index}]`,
        sectionIds,
        controlIds,
      ),
    );
  }
  if (!controls?.length && !sections?.length) {
    throw new Error(
      `ParaDev ${label} must contain controls or nested sections.`,
    );
  }
  return {
    id,
    label: sourceFormText(value.label, `${label} label`),
    ...(value.description === undefined
      ? {}
      : {
          description: sourceFormText(
            value.description,
            `${label} description`,
          ),
        }),
    ...(controls === undefined ? {} : { controls }),
    ...(sections === undefined ? {} : { sections }),
  };
}

function validateSourceFormFields(
  value: Record<string, unknown>,
  allowed: ReadonlySet<string>,
  label: string,
): void {
  const unknown = Object.keys(value)
    .filter((key) => !allowed.has(key))
    .sort();
  if (unknown.length > 0) {
    throw new Error(
      `ParaDev ${label} contains unsupported fields: ${unknown.join(", ")}.`,
    );
  }
}

function projectCatalogStatusPayload(
  value: unknown,
): ProjectCatalogStatusPayload {
  if (!isUnknownRecord(value)) {
    throw new Error(
      "ParaDev project catalog status response must be an object.",
    );
  }
  const expectedKeys = ["schema", "project_id", "database", "status", "code"];
  if (
    Object.keys(value).length !== expectedKeys.length ||
    expectedKeys.some((key) => !Object.hasOwn(value, key))
  ) {
    throw new Error(
      "ParaDev project catalog status response did not match the exact payload shape.",
    );
  }
  if (value.schema !== "paradev.hb.catalog-status.v1") {
    throw new Error(
      "ParaDev project catalog status response has an unsupported schema.",
    );
  }
  if (typeof value.project_id !== "string" || !value.project_id.trim()) {
    throw new Error(
      "ParaDev project catalog status response requires a project_id.",
    );
  }
  if (typeof value.database !== "string" || !value.database.trim()) {
    throw new Error(
      "ParaDev project catalog status response requires a database path.",
    );
  }
  const identity = {
    schema: value.schema,
    project_id: value.project_id,
    database: value.database,
  } as const;
  switch (value.status) {
    case "present":
      if (value.code !== "catalog.present") break;
      return { ...identity, status: value.status, code: value.code };
    case "missing":
      if (value.code !== "catalog.missing") break;
      return { ...identity, status: value.status, code: value.code };
    case "incomplete":
      if (value.code !== "catalog.incomplete") break;
      return { ...identity, status: value.status, code: value.code };
    case "unreadable":
      if (value.code !== "catalog.unreadable") break;
      return { ...identity, status: value.status, code: value.code };
  }
  throw new Error(
    "ParaDev project catalog status response has an invalid status/code pair.",
  );
}

async function loadProjectCatalogStatusUncached(
  request: ProjectCatalogStatusRequest,
): Promise<ProjectCatalogStatusPayload> {
  let payload: unknown;
  if (hasNativeBridge()) {
    payload = await bridgeGetJson<unknown>("/projects/catalog", {
      path: request.projectRoot,
    });
  } else {
    throw new Error(
      "Loading the project catalog status requires the ParaDev desktop application.",
    );
  }
  return projectCatalogStatusPayload(payload);
}

function projectCatalogReadinessMessage(
  status: ProjectCatalogStatusPayload,
): string {
  switch (status.code) {
    case "catalog.missing":
      return "The optional project index is not prepared.";
    case "catalog.incomplete":
      return "The project index is incomplete. Repair it before using indexed search.";
    case "catalog.unreadable":
      return "The project index cannot be read. Check its permissions, then repair it.";
    case "catalog.present":
      return "The project index is ready.";
  }
}

function moduleDraftPayload(
  value: unknown,
  request: CreateModuleDraftRequest,
): ModuleDraftPayload {
  if (!isUnknownRecord(value) || !isUnknownRecord(value.plan)) {
    throw new Error(
      "ParaDev module draft response must include an object plan.",
    );
  }
  if (value.schema !== "paradev.rest.module_draft.v1") {
    throw new Error("ParaDev module draft response has an unsupported schema.");
  }
  const projectId = requiredPayloadString(
    value,
    "project_id",
    "module draft response",
  );
  const familyId = requiredPayloadString(
    value,
    "family_id",
    "module draft response",
  );
  const draftId = requiredPayloadString(
    value,
    "draft_id",
    "module draft response",
  );
  if (value.plan.schema !== "paradev.sdk.module_scaffold.v1") {
    throw new Error("ParaDev module draft plan has an unsupported schema.");
  }
  const planProjectId = requiredPayloadString(
    value.plan,
    "project_id",
    "module draft plan",
  );
  const templateId = requiredPayloadString(
    value.plan,
    "template_id",
    "module draft plan",
  );
  const family = requiredPayloadString(
    value.plan,
    "family",
    "module draft plan",
  );
  const objectId = requiredPayloadString(
    value.plan,
    "object_id",
    "module draft plan",
  );
  const moduleId = requiredPayloadString(
    value.plan,
    "module_id",
    "module draft plan",
  );
  const sourceRoot = requiredPayloadString(
    value.plan,
    "source_root",
    "module draft plan",
  );
  const root = requiredPayloadString(value.plan, "root", "module draft plan");
  requiredPayloadStringRecord(value.plan, "values", "module draft plan");
  const blocked = requiredPayloadBoolean(
    value.plan,
    "blocked",
    "module draft plan",
  );
  const written = requiredPayloadBoolean(
    value.plan,
    "written",
    "module draft plan",
  );
  requiredPayloadRecordArray(value.plan, "diagnostics", "module draft plan");
  validateModuleScaffoldFiles(value.plan, root, blocked, request);
  if (projectId !== planProjectId) {
    throw new Error(
      "ParaDev module draft response project identity does not match its plan.",
    );
  }
  if (
    projectId !== request.projectId.trim() ||
    familyId !== request.familyId.trim()
  ) {
    throw new Error(
      "ParaDev module draft response identity does not match the request.",
    );
  }
  if (blocked && written) {
    throw new Error(
      "ParaDev module draft plan cannot be both blocked and written.",
    );
  }
  if (
    (request.templateId?.trim() && templateId !== request.templateId.trim()) ||
    objectId !== request.objectId.trim()
  ) {
    throw new Error(
      "ParaDev module draft response identity does not match the request.",
    );
  }
  if (
    moduleId !== `${family}/${objectId}` ||
    draftId !== `${familyId}:${objectId}`
  ) {
    throw new Error(
      "ParaDev module draft response module identity is inconsistent.",
    );
  }
  if (written !== (request.write === true && !blocked)) {
    throw new Error(
      "ParaDev module draft response write result does not match the request.",
    );
  }
  const moduleRoot = modulePayloadRoot(
    root,
    family,
    objectId,
    "module draft plan",
  );
  validateOptionalModuleFolderName(
    value.plan,
    moduleRoot.root,
    "module draft plan",
  );
  if (
    !payloadPathsEqual(
      moduleRoot.sourceRoot,
      normalizedPayloadPath(sourceRoot, "module draft plan source_root", true),
    )
  ) {
    throw new Error(
      "ParaDev module draft response root does not match its source_root.",
    );
  }
  const catalogMutation = catalogMutationForSourceOperation(
    value.plan,
    "module draft plan",
    written,
  );
  return {
    ...value,
    plan: {
      ...value.plan,
      ...(catalogMutation ? { catalog_mutation: catalogMutation } : {}),
    },
  } as ModuleDraftPayload;
}

function moduleCreateBatchPayload(
  value: unknown,
  request: CreateModulesRequest,
): ModuleCreateBatchPayload {
  if (!isUnknownRecord(value)) {
    throw new Error("ParaDev module batch response must be an object.");
  }
  if (value.schema !== "paradev.sdk.module_batch.v1") {
    throw new Error("ParaDev module batch response has an unsupported schema.");
  }
  const projectId = requiredPayloadString(
    value,
    "project_id",
    "module batch response",
  );
  const sourceRoot = normalizedPayloadPath(
    requiredPayloadString(value, "source_root", "module batch response"),
    "module batch response source_root",
    true,
  );
  const planHash = requiredPayloadString(
    value,
    "plan_hash",
    "module batch response",
  );
  if (!/^[0-9a-f]{64}$/.test(planHash)) {
    throw new Error(
      "ParaDev module batch response requires a lowercase SHA-256 plan_hash.",
    );
  }
  const blocked = requiredPayloadBoolean(
    value,
    "blocked",
    "module batch response",
  );
  const applied = requiredPayloadBoolean(
    value,
    "applied",
    "module batch response",
  );
  const written = requiredPayloadBoolean(
    value,
    "written",
    "module batch response",
  );
  const requestedCount = requiredPayloadNonnegativeInteger(
    value,
    "requested_count",
    "module batch response",
  );
  const counts = requiredPayloadRecord(
    value,
    "counts",
    "module batch response",
  );
  const statuses = ["create", "created", "unchanged", "blocked"] as const;
  const normalizedCounts = Object.fromEntries(
    statuses.map((status) => [
      status,
      requiredPayloadNonnegativeInteger(
        counts,
        status,
        "module batch response counts",
      ),
    ]),
  ) as ModuleCreateBatchPayload["counts"];
  if (
    Object.keys(counts).length !== statuses.length ||
    statuses.some((status) => !Object.hasOwn(counts, status))
  ) {
    throw new Error(
      "ParaDev module batch response counts must contain only known statuses.",
    );
  }
  const diagnostics = requiredPayloadRecordArray(
    value,
    "diagnostics",
    "module batch response",
  );
  diagnostics.forEach((diagnostic, index) =>
    validateModuleBatchDiagnostic(
      diagnostic,
      `module batch response diagnostic ${index}`,
      sourceRoot,
    ),
  );
  const modules = requiredPayloadRecordArray(
    value,
    "modules",
    "module batch response",
  );

  if (projectId !== request.projectId.trim()) {
    throw new Error(
      "ParaDev module batch response project identity does not match the request.",
    );
  }
  validateRequestedSourceRoot(
    request.projectRoot,
    request.sourceRoot ?? undefined,
    sourceRoot,
    "module batch response",
  );
  if (
    requestedCount !== request.modules.length ||
    modules.length !== requestedCount
  ) {
    throw new Error(
      "ParaDev module batch response requested_count does not match its request and modules.",
    );
  }
  if (
    Object.values(normalizedCounts).reduce(
      (total, count) => total + count,
      0,
    ) !== requestedCount
  ) {
    throw new Error(
      "ParaDev module batch response counts do not total requested_count.",
    );
  }
  if (
    !blocked &&
    (normalizedCounts.blocked > 0 ||
      diagnostics.some((diagnostic) => diagnostic.severity === "error"))
  ) {
    throw new Error(
      "ParaDev module batch response reports blocking rows or diagnostics without blocked state.",
    );
  }
  if ((applied && blocked) || (written && !applied)) {
    throw new Error(
      "ParaDev module batch response has an invalid blocked/applied/written state.",
    );
  }
  if (
    applied &&
    (!request.planHash?.trim() || planHash !== request.planHash.trim())
  ) {
    throw new Error(
      "ParaDev module batch response plan_hash does not match the applied request.",
    );
  }
  if (
    (!applied && normalizedCounts.created > 0) ||
    (applied &&
      (normalizedCounts.create > 0 || normalizedCounts.blocked > 0)) ||
    written !== normalizedCounts.created > 0
  ) {
    throw new Error(
      "ParaDev module batch response counts do not match its apply state.",
    );
  }
  if (request.write !== true && (applied || written)) {
    throw new Error(
      "ParaDev module batch dry plan cannot report applied or written files.",
    );
  }
  if (request.write === true && !applied && !blocked) {
    throw new Error(
      "ParaDev module batch apply must report either applied or blocked state.",
    );
  }

  const normalizedModules = modules.map((module, index) => {
    const label = `module batch response module ${index}`;
    const responseIndex = requiredPayloadNonnegativeInteger(
      module,
      "index",
      label,
    );
    const objectId = requiredPayloadString(module, "object_id", label);
    const templateId = requiredPayloadString(module, "template_id", label);
    const family = requiredPayloadString(module, "family", label);
    const moduleId = requiredPayloadString(module, "module_id", label);
    const rootValue = requiredPayloadString(module, "root", label);
    const status = requiredPayloadString(module, "status", label);
    const moduleBlocked = requiredPayloadBoolean(module, "blocked", label);
    const moduleDiagnostics = requiredPayloadRecordArray(
      module,
      "diagnostics",
      label,
    );
    const moduleFiles = requiredPayloadRecordArray(module, "files", label);
    moduleDiagnostics.forEach((diagnostic, diagnosticIndex) =>
      validateModuleBatchDiagnostic(
        diagnostic,
        `${label} diagnostic ${diagnosticIndex}`,
        sourceRoot,
      ),
    );
    if (
      responseIndex !== index ||
      objectId !== request.modules[index]?.object_id.trim() ||
      !statuses.includes(status as (typeof statuses)[number])
    ) {
      throw new Error(
        `ParaDev ${label} identity or status does not match the request.`,
      );
    }
    const requestedModule = request.modules[index];
    const selectorMatches =
      (typeof requestedModule?.template_id === "string" &&
        templateId === requestedModule.template_id.trim()) ||
      (typeof requestedModule?.family === "string" &&
        family === requestedModule.family.trim()) ||
      (typeof requestedModule?.family_or_template === "string" &&
        [templateId, family].includes(
          requestedModule.family_or_template.trim(),
        ));
    if (!selectorMatches) {
      throw new Error(
        `ParaDev ${label} template or family does not match the request.`,
      );
    }
    const [moduleFamily, moduleObjectId] = moduleIdParts(moduleId, label);
    if (moduleFamily !== family || moduleObjectId !== objectId) {
      throw new Error(`ParaDev ${label} module identity is inconsistent.`);
    }
    const moduleRoot = modulePayloadRoot(
      rootValue,
      family,
      objectId,
      `${label} root`,
    );
    validateOptionalModuleFolderName(module, moduleRoot.root, label);
    if (!payloadPathsEqual(moduleRoot.sourceRoot, sourceRoot)) {
      throw new Error(
        `ParaDev ${label} root does not match the batch source_root.`,
      );
    }
    if ((status === "blocked") !== moduleBlocked) {
      throw new Error(
        `ParaDev ${label} blocked state does not match its status.`,
      );
    }
    if (
      !moduleBlocked &&
      moduleDiagnostics.some((diagnostic) => diagnostic.severity === "error")
    ) {
      throw new Error(
        `ParaDev ${label} reports an error diagnostic without blocked state.`,
      );
    }
    validateModuleBatchFiles(
      moduleFiles,
      moduleRoot.root,
      request.projectRoot,
      status,
      label,
    );
    const catalogMutation =
      status === "created"
        ? catalogMutationForSourceOperation(module, label, true)
        : undefined;
    return {
      ...module,
      ...(catalogMutation ? { catalog_mutation: catalogMutation } : {}),
    };
  });
  for (const status of statuses) {
    if (
      modules.filter((module) => module.status === status).length !==
      normalizedCounts[status]
    ) {
      throw new Error(
        `ParaDev module batch response count for ${status} does not match its modules.`,
      );
    }
  }
  return {
    ...value,
    counts: normalizedCounts,
    diagnostics,
    modules: normalizedModules,
  } as ModuleCreateBatchPayload;
}

function collectionScaffoldPayload(
  value: unknown,
  request: ScaffoldCollectionRequest,
): CollectionScaffoldPayload {
  if (!isUnknownRecord(value)) {
    throw new Error("ParaDev collection scaffold response must be an object.");
  }
  if (value.schema !== "paradev.sdk.collection_scaffold.v1") {
    throw new Error(
      "ParaDev collection scaffold response has an unsupported schema.",
    );
  }
  requiredPayloadString(value, "project_id", "collection scaffold response");
  const templateId = requiredPayloadString(
    value,
    "template_id",
    "collection scaffold response",
  );
  const family = requiredPayloadString(
    value,
    "family",
    "collection scaffold response",
  );
  const collectionId = requiredPayloadString(
    value,
    "collection_id",
    "collection scaffold response",
  );
  const objectId = requiredPayloadString(
    value,
    "object_id",
    "collection scaffold response",
  );
  const sourceRoot = normalizedPayloadPath(
    requiredPayloadString(value, "source_root", "collection scaffold response"),
    "collection scaffold source_root",
    true,
  );
  const root = collectionPayloadRoot(
    requiredPayloadString(value, "root", "collection scaffold response"),
    family,
    collectionId,
    "collection scaffold response root",
  );
  const folderName = requiredPayloadString(
    value,
    "folder_name",
    "collection scaffold response",
  );
  const planHash = requiredPayloadString(
    value,
    "plan_hash",
    "collection scaffold response",
  );
  const blocked = requiredPayloadBoolean(
    value,
    "blocked",
    "collection scaffold response",
  );
  const written = requiredPayloadBoolean(
    value,
    "written",
    "collection scaffold response",
  );
  requiredPayloadStringRecord(value, "values", "collection scaffold response");
  requiredPayloadRecordArray(
    value,
    "diagnostics",
    "collection scaffold response",
  );
  requiredPayloadRecordArray(value, "files", "collection scaffold response");
  requiredPayloadRecord(
    value,
    "authoring_plan",
    "collection scaffold response",
  );
  if (value.kind !== "collection") {
    throw new Error(
      "ParaDev collection scaffold response has an invalid target kind.",
    );
  }
  if (
    templateId !== request.templateId.trim() ||
    collectionId !== request.collectionId.trim() ||
    objectId !== collectionId
  ) {
    throw new Error(
      "ParaDev collection scaffold response identity does not match the request.",
    );
  }
  if (!/^[0-9a-f]{64}$/.test(planHash)) {
    throw new Error(
      "ParaDev collection scaffold response requires a lowercase SHA-256 plan_hash.",
    );
  }
  if (blocked && written) {
    throw new Error(
      "ParaDev collection scaffold response cannot be both blocked and written.",
    );
  }
  if (request.write !== true && written) {
    throw new Error(
      "ParaDev collection scaffold dry plan cannot report written files.",
    );
  }
  if (
    request.write === true &&
    !blocked &&
    (!request.planHash?.trim() ||
      request.planHash.trim() !== planHash ||
      !written)
  ) {
    throw new Error(
      "ParaDev collection scaffold apply does not match its exact plan_hash.",
    );
  }
  if (
    folderName !== payloadPathBasename(root.root) ||
    !payloadPathsEqual(root.sourceRoot, sourceRoot)
  ) {
    throw new Error(
      "ParaDev collection scaffold response root is inconsistent.",
    );
  }
  validateRequestedSourceRoot(
    request.projectRoot,
    request.sourceRoot ?? undefined,
    sourceRoot,
    "collection scaffold response",
  );
  return value as CollectionScaffoldPayload;
}

function validateModuleBatchDiagnostic(
  diagnostic: Record<string, unknown>,
  label: string,
  sourceRoot: NormalizedPayloadPath,
): void {
  const code = requiredPayloadString(diagnostic, "code", label);
  requiredPayloadString(diagnostic, "message", label);
  const severity = requiredPayloadString(diagnostic, "severity", label);
  if (!["error", "info", "warning"].includes(severity)) {
    throw new Error(`ParaDev ${label} has an unsupported severity.`);
  }
  if (
    code === "module_batch.rollback_incomplete" &&
    (typeof diagnostic.recovery_path !== "string" ||
      !diagnostic.recovery_path.trim())
  ) {
    throw new Error(
      `ParaDev ${label} requires recovery_path for incomplete rollback.`,
    );
  }
  if (diagnostic.recovery_path !== undefined) {
    const recoveryPath = normalizedPayloadPath(
      requiredPayloadString(diagnostic, "recovery_path", label),
      `${label} recovery_path`,
      true,
    );
    const transactionRoot = joinedPayloadPath(
      sourceRoot,
      normalizedPayloadPath(
        ".paradev/module-transactions",
        `${label} transaction root`,
        false,
      ),
      `${label} transaction root`,
    );
    const transactionRelativePath = payloadPathRelativeTo(
      transactionRoot,
      recoveryPath,
    );
    if (!transactionRelativePath) {
      throw new Error(
        `ParaDev ${label} recovery_path must identify retained data under the module transaction root.`,
      );
    }
  }
}

function validateModuleBatchFiles(
  files: Array<Record<string, unknown>>,
  moduleRoot: NormalizedPayloadPath,
  projectRoot: string,
  status: string,
  label: string,
): void {
  const expectedAction =
    status === "blocked"
      ? "blocked"
      : status === "unchanged"
        ? "unchanged"
        : "create";
  for (const [index, file] of files.entries()) {
    const fileLabel = `${label} file ${index}`;
    const path = normalizedPayloadPath(
      requiredPayloadString(file, "path", fileLabel),
      `${fileLabel} path`,
      true,
    );
    const modulePath = normalizedPayloadPath(
      requiredPayloadString(file, "module_path", fileLabel),
      `${fileLabel} module_path`,
      false,
    );
    const expectedPath = joinedPayloadPath(
      moduleRoot,
      modulePath,
      `${fileLabel} path`,
    );
    if (!payloadPathsEqual(path, expectedPath)) {
      throw new Error(
        `ParaDev ${fileLabel} path does not match its module_path.`,
      );
    }
    validateProjectRelativePayloadPath(
      projectRoot,
      path.value,
      requiredPayloadString(file, "relative_path", fileLabel),
      `${fileLabel} relative_path`,
    );
    if (requiredPayloadString(file, "action", fileLabel) !== expectedAction) {
      throw new Error(
        `ParaDev ${fileLabel} action does not match its module status.`,
      );
    }
  }
}

function projectPreferredLanguagePayload(
  value: unknown,
  request: ProjectPreferredLanguageRequest,
): ProjectPreferredLanguagePayload {
  if (!isUnknownRecord(value)) {
    throw new Error("ParaDev project language response must be an object.");
  }
  if (value.schema !== "paradev.project.preferred-language.v1") {
    throw new Error(
      "ParaDev project language response has an unsupported schema.",
    );
  }
  requiredPayloadString(value, "project_id", "project language response");
  requiredPayloadString(value, "manifest", "project language response");
  requiredPayloadString(
    value,
    "previous_language",
    "project language response",
  );
  const preferredLanguage = requiredPayloadString(
    value,
    "preferred_language",
    "project language response",
  );
  const expectedLanguage = request.preferredLanguage
    .trim()
    .toLowerCase()
    .replaceAll("-", "_");
  if (preferredLanguage !== expectedLanguage) {
    throw new Error(
      "ParaDev project language response does not match the requested language.",
    );
  }
  requiredPayloadBoolean(value, "changed", "project language response");
  requiredPayloadBoolean(value, "written", "project language response");
  requiredPayloadBoolean(value, "blocked", "project language response");
  if (!Array.isArray(value.diagnostics)) {
    throw new Error(
      "ParaDev project language response diagnostics must be an array.",
    );
  }
  const planHash = requiredPayloadString(
    value,
    "plan_hash",
    "project language response",
  );
  if (!/^[0-9a-f]{64}$/.test(planHash)) {
    throw new Error("ParaDev project language response plan hash is invalid.");
  }
  const revision = requiredPayloadRecord(
    value,
    "revision",
    "project language response",
  );
  if (
    typeof revision.size !== "number"
    || !Number.isSafeInteger(revision.size)
    || revision.size < 0
  ) {
    throw new Error(
      "ParaDev project language response revision size is invalid.",
    );
  }
  if (!/^[0-9a-f]{64}$/.test(requiredPayloadString(
    revision,
    "sha256",
    "project language response revision",
  ))) {
    throw new Error(
      "ParaDev project language response revision digest is invalid.",
    );
  }
  if (value.project !== undefined && !isUnknownRecord(value.project)) {
    throw new Error(
      "ParaDev project language response project must be an object when present.",
    );
  }
  return value as ProjectPreferredLanguagePayload;
}

function projectPreferredLanguageDiagnostic(
  payload: ProjectPreferredLanguagePayload,
): string {
  const diagnostic = payload.diagnostics.find(isUnknownRecord);
  return diagnostic && typeof diagnostic.message === "string"
    ? diagnostic.message
    : "ParaDev blocked the project language update.";
}

function collectionRenamePayload(
  value: unknown,
  request: RenameCollectionRequest,
): CollectionRenamePayload {
  const label = "collection rename response";
  if (!isUnknownRecord(value)) {
    throw new Error(`ParaDev ${label} must be an object.`);
  }
  if (value.schema !== "paradev.collection.rename.v1") {
    throw new Error(`ParaDev ${label} has an unsupported schema.`);
  }
  requiredPayloadString(value, "project_id", label);
  const previousCollectionId = requiredPayloadString(
    value,
    "previous_collection_id",
    label,
  );
  const collectionId = requiredPayloadString(value, "collection_id", label);
  const family = requiredPayloadString(value, "family", label);
  const sourceRoot = normalizedPayloadPath(
    requiredPayloadString(value, "source_root", label),
    `${label} source_root`,
    true,
  );
  const previousRoot = requiredPayloadString(value, "previous_root", label);
  const root = requiredPayloadString(value, "root", label);
  validateProjectRelativePayloadPath(
    request.projectRoot,
    previousRoot,
    requiredPayloadString(value, "previous_relative_path", label),
    `${label} previous_relative_path`,
  );
  validateProjectRelativePayloadPath(
    request.projectRoot,
    root,
    requiredPayloadString(value, "relative_path", label),
    `${label} relative_path`,
  );
  if (
    previousCollectionId !== request.collectionId.trim()
    || collectionId !== request.targetId.trim()
    || (request.family?.trim() && family !== request.family.trim())
  ) {
    throw new Error(`ParaDev ${label} identity does not match the request.`);
  }
  validateRequestedSourceRoot(
    request.projectRoot,
    request.sourceRoot,
    sourceRoot,
    label,
  );
  requiredPayloadBoolean(value, "content_rewritten", label);
  if (
    typeof value.member_count !== "number"
    || !Number.isSafeInteger(value.member_count)
    || value.member_count < 0
  ) {
    throw new Error(`ParaDev ${label} member_count is invalid.`);
  }
  if (
    !Array.isArray(value.members)
    || !value.members.every((member) => typeof member === "string")
  ) {
    throw new Error(`ParaDev ${label} members must be strings.`);
  }
  requiredPayloadRecordArray(value, "files", label);
  requiredPayloadRecord(value, "collection", label);
  const catalogMutation = Object.hasOwn(value, "catalog_mutation")
    ? catalogMutationForSourceOperation(value, label, true)
    : undefined;
  return {
    ...value,
    ...(catalogMutation ? { catalog_mutation: catalogMutation } : {}),
  } as CollectionRenamePayload;
}

function collectionRemovePayload(
  value: unknown,
  request: RemoveCollectionRequest & {
    write: boolean;
    planHash?: string;
  },
): CollectionRemovePayload {
  const label = "collection remove response";
  if (!isUnknownRecord(value)) {
    throw new Error(`ParaDev ${label} must be an object.`);
  }
  if (value.schema !== "paradev.collection.remove.v1") {
    throw new Error(`ParaDev ${label} has an unsupported schema.`);
  }
  requiredPayloadString(value, "project_id", label);
  const collectionId = requiredPayloadString(value, "collection_id", label);
  const family = requiredPayloadString(value, "family", label);
  const sourceRoot = normalizedPayloadPath(
    requiredPayloadString(value, "source_root", label),
    `${label} source_root`,
    true,
  );
  const root = requiredPayloadString(value, "root", label);
  validateProjectRelativePayloadPath(
    request.projectRoot,
    root,
    requiredPayloadString(value, "relative_path", label),
    `${label} relative_path`,
  );
  if (
    collectionId !== request.collectionId.trim()
    || (request.family?.trim() && family !== request.family.trim())
  ) {
    throw new Error(`ParaDev ${label} identity does not match the request.`);
  }
  validateRequestedSourceRoot(
    request.projectRoot,
    request.sourceRoot,
    sourceRoot,
    label,
  );
  const blocked = requiredPayloadBoolean(value, "blocked", label);
  const applied = requiredPayloadBoolean(value, "applied", label);
  const written = requiredPayloadBoolean(value, "written", label);
  const removed = requiredPayloadBoolean(value, "removed", label);
  const write = requiredPayloadBoolean(value, "write", label);
  const status = requiredPayloadString(value, "status", label);
  if (!["planned", "blocked", "removed"].includes(status)) {
    throw new Error(`ParaDev ${label} status is invalid.`);
  }
  if (write !== request.write || blocked && (applied || written || removed)) {
    throw new Error(`ParaDev ${label} state is inconsistent.`);
  }
  if (!request.write && (applied || written || removed || status !== "planned")) {
    throw new Error(`ParaDev ${label} dry-plan state is inconsistent.`);
  }
  if (request.write && !blocked && (!applied || !written || !removed || status !== "removed")) {
    throw new Error(`ParaDev ${label} apply state is inconsistent.`);
  }
  const planHash = requiredPayloadString(value, "plan_hash", label);
  if (!/^[0-9a-f]{64}$/.test(planHash)) {
    throw new Error(`ParaDev ${label} plan_hash is invalid.`);
  }
  if (request.write && !blocked && request.planHash !== planHash) {
    throw new Error(`ParaDev ${label} does not match its exact plan_hash.`);
  }
  requiredPayloadRecordArray(value, "diagnostics", label);
  requiredPayloadRecordArray(value, "files", label);
  requiredPayloadRecordArray(value, "member_files", label);
  if (
    !Array.isArray(value.members)
    || !value.members.every((member) => typeof member === "string")
  ) {
    throw new Error(`ParaDev ${label} members must be strings.`);
  }
  requiredPayloadRecord(value, "counts", label);
  requiredPayloadRecord(value, "collection", label);
  const catalogMutation = Object.hasOwn(value, "catalog_mutation")
    ? catalogMutationForSourceOperation(value, label, removed)
    : undefined;
  return {
    ...value,
    ...(catalogMutation ? { catalog_mutation: catalogMutation } : {}),
  } as CollectionRemovePayload;
}

function collectionRemoveDiagnostic(payload: CollectionRemovePayload): string {
  const diagnostic = payload.diagnostics.find(isUnknownRecord);
  return diagnostic && typeof diagnostic.message === "string"
    ? diagnostic.message
    : "ParaDev blocked the collection removal.";
}

function moduleRenamePayload(
  value: unknown,
  request: RenameModuleRequest,
): ModuleRenamePayload {
  if (!isUnknownRecord(value)) {
    throw new Error("ParaDev module rename response must be an object.");
  }
  if (value.schema !== "paradev.module.rename.v1") {
    throw new Error(
      "ParaDev module rename response has an unsupported schema.",
    );
  }
  requiredPayloadString(value, "project_id", "module rename response");
  const previousModuleId = requiredPayloadString(
    value,
    "previous_module_id",
    "module rename response",
  );
  const moduleId = requiredPayloadString(
    value,
    "module_id",
    "module rename response",
  );
  const responseFamily = requiredPayloadString(
    value,
    "family",
    "module rename response",
  );
  const previousRootValue = requiredPayloadString(
    value,
    "previous_root",
    "module rename response",
  );
  const rootValue = requiredPayloadString(
    value,
    "root",
    "module rename response",
  );
  const previousRelativePath = requiredPayloadString(
    value,
    "previous_relative_path",
    "module rename response",
  );
  const relativePath = requiredPayloadString(
    value,
    "relative_path",
    "module rename response",
  );
  requiredPayloadBoolean(value, "content_rewritten", "module rename response");
  requiredPayloadRecord(value, "module", "module rename response");
  const expectedPreviousModuleId = request.moduleId.trim();
  const [family, previousObjectId] = moduleIdParts(
    expectedPreviousModuleId,
    "module rename request",
  );
  const objectId = request.objectId.trim();
  const expectedModuleId = `${family}/${objectId}`;
  if (
    previousModuleId !== expectedPreviousModuleId ||
    moduleId !== expectedModuleId
  ) {
    throw new Error(
      "ParaDev module rename response identity does not match the request.",
    );
  }
  if (responseFamily !== family) {
    throw new Error(
      "ParaDev module rename response module identity is inconsistent.",
    );
  }
  const previousRoot = modulePayloadRoot(
    previousRootValue,
    family,
    previousObjectId,
    "module rename response previous_root",
  );
  const root = modulePayloadRoot(
    rootValue,
    family,
    objectId,
    "module rename response root",
  );
  if (!payloadPathsEqual(previousRoot.sourceRoot, root.sourceRoot)) {
    throw new Error(
      "ParaDev module rename response old and new roots use different source roots.",
    );
  }
  validateProjectRelativePayloadPath(
    request.projectRoot,
    previousRootValue,
    previousRelativePath,
    "module rename response previous_relative_path",
  );
  validateProjectRelativePayloadPath(
    request.projectRoot,
    rootValue,
    relativePath,
    "module rename response relative_path",
  );
  validateRequestedSourceRoot(
    request.projectRoot,
    request.sourceRoot,
    root.sourceRoot,
    "module rename response",
  );
  const catalogMutation = catalogMutationForSourceOperation(
    value,
    "module rename response",
    true,
  );
  return { ...value, catalog_mutation: catalogMutation } as ModuleRenamePayload;
}

function moduleCollectionPayload(
  value: unknown,
  request: SetModuleCollectionRequest & {
    write: boolean;
    planHash?: string;
  },
): ModuleCollectionPayload {
  const label = "module collection response";
  if (!isUnknownRecord(value)) {
    throw new Error(`ParaDev ${label} must be an object.`);
  }
  if (value.schema !== "paradev.sdk.module_collection_update.v1") {
    throw new Error(`ParaDev ${label} has an unsupported schema.`);
  }
  requiredPayloadString(value, "project_id", label);
  const projectRoot = normalizedPayloadPath(
    requiredPayloadString(value, "project_root", label),
    `${label} project_root`,
    true,
  );
  const requestedProjectRoot = normalizedPayloadPath(
    request.projectRoot,
    "module collection request projectRoot",
    true,
  );
  if (!payloadPathsEqual(projectRoot, requestedProjectRoot)) {
    throw new Error(`ParaDev ${label} project root does not match the request.`);
  }
  const moduleId = requiredPayloadString(value, "module_id", label);
  const family = requiredPayloadString(value, "family", label);
  const sourceRoot = requiredPayloadString(value, "source_root", label);
  const [expectedFamily] = moduleIdParts(request.moduleId.trim(), "module collection request");
  if (moduleId !== request.moduleId.trim() || family !== expectedFamily) {
    throw new Error(`ParaDev ${label} identity does not match the request.`);
  }
  validateRequestedSourceRoot(
    request.projectRoot,
    request.sourceRoot ?? undefined,
    normalizedPayloadPath(sourceRoot, `${label} source_root`, true),
    label,
  );
  for (const key of ["previous_collection_id", "collection_id"] as const) {
    if (value[key] !== null && typeof value[key] !== "string") {
      throw new Error(`ParaDev ${label} requires nullable string ${key}.`);
    }
  }
  const requestedCollection = request.collectionId?.trim() || null;
  if (value.collection_id !== requestedCollection) {
    throw new Error(`ParaDev ${label} target does not match the request.`);
  }
  const changed = requiredPayloadBoolean(value, "changed", label);
  const blocked = requiredPayloadBoolean(value, "blocked", label);
  const applied = requiredPayloadBoolean(value, "applied", label);
  const written = requiredPayloadBoolean(value, "written", label);
  const status = requiredPayloadString(value, "status", label);
  if (!["planned", "blocked", "unchanged", "updated"].includes(status)) {
    throw new Error(`ParaDev ${label} status is invalid.`);
  }
  if (blocked && (applied || written)) {
    throw new Error(`ParaDev ${label} cannot write a blocked plan.`);
  }
  if (written && (!applied || !changed)) {
    throw new Error(`ParaDev ${label} written state is inconsistent.`);
  }
  if (!request.write && (applied || written || status !== "planned")) {
    throw new Error(`ParaDev ${label} dry-plan state is inconsistent.`);
  }
  if (request.write && !blocked) {
    const expectedStatus = changed ? "updated" : "unchanged";
    if (status !== expectedStatus || !applied || written !== changed) {
      throw new Error(`ParaDev ${label} apply state is inconsistent.`);
    }
  }
  if (blocked && status !== "blocked") {
    throw new Error(`ParaDev ${label} blocked state is inconsistent.`);
  }
  const planHash = requiredPayloadString(value, "plan_hash", label);
  if (!/^[0-9a-f]{64}$/.test(planHash)) {
    throw new Error(`ParaDev ${label} plan_hash is invalid.`);
  }
  if (request.write && !blocked && request.planHash !== planHash) {
    throw new Error(`ParaDev ${label} does not match its exact plan_hash.`);
  }
  requiredPayloadRecordArray(value, "diagnostics", label);
  const files = requiredPayloadRecordArray(value, "files", label);
  for (const [index, file] of files.entries()) {
    const fileLabel = `${label} file ${index}`;
    requiredPayloadString(file, "path", fileLabel);
    requiredPayloadString(file, "relative_path", fileLabel);
    if (!["visible", "hidden"].includes(String(file.layer))) {
      throw new Error(`ParaDev ${fileLabel} layer is invalid.`);
    }
    if (!["create", "update", "remove"].includes(String(file.action))) {
      throw new Error(`ParaDev ${fileLabel} action is invalid.`);
    }
    for (const key of ["before_sha256", "after_sha256"] as const) {
      const digest = file[key];
      if (digest !== null && (typeof digest !== "string" || !/^[0-9a-f]{64}$/.test(digest))) {
        throw new Error(`ParaDev ${fileLabel} ${key} is invalid.`);
      }
    }
  }
  if (value.module !== undefined) {
    requiredPayloadRecord(value, "module", label);
  }
  if (value.collection !== undefined) {
    requiredPayloadRecord(value, "collection", label);
  }
  const catalogMutation = catalogMutationForSourceOperation(value, label, written);
  return {
    ...value,
    ...(catalogMutation ? { catalog_mutation: catalogMutation } : {}),
  } as ModuleCollectionPayload;
}

function moduleCollectionDiagnostic(payload: ModuleCollectionPayload): string {
  const diagnostic = payload.diagnostics.find(isUnknownRecord);
  return diagnostic && typeof diagnostic.message === "string"
    ? diagnostic.message
    : "ParaDev blocked the module collection update.";
}

function moduleActivityPayload(
  value: unknown,
  request: SetModuleActiveRequest & {
    write: boolean;
    planHash?: string;
  },
): ModuleActivityPayload {
  const label = "module activity response";
  if (!isUnknownRecord(value)) {
    throw new Error(`ParaDev ${label} must be an object.`);
  }
  if (value.schema !== "paradev.sdk.module_activity_update.v1") {
    throw new Error(`ParaDev ${label} has an unsupported schema.`);
  }
  requiredPayloadString(value, "project_id", label);
  const projectRoot = normalizedPayloadPath(
    requiredPayloadString(value, "project_root", label),
    `${label} project_root`,
    true,
  );
  const requestedProjectRoot = normalizedPayloadPath(
    request.projectRoot,
    "module activity request projectRoot",
    true,
  );
  if (!payloadPathsEqual(projectRoot, requestedProjectRoot)) {
    throw new Error(`ParaDev ${label} project root does not match the request.`);
  }
  const moduleId = requiredPayloadString(value, "module_id", label);
  const family = requiredPayloadString(value, "family", label);
  const sourceRoot = requiredPayloadString(value, "source_root", label);
  const [expectedFamily] = moduleIdParts(
    request.moduleId.trim(),
    "module activity request",
  );
  if (moduleId !== request.moduleId.trim() || family !== expectedFamily) {
    throw new Error(`ParaDev ${label} identity does not match the request.`);
  }
  validateRequestedSourceRoot(
    request.projectRoot,
    request.sourceRoot ?? undefined,
    normalizedPayloadPath(sourceRoot, `${label} source_root`, true),
    label,
  );
  requiredPayloadBoolean(value, "previous_active", label);
  const active = requiredPayloadBoolean(value, "active", label);
  if (active !== request.active) {
    throw new Error(`ParaDev ${label} target does not match the request.`);
  }
  const changed = requiredPayloadBoolean(value, "changed", label);
  const blocked = requiredPayloadBoolean(value, "blocked", label);
  const applied = requiredPayloadBoolean(value, "applied", label);
  const written = requiredPayloadBoolean(value, "written", label);
  const status = requiredPayloadString(value, "status", label);
  if (!["planned", "blocked", "unchanged", "updated"].includes(status)) {
    throw new Error(`ParaDev ${label} status is invalid.`);
  }
  if (blocked && (applied || written)) {
    throw new Error(`ParaDev ${label} cannot write a blocked plan.`);
  }
  if (written && (!applied || !changed)) {
    throw new Error(`ParaDev ${label} written state is inconsistent.`);
  }
  if (!request.write && (applied || written || status !== "planned")) {
    throw new Error(`ParaDev ${label} dry-plan state is inconsistent.`);
  }
  if (request.write && !blocked) {
    const expectedStatus = changed ? "updated" : "unchanged";
    if (status !== expectedStatus || !applied || written !== changed) {
      throw new Error(`ParaDev ${label} apply state is inconsistent.`);
    }
  }
  if (blocked && status !== "blocked") {
    throw new Error(`ParaDev ${label} blocked state is inconsistent.`);
  }
  const planHash = requiredPayloadString(value, "plan_hash", label);
  if (!/^[0-9a-f]{64}$/.test(planHash)) {
    throw new Error(`ParaDev ${label} plan_hash is invalid.`);
  }
  if (request.write && !blocked && request.planHash !== planHash) {
    throw new Error(`ParaDev ${label} does not match its exact plan_hash.`);
  }
  requiredPayloadRecordArray(value, "diagnostics", label);
  const files = requiredPayloadRecordArray(value, "files", label);
  for (const [index, file] of files.entries()) {
    const fileLabel = `${label} file ${index}`;
    requiredPayloadString(file, "path", fileLabel);
    requiredPayloadString(file, "relative_path", fileLabel);
    if (!["visible", "hidden"].includes(String(file.layer))) {
      throw new Error(`ParaDev ${fileLabel} layer is invalid.`);
    }
    if (!["create", "update", "remove"].includes(String(file.action))) {
      throw new Error(`ParaDev ${fileLabel} action is invalid.`);
    }
    for (const key of ["before_sha256", "after_sha256"] as const) {
      const digest = file[key];
      if (
        digest !== null &&
        (typeof digest !== "string" || !/^[0-9a-f]{64}$/.test(digest))
      ) {
        throw new Error(`ParaDev ${fileLabel} ${key} is invalid.`);
      }
    }
  }
  if (value.module !== undefined) {
    requiredPayloadRecord(value, "module", label);
  }
  const catalogMutation = catalogMutationForSourceOperation(value, label, written);
  return {
    ...value,
    ...(catalogMutation ? { catalog_mutation: catalogMutation } : {}),
  } as ModuleActivityPayload;
}

function moduleActivityDiagnostic(payload: ModuleActivityPayload): string {
  const diagnostic = payload.diagnostics.find(isUnknownRecord);
  return diagnostic && typeof diagnostic.message === "string"
    ? diagnostic.message
    : "ParaDev blocked the module activity update.";
}

function moduleDuplicatePayload(
  value: unknown,
  request: DuplicateModuleRequest,
): ModuleDuplicatePayload {
  if (!isUnknownRecord(value)) {
    throw new Error("ParaDev module duplicate response must be an object.");
  }
  if (value.schema !== "paradev.sdk.module_duplicate.v1") {
    throw new Error(
      "ParaDev module duplicate response has an unsupported schema.",
    );
  }
  requiredPayloadString(value, "project_id", "module duplicate response");
  const sourceModuleId = requiredPayloadString(
    value,
    "source_module_id",
    "module duplicate response",
  );
  const moduleId = requiredPayloadString(
    value,
    "module_id",
    "module duplicate response",
  );
  const family = requiredPayloadString(
    value,
    "family",
    "module duplicate response",
  );
  const objectId = requiredPayloadString(
    value,
    "object_id",
    "module duplicate response",
  );
  const sourceRootValue = requiredPayloadString(
    value,
    "source_root",
    "module duplicate response",
  );
  const destinationSourceRootValue = requiredPayloadString(
    value,
    "destination_source_root",
    "module duplicate response",
  );
  const sourceModuleRootValue = requiredPayloadString(
    value,
    "source_module_root",
    "module duplicate response",
  );
  const rootValue = requiredPayloadString(
    value,
    "root",
    "module duplicate response",
  );
  const sourceRelativePath = requiredPayloadString(
    value,
    "source_relative_path",
    "module duplicate response",
  );
  const relativePath = requiredPayloadString(
    value,
    "relative_path",
    "module duplicate response",
  );
  const status = requiredPayloadString(
    value,
    "status",
    "module duplicate response",
  );
  if (!["planned", "duplicated", "blocked"].includes(status)) {
    throw new Error(
      "ParaDev module duplicate response has an unsupported status.",
    );
  }
  const blocked = requiredPayloadBoolean(
    value,
    "blocked",
    "module duplicate response",
  );
  const applied = requiredPayloadBoolean(
    value,
    "applied",
    "module duplicate response",
  );
  const written = requiredPayloadBoolean(
    value,
    "written",
    "module duplicate response",
  );
  const planHash = requiredPayloadString(
    value,
    "plan_hash",
    "module duplicate response",
  );
  if (!/^[0-9a-f]{64}$/.test(planHash)) {
    throw new Error(
      "ParaDev module duplicate response requires a lowercase SHA-256 plan_hash.",
    );
  }
  const identityMode = requiredPayloadString(
    value,
    "identity_mode",
    "module duplicate response",
  );
  if (
    !["rewrite", "preserve"].includes(identityMode) ||
    identityMode !== (request.identity ?? "rewrite")
  ) {
    throw new Error(
      "ParaDev module duplicate response identity mode does not match the request.",
    );
  }
  const identityRewriter =
    value.identity_rewriter === null
      ? null
      : requiredPayloadString(
          value,
          "identity_rewriter",
          "module duplicate response",
        );
  const contentRewritten = requiredPayloadBoolean(
    value,
    "content_rewritten",
    "module duplicate response",
  );
  const pathsRewritten = requiredPayloadBoolean(
    value,
    "paths_rewritten",
    "module duplicate response",
  );
  if (
    (identityMode === "preserve" &&
      (identityRewriter !== null || contentRewritten || pathsRewritten)) ||
    ((contentRewritten || pathsRewritten) && identityRewriter === null)
  ) {
    throw new Error(
      "ParaDev module duplicate response has an inconsistent identity rewrite summary.",
    );
  }
  const diagnostics = requiredPayloadRecordArray(
    value,
    "diagnostics",
    "module duplicate response",
  );
  const directories = requiredPayloadRecordArray(
    value,
    "directories",
    "module duplicate response",
  ).map((row, index) =>
    moduleDuplicateDirectory(
      row,
      `module duplicate response directory ${index}`,
    ),
  );
  const files = requiredPayloadRecordArray(
    value,
    "files",
    "module duplicate response",
  ).map((row, index) =>
    moduleDuplicateFile(row, `module duplicate response file ${index}`),
  );
  const exclusions = requiredPayloadRecordArray(
    value,
    "exclusions",
    "module duplicate response",
  ).map((row, index) =>
    moduleDuplicateExclusion(
      row,
      `module duplicate response exclusion ${index}`,
    ),
  );
  const totals = requiredPayloadRecord(
    value,
    "totals",
    "module duplicate response",
  );
  const normalizedTotals = {
    directory_count: requiredPayloadNonnegativeInteger(
      totals,
      "directory_count",
      "module duplicate response totals",
    ),
    file_count: requiredPayloadNonnegativeInteger(
      totals,
      "file_count",
      "module duplicate response totals",
    ),
    excluded_count: requiredPayloadNonnegativeInteger(
      totals,
      "excluded_count",
      "module duplicate response totals",
    ),
    size_bytes: requiredPayloadNonnegativeInteger(
      totals,
      "size_bytes",
      "module duplicate response totals",
    ),
    target_size_bytes: requiredPayloadNonnegativeInteger(
      totals,
      "target_size_bytes",
      "module duplicate response totals",
    ),
    rewritten_file_count: requiredPayloadNonnegativeInteger(
      totals,
      "rewritten_file_count",
      "module duplicate response totals",
    ),
    renamed_path_count: requiredPayloadNonnegativeInteger(
      totals,
      "renamed_path_count",
      "module duplicate response totals",
    ),
  };
  const source = moduleDuplicateSource(
    requiredPayloadRecord(value, "source", "module duplicate response"),
    "module duplicate response source",
  );
  const destination = moduleDuplicateDestination(
    requiredPayloadRecord(value, "destination", "module duplicate response"),
    "module duplicate response destination",
  );

  const expectedSourceModuleId = request.moduleId.trim();
  const [sourceFamily, sourceObjectId] = moduleIdParts(
    expectedSourceModuleId,
    "module duplicate request",
  );
  const expectedObjectId = request.objectId.trim();
  if (
    sourceModuleId !== expectedSourceModuleId ||
    family !== sourceFamily ||
    objectId !== expectedObjectId ||
    moduleId !== `${sourceFamily}/${expectedObjectId}`
  ) {
    throw new Error(
      "ParaDev module duplicate response identity does not match the request.",
    );
  }
  const sourceModuleRoot = modulePayloadRoot(
    sourceModuleRootValue,
    sourceFamily,
    sourceObjectId,
    "module duplicate response source_module_root",
  );
  const destinationModuleRoot = modulePayloadRoot(
    rootValue,
    sourceFamily,
    expectedObjectId,
    "module duplicate response root",
  );
  const sourceRoot = normalizedPayloadPath(
    sourceRootValue,
    "module duplicate response source_root",
    true,
  );
  const destinationSourceRoot = normalizedPayloadPath(
    destinationSourceRootValue,
    "module duplicate response destination_source_root",
    true,
  );
  if (!payloadPathsEqual(sourceModuleRoot.sourceRoot, sourceRoot)) {
    throw new Error(
      "ParaDev module duplicate response source module root does not match its source_root.",
    );
  }
  if (
    !payloadPathsEqual(destinationModuleRoot.sourceRoot, destinationSourceRoot)
  ) {
    throw new Error(
      "ParaDev module duplicate response root does not match its destination_source_root.",
    );
  }
  validateProjectRelativePayloadPath(
    request.projectRoot,
    sourceModuleRootValue,
    sourceRelativePath,
    "module duplicate response source_relative_path",
  );
  validateProjectRelativePayloadPath(
    request.projectRoot,
    rootValue,
    relativePath,
    "module duplicate response relative_path",
  );
  validateRequestedSourceRoot(
    request.projectRoot,
    request.sourceRoot,
    sourceRoot,
    "module duplicate response source",
  );
  validateRequestedSourceRoot(
    request.projectRoot,
    request.destinationSourceRoot,
    destinationSourceRoot,
    "module duplicate response destination",
  );
  if (
    source.module_id !== sourceModuleId ||
    source.source_root !== sourceRootValue ||
    source.root !== sourceModuleRootValue ||
    source.relative_path !== sourceRelativePath ||
    source.identity_rewriter !== identityRewriter
  ) {
    throw new Error(
      "ParaDev module duplicate response source summary is inconsistent.",
    );
  }
  if (
    destination.module_id !== moduleId ||
    destination.source_root !== destinationSourceRootValue ||
    destination.root !== rootValue ||
    destination.relative_path !== relativePath
  ) {
    throw new Error(
      "ParaDev module duplicate response destination summary is inconsistent.",
    );
  }
  if (
    normalizedTotals.directory_count !== directories.length ||
    normalizedTotals.file_count !== files.length ||
    normalizedTotals.excluded_count !== exclusions.length ||
    normalizedTotals.size_bytes !==
      files.reduce((total, file) => total + file.size_bytes, 0) ||
    normalizedTotals.target_size_bytes !==
      files.reduce((total, file) => total + file.target_size_bytes, 0) ||
    normalizedTotals.rewritten_file_count !==
      files.filter((file) => file.content_rewritten).length ||
    normalizedTotals.renamed_path_count !==
      [...directories, ...files].filter(
        (entry) => entry.relative_path !== entry.target_relative_path,
      ).length ||
    contentRewritten !== (normalizedTotals.rewritten_file_count > 0) ||
    pathsRewritten !== (normalizedTotals.renamed_path_count > 0)
  ) {
    throw new Error(
      "ParaDev module duplicate response totals do not match its inventory.",
    );
  }
  const sourceSnapshotValues = [
    source.root_identity,
    source.modules_identity,
    source.family_identity,
    source.module_identity,
    source.tree_digest,
    source.content_digest,
  ];
  const hasSourceSnapshot = sourceSnapshotValues.every((item) => item !== null);
  if (
    !hasSourceSnapshot &&
    sourceSnapshotValues.some((item) => item !== null)
  ) {
    throw new Error(
      "ParaDev module duplicate response has an incomplete source snapshot.",
    );
  }
  const hasDestinationSnapshot =
    destination.root_identity !== null &&
    destination.entry_names_digest !== null &&
    destination.content_digest !== null;
  if (
    hasSourceSnapshot !== hasDestinationSnapshot ||
    (!hasDestinationSnapshot &&
      (destination.modules_identity !== null ||
        destination.family_identity !== null ||
        destination.target_identity !== null ||
        destination.entry_count !== 0 ||
        destination.content_digest !== null))
  ) {
    throw new Error(
      "ParaDev module duplicate response has an incomplete destination snapshot.",
    );
  }
  if (
    !hasSourceSnapshot &&
    (directories.length !== 0 ||
      files.length !== 0 ||
      exclusions.length !== 0 ||
      !blocked)
  ) {
    throw new Error(
      "ParaDev module duplicate response inventory requires a complete filesystem snapshot.",
    );
  }
  if (
    (status === "blocked") !== blocked ||
    (status === "duplicated") !== applied ||
    applied !== written ||
    (blocked && (applied || written))
  ) {
    throw new Error(
      "ParaDev module duplicate response has an inconsistent status.",
    );
  }
  if (
    request.write !== true &&
    (status === "duplicated" || applied || written)
  ) {
    throw new Error(
      "ParaDev module duplicate dry plan cannot report written files.",
    );
  }
  if (
    (status !== "duplicated" && destination.target_identity !== null) ||
    (status === "duplicated" && destination.target_identity === null)
  ) {
    throw new Error(
      "ParaDev module duplicate response target identity does not match its status.",
    );
  }
  if (
    request.write === true &&
    !blocked &&
    (!request.planHash?.trim() ||
      request.planHash.trim() !== planHash ||
      status !== "duplicated")
  ) {
    throw new Error(
      "ParaDev module duplicate apply does not match its exact plan_hash.",
    );
  }
  const catalogMutation = catalogMutationForSourceOperation(
    value,
    "module duplicate response",
    written,
  );
  return {
    ...value,
    destination,
    directories,
    exclusions,
    files,
    source,
    totals: normalizedTotals,
    ...(catalogMutation ? { catalog_mutation: catalogMutation } : {}),
  } as ModuleDuplicatePayload;
}

function moduleDuplicateDirectory(
  value: Record<string, unknown>,
  label: string,
): ModuleDuplicateDirectory {
  validateExactPayloadFields(
    value,
    [
      "relative_path",
      "target_relative_path",
      "kind",
      "identity",
      "mode",
      "mtime_ns",
      "action",
    ],
    label,
  );
  const relativePath = moduleDuplicateRelativePath(value, label);
  const targetRelativePath = moduleDuplicatePath(
    value,
    "target_relative_path",
    label,
  );
  const actions = ["copy", "rename"] as const;
  if (
    value.kind !== "directory" ||
    !actions.includes(value.action as (typeof actions)[number]) ||
    (value.action === "copy") !== (relativePath === targetRelativePath)
  ) {
    throw new Error(`ParaDev ${label} must describe a projected directory.`);
  }
  return {
    relative_path: relativePath,
    target_relative_path: targetRelativePath,
    kind: value.kind,
    identity: moduleDuplicateIdentity(value.identity, `${label} identity`),
    mode: requiredPayloadNonnegativeInteger(value, "mode", label),
    mtime_ns: moduleDuplicateNanoseconds(value, label),
    action: value.action as ModuleDuplicateDirectory["action"],
  };
}

function moduleDuplicateFile(
  value: Record<string, unknown>,
  label: string,
): ModuleDuplicateFile {
  validateExactPayloadFields(
    value,
    [
      "relative_path",
      "target_relative_path",
      "kind",
      "identity",
      "mode",
      "mtime_ns",
      "size_bytes",
      "sha256",
      "target_size_bytes",
      "target_sha256",
      "content_rewritten",
      "action",
    ],
    label,
  );
  const relativePath = moduleDuplicateRelativePath(value, label);
  const targetRelativePath = moduleDuplicatePath(
    value,
    "target_relative_path",
    label,
  );
  const sha256 = requiredPayloadString(value, "sha256", label);
  const targetSha256 = requiredPayloadString(value, "target_sha256", label);
  const contentRewritten = requiredPayloadBoolean(
    value,
    "content_rewritten",
    label,
  );
  const pathRewritten = relativePath !== targetRelativePath;
  const expectedAction = pathRewritten
    ? contentRewritten
      ? "rewrite_and_rename"
      : "rename"
    : contentRewritten
      ? "rewrite"
      : "copy";
  if (
    value.kind !== "file" ||
    value.action !== expectedAction ||
    !/^[0-9a-f]{64}$/.test(sha256) ||
    !/^[0-9a-f]{64}$/.test(targetSha256)
  ) {
    throw new Error(
      `ParaDev ${label} must describe a projected file with SHA-256 digests.`,
    );
  }
  return {
    relative_path: relativePath,
    target_relative_path: targetRelativePath,
    kind: value.kind,
    identity: moduleDuplicateIdentity(value.identity, `${label} identity`),
    mode: requiredPayloadNonnegativeInteger(value, "mode", label),
    mtime_ns: moduleDuplicateNanoseconds(value, label),
    size_bytes: requiredPayloadNonnegativeInteger(value, "size_bytes", label),
    sha256,
    target_size_bytes: requiredPayloadNonnegativeInteger(
      value,
      "target_size_bytes",
      label,
    ),
    target_sha256: targetSha256,
    content_rewritten: contentRewritten,
    action: value.action as ModuleDuplicateFile["action"],
  };
}

function moduleDuplicateExclusion(
  value: Record<string, unknown>,
  label: string,
): ModuleDuplicateExclusion {
  validateExactPayloadFields(
    value,
    [
      "relative_path",
      "kind",
      "identity",
      "mode",
      "mtime_ns",
      "reason",
      "action",
    ],
    label,
  );
  const kinds = ["directory", "file", "symlink", "special"] as const;
  if (
    value.relative_path !== ".paradev" ||
    !kinds.includes(value.kind as (typeof kinds)[number]) ||
    value.reason !== "module_local_system_tree" ||
    value.action !== "exclude"
  ) {
    throw new Error(
      `ParaDev ${label} must describe excluded module-local system metadata.`,
    );
  }
  return {
    relative_path: value.relative_path,
    kind: value.kind as ModuleDuplicateExclusion["kind"],
    identity: moduleDuplicateIdentity(value.identity, `${label} identity`),
    mode: requiredPayloadNonnegativeInteger(value, "mode", label),
    mtime_ns: moduleDuplicateNanoseconds(value, label),
    reason: value.reason,
    action: value.action,
  };
}

function moduleDuplicateSource(
  value: Record<string, unknown>,
  label: string,
): ModuleDuplicateSource {
  validateExactPayloadFields(
    value,
    [
      "module_id",
      "source_root",
      "root",
      "relative_path",
      "root_identity",
      "modules_identity",
      "family_identity",
      "module_identity",
      "tree_digest",
      "content_digest",
      "identity_rewriter",
    ],
    label,
  );
  return {
    module_id: requiredPayloadString(value, "module_id", label),
    source_root: requiredPayloadString(value, "source_root", label),
    root: requiredPayloadString(value, "root", label),
    relative_path: requiredPayloadString(value, "relative_path", label),
    root_identity: moduleDuplicateNullableIdentity(
      value.root_identity,
      `${label} root_identity`,
    ),
    modules_identity: moduleDuplicateNullableIdentity(
      value.modules_identity,
      `${label} modules_identity`,
    ),
    family_identity: moduleDuplicateNullableIdentity(
      value.family_identity,
      `${label} family_identity`,
    ),
    module_identity: moduleDuplicateNullableIdentity(
      value.module_identity,
      `${label} module_identity`,
    ),
    tree_digest: moduleDuplicateNullableDigest(value, "tree_digest", label),
    content_digest: moduleDuplicateNullableDigest(
      value,
      "content_digest",
      label,
    ),
    identity_rewriter:
      value.identity_rewriter === null
        ? null
        : requiredPayloadString(value, "identity_rewriter", label),
  };
}

function moduleDuplicateDestination(
  value: Record<string, unknown>,
  label: string,
): ModuleDuplicateDestination {
  validateExactPayloadFields(
    value,
    [
      "module_id",
      "source_root",
      "root",
      "relative_path",
      "root_identity",
      "modules_identity",
      "family_identity",
      "target_identity",
      "entry_count",
      "entry_names_digest",
      "content_digest",
    ],
    label,
  );
  return {
    module_id: requiredPayloadString(value, "module_id", label),
    source_root: requiredPayloadString(value, "source_root", label),
    root: requiredPayloadString(value, "root", label),
    relative_path: requiredPayloadString(value, "relative_path", label),
    root_identity: moduleDuplicateNullableIdentity(
      value.root_identity,
      `${label} root_identity`,
    ),
    modules_identity: moduleDuplicateNullableIdentity(
      value.modules_identity,
      `${label} modules_identity`,
    ),
    family_identity: moduleDuplicateNullableIdentity(
      value.family_identity,
      `${label} family_identity`,
    ),
    target_identity: moduleDuplicateNullableIdentity(
      value.target_identity,
      `${label} target_identity`,
    ),
    entry_count: requiredPayloadNonnegativeInteger(value, "entry_count", label),
    entry_names_digest: moduleDuplicateNullableDigest(
      value,
      "entry_names_digest",
      label,
    ),
    content_digest: moduleDuplicateNullableDigest(
      value,
      "content_digest",
      label,
    ),
  };
}

function moduleDuplicateNullableIdentity(
  value: unknown,
  label: string,
): ModuleDuplicateIdentity | null {
  return value === null ? null : moduleDuplicateIdentity(value, label);
}

function moduleDuplicateIdentity(
  value: unknown,
  label: string,
): ModuleDuplicateIdentity {
  if (
    !Array.isArray(value) ||
    value.length !== 2 ||
    value.some((item) => !Number.isSafeInteger(item) || Number(item) < 0)
  ) {
    throw new Error(
      `ParaDev ${label} must be a nonnegative filesystem identity pair.`,
    );
  }
  return [Number(value[0]), Number(value[1])];
}

function moduleDuplicateRelativePath(
  value: Record<string, unknown>,
  label: string,
): string {
  return moduleDuplicatePath(value, "relative_path", label);
}

function moduleDuplicatePath(
  value: Record<string, unknown>,
  key: string,
  label: string,
): string {
  const relativePath = requiredPayloadString(value, key, label);
  normalizedPayloadPath(relativePath, `${label} ${key}`, false);
  if (relativePath === ".paradev" || relativePath.startsWith(".paradev/")) {
    throw new Error(
      `ParaDev ${label} cannot copy module-local system metadata.`,
    );
  }
  return relativePath;
}

function moduleDuplicateNanoseconds(
  value: Record<string, unknown>,
  label: string,
): string {
  const nanoseconds = requiredPayloadString(value, "mtime_ns", label);
  if (!/^\d+$/.test(nanoseconds)) {
    throw new Error(`ParaDev ${label} requires decimal mtime_ns.`);
  }
  return nanoseconds;
}

function moduleDuplicateDigest(
  value: Record<string, unknown>,
  key: string,
  label: string,
): string {
  const digest = requiredPayloadString(value, key, label);
  if (!/^[0-9a-f]{64}$/.test(digest)) {
    throw new Error(`ParaDev ${label} requires a lowercase SHA-256 ${key}.`);
  }
  return digest;
}

function moduleDuplicateNullableDigest(
  value: Record<string, unknown>,
  key: string,
  label: string,
): string | null {
  return value[key] === null ? null : moduleDuplicateDigest(value, key, label);
}

function validateExactPayloadFields(
  value: Record<string, unknown>,
  expected: readonly string[],
  label: string,
): void {
  const expectedFields = new Set(expected);
  const unexpected = Object.keys(value)
    .filter((key) => !expectedFields.has(key))
    .sort();
  const missing = expected.filter((key) => !Object.hasOwn(value, key));
  if (unexpected.length > 0 || missing.length > 0) {
    throw new Error(`ParaDev ${label} does not match its exact payload shape.`);
  }
}

function moduleRemovePayload(
  value: unknown,
  request: RemoveModuleRequest,
): ModuleRemovePayload {
  if (!isUnknownRecord(value)) {
    throw new Error("ParaDev module remove response must be an object.");
  }
  if (value.schema !== "paradev.module.remove.v1") {
    throw new Error(
      "ParaDev module remove response has an unsupported schema.",
    );
  }
  requiredPayloadString(value, "project_id", "module remove response");
  const moduleId = requiredPayloadString(
    value,
    "module_id",
    "module remove response",
  );
  const responseFamily = requiredPayloadString(
    value,
    "family",
    "module remove response",
  );
  const sourceRootValue = requiredPayloadString(
    value,
    "source_root",
    "module remove response",
  );
  const rootValue = requiredPayloadString(
    value,
    "root",
    "module remove response",
  );
  const relativePath = requiredPayloadString(
    value,
    "relative_path",
    "module remove response",
  );
  const blocked = requiredPayloadBoolean(
    value,
    "blocked",
    "module remove response",
  );
  const removed = requiredPayloadBoolean(
    value,
    "removed",
    "module remove response",
  );
  const diagnostics = requiredPayloadRecordArray(
    value,
    "diagnostics",
    "module remove response",
  );
  requiredPayloadRecordArray(value, "files", "module remove response");
  requiredPayloadRecord(value, "module", "module remove response");
  const expectedModuleId = request.moduleId.trim();
  const [family, objectId] = moduleIdParts(
    expectedModuleId,
    "module remove request",
  );
  if (moduleId !== expectedModuleId) {
    throw new Error(
      "ParaDev module remove response identity does not match the request.",
    );
  }
  if (responseFamily !== family) {
    throw new Error(
      "ParaDev module remove response module identity is inconsistent.",
    );
  }
  if (blocked && removed) {
    throw new Error(
      "ParaDev module remove response cannot be both blocked and removed.",
    );
  }
  const root = modulePayloadRoot(
    rootValue,
    family,
    objectId,
    "module remove response root",
  );
  const sourceRoot = normalizedPayloadPath(
    sourceRootValue,
    "module remove response source_root",
    true,
  );
  if (!payloadPathsEqual(root.sourceRoot, sourceRoot)) {
    throw new Error(
      "ParaDev module remove response root does not match its source_root.",
    );
  }
  validateProjectRelativePayloadPath(
    request.projectRoot,
    rootValue,
    relativePath,
    "module remove response relative_path",
  );
  validateRequestedSourceRoot(
    request.projectRoot,
    request.sourceRoot,
    sourceRoot,
    "module remove response",
  );
  validateModuleRemoveCleanup(
    value,
    request.projectRoot,
    sourceRoot,
    diagnostics,
    removed,
  );
  const catalogMutation = catalogMutationForSourceOperation(
    value,
    "module remove response",
    removed,
  );
  return {
    ...value,
    ...(catalogMutation ? { catalog_mutation: catalogMutation } : {}),
  } as ModuleRemovePayload;
}

function requiredPayloadString(
  value: Record<string, unknown>,
  key: string,
  label: string,
): string {
  const field = value[key];
  if (typeof field !== "string" || !field.trim()) {
    throw new Error(`ParaDev ${label} requires a non-empty ${key}.`);
  }
  return field;
}

function requiredPayloadBoolean(
  value: Record<string, unknown>,
  key: string,
  label: string,
): boolean {
  const field = value[key];
  if (typeof field !== "boolean") {
    throw new Error(`ParaDev ${label} requires a boolean ${key}.`);
  }
  return field;
}

function requiredPayloadNonnegativeInteger(
  value: Record<string, unknown>,
  key: string,
  label: string,
): number {
  const field = value[key];
  if (!Number.isSafeInteger(field) || Number(field) < 0) {
    throw new Error(`ParaDev ${label} requires a nonnegative integer ${key}.`);
  }
  return Number(field);
}

function requiredPayloadRecord(
  value: Record<string, unknown>,
  key: string,
  label: string,
): Record<string, unknown> {
  const field = value[key];
  if (!isUnknownRecord(field)) {
    throw new Error(`ParaDev ${label} requires an object ${key}.`);
  }
  return field;
}

function requiredPayloadStringRecord(
  value: Record<string, unknown>,
  key: string,
  label: string,
): Record<string, string> {
  const field = requiredPayloadRecord(value, key, label);
  if (Object.values(field).some((item) => typeof item !== "string")) {
    throw new Error(`ParaDev ${label} requires string values in ${key}.`);
  }
  return field as Record<string, string>;
}

function requiredPayloadRecordArray(
  value: Record<string, unknown>,
  key: string,
  label: string,
): Array<Record<string, unknown>> {
  const field = value[key];
  if (!Array.isArray(field) || field.some((item) => !isUnknownRecord(item))) {
    throw new Error(`ParaDev ${label} requires an object array ${key}.`);
  }
  return field;
}

type NormalizedPayloadPath = {
  value: string;
  absolute: boolean;
  caseInsensitive: boolean;
};

type ModulePayloadRoot = {
  root: NormalizedPayloadPath;
  sourceRoot: NormalizedPayloadPath;
};

function normalizedPayloadPath(
  value: string,
  label: string,
  requireAbsolute?: boolean,
  resolveTraversal = false,
): NormalizedPayloadPath {
  const raw = value;
  if (!raw.trim() || raw.includes("\0")) {
    throw new Error(`ParaDev ${label} requires a valid path.`);
  }
  const slashes = raw.replaceAll("\\", "/");
  const driveMatch = /^([A-Za-z]):(\/|$)/.exec(slashes);
  const unc = slashes.startsWith("//");
  const absolute = unc || slashes.startsWith("/") || Boolean(driveMatch?.[2]);
  if (/^[A-Za-z]:[^/]/.test(slashes)) {
    throw new Error(`ParaDev ${label} cannot use a drive-relative path.`);
  }
  if (requireAbsolute === true && !absolute) {
    throw new Error(`ParaDev ${label} requires an absolute path.`);
  }
  if (requireAbsolute === false && absolute) {
    throw new Error(`ParaDev ${label} requires a relative path.`);
  }

  let body = slashes;
  let prefix = "";
  if (unc) {
    prefix = "//";
    body = slashes.slice(2);
  } else if (driveMatch) {
    prefix = `${driveMatch[1].toUpperCase()}:${absolute ? "/" : ""}`;
    body = slashes.slice(driveMatch[0].length);
  } else if (absolute) {
    prefix = "/";
    body = slashes.slice(1);
  }
  const rawSegments = body.split("/").filter(Boolean);
  if (
    unc &&
    (rawSegments.length < 2 ||
      rawSegments
        .slice(0, 2)
        .some((segment) => segment === "." || segment === ".."))
  ) {
    throw new Error(`ParaDev ${label} requires a valid UNC server/share path.`);
  }
  const traversalFloor = unc ? 2 : 0;
  const segments: string[] = [];
  for (const segment of rawSegments) {
    if (segment !== "." && segment !== "..") {
      segments.push(segment);
      continue;
    }
    if (!resolveTraversal) {
      throw new Error(`ParaDev ${label} cannot contain traversal segments.`);
    }
    if (segment === ".." && segments.length > traversalFloor) {
      segments.pop();
    }
  }
  if (!segments.length && !absolute) {
    throw new Error(`ParaDev ${label} requires a valid path.`);
  }
  const normalized = `${prefix}${segments.join("/")}` || prefix;
  return {
    value: normalized,
    absolute,
    caseInsensitive: Boolean(driveMatch) || unc,
  };
}

function payloadPathKey(
  path: NormalizedPayloadPath,
  caseInsensitive = path.caseInsensitive,
): string {
  return caseInsensitive ? path.value.toLowerCase() : path.value;
}

function payloadPathsEqual(
  left: NormalizedPayloadPath,
  right: NormalizedPayloadPath,
): boolean {
  if (left.absolute !== right.absolute) return false;
  const caseInsensitive = left.caseInsensitive || right.caseInsensitive;
  return (
    payloadPathKey(left, caseInsensitive) ===
    payloadPathKey(right, caseInsensitive)
  );
}

function payloadPathParent(
  path: NormalizedPayloadPath,
  label: string,
): NormalizedPayloadPath {
  const separator = path.value.lastIndexOf("/");
  if (separator < 0 || /^[A-Za-z]:\/$/.test(path.value)) {
    throw new Error(`ParaDev ${label} does not have the required parent path.`);
  }
  const parent =
    separator === 0
      ? "/"
      : separator === 2 && /^[A-Za-z]:\//.test(path.value)
        ? path.value.slice(0, 3)
        : path.value.slice(0, separator);
  return normalizedPayloadPath(parent, label, path.absolute);
}

function payloadPathBasename(path: NormalizedPayloadPath): string {
  return path.value.slice(path.value.lastIndexOf("/") + 1);
}

function joinedPayloadPath(
  root: NormalizedPayloadPath,
  relative: NormalizedPayloadPath,
  label: string,
): NormalizedPayloadPath {
  if (relative.absolute) {
    throw new Error(`ParaDev ${label} requires a relative child path.`);
  }
  const separator = root.value.endsWith("/") ? "" : "/";
  return normalizedPayloadPath(
    `${root.value}${separator}${relative.value}`,
    label,
    root.absolute,
  );
}

function payloadPathRelativeTo(
  root: NormalizedPayloadPath,
  target: NormalizedPayloadPath,
): string | undefined {
  if (!root.absolute || !target.absolute) return undefined;
  const caseInsensitive = root.caseInsensitive || target.caseInsensitive;
  const rootKey = payloadPathKey(root, caseInsensitive);
  const targetKey = payloadPathKey(target, caseInsensitive);
  if (rootKey === targetKey) return "";
  const prefix = root.value.endsWith("/") ? root.value : `${root.value}/`;
  if (!targetKey.startsWith(caseInsensitive ? prefix.toLowerCase() : prefix))
    return undefined;
  return target.value.slice(prefix.length);
}

function modulePayloadRoot(
  value: string,
  family: string,
  objectId: string,
  label: string,
): ModulePayloadRoot {
  const root = normalizedPayloadPath(value, label, true);
  const folder = payloadPathBasename(root);
  const separator = folder.indexOf(" - ");
  const titledFolderObjectId =
    separator > 0 ? folder.slice(0, separator).trim() : "";
  const titledFolderTitle =
    separator > 0 ? folder.slice(separator + 3).trim() : "";
  const folderMatches =
    folder === objectId ||
    (titledFolderObjectId === objectId && Boolean(titledFolderTitle));
  const familyRoot = payloadPathParent(root, label);
  const modulesRoot = payloadPathParent(familyRoot, label);
  if (
    !folderMatches ||
    payloadPathBasename(familyRoot) !== family ||
    payloadPathBasename(modulesRoot) !== "modules"
  ) {
    throw new Error(`ParaDev ${label} is not the canonical module root.`);
  }
  return { root, sourceRoot: payloadPathParent(modulesRoot, label) };
}

function collectionPayloadRoot(
  value: string,
  family: string,
  collectionId: string,
  label: string,
): ModulePayloadRoot {
  const root = normalizedPayloadPath(value, label, true);
  const folder = payloadPathBasename(root);
  const separator = folder.indexOf(" - ");
  const titledFolderId = separator > 0 ? folder.slice(0, separator).trim() : "";
  const titledFolderTitle =
    separator > 0 ? folder.slice(separator + 3).trim() : "";
  const folderMatches =
    folder === collectionId ||
    (titledFolderId === collectionId && Boolean(titledFolderTitle));
  const familyRoot = payloadPathParent(root, label);
  const collectionsRoot = payloadPathParent(familyRoot, label);
  if (
    !folderMatches ||
    payloadPathBasename(familyRoot) !== family ||
    payloadPathBasename(collectionsRoot) !== "collections"
  ) {
    throw new Error(`ParaDev ${label} is not the canonical collection root.`);
  }
  return {
    root,
    sourceRoot: payloadPathParent(collectionsRoot, label),
  };
}

function validateOptionalModuleFolderName(
  value: Record<string, unknown>,
  root: NormalizedPayloadPath,
  label: string,
): void {
  if (!Object.hasOwn(value, "folder_name")) {
    return;
  }
  if (
    requiredPayloadString(value, "folder_name", label) !==
    payloadPathBasename(root)
  ) {
    throw new Error(`ParaDev ${label} folder_name does not match its root.`);
  }
}

function moduleIdParts(moduleId: string, label: string): [string, string] {
  const parts = moduleId.split("/");
  if (
    parts.length !== 2 ||
    parts.some(
      (part) => !part || part === "." || part === ".." || part.includes("\\"),
    )
  ) {
    throw new Error(
      `ParaDev ${label} requires a canonical family/object module id.`,
    );
  }
  return [parts[0], parts[1]];
}

function validateProjectRelativePayloadPath(
  projectRootValue: string,
  targetValue: string,
  relativeValue: string,
  label: string,
): void {
  const projectRoot = normalizedPayloadPath(
    projectRootValue,
    `${label} project root`,
    true,
    true,
  );
  const target = normalizedPayloadPath(targetValue, `${label} target`, true);
  const relative = normalizedPayloadPath(relativeValue, label);
  const expectedRelative = payloadPathRelativeTo(projectRoot, target);
  if (expectedRelative === undefined) {
    if (!relative.absolute || !payloadPathsEqual(relative, target)) {
      throw new Error(`ParaDev ${label} does not identify its target root.`);
    }
    return;
  }
  if (relative.absolute || relative.value !== expectedRelative) {
    throw new Error(`ParaDev ${label} does not identify its target root.`);
  }
}

function validateRequestedSourceRoot(
  projectRootValue: string,
  requestedSourceRootValue: string | undefined,
  actualSourceRoot: NormalizedPayloadPath,
  label: string,
): void {
  if (requestedSourceRootValue === undefined) return;
  if (!requestedSourceRootValue.trim()) {
    throw new Error(
      `ParaDev ${label} requested sourceRoot requires a valid path.`,
    );
  }
  const requested = requestedSourceRootValue.replaceAll("\\", "/");
  const requestedIsAbsolute =
    requested.startsWith("/") || /^[A-Za-z]:\//.test(requested);
  const projectRoot = normalizedPayloadPath(
    projectRootValue,
    `${label} project root`,
    true,
    true,
  );
  const expected = normalizedPayloadPath(
    requestedIsAbsolute ? requested : `${projectRoot.value}/${requested}`,
    `${label} requested sourceRoot`,
    true,
    true,
  );
  if (!payloadPathsEqual(expected, actualSourceRoot)) {
    throw new Error(
      `ParaDev ${label} source_root identity does not match the request.`,
    );
  }
}

function validateModuleScaffoldFiles(
  plan: Record<string, unknown>,
  rootValue: string,
  blocked: boolean,
  request: CreateModuleDraftRequest,
): void {
  const files = requiredPayloadRecordArray(plan, "files", "module draft plan");
  const root = normalizedPayloadPath(rootValue, "module draft plan root", true);
  for (const [index, file] of files.entries()) {
    const label = `module draft plan file ${index}`;
    const path = normalizedPayloadPath(
      requiredPayloadString(file, "path", label),
      `${label} path`,
      true,
    );
    const relativePath = requiredPayloadString(file, "relative_path", label);
    const modulePath = normalizedPayloadPath(
      requiredPayloadString(file, "module_path", label),
      `${label} module_path`,
      false,
    );
    const action = requiredPayloadString(file, "action", label);
    if (
      action !== "create" &&
      action !== "exists" &&
      action !== "overwrite" &&
      action !== "blocked"
    ) {
      throw new Error(`ParaDev ${label} has an unsupported action.`);
    }
    if (action === "overwrite" && request.force !== true) {
      throw new Error(
        "ParaDev module draft response cannot claim an overwrite that the request did not authorize.",
      );
    }
    if (action === "exists" && (request.force === true || !blocked)) {
      throw new Error(
        "ParaDev module draft response file action does not match the requested force behavior.",
      );
    }
    if (action === "blocked" && !blocked) {
      throw new Error(
        "ParaDev module draft response file action requires a blocked plan.",
      );
    }
    if (
      !payloadPathsEqual(
        path,
        joinedPayloadPath(root, modulePath, `${label} path`),
      )
    ) {
      throw new Error(`ParaDev ${label} path is outside the module root.`);
    }
    validateProjectRelativePayloadPath(
      request.projectRoot,
      path.value,
      relativePath,
      `${label} relative_path`,
    );
  }
}

function validateModuleRemoveCleanup(
  value: Record<string, unknown>,
  projectRootValue: string,
  sourceRoot: NormalizedPayloadPath,
  diagnostics: Array<Record<string, unknown>>,
  removed: boolean,
): void {
  if (!Object.hasOwn(value, "cleanup")) return;
  if (!removed) {
    throw new Error(
      "ParaDev module remove response cleanup requires a successful source removal.",
    );
  }
  const cleanup = requiredPayloadRecord(
    value,
    "cleanup",
    "module remove response",
  );
  const expectedKeys = [
    "schema",
    "status",
    "code",
    "path",
    "relative_path",
    "message",
  ];
  if (
    Object.keys(cleanup).length !== expectedKeys.length ||
    expectedKeys.some((key) => !Object.hasOwn(cleanup, key))
  ) {
    throw new Error(
      "ParaDev module remove response cleanup did not match the exact payload shape.",
    );
  }
  if (
    cleanup.schema !== "paradev.module.remove-cleanup.v1" ||
    cleanup.status !== "pending" ||
    cleanup.code !== "module_remove.cleanup_pending"
  ) {
    throw new Error(
      "ParaDev module remove response cleanup has an invalid schema/status/code combination.",
    );
  }
  const pathValue = requiredPayloadString(
    cleanup,
    "path",
    "module remove response cleanup",
  );
  const relativePath = requiredPayloadString(
    cleanup,
    "relative_path",
    "module remove response cleanup",
  );
  const message = requiredPayloadString(
    cleanup,
    "message",
    "module remove response cleanup",
  );
  const path = normalizedPayloadPath(
    pathValue,
    "module remove response cleanup path",
    true,
  );
  const trashRoot = joinedPayloadPath(
    sourceRoot,
    normalizedPayloadPath(
      ".paradev/module-trash",
      "module remove response cleanup quarantine root",
      false,
    ),
    "module remove response cleanup quarantine root",
  );
  const quarantineName = payloadPathRelativeTo(trashRoot, path);
  if (!quarantineName || quarantineName.includes("/")) {
    throw new Error(
      "ParaDev module remove response cleanup path is outside the source-root quarantine.",
    );
  }
  validateProjectRelativePayloadPath(
    projectRootValue,
    pathValue,
    relativePath,
    "module remove response cleanup relative_path",
  );
  const hasCleanupWarning = diagnostics.some(
    (diagnostic) =>
      diagnostic.severity === "warning" &&
      diagnostic.code === "module_remove.cleanup_pending" &&
      diagnostic.path === pathValue &&
      diagnostic.relative_path === relativePath &&
      diagnostic.message === message,
  );
  if (!hasCleanupWarning) {
    throw new Error(
      "ParaDev module remove response cleanup requires its matching warning diagnostic.",
    );
  }
}

function catalogMutationForSourceOperation(
  value: Record<string, unknown>,
  label: string,
  sourceCompleted: boolean,
): CatalogMutationResult | undefined {
  const hasMutation = Object.hasOwn(value, "catalog_mutation");
  if (!sourceCompleted) {
    if (hasMutation) {
      throw new Error(
        `ParaDev ${label} must omit catalog_mutation when the source operation did not complete.`,
      );
    }
    return undefined;
  }
  if (!hasMutation) {
    return unverifiedCatalogMutation(
      label,
      "the backend omitted catalog_mutation",
    );
  }
  try {
    return catalogMutationPayload(value.catalog_mutation, label);
  } catch (error) {
    const detail = error instanceof Error ? error.message : String(error);
    return unverifiedCatalogMutation(label, detail);
  }
}

function unverifiedCatalogMutation(
  label: string,
  detail: string,
): CatalogMutationResult {
  return {
    schema: "paradev.desktop.catalog-mutation-unverified.v1",
    status: "unverified",
    code: "catalog.mutation.unverified",
    message: `The ${label} source operation completed, but its Catalog synchronization result could not be verified: ${detail}`,
  };
}

function catalogMutationPayload(
  value: unknown,
  label: string,
): CatalogMutationPayload {
  if (!isUnknownRecord(value)) {
    throw new Error(`ParaDev ${label} catalog_mutation must be an object.`);
  }
  const expectedKeys =
    value.status === "failed"
      ? ["schema", "status", "code", "database", "message"]
      : ["schema", "status", "code", "database"];
  if (
    Object.keys(value).length !== expectedKeys.length ||
    expectedKeys.some((key) => !Object.hasOwn(value, key))
  ) {
    throw new Error(
      `ParaDev ${label} catalog_mutation did not match the exact payload shape.`,
    );
  }
  if (value.schema !== "paradev.hb.catalog-mutation.v1") {
    throw new Error(
      `ParaDev ${label} catalog_mutation has an unsupported schema.`,
    );
  }
  if (typeof value.database !== "string" || !value.database.trim()) {
    throw new Error(
      `ParaDev ${label} catalog_mutation requires a database path.`,
    );
  }
  const identity = { schema: value.schema, database: value.database } as const;
  switch (value.status) {
    case "applied":
      if (value.code === "catalog.mutation.applied") {
        return { ...identity, status: value.status, code: value.code };
      }
      break;
    case "not_configured":
      if (value.code === "catalog.mutation.not_configured") {
        return { ...identity, status: value.status, code: value.code };
      }
      break;
    case "failed":
      if (
        value.code === "catalog.mutation.failed" &&
        typeof value.message === "string" &&
        value.message.trim()
      ) {
        return {
          ...identity,
          status: value.status,
          code: value.code,
          message: value.message,
        };
      }
      break;
  }
  throw new Error(
    `ParaDev ${label} catalog_mutation has an invalid status/code pair.`,
  );
}

function isUnknownRecord(value: unknown): value is Record<string, unknown> {
  return value !== null && typeof value === "object" && !Array.isArray(value);
}

function normalizedProjectCatalogRoot(projectRoot: string): string {
  const normalized = projectRoot.trim();
  if (!normalized) {
    throw new Error(
      "Project catalog requests require a non-empty project root.",
    );
  }
  return normalized;
}

function normalizedCatalogFilter(
  value: string | null | undefined,
): string | undefined {
  const normalized = value?.trim();
  return normalized || undefined;
}

function projectInspectionRestFilterName(key: string): string {
  if (key === "moduleId") {
    return "module_id";
  }
  if (key === "collectionId") {
    return "collection_id";
  }
  if (key === "sourcePath") {
    return "source_path";
  }
  if (key === "targetRoot") {
    return "target_root";
  }
  if (key === "strictMetadata") {
    return "strict_metadata";
  }
  return key;
}

function sourceReplacementFrontendApiValue(
  replacement: SourceReplacement,
): Record<string, unknown> {
  return compactBody({
    path: replacement.path,
    content_base64: replacement.contentBase64,
    content_format: replacement.contentFormat,
    target_format: replacement.targetFormat,
    expected_size: replacement.expectedSize,
    expected_mtime_ns: replacement.expectedMtimeNs,
    expected_absent: replacement.expectedAbsent,
  });
}

function sourceRemovalFrontendApiValue(
  removal: string | SourceRemoval,
): string | Record<string, unknown> {
  if (typeof removal === "string") {
    return removal;
  }
  return compactBody({
    path: removal.path,
    expected_size: removal.expectedSize,
    expected_mtime_ns: removal.expectedMtimeNs,
  });
}

function sourceTextEditFrontendApiValue(
  edit: SourceTextEdit,
): Record<string, unknown> {
  return compactBody({
    path: edit.path,
    text: edit.text,
    expected_size: edit.expectedSize,
    expected_mtime_ns: edit.expectedMtimeNs,
  });
}

function compactBody(values: Record<string, unknown>): Record<string, unknown> {
  return Object.fromEntries(
    Object.entries(values).filter(
      ([, value]) => value !== undefined && value !== "",
    ),
  );
}
