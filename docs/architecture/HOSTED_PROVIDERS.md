# Hosted provider assessment (S014a)

Assessed 2026-11-15 from the providers' own documentation, read in this session.
Provider terms change; every integration milestone re-reads the cited pages and
records the date it did so. This is an engineering/compliance assessment, not
legal advice. No credential was handled and no provider request was made.

The programme's question and boundaries are in
[ADR-0016](../decisions/ADR-0016-hosted-provider-broker.md) and the S014
milestones in the roadmap.

## Summary

| Provider route | Officially supported for this use? | Status | Main blockers / human actions |
| --- | --- | --- | --- |
| Google Gemma via Gemini API (free tier, owner's key) | Yes: Gemma models are served by the Gemini API with function calling and system instructions | **Scrapped by the owner (OD-12, 2026-11-15)** after intermittent provider HTTP 500 on multi-step turns | None; profile disabled. Integration record kept |
| OpenAI via Sign in with ChatGPT plan usage | Yes for open-source and locally hosted apps, self-serve, as a **preview** | **Eligible and integrated (S014d)**, with registered parameter gaps | Done 2026-11-15: Apache-2.0 licence, owner sign-in, per-app limit 10%, approved budgets (8/20/30) |
| Anthropic via Claude Pro subscription | **Not established.** Published policy directs developers' products, including Agent SDK use, to API keys | **Unavailable** until Anthropic confirms in writing | Owner may ask Anthropic; paid API use needs a separate spend authorisation (not given) |

## Google: Gemma on the Gemini API

Sources: [Gemma on the Gemini API](https://ai.google.dev/gemma/docs/core/gemma_on_gemini_api),
[terms](https://aistudio.google.com/docs/terms),
[rate limits](https://aistudio.google.com/docs/rate-limits),
[function calling](https://aistudio.google.com/docs/function-calling).

- **Models:** `gemma-4-26b-a4b-it` and `gemma-4-31b-it` are listed and accessible
  on the owner's project (30 RPM, 16K input TPM, 14.4K RPD each, free tier).
  S014c (2026-11-15): 26B failed every request whose history held two call turns,
  including a minimal synthetic one; 31B succeeded on 2 of 6 such requests, failing
  intermittently with HTTP 500. The owner moved the arm to 31B.
  [Report](../experiments/2026-11-15-gemma-integration.md).
- **Tools:** function declarations are supported for Gemma; the model returns
  function calls that the client executes and answers. System instructions are
  supported. Thinking is selectable (`high` or `minimal`), so the reasoning
  level is a setting to freeze before scoring.
- **Interfaces:** Google documents both `generateContent` and a newer
  `interactions` endpoint (`function_call` / `function_result` steps with ids;
  model steps, including thoughts, must be resent exactly in stateless mode).
  S014c chooses one documented REST interface and pins it; the Laboratory adds
  no SDK dependency unless the REST path is inadequate.
- **Limits:** rate limits apply **per project, not per key**; daily quotas reset
  at midnight Pacific time; exceeding a limit returns a rate-limit error (429
  `RESOURCE_EXHAUSTED` is the documented code for spend limits). The official
  page does not publish Gemma's free-tier numbers. Secondary reports vary (for
  example 30 RPM / 14,400 RPD), so they are **not** used: the owner reads the
  project's actual limits at AI Studio's rate-limit page before budgets are set.
- **Data use (unpaid quota):** Google may use inputs and outputs to improve its
  products, and human reviewers may read, annotate and process API input and
  output; users are told not to submit sensitive, confidential or personal
  information to unpaid services. **For users in the EEA, Switzerland or the UK, Google
  applies its paid-service data terms to unpaid quota** (not used to improve
  products; limited log retention). Which applies depends on the owner's region,
  which the owner confirms; either way the Laboratory sends only the experiment's
  model-facing conversation.
- **Terms of use:** the API is for developers building for professional or
  business purposes, users must be 18+, and in the EEA/Switzerland/UK only Paid
  Services may be used to make API clients available to *other users*. The
  Laboratory is the owner's own research tool, not offered to other users.
- **No paid tier or fallback** is enabled. A billing account on the project could
  change quota behaviour; the owner keeps the project on the free tier.

## OpenAI: Sign in with ChatGPT plan usage

Sources: [overview](https://developers.openai.com/siwc),
[plan usage for open-source apps](https://developers.openai.com/siwc/token-sharing-open-source),
[sign-in](https://developers.openai.com/siwc/token-sharing-open-source/sign-in),
[models and inference](https://developers.openai.com/siwc/token-sharing-open-source/models-and-inference),
[preview limitations](https://developers.openai.com/siwc/token-sharing-open-source/preview-limitations),
[errors and recovery](https://developers.openai.com/siwc/token-sharing-open-source/errors-and-recovery).

- **Eligibility:** the documentation covers plan usage "for open-source and
  locally hosted apps"; paid or remotely hosted apps go to an interest form.
  Registration is self-serve (dynamic client registration, no client secret).
  The Laboratory is locally hosted and, since S014d (OD-10, owner decision), all
  three repositories are licensed Apache-2.0. Wording re-checked 2026-11-15.
- **Flow:** OAuth with PKCE in the user's browser, loopback redirect on
  `127.0.0.1` only, scopes `offline_access resource.invoke
  chatgpt.tokens.use.direct` (plus `openid profile email`); the granted scopes
  must be checked, since an ID token alone does not authorise plan usage. A
  persisted opaque host id identifies each installation.
- **Inference:** `POST https://api.openai.com/v1/responses` with the bearer token,
  `store: false` and `stream: true` on every request, success only on
  `response.completed`. Never ChatGPT's `backend-api`. Models are those the
  signed-in account lists at `GET /v1/models` (`visibility == "list"`); the ChatGPT
  menu is not evidence of API access.
- **Unsupported parameters (preview, re-checked 2026-11-15):** `background`,
  `conversation`, `max_output_tokens`, `max_tool_calls`, `metadata`,
  `moderation`, `multi_agent`, `prompt`, `prompt_cache_retention`,
  `safety_identifier`, `temperature`, `top_logprobs`, `top_p`, `truncation`,
  `user` must be omitted; so must `previous_response_id` over HTTP. Explicit
  `system` message items are rejected (use `instructions`). The Responses API
  has no seed. Function/custom tools must be grouped in a `namespace` tool or
  sent via `additional_tools`; hosted tools (file search, code interpreter,
  computer use, hosted MCP, tool search, image generation) are not supported.
- **Errors:** documented codes include `subscription_sharing_usage_limit_exceeded`
  (429: pause; may be an app-specific limit), `subscription_sharing_user_not_eligible`
  (403: do not retry or loop through OAuth), `subscription_sharing_unsupported_capability`
  (400: do not resend), `subscription_sharing_usage_unavailable` (503: bounded
  backoff). Whether retries are charged is undocumented, so every attempt is
  counted. OpenAI does not notify the app when the user disconnects it; refresh
  failures end the session.
- **Comparability consequences:** no temperature, no output cap and an unknown
  seed mean the ChatGPT arm cannot match the local profile's sampling. These are
  registered as provider-specific conditions, never emulated.
- **Implemented (S014d):** Simulation `chatgpt_auth.py` (sign-in, refresh,
  revocation) and `chatgpt.py` (adapter `openai-responses-chatgpt-plan` 1.0.0).
  Live check: [2026-11-15 integration report](../experiments/2026-11-15-chatgpt-integration.md).
  Tokens refresh serially under a lock; unusable-refresh codes clear tokens and
  end the run; temporary refresh failures retry and keep tokens. Per-app limit
  set by the owner to 10% of the weekly allowance.

## Anthropic: Claude Pro

Source: [Claude Code legal and compliance](https://code.claude.com/docs/en/legal-and-compliance).

- Subscription (OAuth) authentication is described as intended for plan
  purchasers' ordinary use of Claude Code and Anthropic's own applications.
- Developers building products or services that interact with Claude, explicitly
  including Agent SDK use, are directed to "use API key authentication". Third
  parties may not offer Claude.ai login, route requests through consumer plan
  credentials, or collect, store or intermediate Claude.ai credentials or tokens.
- An end user may sign in to the **unmodified** Claude Code binary with their own
  subscription. The page also notes advertised plan limits assume ordinary,
  individual use of Claude Code and the Agent SDK.

**Assessment.** The Laboratory is a developer-built harness that would drive the
model as its orchestrator under a supervisor. That is closer to "a product or
service that interacts with Claude's capabilities" than to ordinary interactive
use of Claude Code. Driving `claude -p` from the supervisor would also replace
the Laboratory's model-facing conversation with Claude Code's own system prompt,
context management and agent loop. Even with built-in tools disabled and
capabilities exposed through MCP, that is not the same tool-use semantics, so it
could not enter the matched comparison as equivalent. The boundary is at best
ambiguous, and ADR-0016 requires explicit confirmation for ambiguity. **Anthropic
is therefore recorded as unavailable for subscription-backed experiments.** No
credential is read and nothing is bypassed. Two legitimate routes remain:
written confirmation from Anthropic for this exact use (owner action, S014e), or
a separately authorised, budgeted API key (not authorised by the programme
instruction).

## What is never done

No website scraping, browser automation of chat UIs, extracted cookies or session
tokens, unofficial or `backend-api` endpoints, reverse-engineered proxies,
modified vendor binaries, credential extraction from other tools, or silent
model/provider substitution.
