/** Converts a validated template scalar into the string form used by GUI controls. */
export function templateScalarText(value: unknown): string {
  if (
    typeof value === "string" ||
    typeof value === "number" ||
    typeof value === "boolean"
  ) {
    return String(value);
  }
  return "";
}
