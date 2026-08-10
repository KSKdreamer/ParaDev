/** @vitest-environment jsdom */

import { act } from "react";
import { createRoot, type Root } from "react-dom/client";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { createTranslator } from "../../i18n";
import type { PanelOption } from "../../types";
import { OptionList } from "./OptionList";

const items: PanelOption[] = [
  {
    groupKey: "modules.group.country",
    id: "countries",
    titleKey: "modules.countries.title"
  },
  {
    groupKey: "modules.group.other",
    id: "future-extension",
    label: "Future Extension"
  }
];

describe("OptionList grouped disclosure", () => {
  let container: HTMLDivElement;
  let root: Root;

  beforeEach(() => {
    container = document.createElement("div");
    document.body.append(container);
    root = createRoot(container);
  });

  afterEach(() => {
    act(() => root.unmount());
    container.remove();
  });

  it("lets authors expand a group that starts collapsed", () => {
    render("countries");
    const toggle = groupToggle("Other & Advanced");
    const group = controlledGroup(toggle);

    expect(toggle.getAttribute("aria-expanded")).toBe("false");
    expect(group.hidden).toBe(true);

    act(() => toggle.click());

    expect(toggle.getAttribute("aria-expanded")).toBe("true");
    expect(group.hidden).toBe(false);
  });

  it("reveals a collapsed group when its active family changes externally", () => {
    render("countries");
    const toggle = groupToggle("Other & Advanced");

    expect(toggle.getAttribute("aria-expanded")).toBe("false");

    render("future-extension");

    expect(toggle.getAttribute("aria-expanded")).toBe("true");
    expect(controlledGroup(toggle).hidden).toBe(false);
    expect(
      container
        .querySelector('[aria-label="Future Extension"]')
        ?.classList.contains("selected")
    ).toBe(true);
  });

  it("closes a boot placeholder group when the real active family loads", () => {
    render("future-extension", [items[1]]);

    expect(groupToggle("Other & Advanced").getAttribute("aria-expanded")).toBe("true");

    render("countries", items);

    expect(groupToggle("Countries & Politics").getAttribute("aria-expanded")).toBe("true");
    expect(groupToggle("Other & Advanced").getAttribute("aria-expanded")).toBe("false");
  });

  it("keeps a group open when the author expanded it explicitly", () => {
    render("countries");
    const otherToggle = groupToggle("Other & Advanced");

    act(() => otherToggle.click());
    render("future-extension");
    render("countries");

    expect(otherToggle.getAttribute("aria-expanded")).toBe("true");
  });

  function render(activeId: string, renderedItems: PanelOption[] = items) {
    act(() => {
      root.render(
        <OptionList
          activeId={activeId}
          defaultCollapsedGroupKeys={[
            "modules.group.country",
            "modules.group.other"
          ]}
          grouped
          items={renderedItems}
          onSelect={vi.fn()}
          t={createTranslator("en")}
        />
      );
    });
  }

  function groupToggle(label: string): HTMLButtonElement {
    const toggle = [...container.querySelectorAll<HTMLButtonElement>(
      ".option-group-title"
    )].find((candidate) => candidate.textContent?.includes(label));
    if (!toggle) {
      throw new Error(`Missing group toggle ${label}.`);
    }
    return toggle;
  }

  function controlledGroup(toggle: HTMLButtonElement): HTMLElement {
    const id = toggle.getAttribute("aria-controls");
    const group = id ? document.getElementById(id) : null;
    if (!group) {
      throw new Error("Group toggle does not reference a rendered group.");
    }
    return group;
  }
});
