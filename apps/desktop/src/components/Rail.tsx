import { Settings } from "lucide-react";
import type { Translator } from "../i18n";
import type { RailItem, ThemeName } from "../types";
import anthroLogo from "../assets/paradev-logo/paradev-logo-anthro.png";
import githubLogo from "../assets/paradev-logo/paradev-logo-github.png";
import ollamaLogo from "../assets/paradev-logo/paradev-logo-ollama.png";

type RailProps = {
  activeRail: string;
  blocked?: boolean;
  items: RailItem[];
  onSelect: (id: string) => void;
  onSettingsSelect: () => void;
  t: Translator;
  theme: ThemeName;
};

const brandLogoByTheme: Record<ThemeName, string> = {
  light: ollamaLogo,
  dark: githubLogo,
  anthropic: anthroLogo
};

export function Rail({ activeRail, blocked = false, items, onSelect, onSettingsSelect, t, theme }: RailProps) {
  return (
    <aside aria-hidden={blocked ? true : undefined} className="rail" inert={blocked ? true : undefined} aria-label={t("rail.aria")}>
      <div className="brand-mark" aria-label="ParaDev">
        <img alt="ParaDev" className="brand-mark-image" draggable="false" src={brandLogoByTheme[theme]} />
      </div>
      <nav className="rail-nav">
        {items.map((item) => {
          const label = t(item.labelKey);
          const Icon = item.icon;
          return (
            <button
              aria-label={label}
              className={item.id === activeRail ? "rail-button selected" : "rail-button"}
              key={item.id}
              onClick={() => onSelect(item.id)}
              title={label}
              type="button"
            >
              <Icon aria-hidden="true" size={19} strokeWidth={1.8} />
            </button>
          );
        })}
      </nav>
      <button aria-label={t("rail.config")} className={activeRail === "settings" ? "rail-button selected" : "rail-button"} onClick={onSettingsSelect} title={t("rail.config")} type="button">
        <Settings aria-hidden="true" size={19} strokeWidth={1.8} />
      </button>
    </aside>
  );
}
