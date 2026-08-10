import { autocompletion, type Completion, type CompletionContext, type CompletionResult } from "@codemirror/autocomplete";
import { type Extension, StateEffect, StateField, Text } from "@codemirror/state";
import { Decoration, type DecorationSet, EditorView, ViewPlugin, type ViewUpdate } from "@codemirror/view";
import { requestPdxLspCompletion, requestPdxLspSemanticTokens } from "../services/paradev";
import type {
  PdxLspCompletionPayload,
  PdxLspCompletionRequest,
  PdxLspPosition,
  PdxLspSemanticToken,
  PdxLspSemanticTokensPayload,
  PdxLspSemanticTokensRequest
} from "../types";

export type PdxLspEditorContext = {
  projectRoot?: string;
  sourcePath?: string;
  gameRoot?: string;
  limit?: number;
  completionDebounceMs?: number;
  implicitCompletionMaxLength?: number;
  minImplicitCompletionPrefixLength?: number;
  semanticTokensDebounceMs?: number;
  semanticTokensMaxLength?: number;
};

export type PdxSemanticTokenRange = {
  from: number;
  to: number;
  className: string;
};

const completionKindType: Record<number, Completion["type"]> = {
  7: "class",
  10: "property",
  12: "constant",
  18: "variable"
};
const completionWord = /[\w.@:-]*$/;
const defaultCompletionDebounceMs = 120;
const defaultImplicitCompletionMaxLength = 50_000;
const defaultMinImplicitCompletionPrefixLength = 2;
const defaultSemanticTokensDebounceMs = 650;
const defaultSemanticTokensMaxLength = 200_000;
const semanticTokensCacheLimit = 12;
const semanticTokensCache = new Map<string, PdxLspSemanticTokensPayload>();
const setSemanticDecorations = StateEffect.define<DecorationSet>();
const semanticDecorations = StateField.define<DecorationSet>({
  create: () => Decoration.none,
  update(value, transaction) {
    let current = value.map(transaction.changes);
    for (const effect of transaction.effects) {
      if (effect.is(setSemanticDecorations)) {
        current = effect.value;
      }
    }
    return current;
  },
  provide: (field) => EditorView.decorations.from(field)
});

export function createPdxLspExtensions(context: PdxLspEditorContext): Extension[] {
  return [
    autocompletion({ override: [pdxCompletionSource(context)] }),
    semanticDecorations,
    pdxSemanticTokenPlugin(context),
    pdxLspTheme
  ];
}

export function buildPdxLspCompletionRequest(text: string, position: PdxLspPosition, context: PdxLspEditorContext): PdxLspCompletionRequest {
  return {
    text,
    line: position.line,
    character: position.character,
    offset: position.offset,
    path: context.sourcePath,
    projectPath: context.projectRoot,
    gameRoot: context.gameRoot,
    limit: context.limit ?? 100
  };
}

export function buildPdxLspSemanticTokensRequest(text: string, context: PdxLspEditorContext): PdxLspSemanticTokensRequest {
  return {
    text,
    path: context.sourcePath
  };
}

export function completionPayloadToOptions(payload: PdxLspCompletionPayload): Completion[] {
  if (!payload.ok) {
    return [];
  }
  return payload.items.map((item) => ({
    label: item.label,
    type: completionKindType[item.kind ?? 0] ?? "text",
    detail: item.detail,
    info: completionInfo(item.documentation)
  }));
}

export function semanticTokenRanges(payload: PdxLspSemanticTokensPayload, doc: Text): PdxSemanticTokenRange[] {
  if (!payload.ok) {
    return [];
  }
  return payload.tokens.flatMap((token) => semanticTokenRange(token, doc));
}

export function shouldRequestPdxCompletion(
  matchText: string,
  explicit: boolean,
  context: PdxLspEditorContext = {},
  docLength = 0
): boolean {
  if (explicit) {
    return true;
  }
  if (docLength > (context.implicitCompletionMaxLength ?? defaultImplicitCompletionMaxLength)) {
    return false;
  }
  return matchText.length >= (context.minImplicitCompletionPrefixLength ?? defaultMinImplicitCompletionPrefixLength);
}

export function shouldRequestPdxSemanticTokens(docLength: number, context: PdxLspEditorContext = {}): boolean {
  return docLength <= (context.semanticTokensMaxLength ?? defaultSemanticTokensMaxLength);
}

function pdxCompletionSource(context: PdxLspEditorContext) {
  return async (completionContext: CompletionContext): Promise<CompletionResult | null> => {
    const match = completionContext.matchBefore(completionWord);
    if (!match || (match.from === match.to && !completionContext.explicit)) {
      return null;
    }
    if (!shouldRequestPdxCompletion(match.text, completionContext.explicit, context, completionContext.state.doc.length)) {
      return null;
    }
    const position = lspPosition(completionContext.state.doc, completionContext.pos);
    const controller = new AbortController();
    completionContext.addEventListener("abort", () => controller.abort(), { onDocChange: true });
    try {
      await waitForIdle(context.completionDebounceMs ?? defaultCompletionDebounceMs, () => completionContext.aborted);
      if (completionContext.aborted) {
        return null;
      }
      const payload = await requestPdxLspCompletion(
        buildPdxLspCompletionRequest(completionContext.state.doc.toString(), position, context),
        { signal: controller.signal }
      );
      if (completionContext.aborted) {
        return null;
      }
      return {
        from: match.from,
        options: completionPayloadToOptions(payload),
        validFor: /^[\w.@:-]*$/
      };
    } catch {
      return null;
    }
  };
}

function pdxSemanticTokenPlugin(context: PdxLspEditorContext): Extension {
  return ViewPlugin.fromClass(
    class {
      private requestId = 0;
      private debounceHandle: ReturnType<typeof setTimeout> | undefined;
      private abortController: AbortController | undefined;
      private destroyed = false;

      constructor(view: EditorView) {
        this.scheduleRefresh(view);
      }

      update(update: ViewUpdate) {
        if (update.docChanged) {
          this.scheduleRefresh(update.view);
        }
      }

      destroy() {
        this.destroyed = true;
        this.requestId += 1;
        this.abortController?.abort();
        if (this.debounceHandle !== undefined) {
          clearTimeout(this.debounceHandle);
        }
      }

      private scheduleRefresh(view: EditorView) {
        const requestId = ++this.requestId;
        this.abortController?.abort();
        if (this.debounceHandle !== undefined) {
          clearTimeout(this.debounceHandle);
        }
        if (!shouldRequestPdxSemanticTokens(view.state.doc.length, context)) {
          view.dispatch({ effects: setSemanticDecorations.of(Decoration.none) });
          return;
        }
        this.debounceHandle = setTimeout(() => {
          if (this.destroyed || requestId !== this.requestId || !shouldRequestPdxSemanticTokens(view.state.doc.length, context)) {
            return;
          }
          const text = view.state.doc.toString();
          this.refresh(view, requestId, text);
        }, context.semanticTokensDebounceMs ?? defaultSemanticTokensDebounceMs);
      }

      private refresh(view: EditorView, requestId: number, text: string) {
        const cacheKey = semanticTokensCacheKey(text, context);
        const cached = semanticTokensCache.get(cacheKey);
        if (cached !== undefined) {
          this.dispatchDecorations(view, requestId, text, cached);
          return;
        }
        const controller = new AbortController();
        this.abortController = controller;
        requestPdxLspSemanticTokens(buildPdxLspSemanticTokensRequest(text, context), { signal: controller.signal })
          .then((payload) => {
            rememberSemanticTokens(cacheKey, payload);
            this.dispatchDecorations(view, requestId, text, payload);
          })
          .catch(() => {
            if (!this.destroyed && requestId === this.requestId && view.state.doc.toString() === text) {
              view.dispatch({ effects: setSemanticDecorations.of(Decoration.none) });
            }
          });
      }

      private dispatchDecorations(view: EditorView, requestId: number, text: string, payload: PdxLspSemanticTokensPayload) {
        if (!this.destroyed && requestId === this.requestId && view.state.doc.toString() === text) {
          view.dispatch({ effects: setSemanticDecorations.of(decorationsFromSemanticTokens(payload, view.state.doc)) });
        }
      }
    }
  );
}

function decorationsFromSemanticTokens(payload: PdxLspSemanticTokensPayload, doc: Text): DecorationSet {
  return Decoration.set(
    semanticTokenRanges(payload, doc).map((range) => Decoration.mark({ class: range.className }).range(range.from, range.to)),
    true
  );
}

function semanticTokenRange(token: PdxLspSemanticToken, doc: Text): PdxSemanticTokenRange[] {
  if (token.line < 0 || token.line >= doc.lines || token.character < 0 || token.length <= 0) {
    return [];
  }
  const line = doc.line(token.line + 1);
  const from = line.from + token.character;
  const to = Math.min(from + token.length, line.to);
  if (from >= to || from > line.to) {
    return [];
  }
  return [{ from, to, className: `cm-pdx-token-${token.token_type.replace(/[^a-z0-9_-]/gi, "-")}` }];
}

function lspPosition(doc: Text, offset: number): PdxLspPosition {
  const line = doc.lineAt(offset);
  return {
    line: line.number - 1,
    character: offset - line.from,
    offset
  };
}

function completionInfo(documentation: PdxLspCompletionPayload["items"][number]["documentation"]): string | undefined {
  if (typeof documentation === "string") {
    return documentation;
  }
  return documentation?.value;
}

function waitForIdle(delayMs: number, aborted: () => boolean): Promise<void> {
  if (delayMs <= 0 || aborted()) {
    return Promise.resolve();
  }
  return new Promise((resolve) => {
    const handle = setTimeout(resolve, delayMs);
    if (aborted()) {
      clearTimeout(handle);
      resolve();
    }
  });
}

function semanticTokensCacheKey(text: string, context: PdxLspEditorContext): string {
  return `${context.sourcePath ?? ""}\n${text}`;
}

function rememberSemanticTokens(key: string, payload: PdxLspSemanticTokensPayload) {
  semanticTokensCache.set(key, payload);
  if (semanticTokensCache.size > semanticTokensCacheLimit) {
    const oldest = semanticTokensCache.keys().next().value;
    if (typeof oldest === "string") {
      semanticTokensCache.delete(oldest);
    }
  }
}

const pdxLspTheme = EditorView.baseTheme({
  ".cm-pdx-token-class": { color: "var(--cm-token-class)", fontWeight: "600" },
  ".cm-pdx-token-property": { color: "var(--cm-token-property)" },
  ".cm-pdx-token-enum": { color: "var(--cm-token-enum)" },
  ".cm-pdx-token-string": { color: "var(--cm-token-string)" },
  ".cm-pdx-token-number": { color: "var(--cm-token-number)" },
  ".cm-pdx-token-variable": { color: "var(--cm-token-variable)" }
});
