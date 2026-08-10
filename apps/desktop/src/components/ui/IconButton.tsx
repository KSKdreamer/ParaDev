import type { ButtonHTMLAttributes, ReactNode } from "react";

type IconButtonProps = Omit<ButtonHTMLAttributes<HTMLButtonElement>, "aria-label"> & {
  label: string;
  selected?: boolean;
  children: ReactNode;
};

export function IconButton({ children, className = "", label, selected = false, title, ...props }: IconButtonProps) {
  const classes = ["icon-button", selected ? "selected" : "", className].filter(Boolean).join(" ");

  return (
    <button aria-label={label} className={classes} title={title ?? label} type="button" {...props}>
      {children}
    </button>
  );
}
