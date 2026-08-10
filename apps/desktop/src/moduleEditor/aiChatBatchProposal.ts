import type { Translator } from "../i18n";
import { canonicalFamilyId } from "../projectModules";
import type {
  ParaDevAiChatCollectionScaffoldProposal,
  ParaDevAiChatModuleBatchProposal,
  ParaDevAiChatSourceFormUpdateProposal
} from "../services/paradev";
import type { ProjectTemplatesPayload } from "../types";
import type {
  ModuleEditorBatchCreateState,
  ModuleEditorCollectionCreateState,
  ModuleEditorSourceUpdateState
} from "./editorSessionStore";
import {
  selectCollectionCreateTemplates,
  selectCreateTemplates
} from "./model";

export type PreparedAiChatModuleBatchReview = {
  familyId: string;
  state: ModuleEditorBatchCreateState;
};

export type PreparedAiChatCollectionReview = {
  familyId: string;
  state: ModuleEditorCollectionCreateState;
};

export type PreparedAiChatSourceUpdateReview = {
  familyId: string;
  state: ModuleEditorSourceUpdateState;
};

type PrepareAiChatModuleBatchReviewInput = {
  activeProjectId: string;
  activeProjectRoot: string;
  proposal: ParaDevAiChatModuleBatchProposal;
  proposalProjectRoot: string;
  t: Translator;
  templates: ProjectTemplatesPayload | null;
};

type PrepareAiChatCollectionReviewInput = {
  activeProjectId: string;
  activeProjectRoot: string;
  proposal: ParaDevAiChatCollectionScaffoldProposal;
  proposalProjectRoot: string;
  t: Translator;
  templates: ProjectTemplatesPayload | null;
};

type PrepareAiChatSourceUpdateReviewInput = {
  activeProjectId: string;
  activeProjectRoot: string;
  proposal: ParaDevAiChatSourceFormUpdateProposal;
  proposalProjectRoot: string;
  t: Translator;
};

/**
 * Convert one validated AI dry-run into the existing retained batch editor state.
 */
export function prepareAiChatModuleBatchReview({
  activeProjectId,
  activeProjectRoot,
  proposal,
  proposalProjectRoot,
  t,
  templates
}: PrepareAiChatModuleBatchReviewInput): PreparedAiChatModuleBatchReview {
  if (
    !activeProjectRoot ||
    activeProjectRoot !== proposalProjectRoot ||
    activeProjectId !== proposal.plan.project_id
  ) {
    throw new Error(t("chat.proposal.moduleBatch.projectChanged"));
  }
  if (
    !templates ||
    templates.project_id !== activeProjectId ||
    templates.schema !== "paradev.sdk.templates.v1"
  ) {
    throw new Error(t("chat.proposal.moduleBatch.templatesChanged"));
  }

  const proposalFamily = canonicalFamilyId(proposal.familyId);
  const familyTemplates = selectCreateTemplates(templates, proposalFamily);
  const familyId = canonicalFamilyId(
    familyTemplates[0]?.family_id ?? proposalFamily,
  );
  const templatesById = new Map(
    familyTemplates.map((template) => [template.id, template])
  );
  if (
    !familyId ||
    proposal.requests.some(
      (request) => !templatesById.has(request.template_id)
    )
  ) {
    throw new Error(t("chat.proposal.moduleBatch.templatesChanged"));
  }

  const sourceRoots = templates.source_roots ?? [];
  const selectedSourceRoot = sourceRoots.find(
    (row) => row.path === proposal.sourceRoot
  );
  if (!selectedSourceRoot) {
    throw new Error(t("chat.proposal.moduleBatch.sourceChanged"));
  }
  const pristineSourceRoot =
    sourceRoots.find((row) => row.default)?.path ??
    sourceRoots[0]?.path ??
    "";
  const pristineTemplateId = familyTemplates[0]?.id ?? "";
  const modules = proposal.requests.map((request) => ({
    template_id: request.template_id,
    object_id: request.object_id,
    values: { ...request.values }
  }));
  const showAdvanced = proposal.requests.some((request) => {
    const template = templatesById.get(request.template_id);
    return Object.keys(request.values).some(
      (name) => template?.args[name]?.advanced === true
    );
  });

  return {
    familyId,
    state: {
      open: true,
      preview: {
        modules,
        plan: proposal.plan,
        sourceRoot: proposal.sourceRoot
      },
      pristineSourceRoot,
      pristineTemplateId,
      rows: proposal.requests.map((request, index) => ({
        key: index + 1,
        objectId: request.object_id,
        templateId: request.template_id,
        values: Object.fromEntries(
          Object.entries(request.values).map(([name, value]) => [
            name,
            String(value)
          ])
        )
      })),
      showAdvanced,
      sourceRoot: selectedSourceRoot.path
    }
  };
}

/** Convert one validated AI collection dry-run into the existing scaffold dialog. */
export function prepareAiChatCollectionReview({
  activeProjectId,
  activeProjectRoot,
  proposal,
  proposalProjectRoot,
  t,
  templates
}: PrepareAiChatCollectionReviewInput): PreparedAiChatCollectionReview {
  if (
    !activeProjectRoot ||
    activeProjectRoot !== proposalProjectRoot ||
    activeProjectId !== proposal.plan.project_id
  ) {
    throw new Error(t("chat.proposal.collection.projectChanged"));
  }
  if (
    !templates ||
    templates.project_id !== activeProjectId ||
    templates.schema !== "paradev.sdk.templates.v1"
  ) {
    throw new Error(t("chat.proposal.collection.templatesChanged"));
  }
  if (
    proposal.plan.schema !== "paradev.sdk.collection_scaffold.v1" ||
    proposal.plan.kind !== "collection" ||
    proposal.plan.written ||
    proposal.plan.template_id !== proposal.request.template_id ||
    proposal.plan.collection_id !== proposal.request.collection_id ||
    proposal.plan.object_id !== proposal.request.collection_id ||
    canonicalFamilyId(proposal.plan.family) !==
      canonicalFamilyId(proposal.familyId) ||
    Object.entries(proposal.request.values).some(
      ([name, value]) => proposal.plan.values[name] !== value
    )
  ) {
    throw new Error(t("chat.proposal.collection.templatesChanged"));
  }
  if (proposal.plan.source_root !== proposal.sourceRoot) {
    throw new Error(t("chat.proposal.collection.sourceChanged"));
  }

  const proposalFamily = canonicalFamilyId(proposal.familyId);
  const familyTemplates = selectCollectionCreateTemplates(
    templates,
    proposalFamily
  );
  const selectedTemplate = familyTemplates.find(
    (template) => template.id === proposal.request.template_id
  );
  const familyId = canonicalFamilyId(
    selectedTemplate?.family_id ?? proposalFamily
  );
  if (!familyId || !selectedTemplate) {
    throw new Error(t("chat.proposal.collection.templatesChanged"));
  }

  const sourceRoots = templates.source_roots ?? [];
  const selectedSourceRoot = sourceRoots.find(
    (row) => row.path === proposal.sourceRoot
  );
  if (!selectedSourceRoot) {
    throw new Error(t("chat.proposal.collection.sourceChanged"));
  }
  const pristineSourceRoot =
    sourceRoots.find((row) => row.default)?.path ??
    sourceRoots[0]?.path ??
    "";
  const pristineTemplateId = familyTemplates[0]?.id ?? "";
  const values = Object.fromEntries(
    Object.entries(proposal.request.values).map(([name, value]) => [
      name,
      String(value)
    ])
  );
  const showAdvanced = Object.keys(values).some(
    (name) => selectedTemplate.args[name]?.advanced === true
  );
  const request = {
    projectRoot: activeProjectRoot,
    templateId: proposal.request.template_id,
    collectionId: proposal.request.collection_id,
    values,
    sourceRoot: proposal.sourceRoot,
    force: false
  };

  return {
    familyId,
    state: {
      open: true,
      preview: {
        plan: proposal.plan,
        request
      },
      pristineSourceRoot,
      pristineTemplateId,
      templateId: selectedTemplate.id,
      collectionId: proposal.request.collection_id,
      values,
      showAdvanced,
      sourceRoot: selectedSourceRoot.path
    }
  };
}

/** Convert one validated AI Guided edit into an exact retained review. */
export function prepareAiChatSourceUpdateReview({
  activeProjectId,
  activeProjectRoot,
  proposal,
  proposalProjectRoot,
  t
}: PrepareAiChatSourceUpdateReviewInput): PreparedAiChatSourceUpdateReview {
  if (
    !activeProjectRoot ||
    activeProjectRoot !== proposalProjectRoot ||
    activeProjectId !== proposal.plan.projectId
  ) {
    throw new Error(t("chat.proposal.sourceUpdate.projectChanged"));
  }
  const familyId = canonicalFamilyId(proposal.familyId);
  if (
    !familyId ||
    proposal.plan.schema !== "paradev.source-form-update-batch.v1" ||
    proposal.plan.updates.length !== proposal.requests.length ||
    proposal.plan.counts.requested !== proposal.requests.length ||
    proposal.plan.updates.some((update, index) => {
      const request = proposal.requests[index];
      return (
        !request ||
        canonicalFamilyId(update.family) !== familyId ||
        update.moduleId !== request.module_id ||
        update.relativePath !== request.source_path ||
        update.changes.some(
          (change) =>
            !Object.hasOwn(request.values, change.controlId) ||
            !Object.is(request.values[change.controlId], change.value) ||
            !Object.hasOwn(request.control_labels, change.controlId)
        )
      );
    })
  ) {
    throw new Error(t("chat.proposal.sourceUpdate.sourceChanged"));
  }
  return {
    familyId,
    state: {
      open: true,
      requests: proposal.requests,
      plan: proposal.plan
    }
  };
}
