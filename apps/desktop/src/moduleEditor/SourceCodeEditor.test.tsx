import { renderToStaticMarkup } from "react-dom/server";
import { beforeEach, describe, expect, it, vi } from "vitest";

const mocks = vi.hoisted(() => ({
  createPdxLspExtensions: vi.fn(() => []),
  json: vi.fn(() => []),
  yaml: vi.fn(() => [])
}));

vi.mock("@uiw/react-codemirror", () => ({
  default: ({ value }: { value: string }) => <div data-editor-value={value} />
}));

vi.mock("./pdxLsp", () => ({
  createPdxLspExtensions: mocks.createPdxLspExtensions
}));

vi.mock("@codemirror/lang-json", () => ({
  json: mocks.json
}));

vi.mock("@codemirror/lang-yaml", () => ({
  yaml: mocks.yaml
}));

import { SourceCodeEditor } from "./SourceCodeEditor";

describe("SourceCodeEditor", () => {
  beforeEach(() => {
    mocks.createPdxLspExtensions.mockClear();
    mocks.json.mockClear();
    mocks.yaml.mockClear();
  });

  it("passes the configured HOI4 game root into PDX LSP extensions", () => {
    renderToStaticMarkup(
      <SourceCodeEditor
        gameRoot="/Games/Hearts of Iron IV"
        kind="code"
        onChange={() => undefined}
        projectRoot="/workspace/projects/PIHC3"
        sourcePath="src/common/ideas/sample.txt"
        theme="light"
        value="idea = {}"
      />
    );

    expect(mocks.createPdxLspExtensions).toHaveBeenCalledWith({
      gameRoot: "/Games/Hearts of Iron IV",
      projectRoot: "/workspace/projects/PIHC3",
      sourcePath: "src/common/ideas/sample.txt"
    });
  });

  it("does not attach PDX LSP extensions to localization buffers", () => {
    renderToStaticMarkup(
      <SourceCodeEditor
        gameRoot="/Games/Hearts of Iron IV"
        kind="localization"
        onChange={() => undefined}
        projectRoot="/workspace/projects/PIHC3"
        sourcePath="src/localisation/english/sample_l_english.yml"
        theme="light"
        value="l_english:"
      />
    );

    expect(mocks.createPdxLspExtensions).not.toHaveBeenCalled();
  });

  it.each(["meta.yaml", "settings.yml"])("uses YAML language support for %s code sources", (fileName) => {
    renderToStaticMarkup(
      <SourceCodeEditor
        gameRoot="/Games/Hearts of Iron IV"
        kind="code"
        onChange={() => undefined}
        projectRoot="/workspace/projects/PIHC3"
        sourcePath={`/workspace/projects/PIHC3/src/modules/entity/VIENTO_AIRSHIP/${fileName}`}
        theme="light"
        value="type: entity"
      />
    );

    expect(mocks.yaml).toHaveBeenCalledOnce();
    expect(mocks.json).not.toHaveBeenCalled();
    expect(mocks.createPdxLspExtensions).not.toHaveBeenCalled();
  });

  it("uses JSON language support without attaching PDX LSP extensions", () => {
    renderToStaticMarkup(
      <SourceCodeEditor
        gameRoot="/Games/Hearts of Iron IV"
        kind="code"
        onChange={() => undefined}
        projectRoot="/workspace/projects/PIHC3"
        sourcePath="/workspace/projects/PIHC3/src/modules/entity/VIENTO_AIRSHIP/record.json"
        theme="light"
        value={'{"mesh":{"scale":1},"entities":[]}'}
      />
    );

    expect(mocks.json).toHaveBeenCalledOnce();
    expect(mocks.createPdxLspExtensions).not.toHaveBeenCalled();
  });
});
