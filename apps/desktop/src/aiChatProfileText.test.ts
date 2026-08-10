import { describe, expect, it } from "vitest";
import { createTranslator } from "./i18n";
import type { ParaDevAiChatProfile, ParaDevAiChatSourceKindRow } from "./services/paradev";
import {
  aiChatProfileDraftDetail,
  aiChatProfileDraftLabel,
  aiChatProfileDraftPrompt,
  aiChatProfileLabel,
  aiChatProfileSaveDraft,
  frontendAiChatContextKindsForProfileKind,
  hasAiChatProfileDraftChanges
} from "./aiChatProfileText";

const profile: ParaDevAiChatProfile = {
  detail: "Explain selected source.",
  detailKey: "chat.profile.explain.detail",
  id: "explain",
  label: "Explain HoI4 code",
  labelKey: "chat.profile.explain.label",
  promptKey: "chat.profile.explain.prompt",
  prompt: "Explain HoI4 code.",
  sourceKinds: ["project", "selection"]
} as ParaDevAiChatProfile;

describe("aiChatProfileText", () => {
  it("translates built-in profile fields without saving translated defaults", () => {
    const t = createTranslator("zh");

    expect(aiChatProfileLabel(profile, t)).toBe("说明 HOI4 代码");
    expect(aiChatProfileDraftLabel(profile, {}, t)).toBe("说明 HOI4 代码");
    expect(aiChatProfileSaveDraft(profile, { label: "说明 HOI4 代码" }, t)).not.toHaveProperty("label");
  });

  it("preserves custom profile fields during save", () => {
    const t = createTranslator("zh");

    expect(aiChatProfileSaveDraft(profile, { label: "PIHC3 代码解释" }, t)).toMatchObject({
      label: "PIHC3 代码解释"
    });
  });

  it("does not save unchanged built-in text when only the prompt changes", () => {
    const t = createTranslator("zh");
    const draft = {
      detail: profile.detail,
      label: profile.label,
      prompt: "Explain PIHC3 source with exact SDK next steps."
    };

    expect(aiChatProfileDraftLabel(profile, draft, t)).toBe("说明 HOI4 代码");
    expect(aiChatProfileDraftDetail(profile, draft, t)).toBe("说明 PDX、本地化、元数据、GUI、GFX 和生成产物。");
    expect(aiChatProfileSaveDraft(profile, draft, t)).toEqual({
      prompt: "Explain PIHC3 source with exact SDK next steps."
    });
  });

  it("does not save unchanged translated built-in prompts", () => {
    const t = createTranslator("zh");

    expect(aiChatProfileDraftPrompt(profile, {}, t)).toBe("说明 HoI4 代码和 ParaDev 源文件，面向模组作者解释文件职责、可能的游戏效果，并指出由 SDK 支撑的下一步操作。");
    expect(aiChatProfileSaveDraft(profile, { prompt: "说明 HoI4 代码和 ParaDev 源文件，面向模组作者解释文件职责、可能的游戏效果，并指出由 SDK 支撑的下一步操作。" }, t)).not.toHaveProperty("prompt");
  });

  it("canonicalizes source kinds before comparing and saving", () => {
    const t = createTranslator("en");

    expect(aiChatProfileSaveDraft(profile, { sourceKinds: ["selection", "project"] }, t)).not.toHaveProperty("sourceKinds");
    expect(aiChatProfileSaveDraft(profile, { sourceKinds: ["diagnostics", "project", "selection"] }, t)).toEqual({
      sourceKinds: ["project", "selection", "diagnostics"]
    });
  });

  it("uses SDK-generated source kind mappings for frontend context kinds", () => {
    expect(frontendAiChatContextKindsForProfileKind("project")).toEqual(["workspace"]);
    expect(frontendAiChatContextKindsForProfileKind("selection")).toEqual(["source"]);
    expect(frontendAiChatContextKindsForProfileKind("diagnostics")).toEqual(["diagnostics"]);
    expect(frontendAiChatContextKindsForProfileKind("templates")).toEqual(["templates"]);
    expect(frontendAiChatContextKindsForProfileKind("scripted-gui")).toEqual(["scripted-gui"]);
  });

  it("uses SDK source kind rows for runtime frontend context mappings", () => {
    const sourceKindRows: ParaDevAiChatSourceKindRow[] = [
      {
        frontendKinds: ["catalog"],
        id: "project-index",
        label: "Project index"
      }
    ];

    expect(frontendAiChatContextKindsForProfileKind("project-index", sourceKindRows)).toEqual(["catalog"]);
  });

  it("detects whether a profile draft would change the SDK payload", () => {
    const t = createTranslator("zh");

    expect(hasAiChatProfileDraftChanges(profile, {}, t)).toBe(false);
    expect(hasAiChatProfileDraftChanges(profile, { label: "说明 HOI4 代码" }, t)).toBe(false);
    expect(hasAiChatProfileDraftChanges(profile, { sourceKinds: ["selection", "project"] }, t)).toBe(false);
    expect(hasAiChatProfileDraftChanges(profile, { prompt: "Explain PIHC3 source with exact SDK next steps." }, t)).toBe(true);
    expect(hasAiChatProfileDraftChanges(profile, { sourceKinds: ["project", "selection", "diagnostics"] }, t)).toBe(true);
  });
});
