export type ConfigPageSmokeState = {
  activeTab: string;
  aiExplainSelectedSources?: string;
  aiExplainProjectIndexSelected?: boolean;
  aiExplainSaveDisabled?: boolean;
  aiExplainTemplatesSelected?: boolean;
  aiExplainToggleCount?: number;
  aiLastSavedProfileId?: string;
  aiLastSavedSourceKinds?: string;
  aiProfileSourceLabels?: string;
  aiProfileSourceKinds?: string;
  buildParallelismValue: string;
  buildStrictMetadataChecked: boolean;
  cliOutputValue: string;
  configPanelCount: number;
  hasBuildParallelismKey: boolean;
  hasBuildStrictMetadataKey: boolean;
  hasCliOutputKey: boolean;
  lastConfigWriteCount?: number;
  lastConfigWriteKey?: string;
  lastConfigWriteValue?: string;
  projectName: string;
  settingsRailSelected: boolean;
};

type DatasetRoot = {
  dataset: Record<string, string>;
};

type ConfigKeyRoot = {
  querySelector: (selector: string) => unknown;
};

type ConfigControl = {
  checked?: unknown;
  value?: unknown;
};

export function configPageSmokeHasConfigKey(root: ConfigKeyRoot, key: string): boolean {
  return configPageSmokeConfigControl(root, key) != null;
}

export function configPageSmokeConfigValue(root: ConfigKeyRoot, key: string, fallback: string): string {
  const control = configPageSmokeConfigControl(root, key);
  return typeof control?.value === "string" ? control.value : fallback;
}

export function configPageSmokeConfigChecked(root: ConfigKeyRoot, key: string, fallback: boolean): boolean {
  const control = configPageSmokeConfigControl(root, key);
  return typeof control?.checked === "boolean" ? control.checked : fallback;
}

function configPageSmokeConfigControl(root: ConfigKeyRoot, key: string): ConfigControl | null {
  const selectorKey = key.replace(/\\/g, "\\\\").replace(/"/g, '\\"');
  return root.querySelector(`[data-paradev-config-key="${selectorKey}"]`) as ConfigControl | null;
}

export function writeConfigPageSmokeDataset(root: DatasetRoot, state: ConfigPageSmokeState) {
  root.dataset.paradevConfigPageSmokeActiveTab = state.activeTab;
  root.dataset.paradevConfigPageSmokeSettingsRailSelected = state.settingsRailSelected ? "1" : "0";
  root.dataset.paradevConfigPageSmokeProjectName = state.projectName;
  root.dataset.paradevConfigPageSmokePanelCount = String(Math.max(0, state.configPanelCount));
  root.dataset.paradevConfigPageSmokeHasCliOutputKey = state.hasCliOutputKey ? "1" : "0";
  root.dataset.paradevConfigPageSmokeCliOutputValue = state.cliOutputValue;
  root.dataset.paradevConfigPageSmokeHasBuildParallelismKey = state.hasBuildParallelismKey ? "1" : "0";
  root.dataset.paradevConfigPageSmokeBuildParallelismValue = state.buildParallelismValue;
  root.dataset.paradevConfigPageSmokeHasBuildStrictMetadataKey = state.hasBuildStrictMetadataKey ? "1" : "0";
  root.dataset.paradevConfigPageSmokeBuildStrictMetadataChecked = state.buildStrictMetadataChecked ? "1" : "0";
  root.dataset.paradevConfigPageSmokeLastConfigWriteCount = String(Math.max(0, state.lastConfigWriteCount ?? 0));
  root.dataset.paradevConfigPageSmokeLastConfigWriteKey = state.lastConfigWriteKey ?? "";
  root.dataset.paradevConfigPageSmokeLastConfigWriteValue = state.lastConfigWriteValue ?? "";
  root.dataset.paradevConfigPageSmokeAiProfileSourceKinds = state.aiProfileSourceKinds ?? "";
  root.dataset.paradevConfigPageSmokeAiProfileSourceLabels = state.aiProfileSourceLabels ?? "";
  root.dataset.paradevConfigPageSmokeAiExplainSelectedSources = state.aiExplainSelectedSources ?? "";
  root.dataset.paradevConfigPageSmokeAiExplainSaveDisabled = state.aiExplainSaveDisabled ? "1" : "0";
  root.dataset.paradevConfigPageSmokeAiExplainTemplatesSelected = state.aiExplainTemplatesSelected ? "1" : "0";
  root.dataset.paradevConfigPageSmokeAiExplainProjectIndexSelected = state.aiExplainProjectIndexSelected ? "1" : "0";
  root.dataset.paradevConfigPageSmokeAiExplainToggleCount = String(Math.max(0, state.aiExplainToggleCount ?? 0));
  root.dataset.paradevConfigPageSmokeAiLastSavedProfileId = state.aiLastSavedProfileId ?? "";
  root.dataset.paradevConfigPageSmokeAiLastSavedSourceKinds = state.aiLastSavedSourceKinds ?? "";
}
