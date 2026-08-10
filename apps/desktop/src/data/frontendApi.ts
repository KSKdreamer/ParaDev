import {
  PARADEV_FRONTEND_API_CONTRACT,
  PARADEV_FRONTEND_API_GROUP_IDS,
  PARADEV_FRONTEND_API_MODE_VALUES,
  PARADEV_FRONTEND_API_OPERATION_IDS,
  PARADEV_FRONTEND_API_STATUS_VALUES,
  PARADEV_FRONTEND_API_WORKSPACE_SECTION_IDS
} from "../generated/frontendApi";
import type {
  ParaDevFrontendApiGroupId,
  ParaDevFrontendApiMode,
  ParaDevFrontendApiOperationId,
  ParaDevFrontendApiStatus,
  ParaDevFrontendApiWorkspaceSectionId
} from "../generated/frontendApi";

export type FrontendApiBinding = Readonly<Record<string, unknown>>;

export type FrontendApiRestBinding = FrontendApiBinding & {
  readonly method: string;
  readonly path: string;
  readonly query?: Readonly<Record<string, unknown>>;
};

export type FrontendApiBindings = {
  readonly sdk?: FrontendApiBinding;
  readonly cli?: FrontendApiBinding;
  readonly rest?: FrontendApiRestBinding;
  readonly mcp?: FrontendApiBinding;
  readonly lsp?: FrontendApiBinding;
  readonly [key: string]: FrontendApiBinding | undefined;
};

export type FrontendApiBindingSurface = "cli" | "lsp" | "mcp" | "rest" | "sdk";

export type FrontendApiBindingIndex = Readonly<
  Record<FrontendApiBindingSurface, Readonly<Record<string, readonly ParaDevFrontendApiOperationId[]>>>
>;

export type FrontendApiGroupIndex = Readonly<
  Record<ParaDevFrontendApiGroupId, readonly ParaDevFrontendApiOperationId[]>
>;

export type FrontendApiStatusIndex = Readonly<Record<ParaDevFrontendApiStatus, readonly ParaDevFrontendApiOperationId[]>>;

export type FrontendApiModeIndex = Readonly<Record<ParaDevFrontendApiMode, readonly ParaDevFrontendApiOperationId[]>>;

export type FrontendApiSurfaceIndex = Readonly<
  Record<FrontendApiBindingSurface | "unbound", readonly ParaDevFrontendApiOperationId[]>
>;

export type FrontendApiPayloadIndex = Readonly<Record<string, readonly ParaDevFrontendApiOperationId[]>>;

export type FrontendApiWorkspaceSectionIndex = Readonly<
  Record<ParaDevFrontendApiWorkspaceSectionId, readonly ParaDevFrontendApiOperationId[]>
>;

export type FrontendApiOptionSource = {
  readonly schema: string;
  readonly operation_id: ParaDevFrontendApiOperationId;
  readonly values_path: readonly string[];
  readonly value_field: string;
  readonly label_field?: string;
  readonly detail_fields?: readonly string[];
  readonly requires?: readonly string[];
  readonly forward?: readonly string[];
  readonly filters?: Readonly<Record<string, unknown>>;
  readonly [key: string]: unknown;
};

export type FrontendApiInput = {
  readonly name: string;
  readonly type: string;
  readonly required?: boolean;
  readonly default?: unknown;
  readonly choices?: readonly unknown[];
  readonly maps_to?: string;
  readonly minimum?: number;
  readonly nonblank?: boolean;
  readonly option_source?: FrontendApiOptionSource;
  readonly [key: string]: unknown;
};

export type FrontendApiFormControlKind = "checkbox" | "combobox" | "json" | "number" | "path" | "select" | "text";

export type FrontendApiFormControlOptionSource = "option-source" | "static";

export type FrontendApiFormControlOption = {
  readonly value: unknown;
  readonly value_token: string;
  readonly label: string;
  readonly source: FrontendApiFormControlOptionSource;
  readonly details?: Readonly<Record<string, unknown>>;
  readonly row?: Readonly<Record<string, unknown>>;
};

export type FrontendApiFormControl = {
  readonly name: string;
  readonly type: string;
  readonly kind: FrontendApiFormControlKind;
  readonly required: boolean;
  readonly value: unknown;
  readonly value_preview: string;
  readonly defaulted: boolean;
  readonly disabled: boolean;
  readonly disabled_reason?: string;
  readonly choices?: readonly unknown[];
  readonly maps_to?: string;
  readonly minimum?: number;
  readonly nonblank?: boolean;
  readonly option_source?: FrontendApiOptionSource;
  readonly option_status?: FrontendApiFormOptionResultStatus;
  readonly option_count?: number;
  readonly option_error?: string;
  readonly options: readonly FrontendApiFormControlOption[];
};

export type FrontendApiFormOptionRequest = {
  readonly field_name: string;
  readonly available: boolean;
  readonly missing_requirements: readonly string[];
  readonly option_source: FrontendApiOptionSource;
  readonly request?: FrontendApiJsonRequestInit;
};

export type FrontendApiOperation = {
  readonly id: ParaDevFrontendApiOperationId;
  readonly group: ParaDevFrontendApiGroupId;
  readonly status: ParaDevFrontendApiStatus;
  readonly summary: string;
  readonly mutates?: boolean;
  readonly sdk?: string;
  readonly cli?: string;
  readonly rest?: string;
  readonly mcp?: string;
  readonly lsp?: string;
  readonly payload?: string;
  readonly inputs?: readonly FrontendApiInput[];
  readonly bindings?: FrontendApiBindings;
  readonly [key: string]: unknown;
};

export type FrontendApiGroup = {
  readonly id: ParaDevFrontendApiGroupId;
  readonly title: string;
  readonly summary: string;
  readonly operation_count: number;
  readonly [key: string]: unknown;
};

export type FrontendApiGroupCount = {
  readonly operation_count: number;
  readonly read: number;
  readonly write: number;
  readonly implemented?: number;
  readonly planned?: number;
  readonly "frontend-local"?: number;
  readonly [key: string]: number | undefined;
};

export type FrontendApiSurfaceCount = Readonly<
  Record<FrontendApiBindingSurface | "operation_count" | "unbound", number>
>;

export type FrontendApiSummary = {
  readonly schema: string;
  readonly operation_count: number;
  readonly group_count: number;
  readonly workspace_section_count: number;
  readonly status_counts: Readonly<Record<string, number>>;
  readonly mode_counts: Readonly<Record<"read" | "write", number>>;
  readonly surface_counts: FrontendApiSurfaceCount;
  readonly group_counts: Readonly<Record<ParaDevFrontendApiGroupId, FrontendApiGroupCount>>;
  readonly group_surface_counts: Readonly<Record<ParaDevFrontendApiGroupId, FrontendApiSurfaceCount>>;
};

export type FrontendApiActionExecutionConfirmation = {
  readonly schema: string;
  readonly required: boolean;
  readonly scope: string;
  readonly style: string;
  readonly title: string;
  readonly summary: string;
  readonly confirm_fields: readonly string[];
  readonly default_confirmed: boolean;
  readonly [key: string]: unknown;
};

export type FrontendApiActionConfirmationStates = Partial<Record<ParaDevFrontendApiOperationId, boolean>>;

export type FrontendApiActionExecution = {
  readonly kind: string;
  readonly default_surface: string;
  readonly available_surfaces: readonly string[];
  readonly binding: FrontendApiBinding;
  readonly requires_values: boolean;
  readonly confirmation: FrontendApiActionExecutionConfirmation;
  readonly state_scope?: string;
  readonly normalizer_schema?: string;
  readonly rest_request_schema?: string;
  readonly [key: string]: unknown;
};

export type FrontendApiAction = {
  readonly schema: string;
  readonly operation_id: ParaDevFrontendApiOperationId;
  readonly title: string;
  readonly group: ParaDevFrontendApiGroupId;
  readonly status: ParaDevFrontendApiStatus;
  readonly read_only: boolean;
  readonly mutates: boolean;
  readonly form: boolean;
  readonly summary: string;
  readonly execution: FrontendApiActionExecution;
  readonly payload?: string;
  readonly form_schema?: string;
  readonly bindings?: FrontendApiBindings;
  readonly [key: string]: unknown;
};

export type FrontendApiForm = {
  readonly schema: string;
  readonly operation_id: ParaDevFrontendApiOperationId;
  readonly fields: readonly FrontendApiInput[];
  readonly required: readonly string[];
  readonly defaults: Readonly<Record<string, unknown>>;
  readonly aliases?: Readonly<Record<string, string>>;
  readonly json_schema?: Readonly<Record<string, unknown>>;
  readonly [key: string]: unknown;
};

export type FrontendApiActionDetail = {
  readonly schema: string;
  readonly operation: FrontendApiOperation;
  readonly action: FrontendApiAction;
  readonly sections: readonly ParaDevFrontendApiWorkspaceSectionId[];
  readonly form?: FrontendApiForm;
  readonly option_fields: readonly string[];
  readonly bindings?: FrontendApiBindings;
  readonly execution: FrontendApiActionExecution;
  readonly [key: string]: unknown;
};

export type FrontendApiOptionPayload = {
  readonly schema: string;
  readonly operation_id: ParaDevFrontendApiOperationId;
  readonly field_name: string;
  readonly available: boolean;
  readonly missing_requirements: readonly string[];
  readonly options: readonly Readonly<Record<string, unknown>>[];
  readonly count: number;
  readonly [key: string]: unknown;
};

export type FrontendApiNormalizedInputs = {
  readonly schema: string;
  readonly operation_id: ParaDevFrontendApiOperationId;
  readonly values: Readonly<Record<string, unknown>>;
  readonly project: Readonly<Record<string, unknown>>;
  readonly parameters: Readonly<Record<string, unknown>>;
  readonly selectors: Readonly<Record<string, unknown>>;
  readonly projections: Readonly<Record<string, unknown>>;
  readonly [key: string]: unknown;
};

export type FrontendApiRestRequestPlan = {
  readonly schema: string;
  readonly operation_id: ParaDevFrontendApiOperationId;
  readonly method: string;
  readonly path: string;
  readonly query: Readonly<Record<string, unknown>>;
  readonly body: Readonly<Record<string, unknown>>;
  readonly binding: FrontendApiRestBinding;
  readonly normalized: FrontendApiNormalizedInputs;
  readonly [key: string]: unknown;
};

export type FrontendApiSubmittedValues = Readonly<Record<string, unknown>>;

export type FrontendApiJsonRequestInit = {
  readonly url: string;
  readonly init: RequestInit;
};

export type FrontendApiFetch = typeof fetch;

export type FrontendApiMetaRequestResultStatus = "error" | "loading" | "ready";

export type FrontendApiNormalizeResult = {
  readonly status: FrontendApiMetaRequestResultStatus;
  readonly payload?: FrontendApiNormalizedInputs;
  readonly error?: string;
};

export type FrontendApiRestPlanResult = {
  readonly status: FrontendApiMetaRequestResultStatus;
  readonly payload?: FrontendApiRestRequestPlan;
  readonly error?: string;
};

export type FrontendApiRestExecutionResultStatus = "error" | "loading" | "ready";

export type FrontendApiRestExecutionResult = {
  readonly status: FrontendApiRestExecutionResultStatus;
  readonly request?: FrontendApiJsonRequestInit;
  readonly status_code?: number;
  readonly payload?: unknown;
  readonly error?: string;
};

export type FrontendApiActionRunState = {
  readonly disabled: boolean;
  readonly detail: string;
  readonly status: FrontendApiRestExecutionResultStatus | "idle";
  readonly confirmation_satisfied: boolean;
};

export type FrontendApiFormOptionResultStatus = "error" | "loading" | "ready" | "unavailable";

export type FrontendApiFormOptionResult = {
  readonly field_name: string;
  readonly status: FrontendApiFormOptionResultStatus;
  readonly missing_requirements: readonly string[];
  readonly payload?: FrontendApiOptionPayload;
  readonly error?: string;
};

export type FrontendApiFormOptionResults = Readonly<Record<string, FrontendApiFormOptionResult>>;

export type FrontendApiWorkspaceSection = {
  readonly id: ParaDevFrontendApiWorkspaceSectionId;
  readonly title: string;
  readonly summary: string;
  readonly operation_ids: readonly ParaDevFrontendApiOperationId[];
  readonly default_operation_id?: ParaDevFrontendApiOperationId;
  readonly actions: readonly FrontendApiAction[];
  readonly [key: string]: unknown;
};

export type FrontendApiActionPanelStateInput = {
  readonly operationId: ParaDevFrontendApiOperationId;
  readonly values?: FrontendApiSubmittedValues;
  readonly optionResults?: FrontendApiFormOptionResults;
  readonly normalizeResult?: FrontendApiNormalizeResult;
  readonly restPlanResult?: FrontendApiRestPlanResult;
  readonly restExecutionResult?: FrontendApiRestExecutionResult;
  readonly confirmationStates?: FrontendApiActionConfirmationStates;
};

export type FrontendApiActionPanelState = {
  readonly operation_id: ParaDevFrontendApiOperationId;
  readonly action: FrontendApiAction;
  readonly detail: FrontendApiActionDetail;
  readonly fields: readonly FrontendApiInput[];
  readonly values: FrontendApiSubmittedValues;
  readonly values_with_defaults: FrontendApiSubmittedValues;
  readonly option_results: FrontendApiFormOptionResults;
  readonly controls: readonly FrontendApiFormControl[];
  readonly option_requests: readonly FrontendApiFormOptionRequest[];
  readonly normalize_request: FrontendApiJsonRequestInit;
  readonly rest_plan_request: FrontendApiJsonRequestInit;
  readonly normalize_result?: FrontendApiNormalizeResult;
  readonly rest_plan_result?: FrontendApiRestPlanResult;
  readonly rest_execution_result?: FrontendApiRestExecutionResult;
  readonly confirmation: FrontendApiActionExecutionConfirmation;
  readonly confirmation_satisfied: boolean;
  readonly run_state: FrontendApiActionRunState;
  readonly option_request_key: string;
  readonly execution_request_key: string;
  readonly default_count: number;
};

export const frontendApiOperationIds = PARADEV_FRONTEND_API_OPERATION_IDS;
export const frontendApiGroupIds = PARADEV_FRONTEND_API_GROUP_IDS;
export const frontendApiStatusValues = PARADEV_FRONTEND_API_STATUS_VALUES;
export const frontendApiModeValues = PARADEV_FRONTEND_API_MODE_VALUES;
export const frontendApiWorkspaceSectionIds = PARADEV_FRONTEND_API_WORKSPACE_SECTION_IDS;

export const frontendApiSummary = PARADEV_FRONTEND_API_CONTRACT.summary as unknown as FrontendApiSummary;
export const frontendApiOperations = PARADEV_FRONTEND_API_CONTRACT.operations as unknown as readonly FrontendApiOperation[];
export const frontendApiGroups = PARADEV_FRONTEND_API_CONTRACT.groups as unknown as readonly FrontendApiGroup[];
export const frontendApiWorkspaceSections = PARADEV_FRONTEND_API_CONTRACT.workspace.sections as unknown as readonly FrontendApiWorkspaceSection[];
export const frontendApiBindingIndex = PARADEV_FRONTEND_API_CONTRACT.index.binding as unknown as FrontendApiBindingIndex;
export const frontendApiGroupIndex = PARADEV_FRONTEND_API_CONTRACT.index.group as unknown as FrontendApiGroupIndex;
export const frontendApiStatusIndex = PARADEV_FRONTEND_API_CONTRACT.index.status as unknown as FrontendApiStatusIndex;
export const frontendApiModeIndex = PARADEV_FRONTEND_API_CONTRACT.index.mode as unknown as FrontendApiModeIndex;
export const frontendApiSurfaceIndex = PARADEV_FRONTEND_API_CONTRACT.index.surface as unknown as FrontendApiSurfaceIndex;
export const frontendApiPayloadIndex = PARADEV_FRONTEND_API_CONTRACT.index.payload as unknown as FrontendApiPayloadIndex;
export const frontendApiWorkspaceSectionIndex = PARADEV_FRONTEND_API_CONTRACT.index.workspace_section as unknown as FrontendApiWorkspaceSectionIndex;
export const frontendApiWorkspaceActions = frontendApiWorkspaceSections.flatMap((section) => section.actions);
export const frontendApiRestOperations = frontendApiOperations.filter((operation) => Boolean(operation.bindings?.rest));
export const frontendApiInputOperations = frontendApiOperations.filter((operation) => Boolean(operation.inputs?.length));
export const frontendApiEndpointPaths = {
  discovery: "/frontend-api",
  workspace: "/frontend-api/workspace",
  action: "/frontend-api/action",
  options: "/frontend-api/options",
  normalize: "/frontend-api/normalize",
  restRequest: "/frontend-api/rest-request",
  binding: "/frontend-api/binding"
} as const;
const frontendApiEndpointBaseUrl = import.meta.env.VITE_PARADEV_FRONTEND_API_BASE_URL ?? "";

const operationsById = new Map<ParaDevFrontendApiOperationId, FrontendApiOperation>(
  frontendApiOperations.map((operation) => [operation.id, operation])
);

const actionsByOperationId = new Map<ParaDevFrontendApiOperationId, FrontendApiAction>();
frontendApiWorkspaceActions.forEach((action) => {
  if (!actionsByOperationId.has(action.operation_id)) {
    actionsByOperationId.set(action.operation_id, action);
  }
});

function formatFrontendApiRestIndexValue(value: unknown): string {
  if (typeof value === "boolean") {
    return value ? "true" : "false";
  }
  if (typeof value === "number" || typeof value === "string") {
    return String(value);
  }
  return JSON.stringify(value);
}

export function buildFrontendApiRestIndexKey(
  method: string,
  path: string,
  query: Readonly<Record<string, unknown>> = {}
): string {
  const entries = Object.entries(query)
    .filter(([, value]) => value !== undefined && value !== null)
    .sort(([left], [right]) => left.localeCompare(right));
  if (!entries.length) {
    return `${method} ${path}`;
  }
  const queryString = entries.map(([key, value]) => `${key}=${formatFrontendApiRestIndexValue(value)}`).join("&");
  return `${method} ${path}?${queryString}`;
}

export function getFrontendApiBindingOperationIds(
  surface: FrontendApiBindingSurface,
  key: string
): readonly ParaDevFrontendApiOperationId[] {
  return frontendApiBindingIndex[surface]?.[key] ?? [];
}

export function getFrontendApiGroupOperationIds(
  groupId: ParaDevFrontendApiGroupId
): readonly ParaDevFrontendApiOperationId[] {
  return frontendApiGroupIndex[groupId] ?? [];
}

export function getFrontendApiStatusOperationIds(
  status: ParaDevFrontendApiStatus
): readonly ParaDevFrontendApiOperationId[] {
  return frontendApiStatusIndex[status] ?? [];
}

export function getFrontendApiModeOperationIds(
  mode: ParaDevFrontendApiMode
): readonly ParaDevFrontendApiOperationId[] {
  return frontendApiModeIndex[mode] ?? [];
}

export function getFrontendApiSurfaceOperationIds(
  surface: FrontendApiBindingSurface | "unbound"
): readonly ParaDevFrontendApiOperationId[] {
  return frontendApiSurfaceIndex[surface] ?? [];
}

export function getFrontendApiPayloadOperationIds(
  payload: string
): readonly ParaDevFrontendApiOperationId[] {
  return frontendApiPayloadIndex[payload] ?? [];
}

export function getFrontendApiWorkspaceSectionOperationIds(
  sectionId: ParaDevFrontendApiWorkspaceSectionId
): readonly ParaDevFrontendApiOperationId[] {
  return frontendApiWorkspaceSectionIndex[sectionId] ?? [];
}

export function getFrontendApiRestOperationIds(
  method: string,
  path: string,
  query: Readonly<Record<string, unknown>> = {}
): readonly ParaDevFrontendApiOperationId[] {
  return getFrontendApiBindingOperationIds("rest", buildFrontendApiRestIndexKey(method, path, query));
}

function buildFrontendApiUrl(path: string, query: Readonly<Record<string, string>> = {}): string {
  const parameters = new URLSearchParams(query);
  if (frontendApiEndpointBaseUrl) {
    const url = new URL(path, frontendApiEndpointBaseUrl);
    url.search = parameters.toString();
    return url.toString();
  }
  const suffix = parameters.toString();
  return suffix ? `${path}?${suffix}` : path;
}

export function getFrontendApiOperation(operationId: ParaDevFrontendApiOperationId): FrontendApiOperation {
  const operation = operationsById.get(operationId);
  if (!operation) {
    throw new Error(`Unknown ParaDev frontend operation: ${operationId}`);
  }
  return operation;
}

export function getFrontendApiBindings(operationId: ParaDevFrontendApiOperationId): FrontendApiBindings {
  return getFrontendApiOperation(operationId).bindings ?? {};
}

export function getFrontendApiRestBinding(operationId: ParaDevFrontendApiOperationId): FrontendApiRestBinding {
  const binding = getFrontendApiBindings(operationId).rest;
  if (!binding) {
    throw new Error(`ParaDev frontend operation does not expose a REST binding: ${operationId}`);
  }
  return binding;
}

export function buildFrontendApiDiscoveryUrl(query: {
  readonly operationId?: ParaDevFrontendApiOperationId;
  readonly groupId?: ParaDevFrontendApiGroupId;
  readonly form?: boolean;
} = {}): string {
  const parameters: Record<string, string> = {};
  if (query.operationId) {
    parameters.operation_id = query.operationId;
  }
  if (query.groupId) {
    parameters.group_id = query.groupId;
  }
  if (query.form !== undefined) {
    parameters.form = String(query.form);
  }
  return buildFrontendApiUrl(frontendApiEndpointPaths.discovery, parameters);
}

export function buildFrontendApiActionUrl(operationId: ParaDevFrontendApiOperationId): string {
  return buildFrontendApiUrl(frontendApiEndpointPaths.action, { operation_id: operationId });
}

export function buildFrontendApiOptionsUrl(operationId: ParaDevFrontendApiOperationId, fieldName: string): string {
  return buildFrontendApiUrl(frontendApiEndpointPaths.options, { operation_id: operationId, field_name: fieldName });
}

export function buildFrontendApiNormalizeUrl(operationId: ParaDevFrontendApiOperationId): string {
  return buildFrontendApiUrl(frontendApiEndpointPaths.normalize, { operation_id: operationId });
}

export function buildFrontendApiRestRequestUrl(operationId: ParaDevFrontendApiOperationId): string {
  return buildFrontendApiUrl(frontendApiEndpointPaths.restRequest, { operation_id: operationId });
}

export function buildFrontendApiBindingLookupUrl(surface: FrontendApiBindingSurface, key: string): string {
  return buildFrontendApiUrl(frontendApiEndpointPaths.binding, { binding_surface: surface, binding_key: key });
}

export function buildFrontendApiJsonRequestInit(url: string, values: FrontendApiSubmittedValues = {}): FrontendApiJsonRequestInit {
  return {
    url,
    init: {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(values)
    }
  };
}

export function buildFrontendApiOptionsRequest(
  operationId: ParaDevFrontendApiOperationId,
  fieldName: string,
  values: FrontendApiSubmittedValues = {}
): FrontendApiJsonRequestInit {
  return buildFrontendApiJsonRequestInit(buildFrontendApiOptionsUrl(operationId, fieldName), values);
}

export function buildFrontendApiNormalizeRequest(
  operationId: ParaDevFrontendApiOperationId,
  values: FrontendApiSubmittedValues = {}
): FrontendApiJsonRequestInit {
  return buildFrontendApiJsonRequestInit(buildFrontendApiNormalizeUrl(operationId), values);
}

export function buildFrontendApiRestPlanRequest(
  operationId: ParaDevFrontendApiOperationId,
  values: FrontendApiSubmittedValues = {}
): FrontendApiJsonRequestInit {
  return buildFrontendApiJsonRequestInit(buildFrontendApiRestRequestUrl(operationId), values);
}

function formatFrontendApiQueryValue(value: unknown): string {
  if (typeof value === "string") {
    return value;
  }
  if (typeof value === "boolean") {
    return value ? "true" : "false";
  }
  if (typeof value === "number") {
    return String(value);
  }
  return JSON.stringify(value);
}

export function buildFrontendApiRestExecutionRequest(plan: FrontendApiRestRequestPlan): FrontendApiJsonRequestInit {
  const query = Object.fromEntries(
    Object.entries(plan.query)
      .filter(([, value]) => value !== undefined && value !== null)
      .map(([key, value]) => [key, formatFrontendApiQueryValue(value)])
  );
  const hasBody = Object.keys(plan.body).length > 0;
  return {
    url: buildFrontendApiUrl(plan.path, query),
    init: {
      method: plan.method,
      ...(hasBody
        ? {
            headers: {
              "Content-Type": "application/json"
            },
            body: JSON.stringify(plan.body)
          }
        : {})
    }
  };
}

export function isFrontendApiActionConfirmationSatisfied(
  operationId: ParaDevFrontendApiOperationId,
  confirmation: FrontendApiActionExecutionConfirmation,
  confirmationStates: FrontendApiActionConfirmationStates = {}
): boolean {
  return confirmation.required !== true || confirmationStates[operationId] === true;
}

export function getFrontendApiActionRunState(
  operationId: ParaDevFrontendApiOperationId,
  confirmation: FrontendApiActionExecutionConfirmation,
  restPlanResult?: FrontendApiRestPlanResult,
  restExecutionResult?: FrontendApiRestExecutionResult,
  confirmationStates: FrontendApiActionConfirmationStates = {}
): FrontendApiActionRunState {
  const confirmationSatisfied = isFrontendApiActionConfirmationSatisfied(operationId, confirmation, confirmationStates);
  const status = restExecutionResult?.status ?? "idle";
  if (!confirmationSatisfied) {
    return {
      disabled: true,
      detail: `Requires confirmation: ${confirmation.title}`,
      status,
      confirmation_satisfied: confirmationSatisfied
    };
  }
  if (restExecutionResult?.status === "loading") {
    return {
      disabled: true,
      detail: restExecutionResult.request?.url ?? "Running",
      status,
      confirmation_satisfied: confirmationSatisfied
    };
  }
  if (!restPlanResult?.payload) {
    return {
      disabled: true,
      detail: restPlanResult?.error ?? "REST plan not ready",
      status,
      confirmation_satisfied: confirmationSatisfied
    };
  }
  return {
    disabled: false,
    detail:
      restExecutionResult?.error ??
      (restExecutionResult?.payload
        ? JSON.stringify(restExecutionResult.payload)
        : restExecutionResult?.request?.url ?? "Not run"),
    status,
    confirmation_satisfied: confirmationSatisfied
  };
}

export function getFrontendApiInputs(operationId: ParaDevFrontendApiOperationId): readonly FrontendApiInput[] {
  return getFrontendApiOperation(operationId).inputs ?? [];
}

export function getFrontendApiRequiredInputNames(operationId: ParaDevFrontendApiOperationId): readonly string[] {
  return getFrontendApiInputs(operationId)
    .filter((input) => input.required === true)
    .map((input) => input.name);
}

export function getFrontendApiDefaultValues(operationId: ParaDevFrontendApiOperationId): Readonly<Record<string, unknown>> {
  return Object.fromEntries(
    getFrontendApiInputs(operationId)
      .filter((input) => Object.prototype.hasOwnProperty.call(input, "default"))
      .map((input) => [input.name, input.default])
  );
}

export function getFrontendApiOptionSourceInputs(operationId: ParaDevFrontendApiOperationId): readonly FrontendApiInput[] {
  return getFrontendApiInputs(operationId).filter((input) => Boolean(input.option_source));
}

export function getFrontendApiFormValuesWithDefaults(
  operationId: ParaDevFrontendApiOperationId,
  values: FrontendApiSubmittedValues = {}
): FrontendApiSubmittedValues {
  return {
    ...getFrontendApiDefaultValues(operationId),
    ...values
  };
}

export function getFrontendApiFormControlKind(input: FrontendApiInput): FrontendApiFormControlKind {
  if (input.choices?.length) {
    return "select";
  }
  if (input.option_source) {
    return "combobox";
  }
  if (input.type === "boolean") {
    return "checkbox";
  }
  if (input.type === "object" || input.type === "array") {
    return "json";
  }
  if (input.type === "integer" || input.type === "number") {
    return "number";
  }
  if (input.type === "path") {
    return "path";
  }
  return "text";
}

function hasFrontendApiControlValue(value: unknown): boolean {
  return value !== undefined && value !== null && value !== "";
}

function formatFrontendApiControlValue(value: unknown): string {
  if (value === undefined || value === null || value === "") {
    return "";
  }
  if (typeof value === "string") {
    return value;
  }
  if (typeof value === "boolean") {
    return value ? "true" : "false";
  }
  if (typeof value === "number") {
    return String(value);
  }
  return JSON.stringify(value);
}

function getFrontendApiControlOptionToken(index: number, value: unknown): string {
  return `${index}:${formatFrontendApiControlValue(value)}`;
}

function isFrontendApiRecord(value: unknown): value is Readonly<Record<string, unknown>> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function getFrontendApiStaticControlOptions(choices: readonly unknown[] = []): readonly FrontendApiFormControlOption[] {
  return choices.map((choice, index) => {
    const label = formatFrontendApiControlValue(choice);
    return {
      value: choice,
      value_token: getFrontendApiControlOptionToken(index, choice),
      label: label || "(empty)",
      source: "static"
    };
  });
}

function getFrontendApiOptionPayloadControlOptions(payload: FrontendApiOptionPayload): readonly FrontendApiFormControlOption[] {
  return payload.options.map((option, index) => {
    const value = Object.prototype.hasOwnProperty.call(option, "value") ? option.value : option.label;
    const label = typeof option.label === "string" && option.label ? option.label : formatFrontendApiControlValue(value);
    return {
      value,
      value_token: getFrontendApiControlOptionToken(index, value),
      label: label || "(empty)",
      source: "option-source",
      details: isFrontendApiRecord(option.details) ? option.details : undefined,
      row: isFrontendApiRecord(option.row) ? option.row : undefined
    };
  });
}

function isFrontendApiBridgeRequestAvailable(request: FrontendApiJsonRequestInit): boolean {
  return !import.meta.env.DEV || Boolean(frontendApiEndpointBaseUrl) || !request.url.startsWith("/");
}

function isFrontendApiMetaEndpointAvailable(request: FrontendApiJsonRequestInit): boolean {
  return isFrontendApiBridgeRequestAvailable(request);
}

function getFrontendApiBridgeUnavailableError(): string {
  return "Frontend API bridge unavailable; set VITE_PARADEV_FRONTEND_API_BASE_URL or run the desktop REST bridge.";
}

export function getFrontendApiFormControls(
  operationId: ParaDevFrontendApiOperationId,
  values: FrontendApiSubmittedValues = {},
  optionResults: FrontendApiFormOptionResults = {}
): readonly FrontendApiFormControl[] {
  const defaults = getFrontendApiDefaultValues(operationId);
  const valuesWithDefaults = getFrontendApiFormValuesWithDefaults(operationId, values);
  return getFrontendApiInputs(operationId).map((input) => {
    const hasSubmittedValue = Object.prototype.hasOwnProperty.call(values, input.name);
    const value = hasSubmittedValue ? values[input.name] : valuesWithDefaults[input.name];
    const missingRequirements = (input.option_source?.requires ?? []).filter((requirement) => !hasFrontendApiControlValue(valuesWithDefaults[requirement]));
    const optionResult = optionResults[input.name];
    return {
      name: input.name,
      type: input.type,
      kind: getFrontendApiFormControlKind(input),
      required: input.required === true,
      value,
      value_preview: formatFrontendApiControlValue(value),
      defaulted: !hasSubmittedValue && Object.prototype.hasOwnProperty.call(defaults, input.name),
      disabled: missingRequirements.length > 0,
      disabled_reason: missingRequirements.length ? `Requires ${missingRequirements.join(", ")}` : undefined,
      choices: input.choices,
      maps_to: input.maps_to,
      minimum: input.minimum,
      ...(input.nonblank === true ? { nonblank: true } : {}),
      option_source: input.option_source,
      option_status: optionResult?.status,
      option_count: optionResult?.payload?.count,
      option_error: optionResult?.error,
      options: optionResult?.payload ? getFrontendApiOptionPayloadControlOptions(optionResult.payload) : getFrontendApiStaticControlOptions(input.choices)
    };
  });
}

export function getFrontendApiFormOptionRequests(
  operationId: ParaDevFrontendApiOperationId,
  values: FrontendApiSubmittedValues = {}
): readonly FrontendApiFormOptionRequest[] {
  const valuesWithDefaults = getFrontendApiFormValuesWithDefaults(operationId, values);
  return getFrontendApiOptionSourceInputs(operationId).map((input) => {
    const optionSource = input.option_source;
    if (!optionSource) {
      throw new Error(`ParaDev frontend input does not expose an option source: ${operationId}.${input.name}`);
    }
    const missingRequirements = (optionSource.requires ?? []).filter((requirement) => !hasFrontendApiControlValue(valuesWithDefaults[requirement]));
    return {
      field_name: input.name,
      available: missingRequirements.length === 0,
      missing_requirements: missingRequirements,
      option_source: optionSource,
      request: missingRequirements.length === 0 ? buildFrontendApiOptionsRequest(operationId, input.name, valuesWithDefaults) : undefined
    };
  });
}

export function getFrontendApiActionPanelState({
  operationId,
  values = {},
  optionResults = {},
  normalizeResult,
  restPlanResult,
  restExecutionResult,
  confirmationStates = {}
}: FrontendApiActionPanelStateInput): FrontendApiActionPanelState {
  const detail = getFrontendApiActionDetail(operationId);
  const valuesWithDefaults = getFrontendApiFormValuesWithDefaults(operationId, values);
  const optionRequests = getFrontendApiFormOptionRequests(operationId, values);
  const confirmation = detail.execution.confirmation;
  const confirmationSatisfied = isFrontendApiActionConfirmationSatisfied(operationId, confirmation, confirmationStates);
  return {
    operation_id: operationId,
    action: detail.action,
    detail,
    fields: detail.form?.fields ?? [],
    values,
    values_with_defaults: valuesWithDefaults,
    option_results: optionResults,
    controls: getFrontendApiFormControls(operationId, values, optionResults),
    option_requests: optionRequests,
    normalize_request: buildFrontendApiNormalizeRequest(operationId, valuesWithDefaults),
    rest_plan_request: buildFrontendApiRestPlanRequest(operationId, valuesWithDefaults),
    normalize_result: normalizeResult,
    rest_plan_result: restPlanResult,
    rest_execution_result: restExecutionResult,
    confirmation,
    confirmation_satisfied: confirmationSatisfied,
    run_state: getFrontendApiActionRunState(operationId, confirmation, restPlanResult, restExecutionResult, confirmationStates),
    option_request_key: JSON.stringify(
      optionRequests.map((optionRequest) => ({
        field_name: optionRequest.field_name,
        available: optionRequest.available,
        missing_requirements: optionRequest.missing_requirements,
        url: optionRequest.request?.url,
        body: optionRequest.request?.init.body
      }))
    ),
    execution_request_key: JSON.stringify({
      operation_id: operationId,
      values: valuesWithDefaults
    }),
    default_count: Object.keys(detail.form?.defaults ?? {}).length
  };
}

export async function resolveFrontendApiFormOptionRequest(
  optionRequest: FrontendApiFormOptionRequest,
  fetcher: FrontendApiFetch = fetch
): Promise<FrontendApiFormOptionResult> {
  if (!optionRequest.available || !optionRequest.request) {
    return {
      field_name: optionRequest.field_name,
      status: "unavailable",
      missing_requirements: optionRequest.missing_requirements
    };
  }

  try {
    if (!isFrontendApiMetaEndpointAvailable(optionRequest.request)) {
      return {
        field_name: optionRequest.field_name,
        status: "error",
        missing_requirements: optionRequest.missing_requirements,
        error: getFrontendApiBridgeUnavailableError()
      };
    }
    const response = await fetcher(optionRequest.request.url, optionRequest.request.init);
    if (!response.ok) {
      return {
        field_name: optionRequest.field_name,
        status: "error",
        missing_requirements: optionRequest.missing_requirements,
        error: `${response.status} ${response.statusText}`.trim()
      };
    }
    const payload = (await response.json()) as FrontendApiOptionPayload;
    return {
      field_name: optionRequest.field_name,
      status: payload.available ? "ready" : "unavailable",
      missing_requirements: payload.missing_requirements,
      payload
    };
  } catch (error) {
    return {
      field_name: optionRequest.field_name,
      status: "error",
      missing_requirements: optionRequest.missing_requirements,
      error: error instanceof Error ? error.message : String(error)
    };
  }
}

export async function resolveFrontendApiNormalizeRequest(
  request: FrontendApiJsonRequestInit,
  fetcher: FrontendApiFetch = fetch
): Promise<FrontendApiNormalizeResult> {
  try {
    if (!isFrontendApiMetaEndpointAvailable(request)) {
      return {
        status: "error",
        error: getFrontendApiBridgeUnavailableError()
      };
    }
    const response = await fetcher(request.url, request.init);
    if (!response.ok) {
      return {
        status: "error",
        error: `${response.status} ${response.statusText}`.trim()
      };
    }
    const payload = (await response.json()) as FrontendApiNormalizedInputs;
    return {
      status: "ready",
      payload
    };
  } catch (error) {
    return {
      status: "error",
      error: error instanceof Error ? error.message : String(error)
    };
  }
}

export async function resolveFrontendApiRestPlanRequest(
  request: FrontendApiJsonRequestInit,
  fetcher: FrontendApiFetch = fetch
): Promise<FrontendApiRestPlanResult> {
  try {
    if (!isFrontendApiMetaEndpointAvailable(request)) {
      return {
        status: "error",
        error: getFrontendApiBridgeUnavailableError()
      };
    }
    const response = await fetcher(request.url, request.init);
    if (!response.ok) {
      return {
        status: "error",
        error: `${response.status} ${response.statusText}`.trim()
      };
    }
    const payload = (await response.json()) as FrontendApiRestRequestPlan;
    return {
      status: "ready",
      payload
    };
  } catch (error) {
    return {
      status: "error",
      error: error instanceof Error ? error.message : String(error)
    };
  }
}

export async function resolveFrontendApiRestExecutionRequest(
  request: FrontendApiJsonRequestInit,
  fetcher: FrontendApiFetch = fetch
): Promise<FrontendApiRestExecutionResult> {
  try {
    if (!isFrontendApiBridgeRequestAvailable(request)) {
      return {
        status: "error",
        request,
        error: getFrontendApiBridgeUnavailableError()
      };
    }
    const response = await fetcher(request.url, request.init);
    if (!response.ok) {
      return {
        status: "error",
        request,
        status_code: response.status,
        error: `${response.status} ${response.statusText}`.trim()
      };
    }
    const payload = await response.json();
    return {
      status: "ready",
      request,
      status_code: response.status,
      payload
    };
  } catch (error) {
    return {
      status: "error",
      request,
      error: error instanceof Error ? error.message : String(error)
    };
  }
}

export function getFrontendApiActionDetail(operationId: ParaDevFrontendApiOperationId): FrontendApiActionDetail {
  const operation = getFrontendApiOperation(operationId);
  const action = getFrontendApiAction(operationId);
  const fields = getFrontendApiInputs(operationId);
  const sections = frontendApiWorkspaceSections.filter((section) => section.operation_ids.includes(operationId)).map((section) => section.id);
  const form = fields.length
    ? {
        schema: "paradev.sdk.frontend-api.form.v1",
        operation_id: operationId,
        fields: getFrontendApiInputs(operationId),
        required: getFrontendApiRequiredInputNames(operationId),
        defaults: getFrontendApiDefaultValues(operationId)
      }
    : undefined;

  return {
    schema: "paradev.sdk.frontend-api.action-detail.v1",
    operation,
    action,
    sections,
    form,
    option_fields: getFrontendApiOptionSourceInputs(operationId).map((input) => input.name),
    bindings: operation.bindings,
    execution: action.execution
  };
}

export function getFrontendApiGroupOperations(groupId: ParaDevFrontendApiGroupId): readonly FrontendApiOperation[] {
  return getFrontendApiGroupOperationIds(groupId).map((operationId) => getFrontendApiOperation(operationId));
}

export function getFrontendApiSectionOperations(sectionId: ParaDevFrontendApiWorkspaceSectionId): readonly FrontendApiOperation[] {
  return getFrontendApiWorkspaceSectionOperationIds(sectionId).map((operationId) => getFrontendApiOperation(operationId));
}

export function getFrontendApiAction(operationId: ParaDevFrontendApiOperationId): FrontendApiAction {
  const action = actionsByOperationId.get(operationId);
  if (!action) {
    throw new Error(`Unknown ParaDev frontend workspace action: ${operationId}`);
  }
  return action;
}

export function getFrontendApiSectionActions(sectionId: ParaDevFrontendApiWorkspaceSectionId): readonly FrontendApiAction[] {
  const section = frontendApiWorkspaceSections.find((candidate) => candidate.id === sectionId);
  return section ? section.actions : [];
}

export function getFrontendApiDefaultSectionAction(sectionId: ParaDevFrontendApiWorkspaceSectionId): FrontendApiAction {
  const section = frontendApiWorkspaceSections.find((candidate) => candidate.id === sectionId);
  if (!section || !section.default_operation_id) {
    throw new Error(`Unknown ParaDev frontend workspace section: ${sectionId}`);
  }
  return getFrontendApiAction(section.default_operation_id);
}
