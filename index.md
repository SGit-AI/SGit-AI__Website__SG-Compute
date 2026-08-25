# sg-compute.sgit.ai — ephemeral environments in AWS, one command away

> SG/Compute launches an isolated EC2 environment, runs your work, and terminates it — by
> design, every time. Sixteen ready-to-launch specs — browsers, encrypted vaults, container
> runtimes, LLM inference, observability — each a typed manifest away from a running node,
> with a measured ~16-second boot, a generated CLI, and a self-destruct timer built in.
> Open source, early access, and looking for users and contributors.

*Source: <https://sg-compute.sgit.ai/index.html> · site v0.2.0 · markdown twin of the front page.
Every number measured from the tree on 24 August 2026, at repo version v0.2.71. Code wins:
where the README, `capabilities.json`, the reality document and the tree disagree, the tree
is right.*

---

## Launch, work, terminate

One command gives you a dedicated, isolated environment: a per-node API key is minted and
written to SSM before launch (*never reused*), the instance boots with composed user-data, a
two-phase health poll tells you the moment it is ready, and a self-destruct timer is armed
from the start — **halt means terminate, not stop**. Around 50 seconds end to end, and you
never have to remember to clean up.

```
# every spec gets the same generated CLI — sixteen specs, one surface
sg <spec> list · info · create · wait · health · connect · exec · delete · ami list|bake · cert

# the node terminates itself — default one hour, fractional supported
systemd-run --on-active={seconds}s /sbin/shutdown -h now
InstanceInitiatedShutdownBehavior=terminate   # halt means terminate
```

Adding a spec costs a manifest, a route class and a service — **the CLI comes free**.
[The full lifecycle](what-it-is/index.html).

## Two ephemeral layers, so nothing outlives its purpose

| | Layer 1 — per HTTP request | Layer 2 — per node |
|---|---|---|
| What is ephemeral | A browser | An EC2 instance |
| Mechanism | Fresh Playwright subprocess + fresh Chromium, torn down in `try/finally` | `systemd-run --on-active` + `InstanceInitiatedShutdownBehavior=terminate` |
| Lifetime | One request | One hour by default; `0.1` supported; `0` disables |
| Guarantee | Zero cross-request state — a CI guard fails the build on any raw `browser.new_context(` outside the one sanctioned factory | **Halt means terminate, not stop** |

[Both layers in full, with sessions, the watchdog and the isolation table](what-it-is/index.html).

## Batteries included

- **Sixteen specs, one CLI surface** — per-spec CLIs are generated, not written: the same ten
  verbs for every spec in the catalogue.
- **A deep AWS command surface** — over 71,000 lines of operator tooling: EC2 provisioning,
  IAM and credential management, AMI bake-and-verify, fleet sentinel commands, plus an
  **interactive REPL/TUI** for driving environments live from the terminal.
- **A 25-verb sequence language** — declare a step list, get back COMPLETED / FAILED /
  PARTIAL with every skipped step named and a full timings block. Plus stateful sessions,
  Prometheus metrics, and a self-describing `/health/capabilities` endpoint.
- **Web consoles out of the box** — a capability-driven HTML console on every node, per-spec
  UIs, an agentic admin surface, and live VNC desktops for the headed-browser specs.

## Sixteen ready-to-launch environments

| Family | Specs | Lines |
|---|---|---:|
| browser | playwright, content_proxy, firefox, vnc, neko | 20,199 |
| vault | vault_publish, vault_app | 19,943 |
| observability | elastic, prometheus, opensearch | 3,904 |
| runtime | docker, podman | 2,757 |
| llm | local_claude, ollama | 2,437 |
| network | mitmproxy | 1,448 |
| tool | open_design | 773 |

Nine stable, seven experimental, boot times from 15 seconds. Each spec is a working package —
manifest, routes, service, CLI, tests, often a UI — and the catalogue is open: **third-party
specs can join via a PEP 621 entry point**, no fork required.
[The full catalogue, one page per spec, generated from the data](specs/index.html).

## Three axioms, implemented

Not aspirations — each one is enforced by working code: **statelessness** (fresh browser,
context and page per request, torn down in `try/finally`), **least-privilege-by-declaration**
(the JS allowlist is deny by default, exact match), **self-description**
(`/health/capabilities`, built at runtime by a detector that identifies its own deployment
target).

## Built fast, tested hard, measured honestly

- **4,785 tests passing in 81 seconds** — a large, fast, green suite across 799 files.
- **2,777 commits and 245 tags in 100 days** — 16 Apr to 24 Jul 2026.
- **~16 seconds** measured EC2 boot to SSM-ready, across 24 real runs; **~50 seconds** end to
  end, click to a dedicated environment with its own DNS name.
- **1,265,371 words of documentation**, with a formal reality discipline.
- **25 verbs** in the sequence language; **6 isolation boundaries**, each with a mechanism.

[Every measured number, with its provenance](numbers/index.html). And because measured means
*all of it*, [the full audit is published alongside](shipped/index.html).

## The rough edges are published — and they are the way in

This is an early-access platform, and we publish exactly where it is thin. Well-scoped,
high-value places to start contributing: **warm pools** (specified with worked economics —
the design is done), **S3 and vault artefact sinks** (the interfaces exist; inline and
local-file already work), **uniform `create_node`** (the CLI covers all sixteen specs, the
control-plane API covers three so far — a working pattern to copy), and
[seven fixes in order of value](roadmap/index.html) — the first is literally four characters.

## The argument

> *"We are **not** competing for the generic developer-platform market (Vercel, Cloudflare
> Workers, Lambda)… **We are competing for the agent-deployment market.**"*

A dedicated EC2 instance per workload, with full control, real isolation and a stable DNS
name, where 50 seconds is a fair trade — and the measured 16-second boot beats the design's
own claimed 30–60. [The argument](why/index.html).

## Use it, break it, build on it

**If you need ephemeral environments in AWS** — for browser automation, agent workloads,
container experiments, or LLM inference that cleans up after itself —
[pick a spec](specs/index.html) and read [the machine surface](agents/index.html): the whole
platform is driven over a documented HTTP API and a generated CLI, so an agent can use it as
easily as a person.

**If you want to contribute** — the platform is Apache-2.0, the specs are extensible from
your own repository via entry points, and [the roadmap](roadmap/index.html) names exactly
what is wanted next. Say hello on [the comms page](admin/comms.html) or via
[GitHub](https://github.com/SGit-AI/SGit-AI__Website__SG-Compute).

## One thing to know before you discover it

**`sg-compute.sgit.ai` is this site: documentation.** **`sg-compute.sgraph.ai` is a live Route 53
zone** serving per-node DNS — every node you launch gets a stable DNS name under it. Same
label, different TLD, stated here deliberately. [The decision in full](network/index.html#domains).

## Who is writing this

Published by the sgit project, which builds the platform this site documents. Every number
names what it was measured from, and the audit is published in full alongside the feature
pages. [The participant disclosure, including where our approach loses](about/participant.html).

## Site

- [The source documents](documents/index.html) — twelve, verbatim; two redacted under their own rule
- [The catalogue as JSON](data/specs.json)
- [Comms: tasks & requests](admin/comms.html)
- [Release history](admin/versions.html)
- [How this site is built](admin/index.html)
- [llms.txt](llms.txt) · [llms-full.txt](llms-full.txt)

All content CC BY 4.0. The platform's own source is Apache-2.0.
