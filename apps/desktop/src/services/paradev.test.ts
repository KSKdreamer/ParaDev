import { afterEach, describe, expect, it, vi } from "vitest";
import { projectOptions } from "../data/shell";
import type { ProjectBrowserPayload, SourceFormPayload } from "../types";
import {
  chatWithParaDevAi,
  checkDesktopDependency,
  applyProjectDraft,
  createModuleBatchRequest,
  createModuleDraft,
  createModules,
  duplicateModule,
  getProjectBuildRuns,
  getProjectBuildStatus,
  hasDesktopBackend,
  importProjectPackage,
  installDesktopDependency,
  interruptProjectBuild,
  editModuleDiagram,
  loadHoi4LaunchReadiness,
  loadParaDevAiChatProfiles,
  loadDesktopState,
  loadDesktopPathStatus,
  loadModuleDiagram,
  loadProjectInspection,
  loadProjectBrowser,
  loadProjectCatalogStatus,
  openProjectPath,
  planProjectLocalizationUpdate,
  planProjectSourceFormUpdates,
  queryProjectCatalog,
  readProjectBrowserCache,
  readConfigValue,
  readProjectLocalizationWorkspace,
  readProjectSourceForm,
  readTextSource,
  readThumbnailCache,
  removeCollection,
  removeModule,
  requestPdxLspCompletion,
  refreshProjectCatalog,
  resetParaDevAiChatProfile,
  renameModule,
  renameCollection,
  scaffoldCollection,
  setModuleActive,
  setModuleCollection,
  setProjectPreferredLanguage,
  runHoi4Game,
  selectProjectPath,
  sourceDraftRecoveryPathFromError,
  startProjectBuild,
  testHeavenBaseLlmRoute,
  writeParaDevAiChatProfile,
  writeConfigValue,
  writeProjectBrowserCache,
  type CreateModulesRequest,
  type ModuleDuplicatePayload,
  type ModuleCollectionPayload,
  type ModuleActivityPayload,
  type ModuleRemovePayload,
  type ModuleRenamePayload,
  type CollectionRemovePayload,
  type CollectionRenamePayload,
  type CollectionScaffoldPayload,
  type ProjectPreferredLanguagePayload,
  type ProjectCatalogQueryPayload,
  type ProjectCatalogRefreshPayload,
  type ProjectCatalogStatus,
  type ProjectCatalogStatusPayload,
  type ProjectPackageInstallPayload
} from "./paradev";

const nativeBridgePayloadMock = vi.hoisted(() => vi.fn());

function installNativeBridge() {
  const origin = "http://paradev.test";
  vi.stubGlobal("window", {
    location: { origin },
    __PARADEV_RUNTIME_CONFIG__: { nativeBridgeBaseUrl: origin }
  });
  vi.stubGlobal(
    "fetch",
    vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
      const request = input instanceof Request ? input : null;
      const url =
        typeof input === "string"
          ? input
          : input instanceof URL
            ? input.toString()
            : input.url;
      const parsedUrl = new URL(url);
      if (parsedUrl.pathname === "/frontend-api/rest-request") {
        return Response.json({
          body: {},
          method: "POST",
          path: "/test/native-operation",
          query: {}
        });
      }
      const payload = await nativeBridgePayloadMock({
        body: init?.body ?? (request ? await request.clone().text() : undefined),
        method: init?.method ?? request?.method ?? "GET",
        url
      });
      const responsePayload =
        parsedUrl.pathname === "/desktop/select-project" &&
        typeof payload === "string"
          ? {
              path: payload,
              schema: "paradev.desktop.project-selection.v1"
            }
          : payload;
      return new Response(JSON.stringify(responsePayload), {
        headers: { "content-type": "application/json" },
        status: 200
      });
    })
  );
}

function moduleCreateBatchRequest(): CreateModulesRequest {
  return {
    projectId: "PIHC3",
    projectRoot: "/tmp/PIHC3",
    modules: [
      {
        family: "idea",
        object_id: "IDEA_DEMO",
        values: { title: "Demo Idea" }
      }
    ]
  };
}

function moduleCreateBatchPlanPayload(): Record<string, unknown> {
  return {
    schema: "paradev.sdk.module_batch.v1",
    project_id: "PIHC3",
    source_root: "/tmp/PIHC3/src",
    plan_hash: "a".repeat(64),
    blocked: false,
    applied: false,
    written: false,
    requested_count: 1,
    counts: { create: 1, created: 0, unchanged: 0, blocked: 0 },
    diagnostics: [],
    modules: [
      {
        index: 0,
        template_id: "hoi4:idea/basic",
        family: "idea",
        object_id: "IDEA_DEMO",
        module_id: "idea/IDEA_DEMO",
        root: "/tmp/PIHC3/src/modules/idea/IDEA_DEMO",
        status: "create",
        blocked: false,
        diagnostics: [],
        files: []
      }
    ]
  };
}

function projectCatalogQueryPayload(): ProjectCatalogQueryPayload {
  return {
    schema: "paradev.hb.catalog-query.v1",
    project_id: "PIHC3",
    database: "/tmp/PIHC3/.paradev/.cache/hb/catalog.sqlite",
    filters: { entity: "hoi4-module", tag: "scripted_effect", limit: 100, include_data: false },
    total_count: 1_116_679,
    filtered_count: 8_279,
    count: 1,
    data_included: false,
    page: { offset: 0, limit: 100, has_more: true, next_offset: 1 },
    rows: [
      {
        object_id: "catalog/module/scripted_effect/ADD_FOG_OF_WAR_BUILDING",
        target_id: "module/scripted_effect/ADD_FOG_OF_WAR_BUILDING",
        target_entity: "hoi4-module",
        name: "scripted_effect/ADD_FOG_OF_WAR_BUILDING",
        desc: "",
        tags: ["module", "scripted_effect", "scripted_effect/ADD_FOG_OF_WAR_BUILDING"],
        active: true,
        workspace_id: "PIHC3-hoi4"
      }
    ]
  };
}

function installedProjectPackagePayload(): ProjectPackageInstallPayload {
  const projectRoot = "/Users/demo/Documents/ParaDev/Projects/PIHC3-0.2.3";
  return {
    schema: "paradev.desktop.project-package-install.v1",
    status: "installed",
    installed: true,
    project_root: projectRoot,
    package: {
      id: "pihc3-0.2.3",
      label: "PIHC3 0.2.3",
      game: "hoi4",
      archive_name: "PIHC3-0.2.3-project.zip",
      archive_sha256: "8".repeat(64),
      archive_size: 100,
      project_id: "PIHC3",
      project_version: "0.2.3",
      top_level_folder: "PIHC3-0.2.3",
      entry_count: 3,
      file_count: 2,
      directory_count: 1,
      uncompressed_size: 80,
      compressed_size: 60,
      max_member_path_code_units: 42
    },
    project: {
      project_id: "PIHC3",
      title: "PIHC3",
      game: "hoi4",
      root: projectRoot,
      manifest: `${projectRoot}/paradev.yaml`,
      source_roots: [`${projectRoot}/src`]
    }
  };
}

function projectCatalogRefreshPayload(): ProjectCatalogRefreshPayload {
  return {
    schema: "paradev.hb.catalog-refresh.v1",
    project_id: "PIHC3",
    game: "hoi4",
    profile: "hoi4",
    workspace_id: "PIHC3-hoi4",
    registered_entities: ["hoi4-module"],
    enabled_extensions: { "paradev.hoi4": {} },
    preview_counts: { module: 18_038 },
    row_counts: { module: 18_038 },
    catalog_count: 1_116_679,
    catalog_counts: { "hoi4-module": 18_038 },
    metaschema_entity_count: 21,
    ok: true,
    database: "/tmp/PIHC3/.paradev/.cache/hb/catalog.sqlite",
    removed: ["/tmp/PIHC3/.paradev/.cache/hb/catalog.sqlite"],
    recovered: []
  };
}

function projectCatalogStatusPayload(status: ProjectCatalogStatus = "present"): ProjectCatalogStatusPayload {
  const identity = {
    schema: "paradev.hb.catalog-status.v1" as const,
    project_id: "PIHC3",
    database: "/tmp/PIHC3/.paradev/.cache/hb/catalog.sqlite"
  };
  switch (status) {
    case "present":
      return { ...identity, status, code: "catalog.present" };
    case "missing":
      return { ...identity, status, code: "catalog.missing" };
    case "incomplete":
      return { ...identity, status, code: "catalog.incomplete" };
    case "unreadable":
      return { ...identity, status, code: "catalog.unreadable" };
  }
}

function validModuleDraftResponse() {
  return {
    schema: "paradev.rest.module_draft.v1",
    project_id: "PIHC3",
    family_id: "ideas",
    draft_id: "ideas:IDEA_DEMO",
    plan: {
      schema: "paradev.sdk.module_scaffold.v1",
      project_id: "PIHC3",
      template_id: "idea",
      family: "idea",
      object_id: "IDEA_DEMO",
      module_id: "idea/IDEA_DEMO",
      source_root: "/tmp/PIHC3/src",
      root: "/tmp/PIHC3/src/modules/idea/IDEA_DEMO",
      values: {},
      blocked: false,
      written: true,
      diagnostics: [],
      files: [],
      catalog_mutation: {
        schema: "paradev.hb.catalog-mutation.v1",
        status: "applied",
        code: "catalog.mutation.applied",
        database: "/tmp/PIHC3/.paradev/.cache/hb/catalog.sqlite"
      }
    }
  };
}

function validModuleRenameResponse() {
  return {
    schema: "paradev.module.rename.v1",
    project_id: "PIHC3",
    previous_module_id: "modifier/demo",
    module_id: "modifier/renamed",
    family: "modifier",
    previous_root: "/tmp/PIHC3/src/modules/modifier/demo",
    root: "/tmp/PIHC3/src/modules/modifier/renamed",
    previous_relative_path: "src/modules/modifier/demo",
    relative_path: "src/modules/modifier/renamed",
    content_rewritten: false,
    module: {},
    catalog_mutation: {
      schema: "paradev.hb.catalog-mutation.v1",
      status: "applied",
      code: "catalog.mutation.applied",
      database: "/tmp/PIHC3/.paradev/.cache/hb/catalog.sqlite"
    }
  };
}

function validCollectionRenameResponse(): CollectionRenamePayload {
  return {
    schema: "paradev.collection.rename.v1",
    project_id: "PIHC3",
    previous_collection_id: "C01_OLD",
    collection_id: "C01_NEW",
    family: "focus",
    source_root: "/tmp/PIHC3/src",
    previous_root: "/tmp/PIHC3/src/collections/focus/C01_OLD",
    root: "/tmp/PIHC3/src/collections/focus/C01_NEW",
    previous_relative_path: "src/collections/focus/C01_OLD",
    relative_path: "src/collections/focus/C01_NEW",
    content_rewritten: true,
    member_count: 1,
    members: ["focus/FOCUS_DEMO"],
    files: [],
    collection: {},
    catalog_mutation: {
      schema: "paradev.hb.catalog-mutation.v1",
      status: "applied",
      code: "catalog.mutation.applied",
      database: "/tmp/PIHC3/.paradev/.cache/hb/catalog.sqlite"
    }
  };
}

function validCollectionScaffoldResponse(): CollectionScaffoldPayload {
  return {
    schema: "paradev.sdk.collection_scaffold.v1",
    project_id: "PIHC3",
    template_id: "pihc3:focus-tree/basic",
    kind: "collection",
    family: "focus",
    object_id: "C01_NEW",
    collection_id: "C01_NEW",
    folder_name: "C01_NEW",
    source_root: "/tmp/PIHC3/src",
    root: "/tmp/PIHC3/src/collections/focus/C01_NEW",
    values: { title: "New focus tree" },
    blocked: false,
    written: false,
    applied: false,
    plan_hash: "a".repeat(64),
    diagnostics: [],
    files: [],
    authoring_plan: {},
  };
}

function validProjectPreferredLanguageResponse(
  written = false,
  blocked = false,
): ProjectPreferredLanguagePayload {
  return {
    schema: "paradev.project.preferred-language.v1",
    project_id: "PIHC3",
    manifest: "/tmp/PIHC3/paradev.yaml",
    previous_language: "en",
    preferred_language: "zh",
    changed: true,
    written,
    blocked,
    diagnostics: blocked
      ? [{
          code: "project_preferred_language.plan_hash_mismatch",
          severity: "error",
          message: "The project manifest changed after planning."
        }]
      : [],
    plan_hash: "a".repeat(64),
    revision: {
      size: 128,
      sha256: "b".repeat(64)
    }
  };
}

function validModuleDuplicateResponse(
  status: ModuleDuplicatePayload["status"] = "planned"
): ModuleDuplicatePayload {
  const duplicated = status === "duplicated";
  const blocked = status === "blocked";
  return {
    schema: "paradev.sdk.module_duplicate.v1",
    project_id: "PIHC3",
    source_module_id: "modifier/demo",
    module_id: "modifier/demo_copy",
    family: "modifier",
    object_id: "demo_copy",
    source_root: "/tmp/PIHC3/src",
    destination_source_root: "/tmp/PIHC3/src",
    source_module_root: "/tmp/PIHC3/src/modules/modifier/demo",
    root: "/tmp/PIHC3/src/modules/modifier/demo_copy",
    source_relative_path: "src/modules/modifier/demo",
    relative_path: "src/modules/modifier/demo_copy",
    status,
    blocked,
    applied: duplicated,
    written: duplicated,
    plan_hash: "d".repeat(64),
    identity_mode: "rewrite",
    identity_rewriter: "paradev.token-identity.v1",
    content_rewritten: true,
    paths_rewritten: false,
    diagnostics: [],
    directories: [
      {
        relative_path: "assets",
        target_relative_path: "assets",
        kind: "directory",
        identity: [1, 11],
        mode: 493,
        mtime_ns: "123456789",
        action: "copy"
      }
    ],
    files: [
      {
        relative_path: "def.txt",
        target_relative_path: "def.txt",
        kind: "file",
        identity: [1, 12],
        mode: 420,
        mtime_ns: "123456790",
        size_bytes: 18,
        sha256: "e".repeat(64),
        target_size_bytes: 22,
        target_sha256: "f".repeat(64),
        content_rewritten: true,
        action: "rewrite"
      }
    ],
    exclusions: [
      {
        relative_path: ".paradev",
        kind: "directory",
        identity: [1, 13],
        mode: 493,
        mtime_ns: "123456791",
        reason: "module_local_system_tree",
        action: "exclude"
      }
    ],
    totals: {
      directory_count: 1,
      file_count: 1,
      excluded_count: 1,
      size_bytes: 18,
      target_size_bytes: 22,
      rewritten_file_count: 1,
      renamed_path_count: 0
    },
    source: {
      module_id: "modifier/demo",
      source_root: "/tmp/PIHC3/src",
      root: "/tmp/PIHC3/src/modules/modifier/demo",
      relative_path: "src/modules/modifier/demo",
      root_identity: [1, 1],
      modules_identity: [1, 2],
      family_identity: [1, 3],
      module_identity: [1, 4],
      tree_digest: "a".repeat(64),
      content_digest: "b".repeat(64),
      identity_rewriter: "paradev.token-identity.v1"
    },
    destination: {
      module_id: "modifier/demo_copy",
      source_root: "/tmp/PIHC3/src",
      root: "/tmp/PIHC3/src/modules/modifier/demo_copy",
      relative_path: "src/modules/modifier/demo_copy",
      root_identity: [1, 1],
      modules_identity: [1, 2],
      family_identity: [1, 3],
      target_identity: duplicated ? [1, 14] : null,
      entry_count: 2,
      entry_names_digest: "c".repeat(64),
      content_digest: "1".repeat(64)
    },
    ...(duplicated
      ? {
          catalog_mutation: {
            schema: "paradev.hb.catalog-mutation.v1",
            status: "applied",
            code: "catalog.mutation.applied",
            database: "/tmp/PIHC3/.paradev/.cache/hb/catalog.sqlite"
          }
        }
      : {})
  };
}

function validModuleCollectionResponse(
  phase: "planned" | "updated" | "blocked" = "planned",
): ModuleCollectionPayload {
  const blocked = phase === "blocked";
  const updated = phase === "updated";
  return {
    schema: "paradev.sdk.module_collection_update.v1",
    project_id: "PIHC3",
    project_root: "/tmp/PIHC3",
    module_id: "focus/FOCUS_DEMO",
    family: "focus",
    source_root: "/tmp/PIHC3/src",
    previous_collection_id: null,
    collection_id: "C01_focus_tree",
    changed: true,
    blocked,
    applied: updated,
    written: updated,
    status: phase,
    plan_hash: "9".repeat(64),
    diagnostics: blocked
      ? [{
          code: "module_collection_update.plan_hash_mismatch",
          severity: "error",
          message: "Module metadata changed after planning."
        }]
      : [],
    files: [
      {
        path: "/tmp/PIHC3/src/modules/focus/FOCUS_DEMO/.paradev/meta.yaml",
        relative_path: "src/modules/focus/FOCUS_DEMO/.paradev/meta.yaml",
        layer: "hidden",
        action: "create",
        before_sha256: null,
        after_sha256: "8".repeat(64)
      }
    ],
    module: {},
    collection: {},
    ...(updated
      ? {
          catalog_mutation: {
            schema: "paradev.hb.catalog-mutation.v1",
            status: "applied",
            code: "catalog.mutation.applied",
            database: "/tmp/PIHC3/.paradev/.cache/hb/catalog.sqlite"
          }
        }
      : {})
  };
}

function validModuleActivityResponse(
  phase: "planned" | "updated" | "blocked" = "planned",
): ModuleActivityPayload {
  const blocked = phase === "blocked";
  const updated = phase === "updated";
  return {
    schema: "paradev.sdk.module_activity_update.v1",
    project_id: "PIHC3",
    project_root: "/tmp/PIHC3",
    module_id: "bookmark/PIHC_DIE_NEBENWELT",
    family: "bookmark",
    source_root: "/tmp/PIHC3/src",
    previous_active: false,
    active: true,
    changed: true,
    blocked,
    applied: updated,
    written: updated,
    status: phase,
    plan_hash: "7".repeat(64),
    diagnostics: blocked
      ? [
          {
            code: "module_activity_update.plan_hash_mismatch",
            severity: "error",
            message: "Module metadata changed after planning.",
          },
        ]
      : [],
    files: [
      {
        path: "/tmp/PIHC3/src/modules/bookmark/PIHC_DIE_NEBENWELT/meta.yaml",
        relative_path:
          "src/modules/bookmark/PIHC_DIE_NEBENWELT/meta.yaml",
        layer: "visible",
        action: "remove",
        before_sha256: "6".repeat(64),
        after_sha256: null,
      },
    ],
    module: {},
    ...(updated
      ? {
          catalog_mutation: {
            schema: "paradev.hb.catalog-mutation.v1",
            status: "applied",
            code: "catalog.mutation.applied",
            database: "/tmp/PIHC3/.paradev/.cache/hb/catalog.sqlite",
          },
        }
      : {}),
  };
}

function validModuleRemoveResponse() {
  return {
    schema: "paradev.module.remove.v1",
    project_id: "PIHC3",
    module_id: "modifier/demo",
    family: "modifier",
    source_root: "/tmp/PIHC3/src",
    root: "/tmp/PIHC3/src/modules/modifier/demo",
    relative_path: "src/modules/modifier/demo",
    blocked: false,
    removed: true,
    diagnostics: [],
    files: [],
    module: {},
    catalog_mutation: {
      schema: "paradev.hb.catalog-mutation.v1",
      status: "applied",
      code: "catalog.mutation.applied",
      database: "/tmp/PIHC3/.paradev/.cache/hb/catalog.sqlite"
    }
  };
}

function validCollectionRemoveResponse(
  removed = false,
): CollectionRemovePayload {
  return {
    schema: "paradev.collection.remove.v1",
    project_id: "PIHC3",
    collection_id: "C01_OLD",
    family: "focus",
    source_root: "/tmp/PIHC3/src",
    root: "/tmp/PIHC3/src/collections/focus/C01_OLD",
    relative_path: "src/collections/focus/C01_OLD",
    status: removed ? "removed" : "planned",
    write: removed,
    blocked: false,
    applied: removed,
    written: removed,
    removed,
    plan_hash: "c".repeat(64),
    diagnostics: [],
    files: [],
    members: ["focus/FOCUS_DEMO"],
    member_files: [],
    counts: {
      members_preserved: 1,
      member_metadata_files: 0,
      descriptor_files: 0
    },
    collection: {},
    ...(removed
      ? {
          catalog_mutation: {
            schema: "paradev.hb.catalog-mutation.v1" as const,
            status: "applied",
            code: "catalog.mutation.applied",
            database: "/tmp/PIHC3/.paradev/.cache/hb/catalog.sqlite"
          }
        }
      : {})
  };
}

function validSourceFormPayload(): SourceFormPayload {
  return {
    schema: "paradev.source-form.v1",
    contract: "pihc2.entity.record.v1",
    project_id: "PIHC3",
    family: "Entity",
    module_id: "Entity/VIENTO_MIRROR",
    path: "/tmp/PIHC3/src/modules/Entity/VIENTO_MIRROR/record.json",
    relative_path: "src/modules/Entity/VIENTO_MIRROR/record.json",
    module_relative_path: "record.json",
    source_root: "/tmp/PIHC3/src",
    source_format: "json",
    label: { default: "Entity record", zh: "实体记录" },
    sections: [
      {
        id: "mesh",
        label: "Mesh",
        controls: [
          {
            id: "mesh.scale",
            label: "Scale",
            control: "number",
            value: 4.25,
            patch: { op: "replace-json-scalar", path: ["mesh", "scale"] },
            min: 0,
            step: 0.05,
            placeholder: { default: "For example, 1.0", zh: "例如 1.0" }
          }
        ]
      }
    ]
  };
}

function validPdxSourceFormPayload(): SourceFormPayload {
  return {
    schema: "paradev.source-form.v1",
    contract: "paradev.pdx.guided-form.v1",
    project_id: "PIHC3",
    family: "idea",
    module_id: "idea/IDEA_TEST",
    path: "/tmp/PIHC3/src/modules/idea/IDEA_TEST/def.txt",
    relative_path: "src/modules/idea/IDEA_TEST/def.txt",
    module_relative_path: "def.txt",
    source_root: "/tmp/PIHC3/src",
    source_format: "pdx",
    label: "Guided PDX fields",
    coverage: { truncated: true, shown_controls: 1, total_controls: 104 },
    sections: [
      {
        id: "pdx-section-000",
        label: "Top level",
        controls: [
          {
            id: "pdx-control-000",
            label: "Active",
            description: "Whether this equipment definition is active.",
            description_source: "declared",
            control: "boolean",
            value: true,
            patch: {
              op: "replace-pdx-scalar",
              path: [{ key: "active", occurrence: 0 }],
              span: { start: 9, end: 12 },
              expected: "yes",
              scalar_kind: "boolean",
              source_length: 13
            }
          }
        ]
      }
    ]
  };
}

function validPdxIntegerListSourceFormPayload(): SourceFormPayload {
  const expected = " 345 1637 ";
  return {
    schema: "paradev.source-form.v1",
    contract: "paradev.pdx.guided-form.v1",
    project_id: "PIHC3",
    family: "state",
    module_id: "state/199",
    path: "/tmp/PIHC3/src/modules/state/199/def.txt",
    relative_path: "src/modules/state/199/def.txt",
    module_relative_path: "def.txt",
    source_root: "/tmp/PIHC3/src",
    source_format: "pdx",
    sections: [
      {
        id: "state",
        label: "state",
        controls: [
          {
            id: "provinces",
            label: "Provinces",
            control: "text",
            value: "345\n1637",
            multiline: true,
            patch: {
              op: "replace-pdx-integer-list",
              path: [{ key: "provinces", occurrence: 0 }],
              span: { start: 0, end: expected.length },
              expected,
              item_kind: "integer",
              columns: 1,
              minimum: 1,
              layout: {
                prefix: " ",
                column_separator: " ",
                row_separator: " ",
                suffix: " "
              },
              source_length: expected.length
            }
          }
        ]
      }
    ]
  };
}

function validPdxBlockBodySourceFormPayload(): SourceFormPayload {
  const expected = "\n    add_power = 5\n";
  return {
    schema: "paradev.source-form.v1",
    contract: "paradev.pdx.guided-form.v1",
    project_id: "PIHC3",
    family: "scripted_effect",
    module_id: "scripted_effect/MY_EFFECT",
    path: "/tmp/PIHC3/src/modules/scripted_effect/MY_EFFECT/def.txt",
    relative_path: "src/modules/scripted_effect/MY_EFFECT/def.txt",
    module_relative_path: "def.txt",
    source_root: "/tmp/PIHC3/src",
    source_format: "pdx",
    sections: [
      {
        id: "effect",
        label: "Top level",
        controls: [
          {
            id: "effect-body",
            label: "Effect body",
            control: "text",
            value: "add_power = 5",
            multiline: true,
            patch: {
              op: "replace-pdx-block-body",
              path: [{ key: "MY_EFFECT", occurrence: 0 }],
              span: { start: 0, end: expected.length },
              expected,
              layout: {
                prefix: "\n    ",
                line_prefix: "\n    ",
                suffix: "\n"
              },
              source_length: expected.length
            }
          }
        ]
      }
    ]
  };
}

function validLocSourceFormPayload(): SourceFormPayload {
  return {
    schema: "paradev.source-form.v1",
    contract: "paradev.localization.text-form.v1",
    project_id: "PIHC3",
    family: "idea",
    module_id: "idea/IDEA_TEST",
    path: "/tmp/PIHC3/src/modules/idea/IDEA_TEST/main.loc",
    relative_path: "src/modules/idea/IDEA_TEST/main.loc",
    module_relative_path: "main.loc",
    source_root: "/tmp/PIHC3/src",
    source_format: "loc",
    label: "Localization text",
    coverage: { truncated: false, shown_controls: 1, total_controls: 1 },
    sections: [
      {
        id: "loc-language-000",
        label: "English",
        controls: [
          {
            id: "loc-control-000",
            label: "IDEA_TEST",
            control: "text",
            value: "Old title",
            multiline: true,
            patch: {
              op: "replace-loc-text",
              path: {
                language: "l_english",
                key: "IDEA_TEST",
                occurrence: 0
              },
              span: { start: 15, end: 24 },
              expected: "Old title",
              style: "section",
              newline: "\n",
              source_length: 25
            }
          }
        ]
      }
    ]
  };
}

function validCollectionLocalizationWorkspacePayload(): Record<string, unknown> {
  const path = "/tmp/PIHC3/src/collections/decision/DECISION_CATEGORY_TEST - Test/main.loc";
  return {
    schema: "paradev.localization-workspace.v2",
    project_id: "PIHC3",
    target: {
      kind: "collection",
      id: "DECISION_CATEGORY_TEST",
      family: "decision",
      object_id: "DECISION_CATEGORY_TEST"
    },
    source_root: "/tmp/PIHC3/src",
    languages: ["l_english"],
    rows: [{
      key: "DECISION_CATEGORY_TEST",
      values: {
        l_english: {
          text: "Test category",
          source_path: path,
          relative_path: "src/collections/decision/DECISION_CATEGORY_TEST - Test/main.loc",
          slot: "loc",
          occurrence: 0
        }
      }
    }],
    sources: [{
      path,
      relative_path: "src/collections/decision/DECISION_CATEGORY_TEST - Test/main.loc",
      unit_relative_path: "main.loc",
      slot: "loc",
      source_format: "ini",
      languages: ["l_english"],
      size: 52,
      mtime_ns: "1700000000000000000"
    }],
    coverage: { truncated: false, shown_rows: 1, total_rows: 1 }
  };
}

function validSourceFormUpdateBatchPayload(): Record<string, unknown> {
  const path = "/tmp/PIHC3/src/modules/Entity/VIENTO_MIRROR/record.json";
  const sourceEdit = {
    path,
    text: '{"mesh":{"scale":4.5}}\n',
    expected_size: 24,
    expected_mtime_ns: "1770000000123456789"
  };
  return {
    schema: "paradev.source-form-update-batch.v1",
    project_id: "PIHC3",
    changed: true,
    counts: { requested: 1, changed: 1, unchanged: 0 },
    updates: [
      {
        schema: "paradev.source-form-update.v1",
        project_id: "PIHC3",
        family: "Entity",
        module_id: "Entity/VIENTO_MIRROR",
        path,
        relative_path: "src/modules/Entity/VIENTO_MIRROR/record.json",
        source_format: "json",
        form_contract: "pihc2.entity.record.v1",
        changed: true,
        changes: [
          { control_id: "mesh.scale", previous: 4.25, value: 4.5 }
        ],
        source_edit: sourceEdit
      }
    ],
    source_edits: [sourceEdit]
  };
}

describe("ParaDev desktop service", () => {
  afterEach(() => {
    nativeBridgePayloadMock.mockReset();
    vi.unstubAllGlobals();
    vi.unstubAllEnvs();
  });

  it("uses static project options without a desktop backend", async () => {
    vi.stubGlobal("window", {});

    const state = await loadDesktopState(projectOptions[0].path);

    expect(state.active_project?.project_id).toBe(projectOptions[0].projectId);
    expect(state.active_project?.source_roots).toEqual(projectOptions[0].sourceRoots);
    expect(state.active_project?.output_root).toBe(projectOptions[0].outputRoot);
    expect(state.active_project?.build_root).toBe(projectOptions[0].buildRoot);
  });

  it("surfaces native desktop-state command failures instead of silently falling back", async () => {
    installNativeBridge();
    nativeBridgePayloadMock.mockRejectedValueOnce(new Error("desktop-state failed"));

    await expect(loadDesktopState("/tmp/PIHC3")).rejects.toThrow("desktop-state failed");
  });

  it("selects a project folder through the native web bridge", async () => {
    installNativeBridge();
    nativeBridgePayloadMock.mockResolvedValueOnce("/tmp/PIHC3");

    await expect(selectProjectPath()).resolves.toBe("/tmp/PIHC3");
  });

  it("selects a project folder through the native web bridge", async () => {
    vi.stubGlobal("window", {});
    vi.stubEnv("VITE_PARADEV_NATIVE_BRIDGE_URL", "http://127.0.0.1:47831");
    const fetchMock = vi.fn().mockResolvedValueOnce({
      ok: true,
      status: 200,
      statusText: "OK",
      json: async () => ({
        schema: "paradev.desktop.project-selection.v1",
        path: "/tmp/PIHC3"
      })
    });
    vi.stubGlobal("fetch", fetchMock);

    await expect(selectProjectPath()).resolves.toBe("/tmp/PIHC3");
    expect(fetchMock).toHaveBeenCalledWith(
      "http://127.0.0.1:47831/desktop/select-project",
      {
        body: "{}",
        headers: { "content-type": "application/json" },
        method: "POST"
      }
    );
  });

  it("rejects project folder selection without a desktop backend", async () => {
    vi.stubGlobal("window", {});

    await expect(selectProjectPath()).rejects.toThrow("Selecting a project folder requires the ParaDev desktop application.");
  });

  it("returns a normal null thumbnail-cache miss through the native web bridge", async () => {
    installNativeBridge();
    nativeBridgePayloadMock.mockResolvedValueOnce(null);

    await expect(readThumbnailCache("/tmp/PIHC3", "v1|ideas:IDEA_ALPHA|icon.png")).resolves.toBeNull();
  });

  it("returns a validated thumbnail-cache hit through the native web bridge", async () => {
    installNativeBridge();
    const payload = {
      schema: "paradev.desktop.binary-source.v1" as const,
      path: "/tmp/PIHC3/.paradev/.cache/instance-thumbnails/hit.png",
      mimeType: "image/png",
      bytes: [137, 80, 78, 71]
    };
    nativeBridgePayloadMock.mockResolvedValueOnce(payload);

    await expect(readThumbnailCache("/tmp/PIHC3", "hit")).resolves.toEqual(payload);
  });

  it("rejects malformed thumbnail-cache payloads through the native web bridge", async () => {
    installNativeBridge();
    nativeBridgePayloadMock.mockResolvedValueOnce({
      schema: "paradev.desktop.binary-source.v1",
      path: "/tmp/PIHC3/.paradev/.cache/instance-thumbnails/bad.png",
      mimeType: "image/png",
      bytes: [137, -1]
    });

    await expect(readThumbnailCache("/tmp/PIHC3", "corrupt")).rejects.toThrow(
      "ParaDev returned an invalid thumbnail-cache response."
    );
  });

  it("returns a normal null thumbnail-cache miss through the native web bridge", async () => {
    vi.stubGlobal("window", {});
    vi.stubEnv("VITE_PARADEV_NATIVE_BRIDGE_URL", "http://127.0.0.1:47831");
    const fetchMock = vi.fn().mockResolvedValueOnce({
      ok: true,
      status: 200,
      statusText: "OK",
      json: async () => null
    });
    vi.stubGlobal("fetch", fetchMock);

    await expect(readThumbnailCache("/tmp/PIHC3", "v1|ideas:IDEA_ALPHA|icon.png")).resolves.toBeNull();
    expect(fetchMock).toHaveBeenCalledWith(
      "http://127.0.0.1:47831/desktop/thumbnail-cache?project_root=%2Ftmp%2FPIHC3&cache_key=v1%7Cideas%3AIDEA_ALPHA%7Cicon.png",
      { method: "GET" }
    );
  });

  it("installs and validates a project package through the native web bridge", async () => {
    installNativeBridge();
    const payload = installedProjectPackagePayload();
    nativeBridgePayloadMock.mockResolvedValueOnce(payload);

    await expect(importProjectPackage()).resolves.toEqual(payload);
  });

  it("treats cancelling project-package selection as a no-op", async () => {
    installNativeBridge();
    nativeBridgePayloadMock.mockResolvedValueOnce(null);

    await expect(importProjectPackage()).resolves.toBeNull();
  });

  it("installs and validates a project package through the native web bridge", async () => {
    vi.stubGlobal("window", {});
    vi.stubEnv("VITE_PARADEV_NATIVE_BRIDGE_URL", "http://127.0.0.1:47831");
    const payload = installedProjectPackagePayload();
    const fetchMock = vi.fn().mockResolvedValueOnce({
      ok: true,
      status: 200,
      statusText: "OK",
      json: async () => payload
    });
    vi.stubGlobal("fetch", fetchMock);

    await expect(importProjectPackage()).resolves.toEqual(payload);
    expect(fetchMock).toHaveBeenCalledWith(
      "http://127.0.0.1:47831/desktop/import-project-package",
      {
        body: "{}",
        headers: { "content-type": "application/json" },
        method: "POST"
      }
    );
  });

  it("treats native project-package picker cancellation as a no-op", async () => {
    vi.stubGlobal("window", {});
    vi.stubEnv("VITE_PARADEV_NATIVE_BRIDGE_URL", "http://127.0.0.1:47831");
    vi.stubGlobal("fetch", vi.fn().mockResolvedValueOnce({
      ok: true,
      status: 200,
      statusText: "OK",
      json: async () => null
    }));

    await expect(importProjectPackage()).resolves.toBeNull();
  });

  it("rejects invalid native project-package responses", async () => {
    vi.stubGlobal("window", {});
    vi.stubEnv("VITE_PARADEV_NATIVE_BRIDGE_URL", "http://127.0.0.1:47831");
    vi.stubGlobal("fetch", vi.fn().mockResolvedValueOnce({
      ok: true,
      status: 200,
      statusText: "OK",
      json: async () => ({
        schema: "paradev.desktop.project-package-install.v1",
        status: "installed",
        installed: false
      })
    }));

    await expect(importProjectPackage()).rejects.toThrow(
      "inconsistent project-package installation response"
    );
  });

  it("rejects inconsistent project-package bridge responses", async () => {
    installNativeBridge();
    nativeBridgePayloadMock.mockResolvedValueOnce({
      schema: "paradev.desktop.project-package-install.v1",
      status: "installed",
      installed: false
    });

    await expect(importProjectPackage()).rejects.toThrow(
      "inconsistent project-package installation response"
    );
  });

  it("rejects project-package installation outside the desktop application", async () => {
    vi.stubGlobal("window", {});

    await expect(importProjectPackage()).rejects.toThrow(
      "Installing a project package requires the ParaDev desktop application."
    );
  });

  it("loads scoped project-browser payloads through the native web bridge", async () => {
    installNativeBridge();
    nativeBridgePayloadMock.mockResolvedValueOnce({
      schema: "paradev.sdk.project-browser.v1",
      project_id: "PIHC3",
      title: "PIHC3",
      root: "/tmp/PIHC3",
      profile: "hoi4",
      filters: {},
      families: [],
      items: [],
      diagnostics: []
    });

    await loadProjectBrowser({ projectRoot: "/tmp/PIHC3", family: "focus_tree", moduleId: "C01_MAIN" });

  });

  it("loads source-backed module diagrams through the native web bridge", async () => {
    installNativeBridge();
    const payload = {
      schema: "paradev.sdk.module_diagram.v1",
      provider_schema: "paradev.hoi4.technology-diagram.v1",
      project_id: "PIHC3",
      project_root: "/tmp/PIHC3",
      profile: "hoi4",
      family: "technology",
      source_kind: "technology",
      editable: true,
      sources: [],
      nodes: [],
      edges: [],
      diagnostics: [],
      summary: { source_count: 0, node_count: 0, edge_count: 0 }
    };
    nativeBridgePayloadMock.mockResolvedValueOnce(payload);

    await expect(
      loadModuleDiagram({
        projectRoot: "/tmp/PIHC3",
        family: "technology",
        profile: "hoi4"
      })
    ).resolves.toEqual(payload);

  });

  it("plans and applies source-backed diagram edits through the native web bridge", async () => {
    installNativeBridge();
    const planHash = "a".repeat(64);
    const payload = {
      schema: "paradev.sdk.module_diagram_edit.v1",
      provider_schema: "paradev.hoi4.technology-diagram-edit.v1",
      project_id: "PIHC3",
      project_root: "/tmp/PIHC3",
      profile: "hoi4",
      family: "technology",
      status: "applied",
      plan_hash: planHash,
      blocked: false,
      applied: true,
      written: true,
      drafts: [],
      source_replacements: [],
      diagnostics: [],
      files: []
    };
    nativeBridgePayloadMock.mockResolvedValueOnce(payload);
    const request = {
      projectRoot: "/tmp/PIHC3",
      family: "technology",
      profile: "hoi4",
      positionIntents: [
        {
          technology_id: "TECHNOLOGY_FIREARM_I",
          x: 12,
          y: 4,
          source_revision: "b".repeat(64)
        }
      ],
      edgeIntents: [
        {
          kind: "path" as const,
          source_id: "TECHNOLOGY_FIREARM_I",
          target_id: "TECHNOLOGY_FIREARM_II",
          present: true,
          source_revision: "b".repeat(64)
        }
      ],
      write: true,
      planHash
    };

    await expect(editModuleDiagram(request)).resolves.toEqual(payload);

  });


  it("loads project inspections through the native web bridge", async () => {
    installNativeBridge();
    nativeBridgePayloadMock.mockResolvedValueOnce({
      schema: "paradev.build.diagnostics.v1",
      project_id: "PIHC3",
      profile: "hoi4",
      diagnostics: [{ code: "metadata.unknown_key", severity: "error" }],
      index: { error: { "metadata.unknown_key": [0] } }
    });

    const payload = await loadProjectInspection({
      projectRoot: "/tmp/PIHC3",
      kind: "diagnostics",
      filters: { strictMetadata: false, severity: "error", moduleId: null }
    });

    expect(payload.diagnostics).toHaveLength(1);
  });

  it("loads project inspections through the native web bridge", async () => {
    vi.stubGlobal("window", {});
    vi.stubEnv("VITE_PARADEV_NATIVE_BRIDGE_URL", "http://127.0.0.1:47831");
    const fetchMock = vi.fn().mockResolvedValueOnce({
      ok: true,
      status: 200,
      statusText: "OK",
      json: async () => ({
        schema: "paradev.build.diagnostics.v1",
        project_id: "PIHC3",
        profile: "hoi4",
        diagnostics: [],
        index: {}
      })
    });
    vi.stubGlobal("fetch", fetchMock);

    await loadProjectInspection({
      projectRoot: "/tmp/PIHC3",
      kind: "diagnostics",
      filters: { strictMetadata: true }
    });

    expect(fetchMock).toHaveBeenCalledWith("http://127.0.0.1:47831/projects/inspect?path=%2Ftmp%2FPIHC3&kind=diagnostics&strict_metadata=true", {
      method: "GET"
    });
  });

  it("queries bounded project catalog pages through the native web bridge", async () => {
    installNativeBridge();
    nativeBridgePayloadMock
      .mockResolvedValueOnce(projectCatalogStatusPayload())
      .mockResolvedValueOnce(projectCatalogQueryPayload());

    const payload = await queryProjectCatalog({
      projectRoot: "/tmp/PIHC3",
      entity: " module ",
      tag: " scripted_effect "
    });

    expect(payload.filtered_count).toBe(8_279);
    expect(payload.rows[0]?.data).toBeUndefined();
  });

  it("queries hydrated project catalog rows through the native web bridge", async () => {
    vi.stubGlobal("window", {});
    vi.stubEnv("VITE_PARADEV_NATIVE_BRIDGE_URL", "http://127.0.0.1:47831");
    const hydrated = projectCatalogQueryPayload();
    hydrated.filters = { target_id: "module/focus/GER_sample", limit: 1, offset: 2 };
    hydrated.data_included = true;
    hydrated.page = { offset: 2, limit: 1, has_more: false, next_offset: null };
    hydrated.rows[0] = { ...hydrated.rows[0], data: { family: "focus", module_id: "focus/GER_sample" } };
    const fetchMock = vi.fn()
      .mockResolvedValueOnce({
        ok: true,
        status: 200,
        statusText: "OK",
        json: async () => projectCatalogStatusPayload()
      })
      .mockResolvedValueOnce({
        ok: true,
        status: 200,
        statusText: "OK",
        json: async () => hydrated
      });
    vi.stubGlobal("fetch", fetchMock);

    const payload = await queryProjectCatalog({
      projectRoot: "/tmp/PIHC3",
      targetId: "module/focus/GER_sample",
      limit: 1,
      offset: 2,
      includeData: true
    });

    expect(payload.rows[0]?.data).toEqual({ family: "focus", module_id: "focus/GER_sample" });
    expect(fetchMock).toHaveBeenNthCalledWith(
      1,
      "http://127.0.0.1:47831/projects/catalog?path=%2Ftmp%2FPIHC3",
      { method: "GET" }
    );
    expect(fetchMock).toHaveBeenCalledWith(
      "http://127.0.0.1:47831/projects/inspect?path=%2Ftmp%2FPIHC3&kind=catalog-query&target_id=module%2Ffocus%2FGER_sample&limit=1&offset=2&include_data=true",
      { method: "GET" }
    );
  });

  it("does not probe the catalog query endpoint when the optional index is missing", async () => {
    vi.stubGlobal("window", {});
    vi.stubEnv("VITE_PARADEV_NATIVE_BRIDGE_URL", "http://127.0.0.1:47831");
    const fetchMock = vi.fn().mockResolvedValueOnce({
      ok: true,
      status: 200,
      statusText: "OK",
      json: async () => projectCatalogStatusPayload("missing")
    });
    vi.stubGlobal("fetch", fetchMock);

    await expect(
      queryProjectCatalog({
        projectRoot: "/tmp/PIHC3",
        entity: "module",
        tag: "technology"
      })
    ).rejects.toThrow("The optional project index is not prepared.");

    expect(fetchMock).toHaveBeenCalledTimes(1);
    expect(fetchMock).toHaveBeenCalledWith(
      "http://127.0.0.1:47831/projects/catalog?path=%2Ftmp%2FPIHC3",
      { method: "GET" }
    );
  });

  it("loads every project catalog status variant through the native web bridge", async () => {
    installNativeBridge();
    const statuses: ProjectCatalogStatus[] = ["present", "missing", "incomplete", "unreadable"];

    for (const status of statuses) {
      nativeBridgePayloadMock.mockResolvedValueOnce(projectCatalogStatusPayload(status));

      const payload = await loadProjectCatalogStatus({ projectRoot: "  /tmp/PIHC3  " });

      expect(payload).toEqual(projectCatalogStatusPayload(status));
    }
  });

  it("loads the project catalog status through the native web bridge", async () => {
    vi.stubGlobal("window", {});
    vi.stubEnv("VITE_PARADEV_NATIVE_BRIDGE_URL", "http://127.0.0.1:47831");
    const fetchMock = vi.fn().mockResolvedValueOnce({
      ok: true,
      status: 200,
      statusText: "OK",
      json: async () => projectCatalogStatusPayload("missing")
    });
    vi.stubGlobal("fetch", fetchMock);

    const payload = await loadProjectCatalogStatus({ projectRoot: "/tmp/PIHC3" });

    expect(payload.status).toBe("missing");
    expect(payload.code).toBe("catalog.missing");
    expect(fetchMock).toHaveBeenCalledWith("http://127.0.0.1:47831/projects/catalog?path=%2Ftmp%2FPIHC3", { method: "GET" });
  });

  it("rejects malformed project catalog status responses at the service boundary", async () => {
    installNativeBridge();
    const invalidPayloads: unknown[] = [
      null,
      { ...projectCatalogStatusPayload(), schema: "paradev.hb.catalog-status.v0" },
      { ...projectCatalogStatusPayload(), code: "catalog.missing" },
      { ...projectCatalogStatusPayload(), project_id: "" },
      { ...projectCatalogStatusPayload(), detail: "unexpected field" }
    ];

    for (const payload of invalidPayloads) {
      nativeBridgePayloadMock.mockResolvedValueOnce(payload);
      await expect(loadProjectCatalogStatus({ projectRoot: "/tmp/PIHC3" })).rejects.toThrow("ParaDev project catalog status response");
    }
  });

  it("rejects unsafe project catalog pages before calling the desktop bridge", async () => {
    installNativeBridge();

    await expect(queryProjectCatalog({ projectRoot: "/tmp/PIHC3", limit: 201 })).rejects.toThrow(
      "Project catalog query limit must be an integer from 1 to 200."
    );
    await expect(queryProjectCatalog({ projectRoot: "/tmp/PIHC3", includeData: true })).rejects.toThrow(
      "Hydrated project catalog queries must have limit 1."
    );
    await expect(queryProjectCatalog({ projectRoot: "/tmp/PIHC3", offset: -1 })).rejects.toThrow(
      "Project catalog query offset must be an integer from 0 to 4294967295."
    );
    await expect(queryProjectCatalog({ projectRoot: "/tmp/PIHC3", offset: 4_294_967_296 })).rejects.toThrow(
      "Project catalog query offset must be an integer from 0 to 4294967295."
    );
  });

  it("rejects empty project catalog roots before either desktop transport", async () => {
    installNativeBridge();

    await expect(queryProjectCatalog({ projectRoot: "  " })).rejects.toThrow(
      "Project catalog requests require a non-empty project root."
    );
    await expect(loadProjectCatalogStatus({ projectRoot: "\n" })).rejects.toThrow(
      "Project catalog requests require a non-empty project root."
    );

    vi.stubGlobal("window", {});
    vi.stubEnv("VITE_PARADEV_NATIVE_BRIDGE_URL", "http://127.0.0.1:47831");
    const fetchMock = vi.fn();
    vi.stubGlobal("fetch", fetchMock);

    await expect(refreshProjectCatalog({ projectRoot: "\t" })).rejects.toThrow(
      "Project catalog requests require a non-empty project root."
    );
    expect(fetchMock).not.toHaveBeenCalled();
  });

  it("refreshes the project catalog through the native web bridge", async () => {
    installNativeBridge();
    nativeBridgePayloadMock.mockResolvedValueOnce(projectCatalogRefreshPayload());

    const payload = await refreshProjectCatalog({ projectRoot: "/tmp/PIHC3", profile: "hoi4" });

    expect(payload.ok).toBe(true);
    expect(payload.catalog_count).toBe(1_116_679);
  });

  it("refreshes the project catalog through the native web bridge query contract", async () => {
    vi.stubGlobal("window", {});
    vi.stubEnv("VITE_PARADEV_NATIVE_BRIDGE_URL", "http://127.0.0.1:47831");
    const fetchMock = vi.fn().mockResolvedValueOnce({
      ok: true,
      status: 200,
      statusText: "OK",
      json: async () => projectCatalogRefreshPayload()
    });
    vi.stubGlobal("fetch", fetchMock);

    await refreshProjectCatalog({ projectRoot: "/tmp/PIHC3", profile: "hoi4" });

    expect(fetchMock).toHaveBeenCalledWith("http://127.0.0.1:47831/projects/catalog?path=%2Ftmp%2FPIHC3&profile=hoi4", { method: "PUT" });
  });

  it("loads desktop path status through the native web bridge", async () => {
    installNativeBridge();
    nativeBridgePayloadMock.mockResolvedValueOnce({
      schema: "paradev.desktop.path-status.v1",
      inputPath: "/tmp/PIHC3",
      path: "/tmp/PIHC3",
      exists: true,
      kind: "directory",
      readable: true,
      openable: true
    });

    const status = await loadDesktopPathStatus("/tmp/PIHC3");

    expect(status.kind).toBe("directory");
    expect(status.openable).toBe(true);
  });

  it("loads desktop path status through the native web bridge", async () => {
    vi.stubGlobal("window", {});
    vi.stubEnv("VITE_PARADEV_NATIVE_BRIDGE_URL", "http://127.0.0.1:47831");
    const fetchMock = vi.fn().mockResolvedValueOnce({
      ok: true,
      status: 200,
      statusText: "OK",
      json: async () => ({
        schema: "paradev.desktop.path-status.v1",
        inputPath: "/tmp/PIHC3/build/mod",
        path: "/tmp/PIHC3/build/mod",
        exists: false,
        kind: "missing",
        readable: false,
        openable: false
      })
    });
    vi.stubGlobal("fetch", fetchMock);

    const status = await loadDesktopPathStatus("/tmp/PIHC3/build/mod");

    expect(status.exists).toBe(false);
    expect(status.kind).toBe("missing");
    expect(fetchMock).toHaveBeenCalledWith("http://127.0.0.1:47831/desktop/path-status?path=%2Ftmp%2FPIHC3%2Fbuild%2Fmod", {
      method: "GET"
    });
  });

  it("persists project-browser cache payloads through the native web bridge", async () => {
    installNativeBridge();
    const payload: ProjectBrowserPayload = {
      schema: "paradev.sdk.project-browser.v1",
      project_id: "PIHC3",
      title: "PIHC3",
      root: "/tmp/PIHC3",
      profile: "hoi4",
      filters: {},
      families: [],
      items: [],
      diagnostics: []
    };
    nativeBridgePayloadMock.mockResolvedValueOnce(payload);
    nativeBridgePayloadMock.mockResolvedValueOnce(payload);

    await writeProjectBrowserCache(payload);
    const cached = await readProjectBrowserCache("/tmp/PIHC3");

    expect(cached).toEqual(payload);
  });

  it("creates module batch request previews through the native web bridge", async () => {
    installNativeBridge();
    nativeBridgePayloadMock.mockResolvedValueOnce({
      schema: "paradev.module.batch_edit_request.v1",
      project_id: "PIHC3",
      create: true,
      encoding: "utf-8",
      edit_count: 1,
      summary: {
        edit_count: 1,
        module_count: 1,
        source_root_count: 0,
        existing_target_count: 0,
        missing_target_count: 1,
        changed_target_count: 1,
        unchanged_target_count: 0,
        create_enabled_count: 1,
        encoding_count: 1
      },
      edits: [],
      index: {},
      targets: [],
      target_index: {}
    });

    await createModuleBatchRequest({
      projectRoot: "/tmp/PIHC3",
      create: true,
      edits: [
        {
          module_id: "technology/TECHNOLOGY_AIR_CLOUDSHIP",
          relative_path: "migration/notes.txt",
          text: "generated\n"
        }
      ]
    });

  });

  it("creates transactional module batches through the native web bridge", async () => {
    installNativeBridge();
    const payload = {
      schema: "paradev.sdk.module_batch.v1",
      project_id: "PIHC3",
      source_root: "/tmp/PIHC3/src",
      plan_hash: "a".repeat(64),
      blocked: false,
      applied: false,
      written: false,
      requested_count: 1,
      counts: { create: 1, created: 0, unchanged: 0, blocked: 0 },
      diagnostics: [],
      modules: [
        {
          index: 0,
          template_id: "hoi4:idea/basic",
          family: "idea",
          object_id: "IDEA_DEMO",
          module_id: "idea/IDEA_DEMO",
          root: "/tmp/PIHC3/src/modules/idea/IDEA_DEMO",
          status: "create",
          blocked: false,
          diagnostics: [],
          files: []
        }
      ]
    };
    nativeBridgePayloadMock.mockResolvedValueOnce(payload);
    const request = {
      projectId: "PIHC3",
      projectRoot: "/tmp/PIHC3",
      modules: [
        {
          family: "idea",
          object_id: "IDEA_DEMO",
          values: { title: "Demo Idea" }
        }
      ]
    };

    await expect(createModules(request)).resolves.toEqual(payload);

  });

  it("accepts titled module roots returned for transactional batches", async () => {
    installNativeBridge();
    const payload = moduleCreateBatchPlanPayload();
    const folderName = "IDEA_DEMO - Demo Idea";
    payload.modules = [
      {
        ...(payload.modules as Array<Record<string, unknown>>)[0],
        root: `/tmp/PIHC3/src/modules/idea/${folderName}`,
        folder_name: folderName,
        files: [
          {
            path: `/tmp/PIHC3/src/modules/idea/${folderName}/meta.yaml`,
            relative_path: `src/modules/idea/${folderName}/meta.yaml`,
            module_path: "meta.yaml",
            action: "create"
          }
        ]
      }
    ];
    nativeBridgePayloadMock.mockResolvedValueOnce(payload);

    await expect(createModules(moduleCreateBatchRequest())).resolves.toEqual(payload);
  });

  it.each([
    {
      label: "schema",
      update: (payload: Record<string, unknown>) => ({ ...payload, schema: "paradev.sdk.module_batch.v0" }),
      message: "unsupported schema"
    },
    {
      label: "counts",
      update: (payload: Record<string, unknown>) => ({
        ...payload,
        counts: { create: 0, created: 0, unchanged: 0, blocked: 0 }
      }),
      message: "counts do not total"
    },
    {
      label: "diagnostics",
      update: (payload: Record<string, unknown>) => ({
        ...payload,
        diagnostics: [{ code: "module_batch.rollback_incomplete", severity: "error", message: "Retained." }]
      }),
      message: "requires recovery_path"
    },
    {
      label: "blocked state",
      update: (payload: Record<string, unknown>) => ({
        ...payload,
        counts: { create: 0, created: 0, unchanged: 0, blocked: 1 },
        modules: [
          {
            ...(payload.modules as Array<Record<string, unknown>>)[0],
            status: "blocked",
            blocked: true
          }
        ]
      }),
      message: "without blocked state"
    },
    {
      label: "module identity",
      update: (payload: Record<string, unknown>) => ({
        ...payload,
        modules: [
          {
            ...(payload.modules as Array<Record<string, unknown>>)[0],
            module_id: "idea/OTHER"
          }
        ]
      }),
      message: "module identity is inconsistent"
    },
    {
      label: "titled root identity",
      update: (payload: Record<string, unknown>) => ({
        ...payload,
        modules: [
          {
            ...(payload.modules as Array<Record<string, unknown>>)[0],
            root: "/tmp/PIHC3/src/modules/idea/OTHER - Demo Idea"
          }
        ]
      }),
      message: "is not the canonical module root"
    },
    {
      label: "titled root source containment",
      update: (payload: Record<string, unknown>) => ({
        ...payload,
        modules: [
          {
            ...(payload.modules as Array<Record<string, unknown>>)[0],
            root: "/tmp/PIHC3/imports/modules/idea/IDEA_DEMO - Demo Idea"
          }
        ]
      }),
      message: "root does not match the batch source_root"
    },
    {
      label: "folder name identity",
      update: (payload: Record<string, unknown>) => ({
        ...payload,
        modules: [
          {
            ...(payload.modules as Array<Record<string, unknown>>)[0],
            folder_name: "IDEA_DEMO - Other Title"
          }
        ]
      }),
      message: "folder_name does not match its root"
    },
    {
      label: "nested diagnostic state",
      update: (payload: Record<string, unknown>) => ({
        ...payload,
        modules: [
          {
            ...(payload.modules as Array<Record<string, unknown>>)[0],
            diagnostics: [
              {
                code: "module_batch.module_conflict",
                severity: "error",
                message: "Conflict."
              }
            ]
          }
        ]
      }),
      message: "error diagnostic without blocked state"
    },
    {
      label: "file identity",
      update: (payload: Record<string, unknown>) => ({
        ...payload,
        modules: [
          {
            ...(payload.modules as Array<Record<string, unknown>>)[0],
            files: [
              {
                path: "/tmp/PIHC3/src/modules/idea/OTHER/meta.yaml",
                relative_path: "src/modules/idea/OTHER/meta.yaml",
                module_path: "meta.yaml",
                action: "create"
              }
            ]
          }
        ]
      }),
      message: "path does not match its module_path"
    }
  ])("rejects malformed transactional module batch $label payloads", async ({ update, message }) => {
    installNativeBridge();
    const valid = moduleCreateBatchPlanPayload();
    nativeBridgePayloadMock.mockResolvedValueOnce(update(valid));

    await expect(createModules(moduleCreateBatchRequest())).rejects.toThrow(message);
  });

  it("rejects applied module batches that acknowledge a different plan hash", async () => {
    installNativeBridge();
    const payload = moduleCreateBatchPlanPayload();
    payload.applied = true;
    payload.written = true;
    payload.plan_hash = "b".repeat(64);
    payload.counts = { create: 0, created: 1, unchanged: 0, blocked: 0 };
    payload.modules = [
      {
        ...(payload.modules as Array<Record<string, unknown>>)[0],
        status: "created"
      }
    ];
    nativeBridgePayloadMock.mockResolvedValueOnce(payload);

    await expect(
      createModules({
        ...moduleCreateBatchRequest(),
        write: true,
        planHash: "a".repeat(64)
      })
    ).rejects.toThrow("plan_hash does not match");
  });

  it("rejects module batch applies that report neither applied nor blocked", async () => {
    installNativeBridge();
    nativeBridgePayloadMock.mockResolvedValueOnce(moduleCreateBatchPlanPayload());

    await expect(
      createModules({
        ...moduleCreateBatchRequest(),
        write: true,
        planHash: "a".repeat(64)
      })
    ).rejects.toThrow("either applied or blocked");
  });

  it("rejects module batch rows that do not match the requested selector", async () => {
    installNativeBridge();
    const payload = moduleCreateBatchPlanPayload();
    payload.modules = [
      {
        ...(payload.modules as Array<Record<string, unknown>>)[0],
        family: "modifier",
        module_id: "modifier/IDEA_DEMO",
        template_id: "hoi4:modifier/basic"
      }
    ];
    nativeBridgePayloadMock.mockResolvedValueOnce(payload);

    await expect(createModules(moduleCreateBatchRequest())).rejects.toThrow(
      "template or family does not match"
    );
  });

  it("accepts a changed plan hash when an apply is safely blocked as stale", async () => {
    installNativeBridge();
    const payload = moduleCreateBatchPlanPayload();
    payload.plan_hash = "b".repeat(64);
    payload.blocked = true;
    payload.diagnostics = [
      {
        code: "module_batch.plan_hash_mismatch",
        severity: "error",
        message: "Review the changed plan."
      }
    ];
    nativeBridgePayloadMock.mockResolvedValueOnce(payload);

    await expect(
      createModules({
        ...moduleCreateBatchRequest(),
        write: true,
        planHash: "a".repeat(64)
      })
    ).resolves.toMatchObject({
      blocked: true,
      applied: false,
      plan_hash: "b".repeat(64)
    });
  });

  it("rejects a module batch source root that differs from the explicit request", async () => {
    installNativeBridge();
    nativeBridgePayloadMock.mockResolvedValueOnce(moduleCreateBatchPlanPayload());

    await expect(
      createModules({
        ...moduleCreateBatchRequest(),
        sourceRoot: "/tmp/PIHC3/other"
      })
    ).rejects.toThrow("source_root identity does not match");
  });

  it("rejects rollback recovery paths outside the module transaction root", async () => {
    installNativeBridge();
    const payload = moduleCreateBatchPlanPayload();
    payload.blocked = true;
    payload.diagnostics = [
      {
        code: "module_batch.rollback_incomplete",
        severity: "error",
        message: "Retained.",
        recovery_path: "/tmp/PIHC3/untrusted"
      }
    ];
    nativeBridgePayloadMock.mockResolvedValueOnce(payload);

    await expect(createModules(moduleCreateBatchRequest())).rejects.toThrow(
      "under the module transaction root"
    );
  });

  it("marks created module rows unverified when the batch response omits Catalog status", async () => {
    installNativeBridge();
    const payload = moduleCreateBatchPlanPayload();
    payload.applied = true;
    payload.written = true;
    payload.counts = { create: 0, created: 1, unchanged: 0, blocked: 0 };
    payload.modules = [
      {
        ...(payload.modules as Array<Record<string, unknown>>)[0],
        status: "created"
      }
    ];
    nativeBridgePayloadMock.mockResolvedValueOnce(payload);
    const request = {
      ...moduleCreateBatchRequest(),
      write: true,
      planHash: "a".repeat(64)
    };

    const result = await createModules(request);

    expect(result.modules[0].catalog_mutation).toMatchObject({
      schema: "paradev.desktop.catalog-mutation-unverified.v1",
      status: "unverified",
      code: "catalog.mutation.unverified"
    });
  });

  it("creates module drafts through generated REST planning in the native web bridge", async () => {
    vi.stubGlobal("window", {});
    vi.stubEnv("VITE_PARADEV_NATIVE_BRIDGE_URL", "http://127.0.0.1:47831");
    const values = { title: "Demo Idea" };
    const payload = {
      schema: "paradev.rest.module_draft.v1",
      project_id: "PIHC3",
      family_id: "ideas",
      draft_id: "ideas:IDEA_DEMO",
      plan: {
        schema: "paradev.sdk.module_scaffold.v1",
        project_id: "PIHC3",
        template_id: "idea",
        family: "idea",
        object_id: "IDEA_DEMO",
        module_id: "idea/IDEA_DEMO",
        source_root: "/tmp/PIHC3/src",
        root: "/tmp/PIHC3/src/modules/idea/IDEA_DEMO",
        values,
        blocked: false,
        written: false,
        diagnostics: [],
        files: []
      }
    };
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce({
        ok: true,
        status: 200,
        statusText: "OK",
        json: async () => ({
          schema: "paradev.sdk.frontend-api.rest-request.v1",
          operation_id: "module.draft",
          method: "POST",
          path: "/projects/PIHC3/modules/ideas/drafts",
          query: {},
          body: {
            project_root: "/tmp/PIHC3",
            template_id: "idea",
            object_id: "IDEA_DEMO",
            values,
            write: false,
            force: false
          },
          binding: {
            method: "POST",
            path: "/projects/{project_id}/modules/{family_id}/drafts",
            query: {}
          },
          normalized: {
            schema: "paradev.sdk.frontend-api.inputs.v1",
            operation_id: "module.draft",
            values: {},
            project: { path: "/tmp/PIHC3" },
            parameters: {
              family_id: "ideas",
              template_id: "idea",
              object_id: "IDEA_DEMO",
              values,
              write: false,
              force: false
            },
            selectors: {},
            projections: {}
          }
        })
      })
      .mockResolvedValueOnce({
        ok: true,
        status: 200,
        statusText: "OK",
        json: async () => payload
      });
    vi.stubGlobal("fetch", fetchMock);

    await expect(
      createModuleDraft({
        projectId: "PIHC3",
        projectRoot: "/tmp/PIHC3",
        familyId: "ideas",
        templateId: "idea",
        objectId: "IDEA_DEMO",
        values,
        write: false,
        force: false
      })
    ).resolves.toEqual(payload);

    expect(fetchMock).toHaveBeenNthCalledWith(1, "http://127.0.0.1:47831/frontend-api/rest-request?operation_id=module.draft", {
      body: JSON.stringify({
        project_id: "PIHC3",
        family_id: "ideas",
        path: "/tmp/PIHC3",
        template_id: "idea",
        object_id: "IDEA_DEMO",
        values,
        write: false,
        force: false
      }),
      headers: { "Content-Type": "application/json" },
      method: "POST"
    });
    expect(fetchMock).toHaveBeenNthCalledWith(2, "http://127.0.0.1:47831/projects/PIHC3/modules/ideas/drafts", {
      body: JSON.stringify({
        project_root: "/tmp/PIHC3",
        template_id: "idea",
        object_id: "IDEA_DEMO",
        values,
        write: false,
        force: false
      }),
      headers: { "Content-Type": "application/json" },
      method: "POST"
    });
    expect(fetchMock.mock.calls.map(([url]) => String(url))).not.toContain("http://127.0.0.1:47831/desktop/modules/draft");
  });

  it("renames modules with the SDK payload schema through the native web bridge", async () => {
    installNativeBridge();
    const payload: ModuleRenamePayload = {
      schema: "paradev.module.rename.v1",
      project_id: "PIHC3",
      previous_module_id: "modifier/starter_starter_modifier",
      module_id: "modifier/starter_renamed_modifier",
      family: "modifier",
      previous_root: "/tmp/PIHC3/src/modules/modifier/starter_starter_modifier",
      root: "/tmp/PIHC3/src/modules/modifier/starter_renamed_modifier",
      previous_relative_path: "src/modules/modifier/starter_starter_modifier",
      relative_path: "src/modules/modifier/starter_renamed_modifier",
      content_rewritten: false,
      module: {},
      catalog_mutation: {
        schema: "paradev.hb.catalog-mutation.v1",
        status: "applied",
        code: "catalog.mutation.applied",
        database: "/tmp/PIHC3/.paradev/.cache/hb/catalog.sqlite"
      }
    };
    nativeBridgePayloadMock.mockResolvedValueOnce(payload);

    await expect(
      renameModule({
        projectRoot: "/tmp/PIHC3",
        moduleId: "modifier/starter_starter_modifier",
        objectId: "starter_renamed_modifier",
        title: "Friendly Modifier"
      })
    ).resolves.toEqual(payload);
  });

  it("plans and applies the exact project-language revision through the native web bridge", async () => {
    installNativeBridge();
    const plan = validProjectPreferredLanguageResponse();
    const applied = validProjectPreferredLanguageResponse(true);
    nativeBridgePayloadMock.mockResolvedValueOnce(plan).mockResolvedValueOnce(applied);

    await expect(
      setProjectPreferredLanguage("/tmp/PIHC3", "zh")
    ).resolves.toEqual(applied);

  });

  it("renames a collection through the same Registry-owned desktop path", async () => {
    installNativeBridge();
    const payload = validCollectionRenameResponse();
    nativeBridgePayloadMock.mockResolvedValueOnce(payload);

    await expect(
      renameCollection({
        projectRoot: "/tmp/PIHC3",
        collectionId: "C01_OLD",
        targetId: "C01_NEW",
        family: "focus",
        sourceRoot: "/tmp/PIHC3/src"
      })
    ).resolves.toEqual(payload);
  });

  it("scaffolds collections through generated REST planning in the native web bridge", async () => {
    vi.stubGlobal("window", {});
    vi.stubEnv("VITE_PARADEV_NATIVE_BRIDGE_URL", "http://127.0.0.1:47831");
    const payload = validCollectionScaffoldResponse();
    const request = {
      projectRoot: "/tmp/PIHC3",
      templateId: "pihc3:focus-tree/basic",
      collectionId: "C01_NEW",
      values: { title: "New focus tree" },
      sourceRoot: "src",
    };
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce({
        ok: true,
        status: 200,
        statusText: "OK",
        json: async () => ({
          schema: "paradev.sdk.frontend-api.rest-request.v1",
          operation_id: "collection.scaffold",
          method: "POST",
          path: "/projects/collections/scaffold",
          query: {
            path: "/tmp/PIHC3",
            template_id: "pihc3:focus-tree/basic",
            collection_id: "C01_NEW",
            source_root: "src",
            write: false,
            force: false,
          },
          body: { values: { title: "New focus tree" } },
          binding: {
            method: "POST",
            path: "/projects/collections/scaffold",
            query: {},
          },
          normalized: {
            schema: "paradev.sdk.frontend-api.inputs.v1",
            operation_id: "collection.scaffold",
            values: {},
            project: { path: "/tmp/PIHC3" },
            parameters: {},
            selectors: {},
            projections: {},
          },
        }),
      })
      .mockResolvedValueOnce({
        ok: true,
        status: 200,
        statusText: "OK",
        json: async () => payload,
      });
    vi.stubGlobal("fetch", fetchMock);

    await expect(scaffoldCollection(request)).resolves.toEqual(payload);
    expect(fetchMock).toHaveBeenNthCalledWith(
      1,
      "http://127.0.0.1:47831/frontend-api/rest-request?operation_id=collection.scaffold",
      {
        body: JSON.stringify({
          path: "/tmp/PIHC3",
          template_id: "pihc3:focus-tree/basic",
          collection_id: "C01_NEW",
          source_root: "src",
          values: { title: "New focus tree" },
        }),
        headers: { "Content-Type": "application/json" },
        method: "POST",
      },
    );
    expect(fetchMock).toHaveBeenNthCalledWith(
      2,
      "http://127.0.0.1:47831/projects/collections/scaffold?path=%2Ftmp%2FPIHC3&template_id=pihc3%3Afocus-tree%2Fbasic&collection_id=C01_NEW&source_root=src&write=false&force=false",
      {
        body: JSON.stringify({ values: { title: "New focus tree" } }),
        headers: { "Content-Type": "application/json" },
        method: "POST",
      },
    );
  });

  it("plans and removes a collection with the exact reviewed hash", async () => {
    installNativeBridge();
    const plan = validCollectionRemoveResponse();
    const applied = validCollectionRemoveResponse(true);
    nativeBridgePayloadMock.mockResolvedValueOnce(plan).mockResolvedValueOnce(applied);

    await expect(
      removeCollection({
        projectRoot: "/tmp/PIHC3",
        collectionId: "C01_OLD",
        family: "focus",
        sourceRoot: "/tmp/PIHC3/src"
      })
    ).resolves.toEqual(applied);
  });

  it("surfaces a stale project-language apply diagnostic", async () => {
    installNativeBridge();
    nativeBridgePayloadMock
      .mockResolvedValueOnce(validProjectPreferredLanguageResponse())
      .mockResolvedValueOnce(validProjectPreferredLanguageResponse(false, true));

    await expect(
      setProjectPreferredLanguage("/tmp/PIHC3", "zh")
    ).rejects.toThrow("The project manifest changed after planning.");
  });

  it("previews and applies an exact module duplicate plan through the native web bridge", async () => {
    installNativeBridge();
    const preview = validModuleDuplicateResponse();
    const applied = validModuleDuplicateResponse("duplicated");
    nativeBridgePayloadMock.mockResolvedValueOnce(preview).mockResolvedValueOnce(applied);

    await expect(
      duplicateModule({
        projectRoot: "/tmp/PIHC3",
        moduleId: "modifier/demo",
        objectId: "demo_copy",
        sourceRoot: "src"
      })
    ).resolves.toEqual(preview);
    await expect(
      duplicateModule({
        projectRoot: "/tmp/PIHC3",
        moduleId: "modifier/demo",
        objectId: "demo_copy",
        sourceRoot: "src",
        destinationSourceRoot: "src",
        write: true,
        planHash: preview.plan_hash
      })
    ).resolves.toEqual(applied);

  });

  it("plans and applies collection membership without exposing hidden metadata", async () => {
    installNativeBridge();
    const plan = validModuleCollectionResponse();
    const applied = validModuleCollectionResponse("updated");
    nativeBridgePayloadMock.mockResolvedValueOnce(plan).mockResolvedValueOnce(applied);

    await expect(
      setModuleCollection({
        projectRoot: "/tmp/PIHC3",
        moduleId: "focus/FOCUS_DEMO",
        collectionId: "C01_focus_tree",
        sourceRoot: "src"
      })
    ).resolves.toEqual(applied);

  });

  it("rejects an inconsistent module collection apply before refreshing the GUI", async () => {
    installNativeBridge();
    nativeBridgePayloadMock
      .mockResolvedValueOnce(validModuleCollectionResponse())
      .mockResolvedValueOnce({
        ...validModuleCollectionResponse("updated"),
        applied: false,
        written: false,
        status: "planned"
      });

    await expect(
      setModuleCollection({
        projectRoot: "/tmp/PIHC3",
        moduleId: "focus/FOCUS_DEMO",
        collectionId: "C01_focus_tree"
      })
    ).rejects.toThrow("apply state is inconsistent");
  });

  it("plans and activates an inactive module through the guarded desktop bridge", async () => {
    installNativeBridge();
    const plan = validModuleActivityResponse();
    const applied = validModuleActivityResponse("updated");
    nativeBridgePayloadMock.mockResolvedValueOnce(plan).mockResolvedValueOnce(applied);

    await expect(
      setModuleActive({
        projectRoot: "/tmp/PIHC3",
        moduleId: "bookmark/PIHC_DIE_NEBENWELT",
        active: true,
        sourceRoot: "src",
      }),
    ).resolves.toEqual(applied);

  });

  it("preserves an actionable blocked duplicate response when inspection has no filesystem snapshot", async () => {
    installNativeBridge();
    const planned = validModuleDuplicateResponse("blocked");
    const payload: ModuleDuplicatePayload = {
      ...planned,
      identity_rewriter: null,
      content_rewritten: false,
      paths_rewritten: false,
      diagnostics: [
        {
          code: "module_duplicate.symlink",
          message: "The source module contains a symbolic link.",
          severity: "error"
        }
      ],
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
        renamed_path_count: 0
      },
      source: {
        ...planned.source,
        root_identity: null,
        modules_identity: null,
        family_identity: null,
        module_identity: null,
        tree_digest: null,
        content_digest: null,
        identity_rewriter: null
      },
      destination: {
        ...planned.destination,
        root_identity: null,
        modules_identity: null,
        family_identity: null,
        target_identity: null,
        entry_count: 0,
        entry_names_digest: null,
        content_digest: null
      }
    };
    nativeBridgePayloadMock.mockResolvedValueOnce(payload);

    await expect(
      duplicateModule({
        projectRoot: "/tmp/PIHC3",
        moduleId: "modifier/demo",
        objectId: "demo_copy"
      })
    ).resolves.toEqual(payload);
  });

  it.each([
    {
      case: "wrong source identity",
      payload: {
        ...validModuleDuplicateResponse(),
        source_module_id: "modifier/other"
      },
      message: "identity does not match the request"
    },
    {
      case: "missing identity rewriter",
      payload: {
        ...validModuleDuplicateResponse(),
        identity_rewriter: null
      },
      message: "inconsistent identity rewrite summary"
    },
    {
      case: "mismatched inventory total",
      payload: {
        ...validModuleDuplicateResponse(),
        totals: {
          ...validModuleDuplicateResponse().totals,
          file_count: 2
        }
      },
      message: "totals do not match its inventory"
    },
    {
      case: "write without exact plan hash",
      payload: validModuleDuplicateResponse("duplicated"),
      message: "does not match its exact plan_hash",
      write: true
    },
    {
      case: "partial source snapshot",
      payload: {
        ...validModuleDuplicateResponse("blocked"),
        source: {
          ...validModuleDuplicateResponse("blocked").source,
          content_digest: null
        }
      },
      message: "incomplete source snapshot"
    }
  ])("rejects a module duplicate response with $case", async ({ payload, message, write }) => {
    installNativeBridge();
    nativeBridgePayloadMock.mockResolvedValueOnce(payload);

    await expect(
      duplicateModule({
        projectRoot: "/tmp/PIHC3",
        moduleId: "modifier/demo",
        objectId: "demo_copy",
        ...(write ? { write } : {})
      })
    ).rejects.toThrow(message);
  });

  it("removes modules with the SDK payload schema through the native web bridge", async () => {
    installNativeBridge();
    const payload: ModuleRemovePayload = {
      schema: "paradev.module.remove.v1",
      project_id: "PIHC3",
      module_id: "modifier/starter_starter_modifier",
      family: "modifier",
      source_root: "/tmp/PIHC3/src",
      root: "/tmp/PIHC3/src/modules/modifier/starter_starter_modifier",
      relative_path: "src/modules/modifier/starter_starter_modifier",
      blocked: false,
      removed: true,
      diagnostics: [],
      files: [],
      module: {},
      catalog_mutation: {
        schema: "paradev.hb.catalog-mutation.v1",
        status: "applied",
        code: "catalog.mutation.applied",
        database: "/tmp/PIHC3/.paradev/.cache/hb/catalog.sqlite"
      }
    };
    nativeBridgePayloadMock.mockResolvedValueOnce(payload);

    await expect(
      removeModule({
        projectRoot: "/tmp/PIHC3",
        moduleId: "modifier/starter_starter_modifier",
        sourceRoot: "src"
      })
    ).resolves.toEqual(payload);
  });

  it("renames modules through generated REST planning in the native web bridge", async () => {
    vi.stubGlobal("window", {});
    vi.stubEnv("VITE_PARADEV_NATIVE_BRIDGE_URL", "http://127.0.0.1:47831");
    const payload: ModuleRenamePayload = {
      schema: "paradev.module.rename.v1",
      project_id: "PIHC3",
      previous_module_id: "modifier/starter_starter_modifier",
      module_id: "modifier/starter_renamed_modifier",
      family: "modifier",
      previous_root: "/tmp/PIHC3/src/modules/modifier/starter_starter_modifier",
      root: "/tmp/PIHC3/src/modules/modifier/starter_renamed_modifier",
      previous_relative_path: "src/modules/modifier/starter_starter_modifier",
      relative_path: "src/modules/modifier/starter_renamed_modifier",
      content_rewritten: false,
      module: {},
      catalog_mutation: {
        schema: "paradev.hb.catalog-mutation.v1",
        status: "applied",
        code: "catalog.mutation.applied",
        database: "/tmp/PIHC3/.paradev/.cache/hb/catalog.sqlite"
      }
    };
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce({
        ok: true,
        status: 200,
        statusText: "OK",
        json: async () => ({
          schema: "paradev.sdk.frontend-api.rest-request.v1",
          operation_id: "module.rename",
          method: "PATCH",
          path: "/projects/modules/rename",
          query: {
            path: "/tmp/PIHC3",
            module_id: "modifier/starter_starter_modifier",
            object_id: "starter_renamed_modifier",
            title: "Friendly Modifier",
            source_root: "src"
          },
          body: {},
          binding: {
            method: "PATCH",
            path: "/projects/modules/rename",
            query: {}
          },
          normalized: {
            schema: "paradev.sdk.frontend-api.inputs.v1",
            operation_id: "module.rename",
            values: {},
            project: { path: "/tmp/PIHC3" },
            parameters: {},
            selectors: {},
            projections: {}
          }
        })
      })
      .mockResolvedValueOnce({
        ok: true,
        status: 200,
        statusText: "OK",
        json: async () => payload
      });
    vi.stubGlobal("fetch", fetchMock);

    await expect(
      renameModule({
        projectRoot: "/tmp/PIHC3",
        moduleId: "modifier/starter_starter_modifier",
        objectId: "starter_renamed_modifier",
        title: "Friendly Modifier",
        sourceRoot: "src"
      })
    ).resolves.toEqual(payload);

    expect(fetchMock).toHaveBeenNthCalledWith(1, "http://127.0.0.1:47831/frontend-api/rest-request?operation_id=module.rename", {
      body: JSON.stringify({
        path: "/tmp/PIHC3",
        module_id: "modifier/starter_starter_modifier",
        object_id: "starter_renamed_modifier",
        title: "Friendly Modifier",
        source_root: "src"
      }),
      headers: { "Content-Type": "application/json" },
      method: "POST"
    });
    expect(fetchMock).toHaveBeenNthCalledWith(
      2,
      "http://127.0.0.1:47831/projects/modules/rename?path=%2Ftmp%2FPIHC3&module_id=modifier%2Fstarter_starter_modifier&object_id=starter_renamed_modifier&title=Friendly+Modifier&source_root=src",
      {
        method: "PATCH"
      }
    );
    expect(fetchMock.mock.calls.map(([url]) => String(url))).not.toContain("http://127.0.0.1:47831/desktop/modules/rename");
  });

  it("removes modules through the existing generated REST operation in the native web bridge", async () => {
    vi.stubGlobal("window", {});
    vi.stubEnv("VITE_PARADEV_NATIVE_BRIDGE_URL", "http://127.0.0.1:47831");
    const payload: ModuleRemovePayload = {
      schema: "paradev.module.remove.v1",
      project_id: "PIHC3",
      module_id: "modifier/starter_starter_modifier",
      family: "modifier",
      source_root: "/tmp/PIHC3/src",
      root: "/tmp/PIHC3/src/modules/modifier/starter_starter_modifier",
      relative_path: "src/modules/modifier/starter_starter_modifier",
      blocked: false,
      removed: true,
      diagnostics: [],
      files: [],
      module: {},
      catalog_mutation: {
        schema: "paradev.hb.catalog-mutation.v1",
        status: "failed",
        code: "catalog.mutation.failed",
        database: "/tmp/PIHC3/.paradev/.cache/hb/catalog.sqlite",
        message: "catalog is locked"
      }
    };
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce({
        ok: true,
        status: 200,
        statusText: "OK",
        json: async () => ({
          schema: "paradev.sdk.frontend-api.rest-request.v1",
          operation_id: "module.remove",
          method: "DELETE",
          path: "/projects/modules/remove",
          query: {
            path: "/tmp/PIHC3",
            module_id: "modifier/starter_starter_modifier",
            source_root: "src",
            write: true
          },
          body: {},
          binding: {
            method: "DELETE",
            path: "/projects/modules/remove",
            query: {}
          },
          normalized: {
            schema: "paradev.sdk.frontend-api.inputs.v1",
            operation_id: "module.remove",
            values: {},
            project: { path: "/tmp/PIHC3" },
            parameters: {},
            selectors: {},
            projections: {}
          }
        })
      })
      .mockResolvedValueOnce({
        ok: true,
        status: 200,
        statusText: "OK",
        json: async () => payload
      });
    vi.stubGlobal("fetch", fetchMock);

    await expect(
      removeModule({
        projectRoot: "/tmp/PIHC3",
        moduleId: "modifier/starter_starter_modifier",
        sourceRoot: "src"
      })
    ).resolves.toEqual(payload);

    expect(fetchMock).toHaveBeenNthCalledWith(1, "http://127.0.0.1:47831/frontend-api/rest-request?operation_id=module.remove", {
      body: JSON.stringify({
        path: "/tmp/PIHC3",
        module_id: "modifier/starter_starter_modifier",
        source_root: "src",
        write: true
      }),
      headers: { "Content-Type": "application/json" },
      method: "POST"
    });
    expect(fetchMock).toHaveBeenNthCalledWith(
      2,
      "http://127.0.0.1:47831/projects/modules/remove?path=%2Ftmp%2FPIHC3&module_id=modifier%2Fstarter_starter_modifier&source_root=src&write=true",
      { method: "DELETE" }
    );
    expect(fetchMock.mock.calls.map(([url]) => String(url))).not.toContain("http://127.0.0.1:47831/desktop/modules/remove");
  });

  it.each([
    {
      boundary: "module draft",
      payload: {
        ...validModuleDraftResponse(),
        plan: {
          ...validModuleDraftResponse().plan,
          catalog_mutation: {
            schema: "paradev.hb.catalog-mutation.v1",
            status: "applied",
            code: "catalog.mutation.failed",
            database: "/tmp/catalog.sqlite"
          }
        }
      },
      request: () =>
        createModuleDraft({
          projectId: "PIHC3",
          projectRoot: "/tmp/PIHC3",
          familyId: "ideas",
          objectId: "IDEA_DEMO",
          values: {},
          write: true
        })
    },
    {
      boundary: "module rename",
      payload: {
        ...validModuleRenameResponse(),
        catalog_mutation: {
          schema: "paradev.hb.catalog-mutation.v1",
          status: "applied",
          code: "catalog.mutation.failed",
          database: "/tmp/catalog.sqlite"
        }
      },
      request: () => renameModule({ projectRoot: "/tmp/PIHC3", moduleId: "modifier/demo", objectId: "renamed" })
    },
    {
      boundary: "module remove",
      payload: {
        ...validModuleRemoveResponse(),
        catalog_mutation: {
          schema: "paradev.hb.catalog-mutation.v1",
          status: "applied",
          code: "catalog.mutation.failed",
          database: "/tmp/catalog.sqlite"
        }
      },
      request: () => removeModule({ projectRoot: "/tmp/PIHC3", moduleId: "modifier/demo" })
    }
  ])("preserves source success when $boundary has an invalid Catalog result", async ({ payload, request }) => {
    installNativeBridge();
    nativeBridgePayloadMock.mockResolvedValueOnce(payload);

    const result = await request();
    const mutation = "plan" in result ? result.plan.catalog_mutation : result.catalog_mutation;
    expect(mutation).toEqual(expect.objectContaining({
      schema: "paradev.desktop.catalog-mutation-unverified.v1",
      status: "unverified",
      code: "catalog.mutation.unverified"
    }));
  });

  it("preserves source success when an exact Catalog result has extra fields", async () => {
    installNativeBridge();
    nativeBridgePayloadMock.mockResolvedValueOnce({
      ...validModuleRemoveResponse(),
      catalog_mutation: {
        schema: "paradev.hb.catalog-mutation.v1",
        status: "applied",
        code: "catalog.mutation.applied",
        database: "/tmp/catalog.sqlite",
        message: "unexpected"
      }
    });

    await expect(removeModule({ projectRoot: "/tmp/PIHC3", moduleId: "modifier/demo" })).resolves.toEqual(
      expect.objectContaining({
        removed: true,
        catalog_mutation: expect.objectContaining({
          schema: "paradev.desktop.catalog-mutation-unverified.v1",
          status: "unverified",
          code: "catalog.mutation.unverified"
        })
      })
    );
  });

  it("preserves a pending removal cleanup while normalizing an invalid Catalog result", async () => {
    installNativeBridge();
    const cleanup = {
      schema: "paradev.module.remove-cleanup.v1",
      status: "pending",
      code: "module_remove.cleanup_pending",
      path: "/tmp/PIHC3/src/.paradev/module-trash/modifier-demo-a1b2c3",
      relative_path: "src/.paradev/module-trash/modifier-demo-a1b2c3",
      message: "The module was removed, but its quarantine copy is still pending cleanup."
    };
    nativeBridgePayloadMock.mockResolvedValueOnce({
      ...validModuleRemoveResponse(),
      diagnostics: [
        {
          severity: "warning",
          code: cleanup.code,
          path: cleanup.path,
          relative_path: cleanup.relative_path,
          message: cleanup.message
        }
      ],
      cleanup,
      catalog_mutation: {
        schema: "paradev.hb.catalog-mutation.v1",
        status: "applied",
        code: "catalog.mutation.failed",
        database: "/tmp/catalog.sqlite"
      }
    });

    await expect(removeModule({ projectRoot: "/tmp/PIHC3", moduleId: "modifier/demo", sourceRoot: "src" })).resolves.toEqual(
      expect.objectContaining({
        removed: true,
        cleanup,
        catalog_mutation: expect.objectContaining({
          schema: "paradev.desktop.catalog-mutation-unverified.v1",
          status: "unverified"
        })
      })
    );
  });

  it("rejects a removal cleanup outside the selected source-root quarantine", async () => {
    installNativeBridge();
    const cleanup = {
      schema: "paradev.module.remove-cleanup.v1",
      status: "pending",
      code: "module_remove.cleanup_pending",
      path: "/tmp/PIHC3/unrelated/modifier-demo-a1b2c3",
      relative_path: "unrelated/modifier-demo-a1b2c3",
      message: "Cleanup is pending."
    };
    nativeBridgePayloadMock.mockResolvedValueOnce({
      ...validModuleRemoveResponse(),
      diagnostics: [
        {
          severity: "warning",
          code: cleanup.code,
          path: cleanup.path,
          relative_path: cleanup.relative_path,
          message: cleanup.message
        }
      ],
      cleanup
    });

    await expect(removeModule({ projectRoot: "/tmp/PIHC3", moduleId: "modifier/demo" })).rejects.toThrow(
      "cleanup path is outside the source-root quarantine"
    );
  });

  it.each([
    {
      boundary: "module draft",
      payload: { ...validModuleDraftResponse(), schema: "paradev.rest.module_draft.v2" },
      request: () =>
        createModuleDraft({
          projectId: "PIHC3",
          projectRoot: "/tmp/PIHC3",
          familyId: "ideas",
          objectId: "IDEA_DEMO",
          values: {},
          write: true
        }),
      message: "module draft response has an unsupported schema"
    },
    {
      boundary: "module rename",
      payload: { ...validModuleRenameResponse(), content_rewritten: "false" },
      request: () => renameModule({ projectRoot: "/tmp/PIHC3", moduleId: "modifier/demo", objectId: "renamed" }),
      message: "module rename response requires a boolean content_rewritten"
    },
    {
      boundary: "module remove",
      payload: { removed: true },
      request: () => removeModule({ projectRoot: "/tmp/PIHC3", moduleId: "modifier/demo" }),
      message: "module remove response has an unsupported schema"
    }
  ])("rejects malformed parent payloads at the $boundary boundary", async ({ payload, request, message }) => {
    installNativeBridge();
    nativeBridgePayloadMock.mockResolvedValueOnce(payload);

    await expect(request()).rejects.toThrow(message);
  });

  it.each([
    {
      boundary: "module draft",
      payload: {
        ...validModuleDraftResponse(),
        project_id: "OTHER",
        plan: { ...validModuleDraftResponse().plan, project_id: "OTHER" }
      },
      request: () =>
        createModuleDraft({
          projectId: "PIHC3",
          projectRoot: "/tmp/PIHC3",
          familyId: "ideas",
          objectId: "IDEA_DEMO",
          values: {},
          write: true
        })
    },
    {
      boundary: "module rename",
      payload: { ...validModuleRenameResponse(), previous_module_id: "modifier/other" },
      request: () => renameModule({ projectRoot: "/tmp/PIHC3", moduleId: "modifier/demo", objectId: "renamed" })
    },
    {
      boundary: "module remove",
      payload: { ...validModuleRemoveResponse(), module_id: "modifier/other" },
      request: () => removeModule({ projectRoot: "/tmp/PIHC3", moduleId: "modifier/demo" })
    }
  ])("rejects a $boundary payload for a different requested target", async ({ payload, request }) => {
    installNativeBridge();
    nativeBridgePayloadMock.mockResolvedValueOnce(payload);

    await expect(request()).rejects.toThrow("identity does not match the request");
  });

  it("rejects a module draft that claims a write the request did not authorize", async () => {
    installNativeBridge();
    nativeBridgePayloadMock.mockResolvedValueOnce(validModuleDraftResponse());

    await expect(
      createModuleDraft({
        projectId: "PIHC3",
        projectRoot: "/tmp/PIHC3",
        familyId: "ideas",
        objectId: "IDEA_DEMO",
        values: {},
        write: false
      })
    ).rejects.toThrow("write result does not match the request");
  });

  it("rejects a module draft that omits an authorized unblocked write", async () => {
    installNativeBridge();
    const value = validModuleDraftResponse();
    const { catalog_mutation: _catalogMutation, ...plan } = value.plan;
    void _catalogMutation;
    nativeBridgePayloadMock.mockResolvedValueOnce({ ...value, plan: { ...plan, written: false } });

    await expect(
      createModuleDraft({
        projectId: "PIHC3",
        projectRoot: "/tmp/PIHC3",
        familyId: "ideas",
        objectId: "IDEA_DEMO",
        values: {},
        write: true
      })
    ).rejects.toThrow("write result does not match the request");
  });

  it("rejects a module draft that claims an unauthorized overwrite", async () => {
    installNativeBridge();
    nativeBridgePayloadMock.mockResolvedValueOnce({
      ...validModuleDraftResponse(),
      plan: {
        ...validModuleDraftResponse().plan,
        files: [
          {
            path: "/tmp/PIHC3/src/modules/idea/IDEA_DEMO/def.txt",
            relative_path: "src/modules/idea/IDEA_DEMO/def.txt",
            module_path: "def.txt",
            action: "overwrite"
          }
        ]
      }
    });

    await expect(
      createModuleDraft({
        projectId: "PIHC3",
        projectRoot: "/tmp/PIHC3",
        familyId: "ideas",
        objectId: "IDEA_DEMO",
        values: {},
        write: true,
        force: false
      })
    ).rejects.toThrow("cannot claim an overwrite that the request did not authorize");
  });

  it("rejects an exists action when force requested overwrite planning", async () => {
    installNativeBridge();
    const value = validModuleDraftResponse();
    const { catalog_mutation: _catalogMutation, ...plan } = value.plan;
    void _catalogMutation;
    nativeBridgePayloadMock.mockResolvedValueOnce({
      ...value,
      plan: {
        ...plan,
        blocked: true,
        written: false,
        files: [
          {
            path: "/tmp/PIHC3/src/modules/idea/IDEA_DEMO/def.txt",
            relative_path: "src/modules/idea/IDEA_DEMO/def.txt",
            module_path: "def.txt",
            action: "exists"
          }
        ]
      }
    });

    await expect(
      createModuleDraft({
        projectId: "PIHC3",
        projectRoot: "/tmp/PIHC3",
        familyId: "ideas",
        objectId: "IDEA_DEMO",
        values: {},
        write: true,
        force: true
      })
    ).rejects.toThrow("file action does not match the requested force behavior");
  });

  it("accepts the blocked file action emitted by an unsafe scaffold plan", async () => {
    installNativeBridge();
    const value = validModuleDraftResponse();
    const { catalog_mutation: _catalogMutation, ...plan } = value.plan;
    void _catalogMutation;
    const payload = {
      ...value,
      plan: {
        ...plan,
        blocked: true,
        written: false,
        diagnostics: [{ code: "scaffold.path_symlink", severity: "error" }],
        files: [
          {
            path: "/tmp/PIHC3/src/modules/idea/IDEA_DEMO/def.txt",
            relative_path: "src/modules/idea/IDEA_DEMO/def.txt",
            module_path: "def.txt",
            action: "blocked"
          }
        ]
      }
    };
    nativeBridgePayloadMock.mockResolvedValueOnce(payload);

    await expect(
      createModuleDraft({
        projectId: "PIHC3",
        projectRoot: "/tmp/PIHC3",
        familyId: "ideas",
        objectId: "IDEA_DEMO",
        values: {},
        write: true
      })
    ).resolves.toEqual(payload);
  });

  it("accepts a titled scaffold root while keeping the logical module id", async () => {
    installNativeBridge();
    const folderName = "IDEA_DEMO - Demo Idea";
    const payload = {
      ...validModuleDraftResponse(),
      plan: {
        ...validModuleDraftResponse().plan,
        root: `/tmp/PIHC3/src/modules/idea/${folderName}`,
        folder_name: folderName,
        files: [
          {
            path: `/tmp/PIHC3/src/modules/idea/${folderName}/def.txt`,
            relative_path: `src/modules/idea/${folderName}/def.txt`,
            module_path: "def.txt",
            action: "create"
          }
        ]
      }
    };
    nativeBridgePayloadMock.mockResolvedValueOnce(payload);

    await expect(
      createModuleDraft({
        projectId: "PIHC3",
        projectRoot: "/tmp/PIHC3",
        familyId: "ideas",
        objectId: "IDEA_DEMO",
        values: {},
        write: true
      })
    ).resolves.toEqual(payload);
  });

  it.each([
    {
      case: "non-canonical draft id",
      payload: { ...validModuleDraftResponse(), draft_id: "ideas/IDEA_DEMO" },
      message: "module identity is inconsistent"
    },
    {
      case: "non-string scaffold value",
      payload: {
        ...validModuleDraftResponse(),
        plan: { ...validModuleDraftResponse().plan, values: { title: 42 } }
      },
      message: "requires string values in values"
    },
    {
      case: "file outside its module root",
      payload: {
        ...validModuleDraftResponse(),
        plan: {
          ...validModuleDraftResponse().plan,
          files: [
            {
              path: "/tmp/PIHC3/src/modules/idea/other/def.txt",
              relative_path: "src/modules/idea/other/def.txt",
              module_path: "def.txt",
              action: "create"
            }
          ]
        }
      },
      message: "path is outside the module root"
    },
    {
      case: "non-string scaffold file action",
      payload: {
        ...validModuleDraftResponse(),
        plan: {
          ...validModuleDraftResponse().plan,
          files: [
            {
              path: "/tmp/PIHC3/src/modules/idea/IDEA_DEMO/def.txt",
              relative_path: "src/modules/idea/IDEA_DEMO/def.txt",
              module_path: "def.txt",
              action: 7
            }
          ]
        }
      },
      message: "requires a non-empty action"
    },
    {
      case: "mismatched source root",
      payload: {
        ...validModuleDraftResponse(),
        plan: { ...validModuleDraftResponse().plan, source_root: "/tmp/PIHC3/imports" }
      },
      message: "root does not match its source_root"
    },
    {
      case: "titled root with a different logical prefix",
      payload: {
        ...validModuleDraftResponse(),
        plan: {
          ...validModuleDraftResponse().plan,
          root: "/tmp/PIHC3/src/modules/idea/OTHER - Demo Idea"
        }
      },
      message: "is not the canonical module root"
    },
    {
      case: "titled root without a title",
      payload: {
        ...validModuleDraftResponse(),
        plan: {
          ...validModuleDraftResponse().plan,
          root: "/tmp/PIHC3/src/modules/idea/IDEA_DEMO - "
        }
      },
      message: "is not the canonical module root"
    },
    {
      case: "folder name that differs from the returned root",
      payload: {
        ...validModuleDraftResponse(),
        plan: {
          ...validModuleDraftResponse().plan,
          folder_name: "IDEA_DEMO - Different"
        }
      },
      message: "folder_name does not match its root"
    }
  ])("rejects a module draft with a $case", async ({ payload, message }) => {
    installNativeBridge();
    nativeBridgePayloadMock.mockResolvedValueOnce(payload);

    await expect(
      createModuleDraft({
        projectId: "PIHC3",
        projectRoot: "/tmp/PIHC3",
        familyId: "ideas",
        objectId: "IDEA_DEMO",
        values: {},
        write: true
      })
    ).rejects.toThrow(message);
  });

  it("accepts a typed scaffold file when force authorizes its overwrite", async () => {
    installNativeBridge();
    const payload = {
      ...validModuleDraftResponse(),
      plan: {
        ...validModuleDraftResponse().plan,
        values: { object_id: "IDEA_DEMO", title: "Demo idea" },
        files: [
          {
            path: "/tmp/PIHC3/src/modules/idea/IDEA_DEMO/def.txt",
            relative_path: "src/modules/idea/IDEA_DEMO/def.txt",
            module_path: "def.txt",
            action: "overwrite"
          }
        ]
      }
    };
    nativeBridgePayloadMock.mockResolvedValueOnce(payload);

    await expect(
      createModuleDraft({
        projectId: "PIHC3",
        projectRoot: "/tmp/PIHC3",
        familyId: "ideas",
        objectId: "IDEA_DEMO",
        values: {},
        write: true,
        force: true
      })
    ).resolves.toEqual(payload);
  });

  it.each([
    {
      boundary: "rename with different old and new source roots",
      payload: {
        ...validModuleRenameResponse(),
        root: "/tmp/PIHC3/imports/modules/modifier/renamed",
        relative_path: "imports/modules/modifier/renamed"
      },
      request: () => renameModule({ projectRoot: "/tmp/PIHC3", moduleId: "modifier/demo", objectId: "renamed" }),
      message: "old and new roots use different source roots"
    },
    {
      boundary: "rename with a mismatched requested source root",
      payload: validModuleRenameResponse(),
      request: () =>
        renameModule({
          projectRoot: "/tmp/PIHC3",
          moduleId: "modifier/demo",
          objectId: "renamed",
          sourceRoot: "imports"
        }),
      message: "source_root identity does not match the request"
    },
    {
      boundary: "rename with a titled target for another logical module",
      payload: {
        ...validModuleRenameResponse(),
        root: "/tmp/PIHC3/src/modules/modifier/other - Demo Modifier",
        relative_path: "src/modules/modifier/other - Demo Modifier"
      },
      request: () =>
        renameModule({
          projectRoot: "/tmp/PIHC3",
          moduleId: "modifier/demo",
          objectId: "renamed"
        }),
      message: "is not the canonical module root"
    },
    {
      boundary: "remove with a mismatched source root",
      payload: { ...validModuleRemoveResponse(), source_root: "/tmp/PIHC3/imports" },
      request: () => removeModule({ projectRoot: "/tmp/PIHC3", moduleId: "modifier/demo" }),
      message: "root does not match its source_root"
    },
    {
      boundary: "remove with an unrelated relative path",
      payload: { ...validModuleRemoveResponse(), relative_path: "src/modules/modifier/other" },
      request: () => removeModule({ projectRoot: "/tmp/PIHC3", moduleId: "modifier/demo" }),
      message: "relative_path does not identify its target root"
    }
  ])("rejects a $boundary", async ({ payload, request, message }) => {
    installNativeBridge();
    nativeBridgePayloadMock.mockResolvedValueOnce(payload);

    await expect(request()).rejects.toThrow(message);
  });

  it("accepts titled rename roots and a normalized requested source root", async () => {
    installNativeBridge();
    const payload = {
      ...validModuleRenameResponse(),
      previous_root: "/tmp/PIHC3/src/modules/modifier/demo - Demo Modifier",
      previous_relative_path: "src/modules/modifier/demo - Demo Modifier",
      root: "/tmp/PIHC3/src/modules/modifier/renamed - Demo Modifier",
      relative_path: "src/modules/modifier/renamed - Demo Modifier"
    };
    nativeBridgePayloadMock.mockResolvedValueOnce(payload);

    await expect(
      renameModule({
        projectRoot: "/tmp/PIHC3",
        moduleId: "modifier/demo",
        objectId: "renamed",
        sourceRoot: "./imports/../src/"
      })
    ).resolves.toEqual(payload);
  });

  it("accepts a project-relative external source root and its absolute relative_path payload", async () => {
    installNativeBridge();
    const payload = {
      ...validModuleRemoveResponse(),
      source_root: "/tmp/shared",
      root: "/tmp/shared/modules/modifier/demo",
      relative_path: "/tmp/shared/modules/modifier/demo"
    };
    nativeBridgePayloadMock.mockResolvedValueOnce(payload);

    await expect(
      removeModule({
        projectRoot: "/tmp/PIHC3",
        moduleId: "modifier/demo",
        sourceRoot: "src/../../shared"
      })
    ).resolves.toEqual(payload);
  });

  it("keeps UNC traversal anchored at the requested server share", async () => {
    installNativeBridge();
    const payload = {
      ...validModuleRemoveResponse(),
      source_root: "\\\\server\\share\\src",
      root: "\\\\server\\share\\src\\modules\\modifier\\demo",
      relative_path: "\\\\server\\share\\src\\modules\\modifier\\demo"
    };
    nativeBridgePayloadMock.mockResolvedValueOnce(payload);

    await expect(
      removeModule({
        projectRoot: "\\\\server\\share\\project",
        moduleId: "modifier/demo",
        sourceRoot: "..\\..\\src"
      })
    ).resolves.toEqual(payload);
  });

  it.each([
    {
      boundary: "written module draft",
      payload: (() => {
        const value = validModuleDraftResponse();
        const { catalog_mutation: _catalogMutation, ...plan } = value.plan;
        void _catalogMutation;
        return { ...value, plan };
      })(),
      request: () =>
        createModuleDraft({
          projectId: "PIHC3",
          projectRoot: "/tmp/PIHC3",
          familyId: "ideas",
          objectId: "IDEA_DEMO",
          values: {},
          write: true
        })
    },
    {
      boundary: "module rename",
      payload: (() => {
        const { catalog_mutation: _catalogMutation, ...value } = validModuleRenameResponse();
        void _catalogMutation;
        return value;
      })(),
      request: () => renameModule({ projectRoot: "/tmp/PIHC3", moduleId: "modifier/demo", objectId: "renamed" })
    },
    {
      boundary: "removed module",
      payload: (() => {
        const { catalog_mutation: _catalogMutation, ...value } = validModuleRemoveResponse();
        void _catalogMutation;
        return value;
      })(),
      request: () => removeModule({ projectRoot: "/tmp/PIHC3", moduleId: "modifier/demo" })
    }
  ])("preserves successful $boundary payloads with an unverified Catalog result", async ({ payload, request }) => {
    installNativeBridge();
    nativeBridgePayloadMock.mockResolvedValueOnce(payload);

    const result = await request();
    const mutation = "plan" in result ? result.plan.catalog_mutation : result.catalog_mutation;
    expect(mutation).toEqual(expect.objectContaining({
      schema: "paradev.desktop.catalog-mutation-unverified.v1",
      status: "unverified",
      code: "catalog.mutation.unverified"
    }));
  });

  it("preserves source success when Catalog synchronization has a blank failure message", async () => {
    installNativeBridge();
    nativeBridgePayloadMock.mockResolvedValueOnce({
      ...validModuleRemoveResponse(),
      catalog_mutation: {
        schema: "paradev.hb.catalog-mutation.v1",
        status: "failed",
        code: "catalog.mutation.failed",
        database: "/tmp/catalog.sqlite",
        message: "   "
      }
    });

    await expect(removeModule({ projectRoot: "/tmp/PIHC3", moduleId: "modifier/demo" })).resolves.toEqual(
      expect.objectContaining({
        removed: true,
        catalog_mutation: expect.objectContaining({
          schema: "paradev.desktop.catalog-mutation-unverified.v1",
          status: "unverified",
          code: "catalog.mutation.unverified"
        })
      })
    );
  });

  it.each([
    {
      boundary: "dry module draft",
      payload: {
        ...validModuleDraftResponse(),
        plan: { ...validModuleDraftResponse().plan, written: false }
      },
      request: () =>
        createModuleDraft({
          projectId: "PIHC3",
          projectRoot: "/tmp/PIHC3",
          familyId: "ideas",
          objectId: "IDEA_DEMO",
          values: {},
          write: false
        })
    },
    {
      boundary: "blocked module draft",
      payload: {
        ...validModuleDraftResponse(),
        plan: { ...validModuleDraftResponse().plan, blocked: true, written: false }
      },
      request: () =>
        createModuleDraft({
          projectId: "PIHC3",
          projectRoot: "/tmp/PIHC3",
          familyId: "ideas",
          objectId: "IDEA_DEMO",
          values: {},
          write: true
        })
    },
    {
      boundary: "dry module removal",
      payload: { ...validModuleRemoveResponse(), removed: false },
      request: () => removeModule({ projectRoot: "/tmp/PIHC3", moduleId: "modifier/demo" })
    },
    {
      boundary: "blocked module removal",
      payload: { ...validModuleRemoveResponse(), blocked: true, removed: false },
      request: () => removeModule({ projectRoot: "/tmp/PIHC3", moduleId: "modifier/demo" })
    }
  ])("rejects impossible Catalog status on a $boundary response", async ({ payload, request }) => {
    installNativeBridge();
    nativeBridgePayloadMock.mockResolvedValueOnce(payload);

    await expect(request()).rejects.toThrow("must omit catalog_mutation when the source operation did not complete");
  });

  it("keeps image conversion fields camelCase through the native web bridge", async () => {
    installNativeBridge();
    const payload = {
      schema: "paradev.rest.draft_apply.v1",
      project_id: "PIHC3",
      written: true,
      files: []
    };
    nativeBridgePayloadMock.mockResolvedValueOnce(payload);

    await expect(
      applyProjectDraft({
        projectId: "PIHC3",
        projectRoot: "/tmp/PIHC3",
        sourceReplacements: [{
          path: "src/gfx/interface/ideas/GFX_idea_beta.dds",
          contentBase64: "iVBORw0KGgo=",
          contentFormat: "png",
          targetFormat: "dds",
          expectedSize: 128,
          expectedMtimeNs: "1700000000000000000"
        }]
      })
    ).resolves.toEqual(payload);

  });

  it("derives only the trusted project-owned source recovery directory from recovery errors", () => {
    expect(
      sourceDraftRecoveryPathFromError(
        new Error(
          "Source draft crash recovery stopped because a file changed outside ParaDev.",
        ),
        "/workspace/projects/PIHC3",
      ),
    ).toBe(
      "/workspace/projects/PIHC3/.paradev/source-draft-transaction",
    );
    expect(
      sourceDraftRecoveryPathFromError(
        "Source draft transaction failed and rollback was incomplete; recovery data remains.",
        String.raw`C:\Projects\PIHC3`,
      ),
    ).toBe(
      "C:/Projects/PIHC3/.paradev/source-draft-transaction",
    );
    expect(
      sourceDraftRecoveryPathFromError(
        new Error("meta.yaml: invalid YAML"),
        "/workspace/projects/PIHC3",
      ),
    ).toBeNull();
    expect(
      sourceDraftRecoveryPathFromError(
        new Error("Source draft recovery data is incomplete."),
        "../untrusted",
      ),
    ).toBeNull();
  });

  it("projects the current source draft through the dedicated native web bridge", async () => {
    installNativeBridge();
    const payload = validSourceFormPayload();
    nativeBridgePayloadMock.mockResolvedValueOnce(payload);
    const text = '  {"mesh":{"scale":4.25}}\n';

    await expect(
      readProjectSourceForm({
        projectId: " PIHC3 ",
        projectRoot: " /tmp/PIHC3 ",
        sourcePath: "src/modules/Entity/VIENTO_MIRROR/record.json",
        text
      })
    ).resolves.toEqual(payload);

  });

  it("plans guided control intent through the strict native update-batch bridge", async () => {
    installNativeBridge();
    nativeBridgePayloadMock.mockResolvedValueOnce(validSourceFormUpdateBatchPayload());
    const request = {
      projectId: " PIHC3 ",
      projectRoot: " /tmp/PIHC3 ",
      updates: [
        {
          sourcePath: "src/modules/Entity/VIENTO_MIRROR/record.json",
          text: '{"mesh":{"scale":4.25}}\n',
          values: { "mesh.scale": 4.5 }
        }
      ]
    };

    await expect(planProjectSourceFormUpdates(request)).resolves.toMatchObject({
      schema: "paradev.source-form-update-batch.v1",
      projectId: "PIHC3",
      changed: true,
      sourceEdits: [
        {
          path: "/tmp/PIHC3/src/modules/Entity/VIENTO_MIRROR/record.json",
          text: '{"mesh":{"scale":4.5}}\n',
          expectedSize: 24,
          expectedMtimeNs: "1770000000123456789"
        }
      ]
    });
  });

  it("rejects a guided update plan whose batch edits diverge from its per-source plans", async () => {
    installNativeBridge();
    const payload = validSourceFormUpdateBatchPayload();
    nativeBridgePayloadMock.mockResolvedValueOnce({
      ...payload,
      source_edits: [
        {
          ...(payload.source_edits as Array<Record<string, unknown>>)[0],
          text: "different\n"
        }
      ]
    });

    await expect(
      planProjectSourceFormUpdates({
        projectId: "PIHC3",
        projectRoot: "/tmp/PIHC3",
        updates: [
          {
            sourcePath: "src/modules/Entity/VIENTO_MIRROR/record.json",
            values: { "mesh.scale": 4.5 }
          }
        ]
      })
    ).rejects.toThrow("source_edits do not match");
  });

  it("validates exact-span PDX source forms through the same bridge", async () => {
    installNativeBridge();
    const payload = validPdxSourceFormPayload();
    nativeBridgePayloadMock.mockResolvedValueOnce(payload);

    await expect(
      readProjectSourceForm({
        projectId: "PIHC3",
        projectRoot: "/tmp/PIHC3",
        sourcePath: "src/modules/idea/IDEA_TEST/def.txt",
        text: "active = yes\n"
      })
    ).resolves.toEqual(payload);
  });

  it("accepts an empty bounded PDX search result and preserves its normalized query", async () => {
    installNativeBridge();
    const query = "C01_C02_GREENLIGHT.40";
    const payload: SourceFormPayload = {
      ...validPdxSourceFormPayload(),
      query,
      coverage: { truncated: false, shown_controls: 0, total_controls: 0 },
      sections: []
    };
    nativeBridgePayloadMock.mockResolvedValueOnce(payload);

    await expect(
      readProjectSourceForm({
        projectId: "PIHC3",
        projectRoot: "/tmp/PIHC3",
        sourcePath: "src/modules/idea/IDEA_TEST/def.txt",
        text: "active = yes\n",
        query: `  ${query}  `
      })
    ).resolves.toEqual(payload);
  });

  it("validates Registry-declared PDX integer-list forms through the same bridge", async () => {
    installNativeBridge();
    const payload = validPdxIntegerListSourceFormPayload();
    nativeBridgePayloadMock.mockResolvedValueOnce(payload);

    await expect(
      readProjectSourceForm({
        projectId: "PIHC3",
        projectRoot: "/tmp/PIHC3",
        sourcePath: "src/modules/state/199/def.txt",
        text: "provinces = { 345 1637 }\n"
      })
    ).resolves.toEqual(payload);
  });

  it("validates Registry-declared PDX block-body forms through the same bridge", async () => {
    installNativeBridge();
    const payload = validPdxBlockBodySourceFormPayload();
    nativeBridgePayloadMock.mockResolvedValueOnce(payload);

    await expect(
      readProjectSourceForm({
        projectId: "PIHC3",
        projectRoot: "/tmp/PIHC3",
        sourcePath: "src/modules/scripted_effect/MY_EFFECT/def.txt",
        text: "MY_EFFECT = {\n    add_power = 5\n}\n"
      })
    ).resolves.toEqual(payload);
  });

  it("rejects malformed Registry-declared PDX integer-list rows", async () => {
    installNativeBridge();
    const payload = validPdxIntegerListSourceFormPayload();
    const malformed = structuredClone(payload);
    const control = malformed.sections[0]?.controls?.[0];
    if (!control || control.control !== "text" || control.patch.op !== "replace-pdx-integer-list") {
      throw new Error("Missing PDX integer-list source-form fixture.");
    }
    control.patch.columns = 2;
    control.patch.expected = " 345 1637 5 ";
    control.patch.span.end = control.patch.expected.length;
    control.patch.source_length = control.patch.expected.length;
    nativeBridgePayloadMock.mockResolvedValueOnce(malformed);

    await expect(
      readProjectSourceForm({
        projectId: "PIHC3",
        projectRoot: "/tmp/PIHC3",
        sourcePath: "src/modules/state/199/def.txt",
        text: "provinces = { 345 1637 5 }\n"
      })
    ).rejects.toThrow("exactly 2 integers per row");
  });

  it("validates exact-span localization forms through the same bridge", async () => {
    installNativeBridge();
    const payload = validLocSourceFormPayload();
    nativeBridgePayloadMock.mockResolvedValueOnce(payload);

    await expect(
      readProjectSourceForm({
        projectId: "PIHC3",
        projectRoot: "/tmp/PIHC3",
        sourcePath: "src/modules/idea/IDEA_TEST/main.loc",
        text: "[en.IDEA_TEST]\nOld title\n"
      })
    ).resolves.toEqual(payload);
  });

  it("rejects malformed localization patch spans and control layout", async () => {
    installNativeBridge();
    const payload = validLocSourceFormPayload();
    const malformed = structuredClone(payload);
    const control = malformed.sections[0]?.controls?.[0];
    if (!control || control.control !== "text" || control.patch.op !== "replace-loc-text") {
      throw new Error("Missing localization source-form fixture.");
    }
    control.patch.span.end += 1;
    nativeBridgePayloadMock.mockResolvedValueOnce(malformed);

    await expect(
      readProjectSourceForm({
        projectId: "PIHC3",
        projectRoot: "/tmp/PIHC3",
        sourcePath: "src/modules/idea/IDEA_TEST/main.loc",
        text: "[en.IDEA_TEST]\nOld title\n"
      })
    ).rejects.toThrow("span length must match expected");
  });

  it("rejects contradictory partial PDX form coverage", async () => {
    installNativeBridge();
    const payload = validPdxSourceFormPayload();
    nativeBridgePayloadMock.mockResolvedValueOnce({
      ...payload,
      coverage: { truncated: false, shown_controls: 1, total_controls: 104 }
    });

    await expect(
      readProjectSourceForm({
        projectId: "PIHC3",
        projectRoot: "/tmp/PIHC3",
        sourcePath: "src/modules/idea/IDEA_TEST/def.txt",
        text: "active = yes\n"
      })
    ).rejects.toThrow("coverage truncated flag is inconsistent");
  });

  it("preserves an unsupported source-form null response", async () => {
    installNativeBridge();
    nativeBridgePayloadMock.mockResolvedValueOnce(null);

    await expect(
      readProjectSourceForm({
        projectId: "PIHC3",
        projectRoot: "/tmp/PIHC3",
        sourcePath: "src/modules/idea/DEMO/def.txt",
        text: "ideas = {}\n"
      })
    ).resolves.toBeNull();
  });

  it("accepts an absolute requested source path matching the response path", async () => {
    installNativeBridge();
    const payload = validSourceFormPayload();
    nativeBridgePayloadMock.mockResolvedValueOnce(payload);

    await expect(
      readProjectSourceForm({
        projectId: "PIHC3",
        projectRoot: "/tmp/PIHC3",
        sourcePath: payload.path,
        text: "{}\n"
      })
    ).resolves.toEqual(payload);
  });

  it.each([
    {
      boundary: "schema",
      payload: { ...validSourceFormPayload(), schema: "paradev.source-form.v2" },
      message: "unsupported schema"
    },
    {
      boundary: "project identity",
      payload: { ...validSourceFormPayload(), project_id: "OTHER" },
      message: "project identity"
    },
    {
      boundary: "source identity",
      payload: {
        ...validSourceFormPayload(),
        path: "/tmp/PIHC3/src/modules/Entity/OTHER/record.json",
        relative_path: "src/modules/Entity/OTHER/record.json"
      },
      message: "source identity"
    },
    {
      boundary: "project containment",
      payload: { ...validSourceFormPayload(), path: "/tmp/OTHER/src/modules/Entity/VIENTO_MIRROR/record.json" },
      message: "outside the requested project"
    },
    {
      boundary: "form structure",
      payload: { ...validSourceFormPayload(), sections: [{ id: "empty", label: "Empty" }] },
      message: "must contain controls or nested sections"
    },
    {
      boundary: "unknown fields",
      payload: { ...validSourceFormPayload(), future_contract: true },
      message: "unsupported fields"
    },
    {
      boundary: "duplicate choices",
      payload: {
        ...validSourceFormPayload(),
        sections: [
          {
            id: "states",
            label: "States",
            controls: [
              {
                id: "state.next",
                label: "Next state",
                control: "choice",
                value: "idle",
                patch: { op: "replace-json-scalar", path: ["entities", 0, "state", "next_state"] },
                choices: [
                  { label: "Idle", value: "idle" },
                  { label: "Idle again", value: "idle" }
                ]
              }
            ]
          }
        ]
      },
      message: "must not repeat values"
    },
    {
      boundary: "mixed choice scalar kinds",
      payload: {
        ...validSourceFormPayload(),
        sections: [
          {
            id: "states",
            label: "States",
            controls: [
              {
                id: "state.next",
                label: "Next state",
                control: "choice",
                value: "idle",
                patch: { op: "replace-json-scalar", path: ["entities", 0, "state", "next_state"] },
                choices: [
                  { label: "Idle", value: "idle" },
                  { label: "Disabled", value: false }
                ]
              }
            ]
          }
        ]
      },
      message: "same JSON scalar kind"
    }
  ])("rejects a malformed project source form at the $boundary boundary", async ({ payload, message }) => {
    installNativeBridge();
    nativeBridgePayloadMock.mockResolvedValueOnce(payload);

    await expect(
      readProjectSourceForm({
        projectId: "PIHC3",
        projectRoot: "/tmp/PIHC3",
        sourcePath: "src/modules/Entity/VIENTO_MIRROR/record.json",
        text: "{}\n"
      })
    ).rejects.toThrow(message);
  });

  it("validates collection localization targets through the native web bridge", async () => {
    installNativeBridge();
    const workspace = validCollectionLocalizationWorkspacePayload();
    const operation = {
      op: "set" as const,
      language: "en",
      key: "DECISION_CATEGORY_TEST",
      value: "Updated category"
    };
    const update = {
      schema: "paradev.localization-update-plan.v2",
      project_id: "PIHC3",
      target: workspace.target,
      source_root: "/tmp/PIHC3/src",
      operation: {
        ...operation,
        language: "l_english"
      },
      changed: true,
      changes: [],
      source_edits: [{
        path: (workspace.sources as Array<Record<string, unknown>>)[0].path,
        text: "[en.DECISION_CATEGORY_TEST]\nUpdated category\n",
        expected_size: 52,
        expected_mtime_ns: "1700000000000000000"
      }],
      workspace
    };
    nativeBridgePayloadMock
      .mockResolvedValueOnce(workspace)
      .mockResolvedValueOnce(update);
    const request = {
      projectId: "PIHC3",
      projectRoot: "/tmp/PIHC3",
      targetKind: "collection" as const,
      targetId: "DECISION_CATEGORY_TEST",
      family: "decision"
    };

    await expect(readProjectLocalizationWorkspace(request)).resolves.toMatchObject({
      target: workspace.target
    });
    await expect(planProjectLocalizationUpdate({ ...request, operation })).resolves.toMatchObject({
      target: workspace.target,
      changed: true
    });

  });

  it("applies project drafts through generated REST planning in the native web bridge", async () => {
    vi.stubGlobal("window", {});
    vi.stubEnv("VITE_PARADEV_NATIVE_BRIDGE_URL", "http://127.0.0.1:47831");
    const payload = {
      schema: "paradev.rest.draft_apply.v1",
      project_id: "PIHC3",
      written: true,
      files: [
        {
          path: "/tmp/PIHC3/src/common/ideas/GER_demo.txt",
          relative_path: "src/common/ideas/GER_demo.txt",
          operation: "write_text",
          encoding: "utf-8"
        }
      ]
    };
    const sourceEdits = [{
      path: "src/common/ideas/GER_demo.txt",
      text: "ideas = {}\n",
      expectedSize: 11,
      expectedMtimeNs: "1700000000000000000"
    }];
    const sourceEditValues = [{
      path: "src/common/ideas/GER_demo.txt",
      text: "ideas = {}\n",
      expected_size: 11,
      expected_mtime_ns: "1700000000000000000"
    }];
    const sourceRemovals = [{
      path: "src/common/ideas/old_demo.txt",
      expectedSize: 42,
      expectedMtimeNs: "1700000000000000002"
    }];
    const sourceRemovalValues = [{
      path: "src/common/ideas/old_demo.txt",
      expected_size: 42,
      expected_mtime_ns: "1700000000000000002"
    }];
    const sourceReplacements = [
      {
        path: "src/gfx/interface/ideas/GER_demo.png",
        content_base64: "iVBORw0KGgo=",
        expected_size: 128,
        expected_mtime_ns: "1700000000000000001"
      },
      {
        path: "src/gfx/interface/ideas/GFX_idea_beta.dds",
        content_base64: "iVBORw0KGgo=",
        content_format: "png",
        target_format: "dds",
        expected_absent: true
      }
    ];
    const moduleRename = {
      module_id: "idea/IDEA_ALPHA",
      object_id: "IDEA_ALPHA",
      source_root: "/tmp/PIHC3/src",
      title: "Readable Alpha"
    };
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce({
        ok: true,
        status: 200,
        statusText: "OK",
        json: async () => ({
          schema: "paradev.sdk.frontend-api.rest-request.v1",
          operation_id: "project.draft_apply",
          method: "POST",
          path: "/projects/PIHC3/drafts/apply",
          query: {},
          body: {
            project_root: "/tmp/PIHC3",
            source_edits: sourceEditValues,
            source_removals: sourceRemovalValues,
            source_replacements: sourceReplacements,
            module_rename: moduleRename
          },
          binding: {
            method: "POST",
            path: "/projects/{project_id}/drafts/apply",
            query: {}
          },
          normalized: {
            schema: "paradev.sdk.frontend-api.inputs.v1",
            operation_id: "project.draft_apply",
            values: {},
            project: { path: "/tmp/PIHC3" },
            parameters: {
              source_edits: sourceEditValues,
              source_removals: sourceRemovalValues,
              source_replacements: sourceReplacements,
              module_rename: moduleRename
            },
            selectors: {},
            projections: {}
          }
        })
      })
      .mockResolvedValueOnce({
        ok: true,
        status: 200,
        statusText: "OK",
        json: async () => payload
      });
    vi.stubGlobal("fetch", fetchMock);

    await expect(
      applyProjectDraft({
        projectId: "PIHC3",
        projectRoot: "/tmp/PIHC3",
        sourceEdits,
        sourceRemovals,
        sourceReplacements: [
          {
            path: "src/gfx/interface/ideas/GER_demo.png",
            contentBase64: "iVBORw0KGgo=",
            expectedSize: 128,
            expectedMtimeNs: "1700000000000000001"
          },
          {
            path: "src/gfx/interface/ideas/GFX_idea_beta.dds",
            contentBase64: "iVBORw0KGgo=",
            contentFormat: "png",
            targetFormat: "dds",
            expectedAbsent: true
          }
        ],
        moduleRename: {
          moduleId: "idea/IDEA_ALPHA",
          objectId: "IDEA_ALPHA",
          sourceRoot: "/tmp/PIHC3/src",
          title: "Readable Alpha"
        }
      })
    ).resolves.toEqual(payload);

    expect(fetchMock).toHaveBeenNthCalledWith(1, "http://127.0.0.1:47831/frontend-api/rest-request?operation_id=project.draft_apply", {
      body: JSON.stringify({
        project_id: "PIHC3",
        path: "/tmp/PIHC3",
        source_edits: sourceEditValues,
        source_removals: sourceRemovalValues,
        source_replacements: sourceReplacements,
        module_rename: moduleRename
      }),
      headers: { "Content-Type": "application/json" },
      method: "POST"
    });
    expect(fetchMock).toHaveBeenNthCalledWith(2, "http://127.0.0.1:47831/projects/PIHC3/drafts/apply", {
      body: JSON.stringify({
        project_root: "/tmp/PIHC3",
        source_edits: sourceEditValues,
        source_removals: sourceRemovalValues,
        source_replacements: sourceReplacements,
        module_rename: moduleRename
      }),
      headers: { "Content-Type": "application/json" },
      method: "POST"
    });
    expect(fetchMock.mock.calls.map(([url]) => String(url))).not.toContain("http://127.0.0.1:47831/desktop/drafts/apply");
  });

  it("starts project builds through the native lifecycle bridge", async () => {
    installNativeBridge();
    nativeBridgePayloadMock.mockResolvedValueOnce({
      schema: "paradev.desktop.build-run.v1",
      runId: "build-1",
      status: "running",
      mode: "full",
      projectRoot: "/tmp/PIHC3"
    });

    const payload = await startProjectBuild({
      projectRoot: "/tmp/PIHC3",
      mode: "full",
      parallelism: 4,
      profile: "hoi4",
      strictMetadata: true,
      target: {
        kind: "module",
        id: "focus_tree/GER_main"
      }
    });

    expect(payload.status).toBe("running");
  });

  it("lists active project builds through the native lifecycle bridge", async () => {
    installNativeBridge();
    nativeBridgePayloadMock.mockResolvedValue({
      schema: "paradev.desktop.build-runs.v1",
      runs: [
        {
          schema: "paradev.desktop.build-run.v1",
          projectRoot: "/tmp/PIHC3",
          runId: "build-1",
          status: "running"
        }
      ]
    });

    await expect(getProjectBuildRuns("/tmp/PIHC3")).resolves.toMatchObject({ runs: [{ runId: "build-1" }] });
    await getProjectBuildRuns();

  });

  it("reads and interrupts active project builds through the native web bridge", async () => {
    installNativeBridge();
    nativeBridgePayloadMock.mockResolvedValueOnce({
      schema: "paradev.desktop.build-run.v1",
      status: "running",
      runId: "build-1"
    });
    nativeBridgePayloadMock.mockResolvedValueOnce({
      schema: "paradev.desktop.build-run.v1",
      status: "interrupted",
      runId: "build-1"
    });

    await getProjectBuildStatus("build-1");
    await interruptProjectBuild("build-1");

  });

  it("keeps omitted build selection but rejects explicit blank run IDs", async () => {
    installNativeBridge();
    nativeBridgePayloadMock.mockResolvedValue({
      schema: "paradev.desktop.build-run.v1",
      status: "idle",
      runId: null
    });

    await getProjectBuildStatus();
    await interruptProjectBuild(undefined);
    await getProjectBuildStatus("  build-1  ");


    for (const runId of ["", "   ", "\t\n"]) {
      await expect(getProjectBuildStatus(runId)).rejects.toThrow("Build run ID cannot be empty.");
      await expect(interruptProjectBuild(runId)).rejects.toThrow("Build run ID cannot be empty.");
    }
  });

  it("checks and installs desktop dependencies through the native web bridge", async () => {
    installNativeBridge();
    nativeBridgePayloadMock.mockResolvedValueOnce({
      schema: "paradev.desktop.dependency.v1",
      id: "imagemagick",
      label: "ImageMagick",
      installed: true,
      status: "ready",
      path: "/opt/homebrew/bin/magick",
      version: "ImageMagick 7.1.2",
      installCommand: ["brew", "install", "imagemagick"],
      installSupported: true
    });
    nativeBridgePayloadMock.mockResolvedValueOnce({
      schema: "paradev.desktop.dependency.v1",
      id: "imagemagick",
      label: "ImageMagick",
      installed: true,
      status: "ready",
      path: "/opt/homebrew/bin/magick",
      version: "ImageMagick 7.1.2",
      installCommand: ["brew", "install", "imagemagick"],
      installSupported: true
    });

    const status = await checkDesktopDependency("imagemagick");
    const installed = await installDesktopDependency("imagemagick");

    expect(status.installed).toBe(true);
    expect(installed.path).toBe("/opt/homebrew/bin/magick");
  });

  it("tests HeavenBase LLM routes through the native web bridge", async () => {
    installNativeBridge();
    nativeBridgePayloadMock.mockResolvedValueOnce({
      schema: "paradev.desktop.llm-test.v1",
      baseUrl: "https://api.deepseek.com/v1",
      gateway: "openai",
      keySource: "DEEPSEEK_API_KEY",
      model: "deepseek-v4-flash",
      preset: "reason",
      provider: "deepseek",
      status: "warning",
      resultCode: "empty_response",
      testDetail: "deepseek / deepseek-v4-flash route returned an empty response.",
      testedAt: "2026-06-28T00:00:00.000Z"
    });

    const status = await testHeavenBaseLlmRoute({
      baseUrl: "https://proxy.example/v1",
      gateway: "openai",
      keyEnv: "VISIBLE_DEEPSEEK_KEY",
      model: "deepseek-v4-flash",
      preset: "reason",
      provider: "deepseek"
    });

    expect(status.model).toBe("deepseek-v4-flash");
    expect(status.preset).toBe("reason");
    expect(status.keySource).toBe("DEEPSEEK_API_KEY");
    expect(status.resultCode).toBe("empty_response");
    expect(status.testDetail).toBe("deepseek / deepseek-v4-flash route returned an empty response.");
  });

  it("tests HeavenBase LLM routes through the native web bridge", async () => {
    vi.stubGlobal("window", {});
    vi.stubEnv("VITE_PARADEV_NATIVE_BRIDGE_URL", "http://127.0.0.1:47831");
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      statusText: "OK",
      json: async () => ({
        schema: "paradev.desktop.llm-test.v1",
        provider: "deepseek",
        model: "deepseek-v4-flash",
        gateway: "openai",
        keySource: "VISIBLE_DEEPSEEK_KEY",
        preset: "reason",
        status: "ready",
        resultCode: "ok",
        testDetail: "Received hb-ok.",
        baseUrl: "https://api.deepseek.com/v1",
        testedAt: "2026-06-28T00:00:00.000Z"
      })
    });
    vi.stubGlobal("fetch", fetchMock);

    const status = await testHeavenBaseLlmRoute({
      baseUrl: "https://proxy.example/v1",
      provider: "deepseek",
      model: "deepseek-v4-flash",
      preset: "reason",
      gateway: "openai",
      keyEnv: "VISIBLE_DEEPSEEK_KEY"
    });

    expect(status.resultCode).toBe("ok");
    expect(status.preset).toBe("reason");
    expect(fetchMock).toHaveBeenCalledWith("http://127.0.0.1:47831/desktop/llm/test", {
      body: JSON.stringify({ provider: "deepseek", model: "deepseek-v4-flash", gateway: "openai", preset: "reason", keyEnv: "VISIBLE_DEEPSEEK_KEY", baseUrl: "https://proxy.example/v1" }),
      headers: { "content-type": "application/json" },
      method: "POST"
    });
  });

  it("sends AI chat prompts through the native web bridge", async () => {
    installNativeBridge();
    nativeBridgePayloadMock.mockResolvedValueOnce({
      schema: "paradev.desktop.ai-chat.v1",
      baseUrl: "https://api.deepseek.com/v1",
      checkedAt: "2026-06-29T00:00:00.000Z",
      detail: "",
      gateway: "openai",
      keySource: "DEEPSEEK_API_KEY",
      model: "deepseek-v4-flash",
      projectRoot: "/tmp/PIHC3",
      prompt: "Explain this focus.",
      provider: "deepseek",
      reply: "This focus grants a national spirit.",
      role: "explain",
      sources: [
        { kind: "source", label: "Focus metadata", path: "src/modules/focus_tree/C01_MAIN/info.json" },
        { content: "1. [error] Missing focus icon.", kind: "diagnostics", label: "Diagnostics (1)" }
      ],
      status: "ready"
    });

    const payload = await chatWithParaDevAi({
      baseUrl: "https://proxy.example/v1",
      gateway: "openai",
      keyEnv: "VISIBLE_DEEPSEEK_KEY",
      model: "deepseek-v4-flash",
      preset: "reason",
      projectRoot: "/tmp/PIHC3",
      prompt: "Explain this focus.",
      provider: "deepseek",
      role: "explain",
      sources: [
        { kind: "source", label: "Focus metadata", path: "src/modules/focus_tree/C01_MAIN/info.json" },
        { content: "1. [error] Missing focus icon.", kind: "diagnostics", label: "Diagnostics (1)" }
      ]
    });

    expect(payload.reply).toBe("This focus grants a national spirit.");
    expect(payload.projectRoot).toBe("/tmp/PIHC3");
    expect(payload.sources[1]).toMatchObject({ content: "1. [error] Missing focus icon.", kind: "diagnostics", label: "Diagnostics (1)" });
  });

  it("validates and retains a dry module-batch proposal from AI chat", async () => {
    installNativeBridge();
    const plan = moduleCreateBatchPlanPayload();
    nativeBridgePayloadMock.mockResolvedValueOnce({
      schema: "paradev.desktop.ai-chat.v1",
      baseUrl: "https://api.deepseek.com/v1",
      checkedAt: "2026-07-28T00:00:00.000Z",
      detail: "",
      gateway: "openai",
      keySource: "DEEPSEEK_API_KEY",
      model: "deepseek-v4-flash",
      projectRoot: "/tmp/PIHC3",
      prompt: "Create IDEA_DEMO.",
      provider: "deepseek",
      proposal: {
        schema: "paradev.desktop.ai-chat-proposal.v1",
        operationId: "module.create_batch",
        familyId: "idea",
        sourceRoot: "/tmp/PIHC3/src",
        requests: [
          {
            template_id: "hoi4:idea/basic",
            object_id: "IDEA_DEMO",
            values: { cic: 0.02, title: "Demo Idea" }
          }
        ],
        plan
      },
      reply: "I prepared one read-only module plan.",
      role: "create-module",
      sources: [],
      status: "ready"
    });

    const payload = await chatWithParaDevAi({
      gateway: "openai",
      model: "deepseek-v4-flash",
      projectRoot: "/tmp/PIHC3",
      prompt: "Create IDEA_DEMO.",
      provider: "deepseek",
      role: "create-module",
      sources: []
    });

    expect(payload.proposal).toMatchObject({
      schema: "paradev.desktop.ai-chat-proposal.v1",
      operationId: "module.create_batch",
      familyId: "idea",
      sourceRoot: "/tmp/PIHC3/src",
      requests: [
        {
          template_id: "hoi4:idea/basic",
          object_id: "IDEA_DEMO",
          values: { cic: 0.02, title: "Demo Idea" }
        }
      ],
      plan: {
        schema: "paradev.sdk.module_batch.v1",
        applied: false,
        written: false,
        requested_count: 1
      }
    });
  });

  it("validates and retains a dry collection-scaffold proposal from AI chat", async () => {
    installNativeBridge();
    const plan = {
      schema: "paradev.sdk.collection_scaffold.v1",
      project_id: "PIHC3",
      template_id: "pihc3:focus-tree/basic",
      kind: "collection",
      family: "focus",
      object_id: "C99_AI_REVIEW",
      collection_id: "C99_AI_REVIEW",
      folder_name: "C99_AI_REVIEW - AI Review Tree",
      source_root: "/tmp/PIHC3/src",
      root: "/tmp/PIHC3/src/collections/focus/C99_AI_REVIEW - AI Review Tree",
      values: {
        country_tag: "C99",
        title: "AI Review Tree"
      },
      blocked: false,
      written: false,
      plan_hash: "b".repeat(64),
      diagnostics: [],
      files: [],
      authoring_plan: {}
    };
    nativeBridgePayloadMock.mockResolvedValueOnce({
      schema: "paradev.desktop.ai-chat.v1",
      gateway: "openai",
      keySource: "DEEPSEEK_API_KEY",
      model: "deepseek-v4-flash",
      projectRoot: "/tmp/PIHC3",
      prompt: "Create a focus tree for C99.",
      provider: "deepseek",
      proposal: {
        schema: "paradev.desktop.ai-chat-proposal.v1",
        operationId: "collection.scaffold",
        familyId: "focus",
        sourceRoot: "/tmp/PIHC3/src",
        request: {
          template_id: "pihc3:focus-tree/basic",
          collection_id: "C99_AI_REVIEW",
          values: {
            country_tag: "C99",
            title: "AI Review Tree"
          }
        },
        plan
      },
      reply: "I prepared one read-only collection plan.",
      role: "create-module",
      sources: [],
      status: "ready"
    });

    const payload = await chatWithParaDevAi({
      gateway: "openai",
      model: "deepseek-v4-flash",
      projectRoot: "/tmp/PIHC3",
      prompt: "Create a focus tree for C99.",
      provider: "deepseek",
      role: "create-module",
      sources: []
    });

    expect(payload.proposal).toEqual({
      schema: "paradev.desktop.ai-chat-proposal.v1",
      operationId: "collection.scaffold",
      familyId: "focus",
      sourceRoot: "/tmp/PIHC3/src",
      request: {
        template_id: "pihc3:focus-tree/basic",
        collection_id: "C99_AI_REVIEW",
        values: {
          country_tag: "C99",
          title: "AI Review Tree"
        }
      },
      plan
    });
  });

  it("validates and retains a guarded source-form update proposal from AI chat", async () => {
    installNativeBridge();
    const plan = validSourceFormUpdateBatchPayload();
    nativeBridgePayloadMock.mockResolvedValueOnce({
      schema: "paradev.desktop.ai-chat.v1",
      gateway: "openai",
      keySource: "DEEPSEEK_API_KEY",
      model: "deepseek-v4-flash",
      projectRoot: "/tmp/PIHC3",
      prompt: "Set the selected entity scale to 4.5.",
      provider: "deepseek",
      proposal: {
        schema: "paradev.desktop.ai-chat-proposal.v1",
        operationId: "module.source_form_update_batch",
        familyId: "Entity",
        requests: [
          {
            source_path: "src/modules/Entity/VIENTO_MIRROR/record.json",
            module_id: "Entity/VIENTO_MIRROR",
            values: { "mesh.scale": 4.5 },
            control_labels: {
              "mesh.scale": { default: "Mesh scale", zh: "模型缩放" }
            }
          }
        ],
        plan
      },
      reply: "I prepared one guarded source edit.",
      role: "edit-selection",
      sources: [],
      status: "ready"
    });

    const payload = await chatWithParaDevAi({
      gateway: "openai",
      model: "deepseek-v4-flash",
      projectRoot: "/tmp/PIHC3",
      prompt: "Set the selected entity scale to 4.5.",
      provider: "deepseek",
      role: "edit-selection",
      sources: []
    });

    expect(payload.proposal).toEqual({
      schema: "paradev.desktop.ai-chat-proposal.v1",
      operationId: "module.source_form_update_batch",
      familyId: "Entity",
      requests: [
        {
          source_path: "src/modules/Entity/VIENTO_MIRROR/record.json",
          module_id: "Entity/VIENTO_MIRROR",
          values: { "mesh.scale": 4.5 },
          control_labels: {
            "mesh.scale": { default: "Mesh scale", zh: "模型缩放" }
          }
        }
      ],
      plan: {
        schema: "paradev.source-form-update-batch.v1",
        projectId: "PIHC3",
        changed: true,
        counts: { requested: 1, changed: 1, unchanged: 0 },
        updates: [
          expect.objectContaining({
            family: "Entity",
            moduleId: "Entity/VIENTO_MIRROR",
            relativePath: "src/modules/Entity/VIENTO_MIRROR/record.json",
            changes: [
              { controlId: "mesh.scale", previous: 4.25, value: 4.5 }
            ]
          })
        ],
        sourceEdits: [
          {
            path: "/tmp/PIHC3/src/modules/Entity/VIENTO_MIRROR/record.json",
            text: '{"mesh":{"scale":4.5}}\n',
            expectedSize: 24,
            expectedMtimeNs: "1770000000123456789"
          }
        ]
      }
    });
  });

  it("rejects AI source-update proposals with fields outside the reviewed contract", async () => {
    installNativeBridge();
    nativeBridgePayloadMock.mockResolvedValueOnce({
      schema: "paradev.desktop.ai-chat.v1",
      gateway: "openai",
      keySource: "DEEPSEEK_API_KEY",
      model: "deepseek-v4-flash",
      projectRoot: "/tmp/PIHC3",
      prompt: "Change the selected source.",
      provider: "deepseek",
      proposal: {
        schema: "paradev.desktop.ai-chat-proposal.v1",
        operationId: "module.source_form_update_batch",
        familyId: "Entity",
        requests: [
          {
            source_path: "src/modules/Entity/VIENTO_MIRROR/record.json",
            module_id: "Entity/VIENTO_MIRROR",
            values: { "mesh.scale": 4.5 },
            control_labels: { "mesh.scale": "Mesh scale" },
            write: true
          }
        ],
        plan: validSourceFormUpdateBatchPayload()
      },
      reply: "Unsafe edit.",
      role: "edit-selection",
      sources: [],
      status: "ready"
    });

    await expect(
      chatWithParaDevAi({
        gateway: "openai",
        model: "deepseek-v4-flash",
        projectRoot: "/tmp/PIHC3",
        prompt: "Change the selected source.",
        provider: "deepseek",
        role: "edit-selection",
        sources: []
      })
    ).rejects.toThrow(
      "AI chat source-update request 0 did not match the exact payload shape"
    );
  });

  it("rejects AI collection proposals with fields outside the reviewed scaffold contract", async () => {
    installNativeBridge();
    nativeBridgePayloadMock.mockResolvedValueOnce({
      schema: "paradev.desktop.ai-chat.v1",
      gateway: "openai",
      keySource: "DEEPSEEK_API_KEY",
      model: "deepseek-v4-flash",
      projectRoot: "/tmp/PIHC3",
      prompt: "Create a focus tree.",
      provider: "deepseek",
      proposal: {
        schema: "paradev.desktop.ai-chat-proposal.v1",
        operationId: "collection.scaffold",
        familyId: "focus",
        sourceRoot: "/tmp/PIHC3/src",
        request: {
          template_id: "pihc3:focus-tree/basic",
          collection_id: "C99_AI_REVIEW",
          values: {},
          write: true
        },
        plan: {}
      },
      reply: "",
      role: "create-module",
      sources: [],
      status: "ready"
    });

    await expect(
      chatWithParaDevAi({
        gateway: "openai",
        model: "deepseek-v4-flash",
        projectRoot: "/tmp/PIHC3",
        prompt: "Create a focus tree.",
        provider: "deepseek",
        role: "create-module",
        sources: []
      })
    ).rejects.toThrow(
      "AI chat collection request did not match the exact payload shape"
    );
  });

  it("rejects AI module proposals with fields outside the reviewed batch contract", async () => {
    installNativeBridge();
    nativeBridgePayloadMock.mockResolvedValueOnce({
      schema: "paradev.desktop.ai-chat.v1",
      gateway: "openai",
      keySource: "DEEPSEEK_API_KEY",
      model: "deepseek-v4-flash",
      projectRoot: "/tmp/PIHC3",
      prompt: "Create IDEA_DEMO.",
      provider: "deepseek",
      proposal: {
        schema: "paradev.desktop.ai-chat-proposal.v1",
        operationId: "module.create_batch",
        familyId: "idea",
        sourceRoot: "/tmp/PIHC3/src",
        requests: [
          {
            template_id: "hoi4:idea/basic",
            object_id: "IDEA_DEMO",
            values: { title: "Demo Idea" },
            write: true
          }
        ],
        plan: moduleCreateBatchPlanPayload()
      },
      reply: "",
      role: "create-module",
      sources: [],
      status: "ready"
    });

    await expect(
      chatWithParaDevAi({
        gateway: "openai",
        model: "deepseek-v4-flash",
        projectRoot: "/tmp/PIHC3",
        prompt: "Create IDEA_DEMO.",
        provider: "deepseek",
        role: "create-module",
        sources: []
      })
    ).rejects.toThrow("AI chat proposal request 0 did not match the exact payload shape");
  });

  it("loads AI chat profiles through the native web bridge", async () => {
    installNativeBridge();
    nativeBridgePayloadMock.mockResolvedValueOnce({
      schema: "paradev.desktop.ai-chat-profiles.v1",
      defaultRole: "chat",
      projectRoot: "/tmp/PIHC3",
      sourceKinds: ["project", "selection", "diagnostics", "templates"],
      profiles: [
        {
          id: "explain",
          label: "Explain HoI4 code",
          detail: "Explain selected source.",
          promptKey: "chat.profile.explain.prompt",
          prompt: "Explain HoI4 code.",
          sourceKinds: ["project", "selection"]
        }
      ]
    });

    const payload = await loadParaDevAiChatProfiles("/tmp/PIHC3");

    expect(payload.defaultRole).toBe("chat");
    expect(payload.sourceKinds).toEqual(["project", "selection", "diagnostics", "templates"]);
    expect(payload.profiles[0]?.id).toBe("explain");
    expect(payload.profiles[0]?.promptKey).toBe("chat.profile.explain.prompt");
  });

  it("surfaces AI chat profile validation errors instead of falling back", async () => {
    installNativeBridge();
    nativeBridgePayloadMock.mockRejectedValueOnce(new Error("AI chat profile overrides must use schema paradev.sdk.ai-chat-profile-overrides.v1."));

    await expect(loadParaDevAiChatProfiles("/tmp/PIHC3")).rejects.toThrow("AI chat profile overrides");
  });

  it("writes SDK-owned AI chat profile prompts through the native web bridge", async () => {
    installNativeBridge();
    nativeBridgePayloadMock.mockResolvedValueOnce({
      schema: "paradev.desktop.ai-chat-profiles.v1",
      defaultRole: "chat",
      projectRoot: "/tmp/PIHC3",
      profiles: [
        {
          id: "explain",
          label: "Explain HoI4 code",
          detail: "Custom PIHC3 explanation.",
          prompt: "Prefer editable SDK prompts.",
          sourceKinds: ["project", "selection"]
        }
      ]
    });

    const payload = await writeParaDevAiChatProfile(
      "explain",
      {
        label: "Explain HoI4 code",
        detail: "Custom PIHC3 explanation.",
        prompt: "Prefer editable SDK prompts.",
        sourceKinds: ["project", "selection"]
      },
      "/tmp/PIHC3"
    );

    expect(payload.profiles[0]?.prompt).toBe("Prefer editable SDK prompts.");
  });

  it("resets SDK-owned AI chat profiles through the native web bridge", async () => {
    installNativeBridge();
    nativeBridgePayloadMock.mockResolvedValueOnce({
      schema: "paradev.desktop.ai-chat-profiles.v1",
      defaultRole: "chat",
      projectRoot: "/tmp/PIHC3",
      profiles: [
        {
          id: "explain",
          label: "Explain HoI4 code",
          detail: "Explain selected source.",
          prompt: "Explain HoI4 code.",
          sourceKinds: ["project", "selection"]
        }
      ]
    });

    const payload = await resetParaDevAiChatProfile("explain", "/tmp/PIHC3");

    expect(payload.profiles[0]?.prompt).toBe("Explain HoI4 code.");
  });

  it("keeps SDK-compatible AI chat role options outside the desktop backend", async () => {
    vi.stubGlobal("window", {});

    const payload = await loadParaDevAiChatProfiles("/tmp/PIHC3");

    expect(payload.schema).toBe("paradev.desktop.ai-chat-profiles.v1");
    expect(payload.projectRoot).toBe("/tmp/PIHC3");
    expect(payload.profiles.map((profile) => profile.id)).toEqual(["chat", "explain", "create-module", "edit-selection", "build"]);
    expect(payload.profiles[0]?.prompt).toContain("grounded in the Python SDK");
    expect(payload.profiles[2]?.prompt).toContain("Project.templates()");
    expect(payload.profiles[2]?.prompt).toContain("Project.create_modules(..., write=False)");
    expect(payload.profiles[2]?.prompt).toContain("Project.scaffold_collection(..., write=False)");
    expect(payload.profiles[2]?.operationIds).toEqual(["module.draft", "module.create_batch", "collection.scaffold"]);
    expect(payload.profiles[2]?.operationCards?.map((card) => card.id)).toEqual(["module.draft", "module.create_batch", "collection.scaffold"]);
    expect(payload.profiles[2]?.operationCards?.[0]).toMatchObject({
      mutates: true,
      sdk: "Project.create_module_draft"
    });
    expect(payload.profiles[2]?.operationCards?.[1]).toMatchObject({
      mutates: true,
      sdk: "Project.create_modules"
    });
    expect(payload.profiles[2]?.operationCards?.[2]).toMatchObject({
      mutates: true,
      sdk: "Project.scaffold_collection"
    });
    expect(payload.profiles[3]?.prompt).toContain("Project.plan_source_form_updates(...)");
    expect(payload.profiles[3]?.sourceKinds).toEqual(["project", "selection"]);
    expect(payload.profiles[4]?.prompt).toContain("Project.build(...)");
    expect(payload.profiles[4]?.prompt).toContain("desktop_project_build_command(...)");
    expect(payload.profiles[4]?.operationIds).toEqual(["build.plan", "build.start"]);
    expect(payload.profiles[4]?.operationCards?.map((card) => card.id)).toEqual(["build.plan", "build.start"]);
    expect(payload.profiles[1]).toMatchObject({
      detailKey: "chat.profile.explain.detail",
      labelKey: "chat.profile.explain.label"
    });
  });

  it("sends AI chat prompts through the native web bridge", async () => {
    vi.stubGlobal("window", {});
    vi.stubEnv("VITE_PARADEV_NATIVE_BRIDGE_URL", "http://127.0.0.1:47831");
    const sources = [
      { kind: "workspace", label: "Ideas", familyId: "idea" },
      { content: "1. [warning] Missing localization.", kind: "diagnostics", label: "Diagnostics (1)" }
    ];
    const restPlanResponse = {
      ok: true,
      status: 200,
      statusText: "OK",
      json: async () => ({
        schema: "paradev.sdk.frontend-api.rest-request.v1",
        operation_id: "ai.chat",
        method: "POST",
        path: "/desktop/ai/chat",
        query: {},
        body: {
          provider: "deepseek",
          model: "deepseek-v4-flash",
          gateway: "openai",
          preset: "reason",
          key_env: "VISIBLE_DEEPSEEK_KEY",
          base_url: "https://proxy.example/v1",
          prompt: "Explain this idea.",
          sources
        },
        binding: {
          method: "POST",
          path: "/desktop/ai/chat",
          query: {}
        },
        normalized: {
          schema: "paradev.sdk.frontend-api.inputs.v1",
          operation_id: "ai.chat",
          values: {},
          project: {},
          parameters: {
            provider: "deepseek",
            model: "deepseek-v4-flash",
            gateway: "openai",
            preset: "reason",
            key_env: "VISIBLE_DEEPSEEK_KEY",
            base_url: "https://proxy.example/v1",
            prompt: "Explain this idea.",
            sources
          },
          selectors: {},
          projections: {}
        }
      })
    };
    const chatResponse = {
      ok: true,
      status: 200,
      statusText: "OK",
      json: async () => ({
        schema: "paradev.desktop.ai-chat.v1",
        provider: "deepseek",
        model: "deepseek-v4-flash",
        gateway: "openai",
        keySource: "DEEPSEEK_API_KEY",
        status: "ready",
        role: "chat",
        projectRoot: "",
        prompt: "Explain this idea.",
        reply: "This idea adds a modifier.",
        sources: [{ content: "1. [warning] Missing localization.", kind: "diagnostics", label: "Diagnostics (1)" }],
        detail: "",
        baseUrl: "https://api.deepseek.com/v1",
        checkedAt: "2026-06-29T00:00:00.000Z"
      })
    };
    const fetchMock = vi.fn(async (url: string) => (url.includes("/frontend-api/rest-request") ? restPlanResponse : chatResponse));
    vi.stubGlobal("fetch", fetchMock);

    const payload = await chatWithParaDevAi({
      provider: "deepseek",
      model: "deepseek-v4-flash",
      preset: "reason",
      gateway: "openai",
      keyEnv: "VISIBLE_DEEPSEEK_KEY",
      baseUrl: "https://proxy.example/v1",
      prompt: "Explain this idea.",
      sources
    });

    expect(payload.sources).toEqual([{ content: "1. [warning] Missing localization.", kind: "diagnostics", label: "Diagnostics (1)" }]);
    expect(fetchMock).toHaveBeenNthCalledWith(1, "http://127.0.0.1:47831/frontend-api/rest-request?operation_id=ai.chat", {
      body: JSON.stringify({
        provider: "deepseek",
        model: "deepseek-v4-flash",
        gateway: "openai",
        preset: "reason",
        key_env: "VISIBLE_DEEPSEEK_KEY",
        base_url: "https://proxy.example/v1",
        prompt: "Explain this idea.",
        sources
      }),
      headers: { "Content-Type": "application/json" },
      method: "POST"
    });
    expect(fetchMock).toHaveBeenNthCalledWith(2, "http://127.0.0.1:47831/desktop/ai/chat", {
      body: JSON.stringify({
        provider: "deepseek",
        model: "deepseek-v4-flash",
        gateway: "openai",
        preset: "reason",
        key_env: "VISIBLE_DEEPSEEK_KEY",
        base_url: "https://proxy.example/v1",
        prompt: "Explain this idea.",
        sources
      }),
      headers: { "Content-Type": "application/json" },
      method: "POST"
    });
  });

  it("loads AI chat profiles through the native web bridge", async () => {
    vi.stubGlobal("window", {});
    vi.stubEnv("VITE_PARADEV_NATIVE_BRIDGE_URL", "http://127.0.0.1:47831");
    const restPlanResponse = {
      ok: true,
      status: 200,
      statusText: "OK",
      json: async () => ({
        schema: "paradev.sdk.frontend-api.rest-request.v1",
        operation_id: "ai.profiles",
        method: "GET",
        path: "/desktop/ai/profiles",
        query: { project_root: "/tmp/PIHC3" },
        body: {},
        binding: {
          method: "GET",
          path: "/desktop/ai/profiles",
          query: {}
        },
        normalized: {
          schema: "paradev.sdk.frontend-api.inputs.v1",
          operation_id: "ai.profiles",
          values: {},
          project: {},
          parameters: { project_root: "/tmp/PIHC3" },
          selectors: {},
          projections: {}
        }
      })
    };
    const profilesResponse = {
      ok: true,
      status: 200,
      statusText: "OK",
      json: async () => ({
        schema: "paradev.desktop.ai-chat-profiles.v1",
        defaultRole: "chat",
        projectRoot: "/tmp/PIHC3",
        profiles: [
          {
            id: "build",
            label: "Build/debug project",
            detail: "Explain build output.",
            prompt: "Help debug builds.",
            sourceKinds: ["project", "diagnostics"]
          }
        ]
      })
    };
    const fetchMock = vi.fn(async (url: string) => (url.includes("/frontend-api/rest-request") ? restPlanResponse : profilesResponse));
    vi.stubGlobal("fetch", fetchMock);

    const payload = await loadParaDevAiChatProfiles("/tmp/PIHC3");

    expect(payload.profiles[0]?.id).toBe("build");
    expect(fetchMock).toHaveBeenNthCalledWith(1, "http://127.0.0.1:47831/frontend-api/rest-request?operation_id=ai.profiles", {
      body: JSON.stringify({ project_root: "/tmp/PIHC3" }),
      headers: { "Content-Type": "application/json" },
      method: "POST"
    });
    expect(fetchMock).toHaveBeenNthCalledWith(2, "http://127.0.0.1:47831/desktop/ai/profiles?project_root=%2Ftmp%2FPIHC3", {
      method: "GET"
    });
  });

  it("writes AI chat profiles through the native web bridge", async () => {
    vi.stubGlobal("window", {});
    vi.stubEnv("VITE_PARADEV_NATIVE_BRIDGE_URL", "http://127.0.0.1:47831");
    const profile = {
      label: "Explain HoI4 code",
      detail: "Custom PIHC3 explanation.",
      prompt: "Prefer editable SDK prompts.",
      sourceKinds: ["project", "selection"]
    };
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce({
        ok: true,
        status: 200,
        statusText: "OK",
        json: async () => ({
          schema: "paradev.sdk.frontend-api.rest-request.v1",
          operation_id: "ai.profile.write",
          method: "PUT",
          path: "/desktop/ai/profiles/explain",
          query: {},
          body: {
            profile,
            project_root: "/tmp/PIHC3"
          },
          binding: {
            method: "PUT",
            path: "/desktop/ai/profiles/{profile_id}",
            query: {}
          },
          normalized: {
            schema: "paradev.sdk.frontend-api.inputs.v1",
            operation_id: "ai.profile.write",
            values: {},
            project: {},
            parameters: {
              profile_id: "explain",
              profile,
              project_root: "/tmp/PIHC3"
            },
            selectors: {},
            projections: {}
          }
        })
      })
      .mockResolvedValueOnce({
        ok: true,
        status: 200,
        statusText: "OK",
        json: async () => ({
        schema: "paradev.desktop.ai-chat-profiles.v1",
        defaultRole: "chat",
        projectRoot: "/tmp/PIHC3",
        profiles: [
          {
            id: "explain",
            label: "Explain HoI4 code",
            detail: "Custom PIHC3 explanation.",
            prompt: "Prefer editable SDK prompts.",
            sourceKinds: ["project", "selection"]
          }
        ]
        })
      });
    vi.stubGlobal("fetch", fetchMock);

    await writeParaDevAiChatProfile("explain", profile, "/tmp/PIHC3");

    expect(fetchMock).toHaveBeenNthCalledWith(1, "http://127.0.0.1:47831/frontend-api/rest-request?operation_id=ai.profile.write", {
      body: JSON.stringify({
        profile_id: "explain",
        profile,
        project_root: "/tmp/PIHC3"
      }),
      headers: { "Content-Type": "application/json" },
      method: "POST"
    });
    expect(fetchMock).toHaveBeenNthCalledWith(2, "http://127.0.0.1:47831/desktop/ai/profiles/explain", {
      body: JSON.stringify({
        profile,
        project_root: "/tmp/PIHC3"
      }),
      headers: { "Content-Type": "application/json" },
      method: "PUT"
    });
  });

  it("resets AI chat profiles through the native web bridge", async () => {
    vi.stubGlobal("window", {});
    vi.stubEnv("VITE_PARADEV_NATIVE_BRIDGE_URL", "http://127.0.0.1:47831");
    const restPlanResponse = {
      ok: true,
      status: 200,
      statusText: "OK",
      json: async () => ({
        schema: "paradev.sdk.frontend-api.rest-request.v1",
        operation_id: "ai.profile.reset",
        method: "DELETE",
        path: "/desktop/ai/profiles/explain",
        query: { project_root: "/tmp/PIHC3" },
        body: {},
        binding: {
          method: "DELETE",
          path: "/desktop/ai/profiles/{profile_id}",
          query: {}
        },
        normalized: {
          schema: "paradev.sdk.frontend-api.inputs.v1",
          operation_id: "ai.profile.reset",
          values: {},
          project: {},
          parameters: { profile_id: "explain", project_root: "/tmp/PIHC3" },
          selectors: {},
          projections: {}
        }
      })
    };
    const resetResponse = {
      ok: true,
      status: 200,
      statusText: "OK",
      json: async () => ({
        schema: "paradev.desktop.ai-chat-profiles.v1",
        defaultRole: "chat",
        projectRoot: "/tmp/PIHC3",
        profiles: [
          {
            id: "explain",
            label: "Explain HoI4 code",
            detail: "Explain selected source.",
            prompt: "Explain HoI4 code.",
            sourceKinds: ["project", "selection"]
          }
        ]
      })
    };
    const fetchMock = vi.fn(async (url: string) => (url.includes("/frontend-api/rest-request") ? restPlanResponse : resetResponse));
    vi.stubGlobal("fetch", fetchMock);

    await resetParaDevAiChatProfile("explain", "/tmp/PIHC3");

    expect(fetchMock).toHaveBeenNthCalledWith(1, "http://127.0.0.1:47831/frontend-api/rest-request?operation_id=ai.profile.reset", {
      body: JSON.stringify({ profile_id: "explain", project_root: "/tmp/PIHC3" }),
      headers: { "Content-Type": "application/json" },
      method: "POST"
    });
    expect(fetchMock).toHaveBeenNthCalledWith(2, "http://127.0.0.1:47831/desktop/ai/profiles/explain?project_root=%2Ftmp%2FPIHC3", {
      method: "DELETE"
    });
  });

  it("rejects native build control without a desktop backend", async () => {
    vi.stubGlobal("window", {});

    await expect(startProjectBuild({ projectRoot: "/tmp/PIHC3", mode: "cached" })).rejects.toThrow(
      "Starting project builds requires the ParaDev desktop application."
    );
  });

  it("preserves native web bridge error details for local path actions", async () => {
    vi.stubGlobal("window", {});
    vi.stubEnv("VITE_PARADEV_NATIVE_BRIDGE_URL", "http://127.0.0.1:47831");
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValueOnce({
        ok: false,
        status: 400,
        statusText: "Bad Request",
        json: async () => ({ detail: "Open path does not exist: /tmp/PIHC3/build/mod" })
      })
    );

    await expect(openProjectPath("/tmp/PIHC3/build/mod", "finder")).rejects.toThrow("Open path does not exist: /tmp/PIHC3/build/mod");
  });

  it("launches HOI4 through the native web bridge with an explicit launch mode", async () => {
    installNativeBridge();
    nativeBridgePayloadMock.mockResolvedValueOnce({
      schema: "paradev.desktop.game-launch.v1",
      game: "hoi4",
      mode: "steam",
      status: "started",
      gameRoot: "steam://rungameid/394360"
    });

    const payload = await runHoi4Game({ projectRoot: "/tmp/PIHC3", mode: "steam", gameRoot: "/Games/Hearts of Iron IV" });

    expect(payload.status).toBe("started");
  });

  it("loads authoritative HOI4 launch readiness through the native web bridge", async () => {
    installNativeBridge();
    nativeBridgePayloadMock.mockResolvedValueOnce({
      schema: "paradev.desktop.hoi4-launch-readiness.v1",
      code: "ready",
      game: "hoi4",
      outputRoot: "/mods/PIHC3",
      projectId: "PIHC3",
      projectRoot: "/tmp/PIHC3",
      ready: true,
      reason: "Ready to launch."
    });

    await expect(loadHoi4LaunchReadiness("/tmp/PIHC3")).resolves.toMatchObject({
      code: "ready",
      ready: true
    });
  });

  it("loads authoritative HOI4 launch readiness through the native web bridge", async () => {
    vi.stubGlobal("window", {});
    vi.stubEnv("VITE_PARADEV_NATIVE_BRIDGE_URL", "http://127.0.0.1:47831");
    const fetchMock = vi.fn().mockResolvedValueOnce({
      ok: true,
      status: 200,
      statusText: "OK",
      json: async () => ({
        schema: "paradev.desktop.hoi4-launch-readiness.v1",
        code: "whole_project_baseline_missing",
        game: "hoi4",
        outputRoot: "/mods/PIHC3",
        projectId: "PIHC3",
        projectRoot: "/tmp/PIHC3",
        ready: false,
        reason: "Build the whole project once."
      })
    });
    vi.stubGlobal("fetch", fetchMock);

    await expect(loadHoi4LaunchReadiness("/tmp/PIHC3")).resolves.toMatchObject({
      code: "whole_project_baseline_missing",
      ready: false
    });
    expect(fetchMock).toHaveBeenCalledWith(
      "http://127.0.0.1:47831/desktop/hoi4-launch-readiness?project_root=%2Ftmp%2FPIHC3",
      { method: "GET" }
    );
  });

  it("requests LSP completion through the native web bridge with camelCase game root", async () => {
    installNativeBridge();
    nativeBridgePayloadMock.mockResolvedValueOnce({
      schema: "paradev.lsp.completion.v1",
      method: "textDocument/completion",
      ok: true,
      prefix: "sta",
      isIncomplete: false,
      diagnostics: [],
      items: []
    });

    await requestPdxLspCompletion({
      text: "idea = {\n\tmodifier = {\n\t\tsta",
      line: 2,
      character: 5,
      path: "common/ideas/sample.txt",
      projectPath: "/tmp/PIHC3",
      gameRoot: "/Games/Hearts of Iron IV",
      limit: 40
    });

  });

  it("requests LSP completion through the native web bridge with snake_case game root", async () => {
    vi.stubGlobal("window", {});
    vi.stubEnv("VITE_PARADEV_NATIVE_BRIDGE_URL", "http://127.0.0.1:47831");
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      statusText: "OK",
      json: async () => ({
        schema: "paradev.lsp.completion.v1",
        method: "textDocument/completion",
        ok: true,
        prefix: "sta",
        isIncomplete: false,
        diagnostics: [],
        items: []
      })
    });
    vi.stubGlobal("fetch", fetchMock);

    await requestPdxLspCompletion({
      text: "idea = {\n\tmodifier = {\n\t\tsta",
      line: 2,
      character: 5,
      path: "common/ideas/sample.txt",
      projectPath: "/tmp/PIHC3",
      gameRoot: "/Games/Hearts of Iron IV",
      limit: 40
    });

    expect(fetchMock).toHaveBeenCalledWith("http://127.0.0.1:47831/lsp/completion", {
      body: JSON.stringify({
        text: "idea = {\n\tmodifier = {\n\t\tsta",
        line: 2,
        character: 5,
        path: "common/ideas/sample.txt",
        project_path: "/tmp/PIHC3",
        game_root: "/Games/Hearts of Iron IV",
        limit: 40
      }),
      headers: { "content-type": "application/json" },
      method: "POST"
    });
  });

  it("uses a configured native web bridge without a desktop backend", async () => {
    vi.stubGlobal("window", {});
    vi.stubEnv("VITE_PARADEV_NATIVE_BRIDGE_URL", "http://127.0.0.1:47831/");
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      statusText: "OK",
      json: async () => ({
        schema: "paradev.desktop.state.v1",
        projects: [],
        active_project: null,
        browser: null,
        templates: null,
        diagnostics: []
      })
    });
    vi.stubGlobal("fetch", fetchMock);

    expect(hasDesktopBackend()).toBe(true);
    await loadDesktopState("/tmp/PIHC3", { includeBrowser: false });

    expect(fetchMock).toHaveBeenCalledWith("http://127.0.0.1:47831/desktop/state?project_path=%2Ftmp%2FPIHC3&include_browser=false", {
      method: "GET"
    });
  });

  it("uses the packaged same-origin runtime bridge without a native bridge", async () => {
    vi.stubGlobal("window", {
      location: { origin: "http://127.0.0.1:4817" },
      __PARADEV_RUNTIME_CONFIG__: {
        nativeBridgeBaseUrl: "http://127.0.0.1:4817/"
      }
    });
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      statusText: "OK",
      json: async () => ({
        schema: "paradev.desktop.state.v1",
        projects: [],
        active_project: null,
        browser: null,
        templates: null,
        diagnostics: []
      })
    });
    vi.stubGlobal("fetch", fetchMock);

    expect(hasDesktopBackend()).toBe(true);
    await loadDesktopState("/tmp/PIHC3", { includeBrowser: false });

    expect(fetchMock).toHaveBeenCalledWith(
      "http://127.0.0.1:4817/desktop/state?project_path=%2Ftmp%2FPIHC3&include_browser=false",
      { method: "GET" }
    );
  });

  it("ignores a cross-origin runtime bridge injection", () => {
    vi.stubGlobal("window", {
      location: { origin: "http://127.0.0.1:4817" },
      __PARADEV_RUNTIME_CONFIG__: {
        nativeBridgeBaseUrl: "https://paradev.example"
      }
    });

    expect(hasDesktopBackend()).toBe(false);
  });

  it("reads and writes selected config values through the native web bridge", async () => {
    installNativeBridge();
    nativeBridgePayloadMock.mockResolvedValueOnce({
      schema: "paradev.desktop.config-value.v1",
      key: "paradev.build.parallelism",
      value: 4
    });
    nativeBridgePayloadMock.mockResolvedValueOnce({
      schema: "paradev.desktop.config-value.v1",
      key: "paradev.build.parallelism",
      value: 6
    });
    nativeBridgePayloadMock.mockResolvedValueOnce({
      schema: "paradev.desktop.config-value.v1",
      key: "paradev.hoi4.launch_mode",
      value: "local"
    });
    nativeBridgePayloadMock.mockResolvedValueOnce({
      schema: "paradev.desktop.config-value.v1",
      key: "paradev.hoi4.game_root",
      value: "/Games/Hearts of Iron IV"
    });
    nativeBridgePayloadMock.mockResolvedValueOnce({
      schema: "paradev.desktop.config-value.v1",
      key: "paradev.cli.output",
      value: "json"
    });
    nativeBridgePayloadMock.mockResolvedValueOnce({
      schema: "paradev.desktop.config-value.v1",
      key: "paradev.ai.key_env",
      value: "VISIBLE_DEEPSEEK_KEY"
    });
    nativeBridgePayloadMock.mockResolvedValueOnce({
      schema: "paradev.desktop.config-value.v1",
      key: "paradev.ai.model",
      value: "deepseek-reasoner"
    });
    nativeBridgePayloadMock.mockResolvedValueOnce({
      schema: "paradev.desktop.config-value.v1",
      key: "paradev.ai.preset",
      value: "reason"
    });
    nativeBridgePayloadMock.mockResolvedValueOnce({
      schema: "paradev.desktop.config-value.v1",
      key: "paradev.ai.provider",
      value: "deepseek"
    });
    nativeBridgePayloadMock.mockResolvedValueOnce({
      schema: "paradev.desktop.config-value.v1",
      key: "paradev.ai.gateway",
      value: "openrouter"
    });
    nativeBridgePayloadMock.mockResolvedValueOnce({
      schema: "paradev.desktop.config-value.v1",
      key: "paradev.ai.base_url",
      value: "https://proxy.example/v1"
    });
    nativeBridgePayloadMock.mockResolvedValueOnce({
      schema: "paradev.desktop.config-value.v1",
      key: "paradev.ai.chat.default_role",
      value: "build"
    });
    nativeBridgePayloadMock.mockResolvedValueOnce({
      schema: "paradev.desktop.config-value.v1",
      key: "paradev.project.name",
      value: "PIHC3 Workbench"
    });
    nativeBridgePayloadMock.mockResolvedValueOnce({
      schema: "paradev.desktop.config-value.v1",
      key: "paradev.desktop.thumbnail_cache.max_kb",
      value: 512
    });

    await expect(readConfigValue("paradev.build.parallelism")).resolves.toBe(4);
    await expect(writeConfigValue("paradev.build.parallelism", 6)).resolves.toBe(6);
    await expect(writeConfigValue("paradev.hoi4.launch_mode", "local")).resolves.toBe("local");
    await expect(writeConfigValue("paradev.hoi4.game_root", "/Games/Hearts of Iron IV")).resolves.toBe("/Games/Hearts of Iron IV");
    await expect(readConfigValue("paradev.cli.output")).resolves.toBe("json");
    await expect(writeConfigValue("paradev.ai.key_env", "VISIBLE_DEEPSEEK_KEY")).resolves.toBe("VISIBLE_DEEPSEEK_KEY");
    await expect(writeConfigValue("paradev.ai.model", "deepseek-reasoner")).resolves.toBe("deepseek-reasoner");
    await expect(writeConfigValue("paradev.ai.preset", "reason")).resolves.toBe("reason");
    await expect(writeConfigValue("paradev.ai.provider", "deepseek")).resolves.toBe("deepseek");
    await expect(writeConfigValue("paradev.ai.gateway", "openrouter")).resolves.toBe("openrouter");
    await expect(writeConfigValue("paradev.ai.base_url", "https://proxy.example/v1")).resolves.toBe("https://proxy.example/v1");
    await expect(writeConfigValue("paradev.ai.chat.default_role", "build")).resolves.toBe("build");
    await expect(writeConfigValue("paradev.project.name", "PIHC3 Workbench")).resolves.toBe("PIHC3 Workbench");
    await expect(writeConfigValue("paradev.desktop.thumbnail_cache.max_kb", 512)).resolves.toBe(512);

  });

  it("reads and writes strict metadata config through the native web bridge", async () => {
    installNativeBridge();
    nativeBridgePayloadMock
      .mockResolvedValueOnce({
        schema: "paradev.desktop.config-value.v1",
        key: "paradev.build.strict_metadata",
        value: true
      })
      .mockResolvedValueOnce({
        schema: "paradev.desktop.config-value.v1",
        key: "paradev.build.strict_metadata",
        value: false
      });

    await expect(readConfigValue("paradev.build.strict_metadata")).resolves.toBe(true);
    await expect(writeConfigValue("paradev.build.strict_metadata", false)).resolves.toBe(false);

  });

  it("rejects SDK-backed config values outside the desktop backend", async () => {
    vi.stubGlobal("window", {});

    await expect(readConfigValue("paradev.build.strict_metadata")).rejects.toThrow("Reading ParaDev config values requires the ParaDev desktop application.");
    await expect(writeConfigValue("paradev.build.strict_metadata", false)).rejects.toThrow(
      "Writing ParaDev config values requires the ParaDev desktop application."
    );
  });

  it("reads and writes strict metadata config through the native web bridge", async () => {
    vi.stubGlobal("window", {});
    vi.stubEnv("VITE_PARADEV_NATIVE_BRIDGE_URL", "http://127.0.0.1:47831");
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce({
        ok: true,
        status: 200,
        statusText: "OK",
        json: async () => ({ schema: "paradev.desktop.config-value.v1", key: "paradev.build.strict_metadata", value: true })
      })
      .mockResolvedValueOnce({
        ok: true,
        status: 200,
        statusText: "OK",
        json: async () => ({ schema: "paradev.desktop.config-value.v1", key: "paradev.build.strict_metadata", value: false })
      });
    vi.stubGlobal("fetch", fetchMock);

    await expect(readConfigValue("paradev.build.strict_metadata")).resolves.toBe(true);
    await expect(writeConfigValue("paradev.build.strict_metadata", false)).resolves.toBe(false);

    expect(fetchMock).toHaveBeenNthCalledWith(1, "http://127.0.0.1:47831/desktop/config-value?key=paradev.build.strict_metadata", {
      method: "GET"
    });
    expect(fetchMock).toHaveBeenNthCalledWith(2, "http://127.0.0.1:47831/desktop/config-value", {
      body: JSON.stringify({ key: "paradev.build.strict_metadata", value: false }),
      headers: { "content-type": "application/json" },
      method: "PUT"
    });
  });

  it("reads and writes selected config values through the native web bridge", async () => {
    vi.stubGlobal("window", {});
    vi.stubEnv("VITE_PARADEV_NATIVE_BRIDGE_URL", "http://127.0.0.1:47831");
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce({
        ok: true,
        status: 200,
        statusText: "OK",
        json: async () => ({ schema: "paradev.desktop.config-value.v1", key: "paradev.build.parallelism", value: 4 })
      })
      .mockResolvedValueOnce({
        ok: true,
        status: 200,
        statusText: "OK",
        json: async () => ({ schema: "paradev.desktop.config-value.v1", key: "paradev.build.parallelism", value: 8 })
      })
      .mockResolvedValueOnce({
        ok: true,
        status: 200,
        statusText: "OK",
        json: async () => ({ schema: "paradev.desktop.config-value.v1", key: "paradev.hoi4.launch_mode", value: "local" })
      })
      .mockResolvedValueOnce({
        ok: true,
        status: 200,
        statusText: "OK",
        json: async () => ({ schema: "paradev.desktop.config-value.v1", key: "paradev.hoi4.game_root", value: "/Games/Hearts of Iron IV" })
      })
      .mockResolvedValueOnce({
        ok: true,
        status: 200,
        statusText: "OK",
        json: async () => ({ schema: "paradev.desktop.config-value.v1", key: "paradev.cli.output", value: "json" })
      })
      .mockResolvedValueOnce({
        ok: true,
        status: 200,
        statusText: "OK",
        json: async () => ({ schema: "paradev.desktop.config-value.v1", key: "paradev.ai.key_env", value: "VISIBLE_DEEPSEEK_KEY" })
      })
      .mockResolvedValueOnce({
        ok: true,
        status: 200,
        statusText: "OK",
        json: async () => ({ schema: "paradev.desktop.config-value.v1", key: "paradev.ai.model", value: "deepseek-reasoner" })
      })
      .mockResolvedValueOnce({
        ok: true,
        status: 200,
        statusText: "OK",
        json: async () => ({ schema: "paradev.desktop.config-value.v1", key: "paradev.ai.preset", value: "reason" })
      })
      .mockResolvedValueOnce({
        ok: true,
        status: 200,
        statusText: "OK",
        json: async () => ({ schema: "paradev.desktop.config-value.v1", key: "paradev.ai.provider", value: "deepseek" })
      })
      .mockResolvedValueOnce({
        ok: true,
        status: 200,
        statusText: "OK",
        json: async () => ({ schema: "paradev.desktop.config-value.v1", key: "paradev.ai.gateway", value: "openrouter" })
      })
      .mockResolvedValueOnce({
        ok: true,
        status: 200,
        statusText: "OK",
        json: async () => ({ schema: "paradev.desktop.config-value.v1", key: "paradev.ai.base_url", value: "https://proxy.example/v1" })
      })
      .mockResolvedValueOnce({
        ok: true,
        status: 200,
        statusText: "OK",
        json: async () => ({ schema: "paradev.desktop.config-value.v1", key: "paradev.ai.chat.default_role", value: "build" })
      })
      .mockResolvedValueOnce({
        ok: true,
        status: 200,
        statusText: "OK",
        json: async () => ({ schema: "paradev.desktop.config-value.v1", key: "paradev.project.name", value: "PIHC3 Workbench" })
      })
      .mockResolvedValueOnce({
        ok: true,
        status: 200,
        statusText: "OK",
        json: async () => ({ schema: "paradev.desktop.config-value.v1", key: "paradev.desktop.thumbnail_cache.max_kb", value: 512 })
      });
    vi.stubGlobal("fetch", fetchMock);

    await expect(readConfigValue("paradev.build.parallelism")).resolves.toBe(4);
    await expect(writeConfigValue("paradev.build.parallelism", 8)).resolves.toBe(8);
    await expect(writeConfigValue("paradev.hoi4.launch_mode", "local")).resolves.toBe("local");
    await expect(writeConfigValue("paradev.hoi4.game_root", "/Games/Hearts of Iron IV")).resolves.toBe("/Games/Hearts of Iron IV");
    await expect(readConfigValue("paradev.cli.output")).resolves.toBe("json");
    await expect(writeConfigValue("paradev.ai.key_env", "VISIBLE_DEEPSEEK_KEY")).resolves.toBe("VISIBLE_DEEPSEEK_KEY");
    await expect(writeConfigValue("paradev.ai.model", "deepseek-reasoner")).resolves.toBe("deepseek-reasoner");
    await expect(writeConfigValue("paradev.ai.preset", "reason")).resolves.toBe("reason");
    await expect(writeConfigValue("paradev.ai.provider", "deepseek")).resolves.toBe("deepseek");
    await expect(writeConfigValue("paradev.ai.gateway", "openrouter")).resolves.toBe("openrouter");
    await expect(writeConfigValue("paradev.ai.base_url", "https://proxy.example/v1")).resolves.toBe("https://proxy.example/v1");
    await expect(writeConfigValue("paradev.ai.chat.default_role", "build")).resolves.toBe("build");
    await expect(writeConfigValue("paradev.project.name", "PIHC3 Workbench")).resolves.toBe("PIHC3 Workbench");
    await expect(writeConfigValue("paradev.desktop.thumbnail_cache.max_kb", 512)).resolves.toBe(512);

    expect(fetchMock).toHaveBeenNthCalledWith(1, "http://127.0.0.1:47831/desktop/config-value?key=paradev.build.parallelism", {
      method: "GET"
    });
    expect(fetchMock).toHaveBeenNthCalledWith(2, "http://127.0.0.1:47831/desktop/config-value", {
      body: JSON.stringify({ key: "paradev.build.parallelism", value: 8 }),
      headers: { "content-type": "application/json" },
      method: "PUT"
    });
    expect(fetchMock).toHaveBeenNthCalledWith(3, "http://127.0.0.1:47831/desktop/config-value", {
      body: JSON.stringify({ key: "paradev.hoi4.launch_mode", value: "local" }),
      headers: { "content-type": "application/json" },
      method: "PUT"
    });
    expect(fetchMock).toHaveBeenNthCalledWith(4, "http://127.0.0.1:47831/desktop/config-value", {
      body: JSON.stringify({ key: "paradev.hoi4.game_root", value: "/Games/Hearts of Iron IV" }),
      headers: { "content-type": "application/json" },
      method: "PUT"
    });
    expect(fetchMock).toHaveBeenNthCalledWith(5, "http://127.0.0.1:47831/desktop/config-value?key=paradev.cli.output", {
      method: "GET"
    });
    expect(fetchMock).toHaveBeenNthCalledWith(6, "http://127.0.0.1:47831/desktop/config-value", {
      body: JSON.stringify({ key: "paradev.ai.key_env", value: "VISIBLE_DEEPSEEK_KEY" }),
      headers: { "content-type": "application/json" },
      method: "PUT"
    });
    expect(fetchMock).toHaveBeenNthCalledWith(7, "http://127.0.0.1:47831/desktop/config-value", {
      body: JSON.stringify({ key: "paradev.ai.model", value: "deepseek-reasoner" }),
      headers: { "content-type": "application/json" },
      method: "PUT"
    });
    expect(fetchMock).toHaveBeenNthCalledWith(8, "http://127.0.0.1:47831/desktop/config-value", {
      body: JSON.stringify({ key: "paradev.ai.preset", value: "reason" }),
      headers: { "content-type": "application/json" },
      method: "PUT"
    });
    expect(fetchMock).toHaveBeenNthCalledWith(9, "http://127.0.0.1:47831/desktop/config-value", {
      body: JSON.stringify({ key: "paradev.ai.provider", value: "deepseek" }),
      headers: { "content-type": "application/json" },
      method: "PUT"
    });
    expect(fetchMock).toHaveBeenNthCalledWith(10, "http://127.0.0.1:47831/desktop/config-value", {
      body: JSON.stringify({ key: "paradev.ai.gateway", value: "openrouter" }),
      headers: { "content-type": "application/json" },
      method: "PUT"
    });
    expect(fetchMock).toHaveBeenNthCalledWith(11, "http://127.0.0.1:47831/desktop/config-value", {
      body: JSON.stringify({ key: "paradev.ai.base_url", value: "https://proxy.example/v1" }),
      headers: { "content-type": "application/json" },
      method: "PUT"
    });
    expect(fetchMock).toHaveBeenNthCalledWith(12, "http://127.0.0.1:47831/desktop/config-value", {
      body: JSON.stringify({ key: "paradev.ai.chat.default_role", value: "build" }),
      headers: { "content-type": "application/json" },
      method: "PUT"
    });
    expect(fetchMock).toHaveBeenNthCalledWith(13, "http://127.0.0.1:47831/desktop/config-value", {
      body: JSON.stringify({ key: "paradev.project.name", value: "PIHC3 Workbench" }),
      headers: { "content-type": "application/json" },
      method: "PUT"
    });
    expect(fetchMock).toHaveBeenNthCalledWith(14, "http://127.0.0.1:47831/desktop/config-value", {
      body: JSON.stringify({ key: "paradev.desktop.thumbnail_cache.max_kb", value: 512 }),
      headers: { "content-type": "application/json" },
      method: "PUT"
    });
  });

  it("loads project browser and source text through generated REST planning in the native web bridge", async () => {
    vi.stubGlobal("window", {});
    vi.stubEnv("VITE_PARADEV_NATIVE_BRIDGE_URL", "http://127.0.0.1:47831");
    const browserPayload: ProjectBrowserPayload = {
      schema: "paradev.sdk.project-browser.v1",
      project_id: "PIHC3",
      title: "PIHC3",
      root: "/tmp/PIHC3",
      profile: "hoi4",
      filters: {},
      families: [],
      items: [],
      diagnostics: []
    };
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce({
        ok: true,
        status: 200,
        statusText: "OK",
        json: async () => browserPayload
      })
      .mockResolvedValueOnce({
        ok: true,
        status: 200,
        statusText: "OK",
        json: async () => ({
          schema: "paradev.sdk.frontend-api.rest-request.v1",
          operation_id: "project.source_text",
          method: "GET",
          path: "/projects/PIHC3/sources",
          query: {
            path: "src/focus_tree/GER_main/def.txt",
            project_root: "/tmp/PIHC3"
          },
          body: {},
          binding: {
            method: "GET",
            path: "/projects/{project_id}/sources",
            query: {}
          },
          normalized: {
            schema: "paradev.sdk.frontend-api.inputs.v1",
            operation_id: "project.source_text",
            values: {},
            project: { path: "/tmp/PIHC3" },
            parameters: {},
            selectors: {},
            projections: {}
          }
        })
      })
      .mockResolvedValueOnce({
        ok: true,
        status: 200,
        statusText: "OK",
        json: async () => ({ text: "focus = {}\n" })
      });
    vi.stubGlobal("fetch", fetchMock);

    await loadProjectBrowser({ projectRoot: "/tmp/PIHC3", family: "focus_tree", moduleId: "GER_main", summary: true });
    const text = await readTextSource("/tmp/PIHC3", "src/focus_tree/GER_main/def.txt", browserPayload.project_id);

    expect(text).toBe("focus = {}\n");
    expect(fetchMock).toHaveBeenNthCalledWith(
      1,
      "http://127.0.0.1:47831/projects/browser?path=%2Ftmp%2FPIHC3&family=focus_tree&module_id=GER_main&summary=true",
      { method: "GET" }
    );
    expect(fetchMock).toHaveBeenNthCalledWith(2, "http://127.0.0.1:47831/frontend-api/rest-request?operation_id=project.source_text", {
      body: JSON.stringify({
        project_id: "PIHC3",
        path: "/tmp/PIHC3",
        source_path: "src/focus_tree/GER_main/def.txt"
      }),
      headers: { "Content-Type": "application/json" },
      method: "POST"
    });
    expect(fetchMock).toHaveBeenNthCalledWith(
      3,
      "http://127.0.0.1:47831/projects/PIHC3/sources?path=src%2Ffocus_tree%2FGER_main%2Fdef.txt&project_root=%2Ftmp%2FPIHC3",
      { method: "GET" }
    );
    expect(fetchMock.mock.calls.map(([url]) => url)).not.toContain("http://127.0.0.1:47831/desktop/sources/text");
  });

  it("projects source forms through a generated POST plan in the native web bridge", async () => {
    vi.stubGlobal("window", {});
    vi.stubEnv("VITE_PARADEV_NATIVE_BRIDGE_URL", "http://127.0.0.1:47831");
    const payload = validSourceFormPayload();
    const text = "";
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce({
        ok: true,
        status: 200,
        statusText: "OK",
        json: async () => ({
          schema: "paradev.sdk.frontend-api.rest-request.v1",
          operation_id: "project.source_form",
          method: "POST",
          path: "/projects/PIHC3/sources/form",
          query: {},
          body: {
            project_root: "/tmp/PIHC3",
            path: "src/modules/Entity/VIENTO_MIRROR/record.json",
            text
          },
          binding: {
            method: "POST",
            path: "/projects/{project_id}/sources/form",
            query: {}
          },
          normalized: {
            schema: "paradev.sdk.frontend-api.inputs.v1",
            operation_id: "project.source_form",
            group: "projects",
            action: "source-form",
            status: "implemented",
            read_only: true,
            values: {
              project_id: "PIHC3",
              path: "/tmp/PIHC3",
              source_path: "src/modules/Entity/VIENTO_MIRROR/record.json",
              text
            },
            project: {},
            parameters: {
              project_id: "PIHC3",
              project_root: "/tmp/PIHC3",
              path: "src/modules/Entity/VIENTO_MIRROR/record.json",
              text
            },
            selectors: {},
            projections: {},
            aliases: {
              path: "project_root",
              source_path: "path"
            }
          }
        })
      })
      .mockResolvedValueOnce({
        ok: true,
        status: 200,
        statusText: "OK",
        json: async () => payload
      });
    vi.stubGlobal("fetch", fetchMock);

    await expect(
      readProjectSourceForm({
        projectId: "PIHC3",
        projectRoot: "/tmp/PIHC3",
        sourcePath: "src/modules/Entity/VIENTO_MIRROR/record.json",
        text
      })
    ).resolves.toEqual(payload);

    expect(fetchMock).toHaveBeenNthCalledWith(1, "http://127.0.0.1:47831/frontend-api/rest-request?operation_id=project.source_form", {
      body: JSON.stringify({
        project_id: "PIHC3",
        path: "/tmp/PIHC3",
        source_path: "src/modules/Entity/VIENTO_MIRROR/record.json",
        text
      }),
      headers: { "Content-Type": "application/json" },
      method: "POST"
    });
    expect(fetchMock).toHaveBeenNthCalledWith(2, "http://127.0.0.1:47831/projects/PIHC3/sources/form", {
      body: JSON.stringify({
        project_root: "/tmp/PIHC3",
        path: "src/modules/Entity/VIENTO_MIRROR/record.json",
        text
      }),
      headers: { "Content-Type": "application/json" },
      method: "POST"
    });
    expect(fetchMock.mock.calls.every(([url]) => !String(url).includes("text="))).toBe(true);
  });

  it("plans guided update batches through the native desktop bridge", async () => {
    vi.stubGlobal("window", {});
    vi.stubEnv("VITE_PARADEV_NATIVE_BRIDGE_URL", "http://127.0.0.1:47831");
    const fetchMock = vi.fn().mockResolvedValueOnce({
      ok: true,
      status: 200,
      statusText: "OK",
      json: async () => validSourceFormUpdateBatchPayload()
    });
    vi.stubGlobal("fetch", fetchMock);
    const request = {
      projectId: "PIHC3",
      projectRoot: "/tmp/PIHC3",
      updates: [
        {
          sourcePath: "src/modules/Entity/VIENTO_MIRROR/record.json",
          text: '{"mesh":{"scale":4.25}}\n',
          values: { "mesh.scale": 4.5 }
        }
      ]
    };

    await expect(planProjectSourceFormUpdates(request)).resolves.toMatchObject({
      changed: true,
      counts: { requested: 1, changed: 1, unchanged: 0 }
    });
    expect(fetchMock).toHaveBeenCalledWith(
      "http://127.0.0.1:47831/desktop/sources/form-updates/plan",
      {
        body: JSON.stringify({
          projectId: "PIHC3",
          projectRoot: "/tmp/PIHC3",
          updates: [
            {
              sourcePath: "src/modules/Entity/VIENTO_MIRROR/record.json",
              values: { "mesh.scale": 4.5 },
              text: '{"mesh":{"scale":4.25}}\n'
            }
          ]
        }),
        headers: { "content-type": "application/json" },
        method: "POST"
      }
    );
  });

  it("runs build, opener, and HOI4 calls through the native web bridge", async () => {
    vi.stubGlobal("window", {});
    vi.stubEnv("VITE_PARADEV_NATIVE_BRIDGE_URL", "http://127.0.0.1:47831");
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce({
        ok: true,
        status: 200,
        statusText: "OK",
        json: async () => ({
          schema: "paradev.sdk.frontend-api.rest-request.v1",
          operation_id: "build.start",
          method: "POST",
          path: "/desktop/builds",
          query: {},
          body: {
            project_root: "/tmp/PIHC3",
            mode: "cached",
            parallelism: 3
          },
          binding: {
            method: "POST",
            path: "/desktop/builds",
            query: {}
          },
          normalized: {
            schema: "paradev.sdk.frontend-api.inputs.v1",
            operation_id: "build.start",
            values: {},
            project: {},
            parameters: {},
            selectors: {},
            projections: {}
          }
        })
      })
      .mockResolvedValueOnce({
        ok: true,
        status: 200,
        statusText: "OK",
        json: async () => ({
          schema: "paradev.desktop.build-run.v1",
          runId: "build-1",
          status: "running"
        })
      })
      .mockResolvedValueOnce({
        ok: true,
        status: 200,
        statusText: "OK",
        json: async () => ({
          schema: "paradev.sdk.frontend-api.rest-request.v1",
          operation_id: "build.status",
          method: "GET",
          path: "/desktop/builds/status",
          query: {
            run_id: "build-1"
          },
          body: {},
          binding: {
            method: "GET",
            path: "/desktop/builds/status",
            query: {}
          },
          normalized: {
            schema: "paradev.sdk.frontend-api.inputs.v1",
            operation_id: "build.status",
            values: {},
            project: {},
            parameters: {},
            selectors: {},
            projections: {}
          }
        })
      })
      .mockResolvedValueOnce({
        ok: true,
        status: 200,
        statusText: "OK",
        json: async () => ({
          schema: "paradev.desktop.build-run.v1",
          runId: "build-1",
          status: "completed",
          exitCode: 0
        })
      })
      .mockResolvedValueOnce({
        ok: true,
        status: 200,
        statusText: "OK",
        json: async () => ({
          schema: "paradev.sdk.frontend-api.rest-request.v1",
          operation_id: "build.interrupt",
          method: "POST",
          path: "/desktop/builds/interrupt",
          query: {},
          body: {
            run_id: "build-1"
          },
          binding: {
            method: "POST",
            path: "/desktop/builds/interrupt",
            query: {}
          },
          normalized: {
            schema: "paradev.sdk.frontend-api.inputs.v1",
            operation_id: "build.interrupt",
            values: {},
            project: {},
            parameters: {},
            selectors: {},
            projections: {}
          }
        })
      })
      .mockResolvedValueOnce({
        ok: true,
        status: 200,
        statusText: "OK",
        json: async () => ({
          schema: "paradev.desktop.build-run.v1",
          runId: "build-1",
          status: "interrupted"
        })
      })
      .mockResolvedValueOnce({
        ok: true,
        status: 200,
        statusText: "OK",
        json: async () => ({ status: "started" })
      })
      .mockResolvedValueOnce({
        ok: true,
        status: 200,
        statusText: "OK",
        json: async () => ({
          schema: "paradev.desktop.game-launch.v1",
          game: "hoi4",
          mode: "steam",
          status: "started",
          gameRoot: "steam://rungameid/394360",
          command: ["open", "steam://rungameid/394360"]
        })
      })
      .mockResolvedValueOnce({
        ok: true,
        status: 200,
        statusText: "OK",
        json: async () => ({
          schema: "paradev.desktop.dependency.v1",
          id: "imagemagick",
          label: "ImageMagick",
          installed: true,
          status: "ready",
          path: "/opt/homebrew/bin/magick",
          version: "ImageMagick 7.1.2",
          installCommand: ["brew", "install", "imagemagick"],
          installSupported: true
        })
      })
      .mockResolvedValueOnce({
        ok: true,
        status: 200,
        statusText: "OK",
        json: async () => ({
          schema: "paradev.desktop.dependency.v1",
          id: "imagemagick",
          label: "ImageMagick",
          installed: true,
          status: "ready",
          path: "/opt/homebrew/bin/magick",
          version: "ImageMagick 7.1.2",
          installCommand: ["brew", "install", "imagemagick"],
          installSupported: true
        })
      });
    vi.stubGlobal("fetch", fetchMock);

    await startProjectBuild({ projectRoot: "/tmp/PIHC3", mode: "cached", parallelism: 3 });
    await getProjectBuildStatus("build-1");
    await interruptProjectBuild("build-1");
    await openProjectPath("/tmp/PIHC3/build/mod", "finder");
    await runHoi4Game({ projectRoot: "/tmp/PIHC3", mode: "steam" });
    await checkDesktopDependency("imagemagick");
    await installDesktopDependency("imagemagick");

    expect(fetchMock).toHaveBeenNthCalledWith(1, "http://127.0.0.1:47831/frontend-api/rest-request?operation_id=build.start", {
      body: JSON.stringify({ project_root: "/tmp/PIHC3", mode: "cached", parallelism: 3 }),
      headers: { "Content-Type": "application/json" },
      method: "POST"
    });
    expect(fetchMock).toHaveBeenNthCalledWith(2, "http://127.0.0.1:47831/desktop/builds", {
      body: JSON.stringify({ project_root: "/tmp/PIHC3", mode: "cached", parallelism: 3 }),
      headers: { "Content-Type": "application/json" },
      method: "POST"
    });
    expect(fetchMock).toHaveBeenNthCalledWith(3, "http://127.0.0.1:47831/frontend-api/rest-request?operation_id=build.status", {
      body: JSON.stringify({ run_id: "build-1" }),
      headers: { "Content-Type": "application/json" },
      method: "POST"
    });
    expect(fetchMock).toHaveBeenNthCalledWith(4, "http://127.0.0.1:47831/desktop/builds/status?run_id=build-1", {
      method: "GET"
    });
    expect(fetchMock).toHaveBeenNthCalledWith(5, "http://127.0.0.1:47831/frontend-api/rest-request?operation_id=build.interrupt", {
      body: JSON.stringify({ run_id: "build-1" }),
      headers: { "Content-Type": "application/json" },
      method: "POST"
    });
    expect(fetchMock).toHaveBeenNthCalledWith(6, "http://127.0.0.1:47831/desktop/builds/interrupt", {
      body: JSON.stringify({ run_id: "build-1" }),
      headers: { "Content-Type": "application/json" },
      method: "POST"
    });
    expect(fetchMock).toHaveBeenNthCalledWith(7, "http://127.0.0.1:47831/desktop/open-path", {
      body: JSON.stringify({ path: "/tmp/PIHC3/build/mod", target: "finder" }),
      headers: { "content-type": "application/json" },
      method: "POST"
    });
    expect(fetchMock).toHaveBeenNthCalledWith(8, "http://127.0.0.1:47831/desktop/run-hoi4", {
      body: JSON.stringify({ projectRoot: "/tmp/PIHC3", mode: "steam" }),
      headers: { "content-type": "application/json" },
      method: "POST"
    });
    expect(fetchMock).toHaveBeenNthCalledWith(9, "http://127.0.0.1:47831/desktop/dependencies/imagemagick", {
      method: "GET"
    });
    expect(fetchMock).toHaveBeenNthCalledWith(10, "http://127.0.0.1:47831/desktop/dependencies/imagemagick/install", {
      body: JSON.stringify({}),
      headers: { "content-type": "application/json" },
      method: "POST"
    });
  });

  it("lists active builds through generated REST planning in the native web bridge", async () => {
    vi.stubGlobal("window", {});
    vi.stubEnv("VITE_PARADEV_NATIVE_BRIDGE_URL", "http://127.0.0.1:47831");
    const payload = {
      schema: "paradev.desktop.build-runs.v1",
      runs: [
        {
          schema: "paradev.desktop.build-run.v1",
          projectRoot: "/tmp/PIHC3",
          runId: "build-1",
          status: "running"
        }
      ]
    } as const;
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce({
        ok: true,
        status: 200,
        statusText: "OK",
        json: async () => ({
          schema: "paradev.sdk.frontend-api.rest-request.v1",
          operation_id: "build.runs",
          method: "GET",
          path: "/desktop/builds",
          query: { project_root: "/tmp/PIHC3" },
          body: {},
          binding: {
            method: "GET",
            path: "/desktop/builds",
            query: {}
          },
          normalized: {
            schema: "paradev.sdk.frontend-api.inputs.v1",
            operation_id: "build.runs",
            values: {},
            project: {},
            parameters: { project_root: "/tmp/PIHC3" },
            selectors: {},
            projections: {}
          }
        })
      })
      .mockResolvedValueOnce({
        ok: true,
        status: 200,
        statusText: "OK",
        json: async () => payload
      })
      .mockResolvedValueOnce({
        ok: true,
        status: 200,
        statusText: "OK",
        json: async () => ({
          schema: "paradev.sdk.frontend-api.rest-request.v1",
          operation_id: "build.runs",
          method: "GET",
          path: "/desktop/builds",
          query: {},
          body: {},
          binding: {
            method: "GET",
            path: "/desktop/builds",
            query: {}
          },
          normalized: {
            schema: "paradev.sdk.frontend-api.inputs.v1",
            operation_id: "build.runs",
            values: {},
            project: {},
            parameters: {},
            selectors: {},
            projections: {}
          }
        })
      })
      .mockResolvedValueOnce({
        ok: true,
        status: 200,
        statusText: "OK",
        json: async () => ({ schema: "paradev.desktop.build-runs.v1", runs: [] })
      });
    vi.stubGlobal("fetch", fetchMock);

    await expect(getProjectBuildRuns("/tmp/PIHC3")).resolves.toEqual(payload);
    await expect(getProjectBuildRuns()).resolves.toEqual({ schema: "paradev.desktop.build-runs.v1", runs: [] });

    expect(fetchMock).toHaveBeenNthCalledWith(1, "http://127.0.0.1:47831/frontend-api/rest-request?operation_id=build.runs", {
      body: JSON.stringify({ project_root: "/tmp/PIHC3" }),
      headers: { "Content-Type": "application/json" },
      method: "POST"
    });
    expect(fetchMock).toHaveBeenNthCalledWith(2, "http://127.0.0.1:47831/desktop/builds?project_root=%2Ftmp%2FPIHC3", {
      method: "GET"
    });
    expect(fetchMock).toHaveBeenNthCalledWith(3, "http://127.0.0.1:47831/frontend-api/rest-request?operation_id=build.runs", {
      body: JSON.stringify({}),
      headers: { "Content-Type": "application/json" },
      method: "POST"
    });
    expect(fetchMock).toHaveBeenNthCalledWith(4, "http://127.0.0.1:47831/desktop/builds", {
      method: "GET"
    });
  });
});
