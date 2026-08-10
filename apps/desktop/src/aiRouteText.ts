import type { Translator } from "./i18n";

export type AiRouteLabelInput = {
  gateway: string;
  model: string;
  preset?: string;
  provider: string;
  t: Translator;
};

const AI_ROUTE_PART_LABELS: Record<string, string> = {
  "deepseek": "DeepSeek",
  "deepseek-reasoner": "DeepSeek Reasoner",
  "deepseek-v4-flash": "DeepSeek v4 Flash",
  "ds-flash": "DeepSeek Flash",
  "ds-pro": "DeepSeek Pro",
  "openai": "OpenAI",
  "openrouter": "OpenRouter",
  "sonnet": "Claude Sonnet"
};

export function aiRouteLabel({ gateway, model, provider, t }: AiRouteLabelInput): string {
  return t("chat.route", {
    gateway: aiRoutePartLabel(gateway, t),
    model: aiRoutePartLabel(model, t),
    provider: aiRoutePartLabel(provider, t)
  });
}

export function aiRouteLabelWithPreset({ gateway, model, preset, provider, t }: AiRouteLabelInput): string {
  if (preset === undefined) {
    return aiRouteLabel({ gateway, model, provider, t });
  }
  return t("chat.routeWithPreset", {
    gateway: aiRoutePartLabel(gateway, t),
    model: aiRoutePartLabel(model, t),
    preset: aiPresetLabel(preset, t),
    provider: aiRoutePartLabel(provider, t)
  });
}

export function aiRoutePartLabel(value: string, t: Translator): string {
  const clean = value.trim();
  if (!clean) {
    return t("chat.route.default");
  }
  return AI_ROUTE_PART_LABELS[clean.toLowerCase()] ?? humanizeRouteId(clean);
}

function humanizeRouteId(value: string): string {
  return value
    .split(/[-_\s]+/)
    .filter(Boolean)
    .map((part) => part.slice(0, 1).toUpperCase() + part.slice(1))
    .join(" ");
}

function aiPresetLabel(value: string, t: Translator): string {
  const clean = value.trim();
  if (!clean) {
    return t("chat.route.default");
  }
  if (clean === "system") {
    return t("config.models.presets.system.label");
  }
  if (clean === "chat") {
    return t("config.models.presets.chat.label");
  }
  if (clean === "reason") {
    return t("config.models.presets.reason.label");
  }
  if (clean === "coder") {
    return t("config.models.presets.coder.label");
  }
  return humanizeRouteId(clean);
}
