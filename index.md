# sg-compute.sgit.ai — an ephemeral compute platform, named after one of its sixteen specs

> SG/Compute launches an isolated environment, runs the work, and terminates it. Sixteen
> ready-to-launch specs — browsers, vaults, container runtimes, model inference,
> observability — each a typed manifest away from a running node. The repository is still
> named after one of them, and the number that settles it is this: **71.5% of the new
> codebase is not browser code**.

*Source: <https://sg-compute.sgit.ai/index.html> · site v0.1.1 · markdown twin of the front page.
Every number measured from the tree on 24 August 2026, at repo version v0.2.71. Code wins:
where the README, `capabilities.json`, the reality document and the tree disagree, the tree
is right.*

---

## Start with a bug we found in its CI

A guard exists to stop the new tree importing from the legacy package it is being extracted
from. Its regex is `sgraph_ai_service_playwright[^_]` — and `[^_]` requires a **non-underscore**
after the stem, while the real package is `sgraph_ai_service_playwright__cli`, with **two**.

```
GUARD regex   : 0 files    -> test PASSES (vacuously)
REAL imports  : 69 files, 228 import lines
FIXED regex   : 69 files   -> test FAILS, as intended
```

**Deleting four characters turns it red.** And the dependency runs both ways — the legacy
package imports the new one 72 times — so the cycle the guard's own docstring says was broken
is not broken. [The guard in full](rename/index.html#guard).

## Two ephemeral layers, and conflating them is the common misreading

| | Layer 1 — per HTTP request | Layer 2 — per node |
|---|---|---|
| What is ephemeral | A browser | An EC2 instance |
| Mechanism | Fresh Playwright subprocess + fresh Chromium, torn down in `try/finally` | `systemd-run --on-active` + `InstanceInitiatedShutdownBehavior=terminate` |
| Lifetime | One request | One hour by default; `0.1` supported; `0` disables |
| Guarantee | Zero cross-request state — a CI guard fails the build on any raw `browser.new_context(` outside the one sanctioned factory | **Halt means terminate, not stop** |

[Both layers in full, with sessions, the watchdog and the isolation table](what-it-is/index.html).

## Three axioms, rescued from a file 42 versions stale

They are named in `capabilities.json`, frozen at v0.1.29 against code at v0.2.71 — a file the
platform's own documentation says not to read. The axioms are good and, unlike the file,
implemented: **statelessness**, **least-privilege-by-declaration** (the JS allowlist is deny by
default, exact match), **self-description** (`/health/capabilities`, built at runtime).

## The catalogue is the argument

| Family | Specs | Lines |
|---|---|---:|
| browser | playwright, content_proxy, firefox, vnc, neko | 20,199 |
| vault | vault_publish, vault_app | 19,943 |
| observability | elastic, prometheus, opensearch | 3,904 |
| runtime | docker, podman | 2,757 |
| llm | local_claude, ollama | 2,437 |
| network | mitmproxy | 1,448 |
| tool | open_design | 773 |

**Vault specs are within 300 lines of browser specs.** Playwright is 1 of 16 registered specs
and 16.8% of spec code. [The full catalogue, one page per spec, generated from the data](specs/index.html).

## What "very mature" measures out at

- **4,785 tests passing in 81 seconds** — a large, fast, green suite across 799 files.
- **2,777 commits and 245 tags in 100 days** — 16 Apr to 24 Jul 2026. Claude 1,700 / Dinis 826 / Actions 243.
- **1,265,371 words of markdown**, with a formal reality discipline whose governing rule is *"if the reality document doesn't list it, it does not exist."*
- **~16 seconds** measured EC2 boot to SSM-ready, across 24 real runs.

And, in the same breath:

- **No static analysis of any kind** — no mypy, ruff, flake8, black, tox.
- **CI runs 67.4% of collectible tests**; the 2,317 outside it hide **six real import-level breakages**.
- **No infrastructure-as-code.**
- **Four sources of truth disagree with the code**, including a README that says *"Phase 0 in progress — repo skeleton"* at 217,266 lines.
- **No commit since 24 July 2026.**

[Every measured number, with its provenance](numbers/index.html).

## And what is not built

No warm pools. No multi-node stacks. `create_node` for 3 of 16 specs. Artefact sinks 2 of 4 —
no S3, no presigned URLs, no vault writes. One platform of four. No cost model. No throughput
measurement. And the AMI bake pipeline invokes a binary called `sg-play` sixteen times that is
defined nowhere, so it is dead. [The unsoftened ledger](shipped/index.html).

## The rename

Nine acceptance criteria from the 30 April naming brief, scored against the tree: **3 done,
2 partial, 4 not done, plus one deliberate improvement over spec**. Architecturally done,
textually about 40% done. [The scorecard, the breakage list, and the sequencing that does not
orphan live nodes](rename/index.html).

## The argument

> *"We are **not** competing for the generic developer-platform market (Vercel, Cloudflare
> Workers, Lambda)… **We are competing for the agent-deployment market.**"*

The definitional move that lets an EC2 instance with a one-hour self-terminate count as
serverless, the trade stated honestly, and the cold-start ladder measured against its own
benchmark — where the measured 16 seconds beats the ladder's claimed 30–60.
[The argument](why/index.html).

## One thing to state before you discover it

**`sg-compute.sgit.ai` is this site: documentation.** **`sg-compute.sgraph.ai` is a live Route 53
zone** serving per-node DNS, referenced 128 times in the platform's code and tests. Same label,
different TLD. The decision is to claim the distinction rather than move 128 references, and to
say so here. [The decision, and where it could still bite](network/index.html#domains).

## Published unresolved

Eight questions with no answers, seven tensions not smoothed over, and a seven-item fix list
where the first item is four characters. [Build order, open questions and tensions](roadmap/index.html).

## Who is writing this

Published by the sgit project, which builds the platform this site audits. The repository is
public, the audit is published in full as raw source documents, and every number names what it
was measured from. [The participant disclosure, including where our approach loses](about/participant.html).

## Site

- [The source documents](documents/index.html) — twelve, verbatim; two redacted under their own rule
- [The catalogue as JSON](data/specs.json)
- [Comms: tasks & requests](admin/comms.html)
- [Release history](admin/versions.html)
- [How this site is built](admin/index.html)
- [llms.txt](llms.txt) · [llms-full.txt](llms-full.txt)

All content CC BY 4.0. The platform's own source is Apache-2.0.
