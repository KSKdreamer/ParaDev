# React TypeScript Diagram Browser & Editor Design

**Date:** 2026-06-19
**Audience:** frontend, backend, and product engineers
**Decision:** Use **React Flow / xyflow** for the React canvas/editor, and implement a separate **canonical tree layout model** plus optional **Python layout service** for authoritative layout semantics.

---

## 1. Background

We need to add a diagram browser and editor to a React TypeScript GUI.

The editor is not a generic graph viewer. It is a domain-specific tree editor where each node has an image, tree parent/child relationships, editable coordinates, and deterministic behavior when nodes are moved, inserted, pinned, unpinned, or re-auto-positioned.

The expected behavior includes:

- A grid-aligned infinite or bounded canvas.
- Tree nodes rendered as image-based custom UI components.
- Directed tree edges from parent to child.
- Clickable nodes that open an info popup, side panel, or modal.
- Zooming and panning.
- Minimap or thumbnail navigation.
- Dragging nodes to reposition them.
- Dragging the canvas viewport.
- Pin all, unpin all, auto-layout all.
- Per-subtree layout operations.
- Persistent/exportable node coordinates and positioning modes.
- Optional Python backend that can receive the full diagram state, modify coordinates, enforce layout policy, and return resolved positions.

The critical architectural constraint is that the editor must support **three coordinate modes**:

1. **Absolute / pinned position**
   - Node owns absolute `(x, y)` grid coordinates.
   - Coordinates are forced to integer grid units.
   - User-edited layout should be preserved unless explicitly re-layouted.

2. **Relative position**
   - Node position is stored as `(dx, dy)` relative to its parent.
   - Node follows parent movement while preserving manual relative offset.

3. **Auto position**
   - Node position is calculated automatically relative to its parent.
   - Calculation should consider siblings, subtree sizes, fixed nodes, and layout policy.

This is specific enough that no off-the-shelf diagram library should own the domain model. The canvas library should render and handle interaction; our application should own the canonical layout semantics.

---

## 2. Goals

### Functional goals

The editor must support:

- Add node.
- Delete node or subtree.
- Insert child node.
- Reorder siblings.
- Drag node.
- Drag subtree.
- Move parent while keeping children fixed.
- Move parent and re-auto-layout descendants.
- Pin node.
- Unpin node.
- Pin subtree.
- Unpin subtree.
- Pin all nodes.
- Unpin all nodes.
- Auto-layout subtree.
- Auto-layout all.
- Save diagram state.
- Restore diagram state.
- Export/import canonical JSON.
- Open node info popup on click.
- Optional backend-controlled layout.

### UX goals

The editor should feel like an industrial diagram editor:

- Smooth pan/zoom.
- Clear grid.
- Snap-to-grid node positioning.
- Stable deterministic layout.
- Explicit layout commands, not surprising implicit rearrangement.
- Minimap for navigation.
- Visual distinction between pinned, relative, and auto nodes.
- Layout preview before commit where practical.
- Undo/redo-friendly command model.

### Engineering goals

The implementation should be:

- React TypeScript-native.
- Open-source-friendly.
- Maintainable under product-specific layout rules.
- Testable without a browser for layout behavior.
- Capable of delegating layout to Python without making mouse-drag interactions dependent on backend latency.
- Safe for future migration if the rendering library changes.

---

## 3. Recommended technology choice

### Primary choice: React Flow / xyflow

Use:

```bash
npm install @xyflow/react
```

React Flow is the recommended canvas/editor substrate because it directly supports the necessary UI primitives:

- React-based custom nodes.
- Controlled nodes and edges.
- Custom edge types.
- Node click handlers.
- Node drag start / drag / drag stop handlers.
- Canvas pan and zoom.
- Min/max zoom.
- `fitView`.
- Snap-to-grid.
- Configurable snap grid.
- Background grid component.
- Minimap component.
- Controlled viewport.
- Save/restore examples.
- React TypeScript API.

React Flow’s `<ReactFlow />` component renders nodes and edges and handles user interaction. It supports custom node types through `nodeTypes`, where a node type maps to a React component. It also exposes snap-to-grid configuration, viewport controls, node click handlers, node drag handlers, deletion hooks, and interaction props.

Relevant official docs:

- React Flow API reference: https://reactflow.dev/api-reference
- `<ReactFlow />` component: https://reactflow.dev/api-reference/react-flow
- `<Background />` component: https://reactflow.dev/api-reference/components/background
- `<MiniMap />` component: https://reactflow.dev/api-reference/components/minimap
- Layouting overview: https://reactflow.dev/learn/layouting/layouting
- Examples: https://reactflow.dev/examples

### Why React Flow should not own layout semantics

React Flow should be treated as a rendering and interaction layer. It should not be the source of truth for our business layout model.

The application should own:

- Parent/child tree.
- Node ordering.
- Position mode.
- Absolute coordinates.
- Relative offsets.
- Auto-layout policy.
- Fixed/pinned behavior.
- Subtree movement behavior.
- Persistence format.
- Backend layout protocol.

React Flow node positions should be generated from our canonical model. In other words:

```text
Canonical diagram model
  -> resolved layout coordinates
    -> projected React Flow nodes/edges
      -> rendered canvas
```

Dragging or editing in React Flow should emit commands that update the canonical model, not directly become the persisted model.

---

## 4. Alternatives considered

### AntV X6

AntV X6 is a strong alternative if we want a lower-level diagramming engine with MVC architecture and built-in diagram-editor extensions. It supports SVG/HTML rendering, React/Vue/Angular customization, event systems, minimap, alignment lines, lasso selection, and a data-driven architecture.

Relevant docs/repo:

- GitHub: https://github.com/antvis/X6
- Docs: https://x6.antv.antgroup.com/

Use X6 if:

- We want a framework-agnostic diagramming engine.
- We prefer a graph-engine/MVC architecture over React component composition.
- We need more out-of-the-box diagram-editor plugins and are comfortable adapting them into React.

Do not choose X6 as the first option if:

- The rest of the GUI is strongly React TypeScript.
- Nodes should be normal React components.
- We want the most convenient React-native developer experience.

### ELK.js

ELK.js is not a rendering library. It is a layout engine. It can compute node positions for diagrams, especially directed node-link diagrams with layered layout and ports.

Relevant repo:

- https://github.com/kieler/elkjs

Use ELK.js as an optional layout assist when:

- The graph becomes more DAG-like than tree-like.
- We introduce cross-links.
- We need port-aware edge routing.
- We need sophisticated layered graph layout.

Do not use ELK.js as the canonical model. Use it only to produce candidate positions that are then reconciled with our pinned/relative/auto rules.

### Dagre / D3-Hierarchy

Dagre and D3-Hierarchy are useful for simple tree layout. React Flow’s own layouting docs discuss these as layout options.

Use them only for quick prototypes or simple auto-layout modes. They are not sufficient as the whole layout system because our layout has pinned nodes, relative nodes, explicit subtree policies, and Python-controlled constraints.

---

## 5. Architecture

### High-level architecture

```text
React UI
  ├─ DiagramCanvas.tsx
  │   ├─ ReactFlow
  │   ├─ Background
  │   ├─ MiniMap
  │   ├─ Controls / custom toolbar
  │   └─ custom node + custom edge components
  │
  ├─ DiagramCommandController
  │   ├─ dragNode
  │   ├─ insertChild
  │   ├─ pinNode
  │   ├─ unpinNode
  │   ├─ autoLayoutSubtree
  │   └─ save/export
  │
  ├─ LayoutEngine.ts
  │   ├─ resolveWorldPositions
  │   ├─ applyMovePolicy
  │   ├─ packAutoChildren
  │   ├─ computeSubtreeBounds
  │   └─ snapToGrid
  │
  └─ optional BackendLayoutClient
      └─ FastAPI /diagram/layout

Backend
  └─ Python Layout Service
      ├─ validate diagram
      ├─ enforce domain constraints
      ├─ compute authoritative layout
      └─ return resolved positions + changed nodes
```

### Core principle

The application should distinguish between:

1. **Canonical nodes**
   - Persistent semantic source of truth.

2. **Resolved nodes**
   - Result of applying parent relationships, modes, and layout rules.

3. **React Flow nodes**
   - UI projection of resolved nodes into pixel coordinates.

```text
DiagramNode[] + DiagramEdge[]
  -> ResolvedNode[]
    -> ReactFlow Node[] + Edge[]
```

---

## 6. Canonical data model

Use grid units internally. Do not persist pixels.

Recommended TypeScript model:

```ts
export type NodeId = string;

export type PositionMode = "absolute" | "relative" | "auto";

export type MovePolicy =
  | "move_subtree"
  | "keep_descendants"
  | "reauto_descendants";

export interface DiagramNode {
  id: NodeId;

  /**
   * Tree structure.
   * Root nodes have no parentId.
   */
  parentId?: NodeId | null;

  /**
   * Sibling ordering under the same parent.
   * Used by auto-layout.
   */
  order: number;

  /**
   * absolute:
   *   use x/y as world grid coordinates.
   *
   * relative:
   *   use dx/dy relative to parent world coordinate.
   *
   * auto:
   *   layout engine computes position.
   */
  mode: PositionMode;

  /**
   * Absolute position in grid units.
   * Required when mode === "absolute".
   */
  x?: number;
  y?: number;

  /**
   * Relative position in grid units.
   * Required when mode === "relative".
   */
  dx?: number;
  dy?: number;

  /**
   * Stronger manual-layout signal.
   * Usually fixed=true implies mode="absolute",
   * but keep both fields because "fixed" may be useful
   * as a layout constraint even during temporary operations.
   */
  fixed?: boolean;

  /**
   * Node visual size in grid units.
   * If rendered pixel size is measured dynamically,
   * convert to grid units before layout.
   */
  width: number;
  height: number;

  /**
   * Image and domain payload.
   */
  imageUrl?: string;
  title?: string;
  payload?: unknown;
}

export interface DiagramEdge {
  id: string;
  source: NodeId;
  target: NodeId;
  kind: "tree" | "reference" | "dependency";
}

export interface DiagramDocument {
  schemaVersion: 1;
  gridSizePx: number;
  nodes: DiagramNode[];
  edges: DiagramEdge[];
  viewport?: {
    x: number;
    y: number;
    zoom: number;
  };
}
```

Resolved node:

```ts
export interface ResolvedNode extends DiagramNode {
  worldX: number;
  worldY: number;
  subtreeBounds?: {
    minX: number;
    minY: number;
    maxX: number;
    maxY: number;
  };
}
```

Projection to React Flow:

```ts
import type { Node, Edge } from "@xyflow/react";

export function toReactFlowNode(
  node: ResolvedNode,
  gridSizePx: number,
): Node {
  return {
    id: node.id,
    type: "imageNode",
    position: {
      x: node.worldX * gridSizePx,
      y: node.worldY * gridSizePx,
    },
    data: {
      title: node.title,
      imageUrl: node.imageUrl,
      mode: node.mode,
      fixed: node.fixed,
      payload: node.payload,
    },
    draggable: true,
    selectable: true,
  };
}

export function toReactFlowEdge(edge: DiagramEdge): Edge {
  return {
    id: edge.id,
    source: edge.source,
    target: edge.target,
    type: edge.kind === "tree" ? "smoothstep" : "default",
  };
}
```

---

## 7. Positioning rules

### Absolute / pinned mode

Absolute nodes store world grid coordinates:

```text
worldX = x
worldY = y
```

Rules:

- `x` and `y` must be integers.
- Dragging an auto node manually should usually convert it to absolute mode.
- Pinning a node sets `mode = "absolute"` and stores current resolved world position into `x/y`.
- Pinned nodes should be respected by auto-layout unless the user runs an explicit destructive layout command.

Example:

```ts
function pinNode(node: DiagramNode, resolved: ResolvedNode): DiagramNode {
  return {
    ...node,
    mode: "absolute",
    fixed: true,
    x: Math.round(resolved.worldX),
    y: Math.round(resolved.worldY),
    dx: undefined,
    dy: undefined,
  };
}
```

### Relative mode

Relative nodes store offsets from parent:

```text
worldX = parent.worldX + dx
worldY = parent.worldY + dy
```

Rules:

- `dx` and `dy` must be integers.
- Relative nodes move naturally with their parent.
- Dragging a relative node may either:
  - update `dx/dy`, preserving relative mode, or
  - convert to absolute mode, depending on UI command.
- Relative nodes are useful for manually-adjusted children that should remain attached to the parent’s movement.

Example:

```ts
function resolveRelativeNode(
  node: DiagramNode,
  parent: ResolvedNode,
): ResolvedNode {
  if (node.dx == null || node.dy == null) {
    throw new Error(`Relative node ${node.id} is missing dx/dy`);
  }

  return {
    ...node,
    worldX: parent.worldX + node.dx,
    worldY: parent.worldY + node.dy,
  };
}
```

### Auto mode

Auto nodes do not own coordinates. The layout engine computes them.

Rules:

- Auto nodes are placed relative to parent.
- Sibling order matters.
- Node sizes matter.
- Fixed/absolute siblings should be respected.
- Final coordinates must be snapped to integer grid units.
- Auto-layout should be deterministic: same input produces same output.

Basic layout equation:

```text
auto child position = f(parent, siblings, sibling order, subtree sizes, layout policy)
```

For the first implementation, prefer a deterministic custom tree layout instead of a generic graph layout engine. A practical policy:

```text
For each parent:
  1. Keep absolute/fixed children at their current world coordinates.
  2. Place relative children at parent + dx/dy.
  3. Compute subtree sizes for all auto children.
  4. Pack auto children into sibling slots.
  5. Snap all final positions to integer grid.
```

---

## 8. Subtree move policies

When a node moves, do not make descendant behavior implicit. The UI should expose an explicit move policy.

### Policy A: move subtree

Use when the user wants to drag an entire branch.

Behavior:

```text
delta = newParentWorld - oldParentWorld

for each descendant:
  if descendant.mode === "absolute":
    descendant.x += delta.x
    descendant.y += delta.y

  if descendant.mode === "relative":
    keep dx/dy unchanged

  if descendant.mode === "auto":
    keep auto mode; resolve from new parent position
```

This preserves branch shape.

### Policy B: keep descendants fixed

Use when the user wants to move a logical parent but preserve descendant world positions.

Behavior:

```text
parent moves
each descendant keeps previous worldX/worldY

for each relative child:
  recompute dx/dy against the moved parent

for each auto child that must stay fixed:
  convert to absolute, or mark temporarily fixed
```

This is useful when the hierarchy changes but visual layout should remain stable.

### Policy C: re-auto-position descendants

Use when the user wants to clean up a branch after moving or editing.

Behavior:

```text
parent moves
absolute/fixed descendants stay fixed unless policy says otherwise
auto descendants are recalculated
relative descendants preserve dx/dy
```

This should be available as “Re-layout subtree”.

---

## 9. Layout engine design

### Recommended first implementation

Start with a custom deterministic tree layout.

Why:

- The data is a tree, not an arbitrary graph.
- The positioning modes are domain-specific.
- Pinned/relative/auto semantics need precise control.
- The layout must be predictable and testable.
- Python backend integration should be straightforward.

Suggested layout policy:

```ts
export interface TreeLayoutPolicy {
  direction: "vertical" | "horizontal";
  siblingGap: number;      // grid units
  levelGap: number;        // grid units
  subtreeGap: number;      // grid units
  respectPinned: boolean;
  snapToGrid: boolean;
  defaultNodeWidth: number;
  defaultNodeHeight: number;
}
```

Position resolution:

```ts
export function resolveWorldPositions(
  document: DiagramDocument,
  policy: TreeLayoutPolicy,
): ResolvedNode[] {
  // 1. Validate acyclic tree.
  // 2. Build parent -> children index.
  // 3. Resolve roots.
  // 4. Compute subtree bounds bottom-up.
  // 5. Resolve each node according to mode.
  // 6. Pack auto children.
  // 7. Snap all positions.
  // 8. Return resolved nodes.
  throw new Error("Implement in LayoutEngine.ts");
}
```

### Pseudocode for auto child packing

```ts
function layoutChildren(parent: ResolvedNode, children: DiagramNode[]): ResolvedNode[] {
  const fixedChildren = children.filter(c => c.mode === "absolute" || c.fixed);
  const relativeChildren = children.filter(c => c.mode === "relative" && !c.fixed);
  const autoChildren = children
    .filter(c => c.mode === "auto" && !c.fixed)
    .sort((a, b) => a.order - b.order);

  const resolvedFixed = fixedChildren.map(resolveAbsolute);
  const resolvedRelative = relativeChildren.map(c => resolveRelative(c, parent));

  const occupied = computeOccupiedIntervals([...resolvedFixed, ...resolvedRelative]);

  const resolvedAuto = packAutoChildren({
    parent,
    autoChildren,
    occupied,
    siblingGap: policy.siblingGap,
    levelGap: policy.levelGap,
  });

  return [
    ...resolvedFixed,
    ...resolvedRelative,
    ...resolvedAuto,
  ];
}
```

### Grid snapping

Use integer grid units internally:

```ts
function snapGrid(value: number): number {
  return Math.round(value);
}
```

React Flow snap grid should be configured in pixels:

```tsx
<ReactFlow
  nodes={nodes}
  edges={edges}
  snapToGrid
  snapGrid={[document.gridSizePx, document.gridSizePx]}
/>
```

Do not persist React Flow pixel positions. Convert them back to grid units:

```ts
function pixelToGridPosition(
  position: { x: number; y: number },
  gridSizePx: number,
): { x: number; y: number } {
  return {
    x: Math.round(position.x / gridSizePx),
    y: Math.round(position.y / gridSizePx),
  };
}
```

---

## 10. React Flow integration

### Canvas skeleton

```tsx
import {
  Background,
  BackgroundVariant,
  Controls,
  MiniMap,
  ReactFlow,
  ReactFlowProvider,
  type Node,
  type Edge,
  type OnNodeDrag,
} from "@xyflow/react";

import "@xyflow/react/dist/style.css";

const nodeTypes = {
  imageNode: ImageNode,
};

export function DiagramEditor(props: {
  document: DiagramDocument;
  onCommand: (command: DiagramCommand) => void;
}) {
  const resolved = resolveWorldPositions(props.document, defaultLayoutPolicy);

  const rfNodes: Node[] = resolved.map(node =>
    toReactFlowNode(node, props.document.gridSizePx),
  );

  const rfEdges: Edge[] = props.document.edges.map(toReactFlowEdge);

  return (
    <ReactFlowProvider>
      <ReactFlow
        nodes={rfNodes}
        edges={rfEdges}
        nodeTypes={nodeTypes}
        fitView
        minZoom={0.1}
        maxZoom={4}
        snapToGrid
        snapGrid={[props.document.gridSizePx, props.document.gridSizePx]}
        onNodeClick={(event, node) => {
          props.onCommand({ type: "open_node_popup", nodeId: node.id });
        }}
        onNodeDragStop={(event, node) => {
          const { x, y } = pixelToGridPosition(
            node.position,
            props.document.gridSizePx,
          );

          props.onCommand({
            type: "move_node",
            nodeId: node.id,
            x,
            y,
            modeAfterDrag: "absolute",
            movePolicy: "move_subtree",
          });
        }}
      >
        <Background
          gap={props.document.gridSizePx}
          variant={BackgroundVariant.Lines}
        />
        <MiniMap pannable zoomable />
        <Controls />
      </ReactFlow>
    </ReactFlowProvider>
  );
}
```

### Custom image node

```tsx
import type { NodeProps } from "@xyflow/react";

export function ImageNode(props: NodeProps) {
  const { data, selected } = props;

  return (
    <div
      className={[
        "diagram-node",
        selected ? "diagram-node--selected" : "",
        data.fixed ? "diagram-node--fixed" : "",
        `diagram-node--mode-${data.mode}`,
      ].join(" ")}
    >
      {data.imageUrl ? (
        <img
          className="diagram-node__image"
          src={String(data.imageUrl)}
          alt={String(data.title ?? "node")}
          draggable={false}
        />
      ) : (
        <div className="diagram-node__placeholder" />
      )}

      <div className="diagram-node__title">
        {String(data.title ?? props.id)}
      </div>

      <div className="diagram-node__badge">
        {String(data.mode)}
      </div>
    </div>
  );
}
```

Recommended CSS intent:

```css
.diagram-node {
  width: 96px;
  min-height: 96px;
  border: 1px solid var(--node-border);
  border-radius: 8px;
  background: var(--node-bg);
  overflow: hidden;
  user-select: none;
}

.diagram-node--selected {
  outline: 2px solid var(--selection);
}

.diagram-node--fixed .diagram-node__badge {
  font-weight: 700;
}

.diagram-node__image {
  display: block;
  width: 100%;
  height: 72px;
  object-fit: contain;
}

.diagram-node__title {
  padding: 4px 6px;
  font-size: 12px;
}

.diagram-node__badge {
  padding: 0 6px 4px;
  font-size: 10px;
  opacity: 0.7;
}
```

---

## 11. Command model

Do not scatter layout edits across React components. Define explicit commands.

```ts
export type DiagramCommand =
  | { type: "open_node_popup"; nodeId: NodeId }
  | {
      type: "move_node";
      nodeId: NodeId;
      x: number;
      y: number;
      modeAfterDrag: "absolute" | "relative";
      movePolicy: MovePolicy;
    }
  | { type: "insert_child"; parentId: NodeId; node: DiagramNode }
  | { type: "delete_node"; nodeId: NodeId; deleteSubtree: boolean }
  | { type: "pin_node"; nodeId: NodeId }
  | { type: "unpin_node"; nodeId: NodeId; targetMode: "relative" | "auto" }
  | { type: "pin_subtree"; nodeId: NodeId }
  | { type: "unpin_subtree"; nodeId: NodeId; targetMode: "auto" }
  | { type: "pin_all" }
  | { type: "unpin_all"; targetMode: "auto" }
  | { type: "auto_layout_subtree"; nodeId: NodeId }
  | { type: "auto_layout_all" }
  | { type: "save_viewport"; viewport: { x: number; y: number; zoom: number } };
```

Command handlers should:

1. Receive current canonical document.
2. Resolve current positions if needed.
3. Apply semantic command.
4. Normalize grid positions.
5. Validate tree and coordinates.
6. Return next canonical document.
7. Push to undo/redo history.

---

## 12. Python backend layout service

### When to use Python

Use Python for:

- Authoritative layout computation.
- Complex domain-specific layout constraints.
- Bulk layout.
- Import/export validation.
- Project-level consistency checks.
- Automated migration of old diagram versions.
- Server-side collaboration conflict resolution.

Do not use Python for every drag frame. Mouse movement must stay local and immediate. Call Python on commit events:

- `dragStop`
- `insertChild`
- `deleteNode`
- `pinAll`
- `unpinAll`
- `autoLayoutSubtree`
- `autoLayoutAll`
- `importDiagram`
- `normalizeDiagram`

### Suggested API

```http
POST /diagram/layout
```

Request:

```json
{
  "schemaVersion": 1,
  "gridSizePx": 32,
  "nodes": [
    {
      "id": "root",
      "parentId": null,
      "order": 0,
      "mode": "absolute",
      "x": 10,
      "y": 5,
      "fixed": true,
      "width": 3,
      "height": 2,
      "title": "Root"
    },
    {
      "id": "child-1",
      "parentId": "root",
      "order": 0,
      "mode": "auto",
      "width": 3,
      "height": 2,
      "title": "Child 1"
    }
  ],
  "edges": [
    {
      "id": "root->child-1",
      "source": "root",
      "target": "child-1",
      "kind": "tree"
    }
  ],
  "operation": {
    "type": "auto_layout_subtree",
    "nodeId": "root"
  },
  "policy": {
    "direction": "vertical",
    "siblingGap": 2,
    "levelGap": 4,
    "subtreeGap": 2,
    "respectPinned": true,
    "snapToGrid": true
  }
}
```

Response:

```json
{
  "schemaVersion": 1,
  "resolvedNodes": [
    {
      "id": "root",
      "worldX": 10,
      "worldY": 5,
      "mode": "absolute",
      "fixed": true
    },
    {
      "id": "child-1",
      "worldX": 10,
      "worldY": 11,
      "mode": "auto",
      "fixed": false
    }
  ],
  "canonicalPatch": [
    {
      "op": "replace",
      "path": "/nodes/1/mode",
      "value": "auto"
    }
  ],
  "changedNodeIds": ["child-1"],
  "warnings": []
}
```

### FastAPI skeleton

```py
from pydantic import BaseModel, Field
from typing import Literal, Optional, Any
from fastapi import FastAPI

PositionMode = Literal["absolute", "relative", "auto"]
MovePolicy = Literal["move_subtree", "keep_descendants", "reauto_descendants"]

class DiagramNode(BaseModel):
    id: str
    parentId: Optional[str] = None
    order: int = 0
    mode: PositionMode
    x: Optional[int] = None
    y: Optional[int] = None
    dx: Optional[int] = None
    dy: Optional[int] = None
    fixed: bool = False
    width: int = 3
    height: int = 2
    title: Optional[str] = None
    imageUrl: Optional[str] = None
    payload: Optional[Any] = None

class DiagramEdge(BaseModel):
    id: str
    source: str
    target: str
    kind: Literal["tree", "reference", "dependency"] = "tree"

class LayoutPolicy(BaseModel):
    direction: Literal["vertical", "horizontal"] = "vertical"
    siblingGap: int = 2
    levelGap: int = 4
    subtreeGap: int = 2
    respectPinned: bool = True
    snapToGrid: bool = True

class LayoutOperation(BaseModel):
    type: str
    nodeId: Optional[str] = None

class LayoutRequest(BaseModel):
    schemaVersion: int = 1
    gridSizePx: int = 32
    nodes: list[DiagramNode]
    edges: list[DiagramEdge]
    operation: LayoutOperation
    policy: LayoutPolicy = Field(default_factory=LayoutPolicy)

class ResolvedNode(BaseModel):
    id: str
    worldX: int
    worldY: int
    mode: PositionMode
    fixed: bool = False

class LayoutResponse(BaseModel):
    schemaVersion: int = 1
    resolvedNodes: list[ResolvedNode]
    changedNodeIds: list[str]
    warnings: list[str] = []

app = FastAPI()

@app.post("/diagram/layout", response_model=LayoutResponse)
def layout_diagram(req: LayoutRequest) -> LayoutResponse:
    # 1. Validate tree.
    # 2. Resolve absolute and relative nodes.
    # 3. Compute auto-layout.
    # 4. Respect pinned nodes.
    # 5. Snap to grid.
    # 6. Return resolved positions.
    resolved = []
    warnings = []

    # Placeholder only. Implement real layout in a separate pure function.
    for n in req.nodes:
        if n.mode == "absolute":
            if n.x is None or n.y is None:
                warnings.append(f"Absolute node {n.id} missing x/y; defaulted to 0/0")
            resolved.append(
                ResolvedNode(
                    id=n.id,
                    worldX=n.x or 0,
                    worldY=n.y or 0,
                    mode=n.mode,
                    fixed=n.fixed,
                )
            )

    return LayoutResponse(
        resolvedNodes=resolved,
        changedNodeIds=[n.id for n in req.nodes],
        warnings=warnings,
    )
```

---

## 13. Persistence and export format

Persist the canonical document, not raw React Flow state.

Good persisted state:

```json
{
  "schemaVersion": 1,
  "gridSizePx": 32,
  "nodes": [
    {
      "id": "a",
      "parentId": null,
      "order": 0,
      "mode": "absolute",
      "x": 10,
      "y": 5,
      "fixed": true,
      "width": 3,
      "height": 2,
      "title": "A",
      "imageUrl": "/assets/a.png"
    },
    {
      "id": "b",
      "parentId": "a",
      "order": 0,
      "mode": "relative",
      "dx": 0,
      "dy": 4,
      "fixed": false,
      "width": 3,
      "height": 2,
      "title": "B",
      "imageUrl": "/assets/b.png"
    },
    {
      "id": "c",
      "parentId": "a",
      "order": 1,
      "mode": "auto",
      "fixed": false,
      "width": 3,
      "height": 2,
      "title": "C",
      "imageUrl": "/assets/c.png"
    }
  ],
  "edges": [
    {
      "id": "a->b",
      "source": "a",
      "target": "b",
      "kind": "tree"
    },
    {
      "id": "a->c",
      "source": "a",
      "target": "c",
      "kind": "tree"
    }
  ],
  "viewport": {
    "x": 0,
    "y": 0,
    "zoom": 1
  }
}
```

Bad persisted state:

```json
{
  "reactFlowNodes": [
    {
      "id": "a",
      "position": { "x": 320, "y": 160 }
    }
  ]
}
```

The bad format loses the semantic distinction between absolute, relative, and auto positioning.

---

## 14. Validation rules

Validate before saving and after import.

Required validation:

- Node IDs are unique.
- Edge IDs are unique.
- All tree edges point to existing nodes.
- `parentId` points to existing node or is null.
- No cycles in parent/child tree.
- Each non-root node has exactly one parent.
- `order` is unique among siblings or normalizable.
- Absolute nodes have integer `x/y`.
- Relative nodes have integer `dx/dy`.
- Auto nodes should not persist stale `x/y` unless used as last layout hint.
- Width and height are positive.
- Grid size is positive.
- All final resolved positions are integers.
- If backend returns resolved positions, all returned IDs must exist in the canonical document.

Recommended normalization:

```ts
function normalizeDiagram(doc: DiagramDocument): DiagramDocument {
  return {
    ...doc,
    nodes: doc.nodes.map(node => ({
      ...node,
      x: node.x == null ? undefined : Math.round(node.x),
      y: node.y == null ? undefined : Math.round(node.y),
      dx: node.dx == null ? undefined : Math.round(node.dx),
      dy: node.dy == null ? undefined : Math.round(node.dy),
      width: Math.max(1, Math.round(node.width)),
      height: Math.max(1, Math.round(node.height)),
    })),
  };
}
```

---

## 15. Undo/redo strategy

Use command-level undo/redo, not raw React Flow state snapshots.

Recommended:

```ts
interface DiagramHistoryEntry {
  command: DiagramCommand;
  before: DiagramDocument;
  after: DiagramDocument;
  timestamp: string;
}
```

For large documents, replace full snapshots with patches after the behavior stabilizes. During initial development, full snapshots are easier and safer.

---

## 16. Performance notes

For small and medium trees, fully recomputing layout on command commit is acceptable.

For larger diagrams:

- Keep layout functions pure and deterministic.
- Index nodes by ID.
- Index children by parent ID.
- Re-layout only affected subtree when possible.
- Memoize subtree bounds.
- Use React Flow’s visible-element rendering optimization if needed.
- Avoid calling Python during mousemove.
- Avoid re-creating `nodeTypes`, callbacks, and large arrays unnecessarily.
- Use `useMemo` and `useCallback` around projections and handlers.
- Debounce backend layout commits.
- Consider virtualization only after measuring.

---

## 17. Implementation phases

### Phase 1: Local React Flow prototype

Deliver:

- React Flow canvas.
- Grid background.
- Snap-to-grid.
- Minimap.
- Image node.
- Node click opens popup.
- Drag node commits to absolute mode.
- Save/load canonical JSON.

Acceptance criteria:

- A small tree can be displayed.
- Nodes can be dragged and saved.
- Reload restores positions exactly.
- Coordinates are persisted in grid units, not pixels.

### Phase 2: Canonical layout engine

Deliver:

- `DiagramDocument` model.
- `resolveWorldPositions`.
- Absolute mode.
- Relative mode.
- Basic auto mode.
- Subtree bounds.
- Sibling ordering.
- Validation.
- Unit tests.

Acceptance criteria:

- Absolute nodes remain fixed.
- Relative nodes follow parent.
- Auto nodes are deterministic.
- Re-running layout does not cause drift.
- Unit tests cover insert/delete/move/pin/unpin.

### Phase 3: Subtree policies

Deliver:

- `move_subtree`.
- `keep_descendants`.
- `reauto_descendants`.
- Pin/unpin node.
- Pin/unpin subtree.
- Pin all.
- Unpin all.
- Auto-layout subtree.
- Auto-layout all.

Acceptance criteria:

- Drag behavior is predictable.
- Descendant behavior matches selected policy.
- Fixed nodes are respected.
- Auto-layout does not unexpectedly destroy manual edits.

### Phase 4: Python layout service

Deliver:

- FastAPI endpoint.
- Shared JSON schema or generated types.
- Backend validation.
- Backend layout response.
- Frontend layout client.
- Debounced commit integration.

Acceptance criteria:

- Frontend can call backend on layout commit.
- Backend can return resolved positions.
- Frontend reconciles returned positions into canonical model.
- Backend failure falls back to local layout or shows a recoverable error.

### Phase 5: Industrial polish

Deliver:

- Undo/redo.
- Keyboard shortcuts.
- Context menu.
- Lasso/multi-select if needed.
- Copy/paste if needed.
- Better edge styling.
- Better node badges.
- Node search.
- Export/import UI.
- Layout diagnostics overlay.

Acceptance criteria:

- Engineers and users can understand why a node is where it is.
- Large diagrams remain responsive enough.
- The canonical JSON is stable enough for long-term storage.

---

## 18. Main engineering risks

### Risk 1: Letting React Flow become the data model

This is the largest architectural risk.

Mitigation:

- Persist only `DiagramDocument`.
- Treat React Flow nodes as derived projection.
- Convert drag results back into canonical commands.

### Risk 2: Auto-layout fighting manual edits

Mitigation:

- Make pin/fixed status explicit.
- Preserve absolute nodes.
- Expose destructive layout commands clearly.
- Make auto-layout deterministic.
- Keep layout preview and diff visible where possible.

### Risk 3: Backend layout latency hurting UX

Mitigation:

- Never call Python during mousemove.
- Use local optimistic layout.
- Call backend only on commit.
- Debounce expensive operations.
- Show recoverable layout warnings.

### Risk 4: Position drift from pixel/grid conversion

Mitigation:

- Store grid units only.
- Snap on every command commit.
- Use a single conversion function.
- Avoid storing derived React Flow `position`.

### Risk 5: Layout behavior becoming untestable

Mitigation:

- Keep layout engine framework-free.
- Unit-test layout functions in TypeScript.
- Unit-test Python layout separately.
- Use golden JSON fixtures.

---

## 19. Recommended repository structure

```text
src/
  diagram/
    model/
      DiagramDocument.ts
      DiagramCommand.ts
      validation.ts

    layout/
      LayoutEngine.ts
      TreeLayoutPolicy.ts
      subtreeBounds.ts
      movePolicies.ts
      __tests__/
        absolute.test.ts
        relative.test.ts
        auto.test.ts
        movePolicies.test.ts

    react-flow/
      DiagramEditor.tsx
      ImageNode.tsx
      edges.tsx
      projection.ts
      useDiagramCommands.ts

    backend/
      BackendLayoutClient.ts

backend/
  diagram_layout/
    main.py
    models.py
    layout_engine.py
    validation.py
    tests/
      test_absolute.py
      test_relative.py
      test_auto.py
```

---

## 20. Final decision

Use:

```text
React Flow / @xyflow/react
  for canvas rendering, interaction, pan/zoom, minimap, grid, custom React nodes.

Custom TypeScript layout engine
  for canonical layout semantics, coordinate modes, subtree policies, validation, and persistence.

Optional Python FastAPI service
  for authoritative layout, domain constraints, batch operations, and server-side validation.
```

Do not look for a single diagram library that already implements absolute/relative/auto node semantics. That behavior is application-specific and should be implemented as our own canonical layout layer.

React Flow is the most suitable default because it gives us a mature React TypeScript editor substrate while staying flexible enough for custom layout logic. AntV X6 is the main alternative if we later decide we want a more generic diagramming engine instead of a React-native component architecture.

---

## 21. Reference links

- React Flow API Reference: https://reactflow.dev/api-reference
- React Flow `<ReactFlow />`: https://reactflow.dev/api-reference/react-flow
- React Flow `<Background />`: https://reactflow.dev/api-reference/components/background
- React Flow `<MiniMap />`: https://reactflow.dev/api-reference/components/minimap
- React Flow Layouting Overview: https://reactflow.dev/learn/layouting/layouting
- React Flow Examples: https://reactflow.dev/examples
- xyflow GitHub: https://github.com/xyflow/xyflow
- AntV X6 GitHub: https://github.com/antvis/X6
- AntV X6 Docs: https://x6.antv.antgroup.com/
- ELK.js GitHub: https://github.com/kieler/elkjs
