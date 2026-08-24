# 02 — The rename: what is done, what is not, and what breaks

The lead is right that the repo needs renaming, and the 30 April 2026 naming brief already specified it in full — including nine numbered acceptance criteria. This document scores the work against that brief and lists what a rename would actually break.

**Headline: architecturally done, textually about 40% done.** The Node/Pod/Spec abstraction, the manifest system, the route loader and the CLI builder are all built and working. The package name, the PyPI name, the Docker image, the env-var prefix, the runtime `service_name` and the word "stack" all still say Playwright.

---

## 1. Where the names are, counted

| Name | Files containing |
|---|---:|
| `sgraph_ai_service_playwright` | 5,140 |
| `sg-playwright` | 5,008 |
| `sg_compute` | 3,013 |
| `SG/Compute` | 815 |
| `sg-compute` | 557 |
| `SGraph-AI__Service__Playwright` | 114 |
| `sgraph-ai-service-playwright` (PyPI) | 14 |

Runtime self-identification is still Playwright — `Capability__Detector.py:60` sets `service_name = 'sg-playwright'`. Env vars are **21 distinct `SG_PLAYWRIGHT__*`** against **2 `SG_COMPUTE__*`**.

---

## 2. The nine acceptance criteria, scored

From the 30 April brief. Verified against the tree.

| # | Criterion | | Evidence |
|---|---|:-:|---|
| 1 | No "SP" / "SGraph Playwright" references remain | ❌ | `sp` and `sp-cli` are live `pyproject.toml` entry points; `sgraph_ai_service_playwright__cli` is 71,182 LOC |
| 2 | CLI uses `sg-compute node/pod/stack` | 🟡 | The `sg-compute` binary exists, but only `sg nodes` is wired into `Cli__SG`. **`Cli__Compute` — the taxonomy-correct aggregator with pod/spec/stack — exists and is not a `pyproject` entry point**, reachable only via `scripts/sg_compute_cli.py` |
| 3 | API uses `/nodes /pods /stacks /specs` | ✅ | All four route classes exist and are mounted |
| 4 | Frontend nav shows Nodes/Specs/Stacks/Settings | ✅ | `sg-compute-left-nav.html`: Compute · Nodes · Stacks · Specs · Settings · API |
| 5 | Specs stored as JSON with `spec.json` | ❌→✅ | **Deliberate deviation, and better than the brief asked for**: typed `manifest.py` + `Schema__Spec__Manifest__Entry`. See `04__` |
| 6 | "Stack" reserved for multi-node only | ❌ | Every per-spec CLI help string still says *"Ephemeral X EC2 stacks"* for a single instance — **13 occurrences in `Cli__SG.py` alone** |
| 7 | ≥6 specs defined | ✅ | 16 registered |
| 8 | Folder structure matches the taxonomy | 🟡 | `sg_compute/{core,cli,control_plane,platforms}` + `sg_compute_specs/` match. `frontend/` is still `sgraph_ai_service_playwright__api_site/` |
| 9 | Old naming gone from user-facing surfaces | ❌ | `service_name='sg-playwright'`, `SG_PLAYWRIGHT__*`, the `diniscruz/sg-playwright` image, the `sgraph-ai-service-playwright` PyPI name |

**Score: 3 done, 2 partial, 4 not done — plus one deliberate improvement over spec.**

Criterion 6 is the cheapest and most visible win. The brief was explicit: *"**Reserve 'stack' for this. Do not use it for single nodes.**"* Thirteen help strings in one file currently violate it, and — see `08__` — there is no multi-node orchestration for the word to describe anyway.

---

## 3. The guard that was supposed to hold the line

Covered in `00__` §3 and worth restating here because it belongs to the rename story: `tests/ci/test_no_legacy_imports.py` uses `sgraph_ai_service_playwright[^_]`, which cannot match `sgraph_ai_service_playwright__cli`. **Verified: guard matches 0 files; 228 real legacy imports exist across 69 files; deleting `[^_]` makes it fail as intended.**

The dependency also runs **both ways** — `__cli` imports `sg_compute` 72 times — so the cycle the guard's docstring claims was broken is not broken.

There is a second tell in the same file. Its `_OBJECT_NONE_ALLOWLIST` exempts a path called `sg_compute_specs/playwright/core/docker/Local__Docker__SGraph_AI__Service__Playwright.py` — **a class named after the old service, living inside the new tree.** The rename has not reached the class names.

---

## 4. Full rename scope, and what breaks

| Surface | Current | Breaks? |
|---|---|---|
| Repo name | `SGraph-AI__Service__Playwright` | 114 files reference it |
| **PyPI package** | `sgraph-ai-service-playwright` | **Yes — published name.** Needs a new package plus a deprecation shim |
| **Docker images** | `diniscruz/sg-playwright`, `-vnc`, `sg-host-control` | **Yes — 124 + 19 references** including CI, user-data and compose. Running EC2 nodes pull by name |
| Legacy package dir | `sgraph_ai_service_playwright__cli/` | 228 imports across 69 files |
| Frontend dir | `sgraph_ai_service_playwright__api_site/` | Static mount paths + the `test_wheel_contains_ui` guard |
| **Env vars** | `SG_PLAYWRIGHT__*` (21) | **Baked into `.env` on every running EC2** — a rename orphans live nodes |
| Runtime identity | `service_name = 'sg-playwright'` | Consumers key off `/health/info` |
| CLI aliases | `sp`, `sp-cli` | Documented as *"legacy, kept for backward compat"* |
| DNS zone | `sg-compute.sgraph.ai` (128 refs) | **Live Route 53 zone** — see §5 |

**One thing is already broken:** `.github/workflows/bake-ami.yml` invokes a binary called **`sg-play` sixteen times**. `sg-play` is defined nowhere — not in `pyproject.toml`, not in `scripts/`. **That entire workflow is dead**, which also means the AMI bake pipeline described in `00__` §4 as a maturity signal is currently not runnable as written.

**Recommended sequencing**, because a big-bang rename would orphan live infrastructure:

1. **Fix the guard first** (`00__` §3) so the legacy dependency becomes visible and measurable.
2. **Fix `sg-play`** — the dead workflow is a one-line problem hiding a whole pipeline.
3. **Add aliases before removing names.** Publish the new PyPI package and Docker tags alongside the old; make `service_name` configurable; accept both env-var prefixes with the old one warning.
4. **Break the `__cli` cycle** — 228 imports, mostly `aws`, `credentials` and `tui`. This is the real work and it is the thing blocking a clean package boundary.
5. **Then rename the repo**, last, when nothing points at the old name that is not aliased.

---

## 5. ⚠️ The domain collision — decide it deliberately

The target is **`sg-compute.sgit.ai`**.

**`sg-compute.sgraph.ai` is a live Route 53 zone**, used for per-node DNS as `<stack-name>.sg-compute.sgraph.ai`, and it appears **128 times** in the repo — including in code defaults and test assertions.

Same label, different TLD. That is workable, and it is also the kind of thing that produces a support question every week forever. The site should either:

- **claim the distinction explicitly** — `sgit.ai` is documentation, `sgraph.ai` is running infrastructure — and say so on the front page and in `/network/`; or
- **move the node DNS** to `sgit.ai` too, which touches 128 references and every running node.

The first is much cheaper and is the recommendation. But it must be a stated decision on the site, not an accident a reader discovers.

---

## 6. The naming brief's other good ideas, currently unused

Three lines from the 30 April brief deserve to be on the site rather than buried in a four-month-old document:

> *"An interesting property: **the Ephemeral Compute control plane should be able to run inside Ephemeral Compute**… This is recursion, but it is also practical."*

That is directly supported by the serverless brief's *"We do not need a serverless 'control plane' running 24/7. The control plane is one specific role that can spin up itself on demand, do its work, and shut down."* **Nobody has built it, and it is the most quotable idea in the corpus.**

> *"This is the **simulated AWS Marketplace**: a catalogue of pre-configured, ready-to-launch environments."*

Sixteen specs with typed manifests, stability ratings and boot times is exactly that catalogue, and `/specs/` should be framed as one.

> *"The overall product is sometimes called 'ephemeral EC2,' which is too narrow: **it is bigger than EC2.**"*

Still true, and still not reflected in a `Platform` ABC that only has one implementation. `08__` Q3.

---

This document is released under the Creative Commons Attribution 4.0 International licence (CC BY 4.0).

---

*Published on sg-compute.sgit.ai under CC BY 4.0. Source: the `sg-compute.sgit.ai` brief pack v0.33.62, 24 August 2026, by Dinis Cruz via the SG/Send Librarian, with AI co-authorship (Claude, Anthropic).*
