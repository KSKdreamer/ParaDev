import { describe, expect, it } from "vitest";
import {
  applyAssetDrafts,
  applyAssetReplacementPlanToEntity,
  applyImageReplacementPlanToEntity,
  applyGuidedTextDraft,
  applyScaffoldPlanToEntity,
  applySourceTextPlanToEntity,
  applyImageDraft,
  applyInfoDraft,
  applyTextDraft,
  buildModuleEntitySelectionState,
  buildCreateDraftInput,
  buildModuleEntities,
  buildTemplateCreateFields,
  canApplyAssetDraft,
  canApplyImageDraft,
  canApplyInfoDraft,
  canApplySourceTextDraft,
  canApplyRemovalDraft,
  canApplyScaffoldDraft,
  canPreviewImageSourceInEditor,
  createDraftEntity,
  defaultAssetDraftPath,
  assetDraftTargetsForFile,
  filterAndSortEntities,
  defaultImageDraftPath,
  hasBlockingAssetDraft,
  moduleEntityThumbnailCacheKey,
  moduleEntityThumbnailSource,
  moduleTitleLocalizationTarget,
  markEntitiesForRemoval,
  mergeModuleEntitiesPreservingDrafts,
  type ModuleSourceSlot,
  resolveModuleEntityQueryAfterExternalSelection,
  resolveModuleEntitySelection,
  selectCollectionCreateTemplates,
  selectCreateTemplates,
  selectCreateTemplate,
  selectModuleEntityScope,
  selectModuleEntityRange,
  sourceReplacementsForEntity,
  sourceFormUpdatesForEntity,
  sourceAssetReplacementsForEntity,
  sourceTextEditsForEntity,
  sourceTextEditsWithSourceFormPlan,
  supportsAssetDrafts,
  templateCreateReferenceOptions,
  shouldRefreshAfterScaffoldApply,
  updateMetadataTitleText,
} from "./model";
import type {
  DraftApplyPayload,
  ModuleScaffoldPlan,
  ProjectBrowserPayload,
  ProjectBrowserSource,
  ProjectTemplate,
  ProjectTemplatesPayload,
  SourceFormUpdateBatchPlan,
} from "../types";
import {
  buildProcessedPngImageDraft,
  pngDraftFileName,
  rawBase64ImagePayload,
} from "./imageDraft";

const browser: ProjectBrowserPayload = {
  schema: "paradev.sdk.project-browser.v1",
  project_id: "PIHC3",
  title: "The Pony In The High Castle",
  root: "/workspace/projects/PIHC3",
  profile: "hoi4",
  filters: {},
  diagnostics: [],
  families: [
    {
      id: "ideas",
      family: "idea",
      title: "Ideas",
      item_count: 2,
      source_count: 5,
      layouts: ["canonical"],
    },
  ],
  items: [
    {
      id: "ideas:IDEA_ALPHA",
      kind: "module",
      layout: "canonical",
      family_id: "ideas",
      family: "idea",
      object_id: "IDEA_ALPHA",
      module_id: "IDEA_ALPHA",
      collection_id: "C01_ideas",
      title: "Alpha Idea",
      localized_titles: {
        l_english: "Alpha Idea",
        l_simp_chinese: "Alpha Idea CN",
      },
      title_keys: ["IDEA_ALPHA"],
      root: "/workspace/projects/PIHC3/src/modules/idea/IDEA_ALPHA",
      relative_root: "src/modules/idea/IDEA_ALPHA",
      source_count: 2,
      sources: [
        {
          slot: "def",
          name: "def.pdx",
          path: "/workspace/projects/PIHC3/src/modules/idea/IDEA_ALPHA/def.pdx",
          relative_path: "src/modules/idea/IDEA_ALPHA/def.pdx",
          extension: "pdx",
        },
        {
          slot: "loc",
          name: "main.loc",
          path: "/workspace/projects/PIHC3/src/modules/idea/IDEA_ALPHA/main.loc",
          relative_path: "src/modules/idea/IDEA_ALPHA/main.loc",
          extension: "loc",
        },
      ],
    },
    {
      id: "ideas:IDEA_BETA",
      kind: "module",
      layout: "family_root",
      family_id: "ideas",
      family: "idea",
      object_id: "IDEA_BETA",
      title: "Beta Law",
      root: "/workspace/projects/PIHC3/src/common/ideas",
      relative_root: "src/common/ideas",
      source_count: 3,
      sources: [
        {
          slot: "def",
          name: "ideas.pdx",
          path: "/workspace/projects/PIHC3/src/common/ideas/ideas.pdx",
          relative_path: "src/common/ideas/ideas.pdx",
          extension: "pdx",
        },
        {
          slot: "icon",
          name: "GFX_idea_beta.dds",
          path: "/workspace/projects/PIHC3/src/gfx/interface/ideas/GFX_idea_beta.dds",
          relative_path: "src/gfx/interface/ideas/GFX_idea_beta.dds",
          extension: "dds",
        },
        {
          slot: "loc",
          name: "ideas_l_english.yml",
          path: "/workspace/projects/PIHC3/src/localisation/english/ideas_l_english.yml",
          relative_path: "src/localisation/english/ideas_l_english.yml",
          extension: "yml",
        },
      ],
    },
  ],
};

function source(
  slot: string,
  name: string,
  relativePath: string,
  size?: number,
): ProjectBrowserSource {
  return {
    slot,
    ...(["assets", "compiled_assets", "meshes"].includes(slot)
      ? { slot_kinds: ["copy"] }
      : {}),
    name,
    path: `/workspace/projects/PIHC3/${relativePath}`,
    relative_path: relativePath,
    extension: name.split(".").at(-1) ?? "",
    ...(size === undefined ? {} : { size }),
  };
}

function entityResourceSlots() {
  return [
    {
      name: "meshes",
      match: "^gfx/models/.*\\.mesh$",
      required: false,
      many: true,
      regex: true,
      kind: "copy",
      shared: false,
      authoring_path: "gfx/models/{object_id}/{filename}",
    },
    {
      name: "animations",
      match: "^gfx/models/.*\\.anim$",
      required: false,
      many: true,
      regex: true,
      kind: "copy",
      shared: false,
      authoring_path: "gfx/models/{object_id}/{filename}",
    },
    {
      name: "textures",
      match: "^gfx/models/.*\\.(dds|png|tga)$",
      required: false,
      many: true,
      regex: true,
      kind: "copy",
      shared: false,
      authoring_path: "gfx/models/{object_id}/{filename}",
    },
  ];
}

function pngImageEntity() {
  const entity = buildModuleEntities(browser, "ideas")[1];
  return {
    ...entity,
    sourceSlots: entity.sourceSlots.map((source) =>
      source.editorKind === "image"
        ? {
            ...source,
            name: source.name.replace(/\.dds$/i, ".png"),
            path: source.path.replace(/\.dds$/i, ".png"),
            relative_path: source.relative_path.replace(/\.dds$/i, ".png"),
            extension: "png",
          }
        : source,
    ),
  };
}

const templates: ProjectTemplatesPayload = {
  schema: "paradev.sdk.templates.v1",
  project_id: "PIHC3",
  profile: "hoi4",
  templates: [
    {
      id: "hoi4:idea/basic",
      title: "Basic HoI4 Idea",
      family: "idea",
      source: "builtin",
      args: {
        title: { required: false, default: "", advanced: false },
        description: { required: false, default: "", advanced: false },
        category: { required: false, default: "country", advanced: true },
        language: { required: false, default: "en", advanced: true },
      },
      files: ["meta.yaml", "def.pdx", "main.loc"],
    },
    {
      id: "pihc3:idea/legacy-current",
      title: "PIHC3 Legacy-Compatible Idea",
      family: "idea",
      source: "project",
      args: {
        legacy_tag: {
          required: false,
          default: "{family_tag}",
          advanced: true,
        },
        title: { required: true, default: "", advanced: false },
        description: { required: false, default: "", advanced: false },
        category: { required: false, default: "country", advanced: true },
        language: { required: false, default: "en", advanced: true },
      },
      files: ["meta.yaml", "def.pdx", "main.loc"],
    },
  ],
};

const multiTemplatePayload: ProjectTemplatesPayload = {
  ...templates,
  templates: [
    ...templates.templates,
    {
      id: "pihc3:idea/category-law",
      title: "PIHC3 Idea Category Law",
      family: "idea",
      source: "project",
      args: {
        title: { required: true, default: "", advanced: false },
        category: { required: false, default: "law", advanced: true },
      },
      files: ["meta.yaml", "def.pdx"],
    },
  ],
};

describe("module editor model", () => {
  it("normalizes processed editor image output as a png draft", () => {
    expect(pngDraftFileName("GFX_idea_beta.dds")).toBe("GFX_idea_beta.png");
    expect(
      pngDraftFileName("https://example.test/assets/icon.jpg?cache=1"),
    ).toBe("icon.png");
    expect(pngDraftFileName("data:image/png;base64,cHJvY2Vzc2Vk")).toBe(
      "image.png",
    );
    expect(rawBase64ImagePayload("data:image/png;base64,cHJvY2Vzc2Vk")).toBe(
      "cHJvY2Vzc2Vk",
    );

    expect(
      buildProcessedPngImageDraft({
        imageData: {
          name: "GFX_idea_beta",
          extension: "png",
          mimeType: "image/png",
          imageBase64: "data:image/png;base64,cHJvY2Vzc2Vk",
          width: 64,
          height: 64,
        },
        previewUrl: "data:image/png;base64,cHJvY2Vzc2Vk",
        sourceName: "GFX_idea_beta.dds",
      }),
    ).toEqual({
      fileName: "GFX_idea_beta.png",
      previewUrl: "data:image/png;base64,cHJvY2Vzc2Vk",
      contentBase64: "cHJvY2Vzc2Vk",
      width: 64,
      height: 64,
    });
  });

  it("builds generic module entities with titles, ids, source slots, and empty default tags", () => {
    const entities = buildModuleEntities(browser, "ideas");

    expect(entities).toHaveLength(2);
    expect(entities[0]).toMatchObject({
      id: "ideas:IDEA_ALPHA",
      familyId: "ideas",
      objectId: "IDEA_ALPHA",
      collectionId: "C01_ideas",
      title: "Alpha Idea",
      subtitle: "IDEA_ALPHA",
      relativeRoot: "src/modules/idea/IDEA_ALPHA",
      draftState: "clean",
    });
    expect(entities[0].sourceSlots.map((slot) => slot.slot)).toEqual([
      "def",
      "loc",
    ]);
    expect(entities[0].sourceSlots.map((slot) => slot.draftKey)).toEqual([
      "def",
      "loc",
    ]);
    expect(entities[0].sourceSlots.map((slot) => slot.editorKind)).toEqual([
      "code",
      "localization",
    ]);
    expect(entities[0].tags).toEqual([]);
    expect(entities[1].tags).toEqual([]);
  });

  it("gives duplicate slots stable path-qualified draft keys and applies each file independently", () => {
    const englishPath = "src/modules/idea/IDEA_ALPHA/english.loc";
    const chinesePath = "src/modules/idea/IDEA_ALPHA/chinese.loc";
    const duplicateSlotBrowser: ProjectBrowserPayload = {
      ...browser,
      items: [
        {
          ...browser.items[0],
          source_count: 2,
          sources: [
            {
              slot: "loc",
              name: "english.loc",
              path: `/workspace/projects/PIHC3/${englishPath}`,
              relative_path: englishPath,
              extension: "loc",
            },
            {
              slot: "loc",
              name: "chinese.loc",
              path: `/workspace/projects/PIHC3/${chinesePath}`,
              relative_path: chinesePath,
              extension: "loc",
            },
          ],
        },
      ],
    };
    const [entity] = buildModuleEntities(duplicateSlotBrowser, "ideas");
    const englishKey = `loc::${englishPath}`;
    const chineseKey = `loc::${chinesePath}`;

    expect(entity.sourceSlots.map((source) => source.draftKey)).toEqual([
      englishKey,
      chineseKey,
    ]);

    const edited = applyTextDraft(
      applyTextDraft(entity, englishKey, 'l_english:\n IDEA_ALPHA:0 "Alpha"\n'),
      chineseKey,
      'l_simp_chinese:\n IDEA_ALPHA:0 "阿尔法"\n',
    );
    expect(sourceTextEditsForEntity(edited)).toEqual([
      {
        path: `/workspace/projects/PIHC3/${englishPath}`,
        text: 'l_english:\n IDEA_ALPHA:0 "Alpha"\n',
      },
      {
        path: `/workspace/projects/PIHC3/${chinesePath}`,
        text: 'l_simp_chinese:\n IDEA_ALPHA:0 "阿尔法"\n',
      },
    ]);

    const applied = applySourceTextPlanToEntity(edited, {
      schema: "paradev.rest.draft_apply.v1",
      project_id: "PIHC3",
      written: true,
      files: [
        {
          path: `/workspace/projects/PIHC3/${englishPath}`,
          relative_path: englishPath,
          operation: "write_text",
          encoding: "utf-8",
        },
      ],
    });

    expect(applied.drafts.text).toEqual({
      [chineseKey]: 'l_simp_chinese:\n IDEA_ALPHA:0 "阿尔法"\n',
    });
    expect(applied.draftState).toBe("modified");
  });

  it("retains accumulated guided intent and merges only the Registry-owned edit", () => {
    const [entity] = buildModuleEntities(browser, "ideas");
    const revised = {
      ...entity,
      sourceSlots: entity.sourceSlots.map((source, index) => ({
        ...source,
        size: 100 + index,
        mtime_ns: `${1_000 + index}`,
      })),
    };
    const baseText = "idea = {\n  enabled = yes\n  cost = 1\n}\n";
    const firstText = "idea = {\n  enabled = no\n  cost = 1\n}\n";
    const finalText = "idea = {\n  enabled = no\n  cost = 2\n}\n";
    const first = applyGuidedTextDraft(revised, "def", {
      baseText,
      controlId: "enabled",
      text: firstText,
      value: false,
    });
    const guided = applyGuidedTextDraft(first, "def", {
      baseText: firstText,
      controlId: "cost",
      text: finalText,
      value: 2,
    });

    expect(sourceFormUpdatesForEntity(guided)).toEqual([
      {
        sourceKey: "def",
        sourcePath: revised.sourceSlots[0].path,
        text: baseText,
        values: { enabled: false, cost: 2 },
      },
    ]);

    const plannedEdit = {
      path: revised.sourceSlots[0].path,
      text: finalText,
      expectedSize: 100,
      expectedMtimeNs: "1000",
    };
    const plan = {
      schema: "paradev.source-form-update-batch.v1",
      projectId: "PIHC3",
      changed: true,
      counts: { requested: 1, changed: 1, unchanged: 0 },
      updates: [
        {
          schema: "paradev.source-form-update.v1",
          projectId: "PIHC3",
          family: "idea",
          moduleId: "IDEA_ALPHA",
          path: revised.sourceSlots[0].path,
          relativePath: revised.sourceSlots[0].relative_path,
          sourceFormat: "pdx",
          formContract: "test.idea.v1",
          changed: true,
          changes: [
            { controlId: "enabled", previous: true, value: false },
            { controlId: "cost", previous: 1, value: 2 },
          ],
          sourceEdit: plannedEdit,
        },
      ],
      sourceEdits: [plannedEdit],
    } satisfies SourceFormUpdateBatchPlan;

    expect(sourceTextEditsWithSourceFormPlan(guided, plan)).toEqual({
      ok: true,
      sourceEdits: [plannedEdit],
    });
    expect(
      sourceTextEditsWithSourceFormPlan(guided, {
        ...plan,
        updates: [
          {
            ...plan.updates[0],
            sourceEdit: { ...plannedEdit, text: `${finalText}# stale\n` },
          },
        ],
        sourceEdits: [{ ...plannedEdit, text: `${finalText}# stale\n` }],
      }),
    ).toEqual({ ok: false, reason: "text-mismatch" });
  });

  it("clears guided intent when Code mode takes ownership and restores the prior Code draft", () => {
    const [entity] = buildModuleEntities(browser, "ideas");
    const raw = applyTextDraft(entity, "def", "raw = yes\n");
    const guided = applyGuidedTextDraft(raw, "def", {
      baseText: "raw = yes\n",
      controlId: "raw",
      text: "raw = no\n",
      value: false,
    });

    expect(guided.drafts.sourceForms?.def?.baseWasDraft).toBe(true);
    const reverted = applyGuidedTextDraft(guided, "def", {
      baseText: "raw = no\n",
      controlId: "raw",
      text: "raw = yes\n",
      value: true,
    });
    expect(reverted.drafts.text.def).toBe("raw = yes\n");
    expect(reverted.drafts.sourceForms).toBeUndefined();

    const codeOwned = applyTextDraft(guided, "def", "raw = maybe\n");
    expect(codeOwned.drafts.text.def).toBe("raw = maybe\n");
    expect(codeOwned.drafts.sourceForms).toBeUndefined();
  });

  it("keeps binary HOI4 model formats out of the text editor while raster extensions win over gfx-like slots", () => {
    const textExtensions = ["gfx", "gui", "fnt", "asset", "lua", "csv", "xml"];
    const binaryExtensions = ["anim", "mesh"];
    const sources = [...textExtensions, ...binaryExtensions, "png"].map(
      (extension) => ({
        slot: "gfx_bundle",
        name: `source.${extension}`,
        path: `/workspace/projects/PIHC3/src/modules/idea/IDEA_ALPHA/source.${extension}`,
        relative_path: `src/modules/idea/IDEA_ALPHA/source.${extension}`,
        extension,
      }),
    );
    const [entity] = buildModuleEntities(
      {
        ...browser,
        items: [
          {
            ...browser.items[0],
            source_count: sources.length,
            sources,
          },
        ],
      },
      "ideas",
    );

    expect(entity.sourceSlots.map((source) => source.editorKind)).toEqual([
      ...textExtensions.map(() => "code"),
      ...binaryExtensions.map(() => "asset"),
      "image",
    ]);
    expect(
      new Set(entity.sourceSlots.map((source) => source.draftKey)).size,
    ).toBe(sources.length);
  });

  it("keeps legacy entity JSON records text-editable without enabling asset staging", () => {
    const recordPath = "src/modules/entity/VIENTO_AIRSHIP_C11/record.json";
    const [entity] = buildModuleEntities(
      {
        ...browser,
        families: [
          {
            id: "entity",
            family: "entity",
            title: "Entities",
            item_count: 1,
            source_count: 2,
            layouts: ["canonical"],
          },
        ],
        items: [
          {
            id: "module:entity/VIENTO_AIRSHIP_C11",
            kind: "module",
            layout: "canonical",
            family_id: "entity",
            family: "entity",
            object_id: "VIENTO_AIRSHIP_C11",
            module_id: "entity/VIENTO_AIRSHIP_C11",
            title: "Viento Airship C11",
            root: "/workspace/projects/PIHC3/src/modules/entity/VIENTO_AIRSHIP_C11",
            relative_root: "src/modules/entity/VIENTO_AIRSHIP_C11",
            source_count: 2,
            sources: [
              source(
                "meta",
                "meta.yaml",
                "src/modules/entity/VIENTO_AIRSHIP_C11/meta.yaml",
              ),
              source("record", "record.json", recordPath),
            ],
          },
        ],
      },
      "entity",
    );

    expect(
      entity.sourceSlots.map((item) => [item.slot, item.editorKind]),
    ).toEqual([
      ["meta", "code"],
      ["record", "code"],
    ]);
    expect(supportsAssetDrafts(entity)).toBe(false);

    const recordText = '{"mesh":{"scale":1},"entities":[]}\n';
    const edited = applyTextDraft(entity, "record", recordText);
    expect(sourceTextEditsForEntity(edited)).toEqual([
      {
        path: `/workspace/projects/PIHC3/${recordPath}`,
        text: recordText,
      },
    ]);
  });

  it("enables resource staging only from Registry copy ownership or staged drafts", () => {
    const recordEntity = buildModuleEntities(
      {
        ...browser,
        items: [
          {
            ...browser.items[0],
            id: "module:entity/ENTITY_TEST",
            family_id: "entity",
            family: "entity",
            object_id: "ENTITY_TEST",
            module_id: "entity/ENTITY_TEST",
            sources: [
              source(
                "record",
                "record.json",
                "src/modules/entity/ENTITY_TEST/record.json",
              ),
            ],
          },
        ],
      },
      "entity",
    )[0];
    const modelSourceEntity = {
      ...recordEntity,
      sourceSlots: [
        {
          ...recordEntity.sourceSlots[0],
          slot: "pdx",
          name: "mesh.gfx",
          path: "/workspace/projects/PIHC3/src/modules/entity/ENTITY_TEST/gfx/models/ENTITY_TEST/mesh.gfx",
          relative_path:
            "src/modules/entity/ENTITY_TEST/gfx/models/ENTITY_TEST/mesh.gfx",
          extension: "gfx",
        },
      ],
    };
    const existingAssetEntity = {
      ...recordEntity,
      sourceSlots: [
        {
          ...recordEntity.sourceSlots[0],
          slot: "meshes",
          name: "mesh.mesh",
          path: "/workspace/projects/PIHC3/src/modules/entity/ENTITY_TEST/mesh.mesh",
          relative_path: "src/modules/entity/ENTITY_TEST/mesh.mesh",
          extension: "mesh",
          slot_kinds: ["copy"],
          editorKind: "asset" as const,
        },
      ],
    };
    const stagedAssetEntity = {
      ...recordEntity,
      drafts: {
        ...recordEntity.drafts,
        assets: [
          {
            contentBase64: "bWVzaA==",
            fileName: "mesh.mesh",
            path: "src/modules/entity/ENTITY_TEST/mesh.mesh",
            size: 4,
          },
        ],
      },
    };
    const authorableEntity = {
      ...recordEntity,
      draftState: "new" as const,
      resourceSlots: entityResourceSlots(),
      sourceSlots: [
        {
          ...recordEntity.sourceSlots[0],
          slot: "mesh",
          name: "mesh.gfx",
          path: "",
          relative_path: "",
          extension: ".gfx",
          editorKind: "code" as const,
        },
      ],
    };
    const aggregateCopyEntity = {
      ...recordEntity,
      resourceSlots: [
        {
          name: "assets",
          match: "^gfx/interface/.*\\.dds$",
          required: false,
          many: true,
          regex: true,
          kind: "copy" as const,
          shared: false,
        },
      ],
    };

    expect(supportsAssetDrafts(recordEntity)).toBe(false);
    expect(supportsAssetDrafts(modelSourceEntity)).toBe(false);
    expect(supportsAssetDrafts(existingAssetEntity)).toBe(true);
    expect(supportsAssetDrafts(stagedAssetEntity)).toBe(true);
    expect(supportsAssetDrafts(authorableEntity)).toBe(true);
    expect(supportsAssetDrafts(aggregateCopyEntity)).toBe(true);
  });

  it("derives aggregate copy destinations from directories owned by the same Registry slot", () => {
    const [base] = buildModuleEntities(browser, "ideas");
    const root = "src/modules/ui/UI_SHARED";
    const aggregate = {
      ...base,
      familyId: "ui",
      family: "ui",
      objectId: "UI_SHARED",
      root: `/workspace/projects/PIHC3/${root}`,
      relativeRoot: root,
      resourceSlots: [
        {
          name: "assets",
          match: "^gfx/interface/(ideas|shared)/.*\\.dds$",
          required: false,
          many: true,
          regex: true,
          kind: "copy" as const,
          shared: false,
        },
      ],
      sourceSlots: [
        {
          slot: "assets",
          slot_kinds: ["copy"],
          name: "idea.dds",
          path: `/workspace/projects/PIHC3/${root}/gfx/interface/ideas/idea.dds`,
          relative_path: `${root}/gfx/interface/ideas/idea.dds`,
          extension: "dds",
          draftKey: "assets::idea",
          editorKind: "asset" as const,
        },
        {
          slot: "assets",
          slot_kinds: ["copy"],
          name: "shared.dds",
          path: `/workspace/projects/PIHC3/${root}/gfx/interface/shared/shared.dds`,
          relative_path: `${root}/gfx/interface/shared/shared.dds`,
          extension: "dds",
          draftKey: "assets::shared",
          editorKind: "asset" as const,
        },
      ],
    };

    expect(assetDraftTargetsForFile(aggregate, "new.dds")).toEqual([
      {
        modulePath: "gfx/interface/ideas/new.dds",
        path: `${root}/gfx/interface/ideas/new.dds`,
        slotName: "assets",
      },
      {
        modulePath: "gfx/interface/shared/new.dds",
        path: `${root}/gfx/interface/shared/new.dds`,
        slotName: "assets",
      },
    ]);
    expect(defaultAssetDraftPath(aggregate, "new.dds")).toBe("");
    expect(
      defaultAssetDraftPath(
        { ...aggregate, sourceSlots: aggregate.sourceSlots.slice(0, 1) },
        "only.dds",
      ),
    ).toBe(`${root}/gfx/interface/ideas/only.dds`);
    expect(assetDraftTargetsForFile(aggregate, "new.png")).toEqual([]);
  });

  it("stages exact PIHC3 entity binaries under the nested model root and clears written drafts", () => {
    const modelRoot = "src/modules/entity/ENTITY_TEST/gfx/models/ENTITY_TEST";
    const [entity] = buildModuleEntities(
      {
        ...browser,
        families: [
          {
            id: "entity",
            family: "entity",
            title: "Entity",
            item_count: 1,
            source_count: 5,
            layouts: ["canonical"],
          },
        ],
        items: [
          {
            id: "module:entity/ENTITY_TEST",
            kind: "module",
            layout: "canonical",
            family_id: "entity",
            family: "entity",
            object_id: "ENTITY_TEST",
            module_id: "entity/ENTITY_TEST",
            title: "Entity Test",
            root: "/workspace/projects/PIHC3/src/modules/entity/ENTITY_TEST",
            relative_root: "src/modules/entity/ENTITY_TEST",
            source_count: 5,
            resource_slots: entityResourceSlots(),
            sources: [
              source("pdx", "mesh.gfx", `${modelRoot}/mesh.gfx`),
              source("pdx", "entity.asset", `${modelRoot}/entity.asset`),
              source("assets", "mesh.mesh", `${modelRoot}/mesh.mesh`, 2048),
              source("assets", "idle.anim", `${modelRoot}/idle.anim`, 1024),
              source("assets", "diffuse.dds", `${modelRoot}/diffuse.dds`, 4096),
            ],
          },
        ],
      },
      "entity",
    );
    const meshSource = entity.sourceSlots.find(
      (item) => item.name === "mesh.mesh",
    );
    const animationSource = entity.sourceSlots.find(
      (item) => item.name === "idle.anim",
    );
    const drafts = [
      {
        fileName: "mesh.mesh",
        path: meshSource?.relative_path ?? "",
        sourceKey: meshSource?.draftKey,
        contentBase64: "cGR4YXNzZXRp",
        size: 9,
      },
      {
        fileName: "walk.anim",
        path: animationSource?.relative_path ?? "",
        sourceKey: animationSource?.draftKey,
        contentBase64: "cGR4YXNzZXRp",
        size: 9,
      },
    ];
    const edited = applyAssetDrafts(entity, drafts);

    expect(meshSource?.editorKind).toBe("asset");
    expect(animationSource?.editorKind).toBe("asset");
    expect(defaultAssetDraftPath(entity, "walk.anim")).toBe(
      `${modelRoot}/walk.anim`,
    );
    expect(canApplyAssetDraft(edited)).toBe(true);
    expect(sourceAssetReplacementsForEntity(edited)).toEqual([
      { path: `${modelRoot}/mesh.mesh`, contentBase64: "cGR4YXNzZXRp" },
      { path: `${modelRoot}/idle.anim`, contentBase64: "cGR4YXNzZXRp" },
    ]);

    const applied = applyAssetReplacementPlanToEntity(edited, {
      schema: "paradev.rest.draft_apply.v1",
      project_id: "PIHC3",
      written: true,
      files: drafts.map((draft) => ({
        path: `/workspace/projects/PIHC3/${draft.path}`,
        relative_path: draft.path,
        operation: "replace_bytes",
      })),
    });
    expect(applied.drafts.assets).toBeUndefined();
    expect(applied.draftState).toBe("clean");
  });

  it("targets Registry copy slots for non-Entity module families", () => {
    const root = "src/modules/technology/TECHNOLOGY_AIR_AIRSHIP - 飞艇";
    const [technology] = buildModuleEntities(
      {
        ...browser,
        items: [
          {
            id: "module:technology/TECHNOLOGY_AIR_AIRSHIP",
            kind: "module",
            layout: "canonical",
            family_id: "technology",
            family: "technology",
            object_id: "TECHNOLOGY_AIR_AIRSHIP",
            module_id: "technology/TECHNOLOGY_AIR_AIRSHIP",
            title: "飞艇",
            root: `/workspace/projects/PIHC3/${root}`,
            relative_root: root,
            source_count: 0,
            sources: [],
            resource_slots: [
              {
                name: "compiled_assets",
                match: "^gfx/interface/technologies/.*\\.dds$",
                required: false,
                many: true,
                regex: true,
                kind: "copy",
                shared: false,
                authoring_path: "gfx/interface/technologies/{filename}",
              },
              {
                name: "compiled_assets",
                match: "^interface/technologies/.*\\.gfx$",
                required: false,
                many: true,
                regex: true,
                kind: "copy",
                shared: false,
                authoring_path: "interface/technologies/{filename}",
              },
            ],
          },
        ],
      },
      "technology",
    );

    expect(supportsAssetDrafts(technology)).toBe(true);
    expect(defaultAssetDraftPath(technology, "airship.dds")).toBe(
      `${root}/gfx/interface/technologies/airship.dds`,
    );
    expect(defaultAssetDraftPath(technology, "airship.gfx")).toBe(
      `${root}/interface/technologies/airship.gfx`,
    );
    expect(defaultAssetDraftPath(technology, "notes.txt")).toBe("");
  });

  it("keeps invalid or out-of-module entity asset targets visible but blocks apply", () => {
    const [entity] = buildModuleEntities(browser, "ideas");
    const entityFamily = {
      ...entity,
      familyId: "entity",
      family: "entity",
      root: "/workspace/projects/PIHC3/src/modules/entity/ENTITY_TEST",
      relativeRoot: "src/modules/entity/ENTITY_TEST",
      resourceSlots: entityResourceSlots(),
    };
    const invalidExtension = applyAssetDrafts(entityFamily, [
      {
        fileName: "notes.txt",
        path: "src/modules/entity/ENTITY_TEST/notes.txt",
        contentBase64: "bm90ZXM=",
        size: 5,
      },
    ]);
    const outsideModule = applyAssetDrafts(entityFamily, [
      {
        fileName: "mesh.mesh",
        path: "src/modules/entity/OTHER/mesh.mesh",
        contentBase64: "bWVzaA==",
        size: 4,
      },
    ]);

    expect(invalidExtension.drafts.assets).toHaveLength(1);
    expect(outsideModule.drafts.assets).toHaveLength(1);
    expect(canApplyAssetDraft(invalidExtension)).toBe(false);
    expect(canApplyAssetDraft(outsideModule)).toBe(false);
    expect(sourceAssetReplacementsForEntity(invalidExtension)).toEqual([]);
    expect(sourceAssetReplacementsForEntity(outsideModule)).toEqual([]);
  });

  it("blocks portable duplicate targets, extension mismatches, and image-asset collisions", () => {
    const idea = buildModuleEntities(browser, "ideas")[1];
    const root = "src/modules/entity/ENTITY_TEST";
    const entity = {
      ...idea,
      familyId: "entity",
      family: "entity",
      root: `/workspace/projects/PIHC3/${root}`,
      relativeRoot: root,
    };
    const duplicateTargets = applyAssetDrafts(entity, [
      {
        fileName: "first.mesh",
        path: `${root}/gfx/models/ENTITY_TEST/new.mesh`,
        contentBase64: "Zmlyc3Q=",
        size: 5,
      },
      {
        fileName: "second.mesh",
        path: "/workspace/projects/PIHC3/src//modules/entity/entity_test/GFX/models/entity_test/NEW.MESH",
        contentBase64: "c2Vjb25k",
        size: 6,
      },
    ]);
    const extensionMismatch = applyAssetDrafts(entity, [
      {
        fileName: "walk.anim",
        path: `${root}/gfx/models/ENTITY_TEST/walk.mesh`,
        contentBase64: "YW5pbQ==",
        size: 4,
      },
    ]);

    expect(hasBlockingAssetDraft(duplicateTargets)).toBe(true);
    expect(canApplyAssetDraft(duplicateTargets)).toBe(false);
    expect(sourceAssetReplacementsForEntity(duplicateTargets)).toEqual([]);
    expect(hasBlockingAssetDraft(extensionMismatch)).toBe(true);
    expect(sourceAssetReplacementsForEntity(extensionMismatch)).toEqual([]);

    const imageSource = entity.sourceSlots.find(
      (source) => source.editorKind === "image",
    );
    const imageDraft = applyImageDraft(entity, {
      fileName: "GFX_idea_alpha.png",
      path: imageSource?.relative_path,
      sourceKey: imageSource?.draftKey,
      previewUrl: "blob:idea",
      contentBase64: "cG5n",
    });
    const conflictingAsset = applyAssetDrafts(imageDraft, [
      {
        fileName: imageSource?.name ?? "GFX_idea_alpha.png",
        path: imageSource?.path ?? "",
        sourceKey: imageSource?.draftKey,
        contentBase64: "cmF3",
        size: 3,
      },
    ]);

    expect(canApplyImageDraft(conflictingAsset)).toBe(true);
    expect(hasBlockingAssetDraft(conflictingAsset)).toBe(true);
    expect(sourceAssetReplacementsForEntity(conflictingAsset)).toEqual([]);
  });

  it("uses one declared target without overwriting aggregate basenames implicitly", () => {
    const root = "src/modules/entity/HOI4DEV_ENTITIES";
    const [aggregate] = buildModuleEntities(
      {
        ...browser,
        families: [
          {
            id: "entity",
            family: "entity",
            title: "Entity",
            item_count: 1,
            source_count: 4,
            layouts: ["canonical"],
          },
        ],
        items: [
          {
            id: "module:entity/HOI4DEV_ENTITIES",
            kind: "module",
            layout: "canonical",
            family_id: "entity",
            family: "entity",
            object_id: "HOI4DEV_ENTITIES",
            module_id: "entity/HOI4DEV_ENTITIES",
            title: "Shared entities",
            root: `/workspace/projects/PIHC3/${root}`,
            relative_root: root,
            source_count: 4,
            resource_slots: entityResourceSlots(),
            sources: [
              source(
                "pdx",
                "mesh.gfx",
                `${root}/gfx/models/viento/air/airship/mesh.gfx`,
              ),
              source(
                "assets",
                "mesh.mesh",
                `${root}/gfx/models/viento/air/airship/mesh.mesh`,
                100,
              ),
              source(
                "pdx",
                "mesh.gfx",
                `${root}/gfx/models/viento/tank/normal/mesh.gfx`,
              ),
              source(
                "assets",
                "mesh.mesh",
                `${root}/gfx/models/viento/tank/normal/mesh.mesh`,
                200,
              ),
            ],
          },
        ],
      },
      "entity",
    );

    expect(defaultAssetDraftPath(aggregate, "mesh.mesh")).toBe(
      `${root}/gfx/models/HOI4DEV_ENTITIES/mesh.mesh`,
    );
    const implicitOverwrite = applyAssetDrafts(aggregate, [
      {
        fileName: "mesh.mesh",
        path: `${root}/gfx/models/viento/air/airship/mesh.mesh`,
        contentBase64: "bmV3LW1lc2g=",
        size: 8,
      },
    ]);
    expect(canApplyAssetDraft(implicitOverwrite)).toBe(false);
    expect(sourceAssetReplacementsForEntity(implicitOverwrite)).toEqual([]);

    const sourceRow = aggregate.sourceSlots.find((item) =>
      item.relative_path.endsWith("air/airship/mesh.mesh"),
    );
    const explicitReplace = applyAssetDrafts(aggregate, [
      {
        fileName: "mesh.mesh",
        path: sourceRow?.relative_path ?? "",
        sourceKey: sourceRow?.draftKey,
        contentBase64: "bmV3LW1lc2g=",
        size: 8,
      },
    ]);
    expect(canApplyAssetDraft(explicitReplace)).toBe(true);
    expect(sourceAssetReplacementsForEntity(explicitReplace)).toEqual([
      {
        path: `${root}/gfx/models/viento/air/airship/mesh.mesh`,
        contentBase64: "bmV3LW1lc2g=",
      },
    ]);
  });

  it("refreshes entity structure without discarding matching local drafts", () => {
    const entities = buildModuleEntities(browser, "ideas");
    const modified = applyTextDraft(
      entities[0],
      "loc",
      'IDEA_ALPHA:0 "Draft title"',
    );
    const incoming = [
      {
        ...entities[0],
        title: "Hydrated Alpha Idea",
        root: "/workspace/projects/PIHC3/src/modules/idea/IDEA_ALPHA_HYDRATED",
        sourceCount: 3,
      },
      {
        ...entities[1],
        title: "Refreshed Beta Law",
        root: "/workspace/projects/PIHC3/src/modules/idea/IDEA_BETA_REFRESHED",
      },
    ];

    const reconciled = mergeModuleEntitiesPreservingDrafts(
      [modified, { ...entities[1], title: "Stale Beta Law" }],
      incoming,
    );

    expect(reconciled[0]).toMatchObject({
      title: "Hydrated Alpha Idea",
      root: "/workspace/projects/PIHC3/src/modules/idea/IDEA_ALPHA_HYDRATED",
      sourceCount: 3,
      draftState: "modified",
    });
    expect(reconciled[0].drafts).toBe(modified.drafts);
    expect(reconciled[0].drafts.text.loc).toBe('IDEA_ALPHA:0 "Draft title"');
    expect(reconciled[1]).toBe(incoming[1]);
  });

  it("keeps drafts outside a paged or searched Catalog subset writable", () => {
    const entities = buildModuleEntities(browser, "ideas");
    const modified = applyTextDraft(
      entities[0],
      "def",
      "draft from another Catalog page",
    );

    const reconciled = mergeModuleEntitiesPreservingDrafts(
      [modified],
      [entities[1]],
    );

    expect(reconciled.map((entity) => entity.id)).toEqual([
      entities[1].id,
      modified.id,
    ]);
    expect(reconciled[1].sourceConflict).toBeUndefined();
    expect(canApplySourceTextDraft(reconciled[1])).toBe(true);
  });

  it("retains unmatched drafts but marks rows absent from a full browser as conflicts", () => {
    const entities = buildModuleEntities(browser, "ideas");
    const modifiedSource = {
      ...entities[0],
      id: "ideas:MODIFIED",
      objectId: "MODIFIED",
    };
    const modified = applyTextDraft(modifiedSource, "def", "modified draft");
    const created = createDraftEntity("ideas", entities, "New Idea");
    const removalSource = {
      ...entities[1],
      id: "ideas:REMOVED",
      objectId: "REMOVED",
    };
    const removed = markEntitiesForRemoval(
      [applyTextDraft(removalSource, "loc", "removal draft")],
      new Set([removalSource.id]),
    )[0];
    const staleClean = { ...entities[1], id: "ideas:STALE", objectId: "STALE" };
    const incoming = [
      { ...entities[0], id: "ideas:INCOMING", objectId: "INCOMING" },
    ];

    const reconciled = mergeModuleEntitiesPreservingDrafts(
      [modified, created, removed, staleClean],
      incoming,
      { authoritativeEntities: incoming },
    );

    expect(reconciled.map((entity) => entity.id)).toEqual([
      "ideas:INCOMING",
      "ideas:MODIFIED",
      created.id,
      "ideas:REMOVED",
    ]);
    expect(reconciled[1]).toEqual({
      ...modified,
      sourceConflict: "missing",
    });
    expect(reconciled[2]).toBe(created);
    expect(reconciled[3]).toEqual({
      ...removed,
      sourceConflict: "missing",
    });
    expect(reconciled.map((entity) => entity.draftState)).toEqual([
      "clean",
      "modified",
      "new",
      "remove",
    ]);
    expect(reconciled[3].drafts.text.loc).toBe("removal draft");
    expect(canApplySourceTextDraft(reconciled[1])).toBe(false);
    expect(canApplyRemovalDraft(reconciled[3])).toBe(false);

    const restored = mergeModuleEntitiesPreservingDrafts(
      reconciled,
      [modifiedSource, removalSource],
      { authoritativeEntities: [modifiedSource, removalSource] },
    );
    expect(restored[0]).toMatchObject({
      id: modified.id,
      draftState: "modified",
    });
    expect(restored[0].sourceConflict).toBeUndefined();
    expect(restored[1]).toMatchObject({
      id: removed.id,
      draftState: "remove",
    });
    expect(restored[1].sourceConflict).toBeUndefined();
  });

  it.each([
    [
      "path",
      (source: ModuleSourceSlot) => ({
        ...source,
        path: `${source.path}.moved`,
        relative_path: `${source.relative_path}.moved`,
      }),
    ],
    [
      "size",
      (source: ModuleSourceSlot) => ({
        ...source,
        size: (source.size ?? 0) + 1,
      }),
    ],
    [
      "mtime",
      (source: ModuleSourceSlot) => ({
        ...source,
        mtime_ns: `${BigInt(source.mtime_ns ?? "0") + 1n}`,
      }),
    ],
  ])(
    "blocks a dirty same-id row when its source %s changes",
    (_revisionName, changeSource) => {
      const [entity] = buildModuleEntities(browser, "ideas");
      const revisedEntity = {
        ...entity,
        sourceSlots: entity.sourceSlots.map((source, index) => ({
          ...source,
          size: 100 + index,
          mtime_ns: `${1_000 + index}`,
        })),
      };
      const modified = applyTextDraft(revisedEntity, "def", "draft = yes");
      const changed = {
        ...revisedEntity,
        sourceSlots: revisedEntity.sourceSlots.map((source, index) =>
          index === 0 ? changeSource(source) : source,
        ),
      };

      expect(sourceTextEditsForEntity(modified)[0]).toMatchObject({
        path: revisedEntity.sourceSlots[0].path,
        expectedSize: 100,
        expectedMtimeNs: "1000",
      });
      const [reconciled] = mergeModuleEntitiesPreservingDrafts(
        [modified],
        [changed],
        { authoritativeEntities: [changed] },
      );

      expect(reconciled.sourceConflict).toBe("changed");
      expect(reconciled.drafts.text.def).toBe("draft = yes");
      expect(canApplySourceTextDraft(reconciled)).toBe(false);

      const editedAgain = applyTextDraft(
        reconciled,
        "def",
        "draft = still preserved",
      );
      const [stillConflicted] = mergeModuleEntitiesPreservingDrafts(
        [editedAgain],
        [changed],
        { authoritativeEntities: [changed] },
      );
      expect(stillConflicted.sourceConflict).toBe("changed");
    },
  );

  it("rebases only acknowledged source revisions after a partial apply", () => {
    const [entity] = buildModuleEntities(browser, "ideas");
    const revisedEntity = {
      ...entity,
      sourceSlots: entity.sourceSlots.map((source, index) => ({
        ...source,
        size: 100 + index,
        mtime_ns: `${1_000 + index}`,
      })),
    };
    const modified = applyTextDraft(
      applyTextDraft(revisedEntity, "def", "definition draft"),
      "loc",
      "localization draft",
    );
    const payload: DraftApplyPayload = {
      schema: "paradev.rest.draft_apply.v1",
      project_id: "PIHC3",
      written: true,
      files: [
        {
          path: revisedEntity.sourceSlots[0].path,
          relative_path: revisedEntity.sourceSlots[0].relative_path,
          operation: "write_text",
          encoding: "utf-8",
        },
      ],
    };

    const partiallyApplied = applySourceTextPlanToEntity(modified, payload);
    const refreshed = {
      ...revisedEntity,
      sourceSlots: revisedEntity.sourceSlots.map((source, index) =>
        index === 0 ? { ...source, size: 120, mtime_ns: "2000" } : source,
      ),
    };
    const [reconciled] = mergeModuleEntitiesPreservingDrafts(
      [partiallyApplied],
      [refreshed],
      { authoritativeEntities: [refreshed] },
    );

    expect(partiallyApplied.drafts.text).toEqual({
      loc: "localization draft",
    });
    expect(partiallyApplied.draftSourceRevisions).toEqual([
      expect.objectContaining({
        sourceKey: "loc",
        size: 101,
        mtimeNs: "1001",
      }),
    ]);
    expect(reconciled.sourceConflict).toBeUndefined();
    expect(canApplySourceTextDraft(reconciled)).toBe(true);
  });

  it("captures the refreshed revision when a written source is drafted again", () => {
    const [entity] = buildModuleEntities(browser, "ideas");
    const revisedEntity = {
      ...entity,
      sourceSlots: entity.sourceSlots.map((source, index) => ({
        ...source,
        size: 100 + index,
        mtime_ns: `${1_000 + index}`,
      })),
    };
    const modified = applyInfoDraft(
      applyTextDraft(revisedEntity, "def", "definition draft"),
      { objectId: "idea_alpha_renamed" },
    );
    const payload: DraftApplyPayload = {
      schema: "paradev.rest.draft_apply.v1",
      project_id: "PIHC3",
      written: true,
      files: [
        {
          path: revisedEntity.sourceSlots[0].path,
          relative_path: revisedEntity.sourceSlots[0].relative_path,
          operation: "write_text",
          encoding: "utf-8",
        },
      ],
    };
    const partiallyApplied = applySourceTextPlanToEntity(modified, payload);
    const refreshed = {
      ...revisedEntity,
      sourceSlots: revisedEntity.sourceSlots.map((source, index) =>
        index === 0 ? { ...source, size: 120, mtime_ns: "2000" } : source,
      ),
    };
    const [reconciled] = mergeModuleEntitiesPreservingDrafts(
      [partiallyApplied],
      [refreshed],
      { authoritativeEntities: [refreshed] },
    );

    const editedAgain = applyTextDraft(
      reconciled,
      "def",
      "second definition draft",
    );

    expect(sourceTextEditsForEntity(editedAgain)[0]).toMatchObject({
      path: refreshed.sourceSlots[0].path,
      expectedSize: 120,
      expectedMtimeNs: "2000",
    });
  });

  it("adds PIHC source-backed focus info files as editable source slots", () => {
    const entities = buildModuleEntities(
      {
        ...browser,
        families: [
          {
            id: "focus_tree",
            family: "focus_tree",
            title: "Focus Trees",
            item_count: 1,
            source_count: 2,
            layouts: ["canonical"],
          },
        ],
        items: [
          {
            id: "focus_tree:C01_MAIN",
            kind: "module",
            layout: "canonical",
            family_id: "focuses",
            family: "focus_tree",
            object_id: "C01_MAIN",
            module_id: "C01_MAIN",
            title: "C01 Main",
            root: "/workspace/projects/PIHC3/src/modules/focus_tree/C01_MAIN",
            relative_root: "src/modules/focus_tree/C01_MAIN",
            source_count: 1,
            sources: [
              {
                slot: "meta",
                name: "meta.yaml",
                path: "/workspace/projects/PIHC3/src/modules/focus_tree/C01_MAIN/meta.yaml",
                relative_path: "src/modules/focus_tree/C01_MAIN/meta.yaml",
                extension: "yaml",
              },
            ],
            metadata: {
              settings: {
                source_focuses: [
                  { id: "FOCUS_C01_DEM_CHANGE", source_path: "C01_DEM_CHANGE" },
                  {
                    id: "FOCUS_C01_MAIN",
                    sourcePath: "legacy/C01_MAIN/info.json",
                  },
                ],
              },
            },
          },
        ],
      },
      "focuses",
    );

    expect(
      entities[0].sourceSlots.map((slot) => [
        slot.slot,
        slot.name,
        slot.relative_path,
        slot.editorKind,
      ]),
    ).toEqual([
      [
        "meta",
        "meta.yaml",
        "src/modules/focus_tree/C01_MAIN/meta.yaml",
        "code",
      ],
      [
        "focus:FOCUS_C01_DEM_CHANGE:info",
        "FOCUS_C01_DEM_CHANGE info.json",
        "src/modules/focus_tree/C01_MAIN/legacy/C01_DEM_CHANGE/info.json",
        "code",
      ],
      [
        "focus:FOCUS_C01_MAIN:info",
        "FOCUS_C01_MAIN info.json",
        "src/modules/focus_tree/C01_MAIN/legacy/C01_MAIN/info.json",
        "code",
      ],
    ]);
    expect(entities[0].sourceSlots[1].path).toBe(
      "/workspace/projects/PIHC3/src/modules/focus_tree/C01_MAIN/legacy/C01_DEM_CHANGE/info.json",
    );
  });

  it("selects an optional image source and metadata-aware cache key for instance thumbnails", () => {
    const entities = buildModuleEntities(
      {
        ...browser,
        items: [
          browser.items[0],
          {
            ...browser.items[1],
            sources: browser.items[1].sources.map((source) =>
              source.slot === "icon"
                ? {
                    ...source,
                    size: 4096,
                    mtime_ns: "1770000000123456789",
                  }
                : source,
            ),
          },
        ],
      },
      "ideas",
    );

    expect(moduleEntityThumbnailSource(entities[0])).toBeNull();
    expect(moduleEntityThumbnailSource(entities[1])).toMatchObject({
      slot: "icon",
      name: "GFX_idea_beta.dds",
      editorKind: "image",
    });
    expect(
      moduleEntityThumbnailCacheKey(
        entities[1],
        moduleEntityThumbnailSource(entities[1]),
        36,
      ),
    ).toBe(
      "v1|36|ideas:IDEA_BETA|src/gfx/interface/ideas/GFX_idea_beta.dds|4096|1770000000123456789",
    );
  });

  it("prefers browser-decodable thumbnail sources while retaining DDS as a fallback", () => {
    const entity = buildModuleEntities(browser, "ideas")[1];
    const ddsSource = entity.sourceSlots.find(
      (source) => source.editorKind === "image",
    );
    expect(ddsSource).toBeDefined();
    const pngSource: ModuleSourceSlot = {
      ...ddsSource!,
      name: "GFX_idea_beta.png",
      path: "/workspace/projects/PIHC3/src/gfx/interface/ideas/GFX_idea_beta.png",
      relative_path: "src/gfx/interface/ideas/GFX_idea_beta.png",
      extension: "png",
      draftKey: "preview-png",
    };

    expect(
      moduleEntityThumbnailSource({
        ...entity,
        sourceSlots: [ddsSource!, pngSource],
      }),
    ).toBe(pngSource);
    expect(
      moduleEntityThumbnailSource({
        ...entity,
        sourceSlots: [ddsSource!],
      }),
    ).toBe(ddsSource);
  });

  it("keeps browser-decodable preview metadata first but lets raster sources replace a DDS preview", () => {
    const entity = buildModuleEntities(browser, "ideas")[1];
    const ddsSource = entity.sourceSlots.find(
      (source) => source.editorKind === "image",
    );
    expect(ddsSource).toBeDefined();
    const pngSource: ModuleSourceSlot = {
      ...ddsSource!,
      name: "GFX_idea_beta.png",
      path: "/workspace/projects/PIHC3/src/gfx/interface/ideas/GFX_idea_beta.png",
      relative_path: "src/gfx/interface/ideas/GFX_idea_beta.png",
      extension: "png",
      draftKey: "source-png",
    };
    const webpPreview: ModuleSourceSlot = {
      ...pngSource,
      slot: "preview",
      name: "preview.webp",
      path: `${entity.root}/preview.webp`,
      relative_path: `${entity.relativeRoot}/preview.webp`,
      extension: "webp",
      draftKey: "preview",
    };

    expect(
      moduleEntityThumbnailSource({
        ...entity,
        previewSource: webpPreview,
        sourceSlots: [pngSource],
      }),
    ).toBe(webpPreview);
    expect(
      moduleEntityThumbnailSource({
        ...entity,
        previewSource: ddsSource,
        sourceSlots: [pngSource],
      }),
    ).toBe(pngSource);
  });

  it("uses canonical technology resources without a retired component family", () => {
    const entities = buildModuleEntities(
      {
        ...browser,
        families: [
          {
            id: "technology",
            family: "technology",
            title: "Technologies",
            item_count: 1,
            source_count: 2,
            layouts: ["canonical"],
          },
        ],
        items: [
          {
            id: "module:technology/TECHNOLOGY_AIR_AIRSHIP",
            kind: "module",
            layout: "canonical",
            family_id: "technology",
            family: "technology",
            object_id: "TECHNOLOGY_AIR_AIRSHIP",
            module_id: "technology/TECHNOLOGY_AIR_AIRSHIP",
            title: "飞艇",
            root: "/workspace/projects/PIHC3/src/modules/technology/TECHNOLOGY_AIR_AIRSHIP - 飞艇",
            relative_root:
              "src/modules/technology/TECHNOLOGY_AIR_AIRSHIP - 飞艇",
            source_count: 2,
            sources: [
              {
                slot: "compiled_assets",
                slot_kinds: ["copy"],
                name: "TECHNOLOGY_AIR_AIRSHIP.dds",
                path: "/workspace/projects/PIHC3/src/modules/technology/TECHNOLOGY_AIR_AIRSHIP - 飞艇/gfx/interface/technologies/TECHNOLOGY_AIR_AIRSHIP.dds",
                relative_path:
                  "src/modules/technology/TECHNOLOGY_AIR_AIRSHIP - 飞艇/gfx/interface/technologies/TECHNOLOGY_AIR_AIRSHIP.dds",
                extension: "dds",
              },
              {
                slot: "compiled_assets",
                slot_kinds: ["copy"],
                name: "TECHNOLOGY_AIR_AIRSHIP.gfx",
                path: "/workspace/projects/PIHC3/src/modules/technology/TECHNOLOGY_AIR_AIRSHIP - 飞艇/interface/technologies/TECHNOLOGY_AIR_AIRSHIP.gfx",
                relative_path:
                  "src/modules/technology/TECHNOLOGY_AIR_AIRSHIP - 飞艇/interface/technologies/TECHNOLOGY_AIR_AIRSHIP.gfx",
                extension: "gfx",
              },
            ],
          },
        ],
      },
      "technology",
    );

    expect(entities[0].sourceSlots.map((slot) => slot.name)).toEqual([
      "TECHNOLOGY_AIR_AIRSHIP.dds",
      "TECHNOLOGY_AIR_AIRSHIP.gfx",
    ]);
    expect(moduleEntityThumbnailSource(entities[0])).toMatchObject({
      slot: "compiled_assets",
      name: "TECHNOLOGY_AIR_AIRSHIP.dds",
      editorKind: "image",
    });
  });

  it("uses localized ID-key titles for the selected locale with English and ID fallbacks", () => {
    const zhEntities = buildModuleEntities(browser, "ideas", "zh");

    expect(zhEntities[0].title).toBe("Alpha Idea CN");

    const englishFallbackBrowser: ProjectBrowserPayload = {
      ...browser,
      items: [
        {
          ...browser.items[0],
          title: "Metadata Alpha",
          localized_titles: {
            l_english: "Alpha Idea",
          },
        },
      ],
    };
    expect(
      buildModuleEntities(englishFallbackBrowser, "ideas", "zh")[0].title,
    ).toBe("Alpha Idea");

    const idFallbackBrowser: ProjectBrowserPayload = {
      ...browser,
      items: [
        {
          ...browser.items[0],
          title: "Metadata Alpha",
          localized_titles: {
            l_french: "Idee Alpha",
          },
        },
      ],
    };
    expect(buildModuleEntities(idFallbackBrowser, "ideas", "zh")[0].title).toBe(
      "IDEA_ALPHA",
    );
  });

  it("filters by title, id, source slot, or path and sorts by the requested order", () => {
    const entities = buildModuleEntities(browser, "ideas");

    expect(
      filterAndSortEntities(entities, { query: "beta", sort: "title" }).map(
        (entity) => entity.objectId,
      ),
    ).toEqual(["IDEA_BETA"]);
    expect(
      filterAndSortEntities(entities, { query: "icon", sort: "title" }).map(
        (entity) => entity.objectId,
      ),
    ).toEqual(["IDEA_BETA"]);
    expect(
      filterAndSortEntities(entities, {
        query: "modules/idea",
        sort: "title",
      }).map((entity) => entity.objectId),
    ).toEqual(["IDEA_ALPHA"]);
    expect(
      filterAndSortEntities(entities, { query: "", sort: "sourceCount" }).map(
        (entity) => entity.objectId,
      ),
    ).toEqual(["IDEA_BETA", "IDEA_ALPHA"]);
    expect(
      filterAndSortEntities(entities, { query: "", sort: "id" }).map(
        (entity) => entity.objectId,
      ),
    ).toEqual(["IDEA_ALPHA", "IDEA_BETA"]);
  });

  it("tracks bulk selection across filtered and hidden entity scopes", () => {
    const entities = buildModuleEntities(browser, "ideas");
    const visible = [entities[0]];
    const hiddenSelected = new Set([entities[1].id]);

    expect(
      buildModuleEntitySelectionState(entities, visible, hiddenSelected),
    ).toEqual({
      allSelected: false,
      allVisibleSelected: false,
      hasFilteredScope: true,
      hiddenSelectedCount: 1,
      selectedCount: 1,
      someVisibleSelected: false,
      totalCount: 2,
      visibleCount: 1,
      visibleSelectedCount: 0,
    });

    expect([
      ...selectModuleEntityScope(
        hiddenSelected,
        visible.map((entity) => entity.id),
        "toggle",
      ),
    ]).toEqual(["ideas:IDEA_BETA", "ideas:IDEA_ALPHA"]);
    expect([
      ...selectModuleEntityScope(
        new Set(entities.map((entity) => entity.id)),
        visible.map((entity) => entity.id),
        "toggle",
      ),
    ]).toEqual(["ideas:IDEA_BETA"]);
    expect([
      ...selectModuleEntityScope(
        hiddenSelected,
        visible.map((entity) => entity.id),
        "replace",
      ),
    ]).toEqual(["ideas:IDEA_ALPHA"]);
  });

  it("preserves an externally selected entity hidden by the current filter", () => {
    const entities = buildModuleEntities(browser, "ideas");
    const visible = filterAndSortEntities(entities, {
      query: "alpha",
      sort: "title",
    });

    expect(
      resolveModuleEntitySelection("ideas:IDEA_BETA", entities, visible),
    ).toBe("ideas:IDEA_BETA");
    expect(resolveModuleEntitySelection("missing", entities, visible)).toBe(
      "ideas:IDEA_ALPHA",
    );
    expect(resolveModuleEntitySelection("", entities, [])).toBe(
      "ideas:IDEA_ALPHA",
    );
    expect(resolveModuleEntitySelection("missing", [], [])).toBe("");
  });

  it("clears the entity filter when an external selection is hidden", () => {
    const entities = buildModuleEntities(browser, "ideas");
    const visible = filterAndSortEntities(entities, {
      query: "alpha",
      sort: "title",
    });

    expect(
      resolveModuleEntityQueryAfterExternalSelection(
        "alpha",
        "ideas:IDEA_BETA",
        visible,
      ),
    ).toBe("");
    expect(
      resolveModuleEntityQueryAfterExternalSelection(
        "alpha",
        "ideas:IDEA_ALPHA",
        visible,
      ),
    ).toBe("alpha");
    expect(
      resolveModuleEntityQueryAfterExternalSelection("alpha", "", visible),
    ).toBe("alpha");
    expect(
      resolveModuleEntityQueryAfterExternalSelection(
        "",
        "ideas:IDEA_BETA",
        visible,
      ),
    ).toBe("");
  });

  it("selects or clears contiguous entity ranges in visible order", () => {
    const entities = buildModuleEntities(browser, "ideas");
    const orderedIds = entities.map((entity) => entity.id);

    expect([
      ...selectModuleEntityRange(
        new Set(),
        orderedIds,
        orderedIds[0],
        orderedIds[1],
        "select",
      ),
    ]).toEqual(["ideas:IDEA_ALPHA", "ideas:IDEA_BETA"]);
    expect([
      ...selectModuleEntityRange(
        new Set(orderedIds),
        orderedIds,
        orderedIds[0],
        orderedIds[1],
        "deselect",
      ),
    ]).toEqual([]);
    expect([
      ...selectModuleEntityRange(
        new Set(["outside"]),
        orderedIds,
        "missing",
        orderedIds[1],
        "select",
      ),
    ]).toEqual(["outside", "ideas:IDEA_BETA"]);
  });

  it("keeps edits as local drafts, marks persisted modules, and discards unsaved removals", () => {
    const entities = buildModuleEntities(browser, "ideas");
    const edited = applyTextDraft(
      entities[0],
      "loc",
      'IDEA_ALPHA:0 "Edited name"',
    );
    const renamed = applyInfoDraft(edited, {
      objectId: "idea_alpha_renamed",
      title: "Alpha Renamed",
    });
    const created = createDraftEntity("ideas", entities, "New Idea");
    const marked = markEntitiesForRemoval(
      [edited, entities[1], created],
      new Set([edited.id, created.id]),
    );

    expect(edited.draftState).toBe("modified");
    expect(edited.drafts.text.loc).toBe('IDEA_ALPHA:0 "Edited name"');
    expect(renamed.drafts.info).toEqual({
      objectId: "IDEA_ALPHA_RENAMED",
      title: "Alpha Renamed",
    });
    expect(created).toMatchObject({
      familyId: "ideas",
      objectId: "IDEAS_DRAFT_003",
      title: "New Idea",
      subtitle: "IDEAS_DRAFT_003",
      draftState: "new",
    });
    expect(
      marked.map((entity) => [entity.objectId, entity.draftState]),
    ).toEqual([
      ["IDEA_ALPHA", "remove"],
      ["IDEA_BETA", "clean"],
    ]);
  });

  it("selects project-local create templates and separates primary from advanced fields", () => {
    const template = selectCreateTemplate(templates, "idea");
    const fields = buildTemplateCreateFields(template);
    const created = createDraftEntity("ideas", [], "New PIHC3 Idea", template);

    expect(template?.id).toBe("pihc3:idea/legacy-current");
    expect(fields.primary.map((field) => field.name)).toEqual([
      "title",
      "description",
    ]);
    expect(fields.advanced.map((field) => field.name)).toEqual([
      "legacy_tag",
      "category",
      "language",
    ]);
    expect(created).toMatchObject({
      familyId: "ideas",
      family: "idea",
      objectId: "IDEA_DRAFT_001",
      title: "New PIHC3 Idea",
      draftState: "new",
    });
    expect(created.sourceCount).toBe(3);
    expect(created.drafts.text).toEqual({ meta: "", def: "", loc: "" });
    expect(
      created.sourceSlots.map((slot) => [slot.slot, slot.editorKind]),
    ).toEqual([
      ["meta", "code"],
      ["def", "code"],
      ["loc", "localization"],
    ]);
  });

  it("keeps same-name duplicate template files independently addressable", () => {
    const template: ProjectTemplate = {
      id: "pihc3:idea/multilingual",
      title: "Multilingual Idea",
      family: "idea",
      source: "project",
      args: {},
      files: ["loc/english/main.loc", "loc/simp_chinese/main.loc"],
    };

    const created = createDraftEntity(
      "ideas",
      [],
      "Multilingual Idea",
      template,
    );

    expect(created.sourceSlots.map((source) => source.draftKey)).toEqual([
      "loc::loc/english/main.loc",
      "loc::loc/simp_chinese/main.loc",
    ]);
    expect(created.drafts.text).toEqual({
      "loc::loc/english/main.loc": "",
      "loc::loc/simp_chinese/main.loc": "",
    });
  });

  it("resolves template path placeholders before showing a new draft source", () => {
    const template: ProjectTemplate = {
      id: "pihc3:portrait/basic",
      title: "PIHC3 Shared Portrait",
      family: "portrait",
      source: "project",
      args: {},
      files: ["portraits/{object_id}.txt"],
    };
    const input = buildCreateDraftInput(
      template,
      "PORTRAIT_UI_SMOKE",
      { title: "Portrait UI Smoke" },
    );

    const created = createDraftEntity(
      "portraits",
      [],
      input.title,
      template,
      input,
    );

    expect(created.sourceSlots).toMatchObject([
      {
        draftKey: "PORTRAIT_UI_SMOKE",
        editorKind: "code",
        name: "PORTRAIT_UI_SMOKE.txt",
        slot: "PORTRAIT_UI_SMOKE",
      },
    ]);
    expect(created.drafts.text).toEqual({ PORTRAIT_UI_SMOKE: "" });
  });

  it("keeps creation available when a family has multiple templates", () => {
    const choices = selectCreateTemplates(multiTemplatePayload, "idea");
    const defaultTemplate = selectCreateTemplate(multiTemplatePayload, "idea");
    const selectedTemplate = selectCreateTemplate(
      multiTemplatePayload,
      "idea",
      "pihc3:idea/category-law",
    );
    const selectedFields = buildTemplateCreateFields(selectedTemplate);

    expect(choices.map((template) => template.id)).toEqual([
      "pihc3:idea/legacy-current",
      "pihc3:idea/category-law",
      "hoi4:idea/basic",
    ]);
    expect(defaultTemplate?.id).toBe("pihc3:idea/legacy-current");
    expect(selectedTemplate?.id).toBe("pihc3:idea/category-law");
    expect(selectedFields.primary.map((field) => field.name)).toEqual([
      "title",
    ]);
    expect(selectedFields.advanced.map((field) => field.name)).toEqual([
      "category",
    ]);
  });

  it("excludes templates that the SDK marks as not authoring-ready", () => {
    const readinessPayload: ProjectTemplatesPayload = {
      ...multiTemplatePayload,
      templates: multiTemplatePayload.templates.map((template) => ({
        ...template,
        authoring_ready: template.id !== "pihc3:idea/legacy-current",
      })),
    };

    expect(
      selectCreateTemplates(readinessPayload, "idea").map(
        (template) => template.id,
      ),
    ).toEqual(["pihc3:idea/category-law", "hoi4:idea/basic"]);
    expect(selectCreateTemplate(readinessPayload, "idea")?.id).toBe(
      "pihc3:idea/category-law",
    );
  });

  it("keeps module and collection template choices distinct", () => {
    const payload: ProjectTemplatesPayload = {
      ...templates,
      templates: [
        {
          ...templates.templates[0],
          family: "focus",
          id: "pihc3:focus/basic",
          kind: "module",
          source: "project",
        },
        {
          ...templates.templates[0],
          family: "focus",
          id: "pihc3:focus-tree/basic",
          kind: "collection",
          source: "project",
        },
      ],
    };

    expect(
      selectCreateTemplates(payload, "focus").map((template) => template.id),
    ).toEqual(["pihc3:focus/basic"]);
    expect(
      selectCollectionCreateTemplates(payload, "focus").map(
        (template) => template.id,
      ),
    ).toEqual(["pihc3:focus-tree/basic"]);
  });

  it("preserves SDK create-form field labels and descriptions", () => {
    const template: ProjectTemplate = {
      id: "pihc3:game_rule/basic",
      title: "PIHC3 Basic Game Rule",
      family: "game_rule",
      source: "project",
      args: {
        title: { required: true, default: "", advanced: false },
        default_option_description: {
          required: false,
          default: "Use the default PIHC3 behavior.",
          advanced: true,
        },
      },
      form: {
        fields: [
          {
            name: "title",
            target: "values",
            label: "Display title",
            description: "Human-facing game rule title.",
            description_source: "declared",
            required: true,
            default: "",
            advanced: false,
            type: "string",
          },
          {
            name: "default_option_description",
            target: "values",
            label: "Default Option Description",
            description: "Explains the default game rule choice to players.",
            description_source: "generated",
            required: false,
            default: "Use the default PIHC3 behavior.",
            advanced: true,
            type: "text",
          },
        ],
      },
      files: ["meta.yaml"],
    };

    const fields = buildTemplateCreateFields(template);

    expect(fields.primary[0]).toMatchObject({
      name: "title",
      label: "Display title",
      description: "Human-facing game rule title.",
      descriptionSource: "declared",
      type: "string",
    });
    expect(fields.advanced[0]).toMatchObject({
      name: "default_option_description",
      label: "Default Option Description",
      description: "Explains the default game rule choice to players.",
      descriptionSource: "generated",
      defaultValue: "Use the default PIHC3 behavior.",
      type: "text",
    });
  });

  it("humanizes fallback create-form arg labels", () => {
    const template: ProjectTemplate = {
      id: "pihc3:country/basic",
      title: "PIHC3 Basic Country",
      family: "country",
      source: "project",
      args: {
        title: { required: true, default: "", advanced: false },
        legacy_tag: { required: false, default: "", advanced: true },
        default_option_description: {
          required: false,
          default: "Use the default PIHC3 behavior.",
          advanced: true,
        },
      },
      files: ["meta.yaml"],
    };

    const fields = buildTemplateCreateFields(template);

    expect(fields.primary[0]).toMatchObject({
      name: "title",
      label: "Title",
    });
    expect(fields.advanced.map((field) => [field.name, field.label])).toEqual([
      ["legacy_tag", "Legacy tag"],
      ["default_option_description", "Default option description"],
    ]);
    expect(fields.advanced.map((field) => field.label)).not.toContain(
      "legacy_tag",
    );
  });

  it("normalizes scalar template defaults and choices for form controls", () => {
    const template: ProjectTemplate = {
      id: "pihc3:idea/scalar-defaults",
      title: "Scalar defaults",
      family: "idea",
      source: "project",
      args: {
        cic: {
          required: false,
          default: 0.02,
          advanced: false,
          type: "number",
        },
        enabled: {
          required: false,
          default: false,
          advanced: true,
          type: "choice",
          choices: [true, false],
        },
      },
      files: ["def.txt"],
    };

    const fields = buildTemplateCreateFields(template);

    expect(fields.primary[0]?.defaultValue).toBe("0.02");
    expect(fields.advanced[0]).toMatchObject({
      defaultValue: "false",
      choices: ["true", "false"],
    });
  });

  it("resolves extension-owned relational fields from project browser identities", () => {
    const template: ProjectTemplate = {
      id: "pihc3:focus/basic",
      title: "Basic focus",
      family: "focus",
      source: "project",
      args: {
        tree: {
          required: true,
          default: "",
          advanced: false,
          reference: { kind: "collection", family: "focus" },
        },
      },
      files: ["def.txt"],
    };
    const field = buildTemplateCreateFields(template).primary[0];
    if (!field) {
      throw new Error("Missing focus-tree reference field.");
    }
    const focusTree = {
      ...browser.items[0],
      id: "focus:FOCUS_TREE_C08",
      kind: "collection" as const,
      family_id: "focuses",
      family: "focus",
      object_id: "FOCUS_TREE_C08",
      collection_id: "FOCUS_TREE_C08",
      title: "C08 national focus tree",
    };

    expect(field.reference).toEqual({ kind: "collection", family: "focus" });
    expect(
      templateCreateReferenceOptions(field, [focusTree, ...browser.items]),
    ).toEqual([
      {
        label: "C08 national focus tree — FOCUS_TREE_C08",
        value: "FOCUS_TREE_C08",
      },
    ]);
  });

  it("merges compact create form values with defaulted advanced template args", () => {
    const template = selectCreateTemplate(templates, "idea");
    const input = buildCreateDraftInput(
      template,
      "IDEA_TEST_FRIENDSHIP",
      {
        title: "Friendship Idea",
        description: "A draft national spirit.",
      },
      "New Ideas",
    );
    const created = createDraftEntity(
      "ideas",
      [],
      input.title,
      template,
      input,
    );

    expect(input).toEqual({
      objectId: "IDEA_TEST_FRIENDSHIP",
      title: "Friendship Idea",
      values: {
        object_id: "IDEA_TEST_FRIENDSHIP",
        legacy_tag: "TEST_FRIENDSHIP",
        title: "Friendship Idea",
        description: "A draft national spirit.",
        category: "country",
        language: "en",
      },
      advancedFields: ["legacy_tag", "category", "language"],
    });
    expect(created).toMatchObject({
      objectId: "IDEA_TEST_FRIENDSHIP",
      title: "Friendship Idea",
      drafts: {
        create: {
          templateId: "pihc3:idea/legacy-current",
          values: input.values,
          advancedFields: ["legacy_tag", "category", "language"],
        },
      },
    });
  });

  it("renders SDK escaped-brace defaults consistently for inline create", () => {
    const template: ProjectTemplate = {
      id: "pihc3:special_project_reward/basic",
      title: "PIHC3 Basic Special Project Reward",
      family: "special_project_reward",
      source: "project",
      args: {
        title: { required: true, default: "", advanced: false },
        effect: {
          required: false,
          default: "country_effects = {{ add_political_power = 50 }}",
          advanced: true,
        },
        wrapper: {
          required: false,
          default: "reward = {{ id = {object_id} title = {title} }}",
          advanced: true,
        },
      },
      files: ["meta.yaml", "def.pdx", "main.loc"],
    };

    const input = buildCreateDraftInput(template, "REWARD_TEST", {
      title: "Test Reward",
    });

    expect(input.values).toMatchObject({
      effect: "country_effects = { add_political_power = 50 }",
      wrapper: "reward = { id = REWARD_TEST title = Test Reward }",
    });
  });

  it("uses the generated draft id when compact create object id is blank", () => {
    const template = selectCreateTemplate(templates, "idea");
    const input = buildCreateDraftInput(
      template,
      "",
      {},
      "New Ideas",
      "IDEA_DRAFT_003",
    );

    expect(input.objectId).toBe("IDEA_DRAFT_003");
    expect(input.values).toMatchObject({
      object_id: "IDEA_DRAFT_003",
      legacy_tag: "DRAFT_003",
      title: "New Ideas",
    });
  });

  it("marks a written scaffold draft clean with source paths from the SDK plan", () => {
    const template = selectCreateTemplate(templates, "idea");
    const input = buildCreateDraftInput(
      template,
      "IDEA_TEST_FRIENDSHIP",
      {
        title: "Friendship Idea",
        description: "A draft national spirit.",
      },
      "New Ideas",
    );
    const draft = createDraftEntity("ideas", [], input.title, template, input);
    const plan: ModuleScaffoldPlan = {
      schema: "paradev.sdk.module_scaffold.v1",
      project_id: "PIHC3",
      template_id: "pihc3:idea/legacy-current",
      family: "idea",
      object_id: "IDEA_TEST_FRIENDSHIP",
      module_id: "idea/IDEA_TEST_FRIENDSHIP",
      root: "/workspace/projects/PIHC3/src/modules/idea/IDEA_TEST_FRIENDSHIP",
      values: {
        object_id: "IDEA_TEST_FRIENDSHIP",
        title: "Friendship Idea",
        description: "A draft national spirit.",
      },
      blocked: false,
      written: true,
      diagnostics: [],
      files: [
        {
          path: "/workspace/projects/PIHC3/src/modules/idea/IDEA_TEST_FRIENDSHIP/meta.yaml",
          relative_path: "src/modules/idea/IDEA_TEST_FRIENDSHIP/meta.yaml",
          module_path: "meta.yaml",
          action: "create",
        },
        {
          path: "/workspace/projects/PIHC3/src/modules/idea/IDEA_TEST_FRIENDSHIP/def.pdx",
          relative_path: "src/modules/idea/IDEA_TEST_FRIENDSHIP/def.pdx",
          module_path: "def.pdx",
          action: "create",
        },
        {
          path: "/workspace/projects/PIHC3/src/modules/idea/IDEA_TEST_FRIENDSHIP/main.loc",
          relative_path: "src/modules/idea/IDEA_TEST_FRIENDSHIP/main.loc",
          module_path: "main.loc",
          action: "create",
        },
      ],
    };

    const applied = applyScaffoldPlanToEntity(draft, plan);

    expect(canApplyScaffoldDraft(draft)).toBe(true);
    expect(canApplyScaffoldDraft(applied)).toBe(false);
    expect(applied).toMatchObject({
      id: "module:idea/IDEA_TEST_FRIENDSHIP",
      familyId: "ideas",
      family: "idea",
      moduleId: "idea/IDEA_TEST_FRIENDSHIP",
      objectId: "IDEA_TEST_FRIENDSHIP",
      title: "Friendship Idea",
      subtitle: "IDEA_TEST_FRIENDSHIP",
      root: "/workspace/projects/PIHC3/src/modules/idea/IDEA_TEST_FRIENDSHIP",
      relativeRoot: "src/modules/idea/IDEA_TEST_FRIENDSHIP",
      draftState: "clean",
      drafts: { text: {} },
    });
    expect(applied.tags).toEqual([]);
    expect(
      applied.sourceSlots.map((slot) => [
        slot.slot,
        slot.name,
        slot.relative_path,
        slot.editorKind,
      ]),
    ).toEqual([
      [
        "meta",
        "meta.yaml",
        "src/modules/idea/IDEA_TEST_FRIENDSHIP/meta.yaml",
        "code",
      ],
      [
        "def",
        "def.pdx",
        "src/modules/idea/IDEA_TEST_FRIENDSHIP/def.pdx",
        "code",
      ],
      [
        "loc",
        "main.loc",
        "src/modules/idea/IDEA_TEST_FRIENDSHIP/main.loc",
        "localization",
      ],
    ]);
  });

  it("keeps a titled scaffold folder while retaining the logical module id", () => {
    const template = selectCreateTemplate(templates, "idea");
    const input = buildCreateDraftInput(
      template,
      "IDEA_TITLED",
      { title: "Titled Idea" },
      "New Ideas",
    );
    const draft = createDraftEntity("ideas", [], input.title, template, input);
    const folderName = "IDEA_TITLED - Titled Idea";
    const plan: ModuleScaffoldPlan = {
      schema: "paradev.sdk.module_scaffold.v1",
      project_id: "PIHC3",
      template_id: "pihc3:idea/legacy-current",
      family: "idea",
      object_id: "IDEA_TITLED",
      module_id: "idea/IDEA_TITLED",
      folder_name: folderName,
      root: `/workspace/projects/PIHC3/src/modules/idea/${folderName}`,
      values: {
        object_id: "IDEA_TITLED",
        title: "Titled Idea",
      },
      blocked: false,
      written: true,
      diagnostics: [],
      files: [
        {
          path: `/workspace/projects/PIHC3/src/modules/idea/${folderName}/meta.yaml`,
          relative_path: `src/modules/idea/${folderName}/meta.yaml`,
          module_path: "meta.yaml",
          action: "create",
        },
      ],
    };

    const applied = applyScaffoldPlanToEntity(draft, plan);

    expect(applied).toMatchObject({
      moduleId: "idea/IDEA_TITLED",
      objectId: "IDEA_TITLED",
      root: `/workspace/projects/PIHC3/src/modules/idea/${folderName}`,
      relativeRoot: `src/modules/idea/${folderName}`,
    });
  });

  it("refreshes backend browser state only after a successful scaffold apply", () => {
    const plan: ModuleScaffoldPlan = {
      schema: "paradev.sdk.module_scaffold.v1",
      project_id: "PIHC3",
      template_id: "pihc3:idea/legacy-current",
      family: "idea",
      object_id: "IDEA_REFRESH_TEST",
      module_id: "idea/IDEA_REFRESH_TEST",
      root: "/workspace/projects/PIHC3/src/modules/idea/IDEA_REFRESH_TEST",
      values: { object_id: "IDEA_REFRESH_TEST", title: "Refresh Test" },
      blocked: false,
      written: true,
      diagnostics: [],
      files: [],
    };

    expect(shouldRefreshAfterScaffoldApply(plan)).toBe(true);
    expect(shouldRefreshAfterScaffoldApply({ ...plan, written: false })).toBe(
      false,
    );
    expect(shouldRefreshAfterScaffoldApply({ ...plan, blocked: true })).toBe(
      false,
    );
  });

  it("builds REST source text edits and clears only written text drafts after apply", () => {
    const entities = buildModuleEntities(browser, "ideas");
    const imagePath =
      "/workspace/projects/PIHC3/src/modules/idea/IDEA_ALPHA/icon.png";
    const entityWithImage = {
      ...entities[0],
      sourceSlots: [
        ...entities[0].sourceSlots,
        {
          slot: "icon",
          name: "icon.png",
          path: imagePath,
          relative_path: "src/modules/idea/IDEA_ALPHA/icon.png",
          extension: "png",
          draftKey: "icon",
          editorKind: "image" as const,
        },
      ],
    };
    const edited = applyImageDraft(
      applyTextDraft(entityWithImage, "loc", 'IDEA_ALPHA:0 "Edited name"'),
      {
        fileName: "icon.png",
        path: imagePath,
        previewUrl: "blob:icon",
      },
    );
    const payload: DraftApplyPayload = {
      schema: "paradev.rest.draft_apply.v1",
      project_id: "PIHC3",
      written: true,
      files: [
        {
          path: "/workspace/projects/PIHC3/src/modules/idea/IDEA_ALPHA/main.loc",
          relative_path: "src/modules/idea/IDEA_ALPHA/main.loc",
          operation: "write_text",
          encoding: "utf-8",
        },
      ],
    };

    expect(canApplySourceTextDraft(edited)).toBe(true);
    expect(sourceTextEditsForEntity(edited)).toEqual([
      {
        path: "/workspace/projects/PIHC3/src/modules/idea/IDEA_ALPHA/main.loc",
        text: 'IDEA_ALPHA:0 "Edited name"',
      },
    ]);

    const applied = applySourceTextPlanToEntity(edited, payload);

    expect(applied.draftState).toBe("modified");
    expect(applied.drafts.text).toEqual({});
    expect(applied.drafts.image).toEqual({
      fileName: "icon.png",
      path: imagePath,
      previewUrl: "blob:icon",
    });
    expect(canApplySourceTextDraft(applied)).toBe(false);
  });

  it("retains a canonical title draft until the readable folder is synchronized", () => {
    const entities = buildModuleEntities(browser, "ideas");
    const entity = {
      ...entities[0],
      sourceSlots: [
        {
          slot: "meta",
          name: "meta.yaml",
          path: "/workspace/projects/PIHC3/src/modules/idea/IDEA_ALPHA/meta.yaml",
          relative_path: "src/modules/idea/IDEA_ALPHA/meta.yaml",
          extension: "yaml",
          draftKey: "meta",
          editorKind: "localization" as const,
        },
        ...entities[0].sourceSlots,
      ],
    };
    const edited = applyTextDraft(
      applyInfoDraft(entity, { title: "Edited Alpha" }),
      "meta",
      'title: "Edited Alpha"\n',
    );
    const payload: DraftApplyPayload = {
      schema: "paradev.rest.draft_apply.v1",
      project_id: "PIHC3",
      written: true,
      files: [
        {
          path: "/workspace/projects/PIHC3/src/modules/idea/IDEA_ALPHA/meta.yaml",
          relative_path: "src/modules/idea/IDEA_ALPHA/meta.yaml",
          operation: "write_text",
          encoding: "utf-8",
        },
      ],
    };

    const applied = applySourceTextPlanToEntity(edited, payload);

    expect(applied.draftState).toBe("modified");
    expect(applied.title).toBe("Alpha Idea");
    expect(applied.drafts.text).toEqual({});
    expect(applied.drafts.info).toEqual({ title: "Edited Alpha" });
  });

  it("allows a canonical title-only folder synchronization", () => {
    const [entity, familyRootEntity] = buildModuleEntities(browser, "ideas");

    expect(
      canApplyInfoDraft(applyInfoDraft(entity, { title: "Edited Alpha" })),
    ).toBe(true);
    expect(
      canApplyInfoDraft(applyInfoDraft(entity, { title: "Alpha Idea" })),
    ).toBe(false);
    expect(
      canApplyInfoDraft({
        ...entity,
        draftState: "modified",
        drafts: { text: {}, info: { title: " " } },
      }),
    ).toBe(false);
    expect(
      canApplyInfoDraft(
        applyInfoDraft(familyRootEntity, { title: "Edited shared title" }),
      ),
    ).toBe(false);
  });

  it("allows canonical module removal independently of enumerated source slots", () => {
    const entities = buildModuleEntities(browser, "ideas");
    const marked = markEntitiesForRemoval(entities, new Set([entities[0].id]));

    expect(canApplyRemovalDraft(marked[0])).toBe(true);
    expect(canApplyRemovalDraft({ ...marked[0], sourceSlots: [] })).toBe(true);
    expect(canApplyRemovalDraft(marked[1])).toBe(false);
    expect(canApplyRemovalDraft({ ...marked[0], layout: "family_root" })).toBe(
      false,
    );
    expect(canApplyRemovalDraft({ ...marked[0], moduleId: undefined })).toBe(
      false,
    );
    expect(canApplyRemovalDraft({ ...marked[0], root: "" })).toBe(false);
  });

  it("treats canonical collection identity and removal drafts as first-class", () => {
    const module = buildModuleEntities(browser, "ideas")[0];
    const collection = {
      ...module,
      id: "collection:idea/IDEA_GROUP",
      kind: "collection" as const,
      moduleId: undefined,
      collectionId: "IDEA_GROUP",
      objectId: "IDEA_GROUP",
    };
    const renamed = applyInfoDraft(collection, {
      objectId: "IDEA_GROUP_NEW",
      title: collection.title,
    });
    const marked = markEntitiesForRemoval(
      [collection],
      new Set([collection.id]),
    )[0];

    expect(canApplyInfoDraft(renamed)).toBe(true);
    expect(
      canApplyInfoDraft(
        applyInfoDraft(collection, { title: "Title without ID rename" }),
      ),
    ).toBe(false);
    expect(canApplyRemovalDraft(marked)).toBe(true);
  });

  it("builds PNG source replacements and clears applied image drafts", () => {
    const entity = pngImageEntity();
    const edited = applyImageDraft(entity, {
      fileName: "GFX_idea_beta.png",
      previewUrl: "blob:icon",
      contentBase64: "bmV3LWljb24=",
    });
    const payload: DraftApplyPayload = {
      schema: "paradev.rest.draft_apply.v1",
      project_id: "PIHC3",
      written: true,
      files: [
        {
          path: "/workspace/projects/PIHC3/src/gfx/interface/ideas/GFX_idea_beta.png",
          relative_path: "src/gfx/interface/ideas/GFX_idea_beta.png",
          operation: "replace_bytes",
        },
      ],
    };

    expect(canApplyImageDraft(edited)).toBe(true);
    expect(sourceReplacementsForEntity(edited)).toEqual([
      {
        path: "/workspace/projects/PIHC3/src/gfx/interface/ideas/GFX_idea_beta.png",
        contentBase64: "bmV3LWljb24=",
      },
    ]);
    expect(
      canApplyImageDraft(
        applyImageDraft(entity, {
          fileName: "icon.png",
          previewUrl: "blob:icon",
        }),
      ),
    ).toBe(false);

    const applied = applyImageReplacementPlanToEntity(edited, payload);

    expect(applied.draftState).toBe("clean");
    expect(applied.drafts.image).toBeUndefined();
    expect(canApplyImageDraft(applied)).toBe(false);
  });

  it("keeps the selected source path and rejects custom paths for existing images", () => {
    const entities = buildModuleEntities(browser, "ideas");
    const ddsEntity = entities[1];

    expect(defaultImageDraftPath(ddsEntity, ddsEntity.sourceSlots[1])).toBe(
      "/workspace/projects/PIHC3/src/gfx/interface/ideas/GFX_idea_beta.dds",
    );
    expect(
      applyImageDraft(ddsEntity, {
        fileName: "GFX_idea_beta.png",
        path: "/workspace/projects/PIHC3/src/gfx/interface/ideas/GFX_idea_beta.png",
        previewUrl: "blob:icon",
        contentBase64: "bmV3LWljb24=",
      }),
    ).toBe(ddsEntity);

    const pngEntity = pngImageEntity();
    const edited = applyImageDraft(pngEntity, {
      fileName: "GFX_idea_beta.png",
      path: "/workspace/projects/PIHC3/src/gfx/interface/ideas/custom_beta.png",
      previewUrl: "blob:icon",
      contentBase64: "bmV3LWljb24=",
    });

    expect(edited).toBe(pngEntity);
    expect(sourceReplacementsForEntity(edited)).toEqual([]);

    const nonPngTarget = applyImageDraft(pngEntity, {
      fileName: "GFX_idea_beta.png",
      path: "/workspace/projects/PIHC3/src/gfx/interface/ideas/GFX_idea_beta.dds",
      previewUrl: "blob:icon",
      contentBase64: "bmV3LWljb24=",
    });
    expect(nonPngTarget).toBe(pngEntity);

    const imageSource = pngEntity.sourceSlots.find(
      (source) => source.editorKind === "image",
    );
    const relativeTarget = applyImageDraft(pngEntity, {
      fileName: "GFX_idea_beta.png",
      sourceKey: imageSource?.draftKey,
      path: imageSource?.relative_path,
      previewUrl: "blob:icon",
      contentBase64: "bmV3LWljb24=",
    });
    expect(sourceReplacementsForEntity(relativeTarget)).toEqual([
      {
        path: "src/gfx/interface/ideas/GFX_idea_beta.png",
        contentBase64: "bmV3LWljb24=",
      },
    ]);
  });

  it.each(["dds", "tga", "jpg", "jpeg", "webp", "bmp"])(
    "builds a PNG-to-%s conversion replacement for an existing source",
    (extension) => {
      const pngEntity = pngImageEntity();
      const unsupported = {
        ...pngEntity,
        sourceSlots: pngEntity.sourceSlots.map((source) =>
          source.editorKind === "image"
            ? {
                ...source,
                name: source.name.replace(/\.png$/i, `.${extension}`),
                path: source.path.replace(/\.png$/i, `.${extension}`),
                relative_path: source.relative_path.replace(
                  /\.png$/i,
                  `.${extension}`,
                ),
                extension,
              }
            : source,
        ),
      };
      const imageSource = unsupported.sourceSlots.find(
        (source) => source.editorKind === "image",
      );
      const attempted = applyImageDraft(unsupported, {
        fileName: "replacement.png",
        sourceKey: imageSource?.draftKey,
        path: imageSource?.path,
        previewUrl: "blob:replacement",
        contentBase64: "cG5n",
      });

      expect(attempted).not.toBe(unsupported);
      expect(canApplyImageDraft(attempted)).toBe(true);
      expect(sourceReplacementsForEntity(attempted)).toEqual([
        {
          path: imageSource?.path,
          contentBase64: "cG5n",
          contentFormat: "png",
          targetFormat: extension,
        },
      ]);
    },
  );

  it("only sends browser-decodable source previews to the image editor", () => {
    const imageSource = pngImageEntity().sourceSlots.find(
      (source) => source.editorKind === "image",
    );
    expect(imageSource).toBeDefined();
    const withExtension = (extension: string) => ({
      ...imageSource!,
      name: imageSource!.name.replace(/\.png$/i, `.${extension}`),
      path: imageSource!.path.replace(/\.png$/i, `.${extension}`),
      relative_path: imageSource!.relative_path.replace(
        /\.png$/i,
        `.${extension}`,
      ),
      extension,
    });

    for (const extension of ["png", "jpg", "jpeg", "webp", "bmp"]) {
      expect(canPreviewImageSourceInEditor(withExtension(extension))).toBe(
        true,
      );
    }
    for (const extension of ["dds", "tga"]) {
      expect(canPreviewImageSourceInEditor(withExtension(extension))).toBe(
        false,
      );
    }
  });

  it("builds an exact-path DDS conversion for a canonical PIHC3 technology module", () => {
    const ddsPath =
      "src/modules/technology/TECHNOLOGY_AIR_AIRSHIP - 飞艇/gfx/interface/technologies/TECHNOLOGY_AIR_AIRSHIP.dds";
    const [technology] = buildModuleEntities(
      {
        ...browser,
        families: [
          {
            id: "technology",
            family: "technology",
            title: "Technologies",
            item_count: 1,
            source_count: 1,
            layouts: ["canonical"],
          },
        ],
        items: [
          {
            id: "module:technology/TECHNOLOGY_AIR_AIRSHIP",
            kind: "module",
            layout: "canonical",
            family_id: "technology",
            family: "technology",
            object_id: "TECHNOLOGY_AIR_AIRSHIP",
            module_id: "technology/TECHNOLOGY_AIR_AIRSHIP",
            title: "飞艇",
            root: "/workspace/projects/PIHC3/src/modules/technology/TECHNOLOGY_AIR_AIRSHIP - 飞艇",
            relative_root:
              "src/modules/technology/TECHNOLOGY_AIR_AIRSHIP - 飞艇",
            source_count: 1,
            sources: [
              {
                slot: "compiled_assets",
                slot_kinds: ["copy"],
                name: "TECHNOLOGY_AIR_AIRSHIP.dds",
                path: `/workspace/projects/PIHC3/${ddsPath}`,
                relative_path: ddsPath,
                extension: "dds",
              },
            ],
          },
        ],
      },
      "technology",
    );
    const attempted = applyImageDraft(technology, {
      fileName: "TECHNOLOGY_AIR_AIRSHIP.png",
      sourceKey: "compiled_assets",
      path: defaultImageDraftPath(technology, technology.sourceSlots[0]),
      previewUrl: "blob:technology-icon",
      contentBase64: "cG5nLWJ5dGVz",
    });

    expect(defaultImageDraftPath(technology, technology.sourceSlots[0])).toBe(
      `/workspace/projects/PIHC3/${ddsPath}`,
    );
    expect(attempted).not.toBe(technology);
    expect(sourceReplacementsForEntity(attempted)).toEqual([
      {
        path: `/workspace/projects/PIHC3/${ddsPath}`,
        contentBase64: "cG5nLWJ5dGVz",
        contentFormat: "png",
        targetFormat: "dds",
      },
    ]);
    expect(canApplyImageDraft(attempted)).toBe(true);
  });

  it("rejects source-less image drafts instead of inventing a PNG target", () => {
    const entity = pngImageEntity();
    const sourceLess = {
      ...entity,
      sourceSlots: entity.sourceSlots.filter(
        (source) => source.editorKind !== "image",
      ),
    };
    const rejected = applyImageDraft(sourceLess, {
      fileName: "new-icon.png",
      path: "/workspace/projects/PIHC3/src/gfx/interface/ideas/new-icon.dds",
      previewUrl: "blob:new-icon",
      contentBase64: "cG5n",
    });
    const projectLocalPng = applyImageDraft(sourceLess, {
      fileName: "new-icon.png",
      path: "/workspace/projects/PIHC3/src/gfx/interface/ideas/new-icon.png",
      previewUrl: "blob:new-icon",
      contentBase64: "cG5n",
    });

    expect(defaultImageDraftPath(sourceLess, null)).toBe("");
    expect(rejected).toBe(sourceLess);
    expect(canApplyImageDraft(rejected)).toBe(false);
    expect(projectLocalPng).toBe(sourceLess);
    expect(sourceReplacementsForEntity(projectLocalPng)).toEqual([]);
  });

  it("creates only an exact family-declared missing image target", () => {
    const relativePath = "src/modules/idea/IDEA_ALPHA/icon.png";
    const [entity] = buildModuleEntities(
      {
        ...browser,
        items: [
          {
            ...browser.items[0],
            image_targets: [
              {
                slot: "icon",
                name: "icon.png",
                path: `/workspace/projects/PIHC3/${relativePath}`,
                relative_path: relativePath,
                extension: "png",
                exists: false,
              },
            ],
          },
        ],
      },
      "ideas",
    );
    const imageSource = entity.sourceSlots.find(
      (source) => source.editorKind === "image",
    );

    expect(imageSource).toMatchObject({
      slot: "icon",
      path: `/workspace/projects/PIHC3/${relativePath}`,
      relative_path: relativePath,
      exists: false,
    });
    expect(moduleEntityThumbnailSource(entity)).toBeNull();

    const edited = applyImageDraft(entity, {
      fileName: "replacement.png",
      sourceKey: imageSource?.draftKey,
      path: relativePath,
      previewUrl: "blob:replacement",
      contentBase64: "cG5n",
    });

    expect(edited.drafts.image?.expectedAbsent).toBe(true);
    expect(sourceReplacementsForEntity(edited)).toEqual([
      {
        path: relativePath,
        contentBase64: "cG5n",
        expectedAbsent: true,
      },
    ]);
    expect(
      applyImageDraft(entity, {
        fileName: "replacement.png",
        sourceKey: imageSource?.draftKey,
        path: "src/modules/idea/IDEA_ALPHA/other.png",
        previewUrl: "blob:other",
        contentBase64: "cG5n",
      }),
    ).toBe(entity);
  });

  it("blocks a missing-image draft when its declared target appears during refresh", () => {
    const relativePath = "src/modules/idea/IDEA_ALPHA/icon.png";
    const imageTarget = {
      slot: "icon",
      name: "icon.png",
      path: `/workspace/projects/PIHC3/${relativePath}`,
      relative_path: relativePath,
      extension: "png",
      exists: false as const,
    };
    const targetBrowser: ProjectBrowserPayload = {
      ...browser,
      items: [
        {
          ...browser.items[0],
          image_targets: [imageTarget],
        },
      ],
    };
    const [entity] = buildModuleEntities(targetBrowser, "ideas");
    const imageSource = entity.sourceSlots.find(
      (source) => source.editorKind === "image",
    );
    const edited = applyImageDraft(entity, {
      fileName: "replacement.png",
      sourceKey: imageSource?.draftKey,
      path: relativePath,
      previewUrl: "blob:replacement",
      contentBase64: "cG5n",
    });
    const [refreshed] = buildModuleEntities(
      {
        ...targetBrowser,
        items: [
          {
            ...targetBrowser.items[0],
            image_targets: [],
            source_count: targetBrowser.items[0].source_count + 1,
            sources: [
              ...targetBrowser.items[0].sources,
              {
                ...imageTarget,
                exists: true,
                size: 3,
                mtime_ns: "1700000000000000000",
              },
            ],
          },
        ],
      },
      "ideas",
    );

    const [merged] = mergeModuleEntitiesPreservingDrafts([edited], [refreshed]);

    expect(merged.sourceConflict).toBe("changed");
    expect(merged.drafts.image?.expectedAbsent).toBe(true);
    expect(sourceReplacementsForEntity(merged)).toEqual([]);
  });

  it("targets an explicitly selected image source instead of the first image", () => {
    const firstPath = "src/gfx/interface/ideas/GFX_idea_beta.dds";
    const secondPath = "src/gfx/interface/ideas/GFX_idea_beta_large.png";
    const [entity] = buildModuleEntities(
      {
        ...browser,
        items: [
          {
            ...browser.items[1],
            source_count: 2,
            sources: [
              {
                slot: "image",
                name: "GFX_idea_beta.dds",
                path: `/workspace/projects/PIHC3/${firstPath}`,
                relative_path: firstPath,
                extension: "dds",
              },
              {
                slot: "image",
                name: "GFX_idea_beta_large.png",
                path: `/workspace/projects/PIHC3/${secondPath}`,
                relative_path: secondPath,
                extension: "png",
              },
            ],
          },
        ],
      },
      "ideas",
    );
    const secondSourceKey = `image::${secondPath}`;
    const firstSourceKey = `image::${firstPath}`;
    const edited = applyImageDraft(entity, {
      fileName: "GFX_idea_beta_large.png",
      sourceKey: secondSourceKey,
      previewUrl: "blob:large-icon",
      contentBase64: "bGFyZ2UtaWNvbg==",
    });

    expect(sourceReplacementsForEntity(edited)).toEqual([
      {
        path: "/workspace/projects/PIHC3/src/gfx/interface/ideas/GFX_idea_beta_large.png",
        contentBase64: "bGFyZ2UtaWNvbg==",
      },
    ]);
    expect(
      sourceReplacementsForEntity(
        applyImageDraft(entity, {
          fileName: "GFX_idea_beta.png",
          sourceKey: firstSourceKey,
          previewUrl: "blob:icon",
          contentBase64: "aWNvbg==",
        }),
      ),
    ).toEqual([
      {
        path: `/workspace/projects/PIHC3/${firstPath}`,
        contentBase64: "aWNvbg==",
        contentFormat: "png",
        targetFormat: "dds",
      },
    ]);
    expect(
      sourceReplacementsForEntity(
        applyImageDraft(entity, {
          fileName: "missing.png",
          sourceKey: "image::missing",
          previewUrl: "blob:missing",
          contentBase64: "bWlzc2luZw==",
        }),
      ),
    ).toEqual([]);
  });

  it("selects the Registry-owned title key in the preferred localization source", () => {
    const [entity] = buildModuleEntities(browser, "ideas", "zh");
    const sources = [
      {
        slot: "loc",
        language: "l_english",
        text: 'l_english:\n IDEA_ALPHA:0 "Alpha Idea"\n',
      },
      {
        slot: "loc_zh",
        language: "l_simp_chinese",
        text: 'l_simp_chinese:\n IDEA_ALPHA:0 "Alpha Idea CN"\n',
      },
    ];

    const table = {
      languages: ["l_english", "l_simp_chinese"],
      rows: [{
        key: "IDEA_ALPHA",
        values: {
          l_english: { slot: "loc", text: "Alpha Idea" },
          l_simp_chinese: { slot: "loc_zh", text: "Alpha Idea CN" },
        },
      }],
    };

    expect(moduleTitleLocalizationTarget(entity, "zh", sources, table)).toEqual({
      key: "IDEA_ALPHA",
      language: "l_simp_chinese",
      slot: "loc_zh",
    });
    expect(
      moduleTitleLocalizationTarget(
        { ...entity, titleKeys: [] },
        "zh",
        sources,
        table,
      ),
    ).toBeNull();
  });

  it("updates metadata title text for info-page name edits", () => {
    expect(
      updateMetadataTitleText(
        "title: Old Name\nsettings:\n  category: country\n",
        "New Name",
      ),
    ).toBe('title: "New Name"\nsettings:\n  category: country\n');
    expect(updateMetadataTitleText("label: Old Label\n", "New Label")).toBe(
      'label: "New Label"\n',
    );
    expect(
      updateMetadataTitleText(
        "settings:\n  category: country\n",
        "Named Object",
      ),
    ).toBe('title: "Named Object"\nsettings:\n  category: country\n');
  });
});
