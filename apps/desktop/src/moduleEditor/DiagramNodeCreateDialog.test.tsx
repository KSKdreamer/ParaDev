/** @vitest-environment jsdom */

import { act } from "react";
import { createRoot, type Root } from "react-dom/client";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { createTranslator } from "../i18n";
import type {
  EditModuleDiagramRequest,
  ModuleDiagramEditPayload,
} from "../services/paradev";
import type { ProjectDiagramNodeAuthoring } from "../types";
import { DiagramNodeCreateDialog } from "./DiagramNodeCreateDialog";

const mocks = vi.hoisted(() => ({
  editModuleDiagram: vi.fn(),
}));

vi.mock("../services/paradev", () => ({
  editModuleDiagram: mocks.editModuleDiagram,
}));

const authoring: ProjectDiagramNodeAuthoring = {
  title: "Add MIO trait",
  description: "Create a trait in the selected organization.",
  fields: [
    {
      name: "trait_id",
      label: "Trait ID",
      kind: "text",
      required: true,
    },
    {
      name: "title",
      label: "Title",
      kind: "text",
      required: true,
    },
    {
      name: "bonus_value",
      label: "Bonus value",
      kind: "number",
      required: false,
      default: 0.05,
      advanced: true,
    },
  ],
  selection_defaults: [
    { field: "organization_id", source: "organization_id" },
    { field: "parent_trait_id", source: "trait_id" },
    { field: "x", source: "x" },
    { field: "y", source: "y", offset: 1 },
  ],
  requires_selection: true,
};

const contextValues = {
  organization_id: "example_org",
  parent_trait_id: "parent_trait",
  source_path: "src/modules/mio/example/def.txt",
  source_revision: `sha256:${"a".repeat(64)}`,
  x: 2,
  y: 4,
};

const mounted: Array<{
  container: HTMLDivElement;
  root: Root;
}> = [];

beforeEach(() => {
  (
    globalThis as typeof globalThis & {
      IS_REACT_ACT_ENVIRONMENT: boolean;
    }
  ).IS_REACT_ACT_ENVIRONMENT = true;
  mocks.editModuleDiagram.mockReset();
});

afterEach(() => {
  for (const item of mounted.splice(0)) {
    act(() => item.root.unmount());
    item.container.remove();
  }
});

describe("DiagramNodeCreateDialog", () => {
  it("reviews and applies the frozen provider-owned node intent", async () => {
    const onApplied = vi.fn();
    mocks.editModuleDiagram
      .mockResolvedValueOnce(payload())
      .mockResolvedValueOnce(
        payload({
          applied: true,
          status: "applied",
          written: true,
        }),
      );
    const container = renderDialog(onApplied);

    setInputValue(input(container, "Trait ID"), "precision_tools");
    setInputValue(input(container, "Title"), "Precision Tools");
    click(button(container, "Show defaulted fields"));
    setInputValue(input(container, "Bonus value"), "0.08");
    await clickAsync(button(container, "Preview graph item"));

    const preview = mocks.editModuleDiagram.mock
      .calls[0]?.[0] as EditModuleDiagramRequest;
    expect(preview).toEqual({
      projectRoot: "/workspace/PIHC3",
      family: "military_industrial_organization",
      profile: "hoi4",
      nodeIntents: [
        {
          ...contextValues,
          trait_id: "precision_tools",
          title: "Precision Tools",
          bonus_value: 0.08,
        },
      ],
      write: false,
    });
    expect(container.textContent).toContain("planned");
    expect(container.textContent).toContain("2 source files");
    expect(container.textContent).toContain("Exact source edits");
    expect(container.textContent).toContain("def.txt, characters 40–40");
    expect(container.textContent).toContain("trait = {");
    expect(container.textContent).toContain("b".repeat(64));

    await clickAsync(button(container, "Add graph item"));

    expect(mocks.editModuleDiagram.mock.calls[1]?.[0]).toEqual({
      ...preview,
      nodeIntents: preview.nodeIntents?.map((row) => ({
        ...row,
      })),
      planHash: "b".repeat(64),
      write: true,
    });
    expect(onApplied).toHaveBeenCalledOnce();
  });

  it("invalidates a reviewed plan after a visible field changes", async () => {
    mocks.editModuleDiagram.mockResolvedValueOnce(payload());
    const container = renderDialog();
    const traitId = input(container, "Trait ID");
    setInputValue(traitId, "precision_tools");
    setInputValue(input(container, "Title"), "Precision Tools");

    await clickAsync(button(container, "Preview graph item"));
    expect(button(container, "Add graph item")).not.toBeNull();

    setInputValue(traitId, "precision_tools_v2");

    expect(container.textContent).not.toContain("planned");
    expect(button(container, "Preview graph item")).not.toBeNull();
  });
});

function renderDialog(onApplied = vi.fn()): HTMLDivElement {
  const container = document.createElement("div");
  document.body.append(container);
  const root = createRoot(container);
  act(() => {
    root.render(
      <DiagramNodeCreateDialog
        authoring={authoring}
        contextValues={contextValues}
        family="military_industrial_organization"
        onApplied={onApplied}
        onClose={vi.fn()}
        profile="hoi4"
        projectRoot="/workspace/PIHC3"
        t={createTranslator("en")}
      />,
    );
  });
  mounted.push({ container, root });
  return container;
}

function payload(
  overrides: Partial<ModuleDiagramEditPayload> = {},
): ModuleDiagramEditPayload {
  return {
    schema: "paradev.sdk.module_diagram_edit.v1",
    provider_schema: "paradev.hoi4.mio-trait-creation-plan.v1",
    project_id: "PIHC3",
    project_root: "/workspace/PIHC3",
    profile: "hoi4",
    family: "military_industrial_organization",
    status: "planned",
    plan_hash: "b".repeat(64),
    blocked: false,
    applied: false,
    written: false,
    drafts: [{ path: "def.txt" }, { path: "main.loc" }],
    source_replacements: [
      {
        path: "def.txt",
        start: 40,
        end: 40,
        replacement: "trait = {\n  token = precision_tools\n}\n",
      },
      {
        path: "main.loc",
        start: 20,
        end: 20,
        replacement: "[l_english.precision_tools]\nPrecision Tools\n",
      },
    ],
    diagnostics: [],
    files: [],
    ...overrides,
  };
}

function input(container: HTMLElement, label: string): HTMLInputElement {
  const element = Array.from(
    container.querySelectorAll<HTMLInputElement>("input"),
  ).find(
    (candidate) =>
      candidate.closest("label")?.querySelector("small")?.textContent === label,
  );
  if (!element) {
    throw new Error(`Missing input ${label}`);
  }
  return element;
}

function button(container: HTMLElement, text: string): HTMLButtonElement {
  const element = Array.from(
    container.querySelectorAll<HTMLButtonElement>("button"),
  ).find((candidate) => candidate.textContent?.trim() === text);
  if (!element) {
    throw new Error(`Missing button ${text}`);
  }
  return element;
}

function setInputValue(element: HTMLInputElement, value: string) {
  act(() => {
    const setter = Object.getOwnPropertyDescriptor(
      HTMLInputElement.prototype,
      "value",
    )?.set;
    setter?.call(element, value);
    element.dispatchEvent(new Event("input", { bubbles: true }));
    element.dispatchEvent(new Event("change", { bubbles: true }));
  });
}

function click(element: HTMLElement) {
  act(() => element.click());
}

async function clickAsync(element: HTMLElement) {
  await act(async () => {
    element.click();
    await Promise.resolve();
  });
}
