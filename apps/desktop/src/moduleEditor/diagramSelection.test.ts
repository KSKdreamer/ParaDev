import { describe, expect, it } from "vitest";
import { buildProjectDiagramDocument } from "../diagramEditor/projectDiagram";
import { buildModuleEntities } from "./model";
import { diagramNodeIdForEntity, entityIdForDiagramNode } from "./diagramSelection";
import type { ProjectBrowserPayload } from "../types";

function browserPayload(items: ProjectBrowserPayload["items"]): ProjectBrowserPayload {
  return {
    schema: "paradev.sdk.project-browser.v1",
    project_id: "PIHC3",
    title: "The Pony In The High Castle",
    root: "/workspace/projects/PIHC3",
    profile: "hoi4",
    filters: {},
    families: [],
    items,
    diagnostics: []
  };
}

describe("diagram entity selection", () => {
  it("maps technology diagram nodes to their canonical module entity", () => {
    const browser = browserPayload([
      {
        id: "technology:TECH_CHILD",
        kind: "module",
        layout: "canonical",
        family_id: "technologies",
        family: "technology",
        object_id: "TECH_CHILD",
        module_id: "TECH_CHILD",
        title: "Child Technology",
        root: "/workspace/projects/PIHC3/src/modules/technology/TECH_CHILD",
        relative_root: "src/modules/technology/TECH_CHILD",
        source_count: 1,
        sources: [],
        metadata: { settings: { folder_position: { x: 4, y: 1 } } }
      }
    ]);
    const entities = buildModuleEntities(browser, "technologies", "en");
    const document = buildProjectDiagramDocument(browser, "technologies");

    expect(entityIdForDiagramNode(entities, document, "TECH_CHILD")).toBe("technology:TECH_CHILD");
  });

  it("maps embedded focus nodes back to their focus tree module entity", () => {
    const browser = browserPayload([
      {
        id: "focus_tree:C08_PARTIV",
        kind: "module",
        layout: "canonical",
        family_id: "focuses",
        family: "focus_tree",
        object_id: "C08_PARTIV",
        module_id: "C08_PARTIV",
        title: "C08 Part IV",
        root: "/workspace/projects/PIHC3/src/modules/focus_tree/C08_PARTIV",
        relative_root: "src/modules/focus_tree/C08_PARTIV",
        source_count: 1,
        sources: [],
        metadata: {
          settings: {
            focuses: [
              { id: "FOCUS_C08_CANTERLOT_MIND", x: "12", y: "0" },
              { id: "FOCUS_C08_SECOND_SUMMIT", x: "12", y: "1", prerequisites: ["FOCUS_C08_CANTERLOT_MIND"] }
            ]
          }
        }
      }
    ]);
    const entities = buildModuleEntities(browser, "focuses", "en");
    const document = buildProjectDiagramDocument(browser, "focuses");

    expect(entityIdForDiagramNode(entities, document, "FOCUS_C08_SECOND_SUMMIT")).toBe("focus_tree:C08_PARTIV");
  });

  it("selects a concrete embedded focus node for a focus tree module entity", () => {
    const browser = browserPayload([
      {
        id: "focus_tree:C08_PARTIV",
        kind: "module",
        layout: "canonical",
        family_id: "focuses",
        family: "focus_tree",
        object_id: "C08_PARTIV",
        module_id: "C08_PARTIV",
        title: "C08 Part IV",
        root: "/workspace/projects/PIHC3/src/modules/focus_tree/C08_PARTIV",
        relative_root: "src/modules/focus_tree/C08_PARTIV",
        source_count: 1,
        sources: [],
        metadata: {
          settings: {
            focuses: [
              { id: "FOCUS_C08_CANTERLOT_MIND", x: "12", y: "0" },
              { id: "FOCUS_C08_SECOND_SUMMIT", x: "12", y: "1", prerequisites: ["FOCUS_C08_CANTERLOT_MIND"] }
            ]
          }
        }
      }
    ]);
    const entities = buildModuleEntities(browser, "focuses", "en");
    const document = buildProjectDiagramDocument(browser, "focuses");

    expect(diagramNodeIdForEntity(entities[0], document)).toBe("FOCUS_C08_CANTERLOT_MIND");
    expect(diagramNodeIdForEntity(entities[0], document, "FOCUS_C08_SECOND_SUMMIT")).toBe("FOCUS_C08_SECOND_SUMMIT");
  });
});
