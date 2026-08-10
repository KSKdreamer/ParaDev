# Project Inspection Reference

Generated from `paradev.sdk.get_project_inspection_contract()`.

Regenerate this file whenever the project inspection contract changes:

```bash
rtk uv run paradev inspections --markdown > docs/user-manual/project-inspection-reference.md
```

## Summary / 汇总

- Inspections / Inspection 数: 19
- Filters / Filter 数: 40

## Index Catalog / Index 目录

| Index | Contract Path | Python Helper | Use |
| --- | --- | --- | --- |
| `kind` | `contract["index"]["kind"][kind]` | `get_project_inspection_selection(kind=kind)` | Inspection kind to compact inspection row offset. |
| `filter` | `contract["index"]["filter"][filter_name]` | `get_project_inspection_selection(index_name="filter", key=filter_name)` | Filter name to inspection kinds that accept it. |

## Inspection Kinds / Inspection Kind 表

| Kind | SDK Method | CLI Command | Filters |
| --- | --- | --- | --- |
| `inspections` | `Project.inspections` | `inspections` |  |
| `assets` | `Project.assets` | `assets` | `profile`, `module_id`, `collection_id`, `family`, `slot`, `file_format` |
| `artifacts` | `Project.artifacts` | `artifacts` | `profile`, `artifact_type`, `target_root`, `owner`, `path`, `mode`, `module_id`, `collection_id` |
| `build-explain` | `Project.build_explain` | `build-explain` | `module_id`, `collection_id`, `source_path`, `artifact_path`, `diagnostic_code`, `target_root`, `profile` |
| `build-graph` | `Project.build_graph` | `build-graph` | `profile`, `module_id`, `collection_id`, `family`, `slot`, `artifact_type`, `target_root`, `edge_kind` |
| `catalog-preview` | `Project.catalog_preview` | `hb catalog-preview` | `profile` |
| `catalog-query` | `Project.catalog_query` | `hb catalog-query` | `database`, `entity`, `target_id`, `name`, `tag`, `limit`, `offset`, `include_data` |
| `collections` | `Project.collections` | `collections` | `profile`, `family`, `collection_id`, `module_id`, `source_slot` |
| `dependencies` | `Project.dependencies` | `dependencies` | `profile`, `source`, `target`, `kind`, `module_id` |
| `diagnostics` | `Project.diagnostics` | `diagnostics` | `profile`, `severity`, `code`, `family`, `owner`, `target_root`, `module_id`, `collection_id`, `source_path`, `slot`, `strict_metadata`, `published` |
| `families` | `Project.families` | `families` | `profile`, `family`, `kind`, `source_slot`, `collection_source_slot`, `sprite_slot`, `route`, `artifact_type` |
| `localization` | `Project.localization` | `localization` | `profile`, `language`, `key`, `key_prefix`, `module_id`, `collection_id` |
| `manifests` | `Project.manifests` | `manifests` | `profile` |
| `modules` | `Project.modules` | `modules` | `profile`, `family`, `module_id`, `collection_id`, `source_slot` |
| `source-map` | `Project.source_map` | `source-map` | `profile`, `module_id`, `collection_id`, `family`, `slot`, `artifact_type`, `target_root` |
| `source-slots` | `Project.source_slots` | `source-slots` | `profile`, `family`, `module_id`, `collection_id`, `slot`, `status` |
| `sources` | `Project.sources` | `sources` | `profile`, `family`, `module_id`, `collection_id`, `slot`, `loader`, `status`, `owner_kind` |
| `sprites` | `Project.sprites` | `sprites` | `profile`, `module_id`, `collection_id`, `family`, `slot`, `name` |
| `summary` | `Project.summary` | `summary` | `profile` |

## Filter Index / Filter 索引

| Filter | Inspections | Kinds |
| --- | --- | --- |
| `profile` | 17 | `assets`, `artifacts`, `build-explain`, `build-graph`, `catalog-preview`, `collections`, `dependencies`, `diagnostics`, `families`, `localization`, `manifests`, `modules`, `source-map`, `source-slots`, `sources`, `sprites`, `summary` |
| `module_id` | 13 | `assets`, `artifacts`, `build-explain`, `build-graph`, `collections`, `dependencies`, `diagnostics`, `localization`, `modules`, `source-map`, `source-slots`, `sources`, `sprites` |
| `collection_id` | 12 | `assets`, `artifacts`, `build-explain`, `build-graph`, `collections`, `diagnostics`, `localization`, `modules`, `source-map`, `source-slots`, `sources`, `sprites` |
| `family` | 10 | `assets`, `build-graph`, `collections`, `diagnostics`, `families`, `modules`, `source-map`, `source-slots`, `sources`, `sprites` |
| `slot` | 7 | `assets`, `build-graph`, `diagnostics`, `source-map`, `source-slots`, `sources`, `sprites` |
| `file_format` | 1 | `assets` |
| `artifact_type` | 4 | `artifacts`, `build-graph`, `families`, `source-map` |
| `target_root` | 5 | `artifacts`, `build-explain`, `build-graph`, `diagnostics`, `source-map` |
| `owner` | 2 | `artifacts`, `diagnostics` |
| `path` | 1 | `artifacts` |
| `mode` | 1 | `artifacts` |
| `source_path` | 2 | `build-explain`, `diagnostics` |
| `artifact_path` | 1 | `build-explain` |
| `diagnostic_code` | 1 | `build-explain` |
| `edge_kind` | 1 | `build-graph` |
| `database` | 1 | `catalog-query` |
| `entity` | 1 | `catalog-query` |
| `target_id` | 1 | `catalog-query` |
| `name` | 2 | `catalog-query`, `sprites` |
| `tag` | 1 | `catalog-query` |
| `limit` | 1 | `catalog-query` |
| `offset` | 1 | `catalog-query` |
| `include_data` | 1 | `catalog-query` |
| `source_slot` | 3 | `collections`, `families`, `modules` |
| `source` | 1 | `dependencies` |
| `target` | 1 | `dependencies` |
| `kind` | 2 | `dependencies`, `families` |
| `severity` | 1 | `diagnostics` |
| `code` | 1 | `diagnostics` |
| `strict_metadata` | 1 | `diagnostics` |
| `published` | 1 | `diagnostics` |
| `collection_source_slot` | 1 | `families` |
| `sprite_slot` | 1 | `families` |
| `route` | 1 | `families` |
| `language` | 1 | `localization` |
| `key` | 1 | `localization` |
| `key_prefix` | 1 | `localization` |
| `status` | 2 | `source-slots`, `sources` |
| `loader` | 1 | `sources` |
| `owner_kind` | 1 | `sources` |
