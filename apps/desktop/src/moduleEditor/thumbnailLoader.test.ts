import { describe, expect, it } from "vitest";
import { binarySourceDataUrl, dataUrlBytes, loadThumbnailUrl } from "./thumbnailLoader";
import type { BinarySourcePayload } from "../services/paradev";

function binaryPayload(path: string, mimeType: string, bytes: number[]): BinarySourcePayload {
  return {
    schema: "paradev.desktop.binary-source.v1",
    path,
    mimeType,
    bytes
  };
}

describe("thumbnail loader", () => {
  it("encodes and decodes binary source data URLs without browser globals", () => {
    const url = binarySourceDataUrl(binaryPayload("icon.png", "image/png", [112, 110, 103]));

    expect(url).toBe("data:image/png;base64,cG5n");
    expect(dataUrlBytes(url)).toEqual([112, 110, 103]);
  });

  it("loads cached thumbnails before reading source image candidates", async () => {
    const sourceReads: string[] = [];
    const url = await loadThumbnailUrl(
      {
        cacheKey: "v1|diagram|TECH_ALPHA|icon.png",
        projectRoot: "/workspace/projects/PIHC3",
        sourcePaths: ["icon.png"]
      },
      {
        readBinarySource: async (_projectRoot, sourcePath) => {
          sourceReads.push(sourcePath);
          return binaryPayload(sourcePath, "image/png", [115, 114, 99]);
        },
        readThumbnailCache: async (_projectRoot, cacheKey) => binaryPayload(cacheKey, "image/png", [111, 107]),
        writeThumbnailCache: async (request) => binaryPayload(request.cacheKey, "image/png", request.bytes)
      }
    );

    expect(url).toBe("data:image/png;base64,b2s=");
    expect(sourceReads).toEqual([]);
  });

  it("tries source image candidates until one can be transformed and cached", async () => {
    const sourceReads: string[] = [];
    const cacheWrites: number[][] = [];
    const url = await loadThumbnailUrl(
      {
        cacheKey: "v1|diagram|TECH_ALPHA|icon.png",
        projectRoot: "/workspace/projects/PIHC3",
        sourcePaths: ["missing.png", "icon.png"],
        transform: async (sourceUrl) => {
          expect(sourceUrl).toBe("data:image/png;base64,cG5n");
          return "data:image/png;base64,dGh1bWI=";
        }
      },
      {
        readBinarySource: async (_projectRoot, sourcePath) => {
          sourceReads.push(sourcePath);
          if (sourcePath === "missing.png") {
            throw new Error("not found");
          }
          return binaryPayload(sourcePath, "image/png", [112, 110, 103]);
        },
        readThumbnailCache: async () => null,
        writeThumbnailCache: async (request) => {
          cacheWrites.push(request.bytes);
          return binaryPayload(request.cacheKey, "image/png", request.bytes);
        }
      }
    );

    expect(url).toBe("data:image/png;base64,dGh1bWI=");
    expect(sourceReads).toEqual(["missing.png", "icon.png"]);
    expect(cacheWrites).toEqual([[116, 104, 117, 109, 98]]);
  });

  it("keeps a transform-less non-PNG source visible without writing it to the PNG cache", async () => {
    let cacheWriteCount = 0;
    const url = await loadThumbnailUrl(
      {
        cacheKey: "v1|diagram|TECH_ALPHA|icon.jpg",
        projectRoot: "/workspace/projects/PIHC3",
        sourcePaths: ["icon.jpg"]
      },
      {
        readBinarySource: async (_projectRoot, sourcePath) => binaryPayload(sourcePath, "image/jpeg", [255, 216, 255]),
        readThumbnailCache: async () => null,
        writeThumbnailCache: async () => {
          cacheWriteCount += 1;
          throw new Error("non-PNG cache write must not run");
        }
      }
    );

    expect(url).toBe("data:image/jpeg;base64,/9j/");
    expect(cacheWriteCount).toBe(0);
  });

  it("does not reinterpret real thumbnail cache failures as misses", async () => {
    const sourceReads: string[] = [];

    await expect(
      loadThumbnailUrl(
        {
          cacheKey: "v1|diagram|TECH_ALPHA|icon.png",
          projectRoot: "/workspace/projects/PIHC3",
          sourcePaths: ["icon.png"]
        },
        {
          readBinarySource: async (_projectRoot, sourcePath) => {
            sourceReads.push(sourcePath);
            return binaryPayload(sourcePath, "image/png", [112, 110, 103]);
          },
          readThumbnailCache: async () => {
            throw new Error("corrupt thumbnail cache");
          },
          writeThumbnailCache: async (request) => binaryPayload(request.cacheKey, "image/png", request.bytes)
        }
      )
    ).rejects.toThrow("corrupt thumbnail cache");
    expect(sourceReads).toEqual([]);
  });
});
