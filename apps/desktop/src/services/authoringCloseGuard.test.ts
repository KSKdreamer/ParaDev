/** @vitest-environment jsdom */

import { describe, expect, it, vi } from "vitest";
import { installAuthoringCloseGuards } from "./authoringCloseGuard";

describe("installAuthoringCloseGuards", () => {
  it("blocks unload only while authoring state is dirty or busy", () => {
    let state = { busy: false, dirty: false };
    let listener: ((event: BeforeUnloadEvent) => void) | undefined;
    const browserTarget = {
      addEventListener: vi.fn(
        (_type: "beforeunload", next: (event: BeforeUnloadEvent) => void) => {
          listener = next;
        }
      ),
      removeEventListener: vi.fn()
    };
    const dispose = installAuthoringCloseGuards({
      browserTarget,
      getState: () => state
    });

    const clean = closeEvent();
    listener?.(clean as unknown as BeforeUnloadEvent);
    expect(clean.preventDefault).not.toHaveBeenCalled();

    state = { busy: false, dirty: true };
    const dirty = closeEvent();
    listener?.(dirty as unknown as BeforeUnloadEvent);
    expect(dirty.preventDefault).toHaveBeenCalledTimes(1);

    state = { busy: true, dirty: false };
    const busy = closeEvent();
    listener?.(busy as unknown as BeforeUnloadEvent);
    expect(busy.preventDefault).toHaveBeenCalledTimes(1);

    dispose();
    expect(browserTarget.removeEventListener).toHaveBeenCalledWith(
      "beforeunload",
      listener
    );
  });
});

function closeEvent() {
  return {
    preventDefault: vi.fn(),
    returnValue: undefined as unknown
  };
}
