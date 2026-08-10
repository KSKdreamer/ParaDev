/** @vitest-environment jsdom */

import { act } from "react";
import { createRoot, type Root } from "react-dom/client";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { createTranslator } from "../i18n";
import type { FeatureModule, WorkspaceTab } from "../types";
import { Workspace } from "./Workspace";

const mocks = vi.hoisted(() => ({
  editorMounts: [] as string[],
  editorUnmounts: [] as string[],
  openProjectPath: vi.fn()
}));

vi.mock("../services/paradev", async (loadOriginal) => {
  const original =
    await loadOriginal<typeof import("../services/paradev")>();
  return {
    ...original,
    openProjectPath: mocks.openProjectPath
  };
});

vi.mock("../moduleEditor/ModuleEditor", async () => {
  const { useEffect, useRef } = await import("react");
  return {
    ModuleEditor: ({
      familyId,
      onBatchRecoveryPathsChange,
      projectRoot,
      surface
    }: {
      familyId: string;
      onBatchRecoveryPathsChange: (paths: string[]) => void;
      projectRoot: string;
      surface: "diagram" | "module";
    }) => {
      const identity = useRef(
        `${projectRoot}::${familyId}::${surface}`
      ).current;
      useEffect(() => {
        mocks.editorMounts.push(identity);
        return () => {
          mocks.editorUnmounts.push(identity);
        };
      }, [identity]);
      return (
        <button
          onClick={() =>
            onBatchRecoveryPathsChange([
              "/workspace/PIHC3/src/.paradev/module-transactions/txn-123"
            ])
          }
          type="button"
        >
          Simulate retained recovery data
        </button>
      );
    }
  };
});

const mounted: Array<{ container: HTMLDivElement; root: Root }> = [];
const activeFeature: FeatureModule = {
  id: "countries",
  titleKey: "modules.countries.title",
  status: "ready"
};

beforeEach(() => {
  (
    globalThis as typeof globalThis & { IS_REACT_ACT_ENVIRONMENT: boolean }
  ).IS_REACT_ACT_ENVIRONMENT = true;
  mocks.editorMounts.length = 0;
  mocks.editorUnmounts.length = 0;
  mocks.openProjectPath.mockReset();
});

afterEach(() => {
  for (const item of mounted.splice(0)) {
    act(() => item.root.unmount());
    item.container.remove();
  }
});

describe("Workspace module editor identity", () => {
  it("remounts the same family when its canonical project root changes", async () => {
    const moduleTab: WorkspaceTab = {
      id: "ideas",
      kind: "module",
      title: "Ideas"
    };
    const container = document.createElement("div");
    document.body.append(container);
    const root = createRoot(container);
    mounted.push({ container, root });

    await renderWorkspace(
      root,
      moduleTab,
      [moduleTab],
      "/workspace/checkouts/PIHC3-a"
    );
    await renderWorkspace(
      root,
      moduleTab,
      [moduleTab],
      "/workspace/checkouts/PIHC3-b"
    );
    await renderWorkspace(
      root,
      moduleTab,
      [moduleTab],
      "/workspace/checkouts/PIHC3-b"
    );

    expect(mocks.editorMounts).toEqual([
      "/workspace/checkouts/PIHC3-a::ideas::module",
      "/workspace/checkouts/PIHC3-b::ideas::module"
    ]);
    expect(mocks.editorUnmounts).toEqual([
      "/workspace/checkouts/PIHC3-a::ideas::module"
    ]);
  });
});

describe("Workspace batch recovery notice", () => {
  it("survives a family surface change and disappears only after explicit dismissal", async () => {
    const moduleTab: WorkspaceTab = {
      id: "ideas",
      kind: "module",
      title: "Ideas"
    };
    const surfaceTab: WorkspaceTab = {
      id: "surface-contracts",
      kind: "surface",
      title: "Surface contracts"
    };
    const container = document.createElement("div");
    document.body.append(container);
    const root = createRoot(container);
    mounted.push({ container, root });

    await renderWorkspace(root, moduleTab, [moduleTab, surfaceTab]);
    click(button(container, "Simulate retained recovery data"));

    const recoveryPath =
      "/workspace/PIHC3/src/.paradev/module-transactions/txn-123";
    expect(container.textContent).toContain(recoveryPath);
    await clickAsync(button(container, "Open recovery folder"));
    expect(mocks.openProjectPath).toHaveBeenCalledWith(recoveryPath, "finder");

    await renderWorkspace(root, surfaceTab, [moduleTab, surfaceTab]);
    expect(container.textContent).toContain(recoveryPath);

    click(button(container, "Dismiss recovery notice"));
    expect(container.textContent).not.toContain(recoveryPath);
  });
});

function renderWorkspace(
  root: Root,
  activeWorkspaceTab: WorkspaceTab,
  openTabs: WorkspaceTab[],
  projectRoot = "/workspace/PIHC3"
): Promise<void> {
  const props = {
    activeFeature,
    activeProject: {
      id: "PIHC3",
      projectId: "PIHC3",
      name: "PIHC3",
      path: projectRoot
    },
    activeTab: activeWorkspaceTab.id,
    activeWorkspaceTab,
    aiChatDefaultRole: "chat",
    aiChatProfiles: [],
    browser: null,
    inspectorOpen: false,
    locale: "en",
    onCloseTab: () => undefined,
    onProjectRefresh: async () => undefined,
    onResetAiChatProfile: () => undefined,
    onSaveAiChatProfile: () => undefined,
    onSplitToggle: () => undefined,
    onTabPin: () => undefined,
    onTabSelect: () => undefined,
    openTarget: "finder",
    openTabs,
    secondaryTab: "",
    secondaryWorkspaceTab: null,
    setSecondaryTab: () => undefined,
    splitView: false,
    surfaceRows: [],
    templates: null,
    t: createTranslator("en"),
    theme: "light"
  } as unknown as Parameters<typeof Workspace>[0];
  return act(async () => {
    root.render(<Workspace {...props} />);
    await vi.dynamicImportSettled();
  });
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
