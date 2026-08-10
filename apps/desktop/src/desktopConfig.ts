import { type DesktopConfigKey, type DesktopConfigRow, PARADEV_DESKTOP_CONFIG_DEFAULTS, PARADEV_DESKTOP_CONFIG_KEYS, PARADEV_DESKTOP_CONFIG_ROWS } from "./generated/desktopContract";

export { PARADEV_DESKTOP_CONFIG_DEFAULTS, PARADEV_DESKTOP_CONFIG_KEYS, PARADEV_DESKTOP_CONFIG_ROWS };
export type { DesktopConfigKey, DesktopConfigRow };

export const DESKTOP_CONFIG_KEYS = {
  aiBaseUrl: "paradev.ai.base_url",
  aiGateway: "paradev.ai.gateway",
  aiKeyEnv: "paradev.ai.key_env",
  aiModel: "paradev.ai.model",
  aiPreset: "paradev.ai.preset",
  aiProvider: "paradev.ai.provider",
  aiChatDefaultRole: "paradev.ai.chat.default_role",
  buildParallelism: "paradev.build.parallelism",
  buildStrictMetadata: "paradev.build.strict_metadata",
  cliOutput: "paradev.cli.output",
  hoi4GameRoot: "paradev.hoi4.game_root",
  hoi4LaunchMode: "paradev.hoi4.launch_mode",
  projectName: "paradev.project.name",
  thumbnailCacheMaxKb: "paradev.desktop.thumbnail_cache.max_kb"
} as const satisfies Record<string, DesktopConfigKey>;

export const DESKTOP_CONFIG_KEY_VALUES = Object.values(DESKTOP_CONFIG_KEYS) as DesktopConfigKey[];

export function desktopConfigDefault(key: DesktopConfigKey): DesktopConfigRow["default"] {
  return PARADEV_DESKTOP_CONFIG_DEFAULTS[key];
}

export function desktopConfigChoices(key: DesktopConfigKey): readonly string[] {
  const row = PARADEV_DESKTOP_CONFIG_ROWS.find((item) => item.key === key);
  return row && "choices" in row ? row.choices : [];
}

export function desktopConfigMinimum(key: DesktopConfigKey, fallback = 1): number {
  const row = PARADEV_DESKTOP_CONFIG_ROWS.find((item) => item.key === key);
  const minimum = row && "minimum" in row ? row.minimum : fallback;
  return typeof minimum === "number" && Number.isFinite(minimum) ? minimum : fallback;
}
