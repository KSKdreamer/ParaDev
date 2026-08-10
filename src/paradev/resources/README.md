# ParaDev

[English](README.en.md) | [简体中文](README.zh.md)

**A GUI-first toolkit and Python SDK for building modular Hearts of Iron IV mods.**

ParaDev turns small, understandable source folders into a complete HoI4 mod. Its desktop GUI is designed for mod authors who do not program, while its Python SDK, CLI, REST, and MCP interfaces provide the same validated operations to scripts and AI agents.

[PIHC3](https://github.com/PIHC-Team/HOI4-PIHC) is ParaDev's flagship project. It exercises ideas, characters, focuses, technologies, decisions, divisions, events, achievements, doctrines, equipment, modifiers, countries, states, MIOs, and project-only extensions such as superevents, inventory items, and state lore.

> ParaDev is alpha software. Keep a backup or version-controlled copy of important project sources. The current release supports Python 3.10–3.13; Python 3.12 is recommended.

## What You Need

- A supported macOS, Windows, or Linux machine and enough disk space for your project.
- Python 3.10–3.13. You may install it yourself, let [uv](https://docs.astral.sh/uv/) manage it, or use [Miniforge](https://github.com/conda-forge/miniforge).
- No Node.js, Rust, Conda environment, or developer checkout is required to run an installed ParaDev package.
- Hearts of Iron IV is not required to open and edit a project, but you need the game to test the generated mod.

The simplest setup is **uv**. It installs a private Python runtime for ParaDev and keeps the command separate from other programs. **Miniforge** is a friendly alternative if you already prefer graphical installers and named environments. Conda itself is optional: ParaDev only needs Python.

## Install With uv (Recommended)

### 1. Install uv

Use the [official uv installation guide](https://docs.astral.sh/uv/getting-started/installation/). On macOS or Linux, open Terminal and run:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

On Windows, open PowerShell and run:

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Close and reopen the terminal after installation. If `uv` is still not found, run `uv tool update-shell` and reopen it once more.

### 2. Install ParaDev

Until the first PyPI release is published, install the current public source package:

```bash
uv python install 3.12
uv tool install --python 3.12 "paradev @ https://github.com/PIHC-Team/ParaDev/archive/refs/heads/master.zip"
```

After ParaDev is published on PyPI, the shorter command will be:

```bash
uv tool install --python 3.12 paradev
```

Check the installation:

```bash
paradev --version
paradev dashboard --help
```

## Install With Miniforge (Optional)

Download Miniforge from its [official releases and instructions](https://github.com/conda-forge/miniforge). On Windows, use **Miniforge Prompt** after installation. On macOS or Linux, use Terminal after allowing the installer to initialize your shell.

Create a small environment dedicated to ParaDev:

```bash
conda create -n paradev python=3.12 pip
conda activate paradev
python -m pip install "paradev @ https://github.com/PIHC-Team/ParaDev/archive/refs/heads/master.zip"
```

After the PyPI release, replace the last command with:

```bash
python -m pip install --upgrade paradev
```

Run `conda activate paradev` whenever you open a new terminal and want to use the ParaDev command. The macOS app described below can launch without an active terminal as long as this environment still exists.

## Install With an Existing Python

Experienced Python users may install directly into a virtual environment:

```bash
python3 -m pip install "paradev @ https://github.com/PIHC-Team/ParaDev/archive/refs/heads/master.zip"
```

Do not modify a protected system Python. If you are unsure what that means, use uv or Miniforge instead.

## Launch the GUI

Open the ParaDev desktop interface:

```bash
paradev dashboard
```

ParaDev serves its packaged interface on a private loopback address. On macOS it prefers the system WKWebView; on Windows and Linux it opens the default browser. The browser is only the window—the Python process on your machine still performs every project operation.

Other launch modes are available when needed:

```bash
paradev dashboard --browser   # Always use the default browser
paradev dashboard --app       # Use an installed Chromium browser as an app window
paradev dashboard --no-open   # Start the local service without opening a window
```

### Install the macOS app

Create a Finder- and Dock-launchable application:

```bash
paradev dashboard --install-app --yes
open "$HOME/Applications/ParaDev.app"
```

The app is ad-hoc signed and not notarized. If macOS blocks the first launch, right-click **ParaDev.app** and choose **Open**, or approve it under **System Settings → Privacy & Security**. The installed app remembers the Python used to create it; reinstall the app after moving or deleting that uv tool or Miniforge environment.

## Your First Ten Minutes

### 1. Open PIHC3 or create a starter project

On first launch, ParaDev offers two PIHC3 choices:

- Choose **Install PIHC3 package** when you have the verified PIHC3 project ZIP distributed with a release. ParaDev verifies it and installs a writable copy under `Documents/ParaDev/Projects`.
- Choose **Open existing project** when PIHC3 or another ParaDev project is already on your computer. Select the project folder that directly contains `paradev.yaml`, not its `src` folder.

To begin a small new mod instead, run one command in a terminal:

```bash
paradev new my-mod --title "My Mod"
```

Then launch the GUI, choose **Open project**, and select the new `my-mod` folder. ParaDev remembers the last valid project for the next launch.

### 2. Choose the interface language and project language

Open **Settings → General → Language** to switch the GUI between English and Simplified Chinese. Under the project's settings, choose the preferred project language once. ParaDev uses it for localization and for readable `ID - title` folder names without repeating the choice in every module.

### 3. Find the module family

Use the left project panel to open a family such as Ideas, Characters, Focuses, Technologies, Decisions, Divisions, Events, Achievements, Doctrines, Equipment, Modifiers, Countries, or States. PIHC3 also exposes its registered project-only families. A **module** is one independent gameplay object; a **collection** owns a group or graph such as a focus tree.

### 4. Create a module

Open a family and choose **New**. ParaDev selects a registered template, asks only for required author-facing fields, and keeps defaulted or system fields behind **Show defaulted fields**. Review the destination and files, then confirm creation.

The new folder follows the project's identity convention, normally `ID - preferred-language title`. Use ParaDev's create, duplicate, rename, activate, and deactivate actions instead of moving folders by hand; references and hidden catalogs are updated safely.

### 5. Edit definitions, text, and images

Select a module from the family list. Guided fields cover common definition and localization values. Resource slots expose the source files, images, icons, portraits, and other assets accepted by that family. Use **Apply** to save a reviewed draft; ParaDev detects conflicting disk changes rather than silently overwriting them.

Tree-capable families open a visual diagram beside the normal module editor. Focus trees, technologies, doctrines, and military industrial organizations use their registered graph rules, while project extensions may add other tree editors.

### 6. Build the mod

Open **Build**. The first successful project build should use **Clean output and rebuild** so ParaDev creates a complete baseline and launcher descriptor. Later builds normally use **Update existing output**.

| Build choice | When to use it |
| --- | --- |
| Clean full build | First build, recovery from uncertain output, or intentional complete regeneration. |
| Cached full build | Normal whole-project iteration; unchanged sources reuse validated caches. |
| Family build | Rebuild one family and any required shared output after several related edits. |
| Module build | Rebuild one module and its required owner/aggregate output for the fastest focused check. |

Run a clean full build before relying on partial builds. The Build page shows progress, diagnostics, history, and the exact output location. A build with errors does not silently replace a known-good published output.

### 7. Test in HoI4

Use the generated descriptor and output shown by the Build page with your normal HoI4 launcher workflow. Native game launching is not required for ParaDev authoring and is not part of this alpha's portable desktop guarantee.

## The Project Folder, in Plain Language

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

The exact files inside a module depend on its registered template. Common slots include a definition, localization, and an image or icon. Let the GUI create the folder so required names and starter content are correct.

Keep visible `meta.yaml` files minimal. Folder location supplies family and identity; the project supplies preferred language; extensions supply resource rules. User choices such as `collection`, `comment`, or `inactive: true` appear only when needed. Never hand-edit hidden `.paradev` data.

## Updating and Removing ParaDev

For a uv installation from PyPI:

```bash
uv tool upgrade paradev
```

To refresh the current public source version before PyPI:

```bash
uv tool install --force --reinstall --python 3.12 "paradev @ https://github.com/PIHC-Team/ParaDev/archive/refs/heads/master.zip"
```

For Miniforge, activate the environment and repeat the appropriate `python -m pip install --upgrade ...` command. After changing the Python environment, reinstall the macOS app so it points to the current interpreter.

Remove a uv installation with:

```bash
uv tool uninstall paradev
```

Move `~/Applications/ParaDev.app` to the Trash to remove the optional macOS app shell. Miniforge users can run `python -m pip uninstall paradev` inside the environment. ParaDev does not delete project folders during uninstall.

## Troubleshooting

- **`paradev` is not found:** reopen the terminal after `uv tool update-shell`, or run `conda activate paradev` for a Miniforge installation.
- **The GUI cannot open a project:** select the folder that directly contains `paradev.yaml`; ensure the folder is writable.
- **The installed macOS app stopped working:** its original Python environment was probably moved or removed. Reinstall ParaDev, then run `paradev dashboard --install-app --yes` again.
- **A module cannot be built:** apply or discard its open draft, read the diagnostic shown in the editor, and make sure the module is active.
- **A partial build is refused:** complete one clean full build first so shared output and the launcher descriptor have a valid baseline.
- **A source edit conflicts:** do not force-overwrite immediately. Review ParaDev's preserved recovery files and the newer source, then decide which content to keep.

For more detail, start with the [user manual](docs/user-manual/README.md), [PIHC3 desktop installation guide](docs/user-manual/install-pihc3-desktop.md), [module and collection guide](docs/user-manual/modules-and-collections.md), or [project layout guide](docs/user-manual/project-layout.md).

## Python SDK

The GUI, CLI, REST, MCP, and editor integrations all call the same public `Project` API:

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

Load an existing project from its root or any nested path:

```python
from paradev import Project

project = Project.load("path/to/project")
print(project.project_id, len(project.modules()), len(project.collections()))
```

See the [Python SDK guide](docs/user-manual/sdk-python.md) for template discovery, guarded batch creation, diagnostics, build results, and extension APIs. Run `paradev --help` for the matching command-line surface, or `paradev mcp serve` to expose the bounded authoring toolkit to an MCP client or LLM agent.

## Development

Contributors need the source checkout and frontend toolchain; package users do not:

```bash
git clone https://github.com/PIHC-Team/ParaDev.git
cd ParaDev
bash scripts/sync-env.bash
bash scripts/flake.bash --ci
bash scripts/test.bash
npm --prefix apps/desktop test
bash scripts/build-wheel.bash
```

The React/Vite interface is compiled into the Python wheel. The distributed desktop runtime is the Python loopback service plus a thin macOS system-WebView host; Tauri and Rust are not part of the application.
