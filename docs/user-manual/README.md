# ParaDev User Manual

Status: alpha manual interface

Audience: HoI4 modders who are comfortable with basic CLI commands and light Python. You should not need to read ParaDev internals or HOI4DEV code to start, inspect, build, or continue a small project.

## English

ParaDev is currently an alpha Python SDK and CLI for compiling feature-oriented Paradox mod source folders into game-style output folders. The first target is Hearts of Iron IV.

Start here:

| Page | Use it for |
| --- | --- |
| [Install ParaDev And Build PIHC3](install-pihc3-desktop.md) | Install the desktop candidate, verify and import the PIHC3 companion ZIP in-app, run all four build modes, and launch the generated mod. |
| [Getting Started](getting-started.md) | Create a starter project, inspect the demo project, and run the first build. |
| [Project Layout](project-layout.md) | Understand `paradev.yaml`, source roots, output roots, build roots, and generated files. |
| [Modules And Collections](modules-and-collections.md) | Learn how modules, collections, source slots, and artifacts map to HoI4 files. |
| [Build And Diagnostics](build-and-diagnostics.md) | Run dry builds, emit outputs, inspect manifests, and fix diagnostics. |
| [Python SDK](sdk-python.md) | Use `Project.create(...)`, `Project.load(...)`, template scaffolding, build results, and inspection payloads from Python. |
| [API Catalog Reference](api-catalog-reference.md) | Read the generated overall catalog of API reference tables, schemas, owner modules, surfaces, regeneration commands, and doc pages. |
| [Package API Reference](package-api-reference.md) | Read the generated root `paradev` facade table for package-level imports. |
| [Config API Reference](config-api-reference.md) | Read the generated public `paradev.config` facade table for config defaults, `CM_PARADEV`, and config-reference helper exports. |
| [GUI API Reference](gui-api-reference.md) | Read the generated public `paradev.gui` launcher facade table for the installed `paradev-gui` parser and entry point. |
| [Desktop API Reference](desktop-api-reference.md) | Read the generated public `paradev.desktop` facade table for desktop state, local source/cache/config helpers, build command planning, HOI4 launch, and path openers. |
| [Games API Reference](games-api-reference.md) | Read the generated public `paradev.games` facade table for game profile registry helpers. |
| [Surfaces API Reference](surfaces-api-reference.md) | Read the generated `paradev.surfaces` facade table for CLI, REST, MCP, LSP, VS Code, bundle, and surface contract helpers. |
| [SDK API Reference](sdk-api-reference.md) | Read the generated public `paradev.sdk` facade table grouped by module, feature, and symbol kind. |
| [Project API Reference](project-api-reference.md) | Read the generated public `Project` object table grouped by feature, row kind, CLI command, frontend operation, and inspection kind. |
| [Authoring Templates API Reference](templates-api-reference.md) | Read the generated SDK authoring-template module table for template schemas, dataclasses, registry helpers, and scaffold planning. |
| [Copy Roots API Reference](copy-roots-api-reference.md) | Read the generated SDK copy-root module table for compatibility overlay target roots, manifest parsing, copied artifact generation, and shadow diagnostics. |
| [Project Facade API Reference](project-facade-api-reference.md) | Read the generated public `paradev.project` facade table for project package imports and facade helper exports. |
| [Localization API Reference](localization-api-reference.md) | Read the generated public `paradev.localization` facade table for HOI4 language alias normalization helpers. |
| [Build API Reference](build-api-reference.md) | Read the generated public `paradev.build` facade table for records, families, slots, loaders, manifests, views, and writers. |
| [Architecture API Reference](architecture-api-reference.md) | Read the generated API-standard table for architecture graph SDK, CLI, REST, and MCP entry points. |
| [PDX API Reference](pdx-api-reference.md) | Read the generated parse/format API table for PDX SDK, CLI, REST, and MCP entry points. |
| [PDX Core API Reference](pdx-core-api-reference.md) | Read the generated public `paradev.pdx` facade table for tokenizer, AST, parser, diagnostics, scalar constants, and Markdown reference helpers. |
| [LSP API Reference](lsp-api-reference.md) | Read the generated editor API table for LSP SDK, CLI, REST, and JSON-RPC entry points. |
| [LSP Server API Reference](lsp-server-api-reference.md) | Read the generated public `paradev.lsp` facade table for stdio server, JSON-RPC dispatcher, document cache, framing, and reference helpers. |
| [Catalog API Reference](catalog-api-reference.md) | Read the generated HeavenBase catalog API table for SDK, CLI, REST, MCP, and completion entry points. |
| [HeavenBase Facade API Reference](hb-api-reference.md) | Read the generated public `paradev.hb` facade table grouped by module, feature, and symbol kind. |
| [REST API Reference](rest-api-reference.md) | Read the generated REST/OpenAPI route table and frontend operation reverse index. |
| [REST Facade API Reference](rest-facade-api-reference.md) | Read the generated public `paradev.api` facade table for local API server, OpenAPI seed, source text, and draft helper exports. |
| [MCP API Reference](mcp-api-reference.md) | Read the generated MCP tool table, read/write mode index, and frontend operation reverse index. |
| [CLI API Reference](cli-api-reference.md) | Read the generated CLI command, adapter, projection, and frontend operation reverse-index table. |
| [SDK And CLI API Reference](sdk-cli-reference.md) | Read the generated compact operation matrix for Python SDK calls and CLI commands. |
| [Project Inspection Reference](project-inspection-reference.md) | Read the generated inspection kind, filter, and reverse-index table for `Project.inspect(...)`. |
| [Frontend API Contract](frontend-api.md) | See the maintained SDK/CLI/REST/MCP/LSP operation list for GUI, importer, and desktop clients. |
| [Frontend API Reference](frontend-api-reference.md) | Read the generated full operation table derived from the SDK contract. |
| [Surface Contract Reference](surface-contract-reference.md) | Read the generated static adapter contract table for CLI, MCP, REST/OpenAPI, LSP, VS Code, and bundling. |
| [Developer Manual](developer-manual.md) | Extend ParaDev with families, slots, project-local declarations, and tests. |
| [PIHC3](pihc3.md) | Understand the PIHC3 migration status and how to continue once the skeleton exists. |
| [Troubleshooting](troubleshooting.md) | Diagnose environment, manifest, parser, build, and output problems. |

First working commands:

```bash
rtk uv run paradev new projects/starter-mod --title "Starter Mod" --json
rtk uv run paradev templates projects/starter-mod --json
rtk uv run paradev authoring-plan projects/starter-mod module idea GER_industry_spirit --json
rtk uv run paradev build projects/starter-mod --emit-artifacts --emit-manifests --json
rtk uv run paradev projects --root demos/assets/projects --json
rtk uv run paradev desktop-state --project demos/assets/projects/minimal --root demos/assets/projects --json
rtk uv run paradev project-browser demos/assets/projects/minimal --json
rtk uv run paradev summary demos/assets/projects/minimal --json
rtk uv run paradev diagnostics demos/assets/projects/minimal --json
rtk uv run paradev source-slots demos/assets/projects/minimal --json
```

First Python check:

```python
from paradev.sdk import Project

project = Project.create("projects/starter-mod", title="Starter Mod")
result = project.build(emit_artifacts=True, emit_manifests=True)
print(result.summary())
```

Alpha limits: ParaDev can parse PDX, discover projects, compile PIHC3, emit artifacts/manifests, generate and install launcher descriptors, and inspect build records. Signed/notarized desktop distribution, clean-machine Windows acceptance, complete focus-tree layout writeback, map authoring, workshop packaging, and some guided editors remain in progress.

## 中文

ParaDev 目前是一个 alpha 阶段的 Python SDK 和 CLI，用来把按功能组织的 Paradox Mod 源目录编译成接近游戏目录结构的输出。当前优先支持 Hearts of Iron IV。

建议按这个顺序阅读：

| 页面 | 用途 |
| --- | --- |
| [安装 ParaDev 并构建 PIHC3](install-pihc3-desktop.md) | 安装桌面候选包，在应用内验证并导入 PIHC3 配套 ZIP，执行四种构建模式，并启动生成的 Mod。 |
| [快速开始](getting-started.md) | 创建起步项目，查看演示项目，运行第一次构建。 |
| [项目结构](project-layout.md) | 理解 `paradev.yaml`、源目录、输出目录、构建目录和生成文件。 |
| [模块与集合](modules-and-collections.md) | 理解模块、集合、源槽位和 artifact 如何对应到 HoI4 文件。 |
| [构建与诊断](build-and-diagnostics.md) | 运行 dry build、输出文件、查看 manifests、修复 diagnostics。 |
| [Python SDK](sdk-python.md) | 在 Python 中使用 `Project.create(...)`、`Project.load(...)`、模板创建、构建结果和检查接口。 |
| [API Catalog Reference](api-catalog-reference.md) | 阅读生成版 API reference 总目录，覆盖 schema、owner module、surface、重新生成命令和文档页面。 |
| [Package API Reference](package-api-reference.md) | 阅读生成版根 `paradev` facade 表，覆盖 package-level import。 |
| [Config API Reference](config-api-reference.md) | 阅读生成版 `paradev.config` 公开 facade 表，覆盖 config default、`CM_PARADEV` 和 config reference helper export。 |
| [GUI API Reference](gui-api-reference.md) | 阅读生成版 `paradev.gui` 公开 launcher facade 表，覆盖已安装的 `paradev-gui` parser 和入口。 |
| [Desktop API Reference](desktop-api-reference.md) | 阅读生成版 `paradev.desktop` 公开 facade 表，覆盖 desktop state、本地 source/cache/config helper、build 命令规划、HOI4 启动和路径打开器。 |
| [Games API Reference](games-api-reference.md) | 阅读生成版 `paradev.games` 公开 facade 表，覆盖 game profile registry helper。 |
| [Surfaces API Reference](surfaces-api-reference.md) | 阅读生成版 `paradev.surfaces` facade 表，覆盖 CLI、REST、MCP、LSP、VS Code、bundle 和 surface contract helpers。 |
| [SDK API Reference](sdk-api-reference.md) | 阅读生成版 `paradev.sdk` 公开 facade 表，按 module、feature 和 symbol kind 分组。 |
| [Project API Reference](project-api-reference.md) | 阅读生成版 `Project` 对象公开表，按 feature、row kind、CLI command、frontend operation 和 inspection kind 分组。 |
| [Authoring Templates API Reference](templates-api-reference.md) | 阅读生成版 SDK authoring-template module 表，覆盖 template schema、dataclass、registry helper 和 scaffold planning。 |
| [Copy Roots API Reference](copy-roots-api-reference.md) | 阅读生成版 SDK copy-root module 表，覆盖 compatibility overlay 的 target root、manifest 解析、复制 artifact 生成和 shadow diagnostic。 |
| [Project Facade API Reference](project-facade-api-reference.md) | 阅读生成版 `paradev.project` 公开 facade 表，覆盖 project package import 和 facade helper export。 |
| [Localization API Reference](localization-api-reference.md) | 阅读生成版 `paradev.localization` 公开 facade 表，覆盖 HOI4 language alias normalization helper。 |
| [Build API Reference](build-api-reference.md) | 阅读生成版 `paradev.build` 公开 facade 表，覆盖 record、family、slot、loader、manifest、view 和 writer。 |
| [Architecture API Reference](architecture-api-reference.md) | 阅读生成版 architecture graph API 标准表，覆盖 SDK、CLI、REST 和 MCP 入口。 |
| [PDX API Reference](pdx-api-reference.md) | 阅读生成版 PDX parse/format API 标准表，覆盖 SDK、CLI、REST 和 MCP 入口。 |
| [PDX Core API Reference](pdx-core-api-reference.md) | 阅读生成版 `paradev.pdx` 公开 facade 表，覆盖 tokenizer、AST、parser、diagnostics、scalar constants 和 Markdown reference helper。 |
| [LSP API Reference](lsp-api-reference.md) | 阅读生成版编辑器 API 标准表，覆盖 LSP SDK、CLI、REST 和 JSON-RPC 入口。 |
| [LSP Server API Reference](lsp-server-api-reference.md) | 阅读生成版 `paradev.lsp` 公开 facade 表，覆盖 stdio server、JSON-RPC dispatcher、document cache、framing 和 reference helper。 |
| [Catalog API Reference](catalog-api-reference.md) | 阅读生成版 HeavenBase catalog API 标准表，覆盖 SDK、CLI、REST、MCP 和 completion 入口。 |
| [HeavenBase Facade API Reference](hb-api-reference.md) | 阅读生成版 `paradev.hb` 公开 facade 表，按 module、feature 和 symbol kind 分组。 |
| [REST API Reference](rest-api-reference.md) | 阅读生成版 REST/OpenAPI route 标准表和 frontend operation 反向索引。 |
| [REST Facade API Reference](rest-facade-api-reference.md) | 阅读生成版 `paradev.api` 公开 facade 表，覆盖 local API server、OpenAPI seed、source text 和 draft helper export。 |
| [MCP API Reference](mcp-api-reference.md) | 阅读生成版 MCP tool 标准表、读写模式索引和 frontend operation 反向索引。 |
| [CLI API Reference](cli-api-reference.md) | 阅读生成版 CLI command、adapter、projection 和 frontend operation 反向索引表。 |
| [SDK 与 CLI API Reference](sdk-cli-reference.md) | 阅读由 SDK contract 生成的 Python SDK 调用和 CLI 命令紧凑矩阵。 |
| [Project Inspection Reference](project-inspection-reference.md) | 阅读生成版 `Project.inspect(...)` inspection kind、filter 和反向索引表。 |
| [前端 API Contract](frontend-api.md) | 查看给 GUI、导入器和桌面端使用的 SDK/CLI/REST/MCP/LSP 操作清单。 |
| [前端 API Reference](frontend-api-reference.md) | 阅读由 SDK contract 派生的完整操作表。 |
| [Surface Contract Reference](surface-contract-reference.md) | 阅读生成版静态 adapter contract 表，覆盖 CLI、MCP、REST/OpenAPI、LSP、VS Code 和 bundle。 |
| [开发者手册](developer-manual.md) | 扩展 family、slot、项目本地声明和测试。 |
| [PIHC3](pihc3.md) | 了解 PIHC3 迁移状态，以及骨架项目完成后如何继续。 |
| [故障排查](troubleshooting.md) | 处理环境、manifest、parser、build 和输出问题。 |

第一组可用命令：

```bash
rtk uv run paradev new projects/starter-mod --title "Starter Mod" --json
rtk uv run paradev templates projects/starter-mod --json
rtk uv run paradev authoring-plan projects/starter-mod module idea GER_industry_spirit --json
rtk uv run paradev build projects/starter-mod --emit-artifacts --emit-manifests --json
rtk uv run paradev projects --root demos/assets/projects --json
rtk uv run paradev desktop-state --project demos/assets/projects/minimal --root demos/assets/projects --json
rtk uv run paradev project-browser demos/assets/projects/minimal --json
rtk uv run paradev summary demos/assets/projects/minimal --json
rtk uv run paradev diagnostics demos/assets/projects/minimal --json
rtk uv run paradev source-slots demos/assets/projects/minimal --json
```

第一段 Python 检查：

```python
from paradev.sdk import Project

project = Project.create("projects/starter-mod", title="Starter Mod")
result = project.build(emit_artifacts=True, emit_manifests=True)
print(result.summary())
```

Alpha 限制：ParaDev 已经能解析 PDX、发现并编译 PIHC3、输出 artifacts/manifests、生成和安装 launcher descriptor，并检查构建记录。签名/公证后的桌面发行版、Windows 干净机器验收、完整国策树布局写回、地图创作、创意工坊发布和部分引导式编辑器仍在开发中。

## Maintenance Rule

Every public CLI or SDK workflow added to ParaDev should update this manual, or explicitly record why it remains internal-only.

## 维护规则

每次 ParaDev 增加公开 CLI 或 SDK 工作流时，都应该更新本手册；如果某个能力仍然只是内部接口，也要明确记录原因。
