# sg-compute.sgit.ai — brief pack

**For:** the agent commissioned to build `sg-compute.sgit.ai`
**From:** Dinis Cruz, via the SG/Send Librarian
**Version:** v0.33.62 · 24 August 2026
**Licence:** CC BY 4.0 — **read `LICENSE.md` before publishing anything.** This pack draws on a live infrastructure repo and the redaction list is not advisory.

---

## What this is

A site for **SG/Compute** — an ephemeral compute platform with sixteen ready-to-launch workload specs, currently living in a repo named after one of them.

Both of the lead's claims were tested against the code, and **both hold**:

> *"a repo that needs to be renamed and refactored"* — **~71% of the new codebase is not browser code.** Playwright is 1 of 16 registered specs and 17% of spec LOC.
>
> *"a VERY mature ephemeral compute platform"* — **4,785 tests passing in 81 seconds**, 2,777 commits and 245 tags in 100 days, digest-first multi-arch CI, AMI bake-and-verify, and 1.27 million words of documentation with a formal reality discipline.

Every number in this pack was measured from the tree in this session. The repo was cloned in full so the history is real.

---

## Read in this order

| File | Words | What it does |
|---|---:|---|
| **`00__BRIEF.md`** | 1.6k | **Start here.** The rename verdict with the number that settles it, the one-character bug, what "mature" measures out at, the honesty constraint, the build order |
| **`01__what-it-is.md`** | 1.5k | **The two ephemeral layers** — the thing the site must not conflate. Sessions, the watchdog, the API surface, isolation, and the auth-model correction |
| `03__maturity-audit.md` | 1.3k | Where the maturity is real, and the four places it is overstated. With the paragraph to publish |
| `02__the-rename.md` | 1.2k | Nine acceptance criteria scored, the broken guard, the full breakage list, the sequencing, the domain collision |
| `04__the-spec-system.md` | 1.3k | **What makes it a platform** — one abstraction, sixteen implementations, three generalisation mechanisms |
| `05__the-serverless-argument.md` | 1.4k | *"We are competing for the agent-deployment market."* The cold-start ladder against the measured benchmarks |
| `06__site-architecture.md` | 0.8k | Page by page, and what is generated vs written |
| `07__boundaries-and-security.md` | 1.0k | The redaction list, what was checked and is clean, and how to publish the one security note |
| `08__gaps-and-open-questions.md` | 1.4k | **A five-day fix list**, 8 build-fresh items, 8 open questions, 7 honest tensions |
| `09__source-manifest.csv` | 37 rows | Every source, tiered 0–3. **Every path verified on disk.** 53,132 words of briefs |
| `specs__catalogue.json` | 17 specs | The full catalogue — LOC, capability, boot time, stability, family, `create_node` support — plus the boot benchmarks and the not-implemented list |
| `LICENSE.md` | — | CC BY 4.0, the redaction rules, and the security framing |

---

## Start with the one-character bug

`tests/ci/test_no_legacy_imports.py` exists to stop the new tree importing from the legacy one. Its regex is `sgraph_ai_service_playwright[^_]` — and `[^_]` requires a **non-underscore** after the stem, while the real package is `sgraph_ai_service_playwright__cli`, with **two**.

Verified independently this session by running both patterns over the tree:

```
GUARD regex  : 0 files -> test PASSES (vacuously)
REAL imports : 69 files, 228 import lines
FIXED regex (drop [^_]): 69 files -> test FAILS, as intended
```

The dependency runs **both ways** — `__cli` imports `sg_compute` 72 times — so the cycle the guard's own docstring says was broken is not broken.

**Deleting four characters turns it red.** And it is the site's best opening move: a platform site that leads with a bug it found in its own CI is trusted differently from one that leads with a feature list.

---

## Four more things to know before you write

**1. The README describes a repository that does not exist.** *"Phase 0 in progress — repo skeleton, Dockerfile, CI workflow scaffolding"* — at v0.2.71, 217,266 lines of Python and 7,110 tests. It documents a package directory that is not there. **Write every word of the site from the tree, and make "code wins" the stated policy** for all four stale sources (`capabilities.json` is 42 versions behind; the reality doc 41).

**2. The maturity claim needs four qualifications.** No static analysis of any kind — no mypy, ruff, flake8, black, tox. **CI runs 67.4% of the tests**, and the 2,317 outside it contain six real import-level breakages. No infrastructure-as-code. And four sources of truth that disagree with the code. All of it is about five days from being fixed — `08__` §1 has the list.

**3. Development has been quiet for a month.** 2,777 commits between 16 April and 24 July 2026 — 2,590 of them in the first six weeks, then 129 in June and 58 in July, and **nothing since**. Also worth publishing: **1,700 of those commits are by Claude, 826 by Dinis.** Both halves belong on the site; a reader can check either in one click.

**4. `sg-compute.sgraph.ai` is a live Route 53 zone.** Same label as the target site, different TLD, serving per-node DNS as `<stack-name>.sg-compute.sgraph.ai`, with **128 references in code and tests**. Recommendation: claim the distinction explicitly — `sgit.ai` is documentation, `sgraph.ai` is running infrastructure — rather than moving 128 references. But make it a stated decision on the front page, not something a reader discovers.

---

## What `/shipped/` has to say

No warm pools (specified in a 1,729-word brief, zero code). No multi-node stacks — the taxonomy's whole point, and `Cli__Compute__Stack` is unwired. `create_node` supports 3 of 16 specs. Artefact sinks: 2 of 4 implemented — **no S3, no presigned URLs, no vault writes**. One platform of four declared. No cost model — the dashboard tracker says so itself. No throughput measurement. And `bake-ami.yml` invokes a binary called `sg-play` sixteen times that is defined nowhere, so **the AMI pipeline cited as a maturity signal is currently dead**.

---

## House pattern

Copy `pki.sgit.ai`, add the `/llms-full.txt` it lacks, and add one rule no sibling needs:

> **Generate every page that describes the code, from the code, at build time.**

Every stale artefact in this repo became stale because it was written once by hand. The manifests, route tables, CLI verbs, spec catalogue and test counts are all machine-readable. Read them, or the site becomes the fifth stale source of truth within a quarter.

Publish the build order unresolved, with `08__`'s open questions and tensions visible.

---

This file is released under the Creative Commons Attribution 4.0 International licence (CC BY 4.0).

---

*Published on sg-compute.sgit.ai under CC BY 4.0. Source: the `sg-compute.sgit.ai` brief pack v0.33.62, 24 August 2026, by Dinis Cruz via the SG/Send Librarian, with AI co-authorship (Claude, Anthropic).*
