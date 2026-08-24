#!/usr/bin/env python3
"""Generates /sitemap.xml from the tree.

    python3 admin/build/gen_sitemap.py            # write it
    python3 admin/build/gen_sitemap.py --check    # fail if it has drifted (CI)

Hand-maintained sitemaps go stale the first time somebody adds a page and forgets, and
this site has thirty-odd generated pages. So it is walked from the tree instead: every
.html file that is not under .git or .github, ordered with the front page first and the
rest alphabetically, with lastmod taken from the release date in admin/versions.html.
"""
import re
import sys
from pathlib import Path

from pagelib import ROOT, HOST

MONTHS = {m: i for i, m in enumerate(
    "Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split(), 1)}


def release_date():
    """The current release's date, from the top row of the versions table — so a page's
    lastmod is the release it shipped in rather than a filesystem mtime that changes on
    every checkout."""
    t = (ROOT / "admin/versions.html").read_text()
    m = re.search(r'class="vnum">v[\d.]+</td>\s*<td>(\d{1,2}) (\w{3}) (\d{4})</td>', t)
    if not m:
        print("gen_sitemap: no dated release row in admin/versions.html", file=sys.stderr)
        sys.exit(1)
    d, mon, y = m.groups()
    return f"{y}-{MONTHS[mon]:02d}-{int(d):02d}"


def build():
    pages = sorted(
        p.relative_to(ROOT).as_posix()
        for p in ROOT.rglob("*.html")
        if not {".git", ".github"} & set(p.relative_to(ROOT).parts))
    pages.sort(key=lambda r: (r != "index.html", r))
    day = release_date()
    rows = "\n".join(f"  <url><loc>https://{HOST}/{r}</loc><lastmod>{day}</lastmod></url>"
                     for r in pages)
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
            f'{rows}\n</urlset>\n')


def main():
    content = build()
    out = ROOT / "sitemap.xml"
    if "--check" in sys.argv:
        if not out.exists() or out.read_text() != content:
            print("gen_sitemap --check: sitemap.xml is out of date — re-run the generator",
                  file=sys.stderr)
            sys.exit(1)
        print(f"gen_sitemap --check: OK — {content.count('<url>')} pages listed")
        return
    out.write_text(content)
    print(f"gen_sitemap: wrote sitemap.xml — {content.count('<url>')} pages")


if __name__ == "__main__":
    main()
