import { FolderOpen, PackagePlus } from "lucide-react";
import type { Translator } from "../i18n";

type ProjectOnboardingProps = {
  checking?: boolean;
  error: string;
  importing: boolean;
  onImportProject: () => void;
  onOpenProject: () => void;
  opening: boolean;
  t: Translator;
};

export function ProjectOnboarding({
  checking = false,
  error,
  importing,
  onImportProject,
  onOpenProject,
  opening,
  t
}: ProjectOnboardingProps) {
  const busy = checking || importing || opening;

  return (
    <main className="project-onboarding">
      <section
        aria-busy={busy}
        aria-labelledby="project-onboarding-title"
        className="project-onboarding-card"
      >
        <div aria-hidden="true" className="project-onboarding-mark">
          <FolderOpen size={32} strokeWidth={1.7} />
        </div>
        <p className="project-onboarding-eyebrow">
          {t("project.onboarding.eyebrow")}
        </p>
        <h1 id="project-onboarding-title">
          {t(
            checking
              ? "project.onboarding.checking.title"
              : "project.onboarding.title"
          )}
        </h1>
        <p className="project-onboarding-detail">
          {t(
            checking
              ? "project.onboarding.checking.detail"
              : "project.onboarding.detail"
          )}
        </p>
        {checking ? null : (
          <>
            <div className="project-onboarding-actions">
              <button
                className="toolbar-button primary project-onboarding-action"
                disabled={busy}
                onClick={onImportProject}
                type="button"
              >
                <PackagePlus aria-hidden="true" size={17} />
                {t(
                  importing
                    ? "project.onboarding.installing"
                    : "project.onboarding.installAction"
                )}
              </button>
              <button
                className="toolbar-button project-onboarding-action"
                disabled={busy}
                onClick={onOpenProject}
                type="button"
              >
                <FolderOpen aria-hidden="true" size={17} />
                {t(
                  opening
                    ? "project.onboarding.opening"
                    : "project.onboarding.action"
                )}
              </button>
            </div>
            <small className="project-onboarding-hint">
              {t("project.onboarding.hint")}
            </small>
          </>
        )}
        {error ? (
          <p className="project-onboarding-error" role="alert">
            {error}
          </p>
        ) : null}
      </section>
    </main>
  );
}
