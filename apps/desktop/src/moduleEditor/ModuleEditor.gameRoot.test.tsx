import { renderToStaticMarkup } from "react-dom/server";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { createTranslator } from "../i18n";
import type { ProjectBrowserPayload } from "../types";

const mocks = vi.hoisted(() => ({
  detailProps: [] as Array<Record<string, unknown>>
}));

vi.mock("./ModuleEntityDetails", () => ({
  ModuleEntityDetails: (props: Record<string, unknown>) => {
    mocks.detailProps.push(props);
    return <div data-game-root={String(props.gameRoot ?? "")} data-testid="module-entity-details" />;
  }
}));

import { ModuleEditor } from "./ModuleEditor";

const browser: ProjectBrowserPayload = {
  schema: "paradev.sdk.project-browser.v1",
  project_id: "PIHC3",
  title: "The Pony In The High Castle",
  root: "/workspace/projects/PIHC3",
  profile: "hoi4",
  filters: {},
  diagnostics: [],
  families: [
    {
      id: "ideas",
      family: "idea",
      title: "Ideas",
      item_count: 1,
      source_count: 1,
      layouts: ["canonical"]
    }
  ],
  items: [
    {
      id: "ideas:IDEA_ALPHA",
      kind: "module",
      layout: "canonical",
      family_id: "ideas",
      family: "idea",
      object_id: "IDEA_ALPHA",
      module_id: "ideas/IDEA_ALPHA",
      title: "Alpha Idea",
      root: "/workspace/projects/PIHC3/src/modules/idea/IDEA_ALPHA",
      relative_root: "src/modules/idea/IDEA_ALPHA",
      source_count: 1,
      sources: [
        {
          slot: "def",
          name: "def.pdx",
          path: "/workspace/projects/PIHC3/src/modules/idea/IDEA_ALPHA/def.pdx",
          relative_path: "src/modules/idea/IDEA_ALPHA/def.pdx",
          extension: "pdx"
        }
      ]
    }
  ]
};

describe("ModuleEditor HOI4 game root wiring", () => {
  beforeEach(() => {
    mocks.detailProps.length = 0;
  });

  it("passes the configured HOI4 game root into entity details", () => {
    const markup = renderToStaticMarkup(
      <ModuleEditor
        browser={browser}
        familyId="ideas"
        gameRoot="/Games/Hearts of Iron IV"
        locale="en"
        onPinTab={() => undefined}
        onProjectRefresh={async () => undefined}
        openTarget="finder"
        templates={null}
        t={createTranslator("en")}
        theme="light"
      />
    );

    expect(markup).toContain('data-game-root="/Games/Hearts of Iron IV"');
    expect(mocks.detailProps[0]).toMatchObject({
      gameRoot: "/Games/Hearts of Iron IV",
      projectRoot: "/workspace/projects/PIHC3"
    });
  });
});
