import type { TranslationKey } from "./i18n";

export const moduleNavigationGroupOrder = [
  "modules.group.country",
  "modules.group.military",
  "modules.group.world",
  "modules.group.events",
  "modules.group.shared",
  "modules.group.other"
] as const satisfies readonly TranslationKey[];

export type ModuleNavigationGroupKey = (typeof moduleNavigationGroupOrder)[number];

const moduleNavigationGroupByCapability = {
  country: "modules.group.country",
  military: "modules.group.military",
  world: "modules.group.world",
  events: "modules.group.events",
  shared: "modules.group.shared",
  other: "modules.group.other"
} as const satisfies Readonly<Record<string, ModuleNavigationGroupKey>>;

export function moduleNavigationGroupKey(
  group: string | null | undefined
): ModuleNavigationGroupKey {
  return group && group in moduleNavigationGroupByCapability
    ? moduleNavigationGroupByCapability[
        group as keyof typeof moduleNavigationGroupByCapability
      ]
    : "modules.group.other";
}
