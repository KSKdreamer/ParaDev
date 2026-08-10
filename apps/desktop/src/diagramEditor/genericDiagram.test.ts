import { describe, expect, it } from "vitest";
import type { ModuleDiagramPayload } from "../services/paradev";
import type { ProjectBrowserPayload } from "../types";
import {
  buildGenericDiagramDocument,
  changedGenericDiagramNodeIds,
  genericDiagramEditIntents,
  genericDiagramSourcePath,
} from "./genericDiagram";
import {
  sourceBackedDiagramAdapter,
  sourceBackedDiagramRendererIds,
} from "./sourceBackedDiagramAdapters";

describe("generic Registry diagram renderer", () => {
  it("renders and edits an external provider through the shared graph contract", () => {
    const base = buildGenericDiagramDocument(externalPayload(), browser(), "zh");

    expect(base.nodes).toMatchObject([
      {
        id: "NODE_A",
        mode: "absolute",
        title: "节点 A",
        x: 1,
        y: 2,
      },
      {
        dx: 0,
        dy: 1,
        id: "NODE_B",
        mode: "relative",
        parentId: "NODE_A",
        title: "节点 B",
      },
    ]);
    expect(base.edges).toMatchObject([
      {
        kind: "reference",
        relationshipKind: "all_parent",
        source: "NODE_A",
        target: "NODE_B",
      },
    ]);
    expect(genericDiagramSourcePath(base, "NODE_B")).toBe(
      "src/modules/demo/NODE_B/def.pdx",
    );

    const draft = {
      ...base,
      nodes: base.nodes.map((node) =>
        node.id === "NODE_B" ? { ...node, dy: 3 } : node,
      ),
      edges: [],
    };
    expect(genericDiagramEditIntents(base, draft)).toEqual({
      positionIntents: [
        {
          node_id: "NODE_B",
          source_revision: revision("b"),
          x: 0,
          y: 3,
        },
      ],
      edgeIntents: [
        {
          kind: "all_parent",
          present: false,
          source_id: "NODE_A",
          source_revision: revision("e"),
          target_id: "NODE_B",
        },
      ],
    });
    expect(changedGenericDiagramNodeIds(base, draft)).toEqual([
      "NODE_A",
      "NODE_B",
    ]);
  });

  it("registers bundled renderers and one reusable external graph protocol", () => {
    expect(sourceBackedDiagramRendererIds()).toEqual([
      "doctrine",
      "focus-tree",
      "graph",
      "mio-trait",
      "technology",
    ]);
    const adapter = sourceBackedDiagramAdapter("graph");
    expect(adapter).toBeDefined();
    expect(adapter?.buildDocument({
      browser: browser(),
      locale: "en",
      payload: externalPayload(),
    }).nodes).toHaveLength(2);
    expect(sourceBackedDiagramAdapter("project-specific-secret")).toBeUndefined();
  });

  it("rejects ambiguous nodes and moved nodes without reviewed revisions", () => {
    const payload = externalPayload();
    expect(() =>
      buildGenericDiagramDocument(
        { ...payload, nodes: [payload.nodes[0], payload.nodes[0]] },
        browser(),
        "en",
      ),
    ).toThrow("duplicate node id NODE_A");

    const base = buildGenericDiagramDocument(
      {
        ...payload,
        nodes: payload.nodes.map((node) =>
          node.id === "NODE_B" ? { ...node, source_revision: undefined } : node,
        ),
      },
      browser(),
      "en",
    );
    const draft = {
      ...base,
      nodes: base.nodes.map((node) =>
        node.id === "NODE_B" ? { ...node, dy: 4 } : node,
      ),
    };
    expect(() => genericDiagramEditIntents(base, draft)).toThrow(
      "NODE_B has no authoritative source revision",
    );

    expect(() =>
      buildGenericDiagramDocument(
        {
          ...payload,
          edges: [
            {
              id: "dangling",
              kind: "dependency",
              source: "NODE_A",
              target: "MISSING",
            },
          ],
        },
        browser(),
        "en",
      ),
    ).toThrow("references unknown target node MISSING");

    expect(() =>
      buildGenericDiagramDocument(
        { ...payload, edges: [payload.edges[0], payload.edges[0]] },
        browser(),
        "en",
      ),
    ).toThrow("duplicate edge all_parent:NODE_A->NODE_B");

    expect(() =>
      buildGenericDiagramDocument(
        {
          ...payload,
          nodes: payload.nodes.map((node) =>
            node.id === "NODE_A" ? { ...node, y: undefined } : node,
          ),
        },
        browser(),
        "en",
      ),
    ).toThrow("NODE_A requires both finite x and y coordinates");
  });
});

function externalPayload(): ModuleDiagramPayload {
  return {
    schema: "paradev.sdk.module_diagram.v1",
    provider_schema: "example.external.graph.v1",
    project_id: "PIHC3",
    project_root: "/workspace/projects/PIHC3",
    profile: "hoi4",
    family: "demo",
    source_kind: "project_extension",
    editable: true,
    nodes: [
      {
        id: "NODE_A",
        x: 1,
        y: 2,
        source_path: "src/modules/demo/NODE_A/def.pdx",
        source_revision: revision("a"),
        localized_titles: { en: "Node A", zh: "节点 A" },
      },
      {
        id: "NODE_B",
        module_id: "demo/NODE_B",
        position: { x: 0, y: 1 },
        relative_position_id: "NODE_A",
        source_path: "src/modules/demo/NODE_B/def.pdx",
        source_revision: revision("b"),
        localized_titles: { en: "Node B", zh: "节点 B" },
      },
    ],
    edges: [
      {
        id: "all_parent:NODE_A->NODE_B",
        kind: "all_parent",
        source: "NODE_A",
        target: "NODE_B",
        source_revision: revision("e"),
      },
    ],
    diagnostics: [],
    summary: { node_count: 2 },
  };
}

function browser(): ProjectBrowserPayload {
  const root = "/workspace/projects/PIHC3";
  return {
    schema: "paradev.sdk.project-browser.v1",
    project_id: "PIHC3",
    title: "PIHC3",
    root,
    profile: "hoi4",
    filters: {},
    families: [
      {
        id: "demo",
        family: "demo",
        title: "External graph",
        item_count: 2,
        source_count: 2,
        layouts: ["canonical"],
        diagram: {
          id: "external_graph",
          aliases: [],
          renderer: "graph",
          title: "External graph",
          editable: true,
        },
      },
    ],
    items: ["NODE_A", "NODE_B"].map((id) => ({
      id: `module:demo/${id}`,
      kind: "module" as const,
      layout: "canonical" as const,
      family_id: "demo",
      family: "demo",
      object_id: id,
      module_id: `demo/${id}`,
      title: id,
      root: `${root}/src/modules/demo/${id}`,
      relative_root: `src/modules/demo/${id}`,
      source_count: 1,
      sources: [],
    })),
    diagnostics: [],
  };
}

function revision(seed: string): string {
  return `sha256:${seed.repeat(64).slice(0, 64)}`;
}
