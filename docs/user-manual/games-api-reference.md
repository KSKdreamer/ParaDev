# Games API Reference

Generated from `paradev.games.get_games_api_table()`.

Regenerate this file whenever the public `paradev.games` facade changes:

```bash
rtk uv run paradev games-api --markdown > docs/user-manual/games-api-reference.md
```

## Summary / 汇总

- API rows / API 行数: 8
- Games modules / Games 模块数: 2
- Features / Feature 数: 2
- Row kinds / 行类型数: 4

## Module Index / 模块索引

| Module | Symbols | Public Exports |
| --- | --- | --- |
| `games` | 2 | `PROFILE_REGISTRIES`, `registry_for_profile` |
| `games.api` | 6 | `GAMES_API_TABLE_SCHEMA`, `GamesApiRow`, `GamesApiTable`, `get_games_api_selection`, `get_games_api_table`, `render_games_api_reference_markdown` |

## Feature Index / Feature 索引

| Feature | Symbols | Public Exports |
| --- | --- | --- |
| `profiles` | 2 | `PROFILE_REGISTRIES`, `registry_for_profile` |
| `games-api` | 6 | `GAMES_API_TABLE_SCHEMA`, `GamesApiRow`, `GamesApiTable`, `get_games_api_selection`, `get_games_api_table`, `render_games_api_reference_markdown` |

## Kind Index / 行类型索引

| Kind | Symbols | Public Exports |
| --- | --- | --- |
| `dict constant` | 1 | `PROFILE_REGISTRIES` |
| `function` | 4 | `registry_for_profile`, `get_games_api_selection`, `get_games_api_table`, `render_games_api_reference_markdown` |
| `schema constant` | 1 | `GAMES_API_TABLE_SCHEMA` |
| `TypedDict` | 2 | `GamesApiRow`, `GamesApiTable` |

## API Standard Table / API 标准表

| Symbol | Kind | Layer | Module | Feature | Import Path | Returns | Value | Registry Seam | Surface | Doc Page | Test Anchor |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `PROFILE_REGISTRIES` | `dict constant` | `games` | `games` | `profiles` | `paradev.games.PROFILE_REGISTRIES` | `dict[1]` | hoi4 | `game profile registry` | `sdk` | `docs/user-manual/games-api-reference.md` | `tests/test_architecture.py::test_games_api_table_lists_public_games_facade` |
| `registry_for_profile` | `function` | `games` | `games` | `profiles` | `paradev.games.registry_for_profile` | `BuildRegistry` |  | `game profile registry` | `sdk` | `docs/user-manual/games-api-reference.md` | `tests/test_architecture.py::test_games_api_table_lists_public_games_facade` |
| `GAMES_API_TABLE_SCHEMA` | `schema constant` | `games` | `games.api` | `games-api` | `paradev.games.GAMES_API_TABLE_SCHEMA` | `paradev.games.api-table.v1` | paradev.games.api-table.v1 | `games facade API table` | `sdk` | `docs/user-manual/games-api-reference.md` | `tests/test_architecture.py::test_games_api_table_lists_public_games_facade` |
| `GamesApiRow` | `TypedDict` | `games` | `games.api` | `games-api` | `paradev.games.GamesApiRow` | `TypedDict schema` |  | `games facade API table` | `sdk` | `docs/user-manual/games-api-reference.md` | `tests/test_architecture.py::test_games_api_table_lists_public_games_facade` |
| `GamesApiTable` | `TypedDict` | `games` | `games.api` | `games-api` | `paradev.games.GamesApiTable` | `TypedDict schema` |  | `games facade API table` | `sdk` | `docs/user-manual/games-api-reference.md` | `tests/test_architecture.py::test_games_api_table_lists_public_games_facade` |
| `get_games_api_selection` | `function` | `games` | `games.api` | `games-api` | `paradev.games.get_games_api_selection` | `GamesApiTable \| GamesApiRow \| list[str]` |  | `games facade API table` | `sdk` | `docs/user-manual/games-api-reference.md` | `tests/test_architecture.py::test_games_api_table_lists_public_games_facade` |
| `get_games_api_table` | `function` | `games` | `games.api` | `games-api` | `paradev.games.get_games_api_table` | `GamesApiTable` |  | `games facade API table` | `sdk` | `docs/user-manual/games-api-reference.md` | `tests/test_architecture.py::test_games_api_table_lists_public_games_facade` |
| `render_games_api_reference_markdown` | `function` | `games` | `games.api` | `games-api` | `paradev.games.render_games_api_reference_markdown` | `str` |  | `games facade API table` | `sdk` | `docs/user-manual/games-api-reference.md` | `tests/test_architecture.py::test_games_api_table_lists_public_games_facade` |
