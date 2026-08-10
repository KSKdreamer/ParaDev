import {
  useCallback,
  useEffect,
  useMemo,
  useRef,
  useState,
  type Dispatch,
  type MutableRefObject,
  type SetStateAction
} from "react";
import { localizedParaDevServiceError } from "../desktopBridgeErrors";
import type { Translator } from "../i18n";
import {
  MODULE_CATALOG_PAGE_SIZE,
  loadingModuleCatalogFamilyState,
  moduleCatalogBrowser,
  moduleCatalogFamilyKey,
  moduleCatalogFamilyStateWithDiscoveredRow,
  moduleCatalogFamilyStateWithError,
  moduleCatalogFamilyStateWithHydratedRow,
  moduleCatalogFamilyStateWithPage,
  moduleCatalogModuleIdForEntity,
  moduleCatalogRowHasHydratedData,
  moduleCatalogRowMatchesEntity,
  moduleCatalogTargetIdForEntity,
  type ModuleCatalogFamilyState
} from "../moduleCatalog";
import { projectBrowserFamily } from "../projectModules";
import {
  hasDesktopBackend,
  loadProjectCatalogStatus,
  projectCatalogReadinessFromError,
  queryProjectCatalog,
  refreshProjectCatalog
} from "../services/paradev";
import type { CatalogMutationResult, ProjectBrowserPayload } from "../types";

export type UseModuleCatalogFamilyOptions = {
  browser: ProjectBrowserPayload | null;
  catalogMutationBypass?: "failed" | "unknown";
  externalSelectionEntityId: string;
  familyId: string;
  onExternalSelectionMissing: (entityId: string) => void;
  query: string;
  selectedId: string;
  surface: "diagram" | "module";
  t: Translator;
};

export type ModuleCatalogFamilyController = {
  bypassed: boolean;
  catalogMissing: boolean;
  catalogMutationDirty: boolean;
  catalogPreparing: boolean;
  effectiveBrowser: ProjectBrowserPayload | null;
  enabled: boolean;
  hasMore: boolean;
  hydratingEntityId: string;
  loadError: string;
  loadedCount: number | null;
  loading: boolean;
  loadMore: () => Promise<void>;
  prepareCatalog: () => Promise<void>;
  reconcileMutation: (mutation: CatalogMutationResult | null | undefined) => CatalogMutationReconcileResult;
  repairCatalog: () => Promise<boolean>;
  repairError: string;
  retry: () => void;
  totalCount: number | null;
};

type ModuleCatalogRecoveryState = {
  error: string;
  missing: boolean;
  preparing: boolean;
  requestKey: string;
  scopeKey: string;
};

type ModuleCatalogBypassStatus = "failed" | "not_configured" | "unknown";
type CatalogMutationReconcileResult = "applied" | "bypassed" | "latched";

/** Owns lazy Catalog paging and row hydration for one module-family editor. */
export function useModuleCatalogFamily({
  browser,
  catalogMutationBypass,
  externalSelectionEntityId,
  familyId,
  onExternalSelectionMissing,
  query,
  selectedId,
  surface,
  t
}: UseModuleCatalogFamilyOptions): ModuleCatalogFamilyController {
  const family = projectBrowserFamily(browser, familyId);
  const projectRoot = browser?.root.trim() ?? "";
  const catalogFamily = family?.family.trim() ?? "";
  const scopeKey = projectRoot && catalogFamily ? `${moduleCatalogFamilyKey(projectRoot, familyId)}::${catalogFamily}` : "";
  const available = surface === "module" && Boolean(scopeKey) && hasDesktopBackend();
  const [state, setState] = useState<ModuleCatalogFamilyState | null>(null);
  const [search, setSearch] = useState({ scopeKey: "", value: "" });
  const [reloadNonce, setReloadNonce] = useState(0);
  const [bypassByScope, setBypassByScope] = useState<Record<string, ModuleCatalogBypassStatus>>({});
  const bypassByScopeRef = useRef(bypassByScope);
  bypassByScopeRef.current = bypassByScope;
  const [hydratingEntityId, setHydratingEntityId] = useState("");
  const [hydrationErrors, setHydrationErrors] = useState<Record<string, string>>({});
  const [recovery, setRecovery] = useState<ModuleCatalogRecoveryState>({
    error: "",
    missing: false,
    preparing: false,
    requestKey: "",
    scopeKey: ""
  });
  const requestGeneration = useRef(0);
  const mounted = useRef(true);
  const pageRequestInFlight = useRef(false);
  const hydrationTargetsInFlight = useRef(new Map<string, symbol>());
  const lookupEntitiesInFlight = useRef(new Map<string, symbol>());
  const currentRequestKey = useRef("");
  const currentScopeKey = useRef(scopeKey);
  const currentSelectedId = useRef(selectedId);
  const translator = useRef(t);
  translator.current = t;
  currentSelectedId.current = selectedId;
  currentScopeKey.current = scopeKey;
  const activeBypassStatus =
    bypassByScope[scopeKey] ?? catalogMutationBypass;
  const enabled = available && !activeBypassStatus;
  const searchQuery = search.scopeKey === scopeKey ? search.value : "";
  const requestKey = enabled ? `${scopeKey}::search=${searchQuery}::reload=${reloadNonce}` : "";
  currentRequestKey.current = requestKey;
  const [stateRequestKey, setStateRequestKey] = useState("");
  const activeState =
    enabled &&
    stateRequestKey === requestKey &&
    state?.projectRoot === projectRoot &&
    state.family === catalogFamily
      ? state
      : null;
  const activeHydrationError = hydrationErrors[moduleCatalogHydrationErrorKey(requestKey, selectedId)] ?? "";
  const activeRecovery =
    recovery.scopeKey === scopeKey && (activeBypassStatus || recovery.requestKey === requestKey)
      ? recovery
      : null;
  const effectiveBrowser = useMemo(() => {
    if (!browser || activeBypassStatus || !activeState) {
      return browser;
    }
    if (activeState.rows.length === 0 && (activeState.loading || activeState.error)) {
      return browser;
    }
    return moduleCatalogBrowser(browser, familyId, activeState);
  }, [activeBypassStatus, activeState, browser, familyId]);

  useEffect(
    () => {
      mounted.current = true;
      return () => {
        mounted.current = false;
        requestGeneration.current += 1;
        pageRequestInFlight.current = false;
        hydrationTargetsInFlight.current.clear();
        lookupEntitiesInFlight.current.clear();
      };
    },
    []
  );

  useEffect(() => {
    if (!enabled) {
      return;
    }
    const normalizedQuery = query.trim();
    if (search.scopeKey === scopeKey && search.value === normalizedQuery) {
      return;
    }
    const timeout = globalThis.setTimeout(
      () => setSearch({ scopeKey, value: normalizedQuery }),
      search.scopeKey === scopeKey ? 180 : 0
    );
    return () => globalThis.clearTimeout(timeout);
  }, [enabled, query, scopeKey, search]);

  useEffect(() => {
    const generation = requestGeneration.current + 1;
    requestGeneration.current = generation;
    pageRequestInFlight.current = false;
    hydrationTargetsInFlight.current.clear();
    lookupEntitiesInFlight.current.clear();
    setHydratingEntityId("");
    setHydrationErrors({});
    setStateRequestKey(requestKey);

    if (!enabled) {
      setState(null);
      if (!available) {
        setRecovery({ error: "", missing: false, preparing: false, requestKey: "", scopeKey: "" });
      }
      return;
    }

    setRecovery({ error: "", missing: false, preparing: false, requestKey, scopeKey });

    let cancelled = false;
    setState(loadingModuleCatalogFamilyState(undefined, projectRoot, catalogFamily));
    pageRequestInFlight.current = true;
    void queryProjectCatalog({
      projectRoot,
      entity: "module",
      tag: catalogFamily,
      ...(searchQuery ? { name: searchQuery } : {}),
      limit: MODULE_CATALOG_PAGE_SIZE,
      offset: 0,
      includeData: false
    })
      .then((payload) => {
        if (
          !cancelled &&
          generation === requestGeneration.current &&
          currentRequestKey.current === requestKey
        ) {
          setState(moduleCatalogFamilyStateWithPage(undefined, payload, projectRoot, catalogFamily));
        }
      })
      .catch(async (error: unknown) => {
        if (
          !cancelled &&
          generation === requestGeneration.current &&
          currentRequestKey.current === requestKey
        ) {
          const loadError = localizedParaDevServiceError(translator.current, error);
          setState(
            moduleCatalogFamilyStateWithError(
              undefined,
              projectRoot,
              catalogFamily,
              loadError
            )
          );
          const readiness = projectCatalogReadinessFromError(error);
          if (readiness) {
            applyCatalogReadiness(
              readiness,
              loadError,
              scopeKey,
              requestKey,
              bypassByScopeRef,
              setBypassByScope,
              setRecovery
            );
            return;
          }
          try {
            const status = await loadProjectCatalogStatus({ projectRoot });
            if (
              !cancelled &&
              generation === requestGeneration.current &&
              currentRequestKey.current === requestKey
            ) {
              applyCatalogReadiness(
                status,
                loadError,
                scopeKey,
                requestKey,
                bypassByScopeRef,
                setBypassByScope,
                setRecovery
              );
            }
          } catch {
            // The original query error remains the actionable error when status cannot be classified.
          }
        }
      })
      .finally(() => {
        if (
          !cancelled &&
          generation === requestGeneration.current &&
          currentRequestKey.current === requestKey
        ) {
          pageRequestInFlight.current = false;
        }
      });
    return () => {
      cancelled = true;
    };
  }, [available, catalogFamily, enabled, projectRoot, reloadNonce, requestKey, scopeKey, searchQuery]);

  const loadMore = useCallback(async () => {
    const current = activeState;
    if (!enabled || !current || current.loading || current.nextOffset === null || pageRequestInFlight.current) {
      return;
    }
    const generation = requestGeneration.current;
    const nextOffset = current.nextOffset;
    pageRequestInFlight.current = true;
    setState(loadingModuleCatalogFamilyState(current, projectRoot, catalogFamily));
    try {
      const payload = await queryProjectCatalog({
        projectRoot,
        entity: "module",
        tag: catalogFamily,
        ...(searchQuery ? { name: searchQuery } : {}),
        limit: MODULE_CATALOG_PAGE_SIZE,
        offset: nextOffset,
        includeData: false
      });
      if (generation !== requestGeneration.current || currentRequestKey.current !== requestKey) {
        return;
      }
      setState((value) =>
        value && value.projectRoot === projectRoot && value.family === catalogFamily
          ? moduleCatalogFamilyStateWithPage(value, payload, projectRoot, catalogFamily)
          : value
      );
    } catch (error: unknown) {
      if (generation === requestGeneration.current && currentRequestKey.current === requestKey) {
        setState((value) =>
          value && value.projectRoot === projectRoot && value.family === catalogFamily
            ? moduleCatalogFamilyStateWithError(
                value,
                projectRoot,
                catalogFamily,
                localizedParaDevServiceError(translator.current, error)
              )
            : value
        );
      }
    } finally {
      if (generation === requestGeneration.current && currentRequestKey.current === requestKey) {
        pageRequestInFlight.current = false;
      }
    }
  }, [activeState, catalogFamily, enabled, projectRoot, requestKey, searchQuery]);

  const retry = useCallback(() => {
    if (activeHydrationError) {
      setReloadNonce((value) => value + 1);
      return;
    }
    if (activeState?.rows.length && activeState.nextOffset !== null) {
      void loadMore();
      return;
    }
    setReloadNonce((value) => value + 1);
  }, [activeHydrationError, activeState, loadMore]);

  const reconcileMutation = useCallback((mutation: CatalogMutationResult | null | undefined): CatalogMutationReconcileResult => {
    if (
      !available ||
      !mounted.current ||
      currentScopeKey.current !== scopeKey
    ) {
      return "latched";
    }

    if (
      isDirtyCatalogBypass(activeBypassStatus) ||
      isDirtyCatalogBypass(bypassByScopeRef.current[scopeKey])
    ) {
      return "latched";
    }

    if (mutation?.status === "applied") {
      if (bypassByScopeRef.current[scopeKey]) {
        return "latched";
      }
      setReloadNonce((value) => value + 1);
      return "applied";
    }

    requestGeneration.current += 1;
    pageRequestInFlight.current = false;
    hydrationTargetsInFlight.current.clear();
    lookupEntitiesInFlight.current.clear();
    setHydratingEntityId("");
    setHydrationErrors({});
    setState(null);
    const status: ModuleCatalogBypassStatus = mutation?.status === "failed" || mutation?.status === "not_configured"
      ? mutation.status
      : "unknown";
    const nextBypass = { ...bypassByScopeRef.current, [scopeKey]: status };
    bypassByScopeRef.current = nextBypass;
    setBypassByScope(nextBypass);
    setRecovery({
      error: "",
      missing: status === "not_configured",
      preparing: false,
      requestKey,
      scopeKey
    });
    return "bypassed";
  }, [activeBypassStatus, available, requestKey, scopeKey]);

  const refreshCatalog = useCallback(async (): Promise<boolean> => {
    if (!available || activeRecovery?.preparing || !mounted.current) {
      return false;
    }
    const generation = requestGeneration.current;
    const operationScopeKey = scopeKey;
    setRecovery({
      error: "",
      missing: activeBypassStatus === "not_configured" || activeRecovery?.missing || false,
      preparing: true,
      requestKey,
      scopeKey
    });
    try {
      await refreshProjectCatalog({ projectRoot });
      if (
        generation !== requestGeneration.current ||
        !mounted.current ||
        currentScopeKey.current !== operationScopeKey
      ) {
        return false;
      }
      const nextBypass = withoutCatalogBypass(bypassByScopeRef.current, scopeKey);
      bypassByScopeRef.current = nextBypass;
      setBypassByScope(nextBypass);
      setReloadNonce((value) => value + 1);
      return true;
    } catch (error: unknown) {
      if (
        generation === requestGeneration.current &&
        mounted.current &&
        currentScopeKey.current === operationScopeKey
      ) {
        setRecovery({
          error: localizedParaDevServiceError(translator.current, error),
          missing: activeBypassStatus === "not_configured" || activeRecovery?.missing || false,
          preparing: false,
          requestKey,
          scopeKey
        });
      }
      return false;
    }
  }, [activeBypassStatus, activeRecovery, available, projectRoot, requestKey, scopeKey]);

  const prepareCatalog = useCallback(async () => {
    const catalogMissing = activeBypassStatus === "not_configured" || activeRecovery?.missing;
    if (!catalogMissing) {
      return;
    }
    await refreshCatalog();
  }, [activeBypassStatus, activeRecovery, refreshCatalog]);

  const repairCatalog = useCallback(async (): Promise<boolean> => {
    if (!activeBypassStatus || activeBypassStatus === "not_configured") {
      return false;
    }
    return refreshCatalog();
  }, [activeBypassStatus, refreshCatalog]);

  useEffect(() => {
    if (
      !enabled ||
      !activeState ||
      activeState.loading ||
      activeState.error ||
      !externalSelectionEntityId ||
      activeState.rows.some((row) => moduleCatalogRowMatchesEntity(row, externalSelectionEntityId))
    ) {
      return;
    }
    const generation = requestGeneration.current;
    const lookupKey = `${requestKey}::${externalSelectionEntityId}`;
    if (lookupEntitiesInFlight.current.has(lookupKey)) {
      return;
    }
    const requestToken = Symbol(lookupKey);
    lookupEntitiesInFlight.current.set(lookupKey, requestToken);
    setHydratingEntityId(externalSelectionEntityId);
    setHydrationErrors((current) =>
      withoutModuleCatalogHydrationError(current, requestKey, externalSelectionEntityId)
    );
    let retryBlocked = false;
    void queryProjectCatalog({
      projectRoot,
      entity: "module",
      tag: catalogFamily,
      name: moduleCatalogModuleIdForEntity(externalSelectionEntityId),
      limit: 1,
      offset: 0,
      includeData: true
    })
      .then((payload) => {
        if (generation !== requestGeneration.current || currentRequestKey.current !== requestKey) {
          return;
        }
        const row = payload.rows.find((candidate) =>
          moduleCatalogRowMatchesEntity(candidate, externalSelectionEntityId)
        );
        if (!row) {
          onExternalSelectionMissing(externalSelectionEntityId);
          return;
        }
        if (!moduleCatalogRowHasHydratedData(row, catalogFamily)) {
          throw new Error("Catalog returned incomplete module data.");
        }
        setState((value) => (value ? moduleCatalogFamilyStateWithDiscoveredRow(value, row) : value));
      })
      .catch((error: unknown) => {
        if (
          generation === requestGeneration.current &&
          currentRequestKey.current === requestKey &&
          currentSelectedId.current === externalSelectionEntityId
        ) {
          retryBlocked = true;
          setHydrationErrors((current) => ({
            ...current,
            [moduleCatalogHydrationErrorKey(requestKey, externalSelectionEntityId)]:
              localizedParaDevServiceError(translator.current, error)
          }));
        }
      })
      .finally(() => {
        if (!retryBlocked && lookupEntitiesInFlight.current.get(lookupKey) === requestToken) {
          lookupEntitiesInFlight.current.delete(lookupKey);
        }
        if (generation === requestGeneration.current && currentRequestKey.current === requestKey) {
          setHydratingEntityId((value) =>
            value === externalSelectionEntityId ? "" : value
          );
        }
      });
  }, [
    activeState,
    catalogFamily,
    enabled,
    externalSelectionEntityId,
    onExternalSelectionMissing,
    projectRoot,
    requestKey
  ]);

  useEffect(() => {
    if (!enabled || !activeState || activeState.loading || activeState.error || !selectedId) {
      return;
    }
    const targetId = moduleCatalogTargetIdForEntity(activeState, selectedId);
    if (!targetId || hydrationTargetsInFlight.current.has(targetId)) {
      return;
    }
    const generation = requestGeneration.current;
    const requestToken = Symbol(`${requestKey}::${targetId}`);
    hydrationTargetsInFlight.current.set(targetId, requestToken);
    setHydratingEntityId(selectedId);
    setHydrationErrors((current) =>
      withoutModuleCatalogHydrationError(current, requestKey, selectedId)
    );
    let retryBlocked = false;
    void queryProjectCatalog({
      projectRoot,
      targetId,
      limit: 1,
      offset: 0,
      includeData: true
    })
      .then((payload) => {
        if (generation !== requestGeneration.current || currentRequestKey.current !== requestKey) {
          return;
        }
        const row = payload.rows.find((candidate) => candidate.target_id === targetId);
        if (row) {
          if (!moduleCatalogRowHasHydratedData(row, catalogFamily)) {
            throw new Error("Catalog returned incomplete module data.");
          }
          setState((value) => (value ? moduleCatalogFamilyStateWithHydratedRow(value, row) : value));
          return;
        }
        throw new Error("Catalog did not return the selected module data.");
      })
      .catch((error: unknown) => {
        if (
          generation === requestGeneration.current &&
          currentRequestKey.current === requestKey &&
          currentSelectedId.current === selectedId
        ) {
          retryBlocked = true;
          setHydrationErrors((current) => ({
            ...current,
            [moduleCatalogHydrationErrorKey(requestKey, selectedId)]:
              localizedParaDevServiceError(translator.current, error)
          }));
        }
      })
      .finally(() => {
        if (!retryBlocked && hydrationTargetsInFlight.current.get(targetId) === requestToken) {
          hydrationTargetsInFlight.current.delete(targetId);
        }
        if (generation === requestGeneration.current && currentRequestKey.current === requestKey) {
          setHydratingEntityId((value) => (value === selectedId ? "" : value));
        }
      });
  }, [activeState, catalogFamily, enabled, projectRoot, requestKey, selectedId]);

  return {
    bypassed: Boolean(activeBypassStatus),
    catalogMissing: activeBypassStatus === "not_configured" || (activeRecovery?.missing ?? false),
    catalogMutationDirty: isDirtyCatalogBypass(activeBypassStatus),
    catalogPreparing: activeRecovery?.preparing ?? false,
    effectiveBrowser,
    enabled,
    hasMore: activeState?.hasMore ?? false,
    hydratingEntityId,
    loadError: activeRecovery?.missing
      ? activeRecovery.error
      : activeState?.error || activeHydrationError,
    loadedCount: enabled ? activeState?.rows.length ?? 0 : null,
    loading: enabled && (activeState?.loading ?? true),
    loadMore,
    prepareCatalog,
    reconcileMutation,
    repairCatalog,
    repairError:
      activeBypassStatus && activeBypassStatus !== "not_configured"
        ? activeRecovery?.error ?? ""
        : "",
    retry,
    totalCount: enabled
      ? activeState?.filteredCount || (searchQuery ? 0 : family?.item_count ?? 0)
      : null
  };
}

function moduleCatalogHydrationErrorKey(requestKey: string, entityId: string): string {
  return `${requestKey}\u0000${entityId}`;
}

function withoutModuleCatalogHydrationError(
  errors: Record<string, string>,
  requestKey: string,
  entityId: string
): Record<string, string> {
  const key = moduleCatalogHydrationErrorKey(requestKey, entityId);
  if (!Object.prototype.hasOwnProperty.call(errors, key)) {
    return errors;
  }
  const next = { ...errors };
  delete next[key];
  return next;
}

function withoutCatalogBypass(
  bypassByScope: Record<string, ModuleCatalogBypassStatus>,
  scopeKey: string
): Record<string, ModuleCatalogBypassStatus> {
  if (!Object.prototype.hasOwnProperty.call(bypassByScope, scopeKey)) {
    return bypassByScope;
  }
  const next = { ...bypassByScope };
  delete next[scopeKey];
  return next;
}

function isDirtyCatalogBypass(status: ModuleCatalogBypassStatus | undefined): boolean {
  return status === "failed" || status === "unknown";
}

function applyCatalogReadiness(
  status: { code: "catalog.present" | "catalog.missing" | "catalog.incomplete" | "catalog.unreadable" },
  loadError: string,
  scopeKey: string,
  requestKey: string,
  bypassRef: MutableRefObject<Record<string, ModuleCatalogBypassStatus>>,
  setBypass: Dispatch<SetStateAction<Record<string, ModuleCatalogBypassStatus>>>,
  setRecovery: Dispatch<SetStateAction<ModuleCatalogRecoveryState>>
): void {
  if (status.code === "catalog.present") {
    return;
  }
  const bypassStatus: ModuleCatalogBypassStatus =
    status.code === "catalog.missing" ? "not_configured" : "failed";
  const nextBypass = {
    ...bypassRef.current,
    [scopeKey]: bypassStatus
  };
  bypassRef.current = nextBypass;
  setBypass(nextBypass);
  setRecovery({
    error: bypassStatus === "not_configured" ? "" : loadError,
    missing: bypassStatus === "not_configured",
    preparing: false,
    requestKey,
    scopeKey
  });
}
