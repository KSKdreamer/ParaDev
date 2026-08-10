# PIHC3 Safe Source Inventory

Status: implemented and verified

Date: 2026-08-10

## Outcome

ParaDev's hidden parsed-source cache now avoids rereading unchanged PIHC3
source bodies while preserving content-addressed correctness. Each family cache
entry contains a bounded, checksummed, strictly sorted per-file inventory with
the exact content SHA-256 and the filesystem observations that may safely reuse
it. The authored PIHC3 tree and user-facing metadata remain unchanged.

A cache hit matches all non-source identity fields, decodes the bounded derived
payload, then performs one final family fingerprint against the stored
inventory. Changed or ambiguous files are rehashed. No parsed payload is
returned before that validation succeeds.

## Safety Contract

- Digest reuse is restricted to explicitly trusted local APFS, HFS, ext, XFS,
  Btrfs, ZFS, tmpfs, and ramfs devices. Classification is conservative and
  memoized by numeric device id; macOS mount metadata is probed once rather
  than once per family.
- Reuse requires exact size, mtime, precise ctime, device, and inode equality
  with an observation-time race window. A preserved coarse mtime is safe only
  when ctime is precise; coarse ctime always forces hashing.
- Changed-file hashing binds the path to the opened regular-file handle using
  `O_NOFOLLOW`, fstat before and after streaming, and a post-close lstat. One
  transient identity drift retries the family; repeated drift fails clearly.
- File or directory symlinks and cross-device family topology bypass parsed
  cache reuse. Unknown, network, FUSE, FAT, and Windows filesystems full-hash
  unless a comparably reliable adapter is added later.
- Directory paths participate in the typed family digest, so empty-unit
  add/delete/rename changes cannot alias the prior fingerprint.
- Malformed, checksum-invalid, duplicate, out-of-order, or oversized inventory
  documents reparse and atomically refresh. Write failures remain nonblocking
  and observable.
- A bypassed family contributes no aggregate discovery signature, so the
  artifact-plan cache cannot reuse a plan built from an unsafe source snapshot.

## Performance Evidence

The accepted pre-slice wheel was extracted and run directly against the same
PIHC3 tree, current output, Python environment, and `parallelism=8`. Its true
warm cached build completed in 15.487 seconds; module discovery occupied 10.418
seconds. The frozen one-walk inventory implementation completed in 14.648
seconds; module discovery occupied 10.575 seconds. This is a 5.4% cached-total
improvement with a 1.5% discovery difference inside normal run-to-run noise.

A controlled current-code comparison completed in 14.648 seconds with metadata
digest reuse and 18.152 seconds when reuse was disabled and every source body
was hashed. The unchanged warm discovery path performed zero source-body hash
reads. Both runs returned 14,573 active modules, 106 collections, 33,437
artifacts, and zero diagnostics.

Experiments that performed two complete validation walks or added heavier
`scandir` directory bookkeeping were slower and were removed before this
checkpoint.

## Verification

- Source-cache, artifact-plan-cache, and project-build focused gate: 215 passed.
- Adversarial coverage includes restored-mtime same-size edits, size changes,
  add/delete/rename, file and directory symlinks, unsupported/coarse metadata,
  one-retry/repeated path races, invalid inventories, post-decode edits,
  write-failure observability, target-filter signature stability, collections,
  and full-build bypass.
- Full Python gate: 2,528 passed, with 9 expected native-Windows skips.
- Desktop gate: 1,519 passed across 93 files.
- Black/Flake8: 238 files clean. `git diff --check`, environment lock and
  generated projections, README projections, and exact 22-file GUI package
  inventory pass.
- PIHC3 source-layout audit: zero errors across 70 module families, 14,574
  physical source modules, and 36,469 files; one intentional visible metadata
  file remains.
- The Heaven-style scanner has no new raw-subprocess finding. Low-level
  `hashlib`, JSON, `Path`, and `os` use is explicitly retained here because the
  cache needs incremental streaming SHA-256, exact canonical checksums, atomic
  replacement, `O_NOFOLLOW`/fstat identity checks, and filesystem-device
  classification that HeavenBase 0.1.2.2 does not expose as equivalent safe
  primitives.

## Installed-wheel Evidence

- Wheel: `dist/python/paradev-0.1.0.0.dev0-py3-none-any.whl`
- Wheel bytes: `1,818,983`
- Wheel SHA-256:
  `1123b602a01eca7ae5dbaa6f593d1b7b7512b7944eaf5f7ec1a86ecd4e923ce0`
- Evidence:
  `dist/evidence/2026-08-10-1133-pihc3-source-inventory-wheel-smoke.json`
- Evidence SHA-256:
  `c4ec4b96623e889da23dbe19dfafaf8a2c00cdbab2a5c710ebc2abcb8d68deb3`
- Runtime: isolated venv/home/temp, no developer checkout on the import path,
  no `uv` available to the app; ParaDev `0.1.0.0.dev0`, HeavenBase `0.1.2.2`,
  FastMCP `4.0.0b2`, and MCP `2.0.0`.

| Mode | Seconds | Modules | Collections | Artifacts |
| --- | ---: | ---: | ---: | ---: |
| Clean/full | 81.762 | 14,573 | 106 | 33,437 |
| Cached whole project | 33.817 | 14,573 | 106 | 33,437 |
| MIO family partial | 20.208 | 7 | 0 | 9,304 |
| `ai_bonus_weights` module partial | 20.202 | 1 | 0 | 9,298 |

Every installed-wheel mode completed with zero errors and diagnostics and
preserved exactly 33,436 game files, 1,215,728,316 bytes, and SHA-256
`6793927141002c51ff39f04ee9c68df0607058bb7c2009d77104581abbad7f14`.
The hidden publication marker was validated separately and excluded from the
game-file digest. The 33.817-second cached result is effectively unchanged from
the preceding installed checkpoint's 33.801 seconds, while both partial modes
improved by about three seconds.

## Next

The next performance seam is the 70-family parsed-payload decode and Python
object restoration cost, not weaker source validation. Continue the broader
GUI/PIHC3 usability objective without exposing this hidden inventory as user
metadata.
