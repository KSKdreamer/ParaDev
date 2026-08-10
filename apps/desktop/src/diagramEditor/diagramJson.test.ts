import { describe, expect, it } from "vitest";
import { exportDiagramJson, importDiagramJson } from "./diagramJson";
import type { DiagramDocument } from "./layoutModel";

const document: DiagramDocument = {
  schemaVersion: 1,
  gridSizePx: 24,
  nodes: [
    { id: "ROOT", order: 0, mode: "absolute", fixed: true, x: 0, y: 0, width: 4, height: 2, title: "Root Focus" },
    { id: "CHILD", parentId: "ROOT", order: 1, mode: "auto", width: 4, height: 2, title: "Child Focus" }
  ],
  edges: [{ id: "tree:ROOT->CHILD", source: "ROOT", target: "CHILD", kind: "tree" }]
};

describe("diagram JSON import and export", () => {
  it("exports canonical diagram JSON with a stable trailing newline", () => {
    const json = exportDiagramJson(document);

    expect(json).toBe(`${JSON.stringify(document, null, 2)}\n`);
  });

  it("imports valid canonical diagram JSON", () => {
    expect(importDiagramJson(exportDiagramJson(document))).toEqual(document);
  });

  it("preserves optional legacy layout hints on imported nodes", () => {
    const hinted: DiagramDocument = {
      ...document,
      nodes: [
        { ...document.nodes[0], priority: 20, subtreeWidth: 8, subtreeWidthDelta: -2, subtreeCenterOffset: 1 },
        { ...document.nodes[1], mode: "relative", dx: 1, dy: 2, relativePositionKind: "legacy_offset" }
      ]
    };

    expect(importDiagramJson(exportDiagramJson(hinted))).toEqual(hinted);
  });

  it("preserves document-level layout options for focus-row spacing", () => {
    const compact: DiagramDocument = {
      ...document,
      layoutOptions: { layerGap: 0, siblingGap: 1 }
    };

    expect(importDiagramJson(exportDiagramJson(compact))).toEqual(compact);
  });

  it("rejects malformed diagram JSON with contextual errors", () => {
    expect(() => importDiagramJson("{")).toThrow("Diagram JSON is not valid JSON.");
    expect(() => importDiagramJson(JSON.stringify({ ...document, schemaVersion: 2 }))).toThrow("Diagram JSON schemaVersion must be 1.");
    expect(() => importDiagramJson(JSON.stringify({ ...document, nodes: [{ ...document.nodes[0], mode: "pinned" }] }))).toThrow("Diagram node ROOT has unsupported mode pinned.");
    expect(() => importDiagramJson(JSON.stringify({ ...document, edges: [{ ...document.edges[0], target: "MISSING" }] }))).toThrow("Diagram edge tree:ROOT->CHILD references missing target MISSING.");
  });

  it("rejects imported diagram nodes with non-positive dimensions", () => {
    expect(() => importDiagramJson(JSON.stringify({ ...document, nodes: [{ ...document.nodes[0], width: 0 }, document.nodes[1]] }))).toThrow("Diagram node ROOT width must be positive.");
    expect(() => importDiagramJson(JSON.stringify({ ...document, nodes: [{ ...document.nodes[0], height: 0 }, document.nodes[1]] }))).toThrow("Diagram node ROOT height must be positive.");
  });

  it("rejects imported diagram viewports with non-positive zoom", () => {
    expect(() => importDiagramJson(JSON.stringify({ ...document, viewport: { x: 0, y: 0, zoom: 0 } }))).toThrow("Diagram viewport zoom must be positive.");
  });

  it("rejects imported diagram viewports that are not objects", () => {
    expect(() => importDiagramJson(JSON.stringify({ ...document, viewport: "centered" }))).toThrow("Diagram viewport must be an object.");
  });

  it("rejects imported diagram layout options that are not objects", () => {
    expect(() => importDiagramJson(JSON.stringify({ ...document, layoutOptions: "compact" }))).toThrow("Diagram layoutOptions must be an object.");
    expect(() => importDiagramJson(JSON.stringify({ ...document, layoutOptions: { layerGap: "tight" } }))).toThrow("Diagram layoutOptions layerGap must be numeric.");
  });

  it("rejects dependency cycles in imported diagram JSON", () => {
    const cyclic: DiagramDocument = {
      ...document,
      nodes: [...document.nodes, { id: "LEAF", parentId: "CHILD", order: 0, mode: "auto", width: 4, height: 2, title: "Leaf Focus" }],
      edges: [
        ...document.edges,
        { id: "tree:CHILD->LEAF", source: "CHILD", target: "LEAF", kind: "tree" },
        { id: "dependency:ROOT->CHILD", source: "ROOT", target: "CHILD", kind: "dependency" },
        { id: "dependency:CHILD->LEAF", source: "CHILD", target: "LEAF", kind: "dependency" },
        { id: "dependency:LEAF->ROOT", source: "LEAF", target: "ROOT", kind: "dependency" }
      ]
    };

    expect(() => importDiagramJson(JSON.stringify(cyclic))).toThrow("Diagram dependency edge dependency:LEAF->ROOT creates a cycle.");
  });

  it("rejects tree edges that disagree with imported parent ids", () => {
    const mismatched: DiagramDocument = {
      ...document,
      nodes: [...document.nodes, { id: "ALT_PARENT", order: 2, mode: "absolute", fixed: true, x: 8, y: 0, width: 4, height: 2, title: "Alt Parent" }],
      edges: [{ id: "tree:ALT_PARENT->CHILD", source: "ALT_PARENT", target: "CHILD", kind: "tree" }]
    };

    expect(() => importDiagramJson(JSON.stringify(mismatched))).toThrow("Diagram tree edge tree:ALT_PARENT->CHILD disagrees with parent ROOT for node CHILD.");
  });

  it("rejects imported parent ids without matching tree edges", () => {
    const missingTreeEdge: DiagramDocument = {
      ...document,
      edges: []
    };

    expect(() => importDiagramJson(JSON.stringify(missingTreeEdge))).toThrow("Diagram node CHILD has parent ROOT but no matching tree edge.");
  });

  it("rejects imported diagram edges with duplicate ids", () => {
    const duplicateEdgeId: DiagramDocument = {
      ...document,
      edges: [...document.edges, document.edges[0]]
    };

    expect(() => importDiagramJson(JSON.stringify(duplicateEdgeId))).toThrow("Diagram JSON edges must have unique ids.");
  });

  it("rejects imported diagram edges with non-canonical ids", () => {
    const mismatchedEdgeId: DiagramDocument = {
      ...document,
      edges: [...document.edges, { id: "dependency:ROOT->CHILD:renamed", source: "ROOT", target: "CHILD", kind: "dependency" }]
    };

    expect(() => importDiagramJson(JSON.stringify(mismatchedEdgeId))).toThrow("Diagram edge dependency:ROOT->CHILD:renamed must use canonical id dependency:ROOT->CHILD.");
  });

  it("rejects imported diagram edges that target themselves", () => {
    const selfTargetingEdge: DiagramDocument = {
      ...document,
      edges: [...document.edges, { id: "reference:ROOT->ROOT", source: "ROOT", target: "ROOT", kind: "reference" }]
    };

    expect(() => importDiagramJson(JSON.stringify(selfTargetingEdge))).toThrow("Diagram edge reference:ROOT->ROOT cannot target itself.");
  });

  it("rejects imported diagram edges with duplicate relationships", () => {
    const duplicateRelationship: DiagramDocument = {
      ...document,
      edges: [
        ...document.edges,
        { id: "dependency:ROOT->CHILD", source: "ROOT", target: "CHILD", kind: "dependency" },
        { id: "dependency:ROOT->CHILD:copy", source: "ROOT", target: "CHILD", kind: "dependency" }
      ]
    };

    expect(() => importDiagramJson(JSON.stringify(duplicateRelationship))).toThrow("Diagram JSON edges must have unique kind/source/target relationships.");
  });
});
