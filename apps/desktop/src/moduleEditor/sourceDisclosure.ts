import type { ModuleSourceSlot } from "./model";

export type ModuleEditableSourceGroups = {
  primary: readonly ModuleSourceSlot[];
  metadata: readonly ModuleSourceSlot[];
};

/**
 * Separate ordinary authored text from raw compiler metadata.
 *
 * Module identity and family are folder-derived, while the Info panel owns
 * common title and localization edits. Keeping `meta.yaml` last and explicit
 * preserves the raw escape hatch without presenting it as routine content.
 */
export function groupModuleEditableSources(
  sources: readonly ModuleSourceSlot[]
): ModuleEditableSourceGroups {
  const primary: ModuleSourceSlot[] = [];
  const metadata: ModuleSourceSlot[] = [];

  for (const source of sources) {
    if (source.editorKind !== "code" && source.editorKind !== "localization") {
      continue;
    }
    (source.slot === "meta" ? metadata : primary).push(source);
  }

  return { primary, metadata };
}
