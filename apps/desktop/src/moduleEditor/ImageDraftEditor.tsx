import { useCallback, useEffect, useMemo, useRef, useState, type ComponentProps } from "react";
import FilerobotImageEditor, { TABS, TOOLS, type getCurrentImgDataFunction } from "react-filerobot-image-editor";
import { ImagePlus, Link, Save } from "lucide-react";
import { useDropzone } from "react-dropzone";
import type { Translator } from "../i18n";
import type { ThemeName } from "../types";
import { buildProcessedPngImageDraft, pngDraftFileName, rawBase64ImagePayload } from "./imageDraft";
import { canPreviewImageSourceInEditor, canReplaceImageSource, imageSourceFormat, imageSourceRequiresConversion, type ModuleEntity, type ModuleEntityDrafts, type ModuleSourceSlot } from "./model";

type ImageDraftEditorProps = {
  defaultSavePath: string;
  entity: ModuleEntity;
  initialImageSource?: string;
  source: ModuleSourceSlot | null;
  t: Translator;
  theme: ThemeName;
  onImageDraft: (image: NonNullable<ModuleEntityDrafts["image"]>) => void;
};

type FilerobotTheme = NonNullable<ComponentProps<typeof FilerobotImageEditor>["theme"]>;

const FILEROBOT_TABS = [TABS.ADJUST, TABS.FINETUNE, TABS.FILTERS, TABS.WATERMARK, TABS.ANNOTATE, TABS.RESIZE];
const FONT_STACK = 'Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif';
const THEME_BY_NAME: Record<ThemeName, FilerobotTheme> = {
  light: filerobotTheme({
    bg: "#ffffff",
    bg2: "#f1f1ef",
    bg3: "#e9e9e6",
    text: "#171717",
    muted: "#6f6f6a",
    border: "#deded9",
    borderStrong: "#c8c8c1",
    accent: "#2f6f68",
    danger: "#b54545",
    warning: "#a06419",
    success: "#2f7652"
  }),
  dark: filerobotTheme({
    bg: "#161b22",
    bg2: "#21262d",
    bg3: "#30363d",
    text: "#e6edf3",
    muted: "#8b949e",
    border: "#30363d",
    borderStrong: "#484f58",
    accent: "#58a6ff",
    danger: "#f85149",
    warning: "#d29922",
    success: "#3fb950"
  }),
  anthropic: filerobotTheme({
    bg: "#faf9f5",
    bg2: "#e8e6dc",
    bg3: "#d1cfc5",
    text: "#141413",
    muted: "#5e5d59",
    border: "#1414131a",
    borderStrong: "#14141333",
    accent: "#c6613f",
    danger: "#c25b4e",
    warning: "#d9853b",
    success: "#059669"
  })
};

export function ImageDraftEditor({ defaultSavePath, entity, initialImageSource = "", source, t, theme, onImageDraft }: ImageDraftEditorProps) {
  const image = entity.drafts.image;
  const initialEditorSource = canPreviewImageSourceInEditor(source) ? initialImageSource : "";
  const [editorSource, setEditorSource] = useState(image?.previewUrl ?? initialEditorSource);
  const [sourceName, setSourceName] = useState(image?.fileName ?? source?.name ?? "image.png");
  const [savePath, setSavePath] = useState(image?.path ?? defaultSavePath);
  const [urlValue, setUrlValue] = useState("");
  const [editorError, setEditorError] = useState("");
  const editorDataRef = useRef<getCurrentImgDataFunction | undefined>(undefined);
  const objectUrlRef = useRef("");
  const defaultImageName = useMemo(() => pngDraftFileName(sourceName).replace(/\.png$/, ""), [sourceName]);
  const savePathError = useMemo(() => imageDraftSavePathError(savePath, source, t), [savePath, source, t]);
  const conversionFormat = imageSourceRequiresConversion(source) ? imageSourceFormat(source).toUpperCase() : "";

  useEffect(() => {
    setEditorSource(image?.previewUrl ?? initialEditorSource);
    setSourceName(image?.fileName ?? source?.name ?? "image.png");
    setSavePath(image?.path ?? defaultSavePath);
    setEditorError("");
  }, [defaultSavePath, entity.id, image?.fileName, image?.path, image?.previewUrl, initialEditorSource, source?.name]);

  useEffect(
    () => () => {
      if (objectUrlRef.current) {
        URL.revokeObjectURL(objectUrlRef.current);
      }
    },
    []
  );

  const setFileSource = useCallback((file: File) => {
    if (objectUrlRef.current) {
      URL.revokeObjectURL(objectUrlRef.current);
    }
    const url = URL.createObjectURL(file);
    objectUrlRef.current = url;
    setSourceName(file.name);
    setEditorSource(url);
    setEditorError("");
  }, []);

  const onDrop = useCallback(
    (acceptedFiles: File[]) => {
      const file = acceptedFiles[0];
      if (file) {
        setFileSource(file);
      }
    },
    [setFileSource]
  );
  const { getInputProps, getRootProps, isDragActive, isDragReject } = useDropzone({
    accept: {
      "image/png": [".png"],
      "image/jpeg": [".jpg", ".jpeg"],
      "image/webp": [".webp"],
      "image/bmp": [".bmp"]
    },
    maxFiles: 1,
    onDrop
  });

  const handleLoadUrl = useCallback(() => {
    const value = urlValue.trim();
    if (!value) {
      return;
    }
    setSourceName(value);
    setEditorSource(value);
    setEditorError("");
  }, [urlValue]);

  const handleSaveDraft = useCallback(() => {
    const saveCurrentImage = editorDataRef.current;
    if (!saveCurrentImage || !editorSource || savePathError) {
      return;
    }
    try {
      const { imageData, hideLoadingSpinner } = saveCurrentImage({ name: defaultImageName, extension: "png", quality: 1 }, 2);
      const imageBase64 = imageData.imageBase64 ?? imageData.imageCanvas?.toDataURL("image/png");
      const previewUrl = imageBase64?.startsWith("data:") ? imageBase64 : imageBase64 ? `data:image/png;base64,${rawBase64ImagePayload(imageBase64)}` : editorSource;
      onImageDraft(
        buildProcessedPngImageDraft({
          imageData: { ...imageData, imageBase64 },
          previewUrl,
          path: savePath.trim() || defaultSavePath,
          sourceName
        })
      );
      hideLoadingSpinner?.();
      setEditorError("");
    } catch (error) {
      setEditorError(t("workspace.module.editor.imageEditorError", { message: error instanceof Error ? error.message : String(error) }));
    }
  }, [defaultImageName, defaultSavePath, editorSource, onImageDraft, savePath, savePathError, sourceName, t]);

  return (
    <div className="image-draft-editor">
      <div className="image-source-summary">
        <div className="image-source-row">
          <span>
            <strong>{image?.fileName ?? source?.name ?? t("workspace.module.editor.noImage")}</strong>
            <small>{source?.relative_path || t("workspace.module.editor.imageDraftOnly")}</small>
          </span>
          {image?.contentBase64 ? <span className="status-pill ready">{t("workspace.module.editor.imageDraftReady")}</span> : null}
        </div>
        {conversionFormat ? (
          <p aria-live="polite" className="image-conversion-notice" role="status">
            {t("workspace.module.editor.imageConversionPlanned", { format: conversionFormat })}
          </p>
        ) : source?.exists === false ? (
          <p aria-live="polite" className="image-conversion-notice" role="status">
            {t("workspace.module.editor.imageCreationPlanned")}
          </p>
        ) : null}
      </div>
      <div className="image-source-controls">
        <div {...getRootProps({ className: isDragReject ? "image-dropzone rejected" : "image-dropzone" })}>
          <input {...getInputProps()} />
          <ImagePlus aria-hidden="true" size={18} />
          <span>{isDragActive ? t("workspace.module.editor.dropImage") : t("workspace.module.editor.pickImage")}</span>
        </div>
        <label className="image-url-field">
          <Link aria-hidden="true" size={14} />
          <input
            onChange={(event) => setUrlValue(event.target.value)}
            onKeyDown={(event) => {
              if (event.key === "Enter") {
                handleLoadUrl();
              }
            }}
            placeholder={t("workspace.module.editor.imageUrlPlaceholder")}
            type="url"
            value={urlValue}
          />
          <button className="toolbar-button primary" disabled={!urlValue.trim()} onClick={handleLoadUrl} type="button">
            {t("workspace.module.editor.loadImageUrl")}
          </button>
        </label>
      </div>
      <label className="image-path-field">
        <span>{t("workspace.module.editor.imageSavePath")}</span>
        <input
          aria-invalid={Boolean(savePathError) || undefined}
          onChange={(event) => setSavePath(event.target.value)}
          placeholder={defaultSavePath}
          readOnly={Boolean(source?.path || source?.relative_path)}
          type="text"
          value={savePath}
        />
        {savePathError ? <small className="project-path error" role="alert">{savePathError}</small> : null}
      </label>
      {editorSource ? (
        <div className="filerobot-editor-frame">
          <FilerobotImageEditor
            source={editorSource}
            theme={THEME_BY_NAME[theme]}
            tabsIds={FILEROBOT_TABS}
            defaultTabId={TABS.ADJUST}
            defaultToolId={TOOLS.CROP}
            defaultSavedImageName={defaultImageName}
            defaultSavedImageType="png"
            defaultSavedImageQuality={1}
            savingPixelRatio={2}
            previewPixelRatio={1}
            closeAfterSave={false}
            removeSaveButton
            resetOnSourceChange
            getCurrentImgDataFnRef={editorDataRef}
            annotationsCommon={{ fill: "#2f6f68", stroke: "#2f6f68", strokeWidth: 2 }}
            Text={{ text: entity.title, fontFamily: FONT_STACK, fontSize: 28 }}
            Rotate={{ angle: 90, componentType: "slider" }}
            Crop={{
              ratio: "original",
              presetsItems: [
                { titleKey: "square", descriptionKey: "1:1", ratio: 1 },
                { titleKey: "classicTv", descriptionKey: "4:3", ratio: 4 / 3 },
                { titleKey: "cinemascope", descriptionKey: "16:9", ratio: 16 / 9 }
              ]
            }}
            Watermark={{ textScalingRatio: 0.26, imageScalingRatio: 0.26 }}
            Pen={{ stroke: "#2f6f68", strokeWidth: 4, selectAnnotationAfterDrawing: true }}
          />
        </div>
      ) : (
        <div className="image-editor-empty">
          {source && !canPreviewImageSourceInEditor(source)
            ? t("workspace.module.editor.imageReplacementInputRequired", { format: imageSourceFormat(source).toUpperCase() || source.name })
            : t("workspace.module.editor.noImage")}
        </div>
      )}
      <div className="image-editor-actions">
        {editorError ? <small className="project-path error">{editorError}</small> : null}
        <button className="toolbar-button primary" disabled={!editorSource || Boolean(savePathError)} onClick={handleSaveDraft} type="button">
          <Save aria-hidden="true" size={14} />
          {t("workspace.module.editor.saveImage")}
        </button>
      </div>
    </div>
  );
}

function imageDraftSavePathError(savePath: string, source: ModuleSourceSlot | null, t: Translator): string {
  if (!source?.path && !source?.relative_path) {
    return t("workspace.module.editor.imageTargetUnavailable");
  }
  const targetPath = savePath.trim();
  if (!targetPath) {
    return "";
  }
  const format = imagePathExtension(targetPath);
  if (!canReplaceImageSource(source)) {
    return t("workspace.module.editor.imageFormatUnsupported", { format: imageSourceFormat(source).toUpperCase() || source.name });
  }
  if (!imagePathMatchesSource(targetPath, source)) {
    if (imageSourceFormat(source) === "png" && format !== "png") {
      return t("workspace.module.editor.imagePngPathRequired", { format: format.toUpperCase() || targetPath });
    }
    return t(
      source.exists === false
        ? "workspace.module.editor.imageDeclaredPathRequired"
        : "workspace.module.editor.imageSelectedPathRequired",
      { path: source.relative_path || source.path }
    );
  }
  return "";
}

function imagePathMatchesSource(path: string, source: ModuleSourceSlot): boolean {
  const target = normalizedComparablePath(path);
  return [source.path, source.relative_path].some((candidate) => candidate && normalizedComparablePath(candidate) === target);
}

function imagePathExtension(path: string): string {
  const cleanPath = path.trim().split(/[?#]/, 1)[0] ?? "";
  return (cleanPath.match(/\.([^/.\\]+)$/)?.[1] ?? "").toLowerCase();
}

function normalizedComparablePath(path: string): string {
  const normalized = path.trim().replace(/\\/g, "/").replace(/\/+$/, "");
  return /^[A-Za-z]:\//.test(normalized) ? normalized.toLowerCase() : normalized;
}

function filerobotTheme(colors: {
  bg: string;
  bg2: string;
  bg3: string;
  text: string;
  muted: string;
  border: string;
  borderStrong: string;
  accent: string;
  danger: string;
  warning: string;
  success: string;
}): FilerobotTheme {
  return {
    palette: {
      "bg-primary": colors.bg,
      "bg-secondary": colors.bg2,
      "bg-primary-hover": colors.bg2,
      "bg-primary-active": colors.bg3,
      "txt-primary": colors.text,
      "txt-secondary": colors.muted,
      "txt-placeholder": colors.muted,
      "icons-primary": colors.text,
      "icons-secondary": colors.muted,
      "accent-primary": colors.accent,
      "accent-primary-hover": colors.accent,
      "accent-primary-active": colors.accent,
      "accent-stateless": colors.accent,
      "borders-primary": colors.border,
      "borders-secondary": colors.border,
      "borders-strong": colors.borderStrong,
      error: colors.danger,
      warning: colors.warning,
      success: colors.success
    } as FilerobotTheme["palette"]
  };
}
