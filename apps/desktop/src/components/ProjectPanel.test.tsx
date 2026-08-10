import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";
import { createTranslator } from "../i18n";
import type { PanelOption, ProjectOption } from "../types";
import { ProjectPanel, projectSelectOptions } from "./ProjectPanel";

const project: ProjectOption = {
  id: "minimal_hoi4",
  projectId: "minimal_hoi4",
  name: "Minimal HOI4 Project",
  path: "/tmp/minimal"
};

const options: PanelOption[] = [{ id: "countries", titleKey: "modules.countries.title" }];

function renderProjectPanel({
  activeOption = "countries",
  mode = "modules",
  panelOptions = options,
  projectImporting = false,
  projectLoading = false,
  projectNotice = "",
  projectNoticeDetail = "",
  projectOpening = false
}: {
  activeOption?: string;
  mode?: "modules" | "config";
  panelOptions?: PanelOption[];
  projectImporting?: boolean;
  projectLoading?: boolean;
  projectNotice?: string;
  projectNoticeDetail?: string;
  projectOpening?: boolean;
} = {}) {
  const t = createTranslator("en");
  return renderToStaticMarkup(
    <ProjectPanel
      activeOption={activeOption}
      activeProject={project}
      isOpen={true}
      mode={mode}
      onImportProject={() => undefined}
      onOpenProject={() => undefined}
      onPinOption={() => undefined}
      onReorderOptions={() => undefined}
      onSelectOption={() => undefined}
      onSelectProject={() => undefined}
      options={panelOptions}
      projectError=""
      projectImporting={projectImporting}
      projectLoading={projectLoading}
      projectNotice={projectNotice}
      projectNoticeDetail={projectNoticeDetail}
      projectOpenError=""
      projectOpening={projectOpening}
      projectOptions={[project]}
      t={t}
    />
  );
}

describe("ProjectPanel", () => {
  it("keeps package installation available after onboarding without restoring legacy actions", () => {
    const markup = renderProjectPanel();

    expect(markup).toContain('aria-label="Install PIHC3 package"');
    expect(markup).toContain("Open project");
    expect(markup).not.toContain("New project");
    expect(markup).not.toContain("Refresh project");
  });

  it("keeps active project context visible while browsing configuration", () => {
    const markup = renderProjectPanel({ mode: "config" });

    expect(markup).toContain("Active Project");
    expect(markup).toContain("Minimal HOI4 Project");
    expect(markup).toContain("/tmp/minimal");
    expect(markup).toContain("Configuration");
    expect(markup).toContain('aria-label="Active project"');
  });

  it("shows automatic saved-project recovery as a non-blocking live notice", () => {
    const notice =
      "The saved project was unavailable. ParaDev opened PIHC3 instead.";
    const detail =
      "Previous location: /old/PIHC3. Current location: /new/PIHC3.";
    const markup = renderProjectPanel({
      projectNotice: notice,
      projectNoticeDetail: detail
    });

    expect(markup).toContain('class="project-path notice"');
    expect(markup).toContain('aria-live="polite"');
    expect(markup).toContain('role="status"');
    expect(markup).toContain(notice);
    expect(markup).toContain(
      'title="Previous location: /old/PIHC3. Current location: /new/PIHC3."'
    );
    expect(markup).not.toContain('class="project-path error"');
  });

  it("qualifies same-ID checkout labels while preserving distinct path identities", () => {
    const original = { ...project, id: "/workspace/original/PIHC3", projectId: "PIHC3", name: "PIHC3", path: "/workspace/original/PIHC3" };
    const isolated = { ...project, id: "/workspace/isolated/PIHC3", projectId: "PIHC3", name: "PIHC3", path: "/workspace/isolated/PIHC3" };

    expect(projectSelectOptions([original, isolated])).toEqual([
      { label: "PIHC3 — /workspace/original/PIHC3", value: "/workspace/original/PIHC3" },
      { label: "PIHC3 — /workspace/isolated/PIHC3", value: "/workspace/isolated/PIHC3" }
    ]);
  });

  it("shows opening status and disables the open action during shell handoff", () => {
    const markup = renderProjectPanel({ projectOpening: true });

    expect(markup).toContain("Opening Minimal HOI4 Project");
    expect(markup).toContain('aria-label="Open project"');
    expect(markup).toContain("disabled");
  });

  it("marks the project picker busy and locks project actions during SDK refresh", () => {
    const markup = renderProjectPanel({ projectLoading: true });

    expect(markup).toContain('aria-busy="true"');
    expect(markup).toContain("Loading registry for Minimal HOI4 Project");
    expect(markup).toContain('aria-label="Active project" disabled=""');
    expect(markup).toMatch(/<button[^>]*aria-label="Install PIHC3 package"[^>]*disabled=""/);
    expect(markup).toMatch(/<button[^>]*aria-label="Open project"[^>]*disabled=""/);
  });

  it("keeps project opening, selection, and package installation mutually exclusive", () => {
    const markup = renderProjectPanel({ projectImporting: true });

    expect(markup).toContain('aria-busy="true"');
    expect(markup).toContain("Installing PIHC3 package");
    expect(markup).toContain('aria-label="Active project" disabled=""');
    expect(markup).toMatch(/<button[^>]*aria-label="Install PIHC3 package"[^>]*disabled=""/);
    expect(markup).toMatch(/<button[^>]*aria-label="Open project"[^>]*disabled=""/);
  });

  it("shows a live project progress indicator while the SDK refresh runs", () => {
    const markup = renderProjectPanel({ projectLoading: true });

    expect(markup).toContain('class="project-picker-progress"');
    expect(markup).toContain('role="status"');
    expect(markup).toContain('aria-live="polite"');
    expect(markup).toContain('class="project-picker-progress-orbit"');
    expect(markup).toContain("Loading registry for Minimal HOI4 Project");
  });

  it("does not split diagram-capable families into a separate low sidebar section", () => {
    const markup = renderProjectPanel();

    expect(markup).toContain("Modules");
    expect(markup).toContain('aria-label="Countries"');
    expect(markup).not.toContain("Diagrams");
    expect(markup).not.toContain('aria-label="Focuses diagram"');
  });

  it("groups module mode in stable authoring order without losing counts or selection", () => {
    const markup = renderProjectPanel({
      panelOptions: [
        { id: "future-extension", label: "Future Extension", count: 2, groupKey: "modules.group.other" },
        { id: "modifiers", titleKey: "modules.modifiers.title", count: 4, groupKey: "modules.group.shared" },
        { id: "events", titleKey: "modules.events.title", count: 6, groupKey: "modules.group.events" },
        { id: "states", titleKey: "modules.states.title", count: 8, groupKey: "modules.group.world" },
        { id: "technologies", titleKey: "modules.technologies.title", count: 10, groupKey: "modules.group.military" },
        { id: "countries", titleKey: "modules.countries.title", count: 12, groupKey: "modules.group.country" }
      ]
    });
    const groupOffsets = [
      "Countries &amp; Politics",
      "Military &amp; Research",
      "World &amp; Map",
      "Events &amp; Extensions",
      "Shared Content",
      "Other &amp; Advanced"
    ].map((title) => markup.indexOf(title));

    expect(groupOffsets.every((offset) => offset >= 0)).toBe(true);
    expect(groupOffsets).toEqual([...groupOffsets].sort((left, right) => left - right));
    expect(markup).toMatch(/aria-label="Countries"[^>]*class="option-row selected"/);
    expect(markup).toMatch(/aria-label="Countries"[\s\S]*?<small>12<\/small>/);
    expect(markup).not.toContain("reorderable");
  });

  it("starts with only the active family group expanded", () => {
    const panelOptions: PanelOption[] = [
      { id: "countries", titleKey: "modules.countries.title", groupKey: "modules.group.country" },
      { id: "future-extension", label: "Future Extension", groupKey: "modules.group.other" }
    ];
    const ordinaryMarkup = renderProjectPanel({ panelOptions });
    const advancedMarkup = renderProjectPanel({
      activeOption: "future-extension",
      panelOptions
    });

    expect(ordinaryMarkup).toMatch(
      /aria-expanded="true"[^>]*class="option-group-title"[^>]*><span>Countries &amp; Politics/
    );
    expect(ordinaryMarkup).toMatch(
      /aria-expanded="false"[^>]*class="option-group-title"[^>]*><span>Other &amp; Advanced/
    );
    expect(ordinaryMarkup).toContain('aria-label="Future Extension"');
    expect(advancedMarkup).toMatch(
      /aria-expanded="false"[^>]*class="option-group-title"[^>]*><span>Countries &amp; Politics/
    );
    expect(advancedMarkup).toMatch(
      /aria-expanded="true"[^>]*class="option-group-title"[^>]*><span>Other &amp; Advanced/
    );
    expect(advancedMarkup).toMatch(
      /aria-label="Future Extension"[^>]*class="option-row selected"/
    );
  });
});
