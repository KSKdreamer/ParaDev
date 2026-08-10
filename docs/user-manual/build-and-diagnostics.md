# Build And Diagnostics

## English

For a generated list of every public `paradev.build` import, read [Build API Reference](build-api-reference.md). It is generated from `paradev.build.get_build_api_table()` and groups records, family contracts, source slots, loaders, artifact writers, manifests, views, graph helpers, and planning helpers by module, feature, and symbol kind.

Dry build is the default. It plans artifacts and diagnostics without writing
mod output or build-manifest files. It may atomically refresh ParaDev's hidden
derived parsed-source cache:

```bash
rtk uv run paradev build demos/assets/projects/minimal --json
```

Loose metadata is the package default: unknown module and collection metadata keys are warnings unless `paradev.build.strict_metadata` is enabled in `CM_PARADEV`. For cleanup work or CI, use strict metadata to make those diagnostics blocking errors:

```bash
rtk uv run paradev build demos/assets/projects/minimal --strict-metadata --json
```

Write artifacts and manifests:

```bash
rtk uv run paradev build demos/assets/projects/minimal --emit-artifacts --emit-manifests --json
```

CLI and SDK builds synchronize the external HoI4 launcher descriptor by
default for compatibility. Use `--no-sync-launcher-descriptor`, or
`Project.build(..., sync_launcher_descriptor=False)`, when compilation should
publish only the project output and hidden build manifests. This mode still
writes the project-owned `descriptor.mod` and the launcher preview under the
build root; it never reads, locks, creates, or updates the external launcher
descriptor or its ParaDev ownership marker.

GUI and desktop clients use the same SDK path through REST:

```http
POST /projects/build?path=demos/assets/projects/minimal
POST /projects/build?path=demos/assets/projects/minimal&strict_metadata=true
POST /projects/build?path=demos/assets/projects/minimal&emit_artifacts=true&emit_manifests=true
POST /projects/build?path=projects/PIHC3&family=technology&module_id=technology/TECHNOLOGY_FIREARM_I&emit_artifacts=true
POST /projects/build?path=projects/PIHC3&full_rebuild=true&parallelism=4&emit_artifacts=true&emit_manifests=true
```

The synchronous REST route exposes the SDK's singular `family`, `module_id`, and `collection_id` selectors plus `full_rebuild` and `parallelism`; omitted values retain `Project.build` defaults. The route returns the same `BuildResult.to_dict` payload as CLI `build --json`. Each request discovers and plans the project once. If that plan has blocking diagnostics, an artifact-emitting request returns the blocked dry result and writes no artifacts; `emit_manifests=true` may still publish the diagnostics and other canonical manifests for inspection.

### Cached And Targeted Builds

Cached builds use one complete project plan but only replace outputs that changed. When every compiler, source, Registry, runtime, copy input, and extension-declared external input matches, ParaDev can reuse a previously validated finalized plan instead of recompiling every family. A targeted build uses that same complete plan, then emits the smallest safe closure:

- a module normally emits that module;
- a module owned by a collection emits the whole owning collection, including its descriptor and sibling modules;
- a `building` module emits the complete `building` family because the shared icon strip depends on every building;
- a registered project artifact postprocessor may declare a project-wide artifact closure when cross-module consistency requires it; PIHC3 does this for localization while keeping unrelated non-localization outputs target-scoped;
- a collection target is family-qualified internally, so duplicate collection ids in different families cannot be confused.

Before parsing, cached and targeted builds validate each source family against
a hidden, checksummed per-file inventory under
`.paradev/cache/source-families/`. On a trusted local filesystem, unchanged
size, mtime, precise ctime, device, and inode observations can reuse the stored
content SHA; changed or ambiguous files are opened and hashed with path/handle
identity checks. Unknown, network, coarse-time, symlinked, or cross-device
topologies use the conservative full-hash or no-cache path. Only after the
bounded parsed payload is decoded does one final source fingerprint authorize
the hit. An exact match reuses the already parsed PDX, localization,
copy-source, metadata, and diagnostic records. Full mode always parses source
files again and then refreshes valid cache entries. A changed slot contract,
metadata mode, parser/loader implementation, runtime, or dependency version
also invalidates the entry. ParaDev fingerprints the loaded HeavenBase and
localization helper source too, so an editable HeavenBase checkout invalidates
old entries without requiring a package-version bump. Missing, stale, corrupt,
oversized, or unwritable source-cache files never block compilation; ParaDev
reparses that family. After discovery, normal
project builds may also reuse a finalized plan from the hidden
`.paradev/cache/artifact-plans/` folder. Its signature includes the aggregate
source fingerprints, copy inputs, Registry/compiler code, runtime dependencies,
project/profile inputs, and extension-owned external-state keys. PIHC3 includes
its resolved localization reference files in that key. If any registered
postprocessor cannot safely describe its external inputs, plan reuse is disabled
and the build proceeds normally. Full mode always replans and refreshes the
entry. Missing, stale, corrupt, oversized, or unwritable plan-cache entries also
fall back safely. A cache hit skips unchanged family compilation and artifact
planning, but collection/target resolution, collision checks, publication
closure, PIHC3 localization output, retained-file validation, transactional
publication, and canonical manifests still run for every mode. The first build
after a source/compiler/runtime change pays the normal planning cost; later
unchanged builds receive the steady-state speedup automatically.

On an exact finalized-plan hit, ParaDev can retain canonical manifest files
without rebuilding their large JSON projections. It validates a hidden receipt
under `.paradev/cache/manifest-publications/` against the plan, projector code,
complete manifest inventory, and every retained file SHA-256. Missing, stale,
corrupt, incomplete, or unwritable receipts simply use normal projection.
Externally edited manifest files are repaired automatically. This hidden cache
is disposable system state; users and module authors never maintain it.

Static copy sources also carry a ParaDev-maintained raw-byte `content_sha256`,
separate from HeavenBase's deterministic object hash. During publication,
ParaDev streams an existing generated file and retains it without rereading or
staging the source only when that raw digest matches exactly. Missing, changed,
or externally damaged output takes the ordinary validated copy path and is
repaired. Invalid digest metadata, source drift, oversized direct-copy inputs,
and artifacts covered by a stage transform cannot bypass the safe fallback.
This metadata is hidden derived state; module authors never maintain it.

Use at most one primary selector, `--module` or `--collection`; `--family` can be used alone or to qualify that selector. When a bare collection id exists in more than one family, also pass `--family`. Unknown targets and family/target mismatches fail before any output is changed. `--full-rebuild` cannot be combined with a target.

```bash
rtk uv run paradev build projects/PIHC3 --module idea/EXAMPLE --emit-artifacts --emit-manifests --json
rtk uv run paradev build projects/PIHC3 --family focus_tree --collection C01_MAIN --emit-artifacts --json
```

Manifests remain canonical whole-project views even after a targeted build. Artifact publication follows the requested target plus any registered safety closure. ParaDev records generated paths and declared predecessor paths in `.paradev/.cache/build/.emitted-artifacts.json`. Cached and targeted builds use this hidden, atomically replaced ledger to remove generated files that disappeared from that exact scope. ParaDev refuses unsafe ledger paths and never deletes untracked files, so user-authored files placed beside generated output are not treated as stale artifacts.

### Build From The Desktop App

Open the Build workspace for the selected project, choose Cached or Full mode, review the strict-metadata and parallelism settings, then choose Build and confirm the write. ParaDev reports the compiler's real phase, completed-item count, percentage, and actual parsed-source cache reuse or refresh counts instead of estimating progress in the GUI. App builds always use project-only publication: compiling a project never depends on, claims, or changes an external game-launcher descriptor.

Full mode clears stale generated files before emission. For a HoI4 project registered in the user mod folder, ParaDev clears the directory contents but keeps the output directory itself continuously present and leaves the outer launcher descriptor registered. This prevents an open Paradox Launcher from replacing the mod identity and leaving an existing playset bound to an unavailable duplicate.

You can open another ParaDev workspace while the build runs. Leaving the Build rail does not stop the build. When you return, the dashboard shows the selected project's current progress and an Interrupt action for the active build, whether it is full or targeted. Interrupt also asks for confirmation, then stops the app-owned compiler process and records the interrupted run in build history.

Conflict checks stay within each project: only one artifact-mutating build can run for a project at a time, because targeted builds can expand to collection/family scope and publish canonical manifests. Different project roots can build at the same time and remain independently visible. ParaDev also serializes artifact and manifest writes when builds resolve to the same output or build root. CLI or SDK builds that explicitly keep launcher synchronization enabled additionally serialize the external descriptor target. Avoid intentionally sharing generated destinations between projects because a later build can still replace an earlier project's generated content.

ParaDev automatically reconnects to every active full or partial build after the Build page is remounted. It also recovers those runs after a renderer/webview reload as long as the same native ParaDev app process is still running. Recovery happens before new Build controls are enabled, so you do not need to copy or enter a build run id and cannot accidentally start a conflicting run while ParaDev is still checking. If that check reports an error, choose Refresh to retry it before building.

A failed or interrupted current target remains visible and keeps Run Game disabled so ParaDev does not silently launch stale or partially generated output. A successful rebuild of another partial target does not hide that failure. A successful Full build does establish a clean project baseline: it clears older partial failure state, while any partial build that fails afterward is shown normally.

Within the current native app process, the backend keeps every active run and the newest 256 completed, failed, or interrupted runs. Each retained terminal payload includes `terminalSequence`, a nonnegative causal ordinal that increases when this registry observes another terminal run, even if the wall clock moves backward. Compare it only with payloads from the same native registry lifetime; it has no ordering meaning after a native-process restart. An exact status lookup for an older evicted id returns `idle`. Browser build history is a best-effort local display that may be cleared or trimmed; it does not recover compiler processes or extend their lifetime.

REST status and interrupt calls require the exact nonblank `run_id` returned by build start or build listing; an empty or whitespace value is rejected rather than treated as omission. This prevents a generic client from polling or interrupting an unrelated project's oldest run when several projects are building concurrently.

Closing the native app normally cancels and reaps all builds started by that app, then removes that session's temporary build output, stderr, and progress files. Those paths support live status and retained history only while the native process is open; generated mod artifacts remain in the project's configured output root. A full app quit, crash, or native-process restart does not resume the old build. A hard crash can leave temporary files for later operating-system cleanup. Reopen ParaDev and start a new build after checking the project diagnostics and output state.

The interactive desktop lifecycle uses these SDK-owned routes; it is separate from the synchronous `/projects/build` plan/emit request above:

```http
GET /desktop/builds
POST /desktop/builds
GET /desktop/builds/status?run_id=<run-id>
POST /desktop/builds/interrupt  body: {"runId":"<run-id>"}
```

For HoI4 projects, the default profile plans two project-owned `mod_descriptor` artifacts. `descriptor.mod` is written under the output root. If `output_root` is omitted on macOS, the output root defaults to `~/Documents/Paradox Interactive/Hearts of Iron IV/mod/<project_id>`; otherwise explicit manifest paths still win. The launcher preview is written under the build root (`.paradev/.cache/build/launcher/<project_id>.mod`) and points at the project output root. CLI and SDK builds synchronize `<project_id>.mod` into the user Mod folder unless launcher synchronization is disabled. The desktop App disables it because game-launch integration is a separate action.

Useful inspection commands:

```bash
rtk uv run paradev summary demos/assets/projects/minimal --json
rtk uv run paradev manifests demos/assets/projects/minimal --json
rtk uv run paradev inspections demos/assets/projects/minimal --json
rtk uv run paradev diagnostics demos/assets/projects/minimal --json
rtk uv run paradev source-slots demos/assets/projects/minimal --json
rtk uv run paradev sources demos/assets/projects/minimal --json
rtk uv run paradev assets demos/assets/projects/minimal --json
rtk uv run paradev sprites demos/assets/projects/minimal --json
rtk uv run paradev source-map demos/assets/projects/minimal --json
rtk uv run paradev build-graph demos/assets/projects/minimal --json
```

Use `families` to see the slot and output contracts a profile supports. Each family row includes source slots, metadata/settings rules, and an `outputs` list with `artifact_type`, `template_key`, `template`, `owner_kinds`, `target_root`, and route or sprite-slot context when applicable. Metadata rules include accepted `keys`, SDK-wide `common_keys`, compiler-owned `family_keys`, and `unknown_key_policy` for loose versus strict metadata diagnostics. Use `index["output_artifact_type"]` to find families that can plan a given artifact type, and `index["artifact_type"]` to find registered writers. The same capability payload exposes registered whole-plan transforms in `postprocessors`; `index["postprocessor_id"]` and `index["postprocessor_kind"]` provide deterministic row ids for CLI, REST, MCP, and agent inspection. Use `source-slots` to see, for each discovered module or collection descriptor, which declared slots are `satisfied`, `missing`, `empty`, or `diagnostic`; exact slots also include `suggested_relative_paths` and `suggested_paths` so tools can show where a missing file should be created. Use `sources` to see the actual files ParaDev recognized and loaded before artifact planning details; add `--owner-kind collection` when you only want descriptor-owned collection sources. Use `assets` to inspect static copy/image rows before emission, and use `sprites` to inspect planned interface sprite declarations for icon-style slots. Use `source-map` when you want to trace planned output files back to those sources.

Use `build-graph` when a UI or importer needs a visual trace view. Graph nodes keep stable `id`, `type`, and `label` fields, and also include `group`, `display_label`, `display_detail`, and `display_path` so clients can draw lanes, compact node text, side-panel subtitles, and readable paths without parsing ids. `summary["nodes_by_group"]` and `index["nodes_by_group"]` provide the ready grouping index.

For example, this shows only missing required slots:

```bash
rtk uv run paradev source-slots demos/assets/projects/minimal --status missing --json
```

For local tools that need searchable rows, write or refresh the HeavenBase catalog and query the same source inventory through `source-file` rows:

```bash
rtk uv run paradev hb catalog-refresh demos/assets/projects/minimal --json
rtk uv run paradev hb catalog-query demos/assets/projects/minimal --entity source-file --tag loader:pdx --json
```

Catalog writes enable the HeavenBase `hoi4` extension and persist these rows as `hoi4-*` entities; query inputs can still use short names such as `source-file` and `pdx-symbol`. Source catalog tags include `module:<id>`, `collection:<id>`, `family:<family>`, `slot:<slot>`, `loader:<loader>`, and `status:<status>`. Each result row also includes `data`, the original source inventory row. Use this when an editor, importer, or script needs one searchable index for authored files, PDX documents, symbols, artifacts, graph edges, diagnostics, and project metadata.

Explain one target:

```bash
rtk uv run paradev build-explain demos/assets/projects/minimal --artifact common/national_focus/GER_main.txt --json
rtk uv run paradev build-explain demos/assets/projects/minimal --module focus/GER_sample --json
rtk uv run paradev build-explain demos/assets/projects/minimal --diagnostic-code build.artifact_collision --json
```

How to read diagnostics:

| Field | Meaning |
| --- | --- |
| `code` | Stable machine-readable diagnostic id. |
| `severity` | `error` blocks artifact emission; `warning` does not. |
| `module_id` | Source module involved. |
| `collection_id` | Source collection involved. |
| `source_path` | File path relative to the module or collection root. |
| `artifact_path` | Planned output path involved. |
| `target_root` | `output` for mod output, `build` for `.paradev/.cache/build`. |

Common fixes:

- `metadata.invalid_yaml`: fix `meta.yaml` indentation or mapping shape.
- `slot.source_collision`: make a source file match only one slot, or use a shared slot contract.
- `pdx.*`: run `paradev parse <file> --json` and fix the reported line/column.
- `build.missing_artifact_writer`: register the writer or keep the registry dry-run-only.
- `<family>.missing_localization`: add the missing localization key for every authored language.

## 中文

如果需要查看所有公开 `paradev.build` import，请阅读 [Build API Reference](build-api-reference.md)。它由 `paradev.build.get_build_api_table()` 生成，并按 module、feature 和 symbol kind 给 record、family contract、source slot、loader、artifact writer、manifest、view、graph helper 和 planning helper 分组。

默认构建是 dry build。它只计划 artifacts 和 diagnostics，不写输出文件：

```bash
rtk uv run paradev build demos/assets/projects/minimal --json
```

Loose metadata 是包默认模式：未知的模块和 collection 元数据键会产生 warning，除非在 `CM_PARADEV` 中启用了 `paradev.build.strict_metadata`。做清理或 CI 检查时，可以启用 strict metadata，把这些诊断提升为 blocking error：

```bash
rtk uv run paradev build demos/assets/projects/minimal --strict-metadata --json
```

写出 artifacts 和 manifests：

```bash
rtk uv run paradev build demos/assets/projects/minimal --emit-artifacts --emit-manifests --json
```

为了兼容旧行为，CLI 和 SDK 构建默认同步外部 HoI4 启动器 descriptor。只想发布项目输出和隐藏构建 manifest 时，请使用
`--no-sync-launcher-descriptor`，或
`Project.build(..., sync_launcher_descriptor=False)`。该模式仍会写出项目自己的
`descriptor.mod` 以及构建目录中的 launcher 预览，但不会读取、锁定、创建或修改外部启动器 descriptor 及其 ParaDev 所有权标记。

GUI 和桌面端通过 REST 使用同一条 SDK 路径：

```http
POST /projects/build?path=demos/assets/projects/minimal
POST /projects/build?path=demos/assets/projects/minimal&strict_metadata=true
POST /projects/build?path=demos/assets/projects/minimal&emit_artifacts=true&emit_manifests=true
POST /projects/build?path=projects/PIHC3&family=technology&module_id=technology/TECHNOLOGY_FIREARM_I&emit_artifacts=true
POST /projects/build?path=projects/PIHC3&full_rebuild=true&parallelism=4&emit_artifacts=true&emit_manifests=true
```

同步 REST route 暴露 SDK 的单值 `family`、`module_id`、`collection_id` selector，以及 `full_rebuild` 和 `parallelism`；省略时继续使用 `Project.build` 默认值。该 route 返回的也是 CLI `build --json` 使用的 `BuildResult.to_dict` payload。每次请求只发现和规划项目一次。如果该计划存在 blocking diagnostics，请求会返回被阻塞的 dry result，不会写 artifacts；当 `emit_manifests=true` 时，仍可写出 diagnostics 等完整项目 manifests 供检查。

### 缓存构建与局部构建

缓存构建使用完整项目计划，但只替换发生变化的输出。当 source、Registry、compiler、runtime、copy input 与 extension 声明的外部输入完全一致时，ParaDev 会从隐藏的 `.paradev/cache/artifact-plans/` 复用已经验证的最终计划，而不必重新编译每个 family。局部构建使用同一个完整计划，再输出最小安全闭包：

- 普通模块通常只输出该模块；
- 如果模块属于 collection，会输出整个 collection，包括 descriptor 和兄弟模块；
- `building` 模块会输出完整 `building` family，因为共享图标条依赖所有建筑；
- 当跨模块一致性确有需要时，已注册的项目 artifact postprocessor 可以声明完整项目级 artifact 闭包；PIHC3 对 localization 使用这一机制，同时保持无关的非 localization 输出仍受目标范围限制；
- collection target 在内部使用 family 限定，因此不同 family 中的同名 collection 不会混淆。

缓存与局部构建会通过隐藏的 `.paradev/cache/source-families/` 校验每个
source family。缓存条目包含带校验和的逐文件清单；在可信的本地文件系统
上，只有 size、mtime、精确 ctime、device 与 inode 全部安全匹配时才会复用
已有内容 SHA。发生变化或信息含糊的文件会用绑定路径与文件句柄身份的方式
重新读取并哈希；未知、网络、粗粒度时间戳、symlink 或跨设备结构会自动使用
完整哈希或直接绕过解析缓存。ParaDev 先解码有界的派生 payload，再执行一次
最终 source 指纹校验，只有完全匹配才返回缓存结果。用户无需查看或维护这份
隐藏清单。

计划缓存使用有界、带校验和的 JSON/Gzip，不保存 pickle 或可执行代码。PIHC3 会把解析后的外部 localization reference 文件纳入 extension cache key；任何 postprocessor 无法安全描述外部输入时，ParaDev 都会禁用计划复用并正常重建。完整模式始终重建并刷新缓存。缺失、陈旧、损坏、过大或不可写的缓存也只会触发普通重建，不会阻塞编译。命中缓存后，目标解析、安全发布闭包、collision/ledger 检查、事务式发布与完整 manifests 仍会执行；只跳过未变化的 family compilation 和 artifact planning。精确命中最终计划时，ParaDev 还可以通过隐藏的 `.paradev/cache/manifest-publications/` 回执复用已经发布的规范 manifest 字节。回执会绑定计划签名、投影实现、完整 manifest 清单及每个文件的 SHA-256；缺失、陈旧、损坏、不完整或不可写时自动回退到普通投影，外部篡改的 manifest 也会被修复。用户和模组作者无需维护这些隐藏的派生状态。source、compiler 或 runtime 变化后的第一次构建承担正常规划成本，之后的未变化构建自动获得稳定加速。

主要 selector `--module` 和 `--collection` 最多选择一种；`--family` 可以单独使用，也可以限定主要 selector。如果同一个裸 collection id 存在于多个 family，还需同时提供 `--family`。未知目标和 family/target 不匹配会在修改任何输出前失败。`--full-rebuild` 不能与局部目标组合。

```bash
rtk uv run paradev build projects/PIHC3 --module idea/EXAMPLE --emit-artifacts --emit-manifests --json
rtk uv run paradev build projects/PIHC3 --family focus_tree --collection C01_MAIN --emit-artifacts --json
```

局部构建后，manifests 仍是完整项目的权威视图。Artifact 发布范围由请求目标和已注册的安全闭包共同决定。ParaDev 会把已生成路径和声明的前任路径记录在 `.paradev/.cache/build/.emitted-artifacts.json`。缓存和局部构建通过这份隐藏、原子替换的账本删除该精确范围内已经消失的生成文件。ParaDev 会拒绝不安全的账本路径，也绝不会删除未登记文件，因此放在生成目录旁的用户文件不会被当作陈旧 artifact。

### 在桌面应用中构建

打开当前项目的“构建”工作区，选择“缓存”或“完整”模式，检查严格元数据和并行数设置，然后点击“构建”并确认写入。ParaDev 会显示编译器实际报告的阶段、已完成项目数和百分比，不会在 GUI 中虚构进度。App 构建始终只发布项目内容：编译项目不依赖、不认领、也不修改外部游戏启动器 descriptor。

“完整”模式会在写出前清理陈旧的生成文件。对于注册在用户 Mod 目录中的 HoI4 项目，ParaDev 只清理输出目录内容，持续保留输出目录本身和外层启动器 descriptor。这样，已打开的 Paradox Launcher 就不会重新分配 Mod 身份，也不会让现有播放集继续指向不可用的重复记录。

构建运行时可以继续打开 ParaDev 的其他工作区。离开“构建”导航不会停止构建；返回时，面板会显示当前所选项目的真实进度，并为正在运行的完整或局部构建保留“中断”操作。“中断”同样需要确认，随后会停止由应用拥有的编译进程，并把这次中断记录到构建历史。

冲突检查只作用于同一个项目：同一项目一次只允许一个会修改 artifact 的构建，因为局部构建可能扩展到 collection/family 范围，并发布完整项目 manifests。不同项目根目录可以并行构建，并会分别显示各自状态。多个构建解析到同一个输出目录或构建目录时，ParaDev 也会串行写入 artifact 和 manifest；显式保留启动器同步的 CLI/SDK 构建还会串行化外部 descriptor 目标。仍应避免让不同项目故意共享生成目标，因为后完成的构建仍可能替换先前项目生成的内容。

“构建”页面重新挂载后，ParaDev 会自动连接当前原生应用进程中的所有完整构建和局部构建。只要原生 ParaDev 进程仍在运行，renderer/webview 重新加载后也会自动恢复这些构建。恢复完成前，新的构建控件会保持禁用，因此用户不需要复制或输入构建 run id，也不会在 ParaDev 检查期间误开冲突构建。如果检查报错，请点击“刷新”重试，然后再构建。

当前目标构建失败或被中断时，界面会保留该状态并禁用“运行游戏”，避免静默启动陈旧或只生成了一部分的输出。成功重建另一个局部目标不会掩盖这个失败；成功的“完整”构建则会建立新的项目基线，清除更早的局部失败状态，而完整构建之后发生的新局部失败仍会正常显示。

在当前原生应用进程内，后端会保留全部活动构建，以及最新 256 条已完成、失败或已中断构建。每个已保留的终态 payload 都包含 `terminalSequence`：这是当前 registry 分配的非负因果序号，即使系统时钟回退，每观察到一个新的终态构建也会继续递增。它只能在同一个原生 registry 生命周期内比较；原生进程重启后不再具有排序意义。对更早且已淘汰的 id 做精确状态查询时会返回 `idle`。浏览器构建历史只是尽力保留的本地显示数据，可能被清除或裁剪；它不能恢复编译进程，也不会延长进程寿命。

REST 状态查询和中断请求必须携带构建启动或构建列表返回的精确非空白 `run_id`；空字符串或全空白值会被拒绝，而不会被当作省略。这样在多个项目同时构建时，通用客户端不会误查或中断另一个项目中最早启动的构建。

正常关闭原生应用时，ParaDev 会取消并回收这个应用启动的所有构建，然后删除本次会话的临时构建输出、stderr 和进度文件。这些路径只在原生进程仍打开时用于实时状态和保留历史；生成的 Mod artifact 仍保存在项目配置的输出目录中。完整退出、崩溃或原生进程重启后不会继续旧构建；硬崩溃可能留下临时文件，之后由操作系统清理。重新打开 ParaDev 后，请先检查项目 diagnostics 和输出状态，再启动新的构建。

交互式桌面构建使用下面这些由 SDK 管理的 lifecycle route；它与上面的同步 `/projects/build` 计划/输出请求是两条不同路径：

```http
GET /desktop/builds
POST /desktop/builds
GET /desktop/builds/status?run_id=<run-id>
POST /desktop/builds/interrupt  body: {"runId":"<run-id>"}
```

对于 HoI4 项目，默认 profile 会计划两个项目级 `mod_descriptor` artifact。`descriptor.mod` 会写到输出目录下。macOS 上省略 `output_root` 时，输出目录默认是 `~/Documents/Paradox Interactive/Hearts of Iron IV/mod/<project_id>`；显式 manifest 路径仍然优先。launcher 预览会写到构建目录下（`.paradev/.cache/build/launcher/<project_id>.mod`），并指向项目的输出目录。CLI 和 SDK 构建会同步 `<project_id>.mod`，除非显式禁用启动器同步；桌面 App 默认禁用，因为游戏启动集成属于独立操作。

常用检查命令：

```bash
rtk uv run paradev summary demos/assets/projects/minimal --json
rtk uv run paradev manifests demos/assets/projects/minimal --json
rtk uv run paradev inspections demos/assets/projects/minimal --json
rtk uv run paradev diagnostics demos/assets/projects/minimal --json
rtk uv run paradev source-slots demos/assets/projects/minimal --json
rtk uv run paradev sources demos/assets/projects/minimal --json
rtk uv run paradev assets demos/assets/projects/minimal --json
rtk uv run paradev sprites demos/assets/projects/minimal --json
rtk uv run paradev source-map demos/assets/projects/minimal --json
rtk uv run paradev build-graph demos/assets/projects/minimal --json
```

使用 `families` 查看当前 profile 支持哪些 slot 和 output contract。每个 family 行都会包含 source slots、metadata/settings 规则，以及 `outputs` 列表；其中列出 `artifact_type`、`template_key`、`template`、`owner_kinds`、`target_root`，必要时还会包含 route 或 sprite-slot 上下文。metadata 规则会列出接受的 `keys`、SDK 通用的 `common_keys`、compiler 自己的 `family_keys`，以及描述 loose/strict metadata diagnostic 的 `unknown_key_policy`。用 `index["output_artifact_type"]` 找到能计划某类 artifact 的 family，用 `index["artifact_type"]` 找到已注册 writer。同一 capability payload 会在 `postprocessors` 中公开已注册的完整计划变换；CLI、REST、MCP 和 agent 可通过 `index["postprocessor_id"]` 与 `index["postprocessor_kind"]` 取得确定的行号。使用 `source-slots` 查看每个已发现模块或集合描述符的声明 slot 状态：`satisfied`、`missing`、`empty` 或 `diagnostic`；exact slot 还会包含 `suggested_relative_paths` 和 `suggested_paths`，方便工具展示缺失文件应该创建在哪里。使用 `sources` 查看 ParaDev 已识别并加载的实际源文件；只需要 collection descriptor 自己拥有的源文件时，加上 `--owner-kind collection`。使用 `assets` 在写出前检查静态复制和图片行，使用 `sprites` 检查 icon 类 slot 计划出的 interface sprite 声明；需要把计划输出反查到这些源文件时，再使用 `source-map`。

UI 或导入器需要可视化追踪视图时，使用 `build-graph`。Graph node 会保留稳定的 `id`、`type` 和 `label` 字段，同时提供 `group`、`display_label`、`display_detail` 和 `display_path`，让客户端不用解析 id 就能绘制分组泳道、紧凑节点文字、侧边栏副标题和可读路径。`summary["nodes_by_group"]` 和 `index["nodes_by_group"]` 是可直接使用的分组索引。

例如，只查看缺失的必需 slot：

```bash
rtk uv run paradev source-slots demos/assets/projects/minimal --status missing --json
```

本地工具如果需要可搜索的行，可以写入或刷新 HeavenBase catalog，然后通过 `source-file` 行查询同一份源文件清单：

```bash
rtk uv run paradev hb catalog-refresh demos/assets/projects/minimal --json
rtk uv run paradev hb catalog-query demos/assets/projects/minimal --entity source-file --tag loader:pdx --json
```

Catalog 写入会启用 HeavenBase 的 `hoi4` extension，并把这些行持久化为 `hoi4-*` entities；查询输入仍可使用 `source-file`、`pdx-symbol` 这类短名称。源文件 catalog tag 包括 `module:<id>`、`collection:<id>`、`family:<family>`、`slot:<slot>`、`loader:<loader>` 和 `status:<status>`。每个结果行还包含 `data`，也就是原始 source inventory 行。当 editor、导入器或脚本需要一个可搜索索引来查作者文件、PDX document、symbol、artifact、graph edge、diagnostic 和项目元数据时，使用这个入口。

解释某个目标：

```bash
rtk uv run paradev build-explain demos/assets/projects/minimal --artifact common/national_focus/GER_main.txt --json
rtk uv run paradev build-explain demos/assets/projects/minimal --module focus/GER_sample --json
rtk uv run paradev build-explain demos/assets/projects/minimal --diagnostic-code build.artifact_collision --json
```

如何读 diagnostics：

| 字段 | 含义 |
| --- | --- |
| `code` | 稳定的机器可读诊断 id。 |
| `severity` | `error` 会阻止 artifact 输出；`warning` 不会。 |
| `module_id` | 相关源模块。 |
| `collection_id` | 相关源集合。 |
| `source_path` | 相对模块或集合根目录的源文件路径。 |
| `artifact_path` | 相关的计划输出路径。 |
| `target_root` | `output` 表示 Mod 输出，`build` 表示 `.paradev/.cache/build`。 |

常见修复方式：

- `metadata.invalid_yaml`：修复 `meta.yaml` 缩进或 mapping 结构。
- `slot.source_collision`：让一个源文件只匹配一个 slot，或使用 shared slot contract。
- `pdx.*`：运行 `paradev parse <file> --json`，按行列信息修复。
- `build.missing_artifact_writer`：注册 writer，或者保持 registry 只用于 dry run。
- `<family>.missing_localization`：为每种已编写语言补上缺失的本地化 key。
