/** @vitest-environment jsdom */

import { act, useState } from "react";
import { createRoot, type Root } from "react-dom/client";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { createTranslator } from "../i18n";
import type {
  DuplicateModuleRequest,
  ModuleDuplicatePayload
} from "../services/paradev";
import { ModuleDuplicateDialog } from "./ModuleDuplicateDialog";

const mocks = vi.hoisted(() => ({
  duplicateModule: vi.fn()
}));

vi.mock("../services/paradev", () => ({
  duplicateModule: mocks.duplicateModule
}));

const mounted: Array<{ container: HTMLDivElement; root: Root }> = [];

beforeEach(() => {
  (
    globalThis as typeof globalThis & {
      IS_REACT_ACT_ENVIRONMENT: boolean;
    }
  ).IS_REACT_ACT_ENVIRONMENT = true;
  mocks.duplicateModule.mockReset();
});

afterEach(() => {
  for (const item of mounted.splice(0)) {
    act(() => item.root.unmount());
    item.container.remove();
  }
});

describe("ModuleDuplicateDialog", () => {
  it("preserves uppercase PIHC3 identifier style in the suggested duplicate id", () => {
    const container = renderDialog(undefined, "TECHNOLOGY_X");

    expect(input(container, "New object ID").value).toBe(
      "TECHNOLOGY_X_COPY"
    );
  });

  it("previews inventory and applies only the frozen request with its exact hash", async () => {
    const onApplied = vi.fn().mockResolvedValue(undefined);
    mocks.duplicateModule
      .mockResolvedValueOnce(duplicatePayload())
      .mockResolvedValueOnce(duplicatePayload("duplicated"));
    const container = renderDialog(onApplied);

    setInputValue(input(container, "New object ID"), "demo_variant");
    setSelectValue(
      select(container, "Destination source root"),
      "/workspace/PIHC3/imports"
    );
    await clickAsync(button(container, "Review copy"));

    expect(container.textContent).toContain("Independent copy plan ready");
    expect(container.textContent).toContain("1 folders");
    expect(container.textContent).toContain("2 files");
    expect(container.textContent).toContain("update 1 text file");
    expect(container.textContent).toContain(".paradev");
    expect(
      mocks.duplicateModule.mock.calls[0]?.[0] as DuplicateModuleRequest
    ).toEqual({
      projectRoot: "/workspace/PIHC3",
      moduleId: "modifier/demo",
      objectId: "demo_variant",
      sourceRoot: "/workspace/PIHC3/src",
      destinationSourceRoot: "/workspace/PIHC3/imports",
      identity: "rewrite",
      write: false
    });

    await clickAsync(button(container, "Create duplicate"));

    expect(
      mocks.duplicateModule.mock.calls[1]?.[0] as DuplicateModuleRequest
    ).toEqual({
      projectRoot: "/workspace/PIHC3",
      moduleId: "modifier/demo",
      objectId: "demo_variant",
      sourceRoot: "/workspace/PIHC3/src",
      destinationSourceRoot: "/workspace/PIHC3/imports",
      identity: "rewrite",
      write: true,
      planHash: "a".repeat(64)
    });
    expect(onApplied).toHaveBeenCalledWith(
      expect.objectContaining({
        module_id: "modifier/demo_variant",
        status: "duplicated"
      })
    );
    expect(container.querySelector('[role="dialog"]')).toBeNull();
  });

  it("invalidates a reviewed plan when the target changes", async () => {
    mocks.duplicateModule.mockResolvedValueOnce(duplicatePayload());
    const container = renderDialog();

    await clickAsync(button(container, "Review copy"));
    expect(container.textContent).toContain("Independent copy plan ready");

    setInputValue(input(container, "New object ID"), "changed_copy");

    expect(container.textContent).toContain(
      "Preview the copy before any folder is created."
    );
    expect(
      [...container.querySelectorAll("button")].some(
        (candidate) => candidate.textContent?.trim() === "Create duplicate"
      )
    ).toBe(false);
  });

  it("keeps the dialog open and disables apply for a blocked plan", async () => {
    mocks.duplicateModule.mockResolvedValueOnce(
      duplicatePayload("blocked", [
        {
          code: "module_duplicate.destination_exists",
          message: "The destination folder already exists."
        }
      ])
    );
    const container = renderDialog();

    await clickAsync(button(container, "Review copy"));

    expect(container.textContent).toContain("Copy is blocked");
    expect(container.textContent).toContain(
      "The destination folder already exists."
    );
    expect(container.querySelector('[role="alert"]')).not.toBeNull();
    expect(
      [...container.querySelectorAll("button")].some(
        (candidate) => candidate.textContent?.trim() === "Create duplicate"
      )
    ).toBe(false);
  });

  it("reports cleanup warnings after a successful copy without inviting a duplicate retry", async () => {
    const onApplied = vi.fn().mockResolvedValue(undefined);
    mocks.duplicateModule
      .mockResolvedValueOnce(duplicatePayload())
      .mockResolvedValueOnce(
        duplicatePayload("duplicated", [
          {
            code: "module_duplicate.cleanup_pending",
            message:
              "The duplicate was created, but hidden transaction cleanup is still pending.",
            severity: "warning"
          }
        ])
      );
    const container = renderDialog(onApplied);

    await clickAsync(button(container, "Review copy"));
    await clickAsync(button(container, "Create duplicate"));

    expect(onApplied).toHaveBeenCalledOnce();
    expect(container.textContent).toContain("Duplicate created");
    expect(container.textContent).toContain(
      "hidden transaction cleanup is still pending"
    );
    expect(container.querySelector(".module-duplicate-diagnostics .warning"))
      .not.toBeNull();
    expect(
      [...container.querySelectorAll("button")].some(
        (candidate) => candidate.textContent?.trim() === "Review again"
      )
    ).toBe(false);

    click(button(container, "Done"));
    expect(container.querySelector('[role="dialog"]')).toBeNull();
  });

  it("traps focus, closes on Escape, and restores focus to the opener", () => {
    const container = renderDialog();
    click(button(container, "Cancel"));
    const opener = button(container, "Open duplicate");
    opener.focus();

    click(opener);
    expect(document.activeElement).toBe(input(container, "New object ID"));
    const firstFocusable = button(container, "Cancel");
    firstFocusable.focus();
    act(() => {
      document.activeElement?.dispatchEvent(
        new KeyboardEvent("keydown", {
          bubbles: true,
          key: "Tab",
          shiftKey: true
        })
      );
    });
    expect(document.activeElement).toBe(button(container, "Review copy"));

    act(() => {
      document.activeElement?.dispatchEvent(
        new KeyboardEvent("keydown", { bubbles: true, key: "Escape" })
      );
    });
    expect(container.querySelector('[role="dialog"]')).toBeNull();
    expect(document.activeElement).toBe(opener);
  });

  it("keeps dismissal disabled while a preview owns the session", async () => {
    let finishPreview: ((value: ModuleDuplicatePayload) => void) | undefined;
    mocks.duplicateModule.mockReturnValueOnce(
      new Promise<ModuleDuplicatePayload>((resolve) => {
        finishPreview = resolve;
      })
    );
    const container = renderDialog();

    act(() => button(container, "Review copy").click());
    const cancel = button(container, "Cancel");
    expect(cancel.disabled).toBe(true);
    act(() => {
      container.querySelector('[role="dialog"]')?.dispatchEvent(
        new KeyboardEvent("keydown", { bubbles: true, key: "Escape" })
      );
    });
    expect(container.querySelector('[role="dialog"]')).not.toBeNull();

    await act(async () => {
      finishPreview?.(duplicatePayload());
      await Promise.resolve();
    });
    expect(button(container, "Cancel").disabled).toBe(false);
  });
});

function renderDialog(
  onApplied: (payload: ModuleDuplicatePayload) => Promise<void> = vi
    .fn()
    .mockResolvedValue(undefined),
  objectId = "demo"
): HTMLDivElement {
  const container = document.createElement("div");
  document.body.append(container);
  const root = createRoot(container);
  mounted.push({ container, root });
  act(() => {
    root.render(<DialogHarness objectId={objectId} onApplied={onApplied} />);
  });
  return container;
}

function DialogHarness({
  objectId,
  onApplied
}: {
  objectId: string;
  onApplied: (payload: ModuleDuplicatePayload) => Promise<void>;
}) {
  const [open, setOpen] = useState(true);
  return (
    <>
      <button onClick={() => setOpen(true)} type="button">
        Open duplicate
      </button>
      {open ? (
        <ModuleDuplicateDialog
          moduleId="modifier/demo"
          objectId={objectId}
          onApplied={onApplied}
          onClose={() => setOpen(false)}
          projectRoot="/workspace/PIHC3"
          sourceRoot="/workspace/PIHC3/src"
          sourceRoots={[
            {
              path: "/workspace/PIHC3/src",
              relative_path: "src",
              default: true
            },
            {
              path: "/workspace/PIHC3/imports",
              relative_path: "imports",
              default: false
            }
          ]}
          t={createTranslator("en")}
          title="Demo modifier"
        />
      ) : null}
    </>
  );
}

function duplicatePayload(
  status: ModuleDuplicatePayload["status"] = "planned",
  diagnostics: Array<Record<string, unknown>> = []
): ModuleDuplicatePayload {
  const duplicated = status === "duplicated";
  const blocked = status === "blocked";
  return {
    schema: "paradev.sdk.module_duplicate.v1",
    project_id: "PIHC3",
    source_module_id: "modifier/demo",
    module_id: "modifier/demo_variant",
    family: "modifier",
    object_id: "demo_variant",
    source_root: "/workspace/PIHC3/src",
    destination_source_root: "/workspace/PIHC3/imports",
    source_module_root: "/workspace/PIHC3/src/modules/modifier/demo",
    root: "/workspace/PIHC3/imports/modules/modifier/demo_variant",
    source_relative_path: "src/modules/modifier/demo",
    relative_path: "imports/modules/modifier/demo_variant",
    status,
    blocked,
    applied: duplicated,
    written: duplicated,
    plan_hash: "a".repeat(64),
    identity_mode: "rewrite",
    identity_rewriter: "paradev.token-identity.v1",
    content_rewritten: true,
    paths_rewritten: false,
    diagnostics,
    directories: [
      {
        relative_path: "assets",
        target_relative_path: "assets",
        kind: "directory",
        identity: [1, 11],
        mode: 493,
        mtime_ns: "123456789",
        action: "copy"
      }
    ],
    files: [
      {
        relative_path: "def.txt",
        target_relative_path: "def.txt",
        kind: "file",
        identity: [1, 12],
        mode: 420,
        mtime_ns: "123456790",
        size_bytes: 32,
        sha256: "b".repeat(64),
        target_size_bytes: 32,
        target_sha256: "d".repeat(64),
        content_rewritten: true,
        action: "rewrite"
      },
      {
        relative_path: "icon.png",
        target_relative_path: "icon.png",
        kind: "file",
        identity: [1, 13],
        mode: 420,
        mtime_ns: "123456791",
        size_bytes: 992,
        sha256: "c".repeat(64),
        target_size_bytes: 992,
        target_sha256: "c".repeat(64),
        content_rewritten: false,
        action: "copy"
      }
    ],
    exclusions: [
      {
        relative_path: ".paradev",
        kind: "directory",
        identity: [1, 14],
        mode: 493,
        mtime_ns: "123456792",
        reason: "module_local_system_tree",
        action: "exclude"
      }
    ],
    totals: {
      directory_count: 1,
      file_count: 2,
      excluded_count: 1,
      size_bytes: 1024,
      target_size_bytes: 1024,
      rewritten_file_count: 1,
      renamed_path_count: 0
    },
    source: {
      module_id: "modifier/demo",
      source_root: "/workspace/PIHC3/src",
      root: "/workspace/PIHC3/src/modules/modifier/demo",
      relative_path: "src/modules/modifier/demo",
      root_identity: [1, 1],
      modules_identity: [1, 2],
      family_identity: [1, 3],
      module_identity: [1, 4],
      tree_digest: "d".repeat(64),
      content_digest: "e".repeat(64),
      identity_rewriter: "paradev.token-identity.v1"
    },
    destination: {
      module_id: "modifier/demo_variant",
      source_root: "/workspace/PIHC3/imports",
      root: "/workspace/PIHC3/imports/modules/modifier/demo_variant",
      relative_path: "imports/modules/modifier/demo_variant",
      root_identity: [1, 1],
      modules_identity: [1, 5],
      family_identity: [1, 6],
      target_identity: duplicated ? [1, 15] : null,
      entry_count: 2,
      entry_names_digest: "f".repeat(64),
      content_digest: "1".repeat(64)
    },
  };
}

function input(container: HTMLElement, label: string): HTMLInputElement {
  const element = container.querySelector<HTMLInputElement>(
    `input[aria-label="${label}"]`
  );
  if (!element) {
    throw new Error(`Missing input ${label}.`);
  }
  return element;
}

function select(container: HTMLElement, label: string): HTMLSelectElement {
  const element = container.querySelector<HTMLSelectElement>(
    `select[aria-label="${label}"]`
  );
  if (!element) {
    throw new Error(`Missing select ${label}.`);
  }
  return element;
}

function button(container: HTMLElement, label: string): HTMLButtonElement {
  const element = [...container.querySelectorAll("button")].find(
    (candidate) =>
      candidate.textContent?.trim() === label ||
      candidate.getAttribute("aria-label") === label
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
  const setter = Object.getOwnPropertyDescriptor(
    HTMLInputElement.prototype,
    "value"
  )?.set;
  if (!setter) {
    throw new Error("Missing HTMLInputElement value setter.");
  }
  act(() => {
    setter.call(element, value);
    element.dispatchEvent(new Event("input", { bubbles: true }));
  });
}

function setSelectValue(element: HTMLSelectElement, value: string): void {
  const setter = Object.getOwnPropertyDescriptor(
    HTMLSelectElement.prototype,
    "value"
  )?.set;
  if (!setter) {
    throw new Error("Missing HTMLSelectElement value setter.");
  }
  act(() => {
    setter.call(element, value);
    element.dispatchEvent(new Event("change", { bubbles: true }));
  });
}
