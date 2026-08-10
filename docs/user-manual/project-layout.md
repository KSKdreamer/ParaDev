# Project Layout

## English

A ParaDev project is a folder with `paradev.yaml`.

Minimal manifest:

```yaml
project_id: starter_mod
title: Starter Mod
game: hoi4
source_roots: [src]
build_root: .paradev/.cache/build
```

Main paths:

| Path | Meaning |
| --- | --- |
| `src/` | Authored source. Keep this in Git. |
| `src/modules/<family>/<object_id>/` | One feature-oriented source module. |
| `src/collections/<family>/<collection_id>/` | Optional descriptor folder for sibling modules. |
| `~/Documents/Paradox Interactive/Hearts of Iron IV/mod/<project_id>/` | Default HoI4/macOS game-ready output root when `output_root` is omitted and `--emit-artifacts` is used. |
| `build/mod/` | Optional project-local output root when `output_root: build/mod` is set explicitly. |
| `<output_root>/descriptor.mod` | Generated HoI4 descriptor for the output folder. |
| `.paradev/.cache/build/` | Build manifests and build-root view artifacts. |
| `.paradev/.cache/build/launcher/<project_id>.mod` | Launcher `.mod` preview pointing at the output root. When the output root is inside the HoI4 user mod folder, ParaDev also writes `<project_id>.mod` beside it for the launcher. |

The starter project creates a `modifier` module:

```text
src/modules/modifier/starter_mod_starter_modifier/
  meta.yaml
  def.txt
  main.loc
```

`meta.yaml` tells ParaDev which family owns the module. `def.txt` is loaded through the PDX parser. `main.loc` is loaded as localization source.

Use `paradev project-find` when a GUI, importer, or script has a nested path and needs to know whether it belongs to a ParaDev project:

```bash
rtk uv run paradev project-find projects/starter-mod/src --json
```

Use `paradev project-rename` when you only want to change the display title in `paradev.yaml`:

```bash
rtk uv run paradev project-rename projects/starter-mod "Renamed Starter Mod" --json
```

This does not move the folder or change `project_id`.

Do not edit generated files under `build/mod/` or `.paradev/.cache/build/` as source truth. Edit `src/`, then rebuild.

## 中文

一个 ParaDev 项目就是一个包含 `paradev.yaml` 的目录。

最小 manifest：

```yaml
project_id: starter_mod
title: Starter Mod
game: hoi4
source_roots: [src]
build_root: .paradev/.cache/build
```

主要路径：

| 路径 | 含义 |
| --- | --- |
| `src/` | 作者维护的源文件，应该进入 Git。 |
| `src/modules/<family>/<object_id>/` | 一个按功能组织的源模块。 |
| `src/collections/<family>/<collection_id>/` | 可选的集合描述目录，用来组织同一组兄弟模块。 |
| `~/Documents/Paradox Interactive/Hearts of Iron IV/mod/<project_id>/` | 省略 `output_root` 且使用 `--emit-artifacts` 时，HoI4/macOS 默认游戏输出目录。 |
| `build/mod/` | 显式设置 `output_root: build/mod` 时使用的项目本地输出目录。 |
| `<output_root>/descriptor.mod` | 为输出目录生成的 HoI4 descriptor。 |
| `.paradev/.cache/build/` | 构建 manifests 和 build-root 视图 artifact。 |
| `.paradev/.cache/build/launcher/<project_id>.mod` | 指向输出目录的 launcher `.mod` 预览。当输出目录位于 HoI4 用户 Mod 目录内时，ParaDev 也会在旁边写入 `<project_id>.mod` 给启动器使用。 |

起步项目会创建一个 `modifier` 模块：

```text
src/modules/modifier/starter_mod_starter_modifier/
  meta.yaml
  def.txt
  main.loc
```

`meta.yaml` 告诉 ParaDev 模块属于哪个 family。`def.txt` 会通过 PDX parser 加载。`main.loc` 会作为本地化源文件加载。

GUI、导入器或脚本只有一个嵌套路径、需要判断它是否属于 ParaDev 项目时，使用 `paradev project-find`：

```bash
rtk uv run paradev project-find projects/starter-mod/src --json
```

只想修改 `paradev.yaml` 中的显示名称时，使用 `paradev project-rename`：

```bash
rtk uv run paradev project-rename projects/starter-mod "Renamed Starter Mod" --json
```

这个命令不会移动目录，也不会改变 `project_id`。

不要把 `build/mod/` 或 `.paradev/.cache/build/` 里的生成文件当作源文件维护。修改 `src/`，然后重新构建。
