import { Activity, Circle } from "lucide-react";
import type { Translator } from "../i18n";
import type { SurfaceRow } from "../types";

type StatusBarProps = {
  surfaceRows: SurfaceRow[];
  t: Translator;
};

export function StatusBar({ surfaceRows, t }: StatusBarProps) {
  const ready = surfaceRows.filter((surface) => surface.status === "ready").length;
  const scaffold = surfaceRows.filter((surface) => surface.status === "scaffold").length;

  return (
    <footer className="statusbar">
      <span>
        <Activity aria-hidden="true" size={14} />
        {t("statusbar.sdkReady", { count: ready })}
      </span>
      <span>
        <Circle aria-hidden="true" size={8} />
        {t("statusbar.scaffoldedSurfaces", { count: scaffold })}
      </span>
      <span>{t("statusbar.restOffline")}</span>
      <span>{t("statusbar.mcpPlanned")}</span>
      <span>{t("statusbar.macosPriority")}</span>
    </footer>
  );
}
