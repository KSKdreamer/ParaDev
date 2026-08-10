/** @vitest-environment jsdom */

import { act } from "react";
import { createRoot, type Root } from "react-dom/client";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { createTranslator } from "../i18n";
import { AssetDraftEditor } from "./AssetDraftEditor";
import type { ModuleEntity, ModuleSourceSlot } from "./model";

const mounted: Array<{ container: HTMLDivElement; root: Root }> = [];

beforeEach(() => {
  (
    globalThis as typeof globalThis & { IS_REACT_ACT_ENVIRONMENT: boolean }
  ).IS_REACT_ACT_ENVIRONMENT = true;
  vi.spyOn(FileReader.prototype, "readAsDataURL").mockImplementation(
    function readAsDataUrl(this: FileReader, file: Blob) {
      Object.defineProperty(this, "result", {
        configurable: true,
        value: `data:${file.type || "application/octet-stream"};base64,cGR4YXNzZXRp`,
      });
      queueMicrotask(() =>
        this.onload?.(new ProgressEvent("load") as ProgressEvent<FileReader>),
      );
    },
  );
});

afterEach(() => {
  for (const item of mounted.splice(0)) {
    act(() => item.root.unmount());
    item.container.remove();
  }
  vi.restoreAllMocks();
});

describe("AssetDraftEditor", () => {
  it("maps new files through Registry-owned resource destinations", async () => {
    const onAssetDrafts = vi.fn();
    const entity = starterEntity();
    const container = renderEditor(entity, [], onAssetDrafts);
    const input = container.querySelector<HTMLInputElement>(
      ".asset-dropzone input[type=file]",
    );
    expect(input).not.toBeNull();

    await chooseFiles(input, [
      new File(["mesh"], "pony_export.mesh", {
        type: "application/octet-stream",
      }),
      new File(["animation"], "walk_cycle.anim", {
        type: "application/octet-stream",
      }),
    ]);

    expect(onAssetDrafts).toHaveBeenCalledTimes(1);
    expect(onAssetDrafts).toHaveBeenCalledWith([
      {
        contentBase64: "cGR4YXNzZXRp",
        fileName: "pony_export.mesh",
        path: "src/modules/entity/ENTITY_TEST/gfx/models/ENTITY_TEST/pony_export.mesh",
        size: 4,
        slotName: "meshes",
      },
      {
        contentBase64: "cGR4YXNzZXRp",
        fileName: "walk_cycle.anim",
        path: "src/modules/entity/ENTITY_TEST/gfx/models/ENTITY_TEST/walk_cycle.anim",
        size: 9,
        slotName: "animations",
      },
    ]);
  });

  it("refuses to guess between duplicate basenames but pins row-level replacement to one exact path", async () => {
    const onAssetDrafts = vi.fn();
    const sources = aggregateSources();
    const entity = aggregateEntity(sources);
    const container = renderEditor(entity, sources, onAssetDrafts);
    const dropInput = container.querySelector<HTMLInputElement>(
      ".asset-dropzone input[type=file]",
    );
    expect(container.textContent).toContain("meshes · copy");

    await chooseFiles(dropInput, [new File(["new mesh"], "mesh.mesh")]);
    expect(onAssetDrafts).toHaveBeenLastCalledWith([
      {
        contentBase64: "cGR4YXNzZXRp",
        fileName: "mesh.mesh",
        path: "src/modules/entity/HOI4DEV_ENTITIES/gfx/models/HOI4DEV_ENTITIES/mesh.mesh",
        size: 8,
        slotName: "meshes",
      },
    ]);

    onAssetDrafts.mockClear();
    const replaceInputs = container.querySelectorAll<HTMLInputElement>(
      ".asset-replace-button input[type=file]",
    );
    expect(replaceInputs).toHaveLength(2);
    await chooseFiles(replaceInputs[1], [new File(["tank mesh"], "mesh.mesh")]);
    expect(onAssetDrafts).toHaveBeenCalledWith([
      {
        contentBase64: "cGR4YXNzZXRp",
        fileName: "mesh.mesh",
        path: "src/modules/entity/HOI4DEV_ENTITIES/gfx/models/HOI4DEV_ENTITIES/mesh.mesh",
        size: 8,
        slotName: "meshes",
      },
      {
        contentBase64: "cGR4YXNzZXRp",
        fileName: "mesh.mesh",
        path: sources[1].relative_path,
        size: 9,
        slotName: "meshes",
        sourceKey: sources[1].draftKey,
      },
    ]);
  });

  it("places every new file at its declared Registry destination", async () => {
    const onAssetDrafts = vi.fn();
    const sources = aggregateSources();
    const container = renderEditor(
      aggregateEntity(sources),
      sources,
      onAssetDrafts,
    );
    const input = container.querySelector<HTMLInputElement>(
      ".asset-dropzone input[type=file]",
    );

    await chooseFiles(input, [
      new File(["mesh"], "mesh.mesh"),
      new File(["animation"], "idle.anim"),
    ]);

    expect(onAssetDrafts).toHaveBeenCalledWith([
      {
        contentBase64: "cGR4YXNzZXRp",
        fileName: "mesh.mesh",
        path: "src/modules/entity/HOI4DEV_ENTITIES/gfx/models/HOI4DEV_ENTITIES/mesh.mesh",
        size: 4,
        slotName: "meshes",
      },
      {
        contentBase64: "cGR4YXNzZXRp",
        fileName: "idle.anim",
        path: "src/modules/entity/HOI4DEV_ENTITIES/gfx/models/HOI4DEV_ENTITIES/idle.anim",
        size: 9,
        slotName: "animations",
      },
    ]);
  });

  it("keeps an ambiguous aggregate resource staged until its destination is chosen", async () => {
    const onAssetDrafts = vi.fn();
    const sources = aggregateCopySources();
    const container = renderEditor(
      aggregateCopyEntity(sources),
      sources,
      onAssetDrafts,
    );
    const input = container.querySelector<HTMLInputElement>(
      ".asset-dropzone input[type=file]",
    );

    await chooseFiles(input, [new File(["texture"], "new.dds")]);

    expect(onAssetDrafts).toHaveBeenCalledWith([
      {
        contentBase64: "cGR4YXNzZXRp",
        fileName: "new.dds",
        path: "",
        size: 7,
      },
    ]);
    expect(container.querySelector('[role="alert"]')?.textContent).toContain(
      "Choose a destination folder",
    );
  });

  it("offers Registry-owned aggregate directories and records the chosen slot", () => {
    const onAssetDrafts = vi.fn();
    const sources = aggregateCopySources();
    const entity = aggregateCopyEntity(sources);
    entity.draftState = "modified";
    entity.drafts.assets = [
      {
        contentBase64: "dGV4dHVyZQ==",
        fileName: "new.dds",
        path: "",
        size: 7,
      },
    ];
    const container = renderEditor(entity, sources, onAssetDrafts);
    const select = container.querySelector<HTMLSelectElement>(
      'select[aria-label="Destination folder"]',
    );

    expect(select).not.toBeNull();
    expect(Array.from(select?.options ?? []).map((option) => option.text)).toEqual(
      [
        "Choose a Registry destination",
        "gfx/interface/ideas/new.dds",
        "gfx/interface/shared/new.dds",
      ],
    );

    act(() => {
      if (select) {
        select.value =
          "src/modules/ui/UI_SHARED/gfx/interface/shared/new.dds";
        select.dispatchEvent(new Event("change", { bubbles: true }));
      }
    });

    expect(onAssetDrafts).toHaveBeenCalledWith([
      {
        contentBase64: "dGV4dHVyZQ==",
        fileName: "new.dds",
        path: "src/modules/ui/UI_SHARED/gfx/interface/shared/new.dds",
        size: 7,
        slotName: "assets",
      },
    ]);
  });

  it("rejects a batch when two files resolve to the same Registry target", async () => {
    const onAssetDrafts = vi.fn();
    const container = renderEditor(starterEntity(), [], onAssetDrafts);
    const input = container.querySelector<HTMLInputElement>(
      ".asset-dropzone input[type=file]",
    );

    await chooseFiles(input, [
      new File(["idle"], "idle.anim"),
      new File(["walk"], "idle.anim"),
    ]);

    expect(onAssetDrafts).not.toHaveBeenCalled();
    expect(container.querySelector('[role="alert"]')?.textContent).toContain(
      "Two selected files target src/modules/entity/ENTITY_TEST/gfx/models/ENTITY_TEST/idle.anim",
    );
  });

  it("rejects the same starter target across sequential drops", async () => {
    const onAssetDrafts = vi.fn();
    const container = renderEditor(starterEntity(), [], onAssetDrafts);
    const input = container.querySelector<HTMLInputElement>(
      ".asset-dropzone input[type=file]",
    );

    await chooseFiles(input, [new File(["idle"], "idle.anim")]);
    expect(onAssetDrafts).toHaveBeenCalledTimes(1);
    await chooseFiles(input, [new File(["walk"], "idle.anim")]);

    expect(onAssetDrafts).toHaveBeenCalledTimes(1);
    expect(container.querySelector('[role="alert"]')?.textContent).toContain(
      "Two selected files target src/modules/entity/ENTITY_TEST/gfx/models/ENTITY_TEST/idle.anim",
    );
  });

  it("keeps the later row replacement when overlapping reads finish out of order", async () => {
    const pendingReaders: FileReader[] = [];
    vi.mocked(FileReader.prototype.readAsDataURL).mockImplementation(
      function deferRead(this: FileReader) {
        pendingReaders.push(this);
      },
    );
    const sources = [aggregateSources()[0]];
    const onAssetDrafts = vi.fn();
    const container = renderEditor(
      aggregateEntity(sources),
      sources,
      onAssetDrafts,
    );
    const replaceInput = container.querySelector<HTMLInputElement>(
      ".asset-replace-button input[type=file]",
    );

    await chooseFiles(replaceInput, [new File(["first"], "mesh.mesh")]);
    await chooseFiles(replaceInput, [new File(["second"], "mesh.mesh")]);
    expect(pendingReaders).toHaveLength(2);

    await resolveReader(pendingReaders[1], "c2Vjb25k");
    expect(onAssetDrafts).toHaveBeenCalledTimes(1);
    expect(onAssetDrafts.mock.calls[0]?.[0]?.[0]).toMatchObject({
      contentBase64: "c2Vjb25k",
      fileName: "mesh.mesh",
      path: sources[0].relative_path,
      sourceKey: sources[0].draftKey,
    });

    await resolveReader(pendingReaders[0], "Zmlyc3Q=");
    expect(onAssetDrafts).toHaveBeenCalledTimes(1);
  });

  it("enforces the pending file-count cap across sequential selections", async () => {
    const entity = starterEntity();
    entity.draftState = "modified";
    entity.drafts.assets = Array.from({ length: 31 }, (_, index) =>
      pendingTextureDraft(index),
    );
    const onAssetDrafts = vi.fn();
    const container = renderEditor(entity, [], onAssetDrafts);
    const input = container.querySelector<HTMLInputElement>(
      ".asset-dropzone input[type=file]",
    );

    await chooseFiles(input, [new File(["a"], "texture-31.dds")]);
    expect(onAssetDrafts).toHaveBeenCalledTimes(1);
    expect(onAssetDrafts.mock.calls[0]?.[0]).toHaveLength(32);

    onAssetDrafts.mockClear();
    await chooseFiles(input, [new File(["b"], "texture-32.dds")]);
    expect(onAssetDrafts).not.toHaveBeenCalled();
    expect(container.querySelector('[role="alert"]')?.textContent).toContain(
      "Keep no more than 32 asset files pending",
    );
  });

  it("enforces the pending byte cap across sequential selections", async () => {
    const entity = starterEntity();
    entity.draftState = "modified";
    entity.drafts.assets = [
      {
        ...pendingTextureDraft(0),
        size: 64 * 1024 * 1024 - 2,
      },
    ];
    const onAssetDrafts = vi.fn();
    const container = renderEditor(entity, [], onAssetDrafts);
    const input = container.querySelector<HTMLInputElement>(
      ".asset-dropzone input[type=file]",
    );

    await chooseFiles(input, [new File(["a"], "texture-01.dds")]);
    expect(onAssetDrafts).toHaveBeenCalledTimes(1);

    onAssetDrafts.mockClear();
    await chooseFiles(input, [new File(["bc"], "texture-02.dds")]);
    expect(onAssetDrafts).not.toHaveBeenCalled();
    expect(container.querySelector('[role="alert"]')?.textContent).toContain(
      "Keep pending assets under 64 MB",
    );
  });

  it("keeps empty and wrong-format row replacements out of an applyable draft", async () => {
    const onAssetDrafts = vi.fn();
    const sources = aggregateSources();
    const container = renderEditor(
      aggregateEntity(sources),
      sources,
      onAssetDrafts,
    );
    const dropInput = container.querySelector<HTMLInputElement>(
      ".asset-dropzone input[type=file]",
    );

    await chooseFiles(dropInput, [new File([], "empty.mesh")]);
    expect(onAssetDrafts).not.toHaveBeenCalled();
    expect(container.querySelector('[role="alert"]')?.textContent).toContain(
      "empty.mesh is empty",
    );

    const replaceInput = container.querySelector<HTMLInputElement>(
      ".asset-replace-button input[type=file]",
    );
    await chooseFiles(replaceInput, [new File(["animation"], "wrong.anim")]);
    expect(onAssetDrafts).toHaveBeenCalledTimes(1);
    expect(container.querySelector('[role="alert"]')?.textContent).toContain(
      "uploaded file extension must match its target extension",
    );
  });

  it("clears a stale top-level error when the conflicting draft is discarded", async () => {
    const onAssetDrafts = vi.fn();
    const entity = starterEntity();
    entity.draftState = "modified";
    entity.drafts.assets = [
      {
        contentBase64: "aWRsZQ==",
        fileName: "idle.anim",
        path: "src/modules/entity/ENTITY_TEST/gfx/models/ENTITY_TEST/idle.anim",
        size: 4,
      },
    ];
    const container = renderEditor(entity, [], onAssetDrafts);
    const input = container.querySelector<HTMLInputElement>(
      ".asset-dropzone input[type=file]",
    );

    await chooseFiles(input, [new File(["walk"], "idle.anim")]);
    expect(container.querySelector('[role="alert"]')).not.toBeNull();

    act(() => {
      container
        .querySelector<HTMLButtonElement>(".asset-draft-row button")
        ?.click();
    });

    expect(onAssetDrafts).toHaveBeenCalledWith([]);
    expect(container.querySelector('[role="alert"]')).toBeNull();
  });

  it("isolates an in-flight file read when selection remounts the editor for another entity", async () => {
    let pendingReader: FileReader | undefined;
    vi.mocked(FileReader.prototype.readAsDataURL).mockImplementationOnce(
      function deferRead(this: FileReader) {
        pendingReader = this;
      },
    );
    const first = starterEntity();
    const second = {
      ...starterEntity(),
      id: "module:entity/ENTITY_OTHER",
      objectId: "ENTITY_OTHER",
      moduleId: "entity/ENTITY_OTHER",
      drafts: {
        text: {},
        assets: [
          {
            contentBase64: "b3RoZXI=",
            fileName: "other.mesh",
            path: "src/modules/entity/ENTITY_OTHER/gfx/models/ENTITY_OTHER/other.mesh",
            size: 5,
          },
        ],
      },
      draftState: "modified" as const,
    };
    const onFirstDrafts = vi.fn();
    const onSecondDrafts = vi.fn();
    const container = document.createElement("div");
    document.body.append(container);
    const root = createRoot(container);
    mounted.push({ container, root });
    const t = createTranslator("en");
    act(() => {
      root.render(
        <AssetDraftEditor
          entity={first}
          key={first.id}
          onAssetDrafts={onFirstDrafts}
          sources={[]}
          t={t}
        />,
      );
    });
    const input = container.querySelector<HTMLInputElement>(
      ".asset-dropzone input[type=file]",
    );
    expect(input).not.toBeNull();
    Object.defineProperty(input, "files", {
      configurable: true,
      value: [new File(["mesh"], "pony.mesh")],
    });
    await act(async () => {
      input?.dispatchEvent(new Event("change", { bubbles: true }));
      await Promise.resolve();
      await Promise.resolve();
    });
    expect(pendingReader).toBeDefined();

    act(() => {
      root.render(
        <AssetDraftEditor
          entity={second}
          key={second.id}
          onAssetDrafts={onSecondDrafts}
          sources={[]}
          t={t}
        />,
      );
    });
    await act(async () => {
      Object.defineProperty(pendingReader, "result", {
        configurable: true,
        value: "data:application/octet-stream;base64,cGR4YXNzZXRp",
      });
      pendingReader?.onload?.(
        new ProgressEvent("load") as ProgressEvent<FileReader>,
      );
      await Promise.resolve();
      await Promise.resolve();
    });

    expect(onFirstDrafts).toHaveBeenCalledWith([
      {
        contentBase64: "cGR4YXNzZXRp",
        fileName: "pony.mesh",
        path: "src/modules/entity/ENTITY_TEST/gfx/models/ENTITY_TEST/pony.mesh",
        size: 4,
        slotName: "meshes",
      },
    ]);
    expect(onSecondDrafts).not.toHaveBeenCalled();
  });
});

function renderEditor(
  entity: ModuleEntity,
  sources: ModuleSourceSlot[],
  onAssetDrafts: (
    assets: NonNullable<ModuleEntity["drafts"]["assets"]>,
  ) => void,
): HTMLDivElement {
  const container = document.createElement("div");
  document.body.append(container);
  const root = createRoot(container);
  mounted.push({ container, root });
  act(() => {
    root.render(
      <AssetDraftEditor
        entity={entity}
        onAssetDrafts={onAssetDrafts}
        sources={sources}
        t={createTranslator("en")}
      />,
    );
  });
  return container;
}

async function chooseFiles(
  input: HTMLInputElement | null | undefined,
  files: File[],
): Promise<void> {
  expect(input).not.toBeNull();
  Object.defineProperty(input, "files", { configurable: true, value: files });
  await act(async () => {
    input?.dispatchEvent(new Event("change", { bubbles: true }));
    await Promise.resolve();
    await Promise.resolve();
  });
}

async function resolveReader(
  reader: FileReader | undefined,
  contentBase64: string,
): Promise<void> {
  expect(reader).toBeDefined();
  await act(async () => {
    Object.defineProperty(reader, "result", {
      configurable: true,
      value: `data:application/octet-stream;base64,${contentBase64}`,
    });
    reader?.onload?.(new ProgressEvent("load") as ProgressEvent<FileReader>);
    await Promise.resolve();
    await Promise.resolve();
  });
}

function pendingTextureDraft(
  index: number,
): NonNullable<ModuleEntity["drafts"]["assets"]>[number] {
  const name = `texture-${String(index).padStart(2, "0")}.dds`;
  return {
    contentBase64: "ZA==",
    fileName: name,
    path: `src/modules/entity/ENTITY_TEST/gfx/models/ENTITY_TEST/${name}`,
    size: 1,
    slotName: "textures",
  };
}

function starterEntity(): ModuleEntity {
  const root = "src/modules/entity/ENTITY_TEST";
  return {
    id: "module:entity/ENTITY_TEST",
    familyId: "entity",
    family: "entity",
    moduleId: "entity/ENTITY_TEST",
    objectId: "ENTITY_TEST",
    title: "Entity Test",
    subtitle: "ENTITY_TEST",
    root: `/workspace/projects/PIHC3/${root}`,
    relativeRoot: root,
    layout: "canonical",
    sourceCount: 3,
    sourceSlots: [
      source(
        "pdx",
        "mesh.gfx",
        `${root}/gfx/models/ENTITY_TEST/mesh.gfx`,
        "code",
      ),
      source(
        "pdx",
        "entity.asset",
        `${root}/gfx/models/ENTITY_TEST/entity.asset`,
        "code",
      ),
      source(
        "pdx",
        "animations.asset",
        `${root}/gfx/models/ENTITY_TEST/animations.asset`,
        "code",
      ),
    ],
    resourceSlots: entityResourceSlots(),
    tags: [],
    draftState: "clean",
    drafts: { text: {} },
  };
}

function aggregateEntity(sources: ModuleSourceSlot[]): ModuleEntity {
  const root = "src/modules/entity/HOI4DEV_ENTITIES";
  return {
    ...starterEntity(),
    id: "module:entity/HOI4DEV_ENTITIES",
    moduleId: "entity/HOI4DEV_ENTITIES",
    objectId: "HOI4DEV_ENTITIES",
    title: "Shared entities",
    subtitle: "HOI4DEV_ENTITIES",
    root: `/workspace/projects/PIHC3/${root}`,
    relativeRoot: root,
    sourceCount: sources.length,
    sourceSlots: sources,
    resourceSlots: entityResourceSlots(),
  };
}

function aggregateSources(): ModuleSourceSlot[] {
  const root = "src/modules/entity/HOI4DEV_ENTITIES/gfx/models/viento";
  return [
    source(
      "meshes",
      "mesh.mesh",
      `${root}/air/airship/mesh.mesh`,
      "asset",
      100,
      "meshes::airship",
    ),
    source(
      "meshes",
      "mesh.mesh",
      `${root}/tank/normal/mesh.mesh`,
      "asset",
      200,
      "meshes::tank",
    ),
  ];
}

function aggregateCopyEntity(sources: ModuleSourceSlot[]): ModuleEntity {
  const root = "src/modules/ui/UI_SHARED";
  return {
    ...starterEntity(),
    id: "module:ui/UI_SHARED",
    familyId: "ui",
    family: "ui",
    moduleId: "ui/UI_SHARED",
    objectId: "UI_SHARED",
    title: "Shared UI",
    subtitle: "UI_SHARED",
    root: `/workspace/projects/PIHC3/${root}`,
    relativeRoot: root,
    sourceCount: sources.length,
    sourceSlots: sources,
    resourceSlots: [
      {
        name: "assets",
        match: "^gfx/interface/(ideas|shared)/.*\\.dds$",
        required: false,
        many: true,
        regex: true,
        kind: "copy",
        shared: false,
      },
    ],
  };
}

function aggregateCopySources(): ModuleSourceSlot[] {
  const root = "src/modules/ui/UI_SHARED";
  return [
    source(
      "assets",
      "idea.dds",
      `${root}/gfx/interface/ideas/idea.dds`,
      "asset",
      100,
      "assets::idea",
    ),
    source(
      "assets",
      "shared.dds",
      `${root}/gfx/interface/shared/shared.dds`,
      "asset",
      200,
      "assets::shared",
    ),
  ];
}

function source(
  slot: string,
  name: string,
  relativePath: string,
  editorKind: ModuleSourceSlot["editorKind"],
  size?: number,
  draftKey = slot,
): ModuleSourceSlot {
  return {
    slot,
    name,
    path: `/workspace/projects/PIHC3/${relativePath}`,
    relative_path: relativePath,
    extension: name.split(".").at(-1) ?? "",
    draftKey,
    editorKind,
    ...(editorKind === "asset" ? { slot_kinds: ["copy"] } : {}),
    ...(size === undefined ? {} : { size }),
  };
}

function entityResourceSlots(): NonNullable<ModuleEntity["resourceSlots"]> {
  return [
    {
      name: "meshes",
      match: "^gfx/models/.*\\.mesh$",
      required: false,
      many: true,
      regex: true,
      kind: "copy",
      shared: false,
      authoring_path: "gfx/models/{object_id}/{filename}",
    },
    {
      name: "animations",
      match: "^gfx/models/.*\\.anim$",
      required: false,
      many: true,
      regex: true,
      kind: "copy",
      shared: false,
      authoring_path: "gfx/models/{object_id}/{filename}",
    },
    {
      name: "textures",
      match: "^gfx/models/.*\\.(dds|png|tga)$",
      required: false,
      many: true,
      regex: true,
      kind: "copy",
      shared: false,
      authoring_path: "gfx/models/{object_id}/{filename}",
    },
  ];
}
