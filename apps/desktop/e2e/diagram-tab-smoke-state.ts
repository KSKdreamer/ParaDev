type DatasetTarget = {
  dataset: Record<string, string | undefined>;
};

export type DiagramTabSmokePopupState = {
  ariaLabel: string;
  count: number;
  nodeId: string;
  openModuleText: string;
  selectedNodeId: string;
  sourceInfoPath: string;
  title: string;
};

export type DiagramTabSmokeSelectedNodeState = {
  mode: string;
  nodeId: string;
  switchCount: number;
  switchMode: string;
};

export type DiagramTabSmokeApplyState = {
  applyButtonDisabled: boolean;
  applyButtonText: string;
  applyPreviewText: string;
  dirtySummaryText: string;
  reviewPanelCount: number;
};

export type DiagramTabSmokeSourceState = {
  pickerCount: number;
  pickerOptionCount: number;
  pickerPath: string;
  pickerText: string;
  pickerValue: string;
  sourceTabCount: number;
  textPanelVisible: boolean;
};

export type DiagramTabSmokeHitTargetState = {
  c01HitTargetCount: number;
  c01NodeCount: number;
  targetCount: number;
  targetId: string;
};

export function writeDiagramTabSmokeApplyDataset(root: DatasetTarget, state: DiagramTabSmokeApplyState): void {
  root.dataset.paradevDiagramTabSmokeApplyButtonDisabled = state.applyButtonDisabled ? "1" : "0";
  root.dataset.paradevDiagramTabSmokeApplyButtonText = state.applyButtonText;
  root.dataset.paradevDiagramTabSmokeApplyPreviewText = state.applyPreviewText;
  root.dataset.paradevDiagramTabSmokeDirtySummaryText = state.dirtySummaryText;
  root.dataset.paradevDiagramTabSmokeApplyReviewCount = String(state.reviewPanelCount);
}

export function writeDiagramTabSmokePopupDataset(root: DatasetTarget, state: DiagramTabSmokePopupState): void {
  root.dataset.paradevDiagramTabSmokePopupCount = String(state.count);
  root.dataset.paradevDiagramTabSmokePopupAria = state.ariaLabel;
  root.dataset.paradevDiagramTabSmokePopupNodeId = state.nodeId;
  root.dataset.paradevDiagramTabSmokePopupOpenModuleText = state.openModuleText;
  root.dataset.paradevDiagramTabSmokePopupTitle = state.title;
  root.dataset.paradevDiagramTabSmokePopupSourceInfoPath = state.sourceInfoPath;
  root.dataset.paradevDiagramTabSmokePopupSelectedMatch = state.nodeId && state.nodeId === state.selectedNodeId ? "1" : "0";
}

export function writeDiagramTabSmokeSelectedNodeDataset(root: DatasetTarget, state: DiagramTabSmokeSelectedNodeState): void {
  root.dataset.paradevDiagramTabSmokeSelectedNodeId = state.nodeId;
  root.dataset.paradevDiagramTabSmokeSelectedNodeMode = state.mode;
  root.dataset.paradevDiagramTabSmokeModeSwitchCount = String(state.switchCount);
  root.dataset.paradevDiagramTabSmokeModeSwitchMode = state.switchMode;
  root.dataset.paradevDiagramTabSmokeModeSwitchSelectedMatch = state.nodeId && state.mode && state.mode === state.switchMode ? "1" : "0";
}

export function writeDiagramTabSmokeSourceDataset(root: DatasetTarget, state: DiagramTabSmokeSourceState): void {
  root.dataset.paradevDiagramTabSmokeSourcePickerCount = String(state.pickerCount);
  root.dataset.paradevDiagramTabSmokeSourcePickerOptionCount = String(state.pickerOptionCount);
  root.dataset.paradevDiagramTabSmokeSourcePickerValue = state.pickerValue;
  root.dataset.paradevDiagramTabSmokeSourcePickerText = state.pickerText;
  root.dataset.paradevDiagramTabSmokeSourcePickerPath = state.pickerPath;
  root.dataset.paradevDiagramTabSmokeSourceTabCount = String(state.sourceTabCount);
  root.dataset.paradevDiagramTabSmokeSourceTextPanel = state.textPanelVisible ? "1" : "0";
}

export function writeDiagramTabSmokeHitTargetDataset(root: DatasetTarget, state: DiagramTabSmokeHitTargetState): void {
  root.dataset.paradevDiagramTabSmokeC01HitTargetCount = String(state.c01HitTargetCount);
  root.dataset.paradevDiagramTabSmokeHitTargetNodeMatch = state.c01NodeCount > 0 && state.c01HitTargetCount === state.c01NodeCount ? "1" : "0";
  root.dataset.paradevDiagramTabSmokeHitTargetTargetId = state.targetId;
  root.dataset.paradevDiagramTabSmokeHitTargetTargetCount = String(state.targetCount);
  root.dataset.paradevDiagramTabSmokeHitTargetTargetReady = state.targetId && state.targetCount === 1 ? "1" : "0";
}
