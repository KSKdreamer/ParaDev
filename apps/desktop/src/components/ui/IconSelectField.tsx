import { Check, ChevronDown } from "lucide-react";
import { type CSSProperties, useEffect, useRef, useState } from "react";
import type { OpenPathTargetIconKind } from "../../openPathTargets";

export type IconSelectOption = {
  iconKind: OpenPathTargetIconKind;
  iconSrc: string;
  label: string;
  value: string;
};

type IconSelectFieldProps = {
  className?: string;
  label: string;
  onChange: (value: string) => void;
  options: IconSelectOption[];
  value: string;
  variant?: "default" | "compact";
};

export function IconSelectField({ className = "", label, onChange, options, value, variant = "default" }: IconSelectFieldProps) {
  const [open, setOpen] = useState(false);
  const rootRef = useRef<HTMLDivElement | null>(null);
  const selectedOption = options.find((option) => option.value === value) ?? options[0];
  const classes = ["icon-select-field", variant === "compact" ? "compact" : "", className].filter(Boolean).join(" ");
  const title = selectedOption ? `${label}: ${selectedOption.label}` : label;

  useEffect(() => {
    if (!open) {
      return;
    }
    const handlePointerDown = (event: PointerEvent) => {
      if (!rootRef.current?.contains(event.target as Node)) {
        setOpen(false);
      }
    };
    document.addEventListener("pointerdown", handlePointerDown);
    return () => document.removeEventListener("pointerdown", handlePointerDown);
  }, [open]);

  const handleSelect = (nextValue: string) => {
    onChange(nextValue);
    setOpen(false);
  };

  return (
    <div className={classes} onKeyDown={(event) => event.key === "Escape" && setOpen(false)} ref={rootRef}>
      <button
        aria-expanded={open}
        aria-haspopup="listbox"
        aria-label={title}
        className="icon-select-trigger"
        disabled={options.length === 0}
        onClick={() => setOpen((current) => !current)}
        title={title}
        type="button"
      >
        {selectedOption ? <IconSelectIcon kind={selectedOption.iconKind} src={selectedOption.iconSrc} /> : null}
        <ChevronDown aria-hidden="true" className="select-chevron" size={13} />
      </button>
      {open ? (
        <div aria-label={label} className="icon-select-menu" role="listbox">
          {options.map((option) => (
            <button
              aria-selected={option.value === value}
              className="icon-select-option"
              key={option.value}
              onClick={() => handleSelect(option.value)}
              role="option"
              title={option.label}
              type="button"
            >
              <IconSelectIcon kind={option.iconKind} src={option.iconSrc} />
              <span>{option.label}</span>
              {option.value === value ? <Check aria-hidden="true" className="icon-select-check" size={14} /> : null}
            </button>
          ))}
        </div>
      ) : null}
    </div>
  );
}

function IconSelectIcon({ kind, src }: { kind: OpenPathTargetIconKind; src: string }) {
  if (kind === "mask") {
    return <span aria-hidden="true" className="icon-select-icon mask" style={{ "--icon-select-url": `url(${src})` } as CSSProperties} />;
  }
  return <img alt="" aria-hidden="true" className="icon-select-icon image" draggable={false} src={src} />;
}
