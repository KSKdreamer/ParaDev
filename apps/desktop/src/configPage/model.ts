import { DESKTOP_CONFIG_KEYS, desktopConfigChoices, desktopConfigDefault, type DesktopConfigKey } from "../desktopConfig";
import type { DesktopDependencyStatus, HeavenBaseLlmTestPayload } from "../services/paradev";
import type { TranslationKey } from "../i18n";

export type ConfigDependencyStatus = DesktopDependencyStatus;
export type ConfigLlmStatus = HeavenBaseLlmTestPayload;

export type ConfigLlmSettings = {
  baseUrl: string;
  gateway: string;
  keyEnv: string;
  model: string;
  preset: string;
  provider: string;
};

export type ConfigChatSettings = {
  defaultRole: string;
};

export type ConfigPersistenceState = "persisted" | "saving" | "error";

export type ConfigPersistenceStatus = {
  detail?: string;
  labelKey: TranslationKey;
  labelParams?: Record<string, string | number>;
  state: ConfigPersistenceState;
};

export type ConfigCliOutput = "yaml" | "json";
export type ConfigHoi4LaunchMode = "steam" | "local";

export type ConfigModuleDefault = {
  configKey?: DesktopConfigKey;
  id: string;
  labelKey: TranslationKey;
  detailKey: TranslationKey;
  unit: string;
  value: number;
};

export type ConfigPageSettings = {
  build: {
    parallelism: number;
    strictMetadata: boolean;
  };
  cli: {
    output: ConfigCliOutput;
  };
  project: {
    name: string;
  };
  hoi4: {
    gameRoot: string;
    launchMode: ConfigHoi4LaunchMode;
  };
  chat: ConfigChatSettings;
  llm: ConfigLlmSettings;
  moduleDefaults: ConfigModuleDefault[];
};

export const CONFIG_DEPENDENCY_IDS = ["imagemagick"] as const;

export const CONFIG_CLI_OUTPUT_VALUES = desktopConfigChoices(DESKTOP_CONFIG_KEYS.cliOutput) as readonly ConfigCliOutput[];
export const CONFIG_HOI4_LAUNCH_MODE_VALUES = desktopConfigChoices(DESKTOP_CONFIG_KEYS.hoi4LaunchMode) as readonly ConfigHoi4LaunchMode[];
export const CONFIG_AI_PRESET_VALUES = desktopConfigChoices(DESKTOP_CONFIG_KEYS.aiPreset);

const LLM_PRESET_DISPLAY = {
  system: { model: "ds-flash", labelKey: "config.models.presets.system.label", detailKey: "config.models.presets.system.detail" },
  chat: { model: "ds-flash", labelKey: "config.models.presets.chat.label", detailKey: "config.models.presets.chat.detail" },
  reason: { model: "ds-pro", labelKey: "config.models.presets.reason.label", detailKey: "config.models.presets.reason.detail" },
  coder: { model: "sonnet", labelKey: "config.models.presets.coder.label", detailKey: "config.models.presets.coder.detail" }
} as const satisfies Record<string, { model: string; labelKey: TranslationKey; detailKey: TranslationKey }>;

export const LLM_PRESET_ROWS = CONFIG_AI_PRESET_VALUES.map((preset) => {
  const display = LLM_PRESET_DISPLAY[preset as keyof typeof LLM_PRESET_DISPLAY];
  return {
    preset,
    ...(display ?? {
      model: preset,
      labelKey: "config.models.presets.chat.label",
      detailKey: "config.models.presets.chat.detail"
    })
  };
});

function desktopStringDefault(key: DesktopConfigKey): string {
  const value = desktopConfigDefault(key);
  return typeof value === "string" ? value : "";
}

function desktopNumberDefault(key: DesktopConfigKey): number {
  const value = desktopConfigDefault(key);
  return typeof value === "number" && Number.isFinite(value) ? value : 1;
}

function desktopBooleanDefault(key: DesktopConfigKey): boolean {
  const value: unknown = desktopConfigDefault(key);
  return typeof value === "boolean" ? value : false;
}

function desktopChoiceDefault<T extends string>(key: DesktopConfigKey, choices: readonly T[]): T {
  const value = desktopConfigDefault(key);
  return typeof value === "string" && choices.includes(value as T) ? (value as T) : choices[0];
}

export function defaultConfigPageSettings(): ConfigPageSettings {
  return {
    build: {
      parallelism: desktopNumberDefault(DESKTOP_CONFIG_KEYS.buildParallelism),
      strictMetadata: desktopBooleanDefault(DESKTOP_CONFIG_KEYS.buildStrictMetadata)
    },
    cli: {
      output: desktopChoiceDefault(DESKTOP_CONFIG_KEYS.cliOutput, CONFIG_CLI_OUTPUT_VALUES)
    },
    project: {
      name: desktopStringDefault(DESKTOP_CONFIG_KEYS.projectName)
    },
    hoi4: {
      gameRoot: desktopStringDefault(DESKTOP_CONFIG_KEYS.hoi4GameRoot),
      launchMode: desktopChoiceDefault(DESKTOP_CONFIG_KEYS.hoi4LaunchMode, CONFIG_HOI4_LAUNCH_MODE_VALUES)
    },
    chat: {
      defaultRole: desktopStringDefault(DESKTOP_CONFIG_KEYS.aiChatDefaultRole)
    },
    llm: {
      baseUrl: desktopStringDefault(DESKTOP_CONFIG_KEYS.aiBaseUrl),
      gateway: desktopStringDefault(DESKTOP_CONFIG_KEYS.aiGateway),
      keyEnv: desktopStringDefault(DESKTOP_CONFIG_KEYS.aiKeyEnv),
      model: desktopStringDefault(DESKTOP_CONFIG_KEYS.aiModel),
      preset: desktopStringDefault(DESKTOP_CONFIG_KEYS.aiPreset),
      provider: desktopStringDefault(DESKTOP_CONFIG_KEYS.aiProvider)
    },
    moduleDefaults: [
      {
        id: "focus-node",
        labelKey: "config.moduleDefaults.focusNode.label",
        detailKey: "config.moduleDefaults.focusNode.detail",
        unit: "px",
        value: 96
      },
      {
        id: "technology-node",
        labelKey: "config.moduleDefaults.technologyNode.label",
        detailKey: "config.moduleDefaults.technologyNode.detail",
        unit: "px",
        value: 48
      },
      {
        id: "portrait",
        labelKey: "config.moduleDefaults.portrait.label",
        detailKey: "config.moduleDefaults.portrait.detail",
        unit: "px",
        value: 156
      },
      {
        id: "flag",
        labelKey: "config.moduleDefaults.flag.label",
        detailKey: "config.moduleDefaults.flag.detail",
        unit: "px",
        value: 82
      },
      {
        configKey: DESKTOP_CONFIG_KEYS.thumbnailCacheMaxKb,
        id: "thumbnail-cache",
        labelKey: "config.moduleDefaults.thumbnailCache.label",
        detailKey: "config.moduleDefaults.thumbnailCache.detail",
        unit: "KB",
        value: desktopNumberDefault(DESKTOP_CONFIG_KEYS.thumbnailCacheMaxKb)
      }
    ]
  };
}

export function defaultConfigLlmStatus(settings: ConfigLlmSettings = defaultConfigPageSettings().llm): ConfigLlmStatus {
  return {
    baseUrl: settings.baseUrl,
    gateway: settings.gateway,
    keySource: settings.keyEnv,
    model: settings.model,
    preset: settings.preset,
    provider: settings.provider,
    status: "unknown",
    testDetail: "",
    testedAt: ""
  };
}

export function defaultConfigPersistenceStatus(): ConfigPersistenceStatus {
  return {
    labelKey: "config.page.persisted",
    state: "persisted"
  };
}

export function normalizeConfigPageSettings(value: unknown, fallback: ConfigPageSettings = defaultConfigPageSettings()): ConfigPageSettings {
  const record = isRecord(value) ? value : {};
  const build = isRecord(record.build) ? record.build : {};
  const cli = isRecord(record.cli) ? record.cli : {};
  const project = isRecord(record.project) ? record.project : {};
  const hoi4 = isRecord(record.hoi4) ? record.hoi4 : {};
  const chat = isRecord(record.chat) ? record.chat : {};
  const llm = isRecord(record.llm) ? record.llm : {};
  return {
    build: {
      parallelism: positiveInteger(build.parallelism, fallback.build.parallelism),
      strictMetadata: booleanValue(build.strictMetadata, fallback.build.strictMetadata)
    },
    cli: {
      output: cliOutput(cli.output, fallback.cli.output)
    },
    project: {
      name: cleanText(project.name, fallback.project.name)
    },
    hoi4: {
      gameRoot: optionalText(hoi4.gameRoot, fallback.hoi4.gameRoot),
      launchMode: hoi4LaunchMode(hoi4.launchMode, fallback.hoi4.launchMode)
    },
    chat: {
      defaultRole: aiChatRole(chat.defaultRole, fallback.chat.defaultRole)
    },
    llm: {
      baseUrl: optionalText(llm.baseUrl, fallback.llm.baseUrl),
      gateway: cleanText(llm.gateway, fallback.llm.gateway),
      keyEnv: cleanText(llm.keyEnv, fallback.llm.keyEnv),
      model: cleanText(llm.model, fallback.llm.model),
      preset: cleanText(llm.preset, fallback.llm.preset),
      provider: cleanText(llm.provider, fallback.llm.provider)
    },
    moduleDefaults: normalizeModuleDefaults(record.moduleDefaults, fallback.moduleDefaults)
  };
}

export function dependencyErrorStatus(id: string, message: string): ConfigDependencyStatus {
  return {
    schema: "paradev.desktop.dependency.v1",
    id,
    installed: false,
    installCommand: [],
    installSupported: false,
    label: id === "imagemagick" ? "ImageMagick" : id,
    status: "error",
    detail: message
  };
}

export function llmErrorStatus(settings: ConfigLlmSettings, message: string): ConfigLlmStatus {
  return {
    baseUrl: settings.baseUrl,
    gateway: settings.gateway,
    keySource: settings.keyEnv,
    model: settings.model,
    preset: settings.preset,
    provider: settings.provider,
    status: "error",
    testDetail: message,
    testedAt: new Date().toISOString()
  };
}

function normalizeModuleDefaults(value: unknown, fallback: ConfigModuleDefault[]): ConfigModuleDefault[] {
  if (!Array.isArray(value)) {
    return fallback;
  }
  const fallbackById = new Map(fallback.map((row) => [row.id, row]));
  const rowsById = new Map(
    value.flatMap((row) => {
      if (!isRecord(row)) {
        return [];
      }
      const id = cleanText(row.id, "");
      const base = fallbackById.get(id);
      if (!base) {
        return [];
      }
      const value = typeof row.value === "number" && Number.isFinite(row.value) && row.value > 0 ? Math.round(row.value) : base.value;
      return [[id, { ...base, value }] as const];
    })
  );
  if (rowsById.size === 0) {
    return fallback;
  }
  return fallback.map((row) => rowsById.get(row.id) ?? row);
}

function cleanText(value: unknown, fallback: string): string {
  return typeof value === "string" && value.trim().length > 0 ? value.trim() : fallback;
}

function optionalText(value: unknown, fallback: string): string {
  return typeof value === "string" ? value.trim() : fallback;
}

function positiveInteger(value: unknown, fallback: number): number {
  if (typeof value !== "number" || !Number.isFinite(value) || value < 1) {
    return fallback;
  }
  return Math.round(value);
}

function booleanValue(value: unknown, fallback: boolean): boolean {
  return typeof value === "boolean" ? value : fallback;
}

function cliOutput(value: unknown, fallback: ConfigCliOutput): ConfigCliOutput {
  return typeof value === "string" && CONFIG_CLI_OUTPUT_VALUES.includes(value as ConfigCliOutput) ? (value as ConfigCliOutput) : fallback;
}

function hoi4LaunchMode(value: unknown, fallback: ConfigHoi4LaunchMode): ConfigHoi4LaunchMode {
  return typeof value === "string" && CONFIG_HOI4_LAUNCH_MODE_VALUES.includes(value as ConfigHoi4LaunchMode) ? (value as ConfigHoi4LaunchMode) : fallback;
}

function aiChatRole(value: unknown, fallback: string): string {
  return cleanText(value, fallback);
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}
