# 03 — The maturity audit

The lead's claim is that this is *"a VERY mature ephemeral compute platform."* **It holds** — and a site that repeats it without the four qualifications below will be caught by anyone who clones the repo. Publishing the audit is what makes the claim credible.

Every number here was measured in this session, not estimated.

---

## 1. Where the maturity is real

### Tests

```
pytest tests/ci tests/unit -q
→ 4,785 passed, 4 failed, 4 skipped — 81 seconds
```

**4,785 tests in 81 seconds** is a genuinely fast, genuinely large suite. Repo total collectible: **7,110** across 799 test files.

The 4 failures are **test-hygiene time bombs, not code defects**: three IAM tests hardcode `last_used='2026-05-17T00:00:00+00:00'`, which is now more than 90 days stale, so a `STALE_ROLE` assertion fires. The fourth needs a built wheel. **These will fail for anyone who clones the repo today** — worth fixing before the site invites people to.

### History

**2,777 commits and 245 tags in 100 days.** First commit 16 April 2026, last 24 July 2026.

| Author | Commits |
|---|---:|
| Claude | 1,700 (61%) |
| Dinis Cruz | 826 (30%) |
| GitHub Actions | 243 (9%) |

And the shape, which the site should publish rather than smooth over:

| Month | Commits |
|---|---:|
| Apr 2026 | 1,136 |
| May 2026 | 1,454 |
| Jun 2026 | 129 |
| Jul 2026 | 58 |

**Two-thirds of the repo landed in the first six weeks, and there has been no commit since 24 July** — a month of silence as of this pack. That is not a criticism; it is what "built fast, then stabilised" looks like. But a site claiming an actively-developed platform against a repo whose last commit is a month old is making a claim a reader can check in one click.

### CI/CD

Nine workflows; `ci-pipeline.yml` alone is 36,815 bytes. The pipeline is real:

unit tests → increment tag → **native per-arch builds** (amd64 on `ubuntu-latest`, arm64 on `ubuntu-24.04-arm`) → **push by digest only** → integration-test the pre-tag image → **only then** combine digests into a manifest and push to Docker Hub. Same again for the VNC image.

`bake-ami.yml` is a two-phase bake: install from scratch → health and smoke checks → clean → snapshot → **relaunch from the baked AMI and re-verify** → tag `healthy` or `unhealthy`. That is a better AMI process than most infrastructure teams run. **⚠️ It is also currently dead — see `02__` §4.**

Versioning: `v0.2.71`, single source of truth in the repo-root `version` file, auto-incremented by `owasp-sbot/OSBot-GitHub-Actions`, read at runtime by `consts/version.py` and every `manifest.py`, and used as the image tag.

### Documentation

**1,265,371 words of markdown.**

| Area | Files | Words |
|---|---:|---:|
| `team/humans/` | 219 | 426,410 |
| `team/comms/` | 246 | 218,913 |
| `team/roles/` | 130 | 158,075 |
| `team/claude/` (debriefs) | 204 | 156,651 |
| `library/dev_packs/` | 96 | 144,051 |
| `library/docs/` | 54 | 64,289 |
| `library/guides/` | 22 | 44,547 |
| `library/catalogue/` | 37 | 30,038 |

And the mechanism that makes it trustworthy — a formal **reality-document system** (`team/roles/librarian/reality/`, 72,339 words, 12 domains) with a governing rule quoted in `.claude/CLAUDE.md`:

> ***"If the reality document doesn't list it, it does not exist.** … **Briefs are aspirations, not facts.**"*

That is an unusually disciplined honesty mechanism and it deserves a page of its own. **It is also stale** — the index header reads `v0.2.30 | Last updated: 2026-05-17` against a repo at v0.2.71, and the repo's own dev pack flags it: *"The reality doc and `capabilities.json` are demonstrably stale."*

### Operational hardening

Not aspirational — each piece is traceable to a real incident:

- **`Request__Watchdog`** — daemon thread, `os._exit(2)` on a stuck request, written against a real Lambda deadlock, with the GIL reasoning in the source. See `01__` §3.
- **`Health__Poller`** — two-phase: EC2 `running`, then HTTP probe.
- **Two Dockerfile build-time guards** asserting the installed Playwright version equals `1.58.0` **in the same interpreter as `CMD`**, each with a comment naming the production incident that motivated it.
- **ACME / Let's Encrypt automation including IP certificates** via a `shortlived` profile.
- **Prometheus `/metrics`**, plus an observability service with AMP remote-write and OpenSearch.
- **`utils/ec2_boot_bench/`** — 24 real benchmark runs, including recorded failures.

---

## 2. Where the claim is overstated — four places

### (a) There is no static analysis. None.

No `mypy`, `ruff`, `flake8`, `pylint`, `black`, `isort`, `setup.cfg` or `tox.ini` anywhere, and no such configuration in `pyproject.toml`.

Type safety is enforced **at runtime**, via `Type_Safe` from `osbot-utils`, present in **1,333 of 3,127 package files (42.6%)**. That is a real and defensible architectural choice — runtime validation catches things static analysis cannot — but it is not a substitute, and 57% of files do not use it.

The substitute is `tests/ci/`: four hand-written structural guards. **One of them is broken** (`02__` §3).

### (b) CI runs 67.4% of the tests

| Path | Collected | In CI? |
|---|---:|:-:|
| `tests/ci` | 33 | ✅ |
| `tests/unit` | 4,760 | ✅ |
| `tests/integration` | 24 | ❌ |
| `tests/integration_live` | 60 | ❌ |
| `tests/local` | 5 | ❌ |
| `tests/benchmarks` | 3 | ❌ |
| `sg_compute__tests` | **672** | ❌ |
| `sg_compute_specs/**/tests` | **1,280** | ❌ |
| `sgraph_ai_service_playwright__cli/**/tests` | 273 | ❌ |
| **Total** | **7,110** | **4,793 run** |

**2,317 tests never run in CI — including 1,952 that test the new `sg_compute` and `sg_compute_specs` trees**, which is to say the parts the rename is building.

And it shows. **Six of the seven collection errors are in the un-CI'd suites:** four genuine circular imports (`TAG_PURPOSE_KEY` in the neko, opensearch, prometheus and vnc `*__AWS__Client.py` files), one missing module (`sg_compute_specs.playwright.core.schemas.browser.Schema__Proxy__Auth__Basic`), and one stale osbot import path.

**Adding `sg_compute__tests` and `sg_compute_specs/**/tests` to CI would surface six real breakages immediately.** That is the highest-value change available in the repo.

### (c) No infrastructure-as-code

No Terraform, CloudFormation, CDK or SAM templates anywhere. Provisioning is imperative Python over `osbot-aws`.

Defensible for a platform whose whole point is programmatic provisioning — but it means there is no declarative description of the AWS footprint, no plan/apply, and no drift detection. Worth stating rather than leaving a reader to infer it.

### (d) Four sources of truth are knowingly stale

| Artefact | Says | Reality |
|---|---|---|
| `capabilities.json` | `v0.1.29` | **v0.2.71 — 42 minor versions behind.** `COPY`'d into the image and served at `/admin/capabilities` |
| Reality doc index | `v0.2.30`, 17 May 2026 | v0.2.71 |
| `README.md` | *"Phase 0 in progress — repo skeleton"* | 217,266 LOC, 7,110 tests |
| `sg_compute/version` | `v0.1.162` | **Read by nothing.** Grep for any code reading it returns zero hits |

The repo's own documentation already tells you not to trust `capabilities.json`:

> *"The UI reads `GET /health/capabilities` (the live `Schema__Service__Capabilities`, populated by `Capability__Detector`) — **never** the stale `capabilities.json`."*

**The site needs one stated policy: code wins.** The repo's own dev pack already rules this way; make it explicit and apply it everywhere.

---

## 3. The verdict to publish

> **Mature where it counts, thin where the repo has not looked.**
>
> 4,785 tests passing in 81 seconds, digest-first multi-arch CI, AMI bake-and-verify, 1.27 million words of documentation with a formal reality discipline, and operational hardening written from real incidents.
>
> And: no linter, no type-checker, a third of the tests outside CI hiding six real breakages, no IaC, and four sources of truth that disagree with the code.

That paragraph, published as-is, is worth more to the site's credibility than any feature list. It is also **five days of work away from being a much better paragraph** — fix the guard, add the two test suites to CI, resolve the six imports, delete `capabilities.json` or regenerate it, rewrite the README from the tree, and fix the three date-brittle IAM tests.

---

This document is released under the Creative Commons Attribution 4.0 International licence (CC BY 4.0).

---

*Published on sg-compute.sgit.ai under CC BY 4.0. Source: the `sg-compute.sgit.ai` brief pack v0.33.62, 24 August 2026, by Dinis Cruz via the SG/Send Librarian, with AI co-authorship (Claude, Anthropic).*
