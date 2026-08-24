#!/usr/bin/env python3
"""Shared plumbing for this site's page generators.

Two generators use it — gen_specs.py and gen_documents.py — and both need the same
two things: a page shell in the house design language, and a writer that can also run
in --check mode so CI can prove a generated page still matches its source.

The --check comparison ignores the nav and footer blocks. Those are owned by
chrome.py, which rewrites them in place AFTER generation, so a byte-for-byte compare
of a generated file against fresh generator output would always differ on chrome
alone. Stripping both blocks from both sides compares exactly what the generator is
responsible for, and nothing it is not.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HOST = (ROOT / "CNAME").read_text().strip()

NAV_STUB = '<nav class="site"><div class="row"></div></nav>'
FOOT_STUB = '<footer class="site"><div class="cols"></div></footer>'

_CHROME = re.compile(r'<nav class="site">.*?</nav>|<footer class="site">.*?</footer>', re.S)


def page_head(rel, title, description, og_title=None, og_description=None, extra_head=""):
    """The <head> and the nav stub. `rel` is the page's path from the repo root — it is
    what makes the canonical URL, and validate.js requires every page to declare one on
    the host named in CNAME."""
    up = "../" * (len(Path(rel).parts) - 1)
    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{title}</title>
<meta name="description" content="{description}">
<link rel="canonical" href="https://{HOST}/{rel}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="{HOST}">
<meta property="og:url" content="https://{HOST}/{rel}">
<meta property="og:title" content="{og_title or title}">
<meta property="og:description" content="{og_description or description}">
<meta name="twitter:card" content="summary">
<link rel="stylesheet" href="{up}assets/site.css">{extra_head}
</head>
<body>

{NAV_STUB}
'''


def page_tail():
    return f'\n{FOOT_STUB}\n\n</body>\n</html>\n'


def write_or_check(path, content, check, changed, mismatched):
    """Write the page, or in --check mode report whether it is out of date.

    A generated page that has drifted from its source is the exact failure this whole
    site is built against — four artefacts in the platform's own repo went stale
    because they were written once by hand — so it is a build failure here, not a
    warning."""
    path = Path(path)
    if check:
        if not path.exists():
            mismatched.append(f"{path.relative_to(ROOT)} — missing (never generated)")
            return
        if _CHROME.sub("", path.read_text()) != _CHROME.sub("", content):
            mismatched.append(f"{path.relative_to(ROOT)} — out of date, re-run the generator")
        return
    before = path.read_text() if path.exists() else None
    if before is not None and _CHROME.sub("", before) == _CHROME.sub("", content):
        return                                   # unchanged: keep the chrome already applied
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)
    changed.append(str(path.relative_to(ROOT)))


def report(name, check, changed, mismatched):
    if check:
        if mismatched:
            print(f"{name} --check: {len(mismatched)} page(s) out of date", file=sys.stderr)
            for m in mismatched:
                print("  ✗ " + m, file=sys.stderr)
            sys.exit(1)
        print(f"{name} --check: OK — every generated page matches its source")
        return
    print(f"{name}: {len(changed)} page(s) written")
    for c in changed:
        print("  · " + c)


def esc(s):
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
             .replace('"', "&quot;"))
