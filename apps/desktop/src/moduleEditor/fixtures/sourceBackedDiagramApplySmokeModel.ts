import { clearDiagramTreeParent, setDiagramDependencyEdge, setDiagramNodeLayoutHints, setDiagramReferenceEdge } from "../../diagramEditor/layoutModel";
import type { DiagramDocument } from "../../diagramEditor/layoutModel";
import { buildProjectDiagramDocument } from "../../diagramEditor/projectDiagram";
import {
  sourceBackedSmokeBrowserPayload,
  sourceBackedSmokeProjectRoot
} from "../../diagramEditor/fixtures/sourceBackedSmokeModel";
import type { ProjectBrowserPayload } from "../../types";
import { buildDiagramMetadataTextDrafts } from "../diagramMetadata";
import { buildModuleEntities } from "../model";
import { buildDiagramApplyDraftPlan, buildDiagramChangedEntities } from "../ModuleEditor";

export const sourceBackedClearParentFocusId = "FOCUS_C08_SECOND_SUMMIT";
export const sourceBackedClearParentSourceEditPath = `${sourceBackedSmokeProjectRoot}/src/modules/focus_tree/C08_PARTIV/legacy/C08_SECOND_SUMMIT/info.json`;
export const sourceBackedClearParentSourceEditText = `${JSON.stringify(
  {
    tree: "C08_PARTIV",
    parent: null,
    priority: 10,
    prerequisites: ["FOCUS_C08_CANTERLOT_MIND"],
    x: 9,
    y: 1
  },
  null,
  4
)}\n`;

export const sourceBackedClearParentBrowserPayload: ProjectBrowserPayload = {
  ...sourceBackedSmokeBrowserPayload,
  items: sourceBackedSmokeBrowserPayload.items.map((item) =>
    item.id === "focus_tree:C08_PARTIV"
      ? {
          ...item,
          source_root: `${sourceBackedSmokeProjectRoot}/src`,
          source_root_relative_path: "src",
          sources: [
            {
              slot: "meta",
              name: "meta.yaml",
              path: `${sourceBackedSmokeProjectRoot}/src/modules/focus_tree/C08_PARTIV/meta.yaml`,
              relative_path: "src/modules/focus_tree/C08_PARTIV/meta.yaml",
              extension: "yaml"
            }
          ]
        }
      : item
  )
};

export const sourceBackedClearParentBaseDocument: DiagramDocument = buildProjectDiagramDocument(sourceBackedClearParentBrowserPayload, "focuses");
export const sourceBackedClearParentDraftDocument: DiagramDocument = clearDiagramTreeParent(sourceBackedClearParentBaseDocument, sourceBackedClearParentFocusId);
export const sourceBackedClearParentEntities = buildModuleEntities(sourceBackedClearParentBrowserPayload, "focuses", "en");
export const sourceBackedClearParentRows = buildDiagramChangedEntities(
  sourceBackedClearParentBaseDocument,
  sourceBackedClearParentDraftDocument,
  sourceBackedClearParentEntities
);
export const sourceBackedClearParentMetadataText = [
  "type: focus_tree",
  "settings:",
  "    source_focuses:",
  "    -   folder: C08_CANTERLOT_MIND",
  "        focus_id: FOCUS_C08_CANTERLOT_MIND",
  "        source_path: C08_CANTERLOT_MIND",
  "        tree: C08_PARTIV",
  "        parent:",
  "        x: '9'",
  "        y: '0'",
  "    -   folder: C08_SECOND_SUMMIT",
  "        focus_id: FOCUS_C08_SECOND_SUMMIT",
  "        source_path: C08_SECOND_SUMMIT",
  "        tree: C08_PARTIV",
  "        parent: FOCUS_C08_CANTERLOT_MIND",
  "        x: '9'",
  "        y: '1'",
  "        priority: '10'",
  ""
].join("\n");
export const sourceBackedClearParentSourceInfoText = `${JSON.stringify(
  {
    tree: "C08_PARTIV",
    parent: "FOCUS_C08_CANTERLOT_MIND",
    priority: 10,
    prerequisites: ["FOCUS_C08_CANTERLOT_MIND"],
    dx: 0,
    dy: 1
  },
  null,
  4
)}\n`;

export const sourceBackedClearParentDrafts = buildDiagramMetadataTextDrafts({
  baseDocument: sourceBackedClearParentBaseDocument,
  draftDocument: sourceBackedClearParentDraftDocument,
  entities: sourceBackedClearParentEntities,
  metadataTextByEntityId: {
    "focus_tree:C08_PARTIV": sourceBackedClearParentMetadataText
  },
  sourceTextByPath: {
    [sourceBackedClearParentSourceEditPath]: sourceBackedClearParentSourceInfoText
  }
});

export const sourceBackedClearParentApplyPlan = buildDiagramApplyDraftPlan(
  sourceBackedClearParentRows,
  sourceBackedClearParentDrafts,
  sourceBackedClearParentEntities
);

export const sourceBackedLayoutHintFocusId = "FOCUS_C08_TO_THE_WAR";
export const sourceBackedLayoutHintSourceEditPath = `${sourceBackedSmokeProjectRoot}/src/modules/focus_tree/C08_PARTIV/legacy/C08_TO_THE_WAR/info.json`;
export const sourceBackedLayoutHintSourceInfoText = `${JSON.stringify(
  {
    tree: "C08_PARTIV",
    parent: "FOCUS_C08_SECOND_SUMMIT",
    x: 9,
    y: 2,
    priority: 10,
    prerequisites: ["FOCUS_C08_SECOND_SUMMIT"]
  },
  null,
  4
)}\n`;
export const sourceBackedLayoutHintSourceEditText = `${JSON.stringify(
  {
    tree: "C08_PARTIV",
    parent: "FOCUS_C08_SECOND_SUMMIT",
    x: 9,
    y: 2,
    priority: 15,
    prerequisites: ["FOCUS_C08_SECOND_SUMMIT"],
    w: 8,
    dw: 2,
    dc: 1
  },
  null,
  4
)}\n`;
export const sourceBackedLayoutHintBaseDocument: DiagramDocument = sourceBackedClearParentBaseDocument;
export const sourceBackedLayoutHintDraftDocument: DiagramDocument = setDiagramNodeLayoutHints(
  sourceBackedLayoutHintBaseDocument,
  sourceBackedLayoutHintFocusId,
  {
    priority: 15,
    subtreeCenterOffset: 1,
    subtreeWidth: 8,
    subtreeWidthDelta: 2
  }
);
export const sourceBackedLayoutHintEntities = sourceBackedClearParentEntities;
export const sourceBackedLayoutHintRows = buildDiagramChangedEntities(
  sourceBackedLayoutHintBaseDocument,
  sourceBackedLayoutHintDraftDocument,
  sourceBackedLayoutHintEntities
);
export const sourceBackedLayoutHintDrafts = buildDiagramMetadataTextDrafts({
  baseDocument: sourceBackedLayoutHintBaseDocument,
  draftDocument: sourceBackedLayoutHintDraftDocument,
  entities: sourceBackedLayoutHintEntities,
  metadataTextByEntityId: {},
  sourceTextByPath: {
    [sourceBackedLayoutHintSourceEditPath]: sourceBackedLayoutHintSourceInfoText
  }
});
export const sourceBackedLayoutHintApplyPlan = buildDiagramApplyDraftPlan(
  sourceBackedLayoutHintRows,
  sourceBackedLayoutHintDrafts,
  sourceBackedLayoutHintEntities
);

export const sourceBackedRelationshipFocusId = "FOCUS_C08_THE_RISING_FIRE";
export const sourceBackedRelationshipPrerequisiteId = "FOCUS_C08_CANTERLOT_MIND";
export const sourceBackedRelationshipReferenceId = "FOCUS_C08_PLAN_TWILIGHT";
export const sourceBackedRelationshipSourceEditPath = `${sourceBackedSmokeProjectRoot}/src/modules/focus_tree/C08_PARTIV/legacy/C08_THE_RISING_FIRE/info.json`;
export const sourceBackedRelationshipSourceInfoText = `${JSON.stringify(
  {
    tree: "C08_PARTIV",
    parent: null,
    x: 3,
    y: 5
  },
  null,
  4
)}\n`;
export const sourceBackedRelationshipSourceEditText = `${JSON.stringify(
  {
    tree: "C08_PARTIV",
    parent: null,
    x: 3,
    y: 5,
    prerequisites: [sourceBackedRelationshipPrerequisiteId],
    mutually_exclusive: [sourceBackedRelationshipReferenceId]
  },
  null,
  4
)}\n`;
export const sourceBackedRelationshipBaseDocument: DiagramDocument = sourceBackedClearParentBaseDocument;
export const sourceBackedRelationshipDraftDocument: DiagramDocument = setDiagramReferenceEdge(
  setDiagramDependencyEdge(
    sourceBackedRelationshipBaseDocument,
    sourceBackedRelationshipPrerequisiteId,
    sourceBackedRelationshipFocusId,
    true
  ),
  sourceBackedRelationshipFocusId,
  sourceBackedRelationshipReferenceId,
  true
);
export const sourceBackedRelationshipEntities = sourceBackedClearParentEntities;
export const sourceBackedRelationshipRows = buildDiagramChangedEntities(
  sourceBackedRelationshipBaseDocument,
  sourceBackedRelationshipDraftDocument,
  sourceBackedRelationshipEntities
);
export const sourceBackedRelationshipDrafts = buildDiagramMetadataTextDrafts({
  baseDocument: sourceBackedRelationshipBaseDocument,
  draftDocument: sourceBackedRelationshipDraftDocument,
  entities: sourceBackedRelationshipEntities,
  metadataTextByEntityId: {},
  sourceTextByPath: {
    [sourceBackedRelationshipSourceEditPath]: sourceBackedRelationshipSourceInfoText
  }
});
export const sourceBackedRelationshipApplyPlan = buildDiagramApplyDraftPlan(
  sourceBackedRelationshipRows,
  sourceBackedRelationshipDrafts,
  sourceBackedRelationshipEntities
);
