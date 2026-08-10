import { describe, expect, it } from "vitest";
import type { LocSourceFormPatch } from "../types";
import {
  LocTextPatchError,
  readLocTextAtPatch,
  replaceLocTextAtPatch
} from "./locTextPatch";

describe("localization exact-span patches", () => {
  it("reads and replaces multiline CRLF text without touching source structure", () => {
    const text = "[en.KEY]\r\nOld 😀 title\r\nSecond line\r\n\r\n[zh.KEY]\r\n旧标题\r\n";
    const expected = "Old 😀 title\r\nSecond line";
    const start = text.indexOf("Old");
    const patch = locPatch(text, start, start + expected.length, expected);

    expect(readLocTextAtPatch(text, patch)).toMatchObject({
      from: start,
      to: start + expected.length,
      kind: "string",
      token: expected,
      value: "Old 😀 title\nSecond line"
    });
    expect(
      replaceLocTextAtPatch(text, patch, {
        kind: "string",
        value: "New title\nAnother line"
      })
    ).toBe(text.replace(expected, "New title\r\nAnother line"));
  });

  it("inserts text at a reviewed empty span", () => {
    const text = "[en]\nKEY=\n";
    const start = text.indexOf("\n", text.indexOf("KEY="));
    const patch = locPatch(text, start, start, "", "inline", "\n");

    expect(readLocTextAtPatch(text, patch).value).toBe("");
    expect(
      replaceLocTextAtPatch(text, patch, {
        kind: "string",
        value: "New value"
      })
    ).toBe("[en]\nKEY=New value\n");
  });

  it("rejects stale spans, structural injection, and multiline inline values", () => {
    const text = "[en.KEY]\nOld\n";
    const patch = locPatch(text, text.indexOf("Old"), text.indexOf("Old") + 3, "Old", "section", "\n");

    expect(() => readLocTextAtPatch(`${text}external`, patch)).toThrowError(LocTextPatchError);
    expect(() =>
      replaceLocTextAtPatch(text, patch, {
        kind: "string",
        value: "Safe\n[en.INJECTED]\nUnsafe"
      })
    ).toThrowError(/another source section/);
    expect(() =>
      replaceLocTextAtPatch(text, { ...patch, style: "inline" }, {
        kind: "string",
        value: "Line one\nLine two"
      })
    ).toThrowError(/one line/);
  });

  it("keeps scripted localization brackets valid inside section text", () => {
    const text = "[en.KEY]\nOld\n";
    const patch = locPatch(text, text.indexOf("Old"), text.indexOf("Old") + 3, "Old", "section", "\n");

    expect(
      replaceLocTextAtPatch(text, patch, {
        kind: "string",
        value: "[GetCountryName]\nToday: [?ROOT.VALUE|Y]"
      })
    ).toContain("[GetCountryName]\nToday: [?ROOT.VALUE|Y]");
  });

  it("decodes and re-encodes one HoI4 YAML-like value", () => {
    const text = 'l_english:\r\n KEY:0 "Old \\"title\\""\r\n';
    const expected = '"Old \\"title\\""';
    const start = text.indexOf(expected);
    const patch = locPatch(
      text,
      start,
      start + expected.length,
      expected,
      "yaml"
    );

    expect(readLocTextAtPatch(text, patch).value).toBe('Old "title"');
    expect(
      replaceLocTextAtPatch(text, patch, {
        kind: "string",
        value: 'New "title" at C:\\path'
      })
    ).toBe('l_english:\r\n KEY:0 "New \\"title\\" at C:\\\\path"\r\n');
  });
});

function locPatch(
  text: string,
  start: number,
  end: number,
  expected: string,
  style: LocSourceFormPatch["style"] = "section",
  newline: LocSourceFormPatch["newline"] = "\r\n"
): LocSourceFormPatch {
  return {
    op: "replace-loc-text",
    path: { language: "l_english", key: "KEY", occurrence: 0 },
    span: { start, end },
    expected,
    style,
    newline,
    source_length: text.length
  };
}
