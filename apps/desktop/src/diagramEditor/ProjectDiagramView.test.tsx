import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";
import { createTranslator } from "../i18n";
import { diagramApplyCommandForState, diagramCandidateIdFromInput, diagramCanvasEditCommand, diagramCanvasPanStartAllowed, diagramDragMoveCommand, diagramDragPreviewDocument, diagramDragPreviewNodeIds, diagramEdgeClassName, diagramFitViewBoxForViewport, diagramFocusCoordinateBadges, diagramImageLoadStatusClassName, diagramImageLoadStatusTitle, diagramInitialZoomIndexForDocument, diagramKeyboardShortcut, diagramMiniMapDragEnd, diagramMiniMapDragMove, diagramMiniMapDragStart, diagramMiniMapNodeClassName, diagramModeCounts, diagramMoveFootprintSummary, diagramMoveImpactText, diagramMoveModeHintText, diagramNodeClassName, diagramNodeClickAction, diagramNodeDeleteCommand, diagramNodeDragStartAllowed, diagramNodeEditableSourcePath, diagramNodeHoverCardRows, diagramNodeMoveCommand, diagramNodeMoveShortcut, diagramNodePositionEditable, diagramNodeRenderedImageSideLength, diagramNodeTooltipText, diagramPanOffsetForViewport, diagramPreviewFocusCoordinateBadgeNode, diagramSearchKeyAction, diagramSearchViewportTarget, diagramStoredPositionText, diagramViewportForViewState, diagramWheelClientPointInsideRect, diagramWheelPanDelta, diagramWheelZoomDelta, diagramZoomIndexAfterDelta, diagramZoomIndexForViewportZoom, panDiagramViewBox, panOffsetForCanvasClientDrag, panOffsetForCanvasDrag, panOffsetForZoomAtPoint, panOffsetToCenterNode, panOffsetToCenterNodes, panOffsetToCenterPoint, projectDiagram, ProjectDiagramView, searchDiagramNodes, zoomDiagramViewBox } from "./ProjectDiagramView";
import { resolveDiagramLayout, type DiagramDocument } from "./layoutModel";
import type { DiagramChangedEntity } from "./ProjectDiagramView";

const document: DiagramDocument = {
  schemaVersion: 1,
  gridSizePx: 24,
  nodes: [
    { id: "ROOT", order: 0, mode: "absolute", fixed: true, x: 0, y: 0, width: 4, height: 2, title: "Root Focus" },
    { id: "CHILD", parentId: "ROOT", order: 1, mode: "auto", width: 4, height: 2, title: "Child Focus" }
  ],
  edges: [
    { id: "dependency:ROOT->CHILD", source: "ROOT", target: "CHILD", kind: "dependency" },
    { id: "tree:ROOT->CHILD", source: "ROOT", target: "CHILD", kind: "tree" }
  ]
};

describe("ProjectDiagramView", () => {
  it("zooms diagram view boxes around their center point", () => {
    expect(zoomDiagramViewBox("-48 -48 480 288", 2)).toBe("72 24 240 144");
    expect(zoomDiagramViewBox("-48 -48 480 288", 0.5)).toBe("-288 -192 960 576");
  });

  it("fits wide diagram view boxes to the visible canvas aspect ratio", () => {
    expect(diagramFitViewBoxForViewport("0 0 1200 500", { height: 600, width: 800 })).toBe("0 -200 1200 900");
  });

  it("fits tall diagram view boxes to the visible canvas aspect ratio", () => {
    expect(diagramFitViewBoxForViewport("0 0 400 400", { height: 400, width: 800 })).toBe("-200 0 800 400");
  });

  it("keeps invalid viewport fit inputs unchanged", () => {
    expect(diagramFitViewBoxForViewport("0 0 400 400", { height: 0, width: 800 })).toBe("0 0 400 400");
    expect(diagramFitViewBoxForViewport("invalid", { height: 400, width: 800 })).toBe("invalid");
  });

  it("pans diagram view boxes without changing scale", () => {
    expect(panDiagramViewBox("-48 -48 480 288", { x: 24, y: -12 })).toBe("-24 -60 480 288");
  });

  it("centers a selected move footprint from its combined node bounds", () => {
    expect(
      panOffsetToCenterNodes(
        "0 0 400 200",
        [
          { height: 1, width: 1, worldX: 0, worldY: 0 },
          { height: 2, width: 2, worldX: 4, worldY: 2 }
        ],
        48
      )
    ).toEqual({ x: -56, y: -4 });
    expect(
      panOffsetToCenterNodes(
        "0 0 400 200",
        [
          { height: 1, payload: { embeddedKind: "focus" }, width: 1, worldX: 0, worldY: 0 },
          { height: 1, payload: { embeddedKind: "focus" }, width: 1, worldX: 4, worldY: 2 }
        ],
        48
      )
    ).toEqual({ x: -104, y: -52 });
    expect(panOffsetToCenterNodes("0 0 400 200", [], 48)).toEqual({ x: 0, y: 0 });
  });

  it("computes a pan offset that centers a node in the current view box", () => {
    expect(panOffsetToCenterNode("-48 -48 480 288", { height: 2, width: 4, worldX: 0, worldY: 6 }, 24)).toEqual({ x: -144, y: 72 });
    expect(panOffsetToCenterNode("-48 -48 480 288", { height: 1, payload: { embeddedKind: "focus" }, width: 1, worldX: 0, worldY: 6 }, 24)).toEqual({ x: -192, y: 48 });
  });

  it("computes the viewport target for the first node search match", () => {
    expect(
      diagramSearchViewportTarget(
        [
          { id: "ROOT", payload: {}, title: "Root Focus", height: 2, width: 4, worldX: 0, worldY: 0 },
          { id: "FOCUS_FAR", payload: {}, title: "Far Search Focus", height: 2, width: 4, worldX: 12, worldY: 6 }
        ],
        "far search",
        "-48 -48 480 288",
        24
      )
    ).toEqual({ index: 0, nodeId: "FOCUS_FAR", panOffset: { x: 144, y: 72 } });
    expect(diagramSearchViewportTarget([], "far", "-48 -48 480 288", 24)).toBeNull();
    expect(diagramSearchViewportTarget([{ id: "ROOT", payload: {}, title: "Root Focus", height: 2, width: 4, worldX: 0, worldY: 0 }], "", "-48 -48 480 288", 24)).toBeNull();
  });

  it("computes a pan offset that centers a minimap target point", () => {
    expect(panOffsetToCenterPoint("-48 -48 480 288", { x: 240, y: 120 })).toEqual({ x: 48, y: 24 });
  });

  it("maps minimap pointer drags to active target points", () => {
    expect(diagramMiniMapDragStart({ x: 24, y: 48 }, 7)).toEqual({ dragPointerId: 7, targetPoint: { x: 24, y: 48 } });
    expect(diagramMiniMapDragStart(null, 7)).toBeNull();
    expect(diagramMiniMapDragMove(7, 7, { x: 96, y: 120 })).toEqual({ x: 96, y: 120 });
    expect(diagramMiniMapDragMove(7, 8, { x: 96, y: 120 })).toBeNull();
    expect(diagramMiniMapDragMove(null, 7, { x: 96, y: 120 })).toBeNull();
    expect(diagramMiniMapDragMove(7, 7, null)).toBeNull();
    expect(diagramMiniMapDragEnd(7, 7)).toBeNull();
    expect(diagramMiniMapDragEnd(7, 8)).toBe(7);
  });

  it("computes a pan offset from canvas drag movement", () => {
    expect(panOffsetForCanvasDrag({ x: 24, y: -12 }, { x: 100, y: 80 }, { x: 148, y: 44 })).toEqual({ x: -24, y: 24 });
  });

  it("computes canvas pan from fixed client-pixel drag scale instead of the moving viewBox", () => {
    const scale = { x: 0.5, y: 0.5 };

    expect(panOffsetForCanvasClientDrag({ x: 24, y: -12 }, { x: 100, y: 80 }, { x: 148, y: 44 }, scale)).toEqual({ x: 0, y: 6 });
    expect(panOffsetForCanvasClientDrag({ x: 24, y: -12 }, { x: 100, y: 80 }, { x: 196, y: 44 }, scale)).toEqual({ x: -24, y: 6 });
  });

  it("maps saved viewport values to diagram pan and zoom controls", () => {
    expect(diagramZoomIndexForViewportZoom(1.4)).toBe(2);
    expect(diagramZoomIndexForViewportZoom(99)).toBe(12);
    expect(diagramZoomIndexForViewportZoom(0)).toBe(6);
    expect(diagramPanOffsetForViewport({ x: 24, y: -12, zoom: 1.5 })).toEqual({ x: 24, y: -12 });
    expect(diagramPanOffsetForViewport({ x: Number.NaN, y: -12, zoom: 1.5 })).toEqual({ x: 0, y: 0 });
    expect(diagramPanOffsetForViewport(undefined)).toEqual({ x: 0, y: 0 });
  });

  it("opens image-backed icon focus trees at fitted zoom without overriding saved viewports", () => {
    const focusTreeDocument: DiagramDocument = {
      schemaVersion: 1,
      gridSizePx: 96,
      nodes: Array.from({ length: 6 }, (_, index) => ({
        id: `FOCUS_${index}`,
        order: index,
        mode: "absolute",
        fixed: true,
        x: index * 2,
        y: 0,
        width: 1,
        height: 1,
        imageUrl: `src/modules/focus_tree/C08_MAIN/icons/FOCUS_${index}.png`,
        title: `Focus ${index}`,
        payload: {
          embeddedKind: "focus",
          familyId: "focuses",
          itemId: "TREE",
          objectId: "TREE",
          projectId: "Example",
          relativeRoot: "src/modules/focus_tree/TREE"
        }
      })),
      edges: []
    };

    expect(diagramInitialZoomIndexForDocument(focusTreeDocument)).toBe(6);
    expect(diagramInitialZoomIndexForDocument({ ...focusTreeDocument, viewport: { x: 0, y: 0, zoom: 2 } })).toBe(4);

    const markup = renderToStaticMarkup(<ProjectDiagramView document={focusTreeDocument} onNodeSelect={() => undefined} t={createTranslator("en")} title="Focuses" />);

    expect(markup).toContain("250%");
    expect(markup).toContain('<pattern id="project-diagram-grid-focuses" width="48" height="48" patternUnits="userSpaceOnUse">');
    expect(markup).toContain('class="project-diagram-node-image focus-icon"');
    expect(markup).toContain('width="72"');
    expect(markup).toContain('height="72"');
    expect(markup).not.toContain("project-diagram-arrow");
    expect(markup).not.toContain("marker-end=");
  });

  it("shows local image hydration progress in the toolbar", () => {
    const imageDocument: DiagramDocument = {
      schemaVersion: 1,
      gridSizePx: 48,
      nodes: [
        {
          id: "FOCUS_READY",
          order: 0,
          mode: "absolute",
          fixed: true,
          x: 0,
          y: 0,
          width: 1,
          height: 1,
          imageUrl: "src/modules/focus_tree/C08_MAIN/icons/FOCUS_READY.png",
          title: "Ready",
          payload: { embeddedKind: "focus" }
        },
        {
          id: "FOCUS_MISSING",
          order: 1,
          mode: "absolute",
          fixed: true,
          x: 1,
          y: 0,
          width: 1,
          height: 1,
          imageUrl: "src/modules/focus_tree/C08_MAIN/icons/FOCUS_MISSING.png",
          title: "Missing",
          payload: { embeddedKind: "focus" }
        }
      ],
      edges: []
    };

    const markup = renderToStaticMarkup(<ProjectDiagramView document={imageDocument} projectRoot="/workspace/projects/PIHC3" t={createTranslator("en")} title="Focuses" />);

    expect(markup).toContain('class="project-diagram-image-status loading"');
    expect(markup).toContain('title="Image loading: 0/2 checked, 0 loaded"');
    expect(markup).toContain("Images 0/2");
  });

  it("keeps a source-backed read-only reason visible on the canvas", () => {
    const document: DiagramDocument = {
      schemaVersion: 1,
      gridSizePx: 48,
      nodes: [
        {
          id: "MIO_TRAIT",
          order: 0,
          mode: "absolute",
          fixed: true,
          x: 0,
          y: 0,
          width: 1,
          height: 1,
          title: "MIO trait"
        }
      ],
      edges: []
    };
    const reason =
      "MIO traits are read directly from compiled PDX.";

    const markup = renderToStaticMarkup(
      <ProjectDiagramView
        document={document}
        readOnly
        readOnlyReason={reason}
        t={createTranslator("en")}
        title="MIO traits"
      />
    );

    expect(markup).toContain(
      'class="project-diagram-read-only-reason" role="note"'
    );
    expect(markup).toContain(reason);
    expect(markup).toContain("View only");
  });

  it("classifies local image hydration status for partial and complete loads", () => {
    const t = createTranslator("en");

    expect(diagramImageLoadStatusClassName({ completed: 1, hydrated: 1, status: "loading", total: 2 })).toBe("project-diagram-image-status loading");
    expect(diagramImageLoadStatusClassName({ completed: 2, hydrated: 1, status: "done", total: 2 })).toBe("project-diagram-image-status partial");
    expect(diagramImageLoadStatusClassName({ completed: 2, hydrated: 2, status: "done", total: 2 })).toBe("project-diagram-image-status ready");
    expect(diagramImageLoadStatusTitle({ completed: 2, hydrated: 1, status: "done", total: 2 }, t)).toBe("Image loading: 2/2 checked, 1 loaded");
  });

  it("maps current pan and zoom controls back to canonical viewport state", () => {
    expect(diagramViewportForViewState(6, { x: 24.1234, y: -12.9876 })).toEqual({ x: 24.123, y: -12.988, zoom: 2.5 });
    expect(diagramViewportForViewState(99, { x: 0, y: 0 })).toEqual({ x: 0, y: 0, zoom: 2.5 });
  });

  it("maps focused canvas keyboard shortcuts to viewport commands", () => {
    expect(diagramKeyboardShortcut("ArrowUp", 96)).toEqual({ delta: { x: 0, y: -96 }, kind: "pan" });
    expect(diagramKeyboardShortcut("ArrowRight", 96)).toEqual({ delta: { x: 96, y: 0 }, kind: "pan" });
    expect(diagramKeyboardShortcut("+", 96)).toEqual({ delta: 1, kind: "zoom" });
    expect(diagramKeyboardShortcut("=", 96)).toEqual({ delta: 1, kind: "zoom" });
    expect(diagramKeyboardShortcut("-", 96)).toEqual({ delta: -1, kind: "zoom" });
    expect(diagramKeyboardShortcut("0", 96)).toEqual({ kind: "fit" });
    expect(diagramKeyboardShortcut("Escape", 96)).toEqual({ kind: "fit" });
    expect(diagramKeyboardShortcut("Tab", 96)).toEqual({ kind: "none" });
  });

  it("maps Ctrl mouse wheel movement to viewport zoom deltas", () => {
    expect(diagramWheelZoomDelta({ ctrlKey: true, deltaY: -12 })).toBe(1);
    expect(diagramWheelZoomDelta({ ctrlKey: true, deltaY: 12 })).toBe(-1);
    expect(diagramWheelZoomDelta({ ctrlKey: false, metaKey: true, deltaY: -12 })).toBe(1);
    expect(diagramWheelZoomDelta({ ctrlKey: false, deltaY: -12 })).toBe(0);
    expect(diagramWheelZoomDelta({ ctrlKey: true, deltaY: 0 })).toBe(0);
  });

  it("keeps node dragging left-button only so middle drag can pan from nodes", () => {
    expect(diagramNodeDragStartAllowed(0)).toBe(true);
    expect(diagramNodeDragStartAllowed(1)).toBe(false);
    expect(diagramNodeDragStartAllowed(2)).toBe(false);
  });

  it("allows middle-button canvas panning from child SVG targets", () => {
    expect(diagramCanvasPanStartAllowed({ button: 0, targetIsCanvas: true })).toBe(true);
    expect(diagramCanvasPanStartAllowed({ button: 0, targetIsCanvas: false })).toBe(false);
    expect(diagramCanvasPanStartAllowed({ button: 1, targetIsCanvas: false })).toBe(true);
    expect(diagramCanvasPanStartAllowed({ button: 2, targetIsCanvas: true })).toBe(false);
  });

  it("detects whether a panel-level wheel zoom starts inside the visible diagram canvas", () => {
    const rect = { bottom: 180, left: 10, right: 210, top: 20 };

    expect(diagramWheelClientPointInsideRect({ clientX: 10, clientY: 20 }, rect)).toBe(true);
    expect(diagramWheelClientPointInsideRect({ clientX: 210, clientY: 180 }, rect)).toBe(true);
    expect(diagramWheelClientPointInsideRect({ clientX: 9, clientY: 20 }, rect)).toBe(false);
    expect(diagramWheelClientPointInsideRect({ clientX: 10, clientY: 181 }, rect)).toBe(false);
    expect(diagramWheelClientPointInsideRect({ clientX: 10, clientY: 20 }, { bottom: 20, left: 10, right: 10, top: 20 })).toBe(false);
  });

  it("maps normal wheel movement to viewBox-scaled canvas pan deltas", () => {
    expect(diagramWheelPanDelta({ deltaX: 40, deltaY: 80 }, "0 0 800 400", { height: 200, width: 400 })).toEqual({ x: 80, y: 160 });
    expect(diagramWheelPanDelta({ deltaX: 0, deltaY: 80, shiftKey: true }, "0 0 800 400", { height: 200, width: 400 })).toEqual({ x: 160, y: 0 });
    expect(diagramWheelPanDelta({ deltaX: Number.NaN, deltaY: 80 }, "0 0 800 400", { height: 200, width: 400 })).toEqual({ x: 0, y: 160 });
    expect(diagramWheelPanDelta({ deltaX: 40, deltaY: 80 }, "invalid", { height: 200, width: 400 })).toEqual({ x: 0, y: 0 });
    expect(diagramWheelPanDelta({ deltaX: 40, deltaY: 80 }, "0 0 800 400", { height: 0, width: 400 })).toEqual({ x: 0, y: 0 });
  });

  it("uses 25 percent mouse wheel zoom steps and clamps at the endpoints", () => {
    expect(diagramZoomIndexAfterDelta(2, 1)).toBe(3);
    expect(diagramZoomIndexAfterDelta(2, -1)).toBe(1);
    expect(diagramZoomIndexAfterDelta(0, -1)).toBe(0);
    expect(diagramZoomIndexAfterDelta(12, 1)).toBe(12);
    expect(diagramViewportForViewState(diagramZoomIndexAfterDelta(6, 1), { x: 0, y: 0 })).toEqual({ x: 0, y: 0, zoom: 2.75 });
    expect(diagramViewportForViewState(12, { x: 0, y: 0 })).toEqual({ x: 0, y: 0, zoom: 4 });
  });

  it("computes the pan offset that keeps wheel zoom anchored at the cursor", () => {
    expect(panOffsetForZoomAtPoint("0 0 800 400", "200 100 400 200", { x: 200, y: 100 })).toEqual({ x: -100, y: -50 });
    expect(panOffsetForZoomAtPoint("0 0 800 400", "-400 -200 1600 800", { x: 600, y: 300 })).toEqual({ x: -200, y: -100 });
    expect(panOffsetForZoomAtPoint("invalid", "200 100 400 200", { x: 200, y: 100 })).toEqual({ x: 0, y: 0 });
  });

  it("maps focused canvas edit shortcuts to diagram history and apply commands", () => {
    expect(diagramCanvasEditCommand("z", true, false, false)).toEqual({ kind: "undo" });
    expect(diagramCanvasEditCommand("Z", false, true, false)).toEqual({ kind: "undo" });
    expect(diagramCanvasEditCommand("z", true, false, true)).toEqual({ kind: "redo" });
    expect(diagramCanvasEditCommand("y", false, true, false)).toEqual({ kind: "redo" });
    expect(diagramCanvasEditCommand("s", true, false, false)).toEqual({ kind: "apply" });
    expect(diagramCanvasEditCommand("s", false, false, false)).toBeNull();
    expect(diagramCanvasEditCommand("ArrowDown", true, false, false)).toBeNull();
  });

  it("requires review before applying mixed writable and skipped diagram metadata", () => {
    expect(diagramApplyCommandForState({ busy: false, dirty: true, hasReview: true, reviewAccepted: false, unavailable: false })).toBe("review");
    expect(diagramApplyCommandForState({ busy: false, dirty: true, hasReview: true, reviewAccepted: true, unavailable: false })).toBe("apply");
    expect(diagramApplyCommandForState({ busy: false, dirty: true, hasReview: false, reviewAccepted: false, unavailable: false })).toBe("apply");
    expect(diagramApplyCommandForState({ busy: false, dirty: true, hasReview: true, reviewAccepted: true, unavailable: true })).toBe("none");
    expect(diagramApplyCommandForState({ busy: true, dirty: true, hasReview: true, reviewAccepted: true, unavailable: false })).toBe("none");
  });

  it("maps focused node keyboard shortcuts to one-grid move deltas", () => {
    expect(diagramNodeMoveShortcut("ArrowUp")).toEqual({ dx: 0, dy: -1 });
    expect(diagramNodeMoveShortcut("ArrowRight")).toEqual({ dx: 1, dy: 0 });
    expect(diagramNodeMoveShortcut("ArrowDown")).toEqual({ dx: 0, dy: 1 });
    expect(diagramNodeMoveShortcut("ArrowLeft")).toEqual({ dx: -1, dy: 0 });
    expect(diagramNodeMoveShortcut("Escape")).toBeNull();
  });

  it("maps focused node modifier shortcuts to layout move commands", () => {
    expect(diagramNodeMoveCommand("ArrowLeft", false, false)).toEqual({ delta: { dx: -1, dy: 0 }, kind: "node" });
    expect(diagramNodeMoveCommand("ArrowLeft", false, false, false, false, "subtree")).toEqual({ delta: { dx: -1, dy: 0 }, kind: "subtree" });
    expect(diagramNodeMoveCommand("ArrowLeft", true, false)).toEqual({ delta: { dx: -1, dy: 0 }, kind: "subtree" });
    expect(diagramNodeMoveCommand("ArrowLeft", false, true)).toEqual({ delta: { dx: -1, dy: 0 }, kind: "fixed-descendants" });
    expect(diagramNodeMoveCommand("ArrowLeft", false, false, true, false)).toEqual({ delta: { dx: -1, dy: 0 }, kind: "relayout-descendants" });
    expect(diagramNodeMoveCommand("ArrowLeft", false, false, false, true)).toEqual({ delta: { dx: -1, dy: 0 }, kind: "relayout-descendants" });
    expect(diagramNodeMoveCommand("ArrowLeft", true, false, true, true)).toEqual({ delta: { dx: -1, dy: 0 }, kind: "subtree" });
    expect(diagramNodeMoveCommand("Escape", true, true, true, true)).toBeNull();
  });

  it("opens a diagram node from a native or fallback double click", () => {
    expect(diagramNodeClickAction({ eventDetail: 1, hasOpen: true, lastClickAt: 0, now: 100 })).toEqual({
      action: "select",
      lastClickAt: 100
    });
    expect(diagramNodeClickAction({ eventDetail: 1, hasOpen: true, lastClickAt: 100, now: 300 })).toEqual({
      action: "open",
      lastClickAt: 0
    });
    expect(diagramNodeClickAction({ eventDetail: 1, hasOpen: true, lastClickAt: 100, now: 1700 })).toEqual({
      action: "select",
      lastClickAt: 1700
    });
    expect(diagramNodeClickAction({ eventDetail: 2, hasOpen: true, lastClickAt: 0, now: 700 })).toEqual({
      action: "open",
      lastClickAt: 0
    });
    expect(diagramNodeClickAction({ eventDetail: 1, hasOpen: false, lastClickAt: 100, now: 300 })).toEqual({
      action: "select",
      lastClickAt: 0
    });
  });

  it("maps pointer drag modifiers to layout move commands", () => {
    expect(diagramDragMoveCommand(false, false)).toBe("node");
    expect(diagramDragMoveCommand(false, false, false, false, "subtree")).toBe("subtree");
    expect(diagramDragMoveCommand(false, false, false, false, "relayout-descendants")).toBe("relayout-descendants");
    expect(diagramDragMoveCommand(true, false)).toBe("subtree");
    expect(diagramDragMoveCommand(false, true)).toBe("fixed-descendants");
    expect(diagramDragMoveCommand(false, false, true, false)).toBe("relayout-descendants");
    expect(diagramDragMoveCommand(false, false, false, true)).toBe("relayout-descendants");
    expect(diagramDragMoveCommand(true, true, true, true)).toBe("subtree");
  });

  it("previews the nodes affected by each focus branch drag mode", () => {
    const branchDocument: DiagramDocument = {
      ...document,
      nodes: [
        { ...document.nodes[0], payload: { embeddedKind: "focus" } },
        { ...document.nodes[1], mode: "relative", dx: 1, dy: 5, payload: { embeddedKind: "focus" } },
        { id: "AUTO_GRANDCHILD", parentId: "CHILD", order: 0, mode: "auto", width: 4, height: 2, payload: { embeddedKind: "focus" } },
        { id: "ABSOLUTE_LEAF", parentId: "CHILD", order: 1, mode: "absolute", fixed: true, x: 20, y: 20, width: 4, height: 2, payload: { embeddedKind: "focus" } }
      ],
      edges: []
    };

    expect(diagramDragPreviewNodeIds(branchDocument, "ROOT", "node")).toEqual(["ROOT", "CHILD", "AUTO_GRANDCHILD"]);
    expect(diagramDragPreviewNodeIds(branchDocument, "ROOT", "subtree")).toEqual(["ROOT", "CHILD", "AUTO_GRANDCHILD", "ABSOLUTE_LEAF"]);
    expect(diagramDragPreviewNodeIds(branchDocument, "ROOT", "fixed-descendants")).toEqual(["ROOT"]);
    expect(diagramDragPreviewNodeIds(branchDocument, "ROOT", "relayout-descendants")).toEqual(["ROOT", "CHILD", "AUTO_GRANDCHILD", "ABSOLUTE_LEAF"]);
    expect(diagramDragPreviewNodeIds(branchDocument, "MISSING", "subtree")).toEqual([]);
  });

  it("previews descendant reflow drags with the resolved layout model", () => {
    const branchDocument: DiagramDocument = {
      schemaVersion: 1,
      gridSizePx: 24,
      nodes: [
        { id: "ROOT", order: 0, mode: "absolute", fixed: true, x: 10, y: 4, width: 2, height: 1 },
        { id: "BRANCH", parentId: "ROOT", order: 0, mode: "auto", width: 2, height: 1 },
        { id: "RELATIVE_LEAF", parentId: "BRANCH", order: 0, mode: "relative", dx: 2, dy: 3, width: 2, height: 1 },
        { id: "AUTO_LEAF", parentId: "BRANCH", order: 1, mode: "auto", width: 2, height: 1 },
        { id: "PINNED_LEAF", parentId: "BRANCH", order: 2, mode: "absolute", fixed: true, x: 30, y: 12, width: 2, height: 1 },
        { id: "SIBLING", parentId: "ROOT", order: 1, mode: "absolute", fixed: true, x: 20, y: 8, width: 2, height: 1 }
      ],
      edges: [
        { id: "tree:ROOT->BRANCH", source: "ROOT", target: "BRANCH", kind: "tree" },
        { id: "tree:BRANCH->RELATIVE_LEAF", source: "BRANCH", target: "RELATIVE_LEAF", kind: "tree" },
        { id: "tree:BRANCH->AUTO_LEAF", source: "BRANCH", target: "AUTO_LEAF", kind: "tree" },
        { id: "tree:BRANCH->PINNED_LEAF", source: "BRANCH", target: "PINNED_LEAF", kind: "tree" },
        { id: "tree:ROOT->SIBLING", source: "ROOT", target: "SIBLING", kind: "tree" }
      ]
    };

    const preview = diagramDragPreviewDocument(branchDocument, "BRANCH", "relayout-descendants", { dx: 3, dy: -2 });

    expect(preview).not.toBe(branchDocument);
    expect(resolveDiagramLayout(preview).nodesById).toMatchObject({
      BRANCH: { worldX: 13, worldY: 7 },
      RELATIVE_LEAF: { worldX: 10, worldY: 12 },
      AUTO_LEAF: { worldX: 13, worldY: 12 },
      PINNED_LEAF: { worldX: 16, worldY: 12 },
      SIBLING: { worldX: 20, worldY: 8 }
    });
    expect(preview.nodes.find((node) => node.id === "RELATIVE_LEAF")).toMatchObject({ mode: "auto" });
    expect(preview.nodes.find((node) => node.id === "PINNED_LEAF")).toMatchObject({ mode: "auto" });
    expect(diagramDragPreviewDocument(branchDocument, "BRANCH", "subtree", { dx: 3, dy: -2 })).toBe(branchDocument);
  });

  it("projects focus connectors through drag-preview node offsets", () => {
    const focusDocument: DiagramDocument = {
      ...document,
      nodes: [
        { id: "ROOT", order: 0, mode: "absolute", fixed: true, x: 0, y: 0, width: 3, height: 3, title: "Root", payload: { embeddedKind: "focus" } },
        { id: "CHILD", parentId: "ROOT", order: 0, mode: "relative", dx: 0, dy: 5, width: 3, height: 3, title: "Child", payload: { embeddedKind: "focus" } },
        { id: "ABSOLUTE_LEAF", parentId: "CHILD", order: 1, mode: "absolute", fixed: true, x: 8, y: 11, width: 3, height: 3, title: "Leaf", payload: { embeddedKind: "focus" } }
      ],
      edges: [
        { id: "tree:ROOT->CHILD", source: "ROOT", target: "CHILD", kind: "tree" },
        { id: "tree:CHILD->ABSOLUTE_LEAF", source: "CHILD", target: "ABSOLUTE_LEAF", kind: "tree" }
      ]
    };

    const projection = projectDiagram(focusDocument, {
      nodeIds: diagramDragPreviewNodeIds(focusDocument, "ROOT", "node"),
      offset: { x: 24, y: 12 }
    });

    expect(projection.edges.map((edge) => edge.path)).toEqual([
      "M 24 39 L 24 72 L 24 72 L 24 105",
      "M 24 159 L 24 198 L 192 198 L 192 237"
    ]);
  });

  it("maps focused node delete shortcuts to focus removal commands", () => {
    expect(diagramNodeDeleteCommand("Delete", false)).toEqual({ kind: "node" });
    expect(diagramNodeDeleteCommand("Backspace", false)).toEqual({ kind: "node" });
    expect(diagramNodeDeleteCommand("Delete", true)).toEqual({ kind: "subtree" });
    expect(diagramNodeDeleteCommand("Backspace", true)).toEqual({ kind: "subtree" });
    expect(diagramNodeDeleteCommand("ArrowDown", true)).toBeNull();
  });

  it("matches diagram node search by title, id, and source path", () => {
    const matches = searchDiagramNodes(
      [
        { id: "C08_PARTIV_ROOT", title: "Part IV", payload: { sourceRootRelativePath: "src/modules/focus_tree/C08_PARTIV" } },
        { id: "C08_ARMY_REFORM", title: "Army Reform", payload: { sourceRootRelativePath: "src/modules/technology/C08_ARMY" } },
        { id: "C09_INDUSTRY", title: "Industrial Plan", payload: { sourceRootRelativePath: "src/modules/focus_tree/C09" } }
      ],
      "c08"
    );

    expect(matches.map((node) => node.id)).toEqual(["C08_PARTIV_ROOT", "C08_ARMY_REFORM"]);
    expect(searchDiagramNodes(matches, "technology").map((node) => node.id)).toEqual(["C08_ARMY_REFORM"]);
    expect(searchDiagramNodes(matches, "missing")).toEqual([]);
  });

  it("accepts typed relationship edits only when the id is an available candidate", () => {
    const candidates = [
      { id: "ALT_PARENT", title: "Alt Parent" },
      { id: "EXCLUSIVE", title: "Exclusive Focus" }
    ];

    expect(diagramCandidateIdFromInput(candidates, " ALT_PARENT ")).toBe("ALT_PARENT");
    expect(diagramCandidateIdFromInput(candidates, "ROOT")).toBe("");
    expect(diagramCandidateIdFromInput(candidates, "alt_parent")).toBe("");
    expect(diagramCandidateIdFromInput([], "ALT_PARENT")).toBe("");
  });

  it("maps diagram search keyboard actions", () => {
    expect(diagramSearchKeyAction("Enter", false)).toEqual({ kind: "next" });
    expect(diagramSearchKeyAction("Enter", true)).toEqual({ kind: "previous" });
    expect(diagramSearchKeyAction("Escape", false)).toEqual({ kind: "clear" });
    expect(diagramSearchKeyAction("ArrowDown", false)).toEqual({ kind: "none" });
  });

  it("adds search match classes to diagram node boxes", () => {
    expect(
      diagramNodeClassName({
        branchMember: false,
        draggable: true,
        dragging: false,
        focusNode: false,
        interactive: true,
        mode: "auto",
        searchCurrent: true,
        searchMatch: true,
        selected: false
      })
    ).toBe("project-diagram-node auto interactive draggable search-match search-current");
  });

  it("adds persistent selected-branch classes to diagram node boxes", () => {
    expect(
      diagramNodeClassName({
        branchMember: true,
        draggable: true,
        dragging: false,
        focusNode: true,
        interactive: true,
        mode: "relative",
        searchCurrent: false,
        searchMatch: false,
        selected: false
      })
    ).toBe("project-diagram-node focus-node branch-member relative interactive draggable");
  });

  it("adds active move footprint classes to diagram node boxes", () => {
    expect(
      diagramNodeClassName({
        branchMember: true,
        draggable: true,
        dragging: false,
        focusNode: true,
        interactive: true,
        mode: "relative",
        moveAffected: true,
        searchCurrent: false,
        searchMatch: false,
        selected: false
      })
    ).toBe("project-diagram-node focus-node branch-member move-affected relative interactive draggable");
  });

  it("adds relationship pick classes to diagram node boxes", () => {
    expect(
      diagramNodeClassName({
        branchMember: false,
        draggable: true,
        dragging: false,
        focusNode: true,
        interactive: true,
        mode: "absolute",
        relationshipPickCandidate: true,
        relationshipPickSource: true,
        searchCurrent: false,
        searchMatch: false,
        selected: true
      })
    ).toBe("project-diagram-node focus-node relationship-pick-candidate relationship-pick-source selected absolute interactive draggable");
  });

  it("builds read-only hover text for focus layout details", () => {
    expect(
      diagramNodeTooltipText({
        dx: 1,
        dy: 2,
        height: 1,
        id: "FOCUS_C01_DEM_CHANGE",
        mode: "relative",
        priority: 20,
        subtreeCenterOffset: 1,
        subtreeWidth: 8,
        subtreeWidthDelta: 2,
        title: "Masterly Inactivity",
        width: 1,
        worldX: 19,
        worldY: 4
      })
    ).toBe(["Masterly Inactivity", "ID FOCUS_C01_DEM_CHANGE", "x 19, y 4", "mode relative", "size 1 x 1", "dx 1, dy 2", "priority 20", "w 8", "dw 2", "dc 1"].join("\n"));
  });

  it("builds structured hover card rows for focus layout details", () => {
    expect(
      diagramNodeHoverCardRows({
        dx: 1,
        dy: 2,
        height: 1,
        id: "FOCUS_C01_DEM_CHANGE",
        mode: "relative",
        priority: 20,
        subtreeCenterOffset: 1,
        subtreeWidth: 8,
        subtreeWidthDelta: 2,
        width: 1,
        worldX: 19,
        worldY: 4
      })
    ).toEqual([
      { label: "ID", value: "FOCUS_C01_DEM_CHANGE" },
      { label: "Grid", value: "19, 4" },
      { label: "Mode", value: "relative" },
      { label: "Size", value: "1 x 1" },
      { label: "Offset", value: "1, 2" },
      { label: "Priority", value: "20" },
      { label: "Width", value: "8" },
      { label: "Width delta", value: "2" },
      { label: "Center", value: "1" }
    ]);
  });

  it("localizes diagram node hover metadata", () => {
    const t = createTranslator("zh");
    const node = {
      dx: 1,
      dy: 2,
      height: 1,
      id: "FOCUS_C01_DEM_CHANGE",
      mode: "relative" as const,
      priority: 20,
      subtreeCenterOffset: 1,
      subtreeWidth: 8,
      subtreeWidthDelta: 2,
      title: "Masterly Inactivity",
      width: 1,
      worldX: 19,
      worldY: 4
    };

    expect(diagramNodeTooltipText(node, t)).toBe(["Masterly Inactivity", "ID FOCUS_C01_DEM_CHANGE", "网格 19, 4", "模式 相对", "尺寸 1 x 1", "偏移 1, 2", "优先级 20", "轨道 8", "轨道增量 2", "中心偏移 1"].join("\n"));
    expect(diagramNodeHoverCardRows(node, t)).toEqual([
      { label: "ID", value: "FOCUS_C01_DEM_CHANGE" },
      { label: "网格", value: "19, 4" },
      { label: "模式", value: "相对" },
      { label: "尺寸", value: "1 x 1" },
      { label: "偏移", value: "1, 2" },
      { label: "优先级", value: "20" },
      { label: "轨道", value: "8" },
      { label: "轨道增量", value: "2" },
      { label: "中心偏移", value: "1" }
    ]);
  });

  it("adds search match classes to minimap nodes", () => {
    expect(diagramMiniMapNodeClassName({ searchCurrent: true, searchMatch: true, selected: false })).toBe("project-diagram-minimap-node search-match search-current");
    expect(diagramMiniMapNodeClassName({ searchCurrent: false, searchMatch: true, selected: true })).toBe("project-diagram-minimap-node selected search-match");
  });

  it("adds active move footprint classes to minimap nodes", () => {
    expect(diagramMiniMapNodeClassName({ moveAffected: true, searchCurrent: false, searchMatch: false, selected: false })).toBe("project-diagram-minimap-node move-affected");
  });

  it("marks routed branch edges when both endpoints are in a drag preview", () => {
    const previewIds = new Set(["ROOT", "CHILD", "LEAF"]);

    expect(diagramEdgeClassName({ id: "tree:ROOT->CHILD", kind: "tree", source: "ROOT", target: "CHILD" }, "ROOT", previewIds)).toBe("project-diagram-edge tree connected preview outgoing");
    expect(diagramEdgeClassName({ id: "tree:CHILD->LEAF", kind: "tree", source: "CHILD", target: "LEAF" }, "ROOT", previewIds)).toBe("project-diagram-edge tree distant preview");
    expect(diagramEdgeClassName({ id: "tree:ROOT->SIBLING", kind: "tree", source: "ROOT", target: "SIBLING" }, "ROOT", previewIds)).toBe("project-diagram-edge tree connected outgoing");
  });

  it("marks routed branch edges when both endpoints are in the selected branch", () => {
    const branchIds = new Set(["ROOT", "CHILD", "LEAF"]);

    expect(diagramEdgeClassName({ id: "tree:ROOT->CHILD", kind: "tree", source: "ROOT", target: "CHILD" }, "ROOT", null, branchIds)).toBe("project-diagram-edge tree connected branch-member outgoing");
    expect(diagramEdgeClassName({ id: "tree:CHILD->LEAF", kind: "tree", source: "CHILD", target: "LEAF" }, "ROOT", null, branchIds)).toBe("project-diagram-edge tree distant branch-member");
    expect(diagramEdgeClassName({ id: "tree:ROOT->SIBLING", kind: "tree", source: "ROOT", target: "SIBLING" }, "ROOT", null, branchIds)).toBe("project-diagram-edge tree connected outgoing");
  });

  it("marks active move footprint edges when both endpoints are affected by the selected move mode", () => {
    const branchIds = new Set(["ROOT", "CHILD", "LEAF"]);
    const affectedIds = new Set(["ROOT", "CHILD"]);

    expect(diagramEdgeClassName({ id: "tree:ROOT->CHILD", kind: "tree", source: "ROOT", target: "CHILD" }, "ROOT", null, branchIds, affectedIds)).toBe("project-diagram-edge tree connected branch-member move-affected outgoing");
    expect(diagramEdgeClassName({ id: "tree:CHILD->LEAF", kind: "tree", source: "CHILD", target: "LEAF" }, "ROOT", null, branchIds, affectedIds)).toBe("project-diagram-edge tree distant branch-member");
  });

  it("formats active move mode impact text", () => {
    const t = createTranslator("en");

    expect(diagramMoveImpactText(1, t)).toBe("Affects 1 node");
    expect(diagramMoveImpactText(4, t)).toBe("Affects 4 nodes");
  });

  it("formats active move mode behavior hints", () => {
    const t = createTranslator("en");

    expect(diagramMoveModeHintText("subtree", t)).toBe("Moves branch together");
    expect(diagramMoveModeHintText("node", t)).toBe("Relative descendants follow");
    expect(diagramMoveModeHintText("fixed-descendants", t)).toBe("Keeps descendants in place");
    expect(diagramMoveModeHintText("relayout-descendants", t)).toBe("Recalculates descendants");
  });

  it("summarizes active move footprints for selected focus branches", () => {
    const t = createTranslator("en");

    expect(diagramMoveFootprintSummary("subtree", ["ROOT", "CHILD", "LEAF"], t)).toEqual({
      affectedIds: ["ROOT", "CHILD", "LEAF"],
      hint: "Moves branch together",
      impact: "Affects 3 nodes",
      label: "Branch",
      title: "Branch · Affects 3 nodes · Moves branch together · ROOT, CHILD, LEAF"
    });
  });

  it("counts diagram nodes by layout mode", () => {
    expect(
      diagramModeCounts([
        { mode: "absolute" },
        { mode: "relative" },
        { mode: "auto" },
        { mode: "auto" }
      ])
    ).toEqual({ absolute: 1, auto: 2, relative: 1 });
  });

  it("formats selected node stored layout positions", () => {
    const t = createTranslator("en");

    expect(diagramStoredPositionText({ mode: "absolute", worldX: 2, worldY: -1, x: 2, y: -1 }, t)).toBe("Pinned 2, -1");
    expect(diagramStoredPositionText({ dx: 1, dy: -2, mode: "relative", parentId: "ROOT", worldX: 3, worldY: 4 }, t)).toBe("Offset 1, -2 from ROOT");
    expect(diagramStoredPositionText({ mode: "auto", parentId: "ROOT", worldX: 3, worldY: 4 }, t)).toBe("Auto from parent");
    expect(diagramStoredPositionText({ mode: "auto", worldX: 0, worldY: 0 }, t)).toBe("Auto root");
  });

  it("formats selected focus coordinate badges for world and relative grid positions", () => {
    const t = createTranslator("en");

    expect(diagramFocusCoordinateBadges({ dx: 1, dy: -2, mode: "relative", worldX: 3, worldY: 4 }, t)).toEqual(["x 3 y 4", "dx +1 dy -2"]);
    expect(diagramFocusCoordinateBadges({ dx: -1, dy: 1, mode: "auto", relativePositionKind: "legacy_offset", worldX: 7, worldY: 8 }, t)).toEqual(["x 7 y 8", "dx -1 dy +1"]);
    expect(diagramFocusCoordinateBadges({ mode: "absolute", worldX: -1, worldY: 0 }, t)).toEqual(["x -1 y 0"]);
  });

  it("previews selected focus coordinate badges from snapped drag deltas", () => {
    const t = createTranslator("en");
    const relativePreview = diagramPreviewFocusCoordinateBadgeNode({ dx: -5, dy: 5, mode: "relative", worldX: 5, worldY: 5 }, { dx: 2, dy: -1 });
    const legacyAutoPreview = diagramPreviewFocusCoordinateBadgeNode({ dx: -1, dy: 1, mode: "auto", relativePositionKind: "legacy_offset", worldX: 7, worldY: 8 }, { dx: 2, dy: -1 });
    const absolutePreview = diagramPreviewFocusCoordinateBadgeNode({ mode: "absolute", worldX: -1, worldY: 0 }, { dx: 3, dy: 4 });

    expect(diagramFocusCoordinateBadges(relativePreview, t)).toEqual(["x 7 y 4", "dx -3 dy +4"]);
    expect(diagramFocusCoordinateBadges(legacyAutoPreview, t)).toEqual(["x 9 y 7", "dx +1 dy 0"]);
    expect(diagramFocusCoordinateBadges(absolutePreview, t)).toEqual(["x 2 y 4"]);
    expect(diagramPreviewFocusCoordinateBadgeNode(relativePreview, { dx: 0, dy: 0 })).toBe(relativePreview);
  });

  it("renders a compact edge-kind summary for tree, prerequisite, and reference links", () => {
    const graphDocument: DiagramDocument = {
      ...document,
      nodes: [
        ...document.nodes,
        { id: "OTHER", order: 2, mode: "absolute", fixed: true, x: 8, y: 0, width: 4, height: 2, title: "Other Focus" }
      ],
      edges: [
        { id: "tree:ROOT->CHILD", source: "ROOT", target: "CHILD", kind: "tree" },
        { id: "dependency:ROOT->CHILD", source: "ROOT", target: "CHILD", kind: "dependency" },
        { id: "reference:CHILD->OTHER", source: "CHILD", target: "OTHER", kind: "reference" }
      ]
    };
    const markup = renderToStaticMarkup(<ProjectDiagramView document={graphDocument} onNodeSelect={() => undefined} selectedNodeId="CHILD" t={createTranslator("en")} title="Focuses" />);

    expect(markup).toContain('class="project-diagram-edge-summary"');
    expect(markup).toContain("Tree 1");
    expect(markup).toContain("Prereq 1");
    expect(markup).toContain("Reference 1");
    expect(markup).toContain('class="project-diagram-edge reference connected outgoing"');
  });

  it("renders diagram controls in grouped toolbar rows for normal window layouts", () => {
    const markup = renderToStaticMarkup(
      <ProjectDiagramView
        document={document}
        onDiagramApply={() => undefined}
        onDiagramAutoLayout={() => undefined}
        onDiagramDiscard={() => undefined}
        onDiagramImportJson={() => undefined}
        onDiagramPinAll={() => undefined}
        onDiagramRedo={() => undefined}
        onDiagramUndo={() => undefined}
        onDiagramUnpinAll={() => undefined}
        onNodeMove={() => undefined}
        onNodePin={() => undefined}
        onNodeSelect={() => undefined}
        selectedNodeId="CHILD"
        t={createTranslator("en")}
        title="Focuses"
      />
    );

    expect(markup).toContain('class="project-diagram-summary-row"');
    expect(markup).toContain('class="project-diagram-actions" role="toolbar"');
    expect(markup).toContain('class="project-diagram-action-group project-diagram-search-group"');
    expect(markup).toContain('class="project-diagram-action-group project-diagram-viewport-group"');
    expect(markup).toContain('class="project-diagram-action-group project-diagram-file-group"');
    expect(markup).toContain('class="project-diagram-action-group project-diagram-layout-group"');
    expect(markup).toContain('class="project-diagram-action-group project-diagram-status-group"');
    expect(markup).toContain('class="project-diagram-action-group project-diagram-node-tools"');
    expect(markup).toContain('aria-label="Export JSON"');
    expect(markup).toContain('title="Export JSON"');
    expect(markup).toContain('aria-label="Import JSON"');
    expect(markup).toContain('aria-label="Pin all nodes"');
    expect(markup).toContain('aria-label="Unpin all nodes"');
    expect(markup).toContain('aria-label="Auto layout diagram"');
  });

  it("shows the active move mode affected node count", () => {
    const markup = renderToStaticMarkup(
      <ProjectDiagramView
        document={document}
        onNodeMove={() => undefined}
        onNodeMoveRelayoutDescendants={() => undefined}
        onNodeMoveSubtree={() => undefined}
        onNodeSelect={() => undefined}
        selectedNodeId="ROOT"
        t={createTranslator("en")}
        title="Focuses"
      />
    );

    expect(markup).toContain('class="project-diagram-move-impact"');
    expect(markup).toContain("Affects 2 nodes");
  });

  it("shows the active move mode behavior hint beside the affected count", () => {
    const branchMarkup = renderToStaticMarkup(
      <ProjectDiagramView document={document} onNodeMove={() => undefined} onNodeMoveKeepingDescendants={() => undefined} onNodeMoveRelayoutDescendants={() => undefined} onNodeMoveSubtree={() => undefined} onNodeSelect={() => undefined} selectedNodeId="ROOT" t={createTranslator("en")} title="Focuses" />
    );
    const nodeOnlyMarkup = renderToStaticMarkup(<ProjectDiagramView document={document} onNodeMoveKeepingDescendants={() => undefined} onNodeSelect={() => undefined} selectedNodeId="ROOT" t={createTranslator("en")} title="Focuses" />);

    expect(branchMarkup).toContain('class="project-diagram-move-hint"');
    expect(branchMarkup).toContain("Moves branch together");
    expect(nodeOnlyMarkup).toContain("Keeps descendants in place");
  });

  it("highlights the selected focus branch on the canvas before dragging", () => {
    const branchDocument: DiagramDocument = {
      ...document,
      nodes: [
        document.nodes[0],
        document.nodes[1],
        { id: "GRANDCHILD", parentId: "CHILD", order: 0, mode: "auto", width: 4, height: 2, title: "Grandchild Focus" },
        { id: "SIBLING", parentId: "ROOT", order: 1, mode: "auto", width: 4, height: 2, title: "Sibling Focus" }
      ],
      edges: [
        { id: "tree:ROOT->CHILD", source: "ROOT", target: "CHILD", kind: "tree" },
        { id: "tree:CHILD->GRANDCHILD", source: "CHILD", target: "GRANDCHILD", kind: "tree" },
        { id: "tree:ROOT->SIBLING", source: "ROOT", target: "SIBLING", kind: "tree" }
      ]
    };
    const markup = renderToStaticMarkup(<ProjectDiagramView document={branchDocument} onNodeSelect={() => undefined} selectedNodeId="CHILD" t={createTranslator("en")} title="Focuses" />);

    expect(markup).toContain('class="project-diagram-edge tree connected branch-member outgoing"');
    expect(markup).toContain('class="project-diagram-node branch-member auto interactive" data-node-id="GRANDCHILD"');
    expect(markup).not.toContain('class="project-diagram-node branch-member auto interactive" data-node-id="SIBLING"');
  });

  it("highlights the active selected move footprint on the canvas before dragging", () => {
    const branchDocument: DiagramDocument = {
      ...document,
      nodes: [
        document.nodes[0],
        document.nodes[1],
        { id: "GRANDCHILD", parentId: "CHILD", order: 0, mode: "auto", width: 4, height: 2, title: "Grandchild Focus" },
        { id: "SIBLING", parentId: "ROOT", order: 1, mode: "auto", width: 4, height: 2, title: "Sibling Focus" }
      ],
      edges: [
        { id: "tree:ROOT->CHILD", source: "ROOT", target: "CHILD", kind: "tree" },
        { id: "tree:CHILD->GRANDCHILD", source: "CHILD", target: "GRANDCHILD", kind: "tree" },
        { id: "tree:ROOT->SIBLING", source: "ROOT", target: "SIBLING", kind: "tree" }
      ]
    };
    const markup = renderToStaticMarkup(<ProjectDiagramView document={branchDocument} onNodeMoveSubtree={() => undefined} onNodeSelect={() => undefined} selectedNodeId="CHILD" t={createTranslator("en")} title="Focuses" />);

    expect(markup).toContain('class="project-diagram-edge tree connected branch-member move-affected outgoing"');
    expect(markup).toContain('class="project-diagram-node branch-member move-affected auto interactive draggable" data-node-id="GRANDCHILD"');
    expect(markup).not.toContain('class="project-diagram-node branch-member move-affected auto interactive draggable" data-node-id="SIBLING"');
  });

  it("renders resolved nodes, links, and selected state as an SVG diagram", () => {
    const markup = renderToStaticMarkup(<ProjectDiagramView document={document} onNodeSelect={() => undefined} selectedNodeId="CHILD" t={createTranslator("en")} title="Focuses" />);

    expect(markup).toContain("Focuses diagram");
    expect(markup).toContain("2 nodes / 2 links");
    expect(markup).toContain('class="project-diagram-mode-summary"');
    expect(markup).toContain("Pinned 1");
    expect(markup).toContain("Auto 1");
    expect(markup).toContain('class="project-diagram-node selected auto interactive"');
    expect(markup).toContain('data-node-id="ROOT"');
    expect(markup).toContain('data-node-id="CHILD"');
    expect(markup).toContain('role="button"');
    expect(markup).toContain('tabindex="0"');
    expect(markup).toContain('aria-pressed="true"');
    expect(markup).toContain('class="project-diagram-edge dependency connected incoming"');
    expect(markup).toContain('class="project-diagram-edge tree connected incoming"');
    expect(markup).toContain('d="M 54 48 C 54 96, 54 96, 54 144"');
    expect(markup).toContain('d="M 48 48 C 48 96, 48 96, 48 144"');
    expect(markup).toContain("Child Focus");
  });

  it("routes embedded focus tree and prerequisite links as stepped HOI4-style grid lines", () => {
    const focusPayload = { embeddedKind: "focus", itemId: "focus_tree:C08_PARTIV", objectId: "C08_PARTIV" };
    const focusDocument: DiagramDocument = {
      schemaVersion: 1,
      gridSizePx: 24,
      nodes: [
        { id: "ROOT", order: 0, mode: "absolute", fixed: true, x: 0, y: 0, width: 3, height: 3, title: "Root Focus", payload: focusPayload },
        { id: "CHILD", parentId: "ROOT", order: 1, mode: "absolute", fixed: true, x: 4, y: 5, width: 3, height: 3, title: "Child Focus", payload: focusPayload },
        { id: "ALT", order: 2, mode: "absolute", fixed: true, x: 9, y: 5, width: 3, height: 3, title: "Alt Focus", payload: focusPayload }
      ],
      edges: [
        { id: "tree:ROOT->CHILD", source: "ROOT", target: "CHILD", kind: "tree" },
        { id: "dependency:ROOT->CHILD", source: "ROOT", target: "CHILD", kind: "dependency" },
        { id: "dependency:ROOT->ALT", source: "ROOT", target: "ALT", kind: "dependency" },
        { id: "reference:CHILD->ALT", source: "CHILD", target: "ALT", kind: "reference" }
      ]
    };
    const markup = renderToStaticMarkup(<ProjectDiagramView document={focusDocument} onNodeSelect={() => undefined} t={createTranslator("en")} title="Focuses" />);

    expect(markup).toContain("3 nodes / 4 links");
    expect(markup).toContain("Prereq 2");
    expect(markup).toContain('data-edge-id="tree:ROOT-&gt;CHILD"');
    expect(markup).toContain('d="M 0 27 L 0 60 L 96 60 L 96 93"');
    expect(markup).not.toContain('data-edge-id="dependency:ROOT-&gt;CHILD"');
    expect(markup).toContain('data-edge-id="dependency:ROOT-&gt;ALT"');
    expect(markup).toContain('d="M 6 27 L 6 60 L 222 60 L 222 93"');
    expect(markup).toContain('data-edge-id="reference:CHILD-&gt;ALT"');
    expect(markup).toContain('d="M 123 120 L 189 120"');
  });

  it("keeps the selected node inspector outside the SVG drawing canvas", () => {
    const markup = renderToStaticMarkup(<ProjectDiagramView document={document} onNodeSelect={() => undefined} selectedNodeId="CHILD" t={createTranslator("en")} title="Focuses" />);
    const canvasStart = markup.indexOf('<div class="project-diagram-canvas"');
    const inspectorStart = markup.indexOf('<aside class="project-diagram-selection"');

    expect(markup).toContain('class="project-diagram-workspace"');
    expect(canvasStart).toBeGreaterThanOrEqual(0);
    expect(inspectorStart).toBeGreaterThan(canvasStart);
    expect(markup.slice(canvasStart, inspectorStart)).toContain("</div>");
  });

  it("renders the selected node stored layout state", () => {
    const relativeDocument: DiagramDocument = {
      ...document,
      nodes: [
        document.nodes[0],
        { ...document.nodes[1], dx: 1, dy: -2, mode: "relative" }
      ]
    };
    const markup = renderToStaticMarkup(<ProjectDiagramView document={relativeDocument} onNodeSelect={() => undefined} selectedNodeId="CHILD" t={createTranslator("en")} title="Focuses" />);

    expect(markup).toContain("<dt>Stored</dt><dd>Offset 1, -2 from ROOT</dd>");
  });

  it("renders PIHC legacy layout hints for selected focus nodes", () => {
    const legacyLayoutDocument: DiagramDocument = {
      ...document,
      nodes: [
        { ...document.nodes[0], payload: { embeddedKind: "focus" } },
        {
          ...document.nodes[1],
          payload: { embeddedKind: "focus" },
          priority: 20,
          subtreeCenterOffset: -1,
          subtreeWidth: 5,
          subtreeWidthDelta: 2
        }
      ]
    };
    const markup = renderToStaticMarkup(<ProjectDiagramView document={legacyLayoutDocument} onNodeSelect={() => undefined} selectedNodeId="CHILD" t={createTranslator("en")} title="Focuses" />);

    expect(markup).toContain("<dt>Priority</dt><dd>20</dd>");
    expect(markup).toContain("<dt>Lane</dt><dd>5</dd>");
    expect(markup).toContain("<dt>Lane +</dt><dd>2</dd>");
    expect(markup).toContain("<dt>Center</dt><dd>-1</dd>");
  });

  it("renders editable PIHC legacy layout hint controls for selected focus nodes", () => {
    const legacyLayoutDocument: DiagramDocument = {
      ...document,
      nodes: [
        { ...document.nodes[0], payload: { embeddedKind: "focus" } },
        {
          ...document.nodes[1],
          payload: { embeddedKind: "focus" },
          priority: 20,
          subtreeCenterOffset: -1,
          subtreeWidth: 5,
          subtreeWidthDelta: 2
        }
      ]
    };
    const markup = renderToStaticMarkup(
      <ProjectDiagramView document={legacyLayoutDocument} onNodeSelect={() => undefined} onNodeSetLayoutHints={() => undefined} selectedNodeId="CHILD" t={createTranslator("en")} title="Focuses" />
    );

    expect(markup).toContain('aria-label="Set selected node PIHC layout hints"');
    expect(markup).toContain('name="priority"');
    expect(markup).toContain('name="subtreeWidth"');
    expect(markup).toContain('name="subtreeWidthDelta"');
    expect(markup).toContain('name="subtreeCenterOffset"');
    expect(markup).toContain('value="20"');
    expect(markup).toContain('value="5"');
    expect(markup).toContain('value="2"');
    expect(markup).toContain('value="-1"');
  });

  it("hides PIHC legacy layout hint controls for selected technology nodes", () => {
    const technologyDocument: DiagramDocument = {
      ...document,
      nodes: [
        { ...document.nodes[0], payload: { family: "technology", familyId: "technology", itemId: "technology:ROOT", objectId: "ROOT" } },
        { ...document.nodes[1], payload: { family: "technology", familyId: "technology", itemId: "technology:CHILD", objectId: "CHILD" } }
      ]
    };
    const markup = renderToStaticMarkup(
      <ProjectDiagramView document={technologyDocument} onNodeSelect={() => undefined} onNodeSetLayoutHints={() => undefined} selectedNodeId="CHILD" t={createTranslator("en")} title="Technologies" />
    );

    expect(markup).not.toContain('aria-label="Set selected node PIHC layout hints"');
    expect(markup).not.toContain('name="priority"');
    expect(markup).not.toContain('name="subtreeWidth"');
    expect(markup).not.toContain('name="subtreeWidthDelta"');
    expect(markup).not.toContain('name="subtreeCenterOffset"');
  });

  it("dims edges that are not connected to the selected node", () => {
    const graphDocument: DiagramDocument = {
      ...document,
      nodes: [...document.nodes, { id: "OTHER", order: 2, mode: "absolute", fixed: true, x: 8, y: 0, width: 4, height: 2, title: "Other Focus" }],
      edges: [...document.edges, { id: "tree:ROOT->OTHER", source: "ROOT", target: "OTHER", kind: "tree" }]
    };
    const markup = renderToStaticMarkup(<ProjectDiagramView document={graphDocument} onNodeSelect={() => undefined} selectedNodeId="CHILD" t={createTranslator("en")} title="Focuses" />);

    expect(markup).toContain('class="project-diagram-edge tree distant"');
    expect(markup).toContain('data-edge-id="tree:ROOT-&gt;OTHER"');
  });

  it("ignores selected node state when the selected id is not in the diagram", () => {
    const markup = renderToStaticMarkup(
      <ProjectDiagramView document={document} onNodeMove={() => undefined} onNodeSelect={() => undefined} selectedNodeId="MISSING" t={createTranslator("en")} title="Focuses" />
    );

    expect(markup).not.toContain("project-diagram-nudge");
    expect(markup).not.toContain("distant");
    expect(markup).toContain('class="project-diagram-edge dependency"');
    expect(markup).toContain('class="project-diagram-edge tree"');
  });

  it("renders node image thumbnails without overlapping the node labels", () => {
    const imageDocument: DiagramDocument = {
      ...document,
      nodes: document.nodes.map((node) => (node.id === "CHILD" ? { ...node, imageUrl: "asset://focus-child.png" } : node))
    };
    const markup = renderToStaticMarkup(<ProjectDiagramView document={imageDocument} onNodeSelect={() => undefined} selectedNodeId="CHILD" t={createTranslator("en")} title="Focuses" />);

    expect(markup).toContain('class="project-diagram-node-image"');
    expect(markup).toContain('href="asset://focus-child.png"');
    expect(markup).toContain('<text class="project-diagram-node-title" x="46" y="20">Child Focus</text>');
    expect(markup).toContain('<text class="project-diagram-node-mode" x="46"');
  });

  it("renders embedded focus image nodes as icon-first focus nodes", () => {
    const imageDocument: DiagramDocument = {
      ...document,
      nodes: document.nodes.map((node) =>
        node.id === "CHILD"
          ? {
              ...node,
              width: 3,
              height: 3,
              imageUrl: "asset://focus-child.png",
              payload: {
                embeddedKind: "focus",
                itemId: "focus_tree:C08_PARTIV",
                objectId: "C08_PARTIV"
              }
            }
          : node
      )
    };
    const markup = renderToStaticMarkup(<ProjectDiagramView document={imageDocument} onNodeSelect={() => undefined} selectedNodeId="CHILD" t={createTranslator("en")} title="Focuses" />);

    expect(markup).toContain('class="project-diagram-node focus-node selected auto interactive"');
    expect(markup).toContain('class="project-diagram-node-image focus-icon"');
    expect(markup).toContain('preserveAspectRatio="xMidYMid meet"');
    expect(markup).toContain('href="asset://focus-child.png"');
    expect(markup).not.toContain("project-diagram-focus-icon-frame");
    expect(markup).not.toContain("project-diagram-focus-title-plaque");
    expect(markup).not.toContain("project-diagram-node-title focus-label");
    expect(markup).not.toContain('class="project-diagram-node-mode" x="46"');
  });

  it("renders actual focus icons inside a 1.5 by 1.5 sparse focus coordinate footprint", () => {
    const imageDocument: DiagramDocument = {
      ...document,
      gridSizePx: 96,
      nodes: document.nodes.map((node) =>
        node.id === "CHILD"
          ? {
              ...node,
              width: 1,
              height: 1,
              imageUrl: "asset://focus-child.png",
              payload: {
                embeddedKind: "focus",
                itemId: "focus_tree:C08_PARTIV",
                objectId: "C08_PARTIV"
              }
            }
          : node
      )
    };
    const markup = renderToStaticMarkup(<ProjectDiagramView document={imageDocument} onNodeSelect={() => undefined} selectedNodeId="CHILD" t={createTranslator("en")} title="Focuses" />);

    expect(markup).toContain('class="project-diagram-node focus-node selected auto interactive"');
    expect(markup).toContain('href="asset://focus-child.png"');
    expect(markup).not.toContain("project-diagram-focus-icon-frame");
    expect(markup).toContain('<rect class="project-diagram-node-hit-target" data-node-hit-id="CHILD" height="72" rx="6" width="72" x="-36" y="-36"></rect>');
    expect(markup).toContain('height="72"');
    expect(markup).toContain('width="72" x="-36" y="-36"');
    expect(markup).not.toContain("project-diagram-node-hover-panel");
    expect(markup).not.toContain("project-diagram-focus-title-plaque");
    expect(markup).not.toContain("project-diagram-node-title focus-label");
  });

  it("keeps PIHC focus preview images at a 1.5 by 1.5 grid footprint", () => {
    const gridSizePx = 96;
    const focusNode = {
      height: 1,
      payload: {
        embeddedKind: "focus",
        itemId: "focus_tree:C08_PARTIV",
        objectId: "C08_PARTIV"
      },
      width: 1
    };
    const sideLength = diagramNodeRenderedImageSideLength(focusNode, gridSizePx);

    expect(sideLength).toBe(72);
    expect(sideLength).toBe(gridSizePx * 0.75);
  });

  it("renders technology diagram nodes as compact image icons without focus-only chrome", () => {
    const technologyDocument: DiagramDocument = {
      schemaVersion: 1,
      gridSizePx: 48,
      nodes: [
        {
          id: "TECHNOLOGY_FIREARM_I",
          order: 0,
          mode: "absolute",
          fixed: true,
          x: 4,
          y: 3,
          width: 1,
          height: 1,
          imageUrl: "asset://technology-firearm.png",
          title: "Early Firearm I",
          payload: {
            family: "technology",
            familyId: "technology",
            itemId: "technology:TECHNOLOGY_FIREARM_I",
            objectId: "TECHNOLOGY_FIREARM_I"
          }
        }
      ],
      edges: []
    };
    const markup = renderToStaticMarkup(<ProjectDiagramView document={technologyDocument} onNodeSelect={() => undefined} selectedNodeId="TECHNOLOGY_FIREARM_I" t={createTranslator("en")} title="Technologies" />);

    expect(markup).toContain('class="project-diagram-node icon-node selected absolute interactive"');
    expect(markup).not.toContain("focus-node");
    expect(markup).toContain('class="project-diagram-node-image compact-icon"');
    expect(markup).toContain('preserveAspectRatio="xMidYMid meet"');
    expect(markup).toContain('href="asset://technology-firearm.png"');
    expect(markup).toContain('<rect class="project-diagram-icon-frame" height="42" rx="6" width="42" x="3" y="3"></rect>');
    expect(markup).toContain('height="34"');
    expect(markup).toContain('width="34" x="7" y="7"');
    expect(markup).not.toContain("project-diagram-focus-title-plaque");
    expect(markup).not.toContain("project-diagram-node-title");
    expect(markup).not.toContain("project-diagram-node-mode");
    expect(markup).not.toContain("project-diagram-node-hover-panel");
  });

  it("renders selected focus coordinate badges on the canvas", () => {
    const focusDocument: DiagramDocument = {
      ...document,
      nodes: [
        { ...document.nodes[0], width: 3, height: 3, payload: { embeddedKind: "focus" } },
        { ...document.nodes[1], mode: "relative", dx: 1, dy: 5, width: 3, height: 3, payload: { embeddedKind: "focus" } }
      ]
    };
    const markup = renderToStaticMarkup(<ProjectDiagramView document={focusDocument} onNodeSelect={() => undefined} selectedNodeId="CHILD" t={createTranslator("en")} title="Focuses" />);

    expect(markup).toContain('class="project-diagram-node-coordinate-badges"');
    expect(markup).toContain('aria-label="x 1 y 5 / dx +1 dy +5"');
    expect(markup).toContain(">x 1 y 5</text>");
    expect(markup).toContain(">dx +1 dy +5</text>");
  });

  it("does not render canvas coordinate badges for non-focus nodes", () => {
    const markup = renderToStaticMarkup(<ProjectDiagramView document={document} onNodeSelect={() => undefined} selectedNodeId="CHILD" t={createTranslator("en")} title="Technologies" />);

    expect(markup).not.toContain("project-diagram-node-coordinate-badges");
  });

  it("reserves icon-first focus node space for local project images while they hydrate", () => {
    const imageDocument: DiagramDocument = {
      ...document,
      nodes: document.nodes.map((node) =>
        node.id === "CHILD"
          ? {
              ...node,
              width: 3,
              height: 3,
              imageUrl: "/workspace/projects/PIHC3/src/modules/focus/child/icon.png",
              payload: {
                embeddedKind: "focus",
                itemId: "focus_tree:C08_PARTIV",
                objectId: "C08_PARTIV"
              }
            }
          : node
      )
    };
    const markup = renderToStaticMarkup(<ProjectDiagramView document={imageDocument} onNodeSelect={() => undefined} projectRoot="/workspace/projects/PIHC3" selectedNodeId="CHILD" t={createTranslator("en")} title="Focuses" />);

    expect(markup).not.toContain('href="/workspace/projects/PIHC3/src/modules/focus/child/icon.png"');
    expect(markup).toContain('class="project-diagram-node focus-node selected auto interactive"');
    expect(markup).toContain('class="project-diagram-node-image-placeholder focus-icon"');
    expect(markup).not.toContain("project-diagram-node-title focus-label");
  });

  it("omits in-node focus labels so square icon tiles keep their grid footprint", () => {
    const imageDocument: DiagramDocument = {
      ...document,
      nodes: document.nodes.map((node) =>
        node.id === "CHILD"
          ? {
              ...node,
              width: 3,
              height: 3,
              imageUrl: "asset://focus-child.png",
              payload: {
                embeddedKind: "focus",
                itemId: "focus_tree:C08_PARTIV",
                objectId: "C08_PARTIV"
              },
              title: "Second Summit"
            }
          : node
      )
    };
    const markup = renderToStaticMarkup(<ProjectDiagramView document={imageDocument} onNodeSelect={() => undefined} selectedNodeId="CHILD" t={createTranslator("en")} title="Focuses" />);

    expect(markup).not.toContain('lengthAdjust="spacingAndGlyphs"');
    expect(markup).not.toContain("project-diagram-node-title focus-label");
    expect(markup).not.toContain("project-diagram-node-hover-panel");
  });

  it("shows a focus icon placeholder while local project images hydrate", () => {
    const imageDocument: DiagramDocument = {
      ...document,
      nodes: document.nodes.map((node) =>
        node.id === "CHILD"
          ? {
              ...node,
              width: 3,
              height: 3,
              imageUrl: "/workspace/projects/PIHC3/src/modules/focus/child/icon.png",
              payload: {
                embeddedKind: "focus",
                itemId: "focus_tree:C08_PARTIV",
                objectId: "C08_PARTIV"
              }
            }
          : node
      )
    };
    const markup = renderToStaticMarkup(<ProjectDiagramView document={imageDocument} onNodeSelect={() => undefined} projectRoot="/workspace/projects/PIHC3" selectedNodeId="CHILD" t={createTranslator("en")} title="Focuses" />);

    expect(markup).toContain('class="project-diagram-node-image-placeholder focus-icon"');
    expect(markup).toContain('aria-hidden="true"');
    expect(markup).toContain('<rect height="48" rx="4" width="48" x="-24" y="-24"');
    expect(markup).toContain('<path d="M -12 0 L 12 0 M 0 -12 L 0 12"');
  });

  it("renders nudge controls only when a selected node can be moved", () => {
    const markup = renderToStaticMarkup(
      <ProjectDiagramView document={document} onNodeMove={() => undefined} onNodeSelect={() => undefined} selectedNodeId="CHILD" t={createTranslator("en")} title="Focuses" />
    );

    expect(markup).toContain('class="project-diagram-nudge"');
    expect(markup).toContain('aria-label="Move selected node up"');
    expect(markup).toContain('aria-label="Move selected node left"');
    expect(markup).toContain('aria-label="Move selected node right"');
    expect(markup).toContain('aria-label="Move selected node down"');
  });

  it("renders nudge controls for moving a selected branch", () => {
    const markup = renderToStaticMarkup(
      <ProjectDiagramView document={document} onNodeMoveSubtree={() => undefined} onNodeSelect={() => undefined} selectedNodeId="CHILD" t={createTranslator("en")} title="Focuses" />
    );

    expect(markup).toContain("project-diagram-move-tools");
    expect(markup).toContain('aria-label="Move selected branch"');
    expect(markup).toContain(">Branch</button>");
    expect(markup).toContain('aria-label="Move selected branch up"');
    expect(markup).toContain('aria-label="Move selected branch left"');
    expect(markup).toContain('aria-label="Move selected branch right"');
    expect(markup).toContain('aria-label="Move selected branch down"');
  });

  it("renders nudge controls for moving a selected node while keeping descendants fixed", () => {
    const markup = renderToStaticMarkup(
      <ProjectDiagramView document={document} onNodeMoveKeepingDescendants={() => undefined} onNodeSelect={() => undefined} selectedNodeId="CHILD" t={createTranslator("en")} title="Focuses" />
    );

    expect(markup).toContain("project-diagram-move-tools");
    expect(markup).toContain('aria-label="Move selected node only"');
    expect(markup).toContain(">Node only</button>");
    expect(markup).toContain('aria-label="Move selected node only up"');
    expect(markup).toContain('aria-label="Move selected node only left"');
    expect(markup).toContain('aria-label="Move selected node only right"');
    expect(markup).toContain('aria-label="Move selected node only down"');
  });

  it("renders an auto-layout control for a selected movable node", () => {
    const markup = renderToStaticMarkup(
      <ProjectDiagramView document={document} onNodeAutoLayout={() => undefined} onNodeMove={() => undefined} onNodeSelect={() => undefined} selectedNodeId="CHILD" t={createTranslator("en")} title="Focuses" />
    );

    expect(markup).toContain("project-diagram-auto-layout");
    expect(markup).toContain('aria-label="Auto layout selected node"');
  });

  it("renders an unpin control for a selected node", () => {
    const markup = renderToStaticMarkup(
      <ProjectDiagramView document={document} onNodeSelect={() => undefined} onNodeUnpin={() => undefined} selectedNodeId="CHILD" t={createTranslator("en")} title="Focuses" />
    );

    expect(markup).toContain("project-diagram-unpin-node");
    expect(markup).toContain('aria-label="Unpin selected node"');
  });

  it("renders a pin control for a selected node", () => {
    const markup = renderToStaticMarkup(
      <ProjectDiagramView document={document} onNodePin={() => undefined} onNodeSelect={() => undefined} selectedNodeId="CHILD" t={createTranslator("en")} title="Focuses" />
    );

    expect(markup).toContain("project-diagram-pin-node");
    expect(markup).toContain('aria-label="Pin selected node"');
  });

  it("renders a relative-position control for child nodes only", () => {
    const childMarkup = renderToStaticMarkup(<ProjectDiagramView document={document} onNodeMakeRelative={() => undefined} onNodeSelect={() => undefined} selectedNodeId="CHILD" t={createTranslator("en")} title="Focuses" />);
    const rootMarkup = renderToStaticMarkup(<ProjectDiagramView document={document} onNodeMakeRelative={() => undefined} onNodeSelect={() => undefined} selectedNodeId="ROOT" t={createTranslator("en")} title="Focuses" />);

    expect(childMarkup).toContain("project-diagram-relative-node");
    expect(childMarkup).toContain('aria-label="Make selected node relative"');
    expect(childMarkup).not.toMatch(/aria-label="Make selected node relative"[^>]+disabled=""/);
    expect(rootMarkup).toMatch(/aria-label="Make selected node relative"[^>]+disabled=""/);
  });

  it("disables selected-node pinning when the selected node is already pinned", () => {
    const markup = renderToStaticMarkup(
      <ProjectDiagramView document={document} onNodePin={() => undefined} onNodeSelect={() => undefined} selectedNodeId="ROOT" t={createTranslator("en")} title="Focuses" />
    );

    expect(markup).toMatch(/aria-label="Pin selected node"[^>]+disabled=""/);
  });

  it("disables selected-node auto layout and unpinning when the selected node is already auto", () => {
    const markup = renderToStaticMarkup(
      <ProjectDiagramView document={document} onNodeAutoLayout={() => undefined} onNodeSelect={() => undefined} onNodeUnpin={() => undefined} selectedNodeId="CHILD" t={createTranslator("en")} title="Focuses" />
    );

    expect(markup).toMatch(/aria-label="Auto layout selected node"[^>]+disabled=""/);
    expect(markup).toMatch(/aria-label="Unpin selected node"[^>]+disabled=""/);
  });

  it("renders a pin control for a selected branch", () => {
    const markup = renderToStaticMarkup(
      <ProjectDiagramView document={document} onNodeMove={() => undefined} onNodePinSubtree={() => undefined} onNodeSelect={() => undefined} selectedNodeId="CHILD" t={createTranslator("en")} title="Focuses" />
    );

    expect(markup).toContain("project-diagram-pin-subtree");
    expect(markup).toContain('aria-label="Pin selected branch"');
  });

  it("renders a relative-position control for editable selected branches", () => {
    const allRelativeDocument: DiagramDocument = {
      ...document,
      nodes: [
        document.nodes[0],
        { ...document.nodes[1], mode: "relative", dx: 0, dy: 6 }
      ]
    };
    const rootMarkup = renderToStaticMarkup(<ProjectDiagramView document={document} onNodeMakeSubtreeRelative={() => undefined} onNodeSelect={() => undefined} selectedNodeId="ROOT" t={createTranslator("en")} title="Focuses" />);
    const relativeMarkup = renderToStaticMarkup(<ProjectDiagramView document={allRelativeDocument} onNodeMakeSubtreeRelative={() => undefined} onNodeSelect={() => undefined} selectedNodeId="ROOT" t={createTranslator("en")} title="Focuses" />);

    expect(rootMarkup).toContain("project-diagram-relative-subtree");
    expect(rootMarkup).toContain('aria-label="Make selected branch relative"');
    expect(rootMarkup).not.toMatch(/aria-label="Make selected branch relative"[^>]+disabled=""/);
    expect(relativeMarkup).toMatch(/aria-label="Make selected branch relative"[^>]+disabled=""/);
  });

  it("renders an unpin control for a selected branch", () => {
    const markup = renderToStaticMarkup(
      <ProjectDiagramView document={document} onNodeSelect={() => undefined} onNodeUnpinSubtree={() => undefined} selectedNodeId="CHILD" t={createTranslator("en")} title="Focuses" />
    );

    expect(markup).toContain("project-diagram-unpin-subtree");
    expect(markup).toContain('aria-label="Unpin selected branch"');
  });

  it("renders an auto-layout control for a selected branch", () => {
    const markup = renderToStaticMarkup(
      <ProjectDiagramView document={document} onNodeAutoLayoutSubtree={() => undefined} onNodeMove={() => undefined} onNodeSelect={() => undefined} selectedNodeId="CHILD" t={createTranslator("en")} title="Focuses" />
    );

    expect(markup).toContain("project-diagram-auto-layout-subtree");
    expect(markup).toContain('aria-label="Auto layout selected branch"');
  });

  it("renders an auto-layout control for selected descendants", () => {
    const editableDocument: DiagramDocument = {
      ...document,
      nodes: [
        document.nodes[0],
        { ...document.nodes[1], mode: "absolute", fixed: true, x: 0, y: 6 }
      ]
    };
    const editableMarkup = renderToStaticMarkup(<ProjectDiagramView document={editableDocument} onNodeAutoLayoutDescendants={() => undefined} onNodeSelect={() => undefined} selectedNodeId="ROOT" t={createTranslator("en")} title="Focuses" />);
    const autoMarkup = renderToStaticMarkup(<ProjectDiagramView document={document} onNodeAutoLayoutDescendants={() => undefined} onNodeSelect={() => undefined} selectedNodeId="ROOT" t={createTranslator("en")} title="Focuses" />);

    expect(editableMarkup).toContain("project-diagram-auto-layout-descendants");
    expect(editableMarkup).toContain('aria-label="Auto layout selected descendants"');
    expect(editableMarkup).not.toMatch(/aria-label="Auto layout selected descendants"[^>]+disabled=""/);
    expect(autoMarkup).toMatch(/aria-label="Auto layout selected descendants"[^>]+disabled=""/);
  });

  it("renders move controls that auto-layout selected descendants after the move", () => {
    const rootMarkup = renderToStaticMarkup(<ProjectDiagramView document={document} onNodeMoveRelayoutDescendants={() => undefined} onNodeSelect={() => undefined} selectedNodeId="ROOT" t={createTranslator("en")} title="Focuses" />);
    const childMarkup = renderToStaticMarkup(<ProjectDiagramView document={document} onNodeMoveRelayoutDescendants={() => undefined} onNodeSelect={() => undefined} selectedNodeId="CHILD" t={createTranslator("en")} title="Focuses" />);

    expect(rootMarkup).toContain("project-diagram-move-tools");
    expect(rootMarkup).toContain(">Reflow</button>");
    expect(rootMarkup).toContain('aria-label="Move selected node up and auto-layout descendants"');
    expect(rootMarkup).not.toMatch(/aria-label="Move selected node up and auto-layout descendants"[^>]+disabled=""/);
    expect(childMarkup).toMatch(/aria-label="Move selected node and auto-layout descendants"[^>]+disabled=""/);
  });

  it("renders focus branch removal for embedded focus nodes", () => {
    const focusDocument: DiagramDocument = {
      ...document,
      nodes: [
        { ...document.nodes[0], payload: { embeddedKind: "focus", itemId: "focus_tree:C08_PARTIV", objectId: "C08_PARTIV" } },
        { ...document.nodes[1], payload: { embeddedKind: "focus", itemId: "focus_tree:C08_PARTIV", objectId: "C08_PARTIV" } }
      ]
    };
    const childMarkup = renderToStaticMarkup(<ProjectDiagramView document={focusDocument} onNodeRemoveSubtree={() => undefined} onNodeSelect={() => undefined} selectedNodeId="CHILD" t={createTranslator("en")} title="Focuses" />);
    const rootMarkup = renderToStaticMarkup(<ProjectDiagramView document={focusDocument} onNodeRemoveSubtree={() => undefined} onNodeSelect={() => undefined} selectedNodeId="ROOT" t={createTranslator("en")} title="Focuses" />);
    const technologyMarkup = renderToStaticMarkup(<ProjectDiagramView document={document} onNodeRemoveSubtree={() => undefined} onNodeSelect={() => undefined} selectedNodeId="CHILD" t={createTranslator("en")} title="Technologies" />);

    expect(childMarkup).toContain("project-diagram-remove-subtree");
    expect(childMarkup).toContain('aria-label="Remove selected focus branch"');
    expect(childMarkup).not.toMatch(/aria-label="Remove selected focus branch"[^>]+disabled=""/);
    expect(rootMarkup).not.toMatch(/aria-label="Remove selected focus branch"[^>]+disabled=""/);
    expect(technologyMarkup).not.toContain("project-diagram-remove-subtree");
    expect(technologyMarkup).not.toContain('aria-label="Remove selected focus branch"');
  });

  it("renders focus node removal for embedded focus nodes", () => {
    const focusDocument: DiagramDocument = {
      ...document,
      nodes: [
        { ...document.nodes[0], payload: { embeddedKind: "focus", itemId: "focus_tree:C08_PARTIV", objectId: "C08_PARTIV" } },
        { ...document.nodes[1], payload: { embeddedKind: "focus", itemId: "focus_tree:C08_PARTIV", objectId: "C08_PARTIV" } }
      ]
    };
    const childMarkup = renderToStaticMarkup(<ProjectDiagramView document={focusDocument} onNodeRemoveOnly={() => undefined} onNodeSelect={() => undefined} selectedNodeId="CHILD" t={createTranslator("en")} title="Focuses" />);
    const rootMarkup = renderToStaticMarkup(<ProjectDiagramView document={focusDocument} onNodeRemoveOnly={() => undefined} onNodeSelect={() => undefined} selectedNodeId="ROOT" t={createTranslator("en")} title="Focuses" />);
    const technologyMarkup = renderToStaticMarkup(<ProjectDiagramView document={document} onNodeRemoveOnly={() => undefined} onNodeSelect={() => undefined} selectedNodeId="CHILD" t={createTranslator("en")} title="Technologies" />);

    expect(childMarkup).toContain("project-diagram-remove-node");
    expect(childMarkup).toContain('aria-label="Remove selected focus and keep children"');
    expect(childMarkup).toContain("Delete Backspace");
    expect(childMarkup).not.toMatch(/aria-label="Remove selected focus and keep children"[^>]+disabled=""/);
    expect(rootMarkup).not.toMatch(/aria-label="Remove selected focus and keep children"[^>]+disabled=""/);
    expect(technologyMarkup).not.toContain("project-diagram-remove-node");
    expect(technologyMarkup).not.toContain('aria-label="Remove selected focus and keep children"');
    expect(technologyMarkup).not.toContain("Delete Backspace");
  });

  it("does not render focus removal controls for source-backed non-focus nodes", () => {
    const technologyDocument: DiagramDocument = {
      ...document,
      nodes: [
        { ...document.nodes[0], payload: { itemId: "technology:C08_PARTIV", objectId: "C08_PARTIV" } },
        { ...document.nodes[1], payload: { itemId: "technology:C08_ARMY", objectId: "C08_ARMY" } }
      ]
    };

    const markup = renderToStaticMarkup(<ProjectDiagramView document={technologyDocument} onNodeRemoveOnly={() => undefined} onNodeRemoveSubtree={() => undefined} onNodeSelect={() => undefined} selectedNodeId="CHILD" t={createTranslator("en")} title="Technologies" />);

    expect(markup).not.toContain("project-diagram-remove-node");
    expect(markup).not.toContain("project-diagram-remove-subtree");
    expect(markup).not.toContain('aria-label="Remove selected focus and keep children"');
    expect(markup).not.toContain('aria-label="Remove selected focus branch"');
    expect(markup).not.toContain("Delete Backspace");
    expect(markup).not.toContain("Shift+Delete Shift+Backspace");
  });

  it("renders child focus insertion only for embedded focus nodes", () => {
    const focusDocument: DiagramDocument = {
      ...document,
      nodes: [
        { ...document.nodes[0], payload: { embeddedKind: "focus", itemId: "focus_tree:C08_PARTIV", objectId: "C08_PARTIV" } },
        { ...document.nodes[1], payload: { embeddedKind: "focus", itemId: "focus_tree:C08_PARTIV", objectId: "C08_PARTIV" } }
      ]
    };
    const focusMarkup = renderToStaticMarkup(<ProjectDiagramView document={focusDocument} onNodeInsertChild={() => undefined} onNodeSelect={() => undefined} selectedNodeId="ROOT" t={createTranslator("en")} title="Focuses" />);
    const technologyMarkup = renderToStaticMarkup(<ProjectDiagramView document={document} onNodeInsertChild={() => undefined} onNodeSelect={() => undefined} selectedNodeId="ROOT" t={createTranslator("en")} title="Technologies" />);

    expect(focusMarkup).toContain("project-diagram-insert-child");
    expect(focusMarkup).toContain('aria-label="Insert child focus"');
    expect(focusMarkup).not.toMatch(/aria-label="Insert child focus"[^>]+disabled=""/);
    expect(technologyMarkup).not.toContain("project-diagram-insert-child");
    expect(technologyMarkup).not.toContain('aria-label="Insert child focus"');
  });

  it("renders root focus addition only for diagrams with embedded focus nodes", () => {
    const focusDocument: DiagramDocument = {
      ...document,
      nodes: [
        { ...document.nodes[0], payload: { embeddedKind: "focus", itemId: "focus_tree:C08_PARTIV", objectId: "C08_PARTIV" } },
        { ...document.nodes[1], payload: { embeddedKind: "focus", itemId: "focus_tree:C08_PARTIV", objectId: "C08_PARTIV" } }
      ]
    };
    const focusMarkup = renderToStaticMarkup(<ProjectDiagramView document={focusDocument} onDiagramInsertRoot={() => undefined} onNodeSelect={() => undefined} selectedNodeId="ROOT" t={createTranslator("en")} title="Focuses" />);
    const technologyMarkup = renderToStaticMarkup(<ProjectDiagramView document={document} onDiagramInsertRoot={() => undefined} onNodeSelect={() => undefined} selectedNodeId="ROOT" t={createTranslator("en")} title="Technologies" />);

    expect(focusMarkup).toContain("project-diagram-insert-root");
    expect(focusMarkup).toContain("Add root focus");
    expect(focusMarkup).not.toMatch(/aria-label="Add root focus"[^>]+disabled=""/);
    expect(technologyMarkup).not.toContain("project-diagram-insert-root");
    expect(technologyMarkup).not.toContain("Add root focus");
  });

  it("renders the guarded source-backed Add Focus action even for an empty tree", () => {
    const emptyDocument: DiagramDocument = {
      schemaVersion: 1,
      gridSizePx: 96,
      nodes: [],
      edges: []
    };
    const markup = renderToStaticMarkup(
      <ProjectDiagramView
        createNodeLabel="Add focus"
        document={emptyDocument}
        onDiagramCreateNode={() => undefined}
        t={createTranslator("en")}
        title="Focuses"
      />
    );

    expect(markup).toContain("project-diagram-add-node");
    expect(markup).toContain('aria-label="Add focus"');
    expect(markup).not.toMatch(
      /aria-label="Add focus"[^>]+disabled=""/
    );
  });

  it("enables root focus addition for an empty focus tree context node", () => {
    const focusTreeDocument: DiagramDocument = {
      schemaVersion: 1,
      gridSizePx: 24,
      nodes: [
        {
          id: "C08_PARTIV",
          order: 0,
          mode: "auto",
          width: 6,
          height: 2,
          title: "C08 Part IV",
          payload: {
            family: "focus_tree",
            familyId: "focus_tree",
            itemId: "focus_tree:C08_PARTIV",
            itemKind: "module",
            objectId: "C08_PARTIV",
            projectId: "PIHC3",
            relativeRoot: "src/modules/focus_tree/C08_PARTIV",
            sourceRootRelativePath: "src/modules/focus_tree/C08_PARTIV"
          }
        }
      ],
      edges: []
    };
    const markup = renderToStaticMarkup(<ProjectDiagramView document={focusTreeDocument} onDiagramInsertRoot={() => undefined} onNodeSelect={() => undefined} t={createTranslator("en")} title="Focuses" />);

    expect(markup).toContain("project-diagram-insert-root");
    expect(markup).toContain("Add root focus");
    expect(markup).not.toMatch(/aria-label="Add root focus"[^>]+disabled=""/);
  });

  it("disables selected-subtree auto layout and unpinning when the selected subtree is already auto", () => {
    const markup = renderToStaticMarkup(
      <ProjectDiagramView document={document} onNodeAutoLayoutSubtree={() => undefined} onNodeSelect={() => undefined} onNodeUnpinSubtree={() => undefined} selectedNodeId="CHILD" t={createTranslator("en")} title="Focuses" />
    );

    expect(markup).toMatch(/aria-label="Auto layout selected branch"[^>]+disabled=""/);
    expect(markup).toMatch(/aria-label="Unpin selected branch"[^>]+disabled=""/);
  });

  it("renders sibling reorder controls for a selected node", () => {
    const markup = renderToStaticMarkup(
      <ProjectDiagramView document={document} onNodeReorderSibling={() => undefined} onNodeSelect={() => undefined} selectedNodeId="CHILD" t={createTranslator("en")} title="Focuses" />
    );

    expect(markup).toContain("project-diagram-reorder-sibling");
    expect(markup).toContain('aria-label="Move selected node earlier among siblings"');
    expect(markup).toContain('aria-label="Move selected node later among siblings"');
  });

  it("disables unavailable sibling reorder controls at sibling boundaries", () => {
    const siblingDocument: DiagramDocument = {
      ...document,
      nodes: [
        document.nodes[0],
        { id: "FIRST", parentId: "ROOT", order: 0, mode: "auto", width: 4, height: 2, title: "First Focus" },
        { id: "SECOND", parentId: "ROOT", order: 1, mode: "auto", width: 4, height: 2, title: "Second Focus" },
        { id: "THIRD", parentId: "ROOT", order: 2, mode: "auto", width: 4, height: 2, title: "Third Focus" }
      ]
    };

    const firstMarkup = renderToStaticMarkup(
      <ProjectDiagramView document={siblingDocument} onNodeReorderSibling={() => undefined} onNodeSelect={() => undefined} selectedNodeId="FIRST" t={createTranslator("en")} title="Focuses" />
    );
    const lastMarkup = renderToStaticMarkup(
      <ProjectDiagramView document={siblingDocument} onNodeReorderSibling={() => undefined} onNodeSelect={() => undefined} selectedNodeId="THIRD" t={createTranslator("en")} title="Focuses" />
    );

    expect(firstMarkup).toMatch(/aria-label="Move selected node earlier among siblings"[^>]+disabled=""/);
    expect(firstMarkup).not.toMatch(/aria-label="Move selected node later among siblings"[^>]+disabled=""/);
    expect(lastMarkup).not.toMatch(/aria-label="Move selected node earlier among siblings"[^>]+disabled=""/);
    expect(lastMarkup).toMatch(/aria-label="Move selected node later among siblings"[^>]+disabled=""/);
  });

  it("renders selected node sibling order context", () => {
    const siblingDocument: DiagramDocument = {
      ...document,
      nodes: [
        document.nodes[0],
        { id: "FIRST", parentId: "ROOT", order: 0, mode: "auto", width: 4, height: 2, title: "First Focus" },
        { id: "SECOND", parentId: "ROOT", order: 1, mode: "auto", width: 4, height: 2, title: "Second Focus" },
        { id: "THIRD", parentId: "ROOT", order: 2, mode: "auto", width: 4, height: 2, title: "Third Focus" }
      ]
    };
    const markup = renderToStaticMarkup(<ProjectDiagramView document={siblingDocument} onNodeReorderSibling={() => undefined} onNodeSelect={() => undefined} selectedNodeId="SECOND" t={createTranslator("en")} title="Focuses" />);

    expect(markup).toContain('class="project-diagram-selection-sibling"');
    expect(markup).toContain("Sibling 2 of 3");
    expect(markup).toContain("Siblings");
    expect(markup).toContain('aria-label="Select sibling FIRST - First Focus"');
    expect(markup).toContain('aria-label="Select sibling THIRD - Third Focus"');
    expect(markup).not.toContain('aria-label="Select sibling SECOND');
  });

  it("renders selected branch size context for destructive subtree edits", () => {
    const branchDocument: DiagramDocument = {
      ...document,
      nodes: [
        document.nodes[0],
        document.nodes[1],
        { id: "GRANDCHILD", parentId: "CHILD", order: 2, mode: "auto", width: 4, height: 2, title: "Grandchild Focus" }
      ]
    };
    const markup = renderToStaticMarkup(<ProjectDiagramView document={branchDocument} onNodeRemoveSubtree={() => undefined} onNodeSelect={() => undefined} selectedNodeId="CHILD" t={createTranslator("en")} title="Focuses" />);

    expect(markup).toContain('class="project-diagram-selection-subtree"');
    expect(markup).toContain("Branch 2 nodes / 1 descendant");
  });

  it("renders draggable node affordances when nodes can be moved", () => {
    const markup = renderToStaticMarkup(
      <ProjectDiagramView document={document} onNodeMove={() => undefined} onNodeSelect={() => undefined} selectedNodeId="CHILD" t={createTranslator("en")} title="Focuses" />
    );

    expect(markup).toContain('class="project-diagram-node move-affected selected auto interactive draggable"');
    expect(markup).toContain('aria-keyshortcuts="Enter Space ArrowUp ArrowDown ArrowLeft ArrowRight"');
  });

  it("renders branch and descendant-preserving node keyboard affordances", () => {
    const markup = renderToStaticMarkup(
      <ProjectDiagramView
        document={document}
        onNodeMove={() => undefined}
        onNodeMoveKeepingDescendants={() => undefined}
        onNodeMoveSubtree={() => undefined}
        onNodeSelect={() => undefined}
        selectedNodeId="CHILD"
        t={createTranslator("en")}
        title="Focuses"
      />
    );

    expect(markup).toContain("Shift+ArrowUp Shift+ArrowDown Shift+ArrowLeft Shift+ArrowRight");
    expect(markup).toContain("Alt+ArrowUp Alt+ArrowDown Alt+ArrowLeft Alt+ArrowRight");
  });

  it("renders one selected-node movement pad with explicit move mode buttons", () => {
    const markup = renderToStaticMarkup(
      <ProjectDiagramView
        document={document}
        onNodeMove={() => undefined}
        onNodeMoveKeepingDescendants={() => undefined}
        onNodeMoveRelayoutDescendants={() => undefined}
        onNodeMoveSubtree={() => undefined}
        onNodeSelect={() => undefined}
        selectedNodeId="ROOT"
        t={createTranslator("en")}
        title="Focuses"
      />
    );

    expect(markup).toContain('class="project-diagram-move-tools"');
    expect(markup).toContain('class="project-diagram-move-modes"');
    expect(markup).toContain('aria-label="Move selected branch"');
    expect(markup).toContain('aria-pressed="true" class="toolbar-button project-diagram-move-mode"');
    expect(markup).toContain('class="project-diagram-move-pad"');
    expect(markup).toContain('aria-label="Move selected branch up"');
    expect(markup).not.toContain('project-diagram-move-keeping-descendants');
    expect(markup).not.toContain('project-diagram-move-relayout-descendants');
  });

  it("renders focus subtree removal keyboard affordances for embedded focus branches", () => {
    const focusDocument: DiagramDocument = {
      ...document,
      nodes: [
        { ...document.nodes[0], payload: { embeddedKind: "focus", itemId: "focus_tree:C08_PARTIV", objectId: "C08_PARTIV" } },
        { ...document.nodes[1], payload: { embeddedKind: "focus", itemId: "focus_tree:C08_PARTIV", objectId: "C08_PARTIV" } }
      ]
    };
    const markup = renderToStaticMarkup(
      <ProjectDiagramView document={focusDocument} onNodeRemoveSubtree={() => undefined} onNodeSelect={() => undefined} selectedNodeId="CHILD" t={createTranslator("en")} title="Focuses" />
    );

    expect(markup).toContain("Shift+Delete Shift+Backspace");
  });

  it("renders relayout-descendants drag and keyboard affordances", () => {
    const markup = renderToStaticMarkup(
      <ProjectDiagramView
        document={document}
        onNodeMoveRelayoutDescendants={() => undefined}
        onNodeSelect={() => undefined}
        selectedNodeId="ROOT"
        t={createTranslator("en")}
        title="Focuses"
      />
    );

    expect(markup).toContain('class="project-diagram-node move-affected selected absolute interactive draggable"');
    expect(markup).toContain("Control+ArrowUp Control+ArrowDown Control+ArrowLeft Control+ArrowRight");
    expect(markup).toContain("Meta+ArrowUp Meta+ArrowDown Meta+ArrowLeft Meta+ArrowRight");
    expect(markup).toContain("Drag node and auto-layout descendants");
  });

  it("renders active move footprint details in the selected-node inspector", () => {
    const focusDocument: DiagramDocument = {
      ...document,
      nodes: [
        { ...document.nodes[0], payload: { embeddedKind: "focus" } },
        { ...document.nodes[1], payload: { embeddedKind: "focus" } }
      ]
    };
    const markup = renderToStaticMarkup(
      <ProjectDiagramView
        document={focusDocument}
        onNodeMove={() => undefined}
        onNodeMoveKeepingDescendants={() => undefined}
        onNodeMoveRelayoutDescendants={() => undefined}
        onNodeMoveSubtree={() => undefined}
        onNodeSelect={() => undefined}
        selectedNodeId="ROOT"
        t={createTranslator("en")}
        title="Focuses"
      />
    );

    expect(markup).toContain('class="project-diagram-selection-move-footprint"');
    expect(markup).toContain("Move footprint");
    expect(markup).toContain("Branch");
    expect(markup).toContain("Affects 2 nodes");
    expect(markup).toContain("Moves branch together");
    expect(markup).toContain('class="toolbar-button icon-only project-diagram-center-move-footprint"');
    expect(markup).toContain('aria-label="Center move footprint"');
    expect(markup).toContain("ROOT");
    expect(markup).toContain("CHILD");
  });

  it("renders a diagram apply button for dirty diagrams", () => {
    const markup = renderToStaticMarkup(
      <ProjectDiagramView diagramDirty document={document} onDiagramApply={() => undefined} onNodeMove={() => undefined} onNodeSelect={() => undefined} selectedNodeId="CHILD" t={createTranslator("en")} title="Focuses" />
    );

    expect(markup).toContain("project-diagram-apply");
    expect(markup).toContain("Apply diagram");
  });

  it("disables diagram apply when dirty entities have no writable metadata path", () => {
    const markup = renderToStaticMarkup(
      <ProjectDiagramView
        diagramChangedEntities={[{ id: "focus_tree:C08_PARTIV", title: "Part IV" }]}
        diagramDirty
        document={document}
        onDiagramApply={() => undefined}
        onNodeMove={() => undefined}
        onNodeSelect={() => undefined}
        selectedNodeId="CHILD"
        t={createTranslator("en")}
        title="Focuses"
      />
    );

    expect(markup).toMatch(/project-diagram-apply"[^>]*disabled=""/);
    expect(markup).toContain("Diagram changes do not target writable metadata.");
  });

  it("renders pending PIHC3 metadata scope for dirty diagrams", () => {
    const markup = renderToStaticMarkup(
      <ProjectDiagramView
        diagramChangedEntities={[
          {
            id: "focus_tree:C08_PARTIV",
            path: "src/modules/focus_tree/C08_PARTIV/meta.yaml",
            title: "Part IV"
          },
          {
            id: "focus_tree:C09_CANTERLOT",
            path: "src/modules/focus_tree/C09_CANTERLOT/meta.yaml",
            title: "Canterlot"
          }
        ]}
        diagramDirty
        document={document}
        onDiagramApply={() => undefined}
        onNodeMove={() => undefined}
        onNodeSelect={() => undefined}
        selectedNodeId="CHILD"
        t={createTranslator("en")}
        title="Focuses"
      />
    );

    expect(markup).toContain('class="project-diagram-dirty-summary"');
    expect(markup).toContain('class="project-diagram-dirty-list"');
    expect(markup).toContain('aria-label="Affected metadata"');
    expect(markup).toContain("Source changes: 2 · Ready 2 · Skipped 0");
    expect(markup).toContain("focus_tree:C08_PARTIV src/modules/focus_tree/C08_PARTIV/meta.yaml");
    expect(markup).toContain("<code>focus_tree:C08_PARTIV</code>");
    expect(markup).toContain("<code>focus_tree:C09_CANTERLOT</code>");
    expect(markup).toContain("<span>Part IV</span>");
    expect(markup).toContain("<small>src/modules/focus_tree/C08_PARTIV/meta.yaml</small>");
    expect(markup).toContain("<small>src/modules/focus_tree/C09_CANTERLOT/meta.yaml</small>");
  });

  it("labels dirty PIHC3 metadata rows without a writable path", () => {
    const markup = renderToStaticMarkup(
      <ProjectDiagramView
        diagramChangedEntities={[
          {
            id: "focus_tree:C08_PARTIV",
            path: "src/modules/focus_tree/C08_PARTIV/meta.yaml",
            title: "Part IV"
          },
          {
            id: "focus_tree:C09_CANTERLOT",
            title: "Canterlot"
          }
        ]}
        diagramDirty
        document={document}
        onDiagramApply={() => undefined}
        onNodeMove={() => undefined}
        onNodeSelect={() => undefined}
        selectedNodeId="CHILD"
        t={createTranslator("en")}
        title="Focuses"
      />
    );

    expect(markup).toContain("<code>focus_tree:C09_CANTERLOT</code>");
    expect(markup).toContain("No writable metadata path");
  });

  it("summarizes writable and skipped PIHC3 metadata rows in dirty scope", () => {
    const markup = renderToStaticMarkup(
      <ProjectDiagramView
        diagramChangedEntities={[
          {
            id: "focus_tree:C08_PARTIV",
            path: "src/modules/focus_tree/C08_PARTIV/meta.yaml",
            title: "Part IV"
          },
          {
            id: "focus_tree:C09_CANTERLOT",
            title: "Canterlot"
          }
        ]}
        diagramDirty
        document={document}
        onDiagramApply={() => undefined}
        onNodeMove={() => undefined}
        onNodeSelect={() => undefined}
        selectedNodeId="CHILD"
        t={createTranslator("en")}
        title="Focuses"
      />
    );

    expect(markup).toContain("Source changes: 2 · Ready 1 · Skipped 1");
  });

  it("skips PIHC3 metadata rows that have paths but no generated draft text", () => {
    const markup = renderToStaticMarkup(
      <ProjectDiagramView
        diagramChangedEntities={[
          {
            draftText: ["type: focus_tree", "settings:", "    source_focuses: []", ""].join("\n"),
            id: "focus_tree:C08_PARTIV",
            path: "src/modules/focus_tree/C08_PARTIV/meta.yaml",
            title: "Part IV"
          },
          {
            draftUnavailable: true,
            id: "focus_tree:C08_PARTIV",
            path: "src/modules/focus_tree/C08_PARTIV/legacy/C08_CHILD/info.json",
            title: "Part IV"
          } as DiagramChangedEntity & { draftUnavailable: boolean }
        ]}
        diagramDirty
        document={document}
        onDiagramApply={() => undefined}
        onNodeMove={() => undefined}
        onNodeSelect={() => undefined}
        selectedNodeId="CHILD"
        t={createTranslator("en")}
        title="Focuses"
      />
    );

    expect(markup).toContain("Source changes: 2 · Ready 1 · Skipped 1");
    expect(markup).toContain("Will write 1 · Skip 1");
    expect(markup).toContain('<small class="project-diagram-dirty-missing">No generated metadata draft</small>');
    expect(markup).toContain("<small>src/modules/focus_tree/C08_PARTIV/legacy/C08_CHILD/info.json</small>");
    expect(markup).toContain("Some diagram metadata drafts could not be generated.");
    expect(markup).toContain("Cannot apply diagram");
    expect(markup).toMatch(/project-diagram-apply"[^>]*disabled=""/);
  });

  it("renders an apply preview for mixed PIHC3 metadata rows", () => {
    const markup = renderToStaticMarkup(
      <ProjectDiagramView
        diagramChangedEntities={[
          {
            id: "focus_tree:C08_PARTIV",
            path: "src/modules/focus_tree/C08_PARTIV/meta.yaml",
            title: "Part IV"
          },
          {
            id: "focus_tree:C09_CANTERLOT",
            title: "Canterlot"
          }
        ]}
        diagramDirty
        document={document}
        onDiagramApply={() => undefined}
        onNodeMove={() => undefined}
        onNodeSelect={() => undefined}
        selectedNodeId="CHILD"
        t={createTranslator("en")}
        title="Focuses"
      />
    );

    expect(markup).toContain('class="project-diagram-apply-preview"');
    expect(markup).toContain('title="Write focus_tree:C08_PARTIV src/modules/focus_tree/C08_PARTIV/meta.yaml; Skip focus_tree:C09_CANTERLOT Canterlot"');
    expect(markup).toContain("Will write 1 · Skip 1");
    expect(markup).toContain('class="project-diagram-apply-review"');
    expect(markup).toContain("Review apply scope");
    expect(markup).toContain('class="project-diagram-apply-review-status write"');
    expect(markup).toContain('class="project-diagram-apply-review-status skip"');
    expect(markup).toContain("<small>src/modules/focus_tree/C08_PARTIV/meta.yaml</small>");
    expect(markup).toContain('<small class="project-diagram-dirty-missing">No writable metadata path</small>');
    expect(markup).toContain("Review scope first");
  });

  it("requires review before applying writable PIHC3 technology metadata rows", () => {
    const technologyDocument: DiagramDocument = {
      schemaVersion: 1,
      gridSizePx: 48,
      nodes: [
        {
          fixed: true,
          height: 1,
          id: "TECHNOLOGY_FIREARM_I",
          imageUrl: "asset://technology-firearm.png",
          mode: "absolute",
          order: 0,
          payload: {
            family: "technology",
            familyId: "technology",
            itemId: "technology:TECHNOLOGY_FIREARM_I",
            objectId: "TECHNOLOGY_FIREARM_I"
          },
          title: "Early Firearm I",
          width: 1,
          x: 4,
          y: 3
        }
      ],
      edges: []
    };
    const markup = renderToStaticMarkup(
      <ProjectDiagramView
        diagramChangedEntities={[
          {
            id: "technology:TECHNOLOGY_FIREARM_I",
            path: "src/modules/technology/TECHNOLOGY_FIREARM_I/meta.yaml",
            title: "Early Firearm I"
          }
        ]}
        diagramDirty
        document={technologyDocument}
        onDiagramApply={() => undefined}
        onNodeMove={() => undefined}
        onNodeSelect={() => undefined}
        selectedNodeId="TECHNOLOGY_FIREARM_I"
        t={createTranslator("en")}
        title="Technologies"
      />
    );

    expect(markup).toContain('class="project-diagram-apply-preview"');
    expect(markup).toContain("Will write 1");
    expect(markup).toContain("Review scope first");
    expect(markup).toContain('class="project-diagram-apply-review-status write"');
    expect(markup).toContain("<code>technology:TECHNOLOGY_FIREARM_I</code>");
    expect(markup).toContain("<small>src/modules/technology/TECHNOLOGY_FIREARM_I/meta.yaml</small>");
  });

  it("renders PIHC3 metadata draft text in apply review rows", () => {
    const technologyDocument: DiagramDocument = {
      schemaVersion: 1,
      gridSizePx: 48,
      nodes: [
        {
          fixed: true,
          height: 1,
          id: "TECHNOLOGY_LANDMINE",
          imageUrl: "asset://technology-landmine.png",
          mode: "absolute",
          order: 0,
          payload: {
            family: "technology",
            familyId: "technology",
            itemId: "technology:TECHNOLOGY_LANDMINE",
            objectId: "TECHNOLOGY_LANDMINE"
          },
          title: "Landmine",
          width: 1,
          x: 6,
          y: 3
        }
      ],
      edges: []
    };
    const changedEntity = {
      draftText: ["type: technology", "settings:", "    dependency_ids:", "    - TECHNOLOGY_POWDER_EXPLOSIVE", ""].join("\n"),
      id: "technology:TECHNOLOGY_LANDMINE",
      path: "src/modules/technology/TECHNOLOGY_LANDMINE/meta.yaml",
      title: "Landmine"
    } as DiagramChangedEntity & { draftText: string };
    const markup = renderToStaticMarkup(
      <ProjectDiagramView
        diagramChangedEntities={[changedEntity]}
        diagramDirty
        document={technologyDocument}
        onDiagramApply={() => undefined}
        onNodeMove={() => undefined}
        onNodeSelect={() => undefined}
        selectedNodeId="TECHNOLOGY_LANDMINE"
        t={createTranslator("en")}
        title="Technologies"
      />
    );

    expect(markup).toContain('class="project-diagram-apply-review-draft"');
    expect(markup).toContain("Draft text");
    expect(markup).toContain("dependency_ids:");
    expect(markup).toContain("- TECHNOLOGY_POWDER_EXPLOSIVE");
  });

  it("marks the selected node when its PIHC3 metadata draft is pending", () => {
    const focusDocument: DiagramDocument = {
      ...document,
      nodes: document.nodes.map((node) => ({
        ...node,
        payload: {
          embeddedId: node.id,
          embeddedKind: "focus",
          itemId: "focus_tree:C08_PARTIV",
          objectId: "C08_PARTIV"
        }
      }))
    };
    const markup = renderToStaticMarkup(
      <ProjectDiagramView
        diagramChangedEntities={[
          {
            id: "focus_tree:C08_PARTIV",
            path: "src/modules/focus_tree/C08_PARTIV/meta.yaml",
            title: "Part IV"
          }
        ]}
        diagramDirty
        document={focusDocument}
        onDiagramApply={() => undefined}
        onNodeSelect={() => undefined}
        selectedNodeId="CHILD"
        t={createTranslator("en")}
        title="Focuses"
      />
    );

    expect(markup).toContain('class="project-diagram-selection-draft"');
    expect(markup).toContain("Pending source change");
    expect(markup).toContain("<code>focus_tree:C08_PARTIV</code>");
    expect(markup).toContain("<small>src/modules/focus_tree/C08_PARTIV/meta.yaml</small>");
  });

  it("labels the selected PIHC3 metadata draft when it has no writable path", () => {
    const focusDocument: DiagramDocument = {
      ...document,
      nodes: document.nodes.map((node) => ({
        ...node,
        payload: {
          embeddedId: node.id,
          embeddedKind: "focus",
          itemId: "focus_tree:C08_PARTIV",
          objectId: "C08_PARTIV"
        }
      }))
    };
    const markup = renderToStaticMarkup(
      <ProjectDiagramView
        diagramChangedEntities={[
          {
            id: "focus_tree:C08_PARTIV",
            title: "Part IV"
          }
        ]}
        diagramDirty
        document={focusDocument}
        onDiagramApply={() => undefined}
        onNodeSelect={() => undefined}
        selectedNodeId="CHILD"
        t={createTranslator("en")}
        title="Focuses"
      />
    );

    expect(markup).toMatch(/class="project-diagram-selection-draft"[^>]*>[\s\S]*No writable metadata path[\s\S]*<\/span>/);
  });

  it("keeps apply and discard controls visible for an empty dirty diagram", () => {
    const emptyDocument: DiagramDocument = {
      schemaVersion: 1,
      gridSizePx: 24,
      nodes: [],
      edges: []
    };
    const markup = renderToStaticMarkup(
      <ProjectDiagramView
        diagramChangedEntityIds={["focus_tree:C08_PARTIV"]}
        diagramDirty
        document={emptyDocument}
        onDiagramApply={() => undefined}
        onDiagramDiscard={() => undefined}
        t={createTranslator("en")}
        title="Focuses"
      />
    );

    expect(markup).toContain('class="project-diagram-panel empty"');
    expect(markup).toContain("project-diagram-apply");
    expect(markup).toContain("project-diagram-discard");
    expect(markup).toContain("<code>focus_tree:C08_PARTIV</code>");
  });

  it("renders a diagram discard button for dirty diagrams", () => {
    const markup = renderToStaticMarkup(
      <ProjectDiagramView
        diagramDirty
        document={document}
        onDiagramApply={() => undefined}
        onDiagramDiscard={() => undefined}
        onNodeMove={() => undefined}
        onNodeSelect={() => undefined}
        selectedNodeId="CHILD"
        t={createTranslator("en")}
        title="Focuses"
      />
    );

    expect(markup).toContain("project-diagram-discard");
    expect(markup).toContain("Discard diagram");
  });

  it("renders a diagram-level auto layout command", () => {
    const markup = renderToStaticMarkup(<ProjectDiagramView document={document} onDiagramAutoLayout={() => undefined} onNodeSelect={() => undefined} t={createTranslator("en")} title="Focuses" />);

    expect(markup).toContain("project-diagram-auto-layout-all");
    expect(markup).toContain("Auto layout diagram");
  });

  it("renders a diagram-level pin command", () => {
    const markup = renderToStaticMarkup(<ProjectDiagramView document={document} onDiagramPinAll={() => undefined} onNodeSelect={() => undefined} t={createTranslator("en")} title="Focuses" />);

    expect(markup).toContain("project-diagram-pin-all");
    expect(markup).toContain("Pin all nodes");
  });

  it("renders a diagram-level unpin command", () => {
    const markup = renderToStaticMarkup(<ProjectDiagramView document={document} onDiagramUnpinAll={() => undefined} onNodeSelect={() => undefined} t={createTranslator("en")} title="Focuses" />);

    expect(markup).toContain("project-diagram-unpin-all");
    expect(markup).toContain("Unpin all nodes");
  });

  it("renders diagram JSON import and export commands", () => {
    const markup = renderToStaticMarkup(<ProjectDiagramView document={document} onDiagramImportJson={() => undefined} onNodeSelect={() => undefined} t={createTranslator("en")} title="Focuses" />);

    expect(markup).toContain("project-diagram-json-toggle");
    expect(markup).toContain("Export JSON");
    expect(markup).toContain("Import JSON");
  });

  it("disables diagram-level mode commands that would not change any node", () => {
    const allAutoDocument: DiagramDocument = {
      ...document,
      nodes: [
        { id: "ROOT", order: 0, mode: "auto", width: 4, height: 2, title: "Root Focus" },
        { id: "CHILD", parentId: "ROOT", order: 1, mode: "auto", width: 4, height: 2, title: "Child Focus" }
      ]
    };
    const allPinnedDocument: DiagramDocument = {
      ...document,
      nodes: [
        { id: "ROOT", order: 0, mode: "absolute", fixed: true, x: 0, y: 0, width: 4, height: 2, title: "Root Focus" },
        { id: "CHILD", parentId: "ROOT", order: 1, mode: "absolute", fixed: true, x: 0, y: 6, width: 4, height: 2, title: "Child Focus" }
      ]
    };

    const autoMarkup = renderToStaticMarkup(
      <ProjectDiagramView document={allAutoDocument} onDiagramAutoLayout={() => undefined} onDiagramUnpinAll={() => undefined} onNodeSelect={() => undefined} t={createTranslator("en")} title="Focuses" />
    );
    const pinnedMarkup = renderToStaticMarkup(
      <ProjectDiagramView document={allPinnedDocument} onDiagramPinAll={() => undefined} onNodeSelect={() => undefined} t={createTranslator("en")} title="Focuses" />
    );

    expect(autoMarkup).toMatch(/class="toolbar-button project-diagram-auto-layout-all"[^>]+disabled=""/);
    expect(autoMarkup).toMatch(/class="toolbar-button project-diagram-unpin-all"[^>]+disabled=""/);
    expect(pinnedMarkup).toMatch(/class="toolbar-button project-diagram-pin-all"[^>]+disabled=""/);
  });

  it("renders undo and redo commands for diagram edits", () => {
    const markup = renderToStaticMarkup(
      <ProjectDiagramView
        diagramCanRedo
        diagramCanUndo
        document={document}
        onDiagramRedo={() => undefined}
        onDiagramUndo={() => undefined}
        onNodeSelect={() => undefined}
        t={createTranslator("en")}
        title="Focuses"
      />
    );

    expect(markup).toContain("project-diagram-undo");
    expect(markup).toContain('aria-label="Undo diagram edit"');
    expect(markup).toContain("project-diagram-redo");
    expect(markup).toContain('aria-label="Redo diagram edit"');
  });

  it("renders focused canvas edit keyboard affordances for undo redo and apply", () => {
    const markup = renderToStaticMarkup(
      <ProjectDiagramView
        diagramCanRedo
        diagramCanUndo
        diagramDirty
        document={document}
        onDiagramApply={() => undefined}
        onDiagramRedo={() => undefined}
        onDiagramUndo={() => undefined}
        onNodeSelect={() => undefined}
        t={createTranslator("en")}
        title="Focuses"
      />
    );

    expect(markup).toContain("Meta+Z Control+Z Shift+Meta+Z Shift+Control+Z Meta+Y Control+Y Meta+S Control+S");
  });

  it("renders diagram zoom controls", () => {
    const markup = renderToStaticMarkup(<ProjectDiagramView document={document} onNodeSelect={() => undefined} t={createTranslator("en")} title="Focuses" />);

    expect(markup).toContain('data-diagram-wheel-zoom-surface="panel"');
    expect(markup).toContain('class="project-diagram-zoom"');
    expect(markup).toContain('aria-label="Zoom diagram out"');
    expect(markup).toContain('aria-label="Reset diagram zoom"');
    expect(markup).toContain('aria-label="Zoom diagram in"');
    expect(markup).toContain("250%");
  });

  it("renders dedicated node hit targets for stable diagram interaction", () => {
    const markup = renderToStaticMarkup(<ProjectDiagramView document={document} onNodeSelect={() => undefined} t={createTranslator("en")} title="Focuses" />);

    expect(markup).toContain('class="project-diagram-node-hit-target" data-node-hit-id="ROOT"');
    expect(markup).toContain('class="project-diagram-node-hit-target" data-node-hit-id="CHILD"');
  });

  it("restores a saved diagram viewport from canonical JSON state", () => {
    const viewportDocument: DiagramDocument = {
      ...document,
      viewport: { x: 24, y: -12, zoom: 1.5 }
    };
    const markup = renderToStaticMarkup(<ProjectDiagramView document={viewportDocument} onNodeSelect={() => undefined} t={createTranslator("en")} title="Focuses" />);

    expect(markup).toContain("150%");
    expect(markup).toContain('viewBox="56 -36 320 240"');
    expect(markup).toContain('<rect class="project-diagram-pan-surface" x="56" y="-36" width="320" height="240"></rect>');
  });

  it("renders diagram pan controls", () => {
    const markup = renderToStaticMarkup(<ProjectDiagramView document={document} onNodeSelect={() => undefined} t={createTranslator("en")} title="Focuses" />);

    expect(markup).toContain('class="project-diagram-search"');
    expect(markup).toContain('placeholder="Search diagram nodes"');
    expect(markup).toContain('aria-label="Search diagram nodes"');
    expect(markup).toContain('aria-keyshortcuts="Enter Shift+Enter Escape"');
    expect(markup).toContain('aria-label="Previous search result"');
    expect(markup).toContain('aria-label="Next search result"');
    expect(markup).toContain('<svg aria-keyshortcuts="ArrowUp ArrowDown ArrowLeft ArrowRight + - 0 Escape" class="project-diagram-main pannable" role="img" tabindex="0"');
    expect(markup).toContain('class="project-diagram-pan-surface"');
    expect(markup).toContain('<rect class="project-diagram-pan-surface" x="96" y="24" width="192" height="144"></rect>');
    expect(markup).toContain('class="project-diagram-pan"');
    expect(markup).toContain('aria-label="Pan diagram up"');
    expect(markup).toContain('aria-label="Pan diagram left"');
    expect(markup).toContain('aria-label="Reset diagram pan"');
    expect(markup).toContain('aria-label="Pan diagram right"');
    expect(markup).toContain('aria-label="Pan diagram down"');
  });

  it("renders the canvas grid in fitted normal-window diagram coordinates", () => {
    const markup = renderToStaticMarkup(<ProjectDiagramView document={document} onNodeSelect={() => undefined} t={createTranslator("en")} title="Focuses" />);

    expect(markup).toContain('<pattern id="project-diagram-grid-focuses" width="24" height="24" patternUnits="userSpaceOnUse">');
    expect(markup).toContain('class="project-diagram-grid-line" d="M 24 0 L 0 0 0 24"');
    expect(markup).toContain('<rect class="project-diagram-grid-bg" x="96" y="24" width="192" height="144" fill="url(#project-diagram-grid-focuses)"></rect>');
    expect(markup.indexOf("project-diagram-grid-bg")).toBeLessThan(markup.indexOf("project-diagram-pan-surface"));
  });

  it("renders a fit-view command for restoring the full diagram viewport", () => {
    const markup = renderToStaticMarkup(<ProjectDiagramView document={document} onNodeSelect={() => undefined} t={createTranslator("en")} title="Focuses" />);

    expect(markup).toContain("project-diagram-fit-view");
    expect(markup).toContain('aria-label="Fit diagram to view"');
  });

  it("renders a viewport command for centering the selected node", () => {
    const markup = renderToStaticMarkup(<ProjectDiagramView document={document} onNodeSelect={() => undefined} selectedNodeId="CHILD" t={createTranslator("en")} title="Focuses" />);

    expect(markup).toContain('aria-label="Center selected node"');
  });

  it("marks focus-tree diagrams and renders a selected-node mode switch", () => {
    const focusDocument: DiagramDocument = {
      ...document,
      nodes: document.nodes.map((node) => (node.id === "CHILD" ? { ...node, payload: { embeddedKind: "focus" } } : node))
    };
    const markup = renderToStaticMarkup(
      <ProjectDiagramView
        document={focusDocument}
        onNodeAutoLayout={() => undefined}
        onNodeMakeRelative={() => undefined}
        onNodePin={() => undefined}
        onNodeSelect={() => undefined}
        selectedNodeId="CHILD"
        t={createTranslator("en")}
        title="Focuses"
      />
    );

    expect(markup).toContain('class="project-diagram-panel focus-tree-diagram"');
    expect(markup).toContain('class="project-diagram-node-mode-switch"');
    expect(markup).toContain('data-node-mode-switch="auto"');
    expect(markup).toContain('data-mode-switch-icon="auto"');
    expect(markup).toContain('transform="translate(18 -18)"');
    expect(markup).toContain('aria-label="Set selected node coordinate mode"');
    expect(markup).not.toContain(">A</text>");
  });

  it("renders selected node details in the diagram panel", () => {
    const markup = renderToStaticMarkup(<ProjectDiagramView document={document} onNodeSelect={() => undefined} selectedNodeId="CHILD" t={createTranslator("en")} title="Focuses" />);

    expect(markup).toContain('class="project-diagram-selection"');
    expect(markup).toContain('aria-label="Selected node"');
    expect(markup).toContain("Child Focus");
    expect(markup).toContain("CHILD");
    expect(markup).toContain("Auto");
    expect(markup).toContain("0, 6");
  });

  it("does not synthesize a removed legacy path for an embedded focus node", () => {
    const focusDocument: DiagramDocument = {
      ...document,
      gridSizePx: 96,
      nodes: document.nodes.map((node) =>
        node.id === "CHILD"
          ? {
              ...node,
              payload: {
                embeddedId: "FOCUS_C08_SECOND_SUMMIT",
                embeddedKind: "focus",
                family: "focus_tree",
                familyId: "focus_tree",
                itemId: "focus_tree:C08_PARTIV",
                moduleId: "C08_PARTIV",
                objectId: "C08_PARTIV",
                projectId: "PIHC3",
                relativeRoot: "src/modules/focus_tree/C08_PARTIV",
                sourceFocusPath: "C08_SECOND_SUMMIT",
                sourceRootRelativePath: "src"
              }
            }
          : node
      )
    };
    const markup = renderToStaticMarkup(
      <ProjectDiagramView
        document={focusDocument}
        onNodeInfoClose={() => undefined}
        onNodeOpenModule={() => undefined}
        onNodeSelect={() => undefined}
        openedNodeId="CHILD"
        selectedNodeId="CHILD"
        t={createTranslator("en")}
        title="Focuses"
      />
    );

    expect(markup).toContain('class="project-diagram-node-info-popover"');
    expect(markup).toContain('aria-label="Opened node info"');
    expect(markup).toContain("Child Focus");
    expect(markup).toContain("CHILD");
    expect(markup).not.toContain("/legacy/");
    expect(markup).toContain("Open module item");
    expect(markup).toContain('class="toolbar-button project-diagram-node-open-module"');
  });

  it("prefers a source-backed Focus def.txt over the legacy info path", () => {
    const sourcePath =
      "src/modules/focus_tree/C08_PARTIV/def.txt";
    const focusDocument: DiagramDocument = {
      ...document,
      gridSizePx: 96,
      nodes: document.nodes.map((node) =>
        node.id === "CHILD"
          ? {
              ...node,
              payload: {
                embeddedId: "FOCUS_C08_SECOND_SUMMIT",
                embeddedKind: "focus",
                family: "focus_tree",
                familyId: "focuses",
                itemId:
                  "module:focus_tree/C08_PARTIV",
                moduleId: "focus_tree/C08_PARTIV",
                objectId: "C08_PARTIV",
                projectId: "PIHC3",
                relativeRoot:
                  "src/modules/focus_tree/C08_PARTIV",
                sourceFocusPath: "C08_SECOND_SUMMIT",
                sourcePath
              }
            }
          : node
      )
    };
    const markup = renderToStaticMarkup(
      <ProjectDiagramView
        document={focusDocument}
        onNodeInfoClose={() => undefined}
        onNodeOpenModule={() => undefined}
        onNodeSelect={() => undefined}
        openedNodeId="CHILD"
        selectedNodeId="CHILD"
        t={createTranslator("en")}
        title="Focuses"
      />
    );

    expect(markup).toContain(sourcePath);
    expect(markup).not.toContain(
      "legacy/C08_SECOND_SUMMIT/info.json"
    );
  });

  it("renders an opened technology node popup with its provider source path", () => {
    const sourcePath =
      "src/modules/technology/TECH_CHILD - Child Technology/def.txt";
    const technologyDocument: DiagramDocument = {
      ...document,
      gridSizePx: 48,
      nodes: document.nodes.map((node) =>
        node.id === "CHILD"
          ? {
              ...node,
              height: 1,
              payload: {
                family: "technology",
                familyId: "technologies",
                itemId: "technology:TECH_CHILD",
                itemKind: "module",
                moduleId: "TECH_CHILD",
                objectId: "TECH_CHILD",
                projectId: "PIHC3",
                relativeRoot: "src/modules/technology/TECH_CHILD - Child Technology",
                sourcePath
              },
              width: 1
            }
          : node
      )
    };
    const markup = renderToStaticMarkup(
      <ProjectDiagramView
        document={technologyDocument}
        onNodeInfoClose={() => undefined}
        onNodeOpenModule={() => undefined}
        onNodeSelect={() => undefined}
        openedNodeId="CHILD"
        selectedNodeId="CHILD"
        t={createTranslator("en")}
        title="Technologies"
      />
    );

    expect(markup).toContain('class="project-diagram-node-info-popover"');
    expect(markup).toContain(sourcePath);
    expect(markup).not.toContain("/meta.yaml");
    expect(markup).toContain("Open module item");
  });

  it("opens a MIO trait at its exact nested source file", () => {
    const sourcePath =
      "src/modules/military_industrial_organization/C01/common/military_industrial_organization/organizations/C01.txt";
    const mioDocument: DiagramDocument = {
      ...document,
      nodes: document.nodes.map((node) =>
        node.id === "CHILD"
          ? {
              ...node,
              payload: {
                family:
                  "military_industrial_organization",
                familyId:
                  "military-industrial-organizations",
                sourcePath
              }
            }
          : node
      )
    };
    const markup = renderToStaticMarkup(
      <ProjectDiagramView
        document={mioDocument}
        onNodeInfoClose={() => undefined}
        onNodeOpenModule={() => undefined}
        onNodeSelect={() => undefined}
        openedNodeId="CHILD"
        selectedNodeId="CHILD"
        t={createTranslator("en")}
        title="Military Industrial Organizations"
      />
    );

    expect(
      diagramNodeEditableSourcePath(
        mioDocument.nodes[1].payload
      )
    ).toBe(sourcePath);
    expect(
      diagramNodeEditableSourcePath({
        familyId: "military-industrial-organizations",
        sourcePath: "../outside.txt"
      })
    ).toBe("");
    expect(
      diagramNodeEditableSourcePath({
        familyId: "military-industrial-organizations",
        sourcePath: "src/modules/MIO/def.loc"
      })
    ).toBe("src/modules/MIO/def.loc");
    expect(
      diagramNodeEditableSourcePath({
        familyId: "project-exclusive-entity",
        source_path: "src/modules/project_exclusive_entity/ALPHA/record.json"
      })
    ).toBe("src/modules/project_exclusive_entity/ALPHA/record.json");
    expect(markup).toContain(sourcePath);
  });

  it("suppresses every position control for source-read-only nodes", () => {
    const initialTraitDocument: DiagramDocument = {
      schemaVersion: 1,
      gridSizePx: 48,
      nodes: [
        {
          id: "C01_ORG::initial_trait::START",
          order: 0,
          mode: "absolute",
          fixed: true,
          x: 0,
          y: 0,
          width: 1,
          height: 1,
          title: "Initial designer",
          payload: {
            editable: false,
            family:
              "military_industrial_organization"
          }
        }
      ],
      edges: []
    };
    const markup = renderToStaticMarkup(
      <ProjectDiagramView
        document={initialTraitDocument}
        onNodeMove={() => undefined}
        onNodeSelect={() => undefined}
        onNodeSetPosition={() => undefined}
        selectedNodeId="C01_ORG::initial_trait::START"
        t={createTranslator("en")}
        title="Military Industrial Organizations"
      />
    );

    expect(
      diagramNodePositionEditable(
        initialTraitDocument.nodes[0].payload
      )
    ).toBe(false);
    expect(diagramNodePositionEditable(undefined)).toBe(true);
    expect(markup).not.toContain("project-diagram-node draggable");
    expect(markup).not.toContain("project-diagram-nudge");
    expect(markup).not.toContain(
      'aria-label="Set selected node grid position"'
    );
    expect(markup).toContain(
      "This node has no unambiguous editable source position"
    );
  });

  it("exposes exact MIO relationship kinds and groups in the selected-node inspector", () => {
    const mioDocument: DiagramDocument = {
      ...document,
      edges: [
        {
          id: "all:ROOT->CHILD",
          source: "ROOT",
          target: "CHILD",
          kind: "dependency",
          label: "All parents · group 1",
          relationshipKind: "all_parent"
        },
        {
          id: "any:ROOT->CHILD",
          source: "ROOT",
          target: "CHILD",
          kind: "dependency",
          label: "Any parent · group 2",
          relationshipKind: "any_parent"
        }
      ]
    };
    const markup = renderToStaticMarkup(
      <ProjectDiagramView
        document={mioDocument}
        onNodeSelect={() => undefined}
        selectedNodeId="CHILD"
        t={createTranslator("en")}
        title="Military Industrial Organizations"
      />
    );

    expect(markup).toContain("Exact source relationships");
    expect(markup).toContain("All parents · group 1");
    expect(markup).toContain("Any parent · group 2");
    expect(markup).toContain(
      'aria-label="Select relationship endpoint ROOT - Root Focus"'
    );
    expect(markup).not.toContain(
      'class="project-diagram-selection-link-label">Prereq'
    );
  });

  it("renders exact grid position controls for the selected node", () => {
    const markup = renderToStaticMarkup(
      <ProjectDiagramView document={document} onNodeSelect={() => undefined} onNodeSetPosition={() => undefined} selectedNodeId="CHILD" t={createTranslator("en")} title="Focuses" />
    );

    expect(markup).toContain('aria-label="Set selected node grid position"');
    expect(markup).toContain('aria-label="Selected node X grid coordinate"');
    expect(markup).toContain('aria-label="Selected node Y grid coordinate"');
    expect(markup).toContain('value="0"');
    expect(markup).toContain('value="6"');
    expect(markup).toContain("Set position");
  });

  it("renders selected node coordinate mode controls", () => {
    const childMarkup = renderToStaticMarkup(
      <ProjectDiagramView
        document={document}
        onNodeMakeRelative={() => undefined}
        onNodePin={() => undefined}
        onNodeSelect={() => undefined}
        onNodeUnpin={() => undefined}
        selectedNodeId="CHILD"
        t={createTranslator("en")}
        title="Focuses"
      />
    );
    const rootMarkup = renderToStaticMarkup(
      <ProjectDiagramView
        document={document}
        onNodeMakeRelative={() => undefined}
        onNodePin={() => undefined}
        onNodeSelect={() => undefined}
        onNodeUnpin={() => undefined}
        selectedNodeId="ROOT"
        t={createTranslator("en")}
        title="Focuses"
      />
    );

    expect(childMarkup).toContain('class="project-diagram-mode-controls"');
    expect(childMarkup).toContain('aria-label="Set selected node coordinate mode"');
    expect(childMarkup).toContain('aria-label="Set selected node to pinned mode"');
    expect(childMarkup).toContain('aria-label="Set selected node to relative mode"');
    expect(childMarkup).toContain('aria-label="Set selected node to auto mode"');
    expect(childMarkup).toMatch(/aria-label="Set selected node to auto mode"[^>]+disabled=""/);
    expect(childMarkup).not.toMatch(/aria-label="Set selected node to relative mode"[^>]+disabled=""/);
    expect(rootMarkup).toMatch(/aria-label="Set selected node to relative mode"[^>]+disabled=""/);
  });

  it("renders selected node drag modifier guidance when diagram nodes can be dragged", () => {
    const markup = renderToStaticMarkup(
      <ProjectDiagramView
        document={document}
        onNodeMove={() => undefined}
        onNodeMoveKeepingDescendants={() => undefined}
        onNodeMoveSubtree={() => undefined}
        onNodeSelect={() => undefined}
        selectedNodeId="CHILD"
        t={createTranslator("en")}
        title="Focuses"
      />
    );

    expect(markup).toContain("Drag branch");
    expect(markup).not.toContain("Shift-drag branch");
    expect(markup).toContain("Alt-drag node only");
  });

  it("renders selected node tree context and PIHC3 source path", () => {
    const infoDocument: DiagramDocument = {
      ...document,
      nodes: [
        document.nodes[0],
        {
          ...document.nodes[1],
          payload: {
            embeddedId: "CHILD",
            embeddedKind: "focus",
            family: "focus_tree",
            familyId: "focus_tree",
            itemId: "focus_tree:C08_PARTIV",
            itemKind: "module",
            moduleId: "C08_PARTIV",
            objectId: "CHILD",
            projectId: "PIHC3",
            relativeRoot: "src/modules/focus_tree/C08_PARTIV",
            sourceRootRelativePath: "src/modules/focus_tree/C08_PARTIV"
          }
        },
        {
          id: "GRANDCHILD",
          parentId: "CHILD",
          order: 2,
          mode: "auto",
          width: 4,
          height: 2,
          title: "Grandchild Focus",
          payload: {
            embeddedId: "GRANDCHILD",
            embeddedKind: "focus",
            family: "focus_tree",
            familyId: "focus_tree",
            itemId: "focus_tree:C08_PARTIV",
            itemKind: "module",
            moduleId: "C08_PARTIV",
            objectId: "GRANDCHILD",
            projectId: "PIHC3",
            relativeRoot: "src/modules/focus_tree/C08_PARTIV",
            sourceRootRelativePath: "src/modules/focus_tree/C08_PARTIV"
          }
        }
      ]
    };
    const markup = renderToStaticMarkup(<ProjectDiagramView document={infoDocument} onNodeSelect={() => undefined} selectedNodeId="GRANDCHILD" t={createTranslator("en")} title="Focuses" />);

    expect(markup).toContain('aria-label="Select parent node CHILD - Child Focus"');
    expect(markup).toContain('aria-label="Select ancestor ROOT - Root Focus"');
    expect(markup).toContain('aria-label="Select ancestor CHILD - Child Focus"');
    expect(markup).toContain('class="project-diagram-selection-link-id">ROOT</span>');
    expect(markup).toContain('class="project-diagram-selection-link-title">Root Focus</span>');
    expect(markup).toContain('class="project-diagram-selection-link-id">CHILD</span>');
    expect(markup).toContain('class="project-diagram-selection-link-title">Child Focus</span>');
    expect(markup).toContain("Path");
    expect(markup).toContain("Children 0");
    expect(markup).toContain("src/modules/focus_tree/C08_PARTIV");
    expect(markup).toContain('class="project-diagram-selection-facts"');
    expect(markup).toContain("Embedded focus");
    expect(markup).toContain("Focus tree");
    expect(markup).toContain("focus_tree:C08_PARTIV");
    expect(markup).toContain("<dt>Module</dt><dd>C08_PARTIV</dd>");
    expect(markup).toContain("<dt>Size</dt><dd>4 x 2</dd>");
  });

  it("renders technology module facts without a focus-tree label", () => {
    const technologyDocument: DiagramDocument = {
      ...document,
      nodes: [
        {
          id: "TECH_FIREARM",
          order: 0,
          mode: "absolute",
          fixed: true,
          x: 4,
          y: 3,
          width: 6,
          height: 2,
          title: "Firearm",
          payload: {
            family: "technology",
            familyId: "technology",
            itemId: "technology:TECH_FIREARM",
            itemKind: "module",
            moduleId: "TECH_FIREARM",
            objectId: "TECH_FIREARM",
            projectId: "PIHC3",
            relativeRoot: "src/modules/technology/TECH_FIREARM",
            sourceRootRelativePath: "src/modules/technology/TECH_FIREARM"
          }
        }
      ],
      edges: []
    };
    const markup = renderToStaticMarkup(<ProjectDiagramView document={technologyDocument} onNodeSelect={() => undefined} selectedNodeId="TECH_FIREARM" t={createTranslator("en")} title="Technologies" />);

    expect(markup).toContain("technology");
    expect(markup).not.toContain("Focus tree");
    expect(markup).toContain("<dt>Module</dt><dd>TECH_FIREARM</dd>");
    expect(markup).toContain("technology:TECH_FIREARM");
  });

  it("renders selected node prerequisite, unlock, and reference context", () => {
    const relationshipDocument: DiagramDocument = {
      ...document,
      nodes: [
        document.nodes[0],
        document.nodes[1],
        { id: "NEXT", parentId: "CHILD", order: 2, mode: "auto", width: 4, height: 2, title: "Next Focus" },
        { id: "EXCLUSIVE", order: 3, mode: "absolute", fixed: true, x: 8, y: 0, width: 4, height: 2, title: "Exclusive Focus" }
      ],
      edges: [
        { id: "tree:ROOT->CHILD", source: "ROOT", target: "CHILD", kind: "tree" },
        { id: "dependency:ROOT->CHILD", source: "ROOT", target: "CHILD", kind: "dependency" },
        { id: "dependency:CHILD->NEXT", source: "CHILD", target: "NEXT", kind: "dependency" },
        { id: "reference:CHILD->EXCLUSIVE", source: "CHILD", target: "EXCLUSIVE", kind: "reference" }
      ]
    };
    const markup = renderToStaticMarkup(<ProjectDiagramView document={relationshipDocument} onNodeSelect={() => undefined} selectedNodeId="CHILD" t={createTranslator("en")} title="Focuses" />);

    expect(markup).toContain("Prereq");
    expect(markup).toContain('class="project-diagram-selection-link-title">Root Focus</span>');
    expect(markup).toContain("Unlocks");
    expect(markup).toContain('class="project-diagram-selection-link-title">Next Focus</span>');
    expect(markup).toContain("References");
    expect(markup).toContain('class="project-diagram-selection-link-title">Exclusive Focus</span>');
  });

  it("renders selected node relationships as selectable node buttons", () => {
    const relationshipDocument: DiagramDocument = {
      ...document,
      nodes: [
        document.nodes[0],
        document.nodes[1],
        { id: "NEXT", parentId: "CHILD", order: 2, mode: "auto", width: 4, height: 2, title: "Next Focus" },
        { id: "EXCLUSIVE", order: 3, mode: "absolute", fixed: true, x: 8, y: 0, width: 4, height: 2, title: "Exclusive Focus" }
      ],
      edges: [
        { id: "dependency:ROOT->CHILD", source: "ROOT", target: "CHILD", kind: "dependency" },
        { id: "dependency:CHILD->NEXT", source: "CHILD", target: "NEXT", kind: "dependency" },
        { id: "reference:CHILD->EXCLUSIVE", source: "CHILD", target: "EXCLUSIVE", kind: "reference" }
      ]
    };
    const markup = renderToStaticMarkup(<ProjectDiagramView document={relationshipDocument} onNodeSelect={() => undefined} selectedNodeId="CHILD" t={createTranslator("en")} title="Focuses" />);

    expect(markup).toContain('class="project-diagram-selection-link-row"');
    expect(markup).toContain('aria-label="Select prerequisite ROOT - Root Focus"');
    expect(markup).toContain('aria-label="Select unlocked node NEXT - Next Focus"');
    expect(markup).toContain('aria-label="Select referenced node EXCLUSIVE - Exclusive Focus"');
    expect(markup).toContain('class="project-diagram-selection-link-id">ROOT</span>');
    expect(markup).toContain('class="project-diagram-selection-link-title">Root Focus</span>');
  });

  it("renders selected node dependency edit controls", () => {
    const EditableProjectDiagramView = ProjectDiagramView as (
      props: Parameters<typeof ProjectDiagramView>[0] & {
        onNodeAddDependency?: (targetId: string, sourceId: string) => void;
        onNodeAddUnlock?: (sourceId: string, targetId: string) => void;
        onNodeRemoveDependency?: (targetId: string, sourceId: string) => void;
        onNodeRemoveUnlock?: (sourceId: string, targetId: string) => void;
      }
    ) => ReturnType<typeof ProjectDiagramView>;
    const relationshipDocument: DiagramDocument = {
      ...document,
      nodes: [...document.nodes, { id: "ALT_PARENT", order: 2, mode: "absolute", fixed: true, x: 8, y: 0, width: 4, height: 2, title: "Alt Parent" }],
      edges: [
        { id: "tree:ROOT->CHILD", source: "ROOT", target: "CHILD", kind: "tree" },
        { id: "dependency:ROOT->CHILD", source: "ROOT", target: "CHILD", kind: "dependency" }
      ]
    };
    const markup = renderToStaticMarkup(
      <EditableProjectDiagramView
        document={relationshipDocument}
        onNodeAddDependency={() => undefined}
        onNodeAddUnlock={() => undefined}
        onNodeRemoveDependency={() => undefined}
        onNodeRemoveUnlock={() => undefined}
        onNodeSelect={() => undefined}
        selectedNodeId="CHILD"
        t={createTranslator("en")}
        title="Focuses"
      />
    );

    expect(markup).toContain('class="project-diagram-dependency-form"');
    expect(markup).toContain('class="project-diagram-unlock-form"');
    expect(markup).toContain("Add prerequisite");
    expect(markup).toContain("Add unlock");
    expect(markup).toContain('aria-label="Pick prerequisite on canvas"');
    expect(markup).toContain('aria-label="Pick unlock on canvas"');
    expect(markup).toContain('aria-label="Add prerequisite ALT_PARENT - Alt Parent"');
    expect(markup).toContain('aria-label="Add unlock ALT_PARENT - Alt Parent"');
    expect(markup).toContain('aria-label="Remove prerequisite ROOT - Root Focus"');
  });

  it("renders selected node reference edit controls", () => {
    const EditableProjectDiagramView = ProjectDiagramView as (
      props: Parameters<typeof ProjectDiagramView>[0] & {
        onNodeAddReference?: (sourceId: string, targetId: string) => void;
        onNodeRemoveReference?: (sourceId: string, targetId: string) => void;
      }
    ) => ReturnType<typeof ProjectDiagramView>;
    const relationshipDocument: DiagramDocument = {
      ...document,
      nodes: [...document.nodes, { id: "EXCLUSIVE", order: 2, mode: "absolute", fixed: true, x: 8, y: 0, width: 4, height: 2, title: "Exclusive Focus" }],
      edges: [
        { id: "tree:ROOT->CHILD", source: "ROOT", target: "CHILD", kind: "tree" },
        { id: "reference:CHILD->EXCLUSIVE", source: "CHILD", target: "EXCLUSIVE", kind: "reference" }
      ]
    };
    const markup = renderToStaticMarkup(
      <EditableProjectDiagramView
        document={relationshipDocument}
        onNodeAddReference={() => undefined}
        onNodeRemoveReference={() => undefined}
        onNodeSelect={() => undefined}
        selectedNodeId="CHILD"
        t={createTranslator("en")}
        title="Focuses"
      />
    );

    expect(markup).toContain('class="project-diagram-reference-form"');
    expect(markup).toContain("Add reference");
    expect(markup).toContain('aria-label="Pick reference on canvas"');
    expect(markup).toContain('aria-label="Remove reference EXCLUSIVE - Exclusive Focus"');
  });

  it("renders provider-declared relationship controls without family literals", () => {
    const relationshipDocument: DiagramDocument = {
      ...document,
      nodes: [
        ...document.nodes,
        {
          id: "ALT_PARENT",
          order: 2,
          mode: "absolute",
          fixed: true,
          x: 8,
          y: 0,
          width: 4,
          height: 2,
          title: "Alt Parent",
        },
      ],
      edges: [
        {
          id: "any_parent:ROOT->CHILD",
          source: "ROOT",
          target: "CHILD",
          kind: "dependency",
          relationshipKind: "any_parent",
        },
      ],
    };
    const markup = renderToStaticMarkup(
      <ProjectDiagramView
        document={relationshipDocument}
        onNodeSelect={() => undefined}
        onNodeSetRelationship={() => undefined}
        relationshipActions={[
          {
            cardinality: "many",
            kind: "any_parent",
            label: "Any parent",
            owner_endpoint: "target",
            selected_endpoint: "target",
            symmetric: false,
            visual_kind: "dependency",
          },
        ]}
        selectedNodeId="CHILD"
        t={createTranslator("en")}
        title="External tree"
      />,
    );

    expect(markup).toContain('data-relationship-kind="any_parent"');
    expect(markup).toContain('aria-label="Add Any parent"');
    expect(markup).toContain('aria-label="Pick Any parent on canvas"');
    expect(markup).toContain('aria-label="Add Any parent ALT_PARENT - Alt Parent"');
    expect(markup).toContain('aria-label="Remove Any parent ROOT - Root Focus"');
    expect(markup).not.toContain('aria-label="Add prerequisite"');
  });

  it("renders selected node parent edit controls", () => {
    const EditableProjectDiagramView = ProjectDiagramView as (
      props: Parameters<typeof ProjectDiagramView>[0] & {
        onNodeClearParent?: (nodeId: string) => void;
        onNodeSetParent?: (nodeId: string, parentId: string) => void;
      }
    ) => ReturnType<typeof ProjectDiagramView>;
    const relationshipDocument: DiagramDocument = {
      ...document,
      nodes: [...document.nodes, { id: "NEW_PARENT", order: 2, mode: "absolute", fixed: true, x: 8, y: 0, width: 4, height: 2, title: "New Parent" }]
    };
    const markup = renderToStaticMarkup(
      <EditableProjectDiagramView
        document={relationshipDocument}
        onNodeClearParent={() => undefined}
        onNodeSelect={() => undefined}
        onNodeSetParent={() => undefined}
        selectedNodeId="CHILD"
        t={createTranslator("en")}
        title="Focuses"
      />
    );

    expect(markup).toContain('class="project-diagram-parent-form"');
    expect(markup).toContain("Set parent");
    expect(markup).toContain('aria-label="Selected parent node id"');
    expect(markup).toContain('aria-label="Make selected node a root"');
    expect(markup).toContain("Make root");
  });

  it("renders quick candidate buttons for selected node relationship edits", () => {
    const EditableProjectDiagramView = ProjectDiagramView as (
      props: Parameters<typeof ProjectDiagramView>[0] & {
        onNodeAddDependency?: (targetId: string, sourceId: string) => void;
        onNodeAddReference?: (sourceId: string, targetId: string) => void;
        onNodeAddUnlock?: (sourceId: string, targetId: string) => void;
        onNodeSetParent?: (nodeId: string, parentId: string) => void;
      }
    ) => ReturnType<typeof ProjectDiagramView>;
    const relationshipDocument: DiagramDocument = {
      ...document,
      nodes: [
        ...document.nodes,
        { id: "ALT_PARENT", order: 2, mode: "absolute", fixed: true, x: 8, y: 0, width: 4, height: 2, title: "Alt Parent" },
        { id: "EXCLUSIVE", order: 3, mode: "absolute", fixed: true, x: 12, y: 0, width: 4, height: 2, title: "Exclusive Focus" }
      ],
      edges: [
        { id: "tree:ROOT->CHILD", source: "ROOT", target: "CHILD", kind: "tree" },
        { id: "dependency:ROOT->CHILD", source: "ROOT", target: "CHILD", kind: "dependency" },
        { id: "reference:CHILD->EXCLUSIVE", source: "CHILD", target: "EXCLUSIVE", kind: "reference" }
      ]
    };
    const markup = renderToStaticMarkup(
      <EditableProjectDiagramView
        document={relationshipDocument}
        onNodeAddDependency={() => undefined}
        onNodeAddReference={() => undefined}
        onNodeAddUnlock={() => undefined}
        onNodeSelect={() => undefined}
        onNodeSetParent={() => undefined}
        selectedNodeId="CHILD"
        t={createTranslator("en")}
        title="Focuses"
      />
    );

    expect(markup).toContain('class="project-diagram-candidate-list"');
    expect(markup).toContain('aria-label="Set parent ALT_PARENT - Alt Parent"');
    expect(markup).toContain('class="project-diagram-candidate-id">ALT_PARENT</span>');
    expect(markup).toContain('class="project-diagram-candidate-title">Alt Parent</span>');
    expect(markup).not.toContain('aria-label="Set parent ROOT"');
    expect(markup).toContain('aria-label="Add prerequisite ALT_PARENT - Alt Parent"');
    expect(markup).not.toContain('aria-label="Add prerequisite ROOT"');
    expect(markup).toContain('aria-label="Add unlock ALT_PARENT - Alt Parent"');
    expect(markup).not.toContain('aria-label="Add unlock NEXT"');
    expect(markup).toContain('aria-label="Add reference ALT_PARENT - Alt Parent"');
    expect(markup).not.toContain('aria-label="Add reference EXCLUSIVE"');
  });

  it("does not offer focus-tree context nodes as focus relationship candidates", () => {
    const EditableProjectDiagramView = ProjectDiagramView as (
      props: Parameters<typeof ProjectDiagramView>[0] & {
        onNodeAddDependency?: (targetId: string, sourceId: string) => void;
        onNodeAddReference?: (sourceId: string, targetId: string) => void;
        onNodeSetParent?: (nodeId: string, parentId: string) => void;
      }
    ) => ReturnType<typeof ProjectDiagramView>;
    const contextDocument: DiagramDocument = {
      schemaVersion: 1,
      gridSizePx: 24,
      nodes: [
        {
          id: "C08_PARTIV",
          order: 0,
          mode: "auto",
          width: 6,
          height: 2,
          title: "C08 Part IV",
          payload: {
            family: "focus_tree",
            familyId: "focus_tree",
            itemId: "focus_tree:C08_PARTIV",
            itemKind: "module",
            objectId: "C08_PARTIV",
            projectId: "PIHC3",
            relativeRoot: "src/modules/focus_tree/C08_PARTIV"
          }
        },
        {
          id: "FOCUS_NEW_ROOT",
          order: 1,
          mode: "auto",
          width: 4,
          height: 2,
          title: "Focus New Root",
          payload: {
            embeddedId: "FOCUS_NEW_ROOT",
            embeddedKind: "focus",
            family: "focus_tree",
            familyId: "focus_tree",
            itemId: "focus_tree:C08_PARTIV",
            itemKind: "module",
            objectId: "C08_PARTIV",
            projectId: "PIHC3",
            relativeRoot: "src/modules/focus_tree/C08_PARTIV"
          }
        }
      ],
      edges: []
    };
    const markup = renderToStaticMarkup(
      <EditableProjectDiagramView
        document={contextDocument}
        onNodeAddDependency={() => undefined}
        onNodeAddReference={() => undefined}
        onNodeSelect={() => undefined}
        onNodeSetParent={() => undefined}
        selectedNodeId="FOCUS_NEW_ROOT"
        t={createTranslator("en")}
        title="Focuses"
      />
    );

    expect(markup).not.toContain('class="project-diagram-parent-form"');
    expect(markup).not.toContain('class="project-diagram-dependency-form"');
    expect(markup).not.toContain('class="project-diagram-reference-form"');
    expect(markup).not.toContain('aria-label="Set parent C08_PARTIV - C08 Part IV"');
    expect(markup).not.toContain('aria-label="Add prerequisite C08_PARTIV - C08 Part IV"');
    expect(markup).not.toContain('aria-label="Add reference C08_PARTIV - C08 Part IV"');
  });

  it("does not offer embedded focus nodes as non-focus relationship candidates", () => {
    const EditableProjectDiagramView = ProjectDiagramView as (
      props: Parameters<typeof ProjectDiagramView>[0] & {
        onNodeAddDependency?: (targetId: string, sourceId: string) => void;
        onNodeAddReference?: (sourceId: string, targetId: string) => void;
        onNodeSetParent?: (nodeId: string, parentId: string) => void;
      }
    ) => ReturnType<typeof ProjectDiagramView>;
    const mixedDocument: DiagramDocument = {
      schemaVersion: 1,
      gridSizePx: 24,
      nodes: [
        {
          id: "TECH_CONTEXT",
          order: 0,
          mode: "auto",
          width: 6,
          height: 2,
          title: "Technology Context",
          payload: {
            family: "technology",
            familyId: "technology",
            itemId: "technology:C08_ARMY",
            itemKind: "module",
            objectId: "C08_ARMY",
            projectId: "PIHC3",
            relativeRoot: "src/modules/technology/C08_ARMY"
          }
        },
        {
          id: "FOCUS_NEW_ROOT",
          order: 1,
          mode: "auto",
          width: 4,
          height: 2,
          title: "Focus New Root",
          payload: {
            embeddedId: "FOCUS_NEW_ROOT",
            embeddedKind: "focus",
            family: "focus_tree",
            familyId: "focus_tree",
            itemId: "focus_tree:C08_PARTIV",
            itemKind: "module",
            objectId: "C08_PARTIV",
            projectId: "PIHC3",
            relativeRoot: "src/modules/focus_tree/C08_PARTIV"
          }
        },
        {
          id: "FOCUS_CONTEXT",
          order: 2,
          mode: "auto",
          width: 6,
          height: 2,
          title: "Focus Context",
          payload: {
            family: "focus_tree",
            familyId: "focus_tree",
            itemId: "focus_tree:C08_PARTIV",
            itemKind: "module",
            objectId: "C08_PARTIV",
            projectId: "PIHC3",
            relativeRoot: "src/modules/focus_tree/C08_PARTIV"
          }
        },
        {
          id: "TECH_PEER",
          order: 3,
          mode: "auto",
          width: 4,
          height: 2,
          title: "Technology Peer",
          payload: {
            family: "technology",
            familyId: "technology",
            itemId: "technology:C08_NAVY",
            itemKind: "module",
            objectId: "C08_NAVY",
            projectId: "PIHC3",
            relativeRoot: "src/modules/technology/C08_NAVY"
          }
        }
      ],
      edges: []
    };
    const markup = renderToStaticMarkup(
      <EditableProjectDiagramView
        document={mixedDocument}
        onNodeAddDependency={() => undefined}
        onNodeAddReference={() => undefined}
        onNodeSelect={() => undefined}
        onNodeSetParent={() => undefined}
        selectedNodeId="TECH_CONTEXT"
        t={createTranslator("en")}
        title="Technologies"
      />
    );

    expect(markup).toContain('aria-label="Set parent TECH_PEER - Technology Peer"');
    expect(markup).toContain('aria-label="Add prerequisite TECH_PEER - Technology Peer"');
    expect(markup).toContain('aria-label="Add reference TECH_PEER - Technology Peer"');
    expect(markup).not.toContain('aria-label="Set parent FOCUS_NEW_ROOT - Focus New Root"');
    expect(markup).not.toContain('aria-label="Add prerequisite FOCUS_NEW_ROOT - Focus New Root"');
    expect(markup).not.toContain('aria-label="Add reference FOCUS_NEW_ROOT - Focus New Root"');
    expect(markup).not.toContain('aria-label="Set parent FOCUS_CONTEXT - Focus Context"');
    expect(markup).not.toContain('aria-label="Add prerequisite FOCUS_CONTEXT - Focus Context"');
    expect(markup).not.toContain('aria-label="Add reference FOCUS_CONTEXT - Focus Context"');
  });

  it("does not offer embedded focus nodes from other focus trees as relationship candidates", () => {
    const EditableProjectDiagramView = ProjectDiagramView as (
      props: Parameters<typeof ProjectDiagramView>[0] & {
        onNodeAddDependency?: (targetId: string, sourceId: string) => void;
        onNodeAddReference?: (sourceId: string, targetId: string) => void;
        onNodeSetParent?: (nodeId: string, parentId: string) => void;
      }
    ) => ReturnType<typeof ProjectDiagramView>;
    const mixedDocument: DiagramDocument = {
      schemaVersion: 1,
      gridSizePx: 24,
      nodes: [
        {
          id: "FOCUS_ROOT",
          order: 0,
          mode: "auto",
          width: 4,
          height: 2,
          title: "Focus Root",
          payload: {
            embeddedId: "FOCUS_ROOT",
            embeddedKind: "focus",
            family: "focus_tree",
            familyId: "focus_tree",
            itemId: "focus_tree:C08_PARTIV",
            itemKind: "module",
            objectId: "C08_PARTIV",
            projectId: "PIHC3",
            relativeRoot: "src/modules/focus_tree/C08_PARTIV"
          }
        },
        {
          id: "FOCUS_CHILD",
          order: 1,
          mode: "auto",
          width: 4,
          height: 2,
          title: "Focus Child",
          payload: {
            embeddedId: "FOCUS_CHILD",
            embeddedKind: "focus",
            family: "focus_tree",
            familyId: "focus_tree",
            itemId: "focus_tree:C08_PARTIV",
            itemKind: "module",
            objectId: "C08_PARTIV",
            projectId: "PIHC3",
            relativeRoot: "src/modules/focus_tree/C08_PARTIV"
          }
        },
        {
          id: "FOREIGN_FOCUS",
          order: 2,
          mode: "auto",
          width: 4,
          height: 2,
          title: "Foreign Focus",
          payload: {
            embeddedId: "FOREIGN_FOCUS",
            embeddedKind: "focus",
            family: "focus_tree",
            familyId: "focus_tree",
            itemId: "focus_tree:C09_PARTV",
            itemKind: "module",
            objectId: "C09_PARTV",
            projectId: "PIHC3",
            relativeRoot: "src/modules/focus_tree/C09_PARTV"
          }
        }
      ],
      edges: []
    };
    const markup = renderToStaticMarkup(
      <EditableProjectDiagramView
        document={mixedDocument}
        onNodeAddDependency={() => undefined}
        onNodeAddReference={() => undefined}
        onNodeSelect={() => undefined}
        onNodeSetParent={() => undefined}
        selectedNodeId="FOCUS_ROOT"
        t={createTranslator("en")}
        title="Focuses"
      />
    );

    expect(markup).toContain('aria-label="Set parent FOCUS_CHILD - Focus Child"');
    expect(markup).toContain('aria-label="Add prerequisite FOCUS_CHILD - Focus Child"');
    expect(markup).toContain('aria-label="Add reference FOCUS_CHILD - Focus Child"');
    expect(markup).not.toContain('aria-label="Set parent FOREIGN_FOCUS - Foreign Focus"');
    expect(markup).not.toContain('aria-label="Add prerequisite FOREIGN_FOCUS - Foreign Focus"');
    expect(markup).not.toContain('aria-label="Add reference FOREIGN_FOCUS - Foreign Focus"');
  });

  it("does not offer selected unlocks as new prerequisite candidates", () => {
    const EditableProjectDiagramView = ProjectDiagramView as (
      props: Parameters<typeof ProjectDiagramView>[0] & {
        onNodeAddDependency?: (targetId: string, sourceId: string) => void;
      }
    ) => ReturnType<typeof ProjectDiagramView>;
    const relationshipDocument: DiagramDocument = {
      ...document,
      nodes: [
        ...document.nodes,
        { id: "NEXT", parentId: "CHILD", order: 2, mode: "auto", width: 4, height: 2, title: "Next Focus" },
        { id: "LATER", parentId: "NEXT", order: 3, mode: "auto", width: 4, height: 2, title: "Later Focus" },
        { id: "ALT_PARENT", order: 3, mode: "absolute", fixed: true, x: 8, y: 0, width: 4, height: 2, title: "Alt Parent" }
      ],
      edges: [
        { id: "dependency:ROOT->CHILD", source: "ROOT", target: "CHILD", kind: "dependency" },
        { id: "dependency:CHILD->NEXT", source: "CHILD", target: "NEXT", kind: "dependency" },
        { id: "dependency:NEXT->LATER", source: "NEXT", target: "LATER", kind: "dependency" }
      ]
    };
    const markup = renderToStaticMarkup(
      <EditableProjectDiagramView
        document={relationshipDocument}
        onNodeAddDependency={() => undefined}
        onNodeSelect={() => undefined}
        selectedNodeId="CHILD"
        t={createTranslator("en")}
        title="Focuses"
      />
    );

    expect(markup).toContain('aria-label="Add prerequisite ALT_PARENT - Alt Parent"');
    expect(markup).not.toContain('aria-label="Add prerequisite NEXT - Next Focus"');
    expect(markup).not.toContain('aria-label="Add prerequisite LATER - Later Focus"');
  });

  it("renders a minimap with selected node and viewport feedback", () => {
    const markup = renderToStaticMarkup(<ProjectDiagramView document={document} onNodeSelect={() => undefined} selectedNodeId="CHILD" t={createTranslator("en")} title="Focuses" />);

    expect(markup).toContain('class="project-diagram-minimap"');
    expect(markup).toContain('aria-label="Diagram minimap"');
    expect(markup).toContain('role="button"');
    expect(markup).toContain('tabindex="0"');
    expect(markup).toContain('class="project-diagram-minimap-node selected"');
    expect(markup).toContain('class="project-diagram-minimap-viewport"');
    expect(markup).toContain('aria-label="Visible diagram area"');
  });
});
