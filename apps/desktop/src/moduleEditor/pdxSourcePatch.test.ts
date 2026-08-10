import { describe, expect, it } from "vitest";
import type {
  PdxBlockBodySourceFormPatch,
  PdxIntegerListSourceFormPatch,
  PdxSourceFormPatch
} from "../types";
import {
  parseFinitePdxNumberToken,
  PdxScalarPatchError,
  readPdxBlockBodyAtPatch,
  readPdxIntegerListAtPatch,
  readPdxScalarAtPatch,
  replacePdxBlockBodyAtPatch,
  replacePdxIntegerListAtPatch,
  replacePdxScalarAtPatch,
  type PdxScalarPatchErrorCode
} from "./pdxSourcePatch";

describe("PDX scalar source-form patches", () => {
  it("replaces only the reviewed token and preserves comments, spacing, CRLF, and quoting", () => {
    const text =
      '# 😀 heading\r\ncountry_event = {\r\n  picture = "gfx/events/old.dds" # keep\r\n  factor = 1.00\r\n}\r\n';
    const picture = patchFor(text, '"gfx/events/old.dds"', "string", [
      { key: "country_event", occurrence: 0 },
      { key: "picture", occurrence: 0 }
    ]);
    const factor = patchFor(text, "1.00", "number", [
      { key: "country_event", occurrence: 0 },
      { key: "factor", occurrence: 0 }
    ]);

    const renamed = replacePdxScalarAtPatch(text, picture, {
      kind: "string",
      value: 'gfx\\events\\"new".dds'
    });
    expect(renamed).toContain('picture = "gfx\\\\events\\\\\\"new\\".dds" # keep');
    expect(renamed.startsWith("# 😀 heading\r\n")).toBe(true);
    expect(renamed.endsWith("\r\n")).toBe(true);

    const scaled = replacePdxScalarAtPatch(text, factor, { kind: "number", token: "2.50" });
    expect(scaled).toBe(text.replace("factor = 1.00", "factor = 2.50"));
  });

  it("reads yes/no booleans and finite decimal numbers through one scalar shape", () => {
    const text = "active = yes\nweight = -12.50\n";
    const active = readPdxScalarAtPatch(
      text,
      patchFor(text, "yes", "boolean", [{ key: "active", occurrence: 0 }])
    );
    const weight = readPdxScalarAtPatch(
      text,
      patchFor(text, "-12.50", "number", [{ key: "weight", occurrence: 0 }])
    );

    expect(active).toMatchObject({ kind: "boolean", token: "yes", value: true });
    expect(weight).toMatchObject({ kind: "number", token: "-12.50", value: -12.5 });
    expect(
      replacePdxScalarAtPatch(
        text,
        patchFor(text, "yes", "boolean", [{ key: "active", occurrence: 0 }]),
        { kind: "boolean", value: false }
      )
    ).toContain("active = no");
  });

  it("keeps duplicate-key occurrence identity in the patch without searching by key", () => {
    const text = "option = { factor = 10 }\noption = { factor = 20 }\n";
    const second = patchFor(text, "20", "number", [
      { key: "option", occurrence: 1 },
      { key: "factor", occurrence: 0 }
    ]);

    expect(replacePdxScalarAtPatch(text, second, { kind: "number", token: "25" })).toBe(
      "option = { factor = 10 }\noption = { factor = 25 }\n"
    );
  });

  it("fails closed when text, source length, expected token, or span is stale", () => {
    const text = "active = yes\n";
    const patch = patchFor(text, "yes", "boolean", [{ key: "active", occurrence: 0 }]);

    expectPatchError(
      () => replacePdxScalarAtPatch(`# ${text}`, patch, { kind: "boolean", value: false }),
      "stale-source"
    );
    expectPatchError(
      () =>
        replacePdxScalarAtPatch("active = no \n", patch, {
          kind: "boolean",
          value: false
        }),
      "stale-source"
    );
    expectPatchError(
      () =>
        readPdxScalarAtPatch(text, {
          ...patch,
          span: { start: patch.span.start, end: patch.span.end + 1 }
        }),
      "invalid-span"
    );
  });

  it("rejects exponent numbers and identifier syntax that could inject PDX structure", () => {
    expect(() => parseFinitePdxNumberToken("1e3")).toThrow(PdxScalarPatchError);
    const text = "picture = GFX_TEST\n";
    const patch = patchFor(text, "GFX_TEST", "identifier", [{ key: "picture", occurrence: 0 }]);

    expectPatchError(
      () =>
        replacePdxScalarAtPatch(text, patch, {
          kind: "string",
          value: "GFX_TEST } # injected"
        }),
      "invalid-identifier"
    );
  });
});

describe("PDX block-body source-form patches", () => {
  it("normalizes the reviewed body and preserves CRLF and outer braces", () => {
    const text = "MY_EFFECT = {\r\n\tadd_power = 5\r\n\tif = { always = yes }\r\n}\r\n";
    const expected = "\r\n\tadd_power = 5\r\n\tif = { always = yes }\r\n";
    const patch = blockBodyPatchFor(text, expected);

    expect(readPdxBlockBodyAtPatch(text, patch).value).toBe(
      "add_power = 5\nif = { always = yes }"
    );
    expect(
      replacePdxBlockBodyAtPatch(text, patch, {
        kind: "string",
        value: "add_power = 10\nadd_stability = 0.05"
      })
    ).toBe(
      "MY_EFFECT = {\r\n\tadd_power = 10\r\n\tadd_stability = 0.05\r\n}\r\n"
    );
  });

  it("supports an empty exact span and rejects malformed layout", () => {
    const text = "EMPTY = {}\n";
    const patch = blockBodyPatchFor(text, "");

    expect(
      replacePdxBlockBodyAtPatch(text, patch, {
        kind: "string",
        value: "always = yes"
      })
    ).toBe("EMPTY = {\n    always = yes\n}\n");
    expectPatchError(
      () => readPdxBlockBodyAtPatch(text, {
        ...patch,
        layout: { ...patch.layout, line_prefix: "not whitespace" }
      }),
      "invalid-span"
    );
  });
});

describe("PDX integer-list source-form patches", () => {
  it("normalizes rows and replaces only the reviewed list interior", () => {
    const text = "victory_points = {\r\n    345\r\n    5\r\n    1637\r\n    3\r\n}\r\n";
    const patch = integerListPatchFor(text, "\r\n    345\r\n    5\r\n    1637\r\n    3\r\n", 2, 0);

    expect(readPdxIntegerListAtPatch(text, patch)).toMatchObject({
      kind: "string",
      value: "345 5\n1637 3"
    });
    expect(
      replacePdxIntegerListAtPatch(text, patch, {
        kind: "string",
        value: "345 7\n2000 2"
      })
    ).toBe("victory_points = {\r\n    345 7\r\n    2000 2\r\n}\r\n");
  });

  it("rejects unsafe values, incomplete rows, and stale source", () => {
    const text = "provinces = { 345 1637 }\n";
    const patch = integerListPatchFor(text, " 345 1637 ", 1, 1);

    expectPatchError(
      () => replacePdxIntegerListAtPatch(text, patch, { kind: "string", value: "345 # injected" }),
      "invalid-number"
    );
    expectPatchError(
      () => replacePdxIntegerListAtPatch(text, { ...patch, columns: 2 }, { kind: "string", value: "345" }),
      "invalid-number"
    );
    expectPatchError(
      () => readPdxIntegerListAtPatch(`# changed\n${text}`, patch),
      "stale-source"
    );
  });
});

function patchFor(
  text: string,
  expected: string,
  scalarKind: PdxSourceFormPatch["scalar_kind"],
  path: PdxSourceFormPatch["path"]
): PdxSourceFormPatch {
  const start = text.lastIndexOf(expected);
  if (start < 0) {
    throw new Error(`Missing fixture token ${expected}.`);
  }
  return {
    op: "replace-pdx-scalar",
    path,
    span: { start, end: start + expected.length },
    expected,
    scalar_kind: scalarKind,
    source_length: text.length
  };
}

function integerListPatchFor(
  text: string,
  expected: string,
  columns: number,
  minimum: number
): PdxIntegerListSourceFormPatch {
  const start = text.indexOf(expected);
  if (start < 0) {
    throw new Error(`Missing fixture list ${expected}.`);
  }
  const multiline = expected.includes("\n");
  return {
    op: "replace-pdx-integer-list",
    path: [{ key: "provinces", occurrence: 0 }],
    span: { start, end: start + expected.length },
    expected,
    item_kind: "integer",
    columns,
    minimum,
    layout: multiline
      ? {
          prefix: "\r\n    ",
          column_separator: " ",
          row_separator: "\r\n    ",
          suffix: "\r\n"
        }
      : {
          prefix: " ",
          column_separator: " ",
          row_separator: " ",
          suffix: " "
        },
    source_length: text.length
  };
}

function blockBodyPatchFor(
  text: string,
  expected: string
): PdxBlockBodySourceFormPatch {
  const start = text.indexOf(expected, text.indexOf("{") + 1);
  if (start < 0) {
    throw new Error(`Missing fixture block body ${expected}.`);
  }
  return {
    op: "replace-pdx-block-body",
    path: [{ key: text.slice(0, text.indexOf(" ")), occurrence: 0 }],
    span: { start, end: start + expected.length },
    expected,
    layout: {
      prefix: text.includes("\r\n") ? "\r\n\t" : "\n    ",
      line_prefix: text.includes("\r\n") ? "\r\n\t" : "\n    ",
      suffix: text.includes("\r\n") ? "\r\n" : "\n"
    },
    source_length: text.length
  };
}

function expectPatchError(action: () => unknown, code: PdxScalarPatchErrorCode): void {
  try {
    action();
  } catch (error) {
    expect(error).toBeInstanceOf(PdxScalarPatchError);
    expect((error as PdxScalarPatchError).code).toBe(code);
    return;
  }
  throw new Error(`Expected PdxScalarPatchError ${code}.`);
}
