import { describe, expect, it } from "vitest";
import { resolveDiagramLayout } from "./layoutModel";
import { buildProjectDiagramDocument } from "./projectDiagram";
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

describe("project browser diagram adapter", () => {
  it("builds technology diagrams from PIHC3 folder positions and dependency metadata", () => {
    const document = buildProjectDiagramDocument(
      browserPayload([
        {
          id: "technology:TECHNOLOGY_POWDER_EXPLOSIVE",
          kind: "module",
          layout: "canonical",
          family_id: "technologies",
          family: "technology",
          object_id: "TECHNOLOGY_POWDER_EXPLOSIVE",
          module_id: "TECHNOLOGY_POWDER_EXPLOSIVE",
          title: "Powder Explosive",
          root: "/workspace/projects/PIHC3/src/modules/technology/TECHNOLOGY_POWDER_EXPLOSIVE",
          relative_root: "src/modules/technology/TECHNOLOGY_POWDER_EXPLOSIVE",
          source_count: 1,
          sources: [
            {
              slot: "icon",
              name: "icon.dds",
              path: "/workspace/projects/PIHC3/src/modules/technology/TECHNOLOGY_POWDER_EXPLOSIVE/icon.dds",
              relative_path: "src/modules/technology/TECHNOLOGY_POWDER_EXPLOSIVE/icon.dds",
              extension: ".dds"
            }
          ],
          metadata: {
            settings: {
              folder_position: { x: 2, y: 3 },
              path_target_ids: ["TECHNOLOGY_FIREARM_I"]
            }
          }
        },
        {
          id: "technology:TECHNOLOGY_FIREARM_I",
          kind: "module",
          layout: "canonical",
          family_id: "technologies",
          family: "technology",
          object_id: "TECHNOLOGY_FIREARM_I",
          module_id: "TECHNOLOGY_FIREARM_I",
          title: "Early Firearm I",
          root: "/workspace/projects/PIHC3/src/modules/technology/TECHNOLOGY_FIREARM_I",
          relative_root: "src/modules/technology/TECHNOLOGY_FIREARM_I",
          source_count: 1,
          sources: [],
          metadata: {
            settings: {
              folder: { position: { x: "4", y: "3" } },
              legacy_source_image: { path: "legacy/default.png" },
              dependency_ids: ["TECHNOLOGY_POWDER_EXPLOSIVE", "TECHNOLOGY_ANCIENT_RANGED_WEAPON"],
              path: { leads_to_tech: "TECHNOLOGY_FIREARM_II" }
            }
          }
        }
      ]),
      "technologies"
    );

    expect(document.gridSizePx).toBe(48);
    expect(document.nodes).toMatchObject([
      {
        id: "TECHNOLOGY_FIREARM_I",
        mode: "absolute",
        fixed: true,
        width: 1,
        height: 1,
        imageUrl: "src/modules/technology/TECHNOLOGY_FIREARM_I/legacy/default.png",
        x: 4,
        y: 3,
        title: "Early Firearm I"
      },
      {
        id: "TECHNOLOGY_POWDER_EXPLOSIVE",
        mode: "absolute",
        fixed: true,
        width: 1,
        height: 1,
        imageUrl: "/workspace/projects/PIHC3/src/modules/technology/TECHNOLOGY_POWDER_EXPLOSIVE/icon.png",
        x: 2,
        y: 3,
        title: "Powder Explosive"
      }
    ]);
    expect(document.edges).toEqual([
      {
        id: "dependency:TECHNOLOGY_POWDER_EXPLOSIVE->TECHNOLOGY_FIREARM_I",
        source: "TECHNOLOGY_POWDER_EXPLOSIVE",
        target: "TECHNOLOGY_FIREARM_I",
        kind: "dependency"
      }
    ]);
    expect(resolveDiagramLayout(document).nodesById.TECHNOLOGY_FIREARM_I.worldX).toBe(4);
  });

  it("uses PIHC3 root technology GUI pixels as fallback grid positions", () => {
    const document = buildProjectDiagramDocument(
      browserPayload([
        {
          id: "technology:TECHNOLOGY_ANCIENT_MELEE_WEAPON",
          kind: "module",
          layout: "canonical",
          family_id: "technologies",
          family: "technology",
          object_id: "TECHNOLOGY_ANCIENT_MELEE_WEAPON",
          module_id: "TECHNOLOGY_ANCIENT_MELEE_WEAPON",
          title: "Ancient Melee Weapon",
          root: "/workspace/projects/PIHC3/src/modules/technology/TECHNOLOGY_ANCIENT_MELEE_WEAPON",
          relative_root: "src/modules/technology/TECHNOLOGY_ANCIENT_MELEE_WEAPON",
          source_count: 1,
          sources: [],
          metadata: {
            settings: {
              legacy_root_gui: { is_root: true, root_x: 130, root_y: 200 },
              path_target_ids: ["TECHNOLOGY_ANCIENT_RANGED_WEAPON"]
            }
          }
        },
        {
          id: "technology:TECHNOLOGY_ANCIENT_RANGED_WEAPON",
          kind: "module",
          layout: "canonical",
          family_id: "technologies",
          family: "technology",
          object_id: "TECHNOLOGY_ANCIENT_RANGED_WEAPON",
          module_id: "TECHNOLOGY_ANCIENT_RANGED_WEAPON",
          title: "Ancient Ranged Weapon",
          root: "/workspace/projects/PIHC3/src/modules/technology/TECHNOLOGY_ANCIENT_RANGED_WEAPON",
          relative_root: "src/modules/technology/TECHNOLOGY_ANCIENT_RANGED_WEAPON",
          source_count: 1,
          sources: []
        }
      ]),
      "technologies"
    );

    expect(document.nodes).toEqual(
      expect.arrayContaining([
        expect.objectContaining({
          id: "TECHNOLOGY_ANCIENT_MELEE_WEAPON",
          mode: "absolute",
          fixed: true,
          width: 1,
          height: 1,
          x: 3,
          y: 4
        })
      ])
    );
    expect(document.edges).toEqual([
      {
        id: "dependency:TECHNOLOGY_ANCIENT_MELEE_WEAPON->TECHNOLOGY_ANCIENT_RANGED_WEAPON",
        source: "TECHNOLOGY_ANCIENT_MELEE_WEAPON",
        target: "TECHNOLOGY_ANCIENT_RANGED_WEAPON",
        kind: "dependency"
      }
    ]);
  });

  it("expands focus tree metadata into positioned focus nodes", () => {
    const document = buildProjectDiagramDocument(
      browserPayload([
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
                {
                  id: "FOCUS_C08_CANTERLOT_MIND",
                  image_url: "asset://focus-canterlot.png",
                  x: "12",
                  y: "0",
                  loc_keys: ["FOCUS_C08_CANTERLOT_MIND", "FOCUS_C08_CANTERLOT_MIND_desc"]
                },
                {
                  id: "FOCUS_C08_SECOND_SUMMIT",
                  x: "12",
                  y: "1",
                  prerequisites: ["FOCUS_C08_CANTERLOT_MIND"],
                  loc_keys: ["FOCUS_C08_SECOND_SUMMIT", "FOCUS_C08_SECOND_SUMMIT_desc"]
                },
                {
                  id: "FOCUS_C08_PLAN_STARLIGHT",
                  x: "12",
                  y: "3",
                  parent: "FOCUS_C08_SECOND_SUMMIT",
                  prerequisites: ["FOCUS_C08_SECOND_SUMMIT"],
                  mutually_exclusive: ["FOCUS_C08_PLAN_TWILIGHT"]
                }
              ]
            }
          }
        }
      ]),
      "focuses"
    );

    expect(document.gridSizePx).toBe(96);
    expect(document.nodes).toMatchObject([
      {
        id: "FOCUS_C08_CANTERLOT_MIND",
        mode: "absolute",
        fixed: true,
        width: 1,
        height: 1,
        imageUrl: "asset://focus-canterlot.png",
        x: 12,
        y: 0,
        title: "FOCUS C08 CANTERLOT MIND"
      },
      {
        id: "FOCUS_C08_SECOND_SUMMIT",
        parentId: "FOCUS_C08_CANTERLOT_MIND",
        mode: "absolute",
        fixed: true,
        width: 1,
        height: 1,
        x: 12,
        y: 1
      },
      {
        id: "FOCUS_C08_PLAN_STARLIGHT",
        parentId: "FOCUS_C08_SECOND_SUMMIT",
        mode: "absolute",
        fixed: true,
        width: 1,
        height: 1,
        x: 12,
        y: 3
      }
    ]);
    expect(document.edges).toEqual([
      {
        id: "dependency:FOCUS_C08_CANTERLOT_MIND->FOCUS_C08_SECOND_SUMMIT",
        source: "FOCUS_C08_CANTERLOT_MIND",
        target: "FOCUS_C08_SECOND_SUMMIT",
        kind: "dependency"
      },
      {
        id: "tree:FOCUS_C08_CANTERLOT_MIND->FOCUS_C08_SECOND_SUMMIT",
        source: "FOCUS_C08_CANTERLOT_MIND",
        target: "FOCUS_C08_SECOND_SUMMIT",
        kind: "tree"
      },
      {
        id: "dependency:FOCUS_C08_SECOND_SUMMIT->FOCUS_C08_PLAN_STARLIGHT",
        source: "FOCUS_C08_SECOND_SUMMIT",
        target: "FOCUS_C08_PLAN_STARLIGHT",
        kind: "dependency"
      },
      {
        id: "tree:FOCUS_C08_SECOND_SUMMIT->FOCUS_C08_PLAN_STARLIGHT",
        source: "FOCUS_C08_SECOND_SUMMIT",
        target: "FOCUS_C08_PLAN_STARLIGHT",
        kind: "tree"
      }
    ]);
    expect(resolveDiagramLayout(document).nodesById.FOCUS_C08_PLAN_STARLIGHT.worldY).toBe(3);
  });

  it("uses HOI4 focus coordinates as non-overlapping focus slots", () => {
    const document = buildProjectDiagramDocument(
      browserPayload([
        {
          id: "focus_tree:C08_MAIN",
          kind: "module",
          layout: "canonical",
          family_id: "focuses",
          family: "focus_tree",
          object_id: "C08_MAIN",
          module_id: "C08_MAIN",
          title: "C08 Main",
          root: "/workspace/projects/PIHC3/src/modules/focus_tree/C08_MAIN",
          relative_root: "src/modules/focus_tree/C08_MAIN",
          source_count: 1,
          sources: [],
          metadata: {
            settings: {
              focuses: [
                { id: "FOCUS_C08_ROOT", x: "7", y: "0" },
                { id: "FOCUS_C08_CHILD", x: "7", y: "1", prerequisites: ["FOCUS_C08_ROOT"] },
                { id: "FOCUS_C08_LEAF", x: "7", y: "2", prerequisites: ["FOCUS_C08_CHILD"] }
              ]
            }
          }
        }
      ]),
      "focuses"
    );

    expect(document.gridSizePx).toBe(96);
    expect(document.layoutOptions).toEqual({ layerGap: 0 });
    expect(document.nodes).toEqual(
      expect.arrayContaining([
        expect.objectContaining({ id: "FOCUS_C08_ROOT", height: 1, width: 1, x: 7, y: 0 }),
        expect.objectContaining({ id: "FOCUS_C08_CHILD", height: 1, width: 1, x: 7, y: 1 }),
        expect.objectContaining({ id: "FOCUS_C08_LEAF", height: 1, width: 1, x: 7, y: 2 })
      ])
    );
    const resolved = resolveDiagramLayout(document).nodesById;
    const rootBottom = (resolved.FOCUS_C08_ROOT.worldY + resolved.FOCUS_C08_ROOT.height) * document.gridSizePx;
    const childTop = resolved.FOCUS_C08_CHILD.worldY * document.gridSizePx;
    const childBottom = (resolved.FOCUS_C08_CHILD.worldY + resolved.FOCUS_C08_CHILD.height) * document.gridSizePx;
    const leafTop = resolved.FOCUS_C08_LEAF.worldY * document.gridSizePx;
    expect(rootBottom).toBeLessThanOrEqual(childTop);
    expect(childBottom).toBeLessThanOrEqual(leafTop);
  });

  it("uses module-owned PIHC3 focus previews with source-backed legacy focus offsets", () => {
    const document = buildProjectDiagramDocument(
      browserPayload([
        {
          id: "focus_tree:C01_DEM",
          kind: "module",
          layout: "canonical",
          family_id: "focuses",
          family: "focus_tree",
          object_id: "C01_DEM",
          module_id: "C01_DEM",
          title: "C01 Dem",
          root: "/workspace/projects/PIHC3/src/modules/focus_tree/C01_DEM",
          relative_root: "src/modules/focus_tree/C01_DEM",
          source_root: "/workspace/projects/PIHC3/src",
          source_root_relative_path: "src",
          source_count: 1,
          sources: [],
          metadata: {
            settings: {
              source_focuses: [
                {
                  focus_id: "FOCUS_C01_DEM_CHANGE_1",
                  icon_path: "C01_DEM_CHANGE_1/default.png",
                  preview_url: "src/modules/focus_tree/C01_DEM/icons/FOCUS_C01_DEM_CHANGE_1.png",
                  source_path: "C01_DEM_CHANGE_1"
                }
              ],
              focuses: [
                {
                  id: "FOCUS_C01_DEM_ROOT",
                  icon: "GFX_FOCUS_C01_DEM_ROOT_icon",
                  x: "4",
                  y: "2"
                },
                {
                  id: "FOCUS_C01_DEM_CHANGE_1",
                  parent: "FOCUS_C01_DEM_ROOT",
                  icon: "GFX_FOCUS_C01_DEM_CHANGE_1_icon",
                  dx: "2",
                  dy: "1",
                  priority: "10"
                }
              ]
            }
          }
        }
      ]),
      "focuses"
    );

    expect(document.nodes).toEqual(
      expect.arrayContaining([
        expect.objectContaining({
          id: "FOCUS_C01_DEM_CHANGE_1",
          parentId: "FOCUS_C01_DEM_ROOT",
          mode: "auto",
          relativePositionKind: "legacy_offset",
          dx: 2,
          dy: 1,
          width: 1,
          height: 1,
          imageUrl: "src/modules/focus_tree/C01_DEM/icons/FOCUS_C01_DEM_CHANGE_1.png",
          payload: expect.objectContaining({
            sourceFocusPath: "C01_DEM_CHANGE_1"
          })
        })
      ])
    );
    expect(resolveDiagramLayout(document).nodesById.FOCUS_C01_DEM_CHANGE_1.worldX).toBe(6);
    expect(resolveDiagramLayout(document).nodesById.FOCUS_C01_DEM_CHANGE_1.worldY).toBe(4);
  });

  it("ignores metadata preview aliases in favor of the canonical Focus-tree source slot", () => {
    const document = buildProjectDiagramDocument(
      browserPayload([
        {
          id: "focus_tree:C01_DEM",
          kind: "module",
          layout: "canonical",
          family_id: "focuses",
          family: "focus_tree",
          object_id: "C01_DEM",
          module_id: "C01_DEM",
          title: "C01 Dem",
          root: "/workspace/projects/PIHC3/src/modules/focus_tree/C01_DEM",
          relative_root: "src/modules/focus_tree/C01_DEM",
          source_count: 1,
          sources: [],
          metadata: {
            settings: {
              source_focuses: [
                {
                  focus_id: "FOCUS_C01_DEM_CHANGE_1",
                  preview_url: "asset://focus-c01-dem-change-1.png",
                  source_path: "C01_DEM_CHANGE_1"
                }
              ],
              focuses: [
                {
                  id: "FOCUS_C01_DEM_CHANGE_1",
                  icon: "GFX_FOCUS_C01_DEM_CHANGE_1_icon",
                  x: "4",
                  y: "2"
                }
              ]
            }
          }
        }
      ]),
      "focuses"
    );

    expect(document.nodes).toEqual(
      expect.arrayContaining([
        expect.objectContaining({
          id: "FOCUS_C01_DEM_CHANGE_1",
          imageUrl: "src/modules/focus_tree/C01_DEM/icons/FOCUS_C01_DEM_CHANGE_1.png"
        })
      ])
    );
  });

  it("keeps PIHC legacy focus dx and dy as auto-layout subtree nudges", () => {
    const document = buildProjectDiagramDocument(
      browserPayload([
        {
          id: "focus_tree:C08_MAIN",
          kind: "module",
          layout: "canonical",
          family_id: "focuses",
          family: "focus_tree",
          object_id: "C08_MAIN",
          module_id: "C08_MAIN",
          title: "C08 Main",
          root: "/workspace/projects/PIHC3/src/modules/focus_tree/C08_MAIN",
          relative_root: "src/modules/focus_tree/C08_MAIN",
          source_count: 1,
          sources: [],
          metadata: {
            settings: {
              focuses: [
                { id: "FOCUS_C08_ROOT", x: 10, y: 0 },
                { id: "FOCUS_C08_LEFT", parent: "FOCUS_C08_ROOT", dx: "-1", dy: "1", priority: "20" },
                { id: "FOCUS_C08_LEFT_CHILD", parent: "FOCUS_C08_LEFT" },
                { id: "FOCUS_C08_RIGHT", parent: "FOCUS_C08_ROOT" }
              ]
            }
          }
        }
      ]),
      "focuses"
    );

    expect(document.nodes).toEqual(
      expect.arrayContaining([
        expect.objectContaining({
          id: "FOCUS_C08_LEFT",
          parentId: "FOCUS_C08_ROOT",
          mode: "auto",
          dx: -1,
          dy: 1,
          priority: 20
        })
      ])
    );

    const resolved = resolveDiagramLayout(document).nodesById;
    expect(resolved.FOCUS_C08_LEFT).toMatchObject({ worldX: 8, worldY: 2 });
    expect(resolved.FOCUS_C08_LEFT_CHILD).toMatchObject({ worldX: 8, worldY: 3 });
    expect(resolved.FOCUS_C08_RIGHT).toMatchObject({ worldX: 11, worldY: 1 });
  });

  it("prefers PIHC3 source focus layout fields over compiled focus positions", () => {
    const document = buildProjectDiagramDocument(
      browserPayload([
        {
          id: "focus_tree:C01_DEM",
          kind: "module",
          layout: "canonical",
          family_id: "focuses",
          family: "focus_tree",
          object_id: "C01_DEM",
          module_id: "C01_DEM",
          title: "C01 Dem",
          root: "/workspace/projects/PIHC3/src/modules/focus_tree/C01_DEM",
          relative_root: "src/modules/focus_tree/C01_DEM",
          source_count: 1,
          sources: [],
          metadata: {
            settings: {
              source_focuses: [
                {
                  focus_id: "FOCUS_C01_DEM_CHANGE_1",
                  source_path: "C01_DEM_CHANGE_1",
                  icon_path: "C01_DEM_CHANGE_1/default.png",
                  parent: "FOCUS_C01_DEM_ROOT",
                  dx: "2",
                  dy: "1",
                  dw: "4",
                  dc: "-1",
                  priority: "10"
                }
              ],
              focuses: [
                {
                  id: "FOCUS_C01_DEM_ROOT",
                  icon: "GFX_FOCUS_C01_DEM_ROOT_icon",
                  x: "4",
                  y: "2"
                },
                {
                  id: "FOCUS_C01_DEM_CHANGE_1",
                  icon: "GFX_FOCUS_C01_DEM_CHANGE_1_icon",
                  x: "99",
                  y: "99"
                }
              ]
            }
          }
        }
      ]),
      "focuses"
    );

    expect(document.nodes).toEqual(
      expect.arrayContaining([
        expect.objectContaining({
          id: "FOCUS_C01_DEM_CHANGE_1",
          parentId: "FOCUS_C01_DEM_ROOT",
          mode: "auto",
          relativePositionKind: "legacy_offset",
          dx: 2,
          dy: 1,
          priority: 10,
          subtreeWidthDelta: 4,
          subtreeCenterOffset: -1,
          imageUrl: "src/modules/focus_tree/C01_DEM/icons/FOCUS_C01_DEM_CHANGE_1.png"
        })
      ])
    );
    expect(resolveDiagramLayout(document).nodesById.FOCUS_C01_DEM_CHANGE_1.worldX).toBe(7);
    expect(resolveDiagramLayout(document).nodesById.FOCUS_C01_DEM_CHANGE_1.worldY).toBe(4);
  });

  it("prefers PIHC3 source focus relationships over compiled focus relationships", () => {
    const document = buildProjectDiagramDocument(
      browserPayload([
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
              source_focuses: [
                { focus_id: "FOCUS_ROOT", source_path: "C08_ROOT", mutually_exclusive: ["FOCUS_OTHER"], x: "10", y: "0" },
                { focus_id: "FOCUS_CHILD", source_path: "C08_CHILD", prerequisite: "FOCUS_ROOT", dx: "1", dy: "1" }
              ],
              focuses: [
                { id: "FOCUS_ROOT", mutually_exclusive: ["FOCUS_OLD"], x: "10", y: "0" },
                { id: "FOCUS_CHILD", prerequisites: ["FOCUS_OLD"], x: "99", y: "99" },
                { id: "FOCUS_OLD", x: "12", y: "0" },
                { id: "FOCUS_OTHER", x: "14", y: "0" }
              ]
            }
          }
        }
      ]),
      "focuses"
    );

    expect(document.edges).toEqual([
      {
        id: "dependency:FOCUS_ROOT->FOCUS_CHILD",
        source: "FOCUS_ROOT",
        target: "FOCUS_CHILD",
        kind: "dependency"
      },
      {
        id: "tree:FOCUS_ROOT->FOCUS_CHILD",
        source: "FOCUS_ROOT",
        target: "FOCUS_CHILD",
        kind: "tree"
      },
      {
        id: "reference:FOCUS_ROOT->FOCUS_OTHER",
        source: "FOCUS_ROOT",
        target: "FOCUS_OTHER",
        kind: "reference"
      }
    ]);
  });

  it("uses canonical PIHC3 source focus relationship lists before legacy singular aliases", () => {
    const document = buildProjectDiagramDocument(
      browserPayload([
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
              source_focuses: [
                { focus_id: "FOCUS_OLD", source_path: "C08_OLD", x: "10", y: "0" },
                { focus_id: "FOCUS_NEW", source_path: "C08_NEW", x: "12", y: "0" },
                { focus_id: "FOCUS_CHILD", source_path: "C08_CHILD", prerequisite: "FOCUS_OLD", prerequisites: ["FOCUS_NEW"], dx: "1", dy: "1" }
              ],
              focuses: [
                { id: "FOCUS_OLD", x: "10", y: "0" },
                { id: "FOCUS_NEW", x: "12", y: "0" },
                { id: "FOCUS_CHILD", prerequisites: ["FOCUS_OLD"], x: "11", y: "1" }
              ]
            }
          }
        }
      ]),
      "focuses"
    );

    expect(document.edges).toEqual([
      {
        id: "dependency:FOCUS_NEW->FOCUS_CHILD",
        source: "FOCUS_NEW",
        target: "FOCUS_CHILD",
        kind: "dependency"
      },
      {
        id: "tree:FOCUS_NEW->FOCUS_CHILD",
        source: "FOCUS_NEW",
        target: "FOCUS_CHILD",
        kind: "tree"
      }
    ]);
  });

  it("uses canonical PIHC3 source focus prerequisites before dependency alias lists", () => {
    const document = buildProjectDiagramDocument(
      browserPayload([
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
              source_focuses: [
                { focus_id: "FOCUS_OLD", source_path: "C08_OLD", x: "10", y: "0" },
                { focus_id: "FOCUS_NEW", source_path: "C08_NEW", x: "12", y: "0" },
                { focus_id: "FOCUS_CHILD", source_path: "C08_CHILD", dependency_ids: ["FOCUS_OLD"], prerequisites: ["FOCUS_NEW"], dx: "1", dy: "1" }
              ],
              focuses: [
                { id: "FOCUS_OLD", x: "10", y: "0" },
                { id: "FOCUS_NEW", x: "12", y: "0" },
                { id: "FOCUS_CHILD", prerequisites: ["FOCUS_OLD"], x: "11", y: "1" }
              ]
            }
          }
        }
      ]),
      "focuses"
    );

    expect(document.edges).toEqual([
      {
        id: "dependency:FOCUS_NEW->FOCUS_CHILD",
        source: "FOCUS_NEW",
        target: "FOCUS_CHILD",
        kind: "dependency"
      },
      {
        id: "tree:FOCUS_NEW->FOCUS_CHILD",
        source: "FOCUS_NEW",
        target: "FOCUS_CHILD",
        kind: "tree"
      }
    ]);
  });

  it("keeps source-backed focuses with explicit null parent as roots even when prerequisites exist", () => {
    const document = buildProjectDiagramDocument(
      browserPayload([
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
              source_focuses: [
                {
                  focus_id: "FOCUS_C08_THE_RISING_FIRE",
                  parent: null,
                  source_path: "C08_THE_RISING_FIRE",
                  x: 3,
                  y: 5
                }
              ],
              focuses: [
                { id: "FOCUS_C08_CANTERLOT_MIND", x: 9, y: 0 },
                {
                  id: "FOCUS_C08_THE_RISING_FIRE",
                  prerequisites: ["FOCUS_C08_CANTERLOT_MIND"]
                }
              ]
            }
          }
        }
      ]),
      "focuses"
    );

    const rootNode = document.nodes.find((node) => node.id === "FOCUS_C08_THE_RISING_FIRE");
    expect(rootNode).toMatchObject({
      id: "FOCUS_C08_THE_RISING_FIRE",
      mode: "absolute",
      fixed: true,
      x: 4,
      y: 5
    });
    expect(rootNode?.parentId).toBeUndefined();
    expect(document.edges).toContainEqual({
      id: "dependency:FOCUS_C08_CANTERLOT_MIND->FOCUS_C08_THE_RISING_FIRE",
      source: "FOCUS_C08_CANTERLOT_MIND",
      target: "FOCUS_C08_THE_RISING_FIRE",
      kind: "dependency"
    });
    expect(document.edges).not.toContainEqual({
      id: "tree:FOCUS_C08_CANTERLOT_MIND->FOCUS_C08_THE_RISING_FIRE",
      source: "FOCUS_C08_CANTERLOT_MIND",
      target: "FOCUS_C08_THE_RISING_FIRE",
      kind: "tree"
    });
  });

  it("preserves PIHC focus priority, subtree hints, and partial legacy offsets", () => {
    const document = buildProjectDiagramDocument(
      browserPayload([
        {
          id: "focus_tree:C08_MAIN",
          kind: "module",
          layout: "canonical",
          family_id: "focuses",
          family: "focus_tree",
          object_id: "C08_MAIN",
          module_id: "C08_MAIN",
          title: "C08 Main",
          root: "/workspace/projects/PIHC3/src/modules/focus_tree/C08_MAIN",
          relative_root: "src/modules/focus_tree/C08_MAIN",
          source_count: 1,
          sources: [],
          metadata: {
            settings: {
              focuses: [
                { id: "FOCUS_C08_ROOT", x: 0, y: 0, dc: "1", w: "12" },
                { id: "FOCUS_C08_LOW", parent: "FOCUS_C08_ROOT", priority: "0" },
                { id: "FOCUS_C08_HIGH", parent: "FOCUS_C08_ROOT", priority: "20", w: "8" },
                { id: "FOCUS_C08_DX_ONLY", parent: "FOCUS_C08_ROOT", dx: "2" },
                { id: "FOCUS_C08_CY_ONLY", parent: "FOCUS_C08_ROOT", cy: "1" }
              ]
            }
          }
        }
      ]),
      "focuses"
    );

    expect(document.nodes).toEqual(
      expect.arrayContaining([
        expect.objectContaining({
          id: "FOCUS_C08_ROOT",
          mode: "absolute",
          fixed: true,
          x: 0,
          y: 0,
          subtreeCenterOffset: 1,
          subtreeWidth: 12
        }),
        expect.objectContaining({
          id: "FOCUS_C08_HIGH",
          parentId: "FOCUS_C08_ROOT",
          mode: "auto",
          priority: 20,
          subtreeWidth: 8
        }),
        expect.objectContaining({
          id: "FOCUS_C08_DX_ONLY",
          parentId: "FOCUS_C08_ROOT",
          mode: "auto",
          relativePositionKind: "legacy_offset",
          dx: 2,
          dy: 0
        }),
        expect.objectContaining({
          id: "FOCUS_C08_CY_ONLY",
          parentId: "FOCUS_C08_ROOT",
          mode: "auto",
          relativePositionKind: "legacy_offset",
          dx: 0,
          dy: 1
        })
      ])
    );

    const resolved = resolveDiagramLayout(document).nodesById;
    expect(resolved.FOCUS_C08_HIGH.worldX).toBeLessThan(resolved.FOCUS_C08_LOW.worldX);
    expect(resolved.FOCUS_C08_DX_ONLY).toMatchObject({ worldX: 7, worldY: 1 });
    expect(resolved.FOCUS_C08_CY_ONLY).toMatchObject({ worldX: 7, worldY: 2 });
  });

  it("derives the canonical PIHC3 Focus-tree preview when source icon metadata is missing", () => {
    const document = buildProjectDiagramDocument(
      browserPayload([
        {
          id: "focus_tree:C01_MAIN",
          kind: "module",
          layout: "canonical",
          family_id: "focuses",
          family: "focus_tree",
          object_id: "C01_MAIN",
          module_id: "C01_MAIN",
          title: "C01 Main",
          root: "/workspace/projects/PIHC3/src/modules/focus_tree/C01_MAIN",
          relative_root: "src/modules/focus_tree/C01_MAIN",
          source_count: 1,
          sources: [],
          metadata: {
            settings: {
              focuses: [
                {
                  id: "FOCUS_C01_OUTSOURCING_INFRASTRUCTURE",
                  icon: "GFX_FOCUS_C01_OUTSOURCING_INFRASTRUCTURE_icon",
                  x: "1",
                  y: "0"
                }
              ]
            }
          }
        }
      ]),
      "focuses"
    );

    expect(document.nodes).toEqual(
      expect.arrayContaining([
        expect.objectContaining({
          id: "FOCUS_C01_OUTSOURCING_INFRASTRUCTURE",
          imageUrl: "src/modules/focus_tree/C01_MAIN/icons/FOCUS_C01_OUTSOURCING_INFRASTRUCTURE.png"
        })
      ])
    );
  });

  it("builds a larger PIHC3 source-backed focus tree with migrated preview icons", () => {
    const document = buildProjectDiagramDocument(
      browserPayload([
        {
          id: "focus_tree:C08_MAIN",
          kind: "module",
          layout: "canonical",
          family_id: "focuses",
          family: "focus_tree",
          object_id: "C08_MAIN",
          module_id: "C08_MAIN",
          title: "C08 Main",
          root: "/workspace/projects/PIHC3/src/modules/focus_tree/C08_MAIN",
          relative_root: "src/modules/focus_tree/C08_MAIN",
          source_count: 1,
          sources: [],
          metadata: {
            settings: {
              source_focuses: [
                { focus_id: "FOCUS_C08_CANTERLOT_PACT", source_path: "C08_CANTERLOT_PACT", icon_path: "C08_CANTERLOT_PACT/default.png" },
                { focus_id: "FOCUS_C08_UPRISE", source_path: "C08_UPRISE", icon_path: "C08_UPRISE/default.png" },
                { focus_id: "FOCUS_C08_SPARKING_FIRE", source_path: "C08_SPARKING_FIRE", icon_path: "C08_SPARKING_FIRE/default.png" },
                { focus_id: "FOCUS_C08_CONTACT_COMRADES", source_path: "C08_CONTACT_COMRADES", icon_path: "C08_CONTACT_COMRADES/default.png" },
                { focus_id: "FOCUS_C08_THE_SITUATION", source_path: "C08_THE_SITUATION", icon_path: "C08_THE_SITUATION/default.png" },
                { focus_id: "FOCUS_C08_ANOTHER_YEAR", source_path: "C08_ANOTHER_YEAR", icon_path: "C08_ANOTHER_YEAR/default.png" }
              ],
              focuses: [
                { id: "FOCUS_C08_CANTERLOT_PACT", icon: "GFX_FOCUS_C08_CANTERLOT_PACT_icon", x: "7", y: "0" },
                { id: "FOCUS_C08_UPRISE", icon: "GFX_FOCUS_C08_UPRISE_icon", x: "7", y: "1", prerequisites: ["FOCUS_C08_CANTERLOT_PACT"] },
                { id: "FOCUS_C08_SPARKING_FIRE", icon: "GFX_FOCUS_C08_SPARKING_FIRE_icon", x: "7", y: "2", prerequisites: ["FOCUS_C08_UPRISE"] },
                { id: "FOCUS_C08_CONTACT_COMRADES", icon: "GFX_FOCUS_C08_CONTACT_COMRADES_icon", x: "6", y: "3", prerequisites: ["FOCUS_C08_SPARKING_FIRE"] },
                { id: "FOCUS_C08_THE_SITUATION", icon: "GFX_FOCUS_C08_THE_SITUATION_icon", x: "8", y: "3", prerequisites: ["FOCUS_C08_SPARKING_FIRE"] },
                {
                  id: "FOCUS_C08_ANOTHER_YEAR",
                  icon: "GFX_FOCUS_C08_ANOTHER_YEAR_icon",
                  x: "7",
                  y: "4",
                  prerequisites: ["FOCUS_C08_THE_SITUATION", "FOCUS_C08_CONTACT_COMRADES"]
                }
              ]
            }
          }
        }
      ]),
      "focuses"
    );

    expect(document.nodes).toHaveLength(6);
    expect(document.gridSizePx).toBe(96);
    expect(document.nodes.every((node) => node.width === 1 && node.height === 1)).toBe(true);
    expect(document.nodes.map((node) => node.imageUrl)).toEqual([
      "src/modules/focus_tree/C08_MAIN/icons/FOCUS_C08_CANTERLOT_PACT.png",
      "src/modules/focus_tree/C08_MAIN/icons/FOCUS_C08_UPRISE.png",
      "src/modules/focus_tree/C08_MAIN/icons/FOCUS_C08_SPARKING_FIRE.png",
      "src/modules/focus_tree/C08_MAIN/icons/FOCUS_C08_CONTACT_COMRADES.png",
      "src/modules/focus_tree/C08_MAIN/icons/FOCUS_C08_THE_SITUATION.png",
      "src/modules/focus_tree/C08_MAIN/icons/FOCUS_C08_ANOTHER_YEAR.png"
    ]);
    expect(document.nodes.some((node) => node.imageUrl?.includes("/legacy/focuses/") || node.imageUrl?.endsWith("/default.png"))).toBe(false);
    expect(document.edges).toEqual(
      expect.arrayContaining([
        { id: "dependency:FOCUS_C08_CANTERLOT_PACT->FOCUS_C08_UPRISE", source: "FOCUS_C08_CANTERLOT_PACT", target: "FOCUS_C08_UPRISE", kind: "dependency" },
        { id: "dependency:FOCUS_C08_SPARKING_FIRE->FOCUS_C08_CONTACT_COMRADES", source: "FOCUS_C08_SPARKING_FIRE", target: "FOCUS_C08_CONTACT_COMRADES", kind: "dependency" },
        { id: "dependency:FOCUS_C08_THE_SITUATION->FOCUS_C08_ANOTHER_YEAR", source: "FOCUS_C08_THE_SITUATION", target: "FOCUS_C08_ANOTHER_YEAR", kind: "dependency" },
        { id: "tree:FOCUS_C08_CANTERLOT_PACT->FOCUS_C08_UPRISE", source: "FOCUS_C08_CANTERLOT_PACT", target: "FOCUS_C08_UPRISE", kind: "tree" },
        { id: "tree:FOCUS_C08_THE_SITUATION->FOCUS_C08_ANOTHER_YEAR", source: "FOCUS_C08_THE_SITUATION", target: "FOCUS_C08_ANOTHER_YEAR", kind: "tree" }
      ])
    );
    expect(resolveDiagramLayout(document).nodesById.FOCUS_C08_ANOTHER_YEAR).toMatchObject({ worldX: 7, worldY: 4 });
  });

  it("uses canonical source Focus ids for preview paths when compiled ids contain punctuation", () => {
    const document = buildProjectDiagramDocument(
      browserPayload([
        {
          id: "focus_tree:C12_MAIN",
          kind: "module",
          layout: "canonical",
          family_id: "focuses",
          family: "focus_tree",
          object_id: "C12_MAIN",
          module_id: "C12_MAIN",
          title: "C12 Main",
          root: "/workspace/projects/PIHC3/src/modules/focus_tree/C12_MAIN",
          relative_root: "src/modules/focus_tree/C12_MAIN",
          source_count: 1,
          sources: [],
          metadata: {
            settings: {
              source_focuses: [
                {
                  focus_id: "FOCUS_C12_PINK_ISN_T_FARM_S_COLOR",
                  source_path: "C12_PINK_ISN'T_FARM'S_COLOR",
                  icon_path: "C12_PINK_ISN'T_FARM'S_COLOR/default.png",
                  relative_position_id: "FOCUS_C12_ROCKFARM_DOMINION",
                  x: "1",
                  y: "2"
                },
                {
                  focus_id: "FOCUS_C12_HOLDER_S_BOULDER_PARADE",
                  source_path: "C12_HOLDER'S_BOULDER_PARADE",
                  icon_path: "C12_HOLDER'S_BOULDER_PARADE/default.png"
                }
              ],
              focuses: [
                {
                  id: "FOCUS_C12_ROCKFARM_DOMINION",
                  icon: "GFX_FOCUS_C12_ROCKFARM_DOMINION_icon",
                  x: "4",
                  y: "7"
                },
                {
                  id: "FOCUS_C12_PINK_ISN'T_FARM'S_COLOR",
                  icon: "GFX_FOCUS_C12_PINK_ISN'T_FARM'S_COLOR_icon",
                  x: "99",
                  y: "99"
                },
                {
                  id: "FOCUS_C12_HOLDER'S_BOULDER_PARADE",
                  icon: "GFX_FOCUS_C12_HOLDER'S_BOULDER_PARADE_icon",
                  x: "8",
                  y: "9"
                }
              ]
            }
          }
        }
      ]),
      "focuses"
    );

    expect(document.nodes).toEqual(
      expect.arrayContaining([
        expect.objectContaining({
          id: "FOCUS_C12_PINK_ISN'T_FARM'S_COLOR",
          imageUrl: "src/modules/focus_tree/C12_MAIN/icons/FOCUS_C12_PINK_ISN_T_FARM_S_COLOR.png",
          parentId: "FOCUS_C12_ROCKFARM_DOMINION",
          mode: "relative",
          dx: 1,
          dy: 2
        }),
        expect.objectContaining({
          id: "FOCUS_C12_HOLDER'S_BOULDER_PARADE",
          imageUrl: "src/modules/focus_tree/C12_MAIN/icons/FOCUS_C12_HOLDER_S_BOULDER_PARADE.png"
        })
      ])
    );
    expect(resolveDiagramLayout(document).nodesById["FOCUS_C12_PINK_ISN'T_FARM'S_COLOR"]).toMatchObject({ worldX: 5, worldY: 9 });
  });

  it("adds reference edges for PIHC3 focus mutual-exclusion metadata without changing tree parents", () => {
    const document = buildProjectDiagramDocument(
      browserPayload([
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
                { id: "FOCUS_C08_ROOT", x: 12, y: 0 },
                {
                  id: "FOCUS_C08_PLAN_STARLIGHT",
                  x: 11,
                  y: 1,
                  prerequisites: [{ focus: "FOCUS_C08_ROOT" }],
                  mutually_exclusive: [{ focus: "FOCUS_C08_PLAN_TWILIGHT" }]
                },
                {
                  id: "FOCUS_C08_PLAN_TWILIGHT",
                  x: 13,
                  y: 1,
                  prerequisites: [{ focus: "FOCUS_C08_ROOT" }]
                }
              ]
            }
          }
        }
      ]),
      "focuses"
    );

    expect(document.nodes).toEqual(
      expect.arrayContaining([
        expect.objectContaining({ id: "FOCUS_C08_PLAN_STARLIGHT", parentId: "FOCUS_C08_ROOT" }),
        expect.objectContaining({ id: "FOCUS_C08_PLAN_TWILIGHT", parentId: "FOCUS_C08_ROOT" }),
        expect.objectContaining({ id: "FOCUS_C08_ROOT" })
      ])
    );
    expect(document.edges).toEqual(
      expect.arrayContaining([
        {
          id: "reference:FOCUS_C08_PLAN_STARLIGHT->FOCUS_C08_PLAN_TWILIGHT",
          source: "FOCUS_C08_PLAN_STARLIGHT",
          target: "FOCUS_C08_PLAN_TWILIGHT",
          kind: "reference"
        }
      ])
    );
    expect(document.edges.filter((edge) => edge.kind === "reference")).toHaveLength(1);
  });

  it("uses PIHC3 focus relative positions as visual tree parents", () => {
    const document = buildProjectDiagramDocument(
      browserPayload([
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
                { id: "FOCUS_C08_ROOT", x: 10, y: 0 },
                {
                  id: "FOCUS_C08_VISUAL_CHILD",
                  relative_position_id: "FOCUS_C08_ROOT",
                  x: 1,
                  y: 1
                }
              ]
            }
          }
        }
      ]),
      "focuses"
    );

    expect(document.nodes).toEqual(
      expect.arrayContaining([
        expect.objectContaining({ id: "FOCUS_C08_ROOT" }),
        expect.objectContaining({ id: "FOCUS_C08_VISUAL_CHILD", parentId: "FOCUS_C08_ROOT", mode: "relative", dx: 1, dy: 1 })
      ])
    );
    expect(document.edges).toEqual([
      {
        id: "tree:FOCUS_C08_ROOT->FOCUS_C08_VISUAL_CHILD",
        source: "FOCUS_C08_ROOT",
        target: "FOCUS_C08_VISUAL_CHILD",
        kind: "tree"
      }
    ]);
    expect(resolveDiagramLayout(document).nodesById.FOCUS_C08_VISUAL_CHILD.worldX).toBe(11);
    expect(resolveDiagramLayout(document).nodesById.FOCUS_C08_VISUAL_CHILD.worldY).toBe(1);
  });

  it("uses PIHC3 source focus relative positions as visual tree parents", () => {
    const document = buildProjectDiagramDocument(
      browserPayload([
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
              source_focuses: [
                {
                  focus_id: "FOCUS_C08_VISUAL_CHILD",
                  source_path: "C08_VISUAL_CHILD",
                  relative_position_id: "FOCUS_C08_ROOT",
                  x: "3",
                  y: "2"
                }
              ],
              focuses: [
                { id: "FOCUS_C08_ROOT", x: "10", y: "0" },
                { id: "FOCUS_C08_VISUAL_CHILD", x: "99", y: "99" }
              ]
            }
          }
        }
      ]),
      "focuses"
    );

    expect(document.nodes).toEqual(
      expect.arrayContaining([
        expect.objectContaining({ id: "FOCUS_C08_ROOT" }),
        expect.objectContaining({ id: "FOCUS_C08_VISUAL_CHILD", parentId: "FOCUS_C08_ROOT", mode: "relative", dx: 3, dy: 2 })
      ])
    );
    expect(resolveDiagramLayout(document).nodesById.FOCUS_C08_VISUAL_CHILD.worldX).toBe(13);
    expect(resolveDiagramLayout(document).nodesById.FOCUS_C08_VISUAL_CHILD.worldY).toBe(2);
  });

  it("packs related unpositioned browser rows without referencing missing parents", () => {
    const document = buildProjectDiagramDocument(
      browserPayload([
        {
          id: "technology:TECH_PARENT",
          kind: "module",
          layout: "canonical",
          family_id: "technologies",
          family: "technology",
          object_id: "TECH_PARENT",
          title: "Parent Tech",
          root: "/workspace/projects/PIHC3/src/modules/technology/TECH_PARENT",
          relative_root: "src/modules/technology/TECH_PARENT",
          source_count: 1,
          sources: []
        },
        {
          id: "technology:TECH_CHILD",
          kind: "module",
          layout: "canonical",
          family_id: "technologies",
          family: "technology",
          object_id: "TECH_CHILD",
          title: "Child Tech",
          root: "/workspace/projects/PIHC3/src/modules/technology/TECH_CHILD",
          relative_root: "src/modules/technology/TECH_CHILD",
          source_count: 1,
          sources: [],
          metadata: {
            settings: {
              parent: "TECH_PARENT",
              dependency_ids: ["TECH_PARENT", "UNKNOWN_TECH"]
            }
          }
        }
      ]),
      "technologies"
    );

    expect(document.nodes).toMatchObject([
      { id: "TECH_CHILD", parentId: "TECH_PARENT", mode: "auto" },
      { id: "TECH_PARENT", mode: "auto" }
    ]);
    expect(document.edges).toEqual([
      {
        id: "dependency:TECH_PARENT->TECH_CHILD",
        source: "TECH_PARENT",
        target: "TECH_CHILD",
        kind: "dependency"
      },
      {
        id: "tree:TECH_PARENT->TECH_CHILD",
        source: "TECH_PARENT",
        target: "TECH_CHILD",
        kind: "tree"
      }
    ]);
    expect(resolveDiagramLayout(document).nodesById.TECH_CHILD.worldY).toBeGreaterThan(0);
  });
});
