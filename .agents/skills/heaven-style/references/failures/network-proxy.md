---
id: failure-network-proxy
title: Network and proxy failures
enabled: true
order: 20
keywords: [network timeout, proxy, VPN, HTTP_PROXY, HTTPS_PROXY, connection refused, TLS]
description: Use when CLI/API/network commands fail while local VPN or proxy settings may be active.
---

# Network and Proxy Failures

## Pattern

CLI network calls fail with timeouts, TLS errors, connection resets, provider API failures, package-install failures, or inconsistent behavior between browser and terminal.

## Response

1. Check process proxy state before retrying blindly: `HTTP_PROXY`, `HTTPS_PROXY`, `ALL_PROXY`, `NO_PROXY`, lowercase variants, and tool-specific proxy config.
2. Assume local VPN may be on during development; make proxy behavior explicit per command rather than relying on ambient shell state.
3. Run one minimal connectivity probe for the target service and one neutral endpoint.
4. If a command should bypass proxy, run it with a scoped env override. If it should use proxy, set scoped proxy vars for that command only.
5. For package managers and CLIs, check their own proxy settings before changing code.
6. If repeated network failures block the main task, spawn a narrow subagent when available: "diagnose network/proxy only; identify env vars, failing endpoint, and scoped command fix."

## Do Not

- Do not commit proxy settings, tokens, or local network assumptions.
- Do not mark provider/backend support broken until proxy state and credentials are checked.
- Do not make global VPN/proxy changes without user approval.
