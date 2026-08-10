import CodeMirror from "@uiw/react-codemirror";
import { json } from "@codemirror/lang-json";
import { yaml } from "@codemirror/lang-yaml";
import { EditorView } from "@codemirror/view";
import { useMemo } from "react";
import type { ModuleSourceSlot } from "./model";
import { commonCodeEditorExtensions } from "./codeMirrorSetup";
import { createPdxLspExtensions } from "./pdxLsp";
import type { ThemeName } from "../types";

type SourceCodeEditorProps = {
  gameRoot?: string;
  kind: ModuleSourceSlot["editorKind"];
  projectRoot?: string;
  sourcePath?: string;
  theme: ThemeName;
  value: string;
  onChange: (value: string) => void;
};

function jsonExtensions() {
  return [json(), EditorView.lineWrapping];
}

function yamlExtensions() {
  return [yaml(), EditorView.lineWrapping];
}

export function SourceCodeEditor({ gameRoot, kind, projectRoot, sourcePath, theme, value, onChange }: SourceCodeEditorProps) {
  const editorTheme = useMemo(() => createAppCodeMirrorTheme(theme), [theme]);
  const sourceExtension = sourcePathExtension(sourcePath);
  const isJsonSource = sourceExtension === "json";
  const isYamlSource = sourceExtension === "yaml" || sourceExtension === "yml";
  const extensions = useMemo(() => {
    if (kind === "localization" || isYamlSource) {
      return [...commonCodeEditorExtensions, ...yamlExtensions()];
    }
    if (isJsonSource) {
      return [...commonCodeEditorExtensions, ...jsonExtensions()];
    }
    return [...commonCodeEditorExtensions, EditorView.lineWrapping, ...createPdxLspExtensions({ gameRoot, projectRoot, sourcePath })];
  }, [gameRoot, isJsonSource, isYamlSource, kind, projectRoot, sourcePath]);

  return (
    <CodeMirror
      basicSetup={false}
      extensions={extensions}
      height="100%"
      onChange={onChange}
      theme={editorTheme}
      value={value}
    />
  );
}

function sourcePathExtension(sourcePath: string | undefined): string {
  const cleanPath = sourcePath?.trim().split(/[?#]/, 1)[0] ?? "";
  return cleanPath.match(/\.([^/.\\]+)$/)?.[1]?.toLowerCase() ?? "";
}

function createAppCodeMirrorTheme(theme: ThemeName) {
  return EditorView.theme(
    {
      "&": {
        backgroundColor: "var(--cm-bg)",
        color: "var(--cm-text)"
      },
      ".cm-content": {
        caretColor: "var(--accent)",
        fontFamily: "SFMono-Regular, Menlo, Consolas, \"Liberation Mono\", monospace",
        lineHeight: "1.55"
      },
      ".cm-cursor, .cm-dropCursor": {
        borderLeftColor: "var(--accent)"
      },
      "&.cm-focused": {
        outline: "none"
      },
      "&.cm-focused .cm-selectionBackground, .cm-selectionBackground, .cm-content ::selection": {
        backgroundColor: "var(--cm-selection)"
      },
      ".cm-gutters": {
        backgroundColor: "var(--cm-gutter-bg)",
        borderRightColor: "var(--border)",
        color: "var(--cm-gutter-text)"
      },
      ".cm-activeLine": {
        backgroundColor: "var(--cm-active-line)"
      },
      ".cm-activeLineGutter": {
        backgroundColor: "var(--cm-active-line)",
        color: "var(--cm-text)"
      },
      ".cm-foldPlaceholder": {
        backgroundColor: "var(--surface-2)",
        borderColor: "var(--border)",
        color: "var(--muted)"
      },
      ".cm-searchMatch": {
        backgroundColor: "var(--cm-search-match)",
        outline: "1px solid var(--warning)"
      },
      ".cm-searchMatch.cm-searchMatch-selected": {
        backgroundColor: "var(--cm-search-selected)"
      },
      ".cm-matchingBracket, .cm-nonmatchingBracket": {
        backgroundColor: "var(--accent-soft)",
        outline: "1px solid var(--border-strong)"
      },
      ".cm-tooltip": {
        backgroundColor: "var(--surface)",
        borderColor: "var(--border-strong)",
        color: "var(--text)"
      },
      ".cm-tooltip-autocomplete ul li[aria-selected]": {
        backgroundColor: "var(--accent-soft)",
        color: "var(--text)"
      },
      ".cm-completionIcon": {
        color: "var(--muted)"
      },
      ".cm-completionLabel": {
        color: "var(--text)"
      },
      ".cm-completionDetail": {
        color: "var(--muted)"
      },
      ".cm-diagnostic": {
        backgroundColor: "var(--surface-2)",
        color: "var(--text)"
      },
      ".cm-lintRange-error": {
        backgroundImage: "linear-gradient(45deg, transparent 65%, var(--danger) 80%, transparent 90%)"
      }
    },
    { dark: theme === "dark" }
  );
}
