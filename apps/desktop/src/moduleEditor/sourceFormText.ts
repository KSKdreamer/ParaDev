import type { Locale } from "../i18n";
import type { SourceFormText } from "../types";

/** Resolve Registry-owned source-form copy with the contract fallback. */
export function localizedSourceFormText(
  text: SourceFormText,
  locale: Locale
): string {
  if (typeof text === "string") {
    return text;
  }
  return text[locale] ?? text.default;
}
