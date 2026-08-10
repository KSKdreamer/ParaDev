import { describe, expect, it } from "vitest";
import { createDiagramHistory } from "./diagramHistory";
import { exportDiagramJson } from "./diagramJson";
import { importDiagramJsonDraft } from "./diagramJsonImport";
import { createTranslator } from "../i18n";
import type { DiagramDocument } from "./layoutModel";

const baseDocument: DiagramDocument = {
  schemaVersion: 1,
  gridSizePx: 24,
  nodes: [
    {
      id: "ROOT",
      order: 0,
      mode: "absolute",
      fixed: true,
      x: 0,
      y: 0,
      width: 4,
      height: 2,
      title: "Root Focus",
      payload: { itemId: "focus_tree:C08", objectId: "C08", embeddedId: "ROOT", embeddedKind: "focus" }
    },
    {
      id: "CHILD",
      parentId: "ROOT",
      order: 1,
      mode: "auto",
      width: 4,
      height: 2,
      title: "Child Focus",
      payload: { itemId: "focus_tree:C08", objectId: "C08", embeddedId: "CHILD", embeddedKind: "focus" }
    }
  ],
  edges: [{ id: "tree:ROOT->CHILD", source: "ROOT", target: "CHILD", kind: "tree" }]
};

const importedDocument: DiagramDocument = {
  ...baseDocument,
  nodes: [
    baseDocument.nodes[0],
    { ...baseDocument.nodes[1], mode: "absolute", fixed: true, x: 3, y: 8 }
  ]
};

function technologyDiagramDocument(): DiagramDocument {
  return {
    schemaVersion: 1,
    gridSizePx: 24,
    nodes: [
      {
        id: "TECH_FIREARM",
        order: 0,
        mode: "absolute",
        fixed: true,
        x: 4,
        y: 3,
        width: 6,
        height: 2,
        title: "Firearm",
        payload: {
          projectId: "PIHC3",
          itemId: "technology:TECH_FIREARM",
          itemKind: "module",
          familyId: "technology",
          family: "technology",
          objectId: "TECH_FIREARM",
          moduleId: "TECH_FIREARM",
          relativeRoot: "src/modules/technology/TECH_FIREARM"
        }
      }
    ],
    edges: []
  };
}

function emptyFocusTreeContextDocument(): DiagramDocument {
  return {
    schemaVersion: 1,
    gridSizePx: 24,
    nodes: [
      {
        id: "C08_PARTIV",
        order: 0,
        mode: "auto",
        width: 6,
        height: 2,
        title: "C08 Part IV",
        payload: {
          projectId: "PIHC3",
          itemId: "focus_tree:C08_PARTIV",
          itemKind: "module",
          familyId: "focuses",
          family: "focus_tree",
          objectId: "C08_PARTIV",
          moduleId: "C08_PARTIV",
          relativeRoot: "src/modules/focus_tree/C08_PARTIV",
          sourceRootRelativePath: "src/modules/focus_tree/C08_PARTIV"
        }
      }
    ],
    edges: []
  };
}

describe("diagram JSON draft import", () => {
  it("imports changed JSON as a normal diagram history draft", () => {
    const history = createDiagramHistory(null);
    const result = importDiagramJsonDraft(history, baseDocument, exportDiagramJson(importedDocument));

    expect(result).toMatchObject({ changed: true, ok: true });
    if (!result.ok) {
      throw new Error(result.error);
    }
    expect(result.document).toEqual(importedDocument);
    expect(result.history.present).toEqual(importedDocument);
    expect(result.history.past).toEqual([baseDocument]);
  });

  it("ignores JSON imports that match the current diagram", () => {
    const history = createDiagramHistory(null);
    const result = importDiagramJsonDraft(history, baseDocument, exportDiagramJson(baseDocument));

    expect(result).toMatchObject({ changed: false, ok: true });
    expect(result.history).toBe(history);
  });

  it("returns parse errors without changing history", () => {
    const history = createDiagramHistory(baseDocument);
    const result = importDiagramJsonDraft(history, baseDocument, "{");

    expect(result).toEqual({
      ok: false,
      changed: false,
      error: "Diagram JSON is not valid JSON.",
      history
    });
  });

  it("localizes parse and compatibility errors for GUI imports", () => {
    const history = createDiagramHistory(baseDocument);
    const t = createTranslator("zh");
    const missingPayload = {
      ...baseDocument,
      nodes: [{ ...baseDocument.nodes[0], payload: undefined }, baseDocument.nodes[1]]
    };

    expect(importDiagramJsonDraft(history, baseDocument, "{", t)).toEqual({
      ok: false,
      changed: false,
      error: "图谱 JSON 不是有效的 JSON。",
      history
    });
    expect(importDiagramJsonDraft(history, baseDocument, exportDiagramJson(missingPayload), t)).toEqual({
      ok: false,
      changed: false,
      error: "导入的图谱节点 ROOT 缺少 ParaDev 元数据 payload。",
      history
    });
  });

  it("rejects imports that cannot target the current project metadata", () => {
    const history = createDiagramHistory(baseDocument);
    const missingPayload = {
      ...baseDocument,
      nodes: [{ ...baseDocument.nodes[0], payload: undefined }, baseDocument.nodes[1]]
    };
    const remappedPayload = {
      ...baseDocument,
      nodes: [baseDocument.nodes[0], { ...baseDocument.nodes[1], payload: { itemId: "focus_tree:C09", objectId: "C09", embeddedId: "CHILD", embeddedKind: "focus" } }]
    };
    const foreignObjectPayload = {
      ...baseDocument,
      nodes: [
        ...baseDocument.nodes,
        {
          id: "FOREIGN_CHILD",
          parentId: "ROOT",
          order: 2,
          mode: "auto" as const,
          width: 4,
          height: 2,
          title: "Foreign Child",
          payload: { itemId: "focus_tree:C08", objectId: "C09", embeddedId: "FOREIGN_CHILD", embeddedKind: "focus" }
        }
      ],
      edges: [...baseDocument.edges, { id: "tree:ROOT->FOREIGN_CHILD", source: "ROOT", target: "FOREIGN_CHILD", kind: "tree" as const }]
    };

    expect(importDiagramJsonDraft(history, baseDocument, exportDiagramJson(missingPayload))).toEqual({
      ok: false,
      changed: false,
      error: "Imported diagram node ROOT is missing ParaDev metadata payload.",
      history
    });
    expect(importDiagramJsonDraft(history, baseDocument, exportDiagramJson(remappedPayload))).toEqual({
      ok: false,
      changed: false,
      error: "Imported diagram node CHILD targets metadata entity focus_tree:C09 outside the current diagram.",
      history
    });
    expect(importDiagramJsonDraft(history, baseDocument, exportDiagramJson(foreignObjectPayload))).toEqual({
      ok: false,
      changed: false,
      error: "Imported diagram node FOREIGN_CHILD targets metadata object C09 outside focus_tree:C08.",
      history
    });
  });

  it("rejects imports whose focus payload embedded id disagrees with the node id", () => {
    const history = createDiagramHistory(baseDocument);
    const mismatchedEmbeddedId = {
      ...baseDocument,
      nodes: [baseDocument.nodes[0], { ...baseDocument.nodes[1], payload: { itemId: "focus_tree:C08", objectId: "C08", embeddedId: "ROOT", embeddedKind: "focus" } }]
    };

    expect(importDiagramJsonDraft(history, baseDocument, exportDiagramJson(mismatchedEmbeddedId))).toEqual({
      ok: false,
      changed: false,
      error: "Imported diagram node CHILD has embedded focus id ROOT that disagrees with the node id.",
      history
    });
  });

  it("rejects imports whose focus payload is missing an embedded id", () => {
    const history = createDiagramHistory(baseDocument);
    const missingEmbeddedId = {
      ...baseDocument,
      nodes: [baseDocument.nodes[0], { ...baseDocument.nodes[1], payload: { itemId: "focus_tree:C08", objectId: "C08", embeddedKind: "focus" } }]
    };

    expect(importDiagramJsonDraft(history, baseDocument, exportDiagramJson(missingEmbeddedId))).toEqual({
      ok: false,
      changed: false,
      error: "Imported diagram node CHILD is missing ParaDev embedded focus id.",
      history
    });
  });

  it("rejects imports that change an existing node source context payload", () => {
    const history = createDiagramHistory(baseDocument);
    const sourceContextDocument: DiagramDocument = {
      ...baseDocument,
      nodes: baseDocument.nodes.map((node) => ({
        ...node,
        payload: {
          ...(node.payload as Record<string, unknown>),
          familyId: "focus_tree",
          projectId: "PIHC3",
          relativeRoot: "src/modules/focus_tree/C08"
        }
      }))
    };
    const changedSourceContext = {
      ...sourceContextDocument,
      nodes: [
        sourceContextDocument.nodes[0],
        {
          ...sourceContextDocument.nodes[1],
          payload: {
            ...(sourceContextDocument.nodes[1].payload as Record<string, unknown>),
            relativeRoot: "src/modules/focus_tree/C09"
          }
        }
      ]
    };

    expect(importDiagramJsonDraft(history, sourceContextDocument, exportDiagramJson(changedSourceContext))).toEqual({
      ok: false,
      changed: false,
      error: "Imported diagram node CHILD changes ParaDev metadata payload for the current diagram.",
      history
    });
  });

  it("rejects imported non-focus nodes that cannot be saved to source metadata", () => {
    const history = createDiagramHistory(null);
    const technologyDocument = technologyDiagramDocument();
    const duplicateTechnologyNode = {
      ...technologyDocument,
      nodes: [
        technologyDocument.nodes[0],
        {
          ...technologyDocument.nodes[0],
          id: "TECH_FIREARM_COPY",
          order: 1,
          x: 12,
          title: "Firearm Copy"
        }
      ]
    };

    expect(importDiagramJsonDraft(history, technologyDocument, exportDiagramJson(duplicateTechnologyNode))).toEqual({
      ok: false,
      changed: false,
      error: "Imported diagram node TECH_FIREARM_COPY adds a non-focus metadata node that cannot be saved.",
      history
    });
  });

  it("rejects removed non-focus nodes that still come from source metadata", () => {
    const history = createDiagramHistory(null);
    const technologyDocument = technologyDiagramDocument();
    const removedTechnologyNode: DiagramDocument = {
      ...technologyDocument,
      nodes: []
    };

    expect(importDiagramJsonDraft(history, technologyDocument, exportDiagramJson(removedTechnologyNode))).toEqual({
      ok: false,
      changed: false,
      error: "Imported diagram removes non-focus metadata node TECH_FIREARM that cannot be deleted through diagram import.",
      history
    });
  });

  it("imports the first embedded focus node for an empty focus tree context", () => {
    const history = createDiagramHistory(null);
    const emptyFocusTreeDocument = emptyFocusTreeContextDocument();
    const focusPayload = emptyFocusTreeDocument.nodes[0].payload as Record<string, unknown>;
    const insertedRootFocus: DiagramDocument = {
      ...emptyFocusTreeDocument,
      nodes: [
        emptyFocusTreeDocument.nodes[0],
        {
          id: "FOCUS_NEW_ROOT",
          order: 1,
          mode: "auto",
          width: 6,
          height: 2,
          title: "Focus New Root",
          payload: {
            ...focusPayload,
            embeddedId: "FOCUS_NEW_ROOT",
            embeddedKind: "focus"
          }
        }
      ]
    };

    const result = importDiagramJsonDraft(history, emptyFocusTreeDocument, exportDiagramJson(insertedRootFocus));

    expect(result).toMatchObject({ changed: true, ok: true });
    if (!result.ok) {
      throw new Error(result.error);
    }
    expect(result.document).toEqual(insertedRootFocus);
    expect(result.history.present).toEqual(insertedRootFocus);
    expect(result.history.past).toEqual([emptyFocusTreeDocument]);
  });

  it("rejects new focus nodes whose source context differs from the current focus tree", () => {
    const history = createDiagramHistory(null);
    const emptyFocusTreeDocument = emptyFocusTreeContextDocument();
    const focusPayload = emptyFocusTreeDocument.nodes[0].payload as Record<string, unknown>;
    const mismatchedRootFocus: DiagramDocument = {
      ...emptyFocusTreeDocument,
      nodes: [
        emptyFocusTreeDocument.nodes[0],
        {
          id: "FOCUS_NEW_ROOT",
          order: 1,
          mode: "auto",
          width: 6,
          height: 2,
          title: "Focus New Root",
          payload: {
            ...focusPayload,
            embeddedId: "FOCUS_NEW_ROOT",
            embeddedKind: "focus",
            relativeRoot: "src/modules/focus_tree/C09_WRONG",
            sourceRootRelativePath: "src/modules/focus_tree/C09_WRONG"
          }
        }
      ]
    };

    expect(importDiagramJsonDraft(history, emptyFocusTreeDocument, exportDiagramJson(mismatchedRootFocus))).toEqual({
      ok: false,
      changed: false,
      error: "Imported diagram node FOCUS_NEW_ROOT changes ParaDev metadata payload for a new focus node.",
      history
    });
  });

  it("rejects focus nodes parented to a non-focus context node", () => {
    const history = createDiagramHistory(null);
    const emptyFocusTreeDocument = emptyFocusTreeContextDocument();
    const focusPayload = emptyFocusTreeDocument.nodes[0].payload as Record<string, unknown>;
    const contextParentedFocus: DiagramDocument = {
      ...emptyFocusTreeDocument,
      nodes: [
        emptyFocusTreeDocument.nodes[0],
        {
          id: "FOCUS_NEW_CHILD",
          parentId: "C08_PARTIV",
          order: 1,
          mode: "auto",
          width: 6,
          height: 2,
          title: "Focus New Child",
          payload: {
            ...focusPayload,
            embeddedId: "FOCUS_NEW_CHILD",
            embeddedKind: "focus"
          }
        }
      ],
      edges: [
        {
          id: "tree:C08_PARTIV->FOCUS_NEW_CHILD",
          source: "C08_PARTIV",
          target: "FOCUS_NEW_CHILD",
          kind: "tree"
        }
      ]
    };

    expect(importDiagramJsonDraft(history, emptyFocusTreeDocument, exportDiagramJson(contextParentedFocus))).toEqual({
      ok: false,
      changed: false,
      error: "Imported diagram node FOCUS_NEW_CHILD cannot use non-focus parent C08_PARTIV.",
      history
    });
  });

  it("rejects focus relationship edges connected to non-focus context nodes", () => {
    const history = createDiagramHistory(null);
    const emptyFocusTreeDocument = emptyFocusTreeContextDocument();
    const focusPayload = emptyFocusTreeDocument.nodes[0].payload as Record<string, unknown>;
    const insertedRootFocus: DiagramDocument = {
      ...emptyFocusTreeDocument,
      nodes: [
        emptyFocusTreeDocument.nodes[0],
        {
          id: "FOCUS_NEW_ROOT",
          order: 1,
          mode: "auto",
          width: 6,
          height: 2,
          title: "Focus New Root",
          payload: {
            ...focusPayload,
            embeddedId: "FOCUS_NEW_ROOT",
            embeddedKind: "focus"
          }
        }
      ]
    };
    const dependencyToContext: DiagramDocument = {
      ...insertedRootFocus,
      edges: [
        {
          id: "dependency:C08_PARTIV->FOCUS_NEW_ROOT",
          source: "C08_PARTIV",
          target: "FOCUS_NEW_ROOT",
          kind: "dependency"
        }
      ]
    };
    const referenceToContext: DiagramDocument = {
      ...insertedRootFocus,
      edges: [
        {
          id: "reference:FOCUS_NEW_ROOT->C08_PARTIV",
          source: "FOCUS_NEW_ROOT",
          target: "C08_PARTIV",
          kind: "reference"
        }
      ]
    };

    expect(importDiagramJsonDraft(history, emptyFocusTreeDocument, exportDiagramJson(dependencyToContext))).toEqual({
      ok: false,
      changed: false,
      error: "Imported diagram edge dependency:C08_PARTIV->FOCUS_NEW_ROOT cannot connect focus node FOCUS_NEW_ROOT to non-focus node C08_PARTIV.",
      history
    });
    expect(importDiagramJsonDraft(history, emptyFocusTreeDocument, exportDiagramJson(referenceToContext))).toEqual({
      ok: false,
      changed: false,
      error: "Imported diagram edge reference:FOCUS_NEW_ROOT->C08_PARTIV cannot connect focus node FOCUS_NEW_ROOT to non-focus node C08_PARTIV.",
      history
    });
  });

  it("rejects imported non-focus relationship edges outside the source scope", () => {
    const history = createDiagramHistory(null);
    const base: DiagramDocument = {
      schemaVersion: 1,
      gridSizePx: 24,
      nodes: [
        {
          id: "TECH_ROOT",
          order: 0,
          mode: "auto",
          width: 6,
          height: 2,
          payload: {
            projectId: "PIHC3",
            itemId: "technology:TECH_ROOT",
            itemKind: "module",
            familyId: "technology",
            family: "technology",
            objectId: "TECH_ROOT",
            relativeRoot: "src/modules/technology/TECH_ROOT"
          }
        },
        {
          id: "FOCUS_CONTEXT",
          order: 1,
          mode: "auto",
          width: 6,
          height: 2,
          payload: {
            projectId: "PIHC3",
            itemId: "focus_tree:C08_PARTIV",
            itemKind: "module",
            familyId: "focus_tree",
            family: "focus_tree",
            objectId: "C08_PARTIV",
            relativeRoot: "src/modules/focus_tree/C08_PARTIV"
          }
        }
      ],
      edges: []
    };
    const imported: DiagramDocument = {
      ...base,
      edges: [{ id: "dependency:TECH_ROOT->FOCUS_CONTEXT", source: "TECH_ROOT", target: "FOCUS_CONTEXT", kind: "dependency" }]
    };

    expect(importDiagramJsonDraft(history, base, exportDiagramJson(imported))).toEqual({
      ok: false,
      changed: false,
      error: "Imported diagram edge dependency:TECH_ROOT->FOCUS_CONTEXT cannot connect nodes from different diagram source scopes.",
      history
    });
  });

  it("rejects imported focus edges outside the focus tree source scope", () => {
    const history = createDiagramHistory(null);
    const base: DiagramDocument = {
      schemaVersion: 1,
      gridSizePx: 24,
      nodes: [
        {
          id: "FOCUS_ROOT",
          order: 0,
          mode: "auto",
          width: 4,
          height: 2,
          payload: {
            projectId: "PIHC3",
            itemId: "focus_tree:C08_PARTIV",
            itemKind: "module",
            familyId: "focus_tree",
            family: "focus_tree",
            objectId: "C08_PARTIV",
            embeddedId: "FOCUS_ROOT",
            embeddedKind: "focus",
            relativeRoot: "src/modules/focus_tree/C08_PARTIV"
          }
        },
        {
          id: "FOREIGN_FOCUS",
          order: 1,
          mode: "auto",
          width: 4,
          height: 2,
          payload: {
            projectId: "PIHC3",
            itemId: "focus_tree:C09_PARTV",
            itemKind: "module",
            familyId: "focus_tree",
            family: "focus_tree",
            objectId: "C09_PARTV",
            embeddedId: "FOREIGN_FOCUS",
            embeddedKind: "focus",
            relativeRoot: "src/modules/focus_tree/C09_PARTV"
          }
        }
      ],
      edges: []
    };
    const importedReference: DiagramDocument = {
      ...base,
      edges: [{ id: "reference:FOCUS_ROOT->FOREIGN_FOCUS", source: "FOCUS_ROOT", target: "FOREIGN_FOCUS", kind: "reference" }]
    };
    const importedTree: DiagramDocument = {
      ...base,
      nodes: [{ ...base.nodes[0], parentId: "FOREIGN_FOCUS" }, base.nodes[1]],
      edges: [{ id: "tree:FOREIGN_FOCUS->FOCUS_ROOT", source: "FOREIGN_FOCUS", target: "FOCUS_ROOT", kind: "tree" }]
    };

    expect(importDiagramJsonDraft(history, base, exportDiagramJson(importedReference))).toEqual({
      ok: false,
      changed: false,
      error: "Imported diagram edge reference:FOCUS_ROOT->FOREIGN_FOCUS cannot connect nodes from different diagram source scopes.",
      history
    });
    expect(importDiagramJsonDraft(history, base, exportDiagramJson(importedTree))).toEqual({
      ok: false,
      changed: false,
      error: "Imported diagram edge tree:FOREIGN_FOCUS->FOCUS_ROOT cannot connect nodes from different diagram source scopes.",
      history
    });
  });
});
