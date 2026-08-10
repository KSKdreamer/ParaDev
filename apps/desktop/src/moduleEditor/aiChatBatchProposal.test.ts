import { describe, expect, it } from "vitest";
import { createTranslator } from "../i18n";
import type {
  CollectionScaffoldPayload,
  ModuleCreateBatchPayload,
  ParaDevAiChatCollectionScaffoldProposal,
  ParaDevAiChatModuleBatchProposal,
  ParaDevAiChatSourceFormUpdateProposal
} from "../services/paradev";
import type { ProjectTemplatesPayload } from "../types";
import {
  prepareAiChatCollectionReview,
  prepareAiChatModuleBatchReview,
  prepareAiChatSourceUpdateReview
} from "./aiChatBatchProposal";

const projectRoot = "/workspace/PIHC3";
const sourceRoot = "/workspace/PIHC3/src";
const values = [0.02, 0.05, 0.08, 0.12, 0.16];
const requests = values.map((cic, index) => ({
  template_id: "pihc3:idea/basic",
  object_id: String.fromCharCode(65 + index),
  values: { cic, title: String.fromCharCode(65 + index) }
}));
const plan: ModuleCreateBatchPayload = {
  schema: "paradev.sdk.module_batch.v1",
  project_id: "PIHC3",
  source_root: sourceRoot,
  plan_hash: "a".repeat(64),
  blocked: false,
  applied: false,
  written: false,
  requested_count: 5,
  counts: { create: 5, created: 0, unchanged: 0, blocked: 0 },
  diagnostics: [],
  modules: requests.map((request, index) => ({
    index,
    template_id: request.template_id,
    object_id: request.object_id,
    family: "idea",
    module_id: `idea/${request.object_id}`,
    root: `${sourceRoot}/modules/idea/${request.object_id}`,
    status: "create",
    blocked: false,
    diagnostics: [],
    files: []
  }))
};
const proposal: ParaDevAiChatModuleBatchProposal = {
  schema: "paradev.desktop.ai-chat-proposal.v1",
  operationId: "module.create_batch",
  familyId: "idea",
  sourceRoot,
  requests,
  plan
};
const templates: ProjectTemplatesPayload = {
  schema: "paradev.sdk.templates.v1",
  project_id: "PIHC3",
  profile: "hoi4",
  source_roots: [
    { path: sourceRoot, relative_path: "src", default: true }
  ],
  templates: [
    {
      id: "pihc3:idea/basic",
      title: "PIHC3 idea",
      family: "idea",
      family_id: "ideas",
      source: "project",
      authoring_ready: true,
      args: {
        title: { required: true, default: "", advanced: false },
        cic: { required: true, default: "0", advanced: false, type: "number" }
      },
      files: ["meta.yaml", "idea.json", "locs.txt"]
    },
    {
      id: "pihc3:focus-tree/basic",
      title: "PIHC3 focus tree",
      family: "focus",
      family_id: "focuses",
      kind: "collection",
      source: "project",
      authoring_ready: true,
      args: {
        country_tag: { required: true, default: "", advanced: false },
        title: { required: true, default: "", advanced: false },
        continuous_focus_y: {
          required: false,
          default: "2400",
          advanced: true,
          type: "number"
        }
      },
      files: ["tree.txt"]
    }
  ]
};

const collectionPlan: CollectionScaffoldPayload = {
  schema: "paradev.sdk.collection_scaffold.v1",
  project_id: "PIHC3",
  template_id: "pihc3:focus-tree/basic",
  kind: "collection",
  family: "focus",
  object_id: "C99_AI_REVIEW",
  collection_id: "C99_AI_REVIEW",
  folder_name: "C99_AI_REVIEW - AI Review Tree",
  source_root: sourceRoot,
  root: `${sourceRoot}/collections/focus/C99_AI_REVIEW - AI Review Tree`,
  values: {
    country_tag: "C99",
    title: "AI Review Tree",
    continuous_focus_y: "2500"
  },
  blocked: false,
  written: false,
  plan_hash: "b".repeat(64),
  diagnostics: [],
  files: [],
  authoring_plan: {}
};
const collectionProposal: ParaDevAiChatCollectionScaffoldProposal = {
  schema: "paradev.desktop.ai-chat-proposal.v1",
  operationId: "collection.scaffold",
  familyId: "focus",
  sourceRoot,
  request: {
    template_id: "pihc3:focus-tree/basic",
    collection_id: "C99_AI_REVIEW",
    values: {
      country_tag: "C99",
      title: "AI Review Tree",
      continuous_focus_y: "2500"
    }
  },
  plan: collectionPlan
};
const sourceUpdatePath = "src/modules/idea/IDEA_ALPHA/def.txt";
const sourceUpdateProposal: ParaDevAiChatSourceFormUpdateProposal = {
  schema: "paradev.desktop.ai-chat-proposal.v1",
  operationId: "module.source_form_update_batch",
  familyId: "idea",
  requests: [
    {
      source_path: sourceUpdatePath,
      module_id: "idea/IDEA_ALPHA",
      values: { "pdx-control-002": 2 },
      control_labels: {
        "pdx-control-002": {
          default: "Country resource crystals",
          zh: "国家水晶资源"
        }
      }
    }
  ],
  plan: {
    schema: "paradev.source-form-update-batch.v1",
    projectId: "PIHC3",
    changed: true,
    counts: { requested: 1, changed: 1, unchanged: 0 },
    updates: [
      {
        schema: "paradev.source-form-update.v1",
        projectId: "PIHC3",
        family: "idea",
        moduleId: "idea/IDEA_ALPHA",
        path: `${projectRoot}/${sourceUpdatePath}`,
        relativePath: sourceUpdatePath,
        sourceFormat: "pdx",
        formContract: "paradev.pdx.guided-form.v1",
        changed: true,
        changes: [
          { controlId: "pdx-control-002", previous: 1, value: 2 }
        ],
        sourceEdit: {
          path: `${projectRoot}/${sourceUpdatePath}`,
          text: "modifier = { local_resources = 2 }\n",
          expectedSize: 34,
          expectedMtimeNs: "1770000000123456789"
        }
      }
    ],
    sourceEdits: [
      {
        path: `${projectRoot}/${sourceUpdatePath}`,
        text: "modifier = { local_resources = 2 }\n",
        expectedSize: 34,
        expectedMtimeNs: "1770000000123456789"
      }
    ]
  }
};

describe("prepareAiChatModuleBatchReview", () => {
  it("retains the exact typed A-E dry plan while preparing editable strings", () => {
    const prepared = prepareAiChatModuleBatchReview({
      activeProjectId: "PIHC3",
      activeProjectRoot: projectRoot,
      proposal,
      proposalProjectRoot: projectRoot,
      t: createTranslator("en"),
      templates
    });

    expect(prepared.familyId).toBe("ideas");
    expect(prepared.state.rows.map((row) => row.objectId)).toEqual([
      "A",
      "B",
      "C",
      "D",
      "E"
    ]);
    expect(prepared.state.rows.map((row) => row.values.cic)).toEqual([
      "0.02",
      "0.05",
      "0.08",
      "0.12",
      "0.16"
    ]);
    expect(prepared.state.preview?.modules).toEqual(requests);
    expect(prepared.state.preview?.plan).toBe(plan);
    expect(prepared.state.preview?.sourceRoot).toBe(sourceRoot);
  });

  it("rejects a plan after the active project changes", () => {
    expect(() =>
      prepareAiChatModuleBatchReview({
        activeProjectId: "OTHER",
        activeProjectRoot: "/workspace/OTHER",
        proposal,
        proposalProjectRoot: projectRoot,
        t: createTranslator("en"),
        templates
      })
    ).toThrow("This plan belongs to a different project");
  });

  it("rejects a proposal whose template is no longer authoring-ready", () => {
    expect(() =>
      prepareAiChatModuleBatchReview({
        activeProjectId: "PIHC3",
        activeProjectRoot: projectRoot,
        proposal,
        proposalProjectRoot: projectRoot,
        t: createTranslator("en"),
        templates: {
          ...templates,
          templates: templates.templates.map((template) => ({
            ...template,
            authoring_ready: false
          }))
        }
      })
    ).toThrow("The project templates changed");
  });
});

describe("prepareAiChatCollectionReview", () => {
  it("retains the exact collection dry plan in the regular scaffold dialog", () => {
    const prepared = prepareAiChatCollectionReview({
      activeProjectId: "PIHC3",
      activeProjectRoot: projectRoot,
      proposal: collectionProposal,
      proposalProjectRoot: projectRoot,
      t: createTranslator("en"),
      templates
    });

    expect(prepared.familyId).toBe("focuses");
    expect(prepared.state).toMatchObject({
      open: true,
      templateId: "pihc3:focus-tree/basic",
      collectionId: "C99_AI_REVIEW",
      sourceRoot,
      showAdvanced: true,
      values: {
        country_tag: "C99",
        title: "AI Review Tree",
        continuous_focus_y: "2500"
      }
    });
    expect(prepared.state.preview?.plan).toBe(collectionPlan);
    expect(prepared.state.preview?.request).toEqual({
      projectRoot,
      templateId: "pihc3:focus-tree/basic",
      collectionId: "C99_AI_REVIEW",
      values: collectionProposal.request.values,
      sourceRoot,
      force: false
    });
  });

  it("rejects a collection template that is no longer authoring-ready", () => {
    expect(() =>
      prepareAiChatCollectionReview({
        activeProjectId: "PIHC3",
        activeProjectRoot: projectRoot,
        proposal: collectionProposal,
        proposalProjectRoot: projectRoot,
        t: createTranslator("en"),
        templates: {
          ...templates,
          templates: templates.templates.map((template) =>
            template.id === "pihc3:focus-tree/basic"
              ? { ...template, authoring_ready: false }
              : template
          )
        }
      })
    ).toThrow("The project collection templates changed");
  });
});

describe("prepareAiChatSourceUpdateReview", () => {
  it("retains the exact Registry-owned dry plan for explicit review", () => {
    const prepared = prepareAiChatSourceUpdateReview({
      activeProjectId: "PIHC3",
      activeProjectRoot: projectRoot,
      proposal: sourceUpdateProposal,
      proposalProjectRoot: projectRoot,
      t: createTranslator("en")
    });

    expect(prepared.familyId).toBe("idea");
    expect(prepared.state).toEqual({
      open: true,
      requests: sourceUpdateProposal.requests,
      plan: sourceUpdateProposal.plan
    });
  });

  it("rejects a stale control identity before opening the review", () => {
    expect(() =>
      prepareAiChatSourceUpdateReview({
        activeProjectId: "PIHC3",
        activeProjectRoot: projectRoot,
        proposal: {
          ...sourceUpdateProposal,
          requests: [
            {
              ...sourceUpdateProposal.requests[0],
              values: { "pdx-control-999": 2 }
            }
          ]
        },
        proposalProjectRoot: projectRoot,
        t: createTranslator("en")
      })
    ).toThrow("The selected source or its Guided controls changed");
  });
});
