/** @vitest-environment jsdom */

import { act } from "react";
import { createRoot, type Root } from "react-dom/client";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import type { ModuleEntity } from "./model";
import { ModuleEntityThumbnail } from "./ModuleEntityThumbnail";
import { loadThumbnailUrl } from "./thumbnailLoader";

vi.mock("./thumbnailLoader", () => ({
  loadThumbnailUrl: vi.fn()
}));

const mounted: Array<{ container: HTMLDivElement; root: Root }> = [];
const loadThumbnailUrlMock = vi.mocked(loadThumbnailUrl);

beforeEach(() => {
  (globalThis as typeof globalThis & { IS_REACT_ACT_ENVIRONMENT: boolean }).IS_REACT_ACT_ENVIRONMENT = true;
  loadThumbnailUrlMock.mockReset();
  loadThumbnailUrlMock.mockResolvedValue("data:image/png;base64,dGh1bWI=");
});

afterEach(() => {
  for (const item of mounted.splice(0)) {
    act(() => item.root.unmount());
    item.container.remove();
  }
  vi.unstubAllGlobals();
});

describe("ModuleEntityThumbnail", () => {
  it("does not load an offscreen thumbnail and starts loading after intersection", async () => {
    const intersection = installIntersectionObserver();
    const container = renderThumbnail(thumbnailEntity("IDEA_OFFSCREEN"));

    await flushEffects();
    expect(intersection.observe).toHaveBeenCalledOnce();
    expect(loadThumbnailUrlMock).not.toHaveBeenCalled();
    expect(container.querySelector("img")).toBeNull();

    await intersection.emit(false);
    expect(loadThumbnailUrlMock).not.toHaveBeenCalled();

    await intersection.emit(true);
    expect(loadThumbnailUrlMock).toHaveBeenCalledOnce();
    expect(loadThumbnailUrlMock).toHaveBeenCalledWith(
      expect.objectContaining({
        projectRoot: "/workspace/projects/PIHC3",
        sourcePaths: expect.arrayContaining([
          "src/modules/idea/IDEA_OFFSCREEN/icon.png"
        ])
      })
    );
    expect(container.querySelector("img")?.getAttribute("src")).toBe("data:image/png;base64,dGh1bWI=");
    expect(intersection.disconnect).toHaveBeenCalled();
  });

  it("loads immediately when IntersectionObserver is unavailable", async () => {
    vi.stubGlobal("IntersectionObserver", undefined);
    renderThumbnail(thumbnailEntity("IDEA_FALLBACK"));

    await flushEffects();

    expect(loadThumbnailUrlMock).toHaveBeenCalledOnce();
  });
});

function renderThumbnail(entity: ModuleEntity): HTMLDivElement {
  const container = document.createElement("div");
  document.body.append(container);
  const root = createRoot(container);
  mounted.push({ container, root });
  act(() => {
    root.render(<ModuleEntityThumbnail entity={entity} projectRoot="/workspace/projects/PIHC3" />);
  });
  return container;
}

function thumbnailEntity(objectId: string): ModuleEntity {
  const relativeRoot = `src/modules/idea/${objectId}`;
  return {
    id: `ideas:${objectId}`,
    familyId: "ideas",
    family: "idea",
    objectId,
    title: objectId,
    subtitle: objectId,
    root: `/workspace/projects/PIHC3/${relativeRoot}`,
    relativeRoot,
    layout: "canonical",
    sourceCount: 1,
    sourceSlots: [
      {
        slot: "icon",
        name: "icon.png",
        path: `/workspace/projects/PIHC3/${relativeRoot}/icon.png`,
        relative_path: `${relativeRoot}/icon.png`,
        extension: "png",
        draftKey: "icon",
        editorKind: "image"
      }
    ],
    tags: [],
    draftState: "clean",
    drafts: { text: {} }
  };
}

function installIntersectionObserver() {
  let callback: IntersectionObserverCallback | null = null;
  let observer: IntersectionObserver | null = null;
  let target: Element | null = null;
  const observe = vi.fn((nextTarget: Element) => {
    target = nextTarget;
  });
  const disconnect = vi.fn();

  class TestIntersectionObserver implements IntersectionObserver {
    readonly root = null;
    readonly rootMargin: string;
    readonly scrollMargin = "0px";
    readonly thresholds = [0];

    constructor(nextCallback: IntersectionObserverCallback, options?: IntersectionObserverInit) {
      callback = nextCallback;
      this.rootMargin = options?.rootMargin ?? "0px";
      observer = this;
    }

    disconnect = disconnect;
    observe = observe;
    takeRecords = () => [];
    unobserve = vi.fn();
  }

  vi.stubGlobal("IntersectionObserver", TestIntersectionObserver);

  return {
    disconnect,
    observe,
    async emit(isIntersecting: boolean) {
      if (!callback || !observer || !target) {
        throw new Error("Thumbnail intersection observer is not ready.");
      }
      const activeCallback = callback;
      const activeObserver = observer;
      const observedTarget = target;
      const bounds = observedTarget.getBoundingClientRect();
      await act(async () => {
        activeCallback(
          [
            {
              boundingClientRect: bounds,
              intersectionRatio: isIntersecting ? 1 : 0,
              intersectionRect: isIntersecting ? bounds : emptyRect(),
              isIntersecting,
              rootBounds: null,
              target: observedTarget,
              time: performance.now()
            }
          ],
          activeObserver
        );
        await Promise.resolve();
      });
    }
  };
}

async function flushEffects(): Promise<void> {
  await act(async () => {
    await Promise.resolve();
  });
}

function emptyRect(): DOMRectReadOnly {
  return {
    bottom: 0,
    height: 0,
    left: 0,
    right: 0,
    top: 0,
    width: 0,
    x: 0,
    y: 0,
    toJSON: () => ({})
  };
}
