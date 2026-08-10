import { describe, expect, it } from "vitest";
import { createTranslator } from "./i18n";
import type { ParaDevAiChatSourceKindRow } from "./services/paradev";
import { aiChatContextSourceLabel, aiChatProfileSourceKindLabel } from "./aiChatSourceKindText";

const sourceKindRows: ParaDevAiChatSourceKindRow[] = [
  { frontendKinds: ["catalog"], id: "project-index", label: "Project index" },
  { frontendKinds: ["scripted-gui"], id: "scripted-gui", label: "Scripted GUI" },
  { frontendKinds: ["custom"], id: "custom-archive", label: "Custom archive" }
];

describe("aiChatSourceKindText", () => {
  it("localizes known SDK source kind rows without requiring runtime label keys", () => {
    const t = createTranslator("zh");

    expect(aiChatProfileSourceKindLabel("project-index", t, sourceKindRows)).toBe("项目索引");
    expect(aiChatProfileSourceKindLabel("scripted-gui", t, sourceKindRows)).toBe("脚本 GUI");
  });

  it("keeps custom SDK source labels instead of rendering raw ids", () => {
    const t = createTranslator("zh");

    expect(aiChatProfileSourceKindLabel("custom-archive", t, sourceKindRows)).toBe("Custom archive");
    expect(aiChatProfileSourceKindLabel("missing", t, sourceKindRows)).toBe("未知来源");
  });

  it("uses localized source kind row labels for floating chat contexts", () => {
    const t = createTranslator("zh");

    expect(aiChatContextSourceLabel({ kind: "catalog" }, t, sourceKindRows)).toBe("项目索引");
    expect(aiChatContextSourceLabel({ kind: "scripted-gui" }, t, sourceKindRows)).toBe("脚本 GUI");
  });

  it("localizes generic SDK context labels while preserving specific source labels", () => {
    const t = createTranslator("zh");

    expect(aiChatContextSourceLabel({ kind: "catalog", label: "Project index" }, t, sourceKindRows)).toBe("项目索引");
    expect(aiChatContextSourceLabel({ kind: "workspace", label: "Focus trees" }, t, sourceKindRows)).toBe("Focus trees");
  });
});
