import { describe, expect, it } from "vitest";
import { en } from "./i18n/locales/en";
import { zh } from "./i18n/locales/zh";
import {
  moduleNavigationGroupKey,
  moduleNavigationGroupOrder,
} from "./moduleNavigationGroups";

describe("module navigation groups", () => {
  it("translates extension-owned semantic groups without knowing family ids", () => {
    expect(moduleNavigationGroupKey("country")).toBe("modules.group.country");
    expect(moduleNavigationGroupKey("military")).toBe("modules.group.military");
    expect(moduleNavigationGroupKey("world")).toBe("modules.group.world");
    expect(moduleNavigationGroupKey("events")).toBe("modules.group.events");
    expect(moduleNavigationGroupKey("shared")).toBe("modules.group.shared");
  });

  it("uses one visible advanced fallback for missing or future groups", () => {
    expect(moduleNavigationGroupKey("future-extension")).toBe(
      "modules.group.other",
    );
    expect(moduleNavigationGroupKey(undefined)).toBe("modules.group.other");
  });

  it("keeps canonical group order and bilingual labels complete", () => {
    expect(moduleNavigationGroupOrder).toEqual([
      "modules.group.country",
      "modules.group.military",
      "modules.group.world",
      "modules.group.events",
      "modules.group.shared",
      "modules.group.other",
    ]);
    for (const groupKey of moduleNavigationGroupOrder) {
      expect(en[groupKey]).toBeTruthy();
      expect(zh[groupKey]).toBeTruthy();
      expect(zh[groupKey]).not.toBe(en[groupKey]);
    }
  });
});
