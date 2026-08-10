# Getting Started

## English

Use ParaDev from this repository through `rtk` and `uv`:

```bash
rtk bash scripts/sync-env.bash
rtk uv run paradev --help
rtk uv run paradev --version
```

Create a starter HoI4 project:

```bash
rtk uv run paradev new projects/starter-mod --title "Starter Mod" --json
```

That command creates:

- `projects/starter-mod/paradev.yaml`
- `projects/starter-mod/src/modules/modifier/starter_mod_starter_modifier/`
- the default HoI4 output root, `~/Documents/Paradox Interactive/Hearts of Iron IV/mod/starter_mod/` on macOS
- `projects/starter-mod/.paradev/.cache/build/`

Build it:

```bash
rtk uv run paradev build projects/starter-mod --emit-artifacts --emit-manifests --json
```

The emitted starter output includes `<output_root>/descriptor.mod`, starter modifier files under `<output_root>/common/` and `<output_root>/localisation/`, and a launcher preview at `projects/starter-mod/.paradev/.cache/build/launcher/starter_mod.mod`. When the output root is inside the HoI4 user mod folder, ParaDev also writes `starter_mod.mod` beside it for the launcher. Set `output_root: build/mod` in `paradev.yaml` when you want project-local generated output instead.

Inspect the committed demo project:

```bash
rtk uv run paradev project demos/assets/projects/minimal --json
rtk uv run paradev summary demos/assets/projects/minimal --json
rtk uv run paradev families demos/assets/projects/minimal --json
rtk uv run paradev modules demos/assets/projects/minimal --json
rtk uv run paradev artifacts demos/assets/projects/minimal --json
```

List projects known to the local SDK and inspect the desktop project state used by GUI shells:

```bash
rtk uv run paradev projects --root demos/assets/projects --json
rtk uv run paradev desktop-state --project demos/assets/projects/minimal --root demos/assets/projects --json
rtk uv run paradev project-browser demos/assets/projects/minimal --json
```

`families` also returns an `authoring` block with valid source roots plus the canonical `modules/{family}/{object_id}` and `collections/{family}/{collection_id}` folder templates. Family rows include `metadata.common_keys`, `metadata.family_keys`, and `metadata.unknown_key_policy` so tools can explain accepted `meta.yaml` fields and loose-versus-strict unknown-key behavior. They also include `outputs`, so tools can see planned artifact types, owner scope, target root, and route or sprite-slot context without parsing template keys. Its `index` maps family ids, compiler kinds, source slots, routes, sprite slots, output artifact types, and writer types to returned rows, which is useful when a GUI, importer, MCP tool, or script needs one contract quickly. Use `authoring-path` to resolve one module or collection folder without creating files; use `authoring-plan` when the UI or script also needs to show the files that family expects and whether each expected slot is currently `empty`, `missing`, `satisfied`, or `diagnostic`:

```bash
rtk uv run paradev families demos/assets/projects/minimal --family idea --source-slot icon --artifact-type sprite_gfx --json
rtk uv run paradev authoring-path projects/starter-mod module idea GER_industry_spirit --json
rtk uv run paradev authoring-plan projects/starter-mod module idea GER_industry_spirit --json
```

List authoring templates and add a module to an existing project:

```bash
rtk uv run paradev templates projects/starter-mod --json
rtk uv run paradev scaffold projects/starter-mod hoi4:idea/basic GER_industry_spirit \
  --value "title=German Industry Spirit" \
  --value "description=Industrial production spirit." \
  --json
rtk uv run paradev scaffold projects/starter-mod hoi4:idea/basic GER_industry_spirit \
  --value "title=German Industry Spirit" \
  --value "description=Industrial production spirit." \
  --write \
  --json
```

`scaffold` returns a JSON plan first and only writes source files when `--write` is present. The plan nests `authoring_plan`, so the same response shows the files ParaDev will write and the current status of the expected source slots. The `templates` payload lists valid source roots and marks the default root.
If a project has more than one `source_roots` entry, add `--source-root imports` or another configured root to place the module outside the first source root.

Parse one PDX source without running a project build:

```bash
rtk uv run paradev parse demos/assets/projects/minimal/src/modules/focus/GER_sample/def.txt --json
rtk uv run paradev parse demos/assets/projects/minimal/src/modules/focus/GER_sample/def.txt --tokens --json
```

Use `--json` whenever a script, GUI, MCP tool, or test needs stable machine-readable output. Add `--tokens` only when a parser, editor, or importer integration needs the lexer token rows with source line and column spans.

## 中文

在本仓库里通过 `rtk` 和 `uv` 使用 ParaDev：

```bash
rtk bash scripts/sync-env.bash
rtk uv run paradev --help
rtk uv run paradev --version
```

创建一个 HoI4 起步项目：

```bash
rtk uv run paradev new projects/starter-mod --title "Starter Mod" --json
```

这个命令会创建：

- `projects/starter-mod/paradev.yaml`
- `projects/starter-mod/src/modules/modifier/starter_mod_starter_modifier/`
- 默认 HoI4 输出目录；macOS 上是 `~/Documents/Paradox Interactive/Hearts of Iron IV/mod/starter_mod/`
- `projects/starter-mod/.paradev/.cache/build/`

运行构建：

```bash
rtk uv run paradev build projects/starter-mod --emit-artifacts --emit-manifests --json
```

输出后的起步项目会包含 `<output_root>/descriptor.mod`，`<output_root>/common/` 与 `<output_root>/localisation/` 下的起步 modifier 文件，以及 `projects/starter-mod/.paradev/.cache/build/launcher/starter_mod.mod` 这个 launcher 预览。当输出目录位于 HoI4 用户 Mod 目录内时，ParaDev 也会在旁边写入 `starter_mod.mod` 供启动器使用。如果需要项目内本地输出，可以在 `paradev.yaml` 中显式设置 `output_root: build/mod`。

查看仓库自带的演示项目：

```bash
rtk uv run paradev project demos/assets/projects/minimal --json
rtk uv run paradev summary demos/assets/projects/minimal --json
rtk uv run paradev families demos/assets/projects/minimal --json
rtk uv run paradev modules demos/assets/projects/minimal --json
rtk uv run paradev artifacts demos/assets/projects/minimal --json
```

列出本地 SDK 已知项目，并查看 GUI shell 使用的桌面项目状态：

```bash
rtk uv run paradev projects --root demos/assets/projects --json
rtk uv run paradev desktop-state --project demos/assets/projects/minimal --root demos/assets/projects --json
rtk uv run paradev project-browser demos/assets/projects/minimal --json
```

`families` 还会返回 `authoring` 区块，包含可用源目录，以及标准的 `modules/{family}/{object_id}` 和 `collections/{family}/{collection_id}` 目录模板。Family 行包含 `metadata.common_keys`、`metadata.family_keys` 和 `metadata.unknown_key_policy`，工具可以解释 `meta.yaml` 接受哪些字段，以及未知字段在 loose/strict 模式下的行为。它也包含 `outputs`，工具可以直接看到计划 artifact 类型、owner 范围、target root，以及 route 或 sprite-slot 上下文，不需要解析 template key。它的 `index` 会把 family id、编译器种类、源 slot、route、sprite slot、output artifact type 和 writer 类型映射到返回的行，方便 GUI、导入器、MCP 工具或脚本快速找到某个 contract。使用 `authoring-path` 可以在不创建文件的情况下解析单个模块或集合目录；如果界面或脚本还需要展示该 family 期望哪些文件，以及每个期望 slot 当前是 `empty`、`missing`、`satisfied` 还是 `diagnostic`，使用 `authoring-plan`：

```bash
rtk uv run paradev families demos/assets/projects/minimal --family idea --source-slot icon --artifact-type sprite_gfx --json
rtk uv run paradev authoring-path projects/starter-mod module idea GER_industry_spirit --json
rtk uv run paradev authoring-plan projects/starter-mod module idea GER_industry_spirit --json
```

列出创建模板，并向已有项目添加一个模块：

```bash
rtk uv run paradev templates projects/starter-mod --json
rtk uv run paradev scaffold projects/starter-mod hoi4:idea/basic GER_industry_spirit \
  --value "title=German Industry Spirit" \
  --value "description=Industrial production spirit." \
  --json
rtk uv run paradev scaffold projects/starter-mod hoi4:idea/basic GER_industry_spirit \
  --value "title=German Industry Spirit" \
  --value "description=Industrial production spirit." \
  --write \
  --json
```

`scaffold` 会先返回 JSON plan，只有传入 `--write` 时才会写入源文件。这个 plan 会嵌套 `authoring_plan`，所以同一个响应既能展示 ParaDev 准备写哪些文件，也能展示期望 source slot 当前的状态。`templates` payload 会列出可用源目录，并标记默认源目录。
如果项目有多个 `source_roots`，可以添加 `--source-root imports` 或其他已配置源目录，把模块写到第一个源目录之外。

不运行项目构建，只解析一个 PDX 源文件：

```bash
rtk uv run paradev parse demos/assets/projects/minimal/src/modules/focus/GER_sample/def.txt --json
rtk uv run paradev parse demos/assets/projects/minimal/src/modules/focus/GER_sample/def.txt --tokens --json
```

脚本、GUI、MCP 工具或测试需要稳定机器可读输出时，都建议加 `--json`。只有 parser、编辑器或导入器集成需要带源码行列号的 lexer token rows 时，才额外加 `--tokens`。
