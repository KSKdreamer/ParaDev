/** @vitest-environment jsdom */

import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it, vi } from "vitest";
import { createTranslator } from "../i18n";
import type { ModuleEntity, ModuleSourceSlot } from "./model";
import { ImageDraftEditor } from "./ImageDraftEditor";

vi.mock("react-dropzone", () => ({
  useDropzone: () => ({
    getInputProps: () => ({}),
    getRootProps: (props: Record<string, unknown> = {}) => props,
    isDragActive: false,
    isDragReject: false
  })
}));

vi.mock("react-filerobot-image-editor", () => ({
  default: () => null,
  TABS: {
    ADJUST: "adjust",
    ANNOTATE: "annotate",
    FILTERS: "filters",
    FINETUNE: "finetune",
    RESIZE: "resize",
    WATERMARK: "watermark"
  },
  TOOLS: { CROP: "crop" }
}));

const source: ModuleSourceSlot = {
  slot: "icon",
  name: "icon.png",
  path: "/workspace/projects/PIHC3/src/modules/idea/IDEA_ALPHA/icon.png",
  relative_path: "src/modules/idea/IDEA_ALPHA/icon.png",
  extension: "png",
  draftKey: "icon",
  editorKind: "image"
};

const ddsSource: ModuleSourceSlot = {
  ...source,
  name: "icon.dds",
  path: "/workspace/projects/PIHC3/src/modules/idea/IDEA_ALPHA/icon.dds",
  relative_path: "src/modules/idea/IDEA_ALPHA/icon.dds",
  extension: "dds"
};

const entity: ModuleEntity = {
  id: "ideas:IDEA_ALPHA",
  familyId: "ideas",
  family: "idea",
  moduleId: "idea/IDEA_ALPHA",
  objectId: "IDEA_ALPHA",
  title: "Alpha Idea",
  subtitle: "IDEA_ALPHA",
  root: "/workspace/projects/PIHC3/src/modules/idea/IDEA_ALPHA",
  relativeRoot: "src/modules/idea/IDEA_ALPHA",
  layout: "canonical",
  sourceCount: 1,
  sourceSlots: [source],
  tags: [],
  draftState: "modified",
  drafts: { text: {} }
};

describe("ImageDraftEditor", () => {
  it("disables Save and explains why a non-PNG manual target is unsafe", () => {
    const markup = renderEditor("/workspace/projects/PIHC3/src/modules/idea/IDEA_ALPHA/icon.dds");
    const button = saveButton(markup);

    expect(markup).toContain('aria-invalid="true"');
    expect(markup).toContain("Processed image drafts contain PNG data. Choose a .png path unless you are replacing a supported existing non-PNG source at its exact path; this DDS target is not valid.");
    expect(button?.disabled).toBe(true);
  });

  it("disables Save when an existing PNG source is redirected to a sibling PNG", () => {
    const markup = renderEditor("/workspace/projects/PIHC3/src/modules/idea/IDEA_ALPHA/custom.png");
    const button = saveButton(markup);

    expect(markup).toContain("Replace the selected source at src/modules/idea/IDEA_ALPHA/icon.png. Custom save paths are only available when the entity has no existing image source.");
    expect(button?.disabled).toBe(true);
  });

  it("allows the exact relative path of the selected PNG source", () => {
    const markup = renderEditor(source.relative_path);
    const button = saveButton(markup);

    expect(markup).not.toContain('aria-invalid="true"');
    expect(markup).not.toContain("Custom save paths are only available");
    expect(button?.disabled).toBe(false);
  });

  it("allows the exact DDS source path and explains the apply-time conversion", () => {
    const markup = renderEditor(ddsSource.relative_path, ddsSource);
    const button = saveButton(markup);

    expect(markup).not.toContain('aria-invalid="true"');
    expect(markup).toContain("This DDS source stays at its existing path.");
    expect(markup).toContain("PNG output to DDS when you apply the draft.");
    expect(button?.disabled).toBe(false);
  });

  it.each(["dds", "tga"])("does not pass a raw %s preview to Filerobot", (format) => {
    const selectedSource = sourceWithFormat(format);
    const markup = renderEditor(selectedSource.path, selectedSource, { includeDraft: false });
    const button = saveButton(markup);

    expect(markup).not.toContain("filerobot-editor-frame");
    expect(markup).toContain(`${format.toUpperCase()} previews are not supported by the image editor.`);
    expect(markup).toContain("Drop or load a PNG/JPEG/WebP/BMP replacement to start editing");
    expect(button?.disabled).toBe(true);
  });

  it("shows the DDS replacement-input prompt in Chinese", () => {
    const markup = renderEditor(ddsSource.path, ddsSource, { includeDraft: false, locale: "zh" });

    expect(markup).toContain("图片编辑器不支持预览 DDS");
    expect(markup).toContain("请拖放或加载 PNG/JPEG/WebP/BMP 替换图片以开始编辑");
  });

  it("keeps browser-decodable non-PNG source previews editable", () => {
    const webpSource = sourceWithFormat("webp");
    const markup = renderEditor(webpSource.relative_path, webpSource, { includeDraft: false });
    const button = saveButton(markup);

    expect(markup).toContain("filerobot-editor-frame");
    expect(markup).not.toContain("previews are not supported");
    expect(button?.disabled).toBe(false);
  });

  it("keeps DDS replacement identity pinned to the selected source", () => {
    const markup = renderEditor("/workspace/projects/PIHC3/src/modules/idea/IDEA_ALPHA/custom.dds", ddsSource);
    const button = saveButton(markup);

    expect(markup).toContain("Replace the selected source at src/modules/idea/IDEA_ALPHA/icon.dds. Custom save paths are only available when the entity has no existing image source.");
    expect(button?.disabled).toBe(true);
  });

  it.each([
    "/workspace/projects/PIHC3/src/modules/idea/IDEA_ALPHA/new-icon.png",
    "/workspace/projects/PIHC3/src/modules/idea/IDEA_ALPHA/new-icon.dds",
    ""
  ])("blocks source-less image drafts instead of accepting %j", (path) => {
    const markup = renderEditor(path, null);
    const button = saveButton(markup);

    expect(markup).toContain(
      "Image creation is unavailable because the project SDK did not provide an exact family-owned target for this module."
    );
    expect(markup).toContain("ParaDev will not guess a filename.");
    expect(button?.disabled).toBe(true);
  });

  it("enables a pinned family-declared image target that is still absent", () => {
    const declaredTarget: ModuleSourceSlot = {
      ...source,
      exists: false
    };
    const markup = renderEditor(
      declaredTarget.relative_path,
      declaredTarget
    );
    const button = saveButton(markup);
    const root = document.createElement("div");
    root.innerHTML = markup;

    expect(markup).toContain(
      "This family declares the image path below. Apply will create it only if the target is still absent."
    );
    expect(markup).not.toContain("Image creation is unavailable");
    expect(
      root.querySelector<HTMLInputElement>(".image-path-field input")?.readOnly
    ).toBe(true);
    expect(button?.disabled).toBe(false);
  });
});

function renderEditor(
  path: string,
  selectedSource: ModuleSourceSlot | null = source,
  { includeDraft = true, locale = "en" }: { includeDraft?: boolean; locale?: "en" | "zh" } = {}
): string {
  return renderToStaticMarkup(
    <ImageDraftEditor
      defaultSavePath={selectedSource?.path ?? "/workspace/projects/PIHC3/src/modules/idea/IDEA_ALPHA/new-icon.png"}
      entity={{
        ...entity,
        sourceSlots: selectedSource ? [selectedSource] : [],
        drafts: {
          text: {},
          ...(includeDraft
            ? {
                image: {
                  fileName: "icon.png",
                  ...(selectedSource ? { sourceKey: selectedSource.draftKey } : {}),
                  path,
                  previewUrl: "data:image/png;base64,cG5n",
                  contentBase64: "cG5n"
                }
              }
            : {})
        }
      }}
      initialImageSource="data:image/png;base64,cG5n"
      onImageDraft={() => undefined}
      source={selectedSource}
      t={createTranslator(locale)}
      theme="light"
    />
  );
}

function sourceWithFormat(format: string): ModuleSourceSlot {
  return {
    ...source,
    name: source.name.replace(/\.png$/i, `.${format}`),
    path: source.path.replace(/\.png$/i, `.${format}`),
    relative_path: source.relative_path.replace(/\.png$/i, `.${format}`),
    extension: format
  };
}

function saveButton(markup: string): HTMLButtonElement | undefined {
  const root = document.createElement("div");
  root.innerHTML = markup;
  return [...root.querySelectorAll("button")].find((button) => button.textContent?.trim() === "Save");
}
