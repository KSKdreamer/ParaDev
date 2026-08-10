import { closeBrackets, closeBracketsKeymap, completionKeymap } from "@codemirror/autocomplete";
import { defaultKeymap, history, historyKeymap, indentWithTab } from "@codemirror/commands";
import { bracketMatching, defaultHighlightStyle, foldGutter, foldKeymap, indentOnInput, indentUnit, syntaxHighlighting } from "@codemirror/language";
import { lintGutter, lintKeymap } from "@codemirror/lint";
import { highlightSelectionMatches, search, searchKeymap } from "@codemirror/search";
import { EditorState, type Extension } from "@codemirror/state";
import {
  crosshairCursor,
  drawSelection,
  dropCursor,
  EditorView,
  highlightActiveLine,
  highlightActiveLineGutter,
  highlightSpecialChars,
  keymap,
  lineNumbers,
  rectangularSelection
} from "@codemirror/view";

export const codeMirrorDefaultFeatureNames = [
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
] as const;

export const commonCodeEditorExtensions: Extension[] = [
  lineNumbers(),
  foldGutter(),
  history(),
  search({ top: true }),
  closeBrackets(),
  bracketMatching(),
  syntaxHighlighting(defaultHighlightStyle, { fallback: true }),
  indentOnInput(),
  EditorState.tabSize.of(4),
  indentUnit.of("\t"),
  highlightActiveLine(),
  highlightActiveLineGutter(),
  drawSelection(),
  EditorState.allowMultipleSelections.of(true),
  rectangularSelection(),
  crosshairCursor(),
  dropCursor(),
  highlightSpecialChars(),
  highlightSelectionMatches(),
  lintGutter(),
  EditorView.contentAttributes.of({
    autocapitalize: "off",
    autocomplete: "off",
    spellcheck: "false"
  }),
  keymap.of([indentWithTab, ...closeBracketsKeymap, ...defaultKeymap, ...historyKeymap, ...foldKeymap, ...searchKeymap, ...completionKeymap, ...lintKeymap])
];
