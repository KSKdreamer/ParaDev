/** @vitest-environment jsdom */

import { act } from "react";
import { createRoot, type Root } from "react-dom/client";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { createTranslator } from "../i18n";
import type {
  ParaDevAiChatProfile,
  ParaDevAiChatSource,
  ParaDevAiChatSourceKindRow
} from "../services/paradev";
import {
  FloatingChatShell,
  type AiChatProposalReview,
  type AiChatSendResult
} from "./FloatingChatShell";

const mounted: Array<{ container: HTMLDivElement; root: Root }> = [];
const noSources: ParaDevAiChatSource[] = [];
const noSourceKindRows: ParaDevAiChatSourceKindRow[] = [];

beforeEach(() => {
  (
    globalThis as typeof globalThis & {
      IS_REACT_ACT_ENVIRONMENT: boolean;
    }
  ).IS_REACT_ACT_ENVIRONMENT = true;
});

afterEach(() => {
  for (const item of mounted.splice(0)) {
    act(() => item.root.unmount());
    item.container.remove();
  }
});

describe("FloatingChatShell proposal lifecycle", () => {
  it("renders an async batch proposal without reviewing it until the user clicks", async () => {
    const review = moduleBatchReview();
    const onSend = vi.fn(async () => ({
      proposal: review,
      text: "I prepared a validated two-module plan."
    }));
    const onProposalReview = vi.fn(async () => undefined);
    const container = mountChat({ onProposalReview, onSend });

    setTextareaValue(
      requiredElement<HTMLTextAreaElement>(
        container,
        '[data-paradev-chat-input="true"]'
      ),
      "Create ideas A and B"
    );
    await act(async () => {
      requiredElement<HTMLButtonElement>(
        container,
        '[data-paradev-chat-send="true"]'
      ).click();
      await Promise.resolve();
    });

    expect(onSend).toHaveBeenCalledWith(
      "Create ideas A and B",
      "create-module",
      []
    );
    expect(container.textContent).toContain(
      "I prepared a validated two-module plan."
    );
    expect(
      container.querySelector('[data-paradev-chat-proposal="module.create_batch"]')
    ).not.toBeNull();
    expect(container.textContent).toContain(
      "2 modules were validated with a read-only SDK plan"
    );
    expect(onProposalReview).not.toHaveBeenCalled();

    await act(async () => {
      requiredElement<HTMLButtonElement>(
        container,
        '[data-paradev-chat-proposal-action="review"]'
      ).click();
      await Promise.resolve();
    });

    expect(onProposalReview).toHaveBeenCalledOnce();
    expect(onProposalReview).toHaveBeenCalledWith(review);
  });

  it("renders a collection proposal and hands off only after review", async () => {
    const review = collectionReview();
    const onSend = vi.fn(async () => ({
      proposal: review,
      text: "I prepared a validated focus-tree plan."
    }));
    const onProposalReview = vi.fn(async () => undefined);
    const container = mountChat({ onProposalReview, onSend });

    setTextareaValue(
      requiredElement<HTMLTextAreaElement>(
        container,
        '[data-paradev-chat-input="true"]'
      ),
      "Create a C99 focus tree"
    );
    await act(async () => {
      requiredElement<HTMLButtonElement>(
        container,
        '[data-paradev-chat-send="true"]'
      ).click();
      await Promise.resolve();
    });

    expect(
      container.querySelector(
        '[data-paradev-chat-proposal="collection.scaffold"]'
      )
    ).not.toBeNull();
    expect(container.textContent).toContain(
      "Collection C99_AI_REVIEW was validated with a read-only SDK plan"
    );
    expect(onProposalReview).not.toHaveBeenCalled();

    await act(async () => {
      requiredElement<HTMLButtonElement>(
        container,
        '[data-paradev-chat-proposal-action="review"]'
      ).click();
      await Promise.resolve();
    });

    expect(onProposalReview).toHaveBeenCalledWith(review);
  });
});

function mountChat({
  onProposalReview,
  onSend
}: {
  onProposalReview: (review: AiChatProposalReview) => void | Promise<void>;
  onSend: (
    prompt: string,
    role: string,
    sources: ParaDevAiChatSource[]
  ) => Promise<AiChatSendResult>;
}): HTMLDivElement {
  const container = document.createElement("div");
  document.body.append(container);
  const root = createRoot(container);
  mounted.push({ container, root });
  act(() => {
    root.render(
      <FloatingChatShell
        activeProjectName="PIHC3"
        contextSources={noSources}
        defaultRole="create-module"
        gateway="openai"
        model="deepseek-v4-flash"
        onProposalReview={onProposalReview}
        onSend={onSend}
        open={true}
        preset="chat"
        profiles={[createModuleProfile]}
        provider="deepseek"
        sourceKindRows={noSourceKindRows}
        t={createTranslator("en")}
      />
    );
  });
  return container;
}

const createModuleProfile: ParaDevAiChatProfile = {
  id: "create-module",
  label: "Create module plan",
  detail: "Plan new modules before writing source files.",
  prompt: "Create a validated module plan.",
  sourceKinds: []
};

function moduleBatchReview(): AiChatProposalReview {
  return {
    projectRoot: "/workspace/PIHC3",
    proposal: {
      schema: "paradev.desktop.ai-chat-proposal.v1",
      operationId: "module.create_batch",
      familyId: "idea",
      sourceRoot: "/workspace/PIHC3/src",
      requests: [
        {
          template_id: "pihc3:idea/basic",
          object_id: "A",
          values: { cic: 0.02 }
        },
        {
          template_id: "pihc3:idea/basic",
          object_id: "B",
          values: { cic: 0.05 }
        }
      ],
      plan: {
        schema: "paradev.sdk.module_batch.v1",
        project_id: "PIHC3",
        source_root: "/workspace/PIHC3/src",
        plan_hash: "a".repeat(64),
        blocked: false,
        applied: false,
        written: false,
        requested_count: 2,
        counts: {
          create: 2,
          created: 0,
          unchanged: 0,
          blocked: 0
        },
        diagnostics: [],
        modules: []
      }
    },
    role: "create-module",
    sources: []
  };
}

function collectionReview(): AiChatProposalReview {
  const sourceRoot = "/workspace/PIHC3/src";
  const collectionId = "C99_AI_REVIEW";
  return {
    projectRoot: "/workspace/PIHC3",
    proposal: {
      schema: "paradev.desktop.ai-chat-proposal.v1",
      operationId: "collection.scaffold",
      familyId: "focus",
      sourceRoot,
      request: {
        template_id: "pihc3:focus-tree/basic",
        collection_id: collectionId,
        values: { country_tag: "C99", title: "AI Review Tree" }
      },
      plan: {
        schema: "paradev.sdk.collection_scaffold.v1",
        project_id: "PIHC3",
        template_id: "pihc3:focus-tree/basic",
        kind: "collection",
        family: "focus",
        object_id: collectionId,
        collection_id: collectionId,
        folder_name: `${collectionId} - AI Review Tree`,
        source_root: sourceRoot,
        root: `${sourceRoot}/collections/focus/${collectionId} - AI Review Tree`,
        values: { country_tag: "C99", title: "AI Review Tree" },
        blocked: false,
        written: false,
        plan_hash: "b".repeat(64),
        diagnostics: [],
        files: [],
        authoring_plan: {}
      }
    },
    role: "create-module",
    sources: []
  };
}

function requiredElement<T extends Element>(
  container: ParentNode,
  selector: string
): T {
  const element = container.querySelector<T>(selector);
  if (!element) {
    throw new Error(`Missing element ${selector}.`);
  }
  return element;
}

function setTextareaValue(
  element: HTMLTextAreaElement,
  value: string
): void {
  const setter = Object.getOwnPropertyDescriptor(
    HTMLTextAreaElement.prototype,
    "value"
  )?.set;
  if (!setter) {
    throw new Error("Missing HTMLTextAreaElement value setter.");
  }
  act(() => {
    setter.call(element, value);
    element.dispatchEvent(new Event("input", { bubbles: true }));
  });
}
