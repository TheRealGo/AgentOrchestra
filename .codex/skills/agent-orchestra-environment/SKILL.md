---
name: agent-orchestra-environment
description: Use when an AgentOrchestra Agent must prepare an ephemeral project environment, install dependencies, start or inspect dev servers, run Docker compose, produce UI/E2E evidence, or clean per-agent environment artifacts without polluting the target repository.
---

# agent-orchestra Environment Skill

Use this Skill before environment setup, dependency installation, dev-server
work, Docker compose, browser/UI verification, or cleanup inside an
agent-orchestra run.

## Directories

Use the launch-provided directories:

- `AGENT_ORCHESTRA_CACHE_DIR` for package caches and downloaded dependencies.
- `AGENT_ORCHESTRA_ARTIFACT_DIR` for logs, screenshots, traces, reports, and
  other verification evidence.
- `AGENT_ORCHESTRA_ENV_DIR` for disposable virtualenvs, build sandboxes,
  database files, compose env files, and generated runtime-only config.
- `AGENT_ORCHESTRA_SERVER_MANIFEST` for long-running dev-server metadata such
  as process id, process group id, base URL, port, and log path.

Keep tracked repository files reserved for product changes. Do not add
Dockerfiles, compose files, lockfiles, env files, or wrapper scripts only to
make validation convenient. If a tracked environment file is required by the
actual user request, tie it to an `[Acceptance]` requirement and record
verification evidence.

Cleanup must be scoped to disposable resources this run created. Do not remove
arbitrary untracked repository files, symlinks, directories, supervisor status
files, or `result`/`result-*` Nix symlinks just because they appear in
`git status`. Do not delete `AGENT_ORCHESTRA_RUN_DIR` itself, shared task files,
Agent `state.json`, launch material, command/config JSON, artifacts, logs, or
evidence while the run is active. Clean only specific runtime resources such as
manifest-recorded processes, current-run stop files after their process is gone,
cache/env scratch directories known to be disposable, and compose resources with
this run's `COMPOSE_PROJECT_NAME`. Treat unknown local artifacts as evidence or
candidates, not cleanup targets.

## Setup Order

Prefer repository-native setup, then fallback conservatively:

1. `flake.nix` or project-provided Nix commands.
2. Docker compose files already present in the repo.
3. Package-manager lockfiles such as `package-lock.json`, `pnpm-lock.yaml`,
   `yarn.lock`, `uv.lock`, `poetry.lock`, `Pipfile.lock`, `Cargo.lock`, or
   language-specific project files.
4. Framework/language defaults after inspecting README, scripts, and manifests.

Use local caches when the tool supports it. Examples include npm/pnpm/yarn cache
paths under `AGENT_ORCHESTRA_CACHE_DIR`, Python virtualenvs under
`AGENT_ORCHESTRA_ENV_DIR`, and test/browser traces under
`AGENT_ORCHESTRA_ARTIFACT_DIR`.

## Completion Bias And Alternative Routes

Environment failure is a problem to route around, not a reason to stop after the
first attempt. When a tool, dependency, MCP server, browser install, dev server,
database, container runtime, credential, or network-backed setup path is missing
or broken, try to complete the requirement through an alternate concrete route before
escalating:

- repository-native setup or scripts;
- existing Docker compose files, with runtime-only env files under
  `AGENT_ORCHESTRA_ENV_DIR`;
- ephemeral virtualenvs, package caches, temporary databases, or service state
  under the launch-provided directories;
- Playwright CLI, Browser tooling, direct screenshots, curl/API probes, logs, or
  another alternate evidence-producing tool when an MCP server is unavailable;
- an equivalent reproducible harness or smaller check that still verifies the
  acceptance requirement.

Keep `[status] progress` while any autonomous completion route remains. Use
`needs_user` or `blocked` only when the remaining requirement truly depends on
external input. In that case, record the attempted routes, artifact paths, and
the exact missing credential, approval, network access, service, hardware, or
scope change needed from the user.

Long-running setup and verification commands must be bounded. For Nix builds,
Docker pulls, dependency installs, browser installs, or network-backed fetches,
run one heavy command at a time unless parallelism is required, wrap it with a
timeout, and write stdout/stderr to `AGENT_ORCHESTRA_ARTIFACT_DIR`. A silent or
stalled command is a gate result, not a reason to wait forever; record it in
`[Gates]` or `[Candidates]` with evidence. If another equivalent
repository-standard check already covers the same contract, record the stalled
or skipped command with evidence and continue the finalization decision without
waiting indefinitely.
Browser evidence routes need an outer wall-clock timeout around the entire
install/launch/screenshot/action path. Page-level Playwright timeouts do not
cover hangs in browser download, process launch, MCP approval, or macOS
sandbox startup. Use an available wrapper such as `timeout`, `gtimeout`, or a
`subprocess.run(..., timeout=...)` harness, save stdout/stderr to
`AGENT_ORCHESTRA_ARTIFACT_DIR`, and stop after the first outer-timeout failure
on a route. Then record the timeout in `[Candidates]` or `[Gates]` and switch
to another evidence path or leave the gate failed/blocked; do not start another
unbounded browser run.
Do not assume GNU `timeout`, `pgrep`, or unrestricted process listing exists on
macOS. If `timeout`/`gtimeout` is missing, use a short Python wrapper around
`subprocess.run(..., timeout=seconds)` and write both stdout and stderr to files
under `AGENT_ORCHESTRA_ARTIFACT_DIR`. For cleanup and liveness, prefer the
recorded PID/PGID/stop-file in `AGENT_ORCHESTRA_SERVER_MANIFEST` over `pgrep`;
if OS permissions prevent direct signaling, record the failure and use the
approved external cleanup path for that exact current-run PID.
For Playwright CLI fallback, prefer installing or invoking it from a local
environment under `AGENT_ORCHESTRA_ENV_DIR` with cache under
`AGENT_ORCHESTRA_CACHE_DIR`, then run scripts from that environment with the
outer timeout and artifact logging. Do not assume `npx -p playwright node -e`
exposes the package to arbitrary inline Node scripts. If a script imports
`@playwright/test`, install `@playwright/test` in that same ephemeral
environment first. Otherwise use a plain Playwright script that imports
`playwright` and performs its own assertions, screenshot, console, and network
logging. If Playwright reports `No tests found` or `Cannot find module
'@playwright/test'`, treat that as a harness defect, fix the harness once under
`AGENT_ORCHESTRA_ENV_DIR`, and rerun with the corrected command before deciding
the visual gate.
Install Playwright browsers with the same `HOME` and cache environment that the
later Node/Playwright process will use. In isolated Agent sessions this usually
means exporting `HOME` to the launch-provided agent home and setting
`PLAYWRIGHT_BROWSERS_PATH` or the relevant cache path under
`AGENT_ORCHESTRA_CACHE_DIR` before both `playwright install` and the browser
launch. A browser installed into the shell user's normal cache is not valid
evidence that the isolated Agent's Playwright route is ready.
When using a persistent Node REPL or similar tool for Playwright retries, avoid
top-level `const`/`let` redeclarations across retries. Use unique names, `var`,
or reset the REPL before rerunning. A REPL binding collision is harness
evidence and should be recorded once, then routed around rather than retried
indefinitely.

Fake LLM/API servers and deterministic test harnesses are acceptable only as
ephemeral verification aids. Before using one as E2E evidence, probe the target
application's action schema or API contract and validate that fake responses use
accepted action names and argument shapes. If the first harness run fails
because the fake emitted an invalid action, record that as an E2E candidate,
fix the harness under `AGENT_ORCHESTRA_ENV_DIR`, and rerun; do not count the
failed probe as product evidence.

## Docker Compose

When using compose, set:

```sh
COMPOSE_PROJECT_NAME=agent-orchestra-${AGENT_ORCHESTRA_RUN_ID:-run}-${AGENT_ORCHESTRA_AGENT_ID}
```

If `AGENT_ORCHESTRA_RUN_ID` is unavailable, derive a short stable value from
`AGENT_ORCHESTRA_RUN_DIR`. Before reporting completion, stop and remove compose
resources that are no longer needed, and store logs or inspection output in
`AGENT_ORCHESTRA_ARTIFACT_DIR` if they are evidence.

## Dev Servers And Runtime Processes

Start dev servers through the runtime supervisor when possible so the run keeps
a durable process record even if the terminal stdin closes:

```sh
"$AGENT_ORCHESTRA_PYTHON" -m agent_orchestra_minimal.server_process start \
  --manifest "$AGENT_ORCHESTRA_SERVER_MANIFEST" \
  --name web \
  --cwd "$AGENT_ORCHESTRA_TARGET_PROJECT" \
  --base-url "http://127.0.0.1:3000" \
  --port 3000 \
  --health-url "http://127.0.0.1:3000/" \
  --startup-timeout 10 \
  --log "$AGENT_ORCHESTRA_ARTIFACT_DIR/web-server.log" \
  -- npm run dev -- --host 127.0.0.1 --port 3000
```

`server_process start` returns success only after the supervised process is
still alive and, when `--port` is provided, `127.0.0.1:PORT` accepts TCP
connections before `--startup-timeout`. When a server exposes an HTTP endpoint,
also pass `--health-url` and, when possible, `--health-contains` with a product
or harness-specific marker so a stale localhost listener from an earlier run
cannot satisfy the readiness gate. Use `--allow-tcp-readiness` only for
non-HTTP helpers or when an equivalent identity check is recorded separately in
the gate evidence; never use it for a web/API server just to bypass a missing
health check. If startup fails or times out, the
manifest entry is `startup-failed` or `startup-timeout` with `log_tail`; do not
use that `base_url` for screenshots, API probes, or passed gate evidence.
Choose another port/route or leave the gate failed/blocked with the manifest
evidence.
The supervisor exports `AGENT_ORCHESTRA_SERVER_NAME`,
`AGENT_ORCHESTRA_SERVER_BASE_URL`, and, when `--port` is present,
`AGENT_ORCHESTRA_SERVER_PORT` to the supervised child. Runtime-only helper
servers such as fake LLM/API harnesses should bind from that port environment
instead of hardcoding a localhost port. If a helper ignores the assigned port
and startup times out, fix the helper under `AGENT_ORCHESTRA_ARTIFACT_DIR` or
`AGENT_ORCHESTRA_ENV_DIR`, restart it through `server_process`, and record the
failed attempt as harness evidence rather than product evidence.

Record the same `base_url`, `port`, `pid`, `pgid`, `status`, and `log_path`
from the manifest in `[Gates]` evidence. Visual and API probes must use this
recorded `base_url`; do not fall back to a stale localhost port from an earlier
run or a different evidence file. Before completion, stop the recorded process
with:

```sh
"$AGENT_ORCHESTRA_PYTHON" -m agent_orchestra_minimal.server_process stop \
  --manifest "$AGENT_ORCHESTRA_SERVER_MANIFEST" \
  --name web
```

The runtime start command launches a small same-run supervisor and records a
private `stop_file` in the manifest. The stop command first writes that
`stop_file` so the original supervisor can terminate its own child process even
when a later sandboxed Agent process cannot signal a sibling. If the supervised
stop does not complete, it then targets the recorded process group and falls
back to the direct PID when process-group termination is denied by the sandbox.
If all paths fail, leave the environment gate failed or blocked, record the
exact manifest entry and remaining listeners, and request or perform an
approved external cleanup path; do not convert supervisor-assisted cleanup into
autonomous success evidence.

If the supervisor cannot be used, create an equivalent manifest under
`AGENT_ORCHESTRA_ENV_DIR` before starting the process, include a cleanup command
and process-group/PID evidence, and record cleanup success or failure in
`[Gates]` or `[Candidates]`.

This applies to every long-running helper, not only the primary web server.
Fake LLM/API servers, local databases, queues, file watchers, worker processes,
secondary web servers, browser bridges, and test harness listeners must be
started through `server_process` or recorded in an equivalent manifest with
PID/PGID, port/base_url, log path, owner Agent, and cleanup command before
they are used. Before completion, verify that every manifest entry is stopped
and that no current-run listener remains. An unmanifested current-run listener
is a cleanup gate failure, even if the main product server was stopped.
For ordinary cleanup, stop all recorded helpers in a manifest with:

```sh
"$AGENT_ORCHESTRA_PYTHON" -m agent_orchestra_minimal.server_process stop-all \
  --manifest "$AGENT_ORCHESTRA_SERVER_MANIFEST"
```

If a localhost port is already occupied before startup, do not silently reuse
or trust it. Record the startup failure, choose a fresh port, and before final
completion inspect remaining listeners for the ports you attempted. A listener
from a deleted or previous run is an orphan-process candidate; clean it through
the old manifest when available, or record the exact PID/PGID and request or
perform an approved external cleanup route.
Use `agent-orchestra doctor --server-processes` to scan durable
`server_process` manifests under the configured AgentOrchestra run root when a
run reports cleanup success but ports, PIDs, or helper processes still appear live.
The doctor route is diagnostic: it reports live manifest-recorded helpers and
does not kill them. Stop confirmed current-run helpers through
`server_process stop-all --manifest ...`; treat older or ambiguous helpers as
cleanup candidates with evidence before acting.

## UI And E2E Gates

When the run includes UI requirements or UI changes, start the required dev
server and capture evidence before marking gates passed:

- Use the viewport, device class, or environment required by the user, Spec,
  UI/design docs, or target platform.
- If no viewport or device class is specified, derive the primary verification
  environment from the product's documented or implemented use case and record
  that rationale in `[Gates]`.
- Use desktop, mobile, responsive, small-screen, or other platform coverage
  only when it is explicitly in scope. Do not turn out-of-scope platform
  coverage into an implementation target or completion gate; record it as a
  deferred candidate when it is worth mentioning.
- Record URL, viewport, screenshot path, console/network errors, and the Agent
  that performed verification in `[Gates]`.
- Record requested viewports and measured viewports separately. A passed gate
  must include matching `viewport=` and `viewport_actual=` evidence captured
  from `innerWidth`/`innerHeight` or screenshot metadata, not just the resize
  command that was attempted.
- Save or copy screenshots, DOM/accessibility snapshots, console/network notes,
  and assertion JSON into `AGENT_ORCHESTRA_ARTIFACT_DIR`; record `artifact_dir=`
  in `[Gates]` so workspace-local MCP output is not lost or confused with
  final evidence.
- Include the recorded server manifest path, `base_url`, and semantic
  assertions for required UI states such as required objects, active/breathing
  indicators, completed/found indicators, artifact links, disabled controls,
  or other Spec/UI-mandated elements.
- Include `fit=` evidence for no overlap, no clipping, no unintended horizontal
  scroll, readable density, and operable primary actions at each required
  viewport.

If Playwright MCP is available, use it. If it is not available, try Playwright
CLI, Browser tooling, screenshots, or another concrete UI-inspection path. Do
not mark visual/E2E gates passed from code inspection alone.
All browser install, browser launch, screenshot, Playwright script, and
Browser/MCP visual actions must use a strict outer wall-clock timeout for the
whole route. If one route hangs or times out, stop it, preserve logs, record a
candidate, and switch routes or leave the gate failed/blocked instead of
retrying unbounded.
If a browser, GUI, screenshot, or Quick Look command fails with a sandbox or
permission signature such as `MachPortRendezvous`, `Operation not permitted`,
`SIGABRT`, or sandbox initialization failure, retry the same necessary visual
evidence route once with `sandbox_permissions="require_escalated"` and a narrow
justification before declaring the gate blocked. Record the approval result,
command route, and any remaining error in `[Gates]`.
Do not treat the first `MachPortRendezvous` or equivalent permission failure as
the final visual outcome. If approval is unavailable, denied, or the escalated
retry still fails, immediately switch to another concrete evidence route such as
Browser tooling, DOM/API probes plus screenshots, Chrome/Playwright through a
different launch surface, or a smaller visual harness, and keep the gate
unresolved until one route produces evidence.
If an MCP route opens an interactive approval prompt, make one bounded approval
attempt through the owning pane. If the prompt does not complete, cancel or back
out, stop all manifest-registered helpers, and record the exact prompt/tool
route as blocked evidence. A pending MCP approval prompt is not a reason to
leave dev servers or fake APIs running.
If the same MCP server asks for repeated approval prompts during one visual or
E2E gate, or a tool call remains in `Working` without a fresh result past the
gate's timeout, stop using that MCP route for the gate. Then switch to Playwright
CLI, Browser tooling, DOM/API probes, screenshots, or another evidence path;
record the repeated prompts or timeout in `[Candidates]` and keep the gate
unresolved until alternate evidence exists.

Gate failures include requested/measured viewport mismatch, screenshots or
snapshots left outside `AGENT_ORCHESTRA_ARTIFACT_DIR`, overlap, clipping,
unintended horizontal scroll, unreadable density, primary actions that cannot be
operated, missing required objects, missing semantic assertions for required
visual states, dev server startup failure, stale or mismatched `base_url`,
failed process cleanup, or unverified console/network failures.

## Completion

Before `ready_for_review` or final completion, ensure environment evidence is
linked from `[Acceptance]` or `[Gates]`. Leave gates `failed`, `blocked`, or
`needs_user` instead of `passed` when the environment, tools, or UI could not be
verified, and keep `[status] progress` while those gate states remain.
