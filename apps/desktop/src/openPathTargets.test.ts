import { describe, expect, test } from "vitest";
import { PARADEV_DESKTOP_OPEN_PATH_DEFAULT_TARGETS, PARADEV_DESKTOP_OPEN_PATH_TARGETS } from "./generated/desktopContract";
import { availableOpenPathTargets, defaultOpenPathTarget, isOpenPathTarget, normalizeOpenPathTarget, OPEN_PATH_TARGETS } from "./openPathTargets";

describe("open path targets", () => {
  test("uses SDK-generated catalog rows for target ids, labels, and platforms", () => {
    expect(OPEN_PATH_TARGETS.map(({ id, labelKey, platforms }) => ({ id, labelKey, platforms }))).toEqual(PARADEV_DESKTOP_OPEN_PATH_TARGETS);
    expect(defaultOpenPathTarget("macos")).toBe(PARADEV_DESKTOP_OPEN_PATH_DEFAULT_TARGETS.macos);
    expect(defaultOpenPathTarget("windows")).toBe(PARADEV_DESKTOP_OPEN_PATH_DEFAULT_TARGETS.windows);
    expect(defaultOpenPathTarget("linux")).toBe(PARADEV_DESKTOP_OPEN_PATH_DEFAULT_TARGETS.linux);
    expect(defaultOpenPathTarget("unknown")).toBe(PARADEV_DESKTOP_OPEN_PATH_DEFAULT_TARGETS.unknown);
  });

  test("lists compact macOS folder opener choices", () => {
    expect(availableOpenPathTargets("macos").map((target) => target.id)).toEqual(["finder", "cursor", "vscode", "sublimeText", "terminal", "iterm2"]);
    expect(defaultOpenPathTarget("macos")).toBe("finder");
  });

  test("lists compact Windows folder opener choices", () => {
    expect(availableOpenPathTargets("windows").map((target) => target.id)).toEqual(["explorer", "cursor", "vscode", "sublimeText", "cmd", "powershell"]);
    expect(defaultOpenPathTarget("windows")).toBe("explorer");
  });

  test("defaults Linux and unknown platforms to the cross-platform editor target", () => {
    expect(availableOpenPathTargets("linux").map((target) => target.id)).toEqual(["cursor", "vscode", "sublimeText"]);
    expect(availableOpenPathTargets("unknown").map((target) => target.id)).toEqual(["cursor", "vscode", "sublimeText"]);
    expect(defaultOpenPathTarget("linux")).toBe("cursor");
    expect(defaultOpenPathTarget("unknown")).toBe("cursor");
  });

  test("normalizes unavailable stored targets to the platform default", () => {
    expect(normalizeOpenPathTarget("cmd", "macos")).toBe("finder");
    expect(normalizeOpenPathTarget("finder", "windows")).toBe("explorer");
    expect(normalizeOpenPathTarget(null, "macos")).toBe("finder");
    expect(normalizeOpenPathTarget(null, "linux")).toBe("cursor");
    expect(normalizeOpenPathTarget("default", "linux")).toBe("cursor");
    expect(normalizeOpenPathTarget("finder", "unknown")).toBe("cursor");
  });

  test("accepts every persisted target id", () => {
    expect(isOpenPathTarget("sublimeText")).toBe(true);
    expect(isOpenPathTarget("powershell")).toBe(true);
    expect(isOpenPathTarget("default")).toBe(false);
  });
});
