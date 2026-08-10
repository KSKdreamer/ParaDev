/** @vitest-environment jsdom */

import { act } from "react";
import { createRoot, type Root } from "react-dom/client";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { createTranslator } from "../i18n";
import type { DraftApplyPayload } from "../types";
import type { ModuleEditorSourceUpdateState } from "./editorSessionStore";
import { SourceUpdateReviewDialog } from "./SourceUpdateReviewDialog";

const mocks = vi.hoisted(() => ({
  applyProjectDraft: vi.fn()
}));

vi.mock("../services/paradev", () => ({
  applyProjectDraft: mocks.applyProjectDraft
}));

const mounted: Array<{ container: HTMLDivElement; root: Root }> = [];

beforeEach(() => {
  (
    globalThis as typeof globalThis & {
      IS_REACT_ACT_ENVIRONMENT: boolean;
    }
  ).IS_REACT_ACT_ENVIRONMENT = true;
  mocks.applyProjectDraft.mockReset();
});

afterEach(() => {
  for (const item of mounted.splice(0)) {
    act(() => item.root.unmount());
    item.container.remove();
  }
});

describe("SourceUpdateReviewDialog", () => {
  it("shows localized Guided controls and applies only the exact dry-plan edits", async () => {
    const onApplied = vi.fn().mockResolvedValue(undefined);
    const finishBusy = vi.fn();
    const onBusyStart = vi.fn(() => finishBusy);
    const payload: DraftApplyPayload = {
      schema: "paradev.rest.draft_apply.v1",
      project_id: "PIHC3",
      written: true,
      files: [
        {
          path: "/workspace/PIHC3/src/modules/idea/IDEA_ALPHA/def.txt",
          relative_path: "src/modules/idea/IDEA_ALPHA/def.txt",
          operation: "write_text",
          encoding: "utf-8"
        }
      ]
    };
    mocks.applyProjectDraft.mockResolvedValueOnce(payload);
    const container = renderDialog({ onApplied, onBusyStart });

    expect(container.textContent).toContain("idea/IDEA_ALPHA");
    expect(container.textContent).toContain(
      "src/modules/idea/IDEA_ALPHA/def.txt"
    );
    expect(container.textContent).toContain("Country resource crystals");
    expect(container.textContent).toContain("1→2");

    const apply = button(container, "Apply source changes");
    expect(apply.disabled).toBe(true);
    click(
      checkbox(
        container,
        "I reviewed the 1 changed source files and want to apply this exact plan."
      )
    );
    expect(apply.disabled).toBe(false);
    await clickAsync(apply);

    expect(onBusyStart).toHaveBeenCalledOnce();
    expect(mocks.applyProjectDraft).toHaveBeenCalledWith({
      projectId: "PIHC3",
      projectRoot: "/workspace/PIHC3",
      sourceEdits: sourceUpdateState.plan.sourceEdits
    });
    expect(onApplied).toHaveBeenCalledWith(payload);
    expect(finishBusy).toHaveBeenCalledOnce();
  });

  it("keeps the review open and localizes an atomic apply failure", async () => {
    mocks.applyProjectDraft.mockRejectedValueOnce(
      new Error("source changed after planning")
    );
    const container = renderDialog();

    click(
      checkbox(
        container,
        "I reviewed the 1 changed source files and want to apply this exact plan."
      )
    );
    await clickAsync(button(container, "Apply source changes"));

    expect(container.querySelector('[role="dialog"]')).not.toBeNull();
    expect(container.querySelector('[role="alert"]')?.textContent).toContain(
      "source changed after planning"
    );
  });
});

const sourceEdit = {
  path: "/workspace/PIHC3/src/modules/idea/IDEA_ALPHA/def.txt",
  text: "modifier = { local_resources = 2 }\n",
  expectedSize: 34,
  expectedMtimeNs: "1770000000123456789"
};

const sourceUpdateState: ModuleEditorSourceUpdateState = {
  open: true,
  requests: [
    {
      source_path: "src/modules/idea/IDEA_ALPHA/def.txt",
      module_id: "idea/IDEA_ALPHA",
      values: { "pdx-control-002": 2 },
      control_labels: {
        "pdx-control-002": {
          default: "Country resource crystals",
          zh: "国家水晶资源"
        }
      }
    }
  ],
  plan: {
    schema: "paradev.source-form-update-batch.v1",
    projectId: "PIHC3",
    changed: true,
    counts: { requested: 1, changed: 1, unchanged: 0 },
    updates: [
      {
        schema: "paradev.source-form-update.v1",
        projectId: "PIHC3",
        family: "idea",
        moduleId: "idea/IDEA_ALPHA",
        path: sourceEdit.path,
        relativePath: "src/modules/idea/IDEA_ALPHA/def.txt",
        sourceFormat: "pdx",
        formContract: "paradev.pdx.guided-form.v1",
        changed: true,
        changes: [
          { controlId: "pdx-control-002", previous: 1, value: 2 }
        ],
        sourceEdit
      }
    ],
    sourceEdits: [sourceEdit]
  }
};

function renderDialog({
  onApplied = vi.fn(),
  onBusyStart = () => vi.fn()
}: {
  onApplied?: (payload: DraftApplyPayload) => Promise<void> | void;
  onBusyStart?: () => () => void;
} = {}): HTMLDivElement {
  const container = document.createElement("div");
  document.body.append(container);
  const root = createRoot(container);
  mounted.push({ container, root });
  act(() =>
    root.render(
      <SourceUpdateReviewDialog
        initialState={sourceUpdateState}
        locale="en"
        onApplied={onApplied}
        onBusyStart={onBusyStart}
        onClose={vi.fn()}
        projectRoot="/workspace/PIHC3"
        t={createTranslator("en")}
      />
    )
  );
  return container;
}

function button(container: HTMLElement, label: string): HTMLButtonElement {
  const element = [...container.querySelectorAll("button")].find(
    (candidate) => candidate.textContent?.trim() === label
  );
  if (!element) {
    throw new Error(`Missing button ${label}.`);
  }
  return element;
}

function checkbox(container: HTMLElement, label: string): HTMLInputElement {
  const element = [...container.querySelectorAll<HTMLInputElement>(
    'input[type="checkbox"]'
  )].find((candidate) => candidate.parentElement?.textContent?.trim() === label);
  if (!element) {
    throw new Error(`Missing checkbox ${label}.`);
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
