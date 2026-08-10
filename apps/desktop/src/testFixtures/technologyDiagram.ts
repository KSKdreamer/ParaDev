import type { ModuleDiagramPayload } from "../services/paradev";
import type {
  ProjectBrowserItem,
  ProjectBrowserPayload
} from "../types";
import { smokeProjectRoot } from "./smokeImages";

export const technologyDiagramSmokeProjectRoot =
  smokeProjectRoot;

const technologies = [
  {
    id: "TECHNOLOGY_POWDER_EXPLOSIVE",
    title: "Powder Explosive",
    x: 2,
    y: 3,
    revision:
      "sha256:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
  },
  {
    id: "TECHNOLOGY_FIREARM_I",
    title: "Early Firearm I",
    x: 4,
    y: 3,
    revision:
      "sha256:bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"
  },
  {
    id: "TECHNOLOGY_LANDMINE",
    title: "Landmine",
    x: 6,
    y: 3,
    revision:
      "sha256:cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc"
  }
] as const;

export const technologyDiagramSmokeBrowserPayload: ProjectBrowserPayload =
  {
    schema: "paradev.sdk.project-browser.v1",
    project_id: "PIHC3",
    title: "The Pony In The High Castle",
    root: technologyDiagramSmokeProjectRoot,
    profile: "hoi4",
    filters: { family: "technology" },
    families: [],
    diagnostics: [],
    items: technologies.map(technologyBrowserItem)
  };

export const technologyDiagramApplySmokePayload: ModuleDiagramPayload =
  {
    schema: "paradev.sdk.module_diagram.v1",
    provider_schema:
      "paradev.hoi4.technology-diagram-projection.v1",
    project_id: "PIHC3",
    project_root: technologyDiagramSmokeProjectRoot,
    profile: "hoi4",
    family: "technology",
    source_kind: "module_def_pdx",
    editable: true,
    sources: technologies.map((technology) => ({
      path: technologySourcePath(technology.id),
      source_revision: technology.revision,
      sha256: technology.revision.slice("sha256:".length),
      size: 256
    })),
    diagnostics: [],
    summary: {
      source_count: technologies.length,
      node_count: technologies.length,
      edge_count: 2
    },
    nodes: technologies.map((technology) => ({
      id: technology.id,
      folder: "infantry_folder",
      x: technology.x,
      y: technology.y,
      source_path: technologySourcePath(technology.id),
      source_revision: technology.revision,
      editable: true
    })),
    edges: [
      {
        id: "dependency:TECHNOLOGY_POWDER_EXPLOSIVE->TECHNOLOGY_FIREARM_I",
        kind: "dependency",
        source: "TECHNOLOGY_POWDER_EXPLOSIVE",
        target: "TECHNOLOGY_FIREARM_I",
        owner_id: "TECHNOLOGY_FIREARM_I",
        source_path:
          technologySourcePath("TECHNOLOGY_FIREARM_I"),
        source_revision: technologies[1].revision
      },
      {
        id: "path:TECHNOLOGY_POWDER_EXPLOSIVE->TECHNOLOGY_FIREARM_I",
        kind: "path",
        source: "TECHNOLOGY_POWDER_EXPLOSIVE",
        target: "TECHNOLOGY_FIREARM_I",
        owner_id: "TECHNOLOGY_POWDER_EXPLOSIVE",
        source_path:
          technologySourcePath(
            "TECHNOLOGY_POWDER_EXPLOSIVE"
          ),
        source_revision: technologies[0].revision
      }
    ]
  };

export const technologyDiagramCanvasSmokePayload: ModuleDiagramPayload =
  {
    ...technologyDiagramApplySmokePayload,
    sources: (technologyDiagramApplySmokePayload.sources ?? []).slice(
      0,
      2
    ),
    nodes: technologyDiagramApplySmokePayload.nodes.slice(0, 2),
    summary: {
      source_count: 2,
      node_count: 2,
      edge_count: 2
    }
  };

function technologyBrowserItem(
  technology: (typeof technologies)[number]
): ProjectBrowserItem {
  const relativeRoot = technologyModuleRoot(technology.id);
  const root = `${technologyDiagramSmokeProjectRoot}/${relativeRoot}`;
  return {
    id: `module:technology/${technology.id}`,
    kind: "module",
    layout: "canonical",
    family_id: "technologies",
    family: "technology",
    object_id: technology.id,
    module_id: `technology/${technology.id}`,
    title: technology.title,
    root,
    relative_root: relativeRoot,
    source_root: `${technologyDiagramSmokeProjectRoot}/src`,
    source_root_relative_path: "src",
    source_count: 2,
    sources: [
      {
        slot: "def",
        name: "def.txt",
        path: `${root}/def.txt`,
        relative_path: `${relativeRoot}/def.txt`,
        extension: "txt"
      },
      {
        slot: "preview",
        name: "icon.png",
        path: `${root}/icon.png`,
        relative_path: `${relativeRoot}/icon.png`,
        extension: "png"
      }
    ]
  };
}

function technologyModuleRoot(technologyId: string): string {
  return `src/modules/technology/${technologyId}`;
}

function technologySourcePath(technologyId: string): string {
  return `${technologyModuleRoot(technologyId)}/def.txt`;
}
