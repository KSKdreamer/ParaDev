/** @vitest-environment jsdom */

import { act, useState } from "react";
import { createRoot, type Root } from "react-dom/client";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { createTranslator } from "../i18n";
import type {
  ModuleCreateBatchPayload,
  CreateModulesRequest
} from "../services/paradev";
import type { ProjectBrowserItem, ProjectTemplate } from "../types";
import { ModuleCreateDialog } from "./ModuleCreateDialog";
import type { ModuleEditorBatchCreateState } from "./editorSessionStore";

const mocks = vi.hoisted(() => ({
  createModules: vi.fn(),
  openProjectPath: vi.fn()
}));

vi.mock("../services/paradev", () => ({
  createModules: mocks.createModules,
  openProjectPath: mocks.openProjectPath
}));

const template: ProjectTemplate = {
  id: "pihc3:idea/basic",
  title: "PIHC3 idea",
  family: "idea",
  source: "project",
  authoring_ready: true,
  diagnostic_codes: [],
  args: {
    title: {
      required: true,
      default: "",
      advanced: false,
      type: "string",
      label: "Title"
    },
    cic: {
      required: true,
      default: "0",
      advanced: false,
      type: "number",
      label: "CIC"
    }
  },
  form: {
    fields: [
      {
        name: "title",
        target: "values",
        required: true,
        default: "",
        advanced: false,
        type: "string",
        label: "Title",
        description: "Preferred-language display name used by `main.loc`.",
        description_source: "generated"
      },
      {
        name: "cic",
        target: "values",
        required: true,
        default: "0",
        advanced: false,
        type: "number",
        label: "CIC",
        description: "Decimal factory-output modifier; use 0.02 for 2%.",
        description_source: "declared"
      }
    ]
  },
  files: ["meta.yaml", "idea.json"]
};

const mounted: Array<{ container: HTMLDivElement; root: Root }> = [];

beforeEach(() => {
  (globalThis as typeof globalThis & { IS_REACT_ACT_ENVIRONMENT: boolean }).IS_REACT_ACT_ENVIRONMENT = true;
  mocks.createModules.mockReset();
  mocks.openProjectPath.mockReset();
});

afterEach(() => {
  for (const item of mounted.splice(0)) {
    act(() => item.root.unmount());
    item.container.remove();
  }
});

describe("ModuleCreateDialog", () => {
  it("renders SDK-owned field help with its declared or generated provenance", () => {
    const container = renderDialog();
    const help = Array.from(
      container.querySelectorAll<HTMLElement>(
        ".module-create-field-description"
      )
    );

    expect(help.map((row) => row.textContent)).toContain(
      "Preferred-language display name used by `main.loc`."
    );
    expect(
      help.find((row) => row.textContent?.startsWith("Preferred-language"))
        ?.dataset.descriptionSource
    ).toBe("generated");
    expect(
      help.find((row) => row.textContent?.startsWith("Decimal factory-output"))
        ?.dataset.descriptionSource
    ).toBe("declared");
  });

  it("suggests existing referenced collections without blocking a custom id", () => {
    const focusTemplate: ProjectTemplate = {
      ...template,
      id: "pihc3:focus/basic",
      family: "focus",
      args: {
        tree: {
          required: true,
          default: "",
          advanced: false,
          label: "Focus tree",
          reference: { kind: "collection", family: "focus" }
        }
      },
      form: undefined
    };
    const referenceItem: ProjectBrowserItem = {
      id: "focus:FOCUS_TREE_C08",
      kind: "collection",
      layout: "canonical",
      family_id: "focuses",
      family: "focus",
      object_id: "FOCUS_TREE_C08",
      collection_id: "FOCUS_TREE_C08",
      title: "C08 national focus tree",
      root: "/workspace/PIHC3/src/collections/focus/FOCUS_TREE_C08",
      relative_root: "src/collections/focus/FOCUS_TREE_C08",
      source_count: 1,
      sources: []
    };
    const container = renderDialog(
      vi.fn(),
      null,
      vi.fn(),
      "single",
      {},
      { referenceItems: [referenceItem], templates: [focusTemplate] }
    );
    const field = input(container, "Focus tree");
    const listId = field.getAttribute("list");

    expect(listId).toBeTruthy();
    expect(
      container.querySelector<HTMLOptionElement>(
        `datalist#${listId} option[value="FOCUS_TREE_C08"]`
      )?.label
    ).toBe("C08 national focus tree — FOCUS_TREE_C08");

    setInputValue(field, "CUSTOM_TREE");
    expect(field.value).toBe("CUSTOM_TREE");
  });

  it("repairs a retained blank source root without discarding draft fields", async () => {
    mocks.createModules.mockResolvedValueOnce(
      batchPayload(["A"], "create")
    );
    const initialState: ModuleEditorBatchCreateState = {
      open: true,
      pristineSourceRoot: "",
      pristineTemplateId: "pihc3:idea/basic",
      rows: [
        {
          key: 1,
          objectId: "A",
          templateId: "pihc3:idea/basic",
          values: { title: "Alpha", cic: "0.02" }
        }
      ],
      showAdvanced: false,
      sourceRoot: ""
    };
    const container = renderDialog(vi.fn(), initialState);

    await clickAsync(button(container, "Preview batch"));

    expect(mocks.createModules).toHaveBeenCalledWith(
      expect.objectContaining({
        sourceRoot: "/workspace/PIHC3/src",
        modules: [
          expect.objectContaining({
            object_id: "A",
            values: expect.objectContaining({ title: "Alpha", cic: 0.02 })
          })
        ]
      })
    );
  });

  it("previews structured rows and applies only the frozen request with its exact hash", async () => {
    const onApplied = vi.fn();
    mocks.createModules
      .mockResolvedValueOnce(batchPayload(["A", "B"], "create"))
      .mockResolvedValueOnce(batchPayload(["A", "B"], "created", { applied: true, written: true }));
    const container = renderDialog(onApplied);

    setSelectValue(select(container, "Source root"), "/workspace/PIHC3/imports");
    setInputValue(input(container, "Object ID for module 1"), "A");
    setInputValue(input(container, "Title for module 1"), "Alpha");
    setInputValue(input(container, "CIC for module 1"), "0.02");
    click(button(container, "Add module"));
    setInputValue(input(container, "Object ID for module 2"), "B");
    setInputValue(input(container, "Title for module 2"), "Beta");
    setInputValue(input(container, "CIC for module 2"), "0.05");

    await clickAsync(button(container, "Preview batch"));

    const previewRequest = mocks.createModules.mock.calls[0]?.[0] as CreateModulesRequest;
    expect(previewRequest).toEqual({
      projectId: "PIHC3",
      projectRoot: "/workspace/PIHC3",
      modules: [
        {
          template_id: "pihc3:idea/basic",
          object_id: "A",
          values: { title: "Alpha", cic: 0.02 }
        },
        {
          template_id: "pihc3:idea/basic",
          object_id: "B",
          values: { title: "Beta", cic: 0.05 }
        }
      ],
      sourceRoot: "/workspace/PIHC3/imports",
      write: false
    });
    expect(container.textContent).toContain("Exact plan ready");
    expect(container.textContent).toContain("a".repeat(64));

    await clickAsync(button(container, "Create 2 modules"));

    expect(mocks.createModules.mock.calls[1]?.[0]).toEqual({
      ...previewRequest,
      modules: previewRequest.modules.map((row) => ({
        ...row,
        values: { ...row.values }
      })),
      planHash: "a".repeat(64),
      write: true
    });
    expect(onApplied).toHaveBeenCalledOnce();
    expect(container.textContent).toContain("Transaction finished");
    expect(container.textContent).toContain("Created: 2");
  });

  it("invalidates the plan as soon as an authored value changes", async () => {
    mocks.createModules.mockResolvedValueOnce(batchPayload(["A"], "create"));
    const container = renderDialog();
    const objectId = input(container, "Object ID for module 1");
    setInputValue(objectId, "A");
    setInputValue(input(container, "Title for module 1"), "Alpha");

    await clickAsync(button(container, "Preview batch"));
    expect(button(container, "Create 1 modules")).not.toBeNull();

    setInputValue(objectId, "A_CHANGED");

    expect(container.textContent).not.toContain("Exact plan ready");
    expect(button(container, "Preview batch")).not.toBeNull();
    expect(mocks.createModules).toHaveBeenCalledOnce();
  });

  it("reuses the exact batch transaction as a focused single-module dialog", async () => {
    mocks.createModules.mockResolvedValueOnce(
      batchPayload(["TECH_NEW"], "create")
    );
    const container = renderDialog(
      vi.fn(),
      null,
      vi.fn(),
      "single"
    );

    expect(container.textContent).toContain("Create one technology");
    expect(container.textContent).toContain(
      "Add icon.png after creation."
    );
    expect(container.textContent).not.toContain("Add module");
    expect(container.textContent).not.toContain("Up to 256");
    expect(
      container.querySelector(".module-batch-dialog.single")
    ).not.toBeNull();

    setInputValue(
      input(container, "Object ID"),
      "TECH_NEW"
    );
    setInputValue(
      input(container, "Title"),
      "New technology"
    );
    setInputValue(input(container, "CIC"), "0.02");
    await clickAsync(button(container, "Preview module"));

    expect(mocks.createModules).toHaveBeenCalledWith({
      projectId: "PIHC3",
      projectRoot: "/workspace/PIHC3",
      modules: [
        {
          template_id: "pihc3:idea/basic",
          object_id: "TECH_NEW",
          values: {
            title: "New technology",
            cic: 0.02
          }
        }
      ],
      sourceRoot: "/workspace/PIHC3/src",
      write: false
    });
    expect(button(container, "Create module")).not.toBeNull();
    expect(container.textContent).not.toContain("module 1");
  });

  it("reviews provider-owned selected-node defaults in the single create form", async () => {
    mocks.createModules.mockResolvedValueOnce(
      batchPayload(["TECH_CHILD"], "create")
    );
    const container = renderDialog(
      vi.fn(),
      null,
      vi.fn(),
      "single",
      {
        cic: "0.08",
        title: "Inherited child"
      }
    );

    expect(input(container, "Title").value).toBe("Inherited child");
    expect(input(container, "CIC").value).toBe("0.08");
    setInputValue(input(container, "Object ID"), "TECH_CHILD");
    await clickAsync(button(container, "Preview module"));

    expect(mocks.createModules).toHaveBeenCalledWith({
      projectId: "PIHC3",
      projectRoot: "/workspace/PIHC3",
      modules: [
        {
          template_id: "pihc3:idea/basic",
          object_id: "TECH_CHILD",
          values: {
            title: "Inherited child",
            cic: 0.08
          }
        }
      ],
      sourceRoot: "/workspace/PIHC3/src",
      write: false
    });
  });

  it("applies a retained exact-hash preview without planning it a second time", async () => {
    const onApplied = vi.fn();
    const onDraftChange = vi.fn();
    const initialState = retainedPreviewState();
    mocks.createModules.mockResolvedValueOnce(
      batchPayload(["A"], "created", { applied: true, written: true })
    );
    const container = renderDialog(onApplied, initialState, onDraftChange);

    expect(container.textContent).toContain("Exact plan ready");
    expect(container.textContent).toContain("a".repeat(64));
    expect(mocks.createModules).not.toHaveBeenCalled();
    expect(onDraftChange).toHaveBeenCalled();
    expect(onDraftChange.mock.calls[0]?.[0]).not.toHaveProperty("preview");

    await clickAsync(button(container, "Create 1 modules"));

    expect(mocks.createModules).toHaveBeenCalledOnce();
    expect(mocks.createModules).toHaveBeenCalledWith({
      projectId: "PIHC3",
      projectRoot: "/workspace/PIHC3",
      modules: [
        {
          template_id: "pihc3:idea/basic",
          object_id: "A",
          values: { title: "Alpha", cic: 0.02 }
        }
      ],
      sourceRoot: "/workspace/PIHC3/imports",
      planHash: "a".repeat(64),
      write: true
    });
    expect(onApplied).toHaveBeenCalledOnce();
  });

  it("invalidates a retained preview when edited and requires a new preview", async () => {
    mocks.createModules.mockResolvedValueOnce(
      batchPayload(["A_CHANGED"], "create")
    );
    const container = renderDialog(vi.fn(), retainedPreviewState());

    expect(container.textContent).toContain("Exact plan ready");
    setInputValue(
      input(container, "Object ID for module 1"),
      "A_CHANGED"
    );

    expect(container.textContent).not.toContain("Exact plan ready");
    expect(container.textContent).not.toContain("Create 1 modules");
    expect(button(container, "Preview batch")).not.toBeNull();
    expect(mocks.createModules).not.toHaveBeenCalled();

    await clickAsync(button(container, "Preview batch"));

    expect(mocks.createModules).toHaveBeenCalledOnce();
    expect(mocks.createModules).toHaveBeenCalledWith(
      expect.objectContaining({
        modules: [
          expect.objectContaining({
            object_id: "A_CHANGED"
          })
        ],
        write: false
      })
    );
  });

  it("blocks case-equivalent duplicate targets before calling the backend", async () => {
    const container = renderDialog();
    setInputValue(input(container, "Object ID for module 1"), "ALPHA");
    setInputValue(input(container, "Title for module 1"), "Alpha");
    click(button(container, "Add module"));
    setInputValue(input(container, "Object ID for module 2"), "alpha");
    setInputValue(input(container, "Title for module 2"), "Duplicate");

    await clickAsync(button(container, "Preview batch"));

    expect(mocks.createModules).not.toHaveBeenCalled();
    expect(container.textContent).toContain("Object ID ALPHA appears more than once");
    expect(container.textContent).toContain("Object ID alpha appears more than once");
  });

  it("locks structural row edits while preview and apply requests are in flight", async () => {
    const preview = deferred<ModuleCreateBatchPayload>();
    const apply = deferred<ModuleCreateBatchPayload>();
    mocks.createModules
      .mockReturnValueOnce(preview.promise)
      .mockReturnValueOnce(apply.promise);
    const container = renderDialog();
    setInputValue(input(container, "Object ID for module 1"), "A");
    setInputValue(input(container, "Title for module 1"), "Alpha");
    click(button(container, "Add module"));
    setInputValue(input(container, "Object ID for module 2"), "B");
    setInputValue(input(container, "Title for module 2"), "Beta");

    click(button(container, "Preview batch"));

    expect(button(container, "Add module").disabled).toBe(true);
    expect(button(container, "Remove module 1").disabled).toBe(true);
    expect(button(container, "Remove module 2").disabled).toBe(true);
    click(button(container, "Add module"));
    expect(container.querySelectorAll('input[aria-label^="Object ID for module"]')).toHaveLength(2);

    await act(async () => {
      preview.resolve(batchPayload(["A", "B"], "create"));
      await preview.promise;
    });
    click(button(container, "Create 2 modules"));

    expect(button(container, "Add module").disabled).toBe(true);
    expect(button(container, "Remove module 1").disabled).toBe(true);
    expect(button(container, "Remove module 2").disabled).toBe(true);

    await act(async () => {
      apply.resolve(batchPayload(["A", "B"], "created", { applied: true, written: true }));
      await apply.promise;
    });
  });

  it("retains and opens rollback recovery paths after a failed exact-hash apply", async () => {
    const recoveryPath = "/workspace/PIHC3/src/.paradev/module-transactions/txn-123";
    mocks.createModules
      .mockResolvedValueOnce(batchPayload(["A"], "create"))
      .mockResolvedValueOnce(
        batchPayload(["A"], "blocked", {
          blocked: true,
          diagnostics: [
            {
              code: "module_batch.rollback_incomplete",
              severity: "error",
              message: "Rollback was incomplete.",
              recovery_path: recoveryPath
            }
          ]
        })
      );
    const container = renderDialog();
    const objectId = input(container, "Object ID for module 1");
    setInputValue(objectId, "A");
    setInputValue(input(container, "Title for module 1"), "Alpha");

    await clickAsync(button(container, "Preview batch"));
    await clickAsync(button(container, "Create 1 modules"));

    expect(container.textContent).toContain("Recovery data was retained");
    expect(container.textContent).toContain(recoveryPath);
    expect(mocks.createModules.mock.calls[1]?.[0]).toMatchObject({
      planHash: "a".repeat(64),
      write: true
    });

    setInputValue(objectId, "A_CHANGED");
    expect(container.textContent).toContain(recoveryPath);

    await clickAsync(button(container, "Open recovery folder"));
    expect(mocks.openProjectPath).toHaveBeenCalledWith(recoveryPath, "finder");

    click(button(container, "Cancel"));
    expect(container.textContent).not.toContain(recoveryPath);
    click(button(container, "Reopen batch"));
    expect(container.textContent).toContain(recoveryPath);
    click(button(container, "Dismiss recovery notice"));
    expect(container.textContent).not.toContain(recoveryPath);
    click(button(container, "Cancel"));
    click(button(container, "Reopen batch"));
    expect(container.textContent).not.toContain(recoveryPath);
  });

  it("closes on Escape and restores focus to the opener", () => {
    const container = renderDialog();
    click(button(container, "Cancel"));
    const opener = button(container, "Reopen batch");
    opener.focus();

    click(opener);
    expect(document.activeElement).toBe(input(container, "Object ID for module 1"));
    act(() => {
      document.activeElement?.dispatchEvent(
        new KeyboardEvent("keydown", { bubbles: true, key: "Escape" })
      );
    });

    expect(container.querySelector('[role="dialog"]')).toBeNull();
    expect(document.activeElement).toBe(opener);
  });
});

function renderDialog(
  onApplied = vi.fn(),
  initialState: ModuleEditorBatchCreateState | null = null,
  onDraftChange = vi.fn(),
  mode: "batch" | "single" = "batch",
  initialValues: Readonly<Record<string, string>> = {},
  overrides: {
    referenceItems?: readonly ProjectBrowserItem[];
    templates?: ProjectTemplate[];
  } = {}
): HTMLDivElement {
  const container = document.createElement("div");
  document.body.append(container);
  const root = createRoot(container);
  mounted.push({ container, root });
  act(() => {
    root.render(
      <DialogHarness
        initialState={initialState}
        mode={mode}
        initialValues={initialValues}
        onApplied={onApplied}
        onDraftChange={onDraftChange}
        referenceItems={overrides.referenceItems}
        templates={overrides.templates}
      />
    );
  });
  return container;
}

function DialogHarness({
  initialState,
  mode,
  initialValues,
  onApplied,
  onDraftChange,
  referenceItems,
  templates
}: {
  initialState: ModuleEditorBatchCreateState | null;
  initialValues: Readonly<Record<string, string>>;
  mode: "batch" | "single";
  onApplied: (payload: ModuleCreateBatchPayload) => void | Promise<void>;
  onDraftChange: (state: ModuleEditorBatchCreateState | null) => void;
  referenceItems?: readonly ProjectBrowserItem[];
  templates?: ProjectTemplate[];
}) {
  const [open, setOpen] = useState(true);
  const [recoveryPaths, setRecoveryPaths] = useState<string[]>([]);
  return (
    <>
      <button onClick={() => setOpen(true)} type="button">
        Reopen batch
      </button>
      {open ? (
        <ModuleCreateDialog
          dialogText={
            mode === "single"
              ? {
                  detail: "Create one reviewed source module.",
                  eyebrow: "Source-backed authoring",
                  guidance: "Add icon.png after creation.",
                  title: "Create one technology"
                }
              : undefined
          }
          familyTitle="Ideas"
          initialValues={initialValues}
          initialState={initialState}
          mode={mode}
          onApplied={onApplied}
          onClose={() => setOpen(false)}
          onDraftChange={onDraftChange}
          onRecoveryPathsChange={setRecoveryPaths}
          openTarget="finder"
          projectId="PIHC3"
          projectRoot="/workspace/PIHC3"
          recoveryPaths={recoveryPaths}
          referenceItems={referenceItems}
          sourceRoots={[
            { path: "/workspace/PIHC3/src", relative_path: "src", default: true },
            { path: "/workspace/PIHC3/imports", relative_path: "imports", default: false }
          ]}
          t={createTranslator("en")}
          templates={templates ?? [template]}
        />
      ) : null}
    </>
  );
}

function retainedPreviewState(): ModuleEditorBatchCreateState {
  return {
    open: true,
    preview: {
      modules: [
        {
          template_id: "pihc3:idea/basic",
          object_id: "A",
          values: { title: "Alpha", cic: 0.02 }
        }
      ],
      plan: batchPayload(["A"], "create"),
      sourceRoot: "/workspace/PIHC3/imports"
    },
    pristineSourceRoot: "/workspace/PIHC3/src",
    pristineTemplateId: "pihc3:idea/basic",
    rows: [
      {
        key: 1,
        objectId: "A",
        templateId: "pihc3:idea/basic",
        values: { title: "Alpha", cic: "0.02" }
      }
    ],
    showAdvanced: false,
    sourceRoot: "/workspace/PIHC3/imports"
  };
}

function batchPayload(
  objectIds: string[],
  status: "blocked" | "create" | "created" | "unchanged",
  overrides: Partial<ModuleCreateBatchPayload> = {}
): ModuleCreateBatchPayload {
  const counts = {
    create: status === "create" ? objectIds.length : 0,
    created: status === "created" ? objectIds.length : 0,
    unchanged: status === "unchanged" ? objectIds.length : 0,
    blocked: status === "blocked" ? objectIds.length : 0
  };
  return {
    schema: "paradev.sdk.module_batch.v1",
    project_id: "PIHC3",
    source_root: "/workspace/PIHC3/imports",
    plan_hash: "a".repeat(64),
    blocked: status === "blocked",
    applied: false,
    written: false,
    requested_count: objectIds.length,
    counts,
    diagnostics: [],
    modules: objectIds.map((objectId, index) => ({
      index,
      family: "idea",
      object_id: objectId,
      module_id: `idea/${objectId}`,
      status,
      blocked: status === "blocked",
      diagnostics: [],
      files: [{ relative_path: `${objectId}/meta.yaml` }]
    })),
    ...overrides
  };
}

function input(container: HTMLElement, label: string): HTMLInputElement {
  const element = container.querySelector<HTMLInputElement>(`input[aria-label="${label}"]`);
  if (!element) {
    throw new Error(`Missing input ${label}.`);
  }
  return element;
}

function select(container: HTMLElement, label: string): HTMLSelectElement {
  const element = container.querySelector<HTMLSelectElement>(`select[aria-label="${label}"]`);
  if (!element) {
    throw new Error(`Missing select ${label}.`);
  }
  return element;
}

function button(container: HTMLElement, label: string): HTMLButtonElement {
  const element = [...container.querySelectorAll("button")].find(
    (candidate) => candidate.textContent?.trim() === label || candidate.getAttribute("aria-label") === label
  );
  if (!element) {
    throw new Error(`Missing button ${label}.`);
  }
  return element;
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

function setInputValue(element: HTMLInputElement, value: string): void {
  const setter = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, "value")?.set;
  if (!setter) {
    throw new Error("Missing HTMLInputElement value setter.");
  }
  act(() => {
    setter.call(element, value);
    element.dispatchEvent(new Event("input", { bubbles: true }));
  });
}

function setSelectValue(element: HTMLSelectElement, value: string): void {
  const setter = Object.getOwnPropertyDescriptor(HTMLSelectElement.prototype, "value")?.set;
  if (!setter) {
    throw new Error("Missing HTMLSelectElement value setter.");
  }
  act(() => {
    setter.call(element, value);
    element.dispatchEvent(new Event("change", { bubbles: true }));
  });
}

function deferred<T>(): {
  promise: Promise<T>;
  resolve: (value: T) => void;
} {
  let resolve = (_value: T): void => undefined;
  const promise = new Promise<T>((complete) => {
    resolve = (value: T) => complete(value);
  });
  return { promise, resolve };
}
