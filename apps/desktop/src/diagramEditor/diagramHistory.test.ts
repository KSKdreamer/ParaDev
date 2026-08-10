import { describe, expect, it } from "vitest";
import { applyDiagramHistoryUpdate, applyDiagramPresentUpdate, canRedoDiagramHistory, canUndoDiagramHistory, createDiagramHistory, DIAGRAM_HISTORY_LIMIT, pushDiagramHistory, redoDiagramHistory, undoDiagramHistory } from "./diagramHistory";
import type { DiagramDocument } from "./layoutModel";

const baseDocument: DiagramDocument = {
  schemaVersion: 1,
  gridSizePx: 24,
  nodes: [{ id: "ROOT", order: 0, mode: "absolute", fixed: true, x: 0, y: 0, width: 4, height: 2 }],
  edges: []
};

const movedDocument: DiagramDocument = {
  ...baseDocument,
  nodes: [{ id: "ROOT", order: 0, mode: "absolute", fixed: true, x: 2, y: 1, width: 4, height: 2 }]
};

const nextDocument: DiagramDocument = {
  ...baseDocument,
  nodes: [{ id: "ROOT", order: 0, mode: "absolute", fixed: true, x: 4, y: 1, width: 4, height: 2 }]
};

function documentAt(x: number): DiagramDocument {
  return {
    ...baseDocument,
    nodes: [{ ...baseDocument.nodes[0], x }]
  };
}

describe("diagram history", () => {
  it("bounds full-document checkpoints for long editing sessions", () => {
    let history = createDiagramHistory(documentAt(0));

    for (let index = 1; index <= DIAGRAM_HISTORY_LIMIT + 5; index += 1) {
      history = pushDiagramHistory(history, documentAt(index));
    }

    expect(history.past).toHaveLength(DIAGRAM_HISTORY_LIMIT);
    expect(history.past[0]?.nodes[0]?.x).toBe(5);
    for (let index = 0; index < DIAGRAM_HISTORY_LIMIT; index += 1) {
      history = undoDiagramHistory(history);
    }
    expect(history.past).toHaveLength(0);
    expect(history.future).toHaveLength(DIAGRAM_HISTORY_LIMIT);
    expect(history.present?.nodes[0]?.x).toBe(5);
    expect(undoDiagramHistory(history)).toBe(history);
  });

  it("pushes diagram snapshots and walks backward and forward", () => {
    const base = createDiagramHistory(baseDocument);
    const moved = pushDiagramHistory(base, movedDocument);
    const next = pushDiagramHistory(moved, nextDocument);

    expect(canUndoDiagramHistory(next)).toBe(true);
    expect(canRedoDiagramHistory(next)).toBe(false);
    expect(next.past).toHaveLength(2);
    expect(next.present).toBe(nextDocument);

    const undone = undoDiagramHistory(next);
    expect(undone.present).toBe(movedDocument);
    expect(canRedoDiagramHistory(undone)).toBe(true);

    const redone = redoDiagramHistory(undone);
    expect(redone.present).toBe(nextDocument);
    expect(redone.future).toHaveLength(0);
  });

  it("does not create a history entry for unchanged documents", () => {
    const base = createDiagramHistory(baseDocument);
    const unchanged = pushDiagramHistory(base, { ...baseDocument });

    expect(unchanged).toBe(base);
  });

  it("does not create a history entry when object keys are reordered", () => {
    const base = createDiagramHistory(baseDocument);
    const reordered: DiagramDocument = {
      edges: [],
      gridSizePx: 24,
      nodes: [{ fixed: true, height: 2, id: "ROOT", mode: "absolute", order: 0, width: 4, x: 0, y: 0 }],
      schemaVersion: 1
    };

    expect(pushDiagramHistory(base, reordered)).toBe(base);
  });

  it("reports whether an update changes a clean base document", () => {
    const emptyHistory = createDiagramHistory(null);
    const unchanged = applyDiagramHistoryUpdate(emptyHistory, baseDocument, (current) => current);

    expect(unchanged.changed).toBe(false);
    expect(unchanged.history).toBe(emptyHistory);

    const moved = applyDiagramHistoryUpdate(emptyHistory, baseDocument, () => movedDocument);

    expect(moved.changed).toBe(true);
    expect(moved.history.present).toBe(movedDocument);
    expect(moved.history.past).toEqual([baseDocument]);
  });

  it("updates viewport state without adding undo entries", () => {
    const emptyHistory = createDiagramHistory(null);
    const viewportDocument: DiagramDocument = { ...baseDocument, viewport: { x: 24, y: -12, zoom: 1.5 } };
    const cleanViewport = applyDiagramPresentUpdate(emptyHistory, baseDocument, () => viewportDocument);

    expect(cleanViewport.changed).toBe(true);
    expect(cleanViewport.history.present).toBe(viewportDocument);
    expect(cleanViewport.history.past).toEqual([]);
    expect(canUndoDiagramHistory(cleanViewport.history)).toBe(false);

    const moved = applyDiagramHistoryUpdate(cleanViewport.history, baseDocument, () => movedDocument);
    const movedViewportDocument: DiagramDocument = { ...movedDocument, viewport: { x: 48, y: 0, zoom: 2 } };
    const movedViewport = applyDiagramPresentUpdate(moved.history, baseDocument, () => movedViewportDocument);

    expect(movedViewport.changed).toBe(true);
    expect(movedViewport.history.present).toBe(movedViewportDocument);
    expect(movedViewport.history.past).toEqual([viewportDocument]);
    expect(canUndoDiagramHistory(movedViewport.history)).toBe(true);
  });
});
