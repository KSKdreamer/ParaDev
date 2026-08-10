# Project API Reference

Generated from `paradev.sdk.get_project_api_table()`.

Regenerate this file whenever the public `Project` object API changes:

```bash
rtk uv run paradev project-api --markdown > docs/user-manual/project-api-reference.md
```

## Summary / 汇总

- API rows / API 行数: 81
- Features / Feature 数: 8
- Row kinds / 行类型数: 3
- CLI commands / CLI 命令数: 50
- Frontend operations / 前端操作数: 61
- Inspection kinds / Inspection 类型数: 19

## Feature Index / Feature 索引

| Feature | Symbols | Project APIs |
| --- | --- | --- |
| `project-state` | 15 | `Project.root`, `Project.manifest_path`, `Project.project_id`, `Project.title`, `Project.game`, `Project.preferred_language`, `Project.source_roots`, `Project.output_root`, `Project.build_root`, `Project.extension_modules`, `Project.python_modules`, `Project.family_specs`, `Project.template_specs`, `Project.copy_roots`, `Project.descriptor_metadata` |
| `projects` | 14 | `Project.find`, `Project.create`, `Project.load`, `Project.to_view`, `Project.rename`, `Project.set_preferred_language`, `Project.read_source_text`, `Project.read_source_binary`, `Project.source_form`, `Project.plan_source_form_update`, `Project.plan_source_form_updates`, `Project.apply_source_draft`, `Project.browser`, `Project.browser_summary` |
| `modules` | 15 | `Project.rename_module`, `Project.duplicate_module`, `Project.clean_module_metadata`, `Project.set_module_collection`, `Project.set_module_active`, `Project.module_diagram`, `Project.edit_module_diagram`, `Project.remove_module`, `Project.read_module_file`, `Project.read_module_asset`, `Project.write_module_file`, `Project.write_module_files`, `Project.module_batch_edit_request`, `Project.modules`, `Project.discover_modules` |
| `authoring` | 9 | `Project.localization_workspace`, `Project.plan_localization_update`, `Project.templates`, `Project.authoring_path`, `Project.authoring_plan`, `Project.scaffold_module`, `Project.create_module`, `Project.create_modules`, `Project.create_module_draft` |
| `collections` | 8 | `Project.read_collection_file`, `Project.write_collection_file`, `Project.create_collection`, `Project.rename_collection`, `Project.remove_collection`, `Project.scaffold_collection`, `Project.collections`, `Project.discover_collections` |
| `build` | 15 | `Project.build`, `Project.summary`, `Project.manifests`, `Project.artifacts`, `Project.localization`, `Project.assets`, `Project.sources`, `Project.source_slots`, `Project.sprites`, `Project.diagnostics`, `Project.source_map`, `Project.dependencies`, `Project.build_graph`, `Project.build_explain`, `Project.families` |
| `inspections` | 2 | `Project.inspections`, `Project.inspect` |
| `catalog` | 3 | `Project.catalog_preview`, `Project.catalog_status`, `Project.catalog_query` |

## Kind Index / 行类型索引

| Kind | Symbols | Project APIs |
| --- | --- | --- |
| `field` | 15 | `Project.root`, `Project.manifest_path`, `Project.project_id`, `Project.title`, `Project.game`, `Project.preferred_language`, `Project.source_roots`, `Project.output_root`, `Project.build_root`, `Project.extension_modules`, `Project.python_modules`, `Project.family_specs`, `Project.template_specs`, `Project.copy_roots`, `Project.descriptor_metadata` |
| `classmethod` | 3 | `Project.find`, `Project.create`, `Project.load` |
| `method` | 63 | `Project.to_view`, `Project.rename`, `Project.set_preferred_language`, `Project.rename_module`, `Project.duplicate_module`, `Project.clean_module_metadata`, `Project.set_module_collection`, `Project.set_module_active`, `Project.module_diagram`, `Project.edit_module_diagram`, `Project.remove_module`, `Project.read_module_file`, `Project.read_module_asset`, `Project.write_module_file`, `Project.read_source_text`, `Project.read_source_binary`, `Project.source_form`, `Project.plan_source_form_update`, `Project.plan_source_form_updates`, `Project.localization_workspace`, `Project.plan_localization_update`, `Project.apply_source_draft`, `Project.write_module_files`, `Project.module_batch_edit_request`, `Project.read_collection_file`, `Project.write_collection_file`, `Project.create_collection`, `Project.rename_collection`, `Project.remove_collection`, `Project.templates`, `Project.authoring_path`, `Project.authoring_plan`, `Project.scaffold_module`, `Project.scaffold_collection`, `Project.create_module`, `Project.create_modules`, `Project.create_module_draft`, `Project.build`, `Project.summary`, `Project.manifests`, `Project.inspections`, `Project.inspect`, `Project.browser`, `Project.browser_summary`, `Project.catalog_preview`, `Project.catalog_status`, `Project.catalog_query`, `Project.modules`, `Project.collections`, `Project.artifacts`, `Project.localization`, `Project.assets`, `Project.sources`, `Project.source_slots`, `Project.sprites`, `Project.diagnostics`, `Project.source_map`, `Project.dependencies`, `Project.build_graph`, `Project.build_explain`, `Project.families`, `Project.discover_modules`, `Project.discover_collections` |

## CLI Command Index / CLI 命令索引

| CLI Command | Symbols | Project APIs |
| --- | --- | --- |
| `paradev project-find` | 1 | `Project.find` |
| `paradev new` | 1 | `Project.create` |
| `paradev project` | 1 | `Project.to_view` |
| `paradev project-rename` | 1 | `Project.rename` |
| `paradev project-language` | 1 | `Project.set_preferred_language` |
| `paradev module-rename` | 1 | `Project.rename_module` |
| `paradev module-duplicate` | 1 | `Project.duplicate_module` |
| `paradev module-metadata-clean` | 1 | `Project.clean_module_metadata` |
| `paradev module-collection-set` | 1 | `Project.set_module_collection` |
| `paradev module-activity-set` | 1 | `Project.set_module_active` |
| `paradev module-diagram` | 1 | `Project.module_diagram` |
| `paradev module-diagram-edit` | 1 | `Project.edit_module_diagram` |
| `paradev module-remove` | 1 | `Project.remove_module` |
| `paradev module-file` | 1 | `Project.read_module_file` |
| `paradev module-edit` | 1 | `Project.write_module_file` |
| `paradev draft-apply` | 1 | `Project.apply_source_draft` |
| `paradev module-batch-edit` | 1 | `Project.write_module_files` |
| `paradev module-batch-request` | 1 | `Project.module_batch_edit_request` |
| `paradev collection-file` | 1 | `Project.read_collection_file` |
| `paradev collection-edit` | 1 | `Project.write_collection_file` |
| `paradev collection-create` | 1 | `Project.create_collection` |
| `paradev collection-rename` | 1 | `Project.rename_collection` |
| `paradev collection-remove` | 1 | `Project.remove_collection` |
| `paradev templates` | 1 | `Project.templates` |
| `paradev authoring-path` | 1 | `Project.authoring_path` |
| `paradev authoring-plan` | 1 | `Project.authoring_plan` |
| `paradev scaffold` | 1 | `Project.scaffold_module` |
| `paradev collection-scaffold` | 1 | `Project.scaffold_collection` |
| `paradev module-batch-create` | 1 | `Project.create_modules` |
| `paradev build` | 1 | `Project.build` |
| `paradev summary` | 1 | `Project.summary` |
| `paradev manifests` | 1 | `Project.manifests` |
| `paradev inspections` | 1 | `Project.inspections` |
| `paradev project-browser` | 1 | `Project.browser` |
| `paradev hb catalog-preview` | 1 | `Project.catalog_preview` |
| `paradev hb catalog-query` | 1 | `Project.catalog_query` |
| `paradev modules` | 1 | `Project.modules` |
| `paradev collections` | 1 | `Project.collections` |
| `paradev artifacts` | 1 | `Project.artifacts` |
| `paradev localization` | 1 | `Project.localization` |
| `paradev assets` | 1 | `Project.assets` |
| `paradev sources` | 1 | `Project.sources` |
| `paradev source-slots` | 1 | `Project.source_slots` |
| `paradev sprites` | 1 | `Project.sprites` |
| `paradev diagnostics` | 1 | `Project.diagnostics` |
| `paradev source-map` | 1 | `Project.source_map` |
| `paradev dependencies` | 1 | `Project.dependencies` |
| `paradev build-graph` | 1 | `Project.build_graph` |
| `paradev build-explain` | 1 | `Project.build_explain` |
| `paradev families` | 1 | `Project.families` |

## Frontend Operation Index / 前端操作索引

| Operation | Symbols | Project APIs |
| --- | --- | --- |
| `project.find` | 1 | `Project.find` |
| `project.create` | 1 | `Project.create` |
| `project.open` | 1 | `Project.load` |
| `project.view` | 1 | `Project.to_view` |
| `project.rename` | 1 | `Project.rename` |
| `project.language` | 1 | `Project.set_preferred_language` |
| `module.rename` | 1 | `Project.rename_module` |
| `module.duplicate` | 1 | `Project.duplicate_module` |
| `module.metadata.clean` | 1 | `Project.clean_module_metadata` |
| `module.collection.set` | 1 | `Project.set_module_collection` |
| `module.activity.set` | 1 | `Project.set_module_active` |
| `module.diagram` | 1 | `Project.module_diagram` |
| `module.diagram.edit` | 1 | `Project.edit_module_diagram` |
| `module.remove` | 1 | `Project.remove_module` |
| `module.file` | 1 | `Project.read_module_file` |
| `module.edit` | 1 | `Project.write_module_file` |
| `project.source_text` | 1 | `Project.read_source_text` |
| `project.source_form` | 1 | `Project.source_form` |
| `localization.workspace` | 1 | `Project.localization_workspace` |
| `localization.plan` | 1 | `Project.plan_localization_update` |
| `project.draft_apply` | 1 | `Project.apply_source_draft` |
| `collection.file` | 1 | `Project.read_collection_file` |
| `collection.edit` | 1 | `Project.write_collection_file` |
| `collection.create` | 1 | `Project.create_collection` |
| `collection.rename` | 1 | `Project.rename_collection` |
| `collection.remove` | 1 | `Project.remove_collection` |
| `module.templates` | 1 | `Project.templates` |
| `module.authoring_path` | 1 | `Project.authoring_path` |
| `collection.authoring_path` | 1 | `Project.authoring_path` |
| `module.authoring_plan` | 1 | `Project.authoring_plan` |
| `collection.authoring_plan` | 1 | `Project.authoring_plan` |
| `module.create` | 1 | `Project.scaffold_module` |
| `collection.scaffold` | 1 | `Project.scaffold_collection` |
| `module.create_batch` | 1 | `Project.create_modules` |
| `module.draft` | 1 | `Project.create_module_draft` |
| `build.plan` | 1 | `Project.build` |
| `build.emit` | 1 | `Project.build` |
| `build.summary` | 1 | `Project.summary` |
| `build.manifests` | 1 | `Project.manifests` |
| `project.inspect` | 1 | `Project.inspect` |
| `project.browser` | 1 | `Project.browser` |
| `catalog.preview` | 1 | `Project.catalog_preview` |
| `catalog.query` | 1 | `Project.catalog_query` |
| `module.list` | 1 | `Project.modules` |
| `collection.list` | 1 | `Project.collections` |
| `collection.view` | 1 | `Project.collections` |
| `build.artifacts` | 1 | `Project.artifacts` |
| `build.localization` | 1 | `Project.localization` |
| `build.assets` | 1 | `Project.assets` |
| `module.sources` | 1 | `Project.sources` |
| `collection.sources` | 1 | `Project.sources` |
| `module.source_slots` | 1 | `Project.source_slots` |
| `collection.source_slots` | 1 | `Project.source_slots` |
| `build.sprites` | 1 | `Project.sprites` |
| `build.diagnostics` | 1 | `Project.diagnostics` |
| `build.source_map` | 1 | `Project.source_map` |
| `build.dependencies` | 1 | `Project.dependencies` |
| `build.graph` | 1 | `Project.build_graph` |
| `module.view` | 1 | `Project.build_explain` |
| `build.explain` | 1 | `Project.build_explain` |
| `build.families` | 1 | `Project.families` |

## Inspection Kind Index / Inspection 类型索引

| Inspection Kind | Symbols | Project APIs |
| --- | --- | --- |
| `summary` | 2 | `Project.summary`, `Project.inspect` |
| `manifests` | 2 | `Project.manifests`, `Project.inspect` |
| `inspections` | 2 | `Project.inspections`, `Project.inspect` |
| `assets` | 2 | `Project.inspect`, `Project.assets` |
| `artifacts` | 2 | `Project.inspect`, `Project.artifacts` |
| `build-explain` | 2 | `Project.inspect`, `Project.build_explain` |
| `build-graph` | 2 | `Project.inspect`, `Project.build_graph` |
| `catalog-preview` | 2 | `Project.inspect`, `Project.catalog_preview` |
| `catalog-query` | 2 | `Project.inspect`, `Project.catalog_query` |
| `collections` | 2 | `Project.inspect`, `Project.collections` |
| `dependencies` | 2 | `Project.inspect`, `Project.dependencies` |
| `diagnostics` | 2 | `Project.inspect`, `Project.diagnostics` |
| `families` | 2 | `Project.inspect`, `Project.families` |
| `localization` | 2 | `Project.inspect`, `Project.localization` |
| `modules` | 2 | `Project.inspect`, `Project.modules` |
| `source-map` | 2 | `Project.inspect`, `Project.source_map` |
| `source-slots` | 2 | `Project.inspect`, `Project.source_slots` |
| `sources` | 2 | `Project.inspect`, `Project.sources` |
| `sprites` | 2 | `Project.inspect`, `Project.sprites` |

## API Standard Table / API 标准表

| Symbol | Kind | Layer | Feature | Inputs | Returns | Raises | CLI Commands | Frontend Operation IDs | Inspection Kinds | Registry Seam | Surface | Doc Page | Test Anchor |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `Project.root` | `field` | `sdk` | `project-state` | `constructor` | `Path` |  |  |  |  | `none` | `sdk` | `docs/user-manual/sdk-python.md` | `tests/test_architecture.py::test_project_api_table_lists_project_object_surface` |
| `Project.manifest_path` | `field` | `sdk` | `project-state` | `constructor` | `Path` |  |  |  |  | `none` | `sdk` | `docs/user-manual/sdk-python.md` | `tests/test_architecture.py::test_project_api_table_lists_project_object_surface` |
| `Project.project_id` | `field` | `sdk` | `project-state` | `constructor` | `str` |  |  |  |  | `none` | `sdk` | `docs/user-manual/sdk-python.md` | `tests/test_architecture.py::test_project_api_table_lists_project_object_surface` |
| `Project.title` | `field` | `sdk` | `project-state` | `constructor` | `str` |  |  |  |  | `none` | `sdk` | `docs/user-manual/sdk-python.md` | `tests/test_architecture.py::test_project_api_table_lists_project_object_surface` |
| `Project.game` | `field` | `sdk` | `project-state` | `constructor` | `str` |  |  |  |  | `none` | `sdk` | `docs/user-manual/sdk-python.md` | `tests/test_architecture.py::test_project_api_table_lists_project_object_surface` |
| `Project.preferred_language` | `field` | `sdk` | `project-state` | `constructor` | `str` |  |  |  |  | `none` | `sdk` | `docs/user-manual/sdk-python.md` | `tests/test_architecture.py::test_project_api_table_lists_project_object_surface` |
| `Project.source_roots` | `field` | `sdk` | `project-state` | `constructor` | `tuple[Path, ...]` |  |  |  |  | `none` | `sdk` | `docs/user-manual/sdk-python.md` | `tests/test_architecture.py::test_project_api_table_lists_project_object_surface` |
| `Project.output_root` | `field` | `sdk` | `project-state` | `constructor` | `Path` |  |  |  |  | `none` | `sdk` | `docs/user-manual/sdk-python.md` | `tests/test_architecture.py::test_project_api_table_lists_project_object_surface` |
| `Project.build_root` | `field` | `sdk` | `project-state` | `constructor` | `Path` |  |  |  |  | `none` | `sdk` | `docs/user-manual/sdk-python.md` | `tests/test_architecture.py::test_project_api_table_lists_project_object_surface` |
| `Project.extension_modules` | `field` | `sdk` | `project-state` | `constructor` | `tuple[Path, ...]` |  |  |  |  | `none` | `sdk` | `docs/user-manual/sdk-python.md` | `tests/test_architecture.py::test_project_api_table_lists_project_object_surface` |
| `Project.python_modules` | `field` | `sdk` | `project-state` | `constructor` | `tuple[Path, ...]` |  |  |  |  | `none` | `sdk` | `docs/user-manual/sdk-python.md` | `tests/test_architecture.py::test_project_api_table_lists_project_object_surface` |
| `Project.family_specs` | `field` | `sdk` | `project-state` | `constructor` | `tuple['ProjectFamilySpec', ...]` |  |  |  |  | `none` | `sdk` | `docs/user-manual/sdk-python.md` | `tests/test_architecture.py::test_project_api_table_lists_project_object_surface` |
| `Project.template_specs` | `field` | `sdk` | `project-state` | `constructor` | `tuple[ModuleTemplate, ...]` |  |  |  |  | `none` | `sdk` | `docs/user-manual/sdk-python.md` | `tests/test_architecture.py::test_project_api_table_lists_project_object_surface` |
| `Project.copy_roots` | `field` | `sdk` | `project-state` | `constructor` | `tuple[CopyRootSpec, ...]` |  |  |  |  | `none` | `sdk` | `docs/user-manual/sdk-python.md` | `tests/test_architecture.py::test_project_api_table_lists_project_object_surface` |
| `Project.descriptor_metadata` | `field` | `sdk` | `project-state` | `constructor` | `Mapping[str, object]` |  |  |  |  | `none` | `sdk` | `docs/user-manual/sdk-python.md` | `tests/test_architecture.py::test_project_api_table_lists_project_object_surface` |
| `Project.find` | `classmethod` | `sdk` | `projects` | `path: 'str \| os.PathLike[str]' = '.'` | `dict[str, object]` | `returns diagnostics instead of raising` | `paradev project-find` | `project.find` |  | `none` | `sdk` | `docs/user-manual/sdk-python.md` | `tests/test_architecture.py::test_project_api_table_lists_project_object_surface` |
| `Project.create` | `classmethod` | `sdk` | `projects` | `path: 'str \| os.PathLike[str]', project_id: 'str \| None' = None, title: 'str \| None' = None, game: 'str' = 'hoi4', force: 'bool' = False` | `'Project'` | `ProjectCreateError` | `paradev new` | `project.create` |  | `none` | `sdk` | `docs/user-manual/sdk-python.md` | `tests/test_architecture.py::test_project_api_table_lists_project_object_surface` |
| `Project.load` | `classmethod` | `sdk` | `projects` | `path: 'str \| os.PathLike[str]' = '.', game: 'str \| None' = None, title: 'str \| None' = None` | `'Project'` | `ProjectManifestError` |  | `project.open` |  | `none` | `sdk` | `docs/user-manual/sdk-python.md` | `tests/test_architecture.py::test_project_api_table_lists_project_object_surface` |
| `Project.to_view` | `method` | `sdk` | `projects` | `none` | `dict[str, object]` |  | `paradev project` | `project.view` |  | `none` | `sdk` | `docs/user-manual/sdk-python.md` | `tests/test_architecture.py::test_project_api_table_lists_project_object_surface` |
| `Project.rename` | `method` | `sdk` | `projects` | `title: 'str'` | `'Project'` |  | `paradev project-rename` | `project.rename` |  | `none` | `sdk` | `docs/user-manual/sdk-python.md` | `tests/test_architecture.py::test_project_api_table_lists_project_object_surface` |
| `Project.set_preferred_language` | `method` | `sdk` | `projects` | `preferred_language: 'str', write: 'bool' = False, plan_hash: 'str \| None' = None` | `dict[str, object]` |  | `paradev project-language` | `project.language` |  | `none` | `sdk` | `docs/user-manual/sdk-python.md` | `tests/test_architecture.py::test_project_api_table_lists_project_object_surface` |
| `Project.rename_module` | `method` | `sdk` | `modules` | `module_id: 'str', object_id: 'str', source_root: 'str \| os.PathLike[str] \| None' = None, title: 'str \| None' = None` | `dict[str, object]` |  | `paradev module-rename` | `module.rename` |  | `project build registry` | `sdk` | `docs/user-manual/modules-and-collections.md` | `tests/test_architecture.py::test_project_api_table_lists_project_object_surface` |
| `Project.duplicate_module` | `method` | `sdk` | `modules` | `module_id: 'str', object_id: 'str', source_root: 'str \| os.PathLike[str] \| None' = None, destination_source_root: 'str \| os.PathLike[str] \| None' = None, identity: "Literal['rewrite', 'preserve']" = 'rewrite', write: 'bool' = False, plan_hash: 'str \| None' = None` | `dict[str, object]` |  | `paradev module-duplicate` | `module.duplicate` |  | `project build registry` | `sdk` | `docs/user-manual/modules-and-collections.md` | `tests/test_architecture.py::test_project_api_table_lists_project_object_surface` |
| `Project.clean_module_metadata` | `method` | `sdk` | `modules` | `family: 'str \| None' = None, module_id: 'str \| None' = None, source_root: 'str \| os.PathLike[str] \| None' = None, write: 'bool' = False, plan_hash: 'str \| None' = None` | `dict[str, object]` |  | `paradev module-metadata-clean` | `module.metadata.clean` |  | `project build registry` | `sdk` | `docs/user-manual/modules-and-collections.md` | `tests/test_architecture.py::test_project_api_table_lists_project_object_surface` |
| `Project.set_module_collection` | `method` | `sdk` | `modules` | `module_id: 'str', collection_id: 'str \| None', source_root: 'str \| os.PathLike[str] \| None' = None, write: 'bool' = False, plan_hash: 'str \| None' = None` | `dict[str, object]` |  | `paradev module-collection-set` | `module.collection.set` |  | `project build registry` | `sdk` | `docs/user-manual/modules-and-collections.md` | `tests/test_architecture.py::test_project_api_table_lists_project_object_surface` |
| `Project.set_module_active` | `method` | `sdk` | `modules` | `module_id: 'str', active: 'bool', source_root: 'str \| os.PathLike[str] \| None' = None, write: 'bool' = False, plan_hash: 'str \| None' = None` | `dict[str, object]` |  | `paradev module-activity-set` | `module.activity.set` |  | `project build registry` | `sdk` | `docs/user-manual/modules-and-collections.md` | `tests/test_architecture.py::test_project_api_table_lists_project_object_surface` |
| `Project.module_diagram` | `method` | `sdk` | `modules` | `family: 'str', profile: 'str \| None' = None` | `dict[str, object]` |  | `paradev module-diagram` | `module.diagram` |  | `project build registry` | `sdk` | `docs/user-manual/modules-and-collections.md` | `tests/test_architecture.py::test_project_api_table_lists_project_object_surface` |
| `Project.edit_module_diagram` | `method` | `sdk` | `modules` | `family: 'str', position_intents: 'Sequence[Mapping[str, object]]' = (), edge_intents: 'Sequence[Mapping[str, object]]' = (), node_intents: 'Sequence[Mapping[str, object]]' = (), profile: 'str \| None' = None, write: 'bool' = False, plan_hash: 'str \| None' = None` | `dict[str, object]` |  | `paradev module-diagram-edit` | `module.diagram.edit` |  | `project build registry` | `sdk` | `docs/user-manual/modules-and-collections.md` | `tests/test_architecture.py::test_project_api_table_lists_project_object_surface` |
| `Project.remove_module` | `method` | `sdk` | `modules` | `module_id: 'str', source_root: 'str \| os.PathLike[str] \| None' = None, write: 'bool' = False` | `dict[str, object]` |  | `paradev module-remove` | `module.remove` |  | `project build registry` | `sdk` | `docs/user-manual/modules-and-collections.md` | `tests/test_architecture.py::test_project_api_table_lists_project_object_surface` |
| `Project.read_module_file` | `method` | `sdk` | `modules` | `module_id: 'str', relative_path: 'str', source_root: 'str \| os.PathLike[str] \| None' = None, encoding: 'str' = 'utf-8'` | `dict[str, object]` |  | `paradev module-file` | `module.file` |  | `project build registry` | `sdk` | `docs/user-manual/modules-and-collections.md` | `tests/test_architecture.py::test_project_api_table_lists_project_object_surface` |
| `Project.read_module_asset` | `method` | `sdk` | `modules` | `module_id: 'str', relative_path: 'str', source_root: 'str \| os.PathLike[str] \| None' = None, include_content: 'bool' = False` | `dict[str, object]` |  |  |  |  | `project build registry` | `sdk` | `docs/user-manual/modules-and-collections.md` | `tests/test_architecture.py::test_project_api_table_lists_project_object_surface` |
| `Project.write_module_file` | `method` | `sdk` | `modules` | `module_id: 'str', relative_path: 'str', text: 'str', source_root: 'str \| os.PathLike[str] \| None' = None, create: 'bool' = False, encoding: 'str' = 'utf-8'` | `dict[str, object]` |  | `paradev module-edit` | `module.edit` |  | `project build registry` | `sdk` | `docs/user-manual/modules-and-collections.md` | `tests/test_architecture.py::test_project_api_table_lists_project_object_surface` |
| `Project.read_source_text` | `method` | `sdk` | `projects` | `source_path: 'str \| os.PathLike[str]'` | `dict[str, object]` |  |  | `project.source_text` |  | `none` | `sdk` | `docs/user-manual/sdk-python.md` | `tests/test_architecture.py::test_project_api_table_lists_project_object_surface` |
| `Project.read_source_binary` | `method` | `sdk` | `projects` | `source_path: 'str \| os.PathLike[str]', include_content: 'bool' = True` | `dict[str, object]` |  |  |  |  | `none` | `sdk` | `docs/user-manual/sdk-python.md` | `tests/test_architecture.py::test_project_api_table_lists_project_object_surface` |
| `Project.source_form` | `method` | `sdk` | `projects` | `source_path: 'str \| os.PathLike[str]', text: 'str \| None' = None, query: 'str \| None' = None` | `dict[str, object] \| None` |  |  | `project.source_form` |  | `none` | `sdk` | `docs/user-manual/sdk-python.md` | `tests/test_architecture.py::test_project_api_table_lists_project_object_surface` |
| `Project.plan_source_form_update` | `method` | `sdk` | `projects` | `source_path: 'str \| os.PathLike[str]', values: 'Mapping[str, object]', text: 'str \| None' = None, query: 'str \| None' = None` | `dict[str, object]` |  |  |  |  | `none` | `sdk` | `docs/user-manual/sdk-python.md` | `tests/test_architecture.py::test_project_api_table_lists_project_object_surface` |
| `Project.plan_source_form_updates` | `method` | `sdk` | `projects` | `updates: 'Sequence[Mapping[str, object]]'` | `dict[str, object]` |  |  |  |  | `none` | `sdk` | `docs/user-manual/sdk-python.md` | `tests/test_architecture.py::test_project_api_table_lists_project_object_surface` |
| `Project.localization_workspace` | `method` | `sdk` | `authoring` | `target_id: 'str', target_kind: "Literal['module', 'collection']" = 'module', family: 'str \| None' = None, source_root: 'str \| os.PathLike[str] \| None' = None, drafts: 'Mapping[str, str] \| None' = None, limit: 'int' = 512` | `dict[str, object]` |  |  | `localization.workspace` |  | `project build registry` | `sdk` | `docs/user-manual/modules-and-collections.md` | `tests/test_architecture.py::test_project_api_table_lists_project_object_surface` |
| `Project.plan_localization_update` | `method` | `sdk` | `authoring` | `target_id: 'str', operation: 'Mapping[str, object]', target_kind: "Literal['module', 'collection']" = 'module', family: 'str \| None' = None, source_root: 'str \| os.PathLike[str] \| None' = None, drafts: 'Mapping[str, str] \| None' = None, limit: 'int' = 512` | `dict[str, object]` |  |  | `localization.plan` |  | `project build registry` | `sdk` | `docs/user-manual/modules-and-collections.md` | `tests/test_architecture.py::test_project_api_table_lists_project_object_surface` |
| `Project.apply_source_draft` | `method` | `sdk` | `projects` | `source_edits: 'object' = None, source_removals: 'object' = None, source_replacements: 'object' = None, module_rename: 'object' = None` | `dict[str, object]` |  | `paradev draft-apply` | `project.draft_apply` |  | `none` | `sdk` | `docs/user-manual/sdk-python.md` | `tests/test_architecture.py::test_project_api_table_lists_project_object_surface` |
| `Project.write_module_files` | `method` | `sdk` | `modules` | `edits: 'Sequence[Mapping[str, object]]', create: 'bool' = False, encoding: 'str' = 'utf-8', write: 'bool' = True` | `dict[str, object]` |  | `paradev module-batch-edit` |  |  | `project build registry` | `sdk` | `docs/user-manual/modules-and-collections.md` | `tests/test_architecture.py::test_project_api_table_lists_project_object_surface` |
| `Project.module_batch_edit_request` | `method` | `sdk` | `modules` | `edits: 'Sequence[Mapping[str, object]]', create: 'bool' = False, encoding: 'str' = 'utf-8'` | `dict[str, object]` |  | `paradev module-batch-request` |  |  | `project build registry` | `sdk` | `docs/user-manual/modules-and-collections.md` | `tests/test_architecture.py::test_project_api_table_lists_project_object_surface` |
| `Project.read_collection_file` | `method` | `sdk` | `collections` | `collection_id: 'str', relative_path: 'str', family: 'str \| None' = None, source_root: 'str \| os.PathLike[str] \| None' = None, encoding: 'str' = 'utf-8'` | `dict[str, object]` |  | `paradev collection-file` | `collection.file` |  | `project build registry` | `sdk` | `docs/user-manual/modules-and-collections.md` | `tests/test_architecture.py::test_project_api_table_lists_project_object_surface` |
| `Project.write_collection_file` | `method` | `sdk` | `collections` | `collection_id: 'str', relative_path: 'str', text: 'str', family: 'str \| None' = None, source_root: 'str \| os.PathLike[str] \| None' = None, create: 'bool' = False, encoding: 'str' = 'utf-8'` | `dict[str, object]` |  | `paradev collection-edit` | `collection.edit` |  | `project build registry` | `sdk` | `docs/user-manual/modules-and-collections.md` | `tests/test_architecture.py::test_project_api_table_lists_project_object_surface` |
| `Project.create_collection` | `method` | `sdk` | `collections` | `family: 'str', collection_id: 'str', source_root: 'str \| os.PathLike[str] \| None' = None, metadata: 'Mapping[str, object] \| None' = None, write: 'bool' = False, force: 'bool' = False` | `dict[str, object]` |  | `paradev collection-create` | `collection.create` |  | `project build registry` | `sdk` | `docs/user-manual/modules-and-collections.md` | `tests/test_architecture.py::test_project_api_table_lists_project_object_surface` |
| `Project.rename_collection` | `method` | `sdk` | `collections` | `collection_id: 'str', target_id: 'str', family: 'str \| None' = None, source_root: 'str \| os.PathLike[str] \| None' = None` | `dict[str, object]` |  | `paradev collection-rename` | `collection.rename` |  | `project build registry` | `sdk` | `docs/user-manual/modules-and-collections.md` | `tests/test_architecture.py::test_project_api_table_lists_project_object_surface` |
| `Project.remove_collection` | `method` | `sdk` | `collections` | `collection_id: 'str', family: 'str \| None' = None, source_root: 'str \| os.PathLike[str] \| None' = None, write: 'bool' = False, plan_hash: 'str \| None' = None` | `dict[str, object]` |  | `paradev collection-remove` | `collection.remove` |  | `project build registry` | `sdk` | `docs/user-manual/modules-and-collections.md` | `tests/test_architecture.py::test_project_api_table_lists_project_object_surface` |
| `Project.templates` | `method` | `sdk` | `authoring` | `template_id: 'str \| None' = None, family: 'str \| None' = None, kind: "Literal['module', 'collection'] \| None" = None, source: 'str \| None' = None, authoring_ready: 'bool \| None' = None, diagnostic_code: 'str \| None' = None` | `dict[str, object]` |  | `paradev templates` | `module.templates` |  | `project build registry` | `sdk` | `docs/user-manual/modules-and-collections.md` | `tests/test_architecture.py::test_project_api_table_lists_project_object_surface` |
| `Project.authoring_path` | `method` | `sdk` | `authoring` | `kind: 'str', family: 'str', target_id: 'str', source_root: 'str \| os.PathLike[str] \| None' = None` | `dict[str, object]` |  | `paradev authoring-path` | `module.authoring_path`, `collection.authoring_path` |  | `project build registry` | `sdk` | `docs/user-manual/modules-and-collections.md` | `tests/test_architecture.py::test_project_api_table_lists_project_object_surface` |
| `Project.authoring_plan` | `method` | `sdk` | `authoring` | `kind: 'str', family: 'str', target_id: 'str', source_root: 'str \| os.PathLike[str] \| None' = None, profile: 'str \| None' = None, registry: "'BuildRegistry \| None'" = None` | `dict[str, object]` |  | `paradev authoring-plan` | `module.authoring_plan`, `collection.authoring_plan` |  | `project build registry` | `sdk` | `docs/user-manual/modules-and-collections.md` | `tests/test_architecture.py::test_project_api_table_lists_project_object_surface` |
| `Project.scaffold_module` | `method` | `sdk` | `authoring` | `template_id: 'str', object_id: 'str', source_root: 'str \| os.PathLike[str] \| None' = None, values: 'Mapping[str, object] \| None' = None, write: 'bool' = False, force: 'bool' = False` | `dict[str, object]` |  | `paradev scaffold` | `module.create` |  | `project build registry` | `sdk` | `docs/user-manual/modules-and-collections.md` | `tests/test_architecture.py::test_project_api_table_lists_project_object_surface` |
| `Project.scaffold_collection` | `method` | `sdk` | `collections` | `template_id: 'str', collection_id: 'str', source_root: 'str \| os.PathLike[str] \| None' = None, values: 'Mapping[str, object] \| None' = None, write: 'bool' = False, force: 'bool' = False, plan_hash: 'str \| None' = None` | `dict[str, object]` |  | `paradev collection-scaffold` | `collection.scaffold` |  | `project build registry` | `sdk` | `docs/user-manual/modules-and-collections.md` | `tests/test_architecture.py::test_project_api_table_lists_project_object_surface` |
| `Project.create_module` | `method` | `sdk` | `authoring` | `family_or_template: 'str', object_id: 'str', values: 'Mapping[str, object] \| None' = None, write: 'bool' = True, force: 'bool' = False` | `dict[str, object]` |  |  |  |  | `project build registry` | `sdk` | `docs/user-manual/modules-and-collections.md` | `tests/test_architecture.py::test_project_api_table_lists_project_object_surface` |
| `Project.create_modules` | `method` | `sdk` | `authoring` | `modules: 'Sequence[Mapping[str, object]]', source_root: 'str \| os.PathLike[str] \| None' = None, write: 'bool' = False, plan_hash: 'str \| None' = None` | `dict[str, object]` |  | `paradev module-batch-create` | `module.create_batch` |  | `project build registry` | `sdk` | `docs/user-manual/modules-and-collections.md` | `tests/test_architecture.py::test_project_api_table_lists_project_object_surface` |
| `Project.create_module_draft` | `method` | `sdk` | `authoring` | `family_id: 'str', object_id: 'str', template_id: 'str \| None' = None, values: 'Mapping[str, object] \| None' = None, write: 'bool' = False, force: 'bool' = False` | `dict[str, object]` |  |  | `module.draft` |  | `project build registry` | `sdk` | `docs/user-manual/modules-and-collections.md` | `tests/test_architecture.py::test_project_api_table_lists_project_object_surface` |
| `Project.build` | `method` | `sdk` | `build` | `profile: 'str \| None' = None, registry: "'BuildRegistry \| None'" = None, modules: "tuple['Module', ...]" = (), collections: "tuple['Collection', ...]" = (), diagnostics: "tuple['Diagnostic', ...]" = (), emit_artifacts: 'bool' = False, emit_manifests: 'bool' = False, family: 'str \| None' = None, module_id: 'str \| None' = None, collection_id: 'str \| None' = None, full_rebuild: 'bool' = False, sync_launcher_descriptor: 'bool' = True, parallelism: 'int \| None' = None, strict_metadata: 'bool \| str \| None' = None, progress: 'Callable[[dict[str, object]], None] \| None' = None` | `'BuildResult'` |  | `paradev build` | `build.plan`, `build.emit` |  | `project build registry` | `sdk` | `docs/user-manual/build-and-diagnostics.md` | `tests/test_architecture.py::test_project_api_table_lists_project_object_surface` |
| `Project.summary` | `method` | `sdk` | `build` | `profile: 'str \| None' = None, registry: "'BuildRegistry \| None'" = None` | `dict[str, object]` |  | `paradev summary` | `build.summary` | `summary` | `project build registry` | `sdk` | `docs/user-manual/project-inspection-reference.md` | `tests/test_architecture.py::test_project_api_table_lists_project_object_surface` |
| `Project.manifests` | `method` | `sdk` | `build` | `profile: 'str \| None' = None, registry: "'BuildRegistry \| None'" = None` | `dict[str, object]` |  | `paradev manifests` | `build.manifests` | `manifests` | `project build registry` | `sdk` | `docs/user-manual/project-inspection-reference.md` | `tests/test_architecture.py::test_project_api_table_lists_project_object_surface` |
| `Project.inspections` | `method` | `sdk` | `inspections` | `none` | `dict[str, object]` |  | `paradev inspections` |  | `inspections` | `Project inspection dispatcher` | `sdk` | `docs/user-manual/project-inspection-reference.md` | `tests/test_architecture.py::test_project_api_table_lists_project_object_surface` |
| `Project.inspect` | `method` | `sdk` | `inspections` | `kind: 'str', **filters: 'object'` | `dict[str, object]` |  |  | `project.inspect` | `inspections`, `assets`, `artifacts`, `build-explain`, `build-graph`, `catalog-preview`, `catalog-query`, `collections`, `dependencies`, `diagnostics`, `families`, `localization`, `manifests`, `modules`, `source-map`, `source-slots`, `sources`, `sprites`, `summary` | `Project inspection dispatcher` | `sdk` | `docs/user-manual/project-inspection-reference.md` | `tests/test_architecture.py::test_project_api_table_lists_project_object_surface` |
| `Project.browser` | `method` | `sdk` | `projects` | `profile: 'str \| None' = None, registry: "'BuildRegistry \| None'" = None, kind: 'str \| None' = None, family: 'str \| None' = None, module_id: 'str \| None' = None, collection_id: 'str \| None' = None` | `dict[str, object]` |  | `paradev project-browser` | `project.browser` |  | `none` | `sdk` | `docs/user-manual/sdk-python.md` | `tests/test_architecture.py::test_project_api_table_lists_project_object_surface` |
| `Project.browser_summary` | `method` | `sdk` | `projects` | `profile: 'str \| None' = None, registry: "'BuildRegistry \| None'" = None, kind: 'str \| None' = None, family: 'str \| None' = None` | `dict[str, object]` |  |  |  |  | `none` | `sdk` | `docs/user-manual/sdk-python.md` | `tests/test_architecture.py::test_project_api_table_lists_project_object_surface` |
| `Project.catalog_preview` | `method` | `sdk` | `catalog` | `profile: 'str \| None' = None, registry: "'BuildRegistry \| None'" = None` | `dict[str, object]` |  | `paradev hb catalog-preview` | `catalog.preview` | `catalog-preview` | `HeavenBase catalog registry` | `sdk` | `docs/user-manual/project-inspection-reference.md` | `tests/test_architecture.py::test_project_api_table_lists_project_object_surface` |
| `Project.catalog_status` | `method` | `sdk` | `catalog` | `database: 'str \| Path \| None' = None` | `dict[str, object]` |  |  |  |  | `HeavenBase catalog registry` | `sdk` | `docs/user-manual/build-and-diagnostics.md` | `tests/test_architecture.py::test_project_api_table_lists_project_object_surface` |
| `Project.catalog_query` | `method` | `sdk` | `catalog` | `database: 'str \| Path \| None' = None, entity: 'str \| None' = None, target_id: 'str \| None' = None, name: 'str \| None' = None, tag: 'str \| None' = None, limit: 'int \| None' = None, offset: 'int' = 0, include_data: 'bool' = True` | `dict[str, object]` |  | `paradev hb catalog-query` | `catalog.query` | `catalog-query` | `HeavenBase catalog registry` | `sdk` | `docs/user-manual/project-inspection-reference.md` | `tests/test_architecture.py::test_project_api_table_lists_project_object_surface` |
| `Project.modules` | `method` | `sdk` | `modules` | `profile: 'str \| None' = None, registry: "'BuildRegistry \| None'" = None, family: 'str \| None' = None, module_id: 'str \| None' = None, collection_id: 'str \| None' = None, source_slot: 'str \| None' = None` | `dict[str, object]` |  | `paradev modules` | `module.list` | `modules` | `project build registry` | `sdk` | `docs/user-manual/project-inspection-reference.md` | `tests/test_architecture.py::test_project_api_table_lists_project_object_surface` |
| `Project.collections` | `method` | `sdk` | `collections` | `profile: 'str \| None' = None, registry: "'BuildRegistry \| None'" = None, family: 'str \| None' = None, collection_id: 'str \| None' = None, module_id: 'str \| None' = None, source_slot: 'str \| None' = None` | `dict[str, object]` |  | `paradev collections` | `collection.list`, `collection.view` | `collections` | `project build registry` | `sdk` | `docs/user-manual/project-inspection-reference.md` | `tests/test_architecture.py::test_project_api_table_lists_project_object_surface` |
| `Project.artifacts` | `method` | `sdk` | `build` | `profile: 'str \| None' = None, registry: "'BuildRegistry \| None'" = None, artifact_type: 'str \| None' = None, target_root: 'str \| None' = None, owner: 'str \| None' = None, path: 'str \| None' = None, mode: 'str \| None' = None, module_id: 'str \| None' = None, collection_id: 'str \| None' = None` | `dict[str, object]` |  | `paradev artifacts` | `build.artifacts` | `artifacts` | `project build registry` | `sdk` | `docs/user-manual/project-inspection-reference.md` | `tests/test_architecture.py::test_project_api_table_lists_project_object_surface` |
| `Project.localization` | `method` | `sdk` | `build` | `profile: 'str \| None' = None, registry: "'BuildRegistry \| None'" = None, language: 'str \| None' = None, key: 'str \| None' = None, key_prefix: 'str \| None' = None, module_id: 'str \| None' = None, collection_id: 'str \| None' = None` | `dict[str, object]` |  | `paradev localization` | `build.localization` | `localization` | `project build registry` | `sdk` | `docs/user-manual/project-inspection-reference.md` | `tests/test_architecture.py::test_project_api_table_lists_project_object_surface` |
| `Project.assets` | `method` | `sdk` | `build` | `profile: 'str \| None' = None, registry: "'BuildRegistry \| None'" = None, module_id: 'str \| None' = None, collection_id: 'str \| None' = None, family: 'str \| None' = None, slot: 'str \| None' = None, file_format: 'str \| None' = None` | `dict[str, object]` |  | `paradev assets` | `build.assets` | `assets` | `project build registry` | `sdk` | `docs/user-manual/project-inspection-reference.md` | `tests/test_architecture.py::test_project_api_table_lists_project_object_surface` |
| `Project.sources` | `method` | `sdk` | `build` | `profile: 'str \| None' = None, registry: "'BuildRegistry \| None'" = None, family: 'str \| None' = None, module_id: 'str \| None' = None, collection_id: 'str \| None' = None, slot: 'str \| None' = None, loader: 'str \| None' = None, status: 'str \| None' = None, owner_kind: 'str \| None' = None` | `dict[str, object]` |  | `paradev sources` | `module.sources`, `collection.sources` | `sources` | `project build registry` | `sdk` | `docs/user-manual/project-inspection-reference.md` | `tests/test_architecture.py::test_project_api_table_lists_project_object_surface` |
| `Project.source_slots` | `method` | `sdk` | `build` | `profile: 'str \| None' = None, registry: "'BuildRegistry \| None'" = None, family: 'str \| None' = None, module_id: 'str \| None' = None, collection_id: 'str \| None' = None, slot: 'str \| None' = None, status: 'str \| None' = None` | `dict[str, object]` |  | `paradev source-slots` | `module.source_slots`, `collection.source_slots` | `source-slots` | `project build registry` | `sdk` | `docs/user-manual/project-inspection-reference.md` | `tests/test_architecture.py::test_project_api_table_lists_project_object_surface` |
| `Project.sprites` | `method` | `sdk` | `build` | `profile: 'str \| None' = None, registry: "'BuildRegistry \| None'" = None, module_id: 'str \| None' = None, collection_id: 'str \| None' = None, family: 'str \| None' = None, slot: 'str \| None' = None, name: 'str \| None' = None` | `dict[str, object]` |  | `paradev sprites` | `build.sprites` | `sprites` | `project build registry` | `sdk` | `docs/user-manual/project-inspection-reference.md` | `tests/test_architecture.py::test_project_api_table_lists_project_object_surface` |
| `Project.diagnostics` | `method` | `sdk` | `build` | `profile: 'str \| None' = None, registry: "'BuildRegistry \| None'" = None, severity: 'str \| None' = None, code: 'str \| None' = None, family: 'str \| None' = None, owner: 'str \| None' = None, target_root: 'str \| None' = None, module_id: 'str \| None' = None, collection_id: 'str \| None' = None, source_path: 'str \| None' = None, slot: 'str \| None' = None, strict_metadata: 'bool \| str \| None' = None, published: 'bool \| str' = False` | `dict[str, object]` |  | `paradev diagnostics` | `build.diagnostics` | `diagnostics` | `project build registry` | `sdk` | `docs/user-manual/project-inspection-reference.md` | `tests/test_architecture.py::test_project_api_table_lists_project_object_surface` |
| `Project.source_map` | `method` | `sdk` | `build` | `profile: 'str \| None' = None, registry: "'BuildRegistry \| None'" = None, module_id: 'str \| None' = None, collection_id: 'str \| None' = None, family: 'str \| None' = None, slot: 'str \| None' = None, artifact_type: 'str \| None' = None, target_root: 'str \| None' = None` | `dict[str, object]` |  | `paradev source-map` | `build.source_map` | `source-map` | `project build registry` | `sdk` | `docs/user-manual/project-inspection-reference.md` | `tests/test_architecture.py::test_project_api_table_lists_project_object_surface` |
| `Project.dependencies` | `method` | `sdk` | `build` | `profile: 'str \| None' = None, registry: "'BuildRegistry \| None'" = None, source: 'str \| None' = None, target: 'str \| None' = None, kind: 'str \| None' = None, module_id: 'str \| None' = None` | `dict[str, object]` |  | `paradev dependencies` | `build.dependencies` | `dependencies` | `project build registry` | `sdk` | `docs/user-manual/project-inspection-reference.md` | `tests/test_architecture.py::test_project_api_table_lists_project_object_surface` |
| `Project.build_graph` | `method` | `sdk` | `build` | `profile: 'str \| None' = None, registry: "'BuildRegistry \| None'" = None, module_id: 'str \| None' = None, collection_id: 'str \| None' = None, family: 'str \| None' = None, slot: 'str \| None' = None, artifact_type: 'str \| None' = None, target_root: 'str \| None' = None, edge_kind: 'str \| None' = None` | `dict[str, object]` |  | `paradev build-graph` | `build.graph` | `build-graph` | `project build registry` | `sdk` | `docs/user-manual/project-inspection-reference.md` | `tests/test_architecture.py::test_project_api_table_lists_project_object_surface` |
| `Project.build_explain` | `method` | `sdk` | `build` | `module_id: 'str \| None' = None, collection_id: 'str \| None' = None, source_path: 'str \| os.PathLike[str] \| None' = None, artifact_path: 'str \| None' = None, diagnostic_code: 'str \| None' = None, target_root: 'str \| None' = None, profile: 'str \| None' = None, registry: "'BuildRegistry \| None'" = None` | `dict[str, object]` |  | `paradev build-explain` | `module.view`, `build.explain` | `build-explain` | `project build registry` | `sdk` | `docs/user-manual/project-inspection-reference.md` | `tests/test_architecture.py::test_project_api_table_lists_project_object_surface` |
| `Project.families` | `method` | `sdk` | `build` | `profile: 'str \| None' = None, registry: "'BuildRegistry \| None'" = None, family: 'str \| None' = None, kind: 'str \| None' = None, source_slot: 'str \| None' = None, collection_source_slot: 'str \| None' = None, sprite_slot: 'str \| None' = None, route: 'str \| None' = None, artifact_type: 'str \| None' = None` | `dict[str, object]` |  | `paradev families` | `build.families` | `families` | `project build registry` | `sdk` | `docs/user-manual/project-inspection-reference.md` | `tests/test_architecture.py::test_project_api_table_lists_project_object_surface` |
| `Project.discover_modules` | `method` | `sdk` | `modules` | `profile: 'str \| None' = None, registry: "'BuildRegistry \| None'" = None, strict_metadata: 'bool \| str \| None' = None, family: 'str \| None' = None, module_id: 'str \| None' = None, collection_id: 'str \| None' = None` | `'ModuleDiscoveryResult'` |  |  |  |  | `project build registry` | `sdk` | `docs/user-manual/modules-and-collections.md` | `tests/test_architecture.py::test_project_api_table_lists_project_object_surface` |
| `Project.discover_collections` | `method` | `sdk` | `collections` | `profile: 'str \| None' = None, registry: "'BuildRegistry \| None'" = None, strict_metadata: 'bool \| str \| None' = None, family: 'str \| None' = None, collection_id: 'str \| None' = None, module_id: 'str \| None' = None` | `'CollectionDiscoveryResult'` |  |  |  |  | `project build registry` | `sdk` | `docs/user-manual/modules-and-collections.md` | `tests/test_architecture.py::test_project_api_table_lists_project_object_surface` |
