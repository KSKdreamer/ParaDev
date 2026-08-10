import type { ParaDevAiChatOperationCard, ParaDevAiChatProfile } from "./services/paradev";
import type { TranslationKey, Translator } from "./i18n";

export type AiChatOperationCard = {
  actionTitle: string;
  mutates: boolean;
  operation: {
    id: string;
    summary: string;
  };
  restLabel: string;
  sdkLabel: string;
};

type AiChatOperationCardTextKeys = {
  summary: TranslationKey;
  title: TranslationKey;
};

const OPERATION_CARD_TEXT_KEYS: Record<string, AiChatOperationCardTextKeys> = {
  "build.plan": {
    summary: "chat.operation.card.buildPlan.summary",
    title: "chat.operation.card.buildPlan.title"
  },
  "build.start": {
    summary: "chat.operation.card.buildStart.summary",
    title: "chat.operation.card.buildStart.title"
  },
  "module.draft": {
    summary: "chat.operation.card.moduleDraft.summary",
    title: "chat.operation.card.moduleDraft.title"
  },
  "module.create_batch": {
    summary: "chat.operation.card.moduleCreateBatch.summary",
    title: "chat.operation.card.moduleCreateBatch.title"
  },
  "collection.scaffold": {
    summary: "chat.operation.card.collectionScaffold.summary",
    title: "chat.operation.card.collectionScaffold.title"
  }
};

export function aiChatProfileOperationCards(profile?: Pick<ParaDevAiChatProfile, "operationCards">, t?: Translator): AiChatOperationCard[] {
  return (profile?.operationCards ?? []).filter(isRenderableOperationCard).map((card) => ({
    actionTitle: aiChatOperationCardTitle(card, t),
    mutates: card.mutates,
    operation: {
      id: card.id,
      summary: aiChatOperationCardSummary(card, t)
    },
    restLabel: card.rest,
    sdkLabel: card.sdk
  }));
}

function aiChatOperationCardTitle(card: ParaDevAiChatOperationCard, t?: Translator): string {
  const key = OPERATION_CARD_TEXT_KEYS[card.id]?.title;
  return key && t ? t(key) : card.title || card.id;
}

function aiChatOperationCardSummary(card: ParaDevAiChatOperationCard, t?: Translator): string {
  const key = OPERATION_CARD_TEXT_KEYS[card.id]?.summary;
  return key && t ? t(key) : card.summary;
}

function isRenderableOperationCard(card: ParaDevAiChatOperationCard): boolean {
  return Boolean(card.id && card.summary);
}
