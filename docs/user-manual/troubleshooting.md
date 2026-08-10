# Troubleshooting

## English

## Command Not Found

Run commands through `uv` in this repo:

```bash
rtk uv run paradev --help
```

If dependencies are stale:

```bash
rtk bash scripts/sync-env.bash
```

## Missing `paradev.yaml`

Use a project root or any path inside a project:

```bash
rtk uv run paradev project path/to/project --json
```

If there is no project yet:

```bash
rtk uv run paradev new path/to/project --title "My Mod" --json
```

## Build Is Blocked

Inspect diagnostics:

```bash
rtk uv run paradev diagnostics path/to/project --json
```

Then explain a module, artifact, or diagnostic:

```bash
rtk uv run paradev build-explain path/to/project --module modifier/example --json
rtk uv run paradev build-explain path/to/project --diagnostic-code metadata.invalid_yaml --json
```

## PDX Parse Error

Parse the file directly:

```bash
rtk uv run paradev parse path/to/file.pdx --json
```

Use `--dump` when you need the lossless parse payload:

```bash
rtk uv run paradev parse path/to/file.pdx --dump --json
```

Use `--tokens` when an editor, importer, or parser bug report needs the lexer token rows:

```bash
rtk uv run paradev parse path/to/file.pdx --tokens --json
```

Preview formatter output without writing the file:

```bash
rtk uv run paradev format path/to/file.pdx --json
```

Write the formatted file only after parsing succeeds:

```bash
rtk uv run paradev format path/to/file.pdx --write --json
```

## Output Missing

Dry builds do not write files. Use:

```bash
rtk uv run paradev build path/to/project --emit-artifacts --emit-manifests --json
```

Artifacts under `target_root: output` go to `output_root`. Artifacts under `target_root: build` go to `build_root`.

## 中文

## 找不到命令

在本仓库中通过 `uv` 运行：

```bash
rtk uv run paradev --help
```

如果依赖过期：

```bash
rtk bash scripts/sync-env.bash
```

## 缺少 `paradev.yaml`

使用项目根目录，或项目内部任意路径：

```bash
rtk uv run paradev project path/to/project --json
```

如果还没有项目：

```bash
rtk uv run paradev new path/to/project --title "My Mod" --json
```

## 构建被阻止

查看 diagnostics：

```bash
rtk uv run paradev diagnostics path/to/project --json
```

然后解释某个模块、artifact 或 diagnostic：

```bash
rtk uv run paradev build-explain path/to/project --module modifier/example --json
rtk uv run paradev build-explain path/to/project --diagnostic-code metadata.invalid_yaml --json
```

## PDX 解析错误

直接解析该文件：

```bash
rtk uv run paradev parse path/to/file.pdx --json
```

需要 lossless parse payload 时加 `--dump`：

```bash
rtk uv run paradev parse path/to/file.pdx --dump --json
```

编辑器、导入器或 parser bug report 需要 lexer token rows 时加 `--tokens`：

```bash
rtk uv run paradev parse path/to/file.pdx --tokens --json
```

预览格式化结果但不写入文件：

```bash
rtk uv run paradev format path/to/file.pdx --json
```

只有在解析成功后才写入格式化结果：

```bash
rtk uv run paradev format path/to/file.pdx --write --json
```

## 没有输出文件

Dry build 不会写文件。使用：

```bash
rtk uv run paradev build path/to/project --emit-artifacts --emit-manifests --json
```

`target_root: output` 的 artifacts 会写到 `output_root`。`target_root: build` 的 artifacts 会写到 `build_root`。
