import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";
import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { createTranslator } from "../i18n";
import type { ProjectBrowserPayload, ProjectOption } from "../types";
import * as pageModule from "./ProjectManagementPage";
import { ProjectManagementPage } from "./ProjectManagementPage";

describe("ProjectManagementPage", () => {
  it("uses SDK descriptor metadata as the project version fallback", () => {
    const project = {
      id: "PIHC3",
      projectId: "PIHC3",
      name: "The Pony In The High Castle",
      path: "/workspace/projects/PIHC3",
      descriptor: {
        mod_version: "v0.2.3",
        supported_version: "1.19.*"
      },
      game: "hoi4"
    } as ProjectOption;

    const markup = renderToStaticMarkup(
      <ProjectManagementPage
        activeProject={project}
        browser={null}
        onActivateProject={() => undefined}
        onOpenBuildPage={() => undefined}
        openTarget="finder"
        projectOptions={[project]}
        t={createTranslator("zh")}
      />
    );

    expect(markup).toContain("0.2.3");
    expect(markup).not.toContain("未设置");
  });

  it("renders project root instead of project id in project details", () => {
    const project = {
      id: "PIHC3",
      projectId: "PIHC3",
      name: "The Pony In The High Castle",
      path: "/workspace/projects/PIHC3",
      game: "hoi4"
    } as ProjectOption;

    const markup = renderToStaticMarkup(
      <ProjectManagementPage
        activeProject={project}
        browser={null}
        onActivateProject={() => undefined}
        onOpenBuildPage={() => undefined}
        openTarget="finder"
        projectOptions={[project]}
        t={createTranslator("zh")}
      />
    );

    expect(markup).toContain("项目根目录");
    expect(markup).toContain("/workspace/projects/PIHC3");
    expect(markup).not.toContain("项目 ID");
    expect(markup).not.toContain("<dd>PIHC3</dd>");
  });

  it("localizes known project game ids for PIHC3 management rows", () => {
    const project = {
      id: "PIHC3",
      projectId: "PIHC3",
      name: "The Pony In The High Castle",
      path: "/workspace/projects/PIHC3",
      game: "hoi4"
    } as ProjectOption;

    const markup = renderToStaticMarkup(
      <ProjectManagementPage
        activeProject={project}
        browser={null}
        onActivateProject={() => undefined}
        onOpenBuildPage={() => undefined}
        openTarget="finder"
        projectOptions={[project]}
        t={createTranslator("zh")}
      />
    );

    expect(markup).toContain("钢铁雄心 IV");
    expect(markup).not.toContain("<strong>hoi4</strong>");
  });

  it("treats same-ID checkouts as separate management rows", () => {
    const original = {
      id: "/workspace/original/PIHC3",
      projectId: "PIHC3",
      name: "PIHC3",
      path: "/workspace/original/PIHC3",
      game: "hoi4"
    } as ProjectOption;
    const isolated = {
      ...original,
      id: "/workspace/isolated/PIHC3",
      path: "/workspace/isolated/PIHC3"
    };
    const browser = {
      schema: "paradev.sdk.project-browser.v1",
      project_id: "PIHC3",
      title: "PIHC3",
      root: isolated.path,
      profile: "hoi4",
      filters: {},
      families: [],
      items: [
        {
          id: "idea/GUI_SMOKE",
          kind: "module",
          layout: "canonical",
          family_id: "ideas",
          family: "idea",
          object_id: "GUI_SMOKE",
          title: "GUI Smoke",
          root: `${isolated.path}/src/modules/idea/GUI_SMOKE`,
          relative_root: "src/modules/idea/GUI_SMOKE",
          source_count: 1,
          sources: []
        }
      ],
      diagnostics: []
    } satisfies ProjectBrowserPayload;

    const markup = renderToStaticMarkup(
      <ProjectManagementPage
        activeProject={isolated}
        browser={browser}
        onActivateProject={() => undefined}
        onOpenBuildPage={() => undefined}
        openTarget="finder"
        projectOptions={[original, isolated]}
        t={createTranslator("en")}
      />
    );

    expect(markup).toContain("/workspace/original/PIHC3");
    expect(markup).toContain("/workspace/isolated/PIHC3");
    expect(markup).toContain('<span class="status-pill planned">Inactive</span>');
    expect(markup).toContain('<span class="status-pill ready">Active</span>');
    expect(markup.match(/<dd>1<\/dd>/g)).toHaveLength(2);
    expect(markup).toContain('aria-controls="management-project-0"');
    expect(markup).toContain('aria-controls="management-project-1"');
  });

  it("renders every configured source root", () => {
    const project = {
      id: "PIHC3",
      projectId: "PIHC3",
      name: "The Pony In The High Castle",
      path: "/workspace/projects/PIHC3",
      sourceRoots: [
        "/workspace/projects/PIHC3/src",
        "/workspace/projects/PIHC3/import",
        "/workspace/projects/PIHC3/overlay"
      ],
      game: "hoi4"
    } as ProjectOption;

    const markup = renderToStaticMarkup(
      <ProjectManagementPage
        activeProject={project}
        browser={null}
        onActivateProject={() => undefined}
        onOpenBuildPage={() => undefined}
        openTarget="finder"
        projectOptions={[project]}
        t={createTranslator("zh")}
      />
    );

    expect(markup).toContain("源代码 1");
    expect(markup).toContain("源代码 2");
    expect(markup).toContain("源代码 3");
    expect(markup).toContain("/workspace/projects/PIHC3/src");
    expect(markup).toContain("/workspace/projects/PIHC3/import");
    expect(markup).toContain("/workspace/projects/PIHC3/overlay");
  });

  it("formats visible management path open failures", () => {
    const openError = (
      pageModule as typeof pageModule & {
        projectManagementOpenError?: (t: ReturnType<typeof createTranslator>, error: unknown) => string;
      }
    ).projectManagementOpenError;

    expect(typeof openError).toBe("function");
    expect(openError?.(createTranslator("zh"), new Error("Opening local paths requires the ParaDev desktop application."))).toBe(
      "打开失败：此操作需要使用 ParaDev 桌面应用。"
    );
  });

  it("does not swallow management path open failures", () => {
    const source = readFileSync(resolve(__dirname, "ProjectManagementPage.tsx"), "utf8");

    expect(source).not.toContain(".catch(() => undefined)");
    expect(source).toContain("projectManagementOpenError(t, error)");
    expect(source).toContain('role="alert"');
  });
});
