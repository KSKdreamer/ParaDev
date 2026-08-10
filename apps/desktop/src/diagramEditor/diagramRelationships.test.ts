import { describe, expect, it } from "vitest";
import type { ProjectDiagramRelationship } from "../types";
import {
  diagramRelationshipCycleCandidateIds,
  diagramRelationshipRelatedNodeIds,
  setDiagramRelationship,
} from "./diagramRelationships";
import type { DiagramDocument } from "./layoutModel";

const anyParent: ProjectDiagramRelationship = {
  cardinality: "many",
  kind: "any_parent",
  label: "Any parent",
  owner_endpoint: "target",
  selected_endpoint: "target",
  symmetric: false,
  visual_kind: "dependency",
};

const document: DiagramDocument = {
  edges: [],
  gridSizePx: 48,
  nodes: ["ROOT", "CHILD", "ALT"].map((id, order) => ({
    height: 1,
    id,
    mode: "auto" as const,
    order,
    payload: { family: "demo", projectId: "PIHC3" },
    width: 1,
  })),
  schemaVersion: 1,
};

describe("provider-declared diagram relationships", () => {
  it("adds and removes an open relationship kind without family dispatch", () => {
    const added = setDiagramRelationship(
      document,
      anyParent,
      "CHILD",
      "ROOT",
      true,
    );

    expect(added.edges).toEqual([
      {
        id: "any_parent:ROOT->CHILD",
        kind: "dependency",
        label: "Any parent",
        relationshipKind: "any_parent",
        source: "ROOT",
        target: "CHILD",
      },
    ]);
    expect(
      diagramRelationshipRelatedNodeIds(added, anyParent, "CHILD"),
    ).toEqual(["ROOT"]);
    expect(
      setDiagramRelationship(added, anyParent, "CHILD", "ROOT", false),
    ).toEqual(document);
  });

  it("replaces single-cardinality edges and canonicalizes symmetric pairs", () => {
    const relativeParent: ProjectDiagramRelationship = {
      ...anyParent,
      cardinality: "one",
      kind: "relative_position",
      label: "Relative-position parent",
      visual_kind: "tree",
    };
    const first = setDiagramRelationship(
      document,
      relativeParent,
      "CHILD",
      "ROOT",
      true,
    );
    const replaced = setDiagramRelationship(
      first,
      relativeParent,
      "CHILD",
      "ALT",
      true,
    );
    expect(replaced.edges.map((edge) => edge.id)).toEqual([
      "relative_position:ALT->CHILD",
    ]);

    const exclusive: ProjectDiagramRelationship = {
      ...anyParent,
      kind: "mutually_exclusive",
      label: "Mutually exclusive",
      owner_endpoint: "source",
      selected_endpoint: "source",
      symmetric: true,
      visual_kind: "reference",
    };
    const symmetric = setDiagramRelationship(
      document,
      exclusive,
      "ROOT",
      "ALT",
      true,
    );
    expect(symmetric.edges[0]).toMatchObject({
      id: "mutually_exclusive:ALT->ROOT",
      source: "ALT",
      target: "ROOT",
    });
    expect(
      diagramRelationshipRelatedNodeIds(symmetric, exclusive, "ROOT"),
    ).toEqual(["ALT"]);
  });

  it("fails closed across relationship scopes and blocks directed cycles", () => {
    const scoped: DiagramDocument = {
      ...document,
      nodes: document.nodes.map((node) =>
        node.id === "ALT"
          ? { ...node, payload: { family: "other", projectId: "PIHC3" } }
          : node,
      ),
    };
    expect(
      setDiagramRelationship(scoped, anyParent, "CHILD", "ALT", true),
    ).toBe(scoped);

    const chained = setDiagramRelationship(
      setDiagramRelationship(document, anyParent, "CHILD", "ROOT", true),
      anyParent,
      "ALT",
      "CHILD",
      true,
    );
    expect(
      diagramRelationshipCycleCandidateIds(chained, anyParent, "ROOT"),
    ).toEqual(["CHILD", "ALT"]);
  });
});
