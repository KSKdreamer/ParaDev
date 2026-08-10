import type { LocSourceFormPatch } from "../types";
import type {
  JsonScalarReplacement,
  JsonScalarToken
} from "./jsonScalarPatch";

export type LocTextPatchErrorCode =
  | "invalid-span"
  | "invalid-text"
  | "stale-source"
  | "type-mismatch";

export class LocTextPatchError extends Error {
  readonly code: LocTextPatchErrorCode;

  constructor(code: LocTextPatchErrorCode, message: string) {
    super(message);
    this.name = "LocTextPatchError";
    this.code = code;
  }
}

const LANGUAGE_ALIASES: Readonly<Record<string, string>> = {
  braz_por: "l_braz_por",
  br: "l_braz_por",
  de: "l_german",
  en: "l_english",
  english: "l_english",
  es: "l_spanish",
  fr: "l_french",
  french: "l_french",
  german: "l_german",
  ja: "l_japanese",
  japanese: "l_japanese",
  jp: "l_japanese",
  ko: "l_korean",
  korean: "l_korean",
  kr: "l_korean",
  pl: "l_polish",
  polish: "l_polish",
  pt_br: "l_braz_por",
  ru: "l_russian",
  russian: "l_russian",
  simp_chinese: "l_simp_chinese",
  spanish: "l_spanish",
  zh: "l_simp_chinese",
  zh_cn: "l_simp_chinese"
};

/** Reads exactly the localization text reviewed by an SDK source form. */
export function readLocTextAtPatch(
  text: string,
  patch: LocSourceFormPatch
): JsonScalarToken {
  validateLocPatchSpan(text, patch);
  const token = text.slice(patch.span.start, patch.span.end);
  if (token !== patch.expected) {
    throw new LocTextPatchError(
      "stale-source",
      "The localization text no longer matches the reviewed source span."
    );
  }
  const normalized = normalizedLocText(token, patch.newline);
  const value = patch.style === "yaml" ? decodedYamlValue(normalized) : normalized;
  if (patch.style !== "section" && value.includes("\n")) {
    throw new LocTextPatchError(
      "invalid-text",
      "The reviewed inline localization value spans more than one line."
    );
  }
  return {
    from: patch.span.start,
    to: patch.span.end,
    kind: "string",
    token,
    value
  };
}

/** Replaces one reviewed localization value without touching its source syntax. */
export function replaceLocTextAtPatch(
  text: string,
  patch: LocSourceFormPatch,
  replacement: JsonScalarReplacement
): string {
  const current = readLocTextAtPatch(text, patch);
  if (replacement.kind !== "string") {
    throw new LocTextPatchError(
      "type-mismatch",
      "Localization text requires a text replacement."
    );
  }
  const value = validatedLocReplacement(replacement.value, patch.style);
  let encoded = patch.style === "yaml"
    ? `"${value.replaceAll("\\", "\\\\").replaceAll('"', '\\"')}"`
    : value.replaceAll("\n", patch.newline);
  if (
    patch.style === "section" &&
    current.from === current.to &&
    value &&
    text[current.to] === "["
  ) {
    encoded += patch.newline;
  }
  if (encoded === current.token) {
    return text;
  }
  return `${text.slice(0, current.from)}${encoded}${text.slice(current.to)}`;
}

function validateLocPatchSpan(text: string, patch: LocSourceFormPatch): void {
  const { end, start } = patch.span;
  if (
    !Number.isSafeInteger(start) ||
    !Number.isSafeInteger(end) ||
    start < 0 ||
    end < start ||
    end > text.length ||
    patch.expected.length !== end - start
  ) {
    throw new LocTextPatchError(
      "invalid-span",
      "The localization source span is malformed."
    );
  }
  if (!Number.isSafeInteger(patch.source_length) || patch.source_length < end) {
    throw new LocTextPatchError(
      "invalid-span",
      "The localization source length guard is malformed."
    );
  }
  if (text.length !== patch.source_length) {
    throw new LocTextPatchError(
      "stale-source",
      "The localization source length changed after its form was prepared."
    );
  }
}

function normalizedLocText(value: string, newline: LocSourceFormPatch["newline"]): string {
  if (newline === "\r\n") {
    const withoutCrLf = value.replaceAll("\r\n", "");
    if (withoutCrLf.includes("\r") || withoutCrLf.includes("\n")) {
      throw new LocTextPatchError(
        "invalid-text",
        "The localization value mixes line-ending styles."
      );
    }
    return value.replaceAll("\r\n", "\n");
  }
  if (value.includes("\r")) {
    throw new LocTextPatchError(
      "invalid-text",
      "The localization value contains an unsupported carriage return."
    );
  }
  return value;
}

function validatedLocReplacement(
  value: string,
  style: LocSourceFormPatch["style"]
): string {
  if (value.includes("\r")) {
    throw new LocTextPatchError(
      "invalid-text",
      "Localization replacements must use LF line endings."
    );
  }
  if (value !== value.trim()) {
    throw new LocTextPatchError(
      "invalid-text",
      "Localization replacements cannot start or end with whitespace."
    );
  }
  if (style !== "section" && value.includes("\n")) {
    throw new LocTextPatchError(
      "invalid-text",
      `${style === "yaml" ? "YAML" : "Inline"} localization replacements must stay on one line.`
    );
  }
  if (style === "section" && value.split("\n").some(isLocalizationHeader)) {
    throw new LocTextPatchError(
      "invalid-text",
      "Localization replacements cannot introduce another source section."
    );
  }
  return value;
}

function decodedYamlValue(value: string): string {
  if (value.startsWith('"') && value.endsWith('"')) {
    let decoded = "";
    const body = value.slice(1, -1);
    for (let index = 0; index < body.length; index += 1) {
      if (
        body[index] === "\\" &&
        index + 1 < body.length &&
        (body[index + 1] === "\\" || body[index + 1] === '"')
      ) {
        decoded += body[index + 1];
        index += 1;
      } else {
        decoded += body[index];
      }
    }
    return decoded;
  }
  if (value.startsWith("'") && value.endsWith("'")) {
    return value.slice(1, -1).replaceAll("''", "'");
  }
  return value;
}

function isLocalizationHeader(line: string): boolean {
  const stripped = line.trim();
  if (!stripped.startsWith("[")) {
    return false;
  }
  if (!stripped.endsWith("]") || stripped.length < 3) {
    return true;
  }
  const header = stripped.slice(1, -1).trim();
  if (!header) {
    return true;
  }
  const dot = header.indexOf(".");
  if (dot >= 0 && !header.slice(dot + 1).trim()) {
    return true;
  }
  const rawLanguage = dot >= 0 ? header.slice(0, dot) : header;
  const language = rawLanguage.trim().toLowerCase().replaceAll("-", "_");
  return (LANGUAGE_ALIASES[language] ?? language).startsWith("l_");
}
