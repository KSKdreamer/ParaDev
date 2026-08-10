---
id: failure-auth-secrets
title: Auth, MCP, and secret lookup failures
enabled: true
order: 30
keywords: [Linear auth expired, Tavily auth failed, cannot find api key, missing token, MCP failed, GraphQL API, LLM provider key]
description: Use when MCP tools, CLIs, Linear/Tavily, GraphQL, or LLM providers fail because auth, tokens, or API keys are missing or expired.
---

# Auth, MCP, and Secret Lookup Failures

## Pattern

MCP calls, provider SDKs, CLIs, GraphQL calls, or LLM integrations fail repeatedly because auth appears expired, a token/API key is missing from the process env, or the active shell did not load the expected secrets. Linear is common and important, but this also applies to Tavily, LLM providers, GitHub, OpenRouter, DeepSeek, Portkey, and other local development integrations.

## Response

1. Classify the failure as auth/secret lookup, network/proxy, wrong environment, wrong workspace/team, or provider outage.
2. Inspect available secret sources without printing values: `~/.bashrc` or `~/.bash_profile`, repo-local `secret/*.token`, `.env*`, documented env var names, and any repo-provided `secret/setup.bash`.
3. Load only the needed variable into the current process or a scoped command. Keep token values out of chat, logs, committed files, review artifacts, and screenshots.
4. If an MCP repeatedly fails after env/proxy checks, use the provider's direct API path when available. For Linear, prefer the GraphQL API with the discovered token after three identical MCP/auth failures.
5. Record the env var name, credential source, endpoint/API path, and whether the fallback worked, without exposing the secret.
6. If auth debugging blocks the main coding/review task, spawn a narrow subagent when available: "diagnose provider auth only; report env var names, endpoint, command path, and whether direct API works; do not print secrets."

## Do Not

- Do not create duplicate Linear/provider records because lookup failed once.
- Do not log, print, paste, screenshot, or commit secret values.
- Do not keep retrying the same failing MCP call after three identical auth failures; switch to direct API fallback or ask for re-auth when no token exists.
- Do not broaden secret access beyond the specific provider needed for the current task.
