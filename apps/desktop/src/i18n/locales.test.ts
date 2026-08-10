import { describe, expect, it } from "vitest";
import { en } from "./locales/en";
import { zh } from "./locales/zh";

describe("desktop locale dictionaries", () => {
  it("keeps Chinese translations complete for every English UI key", () => {
    expect(Object.keys(zh).sort()).toEqual(Object.keys(en).sort());
  });

  it("describes Chinese as a complete maintained locale instead of an English fallback", () => {
    expect(en["config.general.language.detail"]).not.toMatch(/fallback|falls back/i);
    expect(zh["config.general.language.detail"]).not.toMatch(/回退|英文/);
  });

  it("keeps AI chat profile and unknown source fallback translations localized", () => {
    const keys = [
      "chat.profile.chat.detail",
      "chat.profile.chat.prompt",
      "chat.profile.explain.detail",
      "chat.profile.explain.prompt",
      "chat.profile.createModule.detail",
      "chat.profile.createModule.prompt",
      "chat.profile.build.detail",
      "chat.profile.build.prompt",
      "chat.operation.note",
      "chat.operation.card.moduleDraft.title",
      "chat.operation.card.moduleDraft.summary",
      "chat.operation.card.buildPlan.title",
      "chat.operation.card.buildPlan.summary",
      "chat.operation.card.buildStart.title",
      "chat.operation.card.buildStart.summary",
      "build.aiHandoff.plan.detail",
      "build.aiHandoff.start.detail",
      "chat.source.kind.unknown",
      "config.models.chatProfiles.operationsDetail",
      "config.models.sourceKind.unknown",
      "workspace.module.editor.aiHandoff.moduleDraft.detail"
    ] as const;

    for (const key of keys) {
      expect(zh[key]).toBeTruthy();
      expect(zh[key]).not.toBe(en[key]);
    }
  });

  it("keeps AI chat operational prompts tied to SDK call names in every locale", () => {
    for (const dictionary of [en, zh]) {
      expect(dictionary["chat.profile.createModule.prompt"]).toContain("Project.templates()");
      expect(dictionary["chat.profile.createModule.prompt"]).toContain("Project.create_modules(");
      expect(dictionary["chat.profile.createModule.prompt"]).toContain("write=False");
      expect(dictionary["chat.profile.build.prompt"]).toContain("Project.build(...)");
      expect(dictionary["chat.profile.build.prompt"]).toContain("desktop_project_build_command(...)");
    }
  });
});
