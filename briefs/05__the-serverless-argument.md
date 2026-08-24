# 05 — The argument: a serverless environment for agents

The strategy is well developed — **23 briefs, 52,873 words measured**, mostly between 30 April and 16 May 2026. This is the `/why/` section, and it is the strongest writing in the corpus.

---

## 1. The positioning, in its own words

> *"**A serverless environment for agents, with the isolation, observability, and substrate control that agent workloads actually need.**"*

And the market it is explicitly *not* in:

> *"We are **not** competing for the generic developer-platform market (Vercel, Cloudflare Workers, Lambda)… **We are competing for the agent-deployment market.**"*

That is a sharper position than most infrastructure projects manage, and it is defensible because the workload genuinely differs — agent runs are seconds-to-minutes, need a real filesystem and a real browser, and care more about isolation and substrate control than about millisecond cold starts.

The definition the whole argument rests on:

> *"**Serverless = no servers running when there is no traffic, with a defined cost to start serving traffic and ongoing per-invocation cost while traffic is served.**"*

Note what it does *not* say: nothing about functions, nothing about managed runtimes. That definitional move is what lets an EC2 instance with a one-hour self-terminate count as serverless, and the site should make the move explicitly rather than assuming it.

---

## 2. The trade, stated honestly

> *"The trade-off Lambda makes is 'less control, smaller startup tax, fully managed.' Our composition makes a different trade: **more control, slightly longer first-call cold-start, broader workload range, and per-substrate optimisation.**"*

> *"**Lambda's 100ms cold-start is impressive but irrelevant for most agentic workloads** (which run for seconds or minutes anyway)."*

> *"**Containers do not have this problem.** A single container can serve hundreds of parallel requests trivially. The cold-start is paid **once per container, not once per request**." … "**the workhorse substrate is a container, not a function.**"*

**⚠️ The "hundreds of parallel requests" claim is argued and never measured.** There are no load tests anywhere in the repo. Either measure it before publishing or state it as a design expectation. `08__` Q2.

---

## 3. The cold-start ladder

The corpus's most useful single table:

| Substrate | Cold start | Status |
|---|---|---|
| EC2 cold | 30–60 s | ✅ implemented |
| **EC2 from warm pool** | **5–15 s** | ❌ **not implemented** |
| Fargate cold | 10–30 s | partial (experiment) |
| Container on a running EC2 | 1–5 s | ✅ implemented |
| Cached-image restart | 100–500 ms | — |
| Firecracker snapshot restore | < 50 ms | future |

**And the measured reality beats the ladder's own top rung.** From `utils/ec2_boot_bench/` — 24 real runs, eu-west-2, 11 May 2026, time to SSM-ready:

| Instance | Purchase | Seconds |
|---|---|---|
| t3.micro | on-demand | **16.4–16.5** |
| c5.large | on-demand | **16.2–16.3** |
| g5.xlarge | on-demand | **18.2–18.7** |
| g5.xlarge | spot | **20.5–20.6** |
| g5.xlarge (different AMI) | on-demand | **38.5–69.5** |

Two things there are worth publishing. **The measured EC2 cold start is ~16 seconds, not 30–60** — the ladder is pessimistic against its own benchmark. And **AMI choice changes boot time by 2–4×**, which is a more actionable finding than the instance type.

Plus **7 recorded `InsufficientInstanceCapacity` failures** for g5.xlarge across both AZs. **Publish those.** Honest evidence that spot GPU capacity is not guaranteed is worth more than a clean table, and it is exactly the kind of number nobody else publishes.

> ⚠️ **Strip the instance IDs and AMI IDs before publishing.** See `07__` §2.

---

## 4. The 50-second number, and what it is for

> *"**The 50-second end-to-end provisioning is the number that matters most.** It is not as fast as Lambda (sub-second cold start), not as fast as Fargate (10–30s), but it gives a dedicated EC2 instance per-vault with full control, isolation, and a stable DNS name."*

> *"…the 'click and you have a dedicated environment' pattern (**where 50s is a fair trade for the isolation**)."*

That is the product claim in one sentence, and it is honest about what it is trading. Note the gap between the 16-second boot benchmark and the 50-second end-to-end figure: **the difference is provisioning, DNS and health-checking, not instance start.** Publishing that breakdown would be more useful than either number alone.

---

## 5. The recursion — the best unbuilt idea

> *"**We do not need a serverless 'control plane' running 24/7.** The control plane is one specific role that can spin up itself on demand, do its work, and shut down. **The DNS layer is the always-on piece** (cheap; effectively free); everything else is on-demand."*

And from the naming brief:

> *"An interesting property: **the Ephemeral Compute control plane should be able to run inside Ephemeral Compute**… This is recursion, but it is also practical."*

**Nobody has built it.** It is the most quotable idea in the corpus, it follows directly from the architecture, and a platform that can host its own control plane is a much stronger claim than one that cannot. Whether it *should* be built is `08__` Q1 — a control plane that must exist to start itself has a bootstrap problem, and the honest answer may be "the DNS layer and one small always-on waker, everything else ephemeral."

---

## 6. Cost — what can be said, and what cannot

**Can be said:**

- Measured boot times (§3), including the failures.
- Spot is used and defaulted where appropriate: `vault_app` and Fargate set `use_spot = True # spot by default (~70% cheaper)` and `launch_type = 'FARGATE_SPOT'`.
- Teardown defaults: `max_hours = 1` everywhere, fractional supported (`0.1` = 6 minutes), idle reconciliation at ~15 minutes.
- The brief-level estimates, **labelled as estimates**: *"Cost per running unit | **$0.005–0.10+ per hour** | Effectively free for short bursts"*, and for warm pools *"A pool of 3–5 t3.small instances at ~$0.02/hour each is roughly **$1–3/day**."*

**Cannot be said:**

- **Any figure from the dashboard cost tracker.** Its own header: *"placeholder cost tracker. Shows **mocked** cost estimate… **Real cost calculation is its own brief**."* Its `HOURLY_RATES` table is five hardcoded t3 rates. **That brief does not exist in either repo.**
- **Image sizes.** Not recorded anywhere and not derivable without a build.
- **Any throughput or concurrency number.** None were measured.

**The honest cost page is: here is what a run costs to *start* (measured), here is what it costs to *hold* (teardown defaults), and the per-workload cost model is not built yet.** That is more useful than a fabricated pricing table, and it is checkable.

---

## 7. The adjacent bets — three research threads worth a page each

**Nitro Enclaves** (3,480 w, 15 May) — the confidential-compute tier, and it carries the best customer sentence in the whole corpus:

> *"Run your security scan against your private repository. The scanner code is open source. The enclave's attestation proves it is the exact code you can inspect. **We cannot see your code, even though it ran on our infrastructure.**"*

That is the SG/Send zero-knowledge argument extended to compute, and it belongs on this site because it is the thing that distinguishes it from every generic runner.

**Firecracker** (3,222 w + 2,607 w research, 15 May) — with a fact that changed the economics:

> *"**AWS nested-virt support on C8i/M8i/R8i (Feb 2026) collapsed Firecracker entry cost from $3+/hour to ~$0.09/hour.**"*

**AgentCore** (2,980 w, 15 May) — where SG/Compute layers on Bedrock rather than competing with it. Worth publishing as positioning, and worth re-checking, because it is fifteen months old and that market has moved.

---

## 8. The workload classes to name on the front page

From the serverless brief: **vault apps, agents, AppSec mini-tools, demo environments, CI workloads, multi-region testing, and security scanners in Nitro Enclaves.**

Note that the spec catalogue (`04__` §4) already covers most of these — vault specs, browser specs, LLM specs, observability specs. **The workload list and the spec list are the same argument told twice, and the site should join them:** each named workload class should link to the spec that serves it, and the ones with no spec are the roadmap.

And the honest caveat that belongs with all of it, from the serverless brief itself:

> *"**The composition is not built yet, but the gap is integration, not new invention.**"*

Fifteen months later that is still the right sentence, and `03__`'s audit says why: the pieces are real, and warm pools, multi-node stacks, non-EC2 platforms and the artefact sinks are the integration that has not happened.

---

This document is released under the Creative Commons Attribution 4.0 International licence (CC BY 4.0).

---

*Published on sg-compute.sgit.ai under CC BY 4.0. Source: the `sg-compute.sgit.ai` brief pack v0.33.62, 24 August 2026, by Dinis Cruz via the SG/Send Librarian, with AI co-authorship (Claude, Anthropic).*
