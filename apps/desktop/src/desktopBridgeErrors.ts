import type { TranslationKey, Translator } from "./i18n";

const DESKTOP_BRIDGE_ERROR_KEYS: Record<string, TranslationKey> = {
  "Reading project source text through the native web bridge requires a project id.":
    "desktop.error.readSourceRequiresProjectId"
};

const DESKTOP_APPLICATION_REQUIRED =
  / requires the ParaDev desktop application\.$/;

export function localizeDesktopBridgeError(
  t: Translator,
  message: string
): string {
  if (DESKTOP_APPLICATION_REQUIRED.test(message)) {
    return t("desktop.error.desktopApplicationRequired");
  }
  const key = DESKTOP_BRIDGE_ERROR_KEYS[message];
  return key ? t(key) : message;
}

export function localizedParaDevServiceError(
  t: Translator,
  error: unknown
): string {
  if (error instanceof Error) {
    return localizeDesktopBridgeError(t, error.message);
  }
  if (typeof error === "string") {
    return localizeDesktopBridgeError(t, error);
  }
  return localizeDesktopBridgeError(t, String(error));
}
