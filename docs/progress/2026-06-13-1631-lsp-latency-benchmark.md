# LSP Latency Benchmark Progress

Date: 2026-06-13 16:31

Linear: none

## Done

- Benchmarked PDX LSP diagnostics, semantic tokens, completion, and server `textDocument/didChange` on synthetic 132 KB, 672 KB, and 1.35 MB PDX documents.
- Root cause: the stdio LSP server synchronously ran full diagnostics on every `didChange`, so keystrokes scaled with full-document parse time. Baseline `didChange` was about 88 ms at 132 KB, 468 ms at 672 KB, and 925 ms at 1.35 MB.
- Added a default large-document `didChange` diagnostics gate. Open/save and explicit diagnostics still parse; large change notifications just update server text state.
- Added bounded parsed-document reuse for LSP diagnostics, symbols, hover, and semantic-token consumers on repeated identical editor buffers.
- Changed desktop CodeMirror semantic-token refresh to check document length before `doc.toString()`, defer full text copying until the debounce survives, and abort stale REST semantic-token work.

## Verification

- `rtk bash scripts/test.bash tests/test_lsp.py -q` passed, 17 tests.
- `rtk npm --prefix apps/desktop run test:unit -- src/moduleEditor/pdxLsp.test.ts` passed, 5 tests.
- Post-change benchmark: large `didChange` notifications were effectively 0 ms for the same 132 KB, 672 KB, and 1.35 MB synthetic documents because the server skipped synchronous diagnostics above the 50 KB default gate.
- Repeated cached diagnostics were effectively 0 ms after the first parse. Repeated semantic-token generation still spends traversal/encoding time: about 10 ms at 132 KB, 92 ms at 672 KB, and 225 ms at 1.35 MB.

## Risks Or Blockers

- Large-document diagnostics now update on open/save or explicit diagnostics requests, not every keystroke. This is intentional until the server has an async debounce scheduler.
- Completion context still scans from document start to cursor to infer HOI4 modifier/effect/trigger context. At 1.35 MB this measured about 165 ms, which is acceptable for debounced completion but still a target for an incremental document-state index.

## Next

- Add an async or background diagnostic scheduler for stdio LSP clients so large files can publish delayed diagnostics after typing stops.
- Maintain per-open-document brace/context indexes for completion instead of rescanning from the beginning of the file.
- Consider semantic-token delta/range support once the editor moves to a fuller Monaco or VS Code language-client bridge.
