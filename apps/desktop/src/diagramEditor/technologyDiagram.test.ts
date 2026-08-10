import { describe, expect, it } from "vitest";
import type {
  ModuleDiagramPayload
} from "../services/paradev";
import type { ProjectBrowserPayload } from "../types";
import {
  moveDiagramNode,
  setDiagramDependencyEdge,
  setDiagramPathEdge
} from "./layoutModel";
import {
  buildTechnologyDiagramDocument,
  changedTechnologyDiagramNodeIds,
  technologyDiagramEditIntents
} from "./technologyDiagram";

const browser: ProjectBrowserPayload = {
  schema: "paradev.sdk.project-browser.v1",
  project_id: "PIHC3",
  title: "PIHC3",
  root: "/workspace/PIHC3",
  profile: "hoi4",
  filters: { family: "technology" },
  families: [],
  diagnostics: [],
  items: [
    {
      id: "module:technology/TECH_ALPHA",
      kind: "module",
      layout: "canonical",
      family_id: "technologies",
      family: "technology",
      object_id: "TECH_ALPHA",
      module_id: "technology/TECH_ALPHA",
      title: "Alpha",
      root: "/workspace/PIHC3/src/modules/technology/TECH_ALPHA",
      relative_root: "src/modules/technology/TECH_ALPHA",
      source_count: 2,
      source_root: "/workspace/PIHC3/src",
      sources: [
        {
          slot: "def",
          name: "def.txt",
          path: "/workspace/PIHC3/src/modules/technology/TECH_ALPHA/def.txt",
          relative_path: "src/modules/technology/TECH_ALPHA/def.txt",
          extension: "txt"
        },
        {
          slot: "preview",
          name: "icon.png",
          path: "/workspace/PIHC3/src/modules/technology/TECH_ALPHA/icon.png",
          relative_path: "src/modules/technology/TECH_ALPHA/icon.png",
          extension: "png"
        }
      ]
    },
    {
      id: "module:technology/TECH_BETA",
      kind: "module",
      layout: "canonical",
      family_id: "technologies",
      family: "technology",
      object_id: "TECH_BETA",
      module_id: "technology/TECH_BETA",
      title: "Beta",
      root: "/workspace/PIHC3/src/modules/technology/TECH_BETA",
      relative_root: "src/modules/technology/TECH_BETA",
      source_count: 1,
      source_root: "/workspace/PIHC3/src",
      sources: [
        {
          slot: "def",
          name: "def.txt",
          path: "/workspace/PIHC3/src/modules/technology/TECH_BETA/def.txt",
          relative_path: "src/modules/technology/TECH_BETA/def.txt",
          extension: "txt"
        }
      ]
    }
  ]
};

const payload: ModuleDiagramPayload = {
  schema: "paradev.sdk.module_diagram.v1",
  provider_schema:
    "paradev.hoi4.technology-diagram-projection.v1",
  project_id: "PIHC3",
  project_root: "/workspace/PIHC3",
  profile: "hoi4",
  family: "technology",
  source_kind: "module_def_pdx",
  editable: true,
  sources: [],
  diagnostics: [],
  summary: {
    source_count: 2,
    node_count: 2,
    edge_count: 2
  },
  nodes: [
    {
      id: "TECH_ALPHA",
      folder: "infantry_folder",
      x: 1,
      y: 2,
      source_path:
        "src/modules/technology/TECH_ALPHA/def.txt",
      source_revision: "sha256:alpha",
      editable: true
    },
    {
      id: "TECH_BETA",
      folder: "infantry_folder",
      x: 3,
      y: 4,
      source_path:
        "src/modules/technology/TECH_BETA/def.txt",
      source_revision: "sha256:beta",
      editable: true
    }
  ],
  edges: [
    {
      id: "dependency:TECH_ALPHA->TECH_BETA",
      kind: "dependency",
      source: "TECH_ALPHA",
      target: "TECH_BETA",
      owner_id: "TECH_BETA",
      source_path:
        "src/modules/technology/TECH_BETA/def.txt",
      source_revision: "sha256:beta"
    },
    {
      id: "path:TECH_ALPHA->TECH_BETA",
      kind: "path",
      source: "TECH_ALPHA",
      target: "TECH_BETA",
      owner_id: "TECH_ALPHA",
      source_path:
        "src/modules/technology/TECH_ALPHA/def.txt",
      source_revision: "sha256:alpha"
    }
  ]
};

describe("source-backed technology diagram", () => {
  it("projects authoritative positions, distinct edge kinds, and exact source payloads", () => {
    const document = buildTechnologyDiagramDocument(
      payload,
      browser
    );

    expect(document.gridSizePx).toBe(48);
    expect(document.nodes[0]).toMatchObject({
      id: "TECH_ALPHA",
      mode: "absolute",
      x: 1,
      y: 2,
      imageUrl:
        "src/modules/technology/TECH_ALPHA/icon.png",
      title: "Alpha",
      payload: {
        itemId: "module:technology/TECH_ALPHA",
        sourcePath:
          "src/modules/technology/TECH_ALPHA/def.txt",
        sourceRevision: "sha256:alpha"
      }
    });
    expect(document.edges).toEqual([
      {
        id: "dependency:TECH_ALPHA->TECH_BETA",
        kind: "dependency",
        source: "TECH_ALPHA",
        target: "TECH_BETA"
      },
      {
        id: "path:TECH_ALPHA->TECH_BETA",
        kind: "path",
        source: "TECH_ALPHA",
        target: "TECH_BETA"
      }
    ]);
  });

  it("derives reviewed source revisions for position and edge intents", () => {
    const base = buildTechnologyDiagramDocument(payload, browser);
    let draft = moveDiagramNode(base, "TECH_BETA", {
      dx: 2,
      dy: -1
    });
    draft = setDiagramDependencyEdge(
      draft,
      "TECH_ALPHA",
      "TECH_BETA",
      false
    );
    draft = setDiagramPathEdge(
      draft,
      "TECH_BETA",
      "TECH_ALPHA",
      true
    );

    expect(technologyDiagramEditIntents(base, draft)).toEqual({
      positionIntents: [
        {
          technology_id: "TECH_BETA",
          x: 5,
          y: 3,
          source_revision: "sha256:beta"
        }
      ],
      edgeIntents: [
        {
          kind: "dependency",
          source_id: "TECH_ALPHA",
          target_id: "TECH_BETA",
          present: false,
          source_revision: "sha256:beta"
        },
        {
          kind: "path",
          source_id: "TECH_BETA",
          target_id: "TECH_ALPHA",
          present: true,
          source_revision: "sha256:beta"
        }
      ]
    });
    expect(
      changedTechnologyDiagramNodeIds(base, draft)
    ).toEqual(["TECH_BETA"]);
  });
});
