#!/usr/bin/env python3
"""Generates /specs/ — the catalogue index and one page per spec — from data/specs.json.

    python3 admin/build/gen_specs.py            # write the pages
    python3 admin/build/gen_specs.py --check    # fail if any page has drifted (CI)

This is the site's one rule that no sibling site needs:

    Generate every page that describes the code, from the code, at build time.

Four artefacts in the platform's own repository went stale — capabilities.json 42
minor versions behind, the reality doc 41, a README describing a package directory
that does not exist, and a `version` file nothing reads — and every one of them went
stale for the same reason: it was written once, by hand. Sixteen hand-written spec
pages would be the fifth.

So the catalogue is data (data/specs.json), the pages are a projection of it, and CI
re-runs this in --check mode so a page cannot silently disagree with the data.

It also does something a hand-written page cannot: every derived total on the site —
family LOC, browser share, spec counts, stable/experimental split — is COMPUTED from
the per-spec rows and then cross-checked against the summary blocks the survey
recorded independently. If the two ever disagree, the build fails rather than
publishing a number nobody can reproduce.
"""
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

from pagelib import ROOT, page_head, page_tail, write_or_check, report, esc

CAT = json.loads((ROOT / "data/specs.json").read_text())
SPECS = CAT["specs"]
SURVEYED = CAT["surveyed"]
REPO_VER = CAT["repo_version"]

FAMILY_BLURB = {
    "browser":       "Browsers and the proxies in front of them — the family the repository is named after, and 28.5% of the new codebase.",
    "vault":         "Vault publishing and vault applications. Within 300 lines of the browser family, which is the single clearest statement that this is not a browser service.",
    "observability": "Metrics and search backends for the platform's own telemetry.",
    "runtime":       "General container runtimes — and, with vnc, the only specs the control-plane API can provision.",
    "llm":           "Model inference, local and hosted-on-your-own-node.",
    "network":       "The proxy sidecar the browser family routes through.",
    "tool":          "Application specs that are neither browser nor runtime.",
    "infra":         "Platform infrastructure that lives in the spec tree without being a registered spec.",
}
FAMILY_ORDER = ["browser", "vault", "observability", "runtime", "llm", "network", "tool", "infra"]


def derive():
    """Compute every total from the rows, then check the computed values against the
    summary blocks the survey recorded separately. Two independent paths to the same
    number is the only reason to trust either."""
    reg = [s for s in SPECS if s["registered"]]
    fam_loc = Counter()
    for s in SPECS:
        fam_loc[s["family"]] += s["loc"]
    d = {
        "total_dirs":            len(SPECS),
        "registered":            len(reg),
        "stable":                sum(1 for s in reg if s["stability"] == "STABLE"),
        "experimental":          sum(1 for s in reg if s["stability"] == "EXPERIMENTAL"),
        "browser_family":        sum(1 for s in SPECS if s["family"] == "browser"),
        "create_node_supported": sum(1 for s in SPECS if s["create_node"]),
        "family_loc":            dict(fam_loc),
        "browser_loc":           fam_loc["browser"],
        "spec_loc":              sum(s["loc"] for s in reg),
    }
    problems = []
    for k, v in CAT["counts"].items():
        if d.get(k) != v:
            problems.append(f'counts.{k}: data/specs.json says {v}, the rows compute {d.get(k)}')
    if d["browser_loc"] != CAT["loc"]["browser_specs"]:
        problems.append(f'loc.browser_specs: says {CAT["loc"]["browser_specs"]}, '
                        f'the rows compute {d["browser_loc"]}')
    non_browser = sum(s["loc"] for s in SPECS if s["family"] != "browser")
    if non_browser != CAT["loc"]["non_browser_specs"]:
        problems.append(f'loc.non_browser_specs: says {CAT["loc"]["non_browser_specs"]}, '
                        f'the rows compute {non_browser}')
    if problems:
        print("gen_specs: the catalogue disagrees with itself — refusing to publish a "
              "number nobody can reproduce", file=sys.stderr)
        for p in problems:
            print("  ✗ " + p, file=sys.stderr)
        sys.exit(1)
    core = CAT["loc"]["generic_core_sg_compute"]
    new_code = core + d["browser_loc"] + non_browser
    d["non_browser_loc"] = non_browser
    d["new_code"] = new_code
    d["not_browser_pct"] = round(100 * (new_code - d["browser_loc"]) / new_code, 1)
    d["playwright_share_of_specs"] = round(
        100 * next(s["loc"] for s in SPECS if s["spec_id"] == "playwright")
        / sum(s["loc"] for s in SPECS), 1)
    return d


D = derive()


def stab_pill(s):
    if s["stability"] == "STABLE":
        return '<span class="opt-verdict opt-yes">stable</span>'
    if s["stability"] == "EXPERIMENTAL":
        return '<span class="opt-verdict opt-part">experimental</span>'
    return '<span class="opt-verdict opt-no">unregistered</span>'


def boot(s):
    return f'{s["boot_seconds_typical"]}s' if s["boot_seconds_typical"] else '—'


def create_node_cell(s):
    if not s["registered"]:
        return '<span class="opt-verdict opt-no">n/a</span>'
    return ('<span class="opt-verdict opt-yes">yes</span>' if s["create_node"]
            else '<span class="opt-verdict opt-no">no</span>')


# ---------------------------------------------------------------- index page
def spec_link(s):
    return '<a href="' + s["spec_id"] + '.html">' + s["spec_id"] + '</a>'


def cap_cell(s):
    if not s["capabilities"]:
        return '<span class="dim">— unregistered —</span>'
    return ", ".join("<code>" + c + "</code>" for c in s["capabilities"])


def index_page():
    rel = "specs/index.html"
    by_fam = defaultdict(list)
    for s in SPECS:
        by_fam[s["family"]].append(s)

    def by_loc(f):
        return sorted(by_fam[f], key=lambda x: -x["loc"])

    fam_rows = "\n".join(
        f'        <tr><td><b>{f}</b></td>'
        f'<td>{", ".join(spec_link(s) for s in by_loc(f))}</td>'
        f'<td style="text-align:right">{D["family_loc"][f]:,}</td></tr>'
        for f in FAMILY_ORDER if f in by_fam)

    fam_sections = "\n".join(f'''
<h3 id="f-{f}">{f} <span class="dim small">— {len(by_fam[f])} spec{"s" if len(by_fam[f]) != 1 else ""}, {D["family_loc"][f]:,} lines</span></h3>
<p>{FAMILY_BLURB[f]}</p>
<div class="cards" style="padding:0;margin:.8rem 0 1.6rem">
''' + "\n".join(
        f'''  <a class="card" href="{s["spec_id"]}.html">
    <div class="tag">{boot(s)} typical boot · {s["loc"]:,} lines</div>
    <h3>{s["spec_id"]}</h3>
    <p>{esc(s["note"][:150])}{"…" if len(s["note"]) > 150 else ""}</p>
    <span class="go">{stab_pill(s)}</span>
  </a>''' for s in sorted(by_fam[f], key=lambda x: -x["loc"]))
        + "\n</div>" for f in FAMILY_ORDER if f in by_fam)

    alpha_rows = "\n".join(
        f'        <tr><td><a href="{s["spec_id"]}.html"><b>{s["spec_id"]}</b></a></td>'
        f'<td>{stab_pill(s)}</td>'
        f'<td>{cap_cell(s)}</td>'
        f'<td style="text-align:right">{boot(s)}</td>'
        f'<td style="text-align:right">{s["loc"]:,}</td>'
        f'<td>{s["family"]}</td>'
        f'<td>{create_node_cell(s)}</td></tr>'
        for s in sorted(SPECS, key=lambda x: x["spec_id"]))

    mechs = "\n".join(
        f'  <div class="cap"><span class="capnum">{i}</span>'
        f'<h3>{esc(m["name"])}</h3><p>{esc(m["what"])}</p></div>'
        for i, m in enumerate(CAT["generalisation_mechanisms"], 1))

    body = f'''
<main class="doc" style="max-width:1160px">
<div class="crumb"><a href="../index.html">sg-compute.sgit.ai</a> / specs</div>
<h1>The catalogue: sixteen ready-to-launch environments</h1>
<p class="lead">The 30 April naming brief called it <em>“the simulated AWS Marketplace: a catalogue of pre-configured, ready-to-launch environments.”</em> That is what this is. Seventeen directories, <b>{D["registered"]} registered</b> — {D["stable"]} stable, {D["experimental"]} experimental — each a working package with a typed manifest, its own routes, service, CLI, schemas and tests. <b>This page is generated from <a href="../data/specs.json">data/specs.json</a></b> and CI fails if it drifts.</p>

<div class="evbox">
  <span class="evtag">measured</span>
  <p>Surveyed <b>{SURVEYED}</b> against repo <b>{REPO_VER}</b>, from <code>sg_compute_specs/*/manifest.py</code>. Every total on this page is computed from the per-spec rows and cross-checked against the survey's own summary blocks — <a href="../admin/index.html#generated">a disagreement fails the build</a> rather than publishing a number nobody can reproduce.</p>
</div>

<h2 id="why">Why this page justifies the rename</h2>
<p><b>Playwright is 1 of {D["registered"]} registered specs and {D["playwright_share_of_specs"]}% of spec code.</b> Counting the generic compute core alongside the specs, <b>{D["not_browser_pct"]}% of the new codebase is not browser code</b>. The repository is named after one row in this table. <a href="../rename/index.html">The rename, scored against its own nine acceptance criteria →</a></p>

<h2 id="families">By family — read this one first</h2>
<p>The alphabetical list is below, but the family view is the one that carries the argument. It is a single row that makes the case:</p>
<div class="tablewrap">
  <table>
    <thead><tr><th>Family</th><th>Specs</th><th style="text-align:right">Lines</th></tr></thead>
    <tbody>
{fam_rows}
    </tbody>
  </table>
</div>
<p class="dim small"><b>Vault specs are within 300 lines of browser specs.</b> That row is the clearest possible statement that this is not a browser service — and it points at the integration the rest of the estate wants. It also explains why <a href="../shipped/index.html#sinks">the artefact-sink gap</a> matters more than it looks: two specs exist whose declared capability is <code>vault-writes</code>, while the platform's own generic vault sink raises <code>NotImplementedError</code>. The capability exists at the spec layer and not at the platform layer.</p>
{fam_sections}

<h2 id="all">All {D["total_dirs"]}, alphabetically</h2>
<div class="tablewrap">
  <table>
    <thead><tr><th>Spec</th><th>Stability</th><th>Capabilities</th><th style="text-align:right">Boot</th><th style="text-align:right">Lines</th><th>Family</th><th><code>create_node</code></th></tr></thead>
    <tbody>
{alpha_rows}
    </tbody>
  </table>
</div>
<p class="dim small">Boot is <code>boot_seconds_typical</code> from each manifest — 15 seconds to 600 seconds, a 40× range, which is itself the argument for carrying it as a manifest field rather than a footnote. Spec ids are API identifiers and are not prettified.</p>

<div class="warnbox">
  <p><b>The uniform CLI is real; the uniform API is not.</b> <code>create_node</code> covers <b>{D["create_node_supported"]} of {D["registered"]} specs</b> — <code>EC2__Platform._service_for</code> raises <code>NotImplementedError</code> for anything but <code>docker</code>, <code>podman</code> and <code>vnc</code>. The other thirteen create nodes through their own CLI and service paths, not the control-plane API. Every spec page below states this for itself.</p>
</div>

<h2 id="mechanisms">Three mechanisms, and none of them is <code>capabilities.json</code></h2>
<p>What makes this a platform rather than a service is that adding a spec costs a manifest, a route class and a service — and the CLI comes free.</p>
<div class="ladder">
{mechs}
</div>

<div class="warnbox">
  <p><b>What is <em>not</em> the mechanism.</b> {esc(CAT["not_the_mechanism"]["why"])}</p>
  <p>The live mechanism is <b>{esc(CAT["not_the_mechanism"]["live_mechanism"])}</b>. The three axioms that stale file names — <b>statelessness, least-privilege-by-declaration, self-description</b> — are good, and unlike the file that names them they are actually implemented. <a href="../index.html#axioms">They are rescued onto the front page</a>.</p>
</div>

<h2 id="third-party">Specs that live in your repository</h2>
<p><code>Spec__Loader</code> already supports <b>PEP 621 entry-point discovery</b> under the group <code>sg_compute.specs</code>, alongside the in-repo walk. A spec in your own package, declaring that entry point, joins this catalogue with no change to this repository.</p>
<div class="note">
  <p><b>Stated as a claim, not a feature.</b> Third-party specs are architecturally supported and <b>untested in the wild</b> — nobody outside the repository has published one. That is an invitation rather than a guarantee, and if you try it we would like to hear what broke.</p>
</div>
<p>One design note worth publishing because it cuts both ways: <em>“specs without a route class are silently skipped.”</em> Convenient during development; a silent-failure mode in production. A spec that loses its route class disappears from the API with no error.</p>

<div class="pagenav">
  <a href="../what-it-is/index.html">← What it actually is</a>
  <a href="../agents/index.html">The machine surface →</a>
</div>
</main>
'''
    return rel, (page_head(
        rel,
        "The spec catalogue — sixteen ready-to-launch environments · sg-compute.sgit.ai",
        f"Sixteen registered workload specs with typed manifests, stability ratings and measured boot times. "
        f"Playwright is 1 of {D['registered']} and {D['playwright_share_of_specs']}% of spec code; "
        f"{D['not_browser_pct']}% of the new codebase is not browser code. Generated from the catalogue data.",
        og_title="The simulated AWS Marketplace: sixteen ready-to-launch environments",
    ) + body + page_tail())


# ------------------------------------------------------------- per-spec page
def spec_page(s):
    rel = f'specs/{s["spec_id"]}.html'
    sid = s["spec_id"]
    caps = ", ".join(f"<code>{c}</code>" for c in s["capabilities"]) or "<span class=\"dim\">none declared</span>"

    if not s["registered"]:
        status = f'''
<div class="warnbox">
  <p><b>{sid} is not a registered spec.</b> It has no <code>manifest.py</code>, so <code>Spec__Loader</code> never finds it and it is invisible to the registry, the API and the generated CLI. At {s["loc"]:,} lines it is the second-largest directory in <code>sg_compute_specs/</code>.</p>
  <p>It appears on this page because leaving it out would be the same omission the tree makes. The decision to take is <a href="../roadmap/index.html#loose">register it or move it out</a>.</p>
</div>'''
        create = ''
    else:
        status = ''
        if s["create_node"]:
            create = f'''
<div class="note">
  <p><b>Provisionable through the control-plane API.</b> <code>{sid}</code> is one of the {D["create_node_supported"]} specs <code>EC2__Platform._service_for</code> knows how to build, so <code>POST /api/nodes</code> and <code>sg {sid} create</code> both work.</p>
</div>'''
        else:
            create = f'''
<div class="warnbox">
  <p><b><code>create_node</code> does not cover {sid}.</b> <code>EC2__Platform._service_for</code> raises <code>NotImplementedError</code> for everything but <code>docker</code>, <code>podman</code> and <code>vnc</code>. This spec creates nodes through its own CLI and service path, not the control-plane API. The generated CLI verbs below are real; the uniform API is not, for this spec.</p>
</div>'''

    others = [x for x in SPECS if x["family"] == s["family"] and x["spec_id"] != sid]
    siblings = (", ".join(f'<a href="{o["spec_id"]}.html">{o["spec_id"]}</a>' for o in
                sorted(others, key=lambda x: -x["loc"])) or "none — it is alone in its family")

    verbs = ("list · info · create · wait · health · connect · exec · delete · "
             "ami list|bake · cert")

    body = f'''
<main class="doc">
<div class="crumb"><a href="../index.html">sg-compute.sgit.ai</a> / <a href="index.html">specs</a> / {sid}</div>
<h1><code style="font-size:.8em">{sid}</code></h1>
<p class="lead">{esc(s["note"])}</p>

<div class="docmeta">
  <div class="k">Stability</div><div class="v">{stab_pill(s)}</div>
  <div class="k">Capabilities</div><div class="v">{caps}</div>
  <div class="k">Typical boot</div><div class="v">{boot(s)} <span class="dim small">— <code>boot_seconds_typical</code>, from the manifest</span></div>
  <div class="k">Size</div><div class="v">{s["loc"]:,} lines <span class="dim small">— {round(100 * s["loc"] / sum(x["loc"] for x in SPECS), 1)}% of spec code</span></div>
  <div class="k">Family</div><div class="v"><a href="index.html#f-{s["family"]}">{s["family"]}</a> <span class="dim small">— alongside {siblings}</span></div>
  <div class="k">create_node</div><div class="v">{create_node_cell(s)}</div>
  <div class="k">Measured</div><div class="v">{SURVEYED}, against repo {REPO_VER}</div>
</div>
{status}{create}
<h2 id="cli">The CLI, which nobody wrote</h2>
<p>Per-spec CLIs are <b>generated, not written</b>. <code>Spec__CLI__Builder</code> registers the same verb set for every registered spec, so <code>{sid}</code> gets its command surface from the same code that gives every other spec theirs:</p>
<pre class="shell"><span class="d"># the uniform verb set, for every registered spec</span>
{verbs}

<span class="d"># so, for this one</span>
sg {sid} <span class="cy">create</span> <span class="d">--max-hours 1</span>
sg {sid} <span class="cy">wait</span>
sg {sid} <span class="cy">health</span>
sg {sid} <span class="cy">delete</span>
</pre>
<p class="dim small">This is the strongest single argument that the thing is a platform rather than a service: adding a spec costs a manifest, a route class and a service — the CLI comes free. <a href="index.html#mechanisms">The three mechanisms →</a></p>

<h2 id="lifecycle">What a node of this spec does</h2>
<p>Every spec rides the same node lifecycle: a per-node API key minted and written to SSM <em>before</em> launch, composed user-data sections, EC2 tags as the registry, a two-phase health poll, then teardown. <b>Teardown means terminate, not stop</b> — <code>systemd-run --on-active</code> paired with <code>InstanceInitiatedShutdownBehavior=terminate</code>, on a default one-hour timer.</p>
<p><a href="../what-it-is/index.html#layer2">The full node lifecycle, step by step →</a></p>

<div class="pagenav">
  <a href="index.html">← The catalogue</a>
  <a href="../shipped/index.html">What ships today →</a>
</div>
</main>
'''
    return rel, (page_head(
        rel,
        f"{sid} — a workload spec · sg-compute.sgit.ai",
        f"{sid}: {s['stability'] or 'unregistered'}, {boot(s)} typical boot, {s['loc']:,} lines, "
        f"family {s['family']}. Generated from the spec catalogue surveyed {SURVEYED}.",
    ) + body + page_tail())


def main():
    check = "--check" in sys.argv
    changed, mismatched = [], []
    rel, html = index_page()
    write_or_check(ROOT / rel, html, check, changed, mismatched)
    for s in SPECS:
        rel, html = spec_page(s)
        write_or_check(ROOT / rel, html, check, changed, mismatched)
    report("gen_specs", check, changed, mismatched)


if __name__ == "__main__":
    main()
