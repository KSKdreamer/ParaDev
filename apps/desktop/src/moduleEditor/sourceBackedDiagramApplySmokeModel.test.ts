import { describe, expect, it } from "vitest";
import { makeDiagramSelectedNodeRelative } from "../diagramEditor/layoutModel";
import {
  c01CozyGlowSmokeSourceInfoText,
  c01MainSmokeBrowserItem,
  c01MainSmokeDiagramDocument,
  sourceBackedSmokeBrowserPayload,
  sourceBackedSmokeProjectRoot
} from "../diagramEditor/fixtures/sourceBackedSmokeModel";
import { buildDiagramMetadataTextDrafts, changedDiagramMetadataSourceInfoPaths } from "./diagramMetadata";
import { buildModuleEntities } from "./model";
import {
  sourceBackedClearParentApplyPlan,
  sourceBackedClearParentDraftDocument,
  sourceBackedClearParentSourceEditPath,
  sourceBackedClearParentSourceEditText,
  sourceBackedLayoutHintApplyPlan,
  sourceBackedLayoutHintDraftDocument,
  sourceBackedLayoutHintSourceEditPath,
  sourceBackedLayoutHintSourceEditText,
  sourceBackedRelationshipApplyPlan,
  sourceBackedRelationshipDraftDocument,
  sourceBackedRelationshipFocusId,
  sourceBackedRelationshipPrerequisiteId,
  sourceBackedRelationshipReferenceId,
  sourceBackedRelationshipSourceEditPath,
  sourceBackedRelationshipSourceEditText
} from "./fixtures/sourceBackedDiagramApplySmokeModel";
import { buildDiagramApplyDraftPlan, buildDiagramChangedEntities } from "./ModuleEditor";

describe("source-backed diagram apply smoke model", () => {
  it("builds a C01_MAIN source-info draft when a focus mode switch chooses relative positioning", () => {
    const focusId = "FOCUS_C01_COZY_GLOW_CORONATION";
    const sourceInfoPath = `${sourceBackedSmokeProjectRoot}/src/modules/focus_tree/C01_MAIN/legacy/C01_COZY_GLOW_CORONATION/info.json`;
    const browser = {
      ...sourceBackedSmokeBrowserPayload,
      items: [c01MainSmokeBrowserItem]
    };
    const draftDocument = makeDiagramSelectedNodeRelative(c01MainSmokeDiagramDocument, focusId);
    const entities = buildModuleEntities(browser, "focuses", "en");
    const rows = buildDiagramChangedEntities(c01MainSmokeDiagramDocument, draftDocument, entities);
    const drafts = buildDiagramMetadataTextDrafts({
      baseDocument: c01MainSmokeDiagramDocument,
      draftDocument,
      entities,
      metadataTextByEntityId: {},
      sourceTextByPath: {
        [sourceInfoPath]: c01CozyGlowSmokeSourceInfoText
      }
    });
    const applyPlan = buildDiagramApplyDraftPlan(rows, drafts, entities);

    expect(draftDocument.nodes.find((node) => node.id === focusId)).toMatchObject({
      mode: "relative",
      parentId: "FOCUS_C01_CANTERLOT_PACT"
    });
    expect(changedDiagramMetadataSourceInfoPaths(c01MainSmokeDiagramDocument, draftDocument)).toEqual([sourceInfoPath]);
    expect(applyPlan).toMatchObject({ ok: true });
    expect(applyPlan.ok ? applyPlan.rows : []).toEqual([
      expect.objectContaining({
        draftText: expect.stringContaining('"relative_position_id": "FOCUS_C01_CANTERLOT_PACT"'),
        path: "src/modules/focus_tree/C01_MAIN/legacy/C01_COZY_GLOW_CORONATION/info.json"
      })
    ]);
    expect(applyPlan.ok ? applyPlan.sourceEdits : []).toContainEqual({
      path: sourceInfoPath,
      text: expect.stringContaining('"relative_position_id": "FOCUS_C01_CANTERLOT_PACT"')
    });
  });

  it("builds a PIHC source-info draft that preserves explicit root parent null", () => {
    expect(sourceBackedClearParentDraftDocument.nodes.find((node) => node.id === "FOCUS_C08_SECOND_SUMMIT")).toMatchObject({
      mode: "absolute",
      x: 12,
      y: 1
    });
    expect(sourceBackedClearParentDraftDocument.nodes.find((node) => node.id === "FOCUS_C08_SECOND_SUMMIT")?.parentId).toBeUndefined();
    expect(sourceBackedClearParentApplyPlan).toMatchObject({ ok: true });
    expect(sourceBackedClearParentApplyPlan.ok ? sourceBackedClearParentApplyPlan.sourceEdits : []).toContainEqual({
      path: sourceBackedClearParentSourceEditPath,
      text: sourceBackedClearParentSourceEditText
    });
    expect(sourceBackedClearParentSourceEditText).toContain('"parent": null');
  });

  it("builds a PIHC source-info draft for source-backed layout hint edits", () => {
    expect(sourceBackedLayoutHintDraftDocument.nodes.find((node) => node.id === "FOCUS_C08_TO_THE_WAR")).toMatchObject({
      priority: 15,
      subtreeCenterOffset: 1,
      subtreeWidth: 8,
      subtreeWidthDelta: 2
    });
    expect(sourceBackedLayoutHintApplyPlan).toMatchObject({ ok: true });
    expect(sourceBackedLayoutHintApplyPlan.ok ? sourceBackedLayoutHintApplyPlan.rows : []).toEqual([
      expect.objectContaining({
        draftText: sourceBackedLayoutHintSourceEditText,
        path: "src/modules/focus_tree/C08_PARTIV/legacy/C08_TO_THE_WAR/info.json"
      })
    ]);
    expect(sourceBackedLayoutHintApplyPlan.ok ? sourceBackedLayoutHintApplyPlan.sourceEdits : []).toContainEqual({
      path: sourceBackedLayoutHintSourceEditPath,
      text: sourceBackedLayoutHintSourceEditText
    });
    expect(sourceBackedLayoutHintSourceEditText).toContain('"w": 8');
    expect(sourceBackedLayoutHintSourceEditText).toContain('"dw": 2');
    expect(sourceBackedLayoutHintSourceEditText).toContain('"dc": 1');
  });

  it("builds a PIHC source-info draft for source-backed relationship edits", () => {
    expect(sourceBackedRelationshipDraftDocument.edges).toContainEqual(
      expect.objectContaining({
        kind: "dependency",
        source: sourceBackedRelationshipPrerequisiteId,
        target: sourceBackedRelationshipFocusId
      })
    );
    expect(sourceBackedRelationshipDraftDocument.edges).toContainEqual(
      expect.objectContaining({
        kind: "reference",
        source: sourceBackedRelationshipFocusId,
        target: sourceBackedRelationshipReferenceId
      })
    );
    expect(sourceBackedRelationshipApplyPlan).toMatchObject({ ok: true });
    expect(sourceBackedRelationshipApplyPlan.ok ? sourceBackedRelationshipApplyPlan.rows : []).toEqual([
      expect.objectContaining({
        draftText: sourceBackedRelationshipSourceEditText,
        path: "src/modules/focus_tree/C08_PARTIV/legacy/C08_THE_RISING_FIRE/info.json"
      })
    ]);
    expect(sourceBackedRelationshipApplyPlan.ok ? sourceBackedRelationshipApplyPlan.sourceEdits : []).toContainEqual({
      path: sourceBackedRelationshipSourceEditPath,
      text: sourceBackedRelationshipSourceEditText
    });
    expect(sourceBackedRelationshipSourceEditText).toContain(`"prerequisites": [\n        "${sourceBackedRelationshipPrerequisiteId}"`);
    expect(sourceBackedRelationshipSourceEditText).toContain(`"mutually_exclusive": [\n        "${sourceBackedRelationshipReferenceId}"`);
  });
});
