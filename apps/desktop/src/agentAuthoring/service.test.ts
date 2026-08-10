import { describe, expect, it } from "vitest";
import {
  fallbackAgentAuthoringInfo,
  mcpCommandText
} from "./service";

describe("agent authoring runtime service", () => {
  it("keeps the plain-browser fallback honest about unavailable bundled tools", () => {
    expect(fallbackAgentAuthoringInfo(" /workspace/PIHC3 ")).toEqual({
      schema: "paradev.desktop.agent-authoring.v1",
      projectRoot: "/workspace/PIHC3",
      mcp: {
        available: false,
        command: "paradev",
        args: ["mcp", "serve"],
        cwd: null
      },
      skill: {
        available: false,
        id: "paradev-authoring",
        invocation: "$paradev-authoring",
        path: ".agents/skills/paradev-authoring/SKILL.md"
      }
    });
  });

  it("renders the exact resolved backend command without losing spaced paths", () => {
    expect(
      mcpCommandText({
        available: true,
        command: "/Applications/ParaDev Preview.app/Contents/MacOS/paradev-backend",
        args: ["mcp", "serve"]
      })
    ).toBe(
      '"/Applications/ParaDev Preview.app/Contents/MacOS/paradev-backend" mcp serve'
    );
    expect(
      mcpCommandText({
        available: true,
        command: "uv",
        args: ["run", "python", "-m", "paradev.desktop.backend", "mcp", "serve"]
      })
    ).toBe("uv run python -m paradev.desktop.backend mcp serve");
  });
});
