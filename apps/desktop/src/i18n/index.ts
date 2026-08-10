import { en, type TranslationKey } from "./locales/en";
import { zh } from "./locales/zh";

export type Locale = "en" | "zh";
export type Translator = (key: TranslationKey, params?: Record<string, string | number>) => string;

const dictionaries: Record<Locale, Record<TranslationKey, string>> = {
  en,
  zh
};

export function createTranslator(locale: Locale): Translator {
  const dictionary = dictionaries[locale];

  return (key, params = {}) => {
    const template = dictionary[key] ?? en[key] ?? key;
    return Object.entries(params).reduce((text, [name, value]) => text.replaceAll(`{${name}}`, String(value)), template);
  };
}

export function htmlLangForLocale(locale: Locale): string {
  return locale === "zh" ? "zh-CN" : "en";
}

export function isTranslationKey(value: string | undefined): value is TranslationKey {
  return Boolean(value && value in en);
}

export type { TranslationKey };
