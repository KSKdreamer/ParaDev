import { describe, expect, it } from "vitest";
import type { ModuleDiagramPayload } from "../services/paradev";
import type { ProjectBrowserPayload } from "../types";
import {
  moveDiagramNode,
  setDiagramDependencyEdge,
  setDiagramReferenceEdge
} from "./layoutModel";
import {
  buildFocusTreeDiagramDocument,
  changedFocusTreeDiagramNodeIds,
  focusTreeDiagramEditIntents,
  focusTreeDiagramSourcePath,
} from "./focusTreeDiagram";

const alphaSource =
  "src/modules/focus_tree/ALPHA_TREE/def.txt";
const betaSource =
  "src/modules/focus_tree/BETA_TREE/def.txt";

const browser: ProjectBrowserPayload = {
  schema: "paradev.sdk.project-browser.v1",
  project_id: "PIHC3",
  title: "PIHC3",
  root: "/workspace/PIHC3",
  profile: "hoi4",
  filters: { family: "focus_tree" },
  families: [],
  diagnostics: [],
  items: [
    {
      id: "module:focus_tree/ALPHA_TREE",
      kind: "module",
      layout: "canonical",
      family_id: "focuses",
      family: "focus_tree",
      object_id: "ALPHA_TREE",
      module_id: "focus_tree/ALPHA_TREE",
      title: "Alpha tree",
      root:
        "/workspace/PIHC3/src/modules/focus_tree/ALPHA_TREE",
      relative_root:
        "src/modules/focus_tree/ALPHA_TREE",
      source_root: "/workspace/PIHC3/src",
      source_count: 1,
      sources: [],
      metadata: {
        settings: {
          focuses: [
            {
              id: "LEGACY_METADATA_ONLY",
              x: 99,
              y: 99
            }
          ]
        }
      }
    }
  ]
};

const payload: ModuleDiagramPayload = {
  schema: "paradev.sdk.module_diagram.v1",
  provider_schema:
    "paradev.hoi4.focus-tree-diagram-projection.v1",
  project_id: "PIHC3",
  project_root: "/workspace/PIHC3",
  profile: "hoi4",
  family: "focus_tree",
  source_kind: "module_def_pdx",
  editable: true,
  sources: [],
  trees: [
    {
      id: "BETA_TREE",
      source_path: betaSource,
      source_revision: "sha256:beta",
      node_count: 1,
      edge_count: 0,
      editable: true
    },
    {
      id: "ALPHA_TREE",
      source_path: alphaSource,
      source_revision: "sha256:alpha",
      node_count: 3,
      edge_count: 2,
      editable: true
    }
  ],
  nodes: [
    {
      id: "FOCUS_BETA",
      tree_id: "BETA_TREE",
      x: 7,
      y: 8,
      source_path: betaSource,
      source_revision: "sha256:beta",
      editable: true
    },
    {
      id: "FOCUS_CHILD",
      tree_id: "ALPHA_TREE",
      x: 2,
      y: 1,
      relative_position_id: "FOCUS_ROOT",
      icon: "GFX_FOCUS_CHILD_icon",
      name_key: "FOCUS_CHILD",
      localized_titles: {
        l_english: "A Better Tomorrow",
        l_simp_chinese: "更好的明天"
      },
      source_path: alphaSource,
      source_revision: "sha256:alpha",
      editable: true
    },
    {
      id: "FOCUS_OTHER",
      tree_id: "ALPHA_TREE",
      x: 4,
      y: 1,
      source_path: alphaSource,
      source_revision: "sha256:alpha",
      editable: true
    },
    {
      id: "FOCUS_ROOT",
      tree_id: "ALPHA_TREE",
      x: 10,
      y: 0,
      source_path: alphaSource,
      source_revision: "sha256:alpha",
      editable: true
    }
  ],
  edges: [
    {
      id: "mutually_exclusive:FOCUS_CHILD->FOCUS_OTHER",
      kind: "mutually_exclusive",
      source: "FOCUS_CHILD",
      target: "FOCUS_OTHER",
      tree_id: "ALPHA_TREE",
      owner_ids: ["FOCUS_CHILD", "FOCUS_OTHER"],
      source_paths: [alphaSource],
      source_path: alphaSource,
      source_revision: "sha256:mutex-review",
      declaration_count: 2,
      editable: true
    },
    {
      id: "prerequisite:FOCUS_ROOT->FOCUS_CHILD",
      kind: "prerequisite",
      source: "FOCUS_ROOT",
      target: "FOCUS_CHILD",
      tree_id: "ALPHA_TREE",
      owner_ids: ["FOCUS_CHILD"],
      source_paths: [alphaSource],
      source_path: alphaSource,
      source_revision: "sha256:alpha",
      declaration_count: 1,
      editable: true
    }
  ],
  diagnostics: [],
  summary: {
    source_count: 2,
    tree_count: 2,
    node_count: 4,
    edge_count: 2
  }
};

describe("source-backed Focus tree diagram", () => {
  it("projects one selected def.txt tree without reading generated metadata", () => {
    const document = buildFocusTreeDiagramDocument(
      payload,
      browser
    );

    expect(document.gridSizePx).toBe(96);
    expect(document.layoutOptions).toEqual({ layerGap: 0 });
    expect(document.nodes.map((node) => node.id)).toEqual([
      "FOCUS_CHILD",
      "FOCUS_OTHER",
      "FOCUS_ROOT"
    ]);
    expect(document.nodes).not.toContainEqual(
      expect.objectContaining({ id: "LEGACY_METADATA_ONLY" })
    );
    expect(
      document.nodes.find((node) => node.id === "FOCUS_CHILD")
    ).toMatchObject({
      mode: "relative",
      parentId: "FOCUS_ROOT",
      dx: 2,
      dy: 1,
      relativePositionKind: "relative_position_id",
      title: "A Better Tomorrow",
      payload: {
        embeddedId: "FOCUS_CHILD",
        icon: "GFX_FOCUS_CHILD_icon",
        itemId: "module:focus_tree/ALPHA_TREE",
        sourcePath: alphaSource,
        sourceRevision: "sha256:alpha",
        treeId: "ALPHA_TREE"
      }
    });
    expect(document.edges).toEqual([
      {
        id: "dependency:FOCUS_ROOT->FOCUS_CHILD",
        kind: "dependency",
        source: "FOCUS_ROOT",
        target: "FOCUS_CHILD"
      },
      {
        id: "tree:FOCUS_ROOT->FOCUS_CHILD",
        kind: "tree",
        source: "FOCUS_ROOT",
        target: "FOCUS_CHILD"
      },
      {
        id: "reference:FOCUS_CHILD->FOCUS_OTHER",
        kind: "reference",
        source: "FOCUS_CHILD",
        target: "FOCUS_OTHER"
      }
    ]);
    expect(
      buildFocusTreeDiagramDocument(payload, browser, "zh")
        .nodes.find((node) => node.id === "FOCUS_CHILD")
        ?.title
    ).toBe("更好的明天");
  });

  it("derives guarded position, prerequisite, and mutex intents", () => {
    const base = buildFocusTreeDiagramDocument(payload, browser);
    let draft = moveDiagramNode(base, "FOCUS_CHILD", {
      dx: 2,
      dy: -1
    });
    draft = setDiagramDependencyEdge(
      draft,
      "FOCUS_ROOT",
      "FOCUS_CHILD",
      false
    );
    draft = setDiagramDependencyEdge(
      draft,
      "FOCUS_CHILD",
      "FOCUS_OTHER",
      true
    );
    draft = setDiagramReferenceEdge(
      draft,
      "FOCUS_CHILD",
      "FOCUS_OTHER",
      false
    );
    draft = setDiagramReferenceEdge(
      draft,
      "FOCUS_ROOT",
      "FOCUS_OTHER",
      true
    );

    expect(
      focusTreeDiagramEditIntents(payload, base, draft)
    ).toEqual({
      positionIntents: [
        {
          focus_id: "FOCUS_CHILD",
          x: 4,
          y: 0,
          source_revision: "sha256:alpha"
        }
      ],
      edgeIntents: [
        {
          kind: "prerequisite",
          source_id: "FOCUS_CHILD",
          target_id: "FOCUS_OTHER",
          present: true,
          source_revision: "sha256:alpha"
        },
        {
          kind: "prerequisite",
          source_id: "FOCUS_ROOT",
          target_id: "FOCUS_CHILD",
          present: false,
          source_revision: "sha256:alpha"
        },
        {
          kind: "mutually_exclusive",
          source_id: "FOCUS_CHILD",
          target_id: "FOCUS_OTHER",
          present: false,
          source_revision: "sha256:mutex-review"
        },
        {
          kind: "mutually_exclusive",
          source_id: "FOCUS_OTHER",
          target_id: "FOCUS_ROOT",
          present: true,
          source_revision: "sha256:alpha"
        }
      ]
    });
    expect(
      changedFocusTreeDiagramNodeIds(payload, base, draft)
    ).toEqual([
      "FOCUS_CHILD",
      "FOCUS_OTHER",
      "FOCUS_ROOT"
    ]);
    expect(
      focusTreeDiagramSourcePath(base, "FOCUS_CHILD")
    ).toBe(alphaSource);
  });

  it("projects modular focus collections through their child module sources", () => {
    const modularBrowser: ProjectBrowserPayload = {
      ...browser,
      items: [
        {
          ...browser.items[0],
          id: "collection:focus/ALPHA_TREE",
          kind: "collection",
          family: "focus",
          object_id: "ALPHA_TREE",
          module_id: undefined,
          collection_id: "ALPHA_TREE",
          relative_root: "src/collections/focus/ALPHA_TREE",
          root: "/workspace/PIHC3/src/collections/focus/ALPHA_TREE"
        },
        ...["FOCUS_CHILD", "FOCUS_OTHER", "FOCUS_ROOT"].map((id) => ({
          ...browser.items[0],
          id: `module:focus/${id}`,
          kind: "module" as const,
          family: "focus",
          object_id: id,
          module_id: `focus/${id}`,
          collection_id: "ALPHA_TREE",
          relative_root: `src/modules/focus/${id}`,
          root: `/workspace/PIHC3/src/modules/focus/${id}`
        }))
      ]
    };
    const modularPayload: ModuleDiagramPayload = {
      ...payload,
      source_kind: "focus_collection_modules",
      trees: payload.trees?.filter((tree) => tree.id === "ALPHA_TREE"),
      nodes: payload.nodes
        .filter((node) => node.tree_id === "ALPHA_TREE")
        .map((node) => ({ ...node, module_id: `focus/${node.id}` }))
    };

    const document = buildFocusTreeDiagramDocument(
      modularPayload,
      modularBrowser
    );

    expect(document.nodes).toHaveLength(3);
    expect(
      document.nodes.find((node) => node.id === "FOCUS_CHILD")
    ).toMatchObject({
      payload: {
        itemId: "module:focus/FOCUS_CHILD",
        moduleId: "focus/FOCUS_CHILD",
        objectId: "FOCUS_CHILD",
        relativeRoot: "src/modules/focus/FOCUS_CHILD",
        treeId: "ALPHA_TREE"
      }
    });
  });

  it("fails closed for structural edits and cross-source mutex additions", () => {
    const base = buildFocusTreeDiagramDocument(payload, browser);
    const reparented = {
      ...base,
      nodes: base.nodes.map((node) =>
        node.id === "FOCUS_CHILD"
          ? {
              ...node,
              mode: "absolute" as const,
              parentId: undefined,
              x: 12,
              y: 1
            }
          : node
      )
    };
    expect(() =>
      focusTreeDiagramEditIntents(payload, base, reparented)
    ).toThrow(/relative_position_id/);

    const allTreesBrowser = {
      ...browser,
      items: [
        ...browser.items,
        {
          ...browser.items[0],
          id: "module:focus_tree/BETA_TREE",
          object_id: "BETA_TREE",
          module_id: "focus_tree/BETA_TREE",
          relative_root:
            "src/modules/focus_tree/BETA_TREE",
          root:
            "/workspace/PIHC3/src/modules/focus_tree/BETA_TREE"
        }
      ]
    };
    const allTrees = buildFocusTreeDiagramDocument(
      payload,
      allTreesBrowser
    );
    const crossSource = {
      ...allTrees,
      edges: [
        ...allTrees.edges,
        {
          id: "reference:FOCUS_BETA->FOCUS_ROOT",
          kind: "reference" as const,
          source: "FOCUS_BETA",
          target: "FOCUS_ROOT"
        }
      ]
    };
    expect(() =>
      focusTreeDiagramEditIntents(
        payload,
        allTrees,
        crossSource
      )
    ).toThrow(/one reviewed Focus tree source file/);
  });

  it("rejects non-authoritative payloads and unmatched scopes", () => {
    expect(() =>
      buildFocusTreeDiagramDocument(
        { ...payload, provider_schema: "legacy.metadata.v1" },
        browser
      )
    ).toThrow(/authoritative module def\.txt provider/);
    expect(() =>
      buildFocusTreeDiagramDocument(payload, {
        ...browser,
        items: browser.items.map((item) => ({
          ...item,
          id: "module:focus_tree/UNKNOWN",
          object_id: "UNKNOWN",
          module_id: "focus_tree/UNKNOWN",
          relative_root:
            "src/modules/focus_tree/UNKNOWN"
        }))
      })
    ).toThrow(/does not match the authoritative def\.txt projection/);
  });
});
