# Install ParaDev And Build PIHC3

Status: usable unsigned macOS Python-wheel application with a system-WebView
host; Windows native packaging is deferred

## Preferred Unsigned macOS Installation

With Python 3.10 or newer, install a downloaded ParaDev wheel and create the
Finder- and Dock-launchable app:

```bash
python3 -m pip install /path/to/paradev-0.1.0.0.dev0-py3-none-any.whl
paradev dashboard --install-app --yes
open "$HOME/Applications/ParaDev.app"
```

When ParaDev is published to PyPI, use
`python3 -m pip install --upgrade paradev` instead. To let a tool provision and
own the compatible interpreter, use `uv tool install --python 3.12 <wheel>` and
then `"$(uv tool dir --bin)/paradev" dashboard --install-app --yes`. No Conda
environment or developer checkout is required. The installed `.app`
intentionally points to the Python runtime that created it, so do not remove
that environment while the app remains installed.

Running `paradev dashboard` without installing opens the same native
system-WebView host for the lifetime of that command. `paradev dashboard --app`
explicitly requests a Chromium app window. `paradev-gui` calls the same launcher
as a compatibility entry point. The system-WebView app is ad-hoc signed, not notarized;
the first-open Gatekeeper steps below still apply.

After upgrading the package, run `paradev dashboard --install-app --yes` again.
To remove ParaDev, move `~/Applications/ParaDev.app` to Trash, then uninstall
the Python package or run `uv tool uninstall paradev`. Neither operation removes
projects under `~/Documents/ParaDev/Projects`.

## First Launch And PIHC3 Import

1. Open `~/Applications/ParaDev.app`. Because the app is ad-hoc signed rather
   than notarized, the first launch may require Control-clicking the app,
   choosing **Open**, and confirming **Open**. If macOS still blocks it, try
   once and use **System Settings → Privacy & Security → Open Anyway**. Never
   disable Gatekeeper or remove quarantine protection system-wide.
2. Choose **Install PIHC3 package** and select the catalog-bound
   `PIHC3-0.2.3-project.zip` in the native ZIP picker. Do not extract it.
3. ParaDev verifies the cataloged SHA-256, archive inventory, portable paths,
   and per-file checksums before publishing the project atomically under
   `~/Documents/ParaDev/Projects/PIHC3-0.2.3`.
4. ParaDev opens and remembers the installed project automatically.

Use **Open existing project** only for a writable project folder that already
contains `paradev.yaml`. Cancelling either native picker leaves the current
workspace unchanged.

## Windows Native Packaging (Deferred)

No Windows MSI, NSIS, or other native installer is currently part of the
release contract. Windows native packaging remains deferred until a supported
host, installer lifecycle, system-WebView integration, and clean-machine smoke
gate are implemented and verified. Where a Python environment is installed
manually, `paradev dashboard --app` may be used as a Chromium-window fallback; that
command is not a Windows native package and must not be presented as one.

## First-Release Upgrades And Removal

The first release uses manual upgrades. ParaDev does not download or apply
updates in the background:

1. Finish or cancel any active build, then quit ParaDev.
2. Reinstall the replacement wheel with
   `uv tool install --force --python 3.12 <new wheel>`.
3. Refresh the application bundle with
   `paradev dashboard --install-app --yes`.
4. Launch ParaDev and reopen the remembered project.

The application identifier remains stable across releases. macOS testers must
not manually replace a newer application with an older one; rollback is not a
supported first-release workflow. Upgrades and removal must never delete
project folders or generated mods. Moving the app to Trash removes the Finder
entry, while `uv tool uninstall paradev` removes its private Python runtime;
user settings and caches may remain. Complete cache cleanup and uninstall
residue checks remain clean-machine acceptance gates, so testers should not
manually delete hidden ParaDev data unless a troubleshooting instruction names
the exact path.

An in-app updater remains deferred until signed update artifacts, immutable
hosting, key rotation, failure recovery, and clean-machine upgrade tests exist.

## Package Verification And Recovery

The project-package catalog is part of the bundled ParaDev backend and is bound
to the matching desktop and Python versions. The archive's SHA-256 is the trust
root, including PIHC3's project-local executable Python modules. Renamed browser
downloads are accepted when their bytes match; modified, incomplete, encrypted,
unsafe, or unknown ZIP files are rejected.

Import happens in a private sibling staging folder. ParaDev checks free space
before extraction and uses one final directory rename, so a failed import never
publishes a partial project. It never overwrites an unmanaged folder or an
existing installed project. Selecting the same verified package again safely
reopens the managed project and preserves user edits.

Errors name the corrective action: re-download checksum failures, free disk
space, choose a writable destination, or use **Open existing project**
for an unpackaged folder.

## Configure Hearts Of Iron IV

Open **Config** and choose the launch mode. The Hearts of Iron IV game folder
is required only for **Local app** mode; Steam mode uses the normal Steam
launch path. ParaDev publishes to the current OS user's standard Hearts of
Iron IV mod folder and reports its exact expected path when it is missing,
unwritable, or unsafe. The generated mod must never be inside the PIHC3 source
project.

## Build PIHC3

Use **Build** for the first clean/full build. A successful PIHC3 build reports:

- 14,574 active modules, plus one discoverable inactive module;
- 106 collections;
- 35,398 generated artifacts; and
- zero diagnostics and zero errors.

After the first build:

- **Cached** rebuilds the complete project while reusing valid build state.
- **Build family** updates the selected family, such as all 300 Technology
  modules.
- **Build module** updates one selected module, such as
  `technology/TECHNOLOGY_FIREARM_I`.

All four modes publish into the same generated mod. Partial builds preserve
unrelated output; they do not create a second incomplete mod.

When the build succeeds, use **Launch Hearts of Iron IV**. Confirm in the
Paradox Launcher that the generated PIHC3 mod is enabled before starting the
game.

## What To Report

For an installation or build failure, record:

- operating-system version and CPU architecture;
- installer filename and SHA-256;
- the visible ParaDev error;
- the build mode and selected family or module;
- the final module, collection, artifact, diagnostic, and error counts; and
- whether Hearts of Iron IV and its mod folder were installed in default or
  custom locations.

Do not attach private project contents, credentials, or unrelated files.

## 中文

如果已有 Python 3.10 或更新版本，可以直接安装下载的 ParaDev wheel，再创建可从
Finder 和 Dock 启动的 macOS 应用：

```bash
python3 -m pip install /path/to/paradev-0.1.0.0.dev0-py3-none-any.whl
paradev dashboard --install-app --yes
open "$HOME/Applications/ParaDev.app"
```

PyPI 发布后可改用 `python3 -m pip install --upgrade paradev`。如需工具自动准备并
管理 Python，可以先运行 `uv tool install --python 3.12 <wheel>`，再运行
`"$(uv tool dir --bin)/paradev" dashboard --install-app --yes`。`paradev dashboard`
默认使用 macOS 系统 WebView；`paradev dashboard --app` 只是显式请求 Chromium
窗口的后备方式，`paradev-gui` 是兼容入口。首次打开采用
临时签名、尚未公证的应用时，可以按住 Control 点击应用并选择“打开”，但不要关闭
Gatekeeper 或移除系统级隔离保护。

启动后点击“安装 PIHC3 项目包”，在系统 ZIP 选择器中选择目录绑定的
`PIHC3-0.2.3-project.zip`，无需手工解压。ParaDev 会核对 SHA-256、压缩包清单、
跨平台路径与每个文件的校验和，再以原子方式安装到
`~/文稿/ParaDev/Projects/PIHC3-0.2.3`。安装成功后会自动打开并记住该项目。
“打开现有项目”只用于已经包含 `paradev.yaml` 的可写项目文件夹；取消任一系统
选择器都不会改变当前工作区。

Windows 原生打包目前明确延期；现阶段没有 MSI、NSIS 或其他 Windows 原生安装包
属于发行约定。只有受支持的宿主、安装与卸载生命周期、系统 WebView 集成和干净机器
验收都实现并通过后，才能声称 Windows 原生发行可用。在手工准备的 Python 环境中，
可以把 `paradev dashboard --app` 作为 Chromium 窗口后备方式，但它不是 Windows 原生
安装包，也不得被描述为原生发布物。

首个发行版采用手动升级，不会在后台下载或安装更新。升级前先完成或取消当前构建并
退出 ParaDev，升级 Python 包后，再运行
`paradev dashboard --install-app --yes` 刷新 `.app`。启动新版本并
重新打开已记住的项目即可。macOS 测试人员不应手工用旧应用替换新应用；首发版不
提供回滚流程。

升级和卸载不得删除项目目录或生成的 Mod。把 `~/Applications/ParaDev.app` 移到
废纸篓会移除 Finder 入口，`uv tool uninstall paradev` 会移除私有 Python
运行环境；用户设置和缓存可能仍会保留。除非故障排查说明给出明确路径，否则不应
手工删除隐藏的 ParaDev 数据。只有在签名更新包、不可变托管、密钥轮换、失败恢复
和干净机器升级测试全部具备后，才会加入应用内更新功能。

项目包目录随 ParaDev 后端一起发布，并绑定相同的桌面版与 Python 版。整个 ZIP
的 SHA-256 是信任根，包括 PIHC3 的项目本地可执行 Python 模块。导入在私有临时
目录中进行，先检查磁盘空间，最后只用一次目录重命名发布；失败不会留下半成品，
也不会覆盖现有文件夹或用户修改。校验失败时请重新下载，空间不足时请释放磁盘，
普通未打包项目则使用“打开现有项目”。

在“配置”页选择启动方式；只有“本地应用”模式需要填写 Hearts of Iron IV
游戏目录。ParaDev 会使用当前用户的标准 Hearts of Iron IV Mod 目录，如果该
目录缺失、不可写或不安全，会报告准确的预期路径。首次使用“构建”执行
clean/full；成功结果应为 14,574 个启用模块、1 个可发现但未启用的模块、106 个集合、35,398 个产物、0 个诊断、
0 个错误。之后可执行 cached、当前 family partial，或当前 module partial。
局部构建会保留无关输出，不会生成残缺的第二份 Mod。构建成功后使用“启动
Hearts of Iron IV”，并在 Paradox Launcher 中确认生成的 PIHC3 Mod 已启用。
