# sg-compute.sgit.ai — an ephemeral compute platform, named after one of its sixteen specs

SG/Compute launches an isolated environment, runs the declared work, and terminates it.
Sixteen ready-to-launch workload specs — browsers, vaults, container runtimes, model
inference, observability — each a typed manifest away from a running node.

Two claims were tested against the platform's code and both hold: **the repository needs
renaming** (71.5% of the new codebase is not browser code; Playwright is 1 of 16 specs), and
**it is a genuinely mature platform** (4,785 tests passing in 81 seconds, 2,777 commits and
245 tags in 100 days, digest-first multi-arch CI, 1.27 million words of documentation).

This site publishes both — and the four places the maturity claim is overstated, the eight
things that are specified or argued and not built, and a four-character bug in the platform's
own CI guard. That is the editorial policy, not a caveat.

Live site: https://sg-compute.sgit.ai (GitHub Pages, deployed from `dev`).

## Structure

- `index.html` — front page: the guard bug, the two ephemeral layers, the axioms, the catalogue, the audit
- `what-it-is/` — the two ephemeral layers, sessions, the watchdog, isolation, artefact sinks
- `specs/` — the catalogue, **generated** from `data/specs.json`: an index plus one page per spec
- `why/` — the serverless argument, the cold-start ladder against the measured benchmarks
- `numbers/` — the measured data, including the seven capacity failures and what cannot be said about cost
- `rename/` — nine acceptance criteria scored, the breakage list, the sequencing, the domain collision
- `shipped/` — what ships and what does not, unsoftened, plus the four stale sources of truth
- `agents/` — the machine surface, the sequence language, and the correction to the auth model
- `security/` — six isolation boundaries, the deny-by-default allowlist, and the EC2-tag trade-off
- `network/` — the site network, and the `sgit.ai` versus `sgraph.ai` domain decision
- `roadmap/` — seven fixes, eight questions published unresolved, seven honest tensions
- `documents/` — the source briefs, readable in-page; **generated** from `data/documents.json`
- `briefs/` — those source documents, verbatim (two redacted under their own rule)
- `about/participant.html` — the participant disclosure, and where our approach loses
- `admin/` — engineering: comms, release history, build tooling
- `data/` — `specs.json` and `documents.json`, the machine-readable sources every generated page reads
- `assets/site.css` — shared stylesheet (sgit.ai design language)

## The one rule no sibling site needs

> **Generate every page that describes the code, from the code, at build time.**

Four artefacts in the platform's own repository are knowingly stale, and every one went stale
because it was written once by hand. Sixteen hand-written spec pages would be the fifth. So the
catalogue is data, the pages are a projection of it, and **CI fails if a page has drifted from
its source**. Derived totals are computed from the per-spec rows and cross-checked against the
survey's own summary blocks — a disagreement fails the build rather than publishing a number
nobody can reproduce.

## Build tooling

| File | Owns |
|---|---|
| `admin/build/version.txt` | The version — single source of truth |
| `admin/build/chrome.py` | The single definition of the nav and footer, rewritten across every page |
| `admin/build/pagelib.py` | The shared page shell and the write-or-check writer |
| `admin/build/gen_specs.py` | `specs/` from `data/specs.json`, with the derived-total cross-check |
| `admin/build/gen_documents.py` | `documents/` from `data/documents.json` |
| `admin/build/gen_llms_full.py` | `llms-full.txt` from `llms.txt`, `index.md` and `briefs/` |
| `admin/build/gen_sitemap.py` | `sitemap.xml` from the tree |
| `admin/build/validate.js` | The release gate: version, links, canonical, provenance, leak tripwire |

## Release process

1. Bump `admin/build/version.txt` (vX.Y.Z, exactly once per release) and add a row to
   `admin/versions.html`; update `admin/comms.html`.
2. Regenerate the pages: `python3 admin/build/gen_specs.py` and `gen_documents.py`.
3. `python3 admin/build/chrome.py` — propagates the version badge and any nav/footer change
   to every page, generated ones included, and stamps the version into `llms.txt` and
   `index.md`.
4. Regenerate the files that read the tree and those stamped twins — **after** chrome, or they
   assemble a stale version line: `python3 admin/build/gen_llms_full.py` and `gen_sitemap.py`.
5. Validate exactly what CI runs:
   ```
   python3 admin/build/gen_specs.py     --check
   python3 admin/build/gen_documents.py --check
   python3 admin/build/gen_llms_full.py --check
   python3 admin/build/gen_sitemap.py   --check
   node admin/build/validate.js
   ```
6. `git commit -am "site vX.Y.Z: ..." && git push -u origin dev`

Every push to `dev` runs `.github/workflows/deploy-pages.yml`: validate → auto-tag
(`vX.Y.Z`, verified against `version.txt` and the commit subject, next-minor enforced) →
deploy to GitHub Pages. Pull requests run validation only. Same pipeline as
[SGit-AI__Website](https://github.com/SGit-AI/SGit-AI__Website) and
[SGit-AI__Website__PKI](https://github.com/SGit-AI/SGit-AI__Website__PKI).

## The leak tripwire

The platform documented here is **live infrastructure**, so `validate.js` fails the release if
any file in the tree contains the platform's AWS account id, any of ten live internal hostnames,
a named live stack FQDN, anything shaped like a real EC2 instance or AMI id, or anything shaped
like an sgit vault key. The rule it encodes is **shapes, not addresses**.

One deliberate exception: the bare zone `sg-compute.sgraph.ai` *is* published, because this
site's label collides with it and the stated decision is to claim the distinction rather than
move 128 references. Per-node FQDNs under that zone stay banned.

## Licence

All site content CC BY 4.0 — Dinis Cruz, with AI co-authorship (Claude, Anthropic). Where the
site quotes the platform's own source, it is quoting **Apache-2.0** code; that notice is
retained and the snippets do not carry this site's licence.
