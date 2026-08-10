import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";
import { createTranslator } from "../i18n";
import { ProjectOnboarding } from "./ProjectOnboarding";

describe("ProjectOnboarding", () => {
  it("offers verified PIHC3 installation before opening an existing project", () => {
    const markup = renderToStaticMarkup(
      <ProjectOnboarding
        error=""
        importing={false}
        onImportProject={() => undefined}
        onOpenProject={() => undefined}
        opening={false}
        t={createTranslator("en")}
      />
    );

    expect(markup).toContain("Install PIHC3 package");
    expect(markup).toContain("Open existing project");
    expect(markup.indexOf("Install PIHC3 package")).toBeLessThan(
      markup.indexOf("Open existing project")
    );
    expect(markup).toContain("Documents/ParaDev/Projects");
    expect(markup).toContain("paradev.yaml");
    expect(markup).not.toContain("Minimal HOI4 Project");
  });

  it("locks both setup actions while installation is running and exposes errors", () => {
    const markup = renderToStaticMarkup(
      <ProjectOnboarding
        error="The selected folder does not contain paradev.yaml."
        importing
        onImportProject={() => undefined}
        onOpenProject={() => undefined}
        opening={false}
        t={createTranslator("en")}
      />
    );

    expect(markup.match(/<button[^>]*disabled=""/g)).toHaveLength(2);
    expect(markup).toContain("Installing PIHC3 package");
    expect(markup).toContain('role="alert"');
    expect(markup).toContain("does not contain paradev.yaml");
  });

  it("shows a neutral busy state while the bundled backend checks saved projects", () => {
    const markup = renderToStaticMarkup(
      <ProjectOnboarding
        checking
        error=""
        importing={false}
        onImportProject={() => undefined}
        onOpenProject={() => undefined}
        opening={false}
        t={createTranslator("en")}
      />
    );

    expect(markup).toContain("Finding your ParaDev project");
    expect(markup).toContain('aria-busy="true"');
    expect(markup).not.toContain("Install PIHC3 package");
    expect(markup).not.toContain("Minimal HOI4 Project");
  });
});
