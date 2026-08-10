/** @vitest-environment jsdom */

import { act } from "react";
import { createRoot, type Root } from "react-dom/client";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { createTranslator } from "../i18n";
import { UnsavedChangesDialog } from "./UnsavedChangesDialog";

describe("UnsavedChangesDialog", () => {
  let container: HTMLDivElement;
  let root: Root;

  beforeEach(() => {
    container = document.createElement("div");
    document.body.append(container);
    root = createRoot(container);
  });

  afterEach(() => {
    act(() => root.unmount());
    container.remove();
  });

  it("focuses the safe action and supports keyboard cancellation", () => {
    const onCancel = vi.fn();
    act(() => {
      root.render(
        <UnsavedChangesDialog
          busy={false}
          dirtySessionCount={1}
          onCancel={onCancel}
          onDiscard={vi.fn()}
          t={createTranslator("en")}
        />
      );
    });

    const dialog = container.querySelector<HTMLElement>('[role="alertdialog"]');
    const keepEditing = button("Keep editing");
    expect(dialog).not.toBeNull();
    expect(document.activeElement).toBe(keepEditing);

    act(() => {
      dialog?.dispatchEvent(
        new KeyboardEvent("keydown", { bubbles: true, key: "Escape" })
      );
    });
    expect(onCancel).toHaveBeenCalledTimes(1);
  });

  it("blocks destructive close while an authoring write is running", () => {
    const onDiscard = vi.fn();
    act(() => {
      root.render(
        <UnsavedChangesDialog
          busy
          dirtySessionCount={1}
          onCancel={vi.fn()}
          onDiscard={onDiscard}
          t={createTranslator("en")}
        />
      );
    });

    const discard = button("Discard changes and close");
    expect(discard.disabled).toBe(true);
    expect(container.textContent).toContain(
      "ParaDev is writing module changes"
    );
    act(() => discard.click());
    expect(onDiscard).not.toHaveBeenCalled();
  });

  it("does not render an unsaved warning after pending work becomes clean", () => {
    act(() => {
      root.render(
        <UnsavedChangesDialog
          busy={false}
          dirtySessionCount={0}
          onCancel={vi.fn()}
          onDiscard={vi.fn()}
          t={createTranslator("en")}
        />
      );
    });

    expect(container.querySelector('[role="alertdialog"]')).toBeNull();
    expect(container.textContent).toBe("");
  });

  it("explains a retained-resource failure as a tab cleanup retry", () => {
    act(() => {
      root.render(
        <UnsavedChangesDialog
          busy={false}
          dirtySessionCount={0}
          error="preview cleanup failed"
          onCancel={vi.fn()}
          onDiscard={vi.fn()}
          t={createTranslator("en")}
        />
      );
    });

    expect(container.textContent).toContain(
      "ParaDev could not close this tab"
    );
    expect(container.textContent).toContain("retained resources");
    expect(button("Keep tab open")).toBe(document.activeElement);
    expect(button("Try closing tab again").disabled).toBe(false);
  });

  function button(label: string): HTMLButtonElement {
    const element = [...container.querySelectorAll("button")].find(
      (candidate) => candidate.textContent?.trim() === label
    );
    if (!(element instanceof HTMLButtonElement)) {
      throw new Error(`Missing button ${label}.`);
    }
    return element;
  }
});
