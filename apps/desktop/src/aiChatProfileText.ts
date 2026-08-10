import type { TranslationKey, Translator } from "./i18n";
import type { ParaDevAiChatProfile, ParaDevAiChatProfileWrite } from "./services/paradev";
import { PARADEV_DESKTOP_AI_CHAT_SOURCE_KIND_ROWS, PARADEV_DESKTOP_AI_CHAT_SOURCE_KINDS } from "./generated/desktopContract";
import { resolvedSourceKindRows, type AiChatSourceKindRowLike } from "./aiChatSourceKindText";

type ProfileTextField = "detail" | "label" | "prompt";

export const DEFAULT_AI_CHAT_PROFILE_SOURCE_KINDS = PARADEV_DESKTOP_AI_CHAT_SOURCE_KINDS;
export const AI_CHAT_PROFILE_SOURCE_KINDS = DEFAULT_AI_CHAT_PROFILE_SOURCE_KINDS;

export function aiChatProfileDetail(profile: ParaDevAiChatProfile, t: Translator): string {
  return translatedProfileField(profile, "detail", t);
}

export function aiChatProfileLabel(profile: ParaDevAiChatProfile, t: Translator): string {
  return translatedProfileField(profile, "label", t);
}

export function aiChatProfilePrompt(profile: ParaDevAiChatProfile, t: Translator): string {
  return translatedProfileField(profile, "prompt", t);
}

export function aiChatProfileDraftDetail(profile: ParaDevAiChatProfile, draft: ParaDevAiChatProfileWrite, t: Translator): string {
  return translatedProfileDraftField(profile, draft, "detail", t);
}

export function aiChatProfileDraftLabel(profile: ParaDevAiChatProfile, draft: ParaDevAiChatProfileWrite, t: Translator): string {
  return translatedProfileDraftField(profile, draft, "label", t);
}

export function aiChatProfileDraftPrompt(profile: ParaDevAiChatProfile, draft: ParaDevAiChatProfileWrite, t: Translator): string {
  return translatedProfileDraftField(profile, draft, "prompt", t);
}

export function aiChatProfileSaveDraft(
  profile: ParaDevAiChatProfile,
  draft: ParaDevAiChatProfileWrite,
  t: Translator,
  sourceKindOrder: readonly string[] = DEFAULT_AI_CHAT_PROFILE_SOURCE_KINDS
): ParaDevAiChatProfileWrite {
  const clean: ParaDevAiChatProfileWrite = {};
  addChangedTextField(clean, profile, draft, "label", t);
  addChangedTextField(clean, profile, draft, "detail", t);
  addChangedTextField(clean, profile, draft, "prompt", t);
  if (draft.sourceKinds !== undefined) {
    const sourceKinds = canonicalAiChatProfileSourceKinds(draft.sourceKinds, sourceKindOrder);
    if (!sameStrings(sourceKinds, canonicalAiChatProfileSourceKinds(profile.sourceKinds, sourceKindOrder))) {
      clean.sourceKinds = sourceKinds;
    }
  }
  return clean;
}

export function hasAiChatProfileDraftChanges(
  profile: ParaDevAiChatProfile,
  draft: ParaDevAiChatProfileWrite,
  t: Translator,
  sourceKindOrder: readonly string[] = DEFAULT_AI_CHAT_PROFILE_SOURCE_KINDS
): boolean {
  return Object.keys(aiChatProfileSaveDraft(profile, draft, t, sourceKindOrder)).length > 0;
}

export function canonicalAiChatProfileSourceKinds(sourceKinds: string[], sourceKindOrder: readonly string[] = DEFAULT_AI_CHAT_PROFILE_SOURCE_KINDS): string[] {
  const selected = new Set(sourceKinds);
  const knownKinds = sourceKindOrder.filter((kind) => selected.has(kind));
  const unknownKinds = sourceKinds.filter((kind) => !sourceKindOrder.includes(kind));
  return [...knownKinds, ...unknownKinds];
}

export function frontendAiChatContextKindsForProfileKind(
  kind: string,
  sourceKindRows: readonly AiChatSourceKindRowLike[] = PARADEV_DESKTOP_AI_CHAT_SOURCE_KIND_ROWS
): string[] {
  const cleanKind = kind.trim();
  if (!cleanKind) {
    return [];
  }
  const frontendKinds = resolvedSourceKindRows(sourceKindRows).find((row) => row.id === cleanKind)?.frontendKinds;
  return frontendKinds ? Array.from(frontendKinds) : [cleanKind];
}

function translatedProfileField(profile: ParaDevAiChatProfile, field: ProfileTextField, t: Translator): string {
  const key = profileTranslationKey(profile, field);
  return key ? t(key) : profile[field];
}

function translatedProfileDraftField(profile: ParaDevAiChatProfile, draft: ParaDevAiChatProfileWrite, field: ProfileTextField, t: Translator): string {
  const value = draft[field] ?? profile[field];
  if (value === profile[field]) {
    return translatedProfileField(profile, field, t);
  }
  return value;
}

function rawProfileDraftField(profile: ParaDevAiChatProfile, draft: ParaDevAiChatProfileWrite, field: ProfileTextField, t: Translator): string {
  const value = draft[field] ?? profile[field];
  const key = profileTranslationKey(profile, field);
  if (key && value === t(key)) {
    return profile[field];
  }
  return value;
}

function addChangedTextField(
  clean: ParaDevAiChatProfileWrite,
  profile: ParaDevAiChatProfile,
  draft: ParaDevAiChatProfileWrite,
  field: ProfileTextField,
  t: Translator
) {
  if (draft[field] === undefined) {
    return;
  }
  const value = rawProfileDraftField(profile, draft, field, t);
  if (value !== profile[field]) {
    clean[field] = value;
  }
}

function sameStrings(left: string[], right: string[]): boolean {
  return left.length === right.length && left.every((value, index) => value === right[index]);
}

function profileTranslationKey(profile: ParaDevAiChatProfile, field: ProfileTextField): TranslationKey | undefined {
  if (field === "label") {
    return profile.labelKey;
  }
  if (field === "detail") {
    return profile.detailKey;
  }
  return profile.promptKey;
}
