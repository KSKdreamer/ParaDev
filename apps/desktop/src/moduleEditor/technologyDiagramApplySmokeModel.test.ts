import { describe, expect, it } from "vitest";
import {
  buildTechnologyApplySmokeDraftPlan,
  technologyApplySmokeAddedLandmineDependencyDocument,
  technologyApplySmokeMovedFirearmDocument,
  technologyApplySmokeProjectRoot
} from "./fixtures/technologyDiagramApplySmokeModel";

describe("technology diagram apply smoke model", () => {
  it("builds a PIHC technology metadata draft for position edits", () => {
    const plan = buildTechnologyApplySmokeDraftPlan(technologyApplySmokeMovedFirearmDocument);

    expect(plan).toMatchObject({ ok: true });
    expect(plan.ok ? plan.sourceEdits : []).toContainEqual({
      path: `${technologyApplySmokeProjectRoot}/src/modules/technology/TECHNOLOGY_FIREARM_I/meta.yaml`,
      text: [
        "type: technology",
        "settings:",
        "    folder:",
        "        position:",
        "            x: 5",
        "            y: 2",
        "    legacy_source_image:",
        "        path: legacy/default.png",
        "    dependency_ids:",
        "    - TECHNOLOGY_POWDER_EXPLOSIVE",
        ""
      ].join("\n")
    });
  });

  it("builds PIHC technology metadata drafts for dependency and path-target edits", () => {
    const plan = buildTechnologyApplySmokeDraftPlan(technologyApplySmokeAddedLandmineDependencyDocument);
    const edits = plan.ok ? Object.fromEntries(plan.sourceEdits.map((edit) => [edit.path, edit.text])) : {};

    expect(plan).toMatchObject({ ok: true });
    expect(edits[`${technologyApplySmokeProjectRoot}/src/modules/technology/TECHNOLOGY_LANDMINE/meta.yaml`]).toBe(
      [
        "type: technology",
        "settings:",
        "    folder_position:",
        "        x: 6",
        "        y: 3",
        "    legacy_source_image:",
        "        path: legacy/default.png",
        "    dependency_ids:",
        "    - TECHNOLOGY_POWDER_EXPLOSIVE",
        "    path_target_ids: []",
        ""
      ].join("\n")
    );
    expect(edits[`${technologyApplySmokeProjectRoot}/src/modules/technology/TECHNOLOGY_POWDER_EXPLOSIVE/meta.yaml`]).toBe(
      [
        "type: technology",
        "settings:",
        "    folder_position:",
        "        x: 2",
        "        y: 3",
        "    legacy_source_image:",
        "        path: legacy/default.png",
        "    path_target_ids:",
        "    - TECHNOLOGY_FIREARM_I",
        "    - TECHNOLOGY_LANDMINE",
        ""
      ].join("\n")
    );
  });
});
