import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import type { FormEvent, KeyboardEvent, MouseEvent, PointerEvent, ReactNode } from "react";
import { ArrowDown, ArrowLeft, ArrowRight, ArrowUp, Crosshair, Download, GitBranch, PanelTopOpen, Pin, Plus, RefreshCw, RotateCcw, Save, Search, Trash2, Upload, X, ZoomIn, ZoomOut } from "lucide-react";
import type { Translator } from "../i18n";
import type { ProjectDiagramRelationship } from "../types";
import { diagramRelationshipCycleCandidateIds, diagramRelationshipRelatedNodeIds } from "./diagramRelationships";
import { exportDiagramJson } from "./diagramJson";
import { diagramImageHydrationNodeCount, isDirectDiagramImageUrl, loadDiagramImageUrls } from "./diagramImages";
import type { DiagramImageLoadProgress } from "./diagramImages";
import { dragDeltaToGrid, moveDiagramNodeRelayoutDescendants, resolveDiagramLayout } from "./layoutModel";
import { diagramNodeRelationshipScopeKey } from "./diagramScope";
import type { CanvasPoint, DiagramBounds, DiagramDocument, DiagramEdge, DiagramEdgeKind, DiagramMoveDelta, DiagramNode, DiagramNodeId, DiagramNodeLayoutHints, DiagramPositionMode, DiagramViewport, ResolvedDiagramNode } from "./layoutModel";

type ProjectDiagramViewProps = {
  createNodeLabel?: string;
  diagramApplyBusy?: boolean;
  diagramApplyError?: string;
  diagramChangedEntities?: DiagramChangedEntity[];
  diagramCanRedo?: boolean;
  diagramCanUndo?: boolean;
  diagramChangedEntityIds?: string[];
  diagramDirty?: boolean;
  document: DiagramDocument;
  onDiagramApply?: () => void;
  onDiagramAutoLayout?: () => void;
  onDiagramCreateNode?: () => void;
  onDiagramDiscard?: () => void;
  onDiagramInsertRoot?: () => void;
  onDiagramImportJson?: (text: string) => void;
  onDiagramPinAll?: () => void;
  onDiagramRedo?: () => void;
  onDiagramUndo?: () => void;
  onDiagramUnpinAll?: () => void;
  onDiagramViewportSave?: (viewport: DiagramViewport) => void;
  onNodeAddDependency?: (targetId: string, sourceId: string) => void;
  onNodeAddReference?: (sourceId: string, targetId: string) => void;
  onNodeAddUnlock?: (sourceId: string, targetId: string) => void;
  onNodeClearParent?: (nodeId: string) => void;
  onNodeAutoLayoutDescendants?: (nodeId: string) => void;
  onNodeAutoLayout?: (nodeId: string) => void;
  onNodeAutoLayoutSubtree?: (nodeId: string) => void;
  onNodeInsertChild?: (nodeId: string) => void;
  onNodeMakeRelative?: (nodeId: string) => void;
  onNodeMakeSubtreeRelative?: (nodeId: string) => void;
  onNodeMove?: (nodeId: string, delta: DiagramMoveDelta) => void;
  onNodeMoveKeepingDescendants?: (nodeId: string, delta: DiagramMoveDelta) => void;
  onNodeMoveRelayoutDescendants?: (nodeId: string, delta: DiagramMoveDelta) => void;
  onNodeMoveSubtree?: (nodeId: string, delta: DiagramMoveDelta) => void;
  onNodePin?: (nodeId: string) => void;
  onNodePinSubtree?: (nodeId: string) => void;
  onNodeReorderSibling?: (nodeId: string, direction: -1 | 1) => void;
  onNodeRemoveDependency?: (targetId: string, sourceId: string) => void;
  onNodeRemoveOnly?: (nodeId: string) => void;
  onNodeRemoveReference?: (sourceId: string, targetId: string) => void;
  onNodeRemoveUnlock?: (sourceId: string, targetId: string) => void;
  onNodeSetRelationship?: (relationship: ProjectDiagramRelationship, selectedNodeId: string, relatedNodeId: string, present: boolean) => void;
  onNodeRemoveSubtree?: (nodeId: string) => void;
  onNodeSetPosition?: (nodeId: string, position: { x: number; y: number }) => void;
  onNodeSetLayoutHints?: (nodeId: string, hints: DiagramNodeLayoutHints) => void;
  onNodeSetParent?: (nodeId: string, parentId: string) => void;
  onNodeUnpin?: (nodeId: string) => void;
  onNodeUnpinSubtree?: (nodeId: string) => void;
  onNodeOpen?: (nodeId: string) => void;
  onNodeOpenModule?: (nodeId: string, sourcePath?: string) => void;
  onNodeSelect?: (nodeId: string) => void;
  onNodeInfoClose?: () => void;
  openedNodeId?: string;
  projectRoot?: string;
  readOnly?: boolean;
  readOnlyReason?: string;
  relationshipActions?: readonly ProjectDiagramRelationship[];
  selectedNodeId?: string;
  title: string;
  t: Translator;
};

export type DiagramChangedEntity = {
  draftText?: string;
  draftUnavailable?: boolean;
  id: string;
  path?: string;
  title?: string;
};

type DiagramApplyPreview = {
  rows: DiagramApplyPreviewRow[];
  text: string;
  title: string;
};

type DiagramApplyPreviewRow = {
  entity: DiagramChangedEntity;
  status: "skip" | "write";
};

type DiagramProjection = {
  edges: ProjectedEdge[];
  nodes: ResolvedDiagramNode[];
  viewBox: string;
};

type DiagramProjectionPreview = {
  nodeIds: Iterable<DiagramNodeId>;
  offset: CanvasPoint;
};

type ProjectedEdge = DiagramEdge & {
  path: string;
};

type DiagramDragState = {
  command: DiagramNodeMoveCommandKind;
  current: CanvasPoint;
  nodeId: DiagramNodeId;
  pointerId: number;
  start: CanvasPoint;
};

type DiagramPanDragState = {
  pointerId: number;
  startClient: CanvasPoint;
  startOffset: CanvasPoint;
  unitsPerClientPx: CanvasPoint;
};

type DiagramKeyboardShortcut = { kind: "fit" } | { delta: CanvasPoint; kind: "pan" } | { delta: -1 | 1; kind: "zoom" } | { kind: "none" };

type DiagramCanvasEditCommand = {
  kind: "apply" | "redo" | "undo";
};

type DiagramWheelZoomInput = {
  ctrlKey: boolean;
  deltaY: number;
  metaKey?: boolean;
};
type DiagramWheelPanInput = {
  deltaX: number;
  deltaY: number;
  shiftKey?: boolean;
};
type DiagramWheelClientPointInput = {
  clientX: number;
  clientY: number;
};
type DiagramWheelClientRectInput = {
  bottom: number;
  left: number;
  right: number;
  top: number;
};
type DiagramCanvasPanStartInput = {
  button: number;
  targetIsCanvas: boolean;
};

export type DiagramApplyCommand = "apply" | "none" | "review";
type DiagramViewportSize = {
  height: number;
  width: number;
};
type DiagramWheelZoomState = {
  diagramViewBox: string;
  fittedViewBox: string;
  panOffset: CanvasPoint;
  zoomIndex: number;
};

type DiagramSearchKeyAction = { kind: "clear" | "next" | "none" | "previous" };

type DiagramNodeMoveCommandKind = "fixed-descendants" | "node" | "relayout-descendants" | "subtree";
type DiagramRelationshipPickKind = "dependency" | "reference" | "unlock";

type DiagramRelationshipPickMode = {
  kind: DiagramRelationshipPickKind;
  nodeId: DiagramNodeId;
  relationship?: ProjectDiagramRelationship;
};

type DiagramProviderRelationshipModel = {
  candidates: DiagramCandidate[];
  relatedIds: string[];
  relationship: ProjectDiagramRelationship;
};

type DiagramNodeMoveCommand = {
  delta: DiagramMoveDelta;
  kind: DiagramNodeMoveCommandKind;
};

type DiagramMoveDirection = "down" | "left" | "right" | "up";

type DiagramMoveDirectionTranslationKey = Parameters<Translator>[0];

type DiagramToolbarMoveMode = {
  disabled: boolean;
  id: DiagramNodeMoveCommandKind;
  label: string;
  title: string;
  move: ((nodeId: string, delta: DiagramMoveDelta) => void) | undefined;
};

type DiagramNodeDeleteCommand = {
  kind: "node" | "subtree";
};

type DiagramNodeRelationships = {
  exactLinks: DiagramExactRelationshipLink[];
  prerequisites: string[];
  references: string[];
  referenceLinks: DiagramReferenceLink[];
  unlocks: string[];
};

type DiagramExactRelationshipLink = {
  edgeId: string;
  label: string;
  relatedId: string;
  relationshipKind: string;
  sourceId: string;
  targetId: string;
};

type DiagramCandidate = {
  id: string;
  title: string;
};

type DiagramReferenceLink = {
  relatedId: string;
  sourceId: string;
  targetId: string;
};

type DiagramSiblingReorderState = {
  canReorderEarlier: boolean;
  canReorderLater: boolean;
  siblingCount: number;
  siblingIds: DiagramNodeId[];
  siblingIndex: number;
};

type SearchableDiagramNode = Pick<ResolvedDiagramNode, "id" | "payload" | "title">;
type SearchableDiagramViewportNode = SearchableDiagramNode & Pick<ResolvedDiagramNode, "height" | "width" | "worldX" | "worldY">;

type DiagramModeCounts = Record<ResolvedDiagramNode["mode"], number>;
type DiagramEdgeCounts = Record<DiagramEdgeKind, number>;

type DiagramSelectionFact = {
  label: string;
  value: string;
};

type DiagramImageLoadState = DiagramImageLoadProgress & {
  status: "done" | "idle" | "loading";
};

export type DiagramMoveFootprintSummary = {
  affectedIds: DiagramNodeId[];
  hint: string;
  impact: string;
  label: string;
  title: string;
};

type DiagramStoredPositionNode = Pick<ResolvedDiagramNode, "mode" | "parentId" | "worldX" | "worldY"> & Pick<Partial<ResolvedDiagramNode>, "dx" | "dy" | "x" | "y">;
type DiagramFocusCoordinateBadgeNode = Pick<ResolvedDiagramNode, "mode" | "worldX" | "worldY"> & Pick<Partial<ResolvedDiagramNode>, "dx" | "dy" | "relativePositionKind">;

type DiagramNodeClassOptions = {
  branchMember?: boolean;
  draggable: boolean;
  dragging: boolean;
  focusNode: boolean;
  iconNode?: boolean;
  interactive: boolean;
  mode: ResolvedDiagramNode["mode"];
  moveAffected?: boolean;
  relationshipPickCandidate?: boolean;
  relationshipPickSource?: boolean;
  searchCurrent: boolean;
  searchMatch: boolean;
  selected: boolean;
};

type DiagramMiniMapNodeClassOptions = {
  moveAffected?: boolean;
  searchCurrent: boolean;
  searchMatch: boolean;
  selected: boolean;
};

type DiagramNodeVisibleBox = {
  height: number;
  width: number;
  x: number;
  y: number;
};
type DiagramViewportCenterNode = Pick<ResolvedDiagramNode, "height" | "width" | "worldX" | "worldY"> & Pick<Partial<ResolvedDiagramNode>, "payload">;

type DiagramDragHintOptions = {
  activeMoveMode: DiagramNodeMoveCommandKind;
  canMoveKeepingDescendants: boolean;
  canMoveNode: boolean;
  canMoveRelayoutDescendants: boolean;
  canMoveSubtree: boolean;
};
type DiagramHoverCardState = {
  left: number;
  nodeId: DiagramNodeId;
  top: number;
};
export type DiagramNodeHoverCardRow = {
  label: string;
  value: string;
};

const VIEW_PADDING = 48;
const MIN_VIEW_WIDTH = 480;
const MIN_VIEW_HEIGHT = 220;
const MIN_CANVAS_HEIGHT = 360;
const MAX_LABEL_LENGTH = 30;
const MAX_QUICK_CANDIDATE_BUTTONS = 6;
const NODE_IMAGE_SIDE = 40;
const FOCUS_NODE_IMAGE_SIDE = 72;
const FOCUS_NODE_VISIBLE_RATIO = 0.75;
const NON_FOCUS_NODE_IMAGE_SIDE = 30;
const DIAGRAM_ZOOM_LEVELS = [1, 1.25, 1.5, 1.75, 2, 2.25, 2.5, 2.75, 3, 3.25, 3.5, 3.75, 4] as const;
const DEFAULT_DIAGRAM_ZOOM_INDEX = 6;
const DIAGRAM_CANVAS_KEYSHORTCUTS = "ArrowUp ArrowDown ArrowLeft ArrowRight + - 0 Escape";
const DIAGRAM_CANVAS_UNDO_KEYSHORTCUTS = "Meta+Z Control+Z";
const DIAGRAM_CANVAS_REDO_KEYSHORTCUTS = "Shift+Meta+Z Shift+Control+Z Meta+Y Control+Y";
const DIAGRAM_CANVAS_APPLY_KEYSHORTCUTS = "Meta+S Control+S";
const DIAGRAM_NODE_SELECT_KEYSHORTCUTS = "Enter Space";
const DIAGRAM_NODE_ARROW_KEYSHORTCUTS = "ArrowUp ArrowDown ArrowLeft ArrowRight";
const DIAGRAM_NODE_SUBTREE_KEYSHORTCUTS = "Shift+ArrowUp Shift+ArrowDown Shift+ArrowLeft Shift+ArrowRight";
const DIAGRAM_NODE_KEEP_DESCENDANTS_KEYSHORTCUTS = "Alt+ArrowUp Alt+ArrowDown Alt+ArrowLeft Alt+ArrowRight";
const DIAGRAM_NODE_RELAYOUT_DESCENDANTS_KEYSHORTCUTS = "Control+ArrowUp Control+ArrowDown Control+ArrowLeft Control+ArrowRight Meta+ArrowUp Meta+ArrowDown Meta+ArrowLeft Meta+ArrowRight";
const DIAGRAM_NODE_REMOVE_KEYSHORTCUTS = "Delete Backspace";
const DIAGRAM_NODE_REMOVE_SUBTREE_KEYSHORTCUTS = "Shift+Delete Shift+Backspace";
const DIAGRAM_NODE_DOUBLE_CLICK_MS = 1500;

export function diagramNodeClickAction({ eventDetail, hasOpen, lastClickAt, now }: { eventDetail: number; hasOpen: boolean; lastClickAt: number; now: number }): { action: "open" | "select"; lastClickAt: number } {
  if (!hasOpen) {
    return { action: "select", lastClickAt: 0 };
  }
  if (eventDetail >= 2 || (lastClickAt > 0 && now - lastClickAt <= DIAGRAM_NODE_DOUBLE_CLICK_MS)) {
    return { action: "open", lastClickAt: 0 };
  }
  return { action: "select", lastClickAt: now };
}

export function diagramZoomIndexForViewportZoom(zoom: number | undefined): number {
  if (typeof zoom !== "number" || !Number.isFinite(zoom) || zoom <= 0) {
    return DEFAULT_DIAGRAM_ZOOM_INDEX;
  }
  let bestIndex = DEFAULT_DIAGRAM_ZOOM_INDEX;
  DIAGRAM_ZOOM_LEVELS.forEach((level, index) => {
    const bestDistance = Math.abs(DIAGRAM_ZOOM_LEVELS[bestIndex] - zoom);
    const distance = Math.abs(level - zoom);
    if (distance < bestDistance) {
      bestIndex = index;
    }
  });
  return bestIndex;
}

export function diagramInitialZoomIndexForDocument(document: Pick<DiagramDocument, "nodes" | "viewport">): number {
  if (document.viewport) {
    return diagramZoomIndexForViewportZoom(document.viewport.zoom);
  }
  return DEFAULT_DIAGRAM_ZOOM_INDEX;
}

function validDiagramZoomIndex(zoomIndex: number): number {
  return Number.isInteger(zoomIndex) && zoomIndex >= 0 && zoomIndex < DIAGRAM_ZOOM_LEVELS.length ? zoomIndex : DEFAULT_DIAGRAM_ZOOM_INDEX;
}

export function diagramZoomIndexAfterDelta(zoomIndex: number, delta: -1 | 1): number {
  const current = validDiagramZoomIndex(zoomIndex);
  return Math.max(0, Math.min(DIAGRAM_ZOOM_LEVELS.length - 1, current + delta));
}

export function diagramPanOffsetForViewport(viewport: DiagramDocument["viewport"]): CanvasPoint {
  if (!viewport || !Number.isFinite(viewport.x) || !Number.isFinite(viewport.y)) {
    return { x: 0, y: 0 };
  }
  return { x: viewport.x, y: viewport.y };
}

export function diagramViewportForViewState(zoomIndex: number, panOffset: CanvasPoint): DiagramViewport {
  return {
    x: formatOffsetNumber(panOffset.x),
    y: formatOffsetNumber(panOffset.y),
    zoom: DIAGRAM_ZOOM_LEVELS[validDiagramZoomIndex(zoomIndex)],
  };
}

export function diagramApplyCommandForState({ busy, dirty, hasReview, reviewAccepted, unavailable }: { busy: boolean; dirty: boolean; hasReview: boolean; reviewAccepted: boolean; unavailable: boolean }): DiagramApplyCommand {
  if (!dirty || busy || unavailable) {
    return "none";
  }
  if (hasReview && !reviewAccepted) {
    return "review";
  }
  return "apply";
}

export function diagramWheelZoomDelta(event: DiagramWheelZoomInput): -1 | 0 | 1 {
  if ((!event.ctrlKey && !event.metaKey) || event.deltaY === 0) {
    return 0;
  }
  return event.deltaY < 0 ? 1 : -1;
}

export function diagramWheelClientPointInsideRect(point: DiagramWheelClientPointInput, rect: DiagramWheelClientRectInput): boolean {
  if (rect.left >= rect.right || rect.top >= rect.bottom) {
    return false;
  }
  return point.clientX >= rect.left && point.clientX <= rect.right && point.clientY >= rect.top && point.clientY <= rect.bottom;
}

export function diagramWheelPanDelta(event: DiagramWheelPanInput, viewBox: string, viewport: DiagramViewportSize): CanvasPoint {
  const rect = viewBoxRect(viewBox);
  if (!rect || !Number.isFinite(viewport.width) || !Number.isFinite(viewport.height) || viewport.width <= 0 || viewport.height <= 0) {
    return { x: 0, y: 0 };
  }
  const deltaX = Number.isFinite(event.deltaX) ? event.deltaX : 0;
  const deltaY = Number.isFinite(event.deltaY) ? event.deltaY : 0;
  const horizontalDelta = event.shiftKey ? deltaX || deltaY : deltaX;
  const verticalDelta = event.shiftKey ? 0 : deltaY;
  return {
    x: formatOffsetNumber(horizontalDelta * (rect.width / viewport.width)),
    y: formatOffsetNumber(verticalDelta * (rect.height / viewport.height)),
  };
}

export function diagramNodeDragStartAllowed(button: number): boolean {
  return button === 0;
}

export function diagramCanvasPanStartAllowed({ button, targetIsCanvas }: DiagramCanvasPanStartInput): boolean {
  return (button === 0 && targetIsCanvas) || button === 1;
}

export function ProjectDiagramView({ createNodeLabel = "", diagramApplyBusy = false, diagramApplyError = "", diagramCanRedo = false, diagramCanUndo = false, diagramChangedEntities, diagramChangedEntityIds = [], diagramDirty = false, document, onDiagramApply, onDiagramAutoLayout, onDiagramCreateNode, onDiagramDiscard, onDiagramInsertRoot, onDiagramImportJson, onDiagramPinAll, onDiagramRedo, onDiagramUndo, onDiagramUnpinAll, onDiagramViewportSave, onNodeAddDependency, onNodeAddReference, onNodeAddUnlock, onNodeClearParent, onNodeAutoLayout, onNodeAutoLayoutDescendants, onNodeAutoLayoutSubtree, onNodeInfoClose, onNodeInsertChild, onNodeMakeRelative, onNodeMakeSubtreeRelative, onNodeMove, onNodeMoveKeepingDescendants, onNodeMoveRelayoutDescendants, onNodeMoveSubtree, onNodeOpen, onNodeOpenModule, onNodePin, onNodePinSubtree, onNodeReorderSibling, onNodeRemoveDependency, onNodeRemoveOnly, onNodeRemoveReference, onNodeRemoveSubtree, onNodeRemoveUnlock, onNodeSelect, onNodeSetPosition, onNodeSetLayoutHints, onNodeSetParent, onNodeSetRelationship, onNodeUnpin, onNodeUnpinSubtree, openedNodeId = "", projectRoot = "", readOnly = false, readOnlyReason = "", relationshipActions = [], selectedNodeId = "", title, t }: ProjectDiagramViewProps) {
  const panelRef = useRef<HTMLElement | null>(null);
  const canvasRef = useRef<HTMLDivElement | null>(null);
  const svgRef = useRef<SVGSVGElement | null>(null);
  const wheelZoomStateRef = useRef<DiagramWheelZoomState | null>(null);
  const panDragActiveRef = useRef(false);
  const [dragState, setDragState] = useState<DiagramDragState | null>(null);
  const [selectedMoveMode, setSelectedMoveMode] = useState<DiagramNodeMoveCommandKind>("subtree");
  const [diagramJsonOpen, setDiagramJsonOpen] = useState(false);
  const [diagramJsonText, setDiagramJsonText] = useState("");
  const [diagramApplyReviewAccepted, setDiagramApplyReviewAccepted] = useState(false);
  const [panDragState, setPanDragState] = useState<DiagramPanDragState | null>(null);
  const [relationshipPickMode, setRelationshipPickMode] = useState<DiagramRelationshipPickMode | null>(null);
  const [nodeImageUrls, setNodeImageUrls] = useState<Record<DiagramNodeId, string>>({});
  const imageHydrationTargetCount = projectRoot ? diagramImageHydrationNodeCount(document.nodes) : 0;
  const [nodeImageLoadState, setNodeImageLoadState] = useState<DiagramImageLoadState>(() => diagramImageLoadStateForTargetCount(imageHydrationTargetCount));
  const [nodeSearchIndex, setNodeSearchIndex] = useState(0);
  const [nodeSearchQuery, setNodeSearchQuery] = useState("");
  const [zoomIndex, setZoomIndex] = useState(() => diagramInitialZoomIndexForDocument(document));
  const [panOffset, setPanOffset] = useState<CanvasPoint>(() => diagramPanOffsetForViewport(document.viewport));
  const [canvasSize, setCanvasSize] = useState<DiagramViewportSize>({
    height: MIN_CANVAS_HEIGHT,
    width: MIN_VIEW_WIDTH,
  });
  const [hoverCard, setHoverCard] = useState<DiagramHoverCardState | null>(null);
  const [lastNodeClick, setLastNodeClick] = useState<{
    at: number;
    nodeId: DiagramNodeId;
  } | null>(null);
  const initialViewportKey = diagramInitialViewportKey(document);

  useEffect(() => {
    let cancelled = false;
    const targetCount = projectRoot ? diagramImageHydrationNodeCount(document.nodes) : 0;
    if (targetCount === 0) {
      setNodeImageUrls({});
      setNodeImageLoadState(diagramImageLoadStateForTargetCount(0));
      return () => {
        cancelled = true;
      };
    }
    setNodeImageLoadState(diagramImageLoadStateForTargetCount(targetCount));
    void loadDiagramImageUrls({
      nodes: document.nodes,
      onProgress: (progress) => {
        if (!cancelled) {
          setNodeImageLoadState(diagramImageLoadStateForProgress(progress));
        }
      },
      projectRoot,
      sideLength: (node) => diagramNodeRenderedImageSideLength(node, document.gridSizePx),
    })
      .then((urls) => {
        if (!cancelled) {
          setNodeImageUrls(urls);
          setNodeImageLoadState({
            completed: targetCount,
            hydrated: Object.keys(urls).length,
            status: "done",
            total: targetCount,
          });
        }
      })
      .catch(() => {
        if (!cancelled) {
          setNodeImageUrls({});
          setNodeImageLoadState({
            completed: targetCount,
            hydrated: 0,
            status: "done",
            total: targetCount,
          });
        }
      });
    return () => {
      cancelled = true;
    };
  }, [document.gridSizePx, document.nodes, projectRoot]);

  useEffect(() => {
    if (panDragActiveRef.current) {
      return;
    }
    setZoomIndex(diagramInitialZoomIndexForDocument(document));
    setPanOffset(diagramPanOffsetForViewport(document.viewport));
  }, [document.viewport?.x, document.viewport?.y, document.viewport?.zoom, initialViewportKey]);

  useEffect(() => {
    const element = canvasRef.current;
    if (!element) {
      return;
    }

    const measure = () => {
      const rect = element.getBoundingClientRect();
      const width = Math.max(MIN_VIEW_WIDTH, Math.round(rect.width));
      const height = Math.max(MIN_CANVAS_HEIGHT, Math.round(rect.height));
      setCanvasSize((current) => (current.width === width && current.height === height ? current : { height, width }));
    };

    measure();
    if (typeof ResizeObserver !== "undefined") {
      const observer = new ResizeObserver(measure);
      observer.observe(element);
      return () => observer.disconnect();
    }

    window.addEventListener("resize", measure);
    return () => window.removeEventListener("resize", measure);
  }, []);

  const applyDiagramViewportState = useCallback(
    (nextZoomIndex: number, nextPanOffset: CanvasPoint) => {
      const validZoomIndex = validDiagramZoomIndex(nextZoomIndex);
      const viewport = diagramViewportForViewState(validZoomIndex, nextPanOffset);
      setZoomIndex(validZoomIndex);
      setPanOffset({ x: viewport.x, y: viewport.y });
      onDiagramViewportSave?.(viewport);
    },
    [onDiagramViewportSave],
  );

  useEffect(() => {
    const element = panelRef.current;
    if (!element) {
      return;
    }

    const handleWheel = (event: WheelEvent) => {
      const delta = diagramWheelZoomDelta(event);
      const state = wheelZoomStateRef.current;
      if (!state) {
        return;
      }
      if (delta === 0) {
        const svg = svgRef.current;
        const rect = svg?.getBoundingClientRect();
        if (!svg || !rect || !diagramWheelClientPointInsideRect(event, rect)) {
          return;
        }
        const panDelta = diagramWheelPanDelta(event, state.diagramViewBox, {
          height: rect.height,
          width: rect.width,
        });
        if (panDelta.x === 0 && panDelta.y === 0) {
          return;
        }
        event.preventDefault();
        applyDiagramViewportState(state.zoomIndex, {
          x: state.panOffset.x + panDelta.x,
          y: state.panOffset.y + panDelta.y,
        });
        return;
      }
      event.preventDefault();
      const nextZoomIndex = diagramZoomIndexAfterDelta(state.zoomIndex, delta);
      const point = wheelEventToRootSvgPoint(event, svgRef.current);
      const nextZoomedViewBox = zoomDiagramViewBox(state.fittedViewBox, DIAGRAM_ZOOM_LEVELS[nextZoomIndex]);
      const nextPanOffset = point ? panOffsetForZoomAtPoint(state.diagramViewBox, nextZoomedViewBox, point) : state.panOffset;
      applyDiagramViewportState(nextZoomIndex, nextPanOffset);
    };

    element.addEventListener("wheel", handleWheel, { passive: false });
    return () => element.removeEventListener("wheel", handleWheel);
  }, [applyDiagramViewportState]);

  const diagramChangedRows: DiagramChangedEntity[] = diagramChangedEntities ?? diagramChangedEntityIds.map((id) => ({ id }));
  const diagramHasUnavailableDraft = diagramChangedRows.some((entity) => entity.draftUnavailable);
  const diagramHasWritableRows = diagramChangedRows.some(diagramChangedEntityCanWrite);
  const diagramApplyUnavailableReason = diagramChangedEntities !== undefined && diagramHasUnavailableDraft ? t("workspace.diagram.applyDraftUnavailable") : diagramChangedEntities !== undefined && diagramChangedRows.length > 0 && !diagramHasWritableRows ? t("workspace.diagram.applyUnavailable") : "";
  const diagramApplyUnavailable = Boolean(diagramApplyUnavailableReason);
  const diagramApplyPreview = diagramApplyPreviewForEntities(diagramChangedEntities, t);
  const showDiagramApplyPreview = Boolean(diagramDirty && onDiagramApply && diagramApplyPreview);
  const diagramApplyCommand = diagramApplyCommandForState({
    busy: diagramApplyBusy,
    dirty: Boolean(diagramDirty),
    hasReview: Boolean(diagramApplyPreview),
    reviewAccepted: diagramApplyReviewAccepted,
    unavailable: diagramApplyUnavailable,
  });
  const diagramApplyTitle = diagramApplyUnavailable ? diagramApplyUnavailableReason : diagramApplyCommand === "review" ? t("workspace.diagram.applyReviewFirstTitle") : diagramApplyPreview ? t("workspace.diagram.applyWritableTitle") : t("workspace.diagram.apply");
  const diagramApplyButtonText = diagramApplyBusy ? t("workspace.diagram.applying") : diagramApplyUnavailable ? t("workspace.diagram.applyBlocked") : diagramApplyCommand === "review" ? t("workspace.diagram.applyReviewFirst") : diagramApplyPreview ? t("workspace.diagram.applyWritable") : t("workspace.diagram.apply");
  const handleDiagramApplyAction = () => {
    if (diagramApplyCommand === "review") {
      setDiagramApplyReviewAccepted(true);
      return;
    }
    if (diagramApplyCommand === "apply") {
      onDiagramApply?.();
    }
  };

  useEffect(() => {
    setDiagramApplyReviewAccepted(false);
  }, [diagramApplyPreview?.title, diagramDirty]);

  const dragProjection = useMemo(() => {
    const dragPreviewGridDelta = dragState ? dragDeltaToGrid(dragState.start, dragState.current, document.gridSizePx) : null;
    const dragPreviewDocument = dragState && dragPreviewGridDelta ? diagramDragPreviewDocument(document, dragState.nodeId, dragState.command, dragPreviewGridDelta) : document;
    const dragPreviewOffset =
      dragState && dragState.command !== "relayout-descendants"
        ? {
            x: dragState.current.x - dragState.start.x,
            y: dragState.current.y - dragState.start.y,
          }
        : null;
    const dragPreviewNodeIds = dragState ? diagramDragPreviewNodeIds(dragPreviewDocument, dragState.nodeId, dragState.command) : [];
    const dragPreviewIds = dragPreviewNodeIds.length > 0 ? new Set(dragPreviewNodeIds) : null;
    const projection = projectDiagram(dragPreviewDocument, dragPreviewOffset && dragPreviewIds ? { nodeIds: dragPreviewIds, offset: dragPreviewOffset } : undefined);
    return {
      dragPreviewGridDelta,
      dragPreviewIds,
      dragPreviewOffset,
      projection,
    };
  }, [document.edges, document.gridSizePx, document.layoutOptions, document.nodes, dragState]);

  if (document.nodes.length === 0) {
    wheelZoomStateRef.current = null;
    return (
      <section className="project-diagram-panel empty" aria-label={t("workspace.diagram.aria", { title })}>
        <div className="project-diagram-header">
          <div className="project-diagram-title">
            <span>{t("workspace.diagram.title")}</span>
            <small>{readOnly ? `${t("workspace.diagram.empty")} · ${t("workspace.diagram.readOnly")}` : t("workspace.diagram.empty")}</small>
          </div>
          {readOnly && readOnlyReason ? (
            <p className="project-diagram-read-only-reason" role="note">
              {readOnlyReason}
            </p>
          ) : null}
          <div className="project-diagram-actions">
            {onDiagramCreateNode && createNodeLabel ? (
              <button aria-label={createNodeLabel} className="toolbar-button project-diagram-add-node" disabled={diagramApplyBusy} onClick={onDiagramCreateNode} title={createNodeLabel} type="button">
                <Plus aria-hidden="true" size={13} />
                {createNodeLabel}
              </button>
            ) : null}
            {diagramDirty && diagramChangedRows.length > 0 ? <DiagramDirtyScope entities={diagramChangedRows} t={t} /> : null}
            {diagramApplyError ? <small className="project-diagram-error">{diagramApplyError}</small> : null}
            {diagramDirty && diagramApplyUnavailable ? <small className="project-diagram-warning">{diagramApplyUnavailableReason}</small> : null}
            {showDiagramApplyPreview && diagramApplyPreview ? (
              <small className="project-diagram-apply-preview" title={diagramApplyPreview.title}>
                {diagramApplyPreview.text}
              </small>
            ) : null}
            {diagramDirty && onDiagramApply ? (
              <button className="toolbar-button primary project-diagram-apply" disabled={diagramApplyCommand === "none"} onClick={handleDiagramApplyAction} title={diagramApplyTitle} type="button">
                <Save aria-hidden="true" size={13} />
                {diagramApplyButtonText}
              </button>
            ) : null}
            {diagramDirty && onDiagramDiscard ? (
              <button className="toolbar-button project-diagram-discard" disabled={diagramApplyBusy} onClick={onDiagramDiscard} type="button">
                <RotateCcw aria-hidden="true" size={13} />
                {t("workspace.diagram.discard")}
              </button>
            ) : null}
          </div>
        </div>
        {showDiagramApplyPreview && diagramApplyPreview ? <DiagramApplyReview preview={diagramApplyPreview} t={t} /> : null}
      </section>
    );
  }

  const { dragPreviewGridDelta, dragPreviewIds, dragPreviewOffset, projection } = dragProjection;
  const fittedViewBox = diagramFitViewBoxForViewport(projection.viewBox, canvasSize);
  const zoom = DIAGRAM_ZOOM_LEVELS[zoomIndex];
  const zoomedViewBox = zoomDiagramViewBox(fittedViewBox, zoom);
  const diagramViewBox = panDiagramViewBox(zoomedViewBox, panOffset);
  wheelZoomStateRef.current = {
    diagramViewBox,
    fittedViewBox,
    panOffset,
    zoomIndex,
  };
  const diagramPanSurface = viewBoxRect(diagramViewBox);
  const panStep = document.gridSizePx * 4;
  const modeCounts = diagramModeCounts(projection.nodes);
  const edgeCounts = diagramEdgeCounts(document.edges);
  const nodeSearchMatches = searchDiagramNodes(projection.nodes, nodeSearchQuery);
  const activeNodeSearchIndex = nodeSearchMatches.length > 0 ? Math.min(nodeSearchIndex, nodeSearchMatches.length - 1) : -1;
  const nodeSearchMatchIds = new Set(nodeSearchMatches.map((node) => node.id));
  const currentNodeSearchMatchId = activeNodeSearchIndex >= 0 ? (nodeSearchMatches[activeNodeSearchIndex]?.id ?? "") : "";
  const activeNodeImageLoadState = nodeImageLoadState.total === imageHydrationTargetCount ? nodeImageLoadState : diagramImageLoadStateForTargetCount(imageHydrationTargetCount);
  const nodeImageLoadStatus = diagramImageLoadStatusText(activeNodeImageLoadState, t);
  const nodeImageLoadStatusTitle = diagramImageLoadStatusTitle(activeNodeImageLoadState, t);
  const nodeImageLoadStatusClassName = diagramImageLoadStatusClassName(activeNodeImageLoadState);
  const selectedNode = projection.nodes.find((node) => node.id === selectedNodeId) ?? null;
  const openedNode = openedNodeId ? (projection.nodes.find((node) => node.id === openedNodeId) ?? null) : null;
  const hoveredNode = hoverCard ? (projection.nodes.find((node) => node.id === hoverCard.nodeId) ?? null) : null;
  const selectedChangedEntity = selectedNode ? diagramChangedEntityForNode(diagramChangedRows, selectedNode) : null;
  const selectedNodePositionEditable = selectedNode ? diagramNodePositionEditable(selectedNode.payload) : false;
  const canPinDiagram = document.nodes.some((node) => node.mode !== "absolute");
  const canAutoLayoutDiagram = document.nodes.some((node) => node.mode !== "auto");
  const canInsertRootFocus = document.nodes.some(isDiagramFocusRootTemplateNode);
  const selectedNodeCanPin = selectedNode ? selectedNodePositionEditable && selectedNode.mode !== "absolute" : false;
  const selectedNodeCanAutoLayout = selectedNode ? selectedNodePositionEditable && selectedNode.mode !== "auto" : false;
  const selectedNodeCanMakeRelative = selectedNode ? selectedNodePositionEditable && Boolean(selectedNode.parentId) && selectedNode.mode !== "relative" : false;
  const selectedSubtreeNodes = selectedNode ? diagramSubtreeNodes(document, selectedNode.id) : [];
  const selectedDescendantNodes = selectedNode ? selectedSubtreeNodes.filter((node) => node.id !== selectedNode.id) : [];
  const selectedBranchNodeIds = selectedSubtreeNodes.length > 1 ? new Set(selectedSubtreeNodes.map((node) => node.id)) : null;
  const selectedDescendantNodeIds = selectedDescendantNodes.length > 0 ? new Set(selectedDescendantNodes.map((node) => node.id)) : null;
  const selectedSubtreeCanPin = selectedSubtreeNodes.some((node) => node.mode !== "absolute");
  const selectedSubtreeCanMakeRelative = selectedSubtreeNodes.some((node) => Boolean(node.parentId) && node.mode !== "relative");
  const selectedSubtreeCanAutoLayout = selectedSubtreeNodes.some((node) => node.mode !== "auto");
  const selectedDescendantsCanAutoLayout = selectedDescendantNodes.some((node) => node.mode !== "auto");
  const selectedNodeCanInsertChild = selectedNode ? isDiagramFocusNode(selectedNode) : false;
  const selectedNodeCanRemoveOnly = selectedNode ? isDiagramFocusNode(selectedNode) : false;
  const selectedSubtreeCanRemove = selectedNode ? canRemoveDiagramFocusSubtree(selectedNode) : false;
  const selectedNodeHasDescendants = selectedDescendantNodes.length > 0;
  const selectedNodeSiblingReorderState = selectedNode
    ? diagramSiblingReorderState(document, selectedNode.id)
    : {
        canReorderEarlier: false,
        canReorderLater: false,
        siblingCount: 0,
        siblingIds: [],
        siblingIndex: -1,
      };
  const moveModesForNode = (nodeId: DiagramNodeId) => {
    const node = projection.nodes.find((candidate) => candidate.id === nodeId);
    return node && diagramNodePositionEditable(node.payload)
      ? diagramToolbarMoveModes({
          canMoveRelayoutDescendants: diagramNodeCanMoveRelayoutDescendants(document, nodeId),
          onNodeMove,
          onNodeMoveKeepingDescendants,
          onNodeMoveRelayoutDescendants,
          onNodeMoveSubtree,
          t,
        })
      : [];
  };
  const selectedNodeMoveModes = selectedNode ? moveModesForNode(selectedNode.id) : [];
  const activeSelectedMoveMode = diagramActiveToolbarMoveMode(selectedNodeMoveModes, selectedMoveMode);
  const activeSelectedMoveModeId = activeSelectedMoveMode?.id ?? "node";
  const activeMoveModeIdForNode = (nodeId: DiagramNodeId): DiagramNodeMoveCommandKind => diagramActiveToolbarMoveMode(moveModesForNode(nodeId), selectedMoveMode)?.id ?? "node";
  const activeSelectedMoveAffectedNodeIds = selectedNode && activeSelectedMoveMode ? diagramDragPreviewNodeIds(document, selectedNode.id, activeSelectedMoveModeId) : [];
  const activeSelectedMoveAffectedIds = activeSelectedMoveAffectedNodeIds.length > 0 ? new Set(activeSelectedMoveAffectedNodeIds) : null;
  const activeSelectedMoveModeAffectedCount = activeSelectedMoveAffectedNodeIds.length;
  const activeSelectedMoveFootprint = selectedNode && activeSelectedMoveMode ? diagramMoveFootprintSummary(activeSelectedMoveMode.id, activeSelectedMoveAffectedNodeIds, t) : null;
  const activeSelectedMoveFootprintNodes = activeSelectedMoveAffectedNodeIds.map((id) => projection.nodes.find((node) => node.id === id)).filter((node): node is ResolvedDiagramNode => Boolean(node));
  const centerSelectedMoveFootprint = activeSelectedMoveFootprintNodes.length > 0 ? () => applyDiagramViewportState(zoomIndex, panOffsetToCenterNodes(zoomedViewBox, activeSelectedMoveFootprintNodes, document.gridSizePx)) : undefined;
  const activeSelectedNodeId = selectedNode?.id ?? "";
  const nodeCandidates = projection.nodes.map(diagramNodeCandidate);
  const nodeCandidateById = new Map(nodeCandidates.map((candidate) => [candidate.id, candidate]));
  const selectedPeerNodes = selectedNode ? relationshipCandidateNodes(projection.nodes, selectedNode) : [];
  const selectedPeerCandidates = selectedPeerNodes.map(diagramNodeCandidate);
  const selectedParentCandidateIds = selectedNode ? parentCandidateIds(document, selectedNode.id).filter((id) => selectedPeerNodes.some((node) => node.id === id)) : [];
  const selectedNodeChildIds = selectedNode ? projection.nodes.filter((node) => node.parentId === selectedNode.id).map((node) => node.id) : [];
  const selectedNodeChildCount = selectedNodeChildIds.length;
  const selectedNodeAncestorIds = selectedNode ? diagramAncestorIds(document, selectedNode.id) : [];
  const selectedNodeRelationships = selectedNode ? diagramNodeRelationships(document.edges, selectedNode.id) : emptyDiagramNodeRelationships();
  const selectedDependencyCycleCandidateIds = selectedNode ? diagramDependencyReachableIds(document.edges, selectedNode.id) : [];
  const selectedDependencyCandidates = withoutCandidates(selectedPeerCandidates, selectedDependencyCycleCandidateIds);
  const selectedDependencyEditCandidates = selectedNode ? withoutCandidates(selectedDependencyCandidates, [...selectedNodeRelationships.prerequisites, ...selectedNodeRelationships.unlocks]) : [];
  const selectedOutgoingReferenceTargetIds = selectedNodeRelationships.referenceLinks.filter((link) => link.sourceId === selectedNode?.id).map((link) => link.targetId);
  const selectedReferenceEditCandidates = selectedNode ? withoutCandidates(selectedPeerCandidates, selectedOutgoingReferenceTargetIds) : [];
  const selectedProviderRelationships: DiagramProviderRelationshipModel[] = selectedNode
    ? relationshipActions.map((relationship) => {
        const relatedIds = diagramRelationshipRelatedNodeIds(document, relationship, selectedNode.id);
        return {
          candidates: withoutCandidates(selectedPeerCandidates, [...relatedIds, ...diagramRelationshipCycleCandidateIds(document, relationship, selectedNode.id)]),
          relatedIds,
          relationship,
        };
      })
    : [];
  const activeRelationshipPickMode = relationshipPickMode?.nodeId === activeSelectedNodeId ? relationshipPickMode : null;
  const relationshipPickCandidateIds = activeRelationshipPickMode?.relationship ? new Set(selectedProviderRelationships.find((model) => model.relationship.kind === activeRelationshipPickMode.relationship?.kind)?.candidates.map((candidate) => candidate.id) ?? []) : activeRelationshipPickMode?.kind === "dependency" || activeRelationshipPickMode?.kind === "unlock" ? new Set(selectedDependencyEditCandidates.map((candidate) => candidate.id)) : activeRelationshipPickMode?.kind === "reference" ? new Set(selectedReferenceEditCandidates.map((candidate) => candidate.id)) : null;
  const diagramCanvasKeyShortcuts = [DIAGRAM_CANVAS_KEYSHORTCUTS, onDiagramUndo && diagramCanUndo && !diagramApplyBusy ? DIAGRAM_CANVAS_UNDO_KEYSHORTCUTS : "", onDiagramRedo && diagramCanRedo && !diagramApplyBusy ? DIAGRAM_CANVAS_REDO_KEYSHORTCUTS : "", onDiagramApply && diagramApplyCommand !== "none" ? DIAGRAM_CANVAS_APPLY_KEYSHORTCUTS : ""].filter(Boolean).join(" ");
  const selectedNodeDragHintLabels =
    selectedNode && selectedNodePositionEditable
      ? diagramDragHintLabels(
          {
            activeMoveMode: activeSelectedMoveModeId,
            canMoveKeepingDescendants: Boolean(onNodeMoveKeepingDescendants),
            canMoveNode: Boolean(onNodeMove),
            canMoveRelayoutDescendants: Boolean(onNodeMoveRelayoutDescendants),
            canMoveSubtree: Boolean(onNodeMoveSubtree),
          },
          t,
        )
      : [];
  const gridId = `project-diagram-grid-${slug(title)}`;
  const gridPatternSizePx = diagramGridPatternSizePx(document);
  const focusTreeDiagram = document.nodes.some(isDiagramFocusNode);
  const diagramPanelClassName = ["project-diagram-panel", focusTreeDiagram ? "focus-tree-diagram" : ""].filter(Boolean).join(" ");
  const handleNodeActivateFromPointer = (event: PointerEvent<SVGGElement>, nodeId: DiagramNodeId): boolean => {
    const result = diagramNodeClickAction({
      eventDetail: event.detail,
      hasOpen: Boolean(onNodeOpen),
      lastClickAt: lastNodeClick?.nodeId === nodeId ? lastNodeClick.at : 0,
      now: event.timeStamp || performance.now(),
    });
    setLastNodeClick(result.lastClickAt > 0 ? { at: result.lastClickAt, nodeId } : null);
    onNodeSelect?.(nodeId);
    if (result.action === "open") {
      onNodeOpen?.(nodeId);
      return true;
    }
    return false;
  };
  const handleNodeModeCycle = (nodeId: DiagramNodeId) => {
    const node = projection.nodes.find((candidate) => candidate.id === nodeId);
    if (!node) {
      return;
    }
    if (node.mode === "relative") {
      onNodePin?.(nodeId);
      return;
    }
    if (node.mode === "absolute") {
      onNodeAutoLayout?.(nodeId);
      return;
    }
    if (node.parentId) {
      onNodeMakeRelative?.(nodeId);
      return;
    }
    onNodePin?.(nodeId);
  };
  const nodeModeCycleAvailable = Boolean(onNodePin || onNodeAutoLayout || onNodeMakeRelative);
  const handleNodeDragStart = (event: PointerEvent<SVGGElement>, nodeId: DiagramNodeId) => {
    if (!diagramNodeDragStartAllowed(event.button)) {
      return;
    }
    if (!onNodeMove && !onNodeMoveKeepingDescendants && !onNodeMoveRelayoutDescendants && !onNodeMoveSubtree) {
      return;
    }
    const node = projection.nodes.find((candidate) => candidate.id === nodeId);
    if (!node || !diagramNodePositionEditable(node.payload)) {
      return;
    }
    const start = pointerEventToSvgPoint(event);
    if (!start) {
      return;
    }
    event.preventDefault();
    onNodeSelect?.(nodeId);
    event.currentTarget.setPointerCapture(event.pointerId);
    setDragState({
      command: diagramDragMoveCommand(event.shiftKey, event.altKey, event.metaKey, event.ctrlKey, activeMoveModeIdForNode(nodeId)),
      current: start,
      nodeId,
      pointerId: event.pointerId,
      start,
    });
  };
  const handleNodeDragMove = (event: PointerEvent<SVGGElement>, nodeId: DiagramNodeId) => {
    if (!dragState || dragState.nodeId !== nodeId || dragState.pointerId !== event.pointerId) {
      return;
    }
    const current = pointerEventToSvgPoint(event);
    if (!current) {
      return;
    }
    event.preventDefault();
    setDragState((state) =>
      state && state.nodeId === nodeId && state.pointerId === event.pointerId
        ? {
            ...state,
            command: diagramDragMoveCommand(event.shiftKey, event.altKey, event.metaKey, event.ctrlKey, activeMoveModeIdForNode(nodeId)),
            current,
          }
        : state,
    );
  };
  const handleNodeDragEnd = (event: PointerEvent<SVGGElement>, nodeId: DiagramNodeId) => {
    if (!dragState || dragState.nodeId !== nodeId || dragState.pointerId !== event.pointerId) {
      return;
    }
    const current = pointerEventToSvgPoint(event) ?? dragState.current;
    const delta = dragDeltaToGrid(dragState.start, current, document.gridSizePx);
    event.preventDefault();
    releasePointerCapture(event);
    setDragState(null);
    if (delta.dx === 0 && delta.dy === 0) {
      handleNodeActivateFromPointer(event, nodeId);
      return;
    }
    const command = diagramDragMoveCommand(event.shiftKey, event.altKey, event.metaKey, event.ctrlKey, activeMoveModeIdForNode(nodeId));
    const move = command === "subtree" ? onNodeMoveSubtree : command === "relayout-descendants" ? onNodeMoveRelayoutDescendants : command === "fixed-descendants" ? onNodeMoveKeepingDescendants : onNodeMove;
    move?.(nodeId, delta);
  };
  const handleNodeDragCancel = (event: PointerEvent<SVGGElement>, nodeId: DiagramNodeId) => {
    if (!dragState || dragState.nodeId !== nodeId || dragState.pointerId !== event.pointerId) {
      return;
    }
    event.preventDefault();
    releasePointerCapture(event);
    setDragState(null);
  };
  const handleNodeHoverMove = (event: PointerEvent<SVGGElement>, nodeId: DiagramNodeId) => {
    const rect = canvasRef.current?.getBoundingClientRect();
    if (!rect) {
      return;
    }
    const cardWidth = 260;
    const cardHeight = 170;
    const left = clampNumber(event.clientX - rect.left + 12, 8, Math.max(8, rect.width - cardWidth - 8));
    const top = clampNumber(event.clientY - rect.top + 12, 8, Math.max(8, rect.height - cardHeight - 8));
    setHoverCard((current) => (current?.nodeId === nodeId && Math.abs(current.left - left) < 1 && Math.abs(current.top - top) < 1 ? current : { left, nodeId, top }));
  };
  const handleNodeHoverEnd = () => setHoverCard(null);
  const handleCanvasPanStart = <T extends SVGElement>(event: PointerEvent<T>) => {
    if (
      !diagramCanvasPanStartAllowed({
        button: event.button,
        targetIsCanvas: event.target === event.currentTarget,
      })
    ) {
      return;
    }
    const unitsPerClientPx = diagramClientScaleForViewBox(diagramViewBox, canvasSize);
    if (!unitsPerClientPx) {
      return;
    }
    event.preventDefault();
    event.currentTarget.setPointerCapture(event.pointerId);
    panDragActiveRef.current = true;
    setPanDragState({
      pointerId: event.pointerId,
      startClient: pointerEventToClientPoint(event),
      startOffset: panOffset,
      unitsPerClientPx,
    });
  };
  const handleCanvasPanMove = <T extends SVGElement>(event: PointerEvent<T>) => {
    if (!panDragState || panDragState.pointerId !== event.pointerId) {
      return;
    }
    event.preventDefault();
    setPanOffset(panOffsetForCanvasClientDrag(panDragState.startOffset, panDragState.startClient, pointerEventToClientPoint(event), panDragState.unitsPerClientPx));
  };
  const handleCanvasPanEnd = <T extends SVGElement>(event: PointerEvent<T>) => {
    if (!panDragState || panDragState.pointerId !== event.pointerId) {
      return;
    }
    applyDiagramViewportState(zoomIndex, panOffsetForCanvasClientDrag(panDragState.startOffset, panDragState.startClient, pointerEventToClientPoint(event), panDragState.unitsPerClientPx));
    event.preventDefault();
    releasePointerCapture(event);
    panDragActiveRef.current = false;
    setPanDragState(null);
  };
  const handleCanvasPanCancel = <T extends SVGElement>(event: PointerEvent<T>) => {
    if (!panDragState || panDragState.pointerId !== event.pointerId) {
      return;
    }
    event.preventDefault();
    releasePointerCapture(event);
    panDragActiveRef.current = false;
    setPanDragState(null);
  };
  const handleDiagramKeyDown = (event: KeyboardEvent<SVGSVGElement>) => {
    if (event.target !== event.currentTarget) {
      return;
    }
    const editCommand = diagramCanvasEditCommand(event.key, event.metaKey, event.ctrlKey, event.shiftKey);
    if (editCommand) {
      let run: (() => void) | undefined;
      if (editCommand.kind === "undo" && diagramCanUndo && !diagramApplyBusy) {
        run = onDiagramUndo;
      }
      if (editCommand.kind === "redo" && diagramCanRedo && !diagramApplyBusy) {
        run = onDiagramRedo;
      }
      if (editCommand.kind === "apply" && diagramApplyCommand !== "none") {
        run = handleDiagramApplyAction;
      }
      event.preventDefault();
      if (run) {
        run();
      }
      return;
    }
    const shortcut = diagramKeyboardShortcut(event.key, panStep);
    if (shortcut.kind === "none") {
      return;
    }
    event.preventDefault();
    if (shortcut.kind === "pan") {
      applyDiagramViewportState(zoomIndex, {
        x: panOffset.x + shortcut.delta.x,
        y: panOffset.y + shortcut.delta.y,
      });
      return;
    }
    if (shortcut.kind === "zoom") {
      applyDiagramViewportState(diagramZoomIndexAfterDelta(zoomIndex, shortcut.delta), panOffset);
      return;
    }
    applyDiagramViewportState(DEFAULT_DIAGRAM_ZOOM_INDEX, { x: 0, y: 0 });
  };
  const handleNodeSearchChange = (query: string) => {
    setNodeSearchQuery(query);
    const target = diagramSearchViewportTarget(projection.nodes, query, zoomedViewBox, document.gridSizePx);
    setNodeSearchIndex(target?.index ?? 0);
    if (target) {
      applyDiagramViewportState(zoomIndex, target.panOffset);
      onNodeSelect?.(target.nodeId);
    }
  };
  const handleNodeSearchNavigate = (direction: -1 | 1) => {
    if (nodeSearchMatches.length === 0) {
      return;
    }
    const nextIndex = wrapIndex(activeNodeSearchIndex + direction, nodeSearchMatches.length);
    const node = nodeSearchMatches[nextIndex];
    setNodeSearchIndex(nextIndex);
    applyDiagramViewportState(zoomIndex, panOffsetToCenterNode(zoomedViewBox, node, document.gridSizePx));
    onNodeSelect?.(node.id);
  };
  const handleRelationshipPickStart = (kind: DiagramRelationshipPickKind) => {
    if (!selectedNode) {
      return;
    }
    setRelationshipPickMode((current) => (current?.kind === kind && current.nodeId === selectedNode.id ? null : { kind, nodeId: selectedNode.id }));
  };
  const handleProviderRelationshipPickStart = (relationship: ProjectDiagramRelationship) => {
    if (!selectedNode) {
      return;
    }
    setRelationshipPickMode((current) =>
      current?.relationship?.kind === relationship.kind && current.nodeId === selectedNode.id
        ? null
        : {
            kind: "reference",
            nodeId: selectedNode.id,
            relationship,
          },
    );
  };
  const handleDiagramNodeSelect = (nodeId: DiagramNodeId) => {
    if (!activeRelationshipPickMode || !relationshipPickCandidateIds?.has(nodeId)) {
      setRelationshipPickMode(null);
      onNodeSelect?.(nodeId);
      return;
    }
    if (activeRelationshipPickMode.relationship) {
      onNodeSetRelationship?.(activeRelationshipPickMode.relationship, activeRelationshipPickMode.nodeId, nodeId, true);
      setRelationshipPickMode(null);
      return;
    }
    if (activeRelationshipPickMode.kind === "dependency") {
      onNodeAddDependency?.(activeRelationshipPickMode.nodeId, nodeId);
    }
    if (activeRelationshipPickMode.kind === "unlock") {
      onNodeAddUnlock?.(activeRelationshipPickMode.nodeId, nodeId);
    }
    if (activeRelationshipPickMode.kind === "reference") {
      onNodeAddReference?.(activeRelationshipPickMode.nodeId, nodeId);
    }
    setRelationshipPickMode(null);
  };
  const openDiagramJsonPanel = () => {
    setDiagramJsonText(exportDiagramJson(document));
    setDiagramJsonOpen(true);
  };
  const diagramMainClass = ["project-diagram-main", "pannable", panDragState ? "panning" : ""].filter(Boolean).join(" ");
  const hasSelectedNodeTools = Boolean(selectedNode && selectedNodePositionEditable && (onNodeMove || onNodeMoveKeepingDescendants || onNodeMoveRelayoutDescendants || onNodeMoveSubtree || onNodeAutoLayout || onNodeAutoLayoutDescendants || onNodeAutoLayoutSubtree || onNodeInsertChild || onNodeMakeRelative || onNodeMakeSubtreeRelative || onNodePin || onNodePinSubtree || onNodeReorderSibling || onNodeRemoveOnly || onNodeRemoveSubtree || onNodeUnpin || onNodeUnpinSubtree));

  return (
    <section className={diagramPanelClassName} data-diagram-wheel-zoom-surface="panel" ref={panelRef} aria-label={t("workspace.diagram.aria", { title })}>
      <div className="project-diagram-header">
        <div className="project-diagram-summary-row">
          <div className="project-diagram-title">
            <span>{t("workspace.diagram.title")}</span>
            <small>{readOnly ? `${diagramStats(document, t)} · ${t("workspace.diagram.readOnly")}` : diagramStats(document, t)}</small>
          </div>
          <DiagramModeSummary counts={modeCounts} t={t} />
          <DiagramEdgeSummary counts={edgeCounts} t={t} />
        </div>
        {readOnly && readOnlyReason ? (
          <p className="project-diagram-read-only-reason" role="note">
            {readOnlyReason}
          </p>
        ) : null}
        <div className="project-diagram-actions" role="toolbar" aria-label={t("workspace.diagram.title")}>
          <div className="project-diagram-action-group project-diagram-search-group">
            <DiagramSearchControls matchCount={nodeSearchMatches.length} matchIndex={activeNodeSearchIndex} nodeCount={projection.nodes.length} onNavigate={handleNodeSearchNavigate} onQueryChange={handleNodeSearchChange} query={nodeSearchQuery} t={t} />
          </div>
          <div className="project-diagram-action-group project-diagram-viewport-group">
            <DiagramZoomControls onZoomIndexChange={(updater) => applyDiagramViewportState(updater(zoomIndex), panOffset)} t={t} zoomIndex={zoomIndex} />
            <DiagramPanControls
              canCenterSelected={Boolean(selectedNode)}
              onCenterSelected={() => {
                if (selectedNode) {
                  applyDiagramViewportState(zoomIndex, panOffsetToCenterNode(zoomedViewBox, selectedNode, document.gridSizePx));
                }
              }}
              onPan={(delta) =>
                applyDiagramViewportState(zoomIndex, {
                  x: panOffset.x + delta.x,
                  y: panOffset.y + delta.y,
                })
              }
              onReset={() => applyDiagramViewportState(zoomIndex, { x: 0, y: 0 })}
              panOffset={panOffset}
              step={panStep}
              t={t}
            />
            <button
              aria-label={t("workspace.diagram.fitView")}
              className="toolbar-button icon-only project-diagram-fit-view"
              onClick={() => {
                applyDiagramViewportState(DEFAULT_DIAGRAM_ZOOM_INDEX, {
                  x: 0,
                  y: 0,
                });
              }}
              title={t("workspace.diagram.fitView")}
              type="button"
            >
              <Crosshair aria-hidden="true" size={13} />
            </button>
          </div>
          <div className="project-diagram-action-group project-diagram-file-group">
            <button aria-label={t("workspace.diagram.exportJson")} className="toolbar-button project-diagram-json-toggle project-diagram-json-export" onClick={openDiagramJsonPanel} title={t("workspace.diagram.exportJson")} type="button">
              <Download aria-hidden="true" size={13} />
              {t("workspace.diagram.exportJson")}
            </button>
            {onDiagramImportJson ? (
              <button aria-label={t("workspace.diagram.importJson")} className="toolbar-button project-diagram-json-toggle project-diagram-json-import" onClick={openDiagramJsonPanel} title={t("workspace.diagram.importJson")} type="button">
                <Upload aria-hidden="true" size={13} />
                {t("workspace.diagram.importJson")}
              </button>
            ) : null}
            {onDiagramUndo ? (
              <button aria-label={t("workspace.diagram.undo")} className="toolbar-button icon-only project-diagram-undo" disabled={diagramApplyBusy || !diagramCanUndo} onClick={onDiagramUndo} title={t("workspace.diagram.undo")} type="button">
                <RotateCcw aria-hidden="true" size={13} />
              </button>
            ) : null}
            {onDiagramRedo ? (
              <button aria-label={t("workspace.diagram.redo")} className="toolbar-button icon-only project-diagram-redo" disabled={diagramApplyBusy || !diagramCanRedo} onClick={onDiagramRedo} title={t("workspace.diagram.redo")} type="button">
                <RefreshCw aria-hidden="true" size={13} />
              </button>
            ) : null}
          </div>
          <div className="project-diagram-action-group project-diagram-layout-group">
            {onDiagramPinAll ? (
              <button aria-label={t("workspace.diagram.pinAll")} className="toolbar-button project-diagram-pin-all" disabled={diagramApplyBusy || !canPinDiagram} onClick={onDiagramPinAll} title={t("workspace.diagram.pinAll")} type="button">
                <Pin aria-hidden="true" size={13} />
                {t("workspace.diagram.pinAll")}
              </button>
            ) : null}
            {onDiagramUnpinAll ? (
              <button aria-label={t("workspace.diagram.unpinAll")} className="toolbar-button project-diagram-unpin-all" disabled={diagramApplyBusy || !canAutoLayoutDiagram} onClick={onDiagramUnpinAll} title={t("workspace.diagram.unpinAll")} type="button">
                <RotateCcw aria-hidden="true" size={13} />
                {t("workspace.diagram.unpinAll")}
              </button>
            ) : null}
            {onDiagramAutoLayout ? (
              <button aria-label={t("workspace.diagram.autoLayoutAll")} className="toolbar-button project-diagram-auto-layout-all" disabled={diagramApplyBusy || !canAutoLayoutDiagram} onClick={onDiagramAutoLayout} title={t("workspace.diagram.autoLayoutAll")} type="button">
                <RefreshCw aria-hidden="true" size={13} />
                {t("workspace.diagram.autoLayoutAll")}
              </button>
            ) : null}
            {onDiagramCreateNode && createNodeLabel ? (
              <button aria-label={createNodeLabel} className="toolbar-button project-diagram-add-node" disabled={diagramApplyBusy} onClick={onDiagramCreateNode} title={createNodeLabel} type="button">
                <Plus aria-hidden="true" size={13} />
                {createNodeLabel}
              </button>
            ) : null}
            {onDiagramInsertRoot && canInsertRootFocus ? (
              <button aria-label={t("workspace.diagram.addRootFocus")} className="toolbar-button project-diagram-insert-root" disabled={diagramApplyBusy} onClick={onDiagramInsertRoot} title={t("workspace.diagram.addRootFocus")} type="button">
                <Plus aria-hidden="true" size={13} />
                {t("workspace.diagram.addRootFocus")}
              </button>
            ) : null}
          </div>
          <div className="project-diagram-action-group project-diagram-status-group">
            {nodeImageLoadStatus ? (
              <small aria-busy={activeNodeImageLoadState.status === "loading"} aria-live="polite" className={nodeImageLoadStatusClassName} title={nodeImageLoadStatusTitle}>
                {nodeImageLoadStatus}
              </small>
            ) : null}
            {diagramDirty && diagramChangedRows.length > 0 ? <DiagramDirtyScope entities={diagramChangedRows} t={t} /> : null}
            {diagramApplyError ? <small className="project-diagram-error">{diagramApplyError}</small> : null}
            {diagramDirty && diagramApplyUnavailable ? <small className="project-diagram-warning">{diagramApplyUnavailableReason}</small> : null}
            {showDiagramApplyPreview && diagramApplyPreview ? (
              <small className="project-diagram-apply-preview" title={diagramApplyPreview.title}>
                {diagramApplyPreview.text}
              </small>
            ) : null}
            {diagramDirty && onDiagramApply ? (
              <button className="toolbar-button primary project-diagram-apply" disabled={diagramApplyCommand === "none"} onClick={handleDiagramApplyAction} title={diagramApplyTitle} type="button">
                <Save aria-hidden="true" size={13} />
                {diagramApplyButtonText}
              </button>
            ) : null}
            {diagramDirty && onDiagramDiscard ? (
              <button className="toolbar-button project-diagram-discard" disabled={diagramApplyBusy} onClick={onDiagramDiscard} type="button">
                <RotateCcw aria-hidden="true" size={13} />
                {t("workspace.diagram.discard")}
              </button>
            ) : null}
          </div>
          {hasSelectedNodeTools && selectedNode ? (
            <div className="project-diagram-action-group project-diagram-node-tools">
              <DiagramNudgeControls nodeId={selectedNode.id} onNodeAutoLayout={onNodeAutoLayout} onNodeAutoLayoutDescendants={onNodeAutoLayoutDescendants} onNodeAutoLayoutSubtree={onNodeAutoLayoutSubtree} canAutoLayoutSelectedDescendants={selectedDescendantsCanAutoLayout} canAutoLayoutSelectedNode={selectedNodeCanAutoLayout} canAutoLayoutSelectedSubtree={selectedSubtreeCanAutoLayout} canMakeRelativeSelectedNode={selectedNodeCanMakeRelative} canMakeRelativeSelectedSubtree={selectedSubtreeCanMakeRelative} canInsertSelectedChild={selectedNodeCanInsertChild} canMoveSelectedRelayoutDescendants={selectedNodeHasDescendants} canPinSelectedNode={selectedNodeCanPin} canPinSelectedSubtree={selectedSubtreeCanPin} canReorderSiblingEarlier={selectedNodeSiblingReorderState.canReorderEarlier} canReorderSiblingLater={selectedNodeSiblingReorderState.canReorderLater} canRemoveSelectedNodeOnly={selectedNodeCanRemoveOnly} canRemoveSelectedSubtree={selectedSubtreeCanRemove} onNodeMove={onNodeMove} onNodeInsertChild={onNodeInsertChild} onNodeMoveKeepingDescendants={onNodeMoveKeepingDescendants} onNodeMoveRelayoutDescendants={onNodeMoveRelayoutDescendants} onNodeMoveSubtree={onNodeMoveSubtree} onNodeMakeRelative={onNodeMakeRelative} onNodeMakeSubtreeRelative={onNodeMakeSubtreeRelative} onSelectedMoveModeChange={setSelectedMoveMode} moveImpactNodeCount={activeSelectedMoveModeAffectedCount} onNodePin={onNodePin} onNodePinSubtree={onNodePinSubtree} onNodeReorderSibling={onNodeReorderSibling} onNodeRemoveOnly={onNodeRemoveOnly} onNodeRemoveSubtree={onNodeRemoveSubtree} onNodeUnpin={onNodeUnpin} onNodeUnpinSubtree={onNodeUnpinSubtree} selectedMoveMode={selectedMoveMode} t={t} />
            </div>
          ) : null}
        </div>
      </div>
      {showDiagramApplyPreview && diagramApplyPreview ? <DiagramApplyReview preview={diagramApplyPreview} t={t} /> : null}
      {diagramJsonOpen ? (
        <form
          aria-label={t("workspace.diagram.jsonPanel")}
          className="project-diagram-json-panel"
          onSubmit={(event) => {
            event.preventDefault();
            onDiagramImportJson?.(diagramJsonText);
          }}
        >
          <div className="project-diagram-json-panel-header">
            <strong>{t("workspace.diagram.jsonPanel")}</strong>
            <button className="toolbar-button icon-only" onClick={() => setDiagramJsonOpen(false)} title={t("workspace.diagram.closeJson")} type="button">
              <RotateCcw aria-hidden="true" size={13} />
            </button>
          </div>
          <textarea aria-label={t("workspace.diagram.jsonText")} onChange={(event) => setDiagramJsonText(event.currentTarget.value)} spellCheck={false} value={diagramJsonText} />
          <div className="project-diagram-json-actions">
            <button className="toolbar-button" onClick={() => setDiagramJsonText(exportDiagramJson(document))} type="button">
              <Download aria-hidden="true" size={13} />
              {t("workspace.diagram.exportJson")}
            </button>
            {onDiagramImportJson ? (
              <button className="toolbar-button primary" type="submit">
                <Upload aria-hidden="true" size={13} />
                {t("workspace.diagram.importJson")}
              </button>
            ) : null}
          </div>
        </form>
      ) : null}
      <div className="project-diagram-workspace">
        <div className="project-diagram-canvas" ref={canvasRef}>
          <svg aria-keyshortcuts={diagramCanvasKeyShortcuts} className={diagramMainClass} ref={svgRef} role="img" tabIndex={0} viewBox={diagramViewBox} aria-label={t("workspace.diagram.aria", { title })} onKeyDown={handleDiagramKeyDown} onPointerCancel={handleCanvasPanCancel} onPointerDown={handleCanvasPanStart} onPointerMove={handleCanvasPanMove} onPointerUp={handleCanvasPanEnd}>
            <defs>
              <pattern id={gridId} width={gridPatternSizePx} height={gridPatternSizePx} patternUnits="userSpaceOnUse">
                <path className="project-diagram-grid-line" d={`M ${gridPatternSizePx} 0 L 0 0 0 ${gridPatternSizePx}`} />
              </pattern>
            </defs>
            {diagramPanSurface ? <rect className="project-diagram-grid-bg" x={diagramPanSurface.x} y={diagramPanSurface.y} width={diagramPanSurface.width} height={diagramPanSurface.height} fill={`url(#${gridId})`} /> : null}
            {diagramPanSurface ? <rect className="project-diagram-pan-surface" x={diagramPanSurface.x} y={diagramPanSurface.y} width={diagramPanSurface.width} height={diagramPanSurface.height} onPointerCancel={handleCanvasPanCancel} onPointerDown={handleCanvasPanStart} onPointerMove={handleCanvasPanMove} onPointerUp={handleCanvasPanEnd} /> : null}
            <g className="project-diagram-edges">
              {projection.edges.map((edge) => (
                <path className={diagramEdgeClassName(edge, activeSelectedNodeId, dragPreviewIds, selectedBranchNodeIds, activeSelectedMoveAffectedIds)} d={edge.path} data-edge-id={edge.id} data-relationship-kind={edge.relationshipKind} key={edge.id}>
                  {edge.label ? <title>{edge.label}</title> : null}
                </path>
              ))}
            </g>
            <g className="project-diagram-nodes">
              {projection.nodes.map((node) => {
                const dragOffset = dragPreviewOffset && dragPreviewIds?.has(node.id) ? dragPreviewOffset : undefined;
                const dragGridDelta = dragPreviewGridDelta && dragPreviewIds?.has(node.id) && dragState?.command !== "relayout-descendants" ? dragPreviewGridDelta : undefined;
                const dragging = Boolean(dragPreviewIds?.has(node.id));
                const positionEditable = diagramNodePositionEditable(node.payload);
                return <DiagramNodeBox branchMember={Boolean(selectedDescendantNodeIds?.has(node.id))} dragGridDelta={dragGridDelta} dragOffset={dragOffset} draggable={positionEditable && Boolean(onNodeMove || onNodeMoveKeepingDescendants || onNodeMoveRelayoutDescendants || onNodeMoveSubtree)} dragging={dragging} gridSize={document.gridSizePx} hasImage={Boolean(node.imageUrl)} imageUrl={nodeImageHref(node, nodeImageUrls, projectRoot)} key={node.id} lastClickAt={lastNodeClick?.nodeId === node.id ? lastNodeClick.at : 0} moveMode={activeMoveModeIdForNode(node.id)} moveAffected={Boolean(activeSelectedMoveAffectedIds?.has(node.id))} node={node} onDragCancel={handleNodeDragCancel} onDragEnd={handleNodeDragEnd} onDragMove={handleNodeDragMove} onDragStart={handleNodeDragStart} onHoverEnd={handleNodeHoverEnd} onHoverMove={handleNodeHoverMove} onMove={positionEditable ? onNodeMove : undefined} onMoveKeepingDescendants={positionEditable ? onNodeMoveKeepingDescendants : undefined} onMoveRelayoutDescendants={positionEditable ? onNodeMoveRelayoutDescendants : undefined} onMoveSubtree={positionEditable ? onNodeMoveSubtree : undefined} onModeCycle={focusTreeDiagram && nodeModeCycleAvailable && node.id === activeSelectedNodeId ? handleNodeModeCycle : undefined} onNodeClickAtChange={(at) => setLastNodeClick(at > 0 ? { at, nodeId: node.id } : null)} onOpen={onNodeOpen} onRemoveOnly={onNodeRemoveOnly} onRemoveSubtree={onNodeRemoveSubtree} onSelect={handleDiagramNodeSelect} relationshipPickCandidate={Boolean(relationshipPickCandidateIds?.has(node.id))} relationshipPickSource={Boolean(activeRelationshipPickMode && node.id === activeRelationshipPickMode.nodeId)} searchCurrent={node.id === currentNodeSearchMatchId} searchMatch={nodeSearchMatchIds.has(node.id)} selected={node.id === activeSelectedNodeId} t={t} />;
              })}
            </g>
          </svg>
          {hoveredNode && hoverCard ? <DiagramNodeHoverCard left={hoverCard.left} node={hoveredNode} t={t} top={hoverCard.top} /> : null}
          <DiagramMiniMap currentSearchMatchId={currentNodeSearchMatchId} gridSize={document.gridSizePx} nodes={projection.nodes} moveAffectedIds={activeSelectedMoveAffectedIds} onTargetPoint={(point) => applyDiagramViewportState(zoomIndex, panOffsetToCenterPoint(zoomedViewBox, point))} selectedNodeId={activeSelectedNodeId} searchMatchIds={nodeSearchMatchIds} t={t} viewBox={fittedViewBox} viewportViewBox={diagramViewBox} />
          {openedNode ? <DiagramNodeInfoPopover node={openedNode} onClose={onNodeInfoClose} onOpenModule={onNodeOpenModule ? (sourcePath) => onNodeOpenModule(openedNode.id, sourcePath) : undefined} t={t} /> : null}
        </div>
        {selectedNode ? <DiagramSelectionSummary childCount={selectedNodeChildCount} childIds={selectedNodeChildIds} ancestorIds={selectedNodeAncestorIds} changedEntity={selectedChangedEntity} dependencyCandidates={selectedDependencyEditCandidates} dragHintLabels={selectedNodeDragHintLabels} moveFootprint={activeSelectedMoveFootprint} node={selectedNode} nodeCandidateById={nodeCandidateById} onMoveFootprintCenter={centerSelectedMoveFootprint} onNodeAddDependency={onNodeAddDependency} onNodeAddReference={onNodeAddReference} onNodeAddUnlock={onNodeAddUnlock} onNodeClearParent={onNodeClearParent} onNodeMakeRelative={onNodeMakeRelative} onNodePin={onNodePin} onNodeRemoveDependency={onNodeRemoveDependency} onNodeRemoveReference={onNodeRemoveReference} onNodeRemoveUnlock={onNodeRemoveUnlock} onNodeSelect={onNodeSelect} onNodeSetPosition={onNodeSetPosition} onNodeSetLayoutHints={onNodeSetLayoutHints} onNodeSetParent={onNodeSetParent} onNodeSetRelationship={onNodeSetRelationship} onNodeUnpin={onNodeUnpin} onProviderRelationshipPickStart={handleProviderRelationshipPickStart} onRelationshipPickStart={handleRelationshipPickStart} parentCandidates={candidatesByIds(selectedParentCandidateIds, nodeCandidateById)} referenceCandidates={selectedReferenceEditCandidates} relationshipPickMode={activeRelationshipPickMode} relationships={selectedNodeRelationships} providerRelationships={selectedProviderRelationships} siblingCount={selectedNodeSiblingReorderState.siblingCount} siblingIds={selectedNodeSiblingReorderState.siblingIds} siblingIndex={selectedNodeSiblingReorderState.siblingIndex} subtreeCount={selectedSubtreeNodes.length} subtreeDescendantCount={selectedDescendantNodes.length} t={t} /> : null}
      </div>
    </section>
  );
}

function DiagramModeSummary({ counts, t }: { counts: DiagramModeCounts; t: Translator }) {
  return (
    <div className="project-diagram-mode-summary">
      <span>
        {modeLabel("absolute", t)} {counts.absolute}
      </span>
      <span>
        {modeLabel("relative", t)} {counts.relative}
      </span>
      <span>
        {modeLabel("auto", t)} {counts.auto}
      </span>
    </div>
  );
}

function DiagramEdgeSummary({ counts, t }: { counts: DiagramEdgeCounts; t: Translator }) {
  return (
    <div className="project-diagram-edge-summary" aria-label={t("workspace.diagram.edgeSummary")}>
      {(["tree", "dependency", "path", "reference"] as const).map((kind) => (
        <span className={`project-diagram-edge-summary-item ${kind}`} key={kind}>
          <i aria-hidden="true" />
          {edgeKindLabel(kind, t)} {counts[kind]}
        </span>
      ))}
    </div>
  );
}

function diagramApplyPreviewForEntities(entities: DiagramChangedEntity[] | undefined, t: Translator): DiagramApplyPreview | null {
  if (!entities || entities.length === 0) {
    return null;
  }
  const writableEntities = entities.filter(diagramChangedEntityCanWrite);
  const skippedEntities = entities.filter((entity) => !diagramChangedEntityCanWrite(entity));
  return {
    rows: [
      ...writableEntities.map((entity) => ({
        entity,
        status: "write" as const,
      })),
      ...skippedEntities.map((entity) => ({ entity, status: "skip" as const })),
    ],
    text: t("workspace.diagram.applyPreview", {
      skipped: String(skippedEntities.length),
      writable: String(writableEntities.length),
    }),
    title: [
      ...writableEntities.map((entity) =>
        t("workspace.diagram.applyPreviewWrite", {
          entity: diagramApplyPreviewEntityLabel(entity),
        }),
      ),
      ...skippedEntities.map((entity) =>
        t("workspace.diagram.applyPreviewSkip", {
          entity: diagramApplyPreviewEntityLabel(entity),
        }),
      ),
    ].join("; "),
  };
}

function diagramApplyPreviewEntityLabel(entity: DiagramChangedEntity): string {
  return [entity.id, entity.path ?? entity.title].filter(Boolean).join(" ");
}

function diagramChangedEntityCanWrite(entity: DiagramChangedEntity): boolean {
  return Boolean(entity.path) && !entity.draftUnavailable;
}

function DiagramChangedEntityPath({ entity, t }: { entity: DiagramChangedEntity; t: Translator }) {
  return (
    <>
      {entity.path ? <small>{entity.path}</small> : null}
      {entity.draftUnavailable ? <small className="project-diagram-dirty-missing">{t("workspace.diagram.dirtyDraftUnavailable")}</small> : !entity.path ? <small className="project-diagram-dirty-missing">{t("workspace.diagram.dirtyMissingPath")}</small> : null}
    </>
  );
}

function DiagramApplyReview({ preview, t }: { preview: DiagramApplyPreview; t: Translator }) {
  return (
    <details className="project-diagram-apply-review" open>
      <summary>
        <span>{t("workspace.diagram.applyReview")}</span>
        <small>{preview.text}</small>
      </summary>
      <ul aria-label={t("workspace.diagram.applyReviewAria")} className="project-diagram-apply-review-list">
        {preview.rows.map(({ entity, status }, index) => (
          <li key={`${status}:${diagramChangedEntityKey(entity, index)}`}>
            <span className={`project-diagram-apply-review-status ${status}`}>{status === "write" ? t("workspace.diagram.applyReviewWrite") : t("workspace.diagram.applyReviewSkip")}</span>
            <code>{entity.id}</code>
            {entity.title && entity.title !== entity.id ? <span>{entity.title}</span> : null}
            <DiagramChangedEntityPath entity={entity} t={t} />
            {entity.draftText ? (
              <details className="project-diagram-apply-review-draft">
                <summary>{t("workspace.diagram.applyReviewDraft")}</summary>
                <pre>{entity.draftText}</pre>
              </details>
            ) : null}
          </li>
        ))}
      </ul>
    </details>
  );
}

function DiagramDirtyScope({ entities, t }: { entities: DiagramChangedEntity[]; t: Translator }) {
  const title = entities.map((entity) => [entity.id, entity.path].filter(Boolean).join(" ")).join(", ");
  const writableCount = entities.filter(diagramChangedEntityCanWrite).length;
  const skippedCount = entities.length - writableCount;
  const summary = t("workspace.diagram.dirtySummaryMixed", {
    count: String(entities.length),
    skipped: String(skippedCount),
    writable: String(writableCount),
  });
  return (
    <details className="project-diagram-dirty-scope">
      <summary className="project-diagram-dirty-summary" title={title}>
        {summary}
      </summary>
      <ul aria-label={t("workspace.diagram.dirtyScope")} className="project-diagram-dirty-list">
        {entities.map((entity, index) => (
          <li key={diagramChangedEntityKey(entity, index)}>
            <code>{entity.id}</code>
            {entity.title && entity.title !== entity.id ? <span>{entity.title}</span> : null}
            <DiagramChangedEntityPath entity={entity} t={t} />
          </li>
        ))}
      </ul>
    </details>
  );
}

function diagramChangedEntityKey(entity: DiagramChangedEntity, index: number): string {
  return `${entity.id}\0${entity.path ?? ""}\0${index}`;
}

function DiagramNodeInfoPopover({ node, onClose, onOpenModule, t }: { node: ResolvedDiagramNode; onClose?: () => void; onOpenModule?: (sourcePath: string) => void; t: Translator }) {
  const facts = diagramSelectionFacts(node, t);
  const editableSourcePath = diagramNodeEditableSourcePath(node.payload);
  return (
    <aside className="project-diagram-node-info-popover" aria-label={t("workspace.diagram.openedNodeInfo")}>
      <header>
        <div>
          <span>{t("workspace.diagram.openedNodeInfo")}</span>
          <strong>{node.title ?? node.id}</strong>
        </div>
        {onOpenModule || onClose ? (
          <div className="project-diagram-node-info-actions">
            {onOpenModule ? (
              <button className="toolbar-button project-diagram-node-open-module" onClick={() => onOpenModule(editableSourcePath)} title={t("workspace.diagram.openNodeModule")} type="button">
                <PanelTopOpen aria-hidden="true" size={13} />
                {t("workspace.diagram.openNodeModule")}
              </button>
            ) : null}
            {onClose ? (
              <button aria-label={t("workspace.diagram.closeNodeInfo")} className="toolbar-button icon-only" onClick={onClose} title={t("workspace.diagram.closeNodeInfo")} type="button">
                <X aria-hidden="true" size={13} />
              </button>
            ) : null}
          </div>
        ) : null}
      </header>
      <code>{node.id}</code>
      <dl>
        <div>
          <dt>{t("workspace.diagram.openedNodeGrid")}</dt>
          <dd>
            {formatViewBoxNumber(node.worldX)}, {formatViewBoxNumber(node.worldY)}
          </dd>
        </div>
        {facts.map((fact) => (
          <div key={`${fact.label}:${fact.value}`}>
            <dt>{fact.label}</dt>
            <dd>{fact.value}</dd>
          </div>
        ))}
      </dl>
      {editableSourcePath ? (
        <p className="project-diagram-node-info-source" title={editableSourcePath}>
          <span>{t("workspace.diagram.openedNodeSourceInfo")}</span>
          <code>{editableSourcePath}</code>
        </p>
      ) : null}
    </aside>
  );
}

function DiagramSelectionSummary({ ancestorIds, changedEntity, childCount, childIds, dependencyCandidates, dragHintLabels, moveFootprint, node, nodeCandidateById, onMoveFootprintCenter, onNodeAddDependency, onNodeAddReference, onNodeAddUnlock, onNodeClearParent, onNodeMakeRelative, onNodePin, onNodeRemoveDependency, onNodeRemoveReference, onNodeRemoveUnlock, onNodeSelect, onNodeSetLayoutHints, onNodeSetPosition, onNodeSetParent, onNodeSetRelationship, onNodeUnpin, onProviderRelationshipPickStart, onRelationshipPickStart, parentCandidates, referenceCandidates, relationshipPickMode, relationships, providerRelationships, siblingCount, siblingIds, siblingIndex, subtreeCount, subtreeDescendantCount, t }: { ancestorIds: string[]; changedEntity: DiagramChangedEntity | null; childCount: number; childIds: string[]; dependencyCandidates: DiagramCandidate[]; dragHintLabels: string[]; moveFootprint: DiagramMoveFootprintSummary | null; node: ResolvedDiagramNode; nodeCandidateById: Map<string, DiagramCandidate>; onMoveFootprintCenter?: () => void; onNodeAddDependency?: (targetId: string, sourceId: string) => void; onNodeAddReference?: (sourceId: string, targetId: string) => void; onNodeAddUnlock?: (sourceId: string, targetId: string) => void; onNodeClearParent?: (nodeId: string) => void; onNodeMakeRelative?: (nodeId: string) => void; onNodePin?: (nodeId: string) => void; onNodeRemoveDependency?: (targetId: string, sourceId: string) => void; onNodeRemoveReference?: (sourceId: string, targetId: string) => void; onNodeRemoveUnlock?: (sourceId: string, targetId: string) => void; onNodeSelect?: (nodeId: string) => void; onNodeSetLayoutHints?: (nodeId: string, hints: DiagramNodeLayoutHints) => void; onNodeSetPosition?: (nodeId: string, position: { x: number; y: number }) => void; onNodeSetParent?: (nodeId: string, parentId: string) => void; onNodeSetRelationship?: (relationship: ProjectDiagramRelationship, selectedNodeId: string, relatedNodeId: string, present: boolean) => void; onNodeUnpin?: (nodeId: string) => void; onProviderRelationshipPickStart?: (relationship: ProjectDiagramRelationship) => void; onRelationshipPickStart?: (kind: DiagramRelationshipPickKind) => void; parentCandidates: DiagramCandidate[]; referenceCandidates: DiagramCandidate[]; relationshipPickMode: DiagramRelationshipPickMode | null; relationships: DiagramNodeRelationships; providerRelationships: DiagramProviderRelationshipModel[]; siblingCount: number; siblingIds: string[]; siblingIndex: number; subtreeCount: number; subtreeDescendantCount: number; t: Translator }) {
  const sourcePath = diagramNodeSourcePath(node.payload);
  const facts = diagramSelectionFacts(node, t);
  const positionEditable = diagramNodePositionEditable(node.payload);
  const parentEditCandidates = withoutCandidates(parentCandidates, node.parentId ? [node.parentId] : []);
  const dependencyEditCandidates = withoutCandidates(dependencyCandidates, [...relationships.prerequisites, ...relationships.unlocks]);
  const unlockEditCandidates = dependencyEditCandidates;
  const outgoingReferenceTargetIds = relationships.referenceLinks.filter((link) => link.sourceId === node.id).map((link) => link.targetId);
  const referenceEditCandidates = withoutCandidates(referenceCandidates, outgoingReferenceTargetIds);
  const addUnlock = onNodeAddUnlock ?? (onNodeAddDependency ? (sourceId: string, targetId: string) => onNodeAddDependency(targetId, sourceId) : undefined);
  const removeUnlock = onNodeRemoveUnlock ?? (onNodeRemoveDependency ? (sourceId: string, targetId: string) => onNodeRemoveDependency(targetId, sourceId) : undefined);
  const removeReference = onNodeRemoveReference
    ? (id: string) => {
        const link = relationships.referenceLinks.find((candidate) => candidate.relatedId === id && candidate.sourceId === node.id) ?? relationships.referenceLinks.find((candidate) => candidate.relatedId === id);
        if (link) {
          onNodeRemoveReference(link.sourceId, link.targetId);
        }
      }
    : undefined;
  return (
    <aside className="project-diagram-selection" aria-label={t("workspace.diagram.selectedNode")}>
      <strong>{node.title ?? node.id}</strong>
      <code>{node.id}</code>
      <span>{modeLabel(node.mode, t)}</span>
      <span>
        {t("workspace.diagram.selectedPosition", {
          x: formatViewBoxNumber(node.worldX),
          y: formatViewBoxNumber(node.worldY),
        })}
      </span>
      {facts.length > 0 ? <DiagramSelectionFacts facts={facts} /> : null}
      {changedEntity ? <DiagramSelectedDraft entity={changedEntity} t={t} /> : null}
      <DiagramSelectedModeControls node={node} onNodeMakeRelative={positionEditable ? onNodeMakeRelative : undefined} onNodePin={positionEditable ? onNodePin : undefined} onNodeUnpin={positionEditable ? onNodeUnpin : undefined} t={t} />
      {onNodeSetPosition && positionEditable ? <DiagramSelectedPositionForm key={`${node.id}:${node.worldX}:${node.worldY}`} node={node} onNodeSetPosition={onNodeSetPosition} t={t} /> : null}
      {!positionEditable ? (
        <p className="project-diagram-selection-position-read-only" role="note">
          {t("workspace.diagram.nodePositionReadOnly")}
        </p>
      ) : null}
      {onNodeSetLayoutHints && isDiagramFocusNode(node) ? <DiagramSelectedLayoutHintsForm key={`${node.id}:layout:${node.priority ?? ""}:${node.subtreeWidth ?? ""}:${node.subtreeWidthDelta ?? ""}:${node.subtreeCenterOffset ?? ""}`} node={node} onNodeSetLayoutHints={onNodeSetLayoutHints} t={t} /> : null}
      {onNodeSetParent ? <DiagramSelectedParentForm candidates={parentEditCandidates} nodeId={node.id} onNodeSetParent={onNodeSetParent} t={t} /> : null}
      {onNodeClearParent && node.parentId ? (
        <button aria-label={t("workspace.diagram.clearParent")} className="toolbar-button project-diagram-clear-parent" onClick={() => onNodeClearParent(node.id)} type="button">
          <GitBranch aria-hidden="true" size={13} />
          {t("workspace.diagram.clearParentAction")}
        </button>
      ) : null}
      {onNodeAddDependency ? <DiagramSelectedDependencyForm candidates={dependencyEditCandidates} nodeId={node.id} onNodeAddDependency={onNodeAddDependency} onRelationshipPickStart={onRelationshipPickStart} pickActive={relationshipPickMode?.kind === "dependency"} t={t} /> : null}
      {addUnlock ? <DiagramSelectedUnlockForm candidates={unlockEditCandidates} nodeId={node.id} onNodeAddUnlock={addUnlock} onRelationshipPickStart={onRelationshipPickStart} pickActive={relationshipPickMode?.kind === "unlock"} t={t} /> : null}
      {onNodeAddReference ? <DiagramSelectedReferenceForm candidates={referenceEditCandidates} nodeId={node.id} onNodeAddReference={onNodeAddReference} onRelationshipPickStart={onRelationshipPickStart} pickActive={relationshipPickMode?.kind === "reference"} t={t} /> : null}
      {onNodeSetRelationship ? providerRelationships.map((model) => <DiagramSelectedProviderRelationshipForm candidates={model.candidates} key={model.relationship.kind} nodeId={node.id} onNodeSetRelationship={onNodeSetRelationship} onRelationshipPickStart={onProviderRelationshipPickStart} pickActive={relationshipPickMode?.relationship?.kind === model.relationship.kind} relationship={model.relationship} />) : null}
      {relationshipPickMode ? <span className="project-diagram-relationship-pick-hint">{relationshipPickMode.relationship ? `${relationshipPickMode.relationship.label}: select a highlighted node` : relationshipPickHintText(relationshipPickMode.kind, t)}</span> : null}
      {node.parentId ? (
        <DiagramSelectionRelationshipRow
          candidatesById={nodeCandidateById}
          ids={[node.parentId]}
          label={t("workspace.diagram.selectedParent", {
            parent: node.parentId,
          })}
          onNodeSelect={onNodeSelect}
          selectLabel={(id) => t("workspace.diagram.selectTreeParent", { id })}
        />
      ) : null}
      <DiagramSelectionRelationshipRow
        candidatesById={nodeCandidateById}
        ids={ancestorIds}
        label={t("workspace.diagram.selectedPath", {
          count: String(ancestorIds.length),
        })}
        onNodeSelect={onNodeSelect}
        selectLabel={(id) => t("workspace.diagram.selectAncestor", { id })}
      />
      {siblingCount > 1 && siblingIndex >= 0 ? (
        <span className="project-diagram-selection-sibling">
          {t("workspace.diagram.selectedSiblingOrder", {
            count: String(siblingCount),
            index: String(siblingIndex + 1),
          })}
        </span>
      ) : null}
      <DiagramSelectionRelationshipRow
        candidatesById={nodeCandidateById}
        ids={siblingIds}
        label={t("workspace.diagram.selectedSiblings", {
          count: String(siblingIds.length),
        })}
        onNodeSelect={onNodeSelect}
        selectLabel={(id) => t("workspace.diagram.selectSibling", { id })}
      />
      <span>{t("workspace.diagram.selectedChildren", { count: String(childCount) })}</span>
      <DiagramSelectionRelationshipRow
        candidatesById={nodeCandidateById}
        ids={childIds}
        label={t("workspace.diagram.selectedChildren", {
          count: String(childCount),
        })}
        onNodeSelect={onNodeSelect}
        selectLabel={(id) => t("workspace.diagram.selectTreeChild", { id })}
      />
      {subtreeDescendantCount > 0 ? <span className="project-diagram-selection-subtree">{diagramBranchSizeText(subtreeCount, subtreeDescendantCount, t)}</span> : null}
      {moveFootprint ? <DiagramSelectionMoveFootprint candidatesById={nodeCandidateById} footprint={moveFootprint} onCenter={onMoveFootprintCenter} onNodeSelect={onNodeSelect} t={t} /> : null}
      {dragHintLabels.length > 0 ? (
        <span className="project-diagram-selection-drag-hints" title={dragHintLabels.join(" / ")}>
          {dragHintLabels.join(" / ")}
        </span>
      ) : null}
      {providerRelationships.length === 0 ? (
        <>
          <DiagramSelectionRelationshipRow
            candidatesById={nodeCandidateById}
            ids={relationships.prerequisites}
            label={t("workspace.diagram.selectedPrerequisites", {
              ids: relationships.prerequisites.join(", "),
            })}
            onNodeSelect={onNodeSelect}
            onRemove={onNodeRemoveDependency ? (id) => onNodeRemoveDependency(node.id, id) : undefined}
            removeLabel={(id) => t("workspace.diagram.removePrerequisite", { id })}
            selectLabel={(id) => t("workspace.diagram.selectPrerequisite", { id })}
          />
          <DiagramSelectionRelationshipRow
            candidatesById={nodeCandidateById}
            ids={relationships.unlocks}
            label={t("workspace.diagram.selectedUnlocks", {
              ids: relationships.unlocks.join(", "),
            })}
            onNodeSelect={onNodeSelect}
            onRemove={removeUnlock ? (id) => removeUnlock(node.id, id) : undefined}
            removeLabel={(id) => t("workspace.diagram.removeUnlock", { id })}
            selectLabel={(id) => t("workspace.diagram.selectUnlock", { id })}
          />
          <DiagramSelectionRelationshipRow
            candidatesById={nodeCandidateById}
            ids={relationships.references}
            label={t("workspace.diagram.selectedReferences", {
              ids: relationships.references.join(", "),
            })}
            onNodeSelect={onNodeSelect}
            onRemove={removeReference}
            removeLabel={(id) => t("workspace.diagram.removeReference", { id })}
            selectLabel={(id) => t("workspace.diagram.selectReference", { id })}
          />
        </>
      ) : null}
      <DiagramSelectionExactRelationships candidatesById={nodeCandidateById} links={relationships.exactLinks.filter((link) => !providerRelationships.some((model) => model.relationship.kind === link.relationshipKind))} onNodeSelect={onNodeSelect} t={t} />
      {onNodeSetRelationship ? providerRelationships.map((model) => <DiagramSelectionRelationshipRow candidatesById={nodeCandidateById} ids={model.relatedIds} key={`provider:${model.relationship.kind}`} label={`${model.relationship.label}: ${model.relatedIds.join(", ")}`} onNodeSelect={onNodeSelect} onRemove={(id) => onNodeSetRelationship(model.relationship, node.id, id, false)} removeLabel={(id) => `Remove ${model.relationship.label} ${id}`} selectLabel={(id) => `Select ${model.relationship.label} node ${id}`} />) : null}
      {sourcePath ? (
        <span className="project-diagram-selection-source" title={sourcePath}>
          {t("workspace.diagram.selectedSource", { source: sourcePath })}
        </span>
      ) : null}
    </aside>
  );
}

function DiagramSelectionExactRelationships({ candidatesById, links, onNodeSelect, t }: { candidatesById: Map<string, DiagramCandidate>; links: DiagramExactRelationshipLink[]; onNodeSelect?: (nodeId: string) => void; t: Translator }) {
  if (links.length === 0) {
    return null;
  }
  return (
    <div className="project-diagram-selection-exact-relationships">
      <span>{t("workspace.diagram.exactRelationships")}</span>
      <ul aria-label={t("workspace.diagram.exactRelationships")}>
        {links.map((link) => {
          const candidate = candidatesById.get(link.relatedId) ?? {
            id: link.relatedId,
            title: link.relatedId,
          };
          return (
            <li key={`${link.edgeId}:${link.relatedId}`}>
              <span>{link.label || link.relationshipKind}</span>
              {onNodeSelect ? (
                <button aria-label={t("workspace.diagram.selectRelationshipEndpoint", { id: candidateDisplayText(candidate) })} onClick={() => onNodeSelect(link.relatedId)} type="button">
                  {candidate.id}
                </button>
              ) : (
                <code>{candidate.id}</code>
              )}
            </li>
          );
        })}
      </ul>
    </div>
  );
}

function DiagramSelectionMoveFootprint({ candidatesById, footprint, onCenter, onNodeSelect, t }: { candidatesById: Map<string, DiagramCandidate>; footprint: DiagramMoveFootprintSummary; onCenter?: () => void; onNodeSelect?: (nodeId: string) => void; t: Translator }) {
  const visibleIds = footprint.affectedIds.slice(0, MAX_QUICK_CANDIDATE_BUTTONS);
  const hiddenCount = Math.max(0, footprint.affectedIds.length - visibleIds.length);
  return (
    <div className="project-diagram-selection-move-footprint" title={footprint.title}>
      <span>
        <span className="project-diagram-selection-move-footprint-label">
          {t("workspace.diagram.selectedMoveFootprint")}
          <code>{footprint.label}</code>
        </span>
        {onCenter ? (
          <button aria-label={t("workspace.diagram.centerMoveFootprint")} className="toolbar-button icon-only project-diagram-center-move-footprint" onClick={onCenter} title={t("workspace.diagram.centerMoveFootprint")} type="button">
            <Crosshair aria-hidden="true" size={12} />
          </button>
        ) : null}
      </span>
      <small>
        {footprint.impact} · {footprint.hint}
      </small>
      <div className="project-diagram-selection-move-footprint-nodes">
        {visibleIds.map((id) => {
          const candidate = candidatesById.get(id) ?? { id, title: id };
          return onNodeSelect ? (
            <button
              aria-label={t("workspace.diagram.selectMoveAffected", {
                id: candidateDisplayText(candidate),
              })}
              key={id}
              onClick={() => onNodeSelect(id)}
              type="button"
            >
              {candidate.id}
            </button>
          ) : (
            <code key={id}>{candidate.id}</code>
          );
        })}
        {hiddenCount > 0 ? (
          <small>
            {t("workspace.diagram.moreMoveAffected", {
              count: String(hiddenCount),
            })}
          </small>
        ) : null}
      </div>
    </div>
  );
}

function DiagramSelectedDraft({ entity, t }: { entity: DiagramChangedEntity; t: Translator }) {
  const title = [entity.id, entity.title, entity.path].filter(Boolean).join(" ");
  return (
    <span className="project-diagram-selection-draft" title={title}>
      <span>{t("workspace.diagram.selectedDraft")}</span>
      <code>{entity.id}</code>
      {entity.path ? <small>{entity.path}</small> : <small className="project-diagram-dirty-missing">{t("workspace.diagram.dirtyMissingPath")}</small>}
    </span>
  );
}

function DiagramSelectionFacts({ facts }: { facts: DiagramSelectionFact[] }) {
  return (
    <dl className="project-diagram-selection-facts">
      {facts.map((fact) => (
        <div key={`${fact.label}:${fact.value}`}>
          <dt>{fact.label}</dt>
          <dd>{fact.value}</dd>
        </div>
      ))}
    </dl>
  );
}

function diagramBranchSizeText(subtreeCount: number, descendantCount: number, t: Translator): string {
  return t("workspace.diagram.selectedBranchSize", {
    count: String(subtreeCount),
    descendantCount: String(descendantCount),
    descendantLabel: t(descendantCount === 1 ? "workspace.diagram.selectedBranchDescendant" : "workspace.diagram.selectedBranchDescendants"),
  });
}

function DiagramSelectedModeControls({ node, onNodeMakeRelative, onNodePin, onNodeUnpin, t }: { node: ResolvedDiagramNode; onNodeMakeRelative?: (nodeId: string) => void; onNodePin?: (nodeId: string) => void; onNodeUnpin?: (nodeId: string) => void; t: Translator }) {
  if (!onNodeMakeRelative && !onNodePin && !onNodeUnpin) {
    return null;
  }
  const controls = [
    {
      ariaLabel: t("workspace.diagram.setModeAbsolute"),
      disabled: node.mode === "absolute" || !onNodePin,
      label: modeLabel("absolute", t),
      mode: "absolute" as const,
      onClick: () => onNodePin?.(node.id),
    },
    {
      ariaLabel: t("workspace.diagram.setModeRelative"),
      disabled: node.mode === "relative" || !node.parentId || !onNodeMakeRelative,
      label: modeLabel("relative", t),
      mode: "relative" as const,
      onClick: () => onNodeMakeRelative?.(node.id),
    },
    {
      ariaLabel: t("workspace.diagram.setModeAuto"),
      disabled: node.mode === "auto" || !onNodeUnpin,
      label: modeLabel("auto", t),
      mode: "auto" as const,
      onClick: () => onNodeUnpin?.(node.id),
    },
  ];
  return (
    <div className="project-diagram-mode-controls" role="group" aria-label={t("workspace.diagram.modeControls")}>
      {controls.map((control) => (
        <button aria-label={control.ariaLabel} aria-pressed={node.mode === control.mode} className="toolbar-button" disabled={control.disabled} key={control.mode} onClick={control.onClick} title={control.ariaLabel} type="button">
          {control.label}
        </button>
      ))}
    </div>
  );
}

function DiagramSelectedPositionForm({ node, onNodeSetPosition, t }: { node: ResolvedDiagramNode; onNodeSetPosition: (nodeId: string, position: { x: number; y: number }) => void; t: Translator }) {
  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    const x = Number(form.get("x"));
    const y = Number(form.get("y"));
    if (Number.isFinite(x) && Number.isFinite(y)) {
      onNodeSetPosition(node.id, { x, y });
    }
  };
  return (
    <form aria-label={t("workspace.diagram.setPosition")} className="project-diagram-position-form" onSubmit={handleSubmit}>
      <label>
        <span>{t("workspace.diagram.positionX")}</span>
        <input aria-label={t("workspace.diagram.positionXAria")} defaultValue={formatViewBoxNumber(node.worldX)} name="x" step="1" type="number" />
      </label>
      <label>
        <span>{t("workspace.diagram.positionY")}</span>
        <input aria-label={t("workspace.diagram.positionYAria")} defaultValue={formatViewBoxNumber(node.worldY)} name="y" step="1" type="number" />
      </label>
      <button className="toolbar-button project-diagram-set-position" type="submit">
        <Crosshair aria-hidden="true" size={13} />
        {t("workspace.diagram.setPositionAction")}
      </button>
    </form>
  );
}

function DiagramSelectedLayoutHintsForm({ node, onNodeSetLayoutHints, t }: { node: ResolvedDiagramNode; onNodeSetLayoutHints: (nodeId: string, hints: DiagramNodeLayoutHints) => void; t: Translator }) {
  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    onNodeSetLayoutHints(node.id, {
      priority: optionalNumberFormValue(form.get("priority")),
      subtreeWidth: optionalNumberFormValue(form.get("subtreeWidth")),
      subtreeWidthDelta: optionalNumberFormValue(form.get("subtreeWidthDelta")),
      subtreeCenterOffset: optionalNumberFormValue(form.get("subtreeCenterOffset")),
    });
  };
  return (
    <form aria-label={t("workspace.diagram.setLayoutHints")} className="project-diagram-layout-hints-form" onSubmit={handleSubmit}>
      <label>
        <span>{t("workspace.diagram.selectedPriority")}</span>
        <input aria-label={t("workspace.diagram.priorityAria")} defaultValue={optionalNumberText(node.priority)} name="priority" step="1" type="number" />
      </label>
      <label>
        <span>{t("workspace.diagram.selectedSubtreeWidth")}</span>
        <input aria-label={t("workspace.diagram.subtreeWidthAria")} defaultValue={optionalNumberText(node.subtreeWidth)} min="1" name="subtreeWidth" step="1" type="number" />
      </label>
      <label>
        <span>{t("workspace.diagram.selectedSubtreeWidthDelta")}</span>
        <input aria-label={t("workspace.diagram.subtreeWidthDeltaAria")} defaultValue={optionalNumberText(node.subtreeWidthDelta)} name="subtreeWidthDelta" step="1" type="number" />
      </label>
      <label>
        <span>{t("workspace.diagram.selectedSubtreeCenterOffset")}</span>
        <input aria-label={t("workspace.diagram.subtreeCenterOffsetAria")} defaultValue={optionalNumberText(node.subtreeCenterOffset)} name="subtreeCenterOffset" step="1" type="number" />
      </label>
      <button className="toolbar-button project-diagram-set-layout-hints" type="submit">
        <Crosshair aria-hidden="true" size={13} />
        {t("workspace.diagram.setLayoutHintsAction")}
      </button>
    </form>
  );
}

function DiagramSelectedProviderRelationshipForm({ candidates, nodeId, onNodeSetRelationship, onRelationshipPickStart, pickActive = false, relationship }: { candidates: DiagramCandidate[]; nodeId: string; onNodeSetRelationship: (relationship: ProjectDiagramRelationship, selectedNodeId: string, relatedNodeId: string, present: boolean) => void; onRelationshipPickStart?: (relationship: ProjectDiagramRelationship) => void; pickActive?: boolean; relationship: ProjectDiagramRelationship }) {
  if (candidates.length === 0) {
    return null;
  }
  const listId = `project-diagram-${slug(relationship.kind)}-candidates-${slug(nodeId)}`;
  const addLabel = `Add ${relationship.label}`;
  const pickLabel = `Pick ${relationship.label} on canvas`;
  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    const relatedId = diagramCandidateIdFromInput(candidates, String(form.get("relatedId") ?? ""));
    if (!relatedId) {
      return;
    }
    onNodeSetRelationship(relationship, nodeId, relatedId, true);
    event.currentTarget.reset();
  };
  return (
    <form aria-label={addLabel} className="project-diagram-provider-relationship-form" data-relationship-kind={relationship.kind} onSubmit={handleSubmit}>
      <label>
        <span>{relationship.label}</span>
        <input aria-label={`${relationship.label} related node id`} list={listId} name="relatedId" placeholder="Choose a node" spellCheck={false} />
      </label>
      <datalist id={listId}>
        {candidates.map((candidate) => (
          <option key={candidate.id} label={candidateOptionLabel(candidate)} value={candidate.id} />
        ))}
      </datalist>
      <button className="toolbar-button project-diagram-add-provider-relationship" type="submit">
        <Plus aria-hidden="true" size={13} />
        {addLabel}
      </button>
      {onRelationshipPickStart ? (
        <button aria-label={pickLabel} aria-pressed={pickActive} className="toolbar-button icon-only project-diagram-pick-relationship" onClick={() => onRelationshipPickStart(relationship)} title={pickLabel} type="button">
          <Crosshair aria-hidden="true" size={13} />
        </button>
      ) : null}
      <DiagramCandidateButtons candidates={candidates} label={addLabel} onChoose={(id) => onNodeSetRelationship(relationship, nodeId, id, true)} />
    </form>
  );
}

function DiagramSelectedDependencyForm({ candidates, nodeId, onNodeAddDependency, onRelationshipPickStart, pickActive = false, t }: { candidates: DiagramCandidate[]; nodeId: string; onNodeAddDependency: (targetId: string, sourceId: string) => void; onRelationshipPickStart?: (kind: DiagramRelationshipPickKind) => void; pickActive?: boolean; t: Translator }) {
  if (candidates.length === 0) {
    return null;
  }
  const listId = `project-diagram-dependency-candidates-${slug(nodeId)}`;
  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    const sourceId = diagramCandidateIdFromInput(candidates, String(form.get("sourceId") ?? ""));
    if (!sourceId) {
      return;
    }
    onNodeAddDependency(nodeId, sourceId);
    event.currentTarget.reset();
  };
  return (
    <form aria-label={t("workspace.diagram.addDependency")} className="project-diagram-dependency-form" onSubmit={handleSubmit}>
      <label>
        <span>{t("workspace.diagram.addDependencySource")}</span>
        <input aria-label={t("workspace.diagram.addDependencySourceAria")} list={listId} name="sourceId" placeholder={t("workspace.diagram.addDependencyPlaceholder")} spellCheck={false} />
      </label>
      <datalist id={listId}>
        {candidates.map((candidate) => (
          <option key={candidate.id} label={candidateOptionLabel(candidate)} value={candidate.id} />
        ))}
      </datalist>
      <button className="toolbar-button project-diagram-add-dependency" type="submit">
        <Plus aria-hidden="true" size={13} />
        {t("workspace.diagram.addDependencyAction")}
      </button>
      {onRelationshipPickStart ? (
        <button aria-label={t("workspace.diagram.pickDependency")} aria-pressed={pickActive} className="toolbar-button icon-only project-diagram-pick-relationship" onClick={() => onRelationshipPickStart("dependency")} title={t("workspace.diagram.pickDependency")} type="button">
          <Crosshair aria-hidden="true" size={13} />
        </button>
      ) : null}
      <DiagramCandidateButtons candidates={candidates} label={t("workspace.diagram.addDependencyAction")} onChoose={(id) => onNodeAddDependency(nodeId, id)} />
    </form>
  );
}

function DiagramSelectedUnlockForm({ candidates, nodeId, onNodeAddUnlock, onRelationshipPickStart, pickActive = false, t }: { candidates: DiagramCandidate[]; nodeId: string; onNodeAddUnlock: (sourceId: string, targetId: string) => void; onRelationshipPickStart?: (kind: DiagramRelationshipPickKind) => void; pickActive?: boolean; t: Translator }) {
  if (candidates.length === 0) {
    return null;
  }
  const listId = `project-diagram-unlock-candidates-${slug(nodeId)}`;
  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    const targetId = diagramCandidateIdFromInput(candidates, String(form.get("targetId") ?? ""));
    if (!targetId) {
      return;
    }
    onNodeAddUnlock(nodeId, targetId);
    event.currentTarget.reset();
  };
  return (
    <form aria-label={t("workspace.diagram.addUnlock")} className="project-diagram-unlock-form" onSubmit={handleSubmit}>
      <label>
        <span>{t("workspace.diagram.addUnlockTarget")}</span>
        <input aria-label={t("workspace.diagram.addUnlockTargetAria")} list={listId} name="targetId" placeholder={t("workspace.diagram.addUnlockPlaceholder")} spellCheck={false} />
      </label>
      <datalist id={listId}>
        {candidates.map((candidate) => (
          <option key={candidate.id} label={candidateOptionLabel(candidate)} value={candidate.id} />
        ))}
      </datalist>
      <button className="toolbar-button project-diagram-add-unlock" type="submit">
        <Plus aria-hidden="true" size={13} />
        {t("workspace.diagram.addUnlockAction")}
      </button>
      {onRelationshipPickStart ? (
        <button aria-label={t("workspace.diagram.pickUnlock")} aria-pressed={pickActive} className="toolbar-button icon-only project-diagram-pick-relationship" onClick={() => onRelationshipPickStart("unlock")} title={t("workspace.diagram.pickUnlock")} type="button">
          <Crosshair aria-hidden="true" size={13} />
        </button>
      ) : null}
      <DiagramCandidateButtons candidates={candidates} label={t("workspace.diagram.addUnlockAction")} onChoose={(id) => onNodeAddUnlock(nodeId, id)} />
    </form>
  );
}

function DiagramSelectedParentForm({ candidates, nodeId, onNodeSetParent, t }: { candidates: DiagramCandidate[]; nodeId: string; onNodeSetParent: (nodeId: string, parentId: string) => void; t: Translator }) {
  if (candidates.length === 0) {
    return null;
  }
  const listId = `project-diagram-parent-candidates-${slug(nodeId)}`;
  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    const parentId = diagramCandidateIdFromInput(candidates, String(form.get("parentId") ?? ""));
    if (!parentId) {
      return;
    }
    onNodeSetParent(nodeId, parentId);
    event.currentTarget.reset();
  };
  return (
    <form aria-label={t("workspace.diagram.setParent")} className="project-diagram-parent-form" onSubmit={handleSubmit}>
      <label>
        <span>{t("workspace.diagram.setParentTarget")}</span>
        <input aria-label={t("workspace.diagram.setParentTargetAria")} list={listId} name="parentId" placeholder={t("workspace.diagram.setParentPlaceholder")} spellCheck={false} />
      </label>
      <datalist id={listId}>
        {candidates.map((candidate) => (
          <option key={candidate.id} label={candidateOptionLabel(candidate)} value={candidate.id} />
        ))}
      </datalist>
      <button className="toolbar-button project-diagram-set-parent" type="submit">
        <GitBranch aria-hidden="true" size={13} />
        {t("workspace.diagram.setParentAction")}
      </button>
      <DiagramCandidateButtons candidates={candidates} label={t("workspace.diagram.setParentAction")} onChoose={(id) => onNodeSetParent(nodeId, id)} />
    </form>
  );
}

function DiagramSelectedReferenceForm({ candidates, nodeId, onNodeAddReference, onRelationshipPickStart, pickActive = false, t }: { candidates: DiagramCandidate[]; nodeId: string; onNodeAddReference: (sourceId: string, targetId: string) => void; onRelationshipPickStart?: (kind: DiagramRelationshipPickKind) => void; pickActive?: boolean; t: Translator }) {
  if (candidates.length === 0) {
    return null;
  }
  const listId = `project-diagram-reference-candidates-${slug(nodeId)}`;
  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    const targetId = diagramCandidateIdFromInput(candidates, String(form.get("targetId") ?? ""));
    if (!targetId) {
      return;
    }
    onNodeAddReference(nodeId, targetId);
    event.currentTarget.reset();
  };
  return (
    <form aria-label={t("workspace.diagram.addReference")} className="project-diagram-reference-form" onSubmit={handleSubmit}>
      <label>
        <span>{t("workspace.diagram.addReferenceTarget")}</span>
        <input aria-label={t("workspace.diagram.addReferenceTargetAria")} list={listId} name="targetId" placeholder={t("workspace.diagram.addReferencePlaceholder")} spellCheck={false} />
      </label>
      <datalist id={listId}>
        {candidates.map((candidate) => (
          <option key={candidate.id} label={candidateOptionLabel(candidate)} value={candidate.id} />
        ))}
      </datalist>
      <button className="toolbar-button project-diagram-add-reference" type="submit">
        <Plus aria-hidden="true" size={13} />
        {t("workspace.diagram.addReferenceAction")}
      </button>
      {onRelationshipPickStart ? (
        <button aria-label={t("workspace.diagram.pickReference")} aria-pressed={pickActive} className="toolbar-button icon-only project-diagram-pick-relationship" onClick={() => onRelationshipPickStart("reference")} title={t("workspace.diagram.pickReference")} type="button">
          <Crosshair aria-hidden="true" size={13} />
        </button>
      ) : null}
      <DiagramCandidateButtons candidates={candidates} label={t("workspace.diagram.addReferenceAction")} onChoose={(id) => onNodeAddReference(nodeId, id)} />
    </form>
  );
}

function DiagramCandidateButtons({ candidates, label, onChoose }: { candidates: DiagramCandidate[]; label: string; onChoose: (id: string) => void }) {
  if (candidates.length === 0) {
    return null;
  }
  const visibleCandidates = candidates.slice(0, MAX_QUICK_CANDIDATE_BUTTONS);
  const hiddenCandidates = candidates.slice(MAX_QUICK_CANDIDATE_BUTTONS);
  return (
    <div className="project-diagram-candidate-list">
      {visibleCandidates.map((candidate) => {
        const title = `${label} ${candidateDisplayText(candidate)}`;
        return (
          <button aria-label={title} className="project-diagram-candidate-button" key={candidate.id} onClick={() => onChoose(candidate.id)} title={title} type="button">
            <span className="project-diagram-candidate-id">{candidate.id}</span>
            {candidate.title !== candidate.id ? <span className="project-diagram-candidate-title">{candidate.title}</span> : null}
          </button>
        );
      })}
      {hiddenCandidates.length > 0 ? (
        <span className="project-diagram-candidate-more" title={hiddenCandidates.map(candidateDisplayText).join(", ")}>
          +{hiddenCandidates.length}
        </span>
      ) : null}
    </div>
  );
}

function DiagramSelectionRelationshipRow({ candidatesById, ids, label, onNodeSelect, onRemove, removeLabel, selectLabel }: { candidatesById: Map<string, DiagramCandidate>; ids: string[]; label: string; onNodeSelect?: (nodeId: string) => void; onRemove?: (nodeId: string) => void; removeLabel?: (id: string) => string; selectLabel: (id: string) => string }) {
  if (ids.length === 0) {
    return null;
  }
  const [prefix] = label.split(" ");
  const displayCandidates = candidatesByIds(ids, candidatesById);
  return (
    <span className="project-diagram-selection-link-row" title={displayCandidates.map(candidateDisplayText).join(", ")}>
      <span className="project-diagram-selection-link-label">{prefix}</span>
      {displayCandidates.map((candidate) => {
        const displayText = candidateDisplayText(candidate);
        return (
          <span className="project-diagram-selection-link-group" key={candidate.id}>
            <button aria-label={selectLabel(displayText)} className="project-diagram-selection-link" disabled={!onNodeSelect} onClick={() => onNodeSelect?.(candidate.id)} type="button">
              <span className="project-diagram-selection-link-id">{candidate.id}</span>
              {candidate.title !== candidate.id ? <span className="project-diagram-selection-link-title">{candidate.title}</span> : null}
            </button>
            {onRemove && removeLabel ? (
              <button aria-label={removeLabel(displayText)} className="project-diagram-selection-link-remove" onClick={() => onRemove(candidate.id)} title={removeLabel(displayText)} type="button">
                <Trash2 aria-hidden="true" size={10} />
              </button>
            ) : null}
          </span>
        );
      })}
    </span>
  );
}

function DiagramSearchControls({ matchCount, matchIndex, nodeCount, onNavigate, onQueryChange, query, t }: { matchCount: number; matchIndex: number; nodeCount: number; onNavigate: (direction: -1 | 1) => void; onQueryChange: (query: string) => void; query: string; t: Translator }) {
  const hasQuery = query.trim().length > 0;
  const hasMatches = matchCount > 0;
  const resultText = hasQuery
    ? t("workspace.diagram.searchResult", {
        current: hasMatches ? String(matchIndex + 1) : "0",
        total: String(matchCount),
      })
    : t("workspace.diagram.searchIdle", { count: String(nodeCount) });
  const handleKeyDown = (event: KeyboardEvent<HTMLInputElement>) => {
    const action = diagramSearchKeyAction(event.key, event.shiftKey);
    if (action.kind === "none") {
      return;
    }
    event.preventDefault();
    if (action.kind === "clear") {
      onQueryChange("");
      return;
    }
    onNavigate(action.kind === "previous" ? -1 : 1);
  };
  return (
    <div className="project-diagram-search">
      <label className="project-diagram-search-box">
        <Search aria-hidden="true" size={13} />
        <input aria-label={t("workspace.diagram.search")} aria-keyshortcuts="Enter Shift+Enter Escape" className="project-diagram-search-input" onChange={(event) => onQueryChange(event.currentTarget.value)} onKeyDown={handleKeyDown} placeholder={t("workspace.diagram.search")} type="search" value={query} />
      </label>
      <span className="project-diagram-search-count">{resultText}</span>
      <button aria-label={t("workspace.diagram.searchPrevious")} className="toolbar-button icon-only" disabled={!hasMatches} onClick={() => onNavigate(-1)} title={t("workspace.diagram.searchPrevious")} type="button">
        <ArrowLeft aria-hidden="true" size={13} />
      </button>
      <button aria-label={t("workspace.diagram.searchNext")} className="toolbar-button icon-only" disabled={!hasMatches} onClick={() => onNavigate(1)} title={t("workspace.diagram.searchNext")} type="button">
        <ArrowRight aria-hidden="true" size={13} />
      </button>
    </div>
  );
}

function DiagramPanControls({ canCenterSelected, onCenterSelected, onPan, onReset, panOffset, step, t }: { canCenterSelected: boolean; onCenterSelected: () => void; onPan: (delta: CanvasPoint) => void; onReset: () => void; panOffset: CanvasPoint; step: number; t: Translator }) {
  const resetDisabled = panOffset.x === 0 && panOffset.y === 0;
  return (
    <div className="project-diagram-pan" aria-label={t("workspace.diagram.panControls")}>
      <button aria-label={t("workspace.diagram.panUp")} className="toolbar-button icon-only" onClick={() => onPan({ x: 0, y: -step })} title={t("workspace.diagram.panUp")} type="button">
        <ArrowUp aria-hidden="true" size={13} />
      </button>
      <button aria-label={t("workspace.diagram.panLeft")} className="toolbar-button icon-only" onClick={() => onPan({ x: -step, y: 0 })} title={t("workspace.diagram.panLeft")} type="button">
        <ArrowLeft aria-hidden="true" size={13} />
      </button>
      <button aria-label={t("workspace.diagram.panReset")} className="toolbar-button icon-only" disabled={resetDisabled} onClick={onReset} title={t("workspace.diagram.panReset")} type="button">
        <RotateCcw aria-hidden="true" size={13} />
      </button>
      <button aria-label={t("workspace.diagram.centerSelected")} className="toolbar-button icon-only" disabled={!canCenterSelected} onClick={onCenterSelected} title={t("workspace.diagram.centerSelected")} type="button">
        <Crosshair aria-hidden="true" size={13} />
      </button>
      <button aria-label={t("workspace.diagram.panRight")} className="toolbar-button icon-only" onClick={() => onPan({ x: step, y: 0 })} title={t("workspace.diagram.panRight")} type="button">
        <ArrowRight aria-hidden="true" size={13} />
      </button>
      <button aria-label={t("workspace.diagram.panDown")} className="toolbar-button icon-only" onClick={() => onPan({ x: 0, y: step })} title={t("workspace.diagram.panDown")} type="button">
        <ArrowDown aria-hidden="true" size={13} />
      </button>
    </div>
  );
}

function DiagramZoomControls({ onZoomIndexChange, t, zoomIndex }: { onZoomIndexChange: (updater: (current: number) => number) => void; t: Translator; zoomIndex: number }) {
  const zoom = DIAGRAM_ZOOM_LEVELS[zoomIndex];
  return (
    <div className="project-diagram-zoom" aria-label={t("workspace.diagram.zoomControls")}>
      <button aria-label={t("workspace.diagram.zoomOut")} className="toolbar-button icon-only" disabled={zoomIndex === 0} onClick={() => onZoomIndexChange((current) => Math.max(0, current - 1))} title={t("workspace.diagram.zoomOut")} type="button">
        <ZoomOut aria-hidden="true" size={13} />
      </button>
      <button aria-label={t("workspace.diagram.zoomReset")} className="toolbar-button project-diagram-zoom-reset" disabled={zoomIndex === DEFAULT_DIAGRAM_ZOOM_INDEX} onClick={() => onZoomIndexChange(() => DEFAULT_DIAGRAM_ZOOM_INDEX)} title={t("workspace.diagram.zoomReset")} type="button">
        {Math.round(zoom * 100)}%
      </button>
      <button aria-label={t("workspace.diagram.zoomIn")} className="toolbar-button icon-only" disabled={zoomIndex === DIAGRAM_ZOOM_LEVELS.length - 1} onClick={() => onZoomIndexChange((current) => Math.min(DIAGRAM_ZOOM_LEVELS.length - 1, current + 1))} title={t("workspace.diagram.zoomIn")} type="button">
        <ZoomIn aria-hidden="true" size={13} />
      </button>
    </div>
  );
}

function DiagramMiniMap({ currentSearchMatchId, gridSize, moveAffectedIds, nodes, onTargetPoint, selectedNodeId, searchMatchIds, t, viewBox, viewportViewBox }: { currentSearchMatchId: string; gridSize: number; moveAffectedIds?: ReadonlySet<DiagramNodeId> | null; nodes: ResolvedDiagramNode[]; onTargetPoint: (point: CanvasPoint) => void; selectedNodeId: string; searchMatchIds: Set<string>; t: Translator; viewBox: string; viewportViewBox: string }) {
  const [dragPointerId, setDragPointerId] = useState<number | null>(null);
  const mapBox = parseViewBox(viewBox);
  const viewport = parseViewBox(viewportViewBox);
  if (!mapBox || !viewport) {
    return null;
  }
  const [mapX, mapY, mapWidth, mapHeight] = mapBox;
  const [viewportX, viewportY, viewportWidth, viewportHeight] = viewport;
  const handlePointerDown = (event: PointerEvent<SVGSVGElement>) => {
    const start = diagramMiniMapDragStart(pointerEventToRootSvgPoint(event), event.pointerId);
    if (!start) {
      return;
    }
    event.preventDefault();
    event.currentTarget.setPointerCapture(event.pointerId);
    setDragPointerId(start.dragPointerId);
    onTargetPoint(start.targetPoint);
  };
  const handlePointerMove = (event: PointerEvent<SVGSVGElement>) => {
    const targetPoint = diagramMiniMapDragMove(dragPointerId, event.pointerId, pointerEventToRootSvgPoint(event));
    if (!targetPoint) {
      return;
    }
    event.preventDefault();
    onTargetPoint(targetPoint);
  };
  const handlePointerEnd = (event: PointerEvent<SVGSVGElement>) => {
    const nextDragPointerId = diagramMiniMapDragEnd(dragPointerId, event.pointerId);
    if (nextDragPointerId === dragPointerId) {
      return;
    }
    event.preventDefault();
    if (event.currentTarget.hasPointerCapture(event.pointerId)) {
      event.currentTarget.releasePointerCapture(event.pointerId);
    }
    setDragPointerId(nextDragPointerId);
  };
  const handleKeyDown = (event: KeyboardEvent<SVGSVGElement>) => {
    if (event.key !== "Enter" && event.key !== " ") {
      return;
    }
    event.preventDefault();
    onTargetPoint({ x: mapX + mapWidth / 2, y: mapY + mapHeight / 2 });
  };
  return (
    <svg className="project-diagram-minimap" role="button" tabIndex={0} viewBox={viewBox} aria-label={t("workspace.diagram.minimap")} onKeyDown={handleKeyDown} onPointerCancel={handlePointerEnd} onPointerDown={handlePointerDown} onPointerMove={handlePointerMove} onPointerUp={handlePointerEnd}>
      <rect className="project-diagram-minimap-bg" height={mapHeight} width={mapWidth} x={mapX} y={mapY} />
      <g>
        {nodes.map((node) => {
          const classes = diagramMiniMapNodeClassName({
            moveAffected: moveAffectedIds?.has(node.id),
            searchCurrent: node.id === currentSearchMatchId,
            searchMatch: searchMatchIds.has(node.id),
            selected: node.id === selectedNodeId,
          });
          const visibleBox = diagramNodeVisibleGridBox(node);
          return <rect className={classes} data-node-id={node.id} height={visibleBox.height * gridSize} key={node.id} width={visibleBox.width * gridSize} x={(node.worldX + visibleBox.x) * gridSize} y={(node.worldY + visibleBox.y) * gridSize} />;
        })}
      </g>
      <rect aria-label={t("workspace.diagram.minimapViewport")} className="project-diagram-minimap-viewport" height={viewportHeight} width={viewportWidth} x={viewportX} y={viewportY} />
    </svg>
  );
}

function DiagramNudgeControls({ nodeId, onNodeAutoLayout, onNodeAutoLayoutDescendants, onNodeAutoLayoutSubtree, canAutoLayoutSelectedDescendants, canAutoLayoutSelectedNode, canAutoLayoutSelectedSubtree, canInsertSelectedChild, canMakeRelativeSelectedNode, canMakeRelativeSelectedSubtree, canMoveSelectedRelayoutDescendants, canPinSelectedNode, canPinSelectedSubtree, canReorderSiblingEarlier, canReorderSiblingLater, canRemoveSelectedNodeOnly, canRemoveSelectedSubtree, onNodeInsertChild, onNodeMove, onNodeMoveKeepingDescendants, onNodeMoveRelayoutDescendants, onNodeMoveSubtree, onNodeMakeRelative, onNodeMakeSubtreeRelative, onSelectedMoveModeChange, moveImpactNodeCount = 0, onNodePin, onNodePinSubtree, onNodeReorderSibling, onNodeRemoveOnly, onNodeRemoveSubtree, onNodeUnpin, onNodeUnpinSubtree, selectedMoveMode, t }: { nodeId: string; onNodeAutoLayout?: (nodeId: string) => void; onNodeAutoLayoutDescendants?: (nodeId: string) => void; onNodeAutoLayoutSubtree?: (nodeId: string) => void; canAutoLayoutSelectedDescendants?: boolean; canAutoLayoutSelectedNode?: boolean; canAutoLayoutSelectedSubtree?: boolean; canInsertSelectedChild?: boolean; canMakeRelativeSelectedNode?: boolean; canMakeRelativeSelectedSubtree?: boolean; canMoveSelectedRelayoutDescendants?: boolean; canPinSelectedNode?: boolean; canPinSelectedSubtree?: boolean; canReorderSiblingEarlier?: boolean; canReorderSiblingLater?: boolean; canRemoveSelectedNodeOnly?: boolean; canRemoveSelectedSubtree?: boolean; onNodeInsertChild?: (nodeId: string) => void; onNodeMove?: (nodeId: string, delta: DiagramMoveDelta) => void; onNodeMoveKeepingDescendants?: (nodeId: string, delta: DiagramMoveDelta) => void; onNodeMoveRelayoutDescendants?: (nodeId: string, delta: DiagramMoveDelta) => void; onNodeMoveSubtree?: (nodeId: string, delta: DiagramMoveDelta) => void; onNodeMakeRelative?: (nodeId: string) => void; onNodeMakeSubtreeRelative?: (nodeId: string) => void; onSelectedMoveModeChange: (mode: DiagramNodeMoveCommandKind) => void; moveImpactNodeCount?: number; onNodePin?: (nodeId: string) => void; onNodePinSubtree?: (nodeId: string) => void; onNodeReorderSibling?: (nodeId: string, direction: -1 | 1) => void; onNodeRemoveOnly?: (nodeId: string) => void; onNodeRemoveSubtree?: (nodeId: string) => void; onNodeUnpin?: (nodeId: string) => void; onNodeUnpinSubtree?: (nodeId: string) => void; selectedMoveMode: DiagramNodeMoveCommandKind; t: Translator }) {
  const moveModes = diagramToolbarMoveModes({
    canMoveRelayoutDescendants: Boolean(canMoveSelectedRelayoutDescendants),
    onNodeMove,
    onNodeMoveKeepingDescendants,
    onNodeMoveRelayoutDescendants,
    onNodeMoveSubtree,
    t,
  });
  const activeMoveMode = diagramActiveToolbarMoveMode(moveModes, selectedMoveMode);
  const activeMoveImpactText = activeMoveMode ? diagramMoveImpactText(moveImpactNodeCount, t) : "";
  const activeMoveHintText = activeMoveMode ? diagramMoveModeHintText(activeMoveMode.id, t) : "";
  const moveDirections = diagramMoveDirections();
  return (
    <div className="project-diagram-nudge" aria-label={t("workspace.diagram.moveSelected")}>
      {onNodePinSubtree ? (
        <button aria-label={t("workspace.diagram.pinSubtree")} className="toolbar-button icon-only project-diagram-pin-subtree" disabled={!canPinSelectedSubtree} onClick={() => onNodePinSubtree(nodeId)} title={t("workspace.diagram.pinSubtree")} type="button">
          <Pin aria-hidden="true" size={13} />
        </button>
      ) : null}
      {onNodeMakeSubtreeRelative ? (
        <button aria-label={t("workspace.diagram.makeRelativeSubtree")} className="toolbar-button icon-only project-diagram-relative-subtree" disabled={!canMakeRelativeSelectedSubtree} onClick={() => onNodeMakeSubtreeRelative(nodeId)} title={t("workspace.diagram.makeRelativeSubtree")} type="button">
          <GitBranch aria-hidden="true" size={13} />
        </button>
      ) : null}
      {onNodePin ? (
        <button aria-label={t("workspace.diagram.pinSelected")} className="toolbar-button icon-only project-diagram-pin-node" disabled={!canPinSelectedNode} onClick={() => onNodePin(nodeId)} title={t("workspace.diagram.pinSelected")} type="button">
          <Pin aria-hidden="true" size={13} />
        </button>
      ) : null}
      {onNodeMakeRelative ? (
        <button aria-label={t("workspace.diagram.makeRelativeSelected")} className="toolbar-button icon-only project-diagram-relative-node" disabled={!canMakeRelativeSelectedNode} onClick={() => onNodeMakeRelative(nodeId)} title={t("workspace.diagram.makeRelativeSelected")} type="button">
          <GitBranch aria-hidden="true" size={13} />
        </button>
      ) : null}
      {onNodeUnpinSubtree ? (
        <button aria-label={t("workspace.diagram.unpinSubtree")} className="toolbar-button icon-only project-diagram-unpin-subtree" disabled={!canAutoLayoutSelectedSubtree} onClick={() => onNodeUnpinSubtree(nodeId)} title={t("workspace.diagram.unpinSubtree")} type="button">
          <RotateCcw aria-hidden="true" size={13} />
        </button>
      ) : null}
      {onNodeAutoLayoutSubtree ? (
        <button aria-label={t("workspace.diagram.autoLayoutSubtree")} className="toolbar-button icon-only project-diagram-auto-layout-subtree" disabled={!canAutoLayoutSelectedSubtree} onClick={() => onNodeAutoLayoutSubtree(nodeId)} title={t("workspace.diagram.autoLayoutSubtree")} type="button">
          <RefreshCw aria-hidden="true" size={13} />
        </button>
      ) : null}
      {onNodeAutoLayoutDescendants ? (
        <button aria-label={t("workspace.diagram.autoLayoutDescendants")} className="toolbar-button icon-only project-diagram-auto-layout-descendants" disabled={!canAutoLayoutSelectedDescendants} onClick={() => onNodeAutoLayoutDescendants(nodeId)} title={t("workspace.diagram.autoLayoutDescendants")} type="button">
          <RefreshCw aria-hidden="true" size={13} />
        </button>
      ) : null}
      {onNodeUnpin ? (
        <button aria-label={t("workspace.diagram.unpinSelected")} className="toolbar-button icon-only project-diagram-unpin-node" disabled={!canAutoLayoutSelectedNode} onClick={() => onNodeUnpin(nodeId)} title={t("workspace.diagram.unpinSelected")} type="button">
          <RotateCcw aria-hidden="true" size={13} />
        </button>
      ) : null}
      {onNodeAutoLayout ? (
        <button aria-label={t("workspace.diagram.autoLayoutSelected")} className="toolbar-button icon-only project-diagram-auto-layout" disabled={!canAutoLayoutSelectedNode} onClick={() => onNodeAutoLayout(nodeId)} title={t("workspace.diagram.autoLayoutSelected")} type="button">
          <RefreshCw aria-hidden="true" size={13} />
        </button>
      ) : null}
      {onNodeReorderSibling ? (
        <>
          <button aria-label={t("workspace.diagram.reorderSiblingEarlier")} className="toolbar-button icon-only project-diagram-reorder-sibling" disabled={!canReorderSiblingEarlier} onClick={() => onNodeReorderSibling(nodeId, -1)} title={t("workspace.diagram.reorderSiblingEarlier")} type="button">
            <ArrowLeft aria-hidden="true" size={13} />
          </button>
          <button aria-label={t("workspace.diagram.reorderSiblingLater")} className="toolbar-button icon-only project-diagram-reorder-sibling" disabled={!canReorderSiblingLater} onClick={() => onNodeReorderSibling(nodeId, 1)} title={t("workspace.diagram.reorderSiblingLater")} type="button">
            <ArrowRight aria-hidden="true" size={13} />
          </button>
        </>
      ) : null}
      {onNodeInsertChild && canInsertSelectedChild ? (
        <button aria-label={t("workspace.diagram.insertChildFocus")} className="toolbar-button icon-only project-diagram-insert-child" onClick={() => onNodeInsertChild(nodeId)} title={t("workspace.diagram.insertChildFocus")} type="button">
          <Plus aria-hidden="true" size={13} />
        </button>
      ) : null}
      {onNodeRemoveOnly && canRemoveSelectedNodeOnly ? (
        <button aria-label={t("workspace.diagram.removeFocus")} className="toolbar-button icon-only danger project-diagram-remove-node" onClick={() => onNodeRemoveOnly(nodeId)} title={t("workspace.diagram.removeFocus")} type="button">
          <Trash2 aria-hidden="true" size={13} />
        </button>
      ) : null}
      {onNodeRemoveSubtree && canRemoveSelectedSubtree ? (
        <button aria-label={t("workspace.diagram.removeFocusSubtree")} className="toolbar-button icon-only danger project-diagram-remove-subtree" onClick={() => onNodeRemoveSubtree(nodeId)} title={t("workspace.diagram.removeFocusSubtree")} type="button">
          <Trash2 aria-hidden="true" size={13} />
        </button>
      ) : null}
      {moveModes.length > 0 ? (
        <div className="project-diagram-move-tools" role="group" aria-label={t("workspace.diagram.moveSelected")}>
          <div className="project-diagram-move-modes" role="group" aria-label={t("workspace.diagram.moveMode")}>
            {moveModes.map((mode) => (
              <button aria-label={mode.title} aria-pressed={activeMoveMode?.id === mode.id} className="toolbar-button project-diagram-move-mode" disabled={mode.disabled} key={mode.id} onClick={() => onSelectedMoveModeChange(mode.id)} title={mode.title} type="button">
                {mode.label}
              </button>
            ))}
          </div>
          {activeMoveImpactText ? (
            <span className="project-diagram-move-impact" title={activeMoveImpactText}>
              {activeMoveImpactText}
            </span>
          ) : null}
          {activeMoveHintText ? (
            <span className="project-diagram-move-hint" title={activeMoveHintText}>
              {activeMoveHintText}
            </span>
          ) : null}
          <div className="project-diagram-move-pad" role="group" aria-label={activeMoveMode?.title ?? t("workspace.diagram.moveSelected")}>
            {moveDirections.map((direction) => {
              const title = activeMoveMode ? diagramMoveDirectionTitle(activeMoveMode.id, direction.id, t) : t("workspace.diagram.moveSelected");
              return (
                <button aria-label={title} className={`toolbar-button icon-only project-diagram-move-pad-${direction.id}`} disabled={!activeMoveMode} key={direction.id} onClick={() => activeMoveMode?.move?.(nodeId, direction.delta)} title={title} type="button">
                  {direction.icon}
                </button>
              );
            })}
          </div>
        </div>
      ) : null}
    </div>
  );
}

function diagramToolbarMoveModes({ canMoveRelayoutDescendants, onNodeMove, onNodeMoveKeepingDescendants, onNodeMoveRelayoutDescendants, onNodeMoveSubtree, t }: { canMoveRelayoutDescendants: boolean; onNodeMove?: (nodeId: string, delta: DiagramMoveDelta) => void; onNodeMoveKeepingDescendants?: (nodeId: string, delta: DiagramMoveDelta) => void; onNodeMoveRelayoutDescendants?: (nodeId: string, delta: DiagramMoveDelta) => void; onNodeMoveSubtree?: (nodeId: string, delta: DiagramMoveDelta) => void; t: Translator }): DiagramToolbarMoveMode[] {
  const modes: DiagramToolbarMoveMode[] = [];
  if (onNodeMoveSubtree) {
    modes.push({
      disabled: false,
      id: "subtree",
      label: t("workspace.diagram.moveMode.subtree"),
      move: onNodeMoveSubtree,
      title: t("workspace.diagram.moveMode.subtreeTitle"),
    });
  }
  if (onNodeMove) {
    modes.push({
      disabled: false,
      id: "node",
      label: t("workspace.diagram.moveMode.node"),
      move: onNodeMove,
      title: t("workspace.diagram.moveMode.nodeTitle"),
    });
  }
  if (onNodeMoveKeepingDescendants) {
    modes.push({
      disabled: false,
      id: "fixed-descendants",
      label: t("workspace.diagram.moveMode.nodeOnly"),
      move: onNodeMoveKeepingDescendants,
      title: t("workspace.diagram.moveMode.nodeOnlyTitle"),
    });
  }
  if (onNodeMoveRelayoutDescendants) {
    modes.push({
      disabled: !canMoveRelayoutDescendants,
      id: "relayout-descendants",
      label: t("workspace.diagram.moveMode.relayoutDescendants"),
      move: onNodeMoveRelayoutDescendants,
      title: t("workspace.diagram.moveMode.relayoutDescendantsTitle"),
    });
  }
  return modes;
}

function diagramActiveToolbarMoveMode(modes: DiagramToolbarMoveMode[], selectedMoveMode: DiagramNodeMoveCommandKind): DiagramToolbarMoveMode | null {
  return modes.find((mode) => mode.id === selectedMoveMode && !mode.disabled) ?? modes.find((mode) => mode.id === "subtree" && !mode.disabled) ?? modes.find((mode) => !mode.disabled) ?? null;
}

export function diagramMoveImpactText(count: number, t: Translator): string {
  const safeCount = Number.isFinite(count) && count > 0 ? Math.round(count) : 0;
  return t(safeCount === 1 ? "workspace.diagram.moveImpactOne" : "workspace.diagram.moveImpactMany", { count: safeCount });
}

export function diagramMoveModeHintText(mode: DiagramNodeMoveCommandKind, t: Translator): string {
  if (mode === "subtree") {
    return t("workspace.diagram.moveModeHint.subtree");
  }
  if (mode === "fixed-descendants") {
    return t("workspace.diagram.moveModeHint.nodeOnly");
  }
  if (mode === "relayout-descendants") {
    return t("workspace.diagram.moveModeHint.relayoutDescendants");
  }
  return t("workspace.diagram.moveModeHint.node");
}

export function diagramMoveFootprintSummary(mode: DiagramNodeMoveCommandKind, affectedIds: Iterable<DiagramNodeId>, t: Translator): DiagramMoveFootprintSummary {
  const ids = Array.from(new Set(affectedIds));
  const label = diagramMoveModeLabel(mode, t);
  const impact = diagramMoveImpactText(ids.length, t);
  const hint = diagramMoveModeHintText(mode, t);
  return {
    affectedIds: ids,
    hint,
    impact,
    label,
    title: [label, impact, hint, ids.join(", ")].filter(Boolean).join(" · "),
  };
}

function diagramMoveModeLabel(mode: DiagramNodeMoveCommandKind, t: Translator): string {
  if (mode === "subtree") {
    return t("workspace.diagram.moveMode.subtree");
  }
  if (mode === "fixed-descendants") {
    return t("workspace.diagram.moveMode.nodeOnly");
  }
  if (mode === "relayout-descendants") {
    return t("workspace.diagram.moveMode.relayoutDescendants");
  }
  return t("workspace.diagram.moveMode.node");
}

function diagramMoveDirections(): Array<{
  delta: DiagramMoveDelta;
  icon: ReactNode;
  id: DiagramMoveDirection;
}> {
  return [
    {
      delta: { dx: 0, dy: -1 },
      icon: <ArrowUp aria-hidden="true" size={13} />,
      id: "up",
    },
    {
      delta: { dx: -1, dy: 0 },
      icon: <ArrowLeft aria-hidden="true" size={13} />,
      id: "left",
    },
    {
      delta: { dx: 1, dy: 0 },
      icon: <ArrowRight aria-hidden="true" size={13} />,
      id: "right",
    },
    {
      delta: { dx: 0, dy: 1 },
      icon: <ArrowDown aria-hidden="true" size={13} />,
      id: "down",
    },
  ];
}

function diagramMoveDirectionTitle(mode: DiagramNodeMoveCommandKind, direction: DiagramMoveDirection, t: Translator): string {
  return t(diagramMoveDirectionKeys[mode][direction]);
}

const diagramMoveDirectionKeys: Record<DiagramNodeMoveCommandKind, Record<DiagramMoveDirection, DiagramMoveDirectionTranslationKey>> = {
  "fixed-descendants": {
    down: "workspace.diagram.moveNodeOnlyDown",
    left: "workspace.diagram.moveNodeOnlyLeft",
    right: "workspace.diagram.moveNodeOnlyRight",
    up: "workspace.diagram.moveNodeOnlyUp",
  },
  node: {
    down: "workspace.diagram.moveDown",
    left: "workspace.diagram.moveLeft",
    right: "workspace.diagram.moveRight",
    up: "workspace.diagram.moveUp",
  },
  "relayout-descendants": {
    down: "workspace.diagram.moveRelayoutDescendantsDown",
    left: "workspace.diagram.moveRelayoutDescendantsLeft",
    right: "workspace.diagram.moveRelayoutDescendantsRight",
    up: "workspace.diagram.moveRelayoutDescendantsUp",
  },
  subtree: {
    down: "workspace.diagram.moveSubtreeDown",
    left: "workspace.diagram.moveSubtreeLeft",
    right: "workspace.diagram.moveSubtreeRight",
    up: "workspace.diagram.moveSubtreeUp",
  },
};

function DiagramNodeBox({ branchMember, dragGridDelta, dragOffset, draggable, dragging, gridSize, hasImage, imageUrl, lastClickAt, moveMode, moveAffected, node, onDragCancel, onDragEnd, onDragMove, onDragStart, onHoverEnd, onHoverMove, onMove, onMoveKeepingDescendants, onMoveRelayoutDescendants, onMoveSubtree, onModeCycle, onNodeClickAtChange, onOpen, onRemoveOnly, onRemoveSubtree, onSelect, relationshipPickCandidate = false, relationshipPickSource = false, searchCurrent, searchMatch, selected, t }: { branchMember: boolean; dragGridDelta?: DiagramMoveDelta; dragOffset?: CanvasPoint; draggable: boolean; dragging: boolean; gridSize: number; hasImage: boolean; imageUrl: string; lastClickAt: number; moveMode: DiagramNodeMoveCommandKind; moveAffected: boolean; node: ResolvedDiagramNode; onDragCancel: (event: PointerEvent<SVGGElement>, nodeId: DiagramNodeId) => void; onDragEnd: (event: PointerEvent<SVGGElement>, nodeId: DiagramNodeId) => void; onDragMove: (event: PointerEvent<SVGGElement>, nodeId: DiagramNodeId) => void; onDragStart: (event: PointerEvent<SVGGElement>, nodeId: DiagramNodeId) => void; onHoverEnd: () => void; onHoverMove: (event: PointerEvent<SVGGElement>, nodeId: DiagramNodeId) => void; onMove?: (nodeId: string, delta: DiagramMoveDelta) => void; onMoveKeepingDescendants?: (nodeId: string, delta: DiagramMoveDelta) => void; onMoveRelayoutDescendants?: (nodeId: string, delta: DiagramMoveDelta) => void; onMoveSubtree?: (nodeId: string, delta: DiagramMoveDelta) => void; onModeCycle?: (nodeId: string) => void; onNodeClickAtChange: (at: number) => void; onOpen?: (nodeId: string) => void; onRemoveOnly?: (nodeId: string) => void; onRemoveSubtree?: (nodeId: string) => void; onSelect?: (nodeId: string) => void; relationshipPickCandidate?: boolean; relationshipPickSource?: boolean; searchCurrent: boolean; searchMatch: boolean; selected: boolean; t: Translator }) {
  const x = node.worldX * gridSize + (dragOffset?.x ?? 0);
  const y = node.worldY * gridSize + (dragOffset?.y ?? 0);
  const width = node.width * gridSize;
  const height = node.height * gridSize;
  const label = compactLabel(node.title ?? node.id);
  const focusNode = isDiagramFocusNode(node);
  const technologyNode = isDiagramTechnologyNode(node);
  const visibleBox = diagramNodeVisibleBox(width, height, focusNode);
  const compactIconNode = isCompactDiagramIconNode(width, height, gridSize, focusNode || technologyNode);
  const imageSize = hasImage ? diagramNodeImageSize(width, height, focusNode, compactIconNode) : 0;
  const imageX = focusNode ? visibleBox.x + Math.max(0, (visibleBox.width - imageSize) / 2) : compactIconNode ? visibleBox.x + Math.max(4, (visibleBox.width - imageSize) / 2) : 8;
  const imageY = focusNode ? visibleBox.y + Math.max(0, (visibleBox.height - imageSize) / 2) : compactIconNode ? visibleBox.y + Math.max(4, (visibleBox.height - imageSize) / 2) : Math.max(8, (visibleBox.height - imageSize) / 2);
  const focusIconFramePadding = 4;
  const iconFrameClass = focusNode ? "project-diagram-focus-icon-frame" : "project-diagram-icon-frame";
  const nodeImageClass = ["project-diagram-node-image", focusNode ? "focus-icon" : compactIconNode ? "compact-icon" : ""].filter(Boolean).join(" ");
  const imagePreserveAspectRatio = focusNode || compactIconNode ? "xMidYMid meet" : "xMidYMid slice";
  const imagePlaceholderClass = ["project-diagram-node-image-placeholder", focusNode ? "focus-icon" : compactIconNode ? "compact-icon" : ""].filter(Boolean).join(" ");
  const labelX = imageSize > 0 ? imageX + imageSize + 8 : 10;
  const interactive = Boolean(onSelect);
  const classes = diagramNodeClassName({
    branchMember,
    draggable,
    dragging,
    focusNode,
    iconNode: technologyNode,
    interactive,
    mode: node.mode,
    moveAffected,
    relationshipPickCandidate,
    relationshipPickSource,
    searchCurrent,
    searchMatch,
    selected,
  });
  const coordinateBadgeTexts = selected && focusNode ? diagramFocusCoordinateBadges(diagramPreviewFocusCoordinateBadgeNode(node, dragGridDelta), t) : [];
  const canRemoveNodeOnly = Boolean(onRemoveOnly) && isDiagramFocusNode(node);
  const canRemoveSubtree = Boolean(onRemoveSubtree) && canRemoveDiagramFocusSubtree(node);
  const canMoveWithActiveMode = Boolean(onMove || onMoveSubtree || onMoveKeepingDescendants || onMoveRelayoutDescendants);
  const keyShortcuts = interactive ? [DIAGRAM_NODE_SELECT_KEYSHORTCUTS, canMoveWithActiveMode ? DIAGRAM_NODE_ARROW_KEYSHORTCUTS : "", onMoveSubtree ? DIAGRAM_NODE_SUBTREE_KEYSHORTCUTS : "", onMoveKeepingDescendants ? DIAGRAM_NODE_KEEP_DESCENDANTS_KEYSHORTCUTS : "", onMoveRelayoutDescendants ? DIAGRAM_NODE_RELAYOUT_DESCENDANTS_KEYSHORTCUTS : "", canRemoveNodeOnly ? DIAGRAM_NODE_REMOVE_KEYSHORTCUTS : "", canRemoveSubtree ? DIAGRAM_NODE_REMOVE_SUBTREE_KEYSHORTCUTS : ""].filter(Boolean).join(" ") : undefined;
  const handleSelect = () => onSelect?.(node.id);
  const handleOpen = () => {
    onSelect?.(node.id);
    onOpen?.(node.id);
  };
  const handleClick = (event: MouseEvent<SVGGElement>) => {
    const result = diagramNodeClickAction({
      eventDetail: event.detail,
      hasOpen: Boolean(onOpen),
      lastClickAt,
      now: event.timeStamp || performance.now(),
    });
    onNodeClickAtChange(result.lastClickAt);
    if (result.action === "open") {
      handleOpen();
      return;
    }
    handleSelect();
  };
  const showModeSwitch = selected && focusNode && Boolean(onModeCycle);
  const handlePointerCancel = (event: PointerEvent<SVGGElement>) => {
    onHoverEnd();
    if (draggable) {
      onDragCancel(event, node.id);
    }
  };
  const handlePointerDown = (event: PointerEvent<SVGGElement>) => {
    onHoverEnd();
    if (draggable) {
      onDragStart(event, node.id);
    }
  };
  const handlePointerMove = (event: PointerEvent<SVGGElement>) => {
    if (draggable) {
      onDragMove(event, node.id);
    }
    if (!dragging) {
      onHoverMove(event, node.id);
    }
  };
  const handlePointerUp = (event: PointerEvent<SVGGElement>) => {
    onHoverEnd();
    if (draggable) {
      onDragEnd(event, node.id);
    }
  };
  const handleKeyDown = (event: KeyboardEvent<SVGGElement>) => {
    if (event.key !== "Enter" && event.key !== " ") {
      const deleteCommand = diagramNodeDeleteCommand(event.key, event.shiftKey);
      if (deleteCommand) {
        const remove = deleteCommand.kind === "subtree" ? (canRemoveSubtree ? onRemoveSubtree : undefined) : canRemoveNodeOnly ? onRemoveOnly : undefined;
        if (!remove) {
          return;
        }
        event.preventDefault();
        event.stopPropagation();
        onSelect?.(node.id);
        remove(node.id);
        return;
      }
      const command = diagramNodeMoveCommand(event.key, event.shiftKey, event.altKey, event.metaKey, event.ctrlKey, moveMode);
      const move = command?.kind === "subtree" ? onMoveSubtree : command?.kind === "relayout-descendants" ? onMoveRelayoutDescendants : command?.kind === "fixed-descendants" ? onMoveKeepingDescendants : onMove;
      if (!command || !move) {
        return;
      }
      event.preventDefault();
      event.stopPropagation();
      onSelect?.(node.id);
      move(node.id, command.delta);
      return;
    }
    event.preventDefault();
    event.stopPropagation();
    handleSelect();
  };

  return (
    <g aria-label={node.title ?? node.id} aria-keyshortcuts={keyShortcuts} aria-pressed={interactive ? selected : undefined} className={classes} data-node-id={node.id} onClick={interactive && !draggable ? handleClick : undefined} onKeyDown={interactive ? handleKeyDown : undefined} onPointerCancel={handlePointerCancel} onPointerDown={handlePointerDown} onPointerLeave={onHoverEnd} onPointerMove={handlePointerMove} onPointerUp={handlePointerUp} role={interactive ? "button" : undefined} tabIndex={interactive ? 0 : undefined} transform={`translate(${x} ${y})`}>
      <title>{diagramNodeTooltipText(node, t)}</title>
      <rect className="project-diagram-node-hit-target" data-node-hit-id={node.id} height={visibleBox.height} rx="6" width={visibleBox.width} x={visibleBox.x} y={visibleBox.y} />
      {compactIconNode ? (
        <>
          {hasImage && !focusNode ? <rect className={iconFrameClass} height={imageSize + focusIconFramePadding * 2} rx="6" width={imageSize + focusIconFramePadding * 2} x={imageX - focusIconFramePadding} y={imageY - focusIconFramePadding} /> : null}
          {imageUrl ? <image aria-hidden="true" className={nodeImageClass} height={imageSize} href={imageUrl} preserveAspectRatio={imagePreserveAspectRatio} width={imageSize} x={imageX} y={imageY} /> : null}
          {hasImage && !imageUrl ? <DiagramNodeImagePlaceholder className={imagePlaceholderClass} height={imageSize} width={imageSize} x={imageX} y={imageY} /> : null}
        </>
      ) : focusNode ? (
        <>
          {imageUrl ? <image aria-hidden="true" className={nodeImageClass} height={imageSize} href={imageUrl} preserveAspectRatio={imagePreserveAspectRatio} width={imageSize} x={imageX} y={imageY} /> : null}
          {hasImage && !imageUrl ? <DiagramNodeImagePlaceholder className={imagePlaceholderClass} height={imageSize} width={imageSize} x={imageX} y={imageY} /> : null}
        </>
      ) : (
        <>
          {imageUrl ? <image aria-hidden="true" className={nodeImageClass} height={imageSize} href={imageUrl} preserveAspectRatio={imagePreserveAspectRatio} width={imageSize} x={imageX} y={imageY} /> : null}
          {hasImage && !imageUrl ? <DiagramNodeImagePlaceholder className={imagePlaceholderClass} height={imageSize} width={imageSize} x={imageX} y={imageY} /> : null}
          <text className="project-diagram-node-title" x={labelX} y="20">
            {label}
          </text>
          <text className="project-diagram-node-mode" x={labelX} y={Math.max(34, visibleBox.height - 9)}>
            {modeLabel(node.mode, t)}
          </text>
        </>
      )}
      {showModeSwitch && onModeCycle ? <DiagramNodeModeSwitch mode={node.mode} onCycle={() => onModeCycle(node.id)} t={t} visibleBox={visibleBox} /> : null}
      {coordinateBadgeTexts.length > 0 ? <DiagramFocusCoordinateBadges texts={coordinateBadgeTexts} visibleBox={visibleBox} /> : null}
    </g>
  );
}

function DiagramNodeModeSwitch({ mode, onCycle, t, visibleBox }: { mode: DiagramPositionMode; onCycle: () => void; t: Translator; visibleBox: DiagramNodeVisibleBox }) {
  const switchSize = Math.min(18, Math.max(12, Math.min(visibleBox.width, visibleBox.height)));
  const iconSize = Math.max(10, switchSize - 6);
  const iconOffset = (switchSize - iconSize) / 2;
  const x = visibleBox.x + visibleBox.width - switchSize;
  const y = visibleBox.y;
  const handleClick = (event: MouseEvent<SVGGElement>) => {
    event.preventDefault();
    event.stopPropagation();
    onCycle();
  };
  const handlePointerDown = (event: PointerEvent<SVGGElement>) => {
    event.stopPropagation();
  };
  const handleKeyDown = (event: KeyboardEvent<SVGGElement>) => {
    if (event.key !== "Enter" && event.key !== " ") {
      return;
    }
    event.preventDefault();
    event.stopPropagation();
    onCycle();
  };
  return (
    <g aria-label={t("workspace.diagram.modeControls")} className="project-diagram-node-mode-switch" data-node-mode-switch={mode} onClick={handleClick} onKeyDown={handleKeyDown} onPointerDown={handlePointerDown} role="button" tabIndex={0} transform={`translate(${formatViewBoxNumber(x)} ${formatViewBoxNumber(y)})`}>
      <title>{modeLabel(mode, t)}</title>
      <rect height={switchSize} rx="4" width={switchSize} x="0" y="0" />
      <g aria-hidden="true" className="project-diagram-node-mode-switch-icon" data-mode-switch-icon={mode} transform={`translate(${formatViewBoxNumber(iconOffset)} ${formatViewBoxNumber(iconOffset)})`}>
        {diagramNodeModeSwitchIcon(mode, iconSize)}
      </g>
    </g>
  );
}

function diagramNodeModeSwitchIcon(mode: DiagramPositionMode, size: number): ReactNode {
  if (mode === "absolute") {
    return <Pin aria-hidden="true" size={size} />;
  }
  if (mode === "relative") {
    return <GitBranch aria-hidden="true" size={size} />;
  }
  return <RefreshCw aria-hidden="true" size={size} />;
}

export function diagramNodeTooltipText(node: Pick<ResolvedDiagramNode, "dx" | "dy" | "height" | "id" | "mode" | "priority" | "subtreeCenterOffset" | "subtreeWidth" | "subtreeWidthDelta" | "title" | "width" | "worldX" | "worldY">, t?: Translator): string {
  const lines = [node.title ?? node.id, `${diagramHoverLabel("workspace.diagram.hoverId", "ID", t)} ${node.id}`, t ? `${diagramHoverLabel("workspace.diagram.hoverGrid", "Grid", t)} ${formatViewBoxNumber(node.worldX)}, ${formatViewBoxNumber(node.worldY)}` : `x ${formatViewBoxNumber(node.worldX)}, y ${formatViewBoxNumber(node.worldY)}`, t ? `${diagramHoverLabel("workspace.diagram.hoverMode", "Mode", t)} ${modeLabel(node.mode, t)}` : `mode ${node.mode}`, `${diagramHoverLabel("workspace.diagram.hoverSize", t ? "Size" : "size", t)} ${formatViewBoxNumber(node.width)} x ${formatViewBoxNumber(node.height)}`];
  if (node.dx !== undefined || node.dy !== undefined) {
    lines.push(t ? `${diagramHoverLabel("workspace.diagram.hoverOffset", "Offset", t)} ${formatViewBoxNumber(node.dx ?? 0)}, ${formatViewBoxNumber(node.dy ?? 0)}` : `dx ${formatViewBoxNumber(node.dx ?? 0)}, dy ${formatViewBoxNumber(node.dy ?? 0)}`);
  }
  for (const [key, fallback, value] of [
    ["workspace.diagram.hoverPriority", "priority", node.priority],
    ["workspace.diagram.hoverWidth", "w", node.subtreeWidth],
    ["workspace.diagram.hoverWidthDelta", "dw", node.subtreeWidthDelta],
    ["workspace.diagram.hoverCenter", "dc", node.subtreeCenterOffset],
  ] as const) {
    if (value !== undefined) {
      lines.push(`${diagramHoverLabel(key, fallback, t)} ${formatViewBoxNumber(value)}`);
    }
  }
  return lines.join("\n");
}

export function diagramNodeHoverCardRows(node: Pick<ResolvedDiagramNode, "dx" | "dy" | "height" | "id" | "mode" | "priority" | "subtreeCenterOffset" | "subtreeWidth" | "subtreeWidthDelta" | "width" | "worldX" | "worldY">, t?: Translator): DiagramNodeHoverCardRow[] {
  return [
    {
      label: diagramHoverLabel("workspace.diagram.hoverId", "ID", t),
      value: node.id,
    },
    {
      label: diagramHoverLabel("workspace.diagram.hoverGrid", "Grid", t),
      value: `${formatViewBoxNumber(node.worldX)}, ${formatViewBoxNumber(node.worldY)}`,
    },
    {
      label: diagramHoverLabel("workspace.diagram.hoverMode", "Mode", t),
      value: t ? modeLabel(node.mode, t) : node.mode,
    },
    {
      label: diagramHoverLabel("workspace.diagram.hoverSize", "Size", t),
      value: `${formatViewBoxNumber(node.width)} x ${formatViewBoxNumber(node.height)}`,
    },
    node.dx !== undefined || node.dy !== undefined
      ? {
          label: diagramHoverLabel("workspace.diagram.hoverOffset", "Offset", t),
          value: `${formatViewBoxNumber(node.dx ?? 0)}, ${formatViewBoxNumber(node.dy ?? 0)}`,
        }
      : null,
    node.priority !== undefined
      ? {
          label: diagramHoverLabel("workspace.diagram.hoverPriority", "Priority", t),
          value: formatViewBoxNumber(node.priority),
        }
      : null,
    node.subtreeWidth !== undefined
      ? {
          label: diagramHoverLabel("workspace.diagram.hoverWidth", "Width", t),
          value: formatViewBoxNumber(node.subtreeWidth),
        }
      : null,
    node.subtreeWidthDelta !== undefined
      ? {
          label: diagramHoverLabel("workspace.diagram.hoverWidthDelta", "Width delta", t),
          value: formatViewBoxNumber(node.subtreeWidthDelta),
        }
      : null,
    node.subtreeCenterOffset !== undefined
      ? {
          label: diagramHoverLabel("workspace.diagram.hoverCenter", "Center", t),
          value: formatViewBoxNumber(node.subtreeCenterOffset),
        }
      : null,
  ].filter((row): row is DiagramNodeHoverCardRow => Boolean(row));
}

function diagramHoverLabel(key: Parameters<Translator>[0], fallback: string, t?: Translator): string {
  return t ? t(key) : fallback;
}

function DiagramNodeHoverCard({ left, node, t, top }: { left: number; node: ResolvedDiagramNode; t: Translator; top: number }) {
  const rows = diagramNodeHoverCardRows(node, t);
  return (
    <aside aria-hidden="true" className="project-diagram-node-hover-card" style={{ left, top }}>
      <strong>{node.title ?? node.id}</strong>
      <dl>
        {rows.map((row) => (
          <div key={`${row.label}:${row.value}`}>
            <dt>{row.label}</dt>
            <dd>{row.value}</dd>
          </div>
        ))}
      </dl>
    </aside>
  );
}

function DiagramFocusCoordinateBadges({ texts, visibleBox }: { texts: string[]; visibleBox: DiagramNodeVisibleBox }) {
  const badgeHeight = 12;
  const badgeGap = 2;
  const y = visibleBox.y - (texts.length * badgeHeight + Math.max(0, texts.length - 1) * badgeGap + 4);
  return (
    <g aria-label={texts.join(" / ")} className="project-diagram-node-coordinate-badges" transform={`translate(${formatViewBoxNumber(visibleBox.x)} ${formatViewBoxNumber(y)})`}>
      {texts.map((text, index) => {
        const rowY = index * (badgeHeight + badgeGap);
        return (
          <g key={`${index}:${text}`}>
            <rect height={badgeHeight} rx="4" width={visibleBox.width} x="0" y={rowY} />
            <text lengthAdjust={text.length > 10 ? "spacingAndGlyphs" : undefined} textAnchor="middle" textLength={text.length > 10 ? Math.max(16, visibleBox.width - 8) : undefined} x={visibleBox.width / 2} y={rowY + 8.5}>
              {text}
            </text>
          </g>
        );
      })}
    </g>
  );
}

function DiagramNodeImagePlaceholder({ className, height, width, x, y }: { className: string; height: number; width: number; x: number; y: number }) {
  const midX = x + width / 2;
  const midY = y + height / 2;
  const arm = Math.max(5, Math.min(width, height) / 4);
  return (
    <g aria-hidden="true" className={className}>
      <rect height={height} rx="4" width={width} x={x} y={y} />
      <path d={`M ${formatViewBoxNumber(midX - arm)} ${formatViewBoxNumber(midY)} L ${formatViewBoxNumber(midX + arm)} ${formatViewBoxNumber(midY)} M ${formatViewBoxNumber(midX)} ${formatViewBoxNumber(midY - arm)} L ${formatViewBoxNumber(midX)} ${formatViewBoxNumber(midY + arm)}`} />
    </g>
  );
}

function diagramNodeImageSize(width: number, height: number, focusNode: boolean, compactIconNode = false): number {
  if (compactIconNode) {
    if (focusNode) {
      return Math.min(Math.max(24, Math.min(width, height) - 24), FOCUS_NODE_IMAGE_SIDE);
    }
    return Math.min(Math.max(8, Math.min(width, height) - 14), NODE_IMAGE_SIDE);
  }
  if (focusNode) {
    return Math.min(Math.max(24, Math.min(width, height) - 24), FOCUS_NODE_IMAGE_SIDE);
  }
  return Math.min(NON_FOCUS_NODE_IMAGE_SIDE, Math.max(18, height - 18));
}

function diagramNodeVisibleBox(width: number, height: number, focusNode: boolean): DiagramNodeVisibleBox {
  if (!focusNode) {
    return { height, width, x: 0, y: 0 };
  }
  const visible = {
    height: height * FOCUS_NODE_VISIBLE_RATIO,
    width: width * FOCUS_NODE_VISIBLE_RATIO,
  };
  return {
    ...visible,
    x: -visible.width / 2,
    y: -visible.height / 2,
  };
}

function diagramNodeVisibleGridBox(node: Pick<DiagramNode, "height" | "payload" | "width">): DiagramNodeVisibleBox {
  if (!isDiagramFocusNode(node)) {
    return { height: node.height, width: node.width, x: 0, y: 0 };
  }
  const visible = {
    height: node.height * FOCUS_NODE_VISIBLE_RATIO,
    width: node.width * FOCUS_NODE_VISIBLE_RATIO,
  };
  return {
    ...visible,
    x: -visible.width / 2,
    y: -visible.height / 2,
  };
}

export function diagramNodeRenderedImageSideLength(node: Pick<DiagramNode, "height" | "payload" | "width">, gridSize: number): number {
  const width = node.width * gridSize;
  const height = node.height * gridSize;
  const focusNode = isDiagramFocusNode(node);
  const technologyNode = isDiagramTechnologyNode(node);
  return diagramNodeImageSize(width, height, focusNode, isCompactDiagramIconNode(width, height, gridSize, focusNode || technologyNode));
}

function diagramGridPatternSizePx(document: Pick<DiagramDocument, "gridSizePx" | "nodes">): number {
  return document.nodes.some(isDiagramFocusNode) ? Math.max(1, document.gridSizePx / 2) : document.gridSizePx;
}

function diagramInitialViewportKey(document: Pick<DiagramDocument, "gridSizePx" | "nodes">): string {
  const firstNode = document.nodes[0];
  const lastNode = document.nodes[document.nodes.length - 1];
  return [document.gridSizePx, document.nodes.length, firstNode?.id ?? "", lastNode?.id ?? ""].join("\0");
}

function isCompactDiagramIconNode(width: number, height: number, gridSize: number, iconNode: boolean): boolean {
  return iconNode && width <= gridSize * 2 && height <= gridSize * 2;
}

function nodeImageHref(node: ResolvedDiagramNode, nodeImageUrls: Record<DiagramNodeId, string>, projectRoot: string): string {
  const imageUrl = node.imageUrl?.trim() ?? "";
  if (!imageUrl) {
    return "";
  }
  if (!projectRoot || isDirectDiagramImageUrl(imageUrl)) {
    return imageUrl;
  }
  return nodeImageUrls[node.id] ?? "";
}

function diagramChangedEntityForNode(entities: DiagramChangedEntity[], node: Pick<ResolvedDiagramNode, "id" | "payload">): DiagramChangedEntity | null {
  const candidates = diagramNodeEntityCandidates(node);
  return entities.find((entity) => candidates.has(entity.id)) ?? null;
}

function diagramNodeEntityCandidates(node: Pick<ResolvedDiagramNode, "id" | "payload">): Set<string> {
  const payload = diagramNodePayloadRecord(node.payload);
  return new Set([node.id, stringPayloadValue(payload?.itemId), stringPayloadValue(payload?.moduleId), stringPayloadValue(payload?.objectId), stringPayloadValue(payload?.embeddedId)].filter(Boolean));
}

function diagramSiblingReorderState(document: DiagramDocument, nodeId: DiagramNodeId): DiagramSiblingReorderState {
  const node = document.nodes.find((candidate) => candidate.id === nodeId);
  if (!node) {
    return {
      canReorderEarlier: false,
      canReorderLater: false,
      siblingCount: 0,
      siblingIds: [],
      siblingIndex: -1,
    };
  }
  const siblings = [...document.nodes.filter((candidate) => diagramParentKey(candidate.parentId) === diagramParentKey(node.parentId))].sort(compareDiagramSiblingOrder);
  const index = siblings.findIndex((candidate) => candidate.id === nodeId);
  return {
    canReorderEarlier: index > 0,
    canReorderLater: index >= 0 && index < siblings.length - 1,
    siblingCount: siblings.length,
    siblingIds: siblings.filter((sibling) => sibling.id !== nodeId).map((sibling) => sibling.id),
    siblingIndex: index,
  };
}

function diagramSubtreeNodes(document: DiagramDocument, nodeId: DiagramNodeId): DiagramNode[] {
  const byParent = diagramChildrenByParent(document.nodes);
  const root = document.nodes.find((node) => node.id === nodeId);
  if (!root) {
    return [];
  }
  const nodes = [root];
  for (let index = 0; index < nodes.length; index += 1) {
    nodes.push(...(byParent.get(nodes[index].id) ?? []));
  }
  return nodes;
}

function diagramNodeCanMoveRelayoutDescendants(document: DiagramDocument, nodeId: DiagramNodeId): boolean {
  return diagramSubtreeNodes(document, nodeId).some((node) => node.id !== nodeId);
}

function diagramChildrenByParent(nodes: DiagramNode[]): Map<DiagramNodeId, DiagramNode[]> {
  const byParent = new Map<DiagramNodeId, DiagramNode[]>();
  for (const node of nodes) {
    if (node.parentId) {
      byParent.set(node.parentId, [...(byParent.get(node.parentId) ?? []), node]);
    }
  }
  return byParent;
}

function diagramAncestorIds(document: DiagramDocument, nodeId: DiagramNodeId): DiagramNodeId[] {
  const nodesById = new Map(document.nodes.map((node) => [node.id, node]));
  const ids: DiagramNodeId[] = [];
  const seen = new Set<DiagramNodeId>([nodeId]);
  let current = nodesById.get(nodeId);
  while (current?.parentId && !seen.has(current.parentId)) {
    ids.unshift(current.parentId);
    seen.add(current.parentId);
    current = nodesById.get(current.parentId);
  }
  return ids;
}

function parentCandidateIds(document: DiagramDocument, nodeId: DiagramNodeId): DiagramNodeId[] {
  const blocked = new Set(diagramSubtreeNodes(document, nodeId).map((node) => node.id));
  return document.nodes
    .filter((node) => !blocked.has(node.id))
    .sort(compareDiagramSiblingOrder)
    .map((node) => node.id);
}

function relationshipCandidateNodes(nodes: ResolvedDiagramNode[], selectedNode: ResolvedDiagramNode): ResolvedDiagramNode[] {
  const selectedScope = diagramNodeRelationshipScopeKey(selectedNode);
  return nodes.filter((node) => node.id !== selectedNode.id && diagramNodeRelationshipScopeKey(node) === selectedScope);
}

function relationshipPickHintText(kind: DiagramRelationshipPickKind, t: Translator): string {
  if (kind === "dependency") {
    return t("workspace.diagram.pickDependencyHint");
  }
  if (kind === "unlock") {
    return t("workspace.diagram.pickUnlockHint");
  }
  return t("workspace.diagram.pickReferenceHint");
}

function canRemoveDiagramFocusSubtree(node: ResolvedDiagramNode): boolean {
  return isDiagramFocusNode(node);
}

function isDiagramFocusNode(node: Pick<DiagramNode, "payload">): boolean {
  if (!node.payload || typeof node.payload !== "object" || Array.isArray(node.payload)) {
    return false;
  }
  return (node.payload as Record<string, unknown>).embeddedKind === "focus";
}

function isDiagramTechnologyNode(node: Pick<DiagramNode, "payload">): boolean {
  const payload = diagramNodePayloadRecord(node.payload);
  return diagramNodeFamilyMatches(payload, "technology", "technologies");
}

function isDiagramFocusRootTemplateNode(node: Pick<DiagramNode, "payload">): boolean {
  const payload = diagramNodePayloadRecord(node.payload);
  if (payload?.embeddedKind === "focus") {
    return true;
  }
  return diagramNodeFamilyMatches(payload, "focus", "focuses", "focus-tree");
}

function diagramNodeFamilyMatches(payload: Record<string, unknown> | null, ...families: string[]): boolean {
  const accepted = new Set(families.map((family) => family.trim().toLowerCase().replace(/_/g, "-")));
  return [payload?.familyId, payload?.family].some((value) => typeof value === "string" && accepted.has(value.trim().toLowerCase().replace(/_/g, "-")));
}

function compareDiagramSiblingOrder(left: DiagramNode, right: DiagramNode): number {
  return left.order - right.order || left.id.localeCompare(right.id);
}

function diagramParentKey(parentId: DiagramNode["parentId"]): string {
  return parentId ?? "";
}

function pointerEventToSvgPoint(event: PointerEvent<SVGGElement>): CanvasPoint | null {
  const svg = event.currentTarget.ownerSVGElement;
  const matrix = svg?.getScreenCTM();
  if (!svg || !matrix) {
    return null;
  }
  const point = svg.createSVGPoint();
  point.x = event.clientX;
  point.y = event.clientY;
  const transformed = point.matrixTransform(matrix.inverse());
  return { x: transformed.x, y: transformed.y };
}

function pointerEventToRootSvgPoint<T extends SVGElement>(event: PointerEvent<T>): CanvasPoint | null {
  const svg = event.currentTarget instanceof SVGSVGElement ? event.currentTarget : event.currentTarget.ownerSVGElement;
  if (!svg) {
    return null;
  }
  return clientPointToRootSvgPoint(svg, event.clientX, event.clientY);
}

function pointerEventToClientPoint(event: Pick<PointerEvent<Element>, "clientX" | "clientY">): CanvasPoint {
  return { x: event.clientX, y: event.clientY };
}

function wheelEventToRootSvgPoint(event: Pick<WheelEvent, "clientX" | "clientY">, svg: SVGSVGElement | null): CanvasPoint | null {
  if (!svg) {
    return null;
  }
  if (!diagramWheelClientPointInsideRect(event, svg.getBoundingClientRect())) {
    return null;
  }
  return clientPointToRootSvgPoint(svg, event.clientX, event.clientY);
}

function clientPointToRootSvgPoint(svg: SVGSVGElement, clientX: number, clientY: number): CanvasPoint | null {
  const matrix = svg.getScreenCTM();
  if (!matrix) {
    return null;
  }
  const point = svg.createSVGPoint();
  point.x = clientX;
  point.y = clientY;
  const transformed = point.matrixTransform(matrix.inverse());
  return { x: transformed.x, y: transformed.y };
}

function releasePointerCapture<T extends SVGElement>(event: PointerEvent<T>): void {
  if (event.currentTarget.hasPointerCapture(event.pointerId)) {
    event.currentTarget.releasePointerCapture(event.pointerId);
  }
}

export function projectDiagram(document: DiagramDocument, preview?: DiagramProjectionPreview): DiagramProjection {
  const resolved = resolveDiagramLayout(document);
  const gridSize = document.gridSizePx;
  const edgeNodesById = previewProjectedNodesById(resolved.nodesById, gridSize, preview);
  const bounds = resolved.nodes.reduce(
    (current, node) => {
      const visibleBox = diagramNodeVisibleGridBox(node);
      return {
        minX: Math.min(current.minX, node.worldX + visibleBox.x),
        minY: Math.min(current.minY, node.worldY + visibleBox.y),
        maxX: Math.max(current.maxX, node.worldX + visibleBox.x + visibleBox.width),
        maxY: Math.max(current.maxY, node.worldY + visibleBox.y + visibleBox.height),
      };
    },
    {
      minX: Number.POSITIVE_INFINITY,
      minY: Number.POSITIVE_INFINITY,
      maxX: Number.NEGATIVE_INFINITY,
      maxY: Number.NEGATIVE_INFINITY,
    },
  );
  const viewX = bounds.minX * gridSize - VIEW_PADDING;
  const viewY = bounds.minY * gridSize - VIEW_PADDING;
  const viewWidth = Math.max((bounds.maxX - bounds.minX) * gridSize + VIEW_PADDING * 2, MIN_VIEW_WIDTH);
  const viewHeight = Math.max((bounds.maxY - bounds.minY) * gridSize + VIEW_PADDING * 2, MIN_VIEW_HEIGHT);

  return {
    nodes: resolved.nodes,
    edges: projectEdges(document.edges, edgeNodesById, gridSize),
    viewBox: `${viewX} ${viewY} ${viewWidth} ${viewHeight}`,
  };
}

function previewProjectedNodesById(nodesById: Record<string, ResolvedDiagramNode>, gridSize: number, preview: DiagramProjectionPreview | undefined): Record<string, ResolvedDiagramNode> {
  if (!preview || (preview.offset.x === 0 && preview.offset.y === 0)) {
    return nodesById;
  }
  const ids = new Set(preview.nodeIds);
  if (ids.size === 0) {
    return nodesById;
  }
  const dx = preview.offset.x / gridSize;
  const dy = preview.offset.y / gridSize;
  const next = { ...nodesById };
  for (const id of ids) {
    const node = nodesById[id];
    if (!node) {
      continue;
    }
    next[id] = {
      ...node,
      subtreeBounds: {
        minX: node.subtreeBounds.minX + dx,
        minY: node.subtreeBounds.minY + dy,
        maxX: node.subtreeBounds.maxX + dx,
        maxY: node.subtreeBounds.maxY + dy,
      },
      worldX: node.worldX + dx,
      worldY: node.worldY + dy,
    };
  }
  return next;
}

function projectEdges(edges: DiagramEdge[], nodesById: Record<string, ResolvedDiagramNode>, gridSize: number): ProjectedEdge[] {
  const focusTreePairs = new Set(
    edges
      .filter((edge) => {
        const source = nodesById[edge.source];
        const target = nodesById[edge.target];
        return edge.kind === "tree" && source && target && isDiagramFocusNode(source) && isDiagramFocusNode(target);
      })
      .map((edge) => diagramEdgePairKey(edge)),
  );
  return edges.flatMap((edge) => {
    if (edge.kind === "dependency" && focusTreePairs.has(diagramEdgePairKey(edge))) {
      return [];
    }
    return projectEdge(edge, nodesById, gridSize);
  });
}

function diagramEdgePairKey(edge: Pick<DiagramEdge, "source" | "target">): string {
  return `${edge.source}\u0000${edge.target}`;
}

function projectEdge(edge: DiagramEdge, nodesById: Record<string, ResolvedDiagramNode>, gridSize: number): ProjectedEdge[] {
  const source = nodesById[edge.source];
  const target = nodesById[edge.target];
  if (!source || !target) {
    return [];
  }
  if (isDiagramFocusNode(source) && isDiagramFocusNode(target)) {
    return [
      {
        ...edge,
        path: edge.kind === "reference" ? focusReferenceEdgePath(source, target, gridSize) : focusTreeEdgePath(edge, source, target, gridSize),
      },
    ];
  }
  const x1 = (source.worldX + source.width / 2) * gridSize;
  const y1 = (source.worldY + source.height) * gridSize;
  const x2 = (target.worldX + target.width / 2) * gridSize;
  const y2 = target.worldY * gridSize;
  const offset = edge.kind === "dependency" ? 6 : edge.kind === "path" ? -6 : 0;
  const midY = (y1 + y2) / 2;
  return [
    {
      ...edge,
      path: `M ${x1 + offset} ${y1} C ${x1 + offset} ${midY}, ${x2 + offset} ${midY}, ${x2 + offset} ${y2}`,
    },
  ];
}

function focusTreeEdgePath(edge: DiagramEdge, source: ResolvedDiagramNode, target: ResolvedDiagramNode, gridSize: number): string {
  const sourceBox = diagramNodeVisibleGridBox(source);
  const targetBox = diagramNodeVisibleGridBox(target);
  const offset = edge.kind === "dependency" ? 6 : edge.kind === "path" ? -6 : 0;
  const x1 = (source.worldX + sourceBox.x + sourceBox.width / 2) * gridSize + offset;
  const y1 = (source.worldY + sourceBox.y + sourceBox.height) * gridSize;
  const x2 = (target.worldX + targetBox.x + targetBox.width / 2) * gridSize + offset;
  const y2 = (target.worldY + targetBox.y) * gridSize;
  const midY = (y1 + y2) / 2;
  return `M ${formatViewBoxNumber(x1)} ${formatViewBoxNumber(y1)} L ${formatViewBoxNumber(x1)} ${formatViewBoxNumber(midY)} L ${formatViewBoxNumber(x2)} ${formatViewBoxNumber(midY)} L ${formatViewBoxNumber(x2)} ${formatViewBoxNumber(y2)}`;
}

function focusReferenceEdgePath(source: ResolvedDiagramNode, target: ResolvedDiagramNode, gridSize: number): string {
  const sourceBox = diagramNodeVisibleGridBox(source);
  const targetBox = diagramNodeVisibleGridBox(target);
  const sourceCenterX = source.worldX + sourceBox.x + sourceBox.width / 2;
  const sourceCenterY = source.worldY + sourceBox.y + sourceBox.height / 2;
  const targetCenterX = target.worldX + targetBox.x + targetBox.width / 2;
  const targetCenterY = target.worldY + targetBox.y + targetBox.height / 2;
  const sourceX = sourceCenterX <= targetCenterX ? source.worldX + sourceBox.x + sourceBox.width : source.worldX + sourceBox.x;
  const targetX = sourceCenterX <= targetCenterX ? target.worldX + targetBox.x : target.worldX + targetBox.x + targetBox.width;
  const sourceY = sourceCenterY;
  const targetY = targetCenterY;
  return `M ${formatViewBoxNumber(sourceX * gridSize)} ${formatViewBoxNumber(sourceY * gridSize)} L ${formatViewBoxNumber(targetX * gridSize)} ${formatViewBoxNumber(targetY * gridSize)}`;
}

export function diagramKeyboardShortcut(key: string, step: number): DiagramKeyboardShortcut {
  switch (key) {
    case "ArrowUp":
      return { delta: { x: 0, y: -step }, kind: "pan" };
    case "ArrowDown":
      return { delta: { x: 0, y: step }, kind: "pan" };
    case "ArrowLeft":
      return { delta: { x: -step, y: 0 }, kind: "pan" };
    case "ArrowRight":
      return { delta: { x: step, y: 0 }, kind: "pan" };
    case "+":
    case "=":
      return { delta: 1, kind: "zoom" };
    case "-":
    case "_":
      return { delta: -1, kind: "zoom" };
    case "0":
    case "Escape":
      return { kind: "fit" };
    default:
      return { kind: "none" };
  }
}

export function diagramCanvasEditCommand(key: string, metaKey: boolean, ctrlKey: boolean, shiftKey: boolean): DiagramCanvasEditCommand | null {
  if (!metaKey && !ctrlKey) {
    return null;
  }
  const commandKey = key.toLocaleLowerCase();
  if (commandKey === "z") {
    return { kind: shiftKey ? "redo" : "undo" };
  }
  if (commandKey === "y") {
    return { kind: "redo" };
  }
  if (commandKey === "s" && !shiftKey) {
    return { kind: "apply" };
  }
  return null;
}

export function diagramNodeMoveShortcut(key: string): DiagramMoveDelta | null {
  switch (key) {
    case "ArrowUp":
      return { dx: 0, dy: -1 };
    case "ArrowDown":
      return { dx: 0, dy: 1 };
    case "ArrowLeft":
      return { dx: -1, dy: 0 };
    case "ArrowRight":
      return { dx: 1, dy: 0 };
    default:
      return null;
  }
}

export function diagramNodeMoveCommand(key: string, shiftKey: boolean, altKey: boolean, metaKey = false, ctrlKey = false, defaultKind: DiagramNodeMoveCommandKind = "node"): DiagramNodeMoveCommand | null {
  const delta = diagramNodeMoveShortcut(key);
  if (!delta) {
    return null;
  }
  return {
    delta,
    kind: diagramDragMoveCommand(shiftKey, altKey, metaKey, ctrlKey, defaultKind),
  };
}

export function diagramNodeDeleteCommand(key: string, shiftKey: boolean): DiagramNodeDeleteCommand | null {
  if (key !== "Delete" && key !== "Backspace") {
    return null;
  }
  return { kind: shiftKey ? "subtree" : "node" };
}

export function diagramDragMoveCommand(shiftKey: boolean, altKey: boolean, metaKey = false, ctrlKey = false, defaultKind: DiagramNodeMoveCommandKind = "node"): DiagramNodeMoveCommandKind {
  if (shiftKey) {
    return "subtree";
  }
  if (metaKey || ctrlKey) {
    return "relayout-descendants";
  }
  if (altKey) {
    return "fixed-descendants";
  }
  return defaultKind;
}

export function diagramDragPreviewDocument(document: DiagramDocument, nodeId: DiagramNodeId, command: DiagramNodeMoveCommandKind, delta: DiagramMoveDelta): DiagramDocument {
  if (command !== "relayout-descendants" || (delta.dx === 0 && delta.dy === 0)) {
    return document;
  }
  return moveDiagramNodeRelayoutDescendants(document, nodeId, delta);
}

export function diagramDragPreviewNodeIds(document: DiagramDocument, nodeId: DiagramNodeId, command: DiagramNodeMoveCommandKind): DiagramNodeId[] {
  const nodesById = new Map(document.nodes.map((node) => [node.id, node]));
  const root = nodesById.get(nodeId);
  if (!root) {
    return [];
  }
  if (command === "fixed-descendants") {
    return [nodeId];
  }
  const childrenByParent = diagramChildrenByParent(document.nodes);
  const ids: DiagramNodeId[] = [];
  const visit = (id: DiagramNodeId, includeAbsoluteDescendants: boolean) => {
    const node = nodesById.get(id);
    if (!node) {
      return;
    }
    ids.push(id);
    for (const child of childrenByParent.get(id) ?? []) {
      if (includeAbsoluteDescendants || child.mode !== "absolute") {
        visit(child.id, includeAbsoluteDescendants);
      }
    }
  };
  visit(nodeId, command === "subtree" || command === "relayout-descendants");
  return ids;
}

function diagramDragHintLabels(options: DiagramDragHintOptions, t: Translator): string[] {
  const labels: string[] = [];
  if (options.activeMoveMode === "subtree" && options.canMoveSubtree) {
    labels.push(t("workspace.diagram.dragHint.activeSubtree"));
  } else if (options.activeMoveMode === "fixed-descendants" && options.canMoveKeepingDescendants) {
    labels.push(t("workspace.diagram.dragHint.activeNodeOnly"));
  } else if (options.activeMoveMode === "relayout-descendants" && options.canMoveRelayoutDescendants) {
    labels.push(t("workspace.diagram.dragHint.activeRelayoutDescendants"));
  } else if (options.canMoveNode) {
    labels.push(t("workspace.diagram.dragHint.node"));
  }
  if (options.canMoveSubtree && options.activeMoveMode !== "subtree") {
    labels.push(t("workspace.diagram.dragHint.subtree"));
  }
  if (options.canMoveKeepingDescendants && options.activeMoveMode !== "fixed-descendants") {
    labels.push(t("workspace.diagram.dragHint.nodeOnly"));
  }
  if (options.canMoveRelayoutDescendants && options.activeMoveMode !== "relayout-descendants") {
    labels.push(t("workspace.diagram.dragHint.relayoutDescendants"));
  }
  return labels;
}

export function searchDiagramNodes<T extends SearchableDiagramNode>(nodes: T[], query: string): T[] {
  const needle = query.trim().toLocaleLowerCase();
  if (!needle) {
    return [];
  }
  return nodes.filter((node) => [node.id, node.title ?? "", diagramNodeSourcePath(node.payload)].some((value) => value.toLocaleLowerCase().includes(needle)));
}

export function diagramSearchViewportTarget<T extends SearchableDiagramViewportNode>(nodes: T[], query: string, viewBox: string, gridSizePx: number): { index: number; nodeId: DiagramNodeId; panOffset: CanvasPoint } | null {
  const [node] = searchDiagramNodes(nodes, query);
  if (!node) {
    return null;
  }
  return {
    index: 0,
    nodeId: node.id,
    panOffset: panOffsetToCenterNode(viewBox, node, gridSizePx),
  };
}

export function diagramModeCounts(nodes: Array<Pick<ResolvedDiagramNode, "mode">>): DiagramModeCounts {
  const counts: DiagramModeCounts = { absolute: 0, auto: 0, relative: 0 };
  for (const node of nodes) {
    counts[node.mode] += 1;
  }
  return counts;
}

export function diagramEdgeCounts(edges: Array<Pick<DiagramEdge, "kind">>): DiagramEdgeCounts {
  const counts: DiagramEdgeCounts = {
    dependency: 0,
    path: 0,
    reference: 0,
    tree: 0,
  };
  for (const edge of edges) {
    counts[edge.kind] += 1;
  }
  return counts;
}

export function diagramStoredPositionText(node: DiagramStoredPositionNode, t: Translator): string {
  if (node.mode === "absolute") {
    return t("workspace.diagram.selectedStoredAbsolute", {
      x: formatViewBoxNumber(numberOrFallback(node.x, node.worldX)),
      y: formatViewBoxNumber(numberOrFallback(node.y, node.worldY)),
    });
  }
  if (node.mode === "relative") {
    const values = {
      dx: formatViewBoxNumber(numberOrFallback(node.dx, node.worldX)),
      dy: formatViewBoxNumber(numberOrFallback(node.dy, node.worldY)),
      parent: node.parentId ?? "",
    };
    return node.parentId ? t("workspace.diagram.selectedStoredRelative", values) : t("workspace.diagram.selectedStoredRelativeRoot", values);
  }
  return node.parentId ? t("workspace.diagram.selectedStoredAuto") : t("workspace.diagram.selectedStoredAutoRoot");
}

export function diagramFocusCoordinateBadges(node: DiagramFocusCoordinateBadgeNode, t: Translator): string[] {
  const badges = [
    t("workspace.diagram.focusGridBadge", {
      x: formatViewBoxNumber(node.worldX),
      y: formatViewBoxNumber(node.worldY),
    }),
  ];
  const dx = typeof node.dx === "number" && Number.isFinite(node.dx) ? node.dx : undefined;
  const dy = typeof node.dy === "number" && Number.isFinite(node.dy) ? node.dy : undefined;
  if ((node.mode === "relative" || node.relativePositionKind === "legacy_offset") && dx !== undefined && dy !== undefined) {
    badges.push(
      t("workspace.diagram.focusRelativeBadge", {
        dx: formatSignedGridNumber(dx),
        dy: formatSignedGridNumber(dy),
      }),
    );
  }
  return badges;
}

export function diagramPreviewFocusCoordinateBadgeNode(node: DiagramFocusCoordinateBadgeNode, dragGridDelta?: DiagramMoveDelta | null): DiagramFocusCoordinateBadgeNode {
  if (!dragGridDelta || (dragGridDelta.dx === 0 && dragGridDelta.dy === 0)) {
    return node;
  }
  const previewNode: DiagramFocusCoordinateBadgeNode = {
    ...node,
    worldX: node.worldX + dragGridDelta.dx,
    worldY: node.worldY + dragGridDelta.dy,
  };
  const dx = typeof node.dx === "number" && Number.isFinite(node.dx) ? node.dx : undefined;
  const dy = typeof node.dy === "number" && Number.isFinite(node.dy) ? node.dy : undefined;
  if ((node.mode === "relative" || node.relativePositionKind === "legacy_offset") && dx !== undefined && dy !== undefined) {
    previewNode.dx = dx + dragGridDelta.dx;
    previewNode.dy = dy + dragGridDelta.dy;
  }
  return previewNode;
}

export function diagramNodeRelationships(edges: DiagramEdge[], nodeId: DiagramNodeId): DiagramNodeRelationships {
  const relationships = emptyDiagramNodeRelationships();
  for (const edge of edges) {
    const relationshipKind = edge.relationshipKind?.trim() ?? "";
    const relationshipLabel = edge.label?.trim() ?? "";
    if ((relationshipKind || relationshipLabel) && (edge.source === nodeId || edge.target === nodeId)) {
      const relatedId = edge.source === nodeId ? edge.target : edge.source;
      if (relatedId !== nodeId && !relationships.exactLinks.some((link) => link.edgeId === edge.id && link.relatedId === relatedId)) {
        relationships.exactLinks.push({
          edgeId: edge.id,
          label: relationshipLabel || relationshipKind,
          relatedId,
          relationshipKind,
          sourceId: edge.source,
          targetId: edge.target,
        });
      }
    }
    if (relationshipKind === "all_parent" || relationshipKind === "any_parent" || relationshipKind === "mutually_exclusive" || relationshipKind === "relative_position") {
      continue;
    }
    if (edge.kind === "dependency") {
      if (edge.target === nodeId) {
        addUniqueId(relationships.prerequisites, edge.source, nodeId);
      }
      if (edge.source === nodeId) {
        addUniqueId(relationships.unlocks, edge.target, nodeId);
      }
      continue;
    }
    if (edge.kind === "path") {
      if (edge.source === nodeId) {
        addUniqueId(relationships.unlocks, edge.target, nodeId);
      }
      continue;
    }
    if (edge.kind === "reference") {
      if (edge.source === nodeId) {
        addReferenceLink(relationships, edge.target, edge.source, edge.target, nodeId);
      } else if (edge.target === nodeId) {
        addReferenceLink(relationships, edge.source, edge.source, edge.target, nodeId);
      }
    }
  }
  return relationships;
}

function diagramDependencyReachableIds(edges: DiagramEdge[], nodeId: DiagramNodeId): DiagramNodeId[] {
  const targetsBySource = new Map<DiagramNodeId, DiagramNodeId[]>();
  for (const edge of edges) {
    if (edge.kind !== "dependency") {
      continue;
    }
    targetsBySource.set(edge.source, [...(targetsBySource.get(edge.source) ?? []), edge.target]);
  }

  const reachable: DiagramNodeId[] = [];
  const seen = new Set<DiagramNodeId>();
  const pending = [...(targetsBySource.get(nodeId) ?? [])];
  while (pending.length > 0) {
    const id = pending.pop();
    if (!id || seen.has(id)) {
      continue;
    }
    seen.add(id);
    reachable.push(id);
    pending.push(...(targetsBySource.get(id) ?? []));
  }
  return reachable;
}

export function diagramSearchKeyAction(key: string, shiftKey: boolean): DiagramSearchKeyAction {
  if (key === "Enter") {
    return { kind: shiftKey ? "previous" : "next" };
  }
  if (key === "Escape") {
    return { kind: "clear" };
  }
  return { kind: "none" };
}

export function diagramNodeClassName({ branchMember = false, draggable, dragging, focusNode, iconNode = false, interactive, mode, moveAffected = false, relationshipPickCandidate = false, relationshipPickSource = false, searchCurrent, searchMatch, selected }: DiagramNodeClassOptions): string {
  return ["project-diagram-node", focusNode ? "focus-node" : "", iconNode ? "icon-node" : "", branchMember ? "branch-member" : "", moveAffected ? "move-affected" : "", relationshipPickCandidate ? "relationship-pick-candidate" : "", relationshipPickSource ? "relationship-pick-source" : "", selected ? "selected" : "", mode, interactive ? "interactive" : "", draggable ? "draggable" : "", dragging ? "dragging" : "", searchMatch ? "search-match" : "", searchCurrent ? "search-current" : ""].filter(Boolean).join(" ");
}

export function diagramMiniMapNodeClassName({ moveAffected = false, searchCurrent, searchMatch, selected }: DiagramMiniMapNodeClassOptions): string {
  return ["project-diagram-minimap-node", moveAffected ? "move-affected" : "", selected ? "selected" : "", searchMatch ? "search-match" : "", searchCurrent ? "search-current" : ""].filter(Boolean).join(" ");
}

export function diagramEdgeClassName(edge: DiagramEdge, selectedNodeId: string, previewNodeIds?: ReadonlySet<DiagramNodeId> | null, branchNodeIds?: ReadonlySet<DiagramNodeId> | null, moveAffectedNodeIds?: ReadonlySet<DiagramNodeId> | null): string {
  const selected = selectedNodeId.trim();
  const connected = selected && (edge.source === selected || edge.target === selected);
  const distant = selected && !connected;
  const preview = Boolean(previewNodeIds?.has(edge.source) && previewNodeIds.has(edge.target));
  const branchMember = Boolean(branchNodeIds?.has(edge.source) && branchNodeIds.has(edge.target));
  const moveAffected = Boolean(moveAffectedNodeIds?.has(edge.source) && moveAffectedNodeIds.has(edge.target));
  return ["project-diagram-edge", edge.kind, edge.relationshipKind ? `relationship-${edge.relationshipKind.replace(/_/g, "-")}` : "", connected ? "connected" : "", distant ? "distant" : "", branchMember ? "branch-member" : "", moveAffected ? "move-affected" : "", preview ? "preview" : "", connected && edge.source === selected ? "outgoing" : "", connected && edge.target === selected ? "incoming" : ""].filter(Boolean).join(" ");
}

function wrapIndex(index: number, length: number): number {
  if (length <= 0) {
    return -1;
  }
  return ((index % length) + length) % length;
}

function clampNumber(value: number, min: number, max: number): number {
  if (!Number.isFinite(value)) {
    return min;
  }
  return Math.max(min, Math.min(max, value));
}

function diagramStats(document: DiagramDocument, t: Translator): string {
  const nodeLabel = document.nodes.length === 1 ? t("workspace.diagram.node") : t("workspace.diagram.nodes");
  const edgeLabel = document.edges.length === 1 ? t("workspace.diagram.link") : t("workspace.diagram.links");
  return `${document.nodes.length} ${nodeLabel} / ${document.edges.length} ${edgeLabel}`;
}

function diagramImageLoadStateForTargetCount(total: number): DiagramImageLoadState {
  return total > 0 ? { completed: 0, hydrated: 0, status: "loading", total } : { completed: 0, hydrated: 0, status: "idle", total: 0 };
}

function diagramImageLoadStateForProgress(progress: DiagramImageLoadProgress): DiagramImageLoadState {
  return {
    ...progress,
    status: progress.completed >= progress.total ? "done" : "loading",
  };
}

function diagramImageLoadStatusText(state: DiagramImageLoadState, t: Translator): string {
  if (state.total <= 0) {
    return "";
  }
  return t("workspace.diagram.imagesProgress", {
    hydrated: String(state.hydrated),
    total: String(state.total),
  });
}

export function diagramImageLoadStatusTitle(state: DiagramImageLoadState, t: Translator): string {
  if (state.total <= 0) {
    return "";
  }
  return t("workspace.diagram.imagesProgressTitle", {
    completed: String(state.completed),
    hydrated: String(state.hydrated),
    total: String(state.total),
  });
}

export function diagramImageLoadStatusClassName(state: DiagramImageLoadState): string {
  return ["project-diagram-image-status", diagramImageLoadStatusTone(state)].filter(Boolean).join(" ");
}

function diagramImageLoadStatusTone(state: DiagramImageLoadState): "loading" | "partial" | "ready" | "" {
  if (state.total <= 0) {
    return "";
  }
  if (state.status === "loading") {
    return "loading";
  }
  return state.hydrated >= state.total ? "ready" : "partial";
}

function modeLabel(mode: ResolvedDiagramNode["mode"], t: Translator): string {
  if (mode === "absolute") {
    return t("workspace.diagram.mode.absolute");
  }
  if (mode === "relative") {
    return t("workspace.diagram.mode.relative");
  }
  return t("workspace.diagram.mode.auto");
}

function edgeKindLabel(kind: DiagramEdgeKind, t: Translator): string {
  if (kind === "tree") {
    return t("workspace.diagram.edge.tree");
  }
  if (kind === "dependency") {
    return t("workspace.diagram.edge.dependency");
  }
  if (kind === "path") {
    return t("workspace.diagram.edge.path");
  }
  return t("workspace.diagram.edge.reference");
}

function emptyDiagramNodeRelationships(): DiagramNodeRelationships {
  return {
    exactLinks: [],
    prerequisites: [],
    references: [],
    referenceLinks: [],
    unlocks: [],
  };
}

function addReferenceLink(relationships: DiagramNodeRelationships, relatedId: string, sourceId: string, targetId: string, selfId: string): void {
  addUniqueId(relationships.references, relatedId, selfId);
  if (relatedId === selfId || relationships.referenceLinks.some((link) => link.relatedId === relatedId && link.sourceId === sourceId && link.targetId === targetId)) {
    return;
  }
  relationships.referenceLinks.push({ relatedId, sourceId, targetId });
}

function addUniqueId(ids: string[], id: string, selfId: string): void {
  if (id !== selfId && !ids.includes(id)) {
    ids.push(id);
  }
}

function diagramNodeCandidate(node: Pick<ResolvedDiagramNode, "id" | "title">): DiagramCandidate {
  return { id: node.id, title: node.title?.trim() || node.id };
}

function candidatesByIds(ids: string[], candidatesById: Map<string, DiagramCandidate>): DiagramCandidate[] {
  return ids.map((id) => candidatesById.get(id) ?? { id, title: id });
}

function withoutCandidates(candidates: DiagramCandidate[], excludedIds: string[]): DiagramCandidate[] {
  const excluded = new Set(excludedIds);
  return candidates.filter((candidate) => !excluded.has(candidate.id));
}

export function diagramCandidateIdFromInput(candidates: DiagramCandidate[], value: string): string {
  const id = value.trim();
  return id && candidates.some((candidate) => candidate.id === id) ? id : "";
}

function candidateDisplayText(candidate: DiagramCandidate): string {
  return candidate.title === candidate.id ? candidate.id : `${candidate.id} - ${candidate.title}`;
}

function candidateOptionLabel(candidate: DiagramCandidate): string {
  return candidate.title === candidate.id ? candidate.id : candidate.title;
}

function diagramNodeSourcePath(payload: unknown): string {
  if (!payload || typeof payload !== "object" || Array.isArray(payload)) {
    return "";
  }
  const record = payload as Record<string, unknown>;
  return stringPayloadValue(record.sourceRootRelativePath) || stringPayloadValue(record.relativeRoot);
}

export function diagramNodePositionEditable(payload: unknown): boolean {
  return diagramNodePayloadRecord(payload)?.editable !== false;
}

export function diagramNodeEditableSourcePath(payload: unknown): string {
  const record = diagramNodePayloadRecord(payload);
  return cleanDiagramSourcePath(stringPayloadValue(record?.sourcePath) || stringPayloadValue(record?.source_path));
}

function cleanDiagramSourcePath(value: string): string {
  const clean = value.replace(/\\/g, "/").replace(/^\/+/, "").replace(/\/+$/, "");
  if (!clean || clean.includes("://")) {
    return "";
  }
  const parts = clean.split("/");
  return parts.some((part) => !part || part === "." || part === "..") ? "" : parts.join("/");
}

function diagramSelectionFacts(node: ResolvedDiagramNode, t: Translator): DiagramSelectionFact[] {
  const payload = diagramNodePayloadRecord(node.payload);
  const facts: DiagramSelectionFact[] = [
    {
      label: t("workspace.diagram.selectedKind"),
      value: diagramNodeKindLabel(payload, t),
    },
    {
      label: t("workspace.diagram.selectedStoredPosition"),
      value: diagramStoredPositionText(node, t),
    },
    {
      label: t("workspace.diagram.selectedSize"),
      value: `${formatViewBoxNumber(node.width)} x ${formatViewBoxNumber(node.height)}`,
    },
  ];
  appendDiagramNumberFact(facts, t("workspace.diagram.selectedPriority"), node.priority);
  appendDiagramNumberFact(facts, t("workspace.diagram.selectedSubtreeWidth"), node.subtreeWidth);
  appendDiagramNumberFact(facts, t("workspace.diagram.selectedSubtreeWidthDelta"), node.subtreeWidthDelta);
  appendDiagramNumberFact(facts, t("workspace.diagram.selectedSubtreeCenterOffset"), node.subtreeCenterOffset);
  const itemId = stringPayloadValue(payload?.itemId);
  if (itemId) {
    const label = payload?.embeddedKind === "focus" ? t("workspace.diagram.selectedFocusTree") : t("workspace.diagram.selectedItem");
    facts.push({ label, value: itemId });
  }
  const moduleId = stringPayloadValue(payload?.moduleId);
  if (moduleId) {
    facts.push({
      label: t("workspace.diagram.selectedModule"),
      value: moduleId,
    });
  }
  return facts;
}

function appendDiagramNumberFact(facts: DiagramSelectionFact[], label: string, value: unknown): void {
  if (typeof value === "number" && Number.isFinite(value)) {
    facts.push({ label, value: formatViewBoxNumber(value) });
  }
}

function diagramNodeKindLabel(payload: Record<string, unknown> | null, t: Translator): string {
  if (payload?.embeddedKind === "focus") {
    return t("workspace.diagram.selectedKindFocus");
  }
  const familyId = stringPayloadValue(payload?.familyId) || stringPayloadValue(payload?.family);
  return familyId || t("workspace.diagram.selectedKindNode");
}

function diagramNodePayloadRecord(payload: unknown): Record<string, unknown> | null {
  if (!payload || typeof payload !== "object" || Array.isArray(payload)) {
    return null;
  }
  return payload as Record<string, unknown>;
}

function stringPayloadValue(value: unknown): string {
  return typeof value === "string" ? value.trim() : "";
}

function optionalNumberText(value: unknown): string {
  return typeof value === "number" && Number.isFinite(value) ? formatViewBoxNumber(value) : "";
}

function optionalNumberFormValue(value: FormDataEntryValue | null): number | undefined {
  const text = typeof value === "string" ? value.trim() : "";
  if (!text) {
    return undefined;
  }
  const numeric = Number(text);
  return Number.isFinite(numeric) ? numeric : undefined;
}

function numberOrFallback(value: unknown, fallback: number): number {
  return typeof value === "number" && Number.isFinite(value) ? value : fallback;
}

function viewBoxRect(viewBox: string): { height: number; width: number; x: number; y: number } | null {
  const parts = parseViewBox(viewBox);
  if (!parts) {
    return null;
  }
  const [x, y, width, height] = parts;
  return { height, width, x, y };
}

function compactLabel(label: string): string {
  return label.length > MAX_LABEL_LENGTH ? `${label.slice(0, MAX_LABEL_LENGTH - 1)}...` : label;
}

export function zoomDiagramViewBox(viewBox: string, zoom: number): string {
  const parts = parseViewBox(viewBox);
  if (!parts || !Number.isFinite(zoom) || zoom <= 0) {
    return viewBox;
  }
  const [x, y, width, height] = parts;
  const nextWidth = width / zoom;
  const nextHeight = height / zoom;
  const nextX = x + (width - nextWidth) / 2;
  const nextY = y + (height - nextHeight) / 2;
  return [nextX, nextY, nextWidth, nextHeight].map(formatViewBoxNumber).join(" ");
}

export function diagramFitViewBoxForViewport(viewBox: string, viewport: DiagramViewportSize): string {
  const parts = parseViewBox(viewBox);
  if (!parts || !Number.isFinite(viewport.width) || !Number.isFinite(viewport.height) || viewport.width <= 0 || viewport.height <= 0) {
    return viewBox;
  }
  const [x, y, width, height] = parts;
  if (width <= 0 || height <= 0) {
    return viewBox;
  }
  const viewportAspect = viewport.width / viewport.height;
  const viewBoxAspect = width / height;
  if (!Number.isFinite(viewportAspect) || viewportAspect <= 0 || Math.abs(viewportAspect - viewBoxAspect) < 0.001) {
    return viewBox;
  }
  if (viewBoxAspect > viewportAspect) {
    const nextHeight = width / viewportAspect;
    const nextY = y - (nextHeight - height) / 2;
    return [x, nextY, width, nextHeight].map(formatViewBoxNumber).join(" ");
  }
  const nextWidth = height * viewportAspect;
  const nextX = x - (nextWidth - width) / 2;
  return [nextX, y, nextWidth, height].map(formatViewBoxNumber).join(" ");
}

export function panDiagramViewBox(viewBox: string, offset: CanvasPoint): string {
  const parts = parseViewBox(viewBox);
  if (!parts || !Number.isFinite(offset.x) || !Number.isFinite(offset.y)) {
    return viewBox;
  }
  const [x, y, width, height] = parts;
  return [x + offset.x, y + offset.y, width, height].map(formatViewBoxNumber).join(" ");
}

export function panOffsetToCenterNode(viewBox: string, node: DiagramViewportCenterNode, gridSizePx: number): CanvasPoint {
  const parts = parseViewBox(viewBox);
  if (!parts || !Number.isFinite(gridSizePx) || gridSizePx <= 0) {
    return { x: 0, y: 0 };
  }
  const [x, y, width, height] = parts;
  const nodeCenter = diagramNodeVisibleGridCenter(node);
  return {
    x: formatOffsetNumber(nodeCenter.x * gridSizePx - (x + width / 2)),
    y: formatOffsetNumber(nodeCenter.y * gridSizePx - (y + height / 2)),
  };
}

export function panOffsetToCenterNodes(viewBox: string, nodes: ReadonlyArray<DiagramViewportCenterNode>, gridSizePx: number): CanvasPoint {
  const parts = parseViewBox(viewBox);
  if (!parts || nodes.length === 0 || !Number.isFinite(gridSizePx) || gridSizePx <= 0) {
    return { x: 0, y: 0 };
  }
  const bounds = nodes.reduce(
    (current, node) => {
      const nodeBounds = diagramNodeVisibleGridBounds(node);
      return {
        maxX: Math.max(current.maxX, nodeBounds.maxX),
        maxY: Math.max(current.maxY, nodeBounds.maxY),
        minX: Math.min(current.minX, nodeBounds.minX),
        minY: Math.min(current.minY, nodeBounds.minY),
      };
    },
    {
      maxX: Number.NEGATIVE_INFINITY,
      maxY: Number.NEGATIVE_INFINITY,
      minX: Number.POSITIVE_INFINITY,
      minY: Number.POSITIVE_INFINITY,
    },
  );
  if (![bounds.minX, bounds.minY, bounds.maxX, bounds.maxY].every(Number.isFinite)) {
    return { x: 0, y: 0 };
  }
  const [x, y, width, height] = parts;
  const centerX = ((bounds.minX + bounds.maxX) / 2) * gridSizePx;
  const centerY = ((bounds.minY + bounds.maxY) / 2) * gridSizePx;
  return {
    x: formatOffsetNumber(centerX - (x + width / 2)),
    y: formatOffsetNumber(centerY - (y + height / 2)),
  };
}

function diagramNodeVisibleGridCenter(node: DiagramViewportCenterNode): CanvasPoint {
  const box = diagramNodeVisibleGridBox(node);
  return {
    x: node.worldX + box.x + box.width / 2,
    y: node.worldY + box.y + box.height / 2,
  };
}

function diagramNodeVisibleGridBounds(node: DiagramViewportCenterNode): DiagramBounds {
  const box = diagramNodeVisibleGridBox(node);
  return {
    maxX: node.worldX + box.x + box.width,
    maxY: node.worldY + box.y + box.height,
    minX: node.worldX + box.x,
    minY: node.worldY + box.y,
  };
}

export function panOffsetToCenterPoint(viewBox: string, point: CanvasPoint): CanvasPoint {
  const parts = parseViewBox(viewBox);
  if (!parts || !Number.isFinite(point.x) || !Number.isFinite(point.y)) {
    return { x: 0, y: 0 };
  }
  const [x, y, width, height] = parts;
  return {
    x: formatOffsetNumber(point.x - (x + width / 2)),
    y: formatOffsetNumber(point.y - (y + height / 2)),
  };
}

export function diagramMiniMapDragStart(point: CanvasPoint | null, pointerId: number): { dragPointerId: number; targetPoint: CanvasPoint } | null {
  if (!point || !Number.isFinite(pointerId)) {
    return null;
  }
  return { dragPointerId: pointerId, targetPoint: point };
}

export function diagramMiniMapDragMove(activePointerId: number | null, pointerId: number, point: CanvasPoint | null): CanvasPoint | null {
  if (activePointerId !== pointerId || !point) {
    return null;
  }
  return point;
}

export function diagramMiniMapDragEnd(activePointerId: number | null, pointerId: number): number | null {
  return activePointerId === pointerId ? null : activePointerId;
}

export function panOffsetForCanvasDrag(startOffset: CanvasPoint, start: CanvasPoint, current: CanvasPoint): CanvasPoint {
  return {
    x: formatOffsetNumber(startOffset.x - (current.x - start.x)),
    y: formatOffsetNumber(startOffset.y - (current.y - start.y)),
  };
}

function diagramClientScaleForViewBox(viewBox: string, viewport: DiagramViewportSize): CanvasPoint | null {
  const parts = parseViewBox(viewBox);
  if (!parts || !Number.isFinite(viewport.width) || !Number.isFinite(viewport.height) || viewport.width <= 0 || viewport.height <= 0) {
    return null;
  }
  const [, , width, height] = parts;
  return { x: width / viewport.width, y: height / viewport.height };
}

export function panOffsetForCanvasClientDrag(startOffset: CanvasPoint, startClient: CanvasPoint, currentClient: CanvasPoint, unitsPerClientPx: CanvasPoint): CanvasPoint {
  return {
    x: formatOffsetNumber(startOffset.x - (currentClient.x - startClient.x) * unitsPerClientPx.x),
    y: formatOffsetNumber(startOffset.y - (currentClient.y - startClient.y) * unitsPerClientPx.y),
  };
}

export function panOffsetForZoomAtPoint(currentViewBox: string, nextBaseViewBox: string, point: CanvasPoint): CanvasPoint {
  const current = parseViewBox(currentViewBox);
  const nextBase = parseViewBox(nextBaseViewBox);
  if (!current || !nextBase || !Number.isFinite(point.x) || !Number.isFinite(point.y)) {
    return { x: 0, y: 0 };
  }
  const [currentX, currentY, currentWidth, currentHeight] = current;
  const [nextBaseX, nextBaseY, nextBaseWidth, nextBaseHeight] = nextBase;
  if (currentWidth <= 0 || currentHeight <= 0 || nextBaseWidth <= 0 || nextBaseHeight <= 0) {
    return { x: 0, y: 0 };
  }
  const ratioX = (point.x - currentX) / currentWidth;
  const ratioY = (point.y - currentY) / currentHeight;
  return {
    x: formatOffsetNumber(point.x - ratioX * nextBaseWidth - nextBaseX),
    y: formatOffsetNumber(point.y - ratioY * nextBaseHeight - nextBaseY),
  };
}

function parseViewBox(viewBox: string): [number, number, number, number] | null {
  const parts = viewBox.split(/\s+/).map(Number);
  return parts.length === 4 && parts.every((part) => Number.isFinite(part)) ? [parts[0], parts[1], parts[2], parts[3]] : null;
}

function formatOffsetNumber(value: number): number {
  const rounded = Math.round(value * 1000) / 1000;
  return Object.is(rounded, -0) ? 0 : rounded;
}

function formatViewBoxNumber(value: number): string {
  const rounded = Math.round(value * 1000) / 1000;
  return Object.is(rounded, -0) ? "0" : String(rounded);
}

function formatSignedGridNumber(value: number): string {
  const text = formatViewBoxNumber(value);
  return Number(value) > 0 ? `+${text}` : text;
}

function slug(value: string): string {
  return (
    value
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, "-")
      .replace(/^-|-$/g, "") || "diagram"
  );
}
