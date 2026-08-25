#!/usr/bin/env python3
"""The single definition of this site's nav and footer, and the tool that applies it.

Run from anywhere: python3 admin/build/chrome.py

Every hand-written page is static HTML — that stays true, because a human should be
able to open any file and edit it. What is NOT hand-maintained is the chrome: the nav
row (including the version badge that validate.js requires to agree everywhere) and
the footer columns. Those are defined once here and rewritten in place across the
tree, which is what stops a forty-page site from drifting.

It also runs over the GENERATED pages (specs/, documents/), so a nav change does not
require re-running the generators — and the generators emit the same block shapes for
exactly that reason.

Adding a page: add it to NAV or FOOTER if it belongs there, write the file with any
nav/footer block at all, then run this. The block contents are replaced; the `here`
state is set from the page's own path.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
VERSION = (ROOT / "admin/build/version.txt").read_text().strip()
GH = "https://github.com/SGit-AI/SGit-AI__Website__SG-Compute"
PARENT = "https://sgit.ai"
PARENT_TITLE = ("sgit.ai — the parent project: the vault layer and the shipped CLI this "
                "compute platform provisions for")

# The nav, two levels. Each entry is (label, own page, [(sub-label, href), ...], (path prefixes)).
#
# Two rules the structure has to keep:
#   · A group label is always a link to a real page, never a menu-only stub. Nothing on
#     this site should be reachable only by opening a dropdown.
#   · `prefixes` decides the "here" state, so a page that is not itself in the nav —
#     which on this site is most of them, because specs/ and documents/ are generated
#     families — still lights up the group it belongs to.
NAV = [
    ("The platform", "what-it-is/index.html", [
        ("What it is: two ephemeral layers", "what-it-is/index.html"),
        ("The spec catalogue", "specs/index.html"),
        ("The machine surface", "agents/index.html"),
        ("Isolation &amp; the one trade-off", "security/index.html"),
    ], ("what-it-is/", "specs/", "agents/", "security/")),
    ("The argument", "why/index.html", [
        ("A serverless environment for agents", "why/index.html"),
        ("The measured numbers", "numbers/index.html"),
        ("The rename", "rename/index.html"),
    ], ("why/", "numbers/", "rename/")),
    ("Shipped", "shipped/index.html", [
        ("What ships today", "shipped/index.html"),
        ("Roadmap &amp; how to help", "roadmap/index.html"),
    ], ("shipped/", "roadmap/")),
    ("Docs", "documents/index.html", [
        ("The documents", "documents/index.html"),
        ("The catalogue as JSON", "data/specs.json"),
        ("llms.txt", "llms.txt"),
        ("llms-full.txt", "llms-full.txt"),
    ], ("documents/", "briefs/")),
    ("Site", "admin/index.html", [
        ("Comms: tasks &amp; requests", "admin/comms.html"),
        ("Release history", "admin/versions.html"),
        ("Admin &amp; engineering", "admin/index.html"),
        ("The network", "network/index.html"),
        ("Where we lose", "about/participant.html"),
    ], ("admin/", "network/", "about/")),
]

FOOTER = [
    ("The platform", [
        ("What it is", "what-it-is/index.html"),
        ("The spec catalogue", "specs/index.html"),
        ("The machine surface", "agents/index.html"),
        ("Isolation &amp; trade-offs", "security/index.html"),
    ]),
    ("The argument", [
        ("Serverless for agents", "why/index.html"),
        ("The measured numbers", "numbers/index.html"),
        ("The rename", "rename/index.html"),
    ]),
    ("Shipped", [
        ("&#8594; What ships today", "shipped/index.html"),
        ("Roadmap &amp; how to help", "roadmap/index.html"),
        ("The documents", "documents/index.html"),
        ("Where we lose", "about/participant.html"),
    ]),
    ("Site", [
        ("Comms: tasks &amp; requests", "admin/comms.html"),
        ("Release history", "admin/versions.html"),
        ("The network", "network/index.html"),
        ("llms.txt", "llms.txt"),
        ("llms-full.txt", "llms-full.txt"),
    ]),
]

BLURB = ("An ephemeral compute platform for AWS: sixteen ready-to-launch workload specs, "
         "each launched, worked and terminated in an isolated environment — with every number "
         "measured from the tree. Part of the <a href=\"https://sgit.ai\" "
         "style=\"display:inline;padding:0\"><b>sgit.ai</b></a> network. All site content "
         "CC BY 4.0; the platform's own source is Apache-2.0.")
PARTNOTE = ('⚠ Participant disclosure: published by the sgit project, which builds the platform '
            'this site documents and audits. <a href="{up}about/participant.html" '
            'style="display:inline;padding:0">Read the disclosure</a>.')
PARTNOTE_SELF = '⚠ Participant disclosure: published by the sgit project. You are on the disclosure page.'
NETLINE = ('<a href="https://sgit.ai"><b>↗ sgit.ai</b></a> — the parent project and the vault layer '
           'this provisions for · <a href="https://open-source.sgit.ai">↗ open-source.sgit.ai</a> · '
           '<a href="https://wardley-maps.sgit.ai">↗ wardley-maps.sgit.ai</a> · '
           '<a href="https://risks.sgit.ai">↗ risks.sgit.ai</a> · '
           '<a href="https://sgit.ai/network/index.html">↗ the network</a>')
# The domain decision, restated in the footer of every page, because it is the question
# this site will be asked most often. 02__ §5 / Q7.
DOMAINNOTE = ('<b>sg-compute.sgit.ai</b> is documentation. <b>sg-compute.sgraph.ai</b> is a live '
              'Route 53 zone serving per-node DNS. Same label, different TLD, stated '
              '<a href="{up}network/index.html#domains" style="display:inline;padding:0">deliberately</a>.')


def nav_html(rel, up):
    groups = []
    for label, own, subs, prefixes in NAV:
        active = rel == own or any(rel.startswith(pre) for pre in prefixes)
        links = "\n".join(
            f'      <a class="sl{" here" if href == rel else ""}" href="{up}{href}">{text}</a>'
            for text, href in subs)
        groups.append(
            f'    <div class="ni ni-has">\n'
            f'      <a class="nl{" here" if active else ""}" href="{up}{own}">{label}'
            f'<span class="caret">&#9662;</span></a>\n'
            f'      <div class="sub">\n{links}\n      </div>\n'
            f'    </div>')
    rows = "\n".join(groups)
    return (f'<nav class="site"><div class="row">\n'
            f'  <a class="brand" href="{up}index.html">sg-compute<span>.sgit.ai</span></a>\n'
            f'  <a class="parent" href="{PARENT}" title="{PARENT_TITLE}">↗ part of <b>sgit.ai</b></a>\n'
            f'  <span class="stage-pill">early access</span>\n'
            f'  <a class="ver" href="{up}admin/versions.html" title="Site release history">{VERSION}</a>\n'
            f'  <button class="nav-toggle" type="button" aria-expanded="false" aria-label="Menu">Menu</button>\n'
            f'  <div class="nav-items">\n{rows}\n  </div>\n'
            f'  <a class="gh" href="{GH}">★ GitHub</a>\n'
            f'  <script src="{up}assets/nav.js" defer></script>\n'
            f'</div></nav>')


def footer_html(rel, up):
    partnote = PARTNOTE_SELF if rel == "about/participant.html" else PARTNOTE.format(up=up)
    md_twin = f' · <a href="{up}index.md">this page as markdown</a>' if rel == "index.html" else ""
    cols = "\n".join(
        "  <div>\n"
        f"    <h4>{head}</h4>\n"
        + "\n".join(f'    <a href="{l if l.startswith("http") else up + l}">{t}</a>' for t, l in links)
        + "\n  </div>"
        for head, links in FOOTER)
    return (f'<footer class="site"><div class="cols">\n'
            f'  <div>\n'
            f'    <div class="brandline">sg-compute<span>.sgit.ai</span></div>\n'
            f'    <p>{BLURB}</p>\n'
            f'    <p class="netline">{NETLINE}</p>\n'
            f'    <p class="domainnote">{DOMAINNOTE.format(up=up)}</p>\n'
            f'    <p class="partnote">{partnote}</p>\n'
            f'    <p class="verline">site <a href="{up}admin/versions.html">{VERSION}</a> · '
            f'<a href="{up}admin/index.html">engineering</a>{md_twin}</p>\n'
            f'  </div>\n{cols}\n</div></footer>')


def stamp_text_twins():
    """The version also appears in llms.txt, llms-full.txt and index.md, and validate.js
    enforces that it agrees. Nothing used to SET it there on the sibling sites, so it was
    hand-edited every release — and hand-editing it silently missed twice. Own it here."""
    out = []
    for name, pattern, repl in [
        ("llms.txt",      r"Site version: v\d+\.\d+\.\d+", f"Site version: {VERSION}"),
        ("llms-full.txt", r"Site version: v\d+\.\d+\.\d+", f"Site version: {VERSION}"),
        ("index.md",      r"· site v\d+\.\d+\.\d+ ·",      f"· site {VERSION} ·"),
    ]:
        p = ROOT / name
        if not p.exists():
            continue
        t = p.read_text()
        t2, n = re.subn(pattern, repl, t, count=1)
        if n and t2 != t:
            p.write_text(t2)
            out.append(name)
    return out


def main():
    changed = []
    for path in sorted(ROOT.rglob("*.html")):
        if ".git" in path.parts:
            continue
        rel = path.relative_to(ROOT).as_posix()
        up = "../" * (len(path.relative_to(ROOT).parts) - 1)
        text = path.read_text()
        before = text
        text, n_nav = re.subn(r'<nav class="site">.*?</nav>', lambda _: nav_html(rel, up),
                              text, count=1, flags=re.S)
        text, n_foot = re.subn(r'<footer class="site">.*?</footer>', lambda _: footer_html(rel, up),
                               text, count=1, flags=re.S)
        if not n_nav or not n_foot:
            print(f"  ! {rel}: missing {'nav' if not n_nav else ''}"
                  f"{' and ' if not n_nav and not n_foot else ''}"
                  f"{'footer' if not n_foot else ''} block", file=sys.stderr)
        if text != before:
            path.write_text(text)
            changed.append(rel)
    changed += stamp_text_twins()
    print(f"chrome: {VERSION} applied — {len(changed)} file(s) updated")
    for c in changed:
        print(f"  · {c}")


if __name__ == "__main__":
    try:
        main()
    except BrokenPipeError:
        sys.stdout = None
