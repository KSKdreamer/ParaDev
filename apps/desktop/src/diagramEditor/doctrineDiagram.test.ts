import { describe, expect, it } from "vitest";
import type { ModuleDiagramPayload } from "../services/paradev";
import type { ProjectBrowserPayload } from "../types";
import {
  moveDiagramNode,
  setDiagramPathEdge,
  setDiagramReferenceEdge
} from "./layoutModel";
import {
  buildDoctrineDiagramDocument,
  changedDoctrineDiagramNodeIds,
  doctrineDiagramEditIntents,
  doctrineDiagramNodeEditable,
  doctrineDiagramSourcePath
} from "./doctrineDiagram";

const browser: ProjectBrowserPayload = {
  schema: "paradev.sdk.project-browser.v1",
  project_id: "PIHC3",
  title: "PIHC3",
  root: "/workspace/PIHC3",
  profile: "hoi4",
  filters: { family: "doctrine" },
  families: [],
  diagnostics: [],
  items: [
    {
      id: "module:doctrine/DOCTRINE_ALPHA",
      kind: "module",
      layout: "canonical",
      family_id: "doctrines",
      family: "doctrine",
      object_id: "DOCTRINE_ALPHA",
      module_id: "doctrine/DOCTRINE_ALPHA",
      title: "Alpha Doctrine",
      root: "/workspace/PIHC3/src/modules/doctrine/DOCTRINE_ALPHA",
      relative_root: "src/modules/doctrine/DOCTRINE_ALPHA",
      source_count: 3,
      source_root: "/workspace/PIHC3/src",
      sources: [
        {
          slot: "def",
          name: "def.txt",
          path: "/workspace/PIHC3/src/modules/doctrine/DOCTRINE_ALPHA/def.txt",
          relative_path:
            "src/modules/doctrine/DOCTRINE_ALPHA/def.txt",
          extension: "txt"
        },
        {
          slot: "icon",
          name: "icon.png",
          path: "/workspace/PIHC3/src/modules/doctrine/DOCTRINE_ALPHA/icon.png",
          relative_path:
            "src/modules/doctrine/DOCTRINE_ALPHA/icon.png",
          extension: "png"
        }
      ]
    },
    {
      id: "module:doctrine/DOCTRINE_BETA",
      kind: "module",
      layout: "canonical",
      family_id: "doctrines",
      family: "doctrine",
      object_id: "DOCTRINE_BETA",
      module_id: "doctrine/DOCTRINE_BETA",
      title: "Beta Doctrine",
      root: "/workspace/PIHC3/src/modules/doctrine/DOCTRINE_BETA",
      relative_root: "src/modules/doctrine/DOCTRINE_BETA",
      source_count: 2,
      source_root: "/workspace/PIHC3/src",
      sources: [
        {
          slot: "def",
          name: "def.txt",
          path: "/workspace/PIHC3/src/modules/doctrine/DOCTRINE_BETA/def.txt",
          relative_path:
            "src/modules/doctrine/DOCTRINE_BETA/def.txt",
          extension: "txt"
        }
      ]
    }
  ]
};

const payload: ModuleDiagramPayload = {
  schema: "paradev.sdk.module_diagram.v1",
  provider_schema:
    "paradev.hoi4.doctrine-diagram-projection.v1",
  project_id: "PIHC3",
  project_root: "/workspace/PIHC3",
  profile: "hoi4",
  family: "doctrine",
  source_kind:
    "module_doctrine_definition_and_hidden_diagram_state",
  editable: true,
  sources: [],
  diagnostics: [],
  summary: {
    source_count: 4,
    node_count: 2,
    edge_count: 2
  },
  nodes: [
    {
      id: "DOCTRINE_ALPHA",
      module_id: "doctrine/DOCTRINE_ALPHA",
      x: 1,
      y: 2,
      source_path:
        "src/modules/doctrine/DOCTRINE_ALPHA/def.txt",
      diagram_source_path:
        "src/modules/doctrine/DOCTRINE_ALPHA/.paradev/diagram.yaml",
      source_revision: "sha256:alpha-state",
      editable: true
    },
    {
      id: "DOCTRINE_BETA",
      module_id: "doctrine/DOCTRINE_BETA",
      x: 3,
      y: 4,
      source_path:
        "src/modules/doctrine/DOCTRINE_BETA/def.txt",
      diagram_source_path:
        "src/modules/doctrine/DOCTRINE_BETA/.paradev/diagram.yaml",
      source_revision: "sha256:beta-state",
      editable: true
    }
  ],
  edges: [
    {
      id: "path:DOCTRINE_ALPHA->DOCTRINE_BETA",
      kind: "path",
      source: "DOCTRINE_ALPHA",
      target: "DOCTRINE_BETA",
      owner_id: "DOCTRINE_ALPHA",
      source_path:
        "src/modules/doctrine/DOCTRINE_ALPHA/.paradev/diagram.yaml",
      source_revision: "sha256:alpha-state"
    },
    {
      id: "mutually_exclusive:DOCTRINE_ALPHA->DOCTRINE_BETA",
      kind: "mutually_exclusive",
      source: "DOCTRINE_ALPHA",
      target: "DOCTRINE_BETA",
      owner_ids: ["DOCTRINE_ALPHA", "DOCTRINE_BETA"],
      source_paths: [
        "src/modules/doctrine/DOCTRINE_ALPHA/.paradev/diagram.yaml",
        "src/modules/doctrine/DOCTRINE_BETA/.paradev/diagram.yaml"
      ]
    }
  ]
};

describe("source-backed doctrine diagram", () => {
  it("projects exact hidden layout, paths, mutual exclusions, titles, and icons", () => {
    const document = buildDoctrineDiagramDocument(
      payload,
      browser
    );

    expect(document.gridSizePx).toBe(48);
    expect(document.nodes[0]).toMatchObject({
      id: "DOCTRINE_ALPHA",
      mode: "absolute",
      x: 1,
      y: 2,
      imageUrl:
        "src/modules/doctrine/DOCTRINE_ALPHA/icon.png",
      title: "Alpha Doctrine",
      payload: {
        itemId: "module:doctrine/DOCTRINE_ALPHA",
        sourcePath:
          "src/modules/doctrine/DOCTRINE_ALPHA/def.txt",
        diagramSourcePath:
          "src/modules/doctrine/DOCTRINE_ALPHA/.paradev/diagram.yaml",
        sourceRevision: "sha256:alpha-state",
        editable: true
      }
    });
    expect(document.edges).toEqual([
      {
        id: "path:DOCTRINE_ALPHA->DOCTRINE_BETA",
        kind: "path",
        source: "DOCTRINE_ALPHA",
        target: "DOCTRINE_BETA"
      },
      {
        id: "reference:DOCTRINE_ALPHA->DOCTRINE_BETA",
        kind: "reference",
        source: "DOCTRINE_ALPHA",
        target: "DOCTRINE_BETA"
      }
    ]);
    expect(
      doctrineDiagramSourcePath(document, "DOCTRINE_ALPHA")
    ).toBe(
      "src/modules/doctrine/DOCTRINE_ALPHA/def.txt"
    );
    expect(
      doctrineDiagramNodeEditable(document, "DOCTRINE_ALPHA")
    ).toBe(true);
  });

  it("derives revision-guarded position, path, and mutual-exclusion intents", () => {
    const base = buildDoctrineDiagramDocument(payload, browser);
    let draft = moveDiagramNode(base, "DOCTRINE_BETA", {
      dx: 2,
      dy: -1
    });
    draft = setDiagramPathEdge(
      draft,
      "DOCTRINE_ALPHA",
      "DOCTRINE_BETA",
      false
    );
    draft = setDiagramPathEdge(
      draft,
      "DOCTRINE_BETA",
      "DOCTRINE_ALPHA",
      true
    );
    draft = setDiagramReferenceEdge(
      draft,
      "DOCTRINE_ALPHA",
      "DOCTRINE_BETA",
      false
    );

    expect(doctrineDiagramEditIntents(base, draft)).toEqual({
      positionIntents: [
        {
          doctrine_id: "DOCTRINE_BETA",
          x: 5,
          y: 3,
          source_revision: "sha256:beta-state"
        }
      ],
      edgeIntents: [
        {
          kind: "path",
          source_id: "DOCTRINE_ALPHA",
          target_id: "DOCTRINE_BETA",
          present: false,
          source_revision: "sha256:alpha-state"
        },
        {
          kind: "path",
          source_id: "DOCTRINE_BETA",
          target_id: "DOCTRINE_ALPHA",
          present: true,
          source_revision: "sha256:beta-state"
        },
        {
          kind: "mutually_exclusive",
          source_id: "DOCTRINE_ALPHA",
          target_id: "DOCTRINE_BETA",
          present: false,
          source_revision: "sha256:alpha-state"
        }
      ]
    });
    expect(
      changedDoctrineDiagramNodeIds(base, draft)
    ).toEqual(["DOCTRINE_ALPHA", "DOCTRINE_BETA"]);
  });

  it("fails closed when a changed node has no editable hidden state", () => {
    const missingStatePayload: ModuleDiagramPayload = {
      ...payload,
      nodes: payload.nodes.map((row) =>
        row.id === "DOCTRINE_BETA"
          ? {
              ...row,
              diagram_source_path: undefined,
              editable: false
            }
          : row
      )
    };
    const base = buildDoctrineDiagramDocument(
      missingStatePayload,
      browser
    );
    const draft = moveDiagramNode(base, "DOCTRINE_BETA", {
      dx: 1,
      dy: 0
    });

    expect(
      doctrineDiagramNodeEditable(base, "DOCTRINE_BETA")
    ).toBe(false);
    expect(() =>
      doctrineDiagramEditIntents(base, draft)
    ).toThrow("no editable hidden diagram state");
  });
});
