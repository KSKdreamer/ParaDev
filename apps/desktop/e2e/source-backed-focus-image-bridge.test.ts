import { describe, expect, it } from "vitest";
import { sourceBackedSmokeProjectRoot } from "../src/diagramEditor/fixtures/sourceBackedSmokeModel";
import { installSourceBackedFocusImageBridge } from "./source-backed-focus-image-bridge";

async function runFrontendOperation(operationId: string, values: Record<string, unknown>): Promise<unknown> {
  const origin = globalThis.location?.origin ?? "http://paradev.test";
  const planResponse = await fetch(`${origin}/frontend-api/rest-request?operation_id=${encodeURIComponent(operationId)}`, {
    body: JSON.stringify(values),
    headers: { "content-type": "application/json" },
    method: "POST"
  });
  const plan = (await planResponse.json()) as {
    body: Record<string, unknown>;
    method: string;
    path: string;
  };
  const response = await fetch(`${origin}${plan.path}`, {
    body: JSON.stringify(plan.body),
    headers: { "content-type": "application/json" },
    method: plan.method
  });
  return await response.json();
}

describe("source-backed focus smoke bridge", () => {
  it("serves PIHC3 focus source info text for diagram metadata drafts", async () => {
    installSourceBackedFocusImageBridge();

    const text = await runFrontendOperation("project.source_text", {
      path: sourceBackedSmokeProjectRoot,
      project_id: "PIHC3",
      source_path: `${sourceBackedSmokeProjectRoot}/src/modules/focus_tree/C01_MAIN/legacy/C01_COZY_GLOW_CORONATION/info.json`
    });

    expect(text).toContain('"parent": "FOCUS_C01_CANTERLOT_PACT"');
  });

  it("accepts diagram source edits as a smoke apply result", async () => {
    installSourceBackedFocusImageBridge();

    const payload = await runFrontendOperation("project.draft_apply", {
      path: sourceBackedSmokeProjectRoot,
      project_id: "PIHC3",
      source_edits: [
        {
          path: `${sourceBackedSmokeProjectRoot}/src/modules/focus_tree/C01_MAIN/legacy/C01_COZY_GLOW_CORONATION/info.json`,
          text: "{\n    \"tree\": \"C01_MAIN\"\n}\n"
        }
      ]
    });

    expect(payload).toMatchObject({
      schema: "paradev.rest.draft_apply.v1",
      project_id: "PIHC3",
      written: true,
      files: [
        {
          operation: "write_text",
          relative_path: "src/modules/focus_tree/C01_MAIN/legacy/C01_COZY_GLOW_CORONATION/info.json"
        }
      ]
    });
  });

  it("records the source info edit as the primary smoke apply edit", async () => {
    const originalDocument = (globalThis as typeof globalThis & { document?: Document }).document;
    const fakeDocument = { documentElement: { dataset: {} as Record<string, string> } };
    Object.defineProperty(globalThis, "document", {
      configurable: true,
      value: fakeDocument
    });
    try {
      installSourceBackedFocusImageBridge({
        lastApplyPath: "lastApplyPath",
        lastApplyText: "lastApplyText"
      });

      await runFrontendOperation("project.draft_apply", {
        path: sourceBackedSmokeProjectRoot,
        project_id: "PIHC3",
        source_edits: [
          {
            path: `${sourceBackedSmokeProjectRoot}/src/modules/focus_tree/C01_MAIN/meta.yaml`,
            text: "type: focus_tree\n"
          },
          {
            path: `${sourceBackedSmokeProjectRoot}/src/modules/focus_tree/C01_MAIN/legacy/C01_COZY_GLOW_CORONATION/info.json`,
            text: "{\n    \"relative_position_id\": \"FOCUS_C01_CANTERLOT_PACT\"\n}\n"
          }
        ]
      });

      expect(fakeDocument.documentElement.dataset.lastApplyPath).toBe(
        `${sourceBackedSmokeProjectRoot}/src/modules/focus_tree/C01_MAIN/legacy/C01_COZY_GLOW_CORONATION/info.json`
      );
      expect(fakeDocument.documentElement.dataset.lastApplyText).toContain('"relative_position_id": "FOCUS_C01_CANTERLOT_PACT"');
    } finally {
      if (originalDocument) {
        Object.defineProperty(globalThis, "document", {
          configurable: true,
          value: originalDocument
        });
      } else {
        Reflect.deleteProperty(globalThis, "document");
      }
    }
  });
});
