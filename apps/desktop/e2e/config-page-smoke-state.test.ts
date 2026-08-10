import { describe, expect, it } from "vitest";
import { configPageSmokeConfigChecked, configPageSmokeConfigValue, configPageSmokeHasConfigKey, writeConfigPageSmokeDataset } from "./config-page-smoke-state";

describe("config page smoke state", () => {
  it("records visible Settings controls and selected values as dataset fields", () => {
    const root = { dataset: {} as Record<string, string> };

    writeConfigPageSmokeDataset(root, {
      activeTab: "config-projects",
      aiExplainSelectedSources: "project,selection",
      aiExplainTemplatesSelected: false,
      aiExplainToggleCount: 5,
      aiExplainProjectIndexSelected: false,
      aiLastSavedProfileId: "explain",
      aiLastSavedSourceKinds: "project,selection,templates",
      aiExplainSaveDisabled: true,
      aiProfileSourceLabels: "Project,Selection,Diagnostics,Templates,Project index",
      aiProfileSourceKinds: "project,selection,diagnostics,templates,project-index",
      buildParallelismValue: "4",
      buildStrictMetadataChecked: true,
      cliOutputValue: "json",
      configPanelCount: 2,
      hasBuildParallelismKey: true,
      hasBuildStrictMetadataKey: true,
      hasCliOutputKey: true,
      lastConfigWriteCount: 1,
      lastConfigWriteKey: "paradev.cli.output",
      lastConfigWriteValue: "yaml",
      projectName: "The Pony In The High Castle",
      settingsRailSelected: true
    });

    expect(root.dataset.paradevConfigPageSmokeActiveTab).toBe("config-projects");
    expect(root.dataset.paradevConfigPageSmokeSettingsRailSelected).toBe("1");
    expect(root.dataset.paradevConfigPageSmokeProjectName).toBe("The Pony In The High Castle");
    expect(root.dataset.paradevConfigPageSmokePanelCount).toBe("2");
    expect(root.dataset.paradevConfigPageSmokeHasCliOutputKey).toBe("1");
    expect(root.dataset.paradevConfigPageSmokeCliOutputValue).toBe("json");
    expect(root.dataset.paradevConfigPageSmokeHasBuildParallelismKey).toBe("1");
    expect(root.dataset.paradevConfigPageSmokeBuildParallelismValue).toBe("4");
    expect(root.dataset.paradevConfigPageSmokeHasBuildStrictMetadataKey).toBe("1");
    expect(root.dataset.paradevConfigPageSmokeBuildStrictMetadataChecked).toBe("1");
    expect(root.dataset.paradevConfigPageSmokeLastConfigWriteCount).toBe("1");
    expect(root.dataset.paradevConfigPageSmokeLastConfigWriteKey).toBe("paradev.cli.output");
    expect(root.dataset.paradevConfigPageSmokeLastConfigWriteValue).toBe("yaml");
    expect(root.dataset.paradevConfigPageSmokeAiProfileSourceKinds).toBe("project,selection,diagnostics,templates,project-index");
    expect(root.dataset.paradevConfigPageSmokeAiExplainSelectedSources).toBe("project,selection");
    expect(root.dataset.paradevConfigPageSmokeAiExplainTemplatesSelected).toBe("0");
    expect(root.dataset.paradevConfigPageSmokeAiExplainProjectIndexSelected).toBe("0");
    expect(root.dataset.paradevConfigPageSmokeAiExplainToggleCount).toBe("5");
    expect(root.dataset.paradevConfigPageSmokeAiLastSavedProfileId).toBe("explain");
    expect(root.dataset.paradevConfigPageSmokeAiLastSavedSourceKinds).toBe("project,selection,templates");
    expect(root.dataset.paradevConfigPageSmokeAiExplainSaveDisabled).toBe("1");
    expect(root.dataset.paradevConfigPageSmokeAiProfileSourceLabels).toBe("Project,Selection,Diagnostics,Templates,Project index");
  });

  it("detects SDK config controls from machine-readable key attributes", () => {
    const root = {
      querySelector: (selector: string) => (selector === '[data-paradev-config-key="paradev.cli.output"]' ? {} : null)
    };

    expect(configPageSmokeHasConfigKey(root, "paradev.cli.output")).toBe(true);
    expect(configPageSmokeHasConfigKey(root, "paradev.build.parallelism")).toBe(false);
  });

  it("reads SDK config control values from machine-readable key attributes", () => {
    const root = {
      querySelector: (selector: string) => (selector === '[data-paradev-config-key="paradev.cli.output"]' ? { value: "yaml" } : null)
    };

    expect(configPageSmokeConfigValue(root, "paradev.cli.output", "json")).toBe("yaml");
    expect(configPageSmokeConfigValue(root, "paradev.build.parallelism", "4")).toBe("4");
  });

  it("reads SDK boolean config control checked state from machine-readable key attributes", () => {
    const root = {
      querySelector: (selector: string) => (selector === '[data-paradev-config-key="paradev.build.strict_metadata"]' ? { checked: true } : null)
    };

    expect(configPageSmokeConfigChecked(root, "paradev.build.strict_metadata", false)).toBe(true);
    expect(configPageSmokeConfigChecked(root, "paradev.build.parallelism", true)).toBe(true);
  });
});
