import { describe, expect, it } from "vitest";
import type {
  ProjectCatalogQueryPayload,
  ProjectCatalogRow,
} from "./services/paradev";
import {
  loadingModuleCatalogFamilyState,
  mergeProjectCatalogRows,
  moduleCatalogBrowser,
  moduleCatalogFamilyStateWithDiscoveredRow,
  moduleCatalogFamilyStateWithHydratedRow,
  moduleCatalogFamilyStateWithPage,
  moduleCatalogModuleIdForEntity,
  moduleCatalogRowMatchesEntity,
  moduleCatalogTargetIdForEntity,
  projectBrowserItemFromCatalogRow,
} from "./moduleCatalog";
import type { ProjectBrowserPayload } from "./types";
import { buildModuleEntities } from "./moduleEditor/model";

const PROJECT_ROOT = "/tmp/PIHC3";

function catalogRow(
  overrides: Partial<ProjectCatalogRow> = {},
): ProjectCatalogRow {
  return {
    object_id: "catalog:module:hash-1",
    target_id: "module:hash-1",
    target_entity: "hoi4-module",
    name: "scripted_effect/ADD_FOG_OF_WAR_BUILDING",
    desc: "",
    tags: [
      "module",
      "scripted_effect",
      "scripted_effect/ADD_FOG_OF_WAR_BUILDING",
    ],
    active: true,
    workspace_id: "PIHC3-hoi4",
    ...overrides,
  };
}

function hydratedCatalogData(
  moduleId = "scripted_effect/ADD_FOG_OF_WAR_BUILDING",
  overrides: Record<string, unknown> = {},
): Record<string, unknown> {
  const separator = moduleId.indexOf("/");
  const family = moduleId.slice(0, separator);
  const objectId = moduleId.slice(separator + 1);
  return {
    module_id: moduleId,
    family,
    root: `${PROJECT_ROOT}/src/modules/${family}/${objectId}`,
    source_slots: { def: ["def.pdx"] },
    metadata: {},
    ...overrides,
  };
}

function queryPayload(
  offset: number,
  rows: ProjectCatalogRow[],
): ProjectCatalogQueryPayload {
  return {
    schema: "paradev.hb.catalog-query.v1",
    project_id: "PIHC3",
    database: `${PROJECT_ROOT}/.paradev/.cache/hb/catalog.sqlite`,
    filters: {
      entity: "hoi4-module",
      tag: "scripted_effect",
      limit: 100,
      ...(offset ? { offset } : {}),
      include_data: false,
    },
    total_count: 1_116_679,
    filtered_count: 8_279,
    count: rows.length,
    data_included: false,
    page: {
      offset,
      limit: 100,
      has_more: true,
      next_offset: offset + rows.length,
    },
    rows,
  };
}

const browser: ProjectBrowserPayload = {
  schema: "paradev.sdk.project-browser.v1",
  project_id: "PIHC3",
  title: "PIHC3",
  root: PROJECT_ROOT,
  profile: "hoi4",
  filters: {},
  families: [
    {
      id: "scripted-effects",
      family: "scripted_effect",
      title: "Scripted effects",
      item_count: 8_279,
      source_count: 8_279,
      layouts: ["canonical"],
    },
  ],
  items: [],
  diagnostics: [],
};

describe("module Catalog paging model", () => {
  it("maps lightweight Catalog rows to list-ready browser items", () => {
    const item = projectBrowserItemFromCatalogRow(
      catalogRow(),
      "scripted_effect",
      PROJECT_ROOT,
      "scripted-effects",
    );

    expect(item).toMatchObject({
      id: "module:scripted_effect/ADD_FOG_OF_WAR_BUILDING",
      family_id: "scripted-effects",
      family: "scripted_effect",
      object_id: "ADD_FOG_OF_WAR_BUILDING",
      module_id: "scripted_effect/ADD_FOG_OF_WAR_BUILDING",
      title: "ADD_FOG_OF_WAR_BUILDING",
      root: "",
      relative_root: "",
      source_count: 0,
      sources: [],
    });
  });

  it("maps hydrated module data to editable source rows", () => {
    const item = projectBrowserItemFromCatalogRow(
      catalogRow({
        name: "focus_tree/C01_MAIN",
        data: {
          module_id: "focus_tree/C01_MAIN",
          family: "focus_tree",
          root: `${PROJECT_ROOT}/src/modules/focus_tree/C01_MAIN`,
          source_slots: {
            def: [`${PROJECT_ROOT}/src/modules/focus_tree/C01_MAIN/def.pdx`],
            loc: ["main.loc"],
          },
          metadata: { title: "C01 main focus tree" },
          collection_id: "C01",
        },
      }),
      "focus_tree",
      PROJECT_ROOT,
      "focuses",
    );

    expect(item.family_id).toBe("focuses");
    expect(item.title).toBe("C01 main focus tree");
    expect(item.collection_id).toBe("C01");
    expect(item.relative_root).toBe("src/modules/focus_tree/C01_MAIN");
    expect(item.source_root).toBe(`${PROJECT_ROOT}/src`);
    expect(item.source_root_relative_path).toBe("src");
    expect(item.localized_titles).toBeUndefined();
    expect(item.sources).toEqual([
      {
        slot: "def",
        name: "def.pdx",
        path: `${PROJECT_ROOT}/src/modules/focus_tree/C01_MAIN/def.pdx`,
        relative_path: "src/modules/focus_tree/C01_MAIN/def.pdx",
        extension: "pdx",
      },
      {
        slot: "loc",
        name: "main.loc",
        path: `${PROJECT_ROOT}/src/modules/focus_tree/C01_MAIN/main.loc`,
        relative_path: "src/modules/focus_tree/C01_MAIN/main.loc",
        extension: "loc",
      },
    ]);
  });

  it("appends pages without duplicates or hydrated-row downgrades", () => {
    const first = catalogRow({
      name: "scripted_effect/ONE",
      data: hydratedCatalogData("scripted_effect/ONE"),
    });
    const duplicateLightweight = catalogRow({ name: "scripted_effect/ONE" });
    const duplicateInvalid = catalogRow({
      name: "scripted_effect/ONE",
      data: {},
    });
    const second = catalogRow({
      target_id: "module:hash-2",
      object_id: "catalog:module:hash-2",
      name: "scripted_effect/TWO",
    });

    expect(
      mergeProjectCatalogRows([first], [duplicateLightweight, second]),
    ).toEqual([first, second]);
    expect(mergeProjectCatalogRows([first], [duplicateInvalid])).toEqual([
      first,
    ]);

    const initial = moduleCatalogFamilyStateWithPage(
      undefined,
      queryPayload(0, [first]),
      PROJECT_ROOT,
      "scripted_effect",
    );
    const appended = moduleCatalogFamilyStateWithPage(
      initial,
      queryPayload(1, [duplicateLightweight, second]),
      PROJECT_ROOT,
      "scripted_effect",
    );
    expect(appended.rows).toEqual([first, second]);
    expect(appended.nextOffset).toBe(3);
  });

  it("rejects stale family identities and discontinuous append offsets", () => {
    const first = moduleCatalogFamilyStateWithPage(
      undefined,
      queryPayload(0, [catalogRow()]),
      PROJECT_ROOT,
      "scripted_effect",
    );
    const otherFamilyLoading = loadingModuleCatalogFamilyState(
      first,
      PROJECT_ROOT,
      "idea",
    );
    const discontinuous = moduleCatalogFamilyStateWithPage(
      first,
      queryPayload(100, [catalogRow({ target_id: "module:hash-2" })]),
      PROJECT_ROOT,
      "scripted_effect",
    );

    expect(otherFamilyLoading.rows).toEqual([]);
    expect(otherFamilyLoading.filteredCount).toBe(0);
    expect(discontinuous.rows).toEqual(first.rows);
    expect(discontinuous.error).toContain("out of sequence");
  });

  it("resolves only lightweight selected rows for one-row hydration", () => {
    const state = moduleCatalogFamilyStateWithPage(
      undefined,
      queryPayload(0, [catalogRow()]),
      PROJECT_ROOT,
      "scripted_effect",
    );

    expect(
      moduleCatalogTargetIdForEntity(
        state,
        "module:scripted_effect/ADD_FOG_OF_WAR_BUILDING",
      ),
    ).toBe("module:hash-1");

    const hydrated = moduleCatalogFamilyStateWithHydratedRow(
      state,
      catalogRow({ data: hydratedCatalogData() }),
    );
    expect(
      moduleCatalogTargetIdForEntity(
        hydrated,
        "module:scripted_effect/ADD_FOG_OF_WAR_BUILDING",
      ),
    ).toBeNull();

    const unknown = catalogRow({
      target_id: "module:other",
      name: "scripted_effect/OTHER",
    });
    expect(moduleCatalogFamilyStateWithHydratedRow(hydrated, unknown)).toBe(
      hydrated,
    );
    expect(
      moduleCatalogFamilyStateWithDiscoveredRow(hydrated, unknown).rows,
    ).toHaveLength(2);
  });

  it("matches logical module identities without treating Catalog target hashes as editor ids", () => {
    const row = catalogRow();

    expect(
      moduleCatalogModuleIdForEntity(
        " module:scripted_effect/ADD_FOG_OF_WAR_BUILDING ",
      ),
    ).toBe("scripted_effect/ADD_FOG_OF_WAR_BUILDING");
    expect(
      moduleCatalogRowMatchesEntity(
        row,
        "module:scripted_effect/ADD_FOG_OF_WAR_BUILDING",
      ),
    ).toBe(true);
    expect(moduleCatalogRowMatchesEntity(row, row.target_id)).toBe(false);
  });

  it("builds a family browser with loaded rows and persisted total count", () => {
    const loading = loadingModuleCatalogFamilyState(
      undefined,
      PROJECT_ROOT,
      "scripted_effect",
    );
    const state = moduleCatalogFamilyStateWithPage(
      loading,
      queryPayload(0, [catalogRow()]),
      PROJECT_ROOT,
      "scripted_effect",
    );
    const familyBrowser = moduleCatalogBrowser(
      browser,
      "scripted-effects",
      state,
    );

    expect(familyBrowser.items).toHaveLength(1);
    expect(familyBrowser.families[0]).toMatchObject({
      id: "scripted-effects",
      family: "scripted_effect",
      item_count: 8_279,
      title: "Scripted effects",
    });
  });

  it("keeps SDK-declared missing image targets through Catalog hydration", () => {
    const row = catalogRow({ data: hydratedCatalogData() });
    const baseItem = projectBrowserItemFromCatalogRow(
      row,
      "scripted_effect",
      PROJECT_ROOT,
      "scripted-effects",
    );
    const targetPath =
      "src/modules/scripted_effect/ADD_FOG_OF_WAR_BUILDING/icon.png";
    const state = moduleCatalogFamilyStateWithPage(
      undefined,
      queryPayload(0, [row]),
      PROJECT_ROOT,
      "scripted_effect",
    );
    const familyBrowser = moduleCatalogBrowser(
      {
        ...browser,
        items: [
          {
            ...baseItem,
            sources: baseItem.sources.map((source) => ({
              ...source,
              slot_kinds: ["pdx"],
            })),
            image_targets: [
              {
                slot: "icon",
                name: "icon.png",
                path: `${PROJECT_ROOT}/${targetPath}`,
                relative_path: targetPath,
                extension: "png",
                exists: false,
              },
            ],
            resource_slots: [
              {
                name: "assets",
                match: "assets/**",
                required: false,
                many: true,
                regex: false,
                kind: "copy",
                shared: false,
                authoring_path: "assets/{filename}",
              },
            ],
          },
        ],
      },
      "scripted-effects",
      state,
    );

    expect(familyBrowser.items[0].image_targets).toEqual([
      {
        slot: "icon",
        name: "icon.png",
        path: `${PROJECT_ROOT}/${targetPath}`,
        relative_path: targetPath,
        extension: "png",
        exists: false,
      },
    ]);
    expect(familyBrowser.items[0].sources[0].slot_kinds).toEqual(["pdx"]);
    expect(familyBrowser.items[0].resource_slots).toEqual([
      expect.objectContaining({
        name: "assets",
        kind: "copy",
        authoring_path: "assets/{filename}",
      }),
    ]);
  });

  it("normalizes Windows source paths and keeps hydrated metadata titles visible", () => {
    const item = projectBrowserItemFromCatalogRow(
      catalogRow({
        name: "idea/IDEA_ALPHA",
        data: {
          module_id: "idea/IDEA_ALPHA",
          family: "idea",
          root: "c:\\Modules\\Archive\\PIHC3\\src\\modules\\idea\\IDEA_ALPHA - Alpha Idea",
          source_slots: { def: ["def.pdx"] },
          metadata: { title: "Alpha Idea" },
        },
      }),
      "idea",
      "C:\\Modules\\Archive\\PIHC3",
      "ideas",
    );

    expect(item.title).toBe("Alpha Idea");
    expect(item.relative_root).toBe("src/modules/idea/IDEA_ALPHA - Alpha Idea");
    expect(item.source_root).toBe("c:/Modules/Archive/PIHC3/src");
    expect(item.sources[0]?.relative_path).toBe(
      "src/modules/idea/IDEA_ALPHA - Alpha Idea/def.pdx",
    );
  });

  it("infers each row's source root from the final modules boundary", () => {
    const sourceRoots = ["/tmp/mods/alpha/src", "/tmp/mods/beta/content"];
    const items = sourceRoots.map((sourceRoot) =>
      projectBrowserItemFromCatalogRow(
        catalogRow({
          data: hydratedCatalogData("scripted_effect/ADD_FOG_OF_WAR_BUILDING", {
            root: `${sourceRoot}/modules/scripted_effect/ADD_FOG_OF_WAR_BUILDING - Fog of War`,
          }),
        }),
        "scripted_effect",
        "/tmp/mods",
        "scripted-effects",
      ),
    );

    expect(items.map((item) => item.source_root)).toEqual(sourceRoots);
    expect(items[0]?.id).toBe(items[1]?.id);
  });

  it("infers a UNC source root without collapsing the network prefix", () => {
    const item = projectBrowserItemFromCatalogRow(
      catalogRow({
        name: "idea/IDEA_ALPHA",
        data: hydratedCatalogData("idea/IDEA_ALPHA", {
          root: "\\\\server\\share\\modules\\archive\\src\\modules\\idea\\IDEA_ALPHA - Alpha Idea",
        }),
      }),
      "idea",
      "\\\\server\\share\\modules\\archive",
      "ideas",
    );

    expect(item.source_root).toBe("//server/share/modules/archive/src");
    expect(item.source_root_relative_path).toBe("src");
  });

  it.each([
    ["an empty object", {}],
    [
      "a partial object",
      {
        module_id: "scripted_effect/ADD_FOG_OF_WAR_BUILDING",
        family: "scripted_effect",
      },
    ],
    ["a mismatched module id", hydratedCatalogData("scripted_effect/OTHER")],
    ["a mismatched family", hydratedCatalogData(undefined, { family: "idea" })],
    [
      "a mismatched root",
      hydratedCatalogData(undefined, {
        root: `${PROJECT_ROOT}/src/modules/scripted_effect/OTHER`,
      }),
    ],
    [
      "invalid source slots",
      hydratedCatalogData(undefined, { source_slots: { def: "def.pdx" } }),
    ],
    ["invalid metadata", hydratedCatalogData(undefined, { metadata: [] })],
  ])("keeps %s lightweight and retryable", (_label, data) => {
    const state = moduleCatalogFamilyStateWithPage(
      undefined,
      queryPayload(0, [catalogRow()]),
      PROJECT_ROOT,
      "scripted_effect",
    );
    const invalidHydration = moduleCatalogFamilyStateWithHydratedRow(
      state,
      catalogRow({ data }),
    );
    const [row] = invalidHydration.rows;
    const item = projectBrowserItemFromCatalogRow(
      row,
      "scripted_effect",
      PROJECT_ROOT,
      "scripted-effects",
    );

    expect(row?.data).toBeUndefined();
    expect(
      moduleCatalogTargetIdForEntity(
        invalidHydration,
        "module:scripted_effect/ADD_FOG_OF_WAR_BUILDING",
      ),
    ).toBe("module:hash-1");
    expect(item.sources).toEqual([]);
    expect(item.root).toBe("");
  });

  it.each([
    ["another module", "scripted_effect/OTHER"],
    ["another family", "idea/ADD_FOG_OF_WAR_BUILDING"],
  ])("rejects a hydrated target response for %s", (_label, moduleId) => {
    const state = moduleCatalogFamilyStateWithPage(
      undefined,
      queryPayload(0, [catalogRow()]),
      PROJECT_ROOT,
      "scripted_effect",
    );
    const mismatched = catalogRow({
      name: moduleId,
      data: hydratedCatalogData(moduleId),
    });

    expect(moduleCatalogFamilyStateWithHydratedRow(state, mismatched)).toBe(
      state,
    );
    expect(
      moduleCatalogTargetIdForEntity(
        state,
        "module:scripted_effect/ADD_FOG_OF_WAR_BUILDING",
      ),
    ).toBe("module:hash-1");
  });

  it("preserves PIHC3 focus metadata needed to expose migrated focus info editors", () => {
    const item = projectBrowserItemFromCatalogRow(
      catalogRow({
        name: "focus_tree/C01_MAIN",
        data: {
          module_id: "focus_tree/C01_MAIN",
          family: "focus_tree",
          root: `${PROJECT_ROOT}/src/modules/focus_tree/C01_MAIN`,
          source_slots: { def: ["def.txt"], loc: ["main.loc"] },
          metadata: {
            title: "C01 Main",
            settings: {
              source_focuses: [
                {
                  focus_id: "FOCUS_C01_CANTERLOT_PACT",
                  folder: "C01_CANTERLOT_PACT",
                },
              ],
            },
          },
        },
      }),
      "focus_tree",
      PROJECT_ROOT,
      "focuses",
    );
    const focusBrowser: ProjectBrowserPayload = {
      ...browser,
      families: [
        {
          id: "focuses",
          family: "focus_tree",
          title: "National Focuses",
          item_count: 1,
          source_count: 3,
          layouts: ["canonical"],
        },
      ],
      items: [item],
    };

    const [entity] = buildModuleEntities(focusBrowser, "focuses");

    expect(entity?.sourceSlots.map((source) => source.slot)).toEqual([
      "def",
      "loc",
      "focus:FOCUS_C01_CANTERLOT_PACT:info",
    ]);
    expect(entity?.sourceSlots.at(-1)?.path).toBe(
      `${PROJECT_ROOT}/src/modules/focus_tree/C01_MAIN/legacy/C01_CANTERLOT_PACT/info.json`,
    );
  });
});
