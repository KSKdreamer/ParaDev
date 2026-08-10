import cursorIcon from "./assets/open-targets/cursor.png";
import cmdIcon from "./assets/open-targets/cmd.svg";
import explorerIcon from "./assets/open-targets/explorer.svg";
import finderIcon from "./assets/open-targets/finder.png";
import iterm2Icon from "./assets/open-targets/iterm2.png";
import powershellIcon from "./assets/open-targets/powershell.svg";
import sublimeTextIcon from "./assets/open-targets/sublime-text.png";
import terminalIcon from "./assets/open-targets/terminal.png";
import vscodeIcon from "./assets/open-targets/vscode.png";
import {
  PARADEV_DESKTOP_OPEN_PATH_DEFAULT_TARGETS,
  PARADEV_DESKTOP_OPEN_PATH_TARGETS,
  type DesktopOpenPathPlatform,
  type DesktopOpenPathTarget
} from "./generated/desktopContract";
import type { TranslationKey } from "./i18n";

export type OpenPathPlatform = DesktopOpenPathPlatform;
export type OpenPathTarget = DesktopOpenPathTarget;
export type OpenPathTargetIconKind = "image" | "mask";

export type OpenPathTargetDefinition = {
  iconKind: OpenPathTargetIconKind;
  iconSrc: string;
  id: OpenPathTarget;
  labelKey: TranslationKey;
  platforms: readonly OpenPathPlatform[];
};

const OPEN_PATH_TARGET_ICONS = {
  finder: { iconSrc: finderIcon, iconKind: "image" },
  explorer: { iconSrc: explorerIcon, iconKind: "mask" },
  cursor: { iconSrc: cursorIcon, iconKind: "image" },
  vscode: { iconSrc: vscodeIcon, iconKind: "image" },
  sublimeText: { iconSrc: sublimeTextIcon, iconKind: "image" },
  terminal: { iconSrc: terminalIcon, iconKind: "image" },
  iterm2: { iconSrc: iterm2Icon, iconKind: "image" },
  cmd: { iconSrc: cmdIcon, iconKind: "mask" },
  powershell: { iconSrc: powershellIcon, iconKind: "mask" }
} as const satisfies Record<OpenPathTarget, { iconKind: OpenPathTargetIconKind; iconSrc: string }>;

export const OPEN_PATH_TARGETS: readonly OpenPathTargetDefinition[] = PARADEV_DESKTOP_OPEN_PATH_TARGETS.map((target) => ({
  ...target,
  ...OPEN_PATH_TARGET_ICONS[target.id],
  labelKey: target.labelKey as TranslationKey
}));

export function availableOpenPathTargets(platform: OpenPathPlatform = currentOpenPathPlatform()): OpenPathTargetDefinition[] {
  return OPEN_PATH_TARGETS.filter((target) => target.platforms.includes(platform));
}

export function currentOpenPathPlatform(): OpenPathPlatform {
  if (typeof navigator === "undefined") {
    return "unknown";
  }
  const userAgentData = "userAgentData" in navigator ? (navigator as Navigator & { userAgentData?: { platform?: string } }).userAgentData : undefined;
  return openPathPlatformFromLabel(userAgentData?.platform ?? navigator.platform ?? navigator.userAgent);
}

export function defaultOpenPathTarget(platform: OpenPathPlatform = currentOpenPathPlatform()): OpenPathTarget {
  return PARADEV_DESKTOP_OPEN_PATH_DEFAULT_TARGETS[platform];
}

export function isOpenPathTarget(value: unknown): value is OpenPathTarget {
  return typeof value === "string" && OPEN_PATH_TARGETS.some((target) => target.id === value);
}

export function normalizeOpenPathTarget(value: string | null | unknown, platform: OpenPathPlatform = currentOpenPathPlatform()): OpenPathTarget {
  if (!isOpenPathTarget(value)) {
    return defaultOpenPathTarget(platform);
  }
  return availableOpenPathTargets(platform).some((target) => target.id === value) ? value : defaultOpenPathTarget(platform);
}

function openPathPlatformFromLabel(label: string): OpenPathPlatform {
  const normalized = label.toLowerCase();
  if (normalized.includes("mac")) {
    return "macos";
  }
  if (normalized.includes("win")) {
    return "windows";
  }
  if (normalized.includes("linux")) {
    return "linux";
  }
  return "unknown";
}
