/** @vitest-environment jsdom */

import { act, useState } from "react";
import { createRoot, type Root } from "react-dom/client";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { createTranslator } from "../i18n";
import type { SourceFormPayload } from "../types";
import type { ModuleEntity } from "./model";
import { ModuleEntityDetails } from "./ModuleEntityDetails";
import type { GuidedSourceFormChange } from "./GuidedSourceForm";

const serviceMocks = vi.hoisted(() => ({
  readProjectSourceForm: vi.fn(),
  readTextSource: vi.fn()
}));

vi.mock("../services/paradev", async (importOriginal) => ({
  ...(await importOriginal<typeof import("../services/paradev")>()),
  readProjectSourceForm: serviceMocks.readProjectSourceForm,
  readTextSource: serviceMocks.readTextSource
}));

vi.mock("./SourceCodeEditor", () => ({
  SourceCodeEditor: ({ onChange, value }: { onChange: (value: string) => void; value: string }) => (
    <textarea
      aria-label="mock code editor"
      data-testid="advanced-editor"
      onChange={(event) => onChange(event.target.value)}
      value={value}
    />
  )
}));

vi.mock("./GuidedSourceForm", () => ({
  GuidedSourceForm: ({ disabled, form, onChange, onSearch, text }: { disabled?: boolean; form: SourceFormPayload; onChange: (change: GuidedSourceFormChange) => void; onSearch?: (query: string) => void; text: string }) => (
    <div data-module-id={form.module_id} data-source-path={form.relative_path} data-testid="guided-editor">
      <output>{text}</output>
      <button
        disabled={disabled}
        onClick={() => onChange({
          baseText: text,
          controlId: "mock.control",
          text: form.source_format === "pdx" ? text.replace("yes", "no") : `${text}\n`,
          value: form.source_format === "pdx" ? false : "guided"
        })}
        type="button"
      >
        mock guided change
      </button>
      <button disabled={disabled} onClick={() => onSearch?.("C01_C02_GREENLIGHT.40")} type="button">
        mock guided search
      </button>
    </div>
  )
}));

const mountedRoots: Array<{ container: HTMLDivElement; root: Root }> = [];
const t = createTranslator("en");
type DraftCallback = (entityId: string, sourceKey: string, value: string) => void;
type GuidedDraftCallback = (entityId: string, sourceKey: string, change: GuidedSourceFormChange) => void;

beforeEach(() => {
  (globalThis as typeof globalThis & { IS_REACT_ACT_ENVIRONMENT: boolean }).IS_REACT_ACT_ENVIRONMENT = true;
  serviceMocks.readProjectSourceForm.mockReset();
  serviceMocks.readTextSource.mockReset();
  serviceMocks.readTextSource.mockResolvedValue("");
});

afterEach(() => {
  for (const mounted of mountedRoots.splice(0)) {
    act(() => mounted.root.unmount());
    mounted.container.remove();
  }
  vi.restoreAllMocks();
});

describe("ModuleEntityDetails guided source-form lifecycle", () => {
  it("requests the exact ready JSON draft and routes Registry control intent through the guided draft callback", async () => {
    const text = '{\r\n  "mesh": { "scale": 3.0 },\r\n  "unknown": true\r\n}';
    const entity = entityRecord("ENTITY_ALPHA", text);
    const form = sourceForm("ENTITY_ALPHA", entity);
    const onTextDraft = vi.fn();
    const onGuidedTextDraft = vi.fn();
    serviceMocks.readProjectSourceForm.mockResolvedValue(form);

    const mounted = mountDetails(entity, onTextDraft, onGuidedTextDraft);
    await flushAsyncWork();

    expect(serviceMocks.readProjectSourceForm).toHaveBeenCalledTimes(1);
    expect(serviceMocks.readProjectSourceForm).toHaveBeenCalledWith({
      projectId: "PIHC3",
      projectRoot: "/workspace/PIHC3",
      sourcePath: entity.sourceSlots[0].path,
      text
    });
    expect(requiredElement(mounted.container, '[data-testid="guided-editor"]').textContent).toContain(text);
    expect(pressedButton(mounted.container, "Guided")).toBe(true);

    act(() => buttonNamed(mounted.container, "mock guided change").click());
    expect(onTextDraft).not.toHaveBeenCalled();
    expect(onGuidedTextDraft).toHaveBeenCalledWith(entity.id, "record", {
      baseText: text,
      controlId: "mock.control",
      text: `${text}\n`,
      value: "guided"
    });

    act(() => buttonNamed(mounted.container, "Guided").click());
    expect(serviceMocks.readProjectSourceForm).toHaveBeenCalledTimes(1);
  });

  it("does not project a source until its text is hydrated and treats an empty file as ready", async () => {
    const pendingText = deferred<string>();
    const entity = entityRecord("ENTITY_EMPTY");
    const form = sourceForm("ENTITY_EMPTY", entity);
    serviceMocks.readTextSource.mockReturnValue(pendingText.promise);
    serviceMocks.readProjectSourceForm.mockResolvedValue(form);

    const mounted = mountDetails(entity, vi.fn());
    await flushAsyncWork();

    expect(serviceMocks.readTextSource).toHaveBeenCalledWith(
      "/workspace/PIHC3",
      entity.sourceSlots[0].path,
      "PIHC3"
    );
    expect(serviceMocks.readProjectSourceForm).not.toHaveBeenCalled();

    pendingText.resolve("");
    await flushAsyncWork();

    expect(serviceMocks.readProjectSourceForm).toHaveBeenCalledOnce();
    expect(serviceMocks.readProjectSourceForm).toHaveBeenCalledWith(expect.objectContaining({ text: "" }));
    expect(requiredElement(mounted.container, '[data-testid="guided-editor"]')).not.toBeNull();
  });

  it("keeps unsupported JSON in the advanced editor without exposing a misleading mode toggle", async () => {
    const entity = entityRecord("ENTITY_UNSUPPORTED", "{}");
    serviceMocks.readProjectSourceForm.mockResolvedValue(null);

    const mounted = mountDetails(entity, vi.fn());
    await flushAsyncWork();

    expect(requiredElement<HTMLTextAreaElement>(mounted.container, '[data-testid="advanced-editor"]').value).toBe("{}");
    expect(mounted.container.textContent).not.toContain("Guided");
    expect(mounted.container.textContent).not.toContain("Code");
  });

  it("reprojects the current advanced draft only when Guided is requested, without emitting a toggle draft", async () => {
    const initialText = '{"mesh":{"scale":3}}';
    const updatedText = '{"mesh":{"scale":4.25},"kept":"yes"}';
    const entity = entityRecord("ENTITY_REPROJECT", initialText);
    const onTextDraft = vi.fn();
    serviceMocks.readProjectSourceForm.mockResolvedValue(sourceForm("ENTITY_REPROJECT", entity));

    const mounted = mountStatefulDetails(entity, onTextDraft);
    await flushAsyncWork();
    act(() => buttonNamed(mounted.container, "Code").click());
    expect(onTextDraft).not.toHaveBeenCalled();

    changeTextarea(requiredElement(mounted.container, '[data-testid="advanced-editor"]'), updatedText);
    expect(onTextDraft).toHaveBeenCalledWith(entity.id, "record", updatedText);
    expect(serviceMocks.readProjectSourceForm).toHaveBeenCalledTimes(1);

    act(() => buttonNamed(mounted.container, "Guided").click());
    await flushAsyncWork();

    expect(serviceMocks.readProjectSourceForm).toHaveBeenCalledTimes(2);
    expect(serviceMocks.readProjectSourceForm).toHaveBeenLastCalledWith(expect.objectContaining({ text: updatedText }));
    expect(onTextDraft).toHaveBeenCalledTimes(1);
    expect(requiredElement(mounted.container, '[data-testid="guided-editor"]').textContent).toContain(updatedText);
  });

  it("leaves invalid advanced text untouched, explains the projection error, and permits a valid retry", async () => {
    const entity = entityRecord("ENTITY_RETRY", '{"mesh":{"scale":3}}');
    const onTextDraft = vi.fn();
    const form = sourceForm("ENTITY_RETRY", entity);
    serviceMocks.readProjectSourceForm.mockResolvedValue(form);

    const mounted = mountStatefulDetails(entity, onTextDraft);
    await flushAsyncWork();
    act(() => buttonNamed(mounted.container, "Code").click());

    serviceMocks.readProjectSourceForm.mockRejectedValueOnce(new Error("record JSON is incomplete"));
    changeTextarea(requiredElement(mounted.container, '[data-testid="advanced-editor"]'), "{");
    act(() => buttonNamed(mounted.container, "Guided").click());
    await flushAsyncWork();

    expect(requiredElement<HTMLTextAreaElement>(mounted.container, '[data-testid="advanced-editor"]').value).toBe("{");
    expect(mounted.container.textContent).toContain("record JSON is incomplete");
    expect(pressedButton(mounted.container, "Code")).toBe(true);

    const validRetry = '{"mesh":{"scale":5}}';
    serviceMocks.readProjectSourceForm.mockResolvedValueOnce(form);
    changeTextarea(requiredElement(mounted.container, '[data-testid="advanced-editor"]'), validRetry);
    act(() => buttonNamed(mounted.container, "Guided").click());
    await flushAsyncWork();

    expect(serviceMocks.readProjectSourceForm).toHaveBeenLastCalledWith(expect.objectContaining({ text: validRetry }));
    expect(requiredElement(mounted.container, '[data-testid="guided-editor"]').textContent).toContain(validRetry);
  });

  it("ignores a late form response after the selected entity changes", async () => {
    const alpha = entityRecord("ENTITY_ALPHA", "{}");
    const beta = entityRecord("ENTITY_BETA", "{}");
    const alphaForm = deferred<SourceFormPayload | null>();
    serviceMocks.readProjectSourceForm
      .mockReturnValueOnce(alphaForm.promise)
      .mockResolvedValueOnce(sourceForm("ENTITY_BETA", beta));

    const mounted = mountDetails(alpha, vi.fn());
    await flushAsyncWork();
    act(() => renderDetails(mounted.root, beta, vi.fn()));
    await flushAsyncWork();

    expect(requiredElement(mounted.container, '[data-testid="guided-editor"]').getAttribute("data-module-id")).toBe("entity/ENTITY_BETA");
    alphaForm.resolve(sourceForm("ENTITY_ALPHA", alpha));
    await flushAsyncWork();

    expect(requiredElement(mounted.container, '[data-testid="guided-editor"]').getAttribute("data-module-id")).toBe("entity/ENTITY_BETA");
  });

  it("keeps the newest source projection when two JSON sources are selected rapidly", async () => {
    const entity = entityRecordWithTwoSources("ENTITY_SOURCE_SWITCH");
    const firstProjection = deferred<SourceFormPayload | null>();
    serviceMocks.readProjectSourceForm
      .mockReturnValueOnce(firstProjection.promise)
      .mockResolvedValueOnce(sourceFormForSource("ENTITY_SOURCE_SWITCH", entity, 1));

    const mounted = mountDetails(entity, vi.fn());
    await flushAsyncWork();
    expect(serviceMocks.readProjectSourceForm).toHaveBeenCalledWith(expect.objectContaining({
      sourcePath: entity.sourceSlots[0].path,
      text: entity.drafts.text.primary
    }));

    act(() => buttonNamed(mounted.container, "secondary").click());
    await flushAsyncWork();

    expect(serviceMocks.readProjectSourceForm).toHaveBeenCalledTimes(2);
    expect(serviceMocks.readProjectSourceForm).toHaveBeenLastCalledWith(expect.objectContaining({
      sourcePath: entity.sourceSlots[1].path,
      text: entity.drafts.text.secondary
    }));
    expect(requiredElement(mounted.container, '[data-testid="guided-editor"]').getAttribute("data-source-path"))
      .toBe(entity.sourceSlots[1].relative_path);

    firstProjection.reject(new Error("ParaDev desktop backend request was superseded by a newer request."));
    await flushAsyncWork();

    expect(requiredElement(mounted.container, '[data-testid="guided-editor"]').getAttribute("data-source-path"))
      .toBe(entity.sourceSlots[1].relative_path);
    expect(mounted.container.textContent).not.toContain("superseded by a newer request");
  });

  it("does not open a form projected from stale text and retries with the latest same-source draft", async () => {
    const initialText = '{"mesh":{"scale":1}}';
    const latestText = '{"mesh":{"scale":2},"new_state":true}';
    const entity = entityRecord("ENTITY_STALE_TEXT", initialText);
    const staleForm = deferred<SourceFormPayload | null>();
    serviceMocks.readProjectSourceForm
      .mockReturnValueOnce(staleForm.promise)
      .mockResolvedValue(sourceForm("ENTITY_STALE_TEXT", entity));

    const mounted = mountStatefulDetails(entity, vi.fn());
    await flushAsyncWork();
    changeTextarea(requiredElement(mounted.container, '[data-testid="advanced-editor"]'), latestText);

    staleForm.resolve(sourceForm("ENTITY_STALE_TEXT", entity));
    await flushAsyncWork();

    expect(mounted.container.querySelector('[data-testid="guided-editor"]')).toBeNull();
    expect(requiredElement<HTMLTextAreaElement>(mounted.container, '[data-testid="advanced-editor"]').value).toBe(latestText);
    expect(mounted.container.textContent).toContain("source changed while Guided mode was loading");
    expect(pressedButton(mounted.container, "Code")).toBe(true);

    act(() => buttonNamed(mounted.container, "Guided").click());
    await flushAsyncWork();

    expect(serviceMocks.readProjectSourceForm).toHaveBeenCalledTimes(2);
    expect(serviceMocks.readProjectSourceForm).toHaveBeenLastCalledWith(expect.objectContaining({ text: latestText }));
    expect(requiredElement(mounted.container, '[data-testid="guided-editor"]')).not.toBeNull();
  });

  it("keeps initial discovery alive when Code is selected and does not override that preference", async () => {
    const entity = entityRecord("ENTITY_ADVANCED_PREFERENCE", "{}");
    const discovery = deferred<SourceFormPayload | null>();
    const form = sourceForm("ENTITY_ADVANCED_PREFERENCE", entity);
    serviceMocks.readProjectSourceForm.mockReturnValueOnce(discovery.promise).mockResolvedValue(form);

    const mounted = mountDetails(entity, vi.fn());
    await flushAsyncWork();
    act(() => buttonNamed(mounted.container, "Code").click());

    expect(pressedButton(mounted.container, "Code")).toBe(true);
    expect(mounted.container.textContent).toContain("Preparing guided editor");

    discovery.resolve(form);
    await flushAsyncWork();

    expect(mounted.container.querySelector('[data-testid="guided-editor"]')).toBeNull();
    expect(requiredElement(mounted.container, '[data-testid="advanced-editor"]')).not.toBeNull();
    expect(pressedButton(mounted.container, "Code")).toBe(true);

    act(() => buttonNamed(mounted.container, "Code").click());
    expect(serviceMocks.readProjectSourceForm).toHaveBeenCalledTimes(1);

    act(() => buttonNamed(mounted.container, "Guided").click());
    await flushAsyncWork();
    expect(serviceMocks.readProjectSourceForm).toHaveBeenCalledTimes(2);
    expect(requiredElement(mounted.container, '[data-testid="guided-editor"]')).not.toBeNull();
  });

  it("reprojects a PDX form after each guided token edit and disables stale spans while refreshing", async () => {
    const initialText = "active = yes\n";
    const nextText = "active = no\n";
    const entity = pdxEntityRecord("IDEA_REPROJECT", initialText);
    const refreshed = deferred<SourceFormPayload | null>();
    const onTextDraft = vi.fn();
    serviceMocks.readProjectSourceForm
      .mockResolvedValueOnce(pdxSourceForm("IDEA_REPROJECT", entity, initialText))
      .mockReturnValueOnce(refreshed.promise);

    const mounted = mountStatefulDetails(entity, onTextDraft);
    await flushAsyncWork();

    act(() => buttonNamed(mounted.container, "mock guided change").click());
    await flushAsyncWork();

    expect(onTextDraft).toHaveBeenCalledWith(entity.id, "def", nextText);
    expect(serviceMocks.readProjectSourceForm).toHaveBeenCalledTimes(2);
    expect(serviceMocks.readProjectSourceForm).toHaveBeenLastCalledWith(
      expect.objectContaining({ sourcePath: entity.sourceSlots[0].path, text: nextText })
    );
    expect(buttonNamed(mounted.container, "mock guided change").disabled).toBe(true);
    expect(requiredElement(mounted.container, '[data-testid="guided-editor"] output').textContent).toBe(initialText);

    refreshed.resolve(pdxSourceForm("IDEA_REPROJECT", entity, nextText));
    await flushAsyncWork();

    expect(buttonNamed(mounted.container, "mock guided change").disabled).toBe(false);
    expect(requiredElement(mounted.container, '[data-testid="guided-editor"] output').textContent).toBe(nextText);
  });

  it("keeps bounded PDX search on the current draft and sends the query through the backend", async () => {
    const text = "active = yes\n";
    const entity = pdxEntityRecord("IDEA_SEARCH", text);
    const defaultForm = pdxSourceForm("IDEA_SEARCH", entity, text);
    const queriedForm = {
      ...defaultForm,
      query: "C01_C02_GREENLIGHT.40"
    };
    serviceMocks.readProjectSourceForm
      .mockResolvedValueOnce(defaultForm)
      .mockResolvedValueOnce(queriedForm);

    const mounted = mountDetails(entity, vi.fn());
    await flushAsyncWork();
    act(() => buttonNamed(mounted.container, "mock guided search").click());
    await flushAsyncWork();

    expect(serviceMocks.readProjectSourceForm).toHaveBeenCalledTimes(2);
    expect(serviceMocks.readProjectSourceForm).toHaveBeenLastCalledWith({
      projectId: "PIHC3",
      projectRoot: "/workspace/PIHC3",
      sourcePath: entity.sourceSlots[0].path,
      text,
      query: "C01_C02_GREENLIGHT.40"
    });
  });

  it.each([
    "fragment.pdx",
    "interface/example.gui",
    "animations/example.asset"
  ])("asks the Registry for guided controls on non-def PDX code source %s", async (moduleRelativePath) => {
    const text = "active = yes\n";
    const entity = pdxEntityRecordAt("PDX_NON_DEF", text, moduleRelativePath);
    serviceMocks.readProjectSourceForm.mockResolvedValue(
      pdxSourceForm("PDX_NON_DEF", entity, text)
    );

    const mounted = mountDetails(entity, vi.fn());
    await flushAsyncWork();

    expect(serviceMocks.readProjectSourceForm).toHaveBeenCalledOnce();
    expect(serviceMocks.readProjectSourceForm).toHaveBeenCalledWith({
      projectId: "PIHC3",
      projectRoot: "/workspace/PIHC3",
      sourcePath: entity.sourceSlots[0].path,
      text
    });
    expect(requiredElement(mounted.container, '[data-testid="guided-editor"]')).not.toBeNull();
  });

  it("accepts an immediate PDX reprojection response without misclassifying its own draft as stale", async () => {
    const initialText = "active = yes\n";
    const nextText = "active = no\n";
    const entity = pdxEntityRecord("IDEA_IMMEDIATE", initialText);
    serviceMocks.readProjectSourceForm
      .mockResolvedValueOnce(pdxSourceForm("IDEA_IMMEDIATE", entity, initialText))
      .mockResolvedValueOnce(pdxSourceForm("IDEA_IMMEDIATE", entity, nextText));

    const mounted = mountStatefulDetails(entity, vi.fn());
    await flushAsyncWork();
    act(() => buttonNamed(mounted.container, "mock guided change").click());
    await flushAsyncWork();

    expect(serviceMocks.readProjectSourceForm).toHaveBeenCalledTimes(2);
    expect(requiredElement(mounted.container, '[data-testid="guided-editor"] output').textContent).toBe(nextText);
    expect(pressedButton(mounted.container, "Guided")).toBe(true);
    expect(mounted.container.textContent).not.toContain("source changed while Guided mode was loading");
  });

  it("enables Save as soon as a guided edit enters the shared draft lifecycle", async () => {
    const entity = entityRecord("ENTITY_SAVE", "{}");
    serviceMocks.readProjectSourceForm.mockResolvedValue(sourceForm("ENTITY_SAVE", entity));
    const mounted = mountStatefulDetails(entity, vi.fn());
    await flushAsyncWork();

    expect(buttonNamed(mounted.container, "Apply").disabled).toBe(true);
    act(() => buttonNamed(mounted.container, "mock guided change").click());
    expect(buttonNamed(mounted.container, "Apply").disabled).toBe(false);
  });

  it("reprojects restored text before Guided reopens after a structural draft is discarded", async () => {
    const originalText = '{"entities":[{"name":"ORIGINAL","scale":1}]}';
    const structuralDraft = '{"entities":[{"name":"OTHER","scale":2},{"name":"ORIGINAL","scale":1}]}';
    const entity = entityRecord("ENTITY_RESTORE", originalText);
    const restoredProjection = deferred<SourceFormPayload | null>();
    serviceMocks.readProjectSourceForm
      .mockResolvedValueOnce(sourceForm("ENTITY_RESTORE", entity))
      .mockResolvedValueOnce(sourceForm("ENTITY_RESTORE", entity))
      .mockReturnValueOnce(restoredProjection.promise);

    const mounted = mountStatefulDetails(entity, vi.fn());
    await flushAsyncWork();
    act(() => buttonNamed(mounted.container, "Code").click());
    changeTextarea(requiredElement(mounted.container, '[data-testid="advanced-editor"]'), structuralDraft);
    act(() => buttonNamed(mounted.container, "Guided").click());
    await flushAsyncWork();

    expect(requiredElement(mounted.container, '[data-testid="guided-editor"]')).not.toBeNull();
    act(() => buttonNamed(mounted.container, "Discard").click());
    await flushAsyncWork();

    expect(serviceMocks.readProjectSourceForm).toHaveBeenCalledTimes(3);
    expect(serviceMocks.readProjectSourceForm).toHaveBeenLastCalledWith(expect.objectContaining({ text: originalText }));
    expect(mounted.container.querySelector('[data-testid="guided-editor"]')).toBeNull();
    expect(requiredElement<HTMLTextAreaElement>(mounted.container, '[data-testid="advanced-editor"]').value).toBe(originalText);
    expect(buttonNamed(mounted.container, "Guided").disabled).toBe(true);

    restoredProjection.resolve(sourceForm("ENTITY_RESTORE", entity));
    await flushAsyncWork();

    expect(requiredElement(mounted.container, '[data-testid="guided-editor"]').textContent).toContain(originalText);
  });
});

function StatefulDetails({ initialEntity, onTextDraft }: { initialEntity: ModuleEntity; onTextDraft: DraftCallback }) {
  const [entity, setEntity] = useState(initialEntity);
  const [sourceReloadKey, setSourceReloadKey] = useState(0);
  return (
    <Details
      canApply={entity.draftState !== "clean"}
      entity={entity}
      onRestore={(entityId) => {
        if (entityId !== initialEntity.id) {
          return;
        }
        setEntity(initialEntity);
        setSourceReloadKey((current) => current + 1);
      }}
      onTextDraft={(entityId, sourceKey, value) => {
        onTextDraft(entityId, sourceKey, value);
        setEntity((current) => ({
          ...current,
          draftState: "modified",
          drafts: {
            ...current.drafts,
            text: { ...current.drafts.text, [sourceKey]: value }
          }
        }));
      }}
      sourceReloadKey={sourceReloadKey}
    />
  );
}

function Details({
  canApply = false,
  entity,
  onRestore = () => undefined,
  onGuidedTextDraft,
  onTextDraft,
  sourceReloadKey = 0
}: {
  canApply?: boolean;
  entity: ModuleEntity;
  onRestore?: (entityId: string) => void;
  onGuidedTextDraft?: GuidedDraftCallback;
  onTextDraft: DraftCallback;
  sourceReloadKey?: number;
}) {
  return (
    <ModuleEntityDetails
      activeDiagramNodeId=""
      applyBusy={false}
      applyError=""
      canApply={canApply}
      entity={entity}
      locale="en"
      onApply={() => undefined}
      onImageDraft={() => undefined}
      onInfoDraft={() => undefined}
      onGuidedTextDraft={onGuidedTextDraft}
      onRefresh={() => undefined}
      onRestore={onRestore}
      onTextDraft={onTextDraft}
      openTarget="finder"
      projectId="PIHC3"
      projectRoot="/workspace/PIHC3"
      sourceReloadKey={sourceReloadKey}
      targetSourcePath={entity.sourceSlots[0].relative_path}
      t={t}
      theme="light"
    />
  );
}

function mountDetails(
  entity: ModuleEntity,
  onTextDraft: DraftCallback,
  onGuidedTextDraft?: GuidedDraftCallback
) {
  const mounted = createMountedRoot();
  act(() => renderDetails(mounted.root, entity, onTextDraft, onGuidedTextDraft));
  return mounted;
}

function mountStatefulDetails(entity: ModuleEntity, onTextDraft: DraftCallback) {
  const mounted = createMountedRoot();
  act(() => mounted.root.render(<StatefulDetails initialEntity={entity} onTextDraft={onTextDraft} />));
  return mounted;
}

function renderDetails(
  root: Root,
  entity: ModuleEntity,
  onTextDraft: DraftCallback,
  onGuidedTextDraft?: GuidedDraftCallback
): void {
  root.render(
    <Details
      entity={entity}
      onGuidedTextDraft={onGuidedTextDraft}
      onTextDraft={onTextDraft}
    />
  );
}

function createMountedRoot() {
  const container = document.createElement("div");
  document.body.append(container);
  const root = createRoot(container);
  const mounted = { container, root };
  mountedRoots.push(mounted);
  return mounted;
}

async function flushAsyncWork(): Promise<void> {
  await act(async () => {
    await Promise.resolve();
    await Promise.resolve();
    await Promise.resolve();
  });
}

function changeTextarea(element: Element, value: string): void {
  const textarea = element as HTMLTextAreaElement;
  act(() => {
    Object.getOwnPropertyDescriptor(HTMLTextAreaElement.prototype, "value")?.set?.call(textarea, value);
    textarea.dispatchEvent(new Event("input", { bubbles: true }));
  });
}

function buttonNamed(container: HTMLElement, name: string): HTMLButtonElement {
  const button = [...container.querySelectorAll<HTMLButtonElement>("button")].find((candidate) => candidate.textContent === name);
  expect(button, `button named ${name}`).toBeDefined();
  return button as HTMLButtonElement;
}

function pressedButton(container: HTMLElement, name: string): boolean {
  return buttonNamed(container, name).getAttribute("aria-pressed") === "true";
}

function requiredElement<T extends Element = HTMLElement>(container: ParentNode, selector: string): T {
  const element = container.querySelector<T>(selector);
  expect(element, selector).not.toBeNull();
  return element as T;
}

function entityRecord(objectId: string, text?: string): ModuleEntity {
  const relativeRoot = `src/modules/entity/${objectId}`;
  const relativePath = `${relativeRoot}/record.json`;
  return {
    id: `module:entity/${objectId}`,
    familyId: "entity",
    family: "entity",
    moduleId: `entity/${objectId}`,
    objectId,
    title: objectId,
    subtitle: objectId,
    root: `/workspace/PIHC3/${relativeRoot}`,
    relativeRoot,
    sourceRoot: `/workspace/PIHC3/${relativeRoot}`,
    layout: "canonical",
    sourceCount: 1,
    sourceSlots: [{
      slot: "record",
      name: "record.json",
      path: `/workspace/PIHC3/${relativePath}`,
      relative_path: relativePath,
      extension: "json",
      draftKey: "record",
      editorKind: "code"
    }],
    tags: [],
    draftState: "clean",
    drafts: { text: text === undefined ? {} : { record: text } }
  };
}

function pdxEntityRecord(objectId: string, text: string): ModuleEntity {
  return pdxEntityRecordAt(objectId, text, "def.txt");
}

function pdxEntityRecordAt(
  objectId: string,
  text: string,
  moduleRelativePath: string
): ModuleEntity {
  const relativeRoot = `src/modules/idea/${objectId}`;
  const relativePath = `${relativeRoot}/${moduleRelativePath}`;
  const sourceName = moduleRelativePath.split("/").at(-1) ?? moduleRelativePath;
  const extension = sourceName.split(".").at(-1) ?? "";
  const draftKey = moduleRelativePath === "def.txt" ? "def" : moduleRelativePath;
  return {
    id: `module:idea/${objectId}`,
    familyId: "idea",
    family: "idea",
    moduleId: `idea/${objectId}`,
    objectId,
    title: objectId,
    subtitle: objectId,
    root: `/workspace/PIHC3/${relativeRoot}`,
    relativeRoot,
    sourceRoot: "/workspace/PIHC3/src",
    layout: "canonical",
    sourceCount: 1,
    sourceSlots: [{
      slot: "def",
      name: sourceName,
      path: `/workspace/PIHC3/${relativePath}`,
      relative_path: relativePath,
      extension,
      draftKey,
      editorKind: "code"
    }],
    tags: [],
    draftState: "clean",
    drafts: { text: { [draftKey]: text } }
  };
}

function entityRecordWithTwoSources(objectId: string): ModuleEntity {
  const entity = entityRecord(objectId);
  const relativeRoot = entity.relativeRoot;
  const sourceSlot = (slot: "primary" | "secondary") => {
    const relativePath = `${relativeRoot}/${slot}.json`;
    return {
      slot,
      name: `${slot}.json`,
      path: `/workspace/PIHC3/${relativePath}`,
      relative_path: relativePath,
      extension: "json",
      draftKey: slot,
      editorKind: "code" as const
    };
  };
  return {
    ...entity,
    sourceCount: 2,
    sourceSlots: [sourceSlot("primary"), sourceSlot("secondary")],
    drafts: {
      text: {
        primary: '{"slot":"primary"}',
        secondary: '{"slot":"secondary"}'
      }
    }
  };
}

function sourceForm(objectId: string, entity: ModuleEntity): SourceFormPayload {
  return sourceFormForSource(objectId, entity, 0);
}

function pdxSourceForm(objectId: string, entity: ModuleEntity, text: string): SourceFormPayload {
  const source = entity.sourceSlots[0];
  const expected = text.includes("yes") ? "yes" : "no";
  const start = text.indexOf(expected);
  return {
    schema: "paradev.source-form.v1",
    contract: "paradev.pdx.guided-form.v1",
    project_id: "PIHC3",
    family: "idea",
    module_id: `idea/${objectId}`,
    path: source.path,
    relative_path: source.relative_path,
    module_relative_path: source.name,
    source_root: entity.sourceRoot ?? entity.root,
    source_format: "pdx",
    label: "Guided PDX fields",
    sections: [{
      id: "pdx-section-000",
      label: "Top level",
      controls: [{
        id: "pdx-control-000",
        label: "Active",
        control: "boolean",
        value: expected === "yes",
        patch: {
          op: "replace-pdx-scalar",
          path: [{ key: "active", occurrence: 0 }],
          span: { start, end: start + expected.length },
          expected,
          scalar_kind: "boolean",
          source_length: text.length
        }
      }]
    }]
  };
}

function sourceFormForSource(objectId: string, entity: ModuleEntity, sourceIndex: number): SourceFormPayload {
  const source = entity.sourceSlots[sourceIndex];
  return {
    schema: "paradev.source-form.v1",
    contract: "pihc.entity.record.v1",
    project_id: "PIHC3",
    family: "entity",
    module_id: `entity/${objectId}`,
    path: source.path,
    relative_path: source.relative_path,
    module_relative_path: source.name,
    source_root: entity.sourceRoot ?? entity.root,
    source_format: "json",
    label: "Entity record",
    sections: []
  };
}

function deferred<T>() {
  let resolve!: (value: T | PromiseLike<T>) => void;
  let reject!: (reason?: unknown) => void;
  const promise = new Promise<T>((resolvePromise, rejectPromise) => {
    resolve = resolvePromise;
    reject = rejectPromise;
  });
  return { promise, reject, resolve };
}
