# 07 — Boundaries, redaction and the security disclosure


> **Redacted for publication.** This document is the redaction list itself, so it named every live address it told the site to strip. It is published here under its own rule — *shapes, not addresses*: the AWS account id, the live internal hostnames, the named stack FQDNs and the real EC2 and AMI ids have each been replaced by the shape they are an instance of. Nothing else was changed. The site's [leak tripwire](../admin/index.html#leak) encodes the same list so it cannot regress.


This pack draws on a **live infrastructure repository**. The redaction list is longer than for the other sites, and it matters more, because publishing a hostname here is publishing an attack surface.

---

## 1. What was checked and is clean

Stated first, because it is the reassuring half and it was verified rather than assumed:

- **No `.env` files with real values.** Only three `.env.example`; the root one uses `<account>.dkr.ecr.<region>.amazonaws.com` and `FAST_API__AUTH__API_KEY__VALUE=change-me`. `.gitignore` lines 138–140 cover `*.env`, `.env`, `.envrc`. No real `.env` is tracked.
- **No AWS access keys.** Every `AKIA*` match is `AKIAIOSFODNN7EXAMPLE` — the AWS public documentation example — plus synthetic `AKIAXXXXXXXXXXXXXXXX` and `AKIANEWKEY1234567890` in test fixtures.
- **No private keys.** Every `BEGIN PRIVATE KEY` match is synthetic: generated at test runtime via `Cert__Generator().generate('example.local')`, a literal `-----BEGIN PRIVATE KEY-----\nKEY\n-----END PRIVATE KEY-----` fixture, or a truncated shape-test constant.
- **No GitHub, Slack, OpenAI or Anthropic tokens.** Zero matches.
- **No public IP addresses in code.** All CI credentials come from `${{ secrets.* }}`.
- Placeholder account ids (`123456789012`, `000000000000`, `111122223333`) are safe.

---

## 2. Must be redacted before publishing

| Item | Where | Why |
|---|---|---|
| **AWS account ID `<aws-account-id>`** | `team/humans/dinis_cruz/claude-code-web/` — **20+ files**, e.g. `05/17/00/…/07__domain-strategy.md:14,86,98,283`; `05/17/01/…bootstrap.md:25,43,113,168`; `04/27/09/01__history-and-context.md:17`; `05/18/10/…/04__cli-debug-commands.md:238,246` | A real 12-digit account ID. Low direct risk, real reconnaissance value |
| **Live internal hostnames** | Throughout | `<ops-zone>` (193) · `sg-compute.sgraph.ai` (128) · `<send-zone>` (46) · `<edge-host>.<ops-zone>` (38) · `<vault-zone>` (36) · `<dev>.<vault-zone>` (19) · `<qa-zone>` (17) · `<admin-host>.<ops-zone>` (25) · `<waker-host>.<ops-zone>` (24) |
| **Named live stack FQDNs** | Throughout | `<stack-name>.sg-compute.<zone>` (32), `<stack-name>…` (12), `<stack-name>.<zone>` (19), `<stack-name>.<vault-zone>` (10), `<demo-slug>.<ops-zone>` (54). **`<demo-slug>` is a demo slug alongside `<demo-slug>`/`<demo-slug>`, not a customer — but it reads like a person's name. Drop it.** |
| **Real EC2 and AMI IDs** | `utils/ec2_boot_bench/ec2_boot_bench_results.csv` — 16 rows, `i-<redacted>` etc., AMIs `ami-<redacted>`, `ami-<redacted>`, `ami-<redacted>` | Instances are long terminated; AMIs are likely private. **Publish the timings, strip the IDs** — see `05__` §3 |
| **Internal CDN hosts** | `<dev>.<tools-zone>` (177), `<tools-zone>` (29) | Hardcoded in shipped web components |

**Practical rule:** the site publishes **shapes, not addresses**. `<stack-name>.sg-compute.<zone>` is documentation; `<stack-name>.sg-compute.<zone>` is a target. Add both the account ID and the hostname list to the CI key-leak check so this cannot regress.

---

## 3. Do not publish

Standard estate list, plus one specific to this repo:

- `library/alchemist/materials/` — the whole tree. Investment figures, valuation, competitive positioning.
- `team/humans/dinis_cruz/briefs/07/12/positioning-and-market/` — competitor maps.
- `team/roles/appsec/reviews/02/21/v0.5.0__review__pki-architecture-security-revised.md` — already classified: *"publishing an attack roadmap for live code."*
- `team/roles/grc/reviews/02/19/` — names a private individual with signature blocks.
- `library/sgraph-send/dev_packs/v0.32.1__vault-to-vault-append-comms/03__provisioning-and-topologies.md` — names the driving rollout customer.
- **Anything in `claude-code-web/` without a redaction pass.** It is the densest source of the account ID and live hostnames, and it is also where much of the operational detail lives — so it is a *redact-and-use* tree, not a skip tree.

---

## 4. The security disclosure — how to publish it

`EC2__Platform.create_node` writes the per-node API key into an EC2 tag:

```python
if node_info.instance_id:                          # tag so dashboard can read key without SSM
    EC2__Launch__Helper().add_tags(region, str(node_info.instance_id),
                                   [{'Key': 'sg-compute:host-api-key', 'Value': api_key}])
```

And the codebase already documents the consequence — `Schema__Playwright__Info.py:22`: *"**Visible to anyone with `ec2:DescribeInstances`.**"*

**The facts, stated fairly:**

- The key is **also** in SSM, which is the correct store. The tag is a **dashboard convenience** with a comment saying exactly that.
- **No live key is exposed in the repo.** This is a design trade-off, not a leak.
- The blast radius is bounded: the key is **per-node and never reused**, and nodes self-terminate on a default one-hour timer.
- The reader who can exploit it already has `ec2:DescribeInstances` in the account — which is a meaningful IAM position, though a very commonly granted one.

**The recommended framing:** publish it, in `/shipped/` or a `/security/` page, as a **known trade-off with a named mitigation path** — read the key from SSM in the dashboard, drop the tag, accept the extra call. A platform site that documents its own trade-offs is trusted; one that omits a weakness its own source code comments on is not, and the code is public either way.

**Do not** frame it as a vulnerability disclosure, and do not publish an exploitation path. It is an architecture note.

---

## 5. Network boundaries

| Site | Owns | Boundary with this site |
|---|---|---|
| **`sg-compute.sgit.ai`** | The compute platform, specs, nodes, pods, the API, the rename | — |
| `sgit.ai` | The vault product, the catalogue, the demos | **The `/pw` reverse proxy is vendored into `diniscruz/sg-send-vault` and is in neither repo** (`01__` §4). Whoever documents the production auth path documents a component they cannot see. Coordinate |
| `open-source.sgit.ai` | The open-source position | Apache-2.0, the PyPI packages, and *"somebody has to be the villagers"* — this platform **is** NFR maintenance made concrete. Cross-link |
| `wardley-maps.sgit.ai` | Mapping | The cold-start ladder is a de-facto evolution axis, and the substrate spectrum is a map waiting to be drawn. One link each way |
| `standards.sgit.ai` | Instruments | Nitro Enclave attestation is an evidence artefact. Light link |
| `nhi.sgit.ai`, `sg-sentinel.sgit.ai` | NHI, sentinel | The per-node key, the JS allowlist and least-privilege-by-declaration are NHI subject matter. Cross-link |
| `risks.sgit.ai` | Risk | The EC2-tag trade-off (§4) is a worked example of an accepted risk with a named acceptor. Good link |

**And the domain rule, restated because it will be asked constantly:** `sg-compute.sgit.ai` is documentation; `sg-compute.sgraph.ai` is the live Route 53 zone serving per-node DNS. Say it on the front page and in `/network/`. `02__` §5.

---

## 6. House style

- **Code wins.** Where the README, `capabilities.json`, the reality doc and the tree disagree, the tree is right. State the policy once and apply it everywhere.
- **Every number on the site is generated or dated.** If it cannot be regenerated at build time, it carries the date it was measured.
- **Shapes, not addresses.** `<stack-name>.sg-compute.<zone>`, never a live FQDN.
- **Publish failures with successes.** The seven capacity failures, the four failing tests, the broken guard, the dead workflow. This repo's own reality-document discipline already says *"briefs are aspirations, not facts"* — inherit it.
- **-ise, not -ize**, to match the estate.

---

This document is released under the Creative Commons Attribution 4.0 International licence (CC BY 4.0).

---

*Published on sg-compute.sgit.ai under CC BY 4.0. Source: the `sg-compute.sgit.ai` brief pack v0.33.62, 24 August 2026, by Dinis Cruz via the SG/Send Librarian, with AI co-authorship (Claude, Anthropic).*
