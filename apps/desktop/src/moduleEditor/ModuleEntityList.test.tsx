/** @vitest-environment jsdom */

import { renderToStaticMarkup } from "react-dom/server";
import { act, type ComponentProps } from "react";
import { createRoot } from "react-dom/client";
import { describe, expect, it, vi } from "vitest";
import { createTranslator } from "../i18n";
import type { ModuleEntity, TemplateCreateField } from "./model";
import { ModuleEntityList, validateTemplateCreateForm } from "./ModuleEntityList";

const entities: ModuleEntity[] = [
  {
    id: "ideas:IDEA_ALPHA",
    familyId: "ideas",
    family: "idea",
    objectId: "IDEA_ALPHA",
    title: "Alpha Idea",
    subtitle: "IDEA_ALPHA",
    root: "/workspace/projects/PIHC3/src/modules/idea/IDEA_ALPHA",
    relativeRoot: "src/modules/idea/IDEA_ALPHA",
    layout: "canonical",
    sourceCount: 2,
    sourceSlots: [
      {
        slot: "icon",
        name: "alpha.png",
        path: "/workspace/projects/PIHC3/src/modules/idea/IDEA_ALPHA/icon.png",
        relative_path: "src/modules/idea/IDEA_ALPHA/icon.png",
        extension: "png",
        draftKey: "icon",
        editorKind: "image",
      },
    ],
    tags: [],
    draftState: "clean",
    drafts: { text: {} },
  },
  {
    id: "ideas:IDEA_BETA",
    familyId: "ideas",
    family: "idea",
    objectId: "IDEA_BETA",
    title: "Beta Law",
    subtitle: "IDEA_BETA",
    root: "/workspace/projects/PIHC3/src/modules/idea/IDEA_BETA",
    relativeRoot: "src/modules/idea/IDEA_BETA",
    layout: "canonical",
    sourceCount: 2,
    sourceSlots: [],
    tags: [],
    draftState: "clean",
    drafts: { text: {} },
  },
];

const templateFields: TemplateCreateField[] = [
  {
    name: "title",
    label: "Display title",
    description: "Shown to players.",
    required: true,
    defaultValue: "",
    advanced: false,
    type: "string",
    choices: [],
  },
  {
    name: "notes",
    label: "Notes",
    description: "Describe the idea in plain language.",
    required: false,
    defaultValue: "",
    advanced: false,
    type: "text",
    choices: [],
  },
  {
    name: "scope",
    label: "Scope",
    description: "Where this idea applies.",
    required: true,
    defaultValue: "country",
    advanced: false,
    type: "choice",
    choices: ["country", "state"],
  },
  {
    name: "enabled",
    label: "Enabled",
    description: "Create the idea enabled by default.",
    required: false,
    defaultValue: "true",
    advanced: false,
    type: "boolean",
    choices: [],
  },
  {
    name: "weight",
    label: "Weight",
    description: "Relative selection weight.",
    required: false,
    defaultValue: "1.5",
    advanced: false,
    type: "number",
    choices: [],
  },
  {
    name: "icon",
    label: "Icon asset",
    description: "Project asset path or sprite identifier.",
    required: false,
    defaultValue: "",
    advanced: false,
    type: "asset",
    choices: [],
  },
];

function renderList(locale: "en" | "zh" = "en") {
  const t = createTranslator(locale);
  return renderToStaticMarkup(<ModuleEntityList allEntities={entities} createAdvancedFields={[]} createBusy={false} createError="" createObjectId="" createObjectIdPreview="IDEA_DRAFT_003" createPreviewValues={{}} createPrimaryFields={[]} createTemplateId="" createTemplateOptions={[]} createTemplateTitle="Idea" createValues={{}} entities={[entities[0]]} locale={locale} onCreate={() => false} onCreateObjectIdChange={() => undefined} onCreateTemplateChange={() => undefined} onCreateValueChange={() => undefined} onQueryChange={() => undefined} onRemoveSelected={() => undefined} onSelect={() => undefined} onSelectionChange={() => undefined} onShowAdvancedCreateChange={() => undefined} projectRoot="/workspace/projects/PIHC3" query="alpha" selectedId={entities[0].id} selectedIds={new Set([entities[1].id])} showAdvancedCreate={false} t={t} />);
}

function renderListWithoutSelection(overrides: Partial<ComponentProps<typeof ModuleEntityList>> = {}) {
  return renderToStaticMarkup(<ModuleEntityList {...listWithoutSelectionProps(overrides)} />);
}

function listWithoutSelectionProps(overrides: Partial<ComponentProps<typeof ModuleEntityList>> = {}): ComponentProps<typeof ModuleEntityList> {
  const locale = overrides.locale ?? "en";
  return {
    allEntities: entities,
    createAdvancedFields: [],
    createBusy: false,
    createError: "",
    createObjectId: "",
    createObjectIdPreview: "IDEA_DRAFT_003",
    createPreviewValues: {},
    createPrimaryFields: [],
    createTemplateId: "",
    createTemplateOptions: [],
    createTemplateTitle: "Idea",
    createValues: {},
    entities,
    locale,
    onCreate: () => false,
    onCreateObjectIdChange: () => undefined,
    onCreateTemplateChange: () => undefined,
    onCreateValueChange: () => undefined,
    onQueryChange: () => undefined,
    onRemoveSelected: () => undefined,
    onSelect: () => undefined,
    onSelectionChange: () => undefined,
    onShowAdvancedCreateChange: () => undefined,
    projectRoot: "/workspace/projects/PIHC3",
    query: "",
    selectedId: entities[0].id,
    selectedIds: new Set(),
    showAdvancedCreate: false,
    t: createTranslator(locale),
    ...overrides,
  };
}

function largeEntitySet(count: number): ModuleEntity[] {
  return Array.from({ length: count }, (_, index) => {
    const objectId = `IDEA_${String(index + 1).padStart(4, "0")}`;
    return {
      ...entities[0],
      id: `ideas:${objectId}`,
      objectId,
      relativeRoot: `src/modules/idea/${objectId}`,
      root: `/workspace/projects/PIHC3/src/modules/idea/${objectId}`,
      subtitle: objectId,
      title: `Idea ${index + 1}`,
    };
  });
}

function renderListWithCreateIntent(overrides: Partial<ComponentProps<typeof ModuleEntityList>> = {}) {
  const t = createTranslator("en");
  return renderToStaticMarkup(
    <ModuleEntityList
      allEntities={entities}
      createAdvancedFields={[]}
      createBusy={false}
      createError=""
      createIntent={{
        ai: {
          nonce: 10,
          operationId: "module.draft",
          role: "create-module",
          sources: [{ familyId: "idea", kind: "templates", label: "Idea templates" }],
        },
        familyId: "ideas",
        nonce: 1,
      }}
      createObjectId=""
      createObjectIdPreview="IDEA_DRAFT_003"
      createPreviewValues={{}}
      createPrimaryFields={[]}
      createTemplateId=""
      createTemplateOptions={[]}
      createTemplateTitle="Idea"
      createValues={{}}
      entities={entities}
      locale="en"
      onCreate={() => {
        throw new Error("create should not run while rendering a navigation intent");
      }}
      onCreateObjectIdChange={() => undefined}
      onCreateTemplateChange={() => undefined}
      onCreateValueChange={() => undefined}
      onQueryChange={() => undefined}
      onRemoveSelected={() => undefined}
      onSelect={() => undefined}
      onSelectionChange={() => undefined}
      onShowAdvancedCreateChange={() => undefined}
      projectRoot="/workspace/projects/PIHC3"
      query=""
      selectedId={entities[0].id}
      selectedIds={new Set()}
      showAdvancedCreate={false}
      t={t}
      {...overrides}
    />,
  );
}

function renderRemovalDialog(): string {
  const t = createTranslator("en");
  const container = document.createElement("div");
  document.body.append(container);
  const root = createRoot(container);
  act(() => {
    root.render(<ModuleEntityList allEntities={entities} createAdvancedFields={[]} createBusy={false} createError="" createObjectId="" createObjectIdPreview="IDEA_DRAFT_003" createPreviewValues={{}} createPrimaryFields={[]} createTemplateId="" createTemplateOptions={[]} createTemplateTitle="Idea" createValues={{}} entities={entities} locale="en" onCreate={() => false} onCreateObjectIdChange={() => undefined} onCreateTemplateChange={() => undefined} onCreateValueChange={() => undefined} onQueryChange={() => undefined} onRemoveSelected={() => undefined} onSelect={() => undefined} onSelectionChange={() => undefined} onShowAdvancedCreateChange={() => undefined} projectRoot="/workspace/projects/PIHC3" query="" selectedId={entities[0].id} selectedIds={new Set()} showAdvancedCreate={false} t={t} />);
  });
  const removeButton = [...container.querySelectorAll("button")].find((button) => button.getAttribute("aria-label") === "Remove current object");
  act(() => removeButton?.click());
  const markup = container.innerHTML;
  act(() => root.unmount());
  container.remove();
  return markup;
}

describe("ModuleEntityList", () => {
  it("renders industrial bulk-selection controls for filtered instance results", () => {
    const markup = renderList();

    expect(markup).toContain("1 selected");
    expect(markup).toContain("1 of 2 results");
    expect(markup).toContain("Select visible results");
    expect(markup).toContain("Select loaded filtered results");
    expect(markup).toContain("Select all loaded objects");
    expect(markup).toContain("Clear selection");
  });

  it("hides bulk-selection controls until at least one row is checked", () => {
    const markup = renderListWithoutSelection();

    expect(markup).not.toContain("Selection tools");
    expect(markup).not.toContain("Select all loaded objects");
    expect(markup).toContain("Remove current object");
  });

  it("exposes batch creation as a secondary module-list command with a visible unavailable reason", () => {
    const enabled = renderListWithoutSelection({
      onOpenBatch: () => undefined,
    });
    const reason = "Batch creation requires the desktop bridge.";
    const disabled = renderListWithoutSelection({
      batchUnavailableReason: reason,
      onOpenBatch: () => undefined,
    });
    const container = document.createElement("div");
    container.innerHTML = disabled;
    const button = container.querySelector<HTMLButtonElement>('button[aria-label="Batch create"]');

    expect(enabled).toContain('aria-label="Batch create"');
    expect(button?.disabled).toBe(true);
    expect(button?.title).toBe(reason);
  });

  it("renders optional thumbnail slots before titles and moves row selection to the right edge", () => {
    const markup = renderListWithoutSelection();

    expect(markup).toContain('class="module-entity-thumb placeholder"');
    expect(markup.indexOf("module-entity-thumb")).toBeLessThan(markup.indexOf("Alpha Idea"));
    expect(markup).toContain('class="module-entity-check"');
    expect(markup.indexOf("module-entity-check")).toBeGreaterThan(markup.indexOf("IDEA_ALPHA"));
  });

  it("renders list and row-selection aria labels in Chinese", () => {
    const markup = renderList("zh");

    expect(markup).toContain('aria-label="模块条目"');
    expect(markup).toContain('lang="zh-CN"');
    expect(markup).toContain('aria-label="搜索模块条目"');
    expect(markup).toContain('aria-label="选择 Alpha Idea"');
    expect(markup).not.toContain("Module entities");
    expect(markup).not.toContain("Search module entities");
    expect(markup).not.toContain("Select Alpha Idea");
  });

  it("opens the create dialog from a chat navigation intent without submitting", () => {
    const markup = renderListWithCreateIntent();

    expect(markup).toContain('role="dialog"');
    expect(markup).toContain('id="module-create-title"');
    expect(markup).toContain("Object ID");
    expect(markup).toContain("IDEA_DRAFT_003");
    expect(markup).toContain('data-paradev-ai-operation-id="module.draft"');
    expect(markup).toContain('data-paradev-ai-operation-passive="true"');
    expect(markup).toContain("Opened from AI: module.draft");
    expect(markup).toContain("No files are written until you apply the draft through the SDK bridge.");
    expect(markup).toContain("Task: create-module");
    expect(markup).toContain("Context: Idea templates");
  });

  it("renders SDK template field types with labels, descriptions, and resolved defaults", () => {
    const markup = renderListWithCreateIntent({
      createPreviewValues: {
        enabled: "true",
        scope: "country",
        weight: "1.5",
      },
      createPrimaryFields: templateFields,
    });
    const container = document.createElement("div");
    container.innerHTML = markup;

    expect(container.querySelector('input[aria-label="Display title"][type="text"]')).not.toBeNull();
    expect(container.querySelector('textarea[aria-label="Notes"][rows="3"]')).not.toBeNull();
    expect(container.querySelector('select[aria-label="Scope"]')?.getAttribute("value")).toBeNull();
    expect(container.querySelector('select[aria-label="Scope"] option[value="country"]')?.hasAttribute("selected")).toBe(true);
    expect(container.querySelector('input[aria-label="Enabled"][type="checkbox"]')?.hasAttribute("checked")).toBe(true);
    expect(container.querySelector('input[aria-label="Weight"][type="number"]')?.getAttribute("step")).toBe("any");
    expect(container.querySelector('input[aria-label="Icon asset"][data-template-field-type="asset"]')?.getAttribute("placeholder")).toBe("Asset path or identifier");
    expect(container.textContent).toContain("Display title *");
    expect(container.textContent).toContain("Describe the idea in plain language.");
    expect(container.textContent).toContain("Project asset path or sprite identifier.");
  });

  it("suggests extension-declared object references without restricting custom IDs", () => {
    const treeField: TemplateCreateField = {
      name: "tree",
      label: "Focus tree",
      description: "Existing tree ID, or a new ID to create later.",
      required: true,
      defaultValue: "",
      advanced: false,
      type: "string",
      choices: [],
      reference: { kind: "collection", family: "focus" },
    };
    const markup = renderListWithCreateIntent({
      createPrimaryFields: [treeField],
      createValues: { tree: "CUSTOM_TREE" },
      referenceItems: [
        {
          id: "focus:collection:GER_focus",
          kind: "collection",
          layout: "canonical",
          family_id: "focuses",
          family: "focus",
          object_id: "GER_focus",
          collection_id: "GER_focus",
          title: "German Focus Tree",
          root: "/workspace/projects/PIHC3/src/modules/focus/GER_focus",
          relative_root: "src/modules/focus/GER_focus",
          source_count: 1,
          sources: [],
        },
      ],
    });
    const container = document.createElement("div");
    container.innerHTML = markup;
    const input = container.querySelector<HTMLInputElement>('input[aria-label="Focus tree"]');
    const listId = input?.getAttribute("list");

    expect(listId).toBeTruthy();
    expect(container.querySelector("datalist")?.id).toBe(listId);
    expect(container.querySelector("datalist")?.innerHTML).toContain("GER_focus");
    expect(container.querySelector(`option[value="GER_focus"]`)?.getAttribute("label")).toBe("German Focus Tree — GER_focus");
    expect(input?.value).toBe("CUSTOM_TREE");
  });

  it("validates effective required, number, choice, and boolean values before creation", () => {
    const invalid = validateTemplateCreateForm(
      "",
      "",
      templateFields,
      {
        enabled: "sometimes",
        scope: "planet",
        weight: "heavy",
      },
      {},
    );
    const validDefaults = validateTemplateCreateForm(
      "",
      "IDEA_DRAFT_003",
      templateFields,
      {},
      {
        enabled: "true",
        scope: "country",
        title: "Draft title",
        weight: "1.5",
      },
    );

    expect(invalid).toEqual({
      objectId: true,
      fields: {
        title: "required",
        scope: "choice",
        enabled: "boolean",
        weight: "number",
      },
    });
    expect(validDefaults).toEqual({ objectId: false, fields: {} });
  });

  it("blocks invalid submit locally and exposes accessible field errors", () => {
    const onCreate = vi.fn(() => true);
    const container = document.createElement("div");
    document.body.append(container);
    const root = createRoot(container);
    act(() => {
      root.render(<ModuleEntityList allEntities={entities} createAdvancedFields={[]} createBusy={false} createError="" createIntent={{ familyId: "ideas", nonce: 20 }} createObjectId="" createObjectIdPreview="" createPreviewValues={{}} createPrimaryFields={templateFields.filter((field) => field.name === "title")} createTemplateId="idea/basic" createTemplateOptions={[{ label: "Idea", value: "idea/basic" }]} createTemplateTitle="Idea" createValues={{}} entities={entities} locale="en" onCreate={onCreate} onCreateObjectIdChange={() => undefined} onCreateTemplateChange={() => undefined} onCreateValueChange={() => undefined} onQueryChange={() => undefined} onRemoveSelected={() => undefined} onSelect={() => undefined} onSelectionChange={() => undefined} onShowAdvancedCreateChange={() => undefined} projectRoot="/workspace/projects/PIHC3" query="" selectedId={entities[0].id} selectedIds={new Set()} showAdvancedCreate={false} t={createTranslator("en")} />);
    });

    act(() => container.querySelector<HTMLButtonElement>('button[type="submit"]')?.click());

    expect(onCreate).not.toHaveBeenCalled();
    expect(container.querySelector('input[aria-label="Object ID"]')?.getAttribute("aria-invalid")).toBe("true");
    expect(container.querySelector('input[aria-label="Display title"]')?.getAttribute("aria-invalid")).toBe("true");
    expect(container.textContent).toContain("Object ID is required.");
    expect(container.textContent).toContain("Display title is required.");
    act(() => root.unmount());
    container.remove();
  });

  it("disables creation with an explicit reason when no authoring-ready template exists", () => {
    const reason = "Creation is unavailable for Ideas because this family has no authoring-ready template.";
    const markup = renderListWithCreateIntent({
      createUnavailableReason: reason,
    });
    const container = document.createElement("div");
    container.innerHTML = markup;
    const createButton = container.querySelector<HTMLButtonElement>('button[aria-label="New"]');

    expect(createButton?.disabled).toBe(true);
    expect(createButton?.getAttribute("title")).toBe(reason);
    expect(container.querySelector(".module-create-unavailable")?.textContent).toBe(reason);
    expect(markup).not.toContain('role="dialog"');
  });

  it("uses native list rows with separate activation buttons and selection checkboxes", () => {
    const markup = renderListWithoutSelection();

    expect(markup).toContain('<ul aria-label="Entity results" class="module-entity-options">');
    expect(markup).toMatch(/<li[^>]*class="module-entity-row selected"[^>]*>/);
    expect(markup).toContain('<button aria-current="true" class="module-entity-activate"');
    expect(markup).not.toContain('role="listbox"');
    expect(markup).not.toContain('role="option"');
    expect(markup).not.toContain("aria-setsize");
    expect(markup).not.toContain("aria-posinset");
    expect(markup).toMatch(/<button[^>]*class="module-entity-activate"[^>]*>.*<\/button><label class="module-entity-check"/);
  });

  it("reports truthful paging totals and keeps load-more outside the entity list", () => {
    const markup = renderListWithoutSelection({
      hasMore: true,
      loadedCount: 2,
      loading: false,
      onLoadMore: () => undefined,
      totalCount: 8_279,
    });

    expect(markup).toContain("2 of 8279 loaded");
    expect(markup).toContain("Load more");
    expect(markup.indexOf("module-catalog-footer")).toBeGreaterThan(markup.lastIndexOf("</ul>"));
    expect(markup).toMatch(/aria-controls="[^"]+"/);
  });

  it("progressively discloses large directly discovered families without hiding the active object", () => {
    const largeEntities = largeEntitySet(250);
    const initialMarkup = renderListWithoutSelection({
      allEntities: largeEntities,
      entities: largeEntities,
      selectedId: largeEntities[0].id,
    });
    const selectedOutsideMarkup = renderListWithoutSelection({
      allEntities: largeEntities,
      entities: largeEntities,
      selectedId: largeEntities[249].id,
    });
    const initialContainer = document.createElement("div");
    initialContainer.innerHTML = initialMarkup;
    const selectedOutsideContainer = document.createElement("div");
    selectedOutsideContainer.innerHTML = selectedOutsideMarkup;

    expect(initialContainer.querySelectorAll(".module-entity-row")).toHaveLength(100);
    expect(initialContainer.textContent).toContain("Showing 100 of 250 matching objects");
    expect(initialContainer.textContent).toContain("Show more");
    expect(selectedOutsideContainer.querySelectorAll(".module-entity-row")).toHaveLength(101);
    expect(selectedOutsideContainer.textContent).toContain("Idea 250");
    expect(selectedOutsideContainer.textContent).toContain("Showing 101 of 250 matching objects");
  });

  it("reveals direct-discovery results in bounded batches", () => {
    const largeEntities = largeEntitySet(250);
    const container = document.createElement("div");
    document.body.append(container);
    const root = createRoot(container);
    act(() => {
      root.render(
        <ModuleEntityList
          {...listWithoutSelectionProps({
            allEntities: largeEntities,
            entities: largeEntities,
            selectedId: largeEntities[0].id,
          })}
        />,
      );
    });

    expect(container.querySelectorAll(".module-entity-row")).toHaveLength(100);
    act(() => {
      [...container.querySelectorAll("button")].find((button) => button.textContent === "Show more")?.click();
    });
    expect(container.querySelectorAll(".module-entity-row")).toHaveLength(200);
    expect(container.textContent).toContain("Showing 200 of 250 matching objects");

    act(() => root.unmount());
    container.remove();
  });

  it("announces catalog loading and localized retry state", () => {
    const loadingMarkup = renderListWithoutSelection({
      loadedCount: 2,
      loading: true,
      totalCount: 8_279,
    });
    const retryMarkup = renderListWithoutSelection({
      loadError: "索引暂时不可用",
      loadedCount: 2,
      locale: "zh",
      onRetryLoad: () => undefined,
      t: createTranslator("zh"),
      totalCount: 8_279,
    });

    expect(loadingMarkup).toContain('aria-busy="true"');
    expect(loadingMarkup).toContain("Loading module rows…");
    expect(retryMarkup).toContain("已加载 2 / 8279");
    expect(retryMarkup).toContain("索引暂时不可用");
    expect(retryMarkup).toContain("重试");
  });

  it("distinguishes missing and changed source conflicts in both locales", () => {
    const conflictedEntities: ModuleEntity[] = [
      {
        ...entities[0],
        draftState: "modified",
        sourceConflict: "missing",
        drafts: { text: { def: "missing draft" } },
      },
      {
        ...entities[1],
        draftState: "modified",
        sourceConflict: "changed",
        drafts: { text: { def: "changed draft" } },
      },
    ];
    const english = renderListWithoutSelection({
      allEntities: conflictedEntities,
      entities: conflictedEntities,
    });
    const chinese = renderListWithoutSelection({
      allEntities: conflictedEntities,
      entities: conflictedEntities,
      locale: "zh",
      t: createTranslator("zh"),
    });

    expect(english).toContain("Draft source missing");
    expect(english).toContain("Draft source changed");
    expect(chinese).toContain("草稿源已缺失");
    expect(chinese).toContain("草稿源已变更");
  });

  it("distinguishes initial loading, filtered zero results, and an empty module", () => {
    const initialMarkup = renderListWithoutSelection({
      allEntities: [],
      entities: [],
      loading: true,
      totalCount: 8_279,
    });
    const filteredMarkup = renderListWithoutSelection({
      allEntities: [],
      entities: [],
      query: "missing",
    });
    const emptyMarkup = renderListWithoutSelection({
      allEntities: [],
      entities: [],
    });

    expect(initialMarkup).toContain("Loading module rows…");
    expect(initialMarkup).not.toContain("No drafts or source rows");
    expect(initialMarkup).not.toContain("module-catalog-footer");
    expect(filteredMarkup).toContain("0 results");
    expect(filteredMarkup).not.toContain("No drafts or source rows");
    expect(emptyMarkup).toContain("No drafts or source rows");
  });

  it("offers an explicit, honest recovery action when the project index is missing", () => {
    const missingMarkup = renderListWithoutSelection({
      allEntities: [],
      catalogMissing: true,
      catalogSearch: true,
      entities: [],
      onPrepareCatalog: () => undefined,
      totalCount: 0,
    });
    const preparingMarkup = renderListWithoutSelection({
      allEntities: [],
      catalogMissing: true,
      catalogPreparing: true,
      catalogSearch: true,
      entities: [],
      onPrepareCatalog: () => undefined,
      totalCount: 0,
    });
    const draftMarkup = renderListWithoutSelection({
      catalogMissing: true,
      catalogSearch: true,
      onPrepareCatalog: () => undefined,
    });
    const sourceFallbackMarkup = renderListWithoutSelection({
      catalogMissing: true,
      catalogSearch: false,
      onPrepareCatalog: () => undefined,
    });

    expect(missingMarkup).toContain("Optional project index is not prepared");
    expect(missingMarkup).toContain("remain editable and buildable below");
    expect(missingMarkup).toContain("about 14 minutes");
    expect(missingMarkup).toContain("2.1 GiB");
    expect(missingMarkup).toContain("cannot currently be cancelled");
    expect(missingMarkup).toContain("Prepare optional project index");
    expect(missingMarkup).toMatch(/<input[^>]*disabled=""[^>]*placeholder="Search internal module ID"/);
    expect(sourceFallbackMarkup).toMatch(/<input[^>]*placeholder="Search objects, ids, paths"/);
    expect(sourceFallbackMarkup).not.toMatch(/<input[^>]*disabled=""[^>]*placeholder="Search objects, ids, paths"/);
    expect(missingMarkup).toContain('aria-label="New"');
    expect(missingMarkup).not.toContain("Retry");
    expect(draftMarkup).toContain("Optional project index is not prepared");
    expect(draftMarkup).toContain("Alpha Idea");
    expect(preparingMarkup).toContain("Preparing project index…");
    expect(preparingMarkup).toContain("module-catalog-recovery-spinner");
    expect(preparingMarkup).toContain('class="module-catalog-recovery-status" role="status"');
    expect(preparingMarkup).toContain('<button class="toolbar-button" disabled=""');
    expect(preparingMarkup).toMatch(/aria-label="New"[^>]*disabled=""/);
  });

  it("discloses the permanent whole-folder deletion scope before marking a saved module", () => {
    const markup = renderRemovalDialog();

    expect(markup).toContain("No folder is deleted until you click Apply");
    expect(markup).toContain("permanently deletes the entire module folder");
    expect(markup).toContain("files that are not shown or indexed here");
    expect(markup).toContain("This cannot be undone");
    expect(markup).toContain("/workspace/projects/PIHC3/src/modules/idea/IDEA_ALPHA");
    expect(markup).toContain("2 indexed file(s)");
  });
});
