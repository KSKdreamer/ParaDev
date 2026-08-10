import { ChevronDown } from "lucide-react";
import type { ReactNode, SelectHTMLAttributes } from "react";

type SelectOption = {
  label: string;
  value: string;
};

type SelectFieldProps = Omit<SelectHTMLAttributes<HTMLSelectElement>, "children" | "prefix"> & {
  controlTitle?: string;
  label: string;
  options: SelectOption[];
  prefix?: ReactNode;
  variant?: "default" | "compact";
};

export function SelectField({ className = "", controlTitle, label, options, prefix, variant = "default", ...props }: SelectFieldProps) {
  const classes = ["select-field", variant === "compact" ? "compact" : "", className].filter(Boolean).join(" ");

  return (
    <label className={classes} title={controlTitle ?? label}>
      {prefix ? <span className="select-prefix">{prefix}</span> : null}
      <select aria-label={label} {...props}>
        {options.map((option) => (
          <option key={option.value} value={option.value}>
            {option.label}
          </option>
        ))}
      </select>
      <ChevronDown aria-hidden="true" className="select-chevron" size={14} />
    </label>
  );
}
