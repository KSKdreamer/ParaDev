import { jsonLanguage } from "@codemirror/lang-json";

export type JsonScalar = string | number | boolean | null;

export type JsonScalarKind = "string" | "number" | "boolean" | "null";

export type JsonScalarToken = {
  from: number;
  to: number;
  kind: JsonScalarKind;
  token: string;
  value: JsonScalar;
};

export type JsonScalarReplacement =
  | { kind: "string"; value: string }
  | { kind: "number"; token: string }
  | { kind: "boolean"; value: boolean }
  | { kind: "null"; value: null };

export type JsonScalarPatchErrorCode =
  | "container-target"
  | "duplicate-property"
  | "invalid-json"
  | "invalid-number"
  | "missing-path"
  | "type-mismatch";

export class JsonScalarPatchError extends Error {
  readonly code: JsonScalarPatchErrorCode;

  constructor(code: JsonScalarPatchErrorCode, message: string) {
    super(message);
    this.name = "JsonScalarPatchError";
    this.code = code;
  }
}

export type JsonScalarDocument = {
  read: (path: readonly (string | number)[]) => JsonScalarToken;
  replace: (path: readonly (string | number)[], replacement: JsonScalarReplacement) => string;
  text: string;
};

type JsonTree = ReturnType<typeof jsonLanguage.parser.parse>;
type JsonSyntaxNode = JsonTree["topNode"];

const JSON_VALUE_NODE_NAMES = new Set(["Array", "False", "Null", "Number", "Object", "String", "True"]);

export function parseJsonScalarDocument(text: string): JsonScalarDocument {
  const tree = jsonLanguage.parser.parse(text);
  assertValidSyntax(tree);

  const rootValues = nodeChildren(tree.topNode).filter(isJsonValueNode);
  if (rootValues.length !== 1) {
    throw new JsonScalarPatchError("invalid-json", "The source must contain exactly one JSON value.");
  }

  const containers = new Set<string>();
  const scalars = new Map<string, JsonScalarToken>();
  indexJsonValue(text, rootValues[0], [], containers, scalars);

  const read = (path: readonly (string | number)[]): JsonScalarToken => {
    const key = jsonPathKey(path);
    const scalar = scalars.get(key);
    if (scalar) {
      return scalar;
    }
    if (containers.has(key)) {
      throw new JsonScalarPatchError(
        "container-target",
        `The JSON path ${displayJsonPath(path)} points to an object or array, not a scalar.`
      );
    }
    throw new JsonScalarPatchError("missing-path", `The JSON path ${displayJsonPath(path)} does not exist.`);
  };

  return {
    read,
    replace(path, replacement) {
      const scalar = read(path);
      const encoded = encodeReplacement(replacement);
      if (scalar.kind !== encoded.kind) {
        throw new JsonScalarPatchError(
          "type-mismatch",
          `The JSON path ${displayJsonPath(path)} contains ${scalar.kind}, not ${encoded.kind}.`
        );
      }
      if (scalar.token === encoded.token) {
        return text;
      }
      return `${text.slice(0, scalar.from)}${encoded.token}${text.slice(scalar.to)}`;
    },
    text
  };
}

export function readJsonScalarAtPath(text: string, path: readonly (string | number)[]): JsonScalarToken {
  return parseJsonScalarDocument(text).read(path);
}

export function replaceJsonScalarAtPath(
  text: string,
  path: readonly (string | number)[],
  replacement: JsonScalarReplacement
): string {
  return parseJsonScalarDocument(text).replace(path, replacement);
}

export function parseFiniteJsonNumberToken(rawToken: string): { token: string; value: number } {
  const token = rawToken.trim();
  let value: unknown;
  try {
    value = JSON.parse(token);
  } catch {
    throw new JsonScalarPatchError("invalid-number", `The value ${JSON.stringify(rawToken)} is not a JSON number.`);
  }
  if (typeof value !== "number" || !Number.isFinite(value)) {
    throw new JsonScalarPatchError("invalid-number", `The value ${JSON.stringify(rawToken)} must be a finite JSON number.`);
  }
  return { token, value };
}

function assertValidSyntax(tree: JsonTree): void {
  const cursor = tree.cursor();
  do {
    if (cursor.type.isError) {
      throw new JsonScalarPatchError("invalid-json", "The source contains invalid JSON syntax.");
    }
  } while (cursor.next());
}

function indexJsonValue(
  text: string,
  node: JsonSyntaxNode,
  path: readonly (string | number)[],
  containers: Set<string>,
  scalars: Map<string, JsonScalarToken>
): void {
  if (node.name === "Object") {
    containers.add(jsonPathKey(path));
    indexJsonObject(text, node, path, containers, scalars);
    return;
  }
  if (node.name === "Array") {
    containers.add(jsonPathKey(path));
    const values = nodeChildren(node).filter(isJsonValueNode);
    values.forEach((value, index) => {
      indexJsonValue(text, value, [...path, index], containers, scalars);
    });
    return;
  }

  scalars.set(jsonPathKey(path), scalarTokenForNode(text, node));
}

function indexJsonObject(
  text: string,
  node: JsonSyntaxNode,
  path: readonly (string | number)[],
  containers: Set<string>,
  scalars: Map<string, JsonScalarToken>
): void {
  const names = new Set<string>();
  for (const property of nodeChildren(node).filter((child) => child.name === "Property")) {
    const children = nodeChildren(property);
    const nameNode = children.find((child) => child.name === "PropertyName");
    const valueNode = children.find(isJsonValueNode);
    if (!nameNode || !valueNode) {
      throw new JsonScalarPatchError("invalid-json", "A JSON object property is incomplete.");
    }

    const name = decodePropertyName(text.slice(nameNode.from, nameNode.to));
    if (names.has(name)) {
      throw new JsonScalarPatchError(
        "duplicate-property",
        `The JSON object at ${displayJsonPath(path)} contains the duplicate property ${JSON.stringify(name)}.`
      );
    }
    names.add(name);
    indexJsonValue(text, valueNode, [...path, name], containers, scalars);
  }
}

function scalarTokenForNode(text: string, node: JsonSyntaxNode): JsonScalarToken {
  const token = text.slice(node.from, node.to);
  if (node.name === "String") {
    return { from: node.from, to: node.to, kind: "string", token, value: decodeJsonString(token) };
  }
  if (node.name === "Number") {
    const parsed = parseFiniteJsonNumberToken(token);
    return { from: node.from, to: node.to, kind: "number", token, value: parsed.value };
  }
  if (node.name === "True" || node.name === "False") {
    return { from: node.from, to: node.to, kind: "boolean", token, value: node.name === "True" };
  }
  if (node.name === "Null") {
    return { from: node.from, to: node.to, kind: "null", token, value: null };
  }
  throw new JsonScalarPatchError("invalid-json", `Unsupported JSON syntax node ${node.name}.`);
}

function encodeReplacement(replacement: JsonScalarReplacement): { kind: JsonScalarKind; token: string } {
  if (replacement.kind === "number") {
    const parsed = parseFiniteJsonNumberToken(replacement.token);
    return { kind: "number", token: parsed.token };
  }
  if (replacement.kind === "string") {
    return { kind: "string", token: JSON.stringify(replacement.value) };
  }
  if (replacement.kind === "boolean") {
    return { kind: "boolean", token: replacement.value ? "true" : "false" };
  }
  return { kind: "null", token: "null" };
}

function decodePropertyName(token: string): string {
  return decodeJsonString(token);
}

function decodeJsonString(token: string): string {
  let value: unknown;
  try {
    value = JSON.parse(token);
  } catch {
    throw new JsonScalarPatchError("invalid-json", `The JSON token ${JSON.stringify(token)} is invalid.`);
  }
  if (typeof value !== "string") {
    throw new JsonScalarPatchError("invalid-json", `The JSON token ${JSON.stringify(token)} is not a string.`);
  }
  return value;
}

function isJsonValueNode(node: JsonSyntaxNode): boolean {
  return JSON_VALUE_NODE_NAMES.has(node.name);
}

function nodeChildren(node: JsonSyntaxNode): JsonSyntaxNode[] {
  const children: JsonSyntaxNode[] = [];
  for (let child = node.firstChild; child; child = child.nextSibling) {
    children.push(child);
  }
  return children;
}

function jsonPathKey(path: readonly (string | number)[]): string {
  return JSON.stringify(path);
}

function displayJsonPath(path: readonly (string | number)[]): string {
  return path.reduce<string>((display, segment) => {
    return typeof segment === "number" ? `${display}[${segment}]` : `${display}[${JSON.stringify(segment)}]`;
  }, "$");
}
