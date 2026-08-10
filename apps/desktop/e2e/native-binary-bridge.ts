type NativeBinaryBridgeOptions = {
  loadBytes: (sourcePath: string) => Promise<number[]>;
  onCacheWrite?: () => void;
  onRead?: (sourcePath: string) => void;
};

export function installNativeBinaryBridge(options: NativeBinaryBridgeOptions) {
  const cache = new Map<string, number[]>();
  const runtime = globalThis as typeof globalThis & {
    __PARADEV_RUNTIME_CONFIG__?: { nativeBridgeBaseUrl?: string };
  };
  const origin = globalThis.location?.origin ?? "http://paradev.test";
  const fallbackFetch = globalThis.fetch?.bind(globalThis);
  runtime.__PARADEV_RUNTIME_CONFIG__ = { nativeBridgeBaseUrl: origin };
  runtime.fetch = async (input: RequestInfo | URL, init?: RequestInit) => {
    const request = new Request(input, init);
    const url = new URL(request.url);
    if (url.origin === origin && url.pathname === "/desktop/sources/binary") {
      const body = (await request.json()) as { sourcePath?: string };
      const sourcePath = body.sourcePath ?? "";
      options.onRead?.(sourcePath);
      return jsonResponse(binaryPayload(sourcePath, await options.loadBytes(sourcePath)));
    }
    if (
      url.origin === origin &&
      url.pathname === "/desktop/thumbnail-cache" &&
      request.method === "GET"
    ) {
      const cacheKey = url.searchParams.get("cache_key") ?? "";
      return jsonResponse(
        cache.has(cacheKey)
          ? binaryPayload(cacheKey, cache.get(cacheKey) ?? [])
          : null
      );
    }
    if (
      url.origin === origin &&
      url.pathname === "/desktop/thumbnail-cache" &&
      request.method === "PUT"
    ) {
      const body = (await request.json()) as {
        bytes?: number[];
        cacheKey?: string;
      };
      const cacheKey = body.cacheKey ?? "";
      if (cacheKey && body.bytes) {
        cache.set(cacheKey, body.bytes);
      }
      options.onCacheWrite?.();
      return jsonResponse(binaryPayload(cacheKey, body.bytes ?? []));
    }
    if (fallbackFetch) {
      return await fallbackFetch(input, init);
    }
    throw new Error(`Unexpected native bridge request: ${request.method} ${url}`);
  };
}

function binaryPayload(path: string, bytes: number[]) {
  return {
    schema: "paradev.desktop.binary-source.v1",
    path,
    mimeType: "image/png",
    bytes
  };
}

function jsonResponse(value: unknown): Response {
  return Response.json(value, {
    headers: { "content-type": "application/json" },
    status: 200
  });
}
