export type AuthoringCloseState = Readonly<{
  busy: boolean;
  dirty: boolean;
}>;

type BeforeUnloadTarget = {
  addEventListener: (
    type: "beforeunload",
    listener: (event: BeforeUnloadEvent) => void
  ) => void;
  removeEventListener: (
    type: "beforeunload",
    listener: (event: BeforeUnloadEvent) => void
  ) => void;
};

type AuthoringCloseGuardOptions = {
  browserTarget: BeforeUnloadTarget;
  getState: () => AuthoringCloseState;
};

/** Protects dirty or busy authoring sessions in browsers and system WebViews. */
export function installAuthoringCloseGuards({
  browserTarget,
  getState
}: AuthoringCloseGuardOptions): () => void {
  const handleBeforeUnload = (event: BeforeUnloadEvent) => {
    const state = getState();
    if (!state.dirty && !state.busy) {
      return;
    }
    event.preventDefault();
    event.returnValue = "";
  };

  browserTarget.addEventListener("beforeunload", handleBeforeUnload);
  return () => {
    browserTarget.removeEventListener("beforeunload", handleBeforeUnload);
  };
}
