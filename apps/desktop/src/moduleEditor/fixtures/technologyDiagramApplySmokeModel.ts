import { moveDiagramNode, setDiagramDependencyEdge } from "../../diagramEditor/layoutModel";
import type { DiagramDocument } from "../../diagramEditor/layoutModel";
import { buildProjectDiagramDocument } from "../../diagramEditor/projectDiagram";
import type { ProjectBrowserPayload } from "../../types";
import { buildDiagramMetadataTextDrafts } from "../diagramMetadata";
import { buildModuleEntities } from "../model";
import { buildDiagramApplyDraftPlan, buildDiagramChangedEntities } from "../ModuleEditor";
import { smokeProjectRoot } from "../../testFixtures/smokeImages";

export const technologyApplySmokeProjectRoot = smokeProjectRoot;

export const technologyApplySmokeBrowserPayload: ProjectBrowserPayload = {
  schema: "paradev.sdk.project-browser.v1",
  project_id: "PIHC3",
  title: "The Pony In The High Castle",
  root: technologyApplySmokeProjectRoot,
  profile: "hoi4",
  filters: {},
  families: [],
  diagnostics: [],
  items: [
    {
      id: "technology:TECHNOLOGY_POWDER_EXPLOSIVE",
      kind: "module",
      layout: "canonical",
      family_id: "technologies",
      family: "technology",
      object_id: "TECHNOLOGY_POWDER_EXPLOSIVE",
      module_id: "TECHNOLOGY_POWDER_EXPLOSIVE",
      title: "Powder Explosive",
      root: `${technologyApplySmokeProjectRoot}/src/modules/technology/TECHNOLOGY_POWDER_EXPLOSIVE`,
      relative_root: "src/modules/technology/TECHNOLOGY_POWDER_EXPLOSIVE",
      source_count: 1,
      sources: [
        {
          slot: "meta",
          name: "meta.yaml",
          path: `${technologyApplySmokeProjectRoot}/src/modules/technology/TECHNOLOGY_POWDER_EXPLOSIVE/meta.yaml`,
          relative_path: "src/modules/technology/TECHNOLOGY_POWDER_EXPLOSIVE/meta.yaml",
          extension: "yaml"
        }
      ],
      metadata: {
        settings: {
          folder_position: { x: 2, y: 3 },
          legacy_source_image: { path: "legacy/default.png" },
          path_target_ids: ["TECHNOLOGY_FIREARM_I"]
        }
      }
    },
    {
      id: "technology:TECHNOLOGY_FIREARM_I",
      kind: "module",
      layout: "canonical",
      family_id: "technologies",
      family: "technology",
      object_id: "TECHNOLOGY_FIREARM_I",
      module_id: "TECHNOLOGY_FIREARM_I",
      title: "Early Firearm I",
      root: `${technologyApplySmokeProjectRoot}/src/modules/technology/TECHNOLOGY_FIREARM_I`,
      relative_root: "src/modules/technology/TECHNOLOGY_FIREARM_I",
      source_count: 1,
      sources: [
        {
          slot: "meta",
          name: "meta.yaml",
          path: `${technologyApplySmokeProjectRoot}/src/modules/technology/TECHNOLOGY_FIREARM_I/meta.yaml`,
          relative_path: "src/modules/technology/TECHNOLOGY_FIREARM_I/meta.yaml",
          extension: "yaml"
        }
      ],
      metadata: {
        settings: {
          folder: { position: { x: 4, y: 3 } },
          legacy_source_image: { path: "legacy/default.png" },
          dependency_ids: ["TECHNOLOGY_POWDER_EXPLOSIVE"]
        }
      }
    },
    {
      id: "technology:TECHNOLOGY_LANDMINE",
      kind: "module",
      layout: "canonical",
      family_id: "technologies",
      family: "technology",
      object_id: "TECHNOLOGY_LANDMINE",
      module_id: "TECHNOLOGY_LANDMINE",
      title: "Landmine",
      root: `${technologyApplySmokeProjectRoot}/src/modules/technology/TECHNOLOGY_LANDMINE`,
      relative_root: "src/modules/technology/TECHNOLOGY_LANDMINE",
      source_count: 1,
      sources: [
        {
          slot: "meta",
          name: "meta.yaml",
          path: `${technologyApplySmokeProjectRoot}/src/modules/technology/TECHNOLOGY_LANDMINE/meta.yaml`,
          relative_path: "src/modules/technology/TECHNOLOGY_LANDMINE/meta.yaml",
          extension: "yaml"
        }
      ],
      metadata: {
        settings: {
          folder_position: { x: 6, y: 3 },
          legacy_source_image: { path: "legacy/default.png" },
          dependency_ids: [],
          path_target_ids: []
        }
      }
    }
  ]
};

export const technologyApplySmokeMetadataTextByEntityId: Record<string, string> = {
  "technology:TECHNOLOGY_POWDER_EXPLOSIVE": [
    "type: technology",
    "settings:",
    "    folder_position:",
    "        x: 2",
    "        y: 3",
    "    legacy_source_image:",
    "        path: legacy/default.png",
    "    path_target_ids:",
    "    - TECHNOLOGY_FIREARM_I",
    ""
  ].join("\n"),
  "technology:TECHNOLOGY_FIREARM_I": [
    "type: technology",
    "settings:",
    "    folder:",
    "        position:",
    "            x: 4",
    "            y: 3",
    "    legacy_source_image:",
    "        path: legacy/default.png",
    "    dependency_ids:",
    "    - TECHNOLOGY_POWDER_EXPLOSIVE",
    ""
  ].join("\n"),
  "technology:TECHNOLOGY_LANDMINE": [
    "type: technology",
    "settings:",
    "    folder_position:",
    "        x: 6",
    "        y: 3",
    "    legacy_source_image:",
    "        path: legacy/default.png",
    "    dependency_ids: []",
    "    path_target_ids: []",
    ""
  ].join("\n")
};

export const technologyApplySmokeBaseDocument: DiagramDocument = buildProjectDiagramDocument(
  technologyApplySmokeBrowserPayload,
  "technologies"
);
export const technologyApplySmokeEntities = buildModuleEntities(technologyApplySmokeBrowserPayload, "technologies", "en");

export const technologyApplySmokeMovedFirearmDocument: DiagramDocument = moveDiagramNode(
  technologyApplySmokeBaseDocument,
  "TECHNOLOGY_FIREARM_I",
  { dx: 1, dy: -1 }
);

export const technologyApplySmokeAddedLandmineDependencyDocument: DiagramDocument = setDiagramDependencyEdge(
  technologyApplySmokeBaseDocument,
  "TECHNOLOGY_POWDER_EXPLOSIVE",
  "TECHNOLOGY_LANDMINE",
  true
);

export function buildTechnologyApplySmokeDraftPlan(draftDocument: DiagramDocument) {
  const rows = buildDiagramChangedEntities(technologyApplySmokeBaseDocument, draftDocument, technologyApplySmokeEntities);
  const drafts = buildDiagramMetadataTextDrafts({
    baseDocument: technologyApplySmokeBaseDocument,
    draftDocument,
    entities: technologyApplySmokeEntities,
    metadataTextByEntityId: technologyApplySmokeMetadataTextByEntityId
  });
  return buildDiagramApplyDraftPlan(rows, drafts, technologyApplySmokeEntities);
}

export function technologyApplySmokeDraftText(draftDocument: DiagramDocument): string {
  const plan = buildTechnologyApplySmokeDraftPlan(draftDocument);
  return plan.ok ? plan.sourceEdits.map((edit) => edit.text).join("\n---\n") : "";
}
