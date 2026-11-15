# ADR-0016: Hosted providers through a supervisor-owned broker

Status: Accepted (S014a, 2026-11-15), on the owner's instruction to begin a
hosted-intelligence comparison programme. Amends ADR-0005 (external providers)
and supersedes the planned S007f decision. Nothing in this record is
implemented yet; enabling any provider also needs the per-provider human
approvals below. Provider facts: [HOSTED_PROVIDERS.md](../architecture/HOSTED_PROVIDERS.md).

## Context

S007d-001 (llama3.2:3b) and S007h-001 (qwen3:4b) both returned NO_GO. The owner
now asks whether more capable hosted models behave differently in the
**unchanged** world: same prompts, capabilities, discovery interface, policies,
observation and rubric, with the orchestrating model as the experimental
variable. Hosted models introduce credentials, quotas, network egress, provider
drift and unmatched inference settings. None of these may weaken the existing
authority, observation or isolation boundaries.

## Decision

**1. One gateway shape, one new trusted process.** The agent runtime keeps
talking to the gateway in its existing internal shape (chat completions with the
four meta-tools), so prompts, repairs, context and continuation policies and
recording stay identical across providers. For a hosted provider, the runtime's
loopback base URL points at a **provider broker**: a supervisor-started process
on `127.0.0.1` with a random port and a per-run bearer token issued by the
supervisor. Only the broker translates to the provider's API (Gemini function
calling; Responses API function tools) and back. Translation never invents,
fills or drops tool arguments; every translation choice is versioned and
recorded.

**2. Credentials never enter the experiment.** Keys and OAuth tokens live in a
host-local secret store under the user profile, outside every repository, data
root, archive, workspace, container and runtime environment, encrypted with
Windows DPAPI for the current user. They are entered only through an interactive
`ols provider` command (hidden input or the provider's own browser sign-in) and
are read only by the broker. They never appear in argv, environment variables,
logs, events, model inputs, configuration files or exceptions. The broker's
outgoing request bodies are recorded only after secrets and auth headers are
excluded, and redaction is tested.

**3. Disabled by default; authority from configuration only.** A provider is
usable only when a host-local provider profile marks it enabled **and** carries
human-approved budgets, and the frozen experiment selects it. Prompts, model
output, provider features or SDK defaults cannot grant tools, network, hosted
tools (search, code execution, computer use, MCP), files or permissions.
Provider-native tools are always disabled. The experiment's capability
permissions are unchanged. The runtime gains no new network right beyond
loopback to the broker. Agent tool network rights stay separate and unchanged
(capabilities keep `network: none`). Only the broker has egress, and only to the
provider's documented API hosts.

**4. Budgets reserved before every request.** The broker keeps a crash-safe,
append-only ledger under the data root (outside archives, mirrored per run into
the archive). Before **every HTTP attempt**, retries included, it reserves one
request against all applicable ceilings and syncs the reservation to disk:
per-run requests, per-campaign requests, per-provider daily or billing-period
requests (in the provider's reset time zone), and token or reasoning ceilings
where the provider honours them. A reservation whose outcome is unknown (crash,
timeout after send) counts as spent. Concurrency is one active hosted request.
Retries are bounded (default two attempts), use provider-specific backoff and
honour documented `Retry-After` and quota codes. Quota exhaustion, eligibility
errors and unsupported-parameter errors are terminal: never retried in a loop,
never re-authenticated in a loop. Accounting survives pause, resume and recovery
through the same ledger.

**5. Failure stops; it never substitutes.** A failed request, exhausted quota,
revoked sign-in or unavailable service ends the model step with a recorded
reason. The supervisor then checkpoints or stops under the run's existing
policy. There is no fallback to another model, provider, tier or paid API. A
paid tier is never enabled implicitly.

**6. Provenance and honest settings.** `model.json` records provider, adapter
and translation version, the provider's model id, provider-reported model
version or revision when available, region and endpoint, and every requested
setting with its effective status: *honoured*, *not supported (omitted)* or
*unknown*. Unsupported settings are omitted and registered as differences, never
emulated. Hosted weights have no digest; the archive says so rather than
inventing one. Provider-reported token usage, including reasoning tokens where
reported, is recorded as reported, not as a measure of intelligence.

**7. Data minimisation.** Only the model-facing conversation the runtime already
records is sent: preamble, initial prompt, meta-tool schemas, results and
continuations. No repository, host file, credential or archive content is sent
because a provider has a large context window. Workspace content reaches a
provider only when the agent itself reads it through a capability.

**8. Subscription routes only where officially supported.** No scraping, browser
automation of chat interfaces, extracted cookies or tokens, unofficial endpoints,
reverse-engineered proxies or modified vendor binaries. Where a provider's
permission boundary is ambiguous, implementation waits for the provider's
confirmation.

## Provider conclusions (2026-11-15)

- **Google Gemma (Gemini API, free tier):** eligible. Pin model id, endpoint,
  thinking level and generation settings; read project limits from AI Studio.
- **OpenAI (Sign in with ChatGPT plan usage):** eligible as a preview for locally
  hosted apps; temperature and output cap are unsupported and seed is unknown,
  so the arm runs under registered provider-specific conditions.
- **Anthropic (Claude Pro):** unavailable. Published policy directs developers'
  products, including Agent SDK use, to API keys, and driving Claude Code would
  replace the Laboratory's tool semantics. It re-enters only with Anthropic's
  written confirmation, or with a separately approved paid API budget, and only
  through this same broker and translation contract.

## Alternatives

- **Give the runtime the key and call providers directly.** Simplest, but puts a
  credential inside the agent's process tree and archive reach.
- **A third-party multi-provider library** (for example LiteLLM). Broad coverage,
  but large, with its own retries, fallbacks and defaults that would have to be
  disabled and audited. Small standard-library adapters with versioned
  translations are easier to make provably bounded.
- **Run vendor agent harnesses (Claude Code, Codex) as the agent.** Uses their
  own loops, prompts and tools, so it does not test the same environment
  semantics. At most a separately labelled study.

## Consequences

- The model-provider contract needs fields for external locality, auth kind and
  setting support. That is a minor schema version with a change-log row, done
  in S014b.
- Hosted runs are less reproducible than local ones: providers may change models
  behind an id. Reports state the dates, reported revisions and probe results.
- Provider failure is a valid, recorded run outcome. A quota-limited partial
  campaign is reported as partial.
- Free-tier data may be used by Google outside the EEA/Switzerland/UK. Only
  Laboratory-generated content is sent.
