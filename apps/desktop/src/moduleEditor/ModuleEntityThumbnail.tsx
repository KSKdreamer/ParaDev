import { useEffect, useMemo, useRef, useState } from "react";
import {
  defaultImageDraftPath,
  moduleEntityThumbnailCacheKey,
  moduleEntityThumbnailSource,
  type ModuleEntity,
  type ModuleSourceSlot
} from "./model";
import { loadThumbnailUrl } from "./thumbnailLoader";

type ModuleEntityThumbnailProps = {
  entity: ModuleEntity;
  projectRoot: string;
};

const THUMBNAIL_SIDE = 36;
const THUMBNAIL_PRELOAD_MARGIN = "96px 0px";
const memoryCache = new Map<string, string>();

export function ModuleEntityThumbnail({ entity, projectRoot }: ModuleEntityThumbnailProps) {
  const source = useMemo(() => moduleEntityThumbnailSource(entity), [entity]);
  const cacheKey = useMemo(() => moduleEntityThumbnailCacheKey(entity, source, THUMBNAIL_SIDE), [entity, source]);
  const draftPreview = entity.drafts.image?.previewUrl ?? "";
  const canShowThumbnail = Boolean(source || draftPreview);
  const thumbnailRef = useRef<HTMLSpanElement>(null);
  const [loadEligible, setLoadEligible] = useState(() => typeof IntersectionObserver === "undefined");
  const [thumbnailUrl, setThumbnailUrl] = useState("");

  useEffect(() => {
    if (!canShowThumbnail || loadEligible) {
      return;
    }
    const target = thumbnailRef.current;
    if (!target || typeof IntersectionObserver === "undefined") {
      setLoadEligible(true);
      return;
    }
    const observer = new IntersectionObserver(
      (entries) => {
        if (entries.some((entry) => entry.isIntersecting)) {
          observer.disconnect();
          setLoadEligible(true);
        }
      },
      { rootMargin: THUMBNAIL_PRELOAD_MARGIN }
    );
    observer.observe(target);
    return () => observer.disconnect();
  }, [canShowThumbnail, loadEligible]);

  useEffect(() => {
    if (!loadEligible) {
      return;
    }
    let cancelled = false;
    const load = async () => {
      if (!canShowThumbnail) {
        setThumbnailUrl("");
        return;
      }
      if (draftPreview) {
        const cropped = await cropImageToSquare(draftPreview, THUMBNAIL_SIDE);
        if (!cancelled) {
          setThumbnailUrl(cropped);
        }
        return;
      }
      if (!source || !projectRoot || !cacheKey) {
        setThumbnailUrl("");
        return;
      }
      const cached = memoryCache.get(cacheKey) ?? "";
      const loaded =
        cached ||
        (await loadThumbnailUrl({
          cacheKey,
          projectRoot,
          sourcePaths: thumbnailCandidatePaths(entity, source),
          transform: (sourceUrl) => cropImageToSquare(sourceUrl, THUMBNAIL_SIDE)
        }));
      if (loaded) {
        memoryCache.set(cacheKey, loaded);
      }
      if (!cancelled) {
        setThumbnailUrl(loaded);
      }
    };

    void load().catch(() => {
      if (!cancelled) {
        setThumbnailUrl("");
      }
    });
    return () => {
      cancelled = true;
    };
  }, [cacheKey, canShowThumbnail, draftPreview, entity, loadEligible, projectRoot, source]);

  if (!canShowThumbnail) {
    return <span ref={thumbnailRef} aria-hidden="true" className="module-entity-thumb empty" />;
  }

  return (
    <span ref={thumbnailRef} aria-hidden="true" className={thumbnailUrl ? "module-entity-thumb" : "module-entity-thumb placeholder"}>
      {thumbnailUrl ? <img alt="" draggable={false} src={thumbnailUrl} /> : null}
    </span>
  );
}

function thumbnailCandidatePaths(entity: ModuleEntity, source: ModuleSourceSlot): string[] {
  return [...new Set([defaultImageDraftPath(entity, source), source.path, source.relative_path].filter(Boolean))];
}

async function cropImageToSquare(sourceUrl: string, sideLength: number): Promise<string> {
  const image = await loadImage(sourceUrl);
  const naturalWidth = image.naturalWidth || image.width;
  const naturalHeight = image.naturalHeight || image.height;
  if (naturalWidth <= 0 || naturalHeight <= 0) {
    return "";
  }
  const canvas = document.createElement("canvas");
  canvas.width = sideLength;
  canvas.height = sideLength;
  const context = canvas.getContext("2d");
  if (!context) {
    return "";
  }
  const scale = sideLength / Math.min(naturalWidth, naturalHeight);
  const width = naturalWidth * scale;
  const height = naturalHeight * scale;
  context.drawImage(image, (sideLength - width) / 2, (sideLength - height) / 2, width, height);
  return canvas.toDataURL("image/png");
}

function loadImage(sourceUrl: string): Promise<HTMLImageElement> {
  return new Promise((resolve, reject) => {
    const image = new Image();
    image.onload = () => resolve(image);
    image.onerror = () => reject(new Error("Cannot load module instance thumbnail image."));
    image.decoding = "async";
    image.src = sourceUrl;
  });
}
