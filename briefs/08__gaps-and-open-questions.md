# 08 — Gaps, open questions and honest tensions

---

## 1. Fix before the site ships — the five-day list

These are not site tasks; they are repo tasks that change what the site can honestly say. In order of value.

| # | Fix | Effort | Effect |
|---|---|---|---|
| **F1** | **Delete `[^_]` from `tests/ci/test_no_legacy_imports.py`** | 4 characters | The guard goes red on 228 real legacy imports across 69 files. It has been passing vacuously since it was written |
| **F2** | **Add `sg_compute__tests` and `sg_compute_specs/**/tests` to CI** | one workflow edit | +1,952 tests into CI, and **six real import-level breakages surface immediately** — four circular imports, one missing module, one stale osbot path |
| **F3** | **Fix `sg-play` in `bake-ami.yml`** | one line | The binary is invoked 16 times and defined nowhere. **The whole AMI bake pipeline is currently dead** — and it is cited as a maturity signal |
| **F4** | **Fix the three date-brittle IAM tests** | small | They hardcode `last_used='2026-05-17'`, now >90 days stale, so `STALE_ROLE` fires. **They fail for anyone who clones the repo today** |
| **F5** | **Delete or regenerate `capabilities.json`** | small | 42 versions stale, `COPY`'d into the image, served at `/admin/capabilities`, and the repo's own docs say not to read it |
| **F6** | **Rewrite the README from the tree** | half a day | It says *"Phase 0 in progress — repo skeleton"* at 217k LOC and documents a package that does not exist |
| **F7** | **Add a linter** — ruff is one config block | half a day | There is currently no static analysis of any kind |

F1–F4 are the ones that change the audit paragraph in `03__` §3 from honest-but-awkward to honest-and-strong.

---

## 2. Build-fresh items for the site

| # | Item | Why |
|---|---|---|
| **G1** | **A generated `/specs/` page per spec** | Sixteen hand-written pages will drift. `manifest.py` already carries everything |
| **G2** | **A real cost model** | The only cost artefact is a JS placeholder whose own header says *"Real cost calculation is its own brief."* **That brief does not exist in either repo** |
| **G3** | **Throughput and concurrency measurement** | *"A single container can serve hundreds of parallel requests trivially"* is argued, never measured. No load tests anywhere |
| **G4** | **Aggregated latency** | `/sequence/execute` emits a full timings block per call and nothing aggregates them. No p50/p95 dataset exists |
| **G5** | **Image sizes** | Not recorded anywhere, not derivable without a build. **Do not publish a number** until one is measured |
| **G6** | **The `/pw` proxy's other half** | Vendored into `diniscruz/sg-send-vault`, whose source is in neither repo. Anyone documenting the production auth path is documenting a component they cannot see |
| **G7** | **A "built in 100 days" narrative** | Now possible — the full history is recoverable: 2,777 commits, 245 tags, 16 Apr → 24 Jul 2026, Claude 1,700 / Dinis 826. **Also shows the last commit is a month old.** Publish both halves |
| **G8** | **Uptime, incidents, SLO** | Debriefs describe successful deployments. There is no SLO, no uptime record, no incident log |

---

## 3. Open questions worth publishing unresolved

| # | Question | Where it stands |
|---|---|---|
| **Q1** | **Should the control plane run inside itself?** *"the Ephemeral Compute control plane should be able to run inside Ephemeral Compute… This is recursion, but it is also practical."* | The most quotable unbuilt idea in the corpus. But a control plane that must exist to start itself has a bootstrap problem. The honest answer may be **DNS plus one small waker always-on, everything else ephemeral** — which is what the serverless brief actually describes |
| **Q2** | **Does a container really serve hundreds of parallel requests here?** | Central to the whole Lambda comparison, and **unmeasured**. Every browser request launches a fresh Chromium *process* — the concurrency ceiling is memory, not the web framework |
| **Q3** | **Is `Platform` a real abstraction or an aspiration?** `'ec2' \| 'k8s' \| 'gcp' \| 'local'` is a comment; only EC2 exists | An ABC with one implementation has not been tested as an abstraction. **`local` would be the cheapest proof** and would also make the test suite runnable without AWS |
| **Q4** | **Why do two specs have `vault-writes` while the platform's vault artefact sink raises `NotImplementedError`?** | The capability exists at the spec layer and not at the platform layer. Either the generic sink is redundant or the specs are doing it twice |
| **Q5** | **What is a Stack, given there is no multi-node orchestration?** | The taxonomy reserves the word for 2+ coordinated nodes. `Routes__Compute__Stacks` returns a list; `Cli__Compute__Stack` is unwired; 13 CLI help strings use "stack" for a single instance. **Either build it or retire the word** |
| **Q6** | **Should the EC2 tag carrying the API key be removed?** | `07__` §4. The mitigation is one SSM call in the dashboard. The trade is convenience against `ec2:DescribeInstances` exposure. **A stated decision either way is fine; silence is not** |
| **Q7** | **`sg-compute.sgit.ai` and `sg-compute.sgraph.ai` — same label, different TLD** | `02__` §5. Recommendation is to claim the distinction explicitly rather than move 128 references. **Needs a decision, not a convention** |
| **Q8** | **Is the platform still being developed?** | No commit since 24 July 2026; June and July together were 187 commits against 2,590 in April–May. Paused, done, or between phases — the site should say which |

---

## 4. Honest tensions

1. **Extraordinary velocity, then silence.** 2,777 commits in 100 days is remarkable; a month with none is a fact a reader can check in one click. Both belong on the site.

2. **61% of the commits are by Claude.** That is genuinely interesting — arguably the most interesting thing about the repo for the wider network — and it invites the obvious question about who reads the code. **`open-source.sgit.ai` has the argument** (*"someone still needs to understand what is underneath"*); this site has the artefact. Joining them is a strong page and an uncomfortable one.

3. **Runtime type-safety instead of static analysis.** `Type_Safe` in 42.6% of files is a real choice with real benefits. It is also not a type-checker, and 57% of files have neither.

4. **A reality-document discipline that is itself stale.** *"If the reality document doesn't list it, it does not exist"* is an excellent rule, and the reality doc is 41 versions behind. The discipline is right; the maintenance did not happen.

5. **The best ideas are the unbuilt ones.** Recursion, warm pools, multi-node stacks, Nitro Enclaves, non-EC2 platforms. The corpus's most quotable material is the part with no code — which is exactly what the repo's own rule warns about: *"briefs are aspirations, not facts."*

6. **A platform named for one of its sixteen specs.** Four months after the naming brief said to fix it, `sp` and `sp-cli` are still entry points and `service_name` still returns `sg-playwright`.

7. **Publishing the audit is the right move and it is not comfortable.** No linter, a third of tests outside CI, a guard that never worked, a dead workflow, four stale sources. Every one is fixable in days, and publishing them alongside the fixes is the strongest possible version of the maturity claim.

---

## 5. Loose ends worth an hour each

- **Register or relocate `sg_edge`** — 9,108 lines, the second-largest directory in `sg_compute_specs/`, no `manifest.py`, invisible to the registry.
- **Wire `Cli__Compute` as an entry point.** The taxonomy-correct CLI exists and is only reachable via `scripts/sg_compute_cli.py`.
- **Delete `sg_compute/version`** (`v0.1.162`) or make something read it. Grep says nothing does.
- **Rename `Local__Docker__SGraph_AI__Service__Playwright.py`** — an old-service class name inside the new tree, currently sitting in a CI allowlist.
- **Fix the 13 "stack" help strings** in `Cli__SG.py`. Cheapest visible win against the naming brief.
- **Measure one image size.** One `docker images` line closes G5.
- **Decide whether `allow_all` on the screenshot surface is still right** — it bypasses the JS allowlist on the stated ground that *"each call is an isolated session."* Probably correct; worth a written decision since it is the one place deny-by-default is switched off.

---

This document is released under the Creative Commons Attribution 4.0 International licence (CC BY 4.0).

---

*Published on sg-compute.sgit.ai under CC BY 4.0. Source: the `sg-compute.sgit.ai` brief pack v0.33.62, 24 August 2026, by Dinis Cruz via the SG/Send Librarian, with AI co-authorship (Claude, Anthropic).*
