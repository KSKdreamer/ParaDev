import {
  useEffect,
  useId,
  useMemo,
  useRef,
  useState,
  type ChangeEvent,
  type FormEvent,
  type KeyboardEvent
} from "react";
import type { Locale, TranslationKey, Translator } from "../i18n";
import type {
  SourceFormChoice,
  SourceFormControl,
  SourceFormPatch,
  SourceFormPayload,
  SourceFormScalar,
  SourceFormSection
} from "../types";
import {
  JsonScalarPatchError,
  parseFiniteJsonNumberToken,
  parseJsonScalarDocument,
  type JsonScalarKind,
  type JsonScalarPatchErrorCode,
  type JsonScalarReplacement,
  type JsonScalarToken
} from "./jsonScalarPatch";
import {
  parseFinitePdxNumberToken,
  PdxScalarPatchError,
  readPdxBlockBodyAtPatch,
  readPdxIntegerListAtPatch,
  readPdxScalarAtPatch,
  replacePdxBlockBodyAtPatch,
  replacePdxIntegerListAtPatch,
  replacePdxScalarAtPatch,
  type PdxScalarPatchErrorCode
} from "./pdxSourcePatch";
import {
  LocTextPatchError,
  readLocTextAtPatch,
  replaceLocTextAtPatch,
  type LocTextPatchErrorCode
} from "./locTextPatch";
import { localizedSourceFormText } from "./sourceFormText";

export { localizedSourceFormText } from "./sourceFormText";

export type GuidedSourceFormChange = {
  /** Text used to prepare the currently rendered Registry form. */
  baseText: string;
  controlId: string;
  /** Immediate local preview; the SDK planner remains write-authoritative. */
  text: string;
  value: SourceFormScalar;
};

type GuidedSourceFormProps = {
  disabled?: boolean;
  form: SourceFormPayload;
  locale: Locale;
  onChange: (change: GuidedSourceFormChange) => void;
  onSearch?: (query: string) => void;
  text: string;
  t: Translator;
};

type GuidedScalarDocument = {
  read: (patch: SourceFormPatch) => JsonScalarToken;
  replace: (patch: SourceFormPatch, replacement: JsonScalarReplacement) => string;
  text: string;
};

type ParsedDocument =
  | { document: GuidedScalarDocument; error: "" }
  | { document: null; error: string };

export function GuidedSourceForm({ disabled = false, form, locale, onChange, onSearch, text, t }: GuidedSourceFormProps) {
  const searchId = useId();
  const [searchText, setSearchText] = useState(form.query ?? "");
  useEffect(() => {
    setSearchText(form.query ?? "");
  }, [form.query]);
  const parsed = useMemo<ParsedDocument>(() => {
    try {
      return { document: parseGuidedScalarDocument(form, text), error: "" };
    } catch (error) {
      return { document: null, error: sourceFormErrorMessage(error, t) };
    }
  }, [form, t, text]);
  const label = form.label ? localizedSourceFormText(form.label, locale) : form.module_id;
  const description = form.description ? localizedSourceFormText(form.description, locale) : "";
  const searchable = Boolean(
    onSearch
      && form.source_format !== "json"
      && (form.coverage?.truncated || form.query !== undefined)
  );
  const submitSearch = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    onSearch?.(searchText.trim());
  };

  if (!parsed.document) {
    return (
      <div
        className="guided-source-form guided-source-form-invalid"
        data-source-form-contract={form.contract}
        data-source-form-error={`invalid-${form.source_format}`}
        role="alert"
      >
        {parsed.error}
      </div>
    );
  }

  return (
    <div
      aria-label={label}
      aria-busy={disabled || undefined}
      className="guided-source-form"
      data-source-form-contract={form.contract}
      data-source-form-schema={form.schema}
    >
      {form.label || description ? (
        <header className="guided-source-form-heading">
          {form.label ? <strong>{label}</strong> : null}
          {description ? <small>{description}</small> : null}
        </header>
      ) : null}
      {searchable ? (
        <form className="guided-source-form-search" onSubmit={submitSearch} role="search">
          <label htmlFor={searchId}>
            {t("workspace.module.editor.guidedFormSearchLabel")}
          </label>
          <div>
            <input
              disabled={disabled}
              id={searchId}
              maxLength={200}
              onChange={(event) => setSearchText(event.target.value)}
              placeholder={t("workspace.module.editor.guidedFormSearchPlaceholder")}
              type="search"
              value={searchText}
            />
            <button disabled={disabled} type="submit">
              {t("workspace.module.editor.guidedFormSearchAction")}
            </button>
            {form.query !== undefined ? (
              <button
                disabled={disabled}
                onClick={() => {
                  setSearchText("");
                  onSearch?.("");
                }}
                type="button"
              >
                {t("workspace.module.editor.guidedFormSearchClear")}
              </button>
            ) : null}
          </div>
        </form>
      ) : null}
      {form.coverage?.truncated ? (
        <div className="guided-source-form-coverage" role="note">
          {t(form.query === undefined
            ? "workspace.module.editor.guidedFormPartialCoverage"
            : "workspace.module.editor.guidedFormSearchPartialCoverage", {
            shown: form.coverage.shown_controls,
            total: form.coverage.total_controls
          })}
        </div>
      ) : null}
      {form.sections.length === 0 ? (
        <div className="guided-source-form-empty" role="status">
          {t("workspace.module.editor.guidedFormSearchNoResults")}
        </div>
      ) : (
        <div className="guided-source-form-sections">
          {form.sections.map((section) => (
            <GuidedSourceFormSection
              document={parsed.document}
              disabled={disabled}
              key={section.id}
              locale={locale}
              onChange={onChange}
              section={section}
              t={t}
            />
          ))}
        </div>
      )}
    </div>
  );
}

function parseGuidedScalarDocument(form: SourceFormPayload, text: string): GuidedScalarDocument {
  if (form.source_format === "json") {
    const document = parseJsonScalarDocument(text);
    return {
      read(patch) {
        if (patch.op !== "replace-json-scalar") {
          throw new Error("A JSON source form contains a non-JSON scalar patch.");
        }
        return document.read(patch.path);
      },
      replace(patch, replacement) {
        if (patch.op !== "replace-json-scalar") {
          throw new Error("A JSON source form contains a non-JSON scalar patch.");
        }
        return document.replace(patch.path, replacement);
      },
      text
    };
  }

  if (form.source_format === "loc") {
    const patches = sourceFormPatches(form.sections);
    if (patches.some((patch) => patch.op !== "replace-loc-text")) {
      throw new LocTextPatchError(
        "invalid-span",
        "A localization source form contains a non-localization patch."
      );
    }
    const locPatches = patches.filter((patch) => patch.op === "replace-loc-text");
    const spans = locPatches
      .map((patch) => patch.span)
      .sort((left, right) => left.start - right.start || left.end - right.end);
    for (let index = 1; index < spans.length; index += 1) {
      const previous = spans[index - 1];
      const current = spans[index];
      if (previous && current && current.start < previous.end) {
        throw new LocTextPatchError(
          "invalid-span",
          "Localization guided controls contain overlapping source spans."
        );
      }
    }
    for (const patch of locPatches) {
      readLocTextAtPatch(text, patch);
    }
    return {
      read(patch) {
        if (patch.op !== "replace-loc-text") {
          throw new LocTextPatchError(
            "invalid-span",
            "A localization source form contains a non-localization patch."
          );
        }
        return readLocTextAtPatch(text, patch);
      },
      replace(patch, replacement) {
        if (patch.op !== "replace-loc-text") {
          throw new LocTextPatchError(
            "invalid-span",
            "A localization source form contains a non-localization patch."
          );
        }
        return replaceLocTextAtPatch(text, patch, replacement);
      },
      text
    };
  }

  const patches = sourceFormPatches(form.sections);
  if (patches.some(
    (patch) =>
      patch.op !== "replace-pdx-scalar" &&
      patch.op !== "replace-pdx-integer-list" &&
      patch.op !== "replace-pdx-block-body"
  )) {
    throw new PdxScalarPatchError("invalid-span", "A PDX source form contains a non-PDX patch.");
  }
  const pdxPatches = patches.filter(
    (patch) =>
      patch.op === "replace-pdx-scalar" ||
      patch.op === "replace-pdx-integer-list" ||
      patch.op === "replace-pdx-block-body"
  );
  const spans = pdxPatches
    .map((patch) => patch.span)
    .sort((left, right) => left.start - right.start || left.end - right.end);
  for (let index = 1; index < spans.length; index += 1) {
    const previous = spans[index - 1];
    const current = spans[index];
    if (previous && current && current.start < previous.end) {
      throw new PdxScalarPatchError("invalid-span", "PDX guided controls contain overlapping source spans.");
    }
  }
  for (const patch of pdxPatches) {
    if (patch.op === "replace-pdx-scalar") {
      readPdxScalarAtPatch(text, patch);
    } else if (patch.op === "replace-pdx-integer-list") {
      readPdxIntegerListAtPatch(text, patch);
    } else {
      readPdxBlockBodyAtPatch(text, patch);
    }
  }
  return {
    read(patch) {
      if (patch.op === "replace-pdx-scalar") {
        return readPdxScalarAtPatch(text, patch);
      }
      if (patch.op === "replace-pdx-integer-list") {
        return readPdxIntegerListAtPatch(text, patch);
      }
      if (patch.op === "replace-pdx-block-body") {
        return readPdxBlockBodyAtPatch(text, patch);
      }
      throw new PdxScalarPatchError("invalid-span", "A PDX source form contains a non-PDX patch.");
    },
    replace(patch, replacement) {
      if (patch.op === "replace-pdx-scalar") {
        return replacePdxScalarAtPatch(text, patch, replacement);
      }
      if (patch.op === "replace-pdx-integer-list") {
        return replacePdxIntegerListAtPatch(text, patch, replacement);
      }
      if (patch.op === "replace-pdx-block-body") {
        return replacePdxBlockBodyAtPatch(text, patch, replacement);
      }
      throw new PdxScalarPatchError("invalid-span", "A PDX source form contains a non-PDX patch.");
    },
    text
  };
}

function sourceFormPatches(sections: SourceFormSection[]): SourceFormPatch[] {
  const patches: SourceFormPatch[] = [];
  const stack = [...sections];
  while (stack.length > 0) {
    const section = stack.pop();
    if (!section) {
      continue;
    }
    for (const control of section.controls ?? []) {
      if (control.patch) {
        patches.push(control.patch);
      }
    }
    stack.push(...(section.sections ?? []));
  }
  return patches;
}

function GuidedSourceFormSection({
  document,
  disabled,
  locale,
  onChange,
  section,
  t
}: {
  document: GuidedScalarDocument;
  disabled: boolean;
  locale: Locale;
  onChange: (change: GuidedSourceFormChange) => void;
  section: SourceFormSection;
  t: Translator;
}) {
  const description = section.description ? localizedSourceFormText(section.description, locale) : "";
  return (
    <fieldset className="guided-source-form-section" data-source-form-section-id={section.id}>
      <legend>{localizedSourceFormText(section.label, locale)}</legend>
      {description ? <small className="guided-source-form-section-description">{description}</small> : null}
      {(section.controls?.length ?? 0) > 0 ? (
        <div className="guided-source-form-controls">
          {section.controls?.map((control) => (
            <GuidedSourceFormControl
              control={control}
              document={document}
              disabled={disabled}
              key={control.id}
              locale={locale}
              onChange={onChange}
              t={t}
            />
          ))}
        </div>
      ) : null}
      {(section.sections?.length ?? 0) > 0 ? (
        <div className="guided-source-form-sections nested">
          {section.sections?.map((child) => (
            <GuidedSourceFormSection
              document={document}
              disabled={disabled}
              key={child.id}
              locale={locale}
              onChange={onChange}
              section={child}
              t={t}
            />
          ))}
        </div>
      ) : null}
    </fieldset>
  );
}

function GuidedSourceFormControl({
  control,
  document,
  disabled,
  locale,
  onChange,
  t
}: {
  control: SourceFormControl;
  document: GuidedScalarDocument;
  disabled: boolean;
  locale: Locale;
  onChange: (change: GuidedSourceFormChange) => void;
  t: Translator;
}) {
  const inputId = useId();
  const descriptionId = `${inputId}-description`;
  const errorId = `${inputId}-error`;
  const [editError, setEditError] = useState("");
  const label = localizedSourceFormText(control.label, locale);
  const description = control.description ? localizedSourceFormText(control.description, locale) : "";
  const placeholder = control.placeholder ? localizedSourceFormText(control.placeholder, locale) : undefined;
  const patch = control.patch;
  const readResult = readControlValue(document, control, t);
  const controlError = readResult.error || editError;
  const controlDisabled = disabled || Boolean(controlError);
  const describedBy = [description ? descriptionId : "", controlError ? errorId : ""].filter(Boolean).join(" ") || undefined;

  const applyReplacement = (replacement: JsonScalarReplacement) => {
    if (!patch) {
      setEditError(t("workspace.module.editor.guidedFormMissingPatch"));
      return;
    }
    try {
      const next = document.replace(patch, replacement);
      setEditError("");
      if (next !== document.text) {
        onChange({
          baseText: document.text,
          controlId: control.id,
          text: next,
          value: scalarForReplacement(replacement, patch),
        });
      }
    } catch (error) {
      setEditError(sourceFormErrorMessage(error, t));
    }
  };

  let input = null;
  if (readResult.scalar) {
    const scalar = readResult.scalar;
    if (control.control === "readonly") {
      input = <input aria-describedby={describedBy} disabled={disabled} id={inputId} readOnly value={displayScalar(scalar.value)} />;
    } else if (control.control === "text") {
      input = patch?.op === "replace-loc-text"
        ? (
            <SourceFormBufferedTextInput
              describedBy={describedBy}
              disabled={disabled || Boolean(readResult.error)}
              id={inputId}
              invalid={Boolean(controlError)}
              multiline={control.multiline === true}
              onCommit={applyReplacement}
              onEdit={() => setEditError("")}
              placeholder={placeholder}
              token={scalar}
            />
          )
        : patch?.op === "replace-pdx-integer-list" || patch?.op === "replace-pdx-block-body"
        ? (
            <SourceFormBufferedTextInput
              describedBy={describedBy}
              disabled={disabled || Boolean(readResult.error)}
              id={inputId}
              invalid={Boolean(controlError)}
              multiline
              onCommit={applyReplacement}
              onEdit={() => setEditError("")}
              placeholder={placeholder}
              token={scalar}
            />
          )
        : patch?.op === "replace-pdx-scalar"
        ? (
            <SourceFormPdxTextInput
              describedBy={describedBy}
              disabled={disabled || Boolean(readResult.error)}
              id={inputId}
              invalid={Boolean(controlError)}
              onCommit={applyReplacement}
              onEdit={() => setEditError("")}
              placeholder={placeholder}
              token={scalar}
            />
          )
        : (
            <input
              aria-describedby={describedBy}
              aria-invalid={Boolean(controlError) || undefined}
              disabled={controlDisabled}
              id={inputId}
              onChange={(event) => applyReplacement({ kind: "string", value: event.target.value })}
              placeholder={placeholder}
              type="text"
              value={typeof scalar.value === "string" ? scalar.value : ""}
            />
          );
    } else if (control.control === "boolean") {
      input = (
        <input
          aria-describedby={describedBy}
          aria-invalid={Boolean(controlError) || undefined}
          checked={scalar.value === true}
          disabled={controlDisabled}
          id={inputId}
          onChange={(event) => applyReplacement({ kind: "boolean", value: event.target.checked })}
          type="checkbox"
        />
      );
    } else if (control.control === "choice") {
      input = (
        <SourceFormChoiceInput
          choices={control.choices ?? []}
          describedBy={describedBy}
          disabled={controlDisabled}
          id={inputId}
          locale={locale}
          onChange={(value) => applyReplacement(replacementForScalar(value))}
          value={scalar.value}
        />
      );
    } else {
      input = (
        <SourceFormNumberInput
          control={control}
          describedBy={describedBy}
          disabled={controlDisabled}
          id={inputId}
          onCommit={applyReplacement}
          placeholder={placeholder}
          t={t}
          token={scalar}
        />
      );
    }
  }

  return (
    <div
      className={`guided-source-form-control module-create-field ${control.control}`}
      data-source-form-control-id={control.id}
      data-source-form-control-kind={control.control}
      data-source-form-description-source={control.description_source}
      data-source-form-multiline={control.control === "text" && control.multiline ? "true" : undefined}
    >
      <label htmlFor={inputId}>
        <small>{label}</small>
      </label>
      {description ? (
        <span className="module-create-field-description" id={descriptionId}>
          {description}
        </span>
      ) : null}
      {input}
      {controlError ? (
        <span className="module-create-field-error" id={errorId} role="alert">
          {controlError}
        </span>
      ) : null}
    </div>
  );
}

function SourceFormBufferedTextInput({
  describedBy,
  disabled,
  id,
  invalid,
  multiline,
  onCommit,
  onEdit,
  placeholder,
  token
}: {
  describedBy?: string;
  disabled: boolean;
  id: string;
  invalid: boolean;
  multiline: boolean;
  onCommit: (replacement: JsonScalarReplacement) => void;
  onEdit: () => void;
  placeholder?: string;
  token: JsonScalarToken;
}) {
  const currentValue = typeof token.value === "string" ? token.value : "";
  const [pending, setPending] = useState(currentValue);
  const submittedValue = useRef(currentValue);

  useEffect(() => {
    setPending(currentValue);
    submittedValue.current = currentValue;
  }, [currentValue, token.token]);

  const commit = () => {
    if (pending === currentValue || pending === submittedValue.current) {
      return;
    }
    submittedValue.current = pending;
    onCommit({ kind: "string", value: pending });
  };
  const shared = {
    "aria-describedby": describedBy,
    "aria-invalid": invalid || undefined,
    disabled,
    id,
    onBlur: commit,
    onChange: (event: ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
      setPending(event.target.value);
      onEdit();
    },
    onKeyDown: (event: KeyboardEvent<HTMLInputElement | HTMLTextAreaElement>) => {
      if (event.key === "Escape") {
        event.preventDefault();
        submittedValue.current = currentValue;
        setPending(currentValue);
        onEdit();
        return;
      }
      if (event.key === "Enter" && (!multiline || event.metaKey || event.ctrlKey)) {
        event.preventDefault();
        commit();
        event.currentTarget.blur();
      }
    },
    placeholder,
    value: pending
  };

  return multiline
    ? <textarea {...shared} rows={Math.max(2, Math.min(12, pending.split("\n").length))} />
    : <input {...shared} type="text" />;
}

function SourceFormPdxTextInput({
  describedBy,
  disabled,
  id,
  invalid,
  onCommit,
  onEdit,
  placeholder,
  token
}: {
  describedBy?: string;
  disabled: boolean;
  id: string;
  invalid: boolean;
  onCommit: (replacement: JsonScalarReplacement) => void;
  onEdit: () => void;
  placeholder?: string;
  token: JsonScalarToken;
}) {
  const currentValue = typeof token.value === "string" ? token.value : "";
  const [pending, setPending] = useState(currentValue);
  const submittedValue = useRef(currentValue);

  useEffect(() => {
    setPending(currentValue);
    submittedValue.current = currentValue;
  }, [currentValue, token.token]);

  const commit = () => {
    if (pending === currentValue || pending === submittedValue.current) {
      return;
    }
    submittedValue.current = pending;
    onCommit({ kind: "string", value: pending });
  };

  return (
    <input
      aria-describedby={describedBy}
      aria-invalid={invalid || undefined}
      disabled={disabled}
      id={id}
      onBlur={commit}
      onChange={(event) => {
        setPending(event.target.value);
        onEdit();
      }}
      onKeyDown={(event) => {
        if (event.key === "Enter") {
          event.preventDefault();
          commit();
          event.currentTarget.blur();
          return;
        }
        if (event.key === "Escape") {
          event.preventDefault();
          submittedValue.current = currentValue;
          setPending(currentValue);
          onEdit();
        }
      }}
      placeholder={placeholder}
      type="text"
      value={pending}
    />
  );
}

function SourceFormChoiceInput({
  choices,
  describedBy,
  disabled,
  id,
  locale,
  onChange,
  value
}: {
  choices: SourceFormChoice[];
  describedBy?: string;
  disabled: boolean;
  id: string;
  locale: Locale;
  onChange: (value: SourceFormScalar) => void;
  value: JsonScalarToken["value"];
}) {
  const selectedIndex = choices.findIndex((choice) => sameScalar(choice.value, value));
  return (
    <select
      aria-describedby={describedBy}
      aria-invalid={disabled || undefined}
      disabled={disabled || choices.length === 0}
      id={id}
      onChange={(event) => {
        const index = Number(event.target.value);
        const choice = choices[index];
        if (choice) {
          onChange(choice.value);
        }
      }}
      value={selectedIndex < 0 ? "" : String(selectedIndex)}
    >
      {selectedIndex < 0 ? <option value="">{displayScalar(value)}</option> : null}
      {choices.map((choice, index) => (
        <option key={`${index}:${displayScalar(choice.value)}`} value={index}>
          {localizedSourceFormText(choice.label, locale)}
        </option>
      ))}
    </select>
  );
}

function SourceFormNumberInput({
  control,
  describedBy,
  disabled,
  id,
  onCommit,
  placeholder,
  t,
  token
}: {
  control: SourceFormControl;
  describedBy?: string;
  disabled: boolean;
  id: string;
  onCommit: (replacement: JsonScalarReplacement) => void;
  placeholder?: string;
  t: Translator;
  token: JsonScalarToken;
}) {
  const [pending, setPending] = useState(token.token);
  const [validationError, setValidationError] = useState("");
  const submittedToken = useRef("");
  const patchKey = JSON.stringify(control.patch ?? null);
  const validationErrorId = `${id}-number-error`;

  useEffect(() => {
    setPending(token.token);
    setValidationError("");
    submittedToken.current = "";
  }, [patchKey, token.token]);

  const commit = (rawToken: string, showError: boolean) => {
    let parsed: { token: string; value: number };
    try {
      parsed = control.patch?.op === "replace-pdx-scalar"
        ? parseFinitePdxNumberToken(rawToken)
        : parseFiniteJsonNumberToken(rawToken);
    } catch (error) {
      if (showError) {
        setValidationError(sourceFormErrorMessage(error, t));
      }
      return;
    }
    if (control.min !== undefined && parsed.value < control.min) {
      if (showError) {
        setValidationError(t("workspace.module.editor.guidedNumberMin", { min: control.min }));
      }
      return;
    }
    if (control.max !== undefined && parsed.value > control.max) {
      if (showError) {
        setValidationError(t("workspace.module.editor.guidedNumberMax", { max: control.max }));
      }
      return;
    }
    setValidationError("");
    if (parsed.token === token.token || submittedToken.current === parsed.token) {
      return;
    }
    submittedToken.current = parsed.token;
    onCommit({ kind: "number", token: parsed.token });
  };

  return (
    <>
      <input
        aria-describedby={[describedBy, validationError ? validationErrorId : ""].filter(Boolean).join(" ") || undefined}
        aria-invalid={disabled || Boolean(validationError) || undefined}
        disabled={disabled}
        id={id}
        inputMode="decimal"
        max={control.max}
        min={control.min}
        onBlur={(event) => commit(event.currentTarget.value, true)}
        onChange={(event) => {
          setPending(event.target.value);
          setValidationError("");
          commit(event.target.value, false);
        }}
        onKeyDown={(event) => {
          if (event.key === "Enter") {
            event.preventDefault();
            commit(event.currentTarget.value, true);
            event.currentTarget.blur();
          }
        }}
        placeholder={placeholder}
        step={control.step ?? "any"}
        type="number"
        value={pending}
      />
      {validationError ? (
        <span className="module-create-field-error" id={validationErrorId} role="alert">
          {validationError}
        </span>
      ) : null}
    </>
  );
}

function readControlValue(
  document: GuidedScalarDocument,
  control: SourceFormControl,
  t: Translator
): { scalar: JsonScalarToken | null; error: string } {
  if (control.control === "readonly") {
    return { scalar: payloadScalarToken(control.value), error: "" };
  }
  if (!control.patch) {
    return { scalar: null, error: t("workspace.module.editor.guidedFormMissingPatch") };
  }

  let scalar: JsonScalarToken;
  try {
    scalar = document.read(control.patch);
  } catch (error) {
    return { scalar: null, error: sourceFormErrorMessage(error, t) };
  }

  const expectedKind = expectedControlKind(control);
  if (expectedKind && scalar.kind !== expectedKind) {
    return {
      scalar,
      error: t("workspace.module.editor.guidedFormExpectedKind", { expected: expectedKind, actual: scalar.kind })
    };
  }
  if (control.control === "choice") {
    const choices = control.choices ?? [];
    if (choices.length === 0) {
      return { scalar, error: t("workspace.module.editor.guidedFormChoiceEmpty") };
    }
    if (choices.some((choice) => scalarKind(choice.value) !== scalar.kind)) {
      return { scalar, error: t("workspace.module.editor.guidedFormChoiceType") };
    }
  }
  return { scalar, error: "" };
}

function expectedControlKind(control: SourceFormControl): JsonScalarKind | null {
  if (control.control === "text") {
    return "string";
  }
  if (control.control === "number") {
    return "number";
  }
  if (control.control === "boolean") {
    return "boolean";
  }
  if (control.control === "choice") {
    return scalarKind(control.value);
  }
  return null;
}

function scalarKind(value: SourceFormScalar): Exclude<JsonScalarKind, "null"> {
  if (typeof value === "string") {
    return "string";
  }
  if (typeof value === "number") {
    return "number";
  }
  return "boolean";
}

function payloadScalarToken(value: SourceFormScalar): JsonScalarToken {
  const kind = scalarKind(value);
  const token = kind === "string" ? JSON.stringify(value) : String(value);
  return { from: 0, to: token.length, kind, token, value };
}

function replacementForScalar(value: SourceFormScalar): JsonScalarReplacement {
  if (typeof value === "string") {
    return { kind: "string", value };
  }
  if (typeof value === "number") {
    return { kind: "number", token: String(value) };
  }
  return { kind: "boolean", value };
}

function scalarForReplacement(
  replacement: JsonScalarReplacement,
  patch: SourceFormPatch,
): SourceFormScalar {
  if (replacement.kind === "string" || replacement.kind === "boolean") {
    return replacement.value;
  }
  if (replacement.kind !== "number") {
    throw new Error("Guided source forms cannot write null scalar values.");
  }
  if (patch.op === "replace-pdx-scalar") {
    return parseFinitePdxNumberToken(replacement.token).value;
  }
  if (patch.op === "replace-json-scalar") {
    return parseFiniteJsonNumberToken(replacement.token).value;
  }
  throw new Error("Localization source forms cannot write numeric values.");
}

function sameScalar(left: SourceFormScalar, right: JsonScalarToken["value"]): boolean {
  return typeof left === typeof right && Object.is(left, right);
}

function displayScalar(value: JsonScalarToken["value"]): string {
  return value === null ? "null" : String(value);
}

const JSON_SCALAR_ERROR_KEYS: Record<JsonScalarPatchErrorCode, TranslationKey> = {
  "container-target": "workspace.module.editor.guidedFormContainerTarget",
  "duplicate-property": "workspace.module.editor.guidedFormDuplicateProperty",
  "invalid-json": "workspace.module.editor.guidedFormInvalidJson",
  "invalid-number": "workspace.module.editor.guidedFormInvalidNumber",
  "missing-path": "workspace.module.editor.guidedFormMissingPath",
  "type-mismatch": "workspace.module.editor.guidedFormTypeMismatch"
};

const PDX_SCALAR_ERROR_KEYS: Record<PdxScalarPatchErrorCode, TranslationKey> = {
  "invalid-identifier": "workspace.module.editor.guidedFormInvalidPdxIdentifier",
  "invalid-number": "workspace.module.editor.guidedFormInvalidPdxNumber",
  "invalid-pdx-string": "workspace.module.editor.guidedFormInvalidPdxString",
  "invalid-span": "workspace.module.editor.guidedFormInvalidPdxSpan",
  "stale-source": "workspace.module.editor.guidedFormStalePdxSpan",
  "type-mismatch": "workspace.module.editor.guidedFormTypeMismatch"
};

const LOC_TEXT_ERROR_KEYS: Record<LocTextPatchErrorCode, TranslationKey> = {
  "invalid-span": "workspace.module.editor.guidedFormInvalidLocSpan",
  "invalid-text": "workspace.module.editor.guidedFormInvalidLocText",
  "stale-source": "workspace.module.editor.guidedFormStaleLocSpan",
  "type-mismatch": "workspace.module.editor.guidedFormTypeMismatch"
};

function sourceFormErrorMessage(error: unknown, t: Translator): string {
  if (error instanceof JsonScalarPatchError) {
    return t(JSON_SCALAR_ERROR_KEYS[error.code]);
  }
  if (error instanceof PdxScalarPatchError) {
    return t(PDX_SCALAR_ERROR_KEYS[error.code]);
  }
  if (error instanceof LocTextPatchError) {
    return t(LOC_TEXT_ERROR_KEYS[error.code]);
  }
  if (error instanceof Error) {
    return error.message;
  }
  return String(error);
}
