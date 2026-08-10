import { describe, expect, it } from "vitest";

import {
  getFrontendApiActionPanelState,
  getFrontendApiDefaultSectionAction,
  getFrontendApiSectionActions
} from "./frontendApi";

describe("frontend API action panel state", () => {
  it("bundles module create form defaults, option requests, execution requests, and run state", () => {
    const state = getFrontendApiActionPanelState({
      operationId: "module.create",
      values: {
        template_id: "event.basic",
        object_id: "my_event"
      }
    });

    expect(state.operation_id).toBe("module.create");
    expect(state.action.operation_id).toBe("module.create");
    expect(state.detail.operation.id).toBe("module.create");
    expect(state.fields.map((field) => field.name)).toEqual([
      "path",
      "template_id",
      "object_id",
      "source_root",
      "values",
      "write",
      "force"
    ]);
    expect(state.values_with_defaults).toMatchObject({
      path: ".",
      template_id: "event.basic",
      object_id: "my_event",
      write: false,
      force: false
    });

    const pathControl = state.controls.find((control) => control.name === "path");
    const templateControl = state.controls.find((control) => control.name === "template_id");
    expect(pathControl).toMatchObject({
      kind: "path",
      value: ".",
      defaulted: true,
      disabled: false
    });
    expect(templateControl).toMatchObject({
      kind: "combobox",
      value: "event.basic",
      defaulted: false,
      disabled: false
    });

    expect(state.option_requests.map((request) => [request.field_name, request.available, request.missing_requirements])).toEqual([
      ["template_id", true, []],
      ["source_root", true, []]
    ]);
    expect(state.option_requests[0]?.request).toMatchObject({
      url: "/frontend-api/options?operation_id=module.create&field_name=template_id",
      init: {
        method: "POST"
      }
    });
    expect(state.option_requests[0]?.request?.init.body).toBe(JSON.stringify(state.values_with_defaults));

    expect(state.normalize_request).toMatchObject({
      url: "/frontend-api/normalize?operation_id=module.create",
      init: {
        method: "POST"
      }
    });
    expect(state.rest_plan_request).toMatchObject({
      url: "/frontend-api/rest-request?operation_id=module.create",
      init: {
        method: "POST"
      }
    });
    expect(state.execution_request_key).toBe(
      JSON.stringify({
        operation_id: "module.create",
        values: state.values_with_defaults
      })
    );
    expect(JSON.parse(state.option_request_key)).toEqual([
      {
        field_name: "template_id",
        available: true,
        missing_requirements: [],
        url: "/frontend-api/options?operation_id=module.create&field_name=template_id",
        body: JSON.stringify(state.values_with_defaults)
      },
      {
        field_name: "source_root",
        available: true,
        missing_requirements: [],
        url: "/frontend-api/options?operation_id=module.create&field_name=source_root",
        body: JSON.stringify(state.values_with_defaults)
      }
    ]);

    expect(state.confirmation).toMatchObject({
      required: true,
      scope: "project-files",
      style: "write"
    });
    expect(state.confirmation_satisfied).toBe(false);
    expect(state.run_state).toMatchObject({
      disabled: true,
      status: "idle",
      confirmation_satisfied: false
    });
    expect(state.run_state.detail).toContain("Requires confirmation");
    expect(state.default_count).toBe(3);
  });

  it("enables run state after confirmation and ready rest plan", () => {
    const state = getFrontendApiActionPanelState({
      operationId: "module.create",
      values: {
        template_id: "event.basic",
        object_id: "my_event"
      },
      restPlanResult: {
        status: "ready",
        payload: {
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
          body: {},
          binding: {
            method: "POST",
            path: "/projects/scaffold",
            query: {}
          },
          normalized: {
            schema: "paradev.sdk.frontend-api.inputs.v1",
            operation_id: "module.create",
            values: {},
            project: {
              path: "."
            },
            parameters: {},
            selectors: {},
            projections: {}
          }
        }
      },
      confirmationStates: {
        "module.create": true
      }
    });

    expect(state.confirmation_satisfied).toBe(true);
    expect(state.run_state).toMatchObject({
      disabled: false,
      detail: "Not run",
      status: "idle",
      confirmation_satisfied: true
    });
  });

  it("requires confirmation before build start run state is enabled", () => {
    const values = {
      project_root: "/workspace/projects/PIHC3",
      mode: "full",
      profile: "hoi4",
      strict_metadata: true,
      parallelism: 4
    };
    const state = getFrontendApiActionPanelState({
      operationId: "build.start",
      values,
      restPlanResult: readyRestPlan("build.start", "POST", "/desktop/builds", {}, values, values)
    });

    expect(state.confirmation).toMatchObject({
      default_confirmed: false,
      required: true,
      scope: "project-files",
      style: "write",
      title: "Confirm Build Start"
    });
    expect(state.confirmation_satisfied).toBe(false);
    expect(state.run_state).toMatchObject({
      confirmation_satisfied: false,
      disabled: true,
      detail: "Requires confirmation: Confirm Build Start"
    });
  });

  it("enables build start run state after confirmation and ready rest plan", () => {
    const values = {
      project_root: "/workspace/projects/PIHC3",
      mode: "full",
      profile: "hoi4",
      strict_metadata: true,
      parallelism: 4
    };
    const state = getFrontendApiActionPanelState({
      operationId: "build.start",
      values,
      restPlanResult: readyRestPlan("build.start", "POST", "/desktop/builds", {}, values, values),
      confirmationStates: {
        "build.start": true
      }
    });

    expect(state.confirmation_satisfied).toBe(true);
    expect(state.run_state).toMatchObject({
      confirmation_satisfied: true,
      disabled: false,
      detail: "Not run"
    });
    expect(state.rest_plan_result?.payload?.path).toBe("/desktop/builds");
  });

  it("requires confirmation before build interrupt run state is enabled", () => {
    const values = { run_id: "build-1" };
    const state = getFrontendApiActionPanelState({
      operationId: "build.interrupt",
      values,
      restPlanResult: readyRestPlan("build.interrupt", "POST", "/desktop/builds/interrupt", {}, values, values)
    });

    expect(state.confirmation).toMatchObject({
      default_confirmed: false,
      required: true,
      scope: "project-files",
      style: "write",
      title: "Confirm Build Interrupt"
    });
    expect(state.confirmation_satisfied).toBe(false);
    expect(state.run_state).toMatchObject({
      confirmation_satisfied: false,
      disabled: true,
      detail: "Requires confirmation: Confirm Build Interrupt"
    });
  });

  it("enables build interrupt run state after confirmation and ready rest plan", () => {
    const values = { run_id: "build-1" };
    const state = getFrontendApiActionPanelState({
      operationId: "build.interrupt",
      values,
      restPlanResult: readyRestPlan("build.interrupt", "POST", "/desktop/builds/interrupt", {}, values, values),
      confirmationStates: {
        "build.interrupt": true
      }
    });

    expect(state.confirmation_satisfied).toBe(true);
    expect(state.run_state).toMatchObject({
      confirmation_satisfied: true,
      disabled: false,
      detail: "Not run"
    });
    expect(state.rest_plan_result?.payload?.path).toBe("/desktop/builds/interrupt");
  });

  it("keeps workspace section defaults tied to generated operation ids", () => {
    expect(getFrontendApiDefaultSectionAction("authoring")?.operation_id).toBe("module.authoring_plan");
    expect(getFrontendApiSectionActions("authoring").map((action) => action.operation_id)).toContain("module.create");
  });
});

function readyRestPlan(
  operationId: "build.interrupt" | "build.start" | "module.create",
  method: string,
  path: string,
  query: Record<string, unknown>,
  body: Record<string, unknown>,
  values: Record<string, unknown>
) {
  return {
    status: "ready" as const,
    payload: {
      schema: "paradev.sdk.frontend-api.rest-request.v1",
      operation_id: operationId,
      method,
      path,
      query,
      body,
      binding: {
        method,
        path,
        query: {}
      },
      normalized: {
        schema: "paradev.sdk.frontend-api.inputs.v1",
        operation_id: operationId,
        values,
        project: {},
        parameters: body,
        selectors: {},
        projections: {}
      }
    }
  };
}
