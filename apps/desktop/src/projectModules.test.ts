import { describe, expect, it } from "vitest";
import { featureModules as baseFeatureModules } from "./data/shell";
import { en } from "./i18n/locales/en";
import { zh } from "./i18n/locales/zh";
import {
  applyModuleOrder,
  familyIdFromTemplateFamily,
  moduleAccentIndex,
  modulesForProjectState,
  moduleTitleKeyForFamilyId,
  moveModuleBefore,
  projectBrowserForFamily,
  projectDiagramFamilyCapability,
  projectDiagramNodeIntent,
  projectDiagramSelectionValues,
  projectDiagramTitleKeyForFamilyId,
  supportsProjectDiagramFamily,
} from "./projectModules";
import type { ProjectBrowserPayload, ProjectTemplatesPayload } from "./types";

const MIO_NODE_AUTHORING = {
  title: "Add MIO trait",
  description: "Create a trait in the selected organization.",
  fields: [
    {
      name: "trait_id",
      label: "Trait ID",
      kind: "text" as const,
      required: true,
    },
    {
      name: "title",
      label: "Title",
      kind: "text" as const,
      required: true,
    },
  ],
  selection_defaults: [
    { field: "organization_id", source: "organization_id" },
    { field: "parent_trait_id", source: "trait_id" },
    { field: "source_path", source: "source_path" },
    { field: "source_revision", source: "source_revision" },
    { field: "x", source: "x" },
    { field: "y", source: "y", offset: 1 },
  ],
  requires_selection: true as const,
};

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
      group: "country",
      title_key: "modules.ideas.title",
      visible: true,
      item_count: 390,
      source_count: 780,
      layouts: ["canonical"],
    },
    {
      id: "achievements",
      family: "achievements",
      title: "Achievements",
      group: "events",
      title_key: "modules.achievements.title",
      visible: true,
      item_count: 49,
      source_count: 147,
      layouts: ["canonical"],
    },
    {
      id: "countries",
      family: "country",
      title: "Countries",
      group: "country",
      title_key: "modules.countries.title",
      visible: true,
      item_count: 67,
      source_count: 201,
      layouts: ["canonical"],
    },
    {
      id: "decisions",
      family: "decision",
      title: "Decisions",
      group: "country",
      title_key: "modules.decisions.title",
      visible: true,
      item_count: 0,
      source_count: 0,
      layouts: [],
    },
    {
      id: "entity",
      family: "entity",
      title: "Entity",
      group: "shared",
      title_key: "modules.entity.title",
      visible: true,
      item_count: 0,
      source_count: 0,
      layouts: [],
    },
    {
      id: "state-lore",
      family: "state_lore",
      title: "State Lore",
      group: "events",
      title_key: "modules.stateLore.title",
      visible: true,
      item_count: 0,
      source_count: 0,
      layouts: [],
    },
  ],
  items: [],
};

const templates: ProjectTemplatesPayload = {
  schema: "paradev.sdk.templates.v1",
  project_id: "PIHC3",
  profile: "hoi4",
  templates: [
    {
      id: "pihc3:idea/legacy-current",
      title: "PIHC3 Idea",
      family: "idea",
      family_id: "ideas",
      source: "project",
      args: {},
      files: ["meta.yaml", "def.pdx", "main.loc"],
    },
    {
      id: "pihc3:achievement/basic",
      title: "PIHC3 Achievement",
      family: "achievement",
      family_id: "achievements",
      source: "project",
      args: {},
      files: ["meta.yaml", "def.pdx", "main.loc"],
    },
    {
      id: "pihc3:decision/basic",
      title: "PIHC3 Decision",
      family: "decision",
      family_id: "decisions",
      source: "project",
      args: {},
      files: ["meta.yaml", "def.pdx", "main.loc"],
    },
    {
      id: "pihc3:entity/basic",
      title: "PIHC3 Entity",
      family: "entity",
      family_id: "entity",
      source: "project",
      args: {},
      files: [
        "meta.yaml",
        "gfx/models/{object_id}/mesh.gfx",
        "gfx/models/{object_id}/entity.asset",
        "gfx/models/{object_id}/animations.asset",
      ],
    },
    {
      id: "pihc3:state_lore/basic",
      title: "PIHC3 State Lore",
      family: "state_lore",
      family_id: "state-lore",
      source: "project",
      args: {},
      files: [
        "meta.yaml",
        "scripted_localisation.pdx",
        "on_actions.pdx",
        "main.loc",
      ],
    },
  ],
};

const diagramBrowser: ProjectBrowserPayload = {
  ...browser,
  families: [
    {
      id: "focuses",
      family: "focus",
      title: "Focuses",
      item_count: 1,
      source_count: 1,
      layouts: ["canonical"],
      diagram: {
        id: "focus_tree",
        aliases: ["focus_trees", "focus", "focuses"],
        renderer: "focus-tree",
        title: "Focus tree",
        editable: true,
        authoring_kind: "diagram-node",
        scope_authoring_kind: "collection",
      },
    },
    {
      id: "technologies",
      family: "technology",
      title: "Technologies",
      item_count: 1,
      source_count: 1,
      layouts: ["canonical"],
      diagram: {
        id: "technology",
        aliases: ["technologies"],
        renderer: "technology",
        title: "Technology tree",
        editable: true,
        authoring_kind: "module",
        selection_defaults: [
          { field: "folder", source: "folder" },
          { field: "x", source: "x" },
          { field: "y", source: "y", offset: 2 },
          {
            field: "dependencies",
            source: "id",
            template: "dependencies = { {value} = 1 }",
          },
        ],
      },
    },
    {
      id: "doctrines",
      family: "doctrine",
      title: "Doctrines",
      item_count: 1,
      source_count: 1,
      layouts: ["canonical"],
      diagram: {
        id: "doctrine",
        aliases: ["doctrines"],
        renderer: "doctrine",
        title: "Doctrine tree",
        editable: true,
        authoring_kind: "module",
      },
    },
    {
      id: "military-industrial-organizations",
      family: "military_industrial_organization",
      title: "Military Industrial Organizations",
      visible: false,
      item_count: 1,
      source_count: 1,
      layouts: ["canonical"],
      diagram: {
        id: "military_industrial_organization",
        aliases: ["mio"],
        renderer: "mio-trait",
        title: "Military Industrial Organization tree",
        editable: true,
        authoring_kind: "diagram-node",
        initial_scope: "project",
        node_authoring: MIO_NODE_AUTHORING,
        show_when_source_hidden: true,
      },
    },
  ],
};

const PIHC3_VISIBLE_FAMILY_CATALOG = [
  ["achievement", "achievements"],
  ["autonomous_state", "autonomous-states"],
  ["balance_of_power", "balance-of-power"],
  ["bookmark", "bookmarks"],
  ["building", "buildings"],
  ["character", "characters"],
  ["continuous_focus", "continuous-focuses"],
  ["country", "countries"],
  ["decision", "decisions"],
  ["difficulty_setting", "difficulty-settings"],
  ["division", "divisions"],
  ["doctrine", "doctrines"],
  ["entity", "entity"],
  ["equipment", "equipment"],
  ["equipment_module", "equipment-module"],
  ["equipment_module_category", "equipment-module-category"],
  ["event", "events"],
  ["faction", "factions"],
  ["focus", "focuses"],
  ["game_rule", "game-rules"],
  ["idea_category", "idea-categories"],
  ["idea", "ideas"],
  ["ideology", "ideologies"],
  ["intelligence_agency", "intelligence-agencies"],
  ["inventory_item", "inventory-items"],
  ["modifier", "modifiers"],
  ["on_action", "on-actions"],
  ["operation", "operations"],
  ["operation_phase", "operation-phases"],
  ["operation_token", "operation-tokens"],
  ["operative_codename", "operative-codenames"],
  ["opinion_modifier", "opinion-modifiers"],
  ["portrait", "portraits"],
  ["resistance_activity", "resistance-activities"],
  ["resource", "resources"],
  ["scripted_effect", "scripted-effects"],
  ["scripted_gui", "scripted-guis"],
  ["scripted_trigger", "scripted-triggers"],
  ["special_project", "special-projects"],
  ["special_project_reward", "special-project-reward"],
  ["state_lore", "state-lore"],
  ["state", "states"],
  ["strategic_region", "strategic-regions"],
  ["superevent", "superevents"],
  ["technology", "technologies"],
  ["trait", "traits"],
  ["unit_medal", "unit-medals"],
  ["wargoal", "wargoals"],
] as const;

describe("project module list", () => {
  it("normalizes Registry family ids without a host-maintained vocabulary", () => {
    expect(familyIdFromTemplateFamily("idea")).toBe("idea");
    expect(familyIdFromTemplateFamily("achievement")).toBe("achievement");
    expect(familyIdFromTemplateFamily("country_defs")).toBe("country-defs");
    expect(familyIdFromTemplateFamily("scripted_effect")).toBe("scripted-effect");
    expect(familyIdFromTemplateFamily("state_lore")).toBe("state-lore");
    expect(familyIdFromTemplateFamily("continuous_focus")).toBe("continuous-focus");
    expect(familyIdFromTemplateFamily("entity")).toBe("entity");
    expect(familyIdFromTemplateFamily("weather_magic")).toBe("weather-magic");
  });

  it("keeps the complete visible PIHC3 family catalog localized and project-backed", () => {
    const projectBrowser: ProjectBrowserPayload = {
      ...browser,
      families: PIHC3_VISIBLE_FAMILY_CATALOG.map(([family, moduleId], index) => ({
        id: moduleId,
        family,
        title: family,
        title_key: "modules.ideas.title",
        group: "other",
        visible: true,
        item_count: index + 1,
        source_count: index + 1,
        layouts: ["canonical"],
      })),
    };
    const modules = modulesForProjectState(
      projectBrowser,
      null,
      baseFeatureModules,
    );
    const expectedIds = PIHC3_VISIBLE_FAMILY_CATALOG.map(
      ([, moduleId]) => moduleId,
    );

    expect(PIHC3_VISIBLE_FAMILY_CATALOG).toHaveLength(48);
    expect(modules.map((module) => module.id).sort()).toEqual(
      [...expectedIds].sort(),
    );
    for (const [family, moduleId] of PIHC3_VISIBLE_FAMILY_CATALOG) {
      const titleKey = moduleTitleKeyForFamilyId(moduleId, projectBrowser);
      expect(titleKey).toBeDefined();
      if (!titleKey) {
        throw new Error(`Missing module title key for ${moduleId}`);
      }
      expect(en[titleKey].trim()).not.toBe("");
      expect(zh[titleKey].trim()).not.toBe("");
      expect(zh[titleKey]).not.toBe(en[titleKey]);
      expect(modules.find((module) => module.id === moduleId)).toMatchObject({
        id: moduleId,
        titleKey,
      });
      expect(projectBrowserForFamily(projectBrowser, family)?.families).toEqual([
        expect.objectContaining({ id: moduleId, family }),
      ]);
    }
    for (const phantomId of ["assets", "localization", "map", "music"]) {
      expect(modules.some((module) => module.id === phantomId)).toBe(false);
    }
  });

  it("discovers a project-exclusive family without desktop source changes", () => {
    const externalBrowser: ProjectBrowserPayload = {
      ...browser,
      families: [
        {
          id: "weather-magic",
          family: "weather_magic",
          title: "Weather Magic",
          group: "events",
          visible: true,
          item_count: 2,
          source_count: 4,
          layouts: ["canonical"],
        },
      ],
    };
    const externalTemplates: ProjectTemplatesPayload = {
      ...templates,
      templates: [
        {
          id: "pihc3:weather_magic/basic",
          title: "Weather magic",
          family: "weather_magic",
          source: "project",
          args: {},
          files: ["def.txt", "main.loc"],
        },
      ],
    };

    expect(
      modulesForProjectState(externalBrowser, externalTemplates, baseFeatureModules),
    ).toEqual([
      expect.objectContaining({
        id: "weather-magic",
        label: "Weather Magic",
        groupKey: "modules.group.events",
        count: 2,
        status: "ready",
      }),
    ]);
  });

  it("uses only a Registry-provided localized module title", () => {
    const assetBrowser: ProjectBrowserPayload = {
      ...browser,
      families: [{
        id: "assets",
        family: "asset",
        title: "Assets",
        title_key: "modules.assets.title",
        item_count: 0,
        source_count: 0,
        layouts: [],
      }],
    };
    expect(moduleTitleKeyForFamilyId("assets", assetBrowser)).toBe(
      "modules.assets.title",
    );
    expect(moduleTitleKeyForFamilyId("assets")).toBeUndefined();
  });

  it("routes only truthful tree projections to dedicated diagram surfaces", () => {
    expect(
      projectDiagramFamilyCapability(diagramBrowser, "focus_tree"),
    ).toEqual({
      authoringKind: "diagram-node",
      editable: true,
      familyId: "focuses",
      initialScope: "selected-entity",
      relationships: [],
      renderer: "focus-tree",
      scopeAuthoringKind: "collection",
      sdkFamily: "focus_tree",
      selectionDefaults: [],
      sourceBacked: true,
      title: "Focus tree",
      titleKey: "workspace.diagram.family.focusTree",
    });
    expect(
      projectDiagramFamilyCapability(diagramBrowser, "technology"),
    ).toEqual({
      authoringKind: "module",
      editable: true,
      familyId: "technologies",
      initialScope: "selected-entity",
      relationships: [],
      renderer: "technology",
      sdkFamily: "technology",
      selectionDefaults: [
        { field: "folder", source: "folder" },
        { field: "x", source: "x" },
        { field: "y", source: "y", offset: 2 },
        {
          field: "dependencies",
          source: "id",
          template: "dependencies = { {value} = 1 }",
        },
      ],
      sourceBacked: true,
      title: "Technology tree",
      titleKey: "workspace.diagram.family.technologyTree",
    });
    expect(projectDiagramFamilyCapability(diagramBrowser, "doctrine")).toEqual({
      authoringKind: "module",
      editable: true,
      familyId: "doctrines",
      initialScope: "selected-entity",
      relationships: [],
      renderer: "doctrine",
      sdkFamily: "doctrine",
      selectionDefaults: [],
      sourceBacked: true,
      title: "Doctrine tree",
      titleKey: "workspace.diagram.family.doctrineTree",
    });
    expect(projectDiagramTitleKeyForFamilyId(diagramBrowser, "doctrines")).toBe(
      "workspace.diagram.family.doctrineTree",
    );
    expect(en["workspace.diagram.family.doctrineTree"]).toBe("Doctrine tree");
    expect(zh["workspace.diagram.family.doctrineTree"]).toBe("学说树");
    expect(supportsProjectDiagramFamily(diagramBrowser, "doctrines")).toBe(
      true,
    );

    expect(projectDiagramFamilyCapability(diagramBrowser, "mio")).toEqual({
      authoringKind: "diagram-node",
      editable: true,
      familyId: "military-industrial-organizations",
      initialScope: "project",
      nodeAuthoring: MIO_NODE_AUTHORING,
      readOnlyReasonKey: "workspace.diagram.mio.readOnlyReason",
      relationships: [],
      renderer: "mio-trait",
      sdkFamily: "military_industrial_organization",
      selectionDefaults: [],
      showWhenSourceHidden: true,
      sourceBacked: true,
      title: "Military Industrial Organization tree",
      titleKey: "workspace.diagram.family.mioTree",
    });
    expect(projectDiagramTitleKeyForFamilyId(diagramBrowser, "mio")).toBe(
      "workspace.diagram.family.mioTree",
    );
    expect(en["workspace.diagram.family.mioTree"]).toBe(
      "Military Industrial Organization trait tree",
    );
    expect(zh["workspace.diagram.family.mioTree"]).toBe("军工机构特质树");
    expect(supportsProjectDiagramFamily(diagramBrowser, "mio")).toBe(true);
  });

  it("projects provider-owned selected-node defaults without family logic", () => {
    const capability = projectDiagramFamilyCapability(
      diagramBrowser,
      "technology",
    );

    expect(
      projectDiagramSelectionValues(capability, {
        id: "TECH_PARENT",
        folder: "industry_folder",
        x: 4,
        y: 7,
      }),
    ).toEqual({
      dependencies: "dependencies = { TECH_PARENT = 1 }",
      folder: "industry_folder",
      x: "4",
      y: "9",
    });
    expect(
      projectDiagramSelectionValues(capability, {
        id: "",
        folder: null,
        x: Number.NaN,
        y: "not-a-number",
      }),
    ).toEqual({});
  });

  it("projects a provider-owned node intent only from an editable selection", () => {
    const capability = projectDiagramFamilyCapability(diagramBrowser, "mio");
    const selected = {
      editable: true,
      organization_id: "example_org",
      trait_id: "parent_trait",
      source_path: "src/modules/mio/example/def.txt",
      source_revision: `sha256:${"a".repeat(64)}`,
      x: 4,
      y: 7,
    };

    expect(projectDiagramNodeIntent(capability, selected)).toEqual({
      organization_id: "example_org",
      parent_trait_id: "parent_trait",
      source_path: "src/modules/mio/example/def.txt",
      source_revision: `sha256:${"a".repeat(64)}`,
      x: 4,
      y: 8,
    });
    expect(
      projectDiagramNodeIntent(capability, {
        ...selected,
        editable: false,
      }),
    ).toBeNull();
    expect(
      projectDiagramNodeIntent(capability, {
        ...selected,
        source_revision: null,
      }),
    ).toBeNull();
  });

  it("allows provider-owned root-node authoring without a selection", () => {
    const capability = projectDiagramFamilyCapability(diagramBrowser, "mio");
    if (!capability?.nodeAuthoring) {
      throw new Error("MIO diagram node authoring capability is required");
    }
    const rootCapability = {
      ...capability,
      nodeAuthoring: {
        ...capability.nodeAuthoring,
        selection_defaults: [],
        requires_selection: false as const,
      },
    };

    expect(projectDiagramNodeIntent(rootCapability, null)).toEqual({});
  });

  it("exposes template-only families in the GUI module list", () => {
    const modules = modulesForProjectState(
      browser,
      templates,
      baseFeatureModules,
    );
    const byId = new Map(modules.map((module) => [module.id, module]));

    expect(byId.get("ideas")).toMatchObject({ status: "ready", count: 390 });
    expect(byId.get("achievements")).toMatchObject({
      id: "achievements",
      titleKey: "modules.achievements.title",
      status: "ready",
      count: 49,
    });
    expect(byId.get("countries")).toMatchObject({ status: "ready", count: 67 });
    expect(byId.get("decisions")).toMatchObject({ status: "scaffold" });
    expect(byId.get("entity")).toMatchObject({
      id: "entity",
      titleKey: "modules.entity.title",
      status: "scaffold",
    });
    expect(byId.get("state-lore")).toMatchObject({
      id: "state-lore",
      titleKey: "modules.stateLore.title",
      status: "scaffold",
    });
    expect(
      modules.filter((module) => module.id === "achievements"),
    ).toHaveLength(1);
    expect(modules.some((module) => module.id === "achievement")).toBe(false);
    expect(modules.some((module) => module.id === "country-defs")).toBe(false);
  });

  it("keeps migration support families out of normal authoring navigation", () => {
    const modules = modulesForProjectState(
      {
        ...browser,
        families: [
          ...browser.families,
          {
            id: "flag-asset-component",
            family: "flag_asset_component",
            title: "Flag Asset Component",
            visible: false,
            item_count: 1110,
            source_count: 2480,
            layouts: ["canonical"],
          },
          {
            id: "common-component",
            family: "common_component",
            title: "Common Component",
            visible: false,
            item_count: 48,
            source_count: 127,
            layouts: ["canonical"],
          },
          {
            id: "military-industrial-organizations",
            family: "military_industrial_organization",
            title: "Military Industrial Organization",
            group: "military",
            title_key: "modules.militaryIndustrialOrganizations.title",
            visible: false,
            item_count: 7,
            source_count: 28,
            layouts: ["canonical"],
            diagram: {
              id: "military_industrial_organization",
              aliases: ["mio"],
              renderer: "mio-trait",
              title: "Military Industrial Organization tree",
              editable: true,
              show_when_source_hidden: true,
            },
          },
          {
            id: "special-projects",
            family: "special_project",
            title: "Special Project",
            group: "military",
            title_key: "modules.specialProjects.title",
            item_count: 18,
            source_count: 54,
            layouts: ["canonical"],
          },
          {
            id: "equipment-module-category",
            family: "equipment_module_category",
            title: "Equipment Module Category",
            group: "military",
            title_key: "modules.equipmentModuleCategories.title",
            item_count: 49,
            source_count: 98,
            layouts: ["canonical"],
          },
          {
            id: "visible-component",
            family: "visible_component",
            title: "Visible Component",
            visible: true,
            item_count: 2,
            source_count: 4,
            layouts: ["canonical"],
          },
          {
            id: "hidden-technical",
            family: "hidden_technical",
            title: "Hidden Technical",
            visible: false,
            item_count: 3,
            source_count: 6,
            layouts: ["canonical"],
          },
        ],
      },
      {
        ...templates,
        templates: [
          ...templates.templates,
          {
            id: "test:hidden-technical/basic",
            title: "Hidden Technical",
            family: "hidden_technical",
            source: "project",
            args: {},
            files: ["def.pdx"],
          },
        ],
      },
      baseFeatureModules,
    );
    const byId = new Map(modules.map((module) => [module.id, module]));

    expect(byId.has("flag-asset-component")).toBe(false);
    expect(byId.has("common-component")).toBe(false);
    expect(byId.get("military-industrial-organizations")).toMatchObject({
      titleKey: "modules.militaryIndustrialOrganizations.title",
      status: "ready",
      count: 7,
    });
    expect(byId.get("special-projects")).toMatchObject({
      titleKey: "modules.specialProjects.title",
      status: "ready",
      count: 18,
    });
    expect(byId.get("equipment-module-category")).toMatchObject({
      titleKey: "modules.equipmentModuleCategories.title",
      status: "ready",
      count: 49,
    });
    expect(byId.get("visible-component")).toMatchObject({
      label: "Visible Component",
      status: "ready",
      count: 2,
    });
    expect(byId.has("hidden-technical")).toBe(false);
    expect(byId.has("assets")).toBe(false);
    expect(byId.has("localization")).toBe(false);
    expect(byId.has("map")).toBe(false);
    expect(byId.has("music")).toBe(false);
  });

  it("keeps module accents deterministic from stable ids", () => {
    expect(moduleAccentIndex("countries")).toBe(moduleAccentIndex("countries"));
    expect(moduleAccentIndex("operative-codenames")).toBeGreaterThanOrEqual(0);
    expect(moduleAccentIndex("operative-codenames")).toBeLessThan(10);
  });

  it("applies and updates persisted module order without losing new modules", () => {
    const modules = [
      { id: "countries" },
      { id: "characters" },
      { id: "operative-codenames" },
      { id: "ideas" },
    ];

    expect(
      applyModuleOrder(modules, ["ideas", "countries"]).map(
        (module) => module.id,
      ),
    ).toEqual(["ideas", "countries", "characters", "operative-codenames"]);
    expect(
      moveModuleBefore(modules, "ideas", "characters").map(
        (module) => module.id,
      ),
    ).toEqual(["countries", "ideas", "characters", "operative-codenames"]);
    expect(moveModuleBefore(modules, "missing", "characters")).toBe(modules);
  });

  it("narrows full cached browser payloads before rendering one module editor", () => {
    const scoped = projectBrowserForFamily(
      {
        ...browser,
        items: [
          {
            id: "idea/IDEA_ALPHA",
            kind: "module",
            layout: "canonical",
            family_id: "ideas",
            family: "idea",
            object_id: "IDEA_ALPHA",
            title: "Idea Alpha",
            root: "/workspace/projects/PIHC3/src/modules/idea/IDEA_ALPHA",
            relative_root: "src/modules/idea/IDEA_ALPHA",
            source_count: 1,
            sources: [],
          },
          {
            id: "achievement/ACH_ALPHA",
            kind: "module",
            layout: "canonical",
            family_id: "achievements",
            family: "achievements",
            object_id: "ACH_ALPHA",
            title: "Achievement Alpha",
            root: "/workspace/projects/PIHC3/src/modules/achievement/ACH_ALPHA",
            relative_root: "src/modules/achievement/ACH_ALPHA",
            source_count: 1,
            sources: [],
          },
        ],
      },
      "ideas",
    );

    expect(scoped?.families.map((family) => family.id)).toEqual(["ideas"]);
    expect(scoped?.items.map((item) => item.id)).toEqual(["idea/IDEA_ALPHA"]);
  });
});
