import { describe, expect, it } from "vitest";
import { Text } from "@codemirror/state";
import {
  buildPdxLspCompletionRequest,
  completionPayloadToOptions,
  semanticTokenRanges,
  shouldRequestPdxSemanticTokens,
  shouldRequestPdxCompletion,
  type PdxLspEditorContext
} from "./pdxLsp";
import type { PdxLspCompletionPayload, PdxLspSemanticTokensPayload } from "../types";

const editorContext: PdxLspEditorContext = {
  projectRoot: "/workspace/mod",
  sourcePath: "/workspace/mod/src/modules/focus/GER_sample/def.txt",
  gameRoot: "/games/hoi4"
};

describe("PDX LSP editor helpers", () => {
  it("builds completion requests with project and source context", () => {
    const request = buildPdxLspCompletionRequest("focus = {\n\tid = GER\n}\n", { line: 1, character: 9, offset: 19 }, editorContext);

    expect(request).toEqual({
      text: "focus = {\n\tid = GER\n}\n",
      line: 1,
      character: 9,
      offset: 19,
      path: "/workspace/mod/src/modules/focus/GER_sample/def.txt",
      projectPath: "/workspace/mod",
      gameRoot: "/games/hoi4",
      limit: 100
    });
  });

  it("maps LSP completion items to CodeMirror options", () => {
    const payload: PdxLspCompletionPayload = {
      schema: "paradev.lsp.completion.v1",
      method: "textDocument/completion",
      ok: true,
      prefix: "GER",
      isIncomplete: false,
      diagnostics: [],
      items: [
        {
          label: "GER_sample",
          kind: 7,
          detail: "focus/GER_sample",
          documentation: { kind: "markdown", value: "Sample Focus" },
          data: { source: "hoi4-entity" }
        }
      ]
    };

    expect(completionPayloadToOptions(payload)).toEqual([
      {
        label: "GER_sample",
        type: "class",
        detail: "focus/GER_sample",
        info: "Sample Focus"
      }
    ]);
  });

  it("avoids implicit backend completion calls for short prefixes", () => {
    expect(shouldRequestPdxCompletion("", false)).toBe(false);
    expect(shouldRequestPdxCompletion("G", false)).toBe(false);
    expect(shouldRequestPdxCompletion("GE", false)).toBe(true);
    expect(shouldRequestPdxCompletion("G", true)).toBe(true);
    expect(shouldRequestPdxCompletion("G", false, { minImplicitCompletionPrefixLength: 1 })).toBe(true);
  });

  it("avoids implicit backend completion calls for large documents", () => {
    expect(shouldRequestPdxCompletion("GE", false, {}, 50_000)).toBe(true);
    expect(shouldRequestPdxCompletion("GE", false, {}, 50_001)).toBe(false);
    expect(shouldRequestPdxCompletion("GE", true, {}, 500_000)).toBe(true);
    expect(shouldRequestPdxCompletion("GE", false, { implicitCompletionMaxLength: 10 }, 11)).toBe(false);
  });

  it("skips semantic-token refreshes for oversized documents before copying text", () => {
    expect(shouldRequestPdxSemanticTokens(200_000)).toBe(true);
    expect(shouldRequestPdxSemanticTokens(200_001)).toBe(false);
    expect(shouldRequestPdxSemanticTokens(6, { semanticTokensMaxLength: 5 })).toBe(false);
  });

  it("maps semantic token rows to bounded editor ranges", () => {
    const payload: PdxLspSemanticTokensPayload = {
      schema: "paradev.lsp.semantic-tokens.v1",
      method: "textDocument/semanticTokens/full",
      ok: true,
      legend: { tokenTypes: ["property", "class"], tokenModifiers: [] },
      data: [],
      diagnostics: [],
      tokens: [
        { line: 0, character: 0, length: 5, token_type: "class", token_modifiers: [] },
        { line: 1, character: 1, length: 50, token_type: "property", token_modifiers: [] }
      ]
    };

    expect(semanticTokenRanges(payload, Text.of(["focus = {", "\tid = GER_sample"]))).toEqual([
      { from: 0, to: 5, className: "cm-pdx-token-class" },
      { from: 11, to: 26, className: "cm-pdx-token-property" }
    ]);
  });
});
