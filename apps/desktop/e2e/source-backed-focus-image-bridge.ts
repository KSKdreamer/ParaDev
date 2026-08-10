import {
  c01CozyGlowSmokeSourceInfoText,
  c01MainSmokeMetaYaml
} from "../src/diagramEditor/fixtures/sourceBackedSmokeModel";
import {
  sourceBackedClearParentMetadataText,
  sourceBackedClearParentSourceEditPath,
  sourceBackedClearParentSourceInfoText,
  sourceBackedLayoutHintSourceEditPath,
  sourceBackedLayoutHintSourceInfoText,
  sourceBackedRelationshipSourceEditPath,
  sourceBackedRelationshipSourceInfoText
} from "../src/moduleEditor/fixtures/sourceBackedDiagramApplySmokeModel";
import { smokePngBytesForSourcePath } from "../src/testFixtures/smokeImages";

type BridgeDatasetNames = {
  applyCount?: string;
  applyEditCount?: string;
  cacheWriteCount?: string;
  lastCommand?: string;
  lastApplyPath?: string;
  lastApplyText?: string;
  lastPath?: string;
  readCount?: string;
};

type SourceTextEdit = {
  path?: string;
  text?: string;
};

const textSourcesByRelativePath = textSourceMapByRelativePath();

export function installSourceBackedFocusImageBridge(datasetNames: BridgeDatasetNames = {}) {
  const cache = new Map<string, number[]>();
  const bridgeState = globalThis as typeof globalThis & {
    __PARADEV_RUNTIME_CONFIG__?: { nativeBridgeBaseUrl?: string };
  };
  const origin = globalThis.location?.origin ?? "http://paradev.test";
  const fallbackFetch = globalThis.fetch?.bind(globalThis);
  bridgeState.__PARADEV_RUNTIME_CONFIG__ = { nativeBridgeBaseUrl: origin };
  bridgeState.fetch = async (input: RequestInfo | URL, init?: RequestInit) => {
    const request = new Request(input, init);
    const url = new URL(request.url);
    if (url.origin !== origin) {
      if (fallbackFetch) {
        return await fallbackFetch(input, init);
      }
      throw new Error(`Unexpected cross-origin smoke request: ${url}`);
    }
    if (url.pathname === "/frontend-api/rest-request") {
      const operationId = url.searchParams.get("operation_id") ?? "unknown";
      return jsonResponse({
        body: await request.json(),
        method: "POST",
        path: `/smoke/frontend-api/${encodeURIComponent(operationId)}`,
        query: {}
      });
    }
    if (url.pathname === "/desktop/sources/binary") {
      const body = (await request.json()) as { sourcePath?: string };
      const sourcePath = body.sourcePath ?? "";
      recordBridgeCommand("binary-source", datasetNames, sourcePath);
      return jsonResponse(payload(sourcePath, await previewBytesForSourcePath(sourcePath)));
    }
    if (url.pathname === "/desktop/thumbnail-cache" && request.method === "GET") {
      const cacheKey = url.searchParams.get("cache_key") ?? "";
      return jsonResponse(cache.has(cacheKey) ? payload(cacheKey, cache.get(cacheKey) ?? []) : null);
    }
    if (url.pathname === "/desktop/thumbnail-cache" && request.method === "PUT") {
      const body = (await request.json()) as { bytes?: number[]; cacheKey?: string };
      const cacheKey = body.cacheKey ?? "";
      if (cacheKey && body.bytes) {
        cache.set(cacheKey, body.bytes);
      }
      recordBridgeCommand("thumbnail-cache-write", datasetNames);
      return jsonResponse(payload(cacheKey, body.bytes ?? []));
    }
    const operationId = decodeURIComponent(url.pathname.replace("/smoke/frontend-api/", ""));
    if (url.pathname.startsWith("/smoke/frontend-api/") && operationId === "project.source_text") {
      const body = (await request.json()) as { source_path?: string };
      const sourcePath = body.source_path ?? "";
      recordBridgeCommand("source-text", datasetNames, sourcePath);
      return jsonResponse(textForSourcePath(sourcePath));
    }
    if (url.pathname.startsWith("/smoke/frontend-api/") && operationId === "project.draft_apply") {
      const body = (await request.json()) as {
        path?: string;
        project_id?: string;
        source_edits?: SourceTextEdit[];
        source_replacements?: { path?: string }[];
      };
      const sourceEdits = (body.source_edits ?? []).filter((edit): edit is Required<SourceTextEdit> => Boolean(edit.path));
      const sourceReplacements = (body.source_replacements ?? []).filter((replacement): replacement is { path: string } => Boolean(replacement.path));
      const files = [
        ...sourceEdits.map((edit) => ({
          path: edit.path,
          relative_path: relativeApplyPath(edit.path, body.path),
          operation: "write_text",
          encoding: "utf-8"
        })),
        ...sourceReplacements.map((replacement) => ({
          path: replacement.path,
          relative_path: relativeApplyPath(replacement.path, body.path),
          operation: "replace_bytes"
        }))
      ];
      recordApplyCommand(datasetNames, sourceEdits);
      return jsonResponse({
        schema: "paradev.rest.draft_apply.v1",
        project_id: body.project_id ?? "PIHC3",
        written: files.length > 0,
        files
      });
    }
    if (fallbackFetch) {
      return await fallbackFetch(input, init);
    }
    throw new Error(`Unexpected smoke bridge request: ${request.method} ${url.pathname}`);
  };
}

function jsonResponse(value: unknown): Response {
  return Response.json(value, {
    headers: { "content-type": "application/json" },
    status: 200
  });
}

function recordBridgeCommand(command: string, datasetNames: BridgeDatasetNames, path = "") {
  setDatasetValue(datasetNames.lastCommand, command);
  if (command === "binary-source") {
    incrementDatasetValue(datasetNames.readCount);
    setDatasetValue(datasetNames.lastPath, path);
  }
  if (command === "thumbnail-cache-write") {
    incrementDatasetValue(datasetNames.cacheWriteCount);
  }
}

function recordApplyCommand(datasetNames: BridgeDatasetNames, edits: Required<SourceTextEdit>[]) {
  const primaryEdit = edits.find((edit) => normalizePath(edit.path).endsWith("/info.json")) ?? edits[0];
  incrementDatasetValue(datasetNames.applyCount);
  setDatasetValue(datasetNames.applyEditCount, String(edits.length));
  setDatasetValue(datasetNames.lastApplyPath, primaryEdit?.path ?? "");
  setDatasetValue(datasetNames.lastApplyText, primaryEdit?.text ?? "");
}

async function previewBytesForSourcePath(sourcePath: string): Promise<number[]> {
  if (!focusIdForSourcePath(sourcePath)) {
    throw new Error(`Unknown source-backed smoke image: ${sourcePath}`);
  }
  return smokePngBytesForSourcePath(sourcePath);
}

function textSourceMapByRelativePath(): Record<string, string> {
  return {
    "src/modules/focus_tree/C01_MAIN/meta.yaml": c01MainSmokeMetaYaml,
    "src/modules/focus_tree/C01_MAIN/legacy/C01_COZY_GLOW_CORONATION/info.json": c01CozyGlowSmokeSourceInfoText,
    "src/modules/focus_tree/C08_PARTIV/meta.yaml": sourceBackedClearParentMetadataText,
    [relativeProjectPath(sourceBackedClearParentSourceEditPath)]: sourceBackedClearParentSourceInfoText,
    [relativeProjectPath(sourceBackedLayoutHintSourceEditPath)]: sourceBackedLayoutHintSourceInfoText,
    [relativeProjectPath(sourceBackedRelationshipSourceEditPath)]: sourceBackedRelationshipSourceInfoText
  };
}

function focusIdForSourcePath(sourcePath: string): string | undefined {
  return sourcePath.match(/focus_tree\/[^/]+\/icons\/([^/]+)\.png$/)?.[1];
}

function textForSourcePath(sourcePath: string): string {
  const relativePath = relativeProjectPath(sourcePath);
  const text = textSourcesByRelativePath[relativePath];
  if (text === undefined) {
    if (relativePath.endsWith("/info.json")) {
      return genericFocusInfoText(relativePath);
    }
    if (relativePath.endsWith("/meta.yaml")) {
      return "type: focus_tree\nsettings: {}\n";
    }
    throw new Error(`Unknown source-backed smoke text source: ${sourcePath}`);
  }
  return text;
}

function genericFocusInfoText(relativePath: string): string {
  const treeId = relativePath.match(/focus_tree\/([^/]+)\//)?.[1] ?? "SMOKE_TREE";
  const focusId = relativePath.match(/legacy\/([^/]+)\/info\.json$/)?.[1] ?? "SMOKE_FOCUS";
  return `${JSON.stringify({ tree: treeId, id: focusId, parent: null }, null, 4)}\n`;
}

function relativeApplyPath(path: string, projectRoot: string | undefined): string {
  const normalizedPath = normalizePath(path);
  const normalizedRoot = normalizePath(projectRoot ?? "").replace(/\/+$/, "");
  if (normalizedRoot && normalizedPath.startsWith(`${normalizedRoot}/`)) {
    return normalizedPath.slice(normalizedRoot.length + 1);
  }
  return relativeProjectPath(normalizedPath);
}

function relativeProjectPath(path: string): string {
  const normalizedPath = normalizePath(path);
  return normalizedPath.match(/(?:^|\/)(src\/modules\/focus_tree\/.*)$/)?.[1] ?? normalizedPath.replace(/^\/+/, "");
}

function normalizePath(path: string): string {
  return path.replace(/\\/g, "/");
}

function payload(path: string, bytes: number[]) {
  return {
    schema: "paradev.desktop.binary-source.v1",
    path,
    mimeType: "image/png",
    bytes
  };
}

function setDatasetValue(name: string | undefined, value: string) {
  if (name) {
    document.documentElement.dataset[name] = value;
  }
}

function incrementDatasetValue(name: string | undefined) {
  if (name) {
    document.documentElement.dataset[name] = String(Number(document.documentElement.dataset[name] ?? "0") + 1);
  }
}
