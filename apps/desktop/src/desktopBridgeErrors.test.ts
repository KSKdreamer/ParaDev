import { describe, expect, it } from "vitest";
import { createTranslator } from "./i18n";
import { localizedParaDevServiceError } from "./desktopBridgeErrors";

describe("desktop bridge service errors", () => {
  it("localizes known desktop bridge fallback errors from thrown values", () => {
    const t = createTranslator("zh");

    const expected = "此操作需要使用 ParaDev 桌面应用。";
    expect(localizedParaDevServiceError(t, new Error("Opening local paths requires the ParaDev desktop application."))).toBe(expected);
    expect(localizedParaDevServiceError(t, "Local source loading requires the ParaDev desktop application.")).toBe(expected);
    expect(localizedParaDevServiceError(t, "Loading project source forms requires the ParaDev desktop application.")).toBe(expected);
    expect(localizedParaDevServiceError(t, "Creating module batches requires the ParaDev desktop application.")).toBe(expected);
  });

  it("keeps unknown backend details unchanged", () => {
    expect(localizedParaDevServiceError(createTranslator("zh"), new Error("Steam is unavailable."))).toBe("Steam is unavailable.");
  });
});
