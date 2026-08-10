"""Wheel-hosted desktop application contract."""

from __future__ import annotations


def get_bundle_contract() -> dict[str, object]:
    """Return the installed desktop application bundling contract.

    Args:
        None.

    Returns:
        dict[str, object]: JSON-safe build inputs, outputs, target support, and
        security invariants for the wheel-hosted system-WebView application.
    """

    return {
        "identifier": "bundle",
        "status": "implemented",
        "runtime": "python-wheel-loopback",
        "inputs": {
            "entrypoint": "paradev-gui",
            "frontend_source": "apps/desktop",
            "packaged_frontend": "src/paradev/resources/gui",
            "dependency_sources": ["requirements.txt"],
            "service": "same-origin FastAPI loopback API",
            "host_assets": "apps/desktop/host",
        },
        "tools": ["uv", "npm", "Vite", "setuptools"],
        "outputs": {
            "python_wheel": "dist/python/paradev-*.whl",
            "packaged_frontend": "paradev/resources/gui",
            "macos_application": "~/Applications/ParaDev.app",
        },
        "platform_priority": ["macos-system-webview", "browser-fallback"],
        "security": {
            "network": "loopback-only same-origin service",
            "instance": "per-launch nonce and private instance probe",
            "lifecycle": "application owns and terminates its Python server child",
        },
        "sdk_owned": True,
    }
