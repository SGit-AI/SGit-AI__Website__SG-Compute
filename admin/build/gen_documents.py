#!/usr/bin/env python3
"""Generates /documents/ — the reader page for each source brief — from data/documents.json.

    python3 admin/build/gen_documents.py            # write the pages
    python3 admin/build/gen_documents.py --check    # fail if any page has drifted (CI)

The raw markdown under briefs/ is the source of truth. These pages are presentation:
each one renders its brief in-page from the raw file via assets/mdreader.js, and if
that fails for any reason the page falls back to a link to the raw markdown, so a
document is never unreachable.

Two of the briefs are published redacted — 07 and 10 are the redaction list itself,
so they named every live address they told the site to strip. Their reader pages say
so above the document rather than leaving a reader to notice the angle brackets.
"""
import json
import sys

from pagelib import ROOT, page_head, page_tail, write_or_check, report, esc

DATA = json.loads((ROOT / "data/documents.json").read_text())
DOCS = DATA["documents"]
PAGES = [d for d in DOCS if d["page"]]

KIND_LABEL = {
    "brief":   ("commission", "The document this site was commissioned by"),
    "source":  ("source", "A source brief, captured verbatim"),
    "licence": ("licence", "The licence and redaction rules this site publishes under"),
    "data":    ("data", "Machine-readable"),
}
REDACTED = {"07__boundaries-and-security.md", "10__licence-and-redaction.md"}

MARKED = ('\n<script src="https://cdn.jsdelivr.net/npm/marked@12/marked.min.js"></script>'
          '\n<script src="../assets/mdreader.js" defer></script>')


def reader_page(d, prev_d, next_d):
    rel = f'documents/{d["page"]}'
    tag, tagline = KIND_LABEL[d["kind"]]
    redacted = d["file"] in REDACTED

    notice = ''
    if redacted:
        notice = '''
<div class="warnbox">
  <p><b>Published redacted.</b> This document is the redaction list, so it named every live address it told the site to strip. It is published under its own rule — <em>shapes, not addresses</em> — with the AWS account id, the live internal hostnames, the named stack FQDNs and the real EC2 and AMI ids each replaced by the shape they are an instance of. Nothing else was changed, and <a href="../admin/index.html#leak">the site's leak tripwire encodes the same list</a> so it cannot regress.</p>
</div>'''

    nav_prev = (f'<a href="{prev_d["page"]}">← {esc(prev_d["title"])}</a>' if prev_d
                else '<a href="index.html">← All documents</a>')
    nav_next = (f'<a href="{next_d["page"]}">{esc(next_d["title"])} →</a>' if next_d
                else '<a href="../briefs/11__source-manifest.csv">The source manifest →</a>')

    body = f'''
<main class="doc">
<div class="crumb"><a href="../index.html">sg-compute.sgit.ai</a> / <a href="index.html">documents</a> / {esc(d["title"])}</div>
<h1>{esc(d["title"])}</h1>
<p class="lead">{esc(d["blurb"])}</p>

<div class="docmeta">
  <div class="k">Kind</div><div class="v">{tagline}</div>
  <div class="k">Length</div><div class="v">{d["words"]:,} words</div>
  <div class="k">Raw source</div><div class="v"><a href="../briefs/{d["file"]}"><code>briefs/{d["file"]}</code></a> — the source of truth; this page is presentation</div>
  <div class="k">Licence</div><div class="v">CC BY 4.0 — {esc(DATA["attribution"])}</div>
</div>
{notice}
<div class="mdread-label">
  <span>{tag}</span> · <span>briefs/{d["file"]}</span> ·
  <a href="../briefs/{d["file"]}">open the raw markdown</a>
</div>
<div class="mdread" id="mdread" data-src="../briefs/{d["file"]}"></div>

<div class="pagenav">
  {nav_prev}
  {nav_next}
</div>
</main>
'''
    return rel, (page_head(
        rel,
        f'{d["title"]} — the source documents · sg-compute.sgit.ai',
        esc(d["blurb"]),
        extra_head=MARKED,
    ) + body + page_tail())


def index_page():
    rel = "documents/index.html"
    cards = "\n".join(
        f'''  <a class="card" href="{d["page"]}">
    <div class="tag">{KIND_LABEL[d["kind"]][0]} · {d["words"]:,} words</div>
    <h3>{esc(d["title"])}</h3>
    <p>{esc(d["blurb"])}</p>
    <span class="go">Read it →</span>
  </a>''' for d in PAGES)

    def title_cell(d):
        if not d["page"]:
            return esc(d["title"])
        return '<a href="' + d["page"] + '">' + esc(d["title"]) + '</a>'

    rows = "\n".join(
        f'        <tr><td>{title_cell(d)}</td>'
        f'<td><a href="../briefs/{d["file"]}"><code>{d["file"]}</code></a></td>'
        f'<td style="text-align:right">{d["words"]:,}</td>'
        f'<td>{"<b>redacted</b>" if d["file"] in REDACTED else "verbatim"}</td></tr>'
        for d in DOCS)

    total = sum(d["words"] for d in DOCS)

    body = f'''
<main class="doc">
<div class="crumb"><a href="../index.html">sg-compute.sgit.ai</a> / documents</div>
<h1>The source documents</h1>
<p class="lead">Everything on this site is written from these {len(DOCS)} documents — {total:,} words commissioning it, and the measurements behind them. They are published in full, because a site that audits a platform should be checkable against the audit it was given.</p>

<div class="note">
  <p><b>The raw markdown is the source of truth.</b> Each reader page renders its document from the raw file in <a href="../briefs/00__brief.md">briefs/</a> at load time; if that fails, the page falls back to a link to the raw file. Nothing is transcribed by hand, so a reader page cannot say something the document does not.</p>
  <p>Every file is fetchable at a stable constructed URL: <code>/briefs/&lt;filename&gt;</code>. That is a promise, not an accident.</p>
</div>

<h2 id="read">Read them</h2>
<div class="cards" style="padding:0">
{cards}
</div>

<h2 id="all">All {len(DOCS)}, with their raw files</h2>
<div class="tablewrap">
  <table>
    <thead><tr><th>Document</th><th>Raw file</th><th style="text-align:right">Words</th><th>Published</th></tr></thead>
    <tbody>
{rows}
    </tbody>
  </table>
</div>

<h2 id="redaction">Two are redacted, and here is why</h2>
<p>The platform this site documents is <b>live infrastructure</b>. Two of the documents are the redaction list itself, so between them they named every live address the site was told to strip: an AWS account id, ten internal hostnames, five named stack FQDNs, and sixteen real EC2 instance ids with three AMI ids. Publishing them verbatim would publish exactly what they exist to prevent.</p>
<p>They are published under their own rule — <b>shapes, not addresses</b>. <code>&lt;stack-name&gt;.sg-compute.&lt;zone&gt;</code> is documentation; a live FQDN is a target. Each address was replaced by the shape it is an instance of, nothing else was changed, and <a href="../admin/index.html#leak">the site's release gate encodes the same list</a> so no future page can reintroduce one.</p>
<p>One thing is <em>not</em> redacted, deliberately: the zone <code>sg-compute.sgraph.ai</code>. This site's own label collides with it, and the stated decision is to <a href="../network/index.html#domains">claim the distinction rather than hide it</a>.</p>

<h2 id="licence">Licence</h2>
<p>All {len(DOCS)} documents, and every page of this site, are released under <b>CC BY 4.0</b>. Attribution: {esc(DATA["attribution"])}. Where the site quotes the platform's own source code, it is quoting <b>Apache-2.0</b> code — that notice is retained and the snippets do not carry this site's licence.</p>

<div class="pagenav">
  <a href="../roadmap/index.html">← Build order &amp; open questions</a>
  <a href="../admin/index.html">How this site is built →</a>
</div>
</main>
'''
    return rel, (page_head(
        rel,
        "The source documents · sg-compute.sgit.ai",
        f"The {len(DOCS)} documents this site was written from, published in full — {total:,} words. "
        "Raw markdown is the source of truth; two are redacted under their own rule.",
    ) + body + page_tail())


def main():
    check = "--check" in sys.argv
    changed, mismatched = [], []
    rel, html = index_page()
    write_or_check(ROOT / rel, html, check, changed, mismatched)
    for i, d in enumerate(PAGES):
        rel, html = reader_page(d, PAGES[i - 1] if i else None,
                                PAGES[i + 1] if i + 1 < len(PAGES) else None)
        write_or_check(ROOT / rel, html, check, changed, mismatched)
    report("gen_documents", check, changed, mismatched)


if __name__ == "__main__":
    main()
