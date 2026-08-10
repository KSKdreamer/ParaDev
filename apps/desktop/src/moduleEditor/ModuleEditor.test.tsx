import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";
import { createTranslator } from "../i18n";
import * as ModuleEditorExports from "./ModuleEditor";
import { ModuleEditor, buildDiagramApplyDraftPlan, buildDiagramChangedEntities, diagnosticSummary, moduleSelectionTargetForEntity, rootDiagramFocusNodeInput, shouldShowProjectDiagram } from "./ModuleEditor";
import { moveDiagramNode, type DiagramDocument } from "../diagramEditor/layoutModel";
import { buildProjectDiagramDocument } from "../diagramEditor/projectDiagram";
import { buildModuleEntities } from "./model";
import type { ProjectBrowserPayload } from "../types";

const technologyBrowser: ProjectBrowserPayload = {
  schema: "paradev.sdk.project-browser.v1",
  project_id: "PIHC3",
  title: "The Pony In The High Castle",
  root: "/workspace/projects/PIHC3",
  profile: "hoi4",
  filters: {},
  diagnostics: [],
  families: [
    {
      id: "technologies",
      family: "technology",
      title: "Technologies",
      title_key: "modules.technologies.title",
      item_count: 2,
      source_count: 2,
      layouts: ["canonical"],
      diagram: {
        id: "technology",
        aliases: ["technologies"],
        renderer: "technology",
        title: "Technology tree",
        editable: true,
        authoring_kind: "module"
      }
    }
  ],
  items: [
    {
      id: "technology:TECH_ROOT",
      kind: "module",
      layout: "canonical",
      family_id: "technologies",
      family: "technology",
      object_id: "TECH_ROOT",
      module_id: "TECH_ROOT",
      title: "Root Technology",
      root: "/workspace/projects/PIHC3/src/modules/technology/TECH_ROOT",
      relative_root: "src/modules/technology/TECH_ROOT",
      source_count: 1,
      sources: [],
      metadata: { settings: { folder_position: { x: 1, y: 1 }, path_target_ids: ["TECH_CHILD"] } }
    },
    {
      id: "technology:TECH_CHILD",
      kind: "module",
      layout: "canonical",
      family_id: "technologies",
      family: "technology",
      object_id: "TECH_CHILD",
      module_id: "TECH_CHILD",
      title: "Child Technology",
      root: "/workspace/projects/PIHC3/src/modules/technology/TECH_CHILD",
      relative_root: "src/modules/technology/TECH_CHILD",
      source_count: 1,
      sources: [],
      metadata: { settings: { folder_position: { x: 4, y: 1 }, dependency_ids: ["TECH_ROOT"] } }
    }
  ]
};

const doctrineBrowser: ProjectBrowserPayload = {
  schema: "paradev.sdk.project-browser.v1",
  project_id: "PIHC3",
  title: "The Pony In The High Castle",
  root: "/workspace/projects/PIHC3",
  profile: "hoi4",
  filters: {},
  diagnostics: [],
  families: [
    {
      id: "doctrines",
      family: "doctrine",
      title: "Doctrines",
      title_key: "modules.doctrines.title",
      item_count: 2,
      source_count: 4,
      layouts: ["canonical"],
      diagram: {
        id: "doctrine",
        aliases: ["doctrines"],
        renderer: "doctrine",
        title: "Doctrine tree",
        editable: true,
        authoring_kind: "module"
      }
    }
  ],
  items: [
    {
      id: "doctrine:DOCTRINE_AIR_ROOT",
      kind: "module",
      layout: "canonical",
      family_id: "doctrines",
      family: "doctrine",
      object_id: "DOCTRINE_AIR_ROOT",
      module_id: "doctrine/DOCTRINE_AIR_ROOT",
      title: "Open Sky",
      root: "/workspace/projects/PIHC3/src/modules/doctrine/DOCTRINE_AIR_ROOT",
      relative_root: "src/modules/doctrine/DOCTRINE_AIR_ROOT",
      source_count: 2,
      sources: [],
      metadata: {
        settings: {
          source_position: { x: 0, y: 0 },
          source_leads_to_by_path: { path: "DOCTRINE_AIR_CHILD" }
        }
      }
    },
    {
      id: "doctrine:DOCTRINE_AIR_CHILD",
      kind: "module",
      layout: "canonical",
      family_id: "doctrines",
      family: "doctrine",
      object_id: "DOCTRINE_AIR_CHILD",
      module_id: "doctrine/DOCTRINE_AIR_CHILD",
      title: "Look Up",
      root: "/workspace/projects/PIHC3/src/modules/doctrine/DOCTRINE_AIR_CHILD",
      relative_root: "src/modules/doctrine/DOCTRINE_AIR_CHILD",
      source_count: 2,
      sources: [],
      metadata: { settings: { source_position: { x: -2, y: 2 } } }
    }
  ]
};

const focusBrowser: ProjectBrowserPayload = {
  schema: "paradev.sdk.project-browser.v1",
  project_id: "PIHC3",
  title: "The Pony In The High Castle",
  root: "/workspace/projects/PIHC3",
  profile: "hoi4",
  filters: {},
  diagnostics: [],
  families: [
    {
      id: "focuses",
      family: "focus",
      title: "Focuses",
      title_key: "modules.focuses.title",
      item_count: 1,
      source_count: 1,
      layouts: ["canonical"],
      diagram: {
        id: "focus_tree",
        aliases: ["focus", "focuses"],
        renderer: "focus-tree",
        title: "Focus tree",
        editable: true,
        authoring_kind: "diagram-node",
        scope_authoring_kind: "collection"
      }
    }
  ],
  items: [
    {
      id: "focus_tree:C08_PARTIV",
      kind: "module",
      layout: "canonical",
      family_id: "focuses",
      family: "focus_tree",
      object_id: "C08_PARTIV",
      module_id: "C08_PARTIV",
      title: "C08 Part IV",
      root: "/workspace/projects/PIHC3/src/modules/focus_tree/C08_PARTIV",
      relative_root: "src/modules/focus_tree/C08_PARTIV",
      source_count: 1,
      sources: [],
      metadata: {
        settings: {
          focuses: [
            { id: "FOCUS_C08_CANTERLOT_MIND", x: "12", y: "0" },
            { id: "FOCUS_C08_SECOND_SUMMIT", x: "12", y: "1", prerequisites: ["FOCUS_C08_CANTERLOT_MIND"] }
          ]
        }
      }
    }
  ]
};

const focusTreeContextDocument: DiagramDocument = {
  schemaVersion: 1,
  gridSizePx: 24,
  nodes: [
    {
      id: "C08_PARTIV",
      order: 0,
      mode: "auto",
      width: 6,
      height: 2,
      title: "C08 Part IV",
      payload: {
        family: "focus",
        familyId: "focuses",
        itemId: "focus_tree:C08_PARTIV",
        itemKind: "module",
        objectId: "C08_PARTIV",
        projectId: "PIHC3",
        relativeRoot: "src/modules/focus_tree/C08_PARTIV",
        sourceRootRelativePath: "src/modules/focus_tree/C08_PARTIV"
      }
    }
  ],
  edges: []
};

const emptyDiagramDocument: DiagramDocument = {
  schemaVersion: 1,
  gridSizePx: 24,
  nodes: [],
  edges: []
};

describe("ModuleEditor diagram integration", () => {
  it("localizes blocked scaffold plan fallback messages", () => {
    const zh = createTranslator("zh");
    const en = createTranslator("en");

    expect(diagnosticSummary(zh, [])).toBe("草稿计划被阻塞。");
    expect(diagnosticSummary(en, [])).toBe("Draft plan is blocked.");
    expect(diagnosticSummary(zh, [{ message: "Object ID already exists." }])).toBe("Object ID already exists.");
  });

  it("shows a scoped diagram loading state before the SDK unavailable fallback", () => {
    const markup = renderToStaticMarkup(
      <ModuleEditor
        browser={null}
        familyId="focuses"
        familyTitle="National Focuses"
        loading
        locale="en"
        onPinTab={() => undefined}
        onProjectRefresh={async () => undefined}
        openTarget="cursor"
        surface="diagram"
        templates={null}
        t={createTranslator("en")}
        theme="light"
      />
    );

    expect(markup).toContain('class="empty-tab-panel module-loading-panel"');
    expect(markup).toContain('role="status"');
    expect(markup).toContain('aria-busy="true"');
    expect(markup).toContain("Loading National Focuses diagram");
    expect(markup).toContain("Fetching scoped diagram data from the ParaDev SDK.");
    expect(markup).not.toContain("SDK browser unavailable");
  });

  it("renders the SDK unavailable fallback in Chinese", () => {
    const markup = renderToStaticMarkup(
      <ModuleEditor
        browser={null}
        familyId="focuses"
        locale="zh"
        onPinTab={() => undefined}
        onProjectRefresh={async () => undefined}
        openTarget="cursor"
        templates={null}
        t={createTranslator("zh")}
        theme="light"
      />
    );

    expect(markup).toContain("SDK 浏览数据不可用");
    expect(markup).toContain("打开 ParaDev 桌面应用以加载本地 SDK 项目数据。");
    expect(markup).not.toContain("SDK browser unavailable");
  });

  it("renders scoped SDK load failures before the generic unavailable fallback", () => {
    const markup = renderToStaticMarkup(
      <ModuleEditor
        browser={null}
        familyId="focuses"
        loadError="Scoped SDK data could not be loaded: bridge denied"
        locale="en"
        onPinTab={() => undefined}
        onProjectRefresh={async () => undefined}
        openTarget="cursor"
        surface="diagram"
        templates={null}
        t={createTranslator("en")}
        theme="light"
      />
    );

    expect(markup).toContain('role="alert"');
    expect(markup).toContain("Diagram data failed to load");
    expect(markup).toContain("Scoped SDK data could not be loaded: bridge denied");
    expect(markup).not.toContain("SDK browser unavailable");
  });

  it("keeps the normal module tab separate from the diagram editor", () => {
    const markup = renderToStaticMarkup(
      <ModuleEditor
        browser={technologyBrowser}
        familyId="technologies"
        locale="en"
        onPinTab={() => undefined}
        onProjectRefresh={async () => undefined}
        openTarget="cursor"
        templates={null}
        t={createTranslator("en")}
        theme="light"
      />
    );

    expect(markup).toContain('class="module-editor"');
    expect(markup).not.toContain('class="module-editor with-diagram"');
    expect(markup).not.toContain('class="project-diagram-panel"');
    expect(markup).toContain('class="module-editor-grid"');
  });

  it("does not render legacy technology metadata before the SDK projection loads", () => {
    const markup = renderToStaticMarkup(
      <ModuleEditor
        browser={technologyBrowser}
        familyId="technologies"
        locale="en"
        onPinTab={() => undefined}
        onProjectRefresh={async () => undefined}
        openTarget="cursor"
        surface="diagram"
        templates={null}
        t={createTranslator("en")}
        theme="light"
      />
    );

    expect(markup).toContain('class="module-editor diagram-editor"');
    expect(markup).toContain("No diagram nodes");
    expect(markup).not.toContain('data-node-id="TECH_CHILD"');
    expect(markup).not.toContain("Technology tree diagram");
    expect(markup).not.toContain('class="diagram-scope-select"');
  });

  it("does not render legacy Doctrine metadata before the SDK projection loads", () => {
    const markup = renderToStaticMarkup(
      <ModuleEditor
        browser={doctrineBrowser}
        familyId="doctrines"
        locale="en"
        onPinTab={() => undefined}
        onProjectRefresh={async () => undefined}
        openTarget="cursor"
        surface="diagram"
        templates={null}
        t={createTranslator("en")}
        theme="light"
      />
    );

    expect(markup).toContain('class="module-editor diagram-editor"');
    expect(markup).toContain("No diagram nodes");
    expect(markup).not.toContain(
      'data-node-id="DOCTRINE_AIR_ROOT"'
    );
    expect(markup).not.toContain(
      'data-node-id="DOCTRINE_AIR_CHILD"'
    );
    expect(markup).not.toContain("Doctrine tree diagram");
  });

  it("does not render legacy Focus metadata before the SDK projection loads", () => {
    const markup = renderToStaticMarkup(
      <ModuleEditor
        browser={focusBrowser}
        familyId="focuses"
        locale="en"
        onPinTab={() => undefined}
        onProjectRefresh={async () => undefined}
        openTarget="cursor"
        surface="diagram"
        templates={null}
        t={createTranslator("en")}
        theme="light"
      />
    );

    expect(markup).toContain("No diagram nodes");
    expect(markup).not.toContain(
      'data-node-id="FOCUS_C08_CANTERLOT_MIND"'
    );
    expect(markup).not.toContain(
      'data-node-id="FOCUS_C08_SECOND_SUMMIT"'
    );
    expect(markup).not.toContain('class="module-editor-grid"');
  });

  it("keeps Focus scope selection without falling back to either module's metadata", () => {
    const secondTreeBrowser: ProjectBrowserPayload = {
      ...focusBrowser,
      families: [{ ...focusBrowser.families[0], item_count: 2, source_count: 2 }],
      items: [
        focusBrowser.items[0],
        {
          ...focusBrowser.items[0],
          id: "focus_tree:C09_MAIN",
          object_id: "C09_MAIN",
          module_id: "C09_MAIN",
          title: "C09 Main",
          root: "/workspace/projects/PIHC3/src/modules/focus_tree/C09_MAIN",
          relative_root: "src/modules/focus_tree/C09_MAIN",
          metadata: {
            settings: {
              focuses: [{ id: "FOCUS_C09_OTHER_TREE", x: "0", y: "0" }],
              source_focuses: [{ id: "FOCUS_C09_OTHER_TREE", source_path: "C09_OTHER_TREE" }]
            }
          }
        }
      ]
    };

    const markup = renderToStaticMarkup(
      <ModuleEditor
        browser={secondTreeBrowser}
        familyId="focuses"
        locale="en"
        onPinTab={() => undefined}
        onProjectRefresh={async () => undefined}
        openTarget="cursor"
        surface="diagram"
        templates={null}
        t={createTranslator("en")}
        theme="light"
      />
    );

    expect(markup).toContain("No diagram nodes");
    expect(markup).toContain("2 focus trees");
    expect(markup).not.toContain(
      'data-node-id="FOCUS_C08_CANTERLOT_MIND"'
    );
    expect(markup).not.toContain('data-node-id="FOCUS_C09_OTHER_TREE"');
  });

  it("shows a focus tree scope selector in the dedicated diagram tab", () => {
    const secondTreeBrowser: ProjectBrowserPayload = {
      ...focusBrowser,
      families: [{ ...focusBrowser.families[0], item_count: 2, source_count: 2 }],
      items: [
        focusBrowser.items[0],
        {
          ...focusBrowser.items[0],
          id: "focus_tree:C09_MAIN",
          object_id: "C09_MAIN",
          module_id: "C09_MAIN",
          title: "C09 Main",
          root: "/workspace/projects/PIHC3/src/modules/focus_tree/C09_MAIN",
          relative_root: "src/modules/focus_tree/C09_MAIN",
          metadata: {
            settings: {
              focuses: [{ id: "FOCUS_C09_OTHER_TREE", x: "0", y: "0" }],
              source_focuses: [{ id: "FOCUS_C09_OTHER_TREE", source_path: "C09_OTHER_TREE" }]
            }
          }
        }
      ]
    };

    const markup = renderToStaticMarkup(
      <ModuleEditor
        browser={secondTreeBrowser}
        familyId="focuses"
        locale="en"
        onPinTab={() => undefined}
        onProjectRefresh={async () => undefined}
        openTarget="cursor"
        surface="diagram"
        templates={null}
        t={createTranslator("en")}
        theme="light"
      />
    );

    expect(markup).toContain('class="diagram-scope-select"');
    expect(markup).toContain('aria-label="Focus tree diagram scope"');
    expect(markup).toContain('value="focus_tree:C08_PARTIV"');
    expect(markup).toContain("C08 Part IV");
    expect(markup).toContain('value="focus_tree:C09_MAIN"');
    expect(markup).toContain("C09 Main");
    expect(markup).toContain("2 focus trees");
  });

  it("uses focus collections, not child focus modules, as diagram scopes", () => {
    const modularBrowser: ProjectBrowserPayload = {
      ...focusBrowser,
      families: [{ ...focusBrowser.families[0], item_count: 4, source_count: 4 }],
      items: [
        ...["C01_MAIN", "C02_MAIN"].map((id) => ({
          ...focusBrowser.items[0],
          id: `collection:focus/${id}`,
          kind: "collection" as const,
          family: "focus",
          object_id: id,
          module_id: undefined,
          collection_id: id,
          title: id,
          root: `/workspace/projects/PIHC3/src/collections/focus/${id}`,
          relative_root: `src/collections/focus/${id}`
        })),
        ...["FOCUS_C01_FIRST", "FOCUS_C02_FIRST"].map((id, index) => ({
          ...focusBrowser.items[0],
          id: `module:focus/${id}`,
          kind: "module" as const,
          family: "focus",
          object_id: id,
          module_id: `focus/${id}`,
          collection_id: index === 0 ? "C01_MAIN" : "C02_MAIN",
          title: id,
          root: `/workspace/projects/PIHC3/src/modules/focus/${id}`,
          relative_root: `src/modules/focus/${id}`
        }))
      ]
    };

    const markup = renderToStaticMarkup(
      <ModuleEditor
        browser={modularBrowser}
        familyId="focuses"
        locale="en"
        onPinTab={() => undefined}
        onProjectRefresh={async () => undefined}
        openTarget="cursor"
        surface="diagram"
        templates={null}
        t={createTranslator("en")}
        theme="light"
      />
    );

    expect(markup).toContain("2 focus trees");
    expect(markup).toContain('value="collection:focus/C01_MAIN"');
    expect(markup).toContain('value="collection:focus/C02_MAIN"');
    expect(markup).not.toContain('value="module:focus/FOCUS_C01_FIRST"');
  });

  it("honors an external entity selection when opening a normal module tab from a diagram node", () => {
    const secondTreeBrowser: ProjectBrowserPayload = {
      ...focusBrowser,
      families: [{ ...focusBrowser.families[0], item_count: 2, source_count: 2 }],
      items: [
        focusBrowser.items[0],
        {
          ...focusBrowser.items[0],
          id: "focus_tree:C09_MAIN",
          object_id: "C09_MAIN",
          module_id: "C09_MAIN",
          title: "C09 Main",
          root: "/workspace/projects/PIHC3/src/modules/focus_tree/C09_MAIN",
          relative_root: "src/modules/focus_tree/C09_MAIN",
          metadata: {
            settings: {
              focuses: [{ id: "FOCUS_C09_OTHER_TREE", x: "0", y: "0" }],
              source_focuses: [{ id: "FOCUS_C09_OTHER_TREE", source_path: "C09_OTHER_TREE" }]
            }
          }
        }
      ]
    };

    const markup = renderToStaticMarkup(
      <ModuleEditor
        browser={secondTreeBrowser}
        familyId="focuses"
        locale="en"
        onPinTab={() => undefined}
        onProjectRefresh={async () => undefined}
        openTarget="cursor"
        selectedEntityId="focus_tree:C09_MAIN"
        selectedSourcePath="src/modules/focus_tree/C09_MAIN/legacy/C09_OTHER_TREE/info.json"
        templates={null}
        t={createTranslator("en")}
        theme="light"
      />
    );

    const selectedRow = markup.match(/<button aria-current="true" class="module-entity-activate"[\s\S]*?<\/button>/)?.[0] ?? "";
    expect(selectedRow).toContain("<strong>C09 Main</strong>");
    expect(selectedRow).not.toContain("<strong>C08 Part IV</strong>");
    expect(markup).toContain('class="source-tab selected" type="button">FOCUS_C09_OTHER_TREE info</button>');
  });

  it("honors a technology metadata source path when opening a normal module tab from a diagram node", () => {
    const sourceBackedTechnologyBrowser: ProjectBrowserPayload = {
      ...technologyBrowser,
      items: technologyBrowser.items.map((item) => ({
        ...item,
        sources: [
          {
            slot: "meta",
            name: "meta.yaml",
            path: `${item.root}/meta.yaml`,
            relative_path: `${item.relative_root}/meta.yaml`,
            extension: "yaml"
          }
        ]
      }))
    };

    const markup = renderToStaticMarkup(
      <ModuleEditor
        browser={sourceBackedTechnologyBrowser}
        familyId="technologies"
        locale="en"
        onPinTab={() => undefined}
        onProjectRefresh={async () => undefined}
        openTarget="cursor"
        selectedEntityId="technology:TECH_CHILD"
        selectedSourcePath="src/modules/technology/TECH_CHILD/meta.yaml"
        templates={null}
        t={createTranslator("en")}
        theme="light"
      />
    );

    const selectedRow = markup.match(/<button aria-current="true" class="module-entity-activate"[\s\S]*?<\/button>/)?.[0] ?? "";
    expect(selectedRow).toContain("<strong>Child Technology</strong>");
    expect(selectedRow).not.toContain("<strong>Root Technology</strong>");
    expect(markup).toContain(
      'class="source-tab source-tab-advanced selected" title="Open meta.yaml. ParaDev already infers the module family and ID from its folder; edit this file only for explicit overrides." type="button">Advanced metadata</button>'
    );
  });

  it("builds chat selection context from a normal selected module source", () => {
    const sourceBackedTechnologyBrowser: ProjectBrowserPayload = {
      ...technologyBrowser,
      items: technologyBrowser.items.map((item) => ({
        ...item,
        sources: [
          {
            slot: "meta",
            name: "meta.yaml",
            path: `${item.root}/meta.yaml`,
            relative_path: `${item.relative_root}/meta.yaml`,
            extension: "yaml"
          }
        ]
      }))
    };
    const entities = buildModuleEntities(sourceBackedTechnologyBrowser, "technologies", "en");
    const child = entities.find((entity) => entity.id === "technology:TECH_CHILD") ?? null;

    expect(moduleSelectionTargetForEntity(child, "technologies")).toEqual({
      entityId: "technology:TECH_CHILD",
      familyId: "technologies",
      sourcePath: "src/modules/technology/TECH_CHILD/meta.yaml"
    });
    expect(moduleSelectionTargetForEntity(child, "technologies", "/tmp/custom/def.txt")).toEqual({
      entityId: "technology:TECH_CHILD",
      familyId: "technologies",
      sourcePath: "/tmp/custom/def.txt"
    });
    expect(moduleSelectionTargetForEntity(null, "technologies")).toBeNull();
  });

  it("includes selected dirty source text in chat selection context", () => {
    const sourceBackedTechnologyBrowser: ProjectBrowserPayload = {
      ...technologyBrowser,
      items: technologyBrowser.items.map((item) => ({
        ...item,
        sources: [
          {
            slot: "meta",
            name: "meta.yaml",
            path: `${item.root}/meta.yaml`,
            relative_path: `${item.relative_root}/meta.yaml`,
            extension: "yaml"
          }
        ]
      }))
    };
    const entities = buildModuleEntities(sourceBackedTechnologyBrowser, "technologies", "en");
    const child = entities.find((entity) => entity.id === "technology:TECH_CHILD");
    const dirtyChild = child ? { ...child, drafts: { ...child.drafts, text: { ...child.drafts.text, meta: "id: TECH_CHILD\nname: Edited\n" } } } : null;

    expect(moduleSelectionTargetForEntity(dirtyChild, "technologies")).toEqual({
      entityId: "technology:TECH_CHILD",
      familyId: "technologies",
      sourcePath: "src/modules/technology/TECH_CHILD/meta.yaml",
      sourceContent: "id: TECH_CHILD\nname: Edited\n"
    });
  });

  it("keeps an intentionally emptied selected source as chat selection content", () => {
    const sourceBackedTechnologyBrowser: ProjectBrowserPayload = {
      ...technologyBrowser,
      items: technologyBrowser.items.map((item) => ({
        ...item,
        sources: [
          {
            slot: "meta",
            name: "meta.yaml",
            path: `${item.root}/meta.yaml`,
            relative_path: `${item.relative_root}/meta.yaml`,
            extension: "yaml"
          }
        ]
      }))
    };
    const entities = buildModuleEntities(sourceBackedTechnologyBrowser, "technologies", "en");
    const child = entities.find((entity) => entity.id === "technology:TECH_CHILD");
    const dirtyChild = child ? { ...child, drafts: { ...child.drafts, text: { ...child.drafts.text, meta: "" } } } : null;

    expect(moduleSelectionTargetForEntity(dirtyChild, "technologies")).toEqual({
      entityId: "technology:TECH_CHILD",
      familyId: "technologies",
      sourcePath: "src/modules/technology/TECH_CHILD/meta.yaml",
      sourceContent: ""
    });
  });

  it("reads chat selection content from the requested duplicate source slot", () => {
    const englishPath = "src/modules/technology/TECH_CHILD/english.loc";
    const chinesePath = "src/modules/technology/TECH_CHILD/chinese.loc";
    const sourceBackedTechnologyBrowser: ProjectBrowserPayload = {
      ...technologyBrowser,
      items: technologyBrowser.items.map((item) => ({
        ...item,
        sources: item.id === "technology:TECH_CHILD"
          ? [
              {
                slot: "loc",
                name: "english.loc",
                path: `/workspace/projects/PIHC3/${englishPath}`,
                relative_path: englishPath,
                extension: "loc"
              },
              {
                slot: "loc",
                name: "chinese.loc",
                path: `/workspace/projects/PIHC3/${chinesePath}`,
                relative_path: chinesePath,
                extension: "loc"
              }
            ]
          : item.sources
      }))
    };
    const child = buildModuleEntities(sourceBackedTechnologyBrowser, "technologies", "en")
      .find((entity) => entity.id === "technology:TECH_CHILD");
    const chineseKey = `loc::${chinesePath}`;
    const dirtyChild = child
      ? {
          ...child,
          drafts: {
            ...child.drafts,
            text: { [chineseKey]: 'l_simp_chinese:\n TECH_CHILD:0 "子科技"\n' }
          }
        }
      : null;

    expect(moduleSelectionTargetForEntity(dirtyChild, "technologies", chinesePath)).toEqual({
      entityId: "technology:TECH_CHILD",
      familyId: "technologies",
      sourcePath: chinesePath,
      sourceContent: 'l_simp_chinese:\n TECH_CHILD:0 "子科技"\n'
    });
  });

  it("builds a root focus draft from an empty focus tree context node", () => {
    const input = rootDiagramFocusNodeInput(focusTreeContextDocument);

    expect(input).toMatchObject({
      height: 2,
      id: "FOCUS_NEW_ROOT",
      mode: "auto",
      title: "FOCUS NEW ROOT",
      width: 6,
      payload: {
        embeddedId: "FOCUS_NEW_ROOT",
        embeddedKind: "focus",
        itemId: "focus_tree:C08_PARTIV",
        objectId: "C08_PARTIV"
      }
    });
  });

  it("keeps focus and technology diagram panels visible for empty draft diagrams", () => {
    expect(shouldShowProjectDiagram(focusBrowser, "focuses", emptyDiagramDocument)).toBe(true);
    expect(shouldShowProjectDiagram(technologyBrowser, "technologies", emptyDiagramDocument)).toBe(true);
    expect(shouldShowProjectDiagram(technologyBrowser, "ideas", emptyDiagramDocument)).toBe(false);
  });

  it("includes moved PIHC3 technology metadata files in diagram changed rows", () => {
    const sourceBackedBrowser: ProjectBrowserPayload = {
      ...technologyBrowser,
      items: technologyBrowser.items.map((item) => ({
        ...item,
        sources: [
          {
            slot: "meta",
            name: "meta.yaml",
            path: `${item.root}/meta.yaml`,
            relative_path: `${item.relative_root}/meta.yaml`,
            extension: "yaml"
          }
        ]
      }))
    };
    const baseDocument = buildProjectDiagramDocument(sourceBackedBrowser, "technologies");
    const draftDocument = moveDiagramNode(baseDocument, "TECH_CHILD", { dx: 1, dy: -1 });

    expect(buildDiagramChangedEntities(baseDocument, draftDocument, buildModuleEntities(sourceBackedBrowser, "technologies", "en"))).toEqual([
      {
        id: "technology:TECH_CHILD",
        path: "src/modules/technology/TECH_CHILD/meta.yaml",
        title: "Child Technology"
      }
    ]);
  });

  it("attaches generated PIHC3 metadata draft text to diagram changed rows", () => {
    const sourceBackedBrowser: ProjectBrowserPayload = {
      ...technologyBrowser,
      items: technologyBrowser.items.map((item) => ({
        ...item,
        sources: [
          {
            slot: "meta",
            name: "meta.yaml",
            path: `${item.root}/meta.yaml`,
            relative_path: `${item.relative_root}/meta.yaml`,
            extension: "yaml"
          }
        ]
      }))
    };
    const baseDocument = buildProjectDiagramDocument(sourceBackedBrowser, "technologies");
    const draftDocument = moveDiagramNode(baseDocument, "TECH_CHILD", { dx: 1, dy: -1 });
    const entities = buildModuleEntities(sourceBackedBrowser, "technologies", "en");
    const rows = buildDiagramChangedEntities(baseDocument, draftDocument, entities);
    const draftText = ["type: technology", "settings:", "    folder_position:", "        x: 5", "        y: 0", ""].join("\n");
    const attachDraftText = (
      ModuleEditorExports as typeof ModuleEditorExports & {
        buildDiagramChangedEntitiesWithDraftTexts?: (rows: ReturnType<typeof buildDiagramChangedEntities>, drafts: Array<{ entityId: string; slot: "meta" | "source"; text: string }>, entities: Parameters<typeof buildDiagramChangedEntities>[2]) => ReturnType<typeof buildDiagramChangedEntities>;
      }
    ).buildDiagramChangedEntitiesWithDraftTexts;

    expect(attachDraftText).toBeTypeOf("function");
    expect(attachDraftText?.(rows, [{ entityId: "technology:TECH_CHILD", slot: "meta", text: draftText }], entities)).toEqual([
      {
        draftText,
        id: "technology:TECH_CHILD",
        path: "src/modules/technology/TECH_CHILD/meta.yaml",
        title: "Child Technology"
      }
    ]);
  });

  it("marks changed PIHC3 rows without generated draft text as unavailable", () => {
    const rows = [
      {
        id: "focus_tree:C08_PARTIV",
        path: "src/modules/focus_tree/C08_PARTIV/meta.yaml",
        title: "C08 Part IV"
      },
      {
        id: "focus_tree:C08_PARTIV",
        path: "src/modules/focus_tree/C08_PARTIV/legacy/C08_CHILD/info.json",
        title: "C08 Part IV"
      }
    ];
    const draftText = ["type: focus_tree", "settings:", "    source_focuses: []", ""].join("\n");
    const entities = buildModuleEntities(
      {
        ...focusBrowser,
        items: [
          {
            ...focusBrowser.items[0],
            sources: [{ slot: "meta", name: "meta.yaml", path: "/workspace/projects/PIHC3/src/modules/focus_tree/C08_PARTIV/meta.yaml", relative_path: "src/modules/focus_tree/C08_PARTIV/meta.yaml", extension: "yaml" }]
          }
        ]
      },
      "focuses",
      "en"
    );
    const attachDraftText = (
      ModuleEditorExports as typeof ModuleEditorExports & {
        buildDiagramChangedEntitiesWithDraftTexts?: (
          changedRows: typeof rows,
          drafts: Array<{ entityId: string; path?: string; slot: "meta" | "source"; text: string }>,
          entities: Parameters<typeof buildDiagramChangedEntities>[2]
        ) => Array<(typeof rows)[number] & { draftText?: string; draftUnavailable?: boolean }>;
      }
    ).buildDiagramChangedEntitiesWithDraftTexts;

    expect(attachDraftText?.(rows, [{ entityId: "focus_tree:C08_PARTIV", slot: "meta", text: draftText }], entities)).toEqual([
      {
        draftText,
        id: "focus_tree:C08_PARTIV",
        path: "src/modules/focus_tree/C08_PARTIV/meta.yaml",
        title: "C08 Part IV"
      },
      {
        draftUnavailable: true,
        id: "focus_tree:C08_PARTIV",
        path: "src/modules/focus_tree/C08_PARTIV/legacy/C08_CHILD/info.json",
        title: "C08 Part IV"
      }
    ]);
  });

  it("blocks diagram apply plans when any changed PIHC3 row lacks generated draft text", () => {
    const rows = [
      {
        id: "focus_tree:C08_PARTIV",
        path: "src/modules/focus_tree/C08_PARTIV/meta.yaml",
        title: "C08 Part IV"
      },
      {
        id: "focus_tree:C08_PARTIV",
        path: "src/modules/focus_tree/C08_PARTIV/legacy/C08_CHILD/info.json",
        title: "C08 Part IV"
      }
    ];
    const draftText = ["type: focus_tree", "settings:", "    source_focuses: []", ""].join("\n");
    const entities = buildModuleEntities(
      {
        ...focusBrowser,
        items: [
          {
            ...focusBrowser.items[0],
            sources: [{ slot: "meta", name: "meta.yaml", path: "/workspace/projects/PIHC3/src/modules/focus_tree/C08_PARTIV/meta.yaml", relative_path: "src/modules/focus_tree/C08_PARTIV/meta.yaml", extension: "yaml" }]
          }
        ]
      },
      "focuses",
      "en"
    );
    const buildApplyPlan = (
      ModuleEditorExports as typeof ModuleEditorExports & {
        buildDiagramApplyDraftPlan?: (
          changedRows: typeof rows,
          drafts: Array<{ entityId: string; path?: string; slot: "meta" | "source"; text: string }>,
          entities: Parameters<typeof buildDiagramChangedEntities>[2]
        ) => unknown;
      }
    ).buildDiagramApplyDraftPlan;

    expect(buildApplyPlan).toBeTypeOf("function");
    expect(buildApplyPlan?.(rows, [{ entityId: "focus_tree:C08_PARTIV", slot: "meta", text: draftText }], entities)).toEqual({
      ok: false,
      reason: "draft-unavailable",
      rows: [
        {
          draftText,
          id: "focus_tree:C08_PARTIV",
          path: "src/modules/focus_tree/C08_PARTIV/meta.yaml",
          title: "C08 Part IV"
        },
        {
          draftUnavailable: true,
          id: "focus_tree:C08_PARTIV",
          path: "src/modules/focus_tree/C08_PARTIV/legacy/C08_CHILD/info.json",
          title: "C08 Part IV"
        }
      ]
    });
  });

  it("marks path-backed diagram apply rows unavailable when draft generation returns no text", () => {
    const rows = [
      {
        id: "focus_tree:C08_PARTIV",
        path: "src/modules/focus_tree/C08_PARTIV/meta.yaml",
        title: "C08 Part IV"
      }
    ];
    const entities = buildModuleEntities(
      {
        ...focusBrowser,
        items: [
          {
            ...focusBrowser.items[0],
            sources: [{ slot: "meta", name: "meta.yaml", path: "/workspace/projects/PIHC3/src/modules/focus_tree/C08_PARTIV/meta.yaml", relative_path: "src/modules/focus_tree/C08_PARTIV/meta.yaml", extension: "yaml" }]
          }
        ]
      },
      "focuses",
      "en"
    );

    expect(buildDiagramApplyDraftPlan(rows, [], entities)).toEqual({
      ok: false,
      reason: "draft-unavailable",
      rows: [
        {
          draftUnavailable: true,
          id: "focus_tree:C08_PARTIV",
          path: "src/modules/focus_tree/C08_PARTIV/meta.yaml",
          title: "C08 Part IV"
        }
      ]
    });
  });

  it("drops unchanged PIHC3 meta rows when only a source info draft is generated", () => {
    const rows = [
      {
        id: "focus_tree:C08_PARTIV",
        path: "src/modules/focus_tree/C08_PARTIV/meta.yaml",
        title: "C08 Part IV"
      },
      {
        id: "focus_tree:C08_PARTIV",
        path: "src/modules/focus_tree/C08_PARTIV/legacy/C08_CHILD/info.json",
        title: "C08 Part IV"
      }
    ];
    const draftText = `${JSON.stringify({ dx: 3, dy: 0 }, null, 4)}\n`;
    const entities = buildModuleEntities(
      {
        ...focusBrowser,
        items: [
          {
            ...focusBrowser.items[0],
            sources: [{ slot: "meta", name: "meta.yaml", path: "/workspace/projects/PIHC3/src/modules/focus_tree/C08_PARTIV/meta.yaml", relative_path: "src/modules/focus_tree/C08_PARTIV/meta.yaml", extension: "yaml" }]
          }
        ]
      },
      "focuses",
      "en"
    );
    const attachDraftText = (
      ModuleEditorExports as typeof ModuleEditorExports & {
        buildDiagramChangedEntitiesWithDraftTexts?: (
          changedRows: typeof rows,
          drafts: Array<{ entityId: string; path?: string; slot: "meta" | "source"; text: string }>,
          entities: Parameters<typeof buildDiagramChangedEntities>[2]
        ) => Array<(typeof rows)[number] & { draftText?: string; draftUnavailable?: boolean }>;
      }
    ).buildDiagramChangedEntitiesWithDraftTexts;

    expect(
      attachDraftText?.(
        rows,
        [
          {
            entityId: "focus_tree:C08_PARTIV",
            path: "/workspace/projects/PIHC3/src/modules/focus_tree/C08_PARTIV/legacy/C08_CHILD/info.json",
            slot: "source",
            text: draftText
          }
        ],
        entities
      )
    ).toEqual([
      {
        draftText,
        id: "focus_tree:C08_PARTIV",
        path: "src/modules/focus_tree/C08_PARTIV/legacy/C08_CHILD/info.json",
        title: "C08 Part IV"
      }
    ]);
  });

  it("includes migrated focus source info files in diagram changed rows", () => {
    const sourceBackedBrowser: ProjectBrowserPayload = {
      ...focusBrowser,
      items: [
        {
          id: "focus_tree:C08_PARTIV",
          kind: "module",
          layout: "canonical",
          family_id: "focuses",
          family: "focus_tree",
          object_id: "C08_PARTIV",
          module_id: "C08_PARTIV",
          title: "C08 Part IV",
          root: "/workspace/projects/PIHC3/src/modules/focus_tree/C08_PARTIV",
          relative_root: "src/modules/focus_tree/C08_PARTIV",
          source_root: "/workspace/projects/PIHC3/src",
          source_root_relative_path: "src",
          source_count: 1,
          sources: [{ slot: "meta", name: "meta.yaml", path: "/workspace/projects/PIHC3/src/modules/focus_tree/C08_PARTIV/meta.yaml", relative_path: "src/modules/focus_tree/C08_PARTIV/meta.yaml", extension: "yaml" }],
          metadata: {
            settings: {
              source_focuses: [
                { folder: "C08_ROOT", focus_id: "FOCUS_ROOT", source_path: "C08_ROOT", x: "10", y: "0" },
                { folder: "C08_CHILD", focus_id: "FOCUS_CHILD", source_path: "C08_CHILD", parent: "FOCUS_ROOT", dx: "2", dy: "1" }
              ],
              focuses: [
                { id: "FOCUS_ROOT", x: "10", y: "0" },
                { id: "FOCUS_CHILD", x: "12", y: "1", prerequisites: ["FOCUS_ROOT"] }
              ]
            }
          }
        }
      ]
    };
    const baseDocument = buildProjectDiagramDocument(sourceBackedBrowser, "focuses");
    const draftDocument = moveDiagramNode(baseDocument, "FOCUS_CHILD", { dx: 1, dy: -1 });

    expect(buildDiagramChangedEntities(baseDocument, draftDocument, buildModuleEntities(sourceBackedBrowser, "focuses", "en"))).toEqual([
      {
        id: "focus_tree:C08_PARTIV",
        path: "src/modules/focus_tree/C08_PARTIV/meta.yaml",
        title: "C08 Part IV"
      },
      {
        id: "focus_tree:C08_PARTIV",
        path: "src/modules/focus_tree/C08_PARTIV/legacy/C08_CHILD/info.json",
        title: "C08 Part IV"
      }
    ]);
  });
});
