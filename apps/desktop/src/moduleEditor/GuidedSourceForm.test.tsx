/** @vitest-environment jsdom */

import { act, useState } from "react";
import { createRoot, type Root } from "react-dom/client";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { createTranslator, type Locale } from "../i18n";
import type { SourceFormPayload } from "../types";
import {
  GuidedSourceForm,
  localizedSourceFormText,
  type GuidedSourceFormChange
} from "./GuidedSourceForm";

const sourceText = [
  "{\r",
  '  "unknown": { "keep": [1, 2, 3] },\r',
  '  "mesh": { "scale": 1.25 },\r',
  '  "entities": [\r',
  "    {\r",
  '      "name": "VIENTO_TEST",\r',
  '      "default_state": "idle",\r',
  '      "state__D2": { "name": "move", "next_state": "idle" },\r',
  '      "state": { "name": "idle", "animation": "idle", "looping": false }\r',
  "    }\r",
  "  ]\r",
  "}\r",
  ""
].join("\n");

const sourceForm: SourceFormPayload = {
  schema: "paradev.source-form.v1",
  contract: "pihc2.entity.record.v1",
  project_id: "PIHC3",
  family: "Entity",
  module_id: "Entity/VIENTO_TEST",
  path: "/workspace/PIHC3/src/modules/entity/VIENTO_TEST/record.json",
  relative_path: "src/modules/entity/VIENTO_TEST/record.json",
  module_relative_path: "record.json",
  source_root: "/workspace/PIHC3/src",
  source_format: "json",
  label: { default: "Entity record", zh: "实体记录" },
  description: { default: "Edit common settings.", zh: "编辑常用设置。" },
  sections: [
    {
      id: "mesh",
      label: { default: "Mesh", zh: "网格" },
      controls: [
        {
          id: "mesh-scale",
          label: { default: "Scale", zh: "缩放" },
          description: { default: "Visual size.", zh: "视觉大小。" },
          control: "number",
          value: 99,
          patch: { op: "replace-json-scalar", path: ["mesh", "scale"] },
          min: 0.1,
          max: 5,
          step: 0.05,
          placeholder: { default: "1.0", zh: "1.0" }
        }
      ]
    },
    {
      id: "entity-0",
      label: { default: "Entity", zh: "实体" },
      controls: [
        {
          id: "entity-name",
          label: { default: "Name", zh: "名称" },
          control: "readonly",
          value: "PROJECTED_NAME"
        },
        {
          id: "default-state",
          label: { default: "Default state", zh: "默认状态" },
          control: "choice",
          value: "move",
          patch: { op: "replace-json-scalar", path: ["entities", 0, "default_state"] },
          choices: [
            { label: { default: "Idle", zh: "待机" }, value: "idle" },
            { label: { default: "Move", zh: "移动" }, value: "move" }
          ]
        }
      ],
      sections: [
        {
          id: "state",
          label: { default: "Idle state", zh: "待机状态" },
          controls: [
            {
              id: "state-name",
              label: { default: "State name", zh: "状态名" },
              control: "readonly",
              value: "idle"
            },
            {
              id: "animation",
              label: { default: "Animation", zh: "动画" },
              control: "text",
              value: "stale",
              patch: { op: "replace-json-scalar", path: ["entities", 0, "state", "animation"] }
            },
            {
              id: "looping",
              label: { default: "Loop", zh: "循环" },
              control: "boolean",
              value: true,
              patch: { op: "replace-json-scalar", path: ["entities", 0, "state", "looping"] }
            }
          ]
        },
        {
          id: "state-d2",
          label: { default: "Move state", zh: "移动状态" },
          controls: [
            {
              id: "next-state",
              label: { default: "Next state", zh: "后续状态" },
              control: "choice",
              value: "idle",
              patch: { op: "replace-json-scalar", path: ["entities", 0, "state__D2", "next_state"] },
              choices: [
                { label: { default: "Idle", zh: "待机" }, value: "idle" },
                { label: { default: "Move", zh: "移动" }, value: "move" }
              ]
            }
          ]
        }
      ]
    }
  ]
};

const pdxSourceText = "# 😀 retained\r\nactive = yes # keep\r\n";
const pdxBooleanStart = pdxSourceText.indexOf("yes");
const pdxSourceForm: SourceFormPayload = {
  schema: "paradev.source-form.v1",
  contract: "paradev.pdx.guided-form.v1",
  project_id: "PIHC3",
  family: "Idea",
  module_id: "Idea/TEST_IDEA",
  path: "/workspace/PIHC3/src/modules/idea/TEST_IDEA/def.txt",
  relative_path: "src/modules/idea/TEST_IDEA/def.txt",
  module_relative_path: "def.txt",
  source_root: "/workspace/PIHC3/src",
  source_format: "pdx",
  label: { default: "Idea definition", zh: "理念定义" },
  coverage: { truncated: true, shown_controls: 1, total_controls: 217 },
  sections: [
    {
      id: "root",
      label: { default: "Definition", zh: "定义" },
      controls: [
        {
          id: "active",
          label: { default: "Active", zh: "启用" },
          description: { default: "Whether the idea is active.", zh: "该理念是否启用。" },
          description_source: "declared",
          control: "boolean",
          value: true,
          patch: {
            op: "replace-pdx-scalar",
            path: [{ key: "active", occurrence: 0 }],
            span: { start: pdxBooleanStart, end: pdxBooleanStart + "yes".length },
            expected: "yes",
            scalar_kind: "boolean",
            source_length: pdxSourceText.length
          }
        }
      ]
    }
  ]
};

const pdxIdentifierSourceText = "picture = OLD_ID # retained\n";
const pdxIdentifierStart = pdxIdentifierSourceText.indexOf("OLD_ID");
const pdxIdentifierSourceForm: SourceFormPayload = {
  ...pdxSourceForm,
  sections: [
    {
      id: "root",
      label: "Definition",
      controls: [
        {
          id: "picture",
          label: "Picture",
          control: "text",
          value: "OLD_ID",
          patch: {
            op: "replace-pdx-scalar",
            path: [{ key: "picture", occurrence: 0 }],
            span: {
              start: pdxIdentifierStart,
              end: pdxIdentifierStart + "OLD_ID".length
            },
            expected: "OLD_ID",
            scalar_kind: "identifier",
            source_length: pdxIdentifierSourceText.length
          }
        }
      ]
    }
  ]
};

const pdxListSourceText = "state = {\r\n  provinces = {\r\n    345\r\n    1637\r\n  }\r\n}\r\n";
const pdxListExpected = "\r\n    345\r\n    1637\r\n  ";
const pdxListStart = pdxListSourceText.indexOf(pdxListExpected);
const pdxListSourceForm: SourceFormPayload = {
  ...pdxSourceForm,
  family: "state",
  module_id: "state/199",
  path: "/workspace/PIHC3/src/modules/state/199/def.txt",
  relative_path: "src/modules/state/199/def.txt",
  coverage: { truncated: false, shown_controls: 1, total_controls: 1 },
  sections: [
    {
      id: "state",
      label: "state",
      controls: [
        {
          id: "provinces",
          label: { default: "Provinces", zh: "省份" },
          description: {
            default: "Province ids inside this State, one per line.",
            zh: "属于该地区的省份 ID，每行一个。"
          },
          description_source: "declared",
          control: "text",
          value: "345\n1637",
          multiline: true,
          placeholder: { default: "One integer per line", zh: "每行一个整数" },
          patch: {
            op: "replace-pdx-integer-list",
            path: [
              { key: "state", occurrence: 0 },
              { key: "provinces", occurrence: 0 }
            ],
            span: {
              start: pdxListStart,
              end: pdxListStart + pdxListExpected.length
            },
            expected: pdxListExpected,
            item_kind: "integer",
            columns: 1,
            minimum: 1,
            layout: {
              prefix: "\r\n    ",
              column_separator: " ",
              row_separator: "\r\n    ",
              suffix: "\r\n  "
            },
            source_length: pdxListSourceText.length
          }
        }
      ]
    }
  ]
};

const pdxBlockSourceText = "MY_EFFECT = {\r\n\tadd_power = 5\r\n}\r\n";
const pdxBlockExpected = "\r\n\tadd_power = 5\r\n";
const pdxBlockStart = pdxBlockSourceText.indexOf(pdxBlockExpected);
const pdxBlockSourceForm: SourceFormPayload = {
  ...pdxSourceForm,
  family: "scripted_effect",
  module_id: "scripted_effect/MY_EFFECT",
  path: "/workspace/PIHC3/src/modules/scripted_effect/MY_EFFECT/def.txt",
  relative_path: "src/modules/scripted_effect/MY_EFFECT/def.txt",
  coverage: { truncated: false, shown_controls: 1, total_controls: 1 },
  sections: [
    {
      id: "effect",
      label: "Top level",
      controls: [
        {
          id: "effect-body",
          label: { default: "Effect body", zh: "效果脚本" },
          control: "text",
          value: "add_power = 5",
          multiline: true,
          placeholder: {
            default: "Enter PDX statements without the outer braces",
            zh: "输入不含外层花括号的 PDX 语句"
          },
          patch: {
            op: "replace-pdx-block-body",
            path: [{ key: "MY_EFFECT", occurrence: 0 }],
            span: {
              start: pdxBlockStart,
              end: pdxBlockStart + pdxBlockExpected.length
            },
            expected: pdxBlockExpected,
            layout: {
              prefix: "\r\n\t",
              line_prefix: "\r\n\t",
              suffix: "\r\n"
            },
            source_length: pdxBlockSourceText.length
          }
        }
      ]
    }
  ]
};

const locSourceText = "[en.IDEA_TEST]\r\nOld title\r\nSecond line\r\n";
const locTextStart = locSourceText.indexOf("Old title");
const locExpected = "Old title\r\nSecond line";
const locSourceForm: SourceFormPayload = {
  schema: "paradev.source-form.v1",
  contract: "paradev.localization.text-form.v1",
  project_id: "PIHC3",
  family: "Idea",
  module_id: "Idea/IDEA_TEST",
  path: "/workspace/PIHC3/src/modules/idea/IDEA_TEST/main.loc",
  relative_path: "src/modules/idea/IDEA_TEST/main.loc",
  module_relative_path: "main.loc",
  source_root: "/workspace/PIHC3/src",
  source_format: "loc",
  label: { default: "Localization text", zh: "本地化文本" },
  sections: [
    {
      id: "english",
      label: { default: "English", zh: "英语" },
      controls: [
        {
          id: "idea-title",
          label: "IDEA_TEST",
          control: "text",
          value: "Old title\nSecond line",
          multiline: true,
          patch: {
            op: "replace-loc-text",
            path: { language: "l_english", key: "IDEA_TEST", occurrence: 0 },
            span: { start: locTextStart, end: locTextStart + locExpected.length },
            expected: locExpected,
            style: "section",
            newline: "\r\n",
            source_length: locSourceText.length
          }
        }
      ]
    }
  ]
};

const mounted: Array<{ container: HTMLDivElement; root: Root }> = [];
const translators = {
  en: createTranslator("en"),
  zh: createTranslator("zh")
} as const;

beforeEach(() => {
  (globalThis as typeof globalThis & { IS_REACT_ACT_ENVIRONMENT: boolean }).IS_REACT_ACT_ENVIRONMENT = true;
});

afterEach(() => {
  for (const item of mounted.splice(0)) {
    act(() => item.root.unmount());
    item.container.remove();
  }
});

describe("GuidedSourceForm", () => {
  it("renders recursive localized sections and reads current values from source text", () => {
    const { container } = renderForm({ locale: "zh" });

    expect(container.querySelector(".guided-source-form")?.getAttribute("aria-label")).toBe("实体记录");
    expect(container.textContent).toContain("编辑常用设置。");
    expect(container.textContent).toContain("网格");
    expect(container.textContent).toContain("待机状态");
    expect(container.querySelectorAll(".guided-source-form-section")).toHaveLength(4);
    expect(controlInput(container, "mesh-scale").value).toBe("1.25");
    expect(controlInput(container, "entity-name").value).toBe("PROJECTED_NAME");
    expect(controlInput(container, "entity-name").readOnly).toBe(true);
    expect(controlInput(container, "animation").value).toBe("idle");
    expect(controlInput(container, "looping").checked).toBe(false);
    expect(controlSelect(container, "default-state").selectedOptions[0]?.textContent).toBe("待机");
  });

  it("commits a valid number lexeme immediately and preserves CRLF, unknown fields, and member order", () => {
    const onDraft = vi.fn();
    const { container } = renderForm({ onDraft });
    const input = controlInput(container, "mesh-scale");

    setInputValue(input, "3.0");
    expect(onDraft).toHaveBeenCalledOnce();
    const next = onDraft.mock.calls[0][0] as string;
    expect(next).toContain('"mesh": { "scale": 3.0 }');
    expect(next).toContain('"unknown": { "keep": [1, 2, 3] }');
    expect(next.indexOf('"state__D2"')).toBeLessThan(next.indexOf('"state"'));
    expect(next.endsWith("\r\n")).toBe(true);

    focusAndBlur(input);
    expect(onDraft).toHaveBeenCalledOnce();
  });

  it("reports the Registry control intent with the unsaved source base", () => {
    const onGuidedChange = vi.fn();
    const { container } = renderForm({ onGuidedChange });

    setInputValue(controlInput(container, "mesh-scale"), "3.0");

    expect(onGuidedChange).toHaveBeenCalledWith({
      baseText: sourceText,
      controlId: "mesh-scale",
      text: expect.stringContaining('"mesh": { "scale": 3.0 }'),
      value: 3
    });
  });

  it("patches string, boolean, and choice controls through the same full-text callback", () => {
    const onDraft = vi.fn();
    const { container } = renderForm({ onDraft });

    setInputValue(controlInput(container, "animation"), "run");
    expect(lastDraft(onDraft)).toContain('"animation": "run"');

    act(() => controlInput(container, "looping").click());
    expect(lastDraft(onDraft)).toContain('"looping": true');

    setSelectValue(controlSelect(container, "default-state"), "1");
    expect(lastDraft(onDraft)).toContain('"default_state": "move"');
    expect(lastDraft(onDraft)).toContain('"unknown": { "keep": [1, 2, 3] }');
  });

  it("never emits from readonly controls", () => {
    const onDraft = vi.fn();
    const { container } = renderForm({ onDraft });
    const readonly = controlInput(container, "entity-name");

    expect(readonly.readOnly).toBe(true);
    setInputValue(readonly, "RENAMED");
    expect(onDraft).not.toHaveBeenCalled();
  });

  it("keeps empty and out-of-range number drafts local instead of turning them into zero", () => {
    const onDraft = vi.fn();
    const { container } = renderForm({ onDraft });
    const input = controlInput(container, "mesh-scale");

    setInputValue(input, "");
    focusAndBlur(input);
    expect(onDraft).not.toHaveBeenCalled();
    const emptyError = control(container, "mesh-scale").querySelector<HTMLElement>('[role="alert"]');
    expect(emptyError?.textContent).toContain("finite JSON number");
    expect(emptyError?.id).toBeTruthy();
    expect(input.getAttribute("aria-describedby")?.split(" ")).toContain(emptyError?.id);

    setInputValue(input, "7");
    focusAndBlur(input);
    expect(onDraft).not.toHaveBeenCalled();
    expect(control(container, "mesh-scale").querySelector('[role="alert"]')?.textContent).toContain("at most 5");
  });

  it("fails closed for malformed JSON and duplicate properties", () => {
    const malformed = renderForm({ initialText: '{"mesh": {"scale": }}' }).container;
    expect(malformed.querySelector('[role="alert"]')?.textContent).toContain("not valid JSON");
    expect(malformed.querySelector("input")).toBeNull();

    const duplicate = renderForm({ initialText: '{"mesh": {"scale": 1, "scale": 2}}' }).container;
    expect(duplicate.querySelector('[role="alert"]')?.textContent).toContain("duplicate JSON properties");
    expect(duplicate.querySelector("input")).toBeNull();
  });

  it("disables controls whose path, patch, or scalar type violates the contract", () => {
    const wrongType = structuredClone(sourceForm);
    const scale = wrongType.sections[0].controls?.[0];
    if (!scale) {
      throw new Error("Missing scale fixture.");
    }
    scale.control = "text";
    const wrongTypeContainer = renderForm({ form: wrongType }).container;
    expect(controlInput(wrongTypeContainer, "mesh-scale").disabled).toBe(true);
    expect(control(wrongTypeContainer, "mesh-scale").textContent).toContain("expects string");

    const missingPath = structuredClone(sourceForm);
    const animation = missingPath.sections[1].sections?.[0]?.controls?.find((item) => item.id === "animation");
    if (!animation?.patch) {
      throw new Error("Missing animation fixture.");
    }
    animation.patch.path = ["entities", 0, "state", "missing"];
    const missingPathContainer = renderForm({ form: missingPath }).container;
    expect(control(missingPathContainer, "animation").textContent).toContain("no longer exists");
    expect(control(missingPathContainer, "animation").querySelector("input")).toBeNull();

    const missingPatch = structuredClone(sourceForm);
    const defaultState = missingPatch.sections[1].controls?.find((item) => item.id === "default-state");
    if (!defaultState) {
      throw new Error("Missing default-state fixture.");
    }
    delete defaultState.patch;
    const missingPatchContainer = renderForm({ form: missingPatch }).container;
    expect(control(missingPatchContainer, "default-state").textContent).toContain("missing its exact source location");
  });

  it("localizes JSON and number validation errors", () => {
    const malformed = renderForm({ initialText: '{"mesh":', locale: "zh" }).container;
    expect(malformed.querySelector('[role="alert"]')?.textContent).toContain("不是有效的 JSON");

    const number = renderForm({ locale: "zh" }).container;
    const input = controlInput(number, "mesh-scale");
    setInputValue(input, "7");
    focusAndBlur(input);
    expect(control(number, "mesh-scale").querySelector('[role="alert"]')?.textContent).toContain("不能大于 5");
  });

  it("patches an exact PDX scalar while preserving comments, CRLF, and UTF-16 positions", () => {
    const onDraft = vi.fn();
    const { container } = renderForm({
      form: pdxSourceForm,
      initialText: pdxSourceText,
      onDraft
    });

    act(() => controlInput(container, "active").click());

    expect(onDraft).toHaveBeenCalledOnce();
    expect(lastDraft(onDraft)).toBe("# 😀 retained\r\nactive = no # keep\r\n");
  });

  it("edits a Registry-declared PDX integer list through a buffered textarea", () => {
    const onDraft = vi.fn();
    const { container } = renderForm({
      form: pdxListSourceForm,
      initialText: pdxListSourceText,
      onDraft
    });
    const textarea = control(container, "provinces").querySelector("textarea");
    if (!(textarea instanceof HTMLTextAreaElement)) {
      throw new Error("Missing PDX integer-list textarea fixture.");
    }
    expect(textarea.value).toBe("345\n1637");
    expect(control(container, "provinces").dataset.sourceFormMultiline).toBe("true");

    setTextAreaValue(textarea, "345\n2000\n3000");
    expect(onDraft).not.toHaveBeenCalled();
    focusAndBlur(textarea);

    expect(onDraft).toHaveBeenCalledOnce();
    expect(lastDraft(onDraft)).toBe(
      "state = {\r\n  provinces = {\r\n    345\r\n    2000\r\n    3000\r\n  }\r\n}\r\n"
    );
  });

  it("edits a Registry-declared PDX block body without exposing its braces", () => {
    const onDraft = vi.fn();
    const { container } = renderForm({
      form: pdxBlockSourceForm,
      initialText: pdxBlockSourceText,
      onDraft
    });
    const textarea = control(container, "effect-body").querySelector("textarea");
    if (!(textarea instanceof HTMLTextAreaElement)) {
      throw new Error("Missing PDX block-body textarea fixture.");
    }
    expect(textarea.value).toBe("add_power = 5");

    setTextAreaValue(textarea, "add_power = 10\nadd_stability = 0.05");
    expect(onDraft).not.toHaveBeenCalled();
    focusAndBlur(textarea);

    expect(onDraft).toHaveBeenCalledOnce();
    expect(lastDraft(onDraft)).toBe(
      "MY_EFFECT = {\r\n\tadd_power = 10\r\n\tadd_stability = 0.05\r\n}\r\n"
    );
  });

  it("edits multiline localization through a buffered exact-span textarea", () => {
    const onDraft = vi.fn();
    const { container } = renderForm({
      form: locSourceForm,
      initialText: locSourceText,
      onDraft
    });
    const textarea = control(container, "idea-title").querySelector("textarea");
    if (!(textarea instanceof HTMLTextAreaElement)) {
      throw new Error("Missing localization textarea fixture.");
    }
    expect(control(container, "idea-title").dataset.sourceFormMultiline).toBe("true");

    setTextAreaValue(textarea, "New title\nAnother line");
    expect(onDraft).not.toHaveBeenCalled();
    focusAndBlur(textarea);

    expect(onDraft).toHaveBeenCalledOnce();
    expect(lastDraft(onDraft)).toBe(
      "[en.IDEA_TEST]\r\nNew title\r\nAnother line\r\n"
    );
  });

  it("keeps localization syntax injection editable and reports a localized error", () => {
    const onDraft = vi.fn();
    const { container } = renderForm({
      form: locSourceForm,
      initialText: locSourceText,
      locale: "zh",
      onDraft
    });
    const textarea = control(container, "idea-title").querySelector("textarea");
    if (!(textarea instanceof HTMLTextAreaElement)) {
      throw new Error("Missing localization textarea fixture.");
    }

    setTextAreaValue(textarea, "Safe\n[en.INJECTED]\nUnsafe");
    focusAndBlur(textarea);

    expect(onDraft).not.toHaveBeenCalled();
    expect(textarea.disabled).toBe(false);
    expect(control(container, "idea-title").textContent).toContain("不要在译文中引入新的本地化分节");
  });

  it("shows partial guided coverage and preserves field-help provenance", () => {
    const { container } = renderForm({
      form: pdxSourceForm,
      initialText: pdxSourceText,
      locale: "zh"
    });

    expect(container.querySelector('[role="note"]')?.textContent).toContain("217");
    expect(container.querySelector('[role="note"]')?.textContent).toContain("1");
    expect(control(container, "active").dataset.sourceFormDescriptionSource).toBe("declared");
    expect(control(container, "active").textContent).toContain("该理念是否启用");
  });

  it("searches bounded PDX forms and can clear an empty result", () => {
    const onSearch = vi.fn();
    const { container } = renderForm({
      form: pdxSourceForm,
      initialText: pdxSourceText,
      onSearch
    });
    const search = container.querySelector('input[type="search"]');
    if (!(search instanceof HTMLInputElement)) {
      throw new Error("Missing guided form search input.");
    }
    setInputValue(search, "C01_C02_GREENLIGHT.40");
    act(() => buttonWithText(container, "Search").click());
    expect(onSearch).toHaveBeenCalledWith("C01_C02_GREENLIGHT.40");

    const empty = renderForm({
      form: {
        ...pdxSourceForm,
        query: "missing",
        coverage: { truncated: false, shown_controls: 0, total_controls: 0 },
        sections: []
      },
      initialText: pdxSourceText,
      onSearch
    }).container;
    expect(empty.textContent).toContain("No safe guided fields match");
    act(() => buttonWithText(empty, "Show first fields").click());
    expect(onSearch).toHaveBeenLastCalledWith("");
  });

  it("buffers multi-character PDX identifiers and emits one exact patch on commit", () => {
    const onDraft = vi.fn();
    const { container } = renderForm({
      form: pdxIdentifierSourceForm,
      initialText: pdxIdentifierSourceText,
      onDraft
    });
    const input = controlInput(container, "picture");

    setInputValue(input, "N");
    setInputValue(input, "NEW");
    setInputValue(input, "NEW_ID");
    expect(onDraft).not.toHaveBeenCalled();

    focusAndBlur(input);
    expect(onDraft).toHaveBeenCalledOnce();
    expect(lastDraft(onDraft)).toBe("picture = NEW_ID # retained\n");
  });

  it("keeps an invalid buffered PDX identifier editable so it can be corrected", () => {
    const onDraft = vi.fn();
    const { container } = renderForm({
      form: pdxIdentifierSourceForm,
      initialText: pdxIdentifierSourceText,
      onDraft
    });
    const input = controlInput(container, "picture");

    setInputValue(input, "BAD VALUE");
    focusAndBlur(input);
    expect(onDraft).not.toHaveBeenCalled();
    expect(input.disabled).toBe(false);
    expect(input.getAttribute("aria-invalid")).toBe("true");
    expect(control(container, "picture").textContent).toContain("without spaces");

    setInputValue(input, "GOOD_ID");
    expect(input.getAttribute("aria-invalid")).toBeNull();
    focusAndBlur(input);
    expect(onDraft).toHaveBeenCalledOnce();
    expect(lastDraft(onDraft)).toBe("picture = GOOD_ID # retained\n");
  });

  it("fails closed when a reviewed PDX token is stale even if the text length is unchanged", () => {
    const staleText = pdxSourceText.replace("yes", "no ");
    const { container } = renderForm({
      form: pdxSourceForm,
      initialText: staleText
    });

    expect(container.querySelector('[role="alert"]')?.textContent).toContain(
      "PDX source changed after this form was prepared"
    );
    expect(container.querySelector("input")).toBeNull();
  });

  it("disables a PDX form while its updated source projection is loading", () => {
    const { container } = renderForm({
      disabled: true,
      form: pdxSourceForm,
      initialText: pdxSourceText
    });

    expect(container.querySelector(".guided-source-form")?.getAttribute("aria-busy")).toBe("true");
    expect(controlInput(container, "active").disabled).toBe(true);
  });

  it("uses the default text when a locale-specific form label is absent", () => {
    expect(localizedSourceFormText({ default: "Fallback", en: "English" }, "zh")).toBe("Fallback");
  });
});

function StatefulForm({
  disabled,
  form,
  initialText,
  locale,
  onDraft,
  onGuidedChange,
  onSearch
}: {
  disabled: boolean;
  form: SourceFormPayload;
  initialText: string;
  locale: Locale;
  onDraft: (text: string) => void;
  onGuidedChange: (change: GuidedSourceFormChange) => void;
  onSearch: (query: string) => void;
}) {
  const [text, setText] = useState(initialText);
  return (
    <GuidedSourceForm
      disabled={disabled}
      form={form}
      locale={locale}
      onChange={(change) => {
        setText(change.text);
        onDraft(change.text);
        onGuidedChange(change);
      }}
      onSearch={onSearch}
      text={text}
      t={translators[locale]}
    />
  );
}

function renderForm({
  disabled = false,
  form = sourceForm,
  initialText = sourceText,
  locale = "en",
  onDraft = () => undefined,
  onGuidedChange = () => undefined,
  onSearch = () => undefined
}: {
  disabled?: boolean;
  form?: SourceFormPayload;
  initialText?: string;
  locale?: Locale;
  onDraft?: (text: string) => void;
  onGuidedChange?: (change: GuidedSourceFormChange) => void;
  onSearch?: (query: string) => void;
} = {}) {
  const container = document.createElement("div");
  document.body.append(container);
  const root = createRoot(container);
  mounted.push({ container, root });
  act(() =>
    root.render(
      <StatefulForm
        disabled={disabled}
        form={form}
        initialText={initialText}
        locale={locale}
        onDraft={onDraft}
        onGuidedChange={onGuidedChange}
        onSearch={onSearch}
      />
    )
  );
  return { container, root };
}

function buttonWithText(container: HTMLElement, text: string): HTMLButtonElement {
  const button = [...container.querySelectorAll("button")].find(
    (candidate) => candidate.textContent?.trim() === text
  );
  if (!(button instanceof HTMLButtonElement)) {
    throw new Error(`Missing button: ${text}`);
  }
  return button;
}

function control(container: HTMLElement, id: string): HTMLElement {
  const element = container.querySelector<HTMLElement>(`[data-source-form-control-id="${id}"]`);
  if (!element) {
    throw new Error(`Missing control ${id}.`);
  }
  return element;
}

function controlInput(container: HTMLElement, id: string): HTMLInputElement {
  const input = control(container, id).querySelector<HTMLInputElement>("input");
  if (!input) {
    throw new Error(`Missing input for ${id}.`);
  }
  return input;
}

function controlSelect(container: HTMLElement, id: string): HTMLSelectElement {
  const select = control(container, id).querySelector<HTMLSelectElement>("select");
  if (!select) {
    throw new Error(`Missing select for ${id}.`);
  }
  return select;
}

function setInputValue(input: HTMLInputElement, value: string): void {
  const setter = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, "value")?.set;
  if (!setter) {
    throw new Error("Missing HTMLInputElement value setter.");
  }
  act(() => {
    setter.call(input, value);
    input.dispatchEvent(new Event("input", { bubbles: true }));
  });
}

function setTextAreaValue(textarea: HTMLTextAreaElement, value: string): void {
  const setter = Object.getOwnPropertyDescriptor(HTMLTextAreaElement.prototype, "value")?.set;
  if (!setter) {
    throw new Error("Missing HTMLTextAreaElement value setter.");
  }
  act(() => {
    setter.call(textarea, value);
    textarea.dispatchEvent(new Event("input", { bubbles: true }));
  });
}

function focusAndBlur(input: HTMLInputElement | HTMLTextAreaElement): void {
  act(() => {
    input.focus();
    input.blur();
  });
}

function setSelectValue(select: HTMLSelectElement, value: string): void {
  const setter = Object.getOwnPropertyDescriptor(HTMLSelectElement.prototype, "value")?.set;
  if (!setter) {
    throw new Error("Missing HTMLSelectElement value setter.");
  }
  act(() => {
    setter.call(select, value);
    select.dispatchEvent(new Event("change", { bubbles: true }));
  });
}

function lastDraft(onDraft: ReturnType<typeof vi.fn>): string {
  const call = onDraft.mock.calls.at(-1);
  if (!call) {
    throw new Error("Expected a draft callback.");
  }
  return String(call[0]);
}
