import { describe, expect, it } from "vitest";
import type { ModuleDiagramPayload } from "../services/paradev";
import type {
  ProjectBrowserPayload,
  ProjectDiagramRelationship,
} from "../types";
import { setDiagramRelationship } from "./diagramRelationships";
import {
  buildMioDiagramDocument,
  changedMioDiagramNodeIds,
  mioDiagramEditIntents,
  mioDiagramNodeEditable,
  mioDiagramOrganizationOptions,
  mioDiagramSourcePath,
  MIO_DIAGRAM_GRID_SIZE_PX,
} from "./mioDiagram";
import {
  moveDiagramNode,
  resolveDiagramLayout,
  setDiagramDependencyEdge,
} from "./layoutModel";

const projectRoot = "/workspace/projects/PIHC3";
const family = "military_industrial_organization";
const revision = `sha256:${"a".repeat(64)}`;

const browser: ProjectBrowserPayload = {
  schema: "paradev.sdk.project-browser.v1",
  project_id: "PIHC3",
  title: "The Pony In The High Castle",
  root: projectRoot,
  profile: "hoi4",
  filters: { family },
  diagnostics: [],
  families: [
    {
      id: "military-industrial-organization-component",
      family,
      title: "Military Industrial Organization",
      visible: true,
      item_count: 2,
      source_count: 2,
      layouts: ["canonical"],
    },
  ],
  items: [mioBrowserItem("mio/C01", "C01"), mioBrowserItem("mio/C02", "C02")],
};

const payload: ModuleDiagramPayload = {
  schema: "paradev.sdk.module_diagram.v1",
  provider_schema: "paradev.hoi4.mio-trait-diagram-projection.v1",
  project_id: "PIHC3",
  project_root: projectRoot,
  profile: "hoi4",
  family,
  source_kind: "module_pdx_source",
  editable: true,
  module_ids: ["mio/C01", "mio/C02"],
  organizations: [
    {
      id: "C01_ORG",
      organization_id: "C01_ORG",
      module_id: "mio/C01",
      name_key: "C01_ORG_NAME",
      localized_titles: {
        l_english: "Canterlot Works",
        l_simp_chinese: "坎特洛特工厂",
      },
    },
    {
      id: "C02_ORG",
      organization_id: "C02_ORG",
      module_id: "mio/C02",
      name_key: "C02_ORG_NAME",
      localized_titles: {
        l_english: "Crystal Works",
      },
    },
  ],
  nodes: [
    {
      id: "C02_ORG::trait::CHILD",
      kind: "trait",
      module_id: "mio/C02",
      organization_id: "C02_ORG",
      trait_id: "CHILD",
      name_key: "C02_CHILD",
      localized_titles: { l_english: "Crystal child" },
      position: { x: 0, y: 1 },
      source_path: "src/modules/military_industrial_organization/C02/def.txt",
      source_revision: revision,
      editable: true,
    },
    {
      id: "C01_ORG::trait::ROOT",
      kind: "trait",
      module_id: "mio/C01",
      organization_id: "C01_ORG",
      trait_id: "ROOT",
      name_key: "C01_ROOT",
      localized_titles: {
        l_english: "Root trait",
        l_simp_chinese: "根特质",
      },
      position: { x: 0, y: 0 },
      source_path: "src/modules/military_industrial_organization/C01/def.txt",
      source_revision: revision,
      editable: true,
    },
    {
      id: "C01_ORG::trait::CHILD",
      kind: "trait",
      module_id: "mio/C01",
      organization_id: "C01_ORG",
      trait_id: "CHILD",
      name_key: "C01_CHILD",
      localized_titles: {
        l_english: "Child trait",
        l_simp_chinese: "子特质",
      },
      token: "CHILD",
      icon: "GFX_C01_CHILD",
      position: { x: 1, y: 1 },
      source_path: "src/modules/military_industrial_organization/C01/def.txt",
      source_revision: revision,
      editable: true,
    },
    {
      id: "C01_ORG::initial_trait::START",
      kind: "initial_trait",
      module_id: "mio/C01",
      organization_id: "C01_ORG",
      trait_id: "START",
      name_key: "C01_START",
      localized_titles: { l_english: "Initial designer" },
      source_path: "src/modules/military_industrial_organization/C01/def.txt",
      source_revision: revision,
      editable: false,
    },
    {
      id: "C01_ORG::trait::ALT",
      kind: "trait",
      module_id: "mio/C01",
      organization_id: "C01_ORG",
      trait_id: "ALT",
      name_key: "C01_ALT",
      localized_titles: { l_english: "Alternative trait" },
      position: { x: -1, y: 1 },
      source_path: "src/modules/military_industrial_organization/C01/def.txt",
      source_revision: revision,
      editable: true,
    },
    {
      id: "C02_ORG::trait::ROOT",
      kind: "trait",
      module_id: "mio/C02",
      organization_id: "C02_ORG",
      trait_id: "ROOT",
      name_key: "C02_ROOT",
      localized_titles: { l_english: "Crystal root" },
      position: { x: 0, y: 0 },
      source_path: "src/modules/military_industrial_organization/C02/def.txt",
      source_revision: revision,
      editable: true,
    },
  ],
  edges: [
    mioEdge(
      "relative_position",
      "C01_ORG::trait::ROOT",
      "C01_ORG::trait::CHILD",
    ),
    mioEdge(
      "all_parent",
      "C01_ORG::trait::ROOT",
      "C01_ORG::trait::CHILD",
      [0, 1],
    ),
    mioEdge("any_parent", "C01_ORG::trait::ROOT", "C01_ORG::trait::CHILD", [1]),
    mioEdge(
      "mutually_exclusive",
      "C01_ORG::trait::ALT",
      "C01_ORG::trait::CHILD",
    ),
    mioEdge(
      "relative_position",
      "C02_ORG::trait::ROOT",
      "C02_ORG::trait::CHILD",
    ),
  ],
  diagnostics: [],
  summary: {
    organization_count: 2,
    trait_count: 6,
    edge_count: 5,
    edge_counts: {
      all_parent: 1,
      any_parent: 1,
      mutually_exclusive: 1,
      relative_position: 2,
    },
  },
};

describe("MIO diagram adapter", () => {
  it("maps exact MIO traits into a deterministic multi-organization canvas", () => {
    const document = buildMioDiagramDocument(payload, browser, "en");
    const resolved = resolveDiagramLayout(document);

    expect(document.gridSizePx).toBe(MIO_DIAGRAM_GRID_SIZE_PX);
    expect(document.nodes.map((node) => node.id)).toEqual([
      "C01_ORG::initial_trait::START",
      "C01_ORG::trait::ALT",
      "C01_ORG::trait::CHILD",
      "C01_ORG::trait::ROOT",
      "C02_ORG::trait::CHILD",
      "C02_ORG::trait::ROOT",
    ]);
    expect(
      document.nodes.find((node) => node.id === "C01_ORG::trait::CHILD"),
    ).toMatchObject({
      mode: "relative",
      parentId: "C01_ORG::trait::ROOT",
      dx: 1,
      dy: 1,
      title: "Child trait",
      payload: {
        familyId: "military-industrial-organizations",
        family,
        itemId: "module:mio/C01",
        moduleId: "mio/C01",
        objectId: "C01",
        organizationId: "C01_ORG",
        organizationTitle: "Canterlot Works",
        traitKind: "trait",
        traitId: "CHILD",
        sourceRevision: revision,
        editable: true,
        sourcePath: "src/modules/military_industrial_organization/C01/def.txt",
        token: "CHILD",
        icon: "GFX_C01_CHILD",
      },
    });
    expect(resolved.nodesById["C01_ORG::trait::CHILD"]).toMatchObject({
      worldX: 2,
      worldY: 1,
    });
    const c01MaximumX = Math.max(
      ...resolved.nodes
        .filter((node) => node.id.startsWith("C01_ORG::"))
        .map((node) => node.worldX),
    );
    const c02MinimumX = Math.min(
      ...resolved.nodes
        .filter((node) => node.id.startsWith("C02_ORG::"))
        .map((node) => node.worldX),
    );
    expect(c02MinimumX).toBeGreaterThan(c01MaximumX);
    expect(document.edges).toEqual([
      {
        id: "relative_position:C01_ORG::trait::ROOT->C01_ORG::trait::CHILD",
        kind: "tree",
        label: "Relative position",
        relationshipKind: "relative_position",
        source: "C01_ORG::trait::ROOT",
        target: "C01_ORG::trait::CHILD",
      },
      {
        id: "relative_position:C02_ORG::trait::ROOT->C02_ORG::trait::CHILD",
        kind: "tree",
        label: "Relative position",
        relationshipKind: "relative_position",
        source: "C02_ORG::trait::ROOT",
        target: "C02_ORG::trait::CHILD",
      },
      {
        id: "all_parent:C01_ORG::trait::ROOT->C01_ORG::trait::CHILD",
        kind: "dependency",
        label: "All parents · groups 1, 2",
        relationshipKind: "all_parent",
        relationshipGroups: [
          {
            groupIndex: 0,
            ownerId: "C01_ORG::trait::CHILD",
          },
          {
            groupIndex: 1,
            ownerId: "C01_ORG::trait::CHILD",
          },
        ],
        source: "C01_ORG::trait::ROOT",
        target: "C01_ORG::trait::CHILD",
      },
      {
        id: "any_parent:C01_ORG::trait::ROOT->C01_ORG::trait::CHILD",
        kind: "dependency",
        label: "Any parent · group 2",
        relationshipKind: "any_parent",
        relationshipGroups: [
          {
            groupIndex: 1,
            ownerId: "C01_ORG::trait::CHILD",
          },
        ],
        source: "C01_ORG::trait::ROOT",
        target: "C01_ORG::trait::CHILD",
      },
      {
        id: "mutually_exclusive:C01_ORG::trait::ALT->C01_ORG::trait::CHILD",
        kind: "reference",
        label: "Mutually exclusive",
        relationshipKind: "mutually_exclusive",
        source: "C01_ORG::trait::ALT",
        target: "C01_ORG::trait::CHILD",
      },
    ]);
  });

  it("uses the requested localization without changing graph identity", () => {
    const document = buildMioDiagramDocument(payload, browser, "zh");
    const child = document.nodes.find(
      (node) => node.id === "C01_ORG::trait::CHILD",
    );

    expect(child?.title).toBe("子特质");
    expect(child?.payload).toMatchObject({
      organizationId: "C01_ORG",
      organizationTitle: "坎特洛特工厂",
    });
  });

  it("offers localized module-owned organization scopes and projects one scope", () => {
    expect(mioDiagramOrganizationOptions(payload, "en", "mio/C01")).toEqual([
      {
        id: "C01_ORG",
        moduleId: "mio/C01",
        title: "Canterlot Works",
      },
    ]);
    expect(mioDiagramOrganizationOptions(payload, "zh")).toEqual([
      {
        id: "C01_ORG",
        moduleId: "mio/C01",
        title: "坎特洛特工厂",
      },
      {
        id: "C02_ORG",
        moduleId: "mio/C02",
        title: "Crystal Works",
      },
    ]);

    const document = buildMioDiagramDocument(payload, browser, "en", "C01_ORG");
    expect(
      new Set(
        document.nodes.map((node) =>
          String((node.payload as { organizationId?: string }).organizationId),
        ),
      ),
    ).toEqual(new Set(["C01_ORG"]));
    expect(document.nodes).toHaveLength(4);
    expect(document.edges).toHaveLength(4);

    const withMetadataOnlyOrganization: ModuleDiagramPayload = {
      ...payload,
      organizations: [
        ...(payload.organizations ?? []),
        {
          id: "DEBUG_EMPTY",
          organization_id: "DEBUG_EMPTY",
          module_id: "mio/DEBUG",
          name_key: "DEBUG_EMPTY_NAME",
          localized_titles: {
            l_english: "Debug organization",
          },
        },
      ],
    };
    expect(
      mioDiagramOrganizationOptions(
        withMetadataOnlyOrganization,
        "en",
        "mio/DEBUG",
      ),
    ).toEqual([]);
    expect(
      mioDiagramOrganizationOptions(
        withMetadataOnlyOrganization,
        "en",
        "mio/POLICIES",
      ),
    ).toEqual([]);
    expect(
      buildMioDiagramDocument(
        withMetadataOnlyOrganization,
        browser,
        "en",
        "DEBUG_EMPTY",
      ),
    ).toEqual({
      schemaVersion: 1,
      gridSizePx: MIO_DIAGRAM_GRID_SIZE_PX,
      nodes: [],
      edges: [],
    });
    expect(() =>
      buildMioDiagramDocument(payload, browser, "en", "MISSING_ORG"),
    ).toThrow(/not present/);
  });

  it("rejects metadata or editable payloads instead of inventing a fallback", () => {
    expect(() =>
      buildMioDiagramDocument(
        {
          ...payload,
          provider_schema: "paradev.metadata.mio.v1",
        },
        browser,
        "en",
      ),
    ).toThrow(/authoritative exact-source provider/);
    expect(() =>
      buildMioDiagramDocument(
        { ...payload, source_kind: "compiled_pdx" },
        browser,
        "en",
      ),
    ).toThrow(/authoritative exact-source provider/);
  });

  it("emits organization-scoped source intents for exact position drags", () => {
    const base = buildMioDiagramDocument(payload, browser, "en");
    const draft = moveDiagramNode(base, "C01_ORG::trait::CHILD", {
      dx: 2,
      dy: -1,
    });

    expect(mioDiagramEditIntents(payload, base, draft)).toEqual({
      positionIntents: [
        {
          organization_id: "C01_ORG",
          trait_id: "CHILD",
          x: 3,
          y: 0,
          source_revision: revision,
        },
      ],
      edgeIntents: [],
    });
    expect(changedMioDiagramNodeIds(payload, base, draft)).toEqual([
      "C01_ORG::trait::CHILD",
    ]);
    expect(mioDiagramSourcePath(base, "C01_ORG::trait::CHILD")).toBe(
      "src/modules/military_industrial_organization/C01/def.txt",
    );
    expect(mioDiagramNodeEditable(base, "C01_ORG::trait::CHILD")).toBe(true);
    expect(mioDiagramNodeEditable(base, "C01_ORG::initial_trait::START")).toBe(
      false,
    );
  });

  it("converts packed root positions back to exact source coordinates", () => {
    const base = buildMioDiagramDocument(payload, browser, "en");
    const draft = moveDiagramNode(base, "C01_ORG::trait::ROOT", {
      dx: 2,
      dy: 1,
    });

    expect(mioDiagramEditIntents(payload, base, draft).positionIntents).toEqual(
      [
        {
          organization_id: "C01_ORG",
          trait_id: "ROOT",
          x: 2,
          y: 1,
          source_revision: revision,
        },
      ],
    );
  });

  it("emits reviewed organization-scoped relationship intents", () => {
    const base = buildMioDiagramDocument(payload, browser, "en");
    const relationship: ProjectDiagramRelationship = {
      cardinality: "many",
      kind: "any_parent",
      label: "Any parent",
      owner_endpoint: "target",
      selected_endpoint: "target",
      symmetric: false,
      visual_kind: "dependency",
    };
    const draft = setDiagramRelationship(
      base,
      relationship,
      "C01_ORG::trait::ALT",
      "C01_ORG::trait::ROOT",
      true,
    );

    expect(mioDiagramEditIntents(payload, base, draft)).toEqual({
      positionIntents: [],
      edgeIntents: [
        {
          kind: "any_parent",
          organization_id: "C01_ORG",
          present: true,
          source_id: "ROOT",
          source_revision: revision,
          target_id: "ALT",
        },
      ],
    });
    expect(changedMioDiagramNodeIds(payload, base, draft)).toEqual([
      "C01_ORG::trait::ALT",
      "C01_ORG::trait::ROOT",
    ]);
  });

  it("blocks ambiguous node and generic relationship edits", () => {
    const base = buildMioDiagramDocument(payload, browser, "en");
    const movedInitial = moveDiagramNode(
      base,
      "C01_ORG::initial_trait::START",
      { dx: 1, dy: 0 },
    );
    expect(() => mioDiagramEditIntents(payload, base, movedInitial)).toThrow(
      /no unambiguous editable source position/,
    );

    const withGenericEdge = setDiagramDependencyEdge(
      base,
      "C01_ORG::trait::ALT",
      "C01_ORG::trait::ROOT",
      true,
    );
    expect(() => mioDiagramEditIntents(payload, base, withGenericEdge)).toThrow(
      /provider-declared reviewed relationship action/,
    );
  });
});

function mioBrowserItem(moduleId: string, objectId: string) {
  const relativeRoot = `src/modules/military_industrial_organization/${objectId}`;
  return {
    id: `module:${moduleId}`,
    kind: "module" as const,
    layout: "canonical" as const,
    family_id: "military-industrial-organizations",
    family,
    object_id: objectId,
    module_id: moduleId,
    title: objectId,
    root: `${projectRoot}/${relativeRoot}`,
    relative_root: relativeRoot,
    source_root: `${projectRoot}/src`,
    source_count: 1,
    sources: [
      {
        slot: "pdx",
        name: "def.txt",
        path: `${projectRoot}/${relativeRoot}/def.txt`,
        relative_path: `${relativeRoot}/def.txt`,
        extension: "txt",
      },
    ],
  };
}

function mioEdge(
  kind:
    "relative_position" | "any_parent" | "all_parent" | "mutually_exclusive",
  source: string,
  target: string,
  groupIndices: number[] = [],
) {
  return {
    id: `${kind}:${source}->${target}`,
    kind,
    organization_id: source.split("::")[0],
    ...(groupIndices.length > 0
      ? {
          relation_groups: groupIndices.map((groupIndex) => ({
            owner_id: target,
            group_index: groupIndex,
          })),
        }
      : {}),
    source,
    target,
  };
}
