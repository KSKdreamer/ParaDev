export type AgentAuthoringMcpRuntime = {
  available: boolean;
  command: string;
  args: string[];
  cwd?: string | null;
};

export type AgentAuthoringSkillRuntime = {
  available: boolean;
  id: string;
  invocation: string;
  path: string;
};

export type AgentAuthoringInfoPayload = {
  schema: "paradev.desktop.agent-authoring.v1";
  projectRoot: string;
  mcp: AgentAuthoringMcpRuntime;
  skill: AgentAuthoringSkillRuntime;
};

export async function loadAgentAuthoringInfo(
  projectRoot: string
): Promise<AgentAuthoringInfoPayload> {
  return fallbackAgentAuthoringInfo(projectRoot);
}

export function fallbackAgentAuthoringInfo(
  projectRoot: string
): AgentAuthoringInfoPayload {
  return {
    schema: "paradev.desktop.agent-authoring.v1",
    projectRoot: projectRoot.trim(),
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
  };
}

export function mcpCommandText(runtime: AgentAuthoringMcpRuntime): string {
  return [runtime.command, ...runtime.args].map(commandToken).join(" ");
}

function commandToken(value: string): string {
  return /^[A-Za-z0-9_./:\\-]+$/.test(value) ? value : JSON.stringify(value);
}
