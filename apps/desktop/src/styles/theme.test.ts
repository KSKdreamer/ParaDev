import { readFileSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { describe, expect, it } from "vitest";

const stylesDir = dirname(fileURLToPath(import.meta.url));
const repoRoot = resolve(stylesDir, "../../../..");
const themeCss = readFileSync(resolve(stylesDir, "theme.css"), "utf8");
const appCss = readFileSync(resolve(stylesDir, "app.css"), "utf8");
const styleDoc = readFileSync(resolve(repoRoot, "docs/techstack/ui/style.md"), "utf8");
const guiSpec = readFileSync(resolve(repoRoot, "docs/techstack/ui/gui-spec.md"), "utf8");

function cssBlock(css: string, selector: string): string {
  const escaped = selector.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  const match = css.match(new RegExp(`${escaped}\\s*\\{(?<body>[^}]*)\\}`));
  if (!match?.groups?.body) {
    throw new Error(`Missing ${selector} block`);
  }
  return match.groups.body;
}

function themeVars(selector: string) {
  return Object.fromEntries(
    [...cssBlock(themeCss, `.${selector}`).matchAll(/(--[a-z0-9-]+):\s*([^;]+);/g)].map((token) => [token[1], token[2].trim()])
  );
}

describe("desktop theme tokens", () => {
  it("keeps Anthropic mode aligned with the official Anthropic homepage first", () => {
    expect(themeCss).not.toContain(".theme-cowork");
    expect(themeVars("theme-anthropic")).toMatchObject({
      "--bg": "#f0eee6",
      "--surface": "#faf9f5",
      "--surface-2": "#e8e6dc",
      "--surface-3": "#d1cfc5",
      "--text": "#141413",
      "--muted": "#3d3d3a",
      "--subtle": "#87867f",
      "--label": "#5e5d59",
      "--border": "#1414131a",
      "--border-strong": "#14141333",
      "--accent": "#c6613f",
      "--accent-contrast": "#ffffff",
      "--accent-2": "#d97757",
      "--danger-soft": "#f3ded8",
      "--warning-soft": "#f4e5d3",
      "--success-soft": "#deeee5",
      "--code-bg": "#ecebe4",
      "--code-text": "#141413",
      "--cm-bg": "#faf9f5",
      "--cm-text": "#141413",
      "--cm-gutter-bg": "#f0eee6",
      "--cm-token-class": "#c6613f",
      "--cm-token-property": "#5563c1",
      "--cm-token-enum": "#d97757",
      "--cm-token-string": "#059669"
    });
  });

  it("defines label, inline-code, and CodeMirror tokens for every major theme", () => {
    for (const selector of ["theme-light", "theme-dark", "theme-anthropic"]) {
      const vars = themeVars(selector);
      expect(vars).toMatchObject({
        "--label": expect.stringMatching(/^#/),
        "--accent-contrast": expect.stringMatching(/^#/),
        "--danger": expect.stringMatching(/^#/),
        "--danger-soft": expect.stringMatching(/^#/),
        "--warning": expect.stringMatching(/^#/),
        "--warning-soft": expect.stringMatching(/^#/),
        "--success": expect.stringMatching(/^#/),
        "--success-soft": expect.stringMatching(/^#/),
        "--code-bg": expect.stringMatching(/^#/),
        "--code-text": expect.stringMatching(/^#/),
        "--cm-bg": expect.stringMatching(/^#/),
        "--cm-text": expect.stringMatching(/^#/),
        "--cm-token-class": expect.stringMatching(/^#/),
        "--cm-token-property": expect.stringMatching(/^#/),
        "--cm-token-enum": expect.stringMatching(/^#/),
        "--cm-token-string": expect.stringMatching(/^#/),
        "--cm-token-number": expect.stringMatching(/^#/),
        "--cm-token-variable": expect.stringMatching(/^#/),
        "--option-accent-0": expect.stringMatching(/^#/),
        "--option-accent-1": expect.stringMatching(/^#/),
        "--option-accent-2": expect.stringMatching(/^#/),
        "--option-accent-3": expect.stringMatching(/^#/),
        "--option-accent-4": expect.stringMatching(/^#/),
        "--option-accent-5": expect.stringMatching(/^#/),
        "--option-accent-6": expect.stringMatching(/^#/),
        "--option-accent-7": expect.stringMatching(/^#/),
        "--option-accent-8": expect.stringMatching(/^#/),
        "--option-accent-9": expect.stringMatching(/^#/)
      });
    }
  });

  it("applies the foreground token at the theme-scoped app root", () => {
    expect(cssBlock(appCss, ".app")).toContain("color: var(--text)");
  });

  it("keeps native controls inheriting the active theme foreground", () => {
    expect(appCss).toMatch(/button,\s*input,\s*select,\s*textarea\s*\{[^}]*font: inherit;[^}]*color: inherit;/);
  });
});

describe("GUI theme documentation", () => {
  it("names the three maintained themes and records token maintenance rules", () => {
    expect(styleDoc).toContain("Light Mode (Ollama Theme)");
    expect(styleDoc).toContain("Dark Mode (GitHub Soft Dark Theme)");
    expect(styleDoc).toContain("Anthropic Mode (Anthropic Theme)");
    expect(styleDoc).toContain("Official Anthropic homepage has highest priority");
    expect(styleDoc).toContain("Code and label color contract");
    expect(guiSpec).toContain("Theme Maintenance Contract");
    expect(guiSpec).toContain("Light Mode (Ollama Theme)");
    expect(guiSpec).toContain("Dark Mode (GitHub Soft Dark Theme)");
    expect(guiSpec).toContain("Anthropic Mode (Anthropic Theme)");
    expect(guiSpec).toContain("Official Anthropic homepage has highest priority");
  });
});
