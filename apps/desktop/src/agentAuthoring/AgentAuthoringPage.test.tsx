import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";
import { createTranslator } from "../i18n";
import type {
  ProjectBrowserPayload,
  ProjectOption,
  ProjectTemplatesPayload
} from "../types";
import {
  AgentAuthoringPage,
  agentAuthoringMetrics,
  agentPrompt
} from "./AgentAuthoringPage";

const project: ProjectOption = {
  id: "/workspace/PIHC3",
  projectId: "PIHC3",
  name: "The Pony In The High Castle",
  path: "/workspace/PIHC3",
  game: "hoi4"
};

const browser: ProjectBrowserPayload = {
  schema: "paradev.sdk.project-browser.v1",
  project_id: "PIHC3",
  title: project.name,
  root: project.path,
  profile: "hoi4",
  filters: {},
  families: [
    {
      id: "ideas",
      family: "idea",
      title: "Ideas",
      item_count: 5,
      source_count: 15,
      layouts: ["canonical"]
    },
    {
      id: "focuses",
      family: "focus",
      title: "Focuses",
      item_count: 10,
      source_count: 30,
      layouts: ["canonical"],
      diagram: {
        id: "focus-tree",
        aliases: [],
        renderer: "focus-tree",
        title: "Focus tree",
        editable: true
      }
    },
    {
      id: "internal",
      family: "internal",
      title: "Internal",
      item_count: 0,
      source_count: 0,
      layouts: ["family_root"],
      visible: false,
      diagram: {
        id: "internal-tree",
        aliases: [],
        renderer: "generic",
        title: "Internal tree",
        editable: false
      }
    }
  ],
  items: [],
  diagnostics: []
};

const templates: ProjectTemplatesPayload = {
  schema: "paradev.sdk.templates.v1",
  project_id: "PIHC3",
  profile: "hoi4",
  templates: [
    {
      id: "hoi4:idea/basic",
      title: "Idea",
      family: "idea",
      source: "builtin",
      authoring_ready: true,
      args: {},
      files: []
    },
    {
      id: "hoi4:focus/basic",
      title: "Focus",
      family: "focus",
      source: "builtin",
      authoring_ready: true,
      args: {},
      files: []
    },
    {
      id: "project:unknown",
      title: "Unknown",
      family: "unknown",
      source: "project",
      authoring_ready: false,
      args: {},
      files: []
    }
  ]
};

describe("AgentAuthoringPage", () => {
  it("derives project capability counts from Registry-backed browser and template payloads", () => {
    expect(agentAuthoringMetrics(browser, templates)).toEqual({
      familyCount: 2,
      authoringTemplateCount: 2,
      diagramFamilyCount: 1
    });
    expect(agentAuthoringMetrics(null, null)).toEqual({
      familyCount: null,
      authoringTemplateCount: null,
      diagramFamilyCount: null
    });
  });

  it("renders real reviewed authoring, MCP, skill, and project context instead of a placeholder", () => {
    const markup = renderToStaticMarkup(
      <AgentAuthoringPage
        activeProject={project}
        browser={browser}
        onOpenAiChat={() => undefined}
        onOpenEditing={() => undefined}
        templates={templates}
        t={createTranslator("en")}
      />
    );

    expect(markup).toContain("The Pony In The High Castle");
    expect(markup).toContain("2</strong><small>visible content types");
    expect(markup).toContain("2</strong><small>authoring-ready templates");
    expect(markup).toContain("1</strong><small>visual tree editors");
    expect(markup).toContain("paradev mcp serve");
    expect(markup).toContain("$paradev-authoring");
    expect(markup).toContain("dry-plan every change");
    expect(markup).toContain("AI proposals never write project files automatically");
    expect(markup).not.toContain("will appear here");
  });

  it("builds a guarded prompt around path-backed project identity", () => {
    expect(agentPrompt(project)).toBe(
      "Use $paradev-authoring from .agents/skills/paradev-authoring/SKILL.md to author modules and collections for The Pony In The High Castle at /workspace/PIHC3. Discover Registry templates first, dry-plan every change, and wait for my review before applying it."
    );
  });
});
