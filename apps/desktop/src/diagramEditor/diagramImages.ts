import { loadThumbnailUrl, type ThumbnailLoadOptions } from "../moduleEditor/thumbnailLoader";
import type { DiagramNode, DiagramNodeId } from "./layoutModel";

export type DiagramImageLoadOptions = {
  nodes: DiagramNode[];
  onProgress?: (progress: DiagramImageLoadProgress) => void;
  projectRoot: string;
  sideLength: number | DiagramImageSideLengthResolver;
};

export type DiagramImageLoader = (request: ThumbnailLoadOptions) => Promise<string>;
export type DiagramImageLoadProgress = {
  completed: number;
  hydrated: number;
  total: number;
};
export type DiagramImageSideLengthResolver = (node: DiagramNode) => number;

const DIAGRAM_IMAGE_DPI_SCALE = 2;
// PIHC3 technology trees approach 300 local icons. Four workers keep the native
// bridge and browser image decoder responsive without making hydration serial.
const DIAGRAM_IMAGE_HYDRATION_CONCURRENCY = 4;

export async function loadDiagramImageUrls(options: DiagramImageLoadOptions, loader: DiagramImageLoader = loadThumbnailUrl): Promise<Record<DiagramNodeId, string>> {
  const projectRoot = options.projectRoot.trim();
  if (!projectRoot) {
    return {};
  }
  const nodes = options.nodes.filter(diagramNodeNeedsImageHydration);
  if (nodes.length === 0) {
    return {};
  }
  let completed = 0;
  let hydrated = 0;
  options.onProgress?.({ completed, hydrated, total: nodes.length });

  const entries = await mapDiagramImagesWithBoundedConcurrency(
    nodes,
    async (node): Promise<[DiagramNodeId, string] | null> => {
      const imageUrl = node.imageUrl?.trim();
      if (!imageUrl) return null;
      const sideLength = diagramImageHydrationSideLength(diagramImageSideLength(options.sideLength, node));
      const loaded = await loadDiagramNodeImageUrl(loader, {
        cacheKey: diagramImageCacheKey(node, sideLength),
        projectRoot,
        sourcePaths: diagramImageSourcePaths(imageUrl, projectRoot),
        transform: (sourceUrl) => cropDiagramImageToSquare(sourceUrl, sideLength)
      });
      completed += 1;
      if (loaded) {
        hydrated += 1;
      }
      options.onProgress?.({ completed, hydrated, total: nodes.length });
      return loaded ? [node.id, loaded] : null;
    }
  );
  return Object.fromEntries(entries.filter((entry): entry is [DiagramNodeId, string] => Boolean(entry)));
}

export function diagramImageHydrationNodeCount(nodes: Pick<DiagramNode, "imageUrl">[]): number {
  return nodes.filter(diagramNodeNeedsImageHydration).length;
}

function diagramNodeNeedsImageHydration(node: Pick<DiagramNode, "imageUrl">): boolean {
  const imageUrl = node.imageUrl?.trim();
  return Boolean(imageUrl && !isDirectDiagramImageUrl(imageUrl));
}

async function loadDiagramNodeImageUrl(loader: DiagramImageLoader, request: ThumbnailLoadOptions): Promise<string> {
  try {
    return await loader(request);
  } catch {
    return "";
  }
}

async function mapDiagramImagesWithBoundedConcurrency<Result>(
  nodes: DiagramNode[],
  hydrate: (node: DiagramNode) => Promise<Result>
): Promise<Result[]> {
  const results = new Array<Result>(nodes.length);
  let nextIndex = 0;
  const worker = async (): Promise<void> => {
    while (nextIndex < nodes.length) {
      const index = nextIndex;
      nextIndex += 1;
      const node = nodes[index];
      if (!node) continue;
      results[index] = await hydrate(node);
    }
  };
  const workerCount = Math.min(DIAGRAM_IMAGE_HYDRATION_CONCURRENCY, nodes.length);
  await Promise.all(Array.from({ length: workerCount }, () => worker()));
  return results;
}

function diagramImageSideLength(sideLength: DiagramImageLoadOptions["sideLength"], node: DiagramNode): number {
  return typeof sideLength === "function" ? sideLength(node) : sideLength;
}

export function diagramImageHydrationSideLength(sideLength: number): number {
  return Math.max(1, Math.round(sideLength * DIAGRAM_IMAGE_DPI_SCALE));
}

export function diagramImageCacheKey(node: Pick<DiagramNode, "id" | "imageUrl">, sideLength: number): string {
  return `v1|diagram|${Math.max(1, Math.round(sideLength))}|${node.id}|${node.imageUrl?.trim() ?? ""}`;
}

export function isDirectDiagramImageUrl(value: string): boolean {
  return /^(?:asset|blob|data|https?):/i.test(value.trim());
}

function diagramImageSourcePaths(imageUrl: string, projectRoot: string): string[] {
  const clean = imageUrl.trim();
  if (isAbsolutePath(clean)) {
    return [clean];
  }
  const relativePath = clean.replace(/^[\\/]+/, "");
  return relativePath ? [relativePath] : [projectRoot.trim()];
}

function isAbsolutePath(value: string): boolean {
  return value.startsWith("/") || /^[A-Za-z]:[\\/]/.test(value);
}

async function cropDiagramImageToSquare(sourceUrl: string, sideLength: number): Promise<string> {
  const image = await loadImage(sourceUrl);
  const naturalWidth = image.naturalWidth || image.width;
  const naturalHeight = image.naturalHeight || image.height;
  if (naturalWidth <= 0 || naturalHeight <= 0) {
    return "";
  }
  const canvas = document.createElement("canvas");
  const size = Math.max(1, Math.round(sideLength));
  canvas.width = size;
  canvas.height = size;
  const context = canvas.getContext("2d");
  if (!context) {
    return "";
  }
  const scale = size / Math.min(naturalWidth, naturalHeight);
  const width = naturalWidth * scale;
  const height = naturalHeight * scale;
  context.drawImage(image, (size - width) / 2, (size - height) / 2, width, height);
  return canvas.toDataURL("image/png");
}

function loadImage(sourceUrl: string): Promise<HTMLImageElement> {
  return new Promise((resolve, reject) => {
    const image = new Image();
    image.onload = () => resolve(image);
    image.onerror = () => reject(new Error("Cannot load diagram node image."));
    image.decoding = "async";
    image.src = sourceUrl;
  });
}
