ObjC.import("AppKit");
ObjC.import("Foundation");
ObjC.import("WebKit");

ObjC.registerSubclass({
  name: "ParaDevAppDelegate",
  methods: {
    "applicationShouldTerminateAfterLastWindowClosed:": {
      types: ["bool", ["id"]],
      implementation: () => true,
    },
  },
});

/**
 * Open the loopback ParaDev application in a native WKWebView window.
 *
 * The host owns only the window lifecycle. Application behavior remains behind
 * the local JSON API served by ParaDev.
 *
 * @param {string[]} argv - Application URL followed by an optional icon path.
 */
function run(argv) {
  if (argv.length < 1) throw new Error("ParaDev WebView host requires an application URL");

  const url = $.NSURL.URLWithString(argv[0]);
  if (
    !url ||
    ObjC.unwrap(url.scheme) !== "http" ||
    !["127.0.0.1", "localhost", "::1"].includes(ObjC.unwrap(url.host))
  ) {
    throw new Error("ParaDev WebView host accepts loopback HTTP URLs only");
  }

  const app = $.NSApplication.sharedApplication;
  const delegate = $.ParaDevAppDelegate.alloc.init;
  app.delegate = delegate;
  app.setActivationPolicy($.NSApplicationActivationPolicyRegular);

  if (argv[1]) {
    const icon = $.NSImage.alloc.initWithContentsOfFile(argv[1]);
    if (icon) app.applicationIconImage = icon;
  }

  const frame = $.NSMakeRect(0, 0, 1360, 900);
  const style =
    $.NSWindowStyleMaskTitled |
    $.NSWindowStyleMaskClosable |
    $.NSWindowStyleMaskMiniaturizable |
    $.NSWindowStyleMaskResizable;
  const window = $.NSWindow.alloc.initWithContentRectStyleMaskBackingDefer(
    frame,
    style,
    $.NSBackingStoreBuffered,
    false,
  );
  window.title = "ParaDev";
  window.minSize = $.NSMakeSize(760, 520);
  window.releasedWhenClosed = false;

  const webView = $.WKWebView.alloc.initWithFrameConfiguration(frame, $.WKWebViewConfiguration.alloc.init);
  webView.autoresizingMask = $.NSViewWidthSizable | $.NSViewHeightSizable;
  webView.loadRequest($.NSURLRequest.requestWithURL(url));
  window.contentView = webView;
  window.center;
  window.makeKeyAndOrderFront(null);
  app.activateIgnoringOtherApps(true);
  app.run;
}
