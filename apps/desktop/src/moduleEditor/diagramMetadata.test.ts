import { describe, expect, it } from "vitest";
import * as layoutModel from "../diagramEditor/layoutModel";
import { autoLayoutDiagramNode, insertDiagramChildNode, insertDiagramRootNode, makeDiagramSelectedNodeRelative, moveDiagramNode, moveDiagramNodeRelayoutDescendants, pinDiagramSelectedNode, removeDiagramSubtree, reorderDiagramSibling, setDiagramDependencyEdge, setDiagramNodeLayoutHints } from "../diagramEditor/layoutModel";
import { buildProjectDiagramDocument } from "../diagramEditor/projectDiagram";
import { buildModuleEntities } from "./model";
import { buildDiagramMetadataTextDrafts, changedDiagramMetadataEntityIds, changedDiagramMetadataSourceInfoPaths, sourceTextEditsForDiagramMetadataDrafts } from "./diagramMetadata";
import type { ProjectBrowserPayload } from "../types";

type DiagramReferenceEdgeSetter = (document: ReturnType<typeof buildProjectDiagramDocument>, sourceId: string, targetId: string, enabled: boolean) => ReturnType<typeof buildProjectDiagramDocument>;
type DiagramNodeOnlyRemover = (document: ReturnType<typeof buildProjectDiagramDocument>, nodeId: string) => ReturnType<typeof buildProjectDiagramDocument>;
type DiagramTreeParentSetter = (document: ReturnType<typeof buildProjectDiagramDocument>, nodeId: string, parentId: string) => ReturnType<typeof buildProjectDiagramDocument>;
type DiagramTreeParentClearer = (document: ReturnType<typeof buildProjectDiagramDocument>, nodeId: string) => ReturnType<typeof buildProjectDiagramDocument>;

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

describe("diagram metadata drafts", () => {
  it("ignores viewport-only diagram changes for PIHC3 metadata writes", () => {
    const browser = browserPayload([
      {
        id: "technology:TECH_FIREARM",
        kind: "module",
        layout: "canonical",
        family_id: "technologies",
        family: "technology",
        object_id: "TECH_FIREARM",
        module_id: "TECH_FIREARM",
        title: "Firearm",
        root: "/workspace/projects/PIHC3/src/modules/technology/TECH_FIREARM",
        relative_root: "src/modules/technology/TECH_FIREARM",
        source_count: 1,
        sources: [{ slot: "meta", name: "meta.yaml", path: "/workspace/projects/PIHC3/src/modules/technology/TECH_FIREARM/meta.yaml", relative_path: "src/modules/technology/TECH_FIREARM/meta.yaml", extension: "yaml" }],
        metadata: { settings: { folder_position: { x: 4, y: 3 } } }
      }
    ]);
    const baseDocument = buildProjectDiagramDocument(browser, "technologies");
    const draftDocument = {
      ...baseDocument,
      viewport: { x: 24, y: -12, zoom: 1.5 }
    };

    expect(changedDiagramMetadataEntityIds(baseDocument, draftDocument)).toEqual([]);
    expect(
      buildDiagramMetadataTextDrafts({
        baseDocument,
        draftDocument,
        entities: buildModuleEntities(browser, "technologies", "en"),
        metadataTextByEntityId: { "technology:TECH_FIREARM": "" }
      })
    ).toEqual([]);
  });

  it("updates PIHC3 technology folder positions in metadata text", () => {
    const browser = browserPayload([
      {
        id: "technology:TECH_FIREARM",
        kind: "module",
        layout: "canonical",
        family_id: "technologies",
        family: "technology",
        object_id: "TECH_FIREARM",
        module_id: "TECH_FIREARM",
        title: "Firearm",
        root: "/workspace/projects/PIHC3/src/modules/technology/TECH_FIREARM",
        relative_root: "src/modules/technology/TECH_FIREARM",
        source_count: 1,
        sources: [{ slot: "meta", name: "meta.yaml", path: "/workspace/projects/PIHC3/src/modules/technology/TECH_FIREARM/meta.yaml", relative_path: "src/modules/technology/TECH_FIREARM/meta.yaml", extension: "yaml" }],
        metadata: { settings: { folder: { position: { x: 4, y: 3 } }, folder_position: { x: 4, y: 3 } } }
      }
    ]);
    const baseDocument = buildProjectDiagramDocument(browser, "technologies");
    const draftDocument = moveDiagramNode(baseDocument, "TECH_FIREARM", { dx: 2, dy: -1 });
    const entities = buildModuleEntities(browser, "technologies", "en");
    const metadataText = [
      "type: technology",
      "settings:",
      "    folder:",
      "        name: infantry_folder",
      "        position:",
      "            x: 4",
      "            y: 3",
      "    folder_position:",
      "        x: 4",
      "        y: 3",
      ""
    ].join("\n");

    const drafts = buildDiagramMetadataTextDrafts({
      baseDocument,
      draftDocument,
      entities,
      metadataTextByEntityId: { "technology:TECH_FIREARM": metadataText }
    });

    expect(drafts).toEqual([
      {
        entityId: "technology:TECH_FIREARM",
        slot: "meta",
        text: [
          "type: technology",
          "settings:",
          "    folder:",
          "        name: infantry_folder",
          "        position:",
          "            x: 6",
          "            y: 2",
          "    folder_position:",
          "        x: 6",
          "        y: 2",
          ""
        ].join("\n")
      }
    ]);
    expect(sourceTextEditsForDiagramMetadataDrafts(entities, drafts)).toEqual([
      {
        path: "/workspace/projects/PIHC3/src/modules/technology/TECH_FIREARM/meta.yaml",
        text: drafts[0].text
      }
    ]);
  });

  it("adds PIHC3 technology folder positions when metadata has none yet", () => {
    const browser = browserPayload([
      {
        id: "technology:TECH_NO_POSITION",
        kind: "module",
        layout: "canonical",
        family_id: "technologies",
        family: "technology",
        object_id: "TECH_NO_POSITION",
        module_id: "TECH_NO_POSITION",
        title: "No Position",
        root: "/workspace/projects/PIHC3/src/modules/technology/TECH_NO_POSITION",
        relative_root: "src/modules/technology/TECH_NO_POSITION",
        source_count: 1,
        sources: [{ slot: "meta", name: "meta.yaml", path: "/workspace/projects/PIHC3/src/modules/technology/TECH_NO_POSITION/meta.yaml", relative_path: "src/modules/technology/TECH_NO_POSITION/meta.yaml", extension: "yaml" }],
        metadata: { settings: { folder: { name: "infantry_folder" } } }
      }
    ]);
    const baseDocument = buildProjectDiagramDocument(browser, "technologies");
    const draftDocument = moveDiagramNode(baseDocument, "TECH_NO_POSITION", { dx: 2, dy: -1 });
    const entities = buildModuleEntities(browser, "technologies", "en");
    const metadataText = ["type: technology", "settings:", "    folder:", "        name: infantry_folder", ""].join("\n");

    expect(
      buildDiagramMetadataTextDrafts({
        baseDocument,
        draftDocument,
        entities,
        metadataTextByEntityId: { "technology:TECH_NO_POSITION": metadataText }
      })
    ).toEqual([
      {
        entityId: "technology:TECH_NO_POSITION",
        slot: "meta",
        text: [
          "type: technology",
          "settings:",
          "    folder:",
          "        name: infantry_folder",
          "    folder_position:",
          "        x: 2",
          "        y: -1",
          ""
        ].join("\n")
      }
    ]);
  });

  it("persists added PIHC3 technology dependency edges in target metadata text", () => {
    const browser = browserPayload([
      {
        id: "technology:TECH_ROOT",
        kind: "module",
        layout: "canonical",
        family_id: "technologies",
        family: "technology",
        object_id: "TECH_ROOT",
        module_id: "TECH_ROOT",
        title: "Root Technology",
        root: "/workspace/projects/PIHC3/src/modules/technology/TECH_ROOT",
        relative_root: "src/modules/technology/TECH_ROOT",
        source_count: 1,
        sources: [{ slot: "meta", name: "meta.yaml", path: "/workspace/projects/PIHC3/src/modules/technology/TECH_ROOT/meta.yaml", relative_path: "src/modules/technology/TECH_ROOT/meta.yaml", extension: "yaml" }],
        metadata: { settings: { folder_position: { x: 1, y: 1 } } }
      },
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
        sources: [{ slot: "meta", name: "meta.yaml", path: "/workspace/projects/PIHC3/src/modules/technology/TECH_CHILD/meta.yaml", relative_path: "src/modules/technology/TECH_CHILD/meta.yaml", extension: "yaml" }],
        metadata: { settings: { folder_position: { x: 4, y: 1 } } }
      }
    ]);
    const baseDocument = buildProjectDiagramDocument(browser, "technologies");
    const draftDocument = {
      ...baseDocument,
      edges: [...baseDocument.edges, { id: "dependency:TECH_ROOT->TECH_CHILD", source: "TECH_ROOT", target: "TECH_CHILD", kind: "dependency" as const }]
    };
    const entities = buildModuleEntities(browser, "technologies", "en");
    const metadataText = ["type: technology", "settings:", "    folder_position:", "        x: 4", "        y: 1", ""].join("\n");

    expect(changedDiagramMetadataEntityIds(baseDocument, draftDocument)).toEqual(["technology:TECH_CHILD", "technology:TECH_ROOT"]);
    expect(
      buildDiagramMetadataTextDrafts({
        baseDocument,
        draftDocument,
        entities,
        metadataTextByEntityId: { "technology:TECH_CHILD": metadataText }
      })
    ).toEqual([
      {
        entityId: "technology:TECH_CHILD",
        slot: "meta",
        text: ["type: technology", "settings:", "    folder_position:", "        x: 4", "        y: 1", "    dependency_ids:", "    - TECH_ROOT", ""].join("\n")
      }
    ]);
  });

  it("updates PIHC3 technology path targets when dependency edges are added", () => {
    const browser = browserPayload([
      {
        id: "technology:TECH_ROOT",
        kind: "module",
        layout: "canonical",
        family_id: "technologies",
        family: "technology",
        object_id: "TECH_ROOT",
        module_id: "TECH_ROOT",
        title: "Root Technology",
        root: "/workspace/projects/PIHC3/src/modules/technology/TECH_ROOT",
        relative_root: "src/modules/technology/TECH_ROOT",
        source_count: 1,
        sources: [{ slot: "meta", name: "meta.yaml", path: "/workspace/projects/PIHC3/src/modules/technology/TECH_ROOT/meta.yaml", relative_path: "src/modules/technology/TECH_ROOT/meta.yaml", extension: "yaml" }],
        metadata: { settings: { folder_position: { x: 1, y: 1 }, path_count: 0, path_target_ids: [] } }
      },
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
        sources: [{ slot: "meta", name: "meta.yaml", path: "/workspace/projects/PIHC3/src/modules/technology/TECH_CHILD/meta.yaml", relative_path: "src/modules/technology/TECH_CHILD/meta.yaml", extension: "yaml" }],
        metadata: { settings: { folder_position: { x: 4, y: 1 } } }
      }
    ]);
    const baseDocument = buildProjectDiagramDocument(browser, "technologies");
    const draftDocument = {
      ...baseDocument,
      edges: [...baseDocument.edges, { id: "dependency:TECH_ROOT->TECH_CHILD", source: "TECH_ROOT", target: "TECH_CHILD", kind: "dependency" as const }]
    };
    const entities = buildModuleEntities(browser, "technologies", "en");
    const metadataText = [
      "type: technology",
      "settings:",
      "    folder_position:",
      "        x: 1",
      "        y: 1",
      "    path_count: 0",
      "    path_target_ids: []",
      ""
    ].join("\n");

    expect(changedDiagramMetadataEntityIds(baseDocument, draftDocument)).toEqual(["technology:TECH_CHILD", "technology:TECH_ROOT"]);
    expect(
      buildDiagramMetadataTextDrafts({
        baseDocument,
        draftDocument,
        entities,
        metadataTextByEntityId: { "technology:TECH_ROOT": metadataText }
      })
    ).toEqual([
      {
        entityId: "technology:TECH_ROOT",
        slot: "meta",
        text: [
          "type: technology",
          "settings:",
          "    folder_position:",
          "        x: 1",
          "        y: 1",
          "    path_count: 1",
          "    path_target_ids:",
          "    - TECH_CHILD",
          ""
        ].join("\n")
      }
    ]);
  });

  it("persists added PIHC3 technology dependency edges from inline empty lists", () => {
    const browser = browserPayload([
      {
        id: "technology:TECH_ROOT",
        kind: "module",
        layout: "canonical",
        family_id: "technologies",
        family: "technology",
        object_id: "TECH_ROOT",
        module_id: "TECH_ROOT",
        title: "Root Technology",
        root: "/workspace/projects/PIHC3/src/modules/technology/TECH_ROOT",
        relative_root: "src/modules/technology/TECH_ROOT",
        source_count: 1,
        sources: [{ slot: "meta", name: "meta.yaml", path: "/workspace/projects/PIHC3/src/modules/technology/TECH_ROOT/meta.yaml", relative_path: "src/modules/technology/TECH_ROOT/meta.yaml", extension: "yaml" }],
        metadata: { settings: { folder_position: { x: 1, y: 1 } } }
      },
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
        sources: [{ slot: "meta", name: "meta.yaml", path: "/workspace/projects/PIHC3/src/modules/technology/TECH_CHILD/meta.yaml", relative_path: "src/modules/technology/TECH_CHILD/meta.yaml", extension: "yaml" }],
        metadata: { settings: { folder_position: { x: 4, y: 1 }, dependency_ids: [] } }
      }
    ]);
    const baseDocument = buildProjectDiagramDocument(browser, "technologies");
    const draftDocument = {
      ...baseDocument,
      edges: [...baseDocument.edges, { id: "dependency:TECH_ROOT->TECH_CHILD", source: "TECH_ROOT", target: "TECH_CHILD", kind: "dependency" as const }]
    };
    const entities = buildModuleEntities(browser, "technologies", "en");
    const metadataText = ["type: technology", "settings:", "    folder_position:", "        x: 4", "        y: 1", "    dependency_ids: []", ""].join("\n");

    expect(changedDiagramMetadataEntityIds(baseDocument, draftDocument)).toEqual(["technology:TECH_CHILD", "technology:TECH_ROOT"]);
    expect(
      buildDiagramMetadataTextDrafts({
        baseDocument,
        draftDocument,
        entities,
        metadataTextByEntityId: { "technology:TECH_CHILD": metadataText }
      })
    ).toEqual([
      {
        entityId: "technology:TECH_CHILD",
        slot: "meta",
        text: ["type: technology", "settings:", "    folder_position:", "        x: 4", "        y: 1", "    dependency_ids:", "    - TECH_ROOT", ""].join("\n")
      }
    ]);
  });

  it("removes PIHC3 technology dependency edges from target metadata text", () => {
    const browser = browserPayload([
      {
        id: "technology:TECH_ROOT",
        kind: "module",
        layout: "canonical",
        family_id: "technologies",
        family: "technology",
        object_id: "TECH_ROOT",
        module_id: "TECH_ROOT",
        title: "Root Technology",
        root: "/workspace/projects/PIHC3/src/modules/technology/TECH_ROOT",
        relative_root: "src/modules/technology/TECH_ROOT",
        source_count: 1,
        sources: [{ slot: "meta", name: "meta.yaml", path: "/workspace/projects/PIHC3/src/modules/technology/TECH_ROOT/meta.yaml", relative_path: "src/modules/technology/TECH_ROOT/meta.yaml", extension: "yaml" }],
        metadata: { settings: { folder_position: { x: 1, y: 1 } } }
      },
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
        sources: [{ slot: "meta", name: "meta.yaml", path: "/workspace/projects/PIHC3/src/modules/technology/TECH_CHILD/meta.yaml", relative_path: "src/modules/technology/TECH_CHILD/meta.yaml", extension: "yaml" }],
        metadata: { settings: { folder_position: { x: 4, y: 1 }, dependency_ids: ["TECH_ROOT"] } }
      }
    ]);
    const baseDocument = buildProjectDiagramDocument(browser, "technologies");
    const draftDocument = setDiagramDependencyEdge(baseDocument, "TECH_ROOT", "TECH_CHILD", false);
    const entities = buildModuleEntities(browser, "technologies", "en");
    const metadataText = ["type: technology", "settings:", "    folder_position:", "        x: 4", "        y: 1", "    dependency_ids:", "    - TECH_ROOT", ""].join("\n");

    expect(changedDiagramMetadataEntityIds(baseDocument, draftDocument)).toEqual(["technology:TECH_CHILD", "technology:TECH_ROOT"]);
    expect(
      buildDiagramMetadataTextDrafts({
        baseDocument,
        draftDocument,
        entities,
        metadataTextByEntityId: { "technology:TECH_CHILD": metadataText }
      })
    ).toEqual([
      {
        entityId: "technology:TECH_CHILD",
        slot: "meta",
        text: ["type: technology", "settings:", "    folder_position:", "        x: 4", "        y: 1", "    dependency_ids: []", ""].join("\n")
      }
    ]);
  });

  it("ignores stale PIHC3 non-focus relationship edges outside the source scope", () => {
    const browser = browserPayload([
      {
        id: "technology:TECH_ROOT",
        kind: "module",
        layout: "canonical",
        family_id: "technologies",
        family: "technology",
        object_id: "TECH_ROOT",
        module_id: "TECH_ROOT",
        title: "Root Technology",
        root: "/workspace/projects/PIHC3/src/modules/technology/TECH_ROOT",
        relative_root: "src/modules/technology/TECH_ROOT",
        source_count: 1,
        sources: [{ slot: "meta", name: "meta.yaml", path: "/workspace/projects/PIHC3/src/modules/technology/TECH_ROOT/meta.yaml", relative_path: "src/modules/technology/TECH_ROOT/meta.yaml", extension: "yaml" }],
        metadata: { settings: { folder_position: { x: 1, y: 1 } } }
      },
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
        sources: [{ slot: "meta", name: "meta.yaml", path: "/workspace/projects/PIHC3/src/modules/focus_tree/C08_PARTIV/meta.yaml", relative_path: "src/modules/focus_tree/C08_PARTIV/meta.yaml", extension: "yaml" }],
        metadata: { settings: { focuses: [] } }
      }
    ]);
    const technologyDocument = buildProjectDiagramDocument(browser, "technologies");
    const focusDocument = buildProjectDiagramDocument(browser, "focuses");
    const baseDocument = {
      ...technologyDocument,
      nodes: [...technologyDocument.nodes, ...focusDocument.nodes]
    };
    const draftDocument = {
      ...baseDocument,
      edges: [
        ...baseDocument.edges,
        {
          id: "dependency:TECH_ROOT->C08_PARTIV",
          source: "TECH_ROOT",
          target: "C08_PARTIV",
          kind: "dependency" as const
        }
      ]
    };
    const entities = [...buildModuleEntities(browser, "technologies", "en"), ...buildModuleEntities(browser, "focuses", "en")];
    const metadataTextByEntityId = {
      "technology:TECH_ROOT": ["type: technology", "settings:", "    folder_position:", "        x: 1", "        y: 1", ""].join("\n"),
      "focus_tree:C08_PARTIV": ["type: focus_tree", "settings:", "    focuses: []", ""].join("\n")
    };

    expect(changedDiagramMetadataEntityIds(baseDocument, draftDocument)).toEqual([]);
    expect(
      buildDiagramMetadataTextDrafts({
        baseDocument,
        draftDocument,
        entities,
        metadataTextByEntityId
      })
    ).toEqual([]);
  });

  it("keeps empty PIHC3 technology path target lists when dependency edges are removed", () => {
    const browser = browserPayload([
      {
        id: "technology:TECH_ROOT",
        kind: "module",
        layout: "canonical",
        family_id: "technologies",
        family: "technology",
        object_id: "TECH_ROOT",
        module_id: "TECH_ROOT",
        title: "Root Technology",
        root: "/workspace/projects/PIHC3/src/modules/technology/TECH_ROOT",
        relative_root: "src/modules/technology/TECH_ROOT",
        source_count: 1,
        sources: [{ slot: "meta", name: "meta.yaml", path: "/workspace/projects/PIHC3/src/modules/technology/TECH_ROOT/meta.yaml", relative_path: "src/modules/technology/TECH_ROOT/meta.yaml", extension: "yaml" }],
        metadata: { settings: { folder_position: { x: 1, y: 1 }, path_count: 1, path_target_ids: ["TECH_CHILD"] } }
      },
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
        sources: [{ slot: "meta", name: "meta.yaml", path: "/workspace/projects/PIHC3/src/modules/technology/TECH_CHILD/meta.yaml", relative_path: "src/modules/technology/TECH_CHILD/meta.yaml", extension: "yaml" }],
        metadata: { settings: { folder_position: { x: 4, y: 1 }, dependency_ids: ["TECH_ROOT"] } }
      }
    ]);
    const baseDocument = buildProjectDiagramDocument(browser, "technologies");
    const draftDocument = setDiagramDependencyEdge(baseDocument, "TECH_ROOT", "TECH_CHILD", false);
    const entities = buildModuleEntities(browser, "technologies", "en");
    const metadataText = [
      "type: technology",
      "settings:",
      "    folder_position:",
      "        x: 1",
      "        y: 1",
      "    path_count: 1",
      "    path_target_ids:",
      "    - TECH_CHILD",
      ""
    ].join("\n");

    expect(changedDiagramMetadataEntityIds(baseDocument, draftDocument)).toEqual(["technology:TECH_CHILD", "technology:TECH_ROOT"]);
    expect(
      buildDiagramMetadataTextDrafts({
        baseDocument,
        draftDocument,
        entities,
        metadataTextByEntityId: { "technology:TECH_ROOT": metadataText }
      })
    ).toEqual([
      {
        entityId: "technology:TECH_ROOT",
        slot: "meta",
        text: [
          "type: technology",
          "settings:",
          "    folder_position:",
          "        x: 1",
          "        y: 1",
          "    path_count: 0",
          "    path_target_ids: []",
          ""
        ].join("\n")
      }
    ]);
  });

  it("persists added PIHC3 focus prerequisite edges in focus tree metadata text", () => {
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
        sources: [{ slot: "meta", name: "meta.yaml", path: "/workspace/projects/PIHC3/src/modules/focus_tree/C08_PARTIV/meta.yaml", relative_path: "src/modules/focus_tree/C08_PARTIV/meta.yaml", extension: "yaml" }],
        metadata: {
          settings: {
            focuses: [
              { id: "FOCUS_ROOT", x: "12", y: "0" },
              { id: "FOCUS_CHILD", x: "12", y: "1" }
            ]
          }
        }
      }
    ]);
    const baseDocument = buildProjectDiagramDocument(browser, "focuses");
    const draftDocument = setDiagramDependencyEdge(baseDocument, "FOCUS_ROOT", "FOCUS_CHILD", true);
    const entities = buildModuleEntities(browser, "focuses", "en");
    const metadataText = ["type: focus_tree", "settings:", "    focuses:", "    -   id: FOCUS_ROOT", "        x: '12'", "        y: '0'", "    -   id: FOCUS_CHILD", "        x: '12'", "        y: '1'", ""].join("\n");

    expect(changedDiagramMetadataEntityIds(baseDocument, draftDocument)).toEqual(["focus_tree:C08_PARTIV"]);
    expect(
      buildDiagramMetadataTextDrafts({
        baseDocument,
        draftDocument,
        entities,
        metadataTextByEntityId: { "focus_tree:C08_PARTIV": metadataText }
      })
    ).toEqual([
      {
        entityId: "focus_tree:C08_PARTIV",
        slot: "meta",
        text: ["type: focus_tree", "settings:", "    focuses:", "    -   id: FOCUS_ROOT", "        x: '12'", "        y: '0'", "    -   id: FOCUS_CHILD", "        x: '12'", "        y: '1'", "        prerequisites:", "        - FOCUS_ROOT", ""].join("\n")
      }
    ]);
  });

  it("does not persist PIHC3 focus relationships to non-focus context nodes", () => {
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
        sources: [{ slot: "meta", name: "meta.yaml", path: "/workspace/projects/PIHC3/src/modules/focus_tree/C08_PARTIV/meta.yaml", relative_path: "src/modules/focus_tree/C08_PARTIV/meta.yaml", extension: "yaml" }],
        metadata: {
          settings: {
            focuses: []
          }
        }
      }
    ]);
    const baseDocument = buildProjectDiagramDocument(browser, "focuses");
    const contextPayload = baseDocument.nodes[0].payload as Record<string, unknown>;
    const draftDocument = {
      ...baseDocument,
      nodes: [
        baseDocument.nodes[0],
        {
          id: "FOCUS_NEW_ROOT",
          order: 1,
          mode: "auto" as const,
          width: 6,
          height: 2,
          title: "Focus New Root",
          payload: {
            ...contextPayload,
            embeddedId: "FOCUS_NEW_ROOT",
            embeddedKind: "focus"
          }
        }
      ],
      edges: [
        {
          id: "dependency:C08_PARTIV->FOCUS_NEW_ROOT",
          source: "C08_PARTIV",
          target: "FOCUS_NEW_ROOT",
          kind: "dependency" as const
        },
        {
          id: "reference:FOCUS_NEW_ROOT->C08_PARTIV",
          source: "FOCUS_NEW_ROOT",
          target: "C08_PARTIV",
          kind: "reference" as const
        }
      ]
    };
    const entities = buildModuleEntities(browser, "focuses", "en");
    const metadataText = ["type: focus_tree", "settings:", "    focuses: []", ""].join("\n");

    expect(
      buildDiagramMetadataTextDrafts({
        baseDocument,
        draftDocument,
        entities,
        metadataTextByEntityId: { "focus_tree:C08_PARTIV": metadataText }
      })
    ).toEqual([
      {
        entityId: "focus_tree:C08_PARTIV",
        slot: "meta",
        text: ["type: focus_tree", "settings:", "    focuses:", "        -   id: FOCUS_NEW_ROOT", ""].join("\n")
      }
    ]);
  });

  it("ignores stale PIHC3 focus relationship edges outside the focus tree source scope", () => {
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
        sources: [{ slot: "meta", name: "meta.yaml", path: "/workspace/projects/PIHC3/src/modules/focus_tree/C08_PARTIV/meta.yaml", relative_path: "src/modules/focus_tree/C08_PARTIV/meta.yaml", extension: "yaml" }],
        metadata: {
          settings: {
            focuses: [{ id: "FOCUS_ROOT", x: "12", y: "0" }]
          }
        }
      },
      {
        id: "focus_tree:C09_PARTV",
        kind: "module",
        layout: "canonical",
        family_id: "focuses",
        family: "focus_tree",
        object_id: "C09_PARTV",
        module_id: "C09_PARTV",
        title: "C09 Part V",
        root: "/workspace/projects/PIHC3/src/modules/focus_tree/C09_PARTV",
        relative_root: "src/modules/focus_tree/C09_PARTV",
        source_count: 1,
        sources: [{ slot: "meta", name: "meta.yaml", path: "/workspace/projects/PIHC3/src/modules/focus_tree/C09_PARTV/meta.yaml", relative_path: "src/modules/focus_tree/C09_PARTV/meta.yaml", extension: "yaml" }],
        metadata: {
          settings: {
            focuses: [{ id: "FOREIGN_FOCUS", x: "10", y: "0" }]
          }
        }
      }
    ]);
    const baseDocument = buildProjectDiagramDocument(browser, "focuses");
    const draftDocument = {
      ...baseDocument,
      edges: [
        ...baseDocument.edges,
        {
          id: "dependency:FOCUS_ROOT->FOREIGN_FOCUS",
          source: "FOCUS_ROOT",
          target: "FOREIGN_FOCUS",
          kind: "dependency" as const
        },
        {
          id: "reference:FOCUS_ROOT->FOREIGN_FOCUS",
          source: "FOCUS_ROOT",
          target: "FOREIGN_FOCUS",
          kind: "reference" as const
        }
      ]
    };
    const entities = buildModuleEntities(browser, "focuses", "en");
    const metadataTextByEntityId = {
      "focus_tree:C08_PARTIV": ["type: focus_tree", "settings:", "    focuses:", "    -   id: FOCUS_ROOT", "        x: '12'", "        y: '0'", ""].join("\n"),
      "focus_tree:C09_PARTV": ["type: focus_tree", "settings:", "    focuses:", "    -   id: FOREIGN_FOCUS", "        x: '10'", "        y: '0'", ""].join("\n")
    };

    expect(changedDiagramMetadataEntityIds(baseDocument, draftDocument)).toEqual([]);
    expect(
      buildDiagramMetadataTextDrafts({
        baseDocument,
        draftDocument,
        entities,
        metadataTextByEntityId
      })
    ).toEqual([]);
  });

  it("does not persist PIHC3 focus parents to non-focus context nodes", () => {
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
        sources: [{ slot: "meta", name: "meta.yaml", path: "/workspace/projects/PIHC3/src/modules/focus_tree/C08_PARTIV/meta.yaml", relative_path: "src/modules/focus_tree/C08_PARTIV/meta.yaml", extension: "yaml" }],
        metadata: {
          settings: {
            focuses: []
          }
        }
      }
    ]);
    const baseDocument = buildProjectDiagramDocument(browser, "focuses");
    const contextPayload = baseDocument.nodes[0].payload as Record<string, unknown>;
    const draftDocument = {
      ...baseDocument,
      nodes: [
        baseDocument.nodes[0],
        {
          id: "FOCUS_NEW_ROOT",
          parentId: "C08_PARTIV",
          order: 1,
          mode: "auto" as const,
          width: 6,
          height: 2,
          title: "Focus New Root",
          payload: {
            ...contextPayload,
            embeddedId: "FOCUS_NEW_ROOT",
            embeddedKind: "focus"
          }
        }
      ],
      edges: [
        {
          id: "tree:C08_PARTIV->FOCUS_NEW_ROOT",
          source: "C08_PARTIV",
          target: "FOCUS_NEW_ROOT",
          kind: "tree" as const
        }
      ]
    };
    const entities = buildModuleEntities(browser, "focuses", "en");
    const metadataText = ["type: focus_tree", "settings:", "    focuses: []", ""].join("\n");

    expect(
      buildDiagramMetadataTextDrafts({
        baseDocument,
        draftDocument,
        entities,
        metadataTextByEntityId: { "focus_tree:C08_PARTIV": metadataText }
      })
    ).toEqual([
      {
        entityId: "focus_tree:C08_PARTIV",
        slot: "meta",
        text: ["type: focus_tree", "settings:", "    focuses:", "        -   id: FOCUS_NEW_ROOT", ""].join("\n")
      }
    ]);
  });

  it("persists added PIHC3 focus mutual exclusion reference edges in focus tree metadata text", () => {
    const setDiagramReferenceEdge = (layoutModel as typeof layoutModel & { setDiagramReferenceEdge?: DiagramReferenceEdgeSetter }).setDiagramReferenceEdge;
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
        sources: [{ slot: "meta", name: "meta.yaml", path: "/workspace/projects/PIHC3/src/modules/focus_tree/C08_PARTIV/meta.yaml", relative_path: "src/modules/focus_tree/C08_PARTIV/meta.yaml", extension: "yaml" }],
        metadata: {
          settings: {
            focuses: [
              { id: "FOCUS_ALPHA", x: "10", y: "1" },
              { id: "FOCUS_BETA", x: "14", y: "1" }
            ]
          }
        }
      }
    ]);
    const baseDocument = buildProjectDiagramDocument(browser, "focuses");
    const draftDocument = setDiagramReferenceEdge?.(baseDocument, "FOCUS_ALPHA", "FOCUS_BETA", true) ?? baseDocument;
    const entities = buildModuleEntities(browser, "focuses", "en");
    const metadataText = ["type: focus_tree", "settings:", "    focuses:", "    -   id: FOCUS_ALPHA", "        x: '10'", "        y: '1'", "    -   id: FOCUS_BETA", "        x: '14'", "        y: '1'", ""].join("\n");

    expect(changedDiagramMetadataEntityIds(baseDocument, draftDocument)).toEqual(["focus_tree:C08_PARTIV"]);
    expect(
      buildDiagramMetadataTextDrafts({
        baseDocument,
        draftDocument,
        entities,
        metadataTextByEntityId: { "focus_tree:C08_PARTIV": metadataText }
      })
    ).toEqual([
      {
        entityId: "focus_tree:C08_PARTIV",
        slot: "meta",
        text: ["type: focus_tree", "settings:", "    focuses:", "    -   id: FOCUS_ALPHA", "        x: '10'", "        y: '1'", "        mutually_exclusive:", "        - FOCUS_BETA", "    -   id: FOCUS_BETA", "        x: '14'", "        y: '1'", ""].join("\n")
      }
    ]);
  });

  it("updates PIHC3 focus relationship counts when diagram edges change", () => {
    const setDiagramReferenceEdge = (layoutModel as typeof layoutModel & { setDiagramReferenceEdge?: DiagramReferenceEdgeSetter }).setDiagramReferenceEdge;
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
        sources: [{ slot: "meta", name: "meta.yaml", path: "/workspace/projects/PIHC3/src/modules/focus_tree/C08_PARTIV/meta.yaml", relative_path: "src/modules/focus_tree/C08_PARTIV/meta.yaml", extension: "yaml" }],
        metadata: {
          settings: {
            focuses: [
              { id: "FOCUS_ALPHA", mutually_exclusive_count: 0, prerequisite_count: 0, x: "10", y: "1" },
              { id: "FOCUS_BETA", mutually_exclusive_count: 0, prerequisite_count: 0, x: "14", y: "1" }
            ]
          }
        }
      }
    ]);
    const baseDocument = buildProjectDiagramDocument(browser, "focuses");
    const withDependency = setDiagramDependencyEdge(baseDocument, "FOCUS_ALPHA", "FOCUS_BETA", true);
    const draftDocument = setDiagramReferenceEdge?.(withDependency, "FOCUS_ALPHA", "FOCUS_BETA", true) ?? withDependency;
    const entities = buildModuleEntities(browser, "focuses", "en");
    const metadataText = [
      "type: focus_tree",
      "settings:",
      "    focuses:",
      "    -   id: FOCUS_ALPHA",
      "        x: '10'",
      "        y: '1'",
      "        prerequisite_count: 0",
      "        mutually_exclusive_count: 0",
      "    -   id: FOCUS_BETA",
      "        x: '14'",
      "        y: '1'",
      "        prerequisite_count: 0",
      "        mutually_exclusive_count: 0",
      ""
    ].join("\n");

    expect(
      buildDiagramMetadataTextDrafts({
        baseDocument,
        draftDocument,
        entities,
        metadataTextByEntityId: { "focus_tree:C08_PARTIV": metadataText }
      })
    ).toEqual([
      {
        entityId: "focus_tree:C08_PARTIV",
        slot: "meta",
        text: [
          "type: focus_tree",
          "settings:",
          "    focuses:",
          "    -   id: FOCUS_ALPHA",
          "        x: '10'",
          "        y: '1'",
          "        prerequisite_count: 0",
          "        mutually_exclusive_count: 1",
          "        mutually_exclusive:",
          "        - FOCUS_BETA",
          "    -   id: FOCUS_BETA",
          "        x: '14'",
          "        y: '1'",
          "        prerequisite_count: 1",
          "        prerequisites:",
          "        - FOCUS_ALPHA",
          "        mutually_exclusive_count: 0",
          ""
        ].join("\n")
      }
    ]);
  });

  it("updates migrated PIHC source focus relationships before compiled focus relationships", () => {
    const setDiagramReferenceEdge = (layoutModel as typeof layoutModel & { setDiagramReferenceEdge?: DiagramReferenceEdgeSetter }).setDiagramReferenceEdge;
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
        sources: [{ slot: "meta", name: "meta.yaml", path: "/workspace/projects/PIHC3/src/modules/focus_tree/C08_PARTIV/meta.yaml", relative_path: "src/modules/focus_tree/C08_PARTIV/meta.yaml", extension: "yaml" }],
        metadata: {
          settings: {
            source_focuses: [
              { folder: "C08_ROOT", focus_id: "FOCUS_ROOT", source_path: "C08_ROOT", x: "10", y: "0" },
              { folder: "C08_CHILD", focus_id: "FOCUS_CHILD", source_path: "C08_CHILD", dx: "2", dy: "1", priority: "10" },
              { folder: "C08_OTHER", focus_id: "FOCUS_OTHER", source_path: "C08_OTHER", x: "14", y: "0" }
            ],
            focuses: [
              { id: "FOCUS_ROOT", x: "10", y: "0" },
              { id: "FOCUS_CHILD", x: "12", y: "1" },
              { id: "FOCUS_OTHER", x: "14", y: "0" }
            ]
          }
        }
      }
    ]);
    const baseDocument = buildProjectDiagramDocument(browser, "focuses");
    const withDependency = setDiagramDependencyEdge(baseDocument, "FOCUS_ROOT", "FOCUS_CHILD", true);
    const draftDocument = setDiagramReferenceEdge?.(withDependency, "FOCUS_ROOT", "FOCUS_OTHER", true) ?? withDependency;
    const entities = buildModuleEntities(browser, "focuses", "en");
    const metadataText = [
      "type: focus_tree",
      "settings:",
      "    source_focuses:",
      "    -   folder: C08_ROOT",
      "        focus_id: FOCUS_ROOT",
      "        source_path: C08_ROOT",
      "        x: '10'",
      "        y: '0'",
      "    -   folder: C08_CHILD",
      "        focus_id: FOCUS_CHILD",
      "        source_path: C08_CHILD",
      "        dx: '2'",
      "        dy: '1'",
      "        priority: '10'",
      "    -   folder: C08_OTHER",
      "        focus_id: FOCUS_OTHER",
      "        source_path: C08_OTHER",
      "        x: '14'",
      "        y: '0'",
      "    focuses:",
      "    -   id: FOCUS_ROOT",
      "        x: '10'",
      "        y: '0'",
      "    -   id: FOCUS_CHILD",
      "        x: '12'",
      "        y: '1'",
      "    -   id: FOCUS_OTHER",
      "        x: '14'",
      "        y: '0'",
      ""
    ].join("\n");

    expect(changedDiagramMetadataEntityIds(baseDocument, draftDocument)).toEqual(["focus_tree:C08_PARTIV"]);
    expect(
      buildDiagramMetadataTextDrafts({
        baseDocument,
        draftDocument,
        entities,
        metadataTextByEntityId: { "focus_tree:C08_PARTIV": metadataText }
      })
    ).toEqual([
      {
        entityId: "focus_tree:C08_PARTIV",
        slot: "meta",
        text: [
          "type: focus_tree",
          "settings:",
          "    source_focuses:",
          "    -   folder: C08_ROOT",
          "        focus_id: FOCUS_ROOT",
          "        source_path: C08_ROOT",
          "        mutually_exclusive:",
          "        - FOCUS_OTHER",
          "        x: '10'",
          "        y: '0'",
          "    -   folder: C08_CHILD",
          "        focus_id: FOCUS_CHILD",
          "        source_path: C08_CHILD",
          "        prerequisites:",
          "        - FOCUS_ROOT",
          "        dx: '2'",
          "        dy: '1'",
          "        priority: '10'",
          "    -   folder: C08_OTHER",
          "        focus_id: FOCUS_OTHER",
          "        source_path: C08_OTHER",
          "        x: '14'",
          "        y: '0'",
          "    focuses:",
          "    -   id: FOCUS_ROOT",
          "        x: '10'",
          "        y: '0'",
          "    -   id: FOCUS_CHILD",
          "        x: '12'",
          "        y: '1'",
          "    -   id: FOCUS_OTHER",
          "        x: '14'",
          "        y: '0'",
          ""
        ].join("\n")
      }
    ]);
  });

  it("replaces migrated PIHC source focus singular prerequisites with canonical relationship lists", () => {
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
        sources: [{ slot: "meta", name: "meta.yaml", path: "/workspace/projects/PIHC3/src/modules/focus_tree/C08_PARTIV/meta.yaml", relative_path: "src/modules/focus_tree/C08_PARTIV/meta.yaml", extension: "yaml" }],
        metadata: {
          settings: {
            source_focuses: [
              { folder: "C08_OLD", focus_id: "FOCUS_OLD", source_path: "C08_OLD", x: "10", y: "0" },
              { folder: "C08_NEW", focus_id: "FOCUS_NEW", source_path: "C08_NEW", x: "12", y: "0" },
              { folder: "C08_CHILD", focus_id: "FOCUS_CHILD", source_path: "C08_CHILD", prerequisite: "FOCUS_OLD", dx: "1", dy: "1" }
            ],
            focuses: [
              { id: "FOCUS_OLD", x: "10", y: "0" },
              { id: "FOCUS_NEW", x: "12", y: "0" },
              { id: "FOCUS_CHILD", prerequisites: ["FOCUS_OLD"], x: "11", y: "1" }
            ]
          }
        }
      }
    ]);
    const baseDocument = buildProjectDiagramDocument(browser, "focuses");
    const withoutOld = setDiagramDependencyEdge(baseDocument, "FOCUS_OLD", "FOCUS_CHILD", false);
    const draftDocument = setDiagramDependencyEdge(withoutOld, "FOCUS_NEW", "FOCUS_CHILD", true);
    const entities = buildModuleEntities(browser, "focuses", "en");
    const metadataText = [
      "type: focus_tree",
      "settings:",
      "    source_focuses:",
      "    -   folder: C08_OLD",
      "        focus_id: FOCUS_OLD",
      "        source_path: C08_OLD",
      "        x: '10'",
      "        y: '0'",
      "    -   folder: C08_NEW",
      "        focus_id: FOCUS_NEW",
      "        source_path: C08_NEW",
      "        x: '12'",
      "        y: '0'",
      "    -   folder: C08_CHILD",
      "        focus_id: FOCUS_CHILD",
      "        source_path: C08_CHILD",
      "        prerequisite: FOCUS_OLD",
      "        dx: '1'",
      "        dy: '1'",
      "    focuses:",
      "    -   id: FOCUS_OLD",
      "        x: '10'",
      "        y: '0'",
      "    -   id: FOCUS_NEW",
      "        x: '12'",
      "        y: '0'",
      "    -   id: FOCUS_CHILD",
      "        x: '11'",
      "        y: '1'",
      "        prerequisites:",
      "        - FOCUS_OLD",
      ""
    ].join("\n");

    expect(changedDiagramMetadataEntityIds(baseDocument, draftDocument)).toEqual(["focus_tree:C08_PARTIV"]);
    expect(
      buildDiagramMetadataTextDrafts({
        baseDocument,
        draftDocument,
        entities,
        metadataTextByEntityId: { "focus_tree:C08_PARTIV": metadataText }
      })
    ).toEqual([
      {
        entityId: "focus_tree:C08_PARTIV",
        slot: "meta",
        text: [
          "type: focus_tree",
          "settings:",
          "    source_focuses:",
          "    -   folder: C08_OLD",
          "        focus_id: FOCUS_OLD",
          "        source_path: C08_OLD",
          "        x: '10'",
          "        y: '0'",
          "    -   folder: C08_NEW",
          "        focus_id: FOCUS_NEW",
          "        source_path: C08_NEW",
          "        x: '12'",
          "        y: '0'",
          "    -   folder: C08_CHILD",
          "        focus_id: FOCUS_CHILD",
          "        source_path: C08_CHILD",
          "        prerequisites:",
          "        - FOCUS_NEW",
          "        dx: '1'",
          "        dy: '1'",
          "    focuses:",
          "    -   id: FOCUS_OLD",
          "        x: '10'",
          "        y: '0'",
          "    -   id: FOCUS_NEW",
          "        x: '12'",
          "        y: '0'",
          "    -   id: FOCUS_CHILD",
          "        x: '11'",
          "        y: '1'",
          "        prerequisites:",
          "        - FOCUS_OLD",
          ""
        ].join("\n")
      }
    ]);
  });

  it("persists changed PIHC3 focus visual parents in focus tree metadata text", () => {
    const setDiagramTreeParent = (layoutModel as typeof layoutModel & { setDiagramTreeParent?: DiagramTreeParentSetter }).setDiagramTreeParent;
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
        sources: [{ slot: "meta", name: "meta.yaml", path: "/workspace/projects/PIHC3/src/modules/focus_tree/C08_PARTIV/meta.yaml", relative_path: "src/modules/focus_tree/C08_PARTIV/meta.yaml", extension: "yaml" }],
        metadata: {
          settings: {
            focuses: [
              { id: "FOCUS_ROOT", x: "12", y: "0" },
              { id: "FOCUS_NEW_PARENT", x: "16", y: "1" },
              { id: "FOCUS_CHILD", parent: "FOCUS_ROOT", x: "12", y: "2", prerequisites: ["FOCUS_ROOT"] }
            ]
          }
        }
      }
    ]);
    const baseDocument = buildProjectDiagramDocument(browser, "focuses");
    const draftDocument = setDiagramTreeParent?.(baseDocument, "FOCUS_CHILD", "FOCUS_NEW_PARENT") ?? baseDocument;
    const entities = buildModuleEntities(browser, "focuses", "en");
    const metadataText = [
      "type: focus_tree",
      "settings:",
      "    focuses:",
      "    -   id: FOCUS_ROOT",
      "        x: '12'",
      "        y: '0'",
      "    -   id: FOCUS_NEW_PARENT",
      "        x: '16'",
      "        y: '1'",
      "    -   id: FOCUS_CHILD",
      "        parent: FOCUS_ROOT",
      "        x: '12'",
      "        y: '2'",
      "        prerequisites:",
      "        - FOCUS_ROOT",
      ""
    ].join("\n");

    expect(changedDiagramMetadataEntityIds(baseDocument, draftDocument)).toEqual(["focus_tree:C08_PARTIV"]);
    expect(
      buildDiagramMetadataTextDrafts({
        baseDocument,
        draftDocument,
        entities,
        metadataTextByEntityId: { "focus_tree:C08_PARTIV": metadataText }
      })
    ).toEqual([
      {
        entityId: "focus_tree:C08_PARTIV",
        slot: "meta",
        text: [
          "type: focus_tree",
          "settings:",
          "    focuses:",
          "    -   id: FOCUS_ROOT",
          "        x: '12'",
          "        y: '0'",
          "    -   id: FOCUS_NEW_PARENT",
          "        x: '16'",
          "        y: '1'",
          "    -   id: FOCUS_CHILD",
          "        parent: FOCUS_NEW_PARENT",
          "        x: '12'",
          "        y: '2'",
          "        prerequisites:",
          "        - FOCUS_ROOT",
          ""
        ].join("\n")
      }
    ]);
  });

  it("updates migrated PIHC source focus visual parents before compiled focus positions", () => {
    const setDiagramTreeParent = (layoutModel as typeof layoutModel & { setDiagramTreeParent?: DiagramTreeParentSetter }).setDiagramTreeParent;
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
        sources: [{ slot: "meta", name: "meta.yaml", path: "/workspace/projects/PIHC3/src/modules/focus_tree/C08_PARTIV/meta.yaml", relative_path: "src/modules/focus_tree/C08_PARTIV/meta.yaml", extension: "yaml" }],
        metadata: {
          settings: {
            source_focuses: [
              { folder: "C08_ROOT", focus_id: "FOCUS_ROOT", source_path: "C08_ROOT", x: "10", y: "0" },
              { folder: "C08_OTHER", focus_id: "FOCUS_OTHER", source_path: "C08_OTHER", x: "14", y: "0" },
              { folder: "C08_CHILD", focus_id: "FOCUS_CHILD", source_path: "C08_CHILD", parent: "FOCUS_ROOT", dx: "2", dy: "1", priority: "10" }
            ],
            focuses: [
              { id: "FOCUS_ROOT", x: "10", y: "0" },
              { id: "FOCUS_OTHER", x: "14", y: "0" },
              { id: "FOCUS_CHILD", x: "12", y: "1", prerequisites: ["FOCUS_ROOT"] }
            ]
          }
        }
      }
    ]);
    const baseDocument = buildProjectDiagramDocument(browser, "focuses");
    const draftDocument = setDiagramTreeParent?.(baseDocument, "FOCUS_CHILD", "FOCUS_OTHER") ?? baseDocument;
    const entities = buildModuleEntities(browser, "focuses", "en");
    const metadataText = [
      "type: focus_tree",
      "settings:",
      "    source_focuses:",
      "    -   folder: C08_ROOT",
      "        focus_id: FOCUS_ROOT",
      "        source_path: C08_ROOT",
      "        x: '10'",
      "        y: '0'",
      "    -   folder: C08_OTHER",
      "        focus_id: FOCUS_OTHER",
      "        source_path: C08_OTHER",
      "        x: '14'",
      "        y: '0'",
      "    -   folder: C08_CHILD",
      "        focus_id: FOCUS_CHILD",
      "        source_path: C08_CHILD",
      "        parent: FOCUS_ROOT",
      "        dx: '2'",
      "        dy: '1'",
      "        priority: '10'",
      "    focuses:",
      "    -   id: FOCUS_ROOT",
      "        x: '10'",
      "        y: '0'",
      "    -   id: FOCUS_OTHER",
      "        x: '14'",
      "        y: '0'",
      "    -   id: FOCUS_CHILD",
      "        x: '12'",
      "        y: '1'",
      "        prerequisites:",
      "        - FOCUS_ROOT",
      ""
    ].join("\n");

    expect(changedDiagramMetadataEntityIds(baseDocument, draftDocument)).toEqual(["focus_tree:C08_PARTIV"]);
    expect(
      buildDiagramMetadataTextDrafts({
        baseDocument,
        draftDocument,
        entities,
        metadataTextByEntityId: { "focus_tree:C08_PARTIV": metadataText }
      })
    ).toEqual([
      {
        entityId: "focus_tree:C08_PARTIV",
        slot: "meta",
        text: [
          "type: focus_tree",
          "settings:",
          "    source_focuses:",
          "    -   folder: C08_ROOT",
          "        focus_id: FOCUS_ROOT",
          "        source_path: C08_ROOT",
          "        x: '10'",
          "        y: '0'",
          "    -   folder: C08_OTHER",
          "        focus_id: FOCUS_OTHER",
          "        source_path: C08_OTHER",
          "        x: '14'",
          "        y: '0'",
          "    -   folder: C08_CHILD",
          "        focus_id: FOCUS_CHILD",
          "        source_path: C08_CHILD",
          "        parent: FOCUS_OTHER",
          "        dx: '-2'",
          "        dy: '2'",
          "        priority: '10'",
          "    focuses:",
          "    -   id: FOCUS_ROOT",
          "        x: '10'",
          "        y: '0'",
          "    -   id: FOCUS_OTHER",
          "        x: '14'",
          "        y: '0'",
          "    -   id: FOCUS_CHILD",
          "        x: '12'",
          "        y: '1'",
          "        prerequisites:",
          "        - FOCUS_ROOT",
          ""
        ].join("\n")
      }
    ]);
  });

  it("persists PIHC3 relative focus reparenting through relative offsets only", () => {
    const setDiagramTreeParent = (layoutModel as typeof layoutModel & { setDiagramTreeParent?: DiagramTreeParentSetter }).setDiagramTreeParent;
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
        sources: [{ slot: "meta", name: "meta.yaml", path: "/workspace/projects/PIHC3/src/modules/focus_tree/C08_PARTIV/meta.yaml", relative_path: "src/modules/focus_tree/C08_PARTIV/meta.yaml", extension: "yaml" }],
        metadata: {
          settings: {
            focuses: [
              { id: "FOCUS_ROOT", x: "10", y: "0" },
              { id: "FOCUS_NEW_PARENT", x: "16", y: "1" },
              { id: "FOCUS_CHILD", relative_position_id: "FOCUS_ROOT", x: "1", y: "1", prerequisites: ["FOCUS_ROOT"] }
            ]
          }
        }
      }
    ]);
    const baseDocument = buildProjectDiagramDocument(browser, "focuses");
    const draftDocument = setDiagramTreeParent?.(baseDocument, "FOCUS_CHILD", "FOCUS_NEW_PARENT") ?? baseDocument;
    const entities = buildModuleEntities(browser, "focuses", "en");
    const metadataText = [
      "type: focus_tree",
      "settings:",
      "    focuses:",
      "    -   id: FOCUS_ROOT",
      "        x: '10'",
      "        y: '0'",
      "    -   id: FOCUS_NEW_PARENT",
      "        x: '16'",
      "        y: '1'",
      "    -   id: FOCUS_CHILD",
      "        relative_position_id: FOCUS_ROOT",
      "        x: '1'",
      "        y: '1'",
      "        prerequisites:",
      "        - FOCUS_ROOT",
      ""
    ].join("\n");

    expect(changedDiagramMetadataEntityIds(baseDocument, draftDocument)).toEqual(["focus_tree:C08_PARTIV"]);
    expect(
      buildDiagramMetadataTextDrafts({
        baseDocument,
        draftDocument,
        entities,
        metadataTextByEntityId: { "focus_tree:C08_PARTIV": metadataText }
      })
    ).toEqual([
      {
        entityId: "focus_tree:C08_PARTIV",
        slot: "meta",
        text: [
          "type: focus_tree",
          "settings:",
          "    focuses:",
          "    -   id: FOCUS_ROOT",
          "        x: '10'",
          "        y: '0'",
          "    -   id: FOCUS_NEW_PARENT",
          "        x: '16'",
          "        y: '1'",
          "    -   id: FOCUS_CHILD",
          "        relative_position_id: FOCUS_NEW_PARENT",
          "        x: '-5'",
          "        y: '0'",
          "        prerequisites:",
          "        - FOCUS_ROOT",
          ""
        ].join("\n")
      }
    ]);
  });

  it("removes PIHC3 focus visual parent metadata when a focus becomes a root", () => {
    const clearDiagramTreeParent = (layoutModel as typeof layoutModel & { clearDiagramTreeParent?: DiagramTreeParentClearer }).clearDiagramTreeParent;
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
        sources: [{ slot: "meta", name: "meta.yaml", path: "/workspace/projects/PIHC3/src/modules/focus_tree/C08_PARTIV/meta.yaml", relative_path: "src/modules/focus_tree/C08_PARTIV/meta.yaml", extension: "yaml" }],
        metadata: {
          settings: {
            focuses: [
              { id: "FOCUS_ROOT", x: "12", y: "0" },
              { id: "FOCUS_CHILD", parent: "FOCUS_ROOT", x: "12", y: "2", prerequisites: ["FOCUS_ROOT"] }
            ]
          }
        }
      }
    ]);
    const baseDocument = buildProjectDiagramDocument(browser, "focuses");
    const draftDocument = clearDiagramTreeParent?.(baseDocument, "FOCUS_CHILD") ?? baseDocument;
    const entities = buildModuleEntities(browser, "focuses", "en");
    const metadataText = [
      "type: focus_tree",
      "settings:",
      "    focuses:",
      "    -   id: FOCUS_ROOT",
      "        x: '12'",
      "        y: '0'",
      "    -   id: FOCUS_CHILD",
      "        parent: FOCUS_ROOT",
      "        x: '12'",
      "        y: '2'",
      "        prerequisites:",
      "        - FOCUS_ROOT",
      ""
    ].join("\n");

    expect(changedDiagramMetadataEntityIds(baseDocument, draftDocument)).toEqual(["focus_tree:C08_PARTIV"]);
    expect(
      buildDiagramMetadataTextDrafts({
        baseDocument,
        draftDocument,
        entities,
        metadataTextByEntityId: { "focus_tree:C08_PARTIV": metadataText }
      })
    ).toEqual([
      {
        entityId: "focus_tree:C08_PARTIV",
        slot: "meta",
        text: [
          "type: focus_tree",
          "settings:",
          "    focuses:",
          "    -   id: FOCUS_ROOT",
          "        x: '12'",
          "        y: '0'",
          "    -   id: FOCUS_CHILD",
          "        x: '12'",
          "        y: '2'",
          "        prerequisites:",
          "        - FOCUS_ROOT",
          ""
        ].join("\n")
      }
    ]);
  });

  it("removes migrated PIHC source focus visual parent metadata before compiled focus positions", () => {
    const clearDiagramTreeParent = (layoutModel as typeof layoutModel & { clearDiagramTreeParent?: DiagramTreeParentClearer }).clearDiagramTreeParent;
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
        sources: [{ slot: "meta", name: "meta.yaml", path: "/workspace/projects/PIHC3/src/modules/focus_tree/C08_PARTIV/meta.yaml", relative_path: "src/modules/focus_tree/C08_PARTIV/meta.yaml", extension: "yaml" }],
        metadata: {
          settings: {
            source_focuses: [
              { folder: "C08_ROOT", focus_id: "FOCUS_ROOT", source_path: "C08_ROOT", x: "10", y: "0" },
              { folder: "C08_CHILD", focus_id: "FOCUS_CHILD", source_path: "C08_CHILD", parent: "FOCUS_ROOT", dx: "2", dy: "1", priority: "10" }
            ],
            focuses: [
              { id: "FOCUS_ROOT", x: "10", y: "0" },
              { id: "FOCUS_CHILD", x: "12", y: "1", prerequisites: ["FOCUS_ROOT"] }
            ]
          }
        }
      }
    ]);
    const baseDocument = buildProjectDiagramDocument(browser, "focuses");
    const draftDocument = clearDiagramTreeParent?.(baseDocument, "FOCUS_CHILD") ?? baseDocument;
    const entities = buildModuleEntities(browser, "focuses", "en");
    const metadataText = [
      "type: focus_tree",
      "settings:",
      "    source_focuses:",
      "    -   folder: C08_ROOT",
      "        focus_id: FOCUS_ROOT",
      "        source_path: C08_ROOT",
      "        x: '10'",
      "        y: '0'",
      "    -   folder: C08_CHILD",
      "        focus_id: FOCUS_CHILD",
      "        source_path: C08_CHILD",
      "        parent: FOCUS_ROOT",
      "        dx: '2'",
      "        dy: '1'",
      "        priority: '10'",
      "    focuses:",
      "    -   id: FOCUS_ROOT",
      "        x: '10'",
      "        y: '0'",
      "    -   id: FOCUS_CHILD",
      "        x: '12'",
      "        y: '1'",
      "        prerequisites:",
      "        - FOCUS_ROOT",
      ""
    ].join("\n");

    expect(changedDiagramMetadataEntityIds(baseDocument, draftDocument)).toEqual(["focus_tree:C08_PARTIV"]);
    expect(
      buildDiagramMetadataTextDrafts({
        baseDocument,
        draftDocument,
        entities,
        metadataTextByEntityId: { "focus_tree:C08_PARTIV": metadataText }
      })
    ).toEqual([
      {
        entityId: "focus_tree:C08_PARTIV",
        slot: "meta",
        text: [
          "type: focus_tree",
          "settings:",
          "    source_focuses:",
          "    -   folder: C08_ROOT",
          "        focus_id: FOCUS_ROOT",
          "        source_path: C08_ROOT",
          "        x: '10'",
          "        y: '0'",
          "    -   folder: C08_CHILD",
          "        focus_id: FOCUS_CHILD",
          "        source_path: C08_CHILD",
          "        x: 12",
          "        y: 2",
          "        priority: '10'",
          "    focuses:",
          "    -   id: FOCUS_ROOT",
          "        x: '10'",
          "        y: '0'",
          "    -   id: FOCUS_CHILD",
          "        x: '12'",
          "        y: '1'",
          "        prerequisites:",
          "        - FOCUS_ROOT",
          ""
        ].join("\n")
      }
    ]);
  });

  it("removes PIHC3 technology folder positions when a node returns to auto layout", () => {
    const browser = browserPayload([
      {
        id: "technology:TECH_FIREARM",
        kind: "module",
        layout: "canonical",
        family_id: "technologies",
        family: "technology",
        object_id: "TECH_FIREARM",
        module_id: "TECH_FIREARM",
        title: "Firearm",
        root: "/workspace/projects/PIHC3/src/modules/technology/TECH_FIREARM",
        relative_root: "src/modules/technology/TECH_FIREARM",
        source_count: 1,
        sources: [{ slot: "meta", name: "meta.yaml", path: "/workspace/projects/PIHC3/src/modules/technology/TECH_FIREARM/meta.yaml", relative_path: "src/modules/technology/TECH_FIREARM/meta.yaml", extension: "yaml" }],
        metadata: { settings: { folder: { name: "infantry_folder", position: { x: 4, y: 3 } }, folder_position: { x: 4, y: 3 } } }
      }
    ]);
    const baseDocument = buildProjectDiagramDocument(browser, "technologies");
    const draftDocument = autoLayoutDiagramNode(baseDocument, "TECH_FIREARM");
    const entities = buildModuleEntities(browser, "technologies", "en");
    const metadataText = [
      "type: technology",
      "settings:",
      "    folder:",
      "        name: infantry_folder",
      "        position:",
      "            x: 4",
      "            y: 3",
      "    folder_position:",
      "        x: 4",
      "        y: 3",
      ""
    ].join("\n");

    expect(
      buildDiagramMetadataTextDrafts({
        baseDocument,
        draftDocument,
        entities,
        metadataTextByEntityId: { "technology:TECH_FIREARM": metadataText }
      })
    ).toEqual([
      {
        entityId: "technology:TECH_FIREARM",
        slot: "meta",
        text: ["type: technology", "settings:", "    folder:", "        name: infantry_folder", ""].join("\n")
      }
    ]);
  });

  it("updates only the moved focus entry in focus tree metadata text", () => {
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
        sources: [{ slot: "meta", name: "meta.yaml", path: "/workspace/projects/PIHC3/src/modules/focus_tree/C08_PARTIV/meta.yaml", relative_path: "src/modules/focus_tree/C08_PARTIV/meta.yaml", extension: "yaml" }],
        metadata: {
          settings: {
            focuses: [
              { id: "FOCUS_ROOT", x: "12", y: "0" },
              { id: "FOCUS_CHILD", x: "12", y: "1", prerequisites: ["FOCUS_ROOT"] }
            ]
          }
        }
      }
    ]);
    const baseDocument = buildProjectDiagramDocument(browser, "focuses");
    const draftDocument = moveDiagramNode(baseDocument, "FOCUS_CHILD", { dx: -3, dy: 2 });
    const entities = buildModuleEntities(browser, "focuses", "en");
    const metadataText = [
      "type: focus_tree",
      "settings:",
      "    focuses:",
      "    -   id: FOCUS_ROOT",
      "        x: '12'",
      "        y: '0'",
      "    -   id: FOCUS_CHILD",
      "        x: '12'",
      "        y: '1'",
      "        prerequisites:",
      "        - FOCUS_ROOT",
      ""
    ].join("\n");

    expect(
      buildDiagramMetadataTextDrafts({
        baseDocument,
        draftDocument,
        entities,
        metadataTextByEntityId: { "focus_tree:C08_PARTIV": metadataText }
      })
    ).toEqual([
      {
        entityId: "focus_tree:C08_PARTIV",
        slot: "meta",
        text: [
          "type: focus_tree",
          "settings:",
          "    focuses:",
          "    -   id: FOCUS_ROOT",
          "        x: '12'",
          "        y: '0'",
          "    -   id: FOCUS_CHILD",
          "        x: '9'",
          "        y: '3'",
          "        prerequisites:",
          "        - FOCUS_ROOT",
          ""
        ].join("\n")
      }
    ]);
  });

  it("persists PIHC3 focus sibling reorder as focus list order", () => {
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
        sources: [{ slot: "meta", name: "meta.yaml", path: "/workspace/projects/PIHC3/src/modules/focus_tree/C08_PARTIV/meta.yaml", relative_path: "src/modules/focus_tree/C08_PARTIV/meta.yaml", extension: "yaml" }],
        metadata: {
          settings: {
            focuses: [
              { id: "FOCUS_ROOT", x: "12", y: "0" },
              { id: "FOCUS_ALPHA", parent: "FOCUS_ROOT", x: "10", y: "1" },
              { id: "FOCUS_BETA", parent: "FOCUS_ROOT", x: "14", y: "1" }
            ]
          }
        }
      }
    ]);
    const baseDocument = buildProjectDiagramDocument(browser, "focuses");
    const draftDocument = reorderDiagramSibling(baseDocument, "FOCUS_BETA", -1);
    const entities = buildModuleEntities(browser, "focuses", "en");
    const metadataText = [
      "type: focus_tree",
      "settings:",
      "    focuses:",
      "    -   id: FOCUS_ROOT",
      "        x: '12'",
      "        y: '0'",
      "    -   id: FOCUS_ALPHA",
      "        parent: FOCUS_ROOT",
      "        x: '10'",
      "        y: '1'",
      "    -   id: FOCUS_BETA",
      "        parent: FOCUS_ROOT",
      "        x: '14'",
      "        y: '1'",
      ""
    ].join("\n");

    expect(
      buildDiagramMetadataTextDrafts({
        baseDocument,
        draftDocument,
        entities,
        metadataTextByEntityId: { "focus_tree:C08_PARTIV": metadataText }
      })
    ).toEqual([
      {
        entityId: "focus_tree:C08_PARTIV",
        slot: "meta",
        text: [
          "type: focus_tree",
          "settings:",
          "    focuses:",
          "    -   id: FOCUS_ROOT",
          "        x: '12'",
          "        y: '0'",
          "    -   id: FOCUS_BETA",
          "        parent: FOCUS_ROOT",
          "        x: '14'",
          "        y: '1'",
          "    -   id: FOCUS_ALPHA",
          "        parent: FOCUS_ROOT",
          "        x: '10'",
          "        y: '1'",
          ""
        ].join("\n")
      }
    ]);
  });

  it("persists moved PIHC3 relative focus positions as parent offsets", () => {
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
        sources: [{ slot: "meta", name: "meta.yaml", path: "/workspace/projects/PIHC3/src/modules/focus_tree/C08_PARTIV/meta.yaml", relative_path: "src/modules/focus_tree/C08_PARTIV/meta.yaml", extension: "yaml" }],
        metadata: {
          settings: {
            focuses: [
              { id: "FOCUS_ROOT", x: "10", y: "0" },
              { id: "FOCUS_CHILD", relative_position_id: "FOCUS_ROOT", x: "1", y: "1" }
            ]
          }
        }
      }
    ]);
    const baseDocument = buildProjectDiagramDocument(browser, "focuses");
    const draftDocument = moveDiagramNode(baseDocument, "FOCUS_CHILD", { dx: 2, dy: 0 });
    const entities = buildModuleEntities(browser, "focuses", "en");
    const metadataText = [
      "type: focus_tree",
      "settings:",
      "    focuses:",
      "    -   id: FOCUS_ROOT",
      "        x: '10'",
      "        y: '0'",
      "    -   id: FOCUS_CHILD",
      "        relative_position_id: FOCUS_ROOT",
      "        x: '1'",
      "        y: '1'",
      ""
    ].join("\n");

    expect(
      buildDiagramMetadataTextDrafts({
        baseDocument,
        draftDocument,
        entities,
        metadataTextByEntityId: { "focus_tree:C08_PARTIV": metadataText }
      })
    ).toEqual([
      {
        entityId: "focus_tree:C08_PARTIV",
        slot: "meta",
        text: [
          "type: focus_tree",
          "settings:",
          "    focuses:",
          "    -   id: FOCUS_ROOT",
          "        x: '10'",
          "        y: '0'",
          "    -   id: FOCUS_CHILD",
          "        relative_position_id: FOCUS_ROOT",
          "        x: '3'",
          "        y: '1'",
          ""
        ].join("\n")
      }
    ]);
  });

  it("preserves legacy PIHC focus parent offsets when moved", () => {
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
        sources: [{ slot: "meta", name: "meta.yaml", path: "/workspace/projects/PIHC3/src/modules/focus_tree/C08_PARTIV/meta.yaml", relative_path: "src/modules/focus_tree/C08_PARTIV/meta.yaml", extension: "yaml" }],
        metadata: {
          settings: {
            focuses: [
              { id: "FOCUS_ROOT", x: "10", y: "0" },
              { id: "FOCUS_CHILD", parent: "FOCUS_ROOT", dx: "2", dy: "1", priority: "10", prerequisites: ["FOCUS_ROOT"] }
            ]
          }
        }
      }
    ]);
    const baseDocument = buildProjectDiagramDocument(browser, "focuses");
    const draftDocument = moveDiagramNode(baseDocument, "FOCUS_CHILD", { dx: 1, dy: -1 });
    const entities = buildModuleEntities(browser, "focuses", "en");
    const metadataText = [
      "type: focus_tree",
      "settings:",
      "    focuses:",
      "    -   id: FOCUS_ROOT",
      "        x: '10'",
      "        y: '0'",
      "    -   id: FOCUS_CHILD",
      "        parent: FOCUS_ROOT",
      "        dx: '2'",
      "        dy: '1'",
      "        priority: '10'",
      "        prerequisites:",
      "        - FOCUS_ROOT",
      ""
    ].join("\n");

    expect(
      buildDiagramMetadataTextDrafts({
        baseDocument,
        draftDocument,
        entities,
        metadataTextByEntityId: { "focus_tree:C08_PARTIV": metadataText }
      })
    ).toEqual([
      {
        entityId: "focus_tree:C08_PARTIV",
        slot: "meta",
        text: [
          "type: focus_tree",
          "settings:",
          "    focuses:",
          "    -   id: FOCUS_ROOT",
          "        x: '10'",
          "        y: '0'",
          "    -   id: FOCUS_CHILD",
          "        parent: FOCUS_ROOT",
          "        dx: '3'",
          "        dy: '0'",
          "        priority: '10'",
          "        prerequisites:",
          "        - FOCUS_ROOT",
          ""
        ].join("\n")
      }
    ]);
  });

  it("updates migrated PIHC source focus offsets before compiled focus positions", () => {
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
        sources: [{ slot: "meta", name: "meta.yaml", path: "/workspace/projects/PIHC3/src/modules/focus_tree/C08_PARTIV/meta.yaml", relative_path: "src/modules/focus_tree/C08_PARTIV/meta.yaml", extension: "yaml" }],
        metadata: {
          settings: {
            source_focuses: [
              { folder: "C08_ROOT", focus_id: "FOCUS_ROOT", source_path: "C08_ROOT", x: "10", y: "0" },
              { folder: "C08_CHILD", focus_id: "FOCUS_CHILD", source_path: "C08_CHILD", parent: "FOCUS_ROOT", dx: "2", dy: "1", priority: "10" }
            ],
            focuses: [
              { id: "FOCUS_ROOT", x: "10", y: "0" },
              { id: "FOCUS_CHILD", x: "12", y: "1", prerequisites: ["FOCUS_ROOT"] }
            ]
          }
        }
      }
    ]);
    const baseDocument = buildProjectDiagramDocument(browser, "focuses");
    const draftDocument = moveDiagramNode(baseDocument, "FOCUS_CHILD", { dx: 1, dy: -1 });
    const entities = buildModuleEntities(browser, "focuses", "en");
    const metadataText = [
      "type: focus_tree",
      "settings:",
      "    source_focuses:",
      "    -   folder: C08_ROOT",
      "        focus_id: FOCUS_ROOT",
      "        source_path: C08_ROOT",
      "        x: '10'",
      "        y: '0'",
      "    -   folder: C08_CHILD",
      "        focus_id: FOCUS_CHILD",
      "        source_path: C08_CHILD",
      "        parent: FOCUS_ROOT",
      "        dx: '2'",
      "        dy: '1'",
      "        priority: '10'",
      "    focuses:",
      "    -   id: FOCUS_ROOT",
      "        x: '10'",
      "        y: '0'",
      "    -   id: FOCUS_CHILD",
      "        x: '12'",
      "        y: '1'",
      "        prerequisites:",
      "        - FOCUS_ROOT",
      ""
    ].join("\n");

    expect(changedDiagramMetadataEntityIds(baseDocument, draftDocument)).toEqual(["focus_tree:C08_PARTIV"]);
    expect(
      buildDiagramMetadataTextDrafts({
        baseDocument,
        draftDocument,
        entities,
        metadataTextByEntityId: { "focus_tree:C08_PARTIV": metadataText }
      })
    ).toEqual([
      {
        entityId: "focus_tree:C08_PARTIV",
        slot: "meta",
        text: [
          "type: focus_tree",
          "settings:",
          "    source_focuses:",
          "    -   folder: C08_ROOT",
          "        focus_id: FOCUS_ROOT",
          "        source_path: C08_ROOT",
          "        x: '10'",
          "        y: '0'",
          "    -   folder: C08_CHILD",
          "        focus_id: FOCUS_CHILD",
          "        source_path: C08_CHILD",
          "        parent: FOCUS_ROOT",
          "        dx: '3'",
          "        dy: '0'",
          "        priority: '10'",
          "    focuses:",
          "    -   id: FOCUS_ROOT",
          "        x: '10'",
          "        y: '0'",
          "    -   id: FOCUS_CHILD",
          "        x: '12'",
          "        y: '1'",
          "        prerequisites:",
          "        - FOCUS_ROOT",
          ""
        ].join("\n")
      }
    ]);
  });

  it("updates migrated PIHC source focus info json when source text is available", () => {
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
        source_root: "/workspace/projects/PIHC3/src",
        source_root_relative_path: "src",
        source_count: 1,
        sources: [{ slot: "meta", name: "meta.yaml", path: "/workspace/projects/PIHC3/src/modules/focus_tree/C08_PARTIV/meta.yaml", relative_path: "src/modules/focus_tree/C08_PARTIV/meta.yaml", extension: "yaml" }],
        metadata: {
          settings: {
            source_focuses: [
              { folder: "C08_ROOT", focus_id: "FOCUS_ROOT", source_path: "C08_ROOT", x: "10", y: "0" },
              { folder: "C08_CHILD", focus_id: "FOCUS_CHILD", source_path: "C08_CHILD", parent: "FOCUS_ROOT", dx: "2", dy: "1", priority: "10" }
            ],
            focuses: [
              { id: "FOCUS_ROOT", x: "10", y: "0" },
              { id: "FOCUS_CHILD", x: "12", y: "1", prerequisites: ["FOCUS_ROOT"] }
            ]
          }
        }
      }
    ]);
    const baseDocument = buildProjectDiagramDocument(browser, "focuses");
    const draftDocument = moveDiagramNode(baseDocument, "FOCUS_CHILD", { dx: 1, dy: -1 });
    const entities = buildModuleEntities(browser, "focuses", "en");
    const metadataText = [
      "type: focus_tree",
      "settings:",
      "    source_focuses:",
      "    -   folder: C08_ROOT",
      "        focus_id: FOCUS_ROOT",
      "        source_path: C08_ROOT",
      "        x: '10'",
      "        y: '0'",
      "    -   folder: C08_CHILD",
      "        focus_id: FOCUS_CHILD",
      "        source_path: C08_CHILD",
      "        parent: FOCUS_ROOT",
      "        dx: '2'",
      "        dy: '1'",
      "        priority: '10'",
      ""
    ].join("\n");
    const sourceInfoPath = "/workspace/projects/PIHC3/src/modules/focus_tree/C08_PARTIV/legacy/C08_CHILD/info.json";
    const sourceInfoText = `${JSON.stringify(
      {
        tree: "C08_PARTIV",
        parent: "FOCUS_ROOT",
        dx: 2,
        dy: 1,
        priority: 10,
        prerequisite: { focus: "FOCUS_ROOT" }
      },
      null,
      4
    )}\n`;

    expect(changedDiagramMetadataSourceInfoPaths(baseDocument, draftDocument)).toEqual([sourceInfoPath]);
    const drafts = buildDiagramMetadataTextDrafts({
      baseDocument,
      draftDocument,
      entities,
      metadataTextByEntityId: { "focus_tree:C08_PARTIV": metadataText },
      sourceTextByPath: { [sourceInfoPath]: sourceInfoText }
    });

    expect(drafts).toContainEqual({
      entityId: "focus_tree:C08_PARTIV",
      slot: "source",
      path: sourceInfoPath,
      text: `${JSON.stringify(
        {
          tree: "C08_PARTIV",
          parent: "FOCUS_ROOT",
          dx: 3,
          dy: 0,
          priority: 10,
          prerequisite: { focus: "FOCUS_ROOT" }
        },
        null,
        4
      )}\n`
    });
    expect(sourceTextEditsForDiagramMetadataDrafts(entities, drafts)).toContainEqual({
      path: sourceInfoPath,
      text: expect.stringContaining('"dx": 3')
    });
  });

  it("preserves migrated PIHC source focus info json explicit roots when clearing a visual parent", () => {
    const clearDiagramTreeParent = (layoutModel as typeof layoutModel & { clearDiagramTreeParent?: DiagramTreeParentClearer }).clearDiagramTreeParent;
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
        source_root: "/workspace/projects/PIHC3/src",
        source_root_relative_path: "src",
        source_count: 1,
        sources: [{ slot: "meta", name: "meta.yaml", path: "/workspace/projects/PIHC3/src/modules/focus_tree/C08_PARTIV/meta.yaml", relative_path: "src/modules/focus_tree/C08_PARTIV/meta.yaml", extension: "yaml" }],
        metadata: {
          settings: {
            source_focuses: [
              { folder: "C08_ROOT", focus_id: "FOCUS_ROOT", source_path: "C08_ROOT", x: "10", y: "0" },
              { folder: "C08_CHILD", focus_id: "FOCUS_CHILD", source_path: "C08_CHILD", parent: "FOCUS_ROOT", dx: "2", dy: "1", priority: "10" }
            ],
            focuses: [
              { id: "FOCUS_ROOT", x: "10", y: "0" },
              { id: "FOCUS_CHILD", x: "12", y: "1", prerequisites: ["FOCUS_ROOT"] }
            ]
          }
        }
      }
    ]);
    const baseDocument = buildProjectDiagramDocument(browser, "focuses");
    const draftDocument = clearDiagramTreeParent?.(baseDocument, "FOCUS_CHILD") ?? baseDocument;
    const entities = buildModuleEntities(browser, "focuses", "en");
    const sourceInfoPath = "/workspace/projects/PIHC3/src/modules/focus_tree/C08_PARTIV/legacy/C08_CHILD/info.json";
    const drafts = buildDiagramMetadataTextDrafts({
      baseDocument,
      draftDocument,
      entities,
      metadataTextByEntityId: {
        "focus_tree:C08_PARTIV": [
          "type: focus_tree",
          "settings:",
          "    source_focuses:",
          "    -   folder: C08_ROOT",
          "        focus_id: FOCUS_ROOT",
          "        source_path: C08_ROOT",
          "        x: '10'",
          "        y: '0'",
          "    -   folder: C08_CHILD",
          "        focus_id: FOCUS_CHILD",
          "        source_path: C08_CHILD",
          "        parent: FOCUS_ROOT",
          "        dx: '2'",
          "        dy: '1'",
          "        priority: '10'",
          ""
        ].join("\n")
      },
      sourceTextByPath: {
        [sourceInfoPath]: `${JSON.stringify({ tree: "C08_PARTIV", parent: "FOCUS_ROOT", dx: 2, dy: 1, priority: 10, prerequisite: { focus: "FOCUS_ROOT" } }, null, 4)}\n`
      }
    });

    expect(changedDiagramMetadataSourceInfoPaths(baseDocument, draftDocument)).toEqual([sourceInfoPath]);
    expect(drafts).toContainEqual({
      entityId: "focus_tree:C08_PARTIV",
      slot: "source",
      path: sourceInfoPath,
      text: `${JSON.stringify({ tree: "C08_PARTIV", parent: null, priority: 10, prerequisite: { focus: "FOCUS_ROOT" }, x: 12, y: 2 }, null, 4)}\n`
    });
  });

  it("updates migrated PIHC source focus info json relationships when source text is available", () => {
    const setDiagramReferenceEdge = (layoutModel as typeof layoutModel & { setDiagramReferenceEdge?: DiagramReferenceEdgeSetter }).setDiagramReferenceEdge;
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
        source_root: "/workspace/projects/PIHC3/src",
        source_root_relative_path: "src",
        source_count: 1,
        sources: [{ slot: "meta", name: "meta.yaml", path: "/workspace/projects/PIHC3/src/modules/focus_tree/C08_PARTIV/meta.yaml", relative_path: "src/modules/focus_tree/C08_PARTIV/meta.yaml", extension: "yaml" }],
        metadata: {
          settings: {
            source_focuses: [
              { folder: "C08_ROOT", focus_id: "FOCUS_ROOT", source_path: "C08_ROOT", x: "10", y: "0" },
              { folder: "C08_CHILD", focus_id: "FOCUS_CHILD", source_path: "C08_CHILD", prerequisite: "FOCUS_OLD", dx: "2", dy: "1" },
              { folder: "C08_OTHER", focus_id: "FOCUS_OTHER", source_path: "C08_OTHER", x: "14", y: "0" }
            ],
            focuses: [
              { id: "FOCUS_ROOT", x: "10", y: "0" },
              { id: "FOCUS_CHILD", prerequisites: ["FOCUS_OLD"], x: "12", y: "1" },
              { id: "FOCUS_OTHER", x: "14", y: "0" }
            ]
          }
        }
      }
    ]);
    const baseDocument = buildProjectDiagramDocument(browser, "focuses");
    const withDependency = setDiagramDependencyEdge(baseDocument, "FOCUS_ROOT", "FOCUS_CHILD", true);
    const draftDocument = setDiagramReferenceEdge?.(withDependency, "FOCUS_ROOT", "FOCUS_OTHER", true) ?? withDependency;
    const entities = buildModuleEntities(browser, "focuses", "en");
    const metadataText = [
      "type: focus_tree",
      "settings:",
      "    source_focuses:",
      "    -   folder: C08_ROOT",
      "        focus_id: FOCUS_ROOT",
      "        source_path: C08_ROOT",
      "        x: '10'",
      "        y: '0'",
      "    -   folder: C08_CHILD",
      "        focus_id: FOCUS_CHILD",
      "        source_path: C08_CHILD",
      "        prerequisite: FOCUS_OLD",
      "        dx: '2'",
      "        dy: '1'",
      "    -   folder: C08_OTHER",
      "        focus_id: FOCUS_OTHER",
      "        source_path: C08_OTHER",
      "        x: '14'",
      "        y: '0'",
      ""
    ].join("\n");
    const rootInfoPath = "/workspace/projects/PIHC3/src/modules/focus_tree/C08_PARTIV/legacy/C08_ROOT/info.json";
    const childInfoPath = "/workspace/projects/PIHC3/src/modules/focus_tree/C08_PARTIV/legacy/C08_CHILD/info.json";
    const drafts = buildDiagramMetadataTextDrafts({
      baseDocument,
      draftDocument,
      entities,
      metadataTextByEntityId: { "focus_tree:C08_PARTIV": metadataText },
      sourceTextByPath: {
        [rootInfoPath]: `${JSON.stringify({ tree: "C08_PARTIV", x: 10, y: 0 }, null, 4)}\n`,
        [childInfoPath]: `${JSON.stringify({ tree: "C08_PARTIV", prerequisite: { focus: "FOCUS_OLD" }, dx: 2, dy: 1 }, null, 4)}\n`
      }
    });

    expect(changedDiagramMetadataSourceInfoPaths(baseDocument, draftDocument)).toEqual([childInfoPath, rootInfoPath]);
    expect(drafts).toContainEqual({
      entityId: "focus_tree:C08_PARTIV",
      slot: "source",
      path: childInfoPath,
      text: `${JSON.stringify({ tree: "C08_PARTIV", dx: 2, dy: 1, prerequisites: ["FOCUS_ROOT"] }, null, 4)}\n`
    });
    expect(drafts).toContainEqual({
      entityId: "focus_tree:C08_PARTIV",
      slot: "source",
      path: rootInfoPath,
      text: `${JSON.stringify({ tree: "C08_PARTIV", x: 10, y: 0, mutually_exclusive: ["FOCUS_OTHER"] }, null, 4)}\n`
    });
  });

  it("updates migrated PIHC source focus coordinates before compiled focus positions", () => {
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
        sources: [{ slot: "meta", name: "meta.yaml", path: "/workspace/projects/PIHC3/src/modules/focus_tree/C08_PARTIV/meta.yaml", relative_path: "src/modules/focus_tree/C08_PARTIV/meta.yaml", extension: "yaml" }],
        metadata: {
          settings: {
            source_focuses: [
              { folder: "C08_ROOT", focus_id: "FOCUS_ROOT", source_path: "C08_ROOT", x: "10", y: "0" },
              { folder: "C08_CHILD", focus_id: "FOCUS_CHILD", source_path: "C08_CHILD", x: "12", y: "1", priority: "10" }
            ],
            focuses: [
              { id: "FOCUS_ROOT", x: "10", y: "0" },
              { id: "FOCUS_CHILD", x: "12", y: "1", prerequisites: ["FOCUS_ROOT"] }
            ]
          }
        }
      }
    ]);
    const baseDocument = buildProjectDiagramDocument(browser, "focuses");
    const draftDocument = moveDiagramNode(baseDocument, "FOCUS_CHILD", { dx: 2, dy: -1 });
    const entities = buildModuleEntities(browser, "focuses", "en");
    const metadataText = [
      "type: focus_tree",
      "settings:",
      "    source_focuses:",
      "    -   folder: C08_ROOT",
      "        focus_id: FOCUS_ROOT",
      "        source_path: C08_ROOT",
      "        x: '10'",
      "        y: '0'",
      "    -   folder: C08_CHILD",
      "        focus_id: FOCUS_CHILD",
      "        source_path: C08_CHILD",
      "        x: '12'",
      "        y: '1'",
      "        priority: '10'",
      "    focuses:",
      "    -   id: FOCUS_ROOT",
      "        x: '10'",
      "        y: '0'",
      "    -   id: FOCUS_CHILD",
      "        x: '12'",
      "        y: '1'",
      "        prerequisites:",
      "        - FOCUS_ROOT",
      ""
    ].join("\n");

    expect(changedDiagramMetadataEntityIds(baseDocument, draftDocument)).toEqual(["focus_tree:C08_PARTIV"]);
    expect(
      buildDiagramMetadataTextDrafts({
        baseDocument,
        draftDocument,
        entities,
        metadataTextByEntityId: { "focus_tree:C08_PARTIV": metadataText }
      })
    ).toEqual([
      {
        entityId: "focus_tree:C08_PARTIV",
        slot: "meta",
        text: [
          "type: focus_tree",
          "settings:",
          "    source_focuses:",
          "    -   folder: C08_ROOT",
          "        focus_id: FOCUS_ROOT",
          "        source_path: C08_ROOT",
          "        x: '10'",
          "        y: '0'",
          "    -   folder: C08_CHILD",
          "        focus_id: FOCUS_CHILD",
          "        source_path: C08_CHILD",
          "        x: '14'",
          "        y: '0'",
          "        priority: '10'",
          "    focuses:",
          "    -   id: FOCUS_ROOT",
          "        x: '10'",
          "        y: '0'",
          "    -   id: FOCUS_CHILD",
          "        x: '12'",
          "        y: '1'",
          "        prerequisites:",
          "        - FOCUS_ROOT",
          ""
        ].join("\n")
      }
    ]);
  });

  it("persists PIHC3 focus relative positioning metadata when a child is made relative", () => {
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
        sources: [{ slot: "meta", name: "meta.yaml", path: "/workspace/projects/PIHC3/src/modules/focus_tree/C08_PARTIV/meta.yaml", relative_path: "src/modules/focus_tree/C08_PARTIV/meta.yaml", extension: "yaml" }],
        metadata: {
          settings: {
            focuses: [
              { id: "FOCUS_ROOT", x: "10", y: "0" },
              { id: "FOCUS_CHILD", x: "13", y: "2", prerequisites: ["FOCUS_ROOT"] }
            ]
          }
        }
      }
    ]);
    const baseDocument = buildProjectDiagramDocument(browser, "focuses");
    const draftDocument = makeDiagramSelectedNodeRelative(baseDocument, "FOCUS_CHILD");
    const entities = buildModuleEntities(browser, "focuses", "en");
    const metadataText = [
      "type: focus_tree",
      "settings:",
      "    focuses:",
      "    -   id: FOCUS_ROOT",
      "        x: '10'",
      "        y: '0'",
      "    -   id: FOCUS_CHILD",
      "        x: '13'",
      "        y: '2'",
      "        prerequisites:",
      "        - FOCUS_ROOT",
      ""
    ].join("\n");

    expect(changedDiagramMetadataEntityIds(baseDocument, draftDocument)).toEqual(["focus_tree:C08_PARTIV"]);
    expect(
      buildDiagramMetadataTextDrafts({
        baseDocument,
        draftDocument,
        entities,
        metadataTextByEntityId: { "focus_tree:C08_PARTIV": metadataText }
      })
    ).toEqual([
      {
        entityId: "focus_tree:C08_PARTIV",
        slot: "meta",
        text: [
          "type: focus_tree",
          "settings:",
          "    focuses:",
          "    -   id: FOCUS_ROOT",
          "        x: '10'",
          "        y: '0'",
          "    -   id: FOCUS_CHILD",
          "        relative_position_id: FOCUS_ROOT",
          "        x: '3'",
          "        y: '2'",
          "        prerequisites:",
          "        - FOCUS_ROOT",
          ""
        ].join("\n")
      }
    ]);
  });

  it("removes PIHC3 focus parent metadata when a parented child is made relative", () => {
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
        sources: [{ slot: "meta", name: "meta.yaml", path: "/workspace/projects/PIHC3/src/modules/focus_tree/C08_PARTIV/meta.yaml", relative_path: "src/modules/focus_tree/C08_PARTIV/meta.yaml", extension: "yaml" }],
        metadata: {
          settings: {
            focuses: [
              { id: "FOCUS_ROOT", x: "10", y: "0" },
              { id: "FOCUS_CHILD", parent: "FOCUS_ROOT", x: "13", y: "2", prerequisites: ["FOCUS_ROOT"] }
            ]
          }
        }
      }
    ]);
    const baseDocument = buildProjectDiagramDocument(browser, "focuses");
    const draftDocument = makeDiagramSelectedNodeRelative(baseDocument, "FOCUS_CHILD");
    const entities = buildModuleEntities(browser, "focuses", "en");
    const metadataText = [
      "type: focus_tree",
      "settings:",
      "    focuses:",
      "    -   id: FOCUS_ROOT",
      "        x: '10'",
      "        y: '0'",
      "    -   id: FOCUS_CHILD",
      "        parent: FOCUS_ROOT",
      "        x: '13'",
      "        y: '2'",
      "        prerequisites:",
      "        - FOCUS_ROOT",
      ""
    ].join("\n");

    expect(changedDiagramMetadataEntityIds(baseDocument, draftDocument)).toEqual(["focus_tree:C08_PARTIV"]);
    expect(
      buildDiagramMetadataTextDrafts({
        baseDocument,
        draftDocument,
        entities,
        metadataTextByEntityId: { "focus_tree:C08_PARTIV": metadataText }
      })
    ).toEqual([
      {
        entityId: "focus_tree:C08_PARTIV",
        slot: "meta",
        text: [
          "type: focus_tree",
          "settings:",
          "    focuses:",
          "    -   id: FOCUS_ROOT",
          "        x: '10'",
          "        y: '0'",
          "    -   id: FOCUS_CHILD",
          "        relative_position_id: FOCUS_ROOT",
          "        x: '3'",
          "        y: '2'",
          "        prerequisites:",
          "        - FOCUS_ROOT",
          ""
        ].join("\n")
      }
    ]);
  });

  it("updates migrated PIHC source focus relative positioning metadata before compiled focus positions", () => {
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
        sources: [{ slot: "meta", name: "meta.yaml", path: "/workspace/projects/PIHC3/src/modules/focus_tree/C08_PARTIV/meta.yaml", relative_path: "src/modules/focus_tree/C08_PARTIV/meta.yaml", extension: "yaml" }],
        metadata: {
          settings: {
            source_focuses: [
              { folder: "C08_ROOT", focus_id: "FOCUS_ROOT", source_path: "C08_ROOT", x: "10", y: "0" },
              { folder: "C08_CHILD", focus_id: "FOCUS_CHILD", source_path: "C08_CHILD", parent: "FOCUS_ROOT", x: "13", y: "2", priority: "10" }
            ],
            focuses: [
              { id: "FOCUS_ROOT", x: "10", y: "0" },
              { id: "FOCUS_CHILD", x: "13", y: "2", prerequisites: ["FOCUS_ROOT"] }
            ]
          }
        }
      }
    ]);
    const baseDocument = buildProjectDiagramDocument(browser, "focuses");
    const draftDocument = makeDiagramSelectedNodeRelative(baseDocument, "FOCUS_CHILD");
    const entities = buildModuleEntities(browser, "focuses", "en");
    const metadataText = [
      "type: focus_tree",
      "settings:",
      "    source_focuses:",
      "    -   folder: C08_ROOT",
      "        focus_id: FOCUS_ROOT",
      "        source_path: C08_ROOT",
      "        x: '10'",
      "        y: '0'",
      "    -   folder: C08_CHILD",
      "        focus_id: FOCUS_CHILD",
      "        source_path: C08_CHILD",
      "        parent: FOCUS_ROOT",
      "        x: '13'",
      "        y: '2'",
      "        priority: '10'",
      "    focuses:",
      "    -   id: FOCUS_ROOT",
      "        x: '10'",
      "        y: '0'",
      "    -   id: FOCUS_CHILD",
      "        x: '13'",
      "        y: '2'",
      "        prerequisites:",
      "        - FOCUS_ROOT",
      ""
    ].join("\n");

    expect(changedDiagramMetadataEntityIds(baseDocument, draftDocument)).toEqual(["focus_tree:C08_PARTIV"]);
    expect(
      buildDiagramMetadataTextDrafts({
        baseDocument,
        draftDocument,
        entities,
        metadataTextByEntityId: { "focus_tree:C08_PARTIV": metadataText }
      })
    ).toEqual([
      {
        entityId: "focus_tree:C08_PARTIV",
        slot: "meta",
        text: [
          "type: focus_tree",
          "settings:",
          "    source_focuses:",
          "    -   folder: C08_ROOT",
          "        focus_id: FOCUS_ROOT",
          "        source_path: C08_ROOT",
          "        x: '10'",
          "        y: '0'",
          "    -   folder: C08_CHILD",
          "        focus_id: FOCUS_CHILD",
          "        source_path: C08_CHILD",
          "        relative_position_id: FOCUS_ROOT",
          "        x: '3'",
          "        y: '2'",
          "        priority: '10'",
          "    focuses:",
          "    -   id: FOCUS_ROOT",
          "        x: '10'",
          "        y: '0'",
          "    -   id: FOCUS_CHILD",
          "        x: '13'",
          "        y: '2'",
          "        prerequisites:",
          "        - FOCUS_ROOT",
          ""
        ].join("\n")
      }
    ]);
  });

  it("removes PIHC3 focus relative positioning metadata when a relative focus is pinned", () => {
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
        sources: [{ slot: "meta", name: "meta.yaml", path: "/workspace/projects/PIHC3/src/modules/focus_tree/C08_PARTIV/meta.yaml", relative_path: "src/modules/focus_tree/C08_PARTIV/meta.yaml", extension: "yaml" }],
        metadata: {
          settings: {
            focuses: [
              { id: "FOCUS_ROOT", x: "10", y: "0" },
              { id: "FOCUS_CHILD", relative_position_id: "FOCUS_ROOT", x: "3", y: "2", prerequisites: ["FOCUS_ROOT"] }
            ]
          }
        }
      }
    ]);
    const baseDocument = buildProjectDiagramDocument(browser, "focuses");
    const draftDocument = pinDiagramSelectedNode(baseDocument, "FOCUS_CHILD");
    const entities = buildModuleEntities(browser, "focuses", "en");
    const metadataText = [
      "type: focus_tree",
      "settings:",
      "    focuses:",
      "    -   id: FOCUS_ROOT",
      "        x: '10'",
      "        y: '0'",
      "    -   id: FOCUS_CHILD",
      "        relative_position_id: FOCUS_ROOT",
      "        x: '3'",
      "        y: '2'",
      "        prerequisites:",
      "        - FOCUS_ROOT",
      ""
    ].join("\n");

    expect(changedDiagramMetadataEntityIds(baseDocument, draftDocument)).toEqual(["focus_tree:C08_PARTIV"]);
    expect(
      buildDiagramMetadataTextDrafts({
        baseDocument,
        draftDocument,
        entities,
        metadataTextByEntityId: { "focus_tree:C08_PARTIV": metadataText }
      })
    ).toEqual([
      {
        entityId: "focus_tree:C08_PARTIV",
        slot: "meta",
        text: [
          "type: focus_tree",
          "settings:",
          "    focuses:",
          "    -   id: FOCUS_ROOT",
          "        x: '10'",
          "        y: '0'",
          "    -   id: FOCUS_CHILD",
          "        x: '13'",
          "        y: '2'",
          "        prerequisites:",
          "        - FOCUS_ROOT",
          ""
        ].join("\n")
      }
    ]);
  });

  it("removes migrated PIHC source focus relative positioning metadata when a relative focus is pinned", () => {
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
        sources: [{ slot: "meta", name: "meta.yaml", path: "/workspace/projects/PIHC3/src/modules/focus_tree/C08_PARTIV/meta.yaml", relative_path: "src/modules/focus_tree/C08_PARTIV/meta.yaml", extension: "yaml" }],
        metadata: {
          settings: {
            source_focuses: [
              { folder: "C08_ROOT", focus_id: "FOCUS_ROOT", source_path: "C08_ROOT", x: "10", y: "0" },
              { folder: "C08_CHILD", focus_id: "FOCUS_CHILD", source_path: "C08_CHILD", relative_position_id: "FOCUS_ROOT", x: "3", y: "2", priority: "10" }
            ],
            focuses: [
              { id: "FOCUS_ROOT", x: "10", y: "0" },
              { id: "FOCUS_CHILD", x: "99", y: "99", prerequisites: ["FOCUS_ROOT"] }
            ]
          }
        }
      }
    ]);
    const baseDocument = buildProjectDiagramDocument(browser, "focuses");
    const draftDocument = pinDiagramSelectedNode(baseDocument, "FOCUS_CHILD");
    const entities = buildModuleEntities(browser, "focuses", "en");
    const metadataText = [
      "type: focus_tree",
      "settings:",
      "    source_focuses:",
      "    -   folder: C08_ROOT",
      "        focus_id: FOCUS_ROOT",
      "        source_path: C08_ROOT",
      "        x: '10'",
      "        y: '0'",
      "    -   folder: C08_CHILD",
      "        focus_id: FOCUS_CHILD",
      "        source_path: C08_CHILD",
      "        relative_position_id: FOCUS_ROOT",
      "        x: '3'",
      "        y: '2'",
      "        priority: '10'",
      "    focuses:",
      "    -   id: FOCUS_ROOT",
      "        x: '10'",
      "        y: '0'",
      "    -   id: FOCUS_CHILD",
      "        x: '99'",
      "        y: '99'",
      "        prerequisites:",
      "        - FOCUS_ROOT",
      ""
    ].join("\n");

    expect(changedDiagramMetadataEntityIds(baseDocument, draftDocument)).toEqual(["focus_tree:C08_PARTIV"]);
    expect(
      buildDiagramMetadataTextDrafts({
        baseDocument,
        draftDocument,
        entities,
        metadataTextByEntityId: { "focus_tree:C08_PARTIV": metadataText }
      })
    ).toEqual([
      {
        entityId: "focus_tree:C08_PARTIV",
        slot: "meta",
        text: [
          "type: focus_tree",
          "settings:",
          "    source_focuses:",
          "    -   folder: C08_ROOT",
          "        focus_id: FOCUS_ROOT",
          "        source_path: C08_ROOT",
          "        x: '10'",
          "        y: '0'",
          "    -   folder: C08_CHILD",
          "        focus_id: FOCUS_CHILD",
          "        source_path: C08_CHILD",
          "        x: '13'",
          "        y: '2'",
          "        priority: '10'",
          "    focuses:",
          "    -   id: FOCUS_ROOT",
          "        x: '10'",
          "        y: '0'",
          "    -   id: FOCUS_CHILD",
          "        x: '99'",
          "        y: '99'",
          "        prerequisites:",
          "        - FOCUS_ROOT",
          ""
        ].join("\n")
      }
    ]);
  });

  it("removes migrated PIHC source focus legacy parent offsets when a legacy relative focus is pinned", () => {
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
        sources: [{ slot: "meta", name: "meta.yaml", path: "/workspace/projects/PIHC3/src/modules/focus_tree/C08_PARTIV/meta.yaml", relative_path: "src/modules/focus_tree/C08_PARTIV/meta.yaml", extension: "yaml" }],
        metadata: {
          settings: {
            source_focuses: [
              { folder: "C08_ROOT", focus_id: "FOCUS_ROOT", source_path: "C08_ROOT", x: "10", y: "0" },
              { folder: "C08_CHILD", focus_id: "FOCUS_CHILD", source_path: "C08_CHILD", parent: "FOCUS_ROOT", dx: "3", dy: "2", priority: "10" }
            ],
            focuses: [
              { id: "FOCUS_ROOT", x: "10", y: "0" },
              { id: "FOCUS_CHILD", x: "99", y: "99", prerequisites: ["FOCUS_ROOT"] }
            ]
          }
        }
      }
    ]);
    const baseDocument = buildProjectDiagramDocument(browser, "focuses");
    const draftDocument = pinDiagramSelectedNode(baseDocument, "FOCUS_CHILD");
    const entities = buildModuleEntities(browser, "focuses", "en");
    const metadataText = [
      "type: focus_tree",
      "settings:",
      "    source_focuses:",
      "    -   folder: C08_ROOT",
      "        focus_id: FOCUS_ROOT",
      "        source_path: C08_ROOT",
      "        x: '10'",
      "        y: '0'",
      "    -   folder: C08_CHILD",
      "        focus_id: FOCUS_CHILD",
      "        source_path: C08_CHILD",
      "        parent: FOCUS_ROOT",
      "        dx: '3'",
      "        dy: '2'",
      "        priority: '10'",
      "    focuses:",
      "    -   id: FOCUS_ROOT",
      "        x: '10'",
      "        y: '0'",
      "    -   id: FOCUS_CHILD",
      "        x: '99'",
      "        y: '99'",
      "        prerequisites:",
      "        - FOCUS_ROOT",
      ""
    ].join("\n");

    expect(changedDiagramMetadataEntityIds(baseDocument, draftDocument)).toEqual(["focus_tree:C08_PARTIV"]);
    expect(
      buildDiagramMetadataTextDrafts({
        baseDocument,
        draftDocument,
        entities,
        metadataTextByEntityId: { "focus_tree:C08_PARTIV": metadataText }
      })
    ).toEqual([
      {
        entityId: "focus_tree:C08_PARTIV",
        slot: "meta",
        text: [
          "type: focus_tree",
          "settings:",
          "    source_focuses:",
          "    -   folder: C08_ROOT",
          "        focus_id: FOCUS_ROOT",
          "        source_path: C08_ROOT",
          "        x: '10'",
          "        y: '0'",
          "    -   folder: C08_CHILD",
          "        focus_id: FOCUS_CHILD",
          "        source_path: C08_CHILD",
          "        x: 13",
          "        y: 3",
          "        priority: '10'",
          "    focuses:",
          "    -   id: FOCUS_ROOT",
          "        x: '10'",
          "        y: '0'",
          "    -   id: FOCUS_CHILD",
          "        x: '99'",
          "        y: '99'",
          "        prerequisites:",
          "        - FOCUS_ROOT",
          ""
        ].join("\n")
      }
    ]);
  });

  it("keeps migrated PIHC source focus cx and cy offset fields when moving a legacy relative focus", () => {
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
        sources: [{ slot: "meta", name: "meta.yaml", path: "/workspace/projects/PIHC3/src/modules/focus_tree/C08_PARTIV/meta.yaml", relative_path: "src/modules/focus_tree/C08_PARTIV/meta.yaml", extension: "yaml" }],
        metadata: {
          settings: {
            source_focuses: [
              { folder: "C08_ROOT", focus_id: "FOCUS_ROOT", source_path: "C08_ROOT", x: "10", y: "0" },
              { folder: "C08_CHILD", focus_id: "FOCUS_CHILD", source_path: "C08_CHILD", parent: "FOCUS_ROOT", cx: "3", cy: "2", priority: "10" }
            ],
            focuses: [
              { id: "FOCUS_ROOT", x: "10", y: "0" },
              { id: "FOCUS_CHILD", x: "99", y: "99", prerequisites: ["FOCUS_ROOT"] }
            ]
          }
        }
      }
    ]);
    const baseDocument = buildProjectDiagramDocument(browser, "focuses");
    const draftDocument = moveDiagramNode(baseDocument, "FOCUS_CHILD", { dx: -1, dy: 2 });
    const entities = buildModuleEntities(browser, "focuses", "en");
    const metadataText = [
      "type: focus_tree",
      "settings:",
      "    source_focuses:",
      "    -   folder: C08_ROOT",
      "        focus_id: FOCUS_ROOT",
      "        source_path: C08_ROOT",
      "        x: '10'",
      "        y: '0'",
      "    -   folder: C08_CHILD",
      "        focus_id: FOCUS_CHILD",
      "        source_path: C08_CHILD",
      "        parent: FOCUS_ROOT",
      "        cx: '3'",
      "        cy: '2'",
      "        priority: '10'",
      "    focuses:",
      "    -   id: FOCUS_ROOT",
      "        x: '10'",
      "        y: '0'",
      "    -   id: FOCUS_CHILD",
      "        x: '99'",
      "        y: '99'",
      "        prerequisites:",
      "        - FOCUS_ROOT",
      ""
    ].join("\n");

    expect(changedDiagramMetadataEntityIds(baseDocument, draftDocument)).toEqual(["focus_tree:C08_PARTIV"]);
    expect(
      buildDiagramMetadataTextDrafts({
        baseDocument,
        draftDocument,
        entities,
        metadataTextByEntityId: { "focus_tree:C08_PARTIV": metadataText }
      })
    ).toEqual([
      {
        entityId: "focus_tree:C08_PARTIV",
        slot: "meta",
        text: [
          "type: focus_tree",
          "settings:",
          "    source_focuses:",
          "    -   folder: C08_ROOT",
          "        focus_id: FOCUS_ROOT",
          "        source_path: C08_ROOT",
          "        x: '10'",
          "        y: '0'",
          "    -   folder: C08_CHILD",
          "        focus_id: FOCUS_CHILD",
          "        source_path: C08_CHILD",
          "        parent: FOCUS_ROOT",
          "        cx: '2'",
          "        cy: '4'",
          "        priority: '10'",
          "    focuses:",
          "    -   id: FOCUS_ROOT",
          "        x: '10'",
          "        y: '0'",
          "    -   id: FOCUS_CHILD",
          "        x: '99'",
          "        y: '99'",
          "        prerequisites:",
          "        - FOCUS_ROOT",
          ""
        ].join("\n")
      }
    ]);
  });

  it("adds missing x and y scalars to a moved focus entry", () => {
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
        sources: [{ slot: "meta", name: "meta.yaml", path: "/workspace/projects/PIHC3/src/modules/focus_tree/C08_PARTIV/meta.yaml", relative_path: "src/modules/focus_tree/C08_PARTIV/meta.yaml", extension: "yaml" }],
        metadata: {
          settings: {
            focuses: [{ id: "FOCUS_ROOT" }, { id: "FOCUS_CHILD", prerequisites: ["FOCUS_ROOT"] }]
          }
        }
      }
    ]);
    const baseDocument = buildProjectDiagramDocument(browser, "focuses");
    const draftDocument = moveDiagramNode(baseDocument, "FOCUS_CHILD", { dx: 2, dy: -1 });
    const entities = buildModuleEntities(browser, "focuses", "en");
    const metadataText = [
      "type: focus_tree",
      "settings:",
      "    focuses:",
      "    -   id: FOCUS_ROOT",
      "    -   id: FOCUS_CHILD",
      "        prerequisites:",
      "        - FOCUS_ROOT",
      ""
    ].join("\n");

    expect(
      buildDiagramMetadataTextDrafts({
        baseDocument,
        draftDocument,
        entities,
        metadataTextByEntityId: { "focus_tree:C08_PARTIV": metadataText }
      })
    ).toEqual([
      {
        entityId: "focus_tree:C08_PARTIV",
        slot: "meta",
        text: [
          "type: focus_tree",
          "settings:",
          "    focuses:",
          "    -   id: FOCUS_ROOT",
          "    -   id: FOCUS_CHILD",
          "        x: 2",
          "        y: 0",
          "        prerequisites:",
          "        - FOCUS_ROOT",
          ""
        ].join("\n")
      }
    ]);
  });

  it("persists PIHC3 focus pinning when the resolved position does not move", () => {
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
        sources: [{ slot: "meta", name: "meta.yaml", path: "/workspace/projects/PIHC3/src/modules/focus_tree/C08_PARTIV/meta.yaml", relative_path: "src/modules/focus_tree/C08_PARTIV/meta.yaml", extension: "yaml" }],
        metadata: {
          settings: {
            focuses: [{ id: "FOCUS_ROOT" }, { id: "FOCUS_CHILD", prerequisites: ["FOCUS_ROOT"] }]
          }
        }
      }
    ]);
    const baseDocument = buildProjectDiagramDocument(browser, "focuses");
    const draftDocument = pinDiagramSelectedNode(baseDocument, "FOCUS_CHILD");
    const entities = buildModuleEntities(browser, "focuses", "en");
    const metadataText = [
      "type: focus_tree",
      "settings:",
      "    focuses:",
      "    -   id: FOCUS_ROOT",
      "    -   id: FOCUS_CHILD",
      "        prerequisites:",
      "        - FOCUS_ROOT",
      ""
    ].join("\n");

    expect(
      buildDiagramMetadataTextDrafts({
        baseDocument,
        draftDocument,
        entities,
        metadataTextByEntityId: { "focus_tree:C08_PARTIV": metadataText }
      })
    ).toEqual([
      {
        entityId: "focus_tree:C08_PARTIV",
        slot: "meta",
        text: [
          "type: focus_tree",
          "settings:",
          "    focuses:",
          "    -   id: FOCUS_ROOT",
          "    -   id: FOCUS_CHILD",
          "        x: 0",
          "        y: 1",
          "        prerequisites:",
          "        - FOCUS_ROOT",
          ""
        ].join("\n")
      }
    ]);
  });

  it("adds focus positions when id is not the first list item field", () => {
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
        sources: [{ slot: "meta", name: "meta.yaml", path: "/workspace/projects/PIHC3/src/modules/focus_tree/C08_PARTIV/meta.yaml", relative_path: "src/modules/focus_tree/C08_PARTIV/meta.yaml", extension: "yaml" }],
        metadata: {
          settings: {
            focuses: [
              { id: "FOCUS_ROOT" },
              { icon: "GFX_FOCUS_CHILD_icon", id: "FOCUS_CHILD", prerequisites: ["FOCUS_ROOT"] }
            ]
          }
        }
      }
    ]);
    const baseDocument = buildProjectDiagramDocument(browser, "focuses");
    const draftDocument = moveDiagramNode(baseDocument, "FOCUS_CHILD", { dx: 2, dy: -1 });
    const entities = buildModuleEntities(browser, "focuses", "en");
    const metadataText = [
      "type: focus_tree",
      "settings:",
      "    focuses:",
      "    -   id: FOCUS_ROOT",
      "    -   icon: GFX_FOCUS_CHILD_icon",
      "        id: FOCUS_CHILD",
      "        prerequisites:",
      "        - FOCUS_ROOT",
      ""
    ].join("\n");

    expect(
      buildDiagramMetadataTextDrafts({
        baseDocument,
        draftDocument,
        entities,
        metadataTextByEntityId: { "focus_tree:C08_PARTIV": metadataText }
      })
    ).toEqual([
      {
        entityId: "focus_tree:C08_PARTIV",
        slot: "meta",
        text: [
          "type: focus_tree",
          "settings:",
          "    focuses:",
          "    -   id: FOCUS_ROOT",
          "    -   icon: GFX_FOCUS_CHILD_icon",
          "        id: FOCUS_CHILD",
          "        x: 2",
          "        y: 0",
          "        prerequisites:",
          "        - FOCUS_ROOT",
          ""
        ].join("\n")
      }
    ]);
  });

  it("removes focus x and y scalars when a focus returns to auto layout", () => {
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
        sources: [{ slot: "meta", name: "meta.yaml", path: "/workspace/projects/PIHC3/src/modules/focus_tree/C08_PARTIV/meta.yaml", relative_path: "src/modules/focus_tree/C08_PARTIV/meta.yaml", extension: "yaml" }],
        metadata: {
          settings: {
            focuses: [
              { id: "FOCUS_ROOT", x: "12", y: "0" },
              { id: "FOCUS_CHILD", x: "12", y: "1", prerequisites: ["FOCUS_ROOT"] }
            ]
          }
        }
      }
    ]);
    const baseDocument = buildProjectDiagramDocument(browser, "focuses");
    const draftDocument = autoLayoutDiagramNode(baseDocument, "FOCUS_CHILD");
    const entities = buildModuleEntities(browser, "focuses", "en");
    const metadataText = [
      "type: focus_tree",
      "settings:",
      "    focuses:",
      "    -   id: FOCUS_ROOT",
      "        x: '12'",
      "        y: '0'",
      "    -   id: FOCUS_CHILD",
      "        x: '12'",
      "        y: '1'",
      "        prerequisites:",
      "        - FOCUS_ROOT",
      ""
    ].join("\n");

    expect(
      buildDiagramMetadataTextDrafts({
        baseDocument,
        draftDocument,
        entities,
        metadataTextByEntityId: { "focus_tree:C08_PARTIV": metadataText }
      })
    ).toEqual([
      {
        entityId: "focus_tree:C08_PARTIV",
        slot: "meta",
        text: [
          "type: focus_tree",
          "settings:",
          "    focuses:",
          "    -   id: FOCUS_ROOT",
          "        x: '12'",
          "        y: '0'",
          "    -   id: FOCUS_CHILD",
          "        prerequisites:",
          "        - FOCUS_ROOT",
          ""
        ].join("\n")
      }
    ]);
  });

  it("removes source focus x and y scalars before compiled focus positions when a source-backed focus returns to auto layout", () => {
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
        sources: [{ slot: "meta", name: "meta.yaml", path: "/workspace/projects/PIHC3/src/modules/focus_tree/C08_PARTIV/meta.yaml", relative_path: "src/modules/focus_tree/C08_PARTIV/meta.yaml", extension: "yaml" }],
        metadata: {
          settings: {
            source_focuses: [
              { folder: "C08_ROOT", focus_id: "FOCUS_ROOT", source_path: "C08_ROOT", x: "12", y: "0" },
              { folder: "C08_CHILD", focus_id: "FOCUS_CHILD", source_path: "C08_CHILD", x: "12", y: "1", priority: "10" }
            ],
            focuses: [
              { id: "FOCUS_ROOT", x: "12", y: "0" },
              { id: "FOCUS_CHILD", x: "12", y: "1", prerequisites: ["FOCUS_ROOT"] }
            ]
          }
        }
      }
    ]);
    const baseDocument = buildProjectDiagramDocument(browser, "focuses");
    const draftDocument = autoLayoutDiagramNode(baseDocument, "FOCUS_CHILD");
    const entities = buildModuleEntities(browser, "focuses", "en");
    const metadataText = [
      "type: focus_tree",
      "settings:",
      "    source_focuses:",
      "    -   folder: C08_ROOT",
      "        focus_id: FOCUS_ROOT",
      "        source_path: C08_ROOT",
      "        x: '12'",
      "        y: '0'",
      "    -   folder: C08_CHILD",
      "        focus_id: FOCUS_CHILD",
      "        source_path: C08_CHILD",
      "        x: '12'",
      "        y: '1'",
      "        priority: '10'",
      "    focuses:",
      "    -   id: FOCUS_ROOT",
      "        x: '12'",
      "        y: '0'",
      "    -   id: FOCUS_CHILD",
      "        x: '12'",
      "        y: '1'",
      "        prerequisites:",
      "        - FOCUS_ROOT",
      ""
    ].join("\n");

    expect(
      buildDiagramMetadataTextDrafts({
        baseDocument,
        draftDocument,
        entities,
        metadataTextByEntityId: { "focus_tree:C08_PARTIV": metadataText }
      })
    ).toEqual([
      {
        entityId: "focus_tree:C08_PARTIV",
        slot: "meta",
        text: [
          "type: focus_tree",
          "settings:",
          "    source_focuses:",
          "    -   folder: C08_ROOT",
          "        focus_id: FOCUS_ROOT",
          "        source_path: C08_ROOT",
          "        x: '12'",
          "        y: '0'",
          "    -   folder: C08_CHILD",
          "        focus_id: FOCUS_CHILD",
          "        source_path: C08_CHILD",
          "        priority: '10'",
          "    focuses:",
          "    -   id: FOCUS_ROOT",
          "        x: '12'",
          "        y: '0'",
          "    -   id: FOCUS_CHILD",
          "        x: '12'",
          "        y: '1'",
          "        prerequisites:",
          "        - FOCUS_ROOT",
          ""
        ].join("\n")
      }
    ]);
  });

  it("updates migrated PIHC source focus legacy layout hints", () => {
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
        sources: [{ slot: "meta", name: "meta.yaml", path: "/workspace/projects/PIHC3/src/modules/focus_tree/C08_PARTIV/meta.yaml", relative_path: "src/modules/focus_tree/C08_PARTIV/meta.yaml", extension: "yaml" }],
        metadata: {
          settings: {
            source_focuses: [
              { folder: "C08_ROOT", focus_id: "FOCUS_ROOT", source_path: "C08_ROOT", x: "12", y: "0" },
              { folder: "C08_CHILD", focus_id: "FOCUS_CHILD", source_path: "C08_CHILD", parent: "FOCUS_ROOT", dx: "2", dy: "1", priority: "10", pw: "6" }
            ],
            focuses: [
              { id: "FOCUS_ROOT", x: "12", y: "0" },
              { id: "FOCUS_CHILD", x: "12", y: "1", prerequisites: ["FOCUS_ROOT"] }
            ]
          }
        }
      }
    ]);
    const baseDocument = buildProjectDiagramDocument(browser, "focuses");
    const draftDocument = setDiagramNodeLayoutHints(baseDocument, "FOCUS_CHILD", {
      priority: 20,
      subtreeCenterOffset: -1,
      subtreeWidth: 8,
      subtreeWidthDelta: 2
    });
    const entities = buildModuleEntities(browser, "focuses", "en");
    const metadataText = [
      "type: focus_tree",
      "settings:",
      "    source_focuses:",
      "    -   folder: C08_ROOT",
      "        focus_id: FOCUS_ROOT",
      "        source_path: C08_ROOT",
      "        x: '12'",
      "        y: '0'",
      "    -   folder: C08_CHILD",
      "        focus_id: FOCUS_CHILD",
      "        source_path: C08_CHILD",
      "        parent: FOCUS_ROOT",
      "        dx: '2'",
      "        dy: '1'",
      "        priority: '10'",
      "        pw: '6'",
      "    focuses:",
      "    -   id: FOCUS_ROOT",
      "        x: '12'",
      "        y: '0'",
      "    -   id: FOCUS_CHILD",
      "        x: '12'",
      "        y: '1'",
      "        prerequisites:",
      "        - FOCUS_ROOT",
      ""
    ].join("\n");

    expect(changedDiagramMetadataEntityIds(baseDocument, draftDocument)).toEqual(["focus_tree:C08_PARTIV"]);
    expect(
      buildDiagramMetadataTextDrafts({
        baseDocument,
        draftDocument,
        entities,
        metadataTextByEntityId: { "focus_tree:C08_PARTIV": metadataText }
      })
    ).toEqual([
      {
        entityId: "focus_tree:C08_PARTIV",
        slot: "meta",
        text: [
          "type: focus_tree",
          "settings:",
          "    source_focuses:",
          "    -   folder: C08_ROOT",
          "        focus_id: FOCUS_ROOT",
          "        source_path: C08_ROOT",
          "        x: '12'",
          "        y: '0'",
          "    -   folder: C08_CHILD",
          "        focus_id: FOCUS_CHILD",
          "        source_path: C08_CHILD",
          "        parent: FOCUS_ROOT",
          "        dx: '2'",
          "        dy: '1'",
          "        priority: '20'",
          "        pw: '8'",
          "        dw: 2",
          "        dc: -1",
          "    focuses:",
          "    -   id: FOCUS_ROOT",
          "        x: '12'",
          "        y: '0'",
          "    -   id: FOCUS_CHILD",
          "        x: '12'",
          "        y: '1'",
          "        prerequisites:",
          "        - FOCUS_ROOT",
          ""
        ].join("\n")
      }
    ]);
  });

  it("canonicalizes migrated PIHC source focus layout aliases when layout hints change", () => {
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
        source_root: "/workspace/projects/PIHC3/src",
        source_root_relative_path: "src",
        source_count: 1,
        sources: [{ slot: "meta", name: "meta.yaml", path: "/workspace/projects/PIHC3/src/modules/focus_tree/C08_PARTIV/meta.yaml", relative_path: "src/modules/focus_tree/C08_PARTIV/meta.yaml", extension: "yaml" }],
        metadata: {
          settings: {
            source_focuses: [
              { folder: "C08_ROOT", focus_id: "FOCUS_ROOT", source_path: "C08_ROOT", x: "12", y: "0" },
              { folder: "C08_CHILD", focus_id: "FOCUS_CHILD", source_path: "C08_CHILD", parent: "FOCUS_ROOT", dx: "2", dy: "1", priority: "10", subtree_width: "6", subtree_width_delta: "1", subtree_center_offset: "0" }
            ],
            focuses: [
              { id: "FOCUS_ROOT", x: "12", y: "0" },
              { id: "FOCUS_CHILD", x: "12", y: "1", prerequisites: ["FOCUS_ROOT"] }
            ]
          }
        }
      }
    ]);
    const baseDocument = buildProjectDiagramDocument(browser, "focuses");
    const draftDocument = setDiagramNodeLayoutHints(baseDocument, "FOCUS_CHILD", {
      priority: 20,
      subtreeCenterOffset: -1,
      subtreeWidth: 8,
      subtreeWidthDelta: 2
    });
    const entities = buildModuleEntities(browser, "focuses", "en");
    const metadataText = [
      "type: focus_tree",
      "settings:",
      "    source_focuses:",
      "    -   folder: C08_ROOT",
      "        focus_id: FOCUS_ROOT",
      "        source_path: C08_ROOT",
      "        x: '12'",
      "        y: '0'",
      "    -   folder: C08_CHILD",
      "        focus_id: FOCUS_CHILD",
      "        source_path: C08_CHILD",
      "        parent: FOCUS_ROOT",
      "        dx: '2'",
      "        dy: '1'",
      "        priority: '10'",
      "        subtree_width: '6'",
      "        subtree_width_delta: '1'",
      "        subtree_center_offset: '0'",
      "    focuses:",
      "    -   id: FOCUS_ROOT",
      "        x: '12'",
      "        y: '0'",
      "    -   id: FOCUS_CHILD",
      "        x: '12'",
      "        y: '1'",
      "        prerequisites:",
      "        - FOCUS_ROOT",
      ""
    ].join("\n");
    const sourceInfoPath = "/workspace/projects/PIHC3/src/modules/focus_tree/C08_PARTIV/legacy/C08_CHILD/info.json";
    const sourceInfoText = `${JSON.stringify(
      {
        tree: "C08_PARTIV",
        parent: "FOCUS_ROOT",
        dx: 2,
        dy: 1,
        priority: 10,
        subtree_width: 6,
        subtree_width_delta: 1,
        subtree_center_offset: 0
      },
      null,
      4
    )}\n`;

    const drafts = buildDiagramMetadataTextDrafts({
      baseDocument,
      draftDocument,
      entities,
      metadataTextByEntityId: { "focus_tree:C08_PARTIV": metadataText },
      sourceTextByPath: { [sourceInfoPath]: sourceInfoText }
    });

    expect(changedDiagramMetadataSourceInfoPaths(baseDocument, draftDocument)).toEqual([sourceInfoPath]);
    expect(drafts).toContainEqual({
      entityId: "focus_tree:C08_PARTIV",
      slot: "meta",
      text: [
        "type: focus_tree",
        "settings:",
        "    source_focuses:",
        "    -   folder: C08_ROOT",
        "        focus_id: FOCUS_ROOT",
        "        source_path: C08_ROOT",
        "        x: '12'",
        "        y: '0'",
        "    -   folder: C08_CHILD",
        "        focus_id: FOCUS_CHILD",
        "        source_path: C08_CHILD",
        "        parent: FOCUS_ROOT",
        "        dx: '2'",
        "        dy: '1'",
        "        priority: '20'",
        "        w: 8",
        "        dw: 2",
        "        dc: -1",
        "    focuses:",
        "    -   id: FOCUS_ROOT",
        "        x: '12'",
        "        y: '0'",
        "    -   id: FOCUS_CHILD",
        "        x: '12'",
        "        y: '1'",
        "        prerequisites:",
        "        - FOCUS_ROOT",
        ""
      ].join("\n")
    });
    expect(drafts).toContainEqual({
      entityId: "focus_tree:C08_PARTIV",
      slot: "source",
      path: sourceInfoPath,
      text: `${JSON.stringify(
        {
          tree: "C08_PARTIV",
          parent: "FOCUS_ROOT",
          dx: 2,
          dy: 1,
          priority: 20,
          w: 8,
          dw: 2,
          dc: -1
        },
        null,
        4
      )}\n`
    });
  });

  it("persists a moved PIHC3 focus root while auto-layouting descendant focus positions", () => {
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
        sources: [{ slot: "meta", name: "meta.yaml", path: "/workspace/projects/PIHC3/src/modules/focus_tree/C08_PARTIV/meta.yaml", relative_path: "src/modules/focus_tree/C08_PARTIV/meta.yaml", extension: "yaml" }],
        metadata: {
          settings: {
            focuses: [
              { id: "FOCUS_ROOT", x: "12", y: "0" },
              { id: "FOCUS_CHILD", x: "12", y: "1", prerequisites: ["FOCUS_ROOT"] }
            ]
          }
        }
      }
    ]);
    const baseDocument = buildProjectDiagramDocument(browser, "focuses");
    const draftDocument = moveDiagramNodeRelayoutDescendants(baseDocument, "FOCUS_ROOT", { dx: 1, dy: 0 });
    const entities = buildModuleEntities(browser, "focuses", "en");
    const metadataText = [
      "type: focus_tree",
      "settings:",
      "    focuses:",
      "    -   id: FOCUS_ROOT",
      "        x: '12'",
      "        y: '0'",
      "    -   id: FOCUS_CHILD",
      "        x: '12'",
      "        y: '1'",
      "        prerequisites:",
      "        - FOCUS_ROOT",
      ""
    ].join("\n");

    expect(changedDiagramMetadataEntityIds(baseDocument, draftDocument)).toEqual(["focus_tree:C08_PARTIV"]);
    expect(
      buildDiagramMetadataTextDrafts({
        baseDocument,
        draftDocument,
        entities,
        metadataTextByEntityId: { "focus_tree:C08_PARTIV": metadataText }
      })
    ).toEqual([
      {
        entityId: "focus_tree:C08_PARTIV",
        slot: "meta",
        text: [
          "type: focus_tree",
          "settings:",
          "    focuses:",
          "    -   id: FOCUS_ROOT",
          "        x: '13'",
          "        y: '0'",
          "    -   id: FOCUS_CHILD",
          "        prerequisites:",
          "        - FOCUS_ROOT",
          ""
        ].join("\n")
      }
    ]);
  });

  it("removes PIHC3 focus subtree entries from focus tree metadata text", () => {
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
        sources: [{ slot: "meta", name: "meta.yaml", path: "/workspace/projects/PIHC3/src/modules/focus_tree/C08_PARTIV/meta.yaml", relative_path: "src/modules/focus_tree/C08_PARTIV/meta.yaml", extension: "yaml" }],
        metadata: {
          settings: {
            focuses: [
              { id: "FOCUS_ROOT", x: "12", y: "0" },
              { id: "FOCUS_CHILD", x: "12", y: "1", prerequisites: ["FOCUS_ROOT"] },
              { id: "FOCUS_LEAF", x: "12", y: "2", prerequisites: ["FOCUS_CHILD"] },
              { id: "FOCUS_SIBLING", x: "14", y: "1", prerequisites: ["FOCUS_ROOT"] }
            ]
          }
        }
      }
    ]);
    const baseDocument = buildProjectDiagramDocument(browser, "focuses");
    const draftDocument = removeDiagramSubtree(baseDocument, "FOCUS_CHILD");
    const entities = buildModuleEntities(browser, "focuses", "en");
    const metadataText = [
      "type: focus_tree",
      "settings:",
      "    focuses:",
      "    -   id: FOCUS_ROOT",
      "        x: '12'",
      "        y: '0'",
      "    -   id: FOCUS_CHILD",
      "        x: '12'",
      "        y: '1'",
      "        prerequisites:",
      "        - FOCUS_ROOT",
      "    -   id: FOCUS_LEAF",
      "        x: '12'",
      "        y: '2'",
      "        prerequisites:",
      "        - FOCUS_CHILD",
      "    -   id: FOCUS_SIBLING",
      "        x: '14'",
      "        y: '1'",
      "        prerequisites:",
      "        - FOCUS_ROOT",
      ""
    ].join("\n");

    expect(changedDiagramMetadataEntityIds(baseDocument, draftDocument)).toEqual(["focus_tree:C08_PARTIV"]);
    expect(
      buildDiagramMetadataTextDrafts({
        baseDocument,
        draftDocument,
        entities,
        metadataTextByEntityId: { "focus_tree:C08_PARTIV": metadataText }
      })
    ).toEqual([
      {
        entityId: "focus_tree:C08_PARTIV",
        slot: "meta",
        text: [
          "type: focus_tree",
          "settings:",
          "    focuses:",
          "    -   id: FOCUS_ROOT",
          "        x: '12'",
          "        y: '0'",
          "    -   id: FOCUS_SIBLING",
          "        x: '14'",
          "        y: '1'",
          "        prerequisites:",
          "        - FOCUS_ROOT",
          ""
        ].join("\n")
      }
    ]);
  });

  it("removes a PIHC3 root focus branch from focus tree metadata text", () => {
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
        sources: [{ slot: "meta", name: "meta.yaml", path: "/workspace/projects/PIHC3/src/modules/focus_tree/C08_PARTIV/meta.yaml", relative_path: "src/modules/focus_tree/C08_PARTIV/meta.yaml", extension: "yaml" }],
        metadata: {
          settings: {
            focuses: [
              { id: "FOCUS_ROOT", x: "12", y: "0" },
              { id: "FOCUS_CHILD", x: "12", y: "1", prerequisites: ["FOCUS_ROOT"] }
            ]
          }
        }
      }
    ]);
    const baseDocument = buildProjectDiagramDocument(browser, "focuses");
    const draftDocument = removeDiagramSubtree(baseDocument, "FOCUS_ROOT");
    const entities = buildModuleEntities(browser, "focuses", "en");
    const metadataText = [
      "type: focus_tree",
      "settings:",
      "    focuses:",
      "    -   id: FOCUS_ROOT",
      "        x: '12'",
      "        y: '0'",
      "    -   id: FOCUS_CHILD",
      "        x: '12'",
      "        y: '1'",
      "        prerequisites:",
      "        - FOCUS_ROOT",
      ""
    ].join("\n");

    expect(changedDiagramMetadataEntityIds(baseDocument, draftDocument)).toEqual(["focus_tree:C08_PARTIV"]);
    expect(
      buildDiagramMetadataTextDrafts({
        baseDocument,
        draftDocument,
        entities,
        metadataTextByEntityId: { "focus_tree:C08_PARTIV": metadataText }
      })
    ).toEqual([
      {
        entityId: "focus_tree:C08_PARTIV",
        slot: "meta",
        text: ["type: focus_tree", "settings:", "    focuses:", ""].join("\n")
      }
    ]);
  });

  it("updates PIHC3 focus_count when focus entries are added or removed", () => {
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
        sources: [{ slot: "meta", name: "meta.yaml", path: "/workspace/projects/PIHC3/src/modules/focus_tree/C08_PARTIV/meta.yaml", relative_path: "src/modules/focus_tree/C08_PARTIV/meta.yaml", extension: "yaml" }],
        metadata: {
          settings: {
            focus_count: 2,
            focuses: [
              { id: "FOCUS_ROOT", x: "12", y: "0" },
              { id: "FOCUS_CHILD", x: "12", y: "1", prerequisites: ["FOCUS_ROOT"] }
            ]
          }
        }
      }
    ]);
    const baseDocument = buildProjectDiagramDocument(browser, "focuses");
    const root = baseDocument.nodes.find((node) => node.id === "FOCUS_ROOT");
    const insertedDocument = insertDiagramRootNode(baseDocument, {
      id: "FOCUS_NEW_ROOT",
      mode: "auto",
      width: root?.width ?? 4,
      height: root?.height ?? 2,
      title: "Focus New Root",
      payload: root?.payload ? { ...(root.payload as Record<string, unknown>), embeddedId: "FOCUS_NEW_ROOT" } : undefined
    });
    const removedDocument = removeDiagramSubtree(baseDocument, "FOCUS_CHILD");
    const entities = buildModuleEntities(browser, "focuses", "en");
    const metadataText = [
      "type: focus_tree",
      "settings:",
      "    focus_count: 2",
      "    focuses:",
      "    -   id: FOCUS_ROOT",
      "        x: '12'",
      "        y: '0'",
      "    -   id: FOCUS_CHILD",
      "        x: '12'",
      "        y: '1'",
      "        prerequisites:",
      "        - FOCUS_ROOT",
      ""
    ].join("\n");

    const insertedDraft = buildDiagramMetadataTextDrafts({
      baseDocument,
      draftDocument: insertedDocument,
      entities,
      metadataTextByEntityId: { "focus_tree:C08_PARTIV": metadataText }
    });
    const removedDraft = buildDiagramMetadataTextDrafts({
      baseDocument,
      draftDocument: removedDocument,
      entities,
      metadataTextByEntityId: { "focus_tree:C08_PARTIV": metadataText }
    });

    expect(insertedDraft[0].text).toContain("    focus_count: 3");
    expect(removedDraft[0].text).toContain("    focus_count: 1");
  });

  it("removes a PIHC3 focus while keeping its children in focus tree metadata text", () => {
    const removeDiagramNodeOnly = (layoutModel as typeof layoutModel & { removeDiagramNodeOnly?: DiagramNodeOnlyRemover }).removeDiagramNodeOnly;
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
        sources: [{ slot: "meta", name: "meta.yaml", path: "/workspace/projects/PIHC3/src/modules/focus_tree/C08_PARTIV/meta.yaml", relative_path: "src/modules/focus_tree/C08_PARTIV/meta.yaml", extension: "yaml" }],
        metadata: {
          settings: {
            focuses: [
              { id: "FOCUS_ROOT", x: "12", y: "0" },
              { id: "FOCUS_CHILD", parent: "FOCUS_ROOT", x: "12", y: "1", prerequisites: ["FOCUS_ROOT"] },
              { id: "FOCUS_LEAF", parent: "FOCUS_CHILD", x: "12", y: "2", prerequisites: ["FOCUS_CHILD"] },
              { id: "FOCUS_SIBLING", parent: "FOCUS_ROOT", x: "14", y: "1", prerequisites: ["FOCUS_ROOT"] }
            ]
          }
        }
      }
    ]);
    const baseDocument = buildProjectDiagramDocument(browser, "focuses");
    expect(removeDiagramNodeOnly).toBeTypeOf("function");
    if (!removeDiagramNodeOnly) {
      return;
    }
    const draftDocument = removeDiagramNodeOnly(baseDocument, "FOCUS_CHILD");
    const entities = buildModuleEntities(browser, "focuses", "en");
    const metadataText = [
      "type: focus_tree",
      "settings:",
      "    focuses:",
      "    -   id: FOCUS_ROOT",
      "        x: '12'",
      "        y: '0'",
      "    -   id: FOCUS_CHILD",
      "        parent: FOCUS_ROOT",
      "        x: '12'",
      "        y: '1'",
      "        prerequisites:",
      "        - FOCUS_ROOT",
      "    -   id: FOCUS_LEAF",
      "        parent: FOCUS_CHILD",
      "        x: '12'",
      "        y: '2'",
      "        prerequisites:",
      "        - FOCUS_CHILD",
      "    -   id: FOCUS_SIBLING",
      "        parent: FOCUS_ROOT",
      "        x: '14'",
      "        y: '1'",
      "        prerequisites:",
      "        - FOCUS_ROOT",
      ""
    ].join("\n");

    expect(changedDiagramMetadataEntityIds(baseDocument, draftDocument)).toEqual(["focus_tree:C08_PARTIV"]);
    expect(
      buildDiagramMetadataTextDrafts({
        baseDocument,
        draftDocument,
        entities,
        metadataTextByEntityId: { "focus_tree:C08_PARTIV": metadataText }
      })
    ).toEqual([
      {
        entityId: "focus_tree:C08_PARTIV",
        slot: "meta",
        text: [
          "type: focus_tree",
          "settings:",
          "    focuses:",
          "    -   id: FOCUS_ROOT",
          "        x: '12'",
          "        y: '0'",
          "    -   id: FOCUS_LEAF",
          "        parent: FOCUS_ROOT",
          "        x: '12'",
          "        y: '2'",
          "    -   id: FOCUS_SIBLING",
          "        parent: FOCUS_ROOT",
          "        x: '14'",
          "        y: '1'",
          "        prerequisites:",
          "        - FOCUS_ROOT",
          ""
        ].join("\n")
      }
    ]);
  });

  it("adds a PIHC3 child focus entry to focus tree metadata text", () => {
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
        sources: [{ slot: "meta", name: "meta.yaml", path: "/workspace/projects/PIHC3/src/modules/focus_tree/C08_PARTIV/meta.yaml", relative_path: "src/modules/focus_tree/C08_PARTIV/meta.yaml", extension: "yaml" }],
        metadata: {
          settings: {
            focuses: [
              { id: "FOCUS_ROOT", x: "12", y: "0" },
              { id: "FOCUS_CHILD", x: "12", y: "1", prerequisites: ["FOCUS_ROOT"] }
            ]
          }
        }
      }
    ]);
    const baseDocument = buildProjectDiagramDocument(browser, "focuses");
    const parent = baseDocument.nodes.find((node) => node.id === "FOCUS_ROOT");
    const draftDocument = insertDiagramChildNode(baseDocument, "FOCUS_ROOT", {
      id: "FOCUS_ROOT_CHILD",
      mode: "auto",
      width: parent?.width ?? 4,
      height: parent?.height ?? 2,
      title: "Focus Root Child",
      payload: parent?.payload ? { ...(parent.payload as Record<string, unknown>), embeddedId: "FOCUS_ROOT_CHILD" } : undefined
    });
    const entities = buildModuleEntities(browser, "focuses", "en");
    const metadataText = [
      "type: focus_tree",
      "settings:",
      "    focuses:",
      "    -   id: FOCUS_ROOT",
      "        x: '12'",
      "        y: '0'",
      "    -   id: FOCUS_CHILD",
      "        x: '12'",
      "        y: '1'",
      "        prerequisites:",
      "        - FOCUS_ROOT",
      ""
    ].join("\n");

    expect(changedDiagramMetadataEntityIds(baseDocument, draftDocument)).toEqual(["focus_tree:C08_PARTIV"]);
    expect(
      buildDiagramMetadataTextDrafts({
        baseDocument,
        draftDocument,
        entities,
        metadataTextByEntityId: { "focus_tree:C08_PARTIV": metadataText }
      })
    ).toEqual([
      {
        entityId: "focus_tree:C08_PARTIV",
        slot: "meta",
        text: [
          "type: focus_tree",
          "settings:",
          "    focuses:",
          "    -   id: FOCUS_ROOT",
          "        x: '12'",
          "        y: '0'",
          "    -   id: FOCUS_CHILD",
          "        x: '12'",
          "        y: '1'",
          "        prerequisites:",
          "        - FOCUS_ROOT",
          "    -   id: FOCUS_ROOT_CHILD",
          "        prerequisites:",
          "        - FOCUS_ROOT",
          ""
        ].join("\n")
      }
    ]);
  });

  it("adds PIHC3 focus relationship count fields when the focus list uses count fields", () => {
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
        sources: [{ slot: "meta", name: "meta.yaml", path: "/workspace/projects/PIHC3/src/modules/focus_tree/C08_PARTIV/meta.yaml", relative_path: "src/modules/focus_tree/C08_PARTIV/meta.yaml", extension: "yaml" }],
        metadata: {
          settings: {
            focus_count: 2,
            focuses: [
              { id: "FOCUS_ROOT", mutually_exclusive_count: 0, prerequisite_count: 0, x: "12", y: "0" },
              { id: "FOCUS_CHILD", mutually_exclusive_count: 0, prerequisite_count: 1, prerequisites: ["FOCUS_ROOT"], x: "12", y: "1" }
            ]
          }
        }
      }
    ]);
    const baseDocument = buildProjectDiagramDocument(browser, "focuses");
    const root = baseDocument.nodes.find((node) => node.id === "FOCUS_ROOT");
    const childDocument = insertDiagramChildNode(baseDocument, "FOCUS_ROOT", {
      id: "FOCUS_ROOT_CHILD",
      mode: "auto",
      width: root?.width ?? 4,
      height: root?.height ?? 2,
      title: "Focus Root Child",
      payload: root?.payload ? { ...(root.payload as Record<string, unknown>), embeddedId: "FOCUS_ROOT_CHILD" } : undefined
    });
    const rootDocument = insertDiagramRootNode(baseDocument, {
      id: "FOCUS_NEW_ROOT",
      mode: "auto",
      width: root?.width ?? 4,
      height: root?.height ?? 2,
      title: "Focus New Root",
      payload: root?.payload ? { ...(root.payload as Record<string, unknown>), embeddedId: "FOCUS_NEW_ROOT" } : undefined
    });
    const entities = buildModuleEntities(browser, "focuses", "en");
    const metadataText = [
      "type: focus_tree",
      "settings:",
      "    focus_count: 2",
      "    focuses:",
      "    -   id: FOCUS_ROOT",
      "        x: '12'",
      "        y: '0'",
      "        prerequisite_count: 0",
      "        mutually_exclusive_count: 0",
      "    -   id: FOCUS_CHILD",
      "        x: '12'",
      "        y: '1'",
      "        prerequisite_count: 1",
      "        prerequisites:",
      "        - FOCUS_ROOT",
      "        mutually_exclusive_count: 0",
      ""
    ].join("\n");

    expect(
      buildDiagramMetadataTextDrafts({
        baseDocument,
        draftDocument: childDocument,
        entities,
        metadataTextByEntityId: { "focus_tree:C08_PARTIV": metadataText }
      })
    ).toEqual([
      {
        entityId: "focus_tree:C08_PARTIV",
        slot: "meta",
        text: [
          "type: focus_tree",
          "settings:",
          "    focus_count: 3",
          "    focuses:",
          "    -   id: FOCUS_ROOT",
          "        x: '12'",
          "        y: '0'",
          "        prerequisite_count: 0",
          "        mutually_exclusive_count: 0",
          "    -   id: FOCUS_CHILD",
          "        x: '12'",
          "        y: '1'",
          "        prerequisite_count: 1",
          "        prerequisites:",
          "        - FOCUS_ROOT",
          "        mutually_exclusive_count: 0",
          "    -   id: FOCUS_ROOT_CHILD",
          "        prerequisite_count: 1",
          "        prerequisites:",
          "        - FOCUS_ROOT",
          "        mutually_exclusive_count: 0",
          ""
        ].join("\n")
      }
    ]);
    expect(
      buildDiagramMetadataTextDrafts({
        baseDocument,
        draftDocument: rootDocument,
        entities,
        metadataTextByEntityId: { "focus_tree:C08_PARTIV": metadataText }
      })
    ).toEqual([
      {
        entityId: "focus_tree:C08_PARTIV",
        slot: "meta",
        text: [
          "type: focus_tree",
          "settings:",
          "    focus_count: 3",
          "    focuses:",
          "    -   id: FOCUS_ROOT",
          "        x: '12'",
          "        y: '0'",
          "        prerequisite_count: 0",
          "        mutually_exclusive_count: 0",
          "    -   id: FOCUS_CHILD",
          "        x: '12'",
          "        y: '1'",
          "        prerequisite_count: 1",
          "        prerequisites:",
          "        - FOCUS_ROOT",
          "        mutually_exclusive_count: 0",
          "    -   id: FOCUS_NEW_ROOT",
          "        prerequisite_count: 0",
          "        mutually_exclusive_count: 0",
          ""
        ].join("\n")
      }
    ]);
  });

  it("adds a PIHC3 root focus entry to focus tree metadata text", () => {
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
        sources: [{ slot: "meta", name: "meta.yaml", path: "/workspace/projects/PIHC3/src/modules/focus_tree/C08_PARTIV/meta.yaml", relative_path: "src/modules/focus_tree/C08_PARTIV/meta.yaml", extension: "yaml" }],
        metadata: {
          settings: {
            focuses: [
              { id: "FOCUS_ROOT", x: "12", y: "0" },
              { id: "FOCUS_CHILD", x: "12", y: "1", prerequisites: ["FOCUS_ROOT"] }
            ]
          }
        }
      }
    ]);
    const baseDocument = buildProjectDiagramDocument(browser, "focuses");
    const root = baseDocument.nodes.find((node) => node.id === "FOCUS_ROOT");
    const draftDocument = insertDiagramRootNode(baseDocument, {
      id: "FOCUS_NEW_ROOT",
      mode: "auto",
      width: root?.width ?? 4,
      height: root?.height ?? 2,
      title: "Focus New Root",
      payload: root?.payload ? { ...(root.payload as Record<string, unknown>), embeddedId: "FOCUS_NEW_ROOT" } : undefined
    });
    const entities = buildModuleEntities(browser, "focuses", "en");
    const metadataText = [
      "type: focus_tree",
      "settings:",
      "    focuses:",
      "    -   id: FOCUS_ROOT",
      "        x: '12'",
      "        y: '0'",
      "    -   id: FOCUS_CHILD",
      "        x: '12'",
      "        y: '1'",
      "        prerequisites:",
      "        - FOCUS_ROOT",
      ""
    ].join("\n");

    expect(changedDiagramMetadataEntityIds(baseDocument, draftDocument)).toEqual(["focus_tree:C08_PARTIV"]);
    expect(
      buildDiagramMetadataTextDrafts({
        baseDocument,
        draftDocument,
        entities,
        metadataTextByEntityId: { "focus_tree:C08_PARTIV": metadataText }
      })
    ).toEqual([
      {
        entityId: "focus_tree:C08_PARTIV",
        slot: "meta",
        text: [
          "type: focus_tree",
          "settings:",
          "    focuses:",
          "    -   id: FOCUS_ROOT",
          "        x: '12'",
          "        y: '0'",
          "    -   id: FOCUS_CHILD",
          "        x: '12'",
          "        y: '1'",
          "        prerequisites:",
          "        - FOCUS_ROOT",
          "    -   id: FOCUS_NEW_ROOT",
          ""
        ].join("\n")
      }
    ]);
  });

  it("adds the first PIHC3 root focus entry to empty focus tree metadata text", () => {
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
        sources: [{ slot: "meta", name: "meta.yaml", path: "/workspace/projects/PIHC3/src/modules/focus_tree/C08_PARTIV/meta.yaml", relative_path: "src/modules/focus_tree/C08_PARTIV/meta.yaml", extension: "yaml" }],
        metadata: { settings: { focuses: [] } }
      }
    ]);
    const baseDocument = buildProjectDiagramDocument(browser, "focuses");
    const template = baseDocument.nodes.find((node) => node.id === "C08_PARTIV");
    const draftDocument = insertDiagramRootNode(baseDocument, {
      id: "FOCUS_NEW_ROOT",
      mode: "auto",
      width: template?.width ?? 6,
      height: template?.height ?? 2,
      title: "Focus New Root",
      payload: template?.payload ? { ...(template.payload as Record<string, unknown>), embeddedId: "FOCUS_NEW_ROOT", embeddedKind: "focus" } : undefined
    });
    const entities = buildModuleEntities(browser, "focuses", "en");
    const metadataText = ["type: focus_tree", "settings:", "    focuses:", ""].join("\n");

    expect(changedDiagramMetadataEntityIds(baseDocument, draftDocument)).toEqual(["focus_tree:C08_PARTIV"]);
    expect(
      buildDiagramMetadataTextDrafts({
        baseDocument,
        draftDocument,
        entities,
        metadataTextByEntityId: { "focus_tree:C08_PARTIV": metadataText }
      })
    ).toEqual([
      {
        entityId: "focus_tree:C08_PARTIV",
        slot: "meta",
        text: ["type: focus_tree", "settings:", "    focuses:", "        -   id: FOCUS_NEW_ROOT", ""].join("\n")
      }
    ]);
  });

  it("expands inline empty PIHC3 focus lists before adding the first root focus entry", () => {
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
        sources: [{ slot: "meta", name: "meta.yaml", path: "/workspace/projects/PIHC3/src/modules/focus_tree/C08_PARTIV/meta.yaml", relative_path: "src/modules/focus_tree/C08_PARTIV/meta.yaml", extension: "yaml" }],
        metadata: { settings: { focuses: [] } }
      }
    ]);
    const baseDocument = buildProjectDiagramDocument(browser, "focuses");
    const template = baseDocument.nodes.find((node) => node.id === "C08_PARTIV");
    const draftDocument = insertDiagramRootNode(baseDocument, {
      id: "FOCUS_NEW_ROOT",
      mode: "auto",
      width: template?.width ?? 6,
      height: template?.height ?? 2,
      title: "Focus New Root",
      payload: template?.payload ? { ...(template.payload as Record<string, unknown>), embeddedId: "FOCUS_NEW_ROOT", embeddedKind: "focus" } : undefined
    });
    const entities = buildModuleEntities(browser, "focuses", "en");
    const metadataText = ["type: focus_tree", "settings:", "    focuses: []", ""].join("\n");

    expect(
      buildDiagramMetadataTextDrafts({
        baseDocument,
        draftDocument,
        entities,
        metadataTextByEntityId: { "focus_tree:C08_PARTIV": metadataText }
      })
    ).toEqual([
      {
        entityId: "focus_tree:C08_PARTIV",
        slot: "meta",
        text: ["type: focus_tree", "settings:", "    focuses:", "        -   id: FOCUS_NEW_ROOT", ""].join("\n")
      }
    ]);
  });

  it("adds count fields to the first PIHC3 focus entry when empty metadata has focus_count", () => {
    const browser = browserPayload([
      {
        id: "focus_tree:C02_ALT",
        kind: "module",
        layout: "canonical",
        family_id: "focuses",
        family: "focus_tree",
        object_id: "C02_ALT",
        module_id: "C02_ALT",
        title: "C02 Alt",
        root: "/workspace/projects/PIHC3/src/modules/focus_tree/C02_ALT",
        relative_root: "src/modules/focus_tree/C02_ALT",
        source_count: 1,
        sources: [{ slot: "meta", name: "meta.yaml", path: "/workspace/projects/PIHC3/src/modules/focus_tree/C02_ALT/meta.yaml", relative_path: "src/modules/focus_tree/C02_ALT/meta.yaml", extension: "yaml" }],
        metadata: { settings: { focus_count: 0, focuses: [] } }
      }
    ]);
    const baseDocument = buildProjectDiagramDocument(browser, "focuses");
    const template = baseDocument.nodes.find((node) => node.id === "C02_ALT");
    const draftDocument = insertDiagramRootNode(baseDocument, {
      id: "FOCUS_NEW_ROOT",
      mode: "auto",
      width: template?.width ?? 6,
      height: template?.height ?? 2,
      title: "Focus New Root",
      payload: template?.payload ? { ...(template.payload as Record<string, unknown>), embeddedId: "FOCUS_NEW_ROOT", embeddedKind: "focus" } : undefined
    });
    const entities = buildModuleEntities(browser, "focuses", "en");
    const metadataText = ["type: focus_tree", "settings:", "    focus_count: 0", "    focuses: []", ""].join("\n");

    expect(
      buildDiagramMetadataTextDrafts({
        baseDocument,
        draftDocument,
        entities,
        metadataTextByEntityId: { "focus_tree:C02_ALT": metadataText }
      })
    ).toEqual([
      {
        entityId: "focus_tree:C02_ALT",
        slot: "meta",
        text: [
          "type: focus_tree",
          "settings:",
          "    focus_count: 1",
          "    focuses:",
          "        -   id: FOCUS_NEW_ROOT",
          "            prerequisite_count: 0",
          "            mutually_exclusive_count: 0",
          ""
        ].join("\n")
      }
    ]);
  });
});
