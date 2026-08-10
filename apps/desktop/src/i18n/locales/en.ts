export const en = {
  "app.search.placeholder": "Search modules and config",
  "app.search.aria": "Search modules and config",
  "app.boot.settings.label": "Preparing workspace",
  "app.boot.settings.detail": "Loading desktop settings",
  "app.boot.project.label": "Loading project",
  "app.boot.project.detail": "Reading SDK project registry for {project}",
  "app.boot.project.error.label": "Project load failed",
  "app.boot.refresh.label": "Refreshing project",
  "app.boot.refresh.detail": "Reading SDK browser and templates for {project}",
  "app.boot.refresh.loadedDetail":
    "Refreshing {project}: {items} project rows, {templates} templates, {diagnostics} diagnostics",
  "app.boot.open.label": "Opening project",
  "app.boot.open.detail": "Opening {project} in {target}",
  "app.boot.progress.aria": "ParaDev startup progress",
  "app.boot.steps.label": "Startup phases",
  "app.boot.steps.prepare": "Prepare",
  "app.boot.steps.load": "Load project",
  "app.boot.steps.open": "Open workspace",
  "app.failure.eyebrow": "Interface recovery",
  "app.failure.title": "ParaDev needs to recover",
  "app.failure.detail":
    "The interface hit an unexpected error. This recovery screen did not change your project files.",
  "app.failure.reported":
    "A privacy-safe diagnostic was recorded without project paths or file contents.",
  "app.failure.retry": "Try interface again",
  "app.failure.reload": "Reload ParaDev",
  "app.failure.hint":
    "If the error returns, reload ParaDev. Unsaved editor changes may need to be entered again.",
  "locale.aria": "Language",
  "locale.en": "EN",
  "locale.zh": "中文",
  "theme.aria": "Theme",
  "theme.light": "Light Mode (Ollama Theme)",
  "theme.dark": "Dark Mode (GitHub Soft Dark Theme)",
  "theme.anthropic": "Anthropic Mode (Anthropic Theme)",
  "openTarget.aria": "Open local paths with",
  "openTarget.finder": "Finder",
  "openTarget.explorer": "Explorer",
  "openTarget.cursor": "Cursor",
  "openTarget.vscode": "VS Code",
  "openTarget.sublimeText": "Sublime Text",
  "openTarget.terminal": "Terminal",
  "openTarget.iterm2": "iTerm2",
  "openTarget.cmd": "Command Prompt",
  "openTarget.powershell": "PowerShell",
  "rail.management": "Management",
  "rail.projects": "Editing",
  "rail.agents": "Agents",
  "rail.build": "Build",
  "rail.developer": "Developer",
  "rail.config": "Config",
  "rail.aria": "Global navigation",
  "chat.open": "Open AI chat",
  "chat.close": "Close AI chat",
  "chat.dockSide": "Dock AI chat to side",
  "chat.float": "Float AI chat",
  "chat.panel.aria": "AI chat",
  "chat.title": "AI chat",
  "chat.route": "Gateway: {gateway} · Provider: {provider} · Model: {model}",
  "chat.routeWithPreset":
    "Preset: {preset} · Gateway: {gateway} · Provider: {provider} · Model: {model}",
  "chat.route.default": "Default",
  "chat.role": "Task",
  "chat.operations": "SDK actions",
  "chat.operation.aria": "{title} SDK action ({id})",
  "chat.operation.note": "Shown for planning; chat will not run actions.",
  "chat.operation.openAria": "{title}; {safety}",
  "chat.operation.open.default": "Open related page",
  "chat.operation.open.moduleCreateBatch": "Open batch module planner",
  "chat.operation.open.moduleDraft": "Open module draft planner",
  "chat.operation.open.collectionScaffold": "Open collection planner",
  "chat.operation.open.buildPlan": "Open Build page",
  "chat.operation.open.buildStart": "Open Build page",
  "chat.operation.card.moduleDraft.title": "Module Draft",
  "chat.operation.card.moduleDraft.summary":
    "Plan or write a source-module draft from a frontend browser family id.",
  "chat.operation.card.moduleCreateBatch.title": "Module Batch",
  "chat.operation.card.moduleCreateBatch.summary":
    "Plan or atomically create several modules through one reviewed request.",
  "chat.operation.card.collectionScaffold.title": "Collection Scaffold",
  "chat.operation.card.collectionScaffold.summary":
    "Plan or create one Registry-backed focus tree, decision category, or other collection.",
  "chat.operation.card.buildPlan.title": "Build Plan",
  "chat.operation.card.buildPlan.summary": "Run a dry build plan.",
  "chat.operation.card.buildStart.title": "Build Start",
  "chat.operation.card.buildStart.summary":
    "Start one desktop build run through the Python desktop facade.",
  "chat.operation.readOnly": "Read-only",
  "chat.operation.safety.default": "Does not run actions.",
  "chat.operation.safety.moduleCreateBatch":
    "Does not create files until you review and apply the batch.",
  "chat.operation.safety.moduleDraft": "Does not create files.",
  "chat.operation.safety.collectionScaffold":
    "Does not create files until you review and apply the collection plan.",
  "chat.operation.safety.buildPlan": "Does not run a build.",
  "chat.operation.safety.buildStart": "Does not start a build.",
  "chat.operation.writeCapable": "Write-capable",
  "chat.sources": "Context",
  "chat.source.toggle": "Attach {label}",
  "chat.source.diagnostics": "Diagnostics ({count})",
  "chat.source.templates": "Templates ({count})",
  "chat.source.kind.diagnostics": "Diagnostics",
  "chat.source.kind.source": "Selection",
  "chat.source.kind.templates": "Templates",
  "chat.source.kind.unknown": "Unknown source",
  "chat.source.kind.workspace": "Project",
  "chat.context.template.family": "family",
  "chat.context.template.source": "source",
  "chat.context.template.file": "1 file",
  "chat.context.template.files": "{count} files",
  "chat.context.template.args": "args",
  "chat.context.template.required": "required",
  "chat.context.template.default": "default={value}",
  "chat.context.template.choices": "choices={choices}",
  "chat.context.project.summary":
    "Project: {project}; families: {families}; rows: {rows}.",
  "chat.context.none": "none",
  "chat.context.summary.attached": "Context: {sources}",
  "chat.context.summary.empty": "No context attached",
  "chat.context.summary.selectedFile": "Selected file",
  "chat.context.templates.omitted": "... {count} more templates omitted.",
  "chat.context.diagnostics.defaultSeverity": "diagnostic",
  "chat.context.diagnostics.noMessage": "No diagnostic message.",
  "chat.context.diagnostics.omitted": "... {count} more diagnostics omitted.",
  "chat.empty": "No messages yet",
  "chat.emptyReply": "The AI route returned an empty reply.",
  "chat.proposal.moduleBatch.detail":
    "{count} modules were validated with a read-only SDK plan. No files were created.",
  "chat.proposal.moduleBatch.review": "Review {count}-module plan",
  "chat.proposal.moduleBatch.reviewAria":
    "Review the validated {count}-module plan",
  "chat.proposal.moduleBatch.projectChanged":
    "This plan belongs to a different project. Ask ParaDev AI to plan it again in the active project.",
  "chat.proposal.moduleBatch.templatesChanged":
    "The project templates changed after this plan was created. Ask ParaDev AI to plan it again.",
  "chat.proposal.moduleBatch.sourceChanged":
    "The planned source folder is no longer configured. Ask ParaDev AI to plan it again.",
  "chat.proposal.moduleBatch.familyUnavailable":
    "The planned module family is not available in the current workspace.",
  "chat.proposal.moduleBatch.draftExists":
    "A batch draft already has unsaved input in this module family. Review or discard that draft before opening the AI plan.",
  "chat.proposal.moduleBatch.dialogOpen":
    "A batch planner is already open for this module family. Close it before reviewing the AI plan.",
  "chat.proposal.collection.detail":
    "Collection {id} was validated with a read-only SDK plan. No files were created.",
  "chat.proposal.collection.review": "Review collection {id}",
  "chat.proposal.collection.reviewAria":
    "Review the validated collection plan for {id}",
  "chat.proposal.collection.projectChanged":
    "This collection plan belongs to a different project. Ask ParaDev AI to plan it again in the active project.",
  "chat.proposal.collection.templatesChanged":
    "The project collection templates changed after this plan was created. Ask ParaDev AI to plan it again.",
  "chat.proposal.collection.sourceChanged":
    "The planned collection source folder is no longer configured. Ask ParaDev AI to plan it again.",
  "chat.proposal.collection.familyUnavailable":
    "The planned collection family is not available in the current workspace.",
  "chat.proposal.collection.draftExists":
    "A collection draft already has unsaved input in this family. Review or discard that draft before opening the AI plan.",
  "chat.proposal.collection.dialogOpen":
    "A collection planner is already open for this family. Close it before reviewing the AI plan.",
  "chat.proposal.sourceUpdate.detail":
    "{changed} of {requested} selected source files have guarded Guided changes ready for review. No files were written.",
  "chat.proposal.sourceUpdate.review": "Review {count} source edits",
  "chat.proposal.sourceUpdate.reviewAria":
    "Review the validated plan for {count} source edits",
  "chat.proposal.sourceUpdate.projectChanged":
    "This source-edit plan belongs to a different project. Ask ParaDev AI to plan it again in the active project.",
  "chat.proposal.sourceUpdate.sourceChanged":
    "The selected source or its Guided controls changed after this plan was created. Ask ParaDev AI to plan it again.",
  "chat.proposal.sourceUpdate.familyUnavailable":
    "The planned source family is not available in the current workspace.",
  "chat.proposal.sourceUpdate.draftExists":
    "This module family already has unsaved authoring work. Apply or discard it before reviewing the AI source plan.",
  "chat.proposal.sourceUpdate.dialogOpen":
    "An AI source-edit review is already open for this family. Close it before reviewing another plan.",
  "chat.routeError": "The AI route returned an error.",
  "chat.input.aria": "Message",
  "chat.input.placeholder": "Ask ParaDev",
  "chat.send": "Send",
  "chat.sending": "Sending",
  "chat.error": "AI chat failed: {message}",
  "chat.profileLoadFailed": "AI chat profiles could not be loaded: {message}",
  "chat.you": "You",
  "chat.ai": "ParaDev AI",
  "chat.profile.chat.label": "Chat",
  "chat.profile.chat.detail": "General ParaDev and HoI4 modding help.",
  "chat.profile.chat.prompt":
    "You are ParaDev AI. Help a Hearts of Iron IV modder use ParaDev. Keep answers practical, concise, and grounded in the Python SDK when actions are needed.",
  "chat.profile.explain.label": "Explain HoI4 code",
  "chat.profile.explain.detail":
    "Explain PDX, localization, metadata, GUI, GFX, and generated artifacts.",
  "chat.profile.explain.prompt":
    "Explain HoI4 code and ParaDev source files for a modder. Name the relevant file roles, likely game effect, and any SDK-backed next action.",
  "chat.profile.createModule.label": "Create content plan",
  "chat.profile.createModule.detail":
    "Plan new modules or collections through ParaDev templates before writing source files.",
  "chat.profile.createModule.prompt":
    "Help create ParaDev modules and collections through the Python SDK. Choose exact authoring templates from Project.templates(), then use Project.create_modules(..., write=False) for a module batch or Project.scaffold_collection(..., write=False) for one collection. Never claim that chat created files; only an explicit reviewed apply action may write.",
  "chat.profile.editSelection.label": "Edit selected source",
  "chat.profile.editSelection.detail":
    "Plan guarded edits using the selected source's Registry-owned Guided controls.",
  "chat.profile.editSelection.prompt":
    "Help edit selected ParaDev module sources through Registry-owned Guided controls. Return only a dry Project.plan_source_form_updates(...) proposal; never invent paths or control ids, and never claim that chat wrote files. An explicit reviewed apply action is required.",
  "chat.profile.build.label": "Build/debug project",
  "chat.profile.build.detail":
    "Explain build commands, diagnostics, artifacts, and safe next actions.",
  "chat.profile.build.prompt":
    "Help debug ParaDev SDK builds. Use Project.build(...) for build plans or artifact emission and desktop_project_build_command(...) or the GUI Build page for desktop compilation; explain diagnostics, artifacts, manifests, and safe next actions.",
  "panel.project.aria": "Project panel",
  "panel.project.hide": "Hide project panel",
  "panel.project.show": "Show project panel",
  "panel.config.aria": "Configuration panel",
  "panel.inspector.aria": "Inspector",
  "panel.inspector.hide": "Hide inspector",
  "panel.inspector.show": "Show inspector",
  "project.active.label": "Active Project",
  "project.active.aria": "Active project",
  "project.action.open": "Open project",
  "project.openFailed": "Open failed: {message}",
  "project.onboarding.eyebrow": "PIHC3 workspace",
  "project.onboarding.checking.title": "Finding your ParaDev project",
  "project.onboarding.checking.detail":
    "Checking the saved project location and local project registry.",
  "project.onboarding.title": "Set up your PIHC3 workspace",
  "project.onboarding.detail":
    "Install the verified PIHC3 project package, or open an existing writable project folder. ParaDev remembers the project for your next launch.",
  "project.onboarding.installAction": "Install PIHC3 package",
  "project.onboarding.installing": "Installing PIHC3 package",
  "project.onboarding.action": "Open existing project",
  "project.onboarding.opening": "Opening folder picker",
  "project.onboarding.hint":
    "Package installs are verified and saved under Documents/ParaDev/Projects. Existing projects must contain paradev.yaml. No Python, Conda, or hidden metadata changes are required.",
  "project.onboarding.installFailed":
    "PIHC3 package installation failed: {message}",
  "project.onboarding.cancelled":
    "No project is open. Select the PIHC3 folder that contains paradev.yaml to continue.",
  "project.onboarding.unavailable":
    "the folder is missing, unreadable, or no longer contains paradev.yaml",
  "project.onboarding.recoveryFailed":
    "ParaDev could not reopen {path}: {message}. Choose the project folder again.",
  "project.onboarding.discoveryFailed":
    "ParaDev could not load a usable project: {message}. Choose the PIHC3 project folder to continue.",
  "project.rememberedRecovery":
    "The saved project was unavailable. ParaDev opened {project} instead and updated the saved location.",
  "project.rememberedRecoveryDetail":
    "Previous location: {path}. Current location: {recoveredPath}. Recovery reason: {message}",
  "project.opening": "Opening project",
  "project.openingProject": "Opening {project}",
  "project.loading": "Loading project registry",
  "project.loadingProject": "Loading registry for {project}",
  "modules.section.title": "Modules",
  "modules.diagrams.title": "Diagrams",
  "modules.group.country": "Countries & Politics",
  "modules.group.military": "Military & Research",
  "modules.group.world": "World & Map",
  "modules.group.events": "Events & Extensions",
  "modules.group.shared": "Shared Content",
  "modules.group.other": "Other & Advanced",
  "config.section.title": "Configuration",
  "config.group.basic": "Basic",
  "config.group.project": "Project",
  "config.group.dependency": "Dependency",
  "config.general.title": "General",
  "config.appearance.title": "Appearance",
  "config.models.title": "Models",
  "config.projects.title": "Projects",
  "config.moduleDefaults.title": "Module defaults",
  "config.dependencies.title": "Dependencies",
  "config.page.label": "Configuration",
  "config.page.persisted": "Saved",
  "config.page.saving": "Saving",
  "config.page.loadFailed": "Load failed",
  "config.page.saveFailed": "Save failed",
  "config.page.saveFailedDetail":
    "Some settings were not saved. Check the desktop bridge and try again.",
  "config.field.sdkBacked": "Shared with builds and command-line ParaDev.",
  "config.field.aiRoute": "Shared with AI chat and HeavenBase routing.",
  "config.field.desktopOnly": "Only changes this app's previews.",
  "config.value.pending": "Pending",
  "config.status.warning": "Warning",
  "config.status.error": "Error",
  "config.status.missing": "Missing",
  "config.status.unknown": "Unknown",
  "config.general.workspace.title": "Workspace",
  "config.general.project.label": "Active project",
  "config.general.project.detail":
    "Project used by editing, build, and dependency-aware actions.",
  "config.general.projectRoot.label": "Project root",
  "config.general.projectRoot.detail": "Local folder used as the project root.",
  "config.general.language.label": "Language",
  "config.general.language.detail":
    "React shell locale. Chinese UI copy is maintained in sync with the English source dictionary.",
  "config.general.openTarget.label": "Default opener",
  "config.general.openTarget.detail":
    "Shared local-path opener for project, module, folder, and file actions.",
  "config.general.state.title": "Loaded SDK state",
  "config.general.state.projects": "Projects",
  "config.general.state.objects": "Objects",
  "config.general.state.families": "Families",
  "config.general.commandDefaults.title": "Command defaults",
  "config.general.projectName.label": "Config profile name",
  "config.general.projectName.detail":
    "Default ParaDev config profile label used by CLI config commands.",
  "config.general.cliOutput.label": "CLI output",
  "config.general.cliOutput.detail":
    "Default structured output for ParaDev CLI commands when no local output flag is passed.",
  "config.general.cliOutput.yaml": "YAML output",
  "config.general.cliOutput.json": "JSON output",
  "config.appearance.theme.title": "Maintained themes",
  "config.appearance.theme.active": "Active",
  "config.appearance.theme.apply": "Apply",
  "config.models.heavenbase.title": "HeavenBase LLM",
  "config.models.heavenbase.detail":
    "ParaDev uses the HeavenBase preset first, with manual route overrides available when needed.",
  "config.models.activeRoute": "Active route",
  "config.models.activePreset": "Active preset",
  "config.models.activeRouteValue": "Route: {route}",
  "config.models.preset": "Preset",
  "config.models.model": "Model",
  "config.models.provider": "Provider",
  "config.models.gateway": "Gateway",
  "config.models.keySource": "Key source",
  "config.models.baseUrl": "Base URL",
  "config.models.resolvedBaseUrl": "Resolved base URL",
  "config.models.testRoute": "Test route",
  "config.models.testHint": "Run a live route test from the desktop bridge.",
  "config.models.testRunning": "Testing {route} through HeavenBase.",
  "config.models.testResult.ready": "Route test succeeded.",
  "config.models.testResult.empty":
    "Route was reachable but returned an empty reply.",
  "config.models.testResult.warning":
    "Route test returned an unexpected reply.",
  "config.models.testResult.error":
    "Route test failed. Check preset, provider, model, key, and network.",
  "config.models.advancedOverrides.title": "Advanced route overrides",
  "config.models.advancedOverrides.detail":
    "Manual model, provider, and gateway values for non-default HeavenBase routes.",
  "config.models.presets.title": "Preset map",
  "config.models.presets.system.label": "System",
  "config.models.presets.system.detail": "Short orchestration calls",
  "config.models.presets.chat.label": "Chat",
  "config.models.presets.chat.detail": "Fast non-thinking answers",
  "config.models.presets.reason.label": "Reason",
  "config.models.presets.reason.detail": "Harder reasoning tasks",
  "config.models.presets.coder.label": "Coder",
  "config.models.presets.coder.detail": "Implementation and review work",
  "config.models.chatProfiles.title": "AI chat profiles",
  "config.models.chatProfiles.defaultRole": "default",
  "config.models.chatProfiles.defaultRoleLabel": "Default chat role",
  "config.models.chatProfiles.defaultRoleDetail":
    "New floating chat sessions open with this role.",
  "config.models.chatProfiles.label": "Label",
  "config.models.chatProfiles.detail": "Detail",
  "config.models.chatProfiles.prompt": "Prompt",
  "config.models.chatProfiles.operations": "Managed SDK actions",
  "config.models.chatProfiles.operationsDetail":
    "These links come from the Python desktop profile catalog and are not prompt-editable.",
  "config.models.chatProfiles.sources": "Context sources",
  "config.models.chatProfiles.sourcesDetail": "Selected by default: {sources}",
  "config.models.chatProfiles.noSources": "No context sources",
  "config.models.chatProfiles.sourceToggle":
    "Use {source} context for {profile}",
  "config.models.chatProfiles.reset": "Reset",
  "config.models.chatProfiles.resetAria": "Reset {profile} to default",
  "config.models.chatProfiles.save": "Save",
  "config.models.sourceKind.diagnostics": "Diagnostics",
  "config.models.sourceKind.project": "Project",
  "config.models.sourceKind.projectIndex": "Project index",
  "config.models.sourceKind.scriptedGui": "Scripted GUI",
  "config.models.sourceKind.selection": "Selection",
  "config.models.sourceKind.templates": "Templates",
  "config.models.sourceKind.unknown": "Unknown source",
  "config.projects.authoring.title": "Authoring defaults",
  "config.projects.preferredLanguage.label": "Project language",
  "config.projects.preferredLanguage.detail":
    "Sets the preferred localization and folder-title language once for this project. Modules inherit it without per-module metadata.",
  "config.projects.preferredLanguage.field": "Preferred project language",
  "config.projects.preferredLanguage.saving": "Saving project language…",
  "config.projects.preferredLanguage.english": "English",
  "config.projects.preferredLanguage.french": "French",
  "config.projects.preferredLanguage.german": "German",
  "config.projects.preferredLanguage.russian": "Russian",
  "config.projects.preferredLanguage.spanish": "Spanish",
  "config.projects.preferredLanguage.polish": "Polish",
  "config.projects.preferredLanguage.brazilianPortuguese":
    "Brazilian Portuguese",
  "config.projects.preferredLanguage.simplifiedChinese": "Simplified Chinese",
  "config.projects.preferredLanguage.japanese": "Japanese",
  "config.projects.preferredLanguage.korean": "Korean",
  "config.projects.paths.title": "Project paths",
  "config.projects.openPath": "Open {label} with {target}",
  "config.projects.openPathWithPath": "Open {label} ({path}) with {target}",
  "config.projects.openPathIndexed":
    "Open {label} {index} ({path}) with {target}",
  "config.projects.pathCount.sourceRoots": "{count} source roots",
  "config.projects.pathLabel.root": "project root",
  "config.projects.pathLabel.source": "source root",
  "config.projects.pathLabel.output": "output directory",
  "config.projects.pathLabel.build": "build cache",
  "config.projects.pathLabel.hoi4Root": "HOI4 game root",
  "config.projects.pathStatus.ready": "Ready",
  "config.projects.pathStatus.checking": "Checking",
  "config.projects.pathStatus.failed": "Failed",
  "config.projects.pathStatus.missing": "Missing",
  "config.projects.pathStatus.unreadable": "Unreadable",
  "config.projects.pathStatus.wrongKind": "Unsupported",
  "config.projects.pathStatus.generated": "Generated on build",
  "config.projects.pathStatus.steam": "Steam/default",
  "config.projects.pathStatus.partial": "{ready}/{total} ready",
  "config.projects.pathStatus.title.ready": "Path exists and is readable.",
  "config.projects.pathStatus.title.checking": "Waiting for SDK path status.",
  "config.projects.pathStatus.title.failed":
    "Path status could not be loaded: {message}",
  "config.projects.pathStatus.title.missing": "Path does not exist.",
  "config.projects.pathStatus.title.unreadable":
    "Path exists but is not readable.",
  "config.projects.pathStatus.title.wrongKind":
    "Path exists but is not a regular file or directory.",
  "config.projects.pathStatus.title.generated":
    "This path can be generated by a build.",
  "config.projects.pathStatus.title.steam":
    "HOI4 game root is not configured; Steam launch will be used.",
  "config.projects.pathStatus.title.partial":
    "{ready} of {total} source roots are ready.",
  "config.projects.buildDefaults.title": "Build defaults",
  "config.projects.hoi4LaunchMode.label": "HOI4 launch mode",
  "config.projects.hoi4LaunchMode.detail":
    "Default launcher used by Build page Run and Python desktop launch calls.",
  "config.projects.hoi4LaunchMode.field": "Launcher",
  "config.projects.hoi4LaunchMode.steam": "Steam launcher",
  "config.projects.hoi4LaunchMode.local": "Local app",
  "config.projects.hoi4GameRoot.label": "HOI4 game root",
  "config.projects.hoi4GameRoot.detail":
    "Optional local Hearts of Iron IV install path used by Local app launch mode.",
  "config.projects.hoi4GameRoot.field": "Install path",
  "config.projects.hoi4GameRoot.placeholder": "Auto-detect or use Steam",
  "config.projects.parallelism.label": "Build parallelism",
  "config.projects.parallelism.detail":
    "Maximum independent build-family workers used when no build command override is passed.",
  "config.projects.strictMetadata.label": "Strict metadata",
  "config.projects.strictMetadata.detail":
    "Treat unknown module or collection metadata keys as build blockers by default.",
  "config.projects.strictMetadata.enabled": "Block unknown metadata keys",
  "config.moduleDefaults.sizes.title": "Module default sizes",
  "config.moduleDefaults.sizes.detail":
    "Default editing and preview sizes for {project}.",
  "config.moduleDefaults.cache.title": "Thumbnail cache",
  "config.moduleDefaults.cache.detail":
    "Limits for cached previews that ParaDev reuses while browsing module source images.",
  "config.moduleDefaults.focusNode.label": "Focus trees",
  "config.moduleDefaults.focusNode.detail":
    "Default focus icon canvas and grid node size.",
  "config.moduleDefaults.technologyNode.label": "Technology folders",
  "config.moduleDefaults.technologyNode.detail":
    "Compact technology grid slot size.",
  "config.moduleDefaults.portrait.label": "Character portraits",
  "config.moduleDefaults.portrait.detail":
    "Default leader and advisor portrait preview height.",
  "config.moduleDefaults.flag.label": "Country flags",
  "config.moduleDefaults.flag.detail": "Default country flag preview width.",
  "config.moduleDefaults.thumbnailCache.label": "Instance thumbnails",
  "config.moduleDefaults.thumbnailCache.detail":
    "Maximum thumbnail cache payload for one source image.",
  "config.dependencies.status.installed": "Installed",
  "config.dependencies.imagemagick.detail":
    "Required for asset inspection, conversion, and DDS/TGA/image workflows.",
  "config.dependencies.path": "Path",
  "config.dependencies.version": "Version",
  "config.dependencies.installCommand": "Install command",
  "config.dependencies.check": "Check",
  "config.dependencies.install": "Install",
  "workspace.aria": "Workspace",
  "workspace.tabs.aria": "Workspace tabs",
  "workspace.tabs.previewTitle": "{title} (preview)",
  "workspace.action.closeTab": "Close {title}",
  "workspace.tabs.unsaved": "{title}, unsaved changes",
  "workspace.unsaved.title": "Unsaved authoring changes",
  "workspace.unsaved.tabDetail":
    "This is the last open view of unsaved module work. Discarding closes the tab without writing those drafts.",
  "workspace.unsaved.busy":
    "ParaDev is writing module changes. Keep this window open until the write finishes.",
  "workspace.unsaved.tabCloseFailedTitle": "ParaDev could not close this tab",
  "workspace.unsaved.tabCloseFailedDetail":
    "ParaDev could not safely release this editor's retained resources. Review the error below, then retry.",
  "workspace.unsaved.keepTabOpen": "Keep tab open",
  "workspace.unsaved.tryCloseTabAgain": "Try closing tab again",
  "workspace.unsaved.keepEditing": "Keep editing",
  "workspace.unsaved.discardAndClose": "Discard changes and close",
  "workspace.action.closeSplit": "Close split view",
  "workspace.action.splitRight": "Split editor right",
  "workspace.action.splitDisabled": "Open at least two tabs to split",
  "workspace.empty.title": "No tabs open",
  "workspace.empty.line": "Choose a module or config item from the left panel.",
  "workspace.page.management.title": "Management",
  "workspace.page.management.body":
    "Project management tools will appear here.",
  "workspace.page.developer.title": "Developer",
  "workspace.page.developer.body": "Developer tools will appear here.",
  "agents.aria": "Agent authoring",
  "agents.header.label": "Agent authoring",
  "agents.header.title": "Create safely with AI",
  "agents.header.detail":
    "Registry-backed tools for the active project",
  "agents.action.openChat": "Open AI chat",
  "agents.action.openEditing": "Review project",
  "agents.metrics.aria": "Active project authoring capabilities",
  "agents.metrics.families": "visible content types",
  "agents.metrics.templates": "authoring-ready templates",
  "agents.metrics.diagrams": "visual tree editors",
  "agents.ai.label": "Inside ParaDev",
  "agents.ai.title": "Describe the change you want",
  "agents.ai.body":
    "ParaDev AI can turn natural-language requests into a validated module batch or collection scaffold that opens in the regular editor for review.",
  "agents.ai.safety":
    "AI proposals never write project files automatically. Review the retained plan before applying it.",
  "agents.example.label": "Example request",
  "agents.example.prompt":
    "Create five new ideas named A, B, C, D, and E, with CIC modifiers increasing by 2%, 5%, 8%, 12%, and 16%.",
  "agents.external.label": "External agents",
  "agents.external.title": "Connect through the same SDK contracts",
  "agents.external.body":
    "Start ParaDev's local stdio MCP server, then let an MCP-capable agent discover Registry families, templates, source forms, diagrams, and guarded write plans.",
  "agents.external.command": "MCP server command",
  "agents.runtime.loading": "Resolving app-owned tools",
  "agents.runtime.ready": "Bundled MCP and skill ready",
  "agents.runtime.fallback": "CLI fallback shown",
  "agents.runtime.detail":
    "Installed builds resolve the exact bundled backend and skill paths automatically.",
  "agents.runtime.cwd": "Working directory:",
  "agents.runtime.error":
    "ParaDev could not resolve its bundled agent tools. The displayed CLI fallback was not verified.",
  "agents.skill.body":
    "Workflow guidance for safe module and collection discovery, dry planning, review, and apply.",
  "agents.prompt.label": "Project-aware starter prompt",
  "agents.copy.action": "Copy {label}",
  "agents.copy.copied": "Copied",
  "agents.copy.error":
    "Clipboard access is unavailable. Select and copy the text manually.",
  "agents.workflow.aria": "Safe agent authoring workflow",
  "agents.workflow.label": "One authoring model",
  "agents.workflow.title": "The GUI, CLI, and MCP follow the same guarded path",
  "agents.workflow.discover.title": "Discover",
  "agents.workflow.discover.body":
    "Read the active project's Registry content families and authoring-ready templates.",
  "agents.workflow.plan.title": "Dry-plan",
  "agents.workflow.plan.body":
    "Resolve canonical folders, localized names, source files, and resource slots without writing.",
  "agents.workflow.review.title": "Review",
  "agents.workflow.review.body":
    "Inspect exact files, diagnostics, and conflicts in ParaDev's retained editor plan.",
  "agents.workflow.apply.title": "Apply",
  "agents.workflow.apply.body":
    "Commit the reviewed plan atomically with revision guards and recovery reporting.",
  "management.aria": "Project management",
  "management.header.label": "Project management",
  "management.header.title": "Projects",
  "management.header.detail": "registered projects",
  "management.field.game": "Game",
  "management.field.version": "Version",
  "management.field.projectRoot": "Project root",
  "management.field.status": "Status",
  "management.field.sources": "Sources",
  "management.field.objects": "Objects",
  "management.game.hoi4": "Hearts of Iron IV",
  "management.value.unknown": "Unknown",
  "management.value.count": "{count}",
  "management.version.unset": "Not set",
  "management.status.active": "Active",
  "management.status.inactive": "Inactive",
  "management.action.active": "Active",
  "management.action.activate": "Activate",
  "management.action.build": "Build",
  "management.paths.aria": "Project paths",
  "management.path.root": "Project root",
  "management.path.source": "Source code",
  "management.path.sourceIndexed": "Source code {index}",
  "management.path.output": "Output directory",
  "management.path.build": "Build cache",
  "management.path.manifest": "Manifest",
  "management.active.detail":
    "{project} is the active project for editing and build actions.",
  "build.aria": "Build workspace",
  "build.header.label": "Compilation status",
  "build.header.title": "Build",
  "build.mode.aria": "Whole-project build mode",
  "build.mode.label": "Whole-project mode",
  "build.mode.cached": "Update existing output",
  "build.mode.full": "Clean output and rebuild",
  "build.mode.detail.cached":
    "Compiles the whole project and safely updates generated files without cleaning the output first.",
  "build.mode.detail.full":
    "Cleans ParaDev-owned generated output and build data, then compiles the whole project.",
  "build.launchMode.aria": "HOI4 launch mode",
  "build.launchMode.label": "Open HOI4",
  "build.launchMode.steam": "Steam launcher",
  "build.launchMode.local": "Local app",
  "build.launchMode.detail.steam": "Steam/default",
  "build.launchMode.detail.local": "Local root: {gameRoot}",
  "build.launchMode.detail.localMissing": "Set HOI4 game root in Config",
  "build.parallelism.aria": "Build parallelism",
  "build.parallelism.label": "Workers",
  "build.strictMetadata.aria": "Treat unknown metadata keys as build blockers",
  "build.strictMetadata.label": "Strict metadata",
  "build.action.refresh": "Refresh",
  "build.action.start": "Build",
  "build.action.interrupt": "Interrupt",
  "build.action.interruptTarget": "Interrupt {target}",
  "build.action.open": "Open",
  "build.action.rebuild": "Rebuild",
  "build.action.partialUpdate": "Safe partial update",
  "build.action.remove": "Remove",
  "build.action.runGame": "Start",
  "build.aiHandoff.title": "Opened from AI: {operation}",
  "build.aiHandoff.plan.detail":
    "Build plan context is open. No build is running; review buildable items and diagnostics first.",
  "build.aiHandoff.start.detail":
    "Build start context is open. No build started; the normal confirmation is still required.",
  "build.aiHandoff.role": "Task: {role}",
  "build.aiHandoff.context": "Context: {sources}",
  "build.confirmation.aria": "Build action confirmation",
  "build.confirmation.start.title": "Confirm whole-project build",
  "build.confirmation.start.detail.cached":
    "Compile the whole project and update existing generated output without cleaning it first.",
  "build.confirmation.start.detail.full":
    "Clean ParaDev-owned generated output and build data, then compile the whole project.",
  "build.confirmation.start.partial.title": "Confirm safe partial update",
  "build.confirmation.start.partial.detail":
    "Update only {target} without cleaning generated roots. The whole-project mode above does not apply.",
  "build.confirmation.interrupt.title": "Confirm interrupt",
  "build.confirmation.interrupt.detail":
    "Stop this build and keep the result in history.",
  "build.confirmation.cancel": "Cancel",
  "build.confirmation.continue": "Continue",
  "build.activePartial.aria": "Active partial updates",
  "build.activePartial.label": "Running partial update",
  "build.activePartial.meta": "{detail} · {percent}% · {elapsed} elapsed",
  "build.activePartial.elapsedUnknown": "elapsed time unavailable",
  "build.activePartial.progress": "Progress for {target}",
  "build.actionError.title": "Build action failed",
  "build.bridge.unavailable": "Desktop build bridge is not available.",
  "desktop.error.desktopApplicationRequired":
    "This action requires the ParaDev desktop application.",
  "desktop.error.readSourceRequiresProjectId":
    "A project id is required before local source text can be loaded.",
  "build.error.commandFailed": "Build command failed.",
  "build.refresh.pending": "Refreshing project build data",
  "build.refresh.done": "Build data refreshed",
  "build.refresh.failed": "Refresh failed: {message}",
  "build.start.started": "Started {mode}.",
  "build.start.partialStarted": "Started partial rebuild for {target}.",
  "build.start.completed": "Build completed.",
  "build.start.partialCompleted": "Partial rebuild completed for {target}.",
  "build.start.failed": "Build failed: {message}",
  "build.interrupt.done": "Build interrupted.",
  "build.interrupt.failed": "Interrupt failed: {message}",
  "build.launch.pending":
    "HOI4 launch handoff for {project} is waiting on the native game bridge.",
  "build.launch.readinessChecking":
    "Checking the generated mod and HOI4 launcher registration…",
  "build.launch.readinessFailed":
    "Launch readiness could not be checked: {message}. Use Refresh to retry.",
  "build.launch.requiresWholeProject":
    "Start unlocks after one successful whole-project Clean/Full or Cached build.",
  "build.launch.readiness.unsupportedGame":
    "This project does not target HOI4, so ParaDev cannot launch it here.",
  "build.launch.readiness.generatedDescriptorMissing":
    "Build the whole project once to create descriptor.mod before starting HOI4.",
  "build.launch.readiness.outputNotVisible":
    "The generated mod is outside HOI4's active user mod folder. Check the project output in Config, then rebuild. Output: {outputRoot}",
  "build.launch.readiness.launcherDescriptorMissing":
    "Build the whole project once to register this mod with the HOI4 launcher.",
  "build.launch.readiness.publicationInvalid":
    "Publication metadata is invalid. Run Update existing output for the whole project to repair it.",
  "build.launch.readiness.wholeProjectRequired":
    "Complete a whole-project build before starting HOI4. Partial updates preserve a valid baseline but cannot create one.",
  "build.launch.readiness.launcherRepair":
    "The HOI4 launcher registration is stale or unreadable. Rebuild the whole project to repair it.",
  "build.launch.started": "HOI4 launch requested from {gameRoot}",
  "build.launch.failed": "HOI4 launch failed: {message}",
  "build.openOutput.failed": "Output folder could not be opened: {message}",
  "build.status.failed": "Build status failed: {message}",
  "build.configRead.failed": "Build settings could not be loaded: {message}",
  "build.configWrite.failed": "Build settings could not be saved: {message}",
  "build.status.label": "Project status",
  "build.status.title.ready": "Ready",
  "build.status.title.running": "Compilation running",
  "build.status.title.parallel": "Partial rebuilds running",
  "build.status.title.completed": "Compilation complete",
  "build.status.title.interrupted": "Compilation interrupted",
  "build.status.title.failed": "Compilation failed",
  "build.status.title.blocked": "Compilation blocked",
  "build.status.pill.ready": "ready",
  "build.status.pill.active": "active",
  "build.status.pill.blocked": "blocked",
  "build.status.detail.ready": "Ready to compile the current project.",
  "build.status.detail.running": "Compiler is processing the current project.",
  "build.status.detail.completed":
    "Compilation finished and build data can be refreshed.",
  "build.status.detail.interrupted":
    "The current compilation run was interrupted before completion.",
  "build.status.detail.failed": "The native compilation command failed.",
  "build.status.detail.blocked":
    "{count} blocking diagnostics must be fixed before artifact emission.",
  "build.latestPartial.label": "Latest partial rebuild",
  "build.latestPartial.title.completed": "{target} rebuilt successfully",
  "build.latestPartial.title.failed": "{target} rebuild failed",
  "build.latestPartial.title.interrupted": "{target} rebuild was interrupted",
  "build.latestPartial.next.completed":
    "This rebuild checked only {target}. Use Build for a whole-project check.",
  "build.latestPartial.next.failed":
    "Review Build history, fix {target}, then run Build to verify the whole project before launching.",
  "build.latestPartial.next.interrupted":
    "Retry {target}, then run Build to verify the whole project before launching.",
  "build.diagnostics.failed":
    "Build diagnostics could not be loaded: {message}",
  "build.diagnostics.blockingTitle": "Fix these diagnostics before building",
  "build.diagnostics.blockingDetail":
    "{count} blocking diagnostics are preventing artifact emission.",
  "build.diagnostics.more": "{count} more blocking diagnostics",
  "build.diagnostics.severity.error": "Error",
  "build.diagnostics.severity.warning": "Warning",
  "build.progress.label": "Compilation progress",
  "build.progress.meta.count": "{phase} · {count}",
  "build.progress.detail.running": "Waiting for compiler progress",
  "build.progress.detail.parallelPartial":
    "{count} partial rebuilds are running.",
  "build.progress.phase.ready": "Ready",
  "build.progress.phase.waiting": "Starting compiler",
  "build.progress.phase.loadProject": "Opening project",
  "build.progress.phase.discoverModules": "Finding modules",
  "build.progress.phase.discoverCollections": "Finding collections",
  "build.progress.phase.basicCopy": "Copying static files",
  "build.progress.phase.collectionCompile": "Compiling collections",
  "build.progress.phase.entityCompile": "Compiling entities",
  "build.progress.phase.artifactGeneration": "Planning artifacts",
  "build.progress.phase.validatingPublication": "Validating publication",
  "build.progress.phase.postProcessing": "Post-processing",
  "build.progress.phase.complete": "Complete",
  "build.progress.phase.parallelPartial": "{count} partial rebuilds",
  "build.progress.phase.custom": "{phase}",
  "build.duration.seconds": "{count}s",
  "build.duration.minutes": "{count}m",
  "build.duration.minutesSeconds": "{minutes}m {seconds}s",
  "build.duration.hours": "{count}h",
  "build.duration.hoursMinutes": "{hours}h {minutes}m",
  "build.timestamp.full": "{year}-{month}-{day} {hour}:{minute}:{second}",
  "build.estimate.ready": "Avg {duration} from last {count} builds",
  "build.estimate.empty": "No build history yet",
  "build.kind.module": "Module",
  "build.kind.collection": "Collection",
  "build.kind.family": "Family",
  "build.metric.modules": "Modules",
  "build.metric.collections": "Collections",
  "build.metric.sources": "Source files",
  "build.metric.diagnostics": "Errors / diagnostics",
  "build.tabs.aria": "Build panel tabs",
  "build.tabs.items": "Buildable items",
  "build.tabs.history": "Build history",
  "build.entity.detail": "{sources} sources in {path}",
  "build.entity.familyDetail": "{modules} modules, {sources} sources",
  "build.entity.sourceProgress": "{current} / {total} sources",
  "build.history.title": "Buildable items",
  "build.history.empty": "No build history yet.",
  "build.history.mode.full": "Full build",
  "build.history.mode.partial": "Partial rebuild",
  "build.history.status.completed": "Success",
  "build.history.status.failed": "Failure",
  "build.history.status.interrupted": "Interrupted",
  "build.history.target.full": "Full project",
  "build.history.detail.runId": "Run ID",
  "build.history.detail.target": "Target",
  "build.history.detail.mode": "Mode",
  "build.history.detail.duration": "Duration",
  "build.history.detail.started": "Started",
  "build.history.detail.finished": "Finished",
  "build.history.detail.reason": "Reason",
  "build.history.detail.command": "Command",
  "build.history.detail.output": "Output",
  "build.history.detail.errorLog": "Error log",
  "build.history.detail.exitCode": "Exited with code {code}.",
  "build.history.detail.interruptedReason":
    "The run was interrupted before completion.",
  "build.history.detail.noReason": "No error reason was reported.",
  "build.history.remove": "Remove build history entry {id}",
  "workspace.primary": "Primary",
  "workspace.secondary": "Secondary",
  "workspace.split.label": "Split",
  "workspace.split.tabAria": "Secondary split tab",
  "workspace.scaffold.title": "{title} scaffold",
  "workspace.scaffold.body":
    "{subtitle} will attach future forms, previews, validation, and generators here.",
  "workspace.selectedModule.label": "Selected Module",
  "workspace.surface.tableAria": "Surface contracts",
  "workspace.surface.column.surface": "Surface",
  "workspace.surface.column.runtime": "Runtime",
  "workspace.surface.column.status": "Status",
  "workspace.module.label": "Project Browser",
  "workspace.module.unavailable.title": "SDK browser unavailable",
  "workspace.module.unavailable.body":
    "Open the ParaDev desktop application to load local SDK project data.",
  "workspace.module.loadFailed.title": "Module data failed to load",
  "workspace.module.loadFailed.body":
    "Scoped SDK data could not be loaded: {message}",
  "workspace.module.loading.title": "Loading {title} data",
  "workspace.module.loading.body":
    "Fetching scoped module data from the ParaDev SDK.",
  "workspace.module.empty.title": "No source rows",
  "workspace.module.empty.body":
    "This project has no visible source folders for the selected family.",
  "workspace.module.summary": "{count} objects · {sources} family source files",
  "workspace.module.summary.filtered":
    "{visible} of {total} objects shown · {sources} family source files",
  "workspace.module.summary.filteredPaged":
    "{visible} shown from {loaded} loaded of {total} objects · {sources} family source files",
  "workspace.module.summary.paged":
    "{loaded} of {total} objects loaded · {sources} family source files",
  "workspace.module.tableAria": "Project source browser",
  "workspace.module.column.object": "Object",
  "workspace.module.column.path": "Path",
  "workspace.module.column.sources": "Sources",
  "workspace.module.layout.canonical": "canonical",
  "workspace.module.layout.familyRoot": "source root",
  "workspace.module.moreSources": "+{count} more",
  "workspace.diagram.aria": "{title} diagram",
  "workspace.diagram.tabTitle": "{title} diagram",
  "workspace.diagram.open": "Open {title} diagram",
  "workspace.diagram.openTree": "Open {title}",
  "workspace.diagram.family.focusTree": "Focus tree",
  "workspace.diagram.family.technologyTree": "Technology tree",
  "workspace.diagram.family.mioTree":
    "Military Industrial Organization trait tree",
  "workspace.diagram.family.doctrineTree": "Doctrine tree",
  "workspace.diagram.title": "Diagram",
  "workspace.diagram.readOnly": "View only",
  "workspace.diagram.mio.readOnlyReason":
    "MIO editing is unavailable because the exact source projection is missing, unsafe, or has blocking diagnostics. Refresh after fixing the reported source issue.",
  "workspace.diagram.mio.positionUnavailable":
    "This MIO trait has no unambiguous editable source position.",
  "workspace.diagram.mio.scopeLabel": "Organization",
  "workspace.diagram.mio.scopeAria":
    "Military Industrial Organization diagram scope",
  "workspace.diagram.mio.scopeCount": "{count} organizations in this module",
  "workspace.diagram.mio.projectScopeCount": "{count} organizations in this project",
  "workspace.diagram.mio.scopeDirtyTitle":
    "Changes in this organization are retained when you switch.",
  "workspace.diagram.mio.scopeEmpty":
    "This module contains no MIO organization with a trait tree.",
  "workspace.diagram.mio.projectScopeEmpty":
    "This project contains no MIO organization with a trait tree.",
  "workspace.diagram.nodePositionReadOnly":
    "This node has no unambiguous editable source position. You can inspect it, but it cannot be moved.",
  "workspace.diagram.scopeLabel": "Focus tree",
  "workspace.diagram.scopeAria": "Focus tree diagram scope",
  "workspace.diagram.scopeCount": "{count} focus trees",
  "workspace.diagram.scopeDirtyTitle":
    "Apply or discard diagram changes before switching focus trees.",
  "workspace.diagram.collectionCreate.open": "New collection",
  "workspace.diagram.collectionCreate.eyebrow": "Collection authoring",
  "workspace.diagram.collectionCreate.title": "Create {title}",
  "workspace.diagram.collectionCreate.detail":
    "Define one standalone {title} collection. ParaDev uses its registered project template to create the correctly named source folder and owned files.",
  "workspace.diagram.collectionCreate.guidance":
    "Choose the essential values, then review the exact target files before ParaDev writes anything.",
  "workspace.diagram.collectionCreate.collectionId": "Collection ID",
  "workspace.diagram.collectionCreate.invalidId":
    "Use an ID that starts with a letter or underscore and contains only letters, numbers, dots, hyphens, or underscores.",
  "workspace.diagram.collectionCreate.noTemplate":
    "This project does not expose an authoring-ready collection template for {title}.",
  "workspace.diagram.collectionCreate.review": "Review files",
  "workspace.diagram.collectionCreate.reviewing": "Building review",
  "workspace.diagram.collectionCreate.back": "Back to fields",
  "workspace.diagram.collectionCreate.ready": "Ready to create",
  "workspace.diagram.collectionCreate.blocked":
    "This {title} collection cannot be created yet.",
  "workspace.diagram.collectionCreate.confirm":
    "I reviewed these exact project files and want to create them.",
  "workspace.diagram.collectionCreate.apply": "Create collection",
  "workspace.diagram.collectionCreate.applying": "Creating collection",
  "workspace.diagram.collectionCreate.refreshFailed":
    "The collection was created, but the project view could not refresh: {message}",
  "workspace.diagram.loading.title": "Loading {title} diagram",
  "workspace.diagram.loading.body":
    "Fetching scoped diagram data from the ParaDev SDK.",
  "workspace.diagram.loadFailed.title": "Diagram data failed to load",
  "workspace.diagram.rendererUnsupported":
    "This project uses the diagram renderer “{renderer}”, which is not installed in this ParaDev app.",
  "workspace.diagram.empty": "No diagram nodes",
  "workspace.diagram.node": "node",
  "workspace.diagram.nodes": "nodes",
  "workspace.diagram.link": "link",
  "workspace.diagram.links": "links",
  "workspace.diagram.mode.absolute": "Pinned",
  "workspace.diagram.mode.relative": "Relative",
  "workspace.diagram.mode.auto": "Auto",
  "workspace.diagram.edgeSummary": "Diagram relationship types",
  "workspace.diagram.edge.tree": "Tree",
  "workspace.diagram.edge.dependency": "Prereq",
  "workspace.diagram.edge.path": "Path",
  "workspace.diagram.edge.reference": "Reference",
  "workspace.diagram.zoomControls": "Diagram zoom controls",
  "workspace.diagram.zoomOut": "Zoom diagram out",
  "workspace.diagram.zoomReset": "Reset diagram zoom",
  "workspace.diagram.zoomIn": "Zoom diagram in",
  "workspace.diagram.panControls": "Diagram pan controls",
  "workspace.diagram.panUp": "Pan diagram up",
  "workspace.diagram.panLeft": "Pan diagram left",
  "workspace.diagram.panReset": "Reset diagram pan",
  "workspace.diagram.centerSelected": "Center selected node",
  "workspace.diagram.panRight": "Pan diagram right",
  "workspace.diagram.panDown": "Pan diagram down",
  "workspace.diagram.fitView": "Fit diagram to view",
  "workspace.diagram.exportJson": "Export JSON",
  "workspace.diagram.importJson": "Import JSON",
  "workspace.diagram.jsonPanel": "Diagram JSON",
  "workspace.diagram.jsonText": "Diagram JSON text",
  "workspace.diagram.importError.invalidJson":
    "Diagram JSON is not valid JSON.",
  "workspace.diagram.importError.rootObject":
    "Diagram JSON root must be an object.",
  "workspace.diagram.importError.schemaVersion":
    "Diagram JSON schemaVersion must be 1.",
  "workspace.diagram.importError.gridSizePositive":
    "Diagram JSON gridSizePx must be a positive number.",
  "workspace.diagram.importError.nodesArray":
    "Diagram JSON nodes must be an array.",
  "workspace.diagram.importError.edgesArray":
    "Diagram JSON edges must be an array.",
  "workspace.diagram.importError.nodeIdsUnique":
    "Diagram JSON nodes must have unique ids.",
  "workspace.diagram.importError.edgeIdsUnique":
    "Diagram JSON edges must have unique ids.",
  "workspace.diagram.importError.edgeRelationshipsUnique":
    "Diagram JSON edges must have unique kind/source/target relationships.",
  "workspace.diagram.importError.edgeCanonicalId":
    "Diagram edge {edgeId} must use canonical id {canonicalId}.",
  "workspace.diagram.importError.treeEdgeParentMismatch":
    "Diagram tree edge {edgeId} disagrees with parent {parentId} for node {nodeId}.",
  "workspace.diagram.importError.nodeMissingTreeEdge":
    "Diagram node {nodeId} has parent {parentId} but no matching tree edge.",
  "workspace.diagram.importError.dependencyCycle":
    "Diagram dependency edge {edgeId} creates a cycle.",
  "workspace.diagram.importError.nodeObject":
    "Diagram node at index {index} must be an object.",
  "workspace.diagram.importError.nodeId":
    "Diagram node at index {index} must have an id.",
  "workspace.diagram.importError.nodeMode":
    "Diagram node {nodeId} must have a mode.",
  "workspace.diagram.importError.nodeUnsupportedMode":
    "Diagram node {nodeId} has unsupported mode {mode}.",
  "workspace.diagram.importError.nodeOrderNumeric":
    "Diagram node {nodeId} must have a numeric order.",
  "workspace.diagram.importError.nodeWidthNumeric":
    "Diagram node {nodeId} must have a numeric width.",
  "workspace.diagram.importError.nodeWidthPositive":
    "Diagram node {nodeId} width must be positive.",
  "workspace.diagram.importError.nodeHeightNumeric":
    "Diagram node {nodeId} must have a numeric height.",
  "workspace.diagram.importError.nodeHeightPositive":
    "Diagram node {nodeId} height must be positive.",
  "workspace.diagram.importError.nodeXNumeric":
    "Diagram node {nodeId} x must be numeric.",
  "workspace.diagram.importError.nodeYNumeric":
    "Diagram node {nodeId} y must be numeric.",
  "workspace.diagram.importError.nodeDxNumeric":
    "Diagram node {nodeId} dx must be numeric.",
  "workspace.diagram.importError.nodeDyNumeric":
    "Diagram node {nodeId} dy must be numeric.",
  "workspace.diagram.importError.nodeRelativePositionKindString":
    "Diagram node {nodeId} relativePositionKind must be a string.",
  "workspace.diagram.importError.nodeUnsupportedRelativePositionKind":
    "Diagram node {nodeId} has unsupported relativePositionKind {kind}.",
  "workspace.diagram.importError.nodePriorityNumeric":
    "Diagram node {nodeId} priority must be numeric.",
  "workspace.diagram.importError.nodeSubtreeWidthNumeric":
    "Diagram node {nodeId} subtreeWidth must be numeric.",
  "workspace.diagram.importError.nodeSubtreeWidthPositive":
    "Diagram node {nodeId} subtreeWidth must be positive.",
  "workspace.diagram.importError.nodeSubtreeWidthDeltaNumeric":
    "Diagram node {nodeId} subtreeWidthDelta must be numeric.",
  "workspace.diagram.importError.nodeSubtreeCenterOffsetNumeric":
    "Diagram node {nodeId} subtreeCenterOffset must be numeric.",
  "workspace.diagram.importError.edgeObject":
    "Diagram edge at index {index} must be an object.",
  "workspace.diagram.importError.edgeId":
    "Diagram edge at index {index} must have an id.",
  "workspace.diagram.importError.edgeSource":
    "Diagram edge {edgeId} must have a source.",
  "workspace.diagram.importError.edgeTarget":
    "Diagram edge {edgeId} must have a target.",
  "workspace.diagram.importError.edgeKind":
    "Diagram edge {edgeId} must have a kind.",
  "workspace.diagram.importError.edgeUnsupportedKind":
    "Diagram edge {edgeId} has unsupported kind {kind}.",
  "workspace.diagram.importError.edgeSelf":
    "Diagram edge {edgeId} cannot target itself.",
  "workspace.diagram.importError.edgeMissingSource":
    "Diagram edge {edgeId} references missing source {nodeId}.",
  "workspace.diagram.importError.edgeMissingTarget":
    "Diagram edge {edgeId} references missing target {nodeId}.",
  "workspace.diagram.importError.layoutOptionsObject":
    "Diagram layoutOptions must be an object.",
  "workspace.diagram.importError.layoutOptionsRootXNumeric":
    "Diagram layoutOptions rootX must be numeric.",
  "workspace.diagram.importError.layoutOptionsRootYNumeric":
    "Diagram layoutOptions rootY must be numeric.",
  "workspace.diagram.importError.layoutOptionsSiblingGapNumeric":
    "Diagram layoutOptions siblingGap must be numeric.",
  "workspace.diagram.importError.layoutOptionsLayerGapNumeric":
    "Diagram layoutOptions layerGap must be numeric.",
  "workspace.diagram.importError.viewportObject":
    "Diagram viewport must be an object.",
  "workspace.diagram.importError.viewportXNumeric":
    "Diagram viewport x must be numeric.",
  "workspace.diagram.importError.viewportYNumeric":
    "Diagram viewport y must be numeric.",
  "workspace.diagram.importError.viewportZoomNumeric":
    "Diagram viewport zoom must be numeric.",
  "workspace.diagram.importError.viewportZoomPositive":
    "Diagram viewport zoom must be positive.",
  "workspace.diagram.importError.removesNonFocus":
    "Imported diagram removes non-focus metadata node {nodeId} that cannot be deleted through diagram import.",
  "workspace.diagram.importError.missingPayload":
    "Imported diagram node {nodeId} is missing ParaDev metadata payload.",
  "workspace.diagram.importError.missingEmbeddedFocusId":
    "Imported diagram node {nodeId} is missing ParaDev embedded focus id.",
  "workspace.diagram.importError.mismatchedEmbeddedFocusId":
    "Imported diagram node {nodeId} has embedded focus id {embeddedId} that disagrees with the node id.",
  "workspace.diagram.importError.nonFocusParent":
    "Imported diagram node {nodeId} cannot use non-focus parent {parentId}.",
  "workspace.diagram.importError.outsideEntity":
    "Imported diagram node {nodeId} targets metadata entity {itemId} outside the current diagram.",
  "workspace.diagram.importError.outsideObject":
    "Imported diagram node {nodeId} targets metadata object {objectId} outside {itemId}.",
  "workspace.diagram.importError.addsNonFocus":
    "Imported diagram node {nodeId} adds a non-focus metadata node that cannot be saved.",
  "workspace.diagram.importError.changesNewFocusPayload":
    "Imported diagram node {nodeId} changes ParaDev metadata payload for a new focus node.",
  "workspace.diagram.importError.changesCurrentPayload":
    "Imported diagram node {nodeId} changes ParaDev metadata payload for the current diagram.",
  "workspace.diagram.importError.edgeFocusNonFocus":
    "Imported diagram edge {edgeId} cannot connect focus node {focusId} to non-focus node {nonFocusId}.",
  "workspace.diagram.importError.edgeDifferentScopes":
    "Imported diagram edge {edgeId} cannot connect nodes from different diagram source scopes.",
  "workspace.diagram.closeJson": "Close diagram JSON",
  "workspace.diagram.undo": "Undo diagram edit",
  "workspace.diagram.redo": "Redo diagram edit",
  "workspace.diagram.search": "Search diagram nodes",
  "workspace.diagram.searchIdle": "{count} nodes",
  "workspace.diagram.searchResult": "{current} / {total}",
  "workspace.diagram.searchPrevious": "Previous search result",
  "workspace.diagram.searchNext": "Next search result",
  "workspace.diagram.imagesProgress": "Images {hydrated}/{total}",
  "workspace.diagram.imagesProgressTitle":
    "Image loading: {completed}/{total} checked, {hydrated} loaded",
  "workspace.diagram.minimap": "Diagram minimap",
  "workspace.diagram.minimapViewport": "Visible diagram area",
  "workspace.diagram.selectedNode": "Selected node",
  "workspace.diagram.openedNodeInfo": "Opened node info",
  "workspace.diagram.closeNodeInfo": "Close node info",
  "workspace.diagram.openNodeModule": "Open module item",
  "workspace.diagram.openedNodeGrid": "Grid",
  "workspace.diagram.openedNodeSourceInfo": "Source info",
  "workspace.diagram.selectedPosition": "Grid {x}, {y}",
  "workspace.diagram.selectedKind": "Kind",
  "workspace.diagram.selectedKindFocus": "Embedded focus",
  "workspace.diagram.selectedKindNode": "Diagram node",
  "workspace.diagram.selectedStoredPosition": "Stored",
  "workspace.diagram.selectedStoredAbsolute": "Pinned {x}, {y}",
  "workspace.diagram.selectedStoredRelative": "Offset {dx}, {dy} from {parent}",
  "workspace.diagram.selectedStoredRelativeRoot": "Offset {dx}, {dy}",
  "workspace.diagram.selectedStoredAuto": "Auto from parent",
  "workspace.diagram.selectedStoredAutoRoot": "Auto root",
  "workspace.diagram.selectedSize": "Size",
  "workspace.diagram.selectedPriority": "Priority",
  "workspace.diagram.selectedSubtreeWidth": "Lane",
  "workspace.diagram.selectedSubtreeWidthDelta": "Lane +",
  "workspace.diagram.selectedSubtreeCenterOffset": "Center",
  "workspace.diagram.hoverId": "ID",
  "workspace.diagram.hoverGrid": "Grid",
  "workspace.diagram.hoverMode": "Mode",
  "workspace.diagram.hoverSize": "Size",
  "workspace.diagram.hoverOffset": "Offset",
  "workspace.diagram.hoverPriority": "Priority",
  "workspace.diagram.hoverWidth": "Width",
  "workspace.diagram.hoverWidthDelta": "Width delta",
  "workspace.diagram.hoverCenter": "Center",
  "workspace.diagram.setLayoutHints": "Set selected node PIHC layout hints",
  "workspace.diagram.setLayoutHintsAction": "Set hints",
  "workspace.diagram.priorityAria": "Selected node legacy priority",
  "workspace.diagram.subtreeWidthAria": "Selected node legacy lane width",
  "workspace.diagram.subtreeWidthDeltaAria":
    "Selected node legacy lane width delta",
  "workspace.diagram.subtreeCenterOffsetAria":
    "Selected node legacy center offset",
  "workspace.diagram.selectedFocusTree": "Focus tree",
  "workspace.diagram.selectedItem": "Item",
  "workspace.diagram.selectedModule": "Module",
  "workspace.diagram.selectedDraft": "Pending source change",
  "workspace.diagram.modeControls": "Set selected node coordinate mode",
  "workspace.diagram.setModeAbsolute": "Set selected node to pinned mode",
  "workspace.diagram.setModeRelative": "Set selected node to relative mode",
  "workspace.diagram.setModeAuto": "Set selected node to auto mode",
  "workspace.diagram.setPosition": "Set selected node grid position",
  "workspace.diagram.setPositionAction": "Set position",
  "workspace.diagram.positionX": "X",
  "workspace.diagram.positionY": "Y",
  "workspace.diagram.positionXAria": "Selected node X grid coordinate",
  "workspace.diagram.positionYAria": "Selected node Y grid coordinate",
  "workspace.diagram.setParent": "Set parent",
  "workspace.diagram.setParentTarget": "Parent",
  "workspace.diagram.setParentTargetAria": "Selected parent node id",
  "workspace.diagram.setParentPlaceholder": "Node id",
  "workspace.diagram.setParentAction": "Set parent",
  "workspace.diagram.clearParent": "Make selected node a root",
  "workspace.diagram.clearParentAction": "Make root",
  "workspace.diagram.selectedParent": "Parent {parent}",
  "workspace.diagram.selectedPath": "Path {count}",
  "workspace.diagram.selectedSiblingOrder": "Sibling {index} of {count}",
  "workspace.diagram.selectedSiblings": "Siblings {count}",
  "workspace.diagram.selectedChildren": "Children {count}",
  "workspace.diagram.selectedBranchSize":
    "Branch {count} nodes / {descendantCount} {descendantLabel}",
  "workspace.diagram.selectedBranchDescendant": "descendant",
  "workspace.diagram.selectedBranchDescendants": "descendants",
  "workspace.diagram.selectedPrerequisites": "Prereq {ids}",
  "workspace.diagram.selectedUnlocks": "Unlocks {ids}",
  "workspace.diagram.selectedReferences": "References {ids}",
  "workspace.diagram.exactRelationships": "Exact source relationships",
  "workspace.diagram.selectRelationshipEndpoint":
    "Select relationship endpoint {id}",
  "workspace.diagram.selectAncestor": "Select ancestor {id}",
  "workspace.diagram.selectSibling": "Select sibling {id}",
  "workspace.diagram.selectPrerequisite": "Select prerequisite {id}",
  "workspace.diagram.selectUnlock": "Select unlocked node {id}",
  "workspace.diagram.selectReference": "Select referenced node {id}",
  "workspace.diagram.selectTreeParent": "Select parent node {id}",
  "workspace.diagram.selectTreeChild": "Select child node {id}",
  "workspace.diagram.removePrerequisite": "Remove prerequisite {id}",
  "workspace.diagram.removeUnlock": "Remove unlock {id}",
  "workspace.diagram.removeReference": "Remove reference {id}",
  "workspace.diagram.addDependency": "Add prerequisite",
  "workspace.diagram.addDependencySource": "Prereq",
  "workspace.diagram.addDependencySourceAria": "Prerequisite source node id",
  "workspace.diagram.addDependencyPlaceholder": "Node id",
  "workspace.diagram.addDependencyAction": "Add prerequisite",
  "workspace.diagram.pickDependency": "Pick prerequisite on canvas",
  "workspace.diagram.pickDependencyHint":
    "Pick a prerequisite node on the canvas",
  "workspace.diagram.addUnlock": "Add unlock",
  "workspace.diagram.addUnlockTarget": "Unlock",
  "workspace.diagram.addUnlockTargetAria": "Unlocked target node id",
  "workspace.diagram.addUnlockPlaceholder": "Node id",
  "workspace.diagram.addUnlockAction": "Add unlock",
  "workspace.diagram.pickUnlock": "Pick unlock on canvas",
  "workspace.diagram.pickUnlockHint": "Pick an unlocked node on the canvas",
  "workspace.diagram.addReference": "Add reference",
  "workspace.diagram.addReferenceTarget": "Reference",
  "workspace.diagram.addReferenceTargetAria": "Reference target node id",
  "workspace.diagram.addReferencePlaceholder": "Node id",
  "workspace.diagram.addReferenceAction": "Add reference",
  "workspace.diagram.pickReference": "Pick reference on canvas",
  "workspace.diagram.pickReferenceHint": "Pick a reference node on the canvas",
  "workspace.diagram.selectedSource": "Source {source}",
  "workspace.diagram.dragHint.node": "Drag node",
  "workspace.diagram.dragHint.activeSubtree": "Drag branch",
  "workspace.diagram.dragHint.activeNodeOnly": "Drag node only",
  "workspace.diagram.dragHint.activeRelayoutDescendants":
    "Drag node and auto-layout descendants",
  "workspace.diagram.dragHint.subtree": "Shift-drag branch",
  "workspace.diagram.dragHint.nodeOnly": "Alt-drag node only",
  "workspace.diagram.dragHint.relayoutDescendants":
    "Cmd/Ctrl-drag node and auto-layout descendants",
  "workspace.diagram.moveSelected": "Move selected node",
  "workspace.diagram.moveMode": "Selected node move mode",
  "workspace.diagram.moveMode.node": "Node",
  "workspace.diagram.moveMode.nodeTitle": "Move selected node",
  "workspace.diagram.moveMode.subtree": "Branch",
  "workspace.diagram.moveMode.subtreeTitle": "Move selected branch",
  "workspace.diagram.moveMode.nodeOnly": "Node only",
  "workspace.diagram.moveMode.nodeOnlyTitle": "Move selected node only",
  "workspace.diagram.moveMode.relayoutDescendants": "Reflow",
  "workspace.diagram.moveMode.relayoutDescendantsTitle":
    "Move selected node and auto-layout descendants",
  "workspace.diagram.moveModeHint.subtree": "Moves branch together",
  "workspace.diagram.moveModeHint.node": "Relative descendants follow",
  "workspace.diagram.moveModeHint.nodeOnly": "Keeps descendants in place",
  "workspace.diagram.moveModeHint.relayoutDescendants":
    "Recalculates descendants",
  "workspace.diagram.selectedMoveFootprint": "Move footprint",
  "workspace.diagram.centerMoveFootprint": "Center move footprint",
  "workspace.diagram.selectMoveAffected": "Select affected node {id}",
  "workspace.diagram.moreMoveAffected": "+{count} more",
  "workspace.diagram.focusGridBadge": "x {x} y {y}",
  "workspace.diagram.focusRelativeBadge": "dx {dx} dy {dy}",
  "workspace.diagram.moveImpactOne": "Affects 1 node",
  "workspace.diagram.moveImpactMany": "Affects {count} nodes",
  "workspace.diagram.pinAll": "Pin all nodes",
  "workspace.diagram.pinSelected": "Pin selected node",
  "workspace.diagram.pinSubtree": "Pin selected branch",
  "workspace.diagram.makeRelativeSelected": "Make selected node relative",
  "workspace.diagram.makeRelativeSubtree": "Make selected branch relative",
  "workspace.diagram.unpinAll": "Unpin all nodes",
  "workspace.diagram.unpinSubtree": "Unpin selected branch",
  "workspace.diagram.unpinSelected": "Unpin selected node",
  "workspace.diagram.autoLayoutAll": "Auto layout diagram",
  "workspace.diagram.autoLayoutDescendants": "Auto layout selected descendants",
  "workspace.diagram.autoLayoutSubtree": "Auto layout selected branch",
  "workspace.diagram.autoLayoutSelected": "Auto layout selected node",
  "workspace.diagram.addRootFocus": "Add root focus",
  "workspace.diagram.addModule": "Create in {title}",
  "workspace.diagram.moduleCreate.eyebrow": "Extension-backed authoring",
  "workspace.diagram.moduleCreate.title": "Create in {title}",
  "workspace.diagram.moduleCreate.detail":
    "Choose a registered {title} template, preview its exact files, then install the reviewed plan as one guarded transaction.",
  "workspace.diagram.moduleCreate.guidance":
    "Required fields, source files, hidden system state, and folder naming come from the active project extension. After creation, open the new graph item to add optional resources or edit advanced fields.",
  "workspace.diagram.moduleCreate.refreshFailed":
    "The {title} module was created, but the diagram refresh failed: {message}",
  "workspace.diagram.nodeCreate.eyebrow": "Extension-backed graph authoring",
  "workspace.diagram.nodeCreate.guidance":
    "Fields, source insertion, localization, and resource defaults come from the active project extension. Preview the exact edits, then apply that reviewed plan as one guarded transaction.",
  "workspace.diagram.nodeCreate.preview": "Preview graph item",
  "workspace.diagram.nodeCreate.previewAgain": "Preview again",
  "workspace.diagram.nodeCreate.previewing": "Previewing…",
  "workspace.diagram.nodeCreate.apply": "Add graph item",
  "workspace.diagram.nodeCreate.applying": "Adding graph item…",
  "workspace.diagram.nodeCreate.reviewTitle": "Exact source edits",
  "workspace.diagram.nodeCreate.replacement":
    "{path}, characters {start}–{end}",

  "workspace.diagram.reorderSiblingEarlier":
    "Move selected node earlier among siblings",
  "workspace.diagram.reorderSiblingLater":
    "Move selected node later among siblings",
  "workspace.diagram.insertChildFocus": "Insert child focus",
  "workspace.diagram.removeFocus": "Remove selected focus and keep children",
  "workspace.diagram.removeFocusSubtree": "Remove selected focus branch",
  "workspace.diagram.moveSubtreeUp": "Move selected branch up",
  "workspace.diagram.moveSubtreeLeft": "Move selected branch left",
  "workspace.diagram.moveSubtreeRight": "Move selected branch right",
  "workspace.diagram.moveSubtreeDown": "Move selected branch down",
  "workspace.diagram.moveNodeOnlyUp": "Move selected node only up",
  "workspace.diagram.moveNodeOnlyLeft": "Move selected node only left",
  "workspace.diagram.moveNodeOnlyRight": "Move selected node only right",
  "workspace.diagram.moveNodeOnlyDown": "Move selected node only down",
  "workspace.diagram.moveRelayoutDescendantsUp":
    "Move selected node up and auto-layout descendants",
  "workspace.diagram.moveRelayoutDescendantsLeft":
    "Move selected node left and auto-layout descendants",
  "workspace.diagram.moveRelayoutDescendantsRight":
    "Move selected node right and auto-layout descendants",
  "workspace.diagram.moveRelayoutDescendantsDown":
    "Move selected node down and auto-layout descendants",
  "workspace.diagram.moveUp": "Move selected node up",
  "workspace.diagram.moveLeft": "Move selected node left",
  "workspace.diagram.moveRight": "Move selected node right",
  "workspace.diagram.moveDown": "Move selected node down",
  "workspace.diagram.apply": "Apply diagram",
  "workspace.diagram.applying": "Applying diagram",
  "workspace.diagram.applyNoChanges": "No diagram changes to apply.",
  "workspace.diagram.applyPreview": "Will write {writable} · Skip {skipped}",
  "workspace.diagram.applyPreviewSkip": "Skip {entity}",
  "workspace.diagram.applyPreviewWrite": "Write {entity}",
  "workspace.diagram.applyReview": "Review apply scope",
  "workspace.diagram.applyReviewAria": "Diagram apply scope",
  "workspace.diagram.applyReviewDraft": "Draft text",
  "workspace.diagram.applyReviewFirst": "Review scope first",
  "workspace.diagram.applyReviewFirstTitle":
    "Review writable and skipped metadata before applying.",
  "workspace.diagram.applyReviewSkip": "Skip",
  "workspace.diagram.applyReviewWrite": "Write",
  "workspace.diagram.applyBlocked": "Cannot apply diagram",
  "workspace.diagram.applyDraftUnavailable":
    "Some diagram metadata drafts could not be generated.",
  "workspace.diagram.applyWritable": "Apply writable rows",
  "workspace.diagram.applyWritableTitle":
    "Apply the writable diagram metadata rows.",
  "workspace.diagram.applyUnavailable":
    "Diagram changes do not target writable metadata.",
  "workspace.diagram.sourceConflict":
    "Project sources changed after this diagram draft began. The draft is preserved but cannot be applied; discard it to load the current graph.",
  "workspace.diagram.dirtySummary": "Source changes: {count}",
  "workspace.diagram.dirtySummaryMixed":
    "Source changes: {count} · Ready {writable} · Skipped {skipped}",
  "workspace.diagram.dirtyScope": "Affected metadata",
  "workspace.diagram.dirtyMissingPath": "No writable metadata path",
  "workspace.diagram.dirtyDraftUnavailable": "No generated metadata draft",
  "workspace.diagram.discard": "Discard diagram",
  "workspace.module.editor.listAria": "Module entities",
  "workspace.module.editor.detailsAria": "Entity editor",
  "workspace.module.editor.search": "Search objects, ids, paths",
  "workspace.module.editor.searchAria": "Search module entities",
  "workspace.module.editor.searchCatalog": "Search internal module ID",
  "workspace.module.editor.searchCatalogAria":
    "Search the project index by internal module ID",
  "workspace.module.editor.entities": "Entity results",
  "workspace.module.editor.resultsSummary": "{count} results",
  "workspace.module.editor.filteredResultsSummary":
    "{visible} of {total} results",
  "workspace.module.editor.selectedSummary": "{count} selected",
  "workspace.module.editor.selectionTools": "Selection tools",
  "workspace.module.editor.selectVisible": "Select visible results",
  "workspace.module.editor.clearVisibleSelection": "Clear visible selection",
  "workspace.module.editor.selectFiltered": "Select loaded filtered results",
  "workspace.module.editor.selectAll": "Select all loaded objects",
  "workspace.module.editor.clearSelection": "Clear selection",
  "workspace.module.editor.selectEntity": "Select {title}",
  "workspace.module.editor.new": "New",
  "workspace.module.editor.newTitle": "New {title}",
  "workspace.module.editor.emptyEntities": "No drafts or source rows",
  "workspace.module.editor.catalogLoadedSummary": "{loaded} of {total} loaded",
  "workspace.module.editor.directShownSummary":
    "Showing {shown} of {total} matching objects",
  "workspace.module.editor.directShowMore": "Show more",
  "workspace.module.editor.catalogLoading": "Loading module rows…",
  "workspace.module.editor.catalogLoadMore": "Load more",
  "workspace.module.editor.catalogRetry": "Retry",
  "workspace.module.editor.catalogHydrating": "Loading editor sources…",
  "workspace.module.editor.catalogMissingTitle":
    "Optional project index is not prepared",
  "workspace.module.editor.catalogMissingDetail":
    "Modules discovered directly from the project remain editable and buildable below. Prepare the full index only for faster search and paging across very large families.",
  "workspace.module.editor.catalogPrepareWarning":
    "For PIHC3 this takes about 14 minutes, uses about 2.1 GiB of disk space, and cannot currently be cancelled. Keep ParaDev open until it finishes.",
  "workspace.module.editor.catalogPrepare": "Prepare optional project index",
  "workspace.module.editor.catalogPreparing": "Preparing project index…",
  "workspace.module.editor.catalogMutationFailed":
    "The module changed, but the project index could not be updated: {message}. The files are already changed, so do not click Apply again. Catalog browsing is paused to avoid stale results.",
  "workspace.module.editor.catalogMutationUnknown":
    "The module changed, but ParaDev could not confirm that the project index was updated. The files are already changed, so do not click Apply again. Catalog browsing is paused to avoid stale results.",
  "workspace.module.editor.catalogMutationPreparing":
    "Wait for project index preparation to finish before creating or applying modules.",
  "workspace.module.editor.catalogMutationDirtyBlocked":
    "The project index is out of sync. Repair it before creating, renaming, or removing modules. You can still apply source-file edits that do not change the module folder.",
  "workspace.module.editor.catalogRepair": "Repair project index (~14 min)",
  "workspace.module.editor.catalogRepairWarning":
    "Rebuild the project index only when you are ready. For PIHC3 this takes about 14 minutes, uses about 2.1 GiB of disk space, and cannot currently be cancelled.",
  "workspace.module.editor.ambiguousModuleMutation":
    "ParaDev found {moduleId} in more than one source folder. Rename and removal are blocked to protect your files. Make the module IDs unique, then refresh sources.",
  "workspace.module.editor.ambiguousEntityMutation":
    "ParaDev found {id} in more than one source folder. Rename and removal are blocked to protect your files. Make the IDs unique, then refresh sources.",
  "workspace.module.editor.create.template": "Template",
  "workspace.module.editor.create.objectId": "Object ID",
  "workspace.module.editor.create.showAdvanced": "Show defaulted fields",
  "workspace.module.editor.create.hideAdvanced": "Hide defaulted fields",
  "workspace.module.editor.create.unavailable":
    "Creation is unavailable for {title} because this family has no authoring-ready template.",
  "workspace.module.editor.create.choicePlaceholder": "Choose {field}",
  "workspace.module.editor.create.assetPlaceholder": "Asset path or identifier",
  "workspace.module.editor.create.validation.required": "{field} is required.",
  "workspace.module.editor.create.validation.number":
    "Enter a valid number for {field}.",
  "workspace.module.editor.create.validation.choice":
    "Choose a listed value for {field}.",
  "workspace.module.editor.create.validation.boolean":
    "Choose whether {field} is enabled.",
  "workspace.module.editor.batch.open": "Batch create",
  "workspace.module.editor.single.guidance":
    "Preview the exact module files before creating them.",
  "workspace.module.editor.single.rows": "Module draft",
  "workspace.module.editor.single.objectId": "Object ID",
  "workspace.module.editor.single.template": "Template",
  "workspace.module.editor.single.field": "{field}",
  "workspace.module.editor.single.validation.fix":
    "Fix the highlighted fields before previewing.",
  "workspace.module.editor.single.preview": "Preview module",
  "workspace.module.editor.single.previewAgain": "Preview again",
  "workspace.module.editor.single.previewing": "Previewing…",
  "workspace.module.editor.single.apply": "Create module",
  "workspace.module.editor.single.applying": "Creating module…",
  "workspace.module.editor.single.resultBlocked": "Module creation is blocked",
  "workspace.module.editor.single.resultBlockedDetail":
    "No files were written. Resolve the diagnostics, then preview again.",
  "workspace.module.editor.single.resultAppliedDetail":
    "The new module files were installed as one guarded transaction.",
  "workspace.module.editor.batch.requiresDesktop":
    "Batch creation requires the ParaDev desktop application.",
  "workspace.module.editor.batch.eyebrow": "Transactional authoring",
  "workspace.module.editor.batch.title": "Create {title} batch",
  "workspace.module.editor.batch.detail":
    "Add the modules, preview every target, then apply that exact plan as one transaction.",
  "workspace.module.editor.batch.moduleCount": "{count} modules",
  "workspace.module.editor.batch.moduleCountLimit":
    "Up to {count} per transaction",
  "workspace.module.editor.batch.sourceRoot": "Source root",
  "workspace.module.editor.batch.showAdvanced": "Show defaulted fields",
  "workspace.module.editor.batch.hideAdvanced": "Hide defaulted fields",
  "workspace.module.editor.batch.add": "Add module",
  "workspace.module.editor.batch.rows": "Batch module drafts",
  "workspace.module.editor.batch.row": "Module {index}",
  "workspace.module.editor.batch.removeRow": "Remove module {index}",
  "workspace.module.editor.batch.objectId": "Object ID for module {index}",
  "workspace.module.editor.batch.template": "Template for module {index}",
  "workspace.module.editor.batch.field": "{field} for module {index}",
  "workspace.module.editor.batch.defaultValue": "Default: {value}",
  "workspace.module.editor.batch.templateDefault": "Use template default",
  "workspace.module.editor.batch.boolean.true": "Enabled",
  "workspace.module.editor.batch.boolean.false": "Disabled",
  "workspace.module.editor.batch.validation.duplicate":
    "Object ID {objectId} appears more than once for this family.",
  "workspace.module.editor.batch.validation.fix":
    "Fix the highlighted module rows before previewing.",
  "workspace.module.editor.batch.preview": "Preview batch",
  "workspace.module.editor.batch.previewAgain": "Preview again",
  "workspace.module.editor.batch.previewing": "Previewing…",
  "workspace.module.editor.batch.apply": "Create {count} modules",
  "workspace.module.editor.batch.applying": "Creating modules…",
  "workspace.module.editor.batch.done": "Done",
  "workspace.module.editor.batch.refreshFailed":
    "The transaction finished, but the project view could not refresh: {message}",
  "workspace.module.editor.batch.resultReady": "Exact plan ready",
  "workspace.module.editor.batch.resultReadyDetail":
    "Review every target below. Apply will send this frozen request with the displayed plan hash.",
  "workspace.module.editor.batch.resultBlocked": "Batch is blocked",
  "workspace.module.editor.batch.resultBlockedDetail":
    "No planned module was written. Resolve the diagnostics, then preview again.",
  "workspace.module.editor.batch.resultApplied": "Transaction finished",
  "workspace.module.editor.batch.resultAppliedDetail":
    "All new module files were installed as one guarded transaction.",
  "workspace.module.editor.batch.resultUnchangedDetail":
    "Every requested module already matched the plan, so no files changed.",
  "workspace.module.editor.batch.status.create": "Will create",
  "workspace.module.editor.batch.status.created": "Created",
  "workspace.module.editor.batch.status.unchanged": "Unchanged",
  "workspace.module.editor.batch.status.blocked": "Blocked",
  "workspace.module.editor.batch.planHash": "Exact plan hash",
  "workspace.module.editor.batch.reviewRows": "Reviewed module targets",
  "workspace.module.editor.batch.fileCount": "{count} files",
  "workspace.module.editor.batch.diagnostics": "Action required",
  "workspace.module.editor.batch.recoveryTitle": "Recovery data was retained",
  "workspace.module.editor.batch.recoveryDetail":
    "Do not delete or retry over these files. Inspect the retained transaction before deciding how to recover.",
  "workspace.module.editor.batch.openRecovery": "Open recovery folder",
  "workspace.module.editor.batch.dismissRecovery": "Dismiss recovery notice",
  "workspace.module.editor.sourceUpdate.eyebrow": "AI Guided edit",
  "workspace.module.editor.sourceUpdate.title": "Review selected source changes",
  "workspace.module.editor.sourceUpdate.detail":
    "The SDK validated {changed} changed files from {requested} requested files. Review every value before applying the exact revision-guarded transaction.",
  "workspace.module.editor.sourceUpdate.close": "Close source-edit review",
  "workspace.module.editor.sourceUpdate.confirm":
    "I reviewed the {count} changed source files and want to apply this exact plan.",
  "workspace.module.editor.sourceUpdate.unchanged":
    "The selected sources already contain the requested values. Nothing needs to be applied.",
  "workspace.module.editor.sourceUpdate.fileUnchanged": "No value changes in this file.",
  "workspace.module.editor.sourceUpdate.cancel": "Cancel",
  "workspace.module.editor.sourceUpdate.apply": "Apply source changes",
  "workspace.module.editor.sourceUpdate.applying": "Applying source changes…",
  "workspace.module.editor.sourceUpdate.refreshFailed":
    "The source changes were saved, but the project view could not refresh: {message}",
  "workspace.module.editor.sourceUpdate.boolean.true": "Enabled",
  "workspace.module.editor.sourceUpdate.boolean.false": "Disabled",
  "workspace.module.editor.duplicate.open": "Duplicate",
  "workspace.module.editor.duplicate.openTitle":
    "Copy this clean module folder after reviewing an exact file plan.",
  "workspace.module.editor.duplicate.unavailable":
    "Duplication is unavailable while the project index is preparing, stale, ambiguous, or disconnected.",
  "workspace.module.editor.duplicate.dirty":
    "Apply or discard this draft before duplicating the module.",
  "workspace.module.editor.duplicate.eyebrow": "Independent module copy",
  "workspace.module.editor.duplicate.title": "Duplicate {title}",
  "workspace.module.editor.duplicate.detail":
    "Choose a new object ID. ParaDev previews the exact paths and identifiers it will update before writing.",
  "workspace.module.editor.duplicate.objectId": "New object ID",
  "workspace.module.editor.duplicate.objectIdRequired":
    "Enter an object ID for the duplicate.",
  "workspace.module.editor.duplicate.objectIdUnchanged":
    "The duplicate needs a different object ID.",
  "workspace.module.editor.duplicate.source": "Source module",
  "workspace.module.editor.duplicate.destinationRoot":
    "Destination source root",
  "workspace.module.editor.duplicate.sameSourceRoot": "Same source root",
  "workspace.module.editor.duplicate.previewFirst":
    "Preview the copy before any folder is created.",
  "workspace.module.editor.duplicate.preview": "Review copy",
  "workspace.module.editor.duplicate.previewAgain": "Review again",
  "workspace.module.editor.duplicate.previewing": "Reviewing…",
  "workspace.module.editor.duplicate.apply": "Create duplicate",
  "workspace.module.editor.duplicate.applying": "Creating duplicate…",
  "workspace.module.editor.duplicate.ready": "Independent copy plan ready",
  "workspace.module.editor.duplicate.readyDetail":
    "No files have been written. Review the projected inventory before creating the module.",
  "workspace.module.editor.duplicate.blocked": "Copy is blocked",
  "workspace.module.editor.duplicate.blockedDetail":
    "No files were written. Resolve the diagnostics, change the target, then review again.",
  "workspace.module.editor.duplicate.completed": "Duplicate created",
  "workspace.module.editor.duplicate.completedDetail":
    "The folder was created. Review the diagnostic note before closing.",
  "workspace.module.editor.duplicate.done": "Done",
  "workspace.module.editor.duplicate.directoryCount": "{count} folders",
  "workspace.module.editor.duplicate.fileCount": "{count} files",
  "workspace.module.editor.duplicate.byteCount": "{count} output",
  "workspace.module.editor.duplicate.identityRewrite":
    "ParaDev will update {files} text file(s) and {paths} owned path(s) to the new object ID. Binary assets remain unchanged.",
  "workspace.module.editor.duplicate.literalWarning":
    "This is a byte-for-byte folder copy. ParaDev does not rewrite PDX IDs, localization keys, scripted references, or content. Edit the duplicate after creation when it must become an independent game object.",
  "workspace.module.editor.duplicate.exclusions":
    "{count} system item(s) excluded",
  "workspace.module.editor.duplicate.systemMetadata": "ParaDev system metadata",
  "workspace.module.editor.duplicate.planHash": "Exact plan hash",
  "workspace.module.editor.duplicate.refreshFailed":
    "The duplicate was created, but the project view could not refresh: {message}. Refresh sources before trying anything else.",
  "workspace.module.editor.aiHandoff.title": "Opened from AI: {operation}",
  "workspace.module.editor.aiHandoff.moduleDraft.detail":
    "No files are written until you apply the draft through the SDK bridge.",
  "workspace.module.editor.aiHandoff.role": "Task: {role}",
  "workspace.module.editor.aiHandoff.context": "Context: {sources}",
  "workspace.module.editor.cancel": "Cancel",
  "workspace.module.editor.remove": "Remove",
  "workspace.module.editor.removeCurrent": "Remove current object",
  "workspace.module.editor.removeSelection": "Remove selection",
  "workspace.module.editor.removeCount": "Remove {count}",
  "workspace.module.editor.removeConfirm":
    "Mark {count} selected item(s) for removal. Apply writes the removal through the SDK bridge.",
  "workspace.module.editor.removeCurrentConfirm":
    "Mark {title} for removal. No folder is deleted until you click Apply.",
  "workspace.module.editor.removeSelectionConfirm":
    "Mark {count} selected item(s) for removal. No folder is deleted until you click Apply on each draft.",
  "workspace.module.editor.removePermanentWarning":
    "Applying a saved removal permanently deletes the entire module folder, including files that are not shown or indexed here. This cannot be undone.",
  "workspace.module.editor.removeTargetDetail":
    "{root} · {count} indexed file(s)",
  "workspace.module.editor.removeMoreTargets": "+{count} more",
  "workspace.module.editor.hiddenSelectionNote":
    "{count} selected item(s) are hidden by the current filter.",
  "workspace.module.editor.removeConfirmAction": "Mark remove",
  "workspace.module.editor.noSelection": "Select an entity",
  "workspace.module.editor.draft.clean": "Clean",
  "workspace.module.editor.draft.modified": "Draft edited",
  "workspace.module.editor.draft.new": "Draft new",
  "workspace.module.editor.draft.remove": "Draft remove",
  "workspace.module.editor.sourceMissingStatus": "Draft source missing",
  "workspace.module.editor.sourceMissing":
    "This module is missing from the refreshed project. Its local draft is preserved, but ParaDev will not write stale paths. Restore to discard the draft, or restore the module on disk and refresh before applying.",
  "workspace.module.editor.sourceChangedStatus": "Draft source changed",
  "workspace.module.editor.sourceChanged":
    "Project sources changed after this module draft began. The draft is preserved, but ParaDev will not overwrite newer file revisions. Restore to discard the draft and load the current sources.",
  "workspace.module.editor.saveDraft": "Apply",
  "workspace.module.editor.applying": "Applying",
  "workspace.module.editor.applyTitle":
    "Write this draft through the SDK bridge.",
  "workspace.module.editor.buildModule": "Build module",
  "workspace.module.editor.buildModuleTitle":
    "Open Build and rebuild only {module}.",
  "workspace.module.editor.buildModuleDirty":
    "Apply or discard this draft before rebuilding {module}.",
  "workspace.module.editor.buildCollection": "Build collection",
  "workspace.module.editor.buildCollectionTitle":
    "Open Build and rebuild only collection {collection}.",
  "workspace.module.editor.buildCollectionDirty":
    "Apply or discard this draft before rebuilding collection {collection}.",
  "workspace.module.editor.activity.inactive": "Inactive · omitted from builds",
  "workspace.module.editor.activity.activate": "Activate",
  "workspace.module.editor.activity.activateTitle":
    "Include this module in full, cached, family, and module builds.",
  "workspace.module.editor.activity.deactivate": "Deactivate",
  "workspace.module.editor.activity.deactivateTitle":
    "Keep this module editable but omit it from every build mode.",
  "workspace.module.editor.activity.buildInactive":
    "Activate {module} before building it directly.",
  "workspace.module.editor.activity.filter": "Module activity",
  "workspace.module.editor.activity.filterAll": "All",
  "workspace.module.editor.activity.filterActive": "Active",
  "workspace.module.editor.activity.filterInactive": "Inactive",
  "workspace.module.editor.buildAffected": "Build affected {family} output",
  "workspace.module.editor.buildAffectedTitle":
    "Open Build and rebuild the entire {family} family, including aggregate output.",
  "workspace.module.editor.buildAffectedDirty":
    "Apply or discard this draft before building the affected {family} output.",
  "workspace.module.editor.applyDidNotWrite":
    "The apply command completed without writing files.",
  "workspace.module.editor.sourceRecoveryRequired":
    "ParaDev preserved recovery data because project files changed during Apply. Do not apply another edit yet; open the recovery folder above and review the preserved files.",
  "workspace.module.editor.draftPlanBlocked": "Draft plan is blocked.",
  "workspace.module.editor.applyFailed": "Apply failed: {message}",
  "workspace.module.editor.applyRequiresDesktop":
    "Apply requires the ParaDev desktop application.",
  "workspace.module.editor.applyUnsupported":
    "Only new scaffold drafts, source text edits, title edits, image replacements, binary asset drafts, and canonical removals can be applied from this panel.",
  "workspace.module.editor.saveDisabled":
    "Finish a valid scaffold, title, text, image, asset, rename, or removal draft before applying.",
  "workspace.module.editor.restore": "Discard",
  "workspace.module.editor.openFolder": "Open",
  "workspace.module.editor.refreshEntity": "Refresh entity",
  "workspace.module.editor.refreshModule": "Refresh sources",
  "workspace.module.editor.path": "Path",
  "workspace.module.editor.sources": "Sources",
  "workspace.module.editor.sourceFile": "Source file",
  "workspace.module.editor.layout": "Layout",
  "workspace.module.editor.info": "Info",
  "workspace.module.editor.activeDiagramNode": "Node {id}",
  "workspace.module.editor.objectId": "ID",
  "workspace.module.editor.title": "Title",
  "workspace.module.editor.name": "Name",
  "workspace.module.editor.collection": "Collection",
  "workspace.module.editor.collectionNone": "No collection",
  "workspace.module.editor.metadataTitleCreateHint":
    "No metadata file is needed yet. ParaDev keeps the module metadata-free unless you change its name.",
  "workspace.module.editor.metadataTitleCreatePending":
    "Apply will create meta.yaml with only the title. The folder will continue to define the module family and ID.",
  "workspace.module.editor.slot.def": "Definition",
  "workspace.module.editor.slot.loc": "Localization",
  "workspace.module.editor.slot.focusInfo": "{id} info",
  "workspace.module.editor.slot.localizationLanguage":
    "{language} localization",
  "workspace.module.editor.translations": "Translations",
  "workspace.module.editor.translationKey": "Key",
  "workspace.module.editor.translationAliasHint":
    "Use @ as the current entity ID: {object}",
  "workspace.module.editor.addTranslationRow": "Add translation row",
  "workspace.module.editor.removeTranslationRow":
    "Remove translation row {key}",
  "workspace.module.editor.noTranslations":
    "No localization text loaded for this entity.",
  "workspace.module.editor.language.english": "English",
  "workspace.module.editor.language.french": "French",
  "workspace.module.editor.language.german": "German",
  "workspace.module.editor.language.russian": "Russian",
  "workspace.module.editor.language.simpChinese": "Simplified Chinese",
  "workspace.module.editor.language.spanish": "Spanish",
  "workspace.module.editor.sourceTabs": "Source editor tabs",
  "workspace.module.editor.image": "Image",
  "workspace.module.editor.assets": "Assets",
  "workspace.module.editor.assetHeading": "Model and binary assets",
  "workspace.module.editor.assetHelp":
    "Drop a resource here. ParaDev uses this module type's Registry slots to choose and validate its target; matching existing filenames are replacements.",
  "workspace.module.editor.assetPick": "Drop files here or choose resources",
  "workspace.module.editor.assetDropActive": "Drop resources",
  "workspace.module.editor.assetDropRejected":
    "Choose no more than {count} files at once.",
  "workspace.module.editor.assetTooMany":
    "Keep no more than {count} asset files pending at once.",
  "workspace.module.editor.assetTooLarge":
    "{name} is larger than the {size} per-file limit.",
  "workspace.module.editor.assetEmpty":
    "{name} is empty. Choose an exported binary file with content.",
  "workspace.module.editor.assetBatchTooLarge":
    "Keep pending assets under {size}; apply them before staging more.",
  "workspace.module.editor.assetDuplicateTarget":
    "Two selected files target {path}. Choose one file for each target so ParaDev cannot silently discard a binary.",
  "workspace.module.editor.assetReadFailed": "ParaDev could not read {name}.",
  "workspace.module.editor.assetEncodeFailed":
    "ParaDev could not prepare {name} for a safe binary write.",
  "workspace.module.editor.assetExisting": "Current assets",
  "workspace.module.editor.assetExistingCount": "{count} file(s)",
  "workspace.module.editor.assetNone":
    "No non-image binary resources are attached yet. New files are accepted only when this module type declares a safe Registry destination.",
  "workspace.module.editor.assetReplace": "Replace",
  "workspace.module.editor.assetPending": "Pending asset changes",
  "workspace.module.editor.assetPendingCount": "{count} pending",
  "workspace.module.editor.assetDestination": "Destination folder",
  "workspace.module.editor.assetDestinationChoose":
    "Choose a Registry destination",
  "workspace.module.editor.assetTargetPath": "Target path",
  "workspace.module.editor.assetTargetPathHelp":
    "No existing destination fits this file yet. Enter a project-relative path inside this module; ParaDev will validate it against the Registry before Apply.",
  "workspace.module.editor.assetDiscard": "Discard {name}",
  "workspace.module.editor.assetPathEmpty":
    "Choose a destination folder or enter a target path.",
  "workspace.module.editor.assetPathSlot":
    "{name} does not match a Registry copy-resource slot for this module. Choose an offered destination or correct the path.",
  "workspace.module.editor.assetPathFormat":
    "The uploaded file extension must match its target extension. Use the Image tab for PNG-to-DDS or PNG-to-TGA conversion.",
  "workspace.module.editor.assetPathSource":
    "{path} already belongs to an existing asset. Use its Replace button so ParaDev cannot overwrite the wrong same-named file.",
  "workspace.module.editor.assetPathUnknown": "This target",
  "workspace.module.editor.assetPathOutside":
    "Choose an explicit target inside this module folder. ParaDev will not write a resource outside its Registry-owned module.",
  "workspace.module.editor.assetResolveErrors":
    "Resolve the highlighted asset paths before applying this entity.",
  "workspace.module.editor.scaffoldFirstTitle":
    "Create the starter files first",
  "workspace.module.editor.scaffoldFirstBody":
    "Click Apply to create this entity's starter module. ParaDev will then unlock the generated PDX files and the Assets tab for safe editing.",
  "workspace.module.editor.imageJump": "Open image replacement",
  "workspace.module.editor.imageSavePath": "Save path",
  "workspace.module.editor.noImage": "No image selected",
  "workspace.module.editor.imageDraftOnly": "Draft image replacement",
  "workspace.module.editor.dropImage": "Drop image",
  "workspace.module.editor.pickImage": "Pick PNG/JPEG/WebP/BMP",
  "workspace.module.editor.imageUrlPlaceholder":
    "https://example.com/image.png",
  "workspace.module.editor.loadImageUrl": "Load URL",
  "workspace.module.editor.saveImage": "Save",
  "workspace.module.editor.savePngDraft": "Save PNG draft",
  "workspace.module.editor.imageDraftReady": "PNG draft ready",
  "workspace.module.editor.imageEditorError": "Image editor error: {message}",
  "workspace.module.editor.imageConversionPlanned":
    "This {format} source stays at its existing path. ParaDev converts the editor's PNG output to {format} when you apply the draft.",
  "workspace.module.editor.imageCreationPlanned":
    "This family declares the image path below. Apply will create it only if the target is still absent.",
  "workspace.module.editor.imageReplacementInputRequired":
    "{format} previews are not supported by the image editor. Drop or load a PNG/JPEG/WebP/BMP replacement to start editing; ParaDev will convert it back to {format} when you apply the draft.",
  "workspace.module.editor.imageFormatUnsupported":
    "ParaDev cannot replace this {format} image format yet.",
  "workspace.module.editor.imageTargetUnavailable":
    "Image creation is unavailable because the project SDK did not provide an exact family-owned target for this module. Add or restore its configured image source, then refresh; ParaDev will not guess a filename.",
  "workspace.module.editor.imagePngPathRequired":
    "Processed image drafts contain PNG data. Choose a .png path unless you are replacing a supported existing non-PNG source at its exact path; this {format} target is not valid.",
  "workspace.module.editor.imageDeclaredPathRequired":
    "Create the family-declared image at {path}. ParaDev keeps this target pinned to the source contract.",
  "workspace.module.editor.imageSelectedPathRequired":
    "Replace the selected source at {path}. Custom save paths are only available when the entity has no existing image source.",
  "workspace.module.editor.zoom": "Zoom",
  "workspace.module.editor.unsavedPath": "Draft object has no folder yet",
  "workspace.module.editor.loadingEditor": "Loading editor",
  "workspace.module.editor.advancedMetadata": "Advanced metadata",
  "workspace.module.editor.advancedMetadataTitle":
    "Open {file}. ParaDev already infers the module family and ID from its folder; edit this file only for explicit overrides.",
  "workspace.module.editor.guided": "Guided",
  "workspace.module.editor.code": "Code",
  "workspace.module.editor.guidedLoading": "Preparing guided editor…",
  "workspace.module.editor.guidedError": "Cannot open Guided mode: {message}",
  "workspace.module.editor.guidedStale":
    "The source changed while Guided mode was loading. Choose Guided again to use the latest draft.",
  "workspace.module.editor.guidedPlanMismatch":
    "Guided mode could not verify this draft against the project extension. Reopen Guided mode and review the fields before applying.",
  "workspace.module.editor.guidedFormPartialCoverage":
    "Showing {shown} of {total} guided fields. Search by event ID, field, or value to reach later sections.",
  "workspace.module.editor.guidedFormSearchLabel": "Find guided fields",
  "workspace.module.editor.guidedFormSearchPlaceholder":
    "Event ID, field name, or current value",
  "workspace.module.editor.guidedFormSearchAction": "Search",
  "workspace.module.editor.guidedFormSearchClear": "Show first fields",
  "workspace.module.editor.guidedFormSearchNoResults":
    "No safe guided fields match this search. Try an event ID, field name, or current value.",
  "workspace.module.editor.guidedFormSearchPartialCoverage":
    "Showing {shown} of {total} matching guided fields. Narrow the search to reach a specific section.",
  "workspace.module.editor.guidedFormInvalidJson":
    "The source is not valid JSON.",
  "workspace.module.editor.guidedFormDuplicateProperty":
    "The source contains duplicate JSON properties, so Guided mode cannot edit it safely.",
  "workspace.module.editor.guidedFormInvalidNumber":
    "Enter a finite JSON number.",
  "workspace.module.editor.guidedFormInvalidPdxNumber":
    "Enter a finite decimal PDX number.",
  "workspace.module.editor.guidedFormInvalidPdxIdentifier":
    "Enter one plain PDX value without spaces, comments, braces, or operators.",
  "workspace.module.editor.guidedFormInvalidPdxString":
    "This PDX string is no longer safely quoted.",
  "workspace.module.editor.guidedFormInvalidPdxSpan":
    "This guided field has an invalid PDX source location. Reopen Guided mode.",
  "workspace.module.editor.guidedFormStalePdxSpan":
    "The PDX source changed after this form was prepared. Reopen Guided mode.",
  "workspace.module.editor.guidedFormInvalidLocSpan":
    "This translated field has an invalid source location. Reopen Guided mode.",
  "workspace.module.editor.guidedFormStaleLocSpan":
    "The localization source changed after this form was prepared. Reopen Guided mode.",
  "workspace.module.editor.guidedFormInvalidLocText":
    "Keep leading and trailing lines clean, and do not introduce another localization section.",
  "workspace.module.editor.guidedFormMissingPath":
    "This field no longer exists in the current JSON.",
  "workspace.module.editor.guidedFormContainerTarget":
    "This field points to an object or list instead of one editable value.",
  "workspace.module.editor.guidedFormTypeMismatch":
    "This field's source value has the wrong type.",
  "workspace.module.editor.guidedFormMissingPatch":
    "This editable field is missing its exact source location.",
  "workspace.module.editor.guidedFormReadonlyPatch":
    "This read-only field incorrectly declares an editable JSON location.",
  "workspace.module.editor.guidedFormExpectedKind":
    "This field expects {expected}, but the current source value is {actual}.",
  "workspace.module.editor.guidedFormChoiceEmpty":
    "This field has no available choices.",
  "workspace.module.editor.guidedFormChoiceType":
    "This field's choices do not match the current JSON value type.",
  "workspace.module.editor.guidedNumberMin":
    "The value must be at least {min}.",
  "workspace.module.editor.guidedNumberMax": "The value must be at most {max}.",
  "workspace.module.editor.restNote":
    "New scaffold drafts, source text edits, image replacements, and canonical removals apply through the SDK bridge. Image crop metadata remains draft-only.",
  "workspace.module.editor.openFailed": "Open failed: {message}",
  "inspector.label": "Inspector",
  "status.ready": "ready",
  "status.scaffold": "scaffold",
  "status.planned": "planned",
  "status.offline": "offline",
  "statusbar.sdkReady": "SDK {count} ready",
  "statusbar.scaffoldedSurfaces": "{count} scaffolded surfaces",
  "statusbar.restOffline": "REST offline",
  "statusbar.mcpPlanned": "MCP planned",
  "statusbar.macosPriority": "macOS priority",
  "tabs.modules.countries.subtitle": "Tags, history, politics",
  "tabs.modules.characters.subtitle": "Leaders, portraits, advisors",
  "tabs.modules.decisions.subtitle": "Categories, missions, events",
  "tabs.modules.divisions.subtitle": "Templates, OOB links, units",
  "tabs.modules.focuses.subtitle": "Trees, rewards, prerequisites",
  "tabs.modules.ideas.subtitle": "National spirits and advisors",
  "tabs.modules.modifiers.subtitle": "Scopes, icons, localization",
  "tabs.modules.map.subtitle": "States, provinces, regions",
  "tabs.modules.states.subtitle": "History, buildings, resources",
  "tabs.modules.events.subtitle": "Options, triggers, chains",
  "tabs.modules.technologies.subtitle": "Unlocks, doctrines, research",
  "tabs.modules.equipment.subtitle": "Archetypes, variants, modules",
  "tabs.modules.buildings.subtitle": "Definitions, slots, effects",
  "tabs.modules.scriptedEffects.subtitle": "Reusable effects and arguments",
  "tabs.modules.scriptedTriggers.subtitle": "Reusable trigger logic",
  "tabs.modules.localization.subtitle": "Keys, termbase, YML output",
  "tabs.modules.assets.subtitle": "DDS/TGA recipes and previews",
  "tabs.modules.music.subtitle": "Stations, tracks, metadata",
  "modules.countries.title": "Countries",
  "modules.countries.description":
    "Country tags, history files, politics, and diplomacy.",
  "modules.characters.title": "Characters",
  "modules.characters.description":
    "Leaders, commanders, advisors, portraits, and traits.",
  "modules.portraits.title": "Shared Portraits",
  "modules.portraits.description":
    "Reusable random, operative, and fallback portrait bundles.",
  "modules.continuousFocuses.title": "Continuous Focuses",
  "modules.decisions.title": "Decisions",
  "modules.decisions.description":
    "Decision categories, missions, scripted costs, and visibility.",
  "modules.divisions.title": "Divisions",
  "modules.divisions.description":
    "Templates, OOB links, units, equipment, and deployment.",
  "modules.entity.title": "Entity",
  "modules.focuses.title": "National Focuses",
  "modules.focuses.description":
    "Focus trees, prerequisites, rewards, filters, and AI weights.",
  "modules.ideas.title": "Ideas",
  "modules.ideas.description":
    "National spirits, advisors, designers, and dynamic modifiers.",
  "modules.modifiers.title": "Modifiers",
  "modules.modifiers.description":
    "Static and dynamic modifiers, scopes, icons, and localization.",
  "modules.map.title": "Map",
  "modules.map.description":
    "States, provinces, strategic regions, supply, and adjacency.",
  "modules.states.title": "States",
  "modules.states.description":
    "State history, buildings, resources, cores, and ownership.",
  "modules.events.title": "Events",
  "modules.events.description":
    "Event files, option effects, triggers, chains, and pictures.",
  "modules.technologies.title": "Technologies",
  "modules.technologies.description":
    "Tech folders, unlocks, doctrines, and research categories.",
  "modules.equipment.title": "Equipment",
  "modules.equipment.description":
    "Equipment archetypes, variants, modules, and production stats.",
  "modules.militaryIndustrialOrganizations.title":
    "Military Industrial Organizations",
  "modules.militaryIndustrialOrganizations.description":
    "Organization trait trees, positions, prerequisites, and exclusions.",
  "modules.equipmentModules.title": "Equipment Modules",
  "modules.equipmentModuleCategories.title": "Equipment Module Categories",
  "modules.buildings.title": "Buildings",
  "modules.buildings.description":
    "Building definitions, slots, state effects, and modifiers.",
  "modules.scriptedEffects.title": "Scripted Effects",
  "modules.scriptedEffects.description":
    "Reusable effects, scope safety, arguments, and diagnostics.",
  "modules.scriptedTriggers.title": "Scripted Triggers",
  "modules.scriptedTriggers.description":
    "Reusable trigger logic, validation, and explainable previews.",
  "modules.localization.title": "Localization",
  "modules.localization.description":
    "Keys, termbase, translation review, and YML output.",
  "modules.assets.title": "Assets",
  "modules.assets.description":
    "DDS/TGA recipes, derivatives, cache, and previews.",
  "modules.music.title": "Music",
  "modules.music.description":
    "Music stations, tracks, metadata, and DLC-aware packaging.",
  "modules.achievements.title": "Achievements",
  "modules.autonomousStates.title": "Autonomous States",
  "modules.balanceOfPower.title": "Balance of Power",
  "modules.bookmarks.title": "Bookmarks",
  "modules.difficultySettings.title": "Difficulty Settings",
  "modules.doctrines.title": "Doctrines",
  "modules.factions.title": "Factions",
  "modules.gameRules.title": "Game Rules",
  "modules.ideaCategories.title": "Idea Categories",
  "modules.ideologies.title": "Ideologies",
  "modules.intelligenceAgencies.title": "Intelligence Agencies",
  "modules.inventoryItems.title": "Inventory Items",
  "modules.onActions.title": "On Actions",
  "modules.operations.title": "Operations",
  "modules.operationPhases.title": "Operation Phases",
  "modules.operationTokens.title": "Operation Tokens",
  "modules.operativeCodenames.title": "Operative Codenames",
  "modules.opinionModifiers.title": "Opinion Modifiers",
  "modules.resistanceActivities.title": "Resistance Activities",
  "modules.resources.title": "Resources",
  "modules.scriptedGuis.title": "Scripted GUIs",
  "modules.specialProjects.title": "Special Projects",
  "modules.specialProjectRewards.title": "Special Project Rewards",
  "modules.stateLore.title": "State Lore",
  "modules.strategicRegions.title": "Strategic Regions",
  "modules.superevents.title": "Super Events",
  "modules.traits.title": "Traits",
  "modules.unitMedals.title": "Unit Medals",
  "modules.wargoals.title": "Wargoals",
  "surface.sdk.title": "Python SDK",
  "surface.mcp.title": "MCP Toolkit",
  "surface.cli.title": "Typer + Rich CLI",
  "surface.rest.title": "REST API",
  "surface.openapi.title": "OpenAPI Contract",
  "surface.bundle.title": "Python Wheel + WebView App",
  "surface.frontend.title": "TypeScript Frontend",
  "surface.desktop.title": "System WebView Desktop",
  "surface.lsp.title": "PDX LSP",
  "surface.vscode.title": "VS Code Extension",
} as const;

export type TranslationKey = keyof typeof en;
