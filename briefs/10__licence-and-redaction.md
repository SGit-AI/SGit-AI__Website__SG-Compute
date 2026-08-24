# Licence


> **Redacted for publication.** This document is the redaction list itself, so it named every live address it told the site to strip. It is published here under its own rule — *shapes, not addresses*: the AWS account id, the live internal hostnames, the named stack FQDNs and the real EC2 and AMI ids have each been replaced by the shape they are an instance of. Nothing else was changed. The site's [leak tripwire](../admin/index.html#leak) encodes the same list so it cannot regress.


## This pack

Everything in this brief pack — the nine numbered documents, `09__source-manifest.csv`, `specs__catalogue.json`, this file and `README.md` — is released under the **Creative Commons Attribution 4.0 International licence (CC BY 4.0)**.

    Copyright (c) 2026 Dinis Cruz
    Licensed under CC BY 4.0 — https://creativecommons.org/licenses/by/4.0/

Attribution: **Dinis Cruz**, with AI co-authorship (Claude, Anthropic).

## The site this pack commissions

**The entire content of `sg-compute.sgit.ai`** — every page, `/documents/`, `/llms.txt`, `/llms-full.txt` and the admin surfaces — is to be published under **CC BY 4.0**, consistent with the network. Stamp every raw markdown document and gate it with `licence-audit.py --check`.

**The code itself is Apache-2.0** (`/root/sg-playwright/LICENSE`, `license = "Apache 2.0"` in `pyproject.toml`), consistent with the rest of the estate. Where the site quotes source, it is quoting Apache-2.0 code — retain the notice and do not imply the snippets carry the site's CC BY licence.

---

## ⚠️ This pack draws on a live infrastructure repository

The redaction list is longer than for the other sites, and it matters more, because publishing a hostname here publishes an attack surface. **`07__` §2 is not advisory.**

**Must be stripped before anything is published:**

- **The AWS account ID `<aws-account-id>`** — appears in 20+ files under `team/humans/dinis_cruz/claude-code-web/`
- **Live internal hostnames** — `<ops-zone>` (193 refs), `sg-compute.sgraph.ai` (128), `<send-zone>` (46), `<edge-host>.<ops-zone>` (38), `<vault-zone>` (36), `<dev>.<vault-zone>` (19), `<qa-zone>` (17), `<admin-host>.<ops-zone>` (25), `<waker-host>.<ops-zone>` (24), `<dev>.<tools-zone>` (177)
- **Named live stack FQDNs** — `<stack-name>.…`, `<stack-name>.…`, `<stack-name>.…`, `<stack-name>.…`, and `<demo-slug>.<ops-zone>` (a demo slug, not a customer — but it reads like a person's name, so drop it)
- **Real EC2 instance IDs and AMI IDs** in `utils/ec2_boot_bench/ec2_boot_bench_results.csv` — **publish the timings, strip the 16 instance IDs and 3 AMI IDs**

**The rule: shapes, not addresses.** `<stack-name>.sg-compute.<zone>` is documentation; a live FQDN is a target. Add the account ID and the hostname list to the CI key-leak check so this cannot regress.

## What was checked and is clean

Verified, not assumed: **no real `.env` values** (three `.env.example` only, and `.gitignore` covers the rest); **no AWS access keys** (every `AKIA*` is the AWS public documentation example or a synthetic fixture); **no private keys** (all synthetic or generated at test runtime); **no GitHub, Slack, OpenAI or Anthropic tokens**; **no public IPs in code**; all CI credentials from `${{ secrets.* }}`.

## The one security note to publish honestly

`EC2__Platform.create_node` writes the per-node API key into an EC2 tag, and the codebase already documents the consequence: *"Visible to anyone with `ec2:DescribeInstances`."*

**No live key is exposed in the repo — this is a design trade-off, not a leak.** The key is also in SSM (the correct store); the tag is a dashboard convenience with a comment saying so; the key is per-node, never reused, and nodes self-terminate on a one-hour default.

Publish it as a **known trade-off with a named mitigation** (read from SSM in the dashboard, drop the tag), not as a vulnerability disclosure, and publish no exploitation path. `07__` §4 has the framing. The source is public either way; omitting a weakness the code itself comments on costs more credibility than the weakness does.

## Manifest tiers

- **Tier 3 (5 rows)** — do not publish, quote or paraphrase.
- **Tier 2 (5 rows)** — `STRIP IDS`, `FIX FIRST`, `REDACT AND USE`, `STALE — DO NOT CITE`, `DO NOT USE`. Read `why_it_matters` before touching them. In particular **the README must not be used as a source for anything**.
- **`STALE — RECHECK`** on four Tier-1 research briefs: the Firecracker and AgentCore material is fifteen months old and those markets have moved.

## Accuracy

**Code wins.** Where the README, `capabilities.json`, the reality document and the tree disagree, the tree is right — and this pack's numbers were all measured from the tree in this session, not taken from documentation.

**Do not publish** an image size (not recorded anywhere, not derivable without a build), any figure from the dashboard cost tracker (its own header says *"placeholder… Shows mocked cost estimate"*), or any throughput or concurrency number (none were ever measured).

---

This file is released under the Creative Commons Attribution 4.0 International licence (CC BY 4.0).

---

*Published on sg-compute.sgit.ai under CC BY 4.0. Source: the `sg-compute.sgit.ai` brief pack v0.33.62, 24 August 2026, by Dinis Cruz via the SG/Send Librarian, with AI co-authorship (Claude, Anthropic).*
