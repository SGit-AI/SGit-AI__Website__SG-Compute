# 04 — The spec system: what makes it a platform

**This is the page that justifies the rename.** One abstraction, sixteen implementations, three generalisation mechanisms, and a documented path for specs that live outside the repo. Full data in `specs__catalogue.json`.

---

## 1. The catalogue

Seventeen directories; **sixteen registered** (`sg_edge` has no `manifest.py` and is therefore invisible to the registry — see §5).

| Spec | LOC | Capability | Boot | Stability | Family |
|---|---:|---|---:|---|---|
| **vault_publish** | 11,682 | vault-writes, subdomain-routing | 45s | EXPERIMENTAL | vault |
| **playwright** | 10,180 | browser-automation | 30s | **STABLE** | browser |
| *sg_edge* | *9,108* | *— unregistered —* | — | — | infra |
| **vault_app** | 8,261 | vault-writes | 45s | EXPERIMENTAL | vault |
| **content_proxy** | 4,971 | mitm-proxy | 600s | EXPERIMENTAL | browser |
| **firefox** | 1,992 | mitm-proxy | 90s | EXPERIMENTAL | browser |
| **vnc** | 1,876 | mitm-proxy | 120s | **STABLE** | browser |
| **docker** | 1,558 | container-runtime | 600s | **STABLE** | runtime |
| **local_claude** | 1,498 | llm-inference | 180s | EXPERIMENTAL | llm |
| **mitmproxy** | 1,448 | mitm-proxy | 15s | **STABLE** | network |
| **elastic** | 1,372 | metrics | 180s | **STABLE** | observability |
| **prometheus** | 1,311 | metrics | 120s | **STABLE** | observability |
| **opensearch** | 1,221 | metrics | 180s | **STABLE** | observability |
| **podman** | 1,199 | container-runtime | 120s | **STABLE** | runtime |
| **neko** | 1,180 | iframe-embed | 120s | **STABLE** | browser |
| **ollama** | 939 | llm-inference | 120s | EXPERIMENTAL | llm |
| **open_design** | 773 | design-tool | 480s | EXPERIMENTAL | tool |

**Nine stable, seven experimental.** Boot times span 15 seconds (mitmproxy) to 600 seconds (docker, content_proxy) — a 40× range, which is itself a good argument for the manifest carrying `boot_seconds_typical` as a field rather than a footnote.

**These are not documents.** Each is a working package with `manifest.py`, `api/routes/`, `cli/`, `service/`, `schemas/`, `tests/`, and often `ui/`.

---

## 2. Three mechanisms, and none of them is `capabilities.json`

### (a) `manifest.py` — the registry

Every spec exposes a typed `MANIFEST` of `Schema__Spec__Manifest__Entry`:

```
spec_id · display_name · icon · version · stability · boot_seconds_typical
capabilities · nav_group · extends · soon · create_endpoint_path
```

> *"**Single source of truth.** Every spec's `manifest.py` exposes `MANIFEST`."*

This is where the 30 April brief's criterion 5 was **deliberately improved on** — it asked for specs stored as JSON with a `spec.json`; what shipped is typed Python with a schema. Better, and the site should say so rather than scoring it as a miss.

### (b) `Spec__Routes__Loader` — convention-based discovery

`spec_id 'docker'` resolves to `sg_compute_specs.docker.api.routes.Routes__Docker__Stack`. No registration list, no import graph to maintain.

And a design note worth publishing because it cuts both ways: *"**Specs without a route class are silently skipped.**"* Convenient during development; a silent-failure mode in production. A spec that loses its route class disappears from the API with no error.

### (c) `Spec__CLI__Builder` — generated CLIs

**Per-spec CLIs are generated, not written.** The builder registers a uniform verb set for every spec:

```
list · info · create · wait · health · connect · exec · delete · ami list|bake · cert
```

Sixteen specs, one CLI surface, written once. This is the strongest single argument that the thing is a platform: **adding a spec costs a manifest, a route class and a service — the CLI comes free.**

### (d) Entry points — specs outside the repo

`Spec__Loader` already supports **PEP 621 entry-point discovery** under the group `sg_compute.specs`, alongside the in-repo walk. The 30 April *"Spec Standard: External Repos"* brief specified it.

**Third-party specs are architecturally supported and untested in the wild.** That is a genuinely interesting claim and it should be published as a claim, not a feature — with an invitation to try it.

### ⚠️ What is *not* the mechanism

`capabilities.json`:

```json
{ "app": "sg-playwright", "version": "v0.1.29",
  "axioms": ["statelessness", "least-privilege-by-declaration", "self-description"],
  "declared_narrowing": [] }
```

**Frozen at v0.1.29 while the repo is at v0.2.71 — 42 minor versions.** It is `COPY`'d into the image and served verbatim at `GET /admin/capabilities`, and **the repo's own documentation says not to read it**:

> *"The UI reads `GET /health/capabilities` (the live `Schema__Service__Capabilities`, populated by `Capability__Detector`) — **never** the stale `capabilities.json`."*

The live mechanism is `Capability__Detector`, which detects the deployment target from environment variables (`laptop | ci | claude_web | container | lambda`) and builds capabilities at runtime. **Present that as the self-description story; mention `capabilities.json` only as a known-stale artefact, or delete it.**

The three axioms it names — *statelessness, least-privilege-by-declaration, self-description* — are good, and they are actually implemented (`01__` §1, the JS allowlist, `/health/capabilities`). **Rescue the axioms from the stale file and put them on the front page.**

---

## 3. What this makes possible — and what it does not yet

**Possible today.** Sixteen ready-to-launch environments, each with a typed manifest, a stability rating, a measured boot time, a generated CLI and auto-discovered routes. The 30 April brief's own framing:

> *"This is the **simulated AWS Marketplace**: a catalogue of pre-configured, ready-to-launch environments."*

That is exactly what `/specs/` should be, and it is real.

**Not yet, and the site must say so:**

- **`create_node` covers 3 of 16 specs.** `EC2__Platform._service_for` raises `NotImplementedError` for anything but `docker`, `podman`, `vnc`. The other thirteen create nodes through their own CLI and service paths, not the control-plane API. **The uniform CLI is real; the uniform API is not.**
- **One platform.** `Platform.name` is documented as `'ec2' | 'k8s' | 'gcp' | 'local'`. Only EC2 exists.
- **No multi-node stacks.** `Routes__Compute__Stacks` returns a list; `Cli__Compute__Stack` is unwired.
- **`sg_edge` is unregistered** — 9,108 lines, the second-largest spec directory, and invisible to the registry because it has no `manifest.py`. Either register it or move it out of `sg_compute_specs/`; leaving the largest unregistered thing inside the spec tree is confusing for anyone reading the catalogue.

---

## 4. Why the family view matters more than the list

Grouped by what they actually do:

| Family | Specs | LOC |
|---|---|---:|
| **browser** | playwright, content_proxy, firefox, vnc, neko | 20,199 |
| **vault** | vault_publish, vault_app | 19,943 |
| **observability** | elastic, prometheus, opensearch | 3,904 |
| **runtime** | docker, podman | 2,757 |
| **llm** | local_claude, ollama | 2,437 |
| **network** | mitmproxy | 1,448 |
| **tool** | open_design | 773 |

**Vault specs are within 300 lines of browser specs.** That single row is the clearest possible statement that this is not a browser service — and it points at the integration the rest of the estate wants: vault-writes as a first-class capability, already implemented twice.

It also explains why the artefact-sink gap (`01__` §6) matters more than it looks. Two specs exist whose capability is literally `vault-writes`, and the generic artefact writer's vault path raises `NotImplementedError`. **The capability exists at the spec layer and not at the platform layer.** That is `08__` Q4.

---

## 5. How to write `/specs/`

1. **One page per spec**, generated from `manifest.py` — the manifest already carries everything a page needs. Do not hand-write sixteen pages that will drift.
2. **Lead with the family view**, not the alphabetical list.
3. **Show stability and boot time in the header**, because they are what a reader is actually choosing on.
4. **State the `create_node` gap per spec** — three of sixteen is a real limitation and hiding it produces support questions.
5. **Publish the entry-point contract** as an invitation: here is how a spec that lives in your repo joins this catalogue.
6. **Generate the page from the tree, at build time.** Every stale artefact in this repo became stale because it was written once by hand.

---

This document is released under the Creative Commons Attribution 4.0 International licence (CC BY 4.0).

---

*Published on sg-compute.sgit.ai under CC BY 4.0. Source: the `sg-compute.sgit.ai` brief pack v0.33.62, 24 August 2026, by Dinis Cruz via the SG/Send Librarian, with AI co-authorship (Claude, Anthropic).*
