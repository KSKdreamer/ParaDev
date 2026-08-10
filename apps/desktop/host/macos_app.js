ObjC.import("AppKit");
ObjC.import("Foundation");
ObjC.import("WebKit");
ObjC.import("signal");
ObjC.import("unistd");

let serverTask = null;
let serverErrorPath = "";
let serverReadyPath = "";
let serverProcessIdentifier = 0;
let applicationBundle = null;
let applicationDelegate = null;
let applicationQuitting = false;
let mainWindow = null;

function unwrap(value) {
  return value ? ObjC.unwrap(value) : "";
}

function metadataValue(bundle, key) {
  return unwrap(bundle.infoDictionary.objectForKey(key));
}

function resolveApplicationBundle() {
  if (applicationBundle) return applicationBundle;
  const mainBundle = $.NSBundle.mainBundle;
  if (metadataValue(mainBundle, "ParaDevPythonExecutable")) {
    applicationBundle = mainBundle;
    return applicationBundle;
  }

  const args = $.NSProcessInfo.processInfo.arguments;
  for (let index = 0; index < args.count; index += 1) {
    const executable = unwrap(args.objectAtIndex(index));
    const marker = "/Contents/MacOS/";
    const markerIndex = executable.lastIndexOf(marker);
    if (markerIndex < 0) continue;
    const bundlePath = executable.slice(0, markerIndex);
    if (!bundlePath.endsWith(".app")) continue;
    const candidate = $.NSBundle.bundleWithPath(bundlePath);
    if (candidate && metadataValue(candidate, "ParaDevPythonExecutable")) {
      applicationBundle = candidate;
      return applicationBundle;
    }
  }
  throw new Error("Could not resolve the enclosing ParaDev.app bundle");
}

function bundleValue(key) {
  return metadataValue(resolveApplicationBundle(), key);
}

function processArguments() {
  const values = [];
  const args = $.NSProcessInfo.processInfo.arguments;
  for (let index = 0; index < args.count; index += 1) values.push(unwrap(args.objectAtIndex(index)));
  return values;
}

function configureTask(executable, args, capture = false) {
  const task = $.NSTask.alloc.init;
  task.executableURL = $.NSURL.fileURLWithPath(executable);
  task.arguments = args;
  if (capture) {
    const pipe = $.NSPipe.pipe;
    task.standardOutput = pipe;
    task.standardError = $.NSFileHandle.fileHandleWithNullDevice;
    return { task, pipe };
  }
  task.standardOutput = $.NSFileHandle.fileHandleWithNullDevice;
  task.standardError = $.NSFileHandle.fileHandleWithNullDevice;
  return { task, pipe: null };
}

function runCaptured(executable, args) {
  const { task, pipe } = configureTask(executable, args, true);
  const error = Ref();
  if (!task.launchAndReturnError(error)) {
    throw new Error(`Could not launch ${executable}: ${unwrap(error[0].localizedDescription)}`);
  }
  task.waitUntilExit;
  const data = pipe.fileHandleForReading.readDataToEndOfFile;
  const output = unwrap($.NSString.alloc.initWithDataEncoding(data, $.NSUTF8StringEncoding));
  if (task.terminationStatus !== 0) throw new Error(`${executable} exited with status ${task.terminationStatus}`);
  return output.trim();
}

const SERVER_ERROR_LIMIT = 8192;
const SERVER_READY_LIMIT = 8192;
const SERVER_READY_SCHEMA = "paradev.gui-server-ready.v1";

function temporaryServerFile(kind) {
  const token = unwrap($.NSUUID.UUID.UUIDString);
  const path = `${unwrap($.NSTemporaryDirectory())}paradev-${$.NSProcessInfo.processInfo.processIdentifier}-${token}-${kind}.log`;
  const created = $.NSFileManager.defaultManager.createFileAtPathContentsAttributes(path, $(), $());
  if (!created) throw new Error(`Could not create the ParaDev ${kind} file`);
  return path;
}

function readServerFile(path, limit) {
  if (!path) return "";
  const data = $.NSData.dataWithContentsOfFile(path);
  if (!data || data.length === 0) return "";
  const value = unwrap($.NSString.alloc.initWithDataEncoding(data, $.NSUTF8StringEncoding));
  return String(value || "").slice(-limit);
}

function removeServerFiles() {
  for (const path of [serverReadyPath, serverErrorPath]) {
    if (path) $.NSFileManager.defaultManager.removeItemAtPathError(path, Ref());
  }
  serverReadyPath = "";
  serverErrorPath = "";
}

function launchServerTask(executable, args) {
  const { task } = configureTask(executable, args);
  serverReadyPath = temporaryServerFile("ready");
  serverErrorPath = temporaryServerFile("error");
  const environment = $.NSProcessInfo.processInfo.environment.mutableCopy;
  environment.setObjectForKey(serverReadyPath, "PARADEV_GUI_READY_FILE");
  task.environment = environment;
  const errorHandle = $.NSFileHandle.fileHandleForWritingAtPath(serverErrorPath);
  task.standardError = errorHandle;
  const error = Ref();
  if (!task.launchAndReturnError(error)) {
    errorHandle.closeFile;
    removeServerFiles();
    throw new Error(`Could not launch ${executable}: ${unwrap(error[0].localizedDescription)}`);
  }
  errorHandle.closeFile;
  return { task };
}

function isLoopbackUrl(value) {
  const url = $.NSURL.URLWithString(value);
  if (!url) return false;
  return unwrap(url.scheme) === "http" && ["127.0.0.1", "localhost", "::1"].includes(unwrap(url.host));
}

function validateReadyDocument(value) {
  const ready = JSON.parse(value);
  const keys = Object.keys(ready).sort().join(",");
  if (keys !== "host,nonce,port,schema") throw new Error("ParaDev server returned an invalid ready document");
  if (ready.schema !== SERVER_READY_SCHEMA) throw new Error("ParaDev server returned an unknown ready schema");
  if (ready.host !== "127.0.0.1") throw new Error("ParaDev server did not bind IPv4 loopback");
  if (!Number.isInteger(ready.port) || ready.port < 1 || ready.port > 65535) {
    throw new Error("ParaDev server returned an invalid loopback port");
  }
  if (typeof ready.nonce !== "string" || !/^[A-Za-z0-9_-]{32,256}$/.test(ready.nonce)) {
    throw new Error("ParaDev server returned an invalid instance nonce");
  }
  return ready;
}

function waitForReadyDocument() {
  for (let attempt = 0; attempt < 450; attempt += 1) {
    const readyText = readServerFile(serverReadyPath, SERVER_READY_LIMIT);
    const lineEnd = readyText.indexOf("\n");
    if (lineEnd >= 0) return validateReadyDocument(readyText.slice(0, lineEnd).trim());
    if (serverTask && !serverTask.running) {
      throw new Error(`ParaDev server exited with status ${serverTask.terminationStatus}`);
    }
    $.NSThread.sleepForTimeInterval(0.1);
  }
  throw new Error("ParaDev server did not publish its ready document");
}

function waitUntilReady(url, nonce) {
  const probe = `${url}/_paradev/app-instance`;
  for (let attempt = 0; attempt < 50; attempt += 1) {
    if (serverTask && !serverTask.running) {
      throw new Error(`ParaDev server exited with status ${serverTask.terminationStatus}`);
    }
    try {
      const response = JSON.parse(
        runCaptured("/usr/bin/curl", [
          "--silent",
          "--fail",
          "--max-time",
          "1",
          "--header",
          `X-ParaDev-Instance: ${nonce}`,
          probe,
        ]),
      );
      if (
        Object.keys(response).sort().join(",") === "nonce,schema" &&
        response.schema === SERVER_READY_SCHEMA &&
        response.nonce === nonce
      ) {
        return;
      }
      throw new Error("ParaDev server instance response did not match its ready document");
    } catch {
      $.NSThread.sleepForTimeInterval(0.15);
    }
  }
  throw new Error("ParaDev server did not become ready");
}

function stopServer() {
  if (serverProcessIdentifier > 0) {
    $.kill(serverProcessIdentifier, $.SIGTERM);
    serverProcessIdentifier = 0;
  }
  serverTask = null;
}

function startupFailureMessage(message) {
  const detail = readServerFile(serverErrorPath, SERVER_ERROR_LIMIT).trim();
  if (!detail) return message;
  return `${message}\n\nServer details:\n${detail}`;
}

ObjC.registerSubclass({
  name: "ParaDevBundledAppLifecycle",
  methods: {
    "windowWillClose:": {
      types: ["void", ["id"]],
      implementation: () => {
        stopServer();
        removeServerFiles();
        if (!applicationQuitting) $.NSApplication.sharedApplication.terminate(null);
      },
    },
  },
});

function showFailure(message) {
  const alert = $.NSAlert.alloc.init;
  alert.messageText = "ParaDev could not start";
  alert.informativeText = String(message);
  alert.alertStyle = $.NSAlertStyleCritical;
  alert.runModal;
}

/**
 * Run the installed ParaDev application.
 *
 * A loopback URL argument connects the window to an existing CLI-owned server.
 * A Finder launch starts a child server and stops it with the application.
 */
function run() {
  const supplied = arguments.length > 0 && Array.isArray(arguments[0]) ? arguments[0] : [];
  const argv = [...processArguments(), ...supplied];
  if (argv.includes("--print-bundle")) return unwrap(resolveApplicationBundle().bundlePath);

  const app = $.NSApplication.sharedApplication;
  applicationDelegate = $.ParaDevBundledAppLifecycle.alloc.init;
  app.setActivationPolicy($.NSApplicationActivationPolicyRegular);

  try {
    const requestedUrl = argv.find((value) => isLoopbackUrl(value));
    let applicationUrl = requestedUrl || "";
    if (!applicationUrl) {
      const python = bundleValue("ParaDevPythonExecutable");
      const module = bundleValue("ParaDevPythonModule") || "paradev.gui_macos";
      if (!python) {
        throw new Error(
          "The application has no Python runtime binding; reinstall it with `paradev-gui --install-app`.",
        );
      }
      const launched = launchServerTask(python, [
        "-m",
        module,
        "--serve",
        "--host",
        "127.0.0.1",
        "--port",
        "0",
        "--ready-json",
      ]);
      serverTask = launched.task;
      serverProcessIdentifier = serverTask.processIdentifier;
      const ready = waitForReadyDocument();
      applicationUrl = `http://${ready.host}:${ready.port}`;
      waitUntilReady(applicationUrl, ready.nonce);
      removeServerFiles();
    }
    if (!isLoopbackUrl(applicationUrl)) throw new Error("ParaDev accepts loopback application URLs only");

    const iconPath = `${unwrap(resolveApplicationBundle().resourcePath)}/ParaDev.icns`;
    const icon = $.NSImage.alloc.initWithContentsOfFile(iconPath);
    if (icon) app.applicationIconImage = icon;

    const frame = $.NSMakeRect(0, 0, 1360, 900);
    const style =
      $.NSWindowStyleMaskTitled |
      $.NSWindowStyleMaskClosable |
      $.NSWindowStyleMaskMiniaturizable |
      $.NSWindowStyleMaskResizable;
    mainWindow = $.NSWindow.alloc.initWithContentRectStyleMaskBackingDefer(
      frame,
      style,
      $.NSBackingStoreBuffered,
      false,
    );
    mainWindow.title = "ParaDev";
    mainWindow.minSize = $.NSMakeSize(760, 520);
    mainWindow.releasedWhenClosed = false;
    mainWindow.delegate = applicationDelegate;

    const webView = $.WKWebView.alloc.initWithFrameConfiguration(frame, $.WKWebViewConfiguration.alloc.init);
    webView.autoresizingMask = $.NSViewWidthSizable | $.NSViewHeightSizable;
    webView.loadRequest($.NSURLRequest.requestWithURL($.NSURL.URLWithString(applicationUrl)));
    mainWindow.contentView = webView;
    mainWindow.center;
    mainWindow.makeKeyAndOrderFront(null);
    app.activateIgnoringOtherApps(true);
  } catch (error) {
    stopServer();
    const message = error instanceof Error ? error.message : String(error);
    const visibleMessage = startupFailureMessage(message);
    removeServerFiles();
    $.NSLog(`ParaDev startup failed: ${visibleMessage}`);
    showFailure(visibleMessage);
    app.terminate(null);
  }
}

function quit() {
  applicationQuitting = true;
  stopServer();
  removeServerFiles();
  return true;
}
