import { describe, expect, it } from "vitest";
import type { ModuleSourceSlot } from "./model";
import { groupModuleEditableSources } from "./sourceDisclosure";

function source(
  slot: string,
  editorKind: ModuleSourceSlot["editorKind"]
): ModuleSourceSlot {
  return {
    slot,
    name: `${slot}.txt`,
    path: `/project/${slot}.txt`,
    relative_path: `${slot}.txt`,
    extension: "txt",
    draftKey: slot,
    editorKind
  };
}

describe("groupModuleEditableSources", () => {
  it("keeps authored text in source order and moves raw metadata to advanced disclosure", () => {
    const metadata = source("meta", "code");
    const definition = source("def", "code");
    const localization = source("loc", "localization");

    expect(
      groupModuleEditableSources([metadata, definition, localization])
    ).toEqual({
      primary: [definition, localization],
      metadata: [metadata]
    });
  });

  it("does not expose image or asset sources as raw text", () => {
    const icon = source("icon", "image");
    const asset = source("mesh", "asset");

    expect(groupModuleEditableSources([icon, asset])).toEqual({
      primary: [],
      metadata: []
    });
  });
});
