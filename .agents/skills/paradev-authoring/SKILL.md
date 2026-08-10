---
name: paradev-authoring
description: Safely discover, create, edit, localize, duplicate, group, or diagram ParaDev and PIHC3 modules and collections through Registry-backed MCP contracts, stable source revisions, and transactional apply. Use for natural-language content authoring, especially multi-module creation, collection or tree work, localization, image replacement, or existing-source edits that must preserve simple metadata, canonical folder identity, and exact plan/apply safety.
---

# ParaDev Authoring

Use ParaDev's canonical authoring contract. Do not synthesize system metadata,
infer source paths, or write module files outside the SDK transaction.

## MCP Surface

Use the ParaDev authoring tools already attached by the host. When configuring
an MCP client, register `paradev mcp serve` as a local stdio server. Its bounded
runtime exposes template/path/plan discovery, filtered `project_browser`,
stable `module_file` and `collection_file` reads, bounded Registry-owned
`module_asset` inspection,
Registry-owned guided source forms and update plans,
guarded batch creation and draft apply, collection scaffolding, duplication,
metadata cleanup, and Registry-backed diagram read/edit tools. Do not infer
support for contract-table tools that the runtime does not advertise.

## Create Modules

1. Locate the project from the path supplied by the user. Never guess a
   different project when loading fails.
2. Discover authoring-ready templates with the read-only
   `project_templates` MCP tool. Filter by family when known and select one
   exact `template_id`. If MCP is unavailable, use:

   ```bash
   paradev templates PROJECT --family FAMILY --authoring-ready --json
   ```

3. Read the selected template's `args`, defaults, descriptions, and generated
   file list. Convert human units only when the template defines their
   semantics. For PIHC3 idea factors and an example batch, read
   [references/pihc3-ideas.md](references/pihc3-ideas.md). For PIHC3 content
   routing, collections, and tree families, read
   [references/pihc3-authoring.md](references/pihc3-authoring.md).
4. Build one ordered request row per module. Supply `object_id`,
   `template_id`, and only meaningful `values`. Do not pass `family` or
   `family_or_template` in the same row as `template_id`.
5. Call `project_create_modules` with `write=false`. Treat the returned
   `paradev.sdk.module_batch.v1` payload as the review boundary.
6. Review every planned module, target path, count, and diagnostic. Do not
   apply a blocked plan. Do not silently rename object ids or discard a row.
7. If the user asked to create the modules, call the same tool with the exact
   same project path, module rows, and source root, setting `write=true` and
   passing the plan's exact `plan_hash`. If the user asked only to preview,
   return the plan without applying it.
8. If the hash is stale, make a fresh dry plan and review the changed result;
   never retry with a fabricated or old hash. ParaDev intentionally has no
   force mode.

## Create Collections

1. Discover an authoring-ready collection template with `project_templates`
   using `kind="collection"` and the narrowest known family. Read its live
   arguments and files; do not adapt a module template by hand.
2. Call `collection_scaffold` with `write=false`, the exact `template_id`,
   `collection_id`, and meaningful `values`. Keep `force=false`.
3. Review its canonical folder, files, source-slot plan, diagnostics, and
   `plan_hash`. To create it, repeat the same request with `write=true` and the
   exact hash. Never overwrite a divergent collection.
4. Add or clear same-family membership through `module_collection_set`: plan
   first, review the complete membership change, then apply the identical
   request with its exact hash.

For collection localization, call `localization_workspace` with
`target_kind="collection"`, its `target_id`, and family when needed. Plan a
closed `set`, `add`, `rename`, or `remove` operation with `localization_plan`,
then pass its guarded `source_edits` unchanged to `project_draft_apply`.

## Edit Existing Modules

1. Call `project_browser` with the narrowest known `family`, `module_id`, or
   `collection_id`. Use its Registry-owned source slots and paths; do not guess
   filenames from the family name.
2. For each supported Registry-owned JSON or PDX source, call
   `module_source_form`. Select values by the returned control ids; never invent
   ids or infer them from source text.
3. Plan one guided source with `module_source_form_update`, or plan several with
   one `module_source_form_update_batch` call. Review every returned change and
   `source_edit`. Unchanged rows are intentionally omitted from the combined
   `source_edits` list.
4. Call `project_draft_apply` once with the reviewed `source_edits` when the
   plan reports `changed=true`. This applies all related guided changes as one
   revision-guarded transaction.
5. When a source has no guided form, read it with `module_file`, retain its
   `relative_path`, `size`, and `mtime_ns`, and make the smallest exact source
   edit. Preserve unrelated PDX, localization, comments, and module-local
   resources. Include those fallback edits in the same `project_draft_apply`
   call with `expected_size` and `expected_mtime_ns` from the stable snapshot.
   Include `module_rename` in that transaction when logical identity or the
   readable folder title changes.
6. For an image or copied resource, use the exact path exposed by the browser
   slot and call `module_asset` with content omitted first. Verify the returned
   `source_slots`, digest, and `draft_guard`. Request base64 only when the old
   bytes are needed. Replace the resource by passing the guard unchanged with
   the new `content_base64` in `source_replacements` in the same
   `project_draft_apply` call. For supported image conversion, also pass the
   paired `content_format` and `target_format` fields.
7. If ParaDev reports that a source changed after it was opened, reread it,
   reconcile the external edit, and submit a new guarded draft. Never retry
   without revisions or overwrite the external content.

For an existing collection, locate it with `project_browser(kind="collection")`.
Read an exact browser-owned text source with `collection_file`, preserve its
`size` and `mtime_ns`, and submit the smallest replacement through
`project_draft_apply`. Use the generic localization workflow above for `.loc`
sources. Do not infer a collection filename or bypass the guarded transaction.

For Focus, Technology, Doctrine, or MIO graph changes, read `module_diagram`
first. Submit bounded intents to `module_diagram_edit` with `write=false`,
review the exact plan, then apply it with the current `plan_hash`. Discover
provider-owned node fields from `browser.families[].diagram.node_authoring`;
Focus, MIO, and project-local graph Entities use this same Registry route.

## Verify

Verify each created or edited module with a strict targeted dry build:

```bash
paradev build PROJECT --module FAMILY/OBJECT_ID --strict-metadata --json
```

Emit artifacts only when the user asks for build output.

## Failure Handling

- Surface diagnostic codes, module indexes, and messages together.
- On `module_batch.rollback_incomplete`, preserve and report `recovery_path`.
  Do not delete, rewrite, or automatically replay retained recovery data.
- On any source-draft recovery error, preserve and report the trusted
  `<project>/.paradev/source-draft-transaction` folder. Do not delete or replay
  it manually.
- On an existing divergent module, stop and ask whether the user wants a
  separate edit workflow. Batch creation never overwrites source.
- Treat a fresh apply that reports every row unchanged as a successful
  idempotent no-op.

## Source Integrity

- The folder supplies `family/object_id`. Do not create `meta.yaml` unless the
  selected live template produces it; keep any visible metadata limited to
  user-facing fields from that template.
- Keep definition, localization, and instance assets in the same module when
  its family supports those slots.
- Treat `module_asset.source_slots` as the ownership source of truth. Do not
  recreate `_component` or `_asset_component` folders or infer an asset path.
- Prefer one precise batch over repeated single-module writes so the request
  is reviewed and applied as one protected operation.
