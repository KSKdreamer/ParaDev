import type { DiagramDocument } from "./layoutModel";

export type DiagramHistory = {
  future: DiagramDocument[];
  past: DiagramDocument[];
  present: DiagramDocument | null;
};

export type DiagramHistoryUpdateResult = {
  changed: boolean;
  history: DiagramHistory;
};

export type DiagramHistoryUpdater = (current: DiagramDocument) => DiagramDocument;

/** Maximum full-document checkpoints retained on either side of the cursor. */
export const DIAGRAM_HISTORY_LIMIT = 100;

export function createDiagramHistory(present: DiagramDocument | null): DiagramHistory {
  return {
    future: [],
    past: [],
    present
  };
}

export function canUndoDiagramHistory(history: DiagramHistory): boolean {
  return history.past.length > 0;
}

export function canRedoDiagramHistory(history: DiagramHistory): boolean {
  return history.future.length > 0;
}

/** Stable identity for the source-backed document a draft was based on. */
export function diagramDocumentFingerprint(
  document: DiagramDocument | null
): string {
  return stableDiagramStringify(document);
}

export function pushDiagramHistory(history: DiagramHistory, next: DiagramDocument): DiagramHistory {
  if (!history.present) {
    return createDiagramHistory(next);
  }
  if (sameDiagramDocument(history.present, next)) {
    return history;
  }
  return {
    future: [],
    past: appendBoundedDiagram(history.past, history.present),
    present: next
  };
}

export function applyDiagramHistoryUpdate(history: DiagramHistory, base: DiagramDocument | null, update: DiagramHistoryUpdater): DiagramHistoryUpdateResult {
  const current = history.present ?? base;
  if (!current) {
    return { changed: false, history };
  }
  const seed = history.present ? history : createDiagramHistory(current);
  const next = update(current);
  const updated = pushDiagramHistory(seed, next);
  return updated === seed ? { changed: false, history } : { changed: true, history: updated };
}

export function applyDiagramPresentUpdate(history: DiagramHistory, base: DiagramDocument | null, update: DiagramHistoryUpdater): DiagramHistoryUpdateResult {
  const current = history.present ?? base;
  if (!current) {
    return { changed: false, history };
  }
  const next = update(current);
  if (sameDiagramDocument(current, next)) {
    return { changed: false, history };
  }
  return {
    changed: true,
    history: {
      ...history,
      present: next
    }
  };
}

export function undoDiagramHistory(history: DiagramHistory): DiagramHistory {
  if (!canUndoDiagramHistory(history)) {
    return history;
  }
  const present = history.past[history.past.length - 1];
  return {
    future: history.present
      ? [history.present, ...history.future].slice(0, DIAGRAM_HISTORY_LIMIT)
      : history.future.slice(0, DIAGRAM_HISTORY_LIMIT),
    past: history.past.slice(0, -1),
    present
  };
}

export function redoDiagramHistory(history: DiagramHistory): DiagramHistory {
  if (!canRedoDiagramHistory(history)) {
    return history;
  }
  const [present, ...future] = history.future;
  return {
    future,
    past: history.present
      ? appendBoundedDiagram(history.past, history.present)
      : history.past.slice(-DIAGRAM_HISTORY_LIMIT),
    present
  };
}

function appendBoundedDiagram(
  documents: readonly DiagramDocument[],
  document: DiagramDocument
): DiagramDocument[] {
  return [...documents, document].slice(-DIAGRAM_HISTORY_LIMIT);
}

function sameDiagramDocument(left: DiagramDocument, right: DiagramDocument): boolean {
  return diagramDocumentFingerprint(left) === diagramDocumentFingerprint(right);
}

function stableDiagramStringify(value: unknown): string {
  if (Array.isArray(value)) {
    return `[${value.map((item) => stableDiagramStringify(item)).join(",")}]`;
  }
  if (value && typeof value === "object") {
    const record = value as Record<string, unknown>;
    return `{${Object.keys(record)
      .sort()
      .filter((key) => record[key] !== undefined)
      .map((key) => `${JSON.stringify(key)}:${stableDiagramStringify(record[key])}`)
      .join(",")}}`;
  }
  return JSON.stringify(value) ?? "null";
}
