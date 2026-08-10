import { FileUp, Replace, Trash2 } from "lucide-react";
import { useCallback, useRef, useState } from "react";
import { useDropzone } from "react-dropzone";
import { SelectField } from "../components/ui/SelectField";
import type { Translator } from "../i18n";
import {
  assetDraftPathError,
  assetDraftTargetForFile,
  assetDraftTargetIdentity,
  assetDraftTargetsForFile,
  type ModuleAssetDraft,
  type ModuleEntity,
  type ModuleSourceSlot,
} from "./model";

type AssetDraftEditorProps = {
  entity: ModuleEntity;
  sources: ModuleSourceSlot[];
  t: Translator;
  onAssetDrafts: (assets: ModuleAssetDraft[]) => void;
};

const MAX_ASSET_BYTES = 64 * 1024 * 1024;
const MAX_ASSET_BATCH_BYTES = 64 * 1024 * 1024;
const MAX_ASSET_FILES = 32;
const EMPTY_ASSET_DRAFTS: ModuleAssetDraft[] = [];

export function AssetDraftEditor({
  entity,
  sources,
  t,
  onAssetDrafts,
}: AssetDraftEditorProps) {
  const [error, setError] = useState("");
  const drafts = entity.drafts.assets ?? EMPTY_ASSET_DRAFTS;
  const draftsRef = useRef(drafts);
  const renderedDraftsRef = useRef(drafts);
  const nextSelectionIdRef = useRef(0);
  const latestSelectionByTargetRef = useRef(new Map<string, number>());
  if (renderedDraftsRef.current !== drafts) {
    renderedDraftsRef.current = drafts;
    draftsRef.current = drafts;
  }

  const stageFiles = useCallback(
    async (files: File[], source?: ModuleSourceSlot) => {
      setError("");
      if (files.length === 0) {
        return;
      }
      if (files.length > MAX_ASSET_FILES) {
        setError(
          t("workspace.module.editor.assetTooMany", { count: MAX_ASSET_FILES }),
        );
        return;
      }
      const oversized = files.find((file) => file.size > MAX_ASSET_BYTES);
      if (oversized) {
        setError(
          t("workspace.module.editor.assetTooLarge", {
            name: oversized.name,
            size: "64 MB",
          }),
        );
        return;
      }
      const empty = files.find((file) => file.size === 0);
      if (empty) {
        setError(t("workspace.module.editor.assetEmpty", { name: empty.name }));
        return;
      }
      if (
        files.reduce((total, file) => total + file.size, 0) >
        MAX_ASSET_BATCH_BYTES
      ) {
        setError(
          t("workspace.module.editor.assetBatchTooLarge", { size: "64 MB" }),
        );
        return;
      }
      const selectionId = nextSelectionIdRef.current + 1;
      nextSelectionIdRef.current = selectionId;
      const planned = files.map((file) => {
        const matchingSource =
          source ?? matchingAssetSource(sources, file.name);
        const declaredTarget = matchingSource
          ? {
              path: matchingSource.relative_path || matchingSource.path,
              slotName: matchingSource.slot,
            }
          : assetDraftTargetForFile(entity, file.name);
        const path = declaredTarget?.path ?? "";
        const targetKey = assetSelectionTargetKey(
          entity,
          file.name,
          path,
          matchingSource,
        );
        latestSelectionByTargetRef.current.set(targetKey, selectionId);
        return {
          file,
          matchingSource,
          path,
          slotName: declaredTarget?.slotName,
          targetKey,
        };
      });
      try {
        const staged: Array<ModuleAssetDraft & { selectionTargetKey: string }> =
          [];
        let firstPathError = "";
        for (const item of planned) {
          const { file, matchingSource, path, slotName, targetKey } = item;
          const draft: ModuleAssetDraft = {
            contentBase64: await fileBase64(file, t),
            fileName: file.name,
            path,
            size: file.size,
            ...(slotName ? { slotName } : {}),
            ...(matchingSource ? { sourceKey: matchingSource.draftKey } : {}),
          };
          if (
            latestSelectionByTargetRef.current.get(targetKey) !== selectionId
          ) {
            continue;
          }
          const pathError = assetDraftPathError(entity, draft);
          if (pathError && !firstPathError) {
            firstPathError = assetPathErrorMessage(pathError, draft.path, t);
          }
          staged.push({ ...draft, selectionTargetKey: targetKey });
        }
        const currentStaged = staged.filter(
          (draft) =>
            latestSelectionByTargetRef.current.get(draft.selectionTargetKey) ===
            selectionId,
        );
        if (currentStaged.length === 0) {
          return;
        }
        const next = [...draftsRef.current];
        const stagedTargets = new Set<string>();
        for (const {
          selectionTargetKey: _selectionTargetKey,
          ...draft
        } of currentStaged) {
          const target = assetDraftTargetIdentity(entity, draft.path);
          const existingIndex = target
            ? next.findIndex(
                (item) =>
                  assetDraftTargetIdentity(entity, item.path) === target,
              )
            : -1;
          if (
            target &&
            (stagedTargets.has(target) ||
              (existingIndex >= 0 &&
                (!source || next[existingIndex].sourceKey !== draft.sourceKey)))
          ) {
            setError(
              t("workspace.module.editor.assetDuplicateTarget", {
                path: draft.path,
              }),
            );
            return;
          }
          if (existingIndex >= 0) {
            next[existingIndex] = draft;
          } else {
            next.push(draft);
          }
          if (target) {
            stagedTargets.add(target);
          }
        }
        if (next.length > MAX_ASSET_FILES) {
          setError(
            t("workspace.module.editor.assetTooMany", {
              count: MAX_ASSET_FILES,
            }),
          );
          return;
        }
        if (
          next.reduce((total, draft) => total + draft.size, 0) >
          MAX_ASSET_BATCH_BYTES
        ) {
          setError(
            t("workspace.module.editor.assetBatchTooLarge", { size: "64 MB" }),
          );
          return;
        }
        draftsRef.current = next;
        onAssetDrafts(next);
        setError(firstPathError);
      } catch (cause) {
        setError(cause instanceof Error ? cause.message : String(cause));
      } finally {
        for (const { targetKey } of planned) {
          if (
            latestSelectionByTargetRef.current.get(targetKey) === selectionId
          ) {
            latestSelectionByTargetRef.current.delete(targetKey);
          }
        }
      }
    },
    [entity, onAssetDrafts, sources, t],
  );

  const { getInputProps, getRootProps, isDragActive, isDragReject } =
    useDropzone({
      maxFiles: MAX_ASSET_FILES,
      onDropAccepted: (files) => void stageFiles(files),
      onDropRejected: () =>
        setError(
          t("workspace.module.editor.assetDropRejected", {
            count: MAX_ASSET_FILES,
          }),
        ),
    });

  const updateDraftPath = (index: number, path: string) => {
    const next = drafts.map((draft, draftIndex) => {
      if (draftIndex !== index) {
        return draft;
      }
      const updated = { ...draft, path };
      if (!draft.sourceKey) {
        delete updated.slotName;
      }
      return updated;
    });
    draftsRef.current = next;
    setError("");
    onAssetDrafts(next);
  };
  const updateDraftTarget = (
    index: number,
    target: { path: string; slotName: string } | null,
  ) => {
    const next = drafts.map((draft, draftIndex) => {
      if (draftIndex !== index) {
        return draft;
      }
      if (target) {
        return { ...draft, path: target.path, slotName: target.slotName };
      }
      const updated = { ...draft, path: "" };
      delete updated.slotName;
      return updated;
    });
    draftsRef.current = next;
    setError("");
    onAssetDrafts(next);
  };
  const removeDraft = (index: number) => {
    const next = drafts.filter((_, draftIndex) => draftIndex !== index);
    draftsRef.current = next;
    setError("");
    onAssetDrafts(next);
  };

  return (
    <div className="asset-draft-editor">
      <section className="asset-editor-intro">
        <strong>{t("workspace.module.editor.assetHeading")}</strong>
        <p>{t("workspace.module.editor.assetHelp")}</p>
      </section>
      <div
        {...getRootProps({
          className: isDragReject
            ? "asset-dropzone rejected"
            : "asset-dropzone",
        })}
      >
        <input {...getInputProps()} />
        <FileUp aria-hidden="true" size={18} />
        <span>
          {isDragActive
            ? t("workspace.module.editor.assetDropActive")
            : t("workspace.module.editor.assetPick")}
        </span>
      </div>
      {error ? (
        <small className="project-path error" role="alert">
          {error}
        </small>
      ) : null}
      {sources.length > 0 ? (
        <section
          className="asset-source-list"
          aria-label={t("workspace.module.editor.assetExisting")}
        >
          <header>
            <strong>{t("workspace.module.editor.assetExisting")}</strong>
            <span>
              {t("workspace.module.editor.assetExistingCount", {
                count: sources.length,
              })}
            </span>
          </header>
          {sources.map((source) => (
            <div className="asset-source-row" key={source.draftKey}>
              <span>
                <strong>{source.name}</strong>
                <small className="asset-source-owner">
                  {[source.slot, ...(source.slot_kinds ?? [])].join(" · ")}
                </small>
                <code title={source.relative_path || source.path}>
                  {source.relative_path || source.path}
                </code>
              </span>
              <span className="asset-source-meta">
                {formatBytes(source.size)}
              </span>
              <label className="toolbar-button asset-replace-button">
                <Replace aria-hidden="true" size={13} />
                {t("workspace.module.editor.assetReplace")}
                <input
                  accept={
                    source.extension
                      ? `.${source.extension.replace(/^\./, "")}`
                      : undefined
                  }
                  onChange={(event) => {
                    const files = Array.from(event.target.files ?? []);
                    event.target.value = "";
                    void stageFiles(files, source);
                  }}
                  type="file"
                />
              </label>
            </div>
          ))}
        </section>
      ) : (
        <div className="asset-source-empty">
          {t("workspace.module.editor.assetNone")}
        </div>
      )}
      {drafts.length > 0 ? (
        <section
          className="asset-draft-list"
          aria-label={t("workspace.module.editor.assetPending")}
        >
          <header>
            <strong>{t("workspace.module.editor.assetPending")}</strong>
            <span>
              {t("workspace.module.editor.assetPendingCount", {
                count: drafts.length,
              })}
            </span>
          </header>
          {drafts.map((draft, index) => {
            const pathError = assetDraftPathError(entity, draft);
            const targetOptions = draft.sourceKey
              ? []
              : assetDraftTargetsForFile(entity, draft.fileName);
            const selectedTarget = targetOptions.find(
              (target) =>
                assetDraftTargetIdentity(entity, target.path) ===
                assetDraftTargetIdentity(entity, draft.path),
            );
            return (
              <div
                className="asset-draft-row"
                key={`${draft.sourceKey ?? "new"}:${draft.fileName}:${index}`}
              >
                <span className="asset-draft-name">
                  <strong>{draft.fileName}</strong>
                  <small>{formatBytes(draft.size)}</small>
                  {draft.slotName ? (
                    <small className="asset-source-owner">
                      {draft.slotName} · copy
                    </small>
                  ) : null}
                </span>
                <div className="asset-draft-target">
                  {targetOptions.length > 1 ? (
                    <SelectField
                      aria-invalid={Boolean(pathError) || undefined}
                      label={t("workspace.module.editor.assetDestination")}
                      onChange={(event) =>
                        updateDraftTarget(
                          index,
                          targetOptions.find(
                            (target) => target.path === event.target.value,
                          ) ?? null,
                        )
                      }
                      options={[
                        {
                          label: t(
                            "workspace.module.editor.assetDestinationChoose",
                          ),
                          value: "",
                        },
                        ...targetOptions.map((target) => ({
                          label: target.modulePath,
                          value: target.path,
                        })),
                      ]}
                      value={selectedTarget?.path ?? ""}
                      variant="compact"
                    />
                  ) : null}
                  <label>
                    <span>{t("workspace.module.editor.assetTargetPath")}</span>
                    <input
                      aria-invalid={Boolean(pathError) || undefined}
                      onChange={(event) =>
                        updateDraftPath(index, event.target.value)
                      }
                      readOnly={Boolean(draft.sourceKey)}
                      title={draft.path}
                      value={draft.path}
                    />
                  </label>
                  {!draft.sourceKey && targetOptions.length === 0 ? (
                    <small className="asset-target-help">
                      {t("workspace.module.editor.assetTargetPathHelp")}
                    </small>
                  ) : null}
                  {pathError ? (
                    <small className="project-path error">
                      {assetPathErrorMessage(pathError, draft.path, t)}
                    </small>
                  ) : null}
                </div>
                <button
                  aria-label={t("workspace.module.editor.assetDiscard", {
                    name: draft.fileName,
                  })}
                  className="toolbar-button icon-only"
                  onClick={() => removeDraft(index)}
                  title={t("workspace.module.editor.assetDiscard", {
                    name: draft.fileName,
                  })}
                  type="button"
                >
                  <Trash2 aria-hidden="true" size={13} />
                </button>
              </div>
            );
          })}
        </section>
      ) : null}
    </div>
  );
}

function matchingAssetSource(
  sources: ModuleSourceSlot[],
  fileName: string,
): ModuleSourceSlot | undefined {
  const normalizedName = fileName.trim().toLocaleLowerCase();
  const matches = sources.filter(
    (source) => source.name.trim().toLocaleLowerCase() === normalizedName,
  );
  return matches.length === 1 ? matches[0] : undefined;
}

function assetSelectionTargetKey(
  entity: ModuleEntity,
  fileName: string,
  path: string,
  source: ModuleSourceSlot | undefined,
): string {
  const target = assetDraftTargetIdentity(entity, path);
  if (target) {
    return `path:${target}`;
  }
  if (source) {
    return `source:${source.draftKey}`;
  }
  return `file:${fileName.trim().normalize("NFC").toLocaleLowerCase("en-US")}`;
}

function fileBase64(file: File, t: Translator): Promise<string> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onerror = () =>
      reject(
        new Error(
          t("workspace.module.editor.assetReadFailed", { name: file.name }),
        ),
      );
    reader.onload = () => {
      const value = reader.result;
      if (typeof value !== "string" || !value.includes(",")) {
        reject(
          new Error(
            t("workspace.module.editor.assetEncodeFailed", { name: file.name }),
          ),
        );
        return;
      }
      resolve(value.slice(value.indexOf(",") + 1));
    };
    reader.readAsDataURL(file);
  });
}

function assetPathErrorMessage(
  error: "duplicate" | "empty" | "format" | "outside" | "slot" | "source",
  path: string,
  t: Translator,
): string {
  if (error === "empty") {
    return t("workspace.module.editor.assetPathEmpty");
  }
  if (error === "slot") {
    return t("workspace.module.editor.assetPathSlot", { name: path });
  }
  if (error === "format") {
    return t("workspace.module.editor.assetPathFormat");
  }
  if (error === "duplicate") {
    return t("workspace.module.editor.assetDuplicateTarget", { path });
  }
  if (error === "source") {
    return t("workspace.module.editor.assetPathSource", {
      path: path || t("workspace.module.editor.assetPathUnknown"),
    });
  }
  return t("workspace.module.editor.assetPathOutside");
}

function formatBytes(size: number | undefined): string {
  if (size === undefined) {
    return "";
  }
  if (size < 1024) {
    return `${size} B`;
  }
  if (size < 1024 * 1024) {
    return `${(size / 1024).toFixed(1)} KB`;
  }
  return `${(size / (1024 * 1024)).toFixed(1)} MB`;
}
