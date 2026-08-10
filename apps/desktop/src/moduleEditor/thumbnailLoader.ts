import {
  readBinarySource as defaultReadBinarySource,
  readThumbnailCache as defaultReadThumbnailCache,
  writeThumbnailCache as defaultWriteThumbnailCache,
  type BinarySourcePayload,
  type ThumbnailCacheWriteRequest
} from "../services/paradev";

export type ThumbnailLoadOptions = {
  cacheKey: string;
  projectRoot: string;
  sourcePaths: string[];
  transform?: (sourceUrl: string) => Promise<string>;
};

export type ThumbnailLoadServices = {
  readBinarySource: (projectRoot: string, sourcePath: string) => Promise<BinarySourcePayload>;
  readThumbnailCache: (projectRoot: string, cacheKey: string) => Promise<BinarySourcePayload | null>;
  writeThumbnailCache: (request: ThumbnailCacheWriteRequest) => Promise<BinarySourcePayload>;
};

const BASE64_ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/";

const defaultServices: ThumbnailLoadServices = {
  readBinarySource: defaultReadBinarySource,
  readThumbnailCache: defaultReadThumbnailCache,
  writeThumbnailCache: defaultWriteThumbnailCache
};

export async function loadThumbnailUrl(options: ThumbnailLoadOptions, services: ThumbnailLoadServices = defaultServices): Promise<string> {
  const cacheKey = options.cacheKey.trim();
  const projectRoot = options.projectRoot.trim();
  if (!cacheKey || !projectRoot) {
    return "";
  }

  const cached = await readCachedThumbnail(projectRoot, cacheKey, services);
  if (cached) {
    return cached;
  }

  for (const sourcePath of uniqueSourcePaths(options.sourcePaths)) {
    try {
      const sourceUrl = binarySourceDataUrl(await services.readBinarySource(projectRoot, sourcePath));
      const thumbnailUrl = options.transform ? await options.transform(sourceUrl) : sourceUrl;
      if (!thumbnailUrl) {
        continue;
      }
      await writeCachedThumbnail(projectRoot, cacheKey, thumbnailUrl, services);
      return thumbnailUrl;
    } catch {
      // Try the next candidate. Some image formats are readable bytes but not browser-decodable.
    }
  }
  return "";
}

export function binarySourceDataUrl(payload: BinarySourcePayload): string {
  return `data:${payload.mimeType || "application/octet-stream"};base64,${bytesToBase64(payload.bytes)}`;
}

export function dataUrlBytes(value: string): number[] {
  const base64 = value.split(",", 2)[1]?.replace(/\s+/g, "") ?? "";
  if (!base64) {
    return [];
  }
  return base64ToBytes(base64);
}

async function readCachedThumbnail(projectRoot: string, cacheKey: string, services: ThumbnailLoadServices): Promise<string> {
  const payload = await services.readThumbnailCache(projectRoot, cacheKey);
  return payload ? binarySourceDataUrl(payload) : "";
}

async function writeCachedThumbnail(projectRoot: string, cacheKey: string, thumbnailUrl: string, services: ThumbnailLoadServices): Promise<void> {
  if (!/^data:image\/png(?:;[^,]*)?;base64,/i.test(thumbnailUrl)) {
    return;
  }
  try {
    const bytes = dataUrlBytes(thumbnailUrl);
    if (bytes.length > 0) {
      await services.writeThumbnailCache({ projectRoot, cacheKey, bytes });
    }
  } catch {
    // Cache failures should not block the visible thumbnail.
  }
}

function uniqueSourcePaths(paths: string[]): string[] {
  return [...new Set(paths.map((path) => path.trim()).filter(Boolean))];
}

function bytesToBase64(bytes: number[]): string {
  let encoded = "";
  for (let index = 0; index < bytes.length; index += 3) {
    const first = bytes[index] ?? 0;
    const second = bytes[index + 1] ?? 0;
    const third = bytes[index + 2] ?? 0;
    const triplet = (first << 16) | (second << 8) | third;
    encoded += BASE64_ALPHABET[(triplet >> 18) & 63];
    encoded += BASE64_ALPHABET[(triplet >> 12) & 63];
    encoded += index + 1 < bytes.length ? BASE64_ALPHABET[(triplet >> 6) & 63] : "=";
    encoded += index + 2 < bytes.length ? BASE64_ALPHABET[triplet & 63] : "=";
  }
  return encoded;
}

function base64ToBytes(value: string): number[] {
  const clean = value.replace(/=+$/, "");
  const bytes: number[] = [];
  let buffer = 0;
  let bits = 0;
  for (const char of clean) {
    const sextet = BASE64_ALPHABET.indexOf(char);
    if (sextet < 0) {
      continue;
    }
    buffer = (buffer << 6) | sextet;
    bits += 6;
    if (bits >= 8) {
      bits -= 8;
      bytes.push((buffer >> bits) & 255);
    }
  }
  return bytes;
}
