import { readFileSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { describe, expect, it } from "vitest";

const stylesDir = dirname(fileURLToPath(import.meta.url));
const appCss = readFileSync(resolve(stylesDir, "app.css"), "utf8");

function cssBlock(selector: string): string {
  const escaped = selector.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  const match = appCss.match(new RegExp(`${escaped}\\s*\\{(?<body>[^}]*)\\}`));
  if (!match?.groups?.body) {
    throw new Error(`Missing ${selector} block`);
  }
  return match.groups.body;
}

describe("diagram editor styles", () => {
  it("keeps boot progress visibly active during long async project loads", () => {
    expect(cssBlock(".boot-progress-track span")).toContain("background-size: 200% 100%");
    expect(cssBlock(".boot-progress-track span")).toContain("animation: boot-progress-track-flow 1.4s linear infinite");
    expect(appCss).toContain("@keyframes boot-progress-track-flow");
    expect(appCss).toContain("@media (prefers-reduced-motion: reduce)");
  });

  it("keeps the normal-window toolbar readable instead of shrinking controls into vertical labels", () => {
    expect(cssBlock(".project-diagram-actions")).toContain("overflow: visible");
    expect(cssBlock(".project-diagram-actions")).toContain("flex-wrap: wrap");
    expect(cssBlock(".project-diagram-actions .toolbar-button")).toContain("flex: 0 0 auto");
    expect(cssBlock(".project-diagram-actions .toolbar-button")).toContain("white-space: nowrap");
    expect(cssBlock(".project-diagram-action-group")).toContain("flex: 0 0 auto");
    expect(cssBlock(".project-diagram-search-group")).toContain("flex: 1 1 260px");
    expect(cssBlock(".project-diagram-node-tools")).toContain("flex: 1 1 100%");
    expect(cssBlock(".project-diagram-node-tools")).toContain("overflow: hidden");
    expect(cssBlock(".project-diagram-node-tools .project-diagram-nudge")).toContain("flex-wrap: nowrap");
    expect(cssBlock(".project-diagram-node-tools .project-diagram-nudge")).toContain("overflow-x: auto");
    expect(cssBlock(".project-diagram-node-tools .project-diagram-move-tools")).toContain("flex-wrap: nowrap");
    expect(appCss).toContain("@media (max-width: 860px)");
    expect(appCss).toContain(".project-diagram-actions .project-diagram-json-toggle");
    expect(appCss).toContain(".project-diagram-actions .project-diagram-auto-layout-all");
    expect(appCss).toContain("font-size: 0");
  });

  it("keeps the selected-node inspector in panel flow instead of overlaying the canvas", () => {
    expect(cssBlock(".project-diagram-workspace")).toContain("grid-template-columns: minmax(0, 1fr) minmax(260px, 320px)");
    expect(cssBlock(".project-diagram-canvas")).toContain("position: relative");
    expect(cssBlock(".project-diagram-selection")).toContain("position: static");
    expect(cssBlock(".project-diagram-selection")).toContain("border-left: 1px solid var(--border)");
    expect(appCss).toContain("@media (max-width: 1100px)");
    expect(appCss).toContain("grid-template-rows: minmax(360px, 1fr) auto");
    expect(appCss).toContain("max-height: none");
  });

  it("hides advanced focus-tree chrome from the primary canvas page", () => {
    expect(appCss).toContain(".project-diagram-panel.focus-tree-diagram .project-diagram-file-group");
    expect(appCss).toContain(".project-diagram-panel.focus-tree-diagram .project-diagram-layout-group");
    expect(appCss).toContain(".project-diagram-panel.focus-tree-diagram .project-diagram-node-tools");
    expect(appCss).toContain(".project-diagram-panel.focus-tree-diagram .project-diagram-pan");
    expect(cssBlock(".project-diagram-panel.focus-tree-diagram .project-diagram-workspace")).toContain("grid-template-columns: minmax(0, 1fr)");
    expect(cssBlock(".project-diagram-panel.focus-tree-diagram .project-diagram-selection")).toContain("display: none");
  });

  it("keeps missing local focus icons visible as image slots during hydration", () => {
    expect(cssBlock(".project-diagram-node-image-placeholder rect")).toContain("fill: var(--surface-2)");
    expect(cssBlock(".project-diagram-node-image-placeholder rect")).toContain("stroke: var(--border-strong)");
    expect(cssBlock(".project-diagram-node-image-placeholder path")).toContain("stroke: var(--muted)");
    expect(cssBlock(".project-diagram-node-image-placeholder.focus-icon rect")).toContain("rx: 4px");
  });

  it("keeps focus-tree canvas chrome thin and icon-first", () => {
    expect(cssBlock(".project-diagram-edge")).toContain("stroke: color-mix(in srgb, var(--text) 84%, transparent)");
    expect(cssBlock(".project-diagram-edge")).toContain("stroke-width: 1");
    expect(cssBlock(".project-diagram-edge.tree")).toContain("stroke: color-mix(in srgb, var(--text) 84%, transparent)");
    expect(cssBlock(".project-diagram-node-hit-target")).toContain("fill: transparent");
    expect(cssBlock(".project-diagram-node-hit-target")).toContain("pointer-events: all");
    expect(cssBlock(".project-diagram-node-hit-target")).toContain("stroke: transparent");
    expect(cssBlock(".project-diagram-node.selected > rect")).toContain("fill: transparent");
    expect(cssBlock(".project-diagram-node.selected > rect")).toContain("stroke-width: 1");
    expect(cssBlock(".project-diagram-focus-icon-frame")).toContain("fill: transparent");
    expect(cssBlock(".project-diagram-focus-icon-frame")).toContain("stroke: transparent");
    expect(cssBlock(".project-diagram-focus-icon-frame")).toContain("pointer-events: none");
    expect(cssBlock(".project-diagram-icon-frame")).toContain("fill: color-mix");
    expect(cssBlock(".project-diagram-icon-frame")).toContain("stroke: var(--border-strong)");
    expect(cssBlock(".project-diagram-icon-frame")).toContain("pointer-events: none");
    expect(cssBlock(".project-diagram-focus-title-plaque")).toContain("display: none");
  });

  it("keeps diagram node hover details in one non-scaling HTML card", () => {
    expect(appCss).not.toContain(".project-diagram-node-hover-panel");
    expect(cssBlock(".project-diagram-node-hover-card")).toContain("position: absolute");
    expect(cssBlock(".project-diagram-node-hover-card")).toContain("pointer-events: none");
    expect(cssBlock(".project-diagram-node-hover-card")).toContain("font-weight: 450");
    expect(cssBlock(".project-diagram-node-hover-card strong")).toContain("font-weight: 500");
    expect(cssBlock(".project-diagram-node-hover-card dt")).toContain("font-weight: 500");
  });

  it("styles opened node info as a compact canvas overlay", () => {
    expect(cssBlock(".project-diagram-node-info-popover")).toContain("position: absolute");
    expect(cssBlock(".project-diagram-node-info-popover")).toContain("right: 10px");
    expect(cssBlock(".project-diagram-node-info-popover")).toContain("max-height: calc(100% - 116px)");
    expect(cssBlock(".project-diagram-node-info-popover dl")).toContain("grid-template-columns: auto minmax(0, 1fr)");
    expect(cssBlock(".project-diagram-node-info-source")).toContain("border-top: 1px solid var(--border)");
  });

  it("keeps long PIHC3 source selectors readable beside source paths", () => {
    expect(cssBlock(".source-tab-strip")).toContain("align-items: center");
    expect(cssBlock(".source-tab-source-picker")).toContain("flex: 1 1 280px");
    expect(cssBlock(".source-tab-source-picker span")).toContain("flex: 0 0 auto");
    expect(cssBlock(".source-tab-source-picker .source-tab-source-select")).toContain("flex: 1 1 180px");
    expect(cssBlock(".source-tab-source-picker .source-tab-source-select")).toContain("width: 100%");
    expect(cssBlock(".source-tab-source-path")).toContain("flex: 0 1 min(520px, 36vw)");
  });

  it("styles the selected focus node mode switch as a tiny icon control", () => {
    expect(cssBlock(".project-diagram-node-mode-switch")).toContain("cursor: pointer");
    expect(cssBlock(".project-diagram-node-mode-switch rect")).toContain("vector-effect: non-scaling-stroke");
    expect(cssBlock(".project-diagram-node-mode-switch-icon")).toContain("pointer-events: none");
    expect(cssBlock(".project-diagram-node-mode-switch-icon svg")).toContain("stroke-width: 2");
  });

  it("keeps selected focus coordinate badges as non-interactive overlays", () => {
    expect(cssBlock(".project-diagram-node-coordinate-badges")).toContain("pointer-events: none");
    expect(cssBlock(".project-diagram-node-coordinate-badges rect")).toContain("fill: color-mix");
    expect(cssBlock(".project-diagram-node-coordinate-badges text")).toContain("font-size: 7px");
  });

  it("keeps selected focus movement controls compact with one mode strip and one pad", () => {
    expect(cssBlock(".project-diagram-move-tools")).toContain("display: inline-flex");
    expect(cssBlock(".project-diagram-move-tools")).toContain("flex-wrap: wrap");
    expect(cssBlock(".project-diagram-move-modes")).toContain("display: inline-flex");
    expect(cssBlock(".project-diagram-move-mode")).toContain("max-width: 64px");
    expect(cssBlock(".project-diagram-move-hint")).toContain("max-width: 154px");
    expect(cssBlock(".project-diagram-move-hint")).toContain("text-overflow: ellipsis");
    expect(cssBlock(".project-diagram-move-pad")).toContain("display: inline-flex");
    expect(cssBlock(".project-diagram-move-pad .toolbar-button")).toContain("width: 26px");
  });

  it("keeps selected move footprint visible without stretching the inspector", () => {
    expect(cssBlock(".project-diagram-selection-move-footprint")).toContain("display: grid");
    expect(cssBlock(".project-diagram-selection-move-footprint")).toContain("grid-column: 1 / -1");
    expect(cssBlock(".project-diagram-selection-move-footprint > span")).toContain("justify-content: space-between");
    expect(cssBlock(".project-diagram-center-move-footprint")).toContain("width: 22px");
    expect(cssBlock(".project-diagram-center-move-footprint")).toContain("height: 22px");
    expect(cssBlock(".project-diagram-selection-move-footprint-nodes")).toContain("display: flex");
    expect(cssBlock(".project-diagram-selection-move-footprint-nodes")).toContain("flex-wrap: wrap");
    expect(cssBlock(".project-diagram-selection-move-footprint-nodes button,\n.project-diagram-selection-move-footprint-nodes code")).toContain("height: 20px");
  });
});
