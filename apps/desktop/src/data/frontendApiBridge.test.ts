import { describe, expect, it } from "vitest";

import {
  getFrontendApiActionPanelState,
  resolveFrontendApiFormOptionRequest,
  resolveFrontendApiNormalizeRequest,
  resolveFrontendApiRestExecutionRequest,
  resolveFrontendApiRestPlanRequest
} from "./frontendApi";
import type { FrontendApiFetch, FrontendApiJsonRequestInit } from "./frontendApi";

function rejectingFetcher(): {
  readonly calls: string[];
  readonly fetcher: FrontendApiFetch;
} {
  const calls: string[] = [];
  return {
    calls,
    fetcher: async (url) => {
      calls.push(String(url));
      throw new Error("fetch should not run without a configured bridge");
    }
  };
}

function expectBridgeUnavailable(error: string | undefined): void {
  expect(error).toContain("Frontend API bridge unavailable");
  expect(error).toContain("VITE_PARADEV_FRONTEND_API_BASE_URL");
}

describe("frontend API bridge availability", () => {
  it("keeps relative option, normalize, and REST-plan meta requests offline-safe in dev", async () => {
    const panel = getFrontendApiActionPanelState({
      operationId: "module.create",
      values: {
        template_id: "event.basic",
        object_id: "my_event"
      }
    });
    const templateRequest = panel.option_requests.find((request) => request.field_name === "template_id");
    if (!templateRequest) {
      throw new Error("module.create.template_id should expose an option request");
    }

    const optionFetcher = rejectingFetcher();
    const optionResult = await resolveFrontendApiFormOptionRequest(templateRequest, optionFetcher.fetcher);
    expect(optionFetcher.calls).toEqual([]);
    expect(optionResult.status).toBe("error");
    expectBridgeUnavailable(optionResult.error);

    const normalizeFetcher = rejectingFetcher();
    const normalizeResult = await resolveFrontendApiNormalizeRequest(panel.normalize_request, normalizeFetcher.fetcher);
    expect(normalizeFetcher.calls).toEqual([]);
    expect(normalizeResult.status).toBe("error");
    expectBridgeUnavailable(normalizeResult.error);

    const restPlanFetcher = rejectingFetcher();
    const restPlanResult = await resolveFrontendApiRestPlanRequest(panel.rest_plan_request, restPlanFetcher.fetcher);
    expect(restPlanFetcher.calls).toEqual([]);
    expect(restPlanResult.status).toBe("error");
    expectBridgeUnavailable(restPlanResult.error);
  });

  it("keeps relative REST execution requests offline-safe in dev", async () => {
    const request: FrontendApiJsonRequestInit = {
      url: "/projects/scaffold?path=.",
      init: {
        method: "POST"
      }
    };
    const fetcher = rejectingFetcher();
    const result = await resolveFrontendApiRestExecutionRequest(request, fetcher.fetcher);

    expect(fetcher.calls).toEqual([]);
    expect(result.status).toBe("error");
    expect(result.request).toBe(request);
    expectBridgeUnavailable(result.error);
  });
});
