import { describe, expect, it } from "vitest";
import { writeDiagramTabSmokeApplyDataset, writeDiagramTabSmokeHitTargetDataset, writeDiagramTabSmokePopupDataset, writeDiagramTabSmokeSelectedNodeDataset, writeDiagramTabSmokeSourceDataset } from "./diagram-tab-smoke-state";

describe("diagram tab smoke state", () => {
  it("records opened focus node popup state as machine-readable dataset fields", () => {
    const root = { dataset: {} as Record<string, string> };

    writeDiagramTabSmokePopupDataset(root, {
      ariaLabel: "Opened node info",
      count: 1,
      nodeId: "FOCUS_C01_DEM_CHANGE",
      openModuleText: "Open module item",
      selectedNodeId: "FOCUS_C01_DEM_CHANGE",
      sourceInfoPath: "src/modules/focus_tree/C01_MAIN/legacy/C01_DEM_CHANGE/info.json",
      title: "FOCUS C01 DEM CHANGE"
    });

    expect(root.dataset.paradevDiagramTabSmokePopupCount).toBe("1");
    expect(root.dataset.paradevDiagramTabSmokePopupAria).toBe("Opened node info");
    expect(root.dataset.paradevDiagramTabSmokePopupNodeId).toBe("FOCUS_C01_DEM_CHANGE");
    expect(root.dataset.paradevDiagramTabSmokePopupOpenModuleText).toBe("Open module item");
    expect(root.dataset.paradevDiagramTabSmokePopupTitle).toBe("FOCUS C01 DEM CHANGE");
    expect(root.dataset.paradevDiagramTabSmokePopupSourceInfoPath).toBe("src/modules/focus_tree/C01_MAIN/legacy/C01_DEM_CHANGE/info.json");
    expect(root.dataset.paradevDiagramTabSmokePopupSelectedMatch).toBe("1");
  });

  it("records selected focus node mode and visible mode switch state", () => {
    const root = { dataset: {} as Record<string, string> };

    writeDiagramTabSmokeSelectedNodeDataset(root, {
      mode: "relative",
      nodeId: "FOCUS_C01_COZY_GLOW_CORONATION",
      switchCount: 1,
      switchMode: "relative"
    });

    expect(root.dataset.paradevDiagramTabSmokeSelectedNodeId).toBe("FOCUS_C01_COZY_GLOW_CORONATION");
    expect(root.dataset.paradevDiagramTabSmokeSelectedNodeMode).toBe("relative");
    expect(root.dataset.paradevDiagramTabSmokeModeSwitchCount).toBe("1");
    expect(root.dataset.paradevDiagramTabSmokeModeSwitchMode).toBe("relative");
    expect(root.dataset.paradevDiagramTabSmokeModeSwitchSelectedMatch).toBe("1");
  });

  it("records diagram apply review state for source-backed mode edits", () => {
    const root = { dataset: {} as Record<string, string> };

    writeDiagramTabSmokeApplyDataset(root, {
      applyButtonDisabled: false,
      applyButtonText: "Review scope first",
      applyPreviewText: "Will write 1 · Skip 0",
      dirtySummaryText: "Source changes: 1 · Ready 1 · Skipped 0",
      reviewPanelCount: 1
    });

    expect(root.dataset.paradevDiagramTabSmokeApplyButtonDisabled).toBe("0");
    expect(root.dataset.paradevDiagramTabSmokeApplyButtonText).toBe("Review scope first");
    expect(root.dataset.paradevDiagramTabSmokeApplyPreviewText).toBe("Will write 1 · Skip 0");
    expect(root.dataset.paradevDiagramTabSmokeDirtySummaryText).toBe("Source changes: 1 · Ready 1 · Skipped 0");
    expect(root.dataset.paradevDiagramTabSmokeApplyReviewCount).toBe("1");
  });

  it("records opened module source picker state after a diagram popup handoff", () => {
    const root = { dataset: {} as Record<string, string> };

    writeDiagramTabSmokeSourceDataset(root, {
      pickerCount: 1,
      pickerOptionCount: 85,
      pickerPath: "src/modules/focus_tree/C01_MAIN/legacy/C01_DEM_CHANGE/info.json",
      pickerText: "FOCUS_C01_DEM_CHANGE info",
      pickerValue: "focus:FOCUS_C01_DEM_CHANGE:info",
      sourceTabCount: 2,
      textPanelVisible: true
    });

    expect(root.dataset.paradevDiagramTabSmokeSourcePickerCount).toBe("1");
    expect(root.dataset.paradevDiagramTabSmokeSourcePickerOptionCount).toBe("85");
    expect(root.dataset.paradevDiagramTabSmokeSourcePickerValue).toBe("focus:FOCUS_C01_DEM_CHANGE:info");
    expect(root.dataset.paradevDiagramTabSmokeSourcePickerText).toBe("FOCUS_C01_DEM_CHANGE info");
    expect(root.dataset.paradevDiagramTabSmokeSourcePickerPath).toBe("src/modules/focus_tree/C01_MAIN/legacy/C01_DEM_CHANGE/info.json");
    expect(root.dataset.paradevDiagramTabSmokeSourceTabCount).toBe("2");
    expect(root.dataset.paradevDiagramTabSmokeSourceTextPanel).toBe("1");
  });

  it("records diagram node hit-target health for browser popup smoke", () => {
    const root = { dataset: {} as Record<string, string> };

    writeDiagramTabSmokeHitTargetDataset(root, {
      c01HitTargetCount: 83,
      c01NodeCount: 83,
      targetCount: 1,
      targetId: "FOCUS_C01_DEM_CHANGE"
    });

    expect(root.dataset.paradevDiagramTabSmokeC01HitTargetCount).toBe("83");
    expect(root.dataset.paradevDiagramTabSmokeHitTargetNodeMatch).toBe("1");
    expect(root.dataset.paradevDiagramTabSmokeHitTargetTargetId).toBe("FOCUS_C01_DEM_CHANGE");
    expect(root.dataset.paradevDiagramTabSmokeHitTargetTargetCount).toBe("1");
    expect(root.dataset.paradevDiagramTabSmokeHitTargetTargetReady).toBe("1");
  });
});
