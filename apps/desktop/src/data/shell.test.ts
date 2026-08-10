import { describe, expect, it } from "vitest";
import { en } from "../i18n/locales/en";
import { zh } from "../i18n/locales/zh";
import { configOptions, defaultRailId, railItems, workspaceTabs } from "./shell";

describe("shell navigation data", () => {
  it("orders page rail items around editing and build", () => {
    expect(railItems.map((item) => item.id)).toEqual([
      "management",
      "projects",
      "agents",
      "build",
      "developer"
    ]);
  });

  it("keeps editing as the startup rail page", () => {
    expect(defaultRailId).toBe("projects");
  });

  it("renames the project rail label to editing", () => {
    expect(en["rail.projects"]).toBe("Editing");
    expect(zh["rail.projects"]).toBe("编辑");
  });

  it("groups config options by ParaDev settings domain", () => {
    expect(configOptions.map((option) => [option.groupKey, option.id])).toEqual([
      ["config.group.basic", "config-general"],
      ["config.group.basic", "config-appearance"],
      ["config.group.basic", "config-models"],
      ["config.group.project", "config-projects"],
      ["config.group.project", "config-module-defaults"],
      ["config.group.dependency", "config-dependencies"]
    ]);
  });

  it("provides workspace tabs for every real config page", () => {
    expect(workspaceTabs.filter((tab) => tab.kind === "config").map((tab) => tab.id)).toEqual(configOptions.map((option) => option.id));
  });
});
