import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";
import { createTranslator, type Locale } from "../i18n";
import type { ModuleEntity } from "./model";
import { ModuleEntityDetails } from "./ModuleEntityDetails";

const entity: ModuleEntity = {
  id: "ideas:IDEA_BETA",
  familyId: "ideas",
  family: "idea",
  moduleId: "idea/IDEA_BETA",
  objectId: "IDEA_BETA",
  title: "Beta Law",
  titleKeys: ["IDEA_BETA"],
  subtitle: "IDEA_BETA",
  root: "/workspace/projects/PIHC3/src/common/ideas",
  relativeRoot: "src/common/ideas",
  layout: "family_root",
  sourceCount: 3,
  sourceSlots: [
    {
      slot: "def",
      name: "ideas.pdx",
      path: "/workspace/projects/PIHC3/src/common/ideas/ideas.pdx",
      relative_path: "src/common/ideas/ideas.pdx",
      extension: "pdx",
      draftKey: "def",
      editorKind: "code",
    },
    {
      slot: "icon",
      name: "GFX_idea_beta.dds",
      path: "/workspace/projects/PIHC3/src/gfx/interface/ideas/GFX_idea_beta.dds",
      relative_path: "src/gfx/interface/ideas/GFX_idea_beta.dds",
      extension: "dds",
      draftKey: "icon",
      editorKind: "image",
    },
    {
      slot: "loc",
      name: "ideas_l_english.yml",
      path: "/workspace/projects/PIHC3/src/localisation/english/ideas_l_english.yml",
      relative_path: "src/localisation/english/ideas_l_english.yml",
      extension: "yml",
      draftKey: "loc",
      editorKind: "localization",
    },
  ],
  tags: [],
  draftState: "clean",
  drafts: {
    text: {
      loc: 'l_english:\n IDEA_BETA:0 "Beta Law"\n IDEA_BETA_desc:0 "A national spirit description that wraps across several compact table lines so the textarea starts tall enough to show all text."\n',
    },
  },
};

function renderDetails(
  targetSourcePath = "",
  collectionOptions: Array<{ label: string; value: string }> = [],
  canChangeCollection = false,
) {
  const t = createTranslator("zh");
  return renderToStaticMarkup(
    <ModuleEntityDetails
      activeDiagramNodeId=""
      applyBusy={false}
      applyError=""
      canApply={false}
      canChangeCollection={canChangeCollection}
      collectionOptions={collectionOptions}
      entity={entity}
      locale="zh"
      onApply={() => undefined}
      onImageDraft={() => undefined}
      onInfoDraft={() => undefined}
      onRefresh={() => undefined}
      onRestore={() => undefined}
      onTextDraft={() => undefined}
      openTarget="finder"
      projectId="PIHC3"
      projectRoot="/workspace/projects/PIHC3"
      sourceReloadKey={0}
      targetSourcePath={targetSourcePath}
      t={t}
      theme="light"
    />,
  );
}

function renderCustomDetails(
  customEntity: ModuleEntity,
  locale: Locale = "zh",
  targetSourcePath = "",
  applyBusy = false,
  applyError = "",
  onBuild?: () => void,
) {
  const t = createTranslator(locale);
  return renderToStaticMarkup(
    <ModuleEntityDetails
      activeDiagramNodeId=""
      applyBusy={applyBusy}
      applyError={applyError}
      buildAffectedFamilyTitle="Ideas"
      canApply={false}
      entity={customEntity}
      locale={locale}
      onApply={() => undefined}
      onBuildAffected={onBuild}
      onBuildModule={onBuild}
      onImageDraft={() => undefined}
      onInfoDraft={() => undefined}
      onRefresh={() => undefined}
      onRestore={() => undefined}
      onTextDraft={() => undefined}
      openTarget="finder"
      projectId="PIHC3"
      projectRoot="/workspace/projects/PIHC3"
      sourceReloadKey={0}
      targetSourcePath={targetSourcePath}
      t={t}
      theme="light"
    />,
  );
}

function renderFocusDetailsWithManySources(locale: Locale = "en") {
  const focusEntity: ModuleEntity = {
    ...entity,
    id: "focus_tree:C01_MAIN",
    familyId: "focuses",
    family: "focus_tree",
    objectId: "C01_MAIN",
    title: "C01 Main",
    subtitle: "C01_MAIN",
    root: "/workspace/projects/PIHC3/src/modules/focus_tree/C01_MAIN",
    relativeRoot: "src/modules/focus_tree/C01_MAIN",
    sourceCount: 19,
    sourceSlots: [
      {
        slot: "meta",
        name: "meta.yaml",
        path: "/workspace/projects/PIHC3/src/modules/focus_tree/C01_MAIN/meta.yaml",
        relative_path: "src/modules/focus_tree/C01_MAIN/meta.yaml",
        extension: "yaml",
        draftKey: "meta",
        editorKind: "code",
      },
      ...Array.from({ length: 18 }, (_, index) => {
        const id = `FOCUS_C01_${String(index + 1).padStart(2, "0")}`;
        return {
          slot: `focus:${id}:info`,
          name: `${id} info.json`,
          path: `/workspace/projects/PIHC3/src/modules/focus_tree/C01_MAIN/legacy/${id}/info.json`,
          relative_path: `src/modules/focus_tree/C01_MAIN/legacy/${id}/info.json`,
          extension: "json",
          draftKey: `focus:${id}:info`,
          editorKind: "code" as const,
        };
      }),
    ],
  };
  const t = createTranslator(locale);
  return renderToStaticMarkup(
    <ModuleEntityDetails
      activeDiagramNodeId=""
      applyBusy={false}
      applyError=""
      canApply={false}
      entity={focusEntity}
      locale={locale}
      onApply={() => undefined}
      onImageDraft={() => undefined}
      onInfoDraft={() => undefined}
      onRefresh={() => undefined}
      onRestore={() => undefined}
      onTextDraft={() => undefined}
      openTarget="finder"
      projectId="PIHC3"
      projectRoot="/workspace/projects/PIHC3"
      sourceReloadKey={0}
      targetSourcePath="src/modules/focus_tree/C01_MAIN/legacy/FOCUS_C01_12/info.json"
      t={t}
      theme="light"
    />,
  );
}

describe("ModuleEntityDetails", () => {
  it("shows collection membership as a guarded picker instead of hidden metadata", () => {
    const markup = renderDetails(
      "",
      [
        { label: "C01 Focus Tree", value: "C01_focus_tree" },
        { label: "C02 Focus Tree", value: "C02_focus_tree" },
      ],
      true,
    );

    expect(markup).toContain("合集");
    expect(markup).toContain("不属于合集");
    expect(markup).toContain("C01 Focus Tree");
    expect(markup).toContain("C02 Focus Tree");
    expect(markup).not.toContain(".paradev/meta.yaml");
  });

  it("keeps raw meta.yaml behind an advanced source while preserving direct access", () => {
    const metadataPath =
      "/workspace/projects/PIHC3/src/modules/idea/IDEA_BETA/meta.yaml";
    const definitionPath =
      "/workspace/projects/PIHC3/src/modules/idea/IDEA_BETA/def.txt";
    const metadataEntity: ModuleEntity = {
      ...entity,
      root: "/workspace/projects/PIHC3/src/modules/idea/IDEA_BETA",
      relativeRoot: "src/modules/idea/IDEA_BETA",
      sourceCount: 2,
      sourceSlots: [
        {
          slot: "meta",
          name: "meta.yaml",
          path: metadataPath,
          relative_path: "src/modules/idea/IDEA_BETA/meta.yaml",
          extension: "yaml",
          draftKey: "meta",
          editorKind: "code",
        },
        {
          slot: "def",
          name: "def.txt",
          path: definitionPath,
          relative_path: "src/modules/idea/IDEA_BETA/def.txt",
          extension: "txt",
          draftKey: "def",
          editorKind: "code",
        },
      ],
    };

    const ordinaryMarkup = renderCustomDetails(
      metadataEntity,
      "en",
      definitionPath,
    );
    const metadataMarkup = renderCustomDetails(
      metadataEntity,
      "en",
      metadataPath,
    );

    expect(ordinaryMarkup).toContain('type="button">Definition</button>');
    expect(ordinaryMarkup).toContain(
      'class="source-tab source-tab-advanced" title="Open meta.yaml. ParaDev already infers the module family and ID from its folder; edit this file only for explicit overrides." type="button">Advanced metadata</button>',
    );
    expect(ordinaryMarkup).not.toContain('type="button">meta.yaml</button>');
    expect(metadataMarkup).toContain(
      'class="source-tab source-tab-advanced selected" title="Open meta.yaml. ParaDev already infers the module family and ID from its folder; edit this file only for explicit overrides." type="button">Advanced metadata</button>',
    );
  });

  it("does not promise or create visible metadata for a title-only draft", () => {
    const metadataFreeEntity: ModuleEntity = {
      ...entity,
      id: "ideas:IDEA_MINIMAL",
      moduleId: "idea/IDEA_MINIMAL",
      objectId: "IDEA_MINIMAL",
      title: "Minimal Idea",
      subtitle: "IDEA_MINIMAL",
      root: "/workspace/projects/PIHC3/src/modules/idea/IDEA_MINIMAL",
      relativeRoot: "src/modules/idea/IDEA_MINIMAL",
      layout: "canonical",
      sourceCount: 1,
      sourceSlots: [
        {
          slot: "def",
          name: "def.pdx",
          path: "/workspace/projects/PIHC3/src/modules/idea/IDEA_MINIMAL/def.pdx",
          relative_path: "src/modules/idea/IDEA_MINIMAL/def.pdx",
          extension: "pdx",
          draftKey: "def",
          editorKind: "code",
        },
      ],
      drafts: { text: {} },
    };

    const english = renderCustomDetails(metadataFreeEntity, "en");
    const chinese = renderCustomDetails(metadataFreeEntity, "zh");
    const pending = renderCustomDetails(
      {
        ...metadataFreeEntity,
        draftState: "modified",
        drafts: {
          text: {},
          info: { title: "Renamed Idea" },
        },
      },
      "en",
    );

    for (const markup of [english, chinese, pending]) {
      expect(markup).not.toContain("meta.yaml with only the title");
      expect(markup).not.toContain("entity-metadata-title-hint");
      expect(markup).not.toContain("才会为此模块创建元数据");
    }
  });

  it("offers duplication only for a clean supported module", () => {
    const cleanMarkup = renderToStaticMarkup(
      <ModuleEntityDetails
        activeDiagramNodeId=""
        applyBusy={false}
        applyError=""
        canApply={false}
        canDuplicate
        entity={entity}
        locale="en"
        onApply={() => undefined}
        onDuplicate={() => undefined}
        onImageDraft={() => undefined}
        onInfoDraft={() => undefined}
        onRefresh={() => undefined}
        onRestore={() => undefined}
        onTextDraft={() => undefined}
        openTarget="finder"
        projectId="PIHC3"
        projectRoot="/workspace/projects/PIHC3"
        sourceReloadKey={0}
        t={createTranslator("en")}
        theme="light"
      />,
    );
    const dirtyMarkup = renderToStaticMarkup(
      <ModuleEntityDetails
        activeDiagramNodeId=""
        applyBusy={false}
        applyError=""
        canApply={false}
        canDuplicate
        entity={{ ...entity, draftState: "modified" }}
        locale="en"
        onApply={() => undefined}
        onDuplicate={() => undefined}
        onImageDraft={() => undefined}
        onInfoDraft={() => undefined}
        onRefresh={() => undefined}
        onRestore={() => undefined}
        onTextDraft={() => undefined}
        openTarget="finder"
        projectId="PIHC3"
        projectRoot="/workspace/projects/PIHC3"
        sourceReloadKey={0}
        t={createTranslator("en")}
        theme="light"
      />,
    );

    expect(cleanMarkup).toContain(">Duplicate<");
    expect(cleanMarkup).toContain(
      "Copy this clean module folder after reviewing an exact file plan.",
    );
    expect(dirtyMarkup).toContain(
      'disabled="" title="Apply or discard this draft before duplicating the module."',
    );
  });

  it("offers module and family rebuild actions only after the draft is clean", () => {
    const cleanMarkup = renderCustomDetails(
      entity,
      "en",
      "",
      false,
      "",
      () => undefined,
    );
    const dirtyMarkup = renderCustomDetails(
      { ...entity, draftState: "modified" },
      "en",
      "",
      false,
      "",
      () => undefined,
    );

    expect(cleanMarkup).toContain('data-paradev-build-target-kind="module"');
    expect(cleanMarkup).toContain("Build module");
    expect(cleanMarkup).toContain("Open Build and rebuild only IDEA_BETA.");
    expect(cleanMarkup).toContain('data-paradev-build-target-kind="family"');
    expect(cleanMarkup).toContain("Build affected Ideas output");
    expect(cleanMarkup).toContain(
      "Open Build and rebuild the entire Ideas family, including aggregate output.",
    );
    expect(dirtyMarkup).toMatch(
      /data-paradev-build-target-kind="module"[^>]*disabled=""/,
    );
    expect(dirtyMarkup).toContain(
      "Apply or discard this draft before rebuilding IDEA_BETA.",
    );
    expect(dirtyMarkup).toMatch(
      /data-paradev-build-target-kind="family"[^>]*disabled=""/,
    );
    expect(dirtyMarkup).toContain(
      "Apply or discard this draft before building the affected Ideas output.",
    );
  });

  it("announces selected-row source hydration without showing an empty editor", () => {
    const markup = renderToStaticMarkup(
      <ModuleEntityDetails
        activeDiagramNodeId=""
        applyBusy={false}
        applyError=""
        canApply={false}
        entity={null}
        loading
        locale="en"
        onApply={() => undefined}
        onImageDraft={() => undefined}
        onInfoDraft={() => undefined}
        onRefresh={() => undefined}
        onRestore={() => undefined}
        onTextDraft={() => undefined}
        openTarget="finder"
        projectId="PIHC3"
        projectRoot="/workspace/projects/PIHC3"
        sourceReloadKey={0}
        t={createTranslator("en")}
        theme="light"
      />,
    );

    expect(markup).toContain('aria-busy="true"');
    expect(markup).toContain('role="status"');
    expect(markup).toContain("Loading editor sources…");
    expect(markup).not.toContain("Select an object to edit");
  });

  it("opens the info page first and translates source slot tabs in Chinese", () => {
    const markup = renderDetails();

    expect(markup).toContain('aria-label="条目编辑器"');
    expect(markup).toContain('lang="zh-CN"');
    expect(markup).toContain('aria-label="源编辑标签页"');
    expect(markup).toContain(">信息<");
    expect(markup).toContain(">定义<");
    expect(markup).toContain(">翻译<");
    expect(markup).toContain(">图片<");
    expect(markup).toContain("IDEA_BETA");
    expect(markup).toContain("GFX_idea_beta.dds");
    expect(markup).toContain("src/common/ideas");
    expect(markup).not.toContain("src/gfx/interface/ideas/GFX_idea_beta.png");
    expect(markup).toContain(">名称<");
    expect(markup).toContain(">路径<");
    expect(markup).toContain("使用 @ 表示当前条目 ID：IDEA_BETA");
    expect(markup).not.toContain("(@ = IDEA_BETA)");
    expect(markup).toContain('aria-label="添加翻译行"');
    expect(markup).toContain("此条目还没有加载到翻译文本。");
    expect(markup).not.toContain('class="entity-path-line"');
    expect(markup).not.toContain(">布局<");
    expect(markup).not.toContain(">源文件<");
    expect(markup).not.toContain("Entity editor");
    expect(markup).not.toContain("Source editor tabs");
    expect(markup).toMatch(/readOnly|readonly/);
  });

  it("renders localization source tabs with friendly labels", () => {
    const bilingualEntity: ModuleEntity = {
      ...entity,
      sourceSlots: [
        ...entity.sourceSlots,
        {
          slot: "loc_zh",
          name: "ideas_l_simp_chinese.yml",
          path: "/workspace/projects/PIHC3/src/localisation/simp_chinese/ideas_l_simp_chinese.yml",
          relative_path:
            "src/localisation/simp_chinese/ideas_l_simp_chinese.yml",
          extension: "yml",
          draftKey: "loc_zh",
          editorKind: "localization",
        },
      ],
      drafts: {
        text: {
          ...entity.drafts.text,
          loc_zh: 'l_simp_chinese:\n IDEA_BETA:0 "贝塔法案"\n',
        },
      },
    };
    const markup = renderCustomDetails(bilingualEntity, "zh");

    expect(markup).toContain(">简体中文翻译</button>");
    expect(markup).not.toContain(">loc_zh</button>");

    const englishMarkup = renderCustomDetails(bilingualEntity, "en");
    expect(englishMarkup).toContain(
      ">Simplified Chinese localization</button>",
    );
  });

  it("opens a requested source path as the active source tab", () => {
    const markup = renderDetails("src/common/ideas/ideas.pdx");

    expect(markup).toContain(
      'class="source-tab selected" type="button">定义</button>',
    );
    expect(markup).toContain("加载编辑器");
    expect(markup).not.toContain(
      'class="source-tab selected" type="button">信息</button>',
    );
    expect(markup).not.toContain("Loading editor");
  });

  it("keeps duplicate source slots as distinct path-addressable tabs", () => {
    const englishPath = "src/localisation/english/ideas_l_english.yml";
    const chinesePath =
      "src/localisation/simp_chinese/ideas_l_simp_chinese.yml";
    const duplicateLocalizationEntity: ModuleEntity = {
      ...entity,
      sourceCount: 4,
      sourceSlots: [
        entity.sourceSlots[0],
        entity.sourceSlots[1],
        {
          ...entity.sourceSlots[2],
          draftKey: `loc::${englishPath}`,
        },
        {
          slot: "loc",
          name: "ideas_l_simp_chinese.yml",
          path: `/workspace/projects/PIHC3/${chinesePath}`,
          relative_path: chinesePath,
          extension: "yml",
          draftKey: `loc::${chinesePath}`,
          editorKind: "localization",
        },
      ],
      drafts: {
        text: {
          [`loc::${englishPath}`]: 'l_english:\n IDEA_BETA:0 "Beta Law"\n',
          [`loc::${chinesePath}`]: 'l_simp_chinese:\n IDEA_BETA:0 "贝塔法案"\n',
        },
      },
    };

    const markup = renderCustomDetails(
      duplicateLocalizationEntity,
      "en",
      chinesePath,
    );

    expect(markup).toContain(
      ">English localization · ideas_l_english.yml</button>",
    );
    expect(markup).toContain(
      'class="source-tab selected" type="button">Simplified Chinese localization · ideas_l_simp_chinese.yml</button>',
    );
    expect(markup).not.toContain(
      'class="source-tab selected" type="button">English localization · ideas_l_english.yml</button>',
    );
  });

  it("selects the requested image source instead of always targeting the first image", () => {
    const firstPath = "src/gfx/interface/ideas/GFX_idea_beta.dds";
    const secondPath = "src/gfx/interface/ideas/GFX_idea_beta_large.png";
    const firstKey = `image::${firstPath}`;
    const secondKey = `image::${secondPath}`;
    const multiImageEntity: ModuleEntity = {
      ...entity,
      sourceCount: 4,
      sourceSlots: [
        entity.sourceSlots[0],
        {
          ...entity.sourceSlots[1],
          slot: "image",
          draftKey: firstKey,
        },
        {
          slot: "image",
          name: "GFX_idea_beta_large.png",
          path: `/workspace/projects/PIHC3/${secondPath}`,
          relative_path: secondPath,
          extension: "png",
          draftKey: secondKey,
          editorKind: "image",
        },
        entity.sourceSlots[2],
      ],
    };

    const markup = renderCustomDetails(multiImageEntity, "en", secondPath);

    expect(markup).toContain(
      'class="source-tab selected" type="button">Image</button>',
    );
    expect(markup).toContain(
      'class="source-tab-source-picker image-source-picker"',
    );
    expect(markup).toContain('aria-label="Image"');
    expect(markup).toContain(`value="${secondKey}" selected`);
    expect(markup).toContain(">GFX_idea_beta_large.png</option>");
    expect(markup).toContain(">GFX_idea_beta.dds</option>");
    expect(markup).not.toContain("image-editor-unavailable");
    expect(markup).not.toContain("format-aware conversion is required");
  });

  it("opens the image editor for a selected DDS source in English and Chinese", () => {
    const ddsPath = entity.sourceSlots[1].relative_path;
    const englishMarkup = renderCustomDetails(entity, "en", ddsPath);
    const chineseMarkup = renderCustomDetails(entity, "zh", ddsPath);

    expect(englishMarkup).not.toContain("image-editor-unavailable");
    expect(englishMarkup).toContain("Loading editor");
    expect(chineseMarkup).not.toContain("image-editor-unavailable");
    expect(chineseMarkup).toContain("加载编辑器");
  });

  it("keeps rare module editor branch labels translated", () => {
    const t = createTranslator("zh");

    expect(t("workspace.module.editor.imageDraftOnly")).toBe("草稿图片替换");
    expect(
      t("workspace.module.editor.openFailed", { message: "权限不足" }),
    ).toBe("打开失败：权限不足");
  });

  it("locks starter source and asset editing until the scaffold has been applied", () => {
    const starterEntity: ModuleEntity = {
      ...entity,
      id: "new:entity/ENTITY_TEST",
      familyId: "entity",
      family: "entity",
      moduleId: "entity/ENTITY_TEST",
      objectId: "ENTITY_TEST",
      title: "Entity Test",
      subtitle: "ENTITY_TEST",
      draftState: "new",
      sourceCount: 1,
      sourceSlots: [
        {
          slot: "def",
          name: "mesh.gfx",
          path: "/workspace/projects/PIHC3/src/modules/entity/ENTITY_TEST/gfx/models/ENTITY_TEST/mesh.gfx",
          relative_path:
            "src/modules/entity/ENTITY_TEST/gfx/models/ENTITY_TEST/mesh.gfx",
          extension: "gfx",
          draftKey: "def",
          editorKind: "code",
        },
      ],
      resourceSlots: [
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
      ],
    };
    const markup = renderCustomDetails(
      starterEntity,
      "en",
      starterEntity.sourceSlots[0].relative_path,
    );

    expect(markup).toContain("Create the starter files first");
    expect(markup).toContain(
      "unlock the generated PDX files and the Assets tab",
    );
    expect(markup).toContain(
      'class="source-tab selected" disabled="" type="button">Definition</button>',
    );
    expect(markup).toContain(
      'class="source-tab" disabled="" type="button">Assets</button>',
    );
    expect(markup).not.toContain("source-editor-panel");
    expect(markup).not.toContain("asset-draft-editor");
  });

  it("shows record-only Entity modules without an irrelevant Assets tab", () => {
    const recordPath = "src/modules/entity/VIENTO_AIRSHIP_C11/record.json";
    const recordEntity: ModuleEntity = {
      ...entity,
      id: "module:entity/VIENTO_AIRSHIP_C11",
      familyId: "entity",
      family: "entity",
      moduleId: "entity/VIENTO_AIRSHIP_C11",
      objectId: "VIENTO_AIRSHIP_C11",
      title: "Viento Airship C11",
      subtitle: "VIENTO_AIRSHIP_C11",
      root: "/workspace/projects/PIHC3/src/modules/entity/VIENTO_AIRSHIP_C11",
      relativeRoot: "src/modules/entity/VIENTO_AIRSHIP_C11",
      sourceCount: 2,
      sourceSlots: [
        {
          slot: "meta",
          name: "meta.yaml",
          path: "/workspace/projects/PIHC3/src/modules/entity/VIENTO_AIRSHIP_C11/meta.yaml",
          relative_path: "src/modules/entity/VIENTO_AIRSHIP_C11/meta.yaml",
          extension: "yaml",
          draftKey: "meta",
          editorKind: "code",
        },
        {
          slot: "record",
          name: "record.json",
          path: `/workspace/projects/PIHC3/${recordPath}`,
          relative_path: recordPath,
          extension: "json",
          draftKey: "record",
          editorKind: "code",
        },
      ],
      drafts: { text: {} },
    };
    const markup = renderCustomDetails(recordEntity, "en", recordPath);

    expect(markup).toContain(
      'class="source-tab selected" type="button">record</button>',
    );
    expect(markup).toContain("Loading editor");
    expect(markup).not.toContain('type="button">Assets</button>');
  });

  it("keeps the Assets tab for aggregate Entity modules with binary sources", () => {
    const aggregateEntity: ModuleEntity = {
      ...entity,
      id: "module:entity/HOI4DEV_ENTITIES",
      familyId: "entity",
      family: "entity",
      moduleId: "entity/HOI4DEV_ENTITIES",
      objectId: "HOI4DEV_ENTITIES",
      title: "Shared entities",
      subtitle: "HOI4DEV_ENTITIES",
      sourceCount: 1,
      sourceSlots: [
        {
          slot: "meshes",
          name: "mesh.mesh",
          path: "/workspace/projects/PIHC3/src/modules/entity/HOI4DEV_ENTITIES/gfx/models/viento/air/airship/mesh.mesh",
          relative_path:
            "src/modules/entity/HOI4DEV_ENTITIES/gfx/models/viento/air/airship/mesh.mesh",
          extension: "mesh",
          slot_kinds: ["copy"],
          draftKey: "meshes",
          editorKind: "asset",
        },
      ],
      drafts: { text: {} },
    };
    const markup = renderCustomDetails(aggregateEntity, "en");

    expect(markup).toContain('type="button">Assets</button>');
  });

  it("makes the editing body inert while an apply is in flight", () => {
    const markup = renderCustomDetails(
      { ...entity, draftState: "modified" },
      "en",
      entity.sourceSlots[0].relative_path,
      true,
    );

    expect(markup).toContain('aria-busy="true"');
    expect(markup).toContain('class="entity-editor-body" inert=""');
    expect(markup).toContain(
      'aria-label="Refresh entity" class="toolbar-button icon-only" disabled=""',
    );
    expect(markup).toContain('class="toolbar-button warning" disabled=""');
    expect(markup).toContain(">Applying</button>");
  });

  it("announces Apply failures as alerts", () => {
    const markup = renderCustomDetails(
      { ...entity, draftState: "modified" },
      "en",
      entity.sourceSlots[0].relative_path,
      false,
      "meta.yaml: invalid YAML",
    );

    expect(markup).toContain('role="alert"');
    expect(markup).toContain("Apply failed: meta.yaml: invalid YAML");
  });

  it("collapses large source-backed focus file lists into a source selector", () => {
    const markup = renderFocusDetailsWithManySources();

    expect(markup).toContain('class="source-tab-source-picker"');
    expect(markup).toContain(
      'class="select-field compact source-tab-source-select"',
    );
    expect(markup).toContain('aria-label="Source file"');
    expect(markup).toContain('value="focus:FOCUS_C01_12:info" selected');
    expect(markup).toContain(">FOCUS_C01_12 info<");
    expect(markup).toContain('<option value="meta">Advanced metadata</option>');
    expect(markup).toContain('class="source-tab-source-path"');
    expect(markup).toContain(
      "src/modules/focus_tree/C01_MAIN/legacy/FOCUS_C01_12/info.json",
    );
    expect(markup).not.toContain(
      'class="source-tab-source-picker"><span>Source file</span><select',
    );
    expect(markup).not.toContain('type="button">FOCUS_C01_01 info</button>');
    expect(markup).not.toContain('type="button">FOCUS_C01_18 info</button>');
  });

  it("translates focus info source labels in Chinese", () => {
    const markup = renderFocusDetailsWithManySources("zh");

    expect(markup).toContain('aria-label="源文件"');
    expect(markup).toContain(">FOCUS_C01_12 信息<");
    expect(markup).not.toContain('aria-label="Source file"');
    expect(markup).not.toContain(">FOCUS_C01_12 info<");
  });
});
