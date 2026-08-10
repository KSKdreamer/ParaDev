import { describe, expect, it } from "vitest";
import { codeMirrorDefaultFeatureNames, commonCodeEditorExtensions } from "./codeMirrorSetup";

describe("CodeMirror default editor setup", () => {
  it("keeps common editor affordances explicit", () => {
    expect(commonCodeEditorExtensions.length).toBeGreaterThan(0);
    expect(codeMirrorDefaultFeatureNames).toEqual([
      "line-numbers",
      "fold-gutter",
      "history",
      "default-keymap",
      "history-keymap",
      "fold-keymap",
      "search",
      "search-keymap",
      "completion-keymap",
      "close-brackets",
      "close-brackets-keymap",
      "bracket-matching",
      "syntax-highlighting",
      "indent-on-input",
      "tab-indentation",
      "active-line",
      "active-line-gutter",
      "draw-selection",
      "multiple-selections",
      "rectangular-selection",
      "crosshair-cursor",
      "drop-cursor",
      "special-character-highlighting",
      "selection-match-highlighting",
      "lint-gutter",
      "lint-keymap",
      "editor-content-attributes"
    ]);
  });
});
