import type { TranslationKey, Translator } from "./i18n";
import type { ParaDevAiChatSource, ParaDevAiChatSourceKindRow } from "./services/paradev";
import { PARADEV_DESKTOP_AI_CHAT_SOURCE_KIND_ROWS } from "./generated/desktopContract";

const contextSourceKindLabelKeys: Record<string, TranslationKey> = {
  catalog: "config.models.sourceKind.projectIndex",
  diagnostics: "chat.source.kind.diagnostics",
  "scripted-gui": "config.models.sourceKind.scriptedGui",
  source: "chat.source.kind.source",
  templates: "chat.source.kind.templates",
  workspace: "chat.source.kind.workspace"
};

const sourceKindLabelKeys: Record<string, TranslationKey> = {
  diagnostics: "config.models.sourceKind.diagnostics",
  project: "config.models.sourceKind.project",
  "project-index": "config.models.sourceKind.projectIndex",
  "scripted-gui": "config.models.sourceKind.scriptedGui",
  selection: "config.models.sourceKind.selection",
  templates: "config.models.sourceKind.templates"
};

export type AiChatSourceKindRowLike = {
  frontendKinds?: readonly string[];
  id: string;
  label?: string;
  labelKey?: TranslationKey;
};

export function aiChatContextSourceLabel(
  source: ParaDevAiChatSource,
  t: Translator,
  sourceKindRows: readonly AiChatSourceKindRowLike[] = PARADEV_DESKTOP_AI_CHAT_SOURCE_KIND_ROWS
): string {
  const sourceKindRow = sourceKindRowForContextKind(source.kind, resolvedSourceKindRows(sourceKindRows));
  const kindLabelKey = contextSourceKindLabelKeys[source.kind];
  const sourceLabel = source.label?.trim() ?? "";
  if (sourceLabel) {
    return sourceKindRow?.label?.trim() === sourceLabel ? sourceKindRowLabel(sourceKindRow, t) : sourceLabel;
  }
  return source.relativePath || source.path || (sourceKindRow ? sourceKindRowLabel(sourceKindRow, t) : kindLabelKey ? t(kindLabelKey) : t("chat.source.kind.unknown"));
}

export function aiChatProfileSourceKindLabel(
  kind: string,
  t: Translator,
  sourceKindRows: readonly AiChatSourceKindRowLike[] = PARADEV_DESKTOP_AI_CHAT_SOURCE_KIND_ROWS
): string {
  const sourceKindRow = resolvedSourceKindRows(sourceKindRows).find((row) => row.id === kind);
  return sourceKindRow ? sourceKindRowLabel(sourceKindRow, t) : t("config.models.sourceKind.unknown");
}

export function resolvedSourceKindRows(sourceKindRows: readonly AiChatSourceKindRowLike[] = []): readonly AiChatSourceKindRowLike[] {
  return sourceKindRows.length > 0 ? sourceKindRows : PARADEV_DESKTOP_AI_CHAT_SOURCE_KIND_ROWS;
}

function sourceKindRowForContextKind(kind: string, sourceKindRows: readonly AiChatSourceKindRowLike[]): AiChatSourceKindRowLike | undefined {
  return sourceKindRows.find((row) => row.id === kind || row.frontendKinds?.includes(kind));
}

function sourceKindRowLabel(row: AiChatSourceKindRowLike | ParaDevAiChatSourceKindRow, t: Translator): string {
  const labelKey = row.labelKey ?? sourceKindLabelKeys[row.id];
  if (labelKey) {
    const translated = t(labelKey);
    if (translated !== labelKey) {
      return translated;
    }
  }
  return row.label?.trim() || row.id;
}
