# 06 — Site Architecture

## The house pattern

Copy **`pki.sgit.ai`** — all six house markers, and its raw-plus-curated split (`/documents/` markdown as source of truth beside rendered HTML) is what this site needs, because much of its content is generated from a codebase.

Add the `/llms-full.txt` pki lacks. And add one thing no sibling has, because this site's failure mode is specific:

> **Generate every page that describes the code, from the code, at build time.**

Every stale artefact in this repo — `capabilities.json` at 42 versions behind, the reality doc at 41, the README describing a package that does not exist — became stale because it was written once by hand. **A documentation site for this platform that is hand-maintained will be the fifth stale source of truth within a quarter.** The manifests, the route tables, the CLI verbs, the spec catalogue and the test counts are all machine-readable. Read them.

Take pki's CI pipeline as-is, and extend the key-leak check to reject the patterns in `07__` §2.

---

## Page by page

### `/` — the front page

Two claims, in this order.

**First, what it is:** an ephemeral compute platform with sixteen ready-to-launch environments — not a browser service. Lead with the number that settles it: **~71% of the new code is not browser code; Playwright is 1 of 16 specs.**

**Second, the three axioms**, rescued from the stale `capabilities.json` where they are currently buried: **statelessness, least-privilege-by-declaration, self-description.** They are good, and unlike the file that names them, they are actually implemented.

Then one honest sentence about state: built in 100 days, mature where it counts, and here is `/shipped/`.

### `/what-it-is/` — build first
`01__`. **The two ephemeral layers, separated on page one** — per-request browser teardown and per-node EC2 teardown are different things and conflating them is the most common misreading. Include the watchdog (`01__` §3); it is the best engineering story in the repo.

### `/specs/` — the catalogue
`04__` and `specs__catalogue.json`. **One page per spec, generated from `manifest.py`.** Family view first, alphabetical second. Stability and boot time in the header. State the `create_node` gap per spec. Publish the entry-point contract as an invitation.

Frame it as the 30 April brief did: *"the simulated AWS Marketplace: a catalogue of pre-configured, ready-to-launch environments."*

### `/why/` — the argument
`05__`. *"We are competing for the agent-deployment market."* The cold-start ladder against the measured benchmarks, the 50-second claim with its breakdown, the recursion idea, and the three adjacent bets.

### `/numbers/` — the measured data
The boot benchmarks **with instance and AMI IDs stripped**, including the seven capacity failures. The test counts. The commit history. **This page is the site's credibility, because everything on it is checkable.**

### `/rename/` — publish the migration
`02__`. Unusual for a product site and right for this one: the repo is public, the old name is everywhere, and a reader will hit the mismatch immediately. Nine criteria scored, the full surface list, the PyPI and Docker breakage, the sequencing, and the domain decision.

### `/agents/` — the machine surface
The API surface from `01__` §4, **the auth model as it actually works** (including the correction to the existing skill documentation), the 25-verb sequence language, and the `/health/capabilities` self-description endpoint. Note the JS allowlist is deny-by-default — an agent cannot `evaluate` until an operator opts in.

### `/shipped/` — non-negotiable
`00__` §6, unsoftened. No warm pools. No multi-node stacks. `create_node` for 3 of 16. Artefact sinks 2 of 4. One platform of four. No cost model. No throughput measurement. `bake-ami.yml` dead. And the four stale sources with the stated policy: **code wins.**

### `/network/` and `/admin/`
The seven-site map (`07__` §5), and the `sg-compute.sgit.ai` vs `sg-compute.sgraph.ai` distinction stated plainly (`02__` §5). House-pattern admin surfaces; publish the build order unresolved with `08__`'s questions and tensions visible.

---

## What is generated and what is written

| Content | Source |
|---|---|
| Spec pages | **generated** from `manifest.py` |
| API reference | **generated** from the FastAPI route definitions |
| CLI reference | **generated** from `Spec__CLI__Builder`'s verb set |
| Test and coverage counts | **generated** from a CI run |
| Version, image tags | **generated** from the `version` file |
| The argument, the audit, the rename story | **written** — `00__`–`05__` are the raw material |

The rule: **if a number appears on the site and also exists in the repo, the site reads it from the repo.** Anything else drifts.

---

## Naming conventions

- The platform is **SG/Compute**; the repo becomes `sg-compute`; the PyPI package and Docker images follow (`02__` §4).
- **`Node`** = one compute instance. **`Pod`** = a container on a node. **`Spec`** = a workload definition. **`Stack`** = 2+ coordinated nodes — **and per the 30 April brief, do not use "stack" for a single node.** Thirteen CLI help strings currently do.
- Spec ids stay as they are in `manifest.py` — `playwright`, `vault_publish`, `local_claude`. Do not prettify them; they are API identifiers.

---

This document is released under the Creative Commons Attribution 4.0 International licence (CC BY 4.0).

---

*Published on sg-compute.sgit.ai under CC BY 4.0. Source: the `sg-compute.sgit.ai` brief pack v0.33.62, 24 August 2026, by Dinis Cruz via the SG/Send Librarian, with AI co-authorship (Claude, Anthropic).*
