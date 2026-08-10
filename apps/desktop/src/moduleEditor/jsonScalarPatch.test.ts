import { describe, expect, it } from "vitest";
import {
  JsonScalarPatchError,
  parseFiniteJsonNumberToken,
  parseJsonScalarDocument,
  readJsonScalarAtPath,
  replaceJsonScalarAtPath,
  type JsonScalarPatchErrorCode
} from "./jsonScalarPatch";

const entityRecord = [
  "{\r",
  '    "unknown": { "keep": [1, 2, 3] },\r',
  '    "mesh": {\r',
  '        "scale": 1.25\r',
  "    },\r",
  '    "entities": [\r',
  "        {\r",
  '            "scale": 1.0,\r',
  '            "default_state": "idle",\r',
  '            "state__D3": { "name": "explode", "looping": false },\r',
  '            "state": { "name": "idle", "animation": "idle" },\r',
  '            "state__D1": { "name": "move", "next_state": "idle" }\r',
  "        }\r",
  "    ]\r",
  "}\r",
  ""
].join("\n");

describe("JSON scalar patching", () => {
  it("replaces one deeply nested number token while preserving every other byte", () => {
    const path = ["mesh", "scale"] as const;
    const scalar = readJsonScalarAtPath(entityRecord, path);
    const next = replaceJsonScalarAtPath(entityRecord, path, { kind: "number", token: " 3.0 " });

    expect(scalar).toMatchObject({ kind: "number", token: "1.25", value: 1.25 });
    expect(next.slice(0, scalar.from)).toBe(entityRecord.slice(0, scalar.from));
    expect(next.slice(scalar.from, scalar.from + 3)).toBe("3.0");
    expect(next.slice(scalar.from + 3)).toBe(entityRecord.slice(scalar.to));
    expect(next).toContain('"unknown": { "keep": [1, 2, 3] }');
    expect(next).toContain('"state__D3"');
    expect(next.indexOf('"state__D3"')).toBeLessThan(next.indexOf('"state__D1"'));
    expect(next.endsWith("\r\n")).toBe(true);
  });

  it("replaces nested string and boolean tokens without normalizing surrounding JSON", () => {
    const moved = replaceJsonScalarAtPath(
      entityRecord,
      ["entities", 0, "state__D1", "next_state"],
      { kind: "string", value: 'fire "now"' }
    );
    const looped = replaceJsonScalarAtPath(
      moved,
      ["entities", 0, "state__D3", "looping"],
      { kind: "boolean", value: true }
    );

    expect(looped).toContain('"next_state": "fire \\"now\\""');
    expect(looped).toContain('"state__D3": { "name": "explode", "looping": true }');
    expect(looped).toContain('"state": { "name": "idle", "animation": "idle" }');
  });

  it("indexes once and reads current scalar values through a reusable document", () => {
    const document = parseJsonScalarDocument(entityRecord);

    expect(document.read(["entities", 0, "default_state"])).toMatchObject({
      kind: "string",
      token: '"idle"',
      value: "idle"
    });
    expect(document.read(["entities", 0, "state__D3", "looping"])).toMatchObject({
      kind: "boolean",
      token: "false",
      value: false
    });
  });

  it("rejects malformed JSON, including finite-invalid number values", () => {
    expectPatchError(() => parseJsonScalarDocument('{"value": }'), "invalid-json");
    expectPatchError(() => parseJsonScalarDocument('{"value": 1e999}'), "invalid-number");
  });

  it("rejects decoded duplicate property names before editing any path", () => {
    expectPatchError(
      () => replaceJsonScalarAtPath('{"value": 1, "\\u0076alue": 2}', ["value"], { kind: "number", token: "3" }),
      "duplicate-property"
    );
  });

  it("rejects missing, container, and out-of-range paths", () => {
    expectPatchError(
      () => replaceJsonScalarAtPath(entityRecord, ["entities", 1, "scale"], { kind: "number", token: "2" }),
      "missing-path"
    );
    expectPatchError(
      () => replaceJsonScalarAtPath(entityRecord, ["entities", 0, "state"], { kind: "string", value: "idle" }),
      "container-target"
    );
    expectPatchError(
      () => replaceJsonScalarAtPath(entityRecord, ["entities", 0, "missing"], { kind: "boolean", value: true }),
      "missing-path"
    );
  });

  it("rejects replacement values whose scalar type differs from the source", () => {
    expectPatchError(
      () => replaceJsonScalarAtPath(entityRecord, ["mesh", "scale"], { kind: "string", value: "3.0" }),
      "type-mismatch"
    );
  });

  it.each(["", " ", "01", "+1", ".5", "1.", "NaN", "Infinity", "1e999"])(
    "rejects invalid or non-finite number token %j",
    (token) => {
      expectPatchError(() => parseFiniteJsonNumberToken(token), "invalid-number");
    }
  );

  it.each([
    ["-0", -0],
    ["3.0", 3],
    ["1e-3", 0.001]
  ])("accepts finite JSON number lexeme %s", (token, value) => {
    const parsed = parseFiniteJsonNumberToken(String(token));
    expect(parsed.token).toBe(token);
    expect(Object.is(parsed.value, value)).toBe(true);
  });
});

function expectPatchError(action: () => unknown, code: JsonScalarPatchErrorCode): void {
  try {
    action();
  } catch (error) {
    expect(error).toBeInstanceOf(JsonScalarPatchError);
    expect((error as JsonScalarPatchError).code).toBe(code);
    return;
  }
  throw new Error(`Expected JsonScalarPatchError ${code}.`);
}
