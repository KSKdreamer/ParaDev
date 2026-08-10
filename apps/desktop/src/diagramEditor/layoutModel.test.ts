import { describe, expect, it } from "vitest";
import * as layoutModel from "./layoutModel";
import { autoLayoutDiagramDescendants, autoLayoutDiagramDocument, autoLayoutDiagramNode, autoLayoutDiagramSubtree, dragDeltaToGrid, insertDiagramChildNode, insertDiagramRootNode, makeDiagramSelectedNodeRelative, makeDiagramSubtreeRelative, moveDiagramNode, moveDiagramNodeKeepingDescendants, moveDiagramNodeRelayoutDescendants, moveDiagramSubtree, pinDiagramDocument, pinDiagramNode, pinDiagramSelectedNode, pinDiagramSubtree, removeDiagramSubtree, reorderDiagramSibling, resolveDiagramLayout, setDiagramNodeLayoutHints, setDiagramNodePosition, setDiagramViewport, toCanvasPoint, unpinDiagramDocument, unpinDiagramSelectedNode, unpinDiagramSubtree } from "./layoutModel";
import type { DiagramDocument } from "./layoutModel";

type DiagramDependencyEdgeSetter = (document: DiagramDocument, sourceId: string, targetId: string, enabled: boolean) => DiagramDocument;
type DiagramNodeOnlyRemover = (document: DiagramDocument, nodeId: string) => DiagramDocument;
type DiagramReferenceEdgeSetter = (document: DiagramDocument, sourceId: string, targetId: string, enabled: boolean) => DiagramDocument;
type DiagramTreeParentSetter = (document: DiagramDocument, nodeId: string, parentId: string) => DiagramDocument;
type DiagramTreeParentClearer = (document: DiagramDocument, nodeId: string) => DiagramDocument;

describe("diagram layout model", () => {
  it("resolves absolute and relative nodes in snapped grid units", () => {
    const document: DiagramDocument = {
      schemaVersion: 1,
      gridSizePx: 24,
      nodes: [
        { id: "root", order: 0, mode: "absolute", x: 5.2, y: 3.7, width: 2, height: 1 },
        { id: "child", parentId: "root", order: 0, mode: "relative", dx: 2.4, dy: -1.6, width: 2, height: 1 }
      ],
      edges: [{ id: "root-child", source: "root", target: "child", kind: "tree" }]
    };

    const resolved = resolveDiagramLayout(document);

    expect(resolved.nodesById.root).toMatchObject({ worldX: 5, worldY: 4 });
    expect(resolved.nodesById.child).toMatchObject({ worldX: 7, worldY: 2 });
    expect(toCanvasPoint(resolved.nodesById.child, document.gridSizePx)).toEqual({ x: 168, y: 48 });
  });

  it("packs auto children deterministically while preserving fixed children", () => {
    const document: DiagramDocument = {
      schemaVersion: 1,
      gridSizePx: 24,
      nodes: [
        { id: "root", order: 0, mode: "absolute", x: 0, y: 0, width: 2, height: 1 },
        { id: "fixed", parentId: "root", order: 0, mode: "absolute", fixed: true, x: 10, y: 12, width: 2, height: 1 },
        { id: "middle", parentId: "root", order: 1, mode: "auto", width: 2, height: 1 },
        { id: "left", parentId: "root", order: 2, mode: "auto", width: 2, height: 1 }
      ],
      edges: [
        { id: "root-fixed", source: "root", target: "fixed", kind: "tree" },
        { id: "root-middle", source: "root", target: "middle", kind: "tree" },
        { id: "root-left", source: "root", target: "left", kind: "tree" }
      ]
    };

    const resolved = resolveDiagramLayout(document, { layerGap: 4, siblingGap: 1 });

    expect(resolved.nodes.map((node) => node.id)).toEqual(["root", "fixed", "middle", "left"]);
    expect(resolved.nodesById.fixed).toMatchObject({ worldX: 10, worldY: 12 });
    expect(resolved.nodesById.middle).toMatchObject({ worldX: -2, worldY: 5 });
    expect(resolved.nodesById.left).toMatchObject({ worldX: 1, worldY: 5 });
  });

  it("uses document-level layout options when resolving auto rows", () => {
    const document: DiagramDocument = {
      schemaVersion: 1,
      gridSizePx: 48,
      layoutOptions: { layerGap: 0 },
      nodes: [
        { id: "root", order: 0, mode: "absolute", x: 4, y: 2, width: 1, height: 1 },
        { id: "child", parentId: "root", order: 1, mode: "auto", dx: 2, dy: 1, relativePositionKind: "legacy_offset", width: 1, height: 1 }
      ],
      edges: [{ id: "tree:root->child", source: "root", target: "child", kind: "tree" }]
    };

    expect(resolveDiagramLayout(document).nodesById.child).toMatchObject({ worldX: 6, worldY: 4 });
    expect(resolveDiagramLayout(document, { layerGap: 4 }).nodesById.child).toMatchObject({ worldX: 6, worldY: 8 });
  });

  it("packs auto children by legacy priority and subtree lane hints", () => {
    const document: DiagramDocument = {
      schemaVersion: 1,
      gridSizePx: 24,
      nodes: [
        { id: "root", order: 0, mode: "absolute", x: 10, y: 0, width: 4, height: 2, subtreeCenterOffset: 1 },
        { id: "low", parentId: "root", order: 0, mode: "auto", width: 4, height: 2 },
        { id: "wide", parentId: "root", order: 1, mode: "auto", width: 4, height: 2, priority: 10, subtreeWidth: 8 },
        { id: "branch", parentId: "root", order: 2, mode: "auto", width: 4, height: 2, priority: 20, subtreeWidthDelta: 2 },
        { id: "branch-left", parentId: "branch", order: 0, mode: "auto", width: 4, height: 2 },
        { id: "branch-right", parentId: "branch", order: 1, mode: "auto", width: 4, height: 2 }
      ],
      edges: [
        { id: "tree:root->low", source: "root", target: "low", kind: "tree" },
        { id: "tree:root->wide", source: "root", target: "wide", kind: "tree" },
        { id: "tree:root->branch", source: "root", target: "branch", kind: "tree" },
        { id: "tree:branch->branch-left", source: "branch", target: "branch-left", kind: "tree" },
        { id: "tree:branch->branch-right", source: "branch", target: "branch-right", kind: "tree" }
      ]
    };

    const resolved = resolveDiagramLayout(document, { layerGap: 4, siblingGap: 1 });

    expect(resolved.nodes.map((node) => node.id)).toEqual(["root", "branch", "branch-left", "branch-right", "wide", "low"]);
    expect(resolved.nodesById.branch).toMatchObject({ worldX: 5, worldY: 6 });
    expect(resolved.nodesById.wide).toMatchObject({ worldX: 15, worldY: 6 });
    expect(resolved.nodesById.low).toMatchObject({ worldX: 22, worldY: 6 });
    expect(resolved.nodesById["branch-left"]).toMatchObject({ worldX: 3, worldY: 12 });
    expect(resolved.nodesById["branch-right"]).toMatchObject({ worldX: 8, worldY: 12 });
  });

  it("sets and clears PIHC legacy focus layout hints on a diagram node", () => {
    const document: DiagramDocument = {
      schemaVersion: 1,
      gridSizePx: 24,
      nodes: [{ id: "focus", order: 0, mode: "auto", width: 4, height: 2, priority: 10, subtreeWidth: 6 }],
      edges: []
    };

    const updated = setDiagramNodeLayoutHints(document, "focus", {
      priority: 20,
      subtreeCenterOffset: -1,
      subtreeWidth: 8,
      subtreeWidthDelta: 2
    });

    expect(updated).not.toBe(document);
    expect(updated.nodes[0]).toMatchObject({
      priority: 20,
      subtreeCenterOffset: -1,
      subtreeWidth: 8,
      subtreeWidthDelta: 2
    });
    const cleared = setDiagramNodeLayoutHints(updated, "focus", {});
    expect(cleared.nodes[0]).toEqual({ id: "focus", order: 0, mode: "auto", width: 4, height: 2 });
    expect(setDiagramNodeLayoutHints(document, "missing", { priority: 1 })).toBe(document);
  });

  it("pins a resolved node as a canonical absolute node", () => {
    const document: DiagramDocument = {
      schemaVersion: 1,
      gridSizePx: 24,
      nodes: [
        { id: "root", order: 0, mode: "absolute", x: 0, y: 0, width: 2, height: 1 },
        { id: "child", parentId: "root", order: 0, mode: "auto", width: 2, height: 1 }
      ],
      edges: [{ id: "root-child", source: "root", target: "child", kind: "tree" }]
    };

    const resolved = resolveDiagramLayout(document).nodesById.child;
    const pinned = pinDiagramNode(document.nodes[1], resolved);

    expect(pinned).toEqual({
      id: "child",
      parentId: "root",
      order: 0,
      mode: "absolute",
      fixed: true,
      x: 0,
      y: 5,
      width: 2,
      height: 1
    });
  });

  it("converts a selected child node to parent-relative coordinates without moving it", () => {
    const document: DiagramDocument = {
      schemaVersion: 1,
      gridSizePx: 24,
      nodes: [
        { id: "root", order: 0, mode: "absolute", fixed: true, x: 10, y: 4, width: 2, height: 1 },
        { id: "child", parentId: "root", order: 0, mode: "absolute", fixed: true, x: 13, y: 7, width: 2, height: 1 }
      ],
      edges: [{ id: "root-child", source: "root", target: "child", kind: "tree" }]
    };

    const updated = makeDiagramSelectedNodeRelative(document, "child");

    expect(updated.nodes[1]).toEqual({
      id: "child",
      parentId: "root",
      order: 0,
      mode: "relative",
      dx: 3,
      dy: 3,
      width: 2,
      height: 1
    });
    expect(resolveDiagramLayout(updated).nodesById.child).toMatchObject({ worldX: 13, worldY: 7 });
    expect(makeDiagramSelectedNodeRelative(updated, "child")).toBe(updated);
    expect(makeDiagramSelectedNodeRelative(document, "root")).toBe(document);
    expect(makeDiagramSelectedNodeRelative(document, "missing")).toBe(document);
  });

  it("converts an editable branch to parent-relative coordinates without moving it", () => {
    const document: DiagramDocument = {
      schemaVersion: 1,
      gridSizePx: 24,
      nodes: [
        { id: "root", order: 0, mode: "absolute", fixed: true, x: 10, y: 4, width: 2, height: 1 },
        { id: "branch", parentId: "root", order: 0, mode: "absolute", fixed: true, x: 13, y: 7, width: 2, height: 1 },
        { id: "leaf", parentId: "branch", order: 0, mode: "auto", width: 2, height: 1 }
      ],
      edges: [
        { id: "root-branch", source: "root", target: "branch", kind: "tree" },
        { id: "branch-leaf", source: "branch", target: "leaf", kind: "tree" }
      ]
    };

    const updated = makeDiagramSubtreeRelative(document, "root");

    expect(updated.nodes).toEqual([
      { id: "root", order: 0, mode: "absolute", fixed: true, x: 10, y: 4, width: 2, height: 1 },
      { id: "branch", parentId: "root", order: 0, mode: "relative", dx: 3, dy: 3, width: 2, height: 1 },
      { id: "leaf", parentId: "branch", order: 0, mode: "relative", dx: 0, dy: 5, width: 2, height: 1 }
    ]);
    expect(resolveDiagramLayout(updated).nodesById).toMatchObject({
      branch: { worldX: 13, worldY: 7 },
      leaf: { worldX: 13, worldY: 12 }
    });
    expect(makeDiagramSubtreeRelative(updated, "root")).toBe(updated);
    expect(makeDiagramSubtreeRelative(document, "missing")).toBe(document);
  });

  it("moves an auto node by pinning its resolved position plus a grid delta", () => {
    const document: DiagramDocument = {
      schemaVersion: 1,
      gridSizePx: 24,
      nodes: [
        { id: "root", order: 0, mode: "absolute", x: 2, y: 3, width: 2, height: 1 },
        { id: "child", parentId: "root", order: 0, mode: "auto", width: 2, height: 1 }
      ],
      edges: [{ id: "root-child", source: "root", target: "child", kind: "tree" }]
    };

    const moved = moveDiagramNode(document, "child", { dx: 2, dy: -1 });

    expect(document.nodes[1]).toMatchObject({ mode: "auto" });
    expect(moved).not.toBe(document);
    expect(moved.nodes[1]).toEqual({
      id: "child",
      parentId: "root",
      order: 0,
      mode: "absolute",
      fixed: true,
      x: 4,
      y: 7,
      width: 2,
      height: 1
    });
    expect(resolveDiagramLayout(moved).nodesById.child).toMatchObject({ worldX: 4, worldY: 7 });
  });

  it("moves a PIHC legacy auto-offset node by updating its dx and dy nudge", () => {
    const document: DiagramDocument = {
      schemaVersion: 1,
      gridSizePx: 24,
      nodes: [
        { id: "root", order: 0, mode: "absolute", fixed: true, x: 10, y: 0, width: 3, height: 3 },
        { id: "left", parentId: "root", order: 0, mode: "auto", dx: -1, dy: 1, relativePositionKind: "legacy_offset", width: 3, height: 3 },
        { id: "leaf", parentId: "left", order: 0, mode: "auto", width: 3, height: 3 },
        { id: "right", parentId: "root", order: 1, mode: "auto", width: 3, height: 3 }
      ],
      edges: [
        { id: "tree:root->left", source: "root", target: "left", kind: "tree" },
        { id: "tree:left->leaf", source: "left", target: "leaf", kind: "tree" },
        { id: "tree:root->right", source: "root", target: "right", kind: "tree" }
      ]
    };

    const moved = moveDiagramNode(document, "left", { dx: 2, dy: -1 });

    expect(moved.nodes[1]).toEqual({
      id: "left",
      parentId: "root",
      order: 0,
      mode: "auto",
      dx: 1,
      dy: 0,
      relativePositionKind: "legacy_offset",
      width: 3,
      height: 3
    });
    expect(resolveDiagramLayout(moved).nodesById).toMatchObject({
      left: { worldX: 9, worldY: 7 },
      leaf: { worldX: 9, worldY: 14 },
      right: { worldX: 12, worldY: 7 }
    });
  });

  it("saves canonical viewport state without changing node layout", () => {
    const document: DiagramDocument = {
      schemaVersion: 1,
      gridSizePx: 24,
      nodes: [{ id: "root", order: 0, mode: "absolute", fixed: true, x: 0, y: 0, width: 2, height: 1 }],
      edges: []
    };

    const updated = setDiagramViewport(document, { x: 24.1234, y: -12.9876, zoom: 1.5 });

    expect(updated).toEqual({
      ...document,
      viewport: { x: 24.123, y: -12.988, zoom: 1.5 }
    });
    expect(setDiagramViewport(updated, { x: 24.123, y: -12.988, zoom: 1.5 })).toBe(updated);
    expect(setDiagramViewport(updated, { x: Number.NaN, y: 0, zoom: 1 })).toBe(updated);
    expect(setDiagramViewport(updated, { x: 0, y: 0, zoom: 0 })).toBe(updated);
  });

  it("moves a relative node by preserving its parent-relative offset mode", () => {
    const document: DiagramDocument = {
      schemaVersion: 1,
      gridSizePx: 24,
      nodes: [
        { id: "root", order: 0, mode: "absolute", fixed: true, x: 10, y: 4, width: 2, height: 1 },
        { id: "child", parentId: "root", order: 0, mode: "relative", dx: 1, dy: 2, width: 2, height: 1 }
      ],
      edges: [{ id: "root-child", source: "root", target: "child", kind: "tree" }]
    };

    const moved = moveDiagramNode(document, "child", { dx: 3, dy: -1 });

    expect(moved).not.toBe(document);
    expect(moved.nodes[1]).toEqual({
      id: "child",
      parentId: "root",
      order: 0,
      mode: "relative",
      dx: 4,
      dy: 1,
      width: 2,
      height: 1
    });
    expect(resolveDiagramLayout(moved).nodesById.child).toMatchObject({ worldX: 14, worldY: 5 });
  });

  it("sets a selected node to an exact snapped grid position", () => {
    const document: DiagramDocument = {
      schemaVersion: 1,
      gridSizePx: 24,
      nodes: [
        { id: "root", order: 0, mode: "absolute", fixed: true, x: 10, y: 4, width: 2, height: 1 },
        { id: "child", parentId: "root", order: 0, mode: "relative", dx: 1, dy: 2, width: 2, height: 1 },
        { id: "auto-child", parentId: "root", order: 1, mode: "auto", width: 2, height: 1 }
      ],
      edges: [
        { id: "root-child", source: "root", target: "child", kind: "tree" },
        { id: "root-auto", source: "root", target: "auto-child", kind: "tree" }
      ]
    };

    const moved = setDiagramNodePosition(document, "child", { x: 14.4, y: 4.6 });
    const pinned = setDiagramNodePosition(document, "auto-child", { x: 16, y: 8 });

    expect(moved.nodes[1]).toEqual({
      id: "child",
      parentId: "root",
      order: 0,
      mode: "relative",
      dx: 4,
      dy: 1,
      width: 2,
      height: 1
    });
    expect(pinned.nodes[2]).toEqual({
      id: "auto-child",
      parentId: "root",
      order: 1,
      mode: "absolute",
      fixed: true,
      x: 16,
      y: 8,
      width: 2,
      height: 1
    });
    expect(setDiagramNodePosition(moved, "child", { x: 14, y: 5 })).toBe(moved);
    expect(setDiagramNodePosition(moved, "missing", { x: 14, y: 5 })).toBe(moved);
  });

  it("moves a relative subtree root by preserving its parent-relative offset mode", () => {
    const document: DiagramDocument = {
      schemaVersion: 1,
      gridSizePx: 24,
      nodes: [
        { id: "root", order: 0, mode: "absolute", fixed: true, x: 10, y: 4, width: 2, height: 1 },
        { id: "branch", parentId: "root", order: 0, mode: "relative", dx: 1, dy: 2, width: 2, height: 1 },
        { id: "leaf", parentId: "branch", order: 0, mode: "relative", dx: 2, dy: 3, width: 2, height: 1 }
      ],
      edges: [
        { id: "root-branch", source: "root", target: "branch", kind: "tree" },
        { id: "branch-leaf", source: "branch", target: "leaf", kind: "tree" }
      ]
    };

    const moved = moveDiagramSubtree(document, "branch", { dx: 3, dy: -1 });

    expect(moved.nodes).toEqual([
      { id: "root", order: 0, mode: "absolute", fixed: true, x: 10, y: 4, width: 2, height: 1 },
      { id: "branch", parentId: "root", order: 0, mode: "relative", dx: 4, dy: 1, width: 2, height: 1 },
      { id: "leaf", parentId: "branch", order: 0, mode: "relative", dx: 2, dy: 3, width: 2, height: 1 }
    ]);
    expect(resolveDiagramLayout(moved).nodesById).toMatchObject({
      branch: { worldX: 14, worldY: 5 },
      leaf: { worldX: 16, worldY: 8 }
    });
  });

  it("reorders a selected node among siblings without changing other branches", () => {
    const document: DiagramDocument = {
      schemaVersion: 1,
      gridSizePx: 24,
      nodes: [
        { id: "root", order: 0, mode: "absolute", fixed: true, x: 0, y: 0, width: 2, height: 1 },
        { id: "first", parentId: "root", order: 0, mode: "auto", width: 2, height: 1 },
        { id: "second", parentId: "root", order: 1, mode: "auto", width: 2, height: 1 },
        { id: "third", parentId: "root", order: 2, mode: "auto", width: 2, height: 1 },
        { id: "other-root", order: 1, mode: "absolute", fixed: true, x: 10, y: 0, width: 2, height: 1 },
        { id: "other-child", parentId: "other-root", order: 0, mode: "auto", width: 2, height: 1 }
      ],
      edges: [
        { id: "root-first", source: "root", target: "first", kind: "tree" },
        { id: "root-second", source: "root", target: "second", kind: "tree" },
        { id: "root-third", source: "root", target: "third", kind: "tree" },
        { id: "other-child", source: "other-root", target: "other-child", kind: "tree" }
      ]
    };

    const reordered = reorderDiagramSibling(document, "third", -1);

    expect(reordered).not.toBe(document);
    expect(reordered.nodes.map((node) => [node.id, node.order])).toEqual([
      ["root", 0],
      ["first", 0],
      ["second", 2],
      ["third", 1],
      ["other-root", 1],
      ["other-child", 0]
    ]);
    expect(resolveDiagramLayout(reordered).nodes.map((node) => node.id)).toEqual(["root", "first", "third", "second", "other-root", "other-child"]);
    expect(reorderDiagramSibling(reordered, "first", -1)).toBe(reordered);
  });

  it("moves a relative node while keeping descendants visually fixed without pinning the selected node", () => {
    const document: DiagramDocument = {
      schemaVersion: 1,
      gridSizePx: 24,
      nodes: [
        { id: "root", order: 0, mode: "absolute", fixed: true, x: 10, y: 4, width: 2, height: 1 },
        { id: "branch", parentId: "root", order: 0, mode: "relative", dx: 1, dy: 2, width: 2, height: 1 },
        { id: "leaf", parentId: "branch", order: 0, mode: "relative", dx: 2, dy: 3, width: 2, height: 1 }
      ],
      edges: [
        { id: "root-branch", source: "root", target: "branch", kind: "tree" },
        { id: "branch-leaf", source: "branch", target: "leaf", kind: "tree" }
      ]
    };

    const moved = moveDiagramNodeKeepingDescendants(document, "branch", { dx: 3, dy: -1 });

    expect(moved.nodes).toEqual([
      { id: "root", order: 0, mode: "absolute", fixed: true, x: 10, y: 4, width: 2, height: 1 },
      { id: "branch", parentId: "root", order: 0, mode: "relative", dx: 4, dy: 1, width: 2, height: 1 },
      { id: "leaf", parentId: "branch", order: 0, mode: "relative", dx: -1, dy: 4, width: 2, height: 1 }
    ]);
    expect(resolveDiagramLayout(moved).nodesById).toMatchObject({
      branch: { worldX: 14, worldY: 5 },
      leaf: { worldX: 13, worldY: 9 }
    });
  });

  it("moves a selected subtree while preserving descendant layout modes", () => {
    const document: DiagramDocument = {
      schemaVersion: 1,
      gridSizePx: 24,
      nodes: [
        { id: "root", order: 0, mode: "absolute", fixed: true, x: 10, y: 4, width: 2, height: 1 },
        { id: "branch", parentId: "root", order: 0, mode: "auto", width: 2, height: 1 },
        { id: "relative-leaf", parentId: "branch", order: 0, mode: "relative", dx: 2, dy: 3, width: 2, height: 1 },
        { id: "auto-leaf", parentId: "branch", order: 1, mode: "auto", width: 2, height: 1 },
        { id: "absolute-leaf", parentId: "branch", order: 2, mode: "absolute", fixed: true, x: 30, y: 12, width: 2, height: 1 },
        { id: "sibling", parentId: "root", order: 1, mode: "absolute", fixed: true, x: 20, y: 8, width: 2, height: 1 }
      ],
      edges: [
        { id: "root-branch", source: "root", target: "branch", kind: "tree" },
        { id: "branch-relative", source: "branch", target: "relative-leaf", kind: "tree" },
        { id: "branch-auto", source: "branch", target: "auto-leaf", kind: "tree" },
        { id: "branch-absolute", source: "branch", target: "absolute-leaf", kind: "tree" },
        { id: "root-sibling", source: "root", target: "sibling", kind: "tree" }
      ]
    };

    const moved = moveDiagramSubtree(document, "branch", { dx: 3, dy: -2 });

    expect(moved).not.toBe(document);
    expect(moved.nodes).toEqual([
      { id: "root", order: 0, mode: "absolute", fixed: true, x: 10, y: 4, width: 2, height: 1 },
      { id: "branch", parentId: "root", order: 0, mode: "absolute", fixed: true, x: 13, y: 7, width: 2, height: 1 },
      { id: "relative-leaf", parentId: "branch", order: 0, mode: "relative", dx: 2, dy: 3, width: 2, height: 1 },
      { id: "auto-leaf", parentId: "branch", order: 1, mode: "auto", width: 2, height: 1 },
      { id: "absolute-leaf", parentId: "branch", order: 2, mode: "absolute", fixed: true, x: 33, y: 10, width: 2, height: 1 },
      { id: "sibling", parentId: "root", order: 1, mode: "absolute", fixed: true, x: 20, y: 8, width: 2, height: 1 }
    ]);
    expect(resolveDiagramLayout(moved).nodesById).toMatchObject({
      branch: { worldX: 13, worldY: 7 },
      "relative-leaf": { worldX: 15, worldY: 10 },
      "auto-leaf": { worldX: 13, worldY: 12 },
      "absolute-leaf": { worldX: 33, worldY: 10 },
      sibling: { worldX: 20, worldY: 8 }
    });
  });

  it("removes a selected subtree and all incident edges", () => {
    const document: DiagramDocument = {
      schemaVersion: 1,
      gridSizePx: 24,
      nodes: [
        { id: "root", order: 0, mode: "absolute", fixed: true, x: 10, y: 4, width: 2, height: 1 },
        { id: "branch", parentId: "root", order: 0, mode: "auto", width: 2, height: 1 },
        { id: "leaf", parentId: "branch", order: 0, mode: "auto", width: 2, height: 1 },
        { id: "referenced", parentId: "root", order: 1, mode: "auto", width: 2, height: 1 }
      ],
      edges: [
        { id: "root-branch", source: "root", target: "branch", kind: "tree" },
        { id: "branch-leaf", source: "branch", target: "leaf", kind: "tree" },
        { id: "leaf-reference", source: "leaf", target: "referenced", kind: "reference" },
        { id: "root-referenced", source: "root", target: "referenced", kind: "tree" }
      ]
    };

    const removed = removeDiagramSubtree(document, "branch");

    expect(removed).not.toBe(document);
    expect(removed.nodes.map((node) => node.id)).toEqual(["root", "referenced"]);
    expect(removed.edges).toEqual([{ id: "root-referenced", source: "root", target: "referenced", kind: "tree" }]);
    expect(removeDiagramSubtree(document, "missing")).toBe(document);
  });

  it("rejects subtree removal for source-backed non-focus nodes", () => {
    const document: DiagramDocument = {
      schemaVersion: 1,
      gridSizePx: 24,
      nodes: [
        { id: "C08_PARTIV", order: 0, mode: "absolute", fixed: true, x: 0, y: 0, width: 6, height: 2, payload: { itemId: "focus_tree:C08_PARTIV", objectId: "C08_PARTIV" } },
        {
          id: "FOCUS_CHILD",
          parentId: "C08_PARTIV",
          order: 0,
          mode: "auto",
          width: 4,
          height: 2,
          payload: { itemId: "focus_tree:C08_PARTIV", objectId: "C08_PARTIV", embeddedId: "FOCUS_CHILD", embeddedKind: "focus" }
        }
      ],
      edges: [{ id: "tree:C08_PARTIV->FOCUS_CHILD", source: "C08_PARTIV", target: "FOCUS_CHILD", kind: "tree" }]
    };

    expect(removeDiagramSubtree(document, "C08_PARTIV")).toBe(document);
    expect(removeDiagramSubtree(document, "FOCUS_CHILD").nodes).toEqual([document.nodes[0]]);
  });

  it("removes a selected node while promoting children to its parent", () => {
    const removeDiagramNodeOnly = (layoutModel as typeof layoutModel & { removeDiagramNodeOnly?: DiagramNodeOnlyRemover }).removeDiagramNodeOnly;
    const document: DiagramDocument = {
      schemaVersion: 1,
      gridSizePx: 24,
      nodes: [
        { id: "root", order: 0, mode: "absolute", fixed: true, x: 10, y: 4, width: 2, height: 1 },
        { id: "branch", parentId: "root", order: 0, mode: "auto", width: 2, height: 1 },
        { id: "relative-leaf", parentId: "branch", order: 0, mode: "relative", dx: 2, dy: 3, width: 2, height: 1 },
        { id: "auto-leaf", parentId: "branch", order: 1, mode: "auto", width: 2, height: 1 },
        { id: "referenced", parentId: "root", order: 1, mode: "auto", width: 2, height: 1 }
      ],
      edges: [
        { id: "tree:root->branch", source: "root", target: "branch", kind: "tree" },
        { id: "tree:branch->relative-leaf", source: "branch", target: "relative-leaf", kind: "tree" },
        { id: "tree:branch->auto-leaf", source: "branch", target: "auto-leaf", kind: "tree" },
        { id: "tree:root->referenced", source: "root", target: "referenced", kind: "tree" },
        { id: "dependency:root->branch", source: "root", target: "branch", kind: "dependency" },
        { id: "reference:branch->referenced", source: "branch", target: "referenced", kind: "reference" },
        { id: "dependency:root->referenced", source: "root", target: "referenced", kind: "dependency" }
      ]
    };

    expect(removeDiagramNodeOnly).toBeTypeOf("function");
    if (!removeDiagramNodeOnly) {
      return;
    }

    const removed = removeDiagramNodeOnly(document, "branch");

    expect(removed).not.toBe(document);
    expect(removed.nodes).toEqual([
      { id: "root", order: 0, mode: "absolute", fixed: true, x: 10, y: 4, width: 2, height: 1 },
      { id: "relative-leaf", parentId: "root", order: 0, mode: "relative", dx: 1, dy: 8, width: 2, height: 1 },
      { id: "auto-leaf", parentId: "root", order: 1, mode: "absolute", fixed: true, x: 9, y: 14, width: 2, height: 1 },
      { id: "referenced", parentId: "root", order: 2, mode: "auto", width: 2, height: 1 }
    ]);
    expect(removed.edges).toEqual([
      { id: "tree:root->referenced", source: "root", target: "referenced", kind: "tree" },
      { id: "dependency:root->referenced", source: "root", target: "referenced", kind: "dependency" },
      { id: "tree:root->relative-leaf", source: "root", target: "relative-leaf", kind: "tree" },
      { id: "tree:root->auto-leaf", source: "root", target: "auto-leaf", kind: "tree" }
    ]);
    expect(resolveDiagramLayout(removed).nodesById).toMatchObject({
      "relative-leaf": { worldX: 11, worldY: 12 },
      "auto-leaf": { worldX: 9, worldY: 14 }
    });
    expect(removeDiagramNodeOnly(document, "missing")).toBe(document);
  });

  it("rejects node-only removal for source-backed non-focus nodes", () => {
    const removeDiagramNodeOnly = (layoutModel as typeof layoutModel & { removeDiagramNodeOnly?: DiagramNodeOnlyRemover }).removeDiagramNodeOnly;
    const document: DiagramDocument = {
      schemaVersion: 1,
      gridSizePx: 24,
      nodes: [
        { id: "C08_PARTIV", order: 0, mode: "absolute", fixed: true, x: 0, y: 0, width: 6, height: 2, payload: { itemId: "focus_tree:C08_PARTIV", objectId: "C08_PARTIV" } },
        {
          id: "FOCUS_CHILD",
          parentId: "C08_PARTIV",
          order: 0,
          mode: "auto",
          width: 4,
          height: 2,
          payload: { itemId: "focus_tree:C08_PARTIV", objectId: "C08_PARTIV", embeddedId: "FOCUS_CHILD", embeddedKind: "focus" }
        }
      ],
      edges: [{ id: "tree:C08_PARTIV->FOCUS_CHILD", source: "C08_PARTIV", target: "FOCUS_CHILD", kind: "tree" }]
    };

    expect(removeDiagramNodeOnly).toBeTypeOf("function");
    if (!removeDiagramNodeOnly) {
      return;
    }

    expect(removeDiagramNodeOnly(document, "C08_PARTIV")).toBe(document);
    expect(removeDiagramNodeOnly(document, "FOCUS_CHILD").nodes).toEqual([document.nodes[0]]);
  });

  it("removes a root node while promoting children without root order collisions", () => {
    const removeDiagramNodeOnly = (layoutModel as typeof layoutModel & { removeDiagramNodeOnly?: DiagramNodeOnlyRemover }).removeDiagramNodeOnly;
    const document: DiagramDocument = {
      schemaVersion: 1,
      gridSizePx: 24,
      nodes: [
        { id: "root", order: 0, mode: "absolute", fixed: true, x: 10, y: 4, width: 2, height: 1 },
        { id: "child-a", parentId: "root", order: 0, mode: "absolute", fixed: true, x: 10, y: 9, width: 2, height: 1 },
        { id: "child-b", parentId: "root", order: 1, mode: "absolute", fixed: true, x: 13, y: 9, width: 2, height: 1 },
        { id: "other-root", order: 1, mode: "auto", width: 2, height: 1 }
      ],
      edges: [
        { id: "tree:root->child-a", source: "root", target: "child-a", kind: "tree" },
        { id: "tree:root->child-b", source: "root", target: "child-b", kind: "tree" }
      ]
    };

    expect(removeDiagramNodeOnly).toBeTypeOf("function");
    if (!removeDiagramNodeOnly) {
      return;
    }

    const removed = removeDiagramNodeOnly(document, "root");

    expect(removed.nodes).toEqual([
      { id: "child-a", order: 0, mode: "absolute", fixed: true, x: 10, y: 9, width: 2, height: 1 },
      { id: "child-b", order: 1, mode: "absolute", fixed: true, x: 13, y: 9, width: 2, height: 1 },
      { id: "other-root", order: 2, mode: "auto", width: 2, height: 1 }
    ]);
    expect(removed.edges).toEqual([]);
  });

  it("inserts a child node with sibling order and a tree edge", () => {
    const document: DiagramDocument = {
      schemaVersion: 1,
      gridSizePx: 24,
      nodes: [
        { id: "root", order: 0, mode: "absolute", fixed: true, x: 10, y: 4, width: 2, height: 1 },
        { id: "sibling", parentId: "root", order: 3, mode: "auto", width: 2, height: 1 }
      ],
      edges: [{ id: "tree:root->sibling", source: "root", target: "sibling", kind: "tree" }]
    };

    const inserted = insertDiagramChildNode(document, "root", {
      id: "child",
      mode: "auto",
      width: 2,
      height: 1,
      title: "Child"
    });

    expect(inserted).not.toBe(document);
    expect(inserted.nodes.at(-1)).toEqual({
      id: "child",
      parentId: "root",
      order: 4,
      mode: "auto",
      width: 2,
      height: 1,
      title: "Child"
    });
    expect(inserted.edges.at(-1)).toEqual({ id: "tree:root->child", source: "root", target: "child", kind: "tree" });
    expect(insertDiagramChildNode(document, "missing", { id: "other", mode: "auto", width: 2, height: 1 })).toBe(document);
    expect(insertDiagramChildNode(document, "root", { id: "sibling", mode: "auto", width: 2, height: 1 })).toBe(document);
  });

  it("appends an inserted child after siblings when the requested order collides", () => {
    const document: DiagramDocument = {
      schemaVersion: 1,
      gridSizePx: 24,
      nodes: [
        { id: "root", order: 0, mode: "absolute", fixed: true, x: 10, y: 4, width: 2, height: 1 },
        { id: "sibling", parentId: "root", order: 0, mode: "auto", width: 2, height: 1 }
      ],
      edges: [{ id: "tree:root->sibling", source: "root", target: "sibling", kind: "tree" }]
    };

    const inserted = insertDiagramChildNode(document, "root", {
      id: "child",
      order: 0,
      mode: "auto",
      width: 2,
      height: 1
    });

    expect(inserted.nodes.at(-1)).toMatchObject({ id: "child", parentId: "root", order: 1 });
  });

  it("rejects inserted children that mix embedded focus and non-focus nodes", () => {
    const document: DiagramDocument = {
      schemaVersion: 1,
      gridSizePx: 24,
      nodes: [
        { id: "C08_PARTIV", order: 0, mode: "absolute", fixed: true, x: 0, y: 0, width: 6, height: 2, payload: { itemId: "focus_tree:C08_PARTIV", objectId: "C08_PARTIV" } },
        {
          id: "FOCUS_ROOT",
          order: 1,
          mode: "absolute",
          fixed: true,
          x: 10,
          y: 0,
          width: 4,
          height: 2,
          payload: { itemId: "focus_tree:C08_PARTIV", objectId: "C08_PARTIV", embeddedId: "FOCUS_ROOT", embeddedKind: "focus" }
        }
      ],
      edges: []
    };

    const focusUnderContext = insertDiagramChildNode(document, "C08_PARTIV", {
      id: "FOCUS_NEW_CHILD",
      mode: "auto",
      width: 4,
      height: 2,
      payload: { itemId: "focus_tree:C08_PARTIV", objectId: "C08_PARTIV", embeddedId: "FOCUS_NEW_CHILD", embeddedKind: "focus" }
    });
    const contextUnderFocus = insertDiagramChildNode(document, "FOCUS_ROOT", {
      id: "CONTEXT_CHILD",
      mode: "auto",
      width: 6,
      height: 2,
      payload: { itemId: "focus_tree:C08_PARTIV", objectId: "C08_PARTIV" }
    });
    const focusUnderFocus = insertDiagramChildNode(document, "FOCUS_ROOT", {
      id: "FOCUS_NEW_CHILD",
      mode: "auto",
      width: 4,
      height: 2,
      payload: { itemId: "focus_tree:C08_PARTIV", objectId: "C08_PARTIV", embeddedId: "FOCUS_NEW_CHILD", embeddedKind: "focus" }
    });
    const foreignFocusUnderFocus = insertDiagramChildNode(document, "FOCUS_ROOT", {
      id: "FOCUS_FOREIGN_CHILD",
      mode: "auto",
      width: 4,
      height: 2,
      payload: { itemId: "focus_tree:C09_PARTV", objectId: "C09_PARTV", embeddedId: "FOCUS_FOREIGN_CHILD", embeddedKind: "focus" }
    });

    expect(focusUnderContext).toBe(document);
    expect(contextUnderFocus).toBe(document);
    expect(foreignFocusUnderFocus).toBe(document);
    expect(focusUnderFocus.nodes.at(-1)).toMatchObject({ id: "FOCUS_NEW_CHILD", parentId: "FOCUS_ROOT" });
    expect(focusUnderFocus.edges).toContainEqual({ id: "tree:FOCUS_ROOT->FOCUS_NEW_CHILD", source: "FOCUS_ROOT", target: "FOCUS_NEW_CHILD", kind: "tree" });
  });

  it("inserts a root node without creating a tree edge", () => {
    const document: DiagramDocument = {
      schemaVersion: 1,
      gridSizePx: 24,
      nodes: [
        { id: "root", order: 0, mode: "absolute", fixed: true, x: 10, y: 4, width: 2, height: 1 },
        { id: "other-root", order: 2, mode: "auto", width: 2, height: 1 },
        { id: "child", parentId: "root", order: 0, mode: "auto", width: 2, height: 1 }
      ],
      edges: [{ id: "tree:root->child", source: "root", target: "child", kind: "tree" }]
    };

    const inserted = insertDiagramRootNode(document, {
      id: "new-root",
      mode: "auto",
      width: 2,
      height: 1,
      title: "New Root"
    });

    expect(inserted).not.toBe(document);
    expect(inserted.nodes.at(-1)).toEqual({
      id: "new-root",
      order: 3,
      mode: "auto",
      width: 2,
      height: 1,
      title: "New Root"
    });
    expect(inserted.edges).toEqual(document.edges);
    expect(insertDiagramRootNode(document, { id: "root", mode: "auto", width: 2, height: 1 })).toBe(document);
  });

  it("appends an inserted root after roots when the requested order collides", () => {
    const document: DiagramDocument = {
      schemaVersion: 1,
      gridSizePx: 24,
      nodes: [
        { id: "root", order: 0, mode: "absolute", fixed: true, x: 10, y: 4, width: 2, height: 1 },
        { id: "child", parentId: "root", order: 0, mode: "auto", width: 2, height: 1 }
      ],
      edges: [{ id: "tree:root->child", source: "root", target: "child", kind: "tree" }]
    };

    const inserted = insertDiagramRootNode(document, {
      id: "new-root",
      order: 0,
      mode: "auto",
      width: 2,
      height: 1
    });

    expect(inserted.nodes.at(-1)).toMatchObject({ id: "new-root", order: 1 });
  });

  it("adds and removes dependency edges without changing the tree layout", () => {
    const setDiagramDependencyEdge = (layoutModel as typeof layoutModel & { setDiagramDependencyEdge?: DiagramDependencyEdgeSetter }).setDiagramDependencyEdge;
    const document: DiagramDocument = {
      schemaVersion: 1,
      gridSizePx: 24,
      nodes: [
        { id: "root", order: 0, mode: "absolute", fixed: true, x: 10, y: 4, width: 2, height: 1 },
        { id: "child", parentId: "root", order: 0, mode: "auto", width: 2, height: 1 }
      ],
      edges: [{ id: "tree:root->child", source: "root", target: "child", kind: "tree" }]
    };

    const linked = setDiagramDependencyEdge?.(document, "root", "child", true);
    const unlinked = linked ? setDiagramDependencyEdge?.(linked, "root", "child", false) : undefined;

    expect(linked?.nodes).toEqual(document.nodes);
    expect(linked?.edges).toContainEqual({ id: "dependency:root->child", source: "root", target: "child", kind: "dependency" });
    expect(unlinked?.edges).toEqual(document.edges);
  });

  it("rejects dependency edges that would create prerequisite cycles", () => {
    const setDiagramDependencyEdge = (layoutModel as typeof layoutModel & { setDiagramDependencyEdge?: DiagramDependencyEdgeSetter }).setDiagramDependencyEdge;
    const document: DiagramDocument = {
      schemaVersion: 1,
      gridSizePx: 24,
      nodes: [
        { id: "root", order: 0, mode: "absolute", fixed: true, x: 10, y: 4, width: 2, height: 1 },
        { id: "child", parentId: "root", order: 0, mode: "auto", width: 2, height: 1 },
        { id: "leaf", parentId: "child", order: 0, mode: "auto", width: 2, height: 1 }
      ],
      edges: [
        { id: "dependency:root->child", source: "root", target: "child", kind: "dependency" },
        { id: "dependency:child->leaf", source: "child", target: "leaf", kind: "dependency" }
      ]
    };

    const cyclic = setDiagramDependencyEdge?.(document, "leaf", "root", true);
    const directCycle = setDiagramDependencyEdge?.(document, "child", "root", true);
    const redundantUnlock = setDiagramDependencyEdge?.(document, "root", "leaf", true);

    expect(cyclic).toBe(document);
    expect(directCycle).toBe(document);
    expect(redundantUnlock?.edges).toContainEqual({ id: "dependency:root->leaf", source: "root", target: "leaf", kind: "dependency" });
  });

  it("rejects dependency edges that mix embedded focus and non-focus nodes", () => {
    const setDiagramDependencyEdge = (layoutModel as typeof layoutModel & { setDiagramDependencyEdge?: DiagramDependencyEdgeSetter }).setDiagramDependencyEdge;
    const document: DiagramDocument = {
      schemaVersion: 1,
      gridSizePx: 24,
      nodes: [
        { id: "C08_PARTIV", order: 0, mode: "absolute", fixed: true, x: 10, y: 4, width: 6, height: 2, payload: { itemId: "focus_tree:C08_PARTIV", objectId: "C08_PARTIV" } },
        {
          id: "FOCUS_NEW_ROOT",
          order: 1,
          mode: "auto",
          width: 4,
          height: 2,
          payload: { itemId: "focus_tree:C08_PARTIV", objectId: "C08_PARTIV", embeddedId: "FOCUS_NEW_ROOT", embeddedKind: "focus" }
        },
        {
          id: "FOCUS_NEW_CHILD",
          order: 2,
          mode: "auto",
          width: 4,
          height: 2,
          payload: { itemId: "focus_tree:C08_PARTIV", objectId: "C08_PARTIV", embeddedId: "FOCUS_NEW_CHILD", embeddedKind: "focus" }
        }
      ],
      edges: []
    };

    const contextToFocus = setDiagramDependencyEdge?.(document, "C08_PARTIV", "FOCUS_NEW_ROOT", true);
    const focusToContext = setDiagramDependencyEdge?.(document, "FOCUS_NEW_ROOT", "C08_PARTIV", true);
    const focusToFocus = setDiagramDependencyEdge?.(document, "FOCUS_NEW_ROOT", "FOCUS_NEW_CHILD", true);

    expect(contextToFocus).toBe(document);
    expect(focusToContext).toBe(document);
    expect(focusToFocus?.edges).toContainEqual({ id: "dependency:FOCUS_NEW_ROOT->FOCUS_NEW_CHILD", source: "FOCUS_NEW_ROOT", target: "FOCUS_NEW_CHILD", kind: "dependency" });
  });

  it("rejects dependency edges outside the selected source scope", () => {
    const setDiagramDependencyEdge = (layoutModel as typeof layoutModel & { setDiagramDependencyEdge?: DiagramDependencyEdgeSetter }).setDiagramDependencyEdge;
    const document: DiagramDocument = {
      schemaVersion: 1,
      gridSizePx: 24,
      nodes: [
        { id: "TECH_ROOT", order: 0, mode: "absolute", fixed: true, x: 0, y: 0, width: 6, height: 2, payload: { projectId: "PIHC3", familyId: "technology", family: "technology", itemId: "technology:TECH_ROOT", objectId: "TECH_ROOT" } },
        { id: "TECH_PEER", order: 1, mode: "absolute", fixed: true, x: 8, y: 0, width: 6, height: 2, payload: { projectId: "PIHC3", familyId: "technology", family: "technology", itemId: "technology:TECH_PEER", objectId: "TECH_PEER" } },
        { id: "FOCUS_CONTEXT", order: 2, mode: "absolute", fixed: true, x: 16, y: 0, width: 6, height: 2, payload: { projectId: "PIHC3", familyId: "focus_tree", family: "focus_tree", itemId: "focus_tree:C08_PARTIV", objectId: "C08_PARTIV" } },
        { id: "FOCUS_ROOT", order: 3, mode: "absolute", fixed: true, x: 0, y: 4, width: 4, height: 2, payload: { projectId: "PIHC3", familyId: "focus_tree", family: "focus_tree", itemId: "focus_tree:C08_PARTIV", objectId: "C08_PARTIV", embeddedId: "FOCUS_ROOT", embeddedKind: "focus" } },
        { id: "FOREIGN_FOCUS", order: 4, mode: "absolute", fixed: true, x: 8, y: 4, width: 4, height: 2, payload: { projectId: "PIHC3", familyId: "focus_tree", family: "focus_tree", itemId: "focus_tree:C09_PARTV", objectId: "C09_PARTV", embeddedId: "FOREIGN_FOCUS", embeddedKind: "focus" } }
      ],
      edges: []
    };

    const techToFocusContext = setDiagramDependencyEdge?.(document, "TECH_ROOT", "FOCUS_CONTEXT", true);
    const focusToForeignFocus = setDiagramDependencyEdge?.(document, "FOCUS_ROOT", "FOREIGN_FOCUS", true);
    const techToTech = setDiagramDependencyEdge?.(document, "TECH_ROOT", "TECH_PEER", true);

    expect(techToFocusContext).toBe(document);
    expect(focusToForeignFocus).toBe(document);
    expect(techToTech?.edges).toContainEqual({ id: "dependency:TECH_ROOT->TECH_PEER", source: "TECH_ROOT", target: "TECH_PEER", kind: "dependency" });
  });

  it("adds and removes reference edges without changing the tree layout", () => {
    const setDiagramReferenceEdge = (layoutModel as typeof layoutModel & { setDiagramReferenceEdge?: DiagramReferenceEdgeSetter }).setDiagramReferenceEdge;
    const document: DiagramDocument = {
      schemaVersion: 1,
      gridSizePx: 24,
      nodes: [
        { id: "root", order: 0, mode: "absolute", fixed: true, x: 10, y: 4, width: 2, height: 1 },
        { id: "exclusive", order: 1, mode: "absolute", fixed: true, x: 14, y: 4, width: 2, height: 1 }
      ],
      edges: []
    };

    const linked = setDiagramReferenceEdge?.(document, "root", "exclusive", true);
    const unlinked = linked ? setDiagramReferenceEdge?.(linked, "root", "exclusive", false) : undefined;

    expect(linked?.nodes).toEqual(document.nodes);
    expect(linked?.edges).toContainEqual({ id: "reference:root->exclusive", source: "root", target: "exclusive", kind: "reference" });
    expect(unlinked?.edges).toEqual(document.edges);
  });

  it("rejects reference edges that mix embedded focus and non-focus nodes", () => {
    const setDiagramReferenceEdge = (layoutModel as typeof layoutModel & { setDiagramReferenceEdge?: DiagramReferenceEdgeSetter }).setDiagramReferenceEdge;
    const document: DiagramDocument = {
      schemaVersion: 1,
      gridSizePx: 24,
      nodes: [
        { id: "C08_PARTIV", order: 0, mode: "absolute", fixed: true, x: 10, y: 4, width: 6, height: 2, payload: { itemId: "focus_tree:C08_PARTIV", objectId: "C08_PARTIV" } },
        {
          id: "FOCUS_NEW_ROOT",
          order: 1,
          mode: "auto",
          width: 4,
          height: 2,
          payload: { itemId: "focus_tree:C08_PARTIV", objectId: "C08_PARTIV", embeddedId: "FOCUS_NEW_ROOT", embeddedKind: "focus" }
        },
        {
          id: "FOCUS_NEW_CHILD",
          order: 2,
          mode: "auto",
          width: 4,
          height: 2,
          payload: { itemId: "focus_tree:C08_PARTIV", objectId: "C08_PARTIV", embeddedId: "FOCUS_NEW_CHILD", embeddedKind: "focus" }
        }
      ],
      edges: []
    };

    const focusToContext = setDiagramReferenceEdge?.(document, "FOCUS_NEW_ROOT", "C08_PARTIV", true);
    const contextToFocus = setDiagramReferenceEdge?.(document, "C08_PARTIV", "FOCUS_NEW_ROOT", true);
    const focusToFocus = setDiagramReferenceEdge?.(document, "FOCUS_NEW_ROOT", "FOCUS_NEW_CHILD", true);

    expect(focusToContext).toBe(document);
    expect(contextToFocus).toBe(document);
    expect(focusToFocus?.edges).toContainEqual({ id: "reference:FOCUS_NEW_ROOT->FOCUS_NEW_CHILD", source: "FOCUS_NEW_ROOT", target: "FOCUS_NEW_CHILD", kind: "reference" });
  });

  it("rejects reference edges outside the selected source scope", () => {
    const setDiagramReferenceEdge = (layoutModel as typeof layoutModel & { setDiagramReferenceEdge?: DiagramReferenceEdgeSetter }).setDiagramReferenceEdge;
    const document: DiagramDocument = {
      schemaVersion: 1,
      gridSizePx: 24,
      nodes: [
        { id: "FOCUS_ROOT", order: 0, mode: "absolute", fixed: true, x: 0, y: 0, width: 4, height: 2, payload: { projectId: "PIHC3", familyId: "focus_tree", family: "focus_tree", itemId: "focus_tree:C08_PARTIV", objectId: "C08_PARTIV", embeddedId: "FOCUS_ROOT", embeddedKind: "focus" } },
        { id: "FOCUS_CHILD", order: 1, mode: "absolute", fixed: true, x: 8, y: 0, width: 4, height: 2, payload: { projectId: "PIHC3", familyId: "focus_tree", family: "focus_tree", itemId: "focus_tree:C08_PARTIV", objectId: "C08_PARTIV", embeddedId: "FOCUS_CHILD", embeddedKind: "focus" } },
        { id: "FOREIGN_FOCUS", order: 2, mode: "absolute", fixed: true, x: 16, y: 0, width: 4, height: 2, payload: { projectId: "PIHC3", familyId: "focus_tree", family: "focus_tree", itemId: "focus_tree:C09_PARTV", objectId: "C09_PARTV", embeddedId: "FOREIGN_FOCUS", embeddedKind: "focus" } }
      ],
      edges: []
    };

    const focusToForeignFocus = setDiagramReferenceEdge?.(document, "FOCUS_ROOT", "FOREIGN_FOCUS", true);
    const focusToFocus = setDiagramReferenceEdge?.(document, "FOCUS_ROOT", "FOCUS_CHILD", true);

    expect(focusToForeignFocus).toBe(document);
    expect(focusToFocus?.edges).toContainEqual({ id: "reference:FOCUS_ROOT->FOCUS_CHILD", source: "FOCUS_ROOT", target: "FOCUS_CHILD", kind: "reference" });
  });

  it("changes a tree parent while replacing the canonical tree edge", () => {
    const setDiagramTreeParent = (layoutModel as typeof layoutModel & { setDiagramTreeParent?: DiagramTreeParentSetter }).setDiagramTreeParent;
    const document: DiagramDocument = {
      schemaVersion: 1,
      gridSizePx: 24,
      nodes: [
        { id: "root", order: 0, mode: "absolute", fixed: true, x: 10, y: 4, width: 2, height: 1 },
        { id: "new-parent", order: 1, mode: "absolute", fixed: true, x: 14, y: 4, width: 2, height: 1 },
        { id: "child", parentId: "root", order: 0, mode: "auto", width: 2, height: 1 }
      ],
      edges: [{ id: "tree:root->child", source: "root", target: "child", kind: "tree" }]
    };

    const reparented = setDiagramTreeParent?.(document, "child", "new-parent");
    const rejectedCycle = reparented ? setDiagramTreeParent?.(reparented, "new-parent", "child") : undefined;

    expect(reparented?.nodes.find((node) => node.id === "child")).toMatchObject({ parentId: "new-parent", order: 0 });
    expect(reparented?.edges).not.toContainEqual({ id: "tree:root->child", source: "root", target: "child", kind: "tree" });
    expect(reparented?.edges).toContainEqual({ id: "tree:new-parent->child", source: "new-parent", target: "child", kind: "tree" });
    expect(rejectedCycle).toBe(reparented);
  });

  it("changes a tree parent without moving the selected node", () => {
    const setDiagramTreeParent = (layoutModel as typeof layoutModel & { setDiagramTreeParent?: DiagramTreeParentSetter }).setDiagramTreeParent;
    const document: DiagramDocument = {
      schemaVersion: 1,
      gridSizePx: 24,
      nodes: [
        { id: "root", order: 0, mode: "absolute", fixed: true, x: 0, y: 0, width: 2, height: 1 },
        { id: "new-parent", order: 1, mode: "absolute", fixed: true, x: 10, y: 4, width: 2, height: 1 },
        { id: "child", parentId: "root", order: 0, mode: "auto", width: 2, height: 1 }
      ],
      edges: [{ id: "tree:root->child", source: "root", target: "child", kind: "tree" }]
    };

    const before = resolveDiagramLayout(document).nodesById.child;
    const reparented = setDiagramTreeParent?.(document, "child", "new-parent");

    expect(reparented?.nodes.find((node) => node.id === "child")).toEqual({
      id: "child",
      parentId: "new-parent",
      order: 0,
      mode: "relative",
      dx: -10,
      dy: 1,
      width: 2,
      height: 1
    });
    expect(reparented ? resolveDiagramLayout(reparented).nodesById.child : null).toMatchObject({
      worldX: before.worldX,
      worldY: before.worldY
    });
  });

  it("rejects tree parents that mix embedded focus and non-focus nodes", () => {
    const setDiagramTreeParent = (layoutModel as typeof layoutModel & { setDiagramTreeParent?: DiagramTreeParentSetter }).setDiagramTreeParent;
    const document: DiagramDocument = {
      schemaVersion: 1,
      gridSizePx: 24,
      nodes: [
        { id: "C08_PARTIV", order: 0, mode: "absolute", fixed: true, x: 0, y: 0, width: 6, height: 2, payload: { itemId: "focus_tree:C08_PARTIV", objectId: "C08_PARTIV" } },
        {
          id: "FOCUS_ROOT",
          order: 1,
          mode: "absolute",
          fixed: true,
          x: 10,
          y: 0,
          width: 4,
          height: 2,
          payload: { itemId: "focus_tree:C08_PARTIV", objectId: "C08_PARTIV", embeddedId: "FOCUS_ROOT", embeddedKind: "focus" }
        },
        {
          id: "FOCUS_CHILD",
          order: 2,
          mode: "auto",
          width: 4,
          height: 2,
          payload: { itemId: "focus_tree:C08_PARTIV", objectId: "C08_PARTIV", embeddedId: "FOCUS_CHILD", embeddedKind: "focus" }
        }
      ],
      edges: []
    };

    const contextAsParent = setDiagramTreeParent?.(document, "FOCUS_CHILD", "C08_PARTIV");
    const focusAsContextParent = setDiagramTreeParent?.(document, "C08_PARTIV", "FOCUS_ROOT");
    const focusAsParent = setDiagramTreeParent?.(document, "FOCUS_CHILD", "FOCUS_ROOT");

    expect(contextAsParent).toBe(document);
    expect(focusAsContextParent).toBe(document);
    expect(focusAsParent?.nodes.find((node) => node.id === "FOCUS_CHILD")).toMatchObject({ parentId: "FOCUS_ROOT" });
    expect(focusAsParent?.edges).toContainEqual({ id: "tree:FOCUS_ROOT->FOCUS_CHILD", source: "FOCUS_ROOT", target: "FOCUS_CHILD", kind: "tree" });
  });

  it("rejects tree parents outside the selected source scope", () => {
    const setDiagramTreeParent = (layoutModel as typeof layoutModel & { setDiagramTreeParent?: DiagramTreeParentSetter }).setDiagramTreeParent;
    const document: DiagramDocument = {
      schemaVersion: 1,
      gridSizePx: 24,
      nodes: [
        { id: "FOCUS_ROOT", order: 0, mode: "absolute", fixed: true, x: 0, y: 0, width: 4, height: 2, payload: { projectId: "PIHC3", familyId: "focus_tree", family: "focus_tree", itemId: "focus_tree:C08_PARTIV", objectId: "C08_PARTIV", embeddedId: "FOCUS_ROOT", embeddedKind: "focus" } },
        { id: "FOCUS_CHILD", order: 1, mode: "absolute", fixed: true, x: 8, y: 0, width: 4, height: 2, payload: { projectId: "PIHC3", familyId: "focus_tree", family: "focus_tree", itemId: "focus_tree:C08_PARTIV", objectId: "C08_PARTIV", embeddedId: "FOCUS_CHILD", embeddedKind: "focus" } },
        { id: "FOREIGN_FOCUS", order: 2, mode: "absolute", fixed: true, x: 16, y: 0, width: 4, height: 2, payload: { projectId: "PIHC3", familyId: "focus_tree", family: "focus_tree", itemId: "focus_tree:C09_PARTV", objectId: "C09_PARTV", embeddedId: "FOREIGN_FOCUS", embeddedKind: "focus" } }
      ],
      edges: []
    };

    const foreignAsParent = setDiagramTreeParent?.(document, "FOCUS_CHILD", "FOREIGN_FOCUS");
    const focusAsParent = setDiagramTreeParent?.(document, "FOCUS_CHILD", "FOCUS_ROOT");

    expect(foreignAsParent).toBe(document);
    expect(focusAsParent?.nodes.find((node) => node.id === "FOCUS_CHILD")).toMatchObject({ parentId: "FOCUS_ROOT" });
    expect(focusAsParent?.edges).toContainEqual({ id: "tree:FOCUS_ROOT->FOCUS_CHILD", source: "FOCUS_ROOT", target: "FOCUS_CHILD", kind: "tree" });
  });

  it("appends a reparented node after existing children of the new parent", () => {
    const setDiagramTreeParent = (layoutModel as typeof layoutModel & { setDiagramTreeParent?: DiagramTreeParentSetter }).setDiagramTreeParent;
    const document: DiagramDocument = {
      schemaVersion: 1,
      gridSizePx: 24,
      nodes: [
        { id: "old-parent", order: 0, mode: "absolute", fixed: true, x: 0, y: 0, width: 2, height: 1 },
        { id: "new-parent", order: 1, mode: "absolute", fixed: true, x: 10, y: 0, width: 2, height: 1 },
        { id: "existing-child", parentId: "new-parent", order: 0, mode: "auto", width: 2, height: 1 },
        { id: "moved-child", parentId: "old-parent", order: 0, mode: "auto", width: 2, height: 1 }
      ],
      edges: [
        { id: "tree:new-parent->existing-child", source: "new-parent", target: "existing-child", kind: "tree" },
        { id: "tree:old-parent->moved-child", source: "old-parent", target: "moved-child", kind: "tree" }
      ]
    };

    const before = resolveDiagramLayout(document).nodesById["moved-child"];
    const reparented = setDiagramTreeParent?.(document, "moved-child", "new-parent");

    expect(reparented?.nodes.find((node) => node.id === "moved-child")).toEqual({
      id: "moved-child",
      parentId: "new-parent",
      order: 1,
      mode: "relative",
      dx: -10,
      dy: 5,
      width: 2,
      height: 1
    });
    expect(reparented ? resolveDiagramLayout(reparented).nodesById["moved-child"] : null).toMatchObject({
      worldX: before.worldX,
      worldY: before.worldY
    });
    expect(reparented?.edges).toContainEqual({ id: "tree:new-parent->moved-child", source: "new-parent", target: "moved-child", kind: "tree" });
    expect(reparented?.edges).not.toContainEqual({ id: "tree:old-parent->moved-child", source: "old-parent", target: "moved-child", kind: "tree" });
  });

  it("clears a tree parent and removes the canonical tree edge", () => {
    const clearDiagramTreeParent = (layoutModel as typeof layoutModel & { clearDiagramTreeParent?: DiagramTreeParentClearer }).clearDiagramTreeParent;
    const document: DiagramDocument = {
      schemaVersion: 1,
      gridSizePx: 24,
      nodes: [
        { id: "root", order: 0, mode: "absolute", fixed: true, x: 10, y: 4, width: 2, height: 1 },
        { id: "child", parentId: "root", order: 0, mode: "auto", width: 2, height: 1 }
      ],
      edges: [
        { id: "tree:root->child", source: "root", target: "child", kind: "tree" },
        { id: "dependency:root->child", source: "root", target: "child", kind: "dependency" }
      ]
    };

    const rooted = clearDiagramTreeParent?.(document, "child");

    expect(rooted?.nodes.find((node) => node.id === "child")).not.toHaveProperty("parentId");
    expect(rooted?.edges).not.toContainEqual({ id: "tree:root->child", source: "root", target: "child", kind: "tree" });
    expect(rooted?.edges).toContainEqual({ id: "dependency:root->child", source: "root", target: "child", kind: "dependency" });
  });

  it("appends a cleared child after existing roots without moving it", () => {
    const clearDiagramTreeParent = (layoutModel as typeof layoutModel & { clearDiagramTreeParent?: DiagramTreeParentClearer }).clearDiagramTreeParent;
    const document: DiagramDocument = {
      schemaVersion: 1,
      gridSizePx: 24,
      nodes: [
        { id: "old-parent", order: 0, mode: "absolute", fixed: true, x: 0, y: 0, width: 2, height: 1 },
        { id: "other-root", order: 1, mode: "absolute", fixed: true, x: 12, y: 0, width: 2, height: 1 },
        { id: "child", parentId: "old-parent", order: 0, mode: "auto", width: 2, height: 1 }
      ],
      edges: [{ id: "tree:old-parent->child", source: "old-parent", target: "child", kind: "tree" }]
    };

    const before = resolveDiagramLayout(document).nodesById.child;
    const rooted = clearDiagramTreeParent?.(document, "child");

    expect(rooted?.nodes.find((node) => node.id === "child")).toEqual({
      id: "child",
      order: 2,
      mode: "absolute",
      fixed: true,
      x: 0,
      y: 5,
      width: 2,
      height: 1
    });
    expect(rooted ? resolveDiagramLayout(rooted).nodesById.child : null).toMatchObject({
      worldX: before.worldX,
      worldY: before.worldY
    });
    expect(rooted?.edges).not.toContainEqual({ id: "tree:old-parent->child", source: "old-parent", target: "child", kind: "tree" });
  });

  it("clears a relative tree parent without making an invalid root node", () => {
    const clearDiagramTreeParent = (layoutModel as typeof layoutModel & { clearDiagramTreeParent?: DiagramTreeParentClearer }).clearDiagramTreeParent;
    const document: DiagramDocument = {
      schemaVersion: 1,
      gridSizePx: 24,
      nodes: [
        { id: "root", order: 0, mode: "absolute", fixed: true, x: 10, y: 4, width: 2, height: 1 },
        { id: "child", parentId: "root", order: 0, mode: "relative", dx: 3, dy: 2, width: 2, height: 1 }
      ],
      edges: [{ id: "tree:root->child", source: "root", target: "child", kind: "tree" }]
    };

    const before = resolveDiagramLayout(document).nodesById.child;
    const rooted = clearDiagramTreeParent?.(document, "child");

    expect(rooted?.nodes.find((node) => node.id === "child")).toEqual({
      id: "child",
      order: 1,
      mode: "absolute",
      fixed: true,
      x: 13,
      y: 6,
      width: 2,
      height: 1
    });
    expect(rooted ? resolveDiagramLayout(rooted).nodesById.child : null).toMatchObject({
      worldX: before.worldX,
      worldY: before.worldY
    });
  });

  it("clears an auto tree parent without visually moving the selected node", () => {
    const clearDiagramTreeParent = (layoutModel as typeof layoutModel & { clearDiagramTreeParent?: DiagramTreeParentClearer }).clearDiagramTreeParent;
    const document: DiagramDocument = {
      schemaVersion: 1,
      gridSizePx: 24,
      nodes: [
        { id: "root", order: 0, mode: "absolute", fixed: true, x: 8, y: 2, width: 2, height: 1 },
        { id: "child", parentId: "root", order: 0, mode: "auto", width: 2, height: 1 }
      ],
      edges: [{ id: "tree:root->child", source: "root", target: "child", kind: "tree" }]
    };

    const before = resolveDiagramLayout(document).nodesById.child;
    const rooted = clearDiagramTreeParent?.(document, "child");

    expect(rooted?.nodes.find((node) => node.id === "child")).toEqual({
      id: "child",
      order: 1,
      mode: "absolute",
      fixed: true,
      x: 8,
      y: 7,
      width: 2,
      height: 1
    });
    expect(rooted ? resolveDiagramLayout(rooted).nodesById.child : null).toMatchObject({
      worldX: before.worldX,
      worldY: before.worldY
    });
  });

  it("moves a selected node while keeping descendants visually fixed", () => {
    const document: DiagramDocument = {
      schemaVersion: 1,
      gridSizePx: 24,
      nodes: [
        { id: "root", order: 0, mode: "absolute", fixed: true, x: 10, y: 4, width: 2, height: 1 },
        { id: "branch", parentId: "root", order: 0, mode: "auto", width: 2, height: 1 },
        { id: "relative-leaf", parentId: "branch", order: 0, mode: "relative", dx: 2, dy: 3, width: 2, height: 1 },
        { id: "auto-leaf", parentId: "branch", order: 1, mode: "auto", width: 2, height: 1 },
        { id: "absolute-leaf", parentId: "branch", order: 2, mode: "absolute", fixed: true, x: 30, y: 12, width: 2, height: 1 },
        { id: "sibling", parentId: "root", order: 1, mode: "absolute", fixed: true, x: 20, y: 8, width: 2, height: 1 }
      ],
      edges: [
        { id: "root-branch", source: "root", target: "branch", kind: "tree" },
        { id: "branch-relative", source: "branch", target: "relative-leaf", kind: "tree" },
        { id: "branch-auto", source: "branch", target: "auto-leaf", kind: "tree" },
        { id: "branch-absolute", source: "branch", target: "absolute-leaf", kind: "tree" },
        { id: "root-sibling", source: "root", target: "sibling", kind: "tree" }
      ]
    };

    const moved = moveDiagramNodeKeepingDescendants(document, "branch", { dx: 3, dy: -2 });

    expect(moved).not.toBe(document);
    expect(moved.nodes).toEqual([
      { id: "root", order: 0, mode: "absolute", fixed: true, x: 10, y: 4, width: 2, height: 1 },
      { id: "branch", parentId: "root", order: 0, mode: "absolute", fixed: true, x: 13, y: 7, width: 2, height: 1 },
      { id: "relative-leaf", parentId: "branch", order: 0, mode: "relative", dx: -1, dy: 5, width: 2, height: 1 },
      { id: "auto-leaf", parentId: "branch", order: 1, mode: "absolute", fixed: true, x: 10, y: 14, width: 2, height: 1 },
      { id: "absolute-leaf", parentId: "branch", order: 2, mode: "absolute", fixed: true, x: 30, y: 12, width: 2, height: 1 },
      { id: "sibling", parentId: "root", order: 1, mode: "absolute", fixed: true, x: 20, y: 8, width: 2, height: 1 }
    ]);
    expect(resolveDiagramLayout(moved).nodesById).toMatchObject({
      branch: { worldX: 13, worldY: 7 },
      "relative-leaf": { worldX: 12, worldY: 12 },
      "auto-leaf": { worldX: 10, worldY: 14 },
      "absolute-leaf": { worldX: 30, worldY: 12 },
      sibling: { worldX: 20, worldY: 8 }
    });
  });

  it("moves a selected node while returning descendants to auto layout", () => {
    const document: DiagramDocument = {
      schemaVersion: 1,
      gridSizePx: 24,
      nodes: [
        { id: "root", order: 0, mode: "absolute", fixed: true, x: 10, y: 4, width: 2, height: 1 },
        { id: "branch", parentId: "root", order: 0, mode: "auto", width: 2, height: 1 },
        { id: "relative-leaf", parentId: "branch", order: 0, mode: "relative", dx: 2, dy: 3, width: 2, height: 1 },
        { id: "auto-leaf", parentId: "branch", order: 1, mode: "auto", width: 2, height: 1 },
        { id: "absolute-leaf", parentId: "branch", order: 2, mode: "absolute", fixed: true, x: 30, y: 12, width: 2, height: 1 },
        { id: "sibling", parentId: "root", order: 1, mode: "absolute", fixed: true, x: 20, y: 8, width: 2, height: 1 }
      ],
      edges: [
        { id: "root-branch", source: "root", target: "branch", kind: "tree" },
        { id: "branch-relative", source: "branch", target: "relative-leaf", kind: "tree" },
        { id: "branch-auto", source: "branch", target: "auto-leaf", kind: "tree" },
        { id: "branch-absolute", source: "branch", target: "absolute-leaf", kind: "tree" },
        { id: "root-sibling", source: "root", target: "sibling", kind: "tree" }
      ]
    };

    const moved = moveDiagramNodeRelayoutDescendants(document, "branch", { dx: 3, dy: -2 });

    expect(moved).not.toBe(document);
    expect(moved.nodes).toEqual([
      { id: "root", order: 0, mode: "absolute", fixed: true, x: 10, y: 4, width: 2, height: 1 },
      { id: "branch", parentId: "root", order: 0, mode: "absolute", fixed: true, x: 13, y: 7, width: 2, height: 1 },
      { id: "relative-leaf", parentId: "branch", order: 0, mode: "auto", width: 2, height: 1 },
      { id: "auto-leaf", parentId: "branch", order: 1, mode: "auto", width: 2, height: 1 },
      { id: "absolute-leaf", parentId: "branch", order: 2, mode: "auto", width: 2, height: 1 },
      { id: "sibling", parentId: "root", order: 1, mode: "absolute", fixed: true, x: 20, y: 8, width: 2, height: 1 }
    ]);
    expect(resolveDiagramLayout(moved).nodesById).toMatchObject({
      branch: { worldX: 13, worldY: 7 },
      "relative-leaf": { worldX: 10, worldY: 12 },
      "auto-leaf": { worldX: 13, worldY: 12 },
      "absolute-leaf": { worldX: 16, worldY: 12 },
      sibling: { worldX: 20, worldY: 8 }
    });
    expect(moveDiagramNodeRelayoutDescendants(document, "missing", { dx: 3, dy: -2 })).toBe(document);
  });

  it("moves HOI4-style focus branches on the icon grid or reflows their descendants", () => {
    const document: DiagramDocument = {
      schemaVersion: 1,
      gridSizePx: 24,
      nodes: [
        { id: "FOCUS_ROOT", order: 0, mode: "absolute", fixed: true, x: 10, y: 0, width: 3, height: 3 },
        { id: "FOCUS_BRANCH", parentId: "FOCUS_ROOT", order: 0, mode: "relative", dx: 4, dy: 5, width: 3, height: 3 },
        { id: "FOCUS_LEAF", parentId: "FOCUS_BRANCH", order: 0, mode: "relative", dx: 0, dy: 5, width: 3, height: 3 },
        { id: "FOCUS_AUTO", parentId: "FOCUS_BRANCH", order: 1, mode: "auto", width: 3, height: 3 },
        { id: "FOCUS_SIBLING", parentId: "FOCUS_ROOT", order: 1, mode: "auto", width: 3, height: 3 }
      ],
      edges: [
        { id: "tree:FOCUS_ROOT->FOCUS_BRANCH", source: "FOCUS_ROOT", target: "FOCUS_BRANCH", kind: "tree" },
        { id: "tree:FOCUS_BRANCH->FOCUS_LEAF", source: "FOCUS_BRANCH", target: "FOCUS_LEAF", kind: "tree" },
        { id: "tree:FOCUS_BRANCH->FOCUS_AUTO", source: "FOCUS_BRANCH", target: "FOCUS_AUTO", kind: "tree" },
        { id: "tree:FOCUS_ROOT->FOCUS_SIBLING", source: "FOCUS_ROOT", target: "FOCUS_SIBLING", kind: "tree" }
      ]
    };

    const movedBranch = moveDiagramSubtree(document, "FOCUS_BRANCH", { dx: 2, dy: 1 });

    expect(movedBranch.nodes).toEqual([
      { id: "FOCUS_ROOT", order: 0, mode: "absolute", fixed: true, x: 10, y: 0, width: 3, height: 3 },
      { id: "FOCUS_BRANCH", parentId: "FOCUS_ROOT", order: 0, mode: "relative", dx: 6, dy: 6, width: 3, height: 3 },
      { id: "FOCUS_LEAF", parentId: "FOCUS_BRANCH", order: 0, mode: "relative", dx: 0, dy: 5, width: 3, height: 3 },
      { id: "FOCUS_AUTO", parentId: "FOCUS_BRANCH", order: 1, mode: "auto", width: 3, height: 3 },
      { id: "FOCUS_SIBLING", parentId: "FOCUS_ROOT", order: 1, mode: "auto", width: 3, height: 3 }
    ]);
    expect(resolveDiagramLayout(movedBranch).nodesById).toMatchObject({
      FOCUS_BRANCH: { worldX: 16, worldY: 6 },
      FOCUS_LEAF: { worldX: 16, worldY: 11 },
      FOCUS_AUTO: { worldX: 20, worldY: 13 }
    });

    const relaidOut = moveDiagramNodeRelayoutDescendants(document, "FOCUS_BRANCH", { dx: -1, dy: 2 });

    expect(relaidOut.nodes).toEqual([
      { id: "FOCUS_ROOT", order: 0, mode: "absolute", fixed: true, x: 10, y: 0, width: 3, height: 3 },
      { id: "FOCUS_BRANCH", parentId: "FOCUS_ROOT", order: 0, mode: "relative", dx: 3, dy: 7, width: 3, height: 3 },
      { id: "FOCUS_LEAF", parentId: "FOCUS_BRANCH", order: 0, mode: "auto", width: 3, height: 3 },
      { id: "FOCUS_AUTO", parentId: "FOCUS_BRANCH", order: 1, mode: "auto", width: 3, height: 3 },
      { id: "FOCUS_SIBLING", parentId: "FOCUS_ROOT", order: 1, mode: "auto", width: 3, height: 3 }
    ]);
    expect(resolveDiagramLayout(relaidOut).nodesById).toMatchObject({
      FOCUS_BRANCH: { worldX: 13, worldY: 7 },
      FOCUS_LEAF: { worldX: 11, worldY: 14 },
      FOCUS_AUTO: { worldX: 15, worldY: 14 }
    });
  });

  it("packs auto children around pinned siblings on the same child row", () => {
    const document: DiagramDocument = {
      schemaVersion: 1,
      gridSizePx: 24,
      nodes: [
        { id: "FOCUS_ROOT", order: 0, mode: "absolute", fixed: true, x: 10, y: 0, width: 2, height: 1 },
        { id: "FOCUS_PINNED", parentId: "FOCUS_ROOT", order: 0, mode: "absolute", fixed: true, x: 10, y: 5, width: 2, height: 1 },
        { id: "FOCUS_RELATIVE", parentId: "FOCUS_ROOT", order: 1, mode: "relative", dx: 3, dy: 5, width: 2, height: 1 },
        { id: "FOCUS_AUTO", parentId: "FOCUS_ROOT", order: 2, mode: "auto", width: 2, height: 1 }
      ],
      edges: [
        { id: "tree:FOCUS_ROOT->FOCUS_PINNED", source: "FOCUS_ROOT", target: "FOCUS_PINNED", kind: "tree" },
        { id: "tree:FOCUS_ROOT->FOCUS_RELATIVE", source: "FOCUS_ROOT", target: "FOCUS_RELATIVE", kind: "tree" },
        { id: "tree:FOCUS_ROOT->FOCUS_AUTO", source: "FOCUS_ROOT", target: "FOCUS_AUTO", kind: "tree" }
      ]
    };

    const resolved = resolveDiagramLayout(document).nodesById;

    expect(resolved.FOCUS_PINNED).toMatchObject({ worldX: 10, worldY: 5 });
    expect(resolved.FOCUS_RELATIVE).toMatchObject({ worldX: 13, worldY: 5 });
    expect(resolved.FOCUS_AUTO).toMatchObject({ worldX: 16, worldY: 5 });
  });

  it("returns a pinned node to auto layout by clearing manual coordinates", () => {
    const document: DiagramDocument = {
      schemaVersion: 1,
      gridSizePx: 24,
      nodes: [
        { id: "root", order: 0, mode: "absolute", fixed: true, x: 0, y: 0, width: 2, height: 1 },
        { id: "left", parentId: "root", order: 0, mode: "absolute", fixed: true, x: 12, y: 8, width: 2, height: 1 },
        { id: "right", parentId: "root", order: 1, mode: "auto", width: 2, height: 1 }
      ],
      edges: [
        { id: "root-left", source: "root", target: "left", kind: "tree" },
        { id: "root-right", source: "root", target: "right", kind: "tree" }
      ]
    };

    const updated = autoLayoutDiagramNode(document, "left");

    expect(updated).not.toBe(document);
    expect(updated.nodes[1]).toEqual({
      id: "left",
      parentId: "root",
      order: 0,
      mode: "auto",
      width: 2,
      height: 1
    });
    expect(resolveDiagramLayout(updated).nodesById.left).toMatchObject({ worldX: -2, worldY: 5 });
    expect(autoLayoutDiagramNode(updated, "left")).toBe(updated);
  });

  it("returns every node to auto layout for full diagram cleanup", () => {
    const document: DiagramDocument = {
      schemaVersion: 1,
      gridSizePx: 24,
      nodes: [
        { id: "root", order: 0, mode: "absolute", fixed: true, x: 10, y: 4, width: 2, height: 1 },
        { id: "left", parentId: "root", order: 0, mode: "absolute", fixed: true, x: 12, y: 8, width: 2, height: 1 },
        { id: "right", parentId: "root", order: 1, mode: "relative", dx: 4, dy: 5, width: 2, height: 1 }
      ],
      edges: [
        { id: "root-left", source: "root", target: "left", kind: "tree" },
        { id: "root-right", source: "root", target: "right", kind: "tree" }
      ]
    };

    const updated = autoLayoutDiagramDocument(document);

    expect(updated).not.toBe(document);
    expect(updated.nodes).toEqual([
      { id: "root", order: 0, mode: "auto", width: 2, height: 1 },
      { id: "left", parentId: "root", order: 0, mode: "auto", width: 2, height: 1 },
      { id: "right", parentId: "root", order: 1, mode: "auto", width: 2, height: 1 }
    ]);
    expect(resolveDiagramLayout(updated).nodesById).toMatchObject({
      root: { worldX: 0, worldY: 0 },
      left: { worldX: -2, worldY: 5 },
      right: { worldX: 1, worldY: 5 }
    });
    expect(autoLayoutDiagramDocument(updated)).toBe(updated);
  });

  it("returns a selected subtree to auto layout without changing siblings", () => {
    const document: DiagramDocument = {
      schemaVersion: 1,
      gridSizePx: 24,
      nodes: [
        { id: "root", order: 0, mode: "absolute", fixed: true, x: 10, y: 4, width: 2, height: 1 },
        { id: "branch", parentId: "root", order: 0, mode: "absolute", fixed: true, x: 12, y: 8, width: 2, height: 1 },
        { id: "leaf", parentId: "branch", order: 0, mode: "relative", fixed: true, dx: 2, dy: 3, width: 2, height: 1 },
        { id: "sibling", parentId: "root", order: 1, mode: "absolute", fixed: true, x: 20, y: 8, width: 2, height: 1 }
      ],
      edges: [
        { id: "root-branch", source: "root", target: "branch", kind: "tree" },
        { id: "branch-leaf", source: "branch", target: "leaf", kind: "tree" },
        { id: "root-sibling", source: "root", target: "sibling", kind: "tree" }
      ]
    };

    const updated = autoLayoutDiagramSubtree(document, "branch");

    expect(updated).not.toBe(document);
    expect(updated.nodes).toEqual([
      { id: "root", order: 0, mode: "absolute", fixed: true, x: 10, y: 4, width: 2, height: 1 },
      { id: "branch", parentId: "root", order: 0, mode: "auto", width: 2, height: 1 },
      { id: "leaf", parentId: "branch", order: 0, mode: "auto", width: 2, height: 1 },
      { id: "sibling", parentId: "root", order: 1, mode: "absolute", fixed: true, x: 20, y: 8, width: 2, height: 1 }
    ]);
    expect(autoLayoutDiagramSubtree(updated, "branch")).toBe(updated);
  });

  it("returns selected descendants to auto layout without changing the selected node or siblings", () => {
    const document: DiagramDocument = {
      schemaVersion: 1,
      gridSizePx: 24,
      nodes: [
        { id: "root", order: 0, mode: "absolute", fixed: true, x: 10, y: 4, width: 2, height: 1 },
        { id: "branch", parentId: "root", order: 0, mode: "absolute", fixed: true, x: 12, y: 8, width: 2, height: 1 },
        { id: "leaf", parentId: "branch", order: 0, mode: "relative", fixed: true, dx: 2, dy: 3, width: 2, height: 1 },
        { id: "bud", parentId: "leaf", order: 0, mode: "absolute", fixed: true, x: 30, y: 12, width: 2, height: 1 },
        { id: "sibling", parentId: "root", order: 1, mode: "absolute", fixed: true, x: 20, y: 8, width: 2, height: 1 }
      ],
      edges: [
        { id: "root-branch", source: "root", target: "branch", kind: "tree" },
        { id: "branch-leaf", source: "branch", target: "leaf", kind: "tree" },
        { id: "leaf-bud", source: "leaf", target: "bud", kind: "tree" },
        { id: "root-sibling", source: "root", target: "sibling", kind: "tree" }
      ]
    };

    const updated = autoLayoutDiagramDescendants(document, "branch");

    expect(updated).not.toBe(document);
    expect(updated.nodes).toEqual([
      { id: "root", order: 0, mode: "absolute", fixed: true, x: 10, y: 4, width: 2, height: 1 },
      { id: "branch", parentId: "root", order: 0, mode: "absolute", fixed: true, x: 12, y: 8, width: 2, height: 1 },
      { id: "leaf", parentId: "branch", order: 0, mode: "auto", width: 2, height: 1 },
      { id: "bud", parentId: "leaf", order: 0, mode: "auto", width: 2, height: 1 },
      { id: "sibling", parentId: "root", order: 1, mode: "absolute", fixed: true, x: 20, y: 8, width: 2, height: 1 }
    ]);
    expect(resolveDiagramLayout(updated).nodesById.branch).toMatchObject({ worldX: 12, worldY: 8 });
    expect(autoLayoutDiagramDescendants(updated, "branch")).toBe(updated);
    expect(autoLayoutDiagramDescendants(document, "missing")).toBe(document);
  });

  it("unpins every node by returning the diagram to auto layout", () => {
    const document: DiagramDocument = {
      schemaVersion: 1,
      gridSizePx: 24,
      nodes: [
        { id: "root", order: 0, mode: "absolute", fixed: true, x: 10, y: 4, width: 2, height: 1 },
        { id: "left", parentId: "root", order: 0, mode: "absolute", fixed: true, x: 12, y: 8, width: 2, height: 1 },
        { id: "right", parentId: "root", order: 1, mode: "relative", dx: 4, dy: 5, width: 2, height: 1 }
      ],
      edges: [
        { id: "root-left", source: "root", target: "left", kind: "tree" },
        { id: "root-right", source: "root", target: "right", kind: "tree" }
      ]
    };

    const updated = unpinDiagramDocument(document);

    expect(updated).not.toBe(document);
    expect(updated).toEqual(autoLayoutDiagramDocument(document));
    expect(unpinDiagramDocument(updated)).toBe(updated);
  });

  it("unpins a selected node without changing descendant or sibling layout modes", () => {
    const document: DiagramDocument = {
      schemaVersion: 1,
      gridSizePx: 24,
      nodes: [
        { id: "root", order: 0, mode: "absolute", fixed: true, x: 10, y: 4, width: 2, height: 1 },
        { id: "branch", parentId: "root", order: 0, mode: "absolute", fixed: true, x: 12, y: 8, width: 2, height: 1 },
        { id: "leaf", parentId: "branch", order: 0, mode: "relative", dx: 2, dy: 3, width: 2, height: 1 },
        { id: "sibling", parentId: "root", order: 1, mode: "absolute", fixed: true, x: 20, y: 8, width: 2, height: 1 }
      ],
      edges: [
        { id: "root-branch", source: "root", target: "branch", kind: "tree" },
        { id: "branch-leaf", source: "branch", target: "leaf", kind: "tree" },
        { id: "root-sibling", source: "root", target: "sibling", kind: "tree" }
      ]
    };

    const updated = unpinDiagramSelectedNode(document, "branch");

    expect(updated.nodes).toEqual([
      { id: "root", order: 0, mode: "absolute", fixed: true, x: 10, y: 4, width: 2, height: 1 },
      { id: "branch", parentId: "root", order: 0, mode: "auto", width: 2, height: 1 },
      { id: "leaf", parentId: "branch", order: 0, mode: "relative", dx: 2, dy: 3, width: 2, height: 1 },
      { id: "sibling", parentId: "root", order: 1, mode: "absolute", fixed: true, x: 20, y: 8, width: 2, height: 1 }
    ]);
    expect(unpinDiagramSelectedNode(updated, "branch")).toBe(updated);
    expect(unpinDiagramSelectedNode(updated, "missing")).toBe(updated);
  });

  it("unpins a selected subtree without changing sibling layout modes", () => {
    const document: DiagramDocument = {
      schemaVersion: 1,
      gridSizePx: 24,
      nodes: [
        { id: "root", order: 0, mode: "absolute", fixed: true, x: 10, y: 4, width: 2, height: 1 },
        { id: "branch", parentId: "root", order: 0, mode: "absolute", fixed: true, x: 12, y: 8, width: 2, height: 1 },
        { id: "leaf", parentId: "branch", order: 0, mode: "relative", dx: 2, dy: 3, width: 2, height: 1 },
        { id: "sibling", parentId: "root", order: 1, mode: "absolute", fixed: true, x: 20, y: 8, width: 2, height: 1 }
      ],
      edges: [
        { id: "root-branch", source: "root", target: "branch", kind: "tree" },
        { id: "branch-leaf", source: "branch", target: "leaf", kind: "tree" },
        { id: "root-sibling", source: "root", target: "sibling", kind: "tree" }
      ]
    };

    const updated = unpinDiagramSubtree(document, "branch");

    expect(updated.nodes).toEqual([
      { id: "root", order: 0, mode: "absolute", fixed: true, x: 10, y: 4, width: 2, height: 1 },
      { id: "branch", parentId: "root", order: 0, mode: "auto", width: 2, height: 1 },
      { id: "leaf", parentId: "branch", order: 0, mode: "auto", width: 2, height: 1 },
      { id: "sibling", parentId: "root", order: 1, mode: "absolute", fixed: true, x: 20, y: 8, width: 2, height: 1 }
    ]);
    expect(unpinDiagramSubtree(updated, "branch")).toBe(updated);
    expect(unpinDiagramSubtree(updated, "missing")).toBe(updated);
  });

  it("pins every node to its resolved world position", () => {
    const document: DiagramDocument = {
      schemaVersion: 1,
      gridSizePx: 24,
      nodes: [
        { id: "root", order: 0, mode: "auto", width: 2, height: 1 },
        { id: "left", parentId: "root", order: 0, mode: "auto", width: 2, height: 1 },
        { id: "right", parentId: "root", order: 1, mode: "relative", dx: 4, dy: 5, width: 2, height: 1 }
      ],
      edges: [
        { id: "root-left", source: "root", target: "left", kind: "tree" },
        { id: "root-right", source: "root", target: "right", kind: "tree" }
      ]
    };

    const pinned = pinDiagramDocument(document);

    expect(pinned).not.toBe(document);
    expect(pinned.nodes).toEqual([
      { id: "root", order: 0, mode: "absolute", fixed: true, x: 0, y: 0, width: 2, height: 1 },
      { id: "left", parentId: "root", order: 0, mode: "absolute", fixed: true, x: 0, y: 5, width: 2, height: 1 },
      { id: "right", parentId: "root", order: 1, mode: "absolute", fixed: true, x: 4, y: 5, width: 2, height: 1 }
    ]);
    expect(pinDiagramDocument(pinned)).toBe(pinned);
  });

  it("pins a selected node without changing descendant or sibling layout modes", () => {
    const document: DiagramDocument = {
      schemaVersion: 1,
      gridSizePx: 24,
      nodes: [
        { id: "root", order: 0, mode: "auto", width: 2, height: 1 },
        { id: "branch", parentId: "root", order: 0, mode: "auto", width: 2, height: 1 },
        { id: "leaf", parentId: "branch", order: 0, mode: "auto", width: 2, height: 1 },
        { id: "sibling", parentId: "root", order: 1, mode: "auto", width: 2, height: 1 }
      ],
      edges: [
        { id: "root-branch", source: "root", target: "branch", kind: "tree" },
        { id: "branch-leaf", source: "branch", target: "leaf", kind: "tree" },
        { id: "root-sibling", source: "root", target: "sibling", kind: "tree" }
      ]
    };

    const pinned = pinDiagramSelectedNode(document, "branch");

    expect(pinned).not.toBe(document);
    expect(pinned.nodes).toEqual([
      { id: "root", order: 0, mode: "auto", width: 2, height: 1 },
      { id: "branch", parentId: "root", order: 0, mode: "absolute", fixed: true, x: -2, y: 5, width: 2, height: 1 },
      { id: "leaf", parentId: "branch", order: 0, mode: "auto", width: 2, height: 1 },
      { id: "sibling", parentId: "root", order: 1, mode: "auto", width: 2, height: 1 }
    ]);
    expect(pinDiagramSelectedNode(pinned, "branch")).toBe(pinned);
    expect(pinDiagramSelectedNode(pinned, "missing")).toBe(pinned);
  });

  it("pins a selected subtree without changing sibling layout modes", () => {
    const document: DiagramDocument = {
      schemaVersion: 1,
      gridSizePx: 24,
      nodes: [
        { id: "root", order: 0, mode: "auto", width: 2, height: 1 },
        { id: "branch", parentId: "root", order: 0, mode: "auto", width: 2, height: 1 },
        { id: "leaf", parentId: "branch", order: 0, mode: "auto", width: 2, height: 1 },
        { id: "sibling", parentId: "root", order: 1, mode: "auto", width: 2, height: 1 }
      ],
      edges: [
        { id: "root-branch", source: "root", target: "branch", kind: "tree" },
        { id: "branch-leaf", source: "branch", target: "leaf", kind: "tree" },
        { id: "root-sibling", source: "root", target: "sibling", kind: "tree" }
      ]
    };

    const pinned = pinDiagramSubtree(document, "branch");

    expect(pinned).not.toBe(document);
    expect(pinned.nodes).toEqual([
      { id: "root", order: 0, mode: "auto", width: 2, height: 1 },
      { id: "branch", parentId: "root", order: 0, mode: "absolute", fixed: true, x: -2, y: 5, width: 2, height: 1 },
      { id: "leaf", parentId: "branch", order: 0, mode: "absolute", fixed: true, x: -2, y: 10, width: 2, height: 1 },
      { id: "sibling", parentId: "root", order: 1, mode: "auto", width: 2, height: 1 }
    ]);
    expect(pinDiagramSubtree(pinned, "branch")).toBe(pinned);
  });

  it("converts canvas drag distance to snapped grid delta", () => {
    expect(dragDeltaToGrid({ x: 0, y: 0 }, { x: 49, y: -25 }, 24)).toEqual({ dx: 2, dy: -1 });
    expect(dragDeltaToGrid({ x: 90, y: 24 }, { x: 79, y: 35 }, 24)).toEqual({ dx: 0, dy: 0 });
  });

  it("keeps a diagram unchanged when moving an unknown node", () => {
    const document: DiagramDocument = {
      schemaVersion: 1,
      gridSizePx: 24,
      nodes: [{ id: "root", order: 0, mode: "absolute", x: 1, y: 2, width: 2, height: 1 }],
      edges: []
    };

    expect(moveDiagramNode(document, "missing", { dx: 1, dy: 1 })).toBe(document);
  });

  it("rejects nodes whose parent cannot be resolved", () => {
    const document: DiagramDocument = {
      schemaVersion: 1,
      gridSizePx: 24,
      nodes: [{ id: "orphan", parentId: "missing", order: 0, mode: "auto", width: 2, height: 1 }],
      edges: []
    };

    expect(() => resolveDiagramLayout(document)).toThrow("Diagram node orphan references missing parent missing.");
  });

  it("rejects cyclic parent chains without a root", () => {
    const document: DiagramDocument = {
      schemaVersion: 1,
      gridSizePx: 24,
      nodes: [
        { id: "alpha", parentId: "beta", order: 0, mode: "auto", width: 2, height: 1 },
        { id: "beta", parentId: "alpha", order: 1, mode: "auto", width: 2, height: 1 }
      ],
      edges: []
    };

    expect(() => resolveDiagramLayout(document)).toThrow("Diagram document has no root nodes; check parent links for cycles.");
  });
});
