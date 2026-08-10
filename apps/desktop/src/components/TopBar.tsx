import { Languages, Moon, PanelLeftClose, PanelLeftOpen, PanelRightClose, PanelRightOpen, Search, Sun, SwatchBook } from "lucide-react";
import type { Locale, Translator } from "../i18n";
import { availableOpenPathTargets } from "../openPathTargets";
import type { OpenPathTarget } from "../services/paradev";
import type { ThemeName } from "../types";
import { IconSelectField } from "./ui/IconSelectField";
import { IconButton } from "./ui/IconButton";
import { SelectField } from "./ui/SelectField";

type TopBarProps = {
  inspectorOpen: boolean;
  locale: Locale;
  openTarget: OpenPathTarget;
  onInspectorToggle: () => void;
  onLocaleChange: (locale: Locale) => void;
  onOpenTargetChange: (target: OpenPathTarget) => void;
  onProjectPanelToggle: () => void;
  onSearchQueryChange: (query: string) => void;
  onThemeChange: (theme: ThemeName) => void;
  projectPanelAvailable?: boolean;
  projectPanelOpen: boolean;
  searchQuery: string;
  t: Translator;
  theme: ThemeName;
};

export function TopBar({
  inspectorOpen,
  locale,
  openTarget,
  onInspectorToggle,
  onLocaleChange,
  onOpenTargetChange,
  onProjectPanelToggle,
  onSearchQueryChange,
  onThemeChange,
  projectPanelAvailable = true,
  projectPanelOpen,
  searchQuery,
  t,
  theme
}: TopBarProps) {
  const openTargetOptions = availableOpenPathTargets().map((target) => ({
    value: target.id,
    label: t(target.labelKey),
    iconSrc: target.iconSrc,
    iconKind: target.iconKind
  }));

  return (
    <header className="topbar">
      <label className="command-field">
        <Search aria-hidden="true" size={15} />
        <input aria-label={t("app.search.aria")} onChange={(event) => onSearchQueryChange(event.target.value)} placeholder={t("app.search.placeholder")} value={searchQuery} />
      </label>
      <div className="toolbar-actions">
        {projectPanelAvailable ? (
          <IconButton
            aria-expanded={projectPanelOpen}
            className="toolbar-button icon-only"
            label={projectPanelOpen ? t("panel.project.hide") : t("panel.project.show")}
            onClick={onProjectPanelToggle}
          >
            {projectPanelOpen ? <PanelLeftClose aria-hidden="true" size={16} /> : <PanelLeftOpen aria-hidden="true" size={16} />}
          </IconButton>
        ) : null}
        <IconSelectField
          className="open-target-select"
          label={t("openTarget.aria")}
          onChange={(value) => onOpenTargetChange(value as OpenPathTarget)}
          options={openTargetOptions}
          value={openTarget}
          variant="compact"
        />
        <div className="segmented" aria-label={t("theme.aria")}>
          <button className={theme === "light" ? "selected" : ""} onClick={() => onThemeChange("light")} title={t("theme.light")} type="button">
            <Sun aria-hidden="true" size={15} />
          </button>
          <button className={theme === "dark" ? "selected" : ""} onClick={() => onThemeChange("dark")} title={t("theme.dark")} type="button">
            <Moon aria-hidden="true" size={15} />
          </button>
          <button className={theme === "anthropic" ? "selected" : ""} onClick={() => onThemeChange("anthropic")} title={t("theme.anthropic")} type="button">
            <SwatchBook aria-hidden="true" size={15} />
          </button>
        </div>
        <SelectField
          className="locale-select"
          label={t("locale.aria")}
          onChange={(event) => onLocaleChange(event.target.value as Locale)}
          options={[
            { label: t("locale.en"), value: "en" },
            { label: t("locale.zh"), value: "zh" }
          ]}
          prefix={<Languages aria-hidden="true" size={15} />}
          value={locale}
          variant="compact"
        />
        <IconButton aria-expanded={inspectorOpen} className="toolbar-button icon-only" label={inspectorOpen ? t("panel.inspector.hide") : t("panel.inspector.show")} onClick={onInspectorToggle}>
          {inspectorOpen ? <PanelRightClose aria-hidden="true" size={16} /> : <PanelRightOpen aria-hidden="true" size={16} />}
        </IconButton>
      </div>
    </header>
  );
}
