import { describe, expect, it } from "vitest";
import {
  moveDiagramNodeKeepingDescendants,
  moveDiagramNodeRelayoutDescendants,
  moveDiagramSubtree,
  resolveDiagramLayout,
  setDiagramNodeLayoutHints
} from "./layoutModel";
import { c01MainSmokeDiagramDocument, c01MainSmokeSummary, sourceBackedSmokeDiagramDocument, sourceBackedSmokeSummary } from "./fixtures/sourceBackedSmokeModel";

describe("source-backed diagram smoke model", () => {
  it("parses a source-backed C01_MAIN focus tree fixture for visual smoke coverage", () => {
    const canterlotPact = c01MainSmokeDiagramDocument.nodes.find((node) => node.id === "FOCUS_C01_CANTERLOT_PACT");
    const demChange = c01MainSmokeDiagramDocument.nodes.find((node) => node.id === "FOCUS_C01_DEM_CHANGE");

    expect(c01MainSmokeDiagramDocument.gridSizePx).toBe(96);
    expect(c01MainSmokeSummary.nodeCount).toBe(3);
    expect(c01MainSmokeSummary.previewNodeCount).toBe(3);
    expect(c01MainSmokeSummary.legacyNodeCount).toBe(0);
    expect(c01MainSmokeSummary.edgeCount).toBeGreaterThan(1);
    expect(canterlotPact).toMatchObject({
      id: "FOCUS_C01_CANTERLOT_PACT",
      imageUrl: "src/modules/focus_tree/C01_MAIN/icons/FOCUS_C01_CANTERLOT_PACT.png",
      mode: "absolute"
    });
    expect(demChange).toMatchObject({
      id: "FOCUS_C01_DEM_CHANGE",
      imageUrl: "src/modules/focus_tree/C01_MAIN/icons/FOCUS_C01_DEM_CHANGE.png"
    });
  });

  it("uses C08_PARTIV source layout roots while keeping prerequisite dependency edges", () => {
    const risingFire = sourceBackedSmokeDiagramDocument.nodes.find((node) => node.id === "FOCUS_C08_THE_RISING_FIRE");
    const canterlotMind = sourceBackedSmokeDiagramDocument.nodes.find((node) => node.id === "FOCUS_C08_CANTERLOT_MIND");
    const resolved = resolveDiagramLayout(sourceBackedSmokeDiagramDocument).nodesById;

    expect(sourceBackedSmokeSummary.nodeCount).toBe(9);
    expect(sourceBackedSmokeSummary.edgeCount).toBe(20);
    expect(sourceBackedSmokeSummary.previewNodeCount).toBe(9);
    expect(sourceBackedSmokeSummary.legacyNodeCount).toBe(0);
    expect(sourceBackedSmokeSummary.explicitRootIds).toEqual(["FOCUS_C08_CANTERLOT_MIND", "FOCUS_C08_THE_RISING_FIRE"]);
    expect(sourceBackedSmokeSummary.dependencyEdgeIds).toContain(
      "dependency:FOCUS_C08_TO_THE_WAR->FOCUS_C08_PLAN_TWILIGHT"
    );
    expect(sourceBackedSmokeSummary.treeEdgeIds).not.toContain("tree:FOCUS_C08_CANTERLOT_MIND->FOCUS_C08_THE_RISING_FIRE");
    expect(canterlotMind).toMatchObject({ mode: "absolute", x: 12, y: 0 });
    expect(canterlotMind?.parentId).toBeUndefined();
    expect(risingFire).toMatchObject({ mode: "absolute", x: 5, y: 5 });
    expect(risingFire?.parentId).toBeUndefined();
    expect(sourceBackedSmokeDiagramDocument.edges).not.toContainEqual({
      id: "tree:FOCUS_C08_CANTERLOT_MIND->FOCUS_C08_THE_RISING_FIRE",
      source: "FOCUS_C08_CANTERLOT_MIND",
      target: "FOCUS_C08_THE_RISING_FIRE",
      kind: "tree"
    });
    expect(resolved.FOCUS_C08_THE_RISING_FIRE).toMatchObject({
      worldX: 5,
      worldY: 5
    });
    expect(resolved.FOCUS_C08_TO_THE_WAR.worldY).toBe(2);
    expect(resolved.FOCUS_C08_PLAN_TWILIGHT.worldY).toBe(3);
    expect(resolved.FOCUS_C08_PLAN_STARLIGHT.worldY).toBe(3);
    expect(resolved.FOCUS_C08_PLAN_SUNBURST.worldY).toBe(3);
    expect(resolved.FOCUS_C08_CANTERLOT_MIND.worldX).toBe(12);
    expect(resolved.FOCUS_C08_SECOND_SUMMIT.worldX).toBe(12);
    expect(resolved.FOCUS_C08_TO_THE_WAR.worldX).toBe(12);
    expect(resolved.FOCUS_C08_PLAN_TWILIGHT.worldX).toBe(9);
    expect(resolved.FOCUS_C08_PLAN_STARLIGHT.worldX).toBe(12);
    expect(resolved.FOCUS_C08_PLAN_SUNBURST.worldX).toBe(15);
    expect(resolved.FOCUS_C08_THE_RISING_FIRE.worldX).toBe(5);
    expect(resolved.FOCUS_C08_T_CADENCE.worldX).toBe(4);
    expect(resolved.FOCUS_C08_T_TRIXIE.worldX).toBe(6);
  });

  it("moves source-backed focus branches with HOI4-style subtree options", () => {
    const branchId = "FOCUS_C08_TO_THE_WAR";
    const delta = { dx: 2, dy: 0 };
    const movedSubtree = moveDiagramSubtree(sourceBackedSmokeDiagramDocument, branchId, delta);
    const subtreeResolved = resolveDiagramLayout(movedSubtree).nodesById;

    expect(subtreeResolved[branchId].worldX).toBe(14);
    expect(subtreeResolved.FOCUS_C08_PLAN_TWILIGHT.worldX).toBe(11);
    expect(subtreeResolved.FOCUS_C08_PLAN_STARLIGHT.worldX).toBe(14);
    expect(subtreeResolved.FOCUS_C08_PLAN_SUNBURST.worldX).toBe(17);
    expect(subtreeResolved.FOCUS_C08_THE_RISING_FIRE.worldX).toBe(5);

    const nodeOnly = moveDiagramNodeKeepingDescendants(sourceBackedSmokeDiagramDocument, branchId, delta);
    const nodeOnlyResolved = resolveDiagramLayout(nodeOnly).nodesById;

    expect(nodeOnlyResolved[branchId].worldX).toBe(14);
    expect(nodeOnlyResolved.FOCUS_C08_PLAN_TWILIGHT.worldX).toBe(9);
    expect(nodeOnlyResolved.FOCUS_C08_PLAN_STARLIGHT.worldX).toBe(12);
    expect(nodeOnlyResolved.FOCUS_C08_PLAN_SUNBURST.worldX).toBe(15);
    expect(nodeOnly.nodes.find((node) => node.id === "FOCUS_C08_PLAN_TWILIGHT")).toMatchObject({
      mode: "absolute",
      x: 9,
      y: 3
    });

    const relaidOut = moveDiagramNodeRelayoutDescendants(sourceBackedSmokeDiagramDocument, branchId, delta);
    const relaidOutResolved = resolveDiagramLayout(relaidOut).nodesById;

    expect(relaidOutResolved[branchId].worldX).toBe(14);
    expect(relaidOutResolved.FOCUS_C08_PLAN_TWILIGHT.worldX).toBe(12);
    expect(relaidOutResolved.FOCUS_C08_PLAN_STARLIGHT.worldX).toBe(14);
    expect(relaidOutResolved.FOCUS_C08_PLAN_SUNBURST.worldX).toBe(16);
    expect(relaidOut.nodes.find((node) => node.id === "FOCUS_C08_PLAN_TWILIGHT")).toMatchObject({
      mode: "auto"
    });
  });

  it("reflows source-backed focus children when PIHC layout hints change", () => {
    const hinted = setDiagramNodeLayoutHints(sourceBackedSmokeDiagramDocument, "FOCUS_C08_TO_THE_WAR", {
      priority: 15,
      subtreeCenterOffset: 1,
      subtreeWidth: 8,
      subtreeWidthDelta: 2
    });
    const resolved = resolveDiagramLayout(hinted).nodesById;

    expect(hinted.nodes.find((node) => node.id === "FOCUS_C08_TO_THE_WAR")).toMatchObject({
      priority: 15,
      subtreeCenterOffset: 1,
      subtreeWidth: 8,
      subtreeWidthDelta: 2
    });
    expect(resolved.FOCUS_C08_TO_THE_WAR.worldX).toBe(12);
    expect(resolved.FOCUS_C08_PLAN_TWILIGHT.worldX).toBe(8);
    expect(resolved.FOCUS_C08_PLAN_STARLIGHT.worldX).toBe(11);
    expect(resolved.FOCUS_C08_PLAN_SUNBURST.worldX).toBe(14);
    expect(resolved.FOCUS_C08_THE_RISING_FIRE.worldX).toBe(5);
  });
});
