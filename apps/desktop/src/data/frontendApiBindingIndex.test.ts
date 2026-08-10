import { describe, expect, it } from "vitest";

import {
  buildFrontendApiBindingLookupUrl,
  frontendApiBindingIndex,
  frontendApiGroupIds,
  frontendApiGroupIndex,
  frontendApiEndpointPaths,
  frontendApiModeIndex,
  frontendApiModeValues,
  frontendApiOperations,
  frontendApiPayloadIndex,
  frontendApiStatusIndex,
  frontendApiStatusValues,
  frontendApiSurfaceIndex,
  frontendApiWorkspaceSectionIndex,
  frontendApiWorkspaceSections,
  getFrontendApiBindingOperationIds,
  getFrontendApiGroupOperationIds,
  getFrontendApiModeOperationIds,
  getFrontendApiPayloadOperationIds,
  getFrontendApiRestOperationIds,
  getFrontendApiSectionOperations,
  getFrontendApiStatusOperationIds,
  getFrontendApiSurfaceOperationIds,
  getFrontendApiWorkspaceSectionOperationIds
} from "./frontendApi";
import type { FrontendApiBindingSurface, FrontendApiOperation } from "./frontendApi";

const frontendApiBindingSurfaces = [
  "sdk",
  "cli",
  "rest",
  "mcp",
  "lsp"
] as const satisfies readonly FrontendApiBindingSurface[];

function restIndexKey(operation: FrontendApiOperation): string | undefined {
  const binding = operation.bindings?.rest;
  if (!binding) {
    return undefined;
  }
  const entries = Object.entries(binding.query ?? {}).sort(([left], [right]) => left.localeCompare(right));
  const query = entries.map(([key, value]) => `${key}=${typeof value === "boolean" ? String(value) : value}`).join("&");
  return query ? `${binding.method} ${binding.path}?${query}` : `${binding.method} ${binding.path}`;
}

describe("frontend API binding index helpers", () => {
  it("exposes the generated binding index without reaching into raw contract JSON", () => {
    expect(frontendApiBindingIndex.cli.project).toEqual(["project.open", "project.view"]);
    expect(frontendApiBindingIndex.rest["GET /projects"]).toEqual(["project.open", "project.view"]);
    expect(frontendApiBindingIndex.mcp.project_inspect).toEqual(
      expect.arrayContaining(["project.inspect", "module.list", "collection.sources", "catalog.query"])
    );
    expect(frontendApiBindingIndex.lsp["textDocument/hover"]).toEqual(["lsp.hover"]);
  });

  it("maps surface call keys to operation ids through a typed helper", () => {
    expect(getFrontendApiBindingOperationIds("cli", "project")).toEqual(["project.open", "project.view"]);
    expect(getFrontendApiBindingOperationIds("mcp", "project_templates")).toEqual(["module.templates"]);
    expect(getFrontendApiBindingOperationIds("lsp", "textDocument/formatting")).toEqual(["lsp.formatting"]);
    expect(getFrontendApiBindingOperationIds("rest", "GET /projects/inspect?kind=modules")).toEqual(["module.list"]);
    expect(getFrontendApiBindingOperationIds("rest", "GET /missing")).toEqual([]);
  });

  it("lists operations by group and implementation status without scanning rows in components", () => {
    expect(frontendApiGroupIndex.projects.slice(0, 5)).toEqual([
      "project.create",
      "project.find",
      "project.open",
      "project.view",
      "project.list"
    ]);
    expect(getFrontendApiGroupOperationIds("lsp")).toEqual([
      "lsp.diagnostics",
      "lsp.symbols",
      "lsp.hover",
      "lsp.formatting",
      "lsp.completion",
      "lsp.semantic_tokens",
      "lsp.keywords"
    ]);
    expect(frontendApiStatusIndex["frontend-local"]).toEqual(["project.activate"]);
    expect(getFrontendApiStatusOperationIds("frontend-local")).toEqual(["project.activate"]);
  });

  it("lists operations by read/write mode without scanning rows in components", () => {
    expect(frontendApiModeValues).toEqual(["read", "write"]);
    expect(frontendApiModeIndex.write.slice(0, 5)).toEqual([
      "project.create",
      "project.config",
      "project.rename",
      "project.language",
      "project.activate"
    ]);
    expect(getFrontendApiModeOperationIds("read").slice(0, 5)).toEqual([
      "project.find",
      "project.open",
      "project.view",
      "project.list",
      "project.inspect"
    ]);
  });

  it("lists operations by surface without scanning bindings in components", () => {
    expect(frontendApiSurfaceIndex.unbound).toEqual(["project.activate"]);
    expect(getFrontendApiSurfaceOperationIds("rest").slice(0, 4)).toEqual([
      "project.create",
      "project.find",
      "project.open",
      "project.view"
    ]);
    expect(getFrontendApiSurfaceOperationIds("mcp")).toEqual(
      expect.arrayContaining(["project.create", "module.file", "collection.edit"])
    );
    expect(getFrontendApiSurfaceOperationIds("lsp")).toEqual([
      "lsp.diagnostics",
      "lsp.symbols",
      "lsp.hover",
      "lsp.formatting",
      "lsp.completion",
      "lsp.semantic_tokens"
    ]);
  });

  it("lists operations by payload schema for renderer dispatch", () => {
    expect(frontendApiPayloadIndex["Project.to_view"]).toEqual(["project.open", "project.view"]);
    expect(getFrontendApiPayloadOperationIds("paradev.build.explain.v1")).toEqual(["module.view", "build.explain"]);
    expect(getFrontendApiPayloadOperationIds("untyped")).toEqual(
      expect.arrayContaining(["project.config", "project.activate", "surface.openapi"])
    );
  });

  it("lists operations by workspace section without scanning workspace rows", () => {
    expect(frontendApiWorkspaceSectionIndex["project-switcher"].slice(0, 4)).toEqual([
      "project.state",
      "project.list",
      "project.find",
      "project.open"
    ]);
    expect(getFrontendApiWorkspaceSectionOperationIds("catalog")).toEqual([
      "catalog.preview",
      "catalog.write",
      "catalog.refresh",
      "catalog.query"
    ]);
    expect(getFrontendApiSectionOperations("surface-contracts").map((operation) => operation.id).slice(0, 3)).toEqual([
      "surface.frontend_api",
      "surface.frontend_api.workspace",
      "surface.frontend_api.action"
    ]);
  });

  it("builds the REST binding lookup endpoint URL through the helper", () => {
    expect(frontendApiEndpointPaths.binding).toBe("/frontend-api/binding");
    expect(buildFrontendApiBindingLookupUrl("rest", "GET /projects/inspect?kind=modules")).toBe(
      "/frontend-api/binding?binding_surface=rest&binding_key=GET+%2Fprojects%2Finspect%3Fkind%3Dmodules"
    );
  });

  it("builds REST index keys from method, path, and sorted query values", () => {
    expect(getFrontendApiRestOperationIds("GET", "/projects")).toEqual(["project.open", "project.view"]);
    expect(getFrontendApiRestOperationIds("GET", "/projects/inspect", { kind: "modules" })).toEqual(["module.list"]);
    expect(getFrontendApiRestOperationIds("POST", "/projects/build", { emit_manifests: true, emit_artifacts: true })).toEqual([
      "build.emit"
    ]);
    expect(getFrontendApiRestOperationIds("POST", "/projects/build", { emit_artifacts: true, emit_manifests: true })).toEqual([
      "build.emit"
    ]);
    expect(getFrontendApiRestOperationIds("POST", "/projects/build", { strict_metadata: true })).toEqual([]);
  });

  it("stays aligned with every generated REST binding row", () => {
    for (const operation of frontendApiOperations) {
      const key = restIndexKey(operation);
      if (!key) {
        continue;
      }
      expect(getFrontendApiBindingOperationIds("rest", key)).toContain(operation.id);
    }
  });

  it("stays aligned with every generated surface binding row", () => {
    for (const surface of frontendApiBindingSurfaces) {
      const expected = frontendApiOperations
        .filter((operation) => Boolean(operation.bindings?.[surface]))
        .map((operation) => operation.id);
      expect(getFrontendApiSurfaceOperationIds(surface)).toEqual(expected);
    }
    expect(getFrontendApiSurfaceOperationIds("unbound")).toEqual(
      frontendApiOperations
        .filter((operation) => !operation.bindings || Object.keys(operation.bindings).length === 0)
        .map((operation) => operation.id)
    );
  });

  it("stays aligned with every generated group and status row", () => {
    for (const groupId of frontendApiGroupIds) {
      const expected = frontendApiOperations.filter((operation) => operation.group === groupId).map((operation) => operation.id);
      expect(getFrontendApiGroupOperationIds(groupId)).toEqual(expected);
    }
    for (const status of frontendApiStatusValues) {
      const expected = frontendApiOperations.filter((operation) => operation.status === status).map((operation) => operation.id);
      expect(getFrontendApiStatusOperationIds(status)).toEqual(expected);
    }
  });

  it("stays aligned with every generated read/write mode row", () => {
    for (const mode of frontendApiModeValues) {
      const expected = frontendApiOperations
        .filter((operation) => (operation.mutates === true ? "write" : "read") === mode)
        .map((operation) => operation.id);
      expect(getFrontendApiModeOperationIds(mode)).toEqual(expected);
    }
  });

  it("stays aligned with every generated payload row", () => {
    const payloads = new Set(frontendApiOperations.map((operation) => operation.payload || "untyped"));
    for (const payload of payloads) {
      const expected = frontendApiOperations
        .filter((operation) => (operation.payload || "untyped") === payload)
        .map((operation) => operation.id);
      expect(getFrontendApiPayloadOperationIds(payload)).toEqual(expected);
    }
  });

  it("stays aligned with every generated workspace section row", () => {
    for (const section of frontendApiWorkspaceSections) {
      expect(getFrontendApiWorkspaceSectionOperationIds(section.id)).toEqual(section.operation_ids);
      expect(getFrontendApiSectionOperations(section.id).map((operation) => operation.id)).toEqual(section.operation_ids);
    }
  });
});
