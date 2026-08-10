import * as vscode from "vscode";
import { LanguageClient, LanguageClientOptions, ServerOptions, TransportKind } from "vscode-languageclient/node";

let client: LanguageClient | undefined;

export async function activate(context: vscode.ExtensionContext): Promise<void> {
  context.subscriptions.push(
    vscode.commands.registerCommand("paradev.restartLsp", async () => {
      await restartClient();
    })
  );
  await restartClient();
}

export async function deactivate(): Promise<void> {
  await stopClient();
}

async function restartClient(): Promise<void> {
  await stopClient();
  client = new LanguageClient("paradevPdxLsp", "ParaDev PDX LSP", serverOptions(), clientOptions());
  await client.start();
}

async function stopClient(): Promise<void> {
  if (client === undefined) {
    return;
  }
  const running = client;
  client = undefined;
  await running.stop();
}

function serverOptions(): ServerOptions {
  const workspaceFolder = activeWorkspaceFolder();
  const config = vscode.workspace.getConfiguration("paradev.lsp");
  const command = config.get<string>("command", "paradev");
  const args = [...config.get<string[]>("args", ["lsp", "serve"])];
  if (workspaceFolder !== undefined) {
    args.push("--project", workspaceFolder.uri.fsPath);
  }
  const database = config.get<string>("database", "").trim();
  if (database.length > 0) {
    args.push("--database", database);
  }
  const gameRoot = config.get<string>("gameRoot", "").trim();
  if (gameRoot.length > 0) {
    args.push("--game-root", gameRoot);
  }
  args.push("--limit", String(completionLimit()));
  const executable = {
    command,
    args,
    transport: TransportKind.stdio,
    options: {
      cwd: workspaceFolder?.uri.fsPath
    }
  };
  return { run: executable, debug: executable };
}

function clientOptions(): LanguageClientOptions {
  const workspaceFolder = activeWorkspaceFolder();
  const config = vscode.workspace.getConfiguration("paradev.lsp");
  const database = config.get<string>("database", "").trim();
  const gameRoot = config.get<string>("gameRoot", "").trim();
  return {
    documentSelector: [{ scheme: "file", language: "paradox-pdx" }],
    initializationOptions: {
      projectPath: workspaceFolder?.uri.fsPath,
      database: database.length > 0 ? database : undefined,
      gameRoot: gameRoot.length > 0 ? gameRoot : undefined,
      completionLimit: completionLimit()
    },
    synchronize: {
      fileEvents: vscode.workspace.createFileSystemWatcher("**/paradev.yaml")
    }
  };
}

function activeWorkspaceFolder(): vscode.WorkspaceFolder | undefined {
  const activeDocument = vscode.window.activeTextEditor?.document;
  if (activeDocument !== undefined) {
    return vscode.workspace.getWorkspaceFolder(activeDocument.uri);
  }
  return vscode.workspace.workspaceFolders?.[0];
}

function completionLimit(): number {
  const value = vscode.workspace.getConfiguration("paradev.lsp").get<number>("completionLimit", 100);
  return Number.isFinite(value) && value > 0 ? Math.floor(value) : 100;
}
