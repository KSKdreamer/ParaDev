# PIHC3 extension Registry concurrency

Date: 2026-07-29

## Outcome

Concurrent ParaDev processes no longer fail while reading PIHC3 authoring
templates through HeavenBase 0.1.2.1. The SDK-owned project-extension loader
now:

- serializes ParaDev publications to the durable HeavenBase module Registry;
- follows HeavenBase's documented refresh-and-retry contract for an external
  compare-and-set conflict;
- bounds retries and preserves a contextual project error when durable state
  cannot be refreshed;
- writes an ignored `.paradev/cache/extension-install.json` receipt after a
  successful install;
- accepts that derived receipt only when extension content digests, descriptor
  keys, receipt coverage, and every durable coordinate and manifest
  fingerprint match.

All interfaces inherit the behavior because desktop, SDK, CLI, REST, and MCP
resolve project modules through the same extension loader. No GUI-side retry or
fallback was added.

## Verification

- Seven extension lifecycle contracts pass, covering successful activation,
  exact-checkout replacement, one-conflict refresh/retry, unrefreshable
  conflict failure, verified receipt reuse, and incomplete-receipt rejection.
- Nineteen focused project-extension, PIHC3 extensible-layout, and authoring
  template contracts pass.
- Three simultaneous fresh-process PIHC3 template queries (`focus`,
  `technology`, and all authoring-ready templates) all exited successfully
  against the real persistent HeavenBase backend.
- After the receipt was established, the same three fresh-process queries each
  completed in about 0.6 seconds without reinstalling unchanged extensions.
- The receipt is ignored by PIHC3 Git policy and is safe to delete.

## Next

The remaining visible PIHC3 authoring gap is whole Focus-tree creation:
individual Focus nodes are source-backed and creatable, while the owning
`src/collections/focus/` tree still needs a compact collection creation flow
from the diagram scope.
