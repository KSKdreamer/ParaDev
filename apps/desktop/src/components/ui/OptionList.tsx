import { ChevronDown } from "lucide-react";
import { useEffect, useId, useRef, useState, type CSSProperties } from "react";
import type { TranslationKey, Translator } from "../../i18n";
import { moduleAccentIndex } from "../../projectModules";
import type { PanelOption } from "../../types";

type OptionListProps = {
  activeId: string;
  defaultCollapsedGroupKeys?: readonly TranslationKey[];
  grouped?: boolean;
  items: PanelOption[];
  onDoubleSelect?: (id: string) => void;
  onSelect: (id: string) => void;
  onReorder?: (fromId: string, toId: string) => void;
  reorderable?: boolean;
  t: Translator;
};

type OptionAccentStyle = CSSProperties & {
  "--option-accent": string;
};

export function OptionList({
  activeId,
  defaultCollapsedGroupKeys = [],
  grouped = false,
  items,
  onDoubleSelect,
  onSelect,
  onReorder,
  reorderable = false,
  t
}: OptionListProps) {
  const reorderEnabled = reorderable && !grouped;
  const listId = useId().replaceAll(":", "");
  const activeGroupKey = items.find((item) => item.id === activeId)?.groupKey;
  const [collapsedGroupKeys, setCollapsedGroupKeys] = useState<Set<TranslationKey>>(
    () =>
      new Set(
        defaultCollapsedGroupKeys.filter(
          (groupKey) =>
            !items.some(
              (item) => item.id === activeId && item.groupKey === groupKey
            )
        )
      )
  );
  const automaticallyExpandedGroupKey = useRef(activeGroupKey);
  const manuallyExpandedGroupKeys = useRef(new Set<TranslationKey>());
  const [draggingId, setDraggingId] = useState("");
  const [dropTargetId, setDropTargetId] = useState("");
  const pointerDrag = useRef<{ active: boolean; id: string; x: number; y: number } | null>(null);
  const dropTarget = useRef("");
  const suppressClick = useRef(false);
  const clearDragState = () => {
    setDraggingId("");
    setDropTargetId("");
    dropTarget.current = "";
  };
  const completeReorder = (fromId: string, toId: string) => {
    if (fromId && toId && fromId !== toId) {
      onReorder?.(fromId, toId);
    }
  };
  const setDropTarget = (id: string) => {
    dropTarget.current = id;
    setDropTargetId(id);
  };

  const renderedItems: Array<{ groupKey: TranslationKey | ""; items: PanelOption[] }> = [];
  if (grouped) {
    for (const item of items) {
      const groupKey = item.groupKey ?? "";
      const group = renderedItems.find((entry) => entry.groupKey === groupKey);
      if (group) {
        group.items.push(item);
      } else {
        renderedItems.push({ groupKey, items: [item] });
      }
    }
  } else {
    renderedItems.push({ groupKey: "", items });
  }

  useEffect(() => {
    if (!activeGroupKey) {
      return;
    }
    setCollapsedGroupKeys((current) => {
      const next = new Set(current);
      const previousAutomaticallyExpandedGroupKey = automaticallyExpandedGroupKey.current;
      if (
        previousAutomaticallyExpandedGroupKey &&
        previousAutomaticallyExpandedGroupKey !== activeGroupKey &&
        !manuallyExpandedGroupKeys.current.has(previousAutomaticallyExpandedGroupKey)
      ) {
        next.add(previousAutomaticallyExpandedGroupKey);
      }
      next.delete(activeGroupKey);
      if (
        next.size === current.size &&
        [...next].every((groupKey) => current.has(groupKey))
      ) {
        return current;
      }
      return next;
    });
    automaticallyExpandedGroupKey.current = activeGroupKey;
  }, [activeGroupKey, activeId]);

  return (
    <div className={grouped ? "option-list grouped" : "option-list"}>
      {renderedItems.map((group) => {
        const groupKey = group.groupKey || null;
        const collapsible = grouped && groupKey !== null;
        const collapsed = Boolean(
          groupKey && collapsedGroupKeys.has(groupKey)
        );
        const groupId = `${listId}-group-${groupKey?.replaceAll(".", "-") ?? "default"}`;
        return (
          <div className={collapsed ? "option-group collapsed" : "option-group"} key={groupKey ?? "default"}>
            {collapsible && groupKey ? (
              <button
                aria-controls={groupId}
                aria-expanded={!collapsed}
                className="option-group-title"
                onClick={() => {
                  setCollapsedGroupKeys((current) => {
                    const next = new Set(current);
                    if (next.has(groupKey)) {
                      next.delete(groupKey);
                      manuallyExpandedGroupKeys.current.add(groupKey);
                    } else {
                      next.add(groupKey);
                      manuallyExpandedGroupKeys.current.delete(groupKey);
                    }
                    return next;
                  });
                }}
                type="button"
              >
                <span>{t(groupKey)}</span>
                <small>{group.items.length}</small>
                <ChevronDown aria-hidden="true" size={14} />
              </button>
            ) : null}
            <div className="option-group-items" hidden={collapsed} id={groupId}>
              {group.items.map((item) => {
                const title = item.titleKey
                  ? t(item.titleKey)
                  : item.label ?? item.id;
                const classes = [
                  "option-row",
                  reorderEnabled ? "reorderable" : "",
                  item.id === activeId ? "selected" : "",
                  draggingId === item.id ? "dragging" : "",
                  dropTargetId === item.id ? "drop-target" : ""
                ]
                  .filter(Boolean)
                  .join(" ");
                const style = {
                  "--option-accent": `var(--option-accent-${moduleAccentIndex(item.id)})`
                } as OptionAccentStyle;
                return (
                  <button
                    aria-label={title}
                    className={classes}
                    draggable={false}
                    key={item.id}
                    onClick={() => {
                      if (suppressClick.current) {
                        suppressClick.current = false;
                        return;
                      }
                      onSelect(item.id);
                    }}
                    onDoubleClick={() => onDoubleSelect?.(item.id)}
                    onDragEnd={() => {
                      completeReorder(draggingId, dropTarget.current);
                      clearDragState();
                    }}
                    onDragEnter={() => {
                      if (
                        reorderEnabled &&
                        draggingId &&
                        draggingId !== item.id
                      ) {
                        setDropTarget(item.id);
                      }
                    }}
                    onDragOver={(event) => {
                      if (
                        !reorderEnabled ||
                        !draggingId ||
                        draggingId === item.id
                      ) {
                        return;
                      }
                      event.preventDefault();
                      event.dataTransfer.dropEffect = "move";
                      setDropTarget(item.id);
                    }}
                    onDragStart={(event) => {
                      if (!reorderEnabled) {
                        return;
                      }
                      event.dataTransfer.effectAllowed = "move";
                      event.dataTransfer.setData("text/plain", item.id);
                      setDraggingId(item.id);
                    }}
                    onDrop={(event) => {
                      if (!reorderEnabled) {
                        return;
                      }
                      event.preventDefault();
                      const fromId =
                        event.dataTransfer.getData("text/plain") || draggingId;
                      completeReorder(fromId, item.id);
                      clearDragState();
                    }}
                    onPointerCancel={() => {
                      pointerDrag.current = null;
                      clearDragState();
                    }}
                    onPointerDown={(event) => {
                      if (!reorderEnabled || event.button !== 0) {
                        return;
                      }
                      pointerDrag.current = {
                        active: false,
                        id: item.id,
                        x: event.clientX,
                        y: event.clientY
                      };
                      suppressClick.current = false;
                    }}
                    onPointerMove={(event) => {
                      if (!reorderEnabled || !pointerDrag.current) {
                        return;
                      }
                      const distance =
                        Math.abs(event.clientX - pointerDrag.current.x) +
                        Math.abs(event.clientY - pointerDrag.current.y);
                      if (!pointerDrag.current.active && distance > 6) {
                        pointerDrag.current.active = true;
                        suppressClick.current = true;
                        setDraggingId(pointerDrag.current.id);
                      }
                      if (
                        pointerDrag.current.active &&
                        pointerDrag.current.id !== item.id
                      ) {
                        setDropTarget(item.id);
                      }
                    }}
                    onPointerUp={() => {
                      if (!pointerDrag.current) {
                        return;
                      }
                      const pointerTarget =
                        pointerDrag.current.active &&
                        pointerDrag.current.id !== item.id
                          ? item.id
                          : "";
                      const targetId = dropTarget.current || pointerTarget;
                      if (pointerDrag.current.active) {
                        completeReorder(pointerDrag.current.id, targetId);
                      }
                      pointerDrag.current = null;
                      clearDragState();
                    }}
                    style={style}
                    title={title}
                    type="button"
                  >
                    <span className="option-accent" />
                    <span className="option-copy">
                      <strong>{title}</strong>
                      {typeof item.count === "number" ? (
                        <small>{item.count}</small>
                      ) : null}
                    </span>
                  </button>
                );
              })}
            </div>
          </div>
        );
      })}
    </div>
  );
}
