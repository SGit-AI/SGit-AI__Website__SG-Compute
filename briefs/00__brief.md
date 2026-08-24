# 00 — The Brief: `sg-compute.sgit.ai`

**Version** v0.33.62 · 24 August 2026
**From** Dinis Cruz, via the SG/Send Librarian
**To** the agent commissioned to build `sg-compute.sgit.ai`
**Licence** CC BY 4.0 — see `07__` for the redaction list, which is longer than usual because this pack draws on a live infrastructure repo

---

## 1. The commission

> *"a pack for `sg-compute.sgit.ai`, which not only we should have a good number of briefs about — if you take a look at `github.com/the-cyber-boardroom/SGraph-AI__Service__Playwright` (**a repo that needs to be renamed and refactored**) you will see that we have already created **a VERY mature ephemeral compute platform**."*

Both claims were tested against the code. **Both hold.** The measurements are below, along with the four places the maturity claim is overstated — because a site that repeats the claim without them will be caught by anyone who clones the repo.

---

## 2. The rename is right, and here is the number that settles it

**~71% of the new codebase is not browser code.**

| | LOC | Share |
|---|---:|---:|
| **Generic compute core** (`sg_compute/` — Platform ABC, spec registry, node/pod managers, EC2 helpers, user-data, TLS, CLI builder, control plane) | 10,416 | 14.7% |
| **Browser specs** (playwright, firefox, vnc, neko, content_proxy) | 20,199 | 28.5% |
| **Non-browser specs** (sg_edge, vault_publish, vault_app, mitmproxy, docker, elastic, prometheus, opensearch, podman, ollama, local_claude, open_design) | 40,370 | 56.9% |

**Playwright is 1 of 16 registered specs and 17% of spec LOC.** Include the legacy `__cli` package — 71,182 lines of AWS, IAM, credentials, sentinel and TUI code, all generic — and the browser-specific share of the whole 217k-line repo falls to about **14%**.

The 30 April naming brief said it first, and better:

> *"The project is called 'SP' (SGraph Playwright), which is wrong: **Playwright is just one of many components now.**"*
> *"The overall product is sometimes called 'ephemeral EC2,' which is **too narrow: it is bigger than EC2.**"*
> *"**Now is the right time to fix this.** We are in the middle of a refactoring. The code, the CLI, the API, and the UI can all be renamed together."*

That was four months ago. **The rename is architecturally done and textually about 40% done** — scored against the brief's own nine acceptance criteria in `02__` §2.

---

## 3. ⚠️ The one-character bug that has been hiding it

`tests/ci/test_no_legacy_imports.py` exists to stop the new tree importing from the legacy one. Its regex:

```python
r'from\s+sgraph_ai_service_playwright[^_]|import\s+sgraph_ai_service_playwright[^_]'
```

`[^_]` requires a **non-underscore** after the package stem. The real package is `sgraph_ai_service_playwright__cli` — **double** underscore. Verified independently in this session by running both patterns over the tree:

```
GUARD regex  : 0 files -> test PASSES (vacuously)
REAL imports : 69 files, 228 import lines
FIXED regex (drop [^_]): 69 files -> test FAILS, as intended
```

Breakdown of the 228: `__cli.aws` 126, `__cli.credentials` 71, `__cli.tui` 23, plus `osx`, `observability`, `firefox`, `neko`, `sentinel`. And the dependency runs **both ways** — `__cli` imports `sg_compute` 72 times. The guard's own docstring says *"BV2.7 broke the cycle."* **The cycle is not broken.**

**Deleting four characters turns this test red immediately.** That is a good thing to do before the site claims the tree is clean — and it is a genuinely good story for `/shipped/`: a guard that was passing because it could not match the thing it was guarding against.

---

## 4. What "very mature" actually means — measured

**Sustained:**

- **`pytest tests/ci tests/unit -q` → 4,785 passed, 4 failed, 4 skipped, in 81 seconds.** A large, fast, green suite.
- **2,777 commits and 245 tags in 100 days** — first commit 16 April 2026, last 24 July 2026. 1,700 commits by Claude, 826 by Dinis Cruz, 243 by GitHub Actions.
- **1,265,371 words of markdown**, including a formal reality-document system (72,339 words, 12 domains) whose governing rule is *"**If the reality document doesn't list it, it does not exist.** … **Briefs are aspirations, not facts.**"*
- **CI/CD that is genuinely sophisticated**: native per-arch builds, **push by digest only**, integration-test the pre-tag image, and only then combine digests into a manifest. `bake-ami.yml` is a two-phase bake that **relaunches from the baked AMI and re-verifies** before tagging `healthy`.
- **Operational hardening built from real incidents** — a `Request__Watchdog` that calls `os._exit(2)` on a stuck request (written against a real Lambda deadlock, with the GIL reasoning in the source), a two-phase `Health__Poller`, ACME automation **including IP certificates**, and two Dockerfile build-time guards each citing the production incident that motivated it.

**Overstated, in four specific places:**

1. **There is no static analysis at all.** No mypy, ruff, flake8, pylint, black, isort, tox — no config anywhere. Type safety is enforced *at runtime* via `Type_Safe`, present in 1,333 of 3,127 package files (42.6%).
2. **CI runs 4,793 of 7,110 collectible tests — 67.4%.** The 2,317 outside CI contain **six real import-level breakages**, including four circular imports and one missing module.
3. **No infrastructure-as-code.** No Terraform, CloudFormation, CDK or SAM. Provisioning is imperative Python over `osbot-aws`.
4. **Four sources of truth are knowingly stale**: `capabilities.json` (v0.1.29 vs code at v0.2.71 — **42 minor versions**), the reality doc (v0.2.30, last updated 17 May), and the README (see §5).

And one thing the site should state rather than hide: **the last commit is 24 July 2026.** Two-thirds of all commits landed in the first six weeks; June had 129 and July 58. This is a platform that was built at extraordinary speed and has been quiet for a month.

---

## 5. The README describes a repository that does not exist

```
## Status
**Phase 0 in progress** — repo skeleton, Dockerfile, CI workflow scaffolding.
```

At **v0.2.71, 217,266 lines of Python, 7,110 tests**. Its "Repo layout" documents a package `sgraph_ai_service_playwright/` with `schemas/ fast_api/ service/ dispatcher/ client/ docker/ consts/` — **that directory does not exist**. It points at a reality path superseded on 17 April 2026, cites base image `v1.58.2-noble` where the Dockerfile pins `v1.58.0-noble`, and claims a Lambda Web Adapter the Dockerfile header explicitly says is absent.

**It is the single most misleading artefact in the repo.** Write every word of the site from the tree, never from the README — and make **"code wins"** the site's stated policy for all four stale sources.

---

## 6. The honesty constraint

`/shipped/` has real work here:

- **No warm pools.** Central to the serverless pitch, specified in a 1,729-word brief with worked economics — **zero implementation.** Grep finds only `IDLE_TEARDOWN_THRESHOLD` in the edge reconciler.
- **No multi-node stacks.** The taxonomy's whole point is that a Stack is 2+ coordinated Nodes. `Routes__Compute__Stacks` returns a *list*, `Cli__Compute__Stack` is unwired. **There is no multi-node orchestration.**
- **`create_node` supports 3 of 16 specs.** `EC2__Platform._service_for` raises `NotImplementedError` for anything but `docker`, `podman`, `vnc`.
- **Artefact sinks: 2 of 4 implemented.** `VAULT` and `S3` both raise `NotImplementedError`. Today it is base64 inline (20 MB cap) or a local file. **No S3, no presigned URLs, no vault writes** — do not claim otherwise.
- **Non-EC2 platforms do not exist.** `'ec2' | 'k8s' | 'gcp' | 'local'` is a comment in the Platform ABC. Only EC2 is implemented.
- **No cost model.** The dashboard tracker says so itself: *"placeholder cost tracker. Shows mocked cost estimate… Real cost calculation is its own brief."* That brief does not exist.
- **No throughput measurement.** *"A single container can serve hundreds of parallel requests trivially"* is argued and never measured. No load tests anywhere.
- **`bake-ami.yml` is dead.** It invokes a binary called **`sg-play` sixteen times**. `sg-play` is defined nowhere — not in `pyproject.toml`, not in `scripts/`.

---

## 7. The numbers

| | |
|---|---|
| **Code** | 3,999 Python files · **217,266 LOC** · 799 test files · **1,265,371 words of markdown** |
| **History** | **2,777 commits, 245 tags, 100 days** (16 Apr → 24 Jul 2026) · Claude 1,700 / Dinis 826 / Actions 243 |
| **Specs** | **16 registered** (+`sg_edge`, unregistered — no manifest) · 8 STABLE, 8 EXPERIMENTAL · boot times 15s–600s |
| **Tests** | 7,110 collectible · **4,785 pass in 81 seconds** · CI covers **67.4%** · 7 collection errors, 6 outside CI |
| **API** | Two FastAPI apps · 25-verb declarative sequence language · stateful sessions · Prometheus metrics |
| **Boot** | Measured: t3.micro **16.4s**, c5.large **16.2s**, g5.xlarge on-demand **18.2s**, spot **20.5s** — plus **7 recorded capacity failures** |
| **Rename** | 9 acceptance criteria: **3 done, 2 partial, 4 not done**, +1 deliberate improvement |
| **This pack** | 9 documents · manifest of **37 rows** — 10 Tier-0, 17 Tier-1, 5 Tier-2, 5 do-not-publish; **53,132 words** of briefs, every path verified on disk · the 16-spec catalogue as JSON |

---

## 8. Build order

1. **Fix the guard, then `/shipped/`.** Delete `[^_]`, watch it go red, and publish §3 as the site's opening credibility move. A platform site that leads with a bug it found in its own CI is trusted differently from one that leads with features.
2. **`/what-it-is/` — the two ephemeral layers.** `01__`. The most common misreading of this platform is conflating the per-request browser teardown with the per-node EC2 teardown. Separate them on page one.
3. **`/specs/` — the catalogue.** `04__` and `specs__catalogue.json`. Sixteen specs, three generalisation mechanisms, and the entry-point path for third-party specs. **This is what makes it a platform rather than a service.**
4. **`/rename/` — publish the migration.** `02__`. Nine criteria scored, the full surface list, the PyPI and Docker breakage, and the `sg-compute.sgit.ai` vs `sg-compute.sgraph.ai` collision (§`02__` §5).
5. **`/why/` — the serverless argument.** `05__`. *"We are competing for the agent-deployment market."*
6. **`/numbers/`** — the boot benchmarks with the instance IDs stripped, including the capacity failures. Honest measured data beats a marketing claim.
7. **`/agents/`** — the API surface, the auth model as it actually works (`01__` §4 corrects the received wisdom), and the sequence language.

Publish the build order unresolved with `08__`'s open questions and tensions visible.

---

This document is released under the Creative Commons Attribution 4.0 International licence (CC BY 4.0).

---

*Published on sg-compute.sgit.ai under CC BY 4.0. Source: the `sg-compute.sgit.ai` brief pack v0.33.62, 24 August 2026, by Dinis Cruz via the SG/Send Librarian, with AI co-authorship (Claude, Anthropic).*
