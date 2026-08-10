import { buildProjectDiagramDocument } from "../projectDiagram";
import type { DiagramDocument } from "../layoutModel";
import type { ProjectBrowserItem, ProjectBrowserPayload } from "../../types";
import { smokeProjectRoot } from "../../testFixtures/smokeImages";

export const sourceBackedSmokeProjectRoot = smokeProjectRoot;

export const sourceBackedSmokeFocusIds = [
  "FOCUS_C08_CANTERLOT_MIND",
  "FOCUS_C08_SECOND_SUMMIT",
  "FOCUS_C08_TO_THE_WAR",
  "FOCUS_C08_THE_RISING_FIRE",
  "FOCUS_C08_PLAN_TWILIGHT",
  "FOCUS_C08_PLAN_STARLIGHT",
  "FOCUS_C08_PLAN_SUNBURST",
  "FOCUS_C08_T_TRIXIE",
  "FOCUS_C08_T_CADENCE"
] as const;

export const c01MainSmokeMetaYaml = `
type: focus_tree
title: C01 Main
settings:
    source_focuses:
    -   folder: C01_CANTERLOT_PACT
        focus_id: FOCUS_C01_CANTERLOT_PACT
        source_path: C01_CANTERLOT_PACT
        preview_url: src/modules/focus_tree/C01_MAIN/icons/FOCUS_C01_CANTERLOT_PACT.png
        tree: C01_MAIN
        parent: null
        x: 0
        y: 0
    -   folder: C01_COZY_GLOW_CORONATION
        focus_id: FOCUS_C01_COZY_GLOW_CORONATION
        source_path: C01_COZY_GLOW_CORONATION
        preview_url: src/modules/focus_tree/C01_MAIN/icons/FOCUS_C01_COZY_GLOW_CORONATION.png
        tree: C01_MAIN
        parent: FOCUS_C01_CANTERLOT_PACT
        priority: 10
    -   folder: C01_DEM_CHANGE
        focus_id: FOCUS_C01_DEM_CHANGE
        source_path: C01_DEM_CHANGE
        preview_url: src/modules/focus_tree/C01_MAIN/icons/FOCUS_C01_DEM_CHANGE.png
        tree: C01_MAIN
        parent: FOCUS_C01_CANTERLOT_PACT
        priority: 20
    focuses:
    -   id: FOCUS_C01_CANTERLOT_PACT
        icon: GFX_FOCUS_C01_CANTERLOT_PACT_icon
        x: 0
        y: 0
    -   id: FOCUS_C01_COZY_GLOW_CORONATION
        icon: GFX_FOCUS_C01_COZY_GLOW_CORONATION_icon
        prerequisite:
        - FOCUS_C01_CANTERLOT_PACT
    -   id: FOCUS_C01_DEM_CHANGE
        icon: GFX_FOCUS_C01_DEM_CHANGE_icon
        prerequisite:
        - FOCUS_C01_CANTERLOT_PACT
`;

export const c01CozyGlowSmokeSourceInfoText = `${JSON.stringify(
  {
    tree: "C01_MAIN",
    parent: "FOCUS_C01_CANTERLOT_PACT",
    prerequisite: {
      focus: "FOCUS_C01_CANTERLOT_PACT"
    },
    cost: 29,
    available: {
      if: {
        limit: {
          has_country_flag: "PIHC_COUNTRY_FLAG_NO_FOCUS"
        },
        custom_trigger_tooltip: {
          tooltip: "PIHC_COUNTRY_FLAG_NO_FOCUS_TOOLTIP",
          always: false
        }
      }
    }
  },
  null,
  4
)}\n`;

export const sourceBackedSmokeBrowserPayload: ProjectBrowserPayload = {
  schema: "paradev.sdk.project-browser.v1",
  project_id: "PIHC3",
  title: "The Pony In The High Castle",
  root: sourceBackedSmokeProjectRoot,
  profile: "hoi4",
  filters: {},
  families: [],
  diagnostics: [],
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
      root: `${sourceBackedSmokeProjectRoot}/src/modules/focus_tree/C08_PARTIV`,
      relative_root: "src/modules/focus_tree/C08_PARTIV",
      source_count: 1,
      sources: [],
      metadata: {
        settings: {
          source_focuses: [
            { focus_id: "FOCUS_C08_CANTERLOT_MIND", source_path: "C08_CANTERLOT_MIND", tree: "C08_PARTIV", parent: null, x: 9, y: 0 },
            { focus_id: "FOCUS_C08_PLAN_STARLIGHT", source_path: "C08_PLAN_STARLIGHT", tree: "C08_PARTIV", parent: "FOCUS_C08_TO_THE_WAR", priority: 0 },
            { focus_id: "FOCUS_C08_PLAN_SUNBURST", source_path: "C08_PLAN_SUNBURST", tree: "C08_PARTIV", parent: "FOCUS_C08_TO_THE_WAR", dx: 1, priority: -10 },
            { focus_id: "FOCUS_C08_PLAN_TWILIGHT", source_path: "C08_PLAN_TWILIGHT", tree: "C08_PARTIV", parent: "FOCUS_C08_TO_THE_WAR", dx: -1, priority: 10 },
            { focus_id: "FOCUS_C08_SECOND_SUMMIT", source_path: "C08_SECOND_SUMMIT", tree: "C08_PARTIV", parent: "FOCUS_C08_CANTERLOT_MIND", x: 9, y: 1, priority: 10 },
            { focus_id: "FOCUS_C08_THE_RISING_FIRE", source_path: "C08_THE_RISING_FIRE", tree: "C08_PARTIV", parent: null, x: 3, y: 5 },
            { focus_id: "FOCUS_C08_TO_THE_WAR", source_path: "C08_TO_THE_WAR", tree: "C08_PARTIV", parent: "FOCUS_C08_SECOND_SUMMIT", x: 9, y: 2, priority: 10 },
            { focus_id: "FOCUS_C08_T_CADENCE", source_path: "C08_T_CADENCE", tree: "C08_PARTIV", parent: "FOCUS_C08_THE_RISING_FIRE", priority: 10 },
            { focus_id: "FOCUS_C08_T_TRIXIE", source_path: "C08_T_TRIXIE", tree: "C08_PARTIV", parent: "FOCUS_C08_THE_RISING_FIRE", priority: 10 }
          ],
          focuses: [
            { id: "FOCUS_C08_CANTERLOT_MIND", icon: "GFX_FOCUS_C08_CANTERLOT_MIND_icon", x: "12", y: "0" },
            { id: "FOCUS_C08_SECOND_SUMMIT", icon: "GFX_FOCUS_C08_SECOND_SUMMIT_icon", x: "12", y: "1", prerequisites: ["FOCUS_C08_CANTERLOT_MIND"] },
            { id: "FOCUS_C08_TO_THE_WAR", icon: "GFX_FOCUS_C08_TO_THE_WAR_icon", x: "12", y: "2", prerequisites: ["FOCUS_C08_SECOND_SUMMIT"] },
            { id: "FOCUS_C08_THE_RISING_FIRE", icon: "GFX_FOCUS_C08_THE_RISING_FIRE_icon", x: "5", y: "5" },
            {
              id: "FOCUS_C08_PLAN_SUNBURST",
              icon: "GFX_FOCUS_C08_PLAN_SUNBURST_icon",
              x: "15",
              y: "3",
              prerequisites: ["FOCUS_C08_TO_THE_WAR"],
              mutually_exclusive: ["FOCUS_C08_PLAN_TWILIGHT", "FOCUS_C08_PLAN_STARLIGHT"]
            },
            {
              id: "FOCUS_C08_PLAN_STARLIGHT",
              icon: "GFX_FOCUS_C08_PLAN_STARLIGHT_icon",
              x: "12",
              y: "3",
              prerequisites: ["FOCUS_C08_TO_THE_WAR"],
              mutually_exclusive: ["FOCUS_C08_PLAN_TWILIGHT", "FOCUS_C08_PLAN_SUNBURST"]
            },
            { id: "FOCUS_C08_T_CADENCE", icon: "GFX_FOCUS_C08_T_CADENCE_icon", x: "4", y: "6", prerequisites: ["FOCUS_C08_THE_RISING_FIRE"] },
            { id: "FOCUS_C08_T_TRIXIE", icon: "GFX_FOCUS_C08_T_TRIXIE_icon", x: "6", y: "6", prerequisites: ["FOCUS_C08_THE_RISING_FIRE"] },
            {
              id: "FOCUS_C08_PLAN_TWILIGHT",
              icon: "GFX_FOCUS_C08_PLAN_TWILIGHT_icon",
              x: "9",
              y: "3",
              prerequisites: ["FOCUS_C08_TO_THE_WAR"],
              mutually_exclusive: ["FOCUS_C08_PLAN_STARLIGHT", "FOCUS_C08_PLAN_SUNBURST"]
            }
          ]
        }
      }
    }
  ]
};

export const sourceBackedSmokeDiagramDocument: DiagramDocument = buildProjectDiagramDocument(sourceBackedSmokeBrowserPayload, "focuses");

const c01MainSmokeSettings = parseFocusTreeYamlSettings(c01MainSmokeMetaYaml);

export const c01MainSmokeBrowserItem: ProjectBrowserItem = {
  id: "focus_tree:C01_MAIN",
  kind: "module",
  layout: "canonical",
  family_id: "focuses",
  family: "focus_tree",
  object_id: "C01_MAIN",
  module_id: "C01_MAIN",
  title: "C01 Main",
  root: `${sourceBackedSmokeProjectRoot}/src/modules/focus_tree/C01_MAIN`,
  relative_root: "src/modules/focus_tree/C01_MAIN",
  source_root: `${sourceBackedSmokeProjectRoot}/src`,
  source_root_relative_path: "src",
  source_count: c01MainSmokeSettings.source_focuses.length,
  sources: [
    {
      slot: "meta",
      name: "meta.yaml",
      path: `${sourceBackedSmokeProjectRoot}/src/modules/focus_tree/C01_MAIN/meta.yaml`,
      relative_path: "src/modules/focus_tree/C01_MAIN/meta.yaml",
      extension: "yaml"
    }
  ],
  metadata: {
    settings: c01MainSmokeSettings
  }
};

export const c01MainSmokeDiagramDocument: DiagramDocument = buildProjectDiagramDocument(
  {
    ...sourceBackedSmokeBrowserPayload,
    items: [c01MainSmokeBrowserItem]
  },
  "focuses"
);

export const sourceBackedSmokeSummary = {
  nodeCount: sourceBackedSmokeDiagramDocument.nodes.length,
  edgeCount: sourceBackedSmokeDiagramDocument.edges.length,
  previewNodeCount: sourceBackedSmokeDiagramDocument.nodes.filter((node) => isCanonicalFocusPreview(node.imageUrl)).length,
  legacyNodeCount: sourceBackedSmokeDiagramDocument.nodes.filter((node) => node.imageUrl?.includes("/legacy/focuses/") || node.imageUrl?.endsWith("/default.png")).length,
  explicitRootIds: sourceBackedSmokeDiagramDocument.nodes.filter((node) => !node.parentId).map((node) => node.id),
  treeEdgeIds: sourceBackedSmokeDiagramDocument.edges.filter((edge) => edge.kind === "tree").map((edge) => edge.id),
  dependencyEdgeIds: sourceBackedSmokeDiagramDocument.edges.filter((edge) => edge.kind === "dependency").map((edge) => edge.id)
} as const;

export const c01MainSmokeSummary = {
  nodeCount: c01MainSmokeDiagramDocument.nodes.length,
  edgeCount: c01MainSmokeDiagramDocument.edges.length,
  previewNodeCount: c01MainSmokeDiagramDocument.nodes.filter((node) => isCanonicalFocusPreview(node.imageUrl)).length,
  legacyNodeCount: c01MainSmokeDiagramDocument.nodes.filter((node) => node.imageUrl?.includes("/legacy/focuses/") || node.imageUrl?.endsWith("/default.png")).length
} as const;

function isCanonicalFocusPreview(imageUrl: string | undefined): boolean {
  return Boolean(imageUrl?.includes("/focus_tree/") && imageUrl.includes("/icons/") && imageUrl.endsWith(".png"));
}

type FocusTreeYamlSettings = {
  focuses: Record<string, unknown>[];
  source_focuses: Record<string, unknown>[];
};

function parseFocusTreeYamlSettings(yamlText: string): FocusTreeYamlSettings {
  return {
    source_focuses: parseYamlRecordList(yamlText, "source_focuses"),
    focuses: parseYamlRecordList(yamlText, "focuses")
  };
}

function parseYamlRecordList(yamlText: string, key: keyof FocusTreeYamlSettings): Record<string, unknown>[] {
  const records: Record<string, unknown>[] = [];
  const lines = yamlText.split(/\r?\n/);
  let inTargetList = false;
  let currentRecord: Record<string, unknown> | null = null;
  let activeListKey = "";

  for (const line of lines) {
    if (!inTargetList) {
      inTargetList = line === `    ${key}:`;
      continue;
    }
    if (/^    [^-\s][^:]*:/.test(line)) {
      break;
    }

    const recordStart = line.match(/^    -\s+(.*)$/);
    if (recordStart) {
      currentRecord = {};
      records.push(currentRecord);
      activeListKey = "";
      assignYamlField(currentRecord, recordStart[1]);
      continue;
    }
    if (!currentRecord) {
      continue;
    }

    const listValue = activeListKey ? line.match(/^        -\s*(.*)$/) : null;
    if (listValue) {
      const values = (currentRecord[activeListKey] as unknown[] | undefined) ?? [];
      values.push(parseYamlScalar(listValue[1]));
      currentRecord[activeListKey] = values;
      continue;
    }

    const field = line.match(/^        ([^:\s][^:]*):\s*(.*)$/);
    if (!field) {
      continue;
    }
    activeListKey = assignYamlField(currentRecord, `${field[1]}: ${field[2]}`);
  }

  return records;
}

function assignYamlField(record: Record<string, unknown>, fieldText: string): string {
  const field = fieldText.trim().match(/^([^:]+):\s*(.*)$/);
  if (!field) {
    return "";
  }
  const key = field[1].trim();
  const value = field[2].trim();
  if (!value) {
    record[key] = [];
    return key;
  }
  record[key] = parseYamlScalar(value);
  return "";
}

function parseYamlScalar(value: string): unknown {
  const cleanValue = value.trim();
  if (cleanValue === "null") {
    return null;
  }
  if (cleanValue === "true") {
    return true;
  }
  if (cleanValue === "false") {
    return false;
  }
  const unquotedValue = cleanValue.match(/^['"](.*)['"]$/)?.[1] ?? cleanValue;
  if (/^-?\d+(?:\.\d+)?$/.test(unquotedValue)) {
    return Number(unquotedValue);
  }
  return unquotedValue;
}
