/** @vitest-environment jsdom */

import { act } from "react";
import { createRoot, type Root } from "react-dom/client";
import {
  afterEach,
  beforeEach,
  describe,
  expect,
  it,
  vi
} from "vitest";
import { APP_SETTINGS_STORAGE_KEY } from "../appSettingsStorage";
import {
  RendererErrorBoundary,
  rendererRecoveryPreferences
} from "./RendererErrorBoundary";

const mounted: Array<{ container: HTMLDivElement; root: Root }> = [];

beforeEach(() => {
  (
    globalThis as typeof globalThis & {
      IS_REACT_ACT_ENVIRONMENT: boolean;
    }
  ).IS_REACT_ACT_ENVIRONMENT = true;
  window.localStorage.clear();
  document.documentElement.lang = "zh-CN";
});

afterEach(() => {
  for (const item of mounted.splice(0)) {
    act(() => item.root.unmount());
    item.container.remove();
  }
  vi.restoreAllMocks();
});

describe("RendererErrorBoundary", () => {
  it("replaces a renderer crash with localized recovery and retries cleanly", () => {
    window.localStorage.setItem(
      APP_SETTINGS_STORAGE_KEY,
      JSON.stringify({ locale: "zh", theme: "dark" })
    );
    const consoleError = vi.spyOn(console, "error").mockImplementation(() => undefined);
    const reloadApplication = vi.fn();
    let shouldFail = true;
    const BrokenView = () => {
      if (shouldFail) {
        throw new Error(
          "private /Users/example/PIHC3 token=never-report-this"
        );
      }
      return <p>workspace recovered</p>;
    };
    const { container, root } = mount(
      <RendererErrorBoundary reloadApplication={reloadApplication}>
        <BrokenView />
      </RendererErrorBoundary>
    );

    expect(container.textContent).toContain("ParaDev 需要恢复");
    expect(container.textContent).toContain("没有修改你的项目文件");
    expect(container.textContent).not.toContain("never-report-this");
    expect(container.querySelector(".renderer-recovery.theme-dark")).not.toBeNull();

    click(button(container, "重新加载 ParaDev"));
    expect(reloadApplication).toHaveBeenCalledOnce();

    shouldFail = false;
    click(button(container, "重试界面"));
    expect(container.textContent).toContain("workspace recovered");

    const reports = rendererReports(consoleError.mock.calls);
    expect(reports).toHaveLength(1);
    expect(reports[0]).toMatchObject({
      schema: "paradev.desktop.renderer-failure.v1",
      kind: "react-render",
      errorName: "Error"
    });
    expect(JSON.stringify(reports)).not.toContain("PIHC3");
    expect(JSON.stringify(reports)).not.toContain("never-report-this");
    expect(root).toBeDefined();
  });

  it("reports window errors and rejected promises without raw details", () => {
    const consoleError = vi.spyOn(console, "error").mockImplementation(() => undefined);
    mount(
      <RendererErrorBoundary>
        <p>healthy workspace</p>
      </RendererErrorBoundary>
    );

    act(() => {
      window.dispatchEvent(
        new ErrorEvent("error", {
          error: new TypeError("secret project path /private/tmp/PIHC3"),
          message: "secret project path /private/tmp/PIHC3",
          filename: "/private/tmp/PIHC3/source.ts"
        })
      );
      const rejection = new Event("unhandledrejection");
      Object.defineProperty(rejection, "reason", {
        value: new Error("api-key=private")
      });
      window.dispatchEvent(rejection);
    });

    const reports = rendererReports(consoleError.mock.calls);
    expect(reports).toEqual([
      {
        schema: "paradev.desktop.renderer-failure.v1",
        kind: "window-error",
        errorName: "TypeError",
        components: []
      },
      {
        schema: "paradev.desktop.renderer-failure.v1",
        kind: "unhandled-rejection",
        errorName: "Error",
        components: []
      }
    ]);
    expect(JSON.stringify(reports)).not.toContain("PIHC3");
    expect(JSON.stringify(reports)).not.toContain("api-key");
  });

  it("falls back safely when stored recovery preferences are malformed", () => {
    const preferences = rendererRecoveryPreferences(
      {
        getItem: () => "{not-json"
      },
      "zh-CN"
    );

    expect(preferences).toEqual({
      locale: "zh",
      theme: "anthropic"
    });
  });
});

function mount(children: React.ReactNode): {
  container: HTMLDivElement;
  root: Root;
} {
  const container = document.createElement("div");
  document.body.append(container);
  const root = createRoot(container);
  mounted.push({ container, root });
  act(() => root.render(children));
  return { container, root };
}

function button(container: HTMLElement, label: string): HTMLButtonElement {
  const match = [...container.querySelectorAll("button")].find(
    (candidate) => candidate.textContent?.trim() === label
  );
  if (!(match instanceof HTMLButtonElement)) {
    throw new Error(`Missing button: ${label}`);
  }
  return match;
}

function click(target: HTMLButtonElement): void {
  act(() => target.click());
}

function rendererReports(
  calls: unknown[][]
): Array<Record<string, unknown>> {
  return calls.flatMap((call) =>
    call[0] === "ParaDev renderer failure captured." &&
    call[1] &&
    typeof call[1] === "object"
      ? [call[1] as Record<string, unknown>]
      : []
  );
}
