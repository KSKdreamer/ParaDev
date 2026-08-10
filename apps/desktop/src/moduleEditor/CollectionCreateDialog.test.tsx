/** @vitest-environment jsdom */

import { act, useState } from "react";
import { createRoot, type Root } from "react-dom/client";
import {
  afterEach,
  beforeEach,
  describe,
  expect,
  it,
  vi
} from "vitest";
import { createTranslator } from "../i18n";
import type {
  CollectionScaffoldPayload,
  ScaffoldCollectionRequest
} from "../services/paradev";
import type { ProjectTemplate } from "../types";
import { CollectionCreateDialog } from "./CollectionCreateDialog";
import type { ModuleEditorCollectionCreateState } from "./editorSessionStore";

const mocks = vi.hoisted(() => ({
  scaffoldCollection: vi.fn()
}));

vi.mock("../services/paradev", () => ({
  scaffoldCollection: mocks.scaffoldCollection
}));

const mounted: Array<{ container: HTMLDivElement; root: Root }> = [];

beforeEach(() => {
  (
    globalThis as typeof globalThis & {
      IS_REACT_ACT_ENVIRONMENT: boolean;
    }
  ).IS_REACT_ACT_ENVIRONMENT = true;
  mocks.scaffoldCollection.mockReset();
});

afterEach(() => {
  for (const item of mounted.splice(0)) {
    act(() => item.root.unmount());
    item.container.remove();
  }
});

describe("CollectionCreateDialog", () => {
  it("reviews and applies the exact collection plan hash", async () => {
    const onApplied = vi.fn().mockResolvedValue(undefined);
    mocks.scaffoldCollection
      .mockResolvedValueOnce(collectionPayload())
      .mockResolvedValueOnce(collectionPayload(true));
    const container = renderDialog(onApplied);

    setInput(input(container, "Collection ID"), "C01_NEW");
    setInput(input(container, "Focus-tree name"), "新国策树");
    setInput(input(container, "Country tag"), "C01");
    await clickAsync(button(container, "Review files"));

    expect(
      mocks.scaffoldCollection.mock.calls[0]?.[0] as ScaffoldCollectionRequest
    ).toEqual({
      projectRoot: "/workspace/PIHC3",
      templateId: "pihc3:focus-tree/basic",
      collectionId: "C01_NEW",
      values: {
        title: "新国策树",
        country_tag: "C01"
      },
      sourceRoot: "/workspace/PIHC3/src",
      force: false
    });
    expect(container.textContent).toContain(
      "src/collections/focus/C01_NEW - 新国策树/def.txt"
    );
    const apply = button(container, "Create collection");
    expect(apply.disabled).toBe(true);
    click(
      checkbox(
        container,
        "I reviewed these exact project files and want to create them."
      )
    );
    expect(apply.disabled).toBe(false);
    await clickAsync(apply);

    expect(
      mocks.scaffoldCollection.mock.calls[1]?.[0] as ScaffoldCollectionRequest
    ).toEqual(
      expect.objectContaining({
        write: true,
        planHash: "a".repeat(64)
      })
    );
    expect(onApplied).toHaveBeenCalledWith(
      expect.objectContaining({
        collection_id: "C01_NEW",
        written: true
      })
    );
    expect(container.querySelector('[role="dialog"]')).toBeNull();
  });

  it("validates required fields before requesting a plan", async () => {
    const container = renderDialog();

    await clickAsync(button(container, "Review files"));

    expect(mocks.scaffoldCollection).not.toHaveBeenCalled();
    expect(container.querySelector('[role="alert"]')?.textContent).toContain(
      "starts with a letter or underscore"
    );
  });

  it("opens an AI-retained dry plan without requesting a second preview", async () => {
    const onApplied = vi.fn().mockResolvedValue(undefined);
    const onDraftChange = vi.fn();
    const plan = collectionPayload();
    const request = {
      projectRoot: "/workspace/PIHC3",
      templateId: "pihc3:focus-tree/basic",
      collectionId: "C01_NEW",
      values: { title: "新国策树", country_tag: "C01" },
      sourceRoot: "/workspace/PIHC3/src",
      force: false
    };
    const initialState: ModuleEditorCollectionCreateState = {
      open: true,
      preview: { plan, request },
      pristineSourceRoot: "/workspace/PIHC3/src",
      pristineTemplateId: "pihc3:focus-tree/basic",
      templateId: "pihc3:focus-tree/basic",
      collectionId: "C01_NEW",
      values: request.values,
      showAdvanced: false,
      sourceRoot: "/workspace/PIHC3/src"
    };
    mocks.scaffoldCollection.mockResolvedValueOnce(collectionPayload(true));
    const container = renderDialog(onApplied, {
      initialState,
      onDraftChange
    });

    expect(mocks.scaffoldCollection).not.toHaveBeenCalled();
    expect(container.textContent).toContain(
      "src/collections/focus/C01_NEW - 新国策树/def.txt"
    );
    expect(onDraftChange).toHaveBeenCalledWith(
      expect.objectContaining({
        open: true,
        preview: { plan, request }
      })
    );

    click(
      checkbox(
        container,
        "I reviewed these exact project files and want to create them."
      )
    );
    await clickAsync(button(container, "Create collection"));

    expect(mocks.scaffoldCollection).toHaveBeenCalledOnce();
    expect(mocks.scaffoldCollection).toHaveBeenCalledWith({
      ...request,
      write: true,
      planHash: "a".repeat(64)
    });
    expect(onDraftChange).toHaveBeenCalledWith(null);
  });
});

function renderDialog(
  onApplied: (
    payload: CollectionScaffoldPayload
  ) => void | Promise<void> = vi.fn(),
  options: {
    initialState?: ModuleEditorCollectionCreateState;
    onDraftChange?: (
      state: ModuleEditorCollectionCreateState | null
    ) => void;
  } = {}
): HTMLDivElement {
  const container = document.createElement("div");
  document.body.append(container);
  const root = createRoot(container);
  mounted.push({ container, root });
  function Harness() {
    const [open, setOpen] = useState(true);
    return open ? (
      <CollectionCreateDialog
        initialState={options.initialState}
        onApplied={onApplied}
        onClose={() => setOpen(false)}
        onDraftChange={options.onDraftChange}
        projectRoot="/workspace/PIHC3"
        sourceRoots={[
          {
            path: "/workspace/PIHC3/src",
            relative_path: "src",
            default: true
          }
        ]}
        t={createTranslator("en")}
        templates={[focusTreeTemplate]}
      />
    ) : null;
  }
  act(() => root.render(<Harness />));
  return container;
}

const focusTreeTemplate: ProjectTemplate = {
  id: "pihc3:focus-tree/basic",
  title: "PIHC3 Basic Focus Tree",
  family: "focus",
  kind: "collection",
  source: "project",
  authoring_ready: true,
  args: {
    title: {
      required: true,
      default: "",
      advanced: false,
      label: "Focus-tree name"
    },
    country_tag: {
      required: true,
      default: "",
      advanced: false,
      label: "Country tag"
    },
    continuous_focus_y: {
      required: false,
      default: "2400",
      advanced: true,
      label: "Continuous-focus Y",
      type: "number"
    }
  },
  files: ["def.txt"]
};

function collectionPayload(written = false): CollectionScaffoldPayload {
  return {
    schema: "paradev.sdk.collection_scaffold.v1",
    project_id: "PIHC3",
    template_id: "pihc3:focus-tree/basic",
    kind: "collection",
    family: "focus",
    object_id: "C01_NEW",
    collection_id: "C01_NEW",
    folder_name: "C01_NEW - 新国策树",
    source_root: "/workspace/PIHC3/src",
    root: "/workspace/PIHC3/src/collections/focus/C01_NEW - 新国策树",
    values: {
      object_id: "C01_NEW",
      collection_id: "C01_NEW",
      title: "新国策树",
      country_tag: "C01",
      continuous_focus_y: "2400"
    },
    blocked: false,
    written,
    applied: written,
    plan_hash: "a".repeat(64),
    diagnostics: [],
    files: [
      {
        action: "create",
        collection_path: "def.txt",
        path:
          "/workspace/PIHC3/src/collections/focus/C01_NEW - 新国策树/def.txt",
        relative_path:
          "src/collections/focus/C01_NEW - 新国策树/def.txt"
      }
    ],
    authoring_plan: {}
  };
}

function input(
  container: HTMLElement,
  label: string
): HTMLInputElement {
  const element = container.querySelector<HTMLInputElement>(
    `input[aria-label="${label}"]`
  );
  if (!element) {
    throw new Error(`Missing input ${label}.`);
  }
  return element;
}

function button(
  container: HTMLElement,
  label: string
): HTMLButtonElement {
  const element = [...container.querySelectorAll("button")].find(
    (candidate) => candidate.textContent?.trim() === label
  );
  if (!element) {
    throw new Error(`Missing button ${label}.`);
  }
  return element;
}

function checkbox(
  container: HTMLElement,
  label: string
): HTMLInputElement {
  const element = [...container.querySelectorAll<HTMLInputElement>(
    'input[type="checkbox"]'
  )].find((candidate) => candidate.parentElement?.textContent?.trim() === label);
  if (!element) {
    throw new Error(`Missing checkbox ${label}.`);
  }
  return element;
}

function setInput(element: HTMLInputElement, value: string): void {
  act(() => {
    const setter = Object.getOwnPropertyDescriptor(
      HTMLInputElement.prototype,
      "value"
    )?.set;
    setter?.call(element, value);
    element.dispatchEvent(new Event("input", { bubbles: true }));
    element.dispatchEvent(new Event("change", { bubbles: true }));
  });
}

function click(element: HTMLElement): void {
  act(() => element.click());
}

async function clickAsync(element: HTMLElement): Promise<void> {
  await act(async () => {
    element.click();
    await Promise.resolve();
  });
}
