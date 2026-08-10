import type { Translator } from "../i18n";

export type ModuleFamilySummaryInput = {
  filtered: boolean;
  loadedCount: number;
  sourceCount: number;
  totalCount: number;
  visibleCount: number;
};

/** Describes visible, loaded, and family-wide counts without conflating them. */
export function moduleFamilySummary(
  {
    filtered,
    loadedCount,
    sourceCount,
    totalCount,
    visibleCount,
  }: ModuleFamilySummaryInput,
  t: Translator,
): string {
  const visible = normalizeCount(visibleCount);
  const loaded = Math.max(visible, normalizeCount(loadedCount));
  const total = Math.max(loaded, normalizeCount(totalCount));
  const sources = normalizeCount(sourceCount);

  if (filtered && loaded < total) {
    return t("workspace.module.summary.filteredPaged", {
      loaded: String(loaded),
      sources: String(sources),
      total: String(total),
      visible: String(visible),
    });
  }
  if (filtered) {
    return t("workspace.module.summary.filtered", {
      sources: String(sources),
      total: String(total),
      visible: String(visible),
    });
  }
  if (loaded < total) {
    return t("workspace.module.summary.paged", {
      loaded: String(loaded),
      sources: String(sources),
      total: String(total),
    });
  }
  return t("workspace.module.summary", {
    count: String(total),
    sources: String(sources),
  });
}

function normalizeCount(value: number): number {
  return Number.isFinite(value) ? Math.max(0, Math.trunc(value)) : 0;
}
