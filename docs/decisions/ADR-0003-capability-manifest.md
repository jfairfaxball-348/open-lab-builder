# ADR-0003: Transport-neutral capability manifest, discovered through meta-tools

Status: Accepted (S001). Implemented across S002 and S005.

## Context

Agents must find and learn tools without the catalogue being in their prompt.
The world will eventually hold many capabilities of very different kinds:
Python functions, command-line programs, local HTTP services, models. The
orchestrator will be a small local model with a limited context window.

## Decision

1. **One manifest per capability** (`capability.json`), carrying everything an
   unfamiliar agent needs: summary, full description, categories and keywords,
   JSON Schemas for input and output, permissions, resource needs,
   dependencies, runnable demonstrations with expected output, a self-test,
   limitations and failure modes.
2. **Transport-neutral invocation.** The manifest says how the tool host runs
   the capability (`python`, `subprocess`, `http`, `mcp`). In every case the
   call is a JSON object in and a JSON object out.
3. **Discovery through four fixed meta-tools** — `capabilities.search`,
   `.describe`, `.demonstrate`, `.invoke`. These are the only tools presented
   to the orchestrator model directly.
4. **MCP is a projection, not the core.** The manifest's `name`,
   `description` and `input_schema` map directly onto an MCP tool definition
   (and onto OpenAI-style function definitions), so the registry can be served
   over MCP, and third-party MCP servers can be wrapped as capabilities with
   `interface: mcp`.

## Alternatives

- **Adopt MCP as the native format.** MCP defines listing and calling tools,
  but not demonstrations, self-tests, failure modes, resource needs or
  permissions, which this project needs first-class. Listing every tool also
  puts the whole catalogue in context.
- **Put all tool definitions in the prompt.** Simple, but violates
  environment-driven discovery, does not scale past a few dozen tools on a
  small context window, and hides discovery behaviour from observation.
- **Free-form documentation only (README per tool).** Readable but not
  machine-checkable; demonstrations could not be validated or re-run.

## Consequences

- Each real action costs the agent an extra step (search/describe before
  invoke). Accepted: that exploration is itself the behaviour under study.
- Small models may use the meta-tools poorly. S005 must test this with the
  actual orchestrator and may add a short, generic hint to the system prompt
  about the existence of the meta-tools (never the catalogue).
- Demonstrations double as release tests, so documentation cannot go stale.
