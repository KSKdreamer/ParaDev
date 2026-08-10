import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";
import { createTranslator } from "../i18n";
import type { SurfaceRow } from "../types";
import { StatusBar } from "./StatusBar";

const surfaceRows: SurfaceRow[] = [
  { id: "sdk", path: "src/paradev/sdk", runtime: "python", status: "ready", titleKey: "surface.sdk.title" },
  { id: "frontend", path: "apps/desktop/src", runtime: "react-vite", status: "ready", titleKey: "surface.frontend.title" },
  { id: "mcp", path: "src/paradev/surfaces/mcp.py", runtime: "heavenbase-mcp", status: "scaffold", titleKey: "surface.mcp.title" }
];

describe("StatusBar", () => {
  it("renders shell status text through the Chinese locale", () => {
    const markup = renderToStaticMarkup(<StatusBar surfaceRows={surfaceRows} t={createTranslator("zh")} />);

    expect(markup).toContain("SDK 2 个就绪");
    expect(markup).toContain("1 个脚手架接口");
    expect(markup).toContain("REST 离线");
    expect(markup).toContain("MCP 已规划");
    expect(markup).toContain("macOS 优先");
    expect(markup).not.toContain("REST offline");
    expect(markup).not.toContain("MCP planned");
    expect(markup).not.toContain("macOS priority");
  });
});
