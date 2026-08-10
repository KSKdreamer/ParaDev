# ParaDev

[English](README.en.md) | [简体中文](README.zh.md)

**一套以图形界面为主、兼具 Python SDK 的模块化《钢铁雄心 IV》模组开发工具。**

ParaDev 可将小型、易懂的源码文件夹编译成完整的 HoI4 模组。桌面图形界面面向不会编程的模组作者；Python SDK、CLI、REST 与 MCP 接口则向脚本和 AI 智能体提供相同且经过验证的操作。

[PIHC3](https://github.com/PIHC-Team/HOI4-PIHC) 是 ParaDev 的旗舰项目，完整使用了理念、角色、国策、科技、决议、编制、事件、成就、学说、装备、修正、国家、地区、军工机构 (MIO)，以及超级事件、背包物品、地区传说等项目专属扩展。

> ParaDev 目前仍是 Alpha 软件。请为重要项目源码保留备份或版本控制副本。当前版本支持 Python 3.10–3.13，推荐使用 Python 3.12。

## 安装前准备

- 一台受支持的 macOS、Windows 或 Linux 电脑，以及足够存放项目的磁盘空间。
- Python 3.10–3.13。你可以自行安装，也可以交给 [uv](https://docs.astral.sh/uv/) 管理，或使用 [Miniforge](https://github.com/conda-forge/miniforge)。
- 使用已安装的 ParaDev 包无需 Node.js、Rust、Conda 环境或开发源码仓库。
- 打开和编辑项目不要求安装《钢铁雄心 IV》，但测试生成的模组仍需要游戏本体。

最简单的方案是 **uv**：它会为 ParaDev 安装独立的 Python 运行环境，并与其他程序隔离。如果你更喜欢图形安装器和命名环境，**Miniforge** 也很友好。Conda 本身是可选的；ParaDev 实际只需要 Python。

## 使用 uv 安装（推荐）

### 1. 安装 uv

请参考 [uv 官方安装指南](https://docs.astral.sh/uv/getting-started/installation/)。在 macOS 或 Linux 上打开终端并运行：

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

在 Windows 上打开 PowerShell 并运行：

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

安装后关闭并重新打开终端。如果仍找不到 `uv`，请运行 `uv tool update-shell`，然后再次重开终端。

### 2. 安装 ParaDev

首个 PyPI 版本发布前，请直接安装当前公开源码包：

```bash
uv python install 3.12
uv tool install --python 3.12 "paradev @ https://github.com/PIHC-Team/ParaDev/archive/refs/heads/master.zip"
```

ParaDev 发布到 PyPI 后，可改用更短的命令：

```bash
uv tool install --python 3.12 paradev
```

检查安装结果：

```bash
paradev --version
paradev dashboard --help
```

## 使用 Miniforge 安装（可选）

请从 Miniforge 的[官方发布页与说明](https://github.com/conda-forge/miniforge)下载安装。在 Windows 上，安装后使用 **Miniforge Prompt**；在 macOS 或 Linux 上，允许安装器初始化 Shell 后使用终端。

创建一个 ParaDev 专用的小型环境：

```bash
conda create -n paradev python=3.12 pip
conda activate paradev
python -m pip install "paradev @ https://github.com/PIHC-Team/ParaDev/archive/refs/heads/master.zip"
```

PyPI 版本发布后，将最后一条命令替换为：

```bash
python -m pip install --upgrade paradev
```

每次打开新终端并使用 ParaDev 命令前，请运行 `conda activate paradev`。下文的 macOS 应用无需保持终端激活，但这个环境必须继续存在。

## 使用已有 Python 安装

熟悉 Python 的用户也可以直接安装到虚拟环境：

```bash
python3 -m pip install "paradev @ https://github.com/PIHC-Team/ParaDev/archive/refs/heads/master.zip"
```

不要修改受系统保护的 Python。如果你不确定这句话的含义，请改用 uv 或 Miniforge。

## 启动图形界面

打开 ParaDev 桌面界面：

```bash
paradev dashboard
```

ParaDev 会在本机私有回环地址上提供已打包的界面。macOS 默认使用系统 WKWebView；Windows 与 Linux 默认打开浏览器。浏览器只是显示窗口，所有项目操作仍由你电脑上的 Python 进程完成。

需要时可选择其他启动模式：

```bash
paradev dashboard --browser   # Always use the default browser
paradev dashboard --app       # Use an installed Chromium browser as an app window
paradev dashboard --no-open   # Start the local service without opening a window
```

### 安装 macOS 应用

创建可从访达和 Dock 启动的应用：

```bash
paradev dashboard --install-app --yes
open "$HOME/Applications/ParaDev.app"
```

该应用仅使用临时签名，尚未公证。如果 macOS 阻止首次启动，请右键点击 **ParaDev.app** 并选择**打开**，或前往**系统设置 → 隐私与安全性**批准。应用会记住创建它时使用的 Python；移动或删除对应 uv 工具或 Miniforge 环境后，请重新安装应用。

## 十分钟入门

### 1. 打开 PIHC3 或创建入门项目

首次启动时，ParaDev 会提供两种 PIHC3 入口：

- 如果你已有随版本分发、经过验证的 PIHC3 项目 ZIP，请选择**安装 PIHC3 项目包**。ParaDev 会校验文件，并在 `Documents/ParaDev/Projects` 中安装一份可写副本。
- 如果 PIHC3 或其他 ParaDev 项目已经在电脑上，请选择**打开现有项目**。应选择直接包含 `paradev.yaml` 的项目文件夹，而不是其中的 `src` 文件夹。

若要创建一个小型新模组，请在终端中运行一条命令：

```bash
paradev new my-mod --title "My Mod"
```

然后启动图形界面，选择**打开项目**，并选中新的 `my-mod` 文件夹。ParaDev 会在下次启动时记住最后一个有效项目。

### 2. 选择界面语言和项目语言

打开**设置 → 通用 → 语言**，可在英文和简体中文界面之间切换。在项目设置中只需选择一次首选项目语言；ParaDev 会将其用于本地化与易读的 `ID - 标题` 文件夹名称，无需在每个模块中重复设置。

### 3. 找到模块类型

在左侧项目面板中打开理念、角色、国策、科技、决议、编制、事件、成就、学说、装备、修正、国家或地区等类型。PIHC3 还会显示已注册的项目专属类型。**模块**是一个独立的玩法对象；**集合**拥有一组对象或图结构，例如一棵国策树。

### 4. 创建模块

打开一个类型并选择**新建**。ParaDev 会选择已注册模板，只询问作者必须填写的字段，并将有默认值或系统字段收在**显示默认字段**之后。检查目标位置和文件，再确认创建。

新文件夹遵循项目的身份命名规则，通常为 `ID - 首选语言标题`。请使用 ParaDev 的创建、复制、重命名、启用和停用操作，不要手动移动文件夹；这样引用和隐藏目录才能安全更新。

### 5. 编辑定义、文本与图片

从类型列表中选择模块。引导字段覆盖常见定义与本地化值；资源槽显示该类型可接受的源码文件、图片、图标、肖像及其他素材。使用**应用**保存经过检查的草稿；如果磁盘文件已被其他程序修改，ParaDev 会报告冲突，而不会静默覆盖。

支持树结构的类型会在普通模块编辑器旁打开可视化图表。国策树、科技、学说和军工机构使用各自注册的图规则；项目扩展也可以添加其他树编辑器。

### 6. 构建模组

打开**构建**。项目第一次成功构建应选择**清理输出并重新构建**，让 ParaDev 建立完整基线和启动器描述文件；之后通常选择**更新现有输出**。

| 构建选项 | 适用场景 |
| --- | --- |
| 清理后完整构建 | 首次构建、从不确定输出中恢复，或有意完整重新生成。 |
| 缓存完整构建 | 日常整项目迭代；未修改源码会复用经过验证的缓存。 |
| 类型构建 | 完成若干相关修改后，重建一个类型及其必需的共享输出。 |
| 模块构建 | 重建一个模块及其必需的所属者或聚合输出，进行最快的定点检查。 |

依赖部分构建前，请先完成一次清理后完整构建。构建页面会显示进度、诊断、历史记录和确切输出位置。发生错误的构建不会静默替换已知可用的发布输出。

### 7. 在 HoI4 中测试

按照构建页面显示的描述文件与输出位置，通过你平时使用的 HoI4 启动器流程加载模组。ParaDev 作者工作流不依赖原生启动游戏功能；该功能也不属于当前 Alpha 版的跨平台桌面保证。

## 用直白方式理解项目文件夹

```text
my-mod/
├── paradev.yaml                 # small project settings
├── extensions/                  # optional project-owned families and compilers
├── src/
│   ├── modules/<family>/
│   │   └── <ID - readable title>/
│   └── collections/<family>/
└── .paradev/                    # generated catalogs, caches, and transactions
```

模块内部的确切文件取决于它注册的模板。常见资源槽包括定义、本地化，以及图片或图标。请让图形界面创建文件夹，以确保必需名称和初始内容正确。

让可见的 `meta.yaml` 保持最简：文件夹位置提供类型与身份，项目提供首选语言，扩展提供资源规则。只有需要时才会出现 `collection`、`comment` 或 `inactive: true` 等用户选择。绝不要手动编辑隐藏的 `.paradev` 数据。

## 更新与卸载 ParaDev

通过 uv 从 PyPI 安装后，可使用：

```bash
uv tool upgrade paradev
```

PyPI 发布前，若要刷新当前公开源码版本，请使用：

```bash
uv tool install --force --reinstall --python 3.12 "paradev @ https://github.com/PIHC-Team/ParaDev/archive/refs/heads/master.zip"
```

Miniforge 用户请先激活环境，再重复相应的 `python -m pip install --upgrade ...` 命令。Python 环境发生变化后，请重新安装 macOS 应用，使其指向当前解释器。

移除 uv 安装：

```bash
uv tool uninstall paradev
```

若要删除可选的 macOS 应用外壳，请将 `~/Applications/ParaDev.app` 移到废纸篓。Miniforge 用户可在环境中运行 `python -m pip uninstall paradev`。卸载 ParaDev 不会删除任何项目文件夹。

## 常见问题

- **找不到 `paradev`：** 运行 `uv tool update-shell` 后重开终端；若使用 Miniforge，则运行 `conda activate paradev`。
- **图形界面无法打开项目：** 选择直接包含 `paradev.yaml` 的文件夹，并确认该文件夹可写。
- **已安装的 macOS 应用突然无法工作：** 原来的 Python 环境很可能已被移动或删除。重新安装 ParaDev，再次运行 `paradev dashboard --install-app --yes`。
- **某个模块无法构建：** 应用或放弃仍打开的草稿，阅读编辑器显示的诊断，并确认模块处于启用状态。
- **部分构建被拒绝：** 先完成一次清理后完整构建，为共享输出和启动器描述文件建立有效基线。
- **源码修改发生冲突：** 不要立即强制覆盖。检查 ParaDev 保存的恢复文件和较新的源码，再决定保留哪一份内容。

需要更多说明时，请从[用户手册](docs/user-manual/README.md)、[PIHC3 桌面安装指南](docs/user-manual/install-pihc3-desktop.md)、[模块与集合指南](docs/user-manual/modules-and-collections.md)或[项目布局指南](docs/user-manual/project-layout.md)开始。

## Python SDK

图形界面、CLI、REST、MCP 和编辑器集成都调用同一个公开 `Project` API：

```python
from paradev import Project

project = Project.create("my-mod", title="My Mod")
project.create_module(
    "idea",
    "IDEA_demo",
    values={"title": "Demo Idea", "description": "My first idea."},
)

clean = project.build(emit_artifacts=True, full_rebuild=True)
cached = project.build(emit_artifacts=True)
family = project.build(family="idea", emit_artifacts=True)
module = project.build(module_id="idea/IDEA_demo", emit_artifacts=True)

print(cached.summary())
```

可从项目根目录或任意内部路径加载已有项目：

```python
from paradev import Project

project = Project.load("path/to/project")
print(project.project_id, len(project.modules()), len(project.collections()))
```

请阅读 [Python SDK 指南](docs/user-manual/sdk-python.md)，了解模板发现、受保护的批量创建、诊断、构建结果和扩展 API。运行 `paradev --help` 可查看对应的命令行界面；运行 `paradev mcp serve` 可向 MCP 客户端或 LLM 智能体提供有明确边界的作者工具集。

## 开发 ParaDev

贡献者需要源码仓库和前端工具链，普通安装用户不需要：

```bash
git clone https://github.com/PIHC-Team/ParaDev.git
cd ParaDev
bash scripts/sync-env.bash
bash scripts/flake.bash --ci
bash scripts/test.bash
npm --prefix apps/desktop test
bash scripts/build-wheel.bash
```

React/Vite 界面会被编译进 Python wheel。发布的桌面运行时由 Python 回环服务与轻量 macOS 系统 WebView 宿主组成；应用不包含 Tauri 或 Rust。
