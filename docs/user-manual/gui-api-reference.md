# GUI API Reference

Generated from `paradev.gui.get_gui_api_table()`.

Regenerate this file whenever the public `paradev.gui` launcher facade changes:

```bash
rtk uv run paradev gui-api --markdown > docs/user-manual/gui-api-reference.md
```

## Summary / 汇总

- API rows / API 行数: 8
- GUI modules / GUI 模块数: 2
- Features / Feature 数: 2
- Row kinds / 行类型数: 3

## Module Index / 模块索引

| Module | Symbols | Public Exports |
| --- | --- | --- |
| `gui` | 2 | `build_parser`, `main` |
| `gui_api` | 6 | `GUI_API_TABLE_SCHEMA`, `GuiApiRow`, `GuiApiTable`, `get_gui_api_selection`, `get_gui_api_table`, `render_gui_api_reference_markdown` |

## Feature Index / Feature 索引

| Feature | Symbols | Public Exports |
| --- | --- | --- |
| `launcher` | 2 | `build_parser`, `main` |
| `gui-api` | 6 | `GUI_API_TABLE_SCHEMA`, `GuiApiRow`, `GuiApiTable`, `get_gui_api_selection`, `get_gui_api_table`, `render_gui_api_reference_markdown` |

## Kind Index / 行类型索引

| Kind | Symbols | Public Exports |
| --- | --- | --- |
| `function` | 5 | `build_parser`, `main`, `get_gui_api_selection`, `get_gui_api_table`, `render_gui_api_reference_markdown` |
| `schema constant` | 1 | `GUI_API_TABLE_SCHEMA` |
| `TypedDict` | 2 | `GuiApiRow`, `GuiApiTable` |

## API Standard Table / API 标准表

| Symbol | Kind | Layer | Module | Feature | Import Path | Returns | Value | Registry Seam | Surface | Doc Page | Test Anchor |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `build_parser` | `function` | `gui` | `gui` | `launcher` | `paradev.gui.build_parser` | `argparse.ArgumentParser` |  | `Python GUI script entry point` | `desktop` | `docs/user-manual/gui-api-reference.md` | `tests/test_architecture.py::test_gui_api_table_lists_public_gui_facade` |
| `main` | `function` | `gui` | `gui` | `launcher` | `paradev.gui.main` | `int` |  | `Python GUI script entry point` | `desktop` | `docs/user-manual/gui-api-reference.md` | `tests/test_architecture.py::test_gui_api_table_lists_public_gui_facade` |
| `GUI_API_TABLE_SCHEMA` | `schema constant` | `gui` | `gui_api` | `gui-api` | `paradev.gui.GUI_API_TABLE_SCHEMA` | `paradev.gui.api-table.v1` | `paradev.gui.api-table.v1` | `GUI facade API table` | `sdk` | `docs/user-manual/gui-api-reference.md` | `tests/test_architecture.py::test_gui_api_table_lists_public_gui_facade` |
| `GuiApiRow` | `TypedDict` | `gui` | `gui_api` | `gui-api` | `paradev.gui.GuiApiRow` | `TypedDict schema` |  | `GUI facade API table` | `sdk` | `docs/user-manual/gui-api-reference.md` | `tests/test_architecture.py::test_gui_api_table_lists_public_gui_facade` |
| `GuiApiTable` | `TypedDict` | `gui` | `gui_api` | `gui-api` | `paradev.gui.GuiApiTable` | `TypedDict schema` |  | `GUI facade API table` | `sdk` | `docs/user-manual/gui-api-reference.md` | `tests/test_architecture.py::test_gui_api_table_lists_public_gui_facade` |
| `get_gui_api_selection` | `function` | `gui` | `gui_api` | `gui-api` | `paradev.gui.get_gui_api_selection` | `GuiApiTable \| GuiApiRow \| list[str]` |  | `GUI facade API table` | `sdk` | `docs/user-manual/gui-api-reference.md` | `tests/test_architecture.py::test_gui_api_table_lists_public_gui_facade` |
| `get_gui_api_table` | `function` | `gui` | `gui_api` | `gui-api` | `paradev.gui.get_gui_api_table` | `GuiApiTable` |  | `GUI facade API table` | `sdk` | `docs/user-manual/gui-api-reference.md` | `tests/test_architecture.py::test_gui_api_table_lists_public_gui_facade` |
| `render_gui_api_reference_markdown` | `function` | `gui` | `gui_api` | `gui-api` | `paradev.gui.render_gui_api_reference_markdown` | `str` |  | `GUI facade API table` | `sdk` | `docs/user-manual/gui-api-reference.md` | `tests/test_architecture.py::test_gui_api_table_lists_public_gui_facade` |
