# 01 — What it actually is

## 1. Two ephemeral layers — and the site must not conflate them

This is the most common misreading of the platform, and separating the two layers is the clearest thing the site can do on page one.

### Layer 1 — an ephemeral *browser*, per HTTP request

From the source, verbatim:

> *"Layer-3 multi-step execution. **Stateless by design: every call launches a fresh `sync_playwright` + Chromium, runs the declared step list, and tears both down in `try/finally` before returning.**"*

> *"Each call to `launch()` starts a fresh `sync_playwright()` Node subprocess **AND** a fresh Browser, so there is zero"* cross-request state.

`Page__Factory` is the single sanctioned path to a `Page`, and **a CI guard fails the build if any raw `browser.new_context(` appears anywhere else.** That is an architectural rule with a mechanism behind it, which is rarer than it should be.

The request lifecycle: parse steps → reject duplicate ids → validate → launch fresh Chromium → new context and page → apply credentials → iterate steps against a deadline (remaining steps marked `SKIPPED` on halt) → derive `COMPLETED` / `FAILED` / `PARTIAL` → **`try/finally` always tears down** → return with a full timings block.

### Layer 2 — an ephemeral *EC2 node*

`sg_compute/platforms/Platform.py` is the abstraction — `create_node`, `list_nodes`, `get_node`, `delete_node` — with `name: str = '' # 'ec2' | 'k8s' | 'gcp' | 'local'`. **Only `EC2__Platform` exists.**

The lifecycle, end to end:

1. **Request** — `POST /api/nodes`, or `sg <spec> create`
2. **Key mint** — `api_key = secrets.token_urlsafe(32)`, commented *"per-node random key; never reused"*, written to SSM **before launch** so cloud-init can read it
3. **Provision** — `run_instances` with composed user-data sections: `Base`, `Docker`, `Sidecar`, `Nginx`, `Env__File`, `GPU_Verify`, `NVIDIA_Container_Toolkit`, `Ollama`, `VLLM`, `SGit_Venv`, `Claude_Code__Firstboot`, `Shutdown`
4. **Address** — **the EC2 tags are the registry.** `sg:stack-name` and `sg:purpose`; states map `running→READY`, `pending→BOOTING`, `shutting-down|stopping→TERMINATING`
5. **Wait** — `Health__Poller`, two-phase: EC2 reports `running`, then an HTTP probe succeeds
6. **Execute** — pods managed over the host-control sidecar; `Sidecar__Client` sends `{'X-API-Key': self.api_key}`
7. **Teardown** — three independent paths

**Teardown is the part worth publishing**, because it is a real design decision:

```bash
systemd-run --on-active={seconds}s /sbin/shutdown -h now
```

paired with `InstanceInitiatedShutdownBehavior=terminate`. **Halt means terminate, not stop.** Default `max_hours = 1` across every spec; `vault_app` supports fractional (`0.1` = 6 minutes); `max_hours=0` disables. Plus explicit `delete`, plus `SG_Edge__Fleet__Reconciler` with `IDLE_TEARDOWN_THRESHOLD = 3` — three consecutive zero-vault idle checks at a 5-minute cadence, so roughly 15 minutes.

On spot instances the flag is deliberately skipped, with the reasoning in the source: *"spot non-hibernation instances always terminate on OS shutdown; skip the flag (it's silently ignored)."*

---

## 2. Sessions — the exception to statelessness, and why

Held sessions get **one dedicated OS thread each**, owning the Playwright runtime, browser and page for the session's whole life. The rationale is a real bug, documented verbatim:

> *"Playwright's sync API is greenlet-based… Calling `page.goto` / `page.locator(...)` from a **DIFFERENT** thread leads to undefined behaviour (deadlocks, silent hangs, or 'navigate failed' with no `error_message` — **the exact symptom `session_act` was hitting in CI**)."*

TTLs: `/session/open` defaults to **300,000 ms (5 minutes)**; `/desktop/browser` to **3,600,000 ms (1 hour)**; both capped at `capabilities.max_session_lifetime_ms`. **Every access refreshes the full TTL.**

Expiry is swept **lazily**, at the start of every registry operation and from `Playwright__Service.setup()` — so any request to any endpoint sweeps idle sessions, and **there is no background thread.** Teardown runs on the worker thread, for Playwright affinity. Idle cost, from the source: *"the worker blocks on `queue.get()` — **0% CPU, ~few KB of RAM.**"*

That is a genuinely elegant design and it is undocumented publicly.

---

## 3. The watchdog — publish this, it is the best engineering story in the repo

`Request__Watchdog` runs a daemon thread. If any in-flight request exceeds `max_request_ms`, it calls `os._exit(2)`.

The source explains why, and the reasoning is the interesting part: **`time.sleep` releases the GIL, so the watchdog keeps ticking even through a main-thread deadlock**, and **`os._exit` bypasses cleanup, `finally` blocks and GIL contention** — which a graceful shutdown could not do from inside a deadlock. The Lambda Web Adapter sees the process die, and AWS hands the next invocation a fresh container.

It was written against a real production deadlock. **A platform site that publishes the failure and the mechanism reads very differently from one that publishes a feature list.**

---

## 4. The API surface — two apps, and one correction to the received wisdom

### App 1 — the Playwright data plane

Image `diniscruz/sg-playwright`. **All routes require `X-API-Key`** via `Middleware__Check_API_Key`.

`GET /` (a capability-driven HTML console) · `/health/info` `/health/status` `/health/capabilities` · `POST /browser/navigate|click|fill|get-content|get-url` · `POST /browser/screenshot` (**raw PNG bytes**, timings in `X-*-Ms` headers) · `POST /sequence/execute` (the **25-verb declarative step language**) · `POST /screenshot` `/screenshot/batch` `/inspect` · `POST /session/open`, `/session/{id}/act|probe|close` · `POST /desktop/browser` (headed on an X display; **VNC image only — 400s on headless**) · `GET /metrics` (Prometheus) · `/test-pages/{name}` · and an agentic admin surface at `/admin/health|info|env|boot-log|error|manifest|capabilities|skills/{name}`.

### App 2 — the SG/Compute control plane

`GET /api/health`, `/api/health/ready`, `/catalog/caller-ip` — **auth-free**. Then `/api/specs`, `/api/nodes` CRUD, `/{node}/pods|stats|logs|stop` via the sidecar, `/api/stacks`, `/api/amis`, **per-spec routes auto-discovered by convention**, and `/legacy/*` carrying `X-Deprecated` on every response. Plus host-plane routes (`Auth`, `Containers`, `Docs`, `Images`, `Logs`, `Pods`, `Shell`, `Status`), `Routes__TLS`, `Routes__Vault__Spec`, and two Lambdas (`/__edge__/*`, `/__waker__/*`).

### ⚠️ The auth model — the guidance is right, the mechanism is not what people think

The received wisdom is *"`x-sgraph-access-token` for `/pw/...`, `X-API-Key` for direct stack access."* **That guidance is correct and should be kept.** The mechanism behind it is not what it implies.

**`x-sgraph-access-token` appears zero times in this repo's Python except as a header to discard.** The service only ever validates `X-API-Key`. The translation happens in the vault's reverse proxy:

```python
ENV_VAR__TOKEN    = 'SGRAPH_SEND__ACCESS_TOKEN'          # injected upstream as X-API-Key
UPSTREAM_API_KEY  = 'X-API-Key'
STRIP_REQUEST     = {'host', 'content-length', 'x-sgraph-access-token', 'cookie'}
...
headers[UPSTREAM_API_KEY] = token                        # vault auth → upstream auth
```

So **`x-sgraph-access-token` is the *vault's* auth header, not sg-playwright's.** The proxy strips it and injects `X-API-Key` from `SGRAPH_SEND__ACCESS_TOKEN`.

**One sub-claim in the existing skill documentation is wrong** and should be corrected on the site: *"A caller sending `X-API-Key` to the proxy gets 401 at the proxy."* It does not — `X-API-Key` is **not** in `STRIP_REQUEST`, and the proxy overwrites it unconditionally. The 401 comes from the vault app's own middleware sitting in front of the proxy.

**And a fact the site must state:** the `/pw` proxy is **in neither repo**. `Fast_API__Reverse_Proxy` is written to be *vendored into* the `diniscruz/sg-send-vault` image — *"kept single-file and dependency-light… so it can be vendored into a container we do not build."* Grepping `__Send` for `/pw`, `REVERSE_PROXY__ROUTES` or `sg-playwright` in code returns **zero hits**. **Anyone documenting the production auth path is documenting a component they cannot see.**

---

## 5. Isolation boundaries

| Boundary | Mechanism |
|---|---|
| Job ↔ job, same node | Fresh Playwright subprocess + fresh Browser + fresh BrowserContext per request, `try/finally` teardown |
| Session ↔ session | Dedicated OS thread, own browser process, registry keyed by `Session_Id` |
| Node ↔ node | Separate EC2 instances, per-node security group, **per-node API key, never reused** |
| Untrusted JS | `JS__Expression__Allowlist` — **deny by default, exact match.** `evaluate` is rejected until an operator populates the allowlist. The `allow_all` bypass is set only by the screenshot surface, on the stated ground that *"each call is an isolated session"* |
| Network | Browser traffic through the mitmproxy sidecar; *"isolation is Docker network"*; sidecar `:8080` unreachable from outside the EC2 |
| Cookies | `SET_COOKIE` applies to the per-request context — *"stateless — the context is fresh per request and discarded after; no session persistence"* |

**One weakness to disclose rather than hide.** `EC2__Platform.create_node` writes the per-node API key into an **EC2 tag**:

```python
if node_info.instance_id:                          # tag so dashboard can read key without SSM
    EC2__Launch__Helper().add_tags(region, str(node_info.instance_id),
                                   [{'Key': 'sg-compute:host-api-key', 'Value': api_key}])
```

The codebase already knows: `Schema__Playwright__Info.py:22` reads *"**Visible to anyone with `ec2:DescribeInstances`.**"*

The key is *also* in SSM, which is the correct store — the tag is a dashboard convenience with a stated cost. **No live key is exposed in the repo; this is a design trade-off, not a leak.** `07__` §4 has the recommended framing, which is to publish it as a known trade-off with the mitigation named. Hiding it would be worse than the trade-off itself.

---

## 6. How artefacts come back — correct the likely assumption

`Enum__Artefact__Sink` declares `VAULT`, `INLINE`, `LOCAL_FILE`, `S3`. The default is `INLINE`.

**Only `INLINE` and `LOCAL_FILE` are implemented.** Both `write_bytes_to_vault` and `write_bytes_to_s3` raise `NotImplementedError`.

So today: **base64 in the JSON body** (20 MB cap — a source comment notes that `Safe_Str__Text__Dangerous`'s 64 KB default was rejecting real screenshot PNGs), **raw PNG bytes** for `POST /browser/screenshot`, or a local file path in development.

**No S3. No presigned URLs. No vault writes.** The site must not claim otherwise — and the gap is worth naming, because vault writes are the obvious integration with the rest of the estate.

---

This document is released under the Creative Commons Attribution 4.0 International licence (CC BY 4.0).

---

*Published on sg-compute.sgit.ai under CC BY 4.0. Source: the `sg-compute.sgit.ai` brief pack v0.33.62, 24 August 2026, by Dinis Cruz via the SG/Send Librarian, with AI co-authorship (Claude, Anthropic).*
