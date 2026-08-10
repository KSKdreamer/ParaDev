export type ProcessedEditorImageData = {
  name?: string;
  extension?: string;
  mimeType?: string;
  fullName?: string;
  width?: number;
  height?: number;
  imageBase64?: string;
  imageCanvas?: HTMLCanvasElement;
};

export type ProcessedPngImageDraft = {
  fileName: string;
  path?: string;
  previewUrl: string;
  contentBase64?: string;
  width?: number;
  height?: number;
};

export type ProcessedPngImageDraftInput = {
  imageData: ProcessedEditorImageData;
  path?: string;
  previewUrl: string;
  sourceName: string;
};

export function buildProcessedPngImageDraft({ imageData, path, previewUrl, sourceName }: ProcessedPngImageDraftInput): ProcessedPngImageDraft {
  const imageBase64 = imageData.imageBase64 ?? imageData.imageCanvas?.toDataURL("image/png");
  return {
    fileName: pngDraftFileName(imageData.fullName || imageData.name || sourceName),
    ...(path?.trim() ? { path: path.trim() } : {}),
    previewUrl,
    contentBase64: imageBase64 ? rawBase64ImagePayload(imageBase64) : undefined,
    width: imageData.width,
    height: imageData.height
  };
}

export function pngDraftFileName(value: string): string {
  if (value.trim().startsWith("data:")) {
    return "image.png";
  }
  const name = value.split(/[?#]/, 1)[0]?.split(/[\\/]/).at(-1)?.trim() || "image";
  const stem = name.replace(/\.[^.]+$/, "") || "image";
  return `${stem}.png`;
}

export function rawBase64ImagePayload(value: string): string {
  return value.includes(",") ? value.split(",").at(-1) ?? "" : value;
}
