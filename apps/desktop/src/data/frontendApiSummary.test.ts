import { describe, expect, it } from "vitest";

import {
  frontendApiGroupIds,
  frontendApiGroups,
  frontendApiInputOperations,
  frontendApiModeValues,
  frontendApiOperationIds,
  frontendApiOperations,
  frontendApiRestOperations,
  frontendApiStatusValues,
  frontendApiSummary,
  frontendApiWorkspaceActions,
  frontendApiWorkspaceSectionIds,
  frontendApiWorkspaceSections,
  getFrontendApiDefaultSectionAction,
  getFrontendApiGroupOperationIds,
  getFrontendApiGroupOperations,
  getFrontendApiOperation,
  getFrontendApiSectionActions,
  getFrontendApiSectionOperations
} from "./frontendApi";
import type { FrontendApiBindingSurface, FrontendApiGroupCount, FrontendApiOperation, FrontendApiSurfaceCount } from "./frontendApi";

const frontendApiBindingSurfaces = ["sdk", "cli", "rest", "mcp", "lsp"] as const satisfies readonly FrontendApiBindingSurface[];

function countOperationsByStatus(operations: readonly FrontendApiOperation[]): Record<string, number> {
  return operations.reduce<Record<string, number>>((counts, operation) => {
    counts[operation.status] = (counts[operation.status] ?? 0) + 1;
    return counts;
  }, {});
}

function countOperationsByMode(operations: readonly FrontendApiOperation[]): Record<"read" | "write", number> {
  return operations.reduce<Record<"read" | "write", number>>(
    (counts, operation) => {
      counts[operation.mutates === true ? "write" : "read"] += 1;
      return counts;
    },
    {
      read: 0,
      write: 0
    }
  );
}

function countFrontendApiGroup(operations: readonly FrontendApiOperation[]): FrontendApiGroupCount {
  return {
    operation_count: operations.length,
    ...countOperationsByMode(operations),
    ...countOperationsByStatus(operations)
  };
}

function countFrontendApiSurfaces(operations: readonly FrontendApiOperation[]): FrontendApiSurfaceCount {
  const counts = {
    operation_count: operations.length,
    sdk: 0,
    cli: 0,
    rest: 0,
    mcp: 0,
    lsp: 0,
    unbound: 0
  };
  for (const operation of operations) {
    if (!operation.bindings || Object.keys(operation.bindings).length === 0) {
      counts.unbound += 1;
      continue;
    }
    for (const surface of frontendApiBindingSurfaces) {
      if (operation.bindings[surface]) {
        counts[surface] += 1;
      }
    }
  }
  return counts;
}

describe("frontend API generated summary registry", () => {
  it("keeps generated ids and summary counts aligned with operation rows", () => {
    expect(frontendApiSummary.operation_count).toBe(frontendApiOperations.length);
    expect(frontendApiSummary.group_count).toBe(frontendApiGroups.length);
    expect(frontendApiSummary.workspace_section_count).toBe(frontendApiWorkspaceSections.length);
    expect(frontendApiOperationIds).toEqual(frontendApiOperations.map((operation) => operation.id));
    expect(frontendApiGroupIds).toEqual(frontendApiGroups.map((group) => group.id));
    expect(frontendApiWorkspaceSectionIds).toEqual(frontendApiWorkspaceSections.map((section) => section.id));
    expect(frontendApiStatusValues).toEqual(["frontend-local", "implemented"]);
    expect(frontendApiModeValues).toEqual(["read", "write"]);

    expect(frontendApiSummary.status_counts).toEqual(countOperationsByStatus(frontendApiOperations));
    expect(frontendApiSummary.mode_counts).toEqual(countOperationsByMode(frontendApiOperations));
    expect(frontendApiSummary.surface_counts).toEqual(countFrontendApiSurfaces(frontendApiOperations));
    expect(frontendApiSummary.group_counts).toEqual(
      Object.fromEntries(frontendApiGroups.map((group) => [group.id, countFrontendApiGroup(getFrontendApiGroupOperations(group.id))]))
    );
    expect(frontendApiSummary.group_surface_counts).toEqual(
      Object.fromEntries(frontendApiGroups.map((group) => [group.id, countFrontendApiSurfaces(getFrontendApiGroupOperations(group.id))]))
    );

    for (const group of frontendApiGroups) {
      expect(group.operation_count).toBe(getFrontendApiGroupOperations(group.id).length);
      expect(getFrontendApiGroupOperations(group.id).map((operation) => operation.id)).toEqual(
        getFrontendApiGroupOperationIds(group.id)
      );
      expect(frontendApiSummary.group_counts[group.id]?.operation_count).toBe(group.operation_count);
      expect(frontendApiSummary.group_surface_counts[group.id]?.operation_count).toBe(group.operation_count);
    }
  });

  it("keeps required frontend-facing operation families present", () => {
    expect(frontendApiGroupIds).toEqual([
      "projects",
      "modules",
      "collections",
      "localization",
      "build",
      "pdx",
      "lsp",
      "catalog",
      "ai",
      "surfaces"
    ]);
    expect(frontendApiOperationIds).toEqual(
      expect.arrayContaining([
        "project.create",
        "project.find",
        "project.rename",
        "project.activate",
        "project.view",
        "module.list",
        "module.create",
        "module.edit",
        "module.view",
        "collection.create",
        "collection.edit",
        "localization.workspace",
        "localization.plan",
        "build.plan",
        "build.emit",
        "pdx.parse",
        "pdx.format",
        "lsp.diagnostics",
        "lsp.hover",
        "lsp.formatting",
        "ai.chat",
        "surface.frontend_api.action",
        "surface.frontend_api.options",
        "surface.frontend_api.normalize",
        "surface.frontend_api.rest_request",
        "surface.frontend_api.binding_lookup"
      ])
    );
  });

  it("keeps workspace section helpers tied to generated sections", () => {
    expect(frontendApiWorkspaceActions).toEqual(frontendApiWorkspaceSections.flatMap((section) => section.actions));

    for (const section of frontendApiWorkspaceSections) {
      expect(getFrontendApiSectionActions(section.id)).toEqual(section.actions);
      expect(getFrontendApiSectionOperations(section.id).map((operation) => operation.id)).toEqual(section.operation_ids);

      if (section.default_operation_id) {
        expect(getFrontendApiDefaultSectionAction(section.id).operation_id).toBe(section.default_operation_id);
      }

      for (const action of section.actions) {
        const operation = getFrontendApiOperation(action.operation_id);
        expect(section.operation_ids).toContain(action.operation_id);
        expect(action.group).toBe(operation.group);
        expect(action.status).toBe(operation.status);
      }
    }
  });

  it("keeps derived TypeScript helper slices aligned with operation bindings", () => {
    expect(frontendApiInputOperations).toEqual(frontendApiOperations.filter((operation) => Boolean(operation.inputs?.length)));
    expect(frontendApiRestOperations).toEqual(frontendApiOperations.filter((operation) => Boolean(operation.bindings?.rest)));
    expect(frontendApiRestOperations.map((operation) => operation.id)).toEqual(
      expect.arrayContaining([
        "project.find",
        "module.create",
        "collection.create",
        "build.plan",
        "pdx.parse",
        "lsp.diagnostics",
        "catalog.write"
      ])
    );
  });
});
