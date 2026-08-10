import { describe, expect, it } from "vitest";

import {
  buildFrontendApiRestExecutionRequest,
  getFrontendApiActionPanelState,
  resolveFrontendApiFormOptionRequest,
  resolveFrontendApiNormalizeRequest,
  resolveFrontendApiRestExecutionRequest,
  resolveFrontendApiRestPlanRequest
} from "./frontendApi";
import type {
  FrontendApiFetch,
  FrontendApiJsonRequestInit,
  FrontendApiNormalizedInputs,
  FrontendApiRestRequestPlan
} from "./frontendApi";

function jsonResponse(payload: unknown, init: ResponseInit = {}): Response {
  return new Response(JSON.stringify(payload), {
    headers: {
      "Content-Type": "application/json"
    },
    status: 200,
    ...init
  });
}

function trackedJsonFetcher(payload: unknown, responseInit: ResponseInit = {}): {
  readonly calls: { readonly url: string; readonly init?: RequestInit }[];
  readonly fetcher: FrontendApiFetch;
} {
  const calls: { url: string; init?: RequestInit }[] = [];
  return {
    calls,
    fetcher: async (url, init) => {
      calls.push({ url: String(url), init });
      return jsonResponse(payload, responseInit);
    }
  };
}

function withBridgeUrl(request: FrontendApiJsonRequestInit, path: string): FrontendApiJsonRequestInit {
  return {
    url: `http://127.0.0.1:8787${path}`,
    init: request.init
  };
}

const normalizedModuleCreate: FrontendApiNormalizedInputs = {
  schema: "paradev.sdk.frontend-api.inputs.v1",
  operation_id: "module.create",
  values: {
    path: ".",
    template_id: "event.basic",
    object_id: "my_event",
    write: false,
    force: false
  },
  project: {
    path: "."
  },
  parameters: {
    template_id: "event.basic",
    object_id: "my_event",
    write: false,
    force: false
  },
  selectors: {},
  projections: {}
};

const restPlanModuleCreate: FrontendApiRestRequestPlan = {
  schema: "paradev.sdk.frontend-api.rest-request.v1",
  operation_id: "module.create",
  method: "POST",
  path: "/projects/scaffold",
  query: {
    path: ".",
    template_id: "event.basic",
    object_id: "my_event",
    write: false,
    force: false
  },
  body: {
    values: {
      difficulty: "normal"
    }
  },
  binding: {
    method: "POST",
    path: "/projects/scaffold",
    query: {}
  },
  normalized: normalizedModuleCreate
};

describe("frontend API resolver helpers", () => {
  it("resolves ready and unavailable option request states", async () => {
    const panel = getFrontendApiActionPanelState({
      operationId: "module.create",
      values: {
        template_id: "event.basic",
        object_id: "my_event"
      }
    });
    const templateRequest = panel.option_requests.find((request) => request.field_name === "template_id");
    if (!templateRequest?.request) {
      throw new Error("module.create.template_id should expose a ready option request");
    }

    const { calls, fetcher } = trackedJsonFetcher({
      schema: "paradev.sdk.frontend-api.options.v1",
      operation_id: "module.create",
      field_name: "template_id",
      available: true,
      missing_requirements: [],
      options: [
        {
          value: "event.basic",
          label: "Basic Event",
          details: {
            family: "event",
            source: "starter"
          }
        }
      ],
      count: 1
    });
    const result = await resolveFrontendApiFormOptionRequest(
      {
        ...templateRequest,
        request: withBridgeUrl(templateRequest.request, "/frontend-api/options?operation_id=module.create&field_name=template_id")
      },
      fetcher
    );

    expect(calls).toHaveLength(1);
    expect(calls[0]).toMatchObject({
      url: "http://127.0.0.1:8787/frontend-api/options?operation_id=module.create&field_name=template_id"
    });
    expect(result).toMatchObject({
      field_name: "template_id",
      status: "ready",
      missing_requirements: [],
      payload: {
        count: 1
      }
    });

    const unavailable = await resolveFrontendApiFormOptionRequest(
      {
        ...templateRequest,
        available: false,
        missing_requirements: ["path"],
        request: undefined
      },
      fetcher
    );
    expect(unavailable).toEqual({
      field_name: "template_id",
      status: "unavailable",
      missing_requirements: ["path"]
    });
    expect(calls).toHaveLength(1);
  });

  it("resolves normalize and REST-plan meta request results", async () => {
    const panel = getFrontendApiActionPanelState({
      operationId: "module.create",
      values: {
        template_id: "event.basic",
        object_id: "my_event"
      }
    });
    const normalizeFetcher = trackedJsonFetcher(normalizedModuleCreate);
    const normalizeResult = await resolveFrontendApiNormalizeRequest(
      withBridgeUrl(panel.normalize_request, "/frontend-api/normalize?operation_id=module.create"),
      normalizeFetcher.fetcher
    );

    expect(normalizeFetcher.calls).toHaveLength(1);
    expect(normalizeResult).toEqual({
      status: "ready",
      payload: normalizedModuleCreate
    });

    const restPlanFetcher = trackedJsonFetcher(restPlanModuleCreate);
    const restPlanResult = await resolveFrontendApiRestPlanRequest(
      withBridgeUrl(panel.rest_plan_request, "/frontend-api/rest-request?operation_id=module.create"),
      restPlanFetcher.fetcher
    );

    expect(restPlanFetcher.calls).toHaveLength(1);
    expect(restPlanResult).toEqual({
      status: "ready",
      payload: restPlanModuleCreate
    });

    const errorFetcher = trackedJsonFetcher(
      {
        error: "bad input"
      },
      {
        status: 422,
        statusText: "Unprocessable Content"
      }
    );
    await expect(
      resolveFrontendApiRestPlanRequest(
        withBridgeUrl(panel.rest_plan_request, "/frontend-api/rest-request?operation_id=module.create"),
        errorFetcher.fetcher
      )
    ).resolves.toEqual({
      status: "error",
      error: "422 Unprocessable Content"
    });
  });

  it("builds and resolves planned REST execution requests", async () => {
    const request = buildFrontendApiRestExecutionRequest(restPlanModuleCreate);
    expect(request).toMatchObject({
      url: "/projects/scaffold?path=.&template_id=event.basic&object_id=my_event&write=false&force=false",
      init: {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify(restPlanModuleCreate.body)
      }
    });

    const executionRequest = withBridgeUrl(request, request.url);
    const fetcher = trackedJsonFetcher(
      {
        schema: "paradev.sdk.module_scaffold.v1",
        write: false,
        module_id: "my_event"
      },
      {
        status: 202,
        statusText: "Accepted"
      }
    );
    await expect(resolveFrontendApiRestExecutionRequest(executionRequest, fetcher.fetcher)).resolves.toEqual({
      status: "ready",
      request: executionRequest,
      status_code: 202,
      payload: {
        schema: "paradev.sdk.module_scaffold.v1",
        write: false,
        module_id: "my_event"
      }
    });
    expect(fetcher.calls).toHaveLength(1);

    const errorFetcher = trackedJsonFetcher(
      {
        error: "server error"
      },
      {
        status: 500,
        statusText: "Server Error"
      }
    );
    await expect(resolveFrontendApiRestExecutionRequest(executionRequest, errorFetcher.fetcher)).resolves.toEqual({
      status: "error",
      request: executionRequest,
      status_code: 500,
      error: "500 Server Error"
    });
  });
});
