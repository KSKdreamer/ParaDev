import type {
  PdxBlockBodySourceFormPatch,
  PdxIntegerListSourceFormPatch,
  PdxSourceFormPatch
} from "../types";
import type {
  JsonScalarPatchErrorCode,
  JsonScalarReplacement,
  JsonScalarToken
} from "./jsonScalarPatch";

export type PdxScalarPatchErrorCode =
  | Extract<JsonScalarPatchErrorCode, "invalid-number" | "type-mismatch">
  | "invalid-identifier"
  | "invalid-pdx-string"
  | "invalid-span"
  | "stale-source";

export class PdxScalarPatchError extends Error {
  readonly code: PdxScalarPatchErrorCode;

  constructor(code: PdxScalarPatchErrorCode, message: string) {
    super(message);
    this.name = "PdxScalarPatchError";
    this.code = code;
  }
}

const SAFE_PDX_IDENTIFIER =
  /^-?[A-Za-z_][A-Za-z0-9_-]*(?:(?:[:@?./^]|\/\/)[A-Za-z0-9_-]+)*(?:%{1,2})?$/;
const SAFE_PDX_NUMBER = /^-?\d+(?:\.\d+)?$/;

/**
 * Reads the exact scalar reviewed by one source-form PDX patch.
 *
 * The span uses UTF-16 code units, matching JavaScript string indexes. The
 * operation rejects any source-length or token mismatch instead of searching
 * for a similar token elsewhere.
 */
export function readPdxScalarAtPatch(text: string, patch: PdxSourceFormPatch): JsonScalarToken {
  validatePdxPatchSpan(text, patch);
  const token = text.slice(patch.span.start, patch.span.end);
  if (token !== patch.expected) {
    throw new PdxScalarPatchError(
      "stale-source",
      "The PDX scalar no longer matches the reviewed source token."
    );
  }
  const scalar = decodePdxScalar(token, patch.scalar_kind);
  return {
    from: patch.span.start,
    to: patch.span.end,
    kind: scalar.kind,
    token,
    value: scalar.value
  };
}

/**
 * Replaces only the exact reviewed scalar token in a PDX source draft.
 *
 * The returned full text remains in the existing draft/save transaction; this
 * function performs no file I/O.
 */
export function replacePdxScalarAtPatch(
  text: string,
  patch: PdxSourceFormPatch,
  replacement: JsonScalarReplacement
): string {
  const scalar = readPdxScalarAtPatch(text, patch);
  const encoded = encodePdxReplacement(patch.scalar_kind, replacement);
  if (scalar.kind !== encoded.kind) {
    throw new PdxScalarPatchError(
      "type-mismatch",
      `The PDX scalar contains ${scalar.kind}, not ${encoded.kind}.`
    );
  }
  if (scalar.token === encoded.token) {
    return text;
  }
  return `${text.slice(0, scalar.from)}${encoded.token}${text.slice(scalar.to)}`;
}

/** Reads one exact Registry-declared integer list as normalized rows. */
export function readPdxIntegerListAtPatch(
  text: string,
  patch: PdxIntegerListSourceFormPatch
): JsonScalarToken {
  validatePdxPatchSpan(text, patch);
  validatePdxIntegerListPatch(patch);
  const token = text.slice(patch.span.start, patch.span.end);
  if (token !== patch.expected) {
    throw new PdxScalarPatchError(
      "stale-source",
      "The PDX integer list no longer matches the reviewed source text."
    );
  }
  return {
    from: patch.span.start,
    to: patch.span.end,
    kind: "string",
    token,
    value: normalizePdxIntegerList(token, patch)
  };
}

/** Replaces one exact integer-list interior without touching its braces. */
export function replacePdxIntegerListAtPatch(
  text: string,
  patch: PdxIntegerListSourceFormPatch,
  replacement: JsonScalarReplacement
): string {
  const current = readPdxIntegerListAtPatch(text, patch);
  if (replacement.kind !== "string") {
    throw new PdxScalarPatchError(
      "type-mismatch",
      "A PDX integer list requires a text replacement."
    );
  }
  const normalized = normalizePdxIntegerList(replacement.value, patch);
  if (current.value === normalized) {
    return text;
  }
  const rows = normalized.split("\n").map((row) =>
    row.trim().split(/\s+/u).join(patch.layout.column_separator)
  );
  const encoded = `${patch.layout.prefix}${rows.join(patch.layout.row_separator)}${patch.layout.suffix}`;
  return `${text.slice(0, current.from)}${encoded}${text.slice(current.to)}`;
}

/** Reads one exact Registry-declared PDX block interior as editable text. */
export function readPdxBlockBodyAtPatch(
  text: string,
  patch: PdxBlockBodySourceFormPatch
): JsonScalarToken {
  validatePdxPatchSpan(text, patch);
  validatePdxBlockBodyPatch(patch);
  const token = text.slice(patch.span.start, patch.span.end);
  if (token !== patch.expected) {
    throw new PdxScalarPatchError(
      "stale-source",
      "The PDX block body no longer matches the reviewed source text."
    );
  }
  return {
    from: patch.span.start,
    to: patch.span.end,
    kind: "string",
    token,
    value: normalizePdxBlockBody(token)
  };
}

/** Replaces one reviewed block interior while preserving its outer braces. */
export function replacePdxBlockBodyAtPatch(
  text: string,
  patch: PdxBlockBodySourceFormPatch,
  replacement: JsonScalarReplacement
): string {
  const current = readPdxBlockBodyAtPatch(text, patch);
  if (replacement.kind !== "string") {
    throw new PdxScalarPatchError(
      "type-mismatch",
      "A PDX block body requires a text replacement."
    );
  }
  const normalized = normalizePdxBlockBody(replacement.value);
  if (current.value === normalized) {
    return text;
  }
  const encoded = normalized
    ? `${patch.layout.prefix}${normalized.split("\n").join(patch.layout.line_prefix)}${patch.layout.suffix}`
    : patch.layout.suffix;
  return `${text.slice(0, current.from)}${encoded}${text.slice(current.to)}`;
}

/** Parses one finite decimal PDX number token without accepting JSON exponents. */
export function parseFinitePdxNumberToken(rawToken: string): { token: string; value: number } {
  const token = rawToken.trim();
  if (!SAFE_PDX_NUMBER.test(token)) {
    throw new PdxScalarPatchError(
      "invalid-number",
      `The value ${JSON.stringify(rawToken)} is not a decimal PDX number.`
    );
  }
  const value = Number(token);
  if (!Number.isFinite(value)) {
    throw new PdxScalarPatchError(
      "invalid-number",
      `The value ${JSON.stringify(rawToken)} must be a finite PDX number.`
    );
  }
  return { token, value };
}

function validatePdxPatchSpan(
  text: string,
  patch: PdxSourceFormPatch | PdxIntegerListSourceFormPatch | PdxBlockBodySourceFormPatch
): void {
  const { end, start } = patch.span;
  const allowsEmpty = patch.op === "replace-pdx-block-body";
  if (
    !Number.isSafeInteger(start) ||
    !Number.isSafeInteger(end) ||
    start < 0 ||
    end < start ||
    (!allowsEmpty && end === start) ||
    end > text.length ||
    patch.expected.length !== end - start
  ) {
    throw new PdxScalarPatchError("invalid-span", "The PDX scalar source span is malformed.");
  }
  if (!Number.isSafeInteger(patch.source_length) || patch.source_length < end) {
    throw new PdxScalarPatchError("invalid-span", "The PDX source length guard is malformed.");
  }
  if (text.length !== patch.source_length) {
    throw new PdxScalarPatchError(
      "stale-source",
      "The PDX source length changed after its guided form was prepared."
    );
  }
}

function validatePdxBlockBodyPatch(patch: PdxBlockBodySourceFormPatch): void {
  for (const [key, whitespace] of Object.entries(patch.layout)) {
    if (
      typeof whitespace !== "string" ||
      whitespace.length > 256 ||
      /[^\t\n\r ]/u.test(whitespace) ||
      (key === "line_prefix" && !whitespace)
    ) {
      throw new PdxScalarPatchError(
        "invalid-span",
        "The PDX block-body layout is malformed."
      );
    }
  }
}

function normalizePdxBlockBody(raw: string): string {
  const normalized = raw.replaceAll("\r\n", "\n");
  if (normalized.includes("\r")) {
    throw new PdxScalarPatchError(
      "invalid-span",
      "The PDX block body contains unsupported line endings."
    );
  }
  const lines = normalized.split("\n");
  while (lines.length > 0 && !lines[0]?.trim()) {
    lines.shift();
  }
  while (lines.length > 0 && !lines.at(-1)?.trim()) {
    lines.pop();
  }
  const indents = lines
    .filter((line) => line.trim())
    .map((line) => line.match(/^[\t ]*/u)?.[0] ?? "");
  let margin = indents[0] ?? "";
  for (const indent of indents.slice(1)) {
    let length = 0;
    while (length < margin.length && margin[length] === indent[length]) {
      length += 1;
    }
    margin = margin.slice(0, length);
  }
  return lines.map((line) => line.slice(margin.length)).join("\n").trim();
}

function validatePdxIntegerListPatch(patch: PdxIntegerListSourceFormPatch): void {
  if (
    patch.item_kind !== "integer" ||
    !Number.isSafeInteger(patch.columns) ||
    patch.columns < 1 ||
    patch.columns > 16 ||
    !Number.isSafeInteger(patch.minimum)
  ) {
    throw new PdxScalarPatchError(
      "invalid-span",
      "The PDX integer-list contract is malformed."
    );
  }
  for (const [key, whitespace] of Object.entries(patch.layout)) {
    if (
      typeof whitespace !== "string" ||
      whitespace.length > 256 ||
      /[^\t\n\r ]/u.test(whitespace) ||
      ((key === "column_separator" || key === "row_separator") && !whitespace)
    ) {
      throw new PdxScalarPatchError(
        "invalid-span",
        "The PDX integer-list layout is malformed."
      );
    }
  }
}

function normalizePdxIntegerList(
  raw: string,
  patch: PdxIntegerListSourceFormPatch
): string {
  const rawTokens = raw.trim().split(/\s+/u).filter(Boolean);
  if (rawTokens.length === 0) {
    throw new PdxScalarPatchError(
      "invalid-number",
      "A PDX integer list must contain at least one integer."
    );
  }
  const tokens = rawTokens.map((token) => {
    if (!/^-?\d+$/u.test(token)) {
      throw new PdxScalarPatchError(
        "invalid-number",
        `The value ${JSON.stringify(token)} is not a decimal PDX integer.`
      );
    }
    const value = Number(token);
    if (!Number.isSafeInteger(value) || value < patch.minimum) {
      throw new PdxScalarPatchError(
        "invalid-number",
        `The value ${JSON.stringify(token)} must be a safe integer of at least ${patch.minimum}.`
      );
    }
    return String(value);
  });
  if (tokens.length % patch.columns !== 0) {
    throw new PdxScalarPatchError(
      "invalid-number",
      `A PDX integer list must contain exactly ${patch.columns} integers per row.`
    );
  }
  const rows: string[] = [];
  for (let index = 0; index < tokens.length; index += patch.columns) {
    rows.push(tokens.slice(index, index + patch.columns).join(" "));
  }
  return rows.join("\n");
}

function decodePdxScalar(
  token: string,
  scalarKind: PdxSourceFormPatch["scalar_kind"]
): { kind: JsonScalarToken["kind"]; value: JsonScalarToken["value"] } {
  if (scalarKind === "boolean") {
    if (token !== "yes" && token !== "no") {
      throw new PdxScalarPatchError("stale-source", "The reviewed PDX boolean is no longer yes or no.");
    }
    return { kind: "boolean", value: token === "yes" };
  }
  if (scalarKind === "number") {
    return { kind: "number", value: parseFinitePdxNumberToken(token).value };
  }
  if (scalarKind === "identifier") {
    if (!SAFE_PDX_IDENTIFIER.test(token)) {
      throw new PdxScalarPatchError("invalid-identifier", "The reviewed PDX identifier is not safely editable.");
    }
    return { kind: "string", value: token };
  }
  return { kind: "string", value: decodePdxString(token) };
}

function encodePdxReplacement(
  scalarKind: PdxSourceFormPatch["scalar_kind"],
  replacement: JsonScalarReplacement
): { kind: JsonScalarToken["kind"]; token: string } {
  if (scalarKind === "boolean") {
    if (replacement.kind !== "boolean") {
      throw new PdxScalarPatchError("type-mismatch", "A PDX boolean requires a boolean replacement.");
    }
    return { kind: "boolean", token: replacement.value ? "yes" : "no" };
  }
  if (scalarKind === "number") {
    if (replacement.kind !== "number") {
      throw new PdxScalarPatchError("type-mismatch", "A PDX number requires a numeric replacement.");
    }
    return { kind: "number", token: parseFinitePdxNumberToken(replacement.token).token };
  }
  if (replacement.kind !== "string") {
    throw new PdxScalarPatchError("type-mismatch", "A PDX text scalar requires a text replacement.");
  }
  if (scalarKind === "identifier") {
    if (!SAFE_PDX_IDENTIFIER.test(replacement.value)) {
      throw new PdxScalarPatchError(
        "invalid-identifier",
        "PDX identifiers cannot contain spaces, comments, braces, or operators."
      );
    }
    return { kind: "string", token: replacement.value };
  }
  return {
    kind: "string",
    token: `"${replacement.value.replaceAll("\\", "\\\\").replaceAll('"', '\\"')}"`
  };
}

function decodePdxString(token: string): string {
  if (token.length < 2 || token[0] !== '"' || token[token.length - 1] !== '"') {
    throw new PdxScalarPatchError("invalid-pdx-string", "The reviewed PDX string is not quoted.");
  }
  let value = "";
  for (let index = 1; index < token.length - 1; index += 1) {
    const character = token[index];
    if (character === "\\") {
      index += 1;
      if (index >= token.length - 1) {
        throw new PdxScalarPatchError("invalid-pdx-string", "The reviewed PDX string ends with an escape.");
      }
      value += token[index];
      continue;
    }
    if (character === '"') {
      throw new PdxScalarPatchError("invalid-pdx-string", "The reviewed PDX string contains an unescaped quote.");
    }
    value += character;
  }
  return value;
}
